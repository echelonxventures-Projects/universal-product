"""UCOS Ω∞ Phase 2 Temporal, Deliverable 3 — clocks as providers.

AUTHORITY = NONE (DERIVED TRUTH).

THIS MODULE IMPORTS NEITHER ``datetime`` NOR ``time``, and that absence is the deliverable rather
than a stylistic preference. A single ``import datetime`` anywhere reachable from a domain model
makes the system's temporal foundation the host operating system's clock, and every later attempt to
run under simulation time, replay a historical measurement or federate with an observer in another
frame becomes a rewrite instead of a registration.

HOW A REAL CIVIL CLOCK IS SUPPORTED WITHOUT BEING IMPORTED. ``ExternalClock`` takes a ``reader``
callable returning an integer position. The caller writes::

    import time                                     # in the CALLER, not in governance code
    civil = ExternalClock(
        "earth-civil-utc", EARTH_FRAME, SI_SECOND, TOTAL,
        reader=lambda: (int(time.time()), 0),
    )
    registry.register(civil)

Nothing in ``engine/omega_governance`` changed. The same three lines with a different reader produce
an atomic clock, a GPS clock, a spacecraft mission clock, a simulation stepper, a ledger height feed
or a clock backed by a remote time service. THAT is Deliverable Ω∞-T2: the extension point is a
constructor argument, not a branch in this file.

WHY A CLOCK DECLARES FOUR THINGS AND NOT ONE. ``read()`` alone would return a position and leave the
frame, the scale and the ordering to be inferred by whoever received it — which is the original
defect one level up. A clock therefore states its frame, its scale and its ordering, and
``assert_provider`` refuses a clock whose coordinates disagree with its own declarations. A
misconfigured ``ExternalClock`` claiming SI seconds while its reader returns sols is caught by
execution rather than discovered by a contradiction six months later.

THE SHIPPED CLOCKS, AND WHY EACH ONE IS HERE.

    LogicalClock   the package default. A counter in the LOGICAL frame, so Phase 2's own evidence
                   is byte-identical on every machine and in every century.
    FixedClock     one coordinate forever, for a caller replaying a measurement at a pinned
                   position.
    LamportClock   the classic total-order-from-messages construction. Present because it is the
                   most common distributed clock AND because it demonstrates the limitation: it is
                   TOTAL, so it can never report concurrency, even where concurrency is the fact.
    VectorClock    the one that CAN report concurrency. CAUSAL ordering, one counter per
                   participant, and the reason ``CONCURRENT`` exists as a relation at all.
    ExternalClock  every clock this package does not know about.

NO GLOBAL CLOCK, and no module-level default instance. A shared counter would make one measurement's
positions depend on how many records an unrelated earlier measurement wrote, so the evidence
document would stop being a function of the population it describes.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass
from itertools import count
from typing import Protocol, runtime_checkable

from engine.omega_governance.temporal.coordinate import TemporalCoordinate
from engine.omega_governance.temporal.frames import (
    LAMPORT_EVENT,
    LOGICAL_FRAME,
    LOGICAL_TICK,
    VECTOR_EVENT,
    ReferenceFrame,
    TimeScale,
)
from engine.omega_governance.temporal.ordering import (
    CAUSAL,
    TOTAL,
    Ordering,
    Position,
)


class ClockError(RuntimeError):
    """A clock was misconfigured, or a clock registry was asked for a clock nobody registered.

    RAISED, NEVER DEFAULTED. A missing clock must not silently become the logical one: a record
    stamped by a fallback clock nobody chose carries a frame nobody chose, and every comparison it
    participates in inherits the substitution.
    """


@runtime_checkable
class ClockProvider(Protocol):
    """The clock contract. Four declarations and one reading.

    EXPRESSIBLE WITHOUT PYTHON, which is Deliverable Ω∞-T7's requirement: four accessors returning
    names and one operation returning a record of integers and strings. ``schema.py`` emits exactly
    that as a language-neutral contract, so a governance engine in another language implements this
    interface without reproducing any Python type.
    """

    def identifier(self) -> str:
        """A stable, unique name, recorded on every coordinate this clock produces."""

    def frame(self) -> ReferenceFrame:
        """Where this clock's observations are made."""

    def scale(self) -> TimeScale:
        """What this clock's integers count."""

    def ordering(self) -> Ordering:
        """How positions from this clock are to be compared."""

    def read(self) -> TemporalCoordinate:
        """The current position, as a complete coordinate. Never a bare integer."""


