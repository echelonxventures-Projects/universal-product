"""EC2-TASK-000095 — Project service tests.

Covers the governed L3 composition point end to end: fail-closed construction and
component validation, authorization-gated project creation scoped to an active parent
workspace with owner recording, the composed access decision (identity ∧ isolation ∧
owner-scoping) — including every denial reason — selection/context handoff, lifecycle
transitions and association add/remove (owner/administrator-gated), deterministic
status derivation, authorization- and isolation-scoped discovery/search, health
integration, deterministic evidence (P5), and governed-action emission (PC-16).
"""

from __future__ import annotations

from platform.foundation.bootstrap import bootstrap_platform
from platform.foundation.identity import Principal, Role
from platform.identity.service import build_authorization_service
from platform.observability.health import HealthRegistry
from platform.observability.service import build_observability_service
from platform.projects.associations import AssociationRegistry
from platform.projects.contracts import AssociationKind, ProjectAction, ProjectStatus
from platform.projects.errors import (
    ProjectAccessError,
    ProjectAssociationError,
    ProjectServiceError,
)
from platform.projects.health import ProjectHealth, project_health_checks
from platform.projects.registry import ProjectRegistry
from platform.projects.search import ProjectSearch
from platform.projects.service import (
    PROJECT_ACCESS_EVENT,
    PROJECT_ASSOCIATION_ADDED_EVENT,
    PROJECT_ASSOCIATION_REMOVED_EVENT,
    PROJECT_CREATED_EVENT,
    PROJECT_LIFECYCLE_EVENT,
    ProjectService,
    build_project_service,
)
from platform.workspace.contracts import WorkspaceStatus
from platform.workspace.errors import WorkspaceRegistryError
from platform.workspace.registration import WorkspaceRegistry

import pytest

# --------------------------------------------------------------------------- #
# Helpers                                                                      #
# --------------------------------------------------------------------------- #


def _fixture(*, events=None, observability=None):
    auth = build_authorization_service(events=events)
    workspaces = WorkspaceRegistry()
    service = build_project_service(
        authorization=auth,
        workspaces=workspaces,
        observability=observability,
        events=events,
    )
    return auth, workspaces, service


def _session(auth, role: Role, subject="u@x", tenant=None):
    principal = Principal.create(subject, [role], tenant=tenant)
    return auth.establish_session(principal, issued_at=0, ttl=1000)


def _workspace(workspaces, *, tenant=None, slug="team"):
    return workspaces.create(slug, slug.title(), "owner@x", tenant=tenant)


def _valid_kwargs(auth, workspaces):
    reg = ProjectRegistry()
    assoc = AssociationRegistry()
    hr = HealthRegistry()
    for check in project_health_checks():
        hr.register(check)
    return {
        "registry": reg,
        "associations": assoc,
        "authorization": auth,
        "workspaces": workspaces,
        "search": ProjectSearch(reg, auth),
        "health": ProjectHealth(reg, assoc),
        "health_registry": hr,
    }


# --------------------------------------------------------------------------- #
# Construction / composition                                                   #
# --------------------------------------------------------------------------- #


def test_build_requires_authorization_and_workspaces():
    with pytest.raises(ProjectServiceError):
        build_project_service(authorization="nope", workspaces=WorkspaceRegistry())  # type: ignore[arg-type]
    with pytest.raises(ProjectServiceError):
        build_project_service(authorization=build_authorization_service(), workspaces="nope")  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "field",
    [
        "registry",
        "associations",
        "authorization",
        "workspaces",
        "search",
        "health",
        "health_registry",
    ],
)
def test_service_rejects_each_invalid_required_component(field):
    auth = build_authorization_service()
    workspaces = WorkspaceRegistry()
    kwargs = _valid_kwargs(auth, workspaces)
    kwargs[field] = "nope"
    with pytest.raises(ProjectServiceError):
        ProjectService(**kwargs)  # type: ignore[arg-type]


