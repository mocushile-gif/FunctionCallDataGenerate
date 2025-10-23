import requests
import os
from urllib.parse import urlparse
from dotenv import load_dotenv
load_dotenv()

def download_file(url, output_path=None):
    """
    Download a file from a URL without progress bar.

    Parameters:
    - url (str): The URL of the file to download.
    - output_path (str): Path to save the file. If None, use the filename from the URL.

    Returns:
    - (bool, str): Success status and message.
    """
    # 设置工作目录
    
    


    try:
        # 自动提取文件名
        if not output_path:
            filename = os.path.basename(urlparse(url).path) or "downloaded_file"
            output_path = f'./{filename}'
        else:
            os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)

        # 下载文件
        response = requests.get(url, stream=True, timeout=15)
        response.raise_for_status()

        with open(output_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        return True, f"File downloaded successfully to {output_path}."

    except Exception as e:
        return False, f"Download failed: {str(e)}"


# Example usage
if __name__ == "__main__":
    os.chdir(os.environ.get("FILE_SYSTEM_PATH"))
    success, message = download_file("https://picsum.photos/id/2/5000/3333.jpg")
    print(success, message)
