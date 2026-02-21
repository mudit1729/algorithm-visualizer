from __future__ import annotations

from collections import deque

from core.step import Step
from core.tracer import AuxPanelTracer, Board2DTracer, combine_step
from problems.base_problem import Problem

_SOURCE = """\
def slidingPuzzle(board):
    target = '123450'
    start = ''.join(str(c) for r in board for c in r)
    if start == target:
        return 0
    swaps = {0:[1,3],1:[0,2,4],2:[1,5],
             3:[0,4],4:[1,3,5],5:[2,4]}
    visited = set([start])
    queue = deque([(start, 0)])

    while queue:
        state, moves = queue.popleft()
        z = state.index('0')
        for nei in swaps[z]:
            s = list(state)
            s[z], s[nei] = s[nei], s[z]
            new = ''.join(s)
            if new == target:
                return moves + 1
            if new not in visited:
                visited.add(new)
                queue.append((new, moves + 1))

    return -1"""


class SlidingPuzzle(Problem):
    @staticmethod
    def name() -> str:
        return "Sliding Puzzle"

    @staticmethod
    def topic() -> str:
        return "Graph / BFS"

    @staticmethod
    def subtopic() -> str:
        return "State Space Search"

    @staticmethod
    def description() -> str:
        return "LeetCode #773: Solve a 2x3 sliding puzzle in minimum moves using BFS."

    @staticmethod
    def long_description() -> str:
        return (
            "Given a 2x3 board with tiles numbered 1-5 and one empty slot (0), "
            "find the minimum number of moves to reach the goal state "
            "`[[1,2,3],[4,5,0]]`. In one move you can swap the empty slot with "
            "an adjacent tile (up, down, left, right).\n\n"
            "Example 1:\n"
            "Input: `board = [[1,2,3],[4,0,5]]`\n"
            "Output: `1`\n\n"
            "Example 2:\n"
            "Input: `board = [[4,1,2],[5,0,3]]`\n"
            "Output: `5`\n\n"
            "Constraints:\n\n"
            "- `board.length == 2`\n"
            "- `board[i].length == 3`\n"
            "- Board contains each of `0, 1, 2, 3, 4, 5` exactly once"
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

        # Choose starting boards that are solvable in ~10-15 moves
        presets = {
            # This takes 11 moves to solve
            1: [[4, 1, 2], [5, 0, 3]],
        }

        initial_board = presets.get(preset, presets[1])

        target = "123450"
        start = "".join(str(c) for r in initial_board for c in r)

        # Adjacency for positions 0-5 in flattened 2x3 grid
        # Position layout:
        #  0  1  2
        #  3  4  5
        swaps = {
            0: [1, 3],
            1: [0, 2, 4],
            2: [1, 5],
            3: [0, 4],
            4: [1, 3, 5],
            5: [2, 4],
        }

        tracer = Board2DTracer(2, 3)
        aux = AuxPanelTracer()
        aux.add_panel("Queue")
        aux.add_panel("Moves")
        steps: list[Step] = []

        def snap(line: int, desc: str = "") -> None:
            steps.append(combine_step(tracer.snapshot(line, desc), aux))

        def show_board(state: str) -> None:
            """Update the 2x3 board from a 6-char string."""
            for idx in range(6):
                r, c = divmod(idx, 3)
                ch = state[idx]
                if ch == "0":
                    tracer.set_value(r, c, " ")
                else:
                    tracer.set_value(r, c, ch)

        def format_board(state: str) -> str:
            """Pretty format for log messages."""
            return f"[{state[0]}{state[1]}{state[2]}|{state[3]}{state[4]}{state[5]}]"

        # Show initial state
        show_board(start)
        tracer.log(f"Start: {format_board(start)}, Target: {format_board(target)}")
        snap(3, f"Start state: {format_board(start)}")

        if start == target:
            for r in range(2):
                for c in range(3):
                    tracer.patch(r, c)
            tracer.log("Already at goal! Return 0")
            snap(5, "Already solved! 0 moves")
            return steps

        visited: set[str] = {start}
        queue: deque[tuple[str, int]] = deque([(start, 0)])
        aux.set_items("Queue", [("States", "1")])
        aux.set_items("Moves", [("Current", "0")])

        tracer.log("Initialize BFS")
        snap(10, "Initialize BFS from start state")

        result = -1
        # To reconstruct the solution path, store parents
        parent: dict[str, tuple[str, int]] = {}  # state -> (prev_state, move_idx)

        while queue:
            state, moves = queue.popleft()

            show_board(state)
            tracer.deselect_all()

            z = state.index("0")
            zr, zc = divmod(z, 3)

            # Highlight the empty slot
            tracer.select(zr, zc)
            aux.set_items("Moves", [("Current", str(moves))])
            aux.set_items(
                "Queue", [("States", str(len(queue)))]
            )
            tracer.log(f"Process {format_board(state)}, moves={moves}")
            snap(13, f"Process {format_board(state)}, moves={moves}")

            found = False
            for nei in swaps[z]:
                # Create new state by swapping
                s = list(state)
                s[z], s[nei] = s[nei], s[z]
                new_state = "".join(s)

                nr, nc = divmod(nei, 3)
                tile = state[nei]

                if new_state == target:
                    # Found the solution
                    parent[new_state] = (state, moves + 1)
                    result = moves + 1

                    show_board(new_state)
                    tracer.deselect_all()
                    for r in range(2):
                        for c in range(3):
                            tracer.patch(r, c)

                    aux.set_items("Moves", [("Solution", str(result))])
                    tracer.log(f"Solved in {result} moves!")
                    snap(17, f"Solved! Target reached in {result} moves!")
                    found = True
                    break

                if new_state not in visited:
                    visited.add(new_state)
                    queue.append((new_state, moves + 1))
                    parent[new_state] = (state, moves + 1)

                    # Show the tile swap
                    show_board(new_state)
                    tracer.deselect_all()
                    tracer.select(zr, zc)   # where tile moved FROM
                    tracer.select(nr, nc)    # where tile moved TO
                    tracer.log(
                        f"  Slide tile {tile}: "
                        f"({nr},{nc})->({zr},{zc}) => {format_board(new_state)}"
                    )
                    snap(
                        20,
                        f"Slide tile {tile} -> {format_board(new_state)}",
                    )
                    tracer.deselect_all()

            if found:
                break

        if result == -1:
            show_board(state)
            tracer.clear_all_errors()
            for r in range(2):
                for c in range(3):
                    tracer.mark_error(r, c)
            tracer.log("No solution found! Return -1")
            snap(22, "Unsolvable -> return -1")
        else:
            # Reconstruct and show the solution path
            path: list[str] = []
            cur = target
            while cur in parent:
                path.append(cur)
                cur = parent[cur][0]
            path.append(start)
            path.reverse()

            tracer.deselect_all()
            tracer.depatch_all()
            tracer.log(f"Solution path ({len(path) - 1} moves):")
            for step_idx, pstate in enumerate(path):
                show_board(pstate)
                tracer.deselect_all()
                tracer.depatch_all()
                if step_idx == len(path) - 1:
                    for r in range(2):
                        for c in range(3):
                            tracer.patch(r, c)
                else:
                    # Highlight the tile that will move next
                    if step_idx < len(path) - 1:
                        next_s = path[step_idx + 1]
                        z_now = pstate.index("0")
                        z_next = next_s.index("0")
                        if z_now != z_next:
                            nr, nc = divmod(z_next, 3)
                            tracer.select(nr, nc)

                aux.set_items("Moves", [("Step", f"{step_idx}/{len(path) - 1}")])
                tracer.log(f"  Step {step_idx}: {format_board(pstate)}")
                snap(17, f"Solution step {step_idx}: {format_board(pstate)}")

        return steps
