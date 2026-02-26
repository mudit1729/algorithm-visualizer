from __future__ import annotations

from collections import deque

from core.step import Step
from core.tracer import Board2DTracer
from problems.base_problem import Problem

_SOURCE = """\
def updateMatrix(mat):
    m, n = len(mat), len(mat[0])
    dist = [[float('inf')] * n for _ in range(m)]
    queue = deque()

    for i in range(m):
        for j in range(n):
            if mat[i][j] == 0:
                dist[i][j] = 0
                queue.append((i, j))

    while queue:
        r, c = queue.popleft()
        for dr, dc in [(1,0),(-1,0),(0,1),(0,-1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < m and 0 <= nc < n:
                if dist[nr][nc] > dist[r][c] + 1:
                    dist[nr][nc] = dist[r][c] + 1
                    queue.append((nr, nc))

    return dist"""


class ZeroOneMatrix(Problem):
    @staticmethod
    def name() -> str:
        return "01 Matrix"

    @staticmethod
    def topic() -> str:
        return "Graph / BFS"

    @staticmethod
    def subtopic() -> str:
        return "Multi-Source BFS"

    @staticmethod
    def description() -> str:
        return "LeetCode #542: Find distance of each cell to nearest 0 using multi-source BFS."

    @staticmethod
    def long_description() -> str:
        return (
            "Given an `m x n` binary matrix `mat`, return the distance of the "
            "nearest `0` for each cell. The distance between two adjacent cells "
            "is `1`.\n\n"
            "Example 1:\n"
            "Input: `mat = [[0,0,0],[0,1,0],[0,0,0]]`\n"
            "Output: `[[0,0,0],[0,1,0],[0,0,0]]`\n\n"
            "Example 2:\n"
            "Input: `mat = [[0,0,0],[0,1,0],[1,1,1]]`\n"
            "Output: `[[0,0,0],[0,1,0],[1,2,1]]`\n\n"
            "Constraints:\n\n"
            "- `1 <= m, n <= 10^4`\n"
            "- `1 <= m * n <= 10^4`\n"
            "- `mat[i][j]` is either `0` or `1`"
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
        return """Approach: Find the distance of each cell to the nearest 0 in a binary matrix. Use multi-source BFS: start from all 0-cells simultaneously and expand outward. Each cell's distance is set when first reached by the BFS wavefront.

Time Complexity: O(M × N) — each cell visited exactly once.

Space Complexity: O(M × N) for the queue and result matrix.

Key Insight: This is the same multi-source BFS pattern as Walls and Gates and Rotting Oranges. Starting from all 0's simultaneously gives the correct distance for every 1-cell in a single pass.

Interview Tip: DP also works (two passes: top-left to bottom-right, then bottom-right to top-left), but multi-source BFS is cleaner and demonstrates BFS mastery."""

    @staticmethod
    def generate_steps(**kwargs: object) -> list[Step]:
        grid_id = int(kwargs.get("grid", 1))

        grids = {
            1: [
                [1, 1, 1, 0, 1, 1, 1],
                [1, 1, 0, 1, 1, 1, 1],
                [1, 1, 1, 1, 1, 0, 1],
                [0, 1, 1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1, 1, 0],
                [1, 1, 1, 0, 1, 1, 1],
                [1, 0, 1, 1, 1, 1, 1],
            ],
        }

        mat = [row[:] for row in grids.get(grid_id, grids[1])]
        m, n = len(mat), len(mat[0])
        INF = float("inf")
        dist = [[INF] * n for _ in range(m)]

        tracer = Board2DTracer(m, n)
        steps: list[Step] = []

        def snap(line: int, desc: str = "") -> None:
            steps.append(tracer.snapshot(line, desc))

        # Initialize display
        for r in range(m):
            for c in range(n):
                tracer.set_value(r, c, str(mat[r][c]))

        tracer.log(f"Matrix: {m}x{n} binary. Find distance to nearest 0.")
        snap(2, f"Initialize {m}x{n} binary matrix")

        # Enqueue all zero cells
        queue: deque[tuple[int, int]] = deque()
        zero_count = 0
        for i in range(m):
            for j in range(n):
                if mat[i][j] == 0:
                    dist[i][j] = 0
                    queue.append((i, j))
                    tracer.set_overlay(i, j, "0", color="#22c55e")
                    tracer.patch(i, j)
                    zero_count += 1

        tracer.log(f"Found {zero_count} zero cells as BFS sources")
        snap(10, f"{zero_count} zero cells enqueued (dist=0)")

        # BFS: expand level by level
        level = 0
        while queue:
            # Process all cells in the current BFS level at once
            level_size = len(queue)
            level_cells: list[tuple[int, int]] = []

            for _ in range(level_size):
                r, c = queue.popleft()

                tracer.deselect_all()
                tracer.select(r, c)
                snap(14, f"Process ({r},{c}), dist={dist[r][c]}")

                for dr, dc in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < m and 0 <= nc < n:
                        if dist[nr][nc] > dist[r][c] + 1:
                            dist[nr][nc] = dist[r][c] + 1
                            queue.append((nr, nc))
                            level_cells.append((nr, nc))

                            tracer.select(nr, nc)
                            tracer.set_overlay(
                                nr, nc, str(dist[nr][nc]), color="#3b82f6"
                            )
                            tracer.log(
                                f"  ({nr},{nc}) dist = {dist[nr][nc]}"
                            )
                            snap(
                                19,
                                f"({nr},{nc}) distance = {dist[nr][nc]}",
                            )

            # Patch all cells finalized in this level
            for cr, cc in level_cells:
                tracer.patch(cr, cc)
                tracer.set_overlay(cr, cc, str(dist[cr][cc]), color="#22c55e")

            if level_cells:
                tracer.deselect_all()
                snap(21, f"Level {dist[level_cells[0][0]][level_cells[0][1]]} complete: {len(level_cells)} cells")

        # Final summary
        tracer.deselect_all()
        max_dist = 0
        for r in range(m):
            for c in range(n):
                if dist[r][c] != INF and dist[r][c] > max_dist:
                    max_dist = int(dist[r][c])

        tracer.log(f"All distances computed. Max distance = {max_dist}")
        snap(21, f"Complete. Max distance to nearest 0 = {max_dist}")

        return steps
