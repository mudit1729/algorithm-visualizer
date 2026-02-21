from __future__ import annotations

from core.step import Step
from core.tracer import Board2DTracer
from problems.base_problem import Problem

_SOURCE = """\
class TrieNode:
    def __init__(self):
        self.children = {}
        self.word = None

def findWords(board, words):
    root = TrieNode()
    for w in words:
        node = root
        for ch in w:
            if ch not in node.children:
                node.children[ch] = TrieNode()
            node = node.children[ch]
        node.word = w

    m, n = len(board), len(board[0])
    found = []

    def dfs(r, c, node):
        ch = board[r][c]
        if ch not in node.children:
            return
        child = node.children[ch]
        if child.word:
            found.append(child.word)
            child.word = None

        board[r][c] = '#'
        for dr, dc in [(0,1),(0,-1),(1,0),(-1,0)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < m and 0 <= nc < n:
                if board[nr][nc] != '#':
                    dfs(nr, nc, child)
        board[r][c] = ch

    for i in range(m):
        for j in range(n):
            dfs(i, j, root)
    return found"""

_DIR_NAMES = {(0, 1): "right", (0, -1): "left", (1, 0): "down", (-1, 0): "up"}


class WordSearchII(Problem):
    @staticmethod
    def name() -> str:
        return "Word Search II"

    @staticmethod
    def topic() -> str:
        return "Trie"

    @staticmethod
    def subtopic() -> str:
        return "Grid + Trie"

    @staticmethod
    def description() -> str:
        return "LeetCode #212: Find all words from a dictionary that exist in a 2D board."

    @staticmethod
    def long_description() -> str:
        return (
            "Given an `m x n` board of characters and a list of strings `words`, "
            "return all words on the board. Each word must be constructed from "
            "letters of sequentially adjacent cells, where adjacent cells are "
            "horizontally or vertically neighboring. The same letter cell may not "
            "be used more than once in a word.\n\n"
            "A Trie is built from the word list to efficiently prune the DFS "
            "search on the grid.\n\n"
            "Example:\n"
            "Input: `board = [[\"o\",\"a\",\"a\",\"n\"],[\"e\",\"t\",\"a\",\"e\"]]`, "
            "`words = [\"oath\",\"pea\",\"eat\",\"rain\"]`\n"
            "Output: `[\"eat\",\"oath\"]`\n\n"
            "Constraints:\n\n"
            "- `m, n <= 12`\n"
            "- `1 <= words.length <= 3 * 10^4`\n"
            "- `words[i]` consists of lowercase English letters"
        )

    @staticmethod
    def source_code() -> str:
        return _SOURCE

    @staticmethod
    def renderer_type() -> str:
        return "board"

    @staticmethod
    def default_params() -> dict[str, object]:
        return {"preset": 1}

    @staticmethod
    def generate_steps(**kwargs: object) -> list[Step]:
        preset = int(kwargs.get("preset", 1))

        presets = {
            1: {
                "board": [
                    ["o", "a", "t", "h", "e"],
                    ["e", "t", "a", "e", "r"],
                    ["p", "e", "a", "i", "n"],
                    ["r", "a", "i", "n", "s"],
                    ["b", "a", "l", "l", "s"],
                ],
                "words": ["oath", "pea", "eat", "rain", "oat"],
            },
        }

        data = presets.get(preset, presets[1])
        board_data = data["board"]
        words = data["words"]
        m = len(board_data)
        n = len(board_data[0])
        board = [row[:] for row in board_data]

        tracer = Board2DTracer(m, n)
        steps: list[Step] = []

        def snap(line: int, desc: str = "") -> None:
            steps.append(tracer.snapshot(line, desc))

        # Initialize board display
        for r in range(m):
            for c in range(n):
                tracer.set_value(r, c, board[r][c])

        tracer.log(f"Board: {m}x{n}, Words: {words}")
        snap(1, f"{m}x{n} board, find words: {words}")

        # =============================================
        # PHASE 1: BUILD TRIE (shown in logs only)
        # =============================================
        tracer.log("--- Build Trie from word list ---")

        # Internal trie structure
        trie_children: dict[int, dict[str, int]] = {}
        trie_word: dict[int, str | None] = {}
        next_id = 0

        def new_trie_node() -> int:
            nonlocal next_id
            nid = next_id
            next_id += 1
            trie_children[nid] = {}
            trie_word[nid] = None
            return nid

        root = new_trie_node()

        for w in words:
            node = root
            for ch in w:
                if ch not in trie_children[node]:
                    trie_children[node][ch] = new_trie_node()
                node = trie_children[node][ch]
            trie_word[node] = w
            tracer.log(f"  Inserted \"{w}\" into trie")

        snap(13, "Trie built from word list")

        # =============================================
        # PHASE 2: DFS SEARCH ON BOARD
        # =============================================
        tracer.log("--- DFS search using Trie ---")
        snap(16, "Begin DFS from each cell")

        found: list[str] = []
        cells_explored = 0
        max_explore = 80  # limit to keep step count reasonable

        def dfs(r: int, c: int, trie_node: int, path: list[tuple[int, int]]) -> None:
            nonlocal cells_explored
            if cells_explored > max_explore:
                return

            ch = board[r][c]
            if ch not in trie_children.get(trie_node, {}):
                return

            child = trie_children[trie_node][ch]
            cells_explored += 1

            # Select current cell
            tracer.select(r, c)
            tracer.set_overlay(r, c, ch.upper(), color="#60a5fa")
            path.append((r, c))

            # Show current path
            for pr, pc in path[:-1]:
                tracer.select(pr, pc)

            tracer.log(f"  Explore ({r},{c})='{ch}'")
            snap(22, f"Explore ({r},{c})='{ch}'")

            # Check if we found a word
            if trie_word[child] is not None:
                word_found = trie_word[child]
                found.append(word_found)
                trie_word[child] = None  # prevent duplicates

                # Mark the entire word path on the board
                for pr, pc in path:
                    tracer.mark_on_path(pr, pc)
                    tracer.patch(pr, pc)
                tracer.log(f"  FOUND \"{word_found}\"!")
                snap(25, f"Found word \"{word_found}\"!")

                # Clear path markers (keep patched)
                for pr, pc in path:
                    tracer.clear_on_path(pr, pc)
                    tracer.depatch(pr, pc)

            # Mark cell as visited
            saved = board[r][c]
            board[r][c] = '#'
            tracer.set_value(r, c, '#')

            # Explore neighbors
            for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < m and 0 <= nc < n and board[nr][nc] != '#':
                    dir_name = _DIR_NAMES[(dr, dc)]
                    tracer.set_arrow(r, c, dir_name)
                    dfs(nr, nc, child, path)
                    tracer.set_arrow(r, c, "")
                    if cells_explored > max_explore:
                        break

            # Backtrack
            board[r][c] = saved
            tracer.set_value(r, c, saved)
            tracer.deselect(r, c)
            tracer.set_overlay(r, c, "")
            path.pop()

            # Restore selection for remaining path
            tracer.deselect_all()
            for pr, pc in path:
                tracer.select(pr, pc)

            snap(34, f"Backtrack from ({r},{c})")

        # Try each cell as a starting point
        for i in range(m):
            for j in range(n):
                if cells_explored > max_explore:
                    break
                if board[i][j] in trie_children.get(root, {}):
                    tracer.deselect_all()
                    tracer.clear_all_overlays()
                    tracer.log(f"Start DFS at ({i},{j})='{board[i][j]}'")
                    snap(38, f"Start DFS at ({i},{j})='{board[i][j]}'")
                    dfs(i, j, root, [])
            if cells_explored > max_explore:
                break

        # =============================================
        # FINAL: Show results
        # =============================================
        tracer.deselect_all()
        tracer.clear_all_overlays()
        tracer.clear_all_errors()
        tracer.clear_all_paths()

        # Highlight found words by re-tracing their paths in the original board
        # Reset board display to original
        for r in range(m):
            for c in range(n):
                tracer.set_value(r, c, board_data[r][c])

        if found:
            tracer.log(f"Found words: {found}")
            # Highlight cells of all found words
            for word_found in found:
                path = _find_word_path(board_data, word_found)
                if path:
                    for pr, pc in path:
                        tracer.patch(pr, pc)
                        tracer.mark_on_path(pr, pc)
            snap(39, f"Result: found {found}")
        else:
            tracer.log("No words found")
            snap(36, "No words found")

        return steps


def _find_word_path(
    board: list[list[str]], word: str
) -> list[tuple[int, int]] | None:
    """Find a path for the word in the board (for final highlight)."""
    m, n = len(board), len(board[0])
    visited = [[False] * n for _ in range(m)]

    def dfs(r: int, c: int, idx: int, path: list[tuple[int, int]]) -> bool:
        if idx == len(word):
            return True
        if r < 0 or r >= m or c < 0 or c >= n:
            return False
        if visited[r][c] or board[r][c] != word[idx]:
            return False
        visited[r][c] = True
        path.append((r, c))
        for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            if dfs(r + dr, c + dc, idx + 1, path):
                return True
        path.pop()
        visited[r][c] = False
        return False

    for i in range(m):
        for j in range(n):
            path: list[tuple[int, int]] = []
            if dfs(i, j, 0, path):
                return path
    return None
