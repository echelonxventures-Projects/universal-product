"""EC3-B11-U03 — Universal Contract construct tests (SMC-03)."""

from __future__ import annotations

import pytest

from service.contract import (
    CONTRACT_FOUNDATION_REUSE,
    CONTRACT_ID_PREFIX,
    Contract,
    make_contract,
)
from service.contract_meta import (
    CONTRACT_META_CLASS,
    CONTRACT_RELATIONSHIPS,
    ContractKind,
)
from service.service import ServiceError
from service.service_meta import ServiceState

_IN = ("ENG-005:DF-2:req",)
_OUT = ("ENG-005:DF-2:resp",)


def _contract(**kw) -> Contract:
    base = dict(type_tag="t", inputs=_IN, outputs=_OUT, effects=("ENG-005:eff",), faults=("ENG-005:flt",))
    base.update(kw)
    return make_contract(**base)


def test_make_contract_builds_a_wellformed_operation_contract():
    c = _contract()
    assert c.kind is ContractKind.OPERATION
    assert c.state is ServiceState.DEFINED
    assert c.meta_class == CONTRACT_META_CLASS == "SMC-03"


@pytest.mark.parametrize("kind", list(ContractKind))
def test_all_sxh03_kinds_are_constructible(kind):
    assert _contract(kind=kind).kind is kind


def test_empty_type_tag_is_rejected():
    with pytest.raises(ServiceError, match="typed"):
        _contract(type_tag="  ")


def test_non_string_type_tag_is_rejected():
    with pytest.raises(ServiceError, match="typed"):
        Contract(type_tag=1, kind=ContractKind.OPERATION)  # type: ignore[arg-type]


def test_bad_kind_is_rejected():
    with pytest.raises(ServiceError, match="SXH-03"):
        Contract(type_tag="t", kind="nope")  # type: ignore[arg-type]


def test_inputs_must_be_a_tuple():
    with pytest.raises(ServiceError, match="inputs"):
        _contract(inputs=["ENG-005:DF-2:x"])  # type: ignore[arg-type]


def test_input_entries_must_be_nonempty_strings():
    with pytest.raises(ServiceError, match="inputs"):
        _contract(inputs=("  ",))


def test_outputs_must_be_a_tuple():
    with pytest.raises(ServiceError, match="outputs"):
        _contract(outputs="ENG-005:DF-2:x")  # type: ignore[arg-type]


def test_effects_must_be_a_tuple():
    with pytest.raises(ServiceError, match="effects"):
        _contract(effects=None)  # type: ignore[arg-type]


def test_faults_entries_must_be_valid():
    with pytest.raises(ServiceError, match="faults"):
        _contract(faults=("",))


def test_non_string_policy_ref_is_rejected():
    with pytest.raises(ServiceError, match="policy_ref"):
        _contract(policy_ref=5)  # type: ignore[arg-type]


def test_bad_state_is_rejected():
    with pytest.raises(ServiceError, match="SOS-01"):
        _contract(state="LIVE")  # type: ignore[arg-type]


def test_identity_is_deterministic_and_prefixed():
    a, b = _contract(), _contract()
    assert a.contract_id == b.contract_id
    assert a.contract_id.startswith(CONTRACT_ID_PREFIX + "-")
    assert len(a.value_digest) == 64


def test_distinct_cores_yield_distinct_identity():
    assert _contract(kind=ContractKind.SERVICE).contract_id != _contract(
        kind=ContractKind.COMPOSITION
    ).contract_id


def test_meta_relationships_and_class():
    c = _contract()
    assert c.meta_relationships() == CONTRACT_RELATIONSHIPS
    assert set(c.meta_relationships()) <= {f"SMR-{n:02d}" for n in range(1, 14)}
    assert c.is_founding_acyclic() is True


def test_contract_obligations():
    c = _contract()
    assert c.specifies_io() is True
    assert c.io_is_data() is True
    assert c.declares_effects_and_faults() is True
    assert c.policy_by_reference() is True


def test_specifies_io_is_false_when_no_io():
    assert _contract(inputs=(), outputs=()).specifies_io() is False


def test_policy_by_reference_false_on_blank_but_present():
    assert _contract(policy_ref="   ").policy_by_reference() is False


def test_non_constitutive_defaults():
    c = _contract()
    assert c.confers_authority() is False
    assert c.selects_technology() is False
    assert c.embeds_secret() is False
    assert c.redefines_foundation() is False


def test_selects_technology_is_detected():
    assert _contract(inputs=("ENG-005:DF-2:grpc.payload",)).selects_technology() is True


def test_embeds_secret_is_detected():
    assert _contract(policy_ref="ENG-005:SOE-09:password=x").embeds_secret() is True


def test_forward_transition_is_allowed():
    c = _contract()
    assert c.transition(ServiceState.CONTRACTED).state is ServiceState.CONTRACTED
    assert c.state is ServiceState.DEFINED


def test_backward_transition_is_rejected():
    c = _contract(state=ServiceState.EXECUTABLE)
    with pytest.raises(ServiceError, match="forward-only"):
        c.transition(ServiceState.DEFINED)


def test_non_state_transition_target_is_rejected():
    with pytest.raises(ServiceError, match="SOS-01"):
        _contract().transition("X")  # type: ignore[arg-type]


def test_to_dict_is_complete():
    d = _contract().to_dict()
    assert d["meta_class"] == "SMC-03"
    assert d["inputs"] == list(_IN)
    assert "SMR-02" in d["relationships"]
    assert "DF-2" in d["substrate_refs"]


def test_foundation_reuse_names_frozen_primitives():
    assert {"ENG-001", "ENG-005", "DF-2"} <= set(CONTRACT_FOUNDATION_REUSE)
