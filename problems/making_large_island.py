from __future__ import annotations

from core.step import Step
from core.tracer import Board2DTracer
from problems.base_problem import Problem

_SOURCE = """\
def largestIsland(grid):
    n = len(grid)
    parent = list(range(n * n))
    rank = [0] * (n * n)
    size = [1] * (n * n)

    def find(x):
        if parent[x] != x:
            parent[x] = find(parent[x])
        return parent[x]

    def union(x, y):
        rx, ry = find(x), find(y)
        if rx == ry:
            return
        if rank[rx] < rank[ry]:
            rx, ry = ry, rx
        parent[ry] = rx
        size[rx] += size[ry]
        if rank[rx] == rank[ry]:
            rank[rx] += 1

    for r in range(n):
        for c in range(n):
            if grid[r][c] == 1:
                for dr, dc in [(0,1),(1,0)]:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < n and 0 <= nc < n:
                        if grid[nr][nc] == 1:
                            union(r*n+c, nr*n+nc)

    best = max(size[find(r*n+c)]
               for r in range(n) for c in range(n)
               if grid[r][c] == 1) if any(
               grid[r][c] for r in range(n)
               for c in range(n)) else 0

    for r in range(n):
        for c in range(n):
            if grid[r][c] == 0:
                seen = set()
                total = 1
                for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < n and 0 <= nc < n:
                        if grid[nr][nc] == 1:
                            root = find(nr*n+nc)
                            if root not in seen:
                                seen.add(root)
                                total += size[root]
                best = max(best, total)

    return best"""


