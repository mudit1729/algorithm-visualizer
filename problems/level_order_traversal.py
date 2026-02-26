from __future__ import annotations

from collections import deque

from core.step import Step
from core.tracer import AuxPanelTracer, GraphTracer, combine_step
from problems.base_problem import Problem

_SOURCE = """\
def levelOrder(root):
    if not root:
        return []
    result = []
    queue = deque([root])

    while queue:
        level = []
        for _ in range(len(queue)):
            node = queue.popleft()
            level.append(node.val)
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
        result.append(level)

    return result"""


class LevelOrderTraversal(Problem):
    @staticmethod
    def name() -> str:
        return "Binary Tree Level Order Traversal"

    @staticmethod
    def topic() -> str:
        return "Tree / BFS"

    @staticmethod
    def subtopic() -> str:
        return "Level Order"

    @staticmethod
    def description() -> str:
        return "LeetCode #102: Return level order traversal of a binary tree using BFS."

    @staticmethod
    def long_description() -> str:
        return (
            "Given the root of a binary tree, return the level order traversal "
            "of its nodes' values (i.e., from left to right, level by level).\n\n"
            "Example 1:\n"
            "Input: `root = [3,9,20,null,null,15,7]`\n"
            "Output: `[[3],[9,20],[15,7]]`\n\n"
            "Constraints:\n\n"
            "- The number of nodes is in the range `[0, 2000]`\n"
            "- `-1000 <= Node.val <= 1000`"
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
    def theory() -> str:
        return """Approach: Traverse a binary tree level by level using BFS. Use a queue: start with the root, then for each level, process all nodes in the queue, adding their children for the next level. Group nodes by level.

Time Complexity: O(N) where N is the number of nodes — each node visited once.

Space Complexity: O(W) where W is the maximum width of the tree (the largest level). For a complete binary tree, this is O(N/2) = O(N).

Key Insight: The "trick" for grouping by level is to record the queue size at the start of each level. Process exactly that many nodes, and any new nodes added go to the next level.

Interview Tip: Level-order traversal (BFS) is the foundation for many tree problems: zigzag traversal, right side view, average of levels, largest value in each row. Master this pattern."""

    @staticmethod
    def generate_steps(**kwargs: object) -> list[Step]:
        preset = int(kwargs.get("preset", 1))

        # Binary tree as adjacency: node_id -> (label, left_child, right_child)
        # Tree structure:
        #            1(3)
        #          /       \
        #       2(9)      3(20)
        #      /   \      /   \
        #    4(8)  5(4) 6(15) 7(7)
        #    /       \
        #  8(2)     9(1)
        presets = {
            1: {
                1: ("3",  2, 3),
                2: ("9",  4, 5),
                3: ("20", 6, 7),
                4: ("8",  8, None),
                5: ("4",  None, 9),
                6: ("15", None, None),
                7: ("7",  None, None),
                8: ("2",  None, None),
                9: ("1",  None, None),
            },
        }

        tree = presets.get(preset, presets[1])
        node_ids = sorted(tree.keys())

        tracer = GraphTracer(node_ids, directed=True)
        aux = AuxPanelTracer()
        aux.add_panel("Queue")
        aux.add_panel("Result")
        steps: list[Step] = []

        def snap(line: int, desc: str = "") -> None:
            steps.append(combine_step(tracer.snapshot(line, desc), aux))

        # Position nodes in a tree layout manually
        positions = {
            1: (0.50, 0.07),
            2: (0.25, 0.25),
            3: (0.75, 0.25),
            4: (0.13, 0.45),
            5: (0.37, 0.45),
            6: (0.63, 0.45),
            7: (0.87, 0.45),
            8: (0.07, 0.65),
            9: (0.43, 0.65),
        }
        for nid in node_ids:
            label, left, right = tree[nid]
            tracer.set_label(nid, label)
            tracer._positions[nid] = positions[nid]

        # Add edges
        for nid in node_ids:
            _label, left, right = tree[nid]
            if left is not None:
                tracer.add_edge(nid, left)
            if right is not None:
                tracer.add_edge(nid, right)

        tracer.log("Binary tree with 9 nodes")
        snap(2, "Initialize binary tree")

        # BFS level order traversal
        root = 1
        queue: deque[int] = deque([root])
        aux.push("Queue", tree[root][0], f"node {root}")
        tracer.log("Start BFS: enqueue root")
        snap(5, "Enqueue root node")

        result: list[list[str]] = []
        level_num = 0

        while queue:
            level_size = len(queue)
            level: list[str] = []

            tracer.deselect_all_nodes()
            tracer.log(f"--- Level {level_num} ({level_size} nodes) ---")
            snap(8, f"Level {level_num}: processing {level_size} nodes")

            for i in range(level_size):
                node_id = queue.popleft()
                aux.pop_front("Queue")
                node_label, left_child, right_child = tree[node_id]
                level.append(node_label)

                # Select current node
                tracer.deselect_all_nodes()
                tracer.select_node(node_id)
                tracer.log(f"Dequeue node {node_label}")
                snap(10, f"Dequeue node {node_label} (id={node_id})")

                # Enqueue left child
                if left_child is not None:
                    queue.append(left_child)
                    aux.push("Queue", tree[left_child][0], f"node {left_child}")
                    tracer.select_edge(node_id, left_child)
                    tracer.log(f"  Enqueue left child: {tree[left_child][0]}")
                    snap(13, f"Enqueue left child {tree[left_child][0]}")
                    tracer.deselect_edge(node_id, left_child)

                # Enqueue right child
                if right_child is not None:
                    queue.append(right_child)
                    aux.push("Queue", tree[right_child][0], f"node {right_child}")
                    tracer.select_edge(node_id, right_child)
                    tracer.log(f"  Enqueue right child: {tree[right_child][0]}")
                    snap(15, f"Enqueue right child {tree[right_child][0]}")
                    tracer.deselect_edge(node_id, right_child)

                # Patch node as processed
                tracer.deselect_node(node_id)
                tracer.patch_node(node_id)

            result.append(level)
            level_str = "[" + ", ".join(level) + "]"
            aux.push("Result", f"L{level_num}", level_str)
            tracer.log(f"Level {level_num} complete: {level_str}")
            snap(18, f"Level {level_num} = {level_str}")
            level_num += 1

        # Final result
        tracer.deselect_all_nodes()
        result_str = str([[v for v in lv] for lv in result])
        tracer.log(f"Result: {result_str}")
        snap(18, f"Done! {level_num} levels traversed")
        return steps
