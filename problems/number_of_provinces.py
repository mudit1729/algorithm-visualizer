from __future__ import annotations

from core.step import Step
from core.tracer import GraphTracer
from problems.base_problem import Problem

_SOURCE = """\
def findCircleNum(isConnected):
    n = len(isConnected)
    parent = list(range(n))
    rank = [0] * n

    def find(x):
        if parent[x] != x:
            parent[x] = find(parent[x])
        return parent[x]

    def union(x, y):
        rx, ry = find(x), find(y)
        if rx == ry:
            return 0
        if rank[rx] < rank[ry]:
            rx, ry = ry, rx
        parent[ry] = rx
        if rank[rx] == rank[ry]:
            rank[rx] += 1
        return 1

    components = n
    for i in range(n):
        for j in range(i + 1, n):
            if isConnected[i][j] == 1:
                components -= union(i, j)

    return components"""


class NumberOfProvinces(Problem):
    @staticmethod
    def name() -> str:
        return "Number of Provinces"

    @staticmethod
    def topic() -> str:
        return "Union Find"

    @staticmethod
    def subtopic() -> str:
        return "Connected Components"

    @staticmethod
    def description() -> str:
        return "LeetCode #547: Count connected components using Union-Find."

    @staticmethod
    def long_description() -> str:
        return (
            "Given an `n x n` adjacency matrix `isConnected` where "
            "`isConnected[i][j] = 1` means cities `i` and `j` are directly "
            "connected, return the number of **provinces** (connected "
            "components). Solved using Union-Find with path compression and "
            "union by rank.\n\n"
            "Example 1:\n"
            "Input: `isConnected = [[1,1,0],[1,1,0],[0,0,1]]`\n"
            "Output: `2`\n\n"
            "Constraints:\n\n"
            "- `1 <= n <= 200`\n"
            "- `isConnected[i][j]` is `0` or `1`\n"
            "- `isConnected[i][i] == 1`\n"
            "- Matrix is symmetric"
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
            # 8 cities, 3 provinces: {0,1,2}, {3,4,5}, {6,7}
            1: [
                [1, 1, 1, 0, 0, 0, 0, 0],
                [1, 1, 0, 0, 0, 0, 0, 0],
                [1, 0, 1, 0, 0, 0, 0, 0],
                [0, 0, 0, 1, 1, 1, 0, 0],
                [0, 0, 0, 1, 1, 0, 0, 0],
                [0, 0, 0, 1, 0, 1, 0, 0],
                [0, 0, 0, 0, 0, 0, 1, 1],
                [0, 0, 0, 0, 0, 0, 1, 1],
            ],
        }

        is_connected = presets.get(preset, presets[1])
        n = len(is_connected)

        parent = list(range(n))
        rank = [0] * n

        tracer = GraphTracer(list(range(n)), directed=False)
        steps: list[Step] = []

        # Province colors
        province_colors = [
            "#89b4fa",  # blue
            "#a6e3a1",  # green
            "#fab387",  # peach
            "#cba6f7",  # mauve
            "#f38ba8",  # red
            "#89dceb",  # sky
        ]

        def snap(line: int, desc: str = "") -> None:
            steps.append(tracer.snapshot(line, desc))

        # Add all edges up front
        for i in range(n):
            for j in range(i + 1, n):
                if is_connected[i][j] == 1:
                    tracer.add_edge(i, j)

        tracer.log(f"Cities: {n}, each its own province")
        snap(3, f"{n} cities, each its own province")

        def find(x: int) -> int:
            if parent[x] != x:
                parent[x] = find(parent[x])
            return parent[x]

        def union(x: int, y: int) -> int:
            rx, ry = find(x), find(y)
            if rx == ry:
                return 0
            if rank[rx] < rank[ry]:
                rx, ry = ry, rx
            parent[ry] = rx
            if rank[rx] == rank[ry]:
                rank[rx] += 1
            return 1

        components = n
        for i in range(n):
            for j in range(i + 1, n):
                if is_connected[i][j] == 1:
                    tracer.deselect_all_nodes()
                    tracer.select_node(i)
                    tracer.select_node(j)
                    tracer.select_edge(i, j)
                    tracer.log(f"Edge ({i},{j}): connected")
                    snap(25, f"Check edge ({i},{j})")

                    ri, rj = find(i), find(j)
                    if ri == rj:
                        tracer.log(f"  Already same province")
                        tracer.deselect_edge(i, j)
                        tracer.patch_edge(i, j)
                        snap(26, f"Already connected")
                    else:
                        union(i, j)
                        components -= 1
                        tracer.patch_edge(i, j)
                        # Color all nodes by their root
                        for k in range(n):
                            root = find(k)
                            c = province_colors[root % len(province_colors)]
                            tracer.set_node_color(k, c)
                        tracer.log(f"  Union! Provinces = {components}")
                        snap(28, f"Union! Provinces = {components}")

                    tracer.deselect_all_edges()

        tracer.deselect_all_nodes()
        tracer.log(f"Result: {components} provinces")
        snap(28, f"Result: {components} provinces")
        return steps
