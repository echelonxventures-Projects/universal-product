"""EC2-TASK-000156 — Certification Console Ledger & Lineage (EC2-EPIC-011).

The console-side, read-only **certification ledger** — the runtime home of Program
Surface #10 *Certification Ledger* (PC-10 ledger navigation). It wraps the certified,
append-only, hash-chained :class:`~engine.certification.ledger.CertificationLedger`
(consumed **by reference**, never re-implemented — TP-01) and exposes deterministic
**ledger access**, **traversal**, and **lineage** navigation over it:

    * :class:`CertificationLedgerView` — an immutable projection of one hash-chained
      ledger entry.
    * :class:`CertificationLineageView` — the deterministic parent/child/ancestry lineage
      of a certification, derived purely from the tamper-evident hash chain (dependency
      lineage) plus the re-certification history of the same target.
    * :class:`CertificationConsoleLedger` — the append-only ledger façade: appending a
      certified record is idempotent by ``certification_id`` (a certification is entered
      once), the chain is verifiable (tamper-evident), and every traversal/lineage query
      is a pure function of the chain (reproducible, P5).

The ledger holds only in-memory entries and **never writes to the certified corpus**
(DP-03); it exposes no update or delete (append-only by construction).
"""

from __future__ import annotations

from dataclasses import dataclass
from platform.certification.errors import CertificationLedgerError, CertificationLineageError
from platform.foundation.contracts import content_hash
from typing import Any

from engine.certification.contracts import CertificationRecord
from engine.certification.ledger import CertificationLedger, CertificationLedgerEntry


@dataclass(frozen=True, slots=True)
class CertificationLedgerView:
    """An immutable read projection of a single hash-chained ledger entry."""

    sequence: int
    certification_id: str
    target_id: str
    blueprint_id: str
    version: str
    status: str
    record_sha256: str
    prev_hash: str
    entry_hash: str

    @classmethod
    def from_entry(cls, entry: CertificationLedgerEntry) -> CertificationLedgerView:
        if not isinstance(entry, CertificationLedgerEntry):
            raise CertificationLedgerError("CertificationLedgerView requires a ledger entry")
        return cls(
            sequence=entry.sequence,
            certification_id=entry.certification_id,
            target_id=entry.target_id,
            blueprint_id=entry.blueprint_id,
            version=entry.version,
            status=entry.status,
            record_sha256=entry.record_sha256,
            prev_hash=entry.prev_hash,
            entry_hash=entry.entry_hash,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "sequence": self.sequence,
            "certification_id": self.certification_id,
            "target_id": self.target_id,
            "blueprint_id": self.blueprint_id,
            "version": self.version,
            "status": self.status,
            "record_sha256": self.record_sha256,
            "prev_hash": self.prev_hash,
            "entry_hash": self.entry_hash,
        }


@dataclass(frozen=True, slots=True)
class CertificationLineageView:
    """An immutable, content-addressed lineage of a certification (dependency + ancestry).

    Derived purely from the tamper-evident hash chain: ``parent``/``child`` are the
    immediate hash-chain predecessor/successor certifications, ``ancestors`` is the full
    chain of predecessors back to genesis (dependency lineage), and ``target_ancestors``
    is the re-certification history of the same target (prior certifications of the same
    ``target_id``). All fields are explicit citations; nothing is synthesized.
    """

    certification_id: str
    target_id: str
    blueprint_id: str
    sequence: int
    is_root: bool
    parent: str | None
    child: str | None
    ancestors: tuple[str, ...]
    target_ancestors: tuple[str, ...]
    depth: int
    lineage_id: str = ""

    @classmethod
    def create(
        cls,
        *,
        certification_id: str,
        target_id: str,
        blueprint_id: str,
        sequence: int,
        parent: str | None,
        child: str | None,
        ancestors: tuple[str, ...],
        target_ancestors: tuple[str, ...],
    ) -> CertificationLineageView:
        core = {
            "certification_id": certification_id,
            "target_id": target_id,
            "blueprint_id": blueprint_id,
            "sequence": sequence,
            "parent": parent,
            "child": child,
            "ancestors": list(ancestors),
            "target_ancestors": list(target_ancestors),
        }
        return cls(
            certification_id=certification_id,
            target_id=target_id,
            blueprint_id=blueprint_id,
            sequence=sequence,
            is_root=parent is None,
            parent=parent,
            child=child,
            ancestors=ancestors,
            target_ancestors=target_ancestors,
            depth=len(ancestors),
            lineage_id=f"UCOS-CLIN-{content_hash(core)[:16]}",
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "lineage_id": self.lineage_id,
            "certification_id": self.certification_id,
            "target_id": self.target_id,
            "blueprint_id": self.blueprint_id,
            "sequence": self.sequence,
            "is_root": self.is_root,
            "parent": self.parent,
            "child": self.child,
            "ancestors": list(self.ancestors),
            "target_ancestors": list(self.target_ancestors),
            "depth": self.depth,
        }

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())


