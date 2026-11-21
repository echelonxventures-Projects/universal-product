"""EC2-TASK-000102 — Blueprint association-by-reference tests (EC2-EPIC-006)."""

from __future__ import annotations

from platform.blueprints.associations import (
    BlueprintAssociation,
    BlueprintAssociationKind,
    BlueprintAssociationRegistry,
    all_association_kinds,
)
from platform.blueprints.errors import BlueprintAssociationError

import pytest


def test_all_association_kinds_cover_epic006_surface():
    kinds = {k.value for k in all_association_kinds()}
    assert kinds == {
        "workspace",
        "project",
        "request",
        "implementation",
        "artifact",
        "blueprint",
        "generation-artifact",
    }


def test_association_is_content_addressed():
    a = BlueprintAssociation.create("UCOS-BLPR-1", BlueprintAssociationKind.PROJECT, "P-1")
    b = BlueprintAssociation.create("UCOS-BLPR-1", BlueprintAssociationKind.PROJECT, "P-1")
    assert a.association_id == b.association_id
    assert a.association_id.startswith("UCOS-BASC-")
    assert a.to_dict()["kind"] == "project"


@pytest.mark.parametrize(
    "args",
    [
        ("", BlueprintAssociationKind.PROJECT, "r"),
        ("b", "project", "r"),
        ("b", BlueprintAssociationKind.PROJECT, ""),
    ],
)
def test_association_create_rejects_malformed(args):
    with pytest.raises(BlueprintAssociationError):
        BlueprintAssociation.create(*args)  # type: ignore[arg-type]


def test_add_remove_and_query():
    reg = BlueprintAssociationRegistry()
    reg.add("b1", BlueprintAssociationKind.GENERATION_ARTIFACT, "BP-DATA-0001", tick=1)
    reg.add("b1", BlueprintAssociationKind.PROJECT, "P-1", tick=2)
    assert reg.has("b1", BlueprintAssociationKind.PROJECT, "P-1") is True
    assert reg.count_of("b1") == 2
    assert len(reg) == 2
    assert reg.blueprint_ids == ("b1",)
    gen = reg.associations_of_kind("b1", BlueprintAssociationKind.GENERATION_ARTIFACT)
    assert gen[0].ref_id == "BP-DATA-0001"
    removed = reg.remove("b1", BlueprintAssociationKind.PROJECT, "P-1", tick=3)
    assert removed.ref_id == "P-1"
    assert reg.count_of("b1") == 1
    assert len(reg.events) == 3
    assert reg.events[0].action == "added"
    assert reg.events[-1].action == "removed"


def test_duplicate_add_and_absent_remove_fail_closed():
    reg = BlueprintAssociationRegistry()
    reg.add("b1", BlueprintAssociationKind.REQUEST, "R-1", tick=1)
    with pytest.raises(BlueprintAssociationError):
        reg.add("b1", BlueprintAssociationKind.REQUEST, "R-1", tick=2)
    with pytest.raises(BlueprintAssociationError):
        reg.remove("b1", BlueprintAssociationKind.REQUEST, "absent", tick=3)


def test_no_cross_blueprint_leakage():
    reg = BlueprintAssociationRegistry()
    reg.add("b1", BlueprintAssociationKind.BLUEPRINT, "shared", tick=1)
    reg.add("b2", BlueprintAssociationKind.BLUEPRINT, "shared", tick=2)
    ids = {a.association_id for a in reg.associations_of("b1")} | {
        a.association_id for a in reg.associations_of("b2")
    }
    assert len(ids) == 2  # distinct records despite identical ref


def test_registry_fingerprint_is_deterministic():
    def build() -> str:
        reg = BlueprintAssociationRegistry()
        reg.add("b1", BlueprintAssociationKind.PROJECT, "P-1", tick=1)
        return reg.fingerprint()

    assert build() == build()
    assert BlueprintAssociationRegistry().to_dict()["association_count"] == 0


def test_association_and_event_serialisation_fingerprints():
    a = BlueprintAssociation.create("b1", BlueprintAssociationKind.PROJECT, "P-1")
    assert isinstance(a.fingerprint(), str)
    reg = BlueprintAssociationRegistry()
    reg.add("b1", BlueprintAssociationKind.PROJECT, "P-1", tick=1)
    event = reg.events[0]
    assert event.to_dict()["action"] == "added"
    assert reg.associations_of_kind("b1", BlueprintAssociationKind.PROJECT)[0].ref_id == "P-1"
    assert reg.count_of("b1") == 1
