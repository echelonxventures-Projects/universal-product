"""Ω∞ reference layer — capability declaration, and the refusals that make it worth having.

WHAT THIS LAYER IS FOR. Resolution by capability rather than by name is only meaningful if an
UNDECLARED capability is genuinely unusable. That is a negative property, so most of these tests
assert a refusal: the refusal is the sole observable difference between a capability that was
declared and one that was merely assumed, and a suite that only exercised the happy path would pass
identically against an implementation that assumed everything.
"""

from __future__ import annotations

import pytest

from engine.omega_governance.reference import capability as capability_module
from engine.omega_governance.reference.capability import (
    APPEND_ONLY,
    ENCODABLE,
    MUTABLE,
    ORDERABLE,
    QUANTITATIVE,
    TOTALLY_ORDERABLE,
    WELL_KNOWN,
    Capability,
    CapabilityError,
    CapabilityRegistry,
    CapabilitySet,
    default_registry,
)


def test_a_capability_must_carry_a_name() -> None:
    with pytest.raises(CapabilityError):
        Capability("   ")


def test_the_registry_seeds_the_well_known_vocabulary() -> None:
    registry = default_registry()
    assert len(registry) == len(WELL_KNOWN)
    assert "ORDERABLE" in registry
    assert registry.resolve("ORDERABLE") == ORDERABLE


def test_an_unknown_capability_name_is_refused_rather_than_invented() -> None:
    """The whole layer collapses if resolving an unknown name mints one: a provider could then
    claim any property by misspelling it."""
    with pytest.raises(CapabilityError):
        default_registry().resolve("TELEPATHIC")


def test_identical_redeclaration_is_idempotent() -> None:
    registry = default_registry()
    again = registry.declare(Capability("ORDERABLE", ORDERABLE.description))
    assert again == ORDERABLE
    assert len(registry) == len(WELL_KNOWN)


def test_redeclaring_a_name_with_a_different_meaning_is_refused() -> None:
    registry = default_registry()
    with pytest.raises(CapabilityError):
        registry.declare(Capability("ORDERABLE", "something else entirely"))


def test_a_capability_can_be_declared_from_primitives_without_editing_the_module() -> None:
    """Rule 3. A deployment with a property this repository never imagined must be able to declare
    it at runtime, or the vocabulary is a closed list wearing a registry's clothes."""
    registry = CapabilityRegistry(seed=())
    declared = registry.declare_name("TAMPER_EVIDENT", "Alteration is detectable after the fact.")
    assert registry.resolve("TAMPER_EVIDENT") == declared
    assert len(registry) == 1


def test_a_set_answers_what_it_declares_and_only_that() -> None:
    declared = CapabilitySet.of(ORDERABLE, ENCODABLE)
    assert declared.supports(ORDERABLE)
    assert declared.supports_name("ENCODABLE")
    assert not declared.supports(QUANTITATIVE)
    assert declared.missing(QUANTITATIVE, TOTALLY_ORDERABLE) == (QUANTITATIVE, TOTALLY_ORDERABLE)
    assert declared.names() == ("ENCODABLE", "ORDERABLE")


def test_require_refuses_and_names_both_the_subject_and_the_missing_capability() -> None:
    """A refusal that does not say WHICH capability was missing sends the reader back to the
    source, so the message is part of the contract rather than decoration."""
    declared = CapabilitySet.of(ORDERABLE)
    with pytest.raises(CapabilityError) as refusal:
        declared.require(QUANTITATIVE, subject="the grade domain")
    assert "QUANTITATIVE" in str(refusal.value)
    assert "the grade domain" in str(refusal.value)


def test_require_passes_silently_when_everything_named_is_declared() -> None:
    CapabilitySet.of(ORDERABLE, ENCODABLE).require(ORDERABLE, ENCODABLE, subject="a provider")


def test_refuse_is_not_the_mirror_of_require_and_is_genuinely_needed() -> None:
    """An append-only register must reject a MUTABLE store. That is a refusal keyed on a
    capability being PRESENT, which ``require`` cannot express at any argument."""
    mutable_store = CapabilitySet.of(MUTABLE)
    with pytest.raises(CapabilityError):
        mutable_store.refuse(MUTABLE, subject="the governance register's storage")
    CapabilitySet.of(APPEND_ONLY).refuse(MUTABLE, subject="the governance register's storage")


def test_a_set_is_the_union_of_its_parts_and_neither_part_is_mutated() -> None:
    left = CapabilitySet.of(ORDERABLE)
    right = CapabilitySet.of(ENCODABLE)
    both = left.union(right)
    assert both.names() == ("ENCODABLE", "ORDERABLE")
    assert left.names() == ("ORDERABLE",), "union mutated its left operand"
    assert right.names() == ("ENCODABLE",), "union mutated its right operand"


def test_the_record_carries_the_descriptions_so_a_reader_need_not_have_the_source() -> None:
    record = CapabilitySet.of(ORDERABLE).as_record()
    assert record["capabilities"] == ["ORDERABLE"]
    assert record["declared"]["ORDERABLE"] == ORDERABLE.description


def test_an_empty_set_declares_nothing_and_therefore_permits_nothing() -> None:
    empty = CapabilitySet()
    assert len(empty) == 0
    assert list(empty) == []
    for capability in capability_module.WELL_KNOWN:
        assert not empty.supports(capability)


def test_the_registry_reports_the_capabilities_it_holds_in_a_stable_order() -> None:
    """The known set is what a report is rendered from, so two renderings of one registry must
    order it the same way — otherwise the document's bytes would depend on insertion order."""

    known = default_registry().known()
    assert known == tuple(sorted(known))
    assert known
