"""EC3-B11-U05 — Operation certification (reused CCE CC-1…CC-10 + Service C1…C7).

The CCE ten-gate suite is **reused verbatim** from
:func:`service.service_certification.cce_gates` (no gate logic duplicated), run through the
**CERTIFIED EC-1 Certification Engine** and appended to the append-only, hash-chained EC-1
ledger. Only the SERVICE-001 §12 **compliance mapping** is operation-specific — for the
Operation, **C3 (typed I/O = DF-2 data — USL-08/11) and C4 (contract/interface/operation
structure explicit — USL-06/07/08) are both materially exercised**: the operation *is* the
typed, contracted, effect-honest unit of work C3/C4 speak to.
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

#: Each compliance condition and the operation validation check ids that substantiate it.
_OPERATION_COMPLIANCE_CHECKS: dict[str, tuple[str, ...]] = {
    "C1": ("operation-typed", "operation-identified-objectbound"),
    "C2": ("foundation-reuse-integrity",),
    "C3": ("service-value-fidelity", "operation-io-is-data", "operation-signature-bounded"),
    "C4": (
        "operation-contract-bound",
        "operation-interface-addressed",
        "operation-effect-honest",
        "operation-signature-bounded",
    ),
    "C5": ("founding-acyclic", "meta-relationships-closed"),
    "C6": ("operation-execution-by-reference", "operation-behavior-by-reference"),
    "C7": ("non-constitutive", "technology-independence"),
}

_C3_NOTE = (
    "operation typed I/O (DF-2) materially exercised (SMR-13/SOP-07); "
    "ENG-003 value explicit — USL-08/11"
)
_C4_NOTE = (
    "operation structure explicit (contract-bound SOP-04 + interface-addressed SOP-05 + "
    "effect-honest SOP-08) — materially exercised; USL-06/08"
)
_C5_NOTE = "composition/orchestration scoped to SMC-06/07; operation founding acyclic"
_C6_NOTE = (
    "operation execution/behavior binds RUNTIME (RL-F2) by reference (SMR-07/11 / SOP-06); "
    "execution engine scoped to SMC-08"
)


def evaluate_operation_compliance(validation: ServiceValidation) -> ServiceComplianceReport:
    """Decide the C1…C7 compliance of the validated operation on validation evidence."""
    passed = {f.check_id: f.passed for f in validation.report.findings}
    conditions: list[dict[str, Any]] = []
    notes = {"C3": _C3_NOTE, "C4": _C4_NOTE, "C5": _C5_NOTE, "C6": _C6_NOTE}
    for cid, checks in _OPERATION_COMPLIANCE_CHECKS.items():
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


def certify_operation(
    validation: ServiceValidation,
    *,
    version: str,
    ledger: CertificationLedger | None = None,
) -> ServiceCertification:
    """Run the CCE ten gates + C1…C7 over a validated operation and ledger the record."""
    subject = CertificationSubject.from_validation(
        validation.report, validation.evidence, version=version
    )
    decision = CertificationEngine(cce_gates()).certify(subject)
    active_ledger = ledger if ledger is not None else CertificationLedger()
    entry = active_ledger.append(decision.record)
    active_ledger.require_intact()
    cert_evidence = build_certification_evidence(decision)
    compliance = evaluate_operation_compliance(validation)
    return ServiceCertification(
        decision=decision,
        evidence=cert_evidence,
        ledger_entry=entry,
        ledger=active_ledger,
        compliance=compliance,
    )


__all__ = [
    "evaluate_operation_compliance",
    "certify_operation",
]
