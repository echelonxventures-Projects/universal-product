"""UCOS-EPIC-002 (Terminal T2) — Universal Knowledge Graph adapter facade.

A single, Foundation-contract-compliant entry point over the Universal Knowledge
Graph. The adapter composes the read-only Registry Adapter (EPIC-002), the graph
engine (core builder), the ten projections, validation and visualization.

Foundation compliance:
    * AR-03 / PL-05 — publishes a versioned :class:`Contract` (``knowledge.graph``
      v1.0.0) via the Foundation :class:`ContractRegistry`.
    * DP-03 — strictly read-only over Registry Truth; introduces no second store
      (single source of truth; GOV-INT-001 GI-RULE-0).
    * PL-02 — builds run inside Foundation telemetry spans and emit structured
      logs.

Loading is lazy and memoised: the core graph, auxiliary registry documents, and
each projection are built on first access and reused thereafter, so the adapter is
cheap to construct and idempotent to query.
"""

from __future__ import annotations

from typing import Any

from engine.foundation.contracts.contract import Contract, ContractRegistry, Version
from engine.foundation.obs.logging import get_logger
from engine.foundation.obs.telemetry import trace
from engine.graph.engine import build_core_graph, load_certification, load_signals, load_twin
from engine.graph.model import KnowledgeGraph
from engine.graph.projections import (
    PROJECTION_NAMES,
    CapabilityGraph,
    CertificationGraph,
    DependencyGraph,
    EvidenceGraph,
    ImpactGraph,
    ImplementationGraph,
    OntologyGraph,
    Projection,
    RequirementGraph,
    TraceabilityGraph,
    ValidationGraph,
    build_projection,
)
from engine.graph.validation import GraphValidationReport, validate_graph
from engine.graph.visualization import render
from engine.registry.adapter import RegistryAdapter

#: The versioned contract this adapter satisfies (AR-03, PL-05).
KNOWLEDGE_GRAPH_CONTRACT = Contract(
    name="knowledge.graph",
    version=Version(1, 0, 0),
    description=(
        "Read-only Universal Knowledge Graph over Registry Truth: a single core "
        "graph and ten projections (ontology, capability, dependency, "
        "traceability, evidence, requirement, implementation, validation, "
        "certification, impact), plus validation and visualization."
    ),
)

_logger = get_logger("graph.adapter")


