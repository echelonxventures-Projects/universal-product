"""EC3-B13-U02 — ComputeResource construct tests (WF-1/2/3/5/11/12 + UIL-03/04/05/08/09/10/13/15)."""

from __future__ import annotations

import pytest

from infrastructure.capability import InfrastructureError
from infrastructure.compute import (
    DEFAULT_EXECUTION_HOST_REF,
    ComputeCapacity,
    ComputeResource,
    make_compute_resource,
)
from infrastructure.compute_meta import (
    COMPUTE_RELATIONSHIPS,
    INFRASTRUCTURE_META_CLASS,
    InfrastructureState,
)

LOCALITY = "ENG-005:INFRASTRUCTURE-011:locality.foundation"


def test_compute_resource_is_typed_identified_and_declares_capacity_locality():
    r = make_compute_resource("ucos.demo.compute", LOCALITY)
    assert r.meta_class == INFRASTRUCTURE_META_CLASS  # WF-1
    assert r.type_tag == "ucos.demo.compute"  # UIL-03 typed
    assert r.resource_id.startswith("UCOS-INFRA-COMPUTE-")  # UIL-04 identified
    assert len(r.value_digest) == 64  # ENG-003 value fidelity
    assert r.declares_capacity_and_locality() is True  # WF-5 / UIL-08 — the governing rule
    assert r.hosts_execution_by_reference() is True  # ICMP-01 / UIL-10
    assert r.located_by_reference() is True  # WF-5
    assert r.execution_host_ref == DEFAULT_EXECUTION_HOST_REF


def test_compute_identity_is_deterministic_and_core_derived():
    a = make_compute_resource("t", LOCALITY)
    b = make_compute_resource("t", LOCALITY)
    c = make_compute_resource("t", "ENG-005:INFRASTRUCTURE-011:locality.other")
    d = make_compute_resource("t", LOCALITY, amount=2)
    assert a.resource_id == b.resource_id  # same core → same ENG-001 identity
    assert a.resource_id != c.resource_id  # different locality → different id
    assert a.resource_id != d.resource_id  # different capacity → different id


def test_compute_resource_is_immutable_objecthood():
    r = make_compute_resource("t", LOCALITY)
    with pytest.raises((AttributeError, TypeError)):
        r.type_tag = "other"  # frozen object (ENG-002 objecthood)


def test_untyped_compute_resource_is_rejected_fail_closed():
    with pytest.raises(InfrastructureError):
        make_compute_resource("", LOCALITY)  # UIL-03
    with pytest.raises(InfrastructureError):
        make_compute_resource("   ", LOCALITY)


def test_missing_locality_reference_is_rejected():
    with pytest.raises(InfrastructureError):
        make_compute_resource("t", "")  # WF-5 / ICMP-02 — must declare a locality
    with pytest.raises(InfrastructureError):
        make_compute_resource("t", "   ")


def test_missing_execution_host_reference_is_rejected():
    with pytest.raises(InfrastructureError):
        make_compute_resource("t", LOCALITY, execution_host_ref="")  # ICMP-01 / UIL-10
    with pytest.raises(InfrastructureError):
        make_compute_resource("t", LOCALITY, execution_host_ref="   ")


def test_non_string_locality_reference_is_rejected():
    with pytest.raises(InfrastructureError):
        ComputeResource(
            type_tag="t",
            capacity=ComputeCapacity(amount=1),
            locality_ref=object(),  # type: ignore[arg-type]
        )


def test_bad_capacity_is_rejected_fail_closed():
    with pytest.raises(InfrastructureError):
        ComputeResource(type_tag="t", capacity="1cpu", locality_ref=LOCALITY)  # type: ignore[arg-type]


def test_bad_state_is_rejected_fail_closed():
    with pytest.raises(InfrastructureError):
        ComputeResource(
            type_tag="t",
            capacity=ComputeCapacity(amount=1),
            locality_ref=LOCALITY,
            state="BAD",  # type: ignore[arg-type]
        )


def test_compute_capacity_rejects_negative_amount():
    with pytest.raises(InfrastructureError):
        ComputeCapacity(amount=-1)  # ENG-003 / ICMP-02 — non-negative quantity


def test_compute_capacity_rejects_boolean_amount():
    with pytest.raises(InfrastructureError):
        ComputeCapacity(amount=True)  # type: ignore[arg-type] — bool is not a quantity


