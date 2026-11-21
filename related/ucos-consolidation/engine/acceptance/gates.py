"""EPIC-VAL-002 — Repository Acceptance gates (Terminal T3).

An acceptance **gate** is an immutable, deterministic predicate over a
:class:`~engine.acceptance.contracts.RepositorySubject`. Each gate has a stable id,
a severity, and an ``evaluate`` method returning an
:class:`~engine.acceptance.contracts.AcceptanceFinding`. Gates are pure functions of
the subject — no secrets, no registry access, no wall-clock — so identical subjects
yield identical findings.

The built-in suite is the Universal Repository Acceptance framework: it validates,
fail-closed, every acceptance dimension the mission requires —

    context assimilation · repository discovery · constitution discovery ·
    ownership · dependencies · reuse · implementation · validation · certification ·
    registration · traceability · coverage (100%) · zero missing · zero duplication ·
    zero overlap · repository reconciliation · cross-EPIC integration ·
    architecture consistency · repository health · repository freeze readiness.

Every built-in gate is **blocking** (nothing is accepted while a required dimension
is unsatisfied). The architecture is open: callers may supply their own gates
(including advisory ones) to the engine.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, ClassVar

from engine.acceptance.contracts import (
    AcceptanceFinding,
    GateSeverity,
    GateStatus,
    RepositorySubject,
)


class AcceptanceGate(ABC):
    """The common contract for a single acceptance gate (the architecture unit)."""

    gate_id: ClassVar[str]
    severity: ClassVar[GateSeverity]
    description: ClassVar[str] = ""

    @abstractmethod
    def evaluate(self, subject: RepositorySubject) -> AcceptanceFinding:
        """Return a finding for ``subject`` (never raises for a well-formed subject)."""
        raise NotImplementedError  # pragma: no cover

    # -- helpers ---------------------------------------------------------------

    def _passed(self, message: str = "", **details: Any) -> AcceptanceFinding:
        return AcceptanceFinding(
            gate_id=self.gate_id,
            severity=self.severity,
            status=GateStatus.PASS,
            message=message or f"{self.gate_id} satisfied",
            details=details,
        )

    def _failed(self, message: str, **details: Any) -> AcceptanceFinding:
        return AcceptanceFinding(
            gate_id=self.gate_id,
            severity=self.severity,
            status=GateStatus.FAIL,
            message=message,
            details=details,
        )


class ContextAssimilationGate(AcceptanceGate):
    """The acceptance context was assimilated before any determination was made."""

    gate_id = "context-assimilation"
    severity = GateSeverity.BLOCKING
    description = "Repository context was assimilated prior to acceptance."

    def evaluate(self, subject: RepositorySubject) -> AcceptanceFinding:
        if not subject.context_assimilated:
            return self._failed("acceptance context was not assimilated")
        return self._passed()


class RepositoryDiscoveryGate(AcceptanceGate):
    """Repository discovery ran and found at least one repository."""

    gate_id = "repository-discovery"
    severity = GateSeverity.BLOCKING
    description = "At least one repository was discovered."

    def evaluate(self, subject: RepositorySubject) -> AcceptanceFinding:
        if not subject.discovered_repositories:
            return self._failed("no repository was discovered")
        return self._passed(discovered=len(subject.discovered_repositories))


class ConstitutionDiscoveryGate(AcceptanceGate):
    """The governing constitution was discovered for the repository."""

    gate_id = "constitution-discovery"
    severity = GateSeverity.BLOCKING
    description = "The governing constitution was discovered."

    def evaluate(self, subject: RepositorySubject) -> AcceptanceFinding:
        if not subject.constitution_discovered:
            return self._failed("the governing constitution was not discovered")
        return self._passed()


class OwnershipGate(AcceptanceGate):
    """Every implementation unit has a resolved owner (no orphans)."""

    gate_id = "ownership-resolved"
    severity = GateSeverity.BLOCKING
    description = "Every implementation unit has a resolved owner."

    def evaluate(self, subject: RepositorySubject) -> AcceptanceFinding:
        orphans = [u.unit_id for u in subject.units if not u.owner]
        if orphans:
            return self._failed("orphaned units without an owner", orphans=sorted(orphans))
        return self._passed(units=len(subject.units))


class DependenciesGate(AcceptanceGate):
    """Every declared dependency is resolved and digest/version pinned (DE-04)."""

    gate_id = "dependencies-resolved"
    severity = GateSeverity.BLOCKING
    description = "Every dependency is resolved and pinned."

    def evaluate(self, subject: RepositorySubject) -> AcceptanceFinding:
        unresolved = [d.dependency_id for d in subject.dependencies if not d.resolved]
        unpinned = [d.dependency_id for d in subject.dependencies if not d.pinned]
        if unresolved or unpinned:
            return self._failed(
                "dependencies are not fully resolved and pinned",
                unresolved=sorted(unresolved),
                unpinned=sorted(unpinned),
            )
        return self._passed(dependencies=len(subject.dependencies))


class ReuseGate(AcceptanceGate):
    """No capability is an unjustified duplicate (reuse over reinvention, TP-05)."""

    gate_id = "reuse-validated"
    severity = GateSeverity.BLOCKING
    description = "No capability is an unjustified duplicate of an existing one."

    def evaluate(self, subject: RepositorySubject) -> AcceptanceFinding:
        duplicates = [r.capability for r in subject.reuse if r.is_unjustified_duplicate]
        if duplicates:
            return self._failed(
                "unjustified duplicate capabilities detected",
                duplicates=sorted(duplicates),
            )
        return self._passed(capabilities=len(subject.reuse))


class ImplementationGate(AcceptanceGate):
    """The repository has implementation units and every one is implemented."""

    gate_id = "implementation-complete"
    severity = GateSeverity.BLOCKING
    description = "At least one unit exists and every unit is implemented."

    def evaluate(self, subject: RepositorySubject) -> AcceptanceFinding:
        if not subject.units:
            return self._failed("repository has no implementation units")
        incomplete = [u.unit_id for u in subject.units if not u.implemented]
        if incomplete:
            return self._failed("units are not implemented", incomplete=sorted(incomplete))
        return self._passed(units=len(subject.units))


class ValidationGate(AcceptanceGate):
    """Every implementation unit passed validation (EPIC-007)."""

    gate_id = "validation-passed"
    severity = GateSeverity.BLOCKING
    description = "Every unit passed validation."

    def evaluate(self, subject: RepositorySubject) -> AcceptanceFinding:
        unvalidated = [u.unit_id for u in subject.units if not u.validated]
        if unvalidated:
            return self._failed("units did not pass validation", units=sorted(unvalidated))
        return self._passed(units=len(subject.units))


class CertificationGate(AcceptanceGate):
    """Every implementation unit was certified (EPIC-008)."""

    gate_id = "certification-passed"
    severity = GateSeverity.BLOCKING
    description = "Every unit was certified."

    def evaluate(self, subject: RepositorySubject) -> AcceptanceFinding:
        uncertified = [u.unit_id for u in subject.units if not u.certified]
        if uncertified:
            return self._failed("units were not certified", units=sorted(uncertified))
        return self._passed(units=len(subject.units))


class RegistrationGate(AcceptanceGate):
    """Every implementation unit was registered in the registry."""

    gate_id = "registration-complete"
    severity = GateSeverity.BLOCKING
    description = "Every unit was registered."

    def evaluate(self, subject: RepositorySubject) -> AcceptanceFinding:
        unregistered = [u.unit_id for u in subject.units if not u.registered]
        if unregistered:
            return self._failed("units were not registered", units=sorted(unregistered))
        return self._passed(units=len(subject.units))


class TraceabilityGate(AcceptanceGate):
    """Every unit covers the full traceability chain (requirement → certification)."""

    gate_id = "traceability-complete"
    severity = GateSeverity.BLOCKING
    description = "Every unit covers the required traceability stages."

    def evaluate(self, subject: RepositorySubject) -> AcceptanceFinding:
        gaps = {
            u.unit_id: list(u.missing_trace_stages())
            for u in subject.units
            if u.missing_trace_stages()
        }
        if gaps:
            return self._failed("traceability chain is incomplete", gaps=gaps)
        return self._passed(units=len(subject.units))


class CoverageGate(AcceptanceGate):
    """Coverage is 100% across every required dimension (statements … repository)."""

    gate_id = "coverage-complete"
    severity = GateSeverity.BLOCKING
    description = (
        "Coverage is 100% for statements, branches, functions, public API, "
        "exception paths, and the repository."
    )

    def evaluate(self, subject: RepositorySubject) -> AcceptanceFinding:
        coverage = subject.coverage
        missing = coverage.missing_dimensions()
        incomplete = coverage.incomplete_dimensions()
        if missing or incomplete:
            return self._failed(
                "coverage is not 100% across all required dimensions",
                missing_dimensions=list(missing),
                incomplete_dimensions=list(incomplete),
            )
        return self._passed(dimensions=len(coverage.dimensions))


class ZeroMissingGate(AcceptanceGate):
    """Every expected artifact is present (zero missing)."""

    gate_id = "zero-missing"
    severity = GateSeverity.BLOCKING
    description = "Every expected artifact is present."

    def evaluate(self, subject: RepositorySubject) -> AcceptanceFinding:
        missing = subject.inventory.missing()
        if missing:
            return self._failed("expected artifacts are missing", missing=list(missing))
        return self._passed(expected=len(subject.inventory.expected))


class ZeroDuplicationGate(AcceptanceGate):
    """No artifact is duplicated by id or by content (zero duplication)."""

    gate_id = "zero-duplication"
    severity = GateSeverity.BLOCKING
    description = "No artifact is duplicated by id or content."

    def evaluate(self, subject: RepositorySubject) -> AcceptanceFinding:
        duplicates = subject.inventory.duplicates()
        if duplicates:
            return self._failed("duplicate artifacts detected", duplicates=list(duplicates))
        return self._passed(present=len(subject.inventory.present))


class ZeroOverlapGate(AcceptanceGate):
    """No responsibility is owned by more than one artifact (zero overlap)."""

    gate_id = "zero-overlap"
    severity = GateSeverity.BLOCKING
    description = "No responsibility is owned by more than one artifact."

    def evaluate(self, subject: RepositorySubject) -> AcceptanceFinding:
        overlaps = subject.inventory.overlaps()
        if overlaps:
            return self._failed("overlapping responsibilities detected", overlaps=list(overlaps))
        return self._passed()


class RepositoryReconciliationGate(AcceptanceGate):
    """The discovered inventory reconciles with the declared inventory (no extras)."""

    gate_id = "repository-reconciliation"
    severity = GateSeverity.BLOCKING
    description = "Discovered artifacts reconcile with the declared inventory."

    def evaluate(self, subject: RepositorySubject) -> AcceptanceFinding:
        extras = subject.inventory.extras()
        if extras:
            return self._failed(
                "discovered artifacts are not declared in the inventory",
                undeclared=list(extras),
            )
        return self._passed(present=len(subject.inventory.present))


class CrossEpicIntegrationGate(AcceptanceGate):
    """Every declared cross-EPIC integration point is satisfied."""

    gate_id = "cross-epic-integration"
    severity = GateSeverity.BLOCKING
    description = "Every cross-EPIC integration point is satisfied."

    def evaluate(self, subject: RepositorySubject) -> AcceptanceFinding:
        unsatisfied = [i.point for i in subject.integrations if not i.satisfied]
        if unsatisfied:
            return self._failed(
                "cross-EPIC integration points are unsatisfied",
                unsatisfied=sorted(unsatisfied),
            )
        return self._passed(integrations=len(subject.integrations))


class ArchitectureConsistencyGate(AcceptanceGate):
    """The repository has no architecture-consistency violations."""

    gate_id = "architecture-consistency"
    severity = GateSeverity.BLOCKING
    description = "The repository has no architecture-consistency violations."

    def evaluate(self, subject: RepositorySubject) -> AcceptanceFinding:
        if subject.architecture_violations:
            return self._failed(
                "architecture-consistency violations detected",
                violations=list(subject.architecture_violations),
            )
        return self._passed()


class RepositoryHealthGate(AcceptanceGate):
    """The repository has no critical health issues."""

    gate_id = "repository-health"
    severity = GateSeverity.BLOCKING
    description = "The repository has no critical health issues."

    def evaluate(self, subject: RepositorySubject) -> AcceptanceFinding:
        health = subject.health
        if not health.healthy:
            return self._failed(
                "repository has critical health issues",
                critical_issues=list(health.critical_issues),
            )
        return self._passed(warnings=len(health.warnings))


class FreezeReadinessGate(AcceptanceGate):
    """The repository has no outstanding freeze blockers (freeze-ready)."""

    gate_id = "freeze-readiness"
    severity = GateSeverity.BLOCKING
    description = "The repository has no outstanding freeze blockers."

    def evaluate(self, subject: RepositorySubject) -> AcceptanceFinding:
        if subject.freeze_blockers:
            return self._failed(
                "repository is not freeze-ready",
                freeze_blockers=list(subject.freeze_blockers),
            )
        return self._passed()


def default_gates() -> tuple[AcceptanceGate, ...]:
    """Return the built-in acceptance suite, ordered deterministically by id."""
    gates: tuple[AcceptanceGate, ...] = (
        ArchitectureConsistencyGate(),
        CertificationGate(),
        ConstitutionDiscoveryGate(),
        ContextAssimilationGate(),
        CoverageGate(),
        CrossEpicIntegrationGate(),
        DependenciesGate(),
        FreezeReadinessGate(),
        ImplementationGate(),
        OwnershipGate(),
        RegistrationGate(),
        RepositoryDiscoveryGate(),
        RepositoryHealthGate(),
        RepositoryReconciliationGate(),
        ReuseGate(),
        TraceabilityGate(),
        ValidationGate(),
        ZeroDuplicationGate(),
        ZeroMissingGate(),
        ZeroOverlapGate(),
    )
    return tuple(sorted(gates, key=lambda g: g.gate_id))


__all__ = [
    "AcceptanceGate",
    "ContextAssimilationGate",
    "RepositoryDiscoveryGate",
    "ConstitutionDiscoveryGate",
    "OwnershipGate",
    "DependenciesGate",
    "ReuseGate",
    "ImplementationGate",
    "ValidationGate",
    "CertificationGate",
    "RegistrationGate",
    "TraceabilityGate",
    "CoverageGate",
    "ZeroMissingGate",
    "ZeroDuplicationGate",
    "ZeroOverlapGate",
    "RepositoryReconciliationGate",
    "CrossEpicIntegrationGate",
    "ArchitectureConsistencyGate",
    "RepositoryHealthGate",
    "FreezeReadinessGate",
    "default_gates",
]
