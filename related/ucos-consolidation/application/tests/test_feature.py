"""EC3-B12-U04 — Feature construct tests (AMC-04 + AMK-01/02/03/04/05/07 + UAL-03…13)."""

from __future__ import annotations

import pytest

from application.feature import Feature, FeatureError, make_feature
from application.feature_meta import (
    FEATURE_META_CLASS,
    FEATURE_RELATIONSHIPS,
    FeatureKind,
    FeatureState,
)

CAP = "ENG-005:AMC-02:ucos.demo.capability"
OPS = (
    "ENG-005:SF-2:ucos.demo.operation.a",
    "ENG-005:SF-2:ucos.demo.operation.b",
)
ONE_OP = ("ENG-005:SF-2:ucos.demo.operation.a",)


def test_feature_is_typed_identified_and_delivers_by_operation_consumption():
    f = make_feature("ucos.demo.feature", CAP, ONE_OP)
    assert f.meta_class == FEATURE_META_CLASS  # V1 (AMC-04)
    assert f.type_tag == "ucos.demo.feature"  # UAL-03 typed
    assert f.feature_id.startswith("UCOS-FEATURE-")  # UAL-04 identified (ENG-001)
    assert len(f.value_digest) == 64  # ENG-003 value fidelity
    assert f.kind is FeatureKind.QUERY  # AXH-04 classified
    assert f.delivers_capability() is True  # AMR-01 / FEA-04
    assert f.consumes_operations() is True  # AMR-13 / FEA-04 (the defining relationship)
    assert f.presents_data() is True  # AMR-14 / FEA-05
    assert f.is_engaged() is True  # AMR-05 / FEA-06 (the NEW relationship)
    assert f.is_owned() is True  # AMR-03 / FEA-07
    assert f.composed_operation_count() == 1


def test_feature_identity_is_deterministic_and_core_derived():
    a = make_feature("t", CAP, OPS)
    b = make_feature("t", CAP, OPS)
    c = make_feature("t", CAP, ONE_OP)
    assert a.feature_id == b.feature_id  # same core → same ENG-001 identity
    assert a.feature_id != c.feature_id  # different composed operations → different identity


def test_composed_operations_are_order_independent_for_identity():
    a = make_feature("t", CAP, ("ENG-005:SF-2:x", "ENG-005:SF-2:y"), kind=FeatureKind.COMPOSITE)
    b = make_feature("t", CAP, ("ENG-005:SF-2:y", "ENG-005:SF-2:x"), kind=FeatureKind.COMPOSITE)
    assert a.feature_id == b.feature_id  # operations are a set (partition); order-independent


def test_feature_is_immutable_objecthood():
    f = make_feature("t", CAP, ONE_OP)
    with pytest.raises((AttributeError, TypeError)):
        f.type_tag = "other"  # frozen object (ENG-002 objecthood)


def test_untyped_feature_is_rejected_fail_closed():
    with pytest.raises(FeatureError):
        make_feature("", CAP, ONE_OP)  # UAL-03 — no untyped feature may exist
    with pytest.raises(FeatureError):
        make_feature("   ", CAP, ONE_OP)


def test_non_string_type_tag_is_rejected():
    with pytest.raises(FeatureError):
        Feature(  # type: ignore[arg-type]
            type_tag=object(), kind=FeatureKind.QUERY, capability_ref=CAP, operation_refs=ONE_OP
        )


def test_bad_kind_is_rejected_fail_closed():
    with pytest.raises(FeatureError):
        Feature(  # type: ignore[arg-type]
            type_tag="t", kind="not-a-kind", capability_ref=CAP, operation_refs=ONE_OP
        )


def test_missing_capability_reference_is_rejected():
    with pytest.raises(FeatureError):
        make_feature("t", "", ONE_OP)  # AMR-01 / FEA-04 — must deliver a capability


def test_feature_without_operation_is_rejected():
    with pytest.raises(FeatureError):
        make_feature("t", CAP, ())  # AMR-13 / FEA-04 — must compose ≥1 SF-2 operation


def test_non_tuple_operation_refs_is_rejected():
    with pytest.raises(FeatureError):
        Feature(  # type: ignore[arg-type]
            type_tag="t", kind=FeatureKind.QUERY, capability_ref=CAP, operation_refs=["a"]
        )


def test_empty_operation_reference_is_rejected():
    with pytest.raises(FeatureError):
        make_feature("t", CAP, ("ENG-005:SF-2:a", ""))  # AMR-13 — each op ref non-empty
    with pytest.raises(FeatureError):
        make_feature("t", CAP, ("   ",))


