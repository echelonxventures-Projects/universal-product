"""EC2-TASK-000145 — Validation console contracts & view-projection tests (EC2-EPIC-010).

Covers the vocabulary (re-exported engine verdict/severity/status, the read-only
``ValidationAction`` verb→permission map bound to ``validation-explorer``), the immutable
view projections (finding/summary/decision/evidence-reference/trace), the
``ValidationRecord`` aggregate (content-addressed identity, idempotence, faithful
projections, fail-closed construction), and the published contract surface.
"""

from __future__ import annotations

from platform.foundation.identity import Permission
from platform.identity.contracts import CapabilityGroup
from platform.tests.validation_console_helpers import accepted_subject, rejected_subject
from platform.validation.contracts import (
    VALIDATION_CONSOLE_CONTRACT_VERSION,
    VALIDATION_CONSOLE_CONTRACTS,
    VALIDATION_CONSOLE_GROUP,
    CheckStatus,
    FindingView,
    Severity,
    ValidationAction,
    ValidationDecisionView,
    ValidationEvidenceReference,
    ValidationRecord,
    ValidationSummary,
    ValidationTrace,
    Verdict,
    all_validation_actions,
    default_validation_console_contracts,
    permission_for,
    validation_console_contract,
)
from platform.validation.errors import ValidationContractError
from platform.validation.metadata import ValidationRecordMetadata

import pytest

from engine.validation.evidence import build_validation_evidence
from engine.validation.executor import ValidationEngine
from engine.validation.gates import enforce_acceptance


def _surface(subject):
    report = ValidationEngine().validate(subject)
    return report, build_validation_evidence(report), enforce_acceptance(report)


def _record(subject, **kw):
    report, evidence, decision = _surface(subject)
    return ValidationRecord.create(
        report=report,
        evidence=evidence,
        decision=decision,
        subject=subject,
        owner_subject=kw.pop("owner_subject", "arch@x"),
        **kw,
    )


# --------------------------------------------------------------------------- #
# Vocabulary                                                                   #
# --------------------------------------------------------------------------- #


def test_group_is_reused_validation_explorer():
    assert VALIDATION_CONSOLE_GROUP is CapabilityGroup.VALIDATION_EXPLORER


def test_engine_vocabulary_is_reexported_not_redefined():
    from engine.validation.contracts import CheckStatus as ECS
    from engine.validation.contracts import Severity as ES
    from engine.validation.contracts import Verdict as EV

    assert Verdict is EV
    assert Severity is ES
    assert CheckStatus is ECS


def test_every_action_requires_read_only():
    assert set(all_validation_actions()) == set(ValidationAction)
    for action in ValidationAction:
        assert permission_for(action) is Permission.READ


def test_permission_for_rejects_bad_action():
    with pytest.raises(ValidationContractError):
        permission_for("inspect")  # type: ignore[arg-type]


# --------------------------------------------------------------------------- #
# View projections                                                             #
# --------------------------------------------------------------------------- #


def test_finding_views_faithful():
    record = _record(rejected_subject())
    views = record.finding_views()
    assert views
    for view in views:
        assert isinstance(view, FindingView)
        assert view.status in {"pass", "fail"}
        assert view.to_dict()["check_id"] == view.check_id
    assert any(v.blocking_failure for v in views)


def test_summary_projection_matches_report():
    record = _record(accepted_subject())
    summary = record.summary()
    assert isinstance(summary, ValidationSummary)
    assert summary.accepted is True
    assert summary.blocking_failed == 0
    assert summary.to_dict()["verdict"] == "pass"


def test_decision_view_projection():
    record = _record(rejected_subject())
    view = record.decision_view()
    assert isinstance(view, ValidationDecisionView)
    assert view.accepted is False
    assert view.blocking_failures
    assert view.to_dict()["accepted"] is False


def test_evidence_reference_carries_fingerprint():
    record = _record(accepted_subject())
    ref = record.evidence_reference()
    assert isinstance(ref, ValidationEvidenceReference)
    assert ref.evidence_format == "ucos-validation-evidence/1.0.0"
    assert ref.evidence_fingerprint
    assert ref.to_dict()["accepted"] is True


def test_trace_projection_and_edge():
    record = _record(accepted_subject(), request_ref="UCOS-GREQ-abc")
    trace = record.trace()
    assert isinstance(trace, ValidationTrace)
    assert trace.is_traceable is True
    edge = trace.edge()
    assert edge["link"] == "validation-trace"
    assert edge["request"]["request_ref"] == "UCOS-GREQ-abc"
    assert edge["traceable"] is True
    assert trace.trace_id.startswith("UCOS-VTRC-")
    assert trace.fingerprint()


