"""Ω∞ temporal — reference frames, time scales, and ordering as a declared discipline.

THE TWO ASSUMPTIONS UNDER TEST, and both were invisible as annotations rather than as decisions.

``default_ordering = TOTAL`` said that every pair of positions is comparable and exactly one of
precedence holds. That is true of one counter read by one observer and false of every distributed,
branching or relativistic system, and the falsehood surfaces as a WRONG ANSWER rather than as an
error — two concurrent events get an order, and the order is stable, and nothing anywhere reports
that it was invented.

A registry seeded with relations between frames would say that an Earth timestamp and a Mars sol are
comparable. ``default_frames()`` therefore ships SEVEN frames and ZERO relations: comparability
across frames is something a deployment must declare, by name and by authority.
"""

from __future__ import annotations

import pytest

from engine.omega_governance.temporal.frames import (
    EARTH_FRAME,
    INITIAL_FRAMES,
    INITIAL_SCALES,
    LOGICAL_TICK,
    MARS_FRAME,
    MARS_SOL,
    VECTOR_EVENT,
    FrameRegistry,
    FrameRelation,
    ReferenceError,
    ReferenceFrame,
    ScaleRegistry,
    TimeScale,
    default_frames,
    default_scales,
)
from engine.omega_governance.temporal.ordering import (
    AFTER,
    BEFORE,
    BRANCHING,
    CAUSAL,
    CONCURRENT,
    INCOMPARABLE,
    PARTIAL,
    SIMULTANEOUS,
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
    assert_consistent,
    default_registry,
)

# --------------------------------------------------------------------------------- frames


def test_the_shipped_registry_declares_seven_frames_and_no_relations_between_them() -> None:
    """The absence is the deliverable. A seeded relation would assert that two frames are
    comparable, which is a physical claim this package has no standing to make."""
    registry = default_frames()
    assert len(registry) == len(INITIAL_FRAMES) == 7
    assert registry.relations() == ()


def test_earth_holds_no_privilege_over_mars_or_over_the_logical_frame() -> None:
    registry = default_frames()
    for name in ("EARTH", "MARS", "LOGICAL", "SIMULATION"):
        assert type(registry.resolve(name)) is ReferenceFrame


def test_a_frame_must_be_named() -> None:
    with pytest.raises(ReferenceError):
        ReferenceFrame("   ")


def test_an_unknown_frame_or_scale_name_is_refused() -> None:
    with pytest.raises(ReferenceError):
        default_frames().resolve("JUPITER")
    with pytest.raises(ReferenceError):
        default_scales().resolve("FURLONGS_PER_FORTNIGHT")


def test_a_frame_is_always_comparable_with_itself_and_needs_no_declaration() -> None:
    registry = default_frames()
    identity = registry.comparable(EARTH_FRAME, EARTH_FRAME)
    assert identity is not None


def test_two_frames_are_not_comparable_until_somebody_declares_the_relation() -> None:
    """The refusal that makes a Mars sol and an Earth second two different questions."""
    registry = default_frames()
    assert registry.comparable(EARTH_FRAME, MARS_FRAME) is None

    registry.relate(
        FrameRelation(
            source="EARTH",
            target="MARS",
            rule="TEST-REL-01",
            description="A declared correspondence, supplied by a mission's own ephemeris.",
        )
    )
    assert registry.comparable(EARTH_FRAME, MARS_FRAME) is not None


def test_a_symmetric_relation_is_comparable_in_both_directions() -> None:
    registry = default_frames()
    registry.relate(
        FrameRelation(source="EARTH", target="MARS", rule="TEST-REL-01", symmetric=True)
    )
    assert registry.comparable(EARTH_FRAME, MARS_FRAME) is not None
    assert registry.comparable(MARS_FRAME, EARTH_FRAME) is not None


def test_an_asymmetric_relation_is_comparable_in_one_direction_only() -> None:
    registry = default_frames()
    registry.relate(
        FrameRelation(source="EARTH", target="MARS", rule="TEST-REL-02", symmetric=False)
    )
    assert registry.comparable(EARTH_FRAME, MARS_FRAME) is not None
    assert registry.comparable(MARS_FRAME, EARTH_FRAME) is None


