"""EC3-B11-U09 — Policy certification (reused CCE CC-1…CC-10 + Service C1…C7).

The CCE ten-gate suite is **reused verbatim** from
:func:`service.service_certification.cce_gates` (no gate logic duplicated), run through the
**CERTIFIED EC-1 Certification Engine** and appended to the append-only, hash-chained EC-1
ledger. Only the SERVICE-001 §12 **compliance mapping** is policy-specific — for the Policy,
**C7 (declarative, non-enforcing, confers no authority — USL-13/15) is materially exercised**:
the policy *is* the declarative, non-enforcing governing rule; and **C6 (evaluation binds RL-F2
by reference — USL-10)** is materially exercised too — a policy's evaluation behaves-as the
RUNTIME policy concern (RUNTIME-010) by reference.
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

#: Each compliance condition and the policy validation check ids that substantiate it.
_POLICY_COMPLIANCE_CHECKS: dict[str, tuple[str, ...]] = {
    "C1": ("policy-typed", "policy-identified-objectbound"),
    "C2": ("foundation-reuse-integrity",),
    "C3": ("service-value-fidelity", "policy-data-by-reference"),
    "C4": ("policy-boundary-bound", "policy-governed-scope"),
    "C5": ("founding-acyclic", "meta-relationships-closed"),
    "C6": ("policy-runtime-reuse",),
    "C7": (
        "policy-declarative-nonenforcing",
        "non-constitutive",
        "technology-independence",
    ),
}

_C3_NOTE = (
    "policy predicate data (DF-2) referenced (SMR-13/SPL-C4); ENG-003 value explicit — USL-11"
)
_C4_NOTE = (
    "policy bound-by its declaring contract boundary (SMR-02/SPL-06) and declares its governed "
    "scope by reference (SMR-08); interface/operation I/O N/A to Policy — USL-06"
)
_C5_NOTE = (
    "composition/orchestration N/A to Policy; the policy's reference-only founding graph is "
    "acyclic (SMK-03) with relationships closed to SMR-01…13"
)
_C6_NOTE = (
    "policy MATERIALLY EXERCISED: evaluation behaves-as the RUNTIME policy concern (RUNTIME-010) "
    "by reference (SMR-11/§7/SPL-05; USL-10); RUNTIME redefined 0"
)
_C7_NOTE = (
    "policy MATERIALLY EXERCISED: declarative and non-enforcing — confers/delegates/enacts no "
    "authority, grants no access, blocks nothing (USL-13/SPL-04/SPL-07) — THE governing law; "
    "selects no policy-engine/IAM technology and embeds no secret (USL-15)"
)


def evaluate_policy_compliance(validation: ServiceValidation) -> ServiceComplianceReport:
    """Decide the C1…C7 compliance of the validated policy on validation evidence."""
    passed = {f.check_id: f.passed for f in validation.report.findings}
    conditions: list[dict[str, Any]] = []
    notes = {"C3": _C3_NOTE, "C4": _C4_NOTE, "C5": _C5_NOTE, "C6": _C6_NOTE, "C7": _C7_NOTE}
    for cid, checks in _POLICY_COMPLIANCE_CHECKS.items():
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


def certify_policy(
    validation: ServiceValidation,
    *,
    version: str,
    ledger: CertificationLedger | None = None,
) -> ServiceCertification:
    """Run the CCE ten gates + C1…C7 over a validated policy and ledger the record."""
    subject = CertificationSubject.from_validation(
        validation.report, validation.evidence, version=version
    )
    decision = CertificationEngine(cce_gates()).certify(subject)
    active_ledger = ledger if ledger is not None else CertificationLedger()
    entry = active_ledger.append(decision.record)
    active_ledger.require_intact()
    cert_evidence = build_certification_evidence(decision)
    compliance = evaluate_policy_compliance(validation)
    return ServiceCertification(
        decision=decision,
        evidence=cert_evidence,
        ledger_entry=entry,
        ledger=active_ledger,
        compliance=compliance,
    )


__all__ = [
    "evaluate_policy_compliance",
    "certify_policy",
]
