"""EC3-B11-U12 — Band-11 completion certification (CCE ten gates + Service C1…C7).

Certification is *aggregation, not re-judgment* (TP-01 soundness): every gate reads only
the outcome of the band-completion validation (:mod:`service.band11_validation`) and never
re-inspects the units. It runs through the **CERTIFIED EC-1 Certification Engine**
(:class:`engine.certification.engine.CertificationEngine`), issues an immutable,
content-addressed record, and appends it to the append-only, hash-chained EC-1
:class:`~engine.certification.ledger.CertificationLedger`.

The CCE ten-gate suite is **reused verbatim from the CERTIFIED SMC-01 surface**
(:func:`service.service_certification.cce_gates`) — the band-completion validation
deliberately emits the shared check ids those gates require (USL-02 reuse-by-reference). No
parallel certification model is introduced.

Two evidence families are produced:

* **CC-1…CC-10** — the CCE ten-gate certification, reused from SMC-01, decided at the band
  level (the band certifies that the eleven realizations are complete and closed).
* **C1…C7** — the SERVICE-001 §12 Service-compliance conditions, decided on the same
  validation evidence, with **C5 (relationships are ENG-005 references; founding structure
  acyclic) materially exercised at the whole-band level** (the band spine closes over
  SMR-01…13 via the CERTIFIED U11 and the unit founding graph is acyclic).

Certification records **engineering readiness only** (CCE-LAW-009 / DE-05): it asserts no
constitutional finality and no operational/deployment/production readiness.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

# --- EC-1 reuse by reference (USL-02) — the certified certification substrate ----
from engine.certification.contracts import CertificationSubject, CriterionStatus
from engine.certification.engine import CertificationDecision, CertificationEngine
from engine.certification.evidence import CertificationEvidence, build_certification_evidence
from engine.certification.ledger import CertificationLedger, CertificationLedgerEntry

# --- SMC-01 reuse by reference (USL-02) — the CERTIFIED CCE ten-gate suite --------
from service.band11_meta import SERVICE_COMPLIANCE
from service.band11_validation import Band11Validation
from service.service_certification import cce_gates

# ---------------------------------------------------------------------------
# SERVICE-001 §12 — Service compliance (C1…C7) at the band-completion level
# ---------------------------------------------------------------------------

#: Each compliance condition and the band validation check ids that substantiate it.
#: **C4** (explicit structure) is the band's inventory + certification closure; **C5** is
#: materially exercised — the band spine closes over SMR-01…13 (via U11) and the unit
#: founding graph is acyclic.
_COMPLIANCE_CHECKS: dict[str, tuple[str, ...]] = {
    "C1": ("band11-typed", "band11-identified"),  # typed + identified/object-bound
    "C2": ("foundation-reuse-integrity",),  # reuse by reference, no redefinition
    "C3": ("service-value-fidelity",),  # ENG-003 value (content-addressed record)
    "C4": ("band11-inventory-complete", "band11-all-units-certified"),  # explicit structure
    "C5": ("meta-relationships-closed", "founding-acyclic"),  # ENG-005 refs; founding acyclic
    "C6": ("band11-independence",),  # no technology (USL-15)
    "C7": ("non-constitutive",),  # no authority / no secret / no technology
}

_C5_NOTE = (
    "the Band-11 spine closes over exactly the thirteen meta-relationships SMR-01…13 via the "
    "CERTIFIED Universal Service Meta-Model (U11) and the eleven-unit founding graph is "
    "acyclic and downward-only — each relationship being an ENG-005 reference (USL-09 at "
    "band level)"
)


@dataclass(frozen=True, slots=True)
class ServiceComplianceReport:
    """A deterministic SERVICE-001 §12 compliance report (C1…C7) for a Band11Completion."""

    target_id: str
    conditions: tuple[dict[str, Any], ...]

    @property
    def compliant(self) -> bool:
        return all(c["status"] == "pass" for c in self.conditions)

    def to_dict(self) -> dict[str, Any]:
        return {
            "compliance_format": "ucos-service-compliance/1.0.0",
            "standard": "SERVICE-001 §12",
            "target_id": self.target_id,
            "compliant": self.compliant,
            "conditions": [dict(c) for c in self.conditions],
        }


def evaluate_band11_compliance(validation: Band11Validation) -> ServiceComplianceReport:
    """Decide the C1…C7 compliance of the validated band completion on validation evidence."""
    passed = {f.check_id: f.passed for f in validation.report.findings}
    conditions: list[dict[str, Any]] = []
    for cid, checks in _COMPLIANCE_CHECKS.items():
        ok = all(passed.get(c, False) for c in checks)
        entry: dict[str, Any] = {
            "id": cid,
            "requirement": SERVICE_COMPLIANCE[cid],
            "status": "pass" if ok else "fail",
            "backed_by": list(checks),
        }
        if cid == "C5":
            entry["note"] = _C5_NOTE
            entry["materially_exercised"] = True
        conditions.append(entry)
    return ServiceComplianceReport(
        target_id=validation.report.target_id, conditions=tuple(conditions)
    )


# ---------------------------------------------------------------------------
# Orchestrated certification
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class Band11Certification:
    """The bundled outcome of certifying a validated Band11Completion."""

    decision: CertificationDecision
    evidence: CertificationEvidence
    ledger_entry: CertificationLedgerEntry
    ledger: CertificationLedger
    compliance: ServiceComplianceReport

    @property
    def certified(self) -> bool:
        return self.decision.certified and self.ledger.verify() and self.compliance.compliant


def certify_band11(
    validation: Band11Validation,
    *,
    version: str,
    ledger: CertificationLedger | None = None,
) -> Band11Certification:
    """Run the CCE ten gates + C1…C7 over a validated band completion and ledger the record.

    Reuses the CERTIFIED EC-1 certification engine + append-only ledger **and** the
    CERTIFIED SMC-01 CCE ten-gate suite. The result is CERTIFIED iff all ten gates close,
    the ledger chain is intact, and the record is Service-COMPLIANT (C1…C7).
    """
    subject = CertificationSubject.from_validation(
        validation.report, validation.evidence, version=version
    )
    decision = CertificationEngine(cce_gates()).certify(subject)
    active_ledger = ledger if ledger is not None else CertificationLedger()
    entry = active_ledger.append(decision.record)
    active_ledger.require_intact()
    cert_evidence = build_certification_evidence(decision)
    compliance = evaluate_band11_compliance(validation)
    return Band11Certification(
        decision=decision,
        evidence=cert_evidence,
        ledger_entry=entry,
        ledger=active_ledger,
        compliance=compliance,
    )


__all__ = [
    "ServiceComplianceReport",
    "evaluate_band11_compliance",
    "Band11Certification",
    "certify_band11",
    "CriterionStatus",
]
