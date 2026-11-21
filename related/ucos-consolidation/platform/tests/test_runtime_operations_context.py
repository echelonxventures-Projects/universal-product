"""EC2-TASK-000167 — Runtime Operations context tests (EC2-EPIC-012)."""

from __future__ import annotations

from platform.foundation.identity import Principal, Role
from platform.runtime_operations.context import RuntimeOperationContext
from platform.runtime_operations.errors import RuntimeOperationServiceError
from platform.runtime_operations.operations import RuntimeOperationPlanner
from platform.runtime_operations.status import RuntimeOperationPosture
from platform.tests.runtime_operations_helpers import certification_record, runtime_unit

import pytest


def _record(kind="deploy"):
    planner = RuntimeOperationPlanner()
    if kind == "deploy":
        return planner.plan_deploy(
            runtime_unit(), certification_record(), owner_subject="admin@x", tenant="acme"
        ).record
    return planner.plan_rollback(
        runtime_unit(), certification_record(), owner_subject="admin@x"
    ).record


def _principal():
    return Principal.create("admin@x", [Role.PLATFORM_ADMINISTRATOR], tenant="acme")


def test_context_binding_deploy():
    ctx = RuntimeOperationContext.create(_record(), _principal(), is_owner=True)
    assert ctx.context_id.startswith("UCOS-ROCX-")
    assert ctx.kind == "deploy"
    assert ctx.posture is RuntimeOperationPosture.DEPLOY_GOVERNED
    assert ctx.is_owner is True
    assert ctx.tenant == "acme"
    assert ctx.to_dict()["kind"] == "deploy"
    assert ctx.fingerprint() == ctx.fingerprint()


def test_context_binding_rollback_reversible():
    ctx = RuntimeOperationContext.create(_record("rollback"), _principal())
    assert ctx.kind == "rollback"
    assert ctx.reversible is True
    assert ctx.posture is RuntimeOperationPosture.ROLLBACK_REVERSIBLE
    assert ctx.is_owner is False


def test_context_rejects_bad_arguments():
    with pytest.raises(RuntimeOperationServiceError):
        RuntimeOperationContext.create("nope", _principal())  # type: ignore[arg-type]
    with pytest.raises(RuntimeOperationServiceError):
        RuntimeOperationContext.create(_record(), "nope")  # type: ignore[arg-type]
    with pytest.raises(RuntimeOperationServiceError):
        RuntimeOperationContext.create(_record(), _principal(), is_owner="yes")  # type: ignore[arg-type]
