"""EC2-CAP-ADMIN-001 — Administration Service (Administration Runtime).

The single, governed **administration runtime composition point** that composes the
whole Administration Runtime into one entry point — the operational administration
boundary for the platform, tenants, and workspaces:

    AdministrativeConfiguration · AdministrativeMembershipRegistry ·
    AdministrativeRoleView · AdministrativePermissions · AdministrativeAuditLog ·
    AdministrativeSearch · AdministrationHealth  ·
    (reused) AuthorizationService · ObservabilityService

It is a strictly **additive**, **administrative-only** layer: it authorizes only
through the certified Identity Layer (L7) on the ``administration-policy`` group —
**no duplicate authorization or identity logic** — observes only through the
Observability Layer (L8), reuses the Foundation registries/events, and reuses the
Workspace Runtime's tenant-isolation rule
(:func:`~platform.workspace.isolation.tenants_isolated`) — **no duplicate isolation
logic**. It creates **no authority**: it can only exercise the ``READ``/``ADMINISTER``
grants the §3.2 matrix already assigns (Auditor reads; Platform Administrator
administers). It mutates no governance, constitutional, certification, or execution
artifact and writes nothing to the certified corpus (DP-03).

Every administrative access is fail-closed and composes two independent gates —
**identity authorization** (RBAC §3.2) and **tenant isolation** — so cross-tenant
administration is refused. Every evaluation and every mutation is recorded to the
append-only administrative activity log and published onto the Foundation event bus,
so observability captures it as append-only audit (OP-C3 / PC-16). The service is
deterministic: the same identity registrations, configuration, memberships, and
ordered calls yield the same :class:`AdministrativeEvidence` fingerprint (P5).
"""

from __future__ import annotations

from dataclasses import dataclass
from platform.administration.audit import AdministrativeAuditLog
from platform.administration.configuration import (
    AdministrativeConfiguration,
    AdministrativeSetting,
)
from platform.administration.context import AdministrativeContext
from platform.administration.contracts import (
    ADMINISTRATION_GROUP,
    AdministrativeAction,
    AdministrativeDomain,
    AdministrativeScope,
    AdministrativeTarget,
    OperationalState,
    required_permission,
)
from platform.administration.errors import (
    AdministrationAccessError,
    AdministrationServiceError,
)
from platform.administration.health import AdministrationHealth, administration_health_checks
from platform.administration.membership import (
    AdministrativeMember,
    AdministrativeMembershipRegistry,
)
from platform.administration.permissions import AdministrativePermissions
from platform.administration.roles import AdministrativeRoleView
from platform.administration.search import AdministrativeSearch, AdministrativeSearchResponse
from platform.foundation.contracts import content_hash
from platform.foundation.events import EventBus
from platform.foundation.identity import Permission
from platform.identity.contracts import AccessDecision
from platform.identity.service import AuthorizationService
from platform.observability.health import HealthRegistry
from platform.observability.service import ObservabilityService
from platform.workspace.isolation import tenants_isolated
from typing import Any

#: Governed events published onto the Foundation event bus (observed as PC-16/OP-C3).
ADMIN_CONTEXT_EVENT = "administration.context.entered"
ADMIN_CONFIG_EVENT = "administration.configuration.changed"
ADMIN_MEMBER_ASSIGNED_EVENT = "administration.member.assigned"
ADMIN_MEMBER_REVOKED_EVENT = "administration.member.revoked"
ADMIN_LIFECYCLE_EVENT = "administration.lifecycle.transitioned"
ADMIN_ACCESS_EVENT = "administration.access.evaluated"

#: The reserved configuration key prefix under which operational lifecycle state lives.
_LIFECYCLE_KEY_PREFIX = "lifecycle::"


