"""EC3-B12-U03 — Module construct tests (AMC-03 + AMK-01/03/05/06 + UAL-03/04/05/07/09/10/12)."""

from __future__ import annotations

import pytest

from application.module import Module, ModuleError, make_module
from application.module_meta import (
    MODULE_META_CLASS,
    MODULE_RELATIONSHIPS,
    ModuleKind,
    ModuleState,
)

FEATS = (
    "ENG-005:AMC-04:ucos.demo.feature.a",
    "ENG-005:AMC-04:ucos.demo.feature.b",
)


def test_module_is_typed_identified_and_feature_grouping():
    m = make_module("ucos.demo.module", FEATS)
    assert m.meta_class == MODULE_META_CLASS  # V1 (AMC-03)
    assert m.type_tag == "ucos.demo.module"  # UAL-03 typed
    assert m.module_id.startswith("UCOS-MODULE-")  # UAL-04 identified (ENG-001)
    assert len(m.value_digest) == 64  # ENG-003 value fidelity
    assert m.kind is ModuleKind.CORE  # AXH-03 classified
    assert m.groups_features() is True  # AMR-03 groups (by reference)
    assert m.owned_feature_count() == 2


def test_module_identity_is_deterministic_and_core_derived():
    a = make_module("t", FEATS)
    b = make_module("t", FEATS)
    c = make_module("t", ("ENG-005:AMC-04:other",))
    assert a.module_id == b.module_id  # same core → same ENG-001 identity
    assert a.module_id != c.module_id  # different owned features → different identity


def test_feature_ownership_is_order_independent_for_identity():
    a = make_module("t", ("ENG-005:AMC-04:x", "ENG-005:AMC-04:y"))
    b = make_module("t", ("ENG-005:AMC-04:y", "ENG-005:AMC-04:x"))
    assert a.module_id == b.module_id  # ownership is a set (partition); order-independent


def test_module_is_immutable_objecthood():
    m = make_module("t", FEATS)
    with pytest.raises((AttributeError, TypeError)):
        m.type_tag = "other"  # frozen object (ENG-002 objecthood)


def test_untyped_module_is_rejected_fail_closed():
    with pytest.raises(ModuleError):
        make_module("", FEATS)  # UAL-03 — no untyped module may exist
    with pytest.raises(ModuleError):
        make_module("   ", FEATS)


def test_non_string_type_tag_is_rejected():
    with pytest.raises(ModuleError):
        Module(type_tag=object(), kind=ModuleKind.CORE, feature_refs=FEATS)  # type: ignore[arg-type]


def test_bad_kind_is_rejected_fail_closed():
    with pytest.raises(ModuleError):
        Module(type_tag="t", kind="not-a-kind", feature_refs=FEATS)  # type: ignore[arg-type]


def test_module_without_features_is_rejected():
    with pytest.raises(ModuleError):
        make_module("t", ())  # AMR-03 / MOD-07 — a module must group ≥1 feature


def test_non_tuple_feature_refs_is_rejected():
    with pytest.raises(ModuleError):
        Module(type_tag="t", kind=ModuleKind.CORE, feature_refs=["a"])  # type: ignore[arg-type]


def test_empty_feature_reference_is_rejected():
    with pytest.raises(ModuleError):
        make_module("t", ("ENG-005:AMC-04:a", ""))  # AMR-03 — each feature ref non-empty
    with pytest.raises(ModuleError):
        make_module("t", ("   ",))


def test_duplicate_feature_ownership_is_rejected_partition():
    with pytest.raises(ModuleError):
        make_module("t", ("ENG-005:AMC-04:a", "ENG-005:AMC-04:a"))  # MOD-05 / MOD-C2 partition


def test_missing_application_composition_or_behavior_reference_is_rejected():
    with pytest.raises(ModuleError):
        make_module("t", FEATS, application_ref="")  # AMR-02 / MOD-06
    with pytest.raises(ModuleError):
        make_module("t", FEATS, composition_ref="")  # AMR-12 / UAL-09
    with pytest.raises(ModuleError):
        make_module("t", FEATS, behavior_ref="")  # §7 / UAL-10


def test_module_cannot_group_its_composing_application():
    app = "ENG-005:AMC-01:ucos.app"
    with pytest.raises(ModuleError):
        make_module("t", (app,), application_ref=app)  # MOD-C3 / MOD-C4 acyclic guard


def test_bad_state_is_rejected_fail_closed():
    with pytest.raises(ModuleError):
        Module(
            type_tag="t",
            kind=ModuleKind.CORE,
            feature_refs=FEATS,
            state="BAD",  # type: ignore[arg-type]
        )


