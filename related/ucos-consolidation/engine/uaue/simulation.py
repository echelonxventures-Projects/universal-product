"""UAUE — AUE-P-04, the evolution simulation engine (UAUE-000001, Epoch 3).

Simulation is **replay against a candidate state**, not a new predictive engine. A predictive
engine would produce an impact estimate that could not be falsified: it would be believed, and
belief is what this programme exists to replace. Replay produces something else — the proof that
executing a plan twice reaches one digest — which is the only impact prediction that *can* be
verified, and it already has an owner.

That owner is :func:`engine.nucleus.lifecycle.replay`, which runs a subject through the canonical
lifecycle stages twice and reports whether the two runs reach one digest. It is inert: it
executes no plan step, writes nothing, and touches no repository state. This module composes its
result with three declaration-derived questions:

* **dependency effects** — which of the plan's declared dependencies resolve, and which do not.
* **potential failures** — which blocking criteria could fail, named before anything runs.
* **validation readiness** — whether every declared validation criterion has something to measure.

If any of those is unanswered, :attr:`~engine.uaue.objects.EvolutionSimulation.executable` is
false, and execution is not authorised. That is the controlled-execution rule: no plan reaches
the execution phase without a prior evaluation.
"""

from __future__ import annotations

from engine.uaue.authority import dependencies_of
from engine.uaue.model import EvolutionAuthority
from engine.uaue.objects import (
    EvolutionCandidate,
    EvolutionObject,
    EvolutionPlan,
    EvolutionSimulation,
    as_context,
)
from engine.uaue.resolution import Substrate
from engine.uckp.canonical import content_hash

_SIMULATION_ORDINAL = 4


def simulate_evolution(
    plan: EvolutionPlan,
    authority: EvolutionAuthority,
    substrate: Substrate | None = None,
) -> EvolutionSimulation:
    """Evaluate a plan before anything executes.

    Args:
        plan: the plan to evaluate. Its steps, dependencies and criteria are the subject.
        authority: the rehydrated authority.
        substrate: the tree used to decide which dependencies and evidence resolve.

    Returns:
        An :class:`~engine.uaue.objects.EvolutionSimulation`. Deterministic: the same plan over
        the same tree yields the same digests, which is what makes the fixed point meaningful.
    """
    from engine.nucleus.lifecycle import replay

    substrate = substrate if substrate is not None else Substrate()
    phase = next(entry for entry in authority.phases if entry.ordinal == _SIMULATION_ORDINAL)
    kind = authority.object_kind_of(phase.identifier)
    subject = plan.obj.subject_identity

    # Replay is performed over the candidate state — the plan's own digest bound to the subject
    # — rather than over the working tree, so simulating twice cannot change what is simulated.
    candidate_state = content_hash([subject, plan.digest()])
    outcome = replay(
        subject,
        context={"frame": phase.identifier, "resolution_digest": candidate_state},
    )
    first = str(outcome.get("first_digest", ""))
    second = str(outcome.get("second_digest", ""))
    fixed_point = bool(outcome.get("fixed_point")) and first == second and bool(first)

    declared_dependencies = dependencies_of(authority, phase.identifier) + plan.dependencies
    # A dependency naming a phase is satisfied by the loop's own order, which the authority has
    # already proved acyclic; only a dependency naming a repository path can fail to resolve.
    phase_ids = {entry.identifier for entry in authority.phases}
    effects: list[str] = []
    unresolved: list[str] = []
    for dependency in dict.fromkeys(declared_dependencies):
        if dependency in phase_ids:
            effects.append(f"{dependency} is an earlier phase of the loop and precedes this one")
            continue
        if substrate.resolves(dependency):
            effects.append(f"{dependency} resolves")
        else:
            unresolved.append(dependency)
            effects.append(f"{dependency} does not resolve")

    expected_impact = (
        f"{plan.obj.previous_state} becomes: {plan.obj.target_state}",
        f"{len(plan.steps)} steps, each discharged by a located owner",
        f"replay over the candidate state {'reaches' if fixed_point else 'does not reach'} "
        "a fixed point",
    )
    potential_failures = tuple(
        f"{entry.identifier}: {entry.obligation}"
        for entry in (*authority.validations, *authority.verifications)
        if entry.blocking
    )
    unwired = tuple(
        entry.bound_gate
        for entry in authority.verifications
        if entry.bound_gate and not substrate.gate_state(entry.bound_gate)[0]
    )
    validation_ready = bool(plan.validation_criteria) and not unwired

    obj = EvolutionObject.derive(
        rule=authority.identity,
        candidate=EvolutionCandidate.from_object(plan.obj, severity=plan.risk),
        object_kind=kind.identifier,
        phase=phase.identifier,
        lifecycle_state=authority.stage_of(phase.identifier),
        dependencies=dependencies_of(authority, phase.identifier),
        evidence=plan.obj.evidence,
        authority=phase.authority,
        plan=plan.obj.plan,
        context=as_context(
            {
                **dict(plan.obj.context),
                "simulated_by": phase.identifier,
                "candidate_state": candidate_state,
                "fixed_point": str(fixed_point),
            }
        ),
    )
    return EvolutionSimulation(
        obj=obj,
        plan=plan,
        expected_impact=expected_impact,
        dependency_effects=tuple(effects),
        unresolved_dependencies=tuple(unresolved),
        potential_failures=potential_failures,
        validation_ready=validation_ready,
        fixed_point=fixed_point,
        first_digest=first,
        second_digest=second,
        replay_owner=phase.owners[0].home if phase.owners else "",
    )


__all__ = ["simulate_evolution"]
