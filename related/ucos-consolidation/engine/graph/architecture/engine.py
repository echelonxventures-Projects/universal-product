"""UCOS-EPIC-010 (Terminal T2) — Architecture Intelligence Engine facade.

A single, Foundation-contract-compliant entry point that turns the certified
Universal Knowledge Graph (UCOS-EPIC-002) into an **Architecture Intelligence
Engine**. The facade composes the read-only
:class:`~engine.graph.adapter.KnowledgeGraphAdapter` and lazily builds — and
memoises — every higher-order engine:

    * **Dependency Intelligence** — capability dependency graph + circular
      dependency detection
      (:class:`~engine.graph.architecture.dependency_intelligence.DependencyIntelligence`).
    * **Layer dependency graph** — the architectural-stack view
      (:class:`~engine.graph.architecture.layers.LayerDependencyGraph`).
    * **Blast Radius Engine** — downstream damage surface of a change.
    * **Critical Path Engine** — the longest dependency chain.
    * **Architecture Impact Engine** — predictive impact of a change set.
    * **Semantic Reachability** — meaning-constrained reachability.
    * **Knowledge Insights Report** — the deterministic architecture roll-up.

Foundation compliance:
    * AR-03 / PL-05 — publishes a versioned :class:`Contract`
      (``architecture.intelligence`` v1.0.0) via the Foundation
      :class:`ContractRegistry`.
    * DP-03 — strictly read-only over Registry Truth (via the EPIC-002 graph
      adapter); introduces no second store (single source of truth; GOV-INT-001).
    * PL-02 — expensive builds run inside Foundation telemetry spans and emit
      structured logs.
"""

from __future__ import annotations

from typing import Any

from engine.foundation.contracts.contract import Contract, ContractRegistry, Version
from engine.foundation.obs.logging import get_logger
from engine.foundation.obs.telemetry import trace
from engine.graph.adapter import KnowledgeGraphAdapter
from engine.graph.architecture.blast_radius import BlastRadiusEngine, BlastRadiusReport
from engine.graph.architecture.critical_path import CriticalPathEngine, CriticalPathReport
from engine.graph.architecture.dependency_intelligence import DependencyIntelligence
from engine.graph.architecture.impact import ArchitectureImpactEngine, ImpactPrediction
from engine.graph.architecture.insights import build_insights_report
from engine.graph.architecture.layers import LayerDependencyGraph
from engine.graph.architecture.reachability import SemanticReachability
from engine.graph.architecture.visualization import (
    ArchitectureModel,
    capability_diagram,
    condensation_diagram,
    layer_diagram,
)
from engine.graph.model import KnowledgeGraph

#: The versioned contract this engine satisfies (AR-03, PL-05).
ARCHITECTURE_INTELLIGENCE_CONTRACT = Contract(
    name="architecture.intelligence",
    version=Version(1, 0, 0),
    description=(
        "Read-only Architecture Intelligence Engine over the Universal Knowledge "
        "Graph: dependency intelligence, layer dependency graph, circular "
        "dependency detection, blast-radius analysis, critical-path analysis, "
        "impact prediction, semantic reachability, architecture visualization "
        "models, and a Knowledge Insights Report."
    ),
)

#: The named diagram models the visualization surface can render.
DIAGRAM_NAMES: tuple[str, ...] = ("layer", "capability", "condensation")

_logger = get_logger("graph.architecture")


