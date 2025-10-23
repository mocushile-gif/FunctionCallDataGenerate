import re
import os
import json
from collections import deque
import random
from fsp_generate.utils.load_utils import *
from fsp_generate.utils.print_graph import print_graph

def induced_edges(graph, nodes):
    """返回在给定节点集合上的有向诱导边集合"""
    edges = []
    node_set = set(nodes)
    for u in nodes:
        for v in graph.get(u, []):
            if v in node_set:
                edges.append([u, v])
    return edges

def sample_connected_subgraph(graph, tool_file_graph, start_node, target_size, allowed_nodes=None):
    """
    从 start_node 出发，用BFS/随机扩张采样一个规模为 target_size 的连通子图（在有向图上以无向连通来近似）。
    若可达节点不足以凑够 target_size，则返回 None。
    """
    if allowed_nodes is None:
        allowed_nodes = set(graph.keys())
    if start_node not in allowed_nodes:
        return None

    nodes = [start_node]
    visited = {start_node}
    # 无向邻接视角：把出边和入边都视作邻接，用于连通扩张
    # 为效率，这里动态求“入邻居”：逆邻表可按需构建或临时扫描
    frontier = [start_node]

    while len(nodes) < target_size and frontier:
        cur = random.choice(frontier)
        # 出邻居
        nbrs_out = graph.get(cur, [])
        # 入邻居（扫描一次，规模大时可预构逆邻表）
        nbrs_in = [u for u, outs in graph.items() if cur in outs]

        candidates = [n for n in (nbrs_out + nbrs_in)
                      if n in allowed_nodes and n not in visited]

        if not candidates:
            # 当前frontier无扩张，换一个frontier点
            frontier.remove(cur)
            continue

        nxt = random.choice(candidates)
        visited.add(nxt)
        nodes.append(nxt)
        frontier.append(nxt)

        # 如果 cur 已无可扩张邻居，移出frontier
        # （这里不强制移出，让其可能再次被选中检查其他邻居）
        # 可按需精简frontier

    if len(nodes) < target_size:
        return None

    # 诱导子图边（保持原有向性）
    edges = induced_edges(graph, nodes)
    # 随机选择点对应的文件
    files = select_files_for_functions(nodes, tool_file_graph) if tool_file_graph else []
    print(f"\ntools number: {subgraph_size}\nfiles number: {len(files)}")
    subgraph={"nodes": nodes, "edges":edges, "files":files}
    print(print_graph(subgraph))
    return subgraph

def sample_connected_subgraph_bfs(graph, tool_file_graph, start_node, target_size, allowed_nodes=None):
    """
    从 start_node 出发，用严格 BFS 扩张采样一个规模为 target_size 的连通子图。
    BFS 保证按层次扩展，邻居加入顺序固定（按 graph 中的顺序）。
    """
    if allowed_nodes is None:
        allowed_nodes = set(graph.keys())
    if start_node not in allowed_nodes:
        return None

    visited = {start_node}
    queue = deque([start_node])

    while queue and len(visited) < target_size:
        cur = queue.popleft()

        # 出邻居
        nbrs_out = graph.get(cur, [])
        # 入邻居（无向连通性考虑）
        nbrs_in = [u for u, outs in graph.items() if cur in outs]

        for nbr in nbrs_out + nbrs_in:
            if nbr in allowed_nodes and nbr not in visited:
                visited.add(nbr)
                queue.append(nbr)
                if len(visited) >= target_size:
                    break

    if len(visited) < target_size:
        return None  # 不够规模

    # 诱导子图边（保持原有向性）
    nodes=list(visited)
    edges = induced_edges(graph, nodes)
    # 随机选择点对应的文件
    files = select_files_for_functions(nodes, tool_file_graph) if tool_file_graph else []
    print(f"\ntools number: {subgraph_size}\nfiles number: {len(files)}")
    subgraph={"nodes": nodes, "edges":edges, "files":files}
    print(print_graph(subgraph))
    return subgraph

