"""Deliverable 5 — a repository root is one KIND of knowledge space, and no longer the only one.

THE ASSUMPTION UNDER TEST is a function signature: ``root: str = "."`` carried three unstated
commitments (a filesystem path, a repository, the whole world). These tests check that each of the
three is now stated, interrogable and independently variable.

``test_a_space_of_a_kind_this_package_does_not_implement_needs_no_edit`` is the one that matters for
the "unlimited expansion" criterion.
"""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

import pytest

from engine.omega_infinite import knowledge_space as space_module
from engine.omega_infinite.artifact import Artifact, Location
from engine.omega_infinite.capability import (
    LOCAL_STORAGE,
    REMOTE_STORAGE,
    TRACKED_CONTENT,
    CapabilityError,
    CapabilitySet,
)
from engine.omega_infinite.knowledge_space import (
    FILESYSTEM,
    KINDS,
    REPOSITORY,
    FilesystemKnowledgeSpace,
    KnowledgeSpace,
    KnowledgeSpaceError,
    RepositoryKnowledgeSpace,
    SpaceKind,
    filesystem_space,
    repository_space,
    resolve_space,
    space_of,
    strongest_provider,
)
from engine.omega_infinite.provider import ProviderMetadata, ProviderRegistry, Selector

PYTHON_ONLY = Selector(patterns=("*.py",))


class Fake:
    """A provider for a storage model this package does not implement."""

    priority = 5

    def __init__(
        self, name: str, capabilities: CapabilitySet, locators: Iterable[str] = ()
    ) -> None:
        self._name = name
        self._capabilities = capabilities
        self._locators = tuple(locators)

    def identifier(self) -> str:
        return self._name

    def capabilities(self) -> CapabilitySet:
        return self._capabilities

    def metadata(self) -> ProviderMetadata:
        return ProviderMetadata(self._name, f"{self._name}://", "synthetic")

    def enumerate(self, selector: Selector | None = None) -> tuple[Artifact, ...]:
        del selector
        return tuple(
            Artifact(f"{self._name}:{loc}", Location(self._name, loc)) for loc in self._locators
        )


# ----------------------------------------------------------------------------- resolution


def test_a_repository_root_resolves_to_a_repository_space(tracked_tree: Path) -> None:
    """What ``root: str`` used to mean, now said explicitly and checkably."""
    space = resolve_space(str(tracked_tree))
    assert space.kind() is REPOSITORY
    assert isinstance(space, RepositoryKnowledgeSpace)
    assert space.registry().identifiers() == ("git",)


def test_a_directory_that_never_was_a_repository_still_resolves(untracked_tree: Path) -> None:
    """THE DELIVERABLE 5 SUCCESS CRITERION reached through Deliverable 2: a root is not required to
    be a repository for UCOS to have a knowledge space over it."""
    space = resolve_space(str(untracked_tree))
    assert space.kind() is FILESYSTEM
    assert isinstance(space, FilesystemKnowledgeSpace)
    assert space.registry().identifiers() == ("filesystem",)
    assert len(space.discover(PYTHON_ONLY)) == 2


def test_resolution_prefers_the_stronger_guarantee(tracked_tree: Path) -> None:
    """Probes rather than assumes, and the ORDER is by strength of guarantee."""
    space = resolve_space(str(tracked_tree))
    assert space.registry().resolve_capable(TRACKED_CONTENT).provider.identifier() == "git"


def test_a_non_repository_cannot_be_declared_a_repository_space(untracked_tree: Path) -> None:
    with pytest.raises(KnowledgeSpaceError, match="not served by a version control provider"):
        repository_space(str(untracked_tree))


def test_unreadable_storage_is_no_knowledge_space(tmp_path: Path) -> None:
    with pytest.raises(KnowledgeSpaceError, match="not readable storage"):
        filesystem_space(str(tmp_path / "absent"))


def test_a_space_needs_an_identifier_and_at_least_one_provider() -> None:
    """An empty registry would report an empty population as a clean one."""
    with pytest.raises(KnowledgeSpaceError, match="non-empty identifier"):
        space_module.BaseKnowledgeSpace("  ", ProviderRegistry((Fake("f", CapabilitySet()),)))
    with pytest.raises(KnowledgeSpaceError, match="no registered provider"):
        space_module.BaseKnowledgeSpace("empty", ProviderRegistry())


# ------------------------------------------------------------------- the eligibility assertion


def test_a_repository_space_refuses_a_provider_without_the_eligibility_boundary() -> None:
    """The boundary expressed as a CAPABILITY rather than as an unstated consequence of calling
    ``git ls-files``. Refused at construction, not silently at verdict time."""
    untracked = ProviderRegistry((Fake("loose", CapabilitySet.of(LOCAL_STORAGE)),))
    with pytest.raises(CapabilityError, match="TRACKED_CONTENT"):
        RepositoryKnowledgeSpace("pretend", untracked)


def test_a_filesystem_space_declares_no_guarantee_it_lacks(untracked_tree: Path) -> None:
    space = filesystem_space(str(untracked_tree))
    assert not space.guarantees().supports(TRACKED_CONTENT)
    with pytest.raises(CapabilityError, match="knowledge space"):
        space.require(TRACKED_CONTENT)


# -------------------------------------------------------------- union versus intersection


