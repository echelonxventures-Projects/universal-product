"""TASK-000021 — Dependency Resolution Engine (EPIC-003, IMP-007 §4).

Given a *build set* of parsed blueprint IRs, the resolver builds the blueprint
dependency graph, verifies every declared dependency resolves to a blueprint in
the set, guarantees the graph is **acyclic** (delegating to TASK-000022; a cycle
fails the build — AR-01), and produces a deterministic **compile order** in which
every blueprint's dependencies precede it.

Dependency versions are **exact/pinned** (IMP-007 §4/§5): the resolver records the
declared version of every blueprint and rejects duplicate blueprint ids, so a
build has one pinned version per id and reproduces byte-identically.

Resolution is read-only and stdlib-only; it invents no dependency edges (TP-01).
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from engine.compiler.cycles import assert_acyclic, topological_order
from engine.compiler.errors import DependencyError
from engine.compiler.ir import BlueprintIR
from engine.foundation.obs.logging import get_logger
from engine.foundation.obs.telemetry import trace

_logger = get_logger("compiler.resolver")


@dataclass(frozen=True, slots=True)
class ResolvedBuild:
    """The resolved, acyclic build plan for a set of blueprints."""

    order: tuple[str, ...]
    graph: dict[str, tuple[str, ...]]
    pinned_versions: dict[str, str]

    def dependencies_of(self, blueprint_id: str) -> tuple[str, ...]:
        """Return the direct dependencies of ``blueprint_id``."""
        return self.graph.get(blueprint_id, ())

    def __len__(self) -> int:
        return len(self.order)


class DependencyResolver:
    """Resolves blueprint dependencies into a deterministic, acyclic build plan."""

    __slots__ = ()

    def resolve(self, blueprints: Iterable[BlueprintIR]) -> ResolvedBuild:
        """Resolve ``blueprints`` into a :class:`ResolvedBuild` or raise."""
        with trace("compiler.resolve"):
            by_id: dict[str, BlueprintIR] = {}
            for ir in blueprints:
                if ir.blueprint_id in by_id:
                    raise DependencyError(
                        "duplicate blueprint id in build set",
                        blueprint_id=ir.blueprint_id,
                    )
                by_id[ir.blueprint_id] = ir

            graph: dict[str, tuple[str, ...]] = {}
            pinned: dict[str, str] = {}
            for blueprint_id, ir in by_id.items():
                pinned[blueprint_id] = ir.version
                for dep in ir.dependencies:
                    if dep not in by_id:
                        raise DependencyError(
                            "declared dependency is missing from the build set",
                            blueprint_id=blueprint_id,
                            dependency=dep,
                        )
                graph[blueprint_id] = tuple(ir.dependencies)

            # Cycle detection: a circular dependency fails the build (IMP-007 §17).
            assert_acyclic(graph)
            order = topological_order(graph)

        _logger.info(
            "compiler.build.resolved",
            blueprints=len(by_id),
            edges=sum(len(deps) for deps in graph.values()),
        )
        return ResolvedBuild(order=order, graph=dict(graph), pinned_versions=pinned)


__all__ = ["ResolvedBuild", "DependencyResolver"]
