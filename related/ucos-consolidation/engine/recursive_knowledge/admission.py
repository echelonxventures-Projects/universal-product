"""URKE-000001 Part 08 — admission. Fourteen doors, one mechanism, no code change to walk through.

Every declared data vocabulary has an admission function, and every one does the same two things:
returns a *new* declaration carrying the member, and admits the member into the ledger as a governed
subject. Neither mutates anything — a declaration is frozen, and an extension that edited it in
place would make "what was declared when this was admitted" unanswerable.

The functions differ only in which tuple they extend, and that difference is mechanical. What
matters is what they have in common: none of them touches a file, none of them is a special case,
and none of them needs to exist before the thing it admits is imagined. That is the property
URKE-L-08 measures by fingerprinting this package before and after admitting twelve members nobody
declared.

:data:`ADMISSIONS` is bound to the declared extension points in both directions, so a door with no
function and a function no door names are both refusals at load time.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import replace
from types import MappingProxyType
from typing import Any

from engine.recursive_knowledge.composition import SITUATION_ROLE, situate
from engine.recursive_knowledge.declaration import (
    AxisSpec,
    Declaration,
    DiscoverySource,
    EvolutionSubject,
    GapClassSpec,
    Named,
    ProfileSpec,
    RealitySpec,
    RelationSpec,
    StateSpec,
    TemporalSpec,
)
from engine.recursive_knowledge.ledger import VOCABULARY_ROLE, KnowledgeLedger
from engine.recursive_knowledge.model import Evidence, GovernedEntity, RecursiveKnowledgeError

Admitted = tuple[Declaration, GovernedEntity]


class AdmissionError(RecursiveKnowledgeError):
    """The member cannot be admitted as declared. A fault, never a refusal of the future."""


def _record(
    ledger: KnowledgeLedger,
    *,
    natural_key: str,
    definition: str,
    origin: str,
    role: str | None = None,
    payload: Mapping[str, Any] | None = None,
) -> GovernedEntity:
    declaration = ledger.declaration
    body = dict(payload or {})
    body["definition"] = definition
    return ledger.admit(
        ledger.subject(
            natural_key=f"{origin}/{natural_key}",
            profile=declaration.profile_for(role or VOCABULARY_ROLE),
            domain=declaration.residual_domain,
            owner=declaration.artifact_id,
            origin=origin,
            title=natural_key,
            payload=body,
            evidence=(Evidence(source=origin, statement=definition),),
        )
    )


def _successor_mesh(declaration: Declaration, identifier: str) -> tuple[StateSpec, ...]:
    """Every existing state gains the newcomer as a successor, and it gains all of them.

    Without this an admitted state would be unreachable, which the lattice law would refuse — and
    correctly: a state nothing can move into is a state that exists only in a table.
    """
    grown = tuple(
        replace(spec, successors=tuple(sorted(set(spec.successors) | {identifier})))
        for spec in declaration.states
    )
    return grown


def admit_state(ledger: KnowledgeLedger, *, natural_key: str, definition: str) -> Admitted:
    """Admit a lifecycle state nobody declared, wired into the successor mesh both ways."""
    declaration = ledger.declaration
    if natural_key in set(declaration.state_ids):
        raise AdmissionError(f"state {natural_key!r} is already declared")
    if len(declaration.states) + 1 > declaration.state_bound:
        raise AdmissionError(
            f"admitting state {natural_key!r} would take the state count past the "
            f"declared bound of "
            f"{declaration.state_bound}; a lifecycle condition that genuinely needs a new state "
            "needs an architectural proposal, not an admission"
        )
        # The bound is the design rule made operational: data is free, structure is not.
    grown = _successor_mesh(declaration, natural_key)
    newcomer = StateSpec(
        identifier=natural_key,
        title=natural_key,
        state_class=declaration.state_classes[0].state_class,
        definition=definition,
        terminal=False,
        successors=tuple(sorted(declaration.state_ids)),
        binding=None,
        binding_gap=MappingProxyType(
            {
                "gap_id": f"URKE-G-RUNTIME/{natural_key}",
                "finding": "a state admitted at runtime holds its vocabulary locally until an "
                "owner carries a row for it",
                "referred_to": declaration.binding_owners[0].owner,
                "remediation": "propose a row with the named owner, or accept the local holding",
            }
        ),
        ucon_research_state=declaration.states[0].ucon_research_state,
    )
    extended = replace(declaration, states=grown + (newcomer,))
    return extended, _record(
        ledger, natural_key=natural_key, definition=definition, origin="states.seed"
    )


def admit_domain(ledger: KnowledgeLedger, *, natural_key: str, definition: str) -> Admitted:
    """Admit a domain nobody declared. This is how a future science arrives: one row."""
    declaration = ledger.declaration
    if natural_key in set(declaration.domain_ids):
        raise AdmissionError(f"domain {natural_key!r} is already declared")
    extended = replace(declaration, domains=declaration.domains + (Named(natural_key, definition),))
    return extended, _record(
        ledger, natural_key=natural_key, definition=definition, origin="domains.seed"
    )


def admit_qualifier_value(
    ledger: KnowledgeLedger, *, natural_key: str, definition: str
) -> Admitted:
    """Admit a value on the first declared qualifier. Where a state would otherwise have been "
    "added."""
    declaration = ledger.declaration
    target = declaration.qualifiers[0]
    if natural_key in target.values:
        raise AdmissionError(f"{natural_key!r} is already a value of {target.qualifier!r}")
    grown = tuple(
        replace(spec, values=spec.values + (natural_key,))
        if spec.qualifier == target.qualifier
        else spec
        for spec in declaration.qualifiers
    )
    return replace(declaration, qualifiers=grown), _record(
        ledger, natural_key=natural_key, definition=definition, origin="qualifiers.seed"
    )


