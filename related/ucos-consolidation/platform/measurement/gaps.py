"""UCOS-EPIC-004 — Gap Engine (UCOS-UMA-001).

Detects and classifies gaps in the Registry population — the deterministic "what is
missing or inconsistent" measurement. Gaps fall into two bands:

    Structural gaps (referential-integrity defects in Truth):
        * ``unknown-volume``        — an artifact placed in a volume Truth does not record.
        * ``unknown-parent``        — an artifact whose parent is not a recorded artifact.
        * ``dangling-edge``         — a relationship endpoint (``UCOS-*``) with no artifact.
        * ``volume-count-mismatch`` — a volume whose declared count ≠ artifacts placed.

    Completeness gaps (recorded but incomplete):
        * ``incomplete-traceability`` — an artifact missing ≥1 of the 13 trace stages.
        * ``unassigned-owner``        — an artifact with no assigned owner.
        * ``isolated-artifact``       — an artifact participating in no relationship.

The engine **reports** gaps; it never repairs Truth and never fabricates a fact to close
one. The result :class:`GapReport` is immutable, content-addressed, and a pure function
of the :class:`~platform.measurement.source.TruthSnapshot` (IMP-007 §5).
"""

from __future__ import annotations

from dataclasses import dataclass
from platform.foundation.contracts import content_hash
from platform.measurement.contracts import Measurement, MeasurementKind
from platform.measurement.errors import GapMeasurementError
from platform.measurement.source import TruthSnapshot
from typing import Any

from engine.registry.models import TRACE_STAGES

# Structural (referential-integrity) gap types.
UNKNOWN_VOLUME = "unknown-volume"
UNKNOWN_PARENT = "unknown-parent"
DANGLING_EDGE = "dangling-edge"
VOLUME_COUNT_MISMATCH = "volume-count-mismatch"

# Completeness gap types.
INCOMPLETE_TRACEABILITY = "incomplete-traceability"
UNASSIGNED_OWNER = "unassigned-owner"
ISOLATED_ARTIFACT = "isolated-artifact"

STRUCTURAL_GAP_TYPES: tuple[str, ...] = (
    UNKNOWN_VOLUME,
    UNKNOWN_PARENT,
    DANGLING_EDGE,
    VOLUME_COUNT_MISMATCH,
)
COMPLETENESS_GAP_TYPES: tuple[str, ...] = (
    INCOMPLETE_TRACEABILITY,
    UNASSIGNED_OWNER,
    ISOLATED_ARTIFACT,
)

#: The sentinel owner value the Registry uses for an unassigned artifact.
_UNASSIGNED = "UNASSIGNED"


@dataclass(frozen=True, slots=True)
class Gap:
    """An immutable, content-addressed gap finding about Registry Truth."""

    gap_type: str
    subject: str
    detail: str = ""
    gap_id: str = ""

    @classmethod
    def create(cls, gap_type: str, subject: str, detail: str = "") -> Gap:
        if gap_type not in STRUCTURAL_GAP_TYPES and gap_type not in COMPLETENESS_GAP_TYPES:
            raise GapMeasurementError("unknown gap type", gap_type=gap_type)
        if not isinstance(subject, str) or not subject.strip():
            raise GapMeasurementError("gap subject must be a non-empty string", gap_type=gap_type)
        core = {"gap_type": gap_type, "subject": subject, "detail": detail}
        return cls(
            gap_type=gap_type,
            subject=subject,
            detail=detail,
            gap_id=f"UCOS-UMAG-{content_hash(core)[:16]}",
        )

    @property
    def structural(self) -> bool:
        return self.gap_type in STRUCTURAL_GAP_TYPES

    def to_dict(self) -> dict[str, Any]:
        return {
            "gap_id": self.gap_id,
            "gap_type": self.gap_type,
            "subject": self.subject,
            "detail": self.detail,
            "band": "structural" if self.structural else "completeness",
        }


