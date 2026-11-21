"""UCOS-URTF-001 — Declared locator eligibility.

A declared *zone* decides whether a locator's **class** may hold canonical ownership. That is
necessary but not always sufficient: a project may additionally require that the specific
artifact be **registered**, be of a particular form, and not be derived residue inside an
otherwise eligible zone. Those are three more project facts, and under UFC-13 they belong in a
declaration rather than in whichever engine happens to need them.

:class:`EligibilityLedger` is that declaration. It is a pure, data-driven predicate over a
locator:

    1. **registration** — where a ledger of registered locators is declared, membership is
       required. This is the executable form of "the canonical owner must be registered".
    2. **form** — where required suffixes are declared, the locator must carry one. A JSON
       projection is not a constitutional declaration in most projects, and where it is, the
       project simply declares that suffix too.
    3. **residue** — where excluded segments are declared, a locator containing one is
       inadmissible however eligible its zone. Evidence and generated output sitting inside a
       canonical tree does not become canonical by adjacency.

An *undeclared* dimension admits everything. That is the honest default: silence in a
declaration means "this project imposes no such requirement", never "this project requires
something the framework guessed".
"""

from __future__ import annotations

import json
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from platform.foundation.contracts import content_hash
from platform.universal_truth.contracts import locator_segments, normalize_locator
from platform.universal_truth.errors import TruthEligibilityError
from platform.universal_truth.policy import TruthPolicy
from typing import Any

#: Reason codes. Each names a *different* deficit so a residue can be triaged rather than
#: treated as one undifferentiated refusal.
REASON_ELIGIBLE = "ELIGIBLE"
REASON_ZONE_INELIGIBLE = "ZONE-NOT-CANONICAL-HOME-ELIGIBLE"
REASON_NOT_REGISTERED = "LOCATOR-NOT-REGISTERED"
REASON_FORM_NOT_ADMITTED = "LOCATOR-FORM-NOT-ADMITTED"
REASON_DERIVED_RESIDUE = "LOCATOR-IS-DERIVED-RESIDUE"

#: Every reason this module can report, in declaration order.
ELIGIBILITY_REASONS: tuple[str, ...] = (
    REASON_ELIGIBLE,
    REASON_ZONE_INELIGIBLE,
    REASON_NOT_REGISTERED,
    REASON_FORM_NOT_ADMITTED,
    REASON_DERIVED_RESIDUE,
)


@dataclass(frozen=True, slots=True)
class EligibilityVerdict:
    """Why one locator is, or is not, eligible to hold canonical ownership."""

    locator: str
    eligible: bool
    reason: str

    def to_dict(self) -> dict[str, Any]:
        """A JSON-serialisable projection of this verdict."""
        return {"locator": self.locator, "eligible": self.eligible, "reason": self.reason}


