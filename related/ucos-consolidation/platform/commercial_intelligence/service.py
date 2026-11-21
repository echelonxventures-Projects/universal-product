"""UCOS-EPIC-014 — Commercial Intelligence service (Terminal T5).

The single composition point for Commercial Intelligence. It wires a
:class:`~platform.commercial_intelligence.config.CommercialConfig` (or an explicit
:class:`~platform.commercial_intelligence.contracts.CommercialTarget`) to the
:class:`~platform.commercial_intelligence.validation.CommercialIntelligenceEngine` and
exposes the operations the mission asks for: the Commercial Intelligence Report, the
dashboard, the Commercial Certificate, and the deterministic Business Evidence record.

The service is strictly additive and record-only: it composes the engine and analyzers,
invents no commercial verdict (TP-01), mutates no target, and never writes to the
certified corpus (DP-03). Certification is *derived* from the report here, never asserted
alongside it, so the certificate and the report can never disagree.
"""

from __future__ import annotations

from collections.abc import Sequence
from platform.commercial_intelligence.certification import CommercialCertificate, certify
from platform.commercial_intelligence.config import CommercialConfig
from platform.commercial_intelligence.contracts import (
    CommercialDashboard,
    CommercialIntelligenceReport,
    CommercialTarget,
)
from platform.commercial_intelligence.evidence import (
    CommercialEvidence,
    build_commercial_evidence,
)
from platform.commercial_intelligence.validation import (
    CommercialIntelligenceEngine,
    DomainAnalyzer,
    select_analyzers,
)


class CommercialAssessment:
    """The three coherent artefacts of one commercial run: report, certificate, evidence."""

    __slots__ = ("_report", "_certificate", "_evidence")

    def __init__(self, report: CommercialIntelligenceReport) -> None:
        self._report = report
        self._certificate = certify(report)
        self._evidence = build_commercial_evidence(report, self._certificate)

    @property
    def report(self) -> CommercialIntelligenceReport:
        return self._report

    @property
    def certificate(self) -> CommercialCertificate:
        return self._certificate

    @property
    def evidence(self) -> CommercialEvidence:
        return self._evidence

    @property
    def dashboard(self) -> CommercialDashboard:
        return self._report.dashboard()

    @property
    def passed(self) -> bool:
        return self._report.passed

    @property
    def certified(self) -> bool:
        return self._certificate.certified

    def to_dict(self) -> dict[str, object]:
        return {
            "report": self._report.to_dict(),
            "dashboard": self.dashboard.to_dict(),
            "certificate": self._certificate.to_dict(),
            "evidence": self._evidence.to_dict(),
        }


class CommercialIntelligenceService:
    """A thin facade over the engine (analyze → report / dashboard / certificate / evidence)."""

    __slots__ = ("_engine",)

    def __init__(self, engine: CommercialIntelligenceEngine) -> None:
        self._engine = engine

    @property
    def engine(self) -> CommercialIntelligenceEngine:
        return self._engine

    def analyze(self, target: CommercialTarget) -> CommercialIntelligenceReport:
        """Produce the Commercial Intelligence Report over ``target`` (the T5 deliverable)."""
        return self._engine.analyze(target)

    def dashboard(self, target: CommercialTarget) -> CommercialDashboard:
        """Analyze ``target`` and project the commercial dashboard."""
        return self.analyze(target).dashboard()

    def certify(self, target: CommercialTarget) -> CommercialCertificate:
        """Analyze ``target`` and derive the Commercial Certificate."""
        return certify(self.analyze(target))

    def evidence(self, target: CommercialTarget) -> CommercialEvidence:
        """Analyze ``target`` and assemble the deterministic Business Evidence record."""
        return build_commercial_evidence(self.analyze(target))

    def assess(self, target: CommercialTarget) -> CommercialAssessment:
        """Analyze ``target`` once and return the report, certificate and evidence together."""
        return CommercialAssessment(self.analyze(target))


def build_commercial_service(
    config: CommercialConfig | None = None,
    *,
    analyzers: Sequence[DomainAnalyzer] | None = None,
) -> CommercialIntelligenceService:
    """Default composition of the Commercial Intelligence engine.

    When ``config`` is supplied, its declared domain subset scopes the engine; when
    ``analyzers`` is supplied, that suite is used verbatim. With neither, the full
    fourteen-domain built-in suite runs.
    """
    domains = config.selected_domains() if config is not None else None
    engine = CommercialIntelligenceEngine(select_analyzers(domains, analyzers))
    return CommercialIntelligenceService(engine)


__all__ = [
    "CommercialAssessment",
    "CommercialIntelligenceService",
    "build_commercial_service",
]
