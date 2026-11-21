"""CMG-000002 §2 — the temporal coordinate, as a type.

A coordinate is a value *plus the system it means something in*. Separating those two
is the whole content of the contract: "2026-08-17T00:00:00Z", Lamport counter 41 and
Mars sol 1247 are all legitimate primaries, and none of them means anything without
its reference system. Code that stores the value alone has silently mandated a
representation, which CMG-000002 §3.1 forbids.

Every type here is frozen and slotted, and no field defaults to an Earth convention.
``system_identifier`` is required precisely so that a caller cannot omit it and let a
default stand in for a decision.
"""

from __future__ import annotations

import enum
from dataclasses import dataclass, field, replace
from typing import Any


class TemporalError(Exception):
    """A temporal obligation was refused."""

    def __init__(self, message: str, *, subject: str | None = None) -> None:
        super().__init__(message if subject is None else f"{message}: {subject}")
        self.subject = subject


class SystemType(str, enum.Enum):
    """The five reference-system families of CMG-000002 §1.1.

    ``UNKNOWN`` is not a failure value. The contract declares "Future Unknown Time"
    as an explicit open slot, so a reference system nobody has invented yet is
    representable today rather than being a future schema change.
    """

    PHYSICAL = "physical"
    LOGICAL = "logical"
    CONTEXTUAL = "contextual"
    SIMULATED = "simulated"
    UNKNOWN = "unknown"


class Ordering(str, enum.Enum):
    """The result of comparing two coordinates.

    ``INCOMPARABLE`` exists because of CMG-000002 Law 7: coordinates in different
    reference systems have no order unless a conversion is declared. Collapsing that
    case into an arbitrary answer is the specific bug this member prevents.
    """

    BEFORE = "before"
    SIMULTANEOUS = "simultaneous"
    AFTER = "after"
    INCOMPARABLE = "incomparable"


class CreationMethod(str, enum.Enum):
    """How a coordinate's value came to be known (CMG-000002 §2.1 provenance)."""

    CLOCK = "clock"
    ORACLE = "oracle"
    CONSENSUS = "consensus"
    COMPUTATION = "computation"


@dataclass(frozen=True, slots=True)
class ReferenceSystem:
    """The frame a coordinate's value is expressed in.

    Two systems are the same system only when identifier *and* version match: a
    calendar reform, an epoch change or a re-based logical clock produces values that
    are not comparable with the old ones, and the version is what makes that
    detectable instead of silent.
    """

    system_type: SystemType
    system_identifier: str
    system_version: str = "1"
    total_order: bool = True
    causality_tracking: bool = False

    def __post_init__(self) -> None:
        if not self.system_identifier:
            raise TemporalError("reference system has no identifier")

    @property
    def key(self) -> str:
        """The identity of this system, including version."""
        return f"{self.system_type.value}:{self.system_identifier}@{self.system_version}"

    def same_system(self, other: ReferenceSystem) -> bool:
        """Whether ``other`` is the same frame, version included."""
        return self.key == other.key

    def to_dict(self) -> dict[str, Any]:
        return {
            "system_type": self.system_type.value,
            "system_identifier": self.system_identifier,
            "system_version": self.system_version,
            "ordering_model": {
                "total_order": self.total_order,
                "partial_order": not self.total_order,
                "causality_tracking": self.causality_tracking,
            },
        }


@dataclass(frozen=True, slots=True)
class Precision:
    """The granularity and uncertainty of a value, in that value's own units.

    Units are deliberately a free string. Requiring "seconds" would mandate a physical
    representation and make a Lamport counter (unit: "tick") or a block height (unit:
    "block") unrepresentable.
    """

    resolution: str
    uncertainty: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {"resolution": self.resolution, "uncertainty": self.uncertainty}


@dataclass(frozen=True, slots=True)
class Provenance:
    """Who asserted a coordinate, by what method, with what evidence.

    CMG-000002 Law 8 binds evidence immutably to the coordinate, which is why this is
    part of the frozen value rather than metadata alongside it.
    """

    creation_authority: str
    creation_method: CreationMethod
    evidence_id: str | None = None
    confidence: str = "asserted"

    def __post_init__(self) -> None:
        if not self.creation_authority:
            raise TemporalError("provenance names no creation authority")

    def to_dict(self) -> dict[str, Any]:
        return {
            "creation_authority": self.creation_authority,
            "creation_method": self.creation_method.value,
            "evidence_id": self.evidence_id,
            "confidence": self.confidence,
        }


@dataclass(frozen=True, slots=True)
class Conversion:
    """One step of a coordinate's conversion history (CMG-000002 Law 3)."""

    source_system: str
    target_system: str
    conversion_function: str
    conversion_authority: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_system": self.source_system,
            "target_system": self.target_system,
            "conversion_function": self.conversion_function,
            "conversion_authority": self.conversion_authority,
        }


