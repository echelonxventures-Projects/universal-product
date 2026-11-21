"""EC2-CAP-SEC-001 / SEC-CERT — Security Certification Runtime tests.

Covers the §18 certification record (evidence-backed, non-constitutive), the §19
control-facet Gap Report guard, the append-only ledger, deterministic program-
certification roll-up, evidence, governed-event emission, and the bootstrap.
"""

from __future__ import annotations

from platform.foundation.bootstrap import bootstrap_platform
from platform.foundation.events import EventBus
from platform.security.bootstrap import (
    SECURITY_CERTIFICATION_BOOTSTRAP_EVENT,
    bootstrap_security_certification,
)
from platform.security.certification import (
    CERTIFICATION_RECORDED_EVENT,
    CertificationLedger,
    ProgramCertification,
    SecurityCertification,
    SecurityCertificationEvidence,
    SecurityCertificationService,
    build_security_certification_service,
    evaluate_control_facets,
    roll_up_program,
)
from platform.security.contracts import (
    REQUIRED_CONTROL_FACETS,
    SECURITY_CERTIFICATION_CONTRACTS,
    CertificationClass,
    CertificationDecision,
    ControlFacet,
)
from platform.security.errors import (
    CertificationValidationError,
    SecurityBootstrapError,
    SecurityCertificationError,
)

import pytest

# --------------------------------------------------------------------------- #
# SecurityCertification (§18; evidence-backed; non-constitutive)               #
# --------------------------------------------------------------------------- #


def test_certified_record_is_deterministic_and_evidence_backed():
    a = SecurityCertification.create(
        CertificationClass.SECURITY,
        "UCOS-CMP-1",
        CertificationDecision.CERTIFIED,
        basis="rolled up from SEC-INTEL evidence",
        certified_at=1,
        evidence_refs=("UCOS-SIEV-1",),
    )
    b = SecurityCertification.create(
        CertificationClass.SECURITY,
        "UCOS-CMP-1",
        CertificationDecision.CERTIFIED,
        basis="rolled up from SEC-INTEL evidence",
        certified_at=1,
        evidence_refs=("UCOS-SIEV-1",),
    )
    assert a.certification_id == b.certification_id
    assert a.certification_id.startswith("UCOS-SCERT-")
    assert a.is_certified is True
    assert a.non_constitutive is True


def test_certified_requires_evidence_refs():
    with pytest.raises(SecurityCertificationError):
        SecurityCertification.create(
            CertificationClass.SECURITY,
            "UCOS-CMP-1",
            CertificationDecision.CERTIFIED,
            basis="no evidence cited",
            certified_at=1,
        )


def test_not_certified_may_omit_evidence():
    c = SecurityCertification.create(
        CertificationClass.OPERATIONAL,
        "UCOS-CMP-2",
        CertificationDecision.NOT_CERTIFIED,
        basis="facet gap",
        certified_at=1,
    )
    assert c.is_certified is False


def test_create_rejects_bad_class_decision_subject_basis_tick():
    NC = CertificationDecision.NOT_CERTIFIED
    with pytest.raises(SecurityCertificationError):
        SecurityCertification.create("x", "UCOS-1", NC, basis="b", certified_at=1)  # type: ignore[arg-type]
    with pytest.raises(SecurityCertificationError):
        SecurityCertification.create(
            CertificationClass.SECURITY, "  ", NC, basis="b", certified_at=1
        )
    with pytest.raises(SecurityCertificationError):
        SecurityCertification.create(
            CertificationClass.SECURITY,
            "UCOS-1",
            "CERTIFIED",
            basis="b",
            certified_at=1,  # type: ignore[arg-type]
        )
    with pytest.raises(SecurityCertificationError):
        SecurityCertification.create(
            CertificationClass.SECURITY, "UCOS-1", NC, basis="  ", certified_at=1
        )
    with pytest.raises(SecurityCertificationError):
        SecurityCertification.create(
            CertificationClass.SECURITY, "UCOS-1", NC, basis="b", certified_at=True
        )


def test_create_rejects_secret_in_evidence_ref():
    with pytest.raises(SecurityCertificationError):
        SecurityCertification.create(
            CertificationClass.SECURITY,
            "UCOS-1",
            CertificationDecision.CERTIFIED,
            basis="b",
            certified_at=1,
            evidence_refs=("password: supersecretvalue",),
        )


