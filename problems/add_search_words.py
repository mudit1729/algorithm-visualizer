from __future__ import annotations

from core.step import Step
from core.tracer import TrieTracer
from problems.base_problem import Problem

_SOURCE = """\
class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end = False

class WordDictionary:
    def __init__(self):
        self.root = TrieNode()

    def addWord(self, word):
        node = self.root
        for ch in word:
            if ch not in node.children:
                node.children[ch] = TrieNode()
            node = node.children[ch]
        node.is_end = True

    def search(self, word):
        def dfs(node, i):
            if i == len(word):
                return node.is_end
            ch = word[i]
            if ch == '.':
                for child in node.children.values():
                    if dfs(child, i + 1):
                        return True
                return False
            if ch not in node.children:
                return False
            return dfs(node.children[ch], i + 1)
        return dfs(self.root, 0)"""


class AddSearchWords(Problem):
    @staticmethod
    def name() -> str:
        return "Add and Search Words"

    @staticmethod
    def topic() -> str:
        return "Trie"

    @staticmethod
    def subtopic() -> str:
        return "Pattern Matching"

    @staticmethod
    def description() -> str:
        return "LeetCode #211: Design a data structure that supports adding words and searching with wildcards."

    @staticmethod
    def long_description() -> str:
        return (
            "Design a data structure that supports adding new words and finding "
            "if a string matches any previously added string. The `search` method "
            "supports the `'.'` wildcard character, which can match any letter.\n\n"
            "- `addWord(word)` adds `word` to the data structure.\n"
            "- `search(word)` returns `true` if any string in the data structure "
            "matches `word`. A `'.'` matches any single character.\n\n"
            "Example:\n"
            "Input: `addWord(\"bad\")`, `addWord(\"dad\")`, `search(\".ad\")` -> `true`, "
            "`search(\"b..\")` -> `true`\n\n"
            "Constraints:\n\n"
            "- `1 <= word.length <= 25`\n"
            "- `word` in `addWord` consists of lowercase English letters\n"
            "- `word` in `search` consists of `'.'` or lowercase English letters"
        )

    @staticmethod
    def source_code() -> str:
        return _SOURCE

    @staticmethod
    def renderer_type() -> str:
        return "trie"

    @staticmethod
    def default_params() -> dict[str, object]:
        return {"preset": 1}

    @staticmethod
    def generate_steps(**kwargs: object) -> list[Step]:
        preset = int(kwargs.get("preset", 1))

        presets = {
            1: {
                "add": ["bad", "dad", "mad", "bat", "pad"],
                "search": ["bad", ".ad", "b..", "b.d", "...", "ba.", "xyz"],
            },
        }

        data = presets.get(preset, presets[1])
        words_to_add = data["add"]
        patterns_to_search = data["search"]

        tracer = TrieTracer()
        steps: list[Step] = []

        def snap(line: int, desc: str = "") -> None:
            steps.append(tracer.snapshot(line, desc))

        # Internal trie tracking
        trie_children: dict[int, dict[str, int]] = {}
        trie_is_end: dict[int, bool] = {}

        # Create root
        root_id = tracer.add_node(label="root")
        trie_children[root_id] = {}
        trie_is_end[root_id] = False

        tracer.log("Initialize empty WordDictionary")
        snap(10, "Create empty WordDictionary")

        # =============================================
        # PHASE 1: ADD WORDS
        # =============================================
        tracer.log("--- Phase 1: Add words ---")
        snap(10, "Phase 1: Add words to dictionary")

        for word in words_to_add:
            tracer.deselect_all_nodes()
            tracer.deselect_all_edges()
            tracer.log(f"addWord(\"{word}\")")
            snap(12, f"addWord(\"{word}\")")

            current = root_id
            tracer.select_node(current)
            snap(13, f"Start at root")

            for i, ch in enumerate(word):
                if ch in trie_children[current]:
                    # Existing path
                    child_id = trie_children[current][ch]
                    tracer.select_edge(current, child_id)
                    tracer.select_node(child_id)
                    tracer.log(f"  '{ch}' exists, follow edge")
                    snap(16, f"'{ch}' exists, follow to node {child_id}")
                    tracer.deselect_node(current)
                    tracer.deselect_edge(current, child_id)
                    current = child_id
                else:
                    # Create new node
                    new_id = tracer.add_node(label=ch)
                    trie_children[new_id] = {}
                    trie_is_end[new_id] = False
                    tracer.add_edge(current, new_id, label=ch)
                    trie_children[current][ch] = new_id
                    tracer.select_edge(current, new_id)
                    tracer.select_node(new_id)
                    tracer.log(f"  Create node for '{ch}'")
                    snap(18, f"Create new node for '{ch}'")
                    tracer.deselect_node(current)
                    tracer.deselect_edge(current, new_id)
                    current = new_id

            # Mark end
            tracer.set_end(current, True)
            trie_is_end[current] = True
            tracer.log(f"  Mark end of \"{word}\"")
            snap(20, f"Mark end of \"{word}\"")

            # Patch the path
            path_nodes, path_edges = _trace_path(root_id, word, trie_children)
            for nid in path_nodes:
                tracer.patch_node(nid)
            for edge in path_edges:
                tracer.patch_edge(*edge)
            tracer.deselect_all_nodes()
            tracer.deselect_all_edges()
            tracer.log(f"  \"{word}\" added")
            snap(20, f"\"{word}\" added to dictionary")

            # Clear patches
            for nid in path_nodes:
                tracer.depatch_node(nid)
            for edge in path_edges:
                tracer.depatch_edge(*edge)

        # =============================================
        # PHASE 2: SEARCH WITH WILDCARDS
        # =============================================
        tracer.deselect_all_nodes()
        tracer.deselect_all_edges()
        tracer.clear_all_node_errors()
        tracer.log("--- Phase 2: Search patterns ---")
        snap(22, "Phase 2: Search with wildcards")

        for pattern in patterns_to_search:
            tracer.deselect_all_nodes()
            tracer.deselect_all_edges()
            tracer.clear_all_node_errors()
            tracer.clear_all_edge_errors()
            tracer.log(f"search(\"{pattern}\")")
            snap(23, f"search(\"{pattern}\")")

            result = _dfs_search(
                tracer, root_id, pattern, 0,
                trie_children, trie_is_end, steps,
            )

            # Show result
            tracer.deselect_all_nodes()
            tracer.deselect_all_edges()
            tracer.clear_all_node_errors()
            tracer.clear_all_edge_errors()

            if result:
                # Patch a matching path
                match_path = _find_match_path(
                    root_id, pattern, trie_children, trie_is_end
                )
                if match_path:
                    nodes, edges = match_path
                    for nid in nodes:
                        tracer.patch_node(nid)
                    for edge in edges:
                        tracer.patch_edge(*edge)
                tracer.log(f"  search(\"{pattern}\") = True")
                snap(31, f"\"{pattern}\" matched!")
                if match_path:
                    nodes, edges = match_path
                    for nid in nodes:
                        tracer.depatch_node(nid)
                    for edge in edges:
                        tracer.depatch_edge(*edge)
            else:
                tracer.log(f"  search(\"{pattern}\") = False")
                snap(29, f"\"{pattern}\" not found")

        # Final state
        tracer.deselect_all_nodes()
        tracer.deselect_all_edges()
        tracer.clear_all_node_errors()
        tracer.clear_all_edge_errors()
        tracer.log("All operations complete")
        snap(31, "All operations complete")

        return steps


