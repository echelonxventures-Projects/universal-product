"""EC2-CAP-SEC-001 / SEC-CLASS — traceability validation tests.

Asserts complete requirement traceability: the determination artifact exists and
authorizes SEC-CLASS; every SEC-CLASS responsibility (classify · record · trace ·
validate · report) is realized; and every classification is reverse-traceable to its
constitutional source and forward-traceable to the certified L7 seam
(ARCH-SECURITY-001 §14).
"""

from __future__ import annotations

from pathlib import Path
from platform.foundation.identity import Permission
from platform.identity.contracts import CapabilityGroup
from platform.security.contracts import (
    SUBJECT_LAYER_SOURCE,
    ClassificationKind,
    EnforcementReference,
    SubjectLayer,
    all_subject_layers,
)
from platform.security.service import build_security_classification_service

_REPO_ROOT = Path(__file__).resolve().parents[2]
_DETERMINATION = _REPO_ROOT / "platform" / "security" / "EC2-CAP-SEC-001-DETERMINATION.md"


def test_determination_artifact_exists():
    assert _DETERMINATION.is_file()


def test_determination_authorizes_sec_class():
    text = _DETERMINATION.read_text(encoding="utf-8")
    assert "SEC-CLASS" in text
    assert "Security Classification Binding Runtime" in text
    assert "READY FOR IMPLEMENTATION" in text


def test_service_realizes_every_sec_class_responsibility():
    service = build_security_classification_service()
    # classify · record · trace · validate · report (mission responsibilities).
    for responsibility in ("classify", "record", "trace", "validate", "validate_all", "report"):
        assert callable(getattr(service, responsibility))


def test_every_classification_traces_backward_to_a_constitutional_source():
    for layer in all_subject_layers():
        assert layer in SUBJECT_LAYER_SOURCE
        assert SUBJECT_LAYER_SOURCE[layer]


def test_recorded_classification_is_reverse_and_forward_traceable():
    service = build_security_classification_service()
    c = service.classify(
        ClassificationKind.AUTHORIZATION,
        SubjectLayer.SERVICE,
        "UCOS-SVC-000001",
        "required",
        enforcement_ref=EnforcementReference.create(
            CapabilityGroup.GENERATION_REQUESTS, Permission.EXECUTE
        ),
    )
    trace = service.trace(c.classification_id)
    # backward: constitution + originating layer
    assert trace["backward"]["layer"] == "SERVICE-014"
    assert "SERVICE-014" in trace["backward"]["constitution_ref"]
    # subject: the classified construct
    assert trace["subject"]["subject_ref"] == "UCOS-SVC-000001"
    # forward: the certified L7 seam
    assert trace["forward"]["seam"] == "platform.identity.AuthorizationService"


def test_non_l7_classification_traces_backward_with_no_forward_enactment():
    service = build_security_classification_service()
    c = service.classify(
        ClassificationKind.ISOLATION,
        SubjectLayer.INFRASTRUCTURE,
        "UCOS-INF-000001",
        "isolated",
    )
    trace = service.trace(c.classification_id)
    assert "INFRASTRUCTURE-013" in trace["backward"]["constitution_ref"]
    assert trace["forward"] is None


def test_evidence_report_carries_full_traceable_records():
    service = build_security_classification_service()
    service.classify(
        ClassificationKind.CONFIDENTIALITY, SubjectLayer.DATA, "UCOS-DATA-000001", "restricted"
    )
    evidence = service.report()
    assert evidence.classification_count == 1
    record = evidence.classifications[0]
    assert record["layer"] == "DATA-014"
    assert record["constitution_ref"]


def test_determination_authorizes_sec_intel():
    text = _DETERMINATION.read_text(encoding="utf-8")
    assert "SEC-INTEL" in text
    assert "Security Intelligence Runtime" in text


def test_intel_service_realizes_every_sec_intel_responsibility():
    from platform.security.intelligence import build_security_intelligence_service

    service = build_security_intelligence_service()
    # record · rollup · trace · validate · report (mission responsibilities).
    for responsibility in (
        "record_finding",
        "record",
        "rollup",
        "trace",
        "validate",
        "validate_all",
        "report",
    ):
        assert callable(getattr(service, responsibility))


