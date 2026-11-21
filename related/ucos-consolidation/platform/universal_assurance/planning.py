"""UCOS-EPIC-014 — Validation Planning & Certification Planning (Terminal T7).

Two of the ten owned capabilities live here. Both are **policy-driven plan synthesis**:
they read the declared obligations out of an
:class:`~platform.universal_assurance.policy.AssurancePolicy`, resolve each obligation's
declared ``requires_facts`` against the :class:`~platform.universal_assurance.contracts.
AssuranceSubject`, and emit an immutable, content-addressed :class:`AssurancePlan`.

    * **Validation Planning** (:class:`ValidationPlanner`) plans the validation work —
      the obligations declared for the *validation-execution* and
      *validation-intelligence* stages.
    * **Certification Planning** (:class:`CertificationPlanner`) plans the certification
      work — the obligations declared for the *certification-execution* stage, together
      with the policy gates that must pass before a certificate may be issued.

Planning is **fail-closed**: an obligation whose required facts are absent is *planned
and recorded as unsatisfiable* — never silently dropped. Unsatisfiability of a blocking
obligation closes the plan, so "we could not check it" can never be mistaken for "it
passed" (absence of evidence is never evidence of correctness).

Planning is **measurable**: :meth:`AssurancePlan.observations` emits the numeric facts
the policy's planning metrics are evaluated against.

Planning is **reproducible**: obligations are ordered canonically and the plan embeds no
wall-clock or ambient state, so an identical subject planned under an identical policy
yields a byte-identical plan and ``plan_sha256`` (IMP-007 §5).

The fact-address grammar resolved by :func:`resolve_fact_address` is the only coupling
between a policy document and a subject's shape::

    validation.<domain>        a ValidationDomain key in subject.validation_facts
    intelligence.<dimension>   an IntelligenceDimension key in subject.intelligence_facts
    repository_truth           the subject's repository-truth attestation
    observations.<key>         a numeric key in subject.observations

An address with an unknown prefix is a malformed *policy* (an authoring fault) and
raises :class:`~platform.universal_assurance.errors.AssurancePlanError`.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from enum import Enum
from platform.foundation.contracts import content_hash
from platform.universal_assurance.contracts import (
    AssuranceStage,
    AssuranceSubject,
    ObligationKind,
    Severity,
)
from platform.universal_assurance.errors import AssurancePlanError
from platform.universal_assurance.policy import AssurancePolicy, PolicyGate, PolicyObligation
from typing import Any

#: The plan format identifier.
PLAN_FORMAT = "ucos-assurance-plan/1.0.0"

#: The fact-address prefixes the planner understands (the whole coupling surface).
FACT_VALIDATION_PREFIX = "validation."
FACT_INTELLIGENCE_PREFIX = "intelligence."
FACT_OBSERVATIONS_PREFIX = "observations."
FACT_REPOSITORY_TRUTH = "repository_truth"

#: The fail-closed reason recorded for an obligation whose required facts are absent.
#: Planning is the earliest stage that can reach this verdict, so the string is defined
#: here and reused by generation (``UNBOUND_UNSATISFIABLE``) and certification
#: (``REASON_UNSATISFIABLE``) rather than restated — one condition, one vocabulary.
REASON_UNSATISFIABLE = "unsatisfiable-obligation"


class PlanKind(str, Enum):
    """Which owned planning capability produced a plan."""

    VALIDATION = "validation"
    CERTIFICATION = "certification"

    @property
    def id_prefix(self) -> str:
        return "UCOS-VPLAN" if self is PlanKind.VALIDATION else "UCOS-CPLAN"


def resolve_fact_address(subject: AssuranceSubject, address: str) -> bool:
    """Return whether ``address`` resolves to present, non-empty evidence on ``subject``.

    Raises:
        AssurancePlanError: if the address uses an unrecognized prefix (a malformed
            policy — an authoring fault, never a fail-closed verdict).
    """
    if address == FACT_REPOSITORY_TRUTH:
        return bool(subject.repository_truth)
    if address.startswith(FACT_VALIDATION_PREFIX):
        key = address[len(FACT_VALIDATION_PREFIX) :]
        return bool(subject.validation_facts.get(key))
    if address.startswith(FACT_INTELLIGENCE_PREFIX):
        key = address[len(FACT_INTELLIGENCE_PREFIX) :]
        return bool(subject.intelligence_facts.get(key))
    if address.startswith(FACT_OBSERVATIONS_PREFIX):
        key = address[len(FACT_OBSERVATIONS_PREFIX) :]
        return key in subject.observations
    raise AssurancePlanError(
        "policy declares an unrecognized fact address",
        address=address,
        supported=[
            f"{FACT_VALIDATION_PREFIX}<domain>",
            f"{FACT_INTELLIGENCE_PREFIX}<dimension>",
            FACT_REPOSITORY_TRUTH,
            f"{FACT_OBSERVATIONS_PREFIX}<key>",
        ],
    )


@dataclass(frozen=True, slots=True)
class PlannedObligation:
    """A policy obligation admitted into a plan, with its decidability resolved."""

    obligation: PolicyObligation
    satisfiable: bool
    missing_facts: tuple[str, ...] = ()

    @classmethod
    def create(cls, obligation: PolicyObligation, subject: AssuranceSubject) -> PlannedObligation:
        """Resolve ``obligation``'s required facts against ``subject`` (fail-closed)."""
        missing = tuple(
            address
            for address in obligation.requires_facts
            if not resolve_fact_address(subject, address)
        )
        return cls(obligation=obligation, satisfiable=not missing, missing_facts=missing)

    @property
    def id(self) -> str:
        return self.obligation.id

    @property
    def blocking(self) -> bool:
        return self.obligation.blocking

    @property
    def is_blocking_shortfall(self) -> bool:
        """True iff a *blocking* obligation cannot be decided from the supplied facts."""
        return self.blocking and not self.satisfiable

    def core(self) -> dict[str, Any]:
        """The canonical, hashable core of the planned obligation."""
        return {
            "obligation_id": self.obligation.id,
            "stage": self.obligation.stage.value,
            "kind": self.obligation.kind.value,
            "ref": self.obligation.ref,
            "severity": self.obligation.severity.value,
            "satisfiable": self.satisfiable,
            "missing_facts": list(self.missing_facts),
        }

    def to_dict(self) -> dict[str, Any]:
        return {**self.core(), "rationale": self.obligation.rationale}


