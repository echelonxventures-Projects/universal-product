"""UCOS-CTRL-000001 — Constitutional Linkage (Wave 10).

An engine that exists, passes its tests and is never connected to anything is an
orphan: measurable, green, and constitutionally invisible. This module is the
measurement that finds those.

For every subject the control plane holds, nine linkages must close —
constitution, ontology, registry, runtime, governance, certification, replay,
version and evidence. Each is a *target identity*, not a boolean: recording that
a subject "has governance" proves nothing, whereas recording the identity of the
governance record that governs it can be followed, and fails when it cannot.

The dimensions are declared in the manifest rather than fixed here, so a
specialisation that adds a tenth constitutional obligation gets it measured
without a code change. Anything a subject leaves empty is reported as missing;
a subject with any missing linkage is an orphan; and the control plane is
constitutionally complete only when the orphan set is empty.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from platform.universal_control_plane.errors import LinkageError, ObjectNotFoundError
from platform.universal_control_plane.manifest import ControlPlaneManifest, default_manifest
from platform.universal_control_plane.ontology import LinkageRecord, payload_digest
from typing import Any


@dataclass
class LinkageEngine:
    """Records and measures constitutional linkage across every declared dimension."""

    manifest: ControlPlaneManifest = field(default_factory=default_manifest)
    _records: dict[str, LinkageRecord] = field(default_factory=dict)

    @property
    def dimensions(self) -> tuple[str, ...]:
        return self.manifest.linkage_dimensions

    # -- recording -------------------------------------------------------

    def link(self, subject_id: str, links: Mapping[str, str], *, tick: int = 0) -> LinkageRecord:
        """Record the linkage of one subject across every declared dimension.

        Fails closed on an undeclared dimension. A linkage the constitution never
        asked for is not a bonus — it is a claim that something was measured
        against a rule that does not exist.
        """
        if not subject_id.strip():
            raise LinkageError("a linkage record requires a non-empty subject_id")
        declared = set(self.dimensions)
        unknown = sorted(set(links) - declared)
        if unknown:
            raise LinkageError(
                f"undeclared linkage dimension(s) for {subject_id!r}: {', '.join(unknown)}"
            )
        resolved = {dimension: str(links.get(dimension, "") or "") for dimension in self.dimensions}
        record = LinkageRecord(
            linkage_id=f"LNK-{subject_id}",
            subject_id=subject_id,
            links=resolved,
            tick=tick,
        )
        self._records[subject_id] = record
        return record

    def link_all(
        self, subjects: Iterable[tuple[str, Mapping[str, str]]], *, tick: int = 0
    ) -> tuple[LinkageRecord, ...]:
        return tuple(
            self.link(subject_id, links, tick=tick)
            for subject_id, links in sorted(subjects, key=lambda item: item[0])
        )

    # -- queries ---------------------------------------------------------

    def record_of(self, subject_id: str) -> LinkageRecord:
        if subject_id not in self._records:
            raise ObjectNotFoundError(f"no linkage recorded for: {subject_id}")
        return self._records[subject_id]

    def records(self) -> tuple[LinkageRecord, ...]:
        return tuple(self._records[key] for key in sorted(self._records))

    def orphans(self) -> tuple[LinkageRecord, ...]:
        """Every subject that leaves at least one constitutional linkage open."""
        return tuple(r for r in self.records() if not r.complete)

    def complete(self) -> bool:
        """True iff something was measured and nothing is orphaned."""
        return bool(self._records) and not self.orphans()

    def coverage(self) -> float:
        """The fraction of measured subjects whose linkage closes entirely."""
        if not self._records:
            return 0.0
        closed = sum(1 for r in self.records() if r.complete)
        return round(closed / len(self._records), 4)

    def missing_by_dimension(self) -> dict[str, int]:
        """How many subjects leave each dimension open — where the gap actually is."""
        counts = {dimension: 0 for dimension in self.dimensions}
        for record in self.records():
            for dimension in record.missing:
                counts[dimension] = counts.get(dimension, 0) + 1
        return dict(sorted(counts.items()))

    def count(self) -> int:
        return len(self._records)

    def digest(self) -> str:
        return payload_digest([r.to_dict() for r in self.records()])

    # -- projection ------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        return {
            "engine": "LinkageEngine",
            "dimensions": list(self.dimensions),
            "counts": {
                "measured": self.count(),
                "complete": self.count() - len(self.orphans()),
                "orphans": len(self.orphans()),
            },
            "coverage": self.coverage(),
            "missing_by_dimension": self.missing_by_dimension(),
            "digest": self.digest(),
            "orphans": [r.to_dict() for r in self.orphans()],
        }


__all__ = ["LinkageEngine"]
