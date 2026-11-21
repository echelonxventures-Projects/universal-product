"""UCOS-EPIC-013 — Continuous Validation Intelligence analyzers (Terminal T5).

An **analyzer** is an immutable, deterministic reasoner over one intelligence
dimension of an
:class:`~platform.validation_intelligence.contracts.IntelligenceTarget`. Each analyzer
has a stable dimension and an ``analyze`` method returning an ordered tuple of
:class:`~platform.validation_intelligence.contracts.Finding` objects. Analyzers are pure
functions of the target facts — no secrets, no registry access, no wall-clock — so
identical targets yield identical findings.

**Fail-closed** is the mission mandate: an analyzer that cannot *prove* its invariant
holds — because the evidence it needs is absent or malformed — records a FAIL finding,
never PASS and never a swallowed exception. Absence of evidence is never evidence of
correctness.

The built-in suite covers the seven dimensions that expand validation *beyond static
rule execution*:

    * **Cross-capability consistency** — capabilities agree: unique ids, every required
      contract is provided, and no contract has conflicting providers.
    * **Repository completeness** — every required artifact is present, the declared gap
      count is zero, and coverage is complete.
    * **Contract compatibility** — the candidate contract set is backward-compatible with
      the baseline (delegated to the Compatibility Engine).
    * **Architecture compliance** — declared architecture policies are satisfied and no
      change writes to the frozen certified corpus.
    * **Runtime compatibility** — the candidate runtime still provides the required
      interfaces and ABI (delegated to the Compatibility Engine).
    * **Version compatibility** — every inter-component version requirement is satisfied
      (delegated to the Compatibility Engine).
    * **Governance compliance** — declared governance controls are satisfied, authority
      is bounded to engineering execution, and the EC-1 disclosure is present.

The architecture is open: callers may supply their own analyzers to the engine.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Mapping, Sequence
from platform.validation_intelligence.compatibility import CompatibilityEngine
from platform.validation_intelligence.contracts import (
    Finding,
    FindingStatus,
    IntelligenceDimension,
    IntelligenceTarget,
    Severity,
)
from typing import Any, ClassVar

from engine.foundation.guards.frozen_paths import FROZEN_PREFIXES, find_frozen_writes
from engine.runtime.disclosure import disclosure_present

#: The engineering-execution authority a governance-compliant target must not exceed.
_BOUNDED_AUTHORITY = "ENGINEERING-EXECUTION-ONLY"


def _as_sequence(value: Any) -> list[Any] | None:
    """Return ``value`` as a list if it is a non-string sequence, else ``None``."""
    if isinstance(value, Sequence) and not isinstance(value, str | bytes):
        return list(value)
    return None


class DimensionAnalyzer(ABC):
    """The common contract for a single dimension analyzer (the intelligence unit)."""

    dimension: ClassVar[IntelligenceDimension]
    description: ClassVar[str] = ""

    @abstractmethod
    def analyze(self, target: IntelligenceTarget) -> tuple[Finding, ...]:
        """Return the ordered findings for ``target`` (never raises for a valid target)."""
        raise NotImplementedError  # pragma: no cover

    # -- helpers ---------------------------------------------------------------

    def facts(self, target: IntelligenceTarget) -> Mapping[str, Any]:
        return target.dimension_facts(self.dimension)

    def _pass(
        self, check_id: str, message: str, *, severity: Severity = Severity.BLOCKING, **details: Any
    ) -> Finding:
        return Finding(
            check_id=check_id,
            dimension=self.dimension,
            severity=severity,
            status=FindingStatus.PASS,
            message=message,
            details=details,
        )

    def _fail(
        self, check_id: str, message: str, *, severity: Severity = Severity.BLOCKING, **details: Any
    ) -> Finding:
        return Finding(
            check_id=check_id,
            dimension=self.dimension,
            severity=severity,
            status=FindingStatus.FAIL,
            message=message,
            details=details,
        )


# ---------------------------------------------------------------------------
# Cross-capability consistency
# ---------------------------------------------------------------------------
class CrossCapabilityConsistencyAnalyzer(DimensionAnalyzer):
    """Capabilities are mutually consistent: unique ids, satisfied and un-conflicting."""

    dimension = IntelligenceDimension.CROSS_CAPABILITY_CONSISTENCY
    description = (
        "Capability ids are unique, every required contract is provided, and no contract "
        "has conflicting providers."
    )

    def analyze(self, target: IntelligenceTarget) -> tuple[Finding, ...]:
        caps = _as_sequence(self.facts(target).get("capabilities"))
        if not caps:
            return (
                self._fail("cross_capability.capabilities-declared", "no capabilities declared"),
            )
        ids: list[str] = []
        provider_of: dict[str, list[str]] = {}
        required: set[str] = set()
        for cap in caps:
            if not isinstance(cap, Mapping) or not cap.get("id"):
                return (
                    self._fail(
                        "cross_capability.capabilities-declared",
                        "a capability declaration is malformed",
                        capability=cap if isinstance(cap, Mapping) else None,
                    ),
                )
            cap_id = str(cap["id"])
            ids.append(cap_id)
            provides = _as_sequence(cap.get("provides"))
            requires = _as_sequence(cap.get("requires"))
            if provides is None or requires is None:
                return (
                    self._fail(
                        "cross_capability.capabilities-declared",
                        f"capability '{cap_id}' has malformed provides/requires",
                        capability=cap_id,
                    ),
                )
            for contract in provides:
                provider_of.setdefault(str(contract), []).append(cap_id)
            for contract in requires:
                required.add(str(contract))

        findings: list[Finding] = [
            self._pass(
                "cross_capability.capabilities-declared",
                "capabilities are well-formed",
                capabilities=len(caps),
            )
        ]
        findings.append(self._check_unique_ids(ids))
        findings.append(self._check_unique_providers(provider_of))
        findings.append(self._check_requirements_satisfied(required, set(provider_of)))
        return tuple(findings)

    def _check_unique_ids(self, ids: list[str]) -> Finding:
        duplicates = sorted({i for i in ids if ids.count(i) > 1})
        if duplicates:
            return self._fail(
                "cross_capability.ids-unique",
                "capability ids are not unique",
                duplicates=duplicates,
            )
        return self._pass("cross_capability.ids-unique", "capability ids are unique")

    def _check_unique_providers(self, provider_of: dict[str, list[str]]) -> Finding:
        conflicts = {
            contract: sorted(providers)
            for contract, providers in provider_of.items()
            if len(providers) > 1
        }
        if conflicts:
            return self._fail(
                "cross_capability.providers-unique",
                "contracts have conflicting providers",
                conflicts={k: conflicts[k] for k in sorted(conflicts)},
            )
        return self._pass(
            "cross_capability.providers-unique", "every contract has a single provider"
        )

    def _check_requirements_satisfied(self, required: set[str], provided: set[str]) -> Finding:
        dangling = sorted(required - provided)
        if dangling:
            return self._fail(
                "cross_capability.requirements-satisfied",
                "required contracts are provided by no capability",
                dangling=dangling,
            )
        return self._pass(
            "cross_capability.requirements-satisfied", "every required contract is provided"
        )


# ---------------------------------------------------------------------------
# Repository completeness
# ---------------------------------------------------------------------------
class RepositoryCompletenessAnalyzer(DimensionAnalyzer):
    """The repository is complete: artifacts present, zero gaps, coverage complete."""

    dimension = IntelligenceDimension.REPOSITORY_COMPLETENESS
    description = "Every required artifact is present, the gap count is zero, and coverage is full."

    def analyze(self, target: IntelligenceTarget) -> tuple[Finding, ...]:
        facts = self.facts(target)
        return (
            self._check_artifacts(facts.get("required_artifacts")),
            self._check_gaps(facts.get("gaps")),
            self._check_coverage(facts.get("coverage")),
        )

    def _check_artifacts(self, raw: Any) -> Finding:
        artifacts = _as_sequence(raw)
        if not artifacts:
            return self._fail(
                "repository_completeness.artifacts-present", "no required artifacts declared"
            )
        missing: list[str] = []
        for artifact in artifacts:
            if not isinstance(artifact, Mapping) or not artifact.get("id"):
                return self._fail(
                    "repository_completeness.artifacts-present",
                    "a required-artifact declaration is malformed",
                    artifact=artifact if isinstance(artifact, Mapping) else None,
                )
            if not bool(artifact.get("present", False)):
                missing.append(str(artifact["id"]))
        if missing:
            return self._fail(
                "repository_completeness.artifacts-present",
                "required artifacts are missing",
                missing=missing,
            )
        return self._pass(
            "repository_completeness.artifacts-present",
            "every required artifact is present",
            artifacts=len(artifacts),
        )

    def _check_gaps(self, raw: Any) -> Finding:
        if not isinstance(raw, int) or isinstance(raw, bool) or raw < 0:
            return self._fail("repository_completeness.no-gaps", "gap count is absent or malformed")
        if raw > 0:
            return self._fail(
                "repository_completeness.no-gaps", "open completeness gaps remain", gaps=raw
            )
        return self._pass("repository_completeness.no-gaps", "no completeness gaps remain", gaps=0)

    def _check_coverage(self, raw: Any) -> Finding:
        if not isinstance(raw, Mapping):
            return self._fail(
                "repository_completeness.coverage-complete", "coverage is absent or malformed"
            )
        covered = raw.get("covered")
        total = raw.get("total")
        if (
            not isinstance(covered, int)
            or isinstance(covered, bool)
            or not isinstance(total, int)
            or isinstance(total, bool)
            or covered < 0
            or total <= 0
        ):
            return self._fail(
                "repository_completeness.coverage-complete", "coverage counts are malformed"
            )
        if covered < total:
            return self._fail(
                "repository_completeness.coverage-complete",
                "repository coverage is incomplete",
                covered=covered,
                total=total,
            )
        return self._pass(
            "repository_completeness.coverage-complete",
            "repository coverage is complete",
            covered=covered,
            total=total,
        )


# ---------------------------------------------------------------------------
# Architecture compliance
# ---------------------------------------------------------------------------
class ArchitectureComplianceAnalyzer(DimensionAnalyzer):
    """Declared architecture policies are satisfied and the frozen corpus is untouched."""

    dimension = IntelligenceDimension.ARCHITECTURE_COMPLIANCE
    description = (
        "Every architecture policy is satisfied and no change writes to the frozen corpus."
    )

    def analyze(self, target: IntelligenceTarget) -> tuple[Finding, ...]:
        facts = self.facts(target)
        return (
            self._check_policies(facts.get("policies")),
            self._check_frozen(facts.get("changed_paths")),
        )

    def _check_policies(self, raw: Any) -> Finding:
        policies = _as_sequence(raw)
        if not policies:
            return self._fail(
                "architecture_compliance.policies-declared", "no architecture policies declared"
            )
        unmet: list[str] = []
        for policy in policies:
            if not isinstance(policy, Mapping) or not policy.get("id"):
                return self._fail(
                    "architecture_compliance.policies-declared",
                    "an architecture policy is malformed",
                    policy=policy if isinstance(policy, Mapping) else None,
                )
            if not bool(policy.get("compliant", False)):
                unmet.append(str(policy["id"]))
        if unmet:
            return self._fail(
                "architecture_compliance.policies-satisfied",
                "architecture policies are unmet",
                unmet=unmet,
            )
        return self._pass(
            "architecture_compliance.policies-satisfied",
            "every architecture policy is satisfied",
            policies=len(policies),
        )

    def _check_frozen(self, raw: Any) -> Finding:
        changed = _as_sequence(raw)
        if changed is None:
            return self._fail(
                "architecture_compliance.no-frozen-writes", "changed_paths are absent or malformed"
            )
        paths = [str(p) for p in changed]
        violations = find_frozen_writes(paths)
        if violations:
            return self._fail(
                "architecture_compliance.no-frozen-writes",
                "writes to the read-only certified corpus detected",
                violations=violations,
                frozen_prefixes=list(FROZEN_PREFIXES),
            )
        return self._pass(
            "architecture_compliance.no-frozen-writes",
            "no writes to the frozen corpus",
            checked=len(paths),
        )


# ---------------------------------------------------------------------------
# Governance compliance
# ---------------------------------------------------------------------------
class GovernanceComplianceAnalyzer(DimensionAnalyzer):
    """Governance controls are satisfied, authority is bounded, and disclosure is present."""

    dimension = IntelligenceDimension.GOVERNANCE_COMPLIANCE
    description = (
        "Every governance control is satisfied, authority is engineering-execution only, and "
        "the EC-1 provisional-state disclosure is present."
    )

    def analyze(self, target: IntelligenceTarget) -> tuple[Finding, ...]:
        facts = self.facts(target)
        return (
            self._check_controls(facts.get("controls")),
            self._check_authority(facts.get("authority")),
            self._check_disclosure(facts.get("disclosure")),
        )

    def _check_controls(self, raw: Any) -> Finding:
        controls = _as_sequence(raw)
        if not controls:
            return self._fail(
                "governance_compliance.controls-declared", "no governance controls declared"
            )
        unmet: list[str] = []
        for control in controls:
            if not isinstance(control, Mapping) or not control.get("id"):
                return self._fail(
                    "governance_compliance.controls-declared",
                    "a governance control is malformed",
                    control=control if isinstance(control, Mapping) else None,
                )
            if not bool(control.get("satisfied", False)):
                unmet.append(str(control["id"]))
        if unmet:
            return self._fail(
                "governance_compliance.controls-satisfied",
                "governance controls are unmet",
                unmet=unmet,
            )
        return self._pass(
            "governance_compliance.controls-satisfied",
            "every governance control is satisfied",
            controls=len(controls),
        )

    def _check_authority(self, raw: Any) -> Finding:
        if raw != _BOUNDED_AUTHORITY:
            return self._fail(
                "governance_compliance.authority-bounded",
                "asserted authority exceeds engineering execution",
                authority=raw,
                expected=_BOUNDED_AUTHORITY,
            )
        return self._pass(
            "governance_compliance.authority-bounded",
            "authority is bounded to engineering execution",
        )

    def _check_disclosure(self, raw: Any) -> Finding:
        if not disclosure_present(raw if isinstance(raw, dict) else None):
            return self._fail(
                "governance_compliance.disclosure-present",
                "EC-1 provisional-state disclosure is absent or malformed",
            )
        return self._pass(
            "governance_compliance.disclosure-present",
            "EC-1 provisional-state disclosure is present",
            disclosure_id=raw.get("disclosure_id"),
        )


# ---------------------------------------------------------------------------
# Compatibility analyzers (delegate to the Compatibility Engine)
# ---------------------------------------------------------------------------
class ContractCompatibilityAnalyzer(DimensionAnalyzer):
    """The candidate contract set is backward-compatible with the baseline."""

    dimension = IntelligenceDimension.CONTRACT_COMPATIBILITY
    description = "No contract is removed or narrowed without a major bump (Compatibility Engine)."

    __slots__ = ("_engine",)

    def __init__(self, engine: CompatibilityEngine | None = None) -> None:
        self._engine = engine or CompatibilityEngine()

    def analyze(self, target: IntelligenceTarget) -> tuple[Finding, ...]:
        facts = self.facts(target)
        return self._engine.compare_contracts(facts.get("baseline"), facts.get("candidate"))


class RuntimeCompatibilityAnalyzer(DimensionAnalyzer):
    """The candidate runtime still provides the required interfaces and ABI."""

    dimension = IntelligenceDimension.RUNTIME_COMPATIBILITY
    description = "Required runtime interfaces and ABI remain satisfied (Compatibility Engine)."

    __slots__ = ("_engine",)

    def __init__(self, engine: CompatibilityEngine | None = None) -> None:
        self._engine = engine or CompatibilityEngine()

    def analyze(self, target: IntelligenceTarget) -> tuple[Finding, ...]:
        facts = self.facts(target)
        return self._engine.compare_runtime(facts.get("required"), facts.get("provided"))


class VersionCompatibilityAnalyzer(DimensionAnalyzer):
    """Every inter-component version requirement is satisfied."""

    dimension = IntelligenceDimension.VERSION_COMPATIBILITY
    description = "Every declared inter-component version requirement holds (Compatibility Engine)."

    __slots__ = ("_engine",)

    def __init__(self, engine: CompatibilityEngine | None = None) -> None:
        self._engine = engine or CompatibilityEngine()

    def analyze(self, target: IntelligenceTarget) -> tuple[Finding, ...]:
        return self._engine.compare_versions(self.facts(target).get("components"))


# ---------------------------------------------------------------------------
# the built-in suite
# ---------------------------------------------------------------------------
def default_analyzers(
    compatibility_engine: CompatibilityEngine | None = None,
) -> tuple[DimensionAnalyzer, ...]:
    """Return the built-in intelligence suite, ordered by canonical dimension order.

    A single shared :class:`CompatibilityEngine` backs the three compatibility analyzers
    so the suite is composed once and remains deterministic across runs (IMP-007 §5).
    """
    engine = compatibility_engine or CompatibilityEngine()
    analyzers: tuple[DimensionAnalyzer, ...] = (
        CrossCapabilityConsistencyAnalyzer(),
        RepositoryCompletenessAnalyzer(),
        ContractCompatibilityAnalyzer(engine),
        ArchitectureComplianceAnalyzer(),
        RuntimeCompatibilityAnalyzer(engine),
        VersionCompatibilityAnalyzer(engine),
        GovernanceComplianceAnalyzer(),
    )
    return tuple(sorted(analyzers, key=lambda a: a.dimension.order))


__all__ = [
    "DimensionAnalyzer",
    "CrossCapabilityConsistencyAnalyzer",
    "RepositoryCompletenessAnalyzer",
    "ContractCompatibilityAnalyzer",
    "ArchitectureComplianceAnalyzer",
    "RuntimeCompatibilityAnalyzer",
    "VersionCompatibilityAnalyzer",
    "GovernanceComplianceAnalyzer",
    "default_analyzers",
]
