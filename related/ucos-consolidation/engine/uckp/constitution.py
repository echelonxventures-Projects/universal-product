"""UCKP Layer Zero — the root law, as canonical knowledge objects (Articles 2, 8).

:mod:`engine.uckp.law` declares the law as immutable Python values. That is where the
law *is*. But Article 2 says every governed entity shall exist exactly once as a
canonical object, and a law, an article, an invariant, a stop condition, a facet and a
vocabulary are all governed categories. So the law must also exist *inside* the
universe it governs, as objects — otherwise the constitution would be the one thing in
UCOS Ω∞ standing outside its own requirements.

These objects are derived, never restated. Every field comes from
:data:`engine.uckp.law.ROOT_LAW`, :mod:`engine.uckp.facets` and
:mod:`engine.uckp.vocabulary`. Nothing here is a second copy of a clause that could
drift from the first — which is what Article 3 forbids and what makes this module a
projection of the law into object form rather than a rival declaration of it.

The module is a *provider*: it exposes :func:`ucko_objects`, so
:meth:`engine.uckp.registry.UniversalKnowledgeRegistry.discover` finds every
constitutional object by walking the package. Nothing enumerates them by hand, which
is what Article 8 requires and what UCKP-INV-16 measures.
"""

from __future__ import annotations

from collections.abc import Iterable

from engine.uckp.facets import REQUIRED_FACETS, Facet
from engine.uckp.identity import urn_for
from engine.uckp.law import ROOT_LAW, Article, Invariant, StopCondition
from engine.uckp.ucko import UCKO
from engine.uckp.values import (
    Constraint,
    PersistenceBinding,
    Policy,
    ProjectionBinding,
    Relationship,
    RuntimeBinding,
)
from engine.uckp.vocabulary import Vocabulary, build_vocabulary_registry

#: The namespace every constitutional object is minted in.
CONSTITUTION_NAMESPACE = "ucos"

#: The accountable owner of the root law and everything derived from it.
CONSTITUTIONAL_OWNER = "ucos-constitutional-authority"

#: The declaring instrument recorded in provenance (UCKP-INV-07): every object names
#: the module its content was derived from, so no field is hardcoded without a source.
LAW_INSTRUMENT = "engine.uckp.law"
FACET_INSTRUMENT = "engine.uckp.facets"
VOCABULARY_INSTRUMENT = "engine.uckp.vocabulary"


def root_law_urn() -> str:
    """The URN of the root law object (pure — no registry needed)."""
    return urn_for(CONSTITUTION_NAMESPACE, ROOT_LAW.law_id)


#: Every object binds to at least two runtimes, so no object is reachable through
#: exactly one execution technology (UCKP-INV-12). One runtime is lock-in wearing an
#: abstraction; two is the smallest number that proves the abstraction is real.
UNIVERSAL_RUNTIMES: tuple[RuntimeBinding, ...] = (
    RuntimeBinding("python", "resolve", "engine.uckp.execution.PythonExecution"),
    RuntimeBinding("ai-agent", "describe", "engine.uckp.execution.AiAgentExecution"),
    RuntimeBinding("future-language", "describe", "engine.uckp.execution.FutureLanguageExecution"),
)

#: The repository and the document appear here — as bindings, and only as bindings.
#: This is the mechanical form of Article 4: the places a copy of the object can be
#: seen, each marked ``authoritative=False`` (UCKP-INV-08, UCKP-INV-10).
UNIVERSAL_PROJECTIONS: tuple[ProjectionBinding, ...] = (
    ProjectionBinding("json", "projection/universe.json", True, False),
    ProjectionBinding("markdown", "projection/UNIVERSE.md", True, False),
    ProjectionBinding("repository", "projection/repository-manifest.json", True, False),
)

UNIVERSAL_PERSISTENCE: tuple[PersistenceBinding, ...] = (
    PersistenceBinding("git", "git://ucos/uckp", False),
    PersistenceBinding("memory", "memory://uckp", False),
)


