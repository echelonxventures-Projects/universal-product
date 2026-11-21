"""EC3-B11-U04 — Interface certification (reused CCE CC-1…CC-10 + Service C1…C7).

The CCE ten-gate suite is **reused verbatim** from
:func:`service.service_certification.cce_gates` (no gate logic duplicated), run through the
**CERTIFIED EC-1 Certification Engine** and appended to the append-only, hash-chained EC-1
ledger. Only the SERVICE-001 §12 **compliance mapping** is interface-specific — for the
Interface, **C4 (contract/interface/operation structure explicit — USL-07) is materially
exercised**: the interface *is* the addressable-surface structure C4 speaks to. C3 (typed
I/O = DF-2 data) is likewise materially exercised via SIN-07 / SMR-13.
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

#: Each compliance condition and the interface validation check ids that substantiate it.
_INTERFACE_COMPLIANCE_CHECKS: dict[str, tuple[str, ...]] = {
    "C1": ("interface-typed", "interface-identified-objectbound"),
    "C2": ("foundation-reuse-integrity",),
    "C3": ("service-value-fidelity", "interface-io-is-data"),
    "C4": ("interface-typed", "interface-classified", "interface-sole-surface"),
    "C5": ("founding-acyclic", "meta-relationships-closed"),
    "C6": ("interface-behavior-by-reference",),
    "C7": ("non-constitutive", "technology-independence"),
}

_C3_NOTE = (
    "operation I/O (DF-2) materially exercised at the interface surface (SIN-07/SMR-13); "
    "ENG-003 value explicit"
)
_C4_NOTE = (
    "interface structure explicit (USL-07 / SIN-01/03) — materially exercised; "
    "contract/operation scoped to SMC-03/05"
)
_C5_NOTE = "composition/orchestration scoped to SMC-06/07; interface founding (exposes) acyclic"
_C6_NOTE = (
    "interface interaction binds RUNTIME (RL-F2) by reference (SMR-11 / SIN-C5); "
    "execution scoped to SMC-08"
)


def evaluate_interface_compliance(validation: ServiceValidation) -> ServiceComplianceReport:
    """Decide the C1…C7 compliance of the validated interface on validation evidence."""
    passed = {f.check_id: f.passed for f in validation.report.findings}
    conditions: list[dict[str, Any]] = []
    notes = {"C3": _C3_NOTE, "C4": _C4_NOTE, "C5": _C5_NOTE, "C6": _C6_NOTE}
    for cid, checks in _INTERFACE_COMPLIANCE_CHECKS.items():
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


def certify_interface(
    validation: ServiceValidation,
    *,
    version: str,
    ledger: CertificationLedger | None = None,
) -> ServiceCertification:
    """Run the CCE ten gates + C1…C7 over a validated interface and ledger the record."""
    subject = CertificationSubject.from_validation(
        validation.report, validation.evidence, version=version
    )
    decision = CertificationEngine(cce_gates()).certify(subject)
    active_ledger = ledger if ledger is not None else CertificationLedger()
    entry = active_ledger.append(decision.record)
    active_ledger.require_intact()
    cert_evidence = build_certification_evidence(decision)
    compliance = evaluate_interface_compliance(validation)
    return ServiceCertification(
        decision=decision,
        evidence=cert_evidence,
        ledger_entry=entry,
        ledger=active_ledger,
        compliance=compliance,
    )


__all__ = [
    "evaluate_interface_compliance",
    "certify_interface",
]
