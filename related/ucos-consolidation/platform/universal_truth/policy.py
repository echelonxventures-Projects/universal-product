"""UCOS-URTF-001 — Repository Truth policy engine.

*Repository Truth SHALL be determined by policy, never by hardcoded paths.*

This module is the reusable determination of that rule. A :class:`TruthPolicy` is an
ordered set of declared :class:`~platform.universal_truth.contracts.TruthZone` values; it
classifies **any** locator of **any** project deterministically, records *which* declared
rule decided, and reports an honest ``UNCLASSIFIED`` absence rather than defaulting a
locator into Truth.

Resolution is total and order-independent of insertion: the admitting zone with the
highest declared ``precedence`` wins, ties broken by ``zone_id``. The policy therefore
has no hidden state, no first-writer-wins bias and no path literals — a project supplies
its specialisation as a declared document (JSON), which is the *only* place its own
directory names ever appear.
"""

from __future__ import annotations

import json
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from platform.foundation.contracts import content_hash
from platform.universal_truth.contracts import (
    RULE_DECLARED_ZONE,
    RULE_NO_DECLARED_ZONE,
    TRUTH_CONTRACT_VERSION,
    TruthClass,
    TruthClassification,
    TruthZone,
    normalize_locator,
)
from platform.universal_truth.errors import TruthPolicyError
from typing import Any

#: The packaged catalogue directory holding declared truth-policy specialisations.
CATALOG_DIRNAME = "catalog"

#: The declared specialisation shipped for the containing repository (data, not code).
DEFAULT_CATALOG_FILENAME = "ucos-repository-truth.json"


@dataclass(frozen=True, slots=True)
class TruthPartition:
    """An immutable partition of a locator population by constitutional truth class."""

    classifications: tuple[TruthClassification, ...]
    counts: tuple[tuple[str, int], ...]
    partition_id: str = ""

    @classmethod
    def create(cls, classifications: Iterable[TruthClassification]) -> TruthPartition:
        """Build a deterministic partition, ordered by locator."""
        ordered = tuple(sorted(classifications, key=lambda item: item.locator))
        tally: dict[str, int] = {member.value: 0 for member in TruthClass}
        for item in ordered:
            tally[item.truth_class.value] += 1
        counts = tuple(sorted(tally.items()))
        core = {
            "classifications": [item.classification_id for item in ordered],
            "counts": list(counts),
        }
        return cls(
            classifications=ordered,
            counts=counts,
            partition_id=f"UCOS-URTP-{content_hash(core)[:16]}",
        )

    @property
    def total(self) -> int:
        """The number of classified locators in the population."""
        return len(self.classifications)

    def count(self, truth_class: TruthClass | str) -> int:
        """How many locators fell into ``truth_class``."""
        resolved = TruthClass.coerce(truth_class)
        for name, value in self.counts:
            if name == resolved.value:
                return value
        return 0

    def of_class(self, truth_class: TruthClass | str) -> tuple[TruthClassification, ...]:
        """Every classification in ``truth_class``, ordered by locator."""
        resolved = TruthClass.coerce(truth_class)
        return tuple(item for item in self.classifications if item.truth_class is resolved)

    def canonical_home_eligible(self) -> tuple[TruthClassification, ...]:
        """Every classification whose declared zone may hold canonical ownership."""
        return tuple(item for item in self.classifications if item.canonical_home_eligible)

    def unclassified(self) -> tuple[TruthClassification, ...]:
        """Every locator no declared zone admitted (an honest absence)."""
        return tuple(item for item in self.classifications if not item.classified)

    def to_dict(self) -> dict[str, Any]:
        """A JSON-serialisable projection of this partition."""
        return {
            "partition_id": self.partition_id,
            "total": self.total,
            "counts": {name: value for name, value in self.counts},
            "canonical_home_eligible": len(self.canonical_home_eligible()),
            "unclassified": [item.locator for item in self.unclassified()],
            "classifications": [item.to_dict() for item in self.classifications],
        }

    def fingerprint(self) -> str:
        """The deterministic content fingerprint of this partition."""
        return content_hash(self.to_dict())


