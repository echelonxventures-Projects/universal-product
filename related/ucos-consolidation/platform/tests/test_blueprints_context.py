"""EC2-TASK-000102 — Blueprint context tests (EC2-EPIC-006)."""

from __future__ import annotations

from platform.blueprints.context import BlueprintContext
from platform.blueprints.contracts import Blueprint, BlueprintFamily, BlueprintStatus
from platform.blueprints.errors import BlueprintServiceError
from platform.foundation.identity import Principal, Role

import pytest


def _principal():
    return Principal.create("arch@x", [Role.ARCHITECT], tenant="acme")


def test_context_binds_who_what_where():
    bp = Blueprint.create(
        "bp",
        "n",
        "UCOS-WSPC-1",
        "arch@x",
        BlueprintFamily.DATA,
        project_id="UCOS-PROJ-1",
        tenant="acme",
    ).with_status(BlueprintStatus.CATALOGUED)
    ctx = BlueprintContext.create(bp, _principal(), is_owner=True)
    assert ctx.context_id.startswith("UCOS-BCTX-")
    assert ctx.blueprint_id == bp.blueprint_id
    assert ctx.family is BlueprintFamily.DATA
    assert ctx.project_id == "UCOS-PROJ-1"
    assert ctx.is_owner is True
    assert ctx.is_catalogued is True
    assert ctx.to_dict()["family"] == "data"


def test_context_is_deterministic():
    bp = Blueprint.create("bp", "n", "w", "arch@x", BlueprintFamily.DATA, tenant="acme")
    p = _principal()
    assert BlueprintContext.create(bp, p).context_id == BlueprintContext.create(bp, p).context_id
    assert isinstance(BlueprintContext.create(bp, p).fingerprint(), str)


def test_context_fail_closed_on_bad_inputs():
    bp = Blueprint.create("bp", "n", "w", "arch@x", BlueprintFamily.DATA)
    with pytest.raises(BlueprintServiceError):
        BlueprintContext.create("nope", _principal())  # type: ignore[arg-type]
    with pytest.raises(BlueprintServiceError):
        BlueprintContext.create(bp, "nope")  # type: ignore[arg-type]
    with pytest.raises(BlueprintServiceError):
        BlueprintContext.create(bp, _principal(), is_owner="yes")  # type: ignore[arg-type]
