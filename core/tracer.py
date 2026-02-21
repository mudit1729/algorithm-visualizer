from __future__ import annotations

from typing import Any

import math

from core.step import ArrayCell, CellState, GraphEdge, GraphNode, Step


class Board2DTracer:
    """Mutable 2D grid tracer. Manipulate state, then call snapshot() to freeze."""

    def __init__(self, rows: int, cols: int):
        self.rows = rows
        self.cols = cols
        self._values: list[list[Any]] = [[0] * cols for _ in range(rows)]
        self._selected: list[list[bool]] = [[False] * cols for _ in range(rows)]
        self._patched: list[list[bool]] = [[False] * cols for _ in range(rows)]
        self._error: list[list[bool]] = [[False] * cols for _ in range(rows)]
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
                )
                for c in range(self.cols)
            )
            for r in range(self.rows)
        )
        return Step(
            line_number=line_number,
            description=description,
            board=board,
            log_messages=tuple(self._log),
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
            log_messages=tuple(self._log),
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
        self._log: list[str] = []

    def set_label(self, node_id: Any, label: str) -> None:
        self._labels[node_id] = label

    def add_edge(self, source: Any, target: Any) -> None:
        key = (source, target)
        if key not in self._edge_selected:
            self._edges.append(key)
            self._edge_selected[key] = False
            self._edge_patched[key] = False
            self._edge_error[key] = False

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

    def mark_edge_error(self, source: Any, target: Any) -> None:
        self._edge_error[(source, target)] = True

    def clear_edge_error(self, source: Any, target: Any) -> None:
        self._edge_error[(source, target)] = False

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
            )
            for s, t in self._edges
        )
        return Step(
            line_number=line_number,
            description=description,
            graph_nodes=nodes,
            graph_edges=edges,
            log_messages=tuple(self._log),
        )