class LogicalClock:
    """A monotonic counter in the LOGICAL frame. The package default, for determinism.

    WHY THE DEFAULT IS FRAME-FREE RATHER THAN EARTH. Phase 2's evidence document is compared
    byte-for-byte across runs and machines; any physically-anchored default makes that impossible on
    the first run. A logical position answers "before or after", which is every ordering question an
    append-only register needs, and declines to answer "at what hour", which is a question about the
    world rather than about the governance record. Declining visibly is better than answering
    wrongly — a fabricated civil time is indistinguishable from a measured one.
    """

    def __init__(self, identifier: str = "logical", *, start: int = 0) -> None:
        if not identifier.strip():
            raise ClockError("a clock must identify itself, because every coordinate cites it")
        self._identifier = identifier
        self._counter = count(start)

    def identifier(self) -> str:
        return self._identifier

    def frame(self) -> ReferenceFrame:
        return LOGICAL_FRAME

    def scale(self) -> TimeScale:
        return LOGICAL_TICK

    def ordering(self) -> Ordering:
        return TOTAL

    def read(self) -> TemporalCoordinate:
        return TemporalCoordinate(
            frame=LOGICAL_FRAME,
            scale=LOGICAL_TICK,
            ordering=TOTAL,
            position=(next(self._counter),),
            clock=self._identifier,
        )


@dataclass(frozen=True)
class FixedClock:
    """One coordinate, returned forever. For replaying a measurement at a pinned position."""

    coordinate: TemporalCoordinate

    def identifier(self) -> str:
        return self.coordinate.clock

    def frame(self) -> ReferenceFrame:
        return self.coordinate.frame

    def scale(self) -> TimeScale:
        return self.coordinate.scale

    def ordering(self) -> Ordering:
        return self.coordinate.ordering

    def read(self) -> TemporalCoordinate:
        return self.coordinate


class LamportClock:
    """A Lamport counter: advanced on local events, raised on receipt of a remote position.

    PRESENT PARTLY AS A CAUTIONARY EXHIBIT. Lamport timestamps are TOTAL, so ``compare`` over two of
    them can never return CONCURRENT — the construction guarantees an order exists, whether or not a
    causal relationship does. That is a real and useful property and it is also exactly the
    assumption a string timestamp makes silently. Here it is DECLARED: the clock says TOTAL, so a
    reader knows the order it reports may exceed what the causality supports, and can choose a
    ``VectorClock`` when that matters.
    """

    def __init__(self, identifier: str, *, start: int = 0) -> None:
        if not identifier.strip():
            raise ClockError("a clock must identify itself, because every coordinate cites it")
        self._identifier = identifier
        self._value = start

    def identifier(self) -> str:
        return self._identifier

    def frame(self) -> ReferenceFrame:
        return LOGICAL_FRAME

    def scale(self) -> TimeScale:
        return LAMPORT_EVENT

    def ordering(self) -> Ordering:
        return TOTAL

    def observe(self, position: Position) -> None:
        """Raise this clock past a received position. The Lamport receive rule."""
        if not position:
            raise ClockError("an observed Lamport position must carry at least one component")
        self._value = max(self._value, position[0])

    def read(self) -> TemporalCoordinate:
        self._value += 1
        return TemporalCoordinate(
            frame=LOGICAL_FRAME,
            scale=LAMPORT_EVENT,
            ordering=TOTAL,
            position=(self._value,),
            clock=self._identifier,
        )


