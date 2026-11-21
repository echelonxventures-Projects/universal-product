"""EC3-B11-U09 — Universal Policy construct tests (SMC-09).

Covers construction fail-closed guards, boundary binding (SMR-02), governed scope (SMR-08),
RUNTIME reuse by reference (RUNTIME-010), DF-2 data by reference, declarative non-enforcement
(USL-13), founding acyclicity (no self-founding), precedence, recorded judgments (SPL-C1),
conflict detection (§12), identity/value determinism, non-constitutiveness, lifecycle,
serialization.
"""

from __future__ import annotations

import pytest

from service.policy import (
    Policy,
    PolicyConflict,
    PolicyDecision,
    PolicyVerdict,
    _default_behavior_ref,
    detect_policy_conflicts,
    make_policy,
)
from service.policy_meta import (
    KIND_PRECEDENCE,
    KIND_RUNTIME_CONCERN,
    POLICY_RELATIONSHIPS,
    PolicyKind,
)
from service.service import ServiceError
from service.service_meta import ServiceState

_CONTRACT = "ENG-005:SOE-03:ucos.service.contract.foundation"
_OP = "ENG-005:SOE-05:ucos.service.operation.foundation"
_EXEC = "ENG-005:SOE-08:ucos.service.execution.foundation"
_DATA = ("ENG-005:DF-2:ucos.data.entity.governed",)


def _authz() -> Policy:
    return make_policy(
        "ucos.service.policy.foundation",
        _CONTRACT,
        kind=PolicyKind.AUTHORIZATION,
        subject_refs=(_OP, _EXEC),
        data_refs=_DATA,
    )


# -- construction guards ----------------------------------------------------


def test_untyped_policy_rejected():
    with pytest.raises(ServiceError, match="typed"):
        make_policy("  ", _CONTRACT)


def test_bad_kind_rejected():
    with pytest.raises(ServiceError, match="PolicyKind"):
        Policy(type_tag="t", kind="Authorization", contract_ref=_CONTRACT)  # type: ignore[arg-type]


def test_empty_contract_ref_rejected():
    with pytest.raises(ServiceError, match="contract_ref"):
        make_policy("t", "   ")


def test_non_tuple_subject_refs_rejected():
    with pytest.raises(ServiceError, match="tuple of ENG-005 references"):
        make_policy("t", _CONTRACT, subject_refs=["x"])  # type: ignore[arg-type]


def test_blank_subject_ref_entry_rejected():
    with pytest.raises(ServiceError, match="entries must be non-empty"):
        make_policy("t", _CONTRACT, subject_refs=(_OP, "  "))


def test_non_tuple_data_refs_rejected():
    with pytest.raises(ServiceError, match="tuple of ENG-005 references"):
        make_policy("t", _CONTRACT, data_refs=["x"])  # type: ignore[arg-type]


def test_blank_data_ref_entry_rejected():
    with pytest.raises(ServiceError, match="entries must be non-empty"):
        make_policy("t", _CONTRACT, data_refs=("ok", "  "))


def test_bad_state_rejected():
    with pytest.raises(ServiceError, match="ServiceState"):
        Policy(type_tag="t", kind=PolicyKind.AUTHORIZATION, contract_ref=_CONTRACT, state="X")  # type: ignore[arg-type]


# -- identity + defaults ----------------------------------------------------


def test_identity_is_deterministic_and_prefixed():
    a, b = _authz(), _authz()
    assert a.policy_id == b.policy_id
    assert a.policy_id.startswith("UCOS-POLICY-")
    assert len(a.value_digest) == 64


def test_self_ref_form():
    assert _authz().self_ref == "ENG-005:SOE-09:ucos.service.policy.foundation"


def test_meta_class_and_relationships():
    p = _authz()
    assert p.meta_class == "SMC-09"
    assert p.meta_relationships() == POLICY_RELATIONSHIPS


@pytest.mark.parametrize("kind", list(PolicyKind))
def test_default_behavior_ref_is_runtime_010(kind):
    ref = _default_behavior_ref(kind)
    assert KIND_RUNTIME_CONCERN[kind] in ref
    assert "RUNTIME-010" in ref
    p = make_policy("t", _CONTRACT, kind=kind)
    assert p.runtime_reuse_valid() is True


