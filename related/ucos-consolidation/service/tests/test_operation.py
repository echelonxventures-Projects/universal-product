"""EC3-B11-U05 — Universal Operation construct tests (SMC-05)."""

from __future__ import annotations

import pytest

from service.operation import (
    DEFAULT_BEHAVIOR_REF,
    DEFAULT_EXECUTION_REF,
    OPERATION_FOUNDATION_REUSE,
    OPERATION_ID_PREFIX,
    Operation,
    make_operation,
)
from service.operation_meta import (
    OPERATION_META_CLASS,
    OPERATION_RELATIONSHIPS,
    EffectKind,
    OperationKind,
)
from service.service import ServiceError
from service.service_meta import ServiceState

_SVC = "ENG-005:SOE-01:svc"
_CON = "ENG-005:SOE-03:contract"
_IFACE = "ENG-005:SOE-04:iface"
_IN = ("ENG-005:DF-2:req",)
_OUT = ("ENG-005:DF-2:resp",)
_FAULTS = ("ucos.fault.bad-input",)


def _op(**kw) -> Operation:
    base = dict(
        type_tag="t",
        service_ref=_SVC,
        contract_ref=_CON,
        interface_ref=_IFACE,
        kind=OperationKind.COMMAND,
        input_refs=_IN,
        output_refs=_OUT,
        effects=(EffectKind.WRITE,),
        faults=_FAULTS,
    )
    base.update(kw)
    return make_operation(
        base.pop("type_tag"),
        base.pop("service_ref"),
        base.pop("contract_ref"),
        base.pop("interface_ref"),
        **base,
    )


def test_make_operation_builds_a_wellformed_command_operation():
    o = _op()
    assert o.kind is OperationKind.COMMAND
    assert o.state is ServiceState.DEFINED
    assert o.meta_class == OPERATION_META_CLASS == "SMC-05"
    assert o.execution_ref == DEFAULT_EXECUTION_REF
    assert o.behavior_ref == DEFAULT_BEHAVIOR_REF


def test_query_and_event_kinds_are_constructible_with_honest_effects():
    q = _op(kind=OperationKind.QUERY, effects=(EffectKind.READ,))
    e = _op(kind=OperationKind.EVENT, effects=(EffectKind.EMIT,))
    assert q.effects_honest() is True
    assert e.effects_honest() is True


def test_empty_type_tag_is_rejected():
    with pytest.raises(ServiceError, match="typed"):
        _op(type_tag="  ")


def test_non_string_type_tag_is_rejected():
    with pytest.raises(ServiceError, match="typed"):
        Operation(
            type_tag=1,  # type: ignore[arg-type]
            kind=OperationKind.COMMAND,
            service_ref=_SVC,
            contract_ref=_CON,
            interface_ref=_IFACE,
            effects=(EffectKind.WRITE,),
        )


def test_bad_kind_is_rejected():
    with pytest.raises(ServiceError, match="SXH-05"):
        Operation(
            type_tag="t",
            kind="nope",  # type: ignore[arg-type]
            service_ref=_SVC,
            contract_ref=_CON,
            interface_ref=_IFACE,
        )


def test_empty_service_ref_is_rejected():
    with pytest.raises(ServiceError, match="service_ref"):
        _op(service_ref="  ")


def test_empty_contract_ref_is_rejected():
    with pytest.raises(ServiceError, match="contract_ref"):
        _op(contract_ref="  ")


def test_empty_interface_ref_is_rejected():
    with pytest.raises(ServiceError, match="interface_ref"):
        _op(interface_ref="  ")


def test_input_refs_must_be_a_tuple():
    with pytest.raises(ServiceError, match="input_refs"):
        _op(input_refs=["ENG-005:DF-2:x"])  # type: ignore[arg-type]


def test_input_ref_entries_must_be_nonempty():
    with pytest.raises(ServiceError, match="input_refs"):
        _op(input_refs=("  ",))


def test_output_refs_must_be_a_tuple():
    with pytest.raises(ServiceError, match="output_refs"):
        _op(output_refs="ENG-005:DF-2:x")  # type: ignore[arg-type]


def test_output_ref_entries_must_be_nonempty():
    with pytest.raises(ServiceError, match="output_refs"):
        _op(output_refs=("",))


def test_effects_must_be_a_tuple():
    with pytest.raises(ServiceError, match="effects must be a tuple"):
        _op(effects=[EffectKind.WRITE])  # type: ignore[arg-type]


def test_effect_entries_must_be_effectkind():
    with pytest.raises(ServiceError, match="EffectKind"):
        _op(effects=("write",))  # type: ignore[arg-type]


