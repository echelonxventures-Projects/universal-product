"""UCOS-NUC-001 Part 10 — the structural population bound to a location-derived context.

The property under test throughout: **an unresolved context fails closed**. Every entry
point that would make a context durable — a lifecycle run, a lineage entry, an evolution
generation, a certificate — refuses an incomplete frame rather than binding a partial
reality and letting the hole surface later.

The second property: a record made in one reality is distinguishable from the same record
made in another. If binding a frame did not change the digest, the binding would be
decoration.
"""

from __future__ import annotations

import pytest

from engine.context.location import build_frame_registry
from engine.nucleus import certification, lifecycle, lineage
from engine.nucleus.context import (
    CONTEXT_BOUND,
    CONTEXT_GATES,
    bind,
    bind_lineage,
    bind_registry,
    context_fingerprint,
    context_gates,
    context_measurements,
    context_stage_function,
    dictionary_with_context,
    evolutions_without_context,
    evolve_in_context,
    execute_in_context,
    replay_in_context,
    require_complete,
    to_document,
    unbound_subjects,
)
from engine.nucleus.errors import (
    CertificationError,
    ContextBindingViolation,
    EvolutionError,
    LifecycleError,
)
from engine.nucleus.evolution import (
    EvolutionLedger,
    all_of,
    context_is_declared,
    state_must_grow,
)
from engine.nucleus.lineage import LineageLedger
from engine.nucleus.registry import build_seed_registry
from engine.registry.universal.dictionary import dictionary_for
from engine.uckp.canonical import content_hash

COMPLETE = "planetary-a1"
OTHER = "planetary-b4"
INCOMPLETE = "partial-frame-p0"
EMPTY = "unresolved"


@pytest.fixture
def frames():
    return build_frame_registry()


@pytest.fixture
def registry():
    return build_seed_registry()


@pytest.fixture
def resolution(frames):
    return frames.resolve(COMPLETE)


# --------------------------------------------------------------------------- #
# Fail-closed                                                                  #
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize("frame", [INCOMPLETE, EMPTY])
def test_an_incomplete_context_cannot_be_bound(frames, frame):
    with pytest.raises(LifecycleError) as caught:
        require_complete(frames.resolve(frame), error=LifecycleError)
    assert caught.value.detail["unresolved"]
    assert caught.value.detail["frame"] == frame


def test_the_refusal_names_the_gap_rather_than_merely_reporting_one(frames):
    with pytest.raises(LifecycleError) as caught:
        context_stage_function(frames.resolve(INCOMPLETE))
    unresolved = caught.value.detail["unresolved"]
    assert set(unresolved) == set(frames.resolve(INCOMPLETE).unresolved_axes)


def test_an_incomplete_context_cannot_carry_an_evolution(frames):
    ledger = EvolutionLedger()
    with pytest.raises(EvolutionError):
        evolve_in_context(
            ledger,
            frames.resolve(EMPTY),
            subject_id="s",
            subject_key="k",
            change="c",
            authority="a",
        )
    assert ledger.evolutions() == ()


def test_an_incomplete_context_cannot_bind_lineage(frames):
    ledger = LineageLedger()
    with pytest.raises(LifecycleError):
        bind_lineage(ledger, frames.resolve(INCOMPLETE), subjects=[("id", "key")])
    assert len(ledger) == 0


def test_a_complete_context_binds(resolution):
    assert require_complete(resolution, error=LifecycleError) is resolution


# --------------------------------------------------------------------------- #
# The fingerprint                                                              #
# --------------------------------------------------------------------------- #


def test_the_fingerprint_names_the_reality(resolution):
    fingerprint = context_fingerprint(resolution)
    assert fingerprint["frame"] == COMPLETE
    assert fingerprint["frame_id"] == resolution.frame_id
    assert fingerprint["chain"] == list(resolution.chain)
    assert fingerprint["resolution_digest"] == resolution.digest()
    assert fingerprint["location"] == resolution.value_of("location")


def test_two_frames_fingerprint_differently(frames):
    assert context_fingerprint(frames.resolve(COMPLETE)) != context_fingerprint(
        frames.resolve(OTHER)
    )


def test_the_fingerprint_is_deterministic(resolution):
    assert context_fingerprint(resolution) == context_fingerprint(resolution)


