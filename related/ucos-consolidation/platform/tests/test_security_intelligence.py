"""EC2-CAP-SEC-001 / SEC-INTEL — Security Intelligence Runtime tests.

Covers the finding model, the append-only ledger, the evidence-derived roll-up
(UKB-ADV-005 §4), the secret-leak defense (UKB-ADV-005 §6 / SEC-04 / RR-07), the
service composition root, deterministic evidence, governed-event emission, and the
bootstrap composition — all record-only and non-enacting (RG-02 / AR-04).
"""

from __future__ import annotations

from platform.foundation.bootstrap import bootstrap_platform
from platform.foundation.events import EventBus
from platform.security.bootstrap import (
    SECURITY_INTELLIGENCE_BOOTSTRAP_EVENT,
    bootstrap_security_intelligence,
)
from platform.security.contracts import (
    SECURITY_INTELLIGENCE_CONTRACTS,
    FindingKind,
    FindingState,
    RollupState,
    Severity,
)
from platform.security.errors import (
    FindingValidationError,
    SecurityBootstrapError,
    SecurityFindingError,
    SecurityRollupError,
)
from platform.security.intelligence import (
    FINDING_RECORDED_EVENT,
    ROLLUP_EVALUATED_EVENT,
    SECRET_LEAK_IDENTIFIER,
    FindingLedger,
    SecurityFinding,
    SecurityIntelligenceEvidence,
    SecurityIntelligenceService,
    SecurityRollup,
    build_security_intelligence_service,
    compute_rollup,
    scan_for_secret,
)

import pytest

# --------------------------------------------------------------------------- #
# SecurityFinding model                                                        #
# --------------------------------------------------------------------------- #


def test_create_vulnerability_finding_has_deterministic_id():
    a = SecurityFinding.create(
        FindingKind.VULNERABILITY,
        "CVE-2026-1",
        severity=Severity.HIGH,
        affects=("UCOS-SVC-000001",),
    )
    b = SecurityFinding.create(
        FindingKind.VULNERABILITY,
        "CVE-2026-1",
        severity=Severity.HIGH,
        affects=("UCOS-SVC-000001",),
    )
    assert a.finding_id == b.finding_id
    assert a.finding_id.startswith("UCOS-SFND-")
    assert a.non_enforcing is True
    assert a.is_exposure is True
    assert a.is_open() is True


def test_create_rejects_bad_kind():
    with pytest.raises(SecurityFindingError):
        SecurityFinding.create("nope", "x")  # type: ignore[arg-type]


def test_create_rejects_empty_name():
    with pytest.raises(SecurityFindingError):
        SecurityFinding.create(FindingKind.VULNERABILITY, "   ")


def test_create_rejects_bad_state():
    with pytest.raises(SecurityFindingError):
        SecurityFinding.create(FindingKind.VULNERABILITY, "x", state="OPEN")  # type: ignore[arg-type]


def test_create_rejects_bad_severity():
    with pytest.raises(SecurityFindingError):
        SecurityFinding.create(FindingKind.VULNERABILITY, "x", severity="HIGH")  # type: ignore[arg-type]


def test_create_rejects_non_int_tick():
    with pytest.raises(SecurityFindingError):
        SecurityFinding.create(FindingKind.VULNERABILITY, "x", sla_due="soon")  # type: ignore[arg-type]


def test_create_rejects_bool_tick():
    # bool is a subclass of int; a logical tick must be a real int.
    with pytest.raises(SecurityFindingError):
        SecurityFinding.create(FindingKind.VULNERABILITY, "x", expires=True)


def test_exception_requires_reference_approver_and_expiry():
    with pytest.raises(SecurityFindingError):
        SecurityFinding.create(FindingKind.EXCEPTION, "accept", approver="ciso", expires=10)
    with pytest.raises(SecurityFindingError):
        SecurityFinding.create(
            FindingKind.EXCEPTION, "accept", exception_of="UCOS-SFND-abc", expires=10
        )
    with pytest.raises(SecurityFindingError):
        SecurityFinding.create(
            FindingKind.EXCEPTION, "accept", exception_of="UCOS-SFND-abc", approver="ciso"
        )


