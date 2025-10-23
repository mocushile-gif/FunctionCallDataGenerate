import json
import re
import random
from collections import defaultdict,Counter
from copy import deepcopy
import uuid
from fsp_generate.utils.fsp_statistics import fsps_statistics
from fsp_generate.utils.select_files_for_fsps import select_files_for_fsps
from fsp_generate.utils.load_utils import *

def insert_operation(fsp, forward_graph,insert_prob=0.5):
    fsp_nested = fsp
    new_fsp_nested = deepcopy(fsp_nested)
    seen = set(f for turn in fsp_nested for f in turn)  # 当前所有函数（避免重复插入）

    for i in reversed(range(len(fsp_nested))):
        if random.random()<insert_prob:
            continue
        turn = fsp_nested[i]
        last_func = turn[-1]
        neighbors = forward_graph.get(last_func, [])
        if neighbors:
            neighbor = random.choice(neighbors)
            if neighbor not in seen:
                if random.random()<0.5:
                    # 插入当前轮末尾
                    new_fsp_nested[i].append(neighbor)
                else:
                    # 或是延后插入，随机插入到“更靠后”的地方
                    insert_index = random.randint(i + 1, len(new_fsp_nested))
                    new_fsp_nested.insert(insert_index, [neighbor])
                    seen.add(neighbor)

        fsp_nested = new_fsp_nested
        # print(f"fsp_nested:{fsp_nested}")
    return fsp_nested

def merge_operation(fsp, merge_probs={2: 0.3, 3: 0.1, 4:0.05}):
    # merge 使用的fsp是initial的fsp.
    # fsp_merged = [[f] for f in fsp]  # 每个函数初始作为一轮
    i = 0
    merged_fsp = []

    while i < len(fsp):
        r = random.random()
        merged = False

        for num_turns in sorted(merge_probs.keys(), reverse=True):  # 倒序遍历
            prob = merge_probs[num_turns]
            if r < prob and i + num_turns <= len(fsp):
                merged_turn = []
                for j in range(num_turns):
                    merged_turn += fsp[i + j]
                merged_fsp.append(merged_turn)
                i += num_turns
                merged = True
                break  # 合并成功就跳出循环

        if not merged:
            merged_fsp.append(deepcopy(fsp[i]))
            i += 1

    return merged_fsp

def parallel_operation(fsp, parallel_probs={2: 0.2, 3: 0.05}):
    # merge 使用的fsp是initial的fsp.
    # fsp_merged = [[f] for f in fsp]  # 每个函数初始作为一轮
    i = 0
    paralleled_fsp = []

    while i < len(fsp):
        if len(fsp[i])>1: #如果merge了就不parallel了
            paralleled_fsp.append(deepcopy(fsp[i]))
            i += 1
        else:
            r=random.random()
            parallel= False
            for num_turns in sorted(parallel_probs.keys(), reverse=True):  # 倒序遍历
                prob = parallel_probs[num_turns]
                if  r < prob:
                    parallel_turn = []
                    for j in range(num_turns):
                        parallel_turn += fsp[i]
                    paralleled_fsp.append(parallel_turn)
                    i += 1
                    parallel=True
                    break

            if not parallel:
                paralleled_fsp.append(deepcopy(fsp[i]))
                i += 1

    return paralleled_fsp

def miss_param_operation(fsp, miss_param_prob=0.5):
    # merge 使用的fsp是initial的fsp.
    # fsp_merged = [[f] for f in fsp]  # 每个函数初始作为一轮
    i = 0
    new_fsp = []

    while i < len(fsp):
        if len(fsp[i])>1: #只对单个函数用miss_param
            new_fsp.append(deepcopy(fsp[i]))
            i += 1
        #函数的参数小于等于3个
        elif len(function_pool_index[fsp[i][0]]["parameters"]["properties"])<=3:
            new_fsp.append(deepcopy(fsp[i]))
            i += 1
        else:
            r=random.random()
            if  r < miss_param_prob:
                new_turn = fsp[i] + ["__miss params__"]
                new_fsp.append(new_turn)
                i += 1

            else:
                new_fsp.append(deepcopy(fsp[i]))
                i += 1

    return new_fsp

def miss_func_operation(fsp, miss_func_probs={1:1,2:0.3}):
    # 执行插入
    miss_func_fsp = deepcopy(fsp)
    r=random.random()
    split=False
    for num in sorted(miss_func_probs.keys(), reverse=True):  # 倒序遍历
        prob = miss_func_probs[num]
        if r < prob and split==False:
            for i in range(num):
                insert_index = random.randint(0, len(miss_func_fsp) - 1)
                miss_func_fsp.insert(insert_index, ["__miss func__"])
            split=True
    return miss_func_fsp