def _mint(
    *,
    local_name: str,
    concept: str,
    definition: str,
    kind: str,
    category: str,
    derives_from: str,
    instrument: str,
    relationships: Iterable[Relationship] = (),
    dependencies: Iterable[str] = (),
    constraints: Iterable[Constraint] = (),
    policies: Iterable[Policy] = (),
    keywords: Iterable[str] = (),
    metadata: dict[str, object] | None = None,
) -> UCKO:
    """Mint one constitutional object with the universal bindings applied."""
    return UCKO.mint(
        namespace=CONSTITUTION_NAMESPACE,
        local_name=local_name,
        concept=concept,
        definition=definition,
        kind=kind,
        category=category,
        authority_tier="constitutional",
        derives_from=derives_from,
        owner=CONSTITUTIONAL_OWNER,
        lifecycle="ratified",
        instrument=instrument,
        provider="engine.uckp.constitution",
        relationships=tuple(relationships),
        dependencies=tuple(dependencies),
        constraints=tuple(constraints),
        policies=tuple(policies),
        keywords=tuple(keywords),
        metadata=metadata or {},
        runtime_bindings=UNIVERSAL_RUNTIMES,
        projection_bindings=UNIVERSAL_PROJECTIONS,
        persistence_bindings=UNIVERSAL_PERSISTENCE,
    )


def law_object() -> UCKO:
    """The root law itself — the single self-grounding object of the universe.

    Its authority derives from itself. Exactly one object in the universe may do
    this: if two did, there would be two ultimate authorities and Article 1 would be
    false; if none did, every chain would regress forever and nothing would ground.

    The definition *describes* the law rather than quoting the supremacy clause. The
    clause is Article 1's content and has its own canonical home in the Article 1
    object; restating it here would mean two objects stated the same knowledge, which
    is the duplication Article 3 forbids and which the redundancy and semantic
    reasoners both detect. The clause is still carried — as a policy and in metadata,
    which are references to it rather than second declarations of it.
    """
    urn = root_law_urn()
    return _mint(
        local_name=ROOT_LAW.law_id,
        concept="universal constitutional knowledge principle",
        definition=(
            f"the root constitutional law of UCOS Ω∞, comprising {len(ROOT_LAW.articles)} "
            f"articles, {len(ROOT_LAW.invariants)} invariants and "
            f"{len(ROOT_LAW.stop_conditions)} stop conditions, from which every "
            "architectural authority in the universe derives and outside which none exists"
        ),
        kind="law",
        category="law",
        derives_from=urn,
        instrument=LAW_INSTRUMENT,
        keywords=("constitution", "law", "supremacy", "root"),
        metadata={
            "version": ROOT_LAW.version,
            "law_digest": ROOT_LAW.digest(),
            "articles": str(len(ROOT_LAW.articles)),
            "invariants": str(len(ROOT_LAW.invariants)),
            "stop_conditions": str(len(ROOT_LAW.stop_conditions)),
            "supremacy_clause_home": urn_for(CONSTITUTION_NAMESPACE, "UCKP-ART-01"),
        },
        policies=(
            Policy(
                policy_id="UCKP-POLICY-SUPREMACY",
                statement=ROOT_LAW.supremacy,
                enforcement="fail-closed",
            ),
        ),
    )


def article_object(article: Article) -> UCKO:
    """One article of the root law, as an object derived from the law."""
    law_urn = root_law_urn()
    relationships = [Relationship("derived-from", law_urn, "authority")]
    for invariant_id in article.enforces:
        relationships.append(
            Relationship("governs", urn_for(CONSTITUTION_NAMESPACE, invariant_id), "constitutional")
        )
    return _mint(
        local_name=article.article_id,
        concept=article.title.lower(),
        definition=article.clause,
        kind="principle",
        category="principle",
        derives_from=law_urn,
        instrument=LAW_INSTRUMENT,
        relationships=relationships,
        dependencies=(law_urn,),
        keywords=("article", *article.binds),
        metadata={"binds": ",".join(article.binds), "enforces": ",".join(article.enforces)},
    )


def invariant_object(invariant: Invariant) -> UCKO:
    """One constitutional invariant, deriving from the first article that enforces it.

    Exactly one parent, even where several articles enforce the same invariant: the
    remaining articles are recorded as ``governs`` relationships instead. Authority
    is single (Article 1); relationship is plural.
    """
    enforcing = ROOT_LAW.articles_enforcing(invariant.invariant_id)
    parent_id = enforcing[0].article_id if enforcing else ROOT_LAW.law_id
    parent_urn = urn_for(CONSTITUTION_NAMESPACE, parent_id)
    relationships = [Relationship("derived-from", parent_urn, "authority")]
    for article in enforcing[1:]:
        relationships.append(
            Relationship(
                "references", urn_for(CONSTITUTION_NAMESPACE, article.article_id), "constitutional"
            )
        )
    return _mint(
        local_name=invariant.invariant_id,
        concept=invariant.name,
        definition=invariant.statement,
        kind="constraint",
        category="constraint",
        derives_from=parent_urn,
        instrument=LAW_INSTRUMENT,
        relationships=relationships,
        dependencies=(parent_urn,),
        keywords=("invariant", invariant.name),
        constraints=(
            Constraint(
                constraint_id=invariant.invariant_id,
                expression=invariant.statement,
                blocking=invariant.blocking,
            ),
        ),
        metadata={
            "blocking": "true" if invariant.blocking else "false",
            "enforced_by": ",".join(a.article_id for a in enforcing),
        },
    )


