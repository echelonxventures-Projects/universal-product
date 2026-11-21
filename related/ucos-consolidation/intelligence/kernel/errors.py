"""Kernel error taxonomy — fail-closed, structured, and never silently swallowed.

Every error carries structured context so a gate can report *exactly* which
reference, record, or substrate failed without re-deriving the failure.
"""

from __future__ import annotations

from typing import Any


class KernelError(Exception):
    """Base class: an exception with deterministic, structured context."""

    def __init__(self, message: str, **context: Any) -> None:
        self.message = message
        self.context = {k: v for k, v in sorted(context.items()) if v is not None}
        detail = " ".join(f"{k}={v!r}" for k, v in self.context.items())
        super().__init__(f"{message} ({detail})" if detail else message)

    def to_dict(self) -> dict[str, Any]:
        return {"error": type(self).__name__, "message": self.message, "context": self.context}


class SubstrateUnavailableError(KernelError):
    """A declared substrate surface is missing or unreadable (fail-closed)."""


class SubstrateDeclarationError(KernelError):
    """A substrate declaration is malformed — no verdict may be asserted."""


class UnresolvedReferenceError(KernelError):
    """A content reference does not resolve against canonical knowledge."""


class DuplicateRecordError(KernelError):
    """The same identity was registered twice in an append-only ledger."""


class KnowledgeOnceViolation(KernelError):
    """Identical content was registered under two distinct identities."""


class LedgerIntegrityError(KernelError):
    """The hash-chained ledger journal failed recomputation (tamper-evident)."""


class IdentityDivergenceError(KernelError):
    """A registered identity diverges from the identity assigned at derivation time."""


class ContentDuplicationError(KernelError):
    """Canonical prose was copied into a derived artifact instead of referenced."""


class FormatUnknownError(KernelError):
    """A publication format id is not present in the open format registry."""


__all__ = [
    "KernelError",
    "SubstrateUnavailableError",
    "SubstrateDeclarationError",
    "UnresolvedReferenceError",
    "DuplicateRecordError",
    "KnowledgeOnceViolation",
    "LedgerIntegrityError",
    "IdentityDivergenceError",
    "ContentDuplicationError",
    "FormatUnknownError",
]
