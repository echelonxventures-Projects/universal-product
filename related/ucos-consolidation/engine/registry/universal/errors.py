"""UCOS-EPIC-001 — Universal Registry Platform error taxonomy.

The registration authority reuses the EC-1 Registry / Foundation error discipline:
every error is rooted in :class:`RegistryError` (in turn a
:class:`~engine.foundation.obs.errors.FoundationError`), carries a stable,
category-prefixed ``code`` and structured, non-secret ``context`` so that a
refused registration is auditable (PL-02, IP-12) and machine-consumable.

These types are additive engineering code (EG-001): they specialise the frozen
registry taxonomy for the *write* surface (registration authority) and modify no
existing taxonomy.
"""

from __future__ import annotations

from engine.registry.errors import RegistryError


class RegistrationError(RegistryError):
    """Base class for all Universal Registry Platform (write-side) errors."""

    code = "REG-PLAT-000"


class RegistrationValidationError(RegistrationError):
    """A registration request failed validation against its required shape."""

    code = "REG-PLAT-VALID-400"


class NamespaceError(RegistrationError):
    """A namespace value is malformed or is not a registered namespace."""

    code = "REG-PLAT-NS-400"


class DuplicateRegistrationError(RegistrationError):
    """A registration for the same (universal_id, version) already exists.

    Enforces the constitutional rule *No duplicate registrations* — the same
    artifact version is never registered twice (append-only, supersede-not-
    overwrite; INV-10 / CFP-008 discipline).
    """

    code = "REG-PLAT-DUP-409"


class KnowledgeOnceViolation(RegistrationError):
    """Identical content is already registered under a different universal_id.

    Enforces the constitutional rule *Knowledge Once* — a single canonical home
    per unit of knowledge; the same content may not be registered twice under
    distinct identities.
    """

    code = "REG-PLAT-KO-409"


class VersionConflictError(RegistrationError):
    """A version violates the version-ordering discipline for its identity.

    Raised when a registered version is not strictly newer than the current
    active version within the same major line (supersede-not-overwrite, PL-05).
    """

    code = "REG-PLAT-VER-409"


class RegistrationNotFoundError(RegistrationError):
    """A requested registration (identity or version) is not present."""

    code = "REG-PLAT-404"


class DependencyError(RegistrationError):
    """A declared dependency is unknown or would introduce a cycle (DC-2)."""

    code = "REG-PLAT-DEP-409"


class AuditIntegrityError(RegistrationError):
    """The append-only audit journal failed its hash-chain integrity check."""

    code = "REG-PLAT-AUD-500"


__all__ = [
    "RegistrationError",
    "RegistrationValidationError",
    "NamespaceError",
    "DuplicateRegistrationError",
    "KnowledgeOnceViolation",
    "VersionConflictError",
    "RegistrationNotFoundError",
    "DependencyError",
    "AuditIntegrityError",
]
