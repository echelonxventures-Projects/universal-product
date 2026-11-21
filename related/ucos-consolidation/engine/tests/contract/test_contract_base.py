"""Tests for TASK-000008 versioned contracts."""

from __future__ import annotations

import pytest

from engine.foundation.contracts.contract import Contract, ContractRegistry, Version
from engine.foundation.obs.errors import ContractViolation


def test_version_parse_and_str():
    version = Version.parse("1.2.3")
    assert (version.major, version.minor, version.patch) == (1, 2, 3)
    assert str(version) == "1.2.3"


def test_version_parse_invalid():
    for bad in ["1.2", "x.y.z", "1.2.3.4", ""]:
        with pytest.raises(ContractViolation):
            Version.parse(bad)


def test_version_ordering():
    assert Version(1, 0, 0) < Version(1, 0, 1) < Version(1, 1, 0) < Version(2, 0, 0)


def test_backward_compatibility_rule():
    assert Version(1, 3, 0).is_backward_compatible_with(Version(1, 2, 5))
    assert not Version(1, 1, 0).is_backward_compatible_with(Version(1, 2, 0))
    assert not Version(2, 0, 0).is_backward_compatible_with(Version(1, 9, 9))


def test_contract_requires_name():
    with pytest.raises(ContractViolation):
        Contract(name="", version=Version(1, 0, 0))


def test_contract_requires_version_type():
    with pytest.raises(ContractViolation):
        Contract(name="ir", version="1.0.0")  # type: ignore[arg-type]


def test_registry_register_and_get_latest():
    registry = ContractRegistry()
    registry.register(Contract("ir", Version(1, 0, 0)))
    registry.register(Contract("ir", Version(1, 1, 0)))
    assert registry.get("ir").version == Version(1, 1, 0)
    assert registry.get("ir", "1.0.0").version == Version(1, 0, 0)


def test_registry_rejects_duplicate():
    registry = ContractRegistry()
    registry.register(Contract("ir", Version(1, 0, 0)))
    with pytest.raises(ContractViolation):
        registry.register(Contract("ir", Version(1, 0, 0)))


def test_registry_rejects_older_within_major():
    registry = ContractRegistry()
    registry.register(Contract("ir", Version(1, 2, 0)))
    with pytest.raises(ContractViolation):
        registry.register(Contract("ir", Version(1, 1, 0)))


def test_registry_allows_new_major_line():
    registry = ContractRegistry()
    registry.register(Contract("ir", Version(1, 2, 0)))
    registry.register(Contract("ir", Version(2, 0, 0)))
    assert registry.get("ir").version == Version(2, 0, 0)


def test_get_unknown_contract_and_version():
    registry = ContractRegistry()
    with pytest.raises(ContractViolation):
        registry.get("missing")
    registry.register(Contract("ir", Version(1, 0, 0)))
    with pytest.raises(ContractViolation):
        registry.get("ir", "9.9.9")


def test_check_compatibility():
    registry = ContractRegistry()
    registry.register(Contract("ir", Version(1, 0, 0)))
    registry.register(Contract("ir", Version(1, 2, 0)))
    registry.register(Contract("ir", Version(2, 0, 0)))
    served = registry.check_compatibility("ir", "1.1.0")
    assert served.version == Version(1, 2, 0)
    with pytest.raises(ContractViolation):
        registry.check_compatibility("ir", "1.3.0")
    with pytest.raises(ContractViolation):
        registry.check_compatibility("missing", "1.0.0")


def test_names_and_versions():
    registry = ContractRegistry()
    registry.register(Contract("b", Version(1, 0, 0)))
    registry.register(Contract("a", Version(1, 0, 0)))
    registry.register(Contract("a", Version(1, 1, 0)))
    assert registry.names() == ["a", "b"]
    assert registry.versions("a") == [Version(1, 0, 0), Version(1, 1, 0)]
