"""TASK-000017 — Universal Compiler error taxonomy (EPIC-003).

The compiler reuses the EC-1 Foundation error discipline (TASK-000006): every
error is rooted in :class:`FoundationError`, carries a stable, category-prefixed
``code`` and structured, non-secret ``context`` so failures are auditable
(PL-02, IP-12) and machine-consumable.

Per IMP-007 §17 (Failure Conditions), a compilation fails and halts when a
blueprint is missing, a dependency is missing, a circular dependency exists,
validation fails, certification is missing, or an identity/registry reference
cannot be resolved. Each failure mode maps to a specific error type below and is
surfaced to callers as a Gap Report (:mod:`engine.compiler.gap`).

These types are additive engineering code. They never modify the frozen
Foundation or Registry taxonomies; they specialise the hierarchy for the
compilation surface.
"""

from __future__ import annotations

from engine.foundation.obs.errors import FoundationError


class CompilerError(FoundationError):
    """Base class for all Universal Compiler errors (EPIC-003)."""

    code = "CMP-000"


class ParseError(CompilerError):
    """A blueprint document could not be admitted into the IR (TASK-000019)."""

    code = "CMP-PARSE-001"


class SerializationError(CompilerError):
    """IR serialization or deserialization failed (TASK-000018)."""

    code = "CMP-SERDE-001"


class ValidationError(CompilerError):
    """A blueprint failed structural/traceability/certification validation.

    Raised by the Validation Engine (TASK-000020) and mapped to IMP-007 §17
    failure conditions (validation fails / certification missing).
    """

    code = "CMP-VALID-001"


class CertificationError(ValidationError):
    """An input blueprint is uncertified or references an uncertified source.

    IMP-007 §14/§15/§16 — only certified blueprints are compiled; uncertified or
    unregistered inputs are rejected (Mandatory Rule 4).
    """

    code = "CMP-CERT-001"


class DependencyError(CompilerError):
    """A blueprint dependency is missing or otherwise unresolvable (TASK-000021)."""

    code = "CMP-DEP-001"


class CyclicDependencyError(DependencyError):
    """A circular dependency was detected — the build must fail (TASK-000022).

    IMP-007 §4/§17 — circular dependencies SHALL FAIL (AR-01).
    """

    code = "CMP-DEP-CYCLE-001"


class CompilationError(CompilerError):
    """Lowering the IR to target artifacts failed (TASK-000023)."""

    code = "CMP-COMPILE-001"


class OptimizationError(CompilerError):
    """A semantics-preserving optimization could not be applied (TASK-000024)."""

    code = "CMP-OPT-001"


class PackagingError(CompilerError):
    """Deterministic packaging failed (TASK-000025)."""

    code = "CMP-PKG-001"


class SigningError(CompilerError):
    """Artifact/package signing or SBOM generation failed (TASK-000026)."""

    code = "CMP-SIGN-001"


class PublishingError(CompilerError):
    """Publishing the compiled artifact failed (TASK-000027)."""

    code = "CMP-PUBLISH-001"


class PipelineError(CompilerError):
    """The pipeline orchestrator halted a build (TASK-000028)."""

    code = "CMP-PIPELINE-001"


__all__ = [
    "CompilerError",
    "ParseError",
    "SerializationError",
    "ValidationError",
    "CertificationError",
    "DependencyError",
    "CyclicDependencyError",
    "CompilationError",
    "OptimizationError",
    "PackagingError",
    "SigningError",
    "PublishingError",
    "PipelineError",
]