# --------------------------------------------------------------------------- #
# Lifecycle → context                                                          #
# --------------------------------------------------------------------------- #


def test_every_stage_runs_inside_the_frame(resolution):
    execution = lifecycle.execute("UCOS-SUBJ", stage_function=context_stage_function(resolution))
    assert execution.complete
    assert len(execution.outcomes) == len(lifecycle.STAGES)
    for outcome in execution.outcomes:
        assert outcome.detail["context"]["frame"] == COMPLETE
        assert outcome.evidence.startswith(resolution.frame_id)


def test_the_journal_chain_survives_the_binding(resolution):
    execution = lifecycle.execute("UCOS-SUBJ", stage_function=context_stage_function(resolution))
    assert execution.chain_is_intact()


def test_a_run_in_context_is_a_fixed_point(resolution):
    replay = lifecycle.replay("UCOS-SUBJ", stage_function=context_stage_function(resolution))
    assert replay["fixed_point"] and replay["chain_intact"]
    assert replay["status"] == "COMPLETE"


def test_the_same_subject_in_two_frames_yields_two_records(frames):
    here = lifecycle.execute("S", stage_function=context_stage_function(frames.resolve(COMPLETE)))
    there = lifecycle.execute("S", stage_function=context_stage_function(frames.resolve(OTHER)))
    assert here.digest() != there.digest()


def test_binding_a_frame_changes_the_execution_digest(resolution):
    plain = lifecycle.execute("S")
    bound = lifecycle.execute("S", stage_function=context_stage_function(resolution))
    assert plain.digest() != bound.digest()


# --------------------------------------------------------------------------- #
# Lineage → context                                                            #
# --------------------------------------------------------------------------- #


def test_every_subject_is_bound_and_the_chain_stays_intact(registry, resolution):
    ledger = lineage.ledger_for(registry)
    heads = bind_registry(registry, ledger, resolution)
    assert len(heads) == len(registry.subjects())
    assert ledger.is_intact()
    assert unbound_subjects(registry, ledger) == ()


def test_a_binding_is_a_first_class_lineage_event(registry, resolution):
    ledger = lineage.ledger_for(registry)
    bind_registry(registry, ledger, resolution)
    entries = ledger.entries(event=CONTEXT_BOUND)
    assert len(entries) == len(registry.subjects())
    for entry in entries:
        assert entry.detail["frame"] == COMPLETE
        assert entry.entry_hash == entry.computed_hash()


def test_an_unbound_population_is_reported(registry):
    ledger = lineage.ledger_for(registry)
    unbound = unbound_subjects(registry, ledger)
    assert len(unbound) == len(registry.subjects())


def test_binding_only_some_subjects_reports_the_rest(registry, resolution):
    ledger = lineage.ledger_for(registry)
    first = registry.subjects()[0]
    bind_lineage(ledger, resolution, subjects=[(first.universal_id, first.key)])
    unbound = unbound_subjects(registry, ledger)
    assert first.universal_id not in unbound
    assert len(unbound) == len(registry.subjects()) - 1


# --------------------------------------------------------------------------- #
# Evolution → context                                                          #
# --------------------------------------------------------------------------- #


def test_an_evolution_carries_the_reality_it_happened_in(resolution):
    ledger = EvolutionLedger(validator=state_must_grow)
    evolution = evolve_in_context(
        ledger,
        resolution,
        subject_id="UCOS-S",
        subject_key="s",
        change="c",
        authority="UCOS-NUC-001",
        state={"capability": 1},
    )
    assert evolution.state["context"]["frame"] == COMPLETE
    assert evolutions_without_context(ledger) == ()


def test_the_same_change_in_two_frames_is_two_evolutions(frames):
    here = EvolutionLedger()
    there = EvolutionLedger()
    common = {"subject_id": "UCOS-S", "subject_key": "s", "change": "c", "authority": "a"}
    a = evolve_in_context(here, frames.resolve(COMPLETE), **common)
    b = evolve_in_context(there, frames.resolve(OTHER), **common)
    assert a.digest() != b.digest()


def test_an_evolution_recorded_without_a_frame_is_reported():
    ledger = EvolutionLedger()
    ledger.evolve(subject_id="UCOS-S", subject_key="s", change="c", authority="a")
    assert evolutions_without_context(ledger) == (ledger.evolutions()[0].evolution_id,)