def admit_relation(ledger: KnowledgeLedger, *, natural_key: str, definition: str) -> Admitted:
    """Admit a relation nobody declared. This is how an ontology grows without a type hierarchy."""
    declaration = ledger.declaration
    if natural_key in set(declaration.relation_ids):
        raise AdmissionError(f"relation {natural_key!r} is already declared")
    grown = declaration.relations + (
        RelationSpec(relation=natural_key, definition=definition, inverse=f"{natural_key}-of"),
    )
    return replace(declaration, relations=grown), _record(
        ledger, natural_key=natural_key, definition=definition, origin="relations.seed"
    )


def admit_profile(ledger: KnowledgeLedger, *, natural_key: str, definition: str) -> Admitted:
    """Admit a profile nobody declared. This is how a future construct arrives without a class."""
    declaration = ledger.declaration
    if natural_key in set(declaration.profile_ids):
        raise AdmissionError(f"profile {natural_key!r} is already declared")
    grown = declaration.profiles + (
        ProfileSpec(
            profile=natural_key,
            required_attributes=(),
            required_payload=(),
            definition=definition,
        ),
    )
    return replace(declaration, profiles=grown), _record(
        ledger, natural_key=natural_key, definition=definition, origin="profiles.seed"
    )


def admit_axis(ledger: KnowledgeLedger, *, natural_key: str, definition: str) -> Admitted:
    """Admit an independent lifecycle axis nobody declared."""
    declaration = ledger.declaration
    if natural_key in set(declaration.axis_ids):
        raise AdmissionError(f"axis {natural_key!r} is already declared")
    values = declaration.lifecycle_axes[0].values
    grown = declaration.lifecycle_axes + (
        AxisSpec(
            axis=natural_key,
            definition=definition,
            initial=declaration.unresolved_token,
            values=values,
        ),
    )
    return replace(declaration, lifecycle_axes=grown), _record(
        ledger, natural_key=natural_key, definition=definition, origin="lifecycle_axes.seed"
    )


def admit_gap_class(ledger: KnowledgeLedger, *, natural_key: str, definition: str) -> Admitted:
    """Admit a gap class nobody declared."""
    declaration = ledger.declaration
    if natural_key in set(declaration.gap_class_ids):
        raise AdmissionError(f"gap class {natural_key!r} is already declared")
    inherited = declaration.gap_class(declaration.residual_gap_class).ucon_unknown_class
    grown = declaration.gap_classes + (
        GapClassSpec(identifier=natural_key, definition=definition, ucon_unknown_class=inherited),
    )
    return replace(declaration, gap_classes=grown), _record(
        ledger, natural_key=natural_key, definition=definition, origin="gaps.classes"
    )


