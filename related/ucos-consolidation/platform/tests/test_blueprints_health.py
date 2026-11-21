"""EC2-TASK-000106 — Blueprint health tests (EC2-EPIC-006, OP-C1)."""

from __future__ import annotations

from platform.blueprints.associations import BlueprintAssociationKind, BlueprintAssociationRegistry
from platform.blueprints.contracts import BlueprintFamily, BlueprintStatus
from platform.blueprints.health import (
    INTEGRITY_CHECK,
    PROVENANCE_CHECK,
    REGISTRY_CHECK,
    BlueprintHealth,
    blueprint_health_checks,
)
from platform.blueprints.provenance import BlueprintProvenance, ProvenanceLedger
from platform.blueprints.registry import BlueprintRegistry
from platform.observability.contracts import HealthStatus

import pytest


def _prov(blueprint_ref):
    return BlueprintProvenance.create(
        blueprint_ref=blueprint_ref,
        family=BlueprintFamily.DATA,
        generation_reference="GEN-DATA-001",
        generation_artifact_id="BP-DATA-0001",
        generation_source="05-GENERATION/GEN-DATA-001",
        implementation_target="platform/blueprints",
        content_hash="c0ffee",
    )


def test_health_checks_are_critical():
    checks = blueprint_health_checks()
    names = {c.name for c in checks}
    assert names == {REGISTRY_CHECK, PROVENANCE_CHECK, INTEGRITY_CHECK}
    assert all(c.critical for c in checks)


def test_healthy_when_all_invariants_hold():
    reg = BlueprintRegistry()
    prov = ProvenanceLedger()
    assoc = BlueprintAssociationRegistry()
    bp = reg.create("bp-1", "n", "ws1", "o", BlueprintFamily.DATA)
    reg.transition(bp.blueprint_id, BlueprintStatus.VALIDATED, tick=1)
    reg.transition(bp.blueprint_id, BlueprintStatus.CATALOGUED, tick=2)
    prov.record(_prov(bp.blueprint_id))
    health = BlueprintHealth(reg, prov, assoc)
    assert health.healthy is True
    assert health.probe()[PROVENANCE_CHECK] is HealthStatus.HEALTHY


def test_catalogued_without_provenance_drives_unhealthy():
    reg = BlueprintRegistry()
    prov = ProvenanceLedger()
    assoc = BlueprintAssociationRegistry()
    bp = reg.create("bp-1", "n", "ws1", "o", BlueprintFamily.DATA)
    reg.transition(bp.blueprint_id, BlueprintStatus.VALIDATED, tick=1)
    reg.transition(bp.blueprint_id, BlueprintStatus.CATALOGUED, tick=2)
    health = BlueprintHealth(reg, prov, assoc)
    assert health.uncited_catalogued_blueprints() == (bp.blueprint_id,)
    assert health.probe()[PROVENANCE_CHECK] is HealthStatus.UNHEALTHY
    assert health.healthy is False


def test_orphaned_association_drives_unhealthy():
    reg = BlueprintRegistry()
    prov = ProvenanceLedger()
    assoc = BlueprintAssociationRegistry()
    assoc.add("UCOS-BLPR-orphan", BlueprintAssociationKind.PROJECT, "P-1", tick=1)
    health = BlueprintHealth(reg, prov, assoc)
    assert health.orphaned_association_blueprints() == ("UCOS-BLPR-orphan",)
    assert health.probe()[INTEGRITY_CHECK] is HealthStatus.UNHEALTHY


def test_health_rejects_bad_components():
    reg = BlueprintRegistry()
    prov = ProvenanceLedger()
    assoc = BlueprintAssociationRegistry()
    with pytest.raises(TypeError):
        BlueprintHealth("nope", prov, assoc)  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        BlueprintHealth(reg, "nope", assoc)  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        BlueprintHealth(reg, prov, "nope")  # type: ignore[arg-type]
