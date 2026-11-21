"""EC2-CAP-SEC-001 / SEC-OBS — Security Observability Runtime (security signal + telemetry).

The **Security Observability Runtime** (Phase 4) emits the **existing** ``security``
signal dimension and shapes security telemetry **through the certified L8 Observability
Layer** (`platform.observability.ObservabilityService`) — it creates **no** new signal
dimension and **no** second telemetry stack (ARCH-SECURITY-001 §15; determination §6.1/§9).
It adds only the security-specific *signal shaping* the L8 layer does not itself provide:
mapping an evidence-derived security state to a ``security``-dimension
:class:`SecuritySignal`, recording it as an L8 metric + structured log + append-only audit
event, and preserving **reverse-traceability** to the finding/scan that raised it
(UMB-015 §5).

Every security signal MUST carry a ``traces_to`` reference (the SEC-INTEL finding id,
roll-up id, or scan id) — a signal that is not reverse-traceable **fails** (PL-02;
UMB-015 §5). The runtime records only; it authorizes, ratifies, and enacts nothing
(RG-02 / AR-04), stores no secret value (SEC-04 / RR-07), and writes nothing to the
frozen corpus (DP-03).

Determinism (IMP-007 §5): all time inputs are caller-supplied logical ticks; signal ids
and evidence fingerprints are content-addressed, so the same emissions yield the same
:class:`SecurityObservabilityEvidence`.
"""

from __future__ import annotations

from dataclasses import dataclass
from platform.foundation.contracts import content_hash
from platform.foundation.events import EventBus
from platform.observability.service import (
    ObservabilityService,
    build_observability_service,
)
from platform.security.contracts import (
    SECURITY_SIGNAL_DIMENSION,
    RollupState,
)
from platform.security.errors import (
    SecurityObservabilityError,
    SecuritySignalError,
    SignalTraceabilityError,
)
from platform.security.intelligence import SecurityRollup, scan_for_secret
from typing import Any

#: The governed event emitted for every shaped security signal (PC-16; §15).
SECURITY_SIGNAL_EMITTED_EVENT = "security.observability.signal.emitted"

#: The L8 metric name incremented once per shaped security signal (through L8 metrics).
SECURITY_SIGNAL_METRIC = "security.signals"

#: The L8 audit action recorded for every shaped security signal (through L8 audit).
SECURITY_SIGNAL_AUDIT_ACTION = "security-signal-emitted"


@dataclass(frozen=True, slots=True)
class SecuritySignal:
    """An immutable, reverse-traceable ``security``-dimension signal (record-only).

    Records that a ``subject_ref`` bears a security roll-up ``state`` on the existing
    ``security`` dimension, derived from evidence and reverse-traceable to the
    finding/scan/roll-up that raised it (``traces_to``; UMB-015 §5). ``metrics`` is a
    sorted evaluative breakdown (e.g. blocking/in-progress counts). ``emitted_at`` is a
    caller-supplied logical tick. ``signal_id`` is content-addressed (``UCOS-SSIG-``).
    """

    dimension: str
    state: RollupState
    subject_ref: str
    traces_to: str
    emitted_at: int
    metrics: tuple[tuple[str, int], ...] = ()
    signal_id: str = ""

    @classmethod
    def create(
        cls,
        state: RollupState,
        subject_ref: str,
        *,
        traces_to: str,
        emitted_at: int,
        metrics: dict[str, int] | None = None,
    ) -> SecuritySignal:
        """Build a security signal with a deterministic id, fail-closed on any violation."""
        if not isinstance(state, RollupState):
            raise SecuritySignalError("security signal state must be a RollupState")
        if not isinstance(subject_ref, str) or not subject_ref.strip():
            raise SecuritySignalError("security signal requires a non-empty subject_ref")
        # Reverse-traceability is mandatory (UMB-015 §5; PL-02).
        if not isinstance(traces_to, str) or not traces_to.strip():
            raise SignalTraceabilityError(
                "security signal is not reverse-traceable to a finding/scan (traces_to required)",
                subject_ref=subject_ref,
            )
        if not isinstance(emitted_at, int) or isinstance(emitted_at, bool):
            raise SecuritySignalError("security signal requires a logical tick emitted_at")
        metric_items = metrics or {}
        for key, value in metric_items.items():
            if not isinstance(value, int) or isinstance(value, bool):
                raise SecuritySignalError(
                    "security signal metric values must be integers", metric=str(key)
                )
        # Secret defense (SEC-04 / RR-07): no secret value may enter a signal.
        if scan_for_secret(subject_ref) or scan_for_secret(traces_to):
            raise SecuritySignalError("security signal rejected: a field matched a secret pattern")
        metrics_t = tuple(sorted((str(k), int(v)) for k, v in metric_items.items()))
        core = {
            "dimension": SECURITY_SIGNAL_DIMENSION,
            "state": state.value,
            "subject_ref": subject_ref,
            "traces_to": traces_to,
            "emitted_at": emitted_at,
            "metrics": [list(m) for m in metrics_t],
        }
        return cls(
            dimension=SECURITY_SIGNAL_DIMENSION,
            state=state,
            subject_ref=subject_ref,
            traces_to=traces_to,
            emitted_at=emitted_at,
            metrics=metrics_t,
            signal_id=f"UCOS-SSIG-{content_hash(core)[:16]}",
        )

    @property
    def reverse_traceable(self) -> bool:
        """True iff the signal carries a reverse-trace reference (UMB-015 §5)."""
        return bool(self.traces_to and self.traces_to.strip())

    def trace(self) -> dict[str, Any]:
        """Return the reverse-traceability chain (signal → finding/scan that raised it)."""
        return {
            "signal_id": self.signal_id,
            "dimension": self.dimension,
            "subject": self.subject_ref,
            "traces_to": self.traces_to,
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "signal_id": self.signal_id,
            "dimension": self.dimension,
            "state": self.state.value,
            "subject_ref": self.subject_ref,
            "traces_to": self.traces_to,
            "emitted_at": self.emitted_at,
            "metrics": [list(m) for m in self.metrics],
        }

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())


