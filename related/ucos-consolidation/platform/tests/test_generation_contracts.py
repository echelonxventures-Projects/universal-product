"""EC2-TASK-000109 — Generation request contract + metadata tests (EC2-EPIC-007).

Covers the immutable vocabulary and value types: RequestStatus / ExecutionState /
RequestAction, the verb→permission map, the lifecycle→execution-posture map, the
content-addressed GenerationRequest aggregate (identity, immutability, derived facets,
validation), RequestMetadata, and the published contract surface — asserting the reuse
of the certified capability group and the frozen BlueprintFamily classification model.
"""

from __future__ import annotations

from platform.blueprints.contracts import BlueprintFamily
from platform.foundation.identity import Permission
from platform.generation.contracts import (
    GENERATION_REQUEST_CONTRACT_VERSION,
    GENERATION_REQUEST_CONTRACTS,
    GENERATION_REQUEST_GROUP,
    MUTATING_ACTIONS,
    TERMINAL_STATUSES,
    ExecutionState,
    GenerationRequest,
    RequestAction,
    RequestFamily,
    RequestStatus,
    all_execution_states,
    all_request_actions,
    all_request_statuses,
    default_generation_request_contracts,
    execution_state_for,
    generation_request_contract,
    permission_for,
)
from platform.generation.errors import RequestContractError, RequestMetadataError
from platform.generation.metadata import EMPTY_METADATA, RequestMetadata
from platform.identity.contracts import CapabilityGroup

import pytest


def _request(**kw):
    base = dict(
        slug="req-1",
        blueprint_ref="UCOS-BLPR-abc",
        workspace_id="UCOS-WSPC-1",
        owner_subject="arch@x",
        family=BlueprintFamily.DATA,
        submitted_tick=1,
    )
    base.update(kw)
    return GenerationRequest.create(**base)


# --------------------------------------------------------------------------- #
# Vocabulary reuse                                                             #
# --------------------------------------------------------------------------- #


def test_reuses_generation_requests_capability_group_no_new_group():
    assert GENERATION_REQUEST_GROUP is CapabilityGroup.GENERATION_REQUESTS


def test_reuses_frozen_family_classification_model():
    assert RequestFamily is BlueprintFamily


def test_all_helpers_return_stable_declaration_order():
    assert all_request_statuses() == tuple(RequestStatus)
    assert all_execution_states() == tuple(ExecutionState)
    assert all_request_actions() == tuple(RequestAction)


def test_terminal_statuses_and_mutating_actions():
    assert TERMINAL_STATUSES == frozenset(
        {RequestStatus.COMPLETED, RequestStatus.FAILED, RequestStatus.CANCELLED}
    )
    assert RequestAction.DISPATCH in MUTATING_ACTIONS
    assert RequestAction.INSPECT not in MUTATING_ACTIONS


# --------------------------------------------------------------------------- #
# permission_for / execution_state_for                                         #
# --------------------------------------------------------------------------- #


def test_permission_for_maps_every_action():
    assert permission_for(RequestAction.SUBMIT) is Permission.CREATE
    assert permission_for(RequestAction.INSPECT) is Permission.READ
    assert permission_for(RequestAction.DISPATCH) is Permission.EXECUTE
    assert permission_for(RequestAction.RUN) is Permission.EXECUTE
    assert permission_for(RequestAction.CANCEL) is Permission.CREATE
    for action in RequestAction:
        assert isinstance(permission_for(action), Permission)


def test_permission_for_rejects_non_action():
    with pytest.raises(RequestContractError):
        permission_for("submit")  # type: ignore[arg-type]


def test_execution_state_for_is_total_and_deterministic():
    assert execution_state_for(RequestStatus.SUBMITTED) is ExecutionState.PENDING
    assert execution_state_for(RequestStatus.QUEUED) is ExecutionState.PENDING
    assert execution_state_for(RequestStatus.DISPATCHED) is ExecutionState.DISPATCHED
    assert execution_state_for(RequestStatus.RUNNING) is ExecutionState.EXECUTING
    assert execution_state_for(RequestStatus.COMPLETED) is ExecutionState.SUCCEEDED
    assert execution_state_for(RequestStatus.FAILED) is ExecutionState.FAILED
    assert execution_state_for(RequestStatus.CANCELLED) is ExecutionState.ABORTED
    for status in RequestStatus:
        assert isinstance(execution_state_for(status), ExecutionState)


def test_execution_state_for_rejects_non_status():
    with pytest.raises(RequestContractError):
        execution_state_for("submitted")  # type: ignore[arg-type]


# --------------------------------------------------------------------------- #
# GenerationRequest aggregate                                                  #
# --------------------------------------------------------------------------- #


