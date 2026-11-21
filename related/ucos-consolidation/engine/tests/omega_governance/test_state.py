"""Ω∞ governance state — six axes, and the elimination of the silent state.

THE DEFECT THIS VOCABULARY REPLACES. Seven separate vocabularies in this repository each collapsed
governance onto one scalar, and none of them had a word for "we do not know". An artifact that is
GOVERNED and UNMEASURED is the most common artifact there is — a rule claims it and nobody has
observed it yet — and a single-axis vocabulary literally cannot say so. It reports one of the two
and silently drops the other.

WHAT MAKES IT A MECHANISM RATHER THAN A LIST. A ``GovernanceStatus`` holds exactly one position per
REGISTERED axis, so silence is unrepresentable; the transition graph's ABSENCE of an edge is the
refusal, so a state change nobody declared cannot happen by default; and every applied transition
returns an audit record naming the rule that permitted it.
"""

from __future__ import annotations

from dataclasses import replace

import pytest

from engine.omega_governance.state import (
    ATTRIBUTED,
    CERTIFIED,
    CONSISTENT,
    CONTRADICTED,
    DISCOVERED,
    EXEMPTED,
    GOVERNED,
    INITIAL_STATES,
    MEASURED,
    REQUIRED_STATE_NAMES,
    SEPARATIONS,
    UNATTRIBUTED,
    UNCERTIFIED,
    UNGOVERNED,
    UNKNOWN,
    UNMEASURABLE,
    UNMEASURED,
    Axis,
    GovernanceState,
    GovernanceStatus,
    StateError,
    StateRegistry,
    Transition,
    TransitionGraph,
    advance,
    assert_total,
    census,
    check,
    default_graph,
    default_states,
    initial_status,
    population_of,
    separation_report,
    vocabulary_report,
)
from engine.omega_governance.temporal.clocks import LogicalClock

CUSTODY_AXIS = UNKNOWN.axis


# ---------------------------------------------------------------------------- vocabulary


def test_the_twenty_shipped_states_span_six_independent_axes() -> None:
    registry = default_states()
    assert len(registry) == len(INITIAL_STATES) == 20
    assert {axis.name for axis in registry.axes()} == {
        "ATTRIBUTION",
        "CERTIFICATION",
        "CONSISTENCY",
        "CUSTODY",
        "GOVERNANCE",
        "MEASUREMENT",
    }


def test_every_required_state_name_is_actually_declared() -> None:
    """``REQUIRED_STATE_NAMES`` is the contract; the registry is the implementation. Checking one
    against the other is what stops a rename from quietly deleting a concept."""
    registry = default_states()
    for name in REQUIRED_STATE_NAMES:
        assert name in registry


def test_each_axis_has_exactly_one_initial_state() -> None:
    """Neither zero nor two. Zero leaves a never-touched artifact silent on that axis; two makes the
    starting position a coin toss."""
    registry = default_states()
    for axis in registry.axes():
        assert registry.initial(axis) is not None


def test_a_state_and_an_axis_must_be_named() -> None:
    with pytest.raises(StateError):
        Axis("   ")
    with pytest.raises(StateError):
        GovernanceState("   ", CUSTODY_AXIS)


def test_an_unknown_state_name_is_refused_rather_than_invented() -> None:
    with pytest.raises(StateError):
        default_states().resolve("PROBABLY_FINE")


def test_a_seventh_axis_can_be_declared_with_no_edit_to_the_module() -> None:
    """Rule 3. A concern this package never imagined is a registration, and ``axes()`` is DERIVED
    from the declared states so it cannot disagree with them."""
    registry = default_states()
    retention = Axis("RETENTION", "Whether an artifact is inside its declared retention window.")
    registry.declare_name("RETAINED", retention, "Inside the window.", initial=True)
    registry.declare_name("EXPIRED", retention, "Past the window.")
    assert retention in registry.axes()
    assert registry.initial(retention).name == "RETAINED"


def test_redeclaring_a_state_with_a_different_meaning_is_refused() -> None:
    registry = default_states()
    with pytest.raises(StateError):
        registry.declare(GovernanceState("MEASURED", CUSTODY_AXIS, "a rival meaning"))


def test_measured_and_governed_are_positions_on_two_different_axes() -> None:
    """The single sentence this whole module exists to make true."""
    assert MEASURED.axis != GOVERNED.axis


