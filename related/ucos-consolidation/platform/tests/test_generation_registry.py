"""EC2-TASK-000111 — Generation request registry tests (EC2-EPIC-007).

Covers the append-only registry substrate: create/register/resolve/discover/transition/
metadata update, fail-closed duplicate + absent handling, the per-status census, the
append-only lifecycle event log, and per-request event reconstruction (§6 persistence).
"""

from __future__ import annotations

from platform.blueprints.contracts import BlueprintFamily
from platform.generation.contracts import GenerationRequest, RequestStatus
from platform.generation.errors import RequestLifecycleError, RequestRegistryError
from platform.generation.metadata import RequestMetadata
from platform.generation.registry import GenerationRequestRegistry

import pytest


def _reg():
    return GenerationRequestRegistry()


def _create(reg, *, slug="req-1", tick=1, tenant=None, project=None, family=BlueprintFamily.DATA):
    return reg.create(
        slug,
        "UCOS-BLPR-abc",
        "UCOS-WSPC-1",
        "arch@x",
        family,
        submitted_tick=tick,
        project_id=project,
        tenant=tenant,
    )


def test_create_and_get():
    reg = _reg()
    req = _create(reg)
    assert req.status is RequestStatus.SUBMITTED
    assert reg.get(req.request_id) is req
    assert req.request_id in reg
    assert len(reg) == 1


def test_register_rejects_non_request_and_duplicate():
    reg = _reg()
    with pytest.raises(RequestRegistryError):
        reg.register("nope")  # type: ignore[arg-type]
    req = _create(reg)
    with pytest.raises(RequestRegistryError):
        reg.register(req)


def test_get_absent_fail_closed():
    with pytest.raises(RequestRegistryError):
        _reg().get("UCOS-GREQ-missing")


def test_exists_probe():
    reg = _reg()
    _create(reg, slug="req-x", tick=7)
    assert reg.exists("req-x", "UCOS-WSPC-1", "UCOS-BLPR-abc", 7) is True
    assert reg.exists("req-x", "UCOS-WSPC-1", "UCOS-BLPR-abc", 8) is False


def test_ids_and_all_stable_order():
    reg = _reg()
    a = _create(reg, slug="a", tick=1)
    b = _create(reg, slug="b", tick=2)
    assert reg.ids == tuple(sorted({a.request_id, b.request_id}))
    assert {r.request_id for r in reg.all()} == {a.request_id, b.request_id}


def test_discover_scopes():
    reg = _reg()
    r1 = _create(reg, slug="a", tick=1, tenant="acme", project="UCOS-PROJ-1")
    _create(reg, slug="b", tick=2, tenant="beta")
    glob = _create(reg, slug="c", tick=3, tenant=None)
    # tenant scope returns tenant + global
    tenant_view = reg.discover(tenant="acme")
    ids = {r.request_id for r in tenant_view}
    assert r1.request_id in ids and glob.request_id in ids
    # project scope
    assert {r.request_id for r in reg.discover(project_id="UCOS-PROJ-1")} == {r1.request_id}
    # workspace scope
    assert len(reg.discover(workspace_id="UCOS-WSPC-1")) == 3
    assert reg.discover(workspace_id="UCOS-WSPC-none") == ()
    # blueprint_ref scope
    assert len(reg.discover(blueprint_ref="UCOS-BLPR-abc")) == 3
    # family + status scope
    assert len(reg.discover(family=BlueprintFamily.DATA)) == 3
    assert len(reg.discover(status=RequestStatus.SUBMITTED)) == 3


def test_transition_records_event_and_reconstruction():
    reg = _reg()
    req = _create(reg)
    reg.transition(req.request_id, RequestStatus.VALIDATING, tick=2)
    reg.transition(req.request_id, RequestStatus.APPROVED, tick=3)
    assert reg.get(req.request_id).status is RequestStatus.APPROVED
    events = reg.events_of(req.request_id)
    assert [e.to_status for e in events] == [RequestStatus.VALIDATING, RequestStatus.APPROVED]
    assert len(reg.events) == 2
    assert [e.sequence for e in reg.events] == [0, 1]


def test_transition_illegal_fail_closed():
    reg = _reg()
    req = _create(reg)
    with pytest.raises(RequestLifecycleError):
        reg.transition(req.request_id, RequestStatus.RUNNING, tick=2)


def test_update_metadata_preserves_id():
    reg = _reg()
    req = _create(reg)
    updated = reg.update_metadata(req.request_id, RequestMetadata.create(description="d"))
    assert updated.request_id == req.request_id
    assert updated.metadata.description == "d"


def test_count_by_status_is_total_census():
    reg = _reg()
    req = _create(reg)
    reg.transition(req.request_id, RequestStatus.CANCELLED, tick=2)
    census = reg.count_by_status()
    assert set(census) == {s.value for s in RequestStatus}
    assert census["cancelled"] == 1
    assert census["submitted"] == 0


def test_to_dict_and_fingerprint_deterministic():
    def build():
        reg = _reg()
        _create(reg, slug="a", tick=1)
        _create(reg, slug="b", tick=2)
        return reg

    assert build().fingerprint() == build().fingerprint()
    d = build().to_dict()
    assert d["request_count"] == 2
    assert "status_census" in d


def test_create_via_type_helper_matches_registry():
    reg = _reg()
    req = _create(reg)
    direct = GenerationRequest.create(
        "req-1", "UCOS-BLPR-abc", "UCOS-WSPC-1", "arch@x", BlueprintFamily.DATA, submitted_tick=1
    )
    assert req.request_id == direct.request_id
