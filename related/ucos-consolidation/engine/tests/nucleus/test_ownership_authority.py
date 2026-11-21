"""UCOS-NUC-001 Part 11 — ownership has exactly one authority, and it is CEU.

The convergence claim: ``Ownership(legacy) == Ownership(CEU)`` for every role, and the
legacy surface is a *projection* rather than a second authority.

The distinction between those two is not rhetorical, and one test settles it: strip the
ownership faculty from the CEU classification and the legacy property must change. An
authority would keep answering from itself; a projection follows its source. That test is
the reason this file exists.
"""

from __future__ import annotations

import pytest

from engine.ceu.catalog import bootstrap
from engine.nucleus import authority
from engine.nucleus.law import StructuralRole
from engine.nucleus.model import CapabilityDeclaration, SubjectDeclaration
from engine.nucleus.ownership import enforce
from engine.nucleus.registry import NucleusRegistry, build_seed_registry

#: What ownership resolved to before the migration, transcribed from the retired code:
#: ``may_own_capability`` was ``self is NUCLEUS``; ``may_select_nuclei`` was
#: ``self is COMPOSITION``. The convergence proof compares against these literals.
LEGACY_OWNERSHIP = {"nucleus": True, "layer": False, "composition": False}
LEGACY_SELECTION = {"nucleus": False, "layer": False, "composition": True}


# --------------------------------------------------------------------------- #
# Phase 4 — convergence: Ownership(original) == Ownership(CEU)                 #
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize("role", list(StructuralRole))
def test_ownership_converges_for_every_role(role: StructuralRole):
    assert role.may_own_capability is LEGACY_OWNERSHIP[role.value]
    assert authority.may_own_capability(role) is LEGACY_OWNERSHIP[role.value]


@pytest.mark.parametrize("role", list(StructuralRole))
def test_selection_converges_for_every_role(role: StructuralRole):
    assert role.may_select_nuclei is LEGACY_SELECTION[role.value]
    assert authority.may_select_units(role) is LEGACY_SELECTION[role.value]


def test_the_owning_set_is_discovered_not_enumerated():
    assert authority.owning_roles() == frozenset(
        {"nucleus", "micro-nucleus", "nano-nucleus", "service", "engine"}
    )
    assert authority.selecting_roles() == frozenset({"composition", "platform"})


def test_the_legacy_surface_agrees_with_the_authority_on_every_registered_role():
    for role in sorted(authority.registered_roles()):
        assert authority.may_own_capability(role) == (role in authority.owning_roles())


# --------------------------------------------------------------------------- #
# Phase 3/5 — the legacy surface is a projection, not an authority             #
# --------------------------------------------------------------------------- #


def test_withdrawing_the_faculty_in_ceu_withdraws_legacy_ownership(monkeypatch):
    """The decisive test. A projection follows its source; an authority would not."""
    nucleus = bootstrap().unit("classification", "nucleus")

    def _ungranted(faculty: str) -> frozenset[str]:
        return frozenset() if faculty == authority.FACULTY_OWN_CAPABILITY else frozenset({"x"})

    monkeypatch.setattr(authority, "roles_holding", _ungranted)
    assert StructuralRole.NUCLEUS.may_own_capability is False
    assert authority.may_own_capability("nucleus") is False
    assert nucleus.key == "nucleus"  # the classification still exists; only the grant went


def test_granting_the_faculty_in_ceu_grants_legacy_ownership(monkeypatch):
    """And in the other direction: a layer that CEU grants ownership to, owns."""
    monkeypatch.setattr(authority, "roles_holding", lambda faculty: frozenset({"layer"}))
    assert StructuralRole.LAYER.may_own_capability is True


def test_an_unregistered_role_owns_nothing():
    assert authority.may_own_capability("dragon") is False
    assert authority.holds("dragon", authority.FACULTY_OWN_CAPABILITY) is False


def test_the_law_document_reports_ceu_derived_ownership():
    from engine.nucleus import law

    rows = {r["role"]: r for r in law.to_document()["structural_roles"]}
    assert rows["nucleus"]["may_own_capability"] is True
    assert rows["layer"]["may_own_capability"] is False
    assert rows["composition"]["may_select_nuclei"] is True