def test_create_is_content_addressed_and_deterministic():
    a = _request()
    b = _request()
    assert a.request_id == b.request_id
    assert a.request_id.startswith("UCOS-GREQ-")
    # Distinct submitted_tick ⇒ distinct request id.
    assert _request(submitted_tick=2).request_id != a.request_id


def test_create_defaults_submitted_and_empty_metadata():
    req = _request()
    assert req.status is RequestStatus.SUBMITTED
    assert req.metadata is EMPTY_METADATA
    assert req.execution_state is ExecutionState.PENDING
    assert req.is_terminal is False
    assert req.is_dispatched is False


def test_derived_facets_track_status():
    assert _request(status=RequestStatus.RUNNING).execution_state is ExecutionState.EXECUTING
    assert _request(status=RequestStatus.DISPATCHED).is_dispatched is True
    assert _request(status=RequestStatus.COMPLETED).is_dispatched is True
    assert _request(status=RequestStatus.CANCELLED).is_terminal is True
    assert _request(status=RequestStatus.CANCELLED).is_dispatched is False


@pytest.mark.parametrize(
    "kw",
    [
        {"slug": ""},
        {"slug": "has space"},
        {"blueprint_ref": ""},
        {"workspace_id": ""},
        {"owner_subject": ""},
        {"family": "data"},
        {"status": "submitted"},
        {"submitted_tick": "1"},
        {"submitted_tick": True},
        {"project_id": ""},
        {"metadata": "nope"},
    ],
)
def test_create_rejects_malformed_fields(kw):
    with pytest.raises(RequestContractError):
        _request(**kw)


def test_with_status_preserves_id_and_validates():
    req = _request()
    updated = req.with_status(RequestStatus.VALIDATING)
    assert updated.request_id == req.request_id
    assert updated.status is RequestStatus.VALIDATING
    with pytest.raises(RequestContractError):
        req.with_status("validating")  # type: ignore[arg-type]


def test_with_metadata_preserves_id_and_validates():
    req = _request()
    md = RequestMetadata.create(description="d")
    updated = req.with_metadata(md)
    assert updated.request_id == req.request_id
    assert updated.metadata.description == "d"
    with pytest.raises(RequestContractError):
        req.with_metadata("nope")  # type: ignore[arg-type]


def test_to_dict_and_fingerprint_round_trip():
    req = _request(project_id="UCOS-PROJ-1", tenant="acme")
    d = req.to_dict()
    assert d["request_id"] == req.request_id
    assert d["execution_state"] == "pending"
    assert d["project_id"] == "UCOS-PROJ-1"
    assert d["tenant"] == "acme"
    assert req.fingerprint() == _request(project_id="UCOS-PROJ-1", tenant="acme").fingerprint()


# --------------------------------------------------------------------------- #
# Published contract surface                                                   #
# --------------------------------------------------------------------------- #


def test_published_contracts_are_versioned_references():
    assert len(GENERATION_REQUEST_CONTRACTS) == 7
    for ref in GENERATION_REQUEST_CONTRACTS:
        assert ref.version == GENERATION_REQUEST_CONTRACT_VERSION
    names = {ref.name for ref in GENERATION_REQUEST_CONTRACTS}
    assert "requests.dispatch.handoff" in names
    assert "requests.runtime.service" in names


def test_default_contracts_build_concrete_contracts():
    contracts = default_generation_request_contracts()
    assert len(contracts) == len(GENERATION_REQUEST_CONTRACTS)
    assert {c.name for c in contracts} == {ref.name for ref in GENERATION_REQUEST_CONTRACTS}


def test_generation_request_contract_rejects_empty_name():
    with pytest.raises(RequestContractError):
        generation_request_contract("")


# --------------------------------------------------------------------------- #
# Metadata                                                                     #
# --------------------------------------------------------------------------- #


def test_metadata_create_normalizes_and_fingerprints():
    md = RequestMetadata.create(description="d", labels=["a", "b"], annotations={"k": "v"})
    assert md.has_label("a")
    assert md.to_dict()["labels"] == ["a", "b"]
    assert (
        md.fingerprint()
        == RequestMetadata.create(
            description="d", labels=["b", "a"], annotations={"k": "v"}
        ).fingerprint()
    )


@pytest.mark.parametrize(
    "kw",
    [
        {"description": 1},
        {"labels": [""]},
        {"annotations": {"": "v"}},
        {"annotations": {"k": 1}},
    ],
)
def test_metadata_rejects_malformed(kw):
    with pytest.raises(RequestMetadataError):
        RequestMetadata.create(**kw)


def test_empty_metadata_is_shared_singleton():
    assert EMPTY_METADATA.description == ""
    assert EMPTY_METADATA.labels == frozenset()
