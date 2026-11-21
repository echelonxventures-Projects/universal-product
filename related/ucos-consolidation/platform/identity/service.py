"""EC2-TASK-000069 — Authorization Service (EC2-EPIC-002).

The single, governed **access decision point** (L7 of the Program architecture) that
composes the whole Identity Platform into one entry point:

    PrincipalRegistry · RoleRegistry · PermissionEngine · PolicyEngine · SessionRegistry

Every authorization flows session → principal → policy → decision, is **fail-closed**
(an absent / expired / revoked session, or an unregistered principal, denies), and
is recorded to an append-only decision log and — when bound to the Platform
Foundation event bus — emitted as an ``identity.access.evaluated`` audit event
(PC-16, IP-12). The service is deterministic: the same registrations and the same
ordered sequence of calls yield the same decisions and the same
:class:`IdentityEvidence` fingerprint (Identity Evidence, acceptance I8).

This module also provides the registry-driven composition helpers
:func:`build_authorization_service` (default wiring, §3.2 matrix seeded) and
:func:`bootstrap_identity` (binds to a :class:`~platform.foundation.bootstrap.PlatformContext`,
publishes the six identity contracts into the foundation service registry, and emits
a composition event). It authenticates nothing itself — sessions are established from
already-authenticated principals — and holds no secret material (SEC-04).
"""

from __future__ import annotations

from dataclasses import dataclass
from platform.foundation.contracts import content_hash
from platform.foundation.events import EventBus
from platform.foundation.identity import Permission, Principal
from platform.identity.contracts import (
    IDENTITY_CONTRACTS,
    AccessDecision,
    AccessRequest,
    CapabilityGroup,
    Decision,
    default_identity_contracts,
)
from platform.identity.errors import AuthorizationError, SessionError
from platform.identity.permissions import PermissionEngine
from platform.identity.policy import PolicyEngine
from platform.identity.principals import PrincipalRegistry
from platform.identity.roles import RoleRegistry, default_role_registry
from platform.identity.sessions import Session, SessionRegistry
from typing import Any

#: The audit event emitted for every authorization evaluation (PC-16).
ACCESS_EVENT = "identity.access.evaluated"

#: The event emitted when the Identity Platform is composed onto a PlatformContext.
IDENTITY_BOOTSTRAP_EVENT = "identity.bootstrap.completed"


@dataclass(frozen=True, slots=True)
class IdentityEvidence:
    """A deterministic, content-addressed record of identity decisions (Identity Evidence).

    Aggregates the registry fingerprints and the append-only decision log into a
    single reproducible evidence object suitable for audit and TRACK-001.
    """

    principals_fingerprint: str
    roles_fingerprint: str
    decision_count: int
    permit_count: int
    deny_count: int
    decisions: tuple[dict[str, Any], ...]
    evidence_id: str = ""

    @classmethod
    def create(
        cls,
        *,
        principals_fingerprint: str,
        roles_fingerprint: str,
        decisions: tuple[dict[str, Any], ...],
    ) -> IdentityEvidence:
        permit_count = sum(1 for d in decisions if d.get("decision") == Decision.PERMIT.value)
        deny_count = len(decisions) - permit_count
        core = {
            "principals_fingerprint": principals_fingerprint,
            "roles_fingerprint": roles_fingerprint,
            "decisions": list(decisions),
        }
        return cls(
            principals_fingerprint=principals_fingerprint,
            roles_fingerprint=roles_fingerprint,
            decision_count=len(decisions),
            permit_count=permit_count,
            deny_count=deny_count,
            decisions=tuple(decisions),
            evidence_id=f"UCOS-IDEV-{content_hash(core)[:16]}",
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "evidence_id": self.evidence_id,
            "principals_fingerprint": self.principals_fingerprint,
            "roles_fingerprint": self.roles_fingerprint,
            "decision_count": self.decision_count,
            "permit_count": self.permit_count,
            "deny_count": self.deny_count,
            "decisions": [dict(d) for d in self.decisions],
        }

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())