def test_a_frame_can_be_declared_from_primitives_with_no_edit_to_the_module() -> None:
    """Deliverable Ω∞-T3 in one call. An eighth frame nobody imagined is a registration."""
    registry = default_frames()
    declared = registry.declare_name(
        "EUROPA", "An observer on the Europan ice shell.", anchor="EUROPA", physical=True
    )
    assert registry.resolve("EUROPA") == declared
    assert len(registry) == 8


def test_redeclaring_a_frame_with_a_different_meaning_is_refused() -> None:
    registry = default_frames()
    with pytest.raises(ReferenceError):
        registry.declare(ReferenceFrame("EARTH", "somewhere else entirely", anchor="NOT-EARTH"))


def test_the_shipped_scales_include_non_numeric_and_vector_shapes() -> None:
    """A scale set of seconds-since-an-epoch would make every non-terrestrial system unrepresentable
    while looking complete."""
    registry = default_scales()
    assert len(registry) == len(INITIAL_SCALES) == 10
    assert VECTOR_EVENT.vector
    assert not LOGICAL_TICK.vector
    assert MARS_SOL.unit == "sol"


def test_a_scale_declares_the_ordering_discipline_its_positions_obey() -> None:
    assert LOGICAL_TICK.ordering == TOTAL
    assert VECTOR_EVENT.ordering == CAUSAL


def test_a_scale_must_be_named() -> None:
    with pytest.raises(ReferenceError):
        TimeScale("   ", "s", "description", TOTAL)


def test_a_scale_can_be_declared_from_primitives() -> None:
    registry = ScaleRegistry(seed=())
    registry.declare_name("HEARTBEAT", "beat", "Beats of a declared oscillator.", TOTAL)
    assert "HEARTBEAT" in registry
    assert len(registry) == 1


def test_an_empty_frame_registry_holds_nothing_and_says_so() -> None:
    empty = FrameRegistry(seed=())
    assert len(empty) == 0
    assert empty.known() == ()
    assert "EARTH" not in empty


# ------------------------------------------------------------------------------- ordering


def test_the_five_shipped_relations_carry_their_own_semantics() -> None:
    """``CONCURRENT`` and ``INCOMPARABLE`` are the two the vocabulary existed to separate: one is an
    answer about causality, the other is a refusal to answer."""
    assert BEFORE.decided and BEFORE.ordered
    assert SIMULTANEOUS.decided and SIMULTANEOUS.coincident and not SIMULTANEOUS.ordered
    assert CONCURRENT.decided and not CONCURRENT.ordered
    assert not INCOMPARABLE.decided


def test_only_the_ordered_and_coincident_relations_admit_a_claim_of_totality() -> None:
    assert BEFORE.admits_total_order
    assert AFTER.admits_total_order
    assert SIMULTANEOUS.admits_total_order
    assert not CONCURRENT.admits_total_order
    assert not INCOMPARABLE.admits_total_order


def test_the_inverse_of_a_relation_is_read_from_the_declaration_not_a_hardcoded_table() -> None:
    registry = RelationRegistry()
    assert registry.inverse_of("BEFORE") == AFTER
    assert registry.inverse_of("AFTER") == BEFORE
    assert registry.inverse_of("SIMULTANEOUS") == SIMULTANEOUS
    assert registry.inverse_of("CONCURRENT") == CONCURRENT


def test_a_sixth_relation_can_be_declared_with_no_edit_to_the_module() -> None:
    registry = RelationRegistry()
    registry.declare_name(
        "OVERLAPPING",
        "The two intervals share at least one instant.",
        decided=True,
        ordered=False,
        inverse="OVERLAPPING",
    )
    assert registry.resolve("OVERLAPPING").decided
    assert registry.inverse_of("OVERLAPPING").name == "OVERLAPPING"


def test_an_unknown_relation_is_refused_rather_than_invented() -> None:
    with pytest.raises(OrderingError):
        RelationRegistry().resolve("SORT_OF_BEFORE")


def test_only_total_declares_itself_total() -> None:
    assert TOTAL.total
    for ordering in (PARTIAL, CAUSAL, BRANCHING):
        assert not ordering.total


