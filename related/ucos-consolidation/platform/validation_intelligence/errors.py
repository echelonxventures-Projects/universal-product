"""UCOS-EPIC-013 — Continuous Validation Intelligence error taxonomy (Terminal T5).

EPIC-013 **expands validation beyond static rule execution** (EPIC-005). Where the
Universal Validation Engine runs a fixed suite of per-target rules, the Continuous
Validation *Intelligence* engine reasons across capabilities, across a repository's
declared completeness, and across *baseline↔candidate* deltas to determine
compatibility and compliance — producing Validation Intelligence Reports, a
Compatibility Engine verdict, Compliance Reports, and content-addressed evidence.

It reuses the EC-1 / Platform Foundation error discipline additively — it does not
fork or modify it. Every error is rooted in
:class:`~platform.foundation.errors.PlatformError` (itself rooted in the certified EC-1
:class:`~engine.foundation.obs.errors.FoundationError`), carries a stable,
category-prefixed ``code`` (``EC2-CVI-*``) and structured, non-secret ``context`` so
failures are auditable (PL-02, IP-12) and machine-consumable.

Fail-closed discipline (the mission mandate): an analyzer that cannot *prove* its
invariant holds — because the evidence it needs is *absent* or *malformed* — records a
**FAIL** finding, never a pass and never a swallowed exception. An exception is raised
**only** for a malformed *engine configuration* (a programming/authoring fault), never
for a legitimate fail-closed verdict, which is always reported as data.
"""

from __future__ import annotations

from platform.foundation.errors import PlatformError


class ValidationIntelligenceError(PlatformError):
    """Base class for all Continuous Validation Intelligence errors (UCOS-EPIC-013)."""

    code = "EC2-CVI-000"


class IntelligenceConfigError(ValidationIntelligenceError):
    """The validation-intelligence configuration is missing, unreadable, or malformed."""

    code = "EC2-CVI-CONFIG-001"


class IntelligenceTargetError(ValidationIntelligenceError):
    """An intelligence target could not be assimilated from the supplied facts."""

    code = "EC2-CVI-TARGET-001"


class AnalyzerDefinitionError(ValidationIntelligenceError):
    """An analyzer (or analyzer set) is malformed or names an unknown dimension."""

    code = "EC2-CVI-ANALYZER-001"


class IntelligenceEngineError(ValidationIntelligenceError):
    """The intelligence engine/service could not be composed or run."""

    code = "EC2-CVI-ENGINE-001"


class CompatibilityError(ValidationIntelligenceError):
    """The Compatibility Engine could not compare a baseline against a candidate."""

    code = "EC2-CVI-COMPAT-001"


__all__ = [
    "ValidationIntelligenceError",
    "IntelligenceConfigError",
    "IntelligenceTargetError",
    "AnalyzerDefinitionError",
    "IntelligenceEngineError",
    "CompatibilityError",
]
