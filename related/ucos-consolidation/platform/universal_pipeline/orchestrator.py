"""UAPF-000001 — the Universal Work Orchestrator (continuous, bounded, autonomous work).

The orchestrator is the thing that *keeps going*. It repeatedly asks one question — is there
work whose declared preconditions now hold? — and if there is, it takes it through the whole
constitutional sequence: promote, cut, admit, execute, validate, verify, certify. It selects
nothing by preference and reorders nothing: every choice it appears to make is a derivation
someone else owns (the queue's derived order, the gateway's admission, the state engine's
legality, the assurance engine's act order).

Readiness is a registry, not a hard-coded predicate
---------------------------------------------------
``03-READY-SELECTION-RULES.md`` defines READY as a conjunction of *seven* predicates over
Repository Truth. Three of those seven are derivable from UAPF's own truth and are seeded
here; the other four (canonical destination, owner, implementation target, traceability
owner) are properties of the repository's object model rather than of a pipeline, so they
are **admitted by registration** through :func:`register_readiness_predicate`. That is the
honest arrangement: UAPF enforces what it can actually derive and provides the one place the
rest are plugged in, instead of hard-coding a predicate it would have to fake.

A unit is promoted only when *every* registered predicate holds; otherwise it is demoted to
the Blocked Set with the failing predicate as its reason (``04`` §2 keys the Blocked Set by
reason). So a new predicate immediately tightens readiness everywhere, with no change here.

Bounded autonomy
----------------
:meth:`UniversalWorkOrchestrator.run` is bounded by ``max_ticks``. Unbounded autonomy is not
a virtue: a non-terminating loop cannot be reasoned about, and ``09-EXECUTION-GOVERNANCE.md``
makes the bound a fixed operational parameter rather than a per-run choice. ``run`` stops
early — the normal case — as soon as a tick can make no progress, so the bound is a safety
net and not the usual exit.

Failure, retry, escalation
--------------------------
A failed unit is retried while its budget lasts (``05`` R1–R3). On exhaustion it is *not*
dropped: it is archived and an escalation is recorded, because R1 requires exhaustion to
reach governance. Autonomy halts for exactly the four reasons
:data:`~platform.universal_pipeline.state.ESCALATION_REASONS` names, and
:class:`~platform.universal_pipeline.errors.PipelineExceptionEscalation` is the only way out.

Determinism: a tick is a pure function of the state it reads. Same admissions, same
declarations, same ticks — and :meth:`OrchestrationTick.fingerprint` proves it.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from platform.foundation.contracts import content_hash
from platform.universal_pipeline.assurance import PipelineAssurance
from platform.universal_pipeline.dependencies import DependencyManager
from platform.universal_pipeline.errors import (
    PipelineExceptionEscalation,
    PipelineOrchestrationError,
    UniversalPipelineError,
)
from platform.universal_pipeline.events import PipelineEventBus
from platform.universal_pipeline.execution import (
    ExecutionUnit,
    ExecutionUnitRecord,
    PipelineRuntime,
)
from platform.universal_pipeline.gateway import UniversalPipelineGateway
from platform.universal_pipeline.governance import PipelineGovernance
from platform.universal_pipeline.handlers import require_stage_handler
from platform.universal_pipeline.identity import Identity, mint
from platform.universal_pipeline.observability import PipelineObservability
from platform.universal_pipeline.queue import PipelineQueueManager, QueueEntry
from platform.universal_pipeline.registry import PipelineRegistry
from platform.universal_pipeline.state import (
    DEFAULT_MAX_RETRY,
    ESCALATION_REASONS,
    require_escalation_reason,
)
from platform.universal_pipeline.vocabulary import Vocabulary
from typing import Any

#: The default bound on :meth:`UniversalWorkOrchestrator.run`. A fixed operational
#: parameter (``09-EXECUTION-GOVERNANCE.md``), overridable per call but never absent.
DEFAULT_MAX_TICKS = 64


@dataclass(frozen=True, slots=True)
class ReadinessContext:
    """Everything a readiness predicate is given.

    Closed on purpose, exactly as :class:`~platform.universal_pipeline.handlers.StageContext`
    is: a predicate receives the queue entry, the registry and the declared dependency graph,
    and can therefore *derive* an answer but not cause an effect.
    """

    entry: QueueEntry
    registry: PipelineRegistry
    dependencies: DependencyManager | None = None
    completed: frozenset[str] = frozenset()

    @property
    def unit_id(self) -> str:
        return self.entry.unit_id


#: A readiness predicate: ``(ReadinessContext) -> bool``. Pure and total.
ReadinessPredicate = Callable[[ReadinessContext], bool]

#: The readiness-predicate vocabulary: the predicate *name* is the governed term and the
#: callable is carried as that term's ``predicate`` attribute. Module-level, so a predicate
#: registered anywhere tightens readiness everywhere — and it is the same
#: :class:`~platform.universal_pipeline.vocabulary.Vocabulary` primitive that governs object
#: kinds, pipeline types, event categories and stage handlers.
_READINESS_PREDICATES = Vocabulary("readiness-predicate", error=PipelineOrchestrationError)


def register_readiness_predicate(
    name: str, predicate: ReadinessPredicate, description: str = ""
) -> None:
    """Register one readiness predicate (unbounded extension by registration).

    Raises:
        PipelineOrchestrationError: if ``name`` is not a lower-case dotted/hyphenated token,
            ``predicate`` is not callable, or ``name`` is already registered. Rebinding a
            predicate would silently change what READY means for every unit.
    """
    if not callable(predicate):
        raise PipelineOrchestrationError("readiness predicate must be callable", name=name)
    _READINESS_PREDICATES.register(
        name, description=description, attributes={"predicate": predicate}
    )


def readiness_predicate_names() -> tuple[str, ...]:
    """Every registered readiness predicate name, sorted (deterministic)."""
    return _READINESS_PREDICATES.terms()


def evaluate_readiness(context: ReadinessContext) -> tuple[str, ...]:
    """The names of every registered predicate that does **not** hold, sorted.

    Empty means READY. Returning the failing names rather than a boolean is what lets the
    Blocked Set be keyed by reason (``04`` §2) without a second mechanism.
    """
    return tuple(
        declared.term
        for declared in _READINESS_PREDICATES.declarations()
        if not declared.attribute("predicate")(context)
    )


def _dependencies_complete(context: ReadinessContext) -> bool:
    """``p1`` (``03`` P1) — every dependency of this unit has reached a completed sink."""
    if context.dependencies is None or context.unit_id not in context.dependencies:
        return True
    return set(context.dependencies.dependencies_of(context.unit_id)) <= context.completed


def _pipeline_registered(context: ReadinessContext) -> bool:
    """``p2`` (``03`` P2 projection) — the pipeline version the unit names is registered."""
    return (context.entry.pipeline_id, context.entry.version) in context.registry


def _handlers_resolvable(context: ReadinessContext) -> bool:
    """``p4`` (``03`` P4 projection) — every stage handler the plan names is registered.

    The direct analogue of "implementation target exists": a stage naming an unregistered
    handler has no realizer, so the unit is blocked rather than dispatched to fail.
    """
    if not _pipeline_registered(context):
        return False
    entry = context.registry.get(context.entry.pipeline_id, context.entry.version)
    for stage in entry.definition.stages:
        try:
            require_stage_handler(stage.handler)
        except UniversalPipelineError:
            return False
    return True


@dataclass(frozen=True, slots=True)
class OrchestrationTick:
    """The complete, auditable account of one orchestration tick."""

    index: int
    promoted: tuple[str, ...] = ()
    blocked: tuple[tuple[str, str], ...] = ()
    cut: tuple[str, ...] = ()
    implemented: tuple[str, ...] = ()
    certified: tuple[str, ...] = ()
    failed: tuple[tuple[str, str], ...] = ()
    retried: tuple[str, ...] = ()
    escalated: tuple[tuple[str, str], ...] = ()
    records: tuple[ExecutionUnitRecord, ...] = field(default=())

    def __post_init__(self) -> None:
        if not isinstance(self.index, int) or self.index < 0:
            raise PipelineOrchestrationError("tick index must be a non-negative integer")

    @property
    def identity(self) -> Identity:
        return mint("orchestration-tick", str(self.index), self.fingerprint())

    @property
    def progressed(self) -> bool:
        """True iff this tick changed anything at all.

        The loop's termination condition. A tick that promotes nothing, cuts nothing and
        certifies nothing cannot be followed by a different one, so the run is finished.
        """
        return bool(
            self.promoted
            or self.cut
            or self.implemented
            or self.certified
            or self.failed
            or self.retried
            or self.escalated
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "index": self.index,
            "promoted": list(self.promoted),
            "blocked": [{"unit_id": u, "reason": r} for u, r in self.blocked],
            "cut": list(self.cut),
            "implemented": list(self.implemented),
            "certified": list(self.certified),
            "failed": [{"unit_id": u, "reason": r} for u, r in self.failed],
            "retried": list(self.retried),
            "escalated": [{"unit_id": u, "reason": r} for u, r in self.escalated],
            "progressed": self.progressed,
        }

    def fingerprint(self) -> str:
        return content_hash(
            {
                "index": self.index,
                "promoted": list(self.promoted),
                "blocked": [list(pair) for pair in self.blocked],
                "cut": list(self.cut),
                "implemented": list(self.implemented),
                "certified": list(self.certified),
                "failed": [list(pair) for pair in self.failed],
                "retried": list(self.retried),
                "escalated": [list(pair) for pair in self.escalated],
            }
        )


class UniversalWorkOrchestrator:
    """Drives admitted work through the constitutional sequence, tick by tick."""

    __slots__ = (
        "_registry",
        "_queue",
        "_gateway",
        "_runtime",
        "_assurance",
        "_governance",
        "_observability",
        "_dependencies",
        "_bus",
        "_max_batch",
        "_max_retry",
        "_ticks",
    )

    def __init__(
        self,
        registry: PipelineRegistry,
        queue: PipelineQueueManager,
        gateway: UniversalPipelineGateway,
        runtime: PipelineRuntime,
        assurance: PipelineAssurance,
        *,
        governance: PipelineGovernance | None = None,
        observability: PipelineObservability | None = None,
        dependencies: DependencyManager | None = None,
        bus: PipelineEventBus | None = None,
        max_batch: int | None = None,
        max_retry: int = DEFAULT_MAX_RETRY,
    ) -> None:
        for label, value, expected in (
            ("registry", registry, PipelineRegistry),
            ("queue", queue, PipelineQueueManager),
            ("gateway", gateway, UniversalPipelineGateway),
            ("runtime", runtime, PipelineRuntime),
            ("assurance", assurance, PipelineAssurance),
        ):
            if not isinstance(value, expected):
                raise PipelineOrchestrationError(
                    f"orchestrator requires a {expected.__name__}", argument=label
                )
        if max_batch is not None and (not isinstance(max_batch, int) or max_batch < 1):
            raise PipelineOrchestrationError("max_batch must be a positive integer")
        self._registry = registry
        self._queue = queue
        self._gateway = gateway
        self._runtime = runtime
        self._assurance = assurance
        self._governance = governance
        self._observability = observability
        self._dependencies = dependencies
        self._bus = bus
        self._max_batch = max_batch
        self._max_retry = max_retry
        self._ticks: list[OrchestrationTick] = []

    @property
    def ticks(self) -> tuple[OrchestrationTick, ...]:
        """Every tick performed, in order."""
        return tuple(self._ticks)

    # -- readiness --------------------------------------------------------------------

    def readiness(self, unit_id: str) -> tuple[str, ...]:
        """The failing readiness predicates for ``unit_id`` (empty means READY)."""
        return evaluate_readiness(self._context(self._queue.entry(unit_id)))

    def _context(self, entry: QueueEntry) -> ReadinessContext:
        return ReadinessContext(
            entry=entry,
            registry=self._registry,
            dependencies=self._dependencies,
            completed=frozenset(item.unit_id for item in self._queue.completed),
        )

    # -- the tick ---------------------------------------------------------------------

    def tick(self, *, inputs: Mapping[str, Mapping[str, Any]] | None = None) -> OrchestrationTick:
        """Perform one orchestration tick and return its account.

        ``inputs`` maps a unit id to the stage inputs for that unit; a unit with no entry
        runs on an empty input mapping. Passing inputs per tick rather than storing them keeps
        the orchestrator stateless with respect to *content* — it sequences work and never
        owns what the work is about.
        """
        supplied = dict(inputs or {})
        promoted, blocked = self._promote_eligible()
        retried = self._retry_failed()
        cut = tuple(entry.unit_id for entry in self._queue.cut(max_batch=self._max_batch))
        implemented: list[str] = []
        certified: list[str] = []
        failed: list[tuple[str, str]] = []
        escalated: list[tuple[str, str]] = []
        records: list[ExecutionUnitRecord] = []
        for unit_id in cut:
            record = self._advance_one(unit_id, dict(supplied.get(unit_id, {})), failed, escalated)
            if record is None:
                continue
            records.append(record)
            implemented.append(unit_id)
            if self._assurance.is_certified(unit_id):
                certified.append(unit_id)
        result = OrchestrationTick(
            index=len(self._ticks),
            promoted=promoted,
            blocked=blocked,
            cut=cut,
            implemented=tuple(implemented),
            certified=tuple(certified),
            failed=tuple(failed),
            retried=retried,
            escalated=tuple(escalated),
            records=tuple(records),
        )
        self._ticks.append(result)
        if self._bus is not None:
            self._bus.emit(
                "uapf.orchestration.tick", f"tick-{result.index}", payload=result.to_dict()
            )
        if self._observability is not None:
            self._observability.record_span("uapf.orchestration.cut", len(cut))
        return result

    def run(
        self, *, max_ticks: int = DEFAULT_MAX_TICKS, **kwargs: Any
    ) -> tuple[OrchestrationTick, ...]:
        """Tick until no tick makes progress, or ``max_ticks`` is reached.

        Returns every tick performed by *this* call. Stopping on "no progress" rather than on
        "queue empty" is deliberate: a permanently blocked unit leaves the queue non-empty
        forever, and a loop that waited for emptiness would never return.

        Raises:
            PipelineOrchestrationError: if ``max_ticks`` is not a positive integer, or the
                bound is reached while progress was still being made — an unbounded workload
                is a finding, not a silent truncation.
        """
        if not isinstance(max_ticks, int) or max_ticks < 1:
            raise PipelineOrchestrationError("max_ticks must be a positive integer")
        performed: list[OrchestrationTick] = []
        for _ in range(max_ticks):
            result = self.tick(**kwargs)
            performed.append(result)
            if not result.progressed:
                return tuple(performed)
        raise PipelineOrchestrationError(
            "orchestration bound reached while still making progress",
            max_ticks=max_ticks,
            ready=len(self._queue.ready_queue),
            execution_queue=len(self._queue.execution_queue),
        )

    # -- tick phases ------------------------------------------------------------------

    def _promote_eligible(self) -> tuple[tuple[str, ...], tuple[tuple[str, str], ...]]:
        """Promote every SPECIFIED unit whose predicates hold; block the rest with a reason."""
        promoted: list[str] = []
        blocked: list[tuple[str, str]] = []
        for entry in self._queue.execution_queue:
            # SPECIFIED and BLOCKED are the two states ``04`` §4 promotes from; a BLOCKED
            # unit whose predicates now hold is re-promoted, which is what makes the queue
            # self-correcting as earlier waves complete.
            if entry.state not in {"SPECIFIED", "BLOCKED"}:
                continue
            failing = evaluate_readiness(self._context(entry))
            if not failing:
                self._queue.promote(entry.unit_id)
                promoted.append(entry.unit_id)
            elif entry.state == "SPECIFIED":
                reason = f"BLOCKED:{failing[0]}"
                self._queue.demote(entry.unit_id, reason)
                blocked.append((entry.unit_id, reason))
            # A unit already BLOCKED and still failing needs no transition: recording one
            # would be a BLOCKED -> BLOCKED move the state engine rightly refuses, and it
            # would make every tick look like progress and the run never terminate.
        return tuple(promoted), tuple(blocked)

    def _retry_failed(self) -> tuple[str, ...]:
        """Return failed units to the Ready Queue while their budget lasts (R1–R3)."""
        retried: list[str] = []
        for entry in self._queue.failed:
            if entry.attempts >= self._max_retry:
                continue
            failing = evaluate_readiness(self._context(entry))
            if failing:
                continue
            self._queue.retry(entry.unit_id)
            retried.append(entry.unit_id)
        return tuple(retried)

    def _advance_one(
        self,
        unit_id: str,
        unit_inputs: dict[str, Any],
        failed: list[tuple[str, str]],
        escalated: list[tuple[str, str]],
    ) -> ExecutionUnitRecord | None:
        """Take one cut unit through admit → execute → validate → verify → certify."""
        entry = self._queue.entry(unit_id)
        registry_entry = self._registry.get(entry.pipeline_id, entry.version)
        transaction = self._gateway.submit(
            entry.pipeline_id,
            unit_id,
            version=entry.version,
            inputs=unit_inputs,
            permissions=registry_entry.definition.security.required_permissions,
            evidence=unit_inputs,
        )
        unit = ExecutionUnit.for_entry(
            registry_entry, unit_id, inputs=unit_inputs, attempt=entry.attempts
        )
        record = self._runtime.execute(unit, transaction)
        if not record.passed:
            failed.append((unit_id, record.findings[0]))
            self._exhaust_or_hold(unit_id, record.findings[0], escalated)
            return None
        self._assure(unit_id, record)
        return record

    def _assure(self, unit_id: str, record: ExecutionUnitRecord) -> None:
        """Validate, verify and certify the unit, driving its lifecycle in step."""
        evidence = {
            "execution_fingerprint": record.fingerprint(),
            "stages_run": list(record.stages_run),
            "outputs_recorded": sorted(record.outputs),
        }
        # The runtime advances a queue-bound unit to IMPLEMENTED itself; a runtime composed
        # without a queue does not, so the transition is made here when it is still owed.
        # Either way the unit reaches VALIDATED from IMPLEMENTED and never skips it.
        if self._queue.entry(unit_id).state == "EXECUTING":
            self._queue.advance(unit_id, "IMPLEMENTED")
        self._assurance.validate(unit_id, evidence=evidence)
        self._queue.advance(unit_id, "VALIDATED")
        self._assurance.verify(unit_id, evidence={"validated": True, **evidence})
        self._assurance.certify(unit_id, evidence={"verified": True, **evidence})
        self._queue.advance(unit_id, "CERTIFIED")
        if self._governance is not None:
            self._governance.record_recovery_point(
                unit_id, "CERTIFIED", detail={"execution_fingerprint": record.fingerprint()}
            )

    def _exhaust_or_hold(self, unit_id: str, reason: str, escalated: list[tuple[str, str]]) -> None:
        """Archive and escalate an exhausted unit; otherwise leave it for the retry phase."""
        entry = self._queue.entry(unit_id)
        if entry.attempts < self._max_retry:
            return
        self._queue.retire(unit_id, to_state="ARCHIVED")
        escalation = ESCALATION_REASONS[2]
        escalated.append((unit_id, escalation))
        if self._bus is not None:
            self._bus.emit(
                "uapf.escalation.raised",
                unit_id,
                payload={
                    "reason": escalation,
                    "detail": reason,
                    "attempts": entry.attempts,
                    "max_retry": self._max_retry,
                },
            )

    def escalate(self, subject: str, reason: str) -> None:
        """Halt autonomy for a declared reason (Human Intervention by Exception).

        The single autonomy escape hatch. It records the escalation before raising, so the
        halt is auditable rather than only observable as a crash.

        Raises:
            PipelineStateError: if ``reason`` is not one of the four declared reasons.
            PipelineExceptionEscalation: always, once the reason is accepted.
        """
        require_escalation_reason(reason)
        if self._bus is not None:
            self._bus.emit(
                "uapf.escalation.raised", subject, payload={"reason": reason, "halted": True}
            )
        raise PipelineExceptionEscalation(
            "autonomy halted; human intervention required", subject=subject, reason=reason
        )

    # -- evidence ---------------------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """A deterministic, serializable render of orchestration history (evidence)."""
        return {
            "tick_count": len(self._ticks),
            "max_batch": self._max_batch,
            "max_retry": self._max_retry,
            "readiness_predicates": list(readiness_predicate_names()),
            "ticks": [tick.to_dict() for tick in self._ticks],
        }

    def fingerprint(self) -> str:
        """A deterministic content hash of orchestration history."""
        return content_hash(self.to_dict())


register_readiness_predicate(
    "p1.dependencies-complete",
    _dependencies_complete,
    "every unit this one depends on has reached a completed sink",
)
register_readiness_predicate(
    "p2.pipeline-registered",
    _pipeline_registered,
    "the pipeline version the unit names is registered",
)
register_readiness_predicate(
    "p4.handlers-resolvable",
    _handlers_resolvable,
    "every stage handler the pipeline names is registered",
)


__all__ = [
    "DEFAULT_MAX_TICKS",
    "OrchestrationTick",
    "ReadinessContext",
    "ReadinessPredicate",
    "UniversalWorkOrchestrator",
    "evaluate_readiness",
    "readiness_predicate_names",
    "register_readiness_predicate",
]
