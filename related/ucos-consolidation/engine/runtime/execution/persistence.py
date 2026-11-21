"""EPIC-RTE-002 — Execution Persistence (Runtime Execution Platform).

Realises **Execution Persistence**: deterministic serialisation and restoration of
the platform's recorded artefacts (checkpoints, snapshots, runs). Serialisation is
canonical JSON — ``sort_keys=True`` with no whitespace variance — so an artefact
round-trips byte-for-byte and two identical artefacts serialise identically
(RUNTIME-013 ORL-20). Persistence stores data; it executes nothing (ORL-15).

Self-contained artefacts (a :class:`~engine.runtime.execution.checkpoint.Checkpoint`)
restore to a live object via their ``from_dict`` constructor, which is what makes an
execution **resumable across process boundaries**. Composition-bearing artefacts (a
full run/snapshot) persist as auditable data; they are restored as data and re-bound
to a composition by re-coordination/replay (see
:mod:`~engine.runtime.execution.replay`).
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

from engine.runtime.execution.checkpoint import Checkpoint
from engine.runtime.execution.errors import PersistenceError

if TYPE_CHECKING:  # pragma: no cover - typing only, avoids an import cycle
    from engine.runtime.execution.snapshot import Snapshot


@runtime_checkable
class Serialisable(Protocol):
    """Anything exposing a deterministic ``to_dict`` view (structural typing)."""

    def to_dict(self) -> dict[str, Any]: ...  # pragma: no cover - protocol stub


def to_json(artefact: Serialisable | dict[str, Any]) -> str:
    """Serialise an artefact (or its dict view) to canonical, deterministic JSON."""
    payload = artefact if isinstance(artefact, dict) else artefact.to_dict()
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def from_json(blob: str) -> dict[str, Any]:
    """Parse canonical JSON back into a plain mapping.

    Raises:
        PersistenceError: if ``blob`` is not a JSON object.
    """
    try:
        data = json.loads(blob)
    except json.JSONDecodeError as exc:
        raise PersistenceError(
            "persisted execution artefact is not valid JSON", detail=str(exc)
        ) from exc
    if not isinstance(data, dict):
        raise PersistenceError("persisted execution artefact is not a JSON object")
    return data


def persist_checkpoint(cp: Checkpoint) -> str:
    """Serialise a checkpoint to canonical JSON."""
    return to_json(cp)


def restore_checkpoint(blob: str) -> Checkpoint:
    """Restore a :class:`Checkpoint` from canonical JSON (a resumable artefact)."""
    return Checkpoint.from_dict(from_json(blob))


def persist_snapshot(snap: Snapshot) -> str:
    """Serialise a snapshot to canonical JSON."""
    return to_json(snap)


def persist_run(run_view: Serialisable | dict[str, Any]) -> str:
    """Serialise a run's auditable view to canonical JSON."""
    return to_json(run_view)


__all__ = [
    "Serialisable",
    "to_json",
    "from_json",
    "persist_checkpoint",
    "restore_checkpoint",
    "persist_snapshot",
    "persist_run",
]
