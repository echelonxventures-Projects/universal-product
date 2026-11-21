"""UCOS-EPIC-004 — Measurement vocabulary & contracts (UCOS-UMA-001).

The immutable, deterministic vocabulary the Universal Measurement Engine speaks, plus
its versioned published contract surface (AR-03/PL-05, reusing the certified Foundation
contract machinery). The engine measures the authoritative Registry population across
four measurement kinds — **enumeration**, **metric**, **coverage**, and **gap** — and
records each as a content-addressed :class:`Measurement`. A :class:`Metric` is the
atomic quantitative observation the Metrics Engine emits, reusing the certified
Observability :class:`~platform.observability.contracts.MetricKind` vocabulary.

Every identity is content-addressed (deterministic, reproducible; IMP-007 §5) and holds
no wall-clock. Measurement identities live in a **disjoint namespace** (``UCOS-UMA*``)
from Registry Truth identities (``UCOS-*`` universal ids): a measurement can never be
mistaken for, nor overwrite, a fact — Measurement consumes Truth and never creates it.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import Enum
from platform.foundation.contracts import ContractRef, content_hash
from platform.measurement.errors import MeasurementContractError
from platform.observability.contracts import MetricKind
from typing import Any

#: The canonical identity of the Universal Measurement Engine instance (UCOS-EPIC-004).
UMA_ID = "UCOS-UMA-001"

#: The semantic version of the measurement instrument contract surface (AR-03/PL-05).
MEASUREMENT_CONTRACT_VERSION = "1.0.0"


class MeasurementKind(str, Enum):
    """The four kinds of measurement the engine produces over Registry Truth."""

    ENUMERATION = "enumeration"
    METRIC = "metric"
    COVERAGE = "coverage"
    GAP = "gap"


def _canonical_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Validate and defensively copy a JSON-serializable measurement payload."""
    if not isinstance(payload, Mapping):
        raise MeasurementContractError("measurement payload must be a mapping")
    try:
        # Round-trip through the canonical encoder to guarantee serializability now
        # (fail-closed) rather than at hashing time deep in an engine.
        content_hash(payload)
    except (TypeError, ValueError) as exc:
        raise MeasurementContractError(
            "measurement payload is not JSON-serializable", detail=str(exc)
        ) from exc
    return dict(payload)


@dataclass(frozen=True, slots=True)
class Metric:
    """An immutable, content-addressed quantitative observation over Registry Truth.

    The ``metric_id`` identifies the *series* — a pure function of ``(name, kind,
    labels)`` and never of the observed ``value`` — so the same series is stably
    addressable across recomputes while its value tracks the current Truth.
    """

    name: str
    kind: MetricKind
    value: float
    labels: tuple[tuple[str, str], ...] = ()
    metric_id: str = ""

    @classmethod
    def create(
        cls,
        name: str,
        kind: MetricKind,
        value: float,
        *,
        labels: Mapping[str, str] | None = None,
    ) -> Metric:
        if not isinstance(name, str) or not name.strip():
            raise MeasurementContractError("metric name must be a non-empty string")
        if not isinstance(kind, MetricKind):
            raise MeasurementContractError("metric kind must be a MetricKind", name=name)
        if isinstance(value, bool) or not isinstance(value, int | float):
            raise MeasurementContractError("metric value must be numeric", name=name)
        label_pairs: tuple[tuple[str, str], ...] = ()
        if labels:
            for key, val in labels.items():
                if not isinstance(key, str) or not key or not isinstance(val, str):
                    raise MeasurementContractError(
                        "metric labels must be a str->str map", name=name
                    )
            label_pairs = tuple(sorted((k, v) for k, v in labels.items()))
        core = {"name": name, "kind": kind.value, "labels": [list(p) for p in label_pairs]}
        return cls(
            name=name,
            kind=kind,
            value=float(value),
            labels=label_pairs,
            metric_id=f"UCOS-UMAX-{content_hash(core)[:16]}",
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "metric_id": self.metric_id,
            "name": self.name,
            "kind": self.kind.value,
            "value": self.value,
            "labels": [list(p) for p in self.labels],
        }

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())


