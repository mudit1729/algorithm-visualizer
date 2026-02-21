from __future__ import annotations

from collections import deque
from dataclasses import replace
from typing import Any

import math

from core.step import (
    ArrayCell, AuxPanel, AuxPanelItem, CellState, DSUNode,
    GraphEdge, GraphNode, Step, TrieEdge, TrieNode,
)

MAX_LOG_MESSAGES_PER_STEP = 50


def _windowed_logs(logs: list[str]) -> tuple[str, ...]:
    if len(logs) <= MAX_LOG_MESSAGES_PER_STEP:
        return tuple(logs)
    return tuple(logs[-MAX_LOG_MESSAGES_PER_STEP:])


class Board2DTracer:
    """Mutable 2D grid tracer. Manipulate state, then call snapshot() to freeze."""

    def __init__(self, rows: int, cols: int):
        self.rows = rows
        self.cols = cols
        self._values: list[list[Any]] = [[0] * cols for _ in range(rows)]
        self._selected: list[list[bool]] = [[False] * cols for _ in range(rows)]
        self._patched: list[list[bool]] = [[False] * cols for _ in range(rows)]
        self._error: list[list[bool]] = [[False] * cols for _ in range(rows)]
        self._overlay_text: list[list[str]] = [[""] * cols for _ in range(rows)]
        self._overlay_color: list[list[str]] = [[""] * cols for _ in range(rows)]
        self._arrow_dir: list[list[str]] = [[""] * cols for _ in range(rows)]
        self._on_path: list[list[bool]] = [[False] * cols for _ in range(rows)]
        self._log: list[str] = []

    # --- mutations ---

    def set_value(self, row: int, col: int, value: Any) -> None:
        self._values[row][col] = value

    def select(self, row: int, col: int) -> None:
        self._selected[row][col] = True

    def deselect(self, row: int, col: int) -> None:
        self._selected[row][col] = False

    def deselect_all(self) -> None:
        self._selected = [[False] * self.cols for _ in range(self.rows)]

    def patch(self, row: int, col: int) -> None:
        self._patched[row][col] = True

    def depatch(self, row: int, col: int) -> None:
        self._patched[row][col] = False

    def depatch_all(self) -> None:
        self._patched = [[False] * self.cols for _ in range(self.rows)]

    def mark_error(self, row: int, col: int) -> None:
        self._error[row][col] = True

    def clear_error(self, row: int, col: int) -> None:
        self._error[row][col] = False

    def clear_all_errors(self) -> None:
        self._error = [[False] * self.cols for _ in range(self.rows)]

    def set_overlay(self, row: int, col: int, text: str, color: str = "") -> None:
        self._overlay_text[row][col] = text
        self._overlay_color[row][col] = color

    def set_arrow(self, row: int, col: int, direction: str) -> None:
        self._arrow_dir[row][col] = direction

    def mark_on_path(self, row: int, col: int) -> None:
        self._on_path[row][col] = True

    def clear_on_path(self, row: int, col: int) -> None:
        self._on_path[row][col] = False

    def clear_all_paths(self) -> None:
        self._on_path = [[False] * self.cols for _ in range(self.rows)]

    def clear_all_overlays(self) -> None:
        self._overlay_text = [[""] * self.cols for _ in range(self.rows)]
        self._overlay_color = [[""] * self.cols for _ in range(self.rows)]
        self._arrow_dir = [[""] * self.cols for _ in range(self.rows)]

    def log(self, message: str) -> None:
        self._log.append(message)

    # --- snapshot ---

    def snapshot(self, line_number: int, description: str = "") -> Step:
        board = tuple(
            tuple(
                CellState(
                    value=self._values[r][c],
                    selected=self._selected[r][c],
                    patched=self._patched[r][c],
                    error=self._error[r][c],
                    overlay_text=self._overlay_text[r][c],
                    overlay_color=self._overlay_color[r][c],
                    arrow_dir=self._arrow_dir[r][c],
                    on_path=self._on_path[r][c],
                )
                for c in range(self.cols)
            )
            for r in range(self.rows)
        )
        return Step(
            line_number=line_number,
            description=description,
            board=board,
            log_messages=_windowed_logs(self._log),
        )


