"""UCOS-UOF-001 — Ownership Declaration Contract & ownership vocabulary.

This module *is* the Ownership Declaration Contract: the constitutional requirements a
claim must satisfy before the platform will call it canonical ownership — for any project,
any subject, any evidence provider.

    * ``OWN-REQ-001`` **DECLARED-NOT-INFERRED** — ownership rests on constitutive declared
      evidence. Corroboration (registration, mention, coincidence) never establishes it.
    * ``OWN-REQ-002`` **EXACTLY-ONE-OWNER** — at most one canonical owner per subject.
    * ``OWN-REQ-003`` **ELIGIBLE-HOME-ZONE** — the evidence locator sits in a zone that
      Repository Truth policy declares able to hold ownership.
    * ``OWN-REQ-004`` **REGISTERED-SUBJECT** — where a registration authority is declared,
      registration is eligibility.
    * ``OWN-REQ-005`` **SETTLED-CONTEST** — a contest is settled only by declared
      precedence, never arbitrarily and never by insertion order.
    * ``OWN-REQ-006`` **AUTHORITY-BOUND** — the declaration names the authority that binds it.
    * ``OWN-REQ-007`` **EVIDENCE-CITED** — the declaration cites the evidence it rests on.

An unmet mandatory requirement yields an honest UNRESOLVED (or CONTESTED) standing. The
framework has no code path that invents an owner: that is the whole point of the capability.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from enum import Enum
from platform.foundation.contracts import ContractRef, content_hash
from platform.universal_ownership.errors import OwnershipContractError
from typing import Any

#: The canonical identity of the Universal Ownership Framework instance.
UOF_ID = "UCOS-UOF-001"

#: The semantic version of the ownership contract surface (AR-03/PL-05).
OWNERSHIP_CONTRACT_VERSION = "1.0.0"

#: The owner recorded when no owner has been declared. Never a real owner.
UNASSIGNED_OWNER = "UNASSIGNED"


class EvidenceKind(str, Enum):
    """The kinds of ownership evidence a provider may produce."""

    DECLARED_ASSIGNMENT = "declared-assignment"
    DECLARED_IDENTITY = "declared-identity"
    DEFINITIONAL_LOCATOR = "definitional-locator"
    DELEGATION = "delegation"
    REGISTRATION = "registration"
    CORROBORATION = "corroboration"

    @classmethod
    def coerce(cls, value: Any, *, subject: str = "evidence kind") -> EvidenceKind:
        """Coerce ``value`` to an :class:`EvidenceKind`, failing closed."""
        if isinstance(value, cls):
            return value
        if isinstance(value, str):
            try:
                return cls(value)
            except ValueError as exc:
                raise OwnershipContractError(
                    "unknown evidence kind", subject=subject, value=value
                ) from exc
        raise OwnershipContractError("evidence kind must be a string", subject=subject)

    @property
    def constitutive(self) -> bool:
        """Whether this kind can *establish* ownership rather than merely corroborate it."""
        return self in CONSTITUTIVE_EVIDENCE_KINDS


#: Evidence kinds that may establish canonical ownership (OWN-REQ-001).
CONSTITUTIVE_EVIDENCE_KINDS: tuple[EvidenceKind, ...] = (
    EvidenceKind.DECLARED_ASSIGNMENT,
    EvidenceKind.DECLARED_IDENTITY,
    EvidenceKind.DEFINITIONAL_LOCATOR,
    EvidenceKind.DELEGATION,
)

#: Evidence kinds that corroborate an established claim but can never create one.
CORROBORATIVE_EVIDENCE_KINDS: tuple[EvidenceKind, ...] = (
    EvidenceKind.REGISTRATION,
    EvidenceKind.CORROBORATION,
)


class OwnershipStanding(str, Enum):
    """The standing of a subject's ownership after determination."""

    DECLARED = "declared"
    CONTESTED = "contested"
    UNRESOLVED = "unresolved"


