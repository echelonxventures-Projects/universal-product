"""EC3-B11-U01 — Service construct tests (SMC-01 + SMK-01/03/05/06 + USL-03/04/05/09/10/12)."""

from __future__ import annotations

import pytest

from service.service import Service, ServiceError, make_service
from service.service_meta import (
    SERVICE_META_CLASS,
    SERVICE_RELATIONSHIPS,
    ServiceKind,
    ServiceState,
)

CAP_REF = "ENG-005:CAPABILITY:ucos.demo.capability"


def test_service_is_typed_identified_and_capability_realizing():
    s = make_service("ucos.demo.service", CAP_REF)
    assert s.meta_class == SERVICE_META_CLASS  # V1 (SMC-01)
    assert s.type_tag == "ucos.demo.service"  # USL-03 typed
    assert s.service_id.startswith("UCOS-SERVICE-")  # USL-04 identified (ENG-001)
    assert len(s.value_digest) == 64  # ENG-003 value fidelity
    assert s.kind is ServiceKind.ATOMIC  # SXH-01 classified
    assert s.capability_ref == CAP_REF  # SMR-01 realizes (by reference)


def test_service_identity_is_deterministic_and_core_derived():
    a = make_service("t", CAP_REF)
    b = make_service("t", CAP_REF)
    c = make_service("t", "ENG-005:CAPABILITY:other")
    assert a.service_id == b.service_id  # same core → same ENG-001 identity
    assert a.service_id != c.service_id  # different capability → different identity


def test_service_is_immutable_objecthood():
    s = make_service("t", CAP_REF)
    with pytest.raises((AttributeError, TypeError)):
        s.type_tag = "other"  # frozen object (ENG-002 objecthood)


def test_untyped_service_is_rejected_fail_closed():
    with pytest.raises(ServiceError):
        make_service("", CAP_REF)  # USL-03 — no untyped service may exist
    with pytest.raises(ServiceError):
        make_service("   ", CAP_REF)


def test_bad_kind_is_rejected_fail_closed():
    with pytest.raises(ServiceError):
        Service(type_tag="t", kind="not-a-kind", capability_ref=CAP_REF)  # SXH-01


def test_missing_capability_reference_is_rejected():
    with pytest.raises(ServiceError):
        make_service("t", "")  # SMR-01 — a service must realize a capability
    with pytest.raises(ServiceError):
        make_service("t", "   ")


def test_missing_behavior_or_composition_reference_is_rejected():
    with pytest.raises(ServiceError):
        make_service("t", CAP_REF, behavior_ref="")  # SMR-11 / USL-10
    with pytest.raises(ServiceError):
        make_service("t", CAP_REF, composition_ref="")  # SMR-12 / USL-09


def test_non_string_capability_reference_is_rejected():
    with pytest.raises(ServiceError):
        Service(type_tag="t", kind=ServiceKind.ATOMIC, capability_ref=object())  # type: ignore[arg-type]


def test_bad_state_is_rejected_fail_closed():
    with pytest.raises(ServiceError):
        Service(type_tag="t", kind=ServiceKind.ATOMIC, capability_ref=CAP_REF, state="BAD")  # type: ignore[arg-type]


def test_relationships_are_within_smr_closure():
    s = make_service("t", CAP_REF)
    assert set(s.meta_relationships()) <= set(SERVICE_RELATIONSHIPS)  # V2
    assert s.meta_relationships() == ("SMR-01", "SMR-10", "SMR-11", "SMR-12")


def test_lifecycle_is_forward_only():
    s = make_service("t", CAP_REF, state=ServiceState.DEFINED)
    contracted = s.transition(ServiceState.CONTRACTED)
    assert contracted.state is ServiceState.CONTRACTED
    executable = contracted.transition(ServiceState.EXECUTABLE)
    assert executable.state is ServiceState.EXECUTABLE
    with pytest.raises(ServiceError):
        executable.transition(ServiceState.DEFINED)  # USL-12 — no backward transition


def test_transition_rejects_non_state_target():
    s = make_service("t", CAP_REF)
    with pytest.raises(ServiceError):
        s.transition("EXECUTABLE")  # type: ignore[arg-type]


def test_all_service_kinds_construct():
    for kind in ServiceKind:
        s = make_service("t", CAP_REF, kind=kind)
        assert s.kind is kind


def test_references_resolve_and_founding_acyclic():
    s = make_service("t", CAP_REF)
    assert s.references_resolve() is True  # SOI-03 / SMK-05/06
    assert s.is_founding_acyclic() is True  # V4 / SMK-03


def test_non_constitutive_and_no_secret_no_technology():
    s = make_service("t", CAP_REF)
    assert s.confers_authority() is False  # USL-15 / C7
    assert s.redefines_foundation() is False  # USL-02 / SMI-05
    assert s.selects_technology() is False  # USL-15 (abstract references only)
    assert s.embeds_secret() is False


def test_technology_bearing_service_is_detected():
    techy = make_service("t", "ENG-005:CAPABILITY:kafka.consumer")
    assert techy.selects_technology() is True  # USL-15 — concrete technology named


def test_secret_bearing_service_is_detected():
    leaky = make_service("t", "ENG-005:CAPABILITY:password-vault")
    assert leaky.embeds_secret() is True  # USL-15 / RR-07


def test_service_to_dict_records_substrate_reuse():
    s = make_service("t", CAP_REF)
    payload = s.to_dict()
    assert payload["substrate_refs"] == [
        "ENG-001",
        "ENG-002",
        "ENG-003",
        "ENG-004",
        "ENG-005",
        "RL-F2",
        "PL-F2",
        "DF-2",
    ]
    assert payload["meta_class"] == "SMC-01"
    assert payload["kind"] == "Atomic-Service"
    assert payload["capability_ref"] == CAP_REF


def test_service_type_is_the_realized_construct():
    assert isinstance(make_service("t", CAP_REF), Service)