@pytest.mark.parametrize("field", ["observability", "events"])
def test_service_rejects_each_invalid_optional_component(field):
    auth = build_authorization_service()
    workspaces = WorkspaceRegistry()
    kwargs = _valid_kwargs(auth, workspaces)
    kwargs[field] = "nope"
    with pytest.raises(ProjectServiceError):
        ProjectService(**kwargs)  # type: ignore[arg-type]


def test_component_property_getters():
    auth, _, service = _fixture()
    assert service.registry is not None
    assert service.associations is not None
    assert service.authorization is auth
    assert service.workspaces is not None
    assert service.health is not None
    assert service.observability is None
    assert service.access_evaluation_count == 0


# --------------------------------------------------------------------------- #
# Creation                                                                     #
# --------------------------------------------------------------------------- #


def test_create_project_records_owner_and_emits_event():
    events = bootstrap_platform().events
    auth, workspaces, service = _fixture(events=events)
    ws = _workspace(workspaces, tenant="acme")
    session = _session(auth, Role.DEVELOPER, subject="dev@x", tenant="acme")
    project = service.create_project(session.session_id, "alpha", "Alpha", ws.workspace_id, now=1)
    assert project.slug == "alpha"
    assert project.owner_subject == "dev@x"
    assert project.workspace_id == ws.workspace_id
    assert project.tenant == "acme"
    assert len(events.events_of(PROJECT_CREATED_EVENT)) == 1


def test_create_project_denied_without_create_grant():
    auth, workspaces, service = _fixture()
    ws = _workspace(workspaces)
    session = _session(auth, Role.OPERATOR)  # READ only
    with pytest.raises(ProjectAccessError):
        service.create_project(session.session_id, "alpha", "Alpha", ws.workspace_id, now=1)


def test_create_project_denied_cross_tenant():
    auth, workspaces, service = _fixture()
    ws = _workspace(workspaces, tenant="beta")
    session = _session(auth, Role.DEVELOPER, subject="dev@x", tenant="acme")
    with pytest.raises(ProjectAccessError):
        service.create_project(session.session_id, "alpha", "Alpha", ws.workspace_id, now=1)


def test_create_project_denied_when_workspace_not_active():
    auth, workspaces, service = _fixture()
    ws = _workspace(workspaces)
    workspaces.transition(ws.workspace_id, WorkspaceStatus.SUSPENDED, tick=0)
    session = _session(auth, Role.DEVELOPER, subject="dev@x")
    with pytest.raises(ProjectAccessError):
        service.create_project(session.session_id, "alpha", "Alpha", ws.workspace_id, now=1)


def test_create_project_unknown_workspace_is_fail_closed():
    auth, _, service = _fixture()
    session = _session(auth, Role.DEVELOPER, subject="dev@x")
    with pytest.raises(WorkspaceRegistryError):
        service.create_project(session.session_id, "alpha", "Alpha", "UCOS-WSPC-missing", now=1)


# --------------------------------------------------------------------------- #
# Access evaluation (identity ∧ isolation ∧ owner-scoping)                     #
# --------------------------------------------------------------------------- #


def _owned_project(auth, workspaces, service, *, subject="dev@x", tenant=None):
    ws = _workspace(workspaces, tenant=tenant)
    session = _session(auth, Role.DEVELOPER, subject=subject, tenant=tenant)
    project = service.create_project(session.session_id, "alpha", "Alpha", ws.workspace_id, now=1)
    return session, project


def test_access_granted_for_owner_inspect():
    auth, workspaces, service = _fixture()
    session, project = _owned_project(auth, workspaces, service)
    access = service.evaluate_access(
        session.session_id, project.project_id, ProjectAction.INSPECT, now=2
    )
    assert access.granted is True
    assert access.reason == "granted"
    assert access.is_owner is True
    assert access.to_dict()["access_id"].startswith("UCOS-PACC-")
    assert service.access_evaluation_count == 1


