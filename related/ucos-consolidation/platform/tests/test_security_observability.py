"""EC2-CAP-SEC-001 / SEC-OBS — Security Observability Runtime tests.

Covers the `security`-dimension signal model, reverse-traceability enforcement
(UMB-015 §5), the append-only signal ledger, telemetry shaping THROUGH the certified
L8 ObservabilityService (no second telemetry stack), deterministic evidence,
governed-event emission, and the bootstrap composition.
"""

from __future__ import annotations

from platform.foundation.bootstrap import bootstrap_platform
from platform.foundation.events import EventBus
from platform.observability.service import build_observability_service
from platform.security.bootstrap import (
    SECURITY_OBSERVABILITY_BOOTSTRAP_EVENT,
    bootstrap_security_observability,
)
from platform.security.contracts import (
    SECURITY_OBSERVABILITY_CONTRACTS,
    SECURITY_SIGNAL_DIMENSION,
    RollupState,
)
from platform.security.errors import (
    SecurityBootstrapError,
    SecurityObservabilityError,
    SecuritySignalError,
    SignalTraceabilityError,
)
from platform.security.intelligence import (
    FindingKind,
    Severity,
    build_security_intelligence_service,
)
from platform.security.observability import (
    SECURITY_SIGNAL_AUDIT_ACTION,
    SECURITY_SIGNAL_EMITTED_EVENT,
    SECURITY_SIGNAL_METRIC,
    SecuritySignal,
    SignalLedger,
    build_security_observability_service,
)

import pytest

# --------------------------------------------------------------------------- #
# SecuritySignal                                                               #
# --------------------------------------------------------------------------- #


def test_signal_is_on_the_existing_security_dimension_and_deterministic():
    a = SecuritySignal.create(
        RollupState.BLOCKED,
        "UCOS-SVC-1",
        traces_to="UCOS-SFND-1",
        emitted_at=1,
        metrics={"blocking": 2},
    )
    b = SecuritySignal.create(
        RollupState.BLOCKED,
        "UCOS-SVC-1",
        traces_to="UCOS-SFND-1",
        emitted_at=1,
        metrics={"blocking": 2},
    )
    assert a.signal_id == b.signal_id
    assert a.signal_id.startswith("UCOS-SSIG-")
    assert a.dimension == SECURITY_SIGNAL_DIMENSION == "security"
    assert a.reverse_traceable is True


def test_signal_rejects_bad_state():
    with pytest.raises(SecuritySignalError):
        SecuritySignal.create("BLOCKED", "UCOS-SVC-1", traces_to="UCOS-SFND-1", emitted_at=1)  # type: ignore[arg-type]


def test_signal_rejects_empty_subject():
    with pytest.raises(SecuritySignalError):
        SecuritySignal.create(RollupState.APPROVED, "  ", traces_to="UCOS-SFND-1", emitted_at=1)


def test_signal_requires_reverse_trace():
    with pytest.raises(SignalTraceabilityError):
        SecuritySignal.create(RollupState.APPROVED, "UCOS-SVC-1", traces_to="", emitted_at=1)


def test_signal_rejects_bad_tick():
    with pytest.raises(SecuritySignalError):
        SecuritySignal.create(
            RollupState.APPROVED,
            "UCOS-SVC-1",
            traces_to="UCOS-SFND-1",
            emitted_at="now",  # type: ignore[arg-type]
        )


def test_signal_rejects_non_int_metric_value():
    with pytest.raises(SecuritySignalError):
        SecuritySignal.create(
            RollupState.APPROVED,
            "UCOS-SVC-1",
            traces_to="UCOS-SFND-1",
            emitted_at=1,
            metrics={"x": "two"},  # type: ignore[dict-item]
        )


def test_signal_rejects_secret_in_field():
    with pytest.raises(SecuritySignalError):
        SecuritySignal.create(
            RollupState.APPROVED, "UCOS-SVC-1", traces_to="password: supersecretvalue", emitted_at=1
        )


def test_signal_trace_and_dict():
    sig = SecuritySignal.create(
        RollupState.IN_PROGRESS, "UCOS-SVC-1", traces_to="UCOS-SRUP-1", emitted_at=3
    )
    t = sig.trace()
    assert t["traces_to"] == "UCOS-SRUP-1"
    assert t["dimension"] == "security"
    assert sig.to_dict()["state"] == "IN_PROGRESS"
    assert (
        sig.fingerprint()
        == SecuritySignal.create(
            RollupState.IN_PROGRESS, "UCOS-SVC-1", traces_to="UCOS-SRUP-1", emitted_at=3
        ).fingerprint()
    )