def test_duplicate_operation_is_rejected_partition():
    with pytest.raises(FeatureError):
        make_feature("t", CAP, ("ENG-005:SF-2:a", "ENG-005:SF-2:a"))  # FEA-C1 partition


def test_composite_feature_requires_two_or_more_operations():
    with pytest.raises(FeatureError):
        make_feature("t", CAP, ONE_OP, kind=FeatureKind.COMPOSITE)  # AXH-04 / FEA-C5
    f = make_feature("t", CAP, OPS, kind=FeatureKind.COMPOSITE)  # ≥2 → ok
    assert f.composed_operation_count() == 2


def test_query_and_command_features_accept_single_operation():
    q = make_feature("t", CAP, ONE_OP, kind=FeatureKind.QUERY)
    c = make_feature("t", CAP, ONE_OP, kind=FeatureKind.COMMAND)
    assert q.delivery_side() == "read-side"  # FEA-C5
    assert c.delivery_side() == "write-side"  # FEA-C5


def test_missing_interaction_module_data_or_behavior_reference_is_rejected():
    with pytest.raises(FeatureError):
        make_feature("t", CAP, ONE_OP, interaction_ref="")  # AMR-05 / FEA-06
    with pytest.raises(FeatureError):
        make_feature("t", CAP, ONE_OP, module_ref="")  # AMR-03 / FEA-07
    with pytest.raises(FeatureError):
        make_feature("t", CAP, ONE_OP, data_ref="")  # AMR-14 / FEA-05
    with pytest.raises(FeatureError):
        make_feature("t", CAP, ONE_OP, behavior_ref="")  # §7 / UAL-10


def test_feature_cannot_compose_its_module_or_interaction_as_operation():
    mod = "ENG-005:AMC-03:ucos.mod"
    with pytest.raises(FeatureError):
        make_feature("t", CAP, (mod,), module_ref=mod)  # FEA-C3 acyclic guard
    inter = "ENG-005:AMC-06:ucos.inter"
    with pytest.raises(FeatureError):
        make_feature("t", CAP, (inter,), interaction_ref=inter)  # FEA-C3 acyclic guard


def test_feature_cannot_compose_its_delivered_capability_as_operation():
    with pytest.raises(FeatureError):
        make_feature("t", CAP, (CAP,))  # FEA-C3 / non-absorption


def test_bad_state_is_rejected_fail_closed():
    with pytest.raises(FeatureError):
        Feature(
            type_tag="t",
            kind=FeatureKind.QUERY,
            capability_ref=CAP,
            operation_refs=ONE_OP,
            state="BAD",  # type: ignore[arg-type]
        )


def test_relationships_are_within_amr_closure():
    f = make_feature("t", CAP, ONE_OP)
    assert set(f.meta_relationships()) <= set(f"AMR-{n:02d}" for n in range(1, 15))  # V2
    assert f.meta_relationships() == (
        "AMR-01",
        "AMR-03",
        "AMR-05",
        "AMR-10",
        "AMR-11",
        "AMR-13",
        "AMR-14",
    )
    assert f.meta_relationships() == FEATURE_RELATIONSHIPS


def test_feature_uses_engaged_through_but_not_composed_of_or_composed_as():
    # The distinctive AMC-04 relationship set: uses AMR-05 (engaged-through, NEW) and does
    # NOT use AMR-02 (composed-of) or AMR-12 (composed-as) that U01/U03 used.
    rels = set(make_feature("t", CAP, ONE_OP).meta_relationships())
    assert "AMR-05" in rels
    assert "AMR-02" not in rels
    assert "AMR-12" not in rels
    assert "AMR-07" not in rels


def test_lifecycle_is_forward_only():
    f = make_feature("t", CAP, ONE_OP, state=FeatureState.DEFINED)
    composed = f.transition(FeatureState.COMPOSED)
    assert composed.state is FeatureState.COMPOSED
    ctx = composed.transition(FeatureState.CONTEXTUALIZED)
    assert ctx.state is FeatureState.CONTEXTUALIZED
    executable = ctx.transition(FeatureState.EXECUTABLE)
    assert executable.state is FeatureState.EXECUTABLE
    with pytest.raises(FeatureError):
        executable.transition(FeatureState.DEFINED)  # UAL-12 — no backward transition


