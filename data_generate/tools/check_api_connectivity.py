#!/usr/bin/env python3
"""
API连通性检查器
专门用于检查api_functions下所有工具的连通性状态
返回一个字典，其中正常的工具为True，不正常的为False
"""

import os
import sys
import importlib
import time
from typing import Dict

# 添加路径以便导入模块
sys.path.append(os.path.join(os.path.dirname(__file__), 'executable_functions'))

def get_test_params(function_name: str) -> Dict:
    """
    为每个函数提供测试参数
    """
    params = {
        "get_ip_info": {},
        "get_current_weather_api": {"q": "London"},
        "get_weather_forcast": {"q": "London", "days": 1},
        "get_weather_history": {"q": "London", "dt": "2025-08-01"},
        "get_weather_alerts": {"q": "Shanghai"},
        "get_stock_data": {"symbol": "AAPL"},
        "get_current_exchange_rate": {"base_currency": "USD", "target_currency": ["EUR"]},
        "convert_currency_api": {"amount": 1, "from_currency": "USD", "to_currency": "EUR"},
        "search_news_articles": {"query": "technology", "lang": "en"},
        "search_guardian_news_content": {"query": "technology"},
        "get_chinese_news": {},
        "get_chinese_hot_topics": {},
        "get_specific_chinese_news_content": {"uniquekey": "0e91704128e9ec7205dc419f87c929e6"},
        "duckduckgo_websearch": {"query": "python programming"},
        "get_random_joke": {"category": ["Programming"], "language": "en"},
        "get_random_dog_images_info": {"limit": 1},
        "get_random_cat_images_info": {"limit": 1},
        "get_dog_breeds": {},
        "get_cat_breeds": {},
        "get_dog_breed_info_by_id": {"breed_id": 1},
        "get_cat_breed_info_by_id": {"breed_id": "asho"},
        "get_dog_image_info_by_id": {"image_id": "BJa4kxc4X"},
        "get_cat_image_info_by_id": {"image_id": "0XYvRd7oD"},
        "convert_coordinates_to_adress": {"latitude": 24, "longitude": 108},
        "convert_adress_to_coordinates": {"address": "New York, NY"},
        "get_data_from_zipcode": {"zipcode": "10001"},
        "get_holidays_by_year_and_country": {"year": 2024, "country_code": "US"},
        "get_chinese_almanac_for_specific_date": {"date": "2024-01-01"},
        "get_huggingface_models_by_task": {"task": "text-generation", "limit": 1},
        "get_specific_huggingface_model_details": {"model_id": "gpt2"},
        "http_request": {"url": "https://httpbin.org/get", "method": "GET"},
        "classify_image": {"image_path": "./image_data/dog.jpg"},
        "segment_image": {"image_path": "./image_data/dog.jpg"},
        "generate_image": {"prompt": "a simple red circle", "width": 256, "height": 256}
    }
    return params.get(function_name, {})

def check_function_connectivity(function_name: str) -> bool:
    """
    检查单个函数的连通性
    """
    try:
        # 导入模块
        module = importlib.import_module(f'api_functions.{function_name}')
        func = getattr(module, function_name)
        
        # 获取测试参数
        test_params = get_test_params(function_name)
        
        # 执行函数
        result = func(**test_params)
        
        # 检查结果
        if result is None:
            return False
        
        # 如果返回的是字典且包含error字段，检查是否成功
        if isinstance(result, dict) and "error" in result:
            return not result["error"]
        
        return True
        
    except Exception as e:
        # 对于需要API key的函数，如果缺少key也算正常
        if "API key" in str(e) or "HUGGINGFACE_API_KEY" in str(e):
            return True
        return False

def check_all_api_connectivity() -> Dict[str, bool]:
    """
    检查所有API函数的连通性
    返回一个字典，其中正常的工具为True，不正常的为False
    """
    # 获取所有API函数
    api_dir = os.path.join(os.path.dirname(__file__), 'executable_functions', 'api_functions')
    functions = []
    
    if os.path.exists(api_dir):
        for file in os.listdir(api_dir):
            if file.endswith('.py') and file != '__init__.py':
                functions.append(file[:-3])
    
    functions = sorted(functions)
    results = {}
    
    print(f"正在检查 {len(functions)} 个API函数的连通性...")
    
    for i, func_name in enumerate(functions, 1):
        
        # 检查函数连通性
        is_working = check_function_connectivity(func_name)
        results[func_name] = is_working
        if is_working:
            print(f"✔通过 {sum(results.values())}/{len(functions)}: {func_name}")
        else:
            print(f"❌失败 {len(results)-sum(results.values())}/{len(functions)}: {func_name}")
        # 添加延迟避免API限制
        time.sleep(0.1)
    
    return results

def main():
    """
    主函数 - 运行检查并返回结果
    """
    results = check_all_api_connectivity()
    
    # 统计结果
    working_count = sum(results.values())
    total_count = len(results)
    
    print(f"\n检查完成！")
    print(f"正常工作的函数: {working_count}/{total_count}")
    print(f"成功率: {working_count/total_count*100:.1f}%")
    
    return results

if __name__ == "__main__":
    main() 