"""EC2-CAP-ADMIN-001 — Administrative Audit & Activity Tracking (Administration Runtime).

The deterministic, append-only **administrative activity log**. It records every
administrative access evaluation and mutation as an ordered
:class:`AdministrativeAuditEvent` so administrators have a reproducible, queryable
view of *who did what, where, and whether it was granted* — the substrate for
administrative activity tracking and administrative search.

This is **not a duplicate of the canonical audit trail**. The platform's append-only,
tamper-evident audit of record is the Observability Layer's
:class:`~platform.observability.audit.AuditTrail` (L8), fed by the Foundation event
bus. The Administration Runtime emits every governed administrative action onto that
bus (so L8 captures it as the audit of record) and *additionally* keeps this
domain-scoped activity log for administrative visibility. It re-implements no L8 audit
machinery; it holds no wall-clock (a caller-supplied logical ``tick``) so the log is
reproducible (P5) and holds no secret material (SEC-04).
"""

from __future__ import annotations

from dataclasses import dataclass
from platform.administration.contracts import (
    AdministrativeAction,
    AdministrativeDomain,
    AdministrativeScope,
)
from platform.administration.errors import AdministrationAuditError
from platform.foundation.contracts import content_hash
from typing import Any


@dataclass(frozen=True, slots=True)
class AdministrativeAuditEvent:
    """An immutable, ordered record of one administrative action (append-only)."""

    sequence: int
    action: AdministrativeAction
    domain: AdministrativeDomain
    scope: AdministrativeScope
    principal_id: str
    target_id: str
    tenant: str | None
    granted: bool
    reason: str
    tick: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "sequence": self.sequence,
            "action": self.action.value,
            "domain": self.domain.value,
            "scope": self.scope.value,
            "principal_id": self.principal_id,
            "target_id": self.target_id,
            "tenant": self.tenant,
            "granted": self.granted,
            "reason": self.reason,
            "tick": self.tick,
        }


class AdministrativeAuditLog:
    """A deterministic, append-only administrative activity log."""

    __slots__ = ("_log",)

    def __init__(self) -> None:
        self._log: list[AdministrativeAuditEvent] = []

    def record(
        self,
        *,
        action: AdministrativeAction,
        domain: AdministrativeDomain,
        scope: AdministrativeScope,
        principal_id: str,
        target_id: str,
        granted: bool,
        reason: str,
        tick: int,
        tenant: str | None = None,
    ) -> AdministrativeAuditEvent:
        """Append an administrative activity record (fail-closed on bad vocabulary)."""
        if not isinstance(action, AdministrativeAction):
            raise AdministrationAuditError("audit action must be an AdministrativeAction")
        if not isinstance(domain, AdministrativeDomain):
            raise AdministrationAuditError("audit domain must be an AdministrativeDomain")
        if not isinstance(scope, AdministrativeScope):
            raise AdministrationAuditError("audit scope must be an AdministrativeScope")
        if not isinstance(principal_id, str) or not principal_id:
            raise AdministrationAuditError("audit record requires a principal_id")
        if not isinstance(reason, str) or not reason:
            raise AdministrationAuditError("audit record requires a reason")
        event = AdministrativeAuditEvent(
            sequence=len(self._log),
            action=action,
            domain=domain,
            scope=scope,
            principal_id=principal_id,
            target_id=target_id,
            tenant=tenant,
            granted=bool(granted),
            reason=reason,
            tick=tick,
        )
        self._log.append(event)
        return event

    @property
    def events(self) -> tuple[AdministrativeAuditEvent, ...]:
        """An immutable snapshot of the append-only activity log (in order)."""
        return tuple(self._log)

    def activity_of(self, principal_id: str) -> tuple[AdministrativeAuditEvent, ...]:
        """Every recorded activity for a principal, in order (activity tracking)."""
        return tuple(e for e in self._log if e.principal_id == principal_id)

    def granted_events(self) -> tuple[AdministrativeAuditEvent, ...]:
        """Every granted administrative action, in order."""
        return tuple(e for e in self._log if e.granted)

    def denied_events(self) -> tuple[AdministrativeAuditEvent, ...]:
        """Every denied administrative action, in order."""
        return tuple(e for e in self._log if not e.granted)

    def action_counts(self) -> dict[str, int]:
        """A deterministic count of recorded events per administrative action."""
        counts: dict[str, int] = {}
        for event in self._log:
            counts[event.action.value] = counts.get(event.action.value, 0) + 1
        return counts

    def __len__(self) -> int:
        return len(self._log)

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_count": len(self._log),
            "granted_count": len(self.granted_events()),
            "denied_count": len(self.denied_events()),
            "events": [e.to_dict() for e in self._log],
        }

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())


__all__ = ["AdministrativeAuditEvent", "AdministrativeAuditLog"]
