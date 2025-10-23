from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page
import random
from readability import Document
from bs4 import BeautifulSoup
import markdownify
import logging
import time
import os
from dotenv import load_dotenv
load_dotenv()

class BrowserService:
    def __init__(self, options: dict):
        self.options = options
        self.debug = options.get("debug", False)

    def get_random_user_agent(self) -> str:
        agents = [
            # Chrome, Firefox, Safari
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0"
        ]
        return random.choice(agents)

    def get_random_viewport(self):
        return random.choice([
            {"width": 1920, "height": 1080},
            {"width": 1366, "height": 768},
            {"width": 1440, "height": 900}
        ])

    def create_browser(self):
        p = sync_playwright().start()
        browser = p.chromium.launch(
            headless=not self.debug, 
            args=[
            "--disable-blink-features=AutomationControlled",
            "--no-sandbox", "--disable-setuid-sandbox"
        ])
        return p, browser

    def create_context(self, browser: Browser):
        viewport = self.get_random_viewport()
        context = browser.new_context(
            viewport=viewport,
            user_agent=self.get_random_user_agent(),
            locale='en-US',
            timezone_id='America/New_York',
        )

        if self.options.get("disableMedia", True):
            context.route("**/*", lambda route: route.abort() if route.request.resource_type in [
                          "image", "media", "stylesheet", "font"] else route.continue_())

        return context, viewport

    def create_page(self, context: BrowserContext):
        return context.new_page()

    def cleanup(self, playwright, browser: Browser, page: Page):
        if not self.debug:
            page.close()
            browser.close()
            playwright.stop()

class WebContentProcessor:
    def __init__(self, options, log_prefix="[FetchURL]"):
        self.options = options
        self.log_prefix = log_prefix

    def process_page_content(self, page, url):
        timeout = self.options.get("timeout", 30000)

        try:
            page.goto(url, timeout=timeout, wait_until=self.options.get("waitUntil", "load"))

            if self.options.get("waitForNavigation"):
                try:
                    page.wait_for_navigation(timeout=self.options.get("navigationTimeout", 10000))
                except:
                    logger.warning(f"{self.log_prefix} waitForNavigation timeout, continuing.")

            page.wait_for_load_state("load")
            time.sleep(0.5)

            html = page.content()
            title = page.title()
            content = self.extract_main_content(html, url, mode=self.options.get("contentMode", "clean_content"))

            if not self.options.get("returnHtml", False):
                content = markdownify.markdownify(content)

            if self.options.get("maxLength", 0) > 0:
                content = content[:self.options["maxLength"]]

            return {
                "success": True,
                "content": f"Title: {title}\nURL: {url}\nContent:\n\n{content}"
            }

        except Exception as e:
            logger.error(f"{self.log_prefix} Error fetching content: {e}")
            return {
                "success": False,
                "content": f"<error>Failed to retrieve content: {e}</error>"
            }

    def extract_main_content(self, html, url, mode="clean_content"):
        try:
            if mode == "summary":
                return Document(html).summary()
            elif mode == "clean_content":
                doc = Document(html)
                main_html = doc.content()
                soup = BeautifulSoup(main_html, "html.parser")

                for tag in soup(["script", "style", "iframe", "footer", "form", "noscript"]):
                    tag.decompose()

                return str(soup)
            elif mode == "full_content":
                return html
            else:
                logger.warning(f"{self.log_prefix} Unknown content mode '{mode}', falling back to full_content.")
                return html
        except Exception as e:
            logger.warning(f"{self.log_prefix} Failed to extract content: {e}")
            return html


def with_proxy_temporarily_disabled(func):
    def wrapper(*args, **kwargs):
        # 保存原始代理配置
        original_http_proxy = os.environ.get("http_proxy")
        original_https_proxy = os.environ.get("https_proxy")

        # 暂时禁用代理
        os.environ.pop("http_proxy", None)
        os.environ.pop("https_proxy", None)

        try:
            return func(*args, **kwargs)
        finally:
            # 恢复原代理配置
            if original_http_proxy:
                os.environ["http_proxy"] = original_http_proxy
            if original_https_proxy:
                os.environ["https_proxy"] = original_https_proxy
    return wrapper

@with_proxy_temporarily_disabled
def fetch_url(
    url: str,
    timeout: int = 30000,
    wait_until: str = "load",
    extract_content: str = "clean_content",  # 新参数
    max_length: int = 0,
    return_html: bool = False,
    wait_for_navigation: bool = False,
    navigation_timeout: int = 10000,
    disable_media: bool = True,
    debug: bool = False,
    save_path: str = None
):
    print(os.getcwd())
    if not url:
        raise ValueError("Missing required 'url'")

    options = {
        "timeout": timeout,
        "waitUntil": wait_until,
        "contentMode": extract_content,
        "maxLength": max_length,
        "returnHtml": return_html,
        "waitForNavigation": wait_for_navigation,
        "navigationTimeout": navigation_timeout,
        "disableMedia": disable_media,
        "debug": debug,
    }

    browser_service = BrowserService(options)
    processor = WebContentProcessor(options)

    p, browser = browser_service.create_browser()
    context, viewport = browser_service.create_context(browser)
    page = browser_service.create_page(context)

    result = processor.process_page_content(page, url)

    browser_service.cleanup(p, browser, page)

    # 写入文件（如果指定了路径）
    if save_path and result.get("success") and result.get("content"):
        os.makedirs(os.path.dirname(save_path) or '.', exist_ok=True)
        with open(save_path, "w", encoding="utf-8") as f:
            f.write(result["content"])
        return f"result successfully saved to {save_path}."

    return result


if __name__ == "__main__":
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    res = fetch_url(
        url="https://ted.com/talks/shaolan_learn_to_read_chinese_with_ease",
        extract_content="clean_content",           # 可改为 "clean_content" 或 "full_content"
        return_html=True,
        max_length=0,
        save_path="./shaolan_learn_to_read_chinese_with_ease.md"
    )
    print(res)

