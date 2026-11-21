"""TASK-000010 — Registry Adapter error taxonomy (EPIC-002).

The Registry Adapter reuses the EC-1 Foundation error discipline (TASK-000006):
every error is rooted in :class:`FoundationError`, carries a stable, category-
prefixed ``code`` and structured, non-secret ``context`` so failures are auditable
(PL-02, IP-12) and machine-consumable.

These types are additive engineering code. They never modify the frozen Foundation
taxonomy; they specialise it for the read-only registry surface over ``00-BOOK``.
"""

from __future__ import annotations

from engine.foundation.obs.errors import FoundationError


class RegistryError(FoundationError):
    """Base class for all Registry Adapter errors (EPIC-002)."""

    code = "REG-000"


class RegistrySourceError(RegistryError):
    """The read-only registry substrate could not be located or read (TASK-000010)."""

    code = "REG-SOURCE-001"


class RegistryDataError(RegistryError):
    """A registry data file was missing, malformed, or structurally invalid (TASK-000010)."""

    code = "REG-DATA-001"


class RegistryValidationError(RegistryError):
    """A registry record failed model validation against its schema shape (TASK-000011)."""

    code = "REG-VALID-001"


class ArtifactNotFoundError(RegistryError):
    """A requested artifact is absent from the registry (TASK-000012)."""

    code = "REG-ARTIFACT-404"


class VolumeNotFoundError(RegistryError):
    """A requested volume is absent from the registry (TASK-000014)."""

    code = "REG-VOLUME-404"


__all__ = [
    "RegistryError",
    "RegistrySourceError",
    "RegistryDataError",
    "RegistryValidationError",
    "ArtifactNotFoundError",
    "VolumeNotFoundError",
]
