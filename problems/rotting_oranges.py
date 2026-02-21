from __future__ import annotations

from collections import deque

from core.step import Step
from core.tracer import Board2DTracer
from problems.base_problem import Problem

_SOURCE = """\
def orangesRotting(grid):
    m, n = len(grid), len(grid[0])
    queue = deque()
    fresh = 0

    for i in range(m):
        for j in range(n):
            if grid[i][j] == 2:
                queue.append((i, j))
            elif grid[i][j] == 1:
                fresh += 1

    if fresh == 0:
        return 0

    minutes = 0
    while queue:
        for _ in range(len(queue)):
            r, c = queue.popleft()
            for dr, dc in [(1,0),(-1,0),(0,1),(0,-1)]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < m and 0 <= nc < n:
                    if grid[nr][nc] == 1:
                        grid[nr][nc] = 2
                        fresh -= 1
                        queue.append((nr, nc))
        minutes += 1

    return minutes - 1 if fresh == 0 else -1"""


class RottingOranges(Problem):
    @staticmethod
    def name() -> str:
        return "Rotting Oranges"

    @staticmethod
    def topic() -> str:
        return "Graph / BFS"

    @staticmethod
    def subtopic() -> str:
        return "Multi-Source BFS"

    @staticmethod
    def description() -> str:
        return "LeetCode #994: Find minimum minutes until all oranges rot via BFS."

    @staticmethod
    def long_description() -> str:
        return (
            "Given a grid where `0` = empty, `1` = fresh orange, and `2` = "
            "rotten orange, every minute each rotten orange rots its "
            "4-directional neighbors. Return the minimum minutes until no "
            "fresh orange remains, or `-1` if impossible.\n\n"
            "Example 1:\n"
            "Input: `grid = [[2,1,1],[1,1,0],[0,1,1]]`\n"
            "Output: `4`\n\n"
            "Constraints:\n\n"
            "- `1 <= m, n <= 10`\n"
            "- `grid[i][j]` is `0`, `1`, or `2`"
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
    def generate_steps(**kwargs: object) -> list[Step]:
        grid_id = int(kwargs.get("grid", 1))

        grids = {
            1: [
                [2, 1, 1, 0, 0, 1, 1],
                [1, 1, 0, 1, 1, 1, 0],
                [0, 1, 1, 1, 0, 1, 1],
                [1, 0, 1, 1, 1, 0, 0],
                [1, 1, 0, 0, 1, 1, 1],
                [0, 1, 1, 0, 1, 1, 2],
                [1, 1, 0, 1, 1, 1, 1],
            ],
        }

        grid = [row[:] for row in grids.get(grid_id, grids[1])]
        m, n = len(grid), len(grid[0])

        tracer = Board2DTracer(m, n)
        steps: list[Step] = []

        def snap(line: int, desc: str = "") -> None:
            steps.append(tracer.snapshot(line, desc))

        # Initialize: 0=empty, 1=fresh, 2=rotten
        for r in range(m):
            for c in range(n):
                tracer.set_value(r, c, str(grid[r][c]))
                if grid[r][c] == 2:
                    tracer.mark_error(r, c)  # rotten = red
                elif grid[r][c] == 1:
                    pass  # fresh = green (land color)

        tracer.log(f"Grid: {m}x{n}")
        snap(2, f"Initialize {m}x{n} grid")

        queue: deque[tuple[int, int]] = deque()
        fresh = 0

        for i in range(m):
            for j in range(n):
                if grid[i][j] == 2:
                    queue.append((i, j))
                elif grid[i][j] == 1:
                    fresh += 1

        tracer.log(f"Rotten sources: {len(queue)}, Fresh: {fresh}")
        snap(8, f"Found {len(queue)} rotten, {fresh} fresh oranges")

        if fresh == 0:
            tracer.log("No fresh oranges — done!")
            snap(29, "Result: 0 minutes")
            return steps

        minutes = 0
        while queue:
            level_size = len(queue)
            tracer.deselect_all()
            tracer.log(f"--- Minute {minutes} (processing {level_size} rotten) ---")
            snap(20, f"Minute {minutes}: {level_size} rotten spreading")

            rotted_this_round = False
            for _ in range(level_size):
                r, c = queue.popleft()
                for dr, dc in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < m and 0 <= nc < n and grid[nr][nc] == 1:
                        grid[nr][nc] = 2
                        fresh -= 1
                        queue.append((nr, nc))
                        rotted_this_round = True

                        tracer.select(nr, nc)
                        tracer.set_value(nr, nc, str(2))
                        tracer.mark_error(nr, nc)
                        tracer.log(f"  Orange at ({nr},{nc}) rots!")
                        snap(27, f"({nr},{nc}) rots! Fresh left: {fresh}")
                        tracer.deselect(nr, nc)

            minutes += 1
            if not rotted_this_round:
                break

        tracer.deselect_all()
        result = minutes - 1 if fresh == 0 else -1
        tracer.log(f"Result: {result} minutes")
        snap(29, f"Result: {result} minutes")
        return steps
