from __future__ import annotations

from collections import deque

from core.step import Step
from core.tracer import Board2DTracer
from problems.base_problem import Problem

_SOURCE = """\
def shortestPathBinaryMatrix(grid):
    n = len(grid)
    if grid[0][0] != 0 or grid[n-1][n-1] != 0:
        return -1

    queue = deque([(0, 0, 1)])
    grid[0][0] = 1
    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),
            (0,1),(1,-1),(1,0),(1,1)]

    while queue:
        r, c, d = queue.popleft()
        if r == n-1 and c == n-1:
            return d
        for dr, dc in dirs:
            nr, nc = r + dr, c + dc
            if 0 <= nr < n and 0 <= nc < n:
                if grid[nr][nc] == 0:
                    grid[nr][nc] = 1
                    queue.append((nr, nc, d + 1))

    return -1"""


class ShortestPathBinaryMatrix(Problem):
    @staticmethod
    def name() -> str:
        return "Shortest Path in Binary Matrix"

    @staticmethod
    def topic() -> str:
        return "Graph / BFS"

    @staticmethod
    def subtopic() -> str:
        return "Shortest Path"

    @staticmethod
    def description() -> str:
        return "LeetCode #1091: Find shortest clear path in 8-directional binary grid."

    @staticmethod
    def long_description() -> str:
        return (
            "Given an `n x n` binary grid, find the length of the shortest path "
            "from top-left `(0,0)` to bottom-right `(n-1,n-1)`. The path can "
            "move in **8 directions** (including diagonals) and may only visit "
            "cells with value `0`. Return `-1` if no path exists.\n\n"
            "Example 1:\n"
            "Input: `grid = [[0,0,0],[1,1,0],[1,1,0]]`\n"
            "Output: `4`\n\n"
            "Constraints:\n\n"
            "- `1 <= n <= 100`\n"
            "- `grid[i][j]` is `0` or `1`"
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
                [0, 0, 1, 0, 0, 0, 0],
                [1, 0, 1, 0, 1, 1, 0],
                [0, 0, 0, 0, 0, 1, 0],
                [0, 1, 1, 1, 0, 0, 0],
                [0, 0, 0, 1, 0, 1, 0],
                [1, 1, 0, 0, 0, 1, 0],
                [0, 0, 0, 1, 0, 0, 0],
            ],
        }

        grid = [row[:] for row in grids.get(grid_id, grids[1])]
        n = len(grid)

        tracer = Board2DTracer(n, n)
        steps: list[Step] = []

        def snap(line: int, desc: str = "") -> None:
            steps.append(tracer.snapshot(line, desc))

        for r in range(n):
            for c in range(n):
                tracer.set_value(r, c, str(grid[r][c]))

        tracer.log(f"Grid: {n}x{n}, 8-directional BFS")
        snap(2, f"Initialize {n}x{n} grid")

        if grid[0][0] != 0 or grid[n - 1][n - 1] != 0:
            tracer.log("Start or end blocked!")
            snap(4, "Blocked: return -1")
            return steps

        queue: deque[tuple[int, int, int]] = deque([(0, 0, 1)])
        grid[0][0] = 1
        tracer.patch(0, 0)
        tracer.log("Start BFS from (0,0), path length = 1")
        snap(6, "Start at (0,0)")

        dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

        result = -1
        while queue:
            r, c, d = queue.popleft()

            tracer.deselect_all()
            tracer.select(r, c)
            snap(11, f"Process ({r},{c}), dist={d}")

            if r == n - 1 and c == n - 1:
                tracer.log(f"Reached target! Path length = {d}")
                snap(13, f"Target reached! Path = {d}")
                result = d
                break

            for dr, dc in dirs:
                nr, nc = r + dr, c + dc
                if 0 <= nr < n and 0 <= nc < n and grid[nr][nc] == 0:
                    grid[nr][nc] = 1
                    queue.append((nr, nc, d + 1))

                    tracer.set_value(nr, nc, str(1))
                    tracer.patch(nr, nc)
                    tracer.log(f"  Enqueue ({nr},{nc}), dist={d + 1}")
                    snap(18, f"Enqueue ({nr},{nc}), dist={d+1}")

        tracer.deselect_all()
        if result == -1:
            tracer.log("No path found!")
            snap(20, "No path: return -1")
        return steps
