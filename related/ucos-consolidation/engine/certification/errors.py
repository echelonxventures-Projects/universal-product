"""TASK-000050 — Certification Layer error taxonomy (EPIC-008).

The Certification Layer reuses the EC-1 Foundation error discipline (TASK-000006):
every error is rooted in :class:`FoundationError`, carries a stable,
category-prefixed ``code`` and structured, non-secret ``context`` so failures are
auditable (PL-02, IP-12) and machine-consumable.

The Certification Layer is *additive and record-only*: it consumes already-produced
Validation Reports and Validation Evidence (EPIC-007) and **aggregates** their
verdicts into an immutable certification record — it invents no verdict (TP-01),
mutates no subject, and never writes to the certified corpus (DP-03). A malformed
certification subject, a tampered (integrity-broken) certification record, or a
corrupted append-only ledger chain fails loudly with a specific error. The base
class is named :class:`CertificationLayerError` so it never shadows the
compiler/foundation/validation error hierarchies.
"""

from __future__ import annotations

from engine.foundation.obs.errors import FoundationError


class CertificationLayerError(FoundationError):
    """Base class for all Certification Layer errors (EPIC-008)."""

    code = "CERT-000"


class CertificationSubjectError(CertificationLayerError):
    """A certification subject could not be built from the supplied validation input."""

    code = "CERT-SUBJECT-001"


class CertificationIntegrityError(CertificationLayerError):
    """An immutable certification record failed its content-hash integrity check."""

    code = "CERT-INTEGRITY-001"


class LedgerIntegrityError(CertificationLayerError):
    """The append-only certification ledger hash chain is broken (tamper-evident)."""

    code = "CERT-LEDGER-001"


class ProgramClosureError(CertificationLayerError):
    """A program closure report could not be assembled from the supplied evidence."""

    code = "CERT-CLOSURE-001"


__all__ = [
    "CertificationLayerError",
    "CertificationSubjectError",
    "CertificationIntegrityError",
    "LedgerIntegrityError",
    "ProgramClosureError",
]
