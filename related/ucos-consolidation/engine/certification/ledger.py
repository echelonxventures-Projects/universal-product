"""TASK-000053 — Certification Ledger Entry (EPIC-008).

The **Certification Ledger** is an append-only, hash-chained register of
certification records. Each :class:`CertificationLedgerEntry` pins the immutable
record's content hash and links to the previous entry via ``prev_hash``, so the
chain is **tamper-evident**: altering any past entry breaks every subsequent
``entry_hash`` (the same discipline the runtime uses for provenance).

The ledger is *append-only* — it exposes no update or delete — and *deterministic*:
appending the same sequence of records from the same genesis yields an identical
chain of entry hashes (IMP-007 §5). It holds only in-memory records and **never
writes to the certified corpus** (DP-03); persistence, if any, is the caller's
concern via :meth:`to_dict`.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from engine.certification.contracts import CertificationRecord, content_hash
from engine.certification.errors import LedgerIntegrityError
from engine.foundation.obs.logging import get_logger

_logger = get_logger("certification.ledger")

#: The genesis predecessor hash for the first ledger entry.
GENESIS_HASH = "0" * 64


@dataclass(frozen=True, slots=True)
class CertificationLedgerEntry:
    """One immutable, hash-chained entry in the certification ledger."""

    sequence: int
    certification_id: str
    target_id: str
    blueprint_id: str
    version: str
    status: str
    record_sha256: str
    prev_hash: str
    entry_hash: str

    @staticmethod
    def compute_hash(
        *,
        sequence: int,
        certification_id: str,
        record_sha256: str,
        prev_hash: str,
    ) -> str:
        """The deterministic entry hash binding this entry to its predecessor."""
        return content_hash(
            {
                "sequence": sequence,
                "certification_id": certification_id,
                "record_sha256": record_sha256,
                "prev_hash": prev_hash,
            }
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


class CertificationLedger:
    """An append-only, hash-chained, in-memory certification ledger (DP-03 safe)."""

    __slots__ = ("_entries",)

    def __init__(self) -> None:
        self._entries: list[CertificationLedgerEntry] = []

    @property
    def entries(self) -> tuple[CertificationLedgerEntry, ...]:
        """An immutable snapshot of the ledger (append-only; never mutated in place)."""
        return tuple(self._entries)

    @property
    def head_hash(self) -> str:
        """The hash of the latest entry (or the genesis hash when empty)."""
        return self._entries[-1].entry_hash if self._entries else GENESIS_HASH

    def __len__(self) -> int:
        return len(self._entries)

    def append(self, record: CertificationRecord) -> CertificationLedgerEntry:
        """Append an immutable certification record and return its ledger entry.

        Raises:
            LedgerIntegrityError: if the record fails its own content-hash integrity
                check (a tampered record is never admitted to the ledger).
        """
        record.require_integrity()
        sequence = len(self._entries)
        prev_hash = self.head_hash
        entry_hash = CertificationLedgerEntry.compute_hash(
            sequence=sequence,
            certification_id=record.certification_id,
            record_sha256=record.content_sha256,
            prev_hash=prev_hash,
        )
        entry = CertificationLedgerEntry(
            sequence=sequence,
            certification_id=record.certification_id,
            target_id=record.target_id,
            blueprint_id=record.blueprint_id,
            version=record.version,
            status=record.status.value,
            record_sha256=record.content_sha256,
            prev_hash=prev_hash,
            entry_hash=entry_hash,
        )
        self._entries.append(entry)
        _logger.info(
            "certification.ledger.appended",
            sequence=sequence,
            certification_id=record.certification_id,
            status=record.status.value,
        )
        return entry

    def verify(self) -> bool:
        """Return True iff the whole hash chain is intact (tamper-evident)."""
        prev = GENESIS_HASH
        for index, entry in enumerate(self._entries):
            if entry.sequence != index or entry.prev_hash != prev:
                return False
            expected = CertificationLedgerEntry.compute_hash(
                sequence=entry.sequence,
                certification_id=entry.certification_id,
                record_sha256=entry.record_sha256,
                prev_hash=entry.prev_hash,
            )
            if expected != entry.entry_hash:
                return False
            prev = entry.entry_hash
        return True

    def require_intact(self) -> None:
        """Raise :class:`LedgerIntegrityError` if the hash chain is broken."""
        if not self.verify():
            raise LedgerIntegrityError(
                "certification ledger hash chain is broken (tamper detected)",
                entries=len(self._entries),
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "ledger_format": "ucos-certification-ledger/1.0.0",
            "count": len(self._entries),
            "head_hash": self.head_hash,
            "entries": [e.to_dict() for e in self._entries],
        }


__all__ = ["GENESIS_HASH", "CertificationLedgerEntry", "CertificationLedger"]
