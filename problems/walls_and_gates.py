from __future__ import annotations

from collections import deque

from core.step import Step
from core.tracer import Board2DTracer
from problems.base_problem import Problem

_SOURCE = """\
def wallsAndGates(rooms):
    if not rooms:
        return
    m, n = len(rooms), len(rooms[0])
    INF = 2147483647
    queue = deque()

    for i in range(m):
        for j in range(n):
            if rooms[i][j] == 0:
                queue.append((i, j))

    while queue:
        r, c = queue.popleft()
        for dr, dc in [(1,0),(-1,0),(0,1),(0,-1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < m and 0 <= nc < n:
                if rooms[nr][nc] == INF:
                    rooms[nr][nc] = rooms[r][c] + 1
                    queue.append((nr, nc))"""


class WallsAndGates(Problem):
    @staticmethod
    def name() -> str:
        return "Walls and Gates"

    @staticmethod
    def topic() -> str:
        return "Graph / BFS"

    @staticmethod
    def subtopic() -> str:
        return "Multi-Source BFS"

    @staticmethod
    def description() -> str:
        return "LeetCode #286: Fill rooms with distance to nearest gate via multi-source BFS."

    @staticmethod
    def long_description() -> str:
        return (
            "Given an `m x n` grid where `-1` = wall, `0` = gate, and "
            "`INF` = empty room, fill each empty room with the distance to its "
            "nearest gate using multi-source BFS. Unreachable rooms stay `INF`.\n\n"
            "Example 1:\n"
            "Input: `rooms = [[INF,-1,0,INF],[INF,INF,INF,-1],[INF,-1,INF,-1],[0,-1,INF,INF]]`\n"
            "Output: `[[3,-1,0,1],[2,2,1,-1],[1,-1,2,-1],[0,-1,3,4]]`\n\n"
            "Constraints:\n\n"
            "- `1 <= m, n <= 250`\n"
            "- `rooms[i][j]` is `-1`, `0`, or `2147483647`"
        )

    @staticmethod
    def source_code() -> str:
        return _SOURCE

    @staticmethod
    def renderer_type() -> str:
        return "board"

    @staticmethod
    def default_params() -> dict[str, object]:
        return {"grid": 1}

    @staticmethod
    def theory() -> str:
        return """Approach: Multi-source BFS from all gates simultaneously. Start by adding all gate positions (cells with value 0) to a queue, then BFS outward. Each empty room gets filled with its distance to the nearest gate on first visit.

Time Complexity: O(M × N) — each cell is enqueued and processed at most once.

Space Complexity: O(M × N) for the BFS queue (worst case all cells are gates).

Key Insight: Multi-source BFS finds shortest distances from any source simultaneously, like dropping stones into a pond and letting the ripples expand. Each cell is reached by whichever gate is closest.

Interview Tip: Single-source BFS from each gate would be O(M²N²). Multi-source BFS from all gates at once is the key optimization — it's O(MN) because each cell is visited exactly once."""

    @staticmethod
    def generate_steps(**kwargs: object) -> list[Step]:
        grid_id = int(kwargs.get("grid", 1))
        INF = 2147483647

        grids = {
            1: [
                [INF, -1,  0,  INF, INF, INF, -1 ],
                [INF, INF, INF, -1,  INF, INF, INF],
                [INF, -1,  INF, -1,  INF, -1,  INF],
                [0,   -1,  INF, INF, INF, INF, INF],
                [INF, INF, -1,  INF, -1,  INF,  0 ],
                [INF, -1,  INF, INF, INF, INF, INF],
                [-1,  INF, INF, 0,   -1,  INF, INF],
            ],
        }

        rooms = [row[:] for row in grids.get(grid_id, grids[1])]
        m, n = len(rooms), len(rooms[0])

        tracer = Board2DTracer(m, n)
        steps: list[Step] = []

        def snap(line: int, desc: str = "") -> None:
            steps.append(tracer.snapshot(line, desc))

        # Display: gates=0, walls=-1, rooms=INF shown as "."
        for r in range(m):
            for c in range(n):
                if rooms[r][c] == -1:
                    tracer.set_value(r, c, "W")
                    tracer.mark_error(r, c)
                elif rooms[r][c] == 0:
                    tracer.set_value(r, c, "0")
                    tracer.patch(r, c)
                else:
                    tracer.set_value(r, c, ".")

        tracer.log(f"Rooms: {m}x{n} (0=gate, W=wall, .=empty)")
        snap(4, f"Initialize {m}x{n} grid")

        queue: deque[tuple[int, int]] = deque()
        for i in range(m):
            for j in range(n):
                if rooms[i][j] == 0:
                    queue.append((i, j))

        tracer.log(f"Gates found: {len(queue)}")
        snap(11, f"{len(queue)} gates enqueued as BFS sources")

        while queue:
            r, c = queue.popleft()

            tracer.deselect_all()
            tracer.select(r, c)
            snap(15, f"Process ({r},{c}), dist={rooms[r][c]}")

            for dr, dc in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < m and 0 <= nc < n and rooms[nr][nc] == INF:
                    rooms[nr][nc] = rooms[r][c] + 1
                    queue.append((nr, nc))

                    tracer.set_value(nr, nc, str(rooms[nr][nc]))
                    tracer.patch(nr, nc)
                    tracer.log(f"  Room ({nr},{nc}) = {rooms[nr][nc]}")
                    snap(20, f"Room ({nr},{nc}) dist = {rooms[nr][nc]}")

            tracer.deselect(r, c)

        tracer.deselect_all()
        tracer.log("All reachable rooms filled!")
        snap(19, "All rooms filled with distances")
        return steps
