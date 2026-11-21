"""EC3-B13-U01 — InfrastructureCapability construct tests (WF-1/2/3/11/12 + UIL-03/04/05/06/13/15)."""

from __future__ import annotations

import pytest

from infrastructure.capability import (
    InfrastructureCapability,
    InfrastructureError,
    make_infrastructure_capability,
)
from infrastructure.capability_meta import (
    CAPABILITY_RELATIONSHIPS,
    INFRASTRUCTURE_META_CLASS,
    InfrastructureCapabilityKind,
    InfrastructureState,
)

ENABLES = "ENG-005:RL-F2:runtime.execution"


def test_capability_is_typed_identified_and_reuses_platform():
    c = make_infrastructure_capability("ucos.demo.capability", ENABLES)
    assert c.meta_class == INFRASTRUCTURE_META_CLASS  # WF-1
    assert c.type_tag == "ucos.demo.capability"  # UIL-03 typed
    assert c.capability_id.startswith("UCOS-INFRA-CAPABILITY-")  # UIL-04 identified
    assert len(c.value_digest) == 64  # ENG-003 value fidelity
    assert c.kind is InfrastructureCapabilityKind.HOSTING  # INFRASTRUCTURE-006 §2
    assert c.enables_ref == ENABLES  # ICAP-03 enables frozen construct by reference
    assert c.reuses_platform_capability() is True  # ICAP-01 / UIL-06


def test_capability_identity_is_deterministic_and_core_derived():
    a = make_infrastructure_capability("t", ENABLES)
    b = make_infrastructure_capability("t", ENABLES)
    c = make_infrastructure_capability("t", "ENG-005:AF-3:application.experience")
    assert a.capability_id == b.capability_id  # same core → same ENG-001 identity
    assert a.capability_id != c.capability_id  # different enable target → different id


def test_capability_is_immutable_objecthood():
    c = make_infrastructure_capability("t", ENABLES)
    with pytest.raises((AttributeError, TypeError)):
        c.type_tag = "other"  # frozen object (ENG-002 objecthood)


def test_untyped_capability_is_rejected_fail_closed():
    with pytest.raises(InfrastructureError):
        make_infrastructure_capability("", ENABLES)  # UIL-03
    with pytest.raises(InfrastructureError):
        make_infrastructure_capability("   ", ENABLES)


def test_bad_kind_is_rejected_fail_closed():
    with pytest.raises(InfrastructureError):
        InfrastructureCapability(type_tag="t", kind="not-a-kind", enables_ref=ENABLES)


def test_missing_enables_reference_is_rejected():
    with pytest.raises(InfrastructureError):
        make_infrastructure_capability("t", "")  # ICAP-03 — must enable a frozen construct
    with pytest.raises(InfrastructureError):
        make_infrastructure_capability("t", "   ")


def test_missing_capability_or_behavior_reference_is_rejected():
    with pytest.raises(InfrastructureError):
        make_infrastructure_capability("t", ENABLES, capability_ref="")  # ICAP-01 / UIL-06
    with pytest.raises(InfrastructureError):
        make_infrastructure_capability("t", ENABLES, behavior_ref="")  # UIL-10


def test_non_string_enables_reference_is_rejected():
    with pytest.raises(InfrastructureError):
        InfrastructureCapability(
            type_tag="t",
            kind=InfrastructureCapabilityKind.HOSTING,
            enables_ref=object(),  # type: ignore[arg-type]
        )


def test_bad_state_is_rejected_fail_closed():
    with pytest.raises(InfrastructureError):
        InfrastructureCapability(
            type_tag="t",
            kind=InfrastructureCapabilityKind.HOSTING,
            enables_ref=ENABLES,
            state="BAD",  # type: ignore[arg-type]
        )


def test_relationships_are_within_admitted_closure():
    c = make_infrastructure_capability("t", ENABLES)
    assert c.meta_relationships() == CAPABILITY_RELATIONSHIPS
    assert c.meta_relationships() == ("dependsOn",)


def test_lifecycle_is_forward_only():
    c = make_infrastructure_capability("t", ENABLES, state=InfrastructureState.DEFINED)
    provisioned = c.transition(InfrastructureState.PROVISIONED)
    assert provisioned.state is InfrastructureState.PROVISIONED
    active = provisioned.transition(InfrastructureState.ACTIVE)
    assert active.state is InfrastructureState.ACTIVE
    with pytest.raises(InfrastructureError):
        active.transition(InfrastructureState.DEFINED)  # forward-only — no backward


def test_transition_rejects_non_state_target():
    c = make_infrastructure_capability("t", ENABLES)
    with pytest.raises(InfrastructureError):
        c.transition("ACTIVE")  # type: ignore[arg-type]


def test_all_capability_kinds_construct():
    for kind in InfrastructureCapabilityKind:
        c = make_infrastructure_capability("t", ENABLES, kind=kind)
        assert c.kind is kind


def test_references_resolve_and_founding_acyclic():
    c = make_infrastructure_capability("t", ENABLES)
    assert c.references_resolve() is True  # WF-2
    assert c.is_founding_acyclic() is True  # WF-3 / UIL-09
    assert c.enables_by_reference() is True  # ICAP-03
    assert c.declares_mandatory_attributes() is True  # WF-1


def test_capability_is_not_resource_or_evaluative_facet():
    c = make_infrastructure_capability("t", ENABLES)
    assert c.is_resource() is False  # WF-5 N/A
    assert c.is_evaluative_facet() is False  # WF-10 N/A


def test_non_constitutive_and_no_secret_no_technology_no_ceiling():
    c = make_infrastructure_capability("t", ENABLES)
    assert c.confers_authority() is False  # UIL-15 / C7
    assert c.enacts_enforcement() is False  # UIL-14
    assert c.redefines_foundation() is False  # UIL-02
    assert c.is_new_primitive() is False  # WF-11 / UIL-01
    assert c.projects_completion() is False  # WF-12
    assert c.selects_technology() is False  # UIL-12 / UIL-15 (abstract references only)
    assert c.embeds_secret() is False
    assert c.declares_no_artificial_ceiling() is True  # UIL-13 / ICAP-04


def test_technology_bearing_capability_is_detected():
    techy = make_infrastructure_capability("t", "ENG-005:RL-F2:kubernetes.pod")
    assert techy.selects_technology() is True  # UIL-12 / UIL-15 — concrete technology named


def test_secret_bearing_capability_is_detected():
    leaky = make_infrastructure_capability("t", "ENG-005:RL-F2:password-vault")
    assert leaky.embeds_secret() is True  # UIL-15 / RR-07


def test_capability_to_dict_records_substrate_reuse():
    c = make_infrastructure_capability("t", ENABLES)
    payload = c.to_dict()
    assert payload["substrate_refs"] == [
        "ENG-001",
        "ENG-002",
        "ENG-003",
        "ENG-004",
        "ENG-005",
        "RL-F2",
        "PL-F2",
        "SF-2",
    ]
    assert payload["meta_class"] == "InfrastructureCapability"
    assert payload["kind"] == "Hosting-Capability"
    assert payload["enables_ref"] == ENABLES


def test_capability_type_is_the_realized_construct():
    assert isinstance(make_infrastructure_capability("t", ENABLES), InfrastructureCapability)