class SignalLedger:
    """SEC-OBS's deterministic, append-only record of shaped security signals.

    Idempotent by ``signal_id``; queryable by state / subject / trace reference. Not a
    telemetry stack (that is L8's); it records *which* security signals were shaped so
    coverage (100% of security actions telemetered) is provable.
    """

    __slots__ = ("_entries", "_index")

    def __init__(self) -> None:
        self._entries: list[SecuritySignal] = []
        self._index: dict[str, int] = {}

    def record(self, signal: SecuritySignal) -> SecuritySignal:
        """Append a signal (idempotent by id); returns the stored entry."""
        if not isinstance(signal, SecuritySignal):
            raise SecuritySignalError("only a SecuritySignal may be recorded")
        if not signal.reverse_traceable:
            raise SignalTraceabilityError(
                "refusing to record a non-reverse-traceable signal", signal_id=signal.signal_id
            )
        existing = self._index.get(signal.signal_id)
        if existing is not None:
            return self._entries[existing]
        self._index[signal.signal_id] = len(self._entries)
        self._entries.append(signal)
        return signal

    @property
    def signals(self) -> tuple[SecuritySignal, ...]:
        return tuple(self._entries)

    def __len__(self) -> int:
        return len(self._entries)

    def __contains__(self, signal_id: str) -> bool:
        return signal_id in self._index

    def get(self, signal_id: str) -> SecuritySignal:
        """Return a recorded signal by id (raises if absent)."""
        idx = self._index.get(signal_id)
        if idx is None:
            raise SecuritySignalError("no such signal", signal_id=signal_id)
        return self._entries[idx]

    def by_state(self, state: RollupState) -> tuple[SecuritySignal, ...]:
        return tuple(s for s in self._entries if s.state is state)

    def by_subject(self, subject_ref: str) -> tuple[SecuritySignal, ...]:
        return tuple(s for s in self._entries if s.subject_ref == subject_ref)

    def tracing_to(self, ref: str) -> tuple[SecuritySignal, ...]:
        return tuple(s for s in self._entries if s.traces_to == ref)

    def fingerprint(self) -> str:
        return content_hash([s.to_dict() for s in self._entries])

    def to_dict(self) -> dict[str, Any]:
        return {"signal_count": len(self._entries), "signals": [s.to_dict() for s in self._entries]}


