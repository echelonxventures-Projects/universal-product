"""URKE-000001 Part 12 — discovery as a permanent operating mode, and the reality probes.

Seventeen detectors read the ledger and return what they found. :func:`discover` admits each finding
as a governed subject, mints nothing twice, and reaches a fixed point — which is measurable
precisely because a finding's identity is derived from what it is about rather than from when it was
found.

This module writes nothing outside the ledger. There is no filesystem call reachable from it, and
the law that says so parses this file for the declared forbidden calls rather than trusting the
sentence you are reading.

The reality probes are the other half: they compare what this capability declares against what the
world actually carries. When they disagree, the disagreement is admitted as a contradiction and the
law refuses — reality is not corrected to match the declaration.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from types import MappingProxyType
from typing import Any

from engine.recursive_knowledge.declaration import Declaration, DiscoverySource
from engine.recursive_knowledge.ledger import KnowledgeLedger
from engine.recursive_knowledge.model import (
    Evidence,
    GovernedEntity,
    Lineage,
    RecursiveKnowledgeError,
)

#: The role a finding is admitted under. A code symbol the declaration binds to a profile.
FINDING_ROLE = "finding"

Finding = tuple[str, str]


class DiscoveryError(RecursiveKnowledgeError):
    """A detector or probe cannot run. A fault, never a finding."""


def _profile(ledger: KnowledgeLedger, role: str) -> str:
    return ledger.declaration.profile_for(role)


def scope(ledger: KnowledgeLedger) -> tuple[GovernedEntity, ...]:
    """The subjects discovery inspects: everything except its own findings.

    Measured reason, not preference: with findings in scope each pass reported on the previous
    pass's reports and the engine never converged. The exclusion is declared, narrow, and its cost
    is disclosed as a governed gap rather than absorbed silently.
    """
    excluded = ledger.declaration.profile_for(ledger.declaration.discovery_scope_excludes_role)
    return tuple(item for item in ledger.all() if item.classification != excluded)


# --- detectors ----------------------------------------------------------------------------


def unknown_without_research(
    ledger: KnowledgeLedger, source: DiscoverySource
) -> tuple[Finding, ...]:
    from engine.recursive_knowledge.research import research_for
    from engine.recursive_knowledge.states import settled
    from engine.recursive_knowledge.subjects import DISCLOSURE_ROLE

    return tuple(
        (item.identity, f"{item.natural_key} is unresolved and nothing is investigating it")
        for item in ledger.of_profile(_profile(ledger, DISCLOSURE_ROLE))
        if not settled(ledger.declaration, item.state) and not research_for(ledger, item.identity)
    )


def contradiction_without_resolution_path(
    ledger: KnowledgeLedger, source: DiscoverySource
) -> tuple[Finding, ...]:
    from engine.recursive_knowledge.subjects import CONFLICT_ROLE

    standing = {
        spec.identifier for spec in ledger.declaration.resolution_states if spec.contradicting
    }
    return tuple(
        (item.identity, f"{item.natural_key} stands with no attempt at resolution recorded")
        for item in ledger.of_profile(_profile(ledger, CONFLICT_ROLE))
        if item.resolution_status in standing and len(item.resolution_history) <= 1
    )


def subject_without_owner(ledger: KnowledgeLedger, source: DiscoverySource) -> tuple[Finding, ...]:
    token = ledger.declaration.unassigned_owner
    return tuple(
        (item.identity, f"{item.natural_key} has no owner assigned")
        for item in scope(ledger)
        if item.owner == token
    )


def gap_overdue_for_review(ledger: KnowledgeLedger, source: DiscoverySource) -> tuple[Finding, ...]:
    from engine.recursive_knowledge.subjects import overdue

    return tuple(
        (item.identity, f"{item.natural_key} is past its review point") for item in overdue(ledger)
    )


def state_without_successor(
    ledger: KnowledgeLedger, source: DiscoverySource
) -> tuple[Finding, ...]:
    return tuple(
        (spec.identifier, f"state {spec.identifier} is a dead end")
        for spec in ledger.declaration.states
        if not spec.successors
    )


def vocabulary_binding_gap(ledger: KnowledgeLedger, source: DiscoverySource) -> tuple[Finding, ...]:
    return tuple(
        (spec.identifier, f"state {spec.identifier} holds its vocabulary locally")
        for spec in ledger.declaration.states
        if spec.binding is None
    )


def subject_without_governance(
    ledger: KnowledgeLedger, source: DiscoverySource
) -> tuple[Finding, ...]:
    roles = {spec.identifier for spec in ledger.declaration.ownership_roles}
    return tuple(
        (item.identity, f"{item.natural_key} names no resolvable governing authority")
        for item in scope(ledger)
        if not item.governance.strip() or item.governance not in roles
    )


def research_without_evidence(
    ledger: KnowledgeLedger, source: DiscoverySource
) -> tuple[Finding, ...]:
    from engine.recursive_knowledge.research import INVESTIGATION_ROLE

    return tuple(
        (item.identity, f"{item.natural_key} is open and has gathered nothing")
        for item in ledger.of_profile(_profile(ledger, INVESTIGATION_ROLE))
        if not item.evidence
    )


def reality_dimension_unresolved(
    ledger: KnowledgeLedger, source: DiscoverySource
) -> tuple[Finding, ...]:
    token = ledger.declaration.unresolved_token
    found: list[Finding] = []
    for spec in ledger.declaration.realities:
        for dimension in spec.unresolved(token):
            found.append(
                (
                    f"{spec.identifier}/{dimension}",
                    f"{spec.identifier} leaves {dimension} unresolved",
                )
            )
    return tuple(found)


def temporal_epoch_unresolved(
    ledger: KnowledgeLedger, source: DiscoverySource
) -> tuple[Finding, ...]:
    token = ledger.declaration.temporal_unresolved_token
    return tuple(
        (spec.identifier, f"{spec.identifier} declares no epoch")
        for spec in ledger.declaration.temporal_systems
        if spec.epoch == token
    )


def domain_without_subject(ledger: KnowledgeLedger, source: DiscoverySource) -> tuple[Finding, ...]:
    populated = {str(item.payload.get("domain") or "") for item in scope(ledger)}
    return tuple(
        (spec.identifier, f"domain {spec.identifier} is named and nothing is recorded in it")
        for spec in ledger.declaration.domains
        if spec.identifier not in populated
    )


def qualifier_value_unused(ledger: KnowledgeLedger, source: DiscoverySource) -> tuple[Finding, ...]:
    used: set[tuple[str, str]] = set()
    for item in scope(ledger):
        for name, value in dict(item.payload.get("qualifiers") or {}).items():
            used.add((str(name), str(value)))
    return tuple(
        (f"{spec.qualifier}/{value}", f"{spec.qualifier} value {value} classifies nothing")
        for spec in ledger.declaration.qualifiers
        for value in spec.values
        if (spec.qualifier, value) not in used
    )


def subject_without_verification(
    ledger: KnowledgeLedger, source: DiscoverySource
) -> tuple[Finding, ...]:
    return tuple(
        (item.identity, f"{item.natural_key} carries no verification")
        for item in scope(ledger)
        if not item.verification_history
        and item.classification != ledger.declaration.default_profile
    )


def subject_without_definition(
    ledger: KnowledgeLedger, source: DiscoverySource
) -> tuple[Finding, ...]:
    from engine.recursive_knowledge.ledger import VOCABULARY_ROLE

    return tuple(
        (item.identity, f"{item.natural_key} carries no definition")
        for item in ledger.of_profile(_profile(ledger, VOCABULARY_ROLE))
        if not str(item.payload.get("definition") or "").strip()
    )


def relation_without_basis(ledger: KnowledgeLedger, source: DiscoverySource) -> tuple[Finding, ...]:
    return tuple(
        (item.identity, f"{item.natural_key} is a link nobody has to account for")
        for item in scope(ledger)
        if item.relation and not item.basis.strip()
    )


def subject_without_context(
    ledger: KnowledgeLedger, source: DiscoverySource
) -> tuple[Finding, ...]:
    return tuple(
        (item.identity, f"{item.natural_key} sits in no context")
        for item in scope(ledger)
        if not item.context.strip() or not ledger.has(item.context)
    )


def residual_population(ledger: KnowledgeLedger, source: DiscoverySource) -> tuple[Finding, ...]:
    """Everything resting in a residual. The nearest available proxy for what no detector can "
    "see."""
    residual = ledger.declaration.residual_domain
    return tuple(
        (item.identity, f"{item.natural_key} rests in the residual domain")
        for item in scope(ledger)
        if str(item.payload.get("domain") or "") == residual
    )