def test_validate_trace_and_dict():
    c = SecurityCertification.create(
        CertificationClass.TRUST,
        "UCOS-CMP-9",
        CertificationDecision.CERTIFIED,
        basis="trust anchors verified",
        certified_at=2,
        evidence_refs=("UCOS-SREG-1",),
    )
    assert c.validate()["meta_valid"] is True
    t = c.trace()
    assert t["backward"]["source_ref"] == "ARCH-SECURITY-001 §18"
    assert t["evidence_refs"] == ["UCOS-SREG-1"]
    assert c.to_dict()["non_constitutive"] is True
    assert c.fingerprint() == c.fingerprint()


def test_validate_fails_on_hand_built_uncited_certified_record():
    bad = SecurityCertification(
        certification_class=CertificationClass.SECURITY,
        subject_ref="UCOS-1",
        decision=CertificationDecision.CERTIFIED,
        basis="b",
        certified_at=1,
        evidence_refs=(),
        certification_id="UCOS-SCERT-bad",
    )
    with pytest.raises(CertificationValidationError):
        bad.validate()


# --------------------------------------------------------------------------- #
# §19 control-facet guard / GapReport                                          #
# --------------------------------------------------------------------------- #


def test_evaluate_control_facets_complete_has_no_gaps():
    gap = evaluate_control_facets("UCOS-CMP-1", set(ControlFacet))
    assert gap.has_gaps is False
    assert gap.missing_facets == ()
    assert gap.gap_id.startswith("UCOS-SGAP-")


def test_evaluate_control_facets_reports_missing():
    gap = evaluate_control_facets("UCOS-CMP-1", {ControlFacet.IDENTITY, ControlFacet.TRUST})
    assert gap.has_gaps is True
    assert len(gap.missing_facets) == len(REQUIRED_CONTROL_FACETS) - 2
    assert "traceability" in gap.missing_facets
    assert gap.to_dict()["subject_ref"] == "UCOS-CMP-1"


def test_evaluate_control_facets_rejects_empty_subject():
    with pytest.raises(SecurityCertificationError):
        evaluate_control_facets("  ", set(ControlFacet))


def test_evaluate_ignores_non_facet_members():
    gap = evaluate_control_facets("UCOS-CMP-1", {ControlFacet.IDENTITY, "not-a-facet"})  # type: ignore[arg-type]
    assert ControlFacet.IDENTITY.value in gap.present_facets


# --------------------------------------------------------------------------- #
# CertificationLedger                                                          #
# --------------------------------------------------------------------------- #


def test_ledger_append_only_idempotent_and_queries():
    ledger = CertificationLedger()
    c = SecurityCertification.create(
        CertificationClass.PRIVACY,
        "UCOS-DATA-1",
        CertificationDecision.CERTIFIED,
        basis="pii classified",
        certified_at=1,
        evidence_refs=("UCOS-SCLS-1",),
    )
    ledger.record(c)
    ledger.record(c)
    assert len(ledger) == 1
    assert c.certification_id in ledger
    assert ledger.get(c.certification_id) is c
    assert ledger.by_class(CertificationClass.PRIVACY) == (c,)
    assert ledger.by_subject("UCOS-DATA-1") == (c,)
    assert ledger.by_decision(CertificationDecision.CERTIFIED) == (c,)
    assert isinstance(ledger.fingerprint(), str)
    assert ledger.to_dict()["certification_count"] == 1


def test_ledger_rejects_non_certification_and_missing_get():
    with pytest.raises(SecurityCertificationError):
        CertificationLedger().record("nope")  # type: ignore[arg-type]
    with pytest.raises(SecurityCertificationError):
        CertificationLedger().get("UCOS-SCERT-missing")


# --------------------------------------------------------------------------- #
# Program roll-up                                                              #
# --------------------------------------------------------------------------- #


def test_rollup_empty_is_not_certified():
    prog = roll_up_program(())
    assert prog.decision is CertificationDecision.NOT_CERTIFIED
    assert prog.program_id.startswith("UCOS-SCPR-")


