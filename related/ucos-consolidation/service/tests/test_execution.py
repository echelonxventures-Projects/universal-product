"""EC3-B11-U08 — Universal Execution construct tests (SMC-08).

Covers construction fail-closed guards, operation-binding, RUNTIME reuse by reference,
transactionality-by-reference, DF-2 data by reference, policy governance, founding acyclicity
(no self-founding), identity/value determinism, non-constitutiveness, lifecycle, serialization.
"""

from __future__ import annotations

import pytest

from service.execution import (
    DEFAULT_POLICY_REF,
    Execution,
    _default_behavior_ref,
    make_execution,
)
from service.execution_meta import (
    EXECUTION_RELATIONSHIPS,
    KIND_RUNTIME_CONCERN,
    ExecutionKind,
)
from service.service import ServiceError
from service.service_meta import ServiceState

_OP = "ENG-005:SOE-05:ucos.service.operation.foundation"
_DATA = ("ENG-005:DF-2:ucos.data.entity.executed",)


def _sync() -> Execution:
    return make_execution(
        "ucos.service.execution.foundation",
        _OP,
        kind=ExecutionKind.SYNCHRONOUS,
        data_refs=_DATA,
    )


# -- construction guards ----------------------------------------------------


def test_untyped_execution_rejected():
    with pytest.raises(ServiceError, match="typed"):
        make_execution("  ", _OP)


def test_bad_kind_rejected():
    with pytest.raises(ServiceError, match="ExecutionKind"):
        Execution(type_tag="t", kind="Synchronous", operation_ref=_OP)  # type: ignore[arg-type]


def test_empty_operation_ref_rejected():
    with pytest.raises(ServiceError, match="operation_ref"):
        make_execution("t", "   ")


def test_non_tuple_data_refs_rejected():
    with pytest.raises(ServiceError, match="tuple of ENG-005 references"):
        make_execution("t", _OP, data_refs=["x"])  # type: ignore[arg-type]


def test_blank_data_ref_entry_rejected():
    with pytest.raises(ServiceError, match="entries must be non-empty"):
        make_execution("t", _OP, data_refs=("ok", "  "))


def test_blank_policy_ref_rejected():
    with pytest.raises(ServiceError, match="policy_ref"):
        make_execution("t", _OP, policy_ref="   ")


def test_bad_state_rejected():
    with pytest.raises(ServiceError, match="ServiceState"):
        Execution(type_tag="t", kind=ExecutionKind.SYNCHRONOUS, operation_ref=_OP, state="X")  # type: ignore[arg-type]


# -- identity + defaults ----------------------------------------------------


def test_identity_is_deterministic_and_prefixed():
    a, b = _sync(), _sync()
    assert a.execution_id == b.execution_id
    assert a.execution_id.startswith("UCOS-EXECUTION-")
    assert len(a.value_digest) == 64


def test_self_ref_form():
    assert _sync().self_ref == "ENG-005:SOE-08:ucos.service.execution.foundation"


def test_meta_class_and_relationships():
    e = _sync()
    assert e.meta_class == "SMC-08"
    assert e.meta_relationships() == EXECUTION_RELATIONSHIPS


@pytest.mark.parametrize("kind", list(ExecutionKind))
def test_default_behavior_ref_matches_kind(kind):
    ref = _default_behavior_ref(kind)
    assert KIND_RUNTIME_CONCERN[kind] in ref
    e = make_execution("t", _OP, kind=kind)
    assert e.runtime_reuse_valid() is True


def test_explicit_behavior_ref_preserved():
    e = make_execution("t", _OP, behavior_ref="ENG-005:RL-F2:RUNTIME-009.transact",
                       kind=ExecutionKind.TRANSACTIONAL)
    assert e.behavior_ref == "ENG-005:RL-F2:RUNTIME-009.transact"
    assert e.policy_ref == DEFAULT_POLICY_REF


# -- founding acyclicity + self-founding ------------------------------------


def test_canonical_execution_is_founding_acyclic():
    e = _sync()
    assert e.no_self_founding() is True
    assert e.is_founding_acyclic() is True
    assert e.references_resolve() is True


