from __future__ import annotations

from core.step import Step
from core.tracer import GraphTracer
from problems.base_problem import Problem

_SOURCE = """\
def prim_mst(graph, n):
    in_mst = [False] * n
    key = [float('inf')] * n
    parent = [-1] * n
    key[0] = 0
    pq = [(0, 0)]
    mst_cost = 0

    while pq:
        w, u = heapq.heappop(pq)
        if in_mst[u]:
            continue
        in_mst[u] = True
        mst_cost += w

        for v, weight in graph[u]:
            if not in_mst[v] and weight < key[v]:
                key[v] = weight
                parent[v] = u
                heapq.heappush(pq, (weight, v))

    return mst_cost, parent"""


class PrimsMST(Problem):
    @staticmethod
    def name() -> str:
        return "Prim's MST"

    @staticmethod
    def topic() -> str:
        return "Minimum Spanning Tree"

    @staticmethod
    def subtopic() -> str:
        return "Prim's Algorithm"

    @staticmethod
    def description() -> str:
        return "Build a minimum spanning tree by greedily adding the cheapest edge from the growing tree."

    @staticmethod
    def long_description() -> str:
        return (
            "Prim's algorithm builds a minimum spanning tree (MST) by starting "
            "from an arbitrary node and repeatedly adding the cheapest edge that "
            "connects a node in the tree to a node outside the tree.\n\n"
            "It uses a min-priority queue to efficiently select the next minimum "
            "weight edge at each step.\n\n"
            "Time Complexity: O((V + E) log V) with a binary heap.\n\n"
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
        import heapq

        preset = int(kwargs.get("preset", 1))

        # edges: (u, v, weight) — undirected connected graph
        presets = {
            1: [
                (0, 1, 4), (0, 7, 8), (1, 2, 8), (1, 7, 3),
                (2, 3, 7), (2, 5, 4), (2, 8, 2), (3, 4, 9),  # note: node 8 not used
                (3, 5, 6), (4, 5, 10), (5, 6, 2), (6, 7, 1),
                (6, 0, 5),
            ],
        }

        # Use a better edge set with nodes 0-7 only
        presets = {
            1: [
                (0, 1, 4), (0, 7, 8), (1, 2, 8), (1, 7, 3),
                (2, 3, 7), (2, 5, 4), (3, 4, 9), (3, 5, 6),
                (4, 5, 10), (5, 6, 2), (6, 7, 1), (6, 0, 5),
            ],
        }

        edge_list = presets.get(preset, presets[1])
        n = 8

        # Build adjacency list
        graph: list[list[tuple[int, int]]] = [[] for _ in range(n)]
        for u, v, w in edge_list:
            graph[u].append((v, w))
            graph[v].append((u, w))

        tracer = GraphTracer(list(range(n)), directed=False)
        steps: list[Step] = []

        def snap(line: int, desc: str = "") -> None:
            steps.append(tracer.snapshot(line, desc))

        # Add edges to tracer
        for u, v, w in edge_list:
            tracer.add_edge(u, v, weight=w)

        tracer.log(f"Prim's MST: {n} nodes, {len(edge_list)} edges")
        snap(1, f"Prim's MST: {n} nodes")

        # Initialize
        in_mst = [False] * n
        key = [float("inf")] * n
        parent = [-1] * n
        key[0] = 0
        pq: list[tuple[int, int]] = [(0, 0)]
        mst_cost = 0

        for i in range(n):
            tracer.set_node_badge(i, "INF")
        tracer.set_node_badge(0, "0")
        tracer.log("key[0] = 0, all others = INF")
        snap(5, "Initialize key[0] = 0")

        while pq:
            w, u = heapq.heappop(pq)

            if in_mst[u]:
                tracer.log(f"Skip node {u} (already in MST)")
                snap(11, f"Skip node {u}, in MST")
                continue

            # Add node to MST
            tracer.select_node(u)
            tracer.log(f"Pop node {u} with key {w}")
            snap(10, f"Pop node {u}, key = {w}")

            in_mst[u] = True
            mst_cost += w
            tracer.patch_node(u)
            tracer.deselect_node(u)

            # Patch the MST edge (parent[u] -> u)
            if parent[u] != -1:
                p = parent[u]
                edge_key = (p, u) if (p, u) in tracer._edge_selected else (u, p)
                tracer.patch_edge(*edge_key)
                tracer.set_edge_class(*edge_key, "relaxed")
                tracer.log(f"  MST edge: {p}-{u} (w={w}), total cost = {mst_cost}")
                snap(13, f"MST edge {p}-{u}, cost = {mst_cost}")
            else:
                tracer.log(f"  Start node {u}, total cost = {mst_cost}")
                snap(12, f"Start node {u}")

            # Examine neighbors
            for v, weight in graph[u]:
                edge_key = (u, v) if (u, v) in tracer._edge_selected else (v, u)

                if in_mst[v]:
                    continue

                tracer.select_edge(*edge_key)
                tracer.log(f"  Examine edge {u}-{v} (w={weight})")
                snap(16, f"Check edge {u}-{v}, w={weight}")

                if weight < key[v]:
                    old_key = key[v]
                    key[v] = weight
                    parent[v] = u
                    heapq.heappush(pq, (weight, v))
                    tracer.set_node_badge(v, str(weight))
                    old_str = "INF" if old_key == float("inf") else str(int(old_key))
                    tracer.log(f"  Update key[{v}]: {old_str} -> {weight}")
                    snap(18, f"key[{v}]: {old_str} -> {weight}")
                else:
                    tracer.log(f"  No update for {v} (key={int(key[v])} <= {weight})")
                    snap(16, f"No update for {v}")

                tracer.deselect_edge(*edge_key)

        # Final result
        tracer.deselect_all_nodes()
        tracer.deselect_all_edges()
        mst_edges = []
        for i in range(n):
            if parent[i] != -1:
                mst_edges.append(f"{parent[i]}-{i}")
        tracer.log(f"MST cost = {mst_cost}, edges: {', '.join(mst_edges)}")
        snap(21, f"MST complete, total cost = {mst_cost}")
        return steps
