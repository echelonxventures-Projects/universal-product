"""UCOS-UFP-001 — The Universal Foundation service.

One object that composes the four reusable capabilities and produces one determination:

    Repository Truth  →  Ownership  →  Assimilation  →  Measurement Policy  →  Determination

Nothing in this module knows a repository. It reads a declared specialisation, projects a
population out of whatever document the project already keeps, determines ownership from
evidence, assimilates declared sources, measures the result through registered policies, and
emits a deterministic, content-addressed determination fit for certification.
"""

from __future__ import annotations

import json
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from pathlib import Path
from platform.foundation.contracts import content_hash
from platform.universal_assimilation.contracts import AssimilationReport
from platform.universal_assimilation.pipeline import AssimilationPipeline, SourceInput
from platform.universal_foundation.errors import FoundationCompositionError
from platform.universal_foundation.specialization import FoundationSpecialization
from platform.universal_measurement.contracts import MeasurementContext, PolicySuite
from platform.universal_measurement.engine import PolicyMeasurementEngine
from platform.universal_ownership.contracts import OwnershipDetermination
from platform.universal_ownership.determination import OwnershipDeterminationEngine
from platform.universal_truth.contracts import Subject
from platform.universal_truth.policy import TruthPartition, TruthPolicy
from platform.universal_truth.projection import SubjectProjection
from typing import Any

#: The capability identities this platform composes, in dependency order.
COMPOSED_CAPABILITIES: tuple[str, ...] = (
    "UCOS-URTF-001",
    "UCOS-UOF-001",
    "UCOS-USAF-001",
    "UCOS-UMPF-001",
)


@dataclass(frozen=True, slots=True)
class FoundationDetermination:
    """The immutable, content-addressed determination of the whole Foundation."""

    project_id: str
    partition: TruthPartition | None = None
    ownership: OwnershipDetermination | None = None
    assimilation: AssimilationReport | None = None
    suite: PolicySuite | None = None
    determination_id: str = ""

    @classmethod
    def create(
        cls,
        project_id: str,
        *,
        partition: TruthPartition | None = None,
        ownership: OwnershipDetermination | None = None,
        assimilation: AssimilationReport | None = None,
        suite: PolicySuite | None = None,
    ) -> FoundationDetermination:
        """Build a determination with a content-addressed identity."""
        core = {
            "project_id": project_id,
            "partition": partition.partition_id if partition else "",
            "ownership": ownership.determination_id if ownership else "",
            "assimilation": assimilation.report_id if assimilation else "",
            "suite": suite.suite_id if suite else "",
        }
        return cls(
            project_id=project_id,
            partition=partition,
            ownership=ownership,
            assimilation=assimilation,
            suite=suite,
            determination_id=f"UCOS-UFPD-{content_hash(core)[:16]}",
        )

    @property
    def closed(self) -> bool:
        """Whether every blocking measurement policy is satisfied."""
        return bool(self.suite and self.suite.closed)

    @property
    def determination(self) -> str:
        """``CLOSED`` or ``NOT-CLOSED`` — the headline verdict."""
        return "CLOSED" if self.closed else "NOT-CLOSED"

    def blockers(self) -> tuple[str, ...]:
        """The identities of the policies withholding closure."""
        if self.suite is None:
            return ()
        return tuple(outcome.policy_id for outcome in self.suite.blockers)

    def to_dict(self) -> dict[str, Any]:
        """A JSON-serialisable projection of this determination."""
        return {
            "determination_id": self.determination_id,
            "project_id": self.project_id,
            "determination": self.determination,
            "closed": self.closed,
            "blockers": list(self.blockers()),
            "truth": self.partition.to_dict() if self.partition else None,
            "ownership": self.ownership.to_dict() if self.ownership else None,
            "assimilation": self.assimilation.to_dict() if self.assimilation else None,
            "measurement": self.suite.to_dict() if self.suite else None,
        }

    def summary(self) -> dict[str, Any]:
        """A compact projection: the headline numbers without the per-record detail."""
        return {
            "determination_id": self.determination_id,
            "project_id": self.project_id,
            "determination": self.determination,
            "closed": self.closed,
            "blockers": list(self.blockers()),
            "truth": (
                {
                    "total": self.partition.total,
                    "counts": {name: value for name, value in self.partition.counts},
                    "unclassified": len(self.partition.unclassified()),
                }
                if self.partition
                else None
            ),
            "ownership": (
                {
                    "counts": self.ownership.counts(),
                    "coverage_percentage": self.ownership.coverage,
                    "by_reason": self.ownership.by_reason(),
                }
                if self.ownership
                else None
            ),
            "assimilation": (
                {
                    "total": self.assimilation.total,
                    "unit_total": self.assimilation.unit_total,
                    "coverage_percentage": self.assimilation.coverage,
                    "counts_by_state": self.assimilation.counts_by_state(),
                    "by_reason": self.assimilation.by_reason(),
                }
                if self.assimilation
                else None
            ),
            "measurement": (
                {
                    "policy_total": self.suite.total,
                    "completeness_percentage": self.suite.completeness,
                    "values": self.suite.values(),
                }
                if self.suite
                else None
            ),
        }

    def fingerprint(self) -> str:
        """The deterministic content fingerprint of this determination."""
        return content_hash(self.to_dict())


