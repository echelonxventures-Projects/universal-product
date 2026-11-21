"""EC3-B12-U01 — Application construct tests (AMC-01 + AMK-01/03/05/06 + UAL-03/04/05/09/10/12)."""

from __future__ import annotations

import pytest

from application.application import Application, ApplicationError, make_application
from application.application_meta import (
    APPLICATION_META_CLASS,
    APPLICATION_RELATIONSHIPS,
    ApplicationKind,
    ApplicationState,
)

CAP_REF = "ENG-005:CAPABILITY:ucos.demo.capability"


def test_application_is_typed_identified_and_capability_delivering():
    a = make_application("ucos.demo.application", CAP_REF)
    assert a.meta_class == APPLICATION_META_CLASS  # V1 (AMC-01)
    assert a.type_tag == "ucos.demo.application"  # UAL-03 typed
    assert a.application_id.startswith("UCOS-APPLICATION-")  # UAL-04 identified (ENG-001)
    assert len(a.value_digest) == 64  # ENG-003 value fidelity
    assert a.kind is ApplicationKind.SINGLE_MODULE  # AXH-01 classified
    assert a.capability_ref == CAP_REF  # AMR-01 delivers (by reference)


def test_application_identity_is_deterministic_and_core_derived():
    a = make_application("t", CAP_REF)
    b = make_application("t", CAP_REF)
    c = make_application("t", "ENG-005:CAPABILITY:other")
    assert a.application_id == b.application_id  # same core → same ENG-001 identity
    assert a.application_id != c.application_id  # different capability → different identity


def test_application_is_immutable_objecthood():
    a = make_application("t", CAP_REF)
    with pytest.raises((AttributeError, TypeError)):
        a.type_tag = "other"  # frozen object (ENG-002 objecthood)


def test_untyped_application_is_rejected_fail_closed():
    with pytest.raises(ApplicationError):
        make_application("", CAP_REF)  # UAL-03 — no untyped application may exist
    with pytest.raises(ApplicationError):
        make_application("   ", CAP_REF)


def test_non_string_type_tag_is_rejected():
    with pytest.raises(ApplicationError):
        Application(type_tag=object(), kind=ApplicationKind.SINGLE_MODULE, capability_ref=CAP_REF)  # type: ignore[arg-type]


def test_bad_kind_is_rejected_fail_closed():
    with pytest.raises(ApplicationError):
        Application(type_tag="t", kind="not-a-kind", capability_ref=CAP_REF)  # type: ignore[arg-type]


def test_missing_capability_reference_is_rejected():
    with pytest.raises(ApplicationError):
        make_application("t", "")  # AMR-01 — an application must deliver a capability
    with pytest.raises(ApplicationError):
        make_application("t", "   ")


def test_missing_behavior_or_composition_reference_is_rejected():
    with pytest.raises(ApplicationError):
        make_application("t", CAP_REF, behavior_ref="")  # AMR-11 / UAL-10
    with pytest.raises(ApplicationError):
        make_application("t", CAP_REF, composition_ref="")  # AMR-12 / UAL-09


def test_non_string_capability_reference_is_rejected():
    with pytest.raises(ApplicationError):
        Application(type_tag="t", kind=ApplicationKind.SINGLE_MODULE, capability_ref=object())  # type: ignore[arg-type]


def test_bad_state_is_rejected_fail_closed():
    with pytest.raises(ApplicationError):
        Application(
            type_tag="t",
            kind=ApplicationKind.SINGLE_MODULE,
            capability_ref=CAP_REF,
            state="BAD",  # type: ignore[arg-type]
        )


def test_relationships_are_within_amr_closure():
    a = make_application("t", CAP_REF)
    assert set(a.meta_relationships()) <= set(APPLICATION_RELATIONSHIPS)  # V2
    assert a.meta_relationships() == ("AMR-01", "AMR-10", "AMR-11", "AMR-12")


def test_lifecycle_is_forward_only():
    a = make_application("t", CAP_REF, state=ApplicationState.DEFINED)
    composed = a.transition(ApplicationState.COMPOSED)
    assert composed.state is ApplicationState.COMPOSED
    ctx = composed.transition(ApplicationState.CONTEXTUALIZED)
    assert ctx.state is ApplicationState.CONTEXTUALIZED
    executable = ctx.transition(ApplicationState.EXECUTABLE)
    assert executable.state is ApplicationState.EXECUTABLE
    with pytest.raises(ApplicationError):
        executable.transition(ApplicationState.DEFINED)  # UAL-12 — no backward transition


def test_transition_to_same_state_is_allowed():
    a = make_application("t", CAP_REF, state=ApplicationState.COMPOSED)
    same = a.transition(ApplicationState.COMPOSED)  # not backward (forward-or-equal)
    assert same.state is ApplicationState.COMPOSED


def test_transition_rejects_non_state_target():
    a = make_application("t", CAP_REF)
    with pytest.raises(ApplicationError):
        a.transition("EXECUTABLE")  # type: ignore[arg-type]


def test_all_application_kinds_construct():
    for kind in ApplicationKind:
        a = make_application("t", CAP_REF, kind=kind)
        assert a.kind is kind


def test_references_resolve_and_founding_acyclic():
    a = make_application("t", CAP_REF)
    assert a.references_resolve() is True  # AOI-03 / AMK-05/06
    assert a.is_founding_acyclic() is True  # V4 / AMK-03


def test_non_constitutive_and_no_secret_no_technology():
    a = make_application("t", CAP_REF)
    assert a.confers_authority() is False  # UAL-15 / C7
    assert a.redefines_foundation() is False  # UAL-02 / AMI-05
    assert a.selects_technology() is False  # UAL-15 (abstract references only)
    assert a.embeds_secret() is False


def test_technology_bearing_application_is_detected():
    techy = make_application("t", "ENG-005:CAPABILITY:react.dashboard")
    assert techy.selects_technology() is True  # UAL-15 — concrete UI technology named


def test_secret_bearing_application_is_detected():
    leaky = make_application("t", "ENG-005:CAPABILITY:password-vault")
    assert leaky.embeds_secret() is True  # UAL-15 / RR-07


def test_application_to_dict_records_substrate_reuse():
    a = make_application("t", CAP_REF)
    payload = a.to_dict()
    assert payload["substrate_refs"] == [
        "ENG-001",
        "ENG-002",
        "ENG-003",
        "ENG-004",
        "ENG-005",
        "RL-F2",
        "PL-F2",
        "DF-2",
        "SF-2",
    ]
    assert payload["meta_class"] == "AMC-01"
    assert payload["kind"] == "Single-Module-Application"
    assert payload["capability_ref"] == CAP_REF
    assert payload["state"] == "DEFINED"


def test_canonical_core_excludes_state_and_id():
    a = make_application("t", CAP_REF)
    core = a.canonical_core()
    assert "state" not in core  # lifecycle is not identity-defining
    assert "application_id" not in core
    assert core["meta_class"] == "AMC-01"


def test_state_does_not_change_identity():
    a = make_application("t", CAP_REF, state=ApplicationState.DEFINED)
    b = make_application("t", CAP_REF, state=ApplicationState.EXECUTABLE)
    assert a.application_id == b.application_id  # identity is core-derived, not state


def test_application_type_is_the_realized_construct():
    assert isinstance(make_application("t", CAP_REF), Application)
