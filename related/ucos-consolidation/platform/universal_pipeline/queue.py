"""UAPF-000001 — the derived queue topology and the batch former.

The queue topology, the membership rules, the ordering rule, the enqueue/dequeue
semantics, the invariants and the batch-formation rules implemented here are **Repository
Truth**: ``04-EXECUTION-QUEUE-MODEL.md`` and ``05-BATCH-GENERATION-RULES.md`` already
legislate them. This module is their executable projection over UAPF execution units and
invents no queue, no ordering criterion and no batching policy of its own.

Derived membership, not manual enqueue
--------------------------------------
``04`` §5 invariant 1 is *no manual enqueue*: membership is a function of the units
admitted, never of a caller's choice. So there is no ``insert_at``, no priority argument
and no reorder operation anywhere in this class. A unit's queue is a function of its
state, and its position is a function of ``(wave, family, unit_id)`` — ``04`` §3's single
ordering rule. Both are recomputed on read rather than stored, so a queue cannot be
stale, and two runs over the same admissions produce identical queues.

Every membership change goes through
:func:`~platform.universal_pipeline.state.require_unit_transition`, so an illegal
lifecycle move cannot enter a queue in the first place — the queue does not need its own
guard because the state engine already is one.

Batching
--------
:meth:`PipelineQueueManager.cut` implements ``05`` §2 exactly: one wave only (B1),
ready-only members (B2), order preserved from the ready-queue head (B3), size capped at
``min(wave width, MAX_BATCH)`` (B4), sentinels never batched (B6). B1 is the reason
``cut`` takes no wave argument: mixing waves would be the caller's choice, and the safe
wave is derivable — it is the lowest wave present in the ready queue.

Determinism: no wall-clock, no RNG, no I/O. Cutting the same ready queue with the same cap
always yields the same batch (``05`` §9).
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from platform.foundation.contracts import content_hash
from platform.universal_pipeline.errors import PipelineQueueError
from platform.universal_pipeline.events import PipelineEventBus
from platform.universal_pipeline.identity import Identity, mint
from platform.universal_pipeline.state import (
    DEFAULT_MAX_RETRY,
    INITIAL_STATE,
    is_terminal,
    require_retry_budget,
    require_state,
    require_unit_transition,
)
from typing import Any

#: The states whose members constitute the Execution Queue (``04`` §2: admitted and not
#: yet retired). Derived from the lifecycle rather than listed independently of it.
_EXECUTION_QUEUE_STATES: frozenset[str] = frozenset(
    {"SPECIFIED", "READY", "EXECUTING", "IMPLEMENTED", "VALIDATED", "BLOCKED", "FAILED"}
)

#: The state whose members constitute the Ready Queue (``04`` §2).
_READY_STATE = "READY"

#: The state whose members constitute the current Execution Batch (``04`` §1).
_BATCH_STATE = "EXECUTING"

#: The state whose members constitute the Blocked Set (``04`` §2).
_BLOCKED_STATE = "BLOCKED"

#: The states whose members have reached the Completed sink (``04`` §1).
_COMPLETED_STATES: frozenset[str] = frozenset({"CERTIFIED", "ARCHIVED", "SUPERSEDED"})


@dataclass(frozen=True, slots=True)
class QueueEntry:
    """One membership record: a unit, its position coordinates, and its lifecycle state.

    ``wave`` and ``family`` are the position coordinates ``04`` §3 names; they are
    *declared* by the admitting caller (they describe the unit's place in the work
    breakdown) and are never mutated by a queue operation, because a queue that could
    change a unit's position would not have a derived order.

    ``excluded`` marks a sentinel: something admitted for completeness that is NOT
    REQUIRED and must never be batched (``05`` B6). It is a separate flag rather than a
    state because an excluded unit has no lifecycle — it was never work.
    """

    unit_id: str
    pipeline_id: str
    version: str
    wave: int = 1
    family: str = ""
    state: str = INITIAL_STATE
    attempts: int = 0
    reason: str = ""
    excluded: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.unit_id, str) or not self.unit_id:
            raise PipelineQueueError("queue entry unit id is required")
        if not isinstance(self.pipeline_id, str) or not self.pipeline_id:
            raise PipelineQueueError("queue entry pipeline id is required", unit_id=self.unit_id)
        if not isinstance(self.version, str) or not self.version:
            raise PipelineQueueError("queue entry version is required", unit_id=self.unit_id)
        if not isinstance(self.wave, int) or isinstance(self.wave, bool) or self.wave < 1:
            raise PipelineQueueError(
                "queue entry wave must be an integer >= 1", unit_id=self.unit_id, wave=self.wave
            )
        if not isinstance(self.family, str):
            raise PipelineQueueError("queue entry family must be a string", unit_id=self.unit_id)
        require_state(self.state)
        if self.attempts < 0:
            raise PipelineQueueError(
                "queue entry attempts must be non-negative", unit_id=self.unit_id
            )

    @property
    def identity(self) -> Identity:
        return mint("queue-entry", self.unit_id, self.pipeline_id, self.version)

    @property
    def position(self) -> tuple[int, str, str]:
        """The ``04`` §3 ordering key: wave ascending, family ascending, id ascending."""
        return (self.wave, self.family, self.unit_id)

    def to_dict(self) -> dict[str, Any]:
        return {
            "unit_id": self.unit_id,
            "pipeline_id": self.pipeline_id,
            "version": self.version,
            "wave": self.wave,
            "family": self.family,
            "state": self.state,
            "attempts": self.attempts,
            "reason": self.reason,
            "excluded": self.excluded,
        }

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())


class PipelineQueueManager:
    """The derived queues of one platform instance, and the only batch former.

    Holds one record per admitted unit and derives every queue from those records. There
    is no per-queue collection to keep in step: the Execution Queue, the Ready Queue, the
    current batch, the Blocked Set, the Excluded Set and the sinks are all filters over
    the same records, so ``04`` §5 invariant 4 (batch ⊆ ready ⊆ execution, excluded
    disjoint) holds by construction rather than by checking.
    """

    __slots__ = ("_entries", "_bus", "_max_retry")

    def __init__(
        self,
        *,
        bus: PipelineEventBus | None = None,
        max_retry: int = DEFAULT_MAX_RETRY,
    ) -> None:
        if bus is not None and not isinstance(bus, PipelineEventBus):
            raise PipelineQueueError("bus must be a PipelineEventBus")
        if max_retry < 0:
            raise PipelineQueueError("max_retry must be non-negative", max_retry=max_retry)
        self._entries: dict[str, QueueEntry] = {}
        self._bus = bus
        self._max_retry = max_retry

    # -- admission --------------------------------------------------------------------

    def enqueue(self, entry: QueueEntry) -> QueueEntry:
        """Admit ``entry`` into the Execution Queue at its derived position.

        Raises:
            PipelineQueueError: if ``entry`` is not a :class:`QueueEntry`, its unit id is
                already admitted, or it does not arrive in the initial state (a unit joins
                the queue as ``SPECIFIED`` and advances only through the lifecycle guard).
        """
        if not isinstance(entry, QueueEntry):
            raise PipelineQueueError("only a QueueEntry can be enqueued")
        if entry.unit_id in self._entries:
            raise PipelineQueueError("unit already admitted to the queue", unit_id=entry.unit_id)
        if entry.state != INITIAL_STATE:
            raise PipelineQueueError(
                "a unit must be admitted in the initial state",
                unit_id=entry.unit_id,
                state=entry.state,
                initial_state=INITIAL_STATE,
            )
        self._entries[entry.unit_id] = entry
        self._record("uapf.queue.enqueued", entry)
        return entry

    def __contains__(self, unit_id: str) -> bool:
        return unit_id in self._entries

    def __len__(self) -> int:
        return len(self._entries)

    def entry(self, unit_id: str) -> QueueEntry:
        """The record for ``unit_id`` (fail-closed if it was never admitted)."""
        record = self._entries.get(unit_id)
        if record is None:
            raise PipelineQueueError("no such unit in the queue", unit_id=unit_id)
        return record

    # -- derived queues ---------------------------------------------------------------

    def _ordered(self, states: frozenset[str], *, excluded: bool = False) -> tuple[QueueEntry, ...]:
        """Every non-/excluded record in ``states``, in ``04`` §3 derived order."""
        return tuple(
            sorted(
                (
                    entry
                    for entry in self._entries.values()
                    if entry.state in states and entry.excluded is excluded
                ),
                key=lambda entry: entry.position,
            )
        )

    @property
    def execution_queue(self) -> tuple[QueueEntry, ...]:
        """Every admitted, non-excluded, non-retired unit in derived order (``04`` §2)."""
        return self._ordered(_EXECUTION_QUEUE_STATES)

    @property
    def ready_queue(self) -> tuple[QueueEntry, ...]:
        """The READY subset, inheriting the Execution Queue's order (``04`` §2)."""
        return self._ordered(frozenset({_READY_STATE}))

    @property
    def execution_batch(self) -> tuple[QueueEntry, ...]:
        """The units currently reserved for execution (``04`` §1)."""
        return self._ordered(frozenset({_BATCH_STATE}))

    @property
    def blocked_set(self) -> tuple[QueueEntry, ...]:
        """Executable units failing at least one readiness predicate (``04`` §2)."""
        return self._ordered(frozenset({_BLOCKED_STATE}))

    @property
    def excluded_set(self) -> tuple[QueueEntry, ...]:
        """The NOT REQUIRED sentinels — never batched (``04`` §2, ``05`` B6)."""
        return tuple(
            sorted(
                (entry for entry in self._entries.values() if entry.excluded),
                key=lambda entry: entry.position,
            )
        )

    @property
    def completed(self) -> tuple[QueueEntry, ...]:
        """Units that reached the Completed sink (``04`` §1)."""
        return self._ordered(_COMPLETED_STATES)

    @property
    def failed(self) -> tuple[QueueEntry, ...]:
        """Units in the Failed sink, awaiting retry or escalation (``04`` §1)."""
        return self._ordered(frozenset({"FAILED"}))

    # -- operations (``04`` §4) -------------------------------------------------------

    def promote(self, unit_id: str) -> QueueEntry:
        """Promote ``unit_id`` to the Ready Queue, preserving its derived position.

        Raises:
            PipelineQueueError: if the unit is unknown, is excluded (a sentinel is never
                promoted), or the transition to ``READY`` is illegal from its state.
        """
        entry = self.entry(unit_id)
        self._require_not_excluded(entry, "promoted")
        return self._advance(entry, _READY_STATE, "uapf.queue.promoted")

    def demote(self, unit_id: str, reason: str) -> QueueEntry:
        """Demote ``unit_id`` to the Blocked Set with a stated ``reason``.

        The reason is required, not optional: ``04`` §2 keys the Blocked Set *by block
        reason*, so a blocked unit with no reason would be unqueryable.

        Raises:
            PipelineQueueError: if the unit is unknown, no reason is given, or the
                transition to ``BLOCKED`` is illegal from its state.
        """
        if not isinstance(reason, str) or not reason:
            raise PipelineQueueError("a block reason is required", unit_id=unit_id)
        entry = self.entry(unit_id)
        return self._advance(entry, _BLOCKED_STATE, "uapf.queue.demoted", reason=reason)

    def exclude(self, unit_id: str, reason: str) -> QueueEntry:
        """Mark ``unit_id`` as a NOT REQUIRED sentinel: excluded from every active queue.

        Raises:
            PipelineQueueError: if the unit is unknown, no reason is given, or the unit
                has already begun executing (excluding work in flight would lose it).
        """
        if not isinstance(reason, str) or not reason:
            raise PipelineQueueError("an exclusion reason is required", unit_id=unit_id)
        entry = self.entry(unit_id)
        if entry.state not in {INITIAL_STATE, _BLOCKED_STATE, _READY_STATE}:
            raise PipelineQueueError(
                "only a not-yet-executing unit can be excluded",
                unit_id=unit_id,
                state=entry.state,
            )
        updated = replace(entry, excluded=True, reason=reason)
        self._entries[unit_id] = updated
        self._record("uapf.queue.retired", updated, extra={"disposition": "EXCLUDED"})
        return updated

    def cut(self, *, max_batch: int | None = None) -> tuple[QueueEntry, ...]:
        """Cut the next Execution Batch from the Ready Queue head (``05`` §2).

        One wave only (B1) — the lowest wave present in the Ready Queue, so the wave is
        derived and not chosen. Order is preserved from the head (B3); size is capped at
        ``min(wave width, max_batch)`` (B4); sentinels cannot appear because they are not
        in the Ready Queue (B6). Every member is transitioned to ``EXECUTING``, which
        *is* the reservation — a cut unit has left the Ready Queue by construction.

        Returns an empty tuple when the Ready Queue is empty: nothing to dispatch is a
        normal steady state for a continuous orchestrator, not an error.

        Raises:
            PipelineQueueError: if ``max_batch`` is not a positive integer.
        """
        if max_batch is not None and (not isinstance(max_batch, int) or max_batch < 1):
            raise PipelineQueueError("max_batch must be a positive integer", max_batch=max_batch)
        ready = self.ready_queue
        if not ready:
            return ()
        wave = ready[0].wave
        members = [entry for entry in ready if entry.wave == wave]
        if max_batch is not None:
            members = members[:max_batch]
        cut = tuple(self._advance(entry, _BATCH_STATE, None) for entry in members)
        if self._bus is not None:
            self._bus.emit(
                "uapf.queue.cut",
                f"wave-{wave}",
                payload={
                    "wave": wave,
                    "size": len(cut),
                    "max_batch": max_batch,
                    "unit_ids": [entry.unit_id for entry in cut],
                },
            )
        return cut

    def advance(self, unit_id: str, to_state: str) -> QueueEntry:
        """Advance ``unit_id`` to ``to_state`` through the lifecycle guard.

        The general transition operation the runtime and the assurance engine use. It
        adds no policy of its own: legality is decided entirely by
        :func:`~platform.universal_pipeline.state.require_unit_transition`.

        Raises:
            PipelineQueueError: if the unit is unknown.
            PipelineStateError: if the transition is illegal.
        """
        return self._advance(self.entry(unit_id), to_state, "uapf.unit.state-changed")

    def fail(self, unit_id: str, reason: str) -> QueueEntry:
        """Route ``unit_id`` to the Failed sink with a stated ``reason``.

        Raises:
            PipelineQueueError: if the unit is unknown or no reason is given.
            PipelineStateError: if the unit cannot legally fail from its state.
        """
        if not isinstance(reason, str) or not reason:
            raise PipelineQueueError("a failure reason is required", unit_id=unit_id)
        return self._advance(
            self.entry(unit_id), "FAILED", "uapf.unit.state-changed", reason=reason
        )

    def retry(self, unit_id: str) -> QueueEntry:
        """Return a failed ``unit_id`` to the Ready Queue, consuming retry budget (R1–R3).

        Re-admission preserves the derived position (R3) because position is a property of
        the unit and no operation here can change it.

        Raises:
            PipelineQueueError: if the unit is unknown.
            PipelineStateError: if the unit is not FAILED, or the retry budget is
                exhausted — in which case the caller must escalate and archive, never
                drop the unit silently (R1).
        """
        entry = self.entry(unit_id)
        require_retry_budget(entry.attempts, max_retry=self._max_retry)
        require_unit_transition(entry.state, _READY_STATE)
        updated = replace(entry, state=_READY_STATE, attempts=entry.attempts + 1, reason="retry")
        self._entries[unit_id] = updated
        self._record("uapf.queue.promoted", updated, extra={"retry": updated.attempts})
        return updated

    def retire(self, unit_id: str, *, to_state: str = "ARCHIVED") -> QueueEntry:
        """Retire ``unit_id`` into a terminal sink, removing it from every active queue.

        Raises:
            PipelineQueueError: if the unit is unknown or ``to_state`` is not terminal.
            PipelineStateError: if the transition to ``to_state`` is illegal.
        """
        entry = self.entry(unit_id)
        require_state(to_state)
        if not is_terminal(to_state):
            raise PipelineQueueError(
                "retirement requires a terminal state", unit_id=unit_id, to_state=to_state
            )
        return self._advance(entry, to_state, "uapf.queue.retired")

    # -- invariants (``04`` §5) -------------------------------------------------------

    def require_invariants(self) -> None:
        """Fail closed unless the ``04`` §5 queue invariants hold.

        Checks the two invariants that are *checkable* rather than structural: batch ⊆
        ready-eligible ⊆ execution-queue membership by state, and disjointness of the
        Excluded Set from every active queue. Order stability and no-manual-enqueue are
        structural — no operation exists that could break them — so there is nothing to
        check for those, which is the stronger guarantee.

        Raises:
            PipelineQueueError: naming the violated invariant and the offending units.
        """
        excluded_ids = {entry.unit_id for entry in self.excluded_set}
        active_ids = {
            entry.unit_id
            for group in (self.execution_queue, self.ready_queue, self.execution_batch)
            for entry in group
        }
        overlap = sorted(excluded_ids & active_ids)
        if overlap:
            raise PipelineQueueError(
                "excluded sentinels must be disjoint from every active queue",
                units=overlap,
            )
        waves = {entry.wave for entry in self.execution_batch}
        if len(waves) > 1:
            raise PipelineQueueError(
                "an execution batch must be drawn from one wave only (B1)",
                waves=sorted(waves),
            )

    # -- internals / evidence ---------------------------------------------------------

    def _require_not_excluded(self, entry: QueueEntry, operation: str) -> None:
        if entry.excluded:
            raise PipelineQueueError(
                f"an excluded sentinel is never {operation}", unit_id=entry.unit_id
            )

    def _advance(
        self,
        entry: QueueEntry,
        to_state: str,
        category: str | None,
        *,
        reason: str | None = None,
    ) -> QueueEntry:
        """The single mutation path: guard the transition, replace the record, record it."""
        require_unit_transition(entry.state, to_state)
        updated = replace(
            entry, state=to_state, reason=reason if reason is not None else entry.reason
        )
        self._entries[entry.unit_id] = updated
        if category is not None:
            self._record(category, updated, extra={"from_state": entry.state})
        return updated

    def _record(
        self,
        category: str,
        entry: QueueEntry,
        *,
        extra: dict[str, Any] | None = None,
    ) -> None:
        if self._bus is None:
            return
        payload: dict[str, Any] = {
            "unit_id": entry.unit_id,
            "pipeline_id": entry.pipeline_id,
            "version": entry.version,
            "state": entry.state,
            "wave": entry.wave,
        }
        if entry.reason:
            payload["reason"] = entry.reason
        if extra:
            payload.update(extra)
        self._bus.emit(category, entry.unit_id, payload=payload)

    def to_dict(self) -> dict[str, Any]:
        """A deterministic, serializable render of every derived queue (evidence)."""
        return {
            "admitted": len(self._entries),
            "max_retry": self._max_retry,
            "execution_queue": [entry.unit_id for entry in self.execution_queue],
            "ready_queue": [entry.unit_id for entry in self.ready_queue],
            "execution_batch": [entry.unit_id for entry in self.execution_batch],
            "blocked_set": [
                {"unit_id": entry.unit_id, "reason": entry.reason} for entry in self.blocked_set
            ],
            "excluded_set": [entry.unit_id for entry in self.excluded_set],
            "completed": [entry.unit_id for entry in self.completed],
            "failed": [
                {"unit_id": entry.unit_id, "reason": entry.reason, "attempts": entry.attempts}
                for entry in self.failed
            ],
            "entries": [
                entry.to_dict()
                for entry in sorted(self._entries.values(), key=lambda entry: entry.position)
            ],
        }

    def fingerprint(self) -> str:
        """A deterministic content hash of the whole queue state."""
        return content_hash(self.to_dict())


__all__ = ["PipelineQueueManager", "QueueEntry"]
