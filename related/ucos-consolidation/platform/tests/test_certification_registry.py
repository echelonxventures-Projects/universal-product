"""EC2-TASK-000154 — Certification record registry tests (EC2-EPIC-011).

Covers append-only registration (idempotent by content-addressed id, fail-closed on a
conflicting id), resolution, discovery/scoping, the append-only inspection log, the
status census, and deterministic serialization.
"""

from __future__ import annotations

from platform.certification.contracts import (
    CertificationConsoleRecord,
    CertificationRecordMetadata,
)
from platform.certification.errors import CertificationRecordError
from platform.certification.registry import CertificationRegistry, InspectionEvent
from platform.tests.certification_console_helpers import (
    VERSION,
    certified_output,
    not_certified_output,
)

import pytest

from engine.certification.contracts import CertificationSubject
from engine.certification.engine import CertificationEngine
from engine.certification.evidence import build_certification_evidence


def _record(validation_output, **kw):
    report, evidence = validation_output
    subject = CertificationSubject.from_validation(report, evidence, version=VERSION)
    decision = CertificationEngine().certify(subject)
    return CertificationConsoleRecord.create(
        report=report,
        validation_evidence=evidence,
        decision=decision,
        certification_evidence=build_certification_evidence(decision),
        owner_subject=kw.pop("owner_subject", "arch@x"),
        **kw,
    )


def test_register_resolve_and_membership():
    reg = CertificationRegistry()
    record = _record(certified_output(), tenant="acme")
    stored = reg.record(record)
    assert stored is record
    assert record.record_id in reg
    assert len(reg) == 1
    assert reg.get(record.record_id).record_id == record.record_id
    assert reg.ids == (record.record_id,)
    assert reg.all() == (record,)


def test_register_is_idempotent_and_conflict_fail_closed():
    reg = CertificationRegistry()
    record = _record(certified_output(), tenant="acme")
    reg.record(record)
    assert reg.record(_record(certified_output(), tenant="acme")).record_id == record.record_id
    clash = CertificationConsoleRecord(
        record_id=record.record_id,
        certification_id=record.certification_id,
        target_id=record.target_id,
        blueprint_id=record.blueprint_id,
        version=record.version,
        report=record.report,
        validation_evidence=record.validation_evidence,
        decision=record.decision,
        record=record.record,
        certification_evidence=record.certification_evidence,
        request_ref="UCOS-GREQ-x",
        workspace_id=None,
        project_id=None,
        tenant=record.tenant,
        owner_subject="other@x",
        metadata=record.metadata,
    )
    with pytest.raises(CertificationRecordError):
        reg.record(clash)


def test_register_rejects_bad_type_and_unknown_get():
    reg = CertificationRegistry()
    with pytest.raises(CertificationRecordError):
        reg.record("nope")  # type: ignore[arg-type]
    with pytest.raises(CertificationRecordError):
        reg.get("UCOS-CREC-missing")


def test_by_target_by_certification_and_discover_scoping():
    reg = CertificationRegistry()
    a = _record(certified_output(), tenant="acme", request_ref="UCOS-GREQ-1", workspace_id="w1")
    b = _record(not_certified_output(), tenant="beta")
    reg.record(a)
    reg.record(b)
    assert reg.by_target(a.target_id) == (a,)
    assert reg.by_certification(a.certification_id) == (a,)
    assert reg.discover(certified=True) == (a,)
    assert reg.discover(certified=False) == (b,)
    assert reg.discover(target_id=b.target_id) == (b,)
    assert reg.discover(blueprint_id=a.blueprint_id) == (a,)
    assert reg.discover(certification_id=a.certification_id) == (a,)
    assert reg.discover(request_ref="UCOS-GREQ-1") == (a,)
    assert reg.discover(workspace_id="w1") == (a,)
    assert {r.record_id for r in reg.discover(tenant="acme")} == {a.record_id}


def test_discover_project_scope():
    reg = CertificationRegistry()
    a = _record(certified_output(), project_id="p1")
    reg.record(a)
    assert reg.discover(project_id="p1") == (a,)
    assert reg.discover(project_id="p2") == ()


def test_update_metadata_preserves_id():
    reg = CertificationRegistry()
    record = _record(certified_output())
    reg.record(record)
    updated = reg.update_metadata(
        record.record_id, CertificationRecordMetadata.create(description="d")
    )
    assert updated.record_id == record.record_id
    assert reg.get(record.record_id).metadata.description == "d"


def test_inspection_log_append_only_and_scoped():
    reg = CertificationRegistry()
    record = _record(certified_output())
    reg.record(record)
    e1 = reg.record_inspection(record.record_id, "inspect", "UCOS-PRIN-1", tick=1)
    e2 = reg.record_inspection(record.record_id, "trace", "UCOS-PRIN-1", tick=2)
    assert isinstance(e1, InspectionEvent)
    assert (e1.sequence, e2.sequence) == (0, 1)
    assert reg.inspections == (e1, e2)
    assert reg.inspections_of(record.record_id) == (e1, e2)
    assert e1.to_dict()["action"] == "inspect"


def test_inspection_for_unknown_record_fail_closed():
    reg = CertificationRegistry()
    with pytest.raises(CertificationRecordError):
        reg.record_inspection("UCOS-CREC-missing", "inspect", "UCOS-PRIN-1", tick=1)


def test_status_census_and_serialization():
    reg = CertificationRegistry()
    reg.record(_record(certified_output()))
    reg.record(_record(not_certified_output()))
    census = reg.count_by_status()
    assert census == {"total": 2, "certified": 1, "not_certified": 1}
    d = reg.to_dict()
    assert d["record_count"] == 2
    assert d["status_census"]["certified"] == 1
    assert reg.fingerprint() == reg.fingerprint()