@dataclass(frozen=True, slots=True)
class SecurityObservabilityEvidence:
    """A deterministic, content-addressed report over shaped security signals (``UCOS-SOEV-``)."""

    ledger_fingerprint: str
    signal_count: int
    telemetered_count: int
    telemetry_complete: bool
    state_counts: tuple[tuple[str, int], ...]
    signals: tuple[dict[str, Any], ...]
    evidence_id: str = ""

    @classmethod
    def create(
        cls,
        *,
        ledger_fingerprint: str,
        telemetered_count: int,
        state_counts: tuple[tuple[str, int], ...],
        signals: tuple[dict[str, Any], ...],
    ) -> SecurityObservabilityEvidence:
        signal_count = len(signals)
        core = {
            "ledger_fingerprint": ledger_fingerprint,
            "telemetered_count": telemetered_count,
            "telemetry_complete": telemetered_count == signal_count,
            "state_counts": [list(sc) for sc in state_counts],
            "signals": list(signals),
        }
        return cls(
            ledger_fingerprint=ledger_fingerprint,
            signal_count=signal_count,
            telemetered_count=telemetered_count,
            telemetry_complete=telemetered_count == signal_count,
            state_counts=state_counts,
            signals=signals,
            evidence_id=f"UCOS-SOEV-{content_hash(core)[:16]}",
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "evidence_id": self.evidence_id,
            "ledger_fingerprint": self.ledger_fingerprint,
            "signal_count": self.signal_count,
            "telemetered_count": self.telemetered_count,
            "telemetry_complete": self.telemetry_complete,
            "state_counts": [list(sc) for sc in self.state_counts],
            "signals": [dict(s) for s in self.signals],
        }

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())


