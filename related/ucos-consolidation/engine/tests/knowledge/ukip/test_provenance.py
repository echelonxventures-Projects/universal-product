"""UKIP Part 05 — Knowledge Provenance: a chain that detects tampering without a copy.

Each step hashes its own content together with the digest of the step before it. That single
choice is the whole design: altering, reordering, inserting or deleting any step invalidates
every digest after it, so ``verify`` catches the tampering with nothing to compare against.
Tests that only appended steps and read them back would never exercise that — so the defect
cases here build genuinely corrupted chains, the way a corrupted chain would actually arrive:
by writing past the constructor that seals each step.

Ordering is enforced at ``append`` rather than checked later, so an out-of-order history cannot
be *constructed*. ``broken_links`` still detects one, because a chain can also arrive from a
document, and a document is not obliged to have come from ``append``.
"""

from __future__ import annotations

import pytest

from engine.knowledge.ukip.contracts import ProviderKind, SourceRef
from engine.knowledge.ukip.errors import ProvenanceError
from engine.knowledge.ukip.provenance import (
    GENESIS,
    PROVENANCE_STAGES,
    REQUIRED_STAGES,
    ProvenanceChain,
    ProvenanceLedger,
    ProvenanceStep,
    Stage,
    begin_chain,
)

from .conftest import make_source, make_unit


def step(
    stage: Stage = Stage.OBSERVED,
    *,
    actor: str = "test-actor",
    action: str = "observe",
    previous: str = GENESIS,
    source: SourceRef | None = None,
    payload_sha256: str = "",
    detail: str = "",
) -> ProvenanceStep:
    return ProvenanceStep(
        stage=stage,
        actor=actor,
        action=action,
        previous_sha256=previous,
        source=source,
        payload_sha256=payload_sha256,
        detail=detail,
    )


def chain(*stages: Stage, subject: str = "UKID-TEST") -> ProvenanceChain:
    """A well-formed chain carrying the supplied stages in order."""
    built = ProvenanceChain(subject=subject)
    for stage in stages:
        built = built.append(stage, actor="test-actor", action=stage.value)
    return built


def complete_chain(subject: str = "UKID-TEST") -> ProvenanceChain:
    """A chain carrying every required stage, grounded in a content-addressed source."""
    built = ProvenanceChain(subject=subject).append(
        Stage.OBSERVED, actor="p", action="observe", source=make_source()
    )
    for stage in (Stage.PROVIDED, Stage.CLASSIFIED, Stage.REGISTERED):
        built = built.append(stage, actor="p", action=stage.value)
    return built


def tampered(original: ProvenanceStep, **fields) -> ProvenanceStep:
    """A step whose sealed content was altered after construction, seal left stale.

    ``dataclasses.replace`` would re-run ``__post_init__`` and re-seal, producing a step that
    is internally consistent — the opposite of what a tamper test needs.
    """
    forged = ProvenanceStep(
        stage=original.stage,
        actor=original.actor,
        action=original.action,
        previous_sha256=original.previous_sha256,
        source=original.source,
        payload_sha256=original.payload_sha256,
        detail=original.detail,
    )
    for name, value in fields.items():
        object.__setattr__(forged, name, value)
    return forged


# ---------------------------------------------------------------------------
# Stage
# ---------------------------------------------------------------------------


def test_the_declared_stages_are_ordered_and_complete():
    assert PROVENANCE_STAGES == tuple(Stage)
    orders = [stage.order for stage in PROVENANCE_STAGES]
    assert orders == sorted(orders) == list(range(len(PROVENANCE_STAGES)))


def test_corroboration_is_not_required_because_a_single_source_is_not_a_defect():
    assert Stage.CORROBORATED not in REQUIRED_STAGES
    assert set(REQUIRED_STAGES) < set(PROVENANCE_STAGES)


def test_a_declared_stage_coerces_from_its_value():
    assert Stage.coerce("registered") is Stage.REGISTERED
    assert Stage.coerce(Stage.CERTIFIED.value) is Stage.CERTIFIED


