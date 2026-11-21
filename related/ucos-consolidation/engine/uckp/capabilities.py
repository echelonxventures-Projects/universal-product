"""UCKP Layer Zero — every layer capability, as canonical knowledge objects.

Article 2 does not exempt the machinery. A projection kind, a persistence technology,
an execution technology, an evolution stage, a governance rule and a mode of reasoning
are all governed categories, so each must have exactly one canonical home — otherwise
the parts of the system that *enforce* the constitution would be the only parts living
outside it.

Giving each capability an object is also what makes several invariants measurable
rather than rhetorical. "Two or more execution technologies satisfy the identical
contract" (UCKP-INV-09) is a claim about a population, and a population you cannot
enumerate from the universe itself is a population you cannot count. Here every
adapter, stage, rule and reasoner is a node with an authority chain to the article
that authorises it, so the count is derived from the universe and never asserted
beside it.

Like :mod:`engine.uckp.constitution`, every value is derived from the module that owns
it — :mod:`engine.uckp.projection`, :mod:`engine.uckp.persistence`,
:mod:`engine.uckp.execution`, :mod:`engine.uckp.evolution`,
:mod:`engine.uckp.governance`, :mod:`engine.uckp.intelligence` — so no capability is
described twice. The module is a provider, so discovery finds all of it by walking the
package (Article 8).
"""

from __future__ import annotations

from engine.uckp.constitution import (
    CONSTITUTION_NAMESPACE,
    CONSTITUTIONAL_OWNER,
    UNIVERSAL_PERSISTENCE,
    UNIVERSAL_PROJECTIONS,
    UNIVERSAL_RUNTIMES,
)
from engine.uckp.evolution import EVOLUTION_CYCLE, EvolutionStage, next_stage
from engine.uckp.execution import KNOWN_EXECUTION_KINDS, OPERATIONS
from engine.uckp.governance import GovernanceRule, build_rules
from engine.uckp.identity import urn_for
from engine.uckp.intelligence import reasoning_kinds
from engine.uckp.law import ROOT_LAW
from engine.uckp.persistence import KNOWN_PERSISTENCE_KINDS
from engine.uckp.projection import KNOWN_PROJECTION_KINDS
from engine.uckp.ucko import UCKO
from engine.uckp.values import Relationship

PROJECTION_INSTRUMENT = "engine.uckp.projection"
PERSISTENCE_INSTRUMENT = "engine.uckp.persistence"
EXECUTION_INSTRUMENT = "engine.uckp.execution"
EVOLUTION_INSTRUMENT = "engine.uckp.evolution"
GOVERNANCE_INSTRUMENT = "engine.uckp.governance"
INTELLIGENCE_INSTRUMENT = "engine.uckp.intelligence"

#: Which article authorises which capability family. Derived authority, not assumed:
#: a capability whose article is not named has no constitutional basis to exist.
AUTHORISING_ARTICLES: dict[str, str] = {
    "projection": "UCKP-ART-11",
    "persistence": "UCKP-ART-09",
    "execution": "UCKP-ART-10",
    "evolution": "UCKP-ART-14",
    "intelligence": "UCKP-ART-15",
}


def _capability(
    *,
    local_name: str,
    concept: str,
    definition: str,
    kind: str,
    category: str,
    parent_article: str,
    instrument: str,
    extra_relationships: tuple[Relationship, ...] = (),
    keywords: tuple[str, ...] = (),
    metadata: dict[str, object] | None = None,
) -> UCKO:
    parent_urn = urn_for(CONSTITUTION_NAMESPACE, parent_article)
    return UCKO.mint(
        namespace=CONSTITUTION_NAMESPACE,
        local_name=local_name,
        concept=concept,
        definition=definition,
        kind=kind,
        category=category,
        authority_tier="architectural",
        derives_from=parent_urn,
        owner=CONSTITUTIONAL_OWNER,
        # ``implemented``, not ``operational``. The capability exists in code, which is
        # what ``implemented`` claims; ``operational`` is the stronger claim that it has
        # been validated in service, and consistency reasoning correctly reports an
        # object that is operational while its validation facet is unattested. The
        # lawful route to ``operational`` runs through an attestation, so minting there
        # directly would be asserting a judgement nobody has made.
        lifecycle="implemented",
        instrument=instrument,
        provider="engine.uckp.capabilities",
        relationships=(
            Relationship("derived-from", parent_urn, "authority"),
            *extra_relationships,
        ),
        dependencies=(parent_urn,),
        keywords=keywords,
        metadata=metadata or {},
        runtime_bindings=UNIVERSAL_RUNTIMES,
        projection_bindings=UNIVERSAL_PROJECTIONS,
        persistence_bindings=UNIVERSAL_PERSISTENCE,
    )