def test_the_context_evolution_still_writes_lineage(resolution):
    lineage_ledger = LineageLedger()
    ledger = EvolutionLedger(lineage=lineage_ledger)
    evolve_in_context(
        ledger, resolution, subject_id="UCOS-S", subject_key="s", change="c", authority="a"
    )
    assert ledger.unevidenced() == ()
    assert lineage_ledger.is_intact()


def test_capability_must_still_not_regress_in_context(resolution):
    ledger = EvolutionLedger(validator=state_must_grow)
    common = {"subject_id": "UCOS-S", "subject_key": "s", "authority": "a"}
    evolve_in_context(ledger, resolution, change="c1", state={"capability": 5}, **common)
    with pytest.raises(EvolutionError):
        evolve_in_context(ledger, resolution, change="c2", state={"capability": 1}, **common)


# --------------------------------------------------------------------------- #
# Identifier → context                                                         #
# --------------------------------------------------------------------------- #


def test_frames_and_axes_enter_the_one_dictionary(registry, frames):
    dictionary = dictionary_with_context(registry, frames)
    by_kind = dictionary.by_kind()
    assert by_kind["LOCATION"] == len(frames)
    assert by_kind["CONTEXT"] > 0
    assert by_kind["NUCLEUS"] == len(registry.nuclei())
    assert dictionary.is_verified


def test_every_dictionary_entry_reproduces(registry, frames):
    dictionary = dictionary_with_context(registry, frames)
    verification = dictionary.verify()
    assert verification["status"] == "PASS"
    assert verification["unreproducible"] == []
    assert verification["unparsed"] == []
    assert verification["duplicated_natural_keys"] == []


def test_an_axis_entry_names_its_frame_as_owner(registry, frames):
    dictionary = dictionary_with_context(registry, frames)
    axis_entries = [e for e in dictionary.entries() if e.attributes.get("axis")]
    assert axis_entries
    for entry in axis_entries:
        assert entry.owner == frames.frame(entry.attributes["frame"]).universal_id


def test_adding_context_is_idempotent(registry, frames):
    dictionary = dictionary_with_context(registry, frames)
    again = dictionary_with_context(registry, frames, dictionary=dictionary)
    assert len(again) == len(dictionary)


def test_the_dictionary_is_deterministic(registry, frames):
    assert (
        dictionary_with_context(registry, frames).digest()
        == dictionary_with_context(registry, frames).digest()
    )


# --------------------------------------------------------------------------- #
# Measurement and certification                                                #
# --------------------------------------------------------------------------- #


def test_the_context_axis_is_measured_without_a_frame(frames):
    measurements = context_measurements(frames)
    assert measurements["certified"] is True
    assert measurements["validation_violations"] == 0
    assert measurements["replay_fixed_point"] is True
    assert measurements["frame"] == ""


def test_naming_a_frame_makes_the_measurement_frame_specific(frames):
    here = context_measurements(frames, frame_key=COMPLETE)
    there = context_measurements(frames, frame_key=OTHER)
    assert here["frame"] == COMPLETE
    assert here["context_digest"] != there["context_digest"]
    assert here["resolution_digest"] == frames.resolve(COMPLETE).digest()


def test_measuring_an_incomplete_frame_fails_closed(frames):
    with pytest.raises(LifecycleError):
        context_measurements(frames, frame_key=INCOMPLETE)


def test_validation_measures_the_context_axis_unconditionally(registry):
    report = certification.validate(registry)
    ids = {check.check_id for check in report.checks}
    assert {"CV-13", "CV-14", "CV-15", "CV-16"} <= ids
    assert report.passed


def test_naming_a_frame_adds_the_four_context_gates(registry):
    report = certification.validate(registry, frame_key=COMPLETE)
    ids = {check.check_id for check in report.checks}
    assert {
        "CV-CONTEXT-01",
        "CV-CONTEXT-02",
        "CV-CONTEXT-03",
        "CV-CONTEXT-04",
    } <= ids
    assert report.passed


def test_the_context_gates_are_absent_until_a_frame_is_named(registry):
    ids = {check.check_id for check in certification.validate(registry).checks}
    assert not any(check.startswith("CV-CONTEXT-") for check in ids)