# --------------------------------------------------------------------------- #
# SignalLedger                                                                 #
# --------------------------------------------------------------------------- #


def test_ledger_append_only_idempotent_and_queries():
    ledger = SignalLedger()
    sig = SecuritySignal.create(
        RollupState.BLOCKED, "UCOS-SVC-1", traces_to="UCOS-SFND-1", emitted_at=1
    )
    ledger.record(sig)
    ledger.record(sig)
    assert len(ledger) == 1
    assert sig.signal_id in ledger
    assert ledger.get(sig.signal_id) is sig
    assert ledger.by_state(RollupState.BLOCKED) == (sig,)
    assert ledger.by_subject("UCOS-SVC-1") == (sig,)
    assert ledger.tracing_to("UCOS-SFND-1") == (sig,)
    assert isinstance(ledger.fingerprint(), str)
    assert ledger.to_dict()["signal_count"] == 1


def test_ledger_rejects_non_signal():
    with pytest.raises(SecuritySignalError):
        SignalLedger().record("nope")  # type: ignore[arg-type]


def test_ledger_refuses_a_non_reverse_traceable_signal():
    # A directly-constructed signal that bypasses create() (no traces_to) is refused.
    bad = SecuritySignal(
        dimension="security",
        state=RollupState.APPROVED,
        subject_ref="UCOS-SVC-1",
        traces_to="",
        emitted_at=1,
        signal_id="UCOS-SSIG-bad",
    )
    with pytest.raises(SignalTraceabilityError):
        SignalLedger().record(bad)


def test_ledger_get_missing_raises():
    with pytest.raises(SecuritySignalError):
        SignalLedger().get("UCOS-SSIG-missing")


# --------------------------------------------------------------------------- #
# SecurityObservabilityService (reuses L8; no second telemetry stack)          #
# --------------------------------------------------------------------------- #


def test_service_requires_a_certified_l8_layer():
    with pytest.raises(SecurityObservabilityError):
        build_security_observability_service(observability="nope")  # type: ignore[arg-type]


def test_service_rejects_bad_ledger_and_events():
    from platform.security.observability import SecurityObservabilityService

    obs = build_observability_service()
    with pytest.raises(SecurityObservabilityError):
        SecurityObservabilityService(observability=obs, ledger="nope")  # type: ignore[arg-type]
    with pytest.raises(SecurityObservabilityError):
        SecurityObservabilityService(observability=obs, events="nope")  # type: ignore[arg-type]


def test_emit_signal_shapes_l8_telemetry():
    obs = build_security_observability_service()
    sig = obs.emit_signal(
        RollupState.BLOCKED,
        "UCOS-SVC-1",
        traces_to="UCOS-SFND-1",
        emitted_at=1,
        metrics={"blocking": 1},
    )
    assert sig.signal_id in obs.ledger
    # telemetry flows THROUGH the L8 layer: metric + log + audit.
    assert (
        obs.observability.metrics.value_of(
            SECURITY_SIGNAL_METRIC, dimension="security", state="BLOCKED"
        )
        == 1.0
    )
    assert len(obs.observability.audit) == 1
    assert obs.observability.audit.events[0].action == SECURITY_SIGNAL_AUDIT_ACTION
    assert obs.telemetered_count == 1
    assert obs.telemetry_complete() is True


def test_emit_signal_emits_governed_event_when_bound():
    bus = EventBus()
    obs = build_security_observability_service(events=bus)
    obs.emit_signal(RollupState.APPROVED, "UCOS-SVC-1", traces_to="UCOS-SFND-1", emitted_at=1)
    evs = bus.events_of(SECURITY_SIGNAL_EMITTED_EVENT)
    assert len(evs) == 1
    assert evs[0].payload["enacts"] is False


def test_observe_rollup_maps_state_and_metrics():
    intel = build_security_intelligence_service()
    intel.record_finding(
        FindingKind.VULNERABILITY, "CVE", severity=Severity.CRITICAL, affects=("UCOS-SVC-1",)
    )
    rollup = intel.rollup(now=7)
    obs = build_security_observability_service()
    sig = obs.observe_rollup(rollup, "UCOS-SVC-1")
    assert sig.state is RollupState.BLOCKED
    assert sig.traces_to == rollup.rollup_id  # reverse-traceable to the roll-up
    assert sig.emitted_at == 7  # uses the roll-up's logical tick (no wall-clock)
    assert dict(sig.metrics)["blocking"] == 1


