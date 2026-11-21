"""EC3-B13-U04 — StorageHostingResource construct tests (WF-1/2/3/5/7/11/12 + UIL-03/04/05/07/08/11/13/15)."""

from __future__ import annotations

import pytest

from infrastructure.capability import InfrastructureError
from infrastructure.storage import (
    DEFAULT_DATUM_HOST_REF,
    DataPlacement,
    StorageCapacity,
    StorageHostingResource,
    make_data_placement,
    make_storage_hosting_resource,
)
from infrastructure.storage_meta import (
    INFRASTRUCTURE_META_CLASS,
    STORAGE_RELATIONSHIPS,
    InfrastructureState,
)

LOCALITY = "ENG-005:INFRASTRUCTURE-011:locality.foundation"
BOUNDARY = "ENG-005:INFRASTRUCTURE-011:isolation.boundary.a"


def test_storage_resource_is_typed_identified_and_declares_capacity_locality():
    r = make_storage_hosting_resource("ucos.demo.storage", LOCALITY)
    assert r.meta_class == INFRASTRUCTURE_META_CLASS  # WF-1
    assert r.type_tag == "ucos.demo.storage"  # UIL-03 typed
    assert r.resource_id.startswith("UCOS-INFRA-STORAGE-")  # UIL-04 identified
    assert len(r.value_digest) == 64  # ENG-003 value fidelity
    assert r.declares_capacity_and_locality() is True  # WF-5 / UIL-08 — governing rule
    assert r.hosts_data_by_reference() is True  # WF-7 / ISTO-01 / UIL-11 — the storage rule
    assert r.honors_isolation_boundaries() is True  # ISTO-03 / UIL-07
    assert r.located_by_reference() is True  # WF-5


def test_storage_identity_is_deterministic_and_core_derived():
    a = make_storage_hosting_resource("t", LOCALITY)
    b = make_storage_hosting_resource("t", LOCALITY)
    c = make_storage_hosting_resource("t", "ENG-005:INFRASTRUCTURE-011:locality.other")
    d = make_storage_hosting_resource("t", LOCALITY, amount=2)
    e = make_storage_hosting_resource("t", LOCALITY, datum_ref="ENG-005:DF-2:DATA-010.other")
    assert a.resource_id == b.resource_id  # same core → same ENG-001 identity
    assert a.resource_id != c.resource_id  # different locality → different id
    assert a.resource_id != d.resource_id  # different capacity → different id
    assert a.resource_id != e.resource_id  # different hosted datum → different id


def test_storage_resource_is_immutable_objecthood():
    r = make_storage_hosting_resource("t", LOCALITY)
    with pytest.raises((AttributeError, TypeError)):
        r.type_tag = "other"  # frozen object (ENG-002 objecthood)


def test_untyped_storage_resource_is_rejected_fail_closed():
    with pytest.raises(InfrastructureError):
        make_storage_hosting_resource("", LOCALITY)  # UIL-03
    with pytest.raises(InfrastructureError):
        make_storage_hosting_resource("   ", LOCALITY)


def test_missing_locality_reference_is_rejected():
    with pytest.raises(InfrastructureError):
        make_storage_hosting_resource("t", "")  # WF-5 / ISTO-02 — must declare a locality
    with pytest.raises(InfrastructureError):
        make_storage_hosting_resource("t", "   ")


def test_empty_placements_is_rejected():
    with pytest.raises(InfrastructureError):
        StorageHostingResource(
            type_tag="t",
            capacity=StorageCapacity(amount=1),
            locality_ref=LOCALITY,
            placements=(),  # WF-7 / ISTO-02 — must host ≥1 DATA-010 datum
        )


def test_non_placement_member_is_rejected():
    with pytest.raises(InfrastructureError):
        StorageHostingResource(
            type_tag="t",
            capacity=StorageCapacity(amount=1),
            locality_ref=LOCALITY,
            placements=("not-a-placement",),  # type: ignore[arg-type]
        )


def test_non_tuple_placements_is_rejected():
    with pytest.raises(InfrastructureError):
        StorageHostingResource(
            type_tag="t",
            capacity=StorageCapacity(amount=1),
            locality_ref=LOCALITY,
            placements=[make_data_placement()],  # type: ignore[arg-type] — not a tuple
        )


