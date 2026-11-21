"""Ω∞ temporal — the coordinate, and clocks as providers.

WHAT A COORDINATE HAS TO CARRY, and why a string never could. ``"2026-08-29T04:43:33Z"`` states a
rendering and omits the frame it was observed in, the scale its integers count, the discipline under
which it may be ordered, and the clock that produced it. Every one of those omissions is recoverable
only by assumption, and the assumptions are invisible: comparing two such strings looks like
comparing two times and is actually comparing two renderings under a silently assumed total order.

THE THREE REFUSAL PATHS ARE THE PRODUCT. ``compare`` refuses on unrelated frames, on mismatched
scales and on mismatched orderings BEFORE it looks at a single component, so a comparison that
cannot be justified never reaches the arithmetic that would produce a confident wrong answer.
"""

from __future__ import annotations

import dataclasses

import pytest

from engine.omega_governance.reference.encoding import (
    CanonicalJsonCodec,
    Encoding,
    PolynomialIdentity,
    Sha256Identity,
    default_encoding,
)
from engine.omega_governance.temporal import coordinate as coordinate_module
from engine.omega_governance.temporal.clocks import (
    ClockError,
    ClockRegistry,
    ExternalClock,
    FixedClock,
    LamportClock,
    LogicalClock,
    VectorClock,
    assert_provider,
    positions_of,
)
from engine.omega_governance.temporal.clocks import (
    default_registry as default_clocks,
)
from engine.omega_governance.temporal.coordinate import (
    DOMAIN,
    RULE_FRAME_UNRELATED,
    RULE_ORDERING_MISMATCH,
    RULE_RELATED_FRAME,
    RULE_SAME_FRAME,
    RULE_SCALE_MISMATCH,
    CoordinateError,
    TemporalCoordinate,
    assert_deterministic,
    canonical_sequence,
    compare,
    from_record,
)
from engine.omega_governance.temporal.frames import (
    EARTH_FRAME,
    LOGICAL_FRAME,
    LOGICAL_TICK,
    MARS_FRAME,
    MARS_SOL,
    SI_SECOND,
    SPACECRAFT_FRAME,
    VECTOR_EVENT,
    FrameRelation,
    default_frames,
    default_scales,
)
from engine.omega_governance.temporal.ordering import (
    CAUSAL,
    TOTAL,
)
from engine.omega_governance.temporal.ordering import (
    default_registry as default_orderings,
)


def _tick(position: int, clock: str = "logical") -> TemporalCoordinate:
    return TemporalCoordinate(LOGICAL_FRAME, LOGICAL_TICK, TOTAL, (position,), clock)


# ----------------------------------------------------------------------------- coordinate


def test_a_coordinate_states_its_frame_scale_ordering_position_and_clock() -> None:
    coordinate = _tick(7)
    assert coordinate.frame == LOGICAL_FRAME
    assert coordinate.scale == LOGICAL_TICK
    assert coordinate.ordering == TOTAL
    assert coordinate.position == (7,)
    assert coordinate.clock == "logical"


def test_a_coordinate_must_name_the_clock_that_produced_it() -> None:
    """An unattributed position cannot be re-derived or distrusted, which are the two things an
    audit ever wants to do with one."""
    with pytest.raises(CoordinateError):
        TemporalCoordinate(LOGICAL_FRAME, LOGICAL_TICK, TOTAL, (1,), "   ")


def test_a_coordinate_must_carry_a_position() -> None:
    with pytest.raises(CoordinateError):
        TemporalCoordinate(LOGICAL_FRAME, LOGICAL_TICK, TOTAL, (), "logical")


def test_a_label_enriches_what_a_coordinate_displays_and_never_what_it_is() -> None:
    """``labels`` is ``compare=False``. If it were not, registering a calendar would change every
    stored digest, and a format tweak would invalidate a hash chain."""
    bare = _tick(3)
    labelled = bare.with_label("earth-civil", "1970-01-04")
    assert labelled.labels == {"earth-civil": "1970-01-04"}
    assert labelled == bare
    assert labelled.identity(default_encoding()) == bare.identity(default_encoding())


