"""EC2-TASK-000055 — Platform contracts tests."""

from __future__ import annotations

from platform.foundation.contracts import (
    ENGINE_CONTRACTS,
    PLATFORM_CONTRACT_VERSION,
    Contract,
    ContractRef,
    ContractRegistry,
    Version,
    canonical_json,
    content_hash,
    platform_contract,
    platform_contract_registry,
)
from platform.foundation.errors import PlatformContractError

import pytest


def test_canonical_json_is_stable_and_sorted():
    assert canonical_json({"b": 1, "a": 2}) == '{"a":2,"b":1}'
    assert content_hash({"a": 1}) == content_hash({"a": 1})
    assert content_hash({"a": 1}) != content_hash({"a": 2})


def test_contract_ref_valid():
    ref = ContractRef("engine.registry.read", "1.0.0")
    assert ref.as_version() == Version(1, 0, 0)
    assert ref.to_dict() == {"name": "engine.registry.read", "version": "1.0.0"}


def test_contract_ref_defaults_to_platform_version():
    ref = ContractRef("svc.x")
    assert ref.version == PLATFORM_CONTRACT_VERSION


def test_contract_ref_rejects_empty_name():
    with pytest.raises(PlatformContractError):
        ContractRef("")


def test_contract_ref_rejects_bad_version():
    from engine.foundation.obs.errors import ContractViolation

    with pytest.raises(ContractViolation):
        ContractRef("svc.x", "notaversion")


def test_platform_contract_builds_versioned_contract():
    c = platform_contract("platform.api", "2.1.0", "API gateway contract")
    assert isinstance(c, Contract)
    assert c.name == "platform.api"
    assert str(c.version) == "2.1.0"


def test_platform_contract_rejects_empty_name():
    with pytest.raises(PlatformContractError):
        platform_contract("", "1.0.0")


def test_platform_contract_registry_is_ec1_registry():
    reg = platform_contract_registry()
    assert isinstance(reg, ContractRegistry)
    reg.register(platform_contract("a.b", "1.0.0"))
    assert reg.get("a.b").name == "a.b"


def test_engine_contracts_cover_certified_capabilities():
    names = {ref.name for ref in ENGINE_CONTRACTS}
    assert "engine.registry.read" in names
    assert "engine.certification.certify" in names
    assert len(ENGINE_CONTRACTS) == 8