@dataclass(frozen=True, slots=True)
class AdministrativeAccess:
    """An immutable, content-addressed administrative access decision (fail-closed).

    Composes identity authorization and tenant isolation into a single verdict for one
    ``(principal, action, target)`` request; ``actions`` are the administrative verbs
    the principal is granted when the verdict is a grant.
    """

    access_id: str
    principal_id: str
    action: AdministrativeAction
    permission: Permission
    target: AdministrativeTarget
    granted: bool
    reason: str
    actions: frozenset[AdministrativeAction]
    decision: AccessDecision

    @classmethod
    def create(
        cls,
        *,
        action: AdministrativeAction,
        permission: Permission,
        target: AdministrativeTarget,
        granted: bool,
        reason: str,
        decision: AccessDecision,
        actions: frozenset[AdministrativeAction] = frozenset(),
    ) -> AdministrativeAccess:
        principal_id = decision.request.principal_id
        core = {
            "principal_id": principal_id,
            "action": action.value,
            "permission": permission.value,
            "target_id": target.target_id,
            "granted": granted,
            "reason": reason,
            "actions": sorted(a.value for a in actions),
        }
        return cls(
            access_id=f"UCOS-AACC-{content_hash(core)[:16]}",
            principal_id=principal_id,
            action=action,
            permission=permission,
            target=target,
            granted=granted,
            reason=reason,
            actions=frozenset(actions),
            decision=decision,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "access_id": self.access_id,
            "principal_id": self.principal_id,
            "action": self.action.value,
            "permission": self.permission.value,
            "target": self.target.to_dict(),
            "granted": self.granted,
            "reason": self.reason,
            "actions": sorted(a.value for a in self.actions),
            "decision": self.decision.to_dict(),
        }


@dataclass(frozen=True, slots=True)
class AdministrativeEvidence:
    """A deterministic, content-addressed record of administration runtime state."""

    configuration_fingerprint: str
    membership_fingerprint: str
    audit_fingerprint: str
    setting_count: int
    administrator_count: int
    access_evaluation_count: int
    health_status: str
    evidence_id: str = ""

    @classmethod
    def create(
        cls,
        *,
        configuration_fingerprint: str,
        membership_fingerprint: str,
        audit_fingerprint: str,
        setting_count: int,
        administrator_count: int,
        access_evaluation_count: int,
        health_status: str,
    ) -> AdministrativeEvidence:
        core = {
            "configuration_fingerprint": configuration_fingerprint,
            "membership_fingerprint": membership_fingerprint,
            "audit_fingerprint": audit_fingerprint,
            "setting_count": setting_count,
            "administrator_count": administrator_count,
            "access_evaluation_count": access_evaluation_count,
            "health_status": health_status,
        }
        return cls(
            configuration_fingerprint=configuration_fingerprint,
            membership_fingerprint=membership_fingerprint,
            audit_fingerprint=audit_fingerprint,
            setting_count=setting_count,
            administrator_count=administrator_count,
            access_evaluation_count=access_evaluation_count,
            health_status=health_status,
            evidence_id=f"UCOS-ADEV-{content_hash(core)[:16]}",
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "evidence_id": self.evidence_id,
            "configuration_fingerprint": self.configuration_fingerprint,
            "membership_fingerprint": self.membership_fingerprint,
            "audit_fingerprint": self.audit_fingerprint,
            "setting_count": self.setting_count,
            "administrator_count": self.administrator_count,
            "access_evaluation_count": self.access_evaluation_count,
            "health_status": self.health_status,
        }

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())


