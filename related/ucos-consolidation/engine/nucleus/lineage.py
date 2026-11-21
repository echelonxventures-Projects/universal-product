"""UCOS-NUC-001 Part 07 — the Universal Lineage Ledger (D-22).

Lineage in this repository was already complete on the object axis: every UCKO carries
provenance, trace links, temporal events, evidence refs, attestations and replay proofs,
and the measured orphan counts are zero. What had no home was lineage for the
*structural* population — nuclei, layers, compositions and ownership moves were not
subjects of any ledger, so an ownership change left no chain of custody.

This module is that ledger and nothing more. It is append-only and hash-chained in the
same shape the registry audit trail already uses (``prev_hash`` → ``entry_hash``), so a
lineage that has been rewritten is detectable rather than merely discouraged. It holds no
wall-clock: ordering is insertion order, which is the only ordering that replays.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from typing import Any

from engine.nucleus.errors import NucleusError
from engine.uckp.canonical import content_hash

#: The kinds of lineage event the ledger records. Open by construction: ``record``
#: accepts any non-empty event name, so a future event kind is a call, not an edit.
GENESIS = "genesis"
REGISTERED = "registered"
OWNERSHIP_ASSIGNED = "ownership-assigned"
OWNERSHIP_SUPERSEDED = "ownership-superseded"
EVOLVED = "evolved"
VALIDATED = "validated"
CERTIFIED = "certified"
REPLAYED = "replayed"

#: The event recording that a subject was bound to a resolved reference frame. Declared
#: here, with the other events, rather than in the binder: the ledger owns its vocabulary,
#: and a caller that queries lineage for context bindings must not have to import the
#: context layer to name the event it is looking for.
CONTEXT_BOUND = "context-bound"


@dataclass(frozen=True, slots=True)
class LineageEntry:
    """One tamper-evident lineage event about one subject."""

    sequence: int
    event: str
    subject_id: str
    subject_key: str
    detail: Mapping[str, Any] = field(default_factory=dict)
    prev_hash: str = ""
    entry_hash: str = ""

    def payload(self) -> dict[str, Any]:
        return {
            "sequence": self.sequence,
            "event": self.event,
            "subject_id": self.subject_id,
            "subject_key": self.subject_key,
            "detail": dict(self.detail),
            "prev_hash": self.prev_hash,
        }

    def computed_hash(self) -> str:
        return content_hash(self.payload())

    def to_dict(self) -> dict[str, Any]:
        payload = self.payload()
        payload["entry_hash"] = self.entry_hash
        return payload


class LineageLedger:
    """An append-only, hash-chained ledger of lineage events.

    Nothing is ever deleted or modified: :meth:`record` appends, and the chain makes any
    retroactive edit detectable through :meth:`is_intact`. Supersession — recording that a
    later entry replaces an earlier one — is how the ledger expresses change (AC-009).
    """

    __slots__ = ("_entries",)

    def __init__(self, entries: Iterable[LineageEntry] = ()) -> None:
        self._entries: list[LineageEntry] = list(entries)

    def record(
        self,
        event: str,
        *,
        subject_id: str,
        subject_key: str,
        detail: Mapping[str, Any] | None = None,
    ) -> LineageEntry:
        """Append one lineage event and return the sealed entry.

        Raises:
            NucleusError: the event name or subject is empty. Lineage without a named
                event and a named subject is not lineage.
        """
        for name, value in (
            ("event", event),
            ("subject_id", subject_id),
            ("subject_key", subject_key),
        ):
            if not isinstance(value, str) or not value.strip():
                raise NucleusError("lineage field must be a non-empty string", at=name)
        previous = self._entries[-1].entry_hash if self._entries else ""
        draft = LineageEntry(
            sequence=len(self._entries) + 1,
            event=event.strip(),
            subject_id=subject_id.strip(),
            subject_key=subject_key.strip(),
            detail=dict(detail or {}),
            prev_hash=previous,
        )
        sealed = LineageEntry(
            sequence=draft.sequence,
            event=draft.event,
            subject_id=draft.subject_id,
            subject_key=draft.subject_key,
            detail=draft.detail,
            prev_hash=previous,
            entry_hash=draft.computed_hash(),
        )
        self._entries.append(sealed)
        return sealed

    # -- inspection --------------------------------------------------------- #

    def __len__(self) -> int:
        return len(self._entries)

    def entries(
        self, *, subject_id: str | None = None, event: str | None = None
    ) -> tuple[LineageEntry, ...]:
        """Every entry, in insertion order, optionally filtered."""
        found = tuple(self._entries)
        if subject_id is not None:
            found = tuple(e for e in found if e.subject_id == subject_id)
        if event is not None:
            found = tuple(e for e in found if e.event == event)
        return found

    @property
    def head(self) -> str:
        """The head of the chain — the digest of the last entry, or the empty string."""
        return self._entries[-1].entry_hash if self._entries else ""

    def is_intact(self) -> bool:
        """True iff every entry's digest and back-link reproduce from its own content."""
        previous = ""
        for index, entry in enumerate(self._entries, start=1):
            if entry.sequence != index or entry.prev_hash != previous:
                return False
            if entry.entry_hash != entry.computed_hash():
                return False
            previous = entry.entry_hash
        return True

    def lineage_of(self, subject_id: str) -> tuple[str, ...]:
        """The ordered event names recorded about one subject."""
        return tuple(e.event for e in self.entries(subject_id=subject_id))

    def subjects(self) -> tuple[str, ...]:
        """Every subject identifier the ledger has heard of, ordered."""
        return tuple(sorted({e.subject_id for e in self._entries}))

    def orphans(self, known_ids: Iterable[str]) -> tuple[str, ...]:
        """Subject ids the ledger records that are not in ``known_ids`` (AC-012)."""
        known = set(known_ids)
        return tuple(sorted(s for s in self.subjects() if s not in known))

    def unrecorded(self, known_ids: Iterable[str]) -> tuple[str, ...]:
        """Known subject ids the ledger has *no* entry for — the gap AC-012 forbids."""
        recorded = set(self.subjects())
        return tuple(sorted(s for s in set(known_ids) if s not in recorded))

    def to_document(self) -> dict[str, Any]:
        return {
            "schema": "ucos-universal-lineage-ledger",
            "version": "1.0.0",
            "count": len(self._entries),
            "head": self.head,
            "intact": self.is_intact(),
            "entries": [e.to_dict() for e in self._entries],
        }

    def digest(self) -> str:
        return content_hash(self.to_document())


