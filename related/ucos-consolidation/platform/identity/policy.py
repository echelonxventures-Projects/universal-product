"""EC2-TASK-000067 — Policy Evaluation Engine (EC2-EPIC-002).

The fail-closed access-policy decision point. Given a principal and an
:class:`~platform.identity.contracts.AccessRequest`, it resolves the principal's
effective permissions (via the :class:`~platform.identity.permissions.PermissionEngine`)
and evaluates an **ordered, deterministic** set of policy rules to produce an
immutable :class:`~platform.identity.contracts.AccessDecision`.

Design (PL-04 least-privilege; fail-closed; §3.2 invariants):
    * **Default deny.** Absence of an explicit grant is DENY — never assumed-allow.
    * **Hard invariants evaluated first** (a matching guard denies regardless of any
      grant), in a fixed order so evaluation is reproducible:
        1. **Frozen-corpus write forbidden** — no role may write to the certified
           corpus (``00-BOOK``/``00-SOURCE``/``99-FREEZE``, DP-03, invariant i).
        2. **Certification/ledger append-only** — no role may mutate an issued
           certification record or ledger entry (invariant ii).
        3. **Read-only roles hold no mutation** — a principal bearing only read-only
           roles (Auditor, Certification Authority) is denied every mutation
           (invariant iii).
        4. **Tenant-scope isolation** — a scoped grant (Partner/Integrator) is honored
           only within the principal's own tenant; a missing or mismatched target
           tenant is denied (invariant iv).
    * **Grant check last.** If no guard fires, PERMIT iff the effective permissions
      include the requested verb, else DENY (``no-grant``).
    * **Obligations** — a permit over a scoped grant carries a ``tenant-scoped``
      obligation; a permit carrying attestation carries an ``attest`` obligation.

The engine is a pure function of its inputs and holds no wall-clock and no state
beyond its (immutable) rule ordering — identical inputs always yield an identical,
content-addressed decision.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass
from platform.foundation.identity import READ_ONLY_ROLES, Permission, Principal
from platform.identity.contracts import AccessDecision, AccessRequest, CapabilityGroup, Decision
from platform.identity.errors import PolicyEvaluationError
from platform.identity.permissions import EffectivePermissions, PermissionEngine
from platform.identity.roles import RoleRegistry

#: The certified corpus path prefixes that are read-only for every role (DP-03).
#:
#: These hold an immutable historical baseline, not an exemption from evolution: the
#: corpus advances by supersession into a new object (CEP-007 XIII) or by amendment of
#: the governing instrument (CEP-009), never by in-place modification of a certified
#: artifact. Identity immutable, history append-only, evolution unlimited through those
#: channels.
FROZEN_CORPUS_PREFIXES: tuple[str, ...] = ("00-BOOK", "00-SOURCE", "99-FREEZE")

#: The mutating permission verbs (READ is non-mutating).
WRITE_PERMISSIONS: frozenset[Permission] = frozenset(
    {Permission.CREATE, Permission.EXECUTE, Permission.ADMINISTER}
)

#: A policy rule: a pure predicate that returns a DENY decision or ``None``.
PolicyRule = Callable[[Principal, AccessRequest, EffectivePermissions], AccessDecision | None]


def _deny(request: AccessRequest, reason: str) -> AccessDecision:
    return AccessDecision.create(request, Decision.DENY, reason)


def _guard_frozen_corpus_write(
    principal: Principal, request: AccessRequest, effective: EffectivePermissions
) -> AccessDecision | None:
    """DENY any write targeting the certified corpus (invariant i, DP-03).

    Refuses in-place modification of an immutable historical baseline. It does not
    refuse evolution: the corpus advances by supersession (CEP-007 XIII) or amendment
    (CEP-009), which create new objects rather than rewriting certified ones.
    """
    if request.resource and request.permission in WRITE_PERMISSIONS:
        normalized = request.resource.lstrip("/")
        for prefix in FROZEN_CORPUS_PREFIXES:
            if normalized == prefix or normalized.startswith(prefix + "/"):
                return _deny(request, "frozen-corpus-write-forbidden")
    return None


def _guard_certification_append_only(
    principal: Principal, request: AccessRequest, effective: EffectivePermissions
) -> AccessDecision | None:
    """DENY any mutation of a certification record / ledger entry (invariant ii)."""
    if (
        request.group is CapabilityGroup.CERTIFICATION_LEDGER
        and request.permission in WRITE_PERMISSIONS
    ):
        return _deny(request, "certification-ledger-append-only")
    return None


def _guard_read_only_role_mutation(
    principal: Principal, request: AccessRequest, effective: EffectivePermissions
) -> AccessDecision | None:
    """DENY mutation for a principal bearing only read-only roles (invariant iii)."""
    if request.permission in WRITE_PERMISSIONS and principal.roles <= READ_ONLY_ROLES:
        return _deny(request, "read-only-role-no-mutation")
    return None


def _guard_tenant_scope_isolation(
    principal: Principal, request: AccessRequest, effective: EffectivePermissions
) -> AccessDecision | None:
    """DENY a scoped grant used outside the principal's own tenant (invariant iv)."""
    if effective.granted and effective.scoped:
        if principal.tenant is None:
            return _deny(request, "scoped-principal-missing-tenant")
        if request.tenant is None:
            return _deny(request, "scoped-request-missing-tenant")
        if request.tenant != principal.tenant:
            return _deny(request, "tenant-scope-violation")
    return None