class AdministrationService:
    """The governed composition point for the UCOS Administration Runtime."""

    __slots__ = (
        "_configuration",
        "_membership",
        "_authorization",
        "_permissions",
        "_roles",
        "_audit",
        "_search",
        "_health",
        "_health_registry",
        "_observability",
        "_events",
        "_access_evaluations",
    )

    def __init__(
        self,
        *,
        configuration: AdministrativeConfiguration,
        membership: AdministrativeMembershipRegistry,
        authorization: AuthorizationService,
        audit: AdministrativeAuditLog,
        search: AdministrativeSearch,
        health: AdministrationHealth,
        health_registry: HealthRegistry,
        observability: ObservabilityService | None = None,
        events: EventBus | None = None,
    ) -> None:
        if not isinstance(configuration, AdministrativeConfiguration):
            raise AdministrationServiceError("a valid AdministrativeConfiguration is required")
        if not isinstance(membership, AdministrativeMembershipRegistry):
            raise AdministrationServiceError("a valid AdministrativeMembershipRegistry is required")
        if not isinstance(authorization, AuthorizationService):
            raise AdministrationServiceError("a valid AuthorizationService is required")
        if not isinstance(audit, AdministrativeAuditLog):
            raise AdministrationServiceError("a valid AdministrativeAuditLog is required")
        if not isinstance(search, AdministrativeSearch):
            raise AdministrationServiceError("a valid AdministrativeSearch is required")
        if not isinstance(health, AdministrationHealth):
            raise AdministrationServiceError("a valid AdministrationHealth is required")
        if not isinstance(health_registry, HealthRegistry):
            raise AdministrationServiceError("a valid HealthRegistry is required")
        if observability is not None and not isinstance(observability, ObservabilityService):
            raise AdministrationServiceError(
                "observability must be an ObservabilityService when provided"
            )
        if events is not None and not isinstance(events, EventBus):
            raise AdministrationServiceError("events must be an EventBus when provided")
        self._configuration = configuration
        self._membership = membership
        self._authorization = authorization
        self._audit = audit
        self._search = search
        self._health = health
        self._health_registry = health_registry
        self._observability = observability
        self._events = events
        self._permissions = AdministrativePermissions(authorization.permissions)
        self._roles = AdministrativeRoleView(authorization.roles)
        self._access_evaluations = 0

    # -- component access -------------------------------------------------------

    @property
    def configuration(self) -> AdministrativeConfiguration:
        return self._configuration

    @property
    def membership(self) -> AdministrativeMembershipRegistry:
        return self._membership

    @property
    def authorization(self) -> AuthorizationService:
        return self._authorization

    @property
    def audit(self) -> AdministrativeAuditLog:
        return self._audit

    @property
    def permissions(self) -> AdministrativePermissions:
        return self._permissions

    @property
    def roles(self) -> AdministrativeRoleView:
        return self._roles

    @property
    def health(self) -> AdministrationHealth:
        return self._health

    @property
    def observability(self) -> ObservabilityService | None:
        return self._observability

    @property
    def access_evaluation_count(self) -> int:
        return self._access_evaluations

    # -- access evaluation ------------------------------------------------------

    def evaluate_access(
        self,
        session_id: str,
        action: AdministrativeAction,
        target: AdministrativeTarget,
        *,
        now: int,
    ) -> AdministrativeAccess:
        """Evaluate composed administrative access (identity ∧ tenant isolation).

        Denials are returned as data (``granted == False``); a malformed request
        raises. Every evaluation is recorded to the administrative activity log and
        emitted as a governed ``administration.access.evaluated`` event (PC-16).
        """
        if not isinstance(action, AdministrativeAction):
            raise AdministrationServiceError("action must be an AdministrativeAction")
        if not isinstance(target, AdministrativeTarget):
            raise AdministrationServiceError("target must be an AdministrativeTarget")
        permission = required_permission(action)
        decision = self._authorization.authorize(
            session_id,
            ADMINISTRATION_GROUP,
            permission,
            now=now,
            tenant=target.tenant,
            resource=target.identifier,
        )
        access = self._compose_access(action, permission, target, decision)
        self._access_evaluations += 1
        self._audit.record(
            action=action,
            domain=target.domain,
            scope=target.scope,
            principal_id=access.principal_id,
            target_id=target.target_id,
            granted=access.granted,
            reason=access.reason,
            tick=now,
            tenant=target.tenant,
        )
        self._emit(
            ADMIN_ACCESS_EVENT,
            subject=access.principal_id,
            payload={
                "action": action.value,
                "target_id": target.target_id,
                "scope": target.scope.value,
                "granted": access.granted,
                "reason": access.reason,
            },
        )
        return access

    def _compose_access(
        self,
        action: AdministrativeAction,
        permission: Permission,
        target: AdministrativeTarget,
        decision: AccessDecision,
    ) -> AdministrativeAccess:
        if not decision.permitted:
            return AdministrativeAccess.create(
                action=action,
                permission=permission,
                target=target,
                granted=False,
                reason=decision.reason,
                decision=decision,
            )
        principal = self._authorization.principals.get(decision.request.principal_id)
        if tenants_isolated(principal.tenant, target.tenant):
            return AdministrativeAccess.create(
                action=action,
                permission=permission,
                target=target,
                granted=False,
                reason="tenant-isolation-violation",
                decision=decision,
            )
        return AdministrativeAccess.create(
            action=action,
            permission=permission,
            target=target,
            granted=True,
            reason="granted",
            decision=decision,
            actions=self._permissions.actions_for(principal),
        )

    def _require_granted(
        self,
        session_id: str,
        action: AdministrativeAction,
        target: AdministrativeTarget,
        *,
        now: int,
    ) -> AdministrativeAccess:
        access = self.evaluate_access(session_id, action, target, now=now)
        if not access.granted:
            raise AdministrationAccessError(
                "administrative action denied",
                reason=access.reason,
                action=action.value,
                target_id=target.target_id,
            )
        return access

    # -- context / session ------------------------------------------------------

    def enter(
        self,
        session_id: str,
        scope: AdministrativeScope,
        *,
        now: int,
        tenant: str | None = None,
    ) -> AdministrativeContext:
        """Enter an administrative scope and return the runtime context (fail-closed).

        Requires INSPECT (READ) on ``administration-policy`` and tenant-isolation
        clearance. Raises :class:`AdministrationAccessError` when entry is denied.
        """
        if not isinstance(scope, AdministrativeScope):
            raise AdministrationServiceError("scope must be an AdministrativeScope")
        identifier = tenant if tenant is not None else scope.value
        target = AdministrativeTarget.create(
            scope, AdministrativeDomain.CONTEXT, identifier, tenant=tenant
        )
        access = self._require_granted(session_id, AdministrativeAction.INSPECT, target, now=now)
        principal = self._authorization.principals.get(access.principal_id)
        context = AdministrativeContext.create(principal, scope, access.actions, tenant=tenant)
        self._emit(
            ADMIN_CONTEXT_EVENT,
            subject=principal.principal_id,
            payload={"scope": scope.value, "tenant": tenant, "context_id": context.context_id},
        )
        return context

    # -- configuration ----------------------------------------------------------

    def set_configuration(
        self,
        session_id: str,
        scope: AdministrativeScope,
        key: str,
        value: str,
        *,
        now: int,
        tenant: str | None = None,
    ) -> AdministrativeSetting:
        """Set an operational setting/control (requires CONFIGURE → ADMINISTER)."""
        target = AdministrativeTarget.create(
            scope, AdministrativeDomain.CONFIGURATION, key, tenant=tenant
        )
        self._require_granted(session_id, AdministrativeAction.CONFIGURE, target, now=now)
        setting = self._configuration.set(scope, key, value, tick=now, tenant=tenant)
        self._emit(
            ADMIN_CONFIG_EVENT,
            subject=setting.setting_id,
            payload={"scope": scope.value, "key": setting.key, "tenant": tenant, "action": "set"},
        )
        return setting

    def get_configuration(
        self,
        session_id: str,
        scope: AdministrativeScope,
        key: str,
        *,
        now: int,
        tenant: str | None = None,
    ) -> AdministrativeSetting:
        """Read an operational setting (requires INSPECT → READ)."""
        target = AdministrativeTarget.create(
            scope, AdministrativeDomain.CONFIGURATION, key, tenant=tenant
        )
        self._require_granted(session_id, AdministrativeAction.INSPECT, target, now=now)
        return self._configuration.get(scope, key, tenant=tenant)

    def remove_configuration(
        self,
        session_id: str,
        scope: AdministrativeScope,
        key: str,
        *,
        now: int,
        tenant: str | None = None,
    ) -> AdministrativeSetting:
        """Remove an operational setting/control (requires CONFIGURE → ADMINISTER)."""
        target = AdministrativeTarget.create(
            scope, AdministrativeDomain.CONFIGURATION, key, tenant=tenant
        )
        self._require_granted(session_id, AdministrativeAction.CONFIGURE, target, now=now)
        setting = self._configuration.remove(scope, key, tick=now, tenant=tenant)
        self._emit(
            ADMIN_CONFIG_EVENT,
            subject=setting.setting_id,
            payload={
                "scope": scope.value,
                "key": setting.key,
                "tenant": tenant,
                "action": "remove",
            },
        )
        return setting

    # -- membership administration (tenant / workspace / platform) --------------

    def assign_administrator(
        self,
        session_id: str,
        scope: AdministrativeScope,
        target_identifier: str,
        principal_id: str,
        subject: str,
        *,
        now: int,
        tenant: str | None = None,
    ) -> AdministrativeMember:
        """Assign a principal as administrator of a scope target (requires ASSIGN)."""
        target = AdministrativeTarget.create(
            scope, AdministrativeDomain.MEMBERSHIP, target_identifier, tenant=tenant
        )
        self._require_granted(session_id, AdministrativeAction.ASSIGN, target, now=now)
        member = self._membership.add(
            scope, target_identifier, principal_id, subject, tick=now, tenant=tenant
        )
        self._emit(
            ADMIN_MEMBER_ASSIGNED_EVENT,
            subject=member.member_id,
            payload={
                "scope": scope.value,
                "target": member.target,
                "principal_id": member.principal_id,
                "tenant": tenant,
            },
        )
        return member

    def revoke_administrator(
        self,
        session_id: str,
        scope: AdministrativeScope,
        target_identifier: str,
        principal_id: str,
        *,
        now: int,
        tenant: str | None = None,
    ) -> AdministrativeMember:
        """Revoke an administrator assignment (requires REVOKE)."""
        target = AdministrativeTarget.create(
            scope, AdministrativeDomain.MEMBERSHIP, target_identifier, tenant=tenant
        )
        self._require_granted(session_id, AdministrativeAction.REVOKE, target, now=now)
        member = self._membership.remove(scope, target_identifier, principal_id, tick=now)
        self._emit(
            ADMIN_MEMBER_REVOKED_EVENT,
            subject=member.member_id,
            payload={
                "scope": scope.value,
                "target": member.target,
                "principal_id": member.principal_id,
            },
        )
        return member

    # -- operational lifecycle management ---------------------------------------

    def set_operational_state(
        self,
        session_id: str,
        scope: AdministrativeScope,
        identifier: str,
        state: OperationalState,
        *,
        now: int,
        tenant: str | None = None,
    ) -> OperationalState:
        """Set an administered resource's operational lifecycle state (fail-closed).

        Activation requires ACTIVATE; suspension/decommission requires SUSPEND — both
        map to ADMINISTER on ``administration-policy``. The state is persisted as a
        reserved operational setting so it is reproducible and audited.
        """
        if not isinstance(state, OperationalState):
            raise AdministrationServiceError("state must be an OperationalState")
        action = (
            AdministrativeAction.ACTIVATE
            if state is OperationalState.ACTIVE
            else AdministrativeAction.SUSPEND
        )
        target = AdministrativeTarget.create(
            scope, AdministrativeDomain.LIFECYCLE, identifier, tenant=tenant
        )
        self._require_granted(session_id, action, target, now=now)
        key = f"{_LIFECYCLE_KEY_PREFIX}{identifier}"
        self._configuration.set(scope, key, state.value, tick=now, tenant=tenant)
        self._emit(
            ADMIN_LIFECYCLE_EVENT,
            subject=target.target_id,
            payload={
                "scope": scope.value,
                "identifier": identifier,
                "tenant": tenant,
                "state": state.value,
            },
        )
        return state

    def operational_state(
        self,
        session_id: str,
        scope: AdministrativeScope,
        identifier: str,
        *,
        now: int,
        tenant: str | None = None,
    ) -> OperationalState | None:
        """Read an administered resource's operational state (requires INSPECT)."""
        target = AdministrativeTarget.create(
            scope, AdministrativeDomain.LIFECYCLE, identifier, tenant=tenant
        )
        self._require_granted(session_id, AdministrativeAction.INSPECT, target, now=now)
        key = f"{_LIFECYCLE_KEY_PREFIX}{identifier}"
        value = self._configuration.value_of(scope, key, tenant=tenant)
        return OperationalState(value) if value is not None else None

    # -- search -----------------------------------------------------------------

    def search(
        self, session_id: str, query: str, *, now: int, tenant: str | None = None
    ) -> AdministrativeSearchResponse:
        """Run an authorization-scoped administrative search."""
        return self._search.search(session_id, query, now=now, tenant=tenant)

    # -- health integration -----------------------------------------------------

    def health_report(self) -> dict[str, Any]:
        """The administration runtime health endpoint (reuses the observability model)."""
        return self._health_registry.endpoint(self._health.probe())

    # -- evidence ---------------------------------------------------------------

    def evidence(self) -> AdministrativeEvidence:
        """Produce deterministic Administrative Evidence over the runtime state."""
        report = self._health_registry.report(self._health.probe())
        return AdministrativeEvidence.create(
            configuration_fingerprint=self._configuration.fingerprint(),
            membership_fingerprint=self._membership.fingerprint(),
            audit_fingerprint=self._audit.fingerprint(),
            setting_count=len(self._configuration),
            administrator_count=len(self._membership),
            access_evaluation_count=self._access_evaluations,
            health_status=report.status.value,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "setting_count": len(self._configuration),
            "administrator_count": len(self._membership),
            "access_evaluation_count": self._access_evaluations,
            "audit_event_count": len(self._audit),
            "observability_bound": self._observability is not None,
            "evidence": self.evidence().to_dict(),
        }

    # -- internals --------------------------------------------------------------

    def _emit(self, event_type: str, *, subject: str, payload: dict[str, Any]) -> None:
        if self._events is not None:
            self._events.publish(
                event_type,
                source="platform.administration.runtime",
                subject=subject,
                payload=payload,
            )


