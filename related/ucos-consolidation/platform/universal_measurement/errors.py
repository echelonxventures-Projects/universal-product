"""UCOS-UMPF-001 — Universal Measurement Policy Framework error taxonomy.

The Universal Measurement Policy Framework (``platform/universal_measurement/``) is a
strictly **additive** platform package in which every measurement — coverage, homed,
upload-only, assimilation, ownership, completeness, and every measurement a future project
needs — is a **registered policy** rather than a branch inside one engine.

It reuses the certified Foundation error discipline: every error is rooted in
:class:`~platform.foundation.errors.PlatformError`, carries a stable ``EC2-UMPF-*`` code and
structured, non-secret context (PL-02, IP-12), and fails **closed** — a policy that cannot
be evaluated honestly raises rather than reporting a comfortable zero.
"""

from __future__ import annotations

from platform.foundation.errors import PlatformError


class MeasurementPolicyError(PlatformError):
    """Base class for all Universal Measurement Policy Framework (UMPF-001) errors."""

    code = "EC2-UMPF-000"


class MeasurementPolicyContractError(MeasurementPolicyError):
    """A policy descriptor, context, or outcome is malformed."""

    code = "EC2-UMPF-CONTRACT-001"


class MeasurementPolicyRegistryError(MeasurementPolicyError):
    """A policy registry operation is malformed or violates registration discipline."""

    code = "EC2-UMPF-REGISTRY-001"


class MeasurementPolicyEvaluationError(MeasurementPolicyError):
    """A policy could not be evaluated over the supplied context (fail-closed)."""

    code = "EC2-UMPF-EVALUATION-001"


class MeasurementContextError(MeasurementPolicyError):
    """The measurement context lacks a determination a policy requires (fail-closed).

    A policy SHALL NOT report a measurement it could not make. An absent determination is
    an error, never a zero.
    """

    code = "EC2-UMPF-CONTEXT-001"


__all__ = [
    "MeasurementPolicyError",
    "MeasurementPolicyContractError",
    "MeasurementPolicyRegistryError",
    "MeasurementPolicyEvaluationError",
    "MeasurementContextError",
]