def test_non_exception_may_not_carry_exception_of():
    with pytest.raises(SecurityFindingError):
        SecurityFinding.create(FindingKind.VULNERABILITY, "x", exception_of="UCOS-SFND-abc")


def test_valid_exception_is_time_boxed():
    ex = SecurityFinding.create(
        FindingKind.EXCEPTION,
        "accept",
        state=FindingState.ACCEPTED,
        exception_of="UCOS-SFND-abc",
        approver="ciso",
        expires=100,
    )
    assert ex.is_valid_exception(50) is True
    assert ex.is_valid_exception(100) is False  # expires <= now => expired
    assert ex.is_valid_exception(150) is False
    # a non-accepted exception is never valid
    pending = SecurityFinding.create(
        FindingKind.EXCEPTION,
        "accept",
        state=FindingState.OPEN,
        exception_of="UCOS-SFND-abc",
        approver="ciso",
        expires=100,
    )
    assert pending.is_valid_exception(50) is False


def test_non_exception_is_never_a_valid_exception():
    f = SecurityFinding.create(FindingKind.VULNERABILITY, "x", severity=Severity.LOW)
    assert f.is_valid_exception(0) is False


def test_control_is_not_an_exposure():
    c = SecurityFinding.create(FindingKind.CONTROL, "AC-2", mitigates=("THREAT-1",))
    assert c.is_exposure is False


def test_validate_success_and_trace():
    f = SecurityFinding.create(
        FindingKind.VULNERABILITY,
        "CVE",
        severity=Severity.MEDIUM,
        identifier="CVE-2026-9",
        affects=("UCOS-SVC-000001",),
    )
    v = f.validate()
    assert v["meta_valid"] is True
    t = f.trace()
    assert t["subject"]["identifier"] == "CVE-2026-9"
    assert t["affects"] == ["UCOS-SVC-000001"]
    assert "finding.schema.json" in t["backward"]["source_ref"]


def test_validate_fails_on_secret_evidence():
    # A finding built directly with secret evidence fails meta-validity (defensive).
    f = SecurityFinding.create(
        FindingKind.AUDIT_EVIDENCE, "audit", evidence="token=abcdef1234567890"
    )
    with pytest.raises(FindingValidationError):
        f.validate()


def test_to_dict_and_fingerprint_roundtrip():
    f = SecurityFinding.create(FindingKind.THREAT, "spoofing", severity=Severity.HIGH)
    d = f.to_dict()
    assert d["kind"] == "THREAT"
    assert d["non_enforcing"] is True
    assert (
        f.fingerprint()
        == SecurityFinding.create(
            FindingKind.THREAT, "spoofing", severity=Severity.HIGH
        ).fingerprint()
    )


# --------------------------------------------------------------------------- #
# scan_for_secret                                                              #
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize(
    "text",
    [
        "-----BEGIN PRIVATE KEY-----",
        "-----BEGIN RSA PRIVATE KEY-----",
        "AKIAIOSFODNN7EXAMPLE",
        "ghp_0123456789abcdefghijklmnopqrstuvwx",
        "xoxb-1234567890-abcdefghij",
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dBjftJeZ4CVPmB92K27u",
        "password: supersecretvalue",
        "api_key=abcdefghij",
    ],
)
def test_scan_for_secret_detects_shapes(text):
    assert scan_for_secret(text) is True


def test_scan_for_secret_ignores_benign_and_empty():
    assert scan_for_secret(None) is False
    assert scan_for_secret("") is False
    assert scan_for_secret("a normal finding about the login page") is False


# --------------------------------------------------------------------------- #
# FindingLedger                                                                #
# --------------------------------------------------------------------------- #


def test_ledger_is_append_only_and_idempotent():
    ledger = FindingLedger()
    f = SecurityFinding.create(FindingKind.VULNERABILITY, "CVE", severity=Severity.LOW)
    ledger.record(f)
    ledger.record(f)  # idempotent by id
    assert len(ledger) == 1
    assert f.finding_id in ledger


def test_ledger_rejects_non_finding():
    with pytest.raises(SecurityFindingError):
        FindingLedger().record("nope")  # type: ignore[arg-type]


def test_ledger_get_missing_raises():
    with pytest.raises(SecurityFindingError):
        FindingLedger().get("UCOS-SFND-missing")


