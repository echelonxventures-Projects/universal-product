"""UCOS-EPIC-005 — Universal Validation Engine error taxonomy (Terminal T5).

The **Universal Validation Engine** is the platform-layer validation *runtime*: it
performs deterministic, fail-closed, evidence-producing validation of a system across
seven universal domains — Architecture, Implementation, Dependency, Registry, Schema,
Runtime, and Quality — from a single, configuration-driven command.

It reuses the EC-1 / Platform Foundation error discipline additively — it does not
fork or modify it. Every error is rooted in
:class:`~platform.foundation.errors.PlatformError` (itself rooted in the certified EC-1
:class:`~engine.foundation.obs.errors.FoundationError`), carries a stable,
category-prefixed ``code`` (``EC2-UVAL-*``) and structured, non-secret ``context`` so
failures are auditable (PL-02, IP-12) and machine-consumable.

Fail-closed discipline (the mission mandate): a validation rule that cannot prove its
invariant holds — because the evidence it needs is *absent* or *malformed* — records a
**FAIL** finding, never a pass and never a swallowed exception. An exception is raised
**only** for a malformed *engine configuration* (a programming/authoring fault), never
for a legitimate fail-closed verdict, which is always reported as data.
"""

from __future__ import annotations

from platform.foundation.errors import PlatformError


class UniversalValidationError(PlatformError):
    """Base class for all Universal Validation Engine errors (UCOS-EPIC-005)."""

    code = "EC2-UVAL-000"


class ValidationConfigError(UniversalValidationError):
    """The validation configuration is missing, unreadable, or malformed."""

    code = "EC2-UVAL-CONFIG-001"


class ValidationTargetError(UniversalValidationError):
    """A validation target could not be assimilated from the supplied facts."""

    code = "EC2-UVAL-TARGET-001"


class RuleDefinitionError(UniversalValidationError):
    """A validation rule (or rule set) is malformed or names an unknown domain."""

    code = "EC2-UVAL-RULE-001"


class ValidationEngineError(UniversalValidationError):
    """The validation engine/service could not be composed or run."""

    code = "EC2-UVAL-ENGINE-001"


__all__ = [
    "UniversalValidationError",
    "ValidationConfigError",
    "ValidationTargetError",
    "RuleDefinitionError",
    "ValidationEngineError",
]
