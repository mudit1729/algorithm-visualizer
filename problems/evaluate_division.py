from __future__ import annotations

from collections import deque

from core.step import Step
from core.tracer import AuxPanelTracer, GraphTracer, combine_step
from problems.base_problem import Problem

_SOURCE = """\
def calcEquation(equations, values, queries):
    graph = defaultdict(dict)
    for (a, b), v in zip(equations, values):
        graph[a][b] = v
        graph[b][a] = 1.0 / v

    def bfs(src, dst):
        if src not in graph or dst not in graph:
            return -1.0
        if src == dst:
            return 1.0
        visited = set([src])
        queue = deque([(src, 1.0)])
        while queue:
            node, prod = queue.popleft()
            for nei, w in graph[node].items():
                if nei == dst:
                    return prod * w
                if nei not in visited:
                    visited.add(nei)
                    queue.append((nei, prod * w))
        return -1.0

    return [bfs(a, b) for a, b in queries]"""


class EvaluateDivision(Problem):
    @staticmethod
    def name() -> str:
        return "Evaluate Division"

    @staticmethod
    def topic() -> str:
        return "Graph / DFS"

    @staticmethod
    def subtopic() -> str:
        return "Weighted Graph"

    @staticmethod
    def description() -> str:
        return "LeetCode #399: Answer division queries by BFS on a weighted graph."

    @staticmethod
    def long_description() -> str:
        return (
            "Given equations like `a / b = 2.0` and `b / c = 3.0`, answer queries "
            "such as `a / c = ?` by finding a path in a weighted directed graph and "
            "multiplying edge weights along the path.\n\n"
            "Example 1:\n"
            "Input: `equations = [[a,b],[b,c]]`, `values = [2.0,3.0]`, "
            "`queries = [[a,c],[b,a]]`\n"
            "Output: `[6.0, 0.5]`\n\n"
            "Constraints:\n\n"
            "- `1 <= equations.length <= 20`\n"
            "- `1 <= queries.length <= 20`\n"
            "- All variable names are lowercase English letters"
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

        # equations, values, queries
        presets = {
            1: (
                [("a", "b"), ("b", "c"), ("c", "d"), ("d", "e"), ("b", "f")],
                [2.0, 3.0, 4.0, 0.5, 0.25],
                [("a", "e"), ("f", "d"), ("a", "a"), ("x", "a")],
            ),
        }

        equations, values, queries = presets.get(preset, presets[1])

        # Collect all variables
        var_set: set[str] = set()
        for a, b in equations:
            var_set.add(a)
            var_set.add(b)
        variables = sorted(var_set)

        # Build adjacency
        graph: dict[str, dict[str, float]] = {v: {} for v in variables}
        for (a, b), v in zip(equations, values):
            graph[a][b] = v
            graph[b][a] = 1.0 / v

        tracer = GraphTracer(variables, directed=True)
        aux = AuxPanelTracer()
        aux.add_panel("Query")
        aux.add_panel("Answers")
        steps: list[Step] = []

        def snap(line: int, desc: str = "") -> None:
            steps.append(combine_step(tracer.snapshot(line, desc), aux))

        # Add edges with weights (both directions)
        for (a, b), v in zip(equations, values):
            tracer.add_edge(a, b, weight=v)
            tracer.add_edge(b, a, weight=round(1.0 / v, 4))
            # Offset reverse edges so they don't overlap
            tracer.set_edge_curve_offset(a, b, 0.15)
            tracer.set_edge_curve_offset(b, a, 0.15)

        tracer.log(f"Variables: {variables}")
        tracer.log(f"Equations: {len(equations)}")
        snap(4, f"Build graph: {len(variables)} variables, {len(equations)} equations")

        # Process each query
        answers: list[float] = []

        for qi, (src, dst) in enumerate(queries):
            aux.clear_panel("Query")
            aux.push("Query", f"{src} / {dst}", f"query {qi + 1}")

            tracer.deselect_all_nodes()
            tracer.deselect_all_edges()
            tracer.depatch_all_nodes()
            tracer.depatch_all_edges()

            tracer.log(f"--- Query {qi + 1}: {src} / {dst} ---")
            snap(8, f"Query {qi + 1}: {src} / {dst}")

            # Check if variables exist
            if src not in graph or dst not in graph:
                tracer.log(f"  Variable not in graph -> -1.0")
                answers.append(-1.0)
                aux.push("Answers", f"Q{qi + 1}: {src}/{dst}", "-1.0")
                snap(10, f"{src}/{dst} = -1.0 (unknown variable)")
                continue

            if src == dst:
                tracer.select_node(src)
                tracer.patch_node(src)
                tracer.log(f"  Same variable -> 1.0")
                answers.append(1.0)
                aux.push("Answers", f"Q{qi + 1}: {src}/{dst}", "1.0")
                snap(12, f"{src}/{dst} = 1.0 (same variable)")
                continue

            # BFS to find path
            visited: set[str] = {src}
            bfs_queue: deque[tuple[str, float, list[str]]] = deque(
                [(src, 1.0, [src])]
            )
            tracer.select_node(src)
            tracer.log(f"  BFS from {src}")
            snap(14, f"Start BFS from '{src}'")

            found = False
            while bfs_queue:
                node, prod, path = bfs_queue.popleft()

                for nei, w in graph[node].items():
                    if nei == dst:
                        # Found the target
                        result = prod * w
                        new_path = path + [nei]

                        # Highlight the full path
                        tracer.deselect_all_nodes()
                        tracer.deselect_all_edges()
                        for p_node in new_path:
                            tracer.patch_node(p_node)
                        for i in range(len(new_path) - 1):
                            tracer.patch_edge(new_path[i], new_path[i + 1])
                            tracer.select_edge(new_path[i], new_path[i + 1])

                        path_str = " -> ".join(new_path)
                        tracer.log(f"  Found path: {path_str} = {result:.4f}")
                        answers.append(result)
                        aux.push(
                            "Answers",
                            f"Q{qi + 1}: {src}/{dst}",
                            f"{result:.4f}",
                        )
                        snap(24, f"{src}/{dst} = {result:.4f} via {path_str}")
                        found = True
                        break

                    if nei not in visited:
                        visited.add(nei)
                        new_path = path + [nei]
                        bfs_queue.append((nei, prod * w, new_path))

                        tracer.select_node(nei)
                        tracer.select_edge(node, nei)
                        tracer.log(f"  Visit {nei}, product = {prod * w:.4f}")
                        snap(22, f"Visit '{nei}', running product = {prod * w:.4f}")
                        tracer.deselect_edge(node, nei)

                if found:
                    break

            if not found:
                tracer.log(f"  No path found -> -1.0")
                answers.append(-1.0)
                aux.push("Answers", f"Q{qi + 1}: {src}/{dst}", "-1.0")
                snap(24, f"{src}/{dst} = -1.0 (no path)")

        # Final result
        tracer.deselect_all_nodes()
        tracer.deselect_all_edges()
        tracer.depatch_all_nodes()
        tracer.depatch_all_edges()
        ans_str = ", ".join(f"{a:.4f}" for a in answers)
        tracer.log(f"All answers: [{ans_str}]")
        snap(24, f"Done! Answers: [{ans_str}]")
        return steps
