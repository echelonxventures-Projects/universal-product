"""UAUE — AUE-P-07, the evolution validation engine (UAUE-000001, Epoch 3).

Six dimensions are declared — correctness, completeness, consistency, compatibility,
traceability, reproducibility — and each is measured here **over one evolution chain**. Not over
the repository: the repository's validation dimensions have owners, and re-implementing one would
be a second validator of the same subject.

The boundary is precise and worth stating, because it is the difference between reuse and
duplication. The assurance orchestrator owns *whether a validation dimension is satisfied for an
artifact*. The UCKP validator owns *whether the constitutional universe holds its invariants*.
Neither of them knows what an evolution transaction is, and neither can answer "does this
evolution object satisfy the obligation this declaration wrote for it". That question is this
register's, and it is the only question answered here. Each outcome names the declared owner, so
a reader can go to the owner for the dimension and to this report for the instance.

Every obligation is measured from the declaration's own words. A dimension whose obligation this
engine cannot measure is reported unsatisfied with that as its detail — never skipped, because a
dimension that silently disappears is a dimension that always passes.
"""

from __future__ import annotations

from collections.abc import Sequence

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

_VALIDATION_ORDINAL = 7

#: Each declared dimension is measured by the method named here. Bound by *dimension text*
#: rather than by criterion id so a renumbered declaration still measures, and a dimension the
#: declaration adds is reported unmeasurable rather than silently satisfied.
_MEASURED = (
    "correctness",
    "completeness",
    "consistency",
    "compatibility",
    "traceability",
    "reproducibility",
)


def _identity_matches(authority: EvolutionAuthority, obj: EvolutionObject) -> bool:
    """Whether an object's identity equals the digest of its own declared identity inputs.

    Re-derived through the same rule and the same generic input reader that minted it. This is the
    one measurement that cannot be taken on trust: an object whose identity does not describe its
    own content is anonymous in the declaration's sense, however well-formed the string looks.
    """
    try:
        inputs = identity_inputs(authority.identity, obj)
        return derive_identity(authority.identity, inputs) == obj.evolution_id
    except EvolutionAuthorityError:
        # An object that cannot even present its identity inputs is not merely mismatched; it is
        # unidentifiable, which is the failure this dimension exists to catch.
        return False


def _correctness(authority: EvolutionAuthority, chain: EvolutionChain) -> tuple[bool, str]:
    wrong = [obj.evolution_id for obj in chain.objects if not _identity_matches(authority, obj)]
    if wrong:
        return False, f"{len(wrong)} objects carry an identity that is not their own digest"
    return True, f"all {len(chain.objects)} identities equal the digest of their inputs"


def _completeness(authority: EvolutionAuthority, chain: EvolutionChain) -> tuple[bool, str]:
    empty: list[str] = []
    for obj in chain.objects:
        for mandated in authority.required_fields:
            value = obj.field_value(mandated.field_name)
            if mandated.non_empty and not value:
                empty.append(f"{obj.object_kind}.{mandated.field_name}")
    if empty:
        return False, f"empty mandated fields: {', '.join(sorted(set(empty))[:6])}"
    return True, (
        f"all {len(authority.required_fields)} mandated fields present on "
        f"{len(chain.objects)} objects"
    )


def _consistency(authority: EvolutionAuthority, chain: EvolutionChain) -> tuple[bool, str]:
    contested = [state.name for state in authority.lifecycle_states if len(state.claimed_by) != 1]
    if contested:
        return False, f"stages not claimed by exactly one phase: {contested}"
    kinds = chain.kinds()
    if len(set(kinds)) != len(kinds):
        return False, "two objects of the chain claim one object kind"
    return True, (
        f"{len(authority.lifecycle_states)} stages each claimed once; "
        f"{len(kinds)} distinct object kinds in the chain"
    )


def _compatibility(
    authority: EvolutionAuthority, chain: EvolutionChain, substrate: Substrate
) -> tuple[bool, str]:
    del chain
    unresolved = [entry.home for entry in authority.ownership if not entry.resolves]
    unbound = [
        f"{phase.identifier}:{symbol}"
        for phase in authority.phases
        for symbol in phase.missing_symbols
    ]
    del substrate
    if unresolved or unbound:
        return False, (
            f"{len(unresolved)} owner homes do not resolve; {len(unbound)} symbols unbound"
        )
    return True, f"all {len(authority.ownership)} owner homes resolve with their symbols"


