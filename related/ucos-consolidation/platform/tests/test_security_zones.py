"""EC2-CAP-SEC-001 / SEC-ZONE — Zone & Control Posture Runtime tests.

Covers the UMB-015 five-zone / seven-control posture model, the zone mutation-direction
invariant (UMB-INV-01), the policy-configured (non-compiled) extensibility, the
append-only posture ledger, deterministic evidence, governed-event emission, and the
bootstrap composition.
"""

from __future__ import annotations

from platform.foundation.bootstrap import bootstrap_platform
from platform.foundation.events import EventBus
from platform.security.bootstrap import (
    SECURITY_ZONE_BOOTSTRAP_EVENT,
    bootstrap_security_zone,
)
from platform.security.contracts import (
    SECURITY_ZONE_CONTRACTS,
    RollupState,
    SecurityControl,
    SecurityZone,
)
from platform.security.errors import (
    SecurityBootstrapError,
    SecurityZoneError,
    ZoneMutationError,
    ZonePostureError,
)
from platform.security.zones import (
    POSTURE_RECORDED_EVENT,
    POSTURE_TARGET_CONTROL,
    POSTURE_TARGET_ZONE,
    PostureLedger,
    PostureRecord,
    SecurityZoneEvidence,
    SecurityZoneService,
    build_security_zone_service,
    zone_may_mutate,
)

import pytest

# --------------------------------------------------------------------------- #
# zone_may_mutate (UMB-INV-01)                                                 #
# --------------------------------------------------------------------------- #


def test_lower_zone_may_not_mutate_inward():
    r = zone_may_mutate(SecurityZone.CONSUMPTION, SecurityZone.CORE)
    assert r["may_mutate"] is False
    assert r["enacts"] is False
    assert "canon" in r["reason"]


def test_core_may_mutate_outward():
    r = zone_may_mutate(SecurityZone.CORE, SecurityZone.CONSUMPTION)
    assert r["may_mutate"] is True


def test_same_zone_may_mutate():
    r = zone_may_mutate(SecurityZone.ENGINEERING, SecurityZone.ENGINEERING)
    assert r["may_mutate"] is True


def test_engineering_may_not_mutate_governance_inward():
    r = zone_may_mutate(SecurityZone.ENGINEERING, SecurityZone.GOVERNANCE)
    assert r["may_mutate"] is False
    assert "inward" in r["reason"]


def test_operations_to_consumption_is_permitted_outward():
    # ZONE-3 -> ZONE-4 is outward (target not canon); permitted.
    r = zone_may_mutate(SecurityZone.OPERATIONS, SecurityZone.CONSUMPTION)
    assert r["may_mutate"] is True


def test_zone_may_mutate_rejects_bad_types():
    with pytest.raises(ZoneMutationError):
        zone_may_mutate("ZONE-0", SecurityZone.CORE)  # type: ignore[arg-type]


# --------------------------------------------------------------------------- #
# PostureRecord                                                                #
# --------------------------------------------------------------------------- #


def test_posture_for_zone_is_deterministic_and_non_enacting():
    a = PostureRecord.for_zone(
        SecurityZone.CORE, RollupState.APPROVED, rationale="append-only via T", evaluated_at=1
    )
    b = PostureRecord.for_zone(
        SecurityZone.CORE, RollupState.APPROVED, rationale="append-only via T", evaluated_at=1
    )
    assert a.posture_id == b.posture_id
    assert a.posture_id.startswith("UCOS-SZON-")
    assert a.target_kind == POSTURE_TARGET_ZONE
    assert a.target == "ZONE-0"
    assert a.non_enacting is True


def test_posture_for_control():
    p = PostureRecord.for_control(
        SecurityControl.AUDIT, RollupState.APPROVED, rationale="hash-chained", evaluated_at=1
    )
    assert p.target_kind == POSTURE_TARGET_CONTROL
    assert p.target == "audit-control"


def test_posture_create_rejects_bad_target_kind():
    with pytest.raises(ZonePostureError):
        PostureRecord.create(
            "universe", "ZONE-0", RollupState.APPROVED, rationale="r", evaluated_at=1
        )


def test_posture_create_rejects_empty_target_and_rationale_and_bad_tick():
    OK = RollupState.APPROVED
    with pytest.raises(ZonePostureError):
        PostureRecord.create(POSTURE_TARGET_ZONE, "  ", OK, rationale="r", evaluated_at=1)
    with pytest.raises(ZonePostureError):
        PostureRecord.create(POSTURE_TARGET_ZONE, "ZONE-0", OK, rationale=" ", evaluated_at=1)
    with pytest.raises(ZonePostureError):
        PostureRecord.create(
            POSTURE_TARGET_ZONE,
            "ZONE-0",
            "APPROVED",
            rationale="r",
            evaluated_at=1,  # type: ignore[arg-type]
        )
    with pytest.raises(ZonePostureError):
        PostureRecord.create(POSTURE_TARGET_ZONE, "ZONE-0", OK, rationale="r", evaluated_at=True)


