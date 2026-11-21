"""UCOS-EPIC-003 — Universal Discovery Engine facade.

A single, Foundation-contract-compliant entry point that runs **registry-driven,
deterministic discovery** across all eight dimensions over the read-only registry
substrate (EPIC-002). The engine composes the pure per-dimension discoverers
(:mod:`engine.discovery.dimensions`) over a :class:`~engine.registry.RegistryAdapter`.

Foundation compliance:
    * AR-03 / PL-05 — the engine publishes a versioned :class:`Contract`
      (``discovery.universal`` v1.0.0) via the Foundation :class:`ContractRegistry`.
    * DP-03 — strictly read-only; it consumes the registry adapter, which guards
      against corpus writes, and never touches the filesystem itself.
    * PL-02 — discovery is wrapped in Foundation telemetry spans (TASK-000007) and
      emits structured logs (TASK-000006).
    * TP-01 / IMP-007 §5 — the engine invents nothing and holds no wall-clock or
      ambient state, so an identical substrate yields a byte-identical
      :class:`~engine.discovery.contracts.DiscoveryReport`.

Everything is registry driven: there are no hard-coded path/name patterns, no regex
over content, and no ``glob``/filesystem discovery anywhere in the engine.
"""

from __future__ import annotations

from collections.abc import Iterable

from engine.discovery.contracts import (
    DISCOVERY_CONTRACT,
    DimensionResult,
    DiscoveryKind,
    DiscoveryReport,
)
from engine.discovery.dimensions import (
    discover_capabilities,
    discover_components,
    discover_dependencies,
    discover_documents,
    discover_evidence,
    discover_namespaces,
    discover_ontology,
    discover_registries,
)
from engine.foundation.contracts.contract import Contract, ContractRegistry
from engine.foundation.obs.logging import get_logger
from engine.foundation.obs.telemetry import trace
from engine.registry.adapter import RegistryAdapter

#: The stable identity of the Universal Discovery Engine (embedded in evidence).
DISCOVERY_ENGINE_ID = "UCOS-DISCOVERY-ENGINE"

_logger = get_logger("discovery.engine")


class UniversalDiscoveryEngine:
    """Registry-driven, deterministic discovery across the eight universal dimensions."""

    __slots__ = ("_registry",)

    def __init__(self, registry: RegistryAdapter | None = None) -> None:
        self._registry = registry if registry is not None else RegistryAdapter()

    # -- construction ----------------------------------------------------------

    @classmethod
    def open(cls, data_dir=None) -> UniversalDiscoveryEngine:
        """Open the engine over ``data_dir`` (defaults to ``00-BOOK/DATA``)."""
        return cls(RegistryAdapter.open(data_dir))

    @property
    def registry(self) -> RegistryAdapter:
        """The underlying read-only registry adapter."""
        return self._registry

    @property
    def contract(self) -> Contract:
        """The versioned interface contract this engine satisfies (AR-03)."""
        return DISCOVERY_CONTRACT

    def register_contract(self, registry: ContractRegistry) -> None:
        """Publish this engine's contract into a Foundation contract registry."""
        registry.register(DISCOVERY_CONTRACT)

    # -- per-dimension discovery APIs -----------------------------------------

    def namespaces(self) -> DimensionResult:
        """Discover the registry's organising namespaces (volumes/categories/programs)."""
        with trace("discovery.namespace"):
            return discover_namespaces(self._registry.artifacts, self._registry.volumes)

    def documents(self) -> DimensionResult:
        """Discover every registered artifact as an addressable document."""
        with trace("discovery.document"):
            return discover_documents(self._registry.artifacts)

    def registries(self) -> DimensionResult:
        """Discover the registries themselves (artifacts/relationships/volumes)."""
        with trace("discovery.registry"):
            return discover_registries(
                self._registry.source,
                self._registry.artifacts,
                self._registry.graph,
                self._registry.volumes,
            )

    def components(self) -> DimensionResult:
        """Discover every registered artifact as a lifecycle component."""
        with trace("discovery.component"):
            return discover_components(self._registry.artifacts, self._registry.graph)

    def dependencies(self) -> DimensionResult:
        """Discover the dependency relations (graph edges + declared arrays)."""
        with trace("discovery.dependency"):
            return discover_dependencies(self._registry.artifacts, self._registry.graph)

    def evidence(self) -> DimensionResult:
        """Discover the evidence each artifact carries (content hash + traceability)."""
        with trace("discovery.evidence"):
            return discover_evidence(self._registry.artifacts)

    def ontology(self) -> DimensionResult:
        """Discover the knowledge-graph vocabulary (types/categories/statuses)."""
        with trace("discovery.ontology"):
            return discover_ontology(self._registry.artifacts, self._registry.graph)

    def capabilities(self) -> DimensionResult:
        """Discover the capabilities the corpus provides (programs + realisation)."""
        with trace("discovery.capability"):
            return discover_capabilities(self._registry.artifacts, self._registry.volumes)

    # -- dispatch --------------------------------------------------------------

    def discover_dimension(self, kind: DiscoveryKind | str) -> DimensionResult:
        """Discover a single dimension by :class:`DiscoveryKind` (or its value)."""
        wanted = DiscoveryKind.coerce(kind)
        dispatch = {
            DiscoveryKind.NAMESPACE: self.namespaces,
            DiscoveryKind.DOCUMENT: self.documents,
            DiscoveryKind.REGISTRY: self.registries,
            DiscoveryKind.COMPONENT: self.components,
            DiscoveryKind.DEPENDENCY: self.dependencies,
            DiscoveryKind.EVIDENCE: self.evidence,
            DiscoveryKind.ONTOLOGY: self.ontology,
            DiscoveryKind.CAPABILITY: self.capabilities,
        }
        return dispatch[wanted]()

    # -- universal discovery ---------------------------------------------------

    def _substrate(self) -> dict[str, int]:
        return self._registry.summary()

    def discover(self, dimensions: Iterable[DiscoveryKind | str] | None = None) -> DiscoveryReport:
        """Run universal discovery across all eight dimensions (or a subset).

        Returns an immutable, content-addressed :class:`DiscoveryReport`. Dimensions
        are always emitted in canonical :class:`DiscoveryKind` order so the report is
        deterministic regardless of the requested ordering.
        """
        wanted = (
            tuple(DiscoveryKind)
            if dimensions is None
            else tuple(dict.fromkeys(DiscoveryKind.coerce(d) for d in dimensions))
        )
        ordered = tuple(k for k in DiscoveryKind if k in set(wanted))
        with trace("discovery.universal"):
            results = tuple(self.discover_dimension(kind) for kind in ordered)
        report = DiscoveryReport(
            engine_id=DISCOVERY_ENGINE_ID,
            substrate=self._substrate(),
            results=results,
        )
        _logger.info(
            "discovery.completed",
            dimensions=len(results),
            total_items=report.total_items(),
            complete=report.complete,
            content_sha256=report.content_sha256(),
        )
        return report


__all__ = ["DISCOVERY_ENGINE_ID", "UniversalDiscoveryEngine"]
