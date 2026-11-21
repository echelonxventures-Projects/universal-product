"""Tests for the MetaKernel facade and its universal operations."""

from __future__ import annotations

import pytest

from engine.foundation.contracts.contract import Version
from engine.kernel.errors import MetaTypeUnknownError
from engine.kernel.kernel import MetaKernel
from engine.kernel.seed import FOUNDING_METATYPES


def test_seeded_kernel_has_root_and_founding_metatypes():
    kernel = MetaKernel()
    keys = set(kernel.registry.metatype_keys())
    assert "MetaType" in keys
    for natural_key, _n, _d in FOUNDING_METATYPES:
        assert natural_key in keys
    # 22 founding + reflective root = 23 meta-types.
    assert len(kernel.metatypes()) == len(FOUNDING_METATYPES) + 1


def test_unseeded_kernel_is_empty():
    kernel = MetaKernel(seed=False)
    assert kernel.registry.count() == 0


def test_register_metatype_and_object_and_classify():
    kernel = MetaKernel()
    kernel.register_metatype("Sensor", description="a provider category")
    obj = kernel.register_object(
        metatype="Sensor", natural_key="s1", namespace="umk.demo", attributes={"unit": "K"}
    )
    assert kernel.classify(obj.identity) == "Sensor"


def test_register_object_unknown_metatype_denied():
    kernel = MetaKernel()
    with pytest.raises(MetaTypeUnknownError):
        kernel.register_object(metatype="Nope", natural_key="x", namespace="umk.demo")


def test_discover_by_metatype_namespace_attribute():
    kernel = MetaKernel()
    kernel.register_metatype("Sensor")
    kernel.register_object(
        metatype="Sensor", natural_key="a", namespace="umk.a", attributes={"unit": "K"}
    )
    kernel.register_object(
        metatype="Sensor", natural_key="b", namespace="umk.b", attributes={"unit": "Pa"}
    )
    assert len(kernel.discover(metatype="Sensor")) == 2
    assert len(kernel.discover(metatype="Sensor", namespace="umk.a")) == 1
    assert len(kernel.discover(metatype="Sensor", attribute=("unit", "Pa"))) == 1
    assert len(kernel.discover()) >= 2


def test_evolve_and_trace():
    kernel = MetaKernel()
    kernel.register_metatype("Sensor")
    obj = kernel.register_object(metatype="Sensor", natural_key="a", namespace="umk.a")
    evolved = kernel.evolve(obj.identity, "1.1.0", attributes={"calibrated": True})
    assert evolved.version == Version(1, 1, 0)
    trace = kernel.trace(obj.identity)
    assert trace["versions"] == ["1.0.0", "1.1.0"]


def test_compose_adds_relationship_as_new_version():
    kernel = MetaKernel()
    kernel.register_metatype("Node")
    a = kernel.register_object(metatype="Node", natural_key="a", namespace="umk.g")
    b = kernel.register_object(metatype="Node", natural_key="b", namespace="umk.g")
    composed = kernel.compose(a.identity, "depends-on", b.identity)
    assert composed.version == Version(1, 0, 1)
    assert b.identity in composed.related("depends-on")
    # Composing the same edge again is a no-op (returns current head unchanged).
    assert kernel.compose(a.identity, "depends-on", b.identity).identity == a.identity


def test_govern_without_admitting():
    kernel = MetaKernel()
    from engine.kernel.meta import MetaObject

    candidate = MetaObject(metatype="Unregistered", namespace="ns", natural_key="k")
    decision = kernel.govern(candidate)
    assert decision.allowed is False
    assert not kernel.registry.exists(candidate.identity)


def test_certify_and_describe_and_validate():
    kernel = MetaKernel()
    assert kernel.validate() is True
    cert = kernel.certify()
    assert cert["determination"] == "CERTIFIED"
    desc = kernel.describe()
    assert desc["open_world"] is True
    assert desc["root_metatype"] == "MetaType"


def test_two_kernels_are_deterministically_identical():
    assert MetaKernel().certify()["snapshot_hash"] == MetaKernel().certify()["snapshot_hash"]
