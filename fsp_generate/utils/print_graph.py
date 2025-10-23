#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ascii_graph.py
将无向图按 BFS 自动分层并渲染为多层 ASCII 文字图。

功能特性
- 输入: subgraph = {"nodes": [...], "edges": [[u, v], ...]}
- 无向图，自动去重自环/重复边
- 自动选择根（度数最高）或手动指定 root
- BFS 分层并绘制“父层 -> 子层”的连接线
- 画布自动扩展，避免标签覆盖；支持中文/英文节点名

用法
- 直接运行会用脚本内示例数据
- 如需指定根节点：在 main 最下方把 root 变量改为你想要的节点名

注意
- 这是 ASCII 文本可视化，复杂交叉边可能会重叠；脚本优先绘制 BFS 树边（每个节点的首个父边）
"""

from collections import defaultdict, deque
from typing import Dict, List, Tuple, Optional, Set

# ===================== 核心构建逻辑 =====================

def build_graph(subgraph: Dict) -> Dict[str, Set[str]]:
    """将 subgraph 转为无向邻接表，并去掉自环与重复边。"""
    g = defaultdict(set)
    nodes = list(subgraph.get("nodes", []))
    edges = list(subgraph.get("edges", []))

    for u in nodes:
        g[u]  # 确保孤立点也在图中

    for e in edges:
        if not isinstance(e, (list, tuple)) or len(e) != 2:
            continue
        u, v = e
        if u == v:
            continue
        g[u].add(v)
        g[v].add(u)
    return g


def choose_root(graph: Dict[str, Set[str]], preferred: Optional[str] = None) -> Optional[str]:
    """选择根节点：优先使用 preferred；否则选择度数最高节点；若图为空返回 None。"""
    if not graph:
        return None
    if preferred and preferred in graph:
        return preferred
    # 度数最高
    return max(graph.keys(), key=lambda x: (len(graph[x]), x))


def bfs_layers(graph: Dict[str, Set[str]], root: str) -> Tuple[List[List[str]], Dict[str, Optional[str]]]:
    """
    从 root 做 BFS，返回分层结果和 parent 映射（BFS 树）。
    layers[i] 为第 i 层节点（按字母序稳定排序）
    parent[x] 是 x 的 BFS 父节点（root 的父为 None）
    """
    seen = set([root])
    parent = {root: None}
    layers = [[root]]
    q = deque([root])

    while q:
        cur_layer_nodes = []
        # 逐层处理：先耗尽当前队列大小
        size = len(q)
        for _ in range(size):
            u = q.popleft()
            cur_layer_nodes.append(u)
        # 收集下一层
        next_nodes = []
        for u in cur_layer_nodes:
            for v in sorted(graph[u]):
                if v not in seen:
                    seen.add(v)
                    parent[v] = u
                    next_nodes.append(v)
                    q.append(v)
        if next_nodes:
            layers.append(sorted(next_nodes))
    return layers, parent


# ===================== 渲染为 ASCII =====================

class Canvas:
    """简单字符画布，支持按坐标写字符与写字符串。"""
    def __init__(self, rows: int, cols: int):
        self.rows = rows
        self.cols = cols
        self.grid = [[' ']*cols for _ in range(rows)]

    def draw_char(self, r: int, c: int, ch: str):
        if 0 <= r < self.rows and 0 <= c < self.cols:
            self.grid[r][c] = ch

    def draw_hline(self, r: int, c1: int, c2: int, ch: str = '-'):
        if r < 0 or r >= self.rows:
            return
        if c1 > c2:
            c1, c2 = c2, c1
        for c in range(c1, c2+1):
            self.draw_char(r, c, ch)

    def draw_vline(self, c: int, r1: int, r2: int, ch: str = '|'):
        if c < 0 or c >= self.cols:
            return
        if r1 > r2:
            r1, r2 = r2, r1
        for r in range(r1, r2+1):
            self.draw_char(r, c, ch)

    def draw_text(self, r: int, c: int, text: str):
        for i, ch in enumerate(text):
            self.draw_char(r, c+i, ch)

    def get(self) -> str:
        # 去掉右侧多余空格
        return "\n".join("".join(row).rstrip() for row in self.grid)


def render_ascii(layers: List[List[str]], parent: Dict[str, Optional[str]],
                 cell_w: int = 24, row_gap: int = 2) -> str:
    """
    将分层结果渲染为 ASCII 图。
    - cell_w: 每个“单元格”横向宽度，确保标签不重叠可适当调大
    - row_gap: 层与层之间的行距（包含连接线绘制空间）
    """
    if not layers:
        return "(empty graph)"

    # 计算画布尺寸
    max_layer_width = max(len(layer) for layer in layers)
    cols = max(1, max_layer_width) * cell_w
    # 每层占两行（节点行 + 连接线行），最后一层无连接线行；层间再插入行距
    rows = 0
    for i in range(len(layers)):
        rows += 1  # 节点行
        if i < len(layers) - 1:
            rows += row_gap  # 连接/空白行
    canvas = Canvas(rows, cols)

    # 计算每个节点的 (row, col) 位置，以及“锚点”用于连线（标签中心）
    node_pos: Dict[str, Tuple[int, int]] = {}
    anchor: Dict[str, Tuple[int, int]] = {}

    cur_row = 0
    for i, layer in enumerate(layers):
        # 为该层的每个节点分配列坐标（居中排列）
        n = len(layer)
        for j, node in enumerate(layer):
            text = f"[{node}]"
            # 节点左上角列坐标
            # 让这一层整体居中：起始偏移 = (cols - n*cell_w) // 2
            start_offset = max(0, (cols - n*cell_w) // 2)
            col = start_offset + j*cell_w + 1  # +1 看起来更美观
            canvas.draw_text(cur_row, col, text)

            # 记录位置
            node_pos[node] = (cur_row, col)
            # 锚点取标签中心位置（用于连线）
            center_c = col + len(text)//2
            anchor[node] = (cur_row, center_c)

        # 如果不是最后一层，预留连接线区域
        if i < len(layers) - 1:
            cur_row += row_gap
        # 跳到下一层的节点行
        cur_row += 1

    # 依据 BFS parent 画“父层 -> 子层”的连线（避免过度杂乱）
    for child, p in parent.items():
        if p is None:
            continue
        (pr, pc) = anchor[p]
        (cr, cc) = anchor[child]

        # 连接策略：
        # 1) 在父节点下一行放一个竖线起点，在子节点上一行放一个竖线终点
        # 2) 用水平线连接（父下竖线的行）到子上竖线的列
        # 3) 在折点放 '+'，竖线用 '|'，水平线用 '-'
        # 为了简单，连线走“先竖一小段 -> 横 -> 再竖一小段”
        up = min(pr, cr)
        down = max(pr, cr)
        mid_r = (pr + cr) // 2  # 中间水平线所在行（大致在两层之间）

        # 竖线：父到中间
        canvas.draw_vline(pc, pr+1, mid_r-1, '|')
        # 竖线：中间到子
        canvas.draw_vline(cc, mid_r+1, cr-1, '|')

        # 在折点打 '+'
        canvas.draw_char(mid_r, pc, '+')
        canvas.draw_char(mid_r, cc, '+')

        # 水平线：父折点到子折点
        if pc != cc:
            canvas.draw_hline(mid_r, pc+1, cc-1, '-')

    return canvas.get()


# ===================== 示例 & 入口 =====================

def print_graph(graph):
    # 构建图
    g = build_graph(graph)

    # 指定根（可改为 None 让程序自动选择度数最高者）
    root = None  # 例如改成: "remove_image_background"

    root = choose_root(g, preferred=root)
    if root is None:
        print("(empty graph)")
        return

    layers, parent = bfs_layers(g, root)
    art = render_ascii(layers, parent, cell_w=26, row_gap=2)

    print("BFS 层次（从根开始）:", " -> ".join(f"{{{', '.join(layer)}}}" for layer in layers))
    print("\nASCII 无向图（BFS 树连线）：\n")
    print(art)

if __name__ == "__main__":
    nodes = ['add_watermark', 'add_text_to_image', 'add_border', 'add_pdf_watermark', 'remove_image_background']
    edges = [
        ['add_watermark', 'add_border'],
        ['add_watermark', 'add_pdf_watermark'],
        ['add_watermark', 'add_text_to_image'],
        ['add_text_to_image', 'add_border'],
        ['add_text_to_image', 'add_pdf_watermark'],
        ['add_text_to_image', 'add_watermark'],
        ['add_border', 'add_text_to_image'],
        ['add_border', 'add_watermark'],
        ['add_pdf_watermark', 'add_watermark'],
        ['remove_image_background', 'add_border'],
        ['remove_image_background', 'add_pdf_watermark'],
        ['remove_image_background', 'add_text_to_image'],
        ['remove_image_background', 'add_watermark'],
    ]
    subgraph = {"nodes": nodes, "edges": edges}
    print_graph(subgraph)
