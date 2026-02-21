from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class CellState:
    value: Any = 0
    selected: bool = False
    patched: bool = False
    error: bool = False
    overlay_text: str = ""
    overlay_color: str = ""
    arrow_dir: str = ""
    on_path: bool = False

    def to_dict(self) -> dict:
        d = {
            "value": self.value,
            "selected": self.selected,
            "patched": self.patched,
            "error": self.error,
        }
        if self.overlay_text:
            d["overlay_text"] = self.overlay_text
        if self.overlay_color:
            d["overlay_color"] = self.overlay_color
        if self.arrow_dir:
            d["arrow_dir"] = self.arrow_dir
        if self.on_path:
            d["on_path"] = self.on_path
        return d


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
    color: str = ""
    x: float = 0.0
    y: float = 0.0
    badge: str = ""
    badge_color: str = ""
    group: int | None = None

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
        if self.badge:
            d["badge"] = self.badge
        if self.badge_color:
            d["badge_color"] = self.badge_color
        if self.group is not None:
            d["group"] = self.group
        return d


@dataclass(frozen=True)
class GraphEdge:
    source: Any = 0
    target: Any = 0
    selected: bool = False
    patched: bool = False
    error: bool = False
    directed: bool = True
    weight: float | None = None
    label: str = ""
    edge_class: str = ""
    curve_offset: float = 0.0

    def to_dict(self) -> dict:
        d = {
            "source": self.source,
            "target": self.target,
            "selected": self.selected,
            "patched": self.patched,
            "error": self.error,
            "directed": self.directed,
        }
        if self.weight is not None:
            d["weight"] = self.weight
        if self.label:
            d["label"] = self.label
        if self.edge_class:
            d["edge_class"] = self.edge_class
        if self.curve_offset != 0.0:
            d["curve_offset"] = self.curve_offset
        return d


@dataclass(frozen=True)
class AuxPanelItem:
    label: str = ""
    value: Any = ""
    selected: bool = False
    patched: bool = False
    error: bool = False

    def to_dict(self) -> dict:
        return {
            "label": self.label,
            "value": self.value,
            "selected": self.selected,
            "patched": self.patched,
            "error": self.error,
        }


@dataclass(frozen=True)
class AuxPanel:
    title: str = ""
    items: tuple[AuxPanelItem, ...] = ()

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "items": [item.to_dict() for item in self.items],
        }


@dataclass(frozen=True)
class DSUNode:
    id: Any = 0
    label: str = ""
    parent_id: Any = None
    rank: int = 0
    selected: bool = False
    patched: bool = False
    error: bool = False

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "label": self.label,
            "parent_id": self.parent_id,
            "rank": self.rank,
            "selected": self.selected,
            "patched": self.patched,
            "error": self.error,
        }


@dataclass(frozen=True)
class TrieNode:
    id: Any = 0
    label: str = ""
    x: float = 0.0
    y: float = 0.0
    selected: bool = False
    patched: bool = False
    error: bool = False
    is_end: bool = False

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "label": self.label,
            "x": self.x,
            "y": self.y,
            "selected": self.selected,
            "patched": self.patched,
            "error": self.error,
            "is_end": self.is_end,
        }


@dataclass(frozen=True)
class TrieEdge:
    source: Any = 0
    target: Any = 0
    label: str = ""
    selected: bool = False
    patched: bool = False
    error: bool = False

    def to_dict(self) -> dict:
        return {
            "source": self.source,
            "target": self.target,
            "label": self.label,
            "selected": self.selected,
            "patched": self.patched,
            "error": self.error,
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
    aux_panels: tuple[AuxPanel, ...] = ()
    dsu_nodes: tuple[DSUNode, ...] | None = None
    trie_nodes: tuple[TrieNode, ...] | None = None
    trie_edges: tuple[TrieEdge, ...] | None = None

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
        if self.aux_panels:
            d["aux_panels"] = [p.to_dict() for p in self.aux_panels]
        if self.dsu_nodes is not None:
            d["dsu_nodes"] = [n.to_dict() for n in self.dsu_nodes]
        if self.trie_nodes is not None:
            d["trie_nodes"] = [n.to_dict() for n in self.trie_nodes]
            d["trie_edges"] = [e.to_dict() for e in (self.trie_edges or ())]
        return d
