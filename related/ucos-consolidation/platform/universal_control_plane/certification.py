"""UCOS-CTRL-000001 — Universal Certification Engine (Wave 3).

Certification asks a narrower question than governance: not *does this object
obey the rules* but *has it earned a seal, and may it be offered for one at all*.
Those are two different verdicts and this engine keeps them apart —
**eligibility** is the prior gate (an ungoverned object may not be offered for
certification, whatever else is true of it), **status** is the outcome once it
has been.

The seal itself is not re-invented. Every assessment issues a real
:class:`engine.certification.contracts.CertificationRecord` — the repository's
canonical, content-addressed, disclosure-carrying certificate — built from the
criteria this engine evaluated. A control-plane certification is therefore the
same artifact type the rest of the repository already trusts, not a lookalike.

Criteria are declared, not coded. Each names the fact its subject must carry and
whether failing it blocks or is advisory; a specialised manifest adds criteria
without touching this module.

History and lineage are append-only. Re-assessing a subject never overwrites its
prior state: the new state records the previous one as its parent, so a subject's
certification lineage is a chain that can be walked back to its first seal.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from contextlib import suppress
from dataclasses import dataclass, field
from platform.universal_control_plane.errors import (
    CertificationStateError,
    DuplicateObjectError,
    ObjectNotFoundError,
)
from platform.universal_control_plane.manifest import ControlPlaneManifest, Rule, default_manifest
from platform.universal_control_plane.ontology import (
    CERTIFICATION_CERTIFIED,
    CERTIFICATION_NOT_CERTIFIED,
    CERTIFICATION_UNCERTIFIED,
    CRITERION_BLOCKING,
    CertificationState,
    CriterionOutcome,
    Evidence,
    GovernanceRecord,
    HistoryEntry,
    payload_digest,
)
from typing import Any

#: The gateway fact: an object that is not governed is not eligible for a seal.
ELIGIBILITY_FACT = "governed"

EVENT_CERTIFICATION_ASSESSED = "CERTIFICATION_ASSESSED"

#: The blueprint identifier every control-plane certificate is issued against.
#: Certification records readiness of a *control-plane object*, so they share one
#: blueprint and are told apart by target.
CONTROL_PLANE_BLUEPRINT = "UCOS-CTRL-000001"


@dataclass(frozen=True)
class CertificationSubject:
    """The normalised fact bag any control-plane object presents to certification."""

    subject_id: str
    kind: str = "Object"
    governed: bool = False
    critical_violations: int = 0
    version: str = ""
    evidence_ids: tuple[str, ...] = ()
    lineage: tuple[str, ...] = ()
    facts: Mapping[str, Any] = field(default_factory=dict)

    @classmethod
    def from_governance(
        cls,
        record: GovernanceRecord,
        *,
        version: str = "",
        kind: str = "Object",
        lineage: tuple[str, ...] = (),
    ) -> CertificationSubject:
        """Project a resolved governance record into a certification subject.

        The count of *blocking* violations travels with the subject rather than
        being recomputed here: governance already adjudicated severity, and a
        second opinion on the same rule set would be a second authority over it.
        """
        blocking = tuple(record.attributes.get("blocking", ()) or ())
        return cls(
            subject_id=record.subject_id,
            kind=str(record.attributes.get("subject_kind", kind)),
            governed=record.governed,
            critical_violations=len(blocking),
            version=version,
            evidence_ids=record.evidence_ids,
            lineage=lineage,
            facts={"governance_status": record.status, "lifecycle": record.lifecycle_state},
        )

    def fact(self, name: str) -> Any:
        resolver = _FACT_RESOLVERS.get(name)
        if resolver is not None:
            return resolver(self)
        return self.facts.get(name)

    def to_dict(self) -> dict[str, Any]:
        return {
            "subject_id": self.subject_id,
            "kind": self.kind,
            "governed": self.governed,
            "critical_violations": self.critical_violations,
            "version": self.version,
            "evidence_ids": list(self.evidence_ids),
            "lineage": list(self.lineage),
            "facts": dict(self.facts),
        }


_FACT_RESOLVERS: Mapping[str, Callable[[CertificationSubject], Any]] = {
    "governed": lambda s: bool(s.governed),
    "no_critical_violation": lambda s: s.critical_violations == 0,
    "version": lambda s: bool(s.version.strip()),
    "evidence": lambda s: bool(s.evidence_ids),
    "lineage": lambda s: bool(s.lineage),
}


@dataclass
class CertificationEngine:
    """Determines certification status, eligibility, history, evidence and lineage."""

    manifest: ControlPlaneManifest = field(default_factory=default_manifest)
    evidence_engine: Any = None
    history_engine: Any = None
    _states: dict[str, CertificationState] = field(default_factory=dict)
    _history: dict[str, list[CertificationState]] = field(default_factory=dict)
    _records: dict[str, Any] = field(default_factory=dict)
    _evidence: list[Evidence] = field(default_factory=list)
    _log: list[HistoryEntry] = field(default_factory=list)

    # -- criteria --------------------------------------------------------

    @property
    def criteria(self) -> tuple[Rule, ...]:
        return self.manifest.certification_criteria

    def criterion(self, criterion_id: str) -> Rule:
        for rule in self.criteria:
            if rule.rule_id == criterion_id:
                return rule
        raise ObjectNotFoundError(f"certification criterion not declared: {criterion_id}")

    # -- eligibility -----------------------------------------------------

    def eligible(self, subject: CertificationSubject) -> bool:
        """Whether *subject* may be offered for certification at all.

        Eligibility is deliberately a single gateway fact rather than a second
        pass over the criteria: an object fails *certification* on its criteria,
        but it is *ineligible* only when it was never governed in the first place.
        """
        return bool(subject.fact(ELIGIBILITY_FACT))

    # -- assessment ------------------------------------------------------

    def assess(self, subject: CertificationSubject, *, tick: int = 0) -> CertificationState:
        """Evaluate every declared criterion and issue a certification state."""
        if not subject.subject_id.strip():
            raise CertificationStateError("certification subject requires a non-empty subject_id")

        outcomes = tuple(
            CriterionOutcome(
                criterion_id=rule.rule_id,
                severity=rule.severity,
                passed=bool(subject.fact(rule.requires)),
                message=rule.message,
            )
            for rule in self.criteria
        )
        blocking = tuple(o.criterion_id for o in outcomes if o.blocking_failure)
        eligible = self.eligible(subject)

        if not eligible:
            status = CERTIFICATION_NOT_CERTIFIED
            rationale = "ineligible: the subject is not governed"
        elif blocking:
            status = CERTIFICATION_NOT_CERTIFIED
            rationale = "blocking criteria failed: " + ", ".join(blocking)
        else:
            status = CERTIFICATION_CERTIFIED
            rationale = "every blocking criterion passed"

        # The chain extends the *prior state's* lineage, not the subject's: the
        # subject is the same fact bag every time, so seeding from it would
        # produce a lineage of one repeated link no matter how often a subject
        # was reassessed. The subject's own lineage seeds only the first link.
        prior = self._states.get(subject.subject_id)
        lineage = (*prior.lineage, prior.identity) if prior is not None else subject.lineage

        state = CertificationState(
            state_id=f"CERT-{subject.subject_id}",
            subject_id=subject.subject_id,
            status=status,
            eligible=eligible,
            version=subject.version,
            criteria=outcomes,
            evidence_ids=(),
            lineage=lineage,
            rationale=rationale,
            attributes={"subject_kind": subject.kind, "revision": len(lineage) + 1},
            tick=tick,
        )
        evidence_id = self._record_evidence(subject, state, tick=tick)
        state = CertificationState(
            state_id=state.state_id,
            subject_id=state.subject_id,
            status=state.status,
            eligible=state.eligible,
            version=state.version,
            criteria=state.criteria,
            evidence_ids=(evidence_id,),
            lineage=state.lineage,
            rationale=state.rationale,
            attributes=state.attributes,
            tick=tick,
        )

        self._states[subject.subject_id] = state
        self._history.setdefault(subject.subject_id, []).append(state)
        self._records[subject.subject_id] = self._issue_record(subject, state, evidence_id)
        self._append_log(subject.subject_id, f"{status}: {rationale}", tick=tick)
        return state

    def assess_all(
        self, subjects: Iterable[CertificationSubject], *, tick: int = 0
    ) -> tuple[CertificationState, ...]:
        return tuple(
            self.assess(subject, tick=tick)
            for subject in sorted(subjects, key=lambda s: s.subject_id)
        )

    # -- the canonical certificate ---------------------------------------

    def _issue_record(
        self, subject: CertificationSubject, state: CertificationState, evidence_ref: str
    ) -> Any:
        """Issue the repository's canonical certification record for this state."""
        from engine.certification.contracts import (
            CertificationClass,
            CertificationFinding,
            CertificationRecord,
            CertificationStatus,
            CriterionSeverity,
            CriterionStatus,
        )
        from engine.runtime.disclosure import build_disclosure

        findings = tuple(
            CertificationFinding(
                criterion_id=outcome.criterion_id,
                severity=(
                    CriterionSeverity.BLOCKING
                    if outcome.severity == CRITERION_BLOCKING
                    else CriterionSeverity.ADVISORY
                ),
                status=CriterionStatus.PASS if outcome.passed else CriterionStatus.FAIL,
                message=outcome.message,
                details={"subject_kind": subject.kind},
            )
            for outcome in state.criteria
        )
        return CertificationRecord.create(
            target_id=subject.subject_id,
            blueprint_id=CONTROL_PLANE_BLUEPRINT,
            version=subject.version or "0.0.0",
            status=(
                CertificationStatus.CERTIFIED
                if state.certified
                else CertificationStatus.NOT_CERTIFIED
            ),
            certification_class=CertificationClass.ENGINEERING_READINESS,
            evidence_ref=evidence_ref,
            criteria=findings,
            disclosure=build_disclosure(),
        )

    def record_for(self, subject_id: str) -> Any:
        """The canonical :class:`CertificationRecord` issued for *subject_id*."""
        if subject_id not in self._records:
            raise ObjectNotFoundError(f"no certification record issued for: {subject_id}")
        return self._records[subject_id]

    # -- recording helpers -----------------------------------------------

    def _record_evidence(
        self, subject: CertificationSubject, state: CertificationState, *, tick: int
    ) -> str:
        payload = {
            "subject": subject.to_dict(),
            "status": state.status,
            "eligible": state.eligible,
            "criteria": [c.to_dict() for c in state.criteria],
        }
        revision = len(self._history.get(subject.subject_id, []))
        evidence = Evidence(
            evidence_id=f"EV-CERT-{subject.subject_id}-{revision}",
            subject_id=subject.subject_id,
            kind="CERTIFICATION",
            claim=f"certification assessed as {state.status}",
            payload_digest=payload_digest(payload),
            attributes={"criterion_count": len(state.criteria)},
            tick=tick,
        )
        self._evidence.append(evidence)
        if self.evidence_engine is not None:
            # An append-only engine refusing a duplicate evidence id is its
            # contract being honoured, not a certification fault.
            with suppress(DuplicateObjectError):
                self.evidence_engine.record(evidence)
        return evidence.evidence_id

    def _append_log(self, subject_id: str, detail: str, *, tick: int) -> None:
        entry = HistoryEntry(
            entry_id=f"HIS-CERT-{subject_id}-{len(self._log)}",
            subject_id=subject_id,
            event=EVENT_CERTIFICATION_ASSESSED,
            detail=detail,
            actor_id="CertificationEngine",
            tick=tick,
        )
        self._log.append(entry)
        if self.history_engine is not None:
            self.history_engine.append(entry)

    # -- queries ---------------------------------------------------------

    def state_of(self, subject_id: str) -> CertificationState:
        if subject_id not in self._states:
            raise ObjectNotFoundError(f"no certification state assessed for: {subject_id}")
        return self._states[subject_id]

    def status_of(self, subject_id: str) -> str:
        """The certification status, UNCERTIFIED when the subject was never assessed."""
        state = self._states.get(subject_id)
        return state.status if state is not None else CERTIFICATION_UNCERTIFIED

    def history_of(self, subject_id: str) -> tuple[CertificationState, ...]:
        """Every assessment of *subject_id*, oldest first (append-only)."""
        return tuple(self._history.get(subject_id, ()))

    def lineage_of(self, subject_id: str) -> tuple[str, ...]:
        """The chain of prior certification identities behind the current state."""
        state = self._states.get(subject_id)
        return state.lineage if state is not None else ()

    def evidence(self, subject_id: str | None = None) -> tuple[Evidence, ...]:
        if subject_id is None:
            return tuple(self._evidence)
        return tuple(e for e in self._evidence if e.subject_id == subject_id)

    def certified(self) -> tuple[CertificationState, ...]:
        return tuple(
            sorted((s for s in self._states.values() if s.certified), key=lambda s: s.subject_id)
        )

    def not_certified(self) -> tuple[CertificationState, ...]:
        return tuple(
            sorted(
                (s for s in self._states.values() if not s.certified), key=lambda s: s.subject_id
            )
        )

    def ineligible(self) -> tuple[CertificationState, ...]:
        return tuple(
            sorted((s for s in self._states.values() if not s.eligible), key=lambda s: s.subject_id)
        )

    def failures(self) -> tuple[str, ...]:
        """Subject ids that were assessed and are not certified — the stage failures."""
        return tuple(s.subject_id for s in self.not_certified())

    def count(self) -> int:
        return len(self._states)

    def log(self) -> tuple[HistoryEntry, ...]:
        return tuple(self._log)

    # -- projection ------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        return {
            "engine": "CertificationEngine",
            "manifest_id": self.manifest.manifest_id,
            "criteria": [c.to_dict() for c in self.criteria],
            "counts": {
                "assessed": self.count(),
                "certified": len(self.certified()),
                "not_certified": len(self.not_certified()),
                "ineligible": len(self.ineligible()),
                "evidence": len(self._evidence),
            },
            "states": [
                s.to_dict() for s in sorted(self._states.values(), key=lambda s: s.subject_id)
            ],
        }


def certification_subjects(
    records: Iterable[GovernanceRecord],
    *,
    versions: Mapping[str, str] | None = None,
) -> tuple[CertificationSubject, ...]:
    """Project resolved governance records into certification subjects."""
    lookup = versions or {}
    return tuple(
        sorted(
            (
                CertificationSubject.from_governance(r, version=lookup.get(r.subject_id, ""))
                for r in records
            ),
            key=lambda s: s.subject_id,
        )
    )


__all__ = [
    "CONTROL_PLANE_BLUEPRINT",
    "ELIGIBILITY_FACT",
    "EVENT_CERTIFICATION_ASSESSED",
    "CertificationEngine",
    "CertificationSubject",
    "certification_subjects",
]