def test_observe_rollup_accepts_explicit_scan_reference():
    intel = build_security_intelligence_service()
    rollup = intel.rollup(now=0)
    obs = build_security_observability_service()
    sig = obs.observe_rollup(rollup, "UCOS-SVC-1", traces_to="scan:trivy#42")
    assert sig.traces_to == "scan:trivy#42"


def test_observe_rollup_rejects_non_rollup():
    obs = build_security_observability_service()
    with pytest.raises(SecurityObservabilityError):
        obs.observe_rollup("nope", "UCOS-SVC-1")  # type: ignore[arg-type]


def test_trace_validate_all_and_report():
    obs = build_security_observability_service()
    sig = obs.emit_signal(RollupState.BLOCKED, "UCOS-SVC-1", traces_to="UCOS-SFND-1", emitted_at=1)
    assert obs.trace(sig.signal_id)["traces_to"] == "UCOS-SFND-1"
    v = obs.validate_all()
    assert v["signal_count"] == 1
    assert v["all_reverse_traceable"] is True
    assert v["telemetry_complete"] is True
    report = obs.report()
    assert report.evidence_id.startswith("UCOS-SOEV-")
    assert report.telemetry_complete is True
    assert report.signal_count == 1
    states = {name for name, _ in report.state_counts}
    assert states == {s.value for s in RollupState}
    assert obs.to_dict()["telemetry_complete"] is True


def test_trace_missing_signal_raises():
    obs = build_security_observability_service()
    with pytest.raises(SecuritySignalError):
        obs.trace("UCOS-SSIG-missing")


def test_report_is_deterministic():
    def build() -> str:
        obs = build_security_observability_service()
        obs.emit_signal(RollupState.APPROVED, "UCOS-SVC-1", traces_to="UCOS-SFND-1", emitted_at=1)
        return obs.report().fingerprint()

    assert build() == build()


def test_reuses_l8_layer_by_reference():
    l8 = build_observability_service()
    obs = build_security_observability_service(observability=l8)
    assert obs.observability is l8


# --------------------------------------------------------------------------- #
# bootstrap_security_observability                                             #
# --------------------------------------------------------------------------- #


def test_bootstrap_composes_and_publishes_contracts():
    context = bootstrap_platform()
    from platform.security.observability import SecurityObservabilityService

    service = bootstrap_security_observability(context)
    assert isinstance(service, SecurityObservabilityService)
    for ref in SECURITY_OBSERVABILITY_CONTRACTS:
        assert ref.name in context.services


def test_bootstrap_emits_completion_event():
    context = bootstrap_platform()
    bootstrap_security_observability(context)
    events = context.events.events_of(SECURITY_OBSERVABILITY_BOOTSTRAP_EVENT)
    assert len(events) == 1
    assert events[0].payload["signal_dimension"] == "security"


def test_bootstrap_accepts_a_prebuilt_l8_layer():
    context = bootstrap_platform()
    l8 = build_observability_service(events=context.events)
    service = bootstrap_security_observability(context, observability=l8)
    assert service.observability is l8


def test_bootstrap_is_idempotent():
    context = bootstrap_platform()
    bootstrap_security_observability(context)
    bootstrap_security_observability(context)
    for ref in SECURITY_OBSERVABILITY_CONTRACTS:
        assert ref.name in context.services


def test_bootstrapped_service_records_end_to_end():
    context = bootstrap_platform()
    service = bootstrap_security_observability(context)
    service.emit_signal(RollupState.BLOCKED, "UCOS-SVC-1", traces_to="UCOS-SFND-1", emitted_at=1)
    assert len(context.events.events_of(SECURITY_SIGNAL_EMITTED_EVENT)) == 1


def test_bootstrap_is_fail_closed_on_bad_context():
    class _BadContext:
        pass

    with pytest.raises(SecurityBootstrapError):
        bootstrap_security_observability(_BadContext())


def test_bootstrap_reraises_a_security_bootstrap_error_without_double_wrapping(monkeypatch):
    import platform.security.bootstrap as boot

    sentinel = SecurityBootstrapError("inner observability failure")

    def _raise(*_args, **_kwargs):
        raise sentinel

    monkeypatch.setattr(boot, "build_security_observability_service", _raise, raising=True)
    context = bootstrap_platform()
    with pytest.raises(SecurityBootstrapError) as excinfo:
        bootstrap_security_observability(context)
    assert excinfo.value is sentinel


def test_observability_contract_requires_a_name():
    from platform.security.contracts import security_observability_contract
    from platform.security.errors import SecurityContractError

    with pytest.raises(SecurityContractError):
        security_observability_contract("")
