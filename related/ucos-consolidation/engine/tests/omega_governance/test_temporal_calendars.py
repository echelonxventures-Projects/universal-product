"""Ω∞ temporal — calendars as providers, and presentation that cannot become identity.

THE ONE PROPERTY THIS MODULE EXISTS TO GUARANTEE::

    coordinate == render(coordinate, calendars)
    coordinate.identity(encoding) == render(coordinate, calendars).identity(encoding)

Registering a calendar must enrich what a record DISPLAYS and must never alter what it MEANS. If
that fails, three unrelated-looking bugs follow at once: a digest that changes when a renderer is
reworded, an ordering that depends on a format, and a hash chain that a locale invalidates.

WHY THIS SUITE EXISTS AT ALL. Ω-3 measured ``calendars.py`` as UNREACHABLE — no import, plane or
entry point reached it, because the only thing that ever imported it was a one-shot probe script
outside the governed tree. A module nothing reaches is a module nothing checks, and this one carries
the arithmetic (``civil_from_days``, the Darian leap rule) most likely to be quietly wrong.
"""

from __future__ import annotations

import pytest

from engine.omega_governance.reference.encoding import (
    CanonicalJsonCodec,
    Encoding,
    PolynomialIdentity,
    default_encoding,
)
from engine.omega_governance.temporal.calendars import (
    CIVIL_SHIFT,
    SECONDS_PER_DAY,
    CalendarError,
    CalendarRegistry,
    MarsSolCalendar,
    ProlepticCivilCalendar,
    TickCalendar,
    assert_presentation_only,
    civil_from_days,
    default_registry,
    render,
)
from engine.omega_governance.temporal.coordinate import TemporalCoordinate
from engine.omega_governance.temporal.frames import (
    EARTH_FRAME,
    LOGICAL_FRAME,
    LOGICAL_TICK,
    MARS_FRAME,
    MARS_SOL,
    SI_SECOND,
)
from engine.omega_governance.temporal.ordering import TOTAL


def _tick(position: int = 0) -> TemporalCoordinate:
    return TemporalCoordinate(LOGICAL_FRAME, LOGICAL_TICK, TOTAL, (position,), "logical")


def _earth(seconds: int) -> TemporalCoordinate:
    return TemporalCoordinate(EARTH_FRAME, SI_SECOND, TOTAL, (seconds,), "earth-clock")


def _mars(sols: int) -> TemporalCoordinate:
    return TemporalCoordinate(MARS_FRAME, MARS_SOL, TOTAL, (sols,), "mars-clock")


# ------------------------------------------------------------------- the identity property


def test_rendering_leaves_a_coordinate_equal_to_itself() -> None:
    """The additive-not-breaking property, stated as the module states it."""
    coordinate = _tick(5)
    assert coordinate == render(coordinate, default_registry())


def test_rendering_leaves_a_coordinates_identity_unchanged_under_every_encoding() -> None:
    registry = default_registry()
    for encoding in (
        default_encoding(),
        Encoding(CanonicalJsonCodec(), PolynomialIdentity()),
    ):
        for coordinate in (_tick(5), _earth(86_400), _mars(3)):
            assert render(coordinate, registry).identity(encoding) == coordinate.identity(encoding)


def test_assert_presentation_only_passes_over_the_shipped_calendars() -> None:
    encoding = default_encoding()
    registry = default_registry()
    for coordinate in (_tick(0), _earth(0), _mars(0)):
        assert_presentation_only(coordinate, registry, encoding)


