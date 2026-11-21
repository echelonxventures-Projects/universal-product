"""Deliverable 6 — providers self-describe, and nothing may assume a capability.

THE PROPERTY UNDER TEST is negative and therefore easy to get wrong: the value of this layer is that
an UNDECLARED capability cannot be silently treated as present. Most of these tests assert a
refusal, because a refusal is the only observable difference between "declared" and "assumed".
"""

from __future__ import annotations

import pytest

from engine.omega_infinite import capability as capability_module
from engine.omega_infinite.capability import (
    CONTENT_HASHING,
    LOCAL_STORAGE,
    REMOTE_STORAGE,
    TRACKED_CONTENT,
    Capability,
    CapabilityError,
    CapabilityRegistry,
    CapabilitySet,
)


def test_a_capability_must_be_named() -> None:
    with pytest.raises(CapabilityError, match="no name"):
        Capability("   ")


def test_the_registry_seeds_the_well_known_vocabulary() -> None:
    registry = CapabilityRegistry()
    assert "TRACKED_CONTENT" in registry
    assert len(registry) == len(capability_module.WELL_KNOWN)


def test_redeclaring_a_capability_identically_is_idempotent() -> None:
    """Two modules declaring the same capability must not fight, so identical re-declaration is a
    no-op returning the existing entry rather than an error."""
    registry = CapabilityRegistry()
    again = registry.declare(Capability("TRACKED_CONTENT", TRACKED_CONTENT.description))
    assert again is TRACKED_CONTENT or again == TRACKED_CONTENT
    assert len(registry) == len(capability_module.WELL_KNOWN)


def test_redeclaring_a_capability_with_a_different_meaning_is_refused() -> None:
    """ONE NAME WITH TWO MEANINGS makes every requirement on that name unenforceable."""
    registry = CapabilityRegistry()
    with pytest.raises(CapabilityError, match="different meaning"):
        registry.declare(Capability("TRACKED_CONTENT", "something else entirely"))


def test_an_unknown_capability_name_raises_rather_than_being_invented() -> None:
    """THE ANTI-TYPO BOUNDARY. If resolve() minted a capability nobody declared, then
    require(resolve("CONTENT_HASHNG")) would pass vacuously forever."""
    registry = CapabilityRegistry()
    with pytest.raises(CapabilityError, match="not a declared capability"):
        registry.resolve("CONTENT_HASHNG")


def test_a_provider_may_declare_a_capability_this_package_never_named() -> None:
    """Ω∞ openness: extending the vocabulary is a registration, not an edit to capability.py."""
    registry = CapabilityRegistry()
    invented = registry.declare_name("QUANTUM_ENTANGLED_STORAGE", "Bytes exist in two places.")
    assert registry.resolve("QUANTUM_ENTANGLED_STORAGE") == invented
    assert "QUANTUM_ENTANGLED_STORAGE" not in capability_module.REGISTRY


def test_known_returns_a_sorted_deterministic_tuple() -> None:
    registry = CapabilityRegistry()
    names = [c.name for c in registry.known()]
    assert names == sorted(names)


# ------------------------------------------------------------------------------- capability sets


def test_a_set_answers_what_it_supports() -> None:
    declared = CapabilitySet.of(LOCAL_STORAGE, CONTENT_HASHING)
    assert declared.supports(LOCAL_STORAGE)
    assert declared.supports_name("CONTENT_HASHING")
    assert not declared.supports(TRACKED_CONTENT)
    assert not declared.supports_name("TRACKED_CONTENT")


def test_missing_names_every_absent_capability_sorted() -> None:
    declared = CapabilitySet.of(LOCAL_STORAGE)
    assert declared.missing(TRACKED_CONTENT, REMOTE_STORAGE) == (REMOTE_STORAGE, TRACKED_CONTENT)


def test_require_passes_when_everything_is_declared() -> None:
    CapabilitySet.of(LOCAL_STORAGE, CONTENT_HASHING).require(LOCAL_STORAGE)


def test_require_refuses_and_names_the_subject_and_the_gap() -> None:
    """THE CENTRAL DELIVERABLE 6 ASSERTION. The refusal must name the provider AND the missing
    capability. "discovery failed" was Ω-1's sentence, and it named neither."""
    declared = CapabilitySet.of(LOCAL_STORAGE)
    with pytest.raises(CapabilityError) as raised:
        declared.require(TRACKED_CONTENT, subject="provider 'filesystem'")
    message = str(raised.value)
    assert "filesystem" in message
    assert "TRACKED_CONTENT" in message
    assert "must never be assumed" in message


def test_an_empty_set_supports_nothing_and_refuses_everything() -> None:
    """An empty declaration must not read as an unrestricted one."""
    empty = CapabilitySet()
    assert len(empty) == 0
    assert not empty.supports(LOCAL_STORAGE)
    with pytest.raises(CapabilityError):
        empty.require(LOCAL_STORAGE)


def test_union_combines_declarations() -> None:
    combined = CapabilitySet.of(LOCAL_STORAGE).union(CapabilitySet.of(TRACKED_CONTENT))
    assert combined.names() == ("LOCAL_STORAGE", "TRACKED_CONTENT")


def test_iteration_and_names_are_sorted_for_determinism() -> None:
    declared = CapabilitySet.of(TRACKED_CONTENT, CONTENT_HASHING, LOCAL_STORAGE)
    assert declared.names() == ("CONTENT_HASHING", "LOCAL_STORAGE", "TRACKED_CONTENT")
    assert [c.name for c in declared] == list(declared.names())


def test_the_record_carries_the_descriptions_a_reader_needs() -> None:
    record = CapabilitySet.of(LOCAL_STORAGE).as_record()
    assert record["capabilities"] == ["LOCAL_STORAGE"]
    assert LOCAL_STORAGE.description in record["declared"]["LOCAL_STORAGE"]  # type: ignore[index]


def test_capability_renders_as_its_name() -> None:
    assert str(TRACKED_CONTENT) == "TRACKED_CONTENT"
