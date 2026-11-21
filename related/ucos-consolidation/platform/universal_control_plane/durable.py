"""UCOS-CTRL-000001 — Durable Replay (Wave 7).

The control plane's original replay was process-local: it could prove that two
in-memory runs agreed, and lost everything the moment the process exited. A
control plane whose state dies with its process cannot be the operating system of
anything, because the first question after a restart — *what did we already
determine?* — has no answer.

This module makes replay durable. Every determination the control plane makes is
appended to a hash-chained NDJSON journal on disk; after a restart the journal is
read back and the state is *reconstructed*, not re-derived. The distinction
matters: re-deriving asks the repository again and gets whatever is true now,
while reconstruction returns what was recorded then, which is the only thing an
audit can be run against.

The chain is what makes that trustworthy. Each entry binds its own payload digest
to the previous entry's hash, so a journal that was edited between runs fails
closed at the first broken link rather than replaying a plausible fiction.

Reconstruction is version-, governance- and certification-aware: those record
types are rebuilt as themselves, not as opaque blobs, so a reconstructed state
answers the same questions a live one does.
"""

from __future__ import annotations

import json
import os
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from pathlib import Path
from platform.universal_control_plane.errors import JournalError
from platform.universal_control_plane.manifest import ControlPlaneManifest, default_manifest
from platform.universal_control_plane.ontology import (
    CertificationState,
    ChangeRecord,
    CriterionOutcome,
    GovernanceRecord,
    JournalEntry,
    RegistrationRecord,
    VersionRecord,
    payload_digest,
)
from typing import Any

#: The genesis link: the previous-hash of the first entry in every journal.
GENESIS_HASH = "0" * 64

# The recorded event vocabulary. Each maps to exactly one reconstructor below, so
# an unknown event is carried through the chain but never silently reinterpreted.
EVENT_TRUTH_DISCOVERED = "TRUTH_DISCOVERED"
EVENT_REGISTERED = "REGISTERED"
EVENT_GOVERNED = "GOVERNED"
EVENT_CERTIFIED = "CERTIFIED"
EVENT_VERSIONED = "VERSIONED"
EVENT_CHANGED = "CHANGED"

JOURNAL_EVENTS: tuple[str, ...] = (
    EVENT_TRUTH_DISCOVERED,
    EVENT_REGISTERED,
    EVENT_GOVERNED,
    EVENT_CERTIFIED,
    EVENT_VERSIONED,
    EVENT_CHANGED,
)


# ---------------------------------------------------------------------------
# Reconstructors — dict → the record type it was written from
# ---------------------------------------------------------------------------


def _tuple(raw: Any) -> tuple[str, ...]:
    if not isinstance(raw, list | tuple):
        return ()
    return tuple(str(item) for item in raw)


def _rebuild_registration(raw: Mapping[str, Any]) -> RegistrationRecord:
    return RegistrationRecord(
        registration_id=str(raw.get("registration_id", "")),
        subject_id=str(raw.get("subject_id", "")),
        subject_kind=str(raw.get("subject_kind", "")),
        name=str(raw.get("name", "")),
        module=str(raw.get("module", "")),
        layer=str(raw.get("layer", "")),
        universe_id=str(raw.get("universe_id", "")),
        owner_id=str(raw.get("owner_id", "")),
        capability_id=str(raw.get("capability_id", "")),
        lineage=_tuple(raw.get("lineage")),
        description=str(raw.get("description", "")),
        attributes=dict(raw.get("attributes", {}) or {}),
        tick=int(raw.get("tick", 0)),
    )


def _rebuild_governance(raw: Mapping[str, Any]) -> GovernanceRecord:
    return GovernanceRecord(
        record_id=str(raw.get("record_id", "")),
        subject_id=str(raw.get("subject_id", "")),
        status=str(raw.get("status", "")),
        lifecycle_state=str(raw.get("lifecycle_state", "")),
        satisfied_rules=_tuple(raw.get("satisfied_rules")),
        violation_ids=_tuple(raw.get("violation_ids")),
        evidence_ids=_tuple(raw.get("evidence_ids")),
        determination_id=str(raw.get("determination_id", "")),
        rationale=str(raw.get("rationale", "")),
        attributes=dict(raw.get("attributes", {}) or {}),
        tick=int(raw.get("tick", 0)),
    )