def test_missing_datum_reference_is_rejected():
    with pytest.raises(InfrastructureError):
        make_data_placement("")  # ISTO-01 / UIL-11 — must host a DATA-010 datum
    with pytest.raises(InfrastructureError):
        make_data_placement("   ")


def test_empty_placement_class_is_rejected():
    with pytest.raises(InfrastructureError):
        DataPlacement(datum_ref=DEFAULT_DATUM_HOST_REF, placement_class="")  # ISTO-01 / UIL-03
    with pytest.raises(InfrastructureError):
        DataPlacement(datum_ref=DEFAULT_DATUM_HOST_REF, placement_class="   ")


def test_non_bool_cross_boundary_is_rejected():
    with pytest.raises(InfrastructureError):
        DataPlacement(datum_ref=DEFAULT_DATUM_HOST_REF, cross_boundary="yes")  # type: ignore[arg-type]


def test_cross_boundary_without_boundary_reference_is_rejected():
    with pytest.raises(InfrastructureError):
        make_data_placement(DEFAULT_DATUM_HOST_REF, cross_boundary=True)  # ISTO-03 / UIL-07
    with pytest.raises(InfrastructureError):
        make_data_placement(DEFAULT_DATUM_HOST_REF, cross_boundary=True, boundary_ref="")


def test_present_but_invalid_boundary_reference_is_rejected():
    # cross_boundary False but a truthy, non-string boundary_ref is malformed.
    with pytest.raises(InfrastructureError):
        DataPlacement(datum_ref=DEFAULT_DATUM_HOST_REF, cross_boundary=False, boundary_ref=123)  # type: ignore[arg-type]


def test_cross_boundary_placement_honors_its_boundary():
    p = make_data_placement(DEFAULT_DATUM_HOST_REF, cross_boundary=True, boundary_ref=BOUNDARY)
    assert p.cross_boundary is True
    assert p.honors_boundary() is True  # ISTO-03 / UIL-07
    r = make_storage_hosting_resource("t", LOCALITY, placements=(p,))
    assert r.honors_isolation_boundaries() is True
    assert r.references_resolve() is True


def test_placement_canonical_and_datum_resolves():
    p = make_data_placement("ENG-005:DF-2:DATA-010.datum")
    assert p.datum_resolves() is True
    assert p.honors_boundary() is True  # non-cross placement
    assert p.canonical() == {
        "datum_ref": "ENG-005:DF-2:DATA-010.datum",
        "placement_class": "data-placement",
        "cross_boundary": False,
        "boundary_ref": "",
    }


def test_non_string_locality_reference_is_rejected():
    with pytest.raises(InfrastructureError):
        StorageHostingResource(
            type_tag="t",
            capacity=StorageCapacity(amount=1),
            locality_ref=object(),  # type: ignore[arg-type]
            placements=(make_data_placement(),),
        )


def test_bad_capacity_is_rejected_fail_closed():
    with pytest.raises(InfrastructureError):
        StorageHostingResource(
            type_tag="t",
            capacity="1tb",  # type: ignore[arg-type]
            locality_ref=LOCALITY,
            placements=(make_data_placement(),),
        )


def test_bad_state_is_rejected_fail_closed():
    with pytest.raises(InfrastructureError):
        StorageHostingResource(
            type_tag="t",
            capacity=StorageCapacity(amount=1),
            locality_ref=LOCALITY,
            placements=(make_data_placement(),),
            state="BAD",  # type: ignore[arg-type]
        )


def test_storage_capacity_rejects_negative_amount():
    with pytest.raises(InfrastructureError):
        StorageCapacity(amount=-1)  # ENG-003 / ISTO-02 — non-negative quantity


def test_storage_capacity_rejects_boolean_amount():
    with pytest.raises(InfrastructureError):
        StorageCapacity(amount=True)  # type: ignore[arg-type] — bool is not a quantity


def test_storage_capacity_rejects_empty_unit():
    with pytest.raises(InfrastructureError):
        StorageCapacity(amount=1, unit="")
    with pytest.raises(InfrastructureError):
        StorageCapacity(amount=1, unit="   ")


def test_storage_capacity_zero_is_valid_and_unbounded():
    cap = StorageCapacity(amount=0)
    assert cap.amount == 0
    assert cap.unit == "storage-unit"
    assert cap.is_unbounded() is True  # ISTO-04 / UIL-13
    assert cap.canonical() == {"amount": 0, "unit": "storage-unit"}


