from __future__ import annotations

from core.step import Step
from core.tracer import Board2DTracer
from problems.base_problem import Problem

_SOURCE = """\
def floodFill(image, sr, sc, color):
    orig = image[sr][sc]
    if orig == color:
        return image
    m, n = len(image), len(image[0])

    def dfs(r, c):
        if r < 0 or r >= m or c < 0 or c >= n:
            return
        if image[r][c] != orig:
            return
        image[r][c] = color
        dfs(r + 1, c)
        dfs(r - 1, c)
        dfs(r, c + 1)
        dfs(r, c - 1)

    dfs(sr, sc)
    return image"""


class FloodFill(Problem):
    @staticmethod
    def name() -> str:
        return "Flood Fill"

    @staticmethod
    def topic() -> str:
        return "Graph / DFS"

    @staticmethod
    def subtopic() -> str:
        return "Flood Fill"

    @staticmethod
    def description() -> str:
        return "LeetCode #733: Fill connected region from a starting pixel with a new color."

    @staticmethod
    def long_description() -> str:
        return (
            "Given an image as an `m x n` grid, a starting pixel `(sr, sc)`, "
            "and a new `color`, flood fill the image. Change the starting pixel "
            "and all 4-directionally connected pixels of the same original color "
            "to the new color.\n\n"
            "Example 1:\n"
            "Input: `image = [[1,1,1],[1,1,0],[1,0,1]]`, `sr = 1`, `sc = 1`, `color = 2`\n"
            "Output: `[[2,2,2],[2,2,0],[2,0,1]]`\n\n"
            "Constraints:\n\n"
            "- `1 <= m, n <= 50`\n"
            "- `0 <= image[i][j], color < 2^16`\n"
            "- `0 <= sr < m`, `0 <= sc < n`"
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
        return """Approach: Starting from a given pixel, change its color and all connected pixels of the same original color to the new color using DFS or BFS. Connected means 4-directionally adjacent (up, down, left, right).

Time Complexity: O(M × N) where M and N are image dimensions — in the worst case, every pixel is the same color.

Space Complexity: O(M × N) for the recursion stack (DFS) or queue (BFS).

Key Insight: This is the algorithm behind the "paint bucket" tool in image editors. DFS is the simplest implementation — recursively fill each valid neighbor.

Interview Tip: Handle the edge case where newColor equals the original color to avoid infinite recursion. Either check upfront and return immediately, or use a visited set."""

    @staticmethod
    def generate_steps(**kwargs: object) -> list[Step]:
        grid_id = int(kwargs.get("grid", 1))

        grids = {
            1: [
                [1, 1, 1, 0, 0, 1, 1],
                [1, 1, 1, 0, 0, 0, 1],
                [1, 1, 0, 0, 1, 1, 1],
                [0, 0, 0, 1, 1, 1, 0],
                [1, 1, 0, 1, 1, 0, 0],
                [1, 1, 1, 1, 0, 0, 1],
                [1, 0, 1, 1, 1, 1, 1],
            ],
        }

        image = [row[:] for row in grids.get(grid_id, grids[1])]
        sr, sc, new_color = 0, 0, 2
        orig = image[sr][sc]
        m, n = len(image), len(image[0])

        tracer = Board2DTracer(m, n)
        steps: list[Step] = []

        def snap(line: int, desc: str = "") -> None:
            steps.append(tracer.snapshot(line, desc))

        # Initialize board with string values for grid renderer
        for r in range(m):
            for c in range(n):
                tracer.set_value(r, c, str(image[r][c]))

        tracer.log(f"Grid: {m}x{n}, start=({sr},{sc}), orig={orig}, new={new_color}")
        snap(2, f"Original color at ({sr},{sc}) = {orig}")

        if orig == new_color:
            tracer.log("Original == new color, nothing to do")
            snap(4, "No-op: same color")
            return steps

        def dfs(r: int, c: int) -> None:
            if r < 0 or r >= m or c < 0 or c >= n:
                return
            if image[r][c] != orig:
                tracer.log(f"  Skip ({r},{c}): not original color")
                return

            tracer.deselect_all()
            tracer.select(r, c)
            tracer.log(f"Visit ({r},{c})")
            snap(12, f"Visit ({r},{c})")

            image[r][c] = new_color
            tracer.set_value(r, c, str(new_color))
            tracer.patch(r, c)
            tracer.deselect(r, c)
            tracer.log(f"  Fill ({r},{c}) -> {new_color}")
            snap(13, f"Fill ({r},{c}) with color {new_color}")

            dfs(r + 1, c)
            dfs(r - 1, c)
            dfs(r, c + 1)
            dfs(r, c - 1)

        dfs(sr, sc)

        tracer.deselect_all()
        tracer.log("Flood fill complete!")
        snap(19, "Flood fill complete!")
        return steps