class ArchitectureIntelligenceEngine:
    """Read-only facade over the Architecture Intelligence Engine (UCOS-EPIC-010)."""

    __slots__ = (
        "_kg",
        "_dependency",
        "_layers",
        "_blast",
        "_critical",
        "_impact",
        "_reachability",
    )

    def __init__(self, kg: KnowledgeGraphAdapter | None = None) -> None:
        self._kg = kg if kg is not None else KnowledgeGraphAdapter()
        self._dependency: DependencyIntelligence | None = None
        self._layers: LayerDependencyGraph | None = None
        self._blast: BlastRadiusEngine | None = None
        self._critical: CriticalPathEngine | None = None
        self._impact: ArchitectureImpactEngine | None = None
        self._reachability: SemanticReachability | None = None

    # -- construction ----------------------------------------------------------

    @classmethod
    def open(cls, data_dir: object = None) -> ArchitectureIntelligenceEngine:
        """Open the engine over ``data_dir`` (defaults to ``00-BOOK/DATA``)."""
        return cls(KnowledgeGraphAdapter.open(data_dir))

    @property
    def knowledge_graph(self) -> KnowledgeGraphAdapter:
        """The underlying read-only Knowledge Graph adapter (Registry Truth)."""
        return self._kg

    @property
    def core(self) -> KnowledgeGraph:
        """The core knowledge graph this engine analyses."""
        return self._kg.core

    @property
    def contract(self) -> Contract:
        """The versioned interface contract this engine satisfies (AR-03)."""
        return ARCHITECTURE_INTELLIGENCE_CONTRACT

    def register_contract(self, registry: ContractRegistry) -> None:
        """Publish this engine's contract into a Foundation contract registry."""
        registry.register(ARCHITECTURE_INTELLIGENCE_CONTRACT)

    # -- lazy, memoised engines ------------------------------------------------

    @property
    def dependency(self) -> DependencyIntelligence:
        if self._dependency is None:
            with trace("architecture.dependency"):
                self._dependency = DependencyIntelligence(self.core)
        return self._dependency

    @property
    def layers(self) -> LayerDependencyGraph:
        if self._layers is None:
            with trace("architecture.layers"):
                self._layers = LayerDependencyGraph(self.core)
        return self._layers

    @property
    def blast_radius(self) -> BlastRadiusEngine:
        if self._blast is None:
            with trace("architecture.blast_radius"):
                self._blast = BlastRadiusEngine(self.core, layers=self.layers)
        return self._blast

    @property
    def critical_path(self) -> CriticalPathEngine:
        if self._critical is None:
            with trace("architecture.critical_path"):
                self._critical = CriticalPathEngine(self.core)
        return self._critical

    @property
    def impact(self) -> ArchitectureImpactEngine:
        if self._impact is None:
            with trace("architecture.impact"):
                self._impact = ArchitectureImpactEngine(self.core, layers=self.layers)
        return self._impact

    @property
    def reachability(self) -> SemanticReachability:
        if self._reachability is None:
            self._reachability = SemanticReachability(self.core)
        return self._reachability

    # -- convenience operations ------------------------------------------------

    def analyze_blast_radius(self, subject: str) -> BlastRadiusReport:
        """The blast-radius report for a single artifact."""
        return self.blast_radius.analyze(subject)

    def analyze_critical_path(self) -> CriticalPathReport:
        """The critical-path (longest dependency chain) report."""
        return self.critical_path.critical_path()

    def predict_impact(self, change_set: object) -> ImpactPrediction:
        """Predict the architecture-wide consequence of changing ``change_set``."""
        return self.impact.predict(change_set)

    def diagram(self, name: str, *, fmt: str = "json") -> str:
        """Render a named architecture diagram (``layer``/``capability``/``condensation``)."""
        model = self._diagram_model(name)
        return model.render(fmt)

    def _diagram_model(self, name: str) -> ArchitectureModel:
        match name:
            case "layer":
                return layer_diagram(self.layers)
            case "capability":
                return capability_diagram(self.dependency.capability)
            case "condensation":
                return condensation_diagram(self.core)
            case _:
                from engine.graph.architecture.errors import UnknownEngineError

                raise UnknownEngineError("unknown diagram", name=name, known=DIAGRAM_NAMES)

    # -- reports ---------------------------------------------------------------

    def insights(self, *, limit: int = 10) -> dict[str, Any]:
        """Build the deterministic Knowledge Insights Report (reusing memoised engines)."""
        with trace("architecture.insights"):
            report = build_insights_report(
                self.core,
                dependency=self.dependency,
                layers=self.layers,
                critical=self.critical_path,
                blast=self.blast_radius,
                limit=limit,
            )
        _logger.info(
            "architecture.insights.built",
            artifacts=report["totals"]["artifacts"],
            findings=len(report["findings"]),
            healthy=report["healthy"],
        )
        return report

    def build_all(self) -> None:
        """Eagerly build every architecture-intelligence engine."""
        _ = (
            self.dependency,
            self.layers,
            self.blast_radius,
            self.critical_path,
            self.impact,
            self.reachability,
        )

    def summary(self) -> dict[str, Any]:
        """A loggable, evidence-grade summary of the whole architecture intelligence."""
        return {
            "contract": {
                "name": ARCHITECTURE_INTELLIGENCE_CONTRACT.name,
                "version": str(ARCHITECTURE_INTELLIGENCE_CONTRACT.version),
            },
            "provenance": self.core.provenance.to_dict(),
            "dependency_intelligence": self.dependency.summary(),
            "layer_intelligence": self.layers.summary(),
            "critical_path": self.critical_path.summary(),
            "blast_radius": self.blast_radius.summary(),
        }


__all__ = [
    "ARCHITECTURE_INTELLIGENCE_CONTRACT",
    "DIAGRAM_NAMES",
    "ArchitectureIntelligenceEngine",
]
