"""EC2-TASK-000067 — Policy evaluation engine tests (invariants + negative access)."""

from __future__ import annotations

from platform.foundation.identity import Permission, Principal, Role
from platform.identity.contracts import AccessRequest, CapabilityGroup, Decision
from platform.identity.errors import PolicyEvaluationError
from platform.identity.permissions import EffectivePermissions, PermissionEngine
from platform.identity.policy import NamedPolicyRule, PolicyEngine
from platform.identity.roles import default_role_registry

import pytest

C, R, X, A = (
    Permission.CREATE,
    Permission.READ,
    Permission.EXECUTE,
    Permission.ADMINISTER,
)


def _policy() -> PolicyEngine:
    return PolicyEngine(PermissionEngine(default_role_registry()))


def _req(principal: Principal, group, permission, *, tenant=None, resource=None):
    return AccessRequest.create(
        principal.principal_id, principal.roles, group, permission, tenant=tenant, resource=resource
    )


def test_permit_on_valid_grant():
    pol = _policy()
    dev = Principal.create("dev", [Role.DEVELOPER])
    dec = pol.evaluate(dev, _req(dev, CapabilityGroup.GENERATION_REQUESTS, X))
    assert dec.decision is Decision.PERMIT
    assert dec.reason == "rbac-grant"


def test_default_deny_when_no_grant():
    pol = _policy()
    dev = Principal.create("dev", [Role.DEVELOPER])
    dec = pol.evaluate(dev, _req(dev, CapabilityGroup.USER_ROLE_QUOTA_ADMIN, R))
    assert dec.decision is Decision.DENY
    assert dec.reason == "no-grant"


def test_frozen_corpus_write_forbidden_for_admin():
    pol = _policy()
    admin = Principal.create("root", [Role.PLATFORM_ADMINISTRATOR])
    dec = pol.evaluate(
        admin,
        _req(admin, CapabilityGroup.ADMINISTRATION_POLICY, C, resource="00-BOOK/x.md"),
    )
    assert dec.decision is Decision.DENY
    assert dec.reason == "frozen-corpus-write-forbidden"


def test_frozen_corpus_read_is_allowed_when_granted():
    pol = _policy()
    admin = Principal.create("root", [Role.PLATFORM_ADMINISTRATOR])
    # ADMINISTER expands to include READ; reading a frozen path is not a write.
    dec = pol.evaluate(
        admin,
        _req(admin, CapabilityGroup.ADMINISTRATION_POLICY, R, resource="00-BOOK/x.md"),
    )
    assert dec.decision is Decision.PERMIT


def test_frozen_corpus_all_prefixes():
    pol = _policy()
    admin = Principal.create("root", [Role.PLATFORM_ADMINISTRATOR])
    for prefix in ("00-BOOK", "00-SOURCE", "99-FREEZE"):
        dec = pol.evaluate(
            admin,
            _req(admin, CapabilityGroup.ADMINISTRATION_POLICY, A, resource=f"/{prefix}/inner/y"),
        )
        assert dec.reason == "frozen-corpus-write-forbidden"


def test_certification_ledger_append_only():
    pol = _policy()
    admin = Principal.create("root", [Role.PLATFORM_ADMINISTRATOR])
    dec = pol.evaluate(admin, _req(admin, CapabilityGroup.CERTIFICATION_LEDGER, C))
    assert dec.decision is Decision.DENY
    assert dec.reason == "certification-ledger-append-only"
    # Read is fine.
    ok = pol.evaluate(admin, _req(admin, CapabilityGroup.CERTIFICATION_LEDGER, R))
    assert ok.decision is Decision.PERMIT


def test_read_only_role_no_mutation():
    pol = _policy()
    auditor = Principal.create("aud", [Role.AUDITOR])
    dec = pol.evaluate(auditor, _req(auditor, CapabilityGroup.GENERATION_REQUESTS, X))
    assert dec.decision is Decision.DENY
    assert dec.reason == "read-only-role-no-mutation"


def test_cert_authority_attest_permit_with_obligation():
    pol = _policy()
    ca = Principal.create("ca", [Role.CERTIFICATION_AUTHORITY])
    dec = pol.evaluate(ca, _req(ca, CapabilityGroup.CERTIFICATION_LEDGER, R))
    assert dec.decision is Decision.PERMIT
    assert "attest" in dec.obligations


def test_scoped_principal_permit_within_tenant():
    pol = _policy()
    partner = Principal.create("prt", [Role.PARTNER], tenant="ws-1")
    dec = pol.evaluate(
        partner, _req(partner, CapabilityGroup.GENERATION_REQUESTS, X, tenant="ws-1")
    )
    assert dec.decision is Decision.PERMIT
    assert "tenant-scoped" in dec.obligations


def test_scoped_principal_denied_cross_tenant():
    pol = _policy()
    partner = Principal.create("prt", [Role.PARTNER], tenant="ws-1")
    dec = pol.evaluate(
        partner, _req(partner, CapabilityGroup.GENERATION_REQUESTS, X, tenant="ws-2")
    )
    assert dec.decision is Decision.DENY
    assert dec.reason == "tenant-scope-violation"


