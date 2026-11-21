"""UCOS-EPIC-004 — Truth sources (UCOS-UMA-001).

The Universal Measurement Engine measures **only** the authoritative Registry — never a
hardcoded population, never a fabricated fact. A :class:`TruthSource` produces an
immutable :class:`TruthSnapshot` (the artifacts, relationships, and volumes exactly as
the Registry records them). Two sources exist:

    * :class:`RegistryTruthSource` — a read-only projection of the certified ``00-BOOK``
      substrate via the certified :class:`~engine.registry.adapter.RegistryAdapter`
      (DP-03: the corpus is read-only to implementation).
    * :class:`InMemoryTruthSource` — an explicit snapshot built from Registry model
      objects (used to exercise the pure engines deterministically).

A :class:`TruthSnapshot` is immutable and **self-normalizing**: records are ordered by
their Registry identity, so the snapshot fingerprint is byte-identical across processes
for identical Truth. The snapshot is a *consumer* of Truth: it exposes only read views,
never a mutation path — Measurement SHALL never create Truth.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable
from dataclasses import dataclass
from platform.foundation.contracts import content_hash
from platform.measurement.errors import TruthSourceError
from typing import Any

from engine.registry.adapter import RegistryAdapter
from engine.registry.models import TRACE_STAGES, Artifact, Relationship, Volume


@dataclass(frozen=True, slots=True)
class TruthSnapshot:
    """An immutable, normalized, read-only projection of the Registry population.

    Holds the certified Registry value objects verbatim (:class:`Artifact`,
    :class:`Relationship`, :class:`Volume`) — all themselves frozen — ordered by their
    Registry identity so the snapshot is deterministic and content-addressable.
    """

    artifacts: tuple[Artifact, ...]
    relationships: tuple[Relationship, ...]
    volumes: tuple[Volume, ...]

    @classmethod
    def create(
        cls,
        artifacts: Iterable[Artifact],
        relationships: Iterable[Relationship],
        volumes: Iterable[Volume],
    ) -> TruthSnapshot:
        """Build a normalized snapshot: type-checked, ordered by Registry id (fail-closed)."""
        arts = tuple(artifacts)
        rels = tuple(relationships)
        vols = tuple(volumes)
        for art in arts:
            if not isinstance(art, Artifact):
                raise TruthSourceError("Truth artifacts must be Registry Artifact instances")
        for rel in rels:
            if not isinstance(rel, Relationship):
                raise TruthSourceError(
                    "Truth relationships must be Registry Relationship instances"
                )
        for vol in vols:
            if not isinstance(vol, Volume):
                raise TruthSourceError("Truth volumes must be Registry Volume instances")
        return cls(
            artifacts=tuple(sorted(arts, key=lambda a: a.universal_id)),
            relationships=tuple(sorted(rels, key=lambda r: r.edge_id)),
            volumes=tuple(sorted(vols, key=lambda v: v.volume_id)),
        )

    # -- read views (no mutation surface — Truth is consumed, never authored) ---

    @property
    def artifact_count(self) -> int:
        return len(self.artifacts)

    @property
    def relationship_count(self) -> int:
        return len(self.relationships)

    @property
    def volume_count(self) -> int:
        return len(self.volumes)

    def artifact_ids(self) -> frozenset[str]:
        """The set of universal ids present in Truth (for referential checks)."""
        return frozenset(a.universal_id for a in self.artifacts)

    def volume_ids(self) -> frozenset[str]:
        """The set of volume ids present in Truth."""
        return frozenset(v.volume_id for v in self.volumes)

    def to_dict(self) -> dict[str, Any]:
        """A deterministic, read-only projection of Truth for fingerprinting.

        Projects only the fields the engine measures; the projection is a faithful,
        lossless-for-measurement view and is never written back to the Registry.
        """
        return {
            "artifact_count": self.artifact_count,
            "relationship_count": self.relationship_count,
            "volume_count": self.volume_count,
            "artifacts": [
                {
                    "universal_id": a.universal_id,
                    "volume": a.volume,
                    "status": a.status.value,
                    "category": a.category,
                    "program": a.program,
                    "owner": a.owner,
                    "parent": a.parent,
                    "traceability": {
                        stage: list(a.traceability.stage(stage)) for stage in TRACE_STAGES
                    },
                }
                for a in self.artifacts
            ],
            "relationships": [
                {
                    "edge_id": r.edge_id,
                    "from": r.source,
                    "to": r.target,
                    "type": r.type,
                }
                for r in self.relationships
            ],
            "volumes": [
                {
                    "volume_id": v.volume_id,
                    "category": v.category,
                    "status": v.status.value,
                    "artifact_count": v.artifact_count,
                }
                for v in self.volumes
            ],
        }

    def fingerprint(self) -> str:
        """Deterministic fingerprint of the measured Truth projection."""
        return content_hash(self.to_dict())


class TruthSource(ABC):
    """Abstract source of Registry Truth. ``snapshot`` MUST be deterministic + read-only."""

    @abstractmethod
    def snapshot(self) -> TruthSnapshot:
        """Return the current Truth snapshot. Repeated calls over stable Truth match."""
        raise NotImplementedError  # pragma: no cover - abstract


class InMemoryTruthSource(TruthSource):
    """An explicit, in-memory Truth source (the deterministic test/fixture source)."""

    __slots__ = ("_snapshot",)

    def __init__(
        self,
        artifacts: Iterable[Artifact],
        relationships: Iterable[Relationship] = (),
        volumes: Iterable[Volume] = (),
    ) -> None:
        self._snapshot = TruthSnapshot.create(artifacts, relationships, volumes)

    def snapshot(self) -> TruthSnapshot:
        return self._snapshot


class RegistryTruthSource(TruthSource):
    """A read-only Truth source over the certified ``00-BOOK`` Registry substrate.

    Wraps the certified read-only :class:`~engine.registry.adapter.RegistryAdapter`; it
    only ever reads the corpus (DP-03) and holds no write path. Every ``snapshot`` is a
    faithful projection of the Registry as it stands.
    """

    __slots__ = ("_adapter",)

    def __init__(self, adapter: RegistryAdapter | None = None) -> None:
        if adapter is not None and not isinstance(adapter, RegistryAdapter):
            raise TruthSourceError("RegistryTruthSource requires a RegistryAdapter")
        self._adapter = adapter if adapter is not None else RegistryAdapter.open()

    @property
    def adapter(self) -> RegistryAdapter:
        return self._adapter

    def snapshot(self) -> TruthSnapshot:
        return TruthSnapshot.create(
            self._adapter.artifacts.all(),
            self._adapter.graph.all(),
            self._adapter.volumes.all(),
        )


__all__ = [
    "TruthSnapshot",
    "TruthSource",
    "InMemoryTruthSource",
    "RegistryTruthSource",
]
