"""EC2-TASK-000114 — Generation request derived-status tests (EC2-EPIC-007).

Covers the pure derived-status computation: lifecycle→posture mapping, derived
execution state, the traceability predicate (dispatch ∧ provenance), and deterministic
fingerprints. Also covers RequestContext derivation.
"""

from __future__ import annotations

from platform.blueprints.contracts import BlueprintFamily
from platform.foundation.identity import Principal, Role
from platform.generation.context import RequestContext
from platform.generation.contracts import ExecutionState, GenerationRequest, RequestStatus
from platform.generation.errors import RequestServiceError, RequestStatusError
from platform.generation.status import RequestPosture, derive_status

import pytest


def _request(status=RequestStatus.SUBMITTED, **kw):
    return GenerationRequest.create(
        "req-1",
        "UCOS-BLPR-abc",
        "UCOS-WSPC-1",
        "arch@x",
        BlueprintFamily.DATA,
        submitted_tick=1,
        status=status,
        **kw,
    )


def test_posture_maps_every_status():
    cases = {
        RequestStatus.SUBMITTED: RequestPosture.PENDING,
        RequestStatus.VALIDATING: RequestPosture.PENDING,
        RequestStatus.APPROVED: RequestPosture.PENDING,
        RequestStatus.QUEUED: RequestPosture.QUEUED,
        RequestStatus.DISPATCHED: RequestPosture.DISPATCHED,
        RequestStatus.RUNNING: RequestPosture.RUNNING,
        RequestStatus.COMPLETED: RequestPosture.COMPLETED,
        RequestStatus.FAILED: RequestPosture.FAILED,
        RequestStatus.CANCELLED: RequestPosture.CANCELLED,
    }
    for status, posture in cases.items():
        derived = derive_status(_request(status), has_dispatch=False, has_provenance=False)
        assert derived.posture is posture


def test_derived_carries_execution_state_and_flags():
    derived = derive_status(_request(RequestStatus.RUNNING), has_dispatch=True, has_provenance=True)
    assert derived.execution_state is ExecutionState.EXECUTING
    assert derived.is_dispatched is True
    assert derived.is_traceable is True
    assert derived.status_id.startswith("UCOS-GDST-")


def test_is_traceable_requires_both_dispatch_and_provenance():
    r = _request(RequestStatus.DISPATCHED)
    assert derive_status(r, has_dispatch=True, has_provenance=False).is_traceable is False
    assert derive_status(r, has_dispatch=False, has_provenance=True).is_traceable is False
    assert derive_status(r, has_dispatch=True, has_provenance=True).is_traceable is True


def test_derive_status_fingerprint_deterministic():
    a = derive_status(_request(RequestStatus.QUEUED), has_dispatch=False, has_provenance=False)
    b = derive_status(_request(RequestStatus.QUEUED), has_dispatch=False, has_provenance=False)
    assert a.fingerprint() == b.fingerprint()
    assert a.to_dict()["posture"] == "queued"


def test_derive_status_rejects_malformed():
    with pytest.raises(RequestStatusError):
        derive_status("nope", has_dispatch=False, has_provenance=False)  # type: ignore[arg-type]
    with pytest.raises(RequestStatusError):
        derive_status(_request(), has_dispatch="no", has_provenance=False)  # type: ignore[arg-type]
    with pytest.raises(RequestStatusError):
        derive_status(_request(), has_dispatch=False, has_provenance="no")  # type: ignore[arg-type]


# --------------------------------------------------------------------------- #
# Context                                                                      #
# --------------------------------------------------------------------------- #


def test_context_creation_and_facets():
    req = _request(RequestStatus.DISPATCHED, tenant="acme", project_id="UCOS-PROJ-1")
    principal = Principal.create("arch@x", [Role.ARCHITECT], tenant="acme")
    ctx = RequestContext.create(req, principal, is_owner=True)
    assert ctx.context_id.startswith("UCOS-GCTX-")
    assert ctx.request_id == req.request_id
    assert ctx.is_owner is True
    assert ctx.is_dispatched is True
    assert ctx.execution_state is ExecutionState.DISPATCHED
    assert ctx.to_dict()["subject"] == "arch@x"
    assert ctx.fingerprint() == RequestContext.create(req, principal, is_owner=True).fingerprint()


def test_context_not_dispatched_for_pending():
    req = _request(RequestStatus.QUEUED)
    principal = Principal.create("arch@x", [Role.ARCHITECT])
    assert RequestContext.create(req, principal).is_dispatched is False


def test_context_rejects_malformed():
    req = _request()
    principal = Principal.create("arch@x", [Role.ARCHITECT])
    with pytest.raises(RequestServiceError):
        RequestContext.create("nope", principal)  # type: ignore[arg-type]
    with pytest.raises(RequestServiceError):
        RequestContext.create(req, "nope")  # type: ignore[arg-type]
    with pytest.raises(RequestServiceError):
        RequestContext.create(req, principal, is_owner="yes")  # type: ignore[arg-type]
