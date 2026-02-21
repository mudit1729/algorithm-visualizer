from __future__ import annotations

from core.step import Step
from core.tracer import AuxPanelTracer, GraphTracer, combine_step
from problems.base_problem import Problem

_SOURCE = """\
def kosaraju_scc(n, adj):
    # Pass 1: DFS on original graph, record finish order
    visited = [False] * n
    finish_stack = []

    def dfs1(u):
        visited[u] = True
        for v in adj[u]:
            if not visited[v]:
                dfs1(v)
        finish_stack.append(u)

    for i in range(n):
        if not visited[i]:
            dfs1(i)

    # Build transposed graph
    adj_t = [[] for _ in range(n)]
    for u in range(n):
        for v in adj[u]:
            adj_t[v].append(u)

    # Pass 2: DFS on transposed graph in reverse finish order
    visited2 = [False] * n
    sccs = []

    def dfs2(u, scc):
        visited2[u] = True
        scc.append(u)
        for v in adj_t[u]:
            if not visited2[v]:
                dfs2(v, scc)

    while finish_stack:
        u = finish_stack.pop()
        if not visited2[u]:
            scc = []
            dfs2(u, scc)
            sccs.append(scc)

    return sccs"""

# SCC colors for pass 2
_SCC_COLORS = [
    "#a6e3a1",  # green
    "#89b4fa",  # blue
    "#f9e2af",  # yellow
    "#f38ba8",  # red/pink
    "#cba6f7",  # mauve
    "#94e2d5",  # teal
    "#fab387",  # peach
    "#74c7ec",  # sapphire
]