def test_trace_not_traceable_when_chain_unrooted():
    trace = ValidationTrace.create(
        target_id="t",
        blueprint_id="bp",
        verdict="pass",
        accepted=True,
        provenance_chain=("other", "bp"),
    )
    assert trace.is_traceable is False


def test_view_projections_reject_bad_types():
    with pytest.raises(ValidationContractError):
        FindingView.from_finding("nope")  # type: ignore[arg-type]
    with pytest.raises(ValidationContractError):
        ValidationSummary.from_report("nope")  # type: ignore[arg-type]
    with pytest.raises(ValidationContractError):
        ValidationDecisionView.from_decision("nope")  # type: ignore[arg-type]
    with pytest.raises(ValidationContractError):
        ValidationEvidenceReference.from_evidence("nope")  # type: ignore[arg-type]


# --------------------------------------------------------------------------- #
# ValidationRecord aggregate                                                   #
# --------------------------------------------------------------------------- #


def test_record_is_content_addressed_and_idempotent():
    a = _record(accepted_subject())
    b = _record(accepted_subject())
    assert a.record_id == b.record_id
    assert a.record_id.startswith("UCOS-VREP-")
    assert a.fingerprint() == b.fingerprint()


def test_record_binding_changes_identity():
    base = _record(accepted_subject())
    bound = _record(accepted_subject(), request_ref="UCOS-GREQ-1", tenant="acme")
    assert base.record_id != bound.record_id


def test_record_accepted_property_and_report_fingerprint():
    record = _record(accepted_subject())
    assert record.accepted is True
    assert record.report_fingerprint()


def test_record_with_metadata_preserves_id():
    record = _record(accepted_subject())
    updated = record.with_metadata(ValidationRecordMetadata.create(description="d"))
    assert updated.record_id == record.record_id
    assert updated.metadata.description == "d"


def test_record_to_dict_roundtrip_fields():
    record = _record(accepted_subject(), request_ref="UCOS-GREQ-1", workspace_id="UCOS-WSPC-1")
    d = record.to_dict()
    assert d["record_id"] == record.record_id
    assert d["report"]["verdict"] == "pass"
    assert d["request_ref"] == "UCOS-GREQ-1"
    assert d["workspace_id"] == "UCOS-WSPC-1"


@pytest.mark.parametrize(
    "bad",
    ["report", "evidence", "decision", "subject", "owner", "metadata"],
)
def test_record_create_fail_closed(bad):
    report, evidence, decision = _surface(accepted_subject())
    subject = accepted_subject()
    kwargs = dict(
        report=report,
        evidence=evidence,
        decision=decision,
        subject=subject,
        owner_subject="arch@x",
    )
    if bad == "report":
        kwargs["report"] = "nope"
    elif bad == "evidence":
        kwargs["evidence"] = "nope"
    elif bad == "decision":
        kwargs["decision"] = "nope"
    elif bad == "subject":
        kwargs["subject"] = "nope"
    elif bad == "owner":
        kwargs["owner_subject"] = ""
    elif bad == "metadata":
        kwargs["metadata"] = "nope"
    with pytest.raises(ValidationContractError):
        ValidationRecord.create(**kwargs)  # type: ignore[arg-type]


def test_record_rejects_blank_binding_and_metadata_type_on_copy():
    report, evidence, decision = _surface(accepted_subject())
    subject = accepted_subject()
    with pytest.raises(ValidationContractError):
        ValidationRecord.create(
            report=report,
            evidence=evidence,
            decision=decision,
            subject=subject,
            owner_subject="arch@x",
            workspace_id="",
        )
    record = _record(accepted_subject())
    with pytest.raises(ValidationContractError):
        record.with_metadata("nope")  # type: ignore[arg-type]


def test_record_rejects_report_subject_target_mismatch():
    report, evidence, decision = _surface(accepted_subject())
    other_subject = accepted_subject(target="UCOS-RUN-other-0123456789abcdef")
    with pytest.raises(ValidationContractError):
        ValidationRecord.create(
            report=report,
            evidence=evidence,
            decision=decision,
            subject=other_subject,
            owner_subject="arch@x",
        )


# --------------------------------------------------------------------------- #
# Published contract surface                                                   #
# --------------------------------------------------------------------------- #


def test_published_contracts_versioned_and_named():
    assert VALIDATION_CONSOLE_CONTRACT_VERSION == "1.0.0"
    names = {ref.name for ref in VALIDATION_CONSOLE_CONTRACTS}
    assert "validation.runtime.service" in names
    assert "validation.facade.surface" in names
    for ref in VALIDATION_CONSOLE_CONTRACTS:
        assert ref.version == "1.0.0"


def test_default_contracts_build_and_reject_blank_name():
    contracts = default_validation_console_contracts()
    assert len(contracts) == len(VALIDATION_CONSOLE_CONTRACTS)
    with pytest.raises(ValidationContractError):
        validation_console_contract("")
