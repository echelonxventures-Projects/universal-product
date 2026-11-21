"""URI-000001 — the Composition Engine.

Planning says *what* must be realized. Composition resolves *what each step is allowed
to see*: it binds every plan step to the exact canonical objects, decisions, and
upstream units it consumes, and refuses to compose knowledge that cannot legally be
composed.

Two fail-closed refusals live here, and they are the reason composition is a distinct
stage rather than a detail of generation:

* **Conflict** — two canonical objects that declare ``conflicts_with`` each other may
  never be bound into the same unit. Realizing them together would emit an artifact
  that satisfies neither.
* **Duplicate knowledge** — two canonical objects with the same *semantic* hash express
  the same knowledge under different identities (a Knowledge Once Principle violation,
  ``UCKO-PRIN-0001`` / ``UCKO-RULE-0001``). Composing them would generate duplicated
  output from a forked source of truth.

Both are reported as structured findings; the governance layer converts them into a
`REJECTED` decision. Composition itself raises only when the *graph* is malformed.
"""

from __future__ import annotations

from dataclasses import dataclass

from engine.foundation.obs.logging import get_logger
from engine.foundation.obs.telemetry import trace
from intelligence.realization.contracts import (
    FAMILY_DEPENDENCIES,
    CompositionUnit,
    RealizationComposition,
    RealizationPlan,
    dedupe,
)
from intelligence.realization.errors import CompositionError
from intelligence.realization.knowledge import KnowledgeIntake

_logger = get_logger("intelligence.realization.composition")


def _unit_id(step_id: str) -> str:
    """A composition unit is one-to-one with a plan step; its identity mirrors it."""
    return step_id.replace("URI-STEP-", "URI-UNIT-", 1)


@dataclass(frozen=True, slots=True)
class CompositionFindings:
    """Structured, non-raising findings the governance layer adjudicates."""

    conflicts: tuple[tuple[str, str], ...]
    duplicate_knowledge: tuple[tuple[str, ...], ...]
    unbound_steps: tuple[str, ...]

    @property
    def clean(self) -> bool:
        return not (self.conflicts or self.duplicate_knowledge or self.unbound_steps)

    def to_dict(self) -> dict[str, object]:
        return {
            "clean": self.clean,
            "conflicts": [list(pair) for pair in self.conflicts],
            "duplicate_knowledge": [list(group) for group in self.duplicate_knowledge],
            "unbound_steps": list(self.unbound_steps),
        }


class CompositionEngine:
    """Composes a realization plan into a sealed, ordered, conflict-checked graph."""

    def compose(
        self, intake: KnowledgeIntake, plan: RealizationPlan
    ) -> tuple[RealizationComposition, CompositionFindings]:
        """Return the composition and its findings. Never partially composes."""
        with trace("realization.compose", plan_id=plan.plan_id, steps=len(plan.steps)):
            if plan.knowledge_seal != intake.knowledge_seal:
                raise CompositionError(
                    "plan was derived from a different canonical knowledge state",
                    plan_seal=plan.knowledge_seal,
                    intake_seal=intake.knowledge_seal,
                )
            units = self._units(intake, plan)
            order = self._order(units)
            findings = self._findings(intake, units)
            composition = RealizationComposition(
                plan_id=plan.plan_id,
                plan_seal=plan.seal,
                knowledge_seal=plan.knowledge_seal,
                units=units,
                order=order,
                conflicts=findings.conflicts,
            )
            _logger.info(
                "realization.composed",
                composition_id=composition.composition_id,
                units=len(units),
                clean=findings.clean,
            )
            return composition, findings

    # -- derivation -----------------------------------------------------------

    def _units(self, intake: KnowledgeIntake, plan: RealizationPlan) -> tuple[CompositionUnit, ...]:
        units: list[CompositionUnit] = []
        for step in plan.steps:
            target = plan.target(step.target_id)
            bound_ckos = dedupe(cko for cko in step.source_ckos if intake.base.has_object(cko))
            missing = tuple(cko for cko in step.source_ckos if not intake.base.has_object(cko))
            if missing:
                raise CompositionError(
                    "plan step binds a canonical object absent from the store",
                    step_id=step.step_id,
                    missing=list(missing),
                )
            units.append(
                CompositionUnit(
                    unit_id=_unit_id(step.step_id),
                    step_id=step.step_id,
                    target_id=step.target_id,
                    universe=step.universe,
                    family=step.family,
                    bound_ckos=bound_ckos,
                    bound_decisions=target.decision_ids,
                    upstream_units=dedupe(_unit_id(dep) for dep in step.depends_on),
                    consumed_families=tuple(f.value for f in FAMILY_DEPENDENCIES[step.family]),
                )
            )
        return tuple(sorted(units, key=lambda u: u.unit_id))

    def _order(self, units: tuple[CompositionUnit, ...]) -> tuple[str, ...]:
        """Topologically order units; deterministic tie-break by unit id."""
        pending = {u.unit_id: set(u.upstream_units) for u in units}
        known = set(pending)
        for unit_id, deps in pending.items():
            unknown = deps - known
            if unknown:
                raise CompositionError(
                    "composition unit depends on an unknown unit",
                    unit_id=unit_id,
                    unknown=sorted(unknown),
                )
        ordered: list[str] = []
        settled: set[str] = set()
        while pending:
            ready = sorted(uid for uid, deps in pending.items() if deps <= settled)
            if not ready:
                raise CompositionError(
                    "composition graph contains a cycle", unresolved=sorted(pending)
                )
            ordered.extend(ready)
            settled.update(ready)
            for uid in ready:
                del pending[uid]
        return tuple(ordered)

    def _findings(
        self, intake: KnowledgeIntake, units: tuple[CompositionUnit, ...]
    ) -> CompositionFindings:
        declared = intake.conflict_pairs()
        co_bound: set[tuple[str, str]] = set()
        for unit in units:
            members = set(unit.bound_ckos)
            for left, right in declared:
                if left in members and right in members:
                    co_bound.add((left, right))
        duplicates = tuple(group for group in intake.semantic_index().values() if len(group) > 1)
        unbound = tuple(sorted(u.step_id for u in units if not u.bound_ckos))
        return CompositionFindings(
            conflicts=tuple(sorted(co_bound)),
            duplicate_knowledge=duplicates,
            unbound_steps=unbound,
        )


def compose_plan(
    intake: KnowledgeIntake, plan: RealizationPlan
) -> tuple[RealizationComposition, CompositionFindings]:
    """Convenience entry point: compose a realization plan."""
    return CompositionEngine().compose(intake, plan)


__all__ = ["CompositionEngine", "CompositionFindings", "compose_plan"]