def projection_objects() -> tuple[UCKO, ...]:
    """One object per projection kind — every view the universe can generate."""
    return tuple(
        _capability(
            local_name=f"UCKP-PROJECTION-{kind}",
            concept=f"{kind} projection",
            definition=(
                f"the {kind} view of the canonical universe; generated, and holding no "
                "independent architectural authority"
            ),
            kind="pattern",
            category="artifact",
            parent_article=AUTHORISING_ARTICLES["projection"],
            instrument=PROJECTION_INSTRUMENT,
            keywords=("projection", kind, "generated"),
            metadata={"projection_kind": kind, "authoritative": "false"},
        )
        for kind in KNOWN_PROJECTION_KINDS
    )


def persistence_objects() -> tuple[UCKO, ...]:
    """One object per persistence technology — every mechanism that may hold a copy."""
    return tuple(
        _capability(
            local_name=f"UCKP-PERSISTENCE-{kind}",
            concept=f"{kind} persistence",
            definition=(
                f"the {kind} mechanism for storing the canonical universe; it satisfies the "
                "identical constitutional persistence contract and owns no knowledge"
            ),
            kind="pattern",
            category="capability",
            parent_article=AUTHORISING_ARTICLES["persistence"],
            instrument=PERSISTENCE_INSTRUMENT,
            keywords=("persistence", kind, "interchangeable"),
            metadata={"persistence_kind": kind, "owns_knowledge": "false"},
        )
        for kind in KNOWN_PERSISTENCE_KINDS
    )


def execution_objects() -> tuple[UCKO, ...]:
    """One object per execution technology — every environment that may act."""
    return tuple(
        _capability(
            local_name=f"UCKP-EXECUTION-{kind}",
            concept=f"{kind} execution",
            definition=(
                f"the {kind} environment for acting on the canonical universe; it satisfies the "
                "identical constitutional execution contract and owns no knowledge"
            ),
            kind="pattern",
            category="runtime",
            parent_article=AUTHORISING_ARTICLES["execution"],
            instrument=EXECUTION_INSTRUMENT,
            keywords=("execution", kind, "interchangeable"),
            metadata={
                "execution_kind": kind,
                "owns_knowledge": "false",
                "operations": ",".join(sorted(OPERATIONS)),
            },
        )
        for kind in KNOWN_EXECUTION_KINDS
    )


def evolution_stage_object(stage: EvolutionStage) -> UCKO:
    """One evolution stage, related to the stage that always follows it.

    The successor relationship is what makes non-termination visible in the graph:
    every stage points at a next stage, so there is no node from which evolution
    cannot continue (UCKP-INV-13).
    """
    successor = next_stage(stage)
    return _capability(
        local_name=f"UCKP-STAGE-{stage.value}",
        concept=f"{stage.value} stage",
        definition=(
            f"the {stage.value} stage of the perpetual constitutional evolution cycle; "
            f"it is always followed by {successor.value}, so evolution never terminates"
        ),
        kind="pattern",
        category="transition",
        parent_article=AUTHORISING_ARTICLES["evolution"],
        instrument=EVOLUTION_INSTRUMENT,
        extra_relationships=(
            Relationship(
                "produces",
                urn_for(CONSTITUTION_NAMESPACE, f"UCKP-STAGE-{successor.value}"),
                "evolution",
            ),
        ),
        keywords=("evolution", "stage", stage.value),
        metadata={
            "stage": stage.value,
            "successor": successor.value,
            "terminal": "false",
            "position": str(EVOLUTION_CYCLE.index(stage)),
        },
    )


def evolution_objects() -> tuple[UCKO, ...]:
    return tuple(evolution_stage_object(stage) for stage in EVOLUTION_CYCLE)


