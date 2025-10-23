import requests
import os
from dotenv import load_dotenv
load_dotenv()


def get_chinese_almanac_for_specific_date(date, detail=True):
    """
    获取指定日期的中国黄历信息。

    参数：
    - date: str，指定日期，格式为yyyy-MM-dd，如：2021-05-01。
    - detail: bool，可选，是否返回详细信息，默认为False。

    返回：
    - dict: 包含黄历信息的字典。
    """
    api_key = os.getenv('Calendar_API_KEY', 'cffdd89c6401a5e793040227fd9946a4')
    url = "http://apis.juhe.cn/fapig/calendar/day"
    params = {
        "key": api_key,
        "date": date,
        "detail": 1 if detail else 0
    }
    
    response = requests.get(url, params=params)
    response.raise_for_status()  # 检查是否成功请求
    data = response.json()
    
    if data.get("error_code") == 0:
        return {"response":data.get("result", {})}
    else:
        return {"error": f"Error fetching data from the API: {data.get('reason')}"}

# 示例用法
if __name__ == "__main__":
    date = "2020-02-18"
    holiday_info = get_chinese_almanac_for_specific_date(date, detail=True)
    print(holiday_info)
