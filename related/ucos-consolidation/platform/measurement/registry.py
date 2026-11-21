"""UCOS-EPIC-004 — Measurement Registry (UCOS-UMA-001).

An append-only, content-addressed registry of :class:`~platform.measurement.contracts.Measurement`
records — the durable, audit-safe, recomputable record of what the engine measured. It
mirrors the certified append-only ledger discipline (e.g. the Coverage registry): records
are keyed by their content-addressed ``measurement_id``, re-recording an identical
measurement is idempotent, and recording a *different* body under an already-known id is
refused (fail-closed — no silent overwrite).

Crucially, this is a registry **of measurements about Truth**, not a registry of Truth.
Its identity namespace (``UCOS-UMA*``) is disjoint from the Registry's universal ids, so
a measurement can never be mistaken for, nor overwrite, a fact — Measurement consumes
Truth and never creates it.
"""

from __future__ import annotations

from platform.foundation.contracts import content_hash
from platform.measurement.contracts import Measurement, MeasurementKind
from platform.measurement.errors import MeasurementRegistryError
from typing import Any


class MeasurementRegistry:
    """A deterministic, append-only, content-addressed record surface for measurements."""

    __slots__ = ("_measurements",)

    def __init__(self) -> None:
        self._measurements: dict[str, Measurement] = {}

    # -- append-only recording --------------------------------------------------

    def record(self, measurement: Measurement) -> Measurement:
        """Record a measurement (idempotent by id; fail-closed on a conflicting duplicate)."""
        if not isinstance(measurement, Measurement):
            raise MeasurementRegistryError("only a Measurement may be recorded")
        existing = self._measurements.get(measurement.measurement_id)
        if existing is not None:
            if existing.fingerprint() == measurement.fingerprint():
                return existing
            raise MeasurementRegistryError(
                "measurement id already recorded with different content",
                measurement_id=measurement.measurement_id,
            )
        self._measurements[measurement.measurement_id] = measurement
        return measurement

    def record_all(self, measurements: object) -> tuple[Measurement, ...]:
        """Record every measurement in an iterable (append-only, fail-closed)."""
        recorded: list[Measurement] = []
        for measurement in measurements:  # type: ignore[union-attr]
            recorded.append(self.record(measurement))
        return tuple(recorded)

    # -- accessors --------------------------------------------------------------

    def __len__(self) -> int:
        return len(self._measurements)

    def __contains__(self, measurement_id: str) -> bool:
        return measurement_id in self._measurements

    @property
    def count(self) -> int:
        return len(self._measurements)

    def has(self, measurement_id: str) -> bool:
        return measurement_id in self._measurements

    def get(self, measurement_id: str) -> Measurement:
        """Return the recorded measurement or raise (fail-closed)."""
        measurement = self._measurements.get(measurement_id)
        if measurement is None:
            raise MeasurementRegistryError("unknown measurement", measurement_id=measurement_id)
        return measurement

    def all(self) -> tuple[Measurement, ...]:
        """Every recorded measurement, ordered by id (stable)."""
        return tuple(self._measurements[mid] for mid in sorted(self._measurements))

    def of_kind(self, kind: MeasurementKind) -> tuple[Measurement, ...]:
        """Every recorded measurement of a given kind, ordered by id."""
        if not isinstance(kind, MeasurementKind):
            raise MeasurementRegistryError("of_kind requires a MeasurementKind")
        return tuple(m for m in self.all() if m.kind is kind)

    def counts_by_kind(self) -> dict[str, int]:
        """Count of recorded measurements per kind (ordered by kind value)."""
        counts: dict[str, int] = {}
        for measurement in self._measurements.values():
            counts[measurement.kind.value] = counts.get(measurement.kind.value, 0) + 1
        return {k: counts[k] for k in sorted(counts)}

    def to_dict(self) -> dict[str, Any]:
        return {
            "count": len(self._measurements),
            "counts_by_kind": self.counts_by_kind(),
            "measurements": [m.to_dict() for m in self.all()],
        }

    def fingerprint(self) -> str:
        """Deterministic fingerprint over all recorded measurements."""
        return content_hash(self.to_dict())


__all__ = ["MeasurementRegistry"]
