"""UCOS-UMPF-001 — Measurement policy vocabulary & contracts.

A measurement is a *policy over determinations*, not a branch inside an engine. This module
declares the four things such a policy needs and nothing more:

    * :class:`MeasurementContext` — the determinations available to measure: the Repository
      Truth partition, the ownership determination, the assimilation report, the subject
      population, and declared numeric facts for policies not yet written.
    * :class:`MeasurementPolicyDescriptor` — a policy's identity, subject, measurement kind,
      whether it **blocks**, and its declared precedence.
    * :class:`PolicyOutcome` — what a policy found: a value, a population, the findings that
      make it up, and whether the policy is satisfied.
    * :class:`PolicySuite` — the deterministic result of running a whole registry.

Every outcome carries its findings, so a number can always be resolved back to the subjects
that produced it, and a policy that cannot be evaluated raises instead of reporting zero.
Identities live in a disjoint ``UCOS-UMP*`` namespace and are content-addressed (IMP-007 §5).
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from platform.foundation.contracts import ContractRef, content_hash
from platform.measurement.contracts import Measurement, MeasurementKind
from platform.universal_assimilation.contracts import AssimilationReport
from platform.universal_measurement.errors import (
    MeasurementContextError,
    MeasurementPolicyContractError,
)
from platform.universal_ownership.contracts import OwnershipDetermination
from platform.universal_truth.contracts import Subject
from platform.universal_truth.policy import TruthPartition
from typing import Any

#: The canonical identity of the Universal Measurement Policy Framework instance.
UMPF_ID = "UCOS-UMPF-001"

#: The semantic version of the measurement policy contract surface (AR-03/PL-05).
POLICY_CONTRACT_VERSION = "1.0.0"

#: How many findings an outcome retains verbatim, so a report can never grow unbounded.
MAX_RETAINED_FINDINGS = 500


def _percent(part: int, whole: int) -> float:
    """A deterministic percentage; ``0.0`` when the population is empty."""
    if whole <= 0:
        return 0.0
    return round((part / whole) * 100, 4)


@dataclass(frozen=True, slots=True)
class MeasurementContext:
    """The determinations a measurement policy may measure. Truth in, measurement out.

    The context is read-only and additive: a policy that needs a determination the caller did
    not supply fails closed through :meth:`require_ownership` and friends rather than quietly
    measuring an empty population.
    """

    partition: TruthPartition | None = None
    ownership: OwnershipDetermination | None = None
    assimilation: AssimilationReport | None = None
    subjects: tuple[Subject, ...] = ()
    facts: Mapping[str, float] = field(default_factory=dict)
    context_id: str = ""

    @classmethod
    def create(
        cls,
        *,
        partition: TruthPartition | None = None,
        ownership: OwnershipDetermination | None = None,
        assimilation: AssimilationReport | None = None,
        subjects: Iterable[Subject] = (),
        facts: Mapping[str, float] | None = None,
    ) -> MeasurementContext:
        """Build a validated context with a content-addressed identity."""
        if partition is not None and not isinstance(partition, TruthPartition):
            raise MeasurementPolicyContractError("partition must be a TruthPartition")
        if ownership is not None and not isinstance(ownership, OwnershipDetermination):
            raise MeasurementPolicyContractError("ownership must be an OwnershipDetermination")
        if assimilation is not None and not isinstance(assimilation, AssimilationReport):
            raise MeasurementPolicyContractError("assimilation must be an AssimilationReport")
        population = tuple(sorted(subjects, key=lambda item: item.subject_id))
        declared = {str(key): float(value) for key, value in dict(facts or {}).items()}
        core = {
            "partition": partition.partition_id if partition else "",
            "ownership": ownership.determination_id if ownership else "",
            "assimilation": assimilation.report_id if assimilation else "",
            "subjects": [subject.subject_id for subject in population],
            "facts": dict(sorted(declared.items())),
        }
        return cls(
            partition=partition,
            ownership=ownership,
            assimilation=assimilation,
            subjects=population,
            facts=declared,
            context_id=f"UCOS-UMPX-{content_hash(core)[:16]}",
        )

    def require_partition(self, policy_id: str) -> TruthPartition:
        """The Repository Truth partition (fail-closed when absent)."""
        if self.partition is None:
            raise MeasurementContextError(
                "policy requires a Repository Truth partition", policy_id=policy_id
            )
        return self.partition

    def require_ownership(self, policy_id: str) -> OwnershipDetermination:
        """The ownership determination (fail-closed when absent)."""
        if self.ownership is None:
            raise MeasurementContextError(
                "policy requires an ownership determination", policy_id=policy_id
            )
        return self.ownership

    def require_assimilation(self, policy_id: str) -> AssimilationReport:
        """The assimilation report (fail-closed when absent)."""
        if self.assimilation is None:
            raise MeasurementContextError(
                "policy requires an assimilation report", policy_id=policy_id
            )
        return self.assimilation

    def fact(self, name: str) -> float:
        """A declared numeric fact (fail-closed when undeclared)."""
        if name not in self.facts:
            raise MeasurementContextError("policy requires a declared fact", fact=name)
        return self.facts[name]

    def available(self) -> tuple[str, ...]:
        """Which determinations this context carries."""
        present = []
        if self.partition is not None:
            present.append("partition")
        if self.ownership is not None:
            present.append("ownership")
        if self.assimilation is not None:
            present.append("assimilation")
        if self.subjects:
            present.append("subjects")
        if self.facts:
            present.append("facts")
        return tuple(present)

    def to_dict(self) -> dict[str, Any]:
        """A JSON-serialisable projection of this context."""
        return {
            "context_id": self.context_id,
            "available": list(self.available()),
            "partition_id": self.partition.partition_id if self.partition else "",
            "ownership_id": self.ownership.determination_id if self.ownership else "",
            "assimilation_id": self.assimilation.report_id if self.assimilation else "",
            "subject_count": len(self.subjects),
            "facts": dict(sorted(self.facts.items())),
        }

    def fingerprint(self) -> str:
        """The deterministic content fingerprint of this context."""
        return content_hash(self.to_dict())


@dataclass(frozen=True, slots=True)
class MeasurementPolicyDescriptor:
    """A policy's identity, what it measures, and whether it blocks."""

    policy_id: str
    subject: str
    kind: MeasurementKind
    blocking: bool = False
    precedence: int = 100
    description: str = ""

    def __post_init__(self) -> None:
        if not isinstance(self.policy_id, str) or not self.policy_id.strip():
            raise MeasurementPolicyContractError("policy_id must be a non-empty string")
        if not isinstance(self.subject, str) or not self.subject.strip():
            raise MeasurementPolicyContractError(
                "policy must declare a subject", policy_id=self.policy_id
            )
        if not isinstance(self.kind, MeasurementKind):
            raise MeasurementPolicyContractError(
                "policy kind must be a MeasurementKind", policy_id=self.policy_id
            )
        if not isinstance(self.precedence, int) or isinstance(self.precedence, bool):
            raise MeasurementPolicyContractError(
                "policy precedence must be an int", policy_id=self.policy_id
            )

    @property
    def order_key(self) -> tuple[int, str]:
        """Deterministic evaluation order: highest precedence first, then identity."""
        return (-self.precedence, self.policy_id)

    def to_dict(self) -> dict[str, Any]:
        """A JSON-serialisable projection of this descriptor."""
        return {
            "policy_id": self.policy_id,
            "subject": self.subject,
            "kind": self.kind.value,
            "blocking": self.blocking,
            "precedence": self.precedence,
            "description": self.description,
        }

    def fingerprint(self) -> str:
        """The deterministic content fingerprint of this descriptor."""
        return content_hash(self.to_dict())


