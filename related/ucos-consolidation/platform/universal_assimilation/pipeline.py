"""UCOS-USAF-001 — The one assimilation pipeline.

Every source travels the same road, whatever it is made of:

    1. **Admit** — a declared kind with a registered adapter is admitted; an undeclared kind
       or an unadapted kind is DEFERRED with ``NO-ADAPTER-FOR-SOURCE-KIND``. Nothing is
       dropped silently.
    2. **Classify** — Repository Truth policy classifies the source locator. A TRANSIENT
       source is REJECTED (it was never Truth); an unclassified source is DEFERRED with
       ``SOURCE-NOT-CLASSIFIED-BY-TRUTH-POLICY`` rather than assumed into Truth.
    3. **Normalise** — the adapter yields units. No units means
       ``NO-EXTRACTABLE-CONTENT``: an honest deferral, never invented content.
    4. **Home** — a source is ASSIMILATED only when a *declared* destination exists **and**
       that destination classifies into a zone Repository Truth policy declares eligible to
       hold canonical ownership. No declared destination yields
       ``NO-DECLARED-CANONICAL-DESTINATION``; a destination in an ineligible zone yields
       ``DESTINATION-NOT-CANONICAL-HOME``.

Step 4 is the generalisation of the whole class of "raw material was uploaded but never
became repository content" measurements: the pipeline computes it from declared policy, so
every project gets it, and no project needs a bespoke rule for it.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from platform.foundation.contracts import content_hash
from platform.universal_assimilation.adapters import SourceAdapterRegistry
from platform.universal_assimilation.contracts import (
    REASON_DESTINATION_NOT_HOME,
    REASON_NO_ADAPTER,
    REASON_NO_DECLARED_DESTINATION,
    REASON_NO_EXTRACTABLE_CONTENT,
    REASON_TRANSIENT_SOURCE,
    REASON_UNCLASSIFIED_SOURCE,
    AssimilationRecord,
    AssimilationReport,
    AssimilationState,
    AssimilationUnit,
    SourceKindRegistry,
    SourceRef,
    default_source_kind_registry,
)
from platform.universal_assimilation.errors import AssimilationPipelineError
from platform.universal_truth.contracts import TruthClass, normalize_locator
from platform.universal_truth.policy import TruthPolicy
from typing import Any


@dataclass(frozen=True, slots=True)
class SourceInput:
    """A source presented for assimilation: a declared kind, a locator, and its bytes.

    Payload acquisition is the caller's business. The framework never scans a filesystem,
    opens a network connection, or rediscovers a repository as a side effect of assimilating
    one of its files.
    """

    kind: str
    locator: str
    payload: bytes
    revision: str = ""
    destination: str = ""

    @classmethod
    def create(
        cls,
        kind: str,
        locator: str,
        payload: bytes,
        *,
        revision: str = "",
        destination: str = "",
    ) -> SourceInput:
        """Build a validated source input."""
        if not isinstance(payload, bytes | bytearray):
            raise AssimilationPipelineError("source payload must be bytes", locator=str(locator))
        return cls(
            kind=str(kind),
            locator=str(locator),
            payload=bytes(payload),
            revision=str(revision),
            destination=str(destination),
        )

    @classmethod
    def from_text(cls, kind: str, locator: str, text: str, **kwargs: Any) -> SourceInput:
        """Build a source input from text (a convenience for declared, textual sources)."""
        return cls.create(kind, locator, text.encode("utf-8"), **kwargs)

    def source_ref(self) -> SourceRef:
        """The content-addressed reference for this input."""
        return SourceRef.from_payload(self.kind, self.locator, self.payload, revision=self.revision)


@dataclass(frozen=True, slots=True)
class AssimilationOutcome:
    """The determination for one source, together with the units it yielded."""

    record: AssimilationRecord
    units: tuple[AssimilationUnit, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        """A JSON-serialisable projection of this outcome."""
        return {
            "record": self.record.to_dict(),
            "units": [unit.to_dict() for unit in self.units],
        }


class AssimilationPipeline:
    """The single framework through which every source — present or future — is assimilated."""

    __slots__ = ("_adapters", "_policy", "_kinds", "_require_declared_kind")

    def __init__(
        self,
        adapters: SourceAdapterRegistry,
        *,
        policy: TruthPolicy | None = None,
        kinds: SourceKindRegistry | None = None,
        require_declared_kind: bool = True,
    ) -> None:
        if not isinstance(adapters, SourceAdapterRegistry):
            raise AssimilationPipelineError("pipeline requires a SourceAdapterRegistry")
        if policy is not None and not isinstance(policy, TruthPolicy):
            raise AssimilationPipelineError("policy must be a TruthPolicy when supplied")
        self._adapters = adapters
        self._policy = policy
        self._kinds = kinds or default_source_kind_registry()
        self._require_declared_kind = bool(require_declared_kind)

    @property
    def adapters(self) -> SourceAdapterRegistry:
        """The registered source adapters."""
        return self._adapters

    @property
    def kinds(self) -> SourceKindRegistry:
        """The open registry of declared source kinds."""
        return self._kinds

    @property
    def policy(self) -> TruthPolicy | None:
        """The Repository Truth policy classifying sources and destinations, if declared."""
        return self._policy

    def _classify(self, locator: str) -> tuple[TruthClass, bool]:
        if self._policy is None:
            return TruthClass.UNCLASSIFIED, False
        classification = self._policy.classify(locator)
        return classification.truth_class, classification.canonical_home_eligible

    def _destination_owner(self, destination: str) -> tuple[bool, str]:
        if self._policy is None:
            return True, ""
        classification = self._policy.classify(destination)
        return (
            classification.canonical_home_eligible,
            classification.authority or classification.zone_id,
        )

    def assimilate_source(
        self, source: SourceInput, *, destination: str = ""
    ) -> AssimilationOutcome:
        """Run one source through the whole pipeline, honestly, to a terminal state."""
        if not isinstance(source, SourceInput):
            raise AssimilationPipelineError("assimilation requires a SourceInput")
        ref = source.source_ref()
        truth_class, _ = self._classify(ref.locator)
        target = (
            normalize_locator(destination or source.destination)
            if (destination or source.destination)
            else ""
        )

        if truth_class is TruthClass.TRANSIENT:
            return AssimilationOutcome(
                AssimilationRecord.create(
                    ref,
                    AssimilationState.REJECTED,
                    truth_class=truth_class,
                    reasons=(REASON_TRANSIENT_SOURCE,),
                )
            )

        if self._require_declared_kind and ref.kind not in self._kinds:
            return AssimilationOutcome(
                AssimilationRecord.create(
                    ref,
                    AssimilationState.DEFERRED,
                    truth_class=truth_class,
                    reasons=(REASON_NO_ADAPTER,),
                )
            )

        adapter = self._adapters.for_source(ref)
        if adapter is None:
            return AssimilationOutcome(
                AssimilationRecord.create(
                    ref,
                    AssimilationState.DEFERRED,
                    truth_class=truth_class,
                    reasons=(REASON_NO_ADAPTER,),
                )
            )

        adapter_id = adapter.descriptor().adapter_id
        units = adapter.units(ref, source.payload)
        if not units:
            return AssimilationOutcome(
                AssimilationRecord.create(
                    ref,
                    AssimilationState.DEFERRED,
                    adapter_id=adapter_id,
                    truth_class=truth_class,
                    reasons=(REASON_NO_EXTRACTABLE_CONTENT,),
                )
            )

        reasons: list[str] = []
        if truth_class is TruthClass.UNCLASSIFIED and self._policy is not None:
            reasons.append(REASON_UNCLASSIFIED_SOURCE)

        if not target:
            reasons.append(REASON_NO_DECLARED_DESTINATION)
            return AssimilationOutcome(
                AssimilationRecord.create(
                    ref,
                    AssimilationState.NORMALIZED,
                    adapter_id=adapter_id,
                    truth_class=truth_class,
                    reasons=tuple(reasons),
                    units=units,
                ),
                units,
            )

        eligible, owner = self._destination_owner(target)
        if not eligible:
            reasons.append(REASON_DESTINATION_NOT_HOME)
            return AssimilationOutcome(
                AssimilationRecord.create(
                    ref,
                    AssimilationState.ADMITTED,
                    adapter_id=adapter_id,
                    truth_class=truth_class,
                    destination=target,
                    reasons=tuple(reasons),
                    units=units,
                ),
                units,
            )

        if reasons:
            return AssimilationOutcome(
                AssimilationRecord.create(
                    ref,
                    AssimilationState.NORMALIZED,
                    adapter_id=adapter_id,
                    truth_class=truth_class,
                    destination=target,
                    owner=owner,
                    reasons=tuple(reasons),
                    units=units,
                ),
                units,
            )

        return AssimilationOutcome(
            AssimilationRecord.create(
                ref,
                AssimilationState.ASSIMILATED,
                adapter_id=adapter_id,
                truth_class=truth_class,
                destination=target,
                owner=owner,
                units=units,
            ),
            units,
        )

    def assimilate(
        self,
        sources: Iterable[SourceInput],
        *,
        destinations: Mapping[str, str] | None = None,
    ) -> AssimilationReport:
        """Assimilate a whole source population into a deterministic report.

        ``destinations`` is the *declared* canonical destination per source locator. It is a
        declaration, never an inference: a locator absent from it yields
        ``NO-DECLARED-CANONICAL-DESTINATION``.
        """
        declared = {
            normalize_locator(key): str(value) for key, value in dict(destinations or {}).items()
        }
        records: list[AssimilationRecord] = []
        for source in sources:
            locator = normalize_locator(source.locator)
            outcome = self.assimilate_source(
                source, destination=declared.get(locator, source.destination)
            )
            records.append(outcome.record)
        return AssimilationReport.create(records)

    def to_dict(self) -> dict[str, Any]:
        """A JSON-serialisable projection of this pipeline's composition."""
        return {
            "adapters": self._adapters.to_dict(),
            "kinds": self._kinds.to_dict(),
            "policy": self._policy.policy_id if self._policy else "",
            "require_declared_kind": self._require_declared_kind,
        }

    def fingerprint(self) -> str:
        """The deterministic content fingerprint of this pipeline's composition."""
        return content_hash(self.to_dict())


__all__ = ["SourceInput", "AssimilationOutcome", "AssimilationPipeline"]
