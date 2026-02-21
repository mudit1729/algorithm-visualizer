from __future__ import annotations

import heapq
from collections import Counter

from core.step import Step
from core.tracer import AuxPanelTracer, GraphTracer, combine_step
from problems.base_problem import Problem

_SOURCE = """\
def leastInterval(tasks, n):
    freq = Counter(tasks)
    heap = [-cnt for cnt in freq.values()]
    heapq.heapify(heap)

    time = 0
    schedule = []
    cooldown = []

    while heap or cooldown:
        time += 1
        if heap:
            cnt = heapq.heappop(heap) + 1
            if cnt < 0:
                cooldown.append((cnt, time + n))
            task = pick_task(cnt)
            schedule.append(task)
        else:
            schedule.append('idle')

        while cooldown and cooldown[0][1] <= time:
            heapq.heappush(heap, cooldown.pop(0)[0])

    return len(schedule)"""


class TaskScheduler(Problem):
    @staticmethod
    def name() -> str:
        return "Task Scheduler"

    @staticmethod
    def topic() -> str:
        return "Greedy"

    @staticmethod
    def subtopic() -> str:
        return "Scheduling"

    @staticmethod
    def description() -> str:
        return "LeetCode #621: Schedule tasks with cooldown using a greedy max-heap approach."

    @staticmethod
    def long_description() -> str:
        return (
            "Given a list of tasks (uppercase letters) and a cooldown interval `n`, "
            "find the minimum number of time units the CPU will take to finish all tasks. "
            "The same task must have at least `n` units of cooldown between executions.\n\n"
            "Strategy: Always pick the most frequent available task (greedy via max-heap). "
            "If no task is available, insert an idle slot.\n\n"
            "Example:\n"
            "Input: `tasks = ['A','A','A','B','B','B','C','C','D','D','E','F']`, `n = 2`\n"
            "Output: `12` (e.g. A B C A B D A D E F idle idle ...)\n\n"
            "Constraints:\n\n"
            "- `1 <= tasks.length <= 10^4`\n"
            "- `tasks[i]` is an uppercase English letter\n"
            "- `0 <= n <= 100`"
        )

    @staticmethod
    def source_code() -> str:
        return _SOURCE

    @staticmethod
    def renderer_type() -> str:
        return "graph"

    @staticmethod
    def default_params() -> dict[str, object]:
        return {"preset": 1}

    @staticmethod
    def generate_steps(**kwargs: object) -> list[Step]:
        preset = int(kwargs.get("preset", 1))

        presets = {
            1: (
                ["A", "A", "A", "B", "B", "B", "C", "C", "D", "D", "E", "F"],
                2,
            ),
        }

        tasks_list, cooldown_n = presets.get(preset, presets[1])

        # Count frequencies
        freq = Counter(tasks_list)
        task_types = sorted(freq.keys())

        # Build graph nodes: one node per task type + idle node
        all_nodes = task_types + ["idle"]
        graph = GraphTracer(all_nodes, directed=True)
        aux = AuxPanelTracer()
        aux.add_panel("Schedule")
        aux.add_panel("Heap")
        aux.add_panel("Cooldown")
        steps: list[Step] = []

        def snap(line: int, desc: str = "") -> None:
            steps.append(combine_step(graph.snapshot(line, desc), aux))

        # Set labels with frequencies
        for t in task_types:
            graph.set_label(t, f"{t}({freq[t]})")
        graph.set_label("idle", "idle")
        graph.set_node_color("idle", "#585b70")

        freq_str = ", ".join(f"{t}:{freq[t]}" for t in task_types)
        graph.log(f"Tasks: {tasks_list}")
        graph.log(f"Frequencies: {freq_str}, cooldown n={cooldown_n}")
        snap(1, f"Task frequencies: {freq_str}, n={cooldown_n}")

        # Initialize max-heap (negate for max-heap behavior)
        # Store (-count, task_name) to break ties alphabetically
        heap: list[tuple[int, str]] = [(-freq[t], t) for t in task_types]
        heapq.heapify(heap)

        # Show initial heap
        heap_display = [(t, str(-cnt)) for cnt, t in sorted(heap)]
        aux.set_items("Heap", heap_display)
        graph.log("Max-heap initialized (most frequent first)")
        snap(3, "Heap initialized with task frequencies")

        time_step = 0
        schedule: list[str] = []
        # cooldown_queue stores (neg_count, available_at_time, task_name)
        cooldown_queue: list[tuple[int, int, str]] = []
        round_num = 0

        # Track edges to show execution order
        prev_task_node: str | None = None

        while heap or cooldown_queue:
            time_step += 1
            round_num += 1

            # Move tasks whose cooldown has expired back to heap
            released = []
            still_cooling = []
            for entry in cooldown_queue:
                neg_cnt, avail_time, tname = entry
                if avail_time <= time_step:
                    heapq.heappush(heap, (neg_cnt, tname))
                    released.append(tname)
                    graph.set_node_color(tname, "")
                    graph.depatch_node(tname)
                else:
                    still_cooling.append(entry)
            cooldown_queue = still_cooling

            if released:
                graph.log(f"t={time_step}: Released from cooldown: {released}")
                aux.set_items("Cooldown", [
                    (tname, f"until t={avail}")
                    for _, avail, tname in cooldown_queue
                ])
                heap_display = [(t, str(-cnt)) for cnt, t in sorted(heap)]
                aux.set_items("Heap", heap_display)
                snap(22, f"t={time_step}: {released} back in heap")

            if heap:
                neg_cnt, task_name = heapq.heappop(heap)
                remaining = -neg_cnt - 1
                schedule.append(task_name)

                # Visual: select the task being executed
                graph.deselect_all_nodes()
                graph.select_node(task_name)
                graph.set_node_color(task_name, "#a6e3a1")
                graph.set_label(task_name, f"{task_name}({remaining})")
                graph.set_node_badge(task_name, f"t{time_step}")
                graph.set_node_group(task_name, round_num)

                # Add edge showing execution flow
                if prev_task_node is not None and prev_task_node != task_name:
                    edge_key = (prev_task_node, task_name)
                    if edge_key not in [
                        (e, t) for e, t in getattr(graph, '_edges', [])
                    ]:
                        graph.add_edge(prev_task_node, task_name)
                    graph.patch_edge(prev_task_node, task_name)

                # Update aux panels
                aux.push("Schedule", task_name, f"t={time_step}")
                heap_display = [(t, str(-cnt)) for cnt, t in sorted(heap)]
                aux.set_items("Heap", heap_display)

                graph.log(
                    f"t={time_step}: Execute '{task_name}' "
                    f"(remaining={remaining})"
                )
                snap(14, f"t={time_step}: Execute '{task_name}'")

                if remaining > 0:
                    cooldown_queue.append(
                        (-remaining, time_step + cooldown_n, task_name)
                    )
                    graph.set_node_color(task_name, "#f9e2af")
                    graph.patch_node(task_name)
                    aux.set_items("Cooldown", [
                        (tname, f"until t={avail}")
                        for _, avail, tname in cooldown_queue
                    ])
                    graph.log(
                        f"  '{task_name}' on cooldown until t={time_step + cooldown_n}"
                    )
                    snap(16, f"'{task_name}' cooling until t={time_step + cooldown_n}")
                else:
                    graph.set_node_color(task_name, "#a6e3a1")
                    graph.patch_node(task_name)
                    graph.log(f"  '{task_name}' fully completed!")
                    snap(14, f"'{task_name}' done!")

                prev_task_node = task_name
            else:
                # No available task, must idle
                schedule.append("idle")
                graph.deselect_all_nodes()
                graph.select_node("idle")
                graph.set_node_badge("idle", f"t{time_step}")
                graph.set_node_group("idle", round_num)

                if prev_task_node is not None and prev_task_node != "idle":
                    edge_key = (prev_task_node, "idle")
                    if edge_key not in [
                        (e, t) for e, t in getattr(graph, '_edges', [])
                    ]:
                        graph.add_edge(prev_task_node, "idle")
                    graph.patch_edge(prev_task_node, "idle")

                aux.push("Schedule", "idle", f"t={time_step}")
                graph.log(f"t={time_step}: IDLE (all tasks on cooldown)")
                snap(19, f"t={time_step}: idle")
                prev_task_node = "idle"

        # Apply layered layout at the end for timeline view
        graph.set_layered_layout()

        # Final result
        graph.deselect_all_nodes()
        graph.deselect_all_edges()
        schedule_str = " -> ".join(schedule)
        graph.log(f"Schedule complete: {schedule_str}")
        graph.log(f"Total time units: {len(schedule)}")
        aux.set_items("Heap", [])
        aux.set_items("Cooldown", [])
        snap(25, f"Done! Total time = {len(schedule)}")

        return steps
