"""EC2-TASK-000169 — Runtime Operation Ledger & Lineage (EC2-EPIC-012).

The read-only, append-only, **hash-chained** register of governed runtime operations — the
runtime home of Program Surface #11 *Runtime Operations* audit (PC-11 monitor + PC-16
audit). Each :class:`RuntimeOperationLedgerEntry` pins the immutable operation record's
descriptor content hash and links to the previous entry via ``prev_hash``, so the chain is
**tamper-evident**: altering any past entry breaks every subsequent ``entry_hash`` (the
same discipline the certified EC-1 certification ledger and runtime provenance use). It
mirrors the certified :mod:`engine.certification.ledger` topology exactly and re-derives no
operation datum (TP-01).

    * :class:`RuntimeOperationLedgerEntry` — one immutable, hash-chained ledger entry.
    * :class:`RuntimeOperationLedgerView` — an immutable read projection of an entry.
    * :class:`RuntimeOperationLineageView` — the deterministic parent/child/ancestry
      lineage of an operation, derived purely from the tamper-evident chain (dependency
      lineage) plus the operation history of the same runtime unit.
    * :class:`RuntimeOperationLedger` — the append-only ledger façade: appending an
      operation is idempotent by ``operation_id`` (an operation is entered once), the
      chain is verifiable (tamper-evident), and every traversal/lineage query is a pure
      function of the chain (reproducible, P5).

The ledger holds only in-memory entries and **never writes to the certified corpus**
(DP-03); it exposes no update or delete (append-only by construction).
"""

from __future__ import annotations

from dataclasses import dataclass
from platform.foundation.contracts import content_hash
from platform.runtime_operations.contracts import RuntimeOperationRecord
from platform.runtime_operations.errors import (
    RuntimeOperationLedgerError,
    RuntimeOperationLineageError,
)
from typing import Any

#: The genesis predecessor hash for the first ledger entry.
GENESIS_HASH = "0" * 64


@dataclass(frozen=True, slots=True)
class RuntimeOperationLedgerEntry:
    """One immutable, hash-chained entry in the runtime-operation ledger."""

    sequence: int
    operation_id: str
    kind: str
    runtime_id: str
    target_id: str
    environment: str
    descriptor_sha256: str
    prev_hash: str
    entry_hash: str

    @staticmethod
    def compute_hash(
        *,
        sequence: int,
        operation_id: str,
        descriptor_sha256: str,
        prev_hash: str,
    ) -> str:
        """The deterministic entry hash binding this entry to its predecessor."""
        return content_hash(
            {
                "sequence": sequence,
                "operation_id": operation_id,
                "descriptor_sha256": descriptor_sha256,
                "prev_hash": prev_hash,
            }
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "sequence": self.sequence,
            "operation_id": self.operation_id,
            "kind": self.kind,
            "runtime_id": self.runtime_id,
            "target_id": self.target_id,
            "environment": self.environment,
            "descriptor_sha256": self.descriptor_sha256,
            "prev_hash": self.prev_hash,
            "entry_hash": self.entry_hash,
        }


@dataclass(frozen=True, slots=True)
class RuntimeOperationLedgerView:
    """An immutable read projection of a single hash-chained ledger entry."""

    sequence: int
    operation_id: str
    kind: str
    runtime_id: str
    target_id: str
    environment: str
    descriptor_sha256: str
    prev_hash: str
    entry_hash: str

    @classmethod
    def from_entry(cls, entry: RuntimeOperationLedgerEntry) -> RuntimeOperationLedgerView:
        if not isinstance(entry, RuntimeOperationLedgerEntry):
            raise RuntimeOperationLedgerError("RuntimeOperationLedgerView requires a ledger entry")
        return cls(
            sequence=entry.sequence,
            operation_id=entry.operation_id,
            kind=entry.kind,
            runtime_id=entry.runtime_id,
            target_id=entry.target_id,
            environment=entry.environment,
            descriptor_sha256=entry.descriptor_sha256,
            prev_hash=entry.prev_hash,
            entry_hash=entry.entry_hash,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "sequence": self.sequence,
            "operation_id": self.operation_id,
            "kind": self.kind,
            "runtime_id": self.runtime_id,
            "target_id": self.target_id,
            "environment": self.environment,
            "descriptor_sha256": self.descriptor_sha256,
            "prev_hash": self.prev_hash,
            "entry_hash": self.entry_hash,
        }