#: The built-in hard invariants, in fixed deterministic evaluation order.
_BUILTIN_GUARDS: tuple[PolicyRule, ...] = (
    _guard_frozen_corpus_write,
    _guard_certification_append_only,
    _guard_read_only_role_mutation,
    _guard_tenant_scope_isolation,
)


@dataclass(frozen=True, slots=True)
class NamedPolicyRule:
    """A named, custom deny-guard appended after the built-in invariants."""

    name: str
    rule: PolicyRule

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name:
            raise PolicyEvaluationError("a policy rule requires a name")
        if not callable(self.rule):
            raise PolicyEvaluationError("a policy rule must be callable", name=self.name)


class PolicyEngine:
    """The deterministic, fail-closed access-policy decision point (§3.2)."""

    __slots__ = ("_permissions", "_extra_rules")

    def __init__(
        self,
        permissions: PermissionEngine,
        *,
        extra_rules: Iterable[NamedPolicyRule] = (),
    ) -> None:
        if not isinstance(permissions, PermissionEngine):
            raise PolicyEvaluationError("a valid PermissionEngine is required")
        self._permissions = permissions
        self._extra_rules = tuple(extra_rules)
        for rule in self._extra_rules:
            if not isinstance(rule, NamedPolicyRule):
                raise PolicyEvaluationError("extra rules must be NamedPolicyRule")

    @property
    def permissions(self) -> PermissionEngine:
        return self._permissions

    @property
    def roles(self) -> RoleRegistry:
        return self._permissions.roles

    @property
    def rule_names(self) -> tuple[str, ...]:
        """The ordered names of all evaluated rules (built-ins then custom)."""
        builtins = tuple(g.__name__ for g in _BUILTIN_GUARDS)
        return builtins + tuple(r.name for r in self._extra_rules)

    def evaluate(self, principal: Principal, request: AccessRequest) -> AccessDecision:
        """Evaluate the policy for ``principal`` over ``request`` (fail-closed)."""
        if not isinstance(principal, Principal):
            raise PolicyEvaluationError("a valid Principal is required")
        if not isinstance(request, AccessRequest):
            raise PolicyEvaluationError("a valid AccessRequest is required")
        if request.principal_id != principal.principal_id:
            raise PolicyEvaluationError(
                "request principal_id does not match the evaluated principal",
                principal_id=principal.principal_id,
            )
        effective = self._permissions.resolve(principal, request.group)

        # Hard invariants first (built-ins, then custom), fixed order, first DENY wins.
        for guard in _BUILTIN_GUARDS:
            decision = guard(principal, request, effective)
            if decision is not None:
                return decision
        for named in self._extra_rules:
            decision = named.rule(principal, request, effective)
            if decision is not None:
                return decision

        # Default-deny grant check.
        if not effective.allows(request.permission):
            return _deny(request, "no-grant")

        obligations: set[str] = set()
        if effective.scoped:
            obligations.add("tenant-scoped")
        if effective.attest:
            obligations.add("attest")
        return AccessDecision.create(
            request,
            Decision.PERMIT,
            "rbac-grant",
            obligations=frozenset(obligations),
        )


__all__ = [
    "FROZEN_CORPUS_PREFIXES",
    "WRITE_PERMISSIONS",
    "PolicyRule",
    "NamedPolicyRule",
    "PolicyEngine",
]
