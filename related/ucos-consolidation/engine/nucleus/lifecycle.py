"""UCOS-NUC-001 Part 06 — the Universal Autonomous Constitutional Lifecycle (D-18).

AC-008 requires the lifecycle to exist as **infrastructure**, not as documentation,
guidance or process. Repository truth before this module: the lifecycle existed as a
45-node declaration (``UCL-000001``'s stage manifest) plus a script that measured it.
The stages were owned, ordered and acyclic — but nothing *in the importable engine* could
run them over an object, so no nucleus, capability, artifact or context actually executed
the lifecycle.

This module is that missing infrastructure and nothing more:

    * the 45 stages are held as **DATA** (:data:`STAGES`), a checked projection of the
      ``UCL-000001`` manifest. :func:`verify_manifest_alignment` fails closed if the two
      ever diverge, so there is one authority and one verified view — the pattern already
      used for vocabularies — rather than a second, drifting stage list;
    * the execution order is **derived** by the single ordering authority
      (:mod:`engine.foundation.composition.ordering`), never hardcoded;
    * :class:`LifecycleExecution` runs the stages over *any* subject through a caller-
      supplied stage function, records one :class:`StageOutcome` per stage with a
      hash-chained journal, and yields a deterministic, replayable record;
    * a run is a **fixed point** when re-running it reproduces the same digest, which is
      what :meth:`LifecycleExecution.replay` measures.

Nothing here knows what a nucleus is. The lifecycle applies to nuclei, layers,
compositions, capabilities, artifacts, knowledge, registries, policies, evidence,
executions, contexts, universes, civilisations and realities alike, because the subject is
an opaque identifier and the work is the caller's function (AC-008: "everything, no
exceptions").
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from engine.foundation.composition.ordering import (
    DEFAULT_STRATEGY,
    derive_order,
    unresolved_keys,
)
from engine.nucleus.errors import LifecycleError
from engine.uckp.canonical import content_hash

#: The identity of the lifecycle declaration this module realises.
LIFECYCLE_ID = "UCL-000001"

#: Versioned so stages can be *appended* without any prior execution changing meaning.
LIFECYCLE_VERSION = "1.0.0"


class StageStatus(str, Enum):
    """The outcome of one stage. There is no ``UNKNOWN``: silence is not a status."""

    SATISFIED = "satisfied"
    NOT_APPLICABLE = "not-applicable"
    FAILED = "failed"

    @classmethod
    def coerce(cls, value: Any, *, at: str = "stage") -> StageStatus:
        if isinstance(value, cls):
            return value
        try:
            return cls(str(value))
        except ValueError as exc:
            raise LifecycleError(
                "unknown stage status", at=at, value=str(value), allowed=[s.value for s in cls]
            ) from exc

    @property
    def is_blocking(self) -> bool:
        return self is StageStatus.FAILED


@dataclass(frozen=True, slots=True)
class Stage:
    """One stage of the constitutional lifecycle: an identity, an ordinal and a group."""

    stage_id: str
    name: str
    ordinal: int
    group: str
    depends_on: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "stage_id": self.stage_id,
            "name": self.name,
            "ordinal": self.ordinal,
            "group": self.group,
            "depends_on": list(self.depends_on),
        }


def _chain(entries: Sequence[tuple[int, str, str]]) -> tuple[Stage, ...]:
    """Build the stage chain, each stage depending on the one before it (DATA → graph)."""
    stages: list[Stage] = []
    previous: str | None = None
    for ordinal, group, name in entries:
        stage_id = f"UCL-S-{ordinal:04d}"
        stages.append(
            Stage(
                stage_id=stage_id,
                name=name,
                ordinal=ordinal,
                group=group,
                depends_on=() if previous is None else (previous,),
            )
        )
        previous = stage_id
    return tuple(stages)


#: The 45 constitutional lifecycle stages (AC-008), as ``(ordinal, group, name)``. A
#: checked projection of the ``UCL-000001`` stage manifest — see
#: :func:`verify_manifest_alignment`. Appending a stage here is a data edit; no function
#: in this module branches on a stage name.
STAGE_DECLARATIONS: tuple[tuple[int, str, str], ...] = (
    (10, "GOAL", "Receive Goal"),
    (20, "GOAL", "Understand"),
    (30, "DISCOVERY", "Context Assimilation"),
    (40, "DISCOVERY", "Repository Truth Discovery"),
    (50, "DISCOVERY", "Knowledge Discovery"),
    (60, "DISCOVERY", "Canonical Owner Discovery"),
    (70, "DISCOVERY", "Capability Discovery"),
    (80, "DISCOVERY", "Dependency Discovery"),
    (90, "DISCOVERY", "Constraint Discovery"),
    (100, "DISCOVERY", "Gap Discovery"),
    (110, "REUSE", "Reuse Before Create"),
    (120, "PERCEPTION", "Observe"),
    (130, "PERCEPTION", "Perceive"),
    (140, "PERCEPTION", "Measure"),
    (150, "EVIDENCE", "Evidence"),
    (160, "ASSURANCE", "Validate"),
    (170, "ASSURANCE", "Verify"),
    (180, "COGNITION", "Learn"),
    (190, "COGNITION", "Reason"),
    (200, "COGNITION", "Reflect"),
    (210, "CORRECTION", "Challenge"),
    (220, "CORRECTION", "Correct"),
    (230, "CORRECTION", "Improve"),
    (240, "CONSTRUCTION", "Architect"),
    (250, "CONSTRUCTION", "Engineer"),
    (260, "CONSTRUCTION", "Test"),
    (270, "GOVERNANCE", "Govern"),
    (280, "GOVERNANCE", "Certify"),
    (290, "INTEGRATION", "Integrate"),
    (300, "INTEGRATION", "Register"),
    (310, "IDENTITY", "Assign Universal Constitutional Identifier"),
    (320, "IDENTITY", "Update Universal Constitutional Identifier Dictionary"),
    (330, "IDENTITY", "Update Universal Registry"),
    (340, "IDENTITY", "Update Universal Bookkeeping"),
    (350, "IDENTITY", "Update Universal Lineage"),
    (360, "TRUTH", "Update Repository Truth"),
    (370, "CONVERGENCE", "Replay"),
    (380, "CONVERGENCE", "Deterministic Fixed Point"),
    (390, "KNOWLEDGE", "Extract Engineering Knowledge"),
    (400, "KNOWLEDGE", "Register Engineering Knowledge"),
    (410, "ELEVATION", "Elevate"),
    (420, "ELEVATION", "Increase Constitutional Capability"),
    (430, "ELEVATION", "Increase Engineering Capability"),
    (440, "ELEVATION", "Increase Autonomous Engineering Capability"),
    (450, "ELEVATION", "Begin Next Elevated Engineering Cycle"),
)

#: The stage chain, derived from the declarations above.
STAGES: tuple[Stage, ...] = _chain(STAGE_DECLARATIONS)

#: ``stage_id → Stage`` for lookup.
_BY_ID: Mapping[str, Stage] = {stage.stage_id: stage for stage in STAGES}


def stage_graph(stages: Sequence[Stage] = STAGES) -> dict[str, tuple[str, ...]]:
    """The stage dependency graph in the shape the single ordering authority consumes."""
    return {stage.stage_id: stage.depends_on for stage in stages}


def stage_order(stages: Sequence[Stage] = STAGES, *, strategy: str = DEFAULT_STRATEGY) -> list[str]:
    """The derived execution order of the stages.

    Raises:
        LifecycleError: the declared graph contains a cycle, so no order exists.
    """
    graph = stage_graph(stages)
    ordering = derive_order(graph, strategy=strategy)
    unresolved = unresolved_keys(graph, ordering)
    if unresolved:
        raise LifecycleError(
            "the lifecycle stage graph contains a cycle; no order exists",
            unresolved=sorted(unresolved),
        )
    return [key for _wave, key in ordering]


def stage(stage_id: str) -> Stage:
    """Return the declared stage or fail closed."""
    found = _BY_ID.get(stage_id)
    if found is None:
        raise LifecycleError("no such lifecycle stage", stage_id=stage_id)
    return found


def verify_manifest_alignment(manifest: Mapping[str, Any]) -> tuple[str, ...]:
    """Compare a supplied ``UCL-000001`` stage manifest with :data:`STAGES`.

    Returns the divergences as human-readable strings; an empty tuple means the
    projection is exact. Callers that hold the manifest (a CLI, a CI gate) use this to
    prove the in-engine stage set has not drifted from the declaration that owns it,
    which is what keeps this module a *view* and not a second authority.
    """
    nodes = manifest.get("nodes")
    if not isinstance(nodes, list):
        return ("manifest carries no 'nodes' list",)
    divergences: list[str] = []
    declared = {stage.stage_id: stage for stage in STAGES}
    seen: set[str] = set()
    for node in nodes:
        if not isinstance(node, Mapping):
            divergences.append("manifest node is not a mapping")
            continue
        node_id = str(node.get("id", ""))
        seen.add(node_id)
        mine = declared.get(node_id)
        if mine is None:
            divergences.append(f"{node_id}: present in manifest, absent from STAGES")
            continue
        if str(node.get("stage", "")) != mine.name:
            divergences.append(f"{node_id}: manifest stage {node.get('stage')!r} != {mine.name!r}")
        if int(node.get("ordinal", -1)) != mine.ordinal:
            divergences.append(
                f"{node_id}: manifest ordinal {node.get('ordinal')!r} != {mine.ordinal!r}"
            )
        if str(node.get("group", "")) != mine.group:
            divergences.append(f"{node_id}: manifest group {node.get('group')!r} != {mine.group!r}")
    for missing in sorted(set(declared) - seen):
        divergences.append(f"{missing}: present in STAGES, absent from manifest")
    return tuple(divergences)


# --------------------------------------------------------------------------- #
# Execution                                                                    #
# --------------------------------------------------------------------------- #


@dataclass(frozen=True, slots=True)
class StageOutcome:
    """The record of one stage having been executed over one subject."""

    stage_id: str
    name: str
    group: str
    status: StageStatus
    evidence: str
    detail: Mapping[str, Any] = field(default_factory=dict)
    entry_hash: str = ""
    prev_hash: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "stage_id": self.stage_id,
            "name": self.name,
            "group": self.group,
            "status": self.status.value,
            "evidence": self.evidence,
            "detail": dict(self.detail),
            "prev_hash": self.prev_hash,
            "entry_hash": self.entry_hash,
        }


#: A stage function: given ``(subject, stage)``, return ``(status, evidence, detail)``.
#: Pure and deterministic by contract — the lifecycle reads no clock, no RNG and no
#: network, so a run replays byte-identically.
StageFunction = Callable[[str, Stage], "tuple[StageStatus, str, Mapping[str, Any]]"]


def satisfied_by_declaration(
    subject: str, stage: Stage
) -> tuple[StageStatus, str, Mapping[str, Any]]:
    """The default stage function: every stage is discharged by the declaration itself.

    It is deliberately minimal and honest. It records that the stage *ran* over the
    subject and names the declaration as the evidence; it does not claim work that no
    code performed. A caller with real per-stage work supplies its own function.
    """
    return (
        StageStatus.SATISFIED,
        f"{LIFECYCLE_ID}:{stage.stage_id}",
        {"subject": subject, "ordinal": stage.ordinal},
    )


@dataclass(frozen=True, slots=True)
class LifecycleExecution:
    """One complete, replayable execution of the lifecycle over one subject."""

    subject: str
    lifecycle_id: str
    outcomes: tuple[StageOutcome, ...]
    order: tuple[str, ...]
    context: Mapping[str, Any] = field(default_factory=dict)

    @property
    def failures(self) -> tuple[StageOutcome, ...]:
        return tuple(o for o in self.outcomes if o.status.is_blocking)

    @property
    def context_bound(self) -> bool:
        """True iff this execution names the reference frame it ran in."""
        return bool(self.context.get("frame"))

    @property
    def complete(self) -> bool:
        """True iff every stage THIS RUN declared produced an outcome, and none failed.

        The population is :attr:`order` — the execution order derived from the stages this
        run was actually given — not the module-level :data:`STAGES`. Reading the constant
        made the predicate a statement about the repository's current stage count rather
        than about the run: a lawful 46-stage execution reported INCOMPLETE while every one
        of its stages had in fact been discharged.

        ``order`` is the right authority because it is *derived* on every run rather than
        stored, so it cannot drift from the run it describes. Carrying a second declared
        population on the record could disagree with it; deriving from ``order`` makes that
        disagreement unrepresentable.

        An execution over an empty stage sequence is complete, vacuously and deliberately —
        see :func:`execute`.
        """
        return len(self.outcomes) == len(self.order) and not self.failures

    @property
    def status(self) -> str:
        return "COMPLETE" if self.complete else "INCOMPLETE"

    @property
    def chain_head(self) -> str:
        """The head of the hash chain — the digest of the last stage entry."""
        return self.outcomes[-1].entry_hash if self.outcomes else ""

    def chain_is_intact(self) -> bool:
        """True iff every journal entry's digest reproduces from its own content."""
        previous = ""
        for outcome in self.outcomes:
            expected = _entry_hash(outcome, previous)
            if outcome.prev_hash != previous or outcome.entry_hash != expected:
                return False
            previous = expected
        return True

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": "ucos-constitutional-lifecycle-execution",
            "version": LIFECYCLE_VERSION,
            "lifecycle_id": self.lifecycle_id,
            "subject": self.subject,
            "context": dict(self.context),
            "context_bound": self.context_bound,
            "status": self.status,
            "stage_count": len(self.outcomes),
            "declared_stage_count": len(self.order),
            "order": list(self.order),
            "outcomes": [o.to_dict() for o in self.outcomes],
            "chain_head": self.chain_head,
            "failures": [o.stage_id for o in self.failures],
        }

    def digest(self) -> str:
        """The digest of the whole execution — the fixed point candidate."""
        return content_hash(self.to_dict())


