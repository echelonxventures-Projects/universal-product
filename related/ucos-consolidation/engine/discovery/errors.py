"""UCOS-EPIC-003 — Universal Discovery Engine error taxonomy.

The Discovery Engine reuses the EC-1 Foundation error discipline (TASK-000006):
every error is rooted in :class:`FoundationError`, carries a stable, category-
prefixed ``code`` and structured, non-secret ``context`` so failures are auditable
(PL-02, IP-12) and machine-consumable.

Discovery is a **read-only** projection over the registry substrate (EPIC-002); it
never mutates the certified corpus (DP-03). These errors specialise the Foundation
taxonomy for the discovery surface.
"""

from __future__ import annotations

from engine.foundation.obs.errors import FoundationError


class DiscoveryError(FoundationError):
    """Base class for all Universal Discovery Engine errors (EPIC-003)."""

    code = "DISC-000"


class DiscoveryDimensionError(DiscoveryError):
    """An unknown or unsupported discovery dimension was requested (EPIC-003)."""

    code = "DISC-DIM-001"


class DiscoveryEvidenceError(DiscoveryError):
    """A discovery evidence artifact could not be emitted (EPIC-003)."""

    code = "DISC-EVID-001"


__all__ = [
    "DiscoveryError",
    "DiscoveryDimensionError",
    "DiscoveryEvidenceError",
]