def test_ledger_queries():
    ledger = FindingLedger()
    v = SecurityFinding.create(
        FindingKind.VULNERABILITY, "CVE", severity=Severity.HIGH, affects=("UCOS-SVC-000001",)
    )
    c = SecurityFinding.create(FindingKind.CONTROL, "AC-2")
    ex = SecurityFinding.create(
        FindingKind.EXCEPTION,
        "accept",
        state=FindingState.ACCEPTED,
        exception_of=v.finding_id,
        approver="ciso",
        expires=100,
    )
    for f in (v, c, ex):
        ledger.record(f)
    assert ledger.by_kind(FindingKind.VULNERABILITY) == (v,)
    assert ledger.by_state(FindingState.ACCEPTED) == (ex,)
    assert ledger.by_severity(Severity.HIGH) == (v,)
    assert ledger.affecting("UCOS-SVC-000001") == (v,)
    assert ledger.exceptions() == (ex,)
    assert ledger.to_dict()["finding_count"] == 3
    assert isinstance(ledger.fingerprint(), str)


# --------------------------------------------------------------------------- #
# compute_rollup (evidence-derived; UKB-ADV-005 §4)                            #
# --------------------------------------------------------------------------- #


def test_rollup_blocked_on_open_critical():
    f = SecurityFinding.create(FindingKind.VULNERABILITY, "CVE", severity=Severity.CRITICAL)
    r = compute_rollup((f,), now=0)
    assert r.state is RollupState.BLOCKED
    assert r.blocking_count == 1
    assert r.blocked_by == (f.finding_id,)


def test_rollup_in_progress_on_open_medium():
    f = SecurityFinding.create(FindingKind.VULNERABILITY, "CVE", severity=Severity.MEDIUM)
    r = compute_rollup((f,), now=0)
    assert r.state is RollupState.IN_PROGRESS
    assert r.blocking_count == 0
    assert r.in_progress_count == 1


def test_rollup_approved_when_no_open_exposures():
    resolved = SecurityFinding.create(
        FindingKind.VULNERABILITY, "CVE", severity=Severity.CRITICAL, state=FindingState.RESOLVED
    )
    control = SecurityFinding.create(FindingKind.CONTROL, "AC-2")
    r = compute_rollup((resolved, control), now=0)
    assert r.state is RollupState.APPROVED
    assert r.open_exposure_count == 0


def test_rollup_valid_exception_suppresses_block():
    v = SecurityFinding.create(FindingKind.VULNERABILITY, "CVE", severity=Severity.CRITICAL)
    ex = SecurityFinding.create(
        FindingKind.EXCEPTION,
        "accept",
        state=FindingState.ACCEPTED,
        exception_of=v.finding_id,
        approver="ciso",
        expires=100,
    )
    r = compute_rollup((v, ex), now=50)
    assert r.state is RollupState.IN_PROGRESS  # exposure open but excepted -> not blocking
    assert r.blocking_count == 0
    assert r.valid_exception_count == 1


def test_rollup_expired_exception_reverts_to_blocked():
    v = SecurityFinding.create(FindingKind.VULNERABILITY, "CVE", severity=Severity.CRITICAL)
    ex = SecurityFinding.create(
        FindingKind.EXCEPTION,
        "accept",
        state=FindingState.ACCEPTED,
        exception_of=v.finding_id,
        approver="ciso",
        expires=100,
    )
    r = compute_rollup((v, ex), now=200)
    assert r.state is RollupState.BLOCKED
    assert r.blocking_count == 1
    assert r.expired_exception_count == 1


def test_rollup_requires_int_now():
    with pytest.raises(SecurityRollupError):
        compute_rollup((), now="later")  # type: ignore[arg-type]
    with pytest.raises(SecurityRollupError):
        compute_rollup((), now=True)


def test_rollup_is_deterministic():
    findings = (SecurityFinding.create(FindingKind.VULNERABILITY, "CVE", severity=Severity.HIGH),)
    assert compute_rollup(findings, now=5).rollup_id == compute_rollup(findings, now=5).rollup_id


def test_rollup_to_dict_never_enacts():
    r = compute_rollup((), now=0)
    assert r.to_dict()["enacts"] is False
    assert r.fingerprint() == compute_rollup((), now=0).fingerprint()


