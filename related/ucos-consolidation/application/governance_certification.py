"""EC3-B12-U10 — Governance certification (CCE ten gates CC-1…CC-10 + Application C1…C7).

Certification is *aggregation, not re-judgment* (TP-01 soundness): every gate below reads only
the outcome of the governance-layer validation (:mod:`application.governance_validation`) and
never re-inspects the record. It runs through the **CERTIFIED EC-1 Certification Engine**
(:class:`engine.certification.engine.CertificationEngine`), issues an immutable,
content-addressed record, and appends it to the append-only, hash-chained EC-1
:class:`~engine.certification.ledger.CertificationLedger`.

Two evidence families are produced:

* **CC-1…CC-10** — the CCE ten-gate certification (EC-3 AP-4 §8.4), realized as ten blocking
  :class:`~engine.certification.criteria.CertificationCriterion` aggregating the validation
  verdict, evidence, traceability, disclosure, and gap signals. All ten CLOSED →
  ``CertificationStatus.CERTIFIED`` → ledgered.
* **C1…C7** — the APPLICATION-001 §12 Application-compliance conditions, decided on the same
  validation evidence, deterministically and non-coercively (UAL-14).

Certification records **engineering readiness only** (CCE-LAW-009 / DE-05): it asserts no
constitutional finality (the EC-1 provisional-state disclosure is embedded in every record).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from application.governance_meta import APPLICATION_COMPLIANCE
from application.governance_validation import GovernanceValidation

# --- EC-1 reuse by reference (UAL-02) — the certified certification substrate -----
from engine.certification.contracts import (
    CertificationFinding,
    CertificationSubject,
    CriterionSeverity,
    CriterionStatus,
)
from engine.certification.criteria import CertificationCriterion
from engine.certification.engine import CertificationDecision, CertificationEngine
from engine.certification.evidence import CertificationEvidence, build_certification_evidence
from engine.certification.ledger import CertificationLedger, CertificationLedgerEntry

# ---------------------------------------------------------------------------
# CCE ten-gate criteria (CC-1…CC-10) — pure aggregation over validation output
# ---------------------------------------------------------------------------


class _GateCriterion(CertificationCriterion):
    """Base for a CCE gate that aggregates one or more validation check outcomes."""

    severity = CriterionSeverity.BLOCKING
    #: The validation check ids this gate requires (ran and did not block).
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
    description = "Gate 1 Architecture — no orphan (Governance traces the Universe→Code spine)."
    required_checks = ("traceability-rooted", "meta-class-single")

    def evaluate(self, subject: CertificationSubject) -> CertificationFinding:
        ok, problems = self._checks_ok(subject)
        return self._passed(gate="architecture") if ok else self._failed(
            "architecture gate: orphan/meta-class defect", problems=problems
        )


class Gate2Dependencies(_GateCriterion):
    criterion_id = "CC-2"
    description = "Gate 2 Dependencies Closed — digest-pinned closure over the frozen substrate."
    required_checks = ("foundation-reuse-integrity", "governance-behavior-by-reference")

    def evaluate(self, subject: CertificationSubject) -> CertificationFinding:
        ok, problems = self._checks_ok(subject)
        return self._passed(gate="dependencies") if ok else self._failed(
            "dependencies gate: substrate closure defect", problems=problems
        )


class Gate3Coverage(_GateCriterion):
    criterion_id = "CC-3"
    description = "Gate 3 Coverage — deterministic; no structural violation."
    required_checks = (
        "governance-value-fidelity",
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
    description = "Gate 7 Certification-Ready — provisional-state disclosed; criteria satisfiable."
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
    description = "Gate 10 Completeness Certified — Gates 1–9 closed; certification sound."

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
# APPLICATION-001 §12 — Application compliance (C1…C7)
# ---------------------------------------------------------------------------

#: Each compliance condition and the validation check ids that substantiate it. For the
#: Governance record, **C7 (selects no technology, confers no authority, embeds no secret —
#: UAL-15 — together with the declarative, record-only, non-enforcing nature — UAL-14) is THE
#: governing materially-exercised condition** of AMC-10: the record classifies conformance/
#: lifecycle/policy concerns and enacts nothing (approves/enforces/ratifies nothing). C6
#: (workflow/state bind RL-F2 — UAL-10/12) is materially exercised through the
#: governance-evaluate RL-F2 binding + forward-only lifecycle. C3 (capability delivered via SF-2
#: + DF-2 data by reference — UAL-06/13) is scoped to the Feature/Capability units (AMC-02/04);
#: a governance record consumes no operation and presents no data — satisfied structurally
#: against the governed constructs (AMR-09) and recorded with a note. C4 (modules bounded,
#: features explicit, interactions typed — UAL-07/08/11) is scoped to the Module/Feature/
#: Interaction units; the governance analog is materially exercised — the record governs declared
#: application boundaries with a typed concern (AMR-09 / GOV-07). C5 (composition ENG-005 refs +
#: founding acyclic — UAL-09) is scoped to the Composition unit; the governance analog is
#: materially exercised — the record binds all links by ENG-005 reference and participates in no
#: founding edge (vacuously acyclic).
_COMPLIANCE_CHECKS: dict[str, tuple[str, ...]] = {
    "C1": ("governance-typed", "governance-identified-objectbound"),
    "C2": ("foundation-reuse-integrity",),
    "C3": ("governance-governs-boundary",),
    "C4": ("governance-governs-boundary", "governance-classified"),
    "C5": (
        "governance-no-new-connection",
        "founding-acyclic",
        "meta-relationships-closed",
    ),
    "C6": ("governance-behavior-by-reference", "lifecycle-valid"),
    "C7": (
        "non-constitutive",
        "technology-independence",
        "governance-evaluative-nonenforcing",
    ),
}

_C3_NOTE = (
    "capability delivery via SF-2 operations + DF-2 data (UAL-06/13) is scoped to the "
    "Feature/Capability units (AMC-02/04); a governance record records conformance/lifecycle/"
    "policy judgments against constructs that deliver — it consumes no operation and presents no "
    "data itself, so C3 is satisfied structurally via the governed constructs (AMR-09 / GOV-07)"
)
_C4_NOTE = (
    "the module/feature/interaction clauses (UAL-07/08/11) are scoped to the Module (AMC-03), "
    "Feature (AMC-04), and Interaction (AMC-06) units; the governance analog is materially "
    "exercised — the record governs declared application boundaries with a typed concern "
    "(AMR-09 / GOV-07)"
)
_C5_NOTE = (
    "the composition clause (UAL-09) is scoped to the Composition unit (AMC-08); the governance "
    "analog is materially exercised — the record binds every governed/security/state/behavior "
    "link by ENG-005 reference and participates in no founding edge (founding graph vacuously "
    "acyclic)"
)
_C6_NOTE = (
    "materially exercised — the governance-evaluate behavior binds the frozen RL-F2 RUNTIME "
    "policy concern by reference (§7 / AMK-05) and the record advances forward-only through the "
    "AOS-01…06 lifecycle (UAL-10/12)"
)
_C7_NOTE = (
    "materially exercised — THE governing condition of AMC-10: the record is declarative, "
    "record-only, and non-enforcing (UAL-14), approves/enforces/ratifies nothing (GOV-04 / "
    "GOV-C2), selects no workflow-approval/policy-enforcement technology (GOV-K5), confers no "
    "authority and embeds no secret (UAL-15 / GOV-09 / RR-07)"
)


@dataclass(frozen=True, slots=True)
class GovernanceComplianceReport:
    """A deterministic APPLICATION-001 §12 compliance report (C1…C7)."""

    target_id: str
    conditions: tuple[dict[str, Any], ...]

    @property
    def compliant(self) -> bool:
        return all(c["status"] == "pass" for c in self.conditions)

    def to_dict(self) -> dict[str, Any]:
        return {
            "compliance_format": "ucos-application-compliance/1.0.0",
            "standard": "APPLICATION-001 §12",
            "target_id": self.target_id,
            "compliant": self.compliant,
            "conditions": [dict(c) for c in self.conditions],
        }


def evaluate_governance_compliance(
    validation: GovernanceValidation,
) -> GovernanceComplianceReport:
    """Decide the C1…C7 compliance of the validated governance record on validation evidence."""
    passed = {f.check_id: f.passed for f in validation.report.findings}
    conditions: list[dict[str, Any]] = []
    for cid, checks in _COMPLIANCE_CHECKS.items():
        ok = all(passed.get(c, False) for c in checks)
        entry: dict[str, Any] = {
            "id": cid,
            "requirement": APPLICATION_COMPLIANCE[cid],
            "status": "pass" if ok else "fail",
            "backed_by": list(checks),
        }
        if cid == "C3":
            entry["note"] = _C3_NOTE
        elif cid == "C4":
            entry["note"] = _C4_NOTE
        elif cid == "C5":
            entry["note"] = _C5_NOTE
        elif cid == "C6":
            entry["note"] = _C6_NOTE
        elif cid == "C7":
            entry["note"] = _C7_NOTE
        conditions.append(entry)
    return GovernanceComplianceReport(
        target_id=validation.report.target_id, conditions=tuple(conditions)
    )


# ---------------------------------------------------------------------------
# Orchestrated certification
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class GovernanceCertification:
    """The bundled outcome of certifying a validated Governance record."""

    decision: CertificationDecision
    evidence: CertificationEvidence
    ledger_entry: CertificationLedgerEntry
    ledger: CertificationLedger
    compliance: GovernanceComplianceReport

    @property
    def certified(self) -> bool:
        return self.decision.certified and self.ledger.verify() and self.compliance.compliant


def certify_governance(
    validation: GovernanceValidation,
    *,
    version: str,
    ledger: CertificationLedger | None = None,
) -> GovernanceCertification:
    """Run the CCE ten gates + C1…C7 over a validated governance record and ledger the record.

    Reuses the CERTIFIED EC-1 certification engine and append-only ledger. The result is
    CERTIFIED iff all ten gates close, the ledger chain is intact, and the record is
    Application-COMPLIANT (C1…C7).
    """
    subject = CertificationSubject.from_validation(
        validation.report, validation.evidence, version=version
    )
    decision = CertificationEngine(cce_gates()).certify(subject)
    active_ledger = ledger if ledger is not None else CertificationLedger()
    entry = active_ledger.append(decision.record)
    active_ledger.require_intact()
    cert_evidence = build_certification_evidence(decision)
    compliance = evaluate_governance_compliance(validation)
    return GovernanceCertification(
        decision=decision,
        evidence=cert_evidence,
        ledger_entry=entry,
        ledger=active_ledger,
        compliance=compliance,
    )


__all__ = [
    "cce_gates",
    "GovernanceComplianceReport",
    "evaluate_governance_compliance",
    "GovernanceCertification",
    "certify_governance",
    "CriterionStatus",
]
