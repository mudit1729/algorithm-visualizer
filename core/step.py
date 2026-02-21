from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class CellState:
    value: Any = 0
    selected: bool = False
    patched: bool = False
    error: bool = False

    def to_dict(self) -> dict:
        return {
            "value": self.value,
            "selected": self.selected,
            "patched": self.patched,
            "error": self.error,
        }


@dataclass(frozen=True)
class ArrayCell:
    value: Any = 0
    selected: bool = False
    patched: bool = False
    error: bool = False

    def to_dict(self) -> dict:
        return {
            "value": self.value,
            "selected": self.selected,
            "patched": self.patched,
            "error": self.error,
        }


@dataclass(frozen=True)
class GraphNode:
    id: Any = 0
    label: str = ""
    selected: bool = False
    patched: bool = False
    error: bool = False
    color: str = ""  # optional override color
    x: float = 0.0
    y: float = 0.0

    def to_dict(self) -> dict:
        d = {
            "id": self.id,
            "label": self.label,
            "selected": self.selected,
            "patched": self.patched,
            "error": self.error,
            "x": self.x,
            "y": self.y,
        }
        if self.color:
            d["color"] = self.color
        return d


@dataclass(frozen=True)
class GraphEdge:
    source: Any = 0
    target: Any = 0
    selected: bool = False
    patched: bool = False
    error: bool = False
    directed: bool = True

    def to_dict(self) -> dict:
        return {
            "source": self.source,
            "target": self.target,
            "selected": self.selected,
            "patched": self.patched,
            "error": self.error,
            "directed": self.directed,
        }


@dataclass(frozen=True)
class Step:
    line_number: int
    description: str = ""
    board: tuple[tuple[CellState, ...], ...] | None = None
    array: tuple[ArrayCell, ...] | None = None
    graph_nodes: tuple[GraphNode, ...] | None = None
    graph_edges: tuple[GraphEdge, ...] | None = None
    log_messages: tuple[str, ...] = ()

    def to_dict(self) -> dict:
        d: dict[str, Any] = {
            "line_number": self.line_number,
            "description": self.description,
            "log_messages": list(self.log_messages),
        }
        if self.board is not None:
            d["board"] = [[c.to_dict() for c in row] for row in self.board]
        if self.array is not None:
            d["array"] = [c.to_dict() for c in self.array]
        if self.graph_nodes is not None:
            d["graph_nodes"] = [n.to_dict() for n in self.graph_nodes]
            d["graph_edges"] = [e.to_dict() for e in (self.graph_edges or ())]
        return d