def test_faults_must_be_a_tuple():
    with pytest.raises(ServiceError, match="faults must be a tuple"):
        _op(faults=["x"])  # type: ignore[arg-type]


def test_fault_entries_must_be_nonempty_strings():
    with pytest.raises(ServiceError, match="fault"):
        _op(faults=("  ",))


def test_empty_execution_ref_is_rejected():
    with pytest.raises(ServiceError, match="execution_ref"):
        _op(execution_ref="   ")


def test_empty_behavior_ref_is_rejected():
    with pytest.raises(ServiceError, match="behavior_ref"):
        _op(behavior_ref="   ")


def test_bad_state_is_rejected():
    with pytest.raises(ServiceError, match="SOS-01"):
        _op(state="LIVE")  # type: ignore[arg-type]


def test_identity_is_deterministic_and_prefixed():
    a, b = _op(), _op()
    assert a.operation_id == b.operation_id
    assert a.operation_id.startswith(OPERATION_ID_PREFIX + "-")
    assert len(a.value_digest) == 64


def test_distinct_cores_yield_distinct_identity():
    assert _op(effects=(EffectKind.WRITE,)).operation_id != _op(
        kind=OperationKind.QUERY, effects=(EffectKind.READ,)
    ).operation_id


def test_meta_relationships_and_class():
    o = _op()
    assert o.meta_relationships() == OPERATION_RELATIONSHIPS
    assert set(o.meta_relationships()) <= {f"SMR-{n:02d}" for n in range(1, 14)}
    assert o.is_founding_acyclic() is True


def test_operation_obligations():
    o = _op()
    assert o.provided_by_service() is True
    assert o.contract_bound() is True
    assert o.interface_addressed() is True
    assert o.signature_bounded() is True
    assert o.effects_honest() is True
    assert o.io_is_data() is True
    assert o.execution_by_reference() is True
    assert o.behavior_by_reference() is True
    assert o.references_resolve() is True


def test_signature_bounded_is_false_without_effects():
    assert _op(effects=()).signature_bounded() is False


def test_signature_bounded_true_with_empty_io_when_effects_declared():
    o = _op(input_refs=(), output_refs=(), effects=(EffectKind.WRITE,))
    assert o.signature_bounded() is True
    assert o.io_is_data() is True


def test_effect_honesty_query_rejects_write():
    assert _op(kind=OperationKind.QUERY, effects=(EffectKind.WRITE,)).effects_honest() is False


def test_effect_honesty_command_requires_write():
    assert _op(kind=OperationKind.COMMAND, effects=(EffectKind.READ,)).effects_honest() is False


def test_effect_honesty_event_requires_emit_or_consume():
    assert _op(kind=OperationKind.EVENT, effects=(EffectKind.READ,)).effects_honest() is False
    assert _op(kind=OperationKind.EVENT, effects=(EffectKind.CONSUME,)).effects_honest() is True


def test_non_constitutive_defaults():
    o = _op()
    assert o.confers_authority() is False
    assert o.selects_technology() is False
    assert o.embeds_secret() is False
    assert o.redefines_foundation() is False


def test_selects_technology_is_detected():
    assert _op(input_refs=("ENG-005:DF-2:grpc.request",)).selects_technology() is True


def test_embeds_secret_is_detected():
    assert _op(faults=("ucos.fault.password=x",)).embeds_secret() is True


def test_forward_transition_is_allowed():
    o = _op()
    assert o.transition(ServiceState.CONTRACTED).state is ServiceState.CONTRACTED
    assert o.state is ServiceState.DEFINED


def test_backward_transition_is_rejected():
    o = _op(state=ServiceState.EXECUTABLE)
    with pytest.raises(ServiceError, match="forward-only"):
        o.transition(ServiceState.DEFINED)


def test_non_state_transition_target_is_rejected():
    with pytest.raises(ServiceError, match="SOS-01"):
        _op().transition("X")  # type: ignore[arg-type]


def test_to_dict_is_complete():
    d = _op().to_dict()
    assert d["meta_class"] == "SMC-05"
    assert d["input_refs"] == list(_IN)
    assert d["output_refs"] == list(_OUT)
    assert d["effects"] == ["write"]
    assert d["faults"] == list(_FAULTS)
    assert "SMR-02" in d["relationships"]
    assert "SMR-04" in d["relationships"]
    assert "RL-F2" in d["substrate_refs"]
    assert "DF-2" in d["substrate_refs"]


def test_foundation_reuse_names_frozen_primitives():
    assert {"ENG-001", "ENG-005", "RL-F2", "DF-2"} <= set(OPERATION_FOUNDATION_REUSE)
