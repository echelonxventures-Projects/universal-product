"""EPIC-007 (T7) — Universal Runtime Platform contracts & vocabulary tests."""

from __future__ import annotations

from platform.runtime_platform.contracts import (
    CONSUMED_CONTRACTS,
    RUNTIME_PLATFORM_CONTRACTS,
    ConsumedCapability,
    RuntimePlatformAction,
    RuntimeServiceKind,
    RuntimeServiceView,
    WorkloadAttestation,
    all_runtime_service_kinds,
    default_runtime_platform_contracts,
    runtime_platform_contract,
)
from platform.runtime_platform.errors import RuntimePlatformContractError

import pytest


def test_attestation_is_content_addressed_and_deterministic():
    a = WorkloadAttestation(workload_id="w", registry_id="r", validated=True, certified=True)
    b = WorkloadAttestation(workload_id="w", registry_id="r", validated=True, certified=True)
    assert a.attestation_id == b.attestation_id
    assert a.attestation_id.startswith("UCOS-URPA-")
    assert a.fingerprint() == b.fingerprint()


def test_attestation_admissible_only_when_validated_and_certified():
    assert WorkloadAttestation("w", "r", True, True).admissible is True
    assert WorkloadAttestation("w", "r", True, False).admissible is False
    assert WorkloadAttestation("w", "r", False, True).admissible is False


def test_attestation_validation_fail_closed():
    with pytest.raises(RuntimePlatformContractError):
        WorkloadAttestation("", "r", True, True)
    with pytest.raises(RuntimePlatformContractError):
        WorkloadAttestation("w", "", True, True)
    with pytest.raises(RuntimePlatformContractError):
        WorkloadAttestation("w", "r", "yes", True)  # type: ignore[arg-type]


def test_attestation_consumed_capabilities_reflect_refs():
    full = WorkloadAttestation("w", "r", True, True, knowledge_id="k", measurement_id="m")
    caps = full.consumed_capabilities()
    assert ConsumedCapability.REGISTRY in caps
    assert ConsumedCapability.KNOWLEDGE in caps
    assert ConsumedCapability.MEASUREMENT in caps
    assert ConsumedCapability.VALIDATION in caps
    assert ConsumedCapability.CERTIFICATION in caps
    minimal = WorkloadAttestation("w", "r", False, False)
    assert minimal.consumed_capabilities() == (ConsumedCapability.REGISTRY,)


def test_attestation_to_dict_roundtrips_core_fields():
    a = WorkloadAttestation("w", "r", True, True, knowledge_id="k")
    d = a.to_dict()
    assert d["workload_id"] == "w"
    assert d["admissible"] is True
    assert d["knowledge_id"] == "k"


def test_service_kinds_and_names():
    kinds = all_runtime_service_kinds()
    assert len(kinds) == 9
    assert RuntimeServiceKind.EXECUTION_SCHEDULING in kinds
    assert RuntimeServiceKind.EXECUTION_SCHEDULING.service_name.startswith(
        "platform.runtime_platform."
    )


def test_consumed_contracts_cover_five_capabilities():
    names = {ref.name for ref in CONSUMED_CONTRACTS}
    assert names == {c.value for c in ConsumedCapability}
    assert len(CONSUMED_CONTRACTS) == 5


def test_contract_builders():
    contract = runtime_platform_contract(RuntimeServiceKind.WORKFLOW_EXECUTION)
    assert contract.name == RuntimeServiceKind.WORKFLOW_EXECUTION.service_name
    assert len(default_runtime_platform_contracts()) == 9
    assert len(RUNTIME_PLATFORM_CONTRACTS) == 9


def test_contract_builder_rejects_non_kind():
    with pytest.raises(RuntimePlatformContractError):
        runtime_platform_contract("not-a-kind")  # type: ignore[arg-type]


def test_runtime_service_view_to_dict():
    view = RuntimeServiceView(
        kind=RuntimeServiceKind.EVENT_DELIVERY,
        service_name=RuntimeServiceKind.EVENT_DELIVERY.service_name,
        capabilities=("CAP-17",),
    )
    assert view.to_dict()["kind"] == "event-delivery"


def test_platform_action_vocabulary():
    assert RuntimePlatformAction.SUBMIT.value == "submit"
    assert {a.value for a in RuntimePlatformAction} >= {"submit", "inspect", "discover"}


def test_an_attestation_that_carries_its_own_id_is_left_alone() -> None:
    """The second half of identity derivation: a supplied id survives __post_init__.

    Registry-first attests to a known identifier; re-minting one that already names
    itself would break the chain that cites it.
    """
    attested = WorkloadAttestation(
        registry_id="UCOS-URPR-GIVEN",
        workload_id="wl-given",
        attestation_id="UCOS-URPA-PRESET",
        validated=True,
        certified=True,
    )
    assert attested.attestation_id == "UCOS-URPA-PRESET"
