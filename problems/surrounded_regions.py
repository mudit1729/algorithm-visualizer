from __future__ import annotations

from core.step import Step
from core.tracer import Board2DTracer
from problems.base_problem import Problem

_SOURCE = """\
def solve(board):
    m, n = len(board), len(board[0])

    def dfs(r, c):
        if r < 0 or r >= m or c < 0 or c >= n:
            return
        if board[r][c] != 'O':
            return
        board[r][c] = 'S'
        dfs(r + 1, c)
        dfs(r - 1, c)
        dfs(r, c + 1)
        dfs(r, c - 1)

    for i in range(m):
        dfs(i, 0)
        dfs(i, n - 1)
    for j in range(n):
        dfs(0, j)
        dfs(m - 1, j)

    for i in range(m):
        for j in range(n):
            if board[i][j] == 'O':
                board[i][j] = 'X'
            elif board[i][j] == 'S':
                board[i][j] = 'O'"""


class SurroundedRegions(Problem):
    @staticmethod
    def name() -> str:
        return "Surrounded Regions"

    @staticmethod
    def topic() -> str:
        return "Graph / DFS"

    @staticmethod
    def subtopic() -> str:
        return "Boundary DFS"

    @staticmethod
    def description() -> str:
        return "LeetCode #130: Capture surrounded 'O' regions by flipping to 'X'."

    @staticmethod
    def long_description() -> str:
        return (
            "Given an `m x n` board containing `'X'` and `'O'`, capture all "
            "regions of `'O'` that are completely surrounded by `'X'` by "
            "flipping them to `'X'`. Border-connected `'O'` cells are not captured.\n\n"
            "Example 1:\n"
            "Input: `board = [[X,X,X,X],[X,O,O,X],[X,X,O,X],[X,O,X,X]]`\n"
            "Output: `[[X,X,X,X],[X,X,X,X],[X,X,X,X],[X,O,X,X]]`\n\n"
            "Constraints:\n\n"
            "- `1 <= m, n <= 200`\n"
            "- `board[i][j]` is `'X'` or `'O'`"
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
                ["X", "X", "X", "X", "O", "X", "X"],
                ["X", "O", "O", "X", "O", "O", "X"],
                ["X", "X", "O", "X", "X", "O", "X"],
                ["X", "O", "X", "X", "O", "X", "X"],
                ["X", "O", "O", "O", "X", "O", "O"],
                ["X", "X", "X", "O", "X", "X", "X"],
                ["X", "X", "X", "X", "X", "O", "X"],
            ],
        }

        board = [row[:] for row in grids.get(grid_id, grids[1])]
        m, n = len(board), len(board[0])

        tracer = Board2DTracer(m, n)
        steps: list[Step] = []

        def snap(line: int, desc: str = "") -> None:
            steps.append(tracer.snapshot(line, desc))

        for r in range(m):
            for c in range(n):
                tracer.set_value(r, c, board[r][c])

        tracer.log(f"Board: {m}x{n}")
        snap(2, f"Initialize {m}x{n} board")

        def dfs(r: int, c: int) -> None:
            if r < 0 or r >= m or c < 0 or c >= n:
                return
            if board[r][c] != "O":
                return

            tracer.deselect_all()
            tracer.select(r, c)
            tracer.log(f"Mark ({r},{c}) as safe (border-connected)")
            snap(9, f"Mark ({r},{c}) as safe")

            board[r][c] = "S"
            tracer.set_value(r, c, "S")
            tracer.patch(r, c)
            tracer.deselect(r, c)
            snap(10, f"({r},{c}) = 'S'")

            dfs(r + 1, c)
            dfs(r - 1, c)
            dfs(r, c + 1)
            dfs(r, c - 1)

        tracer.log("Phase 1: Mark border-connected O cells as safe")
        snap(16, "Phase 1: DFS from border O cells")

        for i in range(m):
            dfs(i, 0)
            dfs(i, n - 1)
        for j in range(n):
            dfs(0, j)
            dfs(m - 1, j)

        tracer.deselect_all()
        tracer.log("Phase 2: Capture surrounded regions")
        snap(25, "Phase 2: Flip remaining O -> X, restore S -> O")

        for i in range(m):
            for j in range(n):
                if board[i][j] == "O":
                    board[i][j] = "X"
                    tracer.set_value(i, j, "X")
                    tracer.mark_error(i, j)
                    tracer.log(f"Capture ({i},{j}): O -> X")
                    snap(25, f"Capture ({i},{j}): O -> X")
                    tracer.clear_error(i, j)
                elif board[i][j] == "S":
                    board[i][j] = "O"
                    tracer.set_value(i, j, "O")
                    tracer.depatch(i, j)
                    tracer.log(f"Restore ({i},{j}): S -> O")
                    snap(27, f"Restore ({i},{j}): S -> O")

        tracer.log("Done!")
        snap(27, "All surrounded regions captured")
        return steps