def _dfs_search(
    tracer: TrieTracer,
    node_id: int,
    pattern: str,
    idx: int,
    trie_children: dict[int, dict[str, int]],
    trie_is_end: dict[int, bool],
    steps: list[Step],
) -> bool:
    """Recursive DFS search with wildcard support, generating visualization steps."""

    def snap(line: int, desc: str = "") -> None:
        steps.append(tracer.snapshot(line, desc))

    # Base case: reached end of pattern
    if idx == len(pattern):
        is_end = trie_is_end.get(node_id, False)
        if is_end:
            tracer.log(f"    End of pattern at node {node_id}, is_end=True")
            snap(26, f"Pattern matched! is_end=True")
        else:
            tracer.log(f"    End of pattern at node {node_id}, is_end=False")
            tracer.mark_node_error(node_id)
            snap(26, f"End of pattern but not a word end")
        return is_end

    ch = pattern[idx]

    if ch == '.':
        # Wildcard: try ALL children
        children = trie_children.get(node_id, {})
        if not children:
            tracer.mark_node_error(node_id)
            tracer.log(f"    '.' at pos {idx}: no children to explore")
            snap(29, f"'.' wildcard: no children")
            return False

        # Highlight all children to show wildcard branching
        for child_ch, child_id in children.items():
            tracer.select_node(child_id)
            tracer.select_edge(node_id, child_id)
        tracer.log(f"    '.' at pos {idx}: try all {len(children)} children")
        snap(29, f"'.' wildcard: explore {len(children)} branches")

        # Deselect all, then try each one
        tracer.deselect_all_nodes()
        tracer.deselect_all_edges()

        for child_ch, child_id in children.items():
            tracer.select_node(node_id)
            tracer.select_edge(node_id, child_id)
            tracer.select_node(child_id)
            tracer.log(f"    '.' matches '{child_ch}' -> node {child_id}")
            snap(30, f"'.' matches '{child_ch}'")

            tracer.deselect_node(node_id)

            if _dfs_search(
                tracer, child_id, pattern, idx + 1,
                trie_children, trie_is_end, steps
            ):
                return True

            tracer.deselect_node(child_id)
            tracer.deselect_edge(node_id, child_id)

        tracer.log(f"    '.' at pos {idx}: no branch matched")
        snap(31, f"'.' wildcard: all branches exhausted")
        return False
    else:
        # Exact character match
        children = trie_children.get(node_id, {})
        if ch not in children:
            tracer.mark_node_error(node_id)
            tracer.log(f"    '{ch}' at pos {idx}: not found")
            snap(30, f"'{ch}' not found from node {node_id}")
            return False

        child_id = children[ch]
        tracer.select_node(node_id)
        tracer.select_edge(node_id, child_id)
        tracer.select_node(child_id)
        tracer.log(f"    '{ch}' at pos {idx}: follow to node {child_id}")
        snap(31, f"Follow '{ch}' to node {child_id}")
        tracer.deselect_node(node_id)

        result = _dfs_search(
            tracer, child_id, pattern, idx + 1,
            trie_children, trie_is_end, steps
        )

        tracer.deselect_node(child_id)
        tracer.deselect_edge(node_id, child_id)
        return result


