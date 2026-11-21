"""EC2-TASK-000089 — Project contracts + metadata tests.

Covers the project vocabulary and published contract surface: the ProjectStatus /
AssociationKind / ProjectAction enums, the verb→permission map (Determination §9), the
content-addressed Project and ProjectAssociation records (deterministic ids keyed by
{workspace_id, slug} and {project_id, kind, ref_id}), immutable copy semantics, the
reused WORKSPACE_PROJECT_LIFECYCLE capability group (no new group), the published
PROJECT_CONTRACTS, and the ProjectMetadata value type.
"""

from __future__ import annotations

from platform.foundation.identity import Permission
from platform.identity.contracts import CapabilityGroup
from platform.projects.contracts import (
    MUTATING_ACTIONS,
    PROJECT_CONTRACT_VERSION,
    PROJECT_CONTRACTS,
    PROJECT_GROUP,
    AssociationKind,
    Project,
    ProjectAction,
    ProjectAssociation,
    ProjectStatus,
    all_association_kinds,
    all_project_actions,
    all_project_statuses,
    default_project_contracts,
    permission_for,
    project_contract,
)
from platform.projects.errors import ProjectContractError, ProjectMetadataError
from platform.projects.metadata import EMPTY_METADATA, ProjectMetadata

import pytest

# --------------------------------------------------------------------------- #
# Vocabulary                                                                   #
# --------------------------------------------------------------------------- #


def test_project_group_is_the_reused_capability_group():
    # EPIC-005 introduces NO new capability group — it reuses matrix index 3.
    assert PROJECT_GROUP is CapabilityGroup.WORKSPACE_PROJECT_LIFECYCLE


def test_all_project_statuses_stable_order():
    assert all_project_statuses() == (
        ProjectStatus.ACTIVE,
        ProjectStatus.SUSPENDED,
        ProjectStatus.COMPLETED,
        ProjectStatus.ARCHIVED,
    )


def test_all_association_kinds_are_the_three_downstream_seams():
    assert all_association_kinds() == (
        AssociationKind.BLUEPRINT,
        AssociationKind.REQUEST,
        AssociationKind.ARTIFACT,
    )


def test_all_project_actions_present():
    assert set(all_project_actions()) == set(ProjectAction)


@pytest.mark.parametrize(
    ("action", "permission"),
    [
        (ProjectAction.CREATE_PROJECT, Permission.CREATE),
        (ProjectAction.INSPECT, Permission.READ),
        (ProjectAction.DISCOVER, Permission.READ),
        (ProjectAction.SEARCH, Permission.READ),
        (ProjectAction.TRANSITION_LIFECYCLE, Permission.CREATE),
        (ProjectAction.ADD_ASSOCIATION, Permission.CREATE),
        (ProjectAction.REMOVE_ASSOCIATION, Permission.CREATE),
    ],
)
def test_verb_to_permission_map(action, permission):
    assert permission_for(action) is permission


def test_permission_for_rejects_non_action():
    with pytest.raises(ProjectContractError):
        permission_for("create")  # type: ignore[arg-type]


def test_mutating_actions_membership():
    assert ProjectAction.CREATE_PROJECT in MUTATING_ACTIONS
    assert ProjectAction.ADD_ASSOCIATION in MUTATING_ACTIONS
    assert ProjectAction.REMOVE_ASSOCIATION in MUTATING_ACTIONS
    assert ProjectAction.TRANSITION_LIFECYCLE in MUTATING_ACTIONS
    assert ProjectAction.INSPECT not in MUTATING_ACTIONS
    assert ProjectAction.SEARCH not in MUTATING_ACTIONS


# --------------------------------------------------------------------------- #
# Project record                                                               #
# --------------------------------------------------------------------------- #


def test_project_id_is_content_addressed_and_deterministic():
    a = Project.create("Alpha", "Alpha", "UCOS-WSPC-1", "dev@x")
    b = Project.create("alpha", "Different Name", "UCOS-WSPC-1", "other@x")
    # id keyed only by normalized slug + workspace_id
    assert a.project_id == b.project_id
    assert a.project_id.startswith("UCOS-PROJ-")
    assert a.slug == "alpha"


def test_project_id_differs_across_workspaces():
    a = Project.create("alpha", "Alpha", "UCOS-WSPC-1", "dev@x")
    b = Project.create("alpha", "Alpha", "UCOS-WSPC-2", "dev@x")
    assert a.project_id != b.project_id


def test_project_created_active_by_default():
    p = Project.create("alpha", "Alpha", "UCOS-WSPC-1", "dev@x")
    assert p.status is ProjectStatus.ACTIVE
    assert p.is_active is True
    assert p.is_terminal is False


@pytest.mark.parametrize(
    ("slug", "name", "workspace_id", "owner"),
    [
        ("", "n", "w", "o"),
        ("  ", "n", "w", "o"),
        ("a b", "n", "w", "o"),
        ("alpha", "", "w", "o"),
        ("alpha", "n", "", "o"),
        ("alpha", "n", "w", ""),
    ],
)
def test_project_create_validation(slug, name, workspace_id, owner):
    with pytest.raises(ProjectContractError):
        Project.create(slug, name, workspace_id, owner)


def test_project_create_rejects_bad_status_and_metadata():
    with pytest.raises(ProjectContractError):
        Project.create("a", "n", "w", "o", status="active")  # type: ignore[arg-type]
    with pytest.raises(ProjectContractError):
        Project.create("a", "n", "w", "o", metadata="md")  # type: ignore[arg-type]