#: Every declared source, mapped to the detector that serves it. Bound both ways at load time.
DETECTORS: Mapping[str, Callable[[KnowledgeLedger, DiscoverySource], tuple[Finding, ...]]] = (
    MappingProxyType(
        {
            "contradiction_without_resolution_path": contradiction_without_resolution_path,
            "domain_without_subject": domain_without_subject,
            "gap_overdue_for_review": gap_overdue_for_review,
            "qualifier_value_unused": qualifier_value_unused,
            "reality_dimension_unresolved": reality_dimension_unresolved,
            "relation_without_basis": relation_without_basis,
            "research_without_evidence": research_without_evidence,
            "residual_population": residual_population,
            "state_without_successor": state_without_successor,
            "subject_without_context": subject_without_context,
            "subject_without_definition": subject_without_definition,
            "subject_without_governance": subject_without_governance,
            "subject_without_owner": subject_without_owner,
            "subject_without_verification": subject_without_verification,
            "temporal_epoch_unresolved": temporal_epoch_unresolved,
            "unknown_without_research": unknown_without_research,
            "vocabulary_binding_gap": vocabulary_binding_gap,
        }
    )
)


def available_detectors() -> frozenset[str]:
    return frozenset(DETECTORS)


def opportunities(ledger: KnowledgeLedger) -> tuple[tuple[DiscoverySource, Finding], ...]:
    """Run every declared detector and return what they found. Mints nothing."""
    found: list[tuple[DiscoverySource, Finding]] = []
    for source in ledger.declaration.discovery_sources:
        detector = DETECTORS.get(source.detector)
        if detector is None:
            raise DiscoveryError(
                f"source {source.source_id!r} names detector {source.detector!r}, which nothing "
                "implements"
            )
        for finding in detector(ledger, source):
            found.append((source, finding))
    return tuple(found)


