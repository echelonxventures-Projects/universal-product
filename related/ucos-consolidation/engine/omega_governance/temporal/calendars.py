"""UCOS Ω∞ Phase 2 Temporal, Deliverable 2 — calendars as providers, and only as providers.

AUTHORITY = NONE (DERIVED TRUTH).

THE ASSUMPTION THIS REMOVES. ``"2026-08-29T04:43:33Z"`` is not a time; it is a Gregorian rendering
of a time, produced by a calendar, in a locale, under a leap-second table. Storing the rendering
makes the calendar part of the record's identity, with three consequences that all look like
unrelated bugs later:

    the digest changes when the renderer changes    a format tweak invalidates a hash chain
    ordering depends on the format                  "10" sorts before "9" in the wrong field
    a non-Gregorian observer cannot be recorded     Mars sols have no month of August

WHAT A CALENDAR IS HERE. A pure function from an integer position to human-readable fields, bound to
the frame and scale in which those fields mean anything. Nothing else in this package consults a
calendar, and no governance decision has access to one. Calendars write into
``TemporalCoordinate.labels``, which is declared ``compare=False``, so a rendering can never change
what a coordinate IS.

THE PROPERTY THAT MAKES DELIVERABLE Ω∞-T2 ADDITIVE RATHER THAN BREAKING::

    coordinate == render(coordinate, calendars)
    coordinate.identity() == render(coordinate, calendars).identity()

Registering a calendar enriches what a record DISPLAYS and cannot alter what it MEANS. If labels
were part of identity, adding a calendar provider would rewrite every digest in an append-only
register, and "extension without code modification" would be true of the code and false of the data.
Asserted by ``assert_presentation_only``.

NO ``datetime``, NO ``time``, NO ``calendar`` MODULE. ``ProlepticCivilCalendar`` implements
civil-date arithmetic in integers, so the one place Gregorian knowledge exists in this repository's
Phase 2 tree is a single class that a caller may decline to register. That is the literal form of
"no domain model may assume Gregorian": not a coding-standards note, but the fact that deleting this
class breaks no governance logic.

WHAT THESE CALENDARS DELIBERATELY DO NOT DO.

    leap seconds     ``ProlepticCivilCalendar`` counts uniform 86 400-second days. A leap-second
                     table is a published fact about one planet's rotation that changes after the
                     records it affects were written, and a governance vocabulary must not pretend
                     to own it. The calendar states the simplification instead of hiding it.
    epoch choice     the epoch is a CONSTRUCTOR ARGUMENT, never a constant. A record whose epoch
                     was assumed is a record nobody can re-derive.
    conversion       no calendar converts between frames. ``MarsSolCalendar`` renders Mars sols and
                     has no opinion about what an Earth date they correspond to, because answering
                     that needs an ephemeris this package cannot verify.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from engine.omega_governance.reference.encoding import Encoding
from engine.omega_governance.temporal.coordinate import TemporalCoordinate
from engine.omega_governance.temporal.frames import (
    EARTH_FRAME,
    LOGICAL_FRAME,
    LOGICAL_TICK,
    MARS_FRAME,
    MARS_SOL,
    SI_SECOND,
    ReferenceFrame,
    TimeScale,
)
from engine.omega_governance.temporal.ordering import Position

#: Seconds in a civil day as ``ProlepticCivilCalendar`` counts them. DECLARED, and declared to be a
#: simplification: it ignores leap seconds, which is why a calendar is a provider and not a truth.
SECONDS_PER_DAY = 86400

#: Days from the proleptic Gregorian year 0000-03-01 to 1970-01-01, the shift used by the integer
#: civil-date algorithm below. A constant of the ARITHMETIC, not a choice about epochs — the epoch a
#: caller's positions are measured from is a constructor argument.
CIVIL_SHIFT = 719468


class CalendarError(RuntimeError):
    """A calendar was asked to render a position it cannot describe.

    RAISED, NEVER DEFAULTED. A calendar that rendered a Mars sol as a Gregorian date would produce a
    label that reads as fact and is not one, and a label that reads as fact is worse than no label.
    """


@runtime_checkable
class CalendarProvider(Protocol):
    """The calendar contract. Two declarations and two renderings.

    EXPRESSIBLE WITHOUT PYTHON, per Deliverable Ω∞-T7: the inputs are integers, the outputs are a
    string and a mapping of string to integer. ``schema.py`` emits it as a language-neutral
    contract.
    """

    def identifier(self) -> str:
        """A stable, unique name, used as the key under which a label is stored."""

    def frame(self) -> ReferenceFrame:
        """The frame in which this calendar's fields mean anything."""

    def scale(self) -> TimeScale:
        """The scale this calendar reads. A calendar for sols cannot read seconds."""

    def label(self, position: Position) -> str:
        """A human-readable rendering. PRESENTATION ONLY; never compared, never hashed."""

    def fields(self, position: Position) -> Mapping[str, int]:
        """The decomposition into named integer fields, so a consumer need not parse the label."""


