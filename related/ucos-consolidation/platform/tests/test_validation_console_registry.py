"""EC2-TASK-000146 — Validation record registry tests (EC2-EPIC-010).

Covers append-only registration (idempotent by content-addressed id, fail-closed on a
conflicting id), resolution, discovery/scoping, the append-only inspection log, the
verdict census, and deterministic serialization.
"""

from __future__ import annotations

from platform.tests.validation_console_helpers import accepted_subject, rejected_subject
from platform.validation.contracts import ValidationRecord
from platform.validation.errors import ValidationRecordError
from platform.validation.metadata import ValidationRecordMetadata
from platform.validation.registry import InspectionEvent, ValidationRecordRegistry

import pytest

from engine.validation.evidence import build_validation_evidence
from engine.validation.executor import ValidationEngine
from engine.validation.gates import enforce_acceptance


def _record(subject, **kw):
    report = ValidationEngine().validate(subject)
    return ValidationRecord.create(
        report=report,
        evidence=build_validation_evidence(report),
        decision=enforce_acceptance(report),
        subject=subject,
        owner_subject=kw.pop("owner_subject", "arch@x"),
        **kw,
    )


def test_register_resolve_and_membership():
    reg = ValidationRecordRegistry()
    record = _record(accepted_subject(), tenant="acme")
    stored = reg.record(record)
    assert stored is record
    assert record.record_id in reg
    assert len(reg) == 1
    assert reg.get(record.record_id).record_id == record.record_id
    assert reg.ids == (record.record_id,)
    assert reg.all() == (record,)


def test_register_is_idempotent_and_conflict_fail_closed():
    reg = ValidationRecordRegistry()
    record = _record(accepted_subject(), tenant="acme")
    reg.record(record)
    # identical record → idempotent
    assert reg.record(_record(accepted_subject(), tenant="acme")).record_id == record.record_id
    # a different record forced onto the same id → refused
    clash = ValidationRecord(
        record_id=record.record_id,
        target_id=record.target_id,
        blueprint_id=record.blueprint_id,
        report=record.report,
        evidence=record.evidence,
        decision=record.decision,
        subject=record.subject,
        request_ref="UCOS-GREQ-x",
        workspace_id=None,
        project_id=None,
        tenant=record.tenant,
        owner_subject="other@x",
        metadata=record.metadata,
    )
    with pytest.raises(ValidationRecordError):
        reg.record(clash)


def test_register_rejects_bad_type_and_unknown_get():
    reg = ValidationRecordRegistry()
    with pytest.raises(ValidationRecordError):
        reg.record("nope")  # type: ignore[arg-type]
    with pytest.raises(ValidationRecordError):
        reg.get("UCOS-VREP-missing")


def test_by_target_and_discover_scoping():
    reg = ValidationRecordRegistry()
    a = _record(accepted_subject(), tenant="acme", request_ref="UCOS-GREQ-1", workspace_id="w1")
    b = _record(rejected_subject(), tenant="beta")
    reg.record(a)
    reg.record(b)
    assert reg.by_target(a.target_id) == (a,)
    assert reg.discover(accepted=True) == (a,)
    assert reg.discover(accepted=False) == (b,)
    assert reg.discover(target_id=b.target_id) == (b,)
    assert reg.discover(blueprint_id=a.blueprint_id) == (a,)
    assert reg.discover(request_ref="UCOS-GREQ-1") == (a,)
    assert reg.discover(workspace_id="w1") == (a,)
    # tenant scoping returns the tenant's records plus untenanted ones
    assert {r.record_id for r in reg.discover(tenant="acme")} == {a.record_id}


def test_discover_project_scope():
    reg = ValidationRecordRegistry()
    a = _record(accepted_subject(), project_id="p1")
    reg.record(a)
    assert reg.discover(project_id="p1") == (a,)
    assert reg.discover(project_id="p2") == ()


def test_update_metadata_preserves_id():
    reg = ValidationRecordRegistry()
    record = _record(accepted_subject())
    reg.record(record)
    updated = reg.update_metadata(
        record.record_id, ValidationRecordMetadata.create(description="d")
    )
    assert updated.record_id == record.record_id
    assert reg.get(record.record_id).metadata.description == "d"


def test_inspection_log_append_only_and_scoped():
    reg = ValidationRecordRegistry()
    record = _record(accepted_subject())
    reg.record(record)
    e1 = reg.record_inspection(record.record_id, "inspect", "UCOS-PRIN-1", tick=1)
    e2 = reg.record_inspection(record.record_id, "trace", "UCOS-PRIN-1", tick=2)
    assert isinstance(e1, InspectionEvent)
    assert (e1.sequence, e2.sequence) == (0, 1)
    assert reg.inspections == (e1, e2)
    assert reg.inspections_of(record.record_id) == (e1, e2)
    assert e1.to_dict()["action"] == "inspect"


def test_inspection_for_unknown_record_fail_closed():
    reg = ValidationRecordRegistry()
    with pytest.raises(ValidationRecordError):
        reg.record_inspection("UCOS-VREP-missing", "inspect", "UCOS-PRIN-1", tick=1)


def test_verdict_census_and_serialization():
    reg = ValidationRecordRegistry()
    reg.record(_record(accepted_subject()))
    reg.record(_record(rejected_subject()))
    census = reg.count_by_verdict()
    assert census == {"total": 2, "accepted": 1, "rejected": 1}
    d = reg.to_dict()
    assert d["record_count"] == 2
    assert d["verdict_census"]["accepted"] == 1
    assert reg.fingerprint() == reg.fingerprint()
