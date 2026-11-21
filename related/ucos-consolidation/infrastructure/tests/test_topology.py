"""Tests for EC3-B13-U06 Topology & Distribution constructs.

Covers:
- WF-1: Topology (meta-class single, mandatory attributes)
- WF-2: LocalityMap (references resolve, meta-constraints)
- WF-3: PlacementRule (founding acyclic)
- WF-8 / UIL-12: DistributionArrangement (hosts AF-3/SF-2 by reference)
- ITOP-03: DeliveryArrangement (hosts by reference, no transport tech)
- ITOP-04: LocalityMap (abstract locality only)
- UIL-03: All constructs typed
- UIL-15: No technology, no secret, no authority
- Lifecycle: Forward-only transition
"""

from __future__ import annotations

import pytest

from infrastructure.capability import InfrastructureError
from infrastructure.topology import (
    INFRA_TOPOLOGY_ID_FAMILY,
    DeliveryArrangement,
    DistributionArrangement,
    LocalityMap,
    PlacementRule,
    Topology,
    make_delivery_arrangement,
    make_distribution_arrangement,
    make_locality_map,
    make_placement_rule,
    make_topology,
)
from infrastructure.topology_meta import InfrastructureState

# ===========================================================================
# Topology
# ===========================================================================


def test_topology_is_typed_identified_and_foundational() -> None:
    t = make_topology("test.topology.foundation")
    assert t.construct_id.startswith(INFRA_TOPOLOGY_ID_FAMILY)
    assert t.type_tag == "test.topology.foundation"
    assert t.meta_class == "Topology"
    assert t.value_digest
    assert t.references_resolve()
    assert t.is_founding_acyclic()
    assert not t.is_resource()
    assert not t.confers_authority()


def test_topology_rejects_empty_type() -> None:
    with pytest.raises(InfrastructureError):
        make_topology("")


def test_topology_rejects_bad_state() -> None:
    with pytest.raises(InfrastructureError):
        Topology(type_tag="test", state="invalid")  # type: ignore[arg-type]


def test_topology_to_dict() -> None:
    t = make_topology(
        "test.topology", composition_ref="ENG-005:PL-F2:comp", contains=("ENG-005:node-1",)
    )
    d = t.to_dict()
    assert d["meta_class"] == "Topology"
    assert d["type_tag"] == "test.topology"
    assert d["composition_ref"] == "ENG-005:PL-F2:comp"
    assert "contains" in d


# ===========================================================================
# LocalityMap
# ===========================================================================


def test_locality_map_is_typed_and_evaluative() -> None:
    lm = make_locality_map("test.localitymap", locality_type="zone")
    assert lm.construct_id.startswith(INFRA_TOPOLOGY_ID_FAMILY)
    assert lm.type_tag == "test.localitymap"
    assert lm.locality_type == "zone"
    assert lm.meta_class == "Topology"
    assert lm.is_evaluative_facet()
    assert not lm.selects_technology()


def test_locality_map_rejects_empty_type() -> None:
    with pytest.raises(InfrastructureError):
        make_locality_map("")


def test_locality_map_rejects_empty_locality_type() -> None:
    with pytest.raises(InfrastructureError):
        LocalityMap(type_tag="test", locality_type="")  # type: ignore[arg-type]


def test_locality_map_to_dict() -> None:
    lm = make_locality_map("test.lm", mapping_refs=("ENG-005:node-1",))
    d = lm.to_dict()
    assert d["locality_type"] == "region"
    assert "mapping_refs" in d


# ===========================================================================
# PlacementRule
# ===========================================================================


def test_placement_rule_is_typed_and_evaluative() -> None:
    pr = make_placement_rule("test.placement", rule_kind="anti-affinity")
    assert pr.construct_id.startswith(INFRA_TOPOLOGY_ID_FAMILY)
    assert pr.type_tag == "test.placement"
    assert pr.rule_kind == "anti-affinity"
    assert pr.meta_class == "Topology"
    assert pr.is_evaluative_facet()


def test_placement_rule_rejects_empty_type() -> None:
    with pytest.raises(InfrastructureError):
        make_placement_rule("")


def test_placement_rule_rejects_empty_rule_kind() -> None:
    with pytest.raises(InfrastructureError):
        PlacementRule(type_tag="test", rule_kind="", state=InfrastructureState.DEFINED)


def test_placement_rule_with_targets() -> None:
    pr = make_placement_rule("test.pr", target_refs=("ENG-005:node-1",))
    assert pr.references_resolve()
    d = pr.to_dict()
    assert d["rule_kind"] == "affinity"


# ===========================================================================
# DistributionArrangement
# ===========================================================================


def test_distribution_is_typed_and_hosts_by_reference() -> None:
    d = make_distribution_arrangement("test.distribution", hosts=("ENG-005:AF-3:exp",))
    assert d.construct_id.startswith(INFRA_TOPOLOGY_ID_FAMILY)
    assert d.type_tag == "test.distribution"
    assert d.meta_class == "Distribution"
    assert d.hosts_by_reference()
    assert not d.selects_technology()
    assert not d.confers_authority()


