"""UAPF-000001 — pipeline observability: metrics, spans, health and bottlenecks.

Observability here is *derived from what was recorded*, never sampled from the environment.
That is a deliberate constraint: a metric read from a clock or a process counter would make
a run irreproducible, and the whole framework's guarantee is that an identical run produces
an identical record. So a "duration" in UAPF is a **count of steps**, not elapsed time, and
health is a function of recorded outcomes rather than of live probes.

What this buys
--------------
Two runs of the same declarations produce identical telemetry and an identical
:meth:`PipelineObservability.fingerprint`. A regression is therefore detectable by
comparing fingerprints — which is impossible for wall-clock metrics, where every run
differs and no comparison means anything.

Bottlenecks
-----------
A bottleneck is ranked by recorded magnitude: the metric names carrying the most weight,
descending, ties broken by name. That is honest about what it measures — where recorded
work concentrates — and makes no claim about causation.

Health
------
Derived from recorded failure counts: ``HEALTHY`` when nothing recorded a failure,
``DEGRADED`` when something did. There is no third state, because a state that means
"probably fine" would be a judgement this module has no basis to make.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from platform.foundation.contracts import content_hash
from platform.universal_pipeline.errors import PipelineObservabilityError
from platform.universal_pipeline.events import PipelineEventBus
from platform.universal_pipeline.identity import Identity, mint
from typing import Any

#: The telemetry kinds. ``counter`` accumulates, ``gauge`` reports a level, ``span``
#: reports a step count over a named scope. Extending this set would be a change to what
#: telemetry *means*, so it is closed while the metric *names* are unbounded — the
#: openness that matters is in the names, not the kinds.
TELEMETRY_KINDS: tuple[str, ...] = ("counter", "gauge", "span")

#: The two health verdicts (see the module docstring on why there is no third).
HEALTHY = "HEALTHY"
DEGRADED = "DEGRADED"

#: The metric name recorded for a stage outcome that did not pass. Named here so the
#: health derivation and the runtime agree by construction rather than by convention.
FAILURE_METRIC = "uapf.stage.failed"

#: The metric name recorded for a stage outcome that passed.
SUCCESS_METRIC = "uapf.stage.passed"


@dataclass(frozen=True, slots=True)
class PipelineTelemetry:
    """One immutable recorded measurement."""

    name: str
    value: float
    kind: str = "counter"
    labels: Mapping[str, str] = field(default_factory=dict)
    ordinal: int = 0

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name:
            raise PipelineObservabilityError("telemetry name is required")
        if isinstance(self.value, bool) or not isinstance(self.value, int | float):
            raise PipelineObservabilityError("telemetry value must be numeric", name=self.name)
        if self.kind not in TELEMETRY_KINDS:
            raise PipelineObservabilityError(
                "unknown telemetry kind",
                name=self.name,
                kind=self.kind,
                declared=list(TELEMETRY_KINDS),
            )
        if not isinstance(self.labels, Mapping):
            raise PipelineObservabilityError("telemetry labels must be a mapping", name=self.name)
        for key, label in self.labels.items():
            if not isinstance(key, str) or not isinstance(label, str):
                raise PipelineObservabilityError(
                    "telemetry labels must be string to string", name=self.name
                )
        if self.ordinal < 0:
            raise PipelineObservabilityError(
                "telemetry ordinal must be non-negative", name=self.name
            )

    @property
    def identity(self) -> Identity:
        return mint("telemetry", self.name, self.kind, str(self.ordinal))

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "value": self.value,
            "kind": self.kind,
            "labels": dict(self.labels),
            "ordinal": self.ordinal,
        }


class PipelineObservability:
    """The recorded telemetry of one platform instance, and the views derived from it."""

    __slots__ = ("_metrics", "_bus")

    def __init__(self, *, bus: PipelineEventBus | None = None) -> None:
        if bus is not None and not isinstance(bus, PipelineEventBus):
            raise PipelineObservabilityError("bus must be a PipelineEventBus")
        self._metrics: list[PipelineTelemetry] = []
        self._bus = bus

    # -- recording --------------------------------------------------------------------

    def record(
        self,
        name: str,
        value: float,
        *,
        kind: str = "counter",
        labels: Mapping[str, str] | None = None,
    ) -> PipelineTelemetry:
        """Record one measurement and return it.

        Raises:
            PipelineObservabilityError: if the name, value, kind or labels are malformed.
        """
        metric = PipelineTelemetry(
            name=name,
            value=value,
            kind=kind,
            labels=dict(labels or {}),
            ordinal=len(self._metrics),
        )
        self._metrics.append(metric)
        if self._bus is not None:
            self._bus.emit("uapf.telemetry.recorded", name, payload=metric.to_dict())
        return metric

    def record_span(self, name: str, steps: int, **labels: str) -> PipelineTelemetry:
        """Record a span over ``name`` measured in *steps*, not seconds.

        Raises:
            PipelineObservabilityError: if ``steps`` is negative.
        """
        if not isinstance(steps, int) or isinstance(steps, bool) or steps < 0:
            raise PipelineObservabilityError(
                "span steps must be a non-negative integer", name=name, steps=steps
            )
        return self.record(name, float(steps), kind="span", labels=labels)

    def observe_outcome(self, stage_id: str, passed: bool, **labels: str) -> PipelineTelemetry:
        """Record the pass/fail outcome of one stage, feeding the health derivation."""
        return self.record(
            SUCCESS_METRIC if passed else FAILURE_METRIC,
            1.0,
            kind="counter",
            labels={"stage_id": stage_id, **labels},
        )

    # -- derived views ----------------------------------------------------------------

    @property
    def metrics(self) -> tuple[PipelineTelemetry, ...]:
        """Every recorded measurement, in record order."""
        return tuple(self._metrics)

    def __len__(self) -> int:
        return len(self._metrics)

    def names(self) -> tuple[str, ...]:
        """Every distinct metric name recorded, sorted."""
        return tuple(sorted({metric.name for metric in self._metrics}))

    def metrics_named(self, name: str) -> tuple[PipelineTelemetry, ...]:
        """Every measurement recorded under ``name``, in record order."""
        return tuple(metric for metric in self._metrics if metric.name == name)

    def total(self, name: str) -> float:
        """The sum of every value recorded under ``name`` (0.0 when never recorded)."""
        return float(sum(metric.value for metric in self._metrics if metric.name == name))

    def totals(self) -> dict[str, float]:
        """name -> summed value, for every recorded name (sorted, deterministic)."""
        return {name: self.total(name) for name in self.names()}

    def bottlenecks(self, *, limit: int | None = None) -> tuple[tuple[str, float], ...]:
        """``(name, total)`` ranked by recorded magnitude, descending, ties broken by name.

        Raises:
            PipelineObservabilityError: if ``limit`` is not a positive integer.
        """
        if limit is not None and (not isinstance(limit, int) or limit < 1):
            raise PipelineObservabilityError("limit must be a positive integer", limit=limit)
        ranked = sorted(self.totals().items(), key=lambda pair: (-pair[1], pair[0]))
        return tuple(ranked if limit is None else ranked[:limit])

    def health(self) -> dict[str, Any]:
        """The derived health verdict: ``HEALTHY`` unless a failure was recorded."""
        failures = self.total(FAILURE_METRIC)
        successes = self.total(SUCCESS_METRIC)
        return {
            "status": DEGRADED if failures else HEALTHY,
            "failures": failures,
            "successes": successes,
            "observed": successes + failures,
            "metric_count": len(self._metrics),
        }

    def to_dict(self) -> dict[str, Any]:
        """A deterministic, serializable render of recorded telemetry (evidence)."""
        return {
            "metric_count": len(self._metrics),
            "names": list(self.names()),
            "totals": self.totals(),
            "health": self.health(),
            "bottlenecks": [list(pair) for pair in self.bottlenecks()],
            "metrics": [metric.to_dict() for metric in self._metrics],
        }

    def fingerprint(self) -> str:
        """A deterministic content hash of recorded telemetry."""
        return content_hash(self.to_dict())


__all__ = [
    "DEGRADED",
    "FAILURE_METRIC",
    "HEALTHY",
    "SUCCESS_METRIC",
    "TELEMETRY_KINDS",
    "PipelineObservability",
    "PipelineTelemetry",
]