class Array1DTracer:
    """Mutable 1D array tracer for sorting / search problems."""

    def __init__(self, data: list[Any]):
        self._values: list[Any] = list(data)
        self._selected: list[bool] = [False] * len(data)
        self._patched: list[bool] = [False] * len(data)
        self._error: list[bool] = [False] * len(data)
        self._log: list[str] = []

    @property
    def size(self) -> int:
        return len(self._values)

    def set_value(self, index: int, value: Any) -> None:
        self._values[index] = value

    def swap(self, i: int, j: int) -> None:
        self._values[i], self._values[j] = self._values[j], self._values[i]

    def select(self, index: int) -> None:
        self._selected[index] = True

    def deselect(self, index: int) -> None:
        self._selected[index] = False

    def deselect_all(self) -> None:
        self._selected = [False] * self.size

    def patch(self, index: int) -> None:
        self._patched[index] = True

    def depatch(self, index: int) -> None:
        self._patched[index] = False

    def depatch_all(self) -> None:
        self._patched = [False] * self.size

    def mark_error(self, index: int) -> None:
        self._error[index] = True

    def clear_error(self, index: int) -> None:
        self._error[index] = False

    def clear_all_errors(self) -> None:
        self._error = [False] * self.size

    def log(self, message: str) -> None:
        self._log.append(message)

    def snapshot(self, line_number: int, description: str = "") -> Step:
        array = tuple(
            ArrayCell(
                value=self._values[i],
                selected=self._selected[i],
                patched=self._patched[i],
                error=self._error[i],
            )
            for i in range(self.size)
        )
        return Step(
            line_number=line_number,
            description=description,
            array=array,
            log_messages=_windowed_logs(self._log),
        )