def test_assert_presentation_only_refuses_a_calendar_that_changes_identity() -> None:
    """Non-vacuity. The guarantee is worth exactly as much as this check's ability to fail, so a
    calendar that reaches past ``labels`` must be caught rather than trusted not to exist."""

    class IdentityChangingCalendar:
        def identifier(self) -> str:
            return "meddling"

        def frame(self):  # noqa: ANN201 - mirrors the CalendarProvider protocol
            return LOGICAL_FRAME

        def scale(self):  # noqa: ANN201
            return LOGICAL_TICK

        def label(self, position: tuple[object, ...]) -> str:
            return "a label"

        def fields(self, position: tuple[object, ...]) -> dict[str, int]:
            return {}

    class MeddlingRegistry(CalendarRegistry):
        def for_coordinate(self, coordinate: TemporalCoordinate):  # noqa: ANN201
            return (IdentityChangingCalendar(),)

    class Reshaping(MeddlingRegistry):
        pass

    registry = Reshaping()

    # A registry whose rendering step returns a DIFFERENT position rather than a label.
    def meddling_render(coordinate: TemporalCoordinate, _calendars: CalendarRegistry):
        return TemporalCoordinate(
            coordinate.frame,
            coordinate.scale,
            coordinate.ordering,
            (coordinate.position[0] + 1,),
            coordinate.clock,
        )

    import engine.omega_governance.temporal.calendars as calendars_module

    original = calendars_module.render
    calendars_module.render = meddling_render
    try:
        with pytest.raises(CalendarError):
            assert_presentation_only(_tick(1), registry, default_encoding())
    finally:
        calendars_module.render = original


# ------------------------------------------------------------------------------- selection


def test_a_calendar_is_selected_only_when_both_frame_and_scale_match() -> None:
    """Neither is inferred. A calendar for sols must never be handed a count of seconds, and the
    only thing standing between those two is that BOTH declarations are checked."""
    registry = default_registry()
    assert [c.identifier() for c in registry.for_coordinate(_tick(0))] == ["tick"]
    assert [c.identifier() for c in registry.for_coordinate(_earth(0))] == ["earth-civil"]
    assert [c.identifier() for c in registry.for_coordinate(_mars(0))] == ["mars-darian"]


def test_a_coordinate_no_calendar_matches_renders_with_no_label_and_no_error() -> None:
    """A frame with no calendar is an ordinary situation, not a fault: the position is still a
    complete coordinate and simply has no human rendering."""
    lunar = TemporalCoordinate(LOGICAL_FRAME, MARS_SOL, TOTAL, (1,), "odd-clock")
    rendered = render(lunar, default_registry())
    assert rendered.labels == {}
    assert rendered == lunar


def test_the_registry_ships_three_calendars_and_refuses_a_duplicate() -> None:
    registry = default_registry()
    assert registry.known() == ("earth-civil", "mars-darian", "tick")
    with pytest.raises(CalendarError):
        registry.register(TickCalendar())


def test_an_unregistered_calendar_identifier_is_refused() -> None:
    with pytest.raises(CalendarError):
        default_registry().resolve("julian")


def test_a_deployment_can_register_its_own_calendar_with_no_edit_to_the_module() -> None:
    class StardateCalendar:
        def identifier(self) -> str:
            return "stardate"

        def frame(self):  # noqa: ANN201
            return LOGICAL_FRAME

        def scale(self):  # noqa: ANN201
            return LOGICAL_TICK

        def label(self, position: tuple[object, ...]) -> str:
            return f"stardate {position[0]}"

        def fields(self, position: tuple[object, ...]) -> dict[str, int]:
            return {"stardate": int(position[0])}

    registry = default_registry([StardateCalendar()])
    rendered = render(_tick(9), registry)
    assert rendered.labels["stardate"] == "stardate 9"
    assert rendered.labels["tick"] == "tick 9"


def test_two_calendars_over_one_coordinate_both_render_and_neither_wins() -> None:
    """Renderings accumulate. A calendar is not a formatter the coordinate is stuck with."""

    class RomanTickCalendar:
        def identifier(self) -> str:
            return "roman-tick"

        def frame(self):  # noqa: ANN201
            return LOGICAL_FRAME

        def scale(self):  # noqa: ANN201
            return LOGICAL_TICK

        def label(self, position: tuple[object, ...]) -> str:
            return "IX" if position[0] == 9 else str(position[0])

        def fields(self, position: tuple[object, ...]) -> dict[str, int]:
            return {"tick": int(position[0])}

    rendered = render(_tick(9), default_registry([RomanTickCalendar()]))
    assert set(rendered.labels) == {"tick", "roman-tick"}


