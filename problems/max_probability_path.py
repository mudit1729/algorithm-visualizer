from __future__ import annotations

import heapq

from core.step import Step
from core.tracer import GraphTracer
from problems.base_problem import Problem

_SOURCE = """\
def maxProbability(n, edges, succ, start, end):
    graph = [[] for _ in range(n)]
    for i, (u, v) in enumerate(edges):
        graph[u].append((v, succ[i]))
        graph[v].append((u, succ[i]))

    prob = [0.0] * n
    prob[start] = 1.0
    heap = [(-1.0, start)]

    while heap:
        neg_p, u = heapq.heappop(heap)
        p = -neg_p
        if u == end:
            return p
        if p < prob[u]:
            continue
        for v, w in graph[u]:
            new_p = p * w
            if new_p > prob[v]:
                prob[v] = new_p
                heapq.heappush(heap, (-new_p, v))

    return 0.0"""


class MaxProbabilityPath(Problem):
    @staticmethod
    def name() -> str:
        return "Path with Maximum Probability"

    @staticmethod
    def topic() -> str:
        return "Shortest Path"

    @staticmethod
    def subtopic() -> str:
        return "Dijkstra"

    @staticmethod
    def description() -> str:
        return "LeetCode #1514: Find the path with maximum probability using modified Dijkstra."

    @staticmethod
    def long_description() -> str:
        return (
            "Given an undirected weighted graph with `n` nodes, a list of "
            "`edges` and their success `probabilities`, find the path from "
            "`start` to `end` with the **maximum probability** of success. "
            "If no path exists, return `0`.\n\n"
            "Each edge has a probability between `0` and `1`. The probability "
            "of a path is the product of probabilities of its edges. Solved "
            "using modified Dijkstra with a max-heap (negate probabilities).\n\n"
            "Example 1:\n"
            "Input: `n = 3`, `edges = [[0,1],[1,2],[0,2]]`, "
            "`succProb = [0.5,0.5,0.2]`, `start = 0`, `end = 2`\n"
            "Output: `0.25`\n\n"
            "Constraints:\n\n"
            "- `2 <= n <= 10^4`\n"
            "- `0 <= succProb[i] <= 1`\n"
            "- At most one edge between each pair of nodes"
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
            1: (
                8,
                [
                    (0, 1), (0, 2), (1, 2), (1, 3), (2, 4),
                    (3, 4), (3, 5), (4, 6), (5, 6), (5, 7),
                    (6, 7),
                ],
                [0.8, 0.3, 0.5, 0.9, 0.4, 0.7, 0.6, 0.5, 0.8, 0.3, 0.9],
                0,  # start
                7,  # end
            ),
        }

        n, edge_list, succ_probs, start, end = presets.get(preset, presets[1])

        # Build adjacency list
        graph: list[list[tuple[int, float]]] = [[] for _ in range(n)]
        for i, (u, v) in enumerate(edge_list):
            graph[u].append((v, succ_probs[i]))
            graph[v].append((u, succ_probs[i]))

        tracer = GraphTracer(list(range(n)), directed=False)
        steps: list[Step] = []

        def snap(line: int, desc: str = "") -> None:
            steps.append(tracer.snapshot(line, desc))

        # Add all edges with probability weights
        added_edges: set[tuple[int, int]] = set()
        for i, (u, v) in enumerate(edge_list):
            key = (min(u, v), max(u, v))
            if key not in added_edges:
                tracer.add_edge(u, v, weight=succ_probs[i])
                added_edges.add(key)

        # Initial state
        prob = [0.0] * n
        prob[start] = 1.0

        tracer.set_node_badge(start, "1.0", "#a6e3a1")
        tracer.set_node_color(start, "#a6e3a1")
        tracer.log(
            f"Nodes: {n}, start={start}, end={end}, "
            f"maximize probability product"
        )
        snap(9, f"start={start}, end={end}; prob[{start}]=1.0")

        # Modified Dijkstra with max-heap
        heap: list[tuple[float, int]] = [(-1.0, start)]
        parent_edge: dict[int, tuple[int, int]] = {}

        while heap:
            neg_p, u = heapq.heappop(heap)
            p = -neg_p

            tracer.deselect_all_nodes()
            tracer.deselect_all_edges()
            tracer.select_node(u)
            tracer.set_node_color(u, "#f9e2af")  # yellow for current
            tracer.log(f"Pop node {u}, prob={p:.4f}")
            snap(14, f"Process node {u}, prob={p:.4f}")

            if u == end:
                tracer.set_node_color(u, "#a6e3a1")
                tracer.set_node_badge(u, f"{p:.4f}", "#a6e3a1")
                tracer.patch_node(u)
                tracer.log(f"Reached end node {end}! prob={p:.4f}")
                snap(17, f"Reached end={end}! prob={p:.4f}")
                break

            if p < prob[u]:
                tracer.deselect_node(u)
                tracer.log(f"  Skip stale entry for node {u}")
                snap(19, f"Skip stale node {u}")
                continue

            # Mark current node as processed
            tracer.set_node_color(u, "#89b4fa")  # blue for visited
            tracer.patch_node(u)

            for v, w in graph[u]:
                new_p = p * w
                edge_key = (min(u, v), max(u, v))
                # Use the canonical edge direction that was added
                eu, ev = edge_key

                tracer.select_edge(eu, ev)
                tracer.select_node(v)

                if new_p > prob[v]:
                    old_p = prob[v]
                    prob[v] = new_p
                    heapq.heappush(heap, (-new_p, v))
                    parent_edge[v] = (eu, ev)

                    tracer.set_node_badge(v, f"{new_p:.3f}", "#89b4fa")
                    tracer.log(
                        f"  Relax {u}->{v}: {old_p:.4f} -> {new_p:.4f} "
                        f"(x{w})"
                    )
                    snap(
                        24,
                        f"prob[{v}] = {new_p:.4f} via {u}",
                    )
                else:
                    tracer.log(
                        f"  No improvement {u}->{v}: "
                        f"{new_p:.4f} <= {prob[v]:.4f}"
                    )

                tracer.deselect_edge(eu, ev)
                tracer.deselect_node(v)

        # Highlight best path by tracing parent_edge
        tracer.deselect_all_nodes()
        tracer.deselect_all_edges()
        tracer.depatch_all_edges()

        if prob[end] > 0:
            # Trace the best path via parent_edge
            visited_path: set[tuple[int, int]] = set()
            node = end
            while node in parent_edge:
                eu, ev = parent_edge[node]
                visited_path.add((eu, ev))
                # Find which neighbor is the "other" side
                if eu == node:
                    node = ev
                else:
                    node = eu
            for eu, ev in visited_path:
                tracer.patch_edge(eu, ev)
            tracer.log(f"Best path probability: {prob[end]:.4f}")
            snap(24, f"Max probability = {prob[end]:.4f}")
        else:
            tracer.log("No path found!")
            snap(24, "No path exists, return 0.0")

        return steps
