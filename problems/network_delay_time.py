from __future__ import annotations

from core.step import Step
from core.tracer import GraphTracer
from problems.base_problem import Problem

_SOURCE = """\
def networkDelayTime(times, n, k):
    adj = [[] for _ in range(n + 1)]
    for u, v, w in times:
        adj[u].append((v, w))

    dist = [float('inf')] * (n + 1)
    dist[k] = 0
    pq = [(0, k)]

    while pq:
        d, u = heapq.heappop(pq)
        if d > dist[u]:
            continue

        for v, w in adj[u]:
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                heapq.heappush(pq, (dist[v], v))

    ans = max(dist[1:n + 1])
    return ans if ans < float('inf') else -1"""


class NetworkDelayTime(Problem):
    @staticmethod
    def name() -> str:
        return "Network Delay Time"

    @staticmethod
    def topic() -> str:
        return "Shortest Path"

    @staticmethod
    def subtopic() -> str:
        return "Dijkstra"

    @staticmethod
    def description() -> str:
        return "LeetCode #743: Find time for a signal to reach all nodes from source k."

    @staticmethod
    def long_description() -> str:
        return (
            "You are given a network of `n` nodes labeled `1` to `n`, and a "
            "list of travel `times` as directed edges `[u, v, w]` where `w` is "
            "the time it takes for a signal to travel from `u` to `v`. Given a "
            "starting node `k`, return the minimum time for all nodes to receive "
            "the signal. Return `-1` if not all nodes are reachable.\n\n"
            "Example:\n"
            "Input: `times = [[2,1,1],[2,3,1],[3,4,1]]`, `n = 4`, `k = 2`\n"
            "Output: `2`\n\n"
            "Constraints:\n\n"
            "- `1 <= k <= n <= 100`\n"
            "- `1 <= u, v <= n`\n"
            "- `0 <= w <= 100`\n"
            "- All edges `(u, v)` are unique"
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

        # (u, v, w) — directed edges, nodes 1-8
        presets = {
            1: [
                (1, 2, 3), (1, 3, 6), (1, 4, 8), (2, 3, 2),
                (2, 5, 7), (3, 6, 5), (3, 4, 3), (4, 7, 4),
                (5, 6, 1), (5, 8, 9), (6, 7, 2), (6, 8, 6),
                (7, 8, 3), (4, 8, 10),
            ],
        }

        times_list = presets.get(preset, presets[1])
        n = 8
        k = 1

        # Build adjacency list (1-indexed)
        adj: list[list[tuple[int, int]]] = [[] for _ in range(n + 1)]
        for u, v, w in times_list:
            adj[u].append((v, w))

        tracer = GraphTracer(list(range(1, n + 1)), directed=True)
        steps: list[Step] = []

        def snap(line: int, desc: str = "") -> None:
            steps.append(tracer.snapshot(line, desc))

        # Add edges to tracer
        for u, v, w in times_list:
            tracer.add_edge(u, v, weight=w)

        tracer.log(f"Network Delay: {n} nodes, source k={k}")
        snap(1, f"Network with {n} nodes, source k={k}")

        # Initialize distances
        dist = [float("inf")] * (n + 1)
        dist[k] = 0
        pq: list[tuple[float, int]] = [(0, k)]

        for i in range(1, n + 1):
            badge = "0" if i == k else "INF"
            tracer.set_node_badge(i, badge)
        tracer.log(f"dist[{k}] = 0, all others = INF")
        snap(7, f"Initialize dist[{k}] = 0")

        visited_count = 0

        while pq:
            d, u = heapq.heappop(pq)

            if d > dist[u]:
                tracer.log(f"Skip stale entry for node {u}")
                snap(11, f"Skip stale node {u}")
                continue

            # Process current node
            tracer.select_node(u)
            tracer.log(f"Pop node {u} with time {int(d)}")
            snap(10, f"Pop node {u}, time = {int(d)}")

            # Finalize node
            tracer.patch_node(u)
            tracer.deselect_node(u)
            visited_count += 1
            tracer.log(f"Finalize node {u} ({visited_count}/{n} reached)")
            snap(12, f"Finalize node {u}")

            # Relax outgoing edges
            for v, w in adj[u]:
                tracer.select_edge(u, v)
                tracer.log(f"  Examine {u}->{v} (w={w})")
                snap(14, f"Examine {u}->{v}, w={w}")

                new_dist = dist[u] + w
                if new_dist < dist[v]:
                    old_dist = dist[v]
                    dist[v] = new_dist
                    heapq.heappush(pq, (dist[v], v))
                    tracer.set_node_badge(v, str(int(dist[v])))
                    tracer.set_edge_class(u, v, "relaxed")
                    tracer.patch_edge(u, v)
                    old_str = "INF" if old_dist == float("inf") else str(int(old_dist))
                    tracer.log(f"  Relax {v}: {old_str} -> {int(new_dist)}")
                    snap(16, f"Relax {v}: {old_str} -> {int(new_dist)}")
                else:
                    tracer.log(f"  No improvement for {v}")
                    snap(15, f"No relax {u}->{v}")

                tracer.deselect_edge(u, v)

        # Compute answer
        tracer.deselect_all_nodes()
        tracer.deselect_all_edges()

        ans = max(dist[1 : n + 1])
        if ans == float("inf"):
            tracer.log("Result: -1 (not all nodes reachable)")
            snap(19, "Result: -1 (unreachable nodes)")
        else:
            # Highlight the node with max delay
            max_node = -1
            for i in range(1, n + 1):
                if dist[i] == ans:
                    max_node = i
                    break
            tracer.select_node(max_node)
            tracer.set_node_color(max_node, "#f9e2af")
            dist_str = ", ".join(
                f"{i}:{int(dist[i]) if dist[i] != float('inf') else 'INF'}"
                for i in range(1, n + 1)
            )
            tracer.log(f"All times: {dist_str}")
            tracer.log(f"Max delay = {int(ans)} at node {max_node}")
            snap(19, f"Answer: {int(ans)} (node {max_node} reached last)")

        return steps
