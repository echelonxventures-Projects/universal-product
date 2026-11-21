"""UCOS-EPIC-014 — Assurance measurement (Terminal T7).

**Everything measurable.** Every stage of the assurance pipeline publishes numeric
*observations*; every threshold those observations are judged against is *declared* by
the policy as a :class:`~platform.universal_assurance.policy.PolicyMetric`. This module
is the only place the two meet, and it contains **no metric, no threshold and no
comparator of its own** — it evaluates whatever the policy declares against whatever the
run observed.

The comparison semantics are not reinvented either: each sample is decided by the
**reused** :class:`engine.universal_certification.contracts.Measurement`, whose
``satisfied`` verdict is *computed* from ``(value, comparator, threshold)`` and can never
be hand-set. Measurement over assertion, all the way down.

Fail-closed discipline: a declared metric whose observation the run never published is
recorded as **unobserved and unsatisfied** — never skipped, never assumed satisfied. To
make that failure visible to the reused certifier (which sees measurements, not policy),
:meth:`MeasurementReport.to_certification_measurements` appends one *derived* blocking
measurement, :data:`OBSERVATION_COVERAGE_METRIC_ID`, whose value is the observed/declared
ratio. A run that could not measure a declared metric therefore cannot be certified.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from platform.foundation.contracts import content_hash
from platform.universal_assurance.contracts import AssuranceStage, Severity, Verdict
from platform.universal_assurance.errors import AssuranceMeasurementError
from platform.universal_assurance.policy import AssurancePolicy, PolicyMetric
from typing import Any

from engine.universal_certification.contracts import (
    Measurement,
    MeasurementComparator,
    MeasurementInput,
)
from engine.universal_certification.contracts import RuleSeverity as CertRuleSeverity

#: The measurement report format identifier.
MEASUREMENT_FORMAT = "ucos-assurance-measurement-report/1.0.0"

#: The derived measurement that makes an unmeasurable policy metric visible to the
#: reused certifier (blocking: full observation coverage is required).
OBSERVATION_COVERAGE_METRIC_ID = "assurance.metric_observation_coverage"

#: The policy severity → reused certification severity mapping (one shared vocabulary).
_SEVERITY_MAP: dict[Severity, CertRuleSeverity] = {
    Severity.BLOCKING: CertRuleSeverity.BLOCKING,
    Severity.ADVISORY: CertRuleSeverity.ADVISORY,
}


def certification_severity(severity: Severity) -> CertRuleSeverity:
    """Project an assurance severity onto the reused certification severity."""
    try:
        return _SEVERITY_MAP[severity]
    except KeyError as exc:  # pragma: no cover - Severity is a closed enum
        raise AssuranceMeasurementError("unsupported severity", severity=str(severity)) from exc


@dataclass(frozen=True, slots=True)
class MetricSample:
    """One declared metric decided against one observed value (or provably unobserved)."""

    metric_id: str
    stage: AssuranceStage
    observation: str
    comparator: MeasurementComparator
    threshold: float
    severity: Severity
    observed: bool
    value: float
    satisfied: bool
    unit: str = ""

    @classmethod
    def evaluate(cls, metric: PolicyMetric, observations: Mapping[str, float]) -> MetricSample:
        """Decide ``metric`` against ``observations`` (fail-closed when unobserved).

        The satisfaction verdict is delegated to the reused
        :class:`~engine.universal_certification.contracts.Measurement`, so the comparison
        semantics are shared with the certifier rather than re-implemented.
        """
        raw = observations.get(metric.observation)
        if raw is None or isinstance(raw, bool) or not isinstance(raw, int | float):
            return cls(
                metric_id=metric.id,
                stage=metric.stage,
                observation=metric.observation,
                comparator=metric.comparator,
                threshold=metric.threshold,
                severity=metric.severity,
                observed=False,
                value=0.0,
                satisfied=False,
                unit=metric.unit,
            )
        measurement = Measurement.evaluate(
            metric_id=metric.id,
            value=float(raw),
            threshold=metric.threshold,
            comparator=metric.comparator,
            severity=certification_severity(metric.severity),
            unit=metric.unit,
        )
        return cls(
            metric_id=metric.id,
            stage=metric.stage,
            observation=metric.observation,
            comparator=metric.comparator,
            threshold=metric.threshold,
            severity=metric.severity,
            observed=True,
            value=measurement.value,
            satisfied=measurement.satisfied,
            unit=metric.unit,
        )

    @property
    def is_blocking_shortfall(self) -> bool:
        return not self.satisfied and self.severity is Severity.BLOCKING

    @property
    def is_advisory_shortfall(self) -> bool:
        return not self.satisfied and self.severity is Severity.ADVISORY

    def as_measurement(self) -> Measurement:
        """Project onto the reused certification measurement type (observed samples)."""
        return Measurement.evaluate(
            metric_id=self.metric_id,
            value=self.value,
            threshold=self.threshold,
            comparator=self.comparator,
            severity=certification_severity(self.severity),
            unit=self.unit,
        )

    def core(self) -> dict[str, Any]:
        return {
            "metric_id": self.metric_id,
            "stage": self.stage.value,
            "observation": self.observation,
            "comparator": self.comparator.value,
            "threshold": self.threshold,
            "severity": self.severity.value,
            "observed": self.observed,
            "value": self.value,
            "satisfied": self.satisfied,
            "unit": self.unit,
        }

    def to_dict(self) -> dict[str, Any]:
        return self.core()


@dataclass(frozen=True, slots=True)
class MeasurementReport:
    """An immutable, content-addressed record of every declared metric, decided."""

    subject_id: str
    policy_id: str
    policy_digest: str
    verdict: Verdict
    samples: tuple[MetricSample, ...]
    declared_total: int
    report_sha256: str

    @staticmethod
    def _core(
        *,
        subject_id: str,
        policy_id: str,
        policy_digest: str,
        verdict: Verdict,
        samples: tuple[MetricSample, ...],
        declared_total: int,
    ) -> dict[str, Any]:
        return {
            "measurement_format": MEASUREMENT_FORMAT,
            "subject_id": subject_id,
            "policy_id": policy_id,
            "policy_digest": policy_digest,
            "verdict": verdict.value,
            "declared_total": declared_total,
            "samples": [sample.core() for sample in samples],
        }

    @classmethod
    def create(
        cls,
        *,
        subject_id: str,
        policy: AssurancePolicy,
        observations: Mapping[str, float],
        stage: AssuranceStage | None = None,
        metrics: Iterable[PolicyMetric] | None = None,
    ) -> MeasurementReport:
        """Decide the declared metrics (all of them, or a stage / explicit subset).

        ``metrics`` lets a caller decide only the metrics whose observations exist yet —
        the certification stage, for instance, can only consume the metrics measured
        *before* certification ran. The subset is still policy-declared; nothing is
        invented here.
        """
        selected = tuple(metrics) if metrics is not None else policy.metrics_for(stage)
        samples = tuple(
            MetricSample.evaluate(metric, observations)
            for metric in sorted(selected, key=lambda m: (m.stage.order, m.id))
        )
        verdict = Verdict.FAIL if any(s.is_blocking_shortfall for s in samples) else Verdict.PASS
        core = cls._core(
            subject_id=subject_id,
            policy_id=policy.identity.id,
            policy_digest=policy.digest(),
            verdict=verdict,
            samples=samples,
            declared_total=len(selected),
        )
        return cls(
            subject_id=subject_id,
            policy_id=policy.identity.id,
            policy_digest=policy.digest(),
            verdict=verdict,
            samples=samples,
            declared_total=len(selected),
            report_sha256=content_hash(core),
        )

    # -- derived properties ----------------------------------------------------

    @property
    def passed(self) -> bool:
        return self.verdict is Verdict.PASS

    def samples_for(self, stage: AssuranceStage) -> tuple[MetricSample, ...]:
        return tuple(sample for sample in self.samples if sample.stage is stage)

    def blocking_shortfalls(self, stage: AssuranceStage | None = None) -> tuple[str, ...]:
        scope = self.samples if stage is None else self.samples_for(stage)
        return tuple(sample.metric_id for sample in scope if sample.is_blocking_shortfall)

    def advisory_shortfalls(self, stage: AssuranceStage | None = None) -> tuple[str, ...]:
        scope = self.samples if stage is None else self.samples_for(stage)
        return tuple(sample.metric_id for sample in scope if sample.is_advisory_shortfall)

    def unobserved(self) -> tuple[str, ...]:
        return tuple(sample.metric_id for sample in self.samples if not sample.observed)

    def observation_coverage(self) -> float:
        """The observed/declared metric ratio (1.0 when the policy declares no metric)."""
        if not self.samples:
            return 1.0
        return sum(1 for sample in self.samples if sample.observed) / len(self.samples)

    def counts(self) -> dict[str, int]:
        return {
            "declared": self.declared_total,
            "sampled": len(self.samples),
            "observed": sum(1 for sample in self.samples if sample.observed),
            "unobserved": len(self.unobserved()),
            "satisfied": sum(1 for sample in self.samples if sample.satisfied),
            "blocking_shortfalls": len(self.blocking_shortfalls()),
            "advisory_shortfalls": len(self.advisory_shortfalls()),
        }

    def to_certification_measurements(self) -> tuple[Measurement, ...]:
        """Project onto the reused certifier's measurement set (fail-closed).

        Observed samples are projected one-for-one. One *derived* blocking measurement,
        :data:`OBSERVATION_COVERAGE_METRIC_ID`, carries the observed/declared ratio so a
        metric the run could not measure becomes a blocking measurement shortfall for the
        certifier — an unmeasurable policy is never certifiable.
        """
        measurements = [sample.as_measurement() for sample in self.samples if sample.observed]
        measurements.append(
            Measurement.evaluate(
                metric_id=OBSERVATION_COVERAGE_METRIC_ID,
                value=self.observation_coverage(),
                threshold=1.0,
                comparator=MeasurementComparator.GE,
                severity=CertRuleSeverity.BLOCKING,
                unit="ratio",
            )
        )
        return tuple(measurements)

    def to_measurement_input(self, *, source: str) -> MeasurementInput:
        """Project onto the reused certifier's :class:`MeasurementInput`."""
        return MeasurementInput.create(self.to_certification_measurements(), source=source)

    def to_dict(self) -> dict[str, Any]:
        return {
            "measurement_format": MEASUREMENT_FORMAT,
            "subject_id": self.subject_id,
            "policy_id": self.policy_id,
            "policy_digest": self.policy_digest,
            "verdict": self.verdict.value,
            "passed": self.passed,
            "counts": self.counts(),
            "observation_coverage": self.observation_coverage(),
            "unobserved": list(self.unobserved()),
            "blocking_shortfalls": list(self.blocking_shortfalls()),
            "advisory_shortfalls": list(self.advisory_shortfalls()),
            "samples": [sample.to_dict() for sample in self.samples],
            "report_sha256": self.report_sha256,
        }