@dataclass(frozen=True)
class TickCalendar:
    """Renders a logical counter. The calendar for a frame with no calendar.

    PRESENT BECAUSE EVERY SCALE DESERVES A RENDERING. Without it, a logical position would have no
    label and a reader would reach for a civil one, which is how an Earth calendar ends up
    describing a frame-free counter.
    """

    calendar_identifier: str = "tick"

    def identifier(self) -> str:
        return self.calendar_identifier

    def frame(self) -> ReferenceFrame:
        return LOGICAL_FRAME

    def scale(self) -> TimeScale:
        return LOGICAL_TICK

    def label(self, position: Position) -> str:
        return f"tick {counter(position, 'tick')}"

    def fields(self, position: Position) -> Mapping[str, int]:
        return {"tick": counter(position, "tick")}


def counter(position: Position, calendar: str) -> int:
    """The first component of ``position`` as a whole number, or a NAMED refusal.

    WHY THIS IS A FUNCTION AND NOT THREE `if not position` GUARDS. Each calendar checked that the
    position was non-empty and then did arithmetic on ``position[0]`` whatever it turned out to be.
    A ``Position`` is a tuple of OPAQUE components by design — that opacity is what lets a domain be
    measurable without being numeric — so a component that is not a count is an ordinary thing to
    receive and the calendars were the wrong place to assume otherwise. The two arithmetic calendars
    let a raw ``TypeError`` out of ``divmod``, which a caller cannot tell from a bug in its own
    code,
    and ``TickCalendar`` did something quieter and worse: it returned the component unexamined, so
    ``fields`` annotated ``Mapping[str, int]`` handed back a ``str`` and the mislabelling travelled.

    ``bool`` is rejected alongside the rest. It is an ``int`` to Python and never a tick, a
    second or
    a sol to anyone, and admitting it would render ``True`` as sol 1.
    """
    if not position:
        raise CalendarError(
            f"the {calendar} calendar cannot describe an empty position; a coordinate always "
            "carries at least one component, so an empty one is a malformed coordinate rather "
            "than an unrenderable time"
        )
    component = position[0]
    if isinstance(component, bool) or not isinstance(component, int):
        raise CalendarError(
            f"the {calendar} calendar reads a whole-number count and was given "
            f"{component!r} ({type(component).__name__}); a position component is opaque by "
            "design, "
            "so a calendar that cannot describe one must say so rather than compute with it"
        )
    return component


