"""URI-000001 — the Planning Engine.

Turns integrity-verified canonical knowledge into a **derived** realization plan: what
must be realized, in what order, and from which canonical objects. Nothing about the
plan is authored — targets come from knowledge universes, steps come from the cross
product of targets and the seven artifact families, and the ordering comes from the
declared family dependency graph plus the canonical knowledge dependency topology.

Guarantees:

* **Deterministic** — ids are content-derived, collections are sorted, no clock is read.
  The same canonical knowledge always yields the identical plan and the identical seal.
* **Acyclic** — the step graph is topologically sorted with a fail-closed cycle check
  (:class:`~intelligence.realization.errors.PlanningError`).
* **Waved** — steps are grouped into parallel-safe waves (longest-path level), so the
  plan is directly executable by a concurrent runner without further analysis.
* **Complete** — every realizable canonical object is claimed by at least one step;
  anything unclaimed is reported as an explicit ``coverage_gaps`` entry rather than
  silently dropped.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from engine.foundation.obs.logging import get_logger
from engine.foundation.obs.telemetry import trace
from intelligence.realization.contracts import (
    FAMILY_DEPENDENCIES,
    FAMILY_ORDER,
    ArtifactFamily,
    PlanStep,
    RealizationPlan,
    RealizationTarget,
    dedupe,
)
from intelligence.realization.errors import PlanningError
from intelligence.realization.knowledge import KnowledgeIntake

_logger = get_logger("intelligence.realization.planning")


def _step_id(target: RealizationTarget, family: ArtifactFamily) -> str:
    """Deterministic, human-legible step identity: ``URI-STEP-<UNIVERSE>-<FAMILY>``."""
    return f"URI-STEP-{target.path_slug.upper()}-{family.value.upper()}"


def _dependency_universes(intake: KnowledgeIntake, target: RealizationTarget) -> tuple[str, ...]:
    """Universes this target depends on, read from canonical dependency links.

    A target depends on another universe when any of its objects declares a
    ``dependencies``/``parent`` link into an object homed in that universe. This makes
    cross-universe realization order a *derived* fact, not a configured one.
    """
    universes: set[str] = set()
    for obj in intake.objects_for(target):
        refs = [*obj.dependencies, *([obj.parent] if obj.parent else [])]
        for ref in refs:
            other = intake.base.get_object(ref)
            if other is not None and other.universe != target.universe:
                universes.add(other.universe)
    return dedupe(universes)


def _topological_waves(
    nodes: Sequence[str], edges: Mapping[str, tuple[str, ...]]
) -> tuple[tuple[str, ...], ...]:
    """Group ``nodes`` into dependency waves (Kahn levelling); raise on any cycle."""
    remaining = {node: set(edges.get(node, ())) for node in nodes}
    known = set(nodes)
    for node, deps in remaining.items():
        unknown = deps - known
        if unknown:
            raise PlanningError(
                "plan step depends on an unknown step",
                step_id=node,
                unknown=sorted(unknown),
            )
    waves: list[tuple[str, ...]] = []
    settled: set[str] = set()
    while remaining:
        ready = tuple(sorted(n for n, deps in remaining.items() if deps <= settled))
        if not ready:
            raise PlanningError(
                "realization plan contains a dependency cycle",
                unresolved=sorted(remaining),
            )
        waves.append(ready)
        settled.update(ready)
        for node in ready:
            del remaining[node]
    return tuple(waves)


class PlanningEngine:
    """Derives the realization plan from canonical knowledge. Holds no state."""

    #: Every target is realized into every family — realization is total, not selective.
    families: tuple[ArtifactFamily, ...] = FAMILY_ORDER

    def plan(self, intake: KnowledgeIntake) -> RealizationPlan:
        """Return the sealed, acyclic, waved realization plan for ``intake``."""
        with trace("realization.plan", targets=len(intake.targets)):
            if not intake.targets:
                raise PlanningError(
                    "no realization targets derived from canonical knowledge",
                    source=intake.source,
                )
            steps = self._steps(intake)
            edges = {step.step_id: step.depends_on for step in steps}
            waves = _topological_waves([s.step_id for s in steps], edges)
            level_of = {sid: idx for idx, wave in enumerate(waves) for sid in wave}
            levelled = tuple(
                sorted(
                    (
                        PlanStep(
                            step_id=step.step_id,
                            target_id=step.target_id,
                            universe=step.universe,
                            family=step.family,
                            depends_on=step.depends_on,
                            source_ckos=step.source_ckos,
                            wave=level_of[step.step_id],
                        )
                        for step in steps
                    ),
                    key=lambda s: (s.wave, s.step_id),
                )
            )
            plan = RealizationPlan(
                knowledge_seal=intake.knowledge_seal,
                targets=intake.targets,
                steps=levelled,
                waves=waves,
                coverage_gaps=self.coverage_gaps(intake, levelled),
            )
            _logger.info(
                "realization.planned",
                plan_id=plan.plan_id,
                steps=len(plan.steps),
                waves=len(plan.waves),
                gaps=len(plan.coverage_gaps),
            )
            return plan

    # -- derivation -----------------------------------------------------------

    def _steps(self, intake: KnowledgeIntake) -> tuple[PlanStep, ...]:
        """One step per (target × family), wired to its intra- and inter-target deps."""
        by_universe = {t.universe: t for t in intake.targets}
        upstream = {t.universe: _dependency_universes(intake, t) for t in intake.targets}
        steps: list[PlanStep] = []
        for target in intake.targets:
            for family in self.families:
                depends: set[str] = {
                    _step_id(target, parent) for parent in FAMILY_DEPENDENCIES[family]
                }
                # Cross-universe order: the same family in every upstream universe must
                # be realized first, so a dependent universe can cite it.
                for other in upstream[target.universe]:
                    peer = by_universe.get(other)
                    if peer is not None:
                        depends.add(_step_id(peer, family))
                steps.append(
                    PlanStep(
                        step_id=_step_id(target, family),
                        target_id=target.target_id,
                        universe=target.universe,
                        family=family,
                        depends_on=dedupe(depends),
                        source_ckos=target.cko_ids,
                        wave=0,
                    )
                )
        return tuple(sorted(steps, key=lambda s: s.step_id))

    def coverage_gaps(self, intake: KnowledgeIntake, steps: Sequence[PlanStep]) -> tuple[str, ...]:
        """Realizable canonical objects that no plan step claims (reported, never hidden)."""
        claimed = {cko for step in steps for cko in step.source_ckos}
        return dedupe(cko for cko in intake.realizable_ids() if cko not in claimed)


def build_plan(intake: KnowledgeIntake) -> RealizationPlan:
    """Convenience entry point: derive a realization plan from canonical knowledge."""
    return PlanningEngine().plan(intake)


__all__ = ["PlanningEngine", "build_plan"]
