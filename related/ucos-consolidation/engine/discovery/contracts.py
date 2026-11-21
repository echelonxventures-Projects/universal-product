"""UCOS-EPIC-003 — Universal Discovery Engine contracts.

The value types that flow across the Universal Discovery boundary. Every type here
is **immutable, typed, deterministic, and serializable** and holds **no runtime
state** (no store handles, no wall-clock): identical registry substrates yield
identical, byte-reproducible discovery results (IMP-007 §5).

    * :class:`DiscoveryKind` — the eight universal discovery dimensions.
    * :class:`DiscoveredItem` — a single thing discovered in the registry.
    * :class:`DimensionCoverage` — the completeness of one dimension (discovered vs
      total in registry scope).
    * :class:`DimensionResult` — the ordered items + coverage for one dimension.
    * :class:`CoverageReport` — the aggregate coverage surface across dimensions.
    * :class:`DiscoveryReport` — the content-addressed, immutable universal
      discovery result across all dimensions.

The engine invents nothing (TP-01): every discovered item is grounded in a registry
record. Discovery is **registry-driven** — there are no hard-coded path/name
patterns, no regex over content, and no filesystem walking; the substrate is the
single source of truth. The public capability is published through the versioned
:data:`DISCOVERY_CONTRACT` (AR-03 / PL-05).
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from engine.discovery.errors import DiscoveryDimensionError
from engine.foundation.contracts.contract import Contract, Version

# The canonical serialization primitive has exactly one definition, in UCKP Layer Zero
# (UCKP-LAW-0001 Art-13, UCKP-INV-03). Re-exported unchanged for existing callers.
from engine.uckp.canonical import canonical_json, content_hash

#: The semantic version of the discovery contract surface (AR-03/PL-05).
DISCOVERY_CONTRACT_VERSION = "1.0.0"


class DiscoveryKind(str, Enum):
    """The eight universal discovery dimensions (UCOS-EPIC-003).

    Every dimension is discovered *from the registry substrate* — never from
    hard-coded patterns, regex, or a filesystem walk:

        * ``NAMESPACE``  — the registry's organising namespaces (volumes,
          categories, programs).
        * ``DOCUMENT``   — every registered artifact as an addressable document.
        * ``REGISTRY``   — the registries themselves (artifacts / relationships /
          volumes) and their sizes.
        * ``COMPONENT``  — every registered artifact as a lifecycle component.
        * ``DEPENDENCY`` — the dependency relations (graph ``Depends-On`` edges plus
          declared dependency arrays).
        * ``EVIDENCE``   — the evidence each artifact carries (content hash,
          traceability chain).
        * ``ONTOLOGY``   — the knowledge-graph vocabulary (relationship types,
          categories, lifecycle statuses).
        * ``CAPABILITY`` — the capabilities the corpus provides (programs and their
          realisation profile).
    """

    NAMESPACE = "namespace"
    DOCUMENT = "document"
    REGISTRY = "registry"
    COMPONENT = "component"
    DEPENDENCY = "dependency"
    EVIDENCE = "evidence"
    ONTOLOGY = "ontology"
    CAPABILITY = "capability"

    @classmethod
    def coerce(cls, value: Any) -> DiscoveryKind:
        """Return the enum member for ``value`` or raise a discovery error."""
        if isinstance(value, cls):
            return value
        try:
            return cls(str(value))
        except ValueError as exc:
            raise DiscoveryDimensionError(
                "unknown discovery dimension",
                value=value,
                known=[k.value for k in cls],
            ) from exc


#: The eight dimensions in stable, canonical order (for deterministic iteration).
DISCOVERY_DIMENSIONS: tuple[DiscoveryKind, ...] = tuple(DiscoveryKind)


@dataclass(frozen=True, slots=True)
class DiscoveredItem:
    """A single, registry-grounded thing discovered in one dimension.

    ``attributes`` holds dimension-specific, JSON-serializable facts drawn verbatim
    from the registry; ``references`` are the ids of related registry entities. The
    item is fully deterministic: identical registry records yield an identical item.
    """

    kind: DiscoveryKind
    item_id: str
    name: str
    source: str
    attributes: Mapping[str, Any] = field(default_factory=dict)
    references: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": self.kind.value,
            "item_id": self.item_id,
            "name": self.name,
            "source": self.source,
            "attributes": dict(self.attributes),
            "references": list(self.references),
        }


@dataclass(frozen=True, slots=True)
class DimensionCoverage:
    """The completeness of one discovery dimension over the registry scope.

    ``discovered`` is the number of in-scope registry entities the engine resolved;
    ``total`` is the number in scope. Coverage is complete iff every in-scope entity
    was discovered — a shortfall marks a referential gap in the substrate (e.g. a
    dependency edge whose target is unknown), never a limitation of the engine.
    """

    kind: DiscoveryKind
    discovered: int
    total: int

    @property
    def complete(self) -> bool:
        """100% complete iff every in-scope entity was discovered (vacuously at 0)."""
        return self.discovered >= self.total

    @property
    def percent(self) -> float:
        return 100.0 if self.total == 0 else round(self.discovered / self.total * 100.0, 4)

    def to_dict(self) -> dict[str, Any]:
        return {
            "dimension": self.kind.value,
            "discovered": self.discovered,
            "total": self.total,
            "percent": self.percent,
            "complete": self.complete,
        }


@dataclass(frozen=True, slots=True)
class DimensionResult:
    """The ordered discovered items + coverage for a single dimension."""

    kind: DiscoveryKind
    items: tuple[DiscoveredItem, ...]
    coverage: DimensionCoverage
    gaps: tuple[str, ...] = ()

    def count(self) -> int:
        """Number of items discovered in this dimension."""
        return len(self.items)

    def item_ids(self) -> tuple[str, ...]:
        """Every discovered item id, in stable order."""
        return tuple(item.item_id for item in self.items)

    @property
    def complete(self) -> bool:
        """True iff the dimension's coverage is complete."""
        return self.coverage.complete

    def to_dict(self) -> dict[str, Any]:
        return {
            "dimension": self.kind.value,
            "count": self.count(),
            "coverage": self.coverage.to_dict(),
            "gaps": list(self.gaps),
            "items": [item.to_dict() for item in self.items],
        }


