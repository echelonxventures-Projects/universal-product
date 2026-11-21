"""EC2-TASK-000146 — Validation Record Registry (EC2-EPIC-010).

The deterministic, append-only store of surfaced :class:`~platform.validation.contracts.\
ValidationRecord` snapshots — the runtime home of validation **surfacing**,
**registration**, **discovery**, and **resolution** (Program §2.1 #9, PC-09), plus an
ordered, append-only **inspection event log** (PC-16 audit / reconstruction). A record's
identity is content-addressed (target + report fingerprint + binding + tick), so
surfacing is idempotent-safe: re-surfacing an identical validation returns the stored
record rather than duplicating it, and a genuinely conflicting record for the same id is
refused (append-only).

The registry holds *records only* — it enforces no authorization (that is the Identity
Layer), no isolation (the reused tenant rule), and it invokes no engine (the façade
does); it is the substrate the console service composes. It mirrors the certified
:mod:`platform.generation.registry` topology exactly and re-derives no validation datum
(TP-01).
"""

from __future__ import annotations

from dataclasses import dataclass
from platform.foundation.contracts import content_hash
from platform.validation.contracts import ValidationRecord
from platform.validation.errors import ValidationRecordError
from platform.validation.metadata import ValidationRecordMetadata
from typing import Any


@dataclass(frozen=True, slots=True)
class InspectionEvent:
    """An immutable, ordered record of a governed inspection over a validation record."""

    sequence: int
    record_id: str
    action: str
    principal_id: str
    tick: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "sequence": self.sequence,
            "record_id": self.record_id,
            "action": self.action,
            "principal_id": self.principal_id,
            "tick": self.tick,
        }


class ValidationRecordRegistry:
    """A deterministic, append-only registry of validation records (surface/resolve/discover)."""

    __slots__ = ("_by_id", "_log")

    def __init__(self) -> None:
        self._by_id: dict[str, ValidationRecord] = {}
        self._log: list[InspectionEvent] = []

    def record(self, record: ValidationRecord) -> ValidationRecord:
        """Register a surfaced record (idempotent by id; fail-closed on a conflict).

        Re-surfacing the identical validation (same content-addressed id) returns the
        stored record. A different record claiming an existing id is refused.
        """
        if not isinstance(record, ValidationRecord):
            raise ValidationRecordError("record requires a ValidationRecord")
        existing = self._by_id.get(record.record_id)
        if existing is not None:
            if existing.fingerprint() == record.fingerprint():
                return existing
            raise ValidationRecordError(
                "a distinct validation record already exists for this id",
                record_id=record.record_id,
            )
        self._by_id[record.record_id] = record
        return record

    def __contains__(self, record_id: str) -> bool:
        return record_id in self._by_id

    def __len__(self) -> int:
        return len(self._by_id)

    def get(self, record_id: str) -> ValidationRecord:
        """Resolve a record by id (fail-closed on absent)."""
        record = self._by_id.get(record_id)
        if record is None:
            raise ValidationRecordError("no such validation record", record_id=record_id)
        return record

    @property
    def ids(self) -> tuple[str, ...]:
        """Every registered record id in stable (sorted) order."""
        return tuple(sorted(self._by_id))

    def all(self) -> tuple[ValidationRecord, ...]:
        """Every registered record in stable (id) order."""
        return tuple(self._by_id[rid] for rid in self.ids)

    def by_target(self, target_id: str) -> tuple[ValidationRecord, ...]:
        """Every record for a given validation target, in stable order."""
        return tuple(r for r in self.all() if r.target_id == target_id)

    def discover(
        self,
        *,
        target_id: str | None = None,
        blueprint_id: str | None = None,
        request_ref: str | None = None,
        workspace_id: str | None = None,
        project_id: str | None = None,
        tenant: str | None = None,
        accepted: bool | None = None,
    ) -> tuple[ValidationRecord, ...]:
        """Discover records, optionally scoped (stable order; pure read view).

        Authorization and isolation are applied by the service. ``tenant`` (when set)
        returns that tenant's records plus every untenanted (global) record (mirrors the
        certified discovery semantics).
        """
        records = self.all()
        if target_id is not None:
            records = tuple(r for r in records if r.target_id == target_id)
        if blueprint_id is not None:
            records = tuple(r for r in records if r.blueprint_id == blueprint_id)
        if request_ref is not None:
            records = tuple(r for r in records if r.request_ref == request_ref)
        if workspace_id is not None:
            records = tuple(r for r in records if r.workspace_id == workspace_id)
        if project_id is not None:
            records = tuple(r for r in records if r.project_id == project_id)
        if tenant is not None:
            records = tuple(r for r in records if r.tenant == tenant or r.tenant is None)
        if accepted is not None:
            records = tuple(r for r in records if r.accepted is accepted)
        return records

    def update_metadata(
        self, record_id: str, metadata: ValidationRecordMetadata
    ) -> ValidationRecord:
        """Replace a record's descriptive metadata immutably (the id is preserved)."""
        record = self.get(record_id)
        updated = record.with_metadata(metadata)
        self._by_id[record_id] = updated
        return updated

    def record_inspection(
        self, record_id: str, action: str, principal_id: str, *, tick: int
    ) -> InspectionEvent:
        """Append an ordered inspection event to the append-only audit log (PC-16)."""
        if record_id not in self._by_id:
            raise ValidationRecordError(
                "cannot record inspection for an unknown record", record_id=record_id
            )
        event = InspectionEvent(
            sequence=len(self._log),
            record_id=record_id,
            action=action,
            principal_id=principal_id,
            tick=tick,
        )
        self._log.append(event)
        return event

    def inspections_of(self, record_id: str) -> tuple[InspectionEvent, ...]:
        """Every recorded inspection for a record, in order (reconstruction, PC-16)."""
        return tuple(e for e in self._log if e.record_id == record_id)

    @property
    def inspections(self) -> tuple[InspectionEvent, ...]:
        """An immutable snapshot of the append-only inspection log (in order)."""
        return tuple(self._log)

    def count_by_verdict(self) -> dict[str, int]:
        """A deterministic accepted/rejected census over the registered records."""
        accepted = sum(1 for r in self._by_id.values() if r.accepted)
        return {
            "total": len(self._by_id),
            "accepted": accepted,
            "rejected": len(self._by_id) - accepted,
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "record_count": len(self._by_id),
            "records": [self._by_id[rid].to_dict() for rid in self.ids],
            "verdict_census": self.count_by_verdict(),
        }

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())


__all__ = ["InspectionEvent", "ValidationRecordRegistry"]
