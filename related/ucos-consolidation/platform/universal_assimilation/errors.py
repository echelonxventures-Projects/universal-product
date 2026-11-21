"""UCOS-USAF-001 — Universal Source Assimilation Framework error taxonomy.

The Universal Source Assimilation Framework (``platform/universal_assimilation/``) is a
strictly **additive** platform package through which *every* source — conversation export,
chat transcript, markdown, DOCX, PDF, repository, git history, API response, database
record, email, and every source not yet invented — is assimilated by one framework rather
than by one bespoke engine per format.

It reuses the certified Foundation error discipline: every error is rooted in
:class:`~platform.foundation.errors.PlatformError`, carries a stable ``EC2-USAF-*`` code and
structured, non-secret context (PL-02, IP-12), and fails **closed** — an unextractable
source is recorded as an honest deferral, never as assimilated content.
"""

from __future__ import annotations

from platform.foundation.errors import PlatformError


class AssimilationError(PlatformError):
    """Base class for all Universal Source Assimilation Framework (USAF-001) errors."""

    code = "EC2-USAF-000"


class AssimilationContractError(AssimilationError):
    """An assimilation vocabulary value (kind, source, unit, record) is malformed."""

    code = "EC2-USAF-CONTRACT-001"


class SourceKindError(AssimilationError):
    """A source kind is undeclared or declared twice with a different body (fail-closed)."""

    code = "EC2-USAF-KIND-001"


class SourceAdapterError(AssimilationError):
    """A source adapter is malformed or failed while normalising a source (fail-closed)."""

    code = "EC2-USAF-ADAPTER-001"


class AdapterConflictError(AssimilationError):
    """Two different adapters claim the same adapter identity."""

    code = "EC2-USAF-ADAPTER-002"


class AssimilationPipelineError(AssimilationError):
    """The assimilation pipeline could not produce an honest determination (fail-closed)."""

    code = "EC2-USAF-PIPELINE-001"


__all__ = [
    "AssimilationError",
    "AssimilationContractError",
    "SourceKindError",
    "SourceAdapterError",
    "AdapterConflictError",
    "AssimilationPipelineError",
]
