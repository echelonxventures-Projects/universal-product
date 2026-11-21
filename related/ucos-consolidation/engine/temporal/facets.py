"""The eight temporal facets of an object's existence.

Before this module the repository had exactly one of these as a first-class field —
creation time, on ``BirthRecord`` — and seven that existed only as prose. Lifecycle
*states* existed (``engine/knowledge/model.py`` has ten, including ``archived``), but
no state carried a coordinate, so "when was this archived" was unanswerable even
though "is this archived" was not.

A :class:`TemporalRecord` is the answer set: an object's identity plus the coordinates
of the events that have happened to it. It is append-only in the same sense the
lineage ledger is — :meth:`TemporalRecord.with_facet` returns a new record, and
recording a facet twice with different coordinates is refused, because an object has
one creation and one archival, not a most-recent opinion about them.

Ordering between facets is *checked, not assumed*: :meth:`TemporalRecord.violations`
uses the declared precedence below, and reports incomparable pairs rather than
silently accepting them. Two coordinates in different reference systems cannot be
ordered (Law 7), so an object whose creation is a Lamport counter and whose archival
is a Mars sol has an unverifiable history — and this says so.
"""

from __future__ import annotations

import enum
from dataclasses import dataclass, field
from typing import Any

from engine.temporal.coordinate import TemporalCoordinate, TemporalError, ValidityPeriod
from engine.temporal.operations import Ordering, TemporalRegistry, compare


class TemporalFacet(str, enum.Enum):
    """The eight time facets every identity may carry.

    ``RESTORATION`` is included even though the knowledge lifecycle currently has no
    edge out of ``ARCHIVED``. The facet exists so that the gap is visible as an
    unreachable state rather than an unrepresentable one; closing the transition is a
    lifecycle-owner change, recorded as gap G10.
    """

    CREATION = "creation"
    EXISTENCE = "existence"
    VALIDITY = "validity"
    EVOLUTION = "evolution"
    CERTIFICATION = "certification"
    RETIREMENT = "retirement"
    ARCHIVE = "archive"
    RESTORATION = "restoration"


#: Facet names in declaration order.
FACET_NAMES: tuple[str, ...] = tuple(f.value for f in TemporalFacet)

#: Declared precedence: a facet may not precede any facet listed as its predecessor.
#: Restoration deliberately follows archive, which is what makes a restored object
#: distinguishable from one that was never archived.
_PRECEDENCE: tuple[tuple[TemporalFacet, TemporalFacet], ...] = (
    (TemporalFacet.CREATION, TemporalFacet.EXISTENCE),
    (TemporalFacet.CREATION, TemporalFacet.EVOLUTION),
    (TemporalFacet.CREATION, TemporalFacet.CERTIFICATION),
    (TemporalFacet.CREATION, TemporalFacet.RETIREMENT),
    (TemporalFacet.EVOLUTION, TemporalFacet.RETIREMENT),
    (TemporalFacet.RETIREMENT, TemporalFacet.ARCHIVE),
    (TemporalFacet.ARCHIVE, TemporalFacet.RESTORATION),
)


@dataclass(frozen=True, slots=True)
class TemporalRecord:
    """An identity's temporal existence: which events happened, and when.

    ``subject_identity`` is a Universal Identity, not a path. That is deliberate: the
    temporal history of an object must survive the object moving, and a path-keyed
    temporal record would lose it on rename.
    """

    subject_identity: str
    facets: tuple[tuple[str, TemporalCoordinate], ...] = field(default_factory=tuple)
    validity: ValidityPeriod | None = None

    def __post_init__(self) -> None:
        if not self.subject_identity:
            raise TemporalError("temporal record names no subject identity")
        seen = [name for name, _ in self.facets]
        duplicated = sorted({n for n in seen if seen.count(n) > 1})
        if duplicated:
            raise TemporalError(
                f"facet recorded more than once: {', '.join(duplicated)}",
                subject=self.subject_identity,
            )

    def coordinate(self, facet: TemporalFacet) -> TemporalCoordinate | None:
        """The coordinate recorded for ``facet``, or None if it has not happened."""
        for name, coord in self.facets:
            if name == facet.value:
                return coord
        return None

    def has(self, facet: TemporalFacet) -> bool:
        """Whether ``facet`` has been recorded."""
        return self.coordinate(facet) is not None

    def recorded_facets(self) -> tuple[str, ...]:
        """Facet names present, in declaration order."""
        present = {name for name, _ in self.facets}
        return tuple(name for name in FACET_NAMES if name in present)

    def missing_facets(self) -> tuple[str, ...]:
        """Facet names absent, in declaration order.

        Absence is not a defect. An object that has not been archived has no archive
        time, and that is correct rather than incomplete.
        """
        present = {name for name, _ in self.facets}
        return tuple(name for name in FACET_NAMES if name not in present)

    def with_facet(self, facet: TemporalFacet, coordinate: TemporalCoordinate) -> TemporalRecord:
        """Return a new record with ``facet`` recorded.

        Idempotent for an identical re-record, which keeps replay safe.

        Raises:
            TemporalError: the facet is already recorded at a different coordinate.
                An object has one creation, not a latest opinion about it.
        """
        existing = self.coordinate(facet)
        if existing is not None:
            if existing == coordinate:
                return self
            raise TemporalError(
                f"facet {facet.value!r} already recorded at a different coordinate",
                subject=self.subject_identity,
            )
        merged = (*self.facets, (facet.value, coordinate))
        ordered = tuple(sorted(merged, key=lambda pair: FACET_NAMES.index(pair[0])))
        return TemporalRecord(
            subject_identity=self.subject_identity,
            facets=ordered,
            validity=self.validity,
        )

    def with_validity(self, period: ValidityPeriod) -> TemporalRecord:
        """Return a new record carrying ``period`` as its temporal validity."""
        return TemporalRecord(
            subject_identity=self.subject_identity,
            facets=self.facets,
            validity=period,
        )

    def violations(self, registry: TemporalRegistry | None = None) -> tuple[str, ...]:
        """Return the ways this record's facet ordering is unsound.

        Empty means sound. Two classes of problem are reported: a facet that precedes
        one it must follow, and a pair that cannot be ordered at all because their
        coordinates are in unconnected reference systems.
        """
        problems: list[str] = []
        for earlier, later in _PRECEDENCE:
            first, second = self.coordinate(earlier), self.coordinate(later)
            if first is None or second is None:
                continue
            verdict = compare(first, second, registry)
            if verdict is Ordering.AFTER:
                problems.append(
                    f"{later.value} precedes {earlier.value} "
                    f"({second.primary} < {first.primary} in {first.system_key})"
                )
            elif verdict is Ordering.INCOMPARABLE:
                problems.append(
                    f"{earlier.value} and {later.value} are incomparable: "
                    f"{first.system_key} vs {second.system_key} (no declared conversion)"
                )

        if self.has(TemporalFacet.RESTORATION) and not self.has(TemporalFacet.ARCHIVE):
            problems.append("restoration recorded without an archive")

        return tuple(problems)

    def to_dict(self) -> dict[str, Any]:
        """Canonical mapping form, facet-ordered for byte-stable output."""
        return {
            "subject_identity": self.subject_identity,
            "facets": {name: coord.to_dict() for name, coord in self.facets},
            "validity": None if self.validity is None else self.validity.to_dict(),
            "recorded": list(self.recorded_facets()),
            "missing": list(self.missing_facets()),
        }
