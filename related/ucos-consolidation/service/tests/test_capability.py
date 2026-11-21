"""EC3-B11-U02 — Universal Capability construct tests (SMC-02).

Covers construction (fail-closed), identity/value fidelity, meta-model participation,
non-constitutiveness, forward-only lifecycle, and serialization.
"""

from __future__ import annotations

import pytest

from service.capability import (
    CAPABILITY_FOUNDATION_REUSE,
    CAPABILITY_ID_PREFIX,
    Capability,
    make_capability,
)
from service.capability_meta import (
    CAPABILITY_META_CLASS,
    CAPABILITY_RELATIONSHIPS,
    CapabilityKind,
)
from service.service import ServiceError
from service.service_meta import ServiceState


def test_make_capability_builds_a_wellformed_functional_capability():
    c = make_capability("ucos.demo.capability")
    assert c.type_tag == "ucos.demo.capability"
    assert c.kind is CapabilityKind.FUNCTIONAL
    assert c.state is ServiceState.DEFINED
    assert c.meta_class == CAPABILITY_META_CLASS == "SMC-02"


@pytest.mark.parametrize("kind", list(CapabilityKind))
def test_all_sxh02_kinds_are_constructible(kind):
    c = make_capability("t", kind=kind)
    assert c.kind is kind


def test_empty_type_tag_is_rejected():
    with pytest.raises(ServiceError, match="typed"):
        make_capability("   ")


def test_non_string_type_tag_is_rejected():
    with pytest.raises(ServiceError, match="typed"):
        Capability(type_tag=123, kind=CapabilityKind.FUNCTIONAL)  # type: ignore[arg-type]


def test_bad_kind_is_rejected():
    with pytest.raises(ServiceError, match="SXH-02"):
        Capability(type_tag="t", kind="not-a-kind")  # type: ignore[arg-type]


def test_blank_behavior_ref_is_rejected():
    with pytest.raises(ServiceError, match="behavior_ref"):
        make_capability("t", behavior_ref="  ")


def test_blank_platform_ref_is_rejected():
    with pytest.raises(ServiceError, match="platform_ref"):
        make_capability("t", platform_ref="")


def test_non_string_service_ref_is_rejected():
    with pytest.raises(ServiceError, match="service_ref"):
        Capability(type_tag="t", kind=CapabilityKind.FUNCTIONAL, service_ref=7)  # type: ignore[arg-type]


def test_bad_state_is_rejected():
    with pytest.raises(ServiceError, match="SOS-01"):
        Capability(type_tag="t", kind=CapabilityKind.FUNCTIONAL, state="LIVE")  # type: ignore[arg-type]


def test_identity_is_deterministic_and_prefixed():
    a = make_capability("t")
    b = make_capability("t")
    assert a.capability_id == b.capability_id
    assert a.capability_id.startswith(CAPABILITY_ID_PREFIX + "-")
    assert len(a.value_digest) == 64


def test_distinct_cores_yield_distinct_identity():
    a = make_capability("t", kind=CapabilityKind.QUERY)
    b = make_capability("t", kind=CapabilityKind.COMMAND)
    assert a.capability_id != b.capability_id


def test_meta_relationships_and_class():
    c = make_capability("t")
    assert c.meta_relationships() == CAPABILITY_RELATIONSHIPS
    assert set(c.meta_relationships()) <= {f"SMR-{n:02d}" for n in range(1, 14)}
    assert c.is_founding_acyclic() is True
    assert c.references_resolve() is True


def test_non_constitutive_defaults():
    c = make_capability("t")
    assert c.confers_authority() is False
    assert c.selects_technology() is False
    assert c.embeds_secret() is False
    assert c.redefines_foundation() is False


def test_selects_technology_is_detected():
    c = make_capability("t", behavior_ref="ENG-005:RL-F2:grpc.invoke")
    assert c.selects_technology() is True


def test_embeds_secret_is_detected():
    c = make_capability("t", service_ref="ENG-005:SMC-01:password=hunter2")
    assert c.embeds_secret() is True


def test_forward_transition_is_allowed():
    c = make_capability("t")
    advanced = c.transition(ServiceState.CONTRACTED)
    assert advanced.state is ServiceState.CONTRACTED
    assert c.state is ServiceState.DEFINED  # immutable original


def test_backward_transition_is_rejected():
    c = make_capability("t", state=ServiceState.EXECUTABLE)
    with pytest.raises(ServiceError, match="forward-only"):
        c.transition(ServiceState.DEFINED)


def test_non_state_transition_target_is_rejected():
    c = make_capability("t")
    with pytest.raises(ServiceError, match="SOS-01"):
        c.transition("NOPE")  # type: ignore[arg-type]


def test_to_dict_is_complete_and_serializable():
    c = make_capability("t", service_ref="ENG-005:SMC-01:svc")
    d = c.to_dict()
    assert d["meta_class"] == "SMC-02"
    assert d["capability_id"] == c.capability_id
    assert d["service_ref"] == "ENG-005:SMC-01:svc"
    assert "SMR-01" in d["relationships"]
    assert d["substrate_refs"]


def test_foundation_reuse_names_the_frozen_primitives():
    assert {"ENG-001", "ENG-005", "RL-F2", "PL-F2", "SMC-01"} <= set(CAPABILITY_FOUNDATION_REUSE)