def test_lexicographic_orders_a_single_counter_and_reports_simultaneity() -> None:
    strategy = LexicographicStrategy()
    assert strategy.ordering() == TOTAL
    assert strategy.compare((1,), (2,)) == "BEFORE"
    assert strategy.compare((2,), (1,)) == "AFTER"
    assert strategy.compare((1,), (1,)) == "SIMULTANEOUS"


def test_lexicographic_refuses_positions_whose_components_cannot_be_compared() -> None:
    """The honest answer for ``(1,) vs ("a",)``. A total order over mutually incomparable components
    is exactly the invented answer this vocabulary exists to prevent."""
    assert LexicographicStrategy().compare((1,), ("a",)) == "INCOMPARABLE"


def test_causal_reports_genuine_concurrency_rather_than_inventing_an_order() -> None:
    """The property TOTAL could not express. Neither vector dominates, and that is an ANSWER."""
    strategy = CausalStrategy()
    assert strategy.ordering() == CAUSAL
    assert strategy.compare((1, 0), (1, 1)) == "BEFORE"
    assert strategy.compare((1, 1), (1, 0)) == "AFTER"
    assert strategy.compare((1, 1), (1, 1)) == "SIMULTANEOUS"
    assert strategy.compare((1, 0), (0, 1)) == "CONCURRENT"


def test_causal_refuses_vectors_of_different_arity() -> None:
    assert CausalStrategy().compare((1, 0), (1, 0, 0)) == "INCOMPARABLE"


def test_branching_positions_are_comparable_only_within_one_branch() -> None:
    """Two histories, not two views of one history — so the answer is INCOMPARABLE and never
    CONCURRENT, and the distinction is the whole reason BRANCHING is its own discipline."""
    strategy = BranchingStrategy()
    assert strategy.ordering() == BRANCHING
    assert strategy.compare(("main", 1), ("main", 2)) == "BEFORE"
    assert strategy.compare(("main", 1), ("fork", 2)) == "INCOMPARABLE"


def test_consensus_positions_are_comparable_only_between_agreeing_observers() -> None:
    strategy = ConsensusStrategy(agreeing=frozenset({"a", "b"}))
    assert strategy.compare(("a", 1), ("b", 2)) == "BEFORE"
    assert strategy.compare(("a", 1), ("c", 2)) == "INCOMPARABLE"


def test_the_shipped_registry_holds_four_strategies_and_five_declared_orderings() -> None:
    registry = default_registry()
    assert registry.known() == ("BRANCHING", "CAUSAL", "DISTRIBUTED", "TOTAL")
    assert len(registry.declared()) == 5


def test_partial_is_declared_as_a_vocabulary_word_with_no_strategy_bound_to_it() -> None:
    """A declared discipline nothing implements is a NAMED gap. Silently omitting PARTIAL from the
    vocabulary would have made the same gap unreportable."""
    registry = default_registry()
    assert "PARTIAL" in {ordering.name for ordering in registry.declared()}
    assert "PARTIAL" not in registry.known()
    with pytest.raises(OrderingError):
        registry.resolve("PARTIAL")


def test_a_strategy_can_be_registered_at_runtime() -> None:
    registry = OrderingRegistry()
    registry.register(LexicographicStrategy())
    assert registry.resolve("TOTAL").compare((1,), (2,)) == "BEFORE"


def test_re_registering_the_same_strategy_is_idempotent() -> None:
    """Two modules seeding the same discipline must not fight, so an identical registration is a
    no-op rather than an error."""
    registry = default_registry()
    registry.register(LexicographicStrategy())
    assert registry.known() == ("BRANCHING", "CAUSAL", "DISTRIBUTED", "TOTAL")


def test_a_second_comparison_behaviour_under_one_ordering_name_is_refused() -> None:
    """One name with two behaviours makes every claim about event order unenforceable — a caller
    asking for TOTAL would get whichever strategy registered last."""

    class RivalTotal:
        def ordering(self) -> Ordering:
            return TOTAL

        def compare(self, left: tuple[object, ...], right: tuple[object, ...]) -> str:
            return "SIMULTANEOUS"

    registry = default_registry()
    with pytest.raises(OrderingError):
        registry.register(RivalTotal())


