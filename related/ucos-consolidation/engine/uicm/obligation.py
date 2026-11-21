"""UCOS-UICM-000001 — the capability-keyed closure obligation register.

This module is the home of the second capability UICM was admitted to create. Located
obligation registers key on something other than a capability: ``UAKOS-CLOSURE-009``
records ``gap_classes[]`` keyed by gap class (``RG-A01``) and ``baseline_conditions[]``
keyed by condition (``BC-01``); ``UCL-000001`` binds obligations to lifecycle *stages*.
None of them can answer "what does capability X still owe?", because none of them is
keyed by capability identity.

Two properties make this a register rather than a list.

**Obligation identity is derived, never counted.** The identifier is a total, injective
function of the capability identity and the dimension ordinal, both of which are already
owned elsewhere. A counter would make the identifier depend on insertion order, so the
same repository measured twice would produce different obligation ids and the register
could never be replayed. Because identity is derived, this module mints nothing — it
composes two identifiers that the canonical owners already assigned.

**The register is append-only and hash-chained.** Each entry links the digest of its
predecessor, so an entry cannot be edited or reordered without breaking every link after
it. The chain construction deliberately mirrors the five existing ledgers in the
repository (``engine.registry.universal.audit``, ``engine.certification.ledger``,
``engine.universal_certification.audit`` and ``.approval``, ``engine.context.registry``)
rather than importing one of them: those ledgers each carry a domain payload of their
own, and this register's obligation payload is not any of theirs. What is *not*
duplicated is the digest primitive itself, which comes from
:mod:`engine.uckp.canonical` exactly as every other chain in the repository does.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from engine.uicm.model import (
    Capability,
    ClosureDeclaration,
    ClosureError,
    DimensionDeclaration,
    digest,
)

#: The register document format.
OBLIGATION_REGISTER_FORMAT = "ucos-uicm-obligation-register/1.0.0"

#: The genesis link of the obligation chain — the same convention the five located
#: ledgers use, so a reader who knows one knows this one.
GENESIS_HASH = "0" * 64

#: The obligation identifier prefix.
OBLIGATION_PREFIX = "UICM-OBL"


class ObligationError(ClosureError):
    """Raised when an obligation is malformed, duplicated, or the chain is broken."""


def obligation_id(capability: Capability, dimension: DimensionDeclaration) -> str:
    """Derive the obligation identifier from identity already owned elsewhere.

    Injective by construction: the capability short identity is a digest fragment minted
    by the capability register, and the dimension ordinal is unique within the
    declaration (``require_unique_dimensions``). No counter, no insertion order, no clock.
    """
    return f"{OBLIGATION_PREFIX}-{capability.short_id}-{dimension.ordinal:02d}"


@dataclass(frozen=True, slots=True)
class ClosureObligation:
    """What one capability owes on one closure dimension.

    ``discharging_owner`` is the located owner that could satisfy the obligation. It is
    recorded because an obligation without a named discharger is a complaint rather than
    an obligation, and because naming the owner is what keeps UICM from discharging it
    itself.
    """

    obligation_id: str
    capability_id: str
    capability_name: str
    canonical_owner: str
    knowledge_reference: str
    dimension_id: str
    dimension_ordinal: int
    dimension_name: str
    question: str
    requirement: str
    discharging_owner: str
    ucic_stages: tuple[int, ...]
    blocking: bool

    @classmethod
    def of(
        cls,
        capability: Capability,
        dimension: DimensionDeclaration,
        *,
        discharging_owner: str,
    ) -> ClosureObligation:
        """Register what ``capability`` owes on ``dimension``."""
        return cls(
            obligation_id=obligation_id(capability, dimension),
            capability_id=capability.capability_id,
            capability_name=capability.name,
            canonical_owner=capability.canonical_owner,
            knowledge_reference=capability.knowledge_reference,
            dimension_id=dimension.id,
            dimension_ordinal=dimension.ordinal,
            dimension_name=dimension.name,
            question=dimension.question,
            requirement=dimension.requirement,
            discharging_owner=discharging_owner,
            ucic_stages=dimension.ucic_stages,
            blocking=dimension.blocking,
        )

    @property
    def key(self) -> str:
        """The matrix coordinate this obligation governs."""
        return f"{self.capability_name}:{self.dimension_id}"

    def to_dict(self) -> dict[str, Any]:
        return {
            "obligation_id": self.obligation_id,
            "capability_id": self.capability_id,
            "capability_name": self.capability_name,
            "canonical_owner": self.canonical_owner,
            "knowledge_reference": self.knowledge_reference,
            "dimension_id": self.dimension_id,
            "dimension_ordinal": self.dimension_ordinal,
            "dimension_name": self.dimension_name,
            "question": self.question,
            "requirement": self.requirement,
            "discharging_owner": self.discharging_owner,
            "ucic_stages": list(self.ucic_stages),
            "blocking": self.blocking,
        }

    def digest(self) -> str:
        return digest(self.to_dict())


@dataclass(frozen=True, slots=True)
class ObligationEntry:
    """One hash-chained register entry."""

    sequence: int
    obligation: ClosureObligation
    previous_hash: str
    entry_hash: str

    @classmethod
    def link(
        cls, *, sequence: int, obligation: ClosureObligation, previous_hash: str
    ) -> ObligationEntry:
        body = {
            "sequence": sequence,
            "obligation": obligation.to_dict(),
            "previous_hash": previous_hash,
        }
        return cls(
            sequence=sequence,
            obligation=obligation,
            previous_hash=previous_hash,
            entry_hash=digest(body),
        )

    def expected_hash(self) -> str:
        """Recompute this entry's link from its own content."""
        return digest(
            {
                "sequence": self.sequence,
                "obligation": self.obligation.to_dict(),
                "previous_hash": self.previous_hash,
            }
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "sequence": self.sequence,
            "obligation": self.obligation.to_dict(),
            "previous_hash": self.previous_hash,
            "entry_hash": self.entry_hash,
        }