def test_with_label_does_not_mutate_the_coordinate_it_was_asked_about() -> None:
    bare = _tick(3)
    bare.with_label("tick", "tick 3")
    assert bare.labels == {}


def test_identity_is_taken_under_a_named_encoding_and_differs_between_encodings() -> None:
    coordinate = _tick(3)
    sha = Encoding(CanonicalJsonCodec(), Sha256Identity())
    polynomial = Encoding(CanonicalJsonCodec(), PolynomialIdentity())
    assert coordinate.identity(sha) != coordinate.identity(polynomial)
    assert coordinate.identity(sha) == coordinate.identity(sha)


def test_a_coordinate_is_a_value_in_the_time_domain_like_any_other() -> None:
    value = _tick(1).as_value()
    assert value.domain == DOMAIN == "TIME"


def test_a_coordinate_survives_a_storage_round_trip_through_the_registries() -> None:
    frames, scales, orderings = default_frames(), default_scales(), default_orderings()
    original = _tick(11)
    restored = from_record(original.as_record(), frames=frames, scales=scales, orderings=orderings)
    assert restored == original


def test_rehydrating_an_unknown_frame_name_refuses_rather_than_inventing_a_frame() -> None:
    frames, scales, orderings = default_frames(), default_scales(), default_orderings()
    record = dict(_tick(1).as_record())
    record["frame"] = "JUPITER"
    with pytest.raises((CoordinateError, Exception)):
        from_record(record, frames=frames, scales=scales, orderings=orderings)


def test_assert_deterministic_passes_for_a_well_formed_coordinate() -> None:
    assert_deterministic(
        _tick(5),
        encoding=default_encoding(),
        frames=default_frames(),
        scales=default_scales(),
        orderings=default_orderings(),
    )


def test_two_positions_from_one_counter_compare_within_the_same_frame() -> None:
    frames, orderings = default_frames(), default_orderings()
    outcome = compare(_tick(1), _tick(2), frames=frames, orderings=orderings)
    assert outcome.relation == "BEFORE"
    assert outcome.rule == RULE_SAME_FRAME
    assert outcome.decided and outcome.ordered


def test_the_same_position_twice_is_simultaneous_and_not_merely_unordered() -> None:
    frames, orderings = default_frames(), default_orderings()
    outcome = compare(_tick(4), _tick(4), frames=frames, orderings=orderings)
    assert outcome.relation == "SIMULTANEOUS"
    assert outcome.decided


def test_two_scales_are_two_questions_and_the_scale_check_comes_first() -> None:
    """An Earth second and a Mars sol are not two renderings of one quantity. The scale check runs
    before the frame check because no declared relation between frames could rescue a comparison of
    sols against seconds — that would be a type error dressed as a result."""
    frames, orderings = default_frames(), default_orderings()
    earth = TemporalCoordinate(EARTH_FRAME, SI_SECOND, TOTAL, (100,), "earth-clock")
    mars = TemporalCoordinate(MARS_FRAME, MARS_SOL, TOTAL, (100,), "mars-clock")
    outcome = compare(earth, mars, frames=frames, orderings=orderings)
    assert outcome.relation == "INCOMPARABLE"
    assert outcome.rule == RULE_SCALE_MISMATCH
    assert not outcome.decided


def test_one_scale_in_two_unrelated_frames_is_still_refused() -> None:
    """The check that makes the single-planet assumption impossible to hold by accident. Both sides
    count SI seconds, so nothing about the UNITS refuses — what refuses is that no observer is
    declared to be able to order an event on Earth against one aboard a spacecraft in transit."""
    frames, orderings = default_frames(), default_orderings()
    earth = TemporalCoordinate(EARTH_FRAME, SI_SECOND, TOTAL, (100,), "earth-clock")
    aboard = TemporalCoordinate(SPACECRAFT_FRAME, SI_SECOND, TOTAL, (100,), "vehicle-clock")
    outcome = compare(earth, aboard, frames=frames, orderings=orderings)
    assert outcome.relation == "INCOMPARABLE"
    assert outcome.rule == RULE_FRAME_UNRELATED
    assert not outcome.decided


