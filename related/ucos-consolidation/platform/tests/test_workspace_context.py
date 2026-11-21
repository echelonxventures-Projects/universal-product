"""EC2-TASK-000086 — Workspace context tests.

Covers the immutable, content-addressed runtime context produced on a resolved,
authorized, isolation-cleared workspace selection: deterministic ``context_id``,
fail-closed input validation, the ``is_active`` binding, serialization, and a
reproducible fingerprint (P5). The context grants nothing on its own and holds no
secret material (SEC-04).
"""

from __future__ import annotations

from platform.foundation.identity import Principal, Role
from platform.workspace.context import WorkspaceContext
from platform.workspace.contracts import MemberRole, Workspace, WorkspaceStatus
from platform.workspace.errors import WorkspaceServiceError

import pytest


def _principal(subject: str = "u@x", tenant: str | None = "acme") -> Principal:
    return Principal.create(subject, [Role.DEVELOPER], tenant=tenant)


def _workspace(
    slug: str = "acme-core",
    tenant: str | None = "acme",
    status: WorkspaceStatus = WorkspaceStatus.ACTIVE,
) -> Workspace:
    ws = Workspace.create(slug, "Acme Core", "owner@x", tenant=tenant)
    return ws.with_status(status) if status is not WorkspaceStatus.ACTIVE else ws


def test_context_binds_who_where_and_role():
    ctx = WorkspaceContext.create(_workspace(), _principal(), member_role=MemberRole.OWNER)
    assert ctx.context_id.startswith("UCOS-WCTX-")
    assert ctx.workspace_slug == "acme-core"
    assert ctx.tenant == "acme"
    assert ctx.member_role is MemberRole.OWNER
    assert ctx.subject == "u@x"


def test_context_id_is_deterministic_for_identical_binding():
    a = WorkspaceContext.create(_workspace(), _principal(), member_role=MemberRole.MEMBER)
    b = WorkspaceContext.create(_workspace(), _principal(), member_role=MemberRole.MEMBER)
    assert a.context_id == b.context_id
    assert a.fingerprint() == b.fingerprint()


def test_context_id_varies_with_member_role():
    owner = WorkspaceContext.create(_workspace(), _principal(), member_role=MemberRole.OWNER)
    viewer = WorkspaceContext.create(_workspace(), _principal(), member_role=MemberRole.VIEWER)
    assert owner.context_id != viewer.context_id


def test_member_role_optional_defaults_to_none():
    ctx = WorkspaceContext.create(_workspace(), _principal())
    assert ctx.member_role is None
    assert ctx.to_dict()["member_role"] is None


def test_is_active_reflects_workspace_status():
    active = WorkspaceContext.create(_workspace(status=WorkspaceStatus.ACTIVE), _principal())
    suspended = WorkspaceContext.create(_workspace(status=WorkspaceStatus.SUSPENDED), _principal())
    assert active.is_active is True
    assert suspended.is_active is False


def test_to_dict_round_trips_every_field():
    ctx = WorkspaceContext.create(_workspace(), _principal(), member_role=MemberRole.OWNER)
    d = ctx.to_dict()
    assert d == {
        "context_id": ctx.context_id,
        "workspace_id": ctx.workspace_id,
        "workspace_slug": "acme-core",
        "workspace_status": "active",
        "principal_id": ctx.principal_id,
        "subject": "u@x",
        "tenant": "acme",
        "member_role": "owner",
    }


def test_global_workspace_context_has_no_tenant():
    ctx = WorkspaceContext.create(_workspace(tenant=None), _principal(tenant=None))
    assert ctx.tenant is None
    assert ctx.to_dict()["tenant"] is None


def test_bound_workspace_fingerprint_is_reproducible():
    # The context binds a content-addressed Workspace; its fingerprint is stable.
    ws = _workspace()
    assert ws.fingerprint() == _workspace().fingerprint()


def test_create_is_fail_closed_on_bad_inputs():
    with pytest.raises(WorkspaceServiceError):
        WorkspaceContext.create("nope", _principal())  # type: ignore[arg-type]
    with pytest.raises(WorkspaceServiceError):
        WorkspaceContext.create(_workspace(), "nope")  # type: ignore[arg-type]
    with pytest.raises(WorkspaceServiceError):
        WorkspaceContext.create(_workspace(), _principal(), member_role="owner")  # type: ignore[arg-type]
