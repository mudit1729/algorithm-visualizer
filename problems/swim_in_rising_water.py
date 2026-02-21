from __future__ import annotations

from core.step import Step
from core.tracer import AuxPanelTracer, Board2DTracer, combine_step
from problems.base_problem import Problem

_SOURCE = """\
def swimInWater(grid):
    n = len(grid)
    parent = list(range(n * n))
    rank = [0] * (n * n)

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
        if rank[rx] == rank[ry]:
            rank[rx] += 1

    pos = {}
    for r in range(n):
        for c in range(n):
            pos[grid[r][c]] = (r, c)

    for t in range(n * n):
        r, c = pos[t]
        for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < n and 0 <= nc < n:
                if grid[nr][nc] <= t:
                    union(r * n + c, nr * n + nc)
        if find(0) == find(n * n - 1):
            return t

    return n * n - 1"""


class SwimInRisingWater(Problem):
    @staticmethod
    def name() -> str:
        return "Swim in Rising Water"

    @staticmethod
    def topic() -> str:
        return "Union Find"

    @staticmethod
    def subtopic() -> str:
        return "Grid Union Find"

    @staticmethod
    def description() -> str:
        return "LeetCode #778: Find minimum time to swim from top-left to bottom-right as water rises."

    @staticmethod
    def long_description() -> str:
        return (
            "Given an `n x n` grid where `grid[r][c]` is the elevation, water "
            "rises to level `t` at time `t`. You can swim from `(0,0)` to "
            "`(n-1,n-1)` through cells with elevation `<= t`. Find the minimum "
            "`t` such that a path exists.\n\n"
            "Algorithm: Process cells in order of elevation. At each time step, "
            "union the new cell with any adjacent cells already underwater. Check "
            "if `(0,0)` and `(n-1,n-1)` are connected.\n\n"
            "Example:\n"
            "Input: `grid = [[0,2],[1,3]]`\n"
            "Output: `3`\n\n"
            "Constraints:\n\n"
            "- `2 <= n <= 50`\n"
            "- All values in `[0, n*n - 1]` are unique"
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
            1: [
                [ 0, 25, 16, 38, 28, 13, 44],
                [31,  5, 21, 43, 37, 11, 47],
                [12, 34,  2, 17, 45, 30, 48],
                [39, 14, 33,  8, 46, 22,  6],
                [40, 26, 42,  3, 35, 19, 41],
                [ 9, 27, 36, 23,  7, 32, 15],
                [29, 10, 20,  1, 24,  4, 18],
            ],
        }

        grid = presets.get(preset, presets[1])
        n = len(grid)
        total = n * n

        parent = list(range(total))
        rank = [0] * total

        board = Board2DTracer(n, n)
        aux = AuxPanelTracer()
        aux.add_panel("Time")
        steps: list[Step] = []

        def snap(line: int, desc: str = "") -> None:
            steps.append(combine_step(board.snapshot(line, desc), aux))

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
            if rank[rx] == rank[ry]:
                rank[rx] += 1

        # Initialize board with elevation values
        for r in range(n):
            for c in range(n):
                board.set_value(r, c, str(grid[r][c]))

        # Map elevation -> position
        pos: dict[int, tuple[int, int]] = {}
        for r in range(n):
            for c in range(n):
                pos[grid[r][c]] = (r, c)

        aux.set_items("Time", [("Water Level", "0")])
        board.log(f"Grid: {n}x{n}, swim from (0,0) to ({n-1},{n-1})")
        snap(1, f"{n}x{n} grid, elevation values 0-{total - 1}")

        # Process cells in order of elevation
        underwater: set[tuple[int, int]] = set()
        answer = -1

        for t in range(total):
            r, c = pos[t]
            aux.set_items("Time", [("Water Level", str(t))])

            # Select the current cell being processed
            board.deselect_all()
            board.select(r, c)
            board.log(f"t={t}: cell ({r},{c}) now underwater")
            snap(22, f"t={t}: cell ({r},{c}) elevation={t}")

            # Mark cell as underwater (patched)
            underwater.add((r, c))
            board.patch(r, c)
            board.set_overlay(r, c, str(t), "#89b4fa")

            # Union with adjacent underwater cells
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < n and 0 <= nc < n and (nr, nc) in underwater:
                    union(r * n + c, nr * n + nc)

            # Check if start and end are connected
            if find(0) == find((n - 1) * n + (n - 1)):
                answer = t
                board.log(f"  Connected! (0,0) and ({n-1},{n-1}) in same component")
                snap(29, f"t={t}: path found!")

                # Trace the path by marking connected cells
                start_root = find(0)
                for pr in range(n):
                    for pc in range(n):
                        if (pr, pc) in underwater and find(pr * n + pc) == start_root:
                            board.mark_on_path(pr, pc)

                board.log(f"Answer: t = {answer}")
                snap(30, f"Minimum time = {answer}")
                break
            else:
                board.deselect(r, c)

        if answer == -1:
            answer = total - 1
            board.log(f"Answer: t = {answer}")
            snap(32, f"Minimum time = {answer}")

        return steps