def build_administration_service(
    *,
    authorization: AuthorizationService,
    observability: ObservabilityService | None = None,
    events: EventBus | None = None,
    configuration: AdministrativeConfiguration | None = None,
    membership: AdministrativeMembershipRegistry | None = None,
) -> AdministrationService:
    """Default, registry-driven composition of the Administration Runtime.

    Wires the configuration store, administrative membership registry, administrative
    audit log, administrative search (over the supplied Identity ``authorization``
    service), the administration health probe and a health registry seeded with the
    administration health checks, and — when supplied — the observability layer and
    event bus.
    """
    if not isinstance(authorization, AuthorizationService):
        raise AdministrationServiceError(
            "build_administration_service requires an AuthorizationService"
        )
    config = configuration if configuration is not None else AdministrativeConfiguration()
    members = membership if membership is not None else AdministrativeMembershipRegistry()
    audit = AdministrativeAuditLog()
    search = AdministrativeSearch(config, members, authorization)
    health = AdministrationHealth(config, members)
    health_registry = HealthRegistry()
    for check in administration_health_checks():
        health_registry.register(check)
    return AdministrationService(
        configuration=config,
        membership=members,
        authorization=authorization,
        audit=audit,
        search=search,
        health=health,
        health_registry=health_registry,
        observability=observability,
        events=events,
    )


__all__ = [
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
]