class VectorClock:
    """One counter per participant. The clock that can report genuine concurrency.

    THE CLOCK THAT MAKES DELIVERABLE Ω∞-T5 OBSERVABLE. Two coordinates ``(1, 0)`` and ``(0, 1)``
    from a two-participant clock compare CONCURRENT under ``CausalStrategy`` — both events happened,
    neither caused the other, and any total order over them is invented. A contradiction record
    stamped by this clock therefore cannot assert a sequence the causality does not support, which
    is the property the directive asks for in the words "a contradiction record must not assume that
    every event has a globally agreed timestamp".
    """

    def __init__(self, identifier: str, participants: int, index: int) -> None:
        if not identifier.strip():
            raise ClockError("a clock must identify itself, because every coordinate cites it")
        if participants < 1:
            raise ClockError(
                "a vector clock needs at least one participant; a zero-width vector would make "
                "every position equal and every pair SIMULTANEOUS"
            )
        if not 0 <= index < participants:
            raise ClockError(
                f"participant index {index} is outside the vector of width {participants}, so this "
                "clock has no component of its own to advance"
            )
        self._identifier = identifier
        self._index = index
        self._components = [0] * participants

    def identifier(self) -> str:
        return self._identifier

    def frame(self) -> ReferenceFrame:
        return LOGICAL_FRAME

    def scale(self) -> TimeScale:
        return VECTOR_EVENT

    def ordering(self) -> Ordering:
        return CAUSAL

    def observe(self, position: Position) -> None:
        """Merge a received position componentwise. The vector-clock receive rule."""
        if len(position) != len(self._components):
            raise ClockError(
                f"an observed vector of width {len(position)} cannot be merged into a clock of "
                f"width {len(self._components)}; differently-shaped vectors describe different "
                "participant sets and merging them would fabricate causality"
            )
        self._components = [max(a, b) for a, b in zip(self._components, position, strict=True)]

    def read(self) -> TemporalCoordinate:
        self._components[self._index] += 1
        return TemporalCoordinate(
            frame=LOGICAL_FRAME,
            scale=VECTOR_EVENT,
            ordering=CAUSAL,
            position=tuple(self._components),
            clock=self._identifier,
        )


@dataclass(frozen=True)
class ExternalClock:
    """Every clock this package does not know about. THE Ω∞-T2 EXTENSION POINT.

    A civil clock, an atomic clock, a GPS clock, a spacecraft mission clock, a simulation stepper, a
    ledger height feed and a clock nobody has invented are all this class with a different
    ``reader``. The reader returns integers; the frame, scale and ordering are declared by the
    caller; nothing in this module learns a new name.

    WHY THE READER RETURNS A TUPLE OF INTEGERS AND NOT A FLOAT OR A STRING. The same reason
    ``Position`` is integral: a governance record that must hash identically twice cannot contain a
    value whose text depends on a locale, a precision setting or a floating-point unit. A caller
    with sub-second civil time returns ``(seconds, nanoseconds)``, which is exact.
    """

    clock_identifier: str
    clock_frame: ReferenceFrame
    clock_scale: TimeScale
    clock_ordering: Ordering
    reader: Callable[[], Position]

    def __post_init__(self) -> None:
        if not self.clock_identifier.strip():
            raise ClockError("a clock must identify itself, because every coordinate cites it")

    def identifier(self) -> str:
        return self.clock_identifier

    def frame(self) -> ReferenceFrame:
        return self.clock_frame

    def scale(self) -> TimeScale:
        return self.clock_scale

    def ordering(self) -> Ordering:
        return self.clock_ordering

    def read(self) -> TemporalCoordinate:
        return TemporalCoordinate(
            frame=self.clock_frame,
            scale=self.clock_scale,
            ordering=self.clock_ordering,
            position=tuple(self.reader()),
            clock=self.clock_identifier,
        )


