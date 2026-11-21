"""UKIP Part 05 — Knowledge Provenance (EPIC-UKDA-003).

Where every piece of knowledge came from, as a tamper-evident chain rather than a
free-text note (UKIP-LAW-004).

A :class:`ProvenanceChain` is an append-only sequence of :class:`ProvenanceStep`
values, each of which hashes its own content **together with the digest of the step
before it**. That single design choice is what makes provenance verifiable instead of
merely recorded: altering, reordering, inserting, or deleting any step invalidates
every digest after it, so :meth:`ProvenanceChain.verify` detects the tampering
without needing a copy of the original.

The canonical stages a record passes through are declared once in
:data:`PROVENANCE_STAGES` and enforced in order, so the chain of any two records is
directly comparable and a missing stage is a detectable gap rather than a silent
omission.

Deterministic and wall-clock free (IMP-007 §5): the chain's digests are a function of
its content only, so the same observation always produces the same seal.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from engine.knowledge.model import content_hash
from engine.knowledge.ukip.contracts import KnowledgeUnit, SourceRef
from engine.knowledge.ukip.errors import ProvenanceError

#: The digest a chain's first step chains from (a chain has no predecessor).
GENESIS = "0" * 64


class Stage(str, Enum):
    """The canonical provenance stages, in the order they must occur."""

    OBSERVED = "observed"
    PROVIDED = "provided"
    CLASSIFIED = "classified"
    REGISTERED = "registered"
    CORROBORATED = "corroborated"
    RELATED = "related"
    VALIDATED = "validated"
    CERTIFIED = "certified"
    SUPERSEDED = "superseded"

    @classmethod
    def coerce(cls, value: Any, *, context: str = "provenance") -> Stage:
        try:
            return cls(str(value))
        except ValueError as exc:
            raise ProvenanceError("unknown provenance stage", value=value, at=context) from exc

    @property
    def order(self) -> int:
        return _STAGE_ORDER[self]


#: Every stage, in canonical order.
PROVENANCE_STAGES: tuple[Stage, ...] = tuple(Stage)

_STAGE_ORDER: dict[Stage, int] = {stage: index for index, stage in enumerate(PROVENANCE_STAGES)}

#: The stages a record must carry before it can be certified. ``CORROBORATED`` is
#: absent by design: corroboration happens only when a second provider supplies the
#: same knowledge, so requiring it would penalise knowledge with a single source.
REQUIRED_STAGES: tuple[Stage, ...] = (
    Stage.OBSERVED,
    Stage.PROVIDED,
    Stage.CLASSIFIED,
    Stage.REGISTERED,
)


@dataclass(frozen=True, slots=True)
class ProvenanceStep:
    """One tamper-evident link in a provenance chain.

    ``step_sha256`` covers the step's own content *and* ``previous_sha256``, which is
    what binds the chain together. It is computed at construction, so a step cannot
    exist in an unsealed state.
    """

    stage: Stage
    actor: str
    action: str
    previous_sha256: str = GENESIS
    source: SourceRef | None = None
    payload_sha256: str = ""
    detail: str = ""
    step_sha256: str = field(default="", compare=False)

    def __post_init__(self) -> None:
        if not isinstance(self.stage, Stage):
            raise ProvenanceError("step stage must be a Stage", at=self.actor)
        if not self.actor:
            raise ProvenanceError("provenance step requires an actor", stage=self.stage.value)
        if not self.action:
            raise ProvenanceError("provenance step requires an action", actor=self.actor)
        if len(self.previous_sha256) != 64:
            raise ProvenanceError(
                "previous digest must be a 64-character sha256 hex digest",
                actor=self.actor,
                stage=self.stage.value,
            )
        object.__setattr__(self, "step_sha256", self._compute())

    def _core(self) -> dict[str, Any]:
        return {
            "stage": self.stage.value,
            "actor": self.actor,
            "action": self.action,
            "previous_sha256": self.previous_sha256,
            "source": self.source.to_dict() if self.source is not None else None,
            "payload_sha256": self.payload_sha256,
            "detail": self.detail,
        }

    def _compute(self) -> str:
        return content_hash(self._core())

    def verify(self) -> bool:
        """True iff this step's recorded digest still matches its content."""
        return self.step_sha256 == self._compute()

    def to_dict(self) -> dict[str, Any]:
        payload = self._core()
        payload["step_sha256"] = self.step_sha256
        return payload

    @classmethod
    def from_dict(cls, record: Mapping[str, Any]) -> ProvenanceStep:
        if not isinstance(record, Mapping):
            raise ProvenanceError("provenance step must be an object")
        source_raw = record.get("source")
        step = cls(
            stage=Stage.coerce(record.get("stage")),
            actor=str(record.get("actor") or ""),
            action=str(record.get("action") or ""),
            previous_sha256=str(record.get("previous_sha256") or GENESIS),
            source=SourceRef.from_dict(source_raw) if isinstance(source_raw, Mapping) else None,
            payload_sha256=str(record.get("payload_sha256") or ""),
            detail=str(record.get("detail") or ""),
        )
        recorded = record.get("step_sha256")
        if recorded and recorded != step.step_sha256:
            raise ProvenanceError(
                "provenance step digest does not match its content",
                stage=step.stage.value,
                expected=str(recorded),
                actual=step.step_sha256,
            )
        return step


