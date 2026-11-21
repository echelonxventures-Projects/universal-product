"""Deliverable 1 — the provider contract, the registry, and resolution BY CAPABILITY.

THE DESIGN CLAIM UNDER TEST: no measurement needs to name a provider. ``resolve_capable`` is the
call a measurement makes, and ``resolve`` by name exists only for evidence and tests. If a
measurement had to say "git", the assumption would simply have moved one layer up.
"""

from __future__ import annotations

from collections.abc import Iterable

import pytest

from engine.omega_infinite.artifact import Artifact, Location
from engine.omega_infinite.capability import (
    CONTENT_HASHING,
    LOCAL_STORAGE,
    REMOTE_STORAGE,
    TRACKED_CONTENT,
    CapabilityError,
    CapabilitySet,
)
from engine.omega_infinite.provider import (
    BaseProvider,
    DiscoveryProvider,
    ProviderError,
    ProviderMetadata,
    ProviderRegistry,
    Selector,
)

#: A module-level empty declaration, so the ``Fake`` default is not a call in an argument default
#: (ruff B008). A provider that declares nothing is a legitimate and useful test subject: it is the
#: shape that must be refused by every ``require``.
NO_CAPABILITIES = CapabilitySet()


class Fake(BaseProvider):
    """A provider over an in-memory list. Exercises the contract with no storage at all."""

    def __init__(
        self,
        name: str,
        locators: Iterable[str] = (),
        capabilities: CapabilitySet = NO_CAPABILITIES,
        priority: int = 0,
    ) -> None:
        self._name = name
        self._locators = tuple(locators)
        self._capabilities = capabilities
        self.priority = priority

    def identifier(self) -> str:
        return self._name

    def capabilities(self) -> CapabilitySet:
        return self._capabilities

    def metadata(self) -> ProviderMetadata:
        return ProviderMetadata(self._name, "memory://", "in-memory list")

    def collect(self, selector: Selector) -> Iterable[Artifact]:
        del selector
        for locator in self._locators:
            yield Artifact(f"{self._name}:{locator}", Location(self._name, locator))


# --------------------------------------------------------------------------------- the selector


def test_an_empty_selector_means_everything() -> None:
    """Ω-1 hard-codes '*.py'. The honest default here is no filter at all."""
    assert Selector().matches("anything/at/all.bin")


def test_a_selector_narrows_by_locator_pattern() -> None:
    selector = Selector(patterns=("*.py",))
    assert selector.matches("engine/deep/nested/module.py")
    assert not selector.matches("docs/guide.md")


def test_a_selector_may_bound_the_population() -> None:
    provider = Fake("fake", ("a.py", "b.py", "c.py"))
    assert len(provider.enumerate(Selector(limit=2))) == 2


def test_selector_patterns_are_string_operations_not_filesystem_ones() -> None:
    """The same selector must work against object keys and graph node names."""
    assert Selector(patterns=("evidence/*",)).matches("evidence/report.json")
    assert Selector(patterns=("*report*",)).matches("s3://bucket/report.json")


def test_the_selector_record_is_reportable() -> None:
    assert Selector(patterns=("*.py",), limit=3).as_record() == {"patterns": ["*.py"], "limit": 3}


# ------------------------------------------------------------------------------- the base provider


def test_enumeration_is_sorted_and_deduplicated_for_every_provider_uniformly() -> None:
    """``git ls-files`` returns sorted output and ``os.walk`` does not. A population whose ORDER
    depends on the provider would make two evidence documents differ for no governed reason."""
    provider = Fake("fake", ("c.py", "a.py", "b.py", "a.py"))
    assert [a.location.locator for a in provider.enumerate()] == ["a.py", "b.py", "c.py"]


def test_a_provider_refuses_an_operation_it_never_claimed_to_support() -> None:
    provider = Fake("fake", capabilities=CapabilitySet.of(LOCAL_STORAGE))
    provider.require(LOCAL_STORAGE)
    with pytest.raises(CapabilityError, match="fake"):
        provider.require(TRACKED_CONTENT)


def test_a_provider_self_describes_for_the_evidence_document() -> None:
    report = Fake("fake", capabilities=CapabilitySet.of(LOCAL_STORAGE), priority=7).report()
    assert report["identifier"] == "fake"
    assert report["priority"] == 7
    assert report["capabilities"] == ["LOCAL_STORAGE"]


def test_the_concrete_providers_satisfy_the_protocol_structurally() -> None:
    assert isinstance(Fake("fake"), DiscoveryProvider)


# ------------------------------------------------------------------------------------- registry


def test_a_duplicate_identifier_is_refused_rather_than_replacing_silently() -> None:
    """Silent replacement would make the population depend on IMPORT ORDER, which is the class of
    defect that cannot be reproduced from a diff."""
    registry = ProviderRegistry((Fake("git"),))
    with pytest.raises(ProviderError, match="already registered"):
        registry.register(Fake("git"))


def test_a_provider_must_declare_an_identifier_to_be_registered() -> None:
    with pytest.raises(ProviderError, match="non-empty identifier"):
        ProviderRegistry((Fake("  "),))


def test_resolution_by_name_names_what_is_registered_when_it_fails() -> None:
    registry = ProviderRegistry((Fake("git"), Fake("filesystem")))
    assert registry.resolve("git").identifier() == "git"
    with pytest.raises(ProviderError, match="filesystem, git"):
        registry.resolve("bucket")