def admit_discovery_source(
    ledger: KnowledgeLedger, *, natural_key: str, definition: str
) -> Admitted:
    """Admit a discovery source. The detector it names must already exist, or nothing would run.

    This is the one admission with a precondition, and the precondition is the point: a source is a
    binding between a declared intent and an implemented detector, so admitting a source that named
    nothing would grow the declaration while measuring nothing.
    """
    declaration = ledger.declaration
    from engine.recursive_knowledge.discovery import available_detectors

    if natural_key in {spec.source_id for spec in declaration.discovery_sources}:
        raise AdmissionError(f"discovery source {natural_key!r} is already declared")
    template = declaration.discovery_sources[0]
    grown = declaration.discovery_sources + (
        DiscoverySource(
            source_id=natural_key,
            detector=template.detector,
            target=template.target,
            priority=declaration.priority_scale[-1],
            impact=declaration.impact_scale[-1],
            definition=definition,
        ),
    )
    if template.detector not in available_detectors():
        raise AdmissionError(
            f"the admitted source names detector {template.detector!r}, which nothing implements"
        )
    return replace(declaration, discovery_sources=grown), _record(
        ledger, natural_key=natural_key, definition=definition, origin="discovery.sources"
    )


def admit_evolution_subject(
    ledger: KnowledgeLedger, *, natural_key: str, definition: str
) -> Admitted:
    """Admit an evolvable subject nobody declared, carrying every declared operator."""
    declaration = ledger.declaration
    if natural_key in {spec.identifier for spec in declaration.evolution_subjects}:
        raise AdmissionError(f"evolution subject {natural_key!r} is already declared")
    grown = declaration.evolution_subjects + (
        EvolutionSubject(
            identifier=natural_key,
            definition=definition,
            operators=tuple(spec.identifier for spec in declaration.operators),
        ),
    )
    return replace(declaration, evolution_subjects=grown), _record(
        ledger, natural_key=natural_key, definition=definition, origin="evolution.subjects"
    )


def admit_learning_stage(ledger: KnowledgeLedger, *, natural_key: str, definition: str) -> Admitted:
    """Admit a learning stage, appended at the end so no existing ordering is disturbed."""
    declaration = ledger.declaration
    if natural_key in {spec.identifier for spec in declaration.learning_stages}:
        raise AdmissionError(f"learning stage {natural_key!r} is already declared")
    grown = declaration.learning_stages + (Named(natural_key, definition),)
    return replace(declaration, learning_stages=grown), _record(
        ledger, natural_key=natural_key, definition=definition, origin="learning.stages"
    )


def admit_reality(ledger: KnowledgeLedger, *, natural_key: str, definition: str) -> Admitted:
    """Admit a reality nobody has met. Every dimension is unresolved, which is the honest answer."""
    declaration = ledger.declaration
    if natural_key in set(declaration.reality_ids):
        raise AdmissionError(f"reality {natural_key!r} is already declared")
    systems = {
        dimension.identifier: declaration.unresolved_token
        for dimension in declaration.reality_dimensions
    }
    grown = declaration.realities + (
        RealitySpec(
            identifier=natural_key,
            title=definition,
            residual=False,
            frame_kind="",
            frame_kind_gap=MappingProxyType(
                {
                    "gap_id": f"URKE-G-RUNTIME/{natural_key}",
                    "finding": "a reality admitted at runtime binds to no frame kind until the "
                    "context authority declares one",
                    "referred_to": declaration.frame_kind_owner,
                    "remediation": "declare a frame kind for it, or record that none applies",
                }
            ),
            systems=MappingProxyType(systems),
        ),
    )
    return replace(declaration, realities=grown), _record(
        ledger,
        natural_key=natural_key,
        definition=definition,
        origin="reality.seed",
        payload={"systems": systems},
    )


def admit_temporal_system(
    ledger: KnowledgeLedger, *, natural_key: str, definition: str
) -> Admitted:
    """Admit a temporal system nobody declared, with its epoch unresolved rather than inherited."""
    declaration = ledger.declaration
    if natural_key in set(declaration.temporal_ids):
        raise AdmissionError(f"temporal system {natural_key!r} is already declared")
    residual = next(
        (spec for spec in declaration.temporal_systems if spec.epoch_gap is not None),
        declaration.temporal_systems[-1],
    )
    grown = declaration.temporal_systems + (
        TemporalSpec(
            identifier=natural_key,
            title=definition,
            system_type=residual.system_type,
            chronology_model=residual.chronology_model,
            epoch=declaration.temporal_unresolved_token,
            calendar_system=declaration.temporal_unresolved_token,
            causality_model=declaration.temporal_unresolved_token,
            reference_frame=declaration.temporal_unresolved_token,
            conversion_authority=declaration.temporal_unresolved_token,
            epoch_gap=MappingProxyType(
                {
                    "gap_id": f"URKE-G-RUNTIME/{natural_key}",
                    "finding": "a temporal system admitted at runtime declares no epoch, because "
                    "an inherited epoch would be an assumption about a chronology nobody has met",
                    "referred_to": declaration.chronology_owner,
                    "remediation": "declare its epoch when one is known",
                }
            ),
        ),
    )
    return replace(declaration, temporal_systems=grown), _record(
        ledger, natural_key=natural_key, definition=definition, origin="temporal.seed"
    )


