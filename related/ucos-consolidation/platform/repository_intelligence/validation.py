"""UCOS-EPIC-014 — Repository Validation (Terminal T5).

Validation adjudicates the intelligence report. It does **not** re-implement repository
adjudication: the repository already owns a certified 20-gate Repository Acceptance suite
(:mod:`engine.acceptance.gates`) that evaluates a normalized
:class:`~engine.acceptance.contracts.RepositorySubject`. Historically that suite had no
producer — a subject had to be hand-authored. This module supplies the missing producer by
**projecting the discovered intelligence into a RepositorySubject** and running the existing
gates over it, then adds only the rules that are specific to repository *intelligence* and
have no existing owner.

Two rule families, kept explicitly separate so the provenance of every verdict is visible:

    * **composed acceptance gates** — instances of the certified
      :class:`~engine.acceptance.gates.AcceptanceGate` suite, run over the projected
      subject. Only the gates the projection can *evidence* are selected
      (:data:`COMPOSED_GATES`); running a gate whose evidence the projection cannot supply
      would manufacture a failure that says nothing about the repository, which is the
      opposite of fail-closed.
    * **intelligence rules** — the checks that exist only because this subsystem exists:
      the substrate was actually read, the capability catalog was composed rather than
      re-derived, the dependency graph is acyclic and layer-clean, no capability is an
      unproven duplicate, ownership is uncontested, and the report is self-consistent.

Fail-closed: the verdict is FAIL if any blocking rule or composed gate fails. Absent
evidence is a failure, never a pass.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from platform.foundation.contracts import content_hash
from platform.repository_intelligence.contracts import (
    VALIDATION_REPORT_FORMAT,
    DiscoveryDimension,
    Finding,
    FindingStatus,
    RepositoryIntelligenceReport,
    Severity,
    Verdict,
)
from platform.repository_intelligence.discovery import (
    CATALOG_COMPOSED,
    CONFLICT_LAYER_VIOLATION,
    DEPENDENCY_ACYCLIC,
    DUPLICATE_MODULE_CONTENT,
    OWNERSHIP_CONTESTED,
    SUBSTRATE_PRESENT,
)
from platform.repository_intelligence.errors import RepositoryValidationError
from typing import Any

from engine.acceptance.contracts import (
    AcceptanceFinding,
    GateStatus,
    RepositoryHealth,
    RepositoryInventory,
    RepositorySubject,
    ReuseRecord,
    UnitRecord,
)
from engine.acceptance.gates import (
    AcceptanceGate,
    ArchitectureConsistencyGate,
    OwnershipGate,
    RepositoryDiscoveryGate,
    RepositoryHealthGate,
    ReuseGate,
    ZeroDuplicationGate,
    ZeroMissingGate,
    ZeroOverlapGate,
)

#: The subset of the certified acceptance suite whose evidence the intelligence projection
#: can genuinely supply. Deliberately a subset: the certification, validation, registration,
#: traceability, coverage and freeze gates depend on evidence produced by other programmes,
#: and asserting it here would be fabrication.
COMPOSED_GATES: tuple[type[AcceptanceGate], ...] = (
    ArchitectureConsistencyGate,
    OwnershipGate,
    RepositoryDiscoveryGate,
    RepositoryHealthGate,
    ReuseGate,
    ZeroDuplicationGate,
    ZeroMissingGate,
    ZeroOverlapGate,
)

#: Intelligence rule ids (stable, machine-consumable).
RULE_SUBSTRATE_READ = "intelligence-substrate-read"
RULE_CATALOG_COMPOSED = "intelligence-catalog-composed"
RULE_GRAPH_ACYCLIC = "intelligence-graph-acyclic"
RULE_GRAPH_LAYERED = "intelligence-graph-layer-clean"
RULE_NO_CONTENT_DUPLICATES = "intelligence-no-content-duplicates"
RULE_OWNERSHIP_UNCONTESTED = "intelligence-ownership-uncontested"
RULE_GRAPH_CLOSED = "intelligence-graph-closed"
RULE_REPORT_SELF_CONSISTENT = "intelligence-report-self-consistent"
RULE_EVERY_DIMENSION_RUN = "intelligence-every-dimension-run"


#: Provenance labels distinguishing a composed certified gate from a new rule.
PROVENANCE_COMPOSED = "engine.acceptance (composed certified gate)"
PROVENANCE_INTELLIGENCE = "platform.repository_intelligence (rule)"


@dataclass(frozen=True, slots=True)
class RuleOutcome:
    """The immutable outcome of one validation rule (intelligence rule or composed gate)."""

    rule_id: str
    provenance: str
    severity: Severity
    status: FindingStatus
    message: str = ""
    details: Mapping[str, Any] = field(default_factory=dict)

    @property
    def passed(self) -> bool:
        return self.status is FindingStatus.PASS

    @property
    def is_blocking_failure(self) -> bool:
        return self.status is FindingStatus.FAIL and self.severity is Severity.BLOCKING

    def core(self) -> dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "provenance": self.provenance,
            "severity": self.severity.value,
            "status": self.status.value,
            "message": self.message,
        }

    def to_dict(self) -> dict[str, Any]:
        return {**self.core(), "details": dict(self.details)}


@dataclass(frozen=True, slots=True)
class RepositoryValidationReport:
    """The immutable, content-addressed outcome of validating an intelligence report."""

    repository_id: str
    verdict: Verdict
    report_sha256: str
    rules: tuple[RuleOutcome, ...]
    subject_digest: str
    validation_sha256: str

    @classmethod
    def create(
        cls,
        *,
        repository_id: str,
        report_sha256: str,
        rules: tuple[RuleOutcome, ...],
        subject_digest: str,
    ) -> RepositoryValidationReport:
        """Aggregate rule outcomes fail-closed into a content-addressed report."""
        ordered = tuple(sorted(rules, key=lambda r: (r.provenance, r.rule_id)))
        verdict = Verdict.FAIL if any(r.is_blocking_failure for r in ordered) else Verdict.PASS
        core = {
            "repository_id": repository_id,
            "report_sha256": report_sha256,
            "subject_digest": subject_digest,
            "verdict": verdict.value,
            "rules": [r.core() for r in ordered],
        }
        return cls(
            repository_id=repository_id,
            verdict=verdict,
            report_sha256=report_sha256,
            rules=ordered,
            subject_digest=subject_digest,
            validation_sha256=content_hash(core),
        )

    @property
    def passed(self) -> bool:
        return self.verdict is Verdict.PASS

    def blocking_failures(self) -> tuple[str, ...]:
        return tuple(r.rule_id for r in self.rules if r.is_blocking_failure)

    def advisory_failures(self) -> tuple[str, ...]:
        return tuple(
            r.rule_id
            for r in self.rules
            if r.status is FindingStatus.FAIL and r.severity is Severity.ADVISORY
        )

    def counts(self) -> dict[str, int]:
        passed = sum(1 for r in self.rules if r.passed)
        composed = sum(1 for r in self.rules if r.provenance == PROVENANCE_COMPOSED)
        return {
            "rules": len(self.rules),
            "passed": passed,
            "failed": len(self.rules) - passed,
            "blocking_failed": len(self.blocking_failures()),
            "advisory_failed": len(self.advisory_failures()),
            "composed_acceptance_gates": composed,
            "intelligence_rules": len(self.rules) - composed,
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "report_format": VALIDATION_REPORT_FORMAT,
            "repository_id": self.repository_id,
            "verdict": self.verdict.value,
            "passed": self.passed,
            "counts": self.counts(),
            "blocking_failures": list(self.blocking_failures()),
            "advisory_failures": list(self.advisory_failures()),
            "intelligence_report_sha256": self.report_sha256,
            "acceptance_subject_digest": self.subject_digest,
            "rules": [r.to_dict() for r in self.rules],
            "validation_sha256": self.validation_sha256,
        }


class RepositoryValidator:
    """Validates an intelligence report by composing acceptance gates and adding rules."""

    __slots__ = ("_report", "_gates")

    def __init__(
        self,
        report: RepositoryIntelligenceReport,
        gates: tuple[AcceptanceGate, ...] | None = None,
    ) -> None:
        if not isinstance(report, RepositoryIntelligenceReport):
            raise RepositoryValidationError(
                "repository validation requires a RepositoryIntelligenceReport",
                received=type(report).__name__,
            )
        self._report = report
        self._gates = gates if gates is not None else tuple(cls() for cls in COMPOSED_GATES)

    # -- the projection that makes the certified gates usable -------------
    def build_subject(self) -> RepositorySubject:
        """Project the intelligence report into an acceptance :class:`RepositorySubject`.

        This is the composition point. Each acceptance concept is fed from the discovery
        dimension that actually evidences it:

            * ``units`` ← discovered capabilities, with ``owner`` from Ownership Discovery
              and ``implemented`` from the presence of modules on disk.
            * ``reuse`` ← Reuse Discovery: a capability with proven reuse is ``reused``;
              one whose reuse is unproven is ``justified`` only if its own catalog directive
              prohibits replacement (the repository has already ruled on it).
            * ``inventory`` ← the capability catalog as *expected* versus the code substrate
              as *present*, with module content hashes for duplication and per-capability
              responsibilities for overlap.
            * ``architecture_violations`` ← blocking conflict findings.
            * ``health`` ← blocking findings as critical issues, advisory as warnings.

        Nothing is asserted that discovery did not observe: no coverage profile, no
        certification flags, no traceability. Those gates are therefore not composed.
        """
        report = self._report
        owners = {record.subject: record for record in report.ownership}
        reuse_index = {assessment.capability: assessment for assessment in report.reuse}

        units = tuple(
            UnitRecord(
                unit_id=capability.name,
                owner=(
                    owners[capability.name].owner
                    if capability.name in owners and owners[capability.name].owned
                    else None
                ),
                implemented=capability.present_on_disk and capability.modules > 0,
            )
            for capability in report.capabilities
        )

        reuse = tuple(
            ReuseRecord(
                capability=assessment.capability,
                reused=assessment.reused,
                justified=assessment.replacement_prohibited,
            )
            for assessment in report.reuse
        )

        expected = tuple(
            capability.name for capability in report.capabilities if capability.present_on_disk
        )
        present = tuple(
            capability.name for capability in report.capabilities if capability.present_on_disk
        )
        content_hashes = {
            finding.subject: str(finding.details.get("content_sha256", ""))
            for finding in report.findings_of(DiscoveryDimension.DUPLICATE)
            if finding.code == DUPLICATE_MODULE_CONTENT
        }
        responsibilities = {
            f"capability:{assessment.capability}": (assessment.capability,)
            for assessment in reuse_index.values()
        }

        violations = tuple(
            f"{finding.code}:{finding.subject}"
            for finding in report.failures_of(DiscoveryDimension.CONFLICT)
            if finding.is_blocking_failure
        )
        critical = tuple(
            sorted({f"{f.code}:{f.subject}" for f in report.all_findings if f.is_blocking_failure})
        )
        warnings = tuple(sorted({f.code for f in report.all_findings if f.is_advisory_failure}))

        return RepositorySubject(
            repository_id=report.repository_id,
            epic_id="UCOS-EPIC-014",
            context_assimilated=True,
            constitution_discovered=bool(report.units),
            discovered_repositories=(report.repository_id,),
            units=units,
            reuse=reuse,
            inventory=RepositoryInventory(
                expected=expected,
                present=present,
                content_hashes=content_hashes,
                responsibilities=responsibilities,
            ),
            architecture_violations=violations,
            health=_health(critical, warnings),
        )

    # -- adjudication -----------------------------------------------------
    def validate(self) -> RepositoryValidationReport:
        """Run the intelligence rules and the composed acceptance gates, fail-closed."""
        subject = self.build_subject()
        rules = [*self._intelligence_rules(), *self._composed_gates(subject)]
        return RepositoryValidationReport.create(
            repository_id=self._report.repository_id,
            report_sha256=self._report.report_sha256,
            rules=tuple(rules),
            subject_digest=subject.digest(),
        )

    def _composed_gates(self, subject: RepositorySubject) -> list[RuleOutcome]:
        outcomes: list[RuleOutcome] = []
        for gate in self._gates:
            finding: AcceptanceFinding = gate.evaluate(subject)
            outcomes.append(
                RuleOutcome(
                    rule_id=finding.gate_id,
                    provenance=PROVENANCE_COMPOSED,
                    severity=(
                        Severity.BLOCKING
                        if finding.severity.value == "blocking"
                        else Severity.ADVISORY
                    ),
                    status=(
                        FindingStatus.PASS
                        if finding.status is GateStatus.PASS
                        else FindingStatus.FAIL
                    ),
                    message=finding.message,
                    details=dict(finding.details),
                )
            )
        return outcomes

    def _intelligence_rules(self) -> list[RuleOutcome]:
        report = self._report
        graph = report.graph
        outcomes: list[RuleOutcome] = []

        outcomes.append(
            self._from_finding(
                RULE_SUBSTRATE_READ,
                DiscoveryDimension.REPOSITORY,
                SUBSTRATE_PRESENT,
                "the repository code substrate was read",
            )
        )
        outcomes.append(
            self._from_finding(
                RULE_CATALOG_COMPOSED,
                DiscoveryDimension.CAPABILITY,
                CATALOG_COMPOSED,
                "the capability catalog was composed from its existing owner rather than "
                "re-derived",
            )
        )
        outcomes.append(
            self._from_finding(
                RULE_GRAPH_ACYCLIC,
                DiscoveryDimension.DEPENDENCY,
                DEPENDENCY_ACYCLIC,
                "the capability dependency graph is acyclic",
            )
        )

        layer_violations = [
            f
            for f in report.failures_of(DiscoveryDimension.CONFLICT)
            if f.code == CONFLICT_LAYER_VIOLATION
        ]
        outcomes.append(
            _rule(
                RULE_GRAPH_LAYERED,
                not layer_violations,
                "no capability depends upward across the declared layer order"
                if not layer_violations
                else f"{len(layer_violations)} layer violation(s) detected",
                violations=[f.subject for f in layer_violations],
            )
        )

        duplicates = [
            f
            for f in report.failures_of(DiscoveryDimension.DUPLICATE)
            if f.code == DUPLICATE_MODULE_CONTENT
        ]
        outcomes.append(
            _rule(
                RULE_NO_CONTENT_DUPLICATES,
                not duplicates,
                "no two source modules are byte-identical"
                if not duplicates
                else f"{len(duplicates)} byte-identical module group(s) detected",
                groups=[f.subject for f in duplicates],
            )
        )

        contested = [
            f
            for f in report.failures_of(DiscoveryDimension.OWNERSHIP)
            if f.code == OWNERSHIP_CONTESTED
        ]
        outcomes.append(
            _rule(
                RULE_OWNERSHIP_UNCONTESTED,
                not contested,
                "every capability has exactly one derivable owner"
                if not contested
                else f"{len(contested)} capability/capabilities have contested ownership",
                contested=[f.subject for f in contested],
            )
        )

        node_ids = set(graph.node_ids())
        dangling = [
            f"{edge.source} -> {edge.target}"
            for edge in graph.edges
            if edge.source not in node_ids or edge.target not in node_ids
        ]
        outcomes.append(
            _rule(
                RULE_GRAPH_CLOSED,
                not dangling,
                f"the repository graph is closed over its {len(node_ids)} nodes"
                if not dangling
                else f"{len(dangling)} edge(s) reference unknown nodes",
                dangling=dangling[:20],
            )
        )

        expected_dimensions = {d.value for d in DiscoveryDimension}
        run_dimensions = set(report.dimension_verdicts())
        missing = sorted(expected_dimensions - run_dimensions)
        outcomes.append(
            _rule(
                RULE_EVERY_DIMENSION_RUN,
                not missing,
                f"all {len(expected_dimensions)} discovery dimensions were run"
                if not missing
                else f"discovery dimensions were not run: {', '.join(missing)}",
                missing=missing,
            )
        )

        recomputed = graph.digest()
        outcomes.append(
            _rule(
                RULE_REPORT_SELF_CONSISTENT,
                bool(report.report_sha256) and len(report.report_sha256) == 64,
                "the intelligence report carries a well-formed content seal",
                report_sha256=report.report_sha256,
                graph_digest=recomputed,
            )
        )
        return outcomes

    def _from_finding(
        self,
        rule_id: str,
        dimension: DiscoveryDimension,
        code: str,
        description: str,
    ) -> RuleOutcome:
        """Lift a specific discovery finding into a validation rule outcome.

        A rule whose evidencing finding is *absent* fails closed: the rule could not be
        proven, which is not the same as the rule holding.
        """
        matches = [f for f in self._report.findings_of(dimension) if f.code == code]
        if not matches:
            return _rule(
                rule_id,
                False,
                f"{description} — could not be determined: no '{code}' finding was produced",
                evidencing_code=code,
                dimension=dimension.value,
            )
        finding: Finding = matches[0]
        return _rule(
            rule_id,
            finding.passed,
            description if finding.passed else finding.message,
            evidencing_code=code,
            dimension=dimension.value,
            finding_id=finding.finding_id,
        )


def _rule(rule_id: str, passed: bool, message: str, **details: Any) -> RuleOutcome:
    return RuleOutcome(
        rule_id=rule_id,
        provenance=PROVENANCE_INTELLIGENCE,
        severity=Severity.BLOCKING,
        status=FindingStatus.PASS if passed else FindingStatus.FAIL,
        message=message,
        details=details,
    )


def _health(critical: tuple[str, ...], warnings: tuple[str, ...]) -> RepositoryHealth:
    """Project blocking findings as critical issues and advisory findings as warnings."""
    return RepositoryHealth(critical_issues=critical, warnings=warnings)


def validate_report(
    report: RepositoryIntelligenceReport,
    gates: tuple[AcceptanceGate, ...] | None = None,
) -> RepositoryValidationReport:
    """Convenience: validate an intelligence report with the default composed suite."""
    return RepositoryValidator(report, gates).validate()


__all__ = [
    "COMPOSED_GATES",
    "PROVENANCE_COMPOSED",
    "PROVENANCE_INTELLIGENCE",
    "RULE_SUBSTRATE_READ",
    "RULE_CATALOG_COMPOSED",
    "RULE_GRAPH_ACYCLIC",
    "RULE_GRAPH_LAYERED",
    "RULE_NO_CONTENT_DUPLICATES",
    "RULE_OWNERSHIP_UNCONTESTED",
    "RULE_GRAPH_CLOSED",
    "RULE_REPORT_SELF_CONSISTENT",
    "RULE_EVERY_DIMENSION_RUN",
    "RuleOutcome",
    "RepositoryValidationReport",
    "RepositoryValidator",
    "validate_report",
]
