from __future__ import annotations

from core.step import Step
from core.tracer import GraphTracer
from problems.base_problem import Problem

_SOURCE = """\
def findRedundantConnection(edges):
    n = len(edges)
    parent = list(range(n + 1))
    rank = [0] * (n + 1)

    def find(x):
        if parent[x] != x:
            parent[x] = find(parent[x])
        return parent[x]

    def union(x, y):
        rx, ry = find(x), find(y)
        if rx == ry:
            return False
        if rank[rx] < rank[ry]:
            rx, ry = ry, rx
        parent[ry] = rx
        if rank[rx] == rank[ry]:
            rank[rx] += 1
        return True

    for u, v in edges:
        if not union(u, v):
            return [u, v]"""


class RedundantConnection(Problem):
    @staticmethod
    def name() -> str:
        return "Redundant Connection"

    @staticmethod
    def topic() -> str:
        return "Union-Find"

    @staticmethod
    def subtopic() -> str:
        return "Cycle Detection"

    @staticmethod
    def description() -> str:
        return "LeetCode #684: Find the edge that creates a cycle in a tree + 1 extra edge."

    @staticmethod
    def long_description() -> str:
        return (
            "A tree with `n` nodes (labeled `1` to `n`) had one extra edge "
            "added, creating exactly one cycle. Given the list of edges, find "
            "the edge that can be removed to restore a valid tree. If multiple "
            "answers exist, return the one that appears last in the input.\n\n"
            "Example 1:\n"
            "Input: `edges = [[1,2],[1,3],[2,3]]`\n"
            "Output: `[2,3]`\n\n"
            "Constraints:\n\n"
            "- `3 <= n <= 1000`\n"
            "- No repeated edges\n"
            "- The graph is connected"
        )

    @staticmethod
    def source_code() -> str:
        return _SOURCE

    @staticmethod
    def renderer_type() -> str:
        return "graph"

    @staticmethod
    def default_params() -> dict[str, object]:
        return {"preset": 1}

    @staticmethod
    def generate_steps(**kwargs: object) -> list[Step]:
        preset = int(kwargs.get("preset", 1))

        presets = {
            # 8-node tree + 1 redundant edge (6->4 creates cycle)
            1: [
                [1, 2], [1, 3], [2, 4], [2, 5],
                [3, 6], [3, 7], [5, 8], [6, 4],
            ],
        }

        edges = presets.get(preset, presets[1])
        # Collect all unique node IDs
        node_set = set()
        for u, v in edges:
            node_set.add(u)
            node_set.add(v)
        node_ids = sorted(node_set)
        n = len(edges)

        parent = list(range(max(node_ids) + 1))
        rank = [0] * (max(node_ids) + 1)

        tracer = GraphTracer(node_ids, directed=False)
        steps: list[Step] = []

        def snap(line: int, desc: str = "") -> None:
            steps.append(tracer.snapshot(line, desc))

        edges_str = ", ".join(f"{u}-{v}" for u, v in edges)
        tracer.log(f"Nodes: {len(node_ids)}, Edges: {edges_str}")
        snap(3, f"Edges: {edges_str}")

        def find(x: int) -> int:
            if parent[x] != x:
                parent[x] = find(parent[x])
            return parent[x]

        def union(x: int, y: int) -> bool:
            rx, ry = find(x), find(y)
            if rx == ry:
                return False
            if rank[rx] < rank[ry]:
                rx, ry = ry, rx
            parent[ry] = rx
            if rank[rx] == rank[ry]:
                rank[rx] += 1
            return True

        redundant = None
        for u, v in edges:
            tracer.add_edge(u, v)
            tracer.deselect_all_nodes()
            tracer.deselect_all_edges()
            tracer.clear_all_node_errors()
            tracer.select_node(u)
            tracer.select_node(v)
            tracer.select_edge(u, v)
            tracer.log(f"Process edge [{u}, {v}]")
            snap(21, f"Add edge [{u}, {v}]")

            if not union(u, v):
                tracer.mark_node_error(u)
                tracer.mark_node_error(v)
                tracer.mark_edge_error(u, v)
                tracer.log(f"  CYCLE! [{u}, {v}] is redundant")
                snap(22, f"Redundant: [{u}, {v}]")
                redundant = [u, v]
                break
            else:
                tracer.patch_node(u)
                tracer.patch_node(v)
                tracer.patch_edge(u, v)
                tracer.log(f"  Union {u} & {v}")
                snap(22, f"Union {u} & {v}")

        tracer.deselect_all_nodes()
        tracer.deselect_all_edges()
        tracer.log(f"Result: {redundant}")
        snap(23, f"Redundant edge: {redundant}")
        return steps
