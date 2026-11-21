"""EC3-B12-U02 — Capability construct tests (AMC-02 + AMK-01/03/05/06/07 + UAL-03/04/05/06/09/10/12/13)."""

from __future__ import annotations

import pytest

from application.capability import Capability, CapabilityError, make_capability
from application.capability_meta import (
    CAPABILITY_META_CLASS,
    CAPABILITY_RELATIONSHIPS,
    CapabilityKind,
    CapabilityState,
)

OP_REF = "ENG-005:SF-2:ucos.demo.operation"


def test_capability_is_typed_identified_and_operation_consuming():
    c = make_capability("ucos.demo.capability", OP_REF)
    assert c.meta_class == CAPABILITY_META_CLASS  # V1 (AMC-02)
    assert c.type_tag == "ucos.demo.capability"  # UAL-03 typed
    assert c.capability_id.startswith("UCOS-CAPABILITY-")  # UAL-04 identified (ENG-001)
    assert len(c.value_digest) == 64  # ENG-003 value fidelity
    assert c.kind is CapabilityKind.FUNCTIONAL  # AXH-02 classified
    assert c.operation_ref == OP_REF  # AMR-13 consumes-operation (by reference)


def test_capability_identity_is_deterministic_and_core_derived():
    a = make_capability("t", OP_REF)
    b = make_capability("t", OP_REF)
    c = make_capability("t", "ENG-005:SF-2:other")
    assert a.capability_id == b.capability_id  # same core → same ENG-001 identity
    assert a.capability_id != c.capability_id  # different operation → different identity


def test_capability_is_immutable_objecthood():
    c = make_capability("t", OP_REF)
    with pytest.raises((AttributeError, TypeError)):
        c.type_tag = "other"  # frozen object (ENG-002 objecthood)


def test_untyped_capability_is_rejected_fail_closed():
    with pytest.raises(CapabilityError):
        make_capability("", OP_REF)  # UAL-03 — no untyped capability may exist
    with pytest.raises(CapabilityError):
        make_capability("   ", OP_REF)


def test_non_string_type_tag_is_rejected():
    with pytest.raises(CapabilityError):
        Capability(type_tag=object(), kind=CapabilityKind.FUNCTIONAL, operation_ref=OP_REF)  # type: ignore[arg-type]


def test_bad_kind_is_rejected_fail_closed():
    with pytest.raises(CapabilityError):
        Capability(type_tag="t", kind="not-a-kind", operation_ref=OP_REF)  # type: ignore[arg-type]


def test_missing_operation_reference_is_rejected():
    with pytest.raises(CapabilityError):
        make_capability("t", "")  # AMR-13 / CAP-05 — a capability must consume an operation
    with pytest.raises(CapabilityError):
        make_capability("t", "   ")


def test_missing_data_behavior_or_composition_reference_is_rejected():
    with pytest.raises(CapabilityError):
        make_capability("t", OP_REF, data_ref="")  # AMR-14 / UAL-13
    with pytest.raises(CapabilityError):
        make_capability("t", OP_REF, behavior_ref="")  # AMR-11 / UAL-10
    with pytest.raises(CapabilityError):
        make_capability("t", OP_REF, composition_ref="")  # AMR-12 / UAL-09


def test_non_string_operation_reference_is_rejected():
    with pytest.raises(CapabilityError):
        Capability(type_tag="t", kind=CapabilityKind.FUNCTIONAL, operation_ref=object())  # type: ignore[arg-type]


def test_bad_state_is_rejected_fail_closed():
    with pytest.raises(CapabilityError):
        Capability(
            type_tag="t",
            kind=CapabilityKind.FUNCTIONAL,
            operation_ref=OP_REF,
            state="BAD",  # type: ignore[arg-type]
        )


def test_relationships_are_within_amr_closure():
    c = make_capability("t", OP_REF)
    assert set(c.meta_relationships()) <= set(f"AMR-{n:02d}" for n in range(1, 15))  # V2
    assert c.meta_relationships() == ("AMR-01", "AMR-10", "AMR-11", "AMR-12", "AMR-13", "AMR-14")
    assert c.meta_relationships() == CAPABILITY_RELATIONSHIPS


