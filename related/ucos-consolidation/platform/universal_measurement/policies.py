"""UCOS-UMPF-001 — The reusable measurement policies.

Each measurement that used to be a branch inside one closure engine is here a small,
registered, independently testable policy over Foundation determinations:

    ``truth.classification.coverage``   every locator is classified by declared policy
    ``ownership.coverage``             every subject has a declared canonical owner
    ``ownership.unresolved``           subjects whose ownership is not declared (gap)
    ``ownership.remediable``           the diagnosed share of that residue (gap, disclosure)
    ``ownership.contested``            subjects with unsettled competing claims (gap)
    ``assimilation.coverage``          every source reached a declared canonical destination
    ``assimilation.evidence-only``     evidence admitted but never homed (gap)
    ``assimilation.unadapted``         sources no adapter can normalise (gap)
    ``foundation.completeness``        the composite closure determination

None of them knows a repository, a directory, a dataset or a file format. Swap the
specialisation document and the same policies measure a different project. Add a policy and
every project that registers it gains the measurement — no engine is edited.
"""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from collections.abc import Mapping, Sequence
from pathlib import Path
from platform.measurement.contracts import MeasurementKind
from platform.universal_assimilation.contracts import (
    REASON_DESTINATION_NOT_HOME,
    REASON_NO_ADAPTER,
    REASON_NO_DECLARED_DESTINATION,
    AssimilationState,
)
from platform.universal_measurement.contracts import (
    MeasurementContext,
    MeasurementPolicyDescriptor,
    PolicyOutcome,
)
from platform.universal_measurement.errors import (
    MeasurementContextError,
    MeasurementPolicyContractError,
    MeasurementPolicyError,
    MeasurementPolicyEvaluationError,
)
from platform.universal_ownership.contracts import OwnershipStanding
from platform.universal_truth.contracts import TruthClass
from typing import Any


class MeasurementPolicy(ABC):
    """The extension point for every measurement, present or future."""

    @abstractmethod
    def descriptor(self) -> MeasurementPolicyDescriptor:
        """Describe this policy's identity, subject, kind and blocking status."""
        raise NotImplementedError  # pragma: no cover - abstract

    @abstractmethod
    def evaluate(self, context: MeasurementContext) -> PolicyOutcome:
        """Measure ``context`` and report an outcome with its findings."""
        raise NotImplementedError  # pragma: no cover - abstract

    def apply(self, context: MeasurementContext) -> PolicyOutcome:
        """Protocol enforcement: contain faults and verify the outcome's provenance."""
        if not isinstance(context, MeasurementContext):
            raise MeasurementPolicyContractError("evaluation requires a MeasurementContext")
        descriptor = self.descriptor()
        try:
            outcome = self.evaluate(context)
        except MeasurementPolicyError:
            raise
        except Exception as exc:  # noqa: BLE001 - contained by design (fail-closed)
            raise MeasurementPolicyEvaluationError(
                "measurement policy failed",
                policy_id=descriptor.policy_id,
                detail=str(exc),
            ) from exc
        if not isinstance(outcome, PolicyOutcome):
            raise MeasurementPolicyEvaluationError(
                "policy produced a non-outcome value", policy_id=descriptor.policy_id
            )
        if outcome.policy_id != descriptor.policy_id:
            raise MeasurementPolicyEvaluationError(
                "outcome provenance does not match its policy",
                policy_id=descriptor.policy_id,
                outcome_policy=outcome.policy_id,
            )
        return outcome


class TruthClassificationCoveragePolicy(MeasurementPolicy):
    """Coverage: every locator in the population is classified by declared Truth policy."""

    __slots__ = ("_descriptor",)

    def __init__(self, *, blocking: bool = True, precedence: int = 900) -> None:
        self._descriptor = MeasurementPolicyDescriptor(
            policy_id="truth.classification.coverage",
            subject="repository.truth",
            kind=MeasurementKind.COVERAGE,
            blocking=blocking,
            precedence=precedence,
            description="Every locator is classified by a declared Repository Truth zone.",
        )

    def descriptor(self) -> MeasurementPolicyDescriptor:
        """Describe this policy."""
        return self._descriptor

    def evaluate(self, context: MeasurementContext) -> PolicyOutcome:
        """Measure classification coverage over the declared locator population."""
        partition = context.require_partition(self._descriptor.policy_id)
        unclassified = partition.unclassified()
        classified = partition.total - len(unclassified)
        value = 0.0 if partition.total == 0 else round((classified / partition.total) * 100, 4)
        return PolicyOutcome.create(
            self._descriptor,
            value=value,
            population=partition.total,
            satisfied=not unclassified,
            summary=f"{classified}/{partition.total} locators classified by declared policy",
            findings=(item.locator for item in unclassified),
        )


