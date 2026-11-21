"""UCOS-EPIC-013 — Compliance Reports (Terminal T5).

The **Compliance Report** deliverable is a deterministic projection of a
:class:`~platform.validation_intelligence.contracts.ValidationIntelligenceReport` over
its *compliance* dimensions — **architecture compliance** and **governance
compliance**. It answers a single, auditable question: is the target compliant, and if
not, which controls are unmet?

The projection is a pure function of the report (it re-reads only the report's compliance
dimension findings), so it carries the same determinism and content-addressing
guarantees (IMP-007 §5) and invents no verdict beyond what the analyzers already
recorded (TP-01).
"""

from __future__ import annotations

from platform.validation_intelligence.contracts import (
    ComplianceReport,
    ValidationIntelligenceReport,
)


def build_compliance_report(report: ValidationIntelligenceReport) -> ComplianceReport:
    """Project the Compliance Report from a full intelligence report."""
    return ComplianceReport.from_report(report)


__all__ = ["build_compliance_report"]
