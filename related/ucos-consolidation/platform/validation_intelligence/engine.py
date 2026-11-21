"""UCOS-EPIC-013 — Continuous Validation Intelligence engine (Terminal T5).

The :class:`ContinuousValidationIntelligenceEngine` is the single conductor of the
intelligence *runtime*: it runs a suite of
:class:`~platform.validation_intelligence.analyzers.DimensionAnalyzer` objects over a
normalized :class:`~platform.validation_intelligence.contracts.IntelligenceTarget`,
groups their findings by dimension, and aggregates them into a deterministic,
content-addressed
:class:`~platform.validation_intelligence.contracts.ValidationIntelligenceReport` (from
which the dashboard, Compatibility Report, and Compliance Report are projected).

Execution is:

    * **deterministic** — analyzers run in stable ``(dimension-order, analyzer-order)``
      order and the report embeds no wall-clock or ambient state, so an identical target
      analyzed by an identical suite yields a byte-identical report and content hash
      (IMP-007 §5);
    * **fail-closed** — a dimension's verdict is FAIL iff any *blocking* finding failed,
      and the run verdict is FAIL iff any dimension failed; advisory failures are recorded
      as evidence but never fail the verdict; and
    * **evidence-producing** — every finding is captured in the report, and the report is
      the input to
      :func:`~platform.validation_intelligence.evidence.build_validation_intelligence_evidence`.

The engine invents no verdict beyond aggregating its analyzers (TP-01) and never mutates
a target or writes to the certified corpus (DP-03).
"""

from __future__ import annotations

from collections.abc import Iterable
from platform.validation_intelligence.analyzers import DimensionAnalyzer, default_analyzers
from platform.validation_intelligence.contracts import (
    DimensionReport,
    IntelligenceDimension,
    IntelligenceTarget,
    ValidationIntelligenceReport,
)
from platform.validation_intelligence.errors import IntelligenceEngineError

from engine.foundation.obs.logging import get_logger
from engine.foundation.obs.telemetry import trace

_logger = get_logger("validation_intelligence.engine")


class ContinuousValidationIntelligenceEngine:
    """Runs a deterministic, fail-closed suite of analyzers over an intelligence target."""

    __slots__ = ("_analyzers",)

    def __init__(
        self,
        analyzers: Iterable[DimensionAnalyzer] | None = None,
        *,
        dimensions: Iterable[IntelligenceDimension] | None = None,
    ) -> None:
        selected = tuple(analyzers) if analyzers is not None else default_analyzers()
        if dimensions is not None:
            allowed = set(dimensions)
            if not allowed:
                raise IntelligenceEngineError(
                    "at least one intelligence dimension must be selected"
                )
            selected = tuple(a for a in selected if a.dimension in allowed)
        if not selected:
            raise IntelligenceEngineError("the intelligence engine has no analyzers to run")
        # Stable (dimension-order, dimension-value) ordering guarantees determinism.
        self._analyzers = tuple(
            sorted(selected, key=lambda a: (a.dimension.order, a.dimension.value))
        )

    @property
    def dimensions(self) -> tuple[IntelligenceDimension, ...]:
        """The distinct dimensions covered by the suite, in canonical order."""
        seen: dict[IntelligenceDimension, None] = {}
        for analyzer in self._analyzers:
            seen.setdefault(analyzer.dimension, None)
        return tuple(sorted(seen, key=lambda d: d.order))

    def analyze(self, target: IntelligenceTarget) -> ValidationIntelligenceReport:
        """Evaluate every analyzer over ``target`` and aggregate a content-addressed report."""
        if not isinstance(target, IntelligenceTarget):
            raise IntelligenceEngineError("a valid IntelligenceTarget is required")
        with trace("validation_intelligence.analyze", target=target.target_id):
            grouped: dict[IntelligenceDimension, list] = {d: [] for d in self.dimensions}
            for analyzer in self._analyzers:
                grouped[analyzer.dimension].extend(analyzer.analyze(target))
            dimension_reports = tuple(
                DimensionReport.create(dimension, tuple(grouped[dimension]))
                for dimension in self.dimensions
            )
            report = ValidationIntelligenceReport.create(
                target_id=target.target_id,
                target_digest=target.digest(),
                dimension_reports=dimension_reports,
            )
        _logger.info(
            "validation_intelligence.completed",
            target=target.target_id,
            verdict=report.verdict.value,
            dimensions=len(dimension_reports),
            blocking_failed=len(report.blocking_failures()),
        )
        return report


__all__ = ["ContinuousValidationIntelligenceEngine"]
