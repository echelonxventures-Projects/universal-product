"""EPIC-PLAT-003 — Resumable-run checkpoint (Terminal T5).

Repository operations are **resumable**: a run persists the set of stages that have
already PASSED, keyed to the configuration digest. A subsequent resumed run skips those
stages (reusing their recorded evidence) and re-runs only what has not yet passed — so a
long verification interrupted after ``verify.sh`` need not re-run it. The checkpoint is
keyed to the config digest, so any change to the pipeline invalidates a stale checkpoint
and forces a clean run (deterministic, fail-safe).
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from platform.repository_operations.errors import CheckpointError
from typing import Any


@dataclass(frozen=True, slots=True)
class Checkpoint:
    """The persisted state of PASSED stages for one configuration digest."""

    config_digest: str
    completed: Mapping[str, str]  # stage_id -> evidence_ref

    def to_dict(self) -> dict[str, Any]:
        return {
            "config_digest": self.config_digest,
            "completed": dict(self.completed),
        }

    @classmethod
    def from_dict(cls, raw: Mapping[str, Any]) -> Checkpoint:
        if not isinstance(raw, Mapping):
            raise CheckpointError("checkpoint payload must be a mapping")
        config_digest = raw.get("config_digest")
        completed = raw.get("completed", {})
        if not isinstance(config_digest, str) or not config_digest:
            raise CheckpointError("checkpoint is missing a config_digest")
        if not isinstance(completed, Mapping):
            raise CheckpointError("checkpoint completed set must be a mapping")
        return cls(
            config_digest=config_digest,
            completed={str(k): str(v) for k, v in completed.items()},
        )


class CheckpointStore:
    """A JSON-backed checkpoint store bound to a filesystem path (injectable in tests)."""

    __slots__ = ("_path",)

    def __init__(self, path: str | Path) -> None:
        self._path = Path(path)

    @property
    def path(self) -> Path:
        return self._path

    def load(self) -> Checkpoint | None:
        """Return the persisted checkpoint, or ``None`` when none exists.

        Raises:
            CheckpointError: if a checkpoint file exists but is unreadable or malformed.
        """
        if not self._path.is_file():
            return None
        try:
            raw = json.loads(self._path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError, UnicodeDecodeError) as exc:
            raise CheckpointError(
                "checkpoint file could not be read or parsed",
                path=str(self._path),
                detail=str(exc),
            ) from exc
        return Checkpoint.from_dict(raw)

    def save(self, checkpoint: Checkpoint) -> None:
        """Persist ``checkpoint`` deterministically (sorted keys), creating parents."""
        try:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            self._path.write_text(
                json.dumps(checkpoint.to_dict(), sort_keys=True, indent=2) + "\n",
                encoding="utf-8",
            )
        except OSError as exc:
            raise CheckpointError(
                "checkpoint file could not be written",
                path=str(self._path),
                detail=str(exc),
            ) from exc


__all__ = ["Checkpoint", "CheckpointStore"]