def test_coerce_reads_declared_values_and_not_already_resolved_members():
    """Its one production caller reads a document, so a value is the only shape it is given.

    ``coerce`` resolves ``str(value)``, and a str-mixin enum member renders as ``Stage.X``
    rather than ``x`` — so passing an already-resolved member is refused rather than passed
    through. Pinned because it is surprising, not because it is wanted: the sibling helper in
    ``universal_foundation.nucleus`` accepts a member first, and a caller who assumed the same
    here would get a refusal naming a stage that plainly exists.
    """
    with pytest.raises(ProvenanceError):
        Stage.coerce(Stage.CERTIFIED)


def test_an_unknown_stage_is_refused_and_names_where_it_was_found():
    with pytest.raises(ProvenanceError) as exc:
        Stage.coerce("audited", context="step[3]")
    message = str(exc.value)
    assert "audited" in message
    assert "step[3]" in message


# ---------------------------------------------------------------------------
# ProvenanceStep
# ---------------------------------------------------------------------------


def test_a_step_cannot_exist_unsealed():
    """The digest is computed at construction, so there is no window in which it is absent."""
    built = step()
    assert len(built.step_sha256) == 64
    assert built.verify()


def test_the_seal_covers_the_previous_digest_and_therefore_binds_the_chain():
    first = step(previous=GENESIS)
    second = step(previous="a" * 64)
    assert first.step_sha256 != second.step_sha256


@pytest.mark.parametrize(
    "field", ("stage", "actor", "action", "previous_sha256", "payload_sha256", "detail")
)
def test_every_sealed_field_changes_the_digest(field):
    values = {
        "stage": Stage.PROVIDED,
        "actor": "somebody-else",
        "action": "forge",
        "previous_sha256": "b" * 64,
        "payload_sha256": "c" * 64,
        "detail": "altered",
    }
    baseline = step()
    altered = ProvenanceStep(
        stage=values["stage"] if field == "stage" else baseline.stage,
        actor=values["actor"] if field == "actor" else baseline.actor,
        action=values["action"] if field == "action" else baseline.action,
        previous_sha256=(
            values["previous_sha256"] if field == "previous_sha256" else baseline.previous_sha256
        ),
        payload_sha256=(
            values["payload_sha256"] if field == "payload_sha256" else baseline.payload_sha256
        ),
        detail=values["detail"] if field == "detail" else baseline.detail,
    )
    assert altered.step_sha256 != baseline.step_sha256


def test_the_cited_source_is_part_of_what_is_sealed():
    assert step(source=make_source()).step_sha256 != step().step_sha256


def test_a_step_whose_stage_is_not_a_declared_stage_is_refused():
    with pytest.raises(ProvenanceError) as exc:
        ProvenanceStep(stage="observed", actor="p", action="observe")
    assert "must be a Stage" in str(exc.value)


def test_a_step_with_no_actor_is_refused():
    """An unattributed step records that something happened but not that anyone did it."""
    with pytest.raises(ProvenanceError) as exc:
        step(actor="")
    assert "requires an actor" in str(exc.value)


def test_a_step_with_no_action_is_refused():
    with pytest.raises(ProvenanceError) as exc:
        step(action="")
    assert "requires an action" in str(exc.value)


@pytest.mark.parametrize("previous", ("", "abc", "0" * 63, "0" * 65))
def test_a_step_that_does_not_chain_from_a_real_digest_is_refused(previous):
    with pytest.raises(ProvenanceError) as exc:
        step(previous=previous)
    assert "64-character sha256" in str(exc.value)


def test_a_tampered_step_no_longer_verifies():
    assert not tampered(step(), detail="altered after sealing").verify()


def test_a_step_round_trips_through_its_projection():
    original = step(source=make_source(), payload_sha256="d" * 64, detail="observed here")
    assert ProvenanceStep.from_dict(original.to_dict()) == original
    assert ProvenanceStep.from_dict(original.to_dict()).step_sha256 == original.step_sha256