class AuthorizationService:
    """The governed L7 access decision point composing the Identity Platform."""

    __slots__ = ("_principals", "_roles", "_permissions", "_policy", "_sessions", "_events", "_log")

    def __init__(
        self,
        *,
        principals: PrincipalRegistry,
        roles: RoleRegistry,
        permissions: PermissionEngine,
        policy: PolicyEngine,
        sessions: SessionRegistry,
        events: EventBus | None = None,
    ) -> None:
        if not isinstance(principals, PrincipalRegistry):
            raise AuthorizationError("a valid PrincipalRegistry is required")
        if not isinstance(roles, RoleRegistry):
            raise AuthorizationError("a valid RoleRegistry is required")
        if not isinstance(permissions, PermissionEngine):
            raise AuthorizationError("a valid PermissionEngine is required")
        if not isinstance(policy, PolicyEngine):
            raise AuthorizationError("a valid PolicyEngine is required")
        if not isinstance(sessions, SessionRegistry):
            raise AuthorizationError("a valid SessionRegistry is required")
        if events is not None and not isinstance(events, EventBus):
            raise AuthorizationError("events must be an EventBus when provided")
        self._principals = principals
        self._roles = roles
        self._permissions = permissions
        self._policy = policy
        self._sessions = sessions
        self._events = events
        self._log: list[AccessDecision] = []

    # -- component access -------------------------------------------------------

    @property
    def principals(self) -> PrincipalRegistry:
        return self._principals

    @property
    def roles(self) -> RoleRegistry:
        return self._roles

    @property
    def permissions(self) -> PermissionEngine:
        return self._permissions

    @property
    def policy(self) -> PolicyEngine:
        return self._policy

    @property
    def sessions(self) -> SessionRegistry:
        return self._sessions

    @property
    def decisions(self) -> tuple[AccessDecision, ...]:
        """An immutable snapshot of the append-only decision log (in order)."""
        return tuple(self._log)

    # -- principal & session lifecycle -----------------------------------------

    def register_principal(self, principal: Principal) -> Principal:
        """Register a principal into the principal registry (idempotent)."""
        return self._principals.register(principal)

    def establish_session(
        self,
        principal: Principal,
        *,
        issued_at: int,
        ttl: int,
        credential_ref: str | None = None,
    ) -> Session:
        """Register the principal (idempotent) and establish a session for it.

        Keeps the principal registry and the session registry consistent so a later
        :meth:`authorize` can always resolve the session's principal.
        """
        self._principals.register(principal)
        return self._sessions.establish(
            principal, issued_at=issued_at, ttl=ttl, credential_ref=credential_ref
        )

    def revoke_session(self, session_id: str, *, tick: int) -> Session:
        """Revoke a session (idempotent, append-only)."""
        return self._sessions.revoke(session_id, tick=tick)

    # -- authorization ----------------------------------------------------------

    def authorize_principal(
        self,
        principal: Principal,
        group: CapabilityGroup,
        permission: Permission,
        *,
        tenant: str | None = None,
        resource: str | None = None,
    ) -> AccessDecision:
        """Evaluate a decision for an explicit principal (no session), fail-closed."""
        request = AccessRequest.create(
            principal.principal_id,
            principal.roles,
            group,
            permission,
            tenant=tenant,
            resource=resource,
        )
        decision = self._policy.evaluate(principal, request)
        return self._record(decision)

    def authorize(
        self,
        session_id: str,
        group: CapabilityGroup,
        permission: Permission,
        *,
        now: int,
        tenant: str | None = None,
        resource: str | None = None,
    ) -> AccessDecision:
        """Evaluate a decision for a session-bearing request (the primary entry point).

        Fail-closed: an absent / expired / revoked session, or a session whose
        principal is not registered, denies without consulting the policy grant.
        """
        try:
            session = self._sessions.validate(session_id, now)
        except SessionError:
            return self._deny_without_session(session_id, group, permission, now, tenant, resource)

        try:
            principal = self._principals.get(session.principal_id)
        except Exception:  # noqa: BLE001 — unregistered principal is a fail-closed deny
            request = self._synthetic_request(
                session.principal_id, frozenset(), group, permission, tenant, resource
            )
            return self._record(
                AccessDecision.create(request, Decision.DENY, "principal-unregistered")
            )

        return self.authorize_principal(
            principal, group, permission, tenant=tenant, resource=resource
        )

    # -- evidence ---------------------------------------------------------------

    def evidence(self) -> IdentityEvidence:
        """Produce the deterministic Identity Evidence over all decisions so far."""
        return IdentityEvidence.create(
            principals_fingerprint=self._principals.fingerprint(),
            roles_fingerprint=self._roles.fingerprint(),
            decisions=tuple(d.to_dict() for d in self._log),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "principals": self._principals.to_dict(),
            "roles": self._roles.to_dict(),
            "sessions": self._sessions.to_dict(),
            "decision_count": len(self._log),
            "evidence": self.evidence().to_dict(),
        }

    # -- internals --------------------------------------------------------------

    def _deny_without_session(
        self,
        session_id: str,
        group: CapabilityGroup,
        permission: Permission,
        now: int,
        tenant: str | None,
        resource: str | None,
    ) -> AccessDecision:
        if session_id in self._sessions:
            session = self._sessions.get(session_id)
            reason = f"session-{session.effective_status(now).value}"
            principal_id = session.principal_id
        else:
            reason = "session-absent"
            principal_id = "anonymous"
        request = self._synthetic_request(
            principal_id, frozenset(), group, permission, tenant, resource
        )
        return self._record(AccessDecision.create(request, Decision.DENY, reason))

    @staticmethod
    def _synthetic_request(
        principal_id: str,
        roles: frozenset,
        group: CapabilityGroup,
        permission: Permission,
        tenant: str | None,
        resource: str | None,
    ) -> AccessRequest:
        return AccessRequest.create(
            principal_id or "anonymous",
            roles,
            group,
            permission,
            tenant=tenant,
            resource=resource,
        )

    def _record(self, decision: AccessDecision) -> AccessDecision:
        """Append a decision to the audit log and emit an audit event (if bound)."""
        self._log.append(decision)
        if self._events is not None:
            self._events.publish(
                ACCESS_EVENT,
                source="platform.identity.authorization",
                subject=decision.request.principal_id,
                payload=decision.to_dict(),
            )
        return decision


