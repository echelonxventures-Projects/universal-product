"""UCKP — the Universal Constitutional Knowledge Principle, implemented.

``UCKP-LAW-0001``: every constitutional entity exists exactly once as a canonical
Universal Constitutional Knowledge Object, and every repository, document, schema,
source file, API, database, graph, interface, runtime and future technology is a view of
one, an environment that acts on one, or a mechanism that stores one. No architectural
authority exists outside that principle.

The package is layered strictly bottom-up, and the order is the dependency order:

    :mod:`~engine.uckp.canonical`      the one serialization primitive (stdlib only)
    :mod:`~engine.uckp.errors`         the fail-closed error taxonomy
    :mod:`~engine.uckp.law`            the law itself: 20 articles, 17 invariants, 13 stops
    :mod:`~engine.uckp.identity`       globally unique, time- and storage-independent identity
    :mod:`~engine.uckp.facets`         the 33 questions every object must answer
    :mod:`~engine.uckp.values`         the typed facet values
    :mod:`~engine.uckp.vocabulary`     open vocabularies — extended by registration
    :mod:`~engine.uckp.ucko`           the canonical object
    :mod:`~engine.uckp.graph`          every object a node, every relationship executable
    :mod:`~engine.uckp.registry`       admission, reuse-before-create, automatic discovery
    :mod:`~engine.uckp.projection`     10 generated views, none authoritative
    :mod:`~engine.uckp.persistence`    10 interchangeable storage technologies
    :mod:`~engine.uckp.execution`      10 interchangeable execution technologies
    :mod:`~engine.uckp.state`          immutable, content-addressed constitutional states
    :mod:`~engine.uckp.evolution`      the 15-stage cycle that never terminates
    :mod:`~engine.uckp.resolution`     the constitutional resolutions, read as data
    :mod:`~engine.uckp.intelligence`   13 ways the universe reasons about itself
    :mod:`~engine.uckp.governance`     decisions that replay from themselves
    :mod:`~engine.uckp.constitution`   the law, re-entered as objects (a provider)
    :mod:`~engine.uckp.capabilities`   every layer capability as objects (a provider)
    :mod:`~engine.uckp.universe`       the assembled whole
    :mod:`~engine.uckp.validation`     the 17 invariants as executable probes
    :mod:`~engine.uckp.assimilation`   every existing UCOS artifact, losslessly
    :mod:`~engine.uckp.cli`            the command surface

Two properties are worth knowing before reading any of it.

**The law is code, not a document.** :mod:`engine.uckp.law` is the only home of the
articles and invariants. Every Markdown register, JSON declaration and certificate that
states the law is generated from those values, because Article 11 forbids a generated
representation from holding truth — and a law whose only home is a document is a law a
document edit can repeal.

**The universe is not enumerated anywhere.** :func:`engine.uckp.universe.build_universe`
contains no list of objects. It walks the package and admits whatever any module offers
through the provider hook, so a new family of constitutional objects is a new module and
never an edit to the builder. Nothing here is imported eagerly for the same reason: this
``__init__`` exposes names lazily through :pep:`562`, so importing
``engine.uckp.canonical`` — which the whole repository now depends on for its single
digest primitive — costs one stdlib-only module and does not drag in the registry, the
persistence adapters or the artifact corpus behind it.
"""

from __future__ import annotations

from typing import Any

#: The identity and version of the law this package implements.
UCKP_LAW_ID = "UCKP-LAW-0001"
UCKP_VERSION = "1.0.0"

