"""UCON-000001 Part 06 — the unknown, contradiction, research and discovery registries.

There are four registries here and exactly one store, which is the design decision worth
stating first. An unknown registry with its own table, a contradiction registry with its own
table and a research registry with a third would be three more places a governed object can
live, three more coverage questions, and three more owners for one concern — the defect the
repository's own ``DEC-MCOS-00R`` precedent refuses. So each of the four is a **projection**
over :class:`engine.construct.registry.ConstructRegistry`, selected by the facet its kind
declares. Registering an unknown is presenting a construct; querying the unknown registry is
filtering the one store. Nothing is duplicated and nothing can drift.

The registries in one sentence each:

    unknowns        constructs whose kind declares the ``unknown`` facet
    contradictions  constructs whose kind declares the ``contradiction`` facet
    research        constructs whose kind declares the ``research`` facet
    discovery       constructs whose kind declares the ``discovery`` facet

Two derivations make the system recursive rather than merely descriptive.
:func:`promote_to_research` turns any construct — most usefully an unknown — into a research
object whose lineage names its subject. :func:`discover` walks the whole registry against the
declared discovery sources and mints one discovery construct per unattended opportunity: every
unknown nobody is researching, every contradiction nobody is investigating, every escalation
(which is evidence of a gap in the rule set itself), every undecidable, every unresolved
dependency and every facet violation.

Both derivations are **idempotent by identity**, and that is what makes recursive discovery
terminate. A derived construct's natural key is a function of the subject it is about
(``discovery-of:<identity>``, with the prefix declared rather than written here), so the
identifier is determined by the subject rather than by when the walk happened. :func:`discover`
therefore checks whether the derived identity already exists and mints nothing when it does. A
second run over an unchanged registry returns an empty tuple and leaves the registry digest
byte-identical — the fixed point law UCON-L-07 measures, rather than a loop with a counter
holding it back.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from typing import Any

from engine.construct.declaration import DiscoverySource
from engine.construct.model import Construct, ConstructError, Evidence, Lineage, Presentation
from engine.construct.model import construct_id as derive_id
from engine.construct.registry import ConstructRegistry

#: The facet names the four projections select on. Read from the declaration's facet table by
#: every function below; named here only so a typo is a NameError rather than an empty result.
FACET_UNKNOWN = "unknown"
FACET_CONTRADICTION = "contradiction"
FACET_RESEARCH = "research"
FACET_DISCOVERY = "discovery"


class ViewError(ConstructError):
    """A projection was asked for something the declaration does not declare."""


def _kind_for_facet(registry: ConstructRegistry, facet: str) -> str:
    """The declared kind that carries ``facet`` and has no parent — the facet's root kind.

    Derived rather than hardcoded so that renaming a kind in the declaration does not silently
    strand a helper here. A facet carried by no kind is a fault: it would mean this module can
    project a population that can never be populated.
    """
    candidates = [
        spec.kind
        for spec in registry.declaration.kinds
        if spec.facet == facet and spec.parent is None
    ]
    if len(candidates) != 1:
        raise ViewError(
            f"the declaration carries {len(candidates)} root kinds for facet {facet!r}; "
            "exactly one is required for a projection to have a canonical registration kind"
        )
    return candidates[0]


# --- the four projections ---------------------------------------------------------------------


def unknowns(registry: ConstructRegistry) -> tuple[Construct, ...]:
    """Every registered unknown. A state, not an absence, and queryable as such."""
    return registry.of_facet(FACET_UNKNOWN)


def contradictions(registry: ConstructRegistry) -> tuple[Construct, ...]:
    """Every registered contradiction, resolved or standing. None is ever deleted."""
    return registry.of_facet(FACET_CONTRADICTION)


def research_objects(registry: ConstructRegistry) -> tuple[Construct, ...]:
    return registry.of_facet(FACET_RESEARCH)


def discovery_objects(registry: ConstructRegistry) -> tuple[Construct, ...]:
    return registry.of_facet(FACET_DISCOVERY)


def standing_contradictions(registry: ConstructRegistry) -> tuple[Construct, ...]:
    """Contradictions whose resolution state the declaration marks as still contradicting."""
    return tuple(
        construct
        for construct in contradictions(registry)
        if str(construct.presentation.payload.get("resolution_state") or "")
        in registry.declaration.contradicting_states
    )


# --- registration -----------------------------------------------------------------------------


def register_unknown(
    registry: ConstructRegistry,
    *,
    natural_key: str,
    unknown_class: str,
    domain: str,
    formulation: str,
    dependencies: Iterable[str] = (),
    evidence_gaps: Iterable[str] = (),
    presented_by: str = "",
) -> Construct:
    """Register an unknown as a first-class governed object.

    ``unknown_class`` is checked against the declared classes and refused when absent — but
    note that the declared classes include one for an unknown whose own class is unknown, so
    "we do not know what kind of not-knowing this is" is representable without weakening the
    check. That is the difference between an open vocabulary and an unchecked one.
    """
    if unknown_class not in registry.declaration.unknown_classes:
        raise ViewError(
            f"{unknown_class!r} is not a declared unknown class; declared classes are "
            f"{', '.join(registry.declaration.unknown_classes)}"
        )
    return registry.present(
        Presentation(
            kind=_kind_for_facet(registry, FACET_UNKNOWN),
            natural_key=natural_key,
            title=formulation,
            payload={
                "dependencies": list(dependencies),
                "domain": domain,
                "evidence_gaps": list(evidence_gaps),
                "formulation": formulation,
                "unknown_class": unknown_class,
            },
            dependencies=tuple(dependencies),
            lineage=Lineage(presented_by=presented_by),
        )
    )


def register_contradiction(
    registry: ConstructRegistry,
    *,
    natural_key: str,
    left: str,
    right: str,
    contradiction_class: str,
    resolution_state: str,
    detected_by: str = "",
    presented_by: str = "",
) -> Construct:
    """Register a contradiction. Neither side is deleted, and neither is preferred.

    A contradiction in a contradicting resolution state quarantines both constructs it names on
    their next presentation — via the registry's disposition context, not via an edit here — so
    registering a contradiction has an operational consequence rather than only a documentary
    one.
    """
    if contradiction_class not in registry.declaration.contradiction_classes:
        raise ViewError(f"{contradiction_class!r} is not a declared contradiction class")
    if resolution_state not in registry.declaration.resolution_states:
        raise ViewError(f"{resolution_state!r} is not a declared resolution state")
    return registry.present(
        Presentation(
            kind=_kind_for_facet(registry, FACET_CONTRADICTION),
            natural_key=natural_key,
            title=f"{left} contradicts {right}",
            payload={
                "contradiction_class": contradiction_class,
                "detected_by": detected_by,
                "left": left,
                "resolution_state": resolution_state,
                "right": right,
            },
            lineage=Lineage(derived_from=(left, right), presented_by=presented_by),
        )
    )


def register_research(
    registry: ConstructRegistry,
    *,
    natural_key: str,
    hypothesis: str,
    research_state: str,
    findings: Iterable[str] = (),
    open_questions: Iterable[str] = (),
    future_work: Iterable[str] = (),
    confidence: str = "",
    derived_from: Iterable[str] = (),
    evidence: Iterable[Evidence] = (),
    reality_status: str = "",
    presented_by: str = "",
) -> Construct:
    """Register a research object.

    ``confidence`` is a REFERENCE, never a number invented here: UKIP already owns confidence
    as a UCXI ``KNOWLEDGE`` context keyed on ``(knowledge_id, version)``
    (``engine/knowledge/ukip/confidence.py``). A float in this payload would be a second
    authority over the same quantity, so the field carries the context identifier and this
    capability computes no confidence of its own.
    """
    if research_state not in registry.declaration.research_states:
        raise ViewError(f"{research_state!r} is not a declared research state")
    return registry.present(
        Presentation(
            kind=_kind_for_facet(registry, FACET_RESEARCH),
            natural_key=natural_key,
            title=hypothesis,
            payload={
                "confidence": confidence,
                "findings": list(findings),
                "future_work": list(future_work),
                "hypothesis": hypothesis,
                "open_questions": list(open_questions),
                "research_state": research_state,
            },
            evidence=tuple(evidence),
            reality_status=reality_status,
            lineage=Lineage(derived_from=tuple(derived_from), presented_by=presented_by),
        )
    )


def register_discovery(
    registry: ConstructRegistry,
    *,
    natural_key: str,
    opportunity: str,
    priority: str,
    impact: str,
    evidence_gaps: Iterable[str] = (),
    derived_from: Iterable[str] = (),
    presented_by: str = "",
) -> Construct:
    """Register a governed discovery object with a declared priority and impact."""
    if priority not in registry.declaration.priority_scale:
        raise ViewError(f"{priority!r} is not a declared discovery priority")
    if impact not in registry.declaration.impact_scale:
        raise ViewError(f"{impact!r} is not a declared discovery impact")
    return registry.present(
        Presentation(
            kind=_kind_for_facet(registry, FACET_DISCOVERY),
            natural_key=natural_key,
            title=opportunity,
            payload={
                "evidence_gaps": list(evidence_gaps),
                "impact": impact,
                "opportunity": opportunity,
                "priority": priority,
            },
            lineage=Lineage(derived_from=tuple(derived_from), presented_by=presented_by),
        )
    )


# --- derivation --------------------------------------------------------------------------------


def research_key(registry: ConstructRegistry, subject: str) -> str:
    """The derived natural key of the research object about ``subject``."""
    return f"{registry.declaration.research_key_prefix}:{subject}"


def discovery_key(registry: ConstructRegistry, subject: str) -> str:
    """The derived natural key of the discovery object about ``subject``."""
    return f"{registry.declaration.discovery_key_prefix}:{subject}"


def research_identity(registry: ConstructRegistry, subject: str) -> str:
    """The identity the research object about ``subject`` would have, computed without minting."""
    return derive_id(_kind_for_facet(registry, FACET_RESEARCH), research_key(registry, subject))


def discovery_identity(registry: ConstructRegistry, subject: str) -> str:
    """The identity the discovery object about ``subject`` would have, without minting it."""
    return derive_id(_kind_for_facet(registry, FACET_DISCOVERY), discovery_key(registry, subject))


def promote_to_research(
    registry: ConstructRegistry, identity: str, *, hypothesis: str = ""
) -> Construct:
    """Transform any construct into a research object about it. Idempotent by identity.

    This is the operational content of "every unknown construct must be transformable into a
    research object": the transformation exists, it is one call, and it works on *any*
    construct rather than only on those the foundation anticipated. The research object starts
    in the declared first research state with the subject's own formulation as its hypothesis,
    and its lineage names the subject, so the chain from "we do not know" to "we are finding
    out" is traceable in both directions.
    """
    subject = registry.get(identity)
    existing = research_identity(registry, identity)
    if registry.has(existing):
        return registry.get(existing)
    stated = (
        hypothesis
        or str(subject.presentation.payload.get("formulation") or "")
        or subject.presentation.title
    )
    return register_research(
        registry,
        natural_key=research_key(registry, identity),
        hypothesis=stated,
        research_state=registry.declaration.research_states[0],
        open_questions=(stated,),
        derived_from=(identity,),
        presented_by=registry.declaration.artifact_id,
    )


# --- the declared discovery selectors ------------------------------------------------------------


def _facet_is(
    registry: ConstructRegistry, construct: Construct, arguments: Mapping[str, Any]
) -> bool:
    return registry.facet_of(construct.kind) == str(arguments.get("facet"))


def _disposition_is(
    registry: ConstructRegistry, construct: Construct, arguments: Mapping[str, Any]
) -> bool:
    return construct.disposition.disposition == str(arguments.get("disposition"))


def _unresolved_dependency(
    registry: ConstructRegistry, construct: Construct, arguments: Mapping[str, Any]
) -> bool:
    return any(not registry.has(dependency) for dependency in construct.presentation.dependencies)


def _has_facet_violation(
    registry: ConstructRegistry, construct: Construct, arguments: Mapping[str, Any]
) -> bool:
    return bool(construct.facet_violations)


#: The implemented discovery selectors. Two-way bound to the declared sources at load, on the
#: same terms as the disposition operators: nothing here may go unclaimed, and no source may
#: name something absent here.
SELECTORS: Mapping[str, Callable[[ConstructRegistry, Construct, Mapping[str, Any]], bool]] = {
    "disposition_is": _disposition_is,
    "facet_is": _facet_is,
    "has_facet_violation": _has_facet_violation,
    "unresolved_dependency": _unresolved_dependency,
}


def available_selectors() -> frozenset[str]:
    """The selector names this module implements — the set the declaration is bound against."""
    return frozenset(SELECTORS)


def _selects(registry: ConstructRegistry, source: DiscoverySource, construct: Construct) -> bool:
    selector = SELECTORS.get(source.selector)
    if selector is None:
        raise ViewError(
            f"{source.source_id}: selector {source.selector!r} is declared but not implemented"
        )
    return selector(registry, construct, source.arguments)


def opportunities(registry: ConstructRegistry) -> tuple[tuple[DiscoverySource, Construct], ...]:
    """Every (source, construct) pair the declared sources select, whether attended or not.

    Separated from :func:`discover` so the question "what is discoverable" can be answered
    without minting anything — a read that changes the thing it reads is a read nobody can
    trust twice.
    """
    found: list[tuple[DiscoverySource, Construct]] = []
    for construct in registry.all():
        if registry.facet_of(construct.kind) == FACET_DISCOVERY:
            continue
        for source in registry.declaration.discovery_sources:
            if _selects(registry, source, construct):
                found.append((source, construct))
    return tuple(found)


def discover(registry: ConstructRegistry) -> tuple[Construct, ...]:
    """Mint one discovery construct per unattended opportunity. Returns only what was new.

    Recursive: the discovery constructs it mints are themselves constructs in the same registry,
    so a later walk sees them — and terminating, because an opportunity whose discovery object
    already exists is skipped by identity rather than by a visited-set the caller has to
    maintain. Running this twice over an unchanged registry returns ``()`` the second time,
    which is the fixed point law UCON-L-07 measures.
    """
    minted: list[Construct] = []
    for source, construct in opportunities(registry):
        target = discovery_identity(registry, construct.identity)
        if registry.has(target):
            continue
        minted.append(
            register_discovery(
                registry,
                natural_key=discovery_key(registry, construct.identity),
                opportunity=(
                    f"{source.opportunity} "
                    f"[{construct.kind}: {construct.presentation.natural_key}]"
                ),
                priority=source.priority,
                impact=source.impact,
                evidence_gaps=(
                    tuple(construct.facet_violations)
                    + tuple(
                        f"unresolved dependency: {dependency}"
                        for dependency in construct.presentation.dependencies
                        if not registry.has(dependency)
                    )
                ),
                derived_from=(construct.identity,),
                presented_by=source.source_id,
            )
        )
    return tuple(minted)


def discovery_report(registry: ConstructRegistry) -> dict[str, Any]:
    """A deterministic account of the discovery population, by priority and by impact."""
    objects = discovery_objects(registry)
    by_priority = {name: 0 for name in registry.declaration.priority_scale}
    by_impact = {name: 0 for name in registry.declaration.impact_scale}
    for construct in objects:
        priority = str(construct.presentation.payload.get("priority") or "")
        impact = str(construct.presentation.payload.get("impact") or "")
        by_priority[priority] = by_priority.get(priority, 0) + 1
        by_impact[impact] = by_impact.get(impact, 0) + 1
    return {
        "by_impact": dict(sorted(by_impact.items())),
        "by_priority": dict(sorted(by_priority.items())),
        "contradictions": len(contradictions(registry)),
        "discovery_objects": len(objects),
        "opportunities": len(opportunities(registry)),
        "research_objects": len(research_objects(registry)),
        "standing_contradictions": len(standing_contradictions(registry)),
        "unknowns": len(unknowns(registry)),
    }


__all__ = [
    "FACET_CONTRADICTION",
    "FACET_DISCOVERY",
    "FACET_RESEARCH",
    "FACET_UNKNOWN",
    "SELECTORS",
    "ViewError",
    "available_selectors",
    "contradictions",
    "discover",
    "discovery_identity",
    "discovery_key",
    "discovery_objects",
    "discovery_report",
    "opportunities",
    "promote_to_research",
    "register_contradiction",
    "register_discovery",
    "register_research",
    "register_unknown",
    "research_identity",
    "research_key",
    "research_objects",
    "standing_contradictions",
    "unknowns",
]