def test_rollup_all_certified_is_certified():
    certs = (
        SecurityCertification.create(
            CertificationClass.SECURITY,
            "UCOS-1",
            CertificationDecision.CERTIFIED,
            basis="b",
            certified_at=1,
            evidence_refs=("UCOS-SIEV-1",),
        ),
        SecurityCertification.create(
            CertificationClass.TRUST,
            "UCOS-2",
            CertificationDecision.CERTIFIED,
            basis="b",
            certified_at=1,
            evidence_refs=("UCOS-SREG-1",),
        ),
    )
    prog = roll_up_program(certs)
    assert prog.decision is CertificationDecision.CERTIFIED
    assert prog.certified_count == 2
    assert prog.not_certified_count == 0
    assert "security-certification" in prog.covered_classes


def test_rollup_any_not_certified_blocks():
    certs = (
        SecurityCertification.create(
            CertificationClass.SECURITY,
            "UCOS-1",
            CertificationDecision.CERTIFIED,
            basis="b",
            certified_at=1,
            evidence_refs=("UCOS-SIEV-1",),
        ),
        SecurityCertification.create(
            CertificationClass.OPERATIONAL,
            "UCOS-2",
            CertificationDecision.NOT_CERTIFIED,
            basis="gap",
            certified_at=1,
        ),
    )
    prog = roll_up_program(certs)
    assert prog.decision is CertificationDecision.NOT_CERTIFIED
    assert prog.to_dict()["constitutive"] is False


def test_program_certification_is_content_addressed():
    prog = ProgramCertification.create(
        decision=CertificationDecision.CERTIFIED,
        certification_count=1,
        certified_count=1,
        not_certified_count=0,
        covered_classes=("security-certification",),
    )
    assert prog.program_id.startswith("UCOS-SCPR-")
    assert prog.fingerprint() == prog.fingerprint()


# --------------------------------------------------------------------------- #
# SecurityCertificationService                                                 #
# --------------------------------------------------------------------------- #


def test_service_rejects_bad_ledger_and_events():
    with pytest.raises(SecurityCertificationError):
        SecurityCertificationService(ledger="nope")  # type: ignore[arg-type]
    with pytest.raises(SecurityCertificationError):
        SecurityCertificationService(events="nope")  # type: ignore[arg-type]


def test_certify_records_and_emits_event():
    bus = EventBus()
    service = build_security_certification_service(events=bus)
    c = service.certify(
        CertificationClass.SECURITY,
        "UCOS-CMP-1",
        CertificationDecision.CERTIFIED,
        basis="b",
        certified_at=1,
        evidence_refs=("UCOS-SIEV-1",),
    )
    assert c.certification_id in service.ledger
    evs = bus.events_of(CERTIFICATION_RECORDED_EVENT)
    assert len(evs) == 1
    assert evs[0].payload["constitutive"] is False


def test_certify_without_bus_and_record_prebuilt():
    service = build_security_certification_service()
    c = SecurityCertification.create(
        CertificationClass.COMPLIANCE,
        "UCOS-CMP-2",
        CertificationDecision.CERTIFIED,
        basis="b",
        certified_at=1,
        evidence_refs=("UCOS-SREG-1",),
    )
    assert service.record(c).certification_id in service.ledger
    with pytest.raises(SecurityCertificationError):
        service.record("nope")  # type: ignore[arg-type]


def test_certify_control_complete_records_certified():
    service = build_security_certification_service()
    result = service.certify_control(
        "UCOS-CMP-1", set(ControlFacet), certified_at=1, evidence_refs=("UCOS-SIEV-1",)
    )
    assert result["certified"] is True
    assert result["gap_report"]["missing_facets"] == []


def test_certify_control_gap_records_not_certified_with_gap_ref():
    service = build_security_certification_service()
    result = service.certify_control("UCOS-CMP-2", {ControlFacet.IDENTITY}, certified_at=1)
    assert result["certified"] is False
    assert len(result["gap_report"]["missing_facets"]) == len(REQUIRED_CONTROL_FACETS) - 1
    assert result["certification"]["gap_ref"] == result["gap_report"]["gap_id"]


def test_certify_control_complete_without_explicit_evidence_uses_gap_id():
    # A complete control with no explicit evidence still cites the (empty) gap id.
    service = build_security_certification_service()
    result = service.certify_control("UCOS-CMP-3", set(ControlFacet), certified_at=1)
    assert result["certified"] is True
    assert result["certification"]["evidence_refs"]  # non-empty (cites the gap id)