class GraphTracer:
    """Mutable graph tracer with nodes and edges."""

    def __init__(self, node_ids: list[Any], directed: bool = True):
        self._directed = directed
        self._node_ids: list[Any] = list(node_ids)
        self._labels: dict[Any, str] = {nid: str(nid) for nid in node_ids}
        self._node_selected: dict[Any, bool] = {nid: False for nid in node_ids}
        self._node_patched: dict[Any, bool] = {nid: False for nid in node_ids}
        self._node_error: dict[Any, bool] = {nid: False for nid in node_ids}
        self._node_color: dict[Any, str] = {nid: "" for nid in node_ids}
        self._node_badge: dict[Any, str] = {nid: "" for nid in node_ids}
        self._node_badge_color: dict[Any, str] = {nid: "" for nid in node_ids}
        self._node_group: dict[Any, int | None] = {nid: None for nid in node_ids}
        # Pre-compute circular layout positions (0..1 range)
        self._positions: dict[Any, tuple[float, float]] = {}
        n = len(node_ids)
        for i, nid in enumerate(node_ids):
            angle = 2 * math.pi * i / n - math.pi / 2  # start from top
            self._positions[nid] = (0.5 + 0.38 * math.cos(angle),
                                     0.5 + 0.38 * math.sin(angle))

        self._edges: list[tuple[Any, Any]] = []
        self._edge_selected: dict[tuple[Any, Any], bool] = {}
        self._edge_patched: dict[tuple[Any, Any], bool] = {}
        self._edge_error: dict[tuple[Any, Any], bool] = {}
        self._edge_weight: dict[tuple[Any, Any], float | None] = {}
        self._edge_label: dict[tuple[Any, Any], str] = {}
        self._edge_class: dict[tuple[Any, Any], str] = {}
        self._edge_curve_offset: dict[tuple[Any, Any], float] = {}
        self._log: list[str] = []

    def set_label(self, node_id: Any, label: str) -> None:
        self._labels[node_id] = label

    def add_edge(self, source: Any, target: Any, weight: float | None = None) -> None:
        key = (source, target)
        if key not in self._edge_selected:
            self._edges.append(key)
            self._edge_selected[key] = False
            self._edge_patched[key] = False
            self._edge_error[key] = False
            self._edge_weight[key] = weight
            self._edge_label[key] = ""
            self._edge_class[key] = ""
            self._edge_curve_offset[key] = 0.0

    def set_edge_weight(self, source: Any, target: Any, weight: float | None) -> None:
        self._edge_weight[(source, target)] = weight

    def set_edge_label(self, source: Any, target: Any, label: str) -> None:
        self._edge_label[(source, target)] = label

    def set_edge_class(self, source: Any, target: Any, cls: str) -> None:
        self._edge_class[(source, target)] = cls

    def set_edge_curve_offset(self, source: Any, target: Any, offset: float) -> None:
        self._edge_curve_offset[(source, target)] = offset

    def set_node_badge(self, node_id: Any, badge: str, color: str = "") -> None:
        self._node_badge[node_id] = badge
        self._node_badge_color[node_id] = color

    def set_node_group(self, node_id: Any, group: int | None) -> None:
        self._node_group[node_id] = group

    def select_node(self, node_id: Any) -> None:
        self._node_selected[node_id] = True

    def deselect_node(self, node_id: Any) -> None:
        self._node_selected[node_id] = False

    def deselect_all_nodes(self) -> None:
        for nid in self._node_ids:
            self._node_selected[nid] = False

    def patch_node(self, node_id: Any) -> None:
        self._node_patched[node_id] = True

    def depatch_node(self, node_id: Any) -> None:
        self._node_patched[node_id] = False

    def depatch_all_nodes(self) -> None:
        for nid in self._node_ids:
            self._node_patched[nid] = False

    def mark_node_error(self, node_id: Any) -> None:
        self._node_error[node_id] = True

    def clear_node_error(self, node_id: Any) -> None:
        self._node_error[node_id] = False

    def clear_all_node_errors(self) -> None:
        for nid in self._node_ids:
            self._node_error[nid] = False

    def set_node_color(self, node_id: Any, color: str) -> None:
        self._node_color[node_id] = color

    def select_edge(self, source: Any, target: Any) -> None:
        self._edge_selected[(source, target)] = True

    def deselect_edge(self, source: Any, target: Any) -> None:
        self._edge_selected[(source, target)] = False

    def deselect_all_edges(self) -> None:
        for key in self._edges:
            self._edge_selected[key] = False

    def patch_edge(self, source: Any, target: Any) -> None:
        self._edge_patched[(source, target)] = True

    def depatch_edge(self, source: Any, target: Any) -> None:
        self._edge_patched[(source, target)] = False

    def depatch_all_edges(self) -> None:
        for key in self._edges:
            self._edge_patched[key] = False

    def mark_edge_error(self, source: Any, target: Any) -> None:
        self._edge_error[(source, target)] = True

    def clear_edge_error(self, source: Any, target: Any) -> None:
        self._edge_error[(source, target)] = False

    def clear_all_edge_errors(self) -> None:
        for key in self._edges:
            self._edge_error[key] = False

    def set_layered_layout(self) -> None:
        """Compute a layered (Sugiyama-style) layout for DAGs."""
        adj: dict[Any, list[Any]] = {nid: [] for nid in self._node_ids}
        in_degree: dict[Any, int] = {nid: 0 for nid in self._node_ids}
        for s, t in self._edges:
            adj[s].append(t)
            in_degree[t] = in_degree.get(t, 0) + 1

        layer: dict[Any, int] = {}
        queue = deque([nid for nid in self._node_ids if in_degree[nid] == 0])
        for nid in queue:
            layer[nid] = 0

        while queue:
            u = queue.popleft()
            for v in adj[u]:
                layer[v] = max(layer.get(v, 0), layer[u] + 1)
                in_degree[v] -= 1
                if in_degree[v] == 0:
                    queue.append(v)

        # Handle nodes not reached (cycles) — place at bottom
        max_layer = max(layer.values()) if layer else 0
        for nid in self._node_ids:
            if nid not in layer:
                max_layer += 1
                layer[nid] = max_layer

        layers: dict[int, list[Any]] = {}
        for nid, lyr in layer.items():
            layers.setdefault(lyr, []).append(nid)

        total_layers = max(layers.keys()) + 1 if layers else 1
        for lyr, nids in layers.items():
            for i, nid in enumerate(nids):
                x = (i + 1) / (len(nids) + 1)
                y = (lyr + 0.5) / total_layers
                self._positions[nid] = (x, y)

    def log(self, message: str) -> None:
        self._log.append(message)

    def snapshot(self, line_number: int, description: str = "") -> Step:
        nodes = tuple(
            GraphNode(
                id=nid,
                label=self._labels[nid],
                selected=self._node_selected[nid],
                patched=self._node_patched[nid],
                error=self._node_error[nid],
                color=self._node_color[nid],
                x=self._positions[nid][0],
                y=self._positions[nid][1],
                badge=self._node_badge[nid],
                badge_color=self._node_badge_color[nid],
                group=self._node_group[nid],
            )
            for nid in self._node_ids
        )
        edges = tuple(
            GraphEdge(
                source=s,
                target=t,
                selected=self._edge_selected[(s, t)],
                patched=self._edge_patched[(s, t)],
                error=self._edge_error[(s, t)],
                directed=self._directed,
                weight=self._edge_weight[(s, t)],
                label=self._edge_label[(s, t)],
                edge_class=self._edge_class[(s, t)],
                curve_offset=self._edge_curve_offset[(s, t)],
            )
            for s, t in self._edges
        )
        return Step(
            line_number=line_number,
            description=description,
            graph_nodes=nodes,
            graph_edges=edges,
            log_messages=_windowed_logs(self._log),
        )