def test_unmeasured_and_unmeasurable_are_different_states() -> None:
    """UCI's ``coverage_percent = None`` against ``0.0``: "nobody measured it" is not "it measured
    zero", and a vocabulary with one word for both cannot report an unmeasurable artifact."""
    assert UNMEASURED != UNMEASURABLE
    assert UNMEASURED.axis == UNMEASURABLE.axis


# --------------------------------------------------------------------------------- status


def test_a_status_holds_one_position_per_axis_so_silence_is_unrepresentable() -> None:
    registry = default_states()
    status = initial_status(registry)
    assert len(status) == len(registry.axes())
    assert status.names() == (
        "CONSISTENT",
        "UNATTRIBUTED",
        "UNCERTIFIED",
        "UNGOVERNED",
        "UNKNOWN",
        "UNMEASURED",
    )


def test_a_status_can_be_asked_its_position_on_one_axis() -> None:
    status = initial_status(default_states())
    assert status.position(CUSTODY_AXIS) == UNKNOWN
    assert status.holds(UNKNOWN)
    assert not status.holds(DISCOVERED)


def test_asking_a_status_about_an_axis_it_is_silent_on_raises() -> None:
    """Returning ``None`` would reintroduce exactly the silent state the axes exist to abolish."""
    partial = GovernanceStatus((UNKNOWN,))
    with pytest.raises(StateError):
        partial.position(GOVERNED.axis)


def test_two_positions_on_one_axis_is_refused() -> None:
    with pytest.raises(StateError):
        GovernanceStatus((UNKNOWN, DISCOVERED))


def test_the_vector_is_the_canonical_identity_of_a_governance_position() -> None:
    registry = default_states()
    status = initial_status(registry)
    assert all(len(pair) == 2 for pair in status.vector())
    # Deterministic and order-independent: two statuses holding the same positions must produce the
    # same vector however the positions were assembled, or the "canonical identity" is not one.
    reshuffled = GovernanceStatus(tuple(reversed(status.states)))
    assert reshuffled.vector() == status.vector()
    assert dict(status.vector()) == {state.axis.name: state.name for state in status}


# ----------------------------------------------------------------------------- transitions


def test_a_declared_edge_is_permitted_and_names_the_rule_that_permitted_it() -> None:
    registry, graph = default_states(), default_graph()
    status = initial_status(registry)
    edge, why = check(status, DISCOVERED, graph=graph)
    assert edge is not None
    assert edge.rule == "Ω²-S-01"
    assert why == ""


def test_an_undeclared_edge_is_refused_and_absence_is_the_refusal() -> None:
    """The default is NO. A transition table whose default was "permit" would make the graph
    decorative — every unlisted move would work and only the listed ones would be checked."""
    registry, graph = default_states(), default_graph()
    status = initial_status(registry)
    edge, why = check(status, CERTIFIED, graph=graph)
    assert edge is None
    assert why.strip()


def test_advancing_returns_a_new_status_and_an_audit_record() -> None:
    registry, graph = default_states(), default_graph()
    status = initial_status(registry)
    advanced, record = advance(status, DISCOVERED, subject="artifact-1", graph=graph)

    assert advanced.holds(DISCOVERED)
    assert record.subject == "artifact-1"
    assert record.axis == "CUSTODY"
    assert record.source == "UNKNOWN"
    assert record.target == "DISCOVERED"
    assert record.rule == "Ω²-S-01"


def test_advancing_does_not_mutate_the_status_it_was_given() -> None:
    registry, graph = default_states(), default_graph()
    status = initial_status(registry)
    advance(status, DISCOVERED, subject="artifact-1", graph=graph)
    assert status.holds(UNKNOWN), "advance mutated its argument"


def test_advancing_along_an_undeclared_edge_raises_rather_than_proceeding() -> None:
    registry, graph = default_states(), default_graph()
    with pytest.raises(StateError):
        advance(initial_status(registry), CERTIFIED, subject="artifact-1", graph=graph)


