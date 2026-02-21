from __future__ import annotations

from core.step import Step
from core.tracer import GraphTracer
from problems.base_problem import Problem

_SOURCE = """\
def bellman_ford(n, edges, src):
    dist = [float('inf')] * n
    dist[src] = 0

    for i in range(n - 1):
        for u, v, w in edges:
            if dist[u] != float('inf') and dist[u] + w < dist[v]:
                dist[v] = dist[u] + w

    for u, v, w in edges:
        if dist[u] != float('inf') and dist[u] + w < dist[v]:
            return None

    return dist"""


class BellmanFord(Problem):
    @staticmethod
    def name() -> str:
        return "Bellman-Ford Algorithm"

    @staticmethod
    def topic() -> str:
        return "Shortest Path"

    @staticmethod
    def subtopic() -> str:
        return "Bellman-Ford"

    @staticmethod
    def description() -> str:
        return "Find shortest paths from a source, handling negative weights and detecting negative cycles."

    @staticmethod
    def long_description() -> str:
        return (
            "The Bellman-Ford algorithm computes shortest paths from a single "
            "source to all other vertices. Unlike Dijkstra, it handles graphs "
            "with negative edge weights and can detect negative-weight cycles.\n\n"
            "The algorithm relaxes all edges V-1 times. After V-1 iterations, "
            "if any edge can still be relaxed, a negative cycle exists.\n\n"
            "Time Complexity: O(V * E)\n\n"
            "Constraints:\n\n"
            "- Works with negative edge weights\n"
            "- Detects negative-weight cycles\n"
            "- V-1 passes over all edges guarantee correctness"
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

        # (u, v, weight) — directed edges
        presets = {
            1: [
                (0, 1, 6), (0, 2, 7), (1, 3, 5), (1, 4, -4),
                (1, 2, 8), (2, 4, 9), (2, 3, -3), (3, 1, -2),
                (4, 3, 7), (4, 0, 2), (0, 5, 3), (5, 6, 4),
                (6, 7, 2), (5, 7, 9), (7, 4, -3),
            ],
        }

        edge_list = presets.get(preset, presets[1])
        n = 8
        src = 0

        tracer = GraphTracer(list(range(n)), directed=True)
        steps: list[Step] = []

        def snap(line: int, desc: str = "") -> None:
            steps.append(tracer.snapshot(line, desc))

        # Add edges to tracer
        for u, v, w in edge_list:
            tracer.add_edge(u, v, weight=w)

        tracer.log(f"Bellman-Ford from source {src}, {n} nodes, {len(edge_list)} edges")
        snap(1, f"Bellman-Ford from source {src}")

        # Initialize distances
        dist = [float("inf")] * n
        dist[src] = 0

        for i in range(n):
            badge = "0" if i == src else "INF"
            tracer.set_node_badge(i, badge)
        tracer.log(f"dist[{src}] = 0, all others = INF")
        snap(3, f"Initialize dist[{src}] = 0")

        # V-1 iterations
        for i in range(n - 1):
            tracer.log(f"--- Pass {i + 1} of {n - 1} ---")
            snap(5, f"Pass {i + 1} of {n - 1}")
            updated = False

            for u, v, w in edge_list:
                tracer.select_edge(u, v)
                tracer.select_node(u)
                tracer.select_node(v)

                if dist[u] != float("inf") and dist[u] + w < dist[v]:
                    old_dist = dist[v]
                    dist[v] = dist[u] + w
                    tracer.set_node_badge(v, str(int(dist[v])))
                    tracer.set_edge_class(u, v, "relaxed")
                    old_str = "INF" if old_dist == float("inf") else str(int(old_dist))
                    tracer.log(f"  Relax {u}->{v}: dist[{v}] = {old_str} -> {int(dist[v])}")
                    snap(7, f"Relax {u}->{v}: {old_str} -> {int(dist[v])}")
                    updated = True
                else:
                    u_str = "INF" if dist[u] == float("inf") else str(int(dist[u]))
                    tracer.log(f"  Edge {u}->{v} (w={w}): no improvement")
                    snap(6, f"Check {u}->{v}: no relax")

                tracer.deselect_edge(u, v)
                tracer.deselect_node(u)
                tracer.deselect_node(v)

            if not updated:
                tracer.log(f"  No updates in pass {i + 1}, early stop")
                snap(5, f"Pass {i + 1}: no updates, done early")
                break

        # Check for negative cycles
        tracer.log("--- Negative cycle check ---")
        snap(10, "Negative cycle check")
        has_negative_cycle = False
        for u, v, w in edge_list:
            tracer.select_edge(u, v)
            if dist[u] != float("inf") and dist[u] + w < dist[v]:
                tracer.mark_node_error(u)
                tracer.mark_node_error(v)
                tracer.mark_edge_error(u, v)
                tracer.log(f"  Negative cycle detected via {u}->{v}")
                snap(11, f"Negative cycle: {u}->{v}")
                has_negative_cycle = True
                break
            tracer.deselect_edge(u, v)

        tracer.deselect_all_nodes()
        tracer.deselect_all_edges()

        if has_negative_cycle:
            tracer.log("Result: Negative cycle exists")
            snap(12, "Negative cycle exists!")
        else:
            dist_str = ", ".join(
                f"{i}:{int(d) if d != float('inf') else 'INF'}" for i, d in enumerate(dist)
            )
            tracer.log(f"Final distances: {dist_str}")
            snap(14, f"Done. Distances: {dist_str}")

            # Patch all reachable nodes
            for i in range(n):
                if dist[i] != float("inf"):
                    tracer.patch_node(i)
            snap(14, "All reachable nodes finalized")

        return steps