def _entry_hash(outcome: StageOutcome, prev_hash: str) -> str:
    """The hash-chained digest of one stage entry (tamper-evident journal)."""
    return content_hash(
        {
            "stage_id": outcome.stage_id,
            "name": outcome.name,
            "group": outcome.group,
            "status": outcome.status.value,
            "evidence": outcome.evidence,
            "detail": dict(outcome.detail),
            "prev_hash": prev_hash,
        }
    )


def execute(
    subject: str,
    *,
    stage_function: StageFunction = satisfied_by_declaration,
    stages: Sequence[Stage] = STAGES,
    strategy: str = DEFAULT_STRATEGY,
    context: Mapping[str, Any] | None = None,
) -> LifecycleExecution:
    """Run the whole lifecycle over ``subject`` and return the replayable record.

    Every stage runs, in derived order, and its outcome is journalled into a hash chain.
    A stage function that returns :attr:`StageStatus.FAILED` does not abort the run — the
    lifecycle records the failure and continues, because a partial record is evidence and
    an aborted record is not.

    An empty ``stages`` sequence is ACCEPTED and its execution is COMPLETE, vacuously.
    That is a decision, not an oversight. Nothing in ``UCL-000001`` bounds the stage count
    from below: the manifest declares ``open`` with ``closed_enumeration`` false and no
    minimum, :func:`to_document` reports ``upper_limit`` ``None`` and declares no lower
    limit, and no constitutional instrument prohibits an empty lifecycle. Where the
    architecture states no prohibition, this module preserves mathematical openness rather
    than inventing a floor: "every supplied stage produced an outcome" is trivially true
    over an empty set, and a caller that requires a non-empty lifecycle can measure that
    itself. Refusing here would be this module legislating a bound its authority never
    declared — the finite-world assumption in the opposite direction.

    Raises:
        LifecycleError: ``subject`` is empty, or a stage function returns a status this
            module cannot coerce.
    """
    if not isinstance(subject, str) or not subject.strip():
        raise LifecycleError("a lifecycle execution must name its subject")
    key = subject.strip()
    order = stage_order(stages, strategy=strategy)
    by_id = {s.stage_id: s for s in stages}
    outcomes: list[StageOutcome] = []
    previous = ""
    for stage_id in order:
        current = by_id[stage_id]
        status, evidence, detail = stage_function(key, current)
        outcome = StageOutcome(
            stage_id=current.stage_id,
            name=current.name,
            group=current.group,
            status=StageStatus.coerce(status, at=current.stage_id),
            evidence=str(evidence),
            detail=dict(detail or {}),
            prev_hash=previous,
        )
        entry = _entry_hash(outcome, previous)
        outcome = StageOutcome(
            stage_id=outcome.stage_id,
            name=outcome.name,
            group=outcome.group,
            status=outcome.status,
            evidence=outcome.evidence,
            detail=outcome.detail,
            prev_hash=previous,
            entry_hash=entry,
        )
        outcomes.append(outcome)
        previous = entry
    return LifecycleExecution(
        subject=key,
        lifecycle_id=LIFECYCLE_ID,
        outcomes=tuple(outcomes),
        order=tuple(order),
        context=dict(context or {}),
    )