def test_relationships_are_within_amr_closure():
    m = make_module("t", FEATS)
    assert set(m.meta_relationships()) <= set(f"AMR-{n:02d}" for n in range(1, 15))  # V2
    assert m.meta_relationships() == ("AMR-02", "AMR-03", "AMR-07", "AMR-10", "AMR-12")
    assert m.meta_relationships() == MODULE_RELATIONSHIPS


def test_lifecycle_is_forward_only():
    m = make_module("t", FEATS, state=ModuleState.DEFINED)
    composed = m.transition(ModuleState.COMPOSED)
    assert composed.state is ModuleState.COMPOSED
    ctx = composed.transition(ModuleState.CONTEXTUALIZED)
    assert ctx.state is ModuleState.CONTEXTUALIZED
    executable = ctx.transition(ModuleState.EXECUTABLE)
    assert executable.state is ModuleState.EXECUTABLE
    with pytest.raises(ModuleError):
        executable.transition(ModuleState.DEFINED)  # UAL-12 — no backward transition


def test_transition_to_same_state_is_allowed():
    m = make_module("t", FEATS, state=ModuleState.COMPOSED)
    same = m.transition(ModuleState.COMPOSED)  # not backward (forward-or-equal)
    assert same.state is ModuleState.COMPOSED


def test_transition_rejects_non_state_target():
    m = make_module("t", FEATS)
    with pytest.raises(ModuleError):
        m.transition("EXECUTABLE")  # type: ignore[arg-type]


def test_all_module_kinds_construct():
    for kind in (ModuleKind.CORE, ModuleKind.SUPPORTING, ModuleKind.EXTENSION):
        m = make_module("t", FEATS, kind=kind)
        assert m.kind is kind


def test_references_resolve_and_founding_acyclic():
    m = make_module("t", FEATS)
    assert m.references_resolve() is True  # AOI-03 / AMK-05/06
    assert m.is_founding_acyclic() is True  # V4 / AMK-03 / MOD-C3


def test_bounded_cohesive_partition_and_ownership():
    m = make_module("t", FEATS)
    assert m.is_bounded() is True  # MOD-03 / MOD-C1 / UAL-07
    assert m.is_cohesive() is True  # MOD-04 / UAL-07
    assert m.ownership_is_partition() is True  # MOD-05 / MOD-C2
    assert m.owns_feature(FEATS[0]) is True  # MOD-07
    assert m.owns_feature("ENG-005:AMC-04:not-owned") is False


def test_non_constitutive_and_no_secret_no_technology():
    m = make_module("t", FEATS)
    assert m.confers_authority() is False  # UAL-15 / MOD-09 / C7
    assert m.redefines_foundation() is False  # UAL-02 / AMI-05
    assert m.selects_technology() is False  # UAL-15 (abstract references only)
    assert m.embeds_secret() is False


def test_technology_bearing_module_is_detected():
    techy = make_module("t", ("ENG-005:AMC-04:kafka.consumer",))
    assert techy.selects_technology() is True  # UAL-15 — concrete technology named


def test_secret_bearing_module_is_detected():
    leaky = make_module("t", ("ENG-005:AMC-04:password-reset",))
    assert leaky.embeds_secret() is True  # UAL-15 / RR-07


def test_module_to_dict_records_substrate_reuse():
    m = make_module("t", FEATS)
    payload = m.to_dict()
    assert payload["substrate_refs"] == [
        "ENG-001",
        "ENG-002",
        "ENG-003",
        "ENG-004",
        "ENG-005",
        "RL-F2",
        "PL-F2",
    ]
    assert payload["meta_class"] == "AMC-03"
    assert payload["kind"] == "Core-Module"
    assert payload["owned_feature_count"] == 2
    assert payload["bounded"] is True
    assert payload["cohesive"] is True
    assert payload["state"] == "DEFINED"
    # feature_refs are canonically sorted in the projection
    assert payload["feature_refs"] == sorted(FEATS)


def test_canonical_core_excludes_state_and_id():
    m = make_module("t", FEATS)
    core = m.canonical_core()
    assert "state" not in core  # lifecycle is not identity-defining
    assert "module_id" not in core
    assert core["meta_class"] == "AMC-03"
    assert core["feature_refs"] == sorted(FEATS)


def test_state_does_not_change_identity():
    a = make_module("t", FEATS, state=ModuleState.DEFINED)
    b = make_module("t", FEATS, state=ModuleState.EXECUTABLE)
    assert a.module_id == b.module_id  # identity is core-derived, not state


def test_module_type_is_the_realized_construct():
    assert isinstance(make_module("t", FEATS), Module)