@dataclass(frozen=True, slots=True)
class RuntimeOperationLineageView:
    """An immutable, content-addressed lineage of an operation (dependency + runtime history)."""

    operation_id: str
    runtime_id: str
    kind: str
    sequence: int
    is_root: bool
    parent: str | None
    child: str | None
    ancestors: tuple[str, ...]
    runtime_ancestors: tuple[str, ...]
    depth: int
    lineage_id: str = ""

    @classmethod
    def create(
        cls,
        *,
        operation_id: str,
        runtime_id: str,
        kind: str,
        sequence: int,
        parent: str | None,
        child: str | None,
        ancestors: tuple[str, ...],
        runtime_ancestors: tuple[str, ...],
    ) -> RuntimeOperationLineageView:
        core = {
            "operation_id": operation_id,
            "runtime_id": runtime_id,
            "kind": kind,
            "sequence": sequence,
            "parent": parent,
            "child": child,
            "ancestors": list(ancestors),
            "runtime_ancestors": list(runtime_ancestors),
        }
        return cls(
            operation_id=operation_id,
            runtime_id=runtime_id,
            kind=kind,
            sequence=sequence,
            is_root=parent is None,
            parent=parent,
            child=child,
            ancestors=ancestors,
            runtime_ancestors=runtime_ancestors,
            depth=len(ancestors),
            lineage_id=f"UCOS-ROLN-{content_hash(core)[:16]}",
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "lineage_id": self.lineage_id,
            "operation_id": self.operation_id,
            "runtime_id": self.runtime_id,
            "kind": self.kind,
            "sequence": self.sequence,
            "is_root": self.is_root,
            "parent": self.parent,
            "child": self.child,
            "ancestors": list(self.ancestors),
            "runtime_ancestors": list(self.runtime_ancestors),
            "depth": self.depth,
        }

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())


