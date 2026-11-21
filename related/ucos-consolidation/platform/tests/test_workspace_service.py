"""EC2-TASK-000088 — Workspace service tests.

Covers the governed L3 composition point end to end: fail-closed construction and
component validation, authorization-gated workspace creation with creator enrollment,
the three-gate composed access decision (identity ∧ isolation ∧ membership) — including
every denial reason — selection/context handoff, membership management and lifecycle
transitions (manager-gated), authorization- and isolation-scoped discovery/search,
health integration, deterministic evidence (P5), and governed-action emission (PC-16).
"""

from __future__ import annotations

from platform.foundation.bootstrap import bootstrap_platform
from platform.foundation.identity import Permission, Principal, Role
from platform.identity.service import build_authorization_service
from platform.observability.health import HealthRegistry
from platform.observability.service import build_observability_service
from platform.workspace.contracts import MemberRole, WorkspaceStatus
from platform.workspace.errors import (
    WorkspaceAccessError,
    WorkspaceRegistryError,
    WorkspaceServiceError,
)
from platform.workspace.health import WorkspaceHealth, workspace_health_checks
from platform.workspace.membership import MembershipRegistry
from platform.workspace.registration import WorkspaceRegistry
from platform.workspace.search import WorkspaceSearch
from platform.workspace.service import (
    WORKSPACE_ACCESS_EVENT,
    WORKSPACE_CREATED_EVENT,
    WORKSPACE_MEMBER_ADDED_EVENT,
    WORKSPACE_MEMBER_REMOVED_EVENT,
    WorkspaceService,
    build_workspace_service,
)

import pytest

# --------------------------------------------------------------------------- #
# Helpers                                                                      #
# --------------------------------------------------------------------------- #


def _service(*, events=None, observability=None):
    auth = build_authorization_service(events=events)
    service = build_workspace_service(
        authorization=auth, observability=observability, events=events
    )
    return auth, service


def _session(auth, role: Role, subject: str = "u@x", tenant: str | None = None):
    principal = Principal.create(subject, [role], tenant=tenant)
    return auth.establish_session(principal, issued_at=0, ttl=1000)


def _valid_kwargs(auth):
    reg = WorkspaceRegistry()
    mem = MembershipRegistry()
    hr = HealthRegistry()
    for check in workspace_health_checks():
        hr.register(check)
    return {
        "registry": reg,
        "membership": mem,
        "authorization": auth,
        "search": WorkspaceSearch(reg, auth),
        "health": WorkspaceHealth(reg, mem),
        "health_registry": hr,
    }


# --------------------------------------------------------------------------- #
# Construction / composition                                                   #
# --------------------------------------------------------------------------- #


def test_build_requires_authorization_service():
    with pytest.raises(WorkspaceServiceError):
        build_workspace_service(authorization="nope")  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "field",
    ["registry", "membership", "authorization", "search", "health", "health_registry"],
)
def test_service_rejects_each_invalid_required_component(field):
    auth = build_authorization_service()
    kwargs = _valid_kwargs(auth)
    kwargs[field] = "nope"
    with pytest.raises(WorkspaceServiceError):
        WorkspaceService(**kwargs)  # type: ignore[arg-type]


@pytest.mark.parametrize("field", ["isolation", "observability", "events"])
def test_service_rejects_each_invalid_optional_component(field):
    auth = build_authorization_service()
    kwargs = _valid_kwargs(auth)
    kwargs[field] = "nope"
    with pytest.raises(WorkspaceServiceError):
        WorkspaceService(**kwargs)  # type: ignore[arg-type]


def test_component_property_getters():
    auth, service = _service()
    assert service.registry is not None
    assert service.membership is not None
    assert service.authorization is auth
    assert service.isolation is not None
    assert service.health is not None
    assert service.observability is None
    assert service.access_evaluation_count == 0


# --------------------------------------------------------------------------- #
# Creation                                                                     #
# --------------------------------------------------------------------------- #


def test_create_workspace_enrolls_creator_as_owner_and_emits_event():
    events = bootstrap_platform().events
    auth, service = _service(events=events)
    session = _session(auth, Role.DEVELOPER, subject="dev@x")
    ws = service.create_workspace(session.session_id, "acme-core", "Acme", now=1, tenant="acme")
    assert ws.slug == "acme-core"
    owner = service.membership.member(ws.workspace_id, ws_owner_id(auth, "dev@x"))
    assert owner is not None and owner.role is MemberRole.OWNER
    assert len(events.events_of(WORKSPACE_CREATED_EVENT)) == 1


