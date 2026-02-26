from __future__ import annotations

from core.step import Step
from core.tracer import GraphTracer
from problems.base_problem import Problem

_SOURCE = """\
def floydWarshall(n, edges):
    INF = float('inf')
    dist = [[INF] * n for _ in range(n)]
    for i in range(n):
        dist[i][i] = 0
    for u, v, w in edges:
        dist[u][v] = w

    for k in range(n):
        for i in range(n):
            for j in range(n):
                if dist[i][k] + dist[k][j] < dist[i][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]

    return dist"""


class FloydWarshall(Problem):
    @staticmethod
    def name() -> str:
        return "Floyd-Warshall"

    @staticmethod
    def topic() -> str:
        return "Shortest Path"

    @staticmethod
    def subtopic() -> str:
        return "Floyd-Warshall"

    @staticmethod
    def description() -> str:
        return "All-pairs shortest paths using Floyd-Warshall with negative edge weights."

    @staticmethod
    def long_description() -> str:
        return (
            "Given a directed weighted graph with `n` nodes and a list of edges "
            "`[u, v, w]`, compute the shortest distance between every pair of "
            "nodes using the Floyd-Warshall algorithm. The graph may contain "
            "negative edge weights but no negative-weight cycles.\n\n"
            "The algorithm considers each node `k` as a potential intermediate "
            "node and relaxes `dist[i][j]` through `k`.\n\n"
            "Time complexity: `O(n^3)`\n"
            "Space complexity: `O(n^2)`\n\n"
            "Constraints:\n\n"
            "- `1 <= n <= 100`\n"
            "- Edge weights can be negative\n"
            "- No negative-weight cycles"
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
    def theory() -> str:
        return """Approach: Floyd-Warshall computes shortest paths between all pairs of vertices. It considers each vertex k as a potential intermediate node and checks if the path through k improves the current shortest path between every pair (i, j).

Time Complexity: O(V³) — three nested loops over all vertices.

Space Complexity: O(V²) for the distance matrix.

Key Insight: The key recurrence is dist[i][j] = min(dist[i][j], dist[i][k] + dist[k][j]). The order of the outermost loop (over k) is critical — it must iterate over intermediate vertices.

Interview Tip: Floyd-Warshall is ideal when you need all-pairs shortest paths or when the graph is dense. For single-source shortest paths, Dijkstra's or Bellman-Ford is more efficient."""

    @staticmethod
    def generate_steps(**kwargs: object) -> list[Step]:
        preset = int(kwargs.get("preset", 1))

        presets = {
            1: (
                6,
                [
                    (0, 1, 3), (0, 2, 8), (1, 3, 1), (1, 4, -2),
                    (2, 1, -1), (2, 4, 5), (3, 5, 4), (4, 3, 2),
                    (4, 5, 6), (5, 0, 7),
                ],
            ),
        }

        n, edges = presets.get(preset, presets[1])

        INF = float("inf")
        dist = [[INF] * n for _ in range(n)]
        for i in range(n):
            dist[i][i] = 0
        for u, v, w in edges:
            dist[u][v] = w

        tracer = GraphTracer(list(range(n)), directed=True)
        steps: list[Step] = []

        def snap(line: int, desc: str = "") -> None:
            steps.append(tracer.snapshot(line, desc))

        # Add all edges with weights
        for u, v, w in edges:
            tracer.add_edge(u, v, weight=w)

        def fmt(d: float) -> str:
            if d == INF:
                return "INF"
            return str(int(d)) if d == int(d) else str(d)

        edges_str = ", ".join(f"{u}->{v}({w})" for u, v, w in edges)
        tracer.log(f"Nodes: {n}, Edges: {edges_str}")
        snap(7, f"{n} nodes, {len(edges)} edges initialized")

        # Floyd-Warshall main loop
        for k in range(n):
            # Select intermediate node k
            tracer.deselect_all_nodes()
            tracer.deselect_all_edges()
            tracer.select_node(k)
            tracer.set_node_color(k, "#f9e2af")  # yellow highlight
            tracer.log(f"Intermediate k={k}")
            snap(10, f"Intermediate node k={k}")

            for i in range(n):
                for j in range(n):
                    if i == j or i == k or j == k:
                        continue
                    if dist[i][k] == INF or dist[k][j] == INF:
                        continue
                    new_dist = dist[i][k] + dist[k][j]
                    if new_dist < dist[i][j]:
                        old_val = dist[i][j]
                        dist[i][j] = new_dist

                        # Visualize the relaxation
                        tracer.deselect_all_edges()
                        tracer.select_node(i)
                        tracer.select_node(j)

                        # Highlight the edges through k if they exist
                        if (i, k) in tracer._edge_selected:
                            tracer.select_edge(i, k)
                            tracer.set_edge_class(i, k, "relaxed")
                        if (k, j) in tracer._edge_selected:
                            tracer.select_edge(k, j)
                            tracer.set_edge_class(k, j, "relaxed")

                        # Update labels to show distances
                        tracer.set_label(i, f"{i}({fmt(new_dist)})")
                        tracer.set_label(j, f"{j}")

                        tracer.log(
                            f"  dist[{i}][{j}]: {fmt(old_val)} -> {fmt(new_dist)} "
                            f"via k={k}"
                        )
                        snap(
                            15,
                            f"dist[{i}][{j}] = {fmt(new_dist)} via k={k}",
                        )

                        # Deselect i, j after snap
                        tracer.deselect_node(i)
                        tracer.deselect_node(j)

                        # Reset edge classes
                        if (i, k) in tracer._edge_class:
                            tracer.set_edge_class(i, k, "")
                        if (k, j) in tracer._edge_class:
                            tracer.set_edge_class(k, j, "")

            # Done with intermediate k
            tracer.set_node_color(k, "")
            tracer.deselect_node(k)
            tracer.patch_node(k)
            tracer.log(f"Done with intermediate k={k}")
            snap(15, f"Completed intermediate k={k}")

        # Final state: show all distances on labels
        tracer.deselect_all_nodes()
        tracer.deselect_all_edges()
        for i in range(n):
            tracer.set_label(i, str(i))
        tracer.log("Floyd-Warshall complete. All-pairs shortest paths computed.")
        snap(15, "All-pairs shortest paths computed")
        return steps
