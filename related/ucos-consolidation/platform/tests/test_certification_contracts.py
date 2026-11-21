"""EC2-TASK-000153 — Certification console contracts & view-projection tests (EC2-EPIC-011).

Covers the vocabulary (re-exported engine status/class/severity, the read-only
``CertificationAction`` verb→permission map bound to ``certification-ledger``), the
descriptive metadata value type, the immutable view projections (criterion-finding /
summary / evidence-reference / trace), the ``CertificationConsoleRecord`` aggregate
(content-addressed identity, idempotence, faithful projections, fail-closed
construction), and the published contract surface.
"""

from __future__ import annotations

from platform.certification.contracts import (
    CERTIFICATION_CONSOLE_CONTRACT_VERSION,
    CERTIFICATION_CONSOLE_CONTRACTS,
    CERTIFICATION_CONSOLE_GROUP,
    EMPTY_CERTIFICATION_METADATA,
    ENGINE_CERTIFICATION_CONTRACT,
    CertificationAction,
    CertificationClass,
    CertificationConsoleRecord,
    CertificationEvidenceReference,
    CertificationRecordMetadata,
    CertificationStatus,
    CertificationSummary,
    CertificationTrace,
    CriterionFindingView,
    CriterionSeverity,
    CriterionStatus,
    all_certification_actions,
    certification_console_contract,
    default_certification_console_contracts,
    permission_for,
)
from platform.certification.errors import CertificationContractError
from platform.foundation.identity import Permission
from platform.identity.contracts import CapabilityGroup
from platform.tests.certification_console_helpers import (
    VERSION,
    certified_output,
    not_certified_output,
)

import pytest

from engine.certification.contracts import CertificationSubject
from engine.certification.engine import CertificationEngine
from engine.certification.evidence import build_certification_evidence


def _surface(validation_output):
    report, evidence = validation_output
    subject = CertificationSubject.from_validation(report, evidence, version=VERSION)
    decision = CertificationEngine().certify(subject)
    return report, evidence, decision, build_certification_evidence(decision)


def _record(validation_output, **kw):
    report, evidence, decision, cert_evidence = _surface(validation_output)
    return CertificationConsoleRecord.create(
        report=report,
        validation_evidence=evidence,
        decision=decision,
        certification_evidence=cert_evidence,
        owner_subject=kw.pop("owner_subject", "arch@x"),
        **kw,
    )


# --------------------------------------------------------------------------- #
# Vocabulary                                                                   #
# --------------------------------------------------------------------------- #


def test_group_is_reused_certification_ledger():
    assert CERTIFICATION_CONSOLE_GROUP is CapabilityGroup.CERTIFICATION_LEDGER


def test_engine_vocabulary_is_reexported_not_redefined():
    from engine.certification.contracts import CertificationClass as ECC
    from engine.certification.contracts import CertificationStatus as ECS
    from engine.certification.contracts import CriterionSeverity as ECSev
    from engine.certification.contracts import CriterionStatus as ECSt

    assert CertificationStatus is ECS
    assert CertificationClass is ECC
    assert CriterionSeverity is ECSev
    assert CriterionStatus is ECSt


def test_every_action_requires_read_only():
    assert set(all_certification_actions()) == set(CertificationAction)
    for action in CertificationAction:
        assert permission_for(action) is Permission.READ


def test_permission_for_rejects_bad_action():
    with pytest.raises(CertificationContractError):
        permission_for("inspect")  # type: ignore[arg-type]


# --------------------------------------------------------------------------- #
# Metadata                                                                     #
# --------------------------------------------------------------------------- #


def test_metadata_normalizes_and_is_content_addressed():
    md = CertificationRecordMetadata.create(
        description="d", labels=["b", "a"], annotations={"k": "v"}
    )
    assert md.has_label("a")
    assert md.to_dict()["labels"] == ["a", "b"]
    assert (
        md.fingerprint()
        == CertificationRecordMetadata.create(
            description="d", labels=["a", "b"], annotations={"k": "v"}
        ).fingerprint()
    )
    assert EMPTY_CERTIFICATION_METADATA.description == ""


@pytest.mark.parametrize(
    "kwargs",
    [
        {"description": 123},
        {"labels": [""]},
        {"annotations": {"": "v"}},
        {"annotations": {"k": 1}},
    ],
)
def test_metadata_fail_closed(kwargs):
    with pytest.raises(CertificationContractError):
        CertificationRecordMetadata.create(**kwargs)  # type: ignore[arg-type]


# --------------------------------------------------------------------------- #
# View projections                                                             #
# --------------------------------------------------------------------------- #


def test_criterion_finding_views_faithful():
    record = _record(not_certified_output())
    views = record.criterion_views()
    assert views
    for view in views:
        assert isinstance(view, CriterionFindingView)
        assert view.status in {"pass", "fail"}
        assert view.to_dict()["criterion_id"] == view.criterion_id
    assert any(v.blocking_failure for v in views)


def test_summary_projection_matches_decision():
    record = _record(certified_output())
    summary = record.summary()
    assert isinstance(summary, CertificationSummary)
    assert summary.certified is True
    assert summary.blocking_failed == 0
    assert summary.to_dict()["status"] == "certified"


def test_evidence_reference_carries_fingerprint():
    record = _record(certified_output())
    ref = record.evidence_reference()
    assert isinstance(ref, CertificationEvidenceReference)
    assert ref.evidence_format == "ucos-certification-evidence/1.0.0"
    assert ref.evidence_fingerprint
    assert ref.validation_evidence_ref
    assert ref.record_sha256
    assert ref.to_dict()["certified"] is True