def test_security_rollup_create_is_content_addressed():
    r = SecurityRollup.create(
        state=RollupState.APPROVED,
        evaluated_at=0,
        open_exposure_count=0,
        blocking_count=0,
        in_progress_count=0,
        valid_exception_count=0,
        expired_exception_count=0,
        blocked_by=(),
    )
    assert r.rollup_id.startswith("UCOS-SRUP-")


# --------------------------------------------------------------------------- #
# SecurityIntelligenceService                                                  #
# --------------------------------------------------------------------------- #


def test_service_rejects_bad_ledger():
    with pytest.raises(SecurityFindingError):
        SecurityIntelligenceService(ledger="nope")  # type: ignore[arg-type]


def test_service_rejects_bad_events():
    with pytest.raises(SecurityFindingError):
        SecurityIntelligenceService(events="nope")  # type: ignore[arg-type]


def test_record_finding_records_and_emits_event():
    bus = EventBus()
    service = build_security_intelligence_service(events=bus)
    f = service.record_finding(
        FindingKind.VULNERABILITY, "CVE-2026-2", severity=Severity.HIGH, affects=("UCOS-SVC-1",)
    )
    assert f.finding_id in service.ledger
    events = bus.events_of(FINDING_RECORDED_EVENT)
    assert len(events) == 1
    assert events[0].payload["enacts"] is False
    assert events[0].payload["secret_leak"] is False


def test_record_finding_without_bus_is_silent_but_records():
    service = build_security_intelligence_service()
    f = service.record_finding(FindingKind.CONTROL, "AC-2")
    assert f.finding_id in service.ledger


def test_record_prebuilt_finding():
    service = build_security_intelligence_service()
    f = SecurityFinding.create(FindingKind.THREAT, "tampering", severity=Severity.MEDIUM)
    recorded = service.record(f)
    assert recorded.finding_id in service.ledger


def test_record_rejects_non_finding():
    service = build_security_intelligence_service()
    with pytest.raises(SecurityFindingError):
        service.record("nope")  # type: ignore[arg-type]


def test_secret_in_evidence_becomes_a_location_only_leak_finding():
    bus = EventBus()
    service = build_security_intelligence_service(events=bus)
    leak = service.record_finding(
        FindingKind.AUDIT_EVIDENCE,
        "config audit",
        evidence="password: hunter2secretvalue",
        affects=("UCOS-INF-000001",),
        location="deploy/config.yaml",
    )
    assert leak.identifier == SECRET_LEAK_IDENTIFIER
    assert leak.severity is Severity.CRITICAL
    assert "deploy/config.yaml" in leak.evidence
    assert "hunter2" not in leak.evidence  # the secret value is never stored
    assert scan_for_secret(leak.evidence) is False
    assert bus.events_of(FINDING_RECORDED_EVENT)[0].payload["secret_leak"] is True


def test_secret_in_name_uses_affects_as_location_when_unspecified():
    service = build_security_intelligence_service()
    leak = service.record_finding(
        FindingKind.VULNERABILITY, "AKIAIOSFODNN7EXAMPLE", affects=("UCOS-SVC-1", "UCOS-SVC-2")
    )
    assert leak.identifier == SECRET_LEAK_IDENTIFIER
    assert "UCOS-SVC-1|UCOS-SVC-2" in leak.evidence


def test_secret_leak_with_no_location_or_affects():
    service = build_security_intelligence_service()
    leak = service.record_finding(FindingKind.VULNERABILITY, "ghp_0123456789abcdefghijklmnop")
    assert leak.identifier == SECRET_LEAK_IDENTIFIER
    assert "unspecified" in leak.evidence


def test_rollup_through_service_emits_event():
    bus = EventBus()
    service = build_security_intelligence_service(events=bus)
    service.record_finding(FindingKind.VULNERABILITY, "CVE", severity=Severity.CRITICAL)
    r = service.rollup(now=10)
    assert r.state is RollupState.BLOCKED
    evs = bus.events_of(ROLLUP_EVALUATED_EVENT)
    assert len(evs) == 1
    assert evs[0].payload["rollup"]["state"] == "BLOCKED"


def test_rollup_through_service_without_bus():
    service = build_security_intelligence_service()
    r = service.rollup(now=10)
    assert r.state is RollupState.APPROVED