def _rebuild_certification(raw: Mapping[str, Any]) -> CertificationState:
    criteria = tuple(
        CriterionOutcome(
            criterion_id=str(item.get("criterion_id", "")),
            severity=str(item.get("severity", "")),
            passed=bool(item.get("passed", False)),
            message=str(item.get("message", "")),
        )
        for item in raw.get("criteria", []) or ()
        if isinstance(item, Mapping)
    )
    return CertificationState(
        state_id=str(raw.get("state_id", "")),
        subject_id=str(raw.get("subject_id", "")),
        status=str(raw.get("status", "")),
        eligible=bool(raw.get("eligible", False)),
        version=str(raw.get("version", "")),
        criteria=criteria,
        evidence_ids=_tuple(raw.get("evidence_ids")),
        lineage=_tuple(raw.get("lineage")),
        rationale=str(raw.get("rationale", "")),
        attributes=dict(raw.get("attributes", {}) or {}),
        tick=int(raw.get("tick", 0)),
    )


def _rebuild_version(raw: Mapping[str, Any]) -> VersionRecord:
    return VersionRecord(
        subject_id=str(raw.get("subject_id", "")),
        kind=str(raw.get("version_kind", "")),
        version=str(raw.get("version", "")),
        revision=int(raw.get("revision", 1)),
        content_digest=str(raw.get("content_digest", "")),
        parent_version_id=str(raw.get("parent_version_id", "")),
        superseded_by=str(raw.get("superseded_by", "")),
        rationale=str(raw.get("rationale", "")),
        attributes=dict(raw.get("attributes", {}) or {}),
        tick=int(raw.get("tick", 0)),
    )


def _rebuild_change(raw: Mapping[str, Any]) -> ChangeRecord:
    return ChangeRecord(
        change_id=str(raw.get("change_id", "")),
        subject_id=str(raw.get("subject_id", "")),
        kind=str(raw.get("change_kind", "")),
        dimension=str(raw.get("dimension", "")),
        sequence=int(raw.get("sequence", 0)),
        from_value=str(raw.get("from_value", "")),
        to_value=str(raw.get("to_value", "")),
        delta_digest=str(raw.get("delta_digest", "")),
        rationale=str(raw.get("rationale", "")),
        attributes=dict(raw.get("attributes", {}) or {}),
        tick=int(raw.get("tick", 0)),
    )


@dataclass(frozen=True, slots=True)
class ReplayedState:
    """Control-plane state reconstructed from a durable journal."""

    truth_id: str
    registrations: tuple[RegistrationRecord, ...] = ()
    governance: tuple[GovernanceRecord, ...] = ()
    certifications: tuple[CertificationState, ...] = ()
    versions: tuple[VersionRecord, ...] = ()
    changes: tuple[ChangeRecord, ...] = ()
    unknown_events: tuple[str, ...] = ()

    def counts(self) -> dict[str, int]:
        return {
            "registrations": len(self.registrations),
            "governance": len(self.governance),
            "certifications": len(self.certifications),
            "versions": len(self.versions),
            "changes": len(self.changes),
        }

    def governance_of(self, subject_id: str) -> GovernanceRecord | None:
        return next((r for r in self.governance if r.subject_id == subject_id), None)

    def certification_of(self, subject_id: str) -> CertificationState | None:
        return next((s for s in self.certifications if s.subject_id == subject_id), None)

    def versions_of(self, subject_id: str) -> tuple[VersionRecord, ...]:
        return tuple(v for v in self.versions if v.subject_id == subject_id)

    def to_dict(self) -> dict[str, Any]:
        return {
            "truth_id": self.truth_id,
            "counts": self.counts(),
            "unknown_events": list(self.unknown_events),
            "registrations": [r.to_dict() for r in self.registrations],
            "governance": [r.to_dict() for r in self.governance],
            "certifications": [s.to_dict() for s in self.certifications],
            "versions": [v.to_dict() for v in self.versions],
            "changes": [c.to_dict() for c in self.changes],
        }

    def digest(self) -> str:
        """The content digest of the reconstructed state — equal iff the state is equal."""
        return payload_digest(self.to_dict())