def ledger_for(registry: Any) -> LineageLedger:
    """Build the lineage of a :class:`~engine.nucleus.registry.NucleusRegistry`.

    Every registered subject gets a genesis and a registration entry; every ownership
    assignment gets an assignment (or supersession) entry. The result is a complete
    chain of custody for the structural population, derived — never authored.

    If the registry is bound to a reference frame, every subject also gets a
    :data:`CONTEXT_BOUND` entry, so a bound population's lineage *is* context lineage
    without the caller having to remember to bind it. An unbound registry produces the
    same ledger it always did — the binding is what adds the coordinate, not this
    function inventing one.
    """
    ledger = LineageLedger()
    context = dict(getattr(registry, "context", {}) or {})
    for subject in registry.subjects():
        ledger.record(
            GENESIS,
            subject_id=subject.universal_id,
            subject_key=subject.key,
            detail={"role": subject.role.value, "content_hash": subject.content_hash},
        )
        ledger.record(
            REGISTERED,
            subject_id=subject.universal_id,
            subject_key=subject.key,
            detail={"namespace": subject.namespace, "composes": list(subject.composes)},
        )
        if context:
            ledger.record(
                CONTEXT_BOUND,
                subject_id=subject.universal_id,
                subject_key=subject.key,
                detail=dict(context),
            )
    for assignment in registry.assignments():
        ledger.record(
            OWNERSHIP_SUPERSEDED if assignment.supersedes else OWNERSHIP_ASSIGNED,
            subject_id=assignment.capability_id,
            subject_key=assignment.capability_key,
            detail={
                "owner_id": assignment.owner_id,
                "owner_key": assignment.owner_key,
                "owner_role": assignment.owner_role.value,
                "authority": assignment.authority,
                "supersedes": assignment.supersedes,
            },
        )
    return ledger


__all__ = [
    "CONTEXT_BOUND",
    "GENESIS",
    "REGISTERED",
    "OWNERSHIP_ASSIGNED",
    "OWNERSHIP_SUPERSEDED",
    "EVOLVED",
    "VALIDATED",
    "CERTIFIED",
    "REPLAYED",
    "LineageEntry",
    "LineageLedger",
    "ledger_for",
]
