"""EC3-B11-U06 — Universal Composition construct tests (SMC-06)."""

from __future__ import annotations

import pytest

from service.composition import (
    COMPOSITION_FOUNDATION_REUSE,
    COMPOSITION_ID_PREFIX,
    DEFAULT_COMPOSITION_REF,
    DEFAULT_INTEGRATION_REF,
    DEFAULT_INVOCATION_REF,
    Composition,
    make_composition,
)
from service.composition_meta import (
    COMPOSITION_META_CLASS,
    COMPOSITION_RELATIONSHIPS,
    CompositionKind,
)
from service.service import ServiceError
from service.service_meta import ServiceState

_MEMBERS = ("ENG-005:SOE-05:op.a", "ENG-005:SOE-05:op.b")
_CON = "ENG-005:SOE-03:contract"
_DATA = ("ENG-005:DF-2:composite",)


def _c(**kw) -> Composition:
    base = dict(
        type_tag="t",
        member_refs=_MEMBERS,
        contract_ref=_CON,
        kind=CompositionKind.AGGREGATION,
        data_refs=_DATA,
    )
    base.update(kw)
    return make_composition(
        base.pop("type_tag"),
        base.pop("member_refs"),
        base.pop("contract_ref"),
        **base,
    )


def test_make_composition_builds_a_wellformed_aggregation():
    c = _c()
    assert c.kind is CompositionKind.AGGREGATION
    assert c.state is ServiceState.DEFINED
    assert c.meta_class == COMPOSITION_META_CLASS == "SMC-06"
    assert c.composition_ref == DEFAULT_COMPOSITION_REF
    assert c.integration_ref == DEFAULT_INTEGRATION_REF
    assert c.invocation_ref == DEFAULT_INVOCATION_REF


def test_federation_and_delegation_kinds_are_constructible():
    fed = _c(kind=CompositionKind.FEDERATION, member_refs=("ENG-005:SOE-01:s1", "ENG-005:SOE-01:s2"))
    dele = _c(kind=CompositionKind.DELEGATION, member_refs=("ENG-005:SOE-05:target",))
    assert fed.topology_valid() is True
    assert dele.topology_valid() is True
    assert fed.is_founding() is False
    assert dele.is_founding() is True


def test_empty_type_tag_is_rejected():
    with pytest.raises(ServiceError, match="typed"):
        _c(type_tag="  ")


def test_non_string_type_tag_is_rejected():
    with pytest.raises(ServiceError, match="typed"):
        Composition(
            type_tag=1,  # type: ignore[arg-type]
            kind=CompositionKind.AGGREGATION,
            member_refs=_MEMBERS,
            contract_ref=_CON,
        )


def test_bad_kind_is_rejected():
    with pytest.raises(ServiceError, match="SXH-06"):
        Composition(
            type_tag="t",
            kind="nope",  # type: ignore[arg-type]
            member_refs=_MEMBERS,
            contract_ref=_CON,
        )


def test_member_refs_must_be_a_tuple():
    with pytest.raises(ServiceError, match="member_refs"):
        _c(member_refs=["ENG-005:SOE-05:x"])  # type: ignore[arg-type]


def test_member_refs_must_be_nonempty():
    with pytest.raises(ServiceError, match="member_refs"):
        _c(member_refs=())


def test_member_ref_entries_must_be_nonempty():
    with pytest.raises(ServiceError, match="member_refs"):
        _c(member_refs=("  ",))


def test_empty_contract_ref_is_rejected():
    with pytest.raises(ServiceError, match="contract_ref"):
        _c(contract_ref="  ")


def test_empty_composition_ref_is_rejected():
    with pytest.raises(ServiceError, match="composition_ref"):
        _c(composition_ref="  ")


def test_empty_integration_ref_is_rejected():
    with pytest.raises(ServiceError, match="integration_ref"):
        _c(integration_ref="  ")


def test_empty_invocation_ref_is_rejected():
    with pytest.raises(ServiceError, match="invocation_ref"):
        _c(invocation_ref="  ")


def test_data_refs_must_be_a_tuple():
    with pytest.raises(ServiceError, match="data_refs"):
        _c(data_refs="ENG-005:DF-2:x")  # type: ignore[arg-type]


def test_data_ref_entries_must_be_nonempty():
    with pytest.raises(ServiceError, match="data_refs"):
        _c(data_refs=("",))


def test_empty_data_refs_is_allowed():
    c = _c(data_refs=())
    assert c.data_by_reference() is True
    assert c.data_refs == ()


def test_bad_state_is_rejected():
    with pytest.raises(ServiceError, match="SOS-01"):
        _c(state="LIVE")  # type: ignore[arg-type]