def _trace_path(
    root_id: int, word: str, trie_children: dict[int, dict[str, int]]
) -> tuple[list[int], list[tuple[int, int]]]:
    """Trace the node/edge path for a word in the trie."""
    nodes = [root_id]
    edges = []
    current = root_id
    for ch in word:
        if ch in trie_children.get(current, {}):
            child = trie_children[current][ch]
            edges.append((current, child))
            nodes.append(child)
            current = child
        else:
            break
    return nodes, edges


def _find_match_path(
    root_id: int,
    pattern: str,
    trie_children: dict[int, dict[str, int]],
    trie_is_end: dict[int, bool],
) -> tuple[list[int], list[tuple[int, int]]] | None:
    """Find one matching path through the trie for a pattern (for highlighting)."""

    def dfs(node: int, idx: int, nodes: list[int], edges: list[tuple[int, int]]) -> bool:
        if idx == len(pattern):
            return trie_is_end.get(node, False)
        ch = pattern[idx]
        children = trie_children.get(node, {})
        if ch == '.':
            for child_ch, child_id in children.items():
                nodes.append(child_id)
                edges.append((node, child_id))
                if dfs(child_id, idx + 1, nodes, edges):
                    return True
                nodes.pop()
                edges.pop()
            return False
        else:
            if ch not in children:
                return False
            child_id = children[ch]
            nodes.append(child_id)
            edges.append((node, child_id))
            if dfs(child_id, idx + 1, nodes, edges):
                return True
            nodes.pop()
            edges.pop()
            return False

    nodes: list[int] = [root_id]
    edges: list[tuple[int, int]] = []
    if dfs(root_id, 0, nodes, edges):
        return nodes, edges
    return None
