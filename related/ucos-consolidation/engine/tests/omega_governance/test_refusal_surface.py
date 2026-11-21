"""Ω∞ governance — the refusal surface, and the rendering surface, exercised directly.

WHY THESE ARE WORTH A MODULE OF THEIR OWN. Every registry in this package is "open for extension,
closed to redefinition", and that sentence is carried entirely by branches a happy-path suite never
enters: the empty name, the conflicting redeclaration, the malformed position, the container
protocol that decides whether ``in`` means anything. A guard nothing exercises is a guard nobody
knows is wired up, and it will be quietly deleted by the first refactor that finds it inconvenient.

``__str__`` and ``report()`` are here for a related reason rather than for the coverage figure: a
registry's report is what an operator reads when a gate refuses, so a report that raises is a
refusal an operator cannot act on.
"""

from __future__ import annotations

import pytest

from engine.omega_governance.reference.capability import ORDERABLE, CapabilityRegistry
from engine.omega_governance.reference.domain import (
    DomainError,
    Field,
    Invariant,
    Provenance,
    Schema,
    Value,
    default_domains,
)
from engine.omega_governance.reference.encoding import (
    CanonicalJsonCodec,
    CodecRegistry,
    IdentityRegistry,
    PolynomialIdentity,
    Sha256Identity,
    TagLengthValueCodec,
    default_encoding,
)
from engine.omega_governance.reference.transformation import (
    Transformation,
    TransformationRegistry,
)
from engine.omega_governance.state import (
    DISCOVERED,
    UNKNOWN,
    Axis,
    GovernanceState,
    StateError,
    default_graph,
    default_states,
)
from engine.omega_governance.temporal.calendars import (
    CalendarError,
    MarsSolCalendar,
    ProlepticCivilCalendar,
    TickCalendar,
    counter,
)
from engine.omega_governance.temporal.calendars import (
    default_registry as default_calendars,
)
from engine.omega_governance.temporal.clocks import (
    ClockError,
    ClockRegistry,
    ExternalClock,
    FixedClock,
    LamportClock,
    LogicalClock,
    VectorClock,
    assert_provider,
)
from engine.omega_governance.temporal.coordinate import TemporalCoordinate
from engine.omega_governance.temporal.frames import (
    EARTH_FRAME,
    LOGICAL_FRAME,
    LOGICAL_TICK,
    MARS_SOL,
    SI_SECOND,
    FrameRegistry,
    ReferenceError,
    ReferenceFrame,
    ScaleRegistry,
    TimeScale,
    default_frames,
    default_scales,
)
from engine.omega_governance.temporal.ordering import (
    BEFORE,
    CAUSAL,
    TOTAL,
    BranchingStrategy,
    CausalStrategy,
    ConsensusStrategy,
    LexicographicStrategy,
    Ordering,
    OrderingError,
    OrderingRegistry,
    Relation,
    RelationRegistry,
)
from engine.omega_governance.temporal.ordering import (
    default_registry as default_orderings,
)


def _tick(position: int = 0) -> TemporalCoordinate:
    return TemporalCoordinate(LOGICAL_FRAME, LOGICAL_TICK, TOTAL, (position,), "logical")


# ------------------------------------------------------------------- the container protocol


def test_every_registry_answers_in_and_len_over_its_own_vocabulary() -> None:
    """``in`` must be keyed on the identifier and must not be fooled by a non-string, or a lookup
    with a stray object would report membership the resolver would then refuse."""
    checks = (
        (CapabilityRegistry(), "ORDERABLE"),
        (default_frames(), "EARTH"),
        (default_scales(), "SI_SECOND"),
        (RelationRegistry(), "BEFORE"),
        (default_orderings(), "TOTAL"),
        (default_states(), "UNKNOWN"),
        (default_calendars(), "tick"),
        (default_domains(), "TIME"),
    )
    for registry, present in checks:
        assert present in registry
        assert "definitely-not-registered" not in registry
        assert object() not in registry
        assert len(registry) > 0


def test_a_clock_registry_answers_in_and_len_and_lists_what_it_holds() -> None:
    registry = ClockRegistry()
    assert len(registry) == 0
    assert "logical" not in registry
    registry.register(LogicalClock("logical"))
    assert "logical" in registry
    assert object() not in registry
    assert registry.known() == ("logical",)
    assert len(registry) == 1


def test_a_transformation_registry_answers_in_and_len() -> None:
    registry = TransformationRegistry()
    assert len(registry) == 0
    registry.declare("T-1", "A", "B", "X")
    assert "T-1" in registry
    assert "T-2" not in registry
    assert len(registry) == 1


# --------------------------------------------------------------------- the rendering surface