class MakingLargeIsland(Problem):
    @staticmethod
    def name() -> str:
        return "Making A Large Island"

    @staticmethod
    def topic() -> str:
        return "Union Find"

    @staticmethod
    def subtopic() -> str:
        return "Grid Union Find"

    @staticmethod
    def description() -> str:
        return "LeetCode #827: Find the largest island after flipping at most one 0 to 1."

    @staticmethod
    def long_description() -> str:
        return (
            "Given an `n x n` binary grid, return the size of the largest island "
            "after changing at most one `0` to `1`. An island is a 4-directionally "
            "connected group of `1`s.\n\n"
            "Algorithm:\n"
            "1. Use Union-Find to label all islands and track their sizes.\n"
            "2. For each `0` cell, check adjacent islands and compute the "
            "potential size if this cell were flipped to `1`.\n\n"
            "Example:\n"
            "Input: `grid = [[1,0],[0,1]]`\n"
            "Output: `3`\n\n"
            "Constraints:\n\n"
            "- `1 <= n <= 500`\n"
            "- `grid[i][j]` is `0` or `1`"
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
    def theory() -> str:
        return """Approach: Find the largest island achievable by changing at most one 0 to 1. First, label each island with a unique ID and compute its size using DFS/BFS. Then, for each 0-cell, check its 4 neighbors' island IDs, sum the distinct island sizes + 1, and track the maximum.

Time Complexity: O(M × N) — two passes over the grid.

Space Complexity: O(M × N) for island labels and size mapping.

Key Insight: Two-pass approach: (1) label all islands and record sizes, (2) for each water cell, check which distinct islands are adjacent and sum their sizes. Using island IDs prevents double-counting when the same island borders a cell from multiple directions.

Interview Tip: The edge case where the entire grid is land (no 0 to flip) must be handled — return M×N. The dedup using island IDs (not just sizes) is the common mistake interviewers watch for."""

    @staticmethod
    def generate_steps(**kwargs: object) -> list[Step]:
        preset = int(kwargs.get("preset", 1))

        presets = {
            1: [
                [1, 1, 0, 0, 1, 1, 0],
                [1, 1, 0, 0, 1, 1, 0],
                [0, 0, 0, 0, 0, 0, 0],
                [0, 0, 1, 1, 1, 0, 0],
                [0, 0, 1, 1, 1, 0, 1],
                [0, 0, 0, 0, 0, 0, 1],
                [1, 1, 0, 0, 0, 1, 1],
            ],
        }

        grid = [row[:] for row in presets.get(preset, presets[1])]
        n = len(grid)
        total = n * n

        parent = list(range(total))
        rank = [0] * total
        size = [1] * total

        board = Board2DTracer(n, n)
        steps: list[Step] = []

        # Island colors for visual distinction
        island_colors = [
            "#89b4fa", "#a6e3a1", "#fab387", "#cba6f7",
            "#f38ba8", "#89dceb", "#f9e2af", "#b4befe",
        ]

        def snap(line: int, desc: str = "") -> None:
            steps.append(board.snapshot(line, desc))

        def find(x: int) -> int:
            if parent[x] != x:
                parent[x] = find(parent[x])
            return parent[x]

        def union(x: int, y: int) -> None:
            rx, ry = find(x), find(y)
            if rx == ry:
                return
            if rank[rx] < rank[ry]:
                rx, ry = ry, rx
            parent[ry] = rx
            size[rx] += size[ry]
            if rank[rx] == rank[ry]:
                rank[rx] += 1

        # Initialize board
        for r in range(n):
            for c in range(n):
                board.set_value(r, c, str(grid[r][c]))

        board.log(f"Grid: {n}x{n} binary grid")
        snap(1, f"{n}x{n} grid, find largest island after one flip")

        # Phase 1: Union all adjacent 1-cells
        board.log("Phase 1: Build islands with Union-Find")
        snap(24, "Phase 1: union adjacent land cells")

        for r in range(n):
            for c in range(n):
                if grid[r][c] == 1:
                    for dr, dc in [(0, 1), (1, 0)]:
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < n and 0 <= nc < n and grid[nr][nc] == 1:
                            union(r * n + c, nr * n + nc)

        # Color islands by their root and show sizes
        root_to_color: dict[int, str] = {}
        color_idx = 0
        for r in range(n):
            for c in range(n):
                if grid[r][c] == 1:
                    root = find(r * n + c)
                    if root not in root_to_color:
                        root_to_color[root] = island_colors[color_idx % len(island_colors)]
                        color_idx += 1
                    board.patch(r, c)
                    board.set_overlay(r, c, "", root_to_color[root])

        # Label each island cell with its island size
        for r in range(n):
            for c in range(n):
                if grid[r][c] == 1:
                    root = find(r * n + c)
                    island_size = size[root]
                    board.set_value(r, c, str(island_size))

        island_count = len(root_to_color)
        board.log(f"Found {island_count} islands")
        snap(53, f"Phase 1 done: {island_count} islands identified")

        # Compute initial best (largest existing island)
        best = 0
        for r in range(n):
            for c in range(n):
                if grid[r][c] == 1:
                    best = max(best, size[find(r * n + c)])

        # Phase 2: Try flipping each 0 cell
        board.log("Phase 2: Try flipping each 0-cell")
        snap(34, "Phase 2: evaluate each 0-cell")

        best_r, best_c, best_total = -1, -1, best

        for r in range(n):
            for c in range(n):
                if grid[r][c] == 0:
                    board.deselect_all()
                    board.select(r, c)

                    seen: set[int] = set()
                    candidate_total = 1  # the flipped cell itself

                    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < n and 0 <= nc < n and grid[nr][nc] == 1:
                            root = find(nr * n + nc)
                            if root not in seen:
                                seen.add(root)
                                candidate_total += size[root]

                    board.set_overlay(r, c, str(candidate_total), "#f9e2af")
                    board.log(f"  ({r},{c}): flip 0->1, potential size = {candidate_total}")
                    snap(45, f"({r},{c}): potential = {candidate_total}")

                    if candidate_total > best_total:
                        # Clear previous best overlay if it was a 0 cell
                        if best_r >= 0:
                            board.set_overlay(best_r, best_c, str(best_total), "")
                        best_total = candidate_total
                        best_r, best_c = r, c

                    # Clear overlay for non-best cells
                    if (r, c) != (best_r, best_c):
                        board.set_overlay(r, c, "", "")

                    board.deselect(r, c)

        # Show the best result
        board.deselect_all()
        if best_r >= 0:
            board.select(best_r, best_c)
            board.mark_on_path(best_r, best_c)
            board.set_overlay(best_r, best_c, str(best_total), "#a6e3a1")

            # Highlight the islands that would connect
            seen_roots: set[int] = set()
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, nc = best_r + dr, best_c + dc
                if 0 <= nr < n and 0 <= nc < n and grid[nr][nc] == 1:
                    root = find(nr * n + nc)
                    if root not in seen_roots:
                        seen_roots.add(root)
                        for pr in range(n):
                            for pc in range(n):
                                if grid[pr][pc] == 1 and find(pr * n + pc) == root:
                                    board.mark_on_path(pr, pc)

        board.log(f"Best: flip ({best_r},{best_c}), island size = {best_total}")
        snap(49, f"Answer: {best_total} (flip ({best_r},{best_c}))")
        return steps