def test_an_evolution_ledger_adds_the_evolution_context_check(registry):
    ledger = lineage.ledger_for(registry)
    evolution = EvolutionLedger(lineage=ledger)
    report = certification.validate(registry, lineage=ledger, evolution=evolution)
    ids = {check.check_id for check in report.checks}
    assert {"CV-11", "CV-12", "CV-18"} <= ids
    assert report.passed


def test_an_evolution_without_a_frame_fails_the_context_check(registry):
    ledger = lineage.ledger_for(registry)
    evolution = EvolutionLedger(lineage=ledger)
    evolution.evolve(subject_id="UCOS-S", subject_key="s", change="c", authority="a")
    report = certification.validate(registry, lineage=ledger, evolution=evolution)
    assert not report.passed
    assert "CV-18" in {check.check_id for check in report.failures}


def test_certifying_in_a_frame_binds_the_population(registry):
    certificate = certification.certify(registry, frame_key=COMPLETE)
    assert certificate.certified
    assert certificate.frame == COMPLETE
    assert certificate.context_digest


def test_one_population_in_two_frames_is_two_certificates():
    """Rebasing produces a new registry — so two realities are two populations."""
    here = certification.certify(build_seed_registry(), frame_key=COMPLETE)
    there = certification.certify(build_seed_registry(), frame_key=OTHER)
    assert here.certificate_id != there.certificate_id
    assert here.context_digest != there.context_digest
    assert here.frame == COMPLETE and there.frame == OTHER


def test_a_certificate_is_stable_for_one_frame(registry):
    first = certification.certify(registry, frame_key=COMPLETE)
    second = certification.certify(registry, frame_key=COMPLETE)
    assert first.certificate_id == second.certificate_id
    assert first.digest() == second.digest()


def test_certifying_in_an_incomplete_frame_is_refused(registry):
    with pytest.raises(ContextBindingViolation):
        certification.certify(registry, frame_key=INCOMPLETE)


def test_the_certificate_records_the_frame_in_lineage(registry):
    ledger = lineage.ledger_for(registry)
    certification.certify(registry, lineage=ledger, frame_key=COMPLETE)
    certified = ledger.entries(event="certified")
    assert certified
    assert certified[-1].detail["frame"] == COMPLETE


def test_the_validation_report_carries_its_context(registry):
    report = certification.validate(registry, frame_key=COMPLETE)
    assert report.to_dict()["context"]["frame"] == COMPLETE


# --------------------------------------------------------------------------- #
# The document                                                                 #
# --------------------------------------------------------------------------- #


def test_the_binding_document_is_deterministic_and_open(registry, frames):
    document = to_document(registry, frames)
    assert document["closed_set"] is False
    assert document["upper_limit"] is None
    assert document["dictionary"]["verification"]["status"] == "PASS"
    assert to_document(registry, frames) == document


# --------------------------------------------------------------------------- #
# The named constitutional context obligations                                 #
# --------------------------------------------------------------------------- #


def test_context_binding(registry, resolution):
    """Binding makes the registry, its lineage and its projections context-aware."""
    ledger = bind(registry, resolution)
    assert registry.is_context_bound
    assert registry.context["frame"] == COMPLETE
    assert registry.require_context() == registry.context
    assert unbound_subjects(registry, ledger) == ()
    assert registry.to_document()["context"]["frame"] == COMPLETE


def test_context_fingerprint_is_deterministic(frames, resolution):
    first = context_fingerprint(resolution)
    second = context_fingerprint(frames.resolve(COMPLETE))
    assert first == second
    assert content_hash(first) == content_hash(second)
    assert first != context_fingerprint(frames.resolve(OTHER))


def test_context_fingerprint_refuses_an_incomplete_resolution(frames):
    """The reality context is checked first, so that is the refusal that fires."""
    with pytest.raises(ContextBindingViolation) as caught:
        context_fingerprint(frames.resolve(INCOMPLETE))
    assert caught.value.detail["unresolved"]
    assert set(caught.value.detail["unresolved"]) <= set(caught.value.detail["required"])


