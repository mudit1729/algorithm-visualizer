from __future__ import annotations

from core.step import Step
from core.tracer import Board2DTracer
from problems.base_problem import Problem

_SOURCE = """\
def minPathSum(grid):
    m, n = len(grid), len(grid[0])
    dp = [[0] * n for _ in range(m)]
    dp[0][0] = grid[0][0]

    for i in range(1, m):
        dp[i][0] = dp[i-1][0] + grid[i][0]
    for j in range(1, n):
        dp[0][j] = dp[0][j-1] + grid[0][j]

    for i in range(1, m):
        for j in range(1, n):
            dp[i][j] = grid[i][j] + min(dp[i-1][j], dp[i][j-1])

    return dp[m-1][n-1]"""


class MinPathSum(Problem):
    @staticmethod
    def name() -> str:
        return "Minimum Path Sum"

    @staticmethod
    def topic() -> str:
        return "Dynamic Programming"

    @staticmethod
    def subtopic() -> str:
        return "Grid DP"

    @staticmethod
    def description() -> str:
        return "LeetCode #64: Find minimum cost path from top-left to bottom-right in a grid."

    @staticmethod
    def long_description() -> str:
        return (
            "Given an `m x n` grid filled with non-negative numbers, find a "
            "path from top-left to bottom-right which minimizes the sum of all "
            "numbers along its path. You can only move either down or right at "
            "any point in time.\n\n"
            "Example 1:\n"
            "Input: `grid = [[1,3,1],[1,5,1],[4,2,1]]`\n"
            "Output: `7` (path 1->3->1->1->1)\n\n"
            "Constraints:\n\n"
            "- `1 <= m, n <= 200`\n"
            "- `0 <= grid[i][j] <= 200`"
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
                [1, 3, 1, 8, 2, 6, 4],
                [5, 2, 7, 1, 3, 4, 2],
                [3, 8, 1, 2, 9, 1, 7],
                [9, 1, 4, 6, 1, 3, 5],
                [2, 7, 3, 1, 8, 2, 1],
                [6, 1, 9, 2, 4, 7, 3],
                [4, 3, 2, 5, 1, 6, 8],
            ],
        }

        grid = [row[:] for row in grids.get(grid_id, grids[1])]
        m, n = len(grid), len(grid[0])
        dp = [[0] * n for _ in range(m)]

        tracer = Board2DTracer(m, n)
        steps: list[Step] = []

        def snap(line: int, desc: str = "") -> None:
            steps.append(tracer.snapshot(line, desc))

        # Initialize grid display with cost values
        for r in range(m):
            for c in range(n):
                tracer.set_value(r, c, str(grid[r][c]))

        tracer.log(f"Grid: {m}x{n} with costs 1-9")
        snap(2, f"Initialize {m}x{n} cost grid")

        # Base case: dp[0][0]
        dp[0][0] = grid[0][0]
        tracer.deselect_all()
        tracer.select(0, 0)
        tracer.set_overlay(0, 0, str(dp[0][0]), color="#3b82f6")
        tracer.patch(0, 0)
        tracer.log(f"dp[0][0] = {dp[0][0]}")
        snap(4, f"dp[0][0] = {dp[0][0]}")

        # Fill first column
        for i in range(1, m):
            dp[i][0] = dp[i - 1][0] + grid[i][0]
            tracer.deselect_all()
            tracer.select(i, 0)
            tracer.select(i - 1, 0)
            tracer.log(f"dp[{i}][0] = dp[{i-1}][0]({dp[i-1][0]}) + {grid[i][0]} = {dp[i][0]}")
            snap(7, f"dp[{i}][0] = {dp[i-1][0]} + {grid[i][0]}")

            tracer.deselect_all()
            tracer.set_overlay(i, 0, str(dp[i][0]), color="#3b82f6")
            tracer.set_arrow(i, 0, "down" if i < m - 1 else "")
            tracer.patch(i, 0)
            snap(7, f"dp[{i}][0] = {dp[i][0]}")

        # Fill first row
        for j in range(1, n):
            dp[0][j] = dp[0][j - 1] + grid[0][j]
            tracer.deselect_all()
            tracer.select(0, j)
            tracer.select(0, j - 1)
            tracer.log(f"dp[0][{j}] = dp[0][{j-1}]({dp[0][j-1]}) + {grid[0][j]} = {dp[0][j]}")
            snap(9, f"dp[0][{j}] = {dp[0][j-1]} + {grid[0][j]}")

            tracer.deselect_all()
            tracer.set_overlay(0, j, str(dp[0][j]), color="#3b82f6")
            tracer.set_arrow(0, j, "right" if j < n - 1 else "")
            tracer.patch(0, j)
            snap(9, f"dp[0][{j}] = {dp[0][j]}")

        # Fill rest of DP table
        for i in range(1, m):
            for j in range(1, n):
                tracer.deselect_all()
                tracer.select(i, j)
                tracer.select(i - 1, j)
                tracer.select(i, j - 1)

                from_top = dp[i - 1][j]
                from_left = dp[i][j - 1]
                tracer.log(
                    f"dp[{i}][{j}] = {grid[i][j]} + min(top={from_top}, left={from_left})"
                )
                snap(13, f"dp[{i}][{j}] = {grid[i][j]} + min({from_top}, {from_left})")

                dp[i][j] = grid[i][j] + min(from_top, from_left)

                tracer.deselect_all()
                tracer.select(i, j)
                tracer.set_overlay(i, j, str(dp[i][j]), color="#3b82f6")
                tracer.patch(i, j)
                came_from = "top" if from_top <= from_left else "left"
                tracer.log(f"  dp[{i}][{j}] = {dp[i][j]} (from {came_from})")
                snap(13, f"dp[{i}][{j}] = {dp[i][j]} (via {came_from})")

        # Trace back the minimum path
        tracer.deselect_all()
        path: list[tuple[int, int]] = []
        r, c = m - 1, n - 1
        path.append((r, c))
        while r > 0 or c > 0:
            if r == 0:
                c -= 1
            elif c == 0:
                r -= 1
            elif dp[r - 1][c] <= dp[r][c - 1]:
                r -= 1
            else:
                c -= 1
            path.append((r, c))
        path.reverse()

        for idx in range(len(path)):
            pr, pc = path[idx]
            tracer.mark_on_path(pr, pc)
            if idx < len(path) - 1:
                nr, nc = path[idx + 1]
                if nr > pr:
                    tracer.set_arrow(pr, pc, "down")
                else:
                    tracer.set_arrow(pr, pc, "right")

        tracer.log(f"Minimum path sum = {dp[m-1][n-1]}")
        snap(15, f"Minimum path sum = {dp[m-1][n-1]}")

        return steps