def test_assert_consistent_accepts_a_strategy_whose_behaviour_matches_its_claim() -> None:
    relations = RelationRegistry()
    assert_consistent(LexicographicStrategy(), [(1,), (2,), (3,)], relations)
    assert_consistent(CausalStrategy(), [(1, 0), (0, 1), (1, 1)], relations)


def test_assert_consistent_refuses_a_strategy_that_claims_totality_and_returns_concurrency() -> (
    None
):
    """Non-vacuity. This is the exact defect ``default_ordering = TOTAL`` produced, caught by
    measuring the strategy's behaviour against its own declaration."""

    class LyingStrategy:
        def ordering(self) -> Ordering:
            return TOTAL

        def compare(self, left: tuple[object, ...], right: tuple[object, ...]) -> str:
            return "CONCURRENT"

    with pytest.raises(OrderingError):
        assert_consistent(LyingStrategy(), [(1,), (2,)], RelationRegistry())


def test_a_relation_naming_an_inverse_nobody_declared_is_refused() -> None:
    registry = RelationRegistry()
    registry.declare(Relation("ODD", "An outcome.", inverse="NEVER_DECLARED"))
    with pytest.raises(OrderingError):
        registry.inverse_of("ODD")


# ------------------------------------------- the relations, the strategies and their refusals


def test_a_relation_claiming_both_precedence_and_coincidence_is_refused() -> None:
    """A position cannot both come before another and be the same position, and a relation
    asserting it would make every comparison citing it uninterpretable."""
    with pytest.raises(OrderingError, match="both precedence and coincidence"):
        Relation(name="BOTH", ordered=True, coincident=True, inverse="BOTH")


def test_a_precedence_relation_with_no_inverse_is_refused() -> None:
    """Without an inverse, swapping the arguments has no defined answer and antisymmetry is
    uncheckable — so the strategy could report a and b as both before each other."""
    with pytest.raises(OrderingError, match="declares no inverse"):
        Relation(name="EARLIER", ordered=True, inverse="   ")


@pytest.mark.parametrize(
    "strategy",
    [LexicographicStrategy(), CausalStrategy(), BranchingStrategy(), ConsensusStrategy()],
    ids=["lexicographic", "causal", "branching", "consensus"],
)
def test_positions_of_different_length_are_incomparable_under_every_strategy(strategy) -> None:
    """Two positions of different arity are not two points in one space. Padding the shorter one
    would invent components nobody measured, and comparing the common prefix would silently
    compare a coordinate against a fragment of a different one."""
    assert strategy.compare((1,), (1, 2)) == INCOMPARABLE.name


@pytest.mark.parametrize(
    "strategy",
    [LexicographicStrategy(), CausalStrategy(), BranchingStrategy()],
    ids=["lexicographic", "causal", "branching"],
)
def test_components_that_cannot_be_ordered_are_incomparable_rather_than_a_crash(strategy) -> None:
    """`components` is opaque by design, so a position may hold anything. A strategy that raised
    on an unorderable pair would make the opacity a lie; INCOMPARABLE is the honest answer."""
    assert strategy.compare((object(),), (object(),)) == INCOMPARABLE.name


def test_a_consensus_comparison_of_unorderable_components_is_incomparable() -> None:
    """The observer prefix agrees and the remainder cannot be ordered, which is a different
    reason for INCOMPARABLE from a disagreeing observer and must not be spelled differently."""
    strategy = ConsensusStrategy(agreeing=("obs",))
    assert strategy.compare(("obs", object()), ("obs", object())) == INCOMPARABLE.name


def test_a_branching_comparison_whose_branches_diverge_is_incomparable() -> None:
    """Two positions on different branches are not ordered by anything this package can see, and
    ordering them by their remainders would order events across a fork."""
    strategy = BranchingStrategy()
    assert strategy.compare(("a", 1), ("b", 1)) == INCOMPARABLE.name


def test_registering_two_strategies_under_one_ordering_name_is_refused() -> None:
    """One ordering name with two comparison behaviours makes every claim about event order
    unenforceable, so a second implementation must declare a new ordering instead."""

    class _Impostor(LexicographicStrategy):
        pass

    with pytest.raises(OrderingError, match="already implemented by"):
        default_registry((_Impostor(),))