def test_posture_create_rejects_secret():
    with pytest.raises(ZonePostureError):
        PostureRecord.create(
            POSTURE_TARGET_ZONE,
            "ZONE-0",
            RollupState.APPROVED,
            rationale="token=abcdef1234567890",
            evaluated_at=1,
        )


def test_for_zone_and_for_control_reject_bad_types():
    OK = RollupState.APPROVED
    with pytest.raises(ZonePostureError):
        PostureRecord.for_zone("ZONE-0", OK, rationale="r", evaluated_at=1)  # type: ignore[arg-type]
    with pytest.raises(ZonePostureError):
        PostureRecord.for_control("audit", OK, rationale="r", evaluated_at=1)  # type: ignore[arg-type]


def test_posture_validate_trace_and_dict():
    p = PostureRecord.for_zone(
        SecurityZone.OPERATIONS,
        RollupState.IN_PROGRESS,
        rationale="append-only signal write",
        evaluated_at=2,
        evidence_refs=("UCOS-SSIG-1",),
    )
    assert p.validate()["meta_valid"] is True
    t = p.trace()
    assert t["backward"]["source_ref"] == "UMB-015 §1"
    assert t["evidence_refs"] == ["UCOS-SSIG-1"]
    control = PostureRecord.for_control(
        SecurityControl.ACCESS, RollupState.APPROVED, rationale="zone membership", evaluated_at=2
    )
    assert control.trace()["backward"]["source_ref"] == "UMB-015 §2"
    assert p.to_dict()["non_enacting"] is True
    assert p.fingerprint() == p.fingerprint()


# --------------------------------------------------------------------------- #
# PostureLedger                                                                #
# --------------------------------------------------------------------------- #


def test_posture_validate_fails_on_hand_built_unidentified_record():
    # A directly-constructed record bypassing create() fails meta-validity.
    bad = PostureRecord(
        target_kind=POSTURE_TARGET_ZONE,
        target="ZONE-0",
        posture=RollupState.APPROVED,
        rationale="r",
        evaluated_at=1,
        posture_id="BAD-ID",
    )
    with pytest.raises(ZonePostureError):
        bad.validate()


def test_ledger_append_only_idempotent_and_queries():
    ledger = PostureLedger()
    p = PostureRecord.for_zone(
        SecurityZone.CORE, RollupState.APPROVED, rationale="r", evaluated_at=1
    )
    ledger.record(p)
    ledger.record(p)
    assert len(ledger) == 1
    assert p.posture_id in ledger
    assert ledger.get(p.posture_id) is p
    assert ledger.by_kind(POSTURE_TARGET_ZONE) == (p,)
    assert ledger.by_target("ZONE-0") == (p,)
    assert ledger.by_posture(RollupState.APPROVED) == (p,)
    assert isinstance(ledger.fingerprint(), str)
    assert ledger.to_dict()["posture_count"] == 1


def test_ledger_rejects_non_posture_and_missing_get():
    with pytest.raises(ZonePostureError):
        PostureLedger().record("nope")  # type: ignore[arg-type]
    with pytest.raises(ZonePostureError):
        PostureLedger().get("UCOS-SZON-missing")


# --------------------------------------------------------------------------- #
# SecurityZoneService                                                          #
# --------------------------------------------------------------------------- #


def test_service_rejects_bad_ledger_and_events():
    with pytest.raises(SecurityZoneError):
        SecurityZoneService(ledger="nope")  # type: ignore[arg-type]
    with pytest.raises(SecurityZoneError):
        SecurityZoneService(events="nope")  # type: ignore[arg-type]


def test_service_exposes_five_zones_and_seven_controls():
    service = build_security_zone_service()
    assert len(service.zone_policies()) == 5
    assert len(service.control_policies()) == 7
    zones = {z["zone"] for z in service.zone_policies()}
    assert zones == {z.value for z in SecurityZone}
    controls = {c["control"] for c in service.control_policies()}
    assert controls == {c.value for c in SecurityControl}


def test_assess_zone_records_and_emits_event():
    bus = EventBus()
    service = build_security_zone_service(events=bus)
    p = service.assess_zone(
        SecurityZone.CORE, RollupState.APPROVED, rationale="append-only via T", evaluated_at=1
    )
    assert p.posture_id in service.ledger
    evs = bus.events_of(POSTURE_RECORDED_EVENT)
    assert len(evs) == 1
    assert evs[0].payload["enacts"] is False