def test_explicit_behavior_ref_preserved():
    p = make_policy("t", _CONTRACT, behavior_ref="ENG-005:RL-F2:RUNTIME-010.evaluate")
    assert p.behavior_ref == "ENG-005:RL-F2:RUNTIME-010.evaluate"


def test_empty_subject_and_data_refs_allowed():
    p = make_policy("t", _CONTRACT)
    assert p.subject_refs == ()
    assert p.data_refs == ()
    assert p.scope_by_reference() is True
    assert p.data_by_reference() is True


# -- founding acyclicity + self-founding ------------------------------------


def test_canonical_policy_is_founding_acyclic():
    p = _authz()
    assert p.no_self_founding() is True
    assert p.is_founding_acyclic() is True
    assert p.references_resolve() is True


def test_self_founding_contract_ref_rejected_by_acyclicity():
    p = make_policy("t", "ENG-005:SOE-09:t")
    assert p.no_self_founding() is False
    assert p.is_founding_acyclic() is False
    assert p.references_resolve() is False


def test_self_founding_via_subject_ref_detected():
    p = make_policy("t", _CONTRACT, subject_refs=("ENG-005:SOE-09:t",))
    assert p.no_self_founding() is False


def test_self_founding_via_data_ref_detected():
    p = make_policy("t", _CONTRACT, data_refs=("ENG-005:SOE-09:t",))
    assert p.no_self_founding() is False


# -- obligations ------------------------------------------------------------


def test_obligation_predicates_hold_for_canonical():
    p = _authz()
    assert p.boundary_bound() is True
    assert p.declarative_nonenforcing() is True
    assert p.runtime_reuse_valid() is True
    assert p.behavior_by_reference() is True
    assert p.data_by_reference() is True
    assert p.scope_by_reference() is True
    assert p.precedence_decidable() is True
    assert p.records_lifecycle() is True
    assert p.references_resolve() is True
    assert p.redefines_foundation() is False
    assert p.confers_authority() is False


@pytest.mark.parametrize(
    "kind,rank",
    [
        (PolicyKind.AUTHORIZATION, 0),
        (PolicyKind.VALIDATION, 1),
        (PolicyKind.QUOTA_SLA, 2),
    ],
)
def test_precedence_matches_taxonomy_order(kind, rank):
    p = make_policy("t", _CONTRACT, kind=kind)
    assert p.precedence == rank
    assert KIND_PRECEDENCE[kind] == rank


def test_runtime_reuse_invalid_when_wrong_concern():
    p = make_policy("t", _CONTRACT, behavior_ref="ENG-005:RL-F2:RUNTIME-999.other")
    assert p.runtime_reuse_valid() is False


def test_selects_technology_detected():
    p = make_policy("t", "ENG-005:SOE-03:kafka.contract")
    assert p.selects_technology() is True


def test_embeds_secret_detected():
    p = make_policy("t", "ENG-005:SOE-03:password.contract")
    assert p.embeds_secret() is True


def test_clean_policy_has_no_tech_or_secret():
    p = _authz()
    assert p.selects_technology() is False
    assert p.embeds_secret() is False


# -- declarative evaluation → recorded judgment (SPL-C1) --------------------


def test_record_decision_satisfied_for_governed_subject():
    p = _authz()
    d = p.record_decision(_OP, satisfied=True)
    assert isinstance(d, PolicyDecision)
    assert d.verdict is PolicyVerdict.SATISFIED
    assert d.policy_id == p.policy_id
    assert d.subject_ref == _OP
    assert d.kind == PolicyKind.AUTHORIZATION.value
    assert d.enacts_nothing() is True


def test_record_decision_violated_for_governed_subject():
    d = _authz().record_decision(_EXEC, satisfied=False)
    assert d.verdict is PolicyVerdict.VIOLATED


def test_record_decision_inapplicable_when_out_of_scope():
    d = _authz().record_decision("ENG-005:SOE-05:some.other.op", satisfied=True)
    assert d.verdict is PolicyVerdict.INAPPLICABLE


def test_record_decision_applies_when_scope_unbound():
    # A policy with no declared subjects governs any subject presented (scope open).
    p = make_policy("t", _CONTRACT)
    d = p.record_decision(_OP, satisfied=True)
    assert d.verdict is PolicyVerdict.SATISFIED


