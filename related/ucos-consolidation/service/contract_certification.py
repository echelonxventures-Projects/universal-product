"""EC3-B11-U03 — Contract certification (reused CCE CC-1…CC-10 + Service C1…C7).

The CCE ten-gate suite is **reused verbatim** from
:func:`service.service_certification.cce_gates` (no gate logic duplicated), run through the
**CERTIFIED EC-1 Certification Engine** and appended to the append-only, hash-chained EC-1
ledger. Only the SERVICE-001 §12 **compliance mapping** is contract-specific — for the
Contract, C3 (typed I/O = DF-2 data) and C4 (explicit specification structure) are
**materially exercised** rather than scoped to another unit.
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

#: Each compliance condition and the contract validation check ids that substantiate it.
_CONTRACT_COMPLIANCE_CHECKS: dict[str, tuple[str, ...]] = {
    "C1": ("contract-typed", "contract-identified-objectbound"),
    "C2": ("foundation-reuse-integrity",),
    "C3": ("service-value-fidelity", "contract-io-is-data"),
    "C4": ("contract-typed", "contract-classified", "contract-explicit-spec"),
    "C5": ("founding-acyclic", "meta-relationships-closed"),
    "C6": ("foundation-reuse-integrity",),
    "C7": ("non-constitutive", "technology-independence"),
}

_C3_NOTE = (
    "operation I/O (DF-2) materially exercised at the contract (SCN-04); ENG-003 value explicit"
)
_C4_NOTE = "contract structure explicit (SCN-03); interface/operation scoped to SMC-04/05"
_C5_NOTE = "composition/orchestration scoped to SMC-06/07; contract founding (bound-by) acyclic"
_C6_NOTE = (
    "execution/fulfilment scoped to SMC-08 (RUNTIME by reference); contract binds no execution"
)


def evaluate_contract_compliance(validation: ServiceValidation) -> ServiceComplianceReport:
    """Decide the C1…C7 compliance of the validated contract on validation evidence."""
    passed = {f.check_id: f.passed for f in validation.report.findings}
    conditions: list[dict[str, Any]] = []
    notes = {"C3": _C3_NOTE, "C4": _C4_NOTE, "C5": _C5_NOTE, "C6": _C6_NOTE}
    for cid, checks in _CONTRACT_COMPLIANCE_CHECKS.items():
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


def certify_contract(
    validation: ServiceValidation,
    *,
    version: str,
    ledger: CertificationLedger | None = None,
) -> ServiceCertification:
    """Run the CCE ten gates + C1…C7 over a validated contract and ledger the record."""
    subject = CertificationSubject.from_validation(
        validation.report, validation.evidence, version=version
    )
    decision = CertificationEngine(cce_gates()).certify(subject)
    active_ledger = ledger if ledger is not None else CertificationLedger()
    entry = active_ledger.append(decision.record)
    active_ledger.require_intact()
    cert_evidence = build_certification_evidence(decision)
    compliance = evaluate_contract_compliance(validation)
    return ServiceCertification(
        decision=decision,
        evidence=cert_evidence,
        ledger_entry=entry,
        ledger=active_ledger,
        compliance=compliance,
    )


__all__ = [
    "evaluate_contract_compliance",
    "certify_contract",
]
