"""EC3-B11-U04 — Universal Interface construct tests (SMC-04)."""

from __future__ import annotations

import pytest

from service.interface import (
    DEFAULT_INTERACTION_REF,
    INTERFACE_FOUNDATION_REUSE,
    INTERFACE_ID_PREFIX,
    Interface,
    make_interface,
)
from service.interface_meta import (
    INTERFACE_META_CLASS,
    INTERFACE_RELATIONSHIPS,
    InterfaceKind,
)
from service.service import ServiceError
from service.service_meta import ServiceState

_SVC = "ENG-005:SOE-01:svc"
_OPS = ("ENG-005:SOE-05:op",)
_IO = ("ENG-005:DF-2:req", "ENG-005:DF-2:resp")


def _iface(**kw) -> Interface:
    base = dict(
        type_tag="t",
        service_ref=_SVC,
        operations=_OPS,
        io_refs=_IO,
        endpoint_ref="ENG-005:locus:abstract",
    )
    base.update(kw)
    return make_interface(**base)


def test_make_interface_builds_a_wellformed_request_response_interface():
    i = _iface()
    assert i.kind is InterfaceKind.REQUEST_RESPONSE
    assert i.state is ServiceState.DEFINED
    assert i.meta_class == INTERFACE_META_CLASS == "SMC-04"
    assert i.behavior_ref == DEFAULT_INTERACTION_REF


@pytest.mark.parametrize("kind", list(InterfaceKind))
def test_all_sxh04_kinds_are_constructible(kind):
    assert _iface(kind=kind).kind is kind


def test_empty_type_tag_is_rejected():
    with pytest.raises(ServiceError, match="typed"):
        _iface(type_tag="  ")


def test_non_string_type_tag_is_rejected():
    with pytest.raises(ServiceError, match="typed"):
        Interface(type_tag=1, kind=InterfaceKind.EVENT, service_ref=_SVC)  # type: ignore[arg-type]


def test_bad_kind_is_rejected():
    with pytest.raises(ServiceError, match="SXH-04"):
        Interface(type_tag="t", kind="nope", service_ref=_SVC)  # type: ignore[arg-type]


def test_empty_service_ref_is_rejected():
    with pytest.raises(ServiceError, match="service_ref"):
        _iface(service_ref="  ")


def test_operations_must_be_a_tuple():
    with pytest.raises(ServiceError, match="operations"):
        _iface(operations=["ENG-005:SOE-05:op"])  # type: ignore[arg-type]


def test_operation_entries_must_be_nonempty_strings():
    with pytest.raises(ServiceError, match="operations"):
        _iface(operations=("  ",))


def test_io_refs_must_be_a_tuple():
    with pytest.raises(ServiceError, match="io_refs"):
        _iface(io_refs="ENG-005:DF-2:x")  # type: ignore[arg-type]


def test_io_ref_entries_must_be_valid():
    with pytest.raises(ServiceError, match="io_refs"):
        _iface(io_refs=("",))


def test_non_string_endpoint_ref_is_rejected():
    with pytest.raises(ServiceError, match="endpoint_ref"):
        _iface(endpoint_ref=5)  # type: ignore[arg-type]


def test_empty_behavior_ref_is_rejected():
    with pytest.raises(ServiceError, match="behavior_ref"):
        _iface(behavior_ref="   ")


def test_bad_state_is_rejected():
    with pytest.raises(ServiceError, match="SOS-01"):
        _iface(state="LIVE")  # type: ignore[arg-type]


def test_identity_is_deterministic_and_prefixed():
    a, b = _iface(), _iface()
    assert a.interface_id == b.interface_id
    assert a.interface_id.startswith(INTERFACE_ID_PREFIX + "-")
    assert len(a.value_digest) == 64


def test_distinct_cores_yield_distinct_identity():
    assert _iface(kind=InterfaceKind.EVENT).interface_id != _iface(
        kind=InterfaceKind.STREAM
    ).interface_id


def test_meta_relationships_and_class():
    i = _iface()
    assert i.meta_relationships() == INTERFACE_RELATIONSHIPS
    assert set(i.meta_relationships()) <= {f"SMR-{n:02d}" for n in range(1, 14)}
    assert i.is_founding_acyclic() is True


def test_interface_obligations():
    i = _iface()
    assert i.exposed_by_service() is True
    assert i.is_sole_surface() is True
    assert i.io_is_data() is True
    assert i.endpoint_is_abstract() is True
    assert i.behavior_by_reference() is True
    assert i.references_resolve() is True


def test_is_sole_surface_is_false_when_no_operations():
    assert _iface(operations=()).is_sole_surface() is False


def test_endpoint_is_abstract_true_when_empty():
    assert _iface(endpoint_ref="").endpoint_is_abstract() is True


def test_non_constitutive_defaults():
    i = _iface()
    assert i.confers_authority() is False
    assert i.selects_technology() is False
    assert i.embeds_secret() is False
    assert i.redefines_foundation() is False


def test_selects_technology_is_detected():
    assert _iface(operations=("ENG-005:SOE-05:grpc.call",)).selects_technology() is True


def test_selects_technology_detects_endpoint_url():
    assert _iface(endpoint_ref="https://api.example.com").selects_technology() is True


def test_embeds_secret_is_detected():
    assert _iface(endpoint_ref="ENG-005:locus:password=x").embeds_secret() is True


def test_forward_transition_is_allowed():
    i = _iface()
    assert i.transition(ServiceState.CONTRACTED).state is ServiceState.CONTRACTED
    assert i.state is ServiceState.DEFINED


def test_backward_transition_is_rejected():
    i = _iface(state=ServiceState.EXECUTABLE)
    with pytest.raises(ServiceError, match="forward-only"):
        i.transition(ServiceState.DEFINED)


def test_non_state_transition_target_is_rejected():
    with pytest.raises(ServiceError, match="SOS-01"):
        _iface().transition("X")  # type: ignore[arg-type]


def test_to_dict_is_complete():
    d = _iface().to_dict()
    assert d["meta_class"] == "SMC-04"
    assert d["operations"] == list(_OPS)
    assert d["io_refs"] == list(_IO)
    assert "SMR-03" in d["relationships"]
    assert "RL-F2" in d["substrate_refs"]
    assert "DF-2" in d["substrate_refs"]


def test_foundation_reuse_names_frozen_primitives():
    assert {"ENG-001", "ENG-005", "RL-F2", "DF-2"} <= set(INTERFACE_FOUNDATION_REUSE)