class UniversalFoundation:
    """The composed Universal Foundation: one determination from four reusable capabilities."""

    __slots__ = ("_specialization", "_truth", "_ownership", "_assimilation", "_policies")

    def __init__(
        self,
        specialization: FoundationSpecialization,
        truth: TruthPolicy,
        ownership: OwnershipDeterminationEngine,
        assimilation: AssimilationPipeline,
        policies: PolicyMeasurementEngine,
    ) -> None:
        if not isinstance(specialization, FoundationSpecialization):
            raise FoundationCompositionError("composition requires a FoundationSpecialization")
        if not isinstance(truth, TruthPolicy):
            raise FoundationCompositionError("composition requires a TruthPolicy")
        if not isinstance(ownership, OwnershipDeterminationEngine):
            raise FoundationCompositionError("composition requires an OwnershipDeterminationEngine")
        if not isinstance(assimilation, AssimilationPipeline):
            raise FoundationCompositionError("composition requires an AssimilationPipeline")
        if not isinstance(policies, PolicyMeasurementEngine):
            raise FoundationCompositionError("composition requires a PolicyMeasurementEngine")
        self._specialization = specialization
        self._truth = truth
        self._ownership = ownership
        self._assimilation = assimilation
        self._policies = policies

    @property
    def specialization(self) -> FoundationSpecialization:
        """The declared project specialisation this Foundation was composed from."""
        return self._specialization

    @property
    def truth(self) -> TruthPolicy:
        """The Repository Truth policy."""
        return self._truth

    @property
    def ownership(self) -> OwnershipDeterminationEngine:
        """The ownership determination engine."""
        return self._ownership

    @property
    def assimilation(self) -> AssimilationPipeline:
        """The source assimilation pipeline."""
        return self._assimilation

    @property
    def policies(self) -> PolicyMeasurementEngine:
        """The policy measurement engine."""
        return self._policies

    def capabilities(self) -> tuple[str, ...]:
        """The Foundation capability identities this platform composes."""
        return COMPOSED_CAPABILITIES

    def project_population(self, *, root: Path | str = ".") -> tuple[Subject, ...]:
        """Project the declared population document into subjects (empty when undeclared)."""
        document = self._specialization.resolve("population_document", root=root)
        if document is None or self._specialization.projection is None:
            return ()
        return SubjectProjection(self._specialization.projection).project_file(document)

    def registered_subjects(self, *, root: Path | str = ".") -> tuple[str, ...]:
        """The declared registration ledger, as subject identities (empty when undeclared)."""
        document = self._specialization.resolve("registered_subjects", root=root)
        if document is None:
            return ()
        try:
            payload = json.loads(Path(document).read_text("utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise FoundationCompositionError(
                "registration ledger could not be read", path=str(document), detail=str(exc)
            ) from exc
        if isinstance(payload, Mapping):
            return tuple(sorted(str(key) for key in payload))
        if isinstance(payload, list):
            return tuple(sorted(str(item) for item in payload))
        raise FoundationCompositionError(
            "registration ledger must be a mapping or list", path=str(document)
        )

    def classify(self, locators: Iterable[str]) -> TruthPartition:
        """Classify a locator population by declared Repository Truth policy."""
        return self._truth.classify_all(locators)

    def determine_ownership(self, subjects: Iterable[Subject]) -> OwnershipDetermination:
        """Determine canonical ownership from constitutional evidence only."""
        return self._ownership.determine(subjects)

    def assimilate(
        self,
        sources: Iterable[SourceInput],
        *,
        destinations: Mapping[str, str] | None = None,
    ) -> AssimilationReport:
        """Assimilate a declared source population through the one framework."""
        return self._assimilation.assimilate(sources, destinations=destinations)

    def measure(self, context: MeasurementContext) -> PolicySuite:
        """Measure a determination context through the registered policies."""
        return self._policies.measure(context)

    def determine(
        self,
        *,
        subjects: Iterable[Subject] | None = None,
        locators: Iterable[str] | None = None,
        sources: Iterable[SourceInput] | None = None,
        destinations: Mapping[str, str] | None = None,
    ) -> FoundationDetermination:
        """Run the whole Foundation over whatever the caller supplies, and measure it.

        Every input is optional: the Foundation measures what it was given and reports the
        rest as not measured. It never substitutes an empty population for a missing one.
        """
        population = tuple(subjects) if subjects is not None else ()
        partition = self.classify(locators) if locators is not None else None
        ownership = self.determine_ownership(population) if population else None
        report = (
            self.assimilate(sources, destinations=destinations) if sources is not None else None
        )
        context = MeasurementContext.create(
            partition=partition,
            ownership=ownership,
            assimilation=report,
            subjects=population,
        )
        suite = self.measure(context)
        return FoundationDetermination.create(
            self._specialization.project_id,
            partition=partition,
            ownership=ownership,
            assimilation=report,
            suite=suite,
        )

    def to_dict(self) -> dict[str, Any]:
        """A JSON-serialisable projection of this Foundation's composition."""
        return {
            "capabilities": list(self.capabilities()),
            "specialization": self._specialization.to_dict(),
            "truth_policy": self._truth.to_dict(),
            "ownership_providers": self._ownership.providers.to_dict(),
            "ownership_contract": self._ownership.contract.to_dict(),
            "assimilation": self._assimilation.to_dict(),
            "policies": self._policies.registry.to_dict(),
        }

    def fingerprint(self) -> str:
        """The deterministic content fingerprint of this Foundation's composition."""
        return content_hash(self.to_dict())


__all__ = ["COMPOSED_CAPABILITIES", "FoundationDetermination", "UniversalFoundation"]
