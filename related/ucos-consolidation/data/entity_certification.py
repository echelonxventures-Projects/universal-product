"""EC3-B10-U03 — Entity certification (CCE ten gates CC-1…CC-10 + Data C1…C7).

Certification is *aggregation, not re-judgment* (TP-01 soundness): every gate reads
only the outcome of the data-layer validation (:mod:`data.entity_validation`) and
never re-inspects the entity. It runs through the **CERTIFIED EC-1 Certification
Engine** (:class:`engine.certification.engine.CertificationEngine`), issues an
immutable, content-addressed :class:`~engine.certification.contracts.CertificationRecord`,
and appends it to the append-only, hash-chained EC-1
:class:`~engine.certification.ledger.CertificationLedger`.

The CCE ten-gate suite is **reused verbatim from the CERTIFIED DMC-01 surface**
(:func:`data.certification.cce_gates`) — the gates aggregate over generic
validation-subject fields and the shared blocking check ids the Entity validation
emits (``meta-class-single``, ``foundation-reuse-integrity``, ``data-value-fidelity``,
``founding-acyclic``, ``meta-relationships-closed``, ``traceability-rooted``,
``provisional-state-disclosure``). No parallel certification model is introduced
(UDL-02 reuse-by-reference).

Two evidence families are produced:

* **CC-1…CC-10** — the CCE ten-gate certification (derived §9), reused from DMC-01.
* **C1…C7** — the DATA-001 §12 Data-compliance conditions, decided on the same
  validation evidence, with **C4 (explicit entity/attribute/schema structure) now
  materially exercised at the strongest level** — an entity declares an explicit,
  decidable, bounded attribute set (UDL-07 Entity Boundedness).

Certification records **engineering readiness only** (CCE-LAW-009 / DE-05): it
asserts no constitutional finality (the EC-1 provisional-state disclosure is embedded
in every record).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

# --- DMC-01 reuse by reference (UDL-02) — the CERTIFIED CCE ten-gate suite --------
from data.certification import cce_gates
from data.entity_meta import DATA_COMPLIANCE
from data.entity_validation import EntityValidation

# --- EC-1 reuse by reference (UDL-02) — the certified certification substrate ----
from engine.certification.contracts import CertificationSubject, CriterionStatus
from engine.certification.engine import CertificationDecision, CertificationEngine
from engine.certification.evidence import CertificationEvidence, build_certification_evidence
from engine.certification.ledger import CertificationLedger, CertificationLedgerEntry

# ---------------------------------------------------------------------------
# DATA-001 §12 — Data compliance (C1…C7), with C4 materially exercised
# ---------------------------------------------------------------------------

#: Each compliance condition and the validation check ids that substantiate it.
#: **C4** is materially exercised at the strongest level: unlike the atomic Datum and
#: the single-property Attribute, an Entity has explicit *entity structure* — an
#: explicit name (DEA-02), an ENG-004 type (DEA-01), and an explicit, decidable,
#: bounded attribute set (UDL-07 Entity Boundedness; DEA-03).
_COMPLIANCE_CHECKS: dict[str, tuple[str, ...]] = {
    "C1": ("entity-typed", "entity-identified"),  # typed + identified/object-bound
    "C2": ("foundation-reuse-integrity",),  # reuse by reference, no redefinition
    "C3": ("data-value-fidelity",),  # ENG-003 value (transitive, via attributes)
    "C4": (  # explicit entity structure (materially exercised — UDL-07 boundedness)
        "entity-named",
        "entity-typed",
        "entity-bears-attributes",
        "entity-boundedness",
    ),
    "C5": ("meta-relationships-closed", "founding-acyclic", "entity-boundary-ownership"),
    "C6": ("storage-independence",),  # no technology; storage abstract
    "C7": ("non-constitutive",),  # no authority / no secret
}

_C4_NOTE = (
    "entity structure explicit: name (DEA-02) + type (DEA-01) "
    "+ bounded, decidable attribute set (UDL-07 / DEA-03)"
)


@dataclass(frozen=True, slots=True)
class DataComplianceReport:
    """A deterministic DATA-001 §12 compliance report (C1…C7) for an Entity."""

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


def evaluate_entity_compliance(validation: EntityValidation) -> DataComplianceReport:
    """Decide the C1…C7 compliance of the validated entity on validation evidence."""
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
        if cid == "C4":
            entry["note"] = _C4_NOTE
            entry["materially_exercised"] = True
        conditions.append(entry)
    return DataComplianceReport(target_id=validation.report.target_id, conditions=tuple(conditions))


# ---------------------------------------------------------------------------
# Orchestrated certification
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class EntityCertification:
    """The bundled outcome of certifying a validated Entity."""

    decision: CertificationDecision
    evidence: CertificationEvidence
    ledger_entry: CertificationLedgerEntry
    ledger: CertificationLedger
    compliance: DataComplianceReport

    @property
    def certified(self) -> bool:
        return self.decision.certified and self.ledger.verify() and self.compliance.compliant


def certify_entity(
    validation: EntityValidation,
    *,
    version: str,
    ledger: CertificationLedger | None = None,
) -> EntityCertification:
    """Run the CCE ten gates + C1…C7 over a validated entity and ledger the record.

    Reuses the CERTIFIED EC-1 certification engine and append-only ledger **and** the
    CERTIFIED DMC-01 CCE ten-gate suite. The result is CERTIFIED iff all ten gates
    close, the ledger chain is intact, and the entity is Data-COMPLIANT (C1…C7).
    """
    subject = CertificationSubject.from_validation(
        validation.report, validation.evidence, version=version
    )
    decision = CertificationEngine(cce_gates()).certify(subject)
    active_ledger = ledger if ledger is not None else CertificationLedger()
    entry = active_ledger.append(decision.record)
    active_ledger.require_intact()
    cert_evidence = build_certification_evidence(decision)
    compliance = evaluate_entity_compliance(validation)
    return EntityCertification(
        decision=decision,
        evidence=cert_evidence,
        ledger_entry=entry,
        ledger=active_ledger,
        compliance=compliance,
    )


__all__ = [
    "DataComplianceReport",
    "evaluate_entity_compliance",
    "EntityCertification",
    "certify_entity",
    "CriterionStatus",
]