def build_authorization_service(
    *,
    principals: PrincipalRegistry | None = None,
    roles: RoleRegistry | None = None,
    events: EventBus | None = None,
) -> AuthorizationService:
    """Default, registry-driven composition of the Identity Platform.

    Seeds the §3.2 RBAC matrix (unless a role registry is supplied) and wires the
    permission engine, policy engine, and session registry into an
    :class:`AuthorizationService`. An empty principal registry is used unless one is
    supplied.
    """
    principal_registry = principals if principals is not None else PrincipalRegistry()
    role_registry = roles if roles is not None else default_role_registry()
    permission_engine = PermissionEngine(role_registry)
    policy_engine = PolicyEngine(permission_engine)
    session_registry = SessionRegistry()
    return AuthorizationService(
        principals=principal_registry,
        roles=role_registry,
        permissions=permission_engine,
        policy=policy_engine,
        sessions=session_registry,
        events=events,
    )


def bootstrap_identity(context: Any) -> AuthorizationService:
    """Compose the Identity Platform onto a :class:`PlatformContext` (registry-driven).

    Publishes the six identity contracts into the foundation service registry
    (EC2-EPIC-001), binds the authorization service to the context event bus, and
    emits a deterministic ``identity.bootstrap.completed`` event. The parameter is
    typed loosely to avoid a hard import cycle on the foundation bootstrap module.
    """
    from platform.foundation.services import ServiceDescriptor

    service = build_authorization_service(events=context.events)

    # Register the six identity service declarations (contract-first, PL-05).
    contracts = {c.name: c for c in default_identity_contracts()}
    for ref in IDENTITY_CONTRACTS:
        if ref.name in context.services:
            continue
        context.services.register(
            ServiceDescriptor(
                name=ref.name,
                contract=contracts[ref.name],
                capabilities=("PC-01", "PC-02") if "authorization" in ref.name else ("PC-02",),
                description=f"Identity Platform service: {ref.name}.",
            ),
            provider=lambda svc=service: svc,
        )

    context.events.publish(
        IDENTITY_BOOTSTRAP_EVENT,
        source="platform.identity.bootstrap",
        subject=context.program_id,
        payload={
            "roles": len(service.roles),
            "identity_contracts": [ref.name for ref in IDENTITY_CONTRACTS],
            "roles_fingerprint": service.roles.fingerprint(),
        },
    )
    return service


__all__ = [
    "ACCESS_EVENT",
    "IDENTITY_BOOTSTRAP_EVENT",
    "IdentityEvidence",
    "AuthorizationService",
    "build_authorization_service",
    "bootstrap_identity",
]
