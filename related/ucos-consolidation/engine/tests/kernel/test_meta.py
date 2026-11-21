"""Tests for the Universal Meta-Object and the reflective root Meta-Type."""

from __future__ import annotations

import pytest

from engine.foundation.contracts.contract import Version
from engine.kernel.errors import RelationshipError
from engine.kernel.meta import (
    META_TYPE_ROOT,
    MetaObject,
    Relationship,
    make_metatype,
    reflective_root,
)


def test_metaobject_mints_identity_and_defaults_name():
    obj = MetaObject(metatype="Capability", namespace="umk.demo", natural_key="alpha")
    assert obj.identity.startswith("UMK-")
    assert obj.name == "alpha"
    assert obj.version == Version(1, 0, 0)
    assert not obj.is_meta_type


def test_reflective_root_is_self_classifying():
    root = reflective_root()
    assert root.metatype == META_TYPE_ROOT
    assert root.natural_key == META_TYPE_ROOT
    assert root.is_meta_type
    assert root.is_reflective_root


def test_make_metatype_is_a_meta_type():
    mt = make_metatype("Widgetoid", description="a thing")
    assert mt.is_meta_type
    assert not mt.is_reflective_root
    assert mt.attributes["description"] == "a thing"


def test_content_hash_ignores_identity_but_tracks_content():
    a = MetaObject(metatype="T", namespace="ns", natural_key="k", attributes={"x": 1})
    b = MetaObject(metatype="T", namespace="ns", natural_key="k", attributes={"x": 1})
    c = MetaObject(metatype="T", namespace="ns", natural_key="k", attributes={"x": 2})
    assert a.content_hash() == b.content_hash()
    assert a.content_hash() != c.content_hash()


def test_evolve_preserves_identity_changes_version():
    a = MetaObject(metatype="T", namespace="ns", natural_key="k")
    b = a.evolve(Version(1, 1, 0), attributes={"changed": True})
    assert b.identity == a.identity
    assert b.version == Version(1, 1, 0)
    assert b.attributes["changed"] is True


def test_with_relationship_adds_edge_and_is_idempotent():
    a = MetaObject(metatype="T", namespace="ns", natural_key="k")
    b = a.with_relationship("depends-on", "UMK-X-000000000000")
    assert b.related("depends-on") == ("UMK-X-000000000000",)
    # Adding the same edge again returns the same object.
    assert b.with_relationship("depends-on", "UMK-X-000000000000") is b


def test_related_filters_by_relation():
    a = MetaObject(
        metatype="T",
        namespace="ns",
        natural_key="k",
        relationships=(Relationship("a", "T1"), Relationship("b", "T2")),
    )
    assert a.related("a") == ("T1",)
    assert set(a.related()) == {"T1", "T2"}


def test_relationship_validation():
    with pytest.raises(RelationshipError):
        Relationship("rel", "")


def test_relationships_accept_mapping_form():
    obj = MetaObject(
        metatype="T",
        namespace="ns",
        natural_key="k",
        relationships=[{"relation": "r", "target": "X"}],
    )
    assert obj.related("r") == ("X",)


def test_relationships_reject_bad_type():
    with pytest.raises(RelationshipError):
        MetaObject(metatype="T", namespace="ns", natural_key="k", relationships=[42])


def test_to_dict_and_describe():
    obj = make_metatype("Capability")
    d = obj.to_dict()
    assert d["identity"] == obj.identity
    assert d["is_meta_type"] is True
    assert d["content_hash"] == obj.content_hash()
    assert "meta-type" in obj.describe()
