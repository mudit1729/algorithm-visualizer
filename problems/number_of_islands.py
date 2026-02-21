from __future__ import annotations

from core.step import Step
from core.tracer import Board2DTracer
from problems.base_problem import Problem

_SOURCE = """\
def numIslands(grid):
    m, n = len(grid), len(grid[0])
    count = 0

    def dfs(r, c):
        if r < 0 or r >= m or c < 0 or c >= n:
            return
        if grid[r][c] != '1':
            return
        grid[r][c] = '0'
        dfs(r + 1, c)
        dfs(r - 1, c)
        dfs(r, c + 1)
        dfs(r, c - 1)

    for i in range(m):
        for j in range(n):
            if grid[i][j] == '1':
                count += 1
                dfs(i, j)
    return count"""

# Example grids the user can choose from via the "grid" param
_GRIDS: dict[int, list[list[str]]] = {
    1: [
        ["1", "1", "0", "0", "1", "1", "0"],
        ["1", "1", "0", "0", "0", "1", "0"],
        ["0", "0", "0", "1", "0", "0", "0"],
        ["0", "1", "0", "1", "1", "0", "1"],
        ["0", "1", "0", "0", "0", "0", "1"],
        ["0", "0", "0", "0", "1", "0", "1"],
        ["1", "1", "0", "0", "1", "0", "0"],
    ],
}


class NumberOfIslands(Problem):
    @staticmethod
    def name() -> str:
        return "Number of Islands"

    @staticmethod
    def topic() -> str:
        return "Graph / DFS"

    @staticmethod
    def subtopic() -> str:
        return "Flood Fill"

    @staticmethod
    def description() -> str:
        return (
            "LeetCode #200: Count islands in a grid using DFS flood fill."
        )

    @staticmethod
    def long_description() -> str:
        return (
            "Given an `m x n` 2D binary grid where `'1'` represents land and "
            "`'0'` represents water, count the number of islands. An island is "
            "a group of adjacent land cells connected horizontally or vertically.\n\n"
            "Example 1:\n"
            "Input: `grid = [[1,1,0,0,0],[1,1,0,0,0],[0,0,1,0,0],[0,0,0,1,1]]`\n"
            "Output: `3`\n\n"
            "Constraints:\n\n"
            "- `1 <= m, n <= 300`\n"
            "- `grid[i][j]` is `'0'` or `'1'`"
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
        grid_template = _GRIDS.get(grid_id, _GRIDS[1])

        # Deep copy the grid
        grid = [row[:] for row in grid_template]
        m, n = len(grid), len(grid[0])

        tracer = Board2DTracer(m, n)
        steps: list[Step] = []

        def snap(line: int, desc: str = "") -> None:
            steps.append(tracer.snapshot(line, desc))

        # Initialize tracer with grid values
        for r in range(m):
            for c in range(n):
                tracer.set_value(r, c, grid[r][c])

        tracer.log(f"Grid: {m}x{n}")
        snap(2, f"Initialize {m}x{n} grid")

        count = 0

        def dfs(r: int, c: int) -> None:
            # Check bounds
            if r < 0 or r >= m or c < 0 or c >= n:
                return

            tracer.deselect_all()
            tracer.select(r, c)
            snap(7, f"Check ({r},{c}): {'land' if grid[r][c] == '1' else 'water/visited'}")

            if grid[r][c] != "1":
                tracer.deselect(r, c)
                return

            # Mark as visited
            grid[r][c] = "0"
            tracer.set_value(r, c, "0")
            tracer.deselect(r, c)
            tracer.patch(r, c)
            tracer.log(f"Visit ({r},{c})")
            snap(9, f"Mark ({r},{c}) as visited")

            # Recurse in 4 directions
            dfs(r + 1, c)
            dfs(r - 1, c)
            dfs(r, c + 1)
            dfs(r, c - 1)

        # Main loop
        for i in range(m):
            for j in range(n):
                tracer.deselect_all()
                tracer.select(i, j)
                snap(17, f"Scan ({i},{j})")

                if grid[i][j] == "1":
                    count += 1
                    tracer.log(f"Found island #{count} at ({i},{j})")
                    snap(19, f"Found island #{count} starting at ({i},{j})")
                    tracer.deselect(i, j)
                    dfs(i, j)
                else:
                    tracer.deselect(i, j)

        tracer.deselect_all()
        tracer.depatch_all()
        tracer.log(f"Total islands: {count}")
        snap(21, f"Done! Found {count} islands")

        return steps
