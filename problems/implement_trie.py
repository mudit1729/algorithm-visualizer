from __future__ import annotations

from core.step import Step
from core.tracer import TrieTracer
from problems.base_problem import Problem

_SOURCE = """\
class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end = False

class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word):
        node = self.root
        for ch in word:
            if ch not in node.children:
                node.children[ch] = TrieNode()
            node = node.children[ch]
        node.is_end = True

    def search(self, word):
        node = self.root
        for ch in word:
            if ch not in node.children:
                return False
            node = node.children[ch]
        return node.is_end

    def startsWith(self, prefix):
        node = self.root
        for ch in prefix:
            if ch not in node.children:
                return False
            node = node.children[ch]
        return True"""


class ImplementTrie(Problem):
    @staticmethod
    def name() -> str:
        return "Implement Trie"

    @staticmethod
    def topic() -> str:
        return "Trie"

    @staticmethod
    def subtopic() -> str:
        return "Basic Operations"

    @staticmethod
    def description() -> str:
        return "LeetCode #208: Implement a trie with insert, search, and startsWith operations."

    @staticmethod
    def long_description() -> str:
        return (
            "A trie (prefix tree) is a tree data structure used to efficiently "
            "store and retrieve keys in a set of strings. Implement the `Trie` "
            "class with:\n\n"
            "- `insert(word)` inserts the string `word` into the trie.\n"
            "- `search(word)` returns `true` if `word` is in the trie.\n"
            "- `startsWith(prefix)` returns `true` if any word starts with `prefix`.\n\n"
            "Example:\n"
            "Input: `insert(\"apple\")`, `search(\"apple\")` -> `true`, "
            "`search(\"app\")` -> `false`, `startsWith(\"app\")` -> `true`\n\n"
            "Constraints:\n\n"
            "- `1 <= word.length, prefix.length <= 2000`\n"
            "- `word` and `prefix` consist only of lowercase English letters"
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
                "insert": ["apple", "app", "ape", "bat", "bar", "ball"],
                "search": ["apple", "app", "apex", "bat", "ban"],
                "prefix": ["ap", "ba", "c"],
            },
        }

        data = presets.get(preset, presets[1])
        words_to_insert = data["insert"]
        words_to_search = data["search"]
        prefixes_to_check = data["prefix"]

        tracer = TrieTracer()
        steps: list[Step] = []

        def snap(line: int, desc: str = "") -> None:
            steps.append(tracer.snapshot(line, desc))

        # --- Internal trie data structure to track node IDs ---
        # Maps (parent_node_id, char) -> child_node_id
        trie_children: dict[int, dict[str, int]] = {}
        trie_is_end: dict[int, bool] = {}

        # Create root node
        root_id = tracer.add_node(label="root")
        trie_children[root_id] = {}
        trie_is_end[root_id] = False

        tracer.log("Initialize empty Trie with root node")
        snap(8, "Create empty Trie")

        # =============================================
        # PHASE 1: INSERT WORDS
        # =============================================
        tracer.log("--- Phase 1: Insert words ---")
        snap(8, "Phase 1: Insert words into Trie")

        for word in words_to_insert:
            tracer.deselect_all_nodes()
            tracer.deselect_all_edges()
            tracer.log(f"insert(\"{word}\")")
            snap(11, f"insert(\"{word}\")")

            current = root_id
            tracer.select_node(current)
            snap(12, f"Start at root")

            for i, ch in enumerate(word):
                # Check if child exists
                if ch in trie_children[current]:
                    # Existing edge — traverse it
                    child_id = trie_children[current][ch]
                    tracer.select_edge(current, child_id)
                    tracer.select_node(child_id)
                    tracer.log(f"  '{ch}' exists, traverse to node {child_id}")
                    snap(15, f"'{ch}' already exists, traverse")
                    tracer.deselect_node(current)
                    tracer.deselect_edge(current, child_id)
                    current = child_id
                else:
                    # Create new node and edge
                    new_id = tracer.add_node(label=ch)
                    trie_children[new_id] = {}
                    trie_is_end[new_id] = False
                    tracer.add_edge(current, new_id, label=ch)
                    trie_children[current][ch] = new_id
                    tracer.select_edge(current, new_id)
                    tracer.select_node(new_id)
                    tracer.log(f"  '{ch}' not found, create node {new_id}")
                    snap(16, f"Create new node for '{ch}'")
                    tracer.deselect_node(current)
                    tracer.deselect_edge(current, new_id)
                    current = new_id

            # Mark end of word
            tracer.set_end(current, True)
            trie_is_end[current] = True
            tracer.log(f"  Mark node {current} as end of \"{word}\"")
            snap(19, f"Mark end of word \"{word}\"")

            # Patch the inserted path to show completion
            path_nodes, path_edges = _trace_word_path(
                root_id, word, trie_children
            )
            for nid in path_nodes:
                tracer.patch_node(nid)
            for edge in path_edges:
                tracer.patch_edge(*edge)
            tracer.deselect_all_nodes()
            tracer.deselect_all_edges()
            tracer.log(f"  \"{word}\" inserted successfully")
            snap(19, f"\"{word}\" inserted")

            # Clear patches for next word
            for nid in path_nodes:
                tracer.depatch_node(nid)
            for edge in path_edges:
                tracer.depatch_edge(*edge)

        # =============================================
        # PHASE 2: SEARCH WORDS
        # =============================================
        tracer.deselect_all_nodes()
        tracer.deselect_all_edges()
        tracer.clear_all_node_errors()
        tracer.log("--- Phase 2: Search words ---")
        snap(21, "Phase 2: Search for words")

        for word in words_to_search:
            tracer.deselect_all_nodes()
            tracer.deselect_all_edges()
            tracer.clear_all_node_errors()
            tracer.log(f"search(\"{word}\")")
            snap(22, f"search(\"{word}\")")

            current = root_id
            tracer.select_node(current)
            found = True
            last_node = current

            for i, ch in enumerate(word):
                if ch in trie_children.get(current, {}):
                    child_id = trie_children[current][ch]
                    tracer.select_edge(current, child_id)
                    tracer.select_node(child_id)
                    tracer.log(f"  '{ch}' found, move to node {child_id}")
                    snap(26, f"Follow '{ch}' to node {child_id}")
                    last_node = child_id
                    current = child_id
                else:
                    # Character not found
                    tracer.mark_node_error(current)
                    tracer.log(f"  '{ch}' NOT found from node {current}")
                    snap(27, f"'{ch}' not found - search fails")
                    found = False
                    break

            if found:
                is_end = trie_is_end.get(current, False)
                if is_end:
                    # Word found - patch the path green
                    path_nodes, path_edges = _trace_word_path(
                        root_id, word, trie_children
                    )
                    tracer.deselect_all_nodes()
                    tracer.deselect_all_edges()
                    for nid in path_nodes:
                        tracer.patch_node(nid)
                    for edge in path_edges:
                        tracer.patch_edge(*edge)
                    tracer.log(f"  \"{word}\" found! (is_end = True)")
                    snap(29, f"\"{word}\" found!")

                    for nid in path_nodes:
                        tracer.depatch_node(nid)
                    for edge in path_edges:
                        tracer.depatch_edge(*edge)
                else:
                    # Prefix exists but not a complete word
                    tracer.mark_node_error(current)
                    tracer.log(f"  \"{word}\" not found (is_end = False)")
                    snap(29, f"\"{word}\" not found (not a complete word)")
            else:
                tracer.log(f"  \"{word}\" not found (missing character)")
                snap(27, f"\"{word}\" not found")

            tracer.clear_all_node_errors()

        # =============================================
        # PHASE 3: PREFIX CHECK
        # =============================================
        tracer.deselect_all_nodes()
        tracer.deselect_all_edges()
        tracer.clear_all_node_errors()
        tracer.log("--- Phase 3: Check prefixes ---")
        snap(31, "Phase 3: startsWith checks")

        for prefix in prefixes_to_check:
            tracer.deselect_all_nodes()
            tracer.deselect_all_edges()
            tracer.clear_all_node_errors()
            tracer.log(f"startsWith(\"{prefix}\")")
            snap(32, f"startsWith(\"{prefix}\")")

            current = root_id
            tracer.select_node(current)
            found = True

            for i, ch in enumerate(prefix):
                if ch in trie_children.get(current, {}):
                    child_id = trie_children[current][ch]
                    tracer.select_edge(current, child_id)
                    tracer.select_node(child_id)
                    tracer.log(f"  '{ch}' found, move to node {child_id}")
                    snap(31, f"Follow '{ch}'")
                    current = child_id
                else:
                    tracer.mark_node_error(current)
                    tracer.log(f"  '{ch}' NOT found from node {current}")
                    snap(32, f"'{ch}' not found - prefix missing")
                    found = False
                    break

            if found:
                path_nodes, path_edges = _trace_word_path(
                    root_id, prefix, trie_children
                )
                tracer.deselect_all_nodes()
                tracer.deselect_all_edges()
                for nid in path_nodes:
                    tracer.patch_node(nid)
                for edge in path_edges:
                    tracer.patch_edge(*edge)
                tracer.log(f"  startsWith(\"{prefix}\") = True")
                snap(32, f"Prefix \"{prefix}\" exists!")

                for nid in path_nodes:
                    tracer.depatch_node(nid)
                for edge in path_edges:
                    tracer.depatch_edge(*edge)
            else:
                tracer.log(f"  startsWith(\"{prefix}\") = False")
                snap(32, f"Prefix \"{prefix}\" not found")

            tracer.clear_all_node_errors()

        # Final cleanup
        tracer.deselect_all_nodes()
        tracer.deselect_all_edges()
        tracer.clear_all_node_errors()
        tracer.log("All operations complete")
        snap(32, "All operations complete")

        return steps


def _trace_word_path(
    root_id: int, word: str, trie_children: dict[int, dict[str, int]]
) -> tuple[list[int], list[tuple[int, int]]]:
    """Return list of node IDs and edge tuples along the path of a word."""
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
