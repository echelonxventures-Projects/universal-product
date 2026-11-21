"""UCOS-EPIC-006 — Certification Audit (Terminal T6).

The **Certification Audit Ledger** is an append-only, hash-chained register of every
material certification and approval event (MIP Part 14 — audit is append-only and
tamper-evident). Each :class:`AuditEntry` pins the certificate content hash and links
to its predecessor via ``prev_hash``, so the chain is **tamper-evident**: altering any
past entry breaks every subsequent ``entry_hash``.

The ledger is *append-only* — it exposes no update or delete — and *deterministic*:
recording the same sequence of events from the same genesis yields an identical chain
of entry hashes (IMP-007 §5). It holds only in-memory entries and **never writes to
the certified corpus** (DP-03); persistence, if any, is the caller's concern via
:meth:`to_dict`.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from engine.foundation.obs.logging import get_logger
from engine.universal_certification.contracts import content_hash
from engine.universal_certification.errors import AuditIntegrityError

_logger = get_logger("universal_certification.audit")

#: The genesis predecessor hash for the first audit entry.
GENESIS_HASH = "0" * 64


class AuditEventType(str, Enum):
    """The material certification/approval events an audit ledger records."""

    CERTIFIED = "certified"
    NOT_CERTIFIED = "not-certified"
    CERTIFICATE_ISSUED = "certificate-issued"
    EVIDENCE_RECORDED = "evidence-recorded"
    APPROVAL_SUBMITTED = "approval-submitted"
    APPROVED = "approved"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"


@dataclass(frozen=True, slots=True)
class AuditEntry:
    """One immutable, hash-chained entry in the certification audit ledger."""

    sequence: int
    event_type: AuditEventType
    certification_id: str
    certificate_sha256: str
    detail: dict[str, Any]
    prev_hash: str
    entry_hash: str

    @staticmethod
    def compute_hash(
        *,
        sequence: int,
        event_type: AuditEventType,
        certification_id: str,
        certificate_sha256: str,
        detail: dict[str, Any],
        prev_hash: str,
    ) -> str:
        """The deterministic entry hash binding this entry to its predecessor."""
        return content_hash(
            {
                "sequence": sequence,
                "event_type": event_type.value,
                "certification_id": certification_id,
                "certificate_sha256": certificate_sha256,
                "detail": detail,
                "prev_hash": prev_hash,
            }
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "sequence": self.sequence,
            "event_type": self.event_type.value,
            "certification_id": self.certification_id,
            "certificate_sha256": self.certificate_sha256,
            "detail": dict(self.detail),
            "prev_hash": self.prev_hash,
            "entry_hash": self.entry_hash,
        }


class CertificationAuditLedger:
    """An append-only, hash-chained, in-memory certification audit ledger (DP-03 safe)."""

    __slots__ = ("_entries",)

    def __init__(self) -> None:
        self._entries: list[AuditEntry] = []

    @property
    def entries(self) -> tuple[AuditEntry, ...]:
        """An immutable snapshot of the ledger (append-only; never mutated in place)."""
        return tuple(self._entries)

    @property
    def head_hash(self) -> str:
        """The hash of the latest entry (or the genesis hash when empty)."""
        return self._entries[-1].entry_hash if self._entries else GENESIS_HASH

    def __len__(self) -> int:
        return len(self._entries)

    def record(
        self,
        event_type: AuditEventType,
        *,
        certification_id: str,
        certificate_sha256: str,
        **detail: Any,
    ) -> AuditEntry:
        """Append an audit event and return its immutable, hash-chained entry."""
        if not isinstance(event_type, AuditEventType):
            raise AuditIntegrityError("audit event_type must be an AuditEventType")
        sequence = len(self._entries)
        prev_hash = self.head_hash
        detail_map = dict(detail)
        entry_hash = AuditEntry.compute_hash(
            sequence=sequence,
            event_type=event_type,
            certification_id=certification_id,
            certificate_sha256=certificate_sha256,
            detail=detail_map,
            prev_hash=prev_hash,
        )
        entry = AuditEntry(
            sequence=sequence,
            event_type=event_type,
            certification_id=certification_id,
            certificate_sha256=certificate_sha256,
            detail=detail_map,
            prev_hash=prev_hash,
            entry_hash=entry_hash,
        )
        self._entries.append(entry)
        _logger.info(
            "universal_certification.audit.recorded",
            sequence=sequence,
            event_type=event_type.value,
            certification_id=certification_id,
        )
        return entry

    def events_for(self, certification_id: str) -> tuple[AuditEntry, ...]:
        """Every audit entry for one certification, in append order."""
        return tuple(e for e in self._entries if e.certification_id == certification_id)

    def verify(self) -> bool:
        """Return True iff the whole hash chain is intact (tamper-evident)."""
        prev = GENESIS_HASH
        for index, entry in enumerate(self._entries):
            if entry.sequence != index or entry.prev_hash != prev:
                return False
            expected = AuditEntry.compute_hash(
                sequence=entry.sequence,
                event_type=entry.event_type,
                certification_id=entry.certification_id,
                certificate_sha256=entry.certificate_sha256,
                detail=entry.detail,
                prev_hash=entry.prev_hash,
            )
            if expected != entry.entry_hash:
                return False
            prev = entry.entry_hash
        return True

    def require_intact(self) -> None:
        """Raise :class:`AuditIntegrityError` if the hash chain is broken."""
        if not self.verify():
            raise AuditIntegrityError(
                "certification audit hash chain is broken (tamper detected)",
                entries=len(self._entries),
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "ledger_format": "ucos-universal-certification-audit/1.0.0",
            "count": len(self._entries),
            "head_hash": self.head_hash,
            "entries": [e.to_dict() for e in self._entries],
        }


__all__ = [
    "GENESIS_HASH",
    "AuditEventType",
    "AuditEntry",
    "CertificationAuditLedger",
]