@dataclass(frozen=True, slots=True)
class AssurancePlan:
    """An immutable, content-addressed plan produced by an owned planning capability.

    A plan is a **pure function of the subject and the policy**: it records which
    declared obligations were admitted, which of them are decidable from the supplied
    facts, and which policy gates the plan must ultimately satisfy.
    """

    plan_id: str
    plan_kind: PlanKind
    subject_id: str
    subject_digest: str
    policy_id: str
    policy_digest: str
    stages: tuple[AssuranceStage, ...]
    planned: tuple[PlannedObligation, ...]
    declared_total: int
    gates: tuple[PolicyGate, ...]
    plan_sha256: str

    @staticmethod
    def _core(
        *,
        plan_kind: PlanKind,
        subject_id: str,
        subject_digest: str,
        policy_id: str,
        policy_digest: str,
        stages: tuple[AssuranceStage, ...],
        planned: tuple[PlannedObligation, ...],
        declared_total: int,
        gates: tuple[PolicyGate, ...],
    ) -> dict[str, Any]:
        return {
            "plan_format": PLAN_FORMAT,
            "plan_kind": plan_kind.value,
            "subject_id": subject_id,
            "subject_digest": subject_digest,
            "policy_id": policy_id,
            "policy_digest": policy_digest,
            "stages": [stage.value for stage in stages],
            "declared_total": declared_total,
            "obligations": [item.core() for item in planned],
            "gates": [gate.to_dict() for gate in gates],
        }

    @classmethod
    def create(
        cls,
        *,
        plan_kind: PlanKind,
        subject: AssuranceSubject,
        policy: AssurancePolicy,
        stages: Iterable[AssuranceStage],
        kinds: Iterable[ObligationKind] | None = None,
    ) -> AssurancePlan:
        """Synthesize a plan for ``stages`` from ``policy`` over ``subject``.

        Every obligation the policy declares for the selected stages (optionally
        narrowed to the selected ``kinds``) is admitted; each is resolved against the
        subject's facts and recorded as satisfiable or not. Nothing is dropped.
        """
        selected_stages = tuple(sorted(set(stages), key=lambda s: s.order))
        if not selected_stages:
            raise AssurancePlanError(
                "a plan requires at least one stage", plan_kind=plan_kind.value
            )
        allowed_kinds = set(kinds) if kinds is not None else None
        declared: list[PolicyObligation] = []
        for stage in selected_stages:
            for obligation in policy.obligations_for(stage):
                if allowed_kinds is None or obligation.kind in allowed_kinds:
                    declared.append(obligation)
        planned = tuple(
            PlannedObligation.create(obligation, subject)
            for obligation in sorted(declared, key=lambda o: (o.stage.order, o.kind.order, o.id))
        )
        gates = tuple(
            sorted(
                (gate for gate in policy.gates if set(gate.stages) & set(selected_stages)),
                key=lambda g: g.id,
            )
        )
        core = cls._core(
            plan_kind=plan_kind,
            subject_id=subject.subject_id,
            subject_digest=subject.digest(),
            policy_id=policy.identity.id,
            policy_digest=policy.digest(),
            stages=selected_stages,
            planned=planned,
            declared_total=len(declared),
            gates=gates,
        )
        digest = content_hash(core)
        return cls(
            plan_id=f"{plan_kind.id_prefix}-{digest[:16]}",
            plan_kind=plan_kind,
            subject_id=subject.subject_id,
            subject_digest=subject.digest(),
            policy_id=policy.identity.id,
            policy_digest=policy.digest(),
            stages=selected_stages,
            planned=planned,
            declared_total=len(declared),
            gates=gates,
            plan_sha256=digest,
        )

    # -- derived, measurable properties ----------------------------------------

    @property
    def satisfiable(self) -> tuple[PlannedObligation, ...]:
        return tuple(item for item in self.planned if item.satisfiable)

    @property
    def unsatisfiable(self) -> tuple[PlannedObligation, ...]:
        return tuple(item for item in self.planned if not item.satisfiable)

    def blocking_shortfalls(self) -> tuple[str, ...]:
        """The ids of blocking obligations that cannot be decided (fail-closed)."""
        return tuple(item.id for item in self.planned if item.is_blocking_shortfall)

    def advisory_shortfalls(self) -> tuple[str, ...]:
        return tuple(
            item.id
            for item in self.planned
            if not item.satisfiable and item.obligation.severity is Severity.ADVISORY
        )

    @property
    def decidable(self) -> bool:
        """True iff every *blocking* planned obligation is decidable."""
        return not self.blocking_shortfalls()

    def obligation_ids(self) -> tuple[str, ...]:
        return tuple(item.id for item in self.planned)

    def failure_reasons_for_shortfalls(self) -> dict[str, str]:
        """A map of ``obligation id -> reason`` for every undecidable planned obligation.

        The plan's contribution to the run-level gate evaluation, mirroring
        :meth:`~platform.universal_assurance.execution.ValidationExecution.failure_reasons`.
        An obligation that could not be decided from the supplied facts is a failure for
        gate purposes at *either* severity — absence of evidence is never evidence of
        correctness, and the sibling contributors to that same map report every
        non-passing obligation regardless of severity.
        """
        return {item.id: REASON_UNSATISFIABLE for item in self.planned if not item.satisfiable}

    def obligations_of_kind(self, kind: ObligationKind) -> tuple[PlannedObligation, ...]:
        return tuple(item for item in self.planned if item.obligation.kind is kind)

    def refs_of_kind(self, kind: ObligationKind) -> tuple[str, ...]:
        """The distinct reused-implementation refs planned for ``kind``, in order."""
        seen: dict[str, None] = {}
        for item in self.obligations_of_kind(kind):
            seen.setdefault(item.obligation.ref, None)
        return tuple(sorted(seen))

    def coverage(self) -> float:
        """The planned/declared ratio (1.0 when the policy declares nothing here)."""
        if self.declared_total <= 0:
            return 1.0
        return len(self.planned) / self.declared_total

    def counts(self) -> dict[str, int]:
        return {
            "declared": self.declared_total,
            "planned": len(self.planned),
            "satisfiable": len(self.satisfiable),
            "unsatisfiable": len(self.unsatisfiable),
            "blocking": sum(1 for item in self.planned if item.blocking),
            "blocking_shortfalls": len(self.blocking_shortfalls()),
            "advisory_shortfalls": len(self.advisory_shortfalls()),
            "gates": len(self.gates),
        }

    def observations(self) -> dict[str, float]:
        namespace = "plan" if self.plan_kind is PlanKind.VALIDATION else "certification_plan"
        counts = self.counts()
        return {
            f"{namespace}.obligations_declared": float(counts["declared"]),
            f"{namespace}.obligations_planned": float(counts["planned"]),
            f"{namespace}.unsatisfiable_obligations": float(counts["unsatisfiable"]),
            f"{namespace}.blocking_shortfalls": float(counts["blocking_shortfalls"]),
            f"{namespace}.obligation_coverage": self.coverage(),
            f"{namespace}.gate_count": float(counts["gates"]),
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "plan_format": PLAN_FORMAT,
            "plan_id": self.plan_id,
            "plan_kind": self.plan_kind.value,
            "subject_id": self.subject_id,
            "subject_digest": self.subject_digest,
            "policy_id": self.policy_id,
            "policy_digest": self.policy_digest,
            "stages": [stage.value for stage in self.stages],
            "decidable": self.decidable,
            "counts": self.counts(),
            "coverage": self.coverage(),
            "blocking_shortfalls": list(self.blocking_shortfalls()),
            "advisory_shortfalls": list(self.advisory_shortfalls()),
            "obligations": [item.to_dict() for item in self.planned],
            "gates": [gate.to_dict() for gate in self.gates],
            "observations": self.observations(),
            "plan_sha256": self.plan_sha256,
        }


