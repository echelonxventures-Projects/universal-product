"""EC2-TASK-000163 — Runtime Operations error taxonomy (EC2-EPIC-012).

The UCOS Platform **Runtime Operations Runtime** — the L8 realization of the Program
"Runtime Operations" surface (Program §2.1 #11, PC-11 runtime deploy/rollback operations,
§4 L4/L8) — reuses the EC-1 / Platform Foundation error discipline additively; it does not
fork or modify it. Every runtime-operations error is rooted in
:class:`~platform.foundation.errors.PlatformError` (itself rooted in the certified EC-1
:class:`~engine.foundation.obs.errors.FoundationError`), carries a stable,
category-prefixed ``code`` (``EC2-RO-*``) and structured, non-secret ``context`` so
failures are auditable (PL-02, IP-12) and machine-consumable by TRACK-001.

The Runtime Operations Runtime is *additive* over EC-1, the Foundation (L4/L6), the
Identity Layer (L7), the Certification Layer (EC2-EPIC-011), and the Observability Layer
(L8): it consumes them only through published contracts / composition roots, never
modifies them, and never writes to the certified corpus (DP-03). It **governs and records
only** — it invokes no deployment logic of its own; the actual runtime execution remains
inside EC-1. It **consumes the certified EC-1 Runtime Assembly engine
(``engine.runtime``) by reference** — invoking its published, deterministic descriptor /
rollback factories read-only to obtain the authoritative deployment / rollback
descriptors of an already-assembled runtime unit — and **redefines no descriptor format,
rollback strategy, disclosure, or reversibility rule** (TP-01, no invention). It consumes
certification status from the certified :mod:`platform.certification` layer. Every
admission decision is **fail-closed**: only a CERTIFIED unit may be deployed or rolled
back, and cross-tenant/cross-workspace access is refused (P3). The runtime is strictly
operate/record-oriented: it exposes **no mutation path** to any surfaced descriptor,
certification record, or ledger entry (the runtime-operation ledger is append-only by
construction).
"""

from __future__ import annotations

from platform.foundation.errors import PlatformError


class RuntimeOperationsError(PlatformError):
    """Base class for all EC-2 Runtime Operations Runtime errors."""

    code = "EC2-RO-000"


class RuntimeOperationsContractError(RuntimeOperationsError):
    """A runtime-operations contract, view, or vocabulary declaration is malformed."""

    code = "EC2-RO-CONTRACT-001"


class RuntimeOperationRecordError(RuntimeOperationsError):
    """A runtime-operation record could not be created or resolved (duplicate/absent/malformed)."""

    code = "EC2-RO-RECORD-001"


class RuntimeDescriptorError(RuntimeOperationsError):
    """A deployment/rollback descriptor is malformed or could not be produced by reference."""

    code = "EC2-RO-DESCRIPTOR-001"


class RuntimeAdmissionError(RuntimeOperationsError):
    """A deploy/rollback admission is denied — a non-CERTIFIED or unpinned unit (fail-closed)."""

    code = "EC2-RO-ADMISSION-001"


class RuntimeFidelityError(RuntimeOperationsError):
    """A recorded descriptor diverges from a fresh EC-1 reproduction (fidelity, P6)."""

    code = "EC2-RO-FIDELITY-001"


class RuntimeReversibilityError(RuntimeOperationsError):
    """A rollback operation fails the reversibility proof (IP-08) or is malformed."""

    code = "EC2-RO-REVERSIBILITY-001"


class RuntimeOperationStatusError(RuntimeOperationsError):
    """A runtime-operation derived-status or governance computation is malformed."""

    code = "EC2-RO-STATUS-001"


class RuntimeOperationSearchError(RuntimeOperationsError):
    """A runtime-operation search request is malformed."""

    code = "EC2-RO-SEARCH-001"


class RuntimeOperationLedgerError(RuntimeOperationsError):
    """A runtime-operation ledger access, traversal, or append request is malformed."""

    code = "EC2-RO-LEDGER-001"


class RuntimeOperationLineageError(RuntimeOperationsError):
    """A runtime-operation lineage (parent-child/ancestry) request is malformed or incomplete."""

    code = "EC2-RO-LINEAGE-001"


class RuntimeOperationAccessError(RuntimeOperationsError):
    """A runtime-operations access/authorization request is denied or malformed (fail-closed)."""

    code = "EC2-RO-ACCESS-001"


class RuntimeOperationServiceError(RuntimeOperationsError):
    """The runtime-operations service could not be composed or an operation is malformed."""

    code = "EC2-RO-SERVICE-001"


__all__ = [
    "RuntimeOperationsError",
    "RuntimeOperationsContractError",
    "RuntimeOperationRecordError",
    "RuntimeDescriptorError",
    "RuntimeAdmissionError",
    "RuntimeFidelityError",
    "RuntimeReversibilityError",
    "RuntimeOperationStatusError",
    "RuntimeOperationSearchError",
    "RuntimeOperationLedgerError",
    "RuntimeOperationLineageError",
    "RuntimeOperationAccessError",
    "RuntimeOperationServiceError",
]
