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
import data_generate
import fsp_generate
from fsp_generate.code.build_dependency_graph.prompt.tool_file_dependency_prompt import tool_file_dependency_prompt
from data_generate.agent.model.gpt import ChatGPTFunction
from data_generate.agent.model.qwq import QwQFunction
from fsp_generate.utils.load_utils import *

        
def process_one_dependency(llm, file_path, file_info, batch_size=5):
    
    # 获取候选函数（同类中除自己外）
    candidates = [func for func in function_pool_index]
    uncached = [c for c in candidates if (c, file_path) not in relation_cache]

    # 先把缓存中已有的信息添加进图
    for c in candidates:
        if (c, file_path) in relation_cache and relation_cache[(c, file_path)]:
            G.add_edge(c, file_path)
            # print(f"✅ 载入已有依赖: {c} -> {file_path}")

    # 如果全部都有缓存，直接返回
    if not uncached:
        return

    print(f"➡️ 正在处理文件: {file_path}")
    # 按 batch 分批处理未缓存的 candidate
    for i in range(0, len(uncached), batch_size):
        batch = uncached[i:i + batch_size]
        sampled_infos = [function_pool_index[c] for c in batch]

        prompt_parameter = {
            "candidate_functions": sampled_infos,
            "file_info": file_info,
        }

        for attempt in range(5):
            try:
                response,status_code = llm_request(llm, tool_file_dependency_prompt, prompt_parameter)
                if status_code!=200:
                    raise Exception(f'Error with code {status_code}: {response}')
                response=response['content']
                try:
                    if '```json' in response:
                        matches = re.findall(r'```json(.*?)```', response, re.DOTALL)
                        response = json.loads(matches[0].strip())
                    elif isinstance(response, str):
                        response = json.loads(response.strip())
                    use_files = response["functions_using_file"]
                except:
                    raise Exception(f'cannot extract: {response}')
                
                if not use_files:
                    print(f"❌ 无依赖: {file_path} -> {c}")
                else:
                    print(use_files)
                    print(response.get("reason", ""))
                
                with lock:
                    for c in batch:
                        relation_cache[(c, file_path)] = c in use_files
                        if c in use_files:
                            G.add_edge(c, file_path)
                            print(f"✅ 添加依赖: {c} -> {file_path}")

                    # 🧠 每 batch 后保存（可选：判断是否有新内容再保存）
                    save_relation_cache(relation_cache, relation_cache_file)

                # print(f"✅ Batch 处理完成: {func_name} -> {batch}")
                break  # 成功后跳出 retry 循环
            except Exception as e:
                print(f"[ERROR][{file_path}] Attempt {attempt + 1} failed: {e}")

def main(llm_name='gpt',thread_num=10):
    if llm_name=='gpt':
        llm = ChatGPTFunction(name='gpt4o-ptu-client')
    else:
        llm = QwQFunction()
    tasks = []
    with ThreadPoolExecutor(max_workers=thread_num) as executor:
        for file_path, file_info in file_pool_index.items():
            tasks.append(executor.submit(process_one_dependency, llm, file_path, file_info))
        for future in tqdm(as_completed(tasks), total=len(tasks), desc="⏳ 等待线程完成"):
            try:
                future.result(timeout=60) 
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
    file_metadata_path = f"{project_dir}/working_dir/all_files_metadata.json"
    save_dir = f"{fsp_dir}/data/graph"
    os.makedirs(save_dir, exist_ok=True)

    function_pool_index = load_functions(tool_metadata_path,limit_categories=['file_system_functions', 'python_functions', 'database_functions','api_functions'])
    file_pool_index = load_file_pools(file_metadata_path)
    all_results = []
    lock = Lock()
    G = nx.DiGraph()

    relation_cache_file = os.path.join(save_dir, "file_tool_dependency_graph.json")
    relation_cache = load_relation_cache(relation_cache_file)

    main(llm_name='gpt',thread_num=10)
