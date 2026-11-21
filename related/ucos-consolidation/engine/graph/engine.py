"""UCOS-EPIC-002 (Terminal T2) — Universal Knowledge Graph engine (builder).

Projects Registry Truth into the core :class:`~engine.graph.model.KnowledgeGraph`.
The engine reads **only** through the read-only EPIC-002 Registry Adapter and its
source (``00-BOOK/DATA``); it never writes to the certified corpus (DP-03) and it
introduces no second store — nodes/edges are a *projection* of the registry
(GOV-INT-001 GI-RULE-0; single source of truth).

Construction rules (mission invariants):
    * Every artifact and every volume becomes exactly one node keyed by its
      immutable identifier — **no duplicate nodes** (:class:`DuplicateNodeError`
      is raised if the registry ever presents a conflicting duplicate).
    * Every relationship becomes exactly one edge keyed by its immutable
      ``edge_id`` — **immutable identifiers**.
    * Node ``version`` is carried from the artifact record — **version aware**.
    * The graph records the substrate ``generated_at`` / ``generator_version`` as
      provenance so a projection is reproducible and reverse-traceable (UMB-007).

Auxiliary registry documents (``signals.json``, ``certification.json``,
``twin.json``) are read through the same read-only source and are *optional*: if
absent the corresponding projections are simply empty.
"""

from __future__ import annotations

from typing import Any

from engine.foundation.obs.logging import get_logger
from engine.foundation.obs.telemetry import trace
from engine.graph.model import (
    KIND_ARTIFACT,
    KIND_VOLUME,
    Edge,
    GraphProvenance,
    KnowledgeGraph,
    Node,
)
from engine.registry.adapter import RegistryAdapter
from engine.registry.errors import RegistryError

_logger = get_logger("graph.engine")

# --- canonical relationship-type families (relationship.schema.json vocab) -----
# These are *reused*, never redefined (UMB-006 §3: additive, open vocabulary).
DEPENDS_ON = "Depends-On"
REQUIRED_BY = "Required-By"
PARENT = "Parent"
CHILD = "Child"
CONSUMES = "Consumes"
CONSUMED_BY = "Consumed-By"
IMPLEMENTS = "Implements"
IMPLEMENTED_BY = "Implemented-By"
TRACES_TO = "Traces-To"
TRACED_FROM = "Traced-From"
EVOLVES_FROM = "Evolves-From"
EVOLVES_FROM_INVERSE = "Evolves-From-Inverse"
AUTHORIZED_BY = "Authorized-By"
AUTHORIZES = "Authorizes"

#: Synthetic edge types minted by the ontology projection (still open vocabulary).
IN_VOLUME = "In-Volume"
OF_CATEGORY = "Of-Category"
IN_PROGRAM = "In-Program"

# Auxiliary registry documents (read-only, optional).
SIGNALS_FILE = "signals.json"
CERTIFICATION_FILE = "certification.json"
TWIN_FILE = "twin.json"


def _artifact_node(artifact: Any) -> Node:
    """Project a single registry :class:`Artifact` into an immutable graph node."""
    return Node(
        node_id=artifact.universal_id,
        kind=KIND_ARTIFACT,
        label=artifact.name,
        version=artifact.version,
        attributes={
            "category": artifact.category,
            "program": artifact.program,
            "status": artifact.status.value,
            "volume": artifact.volume,
            "owner": artifact.owner,
            "path": artifact.path,
            "native_id": artifact.native_id or "",
            "parent": artifact.parent or "",
            "tags": tuple(artifact.tags),
            # traceability stage references are retained for trace projections
            "traceability": {
                stage: artifact.traceability.stage(stage)
                for stage in ("requirement", "architecture", "design", "implementation")
            },
        },
    )


def _volume_node(volume: Any) -> Node:
    """Project a single registry :class:`Volume` into an immutable graph node."""
    return Node(
        node_id=volume.volume_id,
        kind=KIND_VOLUME,
        label=volume.name,
        version="",
        attributes={
            "serial": volume.serial,
            "category": volume.category,
            "status": volume.status.value,
            "artifact_count": volume.artifact_count,
        },
    )