def stop_condition_object(condition: StopCondition) -> UCKO:
    """One stop condition — the measurable statement that the work is finished."""
    law_urn = root_law_urn()
    relationships = [Relationship("derived-from", law_urn, "authority")]
    for invariant_id in condition.invariants:
        relationships.append(
            Relationship("validates", urn_for(CONSTITUTION_NAMESPACE, invariant_id), "validation")
        )
    return _mint(
        local_name=condition.condition_id,
        concept=f"stop condition {condition.condition_id.removeprefix('UCKP-STOP-')}",
        definition=condition.statement,
        kind="rule",
        category="validation",
        derives_from=law_urn,
        instrument=LAW_INSTRUMENT,
        relationships=relationships,
        dependencies=(law_urn,),
        keywords=("stop-condition", "completion"),
        metadata={"invariants": ",".join(condition.invariants)},
    )


def facet_object(facet: Facet) -> UCKO:
    """One universal facet — a question every object must be able to answer."""
    parent_urn = urn_for(CONSTITUTION_NAMESPACE, "UCKP-ART-06")
    return _mint(
        local_name=f"UCKP-FACET-{facet.value}",
        concept=f"{facet.value} facet",
        definition=facet.question,
        kind="standard",
        category="metadata",
        derives_from=parent_urn,
        instrument=FACET_INSTRUMENT,
        relationships=(Relationship("derived-from", parent_urn, "authority"),),
        dependencies=(parent_urn,),
        keywords=("facet", facet.value),
        metadata={"attribute": facet.attribute, "required": "true"},
    )


def vocabulary_object(vocabulary: Vocabulary) -> UCKO:
    """One open vocabulary — the mechanism by which the universe stays extensible.

    A vocabulary is itself governed knowledge. Recording each one as an object is
    what makes Article 17 checkable: the set of admissible terms has a canonical
    home, a digest and an owner, so extending it is a registration event with
    provenance rather than an untracked edit.
    """
    parent_urn = urn_for(CONSTITUTION_NAMESPACE, "UCKP-ART-17")
    return _mint(
        local_name=vocabulary.vocabulary_id,
        concept=f"{vocabulary.vocabulary_id} vocabulary",
        definition=vocabulary.purpose,
        kind="reference",
        category="taxonomy",
        derives_from=parent_urn,
        instrument=VOCABULARY_INSTRUMENT,
        relationships=(Relationship("derived-from", parent_urn, "authority"),),
        dependencies=(parent_urn,),
        keywords=("vocabulary", "open-world", vocabulary.vocabulary_id),
        metadata={
            "terms": str(len(vocabulary.terms)),
            "vocabulary_digest": vocabulary.digest(),
            "extensible": "true",
        },
    )


def constitutional_objects() -> tuple[UCKO, ...]:
    """Every constitutional object, derived from the law in a deterministic order."""
    vocabularies = build_vocabulary_registry()
    objects: list[UCKO] = [law_object()]
    objects.extend(article_object(article) for article in ROOT_LAW.articles)
    objects.extend(invariant_object(invariant) for invariant in ROOT_LAW.invariants)
    objects.extend(stop_condition_object(condition) for condition in ROOT_LAW.stop_conditions)
    objects.extend(facet_object(facet) for facet in REQUIRED_FACETS)
    objects.extend(
        vocabulary_object(vocabularies.require(vocabulary_id))
        for vocabulary_id in vocabularies.vocabulary_ids()
    )
    return tuple(objects)


def ucko_objects() -> tuple[UCKO, ...]:
    """Provider hook (Article 8): the registry discovers these without enumeration."""
    return constitutional_objects()


__all__ = [
    "CONSTITUTIONAL_OWNER",
    "CONSTITUTION_NAMESPACE",
    "FACET_INSTRUMENT",
    "LAW_INSTRUMENT",
    "UNIVERSAL_PERSISTENCE",
    "UNIVERSAL_PROJECTIONS",
    "UNIVERSAL_RUNTIMES",
    "VOCABULARY_INSTRUMENT",
    "article_object",
    "constitutional_objects",
    "facet_object",
    "invariant_object",
    "law_object",
    "root_law_urn",
    "stop_condition_object",
    "ucko_objects",
    "vocabulary_object",
]