def test_declaring_the_relation_is_what_makes_two_frames_comparable() -> None:
    """And the comparison then cites the RELATED_FRAME rule rather than the same-frame one, so an
    audit can tell a within-frame answer from one that leaned on a declaration."""
    frames, orderings = default_frames(), default_orderings()
    frames.relate(
        FrameRelation(
            source="EARTH",
            target="SPACECRAFT",
            rule="TEST-REL-03",
            description="A mission's own declared correspondence.",
        )
    )
    earth = TemporalCoordinate(EARTH_FRAME, SI_SECOND, TOTAL, (100,), "earth-clock")
    aboard = TemporalCoordinate(SPACECRAFT_FRAME, SI_SECOND, TOTAL, (200,), "vehicle-clock")
    outcome = compare(earth, aboard, frames=frames, orderings=orderings)
    assert outcome.relation == "BEFORE"
    assert outcome.rule == RULE_RELATED_FRAME


def test_a_declared_frame_relation_is_still_refused_when_the_scales_disagree() -> None:
    """Relating two frames says positions MAY be compared. It does not say seconds are sols, and
    collapsing those two claims is how a mission loses a spacecraft."""
    frames, orderings = default_frames(), default_orderings()
    frames.relate(FrameRelation(source="EARTH", target="MARS", rule="TEST-REL-01"))
    earth = TemporalCoordinate(EARTH_FRAME, SI_SECOND, TOTAL, (100,), "earth-clock")
    mars = TemporalCoordinate(MARS_FRAME, MARS_SOL, TOTAL, (100,), "mars-clock")
    outcome = compare(earth, mars, frames=frames, orderings=orderings)
    assert outcome.relation == "INCOMPARABLE"
    assert outcome.rule == RULE_SCALE_MISMATCH


def test_two_orderings_over_one_scale_refuse_rather_than_pick_one() -> None:
    frames, orderings = default_frames(), default_orderings()
    total = TemporalCoordinate(LOGICAL_FRAME, VECTOR_EVENT, TOTAL, (1, 0), "a")
    causal = TemporalCoordinate(LOGICAL_FRAME, VECTOR_EVENT, CAUSAL, (0, 1), "b")
    outcome = compare(total, causal, frames=frames, orderings=orderings)
    assert outcome.relation == "INCOMPARABLE"
    assert outcome.rule == RULE_ORDERING_MISMATCH


def test_concurrency_is_reported_as_an_answer_when_the_ordering_admits_it() -> None:
    frames, orderings = default_frames(), default_orderings()
    left = TemporalCoordinate(LOGICAL_FRAME, VECTOR_EVENT, CAUSAL, (1, 0), "a")
    right = TemporalCoordinate(LOGICAL_FRAME, VECTOR_EVENT, CAUSAL, (0, 1), "b")
    outcome = compare(left, right, frames=frames, orderings=orderings)
    assert outcome.relation == "CONCURRENT"
    assert outcome.decided, "concurrency is a finding about causality, not missing information"
    assert not outcome.ordered


def test_every_comparison_carries_a_rule_and_a_reason_a_reader_can_check() -> None:
    frames, orderings = default_frames(), default_orderings()
    for outcome in (
        compare(_tick(1), _tick(2), frames=frames, orderings=orderings),
        compare(
            TemporalCoordinate(EARTH_FRAME, SI_SECOND, TOTAL, (1,), "e"),
            TemporalCoordinate(MARS_FRAME, MARS_SOL, TOTAL, (1,), "m"),
            frames=frames,
            orderings=orderings,
        ),
    ):
        assert outcome.rule.startswith("Ω²-C-")
        assert outcome.reason.strip()
        assert outcome.as_record()["rule"] == outcome.rule


def test_canonical_sequence_is_a_serialisation_order_and_is_deterministic() -> None:
    """Explicitly NOT a history: sorting coordinates from unrelated frames yields a stable list and
    no temporal claim whatsoever."""
    coordinates = [_tick(3), _tick(1), _tick(2)]
    once = canonical_sequence(coordinates)
    twice = canonical_sequence(list(reversed(coordinates)))
    assert [c.position for c in once] == [c.position for c in twice]