def governance_rule_object(rule: GovernanceRule) -> UCKO:
    """One governance rule, deriving from the article it executes.

    The rule's parent is its own article rather than a generic governance article:
    a rule that executes Article 9 draws its force from Article 9, and recording that
    is what makes the authority chain of a decision traceable to the clause it applied.

    The definition *names* the article it enforces instead of repeating the clause.
    ``build_rules`` already derives ``rule.statement`` from ``article.clause``, so the
    text has exactly one home in code — but copying it into a second object's semantic
    identity would give it a second home in the *graph*, which is the same duplication
    seen from the other side. The ``implements`` relationship is how a reader gets from
    the rule to the clause.
    """
    parent_urn = urn_for(CONSTITUTION_NAMESPACE, rule.article_id)
    article = ROOT_LAW.article(rule.article_id)
    relationships = [
        Relationship("derived-from", parent_urn, "authority"),
        Relationship("implements", parent_urn, "governance"),
    ]
    for invariant_id in rule.invariants:
        relationships.append(
            Relationship("validates", urn_for(CONSTITUTION_NAMESPACE, invariant_id), "validation")
        )
    return UCKO.mint(
        namespace=CONSTITUTION_NAMESPACE,
        local_name=rule.rule_id,
        concept=f"governance rule {rule.rule_id.removeprefix('UCKP-RULE-')}",
        definition=(
            f"the executable rule by which governance enforces {rule.article_id} "
            f"({article.title}); the clause it enforces is declared once, by that article"
        ),
        kind="rule",
        category="governance",
        authority_tier="constitutional",
        derives_from=parent_urn,
        owner=CONSTITUTIONAL_OWNER,
        lifecycle="implemented",
        instrument=GOVERNANCE_INSTRUMENT,
        provider="engine.uckp.capabilities",
        relationships=tuple(relationships),
        dependencies=(parent_urn,),
        keywords=("governance", "rule", "executable"),
        metadata={
            "article_id": rule.article_id,
            "article_title": article.title,
            "clause_home": parent_urn,
            "invariants": ",".join(rule.invariants),
        },
        runtime_bindings=UNIVERSAL_RUNTIMES,
        projection_bindings=UNIVERSAL_PROJECTIONS,
        persistence_bindings=UNIVERSAL_PERSISTENCE,
    )


def governance_objects() -> tuple[UCKO, ...]:
    return tuple(governance_rule_object(rule) for rule in build_rules())


def reasoning_objects() -> tuple[UCKO, ...]:
    """One object per mode of reasoning the universe performs about itself."""
    return tuple(
        _capability(
            local_name=f"UCKP-REASONING-{kind}",
            concept=f"{kind} reasoning",
            definition=(
                f"the {kind} mode by which the canonical universe reasons about itself; "
                "every finding is derived from the declared universe, never assumed"
            ),
            kind="pattern",
            category="observation",
            parent_article=AUTHORISING_ARTICLES["intelligence"],
            instrument=INTELLIGENCE_INSTRUMENT,
            keywords=("intelligence", "reasoning", kind),
            metadata={"reasoning_kind": kind},
        )
        for kind in reasoning_kinds()
    )


def capability_objects() -> tuple[UCKO, ...]:
    """Every layer capability, in a deterministic order."""
    return (
        *projection_objects(),
        *persistence_objects(),
        *execution_objects(),
        *evolution_objects(),
        *governance_objects(),
        *reasoning_objects(),
    )


def ucko_objects() -> tuple[UCKO, ...]:
    """Provider hook (Article 8): the registry discovers these without enumeration."""
    return capability_objects()


__all__ = [
    "AUTHORISING_ARTICLES",
    "EVOLUTION_INSTRUMENT",
    "EXECUTION_INSTRUMENT",
    "GOVERNANCE_INSTRUMENT",
    "INTELLIGENCE_INSTRUMENT",
    "PERSISTENCE_INSTRUMENT",
    "PROJECTION_INSTRUMENT",
    "capability_objects",
    "evolution_objects",
    "evolution_stage_object",
    "execution_objects",
    "governance_objects",
    "governance_rule_object",
    "persistence_objects",
    "projection_objects",
    "reasoning_objects",
    "ucko_objects",
]