def test_the_vocabulary_values_render_to_their_own_names() -> None:
    """A governance value that rendered as ``<object at 0x…>`` in a refusal message would make the
    message useless exactly when somebody needs it."""
    assert str(BEFORE) == "BEFORE"
    assert str(TOTAL) == "TOTAL"
    assert str(EARTH_FRAME) == "EARTH"
    assert str(SI_SECOND) == "SI_SECOND"
    assert str(ORDERABLE) == "ORDERABLE"
    assert str(UNKNOWN) == "UNKNOWN"
    assert str(Axis("CUSTODY_TEST", "A test concern.")) == "CUSTODY_TEST"
    assert "LOGICAL" in str(_tick(1))


def test_a_domain_and_a_value_render_readably() -> None:
    registry = default_domains()
    assert "TIME" in str(registry.resolve("TIME"))
    assert "TIME" in str(Value(domain="TIME", components=(1,)))


def test_every_registry_report_is_a_document_an_operator_can_read() -> None:
    for report in (
        default_orderings().report(),
        default_calendars().report(),
        ClockRegistry([LogicalClock()]).report(),
        default_domains().report(),
        TransformationRegistry().report(),
    ):
        assert isinstance(report, dict)


def test_the_relation_and_ordering_records_carry_their_declared_semantics() -> None:
    record = BEFORE.as_record()
    assert record["relation"] == "BEFORE"
    assert record["ordered"] is True
    assert record["inverse"] == "AFTER"


def test_a_frame_relation_renders_to_a_record() -> None:
    from engine.omega_governance.temporal.frames import FrameRelation

    record = FrameRelation(source="EARTH", target="MARS", rule="TEST-REL-01").as_record()
    assert record["source"] == "EARTH"
    assert record["rule"] == "TEST-REL-01"


def test_a_schema_field_invariant_and_provenance_render_to_records() -> None:
    assert Field("name", "OPAQUE_STRING").as_record()["kind"] == "OPAQUE_STRING"
    assert Schema("s", (Field("name", "OPAQUE_STRING"),)).as_record()["schema"] == "s"
    assert Invariant("I-1", "A statement.").as_record()["invariant"] == "I-1"
    assert Invariant("I-1", "A statement.").as_record()["executable"] is False
    assert Provenance(declared_by="a", rule="R").as_record()["declared_by"] == "a"


def test_a_transformation_renders_to_a_record() -> None:
    record = Transformation(identifier="T", source="A", target="B", authority="X").as_record()
    assert record["transformation"] == "T"


# ------------------------------------------------------------------------ empty-name refusals


def test_nothing_in_the_vocabulary_may_be_anonymous() -> None:
    """A nameless entry cannot be cited by a refusal, reported in a census, or resolved by anybody,
    so it is refused at construction rather than discovered later as a blank in a report."""
    with pytest.raises(OrderingError):
        Relation("   ")
    with pytest.raises(OrderingError):
        Ordering("   ")
    with pytest.raises(ReferenceError):
        ReferenceFrame("  ")
    with pytest.raises(ReferenceError):
        TimeScale("  ", "s", "d", TOTAL)
    with pytest.raises(StateError):
        GovernanceState("  ", Axis("A", "d"))


def test_a_clock_with_no_identifier_is_refused_at_every_shipped_implementation() -> None:
    """Every coordinate cites its clock, so an anonymous clock produces positions nothing can
    attribute — the temporal equivalent of an unowned artifact."""
    with pytest.raises(ClockError):
        LogicalClock("   ")
    with pytest.raises(ClockError):
        LamportClock("  ")
    with pytest.raises(ClockError):
        VectorClock("  ", participants=2, index=0)
    with pytest.raises(ClockError):
        ExternalClock(
            clock_identifier="   ",
            clock_frame=LOGICAL_FRAME,
            clock_scale=LOGICAL_TICK,
            clock_ordering=TOTAL,
            reader=lambda: (1,),
        )


def test_a_vector_clock_refuses_a_participant_set_it_cannot_index_into() -> None:
    with pytest.raises(ClockError):
        VectorClock("a", participants=0, index=0)
    with pytest.raises(ClockError):
        VectorClock("a", participants=2, index=5)


def test_a_lamport_clock_refuses_an_empty_observed_position() -> None:
    clock = LamportClock("a")
    with pytest.raises(ClockError):
        clock.observe(())


def test_a_vector_clock_refuses_an_observed_position_of_the_wrong_arity() -> None:
    clock = VectorClock("a", participants=3, index=0)
    with pytest.raises(ClockError):
        clock.observe((1, 2))


# ---------------------------------------------------------------------- redeclaration refusals


def test_a_conflicting_redeclaration_is_refused_across_every_registry() -> None:
    with pytest.raises(OrderingError):
        RelationRegistry().declare(Relation("BEFORE", "a rival meaning"))
    with pytest.raises(ReferenceError):
        default_scales().declare(TimeScale("SI_SECOND", "s", "a rival meaning", CAUSAL))
    with pytest.raises(DomainError):
        default_domains().declare_domain("TIME", "A-RIVAL", Schema("rival"))


