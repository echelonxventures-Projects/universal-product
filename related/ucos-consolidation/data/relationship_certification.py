"""EC3-B10-U10 — Relationship certification (CCE ten gates CC-1…CC-10 + Data C1…C7).

Certification is *aggregation, not re-judgment* (TP-01 soundness): every gate reads only
the outcome of the data-layer validation (:mod:`data.relationship_validation`) and never
re-inspects the relationship object. It runs through the **CERTIFIED EC-1 Certification
Engine** (:class:`engine.certification.engine.CertificationEngine`), issues an immutable,
content-addressed :class:`~engine.certification.contracts.CertificationRecord`, and
appends it to the append-only, hash-chained EC-1
:class:`~engine.certification.ledger.CertificationLedger`.

The CCE ten-gate suite is **reused verbatim from the CERTIFIED DMC-01 surface**
(:func:`data.certification.cce_gates`) — the gates aggregate over generic
validation-subject fields and the shared blocking check ids the Relationship validation
emits. No parallel certification model is introduced (UDL-02 reuse-by-reference).

Two evidence families are produced:

* **CC-1…CC-10** — the CCE ten-gate certification (derived §14), reused from DMC-01.
* **C1…C7** — the DATA-001 §12 Data-compliance conditions, decided on the same
  validation evidence, with **C5 (relationships are ENG-005 references; founding
  structure acyclic — UDL-09) now materially exercised at the strongest level** — a
  Relationship object *is* an ENG-005 reference that relates two CERTIFIED entities, is
  acyclic where founding, resolves its endpoints, and declares explicit cardinality,
  introducing no new connection construct and naming no join/foreign-key/graph/database
  technology (UDL-09 Relationship by Reference; DRA-01/03/04/05; DRA-K5).

Certification records **engineering readiness only** (CCE-LAW-009 / DE-05): it asserts no
constitutional finality, and asserts no operational, deployment, or production readiness.
The EC-1 provisional-state disclosure is embedded in every record.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

# --- DMC-01 reuse by reference (UDL-02) — the CERTIFIED CCE ten-gate suite --------
from data.certification import cce_gates
from data.relationship_meta import DATA_COMPLIANCE
from data.relationship_validation import RelationshipValidation

# --- EC-1 reuse by reference (UDL-02) — the certified certification substrate ----
from engine.certification.contracts import CertificationSubject, CriterionStatus
from engine.certification.engine import CertificationDecision, CertificationEngine
from engine.certification.evidence import CertificationEvidence, build_certification_evidence
from engine.certification.ledger import CertificationLedger, CertificationLedgerEntry

# ---------------------------------------------------------------------------
# DATA-001 §12 — Data compliance (C1…C7), with C5 materially exercised
# ---------------------------------------------------------------------------

#: Each compliance condition and the validation check ids that substantiate it.
#: **C5** is materially exercised at the strongest level: a Relationship object *is* an
#: ENG-005 reference relating two CERTIFIED entities, acyclic where founding, resolving
#: every endpoint, with explicit cardinality — introducing no new connection construct and
#: naming no join/foreign-key/graph/database technology (UDL-09 Relationship by Reference;
#: DRA-01/03/04/05; DRA-K5).
_COMPLIANCE_CHECKS: dict[str, tuple[str, ...]] = {
    "C1": ("relationship-typed", "relationship-identified"),  # typed + identified/object-bound
    "C2": ("foundation-reuse-integrity",),  # reuse by reference, no redefinition
    "C3": ("data-value-fidelity",),  # ENG-003 value (transitive, via related entities)
    "C4": (  # explicit relationship structure (relates + cardinality + directionality)
        "relationship-relates-endpoints",
        "relationship-cardinality-explicit",
        "relationship-directionality-declared",
    ),
    "C5": (  # relationships are ENG-005 refs; founding acyclic (materially exercised — UDL-09)
        "relationship-by-reference",
        "relationship-referential-integrity",
        "relationship-founding-acyclic-rule",
        "founding-acyclic",
        "meta-relationships-closed",
    ),
    "C6": ("relationship-independence",),  # no technology (UDL-09/11)
    "C7": ("non-constitutive",),  # no authority / no secret / no technology
}

_C5_NOTE = (
    "relationship is an ENG-005 reference relating two CERTIFIED entities: it introduces "
    "no new connection construct, is acyclic where founding, resolves every endpoint, and "
    "declares explicit cardinality — naming no join/foreign-key/graph/database technology "
    "(UDL-09 Relationship by Reference; DRA-01/03/04/05; DRA-K5)"
)


@dataclass(frozen=True, slots=True)
class DataComplianceReport:
    """A deterministic DATA-001 §12 compliance report (C1…C7) for a Relationship object."""

    target_id: str
    conditions: tuple[dict[str, Any], ...]

    @property
    def compliant(self) -> bool:
        return all(c["status"] == "pass" for c in self.conditions)

    def to_dict(self) -> dict[str, Any]:
        return {
            "compliance_format": "ucos-data-compliance/1.0.0",
            "standard": "DATA-001 §12",
            "target_id": self.target_id,
            "compliant": self.compliant,
            "conditions": [dict(c) for c in self.conditions],
        }


def evaluate_relationship_compliance(validation: RelationshipValidation) -> DataComplianceReport:
    """Decide the C1…C7 compliance of the validated relationship on validation evidence."""
    passed = {f.check_id: f.passed for f in validation.report.findings}
    conditions: list[dict[str, Any]] = []
    for cid, checks in _COMPLIANCE_CHECKS.items():
        ok = all(passed.get(c, False) for c in checks)
        entry: dict[str, Any] = {
            "id": cid,
            "requirement": DATA_COMPLIANCE[cid],
            "status": "pass" if ok else "fail",
            "backed_by": list(checks),
        }
        if cid == "C5":
            entry["note"] = _C5_NOTE
            entry["materially_exercised"] = True
        conditions.append(entry)
    return DataComplianceReport(target_id=validation.report.target_id, conditions=tuple(conditions))


# ---------------------------------------------------------------------------
# Orchestrated certification
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class RelationshipCertification:
    """The bundled outcome of certifying a validated Relationship object."""

    decision: CertificationDecision
    evidence: CertificationEvidence
    ledger_entry: CertificationLedgerEntry
    ledger: CertificationLedger
    compliance: DataComplianceReport

    @property
    def certified(self) -> bool:
        return self.decision.certified and self.ledger.verify() and self.compliance.compliant


def certify_relationship(
    validation: RelationshipValidation,
    *,
    version: str,
    ledger: CertificationLedger | None = None,
) -> RelationshipCertification:
    """Run the CCE ten gates + C1…C7 over a validated relationship and ledger the record.

    Reuses the CERTIFIED EC-1 certification engine and append-only ledger **and** the
    CERTIFIED DMC-01 CCE ten-gate suite. The result is CERTIFIED iff all ten gates close,
    the ledger chain is intact, and the object is Data-COMPLIANT (C1…C7).
    """
    subject = CertificationSubject.from_validation(
        validation.report, validation.evidence, version=version
    )
    decision = CertificationEngine(cce_gates()).certify(subject)
    active_ledger = ledger if ledger is not None else CertificationLedger()
    entry = active_ledger.append(decision.record)
    active_ledger.require_intact()
    cert_evidence = build_certification_evidence(decision)
    compliance = evaluate_relationship_compliance(validation)
    return RelationshipCertification(
        decision=decision,
        evidence=cert_evidence,
        ledger_entry=entry,
        ledger=active_ledger,
        compliance=compliance,
    )


__all__ = [
    "DataComplianceReport",
    "evaluate_relationship_compliance",
    "RelationshipCertification",
    "certify_relationship",
    "CriterionStatus",
]
