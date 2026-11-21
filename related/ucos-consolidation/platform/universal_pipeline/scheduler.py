"""UAPF-000001 — the scheduler: dependency-safe wave assignment over execution units.

Where :class:`~platform.universal_pipeline.contracts.PipelinePlan` orders the *stages
within* one pipeline, this module orders *units across* pipelines. Both derive their order
from the same authority — :func:`engine.foundation.composition.derive_order` — so the
inside and the outside of a pipeline can never be ordered by two different rules.

Why a schedule is a value and not an action
-------------------------------------------
:class:`PipelineSchedule` is an immutable, fingerprinted value: it says what *may* run
concurrently, and it starts nothing. Separating the two matters because a schedule must be
comparable — a gate re-derives it and compares fingerprints to prove the order in force is
the order the declarations imply — and something that executes as a side effect of being
computed cannot be compared.

Waves and the critical path
---------------------------
A wave is the set of units whose declared dependencies are already satisfied, so every
member of a wave is mutually independent and safe to run in parallel
(``05-BATCH-GENERATION-RULES.md`` §4). The critical path is ranked by *transitive dependent
count*: the unit that most other units wait on is the one whose delay costs the most, which
is a property of the graph rather than of an estimate.

Determinism: ties break on the unit id, every traversal is sorted, and no wall-clock, RNG
or I/O is involved. Identical declarations therefore yield an identical schedule and an
identical fingerprint in every environment.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from platform.foundation.contracts import content_hash
from platform.universal_pipeline.dependencies import DependencyManager
from platform.universal_pipeline.errors import PipelineScheduleError
from platform.universal_pipeline.identity import Identity, mint
from typing import Any

from engine.foundation.composition import derive_order, get_strategy, unresolved_keys

#: The default scheduling strategy. ``parallel-waves`` because a schedule exists to
#: express the concurrency the declarations permit; a caller wanting a strict sequence
#: names ``dependency-order``. Both come from the one shared strategy registry.
DEFAULT_SCHEDULE_STRATEGY = "parallel-waves"


@dataclass(frozen=True, slots=True)
class PipelineSchedule:
    """An immutable, dependency-safe wave assignment over execution units."""

    strategy: str
    waves: tuple[tuple[int, str], ...]

    def __post_init__(self) -> None:
        if not isinstance(self.strategy, str) or not self.strategy:
            raise PipelineScheduleError("schedule strategy is required")
        if not isinstance(self.waves, tuple):
            raise PipelineScheduleError("schedule waves must be a tuple", strategy=self.strategy)

    @property
    def identity(self) -> Identity:
        return mint("schedule", self.strategy, self.fingerprint())

    @property
    def unit_ids(self) -> tuple[str, ...]:
        """The scheduled unit ids in execution order."""
        return tuple(unit_id for _wave, unit_id in self.waves)

    @property
    def wave_indices(self) -> tuple[int, ...]:
        """The distinct wave indices in ascending order."""
        return tuple(sorted({wave for wave, _unit_id in self.waves}))

    @property
    def wave_count(self) -> int:
        return len(self.wave_indices)

    @property
    def max_parallelism(self) -> int:
        """The widest wave — 0 for an empty schedule, which is a legitimate steady state."""
        if not self.waves:
            return 0
        return max(len(self.units_in_wave(wave)) for wave in self.wave_indices)

    def units_in_wave(self, wave: int) -> tuple[str, ...]:
        """The unit ids placed in ``wave``, sorted (deterministic)."""
        return tuple(sorted(unit_id for index, unit_id in self.waves if index == wave))

    def wave_of(self, unit_id: str) -> int:
        """The wave ``unit_id`` was placed in.

        Raises:
            PipelineScheduleError: if the unit is not in this schedule (fail-closed).
        """
        for wave, scheduled in self.waves:
            if scheduled == unit_id:
                return wave
        raise PipelineScheduleError("unit is not in this schedule", unit_id=unit_id)

    def to_dict(self) -> dict[str, Any]:
        return {
            "strategy": self.strategy,
            "unit_count": len(self.waves),
            "wave_count": self.wave_count,
            "max_parallelism": self.max_parallelism,
            "waves": [
                {"wave": wave, "units": list(self.units_in_wave(wave))}
                for wave in self.wave_indices
            ],
        }

    def fingerprint(self) -> str:
        """A deterministic content hash of the wave assignment."""
        return content_hash(
            {
                "strategy": self.strategy,
                "waves": [[wave, unit_id] for wave, unit_id in self.waves],
            }
        )


class PipelineScheduler:
    """Derives schedules from declared dependencies. Holds no state of its own.

    Stateless by construction: a scheduler that remembered a previous schedule would be a
    second place the order lives, and the order lives in the declarations.
    """

    __slots__ = ()

    def schedule(
        self,
        dependencies: DependencyManager,
        *,
        strategy: str = DEFAULT_SCHEDULE_STRATEGY,
    ) -> PipelineSchedule:
        """Derive the schedule of every node declared in ``dependencies``.

        Raises:
            PipelineScheduleError: if ``dependencies`` is not a
                :class:`~platform.universal_pipeline.dependencies.DependencyManager`.
            PipelineDependencyError: if an edge names an undeclared node, or the graph is
                cyclic — the dependency engine decides that, not this one.
        """
        if not isinstance(dependencies, DependencyManager):
            raise PipelineScheduleError("a schedule is derived from a DependencyManager")
        dependencies.validate()
        graph = {
            node_id: dependencies.dependencies_of(node_id) for node_id in dependencies.node_ids
        }
        return self.schedule_graph(graph, strategy=strategy)

    def schedule_graph(
        self,
        graph: Mapping[str, tuple[str, ...]],
        *,
        strategy: str = DEFAULT_SCHEDULE_STRATEGY,
    ) -> PipelineSchedule:
        """Derive the schedule of an already-resolved ``graph``.

        Raises:
            PipelineScheduleError: if the strategy is unregistered, an edge names a node
                absent from ``graph`` (closure honesty), or the graph is cyclic — naming
                the nodes no order could place.
        """
        if not isinstance(graph, Mapping):
            raise PipelineScheduleError("schedule graph must be a mapping")
        try:
            get_strategy(strategy)
        except KeyError as exc:
            raise PipelineScheduleError(
                "unregistered ordering strategy (extension is by registration)",
                strategy=strategy,
            ) from exc
        resolved = {str(node): tuple(sorted(edges)) for node, edges in graph.items()}
        missing = sorted({edge for edges in resolved.values() for edge in edges} - set(resolved))
        if missing:
            raise PipelineScheduleError(
                "schedule graph edge names an unknown node (closure honesty)",
                missing=missing,
            )
        ordering = derive_order(resolved, strategy=strategy)
        unresolved = unresolved_keys(resolved, ordering)
        if unresolved:
            raise PipelineScheduleError("schedule graph contains a cycle", unresolved=unresolved)
        return PipelineSchedule(
            strategy=strategy,
            waves=tuple((int(wave), key) for wave, key in ordering),
        )

    def critical_path(
        self, dependencies: DependencyManager, *, limit: int | None = None
    ) -> tuple[tuple[str, int], ...]:
        """``(unit id, transitive dependent count)`` ranked by widest impact.

        Ties break on the unit id so the ranking is total and reproducible. ``limit``
        truncates the ranking; ``None`` returns every node.

        Raises:
            PipelineScheduleError: if ``limit`` is not a positive integer.
        """
        if limit is not None and (not isinstance(limit, int) or limit < 1):
            raise PipelineScheduleError("limit must be a positive integer", limit=limit)
        if not isinstance(dependencies, DependencyManager):
            raise PipelineScheduleError("a critical path is derived from a DependencyManager")
        ranked = sorted(
            ((node_id, len(dependencies.impact(node_id))) for node_id in dependencies.node_ids),
            key=lambda pair: (-pair[1], pair[0]),
        )
        return tuple(ranked if limit is None else ranked[:limit])


__all__ = ["DEFAULT_SCHEDULE_STRATEGY", "PipelineSchedule", "PipelineScheduler"]
