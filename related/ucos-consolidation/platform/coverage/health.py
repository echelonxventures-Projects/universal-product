"""ZG-P-02 — Coverage health (Universe→Code Coverage Instrument).

Reuses the certified Observability health model (``HealthCheck``, ``HealthStatus``) — it
defines no new health machinery — and computes a deterministic probe over a coverage
graph + registry. Nine critical checks back G4 certification and operational health:

    Integrity (always fail-closed → UNHEALTHY on any violation):
        * ``orphan-universe``               — a universe with no downstream edge.
        * ``orphan-code``                   — code/module/asset/epic with no lineage to a universe.
        * ``duplicate-coverage``            — one logical edge recorded under multiple authorities.
        * ``coverage-fingerprint-mismatch`` — recomputed fingerprint ≠ recorded fingerprint.

    Completeness (gaps → UNHEALTHY under ``strict`` certification policy, else DEGRADED):
        * ``missing-universe-coverage``       — a universe not fully COVERED.
        * ``missing-program-coverage``        — a program not fully COVERED.
        * ``missing-implementation-coverage`` — an implementation not fully COVERED.
        * ``missing-module-coverage``         — a module not fully COVERED.
        * ``missing-runtime-evidence``        — a code asset with no runtime-asset child.

Probing is a pure function of the supplied graph/registry — no I/O, no wall-clock — so
the verdict is reproducible (IMP-007 §5).
"""

from __future__ import annotations

from platform.coverage.contracts import CoverageNodeKind, CoverageStatus
from platform.coverage.graph import CoverageGraph
from platform.coverage.registry import CoverageRegistry
from platform.observability.contracts import HealthStatus
from platform.observability.health import HealthCheck

# Integrity checks (fail-closed → UNHEALTHY on violation).
ORPHAN_UNIVERSE_CHECK = "orphan-universe"
ORPHAN_CODE_CHECK = "orphan-code"
DUPLICATE_COVERAGE_CHECK = "duplicate-coverage"
FINGERPRINT_CHECK = "coverage-fingerprint-mismatch"

# Completeness checks (UNHEALTHY under strict policy, DEGRADED otherwise).
MISSING_UNIVERSE_CHECK = "missing-universe-coverage"
MISSING_PROGRAM_CHECK = "missing-program-coverage"
MISSING_IMPLEMENTATION_CHECK = "missing-implementation-coverage"
MISSING_MODULE_CHECK = "missing-module-coverage"
MISSING_RUNTIME_CHECK = "missing-runtime-evidence"

_INTEGRITY_CHECKS = (
    ORPHAN_UNIVERSE_CHECK,
    ORPHAN_CODE_CHECK,
    DUPLICATE_COVERAGE_CHECK,
    FINGERPRINT_CHECK,
)

_COMPLETENESS_CHECKS = (
    MISSING_UNIVERSE_CHECK,
    MISSING_PROGRAM_CHECK,
    MISSING_IMPLEMENTATION_CHECK,
    MISSING_MODULE_CHECK,
    MISSING_RUNTIME_CHECK,
)

_MISSING_KIND: dict[str, CoverageNodeKind] = {
    MISSING_UNIVERSE_CHECK: CoverageNodeKind.UNIVERSE,
    MISSING_PROGRAM_CHECK: CoverageNodeKind.PROGRAM,
    MISSING_IMPLEMENTATION_CHECK: CoverageNodeKind.IMPLEMENTATION,
    MISSING_MODULE_CHECK: CoverageNodeKind.MODULE,
}


def coverage_health_checks() -> tuple[HealthCheck, ...]:
    """The nine coverage health checks (all critical), in stable order."""
    d = "critical coverage check"
    return (
        HealthCheck(ORPHAN_UNIVERSE_CHECK, critical=True, description=d),
        HealthCheck(ORPHAN_CODE_CHECK, critical=True, description=d),
        HealthCheck(DUPLICATE_COVERAGE_CHECK, critical=True, description=d),
        HealthCheck(FINGERPRINT_CHECK, critical=True, description=d),
        HealthCheck(MISSING_UNIVERSE_CHECK, critical=True, description=d),
        HealthCheck(MISSING_PROGRAM_CHECK, critical=True, description=d),
        HealthCheck(MISSING_IMPLEMENTATION_CHECK, critical=True, description=d),
        HealthCheck(MISSING_MODULE_CHECK, critical=True, description=d),
        HealthCheck(MISSING_RUNTIME_CHECK, critical=True, description=d),
    )


