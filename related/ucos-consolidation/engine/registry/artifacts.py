"""TASK-000012 — Artifact repository (EPIC-002, read-only).

An in-memory, read-only index over ``00-BOOK/DATA/artifacts.json``. The repository
parses each record into an :class:`Artifact` (TASK-000011) once and exposes
deterministic lookups and filters. It never writes to the corpus (DP-03) and
holds only immutable value objects.

Lookups are O(1) by ``universal_id`` and by ``native_id``; list/filter operations
return new tuples in stable registry order, so callers cannot mutate internal state.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

from engine.registry.errors import ArtifactNotFoundError, RegistryValidationError
from engine.registry.models import Artifact, LifecycleStatus
from engine.registry.source import ARTIFACTS_FILE, RegistrySource


class ArtifactRepository:
    """Read-only repository of Universal Artifacts."""

    __slots__ = ("_artifacts", "_by_uid", "_by_native")

    def __init__(self, artifacts: Iterable[Artifact]) -> None:
        self._artifacts: tuple[Artifact, ...] = tuple(artifacts)
        by_uid: dict[str, Artifact] = {}
        by_native: dict[str, Artifact] = {}
        for artifact in self._artifacts:
            if artifact.universal_id in by_uid:
                raise RegistryValidationError(
                    "duplicate universal_id in artifact registry",
                    universal_id=artifact.universal_id,
                )
            by_uid[artifact.universal_id] = artifact
            if artifact.native_id:
                # native_id is not guaranteed unique across the corpus; keep the
                # first occurrence and do not fail (READ-only, forgiving lookups).
                by_native.setdefault(artifact.native_id, artifact)
        self._by_uid = by_uid
        self._by_native = by_native

    # -- construction ----------------------------------------------------------

    @classmethod
    def from_source(cls, source: RegistrySource) -> ArtifactRepository:
        """Build the repository from the read-only registry source."""
        _envelope, records = source.read_document(ARTIFACTS_FILE, root_key="artifacts")
        return cls(Artifact.from_dict(record) for record in records)

    # -- size / iteration ------------------------------------------------------

    def __len__(self) -> int:
        return len(self._artifacts)

    def __iter__(self):
        return iter(self._artifacts)

    def count(self) -> int:
        """Total number of registered artifacts."""
        return len(self._artifacts)

    def all(self) -> tuple[Artifact, ...]:
        """Every artifact in stable registry order."""
        return self._artifacts

    # -- lookups ---------------------------------------------------------------

    def get(self, universal_id: str) -> Artifact:
        """Return the artifact with ``universal_id`` or raise if absent."""
        try:
            return self._by_uid[universal_id]
        except KeyError as exc:
            raise ArtifactNotFoundError(
                "no artifact with that universal_id", universal_id=universal_id
            ) from exc

    def find(self, universal_id: str) -> Artifact | None:
        """Return the artifact with ``universal_id`` or ``None`` if absent."""
        return self._by_uid.get(universal_id)

    def exists(self, universal_id: str) -> bool:
        """True iff an artifact with ``universal_id`` is registered."""
        return universal_id in self._by_uid

    def by_native_id(self, native_id: str) -> Artifact | None:
        """Return the first artifact carrying ``native_id`` or ``None``."""
        return self._by_native.get(native_id)

    # -- filters ---------------------------------------------------------------

    def by_category(self, category: str) -> tuple[Artifact, ...]:
        """All artifacts whose provenance ``category`` matches (case-insensitive)."""
        needle = category.upper()
        return tuple(a for a in self._artifacts if a.category.upper() == needle)

    def by_program(self, program: str) -> tuple[Artifact, ...]:
        """All artifacts belonging to ``program`` (case-insensitive)."""
        needle = program.upper()
        return tuple(a for a in self._artifacts if a.program.upper() == needle)

    def by_volume(self, volume_id: str) -> tuple[Artifact, ...]:
        """All artifacts placed in ``volume_id``."""
        return tuple(a for a in self._artifacts if a.volume == volume_id)

    def by_status(self, status: LifecycleStatus | str) -> tuple[Artifact, ...]:
        """All artifacts in the given lifecycle ``status``."""
        wanted = (
            status
            if isinstance(status, LifecycleStatus)
            else LifecycleStatus.coerce(status, context="filter")
        )
        return tuple(a for a in self._artifacts if a.status is wanted)

    def children_of(self, universal_id: str) -> tuple[Artifact, ...]:
        """All artifacts whose ``parent`` is ``universal_id``."""
        return tuple(a for a in self._artifacts if a.parent == universal_id)

    def filter(self, **criteria: Any) -> tuple[Artifact, ...]:
        """Return artifacts matching all provided attribute ``criteria``.

        Recognised keys: ``category``, ``program``, ``volume``, ``status``,
        ``owner``, ``parent``. ``status`` accepts an enum member or its string.
        Unknown keys raise a validation error (fail loud, no silent no-ops).
        """
        allowed = {"category", "program", "volume", "status", "owner", "parent"}
        unknown = set(criteria) - allowed
        if unknown:
            raise RegistryValidationError(
                "unknown filter criteria", keys=sorted(unknown), allowed=sorted(allowed)
            )
        result = self._artifacts
        if "category" in criteria:
            result = tuple(a for a in result if a.category == criteria["category"])
        if "program" in criteria:
            result = tuple(a for a in result if a.program == criteria["program"])
        if "volume" in criteria:
            result = tuple(a for a in result if a.volume == criteria["volume"])
        if "owner" in criteria:
            result = tuple(a for a in result if a.owner == criteria["owner"])
        if "parent" in criteria:
            result = tuple(a for a in result if a.parent == criteria["parent"])
        if "status" in criteria:
            wanted = criteria["status"]
            wanted = (
                wanted
                if isinstance(wanted, LifecycleStatus)
                else LifecycleStatus.coerce(wanted, context="filter")
            )
            result = tuple(a for a in result if a.status is wanted)
        return result

    # -- aggregate views -------------------------------------------------------

    def categories(self) -> tuple[str, ...]:
        """Distinct categories present, ordered."""
        return tuple(sorted({a.category for a in self._artifacts if a.category}))

    def programs(self) -> tuple[str, ...]:
        """Distinct programs present, ordered."""
        return tuple(sorted({a.program for a in self._artifacts if a.program}))

    def status_counts(self) -> Mapping[str, int]:
        """Count of artifacts per lifecycle status (ordered by status value)."""
        counts: dict[str, int] = {}
        for artifact in self._artifacts:
            counts[artifact.status.value] = counts.get(artifact.status.value, 0) + 1
        return dict(sorted(counts.items()))


__all__ = ["ArtifactRepository"]
