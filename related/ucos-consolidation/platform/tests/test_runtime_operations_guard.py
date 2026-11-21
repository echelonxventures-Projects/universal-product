"""EC2-TASK-000166 — Runtime Operations admission guard tests (EC2-EPIC-012).

Covers the deterministic, fail-closed CERTIFIED-only admission gate: a certified unit is
admitted; a non-CERTIFIED unit, a certification that does not govern the unit, a missing
disclosure, an unpinned package, and an empty dependency closure each deny admission with
the first failing criterion as the reason.
"""

from __future__ import annotations

from platform.runtime_operations.contracts import RuntimeOperationKind
from platform.runtime_operations.errors import RuntimeOperationsContractError
from platform.runtime_operations.guard import (
    ADMISSION_CRITERIA,
    AdmissionDecision,
    RuntimeAdmissionGuard,
)
from platform.tests.runtime_operations_helpers import (
    certification_record,
    not_certified_unit_and_record,
    runtime_unit,
)

import pytest

_GUARD = RuntimeAdmissionGuard()


def test_admits_certified_unit():
    unit = runtime_unit()
    decision = _GUARD.evaluate(unit, certification_record(), RuntimeOperationKind.DEPLOY)
    assert decision.admitted is True
    assert decision.reason == "admitted"
    assert decision.certified is True
    assert decision.blockers == ()
    assert decision.admission_id.startswith("UCOS-ROAD-")
    assert decision.to_dict()["admitted"] is True
    assert decision.fingerprint() == decision.fingerprint()
    assert _GUARD.admits(unit, certification_record(), RuntimeOperationKind.ROLLBACK) is True


def test_denies_not_certified_unit():
    unit, cert = not_certified_unit_and_record()
    decision = _GUARD.evaluate(unit, cert, RuntimeOperationKind.DEPLOY)
    assert decision.admitted is False
    assert decision.reason == "certified"
    assert "certified" in decision.blockers


def test_denies_target_mismatch():
    unit = runtime_unit(runtime_id="UCOS-RUN-mismatch-000000000000", blueprint="UCOS-BLPR-1")
    decision = _GUARD.evaluate(unit, certification_record(), RuntimeOperationKind.DEPLOY)
    assert decision.admitted is False
    assert decision.reason == "target-matches-unit"


def test_denies_blueprint_mismatch():
    # Certified certification (target aligned) but a unit whose blueprint differs.
    unit = runtime_unit(blueprint="UCOS-BLPR-OTHER")
    decision = _GUARD.evaluate(unit, certification_record(), RuntimeOperationKind.DEPLOY)
    assert decision.admitted is False
    assert decision.reason == "blueprint-matches-unit"


def test_denies_missing_disclosure_package_closure():
    cert = certification_record()

    def reason(**kw):
        return _GUARD.evaluate(runtime_unit(**kw), cert, RuntimeOperationKind.DEPLOY).reason

    assert reason(with_disclosure=False) == "disclosure-present"
    assert reason(with_package=False) == "package-pinned"
    assert reason(with_closure=False) == "closure-present"


def test_guard_rejects_bad_arguments():
    unit = runtime_unit()
    cert = certification_record()
    with pytest.raises(RuntimeOperationsContractError):
        _GUARD.evaluate("nope", cert, RuntimeOperationKind.DEPLOY)  # type: ignore[arg-type]
    with pytest.raises(RuntimeOperationsContractError):
        _GUARD.evaluate(unit, "nope", RuntimeOperationKind.DEPLOY)  # type: ignore[arg-type]
    with pytest.raises(RuntimeOperationsContractError):
        _GUARD.evaluate(unit, cert, "deploy")  # type: ignore[arg-type]


def test_admission_criteria_order_stable():
    assert ADMISSION_CRITERIA[0] == "certification-present"
    assert ADMISSION_CRITERIA[-1] == "closure-present"


def test_admission_decision_is_deterministic():
    unit = runtime_unit()
    a = _GUARD.evaluate(unit, certification_record(), RuntimeOperationKind.DEPLOY)
    b = _GUARD.evaluate(unit, certification_record(), RuntimeOperationKind.DEPLOY)
    assert isinstance(a, AdmissionDecision)
    assert a.fingerprint() == b.fingerprint()