def discover(ledger: KnowledgeLedger) -> tuple[GovernedEntity, ...]:
    """Admit every finding not already recorded. Returns only what was new this pass.

    A second pass over an unchanged ledger returns nothing, because a finding's natural key is
    derived from the source and the subject it is about. That is the fixed point, and it is a
    property of the
    identity function rather than of a de-duplication list somebody has to maintain.
    """
    declaration = ledger.declaration
    minted: list[GovernedEntity] = []
    for source, (about, statement) in opportunities(ledger):
        natural_key = f"{source.source_id}/{about}"
        entity = ledger.subject(
            natural_key=natural_key,
            profile=_profile(ledger, FINDING_ROLE),
            domain=declaration.residual_domain,
            owner=declaration.artifact_id,
            origin=source.source_id,
            title=statement,
            payload={
                "impact": source.impact,
                "priority": source.priority,
                "target": source.target,
            },
            evidence=(Evidence(source=source.source_id, statement=statement, independent=False),),
            lineage=Lineage(derived_from=(about,), presented_by=source.source_id),
        )
        if ledger.has(entity.identity):
            continue
        minted.append(ledger.admit(entity))
    return tuple(minted)


def report(ledger: KnowledgeLedger) -> dict[str, Any]:
    """What discovery currently sees, grouped the way the declared scales group it."""
    found = opportunities(ledger)
    by_priority: dict[str, int] = {}
    by_target: dict[str, int] = {}
    for source, _ in found:
        by_priority[source.priority] = by_priority.get(source.priority, 0) + 1
        by_target[source.target] = by_target.get(source.target, 0) + 1
    return {
        "by_priority": dict(sorted(by_priority.items())),
        "by_target": dict(sorted(by_target.items())),
        "findings": len(found),
        "sources": len(ledger.declaration.discovery_sources),
    }


