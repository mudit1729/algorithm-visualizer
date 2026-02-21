from __future__ import annotations

from dataclasses import dataclass
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

    def to_dict(self, compact: bool = False) -> dict:
        d = {
            "value": self.value,
        }
        if not compact or self.selected:
            d["selected"] = self.selected
        if not compact or self.patched:
            d["patched"] = self.patched
        if not compact or self.error:
            d["error"] = self.error
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

    def to_dict(self, compact: bool = False) -> dict:
        d = {
            "value": self.value,
        }
        if not compact or self.selected:
            d["selected"] = self.selected
        if not compact or self.patched:
            d["patched"] = self.patched
        if not compact or self.error:
            d["error"] = self.error
        return d


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

    def to_dict(self, compact: bool = False) -> dict:
        d = {
            "id": self.id,
            "label": self.label,
            "x": self.x,
            "y": self.y,
        }
        if not compact or self.selected:
            d["selected"] = self.selected
        if not compact or self.patched:
            d["patched"] = self.patched
        if not compact or self.error:
            d["error"] = self.error
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

    def to_dict(self, compact: bool = False) -> dict:
        d = {
            "source": self.source,
            "target": self.target,
        }
        if not compact or self.selected:
            d["selected"] = self.selected
        if not compact or self.patched:
            d["patched"] = self.patched
        if not compact or self.error:
            d["error"] = self.error
        if not compact or self.directed is not True:
            d["directed"] = self.directed
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

    def to_dict(self, compact: bool = False) -> dict:
        d = {
            "label": self.label,
            "value": self.value,
        }
        if not compact or self.selected:
            d["selected"] = self.selected
        if not compact or self.patched:
            d["patched"] = self.patched
        if not compact or self.error:
            d["error"] = self.error
        return d


@dataclass(frozen=True)
class AuxPanel:
    title: str = ""
    items: tuple[AuxPanelItem, ...] = ()

    def to_dict(self, compact: bool = False) -> dict:
        return {
            "title": self.title,
            "items": [item.to_dict(compact=compact) for item in self.items],
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

    def to_dict(self, compact: bool = False) -> dict:
        d = {
            "id": self.id,
            "label": self.label,
        }
        if not compact or self.parent_id is not None:
            d["parent_id"] = self.parent_id
        if not compact or self.rank != 0:
            d["rank"] = self.rank
        if not compact or self.selected:
            d["selected"] = self.selected
        if not compact or self.patched:
            d["patched"] = self.patched
        if not compact or self.error:
            d["error"] = self.error
        return d


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

    def to_dict(self, compact: bool = False) -> dict:
        d = {
            "id": self.id,
            "x": self.x,
            "y": self.y,
        }
        if not compact or self.label:
            d["label"] = self.label
        if not compact or self.selected:
            d["selected"] = self.selected
        if not compact or self.patched:
            d["patched"] = self.patched
        if not compact or self.error:
            d["error"] = self.error
        if not compact or self.is_end:
            d["is_end"] = self.is_end
        return d


@dataclass(frozen=True)
class TrieEdge:
    source: Any = 0
    target: Any = 0
    label: str = ""
    selected: bool = False
    patched: bool = False
    error: bool = False

    def to_dict(self, compact: bool = False) -> dict:
        d = {
            "source": self.source,
            "target": self.target,
        }
        if not compact or self.label:
            d["label"] = self.label
        if not compact or self.selected:
            d["selected"] = self.selected
        if not compact or self.patched:
            d["patched"] = self.patched
        if not compact or self.error:
            d["error"] = self.error
        return d


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

    def to_dict(self, compact: bool = False) -> dict:
        d: dict[str, Any] = {
            "line_number": self.line_number,
        }
        if not compact or self.description:
            d["description"] = self.description
        if not compact or self.log_messages:
            d["log_messages"] = list(self.log_messages)
        if self.board is not None:
            d["board"] = [[c.to_dict(compact=compact) for c in row] for row in self.board]
        if self.array is not None:
            d["array"] = [c.to_dict(compact=compact) for c in self.array]
        if self.graph_nodes is not None:
            d["graph_nodes"] = [n.to_dict(compact=compact) for n in self.graph_nodes]
            if not compact or self.graph_edges:
                d["graph_edges"] = [e.to_dict(compact=compact) for e in (self.graph_edges or ())]
        if self.aux_panels:
            d["aux_panels"] = [p.to_dict(compact=compact) for p in self.aux_panels]
        if self.dsu_nodes is not None:
            d["dsu_nodes"] = [n.to_dict(compact=compact) for n in self.dsu_nodes]
        if self.trie_nodes is not None:
            d["trie_nodes"] = [n.to_dict(compact=compact) for n in self.trie_nodes]
            if not compact or self.trie_edges:
                d["trie_edges"] = [e.to_dict(compact=compact) for e in (self.trie_edges or ())]
        return d
