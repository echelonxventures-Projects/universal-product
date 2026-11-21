"""UAUE — AUE-P-08, the evolution verification engine (UAUE-000001, Epoch 3).

Verification proves integrity: identity, dependency, evidence, governance, lifecycle, and
readiness to certify. Each declared dimension is bound to a gate, and this module measures two
distinct things per dimension — whether the integrity property holds over the chain, and whether
the gate the declaration bound it to is actually wired.

The second measurement is the one that matters most and is easy to omit. A dimension bound to a
gate that nothing runs is a dimension nobody checks; it would report satisfied for ever while
discharging nothing. So an unwired gate is carried on the outcome
(:attr:`~engine.uaue.objects.CriterionOutcome.gate_wired`) and makes the governance dimension
fail, rather than being quietly dropped.

Verification never restates a gate's verdict as its own. It names which gate discharges which
dimension and measures that the gate is wired; what the gate decides when it runs is the gate's.
"""

from __future__ import annotations

from engine.uaue.model import EvolutionAuthority, EvolutionAuthorityError
from engine.uaue.objects import (
    CriterionOutcome,
    EvolutionChain,
    EvolutionObject,
    Verdict,
    derive_identity,
    identity_inputs,
    phase_object,
)
from engine.uaue.resolution import Substrate

_VERIFICATION_ORDINAL = 8


def _identity_integrity(authority: EvolutionAuthority, chain: EvolutionChain) -> tuple[bool, str]:
    """No object is anonymous and no two distinct objects share an identity."""
    anonymous: list[str] = []
    for obj in chain.objects:
        if not obj.evolution_id or not obj.subject_identity.strip():
            anonymous.append(obj.object_kind)
            continue
        try:
            inputs = identity_inputs(authority.identity, obj)
        except EvolutionAuthorityError:
            anonymous.append(obj.object_kind)
            continue
        if derive_identity(authority.identity, inputs) != obj.evolution_id:
            anonymous.append(obj.object_kind)
    identities = [obj.evolution_id for obj in chain.objects]
    collisions = len(identities) - len(set(identities))
    if anonymous:
        return False, f"anonymous objects: {sorted(set(anonymous))}"
    if collisions:
        return False, f"{collisions} distinct objects share an identity"
    return True, f"{len(identities)} distinct, non-anonymous identities"


def _dependency_integrity(authority: EvolutionAuthority, chain: EvolutionChain) -> tuple[bool, str]:
    """Every phase dependency names an earlier phase: the loop has no backward edge."""
    del chain
    ordinal = {phase.identifier: phase.ordinal for phase in authority.phases}
    backward = [
        f"{edge.phase}->{edge.depends_on}"
        for edge in authority.dependencies
        if edge.kind == "phase" and ordinal[edge.depends_on] >= ordinal[edge.phase]
    ]
    if backward:
        return False, f"backward dependency edges: {backward}"
    edges = sum(1 for edge in authority.dependencies if edge.kind == "phase")
    return True, f"{edges} phase edges, every one pointing at an earlier phase"


def _evidence_integrity(chain: EvolutionChain, substrate: Substrate) -> tuple[bool, str]:
    """Every object carries at least one *resolving* evidence path."""
    unevidenced = [
        obj.object_kind
        for obj in chain.objects
        if not any(substrate.resolves(path) for path in obj.evidence)
    ]
    if unevidenced:
        return False, f"objects with no resolving evidence: {sorted(set(unevidenced))}"
    return True, f"all {len(chain.objects)} objects carry resolving evidence"


def _governance_integrity(authority: EvolutionAuthority, substrate: Substrate) -> tuple[bool, str]:
    """Every phase names a gate, and every named gate is wired."""
    ungated = [phase.identifier for phase in authority.phases if not phase.gate.command]
    unwired = [
        f"{phase.identifier}:{phase.gate.command}"
        for phase in authority.phases
        if phase.gate.command and not phase.gate.wired
    ]
    bound_unwired = [
        entry.bound_gate
        for entry in authority.verifications
        if entry.bound_gate and not substrate.gate_state(entry.bound_gate)[0]
    ]
    if ungated:
        return False, f"phases naming no gate: {ungated}"
    if unwired or bound_unwired:
        return False, (f"declared gates not wired: {sorted(set(unwired) | set(bound_unwired))}")
    return True, f"all {len(authority.phases)} phase gates and every bound gate are wired"