def test_self_founding_operation_ref_rejected_by_acyclicity():
    e = make_execution("t", "ENG-005:SOE-08:t", kind=ExecutionKind.SYNCHRONOUS)
    assert e.no_self_founding() is False
    assert e.is_founding_acyclic() is False
    assert e.references_resolve() is False


def test_self_founding_via_data_ref_detected():
    e = make_execution("t", _OP, data_refs=("ENG-005:SOE-08:t",))
    assert e.no_self_founding() is False


# -- obligations ------------------------------------------------------------


def test_obligation_predicates_hold_for_canonical():
    e = _sync()
    assert e.operation_bound() is True
    assert e.fulfils_contract() is True
    assert e.runtime_reuse_valid() is True
    assert e.behavior_by_reference() is True
    assert e.transactionality_by_reference() is True  # N/A for synchronous → True
    assert e.data_by_reference() is True
    assert e.policy_governed() is True
    assert e.records_completion() is True
    assert e.references_resolve() is True
    assert e.redefines_foundation() is False
    assert e.confers_authority() is False


def test_transactional_requires_workflow_reference():
    ok = make_execution("t", _OP, kind=ExecutionKind.TRANSACTIONAL)
    assert ok.transactionality_by_reference() is True
    assert "RUNTIME-009" in ok.behavior_ref
    bad = make_execution("t", _OP, behavior_ref="ENG-005:RL-F2:RUNTIME-006.run",
                         kind=ExecutionKind.TRANSACTIONAL)
    assert bad.transactionality_by_reference() is False
    assert bad.runtime_reuse_valid() is False


def test_asynchronous_reuses_event_concern():
    e = make_execution("t", _OP, kind=ExecutionKind.ASYNCHRONOUS)
    assert "RUNTIME-008" in e.behavior_ref
    assert e.runtime_reuse_valid() is True
    assert e.transactionality_by_reference() is True  # N/A → True


def test_runtime_reuse_invalid_when_wrong_concern():
    e = make_execution("t", _OP, behavior_ref="ENG-005:RL-F2:RUNTIME-999.other",
                       kind=ExecutionKind.SYNCHRONOUS)
    assert e.runtime_reuse_valid() is False


def test_selects_technology_detected():
    e = make_execution("t", "ENG-005:SOE-05:kafka.op", kind=ExecutionKind.SYNCHRONOUS)
    assert e.selects_technology() is True


def test_embeds_secret_detected():
    e = make_execution("t", "ENG-005:SOE-05:password.op", kind=ExecutionKind.SYNCHRONOUS)
    assert e.embeds_secret() is True


def test_clean_execution_has_no_tech_or_secret():
    e = _sync()
    assert e.selects_technology() is False
    assert e.embeds_secret() is False


# -- lifecycle --------------------------------------------------------------


def test_forward_transition_ok():
    e = _sync().transition(ServiceState.CONTRACTED)
    assert e.state is ServiceState.CONTRACTED


def test_backward_transition_rejected():
    e = _sync().transition(ServiceState.EXECUTABLE)
    with pytest.raises(ServiceError, match="forward-only"):
        e.transition(ServiceState.DEFINED)


def test_bad_transition_target_rejected():
    with pytest.raises(ServiceError, match="ServiceState"):
        _sync().transition("EXECUTABLE")  # type: ignore[arg-type]


# -- serialization ----------------------------------------------------------


def test_to_dict_is_complete_and_deterministic():
    d = _sync().to_dict()
    assert d["meta_class"] == "SMC-08"
    assert d["kind"] == ExecutionKind.SYNCHRONOUS.value
    assert d["operation_ref"] == _OP
    assert d["runtime_concern"] == "RUNTIME-006"
    assert d["data_refs"] == list(_DATA)
    assert d["policy_ref"] == DEFAULT_POLICY_REF
    assert d["relationships"] == list(EXECUTION_RELATIONSHIPS)
    assert "RL-F2" in d["substrate_refs"] and "DF-2" in d["substrate_refs"]