class RuntimeOperationLedger:
    """A read-only, append-only, hash-chained runtime-operation ledger with lineage (DP-03 safe)."""

    __slots__ = ("_entries", "_seq_by_op")

    def __init__(self) -> None:
        self._entries: list[RuntimeOperationLedgerEntry] = []
        self._seq_by_op: dict[str, int] = {}

    def append(self, record: RuntimeOperationRecord) -> RuntimeOperationLedgerEntry:
        """Append a governed operation record (idempotent by ``operation_id``; fail-closed).

        Re-appending the same operation returns the stored entry rather than duplicating it.
        """
        if not isinstance(record, RuntimeOperationRecord):
            raise RuntimeOperationLedgerError("append requires a RuntimeOperationRecord")
        existing = self._seq_by_op.get(record.operation_id)
        if existing is not None:
            return self._entries[existing]
        sequence = len(self._entries)
        prev_hash = self.head_hash
        descriptor_sha256 = record.descriptor_fingerprint()
        entry_hash = RuntimeOperationLedgerEntry.compute_hash(
            sequence=sequence,
            operation_id=record.operation_id,
            descriptor_sha256=descriptor_sha256,
            prev_hash=prev_hash,
        )
        entry = RuntimeOperationLedgerEntry(
            sequence=sequence,
            operation_id=record.operation_id,
            kind=record.kind.value,
            runtime_id=record.runtime_id,
            target_id=record.certification.target_id,
            environment=record.environment,
            descriptor_sha256=descriptor_sha256,
            prev_hash=prev_hash,
            entry_hash=entry_hash,
        )
        self._entries.append(entry)
        self._seq_by_op[record.operation_id] = sequence
        return entry

    @property
    def entries(self) -> tuple[RuntimeOperationLedgerEntry, ...]:
        """An immutable snapshot of the ledger entries (append-only order)."""
        return tuple(self._entries)

    @property
    def head_hash(self) -> str:
        """The hash of the latest entry (or the genesis hash when empty)."""
        return self._entries[-1].entry_hash if self._entries else GENESIS_HASH

    def __len__(self) -> int:
        return len(self._entries)

    def __contains__(self, operation_id: str) -> bool:
        return operation_id in self._seq_by_op

    def verify(self) -> bool:
        """True iff the whole hash chain is intact (tamper-evident)."""
        prev = GENESIS_HASH
        for index, entry in enumerate(self._entries):
            if entry.sequence != index or entry.prev_hash != prev:
                return False
            expected = RuntimeOperationLedgerEntry.compute_hash(
                sequence=entry.sequence,
                operation_id=entry.operation_id,
                descriptor_sha256=entry.descriptor_sha256,
                prev_hash=entry.prev_hash,
            )
            if expected != entry.entry_hash:
                return False
            prev = entry.entry_hash
        return True

    def require_intact(self) -> None:
        """Raise :class:`RuntimeOperationLedgerError` if the hash chain is broken."""
        if not self.verify():
            raise RuntimeOperationLedgerError(
                "runtime operation ledger hash chain is broken (tamper detected)",
                entries=len(self._entries),
            )

    def get(self, operation_id: str) -> RuntimeOperationLedgerEntry:
        """Resolve a ledger entry by operation id (fail-closed on absent)."""
        sequence = self._seq_by_op.get(operation_id)
        if sequence is None:
            raise RuntimeOperationLedgerError(
                "no such operation in the ledger", operation_id=operation_id
            )
        return self._entries[sequence]

    def view(self, operation_id: str) -> RuntimeOperationLedgerView:
        """Return the read projection of a ledger entry (fail-closed on absent)."""
        return RuntimeOperationLedgerView.from_entry(self.get(operation_id))

    def views(self) -> tuple[RuntimeOperationLedgerView, ...]:
        """Every ledger entry as a read projection, in append-only order."""
        return tuple(RuntimeOperationLedgerView.from_entry(e) for e in self._entries)

    def by_runtime(self, runtime_id: str) -> tuple[RuntimeOperationLedgerView, ...]:
        """Every ledger entry for a runtime unit, in append-only order (operation history)."""
        return tuple(
            RuntimeOperationLedgerView.from_entry(e)
            for e in self._entries
            if e.runtime_id == runtime_id
        )

    def _lineage_entry(self, operation_id: str) -> RuntimeOperationLedgerEntry:
        """Resolve an entry for a lineage query (fail-closed with a lineage error)."""
        sequence = self._seq_by_op.get(operation_id)
        if sequence is None:
            raise RuntimeOperationLineageError(
                "no lineage for an absent operation", operation_id=operation_id
            )
        return self._entries[sequence]

    def ancestry(self, operation_id: str) -> tuple[RuntimeOperationLedgerEntry, ...]:
        """The chain of hash-chain predecessors of an operation, genesis-first."""
        entry = self._lineage_entry(operation_id)
        return tuple(self._entries[: entry.sequence])

    def lineage(self, operation_id: str) -> RuntimeOperationLineageView:
        """Return the deterministic parent/child/ancestry lineage of an operation."""
        entry = self._lineage_entry(operation_id)
        entries = self._entries
        parent = entries[entry.sequence - 1].operation_id if entry.sequence > 0 else None
        child = (
            entries[entry.sequence + 1].operation_id if entry.sequence + 1 < len(entries) else None
        )
        ancestors = tuple(e.operation_id for e in entries[: entry.sequence])
        runtime_ancestors = tuple(
            e.operation_id for e in entries[: entry.sequence] if e.runtime_id == entry.runtime_id
        )
        return RuntimeOperationLineageView.create(
            operation_id=entry.operation_id,
            runtime_id=entry.runtime_id,
            kind=entry.kind,
            sequence=entry.sequence,
            parent=parent,
            child=child,
            ancestors=ancestors,
            runtime_ancestors=runtime_ancestors,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "ledger_format": "ucos-runtime-operation-ledger/1.0.0",
            "count": len(self._entries),
            "head_hash": self.head_hash,
            "intact": self.verify(),
            "entries": [v.to_dict() for v in self.views()],
        }

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())


__all__ = [
    "GENESIS_HASH",
    "RuntimeOperationLedgerEntry",
    "RuntimeOperationLedgerView",
    "RuntimeOperationLineageView",
    "RuntimeOperationLedger",
]
