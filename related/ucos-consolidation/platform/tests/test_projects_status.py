"""EC2-TASK-000093 — Project derived-status tests.

Covers the pure derived-status computation (Program §5 "status derivable
deterministically"): the posture derivation across every lifecycle state, per-kind
association counts, the is_associated helper, fail-closed validation, deterministic
fingerprints across independent computations, and serialization.
"""

from __future__ import annotations

from platform.projects.contracts import AssociationKind, Project, ProjectAssociation, ProjectStatus
from platform.projects.errors import ProjectStatusError
from platform.projects.status import DerivedProjectStatus, ProjectPosture, derive_status

import pytest


def _project(status: ProjectStatus = ProjectStatus.ACTIVE) -> Project:
    return Project.create("alpha", "Alpha", "UCOS-WSPC-1", "dev@x").with_status(status)


def _assoc(project_id: str, kind: AssociationKind, ref: str) -> ProjectAssociation:
    return ProjectAssociation.create(project_id, kind, ref)


def test_active_with_no_associations_is_empty():
    ds = derive_status(_project(), [])
    assert ds.posture is ProjectPosture.EMPTY
    assert ds.association_total == 0
    assert ds.is_associated is False
    assert ds.status_id.startswith("UCOS-PDST-")


def test_active_with_associations_is_populated():
    project = _project()
    associations = [
        _assoc(project.project_id, AssociationKind.BLUEPRINT, "BP-1"),
        _assoc(project.project_id, AssociationKind.REQUEST, "REQ-1"),
    ]
    ds = derive_status(project, associations)
    assert ds.posture is ProjectPosture.POPULATED
    assert ds.association_total == 2
    assert ds.is_associated is True


@pytest.mark.parametrize(
    ("status", "posture"),
    [
        (ProjectStatus.SUSPENDED, ProjectPosture.SUSPENDED),
        (ProjectStatus.COMPLETED, ProjectPosture.COMPLETED),
        (ProjectStatus.ARCHIVED, ProjectPosture.ARCHIVED),
    ],
)
def test_lifecycle_dominates_posture(status, posture):
    # Non-active lifecycle states derive their posture regardless of associations.
    project = _project(status)
    associations = [_assoc(project.project_id, AssociationKind.BLUEPRINT, "BP-1")]
    assert derive_status(project, associations).posture is posture


def test_association_counts_cover_every_kind():
    project = _project()
    associations = [
        _assoc(project.project_id, AssociationKind.BLUEPRINT, "BP-1"),
        _assoc(project.project_id, AssociationKind.BLUEPRINT, "BP-2"),
        _assoc(project.project_id, AssociationKind.ARTIFACT, "ART-1"),
    ]
    counts = dict(derive_status(project, associations).association_counts)
    assert counts == {"blueprint": 2, "request": 0, "artifact": 1}


def test_derive_status_is_deterministic_across_computations():
    project = _project()
    associations = [_assoc(project.project_id, AssociationKind.BLUEPRINT, "BP-1")]
    a = derive_status(project, associations)
    b = derive_status(project, list(associations))
    assert a.fingerprint() == b.fingerprint()
    assert a.status_id == b.status_id


def test_derive_status_validation():
    with pytest.raises(ProjectStatusError):
        derive_status("nope", [])  # type: ignore[arg-type]
    with pytest.raises(ProjectStatusError):
        derive_status(_project(), ["nope"])  # type: ignore[list-item]


def test_to_dict_shape():
    ds = derive_status(_project(), [])
    d = ds.to_dict()
    assert d["posture"] == "empty"
    assert d["lifecycle_status"] == "active"
    assert d["association_counts"] == {"blueprint": 0, "request": 0, "artifact": 0}


def test_create_computes_total_from_counts():
    ds = DerivedProjectStatus.create(
        project_id="UCOS-PROJ-1",
        lifecycle_status=ProjectStatus.ACTIVE,
        posture=ProjectPosture.POPULATED,
        association_counts=(("blueprint", 2), ("request", 1), ("artifact", 0)),
    )
    assert ds.association_total == 3
