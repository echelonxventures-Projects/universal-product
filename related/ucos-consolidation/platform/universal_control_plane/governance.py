"""UCOS-CTRL-000001 — Universal Governance Engine (Wave 2).

Every object the control plane holds must be able to answer *am I governed, and
if not, which declared rule do I fail*. This engine is that answer.

It invents no governance vocabulary. The verdict tokens, the stage roll-up and
the self-verifying repository decision all come from :mod:`engine.governance`,
the repository's canonical governance layer; what this engine adds is the thing
that layer never had — a per-object resolution over an *open* rule set, so a
capability, an artifact, an engine and a backlog item are all adjudicated by the
same declared rules without any of them being special-cased in code.

The rules themselves live in the declared manifest. A rule names the fact its
subject must carry (``owner``, ``registration``, ``version``, ``canonical_home``,
``evidence``, or any fact a specialised manifest invents), and unknown facts
resolve against the subject's own declared fact bag — so extending governance is
a document edit, not a patch.

Resolution is fail-closed: a subject that carries none of the required facts is
NOT-GOVERNED, never governed-by-default, and a subject nobody ever resolved is
UNGOVERNED rather than assumed fine.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from contextlib import suppress
from dataclasses import dataclass, field
from platform.universal_control_plane.errors import (
    DuplicateObjectError,
    GovernanceStateError,
    ObjectNotFoundError,
)
from platform.universal_control_plane.manifest import ControlPlaneManifest, Rule, default_manifest
from platform.universal_control_plane.ontology import (
    GOVERNANCE_GOVERNED,
    GOVERNANCE_NOT_GOVERNED,
    GOVERNANCE_UNGOVERNED,
    LIFECYCLE_DRAFT,
    ArtifactRecord,
    Determination,
    Evidence,
    GovernanceRecord,
    GovernanceViolation,
    HistoryEntry,
    payload_digest,
)
from platform.universal_control_plane.state import StateEngine
from typing import Any

#: History events this engine appends. Open tokens, like every other vocabulary here.
EVENT_GOVERNANCE_RESOLVED = "GOVERNANCE_RESOLVED"
EVENT_GOVERNANCE_VIOLATED = "GOVERNANCE_VIOLATED"
EVENT_GOVERNANCE_TRANSITIONED = "GOVERNANCE_TRANSITIONED"

#: Verdict tokens for the determination this engine records per subject.
VERDICT_AUTHORIZED = "AUTHORIZED"
VERDICT_BLOCKED = "BLOCKED"


@dataclass(frozen=True)
class GovernanceSubject:
    """The normalised fact bag any control-plane object presents to governance.

    Governance never reaches into an object's own type. Every object — a
    discovered artifact, a registered engine, a backlog item — projects itself
    into this one shape, which is what lets a single declared rule set adjudicate
    all of them.
    """

    subject_id: str
    kind: str
    owner: str = ""
    registered: bool = False
    version: str = ""
    canonical_home: bool = True
    evidence_ids: tuple[str, ...] = ()
    lifecycle_state: str = LIFECYCLE_DRAFT
    facts: Mapping[str, Any] = field(default_factory=dict)

    @classmethod
    def from_artifact(cls, artifact: ArtifactRecord) -> GovernanceSubject:
        """Project a discovered repository artifact into a governance subject.

        ``canonical_home`` carries the Repository Truth verdict directly: an
        artifact homed in a class that cannot own (evidence, derived output,
        historical state) fails the canonical-home rule rather than being quietly
        admitted.
        """
        return cls(
            subject_id=artifact.artifact_id,
            kind="Artifact",
            owner=artifact.owner,
            registered=bool(artifact.artifact_id),
            version=artifact.version,
            canonical_home=artifact.canonical_home_eligible,
            evidence_ids=artifact.traceability,
            lifecycle_state=artifact.status or LIFECYCLE_DRAFT,
            facts={
                "category": artifact.category,
                "truth_class": artifact.truth_class,
                "classes": list(artifact.classes),
                "content_digest": artifact.content_digest,
            },
        )

    def fact(self, name: str) -> Any:
        """Resolve a declared fact by name, falling back to the open fact bag."""
        resolver = _FACT_RESOLVERS.get(name)
        if resolver is not None:
            return resolver(self)
        return self.facts.get(name)

    def to_dict(self) -> dict[str, Any]:
        return {
            "subject_id": self.subject_id,
            "kind": self.kind,
            "owner": self.owner,
            "registered": self.registered,
            "version": self.version,
            "canonical_home": self.canonical_home,
            "evidence_ids": list(self.evidence_ids),
            "lifecycle_state": self.lifecycle_state,
            "facts": dict(self.facts),
        }


#: The facts the shipped rule vocabulary names. Anything else a manifest declares
#: resolves against the subject's open fact bag, so new rules need no code.
_FACT_RESOLVERS: Mapping[str, Callable[[GovernanceSubject], Any]] = {
    "owner": lambda s: bool(s.owner.strip()),
    "registration": lambda s: bool(s.registered),
    "version": lambda s: bool(s.version.strip()),
    "canonical_home": lambda s: bool(s.canonical_home),
    "evidence": lambda s: bool(s.evidence_ids),
}


@dataclass
class GovernanceEngine:
    """Resolves, tracks and rolls up governance state for every control-plane object.

    Wire the traceability engines in and every resolution also lands as a
    determination, an evidence record and a history entry — governance that is
    auditable after the fact rather than only assertable in the moment.
    """

    manifest: ControlPlaneManifest = field(default_factory=default_manifest)
    state_engine: StateEngine = field(default_factory=StateEngine)
    determination_engine: Any = None
    evidence_engine: Any = None
    history_engine: Any = None
    _records: dict[str, GovernanceRecord] = field(default_factory=dict)
    _violations: dict[str, GovernanceViolation] = field(default_factory=dict)
    _subjects: dict[str, GovernanceSubject] = field(default_factory=dict)
    _history: list[HistoryEntry] = field(default_factory=list)
    _evidence: list[Evidence] = field(default_factory=list)
    _determinations: list[Determination] = field(default_factory=list)

    # -- rules -----------------------------------------------------------

    @property
    def rules(self) -> tuple[Rule, ...]:
        return self.manifest.governance_rules

    def rule(self, rule_id: str) -> Rule:
        for rule in self.rules:
            if rule.rule_id == rule_id:
                return rule
        raise ObjectNotFoundError(f"governance rule not declared: {rule_id}")

    # -- resolution ------------------------------------------------------

    def resolve(self, subject: GovernanceSubject, *, tick: int = 0) -> GovernanceRecord:
        """Adjudicate *subject* against every declared rule and record the outcome."""
        if not subject.subject_id.strip():
            raise GovernanceStateError("governance subject requires a non-empty subject_id")

        satisfied: list[str] = []
        violations: list[GovernanceViolation] = []
        for rule in self.rules:
            if bool(subject.fact(rule.requires)):
                satisfied.append(rule.rule_id)
                continue
            violations.append(
                GovernanceViolation(
                    violation_id=f"VIO-{subject.subject_id}-{rule.rule_id}",
                    subject_id=subject.subject_id,
                    rule_id=rule.rule_id,
                    severity=rule.severity,
                    message=rule.message,
                    attributes={"requires": rule.requires, "subject_kind": subject.kind},
                    tick=tick,
                )
            )

        blocking = tuple(v.rule_id for v in violations if v.blocking)
        status = GOVERNANCE_NOT_GOVERNED if blocking else GOVERNANCE_GOVERNED
        rationale = (
            "every declared governance rule is satisfied"
            if not violations
            else "blocking rules failed: " + ", ".join(blocking)
            if blocking
            else "advisory rules failed: " + ", ".join(v.rule_id for v in violations)
        )

        for violation in violations:
            self._violations[violation.violation_id] = violation
            self._append_history(
                subject.subject_id,
                EVENT_GOVERNANCE_VIOLATED,
                f"{violation.rule_id} ({violation.severity}): {violation.message}",
                tick=tick,
            )

        determination_id = self._record_determination(
            subject, status, rationale, blocking, tick=tick
        )
        evidence_ids = self._record_evidence(subject, status, violations, tick=tick)

        record = GovernanceRecord(
            record_id=f"GOV-{subject.subject_id}",
            subject_id=subject.subject_id,
            status=status,
            lifecycle_state=subject.lifecycle_state,
            satisfied_rules=tuple(satisfied),
            violation_ids=tuple(v.violation_id for v in violations),
            evidence_ids=tuple(evidence_ids),
            determination_id=determination_id,
            rationale=rationale,
            attributes={"subject_kind": subject.kind, "blocking": list(blocking)},
            tick=tick,
        )
        self._records[subject.subject_id] = record
        self._subjects[subject.subject_id] = subject
        self._append_history(
            subject.subject_id, EVENT_GOVERNANCE_RESOLVED, f"{status}: {rationale}", tick=tick
        )
        return record

    def resolve_all(
        self, subjects: Iterable[GovernanceSubject], *, tick: int = 0
    ) -> tuple[GovernanceRecord, ...]:
        """Resolve a whole population, in a deterministic order."""
        return tuple(
            self.resolve(subject, tick=tick)
            for subject in sorted(subjects, key=lambda s: s.subject_id)
        )

    # -- recording helpers -----------------------------------------------

    def _record_determination(
        self,
        subject: GovernanceSubject,
        status: str,
        rationale: str,
        blocking: tuple[str, ...],
        *,
        tick: int,
    ) -> str:
        determination = Determination(
            determination_id=f"DET-GOV-{subject.subject_id}",
            subject_id=subject.subject_id,
            verdict=VERDICT_AUTHORIZED if status == GOVERNANCE_GOVERNED else VERDICT_BLOCKED,
            rationale=rationale,
            attributes={"governance_status": status, "blocking_rules": list(blocking)},
            tick=tick,
        )
        self._determinations.append(determination)
        if self.determination_engine is not None:
            # Re-resolving a subject re-derives the same determination id. The
            # append-only engine refusing that duplicate is its contract being
            # honoured, not a governance fault, so it is suppressed here rather
            # than propagated to a caller who did nothing wrong.
            with suppress(DuplicateObjectError):
                self.determination_engine.record(determination)
        return determination.determination_id

    def _record_evidence(
        self,
        subject: GovernanceSubject,
        status: str,
        violations: list[GovernanceViolation],
        *,
        tick: int,
    ) -> list[str]:
        payload = {
            "subject": subject.to_dict(),
            "status": status,
            "violations": [v.to_dict() for v in violations],
        }
        evidence = Evidence(
            evidence_id=f"EV-GOV-{subject.subject_id}",
            subject_id=subject.subject_id,
            kind="GOVERNANCE",
            claim=f"governance resolved as {status} over {len(self.rules)} declared rules",
            payload_digest=payload_digest(payload),
            attributes={"rule_count": len(self.rules)},
            tick=tick,
        )
        self._evidence.append(evidence)
        if self.evidence_engine is not None:
            with suppress(DuplicateObjectError):  # see _record_determination
                self.evidence_engine.record(evidence)
        return [evidence.evidence_id]

    def _append_history(self, subject_id: str, event: str, detail: str, *, tick: int) -> None:
        entry = HistoryEntry(
            entry_id=f"HIS-GOV-{subject_id}-{len(self._history)}",
            subject_id=subject_id,
            event=event,
            detail=detail,
            actor_id="GovernanceEngine",
            tick=tick,
        )
        self._history.append(entry)
        if self.history_engine is not None:
            self.history_engine.append(entry)

    # -- lifecycle -------------------------------------------------------

    def advance(self, subject_id: str, event: str, *, tick: int = 0) -> GovernanceRecord:
        """Fire a lifecycle *event* against a resolved subject's governance state."""
        record = self.state_of(subject_id)
        next_state = self.state_engine.transition(record.lifecycle_state, event)
        advanced = GovernanceRecord(
            record_id=record.record_id,
            subject_id=record.subject_id,
            status=record.status,
            lifecycle_state=next_state,
            satisfied_rules=record.satisfied_rules,
            violation_ids=record.violation_ids,
            evidence_ids=record.evidence_ids,
            determination_id=record.determination_id,
            rationale=record.rationale,
            attributes=record.attributes,
            tick=tick,
        )
        self._records[subject_id] = advanced
        self._append_history(
            subject_id,
            EVENT_GOVERNANCE_TRANSITIONED,
            f"{record.lifecycle_state} --{event}--> {next_state}",
            tick=tick,
        )
        return advanced

    # -- queries ---------------------------------------------------------

    def state_of(self, subject_id: str) -> GovernanceRecord:
        """The resolved governance state of *subject_id*; raises when never resolved."""
        if subject_id not in self._records:
            raise ObjectNotFoundError(f"no governance state resolved for: {subject_id}")
        return self._records[subject_id]

    def status_of(self, subject_id: str) -> str:
        """The governance status of *subject_id*, UNGOVERNED when never resolved.

        The non-raising counterpart of :meth:`state_of`: an object nobody governed
        is reported as ungoverned, which is a governance answer, not an absence.
        """
        record = self._records.get(subject_id)
        return record.status if record is not None else GOVERNANCE_UNGOVERNED

    def governed(self) -> tuple[GovernanceRecord, ...]:
        return tuple(
            sorted((r for r in self._records.values() if r.governed), key=lambda r: r.subject_id)
        )

    def not_governed(self) -> tuple[GovernanceRecord, ...]:
        return tuple(
            sorted(
                (r for r in self._records.values() if not r.governed), key=lambda r: r.subject_id
            )
        )

    def violations(self, subject_id: str | None = None) -> tuple[GovernanceViolation, ...]:
        pool = self._violations.values()
        if subject_id is not None:
            pool = [v for v in pool if v.subject_id == subject_id]
        return tuple(sorted(pool, key=lambda v: v.violation_id))

    def blocking_violations(self) -> tuple[GovernanceViolation, ...]:
        return tuple(v for v in self.violations() if v.blocking)

    def history(self, subject_id: str | None = None) -> tuple[HistoryEntry, ...]:
        if subject_id is None:
            return tuple(self._history)
        return tuple(e for e in self._history if e.subject_id == subject_id)

    def evidence(self, subject_id: str | None = None) -> tuple[Evidence, ...]:
        if subject_id is None:
            return tuple(self._evidence)
        return tuple(e for e in self._evidence if e.subject_id == subject_id)

    def determinations(self, subject_id: str | None = None) -> tuple[Determination, ...]:
        if subject_id is None:
            return tuple(self._determinations)
        return tuple(d for d in self._determinations if d.subject_id == subject_id)

    def subjects(self) -> tuple[GovernanceSubject, ...]:
        return tuple(sorted(self._subjects.values(), key=lambda s: s.subject_id))

    def count(self) -> int:
        return len(self._records)

    # -- repository roll-up ----------------------------------------------

    def decision(
        self,
        *,
        repository_id: str = "",
        epic_id: str = "UCOS-CTRL-000001",
        certification_failures: tuple[str, ...] = (),
        certification_total: int | None = None,
        acceptance_failures: tuple[str, ...] = (),
        acceptance_total: int | None = None,
    ) -> Any:
        """Roll the per-object states up into the repository's canonical decision.

        Reuses :class:`engine.governance.contracts.RepositoryDecision` rather than
        inventing a second repository verdict: the control plane's governance
        answer is expressed in the same self-verifying, disclosure-carrying type
        the rest of the repository already adjudicates with.

        Certification and acceptance are supplied by the caller because governance
        is upstream of both. Supplying nothing leaves those stages empty, and an
        empty stage never passes vacuously — the roll-up stays fail-closed.
        """
        from engine.governance.contracts import RepositoryDecision, StageOutcome
        from engine.runtime.disclosure import build_disclosure

        validation = StageOutcome.of(
            "validation",
            total=self.count(),
            failures=tuple(r.subject_id for r in self.not_governed()),
        )
        certification = StageOutcome.of(
            "certification",
            total=self.count() if certification_total is None else certification_total,
            failures=tuple(certification_failures),
        )
        acceptance = StageOutcome.of(
            "acceptance",
            total=self.count() if acceptance_total is None else acceptance_total,
            failures=tuple(acceptance_failures),
        )
        return RepositoryDecision.create(
            repository_id=repository_id or self.manifest.universe_id,
            epic_id=epic_id,
            validation=validation,
            certification=certification,
            acceptance=acceptance,
            disclosure=build_disclosure(),
        )

    # -- projection ------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        return {
            "engine": "GovernanceEngine",
            "manifest_id": self.manifest.manifest_id,
            "rules": [r.to_dict() for r in self.rules],
            "counts": {
                "resolved": self.count(),
                "governed": len(self.governed()),
                "not_governed": len(self.not_governed()),
                "violations": len(self._violations),
                "blocking_violations": len(self.blocking_violations()),
                "history": len(self._history),
                "evidence": len(self._evidence),
            },
            "records": [
                r.to_dict() for r in sorted(self._records.values(), key=lambda r: r.record_id)
            ],
            "violations": [v.to_dict() for v in self.violations()],
        }


def governance_subjects(artifacts: Iterable[ArtifactRecord]) -> tuple[GovernanceSubject, ...]:
    """Project discovered artifacts into governance subjects, deterministically."""
    return tuple(
        sorted(
            (GovernanceSubject.from_artifact(a) for a in artifacts),
            key=lambda s: s.subject_id,
        )
    )


__all__ = [
    "EVENT_GOVERNANCE_RESOLVED",
    "EVENT_GOVERNANCE_TRANSITIONED",
    "EVENT_GOVERNANCE_VIOLATED",
    "VERDICT_AUTHORIZED",
    "VERDICT_BLOCKED",
    "GovernanceEngine",
    "GovernanceSubject",
    "governance_subjects",
]