#: Why a subject's ownership could not be honestly declared.
REASON_NO_EVIDENCE = "NO-OWNERSHIP-EVIDENCE"
REASON_NO_CONSTITUTIVE_DECLARATION = "NO-CONSTITUTIVE-OWNERSHIP-DECLARATION"
REASON_INELIGIBLE_ZONE = "EVIDENCE-NOT-IN-CANONICAL-HOME-ZONE"
REASON_CONTEST_UNSETTLED = "CONTEST-NOT-SETTLED-BY-DECLARED-PRECEDENCE"
REASON_SUBJECT_NOT_REGISTERED = "SUBJECT-NOT-REGISTERED"

#: The complete, closed reason vocabulary (an absence is always named, never blank).
UNRESOLVED_REASONS: tuple[str, ...] = (
    REASON_NO_EVIDENCE,
    REASON_NO_CONSTITUTIVE_DECLARATION,
    REASON_INELIGIBLE_ZONE,
    REASON_CONTEST_UNSETTLED,
    REASON_SUBJECT_NOT_REGISTERED,
)

#: How a declaration was reached.
RULE_SOLE_DECLARATION = "SOLE-CONSTITUTIVE-DECLARATION"
RULE_CONTEST_SETTLED = "CONTEST-SETTLED-BY-DECLARED-PRECEDENCE"


class OwnershipGranularity(str, Enum):
    """At what grain an owner is named. Declared per project, never assumed.

    Some projects hold ownership at the level of a governing **authority**: whichever
    document inside that authority's zone carries the subject, the authority owns it, and
    two documents in one zone are not a contest. Others hold it at the level of the
    **locator**: the canonical home is one artifact, and two artifacts claiming one subject
    is a duplicate home that must be adjudicated, not absorbed.

    Both are defensible constitutional positions, so neither is hardcoded. The grain is
    declared, and the same determination engine enforces whichever was declared.
    """

    AUTHORITY = "authority"
    LOCATOR = "locator"

    @classmethod
    def coerce(cls, value: Any, *, subject: str = "ownership granularity") -> OwnershipGranularity:
        """Coerce ``value`` to a granularity, failing closed (never silently)."""
        if isinstance(value, cls):
            return value
        if isinstance(value, str):
            try:
                return cls(value)
            except ValueError as exc:
                raise OwnershipContractError(
                    "unknown ownership granularity", subject=subject, value=value
                ) from exc
        raise OwnershipContractError("ownership granularity must be a string", subject=subject)


@dataclass(frozen=True, slots=True)
class OwnershipEvidence:
    """An immutable, content-addressed piece of ownership evidence.

    Evidence is a *finding*, not a decision: it names the owner a provider observed to be
    declared, where that declaration lives, and under whose authority the provider speaks.
    """

    subject_id: str
    owner: str
    kind: EvidenceKind
    locator: str = ""
    provider_id: str = ""
    authority: str = ""
    precedence: int = 100
    detail: str = ""
    evidence_id: str = ""

    @classmethod
    def create(
        cls,
        subject_id: str,
        owner: str,
        kind: EvidenceKind | str,
        *,
        locator: str = "",
        provider_id: str = "",
        authority: str = "",
        precedence: int = 100,
        detail: str = "",
    ) -> OwnershipEvidence:
        """Build validated evidence with a content-addressed identity."""
        if not isinstance(subject_id, str) or not subject_id.strip():
            raise OwnershipContractError("evidence requires a subject_id")
        if not isinstance(owner, str) or not owner.strip():
            raise OwnershipContractError("evidence requires an owner", subject=subject_id)
        if owner.strip() == UNASSIGNED_OWNER:
            raise OwnershipContractError(
                "UNASSIGNED is not an owner", subject=subject_id, owner=owner
            )
        resolved = EvidenceKind.coerce(kind, subject=subject_id)
        if not isinstance(precedence, int) or isinstance(precedence, bool):
            raise OwnershipContractError("evidence precedence must be an int", subject=subject_id)
        core = {
            "subject_id": subject_id.strip(),
            "owner": owner.strip(),
            "kind": resolved.value,
            "locator": locator.strip(),
            "provider_id": provider_id.strip(),
        }
        return cls(
            subject_id=subject_id.strip(),
            owner=owner.strip(),
            kind=resolved,
            locator=locator.strip(),
            provider_id=provider_id.strip(),
            authority=authority.strip(),
            precedence=precedence,
            detail=detail,
            evidence_id=f"UCOS-UOFE-{content_hash(core)[:16]}",
        )

    @property
    def constitutive(self) -> bool:
        """Whether this evidence may establish ownership (OWN-REQ-001)."""
        return self.kind.constitutive

    @property
    def order_key(self) -> tuple[int, int, str, str]:
        """Deterministic strength order: precedence, then constitutive, then identity."""
        return (-self.precedence, 0 if self.constitutive else 1, self.owner, self.evidence_id)

    def to_dict(self) -> dict[str, Any]:
        """A JSON-serialisable projection of this evidence."""
        return {
            "evidence_id": self.evidence_id,
            "subject_id": self.subject_id,
            "owner": self.owner,
            "kind": self.kind.value,
            "locator": self.locator,
            "provider_id": self.provider_id,
            "authority": self.authority,
            "precedence": self.precedence,
            "constitutive": self.constitutive,
            "detail": self.detail,
        }

    def fingerprint(self) -> str:
        """The deterministic content fingerprint of this evidence."""
        return content_hash(self.to_dict())


