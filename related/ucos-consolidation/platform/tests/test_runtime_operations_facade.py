"""EC2-TASK-000165 — Runtime Operations EC-1 façade tests (EC2-EPIC-012).

Covers the read-only L4 façade: it binds the certified ``engine.runtime`` contracts by
reference, reproduces deployment / rollback descriptors deterministically (byte-for-byte
fidelity, P6), projects a runtime-unit reference, and is fail-closed on bad inputs and on
an engine refusal (missing disclosure / unpinned package / empty closure).
"""

from __future__ import annotations

from platform.runtime_operations.contracts import (
    ENGINE_RUNTIME_ASSEMBLE_CONTRACT,
    ENGINE_RUNTIME_DEPLOY_CONTRACT,
)
from platform.runtime_operations.errors import RuntimeDescriptorError, RuntimeFidelityError
from platform.runtime_operations.facade import RUNTIME_ENGINE_CONTRACTS, RuntimeFacade
from platform.tests.runtime_operations_helpers import runtime_unit

import pytest

_FACADE = RuntimeFacade()


def test_binds_engine_runtime_contracts_by_reference():
    names = {ref.name for ref in RUNTIME_ENGINE_CONTRACTS}
    assert names == {ENGINE_RUNTIME_ASSEMBLE_CONTRACT, ENGINE_RUNTIME_DEPLOY_CONTRACT}
    assert _FACADE.engine_contracts == RUNTIME_ENGINE_CONTRACTS
    assert _FACADE.assemble_contract == ENGINE_RUNTIME_ASSEMBLE_CONTRACT
    assert _FACADE.deploy_contract == ENGINE_RUNTIME_DEPLOY_CONTRACT


def test_unit_reference():
    unit = runtime_unit()
    ref = _FACADE.unit_reference(unit)
    assert ref.runtime_id == unit.runtime_id
    with pytest.raises(RuntimeDescriptorError):
        _FACADE.unit_reference("nope")  # type: ignore[arg-type]


def test_deployment_descriptor_deterministic():
    unit = runtime_unit()
    a = _FACADE.deployment_descriptor(unit)
    b = _FACADE.deployment_descriptor(unit)
    assert a.to_dict() == b.to_dict()
    assert [m["kind"] for m in a.kubernetes] == ["ConfigMap", "Deployment", "Service"]


def test_deployment_descriptor_environment_override():
    dep = _FACADE.deployment_descriptor(runtime_unit(), environment="production")
    assert dep.environment == "production"


def test_rollback_descriptor_reversible():
    rb = _FACADE.rollback_descriptor(runtime_unit())
    assert rb.reversible is True
    assert rb.reverts_to is None


def test_rollback_descriptor_with_previous():
    rb = _FACADE.rollback_descriptor(runtime_unit(), previous=runtime_unit(pkg="b" * 64))
    assert rb.reverts_to is not None


def test_deployment_descriptor_rejects_bad_unit():
    with pytest.raises(RuntimeDescriptorError):
        _FACADE.deployment_descriptor("nope")  # type: ignore[arg-type]


def test_rollback_descriptor_rejects_bad_unit_and_previous():
    with pytest.raises(RuntimeDescriptorError):
        _FACADE.rollback_descriptor("nope")  # type: ignore[arg-type]
    with pytest.raises(RuntimeDescriptorError):
        _FACADE.rollback_descriptor(runtime_unit(), previous="nope")  # type: ignore[arg-type]


def test_engine_refusal_wrapped_as_descriptor_error():
    # A unit missing the disclosure makes the certified engine refuse (DisclosureError).
    no_disclosure = runtime_unit(with_disclosure=False)
    with pytest.raises(RuntimeDescriptorError):
        _FACADE.deployment_descriptor(no_disclosure)
    with pytest.raises(RuntimeDescriptorError):
        _FACADE.rollback_descriptor(no_disclosure)
    # A unit with an empty dependency closure makes the certified engine refuse (DeploymentError).
    no_closure = runtime_unit(with_closure=False)
    with pytest.raises(RuntimeDescriptorError):
        _FACADE.deployment_descriptor(no_closure)


def test_verify_fidelity_true_and_bad_type():
    unit = runtime_unit()
    dep = _FACADE.deployment_descriptor(unit)
    assert _FACADE.verify_deployment_fidelity(dep, unit) is True
    rb = _FACADE.rollback_descriptor(unit)
    assert _FACADE.verify_rollback_fidelity(rb, unit) is True
    with pytest.raises(RuntimeFidelityError):
        _FACADE.verify_deployment_fidelity("nope", unit)  # type: ignore[arg-type]
    with pytest.raises(RuntimeFidelityError):
        _FACADE.verify_rollback_fidelity("nope", unit)  # type: ignore[arg-type]


def test_verify_fidelity_false_on_divergence():
    unit = runtime_unit()
    dep = _FACADE.deployment_descriptor(unit, environment="production")
    # Reproducing in a different environment yields a different descriptor.
    assert _FACADE.verify_deployment_fidelity(dep, unit, environment="staging") is False
    rb = _FACADE.rollback_descriptor(unit, previous=runtime_unit(pkg="b" * 64))
    assert _FACADE.verify_rollback_fidelity(rb, unit, previous=None) is False
