"""UAUE — AUE-P-03, the evolution planning engine (UAUE-000001, Epoch 3).

The plan is **composed from the declaration**, not authored per candidate. That is the whole
design: three planners already exist in this repository — realization waves, assurance
obligations, and the execution plan the mutation gateway certifies against — and a fourth would
be a fourth authority over one subject. What is missing is not a planner but a record of *which*
located owner discharges each step, and of the criteria each later phase will judge the
evolution against, named before that phase runs.

So every part of an :class:`~engine.uaue.objects.EvolutionPlan` is derived through the declared
plan contract: objectives from the target state, steps from the phases, dependencies from owner
homes and the preceding phase, risk from the discovering owner's severity, and the validation,
verification and certification criteria from their declared blocks. A candidate no owner can
plan for cannot silently acquire a plan, because a step with no located owner is refused.

Rollback is not a compensating action invented per plan. Every step is discharged through the
constitutional mutation gateway, which is the only producer of a clean state seal, so a step
that fails a gateway stage never reaches truth and the prior state is not restored but never
left. The strategy is carried verbatim from the declaration.
"""

from __future__ import annotations

from engine.uaue.authority import dependencies_of
from engine.uaue.model import EvolutionAuthority, EvolutionAuthorityError
from engine.uaue.objects import (
    EvolutionCandidate,
    EvolutionObject,
    EvolutionPlan,
    EvolutionUnderstanding,
    PlanStep,
    as_context,
)

_PLANNING_ORDINAL = 3


def create_evolution_plan(
    understanding: EvolutionUnderstanding,
    authority: EvolutionAuthority,
    candidate: object = None,
) -> EvolutionPlan:
    """Compose the plan for one understood candidate.

    Args:
        understanding: the understanding object this plan is built from. Its target state is
            the plan's objective and its risk is the plan's risk.
        authority: the rehydrated authority, which supplies the steps, the criteria and the
            rollback strategy.
        candidate: accepted and ignored; the candidate is reached through ``understanding`` so
            the two cannot disagree about which subject is being planned.

    Returns:
        An :class:`~engine.uaue.objects.EvolutionPlan` whose every step names a located owner.

    Raises:
        EvolutionAuthorityError: a phase of the loop declares no owner home, so no located
            owner could discharge its step. A plan with an unownable step is a plan that cannot
            be executed, and issuing one would be the manual governance patch this programme
            exists to avoid.
    """
    del candidate
    contract = authority.plan_contract
    phase = next(entry for entry in authority.phases if entry.ordinal == _PLANNING_ORDINAL)
    kind = authority.object_kind_of(phase.identifier)
    subject = understanding.obj.subject_identity

    steps: list[PlanStep] = []
    unownable: list[str] = []
    for entry in authority.phases:
        if not entry.owners:
            unownable.append(entry.identifier)
            continue
        steps.append(
            PlanStep(
                phase=entry.identifier,
                duty=entry.duty,
                # The first declared owner is the step's discharging owner; the rest are
                # collaborators and are carried as dependencies, not as alternative paths.
                owner=entry.owners[0].home,
                gate=entry.gate.command,
                authority=entry.authority,
            )
        )
    if unownable:
        raise EvolutionAuthorityError(
            "a plan step has no located owner, so the plan could not be discharged",
            phases=unownable,
            subject=subject,
        )

    objectives = (
        understanding.target_state,
        *(f"discharge: {statement}" for statement in understanding.validation_requirement),
    )
    dependencies = dependencies_of(authority, phase.identifier)
    risk_controls = (
        *(f"{entry.identifier}: {entry.invariant}" for entry in authority.mandatory),
        f"every step is gated: {', '.join(sorted({step.gate for step in steps if step.gate}))}",
    )
    validation_criteria = tuple(
        f"{entry.identifier}: {entry.obligation}" for entry in authority.validations
    )
    verification_criteria = tuple(
        f"{entry.identifier}: {entry.obligation} (gate: {entry.bound_gate})"
        for entry in authority.verifications
    )
    certification_criteria = tuple(
        f"{entry.identifier}: {entry.obligation}" for entry in authority.certifications
    )

    plan_statement = f"{contract.identifier}: {understanding.target_state}"
    obj = EvolutionObject.derive(
        rule=authority.identity,
        candidate=EvolutionCandidate.from_object(understanding.obj, severity=understanding.risk),
        object_kind=kind.identifier,
        phase=phase.identifier,
        lifecycle_state=authority.stage_of(phase.identifier),
        dependencies=dependencies,
        evidence=understanding.obj.evidence,
        authority=phase.authority,
        plan=plan_statement,
        context=as_context(
            {
                **dict(understanding.obj.context),
                "planned_by": phase.identifier,
                "plan_contract": contract.identifier,
                "steps": str(len(steps)),
            }
        ),
    )
    return EvolutionPlan(
        obj=obj,
        understanding=understanding,
        objectives=objectives,
        steps=tuple(steps),
        dependencies=dependencies,
        risk=understanding.risk,
        risk_controls=risk_controls,
        validation_criteria=validation_criteria,
        verification_criteria=verification_criteria,
        certification_criteria=certification_criteria,
        rollback_strategy=contract.rollback_strategy,
    )


__all__ = ["create_evolution_plan"]
