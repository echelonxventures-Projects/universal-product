"""UCOS-EPIC-014 — Universal Assurance error taxonomy (Terminal T7).

The **Universal Assurance Engine** owns *Validation Intelligence* and *Certification
Intelligence* end to end: it plans, generates, executes, collects evidence for,
certifies, registers, and reasons about validation and certification — entirely from a
declared **policy**, with every stage **measured** and every determination
**reproducible**.

It reuses the EC-1 / Platform Foundation error discipline additively — it does not fork
or modify it. Every error is rooted in
:class:`~platform.foundation.errors.PlatformError` (itself rooted in the certified EC-1
:class:`~engine.foundation.obs.errors.FoundationError`), carries a stable,
category-prefixed ``code`` (``EC2-UASR-*``) and structured, non-secret ``context`` so
failures are auditable (PL-02, IP-12) and machine-consumable.

Fail-closed discipline (the mission mandate): a stage that cannot *prove* its
obligation was discharged — because the evidence it needs is *absent*, *malformed*, or
*unbindable* — records a **FAIL** outcome, never a pass and never a silent skip. An
exception is raised **only** for a malformed *policy* or *configuration* (an authoring
fault), never for a legitimate fail-closed verdict, which is always reported as data.
"""

from __future__ import annotations

from platform.foundation.errors import PlatformError


class UniversalAssuranceError(PlatformError):
    """Base class for all Universal Assurance errors (UCOS-EPIC-014)."""

    code = "EC2-UASR-000"


class AssurancePolicyError(UniversalAssuranceError):
    """The assurance policy is missing, unreadable, or malformed."""

    code = "EC2-UASR-POLICY-001"


class AssuranceConfigError(UniversalAssuranceError):
    """The assurance run configuration is missing, unreadable, or malformed."""

    code = "EC2-UASR-CONFIG-001"


class AssuranceSubjectError(UniversalAssuranceError):
    """An assurance subject could not be assimilated from the supplied facts."""

    code = "EC2-UASR-SUBJECT-001"


class AssurancePlanError(UniversalAssuranceError):
    """A validation or certification plan could not be synthesized from the policy."""

    code = "EC2-UASR-PLAN-001"


class AssuranceGenerationError(UniversalAssuranceError):
    """A validation suite could not be generated from a plan."""

    code = "EC2-UASR-GEN-001"


class AssuranceExecutionError(UniversalAssuranceError):
    """A validation or certification execution could not be composed or run."""

    code = "EC2-UASR-EXEC-001"


class AssuranceEvidenceError(UniversalAssuranceError):
    """Evidence could not be collected, is incomplete, or its write scope is forbidden."""

    code = "EC2-UASR-EVID-001"


class AssuranceRegistryError(UniversalAssuranceError):
    """The certification registry rejected a registration or failed its integrity check."""

    code = "EC2-UASR-REG-001"


class AssuranceMeasurementError(UniversalAssuranceError):
    """A declared metric could not be measured from the supplied observations."""

    code = "EC2-UASR-MEAS-001"


class AssuranceIntelligenceError(UniversalAssuranceError):
    """Validation or certification intelligence could not be composed or run."""

    code = "EC2-UASR-INTEL-001"


class AssuranceReproducibilityError(UniversalAssuranceError):
    """A reproducibility replay could not be performed."""

    code = "EC2-UASR-REPRO-001"


__all__ = [
    "UniversalAssuranceError",
    "AssurancePolicyError",
    "AssuranceConfigError",
    "AssuranceSubjectError",
    "AssurancePlanError",
    "AssuranceGenerationError",
    "AssuranceExecutionError",
    "AssuranceEvidenceError",
    "AssuranceRegistryError",
    "AssuranceMeasurementError",
    "AssuranceIntelligenceError",
    "AssuranceReproducibilityError",
]