@dataclass(frozen=True, slots=True)
class OwnershipRequirement:
    """One constitutional requirement of the Ownership Declaration Contract."""

    requirement_id: str
    statement: str
    mandatory: bool = True

    def to_dict(self) -> dict[str, Any]:
        """A JSON-serialisable projection of this requirement."""
        return {
            "requirement_id": self.requirement_id,
            "statement": self.statement,
            "mandatory": self.mandatory,
        }


#: The Ownership Declaration Contract requirements, in constitutional order.
OWNERSHIP_REQUIREMENTS: tuple[OwnershipRequirement, ...] = (
    OwnershipRequirement(
        "OWN-REQ-001",
        "Canonical ownership SHALL rest on constitutive declared evidence and SHALL NEVER "
        "be inferred, implied, or filled in to close a measurement.",
    ),
    OwnershipRequirement(
        "OWN-REQ-002",
        "A subject SHALL have at most one canonical owner; multiple surviving claims are a "
        "contest, never a merge.",
    ),
    OwnershipRequirement(
        "OWN-REQ-003",
        "Evidence SHALL be located in a zone that Repository Truth policy declares eligible "
        "to hold canonical ownership.",
    ),
    OwnershipRequirement(
        "OWN-REQ-004",
        "Where a registration authority is declared, the subject SHALL be registered; "
        "registration is eligibility.",
    ),
    OwnershipRequirement(
        "OWN-REQ-005",
        "A contest SHALL be settled only by declared precedence, never arbitrarily and never "
        "by insertion order.",
    ),
    OwnershipRequirement(
        "OWN-REQ-006",
        "A declaration SHALL name the authority under which it binds.",
    ),
    OwnershipRequirement(
        "OWN-REQ-007",
        "A declaration SHALL cite the evidence identities on which it rests.",
    ),
)