def ws_owner_id(auth, subject: str) -> str:
    principal = Principal.create(subject, [Role.DEVELOPER])
    return principal.principal_id


def test_create_workspace_denied_without_create_grant():
    # Operator holds only READ on the workspace group — creation is denied.
    auth, service = _service()
    session = _session(auth, Role.OPERATOR)
    with pytest.raises(WorkspaceAccessError):
        service.create_workspace(session.session_id, "s", "n", now=1)


def test_create_workspace_denied_cross_tenant():
    auth, service = _service()
    session = _session(auth, Role.DEVELOPER, tenant="acme")
    with pytest.raises(WorkspaceAccessError):
        service.create_workspace(session.session_id, "s", "n", now=1, tenant="beta")


# --------------------------------------------------------------------------- #
# Access evaluation (identity ∧ isolation ∧ membership)                        #
# --------------------------------------------------------------------------- #


def test_access_granted_for_member_owner():
    auth, service = _service()
    session = _session(auth, Role.DEVELOPER, subject="dev@x")
    ws = service.create_workspace(session.session_id, "s", "n", now=1)
    access = service.evaluate_access(session.session_id, ws.workspace_id, Permission.READ, now=2)
    assert access.granted is True
    assert access.reason == "granted"
    assert access.member_role is MemberRole.OWNER
    assert access.to_dict()["access_id"].startswith("UCOS-WACC-")
    assert service.access_evaluation_count == 1


def test_access_granted_for_administrator_without_membership():
    auth, service = _service()
    dev = _session(auth, Role.DEVELOPER, subject="dev@x")
    ws = service.create_workspace(dev.session_id, "s", "n", now=1)
    admin = _session(auth, Role.PLATFORM_ADMINISTRATOR, subject="admin@x")
    access = service.evaluate_access(admin.session_id, ws.workspace_id, Permission.READ, now=2)
    assert access.granted is True
    assert access.member_role is None  # admin, not a member


def test_access_denied_when_authorization_refuses():
    auth, service = _service()
    dev = _session(auth, Role.DEVELOPER, subject="dev@x")
    ws = service.create_workspace(dev.session_id, "s", "n", now=1)
    # Operator lacks CREATE on the workspace group → not permitted.
    op = _session(auth, Role.OPERATOR, subject="op@x")
    access = service.evaluate_access(op.session_id, ws.workspace_id, Permission.CREATE, now=2)
    assert access.granted is False
    assert access.reason == "no-grant"


def test_access_denied_cross_tenant_isolation():
    auth, service = _service()
    admin = _session(auth, Role.PLATFORM_ADMINISTRATOR, subject="admin@x")
    ws = service.create_workspace(admin.session_id, "beta-ws", "n", now=1, tenant="beta")
    dev = _session(auth, Role.DEVELOPER, subject="dev@x", tenant="acme")
    access = service.evaluate_access(dev.session_id, ws.workspace_id, Permission.READ, now=2)
    assert access.granted is False
    assert access.reason == "tenant-isolation-violation"


def test_access_denied_when_not_a_member():
    auth, service = _service()
    owner = _session(auth, Role.DEVELOPER, subject="dev@x")
    ws = service.create_workspace(owner.session_id, "s", "n", now=1)
    other = _session(auth, Role.DEVELOPER, subject="other@x")
    access = service.evaluate_access(other.session_id, ws.workspace_id, Permission.READ, now=2)
    assert access.granted is False
    assert access.reason == "not-a-member"


def test_access_denied_mutation_on_non_active_workspace():
    auth, service = _service()
    owner = _session(auth, Role.DEVELOPER, subject="dev@x")
    ws = service.create_workspace(owner.session_id, "s", "n", now=1)
    service.transition(owner.session_id, ws.workspace_id, WorkspaceStatus.SUSPENDED, now=2)
    access = service.evaluate_access(owner.session_id, ws.workspace_id, Permission.CREATE, now=3)
    assert access.granted is False
    assert access.reason == "workspace-suspended"