# --------------------------------------------------------------------------- #
# The gate and the registry route through the one authority                    #
# --------------------------------------------------------------------------- #


def test_the_registry_still_refuses_a_layer_owner():
    fresh = NucleusRegistry()
    fresh.register_subject(SubjectDeclaration(key="payment", title="Payment", concept="payment"))
    fresh.register_subject(SubjectDeclaration(key="platform", title="Platform Layer"))
    with pytest.raises(Exception) as caught:
        fresh.register_capability(
            CapabilityDeclaration(key="invoice", title="Invoice", owner="platform")
        )
    assert "own" in str(caught.value).lower()


def test_the_gate_still_passes_over_the_seed_population():
    report = enforce(build_seed_registry())
    assert report.status == "PASS"
    assert report.blocking_failures == ()


def test_the_gate_attributes_a_refusal_to_the_right_invariant():
    """The role now selects the *finding id* only; the refusal itself came from CEU."""
    from engine.nucleus.model import CapabilityRecord

    fresh = NucleusRegistry()
    fresh.register_subject(SubjectDeclaration(key="payment", title="Payment", concept="payment"))
    layer = fresh.register_subject(SubjectDeclaration(key="platform", title="Platform Layer"))
    fresh.register_capability(
        CapabilityDeclaration(key="invoice", title="Invoice", owner="payment")
    )
    record = fresh.capability("invoice")
    fresh._capabilities["invoice"] = CapabilityRecord(  # noqa: SLF001 - forced state
        universal_id=record.universal_id,
        key=record.key,
        title=record.title,
        owner_key=layer.key,
        owner_id=layer.universal_id,
        namespace=record.namespace,
    )
    report = enforce(fresh)
    assert "NUC-INV-01" in report.blocking_failures
    detail = next(f.detail for f in report.findings if f.invariant_id == "NUC-INV-01")
    assert "ownership authority" in detail


# --------------------------------------------------------------------------- #
# Determinism, replay and evidence                                             #
# --------------------------------------------------------------------------- #


def test_the_authority_is_deterministic():
    assert authority.to_document() == authority.to_document()


def test_the_authority_document_names_its_source():
    document = authority.to_document()
    assert document["authority"] == "engine.ceu"
    assert document["authority_digest"] == bootstrap().digest()
    assert document["closed_set"] is False


def test_the_authority_replays_from_the_reconstructed_substrate():
    """Ownership survives Steering 022 reconstruction unchanged."""
    from engine.ceu.existence import ExistenceRegistry

    original = bootstrap()
    rebuilt = ExistenceRegistry.from_document(original.to_document())
    owning_original = {
        original.resolve(i).key
        for i in original.holding(authority.FACULTY_OWN_CAPABILITY, form="classification")
    }
    owning_rebuilt = {
        rebuilt.resolve(i).key
        for i in rebuilt.holding(authority.FACULTY_OWN_CAPABILITY, form="classification")
    }
    assert owning_original == owning_rebuilt == set(authority.owning_roles())


def test_certification_is_unchanged_by_the_migration():
    from engine.nucleus.certification import certify

    first = certify(build_seed_registry())
    second = certify(build_seed_registry())
    assert first.certificate_id == second.certificate_id
    assert first.certified is True


def test_the_authority_hands_out_a_fresh_substrate_each_time():
    """A SHARED MUTABLE AUTHORITY IS AN AUTHORITY A CALLER CAN GRANT ITSELF.

    Every predicate here reads the CACHED answers, so the constructor that builds the
    substrate had no direct caller — and the property it exists for is exactly that it does
    NOT cache: the CEU substrate is append-only, so handing out one shared registry would let
    a caller register a subject into the authority that decides what may own, and grant
    itself ownership without any declaration having been made.
    """
    first = authority.ownership_authority()
    second = authority.ownership_authority()

    assert first is not second
    assert {u.universal_id for u in first.units()} == {u.universal_id for u in second.units()}
