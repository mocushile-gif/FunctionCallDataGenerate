import pickle
import os
import networkx as nx
from pyvis.network import Network
import json

# 文件路径
dependency_dir = "/afs_b/qinxinyi/function_call_mt/tools_pool/dependency_graph/build_tool_graph"
relation_cache_file = os.path.join(dependency_dir, "tool_dependency_graph.json")
relation_cache_file = os.path.join(dependency_dir, "file_tool_dependency_graph.json")
output_html_path = os.path.join(dependency_dir, "tool_dependency_graph.html")
output_html_path = os.path.join(dependency_dir, "file_tool_dependency_graph.html")

# 加载缓存
if os.path.exists(relation_cache_file):
    with open(relation_cache_file, "r", encoding="utf-8") as f:
        raw_cache = json.load(f)
        relation_cache = {
            tuple(k.split(" → ", 1)): v for k, v in raw_cache.items()
        }
else:
    raise FileNotFoundError(f"No cache file found at: {relation_cache_file}")

# 构建图
G = nx.DiGraph()
for (source, target), is_related in relation_cache.items():
    if is_related:
        G.add_edge(source, target)

out_degrees = [(node, G.out_degree(node)) for node in G.nodes()]
out_degrees.sort(key=lambda x: x[1], reverse=True)

for node, degree in out_degrees:
    print(f"{node} → {degree} target(s)")

# # 可视化
net = Network(height="800px", width="100%", directed=True, notebook=False)
net.from_nx(G)
net.force_atlas_2based()  # 使用力导向布局增强结构清晰度
html = net.generate_html()
with open(output_html_path, "w", encoding="utf-8") as f:
    f.write(html)

print(f"✅ 可视化图已保存为: {output_html_path}")