def test_finding_traces_backward_to_the_schema_and_forward_to_affected_refs():
    from platform.security.contracts import FindingKind, Severity
    from platform.security.intelligence import build_security_intelligence_service

    service = build_security_intelligence_service()
    f = service.record_finding(
        FindingKind.VULNERABILITY,
        "CVE-2026-42",
        severity=Severity.HIGH,
        identifier="CVE-2026-42",
        affects=("UCOS-SVC-000001",),
    )
    trace = service.trace(f.finding_id)
    assert "finding.schema.json" in trace["backward"]["source_ref"]
    assert trace["affects"] == ["UCOS-SVC-000001"]


def test_determination_authorizes_sec_reg():
    text = _DETERMINATION.read_text(encoding="utf-8")
    assert "SEC-REG" in text
    assert "Security Registry Runtime" in text


def test_registry_entry_traces_backward_to_its_constitutional_source():
    from platform.security.contracts import RegistryKind
    from platform.security.registries import build_security_registry_service

    service = build_security_registry_service()
    e = service.record(
        RegistryKind.TRUST,
        "trust-anchor",
        "UCOS-INF-000001",
        recorded_by="UCOS-PRIN-000001",
        recorded_at=1,
        refs=("UCOS-SFND-1",),
    )
    trace = service.trace(RegistryKind.TRUST, e.entry_id)
    assert "§17" in trace["backward"]["source_ref"]
    assert trace["refs"] == ["UCOS-SFND-1"]


def test_determination_authorizes_sec_obs():
    text = _DETERMINATION.read_text(encoding="utf-8")
    assert "SEC-OBS" in text
    assert "Security Observability Runtime" in text


def test_security_signal_is_reverse_traceable_to_its_finding():
    # UMB-015 §5: every security event is reverse-traceable to the finding/scan.
    from platform.security.contracts import FindingKind, RollupState, Severity
    from platform.security.intelligence import build_security_intelligence_service
    from platform.security.observability import build_security_observability_service

    intel = build_security_intelligence_service()
    f = intel.record_finding(
        FindingKind.VULNERABILITY, "CVE-2026-7", severity=Severity.CRITICAL, affects=("UCOS-SVC-1",)
    )
    obs = build_security_observability_service()
    sig = obs.emit_signal(RollupState.BLOCKED, "UCOS-SVC-1", traces_to=f.finding_id, emitted_at=1)
    assert obs.trace(sig.signal_id)["traces_to"] == f.finding_id


def test_determination_authorizes_sec_cert():
    text = _DETERMINATION.read_text(encoding="utf-8")
    assert "SEC-CERT" in text
    assert "Security Certification Runtime" in text


def test_certification_traces_backward_to_section_18_and_cites_evidence():
    from platform.security.certification import build_security_certification_service
    from platform.security.contracts import CertificationClass, CertificationDecision

    service = build_security_certification_service()
    c = service.certify(
        CertificationClass.SECURITY,
        "UCOS-CMP-1",
        CertificationDecision.CERTIFIED,
        basis="rolled up from evidence",
        certified_at=1,
        evidence_refs=("UCOS-SIEV-1",),
    )
    trace = service.trace(c.certification_id)
    assert trace["backward"]["source_ref"] == "ARCH-SECURITY-001 §18"
    assert trace["evidence_refs"] == ["UCOS-SIEV-1"]


def test_determination_authorizes_sec_zone():
    text = _DETERMINATION.read_text(encoding="utf-8")
    assert "SEC-ZONE" in text
    assert "Zone & Control Posture Runtime" in text


def test_zone_posture_traces_backward_to_umb_015():
    from platform.security.contracts import RollupState, SecurityZone
    from platform.security.zones import build_security_zone_service

    service = build_security_zone_service()
    p = service.assess_zone(
        SecurityZone.CORE,
        RollupState.APPROVED,
        rationale="append-only via T",
        evaluated_at=1,
        evidence_refs=("UCOS-SREG-1",),
    )
    trace = service.trace(p.posture_id)
    assert trace["backward"]["source_ref"] == "UMB-015 §1"
    assert trace["evidence_refs"] == ["UCOS-SREG-1"]
