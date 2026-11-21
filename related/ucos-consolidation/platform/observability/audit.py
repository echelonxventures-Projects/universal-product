"""EC2-TASK-000184 — Platform Audit Trail (EC2-EPIC-013).

An append-only, deterministic audit trail recording **every governed action** as an
immutable, content-addressed :class:`AuditEvent` with a verifiable hash chain
(acceptance P9 "append-only audit complete"; PC-16 audit & traceability; go-live G8
"audit records exist for every governed action").

Design (P9/PC-16 audit; IMP-007 §5 determinism; append-only immutability):
    * :class:`AuditEvent` is immutable and **carries no wall-clock** — ordering is a
      monotonic ``sequence`` assigned on append. Each event chains to the previous
      event's hash (``prev_hash`` → ``event_hash``), giving a tamper-evident,
      verifiable chain analogous to the EC-1 certification ledger.
    * :class:`AuditTrail` is strictly append-only: there is no update or delete path;
      :meth:`AuditTrail.verify` recomputes the chain and detects any divergence
      (fail-closed).
    * No secret material is recorded (SEC-04); callers pass references/identifiers.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from platform.foundation.contracts import content_hash
from platform.observability.errors import AuditError
from typing import Any

#: The genesis previous-hash for the first event in an audit trail.
GENESIS_HASH = "0" * 64


@dataclass(frozen=True, slots=True)
class AuditEvent:
    """An immutable, content-addressed, hash-chained audit event (no wall-clock)."""

    action: str
    actor: str
    subject: str
    sequence: int
    prev_hash: str
    outcome: str = "recorded"
    detail: Mapping[str, Any] = field(default_factory=dict)
    event_hash: str = ""
    event_id: str = ""

    @classmethod
    def create(
        cls,
        action: str,
        actor: str,
        subject: str,
        sequence: int,
        prev_hash: str,
        *,
        outcome: str = "recorded",
        detail: Mapping[str, Any] | None = None,
    ) -> AuditEvent:
        """Build a chained audit event with a deterministic hash + id."""
        if not isinstance(action, str) or not action:
            raise AuditError("audit action is required")
        if not isinstance(actor, str) or not actor:
            raise AuditError("audit actor is required", action=action)
        if sequence < 0:
            raise AuditError("audit sequence must be non-negative", action=action)
        if not isinstance(prev_hash, str) or len(prev_hash) != 64:
            raise AuditError("audit prev_hash must be a 64-char digest", action=action)
        data = dict(detail or {})
        core = {
            "action": action,
            "actor": actor,
            "subject": subject,
            "sequence": sequence,
            "prev_hash": prev_hash,
            "outcome": outcome,
            "detail": data,
        }
        event_hash = content_hash(core)
        return cls(
            action=action,
            actor=actor,
            subject=subject,
            sequence=sequence,
            prev_hash=prev_hash,
            outcome=outcome,
            detail=data,
            event_hash=event_hash,
            event_id=f"UCOS-AUDIT-{event_hash[:16]}",
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id,
            "action": self.action,
            "actor": self.actor,
            "subject": self.subject,
            "sequence": self.sequence,
            "prev_hash": self.prev_hash,
            "outcome": self.outcome,
            "detail": dict(self.detail),
            "event_hash": self.event_hash,
        }


class AuditTrail:
    """A deterministic, append-only, hash-chained audit trail (fail-closed verify)."""

    __slots__ = ("_events",)

    def __init__(self) -> None:
        self._events: list[AuditEvent] = []

    def record(
        self,
        action: str,
        actor: str,
        subject: str,
        *,
        outcome: str = "recorded",
        detail: Mapping[str, Any] | None = None,
    ) -> AuditEvent:
        """Append a governed-action audit event chained to the current head."""
        prev_hash = self._events[-1].event_hash if self._events else GENESIS_HASH
        event = AuditEvent.create(
            action, actor, subject, len(self._events), prev_hash, outcome=outcome, detail=detail
        )
        self._events.append(event)
        return event

    @property
    def events(self) -> tuple[AuditEvent, ...]:
        """An immutable snapshot of the append-only audit trail (in order)."""
        return tuple(self._events)

    def __len__(self) -> int:
        return len(self._events)

    @property
    def head_hash(self) -> str:
        """The hash of the most recent event (or the genesis hash if empty)."""
        return self._events[-1].event_hash if self._events else GENESIS_HASH

    def events_for(self, action: str) -> tuple[AuditEvent, ...]:
        return tuple(e for e in self._events if e.action == action)

    def verify(self) -> bool:
        """Recompute the chain and return True iff it is intact (fail-closed)."""
        expected_prev = GENESIS_HASH
        for index, event in enumerate(self._events):
            if event.sequence != index:
                return False
            if event.prev_hash != expected_prev:
                return False
            recomputed = AuditEvent.create(
                event.action,
                event.actor,
                event.subject,
                event.sequence,
                event.prev_hash,
                outcome=event.outcome,
                detail=event.detail,
            )
            if recomputed.event_hash != event.event_hash:
                return False
            expected_prev = event.event_hash
        return True

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_count": len(self._events),
            "head_hash": self.head_hash,
            "events": [e.to_dict() for e in self._events],
        }

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())


__all__ = ["GENESIS_HASH", "AuditEvent", "AuditTrail"]