def test_trace_validate_and_validate_all_through_service():
    service = build_security_intelligence_service()
    f = service.record_finding(FindingKind.VULNERABILITY, "CVE", severity=Severity.LOW)
    assert service.trace(f.finding_id)["finding_id"] == f.finding_id
    assert service.validate(f.finding_id)["meta_valid"] is True
    agg = service.validate_all()
    assert agg["finding_count"] == 1
    assert agg["meta_valid"] is True


def test_report_is_deterministic_and_covers_vocabulary():
    def build() -> SecurityIntelligenceEvidence:
        service = build_security_intelligence_service()
        service.record_finding(FindingKind.VULNERABILITY, "CVE", severity=Severity.HIGH)
        service.record_finding(FindingKind.CONTROL, "AC-2")
        return service.report(now=0)

    a, b = build(), build()
    assert a.evidence_id == b.evidence_id
    assert a.evidence_id.startswith("UCOS-SIEV-")
    assert a.fingerprint() == b.fingerprint()
    assert a.finding_count == 2
    kinds = {name for name, _ in a.kind_counts}
    assert kinds == {k.value for k in FindingKind}
    severities = {name for name, _ in a.severity_counts}
    assert severities == {s.value for s in Severity}
    states = {name for name, _ in a.state_counts}
    assert states == {s.value for s in FindingState}
    assert a.rollup["state"] == "BLOCKED"


def test_service_to_dict_summary():
    service = build_security_intelligence_service()
    service.record_finding(FindingKind.VULNERABILITY, "CVE", severity=Severity.LOW)
    summary = service.to_dict(now=0)
    assert summary["ledger"]["finding_count"] == 1
    assert summary["evidence"]["evidence_id"].startswith("UCOS-SIEV-")


# --------------------------------------------------------------------------- #
# bootstrap_security_intelligence                                             #
# --------------------------------------------------------------------------- #


def test_bootstrap_composes_and_publishes_contracts():
    context = bootstrap_platform()
    service = bootstrap_security_intelligence(context)
    assert isinstance(service, SecurityIntelligenceService)
    for ref in SECURITY_INTELLIGENCE_CONTRACTS:
        assert ref.name in context.services


def test_bootstrap_emits_completion_event():
    context = bootstrap_platform()
    bootstrap_security_intelligence(context)
    events = context.events.events_of(SECURITY_INTELLIGENCE_BOOTSTRAP_EVENT)
    assert len(events) == 1
    assert set(events[0].payload["intelligence_contracts"]) == {
        r.name for r in SECURITY_INTELLIGENCE_CONTRACTS
    }


def test_bootstrap_is_idempotent_on_contract_registration():
    context = bootstrap_platform()
    bootstrap_security_intelligence(context)
    bootstrap_security_intelligence(context)
    for ref in SECURITY_INTELLIGENCE_CONTRACTS:
        assert ref.name in context.services


def test_bootstrapped_service_records_end_to_end():
    context = bootstrap_platform()
    service = bootstrap_security_intelligence(context)
    f = service.record_finding(FindingKind.VULNERABILITY, "CVE", severity=Severity.HIGH)
    assert f.finding_id in service.ledger
    # the finding-recorded event flows through the platform bus for L8 audit.
    assert len(context.events.events_of(FINDING_RECORDED_EVENT)) == 1


def test_bootstrap_is_fail_closed_on_bad_context():
    class _BadContext:
        pass

    with pytest.raises(SecurityBootstrapError):
        bootstrap_security_intelligence(_BadContext())


def test_bootstrap_reraises_a_security_bootstrap_error_without_double_wrapping(monkeypatch):
    import platform.security.bootstrap as boot

    sentinel = SecurityBootstrapError("inner intelligence failure")

    def _raise(*_args, **_kwargs):
        raise sentinel

    monkeypatch.setattr(boot, "build_security_intelligence_service", _raise, raising=True)
    context = bootstrap_platform()
    with pytest.raises(SecurityBootstrapError) as excinfo:
        bootstrap_security_intelligence(context)
    assert excinfo.value is sentinel


def test_intelligence_contract_requires_a_name():
    from platform.security.contracts import security_intelligence_contract
    from platform.security.errors import SecurityContractError

    with pytest.raises(SecurityContractError):
        security_intelligence_contract("")