def test_a_step_document_that_is_not_an_object_is_refused():
    with pytest.raises(ProvenanceError) as exc:
        ProvenanceStep.from_dict(["observed"])
    assert "must be an object" in str(exc.value)


def test_a_step_document_may_omit_its_optional_fields():
    rebuilt = ProvenanceStep.from_dict({"stage": "observed", "actor": "p", "action": "observe"})
    assert rebuilt.previous_sha256 == GENESIS
    assert rebuilt.source is None
    assert rebuilt.payload_sha256 == ""
    assert rebuilt.verify()


def test_a_step_document_carrying_a_digest_that_does_not_match_is_refused():
    """Reading a tampered document must fail loudly, not silently re-seal it as authentic."""
    document = step(detail="original").to_dict()
    document["detail"] = "altered in transit"
    with pytest.raises(ProvenanceError) as exc:
        ProvenanceStep.from_dict(document)
    message = str(exc.value)
    assert "does not match its content" in message
    assert document["step_sha256"] in message


def test_a_step_document_with_no_recorded_digest_is_sealed_on_read():
    document = step().to_dict()
    document.pop("step_sha256")
    assert ProvenanceStep.from_dict(document).verify()


# ---------------------------------------------------------------------------
# ProvenanceChain — construction
# ---------------------------------------------------------------------------


def test_an_empty_chain_seals_to_genesis():
    empty = ProvenanceChain(subject="UKID-TEST")
    assert empty.head == empty.seal == GENESIS
    assert len(empty) == 0
    assert empty.verify()


def test_each_appended_step_chains_from_the_one_before_it():
    built = chain(Stage.OBSERVED, Stage.PROVIDED, Stage.CLASSIFIED)
    assert built.steps[0].previous_sha256 == GENESIS
    assert built.steps[1].previous_sha256 == built.steps[0].step_sha256
    assert built.steps[2].previous_sha256 == built.steps[1].step_sha256
    assert built.seal == built.steps[-1].step_sha256
    assert len(built) == 3


def test_appending_returns_a_new_chain_and_leaves_the_original_alone():
    """Append-only means the previous chain is still exactly what it was."""
    original = chain(Stage.OBSERVED)
    extended = original.append(Stage.PROVIDED, actor="p", action="provide")
    assert len(original) == 1
    assert len(extended) == 2
    assert extended.steps[0] == original.steps[0]


def test_a_stage_may_repeat_because_a_thing_can_happen_twice():
    built = chain(Stage.CORROBORATED, Stage.CORROBORATED)
    assert built.stages() == (Stage.CORROBORATED, Stage.CORROBORATED)
    assert built.verify()


def test_stages_may_not_go_backwards():
    """An out-of-order history cannot be constructed in the first place."""
    built = chain(Stage.REGISTERED)
    with pytest.raises(ProvenanceError) as exc:
        built.append(Stage.OBSERVED, actor="p", action="observe")
    message = str(exc.value)
    assert "may not go backwards" in message
    assert "registered" in message and "observed" in message


def test_the_chain_is_deterministic_and_carries_no_wall_clock():
    """The same observation always produces the same seal."""
    assert chain(Stage.OBSERVED, Stage.PROVIDED).seal == chain(Stage.OBSERVED, Stage.PROVIDED).seal


# ---------------------------------------------------------------------------
# ProvenanceChain — queries
# ---------------------------------------------------------------------------


def test_the_chain_reports_the_stages_it_carries():
    built = chain(Stage.OBSERVED, Stage.PROVIDED)
    assert built.stages() == (Stage.OBSERVED, Stage.PROVIDED)
    assert built.has_stage(Stage.OBSERVED)
    assert not built.has_stage(Stage.CERTIFIED)


def test_the_first_step_recorded_for_a_stage_is_the_one_returned():
    built = ProvenanceChain(subject="UKID-TEST")
    built = built.append(Stage.CORROBORATED, actor="first", action="corroborate")
    built = built.append(Stage.CORROBORATED, actor="second", action="corroborate")
    assert built.step_for(Stage.CORROBORATED).actor == "first"