@dataclass(frozen=True, slots=True)
class Measurement:
    """An immutable, content-addressed unit of measurement about Registry Truth.

    A measurement is *derived* knowledge: it describes the corpus, it is never part of
    it. ``subject`` cites the Truth locus being measured (a dimension, a stage, the whole
    population); ``payload`` carries the deterministic measurement body. The
    ``measurement_id`` is a pure function of ``(kind, subject, payload)`` so identical
    measurements over identical Truth collapse to one id (idempotent, append-only).
    """

    kind: MeasurementKind
    subject: str
    summary: str
    payload: Mapping[str, Any] = field(default_factory=dict)
    measurement_id: str = ""

    @classmethod
    def create(
        cls,
        kind: MeasurementKind,
        subject: str,
        *,
        summary: str = "",
        payload: Mapping[str, Any] | None = None,
    ) -> Measurement:
        if not isinstance(kind, MeasurementKind):
            raise MeasurementContractError("measurement kind must be a MeasurementKind")
        if not isinstance(subject, str) or not subject.strip():
            raise MeasurementContractError("measurement subject must be a non-empty string")
        body = _canonical_payload(payload or {})
        core = {"kind": kind.value, "subject": subject, "payload": body}
        return cls(
            kind=kind,
            subject=subject,
            summary=summary,
            payload=body,
            measurement_id=f"UCOS-UMAM-{content_hash(core)[:16]}",
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "measurement_id": self.measurement_id,
            "kind": self.kind.value,
            "subject": self.subject,
            "summary": self.summary,
            "payload": dict(self.payload),
        }

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())


#: The published measurement contract surface (consumed by certification/TRACK-001).
_MEASUREMENT_CONTRACT_NAMES: tuple[tuple[str, str], ...] = (
    ("measurement.truth.snapshot", "Read-only deterministic projection of Registry Truth."),
    ("measurement.enumeration.enumerate", "Enumerate the Registry population by dimension."),
    ("measurement.metrics.compute", "Quantitative metrics (counters/gauges) over Truth."),
    ("measurement.coverage.measure", "Traceability-chain coverage measurement (13 stages)."),
    ("measurement.gaps.detect", "Structural + completeness gap detection over Truth."),
    ("measurement.registry.record", "Append-only content-addressed measurement registry."),
    ("measurement.engine.measure", "Measure/verify/report/fingerprint/evidence surface."),
)

#: Immutable references to the seven published measurement contracts (name + version).
MEASUREMENT_CONTRACTS: tuple[ContractRef, ...] = tuple(
    ContractRef(name, MEASUREMENT_CONTRACT_VERSION) for name, _ in _MEASUREMENT_CONTRACT_NAMES
)

#: The authoritative governance instruments the engine integrates with **by reference**
#: (it reads them; it authors none). Cited in every report/evidence.
GOVERNANCE_AUTHORITIES: tuple[str, ...] = (
    "GOV-002",  # Constitution→Implementation traceability (link model)
    "GOV-005",  # Repository governance reconciliation (zero-gap invariant)
    "TRACK-001",  # Evidence→status, append-only, fail-closed
    "STATUS-001",  # Evidence→status discipline
    "DP-03",  # Certified corpus is read-only to implementation (never create Truth)
    "UCOS-EPIC-004",  # Authorizing basis for the Universal Measurement Engine
)


def measurement_contract_names() -> tuple[str, ...]:
    """Return the published measurement contract names in stable order."""
    return tuple(name for name, _ in _MEASUREMENT_CONTRACT_NAMES)


__all__ = [
    "UMA_ID",
    "MEASUREMENT_CONTRACT_VERSION",
    "MeasurementKind",
    "Metric",
    "Measurement",
    "MetricKind",
    "MEASUREMENT_CONTRACTS",
    "GOVERNANCE_AUTHORITIES",
    "measurement_contract_names",
]