def test_evaluate_access_rejects_bad_permission():
    auth, service = _service()
    session = _session(auth, Role.DEVELOPER, subject="dev@x")
    ws = service.create_workspace(session.session_id, "s", "n", now=1)
    with pytest.raises(WorkspaceServiceError):
        service.evaluate_access(session.session_id, ws.workspace_id, "read", now=2)  # type: ignore[arg-type]


def test_evaluate_access_unknown_workspace_is_fail_closed():
    auth, service = _service()
    session = _session(auth, Role.DEVELOPER)
    with pytest.raises(WorkspaceRegistryError):
        service.evaluate_access(session.session_id, "UCOS-WSPC-missing", Permission.READ, now=1)


def test_access_evaluation_is_emitted_as_governed_action():
    events = bootstrap_platform().events
    auth, service = _service(events=events)
    session = _session(auth, Role.DEVELOPER, subject="dev@x")
    ws = service.create_workspace(session.session_id, "s", "n", now=1)
    service.evaluate_access(session.session_id, ws.workspace_id, Permission.READ, now=2)
    assert len(events.events_of(WORKSPACE_ACCESS_EVENT)) == 1


# --------------------------------------------------------------------------- #
# Selection / context                                                          #
# --------------------------------------------------------------------------- #


def test_select_workspace_returns_runtime_context():
    auth, service = _service()
    session = _session(auth, Role.DEVELOPER, subject="dev@x")
    ws = service.create_workspace(session.session_id, "s", "n", now=1)
    ctx = service.select_workspace(session.session_id, ws.workspace_id, now=2)
    assert ctx.workspace_id == ws.workspace_id
    assert ctx.member_role is MemberRole.OWNER
    assert ctx.is_active is True


def test_select_workspace_denied_for_non_member():
    auth, service = _service()
    owner = _session(auth, Role.DEVELOPER, subject="dev@x")
    ws = service.create_workspace(owner.session_id, "s", "n", now=1)
    other = _session(auth, Role.DEVELOPER, subject="other@x")
    with pytest.raises(WorkspaceAccessError):
        service.select_workspace(other.session_id, ws.workspace_id, now=2)


def test_resolve_reads_by_slug():
    auth, service = _service()
    session = _session(auth, Role.DEVELOPER, subject="dev@x")
    service.create_workspace(session.session_id, "s", "n", now=1, tenant="acme")
    assert service.resolve("s", "acme").slug == "s"


# --------------------------------------------------------------------------- #
# Discovery / search                                                           #
# --------------------------------------------------------------------------- #


def test_discover_returns_authorized_isolated_workspaces():
    auth, service = _service()
    admin = _session(auth, Role.PLATFORM_ADMINISTRATOR, subject="admin@x")
    service.create_workspace(admin.session_id, "acme-ws", "n", now=1, tenant="acme")
    service.create_workspace(admin.session_id, "beta-ws", "n", now=1, tenant="beta")
    dev = _session(auth, Role.DEVELOPER, subject="dev@x", tenant="acme")
    slugs = {ws.slug for ws in service.discover(dev.session_id, now=2)}
    assert "acme-ws" in slugs
    assert "beta-ws" not in slugs  # cross-tenant filtered


def test_discover_returns_empty_for_invalid_session():
    _, service = _service()
    assert service.discover("UCOS-SESS-missing", now=1) == ()


def test_discover_returns_empty_when_authorization_refused():
    auth, service = _service()
    # Integrator's scoped READ is refused when the request tenant does not match.
    session = _session(auth, Role.INTEGRATOR, subject="i@x", tenant="acme")
    assert service.discover(session.session_id, now=1, tenant=None) == ()


def test_search_delegates_to_workspace_search():
    auth, service = _service()
    session = _session(auth, Role.DEVELOPER, subject="dev@x")
    service.create_workspace(session.session_id, "acme-core", "Acme Core", now=1)
    response = service.search(session.session_id, "acme", now=2)
    assert response.authorized is True
    assert {h.workspace.slug for h in response.results} == {"acme-core"}


# --------------------------------------------------------------------------- #
# Membership management / lifecycle (manager-gated)                            #
# --------------------------------------------------------------------------- #


