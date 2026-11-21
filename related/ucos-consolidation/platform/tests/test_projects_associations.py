"""EC2-TASK-000092 — Project association tests.

Covers the append-only association-by-reference registry and its referential-integrity
guards: bind/unbind, fail-closed duplicate binding, fail-closed removal of an absent
binding, no cross-project leakage (per-project scoping), per-kind queries, counts, the
append-only AssociationEvent log, and the deterministic fingerprint.
"""

from __future__ import annotations

from platform.projects.associations import AssociationRegistry
from platform.projects.contracts import AssociationKind
from platform.projects.errors import ProjectAssociationError

import pytest


def test_add_binds_reference_and_records_event():
    reg = AssociationRegistry()
    a = reg.add("UCOS-PROJ-1", AssociationKind.BLUEPRINT, "BP-1", tick=1)
    assert a.association_id.startswith("UCOS-PASC-")
    assert reg.has("UCOS-PROJ-1", AssociationKind.BLUEPRINT, "BP-1") is True
    assert len(reg) == 1
    assert reg.events[0].action == "added"
    assert reg.events[0].tick == 1
    assert reg.events[0].to_dict() == {
        "sequence": 0,
        "project_id": "UCOS-PROJ-1",
        "association_id": a.association_id,
        "kind": "blueprint",
        "ref_id": "BP-1",
        "action": "added",
        "tick": 1,
    }


def test_duplicate_binding_is_fail_closed():
    reg = AssociationRegistry()
    reg.add("UCOS-PROJ-1", AssociationKind.BLUEPRINT, "BP-1", tick=1)
    with pytest.raises(ProjectAssociationError):
        reg.add("UCOS-PROJ-1", AssociationKind.BLUEPRINT, "BP-1", tick=2)


def test_remove_unbinds_and_records_event():
    reg = AssociationRegistry()
    reg.add("UCOS-PROJ-1", AssociationKind.REQUEST, "REQ-1", tick=1)
    removed = reg.remove("UCOS-PROJ-1", AssociationKind.REQUEST, "REQ-1", tick=2)
    assert removed.ref_id == "REQ-1"
    assert reg.has("UCOS-PROJ-1", AssociationKind.REQUEST, "REQ-1") is False
    assert reg.events[-1].action == "removed"


def test_remove_absent_is_fail_closed():
    reg = AssociationRegistry()
    with pytest.raises(ProjectAssociationError):
        reg.remove("UCOS-PROJ-1", AssociationKind.ARTIFACT, "ART-1", tick=1)


def test_no_cross_project_leakage():
    reg = AssociationRegistry()
    reg.add("UCOS-PROJ-1", AssociationKind.BLUEPRINT, "BP-1", tick=1)
    reg.add("UCOS-PROJ-2", AssociationKind.BLUEPRINT, "BP-1", tick=2)
    # Same reference, distinct projects → distinct records, per-project scoping.
    assert reg.has("UCOS-PROJ-2", AssociationKind.BLUEPRINT, "BP-1") is True
    assert {a.project_id for a in reg.associations_of("UCOS-PROJ-1")} == {"UCOS-PROJ-1"}
    assert {a.project_id for a in reg.associations_of("UCOS-PROJ-2")} == {"UCOS-PROJ-2"}
    # Removing from one project leaves the other intact.
    reg.remove("UCOS-PROJ-1", AssociationKind.BLUEPRINT, "BP-1", tick=3)
    assert reg.has("UCOS-PROJ-1", AssociationKind.BLUEPRINT, "BP-1") is False
    assert reg.has("UCOS-PROJ-2", AssociationKind.BLUEPRINT, "BP-1") is True


def test_associations_of_kind_and_count():
    reg = AssociationRegistry()
    reg.add("UCOS-PROJ-1", AssociationKind.BLUEPRINT, "BP-1", tick=1)
    reg.add("UCOS-PROJ-1", AssociationKind.BLUEPRINT, "BP-2", tick=2)
    reg.add("UCOS-PROJ-1", AssociationKind.REQUEST, "REQ-1", tick=3)
    assert reg.count_of("UCOS-PROJ-1") == 3
    blueprints = reg.associations_of_kind("UCOS-PROJ-1", AssociationKind.BLUEPRINT)
    assert {a.ref_id for a in blueprints} == {"BP-1", "BP-2"}
    assert reg.count_of("UCOS-PROJ-2") == 0


def test_project_ids_lists_only_projects_with_associations():
    reg = AssociationRegistry()
    reg.add("UCOS-PROJ-1", AssociationKind.BLUEPRINT, "BP-1", tick=1)
    reg.add("UCOS-PROJ-1", AssociationKind.REQUEST, "REQ-1", tick=2)
    reg.remove("UCOS-PROJ-1", AssociationKind.REQUEST, "REQ-1", tick=3)
    assert reg.project_ids == ("UCOS-PROJ-1",)
    reg.remove("UCOS-PROJ-1", AssociationKind.BLUEPRINT, "BP-1", tick=4)
    assert reg.project_ids == ()


def test_associations_of_stable_order():
    reg = AssociationRegistry()
    reg.add("UCOS-PROJ-1", AssociationKind.ARTIFACT, "ART-2", tick=1)
    reg.add("UCOS-PROJ-1", AssociationKind.ARTIFACT, "ART-1", tick=2)
    associations = reg.associations_of("UCOS-PROJ-1")
    assert [a.association_id for a in associations] == sorted(
        a.association_id for a in associations
    )


def test_to_dict_and_fingerprint_deterministic():
    def build() -> str:
        reg = AssociationRegistry()
        reg.add("UCOS-PROJ-1", AssociationKind.BLUEPRINT, "BP-1", tick=1)
        reg.add("UCOS-PROJ-2", AssociationKind.REQUEST, "REQ-1", tick=2)
        return reg.fingerprint()

    assert build() == build()
    reg = AssociationRegistry()
    reg.add("UCOS-PROJ-1", AssociationKind.BLUEPRINT, "BP-1", tick=1)
    assert reg.to_dict()["association_count"] == 1