#: Public name -> defining module. The map is the package's surface, and resolving it
#: lazily is what keeps Layer Zero cheap to depend on.
_EXPORTS: dict[str, str] = {
    # canonical primitive
    "CANONICAL_PROFILE": "engine.uckp.canonical",
    "DIGEST_ALGORITHM": "engine.uckp.canonical",
    "canonical_bytes": "engine.uckp.canonical",
    "canonical_json": "engine.uckp.canonical",
    "content_hash": "engine.uckp.canonical",
    "digests_match": "engine.uckp.canonical",
    # errors
    "AssimilationError": "engine.uckp.errors",
    "DuplicateAuthorityError": "engine.uckp.errors",
    "FacetError": "engine.uckp.errors",
    "GovernanceError": "engine.uckp.errors",
    "IdentityError": "engine.uckp.errors",
    "IntegrityError": "engine.uckp.errors",
    "LawViolation": "engine.uckp.errors",
    "UCKPError": "engine.uckp.errors",
    "UCKPValidationError": "engine.uckp.errors",
    # law
    "ROOT_LAW": "engine.uckp.law",
    "Article": "engine.uckp.law",
    "Invariant": "engine.uckp.law",
    "RootLaw": "engine.uckp.law",
    "StopCondition": "engine.uckp.law",
    # identity, facets, values
    "UniversalIdentity": "engine.uckp.identity",
    "urn_for": "engine.uckp.identity",
    "Facet": "engine.uckp.facets",
    "REQUIRED_FACETS": "engine.uckp.facets",
    "Relationship": "engine.uckp.values",
    "ReplayProof": "engine.uckp.values",
    # object, vocabulary, graph, registry
    "UCKO": "engine.uckp.ucko",
    "UniversalConstitutionalKnowledgeObject": "engine.uckp.ucko",
    "Term": "engine.uckp.vocabulary",
    "Vocabulary": "engine.uckp.vocabulary",
    "VocabularyRegistry": "engine.uckp.vocabulary",
    "build_vocabulary_registry": "engine.uckp.vocabulary",
    "UniversalKnowledgeGraph": "engine.uckp.graph",
    "UniversalKnowledgeRegistry": "engine.uckp.registry",
    # layers
    "ProjectionEngine": "engine.uckp.projection",
    "build_projection_engine": "engine.uckp.projection",
    "build_persistence_suite": "engine.uckp.persistence",
    "verify_interchangeable": "engine.uckp.persistence",
    "build_execution_suite": "engine.uckp.execution",
    "verify_execution_interchangeable": "engine.uckp.execution",
    "ConstitutionalState": "engine.uckp.state",
    "ConstitutionalTimeline": "engine.uckp.state",
    "EvolutionLedger": "engine.uckp.evolution",
    "EvolutionStage": "engine.uckp.evolution",
    "UniversalIntelligence": "engine.uckp.intelligence",
    "build_intelligence": "engine.uckp.intelligence",
    "Resolution": "engine.uckp.resolution",
    "ResolutionReader": "engine.uckp.resolution",
    "binding_reader": "engine.uckp.resolution",
    "GovernanceEngine": "engine.uckp.governance",
    # self-hosting providers
    "constitutional_objects": "engine.uckp.constitution",
    "root_law_urn": "engine.uckp.constitution",
    "capability_objects": "engine.uckp.capabilities",
    # the whole
    "ConstitutionalUniverse": "engine.uckp.universe",
    "build_universe": "engine.uckp.universe",
    "ConstitutionalValidator": "engine.uckp.validation",
    "ValidationReport": "engine.uckp.validation",
    "require_certified": "engine.uckp.validation",
    "validate_universe": "engine.uckp.validation",
    "AssimilationReport": "engine.uckp.assimilation",
    "assimilate": "engine.uckp.assimilation",
    "build_assimilated_universe": "engine.uckp.assimilation",
    "reconstruct_artifact": "engine.uckp.assimilation",
}


def __getattr__(name: str) -> Any:
    """Resolve a public name to its defining module on first use (PEP 562)."""
    module_name = _EXPORTS.get(name)
    if module_name is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    from importlib import import_module

    return getattr(import_module(module_name), name)


def __dir__() -> list[str]:
    return sorted({*_EXPORTS, "UCKP_LAW_ID", "UCKP_VERSION"})


__all__ = [*sorted(_EXPORTS), "UCKP_LAW_ID", "UCKP_VERSION"]