@dataclass(frozen=True, slots=True)
class OwnershipDeclarationContract:
    """The constitutional requirements for canonical ownership (project independent)."""

    requirements: tuple[OwnershipRequirement, ...] = OWNERSHIP_REQUIREMENTS
    version: str = OWNERSHIP_CONTRACT_VERSION
    contract_id: str = ""

    @classmethod
    def create(
        cls,
        requirements: Iterable[OwnershipRequirement] = OWNERSHIP_REQUIREMENTS,
        *,
        version: str = OWNERSHIP_CONTRACT_VERSION,
    ) -> OwnershipDeclarationContract:
        """Build a validated contract with a content-addressed identity."""
        ordered = tuple(requirements)
        if not ordered:
            raise OwnershipContractError("ownership contract declares no requirements")
        seen: set[str] = set()
        for requirement in ordered:
            if not isinstance(requirement, OwnershipRequirement):
                raise OwnershipContractError("contract accepts only OwnershipRequirement values")
            if requirement.requirement_id in seen:
                raise OwnershipContractError(
                    "duplicate requirement id", requirement_id=requirement.requirement_id
                )
            seen.add(requirement.requirement_id)
        core = {
            "version": version,
            "requirements": [item.to_dict() for item in ordered],
        }
        return cls(
            requirements=ordered,
            version=version,
            contract_id=f"UCOS-UOFC-{content_hash(core)[:16]}",
        )

    @property
    def requirement_ids(self) -> tuple[str, ...]:
        """The declared requirement identities in constitutional order."""
        return tuple(item.requirement_id for item in self.requirements)

    def mandatory_ids(self) -> tuple[str, ...]:
        """The identities of every mandatory requirement."""
        return tuple(item.requirement_id for item in self.requirements if item.mandatory)

    def requirement(self, requirement_id: str) -> OwnershipRequirement:
        """The declared requirement ``requirement_id`` (fail-closed)."""
        for item in self.requirements:
            if item.requirement_id == requirement_id:
                return item
        raise OwnershipContractError("unknown requirement", requirement_id=requirement_id)

    def to_dict(self) -> dict[str, Any]:
        """A JSON-serialisable projection of this contract."""
        return {
            "contract_id": self.contract_id,
            "version": self.version,
            "requirements": [item.to_dict() for item in self.requirements],
        }

    def fingerprint(self) -> str:
        """The deterministic content fingerprint of this contract."""
        return content_hash(self.to_dict())


def default_ownership_contract() -> OwnershipDeclarationContract:
    """The Ownership Declaration Contract as constitutionally declared."""
    return OwnershipDeclarationContract.create()


@dataclass(frozen=True, slots=True)
class OwnershipDeclaration:
    """The immutable, content-addressed statement that a subject is canonically owned."""

    subject_id: str
    owner: str
    authority: str
    kind: EvidenceKind
    locator: str = ""
    rule: str = RULE_SOLE_DECLARATION
    evidence_ids: tuple[str, ...] = ()
    satisfied: tuple[str, ...] = ()
    declaration_id: str = ""

    @classmethod
    def create(
        cls,
        subject_id: str,
        owner: str,
        *,
        authority: str,
        kind: EvidenceKind | str,
        locator: str = "",
        rule: str = RULE_SOLE_DECLARATION,
        evidence_ids: Iterable[str] = (),
        satisfied: Iterable[str] = (),
    ) -> OwnershipDeclaration:
        """Build a validated declaration; refuses an owner without cited evidence."""
        cited = tuple(sorted({str(item) for item in evidence_ids if str(item).strip()}))
        if not cited:
            raise OwnershipContractError(
                "declaration must cite evidence (OWN-REQ-007)", subject=subject_id
            )
        if not isinstance(authority, str) or not authority.strip():
            raise OwnershipContractError(
                "declaration must name its authority (OWN-REQ-006)", subject=subject_id
            )
        resolved = EvidenceKind.coerce(kind, subject=subject_id)
        if not resolved.constitutive:
            raise OwnershipContractError(
                "declaration must rest on constitutive evidence (OWN-REQ-001)",
                subject=subject_id,
                kind=resolved.value,
            )
        core = {
            "subject_id": subject_id.strip(),
            "owner": owner.strip(),
            "authority": authority.strip(),
            "kind": resolved.value,
            "locator": locator.strip(),
            "rule": rule,
            "evidence_ids": list(cited),
        }
        return cls(
            subject_id=subject_id.strip(),
            owner=owner.strip(),
            authority=authority.strip(),
            kind=resolved,
            locator=locator.strip(),
            rule=rule,
            evidence_ids=cited,
            satisfied=tuple(sorted({str(item) for item in satisfied})),
            declaration_id=f"UCOS-UOFD-{content_hash(core)[:16]}",
        )

    def to_dict(self) -> dict[str, Any]:
        """A JSON-serialisable projection of this declaration."""
        return {
            "declaration_id": self.declaration_id,
            "subject_id": self.subject_id,
            "owner": self.owner,
            "authority": self.authority,
            "kind": self.kind.value,
            "locator": self.locator,
            "rule": self.rule,
            "evidence_ids": list(self.evidence_ids),
            "satisfied": list(self.satisfied),
        }

    def fingerprint(self) -> str:
        """The deterministic content fingerprint of this declaration."""
        return content_hash(self.to_dict())


