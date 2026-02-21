from __future__ import annotations

from collections import deque

from core.step import Step
from core.tracer import AuxPanelTracer, Board2DTracer, combine_step
from problems.base_problem import Problem

_SOURCE = """\
def openLock(deadends, target):
    dead = set(deadends)
    if '0000' in dead:
        return -1
    visited = set(['0000'])
    queue = deque([('0000', 0)])

    while queue:
        state, moves = queue.popleft()
        if state == target:
            return moves
        for i in range(4):
            d = int(state[i])
            for delta in (-1, 1):
                nd = (d + delta) % 10
                new = state[:i] + str(nd) + state[i+1:]
                if new not in visited and new not in dead:
                    visited.add(new)
                    queue.append((new, moves + 1))

    return -1"""


class OpenTheLock(Problem):
    @staticmethod
    def name() -> str:
        return "Open the Lock"

    @staticmethod
    def topic() -> str:
        return "Graph / BFS"

    @staticmethod
    def subtopic() -> str:
        return "State Space Search"

    @staticmethod
    def description() -> str:
        return "LeetCode #752: Find minimum moves to reach target lock combination using BFS."

    @staticmethod
    def long_description() -> str:
        return (
            "A lock has 4 circular wheels, each with digits 0-9. Each move turns "
            "one wheel one slot up or down. Given a list of deadend combinations "
            "and a target, find the minimum moves to reach the target from '0000'. "
            "If it is impossible, return -1.\n\n"
            "Example 1:\n"
            "Input: `deadends = ['0201','0101','0102','1212','2002']`, "
            "`target = '0202'`\n"
            "Output: `6`\n\n"
            "Constraints:\n\n"
            "- `1 <= deadends.length <= 500`\n"
            "- `deadends[i].length == 4`\n"
            "- `target.length == 4`\n"
            "- target will not be in deadends"
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
            1: (
                ["0201", "0101", "0102", "1212", "2002"],
                "0202",
            ),
        }

        deadends, target = presets.get(preset, presets[1])
        dead = set(deadends)

        tracer = Board2DTracer(1, 4)
        aux = AuxPanelTracer()
        aux.add_panel("BFS Queue")
        aux.add_panel("Visited")
        steps: list[Step] = []

        def snap(line: int, desc: str = "") -> None:
            steps.append(combine_step(tracer.snapshot(line, desc), aux))

        def show_state(state: str) -> None:
            """Update the 1x4 board to display the lock state."""
            for i in range(4):
                tracer.set_value(0, i, state[i])

        # Initialize
        show_state("0000")
        tracer.log(f"Target: {target}, Deadends: {deadends}")
        snap(2, f"Start: '0000', Target: '{target}'")

        if "0000" in dead:
            tracer.log("Start is a deadend! Return -1")
            for i in range(4):
                tracer.mark_error(0, i)
            snap(4, "'0000' is a deadend -> return -1")
            return steps

        visited: set[str] = {"0000"}
        queue: deque[tuple[str, int]] = deque([("0000", 0)])
        aux.push("BFS Queue", "0000", "moves=0")
        aux.set_items("Visited", [("Count", str(len(visited)))])
        tracer.log("Enqueue '0000' with 0 moves")
        snap(6, "Initialize BFS queue with '0000'")

        result = -1
        deadend_shown = 0

        # Run BFS level by level for a cleaner visualization
        # We snap: level start, a few dequeues per level, deadend hits, target
        current_moves = 0

        while queue:
            # Process one full BFS level
            level_size = len(queue)
            tracer.deselect_all()
            aux.set_items("BFS Queue", [("Size", str(level_size))])
            aux.set_items("Visited", [("Count", str(len(visited)))])
            tracer.log(f"--- BFS Level {current_moves} ({level_size} states) ---")
            snap(8, f"Level {current_moves}: {level_size} states to process")

            found = False
            shown_this_level = 0
            new_states_this_level = 0

            for _li in range(level_size):
                state, moves = queue.popleft()

                if state == target:
                    show_state(state)
                    tracer.deselect_all()
                    for i in range(4):
                        tracer.patch(0, i)
                    tracer.log(f"Target reached! Moves = {moves}")
                    aux.set_items("BFS Queue", [("Size", "0")])
                    snap(11, f"Target '{target}' reached in {moves} moves!")
                    result = moves
                    found = True
                    break

                # Show a few representative dequeues per level
                if shown_this_level < 2:
                    show_state(state)
                    tracer.deselect_all()
                    for i in range(4):
                        tracer.select(0, i)
                    tracer.log(f"Dequeue '{state}' (moves={moves})")
                    snap(9, f"Process '{state}', moves={moves}")
                    tracer.deselect_all()
                    shown_this_level += 1

                # Generate neighbors
                for i in range(4):
                    d = int(state[i])
                    for delta in (-1, 1):
                        nd = (d + delta) % 10
                        new_state = state[:i] + str(nd) + state[i + 1:]

                        if new_state in dead:
                            if deadend_shown < 3:
                                show_state(new_state)
                                for j in range(4):
                                    tracer.mark_error(0, j)
                                tracer.log(f"  '{new_state}' is a deadend, skip")
                                snap(17, f"'{new_state}' is deadend, skip")
                                tracer.clear_all_errors()
                                deadend_shown += 1
                            continue

                        if new_state not in visited:
                            visited.add(new_state)
                            queue.append((new_state, moves + 1))
                            new_states_this_level += 1

                            # Show first few new states per level
                            if new_states_this_level <= 2:
                                show_state(new_state)
                                tracer.deselect_all()
                                tracer.select(0, i)
                                tracer.log(
                                    f"  Enqueue '{new_state}' (wheel {i}: "
                                    f"{state[i]}->{new_state[i]})"
                                )
                                aux.set_items(
                                    "Visited",
                                    [("Count", str(len(visited)))],
                                )
                                snap(
                                    19,
                                    f"Enqueue '{new_state}' (moves={moves + 1})",
                                )
                                tracer.deselect_all()

            if found:
                break

            if new_states_this_level > 2:
                tracer.log(
                    f"  ... {new_states_this_level} new states added at level "
                    f"{current_moves + 1}"
                )
                aux.set_items("BFS Queue", [("Size", str(len(queue)))])
                aux.set_items("Visited", [("Count", str(len(visited)))])
                snap(
                    19,
                    f"Level {current_moves}: +{new_states_this_level} new, "
                    f"queue={len(queue)}",
                )

            current_moves += 1

        if result == -1:
            show_state("0000")
            for i in range(4):
                tracer.mark_error(0, i)
            tracer.log(f"Cannot reach target '{target}'. Return -1")
            snap(22, f"No path to '{target}' -> return -1")

        return steps