class TruthPolicy:
    """A declared, reusable determination of what counts as Repository Truth.

    The policy is append-only and fail-closed: registering a second zone under the same
    ``zone_id`` with a different body raises rather than silently redefining Truth.
    """

    __slots__ = ("_zones", "_policy_id", "_version")

    def __init__(
        self,
        zones: Iterable[TruthZone] = (),
        *,
        policy_id: str = "",
        version: str = TRUTH_CONTRACT_VERSION,
    ) -> None:
        self._zones: dict[str, TruthZone] = {}
        self._policy_id = policy_id.strip() or "truth.policy.default"
        self._version = version
        for zone in zones:
            self.register(zone)

    @property
    def policy_id(self) -> str:
        """The declared identity of this policy."""
        return self._policy_id

    @property
    def version(self) -> str:
        """The declared contract version this policy speaks."""
        return self._version

    @property
    def count(self) -> int:
        """How many zones this policy declares."""
        return len(self._zones)

    def register(self, zone: TruthZone) -> TruthZone:
        """Declare ``zone``; idempotent by identity, fail-closed on redefinition."""
        if not isinstance(zone, TruthZone):
            raise TruthPolicyError("policy accepts only TruthZone declarations")
        existing = self._zones.get(zone.zone_id)
        if existing is not None:
            if existing.fingerprint() != zone.fingerprint():
                raise TruthPolicyError(
                    "zone already declared with a different body", zone_id=zone.zone_id
                )
            return existing
        self._zones[zone.zone_id] = zone
        return zone

    def register_all(self, zones: Iterable[TruthZone]) -> tuple[TruthZone, ...]:
        """Declare every zone in ``zones``, returning them in resolution order."""
        for zone in zones:
            self.register(zone)
        return self.zones()

    def zone(self, zone_id: str) -> TruthZone:
        """The declared zone ``zone_id``; raises when undeclared (fail-closed)."""
        try:
            return self._zones[zone_id]
        except KeyError as exc:
            raise TruthPolicyError("unknown truth zone", zone_id=zone_id) from exc

    def zones(self) -> tuple[TruthZone, ...]:
        """Every declared zone in deterministic resolution order."""
        return tuple(sorted(self._zones.values(), key=lambda zone: zone.order_key))

    def zone_ids(self) -> tuple[str, ...]:
        """The declared zone identities in resolution order."""
        return tuple(zone.zone_id for zone in self.zones())

    def of_class(self, truth_class: TruthClass | str) -> tuple[TruthZone, ...]:
        """Every declared zone of ``truth_class``, in resolution order."""
        resolved = TruthClass.coerce(truth_class)
        return tuple(zone for zone in self.zones() if zone.truth_class is resolved)

    def home_zones(self) -> tuple[TruthZone, ...]:
        """Every zone a project declared eligible to hold canonical ownership."""
        return tuple(zone for zone in self.zones() if zone.canonical_home_eligible)

    def classify(self, locator: str) -> TruthClassification:
        """Classify ``locator`` by declared policy. Total, deterministic, never guessing."""
        normalized = normalize_locator(locator)
        if not normalized:
            raise TruthPolicyError("cannot classify an empty locator")
        for zone in self.zones():
            selector = zone.matching_selector(normalized)
            if selector is None:
                continue
            return TruthClassification.create(
                normalized,
                zone.truth_class,
                zone_id=zone.zone_id,
                rule=RULE_DECLARED_ZONE,
                precedence=zone.precedence,
                authority=zone.authority,
                canonical_home_eligible=zone.canonical_home_eligible,
                selector_id=selector.selector_id,
            )
        return TruthClassification.create(
            normalized, TruthClass.UNCLASSIFIED, rule=RULE_NO_DECLARED_ZONE
        )

    def classify_all(self, locators: Iterable[str]) -> TruthPartition:
        """Classify a whole population into a deterministic :class:`TruthPartition`."""
        seen: set[str] = set()
        results: list[TruthClassification] = []
        for locator in locators:
            normalized = normalize_locator(locator)
            if not normalized or normalized in seen:
                continue
            seen.add(normalized)
            results.append(self.classify(normalized))
        return TruthPartition.create(results)

    def is_canonical_home(self, locator: str) -> bool:
        """Whether ``locator`` sits in a zone a project declared able to own subjects."""
        return self.classify(locator).canonical_home_eligible

    def to_dict(self) -> dict[str, Any]:
        """A JSON-serialisable projection of this policy."""
        return {
            "policy_id": self._policy_id,
            "version": self._version,
            "zone_count": self.count,
            "zones": [zone.to_dict() for zone in self.zones()],
        }

    def fingerprint(self) -> str:
        """The deterministic content fingerprint of this policy."""
        return content_hash(self.to_dict())

    @classmethod
    def from_document(cls, document: Mapping[str, Any]) -> TruthPolicy:
        """Build a policy from a declared document — the only place paths are named."""
        if not isinstance(document, Mapping):
            raise TruthPolicyError("truth policy document must be a mapping")
        zones = document.get("zones")
        if not isinstance(zones, Sequence) or isinstance(zones, str | bytes):
            raise TruthPolicyError("truth policy document requires a 'zones' sequence")
        policy = cls(
            policy_id=str(document.get("policy_id", "")),
            version=str(document.get("version", TRUTH_CONTRACT_VERSION)),
        )
        for declaration in zones:
            policy.register(TruthZone.from_dict(declaration))
        if policy.count == 0:
            raise TruthPolicyError("truth policy declares no zones", policy_id=policy.policy_id)
        return policy

    def to_document(self) -> dict[str, Any]:
        """The declared-document form of this policy (round-trips :meth:`from_document`)."""
        return {
            "policy_id": self._policy_id,
            "version": self._version,
            "zones": [
                {
                    "zone_id": zone.zone_id,
                    "truth_class": zone.truth_class.value,
                    "precedence": zone.precedence,
                    "authority": zone.authority,
                    "canonical_home_eligible": zone.canonical_home_eligible,
                    "description": zone.description,
                    "selectors": [
                        {"kind": selector.kind.value, "value": selector.value}
                        for selector in zone.selectors
                    ],
                }
                for zone in self.zones()
            ],
        }


def load_truth_policy(path: Path | str) -> TruthPolicy:
    """Load a declared truth-policy document from ``path`` (fail-closed)."""
    target = Path(path)
    try:
        raw = target.read_text("utf-8")
    except OSError as exc:
        raise TruthPolicyError(
            "truth policy document could not be read", path=str(target), detail=str(exc)
        ) from exc
    try:
        document = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise TruthPolicyError(
            "truth policy document is not valid JSON", path=str(target), detail=str(exc)
        ) from exc
    return TruthPolicy.from_document(document)


def catalog_path(filename: str = DEFAULT_CATALOG_FILENAME) -> Path:
    """The packaged catalogue path for ``filename`` (no repository path is assumed)."""
    return Path(__file__).resolve().parent / CATALOG_DIRNAME / filename


def default_truth_policy(filename: str = DEFAULT_CATALOG_FILENAME) -> TruthPolicy:
    """The declared truth policy shipped in the packaged catalogue."""
    return load_truth_policy(catalog_path(filename))


__all__ = [
    "CATALOG_DIRNAME",
    "DEFAULT_CATALOG_FILENAME",
    "TruthPartition",
    "TruthPolicy",
    "load_truth_policy",
    "catalog_path",
    "default_truth_policy",
]