def test_scoped_request_missing_tenant_denied():
    pol = _policy()
    partner = Principal.create("prt", [Role.PARTNER], tenant="ws-1")
    dec = pol.evaluate(partner, _req(partner, CapabilityGroup.GENERATION_REQUESTS, X))
    assert dec.decision is Decision.DENY
    assert dec.reason == "scoped-request-missing-tenant"


def test_scoped_principal_missing_own_tenant_denied():
    pol = _policy()
    # Partner without a tenant scope (constructed directly), holding a scoped grant.
    partner = Principal.create("prt", [Role.PARTNER])
    dec = pol.evaluate(
        partner, _req(partner, CapabilityGroup.GENERATION_REQUESTS, X, tenant="ws-1")
    )
    assert dec.decision is Decision.DENY
    assert dec.reason == "scoped-principal-missing-tenant"


def test_partner_read_within_tenant_portal():
    pol = _policy()
    partner = Principal.create("prt", [Role.PARTNER], tenant="ws-1")
    dec = pol.evaluate(partner, _req(partner, CapabilityGroup.PORTAL_NAVIGATION, R, tenant="ws-1"))
    assert dec.decision is Decision.PERMIT


def test_integrator_denied_portal_no_grant():
    pol = _policy()
    integ = Principal.create("int", [Role.INTEGRATOR], tenant="ws-9")
    dec = pol.evaluate(integ, _req(integ, CapabilityGroup.PORTAL_NAVIGATION, R, tenant="ws-9"))
    assert dec.decision is Decision.DENY
    assert dec.reason == "no-grant"


def test_business_user_denied_runtime_ops():
    pol = _policy()
    biz = Principal.create("biz", [Role.BUSINESS_USER])
    dec = pol.evaluate(biz, _req(biz, CapabilityGroup.RUNTIME_OPERATIONS, X))
    assert dec.decision is Decision.DENY
    assert dec.reason == "no-grant"


def test_evaluate_requires_matching_principal():
    pol = _policy()
    dev = Principal.create("dev", [Role.DEVELOPER])
    other = Principal.create("other", [Role.DEVELOPER])
    with pytest.raises(PolicyEvaluationError):
        pol.evaluate(dev, _req(other, CapabilityGroup.PORTAL_NAVIGATION, R))


def test_evaluate_input_validation():
    pol = _policy()
    dev = Principal.create("dev", [Role.DEVELOPER])
    with pytest.raises(PolicyEvaluationError):
        pol.evaluate("not-a-principal", _req(dev, CapabilityGroup.API_ACCESS, X))
    with pytest.raises(PolicyEvaluationError):
        pol.evaluate(dev, "not-a-request")


def test_engine_requires_permission_engine():
    with pytest.raises(PolicyEvaluationError):
        PolicyEngine("not-an-engine")


def test_custom_rule_can_deny_and_names_exposed():
    def deny_all(principal, request, effective):
        from platform.identity.contracts import AccessDecision

        return AccessDecision.create(request, Decision.DENY, "custom-blocked")

    pol = PolicyEngine(
        PermissionEngine(default_role_registry()),
        extra_rules=[NamedPolicyRule(name="deny-all", rule=deny_all)],
    )
    dev = Principal.create("dev", [Role.DEVELOPER])
    dec = pol.evaluate(dev, _req(dev, CapabilityGroup.GENERATION_REQUESTS, X))
    assert dec.reason == "custom-blocked"
    assert "deny-all" in pol.rule_names


def test_named_policy_rule_validation():
    with pytest.raises(PolicyEvaluationError):
        NamedPolicyRule(name="", rule=lambda p, r, e: None)
    with pytest.raises(PolicyEvaluationError):
        NamedPolicyRule(name="x", rule="not-callable")
    with pytest.raises(PolicyEvaluationError):
        PolicyEngine(PermissionEngine(default_role_registry()), extra_rules=["nope"])


def test_custom_rule_passthrough_reaches_grant_check():
    # A custom rule returning None must not affect the built-in grant decision.
    passthrough = NamedPolicyRule(name="noop", rule=lambda p, r, e: None)
    pol = PolicyEngine(PermissionEngine(default_role_registry()), extra_rules=[passthrough])
    dev = Principal.create("dev", [Role.DEVELOPER])
    dec = pol.evaluate(dev, _req(dev, CapabilityGroup.GENERATION_REQUESTS, X))
    assert dec.decision is Decision.PERMIT


def test_effective_permissions_dataclass_helpers():
    eff = EffectivePermissions(
        group=CapabilityGroup.API_ACCESS,
        permissions=frozenset({X}),
        scoped=False,
        attest=False,
        contributing_roles=frozenset({Role.DEVELOPER}),
    )
    assert eff.allows(X)
    assert not eff.allows(R)


def test_write_to_non_frozen_resource_permitted():
    pol = _policy()
    admin = Principal.create("root", [Role.PLATFORM_ADMINISTRATOR])
    dec = pol.evaluate(
        admin,
        _req(admin, CapabilityGroup.ADMINISTRATION_POLICY, C, resource="workspace/cfg"),
    )
    assert dec.decision is Decision.PERMIT


def test_engine_exposes_components():
    pol = _policy()
    assert isinstance(pol.permissions, PermissionEngine)
    assert len(pol.roles) == 9
    assert pol.permissions.roles is pol.roles
    assert all(isinstance(name, str) for name in pol.rule_names)