def test_transition_to_same_state_is_allowed():
    f = make_feature("t", CAP, ONE_OP, state=FeatureState.COMPOSED)
    same = f.transition(FeatureState.COMPOSED)  # not backward (forward-or-equal)
    assert same.state is FeatureState.COMPOSED


def test_transition_rejects_non_state_target():
    f = make_feature("t", CAP, ONE_OP)
    with pytest.raises(FeatureError):
        f.transition("EXECUTABLE")  # type: ignore[arg-type]


def test_all_feature_kinds_construct():
    assert make_feature("t", CAP, ONE_OP, kind=FeatureKind.QUERY).kind is FeatureKind.QUERY
    assert make_feature("t", CAP, ONE_OP, kind=FeatureKind.COMMAND).kind is FeatureKind.COMMAND
    assert make_feature("t", CAP, OPS, kind=FeatureKind.COMPOSITE).kind is FeatureKind.COMPOSITE


def test_references_resolve_and_founding_acyclic():
    f = make_feature("t", CAP, ONE_OP)
    assert f.references_resolve() is True  # AOI-03 / AMK-05/07
    assert f.is_founding_acyclic() is True  # V4 / AMK-03 / FEA-C3


def test_declaration_complete_and_delivery_side_consistent():
    f = make_feature("t", CAP, ONE_OP)
    assert f.declaration_complete() is True  # FEA-C1 / AMK-02 / UAL-08
    assert f.delivery_side_is_consistent() is True  # FEA-C5 / AXH-04
    assert f.operations_are_partition() is True  # FEA-C1
    assert f.owns_operation(ONE_OP[0]) is True  # AMR-13
    assert f.owns_operation("ENG-005:SF-2:not-composed") is False


def test_engaged_before_executable_gate():
    defined = make_feature("t", CAP, ONE_OP, state=FeatureState.DEFINED)
    assert defined.engaged_before_executable() is True  # engaged (interaction present)
    executable = defined.transition(FeatureState.COMPOSED).transition(
        FeatureState.CONTEXTUALIZED
    ).transition(FeatureState.EXECUTABLE)
    assert executable.engaged_before_executable() is True  # AMK-04 holds (engaged)


def test_non_constitutive_and_no_secret_no_technology():
    f = make_feature("t", CAP, ONE_OP)
    assert f.confers_authority() is False  # UAL-15 / FEA-09 / C7
    assert f.redefines_foundation() is False  # UAL-02 / AMI-05
    assert f.selects_technology() is False  # UAL-15 (abstract references only)
    assert f.embeds_secret() is False


def test_technology_bearing_feature_is_detected():
    techy = make_feature("t", CAP, ("ENG-005:SF-2:kafka.consumer",))
    assert techy.selects_technology() is True  # UAL-15 — concrete technology named


def test_secret_bearing_feature_is_detected():
    leaky = make_feature("t", CAP, ("ENG-005:SF-2:password-reset",))
    assert leaky.embeds_secret() is True  # UAL-15 / RR-07


def test_feature_to_dict_records_substrate_reuse():
    f = make_feature("t", CAP, OPS, kind=FeatureKind.COMPOSITE)
    payload = f.to_dict()
    assert payload["substrate_refs"] == [
        "ENG-001",
        "ENG-002",
        "ENG-003",
        "ENG-004",
        "ENG-005",
        "RL-F2",
        "SF-2",
        "DF-2",
    ]
    assert payload["meta_class"] == "AMC-04"
    assert payload["kind"] == "Composite-Feature"
    assert payload["composed_operation_count"] == 2
    assert payload["declaration_complete"] is True
    assert payload["engaged"] is True
    assert payload["delivery_side"] == "composite"
    assert payload["state"] == "DEFINED"
    # operation_refs are canonically sorted in the projection
    assert payload["operation_refs"] == sorted(OPS)


def test_canonical_core_excludes_state_and_id():
    f = make_feature("t", CAP, ONE_OP)
    core = f.canonical_core()
    assert "state" not in core  # lifecycle is not identity-defining
    assert "feature_id" not in core
    assert core["meta_class"] == "AMC-04"
    assert core["operation_refs"] == sorted(ONE_OP)


def test_state_does_not_change_identity():
    a = make_feature("t", CAP, ONE_OP, state=FeatureState.DEFINED)
    b = make_feature("t", CAP, ONE_OP, state=FeatureState.COMPOSED)
    assert a.feature_id == b.feature_id  # identity is core-derived, not state


def test_feature_type_is_the_realized_construct():
    assert isinstance(make_feature("t", CAP, ONE_OP), Feature)