def test_program_certification_trace_validate_report():
    service = build_security_certification_service()
    c = service.certify(
        CertificationClass.SECURITY,
        "UCOS-CMP-1",
        CertificationDecision.CERTIFIED,
        basis="b",
        certified_at=1,
        evidence_refs=("UCOS-SIEV-1",),
    )
    assert service.trace(c.certification_id)["certification_id"] == c.certification_id
    assert service.validate(c.certification_id)["meta_valid"] is True
    agg = service.validate_all()
    assert agg["certification_count"] == 1
    assert agg["meta_valid"] is True
    prog = service.program_certification()
    assert prog.decision is CertificationDecision.CERTIFIED
    report = service.report()
    assert report.evidence_id.startswith("UCOS-SCTE-")
    assert report.certification_count == 1
    classes = {name for name, _ in report.class_counts}
    assert classes == {c.value for c in CertificationClass}
    decisions = {name for name, _ in report.decision_counts}
    assert decisions == {d.value for d in CertificationDecision}
    assert service.to_dict()["evidence"]["evidence_id"].startswith("UCOS-SCTE-")


def test_report_is_deterministic():
    def build() -> SecurityCertificationEvidence:
        service = build_security_certification_service()
        service.certify(
            CertificationClass.SECURITY,
            "UCOS-CMP-1",
            CertificationDecision.CERTIFIED,
            basis="b",
            certified_at=1,
            evidence_refs=("UCOS-SIEV-1",),
        )
        return service.report()

    a, b = build(), build()
    assert a.evidence_id == b.evidence_id
    assert a.fingerprint() == b.fingerprint()


def test_vocabulary_helpers_cover_all_members():
    from platform.security.contracts import all_certification_classes, all_control_facets

    assert set(all_certification_classes()) == set(CertificationClass)
    assert set(all_control_facets()) == set(ControlFacet)


# --------------------------------------------------------------------------- #
# bootstrap_security_certification                                             #
# --------------------------------------------------------------------------- #


def test_bootstrap_composes_and_publishes_contracts():
    context = bootstrap_platform()
    service = bootstrap_security_certification(context)
    assert isinstance(service, SecurityCertificationService)
    for ref in SECURITY_CERTIFICATION_CONTRACTS:
        assert ref.name in context.services


def test_bootstrap_emits_completion_event():
    context = bootstrap_platform()
    bootstrap_security_certification(context)
    events = context.events.events_of(SECURITY_CERTIFICATION_BOOTSTRAP_EVENT)
    assert len(events) == 1
    assert set(events[0].payload["certification_contracts"]) == {
        r.name for r in SECURITY_CERTIFICATION_CONTRACTS
    }


def test_bootstrap_is_idempotent():
    context = bootstrap_platform()
    bootstrap_security_certification(context)
    bootstrap_security_certification(context)
    for ref in SECURITY_CERTIFICATION_CONTRACTS:
        assert ref.name in context.services


def test_bootstrapped_service_records_end_to_end():
    context = bootstrap_platform()
    service = bootstrap_security_certification(context)
    service.certify(
        CertificationClass.SECURITY,
        "UCOS-CMP-1",
        CertificationDecision.CERTIFIED,
        basis="b",
        certified_at=1,
        evidence_refs=("UCOS-SIEV-1",),
    )
    assert len(context.events.events_of(CERTIFICATION_RECORDED_EVENT)) == 1


def test_bootstrap_is_fail_closed_on_bad_context():
    class _BadContext:
        pass

    with pytest.raises(SecurityBootstrapError):
        bootstrap_security_certification(_BadContext())


def test_bootstrap_reraises_a_security_bootstrap_error_without_double_wrapping(monkeypatch):
    import platform.security.bootstrap as boot

    sentinel = SecurityBootstrapError("inner certification failure")

    def _raise(*_args, **_kwargs):
        raise sentinel

    monkeypatch.setattr(boot, "build_security_certification_service", _raise, raising=True)
    context = bootstrap_platform()
    with pytest.raises(SecurityBootstrapError) as excinfo:
        bootstrap_security_certification(context)
    assert excinfo.value is sentinel


def test_certification_contract_requires_a_name():
    from platform.security.contracts import security_certification_contract
    from platform.security.errors import SecurityContractError

    with pytest.raises(SecurityContractError):
        security_certification_contract("")
