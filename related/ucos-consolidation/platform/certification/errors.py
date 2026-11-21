"""EC2-TASK-000153 — Certification Console error taxonomy (EC2-EPIC-011).

The UCOS Platform **Certification Console & Ledger Runtime** — the L3 realization of the
Program "Certification Explorer / Ledger" surface (Program §2.1 #10, PC-10 certification
inspection & ledger + PC-13 search + PC-16 audit, §4 L3/L4) — reuses the EC-1 / Platform
Foundation error discipline additively; it does not fork or modify it. Every
certification-console error is rooted in
:class:`~platform.foundation.errors.PlatformError` (itself rooted in the certified EC-1
:class:`~engine.foundation.obs.errors.FoundationError`), carries a stable,
category-prefixed ``code`` (``EC2-CC-*``) and structured, non-secret ``context`` so
failures are auditable (PL-02, IP-12) and machine-consumable by TRACK-001.

The Certification Console Runtime is *additive* over EC-1, the Foundation (L4/L6), the
Identity Layer (L7), and the Observability Layer (L8): it consumes them only through
published contracts / composition roots, never modifies them, and never writes to the
certified corpus (DP-03). It **consumes the certified EC-1 Certification Layer
(``engine.certification``) by reference** — invoking its published, deterministic
``CertificationEngine`` read-only to reproduce the authoritative decision / record /
evidence over already-certified validation output — and **redefines no criterion,
verdict, ledger rule, severity, or evidence format** (TP-01, no invention). Every access
decision is **fail-closed**: on any doubt the runtime denies rather than admits, and
cross-tenant/cross-workspace access is refused (P3). The console is strictly
read/inspection-oriented: it exposes **no mutation path** to any surfaced certification
record, evidence, or ledger entry (the certification ledger is append-only by
construction).
"""

from __future__ import annotations

from platform.foundation.errors import PlatformError


class CertificationConsoleError(PlatformError):
    """Base class for all EC-2 Certification Console Runtime errors."""

    code = "EC2-CC-000"


class CertificationContractError(CertificationConsoleError):
    """A certification-console contract, view, or vocabulary declaration is malformed."""

    code = "EC2-CC-CONTRACT-001"


class CertificationRecordError(CertificationConsoleError):
    """A certification record could not be created or resolved (duplicate/absent/malformed)."""

    code = "EC2-CC-RECORD-001"


class CertificationFidelityError(CertificationConsoleError):
    """A surfaced certification diverges from the certified engine output (fidelity, P6)."""

    code = "EC2-CC-FIDELITY-001"


class CertificationEvidenceError(CertificationConsoleError):
    """A certification evidence reference is malformed or inconsistent with its record."""

    code = "EC2-CC-EVIDENCE-001"


class CertificationStatusError(CertificationConsoleError):
    """A certification derived-status, readiness, or governance computation is malformed."""

    code = "EC2-CC-STATUS-001"


class CertificationSearchError(CertificationConsoleError):
    """A certification-console search request is malformed."""

    code = "EC2-CC-SEARCH-001"


class CertificationLedgerError(CertificationConsoleError):
    """A certification ledger access, traversal, or append request is malformed."""

    code = "EC2-CC-LEDGER-001"


class CertificationLineageError(CertificationConsoleError):
    """A certification lineage (parent-child/ancestry) request is malformed or incomplete."""

    code = "EC2-CC-LINEAGE-001"


class CertificationAccessError(CertificationConsoleError):
    """A certification-console access/authorization request is denied or malformed (fail-closed)."""

    code = "EC2-CC-ACCESS-001"


class CertificationServiceError(CertificationConsoleError):
    """The certification-console service could not be composed or an operation is malformed."""

    code = "EC2-CC-SERVICE-001"


__all__ = [
    "CertificationConsoleError",
    "CertificationContractError",
    "CertificationRecordError",
    "CertificationFidelityError",
    "CertificationEvidenceError",
    "CertificationStatusError",
    "CertificationSearchError",
    "CertificationLedgerError",
    "CertificationLineageError",
    "CertificationAccessError",
    "CertificationServiceError",
]
