"""UCOS-EPIC-013 — Continuous Validation Intelligence service (Terminal T5).

The single composition point for the Continuous Validation Intelligence engine. It wires
a :class:`~platform.validation_intelligence.config.ValidationIntelligenceConfig` (or an
explicit :class:`~platform.validation_intelligence.contracts.IntelligenceTarget`) to the
:class:`~platform.validation_intelligence.engine.ContinuousValidationIntelligenceEngine`
and exposes the operations the mission asks for: produce the Validation Intelligence
Report, the dashboard, the Compatibility Report, the Compliance Report, and the
deterministic evidence record.

The service is strictly additive and record-only: it composes the engine and analyzers,
invents no verdict (TP-01), and never writes to the certified corpus (DP-03).
"""

from __future__ import annotations

from collections.abc import Iterable
from platform.validation_intelligence.analyzers import DimensionAnalyzer
from platform.validation_intelligence.config import ValidationIntelligenceConfig
from platform.validation_intelligence.contracts import (
    CompatibilityReport,
    ComplianceReport,
    IntelligenceDashboard,
    IntelligenceTarget,
    ValidationIntelligenceReport,
)
from platform.validation_intelligence.engine import ContinuousValidationIntelligenceEngine
from platform.validation_intelligence.evidence import (
    ValidationIntelligenceEvidence,
    build_validation_intelligence_evidence,
)


class ContinuousValidationIntelligenceService:
    """A thin facade over the engine (analyze → report / dashboard / compat / compliance)."""

    __slots__ = ("_engine",)

    def __init__(self, engine: ContinuousValidationIntelligenceEngine) -> None:
        self._engine = engine

    @property
    def engine(self) -> ContinuousValidationIntelligenceEngine:
        return self._engine

    def analyze(self, target: IntelligenceTarget) -> ValidationIntelligenceReport:
        """Produce the Validation Intelligence Report over ``target`` (the T5 deliverable)."""
        return self._engine.analyze(target)

    def dashboard(self, target: IntelligenceTarget) -> IntelligenceDashboard:
        """Analyze ``target`` and project the intelligence dashboard."""
        return self.analyze(target).dashboard()

    def compatibility(self, target: IntelligenceTarget) -> CompatibilityReport:
        """Analyze ``target`` and project the Compatibility Engine's report."""
        return self.analyze(target).compatibility_report()

    def compliance(self, target: IntelligenceTarget) -> ComplianceReport:
        """Analyze ``target`` and project the Compliance Report."""
        return self.analyze(target).compliance_report()

    def evidence(self, target: IntelligenceTarget) -> ValidationIntelligenceEvidence:
        """Analyze ``target`` and assemble the deterministic evidence record."""
        return build_validation_intelligence_evidence(self.analyze(target))


def build_validation_intelligence_service(
    config: ValidationIntelligenceConfig | None = None,
    *,
    analyzers: Iterable[DimensionAnalyzer] | None = None,
) -> ContinuousValidationIntelligenceService:
    """Default composition of the Continuous Validation Intelligence engine.

    When ``config`` is supplied, its declared dimension subset scopes the engine; when
    ``analyzers`` is supplied, that suite is used verbatim. With neither, the full
    built-in universal suite runs.
    """
    dimensions = config.selected_dimensions() if config is not None else None
    engine = ContinuousValidationIntelligenceEngine(analyzers, dimensions=dimensions)
    return ContinuousValidationIntelligenceService(engine)


__all__ = [
    "ContinuousValidationIntelligenceService",
    "build_validation_intelligence_service",
]
