"""UCOS Ω∞ — Universal Portal (UCOS-EPIC-008 · Terminal T8).

The **Universal Portal** is the single, governed presentation composition (L1) that
unifies every operator- and developer-facing surface of UCOS Ω∞ into one deterministic
entry point. It realizes the eight Terminal-T8 surfaces:

    1. Administration Portal      — over ``platform.administration``.
    2. Registry Explorer          — over the platform service/capability directory.
    3. Knowledge Graph Explorer   — over the knowledge graph (``engine.knowledge``).
    4. Measurement Dashboard      — over ``platform.coverage`` (Universe→Code coverage).
    5. Validation Dashboard       — over ``platform.validation`` (Validation Console).
    6. Certification Dashboard    — over ``platform.certification`` (Certification Ledger).
    7. Developer Portal           — the API catalog over every published contract.
    8. Documentation Portal       — the deterministic documentation index.

It is a strictly **additive** layer. It **consumes only published APIs** — the certified
EC-2 Portal shell (EC2-EPIC-003), Identity Layer (L7), Observability Layer (L8), and each
domain runtime's published service — and **never bypasses a platform service**: it
authorizes only through the portal access gateway (Identity), re-implements no domain
logic, mutates nothing, starts no server, opens no socket, and never writes to the
certified corpus (DP-03). Every surface is **fail-closed**: on any doubt the portal denies
rather than exposes. It is **deterministic**: the same identity registrations, bound
providers, and ordered calls yield the same :class:`UniversalPortalEvidence` fingerprint.

Deliverables:
    * **errors** — the ``T8-UPORTAL-*`` error taxonomy over ``PlatformError``.
    * **contracts** — the ``PortalApplication`` vocabulary (the eight surfaces bound to
      §3.2 capability groups), ``UniversalPortalSurface``, and the published
      ``UNIVERSAL_PORTAL_CONTRACTS``.
    * **applications** — ``ApplicationDescriptor``/``ApplicationRegistry``/``ApplicationView``:
      the authorization-gated read model over each bound surface.
    * **developer** — ``DeveloperPortal``: the API catalog over every published contract.
    * **documentation** — ``DocumentationPortal``: the deterministic documentation index.
    * **health** — the deterministic ``UniversalPortalHealth`` report.
    * **service** — ``UniversalPortalService`` (composition root) + ``UniversalPortalEvidence``,
      ``build_universal_portal_service``, and ``bootstrap_universal_portal``.
"""

from __future__ import annotations

from platform.universal_portal.applications import (
    ApplicationDescriptor,
    ApplicationProvider,
    ApplicationRegistry,
    ApplicationView,
)
from platform.universal_portal.contracts import (
    UNIVERSAL_PORTAL_CONTRACT_VERSION,
    UNIVERSAL_PORTAL_CONTRACTS,
    ApplicationSection,
    PortalApplication,
    UniversalPortalSurface,
    all_portal_applications,
    application_group,
    application_section,
    consumed_contract_refs,
    default_universal_portal_contracts,
    default_universal_portal_surfaces,
    required_permission,
    universal_portal_contract,
)
from platform.universal_portal.developer import ApiEntry, DeveloperCatalog, DeveloperPortal
from platform.universal_portal.documentation import (
    DocumentationIndex,
    DocumentationPage,
    DocumentationPortal,
)
from platform.universal_portal.errors import (
    ApplicationBindingError,
    DeveloperPortalError,
    DocumentationPortalError,
    UniversalPortalAccessError,
    UniversalPortalContractError,
    UniversalPortalError,
    UniversalPortalServiceError,
)
from platform.universal_portal.health import (
    UniversalPortalHealth,
    universal_portal_health_report,
)
from platform.universal_portal.service import (
    UNIVERSAL_PORTAL_BOOTSTRAP_EVENT,
    UNIVERSAL_PORTAL_OPENED_EVENT,
    UniversalPortalEvidence,
    UniversalPortalService,
    bootstrap_universal_portal,
    build_universal_portal_service,
)

__all__ = [
    # contracts
    "UNIVERSAL_PORTAL_CONTRACT_VERSION",
    "UNIVERSAL_PORTAL_CONTRACTS",
    "PortalApplication",
    "ApplicationSection",
    "UniversalPortalSurface",
    "all_portal_applications",
    "application_group",
    "application_section",
    "required_permission",
    "consumed_contract_refs",
    "universal_portal_contract",
    "default_universal_portal_contracts",
    "default_universal_portal_surfaces",
    # applications
    "ApplicationProvider",
    "ApplicationDescriptor",
    "ApplicationRegistry",
    "ApplicationView",
    # developer
    "ApiEntry",
    "DeveloperCatalog",
    "DeveloperPortal",
    # documentation
    "DocumentationPage",
    "DocumentationIndex",
    "DocumentationPortal",
    # health
    "UniversalPortalHealth",
    "universal_portal_health_report",
    # service
    "UNIVERSAL_PORTAL_BOOTSTRAP_EVENT",
    "UNIVERSAL_PORTAL_OPENED_EVENT",
    "UniversalPortalEvidence",
    "UniversalPortalService",
    "build_universal_portal_service",
    "bootstrap_universal_portal",
    # errors
    "UniversalPortalError",
    "UniversalPortalContractError",
    "ApplicationBindingError",
    "UniversalPortalAccessError",
    "DeveloperPortalError",
    "DocumentationPortalError",
    "UniversalPortalServiceError",
]
