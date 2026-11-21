"""EC2-EPIC-005 — project governance validation tests.

Asserts the constitutional/governance invariants the mission mandates: no new authority
(the reused WORKSPACE_PROJECT_LIFECYCLE capability group, no new capability group, no
new Role/Permission), no duplication of the certified L7 authorization decision
(the service delegates and exposes no authorize verb), association-by-reference only
(no downstream blueprint/request/artifact runtime dependency), append-only record
discipline (no destructive registry operations), and authority neutrality.
"""

from __future__ import annotations

from pathlib import Path
from platform.foundation.identity import Permission as FoundationPermission
from platform.identity.contracts import CapabilityGroup as IdentityCapabilityGroup
from platform.projects.associations import AssociationRegistry
from platform.projects.contracts import PROJECT_GROUP, Permission
from platform.projects.registry import ProjectRegistry
from platform.projects.service import build_project_service
from platform.workspace.registration import WorkspaceRegistry

_PROJECTS_PKG = Path(__file__).resolve().parents[1] / "projects"

#: Verbs the project runtime must never expose (authority-neutral; delegates to L7).
_FORBIDDEN_OPERATIONS = (
    "authorize",
    "authorize_principal",
    "ratify",
    "enact",
    "grant",
    "govern",
    "override",
    "escalate",
    "deny",
    "permit",
)

#: Tokens that would evidence a forbidden downstream-runtime dependency (EPIC-006/007/009).
_FORBIDDEN_IMPORT_TOKENS = (
    "platform.blueprints",
    "platform.requests",
    "platform.artifacts",
    "platform.generation",
)


def _service():
    auth_ws = WorkspaceRegistry()
    from platform.identity.service import build_authorization_service

    auth = build_authorization_service()
    return build_project_service(authorization=auth, workspaces=auth_ws)


def test_reuses_the_existing_capability_group_no_new_group():
    assert PROJECT_GROUP is IdentityCapabilityGroup.WORKSPACE_PROJECT_LIFECYCLE


def test_defines_no_new_role_or_permission_vocabulary():
    # The project runtime reuses the certified Permission/CapabilityGroup vocabulary.
    assert Permission is FoundationPermission
    from platform.projects import contracts as contracts_module

    assert contracts_module.CapabilityGroup.__module__ == "platform.identity.contracts"


def test_service_exposes_no_authority_operation():
    service = _service()
    for verb in _FORBIDDEN_OPERATIONS:
        assert not hasattr(service, verb), f"project runtime must not expose '{verb}'"


def test_registry_exposes_no_destructive_mutation():
    reg = ProjectRegistry()
    for verb in ("delete", "remove", "drop", "clear", "pop", "truncate"):
        assert not hasattr(reg, verb)


def test_association_registry_is_append_only_with_scoped_removal_only():
    reg = AssociationRegistry()
    # It supports scoped remove(project, kind, ref) but no bulk destructive op.
    assert callable(reg.remove)
    for verb in ("clear", "drop", "truncate", "delete_all", "wipe"):
        assert not hasattr(reg, verb)


def test_no_downstream_runtime_dependency_in_source():
    # Association-by-reference: the runtime imports no blueprint/request/artifact runtime.
    for path in _PROJECTS_PKG.glob("*.py"):
        source = path.read_text(encoding="utf-8")
        for token in _FORBIDDEN_IMPORT_TOKENS:
            assert token not in source, f"{path.name} references forbidden downstream {token}"


def test_no_filesystem_write_or_server_in_source():
    # Deterministic in-memory model: no file writes / sockets / servers (workspace precedent).
    for path in _PROJECTS_PKG.glob("*.py"):
        source = path.read_text(encoding="utf-8")
        assert "open(" not in source
        assert "import socket" not in source
        assert "http.server" not in source
        assert ".write(" not in source


def test_no_secret_material_is_stored_in_records():
    reg = ProjectRegistry()
    project = reg.create("alpha", "Alpha", "UCOS-WSPC-1", "dev@x")
    serialized = str(project.to_dict())
    for token in ("password", "secret", "token", "apikey", "api_key", "private_key"):
        assert token not in serialized.lower()


def test_service_never_calls_authorize_decision_directly_for_reads(monkeypatch):
    # A pure resolve() read path must not invoke an authorization decision.
    from platform.identity.service import AuthorizationService, build_authorization_service

    auth = build_authorization_service()
    workspaces = WorkspaceRegistry()
    service = build_project_service(authorization=auth, workspaces=workspaces)
    project = service.registry.create("alpha", "Alpha", "UCOS-WSPC-1", "dev@x")

    def _boom(*args, **kwargs):  # pragma: no cover - must never be invoked
        raise AssertionError("resolve() must not invoke an authorization decision")

    monkeypatch.setattr(AuthorizationService, "authorize", _boom, raising=True)
    monkeypatch.setattr(AuthorizationService, "authorize_principal", _boom, raising=True)
    assert service.resolve("alpha", "UCOS-WSPC-1").project_id == project.project_id
    assert service.status_of(project.project_id).project_id == project.project_id