def test_record_decision_rejects_empty_subject():
    with pytest.raises(ServiceError, match="subject_ref"):
        _authz().record_decision("   ", satisfied=True)


def test_applies_to():
    p = _authz()
    assert p.applies_to(_OP) is True
    assert p.applies_to("ENG-005:SOE-05:nope") is False


def test_decision_to_dict_shape():
    d = _authz().record_decision(_OP, satisfied=True)
    payload = d.to_dict()
    assert payload["verdict"] == "SATISFIED"
    assert payload["enacts"] == "none"
    assert payload["policy_id"].startswith("UCOS-POLICY-")


# -- conflict detection (§12, evaluative/non-enforcing) ---------------------


def test_detect_conflicts_flags_ambiguous_same_kind_binding():
    p1 = make_policy("a", _CONTRACT, kind=PolicyKind.AUTHORIZATION, subject_refs=(_OP,))
    p2 = make_policy(
        "b", "ENG-005:SOE-03:other.contract", kind=PolicyKind.AUTHORIZATION, subject_refs=(_OP,)
    )
    conflicts = detect_policy_conflicts((p1, p2))
    assert len(conflicts) == 1
    c = conflicts[0]
    assert isinstance(c, PolicyConflict)
    assert c.subject_ref == _OP
    assert c.kind == PolicyKind.AUTHORIZATION.value
    assert set(c.policy_ids) == {p1.policy_id, p2.policy_id}
    assert c.governing_policy_id == min(p1.policy_id, p2.policy_id)


def test_no_conflict_when_same_contract_boundary():
    p1 = make_policy("a", _CONTRACT, kind=PolicyKind.AUTHORIZATION, subject_refs=(_OP,))
    p2 = make_policy("b", _CONTRACT, kind=PolicyKind.AUTHORIZATION, subject_refs=(_OP,))
    assert detect_policy_conflicts((p1, p2)) == ()


def test_no_conflict_across_different_kinds():
    p1 = make_policy("a", _CONTRACT, kind=PolicyKind.AUTHORIZATION, subject_refs=(_OP,))
    p2 = make_policy(
        "b", "ENG-005:SOE-03:other.contract", kind=PolicyKind.VALIDATION, subject_refs=(_OP,)
    )
    assert detect_policy_conflicts((p1, p2)) == ()


def test_no_conflict_when_single_policy_governs_subject():
    assert detect_policy_conflicts((_authz(),)) == ()


def test_conflict_to_dict_shape():
    p1 = make_policy("a", _CONTRACT, kind=PolicyKind.VALIDATION, subject_refs=(_OP,))
    p2 = make_policy(
        "b", "ENG-005:SOE-03:other.contract", kind=PolicyKind.VALIDATION, subject_refs=(_OP,)
    )
    payload = detect_policy_conflicts((p1, p2))[0].to_dict()
    assert payload["kind"] == PolicyKind.VALIDATION.value
    assert "records only" in payload["resolution"]


# -- lifecycle --------------------------------------------------------------


def test_forward_transition_ok():
    p = _authz().transition(ServiceState.CONTRACTED)
    assert p.state is ServiceState.CONTRACTED


def test_backward_transition_rejected():
    p = _authz().transition(ServiceState.EXECUTABLE)
    with pytest.raises(ServiceError, match="forward-only"):
        p.transition(ServiceState.DEFINED)


def test_bad_transition_target_rejected():
    with pytest.raises(ServiceError, match="ServiceState"):
        _authz().transition("EXECUTABLE")  # type: ignore[arg-type]


# -- serialization ----------------------------------------------------------


def test_to_dict_is_complete_and_deterministic():
    d = _authz().to_dict()
    assert d["meta_class"] == "SMC-09"
    assert d["kind"] == PolicyKind.AUTHORIZATION.value
    assert d["contract_ref"] == _CONTRACT
    assert d["subject_refs"] == [_OP, _EXEC]
    assert d["runtime_concern"] == "RUNTIME-010"
    assert d["data_refs"] == list(_DATA)
    assert d["precedence"] == 0
    assert d["relationships"] == list(POLICY_RELATIONSHIPS)
    assert "RL-F2" in d["substrate_refs"] and "DF-2" in d["substrate_refs"]
