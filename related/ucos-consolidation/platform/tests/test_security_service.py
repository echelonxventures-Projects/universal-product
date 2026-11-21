"""EC2-CAP-SEC-001 / SEC-CLASS — service integration tests.

Covers the :class:`SecurityClassificationService` composition root: classify + record,
L7 enforcement-reference resolution (by reference, never authorizes), governed-event
emission, trace / validate / report, and deterministic evidence.
"""

from __future__ import annotations

from platform.foundation.events import EventBus
from platform.foundation.identity import Permission
from platform.identity.contracts import CapabilityGroup
from platform.identity.service import build_authorization_service
from platform.security.contracts import (
    ClassificationKind,
    EnforcementReference,
    SubjectLayer,
)
from platform.security.errors import (
    EnforcementReferenceError,
    SecurityClassificationError,
)
from platform.security.service import (
    CLASSIFICATION_RECORDED_EVENT,
    SecurityClassificationEvidence,
    SecurityClassificationService,
    build_security_classification_service,
)

import pytest


def _authz_ref() -> EnforcementReference:
    return EnforcementReference.create(CapabilityGroup.GENERATION_REQUESTS, Permission.EXECUTE)


def test_service_rejects_bad_ledger():
    with pytest.raises(SecurityClassificationError):
        SecurityClassificationService(ledger="nope")  # type: ignore[arg-type]


def test_service_rejects_bad_authorization():
    with pytest.raises(SecurityClassificationError):
        SecurityClassificationService(authorization="nope")  # type: ignore[arg-type]


def test_service_rejects_bad_events():
    with pytest.raises(SecurityClassificationError):
        SecurityClassificationService(events="nope")  # type: ignore[arg-type]


def test_classify_records_a_confidentiality_classification():
    service = build_security_classification_service()
    c = service.classify(
        ClassificationKind.CONFIDENTIALITY, SubjectLayer.DATA, "UCOS-DATA-000001", "restricted"
    )
    assert c.classification_id in service.ledger
    assert len(service.ledger) == 1


def test_classify_emits_a_governed_event():
    bus = EventBus()
    service = build_security_classification_service(events=bus)
    service.classify(
        ClassificationKind.CONFIDENTIALITY, SubjectLayer.DATA, "UCOS-DATA-000002", "restricted"
    )
    events = bus.events_of(CLASSIFICATION_RECORDED_EVENT)
    assert len(events) == 1
    assert events[0].payload["enacts"] is False
    assert events[0].subject == "UCOS-DATA-000002"


def test_classify_without_event_bus_is_silent_but_records():
    service = build_security_classification_service()
    c = service.classify(
        ClassificationKind.INTEGRITY, SubjectLayer.DATA, "UCOS-DATA-000003", "signed"
    )
    assert c.classification_id in service.ledger


def test_authorization_bound_reflects_seam_presence():
    assert build_security_classification_service().authorization_bound is False
    authz = build_authorization_service()
    assert build_security_classification_service(authorization=authz).authorization_bound is True


def test_l7_bound_classification_resolves_reference_and_records():
    bus = EventBus()
    authz = build_authorization_service()
    service = build_security_classification_service(authorization=authz, events=bus)
    c = service.classify(
        ClassificationKind.AUTHORIZATION,
        SubjectLayer.SERVICE,
        "UCOS-SVC-000001",
        "required",
        enforcement_ref=_authz_ref(),
    )
    assert c.is_l7_bound
    event = bus.events_of(CLASSIFICATION_RECORDED_EVENT)[0]
    resolution = event.payload["enforcement_resolution"]
    assert resolution["resolved"] is True
    assert resolution["enacts"] is False
    assert resolution["seam_bound"] is True
    assert resolution["group"] == "generation-requests"


def test_resolve_enforcement_reference_is_reference_only():
    service = build_security_classification_service()
    resolution = service.resolve_enforcement_reference(_authz_ref())
    assert resolution["resolved"] is True
    assert resolution["enacts"] is False
    assert resolution["seam_bound"] is False  # no authz service bound in this build


def test_resolve_enforcement_reference_rejects_non_reference():
    service = build_security_classification_service()
    with pytest.raises(EnforcementReferenceError):
        service.resolve_enforcement_reference("nope")  # type: ignore[arg-type]


def test_record_prebuilt_classification_resolves_and_records():
    from platform.security.classification import SecurityClassification

    service = build_security_classification_service()
    c = SecurityClassification.create(
        ClassificationKind.AUTHENTICATION,
        SubjectLayer.SERVICE,
        "UCOS-SVC-000002",
        "mfa-required",
        enforcement_ref=EnforcementReference.create(
            CapabilityGroup.IDENTITY_SESSIONS_SELF, Permission.READ
        ),
    )
    recorded = service.record(c)
    assert recorded.classification_id in service.ledger