def test_a_transition_that_requires_a_reason_refuses_an_empty_one() -> None:
    """A state change an operator cannot justify in words is one nobody can review later."""
    axis = Axis("TEST_AXIS", "A test concern.")
    start = GovernanceState("START", axis, "Initial.", initial=True)
    end = GovernanceState("END", axis, "Terminal.")
    graph = TransitionGraph(
        [Transition(source=start, target=end, rule="TEST-T-01", requires_reason=True)]
    )
    status = GovernanceStatus((start,))

    edge, why = check(status, end, graph=graph)
    assert edge is None and why.strip()
    with pytest.raises(StateError):
        advance(status, end, subject="artifact-1", graph=graph)

    advanced, record = advance(
        status, end, subject="artifact-1", reason="the owner retired it", graph=graph
    )
    assert advanced.holds(end)
    assert record.reason == "the owner retired it"


def test_a_blocked_by_state_refuses_a_transition_the_edge_otherwise_permits() -> None:
    """A guard that reads a position on ANOTHER axis. Without it, an artifact could be certified
    while contradicted, and the transition table would have permitted it edge by edge."""
    axis = Axis("TEST_AXIS", "A test concern.")
    start = GovernanceState("START", axis, "Initial.", initial=True)
    end = GovernanceState("END", axis, "Terminal.")
    graph = TransitionGraph(
        [Transition(source=start, target=end, rule="TEST-T-02", blocked_by=(CONTRADICTED,))]
    )

    clear = GovernanceStatus((start, CONSISTENT))
    assert check(clear, end, graph=graph)[0] is not None

    blocked = GovernanceStatus((start, CONTRADICTED))
    edge, why = check(blocked, end, graph=graph)
    assert edge is None
    assert "CONTRADICTED" in why


def test_a_duplicate_edge_raises_rather_than_overwriting_a_declared_rule() -> None:
    axis = Axis("TEST_AXIS", "A test concern.")
    start = GovernanceState("START", axis, "Initial.", initial=True)
    end = GovernanceState("END", axis, "Terminal.")
    graph = TransitionGraph([Transition(source=start, target=end, rule="TEST-T-03")])
    with pytest.raises(StateError):
        graph.register(Transition(source=start, target=end, rule="TEST-T-04"))


def test_a_transition_between_two_axes_is_refused() -> None:
    """A transition is a move ALONG one axis. An edge spanning two would let a measurement outcome
    silently rewrite a governance claim, which is the conflation this design forbids."""
    with pytest.raises(StateError):
        Transition(source=UNKNOWN, target=GOVERNED, rule="TEST-T-05")


def test_the_graph_can_be_queried_forwards_backwards_and_by_rule() -> None:
    graph = default_graph()
    assert DISCOVERED in {edge.target for edge in graph.outgoing(UNKNOWN)}
    assert UNKNOWN in {edge.source for edge in graph.incoming(DISCOVERED)}
    assert graph.rule("Ω²-S-01") is not None


def test_unknown_is_left_only_by_observation_and_never_by_relabelling() -> None:
    """The one property that stops the unknown population from draining without being measured."""
    graph = default_graph()
    exits = {edge.target.name for edge in graph.outgoing(UNKNOWN)}
    assert exits == {"DISCOVERED"}


def test_an_audit_record_renders_to_a_document() -> None:
    registry, graph = default_states(), default_graph()
    _, record = advance(initial_status(registry), DISCOVERED, subject="a", graph=graph)
    assert record.as_record()["rule"] == "Ω²-S-01"


def test_an_audit_record_can_carry_the_coordinate_a_clock_supplied() -> None:
    """The state change is stamped with a position from an injected clock, so replaying a history
    produces byte-identical evidence rather than whatever the wall clock said."""
    registry, graph = default_states(), default_graph()
    clock = LogicalClock("audit")
    _, record = advance(initial_status(registry), DISCOVERED, subject="a", graph=graph, clock=clock)
    assert record.coordinate is not None
    assert record.coordinate.clock == "audit"


# ------------------------------------------------------------------------------ population


def test_a_census_reports_every_declared_position_including_the_zeroes() -> None:
    """A census that omitted the empty states would make "nothing is in this state" and "this state
    does not exist" the same reading, and only one of those is good news."""
    registry, graph = default_states(), default_graph()
    advanced, _ = advance(initial_status(registry), DISCOVERED, subject="a", graph=graph)
    counted = census([advanced], registry)
    assert counted["CUSTODY"]["DISCOVERED"] == 1
    assert counted["CUSTODY"]["UNKNOWN"] == 0
    assert counted["CUSTODY"]["ARCHIVED"] == 0


