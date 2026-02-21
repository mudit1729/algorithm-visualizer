from __future__ import annotations

from collections import deque

from core.step import Step
from core.tracer import AuxPanelTracer, GraphTracer, combine_step
from problems.base_problem import Problem

_SOURCE = """\
def alienOrder(words):
    chars = set(c for w in words for c in w)
    adj = {c: set() for c in chars}
    in_degree = {c: 0 for c in chars}

    for i in range(len(words) - 1):
        w1, w2 = words[i], words[i + 1]
        min_len = min(len(w1), len(w2))
        for j in range(min_len):
            if w1[j] != w2[j]:
                if w2[j] not in adj[w1[j]]:
                    adj[w1[j]].add(w2[j])
                    in_degree[w2[j]] += 1
                break

    queue = deque(c for c in chars
                  if in_degree[c] == 0)
    order = []

    while queue:
        c = queue.popleft()
        order.append(c)
        for nei in sorted(adj[c]):
            in_degree[nei] -= 1
            if in_degree[nei] == 0:
                queue.append(nei)

    if len(order) == len(chars):
        return ''.join(order)
    return ''"""


class AlienDictionary(Problem):
    @staticmethod
    def name() -> str:
        return "Alien Dictionary"

    @staticmethod
    def topic() -> str:
        return "Topological Sort"

    @staticmethod
    def subtopic() -> str:
        return "Order Reconstruction"

    @staticmethod
    def description() -> str:
        return "LeetCode #269: Derive character ordering from a sorted alien dictionary using topological sort."

    @staticmethod
    def long_description() -> str:
        return (
            "Given a sorted list of words from an alien language, derive the "
            "ordering of characters in that language. Build a DAG where an edge "
            "`u -> v` means character `u` comes before `v`. Then perform a "
            "topological sort (Kahn's BFS) to find the order.\n\n"
            "Example:\n"
            "Input: `[\"bac\", \"baf\", \"bag\", \"dac\", \"dcc\", \"dcf\", \"fag\", \"gbe\", \"ech\", \"hbf\"]`\n"
            "Output: `\"abdcfgeh\"` (one valid ordering)\n\n"
            "Constraints:\n\n"
            "- `1 <= words.length <= 100`\n"
            "- `1 <= words[i].length <= 100`\n"
            "- All characters are lowercase English letters"
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
            1: ["bac", "baf", "bag", "dac", "dcc", "dcf", "fag", "gbe", "ech", "hbf"],
        }

        words = presets.get(preset, presets[1])

        # Collect all unique characters
        chars = sorted(set(c for w in words for c in w))

        graph = GraphTracer(chars, directed=True)
        aux = AuxPanelTracer()
        aux.add_panel("Order")
        aux.add_panel("In-Degree")
        steps: list[Step] = []

        def snap(line: int, desc: str = "") -> None:
            steps.append(combine_step(graph.snapshot(line, desc), aux))

        # Initial state
        for ch in chars:
            graph.set_label(ch, ch)
        graph.log(f"Words: {words}")
        graph.log(f"Characters: {chars}")
        snap(1, f"Alien dictionary with {len(chars)} unique characters")

        # Phase 1: Build the DAG by comparing adjacent word pairs
        adj: dict[str, set[str]] = {c: set() for c in chars}
        in_degree: dict[str, int] = {c: 0 for c in chars}

        graph.log("--- Phase 1: Build DAG from adjacent word pairs ---")
        snap(6, "Build DAG by comparing adjacent words")

        for i in range(len(words) - 1):
            w1, w2 = words[i], words[i + 1]
            min_len = min(len(w1), len(w2))
            found = False
            for j in range(min_len):
                if w1[j] != w2[j]:
                    u, v = w1[j], w2[j]
                    # Highlight the two characters being compared
                    graph.select_node(u)
                    graph.select_node(v)
                    if v not in adj[u]:
                        adj[u].add(v)
                        in_degree[v] += 1
                        graph.add_edge(u, v)
                        graph.select_edge(u, v)
                        graph.log(
                            f"Compare \"{w1}\" vs \"{w2}\": "
                            f"'{u}' != '{v}' => edge {u}->{v}"
                        )
                        snap(13, f"\"{w1}\" vs \"{w2}\": {u} < {v}")
                        graph.deselect_edge(u, v)
                    else:
                        graph.log(
                            f"Compare \"{w1}\" vs \"{w2}\": "
                            f"'{u}' != '{v}' => edge {u}->{v} (already exists)"
                        )
                        snap(13, f"\"{w1}\" vs \"{w2}\": {u}<{v} (dup)")
                    graph.deselect_node(u)
                    graph.deselect_node(v)
                    found = True
                    break
            if not found:
                graph.log(f"Compare \"{w1}\" vs \"{w2}\": prefix match, no new edge")
                snap(8, f"\"{w1}\" vs \"{w2}\": prefix, no edge")

        # Apply layered layout after all edges are added
        graph.set_layered_layout()

        # Update in-degree display
        aux.set_items("In-Degree", [(c, str(in_degree[c])) for c in chars])
        graph.log("DAG built. Applying layered layout.")
        snap(30, "DAG complete, layered layout applied")

        # Phase 2: Topological sort (Kahn's algorithm)
        graph.log("--- Phase 2: Topological sort (Kahn's BFS) ---")
        snap(20, "Begin topological sort")

        queue: deque[str] = deque()
        for c in chars:
            if in_degree[c] == 0:
                queue.append(c)
                graph.select_node(c)
                graph.set_node_color(c, "#89b4fa")

        queue_str = ", ".join(queue)
        graph.log(f"Initial queue (in-degree 0): [{queue_str}]")
        aux.set_items("In-Degree", [(c, str(in_degree[c])) for c in chars])
        snap(21, f"Start queue: [{queue_str}]")

        order: list[str] = []
        layer_num = 0
        # Track which layer each node belongs to for grouping
        node_layer: dict[str, int] = {}

        while queue:
            # Snapshot the current queue state
            batch_size = len(queue)
            c = queue.popleft()
            order.append(c)

            # Assign group based on topological layer
            if c not in node_layer:
                # Determine layer: max of predecessors' layers + 1, or 0
                pred_layers = [
                    node_layer[p]
                    for p in chars
                    if c in adj.get(p, set()) and p in node_layer
                ]
                node_layer[c] = (max(pred_layers) + 1) if pred_layers else 0
            graph.set_node_group(c, node_layer[c])

            graph.deselect_all_nodes()
            graph.deselect_all_edges()
            graph.patch_node(c)
            graph.set_node_color(c, "#a6e3a1")
            graph.set_node_badge(c, f"#{len(order)}")
            aux.push("Order", c, f"pos {len(order)}")
            graph.log(f"Dequeue '{c}', add to order (pos {len(order)})")
            aux.set_items("In-Degree", [(ch, str(in_degree[ch])) for ch in chars])
            snap(24, f"Take '{c}' (order pos {len(order)})")

            for nei in sorted(adj[c]):
                in_degree[nei] -= 1
                graph.select_edge(c, nei)
                graph.select_node(nei)
                graph.set_label(nei, f"{nei}({in_degree[nei]})")
                aux.set_items("In-Degree", [(ch, str(in_degree[ch])) for ch in chars])
                graph.log(f"  in_degree['{nei}'] = {in_degree[nei]}")
                snap(28, f"in_degree['{nei}'] = {in_degree[nei]}")

                if in_degree[nei] == 0:
                    queue.append(nei)
                    graph.set_node_color(nei, "#89b4fa")
                    graph.log(f"  '{nei}' ready (in-degree 0), enqueue")
                    snap(30, f"'{nei}' now available")

                graph.deselect_edge(c, nei)
                graph.deselect_node(nei)

        # Final result
        graph.deselect_all_nodes()
        graph.deselect_all_edges()
        result = "".join(order)
        if len(order) == len(chars):
            graph.log(f"Valid alien order: {result}")
            snap(29, f"Alien order: {result}")
        else:
            graph.log("Cycle detected! No valid ordering.")
            snap(30, "No valid ordering (cycle)")

        return steps
