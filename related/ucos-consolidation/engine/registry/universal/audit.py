"""UCOS-EPIC-001 — Append-only, hash-chained audit trail.

Every registration act is recorded on an append-only journal (Requirement:
*Audit trail*; INV-10 append-only discipline). Each :class:`AuditEntry` chains
over the previous entry's hash, making the journal **tamper-evident**: a
retroactive edit, deletion, or reordering breaks :meth:`AuditJournal.verify`.

The journal is deterministic in structure (sequence + hash chain). The wall-clock
is injected via a :class:`Clock` so production records carry real timestamps while
tests remain fully deterministic (RC-4). Persistence is plain, canonical JSON
(stdlib-only); it never writes to the frozen corpus.
"""

from __future__ import annotations

import json
from collections.abc import Callable, Iterable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from engine.registry.universal.errors import AuditIntegrityError
from engine.registry.universal.identity import canonical_json
from engine.registry.universal.records import AuditAct, AuditEntry

#: The genesis predecessor hash (no prior entry).
GENESIS_HASH = "0" * 64

#: A clock returns an ISO-8601 timestamp string for an audit entry.
Clock = Callable[[], str]


def utc_clock() -> str:
    """Default clock: the current UTC time in ISO-8601 form."""
    return datetime.now(UTC).isoformat()


class SequenceClock:
    """A deterministic clock yielding monotonic epoch-anchored timestamps.

    Useful for reproducible evidence: each call advances one second from a fixed
    origin, so audit timestamps are stable across runs without a wall-clock.
    """

    __slots__ = ("_tick",)

    def __init__(self) -> None:
        self._tick = 0

    def __call__(self) -> str:
        stamp = datetime.fromtimestamp(self._tick, UTC).isoformat()
        self._tick += 1
        return stamp


class AuditJournal:
    """An append-only, hash-chained ledger of registration acts."""

    __slots__ = ("_entries", "_clock")

    def __init__(self, *, clock: Clock | None = None) -> None:
        self._entries: list[AuditEntry] = []
        self._clock: Clock = clock if clock is not None else utc_clock

    # -- append ----------------------------------------------------------------

    def record(
        self,
        *,
        act: AuditAct,
        universal_id: str,
        version: str,
        content_hash: str,
        state: str,
        actor: str,
    ) -> AuditEntry:
        """Append a sealed audit entry chained to the current tail."""
        prev = self._entries[-1].entry_hash if self._entries else GENESIS_HASH
        entry = AuditEntry(
            sequence=len(self._entries),
            act=act,
            universal_id=universal_id,
            version=version,
            content_hash=content_hash,
            state=state,
            actor=actor,
            timestamp=self._clock(),
            prev_hash=prev,
        ).sealed()
        self._entries.append(entry)
        return entry

    # -- read ------------------------------------------------------------------

    def __len__(self) -> int:
        return len(self._entries)

    def __iter__(self):
        return iter(self._entries)

    def entries(self) -> tuple[AuditEntry, ...]:
        """Every audit entry in append order (immutable tuple)."""
        return tuple(self._entries)

    def for_id(self, universal_id: str) -> tuple[AuditEntry, ...]:
        """Every audit entry touching ``universal_id`` in append order."""
        return tuple(e for e in self._entries if e.universal_id == universal_id)

    def head_hash(self) -> str:
        """The tail (most recent) chain hash, or the genesis hash if empty."""
        return self._entries[-1].entry_hash if self._entries else GENESIS_HASH

    # -- integrity -------------------------------------------------------------

    def verify(self) -> bool:
        """Verify the full hash chain; raise :class:`AuditIntegrityError` if broken.

        Returns ``True`` when intact so callers can assert on the result.
        """
        prev = GENESIS_HASH
        for index, entry in enumerate(self._entries):
            if entry.sequence != index:
                raise AuditIntegrityError(
                    "audit sequence is not contiguous",
                    expected=index,
                    found=entry.sequence,
                )
            if entry.prev_hash != prev:
                raise AuditIntegrityError(
                    "audit chain is broken (prev_hash mismatch)",
                    sequence=entry.sequence,
                )
            if entry.entry_hash != entry.compute_hash():
                raise AuditIntegrityError(
                    "audit entry hash does not match its body",
                    sequence=entry.sequence,
                )
            prev = entry.entry_hash
        return True

    # -- persistence (canonical JSON; never the frozen corpus) -----------------

    def to_dict(self) -> dict[str, Any]:
        """A canonical, serialisable snapshot of the journal."""
        return {
            "audit_version": "1.0.0",
            "count": len(self._entries),
            "head_hash": self.head_hash(),
            "entries": [e.to_dict() for e in self._entries],
        }

    def save(self, path: str | Path) -> Path:
        """Write the journal to ``path`` as canonical JSON and return the path."""
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(canonical_json(self.to_dict()), encoding="utf-8")
        return target

    @classmethod
    def load(cls, path: str | Path, *, clock: Clock | None = None) -> AuditJournal:
        """Load a journal from canonical JSON and verify its integrity."""
        raw = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls.from_entries(raw.get("entries", ()), clock=clock)

    @classmethod
    def from_entries(cls, records: Iterable[Any], *, clock: Clock | None = None) -> AuditJournal:
        """Rebuild a journal from serialised entries and verify its chain."""
        journal = cls(clock=clock)
        for record in records:
            journal._entries.append(
                AuditEntry(
                    sequence=int(record["sequence"]),
                    act=AuditAct(record["act"]),
                    universal_id=str(record["universal_id"]),
                    version=str(record["version"]),
                    content_hash=str(record["content_hash"]),
                    state=str(record["state"]),
                    actor=str(record["actor"]),
                    timestamp=str(record["timestamp"]),
                    prev_hash=str(record["prev_hash"]),
                    entry_hash=str(record.get("entry_hash", "")),
                )
            )
        journal.verify()
        return journal


__all__ = [
    "GENESIS_HASH",
    "Clock",
    "utc_clock",
    "SequenceClock",
    "AuditJournal",
]
