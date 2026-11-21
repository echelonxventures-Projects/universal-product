"""EC3-B11-U06 — Composition certification (reused CCE CC-1…CC-10 + Service C1…C7).

The CCE ten-gate suite is **reused verbatim** from
:func:`service.service_certification.cce_gates` (no gate logic duplicated), run through the
**CERTIFIED EC-1 Certification Engine** and appended to the append-only, hash-chained EC-1
ledger. Only the SERVICE-001 §12 **compliance mapping** is composition-specific — for the
Composition, **C5 (composition/orchestration uses ENG-005 references; founding acyclic —
USL-09) is materially exercised**: the composition *is* the reference-only, contract-bounded,
founding-acyclic structural assembly C5 speaks to.
"""

from __future__ import annotations

from typing import Any

from engine.certification.contracts import CertificationSubject
from engine.certification.engine import CertificationEngine
from engine.certification.evidence import build_certification_evidence
from engine.certification.ledger import CertificationLedger
from service.service_certification import (
    ServiceCertification,
    ServiceComplianceReport,
    cce_gates,
)
from service.service_meta import SERVICE_COMPLIANCE
from service.service_validation import ServiceValidation

#: Each compliance condition and the composition validation check ids that substantiate it.
_COMPOSITION_COMPLIANCE_CHECKS: dict[str, tuple[str, ...]] = {
    "C1": ("composition-typed", "composition-identified-objectbound"),
    "C2": ("foundation-reuse-integrity",),
    "C3": ("service-value-fidelity", "composition-data-by-reference"),
    "C4": ("composition-contract-bound",),
    "C5": (
        "composition-composes-members",
        "composition-topology-valid",
        "composition-platform-reuse",
        "founding-acyclic",
        "meta-relationships-closed",
    ),
    "C6": ("composition-invocation-by-reference",),
    "C7": ("non-constitutive", "technology-independence"),
}

_C3_NOTE = (
    "cross-composition data (DF-2) referenced (SMR-13/SCO-07); ENG-003 value explicit — USL-11"
)
_C4_NOTE = "composition contract explicit (contract-bound SCO-05/SCO-K2); USL-06"
_C5_NOTE = (
    "composition MATERIALLY EXERCISED: composes members by ENG-005 reference (SMR-05/SCO-03), "
    "reuses PLATFORM-010/011 (SMR-12/SCO-06), founding acyclic (USL-09/SCO-04) — the governing law"
)
_C6_NOTE = (
    "composition delegated invocation binds RUNTIME (RL-F2) by reference (§7 / USL-10); "
    "execution engine scoped to SMC-08"
)


def evaluate_composition_compliance(validation: ServiceValidation) -> ServiceComplianceReport:
    """Decide the C1…C7 compliance of the validated composition on validation evidence."""
    passed = {f.check_id: f.passed for f in validation.report.findings}
    conditions: list[dict[str, Any]] = []
    notes = {"C3": _C3_NOTE, "C4": _C4_NOTE, "C5": _C5_NOTE, "C6": _C6_NOTE}
    for cid, checks in _COMPOSITION_COMPLIANCE_CHECKS.items():
        ok = all(passed.get(c, False) for c in checks)
        entry: dict[str, Any] = {
            "id": cid,
            "requirement": SERVICE_COMPLIANCE[cid],
            "status": "pass" if ok else "fail",
            "backed_by": list(checks),
        }
        if cid in notes:
            entry["note"] = notes[cid]
        conditions.append(entry)
    return ServiceComplianceReport(
        target_id=validation.report.target_id, conditions=tuple(conditions)
    )


def certify_composition(
    validation: ServiceValidation,
    *,
    version: str,
    ledger: CertificationLedger | None = None,
) -> ServiceCertification:
    """Run the CCE ten gates + C1…C7 over a validated composition and ledger the record."""
    subject = CertificationSubject.from_validation(
        validation.report, validation.evidence, version=version
    )
    decision = CertificationEngine(cce_gates()).certify(subject)
    active_ledger = ledger if ledger is not None else CertificationLedger()
    entry = active_ledger.append(decision.record)
    active_ledger.require_intact()
    cert_evidence = build_certification_evidence(decision)
    compliance = evaluate_composition_compliance(validation)
    return ServiceCertification(
        decision=decision,
        evidence=cert_evidence,
        ledger_entry=entry,
        ledger=active_ledger,
        compliance=compliance,
    )


__all__ = [
    "evaluate_composition_compliance",
    "certify_composition",
]
