"""URI-000001 — fail-closed realization governance.

Twelve gates adjudicate a realization run. The rule every gate obeys is the one that makes
governance meaningful:

    passed = total > 0 and failures == 0

A gate with nothing to check does **not** pass vacuously — it fails. That single decision
is what prevents an empty or partially wired pipeline from certifying itself. The verdict
is binary: ``GOVERNED`` only when all twelve gates pass, otherwise ``REJECTED`` with the
blocking reasons named as ``gate:item`` pairs.

Governance invents no verdict of its own. Each gate is a pure predicate over evidence the
upstream stages already produced (integrity records, plan waves, composition findings,
generation manifest, determinism proof, trace ledger). Nothing here re-derives a fact it
could instead check.

Authority: NONE. This is an engineering-execution decision over URI's own output. It does
not certify anything in the repository; certification remains with the constitutional
certification authority.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from engine.foundation.guards.frozen_paths import find_frozen_writes
from engine.foundation.obs.logging import get_logger
from engine.foundation.obs.telemetry import trace as trace_span
from intelligence.realization.canonical import content_hash, short_seal
from intelligence.realization.composition import CompositionFindings
from intelligence.realization.config import CAPABILITY_ID, RealizationConfig
from intelligence.realization.contracts import (
    FAMILY_ORDER,
    GenerationManifest,
    ImplementationRecord,
    RealizationComposition,
    RealizationPlan,
)
from intelligence.realization.errors import GovernanceRejectedError
from intelligence.realization.knowledge import KnowledgeIntake
from intelligence.realization.traceability import TraceLedger

_logger = get_logger("intelligence.realization.governance")

GOVERNANCE_STANDARD = "URI-000001 Realization Governance"
GOVERNANCE_STANDARD_VERSION = "1.0.0"
GOVERNANCE_AUTHORITY = "NONE (engineering execution over URI output only)"

VERDICT_GOVERNED = "GOVERNED"
VERDICT_REJECTED = "REJECTED"

#: The twelve gates, in adjudication order. Declared here so the set is closed: a run
#: reporting fewer than twelve gates is itself a rejection (see ``_assert_complete``).
GATES: tuple[str, ...] = (
    "KNOWLEDGE_INTEGRITY",
    "KNOWLEDGE_AUTHORITY",
    "KNOWLEDGE_ANCHORED",
    "PLAN_ACYCLIC",
    "PLAN_COVERAGE",
    "PLAN_FAMILY_COMPLETE",
    "COMPOSITION_CONFLICT_FREE",
    "COMPOSITION_NO_DUPLICATE_KNOWLEDGE",
    "GENERATION_PATH_UNIQUE",
    "GENERATION_DETERMINISM",
    "IMPLEMENTATION_FROZEN_SAFE",
    "TRACE_CLOSURE",
)


@dataclass(frozen=True, slots=True)
class GateOutcome:
    """The outcome of one fail-closed gate."""

    gate: str
    checked: int
    failures: tuple[str, ...]
    description: str

    @classmethod
    def of(
        cls,
        gate: str,
        *,
        checked: int,
        failures: Sequence[str] = (),
        description: str = "",
    ) -> GateOutcome:
        return cls(
            gate=gate,
            checked=int(checked),
            failures=tuple(sorted(str(item) for item in failures)),
            description=description,
        )

    @property
    def passed(self) -> bool:
        """Fail-closed: an unexercised gate never passes."""
        return self.checked > 0 and not self.failures

    def to_dict(self) -> dict[str, Any]:
        return {
            "gate": self.gate,
            "status": "PASS" if self.passed else "FAIL",
            "checked": self.checked,
            "failed": len(self.failures),
            "failures": list(self.failures),
            "description": self.description,
        }


@dataclass(frozen=True, slots=True)
class RealizationDecision:
    """The sealed, fail-closed governance decision over one realization run."""

    knowledge_seal: str
    plan_id: str
    composition_id: str
    generation_id: str
    implementation_id: str | None
    gates: tuple[GateOutcome, ...]
    capability: str = CAPABILITY_ID

    @property
    def verdict(self) -> str:
        return (
            VERDICT_GOVERNED
            if self.gates and all(gate.passed for gate in self.gates)
            else VERDICT_REJECTED
        )

    @property
    def governed(self) -> bool:
        return self.verdict == VERDICT_GOVERNED

    @property
    def blocking_reasons(self) -> tuple[str, ...]:
        reasons = [
            f"{gate.gate}:{item}"
            for gate in self.gates
            if not gate.passed
            for item in (gate.failures or ("unexercised",))
        ]
        return tuple(sorted(reasons))

    @property
    def passed_count(self) -> int:
        return sum(1 for gate in self.gates if gate.passed)

    @property
    def decision_id(self) -> str:
        return f"URI-GOV-{short_seal(self.seal)}"

    def _core(self) -> dict[str, Any]:
        return {
            "capability": self.capability,
            "standard": GOVERNANCE_STANDARD,
            "standard_version": GOVERNANCE_STANDARD_VERSION,
            "authority": GOVERNANCE_AUTHORITY,
            "knowledge_seal": self.knowledge_seal,
            "plan_id": self.plan_id,
            "composition_id": self.composition_id,
            "generation_id": self.generation_id,
            "implementation_id": self.implementation_id,
            "gates": [gate.to_dict() for gate in self.gates],
            "verdict": self.verdict,
            "blocking_reasons": list(self.blocking_reasons),
        }

    @property
    def seal(self) -> str:
        return content_hash(self._core())

    def to_dict(self) -> dict[str, Any]:
        payload = self._core()
        payload["decision_id"] = self.decision_id
        payload["gates_passed"] = f"{self.passed_count}/{len(self.gates)}"
        payload["seal"] = self.seal
        return payload


class RealizationGovernor:
    """Adjudicates a realization run against the twelve fail-closed gates."""

    def __init__(self, config: RealizationConfig | None = None) -> None:
        self.config = config or RealizationConfig.create()

    def adjudicate(
        self,
        *,
        intake: KnowledgeIntake,
        plan: RealizationPlan,
        composition: RealizationComposition,
        findings: CompositionFindings,
        manifest: GenerationManifest,
        determinism: Mapping[str, Any] | None = None,
        ledger: TraceLedger | None = None,
        record: ImplementationRecord | None = None,
    ) -> RealizationDecision:
        """Return the sealed decision. Never raises on a failed gate — that is the caller's."""
        with trace_span("realization.govern", plan_id=plan.plan_id):
            gates = (
                self._knowledge_integrity(intake),
                self._knowledge_authority(intake, plan),
                self._knowledge_anchored(manifest),
                self._plan_acyclic(plan),
                self._plan_coverage(plan),
                self._plan_family_complete(plan),
                self._composition_conflict_free(findings, composition),
                self._composition_no_duplicate_knowledge(findings, intake),
                self._generation_path_unique(manifest),
                self._generation_determinism(determinism),
                self._implementation_frozen_safe(manifest),
                self._trace_closure(ledger),
            )
            self._assert_complete(gates)
            decision = RealizationDecision(
                knowledge_seal=intake.knowledge_seal,
                plan_id=plan.plan_id,
                composition_id=composition.composition_id,
                generation_id=manifest.generation_id,
                implementation_id=record.implementation_id if record else None,
                gates=gates,
            )
            _logger.info(
                "realization.governed",
                decision_id=decision.decision_id,
                verdict=decision.verdict,
                gates=f"{decision.passed_count}/{len(decision.gates)}",
                blocking=len(decision.blocking_reasons),
            )
            return decision

    # -- gate completeness ----------------------------------------------------

    @staticmethod
    def _assert_complete(gates: Sequence[GateOutcome]) -> None:
        """The gate set is closed: exactly the declared gates, each exactly once."""
        names = [gate.gate for gate in gates]
        if sorted(names) != sorted(GATES):
            raise GovernanceRejectedError(
                "realization gate set is incomplete or duplicated",
                expected=list(GATES),
                actual=names,
            )

    # -- knowledge gates ------------------------------------------------------

    @staticmethod
    def _knowledge_integrity(intake: KnowledgeIntake) -> GateOutcome:
        failures = [str(record["id"]) for record in intake.integrity if not record["verified"]]
        return GateOutcome.of(
            "KNOWLEDGE_INTEGRITY",
            checked=len(intake.integrity),
            failures=failures,
            description="every canonical record verifies its own content hash",
        )

    @staticmethod
    def _knowledge_authority(intake: KnowledgeIntake, plan: RealizationPlan) -> GateOutcome:
        failures = []
        for target in plan.targets:
            active = [
                cko_id for cko_id in target.cko_ids if intake.base.require_object(cko_id).is_active
            ]
            if not active:
                failures.append(target.target_id)
        return GateOutcome.of(
            "KNOWLEDGE_AUTHORITY",
            checked=len(plan.targets),
            failures=failures,
            description="every realization target cites at least one active canonical object",
        )

    @staticmethod
    def _knowledge_anchored(manifest: GenerationManifest) -> GateOutcome:
        failures = [
            artifact.relative_path
            for artifact in manifest.artifacts
            if not artifact.provenance.source_ckos
        ]
        return GateOutcome.of(
            "KNOWLEDGE_ANCHORED",
            checked=len(manifest.artifacts),
            failures=failures,
            description="every generated artifact is anchored to canonical knowledge",
        )

    # -- plan gates -----------------------------------------------------------

    @staticmethod
    def _plan_acyclic(plan: RealizationPlan) -> GateOutcome:
        waved = {step_id for wave in plan.waves for step_id in wave}
        failures = [step.step_id for step in plan.steps if step.step_id not in waved]
        # A cycle would have prevented the planner from levelling every step.
        return GateOutcome.of(
            "PLAN_ACYCLIC",
            checked=len(plan.steps),
            failures=failures,
            description="every plan step was levelled into a dependency wave (DAG proof)",
        )

    @staticmethod
    def _plan_coverage(plan: RealizationPlan) -> GateOutcome:
        return GateOutcome.of(
            "PLAN_COVERAGE",
            checked=len(plan.steps),
            failures=plan.coverage_gaps,
            description="every realizable canonical object is claimed by a plan step",
        )

    @staticmethod
    def _plan_family_complete(plan: RealizationPlan) -> GateOutcome:
        expected = {family.value for family in FAMILY_ORDER}
        failures = []
        for target in plan.targets:
            present = {step.family.value for step in plan.steps_for(target.target_id)}
            for missing in sorted(expected - present):
                failures.append(f"{target.target_id}/{missing}")
        return GateOutcome.of(
            "PLAN_FAMILY_COMPLETE",
            checked=len(plan.targets) * len(expected),
            failures=failures,
            description="every target is realized into all seven artifact families",
        )

    # -- composition gates ----------------------------------------------------

    @staticmethod
    def _composition_conflict_free(
        findings: CompositionFindings, composition: RealizationComposition
    ) -> GateOutcome:
        failures = [f"{left}|{right}" for left, right in findings.conflicts]
        return GateOutcome.of(
            "COMPOSITION_CONFLICT_FREE",
            checked=len(composition.units),
            failures=failures,
            description="no conflicting canonical objects are bound into the same unit",
        )

    @staticmethod
    def _composition_no_duplicate_knowledge(
        findings: CompositionFindings, intake: KnowledgeIntake
    ) -> GateOutcome:
        failures = ["|".join(group) for group in findings.duplicate_knowledge]
        return GateOutcome.of(
            "COMPOSITION_NO_DUPLICATE_KNOWLEDGE",
            checked=len(intake.semantic_index()),
            failures=failures,
            description=(
                "no two canonical objects express the same knowledge "
                "(UCKO-PRIN-0001 / UCKO-RULE-0001)"
            ),
        )

    # -- generation gates -----------------------------------------------------

    @staticmethod
    def _generation_path_unique(manifest: GenerationManifest) -> GateOutcome:
        seen: dict[str, int] = {}
        for artifact in manifest.artifacts:
            seen[artifact.relative_path] = seen.get(artifact.relative_path, 0) + 1
        failures = [path for path, count in seen.items() if count > 1]
        return GateOutcome.of(
            "GENERATION_PATH_UNIQUE",
            checked=len(manifest.artifacts),
            failures=failures,
            description="no two artifacts claim the same output path",
        )

    @staticmethod
    def _generation_determinism(determinism: Mapping[str, Any] | None) -> GateOutcome:
        if determinism is None:
            return GateOutcome.of(
                "GENERATION_DETERMINISM",
                checked=0,
                failures=(),
                description="determinism proof was not supplied (gate fails closed)",
            )
        mismatches = list(determinism.get("mismatches") or ())
        checked = int(determinism.get("artifact_count") or 0)
        if not determinism.get("deterministic") and not mismatches:
            mismatches = ["seal-mismatch"]
        return GateOutcome.of(
            "GENERATION_DETERMINISM",
            checked=checked,
            failures=mismatches,
            description="regeneration from identical knowledge is byte-identical",
        )

    # -- implementation gate --------------------------------------------------

    def _implementation_frozen_safe(self, manifest: GenerationManifest) -> GateOutcome:
        root = self.config.rel(self.config.artifact_root)
        failures = []
        for artifact in manifest.artifacts:
            candidate = f"{root}/{artifact.relative_path}"
            if find_frozen_writes([candidate]) or ".." in artifact.relative_path:
                failures.append(artifact.relative_path)
        return GateOutcome.of(
            "IMPLEMENTATION_FROZEN_SAFE",
            checked=len(manifest.artifacts),
            failures=failures,
            description="no artifact targets the frozen corpus (DP-03 / UCKO-PRIN-0002)",
        )

    # -- traceability gate ----------------------------------------------------

    @staticmethod
    def _trace_closure(ledger: TraceLedger | None) -> GateOutcome:
        if ledger is None:
            return GateOutcome.of(
                "TRACE_CLOSURE",
                checked=0,
                failures=(),
                description="trace ledger was not supplied (gate fails closed)",
            )
        failures = [
            *(f"gap:{item}" for item in ledger.forward_gaps),
            *(f"orphan:{item}" for item in ledger.orphan_artifacts),
            *(f"unmaterialized:{item}" for item in ledger.unmaterialized),
        ]
        return GateOutcome.of(
            "TRACE_CLOSURE",
            checked=len(ledger.edges),
            failures=failures,
            description="knowledge->artifact traceability is closed in both directions",
        )


def enforce_realization(decision: RealizationDecision, *, strict: bool = True) -> None:
    """Raise when the decision is not ``GOVERNED``. The fail-closed enforcement point."""
    if strict and not decision.governed:
        raise GovernanceRejectedError(
            "realization was rejected by fail-closed governance",
            decision_id=decision.decision_id,
            verdict=decision.verdict,
            gates_passed=f"{decision.passed_count}/{len(decision.gates)}",
            blocking_reasons=list(decision.blocking_reasons),
        )


__all__ = [
    "GATES",
    "GOVERNANCE_AUTHORITY",
    "GOVERNANCE_STANDARD",
    "GOVERNANCE_STANDARD_VERSION",
    "VERDICT_GOVERNED",
    "VERDICT_REJECTED",
    "GateOutcome",
    "RealizationDecision",
    "RealizationGovernor",
    "enforce_realization",
]