def test_a_stage_the_chain_never_recorded_has_no_step():
    assert chain(Stage.OBSERVED).step_for(Stage.CERTIFIED) is None
    assert ProvenanceChain(subject="UKID-TEST").step_for(Stage.OBSERVED) is None


def test_sources_are_reported_once_each_in_first_seen_order():
    first = make_source(provider_id="alpha", locator="a.md")
    second = make_source(provider_id="beta", locator="b.md")
    built = ProvenanceChain(subject="UKID-TEST")
    built = built.append(Stage.OBSERVED, actor="alpha", action="observe", source=first)
    built = built.append(Stage.PROVIDED, actor="alpha", action="provide", source=first)
    built = built.append(Stage.CORROBORATED, actor="beta", action="corroborate", source=second)
    assert [s.citation for s in built.sources()] == [first.citation, second.citation]


def test_a_chain_citing_no_source_reports_none():
    assert chain(Stage.OBSERVED).sources() == ()


def test_actors_are_reported_once_each_in_first_seen_order():
    built = ProvenanceChain(subject="UKID-TEST")
    built = built.append(Stage.OBSERVED, actor="alpha", action="observe")
    built = built.append(Stage.PROVIDED, actor="alpha", action="provide")
    built = built.append(Stage.CLASSIFIED, actor="beta", action="classify")
    assert built.actors() == ("alpha", "beta")
    assert ProvenanceChain(subject="UKID-TEST").actors() == ()


def test_a_missing_required_stage_is_a_detectable_gap_never_a_silent_omission():
    built = chain(Stage.OBSERVED, Stage.PROVIDED)
    assert built.missing_stages() == (Stage.CLASSIFIED, Stage.REGISTERED)
    assert not built.is_complete


def test_a_chain_carrying_every_required_stage_is_complete():
    built = complete_chain()
    assert built.missing_stages() == ()
    assert built.is_complete


def test_a_chain_is_grounded_only_by_a_content_addressed_source():
    """A citation with no digest names where knowledge was read, not what was read."""
    digestless = SourceRef(provider_id="p", kind=ProviderKind.DOCUMENT, locator="a.md")
    ungrounded = ProvenanceChain(subject="UKID-TEST").append(
        Stage.OBSERVED, actor="p", action="observe", source=digestless
    )
    grounded = ProvenanceChain(subject="UKID-TEST").append(
        Stage.OBSERVED, actor="p", action="observe", source=make_source()
    )
    assert not ungrounded.is_grounded
    assert grounded.is_grounded
    assert not chain(Stage.OBSERVED).is_grounded


# ---------------------------------------------------------------------------
# ProvenanceChain — tamper detection
# ---------------------------------------------------------------------------


def test_an_intact_chain_reports_no_defect():
    built = complete_chain()
    assert built.broken_links() == ()
    assert built.verify()
    built.require_intact()  # raises nothing


def test_altering_a_step_is_detected_as_a_digest_mismatch():
    built = chain(Stage.OBSERVED, Stage.PROVIDED)
    forged = tampered(built.steps[0], detail="altered after sealing")
    broken = ProvenanceChain(subject=built.subject, steps=(forged, built.steps[1]))
    defects = broken.broken_links()
    assert any("digest-mismatch" in defect for defect in defects)
    assert not broken.verify()


def test_deleting_a_step_breaks_every_link_after_it():
    """This is the property that removes the need for a copy of the original."""
    built = chain(Stage.OBSERVED, Stage.PROVIDED, Stage.CLASSIFIED)
    without_middle = ProvenanceChain(subject=built.subject, steps=(built.steps[0], built.steps[2]))
    defects = without_middle.broken_links()
    assert any("broken-link" in defect for defect in defects)
    assert not without_middle.verify()


def test_inserting_a_step_breaks_the_chain():
    built = chain(Stage.OBSERVED, Stage.PROVIDED)
    interloper = step(Stage.PROVIDED, actor="intruder", action="insert", previous=GENESIS)
    spliced = ProvenanceChain(
        subject=built.subject, steps=(built.steps[0], interloper, built.steps[1])
    )
    assert not spliced.verify()
    assert any("broken-link" in defect for defect in spliced.broken_links())