def sample_subgraphs(graph, tool_file_graph=None, num_subgraphs=5, subgraph_size=5, allowed_nodes=None, max_attempts_per_item=100, mode='random'):
    """
    采样固定数量的连通子图；做简单去重（按节点集合）。
    """
    if allowed_nodes is None:
        allowed_nodes = set(graph.keys())
    allowed_nodes = [n for n in allowed_nodes if n in graph]

    results = []
    seen = set()  # 用节点集合（排序后的tuple）去重
    attempts = 0
    max_attempts = max_attempts_per_item * max(1, num_subgraphs)

    while len(results) < num_subgraphs and attempts < max_attempts:
        attempts += 1
        if not allowed_nodes:
            break
        start = random.choice(allowed_nodes)
        if mode=='random':
            subg = sample_connected_subgraph(graph, tool_file_graph, start, subgraph_size, allowed_nodes=set(allowed_nodes))
        elif mode=='bfs':
            subg = sample_connected_subgraph_bfs(graph, tool_file_graph, start, subgraph_size, allowed_nodes=set(allowed_nodes))
        if subg is None:
            continue
        key = tuple(sorted(subg["nodes"]))
        if key in seen:
            continue
        seen.add(key)
        results.append(subg)

    if len(results) < num_subgraphs:
        print(f"⚠️ 目标 {num_subgraphs} 个子图，仅采到 {len(results)} 个（可增大尝试次数或减小规模）。")

    return results

def generate_subgraph_data(dependency_data_path,
                           tool_file_graph_path,
                           limit_functions=None,
                           num_subgraphs=5,
                           subgraph_size=5,
                           output_file=None):
    """
    从依赖图中随机采样固定数量的连通子图，并写入文件。
    """
    graph = load_graph(dependency_data_path, limit_functions or [])
    tool_file_graph = load_graph(tool_file_graph_path)

    subgraphs = sample_subgraphs(graph,
                                 tool_file_graph=tool_file_graph,
                                 num_subgraphs=num_subgraphs,
                                 subgraph_size=subgraph_size,
                                 allowed_nodes=set(limit_functions) if limit_functions else None)
    if output_file:
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(subgraphs, f, indent=4, ensure_ascii=False)
        print(f"✅ 已生成 {len(subgraphs)} 个子图，保存到 {output_file}")
    else:
        print(f"✅ 已生成 {len(subgraphs)} 个子图")
    return subgraphs

def select_files_for_functions(functions, tool_file_graph):
    tool_files = defaultdict(list)  # func -> list of files（一个函数多次出现就存多个）

    for func in functions:
        relevant_files = set(tool_file_graph.get(func, []))
        if not relevant_files:
            tool_files[func].append(None)
            continue

        # 获取其他函数的相关文件
        other_funcs = [f for f in functions if f != func]
        other_files = set()
        for other in other_funcs:
            other_files.update(tool_file_graph.get(other, []))

        intersect = relevant_files & other_files
        if intersect:
            selected = random.choice(list(intersect))
        else:
            selected = random.choice(list(relevant_files))

        tool_files[func].append(selected)  # 每次都添加一次对应文件

    selected_files = set()
    for func in functions:
        file = tool_files[func].pop(0)
        selected_files.add(file)
    return list(selected_files)

if __name__ == "__main__":
    random.seed(42)
    import fsp_generate, data_generate
    fsp_dir = os.path.dirname(fsp_generate.__file__)
    project_dir = os.path.dirname(data_generate.__file__)

    # 可选：限制函数池（白名单）
    function_pool_index = load_functions(f'{project_dir}/tools/all_tools_metadata.json',
                            limit_categories=['file_system_functions', 'python_functions', 'database_functions','api_functions'])
    # function_pool_index = load_functions(f'{project_dir}/tools/all_tools_metadata.json')
    functions = list(function_pool_index.keys())

    # 配置
    num_subgraphs = 1    # 采样子图数量
    subgraph_size = 5       # 每个子图的节点数
    date = '0810_all_self+xlam'

    graph_data = f"{fsp_dir}/data/graph/tool_dependency_graph.json"
    tool_file_graph_path = f"{fsp_dir}/data/graph/file_tool_dependency_graph.json"
    # output_file = f"{fsp_dir}/data/generated_subgraphs_size{subgraph_size}_{num_subgraphs}_{date}.json"

    subgraphs = generate_subgraph_data(
        graph_data,
        tool_file_graph_path = tool_file_graph_path,
        limit_functions=functions,   # 若不想限制，传 None 或 []
        num_subgraphs=num_subgraphs,
        subgraph_size=subgraph_size,
        # output_file=output_file
    )
    print(subgraphs[0]['nodes'])