def merge_observations(*sources: Mapping[str, float]) -> dict[str, float]:
    """Merge observation maps deterministically; later sources win on collision."""
    merged: dict[str, float] = {}
    for source in sources:
        for key, value in source.items():
            if isinstance(value, bool) or not isinstance(value, int | float):
                raise AssuranceMeasurementError(
                    "observations must be numeric", observation=key, value=repr(value)
                )
            merged[key] = float(value)
    return dict(sorted(merged.items()))


def boolean_observation(value: bool) -> float:
    """Project a boolean invariant onto the numeric observation space (1.0 / 0.0)."""
    return 1.0 if value else 0.0


def measure(
    *,
    subject_id: str,
    policy: AssurancePolicy,
    observations: Mapping[str, float],
    stage: AssuranceStage | None = None,
    metrics: Iterable[PolicyMetric] | None = None,
) -> MeasurementReport:
    """Decide every policy-declared metric against ``observations``."""
    if not isinstance(policy, AssurancePolicy):
        raise AssuranceMeasurementError("measurement requires an AssurancePolicy")
    return MeasurementReport.create(
        subject_id=subject_id,
        policy=policy,
        observations=observations,
        stage=stage,
        metrics=metrics,
    )


def metrics_before(policy: AssurancePolicy, stage: AssuranceStage) -> tuple[PolicyMetric, ...]:
    """The declared metrics for every stage that precedes ``stage`` in canonical order.

    Derived from the stage ordering, never enumerated: it answers "which measurements
    exist by the time this stage runs?" so a stage can only consume what was measured
    before it.
    """
    return tuple(metric for metric in policy.metrics if metric.stage.order < stage.order)


