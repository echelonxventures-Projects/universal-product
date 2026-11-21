"""UCOS-CTRL-STATE-000001 — Project State replay adapter (Wave 11).

Project state persists through the durable journal the control plane already owns:
:class:`~platform.universal_control_plane.durable.DurableJournal`, whose entries are
hash-chained, appended one fsync at a time and verifiable byte-for-byte.

This module introduces no journal, no second chain and no parallel persistence format. It
contributes the two functions the generic journal cannot supply — how a project-state
snapshot becomes one entry, and how an entry becomes that snapshot again — plus the event
token under which such entries are written.

The round trip is exact by construction rather than by convention. A recorded entry carries
each entity's *original control-plane projection*, and reconstruction rebuilds every entity
through the same :meth:`~platform.universal_project_state.state.StateEntity.from_projection`
that built it in the first place. Kind, identifier, lifecycle and owner are therefore
re-derived by the identical rules instead of being re-serialised alongside the payload, which
is what makes ``reconstruct(journal).snapshot_id == snapshot.snapshot_id`` a proof of replay
rather than a comparison of two copies of the same string.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from platform.universal_control_plane.durable import DurableJournal
from platform.universal_control_plane.ontology import JournalEntry
from platform.universal_project_state.state import (
    ProjectStateError,
    ProjectStateSnapshot,
    StateEntity,
)
from typing import Any

#: The event token under which a project-state snapshot is journalled.
EVENT_STATE_PROJECTED = "STATE_PROJECTED"

#: The payload keys one journalled snapshot carries.
PAYLOAD_UNIVERSE = "universe_id"
PAYLOAD_TRUTH = "truth_id"
PAYLOAD_ENTITIES = "entities"
PAYLOAD_TICK = "tick"


def snapshot_payload(snapshot: ProjectStateSnapshot) -> dict[str, Any]:
    """The canonical journal payload for *snapshot*."""
    return {
        PAYLOAD_UNIVERSE: snapshot.universe_id,
        PAYLOAD_TRUTH: snapshot.truth_id,
        PAYLOAD_TICK: snapshot.tick,
        PAYLOAD_ENTITIES: [dict(entity.attributes) for entity in snapshot.entities],
    }


def record_snapshot(
    journal: DurableJournal, snapshot: ProjectStateSnapshot, *, tick: int = 0
) -> JournalEntry:
    """Append *snapshot* to *journal* as one durable, chained entry."""
    return journal.append(
        snapshot.snapshot_id, EVENT_STATE_PROJECTED, snapshot_payload(snapshot), tick=tick
    )


def snapshot_from_payload(payload: Mapping[str, Any]) -> ProjectStateSnapshot:
    """Rebuild a snapshot from one journalled payload (fail-closed)."""
    raw_entities = payload.get(PAYLOAD_ENTITIES)
    if not isinstance(raw_entities, Sequence) or isinstance(raw_entities, str | bytes):
        raise ProjectStateError("journalled state payload carries no entities array")
    tick = int(payload.get(PAYLOAD_TICK, 0) or 0)
    entities: list[StateEntity] = []
    for raw in raw_entities:
        if not isinstance(raw, Mapping):
            raise ProjectStateError("journalled state entity is not an object")
        entities.append(StateEntity.from_projection(raw, tick=tick))
    return ProjectStateSnapshot(
        universe_id=str(payload.get(PAYLOAD_UNIVERSE, "")),
        truth_id=str(payload.get(PAYLOAD_TRUTH, "")),
        entities=tuple(entities),
        tick=tick,
    )


def state_entries(journal: DurableJournal) -> tuple[JournalEntry, ...]:
    """Every project-state entry in *journal*, in append order."""
    return tuple(entry for entry in journal.entries() if entry.event == EVENT_STATE_PROJECTED)


def reconstruct(journal: DurableJournal) -> ProjectStateSnapshot:
    """The latest project-state snapshot the journal holds (fail-closed when it holds none)."""
    entries = state_entries(journal)
    if not entries:
        raise ProjectStateError(f"journal holds no {EVENT_STATE_PROJECTED} entry to replay")
    return snapshot_from_payload(entries[-1].payload)


def reconstruct_all(journal: DurableJournal) -> tuple[ProjectStateSnapshot, ...]:
    """Every snapshot the journal holds, oldest first — the project's recorded history."""
    return tuple(snapshot_from_payload(entry.payload) for entry in state_entries(journal))


def reconstruct_at(journal: DurableJournal, sequence: int) -> ProjectStateSnapshot:
    """The snapshot recorded by the entry at *sequence* — historical reconstruction."""
    for entry in state_entries(journal):
        if entry.sequence == sequence:
            return snapshot_from_payload(entry.payload)
    raise ProjectStateError(f"journal holds no {EVENT_STATE_PROJECTED} entry at {sequence}")


def replays(journal: DurableJournal, snapshot: ProjectStateSnapshot) -> bool:
    """Whether the journal replays *snapshot* exactly — chain intact and identity equal."""
    if not journal.verify():
        return False
    try:
        return reconstruct(journal).snapshot_id == snapshot.snapshot_id
    except ProjectStateError:
        return False


__all__ = [
    "EVENT_STATE_PROJECTED",
    "PAYLOAD_ENTITIES",
    "PAYLOAD_TICK",
    "PAYLOAD_TRUTH",
    "PAYLOAD_UNIVERSE",
    "reconstruct",
    "reconstruct_all",
    "reconstruct_at",
    "record_snapshot",
    "replays",
    "snapshot_from_payload",
    "snapshot_payload",
    "state_entries",
]