def _relationship_edge(rel: Any) -> Edge:
    """Project a single registry :class:`Relationship` into an immutable edge."""
    return Edge(
        edge_id=rel.edge_id,
        source=rel.source,
        target=rel.target,
        type=rel.type,
        note=rel.note,
        attributes={"inverse_of": rel.inverse_of or ""},
    )


def build_core_graph(adapter: RegistryAdapter) -> KnowledgeGraph:
    """Build the core Universal Knowledge Graph from Registry Truth (read-only).

    Nodes: one per artifact (kind ``Artifact``) and one per volume (kind
    ``Volume``). Edges: one per registered relationship. Deterministic and
    idempotent — repeated builds over the same substrate are byte-identical.
    """
    with trace("graph.build.core"):
        artifacts = adapter.artifacts
        volumes = adapter.volumes
        relationships = adapter.graph

        nodes: list[Node] = [_artifact_node(a) for a in artifacts]
        nodes.extend(_volume_node(v) for v in volumes)
        edges: list[Edge] = [_relationship_edge(r) for r in relationships]

        provenance = GraphProvenance(
            generated_at=_envelope_field(adapter, "artifacts.json", "generated_at"),
            generator_version=_envelope_field(adapter, "artifacts.json", "generator_version"),
            artifact_count=artifacts.count(),
            relationship_count=relationships.count(),
            volume_count=volumes.count(),
        )
        graph = KnowledgeGraph(nodes, edges, provenance=provenance)
    _logger.info(
        "graph.core.built",
        nodes=graph.order(),
        edges=graph.size(),
        artifacts=artifacts.count(),
        volumes=volumes.count(),
    )
    return graph


def _envelope_field(adapter: RegistryAdapter, filename: str, key: str) -> str:
    """Read a top-level metadata field from a registry envelope (best effort)."""
    try:
        document = adapter.source.read_json(filename)
    except RegistryError:  # pragma: no cover - corpus always present in practice
        return ""
    if isinstance(document, dict):
        value = document.get(key)
        if isinstance(value, str):
            return value
    return ""


def _read_optional(adapter: RegistryAdapter, filename: str) -> dict[str, Any]:
    """Read an optional auxiliary registry document; ``{}`` if absent/invalid."""
    try:
        if not adapter.source.exists(filename):
            return {}
        document = adapter.source.read_json(filename)
    except RegistryError:
        return {}
    return document if isinstance(document, dict) else {}


def load_signals(adapter: RegistryAdapter) -> tuple[dict[str, Any], ...]:
    """Read the read-only signal records (evidence). Empty tuple if absent."""
    document = _read_optional(adapter, SIGNALS_FILE)
    signals = document.get("signals")
    if not isinstance(signals, list):
        return ()
    return tuple(s for s in signals if isinstance(s, dict))


def load_certification(adapter: RegistryAdapter) -> dict[str, Any]:
    """Read the read-only certification record. Empty dict if absent."""
    return _read_optional(adapter, CERTIFICATION_FILE)


def load_twin(adapter: RegistryAdapter) -> dict[str, Any]:
    """Read the read-only digital-twin projection. Empty dict if absent."""
    return _read_optional(adapter, TWIN_FILE)


__all__ = [
    "build_core_graph",
    "load_signals",
    "load_certification",
    "load_twin",
    "DEPENDS_ON",
    "REQUIRED_BY",
    "PARENT",
    "CHILD",
    "CONSUMES",
    "CONSUMED_BY",
    "IMPLEMENTS",
    "IMPLEMENTED_BY",
    "TRACES_TO",
    "TRACED_FROM",
    "EVOLVES_FROM",
    "EVOLVES_FROM_INVERSE",
    "AUTHORIZED_BY",
    "AUTHORIZES",
    "IN_VOLUME",
    "OF_CATEGORY",
    "IN_PROGRAM",
    "SIGNALS_FILE",
    "CERTIFICATION_FILE",
    "TWIN_FILE",
]