def test_reordering_steps_is_detected_as_out_of_order():
    """append refuses to build one, but a chain read from a document is not obliged to."""
    early = step(Stage.OBSERVED, actor="p", action="observe")
    late = step(Stage.REGISTERED, actor="p", action="register", previous=early.step_sha256)
    reversed_chain = ProvenanceChain(subject="UKID-TEST", steps=(late, early))
    defects = reversed_chain.broken_links()
    assert any("out-of-order" in defect for defect in defects)
    assert not reversed_chain.verify()


def test_a_defect_names_the_position_and_the_stage_it_was_found_at():
    built = chain(Stage.OBSERVED, Stage.PROVIDED)
    forged = tampered(built.steps[1], detail="altered")
    broken = ProvenanceChain(subject=built.subject, steps=(built.steps[0], forged))
    assert broken.broken_links()[0].startswith("step[1]:provided:")


def test_requiring_an_intact_chain_raises_on_a_broken_one():
    built = chain(Stage.OBSERVED)
    forged = tampered(built.steps[0], step_sha256="f" * 64)
    broken = ProvenanceChain(subject="UKID-TEST", steps=(forged,))
    with pytest.raises(ProvenanceError) as exc:
        broken.require_intact()
    assert "integrity check failed" in str(exc.value)


# ---------------------------------------------------------------------------
# ProvenanceChain — projection
# ---------------------------------------------------------------------------


def test_a_chain_round_trips_through_its_projection():
    original = complete_chain()
    assert ProvenanceChain.from_dict(original.to_dict()) == original
    assert ProvenanceChain.from_dict(original.to_dict()).seal == original.seal


def test_the_chain_projection_states_what_it_carries_and_what_it_lacks():
    payload = chain(Stage.OBSERVED, Stage.PROVIDED).to_dict()
    assert payload["length"] == 2
    assert payload["complete"] is False
    assert payload["grounded"] is False
    assert payload["stages"] == ["observed", "provided"]
    assert payload["missing_stages"] == ["classified", "registered"]


def test_a_chain_document_that_is_not_an_object_is_refused():
    with pytest.raises(ProvenanceError) as exc:
        ProvenanceChain.from_dict([{"stage": "observed"}])
    assert "must be an object" in str(exc.value)


def test_a_chain_document_whose_steps_are_not_an_array_is_refused():
    with pytest.raises(ProvenanceError) as exc:
        ProvenanceChain.from_dict({"subject": "UKID-TEST", "steps": {"stage": "observed"}})
    assert "must be an array" in str(exc.value)


def test_a_chain_document_with_no_steps_reads_as_an_empty_chain():
    assert len(ProvenanceChain.from_dict({"subject": "UKID-TEST"})) == 0


def test_a_chain_document_whose_links_are_broken_is_refused_on_read():
    """Reading is where a tampered chain must be caught, because reading is how it arrives."""
    built = chain(Stage.OBSERVED, Stage.PROVIDED, Stage.CLASSIFIED)
    document = built.to_dict()
    del document["steps"][1]
    with pytest.raises(ProvenanceError) as exc:
        ProvenanceChain.from_dict(document)
    assert "integrity check failed" in str(exc.value)


# ---------------------------------------------------------------------------
# begin_chain
# ---------------------------------------------------------------------------


def test_a_chain_opens_at_the_source_it_was_read_from():
    """A record can never exist without a reproducible origin (UKIP-LAW-004)."""
    unit = make_unit("a")
    built = begin_chain(unit)
    assert built.subject == unit.knowledge_id()
    assert built.stages() == (Stage.OBSERVED, Stage.PROVIDED)
    assert built.step_for(Stage.OBSERVED).payload_sha256 == unit.source.content_sha256
    assert built.step_for(Stage.PROVIDED).payload_sha256 == unit.unit_sha256()
    assert built.step_for(Stage.PROVIDED).detail == "unit:a"
    assert built.is_grounded
    assert built.verify()