def test_providers_are_ordered_by_priority_then_identifier() -> None:
    """A total, reproducible order — priority first so a stronger provider wins, identifier second
    so ties do not depend on registration order."""
    registry = ProviderRegistry(
        (Fake("zulu", priority=10), Fake("alpha", priority=10), Fake("weak", priority=1))
    )
    assert [p.identifier() for p in registry.providers()] == ["alpha", "zulu", "weak"]


def test_resolution_by_capability_prefers_the_strongest_provider() -> None:
    """THE CALL A MEASUREMENT MAKES. No call site names a provider."""
    tracked = Fake("git", (), CapabilitySet.of(TRACKED_CONTENT, LOCAL_STORAGE), 100)
    plain = Fake("filesystem", (), CapabilitySet.of(LOCAL_STORAGE), 10)
    registry = ProviderRegistry((plain, tracked))

    resolved = registry.resolve_capable(LOCAL_STORAGE)
    assert resolved.provider.identifier() == "git"
    assert resolved.as_record()["required"] == ["LOCAL_STORAGE"]


def test_capability_resolution_skips_providers_that_cannot_serve_and_records_why() -> None:
    """'No provider supports REMOTE_STORAGE' is a far less useful sentence than naming what each
    provider considered was missing."""
    tracked = Fake("git", capabilities=CapabilitySet.of(TRACKED_CONTENT), priority=100)
    remote = Fake("bucket", capabilities=CapabilitySet.of(REMOTE_STORAGE), priority=5)
    registry = ProviderRegistry((tracked, remote))

    resolved = registry.resolve_capable(REMOTE_STORAGE)
    assert resolved.provider.identifier() == "bucket"
    assert resolved.rejected == (("git", ("REMOTE_STORAGE",)),)


def test_resolution_raises_when_nothing_satisfies_and_names_every_gap() -> None:
    registry = ProviderRegistry((Fake("filesystem", capabilities=CapabilitySet.of(LOCAL_STORAGE)),))
    with pytest.raises(ProviderError) as raised:
        registry.resolve_capable(TRACKED_CONTENT, CONTENT_HASHING)
    message = str(raised.value)
    assert "filesystem" in message
    assert "TRACKED_CONTENT" in message


def test_resolution_over_an_empty_registry_refuses_rather_than_returning_nothing() -> None:
    """A resolution returning None would let a caller measure an empty population and pass."""
    with pytest.raises(ProviderError, match="no providers registered"):
        ProviderRegistry().resolve_capable(LOCAL_STORAGE)


def test_supporting_lists_every_provider_that_can_serve() -> None:
    tracked = Fake("git", (), CapabilitySet.of(TRACKED_CONTENT, LOCAL_STORAGE), 100)
    plain = Fake("filesystem", (), CapabilitySet.of(LOCAL_STORAGE), 10)
    registry = ProviderRegistry((tracked, plain))
    assert [p.identifier() for p in registry.supporting(LOCAL_STORAGE)] == ["git", "filesystem"]
    assert [p.identifier() for p in registry.supporting(TRACKED_CONTENT)] == ["git"]
    assert registry.supporting(REMOTE_STORAGE) == ()


def test_the_capability_matrix_is_the_deliverable_1_report() -> None:
    registry = ProviderRegistry(
        (
            Fake("git", capabilities=CapabilitySet.of(TRACKED_CONTENT), priority=100),
            Fake("filesystem", capabilities=CapabilitySet.of(LOCAL_STORAGE), priority=10),
        )
    )
    assert registry.capability_matrix() == {
        "git": ["TRACKED_CONTENT"],
        "filesystem": ["LOCAL_STORAGE"],
    }


def test_the_registry_reports_providers_and_the_matrix_together() -> None:
    registry = ProviderRegistry((Fake("git", (), CapabilitySet.of(TRACKED_CONTENT)),))
    report = registry.report()
    assert report["capability_matrix"] == {"git": ["TRACKED_CONTENT"]}
    assert report["providers"][0]["identifier"] == "git"  # type: ignore[index]


def test_membership_and_length_are_answerable() -> None:
    registry = ProviderRegistry((Fake("git"),))
    assert "git" in registry
    assert 42 not in registry
    assert len(registry) == 1
    assert registry.identifiers() == ("git",)


def test_a_protocol_only_provider_appears_in_evidence_without_inheriting_baseprovider() -> None:
    """The test of whether ``BaseProvider`` is genuinely optional. A third-party provider must need
    no dependency on this package's classes to be registered and reported."""

    class Minimal:
        def identifier(self) -> str:
            return "minimal"

        def enumerate(self, selector: Selector | None = None) -> tuple[Artifact, ...]:
            del selector
            return ()

        def metadata(self) -> ProviderMetadata:
            return ProviderMetadata("minimal", "nowhere://", "none")

        def capabilities(self) -> CapabilitySet:
            return CapabilitySet.of(REMOTE_STORAGE)

    registry = ProviderRegistry((Minimal(),))
    report = registry.report()
    assert report["capability_matrix"] == {"minimal": ["REMOTE_STORAGE"]}
    assert report["providers"][0]["priority"] == 0  # type: ignore[index]
    assert registry.resolve_capable(REMOTE_STORAGE).provider.identifier() == "minimal"
