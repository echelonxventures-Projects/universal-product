"""Completion tests — exercise every remaining branch to a genuine 100%."""

from __future__ import annotations

from engine.kernel.meta import MetaObject
from engine.provider.compliance import (
    _mechanism_vendor_tokens,
    architectural_proof,
)
from engine.provider.framework import ProviderFramework, _contract_is_wellformed
from engine.provider.metatypes import PROVIDER_INSTANCE_NS


def _provider_obj(metatype, key, *, caps=("c",), contract=None):
    return MetaObject(
        metatype=metatype,
        namespace=PROVIDER_INSTANCE_NS,
        natural_key=key,
        attributes={
            "capabilities": list(caps),
            "contract": {"name": "n", "version": "1.0.0"} if contract is None else contract,
        },
    )


def test_second_framework_reuses_seeded_kernel():
    # Building a second framework over the same kernel exercises the "already seeded /
    # already bound" skip branches in _seed_facets and _bind_governance.
    first = ProviderFramework()
    second = ProviderFramework(kernel=first.kernel)
    assert second.kernel is first.kernel
    assert second.validate() is True


def test_discover_without_capability_filter():
    fw = ProviderFramework()
    fw.register_category("StorageProvider")
    fw.register_provider(
        category="StorageProvider",
        key="s1",
        capabilities=["c"],
        contract={"name": "n", "version": "1.0.0"},
    )
    # capability=None takes the branch that skips the capability filter.
    assert len(fw.discover(category="StorageProvider")) == 1


def test_negotiate_without_capability_requirement():
    fw = ProviderFramework()
    fw.register_category("StorageProvider")
    p = fw.register_provider(
        category="StorageProvider",
        key="s1",
        capabilities=["c"],
        contract={"name": "n", "version": "1.0.0"},
    )
    # requirements without "capability" takes the wanted_cap-is-None branch.
    result = fw.negotiate({"contract": "n", "min_version": "1.0.0"}, p)
    assert result.compatible is True
    assert result.matched_capabilities == ()


def test_register_provider_non_mapping_contract_rejected():
    fw = ProviderFramework()
    fw.register_category("StorageProvider")
    import pytest

    from engine.provider.errors import ProviderContractError

    with pytest.raises(ProviderContractError):
        fw.register_provider(
            category="StorageProvider",
            key="s1",
            capabilities=["c"],
            contract="not-a-mapping",
        )


def test_contract_wellformed_non_mapping():
    assert _contract_is_wellformed("x") is False
    assert _contract_is_wellformed({"name": "n", "version": "1.0.0"}) is True


def test_validate_fails_when_kernel_invalid(monkeypatch):
    from engine.kernel.kernel import MetaKernel

    fw = ProviderFramework()
    monkeypatch.setattr(MetaKernel, "validate", lambda self: False)
    assert fw.validate() is False


def test_validate_fails_when_provider_category_unregistered(monkeypatch):
    fw = ProviderFramework()
    monkeypatch.setattr(
        ProviderFramework,
        "providers",
        lambda self, category=None: (_provider_obj("UnregisteredCat", "p"),),
    )
    assert fw.validate() is False


def test_validate_fails_when_provider_has_no_capability(monkeypatch):
    fw = ProviderFramework()
    fw.register_category("StorageProvider")
    monkeypatch.setattr(
        ProviderFramework,
        "providers",
        lambda self, category=None: (_provider_obj("StorageProvider", "p", caps=()),),
    )
    assert fw.validate() is False


def test_validate_fails_when_provider_contract_malformed(monkeypatch):
    fw = ProviderFramework()
    fw.register_category("StorageProvider")
    monkeypatch.setattr(
        ProviderFramework,
        "providers",
        lambda self, category=None: (_provider_obj("StorageProvider", "p", contract={}),),
    )
    assert fw.validate() is False


def test_mechanism_vendor_scan_flags_control_sample(tmp_path):
    (tmp_path / "leak.py").write_text("BASE = 'aws'  # docker\n", encoding="utf-8")
    found = _mechanism_vendor_tokens(tmp_path)
    assert "aws" in found and "docker" in found


def test_architectural_proof_records_failure(monkeypatch):
    def boom(self, **kwargs):
        raise RuntimeError("cannot realize")

    monkeypatch.setattr(ProviderFramework, "register_provider", boom)
    proof = architectural_proof()
    assert proof["passed"] is False
    assert all(r["ok"] is False for r in proof["records"])
