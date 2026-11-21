"""EC3-B13-U06 — Topology & Distribution certification (CCE gates CC-1…CC-10 + C1…C7).

Certification is *aggregation, not re-judgment* (TP-01 soundness): every gate below reads
only the outcome of the Topology & Distribution validation
(:mod:`infrastructure.topology_validation`) and never re-inspects the construct. It runs
through the **CERTIFIED EC-1 Certification Engine**, issues an immutable,
content-addressed record, and appends it to the append-only, hash-chained EC-1
:class:`~engine.certification.ledger.CertificationLedger`.

Two evidence families are produced per construct:

* **CC-1…CC-10** — the CCE ten-gate certification (EC-3 §8), realized as ten blocking
  :class:`~engine.certification.criteria.CertificationCriterion` aggregating the
  validation verdict, evidence, traceability, disclosure, and gap signals.
* **C1…C7** — the INFRASTRUCTURE-001 §12 Infrastructure-compliance conditions. For this
  unit, **C4** (Distribution typed and hosts AF-3/SF-2 by reference — UIL-12), **C5**
  (Topology uses ENG-005 references, founding acyclic — UIL-09) and **C7** (no technology
  selection — UIL-15) are the **materially-exercised** governing conditions.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from engine.certification.contracts import (
    CertificationClass,
    CertificationFinding,
    CertificationSubject,
    CriterionSeverity,
    CriterionStatus,
)
from engine.certification.criteria import CertificationCriterion
from engine.certification.engine import CertificationDecision, CertificationEngine
from engine.certification.evidence import CertificationEvidence, build_certification_evidence
from engine.certification.ledger import CertificationLedger, CertificationLedgerEntry
from infrastructure.topology_meta import (
    INFRASTRUCTURE_COMPLIANCE,
    TOPOLOGY_CONCERN_RULES,
)
from infrastructure.topology_validation import TopologyValidation


class _GateCriterion(CertificationCriterion):
    """Base for a CCE gate that aggregates one or more validation check outcomes."""

    severity = CriterionSeverity.BLOCKING
    required_checks: tuple[str, ...] = ()

    def _checks_ok(self, subject: CertificationSubject) -> tuple[bool, list[str]]:
        run = set(subject.checks_run)
        blocked = set(subject.blocking_failures)
        problems: list[str] = []
        for cid in self.required_checks:
            if cid not in run:
                problems.append(f"{cid}:not-run")
            elif cid in blocked:
                problems.append(f"{cid}:failed")
        return (not problems), problems


class Gate1Architecture(_GateCriterion):
    criterion_id = "CC-1"
    description = "Gate 1 Architecture — no orphan (construct traces the frozen spec spine)."
    required_checks = ("traceability-rooted", "meta-class-single")

    def evaluate(self, subject: CertificationSubject) -> CertificationFinding:
        ok, problems = self._checks_ok(subject)
        return self._passed(gate="architecture") if ok else self._failed(
            "architecture gate: orphan/meta-class defect", problems=problems
        )


class Gate2Dependencies(_GateCriterion):
    criterion_id = "CC-2"
    description = "Gate 2 Dependencies Closed — reuse-by-reference over the frozen substrate."
    required_checks = ("foundation-reuse-integrity",)

    def evaluate(self, subject: CertificationSubject) -> CertificationFinding:
        ok, problems = self._checks_ok(subject)
        return self._passed(gate="dependencies") if ok else self._failed(
            "dependencies gate: substrate closure defect", problems=problems
        )


class Gate3Coverage(_GateCriterion):
    criterion_id = "CC-3"
    description = "Gate 3 Coverage — deterministic; no structural violation."
    required_checks = (
        "infra-topology-value-fidelity",
        "founding-acyclic",
        "meta-relationships-closed",
    )

    def evaluate(self, subject: CertificationSubject) -> CertificationFinding:
        ok, problems = self._checks_ok(subject)
        failed = int(subject.counts.get("failed", 0))
        if not ok or failed:
            return self._failed(
                "coverage gate: structural violation", problems=problems, failed=failed
            )
        return self._passed(gate="coverage")


class Gate4Validation(_GateCriterion):
    criterion_id = "CC-4"
    description = "Gate 4 Validation — VC-1 satisfied (validation accepted, verdict PASS)."

    def evaluate(self, subject: CertificationSubject) -> CertificationFinding:
        if not subject.validation_accepted or subject.validation_verdict != "pass":
            return self._failed(
                "validation gate: not accepted",
                verdict=subject.validation_verdict,
                blocking=list(subject.blocking_failures),
            )
        return self._passed(gate="validation", verdict=subject.validation_verdict)


class Gate5Traceability(_GateCriterion):
    criterion_id = "CC-5"
    description = "Gate 5 Traceability — lineage rooted and cited (No-Orphan)."
    required_checks = ("traceability-rooted",)

    def evaluate(self, subject: CertificationSubject) -> CertificationFinding:
        ok, problems = self._checks_ok(subject)
        return self._passed(gate="traceability") if ok else self._failed(
            "traceability gate: lineage not closed", problems=problems
        )


class Gate6Evidence(_GateCriterion):
    criterion_id = "CC-6"
    description = "Gate 6 Evidence — validation evidence present and content-hashed."

    def evaluate(self, subject: CertificationSubject) -> CertificationFinding:
        if not subject.evidence_present or not subject.evidence_sha256:
            return self._failed("evidence gate: validation evidence absent")
        return self._passed(gate="evidence", evidence_sha256=subject.evidence_sha256)


class Gate7CertificationReady(_GateCriterion):
    criterion_id = "CC-7"
    description = "Gate 7 Certification-Ready — provisional-state disclosed."
    required_checks = ("provisional-state-disclosure",)

    def evaluate(self, subject: CertificationSubject) -> CertificationFinding:
        ok, problems = self._checks_ok(subject)
        return self._passed(gate="certification-ready") if ok else self._failed(
            "certification-ready gate: provisional-state not disclosed", problems=problems
        )


class Gate8Readiness(_GateCriterion):
    criterion_id = "CC-8"
    description = "Gate 8 Readiness — readiness indicators satisfied; 0 blockers."

    def evaluate(self, subject: CertificationSubject) -> CertificationFinding:
        blockers = list(subject.blocking_failures)
        if blockers:
            return self._failed("readiness gate: blockers present", blockers=blockers)
        return self._passed(gate="readiness")


class Gate9GapZero(_GateCriterion):
    criterion_id = "CC-9"
    description = "Gate 9 Gap = 0 — no open gap at any tier/dimension."

    def evaluate(self, subject: CertificationSubject) -> CertificationFinding:
        failed = int(subject.counts.get("failed", 0))
        if failed:
            return self._failed("gap gate: open gaps remain", failed=failed)
        return self._passed(gate="gap-zero")


class Gate10Completeness(_GateCriterion):
    criterion_id = "CC-10"
    description = "Gate 10 Completeness Certified — Gates 1-9 closed; certification sound."

    def evaluate(self, subject: CertificationSubject) -> CertificationFinding:
        failed = int(subject.counts.get("failed", 0))
        if not (subject.validation_accepted and subject.evidence_present and failed == 0):
            return self._failed(
                "completeness gate: prerequisite gates not all closed",
                accepted=subject.validation_accepted,
                evidence=subject.evidence_present,
                failed=failed,
            )
        return self._passed(gate="completeness")


def cce_gates() -> tuple[CertificationCriterion, ...]:
    """The CCE ten-gate certification suite (CC-1…CC-10), all blocking."""
    return (
        Gate1Architecture(),
        Gate2Dependencies(),
        Gate3Coverage(),
        Gate4Validation(),
        Gate5Traceability(),
        Gate6Evidence(),
        Gate7CertificationReady(),
        Gate8Readiness(),
        Gate9GapZero(),
        Gate10Completeness(),
    )


# ---------------------------------------------------------------------------
# INFRASTRUCTURE-001 §12 — Infrastructure compliance (C1…C7)
# ---------------------------------------------------------------------------

_COMPLIANCE_CHECKS: dict[str, tuple[str, ...]] = {
    "C1": ("infra-topology-typed", "infra-topology-identified-objectbound"),
    "C2": ("foundation-reuse-integrity",),
    "C3": ("infra-topology-distribution-hosts",),
    "C4": ("infra-topology-distribution-hosts",),
    "C5": ("founding-acyclic", "meta-relationships-closed"),
    "C6": ("infra-topology-distribution-hosts", "lifecycle-valid"),
    "C7": ("technology-independence", "non-constitutive"),
}

_COMPLIANCE_CONDITIONS: tuple[dict[str, Any], ...] = (
    {
        "id": "C1",
        "description": INFRASTRUCTURE_COMPLIANCE["C1"],
        "validation": list(_COMPLIANCE_CHECKS["C1"]),
    },
    {
        "id": "C2",
        "description": INFRASTRUCTURE_COMPLIANCE["C2"],
        "validation": list(_COMPLIANCE_CHECKS["C2"]),
    },
    {
        "id": "C3",
        "description": INFRASTRUCTURE_COMPLIANCE["C3"],
        "validation": list(_COMPLIANCE_CHECKS["C3"]),
    },
    {
        "id": "C4",
        "description": INFRASTRUCTURE_COMPLIANCE["C4"],
        "validation": list(_COMPLIANCE_CHECKS["C4"]),
    },
    {
        "id": "C5",
        "description": INFRASTRUCTURE_COMPLIANCE["C5"],
        "validation": list(_COMPLIANCE_CHECKS["C5"]),
    },
    {
        "id": "C6",
        "description": INFRASTRUCTURE_COMPLIANCE["C6"],
        "validation": list(_COMPLIANCE_CHECKS["C6"]),
    },
    {
        "id": "C7",
        "description": INFRASTRUCTURE_COMPLIANCE["C7"],
        "validation": list(_COMPLIANCE_CHECKS["C7"]),
    },
)


def _decide_compliance(subject: CertificationSubject) -> list[dict[str, Any]]:
    """Decide all seven compliance conditions from the certification findings."""
    results: list[dict[str, Any]] = []
    for cond in _COMPLIANCE_CONDITIONS:
        check_ids = cond["validation"]
        satisfied = all(
            cid in subject.checks_run and cid not in subject.blocking_failures
            for cid in check_ids
        )
        results.append({
            "id": cond["id"],
            "status": "pass" if satisfied else "fail",
            "validation_checks": check_ids,
        })
    return results


@dataclass(frozen=True, slots=True)
class ComplianceVerdict:
    """The Infrastructure-compliance verdict (C1…C7), decided from certification data."""

    conditions: tuple[dict[str, Any], ...]

    @property
    def compliant(self) -> bool:
        return all(c["status"] == "pass" for c in self.conditions)

    def to_dict(self) -> dict[str, Any]:
        return {
            "standard": "INFRASTRUCTURE-001 §12 (C1…C7)",
            "compliant": self.compliant,
            "conditions": list(self.conditions),
        }


@dataclass(frozen=True, slots=True)
class TopologyCertification:
    """The bundled certification outcome for a construct."""

    decision: CertificationDecision
    evidence: CertificationEvidence
    compliance: ComplianceVerdict

    @property
    def certified(self) -> bool:
        return self.decision.certified


def certify_construct(
    validation: TopologyValidation,
    *,
    version: str = "1.0.0",
    ledger: CertificationLedger | None = None,
    blueprint_id: str = "Topology",
) -> TopologyCertification:
    """Certify a validated construct through the EC-1 CCE engine and ledger it."""
    from engine.certification.contracts import (
        CERTIFICATION_AUTHORITY,
        CERTIFICATION_STANDARD,
        CERTIFICATION_STANDARD_VERSION,
        CertificationRecord,
        CertificationStatus,
        content_hash,
    )
    checks_run = tuple(f.check_id for f in validation.report.findings)
    blocking_failures = tuple(
        f.check_id for f in validation.report.findings if f.is_blocking_failure
    )
    evidence_present = bool(validation.evidence.checks_run)
    evidence_sha256 = content_hash(dict(
        checks_run=validation.evidence.checks_run,
        counts=validation.evidence.counts,
        target_id=validation.evidence.target_id,
    ))
    subject = CertificationSubject(
        target_id=validation.report.target_id,
        blueprint_id=blueprint_id,
        version=version,
        certification_class=CertificationClass.ENGINEERING_READINESS,
        validation_verdict=validation.report.verdict.value,
        validation_accepted=validation.decision.accepted,
        checks_run=checks_run,
        blocking_failures=blocking_failures,
        counts=validation.report.counts(),
        evidence_present=evidence_present,
        evidence_sha256=evidence_sha256,
    )
    engine = CertificationEngine(cce_gates())
    decision = engine.certify(subject)
    evidence = build_certification_evidence(decision)
    compliance = ComplianceVerdict(
        conditions=tuple(_decide_compliance(subject))
    )
    if ledger is not None:
        status = CertificationStatus.CERTIFIED if decision.certified else CertificationStatus.NOT_CERTIFIED
        record = CertificationRecord.create(
            target_id=subject.target_id,
            blueprint_id=subject.blueprint_id,
            version=version,
            status=status,
            certification_class=CertificationClass.ENGINEERING_READINESS,
            evidence_ref=evidence_sha256,
            criteria=decision.findings,
            disclosure={"disclosure_id": "ec3-b13-u06-provisional"},
            standard=CERTIFICATION_STANDARD,
            standard_version=CERTIFICATION_STANDARD_VERSION,
            authority=CERTIFICATION_AUTHORITY,
        )
        ledger.append(record)
    return TopologyCertification(decision=decision, evidence=evidence, compliance=compliance)


__all__ = [
    "cce_gates",
    "ComplianceVerdict",
    "TopologyCertification",
    "certify_construct",
]
