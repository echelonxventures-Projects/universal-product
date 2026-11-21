"""EPIC-PLAT-003 — Validation subject assimilation tests (Terminal T5)."""

from __future__ import annotations

from platform.repository_operations.errors import StageExecutionError
from platform.repository_operations.subjects import build_validation_subject
from platform.tests.repository_operations_helpers import valid_validation_subject

import pytest


def test_build_validation_subject_valid():
    subject = build_validation_subject(valid_validation_subject())
    assert subject.target_id == "T-1"
    assert subject.blueprint_id == "BP-1"
    assert subject.runtime_id == "UCOS-RUN-BP-1-0123456789abcdef"
    assert subject.blueprint_class == "service"
    assert subject.disclosure is not None
    assert subject.provenance_chain == ("BP-1", "gen")


def test_build_validation_subject_defaults_when_optional_absent():
    subject = build_validation_subject({"target_id": "T", "blueprint_id": "B"})
    assert subject.runtime_id is None
    assert subject.blueprint_class is None
    assert subject.disclosure is None
    assert subject.provenance_chain == ()
    assert subject.signature == {}
    assert subject.dependency_closure == ()


def test_build_validation_subject_rejects_non_mapping():
    with pytest.raises(StageExecutionError):
        build_validation_subject([1, 2])  # type: ignore[arg-type]


def test_build_validation_subject_requires_identity():
    with pytest.raises(StageExecutionError):
        build_validation_subject({"target_id": "T"})
