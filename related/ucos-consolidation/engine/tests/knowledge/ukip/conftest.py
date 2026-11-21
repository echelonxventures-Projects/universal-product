"""Shared fixtures + factories for the UKIP Knowledge Intelligence tests.

Everything is built in memory or under ``tmp_path``; nothing touches the certified
corpus (DP-03).
"""

from __future__ import annotations

import pytest

from engine.knowledge.model import (
    KnowledgeAuthority,
    KnowledgeKind,
    Lifecycle,
    RelationType,
)
from engine.knowledge.seed import build_seed_base
from engine.knowledge.store import KnowledgeBase
from engine.knowledge.ukip.assimilation import KnowledgeAssimilator
from engine.knowledge.ukip.classification import KnowledgeClassifier
from engine.knowledge.ukip.contracts import (
    KnowledgeUnit,
    ProviderKind,
    RelationDeclaration,
    SourceRef,
)
from engine.knowledge.ukip.providers import (
    CallableProvider,
    KnowledgeProvider,
    ProviderDescriptor,
    ProviderRegistry,
    default_registry,
)
from engine.knowledge.ukip.registry import KnowledgeRegistry


def make_source(
    provider_id: str = "test-provider",
    locator: str = "test/doc.md#section",
    *,
    kind: ProviderKind = ProviderKind.DOCUMENT,
    revision: str = "rev-1",
    content_sha256: str = "a" * 64,
) -> SourceRef:
    """A well-formed, content-addressed source citation."""
    return SourceRef(
        provider_id=provider_id,
        kind=kind,
        locator=locator,
        revision=revision,
        content_sha256=content_sha256,
    )


def make_unit(key: str = "unit-1", **overrides) -> KnowledgeUnit:
    """A fully classified unit with sensible defaults; override any field."""
    fields = {
        "key": key,
        "title": f"Title {key}",
        "statement": f"Statement for {key}.",
        "rationale": f"Rationale for {key}.",
        "source": make_source(locator=f"test/{key}.md#s"),
        "kind": KnowledgeKind.FACT,
        "authority": KnowledgeAuthority.ENGINEERING,
        "lifecycle": Lifecycle.OPERATIONAL,
        "universe": "TEST",
        "owner": "TEST-OWNER",
        "version": "1.0.0",
    }
    fields.update(overrides)
    return KnowledgeUnit(**fields)


def make_unclassified(key: str = "raw-1", **overrides) -> KnowledgeUnit:
    """A unit carrying no classification, as an external provider would emit."""
    fields = {
        "key": key,
        "title": f"Raw {key}",
        "statement": f"Raw statement for {key}.",
        "source": make_source(locator=f"raw/{key}.md#s"),
    }
    fields.update(overrides)
    return KnowledgeUnit(**fields)


def make_provider(
    provider_id: str,
    units: tuple[KnowledgeUnit, ...],
    *,
    kind: ProviderKind = ProviderKind.DOCUMENT,
    priority: int = 100,
    authoritative: bool = False,
) -> KnowledgeProvider:
    """Wrap units in a provider whose descriptor matches their source provider id."""
    descriptor = ProviderDescriptor(
        provider_id=provider_id,
        kind=kind,
        title=f"Provider {provider_id}",
        priority=priority,
        authoritative=authoritative,
    )
    return CallableProvider(descriptor, lambda: units)


def unit_from(provider_id: str, key: str, statement: str, **overrides) -> KnowledgeUnit:
    """A classified unit sourced from a named provider (for corroboration tests)."""
    return make_unit(
        key,
        statement=statement,
        source=make_source(provider_id=provider_id, locator=f"{provider_id}/{key}"),
        **overrides,
    )


def register(units: tuple[KnowledgeUnit, ...], **submit_kwargs) -> KnowledgeRegistry:
    """Submit units to a fresh registry, classifying anything unclassified."""
    classifier = KnowledgeClassifier()
    registry = KnowledgeRegistry()
    for unit in units:
        classification = classifier.classify(unit)
        registry.submit(classification.apply(unit), classification, **submit_kwargs)
    return registry


@pytest.fixture
def seed_base() -> KnowledgeBase:
    """The founding canonical knowledge (never mutated by these tests)."""
    return build_seed_base()


@pytest.fixture
def seed_providers(seed_base: KnowledgeBase) -> ProviderRegistry:
    return default_registry(seed_base)


@pytest.fixture
def seed_report(seed_base: KnowledgeBase, seed_providers: ProviderRegistry):
    """A full assimilation of the seed base through the default providers."""
    return KnowledgeAssimilator().assimilate(seed_providers, decisions=seed_base.decisions())


@pytest.fixture
def simple_registry() -> KnowledgeRegistry:
    """A three-record registry with one dependency and one symmetric relation."""
    first = make_unit("a", statement="Alpha knowledge statement.")
    second = make_unit(
        "b",
        statement="Beta knowledge statement.",
        relations=(RelationDeclaration(RelationType.DEPENDS_ON, "a"),),
    )
    third = make_unit("c", statement="Gamma knowledge statement.")
    return register((first, second, third))
