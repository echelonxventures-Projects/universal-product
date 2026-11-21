"""UCOS Ω∞ Phase 2 Temporal, Deliverables 3 and 4 — reference frames and time scales.

AUTHORITY = NONE (DERIVED TRUTH).

THE ASSUMPTION THIS REMOVES. A timestamp names an instant and says nothing about where the observer
was standing or what the units count. Both omissions are usually harmless on one planet with one
clock discipline, and both are fatal the moment they are not:

    "2026-08-29T04:43:33Z"

    where       Earth. Not stated, therefore not questionable.
    what units  SI seconds on a geoid. Not stated, therefore not questionable.
    ordering    total. Not stated, therefore not questionable.

A GOVERNANCE RECORD MUST NOT INHERIT AN UNSTATED FRAME. If it does, a record produced by a
spacecraft, a Mars surface system, a simulation running at 400× or a ledger measuring in block
heights has to be forced into a shape that misdescribes it, and the misdescription is invisible
because the true frame was never a field.

TWO ORTHOGONAL DECLARATIONS, and they are orthogonal on purpose.

    ReferenceFrame   WHERE the observation was made. Earth surface, Mars surface, a lunar station,
                     a spacecraft, a simulation, a distributed participant set, or nothing physical
                     at all.
    TimeScale        WHAT the integers count. SI seconds, Mars sols, block heights, Lamport
                     events, simulation steps, vector-clock components.

They are separate because the same frame supports several scales — an Earth system may record SI
seconds or event counters — and the same scale appears in several frames. Fusing them would produce
one enumeration of every (place, unit) pair, which is the combinatorial version of the list Rule Ω-1
exists to abolish.

NO FRAME IS PRIVILEGED, AND THAT INCLUDES EARTH. There is no ``DEFAULT_FRAME = EARTH`` in this
module and no conversion-to-UTC anywhere in the package. The frame this package uses for its own
records is ``LOGICAL``, which has no physical anchor — chosen because Phase 2's evidence must be
byte-identical on every machine, and any physically-anchored frame makes that impossible.

COMPARABILITY IS DECLARED, NEVER COMPUTED. ``FrameRelation`` states that two frames' positions may
be compared. It carries NO ARITHMETIC and no offset, and the absence is deliberate: relating Mars
local solar time to UTC requires ephemerides, a chosen landing site and a leap-second table, none of
which belong in a governance vocabulary. This module therefore answers "may these be compared?" and
never "what is the difference?". Two coordinates in unrelated frames compare ``INCOMPARABLE``, which
is a reportable governance finding rather than a silently wrong number.

EXTENSION IS A REGISTRATION. Deliverable Ω∞-T3 is discharged by
``evidence.frame_registration_probe``, which declares a frame this file never named — and a scale,
and a calendar, and a clock — and resolves a coordinate through all four with zero edits here.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from engine.omega_governance.temporal.ordering import (
    BRANCHING,
    CAUSAL,
    DISTRIBUTED,
    TOTAL,
    Ordering,
)


class ReferenceError(RuntimeError):
    """A frame, scale or relation was invalid, or an unknown name was resolved.

    RAISED, NEVER DEFAULTED. Resolving an unregistered frame name must fail loudly: if it returned a
    freshly invented frame, every coordinate carrying a misspelt frame would become comparable with
    nothing and INCOMPARABLE would stop meaning "no relation is declared" and start meaning "one of
    us cannot spell".
    """


# ------------------------------------------------------------------------------ reference frames


@dataclass(frozen=True, order=True)
class ReferenceFrame:
    """WHERE an observation was made. A first-class concept, as Deliverable 4 requires.

    ``anchor`` is free text naming the physical or logical body the frame is attached to, and it is
    NOT an enumeration — a frame anchored to a body nobody has named is the case this design exists
    to admit. ``physical`` distinguishes frames whose positions could in principle be related by
    measurement from those whose positions never can, which is the only structural difference the
    package needs and the only one it asserts.
    """

    name: str
    description: str = ""
    anchor: str = ""
    physical: bool = True

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ReferenceError("a reference frame with no name cannot appear in a coordinate")

    def __str__(self) -> str:
        return self.name


LOGICAL_FRAME = ReferenceFrame(
    "LOGICAL",
    "No physical anchor. Positions order events relative to one another and locate them nowhere. "
    "The frame this package uses for its own evidence, because it is the only one in which two "
    "runs on two machines can produce byte-identical records.",
    anchor="",
    physical=False,
)
EARTH_FRAME = ReferenceFrame(
    "EARTH",
    "An observer on or near the Earth geoid. ONE FRAME AMONG MANY here, deliberately: it holds no "
    "default status, no conversion privilege and no implicit role in comparison.",
    anchor="EARTH",
)
MARS_FRAME = ReferenceFrame(
    "MARS",
    "An observer on the Mars areoid. Its sol is not an Earth day and its year is not an Earth "
    "year, so positions in this frame are not Earth positions in different units.",
    anchor="MARS",
)
LUNAR_FRAME = ReferenceFrame(
    "LUNAR",
    "An observer on the lunar surface or in cislunar space.",
    anchor="MOON",
)
SPACECRAFT_FRAME = ReferenceFrame(
    "SPACECRAFT",
    "An observer aboard a vehicle in transit, whose proper time diverges from every surface frame "
    "and whose position is meaningful only relative to its own mission clock.",
    anchor="VEHICLE",
)
SIMULATION_FRAME = ReferenceFrame(
    "SIMULATION",
    "An observer inside a simulated world, whose time advances by step rather than by duration and "
    "may be paused, rewound or branched.",
    anchor="",
    physical=False,
)
DISTRIBUTED_FRAME = ReferenceFrame(
    "DISTRIBUTED",
    "A participant set with no shared observer. Positions are meaningful within the set and "
    "comparable only where the participants agree, which is what makes disagreement reportable.",
    anchor="",
    physical=False,
)

#: The frames this module ships. NOT AN EXHAUSTIVE LIST OF WHERE AN OBSERVER MAY BE — that list
#: cannot be written, which is the whole argument. Nothing in this package quantifies over this
#: tuple, so a frame absent from it works identically.
INITIAL_FRAMES: tuple[ReferenceFrame, ...] = (
    DISTRIBUTED_FRAME,
    EARTH_FRAME,
    LOGICAL_FRAME,
    LUNAR_FRAME,
    MARS_FRAME,
    SIMULATION_FRAME,
    SPACECRAFT_FRAME,
)


# ---------------------------------------------------------------------------------- time scales


@dataclass(frozen=True, order=True)
class TimeScale:
    """WHAT the integers of a position count, and how they should be ordered.

    ``unit`` is a word, not a conversion factor, and the absence of a factor is the point: this
    package never converts. A caller needing sols in seconds owns that arithmetic and the
    ephemeris it requires.

    ``vector`` says the position length is the participant count rather than fixed, so a vector
    clock and a scalar counter are the same type with different arity instead of two types.

    ``ordering`` is REQUIRED AND HAS NO DEFAULT. The first draft of this file defaulted it to
    ``TOTAL``, which quietly reinstated the single-ordering assumption the whole subpackage exists
    to remove: every scale declared without thinking about ordering would have claimed that all its
    positions are mutually comparable. Requiring it costs one argument at each of ten declaration
    sites and closes an assumption that was invisible.

    It is a SUGGESTED DISCIPLINE, not a constraint: a caller may pair any scale with any ordering,
    because the ordering describes the comparison discipline and the scale describes the units.
    Pretending one implies the other is how block heights on a forked chain came to be compared as
    integers.
    """

    name: str
    unit: str
    description: str
    ordering: Ordering
    vector: bool = False

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ReferenceError("a time scale with no name cannot appear in a coordinate")

    def __str__(self) -> str:
        return self.name


LOGICAL_TICK = TimeScale(
    "LOGICAL_TICK",
    "tick",
    "A monotonic counter with no duration. Orders events and measures nothing.",
    TOTAL,
)
LAMPORT_EVENT = TimeScale(
    "LAMPORT_EVENT",
    "event",
    "A Lamport counter, advanced on local events and raised on receipt. Totally ordered by "
    "construction, which is why it cannot distinguish concurrency from sequence.",
    TOTAL,
)
VECTOR_EVENT = TimeScale(
    "VECTOR_EVENT",
    "event",
    "One counter per participant. The scale on which CONCURRENT is a real answer, because "
    "componentwise domination can genuinely fail in both directions.",
    CAUSAL,
    vector=True,
)
SI_SECOND = TimeScale(
    "SI_SECOND",
    "s",
    "SI seconds counted from a declared epoch. ONE REGISTERED UNIT SYSTEM, and not the base of the "
    "architecture: Ω∞ Rule 1 forbids SI as a requirement and permits it as a registration, which "
    "is exactly what this value is.",
    TOTAL,
)
MARS_SOL = TimeScale(
    "MARS_SOL",
    "sol",
    "Mars solar days from a declared epoch. NOT an Earth day in other units, and no code here "
    "relates the two.",
    TOTAL,
)
LUNAR_DAY = TimeScale(
    "LUNAR_DAY",
    "lunar_day",
    "Lunar synodic days from a declared epoch.",
    TOTAL,
)
MISSION_ELAPSED = TimeScale(
    "MISSION_ELAPSED",
    "s",
    "Elapsed proper time aboard a vehicle since a mission event. Meaningful only in the vehicle's "
    "own frame.",
    TOTAL,
)
SIMULATION_STEP = TimeScale(
    "SIMULATION_STEP",
    "step",
    "Discrete simulation steps. May be replayed and branched, which is why a simulation clock is "
    "usually paired with a branching ordering.",
    BRANCHING,
)
BLOCK_HEIGHT = TimeScale(
    "BLOCK_HEIGHT",
    "block",
    "Positions in a ledger, as (chain, height). BRANCHING because a reorganisation makes two "
    "heights on divergent chains genuinely unordered.",
    BRANCHING,
)
OBSERVER_REPORT = TimeScale(
    "OBSERVER_REPORT",
    "report",
    "Positions shaped (observer, counter) in a participant set with no shared clock.",
    DISTRIBUTED,
)

#: The scales this module ships. NOT EXHAUSTIVE, and nothing quantifies over it.
INITIAL_SCALES: tuple[TimeScale, ...] = (
    BLOCK_HEIGHT,
    LAMPORT_EVENT,
    LOGICAL_TICK,
    LUNAR_DAY,
    MARS_SOL,
    MISSION_ELAPSED,
    OBSERVER_REPORT,
    SIMULATION_STEP,
    SI_SECOND,
    VECTOR_EVENT,
)


# ------------------------------------------------------------------------------------- relations


@dataclass(frozen=True, order=True)
class FrameRelation:
    """A DECLARATION that positions in two frames may be compared. Carries no arithmetic.

    WHAT THIS DELIBERATELY DOES NOT HOLD: an offset, a rate, a skew bound or a conversion. Relating
    a Mars areocentric position to a terrestrial one needs an ephemeris, a chosen site and a
    leap-second table; putting a number here would make a governance vocabulary the owner of an
    astronomical fact it cannot verify, and a wrong number is worse than a refusal because a refusal
    is visible.

    ``symmetric`` defaults true because comparability is normally mutual, and is settable because it
    is not always: a simulation may be comparable to the wall-clock frame that drove it while the
    reverse is meaningless.
    """

    source: str
    target: str
    rule: str
    description: str = ""
    symmetric: bool = True

    def __post_init__(self) -> None:
        for field_name, value in (("source", self.source), ("target", self.target)):
            if not value.strip():
                raise ReferenceError(f"a frame relation with no {field_name} relates nothing")
        if not self.rule.strip():
            raise ReferenceError(
                "a frame relation with no rule id cannot be cited by the comparison it permits"
            )

    def as_record(self) -> dict[str, object]:
        return {
            "rule": self.rule,
            "source": self.source,
            "target": self.target,
            "symmetric": self.symmetric,
            "description": self.description,
        }


# ------------------------------------------------------------------------------------ registries


class FrameRegistry:
    """Frame and relation registry. Open for extension, closed to redefinition.

    HOLDS BOTH because a relation is meaningless without both its frames, and a registry that
    accepted a relation naming an unregistered frame would let a typo create permanent, silent
    comparability between a real frame and a frame that does not exist.
    """

    def __init__(
        self,
        seed: Iterable[ReferenceFrame] = INITIAL_FRAMES,
        relations: Iterable[FrameRelation] = (),
    ) -> None:
        self._by_name: dict[str, ReferenceFrame] = {}
        self._relations: dict[tuple[str, str], FrameRelation] = {}
        for frame in seed:
            self.declare(frame)
        for relation in relations:
            self.relate(relation)

    def declare(self, frame: ReferenceFrame) -> ReferenceFrame:
        existing = self._by_name.get(frame.name)
        if existing is None:
            self._by_name[frame.name] = frame
            return frame
        if existing != frame:
            raise ReferenceError(
                f"frame {frame.name!r} is already declared with a different meaning, and one name "
                "with two meanings makes every comparability claim about it unenforceable"
            )
        return existing

    def declare_name(
        self, name: str, description: str, *, anchor: str = "", physical: bool = True
    ) -> ReferenceFrame:
        """Declare from primitives. DELIVERABLE Ω∞-T3 in one call, with no edit to this module."""
        return self.declare(ReferenceFrame(name, description, anchor, physical))

    def resolve(self, name: str) -> ReferenceFrame:
        try:
            return self._by_name[name]
        except KeyError:
            raise ReferenceError(
                f"{name!r} is not a declared reference frame; declare it before recording a "
                "coordinate in it, so a misspelling cannot become a frame comparable with nothing"
            ) from None

    def relate(self, relation: FrameRelation) -> FrameRelation:
        for name in (relation.source, relation.target):
            if name not in self._by_name:
                raise ReferenceError(
                    f"the relation {relation.rule} names frame {name!r}, which is not declared; a "
                    "relation to an undeclared frame is comparability granted to nothing"
                )
        key = (relation.source, relation.target)
        existing = self._relations.get(key)
        if existing is not None and existing != relation:
            raise ReferenceError(
                f"a relation between {relation.source} and {relation.target} is already declared "
                f"as "
                f"{existing.rule}; a second one as {relation.rule} would make comparability depend "
                "on declaration order"
            )
        self._relations[key] = relation
        return relation

    def comparable(self, left: ReferenceFrame, right: ReferenceFrame) -> FrameRelation | None:
        """The relation permitting comparison, or ``None``. IDENTITY IS ALWAYS COMPARABLE.

        A frame is comparable with itself by construction and needs no declaration — requiring one
        would mean every deployment starts by declaring seven reflexive relations, and a deployment
        that forgot would find its own records incomparable with each other.
        """
        if left == right:
            return FrameRelation(
                left.name,
                right.name,
                "Ω²-F-00",
                "Identity. Two positions observed in one frame are comparable without declaration.",
            )
        direct = self._relations.get((left.name, right.name))
        if direct is not None:
            return direct
        reverse = self._relations.get((right.name, left.name))
        if reverse is not None and reverse.symmetric:
            return reverse
        return None

    def relations(self) -> tuple[FrameRelation, ...]:
        return tuple(sorted(self._relations.values()))

    def known(self) -> tuple[ReferenceFrame, ...]:
        return tuple(sorted(self._by_name.values()))

    def __contains__(self, name: object) -> bool:
        return isinstance(name, str) and name in self._by_name

    def __len__(self) -> int:
        return len(self._by_name)


class ScaleRegistry:
    """Time scale registry. Same construction and argument as ``FrameRegistry``."""

    def __init__(self, seed: Iterable[TimeScale] = INITIAL_SCALES) -> None:
        self._by_name: dict[str, TimeScale] = {}
        for scale in seed:
            self.declare(scale)

    def declare(self, scale: TimeScale) -> TimeScale:
        existing = self._by_name.get(scale.name)
        if existing is None:
            self._by_name[scale.name] = scale
            return scale
        if existing != scale:
            raise ReferenceError(
                f"scale {scale.name!r} is already declared with a different meaning; one name "
                "counting two different things makes every position recorded in it ambiguous"
            )
        return existing

    def declare_name(
        self,
        name: str,
        unit: str,
        description: str,
        ordering: Ordering,
        *,
        vector: bool = False,
    ) -> TimeScale:
        """Declare a scale from primitives. ``ordering`` is positional and required, so a caller
        cannot acquire a total-order claim by omission."""
        return self.declare(TimeScale(name, unit, description, ordering, vector))

    def resolve(self, name: str) -> TimeScale:
        try:
            return self._by_name[name]
        except KeyError:
            raise ReferenceError(
                f"{name!r} is not a declared time scale; declare it before recording a position in "
                "it, so a misspelling cannot become a unit nobody defines"
            ) from None

    def known(self) -> tuple[TimeScale, ...]:
        return tuple(sorted(self._by_name.values()))

    def __contains__(self, name: object) -> bool:
        return isinstance(name, str) and name in self._by_name

    def __len__(self) -> int:
        return len(self._by_name)


def default_frames() -> FrameRegistry:
    """A registry of the shipped frames, with NO relations declared between any of them.

    THE EMPTY RELATION SET IS THE HONEST DEFAULT. Shipping a Mars-to-Earth relation would ship a
    comparability claim this package cannot support, and every downstream comparison would inherit
    it silently. A deployment that can relate two frames declares the relation and names the rule
    that justifies it.
    """
    return FrameRegistry()


def default_scales() -> ScaleRegistry:
    return ScaleRegistry()


__all__ = [
    "BLOCK_HEIGHT",
    "DISTRIBUTED_FRAME",
    "EARTH_FRAME",
    "INITIAL_FRAMES",
    "INITIAL_SCALES",
    "LAMPORT_EVENT",
    "LOGICAL_FRAME",
    "LOGICAL_TICK",
    "LUNAR_DAY",
    "LUNAR_FRAME",
    "MARS_FRAME",
    "MARS_SOL",
    "MISSION_ELAPSED",
    "OBSERVER_REPORT",
    "SIMULATION_FRAME",
    "SIMULATION_STEP",
    "SI_SECOND",
    "SPACECRAFT_FRAME",
    "VECTOR_EVENT",
    "FrameRegistry",
    "FrameRelation",
    "ReferenceError",
    "ReferenceFrame",
    "ScaleRegistry",
    "TimeScale",
    "default_frames",
    "default_scales",
]