@dataclass(frozen=True, slots=True)
class OwnershipRecord:
    """The determination outcome for exactly one subject."""

    subject_id: str
    standing: OwnershipStanding
    declaration: OwnershipDeclaration | None = None
    reasons: tuple[str, ...] = ()
    unmet: tuple[str, ...] = ()
    claims: tuple[tuple[str, int], ...] = ()
    evidence_ids: tuple[str, ...] = ()
    refusals: tuple[tuple[str, str, str], ...] = ()
    record_id: str = ""

    @classmethod
    def create(
        cls,
        subject_id: str,
        standing: OwnershipStanding,
        *,
        declaration: OwnershipDeclaration | None = None,
        reasons: Iterable[str] = (),
        unmet: Iterable[str] = (),
        claims: Mapping[str, int] | None = None,
        evidence_ids: Iterable[str] = (),
        refusals: Iterable[tuple[str, str, str]] = (),
    ) -> OwnershipRecord:
        """Build a validated record; DECLARED standing requires a declaration.

        ``refusals`` are ``(locator, reason, provider_id)`` triples naming candidate homes the
        declarations refused. They are *diagnosis*, never evidence and never a claim, so they
        take no part in the record's identity — a record is identified by the determination it
        reached, exactly as before (UFC-08 additive compatibility).
        """
        if not isinstance(standing, OwnershipStanding):
            raise OwnershipContractError("standing must be an OwnershipStanding")
        if standing is OwnershipStanding.DECLARED and declaration is None:
            raise OwnershipContractError(
                "DECLARED standing requires a declaration", subject=subject_id
            )
        if standing is not OwnershipStanding.DECLARED and declaration is not None:
            raise OwnershipContractError(
                "only DECLARED standing may carry a declaration", subject=subject_id
            )
        named = tuple(sorted({str(item) for item in reasons if str(item).strip()}))
        if standing is not OwnershipStanding.DECLARED and not named:
            raise OwnershipContractError(
                "an absence of ownership must name its reason", subject=subject_id
            )
        refused: set[tuple[str, str, str]] = set()
        for item in refusals:
            triple = tuple(str(part) for part in item)
            if len(triple) != 3 or not all(part.strip() for part in triple):
                raise OwnershipContractError(
                    "a refusal must name its locator, reason and provider", subject=subject_id
                )
            refused.add(triple)  # type: ignore[arg-type]
        core = {
            "subject_id": subject_id.strip(),
            "standing": standing.value,
            "declaration": declaration.declaration_id if declaration else "",
            "reasons": list(named),
        }
        return cls(
            subject_id=subject_id.strip(),
            standing=standing,
            declaration=declaration,
            reasons=named,
            unmet=tuple(sorted({str(item) for item in unmet})),
            claims=tuple(sorted((str(k), int(v)) for k, v in dict(claims or {}).items())),
            evidence_ids=tuple(sorted({str(item) for item in evidence_ids})),
            refusals=tuple(sorted(refused)),
            record_id=f"UCOS-UOFR-{content_hash(core)[:16]}",
        )

    @property
    def owner(self) -> str:
        """The declared owner, or :data:`UNASSIGNED_OWNER` when none is declared."""
        return self.declaration.owner if self.declaration else UNASSIGNED_OWNER

    @property
    def declared(self) -> bool:
        """Whether this subject has one declared canonical owner."""
        return self.standing is OwnershipStanding.DECLARED

    @property
    def refusal_reasons(self) -> tuple[str, ...]:
        """The distinct declared eligibility deficits that refused this subject's candidates."""
        return tuple(sorted({reason for _, reason, _ in self.refusals}))

    @property
    def refused_locators(self) -> tuple[str, ...]:
        """Every candidate home the declarations refused for this subject."""
        return tuple(sorted({locator for locator, _, _ in self.refusals}))

    @property
    def remediable(self) -> bool:
        """Whether this open subject's absence has a named, located deficit to remedy.

        A subject nobody ever wrote an artifact for and a subject whose only artifact failed a
        declared eligibility rule are both UNRESOLVED, but only the second one names something
        a project can act on without a governing authority deciding from first principles.
        """
        return bool(self.refusals) and not self.declared

    def to_dict(self) -> dict[str, Any]:
        """A JSON-serialisable projection of this record."""
        return {
            "record_id": self.record_id,
            "subject_id": self.subject_id,
            "standing": self.standing.value,
            "owner": self.owner,
            "declaration": self.declaration.to_dict() if self.declaration else None,
            "reasons": list(self.reasons),
            "unmet": list(self.unmet),
            "claims": {owner: count for owner, count in self.claims},
            "evidence_ids": list(self.evidence_ids),
            "refusals": [
                {"locator": locator, "reason": reason, "provider_id": provider}
                for locator, reason, provider in self.refusals
            ],
        }

    def fingerprint(self) -> str:
        """The deterministic content fingerprint of this record."""
        return content_hash(self.to_dict())


