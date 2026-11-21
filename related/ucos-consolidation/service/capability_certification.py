"""EC3-B11-U02 — Capability certification (CCE ten gates CC-1…CC-10 + Service C1…C7).

Certification is *aggregation, not re-judgment* (TP-01 soundness): every gate reads only
the outcome of capability-layer validation (:mod:`service.capability_validation`) and
never re-inspects the capability. The **CCE ten-gate suite is reused verbatim** from
:func:`service.service_certification.cce_gates` (no gate logic is duplicated), run through
the **CERTIFIED EC-1 Certification Engine**
(:class:`engine.certification.engine.CertificationEngine`), issuing an immutable,
content-addressed record appended to the append-only, hash-chained EC-1
:class:`~engine.certification.ledger.CertificationLedger`.

Only the SERVICE-001 §12 **compliance mapping** is capability-specific (C4 is decided from
the capability's own explicit structure, since contract/interface/operation are scoped to
SMC-03/04/05). Certification records **engineering readiness only** (CCE-LAW-009 / DE-05).
"""

from __future__ import annotations

from typing import Any

# --- EC-1 reuse by reference (USL-02) — the certified certification substrate ----
from engine.certification.contracts import CertificationSubject
from engine.certification.engine import CertificationEngine
from engine.certification.evidence import build_certification_evidence
from engine.certification.ledger import CertificationLedger

# --- service-layer reuse — CCE gates + shared certification bundle types ----------
from service.service_certification import (
    ServiceCertification,
    ServiceComplianceReport,
    cce_gates,
)
from service.service_meta import SERVICE_COMPLIANCE
from service.service_validation import ServiceValidation

#: Each compliance condition and the capability validation check ids that substantiate it.
#: C3's operation-I/O clause and C4 (contract/interface/operation) are scoped to the
#: SMC-03/04/05 units; for the Capability they are satisfied by its own explicit structure
#: (type + kind + realized-by reference).
_CAPABILITY_COMPLIANCE_CHECKS: dict[str, tuple[str, ...]] = {
    "C1": ("capability-typed", "capability-identified-objectbound"),
    "C2": ("foundation-reuse-integrity",),
    "C3": ("service-value-fidelity",),
    "C4": ("capability-typed", "capability-classified", "capability-realized-by"),
    "C5": ("composition-by-reference", "founding-acyclic", "meta-relationships-closed"),
    "C6": ("execution-by-reference",),
    "C7": ("non-constitutive", "technology-independence"),
}

_C3_NOTE = (
    "operation I/O (DF-2) scoped to the Operation unit SMC-05; capability core value explicit"
)
_C4_NOTE = "contract/interface/operation scoped to SMC-03/04/05; capability structure explicit"


def evaluate_capability_compliance(validation: ServiceValidation) -> ServiceComplianceReport:
    """Decide the C1…C7 compliance of the validated capability on validation evidence.

    Reuses the generic :class:`ServiceComplianceReport` (no parallel model); only the
    check-id mapping is capability-specific.
    """
    passed = {f.check_id: f.passed for f in validation.report.findings}
    conditions: list[dict[str, Any]] = []
    for cid, checks in _CAPABILITY_COMPLIANCE_CHECKS.items():
        ok = all(passed.get(c, False) for c in checks)
        entry: dict[str, Any] = {
            "id": cid,
            "requirement": SERVICE_COMPLIANCE[cid],
            "status": "pass" if ok else "fail",
            "backed_by": list(checks),
        }
        if cid == "C3":
            entry["note"] = _C3_NOTE
        elif cid == "C4":
            entry["note"] = _C4_NOTE
        conditions.append(entry)
    return ServiceComplianceReport(
        target_id=validation.report.target_id, conditions=tuple(conditions)
    )


def certify_capability(
    validation: ServiceValidation,
    *,
    version: str,
    ledger: CertificationLedger | None = None,
) -> ServiceCertification:
    """Run the CCE ten gates + C1…C7 over a validated capability and ledger the record.

    Reuses the CERTIFIED EC-1 certification engine, the shared CCE ten-gate suite, and the
    append-only ledger. CERTIFIED iff all ten gates close, the ledger chain is intact, and
    the capability is Service-COMPLIANT (C1…C7).
    """
    subject = CertificationSubject.from_validation(
        validation.report, validation.evidence, version=version
    )
    decision = CertificationEngine(cce_gates()).certify(subject)
    active_ledger = ledger if ledger is not None else CertificationLedger()
    entry = active_ledger.append(decision.record)
    active_ledger.require_intact()
    cert_evidence = build_certification_evidence(decision)
    compliance = evaluate_capability_compliance(validation)
    return ServiceCertification(
        decision=decision,
        evidence=cert_evidence,
        ledger_entry=entry,
        ledger=active_ledger,
        compliance=compliance,
    )


__all__ = [
    "evaluate_capability_compliance",
    "certify_capability",
]