class AuxPanelTracer:
    """Manages auxiliary display panels (queues, stacks, visited sets)."""

    def __init__(self) -> None:
        self._panels: dict[str, list[dict]] = {}
        self._panel_order: list[str] = []

    def add_panel(self, title: str) -> None:
        if title not in self._panels:
            self._panels[title] = []
            self._panel_order.append(title)

    def push(self, panel_title: str, label: str, value: Any = "") -> None:
        self._panels[panel_title].append({
            "label": label, "value": value,
            "selected": False, "patched": False, "error": False,
        })

    def pop(self, panel_title: str) -> dict | None:
        items = self._panels.get(panel_title, [])
        return items.pop() if items else None

    def pop_front(self, panel_title: str) -> dict | None:
        items = self._panels.get(panel_title, [])
        return items.pop(0) if items else None

    def clear_panel(self, panel_title: str) -> None:
        self._panels[panel_title] = []

    def select_item(self, panel_title: str, index: int) -> None:
        self._panels[panel_title][index]["selected"] = True

    def deselect_all_items(self, panel_title: str) -> None:
        for item in self._panels.get(panel_title, []):
            item["selected"] = False

    def patch_item(self, panel_title: str, index: int) -> None:
        self._panels[panel_title][index]["patched"] = True

    def set_items(self, panel_title: str, items: list[tuple[str, Any]]) -> None:
        """Replace entire panel contents. Useful for 'visited set' style panels."""
        self._panels[panel_title] = [
            {"label": label, "value": value,
             "selected": False, "patched": False, "error": False}
            for label, value in items
        ]

    def snapshot(self) -> tuple[AuxPanel, ...]:
        return tuple(
            AuxPanel(
                title=title,
                items=tuple(
                    AuxPanelItem(
                        label=item["label"],
                        value=item["value"],
                        selected=item["selected"],
                        patched=item["patched"],
                        error=item["error"],
                    )
                    for item in self._panels[title]
                ),
            )
            for title in self._panel_order
        )