def civil_from_days(days: int) -> tuple[int, int, int]:
    """Proleptic Gregorian ``(year, month, day)`` from a day count, in integers only.

    THE ONLY GREGORIAN ARITHMETIC IN THE PACKAGE, and it is reachable from exactly one calendar
    provider. Integer division throughout: no floating point, no ``datetime``, no locale, and
    therefore the same answer on every machine — which is what Deliverable Ω∞-T6 requires of
    anything that touches a record.
    """
    shifted = days + CIVIL_SHIFT
    era = (shifted if shifted >= 0 else shifted - 146096) // 146097
    day_of_era = shifted - era * 146097
    year_of_era = (
        day_of_era - day_of_era // 1460 + day_of_era // 36524 - day_of_era // 146096
    ) // 365
    year = year_of_era + era * 400
    day_of_year = day_of_era - (365 * year_of_era + year_of_era // 4 - year_of_era // 100)
    month_prime = (5 * day_of_year + 2) // 153
    day = day_of_year - (153 * month_prime + 2) // 5 + 1
    month = month_prime + (3 if month_prime < 10 else -9)
    return (year + (1 if month <= 2 else 0), month, day)


@dataclass(frozen=True)
class ProlepticCivilCalendar:
    """Earth civil dates from a declared epoch. The Gregorian provider, and nothing more.

    ``epoch_day`` states which day the position's day zero is, expressed as days from 1970-01-01.
    DEFAULTS TO ZERO AND IS STILL A DECLARATION: the default is recorded in the calendar's report,
    so a record's rendering can be re-derived by someone who was not there.

    A caller wanting a different civil convention — a fiscal calendar, a Julian one, a local
    calendar with a different new year — registers another provider. This class is not privileged
    and holds no fallback role.
    """

    calendar_identifier: str = "earth-civil"
    epoch_day: int = 0

    def identifier(self) -> str:
        return self.calendar_identifier

    def frame(self) -> ReferenceFrame:
        return EARTH_FRAME

    def scale(self) -> TimeScale:
        return SI_SECOND

    def fields(self, position: Position) -> Mapping[str, int]:
        seconds = counter(position, "civil")
        days, second_of_day = divmod(seconds, SECONDS_PER_DAY)
        year, month, day = civil_from_days(days + self.epoch_day)
        hour, remainder = divmod(second_of_day, 3600)
        minute, second = divmod(remainder, 60)
        decomposed = {
            "year": year,
            "month": month,
            "day": day,
            "hour": hour,
            "minute": minute,
            "second": second,
        }
        if len(position) > 1:
            decomposed["subsecond"] = position[1]
        return decomposed

    def label(self, position: Position) -> str:
        """A civil rendering. NOT called an ISO-8601 timestamp, because it is not one.

        The shape is familiar on purpose and the name avoids the claim: this is what THIS provider
        renders, under a declared epoch and with leap seconds ignored. Calling it ISO-8601 would
        assert conformance to a standard whose leap-second handling this class does not implement.
        """
        parts = self.fields(position)
        return (
            f"{parts['year']:04d}-{parts['month']:02d}-{parts['day']:02d} "
            f"{parts['hour']:02d}:{parts['minute']:02d}:{parts['second']:02d} "
            f"[{EARTH_FRAME.name} civil, epoch_day={self.epoch_day}, leap seconds not modelled]"
        )


#: Sols in a Darian quarter: five months of 28 and one of 27. Four quarters give 668, and a leap
#: year extends the final month to 28 for 669. DECLARED HERE rather than computed from an
#: astronomical model, because this class renders and does not measure.
DARIAN_QUARTER_MONTHS = 6
DARIAN_LONG_MONTH = 28
DARIAN_SHORT_MONTH = 27


@dataclass(frozen=True)
class MarsSolCalendar:
    """Mars sols rendered in the Darian month structure. A second planet, as a registration.

    WHY THIS SHIPS AT ALL. Deliverable Ω∞-T5 requires a contradiction record stamped with a Mars
    coordinate, and a coordinate with no calendar would be renderable only by an Earth calendar,
    which would either refuse or lie. Shipping one non-Earth calendar proves the frame and scale
    machinery is genuinely used rather than merely declared.

    THE SIMPLIFICATION IS STATED, NOT HIDDEN. The month lengths and the leap rule below are the
    declared Darian structure; this class does not derive them from an areocentric ephemeris and
    does not claim to. A deployment with a precise Mars timekeeping requirement registers its own
    provider, which is the entire point of calendars being providers.
    """

    calendar_identifier: str = "mars-darian"
    epoch_sol: int = 0

    def identifier(self) -> str:
        return self.calendar_identifier

    def frame(self) -> ReferenceFrame:
        return MARS_FRAME

    def scale(self) -> TimeScale:
        return MARS_SOL

    @staticmethod
    def leap(year: int) -> bool:
        """The declared Darian leap rule. Odd years, plus decades with a century exception."""
        if year % 2 == 1:
            return True
        return year % 10 == 0 and not (year % 100 == 0 and year % 500 != 0)

    @classmethod
    def sols_in_month(cls, year: int, month: int) -> int:
        position_in_quarter = ((month - 1) % DARIAN_QUARTER_MONTHS) + 1
        if position_in_quarter <= DARIAN_QUARTER_MONTHS - 1:
            return DARIAN_LONG_MONTH
        if month == 24 and cls.leap(year):
            return DARIAN_LONG_MONTH
        return DARIAN_SHORT_MONTH

    @classmethod
    def sols_in_year(cls, year: int) -> int:
        return sum(cls.sols_in_month(year, month) for month in range(1, 25))

    def fields(self, position: Position) -> Mapping[str, int]:
        remaining = counter(position, "sol") + self.epoch_sol
        year = 1
        # Walk years rather than solving in closed form. The Darian leap rule is not expressible as
        # a single division, and a closed form that was subtly wrong would be far harder to notice
        # than a loop that is obviously right.
        while remaining >= self.sols_in_year(year):
            remaining -= self.sols_in_year(year)
            year += 1
        while remaining < 0:
            year -= 1
            remaining += self.sols_in_year(year)
        month = 1
        while remaining >= self.sols_in_month(year, month):
            remaining -= self.sols_in_month(year, month)
            month += 1
        return {"year": year, "month": month, "sol": remaining + 1}

    def label(self, position: Position) -> str:
        parts = self.fields(position)
        return (
            f"Mars year {parts['year']}, month {parts['month']}, sol {parts['sol']} "
            f"[{MARS_FRAME.name} Darian structure, epoch_sol={self.epoch_sol}]"
        )


class CalendarRegistry:
    """Calendar identifier -> provider, plus lookup by frame and scale.

    A DUPLICATE IDENTIFIER RAISES, because the identifier is the key a label is stored under: two
    providers sharing one would make a coordinate's rendering depend on registration order, and a
    reader comparing two records would see a difference that is not a difference in time.
    """

    def __init__(self, seed: Iterable[CalendarProvider] = ()) -> None:
        self._by_name: dict[str, CalendarProvider] = {}
        for calendar in seed:
            self.register(calendar)

    def register(self, calendar: CalendarProvider) -> CalendarProvider:
        identifier = calendar.identifier()
        if not identifier.strip():
            raise CalendarError("a calendar must identify itself to be registered")
        if identifier in self._by_name:
            raise CalendarError(
                f"a calendar identified {identifier!r} is already registered; replacing it "
                f"silently "
                "would make a coordinate's rendering depend on registration order"
            )
        self._by_name[identifier] = calendar
        return calendar

    def resolve(self, identifier: str) -> CalendarProvider:
        try:
            return self._by_name[identifier]
        except KeyError:
            raise CalendarError(
                f"{identifier!r} names no registered calendar; register it before rendering with "
                "it, so a missing calendar cannot be replaced by a plausible-looking default"
            ) from None

    def for_coordinate(self, coordinate: TemporalCoordinate) -> tuple[CalendarProvider, ...]:
        """Every calendar whose frame AND scale match. Both must match, and neither is inferred.

        A calendar for Earth seconds asked to render Mars sols would produce a date, and the date
        would be meaningless. Matching on both is what makes silence the outcome for an unrenderable
        coordinate, rather than a wrong label.
        """
        return tuple(
            calendar
            for _, calendar in sorted(self._by_name.items())
            if calendar.frame() == coordinate.frame and calendar.scale() == coordinate.scale
        )

    def known(self) -> tuple[str, ...]:
        return tuple(sorted(self._by_name))

    def report(self) -> dict[str, object]:
        return {
            identifier: {"frame": calendar.frame().name, "scale": calendar.scale().name}
            for identifier, calendar in sorted(self._by_name.items())
        }

    def __contains__(self, identifier: object) -> bool:
        return isinstance(identifier, str) and identifier in self._by_name

    def __len__(self) -> int:
        return len(self._by_name)


def render(coordinate: TemporalCoordinate, calendars: CalendarRegistry) -> TemporalCoordinate:
    """A copy carrying every applicable calendar's label. IDENTITY UNCHANGED, and that is the claim.

    A coordinate no registered calendar can describe is returned UNCHANGED rather than raising. A
    frame with no calendar is a normal condition — a spacecraft mission clock may never acquire one
    — and refusing to record an event because nobody can pretty-print it would make renderability a
    precondition of governance.
    """
    rendered = coordinate
    for calendar in calendars.for_coordinate(coordinate):
        rendered = rendered.with_label(calendar.identifier(), calendar.label(coordinate.position))
    return rendered


def assert_presentation_only(
    coordinate: TemporalCoordinate, calendars: CalendarRegistry, encoding: Encoding
) -> None:
    """Refuse a calendar registry whose rendering changes a coordinate's identity.

    THE PROPERTY DELIVERABLE Ω∞-T2 RESTS ON. If rendering changed equality or the fingerprint,
    registering a calendar would rewrite every entry in an append-only register — extension without
    code modification, purchased with a silent migration of all existing data.

    ``encoding`` is required and has no default, so the guarantee is about a NAMED representation
    and identity system rather than about whichever pair this file happened to import.
    """
    rendered = render(coordinate, calendars)
    if rendered != coordinate:
        raise CalendarError(
            f"rendering {coordinate} changed its identity; a label is presentation and must never "
            "participate in equality, or adding a calendar becomes a data migration"
        )
    if rendered.identity(encoding) != coordinate.identity(encoding):
        raise CalendarError(  # pragma: no cover - equality above implies this
            f"rendering {coordinate} changed its fingerprint under {encoding.codec.identifier()}"
        )


def default_registry(calendars: Iterable[CalendarProvider] = ()) -> CalendarRegistry:
    """The three shipped calendars, plus whatever the caller supplies.

    THREE, ACROSS TWO PLANETS AND ONE NON-PLACE. Enough to demonstrate that frame and scale matching
    is real, and deliberately not enough to look like a complete list of how time is written down.
    """
    registry = CalendarRegistry((TickCalendar(), ProlepticCivilCalendar(), MarsSolCalendar()))
    for calendar in calendars:
        registry.register(calendar)
    return registry


__all__ = [
    "CIVIL_SHIFT",
    "DARIAN_LONG_MONTH",
    "DARIAN_QUARTER_MONTHS",
    "DARIAN_SHORT_MONTH",
    "SECONDS_PER_DAY",
    "CalendarError",
    "CalendarProvider",
    "CalendarRegistry",
    "MarsSolCalendar",
    "ProlepticCivilCalendar",
    "TickCalendar",
    "assert_presentation_only",
    "civil_from_days",
    "counter",
    "default_registry",
    "render",
]
