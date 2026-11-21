"""engine.ceu.context_binding — CEU units bound into UCXI-000001 (P4-F-009 remainder).

What these tests exist to falsify, stated as the failures they would catch:

* a CEU unit that cannot carry more than one bound context kind at once (the
  multi-context requirement Phase 5 was scoped against);
* a context binding whose full history cannot be reconstructed from the registry
  alone (only its current state);
* a governance binding that goes stale after a real `supersede()`/`resurrect()`
  instead of evolving with it;
* a second context registry, taxonomy or hardcoded category list smuggled in here
  instead of reusing UCXI-000001's own `ContextRegistry`/`ContextTaxonomy`.
"""

from __future__ import annotations

import pytest

from engine.ceu.context_binding import (
    bind_governance,
    bind_identity,
    governance_context_id,
    governance_history,
    governance_of,
    identity_of,
    resupersede_governance,
)
from engine.ceu.existence import ExistenceRegistry, ExistenceUnit
from engine.context.errors import DuplicateContextError
from engine.context.model import ContextDeclaration, ContextValue
from engine.context.ontology import DimensionSpec
from engine.context.registry import ContextRegistry
from engine.context.taxonomy import ContextAuthority, ContextKind, ContextTaxon


@pytest.fixture
def existence_registry() -> ExistenceRegistry:
    reg = ExistenceRegistry()
    reg.declare_form("entity", title="Entity", code="ENTY")
    return reg


@pytest.fixture
def context_registry() -> ContextRegistry:
    return ContextRegistry()


def _unit(registry: ExistenceRegistry, key: str, title: str = "") -> ExistenceUnit:
    return registry.register(ExistenceUnit(form="entity", key=key, title=title or key.title()))


# --------------------------------------------------------------------------- #
# IDENTITY binding                                                             #
# --------------------------------------------------------------------------- #


def test_bind_identity_projects_the_units_own_universal_id(existence_registry, context_registry):
    unit = _unit(existence_registry, "alpha")
    record = bind_identity(context_registry, unit)
    assert record.kind == ContextKind.IDENTITY.value
    assert identity_of(context_registry, unit) == unit.universal_id


def test_identity_of_is_none_when_never_bound(existence_registry, context_registry):
    unit = _unit(existence_registry, "unbound")
    assert identity_of(context_registry, unit) is None


def test_bind_identity_is_idempotent(existence_registry, context_registry):
    unit = _unit(existence_registry, "beta")
    first = bind_identity(context_registry, unit)
    second = bind_identity(context_registry, unit)
    assert first.context_id == second.context_id
    assert len(context_registry.by_kind(ContextKind.IDENTITY)) == 1


# --------------------------------------------------------------------------- #
# GOVERNANCE binding                                                           #
# --------------------------------------------------------------------------- #


def test_bind_governance_defaults_to_root_authority_when_unsuperseded(
    existence_registry, context_registry
):
    unit = _unit(existence_registry, "gamma")
    record = bind_governance(context_registry, existence_registry, unit)
    assert record.dimension("authority").value == "CEU-001"
    assert governance_of(context_registry, existence_registry, unit).context_id == record.context_id


def test_governance_evolves_after_a_real_supersede_call(existence_registry, context_registry):
    subject = _unit(existence_registry, "delta")
    successor = _unit(existence_registry, "delta-2")
    before = bind_governance(context_registry, existence_registry, subject)
    assert before.dimension("authority").value == "CEU-001"

    existence_registry.supersede(
        subject.universal_id, successors=[successor.universal_id], authority="OWNER-A"
    )
    after = resupersede_governance(context_registry, existence_registry, before.context_id, subject)
    assert after.dimension("authority").value == "OWNER-A"
    assert after.context_id != before.context_id

    # the predecessor is retained, not discarded (append-only)
    assert context_registry.get(before.context_id).lifecycle.value == "superseded"
    assert context_registry.get(after.context_id).lifecycle.value == "registered"