@dataclass(frozen=True, slots=True)
class EligibilityLedger:
    """A declared, data-driven predicate deciding which locators may hold ownership.

    Immutable and content-addressed, so a determination can pin exactly which eligibility
    rules it was made under.
    """

    ledger_id: str = "truth.eligibility.default"
    registered: frozenset[str] = frozenset()
    require_registration: bool = False
    admitted_suffixes: tuple[str, ...] = ()
    excluded_segments: tuple[str, ...] = ()
    description: str = ""

    @classmethod
    def create(
        cls,
        *,
        ledger_id: str = "truth.eligibility.default",
        registered: Iterable[str] | None = None,
        require_registration: bool | None = None,
        admitted_suffixes: Iterable[str] = (),
        excluded_segments: Iterable[str] = (),
        description: str = "",
    ) -> EligibilityLedger:
        """Build a validated ledger.

        ``require_registration`` defaults to *whether a registration ledger was supplied at
        all*: supplying one and not enforcing it would be a declaration with no effect. The
        requirement may also be declared **before** the set is known — a project declares the
        rule in its specialisation and the set is projected from a register it already keeps —
        so an empty set with the requirement declared is legal here and fails closed at
        decision time instead (:meth:`verdict`). A declaration is a declaration; a decision
        needs the data.
        """
        ledger = frozenset(
            normalize_locator(item) for item in (registered or ()) if str(item).strip()
        )
        enforce = (
            bool(registered is not None)
            if require_registration is None
            else bool(require_registration)
        )
        suffixes = tuple(sorted({str(item) for item in admitted_suffixes if str(item).strip()}))
        segments = tuple(sorted({str(item) for item in excluded_segments if str(item).strip()}))
        return cls(
            ledger_id=ledger_id.strip() or "truth.eligibility.default",
            registered=ledger,
            require_registration=enforce,
            admitted_suffixes=suffixes,
            excluded_segments=segments,
            description=description,
        )

    @classmethod
    def from_document(
        cls, document: Mapping[str, Any], *, registered: Iterable[str] | None = None
    ) -> EligibilityLedger:
        """Build from a declared document, with the registration ledger supplied separately.

        The registered set is normally a *projection* a project already keeps (an artifact
        register, a governance registry), so it is passed as data rather than restated in the
        declaration — Knowledge Once.
        """
        if not isinstance(document, Mapping):
            raise TruthEligibilityError("eligibility document must be a mapping")
        for key in ("admitted_suffixes", "excluded_segments"):
            value = document.get(key, ())
            if not isinstance(value, Sequence) or isinstance(value, str | bytes):
                raise TruthEligibilityError(
                    f"'{key}' must be a sequence", ledger_id=str(document.get("ledger_id", ""))
                )
        return cls.create(
            ledger_id=str(document.get("ledger_id", "")),
            registered=registered,
            require_registration=document.get("require_registration"),
            admitted_suffixes=document.get("admitted_suffixes", ()),
            excluded_segments=document.get("excluded_segments", ()),
            description=str(document.get("description", "")),
        )

    @property
    def registration_count(self) -> int:
        """How many locators the registration ledger declares."""
        return len(self.registered)

    @property
    def enforces_anything(self) -> bool:
        """Whether this ledger imposes any requirement at all."""
        return bool(self.require_registration or self.admitted_suffixes or self.excluded_segments)

    def verdict(self, locator: str) -> EligibilityVerdict:
        """Decide ``locator`` against every declared dimension, reporting the first deficit."""
        normalized = normalize_locator(locator)
        if not normalized:
            raise TruthEligibilityError("cannot decide an empty locator", ledger_id=self.ledger_id)
        if self.require_registration:
            if not self.registered:
                raise TruthEligibilityError(
                    "registration is required but no registered locator has been supplied",
                    ledger_id=self.ledger_id,
                )
            if normalized not in self.registered:
                return EligibilityVerdict(normalized, False, REASON_NOT_REGISTERED)
        if self.admitted_suffixes and not any(
            normalized.endswith(suffix) for suffix in self.admitted_suffixes
        ):
            return EligibilityVerdict(normalized, False, REASON_FORM_NOT_ADMITTED)
        if self.excluded_segments:
            segments = locator_segments(normalized)
            if any(
                excluded in segments or excluded in normalized
                for excluded in self.excluded_segments
            ):
                return EligibilityVerdict(normalized, False, REASON_DERIVED_RESIDUE)
        return EligibilityVerdict(normalized, True, REASON_ELIGIBLE)

    def admits(self, locator: str) -> bool:
        """Whether ``locator`` satisfies every declared eligibility dimension."""
        return self.verdict(locator).eligible

    def filter(self, locators: Iterable[str]) -> tuple[str, ...]:
        """Every admitted locator, normalised, de-duplicated and ordered."""
        return tuple(sorted({v.locator for v in self.verdicts(locators) if v.eligible}))

    def verdicts(self, locators: Iterable[str]) -> tuple[EligibilityVerdict, ...]:
        """A verdict per distinct locator, ordered by locator."""
        seen: dict[str, EligibilityVerdict] = {}
        for locator in locators:
            normalized = normalize_locator(locator)
            if not normalized or normalized in seen:
                continue
            seen[normalized] = self.verdict(normalized)
        return tuple(seen[key] for key in sorted(seen))

    def to_dict(self) -> dict[str, Any]:
        """A JSON-serialisable projection of this ledger.

        The registered set is summarised by count and content hash rather than enumerated: a
        registration ledger is a project projection, and copying it into every determination
        would both bloat the record and restate knowledge that is owned elsewhere.
        """
        return {
            "ledger_id": self.ledger_id,
            "require_registration": self.require_registration,
            "registration_count": self.registration_count,
            "registration_digest": content_hash(sorted(self.registered)),
            "admitted_suffixes": list(self.admitted_suffixes),
            "excluded_segments": list(self.excluded_segments),
            "enforces_anything": self.enforces_anything,
            "description": self.description,
        }

    def fingerprint(self) -> str:
        """The deterministic content fingerprint of this ledger."""
        return content_hash(self.to_dict())