@dataclass(frozen=True, slots=True)
class PolicyOutcome:
    """What one policy found: a value, its population, its findings, and its verdict."""

    policy_id: str
    subject: str
    kind: MeasurementKind
    value: float
    population: int
    satisfied: bool
    blocking: bool = False
    summary: str = ""
    findings: tuple[str, ...] = ()
    finding_total: int = 0
    outcome_id: str = ""

    @classmethod
    def create(
        cls,
        descriptor: MeasurementPolicyDescriptor,
        *,
        value: float,
        population: int,
        satisfied: bool,
        summary: str = "",
        findings: Iterable[str] = (),
    ) -> PolicyOutcome:
        """Build a validated outcome with a content-addressed identity."""
        if not isinstance(descriptor, MeasurementPolicyDescriptor):
            raise MeasurementPolicyContractError("outcome requires a policy descriptor")
        named = tuple(sorted({str(item) for item in findings if str(item).strip()}))
        retained = named[:MAX_RETAINED_FINDINGS]
        core = {
            "policy_id": descriptor.policy_id,
            "subject": descriptor.subject,
            "kind": descriptor.kind.value,
            "value": round(float(value), 4),
            "population": int(population),
            "satisfied": bool(satisfied),
            "finding_total": len(named),
        }
        return cls(
            policy_id=descriptor.policy_id,
            subject=descriptor.subject,
            kind=descriptor.kind,
            value=round(float(value), 4),
            population=int(population),
            satisfied=bool(satisfied),
            blocking=descriptor.blocking,
            summary=summary,
            findings=retained,
            finding_total=len(named),
            outcome_id=f"UCOS-UMPO-{content_hash(core)[:16]}",
        )

    @property
    def blocks(self) -> bool:
        """Whether this outcome blocks closure (a blocking policy that is unsatisfied)."""
        return self.blocking and not self.satisfied

    def to_dict(self) -> dict[str, Any]:
        """A JSON-serialisable projection of this outcome."""
        return {
            "outcome_id": self.outcome_id,
            "policy_id": self.policy_id,
            "subject": self.subject,
            "kind": self.kind.value,
            "value": self.value,
            "population": self.population,
            "satisfied": self.satisfied,
            "blocking": self.blocking,
            "blocks": self.blocks,
            "summary": self.summary,
            "finding_total": self.finding_total,
            "findings": list(self.findings),
        }

    def as_measurement(self) -> Measurement:
        """Project this outcome as a :class:`~platform.measurement.contracts.Measurement`."""
        return Measurement.create(
            self.kind,
            self.subject,
            summary=self.summary or f"{self.policy_id}={self.value}",
            payload=self.to_dict(),
        )

    def fingerprint(self) -> str:
        """The deterministic content fingerprint of this outcome."""
        return content_hash(self.to_dict())


