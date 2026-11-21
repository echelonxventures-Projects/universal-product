"""EC2-TASK-000163 — Runtime Operations contracts tests (EC2-EPIC-012).

Covers the vocabulary, verb→permission map, descriptive metadata, the read-only view
projections (runtime unit / certification / deploy / rollback), and the content-addressed
:class:`RuntimeOperationRecord` aggregate including every fail-closed construction branch,
its derived properties, immutable metadata replacement, serialization, and the published
contract surface.
"""

from __future__ import annotations

from platform.foundation.identity import Permission
from platform.runtime_operations.contracts import (
    EMPTY_RUNTIME_OPERATION_METADATA,
    RUNTIME_OPERATIONS_CONTRACT_VERSION,
    RUNTIME_OPERATIONS_CONTRACTS,
    RUNTIME_OPERATIONS_GROUP,
    CertificationReference,
    DeploymentDescriptorView,
    RollbackDescriptorView,
    RuntimeOperationAction,
    RuntimeOperationKind,
    RuntimeOperationMetadata,
    RuntimeOperationRecord,
    RuntimeUnitReference,
    action_for_kind,
    all_runtime_operation_actions,
    default_runtime_operations_contracts,
    permission_for,
    runtime_operations_contract,
)
from platform.runtime_operations.errors import RuntimeOperationsContractError
from platform.runtime_operations.facade import RuntimeFacade
from platform.tests.runtime_operations_helpers import certification_record, runtime_unit

import pytest

_FACADE = RuntimeFacade()


def _deploy_descriptor(unit=None):
    unit = unit or runtime_unit()
    return unit, _FACADE.deployment_descriptor(unit)


def _rollback_descriptor(unit=None, previous=None):
    unit = unit or runtime_unit()
    return unit, _FACADE.rollback_descriptor(unit, previous=previous)


# --------------------------------------------------------------------------- #
# Vocabulary                                                                   #
# --------------------------------------------------------------------------- #


def test_group_is_reused_runtime_operations():
    assert RUNTIME_OPERATIONS_GROUP.value == "runtime-operations"


def test_permission_for_execute_and_read():
    assert permission_for(RuntimeOperationAction.DEPLOY) is Permission.EXECUTE
    assert permission_for(RuntimeOperationAction.ROLLBACK) is Permission.EXECUTE
    for action in RuntimeOperationAction:
        if action not in (RuntimeOperationAction.DEPLOY, RuntimeOperationAction.ROLLBACK):
            assert permission_for(action) is Permission.READ


def test_permission_for_rejects_non_action():
    with pytest.raises(RuntimeOperationsContractError):
        permission_for("deploy")  # type: ignore[arg-type]


def test_all_actions_stable():
    assert all_runtime_operation_actions() == tuple(RuntimeOperationAction)


def test_action_for_kind():
    assert action_for_kind(RuntimeOperationKind.DEPLOY) is RuntimeOperationAction.DEPLOY
    assert action_for_kind(RuntimeOperationKind.ROLLBACK) is RuntimeOperationAction.ROLLBACK
    with pytest.raises(RuntimeOperationsContractError):
        action_for_kind("deploy")  # type: ignore[arg-type]


# --------------------------------------------------------------------------- #
# Metadata                                                                     #
# --------------------------------------------------------------------------- #


def test_metadata_create_and_serialise():
    md = RuntimeOperationMetadata.create(
        description="note", labels=["b", "a"], annotations={"k": "v"}
    )
    assert md.has_label("a") and not md.has_label("z")
    assert md.to_dict()["labels"] == ["a", "b"]
    assert md.fingerprint() == md.fingerprint()
    assert EMPTY_RUNTIME_OPERATION_METADATA.description == ""


def test_metadata_rejects_bad_description_and_labels():
    with pytest.raises(RuntimeOperationsContractError):
        RuntimeOperationMetadata.create(description=1)  # type: ignore[arg-type]
    with pytest.raises(RuntimeOperationsContractError):
        RuntimeOperationMetadata.create(labels=[""])
    with pytest.raises(RuntimeOperationsContractError):
        RuntimeOperationMetadata.create(annotations={"k": 1})  # type: ignore[dict-item]


# --------------------------------------------------------------------------- #
# View projections                                                             #
# --------------------------------------------------------------------------- #


def test_runtime_unit_reference_projection():
    unit = runtime_unit()
    ref = RuntimeUnitReference.from_unit(unit)
    assert ref.reference_id.startswith("UCOS-RURF-")
    assert ref.runtime_id == unit.runtime_id
    assert ref.disclosure_present is True
    assert ref.closure_size == 1
    assert ref.to_dict()["runtime_id"] == unit.runtime_id
    assert ref.fingerprint() == ref.fingerprint()
    with pytest.raises(RuntimeOperationsContractError):
        RuntimeUnitReference.from_unit("nope")  # type: ignore[arg-type]