def test_distribution_rejects_empty_hosts() -> None:
    with pytest.raises(InfrastructureError):
        make_distribution_arrangement("test.distribution", hosts=())


def test_distribution_rejects_empty_type() -> None:
    with pytest.raises(InfrastructureError):
        make_distribution_arrangement("", hosts=("ENG-005:cap",))


def test_distribution_rejects_empty_host_member() -> None:
    with pytest.raises(InfrastructureError):
        make_distribution_arrangement("test.d", hosts=("",))


def test_distribution_rejects_bad_state() -> None:
    with pytest.raises(InfrastructureError):
        DistributionArrangement(type_tag="test", hosts=("ENG-005:cap",), state="invalid")  # type: ignore[arg-type]


def test_distribution_to_dict() -> None:
    d = make_distribution_arrangement(
        "test.d", hosts=("ENG-005:AF-3:exp",), strategy="geo-replicated"
    )
    di = d.to_dict()
    assert di["meta_class"] == "Distribution"
    assert di["strategy"] == "geo-replicated"
    assert "hosts" in di


# ===========================================================================
# DeliveryArrangement
# ===========================================================================


def test_delivery_is_typed_and_hosts_by_reference() -> None:
    dl = make_delivery_arrangement("test.delivery", hosts=("ENG-005:AF-3:exp",))
    assert dl.construct_id.startswith(INFRA_TOPOLOGY_ID_FAMILY)
    assert dl.type_tag == "test.delivery"
    assert dl.meta_class == "Distribution"
    assert dl.hosts_by_reference()
    assert dl.delivery_mode == "direct"
    assert not dl.selects_technology()


def test_delivery_rejects_empty_hosts() -> None:
    with pytest.raises(InfrastructureError):
        make_delivery_arrangement("test.delivery", hosts=())


def test_delivery_rejects_empty_type() -> None:
    with pytest.raises(InfrastructureError):
        make_delivery_arrangement("", hosts=("ENG-005:cap",))


def test_delivery_rejects_empty_delivery_mode() -> None:
    with pytest.raises(InfrastructureError):
        DeliveryArrangement(type_tag="test", hosts=("ENG-005:cap",), delivery_mode="")


def test_delivery_to_dict() -> None:
    dl = make_delivery_arrangement(
        "test.dl", hosts=("ENG-005:SF-2:svc",), delivery_mode="push", channel_refs=("ENG-005:ch-1",)
    )
    di = dl.to_dict()
    assert di["delivery_mode"] == "push"
    assert "channel_refs" in di


# ===========================================================================
# Cross-construct / lifecycle
# ===========================================================================


def test_forward_lifecycle_transition() -> None:
    t = make_topology("test.topology")
    assert t.state == InfrastructureState.DEFINED
    t2 = t.transition(InfrastructureState.PROVISIONED)
    assert t2.state == InfrastructureState.PROVISIONED
    # original unchanged (frozen)
    assert t.state == InfrastructureState.DEFINED


def test_lifecycle_rejects_backward_transition() -> None:
    t = make_topology("test.topology", state=InfrastructureState.ACTIVE)
    with pytest.raises(InfrastructureError):
        t.transition(InfrastructureState.DEFINED)


def test_lifecycle_rejects_non_state() -> None:
    t = make_topology("test.topology")
    with pytest.raises(InfrastructureError):
        t.transition("ACTIVE")  # type: ignore[arg-type]


def test_all_constructs_technology_neutral() -> None:
    constructs = [
        make_topology("test.topo"),
        make_locality_map("test.lm"),
        make_placement_rule("test.pr"),
        make_distribution_arrangement("test.d", hosts=("ENG-005:cap",)),
        make_delivery_arrangement("test.dl", hosts=("ENG-005:cap",)),
    ]
    for c in constructs:
        assert not c.selects_technology(), f"{c.meta_class} selects technology"
        assert not c.embeds_secret(), f"{c.meta_class} embeds secret"
        assert not c.confers_authority(), f"{c.meta_class} confers authority"
        assert not c.redefines_foundation(), f"{c.meta_class} redefines foundation"
        assert not c.is_new_primitive(), f"{c.meta_class} is new primitive"


def test_is_founding_acyclic_answers_false_when_the_core_cannot_be_canonicalised() -> None:
    """The topology construct's except-arm must answer False, not raise, on a broken core."""

    class _Broken(Topology):
        def canonical_core(self):
            return {"poison": object()}

    broken = _Broken(type_tag="ITOP-BROKEN-01")
    assert broken.is_founding_acyclic() is False


def test_distribution_rejects_a_blank_strategy() -> None:
    """A strategy that says nothing is no strategy; the guard refuses whitespace as well as ''."""
    with pytest.raises(InfrastructureError, match="non-empty strategy"):
        make_distribution_arrangement("test.d", hosts=("ENG-005:AF-3:exp",), strategy="   ")