def test_trace_projection_and_edge():
    record = _record(certified_output(), request_ref="UCOS-GREQ-abc")
    trace = record.trace()
    assert isinstance(trace, CertificationTrace)
    assert trace.is_traceable is True
    edge = trace.edge()
    assert edge["link"] == "certification-trace"
    assert edge["request"]["request_ref"] == "UCOS-GREQ-abc"
    assert edge["traceable"] is True
    assert trace.trace_id.startswith("UCOS-CTRC-")
    assert trace.fingerprint()


def test_trace_not_traceable_when_incomplete():
    trace = CertificationTrace.create(
        certification_id="c",
        target_id="t",
        blueprint_id="bp",
        version="1.0.0",
        status="certified",
        certified=True,
        validation_verdict="pass",
        validation_accepted=True,
        validation_evidence_ref="",  # missing upstream evidence → not traceable
    )
    assert trace.is_traceable is False


def test_view_projections_reject_bad_types():
    with pytest.raises(CertificationContractError):
        CriterionFindingView.from_finding("nope")  # type: ignore[arg-type]
    with pytest.raises(CertificationContractError):
        CertificationSummary.from_decision("nope")  # type: ignore[arg-type]
    with pytest.raises(CertificationContractError):
        CertificationEvidenceReference.from_evidence("nope")  # type: ignore[arg-type]


# --------------------------------------------------------------------------- #
# CertificationConsoleRecord aggregate                                         #
# --------------------------------------------------------------------------- #


def test_record_is_content_addressed_and_idempotent():
    a = _record(certified_output())
    b = _record(certified_output())
    assert a.record_id == b.record_id
    assert a.record_id.startswith("UCOS-CREC-")
    assert a.fingerprint() == b.fingerprint()


def test_record_binding_changes_identity():
    base = _record(certified_output())
    bound = _record(certified_output(), request_ref="UCOS-GREQ-1", tenant="acme")
    assert base.record_id != bound.record_id


def test_record_certified_property_and_record_fingerprint():
    record = _record(certified_output())
    assert record.certified is True
    assert record.record_fingerprint() == record.record.content_sha256


def test_record_with_metadata_preserves_id():
    record = _record(certified_output())
    updated = record.with_metadata(CertificationRecordMetadata.create(description="d"))
    assert updated.record_id == record.record_id
    assert updated.metadata.description == "d"


def test_record_to_dict_roundtrip_fields():
    record = _record(certified_output(), request_ref="UCOS-GREQ-1", workspace_id="UCOS-WSPC-1")
    d = record.to_dict()
    assert d["record_id"] == record.record_id
    assert d["record"]["status"] == "certified"
    assert d["request_ref"] == "UCOS-GREQ-1"
    assert d["workspace_id"] == "UCOS-WSPC-1"


@pytest.mark.parametrize(
    "bad",
    ["report", "validation_evidence", "decision", "certification_evidence", "owner", "metadata"],
)
def test_record_create_fail_closed(bad):
    report, evidence, decision, cert_evidence = _surface(certified_output())
    kwargs = dict(
        report=report,
        validation_evidence=evidence,
        decision=decision,
        certification_evidence=cert_evidence,
        owner_subject="arch@x",
    )
    if bad == "owner":
        kwargs["owner_subject"] = ""
    else:
        kwargs[bad] = "nope"
    with pytest.raises(CertificationContractError):
        CertificationConsoleRecord.create(**kwargs)  # type: ignore[arg-type]


def test_record_rejects_blank_binding_and_metadata_type_on_copy():
    report, evidence, decision, cert_evidence = _surface(certified_output())
    with pytest.raises(CertificationContractError):
        CertificationConsoleRecord.create(
            report=report,
            validation_evidence=evidence,
            decision=decision,
            certification_evidence=cert_evidence,
            owner_subject="arch@x",
            workspace_id="",
        )
    record = _record(certified_output())
    with pytest.raises(CertificationContractError):
        record.with_metadata("nope")  # type: ignore[arg-type]


def test_record_rejects_decision_report_target_mismatch():
    report, evidence, decision, cert_evidence = _surface(certified_output())
    other_report, _ = certified_output(target="UCOS-RUN-other-0123456789abcdef")
    with pytest.raises(CertificationContractError):
        CertificationConsoleRecord.create(
            report=other_report,
            validation_evidence=evidence,
            decision=decision,
            certification_evidence=cert_evidence,
            owner_subject="arch@x",
        )


# --------------------------------------------------------------------------- #
# Published contract surface                                                   #
# --------------------------------------------------------------------------- #


def test_published_contracts_versioned_and_named():
    assert CERTIFICATION_CONSOLE_CONTRACT_VERSION == "1.0.0"
    assert ENGINE_CERTIFICATION_CONTRACT == "engine.certification.certify"
    names = {ref.name for ref in CERTIFICATION_CONSOLE_CONTRACTS}
    assert "certification.runtime.service" in names
    assert "certification.ledger.navigate" in names
    assert "certification.lineage.inspect" in names
    for ref in CERTIFICATION_CONSOLE_CONTRACTS:
        assert ref.version == "1.0.0"


def test_default_contracts_build_and_reject_blank_name():
    contracts = default_certification_console_contracts()
    assert len(contracts) == len(CERTIFICATION_CONSOLE_CONTRACTS)
    with pytest.raises(CertificationContractError):
        certification_console_contract("")