def enhance_fsp_with_all_operations(fsp, forward_graph, 
                                     merge_probs={2: 0.3, 3: 0.1, 4:0.05}, 
                                     parallel_probs={2: 0.2, 3: 0.05},
                                     insert_prob=0.5, 
                                     miss_func_probs={1:1,2:0.3}, 
                                     miss_param_prob=0.5,
                                     ):

    # 1. Merge
    merged_fsp = merge_operation(fsp, merge_probs=merge_probs)
    print(f"\nmerged_fsp:{merged_fsp}")

    # 3. Insert
    inserted_fsp = insert_operation(merged_fsp, forward_graph, insert_prob=insert_prob)
    print(f"inserted_fsp:{inserted_fsp}")

    # 3. parallel
    paralleled_fsp = parallel_operation(inserted_fsp, parallel_probs=parallel_probs)
    print(f"paralleled_fsp:{paralleled_fsp}")

    # 4. miss_param
    miss_param_fsp = miss_param_operation(paralleled_fsp, miss_param_prob=miss_param_prob)
    print(f"miss_param_fsp:{miss_param_fsp}")

    # 4. miss_func
    miss_func_fsp = miss_func_operation(miss_param_fsp, miss_func_probs=miss_func_probs)
    print(f"miss_func_fsp:{miss_func_fsp}")

    return miss_func_fsp

def load_generated_fsps(input_file="generated_init_fsps.json"):
    with open(input_file, "r") as f:
        fsps = json.load(f)
    return fsps

def detect_fsp_mode(fsp):
    mode_list=[]
    for task in fsp:
        counter = Counter(task)
        total_tool_calls = sum(counter.values()) - counter.get('__miss func__', 0)
        multiple_or_dependent = 1 if len(counter)- counter.get('__miss params__', 0) > 1 else 0
        parallel = 1 if any(v > 1 for v in counter.values()) else 0
        miss_func = counter.get('__miss func__', 0)
        miss_params = counter.get('__miss params__', 0)
        single = 1 if total_tool_calls == 1 and not miss_func and not miss_params else 0
        flags = {
            "multiple_or_dependent": multiple_or_dependent,
            "parallel": parallel,
            "single": single,
            "miss_func": miss_func,
            "miss_params": miss_params
        }

        assert sum(flags.values())==1
        mode = next(k for k, v in flags.items() if v)
        mode_list.append(mode)
    return mode_list

    
# 处理所有生成的 FSP 并计算 fsp_phi 和 fsp_phi_hat
def enhance_generated_fsps(graph_path,tool_file_graph_path,input_file, output_file,limit_functions=[]):
    # 读取生成的路径文件
    fsps = load_generated_fsps(input_file)
    
    # 加载依赖数据
    graph = load_graph(graph_path,limit_functions)
    tool_file_graph = load_graph(tool_file_graph_path)
    
    # 计算 fsp_phi 和 fsp_phi_hat
    results = []
    for fsp in fsps:
        fsp = [[f] for f in fsp]  # 每个函数初始作为一轮
        enhanced_fsp = enhance_fsp_with_all_operations(
            fsp=fsp,
            forward_graph=graph,
            parallel_probs={2: 0.4, 3: 0.1},
            merge_probs={2: 0.5, 3: 0.2, 4:0.05},
            insert_prob=0.5,
            miss_func_probs={1:1,2:0.3,3:0.3},
            miss_param_prob=0.8,
        )
        mode_list=detect_fsp_mode(enhanced_fsp)
        selected_files = select_files_for_fsps(
            fsp=enhanced_fsp,
            tool_file_graph=tool_file_graph,
        )
        results.append({
            "data_id": str(uuid.uuid4()),
            "original_fsp": fsp,
            "enhanced_fsp": enhanced_fsp,
            "fsp_mode": mode_list,
            "selected_files": selected_files,
        })

    fsp_list=[result["enhanced_fsp"] for result in results]
    print(fsps_statistics(fsp_list))
    # 将结果存储到 JSON 文件中
    with open(output_file, "w") as f:
        json.dump(results, f, indent=4, ensure_ascii=False)
    
    print(f"已处理 {len(results)} 条路径，并存储到文件 {output_file}")



if __name__ == "__main__":
    random.seed(41)
    import fsp_generate,data_generate
    fsp_dir = os.path.dirname(fsp_generate.__file__)
    project_dir = os.path.dirname(data_generate.__file__)
    # function_pool_index = load_functions(f'{project_dir}/tools/all_tools_metadata.json',
    #                         limit_categories=['file_system_functions', 'python_functions', 'database_functions','api_functions'])
    function_pool_index = load_functions(f'{project_dir}/tools/all_tools_metadata.json')
    functions=list(function_pool_index.keys())
    enhance_generated_fsps(
                    graph_path = f"{fsp_dir}/data/graph/tool_dependency_graph.json",
                    tool_file_graph_path = f"{fsp_dir}/data/graph/file_tool_dependency_graph.json",
                    input_file=f"{fsp_dir}/data/generated_fsps_execute_step5_1000_0810_all_self+xlam.json",
                    output_file=f"{fsp_dir}/data/generated_fsps_execute_step5_1000_0810_all_self+xlam_enhance.json",
                    limit_functions=functions)