def _percent(part: int, whole: int) -> float:
    """A deterministic percentage; ``0.0`` when the population is empty."""
    if whole <= 0:
        return 0.0
    return round((part / whole) * 100, 4)


@dataclass(frozen=True, slots=True)
class OwnershipDetermination:
    """The immutable determination of canonical ownership over a subject population."""

    records: tuple[OwnershipRecord, ...]
    contract_id: str = ""
    determination_id: str = ""

    @classmethod
    def create(
        cls, records: Iterable[OwnershipRecord], *, contract_id: str = ""
    ) -> OwnershipDetermination:
        """Build a deterministic determination, ordered by subject identity."""
        ordered = tuple(sorted(records, key=lambda item: item.subject_id))
        seen: set[str] = set()
        for record in ordered:
            if record.subject_id in seen:
                raise OwnershipContractError(
                    "duplicate ownership record", subject=record.subject_id
                )
            seen.add(record.subject_id)
        core = {
            "records": [record.record_id for record in ordered],
            "contract_id": contract_id,
        }
        return cls(
            records=ordered,
            contract_id=contract_id,
            determination_id=f"UCOS-UOFT-{content_hash(core)[:16]}",
        )

    @property
    def total(self) -> int:
        """The size of the determined subject population."""
        return len(self.records)

    def of_standing(self, standing: OwnershipStanding) -> tuple[OwnershipRecord, ...]:
        """Every record with ``standing``, ordered by subject identity."""
        return tuple(record for record in self.records if record.standing is standing)

    @property
    def declared(self) -> tuple[OwnershipRecord, ...]:
        """Every subject with one declared canonical owner."""
        return self.of_standing(OwnershipStanding.DECLARED)

    @property
    def contested(self) -> tuple[OwnershipRecord, ...]:
        """Every subject with more than one surviving, unsettled claim."""
        return self.of_standing(OwnershipStanding.CONTESTED)

    @property
    def unresolved(self) -> tuple[OwnershipRecord, ...]:
        """Every subject whose ownership could not be honestly declared."""
        return self.of_standing(OwnershipStanding.UNRESOLVED)

    @property
    def closed(self) -> bool:
        """Whether every subject in the population has one declared canonical owner."""
        return self.total > 0 and not self.contested and not self.unresolved

    @property
    def coverage(self) -> float:
        """The percentage of the population with declared canonical ownership."""
        return _percent(len(self.declared), self.total)

    def counts(self) -> dict[str, int]:
        """The population counts by standing."""
        return {
            "total": self.total,
            "declared": len(self.declared),
            "contested": len(self.contested),
            "unresolved": len(self.unresolved),
            "remediable": len(self.remediable),
        }

    def by_reason(self) -> dict[str, int]:
        """How many subjects carry each named reason (a closed vocabulary)."""
        tally: dict[str, int] = {}
        for record in self.records:
            for reason in record.reasons:
                tally[reason] = tally.get(reason, 0) + 1
        return dict(sorted(tally.items()))

    def by_refusal(self) -> dict[str, int]:
        """How many subjects each declared eligibility deficit refused.

        This is the diagnosis behind :meth:`by_reason`: where ``by_reason`` says *that* a
        subject had no admissible evidence, this says *which declared rule* refused the
        candidate, in the eligibility vocabulary the project's own declarations publish.
        """
        tally: dict[str, int] = {}
        for record in self.records:
            for reason in record.refusal_reasons:
                tally[reason] = tally.get(reason, 0) + 1
        return dict(sorted(tally.items()))

    @property
    def remediable(self) -> tuple[OwnershipRecord, ...]:
        """Every open subject whose absence names a located, remediable deficit."""
        return tuple(record for record in self.records if record.remediable)

    def refusal_index(self) -> dict[str, dict[str, str]]:
        """A subject → ``{refused locator: deficit}`` index over the diagnosed residue."""
        return {
            record.subject_id: {locator: reason for locator, reason, _ in record.refusals}
            for record in self.records
            if record.refusals
        }

    def by_owner(self) -> dict[str, int]:
        """How many subjects each declared owner owns."""
        tally: dict[str, int] = {}
        for record in self.declared:
            tally[record.owner] = tally.get(record.owner, 0) + 1
        return dict(sorted(tally.items()))

    def index(self) -> dict[str, str]:
        """A subject → declared owner index (declared subjects only)."""
        return {record.subject_id: record.owner for record in self.declared}

    def record(self, subject_id: str) -> OwnershipRecord:
        """The record for ``subject_id`` (fail-closed)."""
        for item in self.records:
            if item.subject_id == subject_id:
                return item
        raise OwnershipContractError("unknown ownership subject", subject=subject_id)

    def to_dict(self) -> dict[str, Any]:
        """A JSON-serialisable projection of this determination."""
        return {
            "determination_id": self.determination_id,
            "contract_id": self.contract_id,
            "counts": self.counts(),
            "coverage_percentage": self.coverage,
            "closed": self.closed,
            "by_reason": self.by_reason(),
            "by_refusal": self.by_refusal(),
            "by_owner": self.by_owner(),
            "records": [record.to_dict() for record in self.records],
        }

    def fingerprint(self) -> str:
        """The deterministic content fingerprint of this determination."""
        return content_hash(self.to_dict())