class DSUTracer:
    """Mutable DSU tracer. Visualizes Union-Find forest."""

    def __init__(self, node_ids: list[Any]) -> None:
        self._node_ids = list(node_ids)
        self._labels: dict[Any, str] = {nid: str(nid) for nid in node_ids}
        self._parent: dict[Any, Any] = {nid: nid for nid in node_ids}
        self._rank: dict[Any, int] = {nid: 0 for nid in node_ids}
        self._selected: dict[Any, bool] = {nid: False for nid in node_ids}
        self._patched: dict[Any, bool] = {nid: False for nid in node_ids}
        self._error: dict[Any, bool] = {nid: False for nid in node_ids}
        self._log: list[str] = []

    def make_set(self, node_id: Any, label: str = "") -> None:
        if node_id not in self._parent:
            self._node_ids.append(node_id)
            self._parent[node_id] = node_id
            self._rank[node_id] = 0
            self._labels[node_id] = label or str(node_id)
            self._selected[node_id] = False
            self._patched[node_id] = False
            self._error[node_id] = False

    def set_parent(self, node_id: Any, parent_id: Any) -> None:
        self._parent[node_id] = parent_id

    def set_rank(self, node_id: Any, rank: int) -> None:
        self._rank[node_id] = rank

    def set_label(self, node_id: Any, label: str) -> None:
        self._labels[node_id] = label

    def select(self, node_id: Any) -> None:
        self._selected[node_id] = True

    def deselect(self, node_id: Any) -> None:
        self._selected[node_id] = False

    def deselect_all(self) -> None:
        for nid in self._node_ids:
            self._selected[nid] = False

    def patch(self, node_id: Any) -> None:
        self._patched[node_id] = True

    def depatch_all(self) -> None:
        for nid in self._node_ids:
            self._patched[nid] = False

    def mark_error(self, node_id: Any) -> None:
        self._error[node_id] = True

    def clear_all_errors(self) -> None:
        for nid in self._node_ids:
            self._error[nid] = False

    def log(self, message: str) -> None:
        self._log.append(message)

    def snapshot(self, line_number: int, description: str = "") -> Step:
        dsu_nodes = tuple(
            DSUNode(
                id=nid,
                label=self._labels[nid],
                parent_id=None if self._parent[nid] == nid else self._parent[nid],
                rank=self._rank[nid],
                selected=self._selected[nid],
                patched=self._patched[nid],
                error=self._error[nid],
            )
            for nid in self._node_ids
        )
        return Step(
            line_number=line_number,
            description=description,
            dsu_nodes=dsu_nodes,
            log_messages=_windowed_logs(self._log),
        )


