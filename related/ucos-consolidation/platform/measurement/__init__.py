"""UCOS Ω∞ — Universal Measurement Engine (``platform.measurement``, UCOS-EPIC-004).

The deterministic, fail-closed runtime that instantiates **UCOS-UMA-001** — the engine
that *measures* the certified corpus. It reconstructs, from the authoritative Registry
Truth (``00-BOOK`` via the certified read-only :class:`~engine.registry.adapter.RegistryAdapter`):

    * an **Enumeration** of the population by dimension (what exists),
    * a **Metric** set of quantitative series (counters + distribution gauges),
    * a traceability **Coverage** measurement over the 13-stage trace spine, and
    * a **Gap** report (structural referential-integrity + completeness gaps),

records each as a content-addressed :class:`Measurement` in an append-only
:class:`MeasurementRegistry`, drives five critical health checks, and emits deterministic
:class:`MeasurementEvidence` for TRACK-001 / certification.

Foundational invariant (UCOS-EPIC-004): **Measurement SHALL consume Registry Truth and
SHALL never create Truth.** The engine reads Truth read-only, measures it, and records
its measurements in a disjoint (``UCOS-UMA*``) identity namespace — a measurement can
never be mistaken for, nor overwrite, a fact. It reuses the certified Foundation contract
machinery and the Observability health model, integrates with GOV-002/005 · TRACK-001 ·
STATUS-001 · DP-03 **by reference**, and modifies no EC-1 module, no prior EC-2 epic, and
no frozen corpus.
"""

from __future__ import annotations

from platform.measurement.contracts import (
    GOVERNANCE_AUTHORITIES,
    MEASUREMENT_CONTRACTS,
    UMA_ID,
    Measurement,
    MeasurementKind,
    Metric,
    MetricKind,
)
from platform.measurement.coverage import CoverageEngine, CoverageMeasurement
from platform.measurement.enumeration import Enumeration, EnumerationEngine
from platform.measurement.errors import (
    MeasurementError,
    MeasurementRegistryError,
    TruthSourceError,
)
from platform.measurement.evidence import MeasurementEvidence
from platform.measurement.gaps import Gap, GapEngine, GapReport
from platform.measurement.health import MeasurementHealth, measurement_health_checks
from platform.measurement.metrics import MetricsEngine, MetricSet
from platform.measurement.registry import MeasurementRegistry
from platform.measurement.service import (
    MeasurementRun,
    MeasurementService,
    build_measurement_service,
)
from platform.measurement.source import (
    InMemoryTruthSource,
    RegistryTruthSource,
    TruthSnapshot,
    TruthSource,
)

__all__ = [
    "UMA_ID",
    "MeasurementKind",
    "Measurement",
    "Metric",
    "MetricKind",
    "MEASUREMENT_CONTRACTS",
    "GOVERNANCE_AUTHORITIES",
    "TruthSnapshot",
    "TruthSource",
    "InMemoryTruthSource",
    "RegistryTruthSource",
    "Enumeration",
    "EnumerationEngine",
    "MetricSet",
    "MetricsEngine",
    "CoverageMeasurement",
    "CoverageEngine",
    "Gap",
    "GapReport",
    "GapEngine",
    "MeasurementRegistry",
    "MeasurementHealth",
    "measurement_health_checks",
    "MeasurementEvidence",
    "MeasurementRun",
    "MeasurementService",
    "build_measurement_service",
    "MeasurementError",
    "TruthSourceError",
    "MeasurementRegistryError",
]
