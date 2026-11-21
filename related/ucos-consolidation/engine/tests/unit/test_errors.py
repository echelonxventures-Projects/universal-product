"""Tests for TASK-000006 error taxonomy."""

from __future__ import annotations

from engine.foundation.obs.errors import (
    ConfigurationError,
    ContractViolation,
    FoundationError,
    ObservabilityError,
    SecurityViolation,
    ValidationError,
)

SUBCLASSES = [
    ConfigurationError,
    SecurityViolation,
    ContractViolation,
    ObservabilityError,
    ValidationError,
]


def test_all_subclasses_are_foundation_errors():
    for cls in SUBCLASSES:
        assert issubclass(cls, FoundationError)


def test_stable_unique_codes():
    codes = [cls.code for cls in SUBCLASSES]
    assert len(codes) == len(set(codes))
    assert FoundationError.code == "FND-000"


def test_to_dict_and_context():
    err = ConfigurationError("bad key", key="x", environment="qa")
    payload = err.to_dict()
    assert payload["code"] == "FND-CONFIG-001"
    assert payload["error"] == "ConfigurationError"
    assert payload["message"] == "bad key"
    assert payload["context"] == {"key": "x", "environment": "qa"}


def test_str_with_and_without_context():
    with_ctx = str(SecurityViolation("nope", key="secret_key"))
    assert "FND-SEC-001" in with_ctx
    assert "key=" in with_ctx
    without_ctx = str(ValidationError("plain"))
    assert without_ctx == "[FND-VALID-001] plain"