def test_compute_capacity_rejects_empty_unit():
    with pytest.raises(InfrastructureError):
        ComputeCapacity(amount=1, unit="")
    with pytest.raises(InfrastructureError):
        ComputeCapacity(amount=1, unit="   ")


def test_compute_capacity_zero_is_valid_and_unbounded():
    cap = ComputeCapacity(amount=0)
    assert cap.amount == 0
    assert cap.unit == "compute-unit"
    assert cap.is_unbounded() is True  # ICMP-04 / UIL-13
    assert cap.canonical() == {"amount": 0, "unit": "compute-unit"}


def test_relationships_are_within_admitted_closure():
    r = make_compute_resource("t", LOCALITY)
    assert r.meta_relationships() == COMPUTE_RELATIONSHIPS
    assert r.meta_relationships() == ("hosts", "locatedAt")


def test_lifecycle_is_forward_only():
    r = make_compute_resource("t", LOCALITY, state=InfrastructureState.DEFINED)
    provisioned = r.transition(InfrastructureState.PROVISIONED)
    assert provisioned.state is InfrastructureState.PROVISIONED
    active = provisioned.transition(InfrastructureState.ACTIVE)
    assert active.state is InfrastructureState.ACTIVE
    with pytest.raises(InfrastructureError):
        active.transition(InfrastructureState.DEFINED)  # forward-only — no backward


def test_transition_rejects_non_state_target():
    r = make_compute_resource("t", LOCALITY)
    with pytest.raises(InfrastructureError):
        r.transition("ACTIVE")  # type: ignore[arg-type]


def test_capacity_may_be_supplied_directly():
    cap = ComputeCapacity(amount=7, unit="compute-unit")
    r = make_compute_resource("t", LOCALITY, capacity=cap)
    assert r.capacity is cap
    assert r.capacity.amount == 7


def test_references_resolve_and_founding_acyclic():
    r = make_compute_resource("t", LOCALITY)
    assert r.references_resolve() is True  # WF-2
    assert r.is_founding_acyclic() is True  # WF-3 / UIL-09 / ICMP-03
    assert r.declares_mandatory_attributes() is True  # WF-1 / WF-5


def test_compute_resource_is_resource_and_not_evaluative_facet():
    r = make_compute_resource("t", LOCALITY)
    assert r.is_resource() is True  # WF-5
    assert r.is_evaluative_facet() is False  # WF-10 N/A


def test_declares_no_artificial_ceiling():
    r = make_compute_resource("t", LOCALITY, amount=10**9)
    assert r.declares_no_artificial_ceiling() is True  # UIL-13 / ICMP-04 — unbounded


def test_non_constitutive_and_no_secret_no_technology():
    r = make_compute_resource("t", LOCALITY)
    assert r.confers_authority() is False  # UIL-15 / C7
    assert r.enacts_enforcement() is False  # UIL-14
    assert r.redefines_foundation() is False  # UIL-02
    assert r.is_new_primitive() is False  # WF-11 / UIL-01
    assert r.projects_completion() is False  # WF-12
    assert r.selects_technology() is False  # UIL-12 / UIL-15 (abstract references only)
    assert r.embeds_secret() is False


def test_technology_bearing_resource_is_detected():
    techy = make_compute_resource("t", LOCALITY, execution_host_ref="ENG-005:RL-F2:kubernetes.pod")
    assert techy.selects_technology() is True  # UIL-12 / UIL-15 / ICMP-05

    techy_unit = make_compute_resource("t", LOCALITY, unit="vmware-vcpu")
    assert techy_unit.selects_technology() is True


def test_secret_bearing_resource_is_detected():
    leaky = make_compute_resource("t", "ENG-005:INFRASTRUCTURE-011:password-vault")
    assert leaky.embeds_secret() is True  # UIL-15 / RR-07


def test_compute_to_dict_records_substrate_reuse():
    r = make_compute_resource("t", LOCALITY)
    payload = r.to_dict()
    assert payload["substrate_refs"] == [
        "ENG-001",
        "ENG-002",
        "ENG-003",
        "ENG-004",
        "ENG-005",
        "RL-F2",
    ]
    assert payload["meta_class"] == "ComputeResource"
    assert payload["capacity"] == {"amount": 1, "unit": "compute-unit"}
    assert payload["locality_ref"] == LOCALITY
    assert payload["execution_host_ref"] == DEFAULT_EXECUTION_HOST_REF


def test_compute_type_is_the_realized_construct():
    assert isinstance(make_compute_resource("t", LOCALITY), ComputeResource)