def test_access_granted_mutating_for_owner():
    auth, workspaces, service = _fixture()
    session, project = _owned_project(auth, workspaces, service)
    access = service.evaluate_access(
        session.session_id, project.project_id, ProjectAction.ADD_ASSOCIATION, now=2
    )
    assert access.granted is True


def test_access_granted_mutating_for_administrator_without_ownership():
    auth, workspaces, service = _fixture()
    _, project = _owned_project(auth, workspaces, service)
    admin = _session(auth, Role.PLATFORM_ADMINISTRATOR, subject="admin@x")
    access = service.evaluate_access(
        admin.session_id, project.project_id, ProjectAction.TRANSITION_LIFECYCLE, now=2
    )
    assert access.granted is True
    assert access.is_owner is False


def test_access_denied_when_authorization_refuses():
    auth, workspaces, service = _fixture()
    _, project = _owned_project(auth, workspaces, service)
    op = _session(auth, Role.OPERATOR, subject="op@x")  # no CREATE
    access = service.evaluate_access(
        op.session_id, project.project_id, ProjectAction.ADD_ASSOCIATION, now=2
    )
    assert access.granted is False
    assert access.reason == "no-grant"


def test_access_denied_cross_tenant_isolation():
    auth, workspaces, service = _fixture()
    _, project = _owned_project(auth, workspaces, service, subject="dev@x", tenant="beta")
    intruder = _session(auth, Role.DEVELOPER, subject="dev2@x", tenant="acme")
    access = service.evaluate_access(
        intruder.session_id, project.project_id, ProjectAction.INSPECT, now=2
    )
    assert access.granted is False
    assert access.reason == "tenant-isolation-violation"


def test_access_denied_not_an_owner_for_mutation():
    auth, workspaces, service = _fixture()
    _, project = _owned_project(auth, workspaces, service, subject="dev@x")
    other = _session(auth, Role.DEVELOPER, subject="other@x")  # has CREATE, not owner
    access = service.evaluate_access(
        other.session_id, project.project_id, ProjectAction.ADD_ASSOCIATION, now=2
    )
    assert access.granted is False
    assert access.reason == "not-an-owner"


def test_access_denied_mutation_on_archived_project():
    auth, workspaces, service = _fixture()
    session, project = _owned_project(auth, workspaces, service)
    service.transition(session.session_id, project.project_id, ProjectStatus.ARCHIVED, now=2)
    access = service.evaluate_access(
        session.session_id, project.project_id, ProjectAction.ADD_ASSOCIATION, now=3
    )
    assert access.granted is False
    assert access.reason == "project-archived"


def test_evaluate_access_rejects_bad_action():
    auth, workspaces, service = _fixture()
    session, project = _owned_project(auth, workspaces, service)
    with pytest.raises(ProjectServiceError):
        service.evaluate_access(session.session_id, project.project_id, "inspect", now=2)  # type: ignore[arg-type]


def test_evaluate_access_unknown_project_is_fail_closed():
    auth, _, service = _fixture()
    session = _session(auth, Role.DEVELOPER)
    with pytest.raises(Exception):  # noqa: B017 - registry error
        service.evaluate_access(
            session.session_id, "UCOS-PROJ-missing", ProjectAction.INSPECT, now=1
        )


def test_access_evaluation_is_emitted_as_governed_action():
    events = bootstrap_platform().events
    auth, workspaces, service = _fixture(events=events)
    session, project = _owned_project(auth, workspaces, service)
    service.evaluate_access(session.session_id, project.project_id, ProjectAction.INSPECT, now=2)
    assert len(events.events_of(PROJECT_ACCESS_EVENT)) == 1


# --------------------------------------------------------------------------- #
# Selection / context / discovery                                              #
# --------------------------------------------------------------------------- #


