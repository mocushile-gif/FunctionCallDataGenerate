import re
import os
import json
from collections import defaultdict
import random
from fsp_generate.utils.load_utils import *

def random_walk(graph, start_node, max_steps=7):
    path = [start_node]
    current = start_node
    visited = set()  # 记录访问过的节点
    tried_neighbors = defaultdict(set)  # 记录每个节点尝试过的邻居

    for _ in range(max_steps - 1):
        neighbors = graph.get(current, [])
        valid_neighbors = [n for n in neighbors if n not in path]  # 排除已经出现在路径中的节点
        
        if not valid_neighbors:
            break  # 如果没有有效的邻居，停止生成路径
        
        while True:
            if len(tried_neighbors[current]) == len(neighbors):
                # 如果所有邻居都尝试过，丢弃当前路径
                return None
            
            next_node = random.choice([n for n in neighbors if n not in tried_neighbors[current]])
            tried_neighbors[current].add(next_node)
            
            if next_node not in path:  # 确保不形成循环
                current = next_node
                path.append(current)
                break

    return path if len(path) >= 3 else None  # 只返回长度大于等于 3 的路径

def sample_initial_fsps(graph, num_paths=5, max_steps=7):
    fsps = []
    attempts = 0
    max_attempts = num_paths * 10  # 防止无限循环的最大尝试次数
    all_funcs=list(graph.keys())
    while len(fsps) < num_paths and attempts < max_attempts:
        start = random.choice(all_funcs)
        fsp = random_walk(graph, start, max_steps=max_steps)
        
        if fsp is not None:  # 只保留有效的路径
            fsps.append(fsp)
        
        attempts += 1

    if attempts == max_attempts:
        print("⚠️ 达到最大尝试次数，生成的路径数量可能不足。")

    return fsps

def generate_fsp_data(dependency_data_path,limit_functions=[],num_paths=5, max_steps=5, output_file="init_fsps.json"):
    graph = load_graph(dependency_data_path,limit_functions)
    init_fsps = sample_initial_fsps(graph,num_paths=num_paths, max_steps=max_steps)
    
    # 将生成的内容存储到文件中
    with open(output_file, "w") as f:
        json.dump(init_fsps, f, indent=4)
    print(f"已生成 {num_paths} 条路径，并存储到文件 {output_file}")
    
    return init_fsps

if __name__ == "__main__":
    random.seed(42)
    import fsp_generate,data_generate
    fsp_dir = os.path.dirname(fsp_generate.__file__)
    project_dir = os.path.dirname(data_generate.__file__)
    function_pool_index = load_functions(f'{project_dir}/tools/all_tools_metadata.json',limit_categories=['file_system_functions', 'python_functions', 'database_functions','api_functions'])
    function_pool_index = load_functions(f'{project_dir}/tools/all_tools_metadata.json')
    functions=list(function_pool_index.keys())
    # 控制生成条数并存储
    num_paths = 1000  # 用户可以自定义生成条数
    max_steps = 5   # 用户可以自定义最大步数
    date = '0810_all_self+xlam'
    graph_data = f"{fsp_dir}/data/graph/tool_dependency_graph.json"
    output_file = f"{fsp_dir}/data/generated_fsps_execute_step{max_steps}_{num_paths}_{date}.json"
    init_fsps = generate_fsp_data(graph_data,limit_functions=functions,num_paths=num_paths, max_steps=max_steps, output_file=output_file)