class CertificationConsoleLedger:
    """A read-only, append-only, hash-chained certification ledger with lineage (DP-03 safe)."""

    __slots__ = ("_ledger", "_seq_by_cert")

    def __init__(self, ledger: CertificationLedger | None = None) -> None:
        if ledger is not None and not isinstance(ledger, CertificationLedger):
            raise CertificationLedgerError(
                "CertificationConsoleLedger requires an engine CertificationLedger"
            )
        self._ledger = ledger if ledger is not None else CertificationLedger()
        self._seq_by_cert: dict[str, int] = {
            entry.certification_id: entry.sequence for entry in self._ledger.entries
        }

    def append(self, record: CertificationRecord) -> CertificationLedgerEntry:
        """Append a certified record (idempotent by ``certification_id``; fail-closed).

        Re-appending the same certification returns the stored entry rather than
        duplicating it. A tampered record (failing its own integrity check) is refused by
        the certified engine ledger.
        """
        if not isinstance(record, CertificationRecord):
            raise CertificationLedgerError("append requires a CertificationRecord")
        existing = self._seq_by_cert.get(record.certification_id)
        if existing is not None:
            return self._ledger.entries[existing]
        entry = self._ledger.append(record)
        self._seq_by_cert[record.certification_id] = entry.sequence
        return entry

    @property
    def entries(self) -> tuple[CertificationLedgerEntry, ...]:
        """An immutable snapshot of the ledger entries (append-only order)."""
        return self._ledger.entries

    @property
    def head_hash(self) -> str:
        """The hash of the latest entry (or the genesis hash when empty)."""
        return self._ledger.head_hash

    def __len__(self) -> int:
        return len(self._ledger)

    def __contains__(self, certification_id: str) -> bool:
        return certification_id in self._seq_by_cert

    def verify(self) -> bool:
        """True iff the whole hash chain is intact (tamper-evident)."""
        return self._ledger.verify()

    def require_intact(self) -> None:
        """Raise if the hash chain is broken (delegates to the certified ledger)."""
        self._ledger.require_intact()

    def get(self, certification_id: str) -> CertificationLedgerEntry:
        """Resolve a ledger entry by certification id (fail-closed on absent)."""
        sequence = self._seq_by_cert.get(certification_id)
        if sequence is None:
            raise CertificationLedgerError(
                "no such certification in the ledger", certification_id=certification_id
            )
        return self._ledger.entries[sequence]

    def view(self, certification_id: str) -> CertificationLedgerView:
        """Return the read projection of a ledger entry (fail-closed on absent)."""
        return CertificationLedgerView.from_entry(self.get(certification_id))

    def views(self) -> tuple[CertificationLedgerView, ...]:
        """Every ledger entry as a read projection, in append-only order."""
        return tuple(CertificationLedgerView.from_entry(e) for e in self._ledger.entries)

    def by_target(self, target_id: str) -> tuple[CertificationLedgerView, ...]:
        """Every ledger entry for a target, in append-only order (re-certification history)."""
        return tuple(
            CertificationLedgerView.from_entry(e)
            for e in self._ledger.entries
            if e.target_id == target_id
        )

    def by_blueprint(self, blueprint_id: str) -> tuple[CertificationLedgerView, ...]:
        """Every ledger entry for a blueprint, in append-only order."""
        return tuple(
            CertificationLedgerView.from_entry(e)
            for e in self._ledger.entries
            if e.blueprint_id == blueprint_id
        )

    def _lineage_entry(self, certification_id: str) -> CertificationLedgerEntry:
        """Resolve an entry for a lineage query (fail-closed with a lineage error)."""
        sequence = self._seq_by_cert.get(certification_id)
        if sequence is None:
            raise CertificationLineageError(
                "no lineage for an absent certification", certification_id=certification_id
            )
        return self._ledger.entries[sequence]

    def ancestry(self, certification_id: str) -> tuple[CertificationLedgerEntry, ...]:
        """The chain of hash-chain predecessors of a certification, genesis-first."""
        entry = self._lineage_entry(certification_id)
        return tuple(self._ledger.entries[: entry.sequence])

    def lineage(self, certification_id: str) -> CertificationLineageView:
        """Return the deterministic parent/child/ancestry lineage of a certification."""
        entry = self._lineage_entry(certification_id)
        entries = self._ledger.entries
        parent = entries[entry.sequence - 1].certification_id if entry.sequence > 0 else None
        child = (
            entries[entry.sequence + 1].certification_id
            if entry.sequence + 1 < len(entries)
            else None
        )
        ancestors = tuple(e.certification_id for e in entries[: entry.sequence])
        target_ancestors = tuple(
            e.certification_id for e in entries[: entry.sequence] if e.target_id == entry.target_id
        )
        return CertificationLineageView.create(
            certification_id=entry.certification_id,
            target_id=entry.target_id,
            blueprint_id=entry.blueprint_id,
            sequence=entry.sequence,
            parent=parent,
            child=child,
            ancestors=ancestors,
            target_ancestors=target_ancestors,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "ledger_format": "ucos-certification-console-ledger/1.0.0",
            "count": len(self._ledger),
            "head_hash": self.head_hash,
            "intact": self.verify(),
            "entries": [v.to_dict() for v in self.views()],
        }

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())


__all__ = [
    "CertificationLedgerView",
    "CertificationLineageView",
    "CertificationConsoleLedger",
]
