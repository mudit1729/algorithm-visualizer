from __future__ import annotations

from core.step import Step
from core.tracer import Board2DTracer
from problems.base_problem import Problem

_SOURCE = """\
def uniquePaths(m, n):
    dp = [[0] * n for _ in range(m)]

    for i in range(m):
        dp[i][0] = 1
    for j in range(n):
        dp[0][j] = 1

    for i in range(1, m):
        for j in range(1, n):
            dp[i][j] = dp[i-1][j] + dp[i][j-1]

    return dp[m-1][n-1]"""


class UniquePaths(Problem):
    @staticmethod
    def name() -> str:
        return "Unique Paths"

    @staticmethod
    def topic() -> str:
        return "Dynamic Programming"

    @staticmethod
    def subtopic() -> str:
        return "Grid DP"

    @staticmethod
    def description() -> str:
        return "LeetCode #62: Count unique paths from top-left to bottom-right using DP."

    @staticmethod
    def long_description() -> str:
        return (
            "A robot is located at the top-left corner of an `m x n` grid. "
            "It can only move either down or right at any point. The robot is "
            "trying to reach the bottom-right corner. How many unique paths "
            "are there?\n\n"
            "Example 1:\n"
            "Input: `m = 3`, `n = 7`\n"
            "Output: `28`\n\n"
            "Example 2:\n"
            "Input: `m = 3`, `n = 2`\n"
            "Output: `3`\n\n"
            "Constraints:\n\n"
            "- `1 <= m, n <= 100`"
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
        return """Approach: Count the number of unique paths from top-left to bottom-right of a grid, moving only right or down. Use dynamic programming: dp[i][j] = dp[i-1][j] + dp[i][j-1]. The first row and column are all 1's (only one way to reach them).

Time Complexity: O(M × N) — fill the entire DP table.

Space Complexity: O(N) with space optimization (only need the previous row), or O(M × N) for the full table.

Key Insight: This is a combinatorial problem: the answer is C(m+n-2, m-1) = (m+n-2)! / ((m-1)! × (n-1)!). DP avoids computing large factorials and generalizes to grids with obstacles.

Interview Tip: Mention the math formula as an O(min(m,n)) alternative. If the interviewer adds obstacles, the DP approach handles it naturally by setting dp[i][j] = 0 for blocked cells."""

    @staticmethod
    def generate_steps(**kwargs: object) -> list[Step]:
        grid_id = int(kwargs.get("grid", 1))

        m, n = 7, 7
        dp = [[0] * n for _ in range(m)]

        tracer = Board2DTracer(m, n)
        steps: list[Step] = []

        def snap(line: int, desc: str = "") -> None:
            steps.append(tracer.snapshot(line, desc))

        # Initialize grid display
        for r in range(m):
            for c in range(n):
                tracer.set_value(r, c, ".")

        tracer.log(f"Grid: {m}x{n}, count unique paths top-left to bottom-right")
        snap(2, f"Initialize {m}x{n} DP grid")

        # Fill first column
        for i in range(m):
            dp[i][0] = 1
            tracer.deselect_all()
            tracer.select(i, 0)
            tracer.set_overlay(i, 0, "1")
            tracer.set_arrow(i, 0, "down" if i < m - 1 else "")
            tracer.patch(i, 0)
            tracer.log(f"dp[{i}][0] = 1 (only one way: straight down)")
            snap(5, f"dp[{i}][0] = 1")

        # Fill first row
        for j in range(1, n):
            dp[0][j] = 1
            tracer.deselect_all()
            tracer.select(0, j)
            tracer.set_overlay(0, j, "1")
            tracer.set_arrow(0, j, "right" if j < n - 1 else "")
            tracer.patch(0, j)
            tracer.log(f"dp[0][{j}] = 1 (only one way: straight right)")
            snap(7, f"dp[0][{j}] = 1")

        # Fill rest of the DP table
        for i in range(1, m):
            for j in range(1, n):
                tracer.deselect_all()
                tracer.select(i, j)

                # Highlight the two cells we are summing
                tracer.select(i - 1, j)
                tracer.select(i, j - 1)
                tracer.log(f"Computing dp[{i}][{j}] = dp[{i-1}][{j}] + dp[{i}][{j-1}]")
                snap(13, f"dp[{i}][{j}] = dp[{i-1}][{j}]({dp[i-1][j]}) + dp[{i}][{j-1}]({dp[i][j-1]})")

                dp[i][j] = dp[i - 1][j] + dp[i][j - 1]

                tracer.deselect_all()
                tracer.select(i, j)
                tracer.set_overlay(i, j, str(dp[i][j]))
                tracer.patch(i, j)
                tracer.log(f"  dp[{i}][{j}] = {dp[i][j]}")
                snap(13, f"dp[{i}][{j}] = {dp[i][j]}")

        # Trace one optimal path (always go right then down, or along edge)
        tracer.deselect_all()
        tracer.clear_all_paths()
        r, c = m - 1, n - 1
        path: list[tuple[int, int]] = [(r, c)]
        while r > 0 or c > 0:
            if r == 0:
                c -= 1
            elif c == 0:
                r -= 1
            elif dp[r - 1][c] >= dp[r][c - 1]:
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

        tracer.log(f"Answer: {dp[m-1][n-1]} unique paths. One path highlighted.")
        snap(13, f"Result: {dp[m-1][n-1]} unique paths")

        return steps