class ValidationPlanner:
    """**Validation Planning** — synthesizes the validation plan from the policy."""

    __slots__ = ("_policy", "_stages")

    #: The stages whose obligations constitute validation work.
    DEFAULT_STAGES: tuple[AssuranceStage, ...] = (
        AssuranceStage.VALIDATION_EXECUTION,
        AssuranceStage.VALIDATION_INTELLIGENCE,
    )

    def __init__(
        self,
        policy: AssurancePolicy,
        *,
        stages: Iterable[AssuranceStage] | None = None,
    ) -> None:
        if not isinstance(policy, AssurancePolicy):
            raise AssurancePlanError("validation planning requires an AssurancePolicy")
        self._policy = policy
        self._stages = tuple(stages) if stages is not None else self.DEFAULT_STAGES

    @property
    def policy(self) -> AssurancePolicy:
        return self._policy

    @property
    def stages(self) -> tuple[AssuranceStage, ...]:
        return self._stages

    def plan(self, subject: AssuranceSubject) -> AssurancePlan:
        """Produce the content-addressed validation plan for ``subject``."""
        if not isinstance(subject, AssuranceSubject):
            raise AssurancePlanError("validation planning requires an AssuranceSubject")
        return AssurancePlan.create(
            plan_kind=PlanKind.VALIDATION,
            subject=subject,
            policy=self._policy,
            stages=self._stages,
        )


