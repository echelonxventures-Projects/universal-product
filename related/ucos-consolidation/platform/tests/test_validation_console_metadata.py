"""EC2-TASK-000145 — Validation record metadata tests (EC2-EPIC-010).

Covers the immutable descriptive metadata value type: normalized construction,
label membership, deterministic fingerprint, the shared empty default, and fail-closed
validation of malformed inputs.
"""

from __future__ import annotations

from platform.validation.errors import ValidationContractError
from platform.validation.metadata import EMPTY_VALIDATION_METADATA, ValidationRecordMetadata

import pytest


def test_create_normalizes_and_serializes():
    md = ValidationRecordMetadata.create(
        description="a note",
        labels=["b", "a"],
        annotations={"k2": "v2", "k1": "v1"},
    )
    assert md.description == "a note"
    assert md.has_label("a") is True
    assert md.has_label("z") is False
    d = md.to_dict()
    assert d["labels"] == ["a", "b"]
    assert list(d["annotations"]) == ["k1", "k2"]
    assert (
        md.fingerprint()
        == ValidationRecordMetadata.create(
            description="a note", labels=["a", "b"], annotations={"k1": "v1", "k2": "v2"}
        ).fingerprint()
    )


def test_empty_metadata_default():
    assert EMPTY_VALIDATION_METADATA.description == ""
    assert EMPTY_VALIDATION_METADATA.labels == frozenset()
    assert EMPTY_VALIDATION_METADATA.to_dict()["labels"] == []


def test_create_fail_closed_inputs():
    with pytest.raises(ValidationContractError):
        ValidationRecordMetadata.create(description=123)  # type: ignore[arg-type]
    with pytest.raises(ValidationContractError):
        ValidationRecordMetadata.create(labels=[""])
    with pytest.raises(ValidationContractError):
        ValidationRecordMetadata.create(annotations={"k": 5})  # type: ignore[dict-item]
    with pytest.raises(ValidationContractError):
        ValidationRecordMetadata.create(annotations={"": "v"})