class OwnershipCoveragePolicy(MeasurementPolicy):
    """Coverage: every subject has exactly one declared canonical owner ("homed")."""

    __slots__ = ("_descriptor",)

    def __init__(self, *, blocking: bool = True, precedence: int = 800) -> None:
        self._descriptor = MeasurementPolicyDescriptor(
            policy_id="ownership.coverage",
            subject="canonical.ownership",
            kind=MeasurementKind.COVERAGE,
            blocking=blocking,
            precedence=precedence,
            description="Every subject has one declared canonical owner.",
        )

    def descriptor(self) -> MeasurementPolicyDescriptor:
        """Describe this policy."""
        return self._descriptor

    def evaluate(self, context: MeasurementContext) -> PolicyOutcome:
        """Measure declared-ownership coverage over the subject population."""
        determination = context.require_ownership(self._descriptor.policy_id)
        undeclared = tuple(record for record in determination.records if not record.declared)
        return PolicyOutcome.create(
            self._descriptor,
            value=determination.coverage,
            population=determination.total,
            satisfied=not undeclared,
            summary=(
                f"{len(determination.declared)}/{determination.total} subjects have a "
                "declared canonical owner"
            ),
            findings=(record.subject_id for record in undeclared),
        )


class UnresolvedOwnershipPolicy(MeasurementPolicy):
    """Gap: subjects whose canonical ownership could not be honestly declared."""

    __slots__ = ("_descriptor",)

    def __init__(self, *, blocking: bool = True, precedence: int = 700) -> None:
        self._descriptor = MeasurementPolicyDescriptor(
            policy_id="ownership.unresolved",
            subject="canonical.ownership",
            kind=MeasurementKind.GAP,
            blocking=blocking,
            precedence=precedence,
            description="Subjects with no declared canonical owner, by named reason.",
        )

    def descriptor(self) -> MeasurementPolicyDescriptor:
        """Describe this policy."""
        return self._descriptor

    def evaluate(self, context: MeasurementContext) -> PolicyOutcome:
        """Count unresolved subjects and report each with its named reason."""
        determination = context.require_ownership(self._descriptor.policy_id)
        unresolved = determination.of_standing(OwnershipStanding.UNRESOLVED)
        return PolicyOutcome.create(
            self._descriptor,
            value=float(len(unresolved)),
            population=determination.total,
            satisfied=not unresolved,
            summary=f"{len(unresolved)} subjects have no declared canonical owner",
            findings=(f"{record.subject_id}:{','.join(record.reasons)}" for record in unresolved),
        )


class RemediableOwnershipPolicy(MeasurementPolicy):
    """Disclosure: how much of the undeclared residue names a located, remediable deficit.

    ``ownership.unresolved`` already blocks on the residue as a whole. This policy does not
    re-block it — it *partitions* it, which is a different measurement over the same population
    (UFC-16 forbids two numbers for one quantity, not two quantities). A subject counted here
    was refused by a declared eligibility rule at a named locator, so discharging it needs an
    act — register the artifact, give it the declared form, move it out of derived residue — and
    not a governing authority's decision. Everything left over is the honest governance floor.

    Non-blocking by the same reasoning as ``assimilation.evidence-only``: the disclosure IS the
    required behaviour, and blocking on it would double-count a block already declared.
    """

    __slots__ = ("_descriptor",)

    def __init__(self, *, blocking: bool = False, precedence: int = 695) -> None:
        self._descriptor = MeasurementPolicyDescriptor(
            policy_id="ownership.remediable",
            subject="canonical.ownership",
            kind=MeasurementKind.GAP,
            blocking=blocking,
            precedence=precedence,
            description=(
                "Undeclared subjects whose absence names a located, remediable eligibility "
                "deficit rather than requiring a governing authority."
            ),
        )

    def descriptor(self) -> MeasurementPolicyDescriptor:
        """Describe this policy."""
        return self._descriptor

    def evaluate(self, context: MeasurementContext) -> PolicyOutcome:
        """Count the diagnosed residue and report each subject with its declared deficit."""
        determination = context.require_ownership(self._descriptor.policy_id)
        remediable = determination.remediable
        undeclared = len(determination.unresolved) + len(determination.contested)
        undiagnosed = undeclared - len(remediable)
        return PolicyOutcome.create(
            self._descriptor,
            value=float(len(remediable)),
            population=determination.total,
            satisfied=not remediable,
            summary=(
                f"{len(remediable)} of {undeclared} undeclared subjects name a remediable "
                f"deficit; {undiagnosed} carry no diagnosed deficit"
            ),
            findings=(
                f"{record.subject_id}:{','.join(record.refusal_reasons)}" for record in remediable
            ),
        )