@dataclass(frozen=True, slots=True)
class GapReport:
    """An immutable, content-addressed report of all gaps found in Registry Truth."""

    gaps: tuple[Gap, ...]
    structural_count: int
    completeness_count: int
    by_type: dict[str, int]
    report_id: str = ""

    @classmethod
    def create(cls, gaps: tuple[Gap, ...]) -> GapReport:
        ordered = tuple(sorted(gaps, key=lambda g: (g.gap_type, g.subject)))
        structural = sum(1 for g in ordered if g.structural)
        by_type: dict[str, int] = {}
        for gap in ordered:
            by_type[gap.gap_type] = by_type.get(gap.gap_type, 0) + 1
        by_type = {k: by_type[k] for k in sorted(by_type)}
        core = {
            "gaps": [g.to_dict() for g in ordered],
            "structural_count": structural,
            "completeness_count": len(ordered) - structural,
            "by_type": by_type,
        }
        return cls(
            gaps=ordered,
            structural_count=structural,
            completeness_count=len(ordered) - structural,
            by_type=by_type,
            report_id=f"UCOS-UMAGR-{content_hash(core)[:16]}",
        )

    def __len__(self) -> int:
        return len(self.gaps)

    @property
    def total(self) -> int:
        return len(self.gaps)

    @property
    def clean(self) -> bool:
        """True iff no structural gap exists (Truth is referentially consistent)."""
        return self.structural_count == 0

    def of_type(self, gap_type: str) -> tuple[Gap, ...]:
        return tuple(g for g in self.gaps if g.gap_type == gap_type)

    def to_dict(self) -> dict[str, Any]:
        return {
            "report_id": self.report_id,
            "total": self.total,
            "structural_count": self.structural_count,
            "completeness_count": self.completeness_count,
            "by_type": dict(self.by_type),
            "gaps": [g.to_dict() for g in self.gaps],
        }

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())

    def as_measurement(self) -> Measurement:
        """Wrap the gap report as a recordable :class:`Measurement`."""
        return Measurement.create(
            MeasurementKind.GAP,
            "registry.gaps",
            summary=(
                f"{self.total} gaps ({self.structural_count} structural, "
                f"{self.completeness_count} completeness)"
            ),
            payload=self.to_dict(),
        )


class GapEngine:
    """Deterministically detects gaps in the Registry population from a Truth snapshot."""

    __slots__ = ("_snapshot",)

    def __init__(self, snapshot: TruthSnapshot) -> None:
        if not isinstance(snapshot, TruthSnapshot):
            raise GapMeasurementError("GapEngine requires a TruthSnapshot")
        self._snapshot = snapshot

    def detect(self) -> GapReport:
        """Detect every structural and completeness gap (pure, deterministic)."""
        snap = self._snapshot
        artifact_ids = snap.artifact_ids()
        volume_ids = snap.volume_ids()
        gaps: list[Gap] = []

        # Artifacts that participate in at least one relationship (for isolation checks).
        connected: set[str] = set()
        for rel in snap.relationships:
            connected.add(rel.source)
            connected.add(rel.target)
            for endpoint in (rel.source, rel.target):
                if endpoint.startswith("UCOS-") and endpoint not in artifact_ids:
                    gaps.append(
                        Gap.create(
                            DANGLING_EDGE,
                            endpoint,
                            detail=f"edge {rel.edge_id} ({rel.type}) references a missing artifact",
                        )
                    )

        placed: dict[str, int] = {}
        for artifact in snap.artifacts:
            uid = artifact.universal_id
            placed[artifact.volume] = placed.get(artifact.volume, 0) + 1
            if artifact.volume and artifact.volume not in volume_ids:
                gaps.append(
                    Gap.create(
                        UNKNOWN_VOLUME, uid, detail=f"volume '{artifact.volume}' not recorded"
                    )
                )
            if artifact.parent and artifact.parent not in artifact_ids:
                gaps.append(
                    Gap.create(
                        UNKNOWN_PARENT, uid, detail=f"parent '{artifact.parent}' not recorded"
                    )
                )
            missing_stages = tuple(
                stage for stage in TRACE_STAGES if not artifact.traceability.stage(stage)
            )
            if missing_stages:
                gaps.append(
                    Gap.create(
                        INCOMPLETE_TRACEABILITY,
                        uid,
                        detail=f"missing stages: {', '.join(missing_stages)}",
                    )
                )
            if not artifact.owner or artifact.owner == _UNASSIGNED:
                gaps.append(Gap.create(UNASSIGNED_OWNER, uid, detail="no owner assigned"))
            if uid not in connected:
                gaps.append(Gap.create(ISOLATED_ARTIFACT, uid, detail="no relationships"))

        for volume in snap.volumes:
            actual = placed.get(volume.volume_id, 0)
            if actual != volume.artifact_count:
                gaps.append(
                    Gap.create(
                        VOLUME_COUNT_MISMATCH,
                        volume.volume_id,
                        detail=f"declared {volume.artifact_count}, placed {actual}",
                    )
                )
        return GapReport.create(tuple(gaps))


__all__ = [
    "Gap",
    "GapReport",
    "GapEngine",
    "STRUCTURAL_GAP_TYPES",
    "COMPLETENESS_GAP_TYPES",
    "UNKNOWN_VOLUME",
    "UNKNOWN_PARENT",
    "DANGLING_EDGE",
    "VOLUME_COUNT_MISMATCH",
    "INCOMPLETE_TRACEABILITY",
    "UNASSIGNED_OWNER",
    "ISOLATED_ARTIFACT",
]