def test_identity_is_deterministic_and_prefixed():
    a, b = _c(), _c()
    assert a.composition_id == b.composition_id
    assert a.composition_id.startswith(COMPOSITION_ID_PREFIX + "-")
    assert len(a.value_digest) == 64


def test_distinct_cores_yield_distinct_identity():
    assert _c().composition_id != _c(kind=CompositionKind.FEDERATION).composition_id


def test_self_ref_shape():
    assert _c(type_tag="x").self_ref == "ENG-005:SOE-06:x"


def test_meta_relationships_and_class():
    c = _c()
    assert c.meta_relationships() == COMPOSITION_RELATIONSHIPS
    assert set(c.meta_relationships()) <= {f"SMR-{n:02d}" for n in range(1, 14)}
    assert c.is_founding_acyclic() is True


def test_composition_obligations():
    c = _c()
    assert c.composes_members() is True
    assert c.topology_valid() is True
    assert c.contract_bound() is True
    assert c.platform_reuse() is True
    assert c.data_by_reference() is True
    assert c.invocation_by_reference() is True
    assert c.references_resolve() is True


def test_topology_aggregation_requires_at_least_one():
    assert _c(kind=CompositionKind.AGGREGATION, member_refs=("ENG-005:SOE-05:a",)).topology_valid() is True


def test_topology_federation_requires_two_peers():
    assert _c(kind=CompositionKind.FEDERATION, member_refs=("ENG-005:SOE-01:only",)).topology_valid() is False


def test_topology_delegation_requires_exactly_one():
    assert _c(kind=CompositionKind.DELEGATION, member_refs=_MEMBERS).topology_valid() is False


def test_founding_acyclic_rejects_self_composition():
    c = _c(kind=CompositionKind.AGGREGATION, member_refs=("ENG-005:SOE-06:t",))
    assert c.self_ref in c.member_refs
    assert c.is_founding_acyclic() is False


def test_founding_acyclic_rejects_duplicate_founding_members():
    c = _c(kind=CompositionKind.AGGREGATION, member_refs=("ENG-005:SOE-05:dup", "ENG-005:SOE-05:dup"))
    assert c.is_founding_acyclic() is False


def test_federation_ignores_founding_acyclicity_constraints():
    # Federation is peer (non-founding): duplicate/self refs do not make it cyclic.
    c = _c(kind=CompositionKind.FEDERATION, member_refs=("ENG-005:SOE-06:t", "ENG-005:SOE-06:t"))
    assert c.is_founding() is False
    assert c.is_founding_acyclic() is True


def test_nested_composition_by_reference_is_allowed():
    nested = _c(member_refs=("ENG-005:SOE-06:inner.composition", "ENG-005:SOE-05:op"))
    assert nested.composes_members() is True
    assert nested.is_founding_acyclic() is True


def test_non_constitutive_defaults():
    c = _c()
    assert c.confers_authority() is False
    assert c.selects_technology() is False
    assert c.embeds_secret() is False
    assert c.redefines_foundation() is False


def test_selects_technology_is_detected():
    assert _c(member_refs=("ENG-005:SOE-01:grpc.peer",)).selects_technology() is True


def test_embeds_secret_is_detected():
    assert _c(data_refs=("ENG-005:DF-2:password=x",)).embeds_secret() is True


def test_forward_transition_is_allowed():
    c = _c()
    assert c.transition(ServiceState.CONTRACTED).state is ServiceState.CONTRACTED
    assert c.state is ServiceState.DEFINED


def test_backward_transition_is_rejected():
    c = _c(state=ServiceState.EXECUTABLE)
    with pytest.raises(ServiceError, match="forward-only"):
        c.transition(ServiceState.DEFINED)


def test_non_state_transition_target_is_rejected():
    with pytest.raises(ServiceError, match="SOS-01"):
        _c().transition("X")  # type: ignore[arg-type]


def test_to_dict_is_complete():
    d = _c().to_dict()
    assert d["meta_class"] == "SMC-06"
    assert d["member_refs"] == list(_MEMBERS)
    assert d["data_refs"] == list(_DATA)
    assert d["kind"] == "Aggregation-Composition"
    assert d["founding"] is True
    assert "SMR-05" in d["relationships"]
    assert "SMR-12" in d["relationships"]
    assert "PL-F2" in d["substrate_refs"]
    assert "DF-2" in d["substrate_refs"]


def test_foundation_reuse_names_frozen_primitives():
    assert {"ENG-001", "ENG-005", "PL-F2", "RL-F2", "DF-2"} <= set(COMPOSITION_FOUNDATION_REUSE)
