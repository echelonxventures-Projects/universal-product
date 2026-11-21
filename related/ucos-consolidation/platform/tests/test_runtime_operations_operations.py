"""EC2-TASK-000166 — Runtime Operations orchestration & registry tests (EC2-EPIC-012).

Covers the record-only orchestration planner (admit → generate descriptor → record;
fail-closed on a non-CERTIFIED unit) and the append-only operation registry (idempotent
recording, conflict rejection, discovery scoping, immutable metadata replacement, and the
append-only inspection log).
"""

from __future__ import annotations

from platform.runtime_operations.contracts import (
    RuntimeOperationKind,
    RuntimeOperationMetadata,
)
from platform.runtime_operations.errors import (
    RuntimeAdmissionError,
    RuntimeOperationRecordError,
)
from platform.runtime_operations.facade import RuntimeFacade
from platform.runtime_operations.guard import RuntimeAdmissionGuard
from platform.runtime_operations.operations import (
    InspectionEvent,
    RuntimeOperationPlan,
    RuntimeOperationPlanner,
    RuntimeOperationRegistry,
)
from platform.tests.runtime_operations_helpers import (
    certification_record,
    not_certified_unit_and_record,
    runtime_unit,
)

import pytest

# --------------------------------------------------------------------------- #
# Planner                                                                      #
# --------------------------------------------------------------------------- #


def test_planner_rejects_bad_components():
    with pytest.raises(RuntimeOperationRecordError):
        RuntimeOperationPlanner(facade="nope")  # type: ignore[arg-type]
    with pytest.raises(RuntimeOperationRecordError):
        RuntimeOperationPlanner(guard="nope")  # type: ignore[arg-type]


def test_planner_default_components():
    planner = RuntimeOperationPlanner()
    assert isinstance(planner.facade, RuntimeFacade)
    assert isinstance(planner.guard, RuntimeAdmissionGuard)


def test_plan_deploy():
    planner = RuntimeOperationPlanner()
    plan = planner.plan_deploy(
        runtime_unit(), certification_record(), owner_subject="op@x", request_ref="UCOS-GREQ-1"
    )
    assert isinstance(plan, RuntimeOperationPlan)
    assert plan.plan_id.startswith("UCOS-ROOP-")
    assert plan.kind is RuntimeOperationKind.DEPLOY
    assert plan.reversibility is None
    assert plan.admission.admitted is True
    assert plan.record.request_ref == "UCOS-GREQ-1"
    assert plan.to_dict()["kind"] == "deploy"
    assert plan.fingerprint() == plan.fingerprint()


def test_plan_rollback_carries_reversibility_proof():
    planner = RuntimeOperationPlanner()
    plan = planner.plan_rollback(
        runtime_unit(),
        certification_record(),
        owner_subject="op@x",
        previous=runtime_unit(pkg="b" * 64),
    )
    assert plan.kind is RuntimeOperationKind.ROLLBACK
    assert plan.reversibility is not None
    assert plan.reversibility.reversible is True
    assert plan.record.previous_ref is not None
    assert plan.to_dict()["reversibility"]["reversible"] is True


def test_plan_deploy_fail_closed_non_certified():
    planner = RuntimeOperationPlanner()
    unit, cert = not_certified_unit_and_record()
    with pytest.raises(RuntimeAdmissionError):
        planner.plan_deploy(unit, cert, owner_subject="op@x")


def test_plan_rollback_fail_closed_non_certified():
    planner = RuntimeOperationPlanner()
    unit, cert = not_certified_unit_and_record()
    with pytest.raises(RuntimeAdmissionError):
        planner.plan_rollback(unit, cert, owner_subject="op@x")


# --------------------------------------------------------------------------- #
# Registry                                                                     #
# --------------------------------------------------------------------------- #


def _plan():
    return RuntimeOperationPlanner().plan_deploy(
        runtime_unit(), certification_record(), owner_subject="op@x", tenant="acme"
    )


def test_registry_record_idempotent_and_conflict():
    registry = RuntimeOperationRegistry()
    plan = _plan()
    a = registry.record(plan.record)
    b = registry.record(plan.record)
    assert a is b or a.operation_id == b.operation_id
    assert len(registry) == 1
    assert plan.record.operation_id in registry
    with pytest.raises(RuntimeOperationRecordError):
        registry.record("nope")  # type: ignore[arg-type]


def test_registry_conflicting_record_rejected():
    registry = RuntimeOperationRegistry()
    rec = _plan().record
    registry.record(rec)
    # Same id, different content (annotate produces a different fingerprint, same id).
    conflicting = rec.with_metadata(RuntimeOperationMetadata.create(description="different"))
    with pytest.raises(RuntimeOperationRecordError):
        registry.record(conflicting)


def test_registry_get_and_queries():
    registry = RuntimeOperationRegistry()
    rec = _plan().record
    registry.record(rec)
    assert registry.get(rec.operation_id) is rec
    assert registry.ids == (rec.operation_id,)
    assert registry.all() == (rec,)
    assert registry.by_runtime(rec.runtime_id) == (rec,)
    assert registry.by_kind(RuntimeOperationKind.DEPLOY) == (rec,)
    assert registry.by_kind(RuntimeOperationKind.ROLLBACK) == ()
    with pytest.raises(RuntimeOperationRecordError):
        registry.get("UCOS-ROPR-missing")


def test_registry_discover_scoping():
    registry = RuntimeOperationRegistry()
    rec = _plan().record
    registry.record(rec)
    assert registry.discover(runtime_id=rec.runtime_id)
    assert registry.discover(blueprint_id=rec.blueprint_id)
    assert registry.discover(certification_id=rec.certification.certification_id)
    assert registry.discover(environment="runtime")
    assert registry.discover(kind=RuntimeOperationKind.DEPLOY)
    assert registry.discover(tenant="acme")  # tenant + global visible
    assert registry.discover(runtime_id="none") == ()
    assert registry.discover(request_ref="none") == ()
    assert registry.discover(workspace_id="none") == ()
    assert registry.discover(project_id="none") == ()


def test_registry_metadata_and_inspection_log():
    registry = RuntimeOperationRegistry()
    rec = _plan().record
    registry.record(rec)
    updated = registry.update_metadata(
        rec.operation_id, RuntimeOperationMetadata.create(description="note")
    )
    assert updated.metadata.description == "note"
    event = registry.record_inspection(rec.operation_id, "inspect", "UCOS-PRIN-1", tick=5)
    assert isinstance(event, InspectionEvent)
    assert event.to_dict()["action"] == "inspect"
    assert registry.inspections_of(rec.operation_id) == (event,)
    assert registry.inspections == (event,)
    with pytest.raises(RuntimeOperationRecordError):
        registry.record_inspection("UCOS-ROPR-missing", "inspect", "p", tick=1)


def test_registry_census_and_serialise():
    registry = RuntimeOperationRegistry()
    registry.record(_plan().record)
    assert registry.count_by_kind() == {"total": 1, "deploy": 1, "rollback": 0}
    assert registry.to_dict()["operation_count"] == 1
    assert registry.fingerprint() == registry.fingerprint()