class TrieTracer:
    """Mutable Trie tracer with automatic tree layout."""

    def __init__(self) -> None:
        self._node_ids: list[Any] = []
        self._labels: dict[Any, str] = {}
        self._selected: dict[Any, bool] = {}
        self._patched: dict[Any, bool] = {}
        self._error: dict[Any, bool] = {}
        self._is_end: dict[Any, bool] = {}
        self._positions: dict[Any, tuple[float, float]] = {}
        self._edges: list[tuple[Any, Any]] = []
        self._edge_labels: dict[tuple[Any, Any], str] = {}
        self._edge_selected: dict[tuple[Any, Any], bool] = {}
        self._edge_patched: dict[tuple[Any, Any], bool] = {}
        self._edge_error: dict[tuple[Any, Any], bool] = {}
        self._children: dict[Any, list[Any]] = {}
        self._log: list[str] = []
        self._next_id = 0

    def add_node(self, node_id: Any = None, label: str = "", is_end: bool = False) -> Any:
        if node_id is None:
            node_id = self._next_id
            self._next_id += 1
        self._node_ids.append(node_id)
        self._labels[node_id] = label
        self._selected[node_id] = False
        self._patched[node_id] = False
        self._error[node_id] = False
        self._is_end[node_id] = is_end
        self._children[node_id] = []
        return node_id

    def add_edge(self, source: Any, target: Any, label: str = "") -> None:
        key = (source, target)
        if key not in self._edge_selected:
            self._edges.append(key)
            self._edge_labels[key] = label
            self._edge_selected[key] = False
            self._edge_patched[key] = False
            self._edge_error[key] = False
            if target not in self._children.get(source, []):
                self._children.setdefault(source, []).append(target)

    def set_end(self, node_id: Any, is_end: bool = True) -> None:
        self._is_end[node_id] = is_end

    def select_node(self, node_id: Any) -> None:
        self._selected[node_id] = True

    def deselect_node(self, node_id: Any) -> None:
        self._selected[node_id] = False

    def deselect_all_nodes(self) -> None:
        for nid in self._node_ids:
            self._selected[nid] = False

    def patch_node(self, node_id: Any) -> None:
        self._patched[node_id] = True

    def depatch_node(self, node_id: Any) -> None:
        self._patched[node_id] = False

    def select_edge(self, source: Any, target: Any) -> None:
        self._edge_selected[(source, target)] = True

    def deselect_edge(self, source: Any, target: Any) -> None:
        self._edge_selected[(source, target)] = False

    def deselect_all_edges(self) -> None:
        for key in self._edges:
            self._edge_selected[key] = False

    def patch_edge(self, source: Any, target: Any) -> None:
        self._edge_patched[(source, target)] = True

    def depatch_edge(self, source: Any, target: Any) -> None:
        self._edge_patched[(source, target)] = False

    def depatch_all_nodes(self) -> None:
        for nid in self._node_ids:
            self._patched[nid] = False

    def depatch_all_edges(self) -> None:
        for key in self._edges:
            self._edge_patched[key] = False

    def mark_node_error(self, node_id: Any) -> None:
        self._error[node_id] = True

    def clear_node_error(self, node_id: Any) -> None:
        self._error[node_id] = False

    def clear_all_node_errors(self) -> None:
        for nid in self._node_ids:
            self._error[nid] = False

    def mark_edge_error(self, source: Any, target: Any) -> None:
        self._edge_error[(source, target)] = True

    def clear_edge_error(self, source: Any, target: Any) -> None:
        self._edge_error[(source, target)] = False

    def clear_all_edge_errors(self) -> None:
        for key in self._edges:
            self._edge_error[key] = False

    def log(self, message: str) -> None:
        self._log.append(message)

    def _compute_layout(self) -> None:
        """Compute tree layout positions in [0,1] range."""
        if not self._node_ids:
            return
        targets = set(t for _, t in self._edges)
        roots = [nid for nid in self._node_ids if nid not in targets]
        if not roots:
            roots = [self._node_ids[0]]

        def depth(nid: Any) -> int:
            ch = self._children.get(nid, [])
            return 1 + max((depth(c) for c in ch), default=0)

        def count_leaves(nid: Any) -> int:
            ch = self._children.get(nid, [])
            if not ch:
                return 1
            return sum(count_leaves(c) for c in ch)

        max_d = max(depth(r) for r in roots)

        def layout(nid: Any, x_min: float, x_max: float, level: int) -> None:
            y = (level + 0.5) / max(max_d, 1)
            ch = self._children.get(nid, [])
            if not ch:
                self._positions[nid] = ((x_min + x_max) / 2, y)
                return
            self._positions[nid] = ((x_min + x_max) / 2, y)
            child_leaves = [count_leaves(c) for c in ch]
            total = sum(child_leaves)
            cx = x_min
            for i, cid in enumerate(ch):
                cw = (child_leaves[i] / total) * (x_max - x_min) if total else (x_max - x_min) / len(ch)
                layout(cid, cx, cx + cw, level + 1)
                cx += cw

        total_leaves = sum(count_leaves(r) for r in roots)
        rx = 0.05
        for root in roots:
            rw = (count_leaves(root) / total_leaves) * 0.9 if total_leaves else 0.9
            layout(root, rx, rx + rw, 0)
            rx += rw

    def snapshot(self, line_number: int, description: str = "") -> Step:
        self._compute_layout()
        trie_nodes = tuple(
            TrieNode(
                id=nid,
                label=self._labels[nid],
                x=self._positions.get(nid, (0.5, 0.5))[0],
                y=self._positions.get(nid, (0.5, 0.5))[1],
                selected=self._selected[nid],
                patched=self._patched[nid],
                error=self._error[nid],
                is_end=self._is_end[nid],
            )
            for nid in self._node_ids
        )
        trie_edges = tuple(
            TrieEdge(
                source=s,
                target=t,
                label=self._edge_labels.get((s, t), ""),
                selected=self._edge_selected[(s, t)],
                patched=self._edge_patched[(s, t)],
                error=self._edge_error[(s, t)],
            )
            for s, t in self._edges
        )
        return Step(
            line_number=line_number,
            description=description,
            trie_nodes=trie_nodes,
            trie_edges=trie_edges,
            log_messages=_windowed_logs(self._log),
        )


def combine_step(base_step: Step, aux_tracer: AuxPanelTracer | None = None) -> Step:
    """Attach aux panel data to an existing step."""
    if aux_tracer:
        return replace(base_step, aux_panels=aux_tracer.snapshot())
    return base_step