class ClockRegistry:
    """Clock identifier -> provider. A duplicate identifier RAISES rather than replacing.

    Replacing silently would make the frame a record was stamped in depend on import order, which is
    the same defect Phase 1 records for ``ProviderRegistry`` and Phase 2 for ``AuthorityResolver``:
    a governance fact must not change because two modules were imported the other way round.
    """

    def __init__(self, seed: Iterable[ClockProvider] = ()) -> None:
        self._by_name: dict[str, ClockProvider] = {}
        for clock in seed:
            self.register(clock)

    def register(self, clock: ClockProvider) -> ClockProvider:
        identifier = clock.identifier()
        if not identifier.strip():
            raise ClockError("a clock must identify itself to be registered")
        if identifier in self._by_name:
            raise ClockError(
                f"a clock identified {identifier!r} is already registered; replacing it silently "
                "would change the frame every subsequent record is stamped in"
            )
        self._by_name[identifier] = clock
        return clock

    def resolve(self, identifier: str) -> ClockProvider:
        try:
            return self._by_name[identifier]
        except KeyError:
            raise ClockError(
                f"{identifier!r} names no registered clock; register it before stamping records "
                "with it, so a missing clock cannot be silently replaced by a default one"
            ) from None

    def known(self) -> tuple[str, ...]:
        return tuple(sorted(self._by_name))

    def report(self) -> dict[str, object]:
        return {
            identifier: {
                "frame": clock.frame().name,
                "scale": clock.scale().name,
                "ordering": clock.ordering().name,
                "vector": clock.scale().vector,
            }
            for identifier, clock in sorted(self._by_name.items())
        }

    def __contains__(self, identifier: object) -> bool:
        return isinstance(identifier, str) and identifier in self._by_name

    def __len__(self) -> int:
        return len(self._by_name)


def assert_provider(clock: ClockProvider, *, readings: int = 2) -> None:
    """Refuse a clock whose coordinates disagree with its own declarations.

    FOUR PROPERTIES, all measured rather than trusted. A clock that declared SI seconds while its
    reader returned sols would otherwise contaminate every comparison it took part in, and the error
    would surface as an unexplainable contradiction rather than as a misconfiguration.
    """
    if readings < 1:
        raise ClockError("a clock cannot be verified without being read at least once")
    for _ in range(readings):
        coordinate = clock.read()
        if coordinate.clock != clock.identifier():
            raise ClockError(
                f"clock {clock.identifier()!r} stamps its coordinates {coordinate.clock!r}; a "
                "coordinate that misnames its producer cannot be traced back to the clock whose "
                "frame it depends on"
            )
        if coordinate.frame != clock.frame():
            raise ClockError(
                f"clock {clock.identifier()!r} declares frame {clock.frame().name} and produced a "
                f"coordinate in {coordinate.frame.name}"
            )
        if coordinate.scale != clock.scale():
            raise ClockError(
                f"clock {clock.identifier()!r} declares scale {clock.scale().name} and produced a "
                f"coordinate on {coordinate.scale.name}; a mislabelled unit makes every comparison "
                "it joins arithmetically wrong while appearing well-formed"
            )
        if coordinate.ordering != clock.ordering():
            raise ClockError(
                f"clock {clock.identifier()!r} declares ordering {clock.ordering().name} and "
                f"produced a coordinate citing {coordinate.ordering.name}"
            )


def positions_of(clock: ClockProvider, readings: int) -> tuple[Position, ...]:
    """Read a clock ``readings`` times and return the positions. For evidence and tests."""
    return tuple(clock.read().position for _ in range(readings))


def default_registry(clocks: Sequence[ClockProvider] = ()) -> ClockRegistry:
    """A registry holding a fresh ``LogicalClock`` plus whatever the caller supplies.

    FRESH, NOT SHARED. Constructing the logical clock here rather than importing a module-level
    instance is what keeps one measurement's positions independent of another's.
    """
    registry = ClockRegistry((LogicalClock(),))
    for clock in clocks:
        registry.register(clock)
    return registry


__all__ = [
    "ClockError",
    "ClockProvider",
    "ClockRegistry",
    "ExternalClock",
    "FixedClock",
    "LamportClock",
    "LogicalClock",
    "VectorClock",
    "assert_provider",
    "default_registry",
    "positions_of",
]
