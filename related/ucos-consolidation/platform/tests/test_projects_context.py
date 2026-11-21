"""EC2-TASK-000093 — Project context tests.

Covers the immutable, content-addressed project runtime context binding: deterministic
context id, ownership flag, active helper, fail-closed validation, and serialization.
"""

from __future__ import annotations

from platform.foundation.identity import Principal, Role
from platform.projects.context import ProjectContext
from platform.projects.contracts import Project, ProjectStatus
from platform.projects.errors import ProjectServiceError

import pytest


def _project(status: ProjectStatus = ProjectStatus.ACTIVE, tenant=None) -> Project:
    return Project.create("alpha", "Alpha", "UCOS-WSPC-1", "dev@x", tenant=tenant).with_status(
        status
    )


def _principal(subject="dev@x", tenant=None) -> Principal:
    return Principal.create(subject, [Role.DEVELOPER], tenant=tenant)


def test_context_is_content_addressed_and_deterministic():
    project = _project()
    principal = _principal()
    a = ProjectContext.create(project, principal, is_owner=True)
    b = ProjectContext.create(project, principal, is_owner=True)
    assert a.context_id == b.context_id
    assert a.context_id.startswith("UCOS-PCTX-")
    assert a.is_owner is True


def test_context_reports_active_and_binding():
    ctx = ProjectContext.create(_project(tenant="acme"), _principal(tenant="acme"))
    assert ctx.is_active is True
    assert ctx.workspace_id == "UCOS-WSPC-1"
    assert ctx.tenant == "acme"
    assert ctx.is_owner is False


def test_context_inactive_when_project_not_active():
    ctx = ProjectContext.create(_project(ProjectStatus.ARCHIVED), _principal())
    assert ctx.is_active is False


def test_context_validation():
    with pytest.raises(ProjectServiceError):
        ProjectContext.create("nope", _principal())  # type: ignore[arg-type]
    with pytest.raises(ProjectServiceError):
        ProjectContext.create(_project(), "nope")  # type: ignore[arg-type]
    with pytest.raises(ProjectServiceError):
        ProjectContext.create(_project(), _principal(), is_owner="yes")  # type: ignore[arg-type]


def test_context_to_dict_and_fingerprint():
    ctx = ProjectContext.create(_project(), _principal(), is_owner=True)
    d = ctx.to_dict()
    assert d["context_id"] == ctx.context_id
    assert d["is_owner"] is True
    assert ctx.fingerprint() == ctx.fingerprint()
