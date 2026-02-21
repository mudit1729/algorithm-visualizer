from __future__ import annotations

from core.step import Step
from core.tracer import GraphTracer
from problems.base_problem import Problem

_SOURCE = """\
def canFinish(numCourses, prerequisites):
    adj = [[] for _ in range(numCourses)]
    for a, b in prerequisites:
        adj[b].append(a)

    state = [0] * numCourses

    def dfs(u):
        state[u] = 1
        for v in adj[u]:
            if state[v] == 1:
                return False
            if state[v] == 0 and not dfs(v):
                return False
        state[u] = 2
        return True

    return all(dfs(i) for i in range(numCourses)
               if state[i] == 0)"""


class CourseSchedule(Problem):
    @staticmethod
    def name() -> str:
        return "Course Schedule"

    @staticmethod
    def topic() -> str:
        return "Topological Sort"

    @staticmethod
    def subtopic() -> str:
        return "Cycle Detection"

    @staticmethod
    def description() -> str:
        return "LeetCode #207: Detect if courses can be finished (no cycle in dependency graph)."

    @staticmethod
    def long_description() -> str:
        return (
            "Given `numCourses` and a list of `prerequisites` pairs `[a, b]` "
            "meaning course `b` must be taken before course `a`, determine if "
            "it is possible to finish all courses. This is equivalent to "
            "detecting a cycle in a directed graph.\n\n"
            "Example 1:\n"
            "Input: `numCourses = 2`, `prerequisites = [[1,0]]`\n"
            "Output: `true`\n\n"
            "Constraints:\n\n"
            "- `1 <= numCourses <= 2000`\n"
            "- `0 <= prerequisites.length <= 5000`\n"
            "- All prerequisite pairs are unique"
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
            1: (4, [[1, 0], [2, 0], [3, 1], [3, 2]]),  # no cycle
            2: (3, [[0, 1], [1, 2], [2, 0]]),  # cycle
            3: (6, [[1, 0], [2, 1], [3, 2], [4, 3], [5, 4]]),  # chain
        }

        num_courses, prerequisites = presets.get(preset, presets[1])

        adj: list[list[int]] = [[] for _ in range(num_courses)]
        for a, b in prerequisites:
            adj[b].append(a)

        tracer = GraphTracer(list(range(num_courses)), directed=True)
        steps: list[Step] = []

        def snap(line: int, desc: str = "") -> None:
            steps.append(tracer.snapshot(line, desc))

        for a, b in prerequisites:
            tracer.add_edge(b, a)

        edges_str = ", ".join(f"{b}->{a}" for a, b in prerequisites)
        tracer.log(f"Courses: {num_courses}, Edges: {edges_str}")
        snap(3, f"{num_courses} courses, edges: {edges_str}")

        state = [0] * num_courses
        has_cycle = False

        def dfs(u: int) -> bool:
            nonlocal has_cycle
            state[u] = 1
            tracer.select_node(u)
            tracer.set_node_color(u, "#f9e2af")
            tracer.log(f"DFS({u}): mark IN_PROGRESS")
            snap(8, f"DFS({u}): in-progress")

            for v in adj[u]:
                tracer.select_edge(u, v)
                if state[v] == 1:
                    tracer.mark_node_error(v)
                    tracer.mark_node_error(u)
                    tracer.mark_edge_error(u, v)
                    tracer.log(f"  Edge {u}->{v}: CYCLE! (back edge)")
                    snap(11, f"Cycle: {u}->{v}")
                    has_cycle = True
                    return False
                if state[v] == 0:
                    tracer.log(f"  Visit {u}->{v}")
                    snap(13, f"DFS {u}->{v}")
                    tracer.deselect_edge(u, v)
                    if not dfs(v):
                        return False
                else:
                    tracer.deselect_edge(u, v)

            state[u] = 2
            tracer.deselect_node(u)
            tracer.set_node_color(u, "")
            tracer.patch_node(u)
            tracer.log(f"DFS({u}): COMPLETED")
            snap(15, f"DFS({u}): completed")
            return True

        for i in range(num_courses):
            if state[i] == 0:
                if not dfs(i):
                    break

        tracer.deselect_all_nodes()
        tracer.deselect_all_edges()
        tracer.clear_all_node_errors()
        result = not has_cycle
        tracer.log(f"Result: {'Can finish' if result else 'Cannot finish (cycle)'}")
        snap(18, f"Result: {result}")
        return steps
