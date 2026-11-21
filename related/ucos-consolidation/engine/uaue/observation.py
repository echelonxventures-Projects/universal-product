"""UAUE — AUE-P-06, the evolution observation loop (UAUE-000001, Epoch 3).

Observation compares what the plan expected against what the substrate actually shows, and
records the difference. **Observation is kept separate from truth**: it asserts nothing about
repository state, it makes no state change, and its verdict is not an input to whether the
execution was authorised. It measures after the fact and is attributed to the owner that
measured it.

**Why no verdict word is emitted.** Delta classification against declared orderings — promoted,
regressed, improved, modified, unchanged — is owned by the universal control plane, and its
vocabulary lives under ``platform/``, which ``engine/`` must not import (the dependency runs the
other way, and inverting it would create a cycle). Restating those five words here would be a
second delta vocabulary that could drift from the first. So the classification is *attributed*
to its owner via :attr:`~engine.uaue.objects.EvolutionObservation.classification_owner`, and what
this module records is the falsifiable part: the expected pairs, the actual pairs, and the named
keys that differ. A consumer that needs the verdict word asks the owner that owns it.
"""

from __future__ import annotations

from engine.uaue.authority import dependencies_of
from engine.uaue.model import EvolutionAuthority
from engine.uaue.objects import (
    Context,
    EvolutionCandidate,
    EvolutionExecution,
    EvolutionObject,
    EvolutionObservation,
    as_context,
)
from engine.uaue.resolution import Substrate

_OBSERVATION_ORDINAL = 6


def _deviation(expected: Context, actual: Context) -> tuple[str, ...]:
    """The named keys on which expectation and measurement disagree.

    Reported as keys rather than as a diff of values so a deviation can be quoted in a finding
    without leaking the whole observation, and sorted so two observations of one state produce
    one deviation set.
    """
    expected_map = dict(expected)
    actual_map = dict(actual)
    keys = sorted(set(expected_map) | set(actual_map))
    return tuple(key for key in keys if expected_map.get(key) != actual_map.get(key))


def observe_evolution(
    execution: EvolutionExecution,
    authority: EvolutionAuthority,
    substrate: Substrate | None = None,
) -> EvolutionObservation:
    """Measure the result of an authorised execution.

    Args:
        execution: the authorisation record to measure against.
        authority: the rehydrated authority, which names the measuring owner.
        substrate: the tree the actual state is measured from.

    Returns:
        An :class:`~engine.uaue.objects.EvolutionObservation` carrying expected, actual and
        deviation. A deviation is a finding, never an error: an evolution whose result differs
        from its expectation is exactly what this phase exists to detect.
    """
    substrate = substrate if substrate is not None else Substrate()
    phase = next(entry for entry in authority.phases if entry.ordinal == _OBSERVATION_ORDINAL)
    kind = authority.object_kind_of(phase.identifier)

    # The expectation is what the authorisation claimed. The measurement re-reads the same
    # questions from the substrate now, so a path that vanished between authorisation and
    # observation shows up as a deviation rather than as a stale pass.
    expected = as_context(
        {
            "mutation_path_resolves": str(execution.path_resolves),
            "gate_wired": str(execution.gate_wired),
            "authorised": str(execution.authorised),
            "evidence_count": str(len(execution.obj.evidence)),
            "mutation_performed": "false",
        }
    )
    actual = as_context(
        {
            "mutation_path_resolves": str(
                bool(execution.mutation_path) and substrate.resolves(execution.mutation_path)
            ),
            "gate_wired": str(substrate.gate_state(execution.gate)[0]),
            "authorised": str(execution.authorised),
            "evidence_count": str(
                len([path for path in execution.obj.evidence if substrate.resolves(path)])
            ),
            "mutation_performed": "false",
        }
    )
    deviation = _deviation(expected, actual)

    obj = EvolutionObject.derive(
        rule=authority.identity,
        candidate=EvolutionCandidate.from_object(execution.obj),
        object_kind=kind.identifier,
        phase=phase.identifier,
        lifecycle_state=authority.stage_of(phase.identifier),
        dependencies=dependencies_of(authority, phase.identifier),
        evidence=execution.obj.evidence,
        authority=phase.authority,
        plan=execution.obj.plan,
        execution_record=execution.obj.execution_record,
        context=as_context(
            {
                **dict(execution.obj.context),
                "observed_by": phase.identifier,
                "deviation_count": str(len(deviation)),
            }
        ),
    )
    return EvolutionObservation(
        obj=obj,
        execution=execution,
        expected=expected,
        actual=actual,
        deviation=deviation,
        evidence=tuple(path for path in execution.obj.evidence if substrate.resolves(path)),
        measured_by=phase.owners[0].home if phase.owners else "",
        classification_owner=phase.authority,
    )


__all__ = ["observe_evolution"]