class SecurityObservabilityService:
    """The governed SEC-OBS composition root (emit · observe · trace · validate · report).

    Shapes security telemetry **through** a certified L8
    :class:`~platform.observability.service.ObservabilityService` — it holds no
    ``MetricRegistry``/``LogBuffer``/``AuditTrail`` of its own (no second telemetry
    stack). Every emitted signal is recorded as an L8 metric + structured log +
    append-only audit event, and (when an event bus is bound) published as a governed
    event so the platform's bound L8 also audits it. 100% of security actions are
    telemetered by construction (§15; PL-02).
    """

    __slots__ = ("_observability", "_ledger", "_events", "_telemetered")

    def __init__(
        self,
        *,
        observability: ObservabilityService,
        ledger: SignalLedger | None = None,
        events: EventBus | None = None,
    ) -> None:
        if not isinstance(observability, ObservabilityService):
            raise SecurityObservabilityError(
                "a certified L8 ObservabilityService is required (no second telemetry stack)"
            )
        if ledger is not None and not isinstance(ledger, SignalLedger):
            raise SecurityObservabilityError("ledger must be a SignalLedger when provided")
        if events is not None and not isinstance(events, EventBus):
            raise SecurityObservabilityError("events must be an EventBus when provided")
        self._observability = observability
        self._ledger = ledger if ledger is not None else SignalLedger()
        self._events = events
        self._telemetered = 0

    @property
    def observability(self) -> ObservabilityService:
        """The L8 layer security telemetry flows through (reused, not duplicated)."""
        return self._observability

    @property
    def ledger(self) -> SignalLedger:
        return self._ledger

    @property
    def telemetered_count(self) -> int:
        """The number of signals for which L8 telemetry was shaped."""
        return self._telemetered

    def telemetry_complete(self) -> bool:
        """True iff every recorded signal was telemetered through L8 (100% coverage)."""
        return self._telemetered == len(self._ledger)

    # -- emit -------------------------------------------------------------------

    def emit_signal(
        self,
        state: RollupState,
        subject_ref: str,
        *,
        traces_to: str,
        emitted_at: int,
        metrics: dict[str, int] | None = None,
        actor: str = "platform.security.observability",
    ) -> SecuritySignal:
        """Shape + record a ``security`` signal and emit its L8 telemetry (record-only)."""
        signal = SecuritySignal.create(
            state, subject_ref, traces_to=traces_to, emitted_at=emitted_at, metrics=metrics
        )
        recorded = self._ledger.record(signal)
        self._telemeter(recorded, actor)
        self._emit_event(recorded)
        return recorded

    def observe_rollup(
        self,
        rollup: SecurityRollup,
        subject_ref: str,
        *,
        traces_to: str | None = None,
        actor: str = "platform.security.observability",
    ) -> SecuritySignal:
        """Map a SEC-INTEL :class:`SecurityRollup` to a ``security`` signal and emit it.

        The signal's ``state`` is the evidence-derived roll-up state, its metrics are
        the roll-up's counts, and it is reverse-traceable to the roll-up (or to a
        caller-supplied ``traces_to`` scan/finding reference). Uses the roll-up's own
        ``evaluated_at`` logical tick — no wall-clock.
        """
        if not isinstance(rollup, SecurityRollup):
            raise SecurityObservabilityError("observe_rollup requires a SecurityRollup")
        return self.emit_signal(
            rollup.state,
            subject_ref,
            traces_to=traces_to if traces_to is not None else rollup.rollup_id,
            emitted_at=rollup.evaluated_at,
            metrics={
                "open_exposures": rollup.open_exposure_count,
                "blocking": rollup.blocking_count,
                "in_progress": rollup.in_progress_count,
                "valid_exceptions": rollup.valid_exception_count,
                "expired_exceptions": rollup.expired_exception_count,
            },
            actor=actor,
        )

    # -- trace + validate + report ----------------------------------------------

    def trace(self, signal_id: str) -> dict[str, Any]:
        """Return the reverse-traceability chain for a recorded signal."""
        return self._ledger.get(signal_id).trace()

    def validate_all(self) -> dict[str, Any]:
        """Assert every recorded signal is reverse-traceable (UMB-015 §5; fail-closed)."""
        signals = self._ledger.signals
        traceable = all(s.reverse_traceable for s in signals)
        return {
            "signal_count": len(signals),
            "all_reverse_traceable": traceable,
            "telemetry_complete": self.telemetry_complete(),
        }

    def report(self) -> SecurityObservabilityEvidence:
        """Produce deterministic security-observability evidence (record-only)."""
        signals = self._ledger.signals
        state_counts = tuple(
            (state.value, sum(1 for s in signals if s.state is state)) for state in RollupState
        )
        return SecurityObservabilityEvidence.create(
            ledger_fingerprint=self._ledger.fingerprint(),
            telemetered_count=self._telemetered,
            state_counts=state_counts,
            signals=tuple(s.to_dict() for s in signals),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "ledger": self._ledger.to_dict(),
            "telemetry_complete": self.telemetry_complete(),
            "evidence": self.report().to_dict(),
        }

    # -- internals --------------------------------------------------------------

    def _telemeter(self, signal: SecuritySignal, actor: str) -> None:
        """Record the signal as an L8 metric + structured log + append-only audit event."""
        obs = self._observability
        obs.metrics.counter(
            SECURITY_SIGNAL_METRIC,
            1.0,
            dimension=signal.dimension,
            state=signal.state.value,
        )
        obs.logs.info(
            "platform.security.observability",
            f"security-signal:{signal.state.value}",
            signal_id=signal.signal_id,
            subject=signal.subject_ref,
            traces_to=signal.traces_to,
        )
        obs.audit.record(
            SECURITY_SIGNAL_AUDIT_ACTION,
            actor,
            signal.subject_ref,
            detail={
                "signal_id": signal.signal_id,
                "dimension": signal.dimension,
                "state": signal.state.value,
                "traces_to": signal.traces_to,
            },
        )
        self._telemetered += 1

    def _emit_event(self, signal: SecuritySignal) -> None:
        """Publish a governed ``security.observability.signal.emitted`` event (if bound)."""
        if self._events is None:
            return
        self._events.publish(
            SECURITY_SIGNAL_EMITTED_EVENT,
            source="platform.security.observability",
            subject=signal.subject_ref,
            payload={"signal": signal.to_dict(), "enacts": False},
        )


def build_security_observability_service(
    *,
    observability: ObservabilityService | None = None,
    events: EventBus | None = None,
) -> SecurityObservabilityService:
    """Default composition of the Security Observability Runtime (reuses L8 by reference).

    When no L8 :class:`ObservabilityService` is supplied, a fresh (unbound) one is
    composed via the certified :func:`build_observability_service` — SEC-OBS never
    defines its own telemetry stack.
    """
    obs = observability if observability is not None else build_observability_service()
    return SecurityObservabilityService(observability=obs, events=events)


__all__ = [
    "SECURITY_SIGNAL_EMITTED_EVENT",
    "SECURITY_SIGNAL_METRIC",
    "SECURITY_SIGNAL_AUDIT_ACTION",
    "SecuritySignal",
    "SignalLedger",
    "SecurityObservabilityEvidence",
    "SecurityObservabilityService",
    "build_security_observability_service",
]
