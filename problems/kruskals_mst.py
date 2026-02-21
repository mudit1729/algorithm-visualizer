from __future__ import annotations

from core.step import Step
from core.tracer import AuxPanelTracer, GraphTracer, combine_step
from problems.base_problem import Problem

_SOURCE = """\
def kruskal_mst(n, edges):
    edges.sort(key=lambda e: e[2])
    parent = list(range(n))
    rank = [0] * n
    mst = []
    mst_cost = 0

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

    for u, v, w in edges:
        if union(u, v):
            mst.append((u, v, w))
            mst_cost += w
        if len(mst) == n - 1:
            break

    return mst_cost, mst"""


class KruskalsMST(Problem):
    @staticmethod
    def name() -> str:
        return "Kruskal's MST"

    @staticmethod
    def topic() -> str:
        return "Minimum Spanning Tree"

    @staticmethod
    def subtopic() -> str:
        return "Kruskal's Algorithm"

    @staticmethod
    def description() -> str:
        return "Build a minimum spanning tree by sorting edges and using Union-Find to avoid cycles."

    @staticmethod
    def long_description() -> str:
        return (
            "Kruskal's algorithm builds a minimum spanning tree (MST) by sorting "
            "all edges by weight and greedily adding the cheapest edge that does "
            "not form a cycle. A Union-Find (DSU) data structure is used to "
            "efficiently detect cycles.\n\n"
            "Time Complexity: O(E log E) for sorting edges.\n\n"
            "Constraints:\n\n"
            "- Graph must be connected and undirected\n"
            "- Edge weights can be negative\n"
            "- The MST has exactly V-1 edges"
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
            1: [
                (0, 1, 4), (0, 7, 8), (1, 2, 8), (1, 7, 3),
                (2, 3, 7), (2, 5, 4), (3, 4, 9), (3, 5, 6),
                (4, 5, 10), (5, 6, 2), (6, 7, 1), (6, 0, 5),
            ],
        }

        edge_list = presets.get(preset, presets[1])
        n = 8

        graph = GraphTracer(list(range(n)), directed=False)
        aux = AuxPanelTracer()
        aux.add_panel("DSU Parent")
        steps: list[Step] = []

        parent = list(range(n))
        rank = [0] * n

        def update_aux() -> None:
            aux.set_items(
                "DSU Parent",
                [(str(i), str(parent[i])) for i in range(n)],
            )

        def snap(line: int, desc: str = "") -> None:
            steps.append(combine_step(graph.snapshot(line, desc), aux))

        # Add all edges to the tracer
        for u, v, w in edge_list:
            graph.add_edge(u, v, weight=w)

        update_aux()
        graph.log(f"Kruskal's MST: {n} nodes, {len(edge_list)} edges")
        snap(1, f"{n} nodes, {len(edge_list)} edges")

        # Sort edges by weight
        sorted_edges = sorted(edge_list, key=lambda e: e[2])
        sorted_str = ", ".join(f"{u}-{v}(w={w})" for u, v, w in sorted_edges)
        graph.log(f"Sorted edges: {sorted_str}")
        snap(2, "Sort edges by weight")

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

        mst: list[tuple[int, int, int]] = []
        mst_cost = 0

        for u, v, w in sorted_edges:
            edge_key = (u, v) if (u, v) in graph._edge_selected else (v, u)

            # Highlight the edge being considered
            graph.deselect_all_nodes()
            graph.deselect_all_edges()
            graph.clear_all_edge_errors()
            graph.select_node(u)
            graph.select_node(v)
            graph.select_edge(*edge_key)
            graph.log(f"Consider edge {u}-{v} (w={w})")
            snap(26, f"Consider edge {u}-{v}, w={w}")

            if union(u, v):
                mst.append((u, v, w))
                mst_cost += w
                graph.patch_edge(*edge_key)
                graph.patch_node(u)
                graph.patch_node(v)
                update_aux()
                graph.log(f"  Accept! MST cost = {mst_cost}")
                snap(28, f"Accept {u}-{v}, cost = {mst_cost}")
            else:
                graph.mark_edge_error(*edge_key)
                graph.mark_node_error(u)
                graph.mark_node_error(v)
                graph.log(f"  Reject! Cycle detected (same root)")
                snap(17, f"Reject {u}-{v}: cycle")

                # Clear errors after showing
                graph.clear_all_edge_errors()
                graph.clear_all_node_errors()

            graph.deselect_all_nodes()
            graph.deselect_all_edges()

            if len(mst) == n - 1:
                graph.log(f"MST complete with {n - 1} edges")
                snap(31, f"MST complete, {n - 1} edges found")
                break

        # Final result
        graph.deselect_all_nodes()
        graph.deselect_all_edges()
        mst_str = ", ".join(f"{u}-{v}(w={w})" for u, v, w in mst)
        graph.log(f"MST cost = {mst_cost}, edges: {mst_str}")
        snap(31, f"Kruskal's MST complete, total cost = {mst_cost}")
        return steps