# --------------------------------------------------------------------------------- clocks


def test_the_logical_clock_advances_and_reports_complete_coordinates() -> None:
    clock = LogicalClock()
    first, second = clock.read(), clock.read()
    assert first.position < second.position
    assert first.frame == LOGICAL_FRAME
    assert first.scale == LOGICAL_TICK
    assert first.clock == clock.identifier()


def test_a_fixed_clock_returns_one_coordinate_forever() -> None:
    """What makes a measurement replayable at a pinned position."""
    pinned = _tick(42, clock="pinned")
    clock = FixedClock(pinned)
    assert clock.read() == clock.read() == pinned


def test_a_lamport_clock_is_raised_past_a_received_position() -> None:
    clock = LamportClock("node-a")
    clock.read()
    clock.observe((50,))
    assert clock.read().position[0] > 50


def test_a_vector_clock_merges_a_received_position_componentwise() -> None:
    clock = VectorClock("node-a", participants=3, index=0)
    clock.read()
    clock.observe((0, 7, 2))
    merged = clock.read().position
    assert merged[1] >= 7
    assert merged[2] >= 2


def test_a_vector_clock_produces_positions_that_can_be_genuinely_concurrent() -> None:
    frames, orderings = default_frames(), default_orderings()
    left = VectorClock("a", participants=2, index=0).read()
    right = VectorClock("b", participants=2, index=1).read()
    assert compare(left, right, frames=frames, orderings=orderings).relation == "CONCURRENT"


def test_an_external_clock_is_the_extension_point_and_needs_no_edit_here() -> None:
    """Ω∞-T2. A deployment's own clock — a GPS receiver, a simulation step counter, a chain head —
    registers by declaring what it is and handing over a reader."""
    readings = iter([(10,), (20,), (30,)])
    clock = ExternalClock(
        clock_identifier="mission-elapsed",
        clock_frame=MARS_FRAME,
        clock_scale=MARS_SOL,
        clock_ordering=TOTAL,
        reader=lambda: next(readings),
    )
    coordinate = clock.read()
    assert coordinate.clock == "mission-elapsed"
    assert coordinate.frame == MARS_FRAME
    assert coordinate.position == (10,)


def test_assert_provider_accepts_the_shipped_clocks() -> None:
    for clock in (LogicalClock(), LamportClock("a"), VectorClock("b", participants=2, index=0)):
        assert_provider(clock)


def test_assert_provider_refuses_a_clock_whose_coordinates_contradict_its_declarations() -> None:
    """Non-vacuity: a clock that declares one frame and stamps another would silently produce
    coordinates that no comparison could justify."""

    class LyingClock:
        def identifier(self) -> str:
            return "liar"

        def frame(self):  # noqa: ANN201 - mirrors the ClockProvider protocol
            return EARTH_FRAME

        def scale(self):  # noqa: ANN201
            return SI_SECOND

        def ordering(self):  # noqa: ANN201
            return TOTAL

        def read(self) -> TemporalCoordinate:
            return _tick(1)

    with pytest.raises(ClockError):
        assert_provider(LyingClock())


def test_positions_of_reads_a_clock_the_requested_number_of_times() -> None:
    assert len(positions_of(LogicalClock(), 4)) == 4


def test_a_registry_refuses_a_duplicate_clock_identifier() -> None:
    registry = ClockRegistry()
    registry.register(LogicalClock("only-one"))
    with pytest.raises(ClockError):
        registry.register(LogicalClock("only-one"))


def test_an_unregistered_clock_identifier_is_refused() -> None:
    with pytest.raises(ClockError):
        default_clocks().resolve("nobody-registered-this")


def test_the_default_clock_registry_ships_a_logical_clock() -> None:
    registry = default_clocks()
    assert "logical" in registry
    assert registry.report()["logical"]["scale"] == "LOGICAL_TICK"


# ------------------------------------------------ rehydration, and the clock contract's refusals