def test_governance_history_reconstructs_every_state(existence_registry, context_registry):
    subject = _unit(existence_registry, "epsilon")
    successor = _unit(existence_registry, "epsilon-2")

    gen0 = bind_governance(context_registry, existence_registry, subject)

    existence_registry.supersede(
        subject.universal_id, successors=[successor.universal_id], authority="OWNER-B"
    )
    gen1 = resupersede_governance(context_registry, existence_registry, gen0.context_id, subject)

    existence_registry.resurrect(subject.universal_id, authority="OWNER-C")
    gen2 = resupersede_governance(context_registry, existence_registry, gen1.context_id, subject)

    history = governance_history(context_registry, subject)
    assert [r.context_id for r in history] == [gen0.context_id, gen1.context_id, gen2.context_id]
    assert [r.dimension("authority").value for r in history] == ["CEU-001", "OWNER-B", "OWNER-C"]
    # the current binding is the live one — history alone would collapse to one row
    assert (
        governance_of(context_registry, existence_registry, subject).context_id == gen2.context_id
    )


def test_reregistering_an_unchanged_governance_state_is_idempotent(
    existence_registry, context_registry
):
    unit = _unit(existence_registry, "zeta")
    first = bind_governance(context_registry, existence_registry, unit)
    second = bind_governance(context_registry, existence_registry, unit)
    assert first.context_id == second.context_id


def test_governance_context_id_matches_the_bound_records_id(existence_registry, context_registry):
    unit = _unit(existence_registry, "eta")
    record = bind_governance(context_registry, existence_registry, unit)
    assert governance_context_id(existence_registry, unit) == record.context_id


# --------------------------------------------------------------------------- #
# Multi-context entity binding                                                #
# --------------------------------------------------------------------------- #


def test_one_unit_carries_two_bound_context_kinds_at_once(existence_registry, context_registry):
    unit = _unit(existence_registry, "theta")
    identity_record = bind_identity(context_registry, unit)
    governance_record = bind_governance(context_registry, existence_registry, unit)

    assert identity_record.kind != governance_record.kind
    assert identity_record.context_id != governance_record.context_id
    assert {identity_record.kind, governance_record.kind} == {
        ContextKind.IDENTITY.value,
        ContextKind.GOVERNANCE.value,
    }
    # both bindings resolve back to the same subject through their own dedicated readers
    assert identity_of(context_registry, unit) == unit.universal_id
    assert governance_of(context_registry, existence_registry, unit).context_id == (
        governance_record.context_id
    )
    # no collision in the one shared registry
    assert len(context_registry) == 2


def test_two_different_units_do_not_collide_in_the_shared_registry(
    existence_registry, context_registry
):
    one = _unit(existence_registry, "iota")
    two = _unit(existence_registry, "kappa")
    bind_identity(context_registry, one)
    bind_identity(context_registry, two)
    bind_governance(context_registry, existence_registry, one)
    bind_governance(context_registry, existence_registry, two)
    assert len(context_registry) == 4
    assert identity_of(context_registry, one) != identity_of(context_registry, two)


# --------------------------------------------------------------------------- #
# No duplicate authority, no duplicate taxonomy — this module invents nothing  #
# --------------------------------------------------------------------------- #


def test_registration_still_enforces_ontological_shape_no_bypass(
    existence_registry, context_registry
):
    """A malformed declaration (missing a required IDENTITY dimension) is refused by
    the *same* `ContextRegistry`/ontology this module reuses — proving no shortcut
    or private validation path was added alongside it."""
    from engine.context.errors import OntologyError

    bad = ContextDeclaration(
        kind=ContextKind.IDENTITY,
        namespace="existence.identity",
        natural_key="broken:unit",
        values=(
            ContextValue(
                dimension="subject",
                value="x",
                authority=ContextAuthority.OPERATIONAL,
                source="test",
            ),
        ),
    )
    with pytest.raises(OntologyError):
        context_registry.register(bad)