def test_an_identical_redeclaration_is_a_no_op_across_every_registry() -> None:
    """Two modules seeding the same vocabulary must not fight. Idempotence is what lets a registry
    be assembled from several independent declarations."""
    relations = RelationRegistry()
    before = len(relations)
    relations.declare(BEFORE)
    assert len(relations) == before

    scales = default_scales()
    count = len(scales)
    scales.declare(SI_SECOND)
    assert len(scales) == count


def test_registering_a_duplicate_codec_or_identity_provider_is_refused() -> None:
    from engine.omega_governance.reference.encoding import EncodingError

    codecs = CodecRegistry([CanonicalJsonCodec()])
    with pytest.raises(EncodingError):
        codecs.register(CanonicalJsonCodec())

    identities = IdentityRegistry([Sha256Identity()])
    with pytest.raises(EncodingError):
        identities.register(Sha256Identity())


# --------------------------------------------------------------------- comparison edge cases


def test_a_strategy_needing_a_structured_position_refuses_an_empty_one() -> None:
    """``BranchingStrategy`` and ``ConsensusStrategy`` read a component by POSITION — a branch
    identity, an observer — so an empty position is one they cannot interpret rather than one they
    can interpret as equal."""
    assert BranchingStrategy().compare((), ()) == "INCOMPARABLE"
    assert ConsensusStrategy(agreeing=frozenset({"a"})).compare((), ()) == "INCOMPARABLE"


def test_a_componentwise_strategy_calls_two_empty_positions_simultaneous_and_that_is_correct() -> (
    None
):
    """Componentwise comparison of two empty sequences IS equality, and the coordinate layer is what
    stops an empty position from ever arising: ``TemporalCoordinate`` refuses one at
    construction, so
    this branch is reachable only by using a strategy directly on raw tuples.

    Recorded rather than 'fixed', because forcing INCOMPARABLE here would make these two strategies
    disagree with their own declared discipline for no case that a coordinate can produce.
    """
    assert LexicographicStrategy().compare((), ()) == "SIMULTANEOUS"
    assert CausalStrategy().compare((), ()) == "SIMULTANEOUS"

    # And the guard that makes it moot, asserted here so the two facts stay together.
    from engine.omega_governance.temporal.coordinate import CoordinateError

    with pytest.raises(CoordinateError):
        TemporalCoordinate(LOGICAL_FRAME, LOGICAL_TICK, TOTAL, (), "logical")


def test_branching_refuses_a_position_too_short_to_carry_its_branch_identity() -> None:
    assert BranchingStrategy().compare(("main",), ("main", 1)) == "INCOMPARABLE"


def test_branching_reports_simultaneity_within_one_branch() -> None:
    assert BranchingStrategy().compare(("main", 1), ("main", 1)) == "SIMULTANEOUS"


def test_consensus_reports_simultaneity_between_two_agreeing_observers() -> None:
    strategy = ConsensusStrategy(agreeing=frozenset({"a", "b"}))
    assert strategy.compare(("a", 1), ("b", 1)) == "SIMULTANEOUS"
    assert strategy.compare(("b", 2), ("a", 1)) == "AFTER"


def test_a_branching_strategy_must_carry_at_least_one_branch_field() -> None:
    with pytest.raises(OrderingError):
        BranchingStrategy(branch_fields=0)


def test_resolving_an_ordering_nobody_implemented_is_refused() -> None:
    with pytest.raises(OrderingError):
        OrderingRegistry().resolve("TOTAL")


def test_the_declared_ordering_vocabulary_is_readable_without_a_strategy() -> None:
    registry = OrderingRegistry()
    registry.declare(TOTAL)
    assert TOTAL in registry.declared()
    assert registry.ordering("TOTAL") == TOTAL


# ------------------------------------------------------------------------------- providers


def test_a_fixed_clock_reports_the_declarations_of_the_coordinate_it_holds() -> None:
    """A fixed clock has no declarations of its own; it must read them off its coordinate, or a
    replayed measurement would disagree with the position it replayed."""
    pinned = _tick(11)
    clock = FixedClock(pinned)
    assert clock.identifier() == pinned.clock
    assert clock.frame() == pinned.frame
    assert clock.scale() == pinned.scale
    assert clock.ordering() == pinned.ordering
    assert_provider(clock)


def test_assert_provider_refuses_a_clock_that_cannot_be_read_at_all() -> None:
    with pytest.raises(ClockError):
        assert_provider(LogicalClock(), readings=0)


