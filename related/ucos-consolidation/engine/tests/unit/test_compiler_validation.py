"""TASK-000020/000029 — Validation Engine tests (certification + registry gate)."""

from __future__ import annotations

import pytest

from engine.compiler.errors import CertificationError, ValidationError
from engine.compiler.parser import parse_document
from engine.compiler.validation import (
    CERTIFIED_LIFECYCLE,
    BlueprintValidator,
    ValidationReport,
)
from engine.registry.models import LifecycleStatus


def test_validate_accepts_certified_registered_blueprint(compiler_registry, data_blueprint):
    validator = BlueprintValidator(compiler_registry)
    report = validator.validate(parse_document(data_blueprint))
    assert isinstance(report, ValidationReport)
    assert report.is_valid
    assert report.certified
    assert len(report.resolved_provenance) == 6
    assert validator.is_valid(parse_document(data_blueprint))


def test_reject_uncertified_blueprint(compiler_registry, data_blueprint):
    data_blueprint["certification"] = {"status": "UNCERTIFIED", "evidence": ""}
    validator = BlueprintValidator(compiler_registry)
    ir = parse_document(data_blueprint)
    with pytest.raises(CertificationError) as exc:
        validator.validate(ir)
    assert exc.value.context["declared_status"] == "UNCERTIFIED"
    assert not validator.is_valid(ir)


def test_reject_unregistered_provenance(compiler_registry, data_blueprint):
    data_blueprint["provenance"]["canonical_source"] = "UCOS-DAT-999999"
    validator = BlueprintValidator(compiler_registry)
    with pytest.raises(CertificationError) as exc:
        validator.validate(parse_document(data_blueprint))
    assert exc.value.context["chain"] == "canonical_source"
    assert exc.value.context["reference"] == "UCOS-DAT-999999"


def test_reject_non_certified_source_status(compiler_registry, data_blueprint):
    # UCOS-DAT-000099 is registered but IN_PROGRESS (not a certified status).
    data_blueprint["provenance"]["canonical_source"] = "UCOS-DAT-000099"
    validator = BlueprintValidator(compiler_registry)
    with pytest.raises(CertificationError) as exc:
        validator.validate(parse_document(data_blueprint))
    assert exc.value.context["status"] == "IN_PROGRESS"


def test_reject_missing_primary_key(compiler_registry, data_blueprint):
    for attribute in data_blueprint["entity"]["attributes"]:
        attribute["primary_key"] = False
        attribute["nullable"] = True
    validator = BlueprintValidator(compiler_registry)
    with pytest.raises(ValidationError) as exc:
        validator.validate(parse_document(data_blueprint))
    assert "primary key" in exc.value.message


def test_reject_composite_primary_key(compiler_registry, data_blueprint):
    data_blueprint["entity"]["attributes"].append(
        {"name": "region", "data_type": "string", "nullable": False, "primary_key": True}
    )
    validator = BlueprintValidator(compiler_registry)
    with pytest.raises(ValidationError) as exc:
        validator.validate(parse_document(data_blueprint))
    assert exc.value.context["primary_key_count"] == 2


def test_certified_lifecycle_membership():
    assert LifecycleStatus.ACTIVE in CERTIFIED_LIFECYCLE
    assert LifecycleStatus.CERTIFIED in CERTIFIED_LIFECYCLE
    assert LifecycleStatus.IN_PROGRESS not in CERTIFIED_LIFECYCLE
    assert LifecycleStatus.RETIRED not in CERTIFIED_LIFECYCLE
