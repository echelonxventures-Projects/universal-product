"""EC2-TASK-000127 — Execution Dashboard error taxonomy (EC2-EPIC-008).

The UCOS Platform **Execution Dashboard Runtime** — the L3 realization of the Program
"Execution Dashboard" surface (Program §2.1 #8/#10, PC-08 execution visibility + PC-13
search + PC-16 audit, §4 L3) — reuses the EC-1 / Platform Foundation error discipline
additively; it does not fork or modify it. Every dashboard error is rooted in
:class:`~platform.foundation.errors.PlatformError` (itself rooted in the certified EC-1
:class:`~engine.foundation.obs.errors.FoundationError`), carries a stable,
category-prefixed ``code`` (``EC2-ED-*``) and structured, non-secret ``context`` so
failures are auditable (PL-02, IP-12) and machine-consumable by TRACK-001.

The Execution Dashboard Runtime is *additive* over EC-1, the Foundation (L4/L6), the
Identity Layer (L7), the Observability Layer (L8), and the Generation Request Runtime
(L3, EPIC-007): it consumes them only through published contracts / composition roots,
never modifies them, and never writes to the certified corpus (DP-03). It **consumes the
Generation Request Runtime by reference** — reading the certified
:class:`~platform.generation.registry.GenerationRequestRegistry`, derived status, search,
and health read-only to surface operational visibility — and **implements no execution,
generation, engine, lifecycle, or registry logic of its own** (observability & navigation
only). Every access decision is **fail-closed**: on any doubt the runtime denies rather
than admits, and cross-tenant/cross-workspace access is refused (P3). The dashboard is
strictly read/inspection-oriented: it exposes **no mutation path** to any request,
dispatch, or lifecycle datum.
"""

from __future__ import annotations

from platform.foundation.errors import PlatformError


class ExecutionDashboardError(PlatformError):
    """Base class for all EC-2 Execution Dashboard Runtime errors."""

    code = "EC2-ED-000"


class DashboardContractError(ExecutionDashboardError):
    """A dashboard contract, view, or vocabulary declaration is malformed."""

    code = "EC2-ED-CONTRACT-001"


class DashboardViewError(ExecutionDashboardError):
    """A dashboard view projection is malformed or inconsistent with its source."""

    code = "EC2-ED-VIEW-001"


class DashboardSearchError(ExecutionDashboardError):
    """An execution-dashboard search request is malformed."""

    code = "EC2-ED-SEARCH-001"


class DashboardHealthError(ExecutionDashboardError):
    """An execution-dashboard health probe is malformed or inconsistent."""

    code = "EC2-ED-HEALTH-001"


class DashboardAccessError(ExecutionDashboardError):
    """An execution-dashboard access/authorization request is denied or malformed (fail-closed)."""

    code = "EC2-ED-ACCESS-001"


class DashboardServiceError(ExecutionDashboardError):
    """The execution-dashboard service could not be composed or an operation is malformed."""

    code = "EC2-ED-SERVICE-001"


__all__ = [
    "ExecutionDashboardError",
    "DashboardContractError",
    "DashboardViewError",
    "DashboardSearchError",
    "DashboardHealthError",
    "DashboardAccessError",
    "DashboardServiceError",
]
