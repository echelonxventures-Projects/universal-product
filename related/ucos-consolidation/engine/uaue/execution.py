"""UAUE — AUE-P-05, the controlled execution engine (UAUE-000001, Epoch 3).

**This module performs no mutation, and that is its entire security property.**

The constitutional mutation gateway is the only producer of a clean state seal, so it is the
only path by which an executed evolution can become repository truth. What this phase produces
is the *authorisation record*: which mutation path is authorised, under which authority, behind
which gate, and whether that path resolves with its declared symbols bound. It offers no
alternative path, which is why no bypass can originate here — there is no code path from this
module to repository state, so there is nothing to bypass to.

The declared field mandate is explicit that ``execution_record`` is "the authorised execution
path, its gate, and whether the path resolves. Never an assertion that a mutation happened."
:attr:`~engine.uaue.objects.EvolutionExecution.mutation_performed` is therefore always ``False``
and is carried in the record so that a reader cannot mistake an authorisation for an effect.

Seven preconditions are required before an execution is authorised: identity, authority,
evidence, plan, and the validation, verification and certification gates. Each is measured, and
every failure is named in ``refusals`` rather than collapsed into a single boolean.
"""

from __future__ import annotations

from engine.uaue.authority import dependencies_of
from engine.uaue.model import EvolutionAuthority
from engine.uaue.objects import (
    EvolutionCandidate,
    EvolutionExecution,
    EvolutionObject,
    EvolutionSimulation,
    as_context,
)
from engine.uaue.resolution import Substrate

_EXECUTION_ORDINAL = 5


def execute_evolution(
    simulation: EvolutionSimulation,
    authority: EvolutionAuthority,
    substrate: Substrate | None = None,
) -> EvolutionExecution:
    """Authorise — never perform — the execution of an evaluated plan.

    Args:
        simulation: the prior evaluation. A plan that was not simulated, or whose simulation is
            not executable, is refused: the controlled-execution rule forbids executing a plan
            with no prior evaluation.
        authority: the rehydrated authority, which names the single authorised mutation path.
        substrate: the tree used to measure whether that path resolves and its gate is wired.

    Returns:
        An :class:`~engine.uaue.objects.EvolutionExecution` whose ``mutation_performed`` is
        always false. When ``authorised`` is false, ``refusals`` names every unmet precondition.
    """
    substrate = substrate if substrate is not None else Substrate()
    phase = next(entry for entry in authority.phases if entry.ordinal == _EXECUTION_ORDINAL)
    kind = authority.object_kind_of(phase.identifier)
    plan = simulation.plan

    gateway = phase.owners[0] if phase.owners else None
    mutation_path = gateway.home if gateway is not None else ""
    mutation_symbols = gateway.symbols if gateway is not None else ()
    path_resolves = bool(mutation_path) and substrate.resolves(mutation_path)
    gate_wired = phase.gate.wired

    refusals: list[str] = []
    if not mutation_path:
        refusals.append(
            "no mutation path is declared: there is no authorised way to execute this plan"
        )
    elif not path_resolves:
        refusals.append(f"the declared mutation path does not resolve: {mutation_path}")
    else:
        bound = substrate.symbols(mutation_path)
        for symbol in mutation_symbols:
            if symbol not in bound:
                refusals.append(
                    f"the mutation path does not bind {symbol}, "
                    "so the authorised path is not the path declared"
                )
    if not gate_wired:
        refusals.append(f"the execution gate is not wired: {phase.gate.command}")
    if not phase.authority:
        refusals.append("the execution phase names no authority")
    if not plan.obj.plan:
        refusals.append("the object carries no plan, so nothing is authorised to be executed")
    if not plan.obj.evidence:
        refusals.append("the object carries no evidence")
    if not simulation.executable:
        refusals.append(
            "the simulation did not authorise execution: "
            f"fixed_point={simulation.fixed_point}, "
            f"unresolved_dependencies={len(simulation.unresolved_dependencies)}, "
            f"validation_ready={simulation.validation_ready}"
        )
    if not plan.obj.evolution_id:
        refusals.append("the object is anonymous")

    execution_record = (
        f"authorised via {mutation_path} behind {phase.gate.command} " f"under {phase.authority}"
        if not refusals
        else f"refused: {'; '.join(refusals)}"
    )

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
        execution_record=execution_record,
        context=as_context(
            {
                **dict(plan.obj.context),
                "executed_by": phase.identifier,
                "mutation_path": mutation_path,
                "gate": phase.gate.command,
                "mutation_performed": "false",
            }
        ),
    )
    return EvolutionExecution(
        obj=obj,
        plan=plan,
        simulation=simulation,
        mutation_path=mutation_path,
        mutation_symbols=mutation_symbols,
        gate=phase.gate.command,
        gate_wired=gate_wired,
        path_resolves=path_resolves,
        authority=phase.authority,
        authorised=not refusals,
        refusals=tuple(refusals),
        mutation_performed=False,
    )


__all__ = ["execute_evolution"]