class CoverageHealth:
    """A deterministic health probe over a coverage graph + its registry."""

    __slots__ = ("_graph", "_registry")

    def __init__(self, graph: CoverageGraph, registry: CoverageRegistry) -> None:
        if not isinstance(graph, CoverageGraph):
            raise TypeError("a valid CoverageGraph is required")
        if not isinstance(registry, CoverageRegistry):
            raise TypeError("a valid CoverageRegistry is required")
        self._graph = graph
        self._registry = registry

    # -- fault surfaces ---------------------------------------------------------

    def orphan_universes(self) -> tuple[str, ...]:
        return tuple(n.ref for n in self._graph.orphan_universes())

    def orphan_code(self) -> tuple[str, ...]:
        return tuple(f"{n.kind.value}:{n.ref}" for n in self._graph.orphan_code())

    def duplicate_records(self) -> tuple[str, ...]:
        return self._registry.duplicate_edge_refs()

    def fingerprint_matches(self) -> bool:
        """True iff the graph rebuilt from the registry fingerprints identically."""
        try:
            return self._registry.graph().fingerprint() == self._graph.fingerprint()
        except Exception:  # pragma: no cover - fail-closed on any rebuild error
            return False

    def uncovered_of_kind(self, kind: CoverageNodeKind) -> tuple[str, ...]:
        return tuple(
            n.ref
            for n in self._graph.nodes_of_kind(kind)
            if self._graph.status_of(n.node_id) is not CoverageStatus.COVERED
        )

    def code_assets_without_runtime(self) -> tuple[str, ...]:
        """Code-asset nodes with no runtime-asset child (missing runtime evidence)."""
        missing: list[str] = []
        for node in self._graph.nodes_of_kind(CoverageNodeKind.CODE_ASSET):
            children = self._graph.children_of(node.node_id)
            has_runtime = any(
                self._graph.get(c).kind is CoverageNodeKind.RUNTIME_ASSET for c in children
            )
            if not has_runtime:
                missing.append(node.ref)
        return tuple(sorted(missing))

    # -- probe ------------------------------------------------------------------

    def probe(self, *, strict: bool = False) -> dict[str, HealthStatus]:
        """Compute the nine coverage health statuses (fail-closed).

        Integrity checks are UNHEALTHY on any violation. Completeness checks are
        UNHEALTHY under ``strict`` (certification) policy and DEGRADED otherwise when a
        gap exists at that tier; HEALTHY when the tier is fully covered.
        """
        gap_status = HealthStatus.UNHEALTHY if strict else HealthStatus.DEGRADED
        results: dict[str, HealthStatus] = {}

        results[ORPHAN_UNIVERSE_CHECK] = (
            HealthStatus.UNHEALTHY if self.orphan_universes() else HealthStatus.HEALTHY
        )
        results[ORPHAN_CODE_CHECK] = (
            HealthStatus.UNHEALTHY if self.orphan_code() else HealthStatus.HEALTHY
        )
        results[DUPLICATE_COVERAGE_CHECK] = (
            HealthStatus.UNHEALTHY if self.duplicate_records() else HealthStatus.HEALTHY
        )
        results[FINGERPRINT_CHECK] = (
            HealthStatus.HEALTHY if self.fingerprint_matches() else HealthStatus.UNHEALTHY
        )

        for check, kind in _MISSING_KIND.items():
            results[check] = gap_status if self.uncovered_of_kind(kind) else HealthStatus.HEALTHY
        results[MISSING_RUNTIME_CHECK] = (
            gap_status if self.code_assets_without_runtime() else HealthStatus.HEALTHY
        )
        return results

    @property
    def integrity_ok(self) -> bool:
        """True iff all four integrity checks are HEALTHY (no structural violation)."""
        probe = self.probe(strict=False)
        return all(probe[c] is HealthStatus.HEALTHY for c in _INTEGRITY_CHECKS)

    def healthy(self, *, strict: bool = False) -> bool:
        """True iff every check is HEALTHY under the chosen policy."""
        return all(s is HealthStatus.HEALTHY for s in self.probe(strict=strict).values())


__all__ = [
    "ORPHAN_UNIVERSE_CHECK",
    "ORPHAN_CODE_CHECK",
    "DUPLICATE_COVERAGE_CHECK",
    "FINGERPRINT_CHECK",
    "MISSING_UNIVERSE_CHECK",
    "MISSING_PROGRAM_CHECK",
    "MISSING_IMPLEMENTATION_CHECK",
    "MISSING_MODULE_CHECK",
    "MISSING_RUNTIME_CHECK",
    "coverage_health_checks",
    "CoverageHealth",
]
