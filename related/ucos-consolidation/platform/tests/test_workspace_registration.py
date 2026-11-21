"""EC2-TASK-000084 — Workspace registry tests.

Covers deterministic creation, registration, resolution, discovery, lifecycle
application (append-only events), metadata update, and fail-closed handling of
duplicates/absent workspaces and illegal transitions.
"""

from __future__ import annotations

from platform.workspace.contracts import WorkspaceStatus
from platform.workspace.errors import WorkspaceLifecycleError, WorkspaceRegistryError
from platform.workspace.metadata import WorkspaceMetadata
from platform.workspace.registration import WorkspaceRegistry

import pytest


def _registry() -> WorkspaceRegistry:
    return WorkspaceRegistry()


def test_create_and_get():
    reg = _registry()
    ws = reg.create("acme-core", "Acme Core", "owner@x", tenant="acme")
    assert reg.get(ws.workspace_id) is ws
    assert ws.workspace_id in reg
    assert len(reg) == 1


def test_duplicate_create_is_fail_closed():
    reg = _registry()
    reg.create("s", "n", "o", tenant="t")
    with pytest.raises(WorkspaceRegistryError):
        reg.create("s", "different", "o2", tenant="t")


def test_register_requires_workspace():
    with pytest.raises(WorkspaceRegistryError):
        _registry().register("nope")  # type: ignore[arg-type]


def test_resolve_by_slug_and_tenant():
    reg = _registry()
    ws = reg.create("s", "n", "o", tenant="t")
    assert reg.resolve("s", "t").workspace_id == ws.workspace_id
    assert reg.exists("s", "t")
    assert not reg.exists("s", None)
    with pytest.raises(WorkspaceRegistryError):
        reg.resolve("missing", "t")


def test_get_absent_is_fail_closed():
    with pytest.raises(WorkspaceRegistryError):
        _registry().get("UCOS-WSPC-missing")


def test_discover_scopes_by_tenant_and_global():
    reg = _registry()
    reg.create("g", "global", "o")  # untenanted
    reg.create("a", "acme", "o", tenant="acme")
    reg.create("b", "beta", "o", tenant="beta")
    assert len(reg.discover(None)) == 3  # all
    acme = reg.discover("acme")
    slugs = {w.slug for w in acme}
    assert slugs == {"g", "a"}  # tenant + global, never beta


def test_transition_applies_and_logs_event():
    reg = _registry()
    ws = reg.create("s", "n", "o")
    updated = reg.transition(ws.workspace_id, WorkspaceStatus.SUSPENDED, tick=1)
    assert updated.status is WorkspaceStatus.SUSPENDED
    assert reg.get(ws.workspace_id).status is WorkspaceStatus.SUSPENDED
    events = reg.events
    assert len(events) == 1
    assert events[0].to_dict()["to_status"] == "suspended"


def test_illegal_transition_is_fail_closed():
    reg = _registry()
    ws = reg.create("s", "n", "o")
    reg.transition(ws.workspace_id, WorkspaceStatus.ARCHIVED, tick=1)
    with pytest.raises(WorkspaceLifecycleError):
        reg.transition(ws.workspace_id, WorkspaceStatus.ACTIVE, tick=2)


def test_update_metadata_preserves_id_and_status():
    reg = _registry()
    ws = reg.create("s", "n", "o")
    reg.transition(ws.workspace_id, WorkspaceStatus.SUSPENDED, tick=1)
    md = WorkspaceMetadata.create(description="updated")
    updated = reg.update_metadata(ws.workspace_id, md)
    assert updated.metadata.description == "updated"
    assert updated.status is WorkspaceStatus.SUSPENDED
    assert updated.workspace_id == ws.workspace_id


def test_registry_is_deterministic():
    def build() -> str:
        reg = _registry()
        reg.create("a", "A", "o", tenant="t")
        reg.create("b", "B", "o", tenant="t")
        return reg.fingerprint()

    assert build() == build()
    assert _registry().ids == ()