def test_declaring_one_ordering_name_with_two_meanings_is_refused() -> None:
    """One name with two meanings is worse than two names: a record citing the ordering would be
    read under whichever meaning the reader's registry happened to hold."""
    registry = default_registry()
    with pytest.raises(OrderingError, match="already declared with a different meaning"):
        registry.declare(Ordering(name=TOTAL.name, description="something else entirely"))


def test_citing_an_ordering_nobody_declared_is_refused() -> None:
    """Declaring it is how a sixth discipline joins this system, and it must happen before a
    record cites it — otherwise the record's order claim is interpreted by nothing."""
    with pytest.raises(OrderingError, match="not a declared ordering"):
        default_registry().ordering("AN-ORDERING-NOBODY-DECLARED")


def test_the_factory_admits_a_strategy_this_package_did_not_ship() -> None:
    """No process-wide singleton: ConsensusStrategy carries its agreeing-observer set, so a
    shared registry would let one federation's configuration govern another's comparisons."""

    class _Custom(LexicographicStrategy):
        def ordering(self) -> Ordering:
            return Ordering(name="FEDERATED", description="a sixth discipline")

    registry = default_registry((_Custom(),))
    assert registry.ordering("FEDERATED").name == "FEDERATED"


def test_a_strategy_whose_comparison_does_not_mirror_its_inverse_is_refused() -> None:
    """`compare(a, b)` must mirror to `compare(b, a)` through the declared inverse, or "the
    earlier event" is undefined while appearing to have an answer."""

    class _Asymmetric(LexicographicStrategy):
        def compare(self, left, right):  # noqa: ANN001, ANN201
            return BEFORE.name

    with pytest.raises(OrderingError, match="where .* was required by the declared"):
        assert_consistent(_Asymmetric(), ((1,), (2,)), RelationRegistry())


def test_a_branching_comparison_of_unorderable_remainders_is_incomparable() -> None:
    """The branch prefix agrees and the remainder cannot be ordered. Reporting a relation anyway
    would order two events on one branch by something nobody measured."""
    strategy = BranchingStrategy()
    assert strategy.compare(("a", object()), ("a", object())) == INCOMPARABLE.name


def test_registering_a_strategy_under_a_declared_name_with_a_different_meaning_is_refused():
    """The two guards are separate: one refuses a second IMPLEMENTATION of a declared ordering,
    this one refuses a second MEANING arriving with its own implementation."""

    class _Redefining(LexicographicStrategy):
        def ordering(self) -> Ordering:
            return Ordering(name=TOTAL.name, description="a different meaning entirely")

    registry = OrderingRegistry()
    registry.declare(TOTAL)
    with pytest.raises(OrderingError, match="already declared with a different meaning"):
        registry.register(_Redefining())


@pytest.mark.parametrize("absent", ["source", "target"])
def test_a_frame_relation_that_relates_nothing_is_refused(absent) -> None:
    """A relation with no source or no target grants comparability between a frame and nothing,
    which reads exactly like comparability granted."""
    fields = {"source": "A", "target": "B", "rule": "R-01"}
    fields[absent] = "   "
    with pytest.raises(ReferenceError, match=f"no {absent} relates nothing"):
        FrameRelation(**fields)


def test_a_registry_can_be_seeded_with_its_relations_and_refuses_a_second_one() -> None:
    """Seeding is one call, and a second relation between the same pair would make comparability
    depend on declaration order rather than on what was declared."""
    first = FrameRelation(source="EARTH", target="MARS", rule="R-01")
    registry = FrameRegistry(relations=(first,))
    assert first in registry.relations()
    assert registry.relate(first) == first
    with pytest.raises(ReferenceError, match="would make comparability depend"):
        registry.relate(FrameRelation(source="EARTH", target="MARS", rule="R-02"))


def test_redeclaring_the_identical_frame_is_idempotent() -> None:
    """A registry has to be seedable twice from one vocabulary, so re-declaring the same frame
    returns it — while a second MEANING under one name is refused."""
    registry = FrameRegistry()
    existing = registry.resolve("EARTH")
    assert registry.declare(existing) is existing