def test_an_external_clock_reports_exactly_what_it_was_declared_with() -> None:
    clock = ExternalClock(
        clock_identifier="chain-head",
        clock_frame=EARTH_FRAME,
        clock_scale=SI_SECOND,
        clock_ordering=TOTAL,
        reader=lambda: (7,),
    )
    assert clock.identifier() == "chain-head"
    assert clock.frame() == EARTH_FRAME
    assert clock.scale() == SI_SECOND
    assert clock.ordering() == TOTAL
    assert clock.read().position == (7,)


# ------------------------------------------------------------------------------- calendars


def test_the_shared_counter_guard_names_the_calendar_that_refused() -> None:
    with pytest.raises(CalendarError) as refusal:
        counter((), "tick")
    assert "tick" in str(refusal.value)

    with pytest.raises(CalendarError) as wrong_type:
        counter(("x",), "civil")
    assert "civil" in str(wrong_type.value)


def test_every_shipped_calendar_refuses_an_unreadable_position_from_label_too() -> None:
    """``label`` and ``fields`` must agree about what is readable, or a coordinate would render a
    label it cannot decompose."""
    for calendar in (TickCalendar(), ProlepticCivilCalendar(), MarsSolCalendar()):
        with pytest.raises(CalendarError):
            calendar.label(())


def test_a_calendar_registry_lists_and_resolves_what_it_holds() -> None:
    registry = default_calendars()
    assert registry.resolve("tick").identifier() == "tick"
    assert len(registry) == 3


# ---------------------------------------------------------------------------------- states


def test_the_graph_reports_the_edges_on_one_axis_and_the_ones_it_does_not_hold() -> None:
    graph = default_graph()
    assert graph.on_axis(UNKNOWN.axis)
    assert graph.edge(DISCOVERED, UNKNOWN) is None, "an undeclared edge must be an absence"
    assert graph.rule("Ω²-S-01") is not None
    assert len(graph) > 0
    assert graph.known()


def test_citing_a_transition_rule_the_graph_does_not_declare_is_refused() -> None:
    """An audit record naming an undeclared rule would describe a transition this graph cannot
    perform, so the lookup refuses rather than returning nothing for the caller to misread."""
    with pytest.raises(StateError):
        default_graph().rule("NOT-A-DECLARED-RULE")


def test_a_state_registry_lists_the_states_on_one_axis() -> None:
    registry = default_states()
    custody = registry.on_axis(UNKNOWN.axis)
    assert UNKNOWN in custody
    assert DISCOVERED in custody


def test_asking_for_the_initial_state_of_an_axis_nobody_declared_is_refused() -> None:
    with pytest.raises(StateError):
        default_states().initial(Axis("NEVER_DECLARED", "A concern nobody registered."))


# --------------------------------------------------------------------------------- encoding


def test_the_tag_length_value_codec_round_trips_every_shape_the_json_codec_accepts() -> None:
    """The second codec has to cover the same value space, or "representation is a slot" would mean
    "representation is a slot as long as you pick JSON"."""
    codec = TagLengthValueCodec()
    for value in ({"a": 1}, [1, 2], "text", 7, True, None, {"nested": {"deep": [1]}}):
        assert codec.supports(value)
        assert isinstance(codec.encode(value), bytes)


def test_two_different_values_do_not_share_a_fingerprint_under_either_identity_provider() -> None:
    for identity in (Sha256Identity(), PolynomialIdentity()):
        assert identity.fingerprint(b"a") != identity.fingerprint(b"b")


def test_the_default_encoding_describes_the_pair_it_actually_holds() -> None:
    encoding = default_encoding()
    assert encoding.encode({"a": 1}) == CanonicalJsonCodec().encode({"a": 1})


# ----------------------------------------------------------------------------------- frames


def test_an_unresolvable_relation_endpoint_is_refused_when_it_is_declared() -> None:
    """A relation naming a frame nobody registered would be a declaration nothing could apply."""
    from engine.omega_governance.temporal.frames import FrameRelation

    registry = FrameRegistry(seed=())
    with pytest.raises(ReferenceError):
        registry.relate(FrameRelation(source="EARTH", target="MARS", rule="TEST-REL-01"))


def test_a_relation_must_name_a_rule() -> None:
    from engine.omega_governance.temporal.frames import FrameRelation

    with pytest.raises(ReferenceError):
        FrameRelation(source="EARTH", target="MARS", rule="   ")


def test_an_empty_scale_registry_holds_nothing() -> None:
    empty = ScaleRegistry(seed=())
    assert len(empty) == 0
    assert empty.known() == ()
    with pytest.raises(ReferenceError):
        empty.resolve("SI_SECOND")


def test_the_mars_scale_and_the_second_are_not_interchangeable() -> None:
    assert MARS_SOL != SI_SECOND
    assert MARS_SOL.unit != SI_SECOND.unit
