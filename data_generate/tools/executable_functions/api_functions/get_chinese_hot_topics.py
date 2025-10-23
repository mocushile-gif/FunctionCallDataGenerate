import requests
import os
from dotenv import load_dotenv
load_dotenv()

def get_chinese_hot_topics(type='douyin'):
    """
    获取特定来源的热搜榜数据。

    Parameters:
    - type: str, the source of the hot topics (e.g., zhihu(知乎热榜)、weibo(微博热搜)、baidu(百度热点)、历史上的今天(history)、 bilihot(哔哩哔哩热搜)、 biliall(哔哩哔哩全站日榜)
sspai(少数派头条)、douyin(抖音热搜)、csdn(CSDN头条榜))

    Returns:
    - dict: JSON response from the API containing hot topics.
    """
    api_key = os.getenv('Oick_API_KEY', '6dc30545804e1b10153f9c6f70955efe')
    url = f"https://api.oick.cn/api/hot?type={type}&apikey={api_key}"   
    response = requests.get(url)

    response.raise_for_status()  # Ensure the request was successful
    try:
        return {'response':response.json()}  # Return the JSON response as a dictionary
    except:
        return {'response':response.text}

if __name__ == "__main__":
    # Example usage
    hot_topics = get_chinese_hot_topics('douyin')
    if hot_topics:
        print(hot_topics)
