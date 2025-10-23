import requests
import os
from dotenv import load_dotenv
load_dotenv()


def get_chinese_news(type='top', page=1, page_size=30, is_filter=0):
    """
    获取中国新闻头条，支持多种分类。

    参数：
    - type: str，新闻类型。可选：'top'（推荐，默认），'guonei'（中国国内），'guoji'（国际），
            'yule'（娱乐），'tiyu'（体育），'junshi'（军事），'keji'（科技），
            'caijing'（财经），'youxi'（游戏），'qiche'（汽车），'jiankang'（健康）。
    - page: int，当前页数，默认1，最大50。
    - page_size: int，每页返回条数，默认30，最大30。
    - is_filter: int，是否只返回有内容详情的新闻，1:是，默认0。

    """
    api_key = os.getenv('TouTiao_API_KEY', '50d5c6451829b6b6aff50506317b0465')
    url = "https://v.juhe.cn/toutiao/index"
    params = {
        "key": api_key,
        "type": type,
        "page": page,
        "page_size": page_size,
        "is_filter": is_filter
    }
    
    response = requests.get(url, params=params)
    response.raise_for_status()  # 检查是否成功请求
    data = response.json()
    return {"response":data.get("result", [])}

# 示例用法
if __name__ == "__main__":
    news_list = get_chinese_news(type="guonei", page=1, page_size=5, is_filter=1)
    print(news_list)
