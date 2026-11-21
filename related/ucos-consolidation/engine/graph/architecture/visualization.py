"""UCOS-EPIC-010 (Terminal T2) — architecture visualization models.

Deterministic, dependency-free exporters that render the *higher-order*
architecture views (not the raw artifact graph, which EPIC-002
:mod:`engine.graph.visualization` already covers) into portable, human- and
tool-consumable models:

    * **Layer diagram** — the layer dependency graph, weighted, with inversions
      flagged (the architectural-stack health view).
    * **Capability diagram** — the capability-provision dependency graph.
    * **Condensation diagram** — the acyclic SCC condensation of the dependency
      graph, which makes any circular cluster visible as a single super-node.

Each builder returns an :class:`ArchitectureModel` (a small, immutable node/edge
document) that renders to JSON node-link, Mermaid ``flowchart`` source, or
Graphviz DOT. Every exporter emits nodes/edges in stable identifier order so
output is reproducible (determinism gate). Nothing here mutates the corpus (DP-03).
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

from engine.graph.architecture.algorithms import condensation, normalise_adjacency
from engine.graph.architecture.dependency_intelligence import CapabilityDependencyGraph
from engine.graph.architecture.layers import LayerDependencyGraph
from engine.graph.engine import DEPENDS_ON
from engine.graph.model import KIND_ARTIFACT, KnowledgeGraph

#: Supported architecture visualization format names.
VISUALIZATION_FORMATS: tuple[str, ...] = ("json", "mermaid", "dot")


@dataclass(frozen=True, slots=True)
class ModelNode:
    """One node in an architecture visualization model."""

    node_id: str
    label: str
    meta: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class ModelEdge:
    """One weighted directed edge in an architecture visualization model."""

    source: str
    target: str
    weight: int = 1
    flag: str = ""


@dataclass(frozen=True, slots=True)
class ArchitectureModel:
    """An immutable, deterministic architecture visualization model."""

    name: str
    nodes: tuple[ModelNode, ...]
    edges: tuple[ModelEdge, ...]

    def to_json(self, *, indent: int | None = 2) -> str:
        document = {
            "name": self.name,
            "nodes": [{"id": n.node_id, "label": n.label, "meta": n.meta} for n in self.nodes],
            "edges": [
                {
                    "source": e.source,
                    "target": e.target,
                    "weight": e.weight,
                    "flag": e.flag,
                }
                for e in self.edges
            ],
        }
        return json.dumps(document, indent=indent, sort_keys=True)

    def to_mermaid(self, *, direction: str = "TB") -> str:
        if direction not in {"LR", "TB", "RL", "BT"}:
            direction = "TB"
        index_of = {n.node_id: f"n{i}" for i, n in enumerate(self.nodes)}
        lines = [f"flowchart {direction}"]
        for node in self.nodes:
            safe = node.label.replace('"', "'")
            lines.append(f'    {index_of[node.node_id]}["{safe}"]')
        for edge in self.edges:
            src = index_of.get(edge.source)
            tgt = index_of.get(edge.target)
            if src is None or tgt is None:
                continue
            label = f"{edge.weight}"
            if edge.flag:
                label += f" {edge.flag}"
            lines.append(f"    {src} -->|{label}| {tgt}")
        return "\n".join(lines)

    def to_dot(self) -> str:
        lines = [f'digraph "{_dot_escape(self.name)}" {{']
        lines.append('  node [style=filled, shape=box, fontname="Helvetica"];')
        for node in self.nodes:
            lines.append(f'  "{_dot_escape(node.node_id)}" [label="{_dot_escape(node.label)}"];')
        for edge in self.edges:
            attrs = f'label="{edge.weight}"'
            if edge.flag:
                attrs = f'label="{edge.weight} {_dot_escape(edge.flag)}", color="red"'
            lines.append(
                f'  "{_dot_escape(edge.source)}" -> "{_dot_escape(edge.target)}" [{attrs}];'
            )
        lines.append("}")
        return "\n".join(lines)

    def render(self, fmt: str) -> str:
        match fmt:
            case "json":
                return self.to_json()
            case "mermaid":
                return self.to_mermaid()
            case "dot":
                return self.to_dot()
            case _:
                raise ValueError(f"unknown visualization format: {fmt!r}")


def _dot_escape(text: str) -> str:
    return text.replace("\\", "\\\\").replace('"', '\\"')


def layer_diagram(layers: LayerDependencyGraph) -> ArchitectureModel:
    """Build the layer dependency diagram model (weighted, inversions flagged)."""
    nodes = tuple(
        ModelNode(
            node_id=name,
            label=name,
            meta={"members": len(layers.members(name))},
        )
        for name in layers.layers()
    )
    edges = tuple(
        ModelEdge(
            source=dep.source,
            target=dep.target,
            weight=dep.weight,
            flag="INVERSION" if dep.inversion else "",
        )
        for dep in layers.dependencies()
    )
    return ArchitectureModel(name="layer-dependency", nodes=nodes, edges=edges)


def capability_diagram(capability: CapabilityDependencyGraph) -> ArchitectureModel:
    """Build the capability-provision dependency diagram model."""
    adjacency = capability.adjacency()
    incident: set[str] = set()
    for src, targets in adjacency.items():
        if targets:
            incident.add(src)
            incident.update(targets)
    nodes = tuple(ModelNode(node_id=nid, label=nid) for nid in sorted(incident))
    edges = tuple(
        ModelEdge(source=src, target=tgt) for src in sorted(adjacency) for tgt in adjacency[src]
    )
    return ArchitectureModel(name="capability-dependency", nodes=nodes, edges=edges)


def condensation_diagram(core: KnowledgeGraph) -> ArchitectureModel:
    """Build the acyclic SCC-condensation diagram of the ``Depends-On`` graph.

    Each node is a strongly-connected component; components with more than one
    member (genuine circular clusters) are flagged, so circular dependencies are
    immediately visible.
    """
    artifacts = {n.node_id for n in core.nodes_of_kind(KIND_ARTIFACT)}
    pairs = [
        (e.source, e.target)
        for e in core.edges_of_type(DEPENDS_ON)
        if e.source in artifacts and e.target in artifacts
    ]
    adjacency = normalise_adjacency(artifacts, pairs)
    dag, _member_of, members = condensation(adjacency)
    nodes = tuple(
        ModelNode(
            node_id=cid,
            label=f"{members[cid][0]} (+{len(members[cid]) - 1})"
            if len(members[cid]) > 1
            else members[cid][0],
            meta={"size": len(members[cid]), "cyclic": len(members[cid]) > 1},
        )
        for cid in sorted(dag)
    )
    edges = tuple(ModelEdge(source=src, target=tgt) for src in sorted(dag) for tgt in dag[src])
    return ArchitectureModel(name="dependency-condensation", nodes=nodes, edges=edges)


__all__ = [
    "VISUALIZATION_FORMATS",
    "ModelNode",
    "ModelEdge",
    "ArchitectureModel",
    "layer_diagram",
    "capability_diagram",
    "condensation_diagram",
]