def replay(
    subject: str,
    *,
    stage_function: StageFunction = satisfied_by_declaration,
    stages: Sequence[Stage] = STAGES,
    strategy: str = DEFAULT_STRATEGY,
    context: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Execute twice and report whether the run is a **deterministic fixed point**.

    This is AC-008's "Replay → Deterministic Fixed Point" made measurable: two hermetic
    runs of the same subject through the same stage function must produce byte-identical
    documents. If they do not, the stage function is reading something it must not.

    A replay is a claim about one reality, so ``context`` is carried through to both runs
    and reported: a fixed point in an unnamed context is a weaker statement than the same
    fixed point in a named one, and the report says which it is.
    """
    runs = [
        execute(
            subject,
            stage_function=stage_function,
            stages=stages,
            strategy=strategy,
            context=context,
        )
        for _ in range(2)
    ]
    first, second = runs
    return {
        "schema": "ucos-constitutional-lifecycle-replay",
        "subject": first.subject,
        "context": dict(context or {}),
        "context_bound": first.context_bound,
        "first_digest": first.digest(),
        "second_digest": second.digest(),
        "fixed_point": first.digest() == second.digest(),
        "chain_intact": first.chain_is_intact() and second.chain_is_intact(),
        "status": first.status,
    }


def to_document() -> dict[str, Any]:
    """The lifecycle declaration as a deterministic, machine-readable document."""
    return {
        "schema": "ucos-constitutional-lifecycle",
        "version": LIFECYCLE_VERSION,
        "lifecycle_id": LIFECYCLE_ID,
        "stage_count": len(STAGES),
        "groups": sorted({s.group for s in STAGES}),
        "stages": [s.to_dict() for s in STAGES],
        "order": stage_order(),
        "closed_set": False,
        "upper_limit": None,
    }


def digest() -> str:
    return content_hash(to_document())


__all__ = [
    "LIFECYCLE_ID",
    "LIFECYCLE_VERSION",
    "StageStatus",
    "Stage",
    "STAGE_DECLARATIONS",
    "STAGES",
    "StageFunction",
    "StageOutcome",
    "LifecycleExecution",
    "stage",
    "stage_graph",
    "stage_order",
    "verify_manifest_alignment",
    "satisfied_by_declaration",
    "execute",
    "replay",
    "to_document",
    "digest",
]
