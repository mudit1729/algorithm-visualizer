from __future__ import annotations

from core.step import Step
from core.tracer import GraphTracer
from problems.base_problem import Problem

_SOURCE = """\
def criticalConnections(n, connections):
    adj = [[] for _ in range(n)]
    for u, v in connections:
        adj[u].append(v)
        adj[v].append(u)

    disc = [-1] * n
    low = [-1] * n
    timer = [0]
    bridges = []

    def dfs(u, parent):
        disc[u] = low[u] = timer[0]
        timer[0] += 1

        for v in adj[u]:
            if v == parent:
                continue
            if disc[v] == -1:
                dfs(v, u)
                low[u] = min(low[u], low[v])
                if low[v] > disc[u]:
                    bridges.append([u, v])
            else:
                low[u] = min(low[u], disc[v])

    for i in range(n):
        if disc[i] == -1:
            dfs(i, -1)

    return bridges"""

class CriticalConnections(Problem):
    @staticmethod
    def name() -> str:
        return "Critical Connections"

    @staticmethod
    def topic() -> str:
        return "Graph / DFS"

    @staticmethod
    def subtopic() -> str:
        return "Bridges"

    @staticmethod
    def description() -> str:
        return "LeetCode #1192: Find all bridges (critical connections) in an undirected network using Tarjan's algorithm."

    @staticmethod
    def long_description() -> str:
        return (
            "Given `n` servers and a list of `connections` forming an undirected "
            "graph, find all **critical connections** (bridges). A connection is "
            "critical if removing it disconnects the graph.\n\n"
            "A bridge edge `(u, v)` satisfies `low[v] > disc[u]`, meaning there "
            "is no back edge from the subtree rooted at `v` that reaches `u` or "
            "an ancestor of `u`.\n\n"
            "Example:\n"
            "Input: `n=4`, `connections=[[0,1],[1,2],[2,0],[1,3]]`\n"
            "Output: `[[1,3]]`\n\n"
            "Constraints:\n\n"
            "- `2 <= n <= 10^5`\n"
            "- `n - 1 <= connections.length <= 10^5`\n"
            "- No repeated connections"
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

        # 8 nodes, undirected, with 3 bridges:
        #   Cluster A: 0-1-2-0 (triangle)
        #   Bridge: 2-3
        #   Cluster B: 3-4-5-3 (triangle)
        #   Bridge: 5-6
        #   Cluster C: 6-7
        #   Bridge: 6-7 (trivially a bridge since it's the only edge)
        presets = {
            1: (
                8,
                [
                    (0, 1), (1, 2), (2, 0),   # triangle {0,1,2}
                    (2, 3),                     # bridge
                    (3, 4), (4, 5), (5, 3),   # triangle {3,4,5}
                    (5, 6),                     # bridge
                    (6, 7),                     # bridge
                ],
            ),
        }

        n, connections = presets.get(preset, presets[1])
        adj: list[list[int]] = [[] for _ in range(n)]
        for u, v in connections:
            adj[u].append(v)
            adj[v].append(u)

        graph = GraphTracer(list(range(n)), directed=False)
        steps: list[Step] = []

        def snap(line: int, desc: str = "") -> None:
            steps.append(graph.snapshot(line, desc))

        # Add edges (undirected: add once, GraphTracer handles display)
        for u, v in connections:
            graph.add_edge(u, v)

        conn_str = ", ".join(f"{u}-{v}" for u, v in connections)
        graph.log(f"Undirected graph: {n} nodes, connections: {conn_str}")
        snap(1, f"Undirected graph with {n} nodes")

        # Tarjan's bridge-finding algorithm
        disc = [-1] * n
        low = [-1] * n
        timer = [0]
        bridges: list[tuple[int, int]] = []

        def dfs(u: int, parent: int) -> None:
            disc[u] = low[u] = timer[0]
            timer[0] += 1

            graph.select_node(u)
            graph.set_node_badge(u, f"{disc[u]}/{low[u]}")
            graph.log(f"DFS({u}): disc={disc[u]}, low={low[u]}")
            snap(13, f"DFS({u}): disc={disc[u]}, low={low[u]}")

            for v in adj[u]:
                if v == parent:
                    continue

                # Find edge key (undirected: stored as (min, max) or original order)
                edge_key = (u, v) if (u, v) in graph._edge_selected else (v, u)
                graph.select_edge(*edge_key)

                if disc[v] == -1:
                    # Tree edge
                    graph.set_edge_class(*edge_key, "tree")
                    graph.log(f"  Edge {u}-{v}: tree edge, recurse")
                    snap(19, f"Tree edge {u}-{v}")
                    graph.deselect_edge(*edge_key)

                    dfs(v, u)

                    # Update low[u]
                    low[u] = min(low[u], low[v])
                    graph.set_node_badge(u, f"{disc[u]}/{low[u]}")
                    graph.log(f"  Back from {v}: low[{u}] = min(low[{u}], low[{v}]) = {low[u]}")
                    snap(20, f"Update low[{u}]={low[u]}")

                    # Check if bridge
                    if low[v] > disc[u]:
                        bridges.append((u, v))
                        graph.mark_edge_error(*edge_key)
                        graph.log(f"  BRIDGE found: {u}-{v} (low[{v}]={low[v]} > disc[{u}]={disc[u]})")
                        snap(22, f"BRIDGE: {u}-{v}")
                    else:
                        # Not a bridge: patch as safe
                        graph.patch_edge(*edge_key)
                        graph.log(f"  Edge {u}-{v}: not a bridge (low[{v}]={low[v]} <= disc[{u}]={disc[u]})")
                        snap(22, f"Safe edge {u}-{v}")
                else:
                    # Back edge
                    graph.set_edge_class(*edge_key, "back")
                    low[u] = min(low[u], disc[v])
                    graph.set_node_badge(u, f"{disc[u]}/{low[u]}")
                    graph.log(f"  Edge {u}-{v}: back edge, low[{u}] = min(low[{u}], disc[{v}]) = {low[u]}")
                    snap(24, f"Back edge {u}-{v}, low[{u}]={low[u]}")
                    graph.deselect_edge(*edge_key)

            # Done with u
            graph.deselect_node(u)
            graph.patch_node(u)
            graph.log(f"DFS({u}): finished")
            snap(26, f"DFS({u}): finished")

        # Main loop
        for i in range(n):
            if disc[i] == -1:
                graph.log(f"Start DFS from node {i}")
                snap(28, f"Start DFS from node {i}")
                dfs(i, -1)

        # Final summary
        graph.deselect_all_nodes()
        graph.deselect_all_edges()
        bridge_str = ", ".join(f"{u}-{v}" for u, v in bridges) if bridges else "none"
        graph.log(f"All bridges found: [{bridge_str}]")
        snap(30, f"Done! Found {len(bridges)} bridges: [{bridge_str}]")
        return steps