def admit_context(ledger: KnowledgeLedger, *, natural_key: str, definition: str) -> Admitted:
    """Admit a context. A civilization, a substrate, a galaxy and a simulation all arrive here.

    Nothing about this function knows what a planet is. It admits a subject with the context profile
    and the residual context kind, and the caller's name for it is data.
    """
    declaration = ledger.declaration
    entity = ledger.admit(
        ledger.subject(
            natural_key=natural_key,
            profile=declaration.profile_for(SITUATION_ROLE),
            domain=declaration.residual_domain,
            owner=declaration.artifact_id,
            origin="context.kinds",
            title=definition,
            payload=dict(situate(declaration, declaration.residual_context_kind)),
            evidence=(Evidence(source="context.kinds", statement=definition),),
        )
    )
    return declaration, entity


def admit_architecture_proposal(
    ledger: KnowledgeLedger, *, natural_key: str, definition: str
) -> Admitted:
    """Admit a proposal to change the foundation itself. Delegates to the proposal mechanism.

    Present here so the extension point is exercisable like any other, and implemented there because
    a proposal carries seven requirements that no other admission carries.
    """
    from engine.recursive_knowledge.proposal import propose

    entity = propose(
        ledger,
        construct=natural_key,
        unrepresentable_because=definition,
        capability_gained="stated by the proposer",
        complexity_added="stated by the proposer",
        tradeoff_justification="stated by the proposer",
        impact="stated by the proposer",
        verification="pending",
        validation="pending",
        governance_decision="pending",
        owner=ledger.declaration.unassigned_owner,
    )
    return ledger.declaration, entity


#: Every declared extension point, mapped to the function that admits through it. Bound both ways.
ADMISSIONS: Mapping[str, Callable[..., Admitted]] = MappingProxyType(
    {
        "admit_architecture_proposal": admit_architecture_proposal,
        "admit_axis": admit_axis,
        "admit_context": admit_context,
        "admit_discovery_source": admit_discovery_source,
        "admit_domain": admit_domain,
        "admit_evolution_subject": admit_evolution_subject,
        "admit_gap_class": admit_gap_class,
        "admit_learning_stage": admit_learning_stage,
        "admit_profile": admit_profile,
        "admit_qualifier_value": admit_qualifier_value,
        "admit_reality": admit_reality,
        "admit_relation": admit_relation,
        "admit_state": admit_state,
        "admit_temporal_system": admit_temporal_system,
    }
)


def available_admissions() -> frozenset[str]:
    """The admissions this module implements — the set the declared doors are bound against."""
    return frozenset(ADMISSIONS)


def exercise(ledger: KnowledgeLedger, admission: str, *, suffix: str) -> Admitted:
    """Perform one admission with a generated member name. Used by the laws that measure "
    "openness."""
    function = ADMISSIONS.get(admission)
    if function is None:
        raise AdmissionError(f"{admission!r} is not an implemented admission")
    point = ledger.declaration.point_for_admission(admission)
    return function(
        ledger,
        natural_key=f"{point.point_id.lower()}-{suffix}",
        definition=f"admitted at runtime through {point.point_id} to measure that it can be",
    )


__all__ = [
    "ADMISSIONS",
    "AdmissionError",
    "admit_architecture_proposal",
    "admit_axis",
    "admit_context",
    "admit_discovery_source",
    "admit_domain",
    "admit_evolution_subject",
    "admit_gap_class",
    "admit_learning_stage",
    "admit_profile",
    "admit_qualifier_value",
    "admit_reality",
    "admit_relation",
    "admit_state",
    "admit_temporal_system",
    "available_admissions",
    "exercise",
]
