"""EC2-TASK-000102 — Blueprint registry tests (EC2-EPIC-006)."""

from __future__ import annotations

from platform.blueprints.contracts import Blueprint, BlueprintFamily, BlueprintStatus
from platform.blueprints.errors import BlueprintRegistryError
from platform.blueprints.metadata import BlueprintMetadata
from platform.blueprints.registry import BlueprintRegistry

import pytest


def _reg_with_one(**kw):
    reg = BlueprintRegistry()
    bp = reg.create("bp-1", "BP One", "UCOS-WSPC-1", "arch@x", BlueprintFamily.DATA, **kw)
    return reg, bp


def test_create_registers_draft_and_resolves():
    reg, bp = _reg_with_one(tenant="acme")
    assert bp.status is BlueprintStatus.DRAFT
    assert bp.blueprint_id in reg
    assert len(reg) == 1
    assert reg.get(bp.blueprint_id) is bp
    assert reg.resolve("bp-1", "UCOS-WSPC-1").blueprint_id == bp.blueprint_id
    assert reg.exists("bp-1", "UCOS-WSPC-1") is True
    assert reg.exists("nope", "UCOS-WSPC-1") is False
    assert reg.ids == (bp.blueprint_id,)
    assert reg.all() == (bp,)


def test_register_rejects_non_blueprint_and_duplicate():
    reg = BlueprintRegistry()
    with pytest.raises(BlueprintRegistryError):
        reg.register("nope")  # type: ignore[arg-type]
    bp = Blueprint.create("bp", "n", "w", "o", BlueprintFamily.DATA)
    reg.register(bp)
    with pytest.raises(BlueprintRegistryError):
        reg.register(bp)


def test_get_and_resolve_fail_closed():
    reg = BlueprintRegistry()
    with pytest.raises(BlueprintRegistryError):
        reg.get("UCOS-BLPR-missing")
    with pytest.raises(BlueprintRegistryError):
        reg.resolve("nope", "w")


def test_discover_scopes_by_workspace_tenant_family_status():
    reg = BlueprintRegistry()
    reg.create("a", "A", "ws1", "o", BlueprintFamily.DATA, tenant="acme")
    reg.create("b", "B", "ws2", "o", BlueprintFamily.EVENT, tenant="beta")
    reg.create("c", "C", "ws1", "o", BlueprintFamily.DATA)  # untenanted/global
    assert {b.slug for b in reg.discover(workspace_id="ws1")} == {"a", "c"}
    # acme tenant plus untenanted/global
    assert {b.slug for b in reg.discover(tenant="acme")} == {"a", "c"}
    assert {b.slug for b in reg.discover(family=BlueprintFamily.EVENT)} == {"b"}
    assert {b.slug for b in reg.discover(status=BlueprintStatus.DRAFT)} == {"a", "b", "c"}


def test_transition_records_event_and_metadata_update():
    reg, bp = _reg_with_one()
    updated = reg.transition(bp.blueprint_id, BlueprintStatus.VALIDATED, tick=5)
    assert updated.status is BlueprintStatus.VALIDATED
    assert len(reg.events) == 1
    assert reg.events[0].to_status is BlueprintStatus.VALIDATED
    md = BlueprintMetadata.create(description="d")
    remeta = reg.update_metadata(bp.blueprint_id, md)
    assert remeta.metadata is md
    assert remeta.status is BlueprintStatus.VALIDATED


def test_versioning_through_registry():
    reg, bp = _reg_with_one()
    assert reg.version_count(bp.blueprint_id) == 0
    assert reg.lineage_of(bp.blueprint_id) == ()
    v1 = reg.add_version(bp.blueprint_id, "h1")
    v2 = reg.add_version(bp.blueprint_id, "h2")
    assert v1.revision == 1
    assert v2.revision == 2
    assert reg.version_count(bp.blueprint_id) == 2
    assert reg.current_version(bp.blueprint_id).version_id == v2.version_id


def test_versioning_fail_closed_on_absent_blueprint():
    reg = BlueprintRegistry()
    with pytest.raises(BlueprintRegistryError):
        reg.add_version("UCOS-BLPR-missing", "h1")
    with pytest.raises(BlueprintRegistryError):
        reg.current_version("UCOS-BLPR-missing")


def test_registry_fingerprint_is_deterministic():
    def build() -> str:
        reg = BlueprintRegistry()
        reg.create("a", "A", "ws1", "o", BlueprintFamily.DATA)
        reg.add_version(reg.resolve("a", "ws1").blueprint_id, "h1")
        return reg.fingerprint()

    assert build() == build()
