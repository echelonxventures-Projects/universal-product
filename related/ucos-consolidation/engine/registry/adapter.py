"""TASK-000015 — Unified Registry Adapter facade (EPIC-002, read-only).

A single, Foundation-contract-compliant entry point over the ``00-BOOK`` registry
substrate. The adapter composes the read-only source (TASK-000010), artifact
repository (TASK-000012), relationship graph (TASK-000013), and volume repository
+ integrity views (TASK-000014).

Foundation compliance:
    * AR-03 / PL-05 — the adapter publishes a versioned :class:`Contract`
      (``registry.read`` v1.0.0) via the Foundation :class:`ContractRegistry`, so
      all inter-module interaction crosses a documented, semantically versioned
      interface.
    * DP-03 — strictly read-only; the source guards against corpus writes.
    * PL-02 — loading is wrapped in Foundation telemetry spans (TASK-000007) and
      emits structured logs (TASK-000006).

Loading is lazy and memoised: the three data files are parsed on first access and
reused thereafter, so the adapter is cheap to construct and idempotent to query.
"""

from __future__ import annotations

from engine.foundation.contracts.contract import Contract, ContractRegistry, Version
from engine.foundation.obs.logging import get_logger
from engine.foundation.obs.telemetry import trace
from engine.registry.artifacts import ArtifactRepository
from engine.registry.graph import RelationshipGraph
from engine.registry.source import RegistrySource
from engine.registry.volumes import IntegrityReport, VolumeRepository, check_integrity

#: The versioned contract this adapter satisfies (AR-03, PL-05).
REGISTRY_READ_CONTRACT = Contract(
    name="registry.read",
    version=Version(1, 0, 0),
    description=(
        "Read-only access to the 00-BOOK registry substrate: artifacts, "
        "relationships, and volumes, plus referential-integrity views."
    ),
)

_logger = get_logger("registry.adapter")


class RegistryAdapter:
    """Read-only facade over the certified 00-BOOK registry substrate."""

    __slots__ = ("_source", "_artifacts", "_graph", "_volumes")

    def __init__(self, source: RegistrySource | None = None) -> None:
        self._source = source if source is not None else RegistrySource()
        self._artifacts: ArtifactRepository | None = None
        self._graph: RelationshipGraph | None = None
        self._volumes: VolumeRepository | None = None

    # -- construction ----------------------------------------------------------

    @classmethod
    def open(cls, data_dir=None) -> RegistryAdapter:
        """Open the adapter over ``data_dir`` (defaults to ``00-BOOK/DATA``)."""
        return cls(RegistrySource(data_dir))

    @property
    def source(self) -> RegistrySource:
        """The underlying read-only registry source."""
        return self._source

    @property
    def contract(self) -> Contract:
        """The versioned interface contract this adapter satisfies (AR-03)."""
        return REGISTRY_READ_CONTRACT

    def register_contract(self, registry: ContractRegistry) -> None:
        """Publish this adapter's contract into a Foundation contract registry."""
        registry.register(REGISTRY_READ_CONTRACT)

    # -- lazy, memoised sub-registries ----------------------------------------

    @property
    def artifacts(self) -> ArtifactRepository:
        """The artifact repository (parsed on first access)."""
        if self._artifacts is None:
            with trace("registry.load.artifacts"):
                self._artifacts = ArtifactRepository.from_source(self._source)
            _logger.info("registry.artifacts.loaded", count=self._artifacts.count())
        return self._artifacts

    @property
    def graph(self) -> RelationshipGraph:
        """The relationship graph (parsed on first access)."""
        if self._graph is None:
            with trace("registry.load.relationships"):
                self._graph = RelationshipGraph.from_source(self._source)
            _logger.info("registry.relationships.loaded", count=self._graph.count())
        return self._graph

    @property
    def volumes(self) -> VolumeRepository:
        """The volume repository (parsed on first access)."""
        if self._volumes is None:
            with trace("registry.load.volumes"):
                self._volumes = VolumeRepository.from_source(self._source)
            _logger.info("registry.volumes.loaded", count=self._volumes.count())
        return self._volumes

    # -- convenience delegations ----------------------------------------------

    def artifact(self, universal_id: str):
        """Return the artifact with ``universal_id`` (raises if absent)."""
        return self.artifacts.get(universal_id)

    def volume(self, volume_id: str):
        """Return the volume with ``volume_id`` (raises if absent)."""
        return self.volumes.get(volume_id)

    def artifacts_in_volume(self, volume_id: str):
        """All artifacts placed in ``volume_id`` (validates the volume exists)."""
        self.volumes.get(volume_id)  # raise VolumeNotFoundError if unknown
        return self.artifacts.by_volume(volume_id)

    def integrity(self) -> IntegrityReport:
        """Cross-reference the substrate and return a read-only integrity report."""
        with trace("registry.integrity"):
            return check_integrity(self.artifacts, self.graph, self.volumes)

    def load_all(self) -> None:
        """Eagerly parse all three data files (artifacts, relationships, volumes)."""
        _ = (self.artifacts, self.graph, self.volumes)

    def summary(self) -> dict[str, int]:
        """A small, loggable summary of substrate sizes."""
        return {
            "artifacts": self.artifacts.count(),
            "relationships": self.graph.count(),
            "volumes": self.volumes.count(),
        }


__all__ = ["RegistryAdapter", "REGISTRY_READ_CONTRACT"]
