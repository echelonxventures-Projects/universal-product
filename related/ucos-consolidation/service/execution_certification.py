"""EC3-B11-U08 — Execution certification (reused CCE CC-1…CC-10 + Service C1…C7).

The CCE ten-gate suite is **reused verbatim** from
:func:`service.service_certification.cce_gates` (no gate logic duplicated), run through the
**CERTIFIED EC-1 Certification Engine** and appended to the append-only, hash-chained EC-1
ledger. Only the SERVICE-001 §12 **compliance mapping** is execution-specific — for the
Execution, **C6 (execution binds RL-F2 by reference — USL-10) is materially exercised**: the
execution *is* the reference-only carrying-out whose behavior binds the RUNTIME execution/state/
workflow concern by reference; **C3 (read/written data is DF-2 by reference — USL-11)** is
materially exercised too.
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

#: Each compliance condition and the execution validation check ids that substantiate it.
_EXECUTION_COMPLIANCE_CHECKS: dict[str, tuple[str, ...]] = {
    "C1": ("execution-typed", "execution-identified-objectbound"),
    "C2": ("foundation-reuse-integrity",),
    "C3": ("service-value-fidelity", "execution-data-by-reference"),
    "C4": ("execution-operation-bound", "execution-contract-fulfilment"),
    "C5": ("founding-acyclic", "meta-relationships-closed"),
    "C6": (
        "execution-runtime-reuse",
        "execution-transactionality-by-reference",
    ),
    "C7": ("non-constitutive", "technology-independence"),
}

_C3_NOTE = (
    "execution MATERIALLY EXERCISED: read/written data (DF-2) referenced (SMR-13/SEX-07); "
    "ENG-003 value explicit — USL-11"
)
_C4_NOTE = "execution fulfils a contracted operation (operation-bound SEX-04/SEX-05); USL-06"
_C5_NOTE = (
    "composition/orchestration N/A to Execution; the execution's reference-only founding graph "
    "is acyclic (SMK-03) with relationships closed to SMR-01…13"
)
_C6_NOTE = (
    "execution MATERIALLY EXERCISED: behaves-as the kind's RUNTIME execution/state/workflow "
    "concern by reference (SMR-11/§7/SEX-03; USL-10) — the governing law; transactional "
    "atomicity by reference (SEX-06/SEX-C1); RUNTIME redefined 0"
)


def evaluate_execution_compliance(validation: ServiceValidation) -> ServiceComplianceReport:
    """Decide the C1…C7 compliance of the validated execution on validation evidence."""
    passed = {f.check_id: f.passed for f in validation.report.findings}
    conditions: list[dict[str, Any]] = []
    notes = {"C3": _C3_NOTE, "C4": _C4_NOTE, "C5": _C5_NOTE, "C6": _C6_NOTE}
    for cid, checks in _EXECUTION_COMPLIANCE_CHECKS.items():
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


def certify_execution(
    validation: ServiceValidation,
    *,
    version: str,
    ledger: CertificationLedger | None = None,
) -> ServiceCertification:
    """Run the CCE ten gates + C1…C7 over a validated execution and ledger the record."""
    subject = CertificationSubject.from_validation(
        validation.report, validation.evidence, version=version
    )
    decision = CertificationEngine(cce_gates()).certify(subject)
    active_ledger = ledger if ledger is not None else CertificationLedger()
    entry = active_ledger.append(decision.record)
    active_ledger.require_intact()
    cert_evidence = build_certification_evidence(decision)
    compliance = evaluate_execution_compliance(validation)
    return ServiceCertification(
        decision=decision,
        evidence=cert_evidence,
        ledger_entry=entry,
        ledger=active_ledger,
        compliance=compliance,
    )


__all__ = [
    "evaluate_execution_compliance",
    "certify_execution",
]