class KnowledgeGraphAdapter:
    """Read-only facade over the Universal Knowledge Graph (UCOS-EPIC-002)."""

    __slots__ = (
        "_registry",
        "_core",
        "_signals",
        "_certification",
        "_twin",
        "_projections",
    )

    def __init__(self, registry: RegistryAdapter | None = None) -> None:
        self._registry = registry if registry is not None else RegistryAdapter()
        self._core: KnowledgeGraph | None = None
        self._signals: tuple[dict[str, Any], ...] | None = None
        self._certification: dict[str, Any] | None = None
        self._twin: dict[str, Any] | None = None
        self._projections: dict[str, Projection] = {}

    # -- construction ----------------------------------------------------------

    @classmethod
    def open(cls, data_dir=None) -> KnowledgeGraphAdapter:
        """Open the adapter over ``data_dir`` (defaults to ``00-BOOK/DATA``)."""
        return cls(RegistryAdapter.open(data_dir))

    @property
    def registry(self) -> RegistryAdapter:
        """The underlying read-only Registry Adapter (Registry Truth)."""
        return self._registry

    @property
    def contract(self) -> Contract:
        """The versioned interface contract this adapter satisfies (AR-03)."""
        return KNOWLEDGE_GRAPH_CONTRACT

    def register_contract(self, registry: ContractRegistry) -> None:
        """Publish this adapter's contract into a Foundation contract registry."""
        registry.register(KNOWLEDGE_GRAPH_CONTRACT)

    # -- lazy, memoised substrate ---------------------------------------------

    @property
    def core(self) -> KnowledgeGraph:
        """The core knowledge graph (built on first access)."""
        if self._core is None:
            with trace("graph.build.core"):
                self._core = build_core_graph(self._registry)
        return self._core

    @property
    def signals(self) -> tuple[dict[str, Any], ...]:
        """The read-only evidence signal records (loaded on first access)."""
        if self._signals is None:
            self._signals = load_signals(self._registry)
        return self._signals

    @property
    def certification(self) -> dict[str, Any]:
        """The read-only certification record (loaded on first access)."""
        if self._certification is None:
            self._certification = load_certification(self._registry)
        return self._certification

    @property
    def twin(self) -> dict[str, Any]:
        """The read-only digital-twin projection (loaded on first access)."""
        if self._twin is None:
            self._twin = load_twin(self._registry)
        return self._twin

    # -- projections -----------------------------------------------------------

    def projection(self, name: str) -> Projection:
        """Return a named projection, building and memoising it on first access."""
        cached = self._projections.get(name)
        if cached is not None:
            return cached
        with trace("graph.projection", projection=name):
            projection = build_projection(
                name,
                self.core,
                signals=self.signals,
                certification=self.certification,
                twin=self.twin,
            )
        self._projections[name] = projection
        summary = projection.summary()
        _logger.info(
            "graph.projection.built",
            projection=name,
            nodes=summary["nodes"],
            edges=summary["edges"],
        )
        return projection

    # -- typed projection accessors -------------------------------------------

    def ontology(self) -> OntologyGraph:
        return self.projection("ontology")  # type: ignore[return-value]

    def capability(self) -> CapabilityGraph:
        return self.projection("capability")  # type: ignore[return-value]

    def dependency(self) -> DependencyGraph:
        return self.projection("dependency")  # type: ignore[return-value]

    def traceability(self) -> TraceabilityGraph:
        return self.projection("traceability")  # type: ignore[return-value]

    def evidence(self) -> EvidenceGraph:
        return self.projection("evidence")  # type: ignore[return-value]

    def requirement(self) -> RequirementGraph:
        return self.projection("requirement")  # type: ignore[return-value]

    def implementation(self) -> ImplementationGraph:
        return self.projection("implementation")  # type: ignore[return-value]

    def validation(self) -> ValidationGraph:
        return self.projection("validation")  # type: ignore[return-value]

    def certification_graph(self) -> CertificationGraph:
        return self.projection("certification")  # type: ignore[return-value]

    def impact(self) -> ImpactGraph:
        return self.projection("impact")  # type: ignore[return-value]

    # -- validation / visualization -------------------------------------------

    def validate(self) -> GraphValidationReport:
        """Validate the core graph against the mission invariants."""
        with trace("graph.validate"):
            return validate_graph(self.core)

    def visualize(self, projection: str | None = None, *, fmt: str = "json") -> str:
        """Render the core graph (or a named projection) in a visualization format."""
        graph = self.core if projection is None else self.projection(projection).graph
        return render(graph, fmt)

    # -- summary ---------------------------------------------------------------

    def build_all(self) -> None:
        """Eagerly build the core graph and all ten projections."""
        for name in PROJECTION_NAMES:
            self.projection(name)

    def summary(self) -> dict[str, Any]:
        """A loggable, evidence-grade summary of the whole knowledge graph."""
        core = self.core
        return {
            "contract": {
                "name": KNOWLEDGE_GRAPH_CONTRACT.name,
                "version": str(KNOWLEDGE_GRAPH_CONTRACT.version),
            },
            "provenance": core.provenance.to_dict(),
            "core": {
                "nodes": core.order(),
                "edges": core.size(),
                "kinds": list(core.kinds()),
                "edge_types": list(core.edge_types()),
            },
            "projections": {name: self.projection(name).summary() for name in PROJECTION_NAMES},
            "certification_verdict": str(self.certification.get("verdict") or "UNKNOWN"),
        }


def emitted_kinds() -> tuple[str, ...]:
    """Every relationship kind this surface actually emits, read off the graphs it builds.

    Declared as the `reporter` for this surface in the CAA register's `emitting_surfaces`, and
    CALLED rather than trusted: CAA-INV-05 requires every emitted kind to resolve into the one
    relationship model (UCKP-ART-07), and a declared list would answer for the code it was
    written beside rather than the code that runs. Building the ten projections is the only way
    to know what they emit.
    """
    adapter = KnowledgeGraphAdapter.open()
    kinds: set[str] = set()
    for name in PROJECTION_NAMES:
        kinds |= set(adapter.projection(name).graph.edge_types())
    return tuple(sorted(kinds))


__all__ = ["emitted_kinds", "KnowledgeGraphAdapter", "KNOWLEDGE_GRAPH_CONTRACT"]
