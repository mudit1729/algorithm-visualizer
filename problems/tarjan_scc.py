from __future__ import annotations

from core.step import Step
from core.tracer import AuxPanelTracer, GraphTracer, combine_step
from problems.base_problem import Problem

_SOURCE = """\
def tarjan_scc(n, adj):
    disc = [-1] * n
    low = [-1] * n
    on_stack = [False] * n
    stack = []
    timer = [0]
    sccs = []

    def dfs(u):
        disc[u] = low[u] = timer[0]
        timer[0] += 1
        stack.append(u)
        on_stack[u] = True

        for v in adj[u]:
            if disc[v] == -1:
                dfs(v)
                low[u] = min(low[u], low[v])
            elif on_stack[v]:
                low[u] = min(low[u], disc[v])

        if low[u] == disc[u]:
            scc = []
            while True:
                w = stack.pop()
                on_stack[w] = False
                scc.append(w)
                if w == u:
                    break
            sccs.append(scc)

    for i in range(n):
        if disc[i] == -1:
            dfs(i)

    return sccs"""

# SCC colors used when an SCC is identified
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


class TarjanSCC(Problem):
    @staticmethod
    def name() -> str:
        return "Tarjan's SCC"

    @staticmethod
    def topic() -> str:
        return "Graph / DFS"

    @staticmethod
    def subtopic() -> str:
        return "Strongly Connected Components"

    @staticmethod
    def description() -> str:
        return "Find all Strongly Connected Components using Tarjan's algorithm with disc/low values and a stack."

    @staticmethod
    def long_description() -> str:
        return (
            "Tarjan's algorithm finds all strongly connected components (SCCs) "
            "in a directed graph using a single DFS pass. It maintains discovery "
            "times (`disc`), low-link values (`low`), and an explicit stack.\n\n"
            "A node `u` is the root of an SCC when `low[u] == disc[u]`. At that "
            "point, all nodes on the stack above `u` (inclusive) form one SCC.\n\n"
            "Time complexity: `O(V + E)`\n\n"
            "Visualization:\n\n"
            "- Node badges show `disc/low` values\n"
            "- Tree, back, and cross edges are classified\n"
            "- Each SCC is colored differently when found"
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

        # 8 nodes, directed graph with 3 SCCs:
        #   SCC1: {0, 1, 2}    (0->1->2->0)
        #   SCC2: {3, 4, 5}    (3->4->5->3)
        #   SCC3: {6, 7}       (6->7->6)
        # Cross-SCC edges: 2->3, 5->6
        presets = {
            1: (
                8,
                [
                    (0, 1), (1, 2), (2, 0),   # SCC {0,1,2}
                    (2, 3),                     # cross to SCC {3,4,5}
                    (3, 4), (4, 5), (5, 3),   # SCC {3,4,5}
                    (5, 6),                     # cross to SCC {6,7}
                    (6, 7), (7, 6),            # SCC {6,7}
                ],
            ),
        }

        n, edges = presets.get(preset, presets[1])
        adj: list[list[int]] = [[] for _ in range(n)]
        for u, v in edges:
            adj[u].append(v)

        graph = GraphTracer(list(range(n)), directed=True)
        aux = AuxPanelTracer()
        aux.add_panel("Stack")
        steps: list[Step] = []

        def snap(line: int, desc: str = "") -> None:
            steps.append(combine_step(graph.snapshot(line, desc), aux))

        # Add edges to graph
        for u, v in edges:
            graph.add_edge(u, v)

        edge_str = ", ".join(f"{u}->{v}" for u, v in edges)
        graph.log(f"Directed graph: {n} nodes, edges: {edge_str}")
        snap(1, f"Directed graph with {n} nodes and {len(edges)} edges")

        # Tarjan's algorithm state
        disc = [-1] * n
        low = [-1] * n
        on_stack = [False] * n
        stack: list[int] = []
        timer = [0]
        sccs: list[list[int]] = []
        scc_color_idx = 0

        def dfs(u: int) -> None:
            nonlocal scc_color_idx

            # disc[u] = low[u] = timer; timer += 1
            disc[u] = low[u] = timer[0]
            timer[0] += 1
            graph.select_node(u)
            graph.set_node_badge(u, f"{disc[u]}/{low[u]}")
            graph.log(f"DFS({u}): disc={disc[u]}, low={low[u]}")
            snap(10, f"DFS({u}): discover, disc={disc[u]}")

            # stack.append(u); on_stack[u] = True
            stack.append(u)
            on_stack[u] = True
            aux.push("Stack", str(u), f"disc={disc[u]}")
            graph.log(f"Push {u} onto stack")
            snap(13, f"Push {u} onto stack")

            for v in adj[u]:
                graph.select_edge(u, v)
                if disc[v] == -1:
                    # Tree edge
                    graph.set_edge_class(u, v, "tree")
                    graph.log(f"  Edge {u}->{v}: tree edge, recurse")
                    snap(16, f"Tree edge {u}->{v}")
                    graph.deselect_edge(u, v)
                    dfs(v)
                    # low[u] = min(low[u], low[v])
                    low[u] = min(low[u], low[v])
                    graph.set_node_badge(u, f"{disc[u]}/{low[u]}")
                    graph.log(f"  Back from {v}: low[{u}] = min(low[{u}], low[{v}]) = {low[u]}")
                    snap(18, f"Update low[{u}]={low[u]} from child {v}")
                elif on_stack[v]:
                    # Back edge
                    graph.set_edge_class(u, v, "back")
                    low[u] = min(low[u], disc[v])
                    graph.set_node_badge(u, f"{disc[u]}/{low[u]}")
                    graph.log(f"  Edge {u}->{v}: back edge, low[{u}] = min(low[{u}], disc[{v}]) = {low[u]}")
                    snap(20, f"Back edge {u}->{v}, low[{u}]={low[u]}")
                    graph.deselect_edge(u, v)
                else:
                    # Cross edge (already in a finished SCC)
                    graph.set_edge_class(u, v, "cross")
                    graph.log(f"  Edge {u}->{v}: cross edge (v already in SCC)")
                    snap(20, f"Cross edge {u}->{v}")
                    graph.deselect_edge(u, v)

            # Check if u is root of SCC
            if low[u] == disc[u]:
                scc: list[int] = []
                graph.log(f"low[{u}] == disc[{u}] == {disc[u]}: SCC root found!")
                snap(23, f"low[{u}]==disc[{u}], SCC root!")

                color = _SCC_COLORS[scc_color_idx % len(_SCC_COLORS)]
                while True:
                    w = stack.pop()
                    on_stack[w] = False
                    scc.append(w)
                    aux.pop("Stack")
                    graph.deselect_node(w)
                    graph.set_node_color(w, color)
                    graph.patch_node(w)
                    graph.log(f"  Pop {w} from stack into SCC")
                    snap(27, f"Pop {w} into SCC")
                    if w == u:
                        break

                sccs.append(scc)
                scc_str = "{" + ", ".join(str(x) for x in reversed(scc)) + "}"
                graph.log(f"SCC #{len(sccs)}: {scc_str}")
                snap(31, f"SCC found: {scc_str}")
                scc_color_idx += 1
            else:
                graph.deselect_node(u)

        # Main loop
        for i in range(n):
            if disc[i] == -1:
                graph.log(f"Start DFS from node {i}")
                snap(34, f"Start DFS from unvisited node {i}")
                dfs(i)

        # Final summary
        graph.deselect_all_nodes()
        graph.deselect_all_edges()
        all_sccs = ["{" + ",".join(str(x) for x in reversed(s)) + "}" for s in sccs]
        graph.log(f"All SCCs found: {', '.join(all_sccs)}")
        snap(37, f"Done! Found {len(sccs)} SCCs")
        return steps
