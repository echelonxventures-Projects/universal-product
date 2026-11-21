"""EPIC-007 (Terminal T7) — Execution Registry (Universal Runtime Platform).

The **Execution Registry** — realizing ``PRS-022`` Element Registration for governed
executions (Registry-First, PEP-001). It is a read-only, append-only, **hash-chained**
register of :class:`~platform.runtime_platform.execution.ExecutionRecord` outcomes: each
:class:`ExecutionLedgerEntry` pins the immutable record's content hash and links to the
previous entry via ``prev_hash``, so the chain is **tamper-evident** — altering any past
entry breaks every subsequent ``entry_hash`` (the discipline the certified EC-1
certification ledger and the runtime-operations ledger use).

Appending is idempotent by ``execution_id`` (an execution is entered once), the chain is
verifiable, and every traversal / lineage query is a pure function of the chain
(reproducible). It holds only in-memory entries, exposes no update or delete, and never
writes to the certified corpus (DP-03).
"""

from __future__ import annotations

from dataclasses import dataclass
from platform.foundation.contracts import content_hash
from platform.runtime_platform.errors import ExecutionRegistryError
from platform.runtime_platform.execution import ExecutionRecord
from typing import Any

#: The recorded registry format.
EXECUTION_REGISTRY_FORMAT = "ucos-runtime-execution-registry/1.0.0"

#: The genesis predecessor hash for the first ledger entry.
GENESIS_HASH = "0" * 64


@dataclass(frozen=True, slots=True)
class ExecutionLedgerEntry:
    """One immutable, hash-chained entry in the execution registry."""

    sequence: int
    execution_id: str
    workload_id: str
    final_state: str
    workflow_id: str | None
    record_sha256: str
    prev_hash: str
    entry_hash: str

    @staticmethod
    def compute_hash(
        *, sequence: int, execution_id: str, record_sha256: str, prev_hash: str
    ) -> str:
        """The deterministic entry hash binding this entry to its predecessor."""
        return content_hash(
            {
                "sequence": sequence,
                "execution_id": execution_id,
                "record_sha256": record_sha256,
                "prev_hash": prev_hash,
            }
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "sequence": self.sequence,
            "execution_id": self.execution_id,
            "workload_id": self.workload_id,
            "final_state": self.final_state,
            "workflow_id": self.workflow_id,
            "record_sha256": self.record_sha256,
            "prev_hash": self.prev_hash,
            "entry_hash": self.entry_hash,
        }


@dataclass(frozen=True, slots=True)
class ExecutionLineageView:
    """An immutable, content-addressed lineage of an execution (chain + workflow siblings)."""

    execution_id: str
    workload_id: str
    workflow_id: str | None
    sequence: int
    is_root: bool
    parent: str | None
    child: str | None
    ancestors: tuple[str, ...]
    workflow_siblings: tuple[str, ...]
    depth: int
    lineage_id: str = ""

    @classmethod
    def create(
        cls,
        *,
        execution_id: str,
        workload_id: str,
        workflow_id: str | None,
        sequence: int,
        parent: str | None,
        child: str | None,
        ancestors: tuple[str, ...],
        workflow_siblings: tuple[str, ...],
    ) -> ExecutionLineageView:
        core = {
            "execution_id": execution_id,
            "workload_id": workload_id,
            "workflow_id": workflow_id,
            "sequence": sequence,
            "parent": parent,
            "child": child,
            "ancestors": list(ancestors),
            "workflow_siblings": list(workflow_siblings),
        }
        return cls(
            execution_id=execution_id,
            workload_id=workload_id,
            workflow_id=workflow_id,
            sequence=sequence,
            is_root=parent is None,
            parent=parent,
            child=child,
            ancestors=ancestors,
            workflow_siblings=workflow_siblings,
            depth=len(ancestors),
            lineage_id=f"UCOS-URPL-{content_hash(core)[:16]}",
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "lineage_id": self.lineage_id,
            "execution_id": self.execution_id,
            "workload_id": self.workload_id,
            "workflow_id": self.workflow_id,
            "sequence": self.sequence,
            "is_root": self.is_root,
            "parent": self.parent,
            "child": self.child,
            "ancestors": list(self.ancestors),
            "workflow_siblings": list(self.workflow_siblings),
            "depth": self.depth,
        }

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())


