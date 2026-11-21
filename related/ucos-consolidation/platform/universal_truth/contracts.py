"""UCOS-URTF-001 — Repository Truth vocabulary & contracts.

The deterministic vocabulary in which *Repository Truth* is declared, for **any**
repository — never for one repository, one dataset, or one measurement.

The constitutional separation this framework makes reusable:

    * **CANONICAL** — the one authoritative statement of a thing (may be a home).
    * **DECLARATION** — a governed declaration that binds (may be a home).
    * **EVIDENCE** — raw admitted material that *proves*, and therefore never owns.
    * **DERIVED** — a pure function of Truth; regenerable, therefore never owns.
    * **OPERATIONAL_MEMORY** — programme workspace; auditable, therefore never owns.
    * **HISTORICAL** — frozen prior state; superseded, therefore never owns.
    * **GENERATED** — machine-authored; owns only where a policy declares it does.
    * **TRANSIENT** — caches and build residue; never Truth.
    * **UNCLASSIFIED** — no zone declared it; an honest absence, never a default home.

Two invariants are enforced *structurally* rather than left to each engine:

    1. Ownership eligibility is a property of a **declared zone**, never of a path
       literal. No path is ever hardcoded in this framework.
    2. Classes that cannot constitutionally own a subject (:data:`NON_HOME_TRUTH_CLASSES`)
       may never be declared canonical-home eligible — the declaration itself fails closed.

Every identity is content-addressed (deterministic, reproducible; IMP-007 §5) and holds
no wall-clock. Truth identities live in a disjoint ``UCOS-URT*`` namespace: a
classification can never be mistaken for the fact it classifies.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from enum import Enum
from fnmatch import fnmatchcase
from platform.foundation.contracts import ContractRef, content_hash
from platform.universal_truth.errors import TruthContractError
from typing import Any

#: The canonical identity of the Universal Repository Truth Framework instance.
URTF_ID = "UCOS-URTF-001"

#: The semantic version of the Repository Truth contract surface (AR-03/PL-05).
TRUTH_CONTRACT_VERSION = "1.0.0"


class TruthClass(str, Enum):
    """The constitutional classes of Repository Truth (project independent)."""

    CANONICAL = "canonical"
    DECLARATION = "declaration"
    EVIDENCE = "evidence"
    DERIVED = "derived"
    OPERATIONAL_MEMORY = "operational-memory"
    HISTORICAL = "historical"
    GENERATED = "generated"
    TRANSIENT = "transient"
    UNCLASSIFIED = "unclassified"

    @classmethod
    def coerce(cls, value: Any, *, context: str = "truth class") -> TruthClass:
        """Coerce ``value`` to a :class:`TruthClass`, failing closed (never silently)."""
        if isinstance(value, cls):
            return value
        if isinstance(value, str):
            try:
                return cls(value)
            except ValueError as exc:
                raise TruthContractError(
                    "unknown truth class", subject=context, value=value
                ) from exc
        raise TruthContractError("truth class must be a string", subject=context)


#: Classes that SHALL NEVER be declared a canonical home. Evidence proves but does not
#: own; derived output is regenerable; operational memory is a workspace; historical
#: state is superseded; transient data is not Truth; an absence is not a home.
NON_HOME_TRUTH_CLASSES: tuple[TruthClass, ...] = (
    TruthClass.EVIDENCE,
    TruthClass.DERIVED,
    TruthClass.OPERATIONAL_MEMORY,
    TruthClass.HISTORICAL,
    TruthClass.TRANSIENT,
    TruthClass.UNCLASSIFIED,
)

#: Classes whose content is authoritative Truth rather than a projection of it.
AUTHORITATIVE_TRUTH_CLASSES: tuple[TruthClass, ...] = (
    TruthClass.CANONICAL,
    TruthClass.DECLARATION,
)


class SelectorKind(str, Enum):
    """How a declared selector matches a locator. Data-declared, never hardcoded."""

    ROOT = "root"
    ROOT_FILE = "root-file"
    SEGMENT = "segment"
    PREFIX = "prefix"
    SUFFIX = "suffix"
    GLOB = "glob"
    EXACT = "exact"

    @classmethod
    def coerce(cls, value: Any, *, context: str = "selector kind") -> SelectorKind:
        """Coerce ``value`` to a :class:`SelectorKind`, failing closed."""
        if isinstance(value, cls):
            return value
        if isinstance(value, str):
            try:
                return cls(value)
            except ValueError as exc:
                raise TruthContractError(
                    "unknown selector kind", subject=context, value=value
                ) from exc
        raise TruthContractError("selector kind must be a string", subject=context)


def normalize_locator(locator: Any) -> str:
    """Normalise any locator to a canonical, comparable, separator-agnostic form."""
    if not isinstance(locator, str):
        raise TruthContractError("locator must be a string")
    text = locator.strip().replace("\\", "/")
    while text.startswith("./"):
        text = text[2:]
    text = text.strip("/")
    return "/".join(part for part in text.split("/") if part not in ("", "."))


def locator_segments(locator: str) -> tuple[str, ...]:
    """The ordered path segments of a normalised locator."""
    normalized = normalize_locator(locator)
    return tuple(normalized.split("/")) if normalized else ()


@dataclass(frozen=True, slots=True)
class PathSelector:
    """An immutable, content-addressed rule that decides whether a locator is in a zone."""

    kind: SelectorKind
    value: str
    selector_id: str = ""

    @classmethod
    def create(cls, kind: SelectorKind | str, value: str) -> PathSelector:
        """Build a validated selector with a content-addressed identity."""
        resolved = SelectorKind.coerce(kind)
        if not isinstance(value, str) or not value.strip():
            raise TruthContractError("selector value must be a non-empty string")
        normalized = value.strip().replace("\\", "/")
        if resolved in (SelectorKind.ROOT, SelectorKind.ROOT_FILE, SelectorKind.SEGMENT):
            normalized = normalized.strip("/")
            if "/" in normalized:
                raise TruthContractError(
                    "root/segment selector value must be a single path segment",
                    value=normalized,
                )
        core = {"kind": resolved.value, "value": normalized}
        return cls(
            kind=resolved,
            value=normalized,
            selector_id=f"UCOS-URTS-{content_hash(core)[:16]}",
        )

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> PathSelector:
        """Build a selector from a declared mapping (``{"kind": ..., "value": ...}``)."""
        if not isinstance(payload, Mapping):
            raise TruthContractError("selector declaration must be a mapping")
        if "kind" not in payload or "value" not in payload:
            raise TruthContractError("selector declaration requires 'kind' and 'value'")
        return cls.create(payload["kind"], payload["value"])

    def matches(self, locator: str) -> bool:
        """Whether ``locator`` falls under this selector (pure, order-independent)."""
        normalized = normalize_locator(locator)
        if not normalized:
            return False
        segments = tuple(normalized.split("/"))
        if self.kind is SelectorKind.ROOT:
            return segments[0] == self.value
        if self.kind is SelectorKind.ROOT_FILE:
            return len(segments) == 1 and fnmatchcase(segments[0], self.value)
        if self.kind is SelectorKind.SEGMENT:
            return self.value in segments
        if self.kind is SelectorKind.PREFIX:
            prefix = self.value.strip("/")
            return normalized == prefix or normalized.startswith(f"{prefix}/")
        if self.kind is SelectorKind.SUFFIX:
            return normalized.endswith(self.value)
        if self.kind is SelectorKind.GLOB:
            return fnmatchcase(normalized, self.value)
        return normalized == self.value.strip("/")

    def to_dict(self) -> dict[str, Any]:
        """A JSON-serialisable projection of this selector."""
        return {"selector_id": self.selector_id, "kind": self.kind.value, "value": self.value}

    def fingerprint(self) -> str:
        """The deterministic content fingerprint of this selector."""
        return content_hash(self.to_dict())


@dataclass(frozen=True, slots=True)
class TruthZone:
    """A declared region of Repository Truth: selectors bound to one constitutional class.

    A zone — not a path literal — is what a project declares. Ownership eligibility is a
    property of the zone, so the same policy shape governs every repository, dataset and
    measurement.
    """

    zone_id: str
    truth_class: TruthClass
    selectors: tuple[PathSelector, ...]
    precedence: int = 100
    authority: str = ""
    canonical_home_eligible: bool = False
    description: str = ""

    def __post_init__(self) -> None:
        if not isinstance(self.zone_id, str) or not self.zone_id.strip():
            raise TruthContractError("zone_id must be a non-empty string")
        if not isinstance(self.truth_class, TruthClass):
            raise TruthContractError("truth_class must be a TruthClass", zone_id=self.zone_id)
        if not self.selectors:
            raise TruthContractError("zone declares no selectors", zone_id=self.zone_id)
        for selector in self.selectors:
            if not isinstance(selector, PathSelector):
                raise TruthContractError(
                    "zone selectors must be PathSelector values", zone_id=self.zone_id
                )
        if not isinstance(self.precedence, int) or isinstance(self.precedence, bool):
            raise TruthContractError("zone precedence must be an int", zone_id=self.zone_id)
        if self.canonical_home_eligible and self.truth_class in NON_HOME_TRUTH_CLASSES:
            raise TruthContractError(
                "truth class can never be a canonical home",
                zone_id=self.zone_id,
                truth_class=self.truth_class.value,
            )
        if self.truth_class in AUTHORITATIVE_TRUTH_CLASSES and not self.authority:
            raise TruthContractError(
                "authoritative zone must declare an authority", zone_id=self.zone_id
            )

    @classmethod
    def create(
        cls,
        zone_id: str,
        truth_class: TruthClass | str,
        selectors: Iterable[PathSelector | Mapping[str, Any]],
        *,
        precedence: int = 100,
        authority: str = "",
        canonical_home_eligible: bool = False,
        description: str = "",
    ) -> TruthZone:
        """Build a validated zone, normalising and de-duplicating its selectors."""
        resolved: list[PathSelector] = []
        seen: set[str] = set()
        for selector in selectors:
            built = (
                selector if isinstance(selector, PathSelector) else PathSelector.from_dict(selector)
            )
            if built.selector_id in seen:
                continue
            seen.add(built.selector_id)
            resolved.append(built)
        return cls(
            zone_id=zone_id.strip(),
            truth_class=TruthClass.coerce(truth_class, context=f"zone {zone_id}"),
            selectors=tuple(sorted(resolved, key=lambda item: item.selector_id)),
            precedence=precedence,
            authority=authority.strip(),
            canonical_home_eligible=bool(canonical_home_eligible),
            description=description,
        )

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> TruthZone:
        """Build a zone from a declared mapping (the catalogue form)."""
        if not isinstance(payload, Mapping):
            raise TruthContractError("zone declaration must be a mapping")
        missing = [key for key in ("zone_id", "truth_class", "selectors") if key not in payload]
        if missing:
            raise TruthContractError("zone declaration is incomplete", missing=",".join(missing))
        selectors = payload["selectors"]
        if not isinstance(selectors, Iterable) or isinstance(selectors, str | bytes):
            raise TruthContractError(
                "zone selectors must be a sequence", zone_id=str(payload["zone_id"])
            )
        return cls.create(
            str(payload["zone_id"]),
            payload["truth_class"],
            selectors,
            precedence=int(payload.get("precedence", 100)),
            authority=str(payload.get("authority", "")),
            canonical_home_eligible=bool(payload.get("canonical_home_eligible", False)),
            description=str(payload.get("description", "")),
        )

    @property
    def authoritative(self) -> bool:
        """Whether this zone holds authoritative Truth rather than a projection of it."""
        return self.truth_class in AUTHORITATIVE_TRUTH_CLASSES

    @property
    def order_key(self) -> tuple[int, str]:
        """Deterministic resolution order: highest precedence first, then zone id."""
        return (-self.precedence, self.zone_id)

    def matches(self, locator: str) -> bool:
        """Whether any declared selector admits ``locator`` into this zone."""
        return any(selector.matches(locator) for selector in self.selectors)

    def matching_selector(self, locator: str) -> PathSelector | None:
        """The first (deterministically ordered) selector that admits ``locator``."""
        for selector in self.selectors:
            if selector.matches(locator):
                return selector
        return None

    def to_dict(self) -> dict[str, Any]:
        """A JSON-serialisable projection of this zone."""
        return {
            "zone_id": self.zone_id,
            "truth_class": self.truth_class.value,
            "selectors": [selector.to_dict() for selector in self.selectors],
            "precedence": self.precedence,
            "authority": self.authority,
            "canonical_home_eligible": self.canonical_home_eligible,
            "authoritative": self.authoritative,
            "description": self.description,
        }

    def fingerprint(self) -> str:
        """The deterministic content fingerprint of this zone."""
        return content_hash(self.to_dict())


#: The rule name recorded when no declared zone admits a locator (an honest absence).
RULE_NO_DECLARED_ZONE = "NO-DECLARED-ZONE"

#: The rule name recorded when a locator is admitted by a declared zone.
RULE_DECLARED_ZONE = "DECLARED-ZONE"


@dataclass(frozen=True, slots=True)
class TruthClassification:
    """The immutable, content-addressed classification of one locator by policy."""

    locator: str
    truth_class: TruthClass
    zone_id: str = ""
    rule: str = RULE_NO_DECLARED_ZONE
    precedence: int = 0
    authority: str = ""
    canonical_home_eligible: bool = False
    selector_id: str = ""
    classification_id: str = ""

    @classmethod
    def create(
        cls,
        locator: str,
        truth_class: TruthClass | str,
        *,
        zone_id: str = "",
        rule: str = RULE_NO_DECLARED_ZONE,
        precedence: int = 0,
        authority: str = "",
        canonical_home_eligible: bool = False,
        selector_id: str = "",
    ) -> TruthClassification:
        """Build a validated classification with a content-addressed identity."""
        resolved = TruthClass.coerce(truth_class, context="classification")
        normalized = normalize_locator(locator)
        if not normalized:
            raise TruthContractError("classification requires a non-empty locator")
        if canonical_home_eligible and resolved in NON_HOME_TRUTH_CLASSES:
            raise TruthContractError(
                "truth class can never be a canonical home",
                locator=normalized,
                truth_class=resolved.value,
            )
        core = {
            "locator": normalized,
            "truth_class": resolved.value,
            "zone_id": zone_id,
            "rule": rule,
        }
        return cls(
            locator=normalized,
            truth_class=resolved,
            zone_id=zone_id,
            rule=rule,
            precedence=precedence,
            authority=authority,
            canonical_home_eligible=bool(canonical_home_eligible),
            selector_id=selector_id,
            classification_id=f"UCOS-URTC-{content_hash(core)[:16]}",
        )

    @property
    def classified(self) -> bool:
        """Whether a declared zone admitted this locator."""
        return self.truth_class is not TruthClass.UNCLASSIFIED and bool(self.zone_id)

    @property
    def authoritative(self) -> bool:
        """Whether this locator holds authoritative Truth."""
        return self.truth_class in AUTHORITATIVE_TRUTH_CLASSES

    def to_dict(self) -> dict[str, Any]:
        """A JSON-serialisable projection of this classification."""
        return {
            "classification_id": self.classification_id,
            "locator": self.locator,
            "truth_class": self.truth_class.value,
            "zone_id": self.zone_id,
            "rule": self.rule,
            "precedence": self.precedence,
            "authority": self.authority,
            "canonical_home_eligible": self.canonical_home_eligible,
            "selector_id": self.selector_id,
            "classified": self.classified,
        }

    def fingerprint(self) -> str:
        """The deterministic content fingerprint of this classification."""
        return content_hash(self.to_dict())


@dataclass(frozen=True, slots=True)
class Subject:
    """A thing whose Truth is measured: a concept, capability, artifact or record.

    A subject is deliberately minimal and project independent — an identity plus the
    locators that mention it. Every Foundation framework (ownership, assimilation,
    measurement) consumes subjects, so no framework needs to know what a project calls
    its things.

    ``roles`` optionally tags a *subset* of those locators with a declared role name. This
    is what lets a project reuse a measurement it already owns — "these locators are the
    definitional ones", decided by whichever instrument owns that question — without any
    Foundation framework learning what the role means. A framework asks for a role by name;
    an undeclared role is simply empty, never guessed.
    """

    subject_id: str
    locators: tuple[str, ...] = ()
    attributes: tuple[tuple[str, str], ...] = ()
    roles: tuple[tuple[str, tuple[str, ...]], ...] = ()
    subject_key: str = ""

    @classmethod
    def create(
        cls,
        subject_id: str,
        *,
        locators: Iterable[str] = (),
        attributes: Mapping[str, str] | None = None,
        roles: Mapping[str, Iterable[str]] | None = None,
    ) -> Subject:
        """Build a validated subject with normalised, de-duplicated locators.

        Every role locator is also a locator of the subject: a role narrows the population,
        it never introduces one, so a role can never smuggle in a locator the subject does
        not carry.
        """
        if not isinstance(subject_id, str) or not subject_id.strip():
            raise TruthContractError("subject_id must be a non-empty string")
        tagged: dict[str, tuple[str, ...]] = {}
        for name, values in dict(roles or {}).items():
            normalized_role = str(name).strip()
            if not normalized_role:
                raise TruthContractError("role name must be a non-empty string")
            members = sorted({normalize_locator(item) for item in values if str(item).strip()})
            if members:
                tagged[normalized_role] = tuple(members)
        union = {normalize_locator(item) for item in locators if str(item).strip()}
        for members in tagged.values():
            union.update(members)
        normalized = sorted(union)
        attrs = tuple(sorted((str(k), str(v)) for k, v in dict(attributes or {}).items()))
        role_pairs = tuple(sorted((name, tagged[name]) for name in tagged))
        core = {
            "subject_id": subject_id.strip(),
            "locators": normalized,
            "attributes": list(attrs),
            "roles": {name: list(values) for name, values in role_pairs},
        }
        return cls(
            subject_id=subject_id.strip(),
            locators=tuple(normalized),
            attributes=attrs,
            roles=role_pairs,
            subject_key=f"UCOS-URTJ-{content_hash(core)[:16]}",
        )

    def attribute(self, name: str, default: str = "") -> str:
        """The declared attribute ``name``, or ``default`` when absent."""
        for key, value in self.attributes:
            if key == name:
                return value
        return default

    def role(self, name: str) -> tuple[str, ...]:
        """The locators tagged with declared role ``name`` (empty when undeclared)."""
        for key, values in self.roles:
            if key == name:
                return values
        return ()

    def role_names(self) -> tuple[str, ...]:
        """Every declared role name carried by this subject, in order."""
        return tuple(name for name, _ in self.roles)

    def to_dict(self) -> dict[str, Any]:
        """A JSON-serialisable projection of this subject."""
        return {
            "subject_key": self.subject_key,
            "subject_id": self.subject_id,
            "locators": list(self.locators),
            "attributes": {key: value for key, value in self.attributes},
            "roles": {name: list(values) for name, values in self.roles},
        }

    def fingerprint(self) -> str:
        """The deterministic content fingerprint of this subject."""
        return content_hash(self.to_dict())


_TRUTH_CONTRACT_NAMES: tuple[tuple[str, str], ...] = (
    ("truth.policy.classify", "Classify a locator against declared Repository Truth zones."),
    ("truth.policy.partition", "Partition a locator population by constitutional truth class."),
    ("truth.policy.load", "Load a declared Repository Truth policy document."),
    ("truth.projection.subjects", "Project subjects from a declared Truth document."),
)

#: The versioned published contract surface of the Repository Truth Framework.
TRUTH_CONTRACTS: tuple[ContractRef, ...] = tuple(
    ContractRef(name, TRUTH_CONTRACT_VERSION) for name, _ in _TRUTH_CONTRACT_NAMES
)


def truth_contract_names() -> tuple[str, ...]:
    """The published Repository Truth contract names, in declaration order."""
    return tuple(name for name, _ in _TRUTH_CONTRACT_NAMES)


__all__ = [
    "URTF_ID",
    "TRUTH_CONTRACT_VERSION",
    "TruthClass",
    "NON_HOME_TRUTH_CLASSES",
    "AUTHORITATIVE_TRUTH_CLASSES",
    "SelectorKind",
    "normalize_locator",
    "locator_segments",
    "PathSelector",
    "TruthZone",
    "RULE_DECLARED_ZONE",
    "RULE_NO_DECLARED_ZONE",
    "TruthClassification",
    "Subject",
    "TRUTH_CONTRACTS",
    "truth_contract_names",
]
