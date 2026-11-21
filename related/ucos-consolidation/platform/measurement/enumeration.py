"""UCOS-EPIC-004 — Enumeration Engine (UCOS-UMA-001).

Enumerates the authoritative Registry population by dimension — the deterministic "what
exists" measurement. It **discovers** the vocabularies present in Truth (programs,
categories, lifecycle statuses, volumes, relationship types, owners) rather than
asserting a hardcoded enumeration: the engine reads the corpus and reports what the
corpus contains. It never invents a dimension value that Truth does not carry, and it
never writes back — Measurement consumes Truth and never creates it.

The result :class:`Enumeration` is immutable, content-addressed, and a pure function of
the :class:`~platform.measurement.source.TruthSnapshot` (IMP-007 §5 determinism).
"""

from __future__ import annotations

from dataclasses import dataclass
from platform.foundation.contracts import content_hash
from platform.measurement.contracts import Measurement, MeasurementKind
from platform.measurement.errors import EnumerationError
from platform.measurement.source import TruthSnapshot
from typing import Any

from engine.registry.models import TRACE_STAGES


@dataclass(frozen=True, slots=True)
class Enumeration:
    """An immutable, content-addressed enumeration of the Registry population.

    ``dimensions`` maps each discovered dimension name to the sorted, de-duplicated set
    of values present in Truth; ``counts`` records the top-level population sizes.
    """

    dimensions: dict[str, tuple[str, ...]]
    counts: dict[str, int]
    enumeration_id: str = ""

    @classmethod
    def create(cls, dimensions: dict[str, tuple[str, ...]], counts: dict[str, int]) -> Enumeration:
        ordered_dims = {name: dimensions[name] for name in sorted(dimensions)}
        ordered_counts = {name: counts[name] for name in sorted(counts)}
        core = {"dimensions": ordered_dims, "counts": ordered_counts}
        return cls(
            dimensions=ordered_dims,
            counts=ordered_counts,
            enumeration_id=f"UCOS-UMAE-{content_hash(core)[:16]}",
        )

    def dimension(self, name: str) -> tuple[str, ...]:
        """Return the enumerated values of ``name`` (raises if the dimension is unknown)."""
        if name not in self.dimensions:
            raise EnumerationError("unknown enumeration dimension", dimension=name)
        return self.dimensions[name]

    def to_dict(self) -> dict[str, Any]:
        return {
            "enumeration_id": self.enumeration_id,
            "dimensions": {name: list(vals) for name, vals in self.dimensions.items()},
            "counts": dict(self.counts),
        }

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())

    def as_measurement(self) -> Measurement:
        """Wrap the enumeration as a recordable :class:`Measurement`."""
        return Measurement.create(
            MeasurementKind.ENUMERATION,
            "registry.population",
            summary=(
                f"{self.counts.get('artifacts', 0)} artifacts, "
                f"{self.counts.get('relationships', 0)} relationships, "
                f"{self.counts.get('volumes', 0)} volumes across "
                f"{len(self.dimensions)} dimensions"
            ),
            payload=self.to_dict(),
        )


def _distinct(values: object) -> tuple[str, ...]:
    """Sorted, de-duplicated, non-empty string values from an iterable."""
    seen = {str(v) for v in values if isinstance(v, str) and v}  # type: ignore[union-attr]
    return tuple(sorted(seen))


class EnumerationEngine:
    """Deterministically enumerates the Registry population from a Truth snapshot."""

    __slots__ = ("_snapshot",)

    def __init__(self, snapshot: TruthSnapshot) -> None:
        if not isinstance(snapshot, TruthSnapshot):
            raise EnumerationError("EnumerationEngine requires a TruthSnapshot")
        self._snapshot = snapshot

    def enumerate(self) -> Enumeration:
        """Enumerate every dimension present in Truth (pure, deterministic)."""
        arts = self._snapshot.artifacts
        rels = self._snapshot.relationships
        vols = self._snapshot.volumes

        dimensions: dict[str, tuple[str, ...]] = {
            "programs": _distinct(a.program for a in arts),
            "categories": _distinct(a.category for a in arts),
            "statuses": _distinct(a.status.value for a in arts),
            "owners": _distinct(a.owner for a in arts),
            "volumes": _distinct(v.volume_id for v in vols),
            "volume_categories": _distinct(v.category for v in vols),
            "relationship_types": _distinct(r.type for r in rels),
            # The canonical 13-stage traceability spine is a fixed vocabulary of Truth's
            # own schema — enumerated here (not invented) for downstream measurement.
            "trace_stages": tuple(TRACE_STAGES),
        }
        counts: dict[str, int] = {
            "artifacts": len(arts),
            "relationships": len(rels),
            "volumes": len(vols),
        }
        for name, values in dimensions.items():
            counts[f"distinct_{name}"] = len(values)
        return Enumeration.create(dimensions, counts)


__all__ = ["Enumeration", "EnumerationEngine"]