@dataclass(frozen=True, slots=True)
class TemporalCoordinate:
    """A point in temporal existence, expressed in a named reference system.

    ``primary`` is the value in that system's native form and is never normalised:
    normalising would pick a canonical representation, and CMG-000002 §3.3 states
    that "no representation is more correct than another".

    ``conversion_history`` grows when a coordinate is converted, so a coordinate that
    has crossed systems carries the route it took and the authority for each step.
    """

    primary: str
    reference_system: ReferenceSystem
    precision: Precision
    provenance: Provenance
    conversion_history: tuple[Conversion, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if self.primary == "":
            raise TemporalError("temporal coordinate has no primary value")

    @property
    def system_key(self) -> str:
        """The reference-system identity this coordinate is expressed in."""
        return self.reference_system.key

    @property
    def qualified(self) -> str:
        """The coordinate as one self-describing string: ``<system_key>#<primary>``.

        Exists so a coordinate can be carried in a single field without degrading into
        a bare value. A bare "2026-08-17" has silently mandated a calendar; this form
        cannot, because the system that gives it meaning travels with it. Round-trips
        through :func:`parse_qualified`.
        """
        return f"{self.reference_system.key}#{self.primary}"

    def with_conversion(
        self, *, target: ReferenceSystem, primary: str, function: str, authority: str
    ) -> TemporalCoordinate:
        """Return the same instant expressed in ``target``, remembering the route."""
        step = Conversion(
            source_system=self.reference_system.key,
            target_system=target.key,
            conversion_function=function,
            conversion_authority=authority,
        )
        return replace(
            self,
            primary=primary,
            reference_system=target,
            conversion_history=(*self.conversion_history, step),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "reference_system": self.reference_system.to_dict(),
            "value": {"primary": self.primary, **self.precision.to_dict()},
            "provenance": self.provenance.to_dict(),
            "conversion_history": [c.to_dict() for c in self.conversion_history],
        }

    @classmethod
    def logical(
        cls, counter: int | str, *, system_identifier: str, authority: str
    ) -> TemporalCoordinate:
        """Build a logical-time coordinate (Lamport-style counter, no clock).

        The convenience constructor the repository itself needs: commit order and
        ledger sequence are logical time, and the seeded temporal context already
        declares ``reference_frame: "repository history (commit order), not
        wall-clock"``.
        """
        return cls(
            primary=str(counter),
            reference_system=ReferenceSystem(
                system_type=SystemType.LOGICAL,
                system_identifier=system_identifier,
                causality_tracking=True,
            ),
            precision=Precision(resolution="tick"),
            provenance=Provenance(
                creation_authority=authority, creation_method=CreationMethod.COMPUTATION
            ),
        )


@dataclass(frozen=True, slots=True)
class ValidityPeriod:
    """The interval over which an assertion holds, in one reference system.

    ``until=None`` means open-ended, which is the normal case for a living object and
    is not the same as unknown. Both bounds must share a reference system, because an
    interval whose ends are in different frames has no length (Law 7).
    """

    since: TemporalCoordinate
    until: TemporalCoordinate | None = None

    def __post_init__(self) -> None:
        if self.until is not None and not self.since.reference_system.same_system(
            self.until.reference_system
        ):
            raise TemporalError(
                "validity bounds are in different reference systems",
                subject=f"{self.since.system_key} vs {self.until.system_key}",
            )

    @property
    def open_ended(self) -> bool:
        """Whether the period has no declared end."""
        return self.until is None

    def to_dict(self) -> dict[str, Any]:
        return {
            "since": self.since.to_dict(),
            "until": None if self.until is None else self.until.to_dict(),
            "open_ended": self.open_ended,
        }


def parse_qualified(qualified: str, *, authority: str) -> TemporalCoordinate:
    """Rehydrate a coordinate from its ``<system_key>#<primary>`` form.

    The inverse of :attr:`TemporalCoordinate.qualified`. ``authority`` is supplied by
    the caller because provenance is not recoverable from the string — the qualified
    form carries the frame and the value, which is what makes the value meaningful,
    but not who asserted it.

    Raises:
        TemporalError: the string is not a qualified coordinate. Refusing is the point:
            a bare value with no reference system is exactly what CMG-000002 §3.1
            forbids, so it must not be silently accepted with a default frame.
    """
    if "#" not in qualified:
        raise TemporalError(
            "not a qualified temporal coordinate; a bare value mandates a representation",
            subject=qualified,
        )
    system_part, _, primary = qualified.partition("#")
    if not primary:
        raise TemporalError("qualified coordinate has no primary value", subject=qualified)
    try:
        type_token, _, remainder = system_part.partition(":")
        identifier, _, version = remainder.rpartition("@")
    except ValueError as exc:  # pragma: no cover - partition does not raise
        raise TemporalError("malformed reference system key", subject=qualified) from exc
    if not identifier or not version:
        raise TemporalError("malformed reference system key", subject=qualified)
    try:
        system_type = SystemType(type_token)
    except ValueError as exc:
        raise TemporalError("unknown reference system type", subject=type_token) from exc
    return TemporalCoordinate(
        primary=primary,
        reference_system=ReferenceSystem(
            system_type=system_type, system_identifier=identifier, system_version=version
        ),
        precision=Precision(resolution="declared"),
        provenance=Provenance(
            creation_authority=authority, creation_method=CreationMethod.COMPUTATION
        ),
    )