class CertificationPlanner:
    """**Certification Planning** — synthesizes the certification plan from the policy."""

    __slots__ = ("_policy", "_stages")

    #: The stage whose obligations constitute certification work.
    DEFAULT_STAGES: tuple[AssuranceStage, ...] = (AssuranceStage.CERTIFICATION_EXECUTION,)

    def __init__(
        self,
        policy: AssurancePolicy,
        *,
        stages: Iterable[AssuranceStage] | None = None,
    ) -> None:
        if not isinstance(policy, AssurancePolicy):
            raise AssurancePlanError("certification planning requires an AssurancePolicy")
        self._policy = policy
        self._stages = tuple(stages) if stages is not None else self.DEFAULT_STAGES

    @property
    def policy(self) -> AssurancePolicy:
        return self._policy

    @property
    def stages(self) -> tuple[AssuranceStage, ...]:
        return self._stages

    def plan(self, subject: AssuranceSubject) -> AssurancePlan:
        """Produce the content-addressed certification plan for ``subject``."""
        if not isinstance(subject, AssuranceSubject):
            raise AssurancePlanError("certification planning requires an AssuranceSubject")
        return AssurancePlan.create(
            plan_kind=PlanKind.CERTIFICATION,
            subject=subject,
            policy=self._policy,
            stages=self._stages,
        )

    def criteria_refs(self, plan: AssurancePlan) -> tuple[str, ...]:
        """The reused certification-rule ids the plan admits."""
        return plan.refs_of_kind(ObligationKind.CERTIFICATION_CRITERION)

    def frame_refs(self, plan: AssurancePlan) -> tuple[str, ...]:
        """The reused compliance-frame ids the plan admits."""
        return plan.refs_of_kind(ObligationKind.CERTIFICATION_FRAME)


