"""UCOS-EPIC-002 (Terminal T2) — Universal Knowledge Graph visualization.

Deterministic, dependency-free exporters that render a :class:`KnowledgeGraph`
into portable, human- and tool-consumable formats. Nothing here mutates the graph
or the corpus (DP-03); every exporter emits nodes/edges in stable identifier order
so output is reproducible (determinism gate).

Formats:
    * ``to_node_link_json`` — a JSON node-link document (D3 / generic).
    * ``to_cytoscape`` — Cytoscape.js ``elements`` (portal rendering).
    * ``to_dot`` — Graphviz DOT.
    * ``to_mermaid`` — Mermaid ``flowchart`` source (Markdown-embeddable).
"""

from __future__ import annotations

import json
from typing import Any

from engine.graph.model import KnowledgeGraph

# A compact, deterministic palette keyed by node kind (portal/Graphviz styling).
_KIND_COLOURS: dict[str, str] = {
    "Artifact": "#4C78A8",
    "Volume": "#54A24B",
    "Category": "#E45756",
    "Program": "#F58518",
    "Signal": "#B279A2",
    "CertificationDomain": "#9D755D",
}
_DEFAULT_COLOUR = "#BAB0AC"


def to_node_link_json(graph: KnowledgeGraph, *, indent: int | None = 2) -> str:
    """Render ``graph`` as a JSON node-link document (deterministic)."""
    document = {
        "provenance": graph.provenance.to_dict(),
        "order": graph.order(),
        "size": graph.size(),
        "nodes": [node.to_dict() for node in graph.nodes()],
        "links": [edge.to_dict() for edge in graph.edges()],
    }
    return json.dumps(document, indent=indent, sort_keys=True)


def to_cytoscape(graph: KnowledgeGraph, *, indent: int | None = 2) -> str:
    """Render ``graph`` as a Cytoscape.js ``elements`` document."""
    elements: list[dict[str, Any]] = []
    for node in graph.nodes():
        elements.append(
            {
                "group": "nodes",
                "data": {
                    "id": node.node_id,
                    "label": node.label,
                    "kind": node.kind,
                    "version": node.version,
                    "colour": _KIND_COLOURS.get(node.kind, _DEFAULT_COLOUR),
                },
            }
        )
    for edge in graph.edges():
        elements.append(
            {
                "group": "edges",
                "data": {
                    "id": edge.edge_id,
                    "source": edge.source,
                    "target": edge.target,
                    "label": edge.type,
                },
            }
        )
    return json.dumps({"elements": elements}, indent=indent, sort_keys=True)


def _dot_escape(text: str) -> str:
    return text.replace("\\", "\\\\").replace('"', '\\"')


def to_dot(graph: KnowledgeGraph, *, name: str = "UniversalKnowledgeGraph") -> str:
    """Render ``graph`` as Graphviz DOT (deterministic node/edge ordering)."""
    lines: list[str] = [f'digraph "{_dot_escape(name)}" {{']
    lines.append('  node [style=filled, shape=box, fontname="Helvetica"];')
    for node in graph.nodes():
        colour = _KIND_COLOURS.get(node.kind, _DEFAULT_COLOUR)
        label = _dot_escape(f"{node.label}\\n[{node.kind}]")
        lines.append(f'  "{_dot_escape(node.node_id)}" [label="{label}", fillcolor="{colour}"];')
    for edge in graph.edges():
        label = _dot_escape(edge.type)
        lines.append(
            f'  "{_dot_escape(edge.source)}" -> "{_dot_escape(edge.target)}" [label="{label}"];'
        )
    lines.append("}")
    return "\n".join(lines)


def _mermaid_id(identifier: str, index: int) -> str:
    """A Mermaid-safe node id (Mermaid ids cannot contain most punctuation)."""
    return f"n{index}"


def to_mermaid(graph: KnowledgeGraph, *, direction: str = "LR") -> str:
    """Render ``graph`` as Mermaid ``flowchart`` source (Markdown-embeddable)."""
    if direction not in {"LR", "TB", "RL", "BT"}:
        direction = "LR"
    index_of: dict[str, str] = {}
    for i, node in enumerate(graph.nodes()):
        index_of[node.node_id] = _mermaid_id(node.node_id, i)

    lines: list[str] = [f"flowchart {direction}"]
    for node in graph.nodes():
        safe_label = node.label.replace('"', "'")
        lines.append(f'    {index_of[node.node_id]}["{safe_label}"]')
    for edge in graph.edges():
        src = index_of.get(edge.source)
        tgt = index_of.get(edge.target)
        if src is None or tgt is None:
            continue
        label = edge.type.replace("|", "/")
        lines.append(f"    {src} -->|{label}| {tgt}")
    return "\n".join(lines)


#: Supported visualization format names (for the CLI ``--format`` option).
VISUALIZATION_FORMATS: tuple[str, ...] = ("json", "cytoscape", "dot", "mermaid")


def render(graph: KnowledgeGraph, fmt: str) -> str:
    """Render ``graph`` in a named format (``json``/``cytoscape``/``dot``/``mermaid``)."""
    match fmt:
        case "json":
            return to_node_link_json(graph)
        case "cytoscape":
            return to_cytoscape(graph)
        case "dot":
            return to_dot(graph)
        case "mermaid":
            return to_mermaid(graph)
        case _:
            raise ValueError(f"unknown visualization format: {fmt!r}")


__all__ = [
    "to_node_link_json",
    "to_cytoscape",
    "to_dot",
    "to_mermaid",
    "render",
    "VISUALIZATION_FORMATS",
]
