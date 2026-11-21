"""EPIC-VAL-002 — Repository Acceptance gate tests.

Every built-in gate passes over the golden ``valid_subject`` and fails when its own
dimension is mutated — proving each gate is an independent, falsifiable predicate.
"""

from __future__ import annotations

from engine.acceptance.contracts import (
    CoverageDimension,
    CoverageProfile,
    DependencyRecord,
    IntegrationRecord,
    RepositoryHealth,
    RepositoryInventory,
    ReuseRecord,
    UnitRecord,
)
from engine.acceptance.gates import (
    ArchitectureConsistencyGate,
    CertificationGate,
    ConstitutionDiscoveryGate,
    ContextAssimilationGate,
    CoverageGate,
    CrossEpicIntegrationGate,
    DependenciesGate,
    FreezeReadinessGate,
    ImplementationGate,
    OwnershipGate,
    RegistrationGate,
    RepositoryDiscoveryGate,
    RepositoryHealthGate,
    RepositoryReconciliationGate,
    ReuseGate,
    TraceabilityGate,
    ValidationGate,
    ZeroDuplicationGate,
    ZeroMissingGate,
    ZeroOverlapGate,
    default_gates,
)

from .conftest import mutate


def test_default_gates_are_sorted_and_complete():
    gates = default_gates()
    ids = [g.gate_id for g in gates]
    assert ids == sorted(ids)
    assert len(gates) == 20


# -- every gate passes on the golden subject ---------------------------------
ALL_GATES = [
    ArchitectureConsistencyGate,
    CertificationGate,
    ConstitutionDiscoveryGate,
    ContextAssimilationGate,
    CoverageGate,
    CrossEpicIntegrationGate,
    DependenciesGate,
    FreezeReadinessGate,
    ImplementationGate,
    OwnershipGate,
    RegistrationGate,
    RepositoryDiscoveryGate,
    RepositoryHealthGate,
    RepositoryReconciliationGate,
    ReuseGate,
    TraceabilityGate,
    ValidationGate,
    ZeroDuplicationGate,
    ZeroMissingGate,
    ZeroOverlapGate,
]


def test_all_gates_pass_on_valid_subject(valid_subject):
    for gate_cls in ALL_GATES:
        finding = gate_cls().evaluate(valid_subject)
        assert finding.passed, f"{gate_cls.__name__} unexpectedly failed"


# -- each gate fails when its dimension is broken ----------------------------
def test_context_assimilation_fails(valid_subject):
    finding = ContextAssimilationGate().evaluate(mutate(valid_subject, context_assimilated=False))
    assert finding.is_blocking_failure


def test_repository_discovery_fails(valid_subject):
    finding = RepositoryDiscoveryGate().evaluate(mutate(valid_subject, discovered_repositories=()))
    assert finding.is_blocking_failure


def test_constitution_discovery_fails(valid_subject):
    finding = ConstitutionDiscoveryGate().evaluate(
        mutate(valid_subject, constitution_discovered=False)
    )
    assert finding.is_blocking_failure


def test_ownership_fails_on_orphan(valid_subject):
    orphan = (UnitRecord("ORPH", owner=None, implemented=True),)
    finding = OwnershipGate().evaluate(mutate(valid_subject, units=orphan))
    assert finding.is_blocking_failure
    assert "ORPH" in finding.details["orphans"]


def test_dependencies_fails_when_unresolved_or_unpinned(valid_subject):
    deps = (DependencyRecord("D", resolved=False, pinned=False),)
    finding = DependenciesGate().evaluate(mutate(valid_subject, dependencies=deps))
    assert finding.is_blocking_failure
    assert "D" in finding.details["unresolved"]


def test_reuse_fails_on_unjustified_duplicate(valid_subject):
    reuse = (ReuseRecord("dup", reused=False, justified=False),)
    finding = ReuseGate().evaluate(mutate(valid_subject, reuse=reuse))
    assert finding.is_blocking_failure
    assert "dup" in finding.details["duplicates"]


def test_implementation_fails_when_empty(valid_subject):
    finding = ImplementationGate().evaluate(mutate(valid_subject, units=()))
    assert finding.is_blocking_failure


