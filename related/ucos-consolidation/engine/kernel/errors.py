"""Universal Meta-Kernel errors.

Every failure mode of the kernel is a subclass of :class:`KernelError`, so a provider
may catch the whole kernel error surface with one type. Errors carry structured context
(keyword details) rather than only a message, so evidence remains machine-readable.
"""

from __future__ import annotations

from typing import Any


class KernelError(Exception):
    """Base class for every Universal Meta-Kernel error."""

    def __init__(self, message: str, **context: Any) -> None:
        super().__init__(message)
        self.message = message
        self.context = context

    def __str__(self) -> str:
        if not self.context:
            return self.message
        rendered = ", ".join(f"{k}={v!r}" for k, v in sorted(self.context.items()))
        return f"{self.message} ({rendered})"

    def to_dict(self) -> dict[str, Any]:
        """A deterministic, serialisable rendering of the error."""
        return {"error": type(self).__name__, "message": self.message, "context": self.context}


class IdentityError(KernelError):
    """A malformed identity segment (metatype ref, namespace, or natural key)."""


class MetaTypeUnknownError(KernelError):
    """A meta-object was classified by a meta-type that is not registered.

    This is the constitutional guard that makes the type system *open by registration*:
    a new concept-category is admitted by first registering its meta-type, never by
    editing kernel code.
    """


class DuplicateRegistrationError(KernelError):
    """The same identity + version, or identical content, was registered twice."""


class KnowledgeOnceViolation(KernelError):
    """Identical content was registered under two different identities."""


class VersionError(KernelError):
    """A version did not strictly supersede the current head of an identity chain."""


class RelationshipError(KernelError):
    """A relationship edge is malformed or would introduce a cycle."""


class GovernanceRejection(KernelError):
    """A governed admission was denied by one or more constraints."""

    def __init__(self, message: str, *, reasons: list[str], **context: Any) -> None:
        super().__init__(message, reasons=reasons, **context)
        self.reasons = reasons


class RegistrationNotFoundError(KernelError):
    """A lookup referenced an identity or version that is not registered."""


class AuditIntegrityError(KernelError):
    """The append-only audit chain failed hash-linkage verification."""


__all__ = [
    "KernelError",
    "IdentityError",
    "MetaTypeUnknownError",
    "DuplicateRegistrationError",
    "KnowledgeOnceViolation",
    "VersionError",
    "RelationshipError",
    "GovernanceRejection",
    "RegistrationNotFoundError",
    "AuditIntegrityError",
]