def test_a_chain_may_be_opened_under_an_explicit_subject():
    built = begin_chain(make_unit("a"), subject="UKID-EXPLICIT")
    assert built.subject == "UKID-EXPLICIT"


# ---------------------------------------------------------------------------
# ProvenanceLedger
# ---------------------------------------------------------------------------


def test_a_ledger_holds_one_chain_per_subject():
    ledger = ProvenanceLedger([complete_chain("A"), complete_chain("B")])
    assert len(ledger) == 2
    assert ledger.subjects() == ("A", "B")
    assert "A" in ledger
    assert "NOBODY" not in ledger


def test_get_reports_an_unrecorded_subject_as_absent():
    assert ProvenanceLedger().get("NOBODY") is None
    assert ProvenanceLedger([complete_chain("A")]).get("A").subject == "A"


def test_require_refuses_a_subject_with_no_recorded_provenance():
    with pytest.raises(ProvenanceError) as exc:
        ProvenanceLedger().require("NOBODY")
    assert "no provenance recorded" in str(exc.value)


def test_require_returns_a_recorded_chain():
    recorded = complete_chain("A")
    assert ProvenanceLedger([recorded]).require("A") is recorded


def test_putting_a_chain_records_or_replaces_it():
    ledger = ProvenanceLedger()
    assert ledger.put(chain(Stage.OBSERVED, subject="A")) is ledger
    assert len(ledger.require("A")) == 1
    ledger.put(complete_chain("A"))
    assert len(ledger.require("A")) == 4


def test_appending_creates_the_chain_when_the_subject_is_new():
    ledger = ProvenanceLedger()
    updated = ledger.append("A", Stage.OBSERVED, actor="p", action="observe")
    assert updated.subject == "A"
    assert ledger.require("A") is updated


def test_appending_extends_an_existing_chain():
    ledger = ProvenanceLedger([chain(Stage.OBSERVED, subject="A")])
    updated = ledger.append("A", Stage.PROVIDED, actor="p", action="provide")
    assert updated.stages() == (Stage.OBSERVED, Stage.PROVIDED)
    assert updated.verify()


def test_chains_are_returned_in_subject_order_never_insertion_order():
    ledger = ProvenanceLedger([complete_chain("Z"), complete_chain("A")])
    assert [c.subject for c in ledger.chains()] == ["A", "Z"]


def test_the_ledger_names_every_subject_whose_chain_is_incomplete():
    ledger = ProvenanceLedger([complete_chain("A"), chain(Stage.OBSERVED, subject="B")])
    assert ledger.incomplete() == ("B",)


def test_the_ledger_names_every_subject_whose_chain_is_broken():
    intact = complete_chain("A")
    built = chain(Stage.OBSERVED, subject="B")
    forged = tampered(built.steps[0], detail="altered")
    ledger = ProvenanceLedger([intact, ProvenanceChain(subject="B", steps=(forged,))])
    assert ledger.broken() == ("B",)


def test_the_ledger_names_every_subject_with_no_content_addressed_source():
    ledger = ProvenanceLedger([complete_chain("A"), chain(Stage.OBSERVED, subject="B")])
    assert ledger.ungrounded() == ("B",)


def test_the_ledger_seal_is_deterministic_and_moves_when_any_chain_does():
    first = ProvenanceLedger([complete_chain("A")])
    assert first.seal() == ProvenanceLedger([complete_chain("A")]).seal()
    first.append("A", Stage.CERTIFIED, actor="p", action="certify")
    assert first.seal() != ProvenanceLedger([complete_chain("A")]).seal()


def test_the_ledger_projection_reports_its_population_and_its_defects():
    ledger = ProvenanceLedger([complete_chain("A"), chain(Stage.OBSERVED, subject="B")])
    payload = ledger.to_dict()
    assert payload["count"] == 2
    assert payload["seal"] == ledger.seal()
    assert payload["incomplete"] == ["B"]
    assert payload["broken"] == []
    assert payload["ungrounded"] == ["B"]
    assert [c["subject"] for c in payload["chains"]] == ["A", "B"]