class ContestedOwnershipPolicy(MeasurementPolicy):
    """Gap: subjects with competing claims that declared precedence could not settle."""

    __slots__ = ("_descriptor",)

    def __init__(self, *, blocking: bool = True, precedence: int = 690) -> None:
        self._descriptor = MeasurementPolicyDescriptor(
            policy_id="ownership.contested",
            subject="canonical.ownership",
            kind=MeasurementKind.GAP,
            blocking=blocking,
            precedence=precedence,
            description="Subjects claimed by more than one owner (duplicate canonical homes).",
        )

    def descriptor(self) -> MeasurementPolicyDescriptor:
        """Describe this policy."""
        return self._descriptor

    def evaluate(self, context: MeasurementContext) -> PolicyOutcome:
        """Count contested subjects and report the competing claims."""
        determination = context.require_ownership(self._descriptor.policy_id)
        contested = determination.contested
        return PolicyOutcome.create(
            self._descriptor,
            value=float(len(contested)),
            population=determination.total,
            satisfied=not contested,
            summary=f"{len(contested)} subjects are claimed by competing owners",
            findings=(
                f"{record.subject_id}:{','.join(owner for owner, _ in record.claims)}"
                for record in contested
            ),
        )


class AssimilationCoveragePolicy(MeasurementPolicy):
    """Coverage: every admitted source reached a declared canonical destination."""

    __slots__ = ("_descriptor",)

    def __init__(self, *, blocking: bool = True, precedence: int = 600) -> None:
        self._descriptor = MeasurementPolicyDescriptor(
            policy_id="assimilation.coverage",
            subject="source.assimilation",
            kind=MeasurementKind.COVERAGE,
            blocking=blocking,
            precedence=precedence,
            description="Every admissible source has been assimilated.",
        )

    def descriptor(self) -> MeasurementPolicyDescriptor:
        """Describe this policy."""
        return self._descriptor

    def evaluate(self, context: MeasurementContext) -> PolicyOutcome:
        """Measure assimilation coverage over the source population."""
        report = context.require_assimilation(self._descriptor.policy_id)
        outstanding = report.outstanding()
        return PolicyOutcome.create(
            self._descriptor,
            value=report.coverage,
            population=report.total,
            satisfied=not outstanding,
            summary=f"{len(report.assimilated)}/{report.total} sources assimilated",
            findings=(record.source.locator for record in outstanding),
        )