def test_select_project_returns_runtime_context():
    auth, workspaces, service = _fixture()
    session, project = _owned_project(auth, workspaces, service)
    ctx = service.select_project(session.session_id, project.project_id, now=2)
    assert ctx.project_id == project.project_id
    assert ctx.is_owner is True
    assert ctx.is_active is True


def test_select_project_denied_cross_tenant():
    auth, workspaces, service = _fixture()
    _, project = _owned_project(auth, workspaces, service, subject="dev@x", tenant="beta")
    intruder = _session(auth, Role.DEVELOPER, subject="x@x", tenant="acme")
    with pytest.raises(ProjectAccessError):
        service.select_project(intruder.session_id, project.project_id, now=2)


def test_resolve_reads_by_slug():
    auth, workspaces, service = _fixture()
    session, project = _owned_project(auth, workspaces, service)
    assert service.resolve("alpha", project.workspace_id).project_id == project.project_id


def test_discover_returns_authorized_isolated_projects():
    auth, workspaces, service = _fixture()
    admin = _session(auth, Role.PLATFORM_ADMINISTRATOR, subject="admin@x")
    ws_a = _workspace(workspaces, tenant="acme", slug="acme-ws")
    ws_b = _workspace(workspaces, tenant="beta", slug="beta-ws")
    service.create_project(admin.session_id, "acme-proj", "n", ws_a.workspace_id, now=1)
    service.create_project(admin.session_id, "beta-proj", "n", ws_b.workspace_id, now=1)
    dev = _session(auth, Role.DEVELOPER, subject="dev@x", tenant="acme")
    slugs = {p.slug for p in service.discover(dev.session_id, now=2)}
    assert "acme-proj" in slugs
    assert "beta-proj" not in slugs  # cross-tenant filtered


def test_discover_returns_empty_for_invalid_session():
    _, _, service = _fixture()
    assert service.discover("UCOS-SESS-missing", now=1) == ()


def test_discover_returns_empty_when_authorization_refused():
    auth, _, service = _fixture()
    session = _session(auth, Role.INTEGRATOR, subject="i@x", tenant="acme")
    assert service.discover(session.session_id, now=1, tenant=None) == ()


# --------------------------------------------------------------------------- #
# Lifecycle / associations                                                     #
# --------------------------------------------------------------------------- #


def test_owner_transitions_lifecycle_with_event():
    events = bootstrap_platform().events
    auth, workspaces, service = _fixture(events=events)
    session, project = _owned_project(auth, workspaces, service)
    updated = service.transition(
        session.session_id, project.project_id, ProjectStatus.COMPLETED, now=2
    )
    assert updated.status is ProjectStatus.COMPLETED
    assert len(events.events_of(PROJECT_LIFECYCLE_EVENT)) == 1


def test_transition_denied_for_non_owner():
    auth, workspaces, service = _fixture()
    _, project = _owned_project(auth, workspaces, service, subject="dev@x")
    other = _session(auth, Role.DEVELOPER, subject="other@x")
    with pytest.raises(ProjectAccessError):
        service.transition(other.session_id, project.project_id, ProjectStatus.ARCHIVED, now=2)


def test_add_and_remove_association_with_events():
    events = bootstrap_platform().events
    auth, workspaces, service = _fixture(events=events)
    session, project = _owned_project(auth, workspaces, service)
    assoc = service.add_association(
        session.session_id, project.project_id, AssociationKind.BLUEPRINT, "BP-1", now=2
    )
    assert assoc.ref_id == "BP-1"
    removed = service.remove_association(
        session.session_id, project.project_id, AssociationKind.BLUEPRINT, "BP-1", now=3
    )
    assert removed.ref_id == "BP-1"
    assert len(events.events_of(PROJECT_ASSOCIATION_ADDED_EVENT)) == 1
    assert len(events.events_of(PROJECT_ASSOCIATION_REMOVED_EVENT)) == 1