class ExecutionRegistry:
    """A read-only, append-only, hash-chained registry of executions with lineage (DP-03 safe)."""

    __slots__ = ("_entries", "_records", "_seq_by_id")

    def __init__(self) -> None:
        self._entries: list[ExecutionLedgerEntry] = []
        self._records: dict[str, ExecutionRecord] = {}
        self._seq_by_id: dict[str, int] = {}

    def register(self, record: ExecutionRecord) -> ExecutionLedgerEntry:
        """Append an execution record (idempotent by ``execution_id``; fail-closed).

        Re-registering the same execution returns the stored entry rather than duplicating.
        """
        if not isinstance(record, ExecutionRecord):
            raise ExecutionRegistryError("register requires an ExecutionRecord")
        existing = self._seq_by_id.get(record.execution_id)
        if existing is not None:
            return self._entries[existing]
        sequence = len(self._entries)
        prev_hash = self.head_hash
        record_sha256 = record.fingerprint()
        entry_hash = ExecutionLedgerEntry.compute_hash(
            sequence=sequence,
            execution_id=record.execution_id,
            record_sha256=record_sha256,
            prev_hash=prev_hash,
        )
        entry = ExecutionLedgerEntry(
            sequence=sequence,
            execution_id=record.execution_id,
            workload_id=record.workload_id,
            final_state=record.final_state,
            workflow_id=record.workflow_id,
            record_sha256=record_sha256,
            prev_hash=prev_hash,
            entry_hash=entry_hash,
        )
        self._entries.append(entry)
        self._records[record.execution_id] = record
        self._seq_by_id[record.execution_id] = sequence
        return entry

    @property
    def entries(self) -> tuple[ExecutionLedgerEntry, ...]:
        """An immutable snapshot of the ledger entries (append-only order)."""
        return tuple(self._entries)

    @property
    def head_hash(self) -> str:
        """The hash of the latest entry (or the genesis hash when empty)."""
        return self._entries[-1].entry_hash if self._entries else GENESIS_HASH

    def __len__(self) -> int:
        return len(self._entries)

    def __contains__(self, execution_id: str) -> bool:
        return execution_id in self._seq_by_id

    def get(self, execution_id: str) -> ExecutionRecord:
        """Resolve a recorded execution by id (fail-closed on absent)."""
        record = self._records.get(execution_id)
        if record is None:
            raise ExecutionRegistryError("no such execution", execution_id=execution_id)
        return record

    def entry(self, execution_id: str) -> ExecutionLedgerEntry:
        """Resolve the hash-chained ledger entry for an execution (fail-closed on absent)."""
        sequence = self._seq_by_id.get(execution_id)
        if sequence is None:
            raise ExecutionRegistryError("no such execution", execution_id=execution_id)
        return self._entries[sequence]

    def records(self) -> tuple[ExecutionRecord, ...]:
        """Every recorded execution in append-only order."""
        return tuple(self._records[e.execution_id] for e in self._entries)

    def by_workflow(self, workflow_id: str) -> tuple[ExecutionRecord, ...]:
        """Every recorded execution belonging to a workflow, in append-only order."""
        return tuple(
            self._records[e.execution_id] for e in self._entries if e.workflow_id == workflow_id
        )

    def by_state(self, final_state: str) -> tuple[ExecutionRecord, ...]:
        """Every recorded execution with a given final state, in append-only order."""
        return tuple(
            self._records[e.execution_id] for e in self._entries if e.final_state == final_state
        )

    def verify(self) -> bool:
        """True iff the whole hash chain is intact (tamper-evident)."""
        prev = GENESIS_HASH
        for index, entry in enumerate(self._entries):
            if entry.sequence != index or entry.prev_hash != prev:
                return False
            expected = ExecutionLedgerEntry.compute_hash(
                sequence=entry.sequence,
                execution_id=entry.execution_id,
                record_sha256=entry.record_sha256,
                prev_hash=entry.prev_hash,
            )
            if expected != entry.entry_hash:
                return False
            prev = entry.entry_hash
        return True

    def require_intact(self) -> None:
        """Raise :class:`ExecutionRegistryError` if the hash chain is broken."""
        if not self.verify():
            raise ExecutionRegistryError(
                "execution registry hash chain is broken (tamper detected)",
                entries=len(self._entries),
            )

    def lineage(self, execution_id: str) -> ExecutionLineageView:
        """Return the deterministic parent/child/ancestry lineage of an execution."""
        sequence = self._seq_by_id.get(execution_id)
        if sequence is None:
            raise ExecutionRegistryError(
                "no lineage for an absent execution", execution_id=execution_id
            )
        entry = self._entries[sequence]
        entries = self._entries
        parent = entries[sequence - 1].execution_id if sequence > 0 else None
        child = entries[sequence + 1].execution_id if sequence + 1 < len(entries) else None
        ancestors = tuple(e.execution_id for e in entries[:sequence])
        workflow_siblings = (
            tuple(
                e.execution_id
                for e in entries
                if e.workflow_id == entry.workflow_id and e.execution_id != execution_id
            )
            if entry.workflow_id is not None
            else ()
        )
        return ExecutionLineageView.create(
            execution_id=entry.execution_id,
            workload_id=entry.workload_id,
            workflow_id=entry.workflow_id,
            sequence=entry.sequence,
            parent=parent,
            child=child,
            ancestors=ancestors,
            workflow_siblings=workflow_siblings,
        )

    def census(self) -> dict[str, int]:
        """A deterministic count of executions by final state (plus a total)."""
        counts: dict[str, int] = {}
        for entry in self._entries:
            counts[entry.final_state] = counts.get(entry.final_state, 0) + 1
        counts["total"] = len(self._entries)
        return counts

    def to_dict(self) -> dict[str, Any]:
        return {
            "execution_registry_format": EXECUTION_REGISTRY_FORMAT,
            "count": len(self._entries),
            "head_hash": self.head_hash,
            "intact": self.verify(),
            "entries": [entry.to_dict() for entry in self._entries],
        }

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())


__all__ = [
    "EXECUTION_REGISTRY_FORMAT",
    "GENESIS_HASH",
    "ExecutionLedgerEntry",
    "ExecutionLineageView",
    "ExecutionRegistry",
]