def evaluate_gates(
    gates: Iterable[PolicyGate],
    *,
    failed_obligations: Mapping[str, str],
    failed_stages: Iterable[AssuranceStage] = (),
) -> tuple[dict[str, Any], ...]:
    """Evaluate policy gates against failed obligations and failed stages.

    A gate passes iff none of the obligations it composes failed **and** none of the
    stages it spans failed. Obligation-level evaluation alone would let a gate over a
    stage that declares no obligation (an evidence or registry gate, say) pass
    vacuously; including the stage verdict closes that hole.

    Gates are returned in canonical id order so the outcome is deterministic.
    """
    failed_stage_set = set(failed_stages)
    outcomes: list[dict[str, Any]] = []
    for gate in sorted(gates, key=lambda g: g.id):
        obligation_failures = tuple(
            obligation_id
            for obligation_id in gate.obligations
            if obligation_id in failed_obligations
        )
        stage_failures = tuple(stage.value for stage in gate.stages if stage in failed_stage_set)
        outcomes.append(
            {
                "gate_id": gate.id,
                "name": gate.name,
                "stages": [stage.value for stage in gate.stages],
                "obligations": list(gate.obligations),
                "passed": not obligation_failures and not stage_failures,
                "failures": list(obligation_failures),
                "failed_stages": list(stage_failures),
            }
        )
    return tuple(outcomes)


def gate_outcomes(
    plan: AssurancePlan, failed_obligations: Mapping[str, str]
) -> tuple[dict[str, Any], ...]:
    """Evaluate the plan's policy gates against a map of ``obligation id -> reason``.

    This is the *obligation-level* evaluation a single stage can perform on its own. The
    run-level evaluation, which also accounts for failed stages, is
    :func:`evaluate_gates`.
    """
    return evaluate_gates(plan.gates, failed_obligations=failed_obligations)


__all__ = [
    "PLAN_FORMAT",
    "FACT_VALIDATION_PREFIX",
    "FACT_INTELLIGENCE_PREFIX",
    "FACT_OBSERVATIONS_PREFIX",
    "FACT_REPOSITORY_TRUTH",
    "REASON_UNSATISFIABLE",
    "PlanKind",
    "resolve_fact_address",
    "PlannedObligation",
    "AssurancePlan",
    "ValidationPlanner",
    "CertificationPlanner",
    "evaluate_gates",
    "gate_outcomes",
]