# ------------------------------------------------------------------------------ arithmetic


def test_the_civil_epoch_day_zero_is_the_unix_epoch_date() -> None:
    assert civil_from_days(0) == (1970, 1, 1)


def test_civil_from_days_handles_leap_years_and_century_rules() -> None:
    """The Gregorian rule in integers, checked at the three dates that separate it from a naive
    every-fourth-year one."""
    assert civil_from_days(59) == (1970, 3, 1)
    assert civil_from_days(365) == (1971, 1, 1)
    # 1972 was a leap year: 29 February exists, and 1 March is the day after.
    assert civil_from_days(365 + 365 + 59) == (1972, 2, 29)
    assert civil_from_days(365 + 365 + 60) == (1972, 3, 1)
    # 2000 was a leap year (divisible by 400); 1900 was not (divisible by 100, not by 400).
    assert civil_from_days(11016) == (2000, 2, 29)


def test_civil_from_days_runs_backwards_before_the_epoch() -> None:
    """A proleptic calendar that only counted forwards would make every pre-1970 observation
    unrenderable, which is a limit nobody declared."""
    assert civil_from_days(-1) == (1969, 12, 31)
    assert civil_from_days(-365) == (1969, 1, 1)


def test_the_civil_shift_constant_is_the_one_the_algorithm_needs() -> None:
    assert CIVIL_SHIFT == 719468
    assert SECONDS_PER_DAY == 86400


def test_the_earth_calendar_reads_seconds_and_renders_a_civil_date() -> None:
    calendar = ProlepticCivilCalendar()
    assert calendar.frame() == EARTH_FRAME
    assert calendar.scale() == SI_SECOND
    fields = calendar.fields((SECONDS_PER_DAY * 3,))
    assert (fields["year"], fields["month"], fields["day"]) == (1970, 1, 4)
    assert "1970" in calendar.label((SECONDS_PER_DAY * 3,))


def test_the_earth_calendar_honours_a_declared_epoch_day() -> None:
    shifted = ProlepticCivilCalendar(epoch_day=1)
    fields = shifted.fields((0,))
    assert (fields["year"], fields["month"], fields["day"]) == (1970, 1, 2)


def test_the_darian_leap_rule_is_the_declared_one_and_not_the_gregorian_one() -> None:
    """Odd years leap, plus decades with a century exception. Reusing the Gregorian rule here is the
    error a single-planet assumption produces, and it would be invisible in every Earth test."""
    calendar = MarsSolCalendar()
    assert calendar.leap(1) is True
    assert calendar.leap(2) is False
    assert calendar.leap(10) is True
    assert calendar.leap(100) is False


def test_a_darian_year_is_668_or_669_sols_and_never_365() -> None:
    calendar = MarsSolCalendar()
    for year in range(1, 12):
        assert calendar.sols_in_year(year) in (668, 669)


def test_the_darian_month_lengths_follow_the_declared_quarter_structure() -> None:
    calendar = MarsSolCalendar()
    assert calendar.sols_in_month(1, 1) == 28
    assert calendar.sols_in_month(2, 6) == 27


def test_the_mars_calendar_reads_sols_and_never_seconds() -> None:
    calendar = MarsSolCalendar()
    assert calendar.frame() == MARS_FRAME
    assert calendar.scale() == MARS_SOL
    fields = calendar.fields((0,))
    assert set(fields) >= {"year", "month", "sol"}