def test_union_is_what_the_space_can_do_and_intersection_is_what_holds_for_everything() -> None:
    """THE FEDERATION-CRITICAL DISTINCTION. A space unioning a tracked and an untracked provider
    offers LOCAL_STORAGE for everything but TRACKED_CONTENT for only part of the population."""
    space = space_of(
        "mixed",
        space_module.FEDERATION,
        (
            Fake("tracked", CapabilitySet.of(TRACKED_CONTENT, LOCAL_STORAGE), ("a.py",)),
            Fake("loose", CapabilitySet.of(LOCAL_STORAGE), ("b.py",)),
        ),
    )
    assert space.capabilities().names() == ("LOCAL_STORAGE", "TRACKED_CONTENT")
    assert space.guarantees().names() == ("LOCAL_STORAGE",)
    space.require(LOCAL_STORAGE)
    with pytest.raises(CapabilityError):
        space.require(TRACKED_CONTENT)


# ------------------------------------------------------------------------------ discovery


def test_discovery_carries_the_provenance_needed_to_compare_populations(
    tracked_tree: Path,
) -> None:
    """The repository already computed four populations that no code compared, and 619 artifacts sat
    in exactly one of them. A population must carry the space, the providers and the selector."""
    population = resolve_space(str(tracked_tree), identifier="<root>").discover(PYTHON_ONLY)
    assert population.space == "<root>"
    assert population.kind is REPOSITORY
    assert population.providers == ("git",)
    assert population.selector == PYTHON_ONLY
    assert population.capabilities.supports(TRACKED_CONTENT)
    assert population.locators() == ("src/module.py", "src/nested/deep.py")
    assert len(population) == 2


def test_a_space_merges_and_deduplicates_across_providers() -> None:
    """THE FEDERATION SEAM, already open: ``discover`` merges and deduplicates on identifier, so
    FEDERATION needs a registration rather than a redesign."""
    space = space_of(
        "federated",
        space_module.FEDERATION,
        (
            Fake("one", CapabilitySet.of(LOCAL_STORAGE), ("a.py", "shared.py")),
            Fake("two", CapabilitySet.of(LOCAL_STORAGE), ("b.py",)),
        ),
    )
    population = space.discover()
    assert population.providers == ("one", "two")
    assert population.identifiers() == ("one:a.py", "one:shared.py", "two:b.py")


def test_a_population_counts_by_type_for_reporting(untracked_tree: Path) -> None:
    from engine.omega_infinite.classification import default_pipeline

    space = filesystem_space(str(untracked_tree))
    population = space.discover()
    typed = default_pipeline().apply_all(population.artifacts)
    counted = space_module.SpacePopulation(
        space=population.space,
        kind=population.kind,
        artifacts=typed,
        providers=population.providers,
        selector=population.selector,
    ).by_type()
    assert counted["PYTHON"] == 2
    assert counted["DOCUMENT"] >= 1
    assert list(counted) == sorted(counted)


def test_the_population_record_is_reportable(untracked_tree: Path) -> None:
    record = filesystem_space(str(untracked_tree), identifier="<root>").discover().as_record()
    assert record["space"] == "<root>"
    assert record["kind"] == "FILESYSTEM"
    assert record["providers"] == ["filesystem"]


# ---------------------------------------------------------------------------- unlimited expansion


def test_a_space_of_a_kind_this_package_does_not_implement_needs_no_edit() -> None:
    """THE UNLIMITED-EXPANSION CRITERION. A bucket space is a registration: no subclass, no new
    branch, no edit to knowledge_space.py. If supporting object storage required changing that
    file, the abstraction would have moved the limit rather than removed it."""
    kind = SpaceKind("BUCKET_V2", "Object storage with a versioned key space.")
    provider = Fake("s3", CapabilitySet.of(REMOTE_STORAGE), ("evidence/report.json",))

    space = space_of("s3://ucos-evidence", kind, (provider,))

    assert kind not in KINDS
    assert space.kind() is kind
    assert space.kind().name == "BUCKET_V2"
    assert space.discover().identifiers() == ("s3:evidence/report.json",)
    assert space.guarantees().supports(REMOTE_STORAGE)
    assert isinstance(space, KnowledgeSpace)


def test_the_six_named_kinds_exist_but_nothing_quantifies_over_them() -> None:
    """A space kind absent from KINDS works identically, which is what makes the list safe to be
    incomplete — and it permanently is."""
    assert {k.name for k in KINDS} == {
        "BUCKET",
        "FEDERATION",
        "FILESYSTEM",
        "GRAPH",
        "REGISTRY",
        "REPOSITORY",
    }
    assert str(REPOSITORY) == "REPOSITORY"


def test_a_space_with_no_provider_is_refused_by_the_builder() -> None:
    with pytest.raises(KnowledgeSpaceError, match="no provider"):
        space_of("empty", space_module.GRAPH, ())


def test_a_space_describes_itself_including_both_capability_views(untracked_tree: Path) -> None:
    described = filesystem_space(str(untracked_tree), identifier="<root>").describe()
    assert described["kind"] == "FILESYSTEM"
    assert described["capabilities_union"] == ["CONTENT_HASHING", "LOCAL_STORAGE"]
    assert described["capabilities_guaranteed"] == ["CONTENT_HASHING", "LOCAL_STORAGE"]
    assert described["capability_matrix"] == {"filesystem": ["CONTENT_HASHING", "LOCAL_STORAGE"]}
    assert described["kind_description"]


# ------------------------------------------------------------------------- resolution helper


def test_the_strongest_provider_is_resolved_by_capability(tracked_tree: Path) -> None:
    space = resolve_space(str(tracked_tree))
    assert strongest_provider(space, TRACKED_CONTENT).identifier() == "git"


def test_asking_for_a_capability_no_provider_has_is_a_named_refusal(untracked_tree: Path) -> None:
    space = filesystem_space(str(untracked_tree), identifier="<root>")
    with pytest.raises(KnowledgeSpaceError, match="no provider for the required"):
        strongest_provider(space, REMOTE_STORAGE)
