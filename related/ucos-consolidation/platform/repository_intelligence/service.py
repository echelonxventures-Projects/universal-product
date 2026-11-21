"""UCOS-EPIC-014 — Repository Intelligence service façade (Terminal T5).

One narrow surface over the whole subsystem, so a caller (the CLI, a hook, a CI gate, or
another platform capability) never has to know the internal pipeline order. The façade holds
no state beyond its configuration and caches nothing: every question is answered from a fresh
cycle, which is exactly what "search the repository continuously" requires.

The façade is also the intended integration point for the reuse guard: any tool that is about
to create a capability should ask :meth:`RepositoryIntelligenceService.advise` first.
"""

from __future__ import annotations

from platform.repository_intelligence.certification import RepositoryCertificate
from platform.repository_intelligence.config import RepositoryIntelligenceConfig
from platform.repository_intelligence.contracts import (
    DiscoveryDimension,
    Finding,
    Recommendation,
    RepositoryIntelligenceReport,
)
from platform.repository_intelligence.discovery import discover_all
from platform.repository_intelligence.graph import RepositoryGraph, build_graph
from platform.repository_intelligence.recommendation import (
    RepositoryRecommendationEngine,
    ReuseCandidate,
)
from platform.repository_intelligence.runtime import (
    IntelligenceCycle,
    RepositoryIntelligenceRuntime,
)
from platform.repository_intelligence.substrate import RepositorySubstrate
from platform.repository_intelligence.validation import RepositoryValidationReport
from typing import Any


class RepositoryIntelligenceService:
    """The single composed entry point to Repository Intelligence."""

    __slots__ = ("_runtime",)

    def __init__(self, config: RepositoryIntelligenceConfig | None = None) -> None:
        self._runtime = RepositoryIntelligenceRuntime(config)

    @property
    def config(self) -> RepositoryIntelligenceConfig:
        return self._runtime.config

    # -- full cycle -------------------------------------------------------
    def scan(self) -> IntelligenceCycle:
        """Run a complete intelligence cycle, including drift against the prior report."""
        return self._runtime.cycle()

    def report(self) -> RepositoryIntelligenceReport:
        return self.scan().report

    def graph(self) -> RepositoryGraph:
        """The repository dependency graph on its own (no validation or certification)."""
        substrate = RepositorySubstrate.scan(self.config)
        outcome = discover_all(substrate)
        return build_graph(outcome.units, outcome.edges)

    def validation(self) -> RepositoryValidationReport:
        return self.scan().validation

    def certificate(self) -> RepositoryCertificate:
        return self.scan().certificate

    # -- dimension projections -------------------------------------------
    def findings(self, dimension: DiscoveryDimension) -> tuple[Finding, ...]:
        """Every finding of one discovery dimension."""
        return self.report().findings_of(dimension)

    def gaps(self) -> tuple[Finding, ...]:
        return self.findings(DiscoveryDimension.GAP)

    def conflicts(self) -> tuple[Finding, ...]:
        return self.findings(DiscoveryDimension.CONFLICT)

    def duplicates(self) -> tuple[Finding, ...]:
        return self.findings(DiscoveryDimension.DUPLICATE)

    # -- recommendation ---------------------------------------------------
    def recommendations(self) -> tuple[Recommendation, ...]:
        return self.report().recommendations

    def advise(self, proposal: str, description: str = "") -> Recommendation:
        """Ask whether a proposed capability may be created, or must reuse what exists."""
        return self._engine().advise(proposal, description)

    def reuse_candidates(
        self, proposal: str, description: str = "", limit: int = 5
    ) -> tuple[ReuseCandidate, ...]:
        """Existing capabilities whose vocabulary overlaps a proposal, best first."""
        return self._engine().reuse_candidates(proposal, description, limit)

    def _engine(self) -> RepositoryRecommendationEngine:
        substrate = RepositorySubstrate.scan(self.config)
        outcome = discover_all(substrate)
        graph = build_graph(outcome.units, outcome.edges)
        return RepositoryRecommendationEngine(substrate, outcome, graph)

    # -- persistence and proofs ------------------------------------------
    def emit(self) -> tuple[str, ...]:
        """Persist every sealed artefact; returns the repository-relative paths written."""
        return self._runtime.write()

    def verify_determinism(self) -> dict[str, Any]:
        """Prove unchanged repository content yields byte-identical artefacts."""
        return self._runtime.verify_determinism()

    def hook_line(self) -> str:
        """The single-line session-start summary for the repository's hook convention."""
        return self.scan().certificate.hook_line()


def build_repository_intelligence_service(
    config: RepositoryIntelligenceConfig | None = None,
) -> RepositoryIntelligenceService:
    """Compose the Repository Intelligence service for a repository."""
    return RepositoryIntelligenceService(config)


__all__ = [
    "RepositoryIntelligenceService",
    "build_repository_intelligence_service",
]
