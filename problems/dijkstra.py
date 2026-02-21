from __future__ import annotations

from core.step import Step
from core.tracer import GraphTracer
from problems.base_problem import Problem

_SOURCE = """\
def dijkstra(graph, src):
    n = len(graph)
    dist = [float('inf')] * n
    dist[src] = 0
    visited = [False] * n
    pq = [(0, src)]

    while pq:
        d, u = heapq.heappop(pq)
        if visited[u]:
            continue
        visited[u] = True

        for v, w in graph[u]:
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                heapq.heappush(pq, (dist[v], v))

    return dist"""


class Dijkstra(Problem):
    @staticmethod
    def name() -> str:
        return "Dijkstra's Shortest Path"

    @staticmethod
    def topic() -> str:
        return "Shortest Path"

    @staticmethod
    def subtopic() -> str:
        return "Dijkstra"

    @staticmethod
    def description() -> str:
        return "Find shortest paths from a source node using Dijkstra's algorithm with a priority queue."

    @staticmethod
    def long_description() -> str:
        return (
            "Dijkstra's algorithm finds the shortest path from a single source "
            "node to all other nodes in a weighted graph with non-negative edge "
            "weights. It uses a min-priority queue to greedily select the closest "
            "unvisited node at each step.\n\n"
            "Time Complexity: O((V + E) log V) with a binary heap.\n\n"
            "Constraints:\n\n"
            "- All edge weights must be non-negative\n"
            "- Graph can be directed or undirected\n"
            "- Unreachable nodes keep distance infinity"
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

        # edges: (u, v, weight) — undirected
        presets = {
            1: [
                (0, 1, 4), (0, 2, 2), (1, 2, 5), (1, 3, 10),
                (2, 4, 3), (3, 5, 7), (4, 3, 4), (4, 5, 8),
                (4, 6, 6), (5, 7, 1), (6, 7, 2), (1, 6, 9),
            ],
        }

        edge_list = presets.get(preset, presets[1])
        n = 8
        src = 0

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

        tracer.log(f"Dijkstra from source node {src}")
        snap(1, f"Dijkstra from source {src}")

        # Initialize distances
        dist = [float("inf")] * n
        dist[src] = 0
        visited = [False] * n
        pq: list[tuple[float, int]] = [(0, src)]

        # Show initial state with badges
        for i in range(n):
            badge = "0" if i == src else "INF"
            tracer.set_node_badge(i, badge)
        tracer.log(f"dist[{src}] = 0, all others = INF")
        snap(4, f"Initialize dist[{src}] = 0")

        while pq:
            d, u = heapq.heappop(pq)

            if visited[u]:
                tracer.log(f"Skip node {u} (already visited)")
                snap(10, f"Skip visited node {u}")
                continue

            # Mark node as being processed
            tracer.select_node(u)
            tracer.log(f"Pop node {u} with dist {d}")
            snap(9, f"Pop node {u}, dist = {d}")

            # Finalize this node
            visited[u] = True
            tracer.patch_node(u)
            tracer.deselect_node(u)
            tracer.log(f"Finalize node {u}")
            snap(12, f"Finalize node {u}")

            # Relax edges
            for v, w in graph[u]:
                edge_key = (u, v) if (u, v) in tracer._edge_selected else (v, u)
                tracer.select_edge(*edge_key)
                tracer.log(f"  Examine edge {u}-{v} (w={w})")
                snap(14, f"Examine edge {u}-{v}, w={w}")

                new_dist = dist[u] + w
                if new_dist < dist[v]:
                    old_dist = dist[v]
                    dist[v] = new_dist
                    heapq.heappush(pq, (dist[v], v))
                    tracer.set_node_badge(v, str(dist[v]))
                    tracer.set_edge_class(*edge_key, "relaxed")
                    tracer.patch_edge(*edge_key)
                    old_str = "INF" if old_dist == float("inf") else str(int(old_dist))
                    tracer.log(f"  Relax {v}: {old_str} -> {int(new_dist)}")
                    snap(16, f"Relax {v}: {old_str} -> {int(new_dist)}")
                else:
                    tracer.log(f"  No improvement for {v}")
                    snap(15, f"No relax {u}-{v}")

                tracer.deselect_edge(*edge_key)

        # Final result
        tracer.deselect_all_nodes()
        tracer.deselect_all_edges()
        dist_str = ", ".join(
            f"{i}:{int(d) if d != float('inf') else 'INF'}" for i, d in enumerate(dist)
        )
        tracer.log(f"Final distances: {dist_str}")
        snap(19, f"Done. Distances: {dist_str}")
        return steps