@dataclass
class DurableJournal:
    """A hash-chained, append-only, restart-safe control-plane journal."""

    path: Path
    _entries: list[JournalEntry] = field(default_factory=list)

    # -- construction ----------------------------------------------------

    @classmethod
    def open(
        cls,
        root: Path | str,
        *,
        manifest: ControlPlaneManifest | None = None,
        load: bool = True,
    ) -> DurableJournal:
        """Open (or create) the journal beneath *root*, per the declared manifest.

        The manifest supplies the directory and filename; the caller supplies the
        root. Neither this module nor the manifest assumes a repository layout.
        """
        resolved = manifest or default_manifest()
        directory = Path(root) / resolved.journal_dirname
        directory.mkdir(parents=True, exist_ok=True)
        journal = cls(path=directory / resolved.journal_filename)
        if load and journal.path.exists():
            journal.load()
        return journal

    # -- writing ---------------------------------------------------------

    @property
    def head_hash(self) -> str:
        """The hash of the last entry — the link the next append will bind to."""
        return self._entries[-1].entry_hash if self._entries else GENESIS_HASH

    def append(
        self, subject_id: str, event: str, payload: Mapping[str, Any], *, tick: int = 0
    ) -> JournalEntry:
        """Append one entry and durably write it before returning.

        The write is flushed and fsynced per entry. That is slower than buffering,
        and it is the whole point: an entry that is only in a buffer when the
        process dies is exactly the entry a restart needed.
        """
        if not subject_id.strip():
            raise JournalError("a journal entry requires a non-empty subject_id")
        if not event.strip():
            raise JournalError("a journal entry requires a non-empty event")
        entry = JournalEntry(
            sequence=len(self._entries) + 1,
            subject_id=subject_id,
            event=event,
            payload_digest=payload_digest(payload),
            previous_hash=self.head_hash,
            payload=dict(payload),
            tick=tick,
        )
        self._entries.append(entry)
        self._write(entry)
        return entry

    def append_record(self, event: str, record: Any, *, tick: int = 0) -> JournalEntry:
        """Append the canonical projection of a control-plane record."""
        payload = record.to_dict()
        subject_id = str(payload.get("subject_id") or payload.get("truth_id") or "")
        return self.append(subject_id, event, payload, tick=tick)

    def _write(self, entry: JournalEntry) -> None:
        line = json.dumps(entry.to_dict(), sort_keys=True, separators=(",", ":"), default=str)
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with self.path.open("a", encoding="utf-8") as handle:
                handle.write(line + "\n")
                handle.flush()
                os.fsync(handle.fileno())
        except OSError as exc:
            raise JournalError(f"journal entry could not be written to {self.path}: {exc}") from exc

    # -- reading ---------------------------------------------------------

    def load(self) -> tuple[JournalEntry, ...]:
        """Read the journal back from disk, replacing any in-memory entries."""
        if not self.path.exists():
            self._entries = []
            return ()
        try:
            raw = self.path.read_text("utf-8")
        except OSError as exc:
            raise JournalError(f"journal could not be read from {self.path}: {exc}") from exc
        entries: list[JournalEntry] = []
        for number, line in enumerate(raw.splitlines(), start=1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                entries.append(JournalEntry.from_dict(json.loads(stripped)))
            except (ValueError, KeyError, TypeError) as exc:
                raise JournalError(
                    f"{self.path}:{number} is not a readable journal entry: {exc}"
                ) from exc
        self._entries = entries
        return tuple(entries)

    def entries(self) -> tuple[JournalEntry, ...]:
        return tuple(self._entries)

    def for_subject(self, subject_id: str) -> tuple[JournalEntry, ...]:
        return tuple(e for e in self._entries if e.subject_id == subject_id)

    def by_event(self, event: str) -> tuple[JournalEntry, ...]:
        return tuple(e for e in self._entries if e.event == event)

    def count(self) -> int:
        return len(self._entries)

    # -- integrity -------------------------------------------------------

    def verify(self) -> bool:
        """Verify the chain end to end; raises :class:`JournalError` at the first break."""
        previous = GENESIS_HASH
        for index, entry in enumerate(self._entries, start=1):
            if entry.sequence != index:
                raise JournalError(
                    f"journal sequence breaks at position {index}: recorded {entry.sequence}"
                )
            if entry.previous_hash != previous:
                raise JournalError(
                    f"journal chain breaks at entry {entry.sequence}: "
                    f"previous_hash {entry.previous_hash[:12]}… != {previous[:12]}…"
                )
            recomputed = payload_digest(entry.payload)
            if entry.payload_digest != recomputed:
                raise JournalError(
                    f"journal entry {entry.sequence} payload does not match its digest "
                    f"(recorded {entry.payload_digest[:12]}…, computed {recomputed[:12]}…)"
                )
            previous = entry.entry_hash
        return True

    # -- reconstruction --------------------------------------------------

    def reconstruct(self) -> ReplayedState:
        """Rebuild control-plane state from the journal, verifying the chain first.

        Later entries for the same subject supersede earlier ones for the state
        types that hold one current value (governance, certification), while
        versions and changes accumulate — the same shape the live engines have,
        so a reconstructed state and a live one answer identically.
        """
        self.verify()
        truth_id = ""
        registrations: dict[str, RegistrationRecord] = {}
        governance: dict[str, GovernanceRecord] = {}
        certifications: dict[str, CertificationState] = {}
        versions: list[VersionRecord] = []
        changes: list[ChangeRecord] = []
        unknown: list[str] = []

        for entry in self._entries:
            payload = entry.payload
            if entry.event == EVENT_TRUTH_DISCOVERED:
                truth_id = str(payload.get("truth_id", "")) or truth_id
            elif entry.event == EVENT_REGISTERED:
                record = _rebuild_registration(payload)
                registrations[record.subject_id] = record
            elif entry.event == EVENT_GOVERNED:
                record_g = _rebuild_governance(payload)
                governance[record_g.subject_id] = record_g
            elif entry.event == EVENT_CERTIFIED:
                state = _rebuild_certification(payload)
                certifications[state.subject_id] = state
            elif entry.event == EVENT_VERSIONED:
                versions.append(_rebuild_version(payload))
            elif entry.event == EVENT_CHANGED:
                changes.append(_rebuild_change(payload))
            else:
                unknown.append(entry.event)

        return ReplayedState(
            truth_id=truth_id,
            registrations=tuple(registrations[k] for k in sorted(registrations)),
            governance=tuple(governance[k] for k in sorted(governance)),
            certifications=tuple(certifications[k] for k in sorted(certifications)),
            versions=tuple(versions),
            changes=tuple(changes),
            unknown_events=tuple(sorted(set(unknown))),
        )

    def record_all(self, event: str, records: Iterable[Any], *, tick: int = 0) -> int:
        """Append many records under one event; returns how many were written."""
        written = 0
        for record in records:
            self.append_record(event, record, tick=tick)
            written += 1
        return written

    def to_dict(self) -> dict[str, Any]:
        return {
            "engine": "DurableJournal",
            "path": str(self.path),
            "count": self.count(),
            "head_hash": self.head_hash,
            "events": sorted({e.event for e in self._entries}),
        }


__all__ = [
    "EVENT_CERTIFIED",
    "EVENT_CHANGED",
    "EVENT_GOVERNED",
    "EVENT_REGISTERED",
    "EVENT_TRUTH_DISCOVERED",
    "EVENT_VERSIONED",
    "GENESIS_HASH",
    "JOURNAL_EVENTS",
    "DurableJournal",
    "ReplayedState",
]