def test_owner_adds_and_removes_members_with_events():
    events = bootstrap_platform().events
    auth, service = _service(events=events)
    owner = _session(auth, Role.DEVELOPER, subject="dev@x")
    ws = service.create_workspace(owner.session_id, "s", "n", now=1)
    member = service.add_member(
        owner.session_id, ws.workspace_id, "UCOS-PRIN-guest", "guest@x", MemberRole.MEMBER, now=2
    )
    assert member.role is MemberRole.MEMBER
    removed = service.remove_member(owner.session_id, ws.workspace_id, "UCOS-PRIN-guest", now=3)
    assert removed.principal_id == "UCOS-PRIN-guest"
    assert len(events.events_of(WORKSPACE_MEMBER_ADDED_EVENT)) == 1
    assert len(events.events_of(WORKSPACE_MEMBER_REMOVED_EVENT)) == 1


def test_management_denied_for_plain_member():
    auth, service = _service()
    owner = _session(auth, Role.DEVELOPER, subject="dev@x")
    ws = service.create_workspace(owner.session_id, "s", "n", now=1)
    # Enroll a plain (non-owner) member who also holds a real session.
    member_session = _session(auth, Role.DEVELOPER, subject="member@x")
    member_principal = service.authorization.principals.get(
        service.authorization.sessions.validate(member_session.session_id, 1).principal_id
    )
    member_pid = member_principal.principal_id
    service.add_member(
        owner.session_id, ws.workspace_id, member_pid, "member@x", MemberRole.MEMBER, now=2
    )
    with pytest.raises(WorkspaceAccessError):
        service.add_member(
            member_session.session_id,
            ws.workspace_id,
            "UCOS-PRIN-z",
            "z@x",
            MemberRole.MEMBER,
            now=3,
        )


def test_management_denied_for_non_member():
    auth, service = _service()
    owner = _session(auth, Role.DEVELOPER, subject="dev@x")
    ws = service.create_workspace(owner.session_id, "s", "n", now=1)
    outsider = _session(auth, Role.DEVELOPER, subject="out@x")
    with pytest.raises(WorkspaceAccessError):
        service.transition(outsider.session_id, ws.workspace_id, WorkspaceStatus.ARCHIVED, now=2)


def test_administrator_can_manage_without_membership():
    auth, service = _service()
    dev = _session(auth, Role.DEVELOPER, subject="dev@x")
    ws = service.create_workspace(dev.session_id, "s", "n", now=1)
    admin = _session(auth, Role.PLATFORM_ADMINISTRATOR, subject="admin@x")
    updated = service.transition(
        admin.session_id, ws.workspace_id, WorkspaceStatus.SUSPENDED, now=2
    )
    assert updated.status is WorkspaceStatus.SUSPENDED


# --------------------------------------------------------------------------- #
# Health / evidence / summary                                                  #
# --------------------------------------------------------------------------- #


def test_health_report_uses_observability_model():
    _, service = _service()
    report = service.health_report()
    assert report["healthy"] is True


def test_evidence_is_deterministic_and_serializable():
    def run() -> str:
        auth, service = _service()
        session = _session(auth, Role.DEVELOPER, subject="dev@x")
        service.create_workspace(session.session_id, "s", "n", now=1)
        workspace_id = service.registry.all()[0].workspace_id
        service.evaluate_access(session.session_id, workspace_id, Permission.READ, now=2)
        return service.evidence().fingerprint()

    assert run() == run()


def test_evidence_reports_counts_and_health():
    auth, service = _service()
    session = _session(auth, Role.DEVELOPER, subject="dev@x")
    service.create_workspace(session.session_id, "s", "n", now=1)
    evidence = service.evidence()
    assert evidence.workspace_count == 1
    assert evidence.membership_count == 1
    assert evidence.evidence_id.startswith("UCOS-WSEV-")
    assert evidence.to_dict()["health_status"] in {"healthy", "degraded", "unhealthy"}


def test_to_dict_summary_reports_observability_binding():
    events = bootstrap_platform().events
    observability = build_observability_service(events=events)
    auth, service = _service(events=events, observability=observability)
    session = _session(auth, Role.DEVELOPER, subject="dev@x")
    service.create_workspace(session.session_id, "s", "n", now=1)
    summary = service.to_dict()
    assert summary["workspace_count"] == 1
    assert summary["observability_bound"] is True
    assert service.observability is observability
