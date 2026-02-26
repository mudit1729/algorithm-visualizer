from __future__ import annotations

from core.step import Step
from core.tracer import Board2DTracer
from problems.base_problem import Problem

_SOURCE = """\
def solve_n_queens(n):
    board = [[0] * n for _ in range(n)]

    def is_safe(row, col):
        for i in range(row):
            if board[i][col] == 1:
                return False
        i, j = row - 1, col - 1
        while i >= 0 and j >= 0:
            if board[i][j] == 1:
                return False
            i -= 1
            j -= 1
        i, j = row - 1, col + 1
        while i >= 0 and j < n:
            if board[i][j] == 1:
                return False
            i -= 1
            j += 1
        return True

    def backtrack(row):
        if row == n:
            return True
        for col in range(n):
            if is_safe(row, col):
                board[row][col] = 1
                if backtrack(row + 1):
                    return True
                board[row][col] = 0
        return False

    backtrack(0)
    return board"""


class NQueens(Problem):
    @staticmethod
    def name() -> str:
        return "N-Queens"

    @staticmethod
    def topic() -> str:
        return "Backtracking"

    @staticmethod
    def subtopic() -> str:
        return "Constraint Satisfaction"

    @staticmethod
    def description() -> str:
        return "Place N queens on an NxN board so no two queens threaten each other."

    @staticmethod
    def long_description() -> str:
        return (
            "Place `n` queens on an `n x n` chessboard so that no two queens "
            "attack each other. A queen attacks along its row, column, and "
            "both diagonals.\n\n"
            "Example 1:\n"
            "Input: `n = 4`\n"
            "Output: `[[.Q..],[...Q],[Q...],[..Q.]]`\n\n"
            "Constraints:\n\n"
            "- `1 <= n <= 9`"
        )

    @staticmethod
    def source_code() -> str:
        return _SOURCE

    @staticmethod
    def renderer_type() -> str:
        return "board"

    @staticmethod
    def default_params() -> dict[str, object]:
        return {"n": 8}

    @staticmethod
    def theory() -> str:
        return """Approach: Place N queens on an N×N chessboard so no two queens threaten each other. Use backtracking: try placing a queen in each column of the current row, check if it's safe (no conflicts with queens in previous rows), and recurse. If stuck, backtrack and try the next column.

Time Complexity: O(N!) — the first row has N choices, the second has at most N-1, etc.

Space Complexity: O(N) for the board state and recursion stack.

Key Insight: To check safety efficiently, track which columns, main diagonals (row-col), and anti-diagonals (row+col) are occupied. This gives O(1) conflict checking instead of scanning all placed queens.

Interview Tip: N-Queens is THE classic backtracking problem. The optimization of using sets for columns and diagonals is a common follow-up. For N=8, there are 92 solutions."""

    @staticmethod
    def generate_steps(**kwargs: object) -> list[Step]:
        n = int(kwargs.get("n", 8))
        tracer = Board2DTracer(n, n)
        steps: list[Step] = []

        def snap(line: int, desc: str = "") -> None:
            steps.append(tracer.snapshot(line, desc))

        # Line 2: initialize board
        tracer.log(f"Initialize {n}x{n} board")
        snap(2, f"Initialize {n}x{n} board")

        def is_safe(row: int, col: int) -> bool:
            # Check column
            for i in range(row):
                tracer.select(i, col)
                snap(7, f"Check column: row {i}, col {col}")
                if tracer._values[i][col] == 1:
                    tracer.mark_error(i, col)
                    tracer.mark_error(row, col)
                    tracer.log(f"Column conflict at ({i}, {col})")
                    snap(8, f"Column conflict at ({i}, {col})")
                    tracer.clear_all_errors()
                    tracer.deselect(i, col)
                    return False
                tracer.deselect(i, col)

            # Check upper-left diagonal
            i, j = row - 1, col - 1
            while i >= 0 and j >= 0:
                tracer.select(i, j)
                snap(11, f"Check diagonal: ({i}, {j})")
                if tracer._values[i][j] == 1:
                    tracer.mark_error(i, j)
                    tracer.mark_error(row, col)
                    tracer.log(f"Diagonal conflict at ({i}, {j})")
                    snap(12, f"Diagonal conflict at ({i}, {j})")
                    tracer.clear_all_errors()
                    tracer.deselect(i, j)
                    return False
                tracer.deselect(i, j)
                i -= 1
                j -= 1

            # Check upper-right diagonal
            i, j = row - 1, col + 1
            while i >= 0 and j < n:
                tracer.select(i, j)
                snap(16, f"Check diagonal: ({i}, {j})")
                if tracer._values[i][j] == 1:
                    tracer.mark_error(i, j)
                    tracer.mark_error(row, col)
                    tracer.log(f"Diagonal conflict at ({i}, {j})")
                    snap(17, f"Diagonal conflict at ({i}, {j})")
                    tracer.clear_all_errors()
                    tracer.deselect(i, j)
                    return False
                tracer.deselect(i, j)
                i -= 1
                j += 1

            return True

        def backtrack(row: int) -> bool:
            if row == n:
                tracer.log("All queens placed! Solution found.")
                snap(26, "All queens placed! Solution found.")
                return True

            for col in range(n):
                tracer.deselect_all()
                tracer.depatch_all()
                tracer.select(row, col)
                tracer.log(f"Try queen at ({row}, {col})")
                snap(28, f"Try queen at ({row}, {col})")

                if is_safe(row, col):
                    tracer.deselect_all()
                    tracer.set_value(row, col, 1)
                    tracer.patch(row, col)
                    tracer.log(f"Place queen at ({row}, {col})")
                    snap(30, f"Place queen at ({row}, {col})")
                    tracer.depatch(row, col)

                    if backtrack(row + 1):
                        return True

                    # Backtrack
                    tracer.set_value(row, col, 0)
                    tracer.deselect_all()
                    tracer.select(row, col)
                    tracer.log(f"Remove queen from ({row}, {col})")
                    snap(34, f"Backtrack: remove queen from ({row}, {col})")
                    tracer.deselect(row, col)
                else:
                    tracer.deselect_all()

            return False

        backtrack(0)
        return steps