def test_add_association_denied_for_non_owner():
    auth, workspaces, service = _fixture()
    _, project = _owned_project(auth, workspaces, service, subject="dev@x")
    other = _session(auth, Role.DEVELOPER, subject="other@x")
    with pytest.raises(ProjectAccessError):
        service.add_association(
            other.session_id, project.project_id, AssociationKind.REQUEST, "REQ-1", now=2
        )


def test_remove_association_denied_for_non_owner():
    auth, workspaces, service = _fixture()
    session, project = _owned_project(auth, workspaces, service, subject="dev@x")
    service.add_association(
        session.session_id, project.project_id, AssociationKind.REQUEST, "REQ-1", now=2
    )
    other = _session(auth, Role.DEVELOPER, subject="other@x")
    with pytest.raises(ProjectAccessError):
        service.remove_association(
            other.session_id, project.project_id, AssociationKind.REQUEST, "REQ-1", now=3
        )


def test_add_association_on_archived_project_denied():
    auth, workspaces, service = _fixture()
    session, project = _owned_project(auth, workspaces, service)
    service.transition(session.session_id, project.project_id, ProjectStatus.ARCHIVED, now=2)
    with pytest.raises(ProjectAccessError):
        service.add_association(
            session.session_id, project.project_id, AssociationKind.BLUEPRINT, "BP-1", now=3
        )


def test_duplicate_association_is_fail_closed():
    auth, workspaces, service = _fixture()
    session, project = _owned_project(auth, workspaces, service)
    service.add_association(
        session.session_id, project.project_id, AssociationKind.BLUEPRINT, "BP-1", now=2
    )
    with pytest.raises(ProjectAssociationError):
        service.add_association(
            session.session_id, project.project_id, AssociationKind.BLUEPRINT, "BP-1", now=3
        )


# --------------------------------------------------------------------------- #
# Status / search / health / evidence                                          #
# --------------------------------------------------------------------------- #


def test_status_of_reflects_associations():
    auth, workspaces, service = _fixture()
    session, project = _owned_project(auth, workspaces, service)
    assert service.status_of(project.project_id).posture.value == "empty"
    service.add_association(
        session.session_id, project.project_id, AssociationKind.BLUEPRINT, "BP-1", now=2
    )
    status = service.status_of(project.project_id)
    assert status.posture.value == "populated"
    assert status.association_total == 1


def test_search_delegates_to_project_search():
    auth, workspaces, service = _fixture()
    session, _ = _owned_project(auth, workspaces, service)
    response = service.search(session.session_id, "alpha", now=2)
    assert response.authorized is True
    assert {h.project.slug for h in response.results} == {"alpha"}


def test_health_report_uses_observability_model():
    _, _, service = _fixture()
    report = service.health_report()
    assert report["healthy"] is True


def test_evidence_is_deterministic_and_reports_counts():
    def run() -> str:
        auth, workspaces, service = _fixture()
        session, project = _owned_project(auth, workspaces, service)
        service.add_association(
            session.session_id, project.project_id, AssociationKind.BLUEPRINT, "BP-1", now=2
        )
        return service.evidence().fingerprint()

    assert run() == run()
    auth, workspaces, service = _fixture()
    session, project = _owned_project(auth, workspaces, service)
    evidence = service.evidence()
    assert evidence.project_count == 1
    assert evidence.association_count == 0
    assert evidence.evidence_id.startswith("UCOS-PEVT-")
    assert evidence.to_dict()["health_status"] in {"healthy", "degraded", "unhealthy"}


def test_to_dict_summary_reports_observability_binding():
    events = bootstrap_platform().events
    observability = build_observability_service(events=events)
    auth, workspaces, service = _fixture(events=events, observability=observability)
    _owned_project(auth, workspaces, service)
    summary = service.to_dict()
    assert summary["project_count"] == 1
    assert summary["observability_bound"] is True
    assert service.observability is observability