def test_the_mars_calendar_walks_a_whole_year_without_losing_a_sol() -> None:
    """Structural: month lengths must sum to the year length, or a rendering drifts by a sol per
    year and nothing notices for a decade."""
    calendar = MarsSolCalendar()
    for year in (1, 2, 10):
        total = sum(calendar.sols_in_month(year, month) for month in range(1, 25))
        assert total == calendar.sols_in_year(year)


def test_the_tick_calendar_renders_the_frame_that_has_no_calendar() -> None:
    calendar = TickCalendar()
    assert calendar.frame() == LOGICAL_FRAME
    assert calendar.label((7,)) == "tick 7"
    assert calendar.fields((7,)) == {"tick": 7}


def test_every_calendar_refuses_an_empty_position_by_name() -> None:
    for calendar in (TickCalendar(), ProlepticCivilCalendar(), MarsSolCalendar()):
        with pytest.raises(CalendarError):
            calendar.fields(())


def test_every_calendar_refuses_a_component_that_is_not_a_count() -> None:
    """A position component is OPAQUE by design — that opacity is what lets a domain be measurable
    without being numeric — so a calendar receiving one it cannot read must say so.

    Before the shared guard the three calendars failed three different ways: the two arithmetic ones
    let a raw ``TypeError`` out of ``divmod``, which a caller cannot tell from a bug in its own
    code,
    and ``TickCalendar`` returned the component unexamined, so a ``Mapping[str, int]`` handed back a
    ``str`` and the mislabelling travelled downstream.
    """
    for calendar in (TickCalendar(), ProlepticCivilCalendar(), MarsSolCalendar()):
        for component in ("not-a-count", 1.5, None, ("nested",)):
            with pytest.raises(CalendarError):
                calendar.fields((component,))


def test_a_boolean_is_not_a_count_even_though_python_says_it_is_an_int() -> None:
    """``True`` would otherwise render as sol 1, which is a rendering of a value nobody measured."""
    with pytest.raises(CalendarError):
        TickCalendar().fields((True,))


def test_the_tick_calendar_returns_integers_from_a_mapping_of_integers() -> None:
    assert TickCalendar().fields((7,)) == {"tick": 7}
    assert all(isinstance(value, int) for value in TickCalendar().fields((7,)).values())


def test_the_registry_report_names_every_calendar_and_what_it_reads() -> None:
    report = default_registry().report()
    assert set(report) == {"earth-civil", "mars-darian", "tick"}
    assert report["mars-darian"]["scale"] == "MARS_SOL"


# ------------------------------------------------ the renderings nothing had asked these to make


def test_a_civil_position_carrying_a_subsecond_component_renders_it() -> None:
    """The second component is optional, and a decomposition that dropped it would render two
    distinct coordinates identically — which is a rendering that loses the thing it was given."""
    calendar = ProlepticCivilCalendar()
    fields = calendar.fields((0, 250))
    assert fields["subsecond"] == 250
    assert "subsecond" not in calendar.fields((0,))


def test_the_darian_calendar_walks_years_in_both_directions() -> None:
    """The Darian leap rule is not expressible as a single division, so the walk is deliberate.
    A position before the epoch walks backwards, and one well after it walks forwards through
    years and then through months — and a closed form that was subtly wrong here would be far
    harder to notice than a loop that is obviously right."""
    calendar = MarsSolCalendar()
    forward = calendar.fields((calendar.epoch_sol + 5000,))
    assert forward["year"] > 1
    assert 1 <= forward["month"] <= 24
    backward = calendar.fields((-calendar.epoch_sol - 1,))
    assert backward["year"] < 1
    assert 1 <= backward["month"] <= 24


def test_a_calendar_that_identifies_as_nothing_cannot_be_registered() -> None:
    """The registry is keyed by identifier, and a rendering citing "" names no calendar a later
    reader could resolve."""

    class _Anonymous(TickCalendar):
        def identifier(self) -> str:
            return "   "

    with pytest.raises(CalendarError, match="must identify itself"):
        CalendarRegistry().register(_Anonymous())
