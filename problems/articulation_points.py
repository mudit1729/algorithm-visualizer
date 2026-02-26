from __future__ import annotations

from core.step import Step
from core.tracer import GraphTracer
from problems.base_problem import Problem

_SOURCE = """\
def articulationPoints(n, edges):
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)

    disc = [-1] * n
    low = [-1] * n
    parent = [-1] * n
    timer = [0]
    ap = set()

    def dfs(u):
        disc[u] = low[u] = timer[0]
        timer[0] += 1
        children = 0

        for v in adj[u]:
            if disc[v] == -1:
                children += 1
                parent[v] = u
                dfs(v)
                low[u] = min(low[u], low[v])
                if parent[u] == -1 and children > 1:
                    ap.add(u)
                if parent[u] != -1 and low[v] >= disc[u]:
                    ap.add(u)
            else:
                low[u] = min(low[u], disc[v])

    for i in range(n):
        if disc[i] == -1:
            dfs(i)

    return list(ap)"""


class ArticulationPoints(Problem):
    @staticmethod
    def name() -> str:
        return "Articulation Points"

    @staticmethod
    def topic() -> str:
        return "Graph / DFS"

    @staticmethod
    def subtopic() -> str:
        return "Cut Vertices"

    @staticmethod
    def description() -> str:
        return "Find all articulation points (cut vertices) in an undirected graph using modified Tarjan's algorithm."

    @staticmethod
    def long_description() -> str:
        return (
            "An **articulation point** (or cut vertex) is a vertex whose removal "
            "disconnects the graph. The algorithm uses Tarjan's DFS with disc/low "
            "values.\n\n"
            "A node `u` is an articulation point if:\n\n"
            "1. `u` is the root of the DFS tree and has **two or more children**\n"
            "2. `u` is not the root and has a child `v` with `low[v] >= disc[u]` "
            "(no back edge from `v`'s subtree bypasses `u`)\n\n"
            "Time complexity: `O(V + E)`\n\n"
            "Visualization:\n\n"
            "- Node badges show `disc/low` values\n"
            "- Tree and back edges are classified\n"
            "- Articulation points are highlighted in red"
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
        return """Approach: Find all articulation points (cut vertices) in an undirected graph using Tarjan's DFS algorithm. Track discovery time and low-link values. A node u is an articulation point if: (1) u is the root of DFS and has 2+ children, or (2) u is not root and has a child v where low[v] >= disc[u].

Time Complexity: O(V + E) — a single DFS traversal.

Space Complexity: O(V + E) for the adjacency list and arrays.

Key Insight: An articulation point's removal disconnects the graph. The condition low[v] >= disc[u] means child v cannot reach any ancestor of u through a back edge, so u is the only connection between its parent side and v's subtree.

Interview Tip: Remember the two separate cases — root nodes need 2+ DFS children, non-root nodes use the low-link condition. This is a common distinction interviewers test."""

    @staticmethod
    def generate_steps(**kwargs: object) -> list[Step]:
        preset = int(kwargs.get("preset", 1))

        # 8 nodes, undirected graph
        # Structure:
        #   0 -- 1 -- 3 -- 5 -- 6
        #   |    |    |         |
        #   +----2    4         7
        #
        # Edges: 0-1, 1-2, 2-0, 1-3, 3-4, 3-5, 5-6, 6-7
        # Articulation points: 1 (bridges {0,1,2} to {3,4,5,6,7}),
        #                      3 (bridges 4 and {5,6,7}),
        #                      5 (bridges 3 and {6,7})
        presets = {
            1: (
                8,
                [
                    (0, 1), (1, 2), (2, 0),   # triangle
                    (1, 3),                     # bridge from triangle
                    (3, 4),                     # pendant
                    (3, 5),                     # chain continues
                    (5, 6), (6, 7),            # chain
                ],
            ),
        }

        n, edge_list = presets.get(preset, presets[1])
        adj: list[list[int]] = [[] for _ in range(n)]
        for u, v in edge_list:
            adj[u].append(v)
            adj[v].append(u)

        graph = GraphTracer(list(range(n)), directed=False)
        steps: list[Step] = []

        def snap(line: int, desc: str = "") -> None:
            steps.append(graph.snapshot(line, desc))

        # Add edges
        for u, v in edge_list:
            graph.add_edge(u, v)

        edge_str = ", ".join(f"{u}-{v}" for u, v in edge_list)
        graph.log(f"Undirected graph: {n} nodes, edges: {edge_str}")
        snap(1, f"Undirected graph with {n} nodes")

        # Tarjan's articulation point algorithm
        disc = [-1] * n
        low = [-1] * n
        par = [-1] * n
        timer = [0]
        ap: set[int] = set()

        def dfs(u: int) -> None:
            disc[u] = low[u] = timer[0]
            timer[0] += 1
            children = 0

            graph.select_node(u)
            graph.set_node_badge(u, f"{disc[u]}/{low[u]}")
            graph.log(f"DFS({u}): disc={disc[u]}, low={low[u]}")
            snap(16, f"DFS({u}): disc={disc[u]}, low={low[u]}")

            for v in adj[u]:
                # Find edge key
                edge_key = (u, v) if (u, v) in graph._edge_selected else (v, u)

                if disc[v] == -1:
                    children += 1
                    par[v] = u

                    graph.select_edge(*edge_key)
                    graph.set_edge_class(*edge_key, "tree")
                    graph.log(f"  Tree edge {u}-{v}, child #{children}")
                    snap(24, f"Tree edge {u}-{v}")
                    graph.deselect_edge(*edge_key)

                    dfs(v)

                    # Update low[u]
                    low[u] = min(low[u], low[v])
                    graph.set_node_badge(u, f"{disc[u]}/{low[u]}")
                    graph.log(f"  Back from {v}: low[{u}] = {low[u]}")
                    snap(25, f"Update low[{u}]={low[u]}")

                    # Check articulation point conditions
                    # Condition 1: u is root with 2+ children
                    if par[u] == -1 and children > 1:
                        ap.add(u)
                        graph.mark_node_error(u)
                        graph.log(f"  AP found: {u} is root with {children} children")
                        snap(27, f"AP: {u} (root, {children} children)")

                    # Condition 2: u is not root and low[v] >= disc[u]
                    if par[u] != -1 and low[v] >= disc[u]:
                        ap.add(u)
                        graph.mark_node_error(u)
                        graph.log(f"  AP found: {u} (low[{v}]={low[v]} >= disc[{u}]={disc[u]})")
                        snap(29, f"AP: {u} (low[{v}]>= disc[{u}])")
                else:
                    # Back edge (skip parent to avoid counting the tree edge)
                    if v != par[u]:
                        graph.select_edge(*edge_key)
                        graph.set_edge_class(*edge_key, "back")
                        low[u] = min(low[u], disc[v])
                        graph.set_node_badge(u, f"{disc[u]}/{low[u]}")
                        graph.log(f"  Back edge {u}-{v}: low[{u}] = min(low[{u}], disc[{v}]) = {low[u]}")
                        snap(32, f"Back edge {u}-{v}, low[{u}]={low[u]}")
                        graph.deselect_edge(*edge_key)

            # Done with u
            if u not in ap:
                graph.deselect_node(u)
                graph.patch_node(u)
                graph.log(f"DFS({u}): finished (not AP)")
                snap(35, f"DFS({u}): finished")
            else:
                graph.deselect_node(u)
                graph.log(f"DFS({u}): finished (is AP)")
                snap(35, f"DFS({u}): finished (AP)")

        # Main loop
        for i in range(n):
            if disc[i] == -1:
                graph.log(f"Start DFS from node {i}")
                snap(31, f"Start DFS from node {i}")
                dfs(i)

        # Final summary
        graph.deselect_all_nodes()
        graph.deselect_all_edges()
        ap_str = ", ".join(str(x) for x in sorted(ap)) if ap else "none"
        graph.log(f"Articulation points: [{ap_str}]")
        snap(35, f"Done! Articulation points: [{ap_str}]")
        return steps
