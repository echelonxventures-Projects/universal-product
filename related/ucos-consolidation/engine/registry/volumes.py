"""TASK-000014 — Volume repository & integrity read views (EPIC-002, read-only).

An in-memory, read-only index over ``00-BOOK/DATA/volumes.json`` plus a small set
of *read-only* referential-integrity diagnostics that cross-reference the artifact
repository (TASK-000012) and relationship graph (TASK-000013).

Diagnostics are pure queries: they report anomalies (e.g. edges that point to
unknown artifacts, artifacts placed in unknown volumes) and never modify the
corpus (DP-03). They exist so downstream, read-only consumers can trust the
substrate without re-implementing the checks.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from engine.registry.artifacts import ArtifactRepository
from engine.registry.errors import VolumeNotFoundError
from engine.registry.graph import RelationshipGraph
from engine.registry.models import Volume
from engine.registry.source import VOLUMES_FILE, RegistrySource


class VolumeRepository:
    """Read-only repository of Universal Master Knowledge Book volumes."""

    __slots__ = ("_volumes", "_by_id")

    def __init__(self, volumes: Iterable[Volume]) -> None:
        self._volumes: tuple[Volume, ...] = tuple(volumes)
        self._by_id: dict[str, Volume] = {}
        for volume in self._volumes:
            self._by_id.setdefault(volume.volume_id, volume)

    @classmethod
    def from_source(cls, source: RegistrySource) -> VolumeRepository:
        """Build the repository from the read-only registry source."""
        _envelope, records = source.read_document(VOLUMES_FILE, root_key="volumes")
        return cls(Volume.from_dict(record) for record in records)

    def __len__(self) -> int:
        return len(self._volumes)

    def __iter__(self):
        return iter(self._volumes)

    def count(self) -> int:
        """Total number of registered volumes."""
        return len(self._volumes)

    def all(self) -> tuple[Volume, ...]:
        """Every volume in stable registry order."""
        return self._volumes

    def get(self, volume_id: str) -> Volume:
        """Return the volume with ``volume_id`` or raise if absent."""
        try:
            return self._by_id[volume_id]
        except KeyError as exc:
            raise VolumeNotFoundError("no volume with that volume_id", volume_id=volume_id) from exc

    def find(self, volume_id: str) -> Volume | None:
        """Return the volume with ``volume_id`` or ``None``."""
        return self._by_id.get(volume_id)

    def exists(self, volume_id: str) -> bool:
        """True iff a volume with ``volume_id`` is registered."""
        return volume_id in self._by_id

    def by_category(self, category: str) -> tuple[Volume, ...]:
        """All volumes whose primary ``category`` matches (case-insensitive)."""
        needle = category.upper()
        return tuple(v for v in self._volumes if v.category.upper() == needle)

    def ids(self) -> tuple[str, ...]:
        """Every volume id, ordered."""
        return tuple(sorted(self._by_id))


@dataclass(frozen=True, slots=True)
class IntegrityReport:
    """Read-only referential-integrity findings across the registry substrate."""

    dangling_edge_endpoints: tuple[str, ...]
    unknown_artifact_volumes: tuple[str, ...]
    unknown_parents: tuple[str, ...]
    volume_count_mismatches: tuple[str, ...]

    @property
    def is_consistent(self) -> bool:
        """True iff no integrity anomalies were found."""
        return not (
            self.dangling_edge_endpoints
            or self.unknown_artifact_volumes
            or self.unknown_parents
            or self.volume_count_mismatches
        )


def check_integrity(
    artifacts: ArtifactRepository,
    graph: RelationshipGraph,
    volumes: VolumeRepository,
) -> IntegrityReport:
    """Return a read-only :class:`IntegrityReport` cross-referencing the substrate.

    Findings (all reported, never raised):
        * ``dangling_edge_endpoints`` — edge endpoints (``UCOS-*`` ids) with no
          matching artifact record.
        * ``unknown_artifact_volumes`` — volumes referenced by an artifact but
          absent from the volume registry.
        * ``unknown_parents`` — artifact ``parent`` ids with no matching artifact.
        * ``volume_count_mismatches`` — volumes whose declared ``artifact_count``
          differs from the number of artifacts actually placed in them.
    """
    dangling: dict[str, None] = {}
    for edge in graph:
        for endpoint in (edge.source, edge.target):
            if endpoint.startswith("UCOS-") and not artifacts.exists(endpoint):
                dangling.setdefault(endpoint, None)

    unknown_volumes: dict[str, None] = {}
    unknown_parents: dict[str, None] = {}
    placed: dict[str, int] = {}
    for artifact in artifacts:
        placed[artifact.volume] = placed.get(artifact.volume, 0) + 1
        if artifact.volume and not volumes.exists(artifact.volume):
            unknown_volumes.setdefault(artifact.volume, None)
        if artifact.parent and not artifacts.exists(artifact.parent):
            unknown_parents.setdefault(artifact.parent, None)

    mismatches: list[str] = [
        volume.volume_id
        for volume in volumes
        if placed.get(volume.volume_id, 0) != volume.artifact_count
    ]

    return IntegrityReport(
        dangling_edge_endpoints=tuple(sorted(dangling)),
        unknown_artifact_volumes=tuple(sorted(unknown_volumes)),
        unknown_parents=tuple(sorted(unknown_parents)),
        volume_count_mismatches=tuple(sorted(mismatches)),
    )


__all__ = ["VolumeRepository", "IntegrityReport", "check_integrity"]
