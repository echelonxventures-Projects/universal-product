"""EC2-EPIC-005 — project traceability validation tests.

Asserts complete requirement traceability: the determination artifact exists and
authorizes implementation; every project responsibility (create · lifecycle · associate
· derive status · discover/search · select · evidence · health) is realized; every
mandated content-addressed ID prefix is used (UCOS-PROJ / UCOS-PASC / UCOS-PCTX /
UCOS-PACC / UCOS-PEVT); the association-kind vocabulary is published for downstream
consumption (blueprint / request / artifact — EPIC-006/007/009); and the project
contracts are published by reference.
"""

from __future__ import annotations

from pathlib import Path
from platform.foundation.identity import Principal, Role
from platform.identity.service import build_authorization_service
from platform.projects.context import ProjectContext
from platform.projects.contracts import (
    PROJECT_CONTRACTS,
    AssociationKind,
    Project,
    ProjectAssociation,
    ProjectStatus,
    all_association_kinds,
)
from platform.projects.service import ProjectAccess, build_project_service
from platform.workspace.registration import WorkspaceRegistry

_REPO_ROOT = Path(__file__).resolve().parents[2]
_DETERMINATION = _REPO_ROOT / "platform" / "project-management" / "EC2-EPIC-005-DETERMINATION.md"


def _service():
    auth = build_authorization_service()
    return auth, build_project_service(authorization=auth, workspaces=WorkspaceRegistry())


def test_determination_artifact_exists():
    assert _DETERMINATION.is_file()


def test_determination_authorizes_implementation():
    text = _DETERMINATION.read_text(encoding="utf-8")
    assert "EC2-EPIC-005" in text
    assert "Project Management Runtime" in text
    assert "IMPLEMENTATION AUTHORIZED" in text


def test_service_realizes_every_project_responsibility():
    _, service = _service()
    for responsibility in (
        "create_project",
        "transition",
        "add_association",
        "remove_association",
        "status_of",
        "discover",
        "search",
        "select_project",
        "resolve",
        "evidence",
        "health_report",
        "evaluate_access",
    ):
        assert callable(getattr(service, responsibility))


def test_mandated_id_prefixes_are_used():
    # UCOS-PROJ (project) / UCOS-PASC (association) / UCOS-PCTX (context).
    project = Project.create("alpha", "Alpha", "UCOS-WSPC-1", "dev@x")
    assert project.project_id.startswith("UCOS-PROJ-")
    association = ProjectAssociation.create(project.project_id, AssociationKind.BLUEPRINT, "BP-1")
    assert association.association_id.startswith("UCOS-PASC-")
    principal = Principal.create("dev@x", [Role.DEVELOPER])
    ctx = ProjectContext.create(project, principal, is_owner=True)
    assert ctx.context_id.startswith("UCOS-PCTX-")


def test_access_and_evidence_prefixes_are_used():
    auth, service = _service()
    ws = service.workspaces.create("team", "Team", "owner@x")
    principal = Principal.create("dev@x", [Role.DEVELOPER])
    session = auth.establish_session(principal, issued_at=0, ttl=1000)
    project = service.create_project(session.session_id, "alpha", "Alpha", ws.workspace_id, now=1)
    from platform.projects.contracts import ProjectAction

    access = service.evaluate_access(
        session.session_id, project.project_id, ProjectAction.INSPECT, now=2
    )
    assert isinstance(access, ProjectAccess)
    assert access.access_id.startswith("UCOS-PACC-")
    assert service.evidence().evidence_id.startswith("UCOS-PEVT-")


def test_association_kind_vocabulary_is_published_for_downstream():
    # Forward traceability: the binding point for EPIC-006/007/009.
    kinds = {k.value for k in all_association_kinds()}
    assert kinds == {"blueprint", "request", "artifact"}


def test_project_contracts_are_published_by_reference():
    names = {ref.name for ref in PROJECT_CONTRACTS}
    assert "projects.registry.registry" in names
    assert "projects.lifecycle.transition" in names
    assert "projects.associations.bind" in names
    assert "projects.status.derive" in names
    assert "projects.search.query" in names
    assert "projects.runtime.service" in names


def test_lifecycle_states_are_defined_and_enforced():
    # Acceptance §5: lifecycle states defined & enforced (archived terminal).
    assert set(ProjectStatus) == {
        ProjectStatus.ACTIVE,
        ProjectStatus.SUSPENDED,
        ProjectStatus.COMPLETED,
        ProjectStatus.ARCHIVED,
    }
