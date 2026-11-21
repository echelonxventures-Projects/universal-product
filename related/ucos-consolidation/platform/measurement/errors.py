"""UCOS-EPIC-004 — Universal Measurement Engine error taxonomy (UCOS-UMA-001).

The Universal Measurement Engine (``platform/measurement/``) is a strictly **additive**
platform package authorized by UCOS-EPIC-004 to instantiate UCOS-UMA-001 — the runtime
that *measures* the certified corpus without ever authoring it. Like every prior EC-2
layer it **reuses** the certified EC-1 / EC-2 Foundation error discipline: every
measurement error is rooted in :class:`~platform.foundation.errors.PlatformError`,
carries a stable ``EC2-UMA-*`` code and structured, non-secret context so failures are
auditable (PL-02, IP-12) and machine-consumable by TRACK-001.

The engine invents no authority and, above all, **creates no Truth** — it reads the
authoritative Registry substrate (``00-BOOK`` via the read-only
:class:`~engine.registry.adapter.RegistryAdapter`) and fails **closed**: absent or
malformed Truth raises a specific error rather than fabricating a measurement.
"""

from __future__ import annotations

from platform.foundation.errors import PlatformError


class MeasurementError(PlatformError):
    """Base class for all Universal Measurement Engine (UMA-001) errors."""

    code = "EC2-UMA-000"


class MeasurementContractError(MeasurementError):
    """A measurement vocabulary value (kind, metric, measurement) is malformed."""

    code = "EC2-UMA-CONTRACT-001"


class TruthSourceError(MeasurementError):
    """Registry Truth is missing, malformed, or non-authoritative (fail-closed).

    Also raised on any attempt to treat the measurement runtime as a Truth author —
    Measurement SHALL consume Truth and SHALL never create it.
    """

    code = "EC2-UMA-TRUTH-001"


class EnumerationError(MeasurementError):
    """A population-enumeration measurement could not be produced (fail-closed)."""

    code = "EC2-UMA-ENUM-001"


class MetricsError(MeasurementError):
    """A quantitative-metric measurement is malformed or could not be produced."""

    code = "EC2-UMA-METRIC-001"


class CoverageMeasurementError(MeasurementError):
    """A traceability-coverage measurement could not be produced (fail-closed)."""

    code = "EC2-UMA-COVERAGE-001"


class GapMeasurementError(MeasurementError):
    """A gap measurement could not be produced (fail-closed)."""

    code = "EC2-UMA-GAP-001"


class MeasurementRegistryError(MeasurementError):
    """A measurement-registry operation is malformed or violates append-only discipline."""

    code = "EC2-UMA-REGISTRY-001"


class MeasurementEngineError(MeasurementError):
    """A measurement compute/verify/report operation failed fail-closed."""

    code = "EC2-UMA-ENGINE-001"


class MeasurementEvidenceError(MeasurementError):
    """A measurement evidence artifact could not be produced or failed closed."""

    code = "EC2-UMA-EVIDENCE-001"


__all__ = [
    "MeasurementError",
    "MeasurementContractError",
    "TruthSourceError",
    "EnumerationError",
    "MetricsError",
    "CoverageMeasurementError",
    "GapMeasurementError",
    "MeasurementRegistryError",
    "MeasurementEngineError",
    "MeasurementEvidenceError",
]
