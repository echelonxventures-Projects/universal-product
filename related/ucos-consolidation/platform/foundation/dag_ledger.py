"""WP-03 — DAG Event Ledger (PRJ-C2 / ACT-C2).

The authoritative, append-only **DAG Event Ledger** — the constitutional foundation
for all *Recorded Truth*. It realizes **AIF-L08** ("Recorded Truth is a Merkle-linked,
mergeable event DAG; branches and merges are first-class") and **AIF-L17**
("Forward-Only Compensation. No deletion or edit of Recorded Truth; correction is a
new event"), and it composes the federation gap-resolution **A/G1** (branch / merge /
offline / org-split / org-merge preserve continuity with no coordination).

It **supersedes** the linear event model (:mod:`platform.foundation.events`,
``EventBus`` with a monotonic ``sequence``) with a parent-referenced event DAG,
while **preserving backward compatibility**:

    * a fresh :class:`EventDag` used like an ``EventBus`` (``append`` with no explicit
      parents) records a single linear chain — the DAG degenerates to the linear log;
    * :meth:`EventDag.from_event_bus` / :meth:`EventDag.from_platform_events` migrate an
      existing linear log into a DAG, preserving order and the original
      ``UCOS-EVT-`` event ids (the append-only history is never rewritten);
    * :meth:`EventDag.to_platform_events` projects the DAG back into the legacy
      :class:`~platform.foundation.events.PlatformEvent` shape, so existing linear
      consumers keep working.

Design (IMP-007 §5 determinism; AX-01/AX-02 bifurcation of truth):
    * :class:`DagEvent` is immutable and **carries no wall-clock**. Its identity is a
      *Merkle* hash (:attr:`DagEvent.event_hash`) binding the event core **and the
      sorted set of its parent hashes**, so altering any ancestor (or an event's own
      content) breaks the hash of every descendant — the whole DAG is tamper-evident.
    * :class:`EventDag` is append-only: it exposes no update or delete. ``append``,
      ``branch``, and ``merge`` add nodes; a parent must already be recorded (edges
      never dangle), which makes the recorded order a valid topological order by
      construction (the DAG is acyclic). Appending an event whose ``event_hash`` is
      already present is **idempotent** (AIF-L13 idempotent retry).

Like the certification ledger it generalizes, the DAG holds only in-memory events and
**never writes to the certified corpus** (DP-03); persistence, if any, is the caller's
concern via :meth:`EventDag.export` / :meth:`EventDag.from_dict`.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from platform.foundation.contracts import content_hash
from platform.foundation.errors import DagLedgerError, DagLedgerIntegrityError
from platform.foundation.events import EventBus, PlatformEvent
from typing import Any

from engine.foundation.obs.context import correlation_id
from engine.foundation.obs.logging import get_logger

_logger = get_logger("foundation.dag_ledger")

#: The genesis predecessor hash (a root event references it implicitly by having no
#: recorded parents). Mirrors the certification ledger's genesis discipline.
GENESIS_HASH = "0" * 64

#: The self-describing export format tag (semantic version — widens append-only).
DAG_LEDGER_FORMAT = "ucos-dag-event-ledger/1.0.0"

#: The legacy content-addressed event-id prefix, preserved for backward compatibility
#: with :class:`~platform.foundation.events.PlatformEvent`.
EVENT_ID_PREFIX = "UCOS-EVT-"


def _normalize_parents(parents: Iterable[str] | None) -> tuple[str, ...]:
    """Return parent hashes as a de-duplicated tuple in first-seen order.

    Order is preserved for the *recorded* edge list; the Merkle hash itself sorts
    the parents so that parent order is never identity-significant (a merge of
    ``{a, b}`` is the same event as a merge of ``{b, a}``).
    """
    if parents is None:
        return ()
    seen: dict[str, None] = {}
    for parent in parents:
        if not isinstance(parent, str) or not parent:
            raise DagLedgerError("parent reference must be a non-empty event hash")
        seen.setdefault(parent, None)
    return tuple(seen)


@dataclass(frozen=True, slots=True)
class DagEvent:
    """An immutable, content-addressed, Merkle-linked event in the ledger DAG.

    ``event_hash`` binds the event core **and** the sorted parent hashes, so it is the
    node's tamper-evident identity in the DAG. ``event_id`` is the human/legacy
    ``UCOS-EVT-`` render (derived from ``event_hash`` for native events, or preserved
    verbatim for events migrated from the linear model). ``index`` is a derived,
    per-ledger admission ordinal (append position) — a convenience total order over
    the DAG's partial order; it is **not** part of the Merkle identity.
    """

    event_type: str
    source: str
    subject: str
    parents: tuple[str, ...]
    payload: Mapping[str, Any] = field(default_factory=dict)
    correlation_id: str | None = None
    index: int = 0
    event_hash: str = ""
    event_id: str = ""

    @staticmethod
    def compute_hash(
        *,
        event_type: str,
        source: str,
        subject: str,
        payload: Mapping[str, Any],
        parents: Iterable[str],
    ) -> str:
        """The deterministic Merkle hash binding the event core to its parents."""
        return content_hash(
            {
                "event_type": event_type,
                "source": source,
                "subject": subject,
                "payload": dict(payload),
                # Sorted so that parent *order* is never identity-significant.
                "parents": sorted(parents),
            }
        )

    @classmethod
    def create(
        cls,
        event_type: str,
        source: str,
        subject: str,
        *,
        parents: Iterable[str] | None = None,
        payload: Mapping[str, Any] | None = None,
        correlation_id: str | None = None,
        index: int = 0,
        event_id: str | None = None,
    ) -> DagEvent:
        """Build a Merkle-linked event with a content-addressed ``event_hash``.

        When ``event_id`` is omitted it is derived from the Merkle hash; a supplied
        ``event_id`` (used by the migration layer) is preserved verbatim so
        append-only history keeps its original identities.
        """
        if not isinstance(event_type, str) or not event_type:
            raise DagLedgerError("event_type is required")
        if not isinstance(source, str) or not source:
            raise DagLedgerError("event source is required", event_type=event_type)
        if not isinstance(subject, str):
            raise DagLedgerError("event subject must be a string", event_type=event_type)
        if index < 0:
            raise DagLedgerError("event index must be non-negative", event_type=event_type)
        data = dict(payload or {})
        parent_tuple = _normalize_parents(parents)
        event_hash = cls.compute_hash(
            event_type=event_type,
            source=source,
            subject=subject,
            payload=data,
            parents=parent_tuple,
        )
        return cls(
            event_type=event_type,
            source=source,
            subject=subject,
            parents=parent_tuple,
            payload=data,
            correlation_id=correlation_id,
            index=index,
            event_hash=event_hash,
            event_id=event_id or f"{EVENT_ID_PREFIX}{event_hash[:16]}",
        )

    @classmethod
    def from_platform_event(
        cls,
        event: PlatformEvent,
        *,
        parents: Iterable[str] | None = None,
        index: int | None = None,
    ) -> DagEvent:
        """Wrap a legacy :class:`PlatformEvent` as a DAG event (migration layer).

        The original ``event_id`` and ``payload`` are preserved verbatim; the DAG
        identity (``event_hash``) is computed over the event core plus ``parents``.
        """
        if not isinstance(event, PlatformEvent):
            raise DagLedgerError("from_platform_event expects a PlatformEvent")
        return cls.create(
            event.event_type,
            event.source,
            event.subject,
            parents=parents,
            payload=event.payload,
            correlation_id=event.correlation_id,
            index=event.sequence if index is None else index,
            event_id=event.event_id,
        )

    @property
    def is_root(self) -> bool:
        """True iff the event has no recorded parent (a genesis/root of the DAG)."""
        return not self.parents

    @property
    def is_merge(self) -> bool:
        """True iff the event has more than one parent (a first-class merge)."""
        return len(self.parents) > 1

    def recompute_hash(self) -> str:
        """Recompute the Merkle hash from the current field values."""
        return self.compute_hash(
            event_type=self.event_type,
            source=self.source,
            subject=self.subject,
            payload=self.payload,
            parents=self.parents,
        )

    def verify_integrity(self) -> bool:
        """Return True iff the stored ``event_hash`` matches a recomputation."""
        return self.recompute_hash() == self.event_hash

    def to_platform_event(self) -> PlatformEvent:
        """Project back into the legacy :class:`PlatformEvent` shape (backward compat).

        The admission ordinal (``index``) becomes the linear ``sequence`` and the
        original ``event_id`` is preserved, so a linear consumer sees a faithful,
        ordered projection of the DAG.
        """
        return PlatformEvent(
            event_type=self.event_type,
            source=self.source,
            subject=self.subject,
            sequence=self.index,
            payload=dict(self.payload),
            correlation_id=self.correlation_id,
            event_id=self.event_id,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id,
            "event_hash": self.event_hash,
            "event_type": self.event_type,
            "source": self.source,
            "subject": self.subject,
            "parents": list(self.parents),
            "payload": dict(self.payload),
            "correlation_id": self.correlation_id,
            "index": self.index,
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> DagEvent:
        """Reconstruct an event from its :meth:`to_dict` form (used by import)."""
        if not isinstance(data, Mapping):
            raise DagLedgerError("event record must be a mapping")
        try:
            event_type = data["event_type"]
            source = data["source"]
            subject = data["subject"]
        except (KeyError, TypeError) as exc:
            raise DagLedgerError("event record is missing required fields") from exc
        return cls.create(
            event_type,
            source,
            subject,
            parents=data.get("parents") or (),
            payload=data.get("payload") or {},
            correlation_id=data.get("correlation_id"),
            index=int(data.get("index", 0)),
            event_id=data.get("event_id"),
        )


class EventDag:
    """An append-only, Merkle-linked, in-memory event DAG (DP-03 safe, WP-03).

    Nodes are keyed by their :attr:`DagEvent.event_hash`. ``append`` records a child
    of the current head(s); ``branch`` records a child of one explicit parent (a
    divergence); ``merge`` records a child of several parents (a convergence). A
    parent must already be recorded, so edges never dangle and the recorded order is
    always a valid topological order (the DAG is acyclic by construction).
    """

    __slots__ = ("_nodes", "_order", "_children")

    def __init__(self) -> None:
        # event_hash -> event (insertion preserved by _order).
        self._nodes: dict[str, DagEvent] = {}
        # event_hash in append (admission-ordinal) order.
        self._order: list[str] = []
        # event_hash -> set of child event_hashes (derived adjacency for head calc).
        self._children: dict[str, set[str]] = {}

    # -- introspection ------------------------------------------------------------

    def __len__(self) -> int:
        return len(self._order)

    def __contains__(self, ref: str) -> bool:
        return ref in self._nodes or any(e.event_id == ref for e in self._nodes.values())

    @property
    def events(self) -> tuple[DagEvent, ...]:
        """An immutable snapshot of the DAG in admission (append) order."""
        return tuple(self._nodes[h] for h in self._order)

    @property
    def heads(self) -> tuple[str, ...]:
        """The head hashes — recorded events that are no parent's parent (the tips).

        Head computation is a pure function of the recorded edges. An empty DAG has
        no heads; a linear DAG has exactly one; a branched DAG has several.
        """
        return tuple(h for h in self._order if not self._children.get(h))

    @property
    def roots(self) -> tuple[str, ...]:
        """The root hashes — recorded events that have no parent (genesis events)."""
        return tuple(h for h in self._order if not self._nodes[h].parents)

    def get(self, ref: str) -> DagEvent:
        """Return the event for ``ref`` (an ``event_hash`` or legacy ``event_id``).

        Raises:
            DagLedgerError: if no such event is recorded (fail-closed).
        """
        event = self._nodes.get(ref)
        if event is not None:
            return event
        for candidate in self._nodes.values():
            if candidate.event_id == ref:
                return candidate
        raise DagLedgerError("event not found in DAG", ref=ref)

    def children(self, ref: str) -> tuple[DagEvent, ...]:
        """The direct children of ``ref`` in admission order."""
        parent = self.get(ref)
        child_hashes = self._children.get(parent.event_hash, set())
        return tuple(self._nodes[h] for h in self._order if h in child_hashes)

    def ancestors(self, ref: str) -> tuple[DagEvent, ...]:
        """All transitive ancestors of ``ref`` in admission order (excludes ``ref``)."""
        start = self.get(ref)
        seen: set[str] = set()
        frontier = list(start.parents)
        while frontier:
            current = frontier.pop()
            if current in seen or current not in self._nodes:
                continue
            seen.add(current)
            frontier.extend(self._nodes[current].parents)
        return tuple(self._nodes[h] for h in self._order if h in seen)

    # -- append-only mutation -----------------------------------------------------

    def _append(
        self,
        event_type: str,
        source: str,
        subject: str,
        *,
        parents: tuple[str, ...],
        payload: Mapping[str, Any] | None,
        event_id: str | None = None,
    ) -> DagEvent:
        """Record one event; idempotent by ``event_hash`` (AIF-L13 idempotent retry)."""
        for parent in parents:
            if parent not in self._nodes:
                raise DagLedgerError(
                    "parent event is not recorded in the DAG (edges never dangle)",
                    parent=parent,
                    event_type=event_type,
                )
        event = DagEvent.create(
            event_type,
            source,
            subject,
            parents=parents,
            payload=payload,
            correlation_id=correlation_id(),
            index=len(self._order),
            event_id=event_id,
        )
        existing = self._nodes.get(event.event_hash)
        if existing is not None:
            # Same content + same parents ⇒ the same node. Re-recording is a no-op.
            return existing
        self._nodes[event.event_hash] = event
        self._order.append(event.event_hash)
        self._children.setdefault(event.event_hash, set())
        for parent in parents:
            self._children[parent].add(event.event_hash)
        _logger.info(
            "foundation.dag_ledger.appended",
            event_id=event.event_id,
            event_type=event_type,
            parents=len(parents),
            index=event.index,
        )
        return event

    def append(
        self,
        event_type: str,
        source: str,
        subject: str,
        *,
        payload: Mapping[str, Any] | None = None,
        parents: Iterable[str] | None = None,
    ) -> DagEvent:
        """Append an event as a child of the current head(s).

        With no explicit ``parents`` the event chains onto the single current head
        (genesis when the DAG is empty), so a fresh DAG behaves like the linear
        ``EventBus``. If the DAG has diverged into several heads, a plain ``append``
        is ambiguous and fails closed — use :meth:`merge` (or pass ``parents``)
        to converge them explicitly.
        """
        if parents is None:
            current = self.heads
            if len(current) > 1:
                raise DagLedgerError(
                    "DAG has multiple heads; use merge() or pass explicit parents",
                    heads=len(current),
                )
            resolved = current
        else:
            resolved = _normalize_parents(parents)
        return self._append(event_type, source, subject, parents=resolved, payload=payload)

    def branch(
        self,
        parent: str,
        event_type: str,
        source: str,
        subject: str,
        *,
        payload: Mapping[str, Any] | None = None,
    ) -> DagEvent:
        """Append an event as a child of one explicit ``parent`` — a divergence.

        Branching an already-parented event creates a second child, so the DAG grows
        an additional head (a first-class branch, AIF-L08 / A/G1).
        """
        parent_event = self.get(parent)
        return self._append(
            event_type,
            source,
            subject,
            parents=(parent_event.event_hash,),
            payload=payload,
        )

    def merge(
        self,
        parents: Iterable[str],
        event_type: str,
        source: str,
        subject: str,
        *,
        payload: Mapping[str, Any] | None = None,
    ) -> DagEvent:
        """Append an event that converges several ``parents`` — a first-class merge.

        Requires at least two distinct, recorded parents (a one-parent "merge" is a
        plain append; a zero-parent merge is meaningless). Parent references are
        resolved from ``event_hash`` or legacy ``event_id`` (AIF-L08 / A/G1).
        """
        resolved = tuple(self.get(p).event_hash for p in _normalize_parents(parents))
        if len(resolved) < 2:
            raise DagLedgerError(
                "merge requires at least two distinct parents",
                parents=len(resolved),
            )
        return self._append(event_type, source, subject, parents=resolved, payload=payload)

    # -- integrity ----------------------------------------------------------------

    def verify(self) -> bool:
        """Return True iff the whole DAG is intact (tamper-evident, acyclic).

        Checks, for every recorded event: (1) its stored ``event_hash`` matches a
        recomputation over its content + parents, and (2) every parent is recorded
        **earlier** in admission order — i.e. the parents-before-children topology
        holds, which also proves acyclicity. Any edit of Recorded Truth is detected.
        """
        position: dict[str, int] = {}
        for pos, event_hash in enumerate(self._order):
            event = self._nodes[event_hash]
            if event.recompute_hash() != event.event_hash:
                return False
            for parent in event.parents:
                if parent not in position:
                    # Parent unknown or recorded after the child ⇒ broken topology.
                    return False
            position[event_hash] = pos
        return True

    def require_intact(self) -> None:
        """Raise :class:`DagLedgerIntegrityError` if the DAG is not intact."""
        if not self.verify():
            raise DagLedgerIntegrityError(
                "DAG event ledger integrity check failed (Recorded Truth mutated)",
                events=len(self._order),
            )

    def fingerprint(self) -> str:
        """A deterministic content hash of the whole DAG (for replay/equality checks)."""
        return content_hash(self.export())

    # -- export / import ----------------------------------------------------------

    def export(self) -> dict[str, Any]:
        """Serialize the DAG to a deterministic, self-describing dict."""
        return {
            "ledger_format": DAG_LEDGER_FORMAT,
            "count": len(self._order),
            "heads": list(self.heads),
            "roots": list(self.roots),
            "events": [self._nodes[h].to_dict() for h in self._order],
        }

    #: Alias kept parallel with the certification ledger's ``to_dict`` surface.
    to_dict = export

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> EventDag:
        """Reconstruct (import) a DAG from its :meth:`export` form, verifying it.

        Events are replayed in their recorded order; a parent that is not yet present
        fails closed (broken topology), and any event whose recomputed Merkle hash
        does not match its stored ``event_hash`` raises
        :class:`DagLedgerIntegrityError` — so an imported DAG is intact by
        construction.
        """
        if not isinstance(data, Mapping):
            raise DagLedgerError("DAG export must be a mapping")
        events = data.get("events")
        if not isinstance(events, list):
            raise DagLedgerError("DAG export has no 'events' list")
        dag = cls()
        for record in events:
            declared = record.get("event_hash") if isinstance(record, Mapping) else None
            parsed = DagEvent.from_dict(record)
            if declared is not None and declared != parsed.event_hash:
                raise DagLedgerIntegrityError(
                    "imported event hash does not match its content (tamper detected)",
                    expected=declared,
                    actual=parsed.event_hash,
                )
            dag._append(
                parsed.event_type,
                parsed.source,
                parsed.subject,
                parents=parsed.parents,
                payload=parsed.payload,
                event_id=parsed.event_id,
            )
        return dag

    # -- backward-compatible migration layer --------------------------------------

    @classmethod
    def from_platform_events(cls, events: Iterable[PlatformEvent]) -> EventDag:
        """Migrate a linear sequence of :class:`PlatformEvent` into a linear DAG.

        Each event is chained to its immediate predecessor, preserving the original
        order and ``event_id`` values. The result is a single-chain DAG whose
        :attr:`heads` is the last migrated event — the append-only history is carried
        forward unchanged, never rewritten (AIF-L17).
        """
        dag = cls()
        prev: tuple[str, ...] = ()
        for event in events:
            node = DagEvent.from_platform_event(event, parents=prev)
            recorded = dag._append(
                node.event_type,
                node.source,
                node.subject,
                parents=prev,
                payload=node.payload,
                event_id=node.event_id,
            )
            prev = (recorded.event_hash,)
        return dag

    @classmethod
    def from_event_bus(cls, bus: EventBus) -> EventDag:
        """Migrate an existing linear :class:`EventBus` into a DAG (backward compat)."""
        if not isinstance(bus, EventBus):
            raise DagLedgerError("from_event_bus expects an EventBus")
        return cls.from_platform_events(bus.events)

    def to_platform_events(self) -> tuple[PlatformEvent, ...]:
        """Project the DAG into the legacy linear :class:`PlatformEvent` shape.

        Events are emitted in admission order with ``sequence == index``, preserving
        each ``event_id``, so a linear consumer can read the DAG as an ordered log.
        """
        return tuple(self._nodes[h].to_platform_event() for h in self._order)


__all__ = [
    "GENESIS_HASH",
    "DAG_LEDGER_FORMAT",
    "EVENT_ID_PREFIX",
    "DagEvent",
    "EventDag",
]
