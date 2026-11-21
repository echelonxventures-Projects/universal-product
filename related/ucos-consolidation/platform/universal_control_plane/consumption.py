"""UCOS-CTRL-000001 — System Consumption (Wave 9).

"Available to consumers" is not the same claim as "consumed", and only one of
them is measurable. A control plane that every subsystem *could* call and none
does is a library with good intentions.

So consumption here is a recorded event, not an import. A consumer is a named
repository domain bound to a control-plane service; invoking it produces a
:class:`ConsumptionRecord` carrying the digest of what came back. The count of
those records is the measurement, and it is zero until something actually runs —
which is exactly the property that makes it worth measuring.

Six domains ship bound, each exercising a different part of the stack:

    repository-truth   classification and artifact discovery
    governance         per-object resolution rolled into the repository decision
    certification      eligibility and seal issuance
    planning           the plan/roadmap/backlog derived from repository state
    implementation     scheduling and assignment over the derived backlog
    intelligence       progress, metrics and the unified dashboard

Each reaches through the control plane into a real repository capability —
``platform.universal_truth`` for classification, ``engine.governance`` for the
repository decision, ``engine.certification`` for the certificate — so a
successful consumption run is evidence that the integration holds end to end,
not that six stubs returned.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass, field
from platform.universal_control_plane.errors import ControlPlaneError, ObjectNotFoundError
from platform.universal_control_plane.ontology import payload_digest
from typing import Any

CONSUMER_REPOSITORY_TRUTH = "repository-truth"
CONSUMER_GOVERNANCE = "governance"
CONSUMER_CERTIFICATION = "certification"
CONSUMER_PLANNING = "planning"
CONSUMER_IMPLEMENTATION = "implementation"
CONSUMER_INTELLIGENCE = "intelligence"

#: The domains bound by :func:`default_consumers`.
DEFAULT_CONSUMERS: tuple[str, ...] = (
    CONSUMER_CERTIFICATION,
    CONSUMER_GOVERNANCE,
    CONSUMER_IMPLEMENTATION,
    CONSUMER_INTELLIGENCE,
    CONSUMER_PLANNING,
    CONSUMER_REPOSITORY_TRUTH,
)

OUTCOME_SERVED = "SERVED"
OUTCOME_FAILED = "FAILED"


@dataclass(frozen=True, slots=True)
class ConsumptionRecord:
    """One measured invocation of a control-plane service by a named domain."""

    consumer_id: str
    service: str
    outcome: str
    result_digest: str = ""
    detail: str = ""
    tick: int = 0

    @property
    def served(self) -> bool:
        return self.outcome == OUTCOME_SERVED

    def to_dict(self) -> dict[str, Any]:
        return {
            "consumer_id": self.consumer_id,
            "service": self.service,
            "outcome": self.outcome,
            "served": self.served,
            "result_digest": self.result_digest,
            "detail": self.detail,
            "tick": self.tick,
        }


@dataclass(frozen=True, slots=True)
class Consumer:
    """A named repository domain bound to a control-plane service."""

    consumer_id: str
    service: str
    invoke: Callable[[Any], Any]
    description: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "consumer_id": self.consumer_id,
            "service": self.service,
            "description": self.description,
        }


@dataclass
class ConsumptionEngine:
    """Registers consumers, invokes them, and measures what they actually consumed."""

    _consumers: dict[str, Consumer] = field(default_factory=dict)
    _records: list[ConsumptionRecord] = field(default_factory=list)

    # -- registration ----------------------------------------------------

    def register(self, consumer: Consumer) -> Consumer:
        if not consumer.consumer_id.strip():
            raise ControlPlaneError("a consumer requires a non-empty consumer_id")
        self._consumers[consumer.consumer_id] = consumer
        return consumer

    def register_all(self, consumers: Iterable[Consumer]) -> tuple[Consumer, ...]:
        return tuple(self.register(c) for c in consumers)

    def consumer(self, consumer_id: str) -> Consumer:
        if consumer_id not in self._consumers:
            raise ObjectNotFoundError(f"consumer not registered: {consumer_id}")
        return self._consumers[consumer_id]

    def consumers(self) -> tuple[Consumer, ...]:
        return tuple(self._consumers[key] for key in sorted(self._consumers))

    # -- invocation ------------------------------------------------------

    def invoke(self, consumer_id: str, plane: Any, *, tick: int = 0) -> ConsumptionRecord:
        """Invoke one consumer against *plane* and record what it consumed.

        A consumer that raises is recorded as FAILED rather than propagating: one
        subsystem's integration breaking is a measurement about that subsystem,
        and losing the other five results to it would destroy the measurement.
        """
        consumer = self.consumer(consumer_id)
        try:
            result = consumer.invoke(plane)
        except Exception as exc:  # noqa: BLE001 — a failed consumer is a datum, not a crash
            record = ConsumptionRecord(
                consumer_id=consumer_id,
                service=consumer.service,
                outcome=OUTCOME_FAILED,
                detail=f"{type(exc).__name__}: {exc}",
                tick=tick,
            )
        else:
            record = ConsumptionRecord(
                consumer_id=consumer_id,
                service=consumer.service,
                outcome=OUTCOME_SERVED,
                result_digest=payload_digest(result),
                detail=_summarise(result),
                tick=tick,
            )
        self._records.append(record)
        return record

    def invoke_all(self, plane: Any, *, tick: int = 0) -> tuple[ConsumptionRecord, ...]:
        return tuple(
            self.invoke(consumer_id, plane, tick=tick) for consumer_id in sorted(self._consumers)
        )

    # -- measurement -----------------------------------------------------

    def records(self, consumer_id: str | None = None) -> tuple[ConsumptionRecord, ...]:
        if consumer_id is None:
            return tuple(self._records)
        return tuple(r for r in self._records if r.consumer_id == consumer_id)

    def served(self) -> tuple[ConsumptionRecord, ...]:
        return tuple(r for r in self._records if r.served)

    def failed(self) -> tuple[ConsumptionRecord, ...]:
        return tuple(r for r in self._records if not r.served)

    def consumed_by(self) -> tuple[str, ...]:
        """The domains that actually consumed a service, in invocation-independent order."""
        return tuple(sorted({r.consumer_id for r in self.served()}))

    def invocation_count(self) -> int:
        return len(self._records)

    def coverage(self) -> float:
        """The fraction of registered consumers that have successfully consumed."""
        if not self._consumers:
            return 0.0
        return round(len(self.consumed_by()) / len(self._consumers), 4)

    def operational(self) -> bool:
        """True iff every registered consumer has consumed at least once."""
        return bool(self._consumers) and len(self.consumed_by()) == len(self._consumers)

    # -- projection ------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        return {
            "engine": "ConsumptionEngine",
            "consumers": [c.to_dict() for c in self.consumers()],
            "counts": {
                "registered": len(self._consumers),
                "invocations": self.invocation_count(),
                "served": len(self.served()),
                "failed": len(self.failed()),
            },
            "coverage": self.coverage(),
            "operational": self.operational(),
            "consumed_by": list(self.consumed_by()),
            "records": [r.to_dict() for r in self._records],
        }


def _summarise(result: Any) -> str:
    """A one-line, deterministic summary of what a consumer got back."""
    if isinstance(result, dict):
        return f"{len(result)} key(s): {', '.join(sorted(result)[:4])}"
    if isinstance(result, list | tuple):
        return f"{len(result)} item(s)"
    return type(result).__name__


# ---------------------------------------------------------------------------
# The bound domains
# ---------------------------------------------------------------------------


def _consume_repository_truth(plane: Any) -> dict[str, Any]:
    truth = plane.truth.truth(tick=plane.tick)
    return {
        "truth_id": truth.truth_id,
        "counts": truth.counts(),
        "policy_id": truth.policy_id,
        "sources": [s.source_id for s in truth.sources],
    }


def _consume_governance(plane: Any) -> dict[str, Any]:
    decision = plane.governance.decision(
        certification_failures=plane.certification.failures(),
        certification_total=plane.certification.count(),
        acceptance_failures=tuple(r.subject_id for r in plane.linkage.orphans()),
        acceptance_total=plane.linkage.count(),
    )
    return {
        "status": decision.status.value,
        "governed": len(plane.governance.governed()),
        "not_governed": len(plane.governance.not_governed()),
        "blocking_reasons": len(decision.blocking_reasons),
        "decision_sha256": decision.decision_sha256,
    }


def _consume_certification(plane: Any) -> dict[str, Any]:
    return {
        "assessed": plane.certification.count(),
        "certified": len(plane.certification.certified()),
        "ineligible": len(plane.certification.ineligible()),
        "criteria": [c.rule_id for c in plane.certification.criteria],
    }


def _consume_planning(plane: Any) -> dict[str, Any]:
    return {
        "plan": plane.plan.to_dict()["objectives"],
        "milestones": plane.roadmap.count(),
        "backlog": plane.backlog.count(),
        "estimate": plane.backlog.total_estimate(),
    }


def _consume_implementation(plane: Any) -> dict[str, Any]:
    schedule = plane.schedule()
    return {
        "waves": schedule.wave_count,
        "entries": len(schedule.entries),
        "agents": plane.agents.count(),
    }


def _consume_intelligence(plane: Any) -> dict[str, Any]:
    snapshot = plane.dashboard()
    return {"sections": sorted(snapshot), "keys": len(snapshot)}


def default_consumers() -> tuple[Consumer, ...]:
    """The six repository domains bound to control-plane services."""
    return (
        Consumer(
            CONSUMER_REPOSITORY_TRUTH,
            "truth.discover",
            _consume_repository_truth,
            "classifies and counts repository truth through the declared policy",
        ),
        Consumer(
            CONSUMER_GOVERNANCE,
            "governance.decide",
            _consume_governance,
            "rolls per-object governance into the canonical repository decision",
        ),
        Consumer(
            CONSUMER_CERTIFICATION,
            "certification.assess",
            _consume_certification,
            "reads certification status and eligibility across every subject",
        ),
        Consumer(
            CONSUMER_PLANNING,
            "plan.derive",
            _consume_planning,
            "reads the plan, roadmap and backlog derived from repository state",
        ),
        Consumer(
            CONSUMER_IMPLEMENTATION,
            "schedule.produce",
            _consume_implementation,
            "schedules the derived backlog across discovered agents",
        ),
        Consumer(
            CONSUMER_INTELLIGENCE,
            "dashboard.snapshot",
            _consume_intelligence,
            "reads the unified progress, metrics and dashboard snapshot",
        ),
    )


__all__ = [
    "CONSUMER_CERTIFICATION",
    "CONSUMER_GOVERNANCE",
    "CONSUMER_IMPLEMENTATION",
    "CONSUMER_INTELLIGENCE",
    "CONSUMER_PLANNING",
    "CONSUMER_REPOSITORY_TRUTH",
    "DEFAULT_CONSUMERS",
    "OUTCOME_FAILED",
    "OUTCOME_SERVED",
    "Consumer",
    "ConsumptionEngine",
    "ConsumptionRecord",
    "default_consumers",
]