# --- reality probes -----------------------------------------------------------------------


def state_binding_reality(declaration: Declaration, *, repository: str) -> list[str]:
    from engine.recursive_knowledge.states import binding_problems

    return binding_problems(declaration)


def _ucon_declaration(repository: str) -> Any:
    from engine.construct.declaration import load_declaration as load_ucon

    return load_ucon(repository=repository)


def gap_class_binding_reality(declaration: Declaration, *, repository: str) -> list[str]:
    ucon = _ucon_declaration(repository)
    live = set(ucon.unknown_classes)
    return [
        f"gap class {spec.identifier!r} binds to unknown class {spec.ucon_unknown_class!r}, which "
        "the construct foundation does not declare"
        for spec in declaration.gap_classes
        if spec.ucon_unknown_class not in live
    ]


def reality_frame_reality(declaration: Declaration, *, repository: str) -> list[str]:
    from engine.recursive_knowledge.worlds import reality_problems

    return reality_problems(declaration, repository=repository)


def temporal_system_type_reality(declaration: Declaration, *, repository: str) -> list[str]:
    from engine.recursive_knowledge.worlds import temporal_problems

    return temporal_problems(declaration)


def research_state_mapping_reality(declaration: Declaration, *, repository: str) -> list[str]:
    ucon = _ucon_declaration(repository)
    live = set(ucon.research_states)
    return [
        f"state {spec.identifier!r} maps to research state {spec.ucon_research_state!r}, which the "
        "construct foundation does not declare"
        for spec in declaration.states
        if spec.ucon_research_state not in live
    ]


def contradiction_binding_reality(declaration: Declaration, *, repository: str) -> list[str]:
    ucon = _ucon_declaration(repository)
    classes = set(ucon.contradiction_classes)
    resolutions = set(ucon.resolution_states)
    problems = [
        f"contradiction class {spec.identifier!r} binds to "
        f"{spec.ucon_contradiction_class!r}, which "
        "the construct foundation does not declare"
        for spec in declaration.contradiction_classes
        if spec.ucon_contradiction_class not in classes
    ]
    problems.extend(
        f"resolution state {spec.identifier!r} binds to {spec.ucon_resolution_state!r}, which the "
        "construct foundation does not declare"
        for spec in declaration.resolution_states
        if spec.ucon_resolution_state not in resolutions
    )
    return problems


#: Every declared probe, mapped to the comparison it performs. Bound both ways at load time.
REALITY_PROBES: Mapping[str, Callable[..., list[str]]] = MappingProxyType(
    {
        "contradiction_binding_reality": contradiction_binding_reality,
        "gap_class_binding_reality": gap_class_binding_reality,
        "reality_frame_reality": reality_frame_reality,
        "research_state_mapping_reality": research_state_mapping_reality,
        "state_binding_reality": state_binding_reality,
        "temporal_system_type_reality": temporal_system_type_reality,
    }
)


def available_probes() -> frozenset[str]:
    return frozenset(REALITY_PROBES)


def probe_all(declaration: Declaration, *, repository: str) -> dict[str, list[str]]:
    """Run every declared probe. A non-empty list is a divergence, not an error."""
    results: dict[str, list[str]] = {}
    for spec in declaration.reality_probes:
        probe = REALITY_PROBES.get(spec.probe)
        if probe is None:
            raise DiscoveryError(
                f"probe {spec.probe_id!r} names {spec.probe!r}, which nothing implements"
            )
        results[spec.probe_id] = list(probe(declaration, repository=repository))
    return results


__all__ = [
    "DETECTORS",
    "scope",
    "FINDING_ROLE",
    "REALITY_PROBES",
    "DiscoveryError",
    "available_detectors",
    "available_probes",
    "discover",
    "opportunities",
    "probe_all",
    "report",
]