def test_certification_reference_projection():
    cert = certification_record()
    ref = CertificationReference.from_record(cert)
    assert ref.certified is True
    assert ref.target_id == cert.target_id
    assert ref.to_dict()["certification_id"] == cert.certification_id
    assert ref.fingerprint() == ref.fingerprint()
    with pytest.raises(RuntimeOperationsContractError):
        CertificationReference.from_record("nope")  # type: ignore[arg-type]


def test_deployment_descriptor_view_projection():
    _, deployment = _deploy_descriptor()
    view = DeploymentDescriptorView.from_descriptor(deployment)
    assert view.immutable is True
    assert view.manifest_kinds == ("ConfigMap", "Deployment", "Service")
    assert view.disclosure_present is True
    assert view.to_dict()["kind"] == "deploy"
    with pytest.raises(RuntimeOperationsContractError):
        DeploymentDescriptorView.from_descriptor("nope")  # type: ignore[arg-type]


def test_rollback_descriptor_view_projection():
    _, rb = _rollback_descriptor()
    view = RollbackDescriptorView.from_descriptor(rb)
    assert view.reversible is True
    assert view.has_checkpoint is True
    assert view.reverts_to_present is False
    assert view.restore_image
    assert view.to_dict()["kind"] == "rollback"
    with pytest.raises(RuntimeOperationsContractError):
        RollbackDescriptorView.from_descriptor("nope")  # type: ignore[arg-type]


def test_rollback_view_reverts_to_present_with_previous():
    unit = runtime_unit()
    previous = runtime_unit(pkg="b" * 64)
    rb = _FACADE.rollback_descriptor(unit, previous=previous)
    view = RollbackDescriptorView.from_descriptor(rb)
    assert view.reverts_to_present is True


# --------------------------------------------------------------------------- #
# RuntimeOperationRecord                                                       #
# --------------------------------------------------------------------------- #


def _deploy_record(**kw):
    unit, deployment = _deploy_descriptor()
    return RuntimeOperationRecord.create(
        kind=RuntimeOperationKind.DEPLOY,
        unit=unit,
        certification=certification_record(),
        deployment=deployment,
        owner_subject="op@x",
        environment="runtime",
        **kw,
    )


def _rollback_record(**kw):
    unit, rb = _rollback_descriptor()
    return RuntimeOperationRecord.create(
        kind=RuntimeOperationKind.ROLLBACK,
        unit=unit,
        certification=certification_record(),
        rollback=rb,
        owner_subject="op@x",
        environment="runtime",
        **kw,
    )


def test_deploy_record_create_and_properties():
    rec = _deploy_record(
        request_ref="UCOS-GREQ-1", workspace_id="ws", project_id="pr", tenant="acme"
    )
    assert rec.operation_id.startswith("UCOS-ROPR-")
    assert rec.kind is RuntimeOperationKind.DEPLOY
    assert rec.certified is True
    assert rec.reversible is False
    assert rec.previous_ref is None
    assert rec.deployment_view().immutable is True
    assert rec.unit_reference().runtime_id == rec.runtime_id
    assert rec.certification_reference().certified is True
    assert rec.descriptor_fingerprint()
    assert rec.to_dict()["kind"] == "deploy"
    assert rec.fingerprint() == rec.fingerprint()
    with pytest.raises(RuntimeOperationsContractError):
        rec.rollback_view()


def test_rollback_record_create_and_properties():
    unit = runtime_unit()
    previous = runtime_unit(pkg="b" * 64)
    rb = _FACADE.rollback_descriptor(unit, previous=previous)
    rec = RuntimeOperationRecord.create(
        kind=RuntimeOperationKind.ROLLBACK,
        unit=unit,
        certification=certification_record(),
        rollback=rb,
        owner_subject="op@x",
        environment="runtime",
        previous_unit=previous,
    )
    assert rec.reversible is True
    assert rec.previous_ref == previous.runtime_id
    assert rec.previous_unit is previous
    assert rec.rollback_view().reverts_to_present is True
    with pytest.raises(RuntimeOperationsContractError):
        rec.deployment_view()


def test_record_metadata_replacement_preserves_id():
    rec = _deploy_record()
    updated = rec.with_metadata(RuntimeOperationMetadata.create(description="x"))
    assert updated.operation_id == rec.operation_id
    assert updated.metadata.description == "x"
    with pytest.raises(RuntimeOperationsContractError):
        rec.with_metadata("nope")  # type: ignore[arg-type]


def test_record_create_rejects_bad_core_fields():
    unit, deployment = _deploy_descriptor()
    cert = certification_record()
    with pytest.raises(RuntimeOperationsContractError):
        RuntimeOperationRecord.create(
            kind="deploy",
            unit=unit,
            certification=cert,
            deployment=deployment,  # type: ignore[arg-type]
            owner_subject="o",
            environment="runtime",
        )
    with pytest.raises(RuntimeOperationsContractError):
        RuntimeOperationRecord.create(
            kind=RuntimeOperationKind.DEPLOY,
            unit="nope",
            certification=cert,  # type: ignore[arg-type]
            deployment=deployment,
            owner_subject="o",
            environment="runtime",
        )
    with pytest.raises(RuntimeOperationsContractError):
        RuntimeOperationRecord.create(
            kind=RuntimeOperationKind.DEPLOY,
            unit=unit,
            certification="nope",  # type: ignore[arg-type]
            deployment=deployment,
            owner_subject="o",
            environment="runtime",
        )
    with pytest.raises(RuntimeOperationsContractError):
        RuntimeOperationRecord.create(
            kind=RuntimeOperationKind.DEPLOY,
            unit=unit,
            certification=cert,
            deployment=deployment,
            owner_subject="",
            environment="runtime",
        )
    with pytest.raises(RuntimeOperationsContractError):
        RuntimeOperationRecord.create(
            kind=RuntimeOperationKind.DEPLOY,
            unit=unit,
            certification=cert,
            deployment=deployment,
            owner_subject="o",
            environment="",
        )


