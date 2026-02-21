from __future__ import annotations

from core.step import Step
from core.tracer import GraphTracer
from problems.base_problem import Problem

_SOURCE = """\
def isBipartite(graph):
    n = len(graph)
    color = [-1] * n

    def dfs(u, c):
        color[u] = c
        for v in graph[u]:
            if color[v] == c:
                return False
            if color[v] == -1:
                if not dfs(v, 1 - c):
                    return False
        return True

    for i in range(n):
        if color[i] == -1:
            if not dfs(i, 0):
                return False
    return True"""


class IsBipartite(Problem):
    @staticmethod
    def name() -> str:
        return "Is Graph Bipartite?"

    @staticmethod
    def topic() -> str:
        return "Graph / DFS"

    @staticmethod
    def subtopic() -> str:
        return "2-Coloring"

    @staticmethod
    def description() -> str:
        return "LeetCode #785: Check if a graph can be 2-colored with no adjacent same-color nodes."

    @staticmethod
    def long_description() -> str:
        return (
            "Given an undirected graph as an adjacency list, determine if it is "
            "**bipartite** -- whether the nodes can be split into two groups such "
            "that every edge connects nodes in different groups. This is solved "
            "by attempting a 2-coloring via DFS.\n\n"
            "Example 1:\n"
            "Input: `graph = [[1,3],[0,2],[1,3],[0,2]]`\n"
            "Output: `true` (sets: `{0,2}` and `{1,3}`)\n\n"
            "Constraints:\n\n"
            "- `1 <= n <= 100`\n"
            "- `graph[u]` does not contain `u`\n"
            "- The graph is undirected (symmetric adjacency list)"
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
            # 8-node bipartite graph: {0,2,4,6} and {1,3,5,7}
            1: [
                [1, 3, 7],     # 0 -> 1,3,7
                [0, 2, 4],     # 1 -> 0,2,4
                [1, 5],        # 2 -> 1,5
                [0, 4],        # 3 -> 0,4
                [1, 3, 5],     # 4 -> 1,3,5
                [2, 4, 6],     # 5 -> 2,4,6
                [5, 7],        # 6 -> 5,7
                [0, 6],        # 7 -> 0,6
            ],
        }

        graph = presets.get(preset, presets[1])
        n = len(graph)

        tracer = GraphTracer(list(range(n)), directed=False)
        steps: list[Step] = []

        def snap(line: int, desc: str = "") -> None:
            steps.append(tracer.snapshot(line, desc))

        # Add edges (only one direction for undirected)
        added = set()
        for i in range(n):
            for j in graph[i]:
                key = (min(i, j), max(i, j))
                if key not in added:
                    tracer.add_edge(i, j)
                    added.add(key)

        edges_str = ", ".join(f"{a}-{b}" for a, b in sorted(added))
        tracer.log(f"Graph: {n} nodes, edges: {edges_str}")
        snap(3, f"{n} nodes, edges: {edges_str}")

        color_a = "#89b4fa"  # blue
        color_b = "#fab387"  # peach/orange
        color = [-1] * n
        is_bipartite = True

        def dfs(u: int, c: int) -> bool:
            nonlocal is_bipartite
            color[u] = c
            node_color = color_a if c == 0 else color_b
            tracer.set_node_color(u, node_color)
            tracer.select_node(u)
            tracer.log(f"Color node {u} = {'A (blue)' if c == 0 else 'B (orange)'}")
            snap(6, f"Color node {u} = {'A' if c == 0 else 'B'}")
            tracer.deselect_node(u)

            for v in graph[u]:
                if color[v] == c:
                    tracer.mark_node_error(u)
                    tracer.mark_node_error(v)
                    key = (min(u, v), max(u, v))
                    tracer.mark_edge_error(min(u, v), max(u, v))
                    tracer.log(f"  Conflict! Nodes {u} and {v} same color")
                    snap(8, f"Conflict: {u} & {v} same color!")
                    is_bipartite = False
                    return False
                if color[v] == -1:
                    tracer.log(f"  Edge {u}-{v}: color {v}")
                    snap(10, f"Visit {u}->{v}")
                    if not dfs(v, 1 - c):
                        return False
            return True

        for i in range(n):
            if color[i] == -1:
                tracer.log(f"Start DFS from node {i}")
                snap(16, f"Start component from {i}")
                if not dfs(i, 0):
                    break

        tracer.deselect_all_nodes()
        tracer.clear_all_node_errors()
        tracer.log(f"Result: {'Bipartite' if is_bipartite else 'Not bipartite'}")
        snap(19, f"Result: {'Bipartite' if is_bipartite else 'Not bipartite'}")
        return steps