class KosarajuSCC(Problem):
    @staticmethod
    def name() -> str:
        return "Kosaraju's SCC"

    @staticmethod
    def topic() -> str:
        return "Graph / DFS"

    @staticmethod
    def subtopic() -> str:
        return "Strongly Connected Components"

    @staticmethod
    def description() -> str:
        return "Find all Strongly Connected Components using Kosaraju's two-pass DFS algorithm."

    @staticmethod
    def long_description() -> str:
        return (
            "Kosaraju's algorithm finds all strongly connected components (SCCs) "
            "in a directed graph using two DFS passes.\n\n"
            "**Pass 1:** Run DFS on the original graph and push nodes onto a "
            "stack in their finish order.\n\n"
            "**Pass 2:** Build the transposed graph. Pop nodes from the stack "
            "and run DFS on the transposed graph; each DFS tree is one SCC.\n\n"
            "Time complexity: `O(V + E)`\n\n"
            "Visualization:\n\n"
            "- Pass 1 selects/patches nodes as they are visited and finished\n"
            "- Finish Stack panel shows the finish order\n"
            "- Pass 2 colors each SCC with a distinct color"
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

        # 8 nodes, 3 SCCs: {0,1,2}, {3,4,5}, {6,7}
        presets = {
            1: (
                8,
                [
                    (0, 1), (1, 2), (2, 0),   # SCC {0,1,2}
                    (2, 3),                     # bridge
                    (3, 4), (4, 5), (5, 3),   # SCC {3,4,5}
                    (5, 6),                     # bridge
                    (6, 7), (7, 6),            # SCC {6,7}
                ],
            ),
        }

        n, edges = presets.get(preset, presets[1])
        adj: list[list[int]] = [[] for _ in range(n)]
        for u, v in edges:
            adj[u].append(v)

        # Build transposed adjacency
        adj_t: list[list[int]] = [[] for _ in range(n)]
        for u, v in edges:
            adj_t[v].append(u)

        graph = GraphTracer(list(range(n)), directed=True)
        aux = AuxPanelTracer()
        aux.add_panel("Finish Stack")
        steps: list[Step] = []

        def snap(line: int, desc: str = "") -> None:
            steps.append(combine_step(graph.snapshot(line, desc), aux))

        # Add edges to graph
        for u, v in edges:
            graph.add_edge(u, v)

        edge_str = ", ".join(f"{u}->{v}" for u, v in edges)
        graph.log(f"Directed graph: {n} nodes, edges: {edge_str}")
        snap(1, f"Directed graph with {n} nodes")

        # ===== Pass 1: DFS on original graph =====
        visited = [False] * n
        finish_stack: list[int] = []

        graph.log("=== Pass 1: DFS on original graph ===")
        snap(3, "Pass 1: DFS to compute finish order")

        def dfs1(u: int) -> None:
            visited[u] = True
            graph.select_node(u)
            graph.set_node_color(u, "#f9e2af")  # yellow = in-progress
            graph.log(f"Pass1 DFS({u}): visit")
            snap(8, f"Pass1: visit node {u}")

            for v in adj[u]:
                graph.select_edge(u, v)
                if not visited[v]:
                    graph.set_edge_class(u, v, "tree")
                    graph.log(f"  Edge {u}->{v}: tree edge")
                    snap(10, f"Pass1: tree edge {u}->{v}")
                    graph.deselect_edge(u, v)
                    dfs1(v)
                else:
                    graph.log(f"  Edge {u}->{v}: already visited")
                    snap(10, f"Pass1: skip {u}->{v}")
                    graph.deselect_edge(u, v)

            # Finish: push to stack
            finish_stack.append(u)
            graph.deselect_node(u)
            graph.set_node_color(u, "")
            graph.patch_node(u)
            graph.set_node_badge(u, f"f={len(finish_stack)}")
            aux.push("Finish Stack", str(u), f"finish #{len(finish_stack)}")
            graph.log(f"Pass1 DFS({u}): finished, push to stack (order={len(finish_stack)})")
            snap(13, f"Pass1: finish {u}, push to stack")

        for i in range(n):
            if not visited[i]:
                graph.log(f"Pass1: start DFS from node {i}")
                snap(15, f"Pass1: start DFS from {i}")
                dfs1(i)

        graph.log(f"Pass1 complete. Finish stack (top to bottom): {list(reversed(finish_stack))}")
        snap(18, "Pass 1 complete")

        # ===== Pass 2: DFS on transposed graph =====
        graph.log("=== Pass 2: DFS on transposed graph ===")
        # Reset visual state for pass 2
        graph.depatch_all_nodes()
        graph.deselect_all_nodes()
        graph.deselect_all_edges()
        for nid in range(n):
            graph.set_node_badge(nid, "")
            graph.set_node_color(nid, "")

        # Remove original edges, add transposed edges
        # We re-create the graph tracer for transposed graph
        graph_t = GraphTracer(list(range(n)), directed=True)

        # Copy positions from original graph
        for nid in range(n):
            graph_t._positions[nid] = graph._positions[nid]

        for u, v in edges:
            graph_t.add_edge(v, u)  # transposed

        graph_t.log("Transposed graph built. Starting Pass 2.")
        snap_t_steps: list[Step] = []

        def snap2(line: int, desc: str = "") -> None:
            steps.append(combine_step(graph_t.snapshot(line, desc), aux))

        snap2(18, "Pass 2: transposed graph built")

        visited2 = [False] * n
        sccs: list[list[int]] = []
        scc_color_idx = 0

        def dfs2(u: int, scc: list[int]) -> None:
            visited2[u] = True
            scc.append(u)
            graph_t.select_node(u)
            color = _SCC_COLORS[scc_color_idx % len(_SCC_COLORS)]
            graph_t.set_node_color(u, color)
            graph_t.log(f"Pass2 DFS({u}): visit, SCC #{len(sccs)+1}")
            snap2(28, f"Pass2: visit {u}")

            for v in adj_t[u]:
                graph_t.select_edge(u, v)
                if not visited2[v]:
                    graph_t.set_edge_class(u, v, "tree")
                    graph_t.log(f"  Edge {u}->{v}: tree edge in transposed graph")
                    snap2(30, f"Pass2: tree edge {u}->{v}")
                    graph_t.deselect_edge(u, v)
                    dfs2(v, scc)
                else:
                    graph_t.log(f"  Edge {u}->{v}: skip (visited)")
                    snap2(30, f"Pass2: skip {u}->{v}")
                    graph_t.deselect_edge(u, v)

        while finish_stack:
            u = finish_stack.pop()
            aux.pop("Finish Stack")
            if not visited2[u]:
                graph_t.log(f"Pop {u} from finish stack, start new SCC")
                snap2(35, f"Pop {u}, start new SCC DFS")
                scc: list[int] = []
                dfs2(u, scc)

                # Patch all nodes in this SCC
                for w in scc:
                    graph_t.deselect_node(w)
                    graph_t.patch_node(w)

                sccs.append(scc)
                scc_str = "{" + ", ".join(str(x) for x in scc) + "}"
                graph_t.log(f"SCC #{len(sccs)} found: {scc_str}")
                snap2(38, f"SCC found: {scc_str}")
                scc_color_idx += 1
            else:
                graph_t.log(f"Pop {u}: already in an SCC, skip")
                snap2(35, f"Pop {u}: already assigned")

        # Final
        graph_t.deselect_all_nodes()
        graph_t.deselect_all_edges()
        all_sccs = ["{" + ",".join(str(x) for x in s) + "}" for s in sccs]
        graph_t.log(f"All SCCs: {', '.join(all_sccs)}")
        snap2(41, f"Done! Found {len(sccs)} SCCs")
        return steps
