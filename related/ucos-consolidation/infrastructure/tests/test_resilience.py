"""Tests for EC3-B13-U07 Resilience & Availability constructs.

Covers:
- WF-1: AvailabilityTopology (meta-class single, mandatory attributes)
- WF-9 / UIL-13: ScalingArrangement (scalingPosture with no artificial ceiling)
- WF-10: Both constructs evaluative, non-enforcing
- IRES-01: Evaluative, enact/provision nothing
- IRES-02: Scaling declares no artificial ceiling
- IRES-06: No HA/failover/autoscale technology selected
- UIL-03: All constructs typed
- UIL-15: No technology, no secret, no authority
- Lifecycle: Forward-only transition
"""

from __future__ import annotations

import pytest

from infrastructure.capability import InfrastructureError
from infrastructure.resilience import (
    DEFAULT_CLUSTER_REF,
    INFRA_RESILIENCE_ID_FAMILY,
    AvailabilityTopology,
    ScalingArrangement,
    _InfraConstruct,
    _require_posture,
    _require_state,
    _require_typed,
    make_availability_topology,
    make_scaling_arrangement,
)
from infrastructure.resilience_meta import InfrastructureState

# ===========================================================================
# AvailabilityTopology
# ===========================================================================


def test_availability_topology_is_typed_identified_and_evaluative() -> None:
    at = make_availability_topology("test.availability.foundation")
    assert at.construct_id.startswith(INFRA_RESILIENCE_ID_FAMILY)
    assert at.type_tag == "test.availability.foundation"
    assert at.meta_class == "AvailabilityTopology"
    assert at.value_digest
    assert at.references_resolve()
    assert at.is_evaluative_facet()
    assert not at.is_resource()
    assert not at.confers_authority()


def test_availability_topology_defaults() -> None:
    at = make_availability_topology("test.avail")
    assert at.resilience_posture == "redundant"
    assert len(at.sustains) >= 1
    assert not at.enacts_enforcement()


def test_availability_topology_rejects_empty_type() -> None:
    with pytest.raises(InfrastructureError):
        make_availability_topology("")


def test_availability_topology_rejects_invalid_posture() -> None:
    with pytest.raises(InfrastructureError):
        make_availability_topology("test.at", resilience_posture="unknown")


def test_availability_topology_rejects_empty_sustains() -> None:
    with pytest.raises(InfrastructureError):
        AvailabilityTopology(
            type_tag="test.at",
            resilience_posture="redundant",
            sustains=(),
            state=InfrastructureState.DEFINED,
        )


def test_availability_topology_rejects_bad_state() -> None:
    with pytest.raises(InfrastructureError):
        AvailabilityTopology(type_tag="test", state="invalid")  # type: ignore[arg-type]


def test_availability_topology_posture_valid() -> None:
    for posture in ("single", "redundant", "fault-tolerant", "self-healing"):
        at = make_availability_topology("test.at", resilience_posture=posture)
        assert at.has_valid_posture()


def test_availability_topology_to_dict() -> None:
    at = make_availability_topology(
        "test.avail",
        resilience_posture="fault-tolerant",
        sustains=("ENG-005:Cluster:c1",),
        continuity_metrics=("rto-1h", "rpo-15m"),
    )
    d = at.to_dict()
    assert d["meta_class"] == "AvailabilityTopology"
    assert d["resilience_posture"] == "fault-tolerant"
    assert "sustains" in d
    assert "continuity_metrics" in d


# ===========================================================================
# ScalingArrangement
# ===========================================================================


def test_scaling_arrangement_is_typed_identified_and_evaluative() -> None:
    sa = make_scaling_arrangement("test.scaling.foundation")
    assert sa.construct_id.startswith(INFRA_RESILIENCE_ID_FAMILY)
    assert sa.type_tag == "test.scaling.foundation"
    assert sa.meta_class == "ScalingArrangement"
    assert sa.value_digest
    assert sa.references_resolve()
    assert sa.is_evaluative_facet()
    assert not sa.is_resource()
    assert not sa.confers_authority()


def test_scaling_arrangement_defaults() -> None:
    sa = make_scaling_arrangement("test.scaling")
    assert sa.scaling_posture == "elastic"
    assert len(sa.scales) >= 1
    assert not sa.enacts_enforcement()


def test_scaling_arrangement_rejects_empty_type() -> None:
    with pytest.raises(InfrastructureError):
        make_scaling_arrangement("")


def test_scaling_arrangement_rejects_invalid_posture() -> None:
    with pytest.raises(InfrastructureError):
        make_scaling_arrangement("test.sa", scaling_posture="infinite")


def test_scaling_arrangement_rejects_empty_scales() -> None:
    with pytest.raises(InfrastructureError):
        ScalingArrangement(
            type_tag="test.sa",
            scaling_posture="elastic",
            scales=(),
            state=InfrastructureState.DEFINED,
        )


def test_scaling_arrangement_rejects_bad_state() -> None:
    with pytest.raises(InfrastructureError):
        ScalingArrangement(type_tag="test", state="invalid")  # type: ignore[arg-type]