def test_lifecycle_is_forward_only():
    c = make_capability("t", OP_REF, state=CapabilityState.DEFINED)
    composed = c.transition(CapabilityState.COMPOSED)
    assert composed.state is CapabilityState.COMPOSED
    ctx = composed.transition(CapabilityState.CONTEXTUALIZED)
    assert ctx.state is CapabilityState.CONTEXTUALIZED
    executable = ctx.transition(CapabilityState.EXECUTABLE)
    assert executable.state is CapabilityState.EXECUTABLE
    with pytest.raises(CapabilityError):
        executable.transition(CapabilityState.DEFINED)  # UAL-12 — no backward transition


def test_transition_to_same_state_is_allowed():
    c = make_capability("t", OP_REF, state=CapabilityState.COMPOSED)
    same = c.transition(CapabilityState.COMPOSED)  # not backward (forward-or-equal)
    assert same.state is CapabilityState.COMPOSED


def test_transition_rejects_non_state_target():
    c = make_capability("t", OP_REF)
    with pytest.raises(CapabilityError):
        c.transition("EXECUTABLE")  # type: ignore[arg-type]


def test_all_capability_kinds_construct_and_have_delivery_side():
    expected = {
        CapabilityKind.FUNCTIONAL: "functional",
        CapabilityKind.INFORMATIONAL: "read-side",
        CapabilityKind.TRANSACTIONAL: "write-side",
    }
    for kind, side in expected.items():
        c = make_capability("t", OP_REF, kind=kind)
        assert c.kind is kind
        assert c.delivery_side() == side  # CAP-C5


def test_references_resolve_and_founding_acyclic():
    c = make_capability("t", OP_REF)
    assert c.references_resolve() is True  # AOI-03 / AMK-05/06/07
    assert c.is_founding_acyclic() is True  # V4 / AMK-03 / CAP-C3


def test_consumes_operation_and_is_bounded():
    c = make_capability("t", OP_REF)
    assert c.consumes_operation() is True  # CAP-05 / AMR-13
    assert c.is_bounded() is True  # CAP-06 / CAP-C1 / UAL-08


def test_non_constitutive_and_no_secret_no_technology():
    c = make_capability("t", OP_REF)
    assert c.confers_authority() is False  # UAL-15 / CAP-09 / C7
    assert c.redefines_foundation() is False  # UAL-02 / AMI-05
    assert c.selects_technology() is False  # UAL-15 (abstract references only)
    assert c.embeds_secret() is False


def test_technology_bearing_capability_is_detected():
    techy = make_capability("t", "ENG-005:SF-2:kafka.stream")
    assert techy.selects_technology() is True  # UAL-15 — concrete technology named


def test_secret_bearing_capability_is_detected():
    leaky = make_capability("t", "ENG-005:SF-2:password-reset")
    assert leaky.embeds_secret() is True  # UAL-15 / RR-07


def test_capability_to_dict_records_substrate_reuse():
    c = make_capability("t", OP_REF)
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
        "DF-2",
    ]
    assert payload["meta_class"] == "AMC-02"
    assert payload["kind"] == "Functional-Capability"
    assert payload["operation_ref"] == OP_REF
    assert payload["delivery_side"] == "functional"
    assert payload["state"] == "DEFINED"


def test_canonical_core_excludes_state_and_id():
    c = make_capability("t", OP_REF)
    core = c.canonical_core()
    assert "state" not in core  # lifecycle is not identity-defining
    assert "capability_id" not in core
    assert core["meta_class"] == "AMC-02"


def test_state_does_not_change_identity():
    a = make_capability("t", OP_REF, state=CapabilityState.DEFINED)
    b = make_capability("t", OP_REF, state=CapabilityState.EXECUTABLE)
    assert a.capability_id == b.capability_id  # identity is core-derived, not state


def test_capability_type_is_the_realized_construct():
    assert isinstance(make_capability("t", OP_REF), Capability)