def test_a_population_can_be_named_subject_by_subject_so_it_can_be_driven_to_zero() -> None:
    registry, graph = default_states(), default_graph()
    advanced, _ = advance(initial_status(registry), DISCOVERED, subject="a", graph=graph)
    statuses = [("a", advanced), ("b", initial_status(registry))]
    assert population_of(statuses, DISCOVERED) == ("a",)
    assert population_of(statuses, UNKNOWN) == ("b",)


def test_assert_total_refuses_a_population_silent_about_a_registered_axis() -> None:
    registry = default_states()
    with pytest.raises(StateError):
        # Import the __init__ so the package's own module executes under measurement.
        __import__("engine.omega_governance")
        raise_if = GovernanceStatus((UNKNOWN,))
        assert_total([("a", raise_if)], registry)


def test_assert_total_accepts_a_population_with_a_position_on_every_axis() -> None:
    registry = default_states()
    assert_total([("a", initial_status(registry)), ("b", initial_status(registry))], registry)


def test_every_required_separation_is_expressible() -> None:
    """The report answers the question the seven old vocabularies could not: can this system even
    SAY that an artifact is governed and unmeasured?"""
    report = {entry["combination"]: entry for entry in separation_report()}
    assert {name for name, _left, _right in SEPARATIONS} == set(report)
    for entry in report.values():
        assert entry["expressible"] is True


def test_a_separation_report_counts_the_artifacts_actually_holding_each_combination() -> None:
    governed_unmeasured = GovernanceStatus(
        (UNKNOWN, UNATTRIBUTED, GOVERNED, UNMEASURED, UNCERTIFIED, CONSISTENT)
    )
    report = {
        entry["combination"]: entry for entry in separation_report([("a", governed_unmeasured)])
    }
    assert report["governed but not measured"]["population"] == 1
    assert "a" in report["governed but not measured"]["examples"]


def test_the_vocabulary_report_describes_the_states_and_the_graph() -> None:
    report = vocabulary_report(default_states(), default_graph())
    assert isinstance(report, dict)
    assert report


def test_an_exempted_artifact_is_governed_rather_than_ungoverned() -> None:
    """An exemption is a GOVERNANCE act. Filing it as "not governed" is how an exempted artifact
    becomes indistinguishable from one nobody ever claimed."""
    assert EXEMPTED.axis == GOVERNED.axis == UNGOVERNED.axis


def test_attribution_is_independent_of_custody() -> None:
    assert ATTRIBUTED.axis != DISCOVERED.axis
    assert UNATTRIBUTED.axis == ATTRIBUTED.axis


def test_an_empty_registry_reports_no_axes_rather_than_raising() -> None:
    empty = StateRegistry(seed=())
    assert len(empty) == 0
    assert empty.axes() == ()


# --------------------------------------------------------------------------------------
# The refusals the vocabulary itself carries.
#
# WHY THESE EXIST. The suite above proves what the SIX AXES mean and what the graph
# permits. The registry and the transition record carry their own refusals — a name
# redeclared with a different meaning, a transition from a state to itself, a transition
# with no rule id, two transitions claiming one rule id — and none of them had ever fired.
# Each refuses a way the vocabulary could quietly stop meaning one thing, which is the
# failure mode a vocabulary has.
# --------------------------------------------------------------------------------------


def test_redeclaring_a_state_identically_is_the_same_declaration(tmp_axis=None):
    registry = StateRegistry()
    first = registry.declare(GOVERNED)
    assert registry.declare(GOVERNED) is first
    assert GOVERNED in registry.known()


def test_one_name_may_not_carry_two_meanings():
    """A name that means two things makes every rule about it unenforceable."""

    registry = StateRegistry()
    registry.declare(GOVERNED)
    with pytest.raises(StateError, match="different"):
        registry.declare(replace(GOVERNED, description="something else entirely"))
    with pytest.raises(StateError, match="different"):
        registry.declare(replace(GOVERNED, initial=not GOVERNED.initial))


def test_extra_states_are_declared_into_the_default_registry():
    extra = GovernanceState(
        axis=GOVERNED.axis, name="PROVISIONALLY_GOVERNED", description="a future position."
    )
    registry = default_states((extra,))
    assert extra in registry.known()
    assert registry.known() == tuple(sorted(registry.known()))


def test_a_transition_from_a_state_to_itself_is_refused():
    with pytest.raises(StateError):
        Transition(source=GOVERNED, target=GOVERNED, rule="Ω-R-SELF")