def test_implementation_fails_when_unimplemented(valid_subject):
    units = (UnitRecord("U", owner="o", implemented=False),)
    finding = ImplementationGate().evaluate(mutate(valid_subject, units=units))
    assert finding.is_blocking_failure
    assert "U" in finding.details["incomplete"]


def test_validation_fails(valid_subject):
    units = (UnitRecord("U", owner="o", implemented=True, validated=False),)
    finding = ValidationGate().evaluate(mutate(valid_subject, units=units))
    assert finding.is_blocking_failure


def test_certification_fails(valid_subject):
    units = (UnitRecord("U", owner="o", validated=True, certified=False),)
    finding = CertificationGate().evaluate(mutate(valid_subject, units=units))
    assert finding.is_blocking_failure


def test_registration_fails(valid_subject):
    units = (UnitRecord("U", owner="o", certified=True, registered=False),)
    finding = RegistrationGate().evaluate(mutate(valid_subject, units=units))
    assert finding.is_blocking_failure


def test_traceability_fails(valid_subject):
    units = (UnitRecord("U", owner="o", traceability=("requirement",)),)
    finding = TraceabilityGate().evaluate(mutate(valid_subject, units=units))
    assert finding.is_blocking_failure
    assert "U" in finding.details["gaps"]


def test_coverage_fails_when_incomplete(valid_subject):
    profile = CoverageProfile(
        dimensions=tuple(CoverageDimension(n, 1, 2) for n in CoverageProfile.REQUIRED)
    )
    finding = CoverageGate().evaluate(mutate(valid_subject, coverage=profile))
    assert finding.is_blocking_failure
    assert finding.details["incomplete_dimensions"]


def test_coverage_fails_when_dimension_missing(valid_subject):
    profile = CoverageProfile(dimensions=(CoverageDimension("statements", 1, 1),))
    finding = CoverageGate().evaluate(mutate(valid_subject, coverage=profile))
    assert finding.is_blocking_failure
    assert "branches" in finding.details["missing_dimensions"]


def test_zero_missing_fails(valid_subject):
    inv = RepositoryInventory(expected=("A", "B"), present=("A",))
    finding = ZeroMissingGate().evaluate(mutate(valid_subject, inventory=inv))
    assert finding.is_blocking_failure
    assert "B" in finding.details["missing"]


def test_zero_duplication_fails(valid_subject):
    inv = RepositoryInventory(present=("A", "A"))
    finding = ZeroDuplicationGate().evaluate(mutate(valid_subject, inventory=inv))
    assert finding.is_blocking_failure
    assert "A" in finding.details["duplicates"]


def test_zero_overlap_fails(valid_subject):
    inv = RepositoryInventory(responsibilities={"r": ("A", "B")})
    finding = ZeroOverlapGate().evaluate(mutate(valid_subject, inventory=inv))
    assert finding.is_blocking_failure
    assert "r" in finding.details["overlaps"]


def test_reconciliation_fails_on_undeclared(valid_subject):
    inv = RepositoryInventory(expected=("A",), present=("A", "X"))
    finding = RepositoryReconciliationGate().evaluate(mutate(valid_subject, inventory=inv))
    assert finding.is_blocking_failure
    assert "X" in finding.details["undeclared"]


def test_cross_epic_integration_fails(valid_subject):
    integrations = (IntegrationRecord("p", satisfied=False),)
    finding = CrossEpicIntegrationGate().evaluate(mutate(valid_subject, integrations=integrations))
    assert finding.is_blocking_failure
    assert "p" in finding.details["unsatisfied"]


def test_architecture_consistency_fails(valid_subject):
    finding = ArchitectureConsistencyGate().evaluate(
        mutate(valid_subject, architecture_violations=("layering",))
    )
    assert finding.is_blocking_failure
    assert "layering" in finding.details["violations"]


def test_repository_health_fails(valid_subject):
    health = RepositoryHealth(critical_issues=("data-loss",))
    finding = RepositoryHealthGate().evaluate(mutate(valid_subject, health=health))
    assert finding.is_blocking_failure
    assert "data-loss" in finding.details["critical_issues"]


def test_freeze_readiness_fails(valid_subject):
    finding = FreezeReadinessGate().evaluate(mutate(valid_subject, freeze_blockers=("open-pr",)))
    assert finding.is_blocking_failure
    assert "open-pr" in finding.details["freeze_blockers"]
