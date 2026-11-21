"""EC2-TASK-000058 — Platform service registry tests."""

from __future__ import annotations

from platform.foundation.contracts import platform_contract
from platform.foundation.errors import (
    ServiceRegistrationError,
    ServiceResolutionError,
)
from platform.foundation.services import ServiceDescriptor, ServiceRegistry

import pytest


def _descriptor(name, deps=(), caps=()):
    return ServiceDescriptor(
        name=name,
        contract=platform_contract(name, "1.0.0"),
        capabilities=tuple(caps),
        dependencies=tuple(deps),
    )


def test_descriptor_requires_name_and_contract():
    with pytest.raises(ServiceRegistrationError):
        ServiceDescriptor(name="", contract=platform_contract("x", "1.0.0"))
    with pytest.raises(ServiceRegistrationError):
        ServiceDescriptor(name="x", contract=object())  # type: ignore[arg-type]


def test_register_and_list_deterministically():
    reg = ServiceRegistry()
    reg.register(_descriptor("b"))
    reg.register(_descriptor("a"))
    assert reg.names == ("a", "b")
    assert "a" in reg and len(reg) == 2
    assert reg.descriptor("a").name == "a"
    assert [d.name for d in reg.descriptors()] == ["a", "b"]


def test_register_publishes_contract():
    reg = ServiceRegistry()
    reg.register(_descriptor("svc.one"))
    assert reg.contracts.get("svc.one").name == "svc.one"


def test_duplicate_registration_rejected():
    reg = ServiceRegistry()
    reg.register(_descriptor("dup"))
    with pytest.raises(ServiceRegistrationError):
        reg.register(_descriptor("dup"))


def test_resolve_uses_provider_and_memoizes():
    reg = ServiceRegistry()
    calls = []

    def provider():
        calls.append(1)
        return {"instance": True}

    reg.register(_descriptor("svc"), provider=provider)
    a = reg.resolve("svc")
    b = reg.resolve("svc")
    assert a is b  # memoized
    assert len(calls) == 1


def test_resolve_without_provider_raises():
    reg = ServiceRegistry()
    reg.register(_descriptor("svc"))
    with pytest.raises(ServiceResolutionError):
        reg.resolve("svc")


def test_resolve_unknown_raises():
    reg = ServiceRegistry()
    with pytest.raises(ServiceResolutionError):
        reg.resolve("nope")
    with pytest.raises(ServiceResolutionError):
        reg.descriptor("nope")


def test_startup_order_honors_dependencies():
    reg = ServiceRegistry()
    reg.register(_descriptor("api", deps=["identity"]))
    reg.register(_descriptor("identity"))
    reg.register(_descriptor("portal", deps=["api", "identity"]))
    order = reg.startup_order()
    assert order.index("identity") < order.index("api") < order.index("portal")


def test_validate_rejects_unregistered_dependency():
    reg = ServiceRegistry()
    reg.register(_descriptor("api", deps=["identity"]))
    with pytest.raises(ServiceRegistrationError):
        reg.validate()


def test_validate_passes_with_satisfied_dependencies():
    reg = ServiceRegistry()
    reg.register(_descriptor("identity"))
    reg.register(_descriptor("api", deps=["identity"]))
    reg.register(_descriptor("portal", deps=["api", "identity"]))
    reg.validate()  # exercises satisfied-dependency loop arcs; does not raise


def test_to_dict():
    reg = ServiceRegistry()
    reg.register(_descriptor("a", caps=["PC-01"]))
    d = reg.to_dict()
    assert d["service_count"] == 1
    assert d["services"][0]["capabilities"] == ["PC-01"]