def test_record_create_descriptor_consistency_branches():
    unit, deployment = _deploy_descriptor()
    _, rb = _rollback_descriptor(unit=unit)
    cert = certification_record()
    # deploy missing deployment
    with pytest.raises(RuntimeOperationsContractError):
        RuntimeOperationRecord.create(
            kind=RuntimeOperationKind.DEPLOY,
            unit=unit,
            certification=cert,
            owner_subject="o",
            environment="runtime",
        )
    # deploy carrying a rollback
    with pytest.raises(RuntimeOperationsContractError):
        RuntimeOperationRecord.create(
            kind=RuntimeOperationKind.DEPLOY,
            unit=unit,
            certification=cert,
            deployment=deployment,
            rollback=rb,
            owner_subject="o",
            environment="runtime",
        )
    # rollback missing rollback
    with pytest.raises(RuntimeOperationsContractError):
        RuntimeOperationRecord.create(
            kind=RuntimeOperationKind.ROLLBACK,
            unit=unit,
            certification=cert,
            owner_subject="o",
            environment="runtime",
        )
    # rollback carrying a deployment
    with pytest.raises(RuntimeOperationsContractError):
        RuntimeOperationRecord.create(
            kind=RuntimeOperationKind.ROLLBACK,
            unit=unit,
            certification=cert,
            rollback=rb,
            deployment=deployment,
            owner_subject="o",
            environment="runtime",
        )


def test_record_create_descriptor_unit_mismatch():
    unit, _ = _deploy_descriptor()
    other_unit = runtime_unit(runtime_id="UCOS-RUN-other-0000000000000000", blueprint="UCOS-BLPR-9")
    other_deployment = _FACADE.deployment_descriptor(other_unit)
    with pytest.raises(RuntimeOperationsContractError):
        RuntimeOperationRecord.create(
            kind=RuntimeOperationKind.DEPLOY,
            unit=unit,
            certification=certification_record(),
            deployment=other_deployment,
            owner_subject="o",
            environment="runtime",
        )


def test_record_create_rejects_bad_optional_fields():
    unit, deployment = _deploy_descriptor()
    cert = certification_record()
    with pytest.raises(RuntimeOperationsContractError):
        RuntimeOperationRecord.create(
            kind=RuntimeOperationKind.DEPLOY,
            unit=unit,
            certification=cert,
            deployment=deployment,
            owner_subject="o",
            environment="runtime",
            request_ref="",
        )
    with pytest.raises(RuntimeOperationsContractError):
        RuntimeOperationRecord.create(
            kind=RuntimeOperationKind.DEPLOY,
            unit=unit,
            certification=cert,
            deployment=deployment,
            owner_subject="o",
            environment="runtime",
            metadata="nope",  # type: ignore[arg-type]
        )


def test_record_create_rejects_bad_previous_unit():
    unit, rb = _rollback_descriptor()
    cert = certification_record()
    with pytest.raises(RuntimeOperationsContractError):
        RuntimeOperationRecord.create(
            kind=RuntimeOperationKind.ROLLBACK,
            unit=unit,
            certification=cert,
            rollback=rb,
            owner_subject="o",
            environment="runtime",
            previous_unit="nope",  # type: ignore[arg-type]
        )
    # deploy must not carry a previous unit
    _, deployment = _deploy_descriptor(unit=unit)
    with pytest.raises(RuntimeOperationsContractError):
        RuntimeOperationRecord.create(
            kind=RuntimeOperationKind.DEPLOY,
            unit=unit,
            certification=cert,
            deployment=deployment,
            owner_subject="o",
            environment="runtime",
            previous_unit=runtime_unit(pkg="b" * 64),
        )


# --------------------------------------------------------------------------- #
# Published contract surface                                                   #
# --------------------------------------------------------------------------- #


def test_published_contracts():
    assert len(RUNTIME_OPERATIONS_CONTRACTS) == 11
    contracts = default_runtime_operations_contracts()
    assert len(contracts) == len(RUNTIME_OPERATIONS_CONTRACTS)
    assert all(str(c.version) == RUNTIME_OPERATIONS_CONTRACT_VERSION for c in contracts)


def test_runtime_operations_contract_rejects_empty_name():
    with pytest.raises(RuntimeOperationsContractError):
        runtime_operations_contract("")
