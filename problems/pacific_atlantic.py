from __future__ import annotations

from collections import deque

from core.step import Step
from core.tracer import Board2DTracer
from problems.base_problem import Problem

_SOURCE = """\
def pacificAtlantic(heights):
    m, n = len(heights), len(heights[0])
    pacific = set()
    atlantic = set()

    def bfs(starts, reachable):
        queue = deque(starts)
        reachable.update(starts)
        while queue:
            r, c = queue.popleft()
            for dr, dc in [(1,0),(-1,0),(0,1),(0,-1)]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < m and 0 <= nc < n:
                    if (nr, nc) not in reachable:
                        if heights[nr][nc] >= heights[r][c]:
                            reachable.add((nr, nc))
                            queue.append((nr, nc))

    pac_starts = ([(0, j) for j in range(n)] +
                  [(i, 0) for i in range(1, m)])
    atl_starts = ([(m-1, j) for j in range(n)] +
                  [(i, n-1) for i in range(m-1)])

    bfs(pac_starts, pacific)
    bfs(atl_starts, atlantic)

    return [[r, c] for r, c in pacific & atlantic]"""


class PacificAtlantic(Problem):
    @staticmethod
    def name() -> str:
        return "Pacific Atlantic Water Flow"

    @staticmethod
    def topic() -> str:
        return "Graph / BFS"

    @staticmethod
    def subtopic() -> str:
        return "Multi-Source BFS"

    @staticmethod
    def description() -> str:
        return "LeetCode #417: Find cells that can reach both Pacific and Atlantic oceans."

    @staticmethod
    def long_description() -> str:
        return (
            "Given an `m x n` island with heights, the Pacific ocean touches "
            "the top and left edges, and the Atlantic ocean touches the bottom "
            "and right edges. Water flows from higher or equal height cells to "
            "lower ones. Find all cells from which water can flow to both "
            "oceans.\n\n"
            "Example 1:\n"
            "Input: `heights = [[1,2,2,3,5],[3,2,3,4,4],[2,4,5,3,1],[6,7,1,4,5],[5,1,1,2,4]]`\n"
            "Output: `[[0,4],[1,3],[1,4],[2,2],[3,0],[3,1],[4,0]]`\n\n"
            "Constraints:\n\n"
            "- `1 <= m, n <= 200`\n"
            "- `0 <= heights[r][c] <= 10^5`"
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
                [1, 2, 2, 3, 5, 4, 2],
                [3, 2, 3, 4, 4, 3, 1],
                [2, 4, 5, 3, 1, 2, 3],
                [6, 7, 1, 4, 5, 6, 4],
                [5, 1, 1, 2, 4, 7, 2],
                [4, 3, 6, 3, 1, 3, 5],
                [3, 5, 4, 7, 2, 4, 6],
            ],
        }

        heights = [row[:] for row in grids.get(grid_id, grids[1])]
        m, n = len(heights), len(heights[0])

        tracer = Board2DTracer(m, n)
        steps: list[Step] = []

        def snap(line: int, desc: str = "") -> None:
            steps.append(tracer.snapshot(line, desc))

        # Initialize grid with height values
        for r in range(m):
            for c in range(n):
                tracer.set_value(r, c, str(heights[r][c]))

        tracer.log(f"Heights: {m}x{n}. Pacific=top+left, Atlantic=bottom+right")
        snap(2, f"{m}x{n} island heights grid")

        # --- Phase 1: BFS from Pacific ---
        pacific: set[tuple[int, int]] = set()
        pac_starts: list[tuple[int, int]] = (
            [(0, j) for j in range(n)] +
            [(i, 0) for i in range(1, m)]
        )

        # Mark Pacific border cells
        for r, c in pac_starts:
            pacific.add((r, c))
            tracer.set_overlay(r, c, "P", color="#3b82f6")
            tracer.select(r, c)

        tracer.log(f"Pacific border: {len(pac_starts)} cells")
        snap(16, f"Pacific border cells ({len(pac_starts)} sources)")

        queue: deque[tuple[int, int]] = deque(pac_starts)
        while queue:
            r, c = queue.popleft()
            tracer.deselect_all()
            tracer.select(r, c)
            snap(8, f"Pacific BFS: process ({r},{c}) h={heights[r][c]}")

            for dr, dc in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < m and 0 <= nc < n:
                    if (nr, nc) not in pacific:
                        if heights[nr][nc] >= heights[r][c]:
                            pacific.add((nr, nc))
                            queue.append((nr, nc))
                            tracer.set_overlay(nr, nc, "P", color="#3b82f6")
                            tracer.log(f"  Pacific reaches ({nr},{nc}) h={heights[nr][nc]}")
                            snap(14, f"Pacific reaches ({nr},{nc})")

        tracer.deselect_all()
        tracer.log(f"Pacific can reach {len(pacific)} cells")
        snap(19, f"Pacific reachable: {len(pacific)} cells")

        # --- Phase 2: BFS from Atlantic ---
        atlantic: set[tuple[int, int]] = set()
        atl_starts: list[tuple[int, int]] = (
            [(m - 1, j) for j in range(n)] +
            [(i, n - 1) for i in range(m - 1)]
        )

        # Mark Atlantic border cells
        for r, c in atl_starts:
            atlantic.add((r, c))
            if (r, c) in pacific:
                tracer.set_overlay(r, c, "B", color="#a855f7")
            else:
                tracer.set_overlay(r, c, "A", color="#ef4444")
            tracer.select(r, c)

        tracer.log(f"Atlantic border: {len(atl_starts)} cells")
        snap(18, f"Atlantic border cells ({len(atl_starts)} sources)")

        queue = deque(atl_starts)
        while queue:
            r, c = queue.popleft()
            tracer.deselect_all()
            tracer.select(r, c)
            snap(8, f"Atlantic BFS: process ({r},{c}) h={heights[r][c]}")

            for dr, dc in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < m and 0 <= nc < n:
                    if (nr, nc) not in atlantic:
                        if heights[nr][nc] >= heights[r][c]:
                            atlantic.add((nr, nc))
                            queue.append((nr, nc))
                            if (nr, nc) in pacific:
                                tracer.set_overlay(nr, nc, "B", color="#a855f7")
                            else:
                                tracer.set_overlay(nr, nc, "A", color="#ef4444")
                            tracer.log(f"  Atlantic reaches ({nr},{nc}) h={heights[nr][nc]}")
                            snap(14, f"Atlantic reaches ({nr},{nc})")

        tracer.deselect_all()
        tracer.log(f"Atlantic can reach {len(atlantic)} cells")
        snap(21, f"Atlantic reachable: {len(atlantic)} cells")

        # --- Phase 3: Find intersection ---
        both = pacific & atlantic
        for r, c in sorted(both):
            tracer.set_overlay(r, c, "B", color="#a855f7")
            tracer.patch(r, c)

        tracer.log(f"Cells reaching both oceans: {len(both)}")
        snap(23, f"Result: {len(both)} cells reach both oceans")

        return steps