def test_context_fingerprint_refuses_a_frame_missing_only_non_reality_axes(frames):
    """A frame whose reality context resolves still needs every declared axis."""
    incomplete = frames.resolve("civilization-alpha")
    with pytest.raises((ContextBindingViolation, LifecycleError)):
        context_fingerprint(incomplete)


def test_unbound_subject_detection(registry, resolution):
    ledger = lineage.ledger_for(registry)
    assert len(unbound_subjects(registry, ledger)) == len(registry.subjects())
    bind_registry(registry, ledger, resolution)
    assert unbound_subjects(registry, ledger) == ()


def test_registry_context_binding(registry, resolution):
    fingerprint = context_fingerprint(resolution)
    assert registry.bind_context(fingerprint) == fingerprint
    # idempotent for the same reality
    assert registry.bind_context(fingerprint) == fingerprint
    assert registry.context == fingerprint


def test_registry_refuses_a_second_reality(registry, frames):
    registry.bind_context(context_fingerprint(frames.resolve(COMPLETE)))
    with pytest.raises(ContextBindingViolation) as caught:
        registry.bind_context(context_fingerprint(frames.resolve(OTHER)))
    assert caught.value.detail["bound_to"] == COMPLETE
    assert caught.value.detail["offered"] == OTHER


def test_registry_refuses_a_binding_that_names_no_frame(registry):
    with pytest.raises(ContextBindingViolation):
        registry.bind_context({})
    with pytest.raises(ContextBindingViolation):
        registry.bind_context({"frame": "f"})
    assert not registry.is_context_bound


def test_an_unbound_registry_fails_closed_on_require_context(registry):
    with pytest.raises(ContextBindingViolation):
        registry.require_context()


def test_lineage_context_binding(registry, resolution):
    ledger = bind(registry, resolution)
    entries = ledger.entries(event=CONTEXT_BOUND)
    assert len(entries) == len(registry.subjects())
    assert ledger.is_intact()
    # deriving again from the bound registry reproduces the same ledger
    assert lineage.ledger_for(registry).digest() == ledger.digest()


def test_lineage_binding_is_idempotent(registry, resolution):
    ledger = bind(registry, resolution)
    head = ledger.head
    assert (
        bind_lineage(
            ledger, resolution, subjects=[(s.universal_id, s.key) for s in registry.subjects()]
        )
        == ()
    )
    assert ledger.head == head


def test_dictionary_context_projection(registry, resolution, frames):
    unbound = dictionary_for(registry)
    bind(registry, resolution)
    bound = dictionary_for(registry)
    assert len(bound) == len(unbound)
    assert bound.digest() != unbound.digest()
    frame_id = frames.frame(COMPLETE).universal_id
    for entry in bound.entries():
        assert entry.attributes["context_frame"] == COMPLETE
        assert frame_id in entry.lineage
    assert bound.is_verified


def test_evolution_requires_context(resolution):
    ledger = EvolutionLedger(validator=context_is_declared)
    with pytest.raises(EvolutionError) as caught:
        ledger.evolve(subject_id="UCOS-S", subject_key="s", change="c", authority="a")
    assert "reference frame" in str(caught.value)
    evolution = evolve_in_context(
        ledger, resolution, subject_id="UCOS-S", subject_key="s", change="c", authority="a"
    )
    assert evolution.state["context"]["frame"] == COMPLETE


def test_evolution_context_composes_with_the_domain_rule(resolution):
    ledger = EvolutionLedger(validator=all_of(context_is_declared, state_must_grow))
    evolve_in_context(
        ledger,
        resolution,
        subject_id="UCOS-S",
        subject_key="s",
        change="c1",
        authority="a",
        state={"capability": 3},
    )
    with pytest.raises(EvolutionError):
        evolve_in_context(
            ledger,
            resolution,
            subject_id="UCOS-S",
            subject_key="s",
            change="c2",
            authority="a",
            state={"capability": 1},
        )


def test_certification_requires_context(registry):
    with pytest.raises(CertificationError) as caught:
        certification.certify(registry, require_context=True)
    assert set(caught.value.detail["failures"]) == {g for g, _n, _s in CONTEXT_GATES}
    certificate = certification.certify(registry, frame_key=COMPLETE, require_context=True)
    assert certificate.certified and certificate.context_bound


