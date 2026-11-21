"""EC2-TASK-000095 — Project health tests.

Covers the deterministic health probe over the project + association registries: both
critical checks are declared, a healthy state reports HEALTHY, and an orphaned
association (a referential-integrity fault) drives the integrity check to UNHEALTHY
(OP-C1 — health under induced fault). Construction is fail-closed.
"""

from __future__ import annotations

from platform.observability.contracts import HealthStatus
from platform.projects.associations import AssociationRegistry
from platform.projects.contracts import AssociationKind
from platform.projects.health import (
    INTEGRITY_CHECK,
    REGISTRY_CHECK,
    ProjectHealth,
    project_health_checks,
)
from platform.projects.registry import ProjectRegistry

import pytest


def test_health_checks_are_declared_and_critical():
    checks = project_health_checks()
    names = {c.name for c in checks}
    assert names == {REGISTRY_CHECK, INTEGRITY_CHECK}
    assert all(c.critical for c in checks)


def test_construction_validation():
    with pytest.raises(TypeError):
        ProjectHealth("nope", AssociationRegistry())  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        ProjectHealth(ProjectRegistry(), "nope")  # type: ignore[arg-type]


def test_healthy_when_all_associations_reference_registered_projects():
    reg = ProjectRegistry()
    assoc = AssociationRegistry()
    project = reg.create("alpha", "Alpha", "UCOS-WSPC-1", "dev@x")
    assoc.add(project.project_id, AssociationKind.BLUEPRINT, "BP-1", tick=1)
    health = ProjectHealth(reg, assoc)
    assert health.orphaned_association_projects() == ()
    assert health.healthy is True
    probe = health.probe()
    assert probe[REGISTRY_CHECK] is HealthStatus.HEALTHY
    assert probe[INTEGRITY_CHECK] is HealthStatus.HEALTHY


def test_orphaned_association_drives_unhealthy():
    reg = ProjectRegistry()
    assoc = AssociationRegistry()
    # Association bound to a project id that is not registered → integrity fault.
    assoc.add("UCOS-PROJ-orphan", AssociationKind.ARTIFACT, "ART-1", tick=1)
    health = ProjectHealth(reg, assoc)
    assert health.orphaned_association_projects() == ("UCOS-PROJ-orphan",)
    assert health.healthy is False
    assert health.probe()[INTEGRITY_CHECK] is HealthStatus.UNHEALTHY
