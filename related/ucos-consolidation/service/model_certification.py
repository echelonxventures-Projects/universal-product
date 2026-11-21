"""EC3-B11-U11 — Meta-model certification (CCE ten gates CC-1…CC-10 + Service C1…C7).

Certification is *aggregation, not re-judgment* (TP-01 soundness): every gate reads only
the outcome of the service-layer validation (:mod:`service.model_validation`) and never
re-inspects the meta-model. It runs through the **CERTIFIED EC-1 Certification Engine**
(:class:`engine.certification.engine.CertificationEngine`), issues an immutable,
content-addressed :class:`~engine.certification.contracts.CertificationRecord`, and appends
it to the append-only, hash-chained EC-1
:class:`~engine.certification.ledger.CertificationLedger`.

The CCE ten-gate suite is **reused verbatim from the CERTIFIED SMC-01 surface**
(:func:`service.service_certification.cce_gates`) — the gates aggregate over generic
validation-subject fields and the shared blocking check ids the meta-model validation
emits. No parallel certification model is introduced (USL-02 reuse-by-reference).

Two evidence families are produced:

* **CC-1…CC-10** — the CCE ten-gate certification (EC-3 AP-3 §8.4), reused from SMC-01.
* **C1…C7** — the SERVICE-001 §12 Service-compliance conditions, decided on the same
  validation evidence, with **C5 (composition/orchestration are ENG-005 references; founding
  structure acyclic — the whole SMR-01…13 meta-relationship graph) materially exercised at
  the whole-model level** — the Universal Service Meta-Model closes over exactly the thirteen
  meta-relationships (SMI-02), keeps the founding meta-graph acyclic (SMI-04), and every map
  edge resolves within the closure or the frozen foundations (§9).

Certification records **engineering readiness only** (CCE-LAW-009 / DE-05): it asserts no
constitutional finality, and asserts no operational, deployment, or production readiness.
The EC-1 provisional-state disclosure is embedded in every record.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from engine.certification.contracts import CertificationSubject, CriterionStatus
from engine.certification.engine import CertificationDecision, CertificationEngine
from engine.certification.evidence import CertificationEvidence, build_certification_evidence
from engine.certification.ledger import CertificationLedger, CertificationLedgerEntry

# --- SMC-01 reuse by reference (USL-02) — the CERTIFIED CCE ten-gate suite --------
from service.model_meta import SERVICE_COMPLIANCE
from service.model_validation import ModelValidation
from service.service_certification import cce_gates

# ---------------------------------------------------------------------------
# SERVICE-001 §12 — Service compliance (C1…C7), with C5 materially exercised
# ---------------------------------------------------------------------------

#: Each compliance condition and the validation check ids that substantiate it.
#: **C5** is materially exercised at the whole-model level: the Universal Service Meta-Model
#: closes over exactly the thirteen meta-relationships (SMI-02) — including composes(SMR-05)
#: and orchestrates(SMR-06) — keeps the founding meta-graph acyclic (SMI-04), and resolves
#: every map edge within the closure/foundations (§9), each meta-relationship being an
#: ENG-005 reference introducing no new connection construct (USL-09 at the meta level).
_COMPLIANCE_CHECKS: dict[str, tuple[str, ...]] = {
    "C1": ("metamodel-typed", "metamodel-identified"),  # typed + identified/object-bound
    "C2": ("foundation-reuse-integrity",),  # reuse by reference, no redefinition (SMI-05)
    "C3": ("service-value-fidelity",),  # ENG-003 value (content-addressed model)
    "C4": (  # explicit model structure — closure + relationship closure + totality
        "meta-class-single",
        "meta-relationships-closed",
        "metamodel-totality",
        "metamodel-map-resolves",
    ),
    "C5": (  # composition/orchestration are ENG-005 refs; founding acyclic (materially exercised)
        "meta-relationships-closed",
        "founding-acyclic",
        "metamodel-map-resolves",
    ),
    "C6": (  # execution/behaviour binds RL-F2 by reference (SMR-07/11 → RL-F2)
        "foundation-reuse-integrity",
        "metamodel-map-resolves",
    ),
    "C7": ("technology-independence", "non-constitutive"),  # no tech / no authority / no secret
}

_C5_NOTE = (
    "the Universal Service Meta-Model closes over exactly the thirteen meta-relationships "
    "SMR-01…13 (SMI-02) — including composes(SMR-05) and orchestrates(SMR-06) — keeps the "
    "founding meta-graph (SMR-02/03/04/05) acyclic (SMI-04), and resolves every map edge "
    "within the closure or the frozen EL-1/RL-F2/PL-F2/DF-2 foundations (§9) — each "
    "meta-relationship being an ENG-005 reference introducing no new connection construct "
    "(USL-09 at the meta level)"
)


@dataclass(frozen=True, slots=True)
class ServiceComplianceReport:
    """A deterministic SERVICE-001 §12 compliance report (C1…C7) for a MetaModel."""

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


def evaluate_model_compliance(validation: ModelValidation) -> ServiceComplianceReport:
    """Decide the C1…C7 compliance of the validated meta-model on validation evidence."""
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
class ModelCertification:
    """The bundled outcome of certifying a validated MetaModel."""

    decision: CertificationDecision
    evidence: CertificationEvidence
    ledger_entry: CertificationLedgerEntry
    ledger: CertificationLedger
    compliance: ServiceComplianceReport

    @property
    def certified(self) -> bool:
        return self.decision.certified and self.ledger.verify() and self.compliance.compliant


def certify_model(
    validation: ModelValidation,
    *,
    version: str,
    ledger: CertificationLedger | None = None,
) -> ModelCertification:
    """Run the CCE ten gates + C1…C7 over a validated meta-model and ledger the record.

    Reuses the CERTIFIED EC-1 certification engine and append-only ledger **and** the
    CERTIFIED SMC-01 CCE ten-gate suite. The result is CERTIFIED iff all ten gates close,
    the ledger chain is intact, and the object is Service-COMPLIANT (C1…C7).
    """
    subject = CertificationSubject.from_validation(
        validation.report, validation.evidence, version=version
    )
    decision = CertificationEngine(cce_gates()).certify(subject)
    active_ledger = ledger if ledger is not None else CertificationLedger()
    entry = active_ledger.append(decision.record)
    active_ledger.require_intact()
    cert_evidence = build_certification_evidence(decision)
    compliance = evaluate_model_compliance(validation)
    return ModelCertification(
        decision=decision,
        evidence=cert_evidence,
        ledger_entry=entry,
        ledger=active_ledger,
        compliance=compliance,
    )


__all__ = [
    "ServiceComplianceReport",
    "evaluate_model_compliance",
    "ModelCertification",
    "certify_model",
    "CriterionStatus",
]
