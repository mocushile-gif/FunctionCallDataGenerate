import requests
import os
from dotenv import load_dotenv
load_dotenv()

def get_specific_chinese_news_content(uniquekey):
    """
    获取特定中国新闻的内容，需要先使用get_chinese_news前置工具获得uniquekey。

    参数：
    - uniquekey: str，新闻ID。
    """
    api_key = os.getenv('TouTiao_API_KEY', '50d5c6451829b6b6aff50506317b0465')
    url = "http://v.juhe.cn/toutiao/content"
    params = {
        "key": api_key,
        "uniquekey": uniquekey
    }
    
    response = requests.get(url, params=params)
    response.raise_for_status()  # 检查是否成功请求
    data = response.json()
    return data

# 示例用法
if __name__ == "__main__":
    news_list = get_specific_chinese_news_content(uniquekey="0e91704128e9ec7205dc419f87c929e6")
    print(news_list)