@dataclass(frozen=True, slots=True)
class ProvenanceChain:
    """An append-only, hash-chained history of one piece of knowledge."""

    subject: str
    steps: tuple[ProvenanceStep, ...] = ()

    @property
    def head(self) -> str:
        """The digest the next step must chain from (the chain's current seal)."""
        return self.steps[-1].step_sha256 if self.steps else GENESIS

    @property
    def seal(self) -> str:
        """A stable seal over the whole chain (its head digest)."""
        return self.head

    def __len__(self) -> int:
        return len(self.steps)

    def append(
        self,
        stage: Stage,
        *,
        actor: str,
        action: str,
        source: SourceRef | None = None,
        payload_sha256: str = "",
        detail: str = "",
    ) -> ProvenanceChain:
        """Return a new chain with one step appended, enforcing stage ordering.

        Ordering is enforced here rather than checked later so that an out-of-order
        history cannot be constructed in the first place.
        """
        if self.steps and stage.order < self.steps[-1].stage.order:
            raise ProvenanceError(
                "provenance stages may not go backwards",
                subject=self.subject,
                current=self.steps[-1].stage.value,
                attempted=stage.value,
            )
        step = ProvenanceStep(
            stage=stage,
            actor=actor,
            action=action,
            previous_sha256=self.head,
            source=source,
            payload_sha256=payload_sha256,
            detail=detail,
        )
        return ProvenanceChain(subject=self.subject, steps=(*self.steps, step))

    # -- queries ---------------------------------------------------------------

    def stages(self) -> tuple[Stage, ...]:
        return tuple(step.stage for step in self.steps)

    def has_stage(self, stage: Stage) -> bool:
        return any(step.stage is stage for step in self.steps)

    def step_for(self, stage: Stage) -> ProvenanceStep | None:
        """The first step recorded for a stage."""
        for step in self.steps:
            if step.stage is stage:
                return step
        return None

    def sources(self) -> tuple[SourceRef, ...]:
        """Every distinct source cited anywhere in the chain, in first-seen order."""
        seen: dict[str, SourceRef] = {}
        for step in self.steps:
            if step.source is not None:
                seen.setdefault(step.source.citation, step.source)
        return tuple(seen.values())

    def actors(self) -> tuple[str, ...]:
        seen: dict[str, None] = {}
        for step in self.steps:
            seen.setdefault(step.actor, None)
        return tuple(seen)

    def missing_stages(self) -> tuple[Stage, ...]:
        """Required stages this chain does not yet carry."""
        return tuple(stage for stage in REQUIRED_STAGES if not self.has_stage(stage))

    @property
    def is_complete(self) -> bool:
        """True iff every required stage is present."""
        return not self.missing_stages()

    @property
    def is_grounded(self) -> bool:
        """True iff the chain cites at least one content-addressed source."""
        return any(s.content_sha256 for s in self.sources())

    # -- verification ----------------------------------------------------------

    def verify(self) -> bool:
        """True iff every step verifies and the links are intact and ordered."""
        return not self.broken_links()

    def broken_links(self) -> tuple[str, ...]:
        """Human-readable descriptions of every integrity defect found."""
        defects: list[str] = []
        expected_previous = GENESIS
        last_order = -1
        for index, step in enumerate(self.steps):
            if not step.verify():
                defects.append(f"step[{index}]:{step.stage.value}:digest-mismatch")
            if step.previous_sha256 != expected_previous:
                defects.append(f"step[{index}]:{step.stage.value}:broken-link")
            if step.stage.order < last_order:
                defects.append(f"step[{index}]:{step.stage.value}:out-of-order")
            last_order = max(last_order, step.stage.order)
            expected_previous = step.step_sha256
        return tuple(defects)

    def require_intact(self) -> None:
        """Raise :class:`ProvenanceError` if the chain is broken."""
        defects = self.broken_links()
        if defects:
            raise ProvenanceError(
                "provenance chain integrity check failed",
                subject=self.subject,
                defects=list(defects),
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "subject": self.subject,
            "length": len(self.steps),
            "seal": self.seal,
            "complete": self.is_complete,
            "grounded": self.is_grounded,
            "stages": [s.value for s in self.stages()],
            "missing_stages": [s.value for s in self.missing_stages()],
            "sources": [s.to_dict() for s in self.sources()],
            "steps": [s.to_dict() for s in self.steps],
        }

    @classmethod
    def from_dict(cls, record: Mapping[str, Any]) -> ProvenanceChain:
        if not isinstance(record, Mapping):
            raise ProvenanceError("provenance chain must be an object")
        steps_raw = record.get("steps") or []
        if not isinstance(steps_raw, list):
            raise ProvenanceError("provenance steps must be an array")
        chain = cls(
            subject=str(record.get("subject") or ""),
            steps=tuple(ProvenanceStep.from_dict(s) for s in steps_raw),
        )
        chain.require_intact()
        return chain