def test_a_label_that_names_no_calendar_is_refused() -> None:
    """A rendering nobody can attribute to a calendar is a string, and reading it as a temporal
    fact would credit this package with a civil claim it never made."""
    coordinate = TemporalCoordinate(LOGICAL_FRAME, LOGICAL_TICK, TOTAL, (0,), "logical")
    with pytest.raises(CoordinateError, match="must name the calendar"):
        coordinate.with_label("   ", "some rendering")


@pytest.mark.parametrize(
    ("mutate", "message"),
    [
        (lambda record: record.pop("frame"), "missing the required field 'frame'"),
        (lambda record: record.__setitem__("position", "not a sequence"), "not a sequence"),
        (lambda record: record.__setitem__("labels", "not a mapping"), "labels that are not"),
    ],
    ids=["missing-field", "position-not-a-sequence", "labels-not-a-mapping"],
)
def test_a_stored_coordinate_this_reader_cannot_rehydrate_is_refused(mutate, message) -> None:
    """A partial coordinate would be rehydrated with an assumed frame, scale or ordering, which
    is the assumption this type exists to make impossible."""
    record = dict(
        TemporalCoordinate(LOGICAL_FRAME, LOGICAL_TICK, TOTAL, (0,), "logical").as_record()
    )
    mutate(record)
    with pytest.raises(CoordinateError, match=message):
        from_record(
            record,
            frames=default_frames(),
            scales=default_scales(),
            orderings=default_orderings(),
        )


def test_a_coordinate_that_does_not_survive_a_round_trip_is_refused(monkeypatch) -> None:
    """A register whose records change on read cannot be audited, so the round trip is performed
    rather than argued — and the guard has to be shown to fire, or performing it proves nothing."""
    coordinate = TemporalCoordinate(LOGICAL_FRAME, LOGICAL_TICK, TOTAL, (0,), "logical")

    monkeypatch.setattr(
        coordinate_module,
        "from_record",
        lambda record, **kwargs: TemporalCoordinate(
            LOGICAL_FRAME, LOGICAL_TICK, TOTAL, (99,), "logical"
        ),
    )
    with pytest.raises(CoordinateError, match="did not survive a storage round trip"):
        assert_deterministic(
            coordinate,
            encoding=default_encoding(),
            frames=default_frames(),
            scales=default_scales(),
            orderings=default_orderings(),
        )


def test_a_clock_that_identifies_as_nothing_cannot_be_registered() -> None:
    """Replacing a registered clock silently would change the frame every subsequent record is
    stamped in, so the registry is keyed by identifier — and "" is not one."""

    class _Anonymous(LogicalClock):
        def identifier(self) -> str:
            return "   "

    with pytest.raises(ClockError, match="must identify itself"):
        ClockRegistry().register(_Anonymous())


@pytest.mark.parametrize(
    ("attribute", "message"),
    [
        ("frame", "declares frame"),
        ("scale", "declares scale"),
        ("ordering", "declares ordering"),
    ],
)
def test_a_clock_whose_readings_contradict_its_own_declaration_is_refused(
    attribute, message
) -> None:
    """A mislabelled unit makes every comparison it joins arithmetically wrong while appearing
    well formed, which is why the contract is checked against readings rather than trusted."""
    truthful = LogicalClock("probe")
    reading = truthful.read()
    replacements = {
        "frame": {"frame": EARTH_FRAME},
        "scale": {"scale": SI_SECOND},
        "ordering": {"ordering": CAUSAL},
    }

    class _Contradicting(LogicalClock):
        def read(self) -> TemporalCoordinate:
            return dataclasses.replace(reading, **replacements[attribute])  # noqa: ANN201

    with pytest.raises(ClockError, match=message):
        assert_provider(_Contradicting("probe"), readings=1)


def test_the_clock_factory_admits_a_clock_this_package_did_not_ship() -> None:
    """Fresh rather than shared: constructing the logical clock in the factory is what keeps one
    measurement's positions independent of another's."""
    extra = LamportClock("federated")
    registry = default_clocks((extra,))
    assert registry.resolve("federated") is extra