def test_with_status_preserves_id_and_validates():
    p = Project.create("alpha", "Alpha", "UCOS-WSPC-1", "dev@x")
    updated = p.with_status(ProjectStatus.COMPLETED)
    assert updated.project_id == p.project_id
    assert updated.status is ProjectStatus.COMPLETED
    with pytest.raises(ProjectContractError):
        p.with_status("completed")  # type: ignore[arg-type]


def test_with_metadata_preserves_id_and_validates():
    md = ProjectMetadata.create(description="d", labels=["x"])
    p = Project.create("alpha", "Alpha", "UCOS-WSPC-1", "dev@x")
    updated = p.with_metadata(md)
    assert updated.project_id == p.project_id
    assert updated.metadata.description == "d"
    with pytest.raises(ProjectContractError):
        p.with_metadata("md")  # type: ignore[arg-type]


def test_project_to_dict_and_fingerprint_roundtrip():
    p = Project.create("alpha", "Alpha", "UCOS-WSPC-1", "dev@x", tenant="acme")
    d = p.to_dict()
    assert d["project_id"] == p.project_id
    assert d["workspace_id"] == "UCOS-WSPC-1"
    assert d["tenant"] == "acme"
    assert d["status"] == "active"
    assert (
        p.fingerprint()
        == Project.create("alpha", "Alpha", "UCOS-WSPC-1", "dev@x", tenant="acme").fingerprint()
    )


# --------------------------------------------------------------------------- #
# ProjectAssociation record                                                    #
# --------------------------------------------------------------------------- #


def test_association_id_is_content_addressed():
    a = ProjectAssociation.create("UCOS-PROJ-1", AssociationKind.BLUEPRINT, "BP-1")
    b = ProjectAssociation.create("UCOS-PROJ-1", AssociationKind.BLUEPRINT, "BP-1")
    assert a.association_id == b.association_id
    assert a.association_id.startswith("UCOS-PASC-")


def test_association_id_differs_by_project_kind_ref():
    base = ProjectAssociation.create("UCOS-PROJ-1", AssociationKind.BLUEPRINT, "BP-1")
    assert (
        base.association_id
        != ProjectAssociation.create(
            "UCOS-PROJ-2", AssociationKind.BLUEPRINT, "BP-1"
        ).association_id
    )
    assert (
        base.association_id
        != ProjectAssociation.create("UCOS-PROJ-1", AssociationKind.REQUEST, "BP-1").association_id
    )
    assert (
        base.association_id
        != ProjectAssociation.create(
            "UCOS-PROJ-1", AssociationKind.BLUEPRINT, "BP-2"
        ).association_id
    )


@pytest.mark.parametrize(
    ("project_id", "kind", "ref_id"),
    [
        ("", AssociationKind.BLUEPRINT, "r"),
        ("p", "blueprint", "r"),
        ("p", AssociationKind.BLUEPRINT, ""),
    ],
)
def test_association_create_validation(project_id, kind, ref_id):
    with pytest.raises(ProjectContractError):
        ProjectAssociation.create(project_id, kind, ref_id)


def test_association_to_dict_and_fingerprint():
    a = ProjectAssociation.create("UCOS-PROJ-1", AssociationKind.ARTIFACT, "ART-9")
    d = a.to_dict()
    assert d["kind"] == "artifact"
    assert d["ref_id"] == "ART-9"
    assert a.fingerprint() == a.fingerprint()


# --------------------------------------------------------------------------- #
# Published contract surface                                                   #
# --------------------------------------------------------------------------- #


def test_published_contracts_versioned():
    assert len(PROJECT_CONTRACTS) == 6
    assert all(ref.version == PROJECT_CONTRACT_VERSION for ref in PROJECT_CONTRACTS)
    names = {ref.name for ref in PROJECT_CONTRACTS}
    assert "projects.associations.bind" in names
    assert "projects.runtime.service" in names


def test_default_project_contracts_are_concrete():
    contracts = default_project_contracts()
    assert len(contracts) == len(PROJECT_CONTRACTS)
    assert {c.name for c in contracts} == {ref.name for ref in PROJECT_CONTRACTS}


def test_project_contract_builder_validates():
    contract = project_contract("projects.registry.registry", "desc")
    assert contract.name == "projects.registry.registry"
    with pytest.raises(ProjectContractError):
        project_contract("")


# --------------------------------------------------------------------------- #
# Metadata                                                                     #
# --------------------------------------------------------------------------- #


def test_metadata_create_normalizes_and_is_deterministic():
    md = ProjectMetadata.create(description="d", labels=["a", "b"], annotations={"k": "v"})
    assert md.has_label("a")
    assert md.to_dict()["labels"] == ["a", "b"]
    assert (
        md.fingerprint()
        == ProjectMetadata.create(
            description="d", labels=["b", "a"], annotations={"k": "v"}
        ).fingerprint()
    )


def test_metadata_empty_default():
    assert EMPTY_METADATA.description == ""
    assert EMPTY_METADATA.labels == frozenset()


@pytest.mark.parametrize(
    "kwargs",
    [
        {"description": 5},
        {"labels": [""]},
        {"annotations": {"": "v"}},
        {"annotations": {"k": ""}},
    ],
)
def test_metadata_validation(kwargs):
    with pytest.raises(ProjectMetadataError):
        ProjectMetadata.create(**kwargs)
