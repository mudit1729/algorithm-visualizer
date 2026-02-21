from __future__ import annotations

from core.step import Step
from core.tracer import Board2DTracer
from problems.base_problem import Problem

_SOURCE = """\
def exist(board, word):
    m, n = len(board), len(board[0])

    def dfs(r, c, idx):
        if idx == len(word):
            return True
        if r < 0 or r >= m or c < 0 or c >= n:
            return False
        if board[r][c] != word[idx]:
            return False
        tmp = board[r][c]
        board[r][c] = '#'
        found = (dfs(r + 1, c, idx + 1) or
                 dfs(r - 1, c, idx + 1) or
                 dfs(r, c + 1, idx + 1) or
                 dfs(r, c - 1, idx + 1))
        board[r][c] = tmp
        return found

    for i in range(m):
        for j in range(n):
            if dfs(i, j, 0):
                return True
    return False"""

_DIRS = {"down": (1, 0), "up": (-1, 0), "right": (0, 1), "left": (0, -1)}
_DIR_NAMES = {(1, 0): "down", (-1, 0): "up", (0, 1): "right", (0, -1): "left"}


class WordSearch(Problem):
    @staticmethod
    def name() -> str:
        return "Word Search"

    @staticmethod
    def topic() -> str:
        return "Backtracking"

    @staticmethod
    def subtopic() -> str:
        return "Grid Search"

    @staticmethod
    def description() -> str:
        return "LeetCode #79: Search for a word in a 2D grid using DFS backtracking."

    @staticmethod
    def long_description() -> str:
        return (
            "Given an `m x n` grid of characters and a string `word`, return "
            "`true` if `word` exists in the grid. The word can be constructed "
            "from letters of sequentially adjacent cells (horizontally or "
            "vertically). The same cell may not be used more than once.\n\n"
            "Example 1:\n"
            "Input: `board = [[\"A\",\"B\",\"C\",\"E\"],[\"S\",\"F\",\"C\",\"S\"],[\"A\",\"D\",\"E\",\"E\"]]`, "
            "`word = \"ABCCED\"`\n"
            "Output: `true`\n\n"
            "Constraints:\n\n"
            "- `1 <= m, n <= 6`\n"
            "- `1 <= word.length <= 15`\n"
            "- `board` and `word` consist of only lowercase and uppercase English letters"
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
            1: (
                [
                    ["A", "L", "G", "O", "R", "I", "T"],
                    ["S", "E", "A", "R", "C", "H", "H"],
                    ["B", "A", "C", "K", "T", "R", "M"],
                    ["D", "F", "G", "H", "I", "A", "J"],
                    ["K", "L", "M", "N", "O", "C", "P"],
                    ["Q", "R", "S", "T", "U", "K", "V"],
                    ["W", "X", "Y", "Z", "A", "B", "C"],
                ],
                "SEARCH",
            ),
        }

        board_data, word = grids.get(grid_id, grids[1])
        board = [row[:] for row in board_data]
        m, n = len(board), len(board[0])

        tracer = Board2DTracer(m, n)
        steps: list[Step] = []

        def snap(line: int, desc: str = "") -> None:
            steps.append(tracer.snapshot(line, desc))

        # Initialize the board display
        for r in range(m):
            for c in range(n):
                tracer.set_value(r, c, board[r][c])

        tracer.log(f"Board: {m}x{n}, word = \"{word}\"")
        snap(2, f"Search for \"{word}\" in {m}x{n} grid")

        found_path: list[tuple[int, int]] = []
        search_done = False

        def dfs(r: int, c: int, idx: int) -> bool:
            nonlocal search_done

            if search_done:
                return True

            # Check: found entire word
            if idx == len(word):
                return True

            # Check: out of bounds
            if r < 0 or r >= m or c < 0 or c >= n:
                return False

            # Check: character mismatch
            if board[r][c] != word[idx]:
                tracer.deselect_all()
                tracer.select(r, c)
                tracer.mark_error(r, c)
                tracer.log(f"  ({r},{c})='{board[r][c]}' != '{word[idx]}' - mismatch")
                snap(8, f"({r},{c})='{board[r][c]}' != '{word[idx]}' - mismatch")
                tracer.clear_error(r, c)
                tracer.deselect(r, c)
                return False

            # Match at this cell
            tracer.deselect_all()
            tracer.select(r, c)
            tracer.mark_on_path(r, c)
            tracer.set_overlay(r, c, str(idx), color="#22c55e")
            found_path.append((r, c))
            tracer.log(f"Match '{word[idx]}' at ({r},{c}), idx={idx}")
            snap(10, f"Match '{word[idx]}' at ({r},{c}), char {idx + 1}/{len(word)}")

            # Mark cell as used
            tmp = board[r][c]
            board[r][c] = '#'
            tracer.set_value(r, c, '#')
            snap(11, f"Mark ({r},{c}) as visited")

            # Try all 4 directions
            for dr, dc in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                nr, nc = r + dr, c + dc
                dir_name = _DIR_NAMES[(dr, dc)]

                if 0 <= nr < m and 0 <= nc < n and board[nr][nc] != '#':
                    tracer.set_arrow(r, c, dir_name)
                    snap(12, f"Try {dir_name} from ({r},{c})")

                if dfs(nr, nc, idx + 1):
                    search_done = True
                    return True

            # Backtrack
            board[r][c] = tmp
            tracer.set_value(r, c, tmp)
            tracer.clear_on_path(r, c)
            tracer.set_overlay(r, c, "")
            tracer.set_arrow(r, c, "")
            found_path.pop()
            tracer.mark_error(r, c)
            tracer.log(f"Backtrack from ({r},{c})")
            snap(14, f"Backtrack from ({r},{c})")
            tracer.clear_error(r, c)
            return False

        # Try each cell as starting point
        result = False
        for i in range(m):
            for j in range(n):
                if search_done:
                    break
                if board[i][j] == word[0]:
                    tracer.deselect_all()
                    tracer.clear_all_paths()
                    tracer.clear_all_overlays()
                    tracer.log(f"Try starting at ({i},{j})")
                    snap(18, f"Try starting search at ({i},{j})")
                    if dfs(i, j, 0):
                        result = True
                        break
            if search_done:
                break

        tracer.deselect_all()
        if result:
            # Highlight the found path
            for idx, (r, c) in enumerate(found_path):
                tracer.mark_on_path(r, c)
                tracer.patch(r, c)
                tracer.set_overlay(r, c, str(idx), color="#22c55e")
                if idx < len(found_path) - 1:
                    nr, nc = found_path[idx + 1]
                    dr, dc = nr - r, nc - c
                    tracer.set_arrow(r, c, _DIR_NAMES.get((dr, dc), ""))
            tracer.log(f"Word \"{word}\" found!")
            snap(20, f"Word \"{word}\" found!")
        else:
            tracer.log(f"Word \"{word}\" not found")
            snap(21, f"Word \"{word}\" not found in grid")

        return steps