class EvidenceOnlySourcePolicy(MeasurementPolicy):
    """Gap: evidence was admitted but never became repository content.

    This is the universal form of every "uploaded but not homed" measurement: an EVIDENCE-class
    source that reached no declared canonical destination, computed from declared policy rather
    than from a rule about one directory.
    """

    __slots__ = ("_descriptor",)

    def __init__(self, *, blocking: bool = True, precedence: int = 590) -> None:
        self._descriptor = MeasurementPolicyDescriptor(
            policy_id="assimilation.evidence-only",
            subject="source.assimilation",
            kind=MeasurementKind.GAP,
            blocking=blocking,
            precedence=precedence,
            description="Evidence-class sources with no declared canonical destination.",
        )

    def descriptor(self) -> MeasurementPolicyDescriptor:
        """Describe this policy."""
        return self._descriptor

    def evaluate(self, context: MeasurementContext) -> PolicyOutcome:
        """Count evidence sources that never reached a canonical home."""
        report = context.require_assimilation(self._descriptor.policy_id)
        evidence_only = tuple(
            record
            for record in report.records
            if record.truth_class is TruthClass.EVIDENCE
            and record.state is not AssimilationState.ASSIMILATED
            and (
                REASON_NO_DECLARED_DESTINATION in record.reasons
                or REASON_DESTINATION_NOT_HOME in record.reasons
            )
        )
        population = len(
            tuple(record for record in report.records if record.truth_class is TruthClass.EVIDENCE)
        )
        return PolicyOutcome.create(
            self._descriptor,
            value=float(len(evidence_only)),
            population=population,
            satisfied=not evidence_only,
            summary=(
                f"{len(evidence_only)}/{population} evidence sources have no declared "
                "canonical destination"
            ),
            findings=(record.source.locator for record in evidence_only),
        )


class UnadaptedSourcePolicy(MeasurementPolicy):
    """Gap: sources the framework cannot yet normalise — the honest edge of assimilation."""

    __slots__ = ("_descriptor",)

    def __init__(self, *, blocking: bool = True, precedence: int = 580) -> None:
        self._descriptor = MeasurementPolicyDescriptor(
            policy_id="assimilation.unadapted",
            subject="source.assimilation",
            kind=MeasurementKind.GAP,
            blocking=blocking,
            precedence=precedence,
            description="Sources for which no registered adapter declares the kind.",
        )

    def descriptor(self) -> MeasurementPolicyDescriptor:
        """Describe this policy."""
        return self._descriptor

    def evaluate(self, context: MeasurementContext) -> PolicyOutcome:
        """Count sources no registered adapter can normalise."""
        report = context.require_assimilation(self._descriptor.policy_id)
        unadapted = report.of_reason(REASON_NO_ADAPTER)
        return PolicyOutcome.create(
            self._descriptor,
            value=float(len(unadapted)),
            population=report.total,
            satisfied=not unadapted,
            summary=f"{len(unadapted)} sources have no registered adapter",
            findings=(f"{record.source.kind}:{record.source.locator}" for record in unadapted),
        )


class FoundationCompletenessPolicy(MeasurementPolicy):
    """The composite completeness determination over every supplied Foundation determination.

    Completeness is not a separate calculation bolted onto a report: it is the conjunction of
    the determinations the Foundation already made, measured by the same framework as
    everything else.
    """

    __slots__ = ("_descriptor",)

    def __init__(self, *, blocking: bool = True, precedence: int = 10) -> None:
        self._descriptor = MeasurementPolicyDescriptor(
            policy_id="foundation.completeness",
            subject="foundation.determination",
            kind=MeasurementKind.METRIC,
            blocking=blocking,
            precedence=precedence,
            description="Truth classified, ownership declared and sources assimilated.",
        )

    def descriptor(self) -> MeasurementPolicyDescriptor:
        """Describe this policy."""
        return self._descriptor

    def evaluate(self, context: MeasurementContext) -> PolicyOutcome:
        """Measure the conjunction of the supplied determinations."""
        checks: list[tuple[str, bool]] = []
        if context.partition is not None:
            checks.append(("truth.classified", not context.partition.unclassified()))
        if context.ownership is not None:
            checks.append(("ownership.closed", context.ownership.closed))
        if context.assimilation is not None:
            checks.append(("assimilation.closed", context.assimilation.closed))
        if not checks:
            raise MeasurementContextError(
                "completeness requires at least one determination",
                policy_id=self._descriptor.policy_id,
            )
        satisfied = [name for name, ok in checks if ok]
        failed = [name for name, ok in checks if not ok]
        value = round((len(satisfied) / len(checks)) * 100, 4)
        return PolicyOutcome.create(
            self._descriptor,
            value=value,
            population=len(checks),
            satisfied=not failed,
            summary=f"{len(satisfied)}/{len(checks)} Foundation determinations complete",
            findings=failed,
        )


