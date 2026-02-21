from __future__ import annotations

from collections import deque

from core.step import Step
from core.tracer import GraphTracer
from problems.base_problem import Problem

_SOURCE = """\
def findOrder(numCourses, prerequisites):
    adj = [[] for _ in range(numCourses)]
    in_degree = [0] * numCourses

    for a, b in prerequisites:
        adj[b].append(a)
        in_degree[a] += 1

    queue = deque(i for i in range(numCourses)
                  if in_degree[i] == 0)
    order = []

    while queue:
        u = queue.popleft()
        order.append(u)
        for v in adj[u]:
            in_degree[v] -= 1
            if in_degree[v] == 0:
                queue.append(v)

    return order if len(order) == numCourses else []"""


class CourseScheduleII(Problem):
    @staticmethod
    def name() -> str:
        return "Course Schedule II"

    @staticmethod
    def topic() -> str:
        return "Topological Sort"

    @staticmethod
    def subtopic() -> str:
        return "Kahn's Algorithm"

    @staticmethod
    def description() -> str:
        return "LeetCode #210: Find valid course ordering using Kahn's topological sort."

    @staticmethod
    def long_description() -> str:
        return (
            "Given `numCourses` and a list of `prerequisites` pairs `[a, b]` "
            "meaning course `b` must be taken before course `a`, return a valid "
            "ordering to finish all courses. If no valid ordering exists (cycle), "
            "return an empty array. Uses **Kahn's algorithm** (BFS topological sort).\n\n"
            "Example 1:\n"
            "Input: `numCourses = 4`, `prerequisites = [[1,0],[2,0],[3,1],[3,2]]`\n"
            "Output: `[0,1,2,3]`\n\n"
            "Constraints:\n\n"
            "- `1 <= numCourses <= 2000`\n"
            "- `0 <= prerequisites.length <= numCourses * (numCourses - 1)`\n"
            "- All prerequisite pairs are distinct"
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
                    [1, 0], [2, 0], [3, 1], [4, 2],
                    [5, 3], [5, 4], [6, 1], [7, 5], [7, 6],
                ],
            ),
        }

        num_courses, prerequisites = presets.get(preset, presets[1])

        adj: list[list[int]] = [[] for _ in range(num_courses)]
        in_degree = [0] * num_courses
        for a, b in prerequisites:
            adj[b].append(a)
            in_degree[a] += 1

        tracer = GraphTracer(list(range(num_courses)), directed=True)
        steps: list[Step] = []

        def snap(line: int, desc: str = "") -> None:
            steps.append(tracer.snapshot(line, desc))

        for a, b in prerequisites:
            tracer.add_edge(b, a)

        # Show in-degrees as labels
        for i in range(num_courses):
            tracer.set_label(i, f"{i}({in_degree[i]})")

        edges_str = ", ".join(f"{b}->{a}" for a, b in prerequisites)
        tracer.log(f"Courses: {num_courses}, Edges: {edges_str}")
        tracer.log(f"Labels show node(in-degree)")
        snap(4, f"{num_courses} courses, showing in-degrees")

        queue: deque[int] = deque()
        for i in range(num_courses):
            if in_degree[i] == 0:
                queue.append(i)
                tracer.select_node(i)

        tracer.log(f"Initial queue (in-degree 0): {list(queue)}")
        snap(9, f"Courses with no prereqs: {list(queue)}")

        order: list[int] = []
        order_pos = 1
        while queue:
            u = queue.popleft()
            order.append(u)
            tracer.deselect_all_nodes()
            tracer.deselect_all_edges()
            tracer.patch_node(u)
            tracer.set_label(u, f"{u}[#{order_pos}]")
            tracer.log(f"Take course {u} (order: {order})")
            snap(13, f"Take course {u}")
            order_pos += 1

            for v in adj[u]:
                in_degree[v] -= 1
                tracer.set_label(v, f"{v}({in_degree[v]})")
                tracer.select_edge(u, v)
                tracer.select_node(v)
                tracer.log(f"  in_degree[{v}] = {in_degree[v]}")
                snap(16, f"in_degree[{v}] = {in_degree[v]}")

                if in_degree[v] == 0:
                    queue.append(v)
                    tracer.log(f"  Course {v} ready!")
                    snap(18, f"Course {v} now available")

            tracer.deselect_all_nodes()
            tracer.deselect_all_edges()

        if len(order) == num_courses:
            tracer.log(f"Valid order: {order}")
            snap(20, f"Order: {order}")
        else:
            tracer.log("Cycle detected! No valid ordering.")
            snap(20, "Cycle: no valid order")
        return steps
