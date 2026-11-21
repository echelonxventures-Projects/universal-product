"""UCOS EC-2 Platform Administration Runtime (EC2-CAP-ADMIN-001).

The Administration Runtime is the platform's **operational administration** surface. It
governs platform administration, tenant administration, workspace administration,
operational configuration, administrative lifecycle, and runtime management. It is
**administrative only** — it is *not* governance, *not* constitutional authority, *not*
certification authority, and *not* execution authorization. It provides operational
administration and nothing more, creating no new authority.

It is a strictly **additive** layer over the certified EC-1 engine and the EC-2
Foundation (EC2-EPIC-001), Identity (EC2-EPIC-002), Workspace (EC2-EPIC-004), and
Observability (EC2-EPIC-013) layers: it authorizes only through the Identity Layer on
the §3.2 ``administration-policy`` capability group (no duplicate identity/authorization
logic), observes only through the Observability Layer (no duplicate audit/observability
logic), reuses the Workspace Runtime's tenant-isolation rule (no duplicate isolation
logic), and reuses the Foundation registries/events, identity model, telemetry model,
and error model. It modifies neither EC-1 nor any prior layer, never writes to the
certified corpus (DP-03), remains deterministic, and preserves every EC-1 certification.

Deliverables:
    * **errors** — the ``EC2-ADMIN-*`` error taxonomy over ``PlatformError``.
    * **contracts** — the versioned contract surface + vocabulary: ``AdministrativeScope``,
      ``AdministrativeDomain``, ``AdministrativeAction``, ``OperationalState``,
      ``AdministrativeTarget``, ``ADMINISTRATION_CONTRACTS``.
    * **context** — the resolved ``AdministrativeContext`` runtime binding.
    * **configuration** — the append-only ``AdministrativeConfiguration`` (settings/controls).
    * **roles** — the read-only ``AdministrativeRoleView`` over the §3.2 matrix.
    * **permissions** — the ``AdministrativePermissions`` evaluation view.
    * **membership** — the append-only ``AdministrativeMembershipRegistry``.
    * **audit** — the append-only ``AdministrativeAuditLog`` (activity tracking).
    * **search** — authorization-scoped ``AdministrativeSearch``.
    * **health** — administration health checks + ``AdministrationHealth`` (reuses L8 model).
    * **service** — the ``AdministrationService`` composition root + ``AdministrativeEvidence``.
    * **bootstrap** — ``bootstrap_administration`` (composes identity + observability + admin).

It starts no server and opens no socket — it is the deterministic runtime model.
"""

from __future__ import annotations

from platform.administration.audit import (
    AdministrativeAuditEvent,
    AdministrativeAuditLog,
)
from platform.administration.bootstrap import (
    ADMINISTRATION_BOOTSTRAP_EVENT,
    bootstrap_administration,
)
from platform.administration.configuration import (
    AdministrativeConfiguration,
    AdministrativeSetting,
    ConfigurationEvent,
)
from platform.administration.context import AdministrativeContext
from platform.administration.contracts import (
    ADMINISTRATION_CONTRACT_VERSION,
    ADMINISTRATION_CONTRACTS,
    ADMINISTRATION_GROUP,
    AdministrativeAction,
    AdministrativeDomain,
    AdministrativeScope,
    AdministrativeTarget,
    OperationalState,
    administration_contract,
    all_administrative_actions,
    all_administrative_scopes,
    all_operational_states,
    default_administration_contracts,
    required_permission,
)
from platform.administration.errors import (
    AdministrationAccessError,
    AdministrationAuditError,
    AdministrationConfigurationError,
    AdministrationContextError,
    AdministrationContractError,
    AdministrationError,
    AdministrationMembershipError,
    AdministrationPermissionError,
    AdministrationRoleError,
    AdministrationSearchError,
    AdministrationServiceError,
)
from platform.administration.health import (
    CONFIGURATION_CHECK,
    INTEGRITY_CHECK,
    AdministrationHealth,
    administration_health_checks,
)
from platform.administration.membership import (
    AdministrativeMember,
    AdministrativeMembershipEvent,
    AdministrativeMembershipRegistry,
)
from platform.administration.permissions import AdministrativePermissions
from platform.administration.roles import AdministrativeRoleView
from platform.administration.search import (
    AdministrativeHit,
    AdministrativeSearch,
    AdministrativeSearchResponse,
)
from platform.administration.service import (
    ADMIN_ACCESS_EVENT,
    ADMIN_CONFIG_EVENT,
    ADMIN_CONTEXT_EVENT,
    ADMIN_LIFECYCLE_EVENT,
    ADMIN_MEMBER_ASSIGNED_EVENT,
    ADMIN_MEMBER_REVOKED_EVENT,
    AdministrationService,
    AdministrativeAccess,
    AdministrativeEvidence,
    build_administration_service,
)

__all__ = [
    # contracts
    "ADMINISTRATION_CONTRACT_VERSION",
    "ADMINISTRATION_CONTRACTS",
    "ADMINISTRATION_GROUP",
    "AdministrativeScope",
    "AdministrativeDomain",
    "AdministrativeAction",
    "OperationalState",
    "AdministrativeTarget",
    "required_permission",
    "all_administrative_scopes",
    "all_administrative_actions",
    "all_operational_states",
    "administration_contract",
    "default_administration_contracts",
    # context
    "AdministrativeContext",
    # configuration
    "AdministrativeSetting",
    "ConfigurationEvent",
    "AdministrativeConfiguration",
    # roles
    "AdministrativeRoleView",
    # permissions
    "AdministrativePermissions",
    # membership
    "AdministrativeMember",
    "AdministrativeMembershipEvent",
    "AdministrativeMembershipRegistry",
    # audit
    "AdministrativeAuditEvent",
    "AdministrativeAuditLog",
    # search
    "AdministrativeHit",
    "AdministrativeSearchResponse",
    "AdministrativeSearch",
    # health
    "CONFIGURATION_CHECK",
    "INTEGRITY_CHECK",
    "administration_health_checks",
    "AdministrationHealth",
    # service
    "ADMIN_CONTEXT_EVENT",
    "ADMIN_CONFIG_EVENT",
    "ADMIN_MEMBER_ASSIGNED_EVENT",
    "ADMIN_MEMBER_REVOKED_EVENT",
    "ADMIN_LIFECYCLE_EVENT",
    "ADMIN_ACCESS_EVENT",
    "AdministrativeAccess",
    "AdministrativeEvidence",
    "AdministrationService",
    "build_administration_service",
    # bootstrap
    "ADMINISTRATION_BOOTSTRAP_EVENT",
    "bootstrap_administration",
    # errors
    "AdministrationError",
    "AdministrationContractError",
    "AdministrationContextError",
    "AdministrationConfigurationError",
    "AdministrationRoleError",
    "AdministrationPermissionError",
    "AdministrationMembershipError",
    "AdministrationAuditError",
    "AdministrationSearchError",
    "AdministrationAccessError",
    "AdministrationServiceError",
]
