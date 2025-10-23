import json
import os
import random
import re
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
from collections import defaultdict
from tqdm import tqdm
import networkx as nx
import pickle
import fsp_generate
from fsp_generate.code.build_dependency_graph.prompt.tool_dependency_prompt import tool_dependency_prompt
from data_generate.agent.model.gpt import ChatGPTFunction
from data_generate.agent.model.qwq import QwQFunction
from fsp_generate.utils.load_utils import *

def load_function_tools(tool_metadata_path):
    temp_function_pool_index = defaultdict(lambda: defaultdict(dict))
    print("🔍 加载函数池...")
    with open(self_tool_res_cache_path, 'r') as f:
        self_tool_cache = json.load(f)
    with open(rapidapi_res_cache_path, 'r') as f:
        rapidapi_cache = json.load(f)
    with open(tool_metadata_path, "r") as f:
        func_data = json.load(f)
        for function in func_data.values():
            define = function["api_define"]
            cache_responses = self_tool_cache.get(define["name"], {}) if function["category"] in [
                'file_system_functions', 'python_functions', 'database_functions', 'api_functions'
            ] else rapidapi_cache.get(define["name"], {})

            example_num = 5
            example_responses = list(cache_responses.items())[:example_num]
            while len(str(example_responses)) > 4096 and example_num > 1:
                example_num -= 1
                example_responses = list(cache_responses.items())[:example_num]
            example_responses = [{"input":example[0],"response":example[1]} for example in example_responses]
            
            func_info = {"define": define, "example_responses": example_responses}
            category = function["category"] if function["category"] not in [
                'file_system_functions', 'python_functions', 'database_functions','api_functions'
            ] else 'self-tools'
            temp_function_pool_index[category][define["name"]] = func_info

    for category, values in temp_function_pool_index.items():
        if len(values) < 30:
            function_pool_index['Others'].update(values)
        else:
            function_pool_index[category] = values
    for category in function_pool_index:
        print(f"✅ 加载 {category} 函数数量: {len(function_pool_index[category])}")


def process_one_dependency(llm, category, func_name, func_info, batch_size=10):
    
    # 获取候选函数（同类中除自己外）
    # candidates = [func for func in function_pool_index[category] if func != func_name]
    # uncached = [c for c in candidates if (func_name, c) not in relation_cache]
    category_funcs = list(function_pool_index[category].keys())
    candidates = [f for f in category_funcs if f != func_name]
    seen = relation_index.get(func_name, set())
    uncached = [c for c in candidates if c not in seen]
    # 先把缓存中已有的信息添加进图
    # for c in candidates:
    #     if (func_name, c) in relation_cache and relation_cache[(func_name, c)]:
    #         G.add_edge(func_name, c)
            # print(f"✅ 载入已有依赖: {func_name} -> {c}")

    # 如果全部都有缓存，直接返回
    if not uncached:
        # print(f'✅ [{category}] {func_name}处理完毕')
        return
    # print(f'✅ [{category}] {func_name}仍需处理：{uncached}')
    print(f'➡️ [{category}] {func_name}仍需处理：{len(uncached)}/{len(candidates)}')
    # print(f"➡️  [{category}] 正在处理函数: {func_name}")
    # 按 batch 分批处理未缓存的 candidate
    for i in range(0, len(uncached), batch_size):
        batch = uncached[i:i + batch_size]
        sampled_infos = [function_pool_index[category][c] for c in batch]

        prompt_parameter = {
            "candidate_functions": sampled_infos,
            "source_function": func_info["define"],
            "source_function_output": func_info["example_responses"]
        }

        for attempt in range(3):
            try:
                response,status_code = llm_request(llm, tool_dependency_prompt, prompt_parameter)
                # print(response)
                if status_code!=200:
                    raise Exception(f'Error with code {status_code}: {response}')
                response=response['content']
                try:
                    if '```json' in response:
                        matches = re.findall(r'```json(.*?)```', response, re.DOTALL)
                        response = json.loads(matches[0].strip())
                    else:
                        response = json.loads(response.strip())
                    
                    dependent_funcs = response["dependent_functions"]
                except:
                    raise Exception(f'cannot extract: {response}')

                if not dependent_funcs:
                    print(f"❌ 无依赖: {func_name} -> {batch}")
                else:
                    print(dependent_funcs)
                    print(response.get("reason", ""))

                with lock:
                    for c in batch:
                        relation_cache[(func_name, c)] = c in dependent_funcs
                        relation_index[func_name].add(c)
                        if c in dependent_funcs:
                        #     G.add_edge(func_name, c)
                            print(f"✅ 添加依赖: {func_name} -> {c}")

                    # 🧠 每 batch 后保存（可选：判断是否有新内容再保存）

                    save_relation_cache(relation_cache, relation_cache_file)
                # print(f"✅ Batch 处理完成: {func_name} -> {batch}")
                break  # 成功后跳出 retry 循环
            except Exception as e:
                print(f"[ERROR][{category}::{func_name}] Attempt {attempt + 1} failed: {e}")
            assert len(relation_index[func_name])==len(candidates)


def main(llm_name='gpt',thread_num=10):
    if llm_name=='gpt':
        llm = ChatGPTFunction(name='gpt4o-ptu-client')
    else:
        llm = QwQFunction()
    tasks = []
    with ThreadPoolExecutor(max_workers=thread_num) as executor:
        for category, functions_group in function_pool_index.items():
            for current_func, function_info in tqdm(functions_group.items(), desc=f"📂  → {category}", leave=False):
                tasks.append(executor.submit(process_one_dependency, llm, category, current_func, function_info))
        for future in tqdm(as_completed(tasks), total=len(tasks), desc="⏳ 等待线程完成"):
            try:
                future.result()
            except Exception as e:
                print(f"[Thread Error] {e}")

    save_relation_cache(relation_cache, relation_cache_file)
    print("✅ 所有依赖关系构建完成")

if __name__ == "__main__":
    import data_generate
    fsp_dir = os.path.dirname(fsp_generate.__file__)
    project_dir = os.path.dirname(data_generate.__file__)
    self_tool_res_cache_path = f'{fsp_dir}/tools/tool_response_collections_self.json'
    rapidapi_res_cache_path = f'{fsp_dir}/tools/tool_response_collections_rapidapi.json'
    tool_metadata_path = f"{project_dir}/tools/all_tools_metadata.json"
    save_dir = f"{fsp_dir}/data/graph"
    os.makedirs(save_dir, exist_ok=True)

    function_pool_index = defaultdict(lambda: defaultdict(dict))
    load_function_tools(tool_metadata_path)
    # G = nx.DiGraph()
    all_results = []
    lock = Lock()

    relation_cache_file = os.path.join(save_dir, "tool_dependency_graph.json")
    relation_cache = load_relation_cache(relation_cache_file)
    relation_index = defaultdict(set)
    for (src, tgt) in relation_cache.keys():
        relation_index[src].add(tgt)
    main(llm_name='gpt',thread_num=10)