#: A ledger that imposes nothing — the honest identity element.
def open_ledger(ledger_id: str = "truth.eligibility.open") -> EligibilityLedger:
    """A ledger admitting every locator (imposes no project requirement)."""
    return EligibilityLedger.create(
        ledger_id=ledger_id,
        description="Imposes no additional eligibility requirement beyond zone class.",
    )


def load_eligibility_ledger(
    path: Path | str, *, registered: Iterable[str] | None = None
) -> EligibilityLedger:
    """Load a declared eligibility document from ``path`` (fail-closed)."""
    target = Path(path)
    try:
        document = json.loads(target.read_text("utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise TruthEligibilityError(
            "eligibility document could not be read", path=str(target), detail=str(exc)
        ) from exc
    return EligibilityLedger.from_document(document, registered=registered)


class CanonicalHomePolicy:
    """The composition of a Truth policy with a declared eligibility ledger.

    This is the one place "may this locator hold canonical ownership?" is answered. A zone
    decides the class; the ledger decides the artifact. Neither is a hardcoded path, and no
    consumer needs to know that two questions were asked.
    """

    __slots__ = ("_policy", "_ledger")

    def __init__(self, policy: TruthPolicy, ledger: EligibilityLedger | None = None) -> None:
        if not isinstance(policy, TruthPolicy):
            raise TruthEligibilityError("canonical-home policy requires a TruthPolicy")
        if ledger is not None and not isinstance(ledger, EligibilityLedger):
            raise TruthEligibilityError("eligibility must be an EligibilityLedger when supplied")
        self._policy = policy
        self._ledger = ledger if ledger is not None else open_ledger()

    @property
    def policy(self) -> TruthPolicy:
        """The declared Repository Truth policy deciding zone class."""
        return self._policy

    @property
    def ledger(self) -> EligibilityLedger:
        """The declared eligibility ledger deciding artifact admissibility."""
        return self._ledger

    def verdict(self, locator: str) -> EligibilityVerdict:
        """Decide ``locator`` against the zone first, then the ledger."""
        classification = self._policy.classify(locator)
        if not classification.canonical_home_eligible:
            return EligibilityVerdict(classification.locator, False, REASON_ZONE_INELIGIBLE)
        return self._ledger.verdict(classification.locator)

    def admits(self, locator: str) -> bool:
        """Whether ``locator`` may hold canonical ownership under both declarations."""
        return self.verdict(locator).eligible

    def authority(self, locator: str) -> str:
        """The declared authority of ``locator``'s zone, or ``""`` when it may not own."""
        if not self.admits(locator):
            return ""
        classification = self._policy.classify(locator)
        return classification.authority or classification.zone_id

    def verdicts(self, locators: Iterable[str]) -> tuple[EligibilityVerdict, ...]:
        """A verdict per distinct locator, ordered by locator."""
        seen: dict[str, EligibilityVerdict] = {}
        for locator in locators:
            normalized = normalize_locator(locator)
            if not normalized or normalized in seen:
                continue
            seen[normalized] = self.verdict(normalized)
        return tuple(seen[key] for key in sorted(seen))

    def by_reason(self, locators: Iterable[str]) -> dict[str, list[str]]:
        """The population grouped by verdict reason, so a residue can be triaged."""
        grouped: dict[str, list[str]] = {}
        for verdict in self.verdicts(locators):
            grouped.setdefault(verdict.reason, []).append(verdict.locator)
        return {reason: sorted(items) for reason, items in sorted(grouped.items())}

    def to_dict(self) -> dict[str, Any]:
        """A JSON-serialisable projection of this composition."""
        return {"policy": self._policy.to_dict(), "eligibility": self._ledger.to_dict()}

    def fingerprint(self) -> str:
        """The deterministic content fingerprint of this composition."""
        return content_hash(self.to_dict())


__all__ = [
    "ELIGIBILITY_REASONS",
    "REASON_DERIVED_RESIDUE",
    "REASON_ELIGIBLE",
    "REASON_FORM_NOT_ADMITTED",
    "REASON_NOT_REGISTERED",
    "REASON_ZONE_INELIGIBLE",
    "CanonicalHomePolicy",
    "EligibilityLedger",
    "EligibilityVerdict",
    "load_eligibility_ledger",
    "open_ledger",
]