def test_duplicate_content_under_the_same_identity_is_a_duplicate_refusal(
    existence_registry, context_registry
):
    unit = _unit(existence_registry, "lambda")
    bind_identity(context_registry, unit)
    # a *different* IDENTITY assertion for the same natural key is refused, not silently
    # overwritten — the registry's own DuplicateContextError, unmodified by this module.
    from engine.ceu.context_binding import identity_declaration

    forged = identity_declaration(unit, note="forged")
    forged_with_diff_subject = ContextDeclaration(
        kind=forged.kind,
        namespace=forged.namespace,
        natural_key=forged.natural_key,
        values=tuple(
            v
            if v.dimension != "subject"
            else ContextValue(
                dimension="subject", value="someone-else", authority=v.authority, source=v.source
            )
            for v in forged.values
        ),
        authority=forged.authority,
        boundary=forged.boundary,
    )
    with pytest.raises(DuplicateContextError):
        context_registry.register(forged_with_diff_subject)


# --------------------------------------------------------------------------- #
# Unknown future context admission (already-proven UCXI-000001 capability)    #
# --------------------------------------------------------------------------- #


def test_unknown_future_context_kind_remains_admissible_without_a_code_change(
    context_registry,
):
    """This module adds two kinds (IDENTITY, GOVERNANCE) to two that already existed
    (KNOWLEDGE, via confidence.py); it must not have narrowed admission of a kind
    *neither* of them declared. `ContextTaxonomy.extend` is UCXI's own open-admission
    mechanism (ADR-0005/CXL-02) — re-exercised here as this phase's acceptance
    evidence for "unknown future context remains admissible," not re-invented."""
    future = ContextTaxon(
        taxon_id="CTX-QUANTUM",
        kind="quantum",
        title="Quantum Context",
        parent="CTX-ROOT",
    )
    extended_taxonomy = context_registry.taxonomy.extend(future)
    assert "quantum" in extended_taxonomy.kinds()
    assert extended_taxonomy.is_universal("quantum") is False
    # a registry built with the extended taxonomy accepts the kind neither IDENTITY
    # nor GOVERNANCE declared, using an ontology extended the same open way
    extended_ontology = context_registry.ontology.extend(
        "quantum",
        (DimensionSpec(name="superposition", value_type="string", required=True),),
    )
    future_registry = ContextRegistry(taxonomy=extended_taxonomy, ontology=extended_ontology)
    record = future_registry.register(
        ContextDeclaration(
            kind="quantum",
            namespace="future.probe",
            natural_key="probe-1",
            values=(
                ContextValue(
                    dimension="superposition",
                    value="collapsed",
                    authority=ContextAuthority.OBSERVED,
                    source="test",
                ),
            ),
        )
    )
    assert record.kind == "quantum"


def test_a_governance_binding_carries_its_note_as_a_declared_dimension(
    context_registry: ContextRegistry, existence_registry: ExistenceRegistry
) -> None:
    """A NOTE IS A DIMENSION OR IT IS NOWHERE.

    Governance is projected as declared context values, so the reason a governance decision
    was taken has to be one of them — there is no free-text field on a declaration. Every
    existing binding is made without a note, so the dimension was never emitted, and a note
    silently dropped is a governance record that says WHAT was decided and never why. It is
    conditional rather than always present because an empty note would declare a dimension
    whose value is the empty string, which is a different claim from not having said anything.
    """
    unit = existence_registry.register(ExistenceUnit(form="entity", key="noted", title="Noted"))

    silent = bind_governance(context_registry, existence_registry, unit)
    assert "note" not in {value.dimension for value in silent.values}

    noted = existence_registry.register(
        ExistenceUnit(form="entity", key="explained", title="Explained")
    )
    record = bind_governance(
        context_registry, existence_registry, noted, note="ratified by the commission"
    )

    values = {value.dimension: value.value for value in record.values}
    assert values["note"] == "ratified by the commission"