_OWNERSHIP_CONTRACT_NAMES: tuple[tuple[str, str], ...] = (
    ("ownership.contract.requirements", "Publish the Ownership Declaration Contract."),
    ("ownership.evidence.collect", "Collect ownership evidence from pluggable providers."),
    ("ownership.determination.determine", "Determine canonical ownership from evidence only."),
    ("ownership.determination.index", "Project a subject → declared owner index."),
)

#: The versioned published contract surface of the Universal Ownership Framework.
OWNERSHIP_CONTRACTS: tuple[ContractRef, ...] = tuple(
    ContractRef(name, OWNERSHIP_CONTRACT_VERSION) for name, _ in _OWNERSHIP_CONTRACT_NAMES
)


def ownership_contract_names() -> tuple[str, ...]:
    """The published ownership contract names, in declaration order."""
    return tuple(name for name, _ in _OWNERSHIP_CONTRACT_NAMES)


__all__ = [
    "UOF_ID",
    "OWNERSHIP_CONTRACT_VERSION",
    "UNASSIGNED_OWNER",
    "EvidenceKind",
    "CONSTITUTIVE_EVIDENCE_KINDS",
    "CORROBORATIVE_EVIDENCE_KINDS",
    "OwnershipStanding",
    "OwnershipGranularity",
    "REASON_NO_EVIDENCE",
    "REASON_NO_CONSTITUTIVE_DECLARATION",
    "REASON_INELIGIBLE_ZONE",
    "REASON_CONTEST_UNSETTLED",
    "REASON_SUBJECT_NOT_REGISTERED",
    "UNRESOLVED_REASONS",
    "RULE_SOLE_DECLARATION",
    "RULE_CONTEST_SETTLED",
    "OwnershipEvidence",
    "OwnershipRequirement",
    "OWNERSHIP_REQUIREMENTS",
    "OwnershipDeclarationContract",
    "default_ownership_contract",
    "OwnershipDeclaration",
    "OwnershipRecord",
    "OwnershipDetermination",
    "OWNERSHIP_CONTRACTS",
    "ownership_contract_names",
]
