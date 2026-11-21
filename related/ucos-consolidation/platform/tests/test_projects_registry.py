"""EC2-TASK-000091 — Project registry tests.

Covers the append-only, content-addressed project registry: idempotent-safe creation,
fail-closed duplicate registration, resolution by id and by slug/workspace, existence
checks, workspace- and tenant-scoped discovery, immutable lifecycle transitions with
an append-only event log, metadata updates, and the deterministic fingerprint.
"""

from __future__ import annotations

from platform.projects.contracts import Project, ProjectStatus
from platform.projects.errors import ProjectRegistryError
from platform.projects.metadata import ProjectMetadata
from platform.projects.registry import ProjectRegistry

import pytest


def _reg_with(*specs):
    reg = ProjectRegistry()
    for slug, workspace_id, tenant in specs:
        reg.create(slug, slug.title(), workspace_id, "dev@x", tenant=tenant)
    return reg


def test_create_and_resolve():
    reg = ProjectRegistry()
    project = reg.create("alpha", "Alpha", "UCOS-WSPC-1", "dev@x", tenant="acme")
    assert project.status is ProjectStatus.ACTIVE
    assert reg.get(project.project_id) is project
    assert reg.resolve("alpha", "UCOS-WSPC-1").project_id == project.project_id
    assert project.project_id in reg
    assert len(reg) == 1


def test_register_rejects_non_project_and_duplicate():
    reg = ProjectRegistry()
    with pytest.raises(ProjectRegistryError):
        reg.register("nope")  # type: ignore[arg-type]
    reg.create("alpha", "Alpha", "UCOS-WSPC-1", "dev@x")
    with pytest.raises(ProjectRegistryError):
        reg.register(Project.create("alpha", "Alpha", "UCOS-WSPC-1", "other@x"))


def test_get_and_resolve_fail_closed():
    reg = ProjectRegistry()
    with pytest.raises(ProjectRegistryError):
        reg.get("UCOS-PROJ-missing")
    with pytest.raises(ProjectRegistryError):
        reg.resolve("ghost", "UCOS-WSPC-1")


def test_exists():
    reg = _reg_with(("alpha", "UCOS-WSPC-1", None))
    assert reg.exists("alpha", "UCOS-WSPC-1") is True
    assert reg.exists("alpha", "UCOS-WSPC-2") is False


def test_ids_and_all_stable_order():
    reg = _reg_with(
        ("alpha", "UCOS-WSPC-1", None),
        ("beta", "UCOS-WSPC-1", None),
    )
    assert list(reg.ids) == sorted(reg.ids)
    assert len(reg.all()) == 2


def test_discover_scopes_by_workspace_and_tenant():
    reg = _reg_with(
        ("alpha", "UCOS-WSPC-1", "acme"),
        ("beta", "UCOS-WSPC-2", "beta"),
        ("gamma", "UCOS-WSPC-1", None),
    )
    # all
    assert len(reg.discover()) == 3
    # by workspace
    ws1 = {p.slug for p in reg.discover(workspace_id="UCOS-WSPC-1")}
    assert ws1 == {"alpha", "gamma"}
    # by tenant (acme + untenanted global)
    acme = {p.slug for p in reg.discover(tenant="acme")}
    assert acme == {"alpha", "gamma"}
    # by both
    both = {p.slug for p in reg.discover(workspace_id="UCOS-WSPC-1", tenant="acme")}
    assert both == {"alpha", "gamma"}


def test_transition_records_append_only_event():
    reg = ProjectRegistry()
    project = reg.create("alpha", "Alpha", "UCOS-WSPC-1", "dev@x")
    updated = reg.transition(project.project_id, ProjectStatus.COMPLETED, tick=5)
    assert updated.status is ProjectStatus.COMPLETED
    assert reg.get(project.project_id).status is ProjectStatus.COMPLETED
    assert len(reg.events) == 1
    event = reg.events[0]
    assert event.from_status is ProjectStatus.ACTIVE
    assert event.to_status is ProjectStatus.COMPLETED
    assert event.tick == 5


def test_transition_illegal_is_fail_closed():
    reg = ProjectRegistry()
    project = reg.create("alpha", "Alpha", "UCOS-WSPC-1", "dev@x")
    reg.transition(project.project_id, ProjectStatus.ARCHIVED, tick=1)
    with pytest.raises(Exception):  # noqa: B017 - lifecycle error out of terminal
        reg.transition(project.project_id, ProjectStatus.ACTIVE, tick=2)


def test_update_metadata_preserves_id_and_status():
    reg = ProjectRegistry()
    project = reg.create("alpha", "Alpha", "UCOS-WSPC-1", "dev@x")
    md = ProjectMetadata.create(description="d", labels=["x"])
    updated = reg.update_metadata(project.project_id, md)
    assert updated.project_id == project.project_id
    assert updated.status is project.status
    assert updated.metadata.description == "d"


def test_fingerprint_is_deterministic():
    def build() -> str:
        reg = _reg_with(
            ("alpha", "UCOS-WSPC-1", "acme"),
            ("beta", "UCOS-WSPC-1", "acme"),
        )
        return reg.fingerprint()

    assert build() == build()