def default_measurement_policies() -> tuple[MeasurementPolicy, ...]:
    """The reusable policies the framework ships with — register more, edit nothing."""
    return (
        TruthClassificationCoveragePolicy(),
        OwnershipCoveragePolicy(),
        UnresolvedOwnershipPolicy(),
        RemediableOwnershipPolicy(),
        ContestedOwnershipPolicy(),
        AssimilationCoveragePolicy(),
        EvidenceOnlySourcePolicy(),
        UnadaptedSourcePolicy(),
        FoundationCompletenessPolicy(),
    )


#: The packaged catalogue directory holding declared policy compositions (UFC-04).
CATALOG_DIRNAME = "catalog"

#: The declared policy composition shipped with the framework (data, not code).
DEFAULT_CATALOG_FILENAME = "ucos-measurement-policies.json"


def catalog_path(filename: str = DEFAULT_CATALOG_FILENAME) -> Path:
    """The packaged catalogue path for ``filename``."""
    return Path(__file__).resolve().parent / CATALOG_DIRNAME / filename


def _policy_type(name: str) -> type[MeasurementPolicy]:
    """Resolve a declared policy class name within this module (fail-closed).

    Resolution is confined to this module's own namespace, so a declaration can compose the
    shipped policies and configure them, but can never name an arbitrary importable object.
    """
    candidate = globals().get(name)
    if not isinstance(candidate, type) or not issubclass(candidate, MeasurementPolicy):
        raise MeasurementPolicyError("declared policy is not a MeasurementPolicy", policy=str(name))
    if candidate is MeasurementPolicy:
        raise MeasurementPolicyError("the abstract policy cannot be registered directly")
    return candidate


def policies_from_document(document: Mapping[str, Any]) -> tuple[MeasurementPolicy, ...]:
    """Compose the declared policy set from a declaration document (fail-closed).

    Each entry names a shipped policy and supplies its ``blocking`` and ``precedence``
    configuration, so *which* measurements bind and *how strongly* is data rather than code.
    """
    if not isinstance(document, Mapping):
        raise MeasurementPolicyError("policy composition document must be a mapping")
    declared = document.get("policies")
    if not isinstance(declared, Sequence) or isinstance(declared, str | bytes):
        raise MeasurementPolicyError("policy composition requires a 'policies' sequence")
    composed: list[MeasurementPolicy] = []
    for entry in declared:
        if not isinstance(entry, Mapping) or "policy" not in entry:
            raise MeasurementPolicyError("policy declaration requires 'policy'")
        policy_type = _policy_type(str(entry["policy"]))
        try:
            composed.append(
                policy_type(
                    blocking=bool(entry.get("blocking", True)),
                    precedence=int(entry.get("precedence", 100)),
                )
            )
        except (TypeError, ValueError) as exc:
            raise MeasurementPolicyError(
                "declared policy could not be configured",
                policy=str(entry["policy"]),
                detail=str(exc),
            ) from exc
    if not composed:
        raise MeasurementPolicyError("policy composition declares no policy")
    return tuple(composed)


def load_measurement_policies(path: Path | str) -> tuple[MeasurementPolicy, ...]:
    """Load a declared policy composition from ``path`` (fail-closed)."""
    target = Path(path)
    try:
        document = json.loads(target.read_text("utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise MeasurementPolicyError(
            "policy composition document could not be read",
            path=str(target),
            detail=str(exc),
        ) from exc
    return policies_from_document(document)


def declared_measurement_policies(
    filename: str = DEFAULT_CATALOG_FILENAME,
) -> tuple[MeasurementPolicy, ...]:
    """The policy composition declared in the packaged catalogue."""
    return load_measurement_policies(catalog_path(filename))


__all__ = [
    "CATALOG_DIRNAME",
    "DEFAULT_CATALOG_FILENAME",
    "MeasurementPolicy",
    "TruthClassificationCoveragePolicy",
    "OwnershipCoveragePolicy",
    "UnresolvedOwnershipPolicy",
    "RemediableOwnershipPolicy",
    "ContestedOwnershipPolicy",
    "AssimilationCoveragePolicy",
    "EvidenceOnlySourcePolicy",
    "UnadaptedSourcePolicy",
    "FoundationCompletenessPolicy",
    "catalog_path",
    "declared_measurement_policies",
    "default_measurement_policies",
    "load_measurement_policies",
    "policies_from_document",
]
