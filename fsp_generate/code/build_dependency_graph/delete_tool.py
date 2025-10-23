from __future__ import annotations

from typing import Dict, Tuple, Iterable, Optional, List, Set

from fsp_generate.utils.load_utils import (
    load_relation_cache,
    save_relation_cache,
    load_graph,
)


class DependencyGraphEditor:
    """
    依赖图编辑器：用于删除点、批量修改边等。

    说明：
    - 基于 `relation_cache_file`（如 `file_tool_dependency_graph.json`）进行读写。
    - relation_cache 的内部结构为：{ (source, target): bool }
    - 仅当 bool 为 True 时，该边才会出现在由 `load_graph` 生成的有向图中。
    """

    def __init__(self, relation_cache_file: str):
        self.relation_cache_file: str = relation_cache_file
        self.relation_cache: Dict[Tuple[str, str], bool] = load_relation_cache(
            relation_cache_file
        )

    # ---------- 基本读写 ----------
    def reload(self) -> None:
        """从磁盘重新载入 relation_cache。"""
        self.relation_cache = load_relation_cache(self.relation_cache_file)

    def save(self) -> None:
        """将当前 relation_cache 保存到磁盘。"""
        save_relation_cache(self.relation_cache, self.relation_cache_file)

    def get_true_graph(self, limit_nodes: Optional[Iterable[str]] = None):
        """
        返回当前为 True 的边构成的图（defaultdict(list)）。
        - limit_nodes 不为 None 时，仅返回该集合内部的子图。
        """
        limit_list: List[str] = list(limit_nodes) if limit_nodes else []
        # 直接复用现有的构图逻辑（它会从文件读取）。
        # 为确保同步，先保存到文件，再读取。
        self.save()
        return load_graph(self.relation_cache_file, limit_nodes=limit_list)

    # ---------- 点级操作 ----------
    def delete_nodes(self, nodes: Iterable[str]) -> int:
        """
        删除一组点：移除所有与这些点相关的边（入边与出边）。
        返回：被删除的边数量。
        """
        node_set: Set[str] = set(nodes)
        to_delete: List[Tuple[str, str]] = [
            pair for pair in self.relation_cache.keys() if pair[0] in node_set or pair[1] in node_set
        ]
        for pair in to_delete:
            self.relation_cache.pop(pair, None)
        return len(to_delete)

    # ---------- 边级批量操作 ----------
    def set_outgoing(self, source: str, value: bool = True, targets: Optional[Iterable[str]] = None, create_missing: bool = False) -> int:
        """
        设置某点的出边为指定布尔值。
        - 当 targets 为 None：仅对当前 relation_cache 中以 source 为起点的所有边进行设置。
        - 当 targets 为给定列表：仅对这些 (source, t) 进行设置；若 create_missing=True，则会为不存在的边创建记录。
        返回：被修改/创建的边数量。
        """
        modified = 0
        if targets is None:
            for (s, t) in list(self.relation_cache.keys()):
                if s == source:
                    if self.relation_cache[(s, t)] != value:
                        self.relation_cache[(s, t)] = value
                        modified += 1
        else:
            target_list = list(targets)
            for t in target_list:
                key = (source, t)
                if key in self.relation_cache:
                    if self.relation_cache[key] != value:
                        self.relation_cache[key] = value
                        modified += 1
                else:
                    if create_missing:
                        self.relation_cache[key] = value
                        modified += 1
        return modified

    def set_incoming(self, target: str, value: bool = True, sources: Optional[Iterable[str]] = None, create_missing: bool = False) -> int:
        """
        设置某点的入边为指定布尔值。
        - 当 sources 为 None：仅对当前 relation_cache 中以 target 为终点的所有边进行设置。
        - 当 sources 为给定列表：仅对这些 (s, target) 进行设置；若 create_missing=True，则会为不存在的边创建记录。
        返回：被修改/创建的边数量。
        """
        modified = 0
        if sources is None:
            for (s, t) in list(self.relation_cache.keys()):
                if t == target:
                    if self.relation_cache[(s, t)] != value:
                        self.relation_cache[(s, t)] = value
                        modified += 1
        else:
            source_list = list(sources)
            for s in source_list:
                key = (s, target)
                if key in self.relation_cache:
                    if self.relation_cache[key] != value:
                        self.relation_cache[key] = value
                        modified += 1
                else:
                    if create_missing:
                        self.relation_cache[key] = value
                        modified += 1
        return modified

    def set_edges(self, pairs: Iterable[Tuple[str, str]], value: bool = True, create_missing: bool = True) -> int:
        """
        批量设置若干边的布尔值。
        - create_missing=True 时，对于不存在的边会创建记录。
        返回：被修改/创建的边数量。
        """
        modified = 0
        for key in pairs:
            if key in self.relation_cache:
                if self.relation_cache[key] != value:
                    self.relation_cache[key] = value
                    modified += 1
            else:
                if create_missing:
                    self.relation_cache[key] = value
                    modified += 1
        return modified

    def remove_edges(self, pairs: Iterable[Tuple[str, str]]) -> int:
        """
        批量删除若干边（无论之前值为何）。
        返回：被删除的边数量。
        """
        removed = 0
        for key in pairs:
            if key in self.relation_cache:
                self.relation_cache.pop(key, None)
                removed += 1
        return removed


__all__ = ["DependencyGraphEditor"]


if __name__ == "__main__":
    # 简单示例（按需手动修改路径与节点）
    # 用法：python delete_tool.py
    relation_path = "/mnt/afs2/qinxinyi/function_call_data/fsp_generate/data/graph/file_tool_dependency_graph.json"
    editor = DependencyGraphEditor(relation_path)

    # 示例：删除点
    # removed = editor.delete_nodes(["some_tool", "some/file.py"])
    # print(f"Removed edges: {removed}")

    # 示例：将某点的出边全部设为 True（仅针对已存在的出边）
    # changed = editor.set_outgoing("some_tool", value=True)
    # print(f"Changed edges: {changed}")

    # 保存更改
    editor.save()