def test_certification_carries_the_four_gates(registry):
    certificate = certification.certify(registry, frame_key=COMPLETE)
    gates = certificate.context_gates
    assert set(gates) == {g for g, _n, _s in CONTEXT_GATES}
    for gate in gates.values():
        assert gate["applicable"] is True
        assert gate["passed"] is True
    assert certificate.to_dict()["context_gates"]["CV-CONTEXT-01"]["name"] == "Context Bound"


def test_validation_reports_context_failures(registry, frames):
    """Each gate names what is wrong, rather than reporting a bare failure."""
    ledger = lineage.ledger_for(registry)
    gates = context_gates(frames, frame_key=COMPLETE, registry=registry, lineage=ledger)
    assert gates["CV-CONTEXT-01"]["passed"] is False
    assert gates["CV-CONTEXT-01"]["finding_count"] == len(registry.subjects()) + 1
    assert gates["CV-CONTEXT-01"]["findings"]
    # the other three hold: the frame itself resolves, verifies and is registered
    for gate in ("CV-CONTEXT-02", "CV-CONTEXT-03", "CV-CONTEXT-04"):
        assert gates[gate]["passed"] is True, gates[gate]["findings"]


def test_the_resolved_gate_fails_on_an_incomplete_frame(frames):
    gates = context_gates(frames, frame_key=INCOMPLETE)
    assert gates["CV-CONTEXT-02"]["passed"] is False
    assert gates["CV-CONTEXT-03"]["passed"] is False


def test_the_verified_gate_catches_a_forged_binding(registry, frames):
    ledger = bind(registry, frames.resolve(COMPLETE))
    ledger.record(
        CONTEXT_BOUND,
        subject_id="UCOS-NUC-forged",
        subject_key="forged",
        detail={"frame": COMPLETE, "resolution_digest": "not-the-real-digest"},
    )
    gates = context_gates(frames, frame_key=COMPLETE, registry=registry, lineage=ledger)
    assert gates["CV-CONTEXT-03"]["passed"] is False
    assert "does not reproduce" in gates["CV-CONTEXT-03"]["findings"][0]


def test_the_gates_are_inapplicable_without_a_frame(frames):
    for gate in context_gates(frames).values():
        assert gate["applicable"] is False
        assert gate["passed"] is True


def test_context_replay_is_deterministic(registry, resolution):
    subject = registry.nuclei()[0].universal_id
    replay = replay_in_context(subject, resolution)
    assert replay["fixed_point"] is True
    assert replay["chain_intact"] is True
    assert replay["context_bound"] is True
    assert replay["context"]["frame"] == COMPLETE
    assert replay == replay_in_context(subject, resolution)


def test_context_measurements_are_stable(frames):
    first = context_measurements(frames, frame_key=COMPLETE)
    second = context_measurements(frames, frame_key=COMPLETE)
    assert first == second
    assert content_hash(first) == content_hash(second)


def test_context_stage_function_is_deterministic(frames, resolution):
    subject = "UCOS-DETERMINISM"
    first = execute_in_context(subject, resolution)
    second = execute_in_context(subject, resolution)
    assert first.digest() == second.digest()
    assert first.context_bound and first.complete
    assert first.to_dict()["context"]["frame"] == COMPLETE
    # deterministic, but not constant: a different reality is a different record
    elsewhere = execute_in_context(subject, frames.resolve(OTHER))
    assert first.digest() != elsewhere.digest()


def test_the_verified_gate_catches_a_registry_bound_to_another_reality(registry, frames):
    """A FORGED LINEAGE ENTRY WAS TESTED AND THE REGISTRY'S OWN BINDING WAS NOT.

    ``bind`` writes the registry's binding and the lineage entries from one resolution, so
    the two always agree and this arm was dead. It is the case that matters most: the
    registry's binding is what every enforcing read resolves against, so a registry bound to
    ANOTHER frame than the one being verified would answer every question under a reality the
    certificate does not describe — and the lineage entries could all reproduce perfectly
    while it did.
    """
    ledger = bind(registry, frames.resolve(OTHER))

    gates = context_gates(frames, frame_key=COMPLETE, registry=registry, lineage=ledger)

    assert gates["CV-CONTEXT-03"]["passed"] is False
    assert any(
        "the registry's binding does not reproduce" in finding
        for finding in gates["CV-CONTEXT-03"]["findings"]
    )