def test_assess_control_and_generic_assess_without_bus():
    service = build_security_zone_service()
    service.assess_control(
        SecurityControl.AUDIT, RollupState.APPROVED, rationale="hash-chained", evaluated_at=1
    )
    # generic assess against a free-form FUTURE target (policy-configured, not compiled).
    future = service.assess(
        POSTURE_TARGET_ZONE,
        "ZONE-5-FUTURE",
        RollupState.IN_PROGRESS,
        rationale="future zone",
        evaluated_at=1,
    )
    assert future.target == "ZONE-5-FUTURE"
    assert len(service.ledger) == 2


def test_evaluate_mutation_through_service():
    service = build_security_zone_service()
    inward = service.evaluate_mutation(SecurityZone.CONSUMPTION, SecurityZone.CORE)
    outward = service.evaluate_mutation(SecurityZone.CORE, SecurityZone.OPERATIONS)
    assert inward["may_mutate"] is False
    assert outward["may_mutate"] is True


def test_trace_validate_validate_all_and_report():
    service = build_security_zone_service()
    p = service.assess_zone(SecurityZone.CORE, RollupState.APPROVED, rationale="r", evaluated_at=1)
    service.assess_control(
        SecurityControl.AUDIT, RollupState.APPROVED, rationale="r", evaluated_at=1
    )
    assert service.trace(p.posture_id)["posture_id"] == p.posture_id
    assert service.validate(p.posture_id)["meta_valid"] is True
    agg = service.validate_all()
    assert agg["posture_count"] == 2
    assert agg["meta_valid"] is True
    report = service.report()
    assert report.evidence_id.startswith("UCOS-SZEV-")
    assert report.zones_assessed == 1
    assert report.controls_assessed == 1
    assert report.posture_count == 2
    postures = {name for name, _ in report.posture_counts}
    assert postures == {s.value for s in RollupState}
    summary = service.to_dict()
    assert len(summary["zone_policies"]) == 5
    assert len(summary["control_policies"]) == 7


def test_report_counts_only_canonical_targets_for_coverage():
    service = build_security_zone_service()
    # a free-form future target is recorded but not counted as a canonical zone assessed.
    service.assess(
        POSTURE_TARGET_ZONE, "ZONE-9-CUSTOM", RollupState.APPROVED, rationale="r", evaluated_at=1
    )
    report = service.report()
    assert report.zones_assessed == 0
    assert report.posture_count == 1


def test_report_is_deterministic():
    def build() -> SecurityZoneEvidence:
        service = build_security_zone_service()
        service.assess_zone(SecurityZone.CORE, RollupState.APPROVED, rationale="r", evaluated_at=1)
        return service.report()

    assert build().evidence_id == build().evidence_id
    assert build().fingerprint() == build().fingerprint()


# --------------------------------------------------------------------------- #
# bootstrap_security_zone                                                      #
# --------------------------------------------------------------------------- #


def test_bootstrap_composes_and_publishes_contracts():
    context = bootstrap_platform()
    service = bootstrap_security_zone(context)
    assert isinstance(service, SecurityZoneService)
    for ref in SECURITY_ZONE_CONTRACTS:
        assert ref.name in context.services


def test_bootstrap_emits_completion_event():
    context = bootstrap_platform()
    bootstrap_security_zone(context)
    events = context.events.events_of(SECURITY_ZONE_BOOTSTRAP_EVENT)
    assert len(events) == 1
    assert events[0].payload["zone_count"] == 5
    assert events[0].payload["control_count"] == 7


def test_bootstrap_is_idempotent():
    context = bootstrap_platform()
    bootstrap_security_zone(context)
    bootstrap_security_zone(context)
    for ref in SECURITY_ZONE_CONTRACTS:
        assert ref.name in context.services


def test_bootstrapped_service_records_end_to_end():
    context = bootstrap_platform()
    service = bootstrap_security_zone(context)
    service.assess_zone(SecurityZone.CORE, RollupState.APPROVED, rationale="r", evaluated_at=1)
    assert len(context.events.events_of(POSTURE_RECORDED_EVENT)) == 1


def test_bootstrap_is_fail_closed_on_bad_context():
    class _BadContext:
        pass

    with pytest.raises(SecurityBootstrapError):
        bootstrap_security_zone(_BadContext())


def test_bootstrap_reraises_a_security_bootstrap_error_without_double_wrapping(monkeypatch):
    import platform.security.bootstrap as boot

    sentinel = SecurityBootstrapError("inner zone failure")

    def _raise(*_args, **_kwargs):
        raise sentinel

    monkeypatch.setattr(boot, "build_security_zone_service", _raise, raising=True)
    context = bootstrap_platform()
    with pytest.raises(SecurityBootstrapError) as excinfo:
        bootstrap_security_zone(context)
    assert excinfo.value is sentinel


def test_zone_contract_requires_a_name():
    from platform.security.contracts import security_zone_contract
    from platform.security.errors import SecurityContractError

    with pytest.raises(SecurityContractError):
        security_zone_contract("")
