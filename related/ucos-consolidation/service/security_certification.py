"""EC3-B11-U10 — Security certification (reused CCE CC-1…CC-10 + Service C1…C7).

The CCE ten-gate suite is **reused verbatim** from
:func:`service.service_certification.cce_gates` (no gate logic duplicated), run through the
**CERTIFIED EC-1 Certification Engine** and appended to the append-only, hash-chained EC-1
ledger. Only the SERVICE-001 §12 **compliance mapping** is security-specific — for Security,
**C7 (evaluative, non-enforcing, confers no authority — USL-14, THE governing law) is
materially exercised**: the security object *is* the decidable, non-enforcing evaluative
protection facet; and **C6 (evaluation binds RL-F2 by reference — USL-10)** is materially
exercised too — a security object's evaluation behaves-as the RUNTIME policy concern
(RUNTIME-010) by reference; **C3** additionally reuses the DATA-014 data-security
classifications for confidentiality/integrity data by reference (SSE-06 / USL-11).
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

#: Each compliance condition and the security validation check ids that substantiate it.
_SECURITY_COMPLIANCE_CHECKS: dict[str, tuple[str, ...]] = {
    "C1": ("security-typed", "security-identified-objectbound"),
    "C2": ("foundation-reuse-integrity",),
    "C3": ("service-value-fidelity", "security-data-by-reference"),
    "C4": ("security-boundary-classified", "security-policy-informed"),
    "C5": ("founding-acyclic", "meta-relationships-closed"),
    "C6": ("security-runtime-reuse",),
    "C7": (
        "security-evaluative-nonenforcing",
        "non-constitutive",
        "technology-independence",
    ),
}

_C3_NOTE = (
    "confidentiality/integrity data reuses DATA-014 by reference (SMR-13/SSE-06); ENG-003 value "
    "explicit — USL-11"
)
_C4_NOTE = (
    "security classifies its declared service/operation/execution boundary (SMR-09/SSE-07) and "
    "is informed by declarative Policies by reference (SMR-08 governed-by); interface/operation "
    "I/O N/A to Security — USL-06/07/08"
)
_C5_NOTE = (
    "composition/orchestration N/A to Security; the security object's reference-only founding "
    "graph is acyclic (SMK-03) with relationships closed to SMR-01…13"
)
_C6_NOTE = (
    "security MATERIALLY EXERCISED: evaluation behaves-as the RUNTIME policy concern "
    "(RUNTIME-010) by reference (SMR-11/§7; USL-10); RUNTIME redefined 0"
)
_C7_NOTE = (
    "security MATERIALLY EXERCISED: evaluative and non-enforcing — grants no access, issues no "
    "credential, encrypts nothing, confers no authority (USL-14/SSE-03/SSE-09) — THE governing "
    "law; selects no cryptography/IAM technology and embeds no secret (USL-15/SSE-04/05)"
)


def evaluate_security_compliance(validation: ServiceValidation) -> ServiceComplianceReport:
    """Decide the C1…C7 compliance of the validated security object on validation evidence."""
    passed = {f.check_id: f.passed for f in validation.report.findings}
    conditions: list[dict[str, Any]] = []
    notes = {"C3": _C3_NOTE, "C4": _C4_NOTE, "C5": _C5_NOTE, "C6": _C6_NOTE, "C7": _C7_NOTE}
    for cid, checks in _SECURITY_COMPLIANCE_CHECKS.items():
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


def certify_security(
    validation: ServiceValidation,
    *,
    version: str,
    ledger: CertificationLedger | None = None,
) -> ServiceCertification:
    """Run the CCE ten gates + C1…C7 over a validated security object and ledger the record."""
    subject = CertificationSubject.from_validation(
        validation.report, validation.evidence, version=version
    )
    decision = CertificationEngine(cce_gates()).certify(subject)
    active_ledger = ledger if ledger is not None else CertificationLedger()
    entry = active_ledger.append(decision.record)
    active_ledger.require_intact()
    cert_evidence = build_certification_evidence(decision)
    compliance = evaluate_security_compliance(validation)
    return ServiceCertification(
        decision=decision,
        evidence=cert_evidence,
        ledger_entry=entry,
        ledger=active_ledger,
        compliance=compliance,
    )


__all__ = [
    "evaluate_security_compliance",
    "certify_security",
]