def test_a_transition_with_no_rule_id_cannot_be_cited_by_an_audit_record():
    with pytest.raises(StateError, match="rule id"):
        Transition(source=UNGOVERNED, target=GOVERNED, rule="   ")


def _synthetic_axis():
    axis = Axis(name="SYNTHETIC", description="An axis declared by this test alone.")
    start = GovernanceState(axis=axis, name="SYN_START", description="start.", initial=True)
    middle = GovernanceState(axis=axis, name="SYN_MIDDLE", description="middle.")
    end = GovernanceState(axis=axis, name="SYN_END", description="end.")
    return start, middle, end


def test_two_transitions_may_not_claim_one_rule_id():
    """A rule id is what an audit record cites, so two edges under one id make the record
    ambiguous about which change it authorised."""
    start, middle, end = _synthetic_axis()
    graph = TransitionGraph()
    graph.register(Transition(source=start, target=middle, rule="Ω-R-SYNTHETIC"))
    with pytest.raises(StateError, match="ambiguous"):
        graph.register(Transition(source=middle, target=end, rule="Ω-R-SYNTHETIC"))


def test_one_edge_may_not_be_declared_twice():
    start, middle, _end = _synthetic_axis()
    graph = TransitionGraph()
    graph.register(Transition(source=start, target=middle, rule="Ω-R-ONE"))
    with pytest.raises(StateError, match="table order"):
        graph.register(Transition(source=start, target=middle, rule="Ω-R-TWO"))


def test_extra_transitions_are_registered_into_the_default_graph():
    start, middle, _end = _synthetic_axis()
    extra = Transition(source=start, target=middle, rule="Ω-R-SYNTHETIC-EXTRA")
    graph = default_graph((extra,))
    assert graph.edge(start, middle) is extra
    assert len(graph) > 1


def test_a_status_reports_its_axes_and_its_record():
    status = initial_status(default_states())
    assert status.axes() == tuple(sorted(status.axes()))
    assert len(status.axes()) == len(status.states)
    record = status.as_record()
    assert set(record) == {axis.name for axis in status.axes()}
    assert all(state in status for state in status.states)
    _start, middle, _end = _synthetic_axis()
    assert middle not in status
    assert "not a state" not in status


def test_a_change_that_cannot_be_made_is_reported_rather_than_performed():
    """A gate must report every refusal in a population rather than stop at the first, which
    is why the refusal comes back as a reason and never as an exception."""
    graph = default_graph()
    status = initial_status(default_states())

    already = status.position(GOVERNED.axis)
    change, reason = check(status, already, graph=graph)
    assert change is None
    assert "already at" in reason

    change, reason = check(status, CERTIFIED, graph=TransitionGraph())
    assert change is None
    assert reason

    _start, middle, _end = _synthetic_axis()
    change, reason = check(status, middle, graph=graph)
    assert change is None
    assert reason


def test_advancing_a_subject_with_no_identity_is_refused():
    """An audit record about an unnamed artifact cannot be joined to the artifact it
    describes, so the record and the change are refused together."""
    status = initial_status(default_states())
    with pytest.raises(StateError, match="name its subject"):
        advance(status, GOVERNED, subject="   ", graph=default_graph())


def test_an_edge_the_graph_does_not_declare_is_refused_by_its_absence() -> None:
    """The edge's absence IS the refusal. A graph holding no transitions permits nothing, and
    adding one is a deliberate widening of what this graph allows rather than a default."""
    status = initial_status(default_states())
    change, reason = check(status, DISCOVERED, graph=TransitionGraph(()))
    assert change is None
    assert "no declared transition from UNKNOWN to DISCOVERED" in reason


def test_a_change_record_carries_a_coordinate_only_when_a_clock_supplied_one() -> None:
    """A record that always carried the key would make "this deployment has no clock" and "the
    clock declined to answer" the same document — and keeping Time unprivileged is the whole
    reason a deployment with no clock has to stay expressible."""

    graph = default_graph()
    status = initial_status(default_states())
    _, unstamped = advance(status, DISCOVERED, subject="a/path", graph=graph)
    assert "coordinate" not in unstamped.as_record()
    _, stamped = advance(
        status, DISCOVERED, subject="a/path", graph=graph, clock=LogicalClock("test")
    )
    assert stamped.as_record()["coordinate"]
