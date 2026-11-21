"""EPIC-RTE-002 — Execution Replay Validation (Runtime Execution Platform).

Realises **Execution Replay Validation**: the proof that the platform is
deterministic. It replays a run (via :mod:`~engine.runtime.execution.replay`) and
asserts the replay reproduces the original **byte-for-byte** — identical
``run_id`` and identical canonical-JSON descriptor (RUNTIME-013 ORL-20). Any
divergence is a determinism defect and is reported precisely. Validation compares
records; it executes nothing (ORL-15).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from engine.foundation.obs.logging import get_logger
from engine.runtime.execution.errors import ReplayValidationError
from engine.runtime.execution.persistence import to_json
from engine.runtime.execution.replay import replay

if TYPE_CHECKING:  # pragma: no cover - typing only, avoids an import cycle
    from engine.runtime.composition import RuntimeComposition
    from engine.runtime.execution.coordinator import ExecutionRun

_logger = get_logger("runtime.execution.replay_validation")

#: The recorded replay-validation format.
REPLAY_VALIDATION_FORMAT = "ucos-execution-replay-validation/1.0.0"


@dataclass(frozen=True, slots=True)
class ReplayValidation:
    """The deterministic result of comparing an original run to its replay."""

    original_run_id: str
    replayed_run_id: str
    identical_id: bool
    identical_descriptor: bool
    mismatches: tuple[str, ...]

    @property
    def valid(self) -> bool:
        """True iff the replay reproduced the original byte-for-byte."""
        return self.identical_id and self.identical_descriptor and not self.mismatches

    def to_dict(self) -> dict[str, Any]:
        return {
            "replay_validation_format": REPLAY_VALIDATION_FORMAT,
            "original_run_id": self.original_run_id,
            "replayed_run_id": self.replayed_run_id,
            "identical_id": self.identical_id,
            "identical_descriptor": self.identical_descriptor,
            "valid": self.valid,
            "mismatches": list(self.mismatches),
        }


def compare_runs(original: ExecutionRun, replayed: ExecutionRun) -> ReplayValidation:
    """Compare two runs for byte-for-byte determinism (no replay is performed)."""
    identical_id = original.run_id == replayed.run_id
    original_json = to_json(original.to_dict())
    replayed_json = to_json(replayed.to_dict())
    identical_descriptor = original_json == replayed_json

    mismatches: list[str] = []
    if not identical_id:
        mismatches.append("run_id")
    if not identical_descriptor:
        mismatches.extend(_field_mismatches(original.to_dict(), replayed.to_dict()))

    return ReplayValidation(
        original_run_id=original.run_id,
        replayed_run_id=replayed.run_id,
        identical_id=identical_id,
        identical_descriptor=identical_descriptor,
        mismatches=tuple(mismatches),
    )


def validate_replay(composition: RuntimeComposition, run: ExecutionRun) -> ReplayValidation:
    """Replay ``run`` and validate it reproduces the original (deterministic)."""
    replayed = replay(composition, run)
    result = compare_runs(run, replayed)
    _logger.info(
        "runtime.execution.replay_validated",
        original_run=run.run_id,
        replayed_run=replayed.run_id,
        valid=result.valid,
    )
    return result


def require_replay(composition: RuntimeComposition, run: ExecutionRun) -> ReplayValidation:
    """Validate a replay and raise if it is not byte-for-byte identical.

    Raises:
        ReplayValidationError: if the replay diverged from the original run.
    """
    result = validate_replay(composition, run)
    if not result.valid:
        raise ReplayValidationError(
            "replay did not reproduce the original execution byte-for-byte",
            original_run_id=result.original_run_id,
            replayed_run_id=result.replayed_run_id,
            mismatches=list(result.mismatches),
        )
    return result


def _field_mismatches(original: dict[str, Any], replayed: dict[str, Any]) -> list[str]:
    """The top-level descriptor keys whose canonical JSON differs (sorted)."""
    keys = sorted(set(original) | set(replayed))
    return [
        key
        for key in keys
        if to_json({key: original.get(key)}) != to_json({key: replayed.get(key)})
    ]


__all__ = [
    "REPLAY_VALIDATION_FORMAT",
    "ReplayValidation",
    "compare_runs",
    "validate_replay",
    "require_replay",
]