class ObligationRegister:
    """An append-only, hash-chained register of closure obligations keyed by capability."""

    __slots__ = ("_entries", "_index")

    def __init__(self) -> None:
        self._entries: list[ObligationEntry] = []
        self._index: dict[str, ObligationEntry] = {}

    def register(self, obligation: ClosureObligation) -> ObligationEntry:
        """Append one obligation. Registering the same coordinate twice is refused."""
        if obligation.obligation_id in self._index:
            raise ObligationError(
                "obligation already registered",
                obligation_id=obligation.obligation_id,
            )
        entry = ObligationEntry.link(
            sequence=len(self._entries) + 1,
            obligation=obligation,
            previous_hash=self.head_hash,
        )
        self._entries.append(entry)
        self._index[obligation.obligation_id] = entry
        return entry

    def register_all(self, obligations: Iterable[ClosureObligation]) -> int:
        """Append many obligations in the order given; returns the number appended."""
        appended = 0
        for obligation in obligations:
            self.register(obligation)
            appended += 1
        return appended

    @property
    def head_hash(self) -> str:
        """The digest of the most recent entry, or the genesis link when empty."""
        return self._entries[-1].entry_hash if self._entries else GENESIS_HASH

    @property
    def entries(self) -> tuple[ObligationEntry, ...]:
        return tuple(self._entries)

    def __len__(self) -> int:
        return len(self._entries)

    def __contains__(self, obligation_id: object) -> bool:
        return obligation_id in self._index

    def get(self, obligation_id: str) -> ClosureObligation:
        """Return one registered obligation, or fail closed."""
        entry = self._index.get(obligation_id)
        if entry is None:
            raise ObligationError("no such obligation", obligation_id=obligation_id)
        return entry.obligation

    def obligations(self) -> tuple[ClosureObligation, ...]:
        return tuple(entry.obligation for entry in self._entries)

    def keys(self) -> frozenset[str]:
        """Every matrix coordinate the register governs."""
        return frozenset(entry.obligation.key for entry in self._entries)

    def for_capability(self, capability_name: str) -> tuple[ClosureObligation, ...]:
        """Everything one capability owes — the query no located register could answer."""
        return tuple(
            entry.obligation
            for entry in self._entries
            if entry.obligation.capability_name == capability_name
        )

    def for_dimension(self, dimension_id: str) -> tuple[ClosureObligation, ...]:
        return tuple(
            entry.obligation
            for entry in self._entries
            if entry.obligation.dimension_id == dimension_id
        )

    def verify(self) -> bool:
        """True iff every link recomputes and every predecessor reference is correct."""
        previous = GENESIS_HASH
        for position, entry in enumerate(self._entries, start=1):
            if entry.sequence != position:
                return False
            if entry.previous_hash != previous:
                return False
            if entry.entry_hash != entry.expected_hash():
                return False
            previous = entry.entry_hash
        return True

    def require_intact(self) -> None:
        """Fail closed on a broken chain."""
        if not self.verify():
            raise ObligationError("obligation register chain is not intact")

    def to_document(self) -> dict[str, Any]:
        return {
            "format": OBLIGATION_REGISTER_FORMAT,
            "authority": "NONE - DERIVED TRUTH",
            "obligation_total": len(self._entries),
            "head_hash": self.head_hash,
            "chain_intact": self.verify(),
            "by_dimension": {
                dimension: len(self.for_dimension(dimension))
                for dimension in sorted({e.obligation.dimension_id for e in self._entries})
            },
            "entries": [entry.to_dict() for entry in self._entries],
        }

    def digest(self) -> str:
        return digest(self.to_document())


def build_register(
    declaration: ClosureDeclaration,
    capabilities: Sequence[Capability],
    *,
    discharging_owners: Mapping[str, str] | None = None,
) -> ObligationRegister:
    """Register one obligation per capability x dimension coordinate.

    The register is total over the matrix by construction: it iterates the discovered
    population against the declared dimensions, so a coordinate cannot exist in the
    matrix without an obligation governing it (UICM-INV-03).
    """
    owners = dict(discharging_owners or {})
    register = ObligationRegister()
    for capability in capabilities:
        for dimension in declaration.dimensions:
            register.register(
                ClosureObligation.of(
                    capability,
                    dimension,
                    discharging_owner=owners.get(dimension.id, dimension.owner_reference),
                )
            )
    register.require_intact()
    return register


__all__ = [
    "GENESIS_HASH",
    "OBLIGATION_PREFIX",
    "OBLIGATION_REGISTER_FORMAT",
    "ClosureObligation",
    "ObligationEntry",
    "ObligationError",
    "ObligationRegister",
    "build_register",
    "obligation_id",
]