def _lifecycle_integrity(authority: EvolutionAuthority, chain: EvolutionChain) -> tuple[bool, str]:
    """Every object's lifecycle state is a stage the canonical stage authority declares."""
    canonical = {state.name for state in authority.lifecycle_states}
    foreign = [
        f"{obj.object_kind}:{obj.lifecycle_state}"
        for obj in chain.objects
        if obj.lifecycle_state not in canonical
    ]
    if foreign:
        return False, f"lifecycle states outside the canonical cycle: {foreign}"
    return True, (
        f"all {len(chain.objects)} lifecycle states are canonical stages of "
        f"{authority.stage_authority_home}"
    )


def _certification_readiness(authority: EvolutionAuthority) -> tuple[bool, str]:
    """No phase is classified MISSING or DUPLICATE."""
    refused = [
        f"{phase.identifier}:{phase.classification}"
        for phase in authority.phases
        if phase.classification in {"MISSING", "DUPLICATE"}
    ]
    if refused:
        return False, f"phases blocking certification: {refused}"
    return True, f"no phase of {len(authority.phases)} is MISSING or DUPLICATE"


def verify_evolution(
    chain: EvolutionChain,
    authority: EvolutionAuthority,
    substrate: Substrate | None = None,
) -> Verdict:
    """Measure every declared verification dimension over one chain.

    Args:
        chain: the chain to verify.
        authority: the rehydrated authority, whose ``verifications`` block is the criteria list
            and supplies each dimension's bound gate.
        substrate: the tree used to measure evidence resolution and gate wiring.

    Returns:
        A :class:`~engine.uaue.objects.Verdict` in which every outcome carries its bound gate and
        whether that gate is wired.
    """
    substrate = substrate if substrate is not None else Substrate()
    phase = next(entry for entry in authority.phases if entry.ordinal == _VERIFICATION_ORDINAL)
    owner = phase.owners[0].home if phase.owners else ""

    outcomes: list[CriterionOutcome] = []
    for criterion in authority.verifications:
        dimension = criterion.subject.strip().lower()
        if dimension.startswith("identity"):
            satisfied, detail = _identity_integrity(authority, chain)
        elif dimension.startswith("dependency"):
            satisfied, detail = _dependency_integrity(authority, chain)
        elif dimension.startswith("evidence"):
            satisfied, detail = _evidence_integrity(chain, substrate)
        elif dimension.startswith("governance"):
            satisfied, detail = _governance_integrity(authority, substrate)
        elif dimension.startswith("lifecycle"):
            satisfied, detail = _lifecycle_integrity(authority, chain)
        elif dimension.startswith("certification"):
            satisfied, detail = _certification_readiness(authority)
        else:
            satisfied, detail = (
                False,
                "the declaration adds a verification dimension this engine cannot measure",
            )
        wired, gate_detail = (
            substrate.gate_state(criterion.bound_gate)
            if criterion.bound_gate
            else (True, "no gate is bound to this dimension")
        )
        outcomes.append(
            CriterionOutcome(
                identifier=criterion.identifier,
                subject=criterion.subject,
                obligation=criterion.obligation,
                satisfied=satisfied,
                blocking=criterion.blocking,
                detail=f"{detail}; gate: {gate_detail}",
                owner=owner,
                gate=criterion.bound_gate,
                gate_wired=wired,
            )
        )
    return Verdict(subject=f"verification of {chain.evolution_id}", outcomes=tuple(outcomes))


def verification_object(
    chain: EvolutionChain, verdict: Verdict, authority: EvolutionAuthority
) -> EvolutionObject:
    """The verification phase's own object, carrying the measured verdict."""
    previous = chain.objects[-1] if chain.objects else None
    if previous is None:
        raise EvolutionAuthorityError(
            "a chain with no prior object cannot be verified", subject=chain.subject_identity
        )
    return phase_object(
        authority,
        previous,
        ordinal=_VERIFICATION_ORDINAL,
        verification_result=verdict.summary,
        note={"verified_by": authority.phase_by_ordinal(_VERIFICATION_ORDINAL).identifier},
    )


__all__ = ["verification_object", "verify_evolution"]