@dataclass(frozen=True, slots=True)
class PolicySuite:
    """The deterministic result of evaluating a whole policy registry over one context."""

    outcomes: tuple[PolicyOutcome, ...]
    context_id: str = ""
    suite_id: str = ""

    @classmethod
    def create(cls, outcomes: Iterable[PolicyOutcome], *, context_id: str = "") -> PolicySuite:
        """Build a deterministic suite, ordered by policy identity."""
        ordered = tuple(sorted(outcomes, key=lambda item: item.policy_id))
        seen: set[str] = set()
        for outcome in ordered:
            if outcome.policy_id in seen:
                raise MeasurementPolicyContractError(
                    "duplicate policy outcome", policy_id=outcome.policy_id
                )
            seen.add(outcome.policy_id)
        core = {
            "outcomes": [outcome.outcome_id for outcome in ordered],
            "context_id": context_id,
        }
        return cls(
            outcomes=ordered,
            context_id=context_id,
            suite_id=f"UCOS-UMPS-{content_hash(core)[:16]}",
        )

    @property
    def total(self) -> int:
        """How many policies were evaluated."""
        return len(self.outcomes)

    @property
    def blocking(self) -> tuple[PolicyOutcome, ...]:
        """Every blocking policy in the suite."""
        return tuple(outcome for outcome in self.outcomes if outcome.blocking)

    @property
    def blockers(self) -> tuple[PolicyOutcome, ...]:
        """Every blocking policy that is unsatisfied — the reasons closure is withheld."""
        return tuple(outcome for outcome in self.outcomes if outcome.blocks)

    @property
    def closed(self) -> bool:
        """Whether every blocking policy is satisfied."""
        return self.total > 0 and not self.blockers

    @property
    def completeness(self) -> float:
        """The percentage of blocking policies that are satisfied."""
        blocking = self.blocking
        return _percent(len(blocking) - len(self.blockers), len(blocking))

    def outcome(self, policy_id: str) -> PolicyOutcome:
        """The outcome of ``policy_id`` (fail-closed)."""
        for item in self.outcomes:
            if item.policy_id == policy_id:
                return item
        raise MeasurementPolicyContractError("unknown policy outcome", policy_id=policy_id)

    def values(self) -> dict[str, float]:
        """Every measured value, keyed by policy identity."""
        return {outcome.policy_id: outcome.value for outcome in self.outcomes}

    def as_measurements(self) -> tuple[Measurement, ...]:
        """Project every outcome as a recordable measurement."""
        return tuple(outcome.as_measurement() for outcome in self.outcomes)

    def to_dict(self) -> dict[str, Any]:
        """A JSON-serialisable projection of this suite."""
        return {
            "suite_id": self.suite_id,
            "context_id": self.context_id,
            "policy_total": self.total,
            "blocking_total": len(self.blocking),
            "blocker_total": len(self.blockers),
            "closed": self.closed,
            "completeness_percentage": self.completeness,
            "determination": "CLOSED" if self.closed else "NOT-CLOSED",
            "blockers": [outcome.policy_id for outcome in self.blockers],
            "values": self.values(),
            "outcomes": [outcome.to_dict() for outcome in self.outcomes],
        }

    def fingerprint(self) -> str:
        """The deterministic content fingerprint of this suite."""
        return content_hash(self.to_dict())


_POLICY_CONTRACT_NAMES: tuple[tuple[str, str], ...] = (
    ("measurement.policy.register", "Register a reusable measurement policy."),
    ("measurement.policy.evaluate", "Evaluate one policy over a determination context."),
    ("measurement.policy.suite", "Evaluate a whole policy registry deterministically."),
    ("measurement.policy.project", "Project policy outcomes as recordable measurements."),
)

#: The versioned published contract surface of the Measurement Policy Framework.
POLICY_CONTRACTS: tuple[ContractRef, ...] = tuple(
    ContractRef(name, POLICY_CONTRACT_VERSION) for name, _ in _POLICY_CONTRACT_NAMES
)


def policy_contract_names() -> tuple[str, ...]:
    """The published measurement policy contract names, in declaration order."""
    return tuple(name for name, _ in _POLICY_CONTRACT_NAMES)


__all__ = [
    "UMPF_ID",
    "POLICY_CONTRACT_VERSION",
    "MAX_RETAINED_FINDINGS",
    "MeasurementContext",
    "MeasurementPolicyDescriptor",
    "PolicyOutcome",
    "PolicySuite",
    "POLICY_CONTRACTS",
    "policy_contract_names",
]
