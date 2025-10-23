import json
import os
import random
import re
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
from collections import defaultdict
from tqdm import tqdm
import traceback
import networkx as nx
import pickle
import fsp_generate
from fsp_generate.code.build_dependency_graph.prompt.tool_category_prompt import tool_category_prompt
from data_generate.agent.model.gpt import ChatGPTFunction
from data_generate.agent.model.qwq import QwQFunction
from fsp_generate.utils.load_utils import *

def process_one(llm, func_name, func_info):
    
    # 获取候选
    uncached_category = [category for category in ['lookup','modification','realtime'] if (func_name, category) not in relation_cache]

    # 先把缓存中已有的信息添加进图
    for category in ['lookup','modification','realtime']:
        if (func_name, category) in relation_cache and relation_cache[(func_name, category)]:
            print(f"✅ 载入已有依赖: {func_name} -> {category}")

    # 如果全部都有缓存，直接返回
    if not uncached_category:
        return

    print(f"➡️ 正在处理函数: {func_name}")
    # 处理未缓存的 candidate
    prompt_parameter = {
        "function": func_info,
    }

    for attempt in range(5):
        try:
            response,status_code = llm_request(llm, tool_category_prompt, prompt_parameter)
            print(response)
            if status_code!=200:
                raise Exception(f'Error with code {status_code}: {response}')
            response=response['content']
            if '```json' in response:
                matches = re.findall(r'```json(.*?)```', response, re.DOTALL)
                response = json.loads(matches[0].strip()) if matches else response
            elif isinstance(response, str):
                response = json.loads(response.strip())

            
            is_lookup_function = response["is_lookup_function"]
            is_modification_function = response["is_modification_function"]
            is_modification_function = response["is_realtime_function"]
            print(response.get("reason", ""))
            print(f"is_lookup_function: {is_lookup_function}")
            print(f"is_modification_function: {is_modification_function}")
            print(f"is_realtime_function: {is_realtime_function}")
        
            with lock:
                relation_cache[(func_name, 'lookup')] = is_lookup_function
                relation_cache[(func_name, 'modification')] = is_modification_function
                relation_cache[(func_name, 'realtime')] = is_modification_function
                
                save_relation_cache(relation_cache, relation_cache_file)

                break  # 成功后跳出 retry 循环
        except Exception as e:
            print(f"[ERROR][{func_name}] Attempt {attempt + 1} failed: {e}")

def main(llm_name='gpt',thread_num=10):
    if llm_name=='gpt':
        llm = ChatGPTFunction(name='gpt4o-ptu-client')
    else:
        llm = QwQFunction()
    tasks = []
    with ThreadPoolExecutor(max_workers=thread_num) as executor:
        for func_name, func_info in function_pool_index.items():
            tasks.append(executor.submit(process_one, llm, func_name, func_info))
        for future in tqdm(as_completed(tasks), total=len(tasks), desc="⏳ 等待线程完成"):
            try:
                future.result(timeout=60)  # ⏱️ 可加超时
            except Exception as e:
                print(f"[Thread Error] {e}")
                traceback.print_exc()

    save_relation_cache(relation_cache, relation_cache_file)
    print("✅ 所有依赖关系构建完成。")


if __name__ == "__main__":
    import data_generate
    fsp_dir = os.path.dirname(fsp_generate.__file__)
    project_dir = os.path.dirname(data_generate.__file__)
    tool_metadata_path = f"{project_dir}/tools/all_tools_metadata.json"
    save_dir = f"{fsp_dir}/data/graph"
    os.makedirs(save_dir, exist_ok=True)

    function_pool_index = load_functions(tool_metadata_path,limit_categories=['file_system_functions', 'python_functions', 'database_functions','api_functions'])
    file_pool_index = defaultdict(dict)
    all_results = []
    lock = Lock()

    relation_cache_file = os.path.join(save_dir, "tool_category_graph.json")
    relation_cache = load_relation_cache(relation_cache_file)
    main(llm_name='gpt')
