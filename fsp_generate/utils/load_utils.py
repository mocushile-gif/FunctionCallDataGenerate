from collections import defaultdict
import json
import os

def load_functions(tool_metadata_path,limit_categories=None):
    print("🔍 加载函数池...")
    functions_pool = defaultdict(dict)
    with open(tool_metadata_path, "r") as f:
        func_data = json.load(f)
        for function in func_data.values():
            if limit_categories:
                if function["category"] in limit_categories:
                    functions_pool[function["api_define"]["name"]] = function["api_define"]
            else:
                functions_pool[function["api_define"]["name"]] = function["api_define"]
    print(f"✅ 加载函数数量: {len(functions_pool)}")
    return functions_pool

def load_file_pools(file_metadata_path):
    file_pool_index = defaultdict(dict)
    print("🔍 加载文件池...")
    with open(file_metadata_path, "r") as f:
        file_data = json.load(f)
        for file_name,file_info in file_data.items():
            file_pool_index[file_name] = file_info
    print(f"✅ 加载文件数量: {len(file_pool_index)}")
    return file_pool_index

def load_graph(dependency_data_path,limit_nodes=[]):
    """
    构建依赖图，边方向为：target_func → func（即调用顺序）
    """
    with open(dependency_data_path, "r", encoding="utf-8") as f:
        raw_cache = json.load(f)
        relation_cache = {
            tuple(k.split(" → ", 1)): v for k, v in raw_cache.items()
        }
    # 构建图
    graph = defaultdict(list)
    for (source, target), is_related in relation_cache.items():
        if not limit_nodes:
            if is_related:
                graph[source].append(target)
        else:
            if source in limit_nodes and target in limit_nodes and is_related:
                graph[source].append(target)
                
    return graph

def load_relation_cache(relation_cache_file):
    relation_cache = {}
    if os.path.exists(relation_cache_file):
        with open(relation_cache_file, "r", encoding="utf-8") as f:
            raw_cache = json.load(f)
            relation_cache = {
                tuple(k.split(" → ", 1)): v for k, v in raw_cache.items()
            }
    print(f"✅ loading relation count: {len(relation_cache)}")
    return relation_cache

def save_relation_cache(cache: dict, path: str):
    # 将 key 转为字符串用于 json 存储
    json_cache = {
            f"{k[0]} → {k[1]}": v
            for k, v in sorted(cache.items(), key=lambda x: f"{x[0][0]} → {x[0][1]}")
        }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(json_cache, f, ensure_ascii=False, indent=2)

def llm_request(llm, prompt, prompt_parameter):
    prompt = prompt.format(**prompt_parameter)
    return llm.chat([{"role": "user", "content": prompt}])