def begin_chain(unit: KnowledgeUnit, *, subject: str | None = None) -> ProvenanceChain:
    """Open a provenance chain for a unit with its observation and provision steps.

    Every chain starts at the source: ``OBSERVED`` cites the exact locator and digest
    the provider read, and ``PROVIDED`` binds the whole contribution's digest. A
    record can therefore never exist without a reproducible origin (UKIP-LAW-004).
    """
    chain = ProvenanceChain(subject=subject or unit.knowledge_id())
    chain = chain.append(
        Stage.OBSERVED,
        actor=unit.source.provider_id,
        action="observe",
        source=unit.source,
        payload_sha256=unit.source.content_sha256,
        detail=unit.source.citation,
    )
    return chain.append(
        Stage.PROVIDED,
        actor=unit.source.provider_id,
        action="provide",
        source=unit.source,
        payload_sha256=unit.unit_sha256(),
        detail=f"unit:{unit.key}",
    )


class ProvenanceLedger:
    """The provenance of every subject, keyed by canonical knowledge identifier."""

    __slots__ = ("_chains",)

    def __init__(self, chains: Iterable[ProvenanceChain] = ()) -> None:
        self._chains: dict[str, ProvenanceChain] = {}
        for chain in chains:
            self._chains[chain.subject] = chain

    def __len__(self) -> int:
        return len(self._chains)

    def __contains__(self, subject: object) -> bool:
        return subject in self._chains

    def subjects(self) -> tuple[str, ...]:
        return tuple(sorted(self._chains))

    def get(self, subject: str) -> ProvenanceChain | None:
        return self._chains.get(subject)

    def require(self, subject: str) -> ProvenanceChain:
        chain = self._chains.get(subject)
        if chain is None:
            raise ProvenanceError("no provenance recorded for subject", subject=subject)
        return chain

    def put(self, chain: ProvenanceChain) -> ProvenanceLedger:
        """Record (or replace) the chain for a subject."""
        self._chains[chain.subject] = chain
        return self

    def append(
        self,
        subject: str,
        stage: Stage,
        *,
        actor: str,
        action: str,
        source: SourceRef | None = None,
        payload_sha256: str = "",
        detail: str = "",
    ) -> ProvenanceChain:
        """Append a step to a subject's chain, creating the chain if needed."""
        chain = self._chains.get(subject) or ProvenanceChain(subject=subject)
        updated = chain.append(
            stage,
            actor=actor,
            action=action,
            source=source,
            payload_sha256=payload_sha256,
            detail=detail,
        )
        self._chains[subject] = updated
        return updated

    def chains(self) -> tuple[ProvenanceChain, ...]:
        return tuple(self._chains[k] for k in self.subjects())

    def incomplete(self) -> tuple[str, ...]:
        """Subjects whose chain is missing a required stage."""
        return tuple(c.subject for c in self.chains() if not c.is_complete)

    def broken(self) -> tuple[str, ...]:
        """Subjects whose chain fails integrity verification."""
        return tuple(c.subject for c in self.chains() if not c.verify())

    def ungrounded(self) -> tuple[str, ...]:
        """Subjects with no content-addressed source anywhere in their chain."""
        return tuple(c.subject for c in self.chains() if not c.is_grounded)

    def seal(self) -> str:
        """A single deterministic seal over every chain in the ledger."""
        return content_hash({c.subject: c.seal for c in self.chains()})

    def to_dict(self) -> dict[str, Any]:
        return {
            "count": len(self._chains),
            "seal": self.seal(),
            "incomplete": list(self.incomplete()),
            "broken": list(self.broken()),
            "ungrounded": list(self.ungrounded()),
            "chains": [c.to_dict() for c in self.chains()],
        }


__all__ = [
    "GENESIS",
    "Stage",
    "PROVENANCE_STAGES",
    "REQUIRED_STAGES",
    "ProvenanceStep",
    "ProvenanceChain",
    "ProvenanceLedger",
    "begin_chain",
]
