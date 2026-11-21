"""UCOS-EPIC-006 — Universal Certification Engine error taxonomy (Terminal T6).

The Universal Certification Engine reuses the EC-1 Foundation error discipline
(TASK-000006): every error is rooted in :class:`FoundationError`, carries a stable,
category-prefixed ``code`` and structured, non-secret ``context`` so failures are
auditable (PL-02, IP-12) and machine-consumable.

The engine is *additive* and *record-only*: it consumes already-produced Validation
output, Measurement results, and a Repository-Truth attestation, and **aggregates**
them into an immutable, content-addressed Certificate (it invents no verdict — TP-01),
mutates no subject, and never writes to the certified corpus (DP-03). A malformed
certification subject, a tampered (integrity-broken) certificate, an unauthorized
approval transition, or a corrupted append-only audit chain fails loudly with a
specific error. The base class is named :class:`UniversalCertificationError` so it
never shadows the compiler/foundation/validation/certification error hierarchies.
"""

from __future__ import annotations

from engine.foundation.obs.errors import FoundationError


class UniversalCertificationError(FoundationError):
    """Base class for all Universal Certification Engine errors (UCOS-EPIC-006)."""

    code = "UCERT-000"


class CertificationInputError(UniversalCertificationError):
    """A consumed input (validation, measurement, or repository truth) is malformed."""

    code = "UCERT-INPUT-001"


class CertificationSubjectError(UniversalCertificationError):
    """A certification subject could not be built from the supplied inputs."""

    code = "UCERT-SUBJECT-001"


class ComplianceEvaluationError(UniversalCertificationError):
    """A compliance frame could not be evaluated over the subject."""

    code = "UCERT-COMPLIANCE-001"


class CertificationRuleError(UniversalCertificationError):
    """A certification rule could not be evaluated (a malformed rule or subject)."""

    code = "UCERT-RULE-001"


class CertificateIntegrityError(UniversalCertificationError):
    """An immutable certificate failed its content-hash integrity check."""

    code = "UCERT-INTEGRITY-001"


class ApprovalWorkflowError(UniversalCertificationError):
    """An approval transition was requested that the fail-closed workflow forbids."""

    code = "UCERT-APPROVAL-001"


class AuditIntegrityError(UniversalCertificationError):
    """The append-only certification audit hash chain is broken (tamper-evident)."""

    code = "UCERT-AUDIT-001"


class CertificationPipelineError(UniversalCertificationError):
    """The end-to-end certification pipeline could not complete a stage."""

    code = "UCERT-PIPELINE-001"


__all__ = [
    "UniversalCertificationError",
    "CertificationInputError",
    "CertificationSubjectError",
    "ComplianceEvaluationError",
    "CertificationRuleError",
    "CertificateIntegrityError",
    "ApprovalWorkflowError",
    "AuditIntegrityError",
    "CertificationPipelineError",
]