def test_scaling_arrangement_posture_valid() -> None:
    for posture in ("fixed", "elastic", "unbounded"):
        sa = make_scaling_arrangement("test.sa", scaling_posture=posture)
        assert sa.has_valid_posture()


def test_scaling_arrangement_no_artificial_ceiling() -> None:
    sa = make_scaling_arrangement("test.sa", scaling_posture="unbounded")
    assert not sa.has_artificial_ceiling()

    sa2 = make_scaling_arrangement("test.sa", scaling_posture="elastic")
    assert not sa2.has_artificial_ceiling()

    sa3 = make_scaling_arrangement("test.sa", scaling_posture="fixed")
    assert not sa3.has_artificial_ceiling()


def test_scaling_arrangement_to_dict() -> None:
    sa = make_scaling_arrangement(
        "test.scaling",
        scaling_posture="elastic",
        scales=("ENG-005:Resource:compute-1",),
        scaling_metrics=("cpu-util", "request-rate"),
    )
    d = sa.to_dict()
    assert d["meta_class"] == "ScalingArrangement"
    assert d["scaling_posture"] == "elastic"
    assert "scales" in d
    assert "scaling_metrics" in d


# ===========================================================================
# Cross-construct / lifecycle
# ===========================================================================


def test_forward_lifecycle_transition() -> None:
    at = make_availability_topology("test.at")
    assert at.state == InfrastructureState.DEFINED
    at2 = at.transition(InfrastructureState.PROVISIONED)
    assert at2.state == InfrastructureState.PROVISIONED
    # original unchanged (frozen)
    assert at.state == InfrastructureState.DEFINED


def test_lifecycle_rejects_backward_transition() -> None:
    sa = make_scaling_arrangement("test.sa", state=InfrastructureState.ACTIVE)
    with pytest.raises(InfrastructureError):
        sa.transition(InfrastructureState.DEFINED)


def test_lifecycle_rejects_non_state() -> None:
    at = make_availability_topology("test.at")
    with pytest.raises(InfrastructureError):
        at.transition("ACTIVE")  # type: ignore[arg-type]


def test_all_constructs_technology_neutral() -> None:
    constructs = [
        make_availability_topology("test.at"),
        make_scaling_arrangement("test.sa"),
    ]
    for c in constructs:
        assert not c.selects_technology(), f"{c.meta_class} selects technology"
        assert not c.embeds_secret(), f"{c.meta_class} embeds secret"
        assert not c.confers_authority(), f"{c.meta_class} confers authority"
        assert not c.redefines_foundation(), f"{c.meta_class} redefines foundation"
        assert not c.is_new_primitive(), f"{c.meta_class} is new primitive"
        assert not c.projects_completion(), f"{c.meta_class} projects completion"


def test_all_constructs_evaluative_non_enforcing() -> None:
    constructs = [
        make_availability_topology("test.at"),
        make_scaling_arrangement("test.sa"),
    ]
    for c in constructs:
        assert c.is_evaluative_facet(), f"{c.meta_class} is not evaluative"
        assert not c.enacts_enforcement(), f"{c.meta_class} enacts enforcement"


def test_is_founding_acyclic_reports_false_when_the_core_is_not_canonicalisable() -> None:
    """The except-arm is the answer to a broken core, and it must answer False, not raise.

    A construct whose canonical_core cannot be serialised is not acyclic and not an
    exception — the boolean is what the certification roll-up consumes, and a raise there
    would replace one failure mode with another.
    """

    class _Broken(AvailabilityTopology):
        def canonical_core(self):
            return {"poison": object()}

    assert (
        _Broken(
            type_tag="RES-BROKEN-01",
            resilience_posture="redundant",
            sustains=(DEFAULT_CLUSTER_REF,),
        ).is_founding_acyclic()
        is False
    )


def test_the_base_construct_answers_posture_and_newness_before_any_override() -> None:
    """Every honest arm of the base: an un-overridden construct says NO.

    has_valid_posture and is_new_primitive default to False on the base — the value a future
    construct inherits until it declares otherwise — and a default nobody executes is a
    default nobody has shown to fire.
    """

    assert _InfraConstruct.__dict__["has_valid_posture"].__doc__ is not None
    bare = _InfraConstruct()
    assert bare.has_valid_posture() is False
    assert bare.is_new_primitive() is False


def test_the_resilience_guards_refuse_a_malformed_type_tag_posture_and_state() -> None:
    """The three private guards, each on its refusal side — guards only count both ways.

    _require_typed, _require_posture and _require_state protect invariants §3/WF-9/WF-10;
    a guard with no measured raise is a guard that only reports agreement.
    """

    with pytest.raises(Exception, match="ENG-004 type_tag"):
        _require_typed(None, "availability topology")
    with pytest.raises(Exception, match="non-empty posture"):
        _require_posture("   ", "AvailabilityTopology")
    with pytest.raises(Exception, match="not in admitted set"):
        _require_posture("floating", "AvailabilityTopology")
    with pytest.raises(Exception, match="InfrastructureState"):
        _require_state("DEFINED", "scaling arrangement")
    assert _require_state(InfrastructureState.ACTIVE, "scaling arrangement") is None