def test_record_rejects_non_classification():
    service = build_security_classification_service()
    with pytest.raises(SecurityClassificationError):
        service.record("nope")  # type: ignore[arg-type]


def test_record_prebuilt_non_l7_classification_records_without_resolution():
    from platform.security.classification import SecurityClassification

    service = build_security_classification_service()
    c = SecurityClassification.create(
        ClassificationKind.CONFIDENTIALITY, SubjectLayer.DATA, "UCOS-DATA-000099", "restricted"
    )
    recorded = service.record(c)
    assert recorded.classification_id in service.ledger
    assert recorded.enforcement_ref is None


def test_resolve_enforcement_reference_fails_when_group_not_a_known_seam_row(monkeypatch):
    # Defensive guard: if a reference does not resolve to a known L7 row, it is rejected.
    import platform.security.service as svc

    monkeypatch.setattr(svc, "_KNOWN_GROUPS", frozenset(), raising=True)
    service = build_security_classification_service()
    with pytest.raises(EnforcementReferenceError):
        service.resolve_enforcement_reference(_authz_ref())


def test_trace_and_validate_through_service():
    service = build_security_classification_service()
    c = service.classify(
        ClassificationKind.CONFIDENTIALITY, SubjectLayer.DATA, "UCOS-DATA-000004", "restricted"
    )
    trace = service.trace(c.classification_id)
    assert trace["subject"]["subject_ref"] == "UCOS-DATA-000004"
    validation = service.validate(c.classification_id)
    assert validation["meta_valid"] is True


def test_validate_all_aggregates_meta_validity():
    service = build_security_classification_service()
    service.classify(
        ClassificationKind.CONFIDENTIALITY, SubjectLayer.DATA, "UCOS-DATA-000005", "restricted"
    )
    service.classify(
        ClassificationKind.INTEGRITY, SubjectLayer.SERVICE, "UCOS-SVC-000003", "signed"
    )
    result = service.validate_all()
    assert result["classification_count"] == 2
    assert result["meta_valid"] is True


def test_report_produces_deterministic_evidence():
    def build() -> SecurityClassificationEvidence:
        service = build_security_classification_service()
        service.classify(
            ClassificationKind.CONFIDENTIALITY,
            SubjectLayer.DATA,
            "UCOS-DATA-000006",
            "restricted",
        )
        service.classify(
            ClassificationKind.AUTHORIZATION,
            SubjectLayer.SERVICE,
            "UCOS-SVC-000004",
            "required",
            enforcement_ref=_authz_ref(),
        )
        return service.report()

    a = build()
    b = build()
    assert a.evidence_id == b.evidence_id
    assert a.evidence_id.startswith("UCOS-SCEV-")
    assert a.fingerprint() == b.fingerprint()
    assert a.classification_count == 2
    assert a.l7_bound_count == 1


def test_report_kind_counts_cover_every_kind():
    service = build_security_classification_service()
    service.classify(
        ClassificationKind.CONFIDENTIALITY, SubjectLayer.DATA, "UCOS-DATA-000007", "restricted"
    )
    evidence = service.report()
    kinds = {name for name, _ in evidence.kind_counts}
    assert kinds == {k.value for k in ClassificationKind}
    counts = dict(evidence.kind_counts)
    assert counts["confidentiality-record"] == 1
    assert counts["authorization-record"] == 0


def test_to_dict_summary_reports_binding_and_evidence():
    authz = build_authorization_service()
    service = build_security_classification_service(authorization=authz)
    service.classify(
        ClassificationKind.CONFIDENTIALITY, SubjectLayer.DATA, "UCOS-DATA-000008", "restricted"
    )
    summary = service.to_dict()
    assert summary["authorization_bound"] is True
    assert summary["ledger"]["classification_count"] == 1
    assert summary["evidence"]["evidence_id"].startswith("UCOS-SCEV-")


def test_idempotent_classification_records_once():
    bus = EventBus()
    service = build_security_classification_service(events=bus)
    service.classify(
        ClassificationKind.CONFIDENTIALITY, SubjectLayer.DATA, "UCOS-DATA-000009", "restricted"
    )
    service.classify(
        ClassificationKind.CONFIDENTIALITY, SubjectLayer.DATA, "UCOS-DATA-000009", "restricted"
    )
    assert len(service.ledger) == 1
    # Two record events fire (one per call) but the ledger is idempotent.
    assert len(bus.events_of(CLASSIFICATION_RECORDED_EVENT)) == 2
