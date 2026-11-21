"""EC2-TASK-000100 — Blueprint structural validation tests (EC2-EPIC-006, P4).

Covers the deterministic validation orchestration: a valid EC-1 classification yields a
valid result; an unresolved or defective classification is rejected with the EC-1 gap
report (fail-closed). The platform adds no validation semantics beyond surfacing EC-1.
"""

from __future__ import annotations

from platform.blueprints.classification import classify
from platform.blueprints.contracts import BlueprintFamily
from platform.blueprints.errors import BlueprintValidationError
from platform.blueprints.validation import ValidationResult, evaluate, require_valid

import pytest


def test_valid_classification_evaluates_valid():
    result = evaluate(classify("UCOS-BLPR-1", BlueprintFamily.DATA))
    assert result.valid is True
    assert result.family is BlueprintFamily.DATA
    assert result.gap_report == ()
    assert result.result_id.startswith("UCOS-BVLD-")
    assert result.to_dict()["valid"] is True


def test_unresolved_classification_is_invalid_with_gap_report():
    result = evaluate(classify("UCOS-BLPR-1", BlueprintFamily.DATA, resolved=False))
    assert result.valid is False
    assert any("did not resolve" in g for g in result.gap_report)


def test_defective_classification_carries_defects():
    result = evaluate(
        classify("UCOS-BLPR-1", BlueprintFamily.API, defects=["schema-missing", "type-error"])
    )
    assert result.valid is False
    assert "schema-missing" in result.gap_report
    assert "type-error" in result.gap_report


def test_evaluate_is_deterministic():
    a = evaluate(classify("UCOS-BLPR-1", BlueprintFamily.DATA))
    b = evaluate(classify("UCOS-BLPR-1", BlueprintFamily.DATA))
    assert a.fingerprint() == b.fingerprint()


def test_evaluate_rejects_non_classification():
    with pytest.raises(BlueprintValidationError):
        evaluate("nope")  # type: ignore[arg-type]


def test_require_valid_passes_for_valid():
    result = require_valid(classify("UCOS-BLPR-1", BlueprintFamily.DATA))
    assert isinstance(result, ValidationResult)
    assert result.valid is True


def test_require_valid_raises_with_gap_report_for_invalid():
    with pytest.raises(BlueprintValidationError) as exc:
        require_valid(classify("UCOS-BLPR-1", BlueprintFamily.API, defects=["bad"]))
    assert "bad" in str(exc.value.context.get("gap_report", ""))