def subject_observations(observations: Mapping[str, float]) -> dict[str, float]:
    """Namespace externally supplied subject observations under ``subject.``.

    Namespacing keeps caller-supplied facts from colliding with the stage observations
    the pipeline derives, so a subject can never overwrite a measured stage outcome.
    """
    return {f"subject.{key}": float(value) for key, value in sorted(observations.items())}


def observation_names(policy: AssurancePolicy) -> tuple[str, ...]:
    """Every observation name the policy's metrics depend on, in canonical order."""
    return tuple(sorted({metric.observation for metric in policy.metrics}))


def stage_metric_ids(policy: AssurancePolicy, stage: AssuranceStage) -> tuple[str, ...]:
    """The metric ids declared for ``stage``, in canonical order."""
    return tuple(sorted(metric.id for metric in policy.metrics_for(stage)))


def samples_as_input(samples: Iterable[MetricSample], *, source: str) -> MeasurementInput:
    """Project an arbitrary sample iterable onto the reused certifier's input."""
    return MeasurementInput.create(
        tuple(sample.as_measurement() for sample in samples if sample.observed), source=source
    )


__all__ = [
    "MEASUREMENT_FORMAT",
    "OBSERVATION_COVERAGE_METRIC_ID",
    "certification_severity",
    "MetricSample",
    "MeasurementReport",
    "merge_observations",
    "boolean_observation",
    "measure",
    "metrics_before",
    "subject_observations",
    "observation_names",
    "stage_metric_ids",
    "samples_as_input",
]