@dataclass(frozen=True, slots=True)
class CoverageReport:
    """The aggregate coverage surface across every discovery dimension."""

    coverages: tuple[DimensionCoverage, ...]

    def by_dimension(self) -> dict[str, DimensionCoverage]:
        return {c.kind.value: c for c in self.coverages}

    def incomplete_dimensions(self) -> tuple[str, ...]:
        return tuple(sorted(c.kind.value for c in self.coverages if not c.complete))

    @property
    def total_discovered(self) -> int:
        return sum(c.discovered for c in self.coverages)

    @property
    def total_scope(self) -> int:
        return sum(c.total for c in self.coverages)

    @property
    def complete(self) -> bool:
        """True iff every dimension is completely covered (universal discovery)."""
        return all(c.complete for c in self.coverages)

    @property
    def percent(self) -> float:
        total = self.total_scope
        return 100.0 if total == 0 else round(self.total_discovered / total * 100.0, 4)

    def to_dict(self) -> dict[str, Any]:
        return {
            "complete": self.complete,
            "percent": self.percent,
            "total_discovered": self.total_discovered,
            "total_scope": self.total_scope,
            "incomplete_dimensions": list(self.incomplete_dimensions()),
            "dimensions": [c.to_dict() for c in self.coverages],
        }


@dataclass(frozen=True, slots=True)
class DiscoveryReport:
    """The immutable, content-addressed universal discovery result (EPIC-003).

    Aggregates the per-dimension results into one deterministic report. The
    ``content_sha256`` is the canonical hash of the whole discovery, so two runs
    over an identical substrate produce a byte-identical, verifiable report.
    """

    engine_id: str
    substrate: Mapping[str, int]
    results: tuple[DimensionResult, ...]

    def by_dimension(self) -> dict[str, DimensionResult]:
        return {r.kind.value: r for r in self.results}

    def result(self, kind: DiscoveryKind | str) -> DimensionResult:
        """Return the result for a dimension or raise if it was not discovered."""
        wanted = DiscoveryKind.coerce(kind)
        for result in self.results:
            if result.kind is wanted:
                return result
        raise DiscoveryDimensionError("dimension not discovered", dimension=wanted.value)

    def coverage(self) -> CoverageReport:
        """The aggregate coverage report across every dimension."""
        return CoverageReport(coverages=tuple(r.coverage for r in self.results))

    def counts(self) -> dict[str, int]:
        """Per-dimension discovered-item counts (ordered by dimension)."""
        return {r.kind.value: r.count() for r in self.results}

    def total_items(self) -> int:
        return sum(r.count() for r in self.results)

    @property
    def complete(self) -> bool:
        """True iff discovery is universal — every dimension fully covered."""
        return self.coverage().complete

    def core(self) -> dict[str, Any]:
        """The canonical, hashable core of the report (excludes the content hash)."""
        return {
            "engine_id": self.engine_id,
            "substrate": dict(self.substrate),
            "results": [r.to_dict() for r in self.results],
        }

    def content_sha256(self) -> str:
        """The deterministic content hash of the discovery report."""
        return content_hash(self.core())

    def to_dict(self) -> dict[str, Any]:
        return {
            **self.core(),
            "coverage": self.coverage().to_dict(),
            "counts": self.counts(),
            "total_items": self.total_items(),
            "complete": self.complete,
            "content_sha256": self.content_sha256(),
        }


def build_coverage_report(results: Iterable[DimensionResult]) -> CoverageReport:
    """Assemble a :class:`CoverageReport` from an iterable of dimension results."""
    return CoverageReport(coverages=tuple(r.coverage for r in results))


#: The versioned public contract of the Universal Discovery Engine (AR-03 / PL-05).
DISCOVERY_CONTRACT = Contract(
    name="discovery.universal",
    version=Version(1, 0, 0),
    description=(
        "Universal, registry-driven, deterministic discovery over the 00-BOOK "
        "substrate across eight dimensions: namespace, document, registry, "
        "component, dependency, evidence, ontology, and capability. No hard-coded "
        "patterns; the registry is the single source of truth."
    ),
)


__all__ = [
    "DISCOVERY_CONTRACT_VERSION",
    "canonical_json",
    "content_hash",
    "DiscoveryKind",
    "DISCOVERY_DIMENSIONS",
    "DiscoveredItem",
    "DimensionCoverage",
    "DimensionResult",
    "CoverageReport",
    "DiscoveryReport",
    "build_coverage_report",
    "DISCOVERY_CONTRACT",
]