def test_relationships_are_within_admitted_closure():
    r = make_storage_hosting_resource("t", LOCALITY)
    assert r.meta_relationships() == STORAGE_RELATIONSHIPS
    assert r.meta_relationships() == ("hosts", "locatedAt")


def test_lifecycle_is_forward_only():
    r = make_storage_hosting_resource("t", LOCALITY, state=InfrastructureState.DEFINED)
    provisioned = r.transition(InfrastructureState.PROVISIONED)
    assert provisioned.state is InfrastructureState.PROVISIONED
    active = provisioned.transition(InfrastructureState.ACTIVE)
    assert active.state is InfrastructureState.ACTIVE
    with pytest.raises(InfrastructureError):
        active.transition(InfrastructureState.DEFINED)  # forward-only — no backward


def test_transition_rejects_non_state_target():
    r = make_storage_hosting_resource("t", LOCALITY)
    with pytest.raises(InfrastructureError):
        r.transition("ACTIVE")  # type: ignore[arg-type]


def test_capacity_and_placements_may_be_supplied_directly():
    cap = StorageCapacity(amount=7, unit="storage-unit")
    placements = (
        make_data_placement("ENG-005:DF-2:DATA-010.a"),
        make_data_placement("ENG-005:DF-2:DATA-010.b"),
    )
    r = make_storage_hosting_resource("t", LOCALITY, capacity=cap, placements=placements)
    assert r.capacity is cap
    assert r.capacity.amount == 7
    assert len(r.placements) == 2


def test_references_resolve_and_founding_acyclic():
    r = make_storage_hosting_resource("t", LOCALITY)
    assert r.references_resolve() is True  # WF-2
    assert r.is_founding_acyclic() is True  # WF-3
    assert r.declares_mandatory_attributes() is True  # WF-1 / WF-5 / WF-7


def test_storage_resource_is_resource_and_not_evaluative_facet():
    r = make_storage_hosting_resource("t", LOCALITY)
    assert r.is_resource() is True  # WF-5
    assert r.is_evaluative_facet() is False  # WF-10 N/A


def test_declares_no_artificial_ceiling():
    r = make_storage_hosting_resource("t", LOCALITY, amount=10**12)
    assert r.declares_no_artificial_ceiling() is True  # UIL-13 / ISTO-04 — unbounded


def test_non_constitutive_and_no_secret_no_technology():
    r = make_storage_hosting_resource("t", LOCALITY)
    assert r.confers_authority() is False  # UIL-15 / C7
    assert r.enacts_enforcement() is False  # UIL-14
    assert r.redefines_foundation() is False  # UIL-02 / UIL-11
    assert r.is_new_primitive() is False  # WF-11 / UIL-01
    assert r.projects_completion() is False  # WF-12
    assert r.selects_technology() is False  # UIL-15 (abstract references only)
    assert r.embeds_secret() is False


def test_technology_bearing_resource_is_detected():
    techy = make_storage_hosting_resource("t", LOCALITY, datum_ref="ENG-005:DF-2:postgres.table")
    assert techy.selects_technology() is True  # UIL-15 / ISTO-05

    techy_unit = make_storage_hosting_resource("t", LOCALITY, unit="mongodb-collection")
    assert techy_unit.selects_technology() is True


def test_secret_bearing_resource_is_detected():
    leaky = make_storage_hosting_resource("t", "ENG-005:INFRASTRUCTURE-011:password-vault")
    assert leaky.embeds_secret() is True  # UIL-15 / RR-07


def test_storage_to_dict_records_substrate_reuse():
    r = make_storage_hosting_resource("t", LOCALITY)
    payload = r.to_dict()
    assert payload["substrate_refs"] == [
        "ENG-001",
        "ENG-002",
        "ENG-003",
        "ENG-004",
        "ENG-005",
        "DF-2",
    ]
    assert payload["meta_class"] == "StorageHostingResource"
    assert payload["capacity"] == {"amount": 1, "unit": "storage-unit"}
    assert payload["locality_ref"] == LOCALITY
    assert payload["placements"] == [
        {
            "datum_ref": DEFAULT_DATUM_HOST_REF,
            "placement_class": "data-placement",
            "cross_boundary": False,
            "boundary_ref": "",
        }
    ]


def test_storage_type_is_the_realized_construct():
    assert isinstance(make_storage_hosting_resource("t", LOCALITY), StorageHostingResource)
