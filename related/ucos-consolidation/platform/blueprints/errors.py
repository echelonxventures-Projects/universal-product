"""EC2-TASK-000097 — Blueprint error taxonomy (EC2-EPIC-006).

The UCOS Platform **Blueprint Catalog & Management Runtime** — the L3/L6 realization
of the Program "Blueprint Management" surface (Program §2.1 #7, PC-04 authoring &
validation + PC-05 catalog, §4 L3/L4/L5/L6) — reuses the EC-1 / Platform Foundation
error discipline additively; it does not fork or modify it. Every blueprint error is
rooted in :class:`~platform.foundation.errors.PlatformError` (itself rooted in the
certified EC-1 :class:`~engine.foundation.obs.errors.FoundationError`), carries a
stable, category-prefixed ``code`` (``EC2-BP-*``) and structured, non-secret
``context`` so failures are auditable (PL-02, IP-12) and machine-consumable by
TRACK-001.

The Blueprint Runtime is *additive* over EC-1, the Foundation (L4/L6), the Identity
Layer (L7), the Observability Layer (L8), the Workspace Runtime (L3), and the Project
Management Runtime (L3): it consumes them only through published contracts /
composition roots, never modifies them, and never writes to the certified corpus
(DP-03). A malformed blueprint contract, metadata, provenance, classification,
validation, lifecycle transition, version, registration, association, status, catalog
record, search, context, or access decision fails loudly with a specific error. Every
access decision is **fail-closed**: on any doubt the runtime denies rather than
admits, and cross-tenant/cross-workspace access is refused (P3). An invalid blueprint
is refused with the EC-1 classification gap report and never enters the catalog
(§4.3 acceptance, P4).
"""

from __future__ import annotations

from platform.foundation.errors import PlatformError


class BlueprintError(PlatformError):
    """Base class for all EC-2 Blueprint Catalog & Management Runtime errors."""

    code = "EC2-BP-000"


class BlueprintContractError(BlueprintError):
    """A blueprint contract, record, or vocabulary declaration is malformed (AR-03/PL-05)."""

    code = "EC2-BP-CONTRACT-001"


class BlueprintMetadataError(BlueprintError):
    """Blueprint metadata is malformed."""

    code = "EC2-BP-METADATA-001"


class BlueprintProvenanceError(BlueprintError):
    """Blueprint provenance-by-reference is malformed or incomplete (link-4, fail-closed)."""

    code = "EC2-BP-PROVENANCE-001"


class BlueprintClassificationError(BlueprintError):
    """A recorded EC-1 classification result is malformed (records, never computes)."""

    code = "EC2-BP-CLASSIFICATION-001"


class BlueprintValidationError(BlueprintError):
    """A blueprint failed structural validation; rejected with an EC-1 gap report (P4)."""

    code = "EC2-BP-VALIDATION-001"


class BlueprintLifecycleError(BlueprintError):
    """An illegal or malformed blueprint lifecycle transition (fail-closed)."""

    code = "EC2-BP-LIFECYCLE-001"


class BlueprintVersionError(BlueprintError):
    """A blueprint version or lineage operation is malformed (immutability violated)."""

    code = "EC2-BP-VERSION-001"


class BlueprintRegistryError(BlueprintError):
    """A blueprint could not be registered or resolved (duplicate/absent/malformed)."""

    code = "EC2-BP-REGISTRY-001"


class BlueprintAssociationError(BlueprintError):
    """A blueprint association is malformed or violates referential integrity (fail-closed)."""

    code = "EC2-BP-ASSOCIATION-001"


class BlueprintStatusError(BlueprintError):
    """A blueprint derived-status computation is malformed."""

    code = "EC2-BP-STATUS-001"


class BlueprintCatalogError(BlueprintError):
    """A blueprint catalog (L6 read model) operation is malformed (fail-closed)."""

    code = "EC2-BP-CATALOG-001"


class BlueprintSearchError(BlueprintError):
    """A blueprint search request is malformed."""

    code = "EC2-BP-SEARCH-001"


class BlueprintAccessError(BlueprintError):
    """A blueprint access/authorization request is denied or malformed (fail-closed)."""

    code = "EC2-BP-ACCESS-001"


class BlueprintServiceError(BlueprintError):
    """The blueprint service could not be composed or an operation is malformed."""

    code = "EC2-BP-SERVICE-001"


__all__ = [
    "BlueprintError",
    "BlueprintContractError",
    "BlueprintMetadataError",
    "BlueprintProvenanceError",
    "BlueprintClassificationError",
    "BlueprintValidationError",
    "BlueprintLifecycleError",
    "BlueprintVersionError",
    "BlueprintRegistryError",
    "BlueprintAssociationError",
    "BlueprintStatusError",
    "BlueprintCatalogError",
    "BlueprintSearchError",
    "BlueprintAccessError",
    "BlueprintServiceError",
]