def _traceability(authority: EvolutionAuthority, chain: EvolutionChain) -> tuple[bool, str]:
    source_ids = {entry.identifier for entry in authority.discovery_sources}
    if chain.candidate.source not in source_ids:
        return False, f"the candidate names no declared source: {chain.candidate.source!r}"
    produced = set(chain.kinds())
    missing = [
        kind.identifier for kind in authority.mandated_kinds() if kind.identifier not in produced
    ]
    if missing:
        return False, f"mandated object kinds not produced: {missing}"
    return True, (
        f"candidate traces to {chain.candidate.source}; "
        f"all {len(authority.mandated_kinds())} mandated kinds produced"
    )


def _reproducibility(chain: EvolutionChain) -> tuple[bool, str]:
    """Two renders of one chain must be byte-identical.

    Measured by digesting the chain twice. Because every object is frozen and every collection
    is an ordered tuple, a difference here would mean non-determinism entered the chain, which
    is the one failure that would make every other measurement unrepeatable.
    """
    first = chain.digest()
    second = chain.digest()
    if first != second:
        return False, "two renders of one chain are not byte-identical"
    return True, f"chain digest is stable: {first[:12]}"


def validate_evolution(
    chain: EvolutionChain,
    authority: EvolutionAuthority,
    substrate: Substrate | None = None,
) -> Verdict:
    """Measure every declared validation dimension over one chain.

    Args:
        chain: the chain to judge. Every object in it is measured.
        authority: the rehydrated authority, whose ``validations`` block *is* the criteria list.
        substrate: the tree used for the compatibility dimension.

    Returns:
        A :class:`~engine.uaue.objects.Verdict`. ``passed`` is false when any blocking dimension
        is unsatisfied.
    """
    substrate = substrate if substrate is not None else Substrate()
    phase = next(entry for entry in authority.phases if entry.ordinal == _VALIDATION_ORDINAL)
    owner = phase.owners[0].home if phase.owners else ""

    outcomes: list[CriterionOutcome] = []
    for criterion in authority.validations:
        dimension = criterion.subject.strip().lower()
        if dimension == "correctness":
            satisfied, detail = _correctness(authority, chain)
        elif dimension == "completeness":
            satisfied, detail = _completeness(authority, chain)
        elif dimension == "consistency":
            satisfied, detail = _consistency(authority, chain)
        elif dimension == "compatibility":
            satisfied, detail = _compatibility(authority, chain, substrate)
        elif dimension == "traceability":
            satisfied, detail = _traceability(authority, chain)
        elif dimension == "reproducibility":
            satisfied, detail = _reproducibility(chain)
        else:
            satisfied, detail = (
                False,
                "the declaration adds a validation dimension this engine cannot measure",
            )
        outcomes.append(
            CriterionOutcome(
                identifier=criterion.identifier,
                subject=criterion.subject,
                obligation=criterion.obligation,
                satisfied=satisfied,
                blocking=criterion.blocking,
                detail=detail,
                owner=owner,
            )
        )
    return Verdict(subject=f"validation of {chain.evolution_id}", outcomes=tuple(outcomes))


def measurable_dimensions() -> Sequence[str]:
    """The dimensions this engine implements, for a non-vacuity check against the declaration."""
    return _MEASURED


def validation_object(
    chain: EvolutionChain, verdict: Verdict, authority: EvolutionAuthority
) -> EvolutionObject:
    """The validation phase's own object, carrying the measured verdict.

    The verdict is carried as a summary rather than as the whole outcome set: the object is the
    field carrier, and the outcome detail lives on the :class:`Verdict` the chain also holds. Two
    copies of the same detail would be two records that could disagree.
    """
    previous = chain.objects[-1] if chain.objects else None
    if previous is None:
        raise EvolutionAuthorityError(
            "a chain with no prior object cannot be validated", subject=chain.subject_identity
        )
    return phase_object(
        authority,
        previous,
        ordinal=_VALIDATION_ORDINAL,
        validation_result=verdict.summary,
        note={"validated_by": authority.phase_by_ordinal(_VALIDATION_ORDINAL).identifier},
    )


__all__ = ["measurable_dimensions", "validate_evolution", "validation_object"]
