"""Tests for the open, governed, append-only Universal Registry."""

from __future__ import annotations

import pytest

from engine.foundation.contracts.contract import Version
from engine.kernel.errors import (
    DuplicateRegistrationError,
    KnowledgeOnceViolation,
    MetaTypeUnknownError,
    RegistrationNotFoundError,
    RelationshipError,
    VersionError,
)
from engine.kernel.meta import MetaObject, make_metatype, reflective_root


@pytest.fixture
def registry():
    from engine.kernel.registry import UniversalRegistry

    reg = UniversalRegistry()
    reg.register(reflective_root())
    return reg


def _instance(reg, metatype, key, **attrs):
    return reg.register(
        MetaObject(metatype=metatype, namespace="umk.demo", natural_key=key, attributes=attrs)
    )


def test_register_metatype_then_instance(registry):
    registry.register(make_metatype("Capability"))
    obj = _instance(registry, "Capability", "alpha")
    assert registry.exists(obj.identity)
    assert registry.get(obj.identity).natural_key == "alpha"


def test_instance_without_registered_metatype_is_denied(registry):
    with pytest.raises(MetaTypeUnknownError):
        _instance(registry, "NeverRegistered", "x")


def test_open_world_admits_arbitrary_new_metatype(registry):
    before = len(registry.metatypes())
    registry.register(make_metatype("CompletelyNovelCategory"))
    assert len(registry.metatypes()) == before + 1
    assert "CompletelyNovelCategory" in registry.metatype_keys()


def test_knowledge_once_blocks_identical_body_under_new_identity(registry):
    registry.register(make_metatype("T"))
    first = registry.register(
        MetaObject(
            metatype="T", namespace="ns1", natural_key="k1", name="Same", attributes={"v": 1}
        )
    )
    # A different identity (different natural_key) but an identical knowledge body.
    with pytest.raises(KnowledgeOnceViolation):
        registry.register(
            MetaObject(
                metatype="T", namespace="ns1", natural_key="k2", name="Same", attributes={"v": 1}
            )
        )
    assert registry.content_owner(first.content_hash()) == first.identity


def test_duplicate_identical_content_same_identity_rejected(registry):
    registry.register(make_metatype("T"))
    _instance(registry, "T", "alpha", x=1)
    with pytest.raises(DuplicateRegistrationError):
        registry.register(
            MetaObject(metatype="T", namespace="umk.demo", natural_key="alpha", attributes={"x": 1})
        )


def test_versioning_supersede_and_history(registry):
    registry.register(make_metatype("T"))
    a = _instance(registry, "T", "alpha", x=1)
    v2 = a.evolve(Version(1, 1, 0), attributes={"x": 2})
    registry.register(v2)
    assert registry.get(a.identity).version == Version(1, 1, 0)
    assert len(registry.history(a.identity)) == 2
    assert registry.get_version(a.identity, "1.0.0").attributes["x"] == 1


def test_non_superseding_version_rejected(registry):
    registry.register(make_metatype("T"))
    a = _instance(registry, "T", "alpha", x=1)
    stale = a.evolve(Version(1, 0, 0), attributes={"x": 9})
    # same version -> duplicate content check first? different content, same version.
    with pytest.raises(VersionError):
        registry.register(stale)


def test_resolve_reference_forms(registry):
    registry.register(make_metatype("T"))
    a = _instance(registry, "T", "alpha", x=1)
    assert registry.resolve(a.identity).identity == a.identity
    assert registry.resolve(f"{a.identity}@1.0.0").version == Version(1, 0, 0)


def test_missing_identity_and_version(registry):
    with pytest.raises(RegistrationNotFoundError):
        registry.get("UMK-X-000000000000")
    registry.register(make_metatype("T"))
    a = _instance(registry, "T", "alpha")
    with pytest.raises(RegistrationNotFoundError):
        registry.get_version(a.identity, "9.9.9")


def test_relationship_cycle_denied(registry):
    registry.register(make_metatype("T"))
    a = _instance(registry, "T", "a")
    b = registry.register(
        MetaObject(
            metatype="T",
            namespace="umk.demo",
            natural_key="b",
            relationships=[{"relation": "dep", "target": a.identity}],
        )
    )
    # Now make a depend on b -> cycle.
    cyclic = a.evolve(Version(1, 1, 0)).with_relationship("dep", b.identity)
    with pytest.raises(RelationshipError):
        registry.register(cyclic)


def test_by_metatype_and_instances_and_counts(registry):
    registry.register(make_metatype("T"))
    _instance(registry, "T", "a")
    _instance(registry, "T", "b")
    assert len(registry.by_metatype("T")) == 2
    assert len(registry.instances()) == 2
    assert registry.count() >= 3  # root + metatype + at least instances counted per identity


def test_trace_reports_lineage(registry):
    registry.register(make_metatype("T"))
    a = _instance(registry, "T", "a")
    b = registry.register(
        MetaObject(
            metatype="T",
            namespace="umk.demo",
            natural_key="b",
            relationships=[{"relation": "dep", "target": a.identity}],
        )
    )
    trace = registry.trace(a.identity)
    assert b.identity in trace["relationships_in"]
    trace_b = registry.trace(b.identity)
    assert any(r["target"] == a.identity for r in trace_b["relationships_out"])


def test_audit_chain_verifies_and_snapshot_is_deterministic(registry):
    registry.register(make_metatype("T"))
    _instance(registry, "T", "a")
    assert registry.verify() is True
    assert registry.audit_head != "0" * 64
    assert registry.snapshot_json() == registry.snapshot_json()
    assert len(registry.journal()) == registry.count_versions()
