"""EC2-TASK-000145 — Validation Console error taxonomy (EC2-EPIC-010).

The UCOS Platform **Validation Console Runtime** — the L3 realization of the Program
"Validation Explorer" surface (Program §2.1 #9, PC-09 validation inspection + PC-13
search + PC-16 audit, §4 L3/L4) — reuses the EC-1 / Platform Foundation error discipline
additively; it does not fork or modify it. Every validation-console error is rooted in
:class:`~platform.foundation.errors.PlatformError` (itself rooted in the certified EC-1
:class:`~engine.foundation.obs.errors.FoundationError`), carries a stable,
category-prefixed ``code`` (``EC2-VC-*``) and structured, non-secret ``context`` so
failures are auditable (PL-02, IP-12) and machine-consumable by TRACK-001.

The Validation Console Runtime is *additive* over EC-1, the Foundation (L4/L6), the
Identity Layer (L7), and the Observability Layer (L8): it consumes them only through
published contracts / composition roots, never modifies them, and never writes to the
certified corpus (DP-03). It **consumes the certified EC-1 Validation Layer
(``engine.validation``) by reference** — invoking its published, deterministic
``ValidationEngine`` read-only to reproduce the authoritative report/evidence/decision —
and **redefines no check, verdict, gate, severity, or evidence format** (TP-01, no
invention). Every access decision is **fail-closed**: on any doubt the runtime denies
rather than admits, and cross-tenant/cross-workspace access is refused (P3). The console
is strictly read/inspection-oriented: it exposes **no mutation path** to any surfaced
report, evidence, or acceptance decision.
"""

from __future__ import annotations

from platform.foundation.errors import PlatformError


class ValidationConsoleError(PlatformError):
    """Base class for all EC-2 Validation Console Runtime errors."""

    code = "EC2-VC-000"


class ValidationContractError(ValidationConsoleError):
    """A validation-console contract, view, or vocabulary declaration is malformed."""

    code = "EC2-VC-CONTRACT-001"


class ValidationRecordError(ValidationConsoleError):
    """A validation record could not be created or resolved (duplicate/absent/malformed)."""

    code = "EC2-VC-RECORD-001"


class ValidationFidelityError(ValidationConsoleError):
    """A surfaced validation diverges from the certified engine output (fidelity, P6)."""

    code = "EC2-VC-FIDELITY-001"


class ValidationEvidenceError(ValidationConsoleError):
    """A validation evidence reference is malformed or inconsistent with its report."""

    code = "EC2-VC-EVIDENCE-001"


class ValidationStatusError(ValidationConsoleError):
    """A validation derived-status computation is malformed."""

    code = "EC2-VC-STATUS-001"


class ValidationSearchError(ValidationConsoleError):
    """A validation-console search request is malformed."""

    code = "EC2-VC-SEARCH-001"


class ValidationTraceError(ValidationConsoleError):
    """A validation trace (link continuation) is malformed or incomplete."""

    code = "EC2-VC-TRACE-001"


class ValidationAccessError(ValidationConsoleError):
    """A validation-console access/authorization request is denied or malformed (fail-closed)."""

    code = "EC2-VC-ACCESS-001"


class ValidationServiceError(ValidationConsoleError):
    """The validation-console service could not be composed or an operation is malformed."""

    code = "EC2-VC-SERVICE-001"


__all__ = [
    "ValidationConsoleError",
    "ValidationContractError",
    "ValidationRecordError",
    "ValidationFidelityError",
    "ValidationEvidenceError",
    "ValidationStatusError",
    "ValidationSearchError",
    "ValidationTraceError",
    "ValidationAccessError",
    "ValidationServiceError",
]
