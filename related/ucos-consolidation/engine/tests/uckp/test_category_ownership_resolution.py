"""Measured reality against recognised resolution (`PHASE-UCF-013`).

`PHASE-UCF-011` built the measurement — which providers populate which category — and
could go no further, because the declared side did not exist to read: with no recognition
anywhere in the repository, a populated category could not be told apart from one whose
population anyone had agreed to. Every category collapsed into a single observation, and
the two scenarios that need a declaration were left unwritten rather than faked.

This module covers the join that closes that gap, in two halves.

**The reader** (:mod:`engine.uckp.resolution`) is general by construction: it knows what a
`*_resolution` section *is* and nothing about what any one says. Its tests hold it to
that — discovery by declared suffix rather than by a list, and three states where a naive
reader would have two, so an unreadable source can never be mistaken for one that
declares nothing.

**The join** (:meth:`~engine.uckp.intelligence.UniversalIntelligence.category_integrity`)
compares the two planes and asserts neither. Its tests hold the three states apart —
MATCH, CONFLICT, UNKNOWN — and hold UNKNOWN open: a 22nd category populated tomorrow by a
provider nobody has recognised must report UNKNOWN rather than pass by omission, which is
`PHASE-UCF-005`'s blind spot one layer up.

**The ledger** was written by `PHASE-UCF-015` and is now what the live tests at the foot of
this module read. The three states are still held apart by in-memory fixtures rather than
by the repository's own file, because a suite that could only construct the state its
repository happens to be in would stop being able to test the other two the moment the
file changed. What the live tests add is the pair of claims only the real file can make:
that every category this repository populates is recognised, and that the recognised side
is the measured side — recomputed on both sides, so a fifth provider fails it rather than
extending it.

Nothing here promotes anything. Every state is an OBSERVATION and certification is
indifferent to all of them: the ledger moved the stage from Observational to Advisory, and
a CONFLICT still reports rather than refuses. Promotion needs a plurality-versus-
contamination rule and a certification invariant, both deliberately still deferred.
"""

from __future__ import annotations

import json

import pytest

from engine.tests.uckp.doubles import RegistryView
from engine.uckp.alignment import ALIGNMENT_BINDING_PATH
from engine.uckp.errors import UCKPValidationError
from engine.uckp.identity import urn_for
from engine.uckp.intelligence import (
    ACCOUNTABLE_AUTHORITY,
    CATEGORY_EVIDENCE,
    CATEGORY_OWNERSHIP_RESOLUTION,
    CONFLICT,
    MATCH,
    OBSERVATION,
    RECOGNISED_POPULATORS,
    RECOGNITION_CATEGORY,
    RECOGNITIONS,
    UNKNOWN,
    CategoryRecognition,
    build_intelligence,
)
from engine.uckp.resolution import (
    ABSENT,
    PRESENT,
    RESOLUTION_SUFFIX,
    UNREADABLE,
    Resolution,
    ResolutionReader,
    binding_reader,
)

#: The statements the observational stage already made, which a declaration must retire
#: and an absent declaration must leave exactly as they were.
UNDECLARED = "an undeclared default, not a decision"
CONTAMINATION = "and no declared owner reconciles them"
#: What the join adds.
RECOGNISED = "every populator of it recognised by"
UNRECONCILED = "is not among the populators"
UNPOPULATED = "no object attributes it to any provider"
PLURALITY = "a recognised plurality is reconciled only where"
PROVIDER_AS_OWNER = "a provider is a discovery fact, never an owner"

AUTHORITY = "ucos-constitutional-authority"
#: The value the live ledger recognises as accountable for the governed-category value
#: space (`PHASE-UCF-014` D14-2) — the root law that owns the vocabulary and refuses every
#: value outside it, never a provider and never an object owner.
LAW = "UCKP-LAW-0001"


def _entry(category: str, *populators: str, authority: str = AUTHORITY) -> dict[str, object]:
    """One recognitive ledger entry: what populates the category, and who is accountable.

    Deliberately carries no object count, no measured provider list and no populated-
    category list — a ledger that restated a measurement would be a second truth, stale
    the day a provider mints one more object (`PHASE-UCF-012` D3).
    """
    return {
        RECOGNITION_CATEGORY: category,
        RECOGNISED_POPULATORS: list(populators),
        ACCOUNTABLE_AUTHORITY: authority,
    }


def _ledger(*entries: object, **overrides: object) -> ResolutionReader:
    """A reader over an in-memory binding declaring a category ownership resolution."""
    section: dict[str, object] = {
        "model": "RECOGNISED_POPULATION",
        "bounded_question": "which provider does each populated category already have?",
        RECOGNITIONS: list(entries),
        "second_populator_test": (
            "a second provider minting into a recognised category, measured by "
            "engine.uckp.intelligence.category_populations()"
        ),
    }
    section.update(overrides)
    return ResolutionReader.from_document(
        {CATEGORY_OWNERSHIP_RESOLUTION: section}, source="<ledger fixture>"
    )


def _gap(*objects, vocabularies, resolutions=None):
    view = RegistryView(objects, vocabularies=vocabularies)
    return build_intelligence(view, resolutions).reason("gap")


def _integrity(*objects, vocabularies, resolutions=None):
    view = RegistryView(objects, vocabularies=vocabularies)
    return build_intelligence(view, resolutions).category_integrity()


def _state(states, category: str):
    return next(state for state in states if state.category == category)


def _statements(result, category: str) -> str:
    subject = f"category:{category}"
    return "\n".join(f.statement for f in result.findings if f.subject == subject)


def _resolution_statements(result) -> str:
    subject = f"resolution:{CATEGORY_OWNERSHIP_RESOLUTION}"
    return "\n".join(f.statement for f in result.findings if f.subject == subject)


@pytest.fixture
def sole(mint_object):
    """One category, one populator: the shape 21 of this repository's categories have."""
    return mint_object(
        "SOLE", derives_from=urn_for("test", "ROOT"), category="runtime", provider="p.sole"
    )


# --- the reader: general over sections, never specific to one -----------------------


def test_the_reader_discovers_every_resolution_the_live_binding_declares():
    """Discovery is by declared suffix, so a seventh section needs no edit here.

    Measured against the real binding rather than a fixture: the claim is that this reader
    serves the sections that actually exist, and a list kept in the test would prove only
    that the test and the reader agree with each other.
    """
    names = binding_reader().names()
    assert names, "the live binding declares no resolution sections"
    assert all(name.endswith(RESOLUTION_SUFFIX) for name in names)
    assert names == tuple(sorted(names))
    assert "identity_authority_resolution" in names
    assert "existence_resolution" in names


def test_a_live_section_reads_as_present_with_its_body_verbatim():
    resolution = binding_reader().read("identity_authority_resolution")
    assert resolution.state == PRESENT
    assert resolution.present and resolution.readable
    assert "derivation" in resolution.body
    assert ALIGNMENT_BINDING_PATH in resolution.source


def test_the_four_sections_nothing_read_before_are_readable_now():
    """The reader was built for the seventh section and serves all of them.

    `PHASE-UCF-012 § 6.2` measured four of six sections with no machine reader anywhere in
    the repository. A capability built only for category ownership would have left them
    exactly as unread, which is how one file acquires six loaders.
    """
    reader = binding_reader()
    for name in (
        "existence_resolution",
        "lifecycle_resolution",
        "certification_authority_resolution",
        "identity_namespace_resolution",
    ):
        assert reader.read(name).state == PRESENT


def test_an_undeclared_section_reads_as_absent_not_as_a_failure():
    """Absence is a lawful state, and it must stay constructible after the write.

    Until `PHASE-UCF-015` the live binding was itself the fixture for this: the ledger did
    not exist, so reading it from the real file proved the state. It exists now, and the
    state it used to demonstrate is not thereby retired — a section no document declares
    must still read ABSENT rather than as a failure, because that is the state every
    resolution the repository has not written is in.
    """
    resolution = ResolutionReader.from_document({}, source="<no ledger>").read(
        CATEGORY_OWNERSHIP_RESOLUTION
    )
    assert resolution.state == ABSENT
    assert resolution.readable and not resolution.present
    assert resolution.body == {}
    assert CATEGORY_OWNERSHIP_RESOLUTION in resolution.detail


def test_the_live_section_reads_as_present_with_every_recognition_it_declares():
    """What `PHASE-UCF-015` wrote, read back through the production path."""
    resolution = binding_reader().read(CATEGORY_OWNERSHIP_RESOLUTION)
    assert resolution.state == PRESENT
    assert ALIGNMENT_BINDING_PATH in resolution.source
    entries = resolution.entries(RECOGNITIONS)
    assert entries and len(entries) == resolution.declared(RECOGNITIONS)
    assert all(entry[ACCOUNTABLE_AUTHORITY] == LAW for entry in entries)
    assert all(entry["basis"] for entry in entries), "every recognition cites a code location"


def test_an_absent_source_is_unreadable_rather_than_empty(tmp_path):
    """The distinction the third state exists for: no claim, versus an unchecked claim."""
    resolution = ResolutionReader.from_path(tmp_path / "nothing.json").read(
        CATEGORY_OWNERSHIP_RESOLUTION
    )
    assert resolution.state == UNREADABLE
    assert not resolution.readable
    assert "FileNotFoundError" in resolution.detail


def test_a_malformed_source_is_unreadable_rather_than_a_pass(tmp_path):
    path = tmp_path / "binding.json"
    path.write_text("{not json", encoding="utf-8")
    resolution = ResolutionReader.from_path(path).read(CATEGORY_OWNERSHIP_RESOLUTION)
    assert resolution.state == UNREADABLE
    assert "JSONDecodeError" in resolution.detail


def test_a_document_that_is_not_a_mapping_is_unreadable(tmp_path):
    path = tmp_path / "binding.json"
    path.write_text(json.dumps(["a", "list"]), encoding="utf-8")
    reader = ResolutionReader.from_path(path)
    assert reader.names() == ()
    assert reader.read(CATEGORY_OWNERSHIP_RESOLUTION).detail == "the document is not a mapping"


def test_a_section_declared_as_the_wrong_shape_is_unreadable():
    reader = ResolutionReader.from_document({CATEGORY_OWNERSHIP_RESOLUTION: ["recognitions"]})
    resolution = reader.read(CATEGORY_OWNERSHIP_RESOLUTION)
    assert resolution.state == UNREADABLE
    assert "not as a mapping" in resolution.detail


def test_the_reader_refuses_a_name_that_is_not_a_resolution_section():
    """A guard against becoming a second accessor for the binding's other 35 keys."""
    with pytest.raises(UCKPValidationError):
        binding_reader().read("supreme_authority")


def test_a_source_is_loaded_once_and_its_outcome_memoised():
    """Including a failure: an unreadable source reports identically on every read."""
    loads = []

    def _load():
        loads.append(1)
        raise OSError("gone")

    reader = ResolutionReader("<counted>", _load)
    first = reader.read(CATEGORY_OWNERSHIP_RESOLUTION)
    second = reader.read(CATEGORY_OWNERSHIP_RESOLUTION)
    assert reader.names() == ()
    assert first == second
    assert len(loads) == 1


def test_a_string_field_is_not_read_as_a_list_of_entries():
    """The guard that stops a mistyped field from iterating one character at a time."""
    reader = _ledger(**{RECOGNITIONS: "runtime"})
    resolution = reader.read(CATEGORY_OWNERSHIP_RESOLUTION)
    assert resolution.entries(RECOGNITIONS) == ()
    assert resolution.declared(RECOGNITIONS) == 0


def test_a_resolution_cites_its_own_name_state_and_source():
    resolution = Resolution("existence_resolution", PRESENT, "<somewhere>", {"model": {}})
    assert resolution.cite() == "existence_resolution (present) in <somewhere>"
    assert set(resolution.to_dict()) == {"name", "state", "source", "detail"}
    assert resolution.entries("absent_key") == ()


# --- MATCH: the declared populator is the measured populator ------------------------


def test_a_declared_populator_that_matches_the_measurement_reports_match(sole, vocabularies):
    """The positive case `PHASE-UCF-011` could not construct."""
    ledger = _ledger(_entry("runtime", "p.sole"))
    state = _state(_integrity(sole, vocabularies=vocabularies, resolutions=ledger), "runtime")
    assert state.state == MATCH
    assert state.measured == ("p.sole",)
    assert state.declared == ("p.sole",)
    assert state.unrecognised == () and state.unmeasured == ()


def test_a_match_is_reported_as_a_recognition_and_no_longer_as_undeclared(sole, vocabularies):
    """PASS must be *distinguishable* from UNKNOWN in the finding, not merely absent."""
    ledger = _ledger(_entry("runtime", "p.sole"))
    result = _gap(sole, vocabularies=vocabularies, resolutions=ledger)
    statements = _statements(result, "runtime")
    assert RECOGNISED in statements
    assert AUTHORITY in statements
    assert CATEGORY_OWNERSHIP_RESOLUTION in statements
    assert CATEGORY_EVIDENCE in statements
    assert UNDECLARED not in statements
    assert result.observations["categories_recognised"] == 1.0
    assert result.observations["categories_without_declared_owner"] == 0.0


def test_a_match_produces_no_violation(sole, vocabularies):
    result = _gap(sole, vocabularies=vocabularies, resolutions=_ledger(_entry("runtime", "p.sole")))
    assert result.violations == ()
    assert result.clean is True


def test_recognising_more_populators_than_are_measured_is_still_a_match(sole, vocabularies):
    """A recognition may anticipate a populator that has not minted yet.

    The comparison is containment, not equality: what must never happen is a *measured*
    provider nobody recognises. A recognised populator that has minted nothing is visible
    as `unmeasured` and is not, by itself, a divergence in the population.
    """
    ledger = _ledger(_entry("runtime", "p.sole", "p.future"))
    state = _state(_integrity(sole, vocabularies=vocabularies, resolutions=ledger), "runtime")
    assert state.state == MATCH
    assert state.unmeasured == ("p.future",)


# --- CONFLICT: the declaration and the measurement disagree -------------------------


def test_a_measured_provider_the_resolution_does_not_recognise_is_a_conflict(
    mint_object, vocabularies
):
    """The `PHASE-UCF-005` defect class, now with a declared side to contradict."""
    root = urn_for("test", "ROOT")
    native = mint_object("N", derives_from=root, category="metadata", provider="p.native")
    intruder = mint_object("I", derives_from=root, category="metadata", provider="p.intruder")
    ledger = _ledger(_entry("metadata", "p.native"))
    result = _gap(native, intruder, vocabularies=vocabularies, resolutions=ledger)
    statements = _statements(result, "metadata")
    assert UNRECONCILED in statements
    assert "p.intruder" in statements and "p.native" in statements
    assert AUTHORITY in statements
    assert result.observations["categories_ownership_conflict"] == 1.0


def test_a_conflict_names_both_the_measured_and_the_declared_side(mint_object, vocabularies):
    """A finding a reader cannot reproduce from both sides is an assertion."""
    obj = mint_object(
        "X", derives_from=urn_for("test", "ROOT"), category="policy", provider="p.actual"
    )
    ledger = _ledger(_entry("policy", "p.declared"))
    state = _state(_integrity(obj, vocabularies=vocabularies, resolutions=ledger), "policy")
    assert state.state == CONFLICT
    assert state.measured == ("p.actual",) and state.declared == ("p.declared",)
    assert state.unrecognised == ("p.actual",) and state.unmeasured == ("p.declared",)
    statement = _statements(_gap(obj, vocabularies=vocabularies, resolutions=ledger), "policy")
    assert "p.actual" in statement and "p.declared" in statement


def test_a_recognition_of_a_category_nothing_populates_is_a_conflict(sole, vocabularies):
    """Totality in the other direction (`PHASE-UCF-012` D6).

    The 14 governed-but-unpopulated categories get no entry, because there is no populator
    to recognise; an entry for one declares a right rather than recognising a standing. The
    comparison must therefore iterate the union of both sides — a join that only walked what
    it could measure would report having checked something it never looked at.
    """
    ledger = _ledger(_entry("runtime", "p.sole"), _entry("proof", "p.nobody"))
    states = _integrity(sole, vocabularies=vocabularies, resolutions=ledger)
    assert _state(states, "runtime").state == MATCH
    assert _state(states, "proof").state == CONFLICT
    assert UNPOPULATED in _statements(
        _gap(sole, vocabularies=vocabularies, resolutions=ledger), "proof"
    )


def test_a_category_whose_objects_name_no_provider_cannot_match_a_declaration(
    mint_object, vocabularies
):
    """An empty measured side is not a subset that passes.

    Nothing is attributed, so nothing can be compared; certifying the declaration anyway
    would be a pass reached by having no evidence rather than by having agreeing evidence.
    """
    import dataclasses

    obj = mint_object("NAMELESS", derives_from=urn_for("test", "ROOT"), category="runtime")
    nameless = dataclasses.replace(obj, discovery=dataclasses.replace(obj.discovery, provider=""))
    ledger = _ledger(_entry("runtime", "p.sole"))
    state = _state(_integrity(nameless, vocabularies=vocabularies, resolutions=ledger), "runtime")
    assert state.state == CONFLICT


# --- UNKNOWN: valid, permanent, and never silently upgraded -------------------------


def test_no_resolution_leaves_every_populated_category_unknown(sole, vocabularies):
    """The repository's live state, and the observational stage's statements unchanged."""
    result = _gap(sole, vocabularies=vocabularies, resolutions=_ledger())
    assert UNDECLARED in _statements(result, "runtime")
    assert result.observations["categories_ownership_unknown"] == 1.0
    assert result.observations["categories_recognised"] == 0.0


def test_an_absent_resolution_is_unknown_and_is_not_itself_reported(sole, vocabularies):
    """Absence is a recorded, deferred decision — not a finding to re-report each pass."""
    reader = ResolutionReader.from_document({}, source="<no ledger>")
    result = _gap(sole, vocabularies=vocabularies, resolutions=reader)
    assert _resolution_statements(result) == ""
    assert UNDECLARED in _statements(result, "runtime")


def test_a_category_no_entry_names_stays_unknown_beside_one_that_matches(mint_object, vocabularies):
    """The 22nd category, populated tomorrow by a provider nobody has recognised.

    UNKNOWN is permanent, not transitional (`PHASE-UCF-012` D7): if a complete backfill
    removed the state, every category invented after the ledger was written would pass by
    omission — `PHASE-UCF-005`'s blind spot, one layer up.
    """
    root = urn_for("test", "ROOT")
    declared = mint_object("D", derives_from=root, category="runtime", provider="p.sole")
    fresh = mint_object("F", derives_from=root, category="policy", provider="p.newcomer")
    ledger = _ledger(_entry("runtime", "p.sole"))
    states = _integrity(declared, fresh, vocabularies=vocabularies, resolutions=ledger)
    assert _state(states, "runtime").state == MATCH
    assert _state(states, "policy").state == UNKNOWN
    result = _gap(declared, fresh, vocabularies=vocabularies, resolutions=ledger)
    assert UNDECLARED in _statements(result, "policy")
    assert result.observations["categories_without_declared_owner"] == 1.0


def test_an_unreadable_resolution_is_reported_and_never_passes(sole, vocabularies, tmp_path):
    """Fail-closed on unreadable evidence (`PHASE-UCF-012` D12).

    A check that passed because it could not read its own evidence has "passed because it
    never looked". The finding says so, and every category stays UNKNOWN.
    """
    reader = ResolutionReader.from_path(tmp_path / "missing.json")
    result = _gap(sole, vocabularies=vocabularies, resolutions=reader)
    assert "could not be read" in _resolution_statements(result)
    assert result.observations["categories_ownership_unknown"] == 1.0
    assert result.observations["categories_recognised"] == 0.0
    assert result.violations == ()


# --- ledger defects: dropped and reported, never repaired or assumed ----------------


def test_an_entry_that_recognises_nothing_is_reported_and_leaves_its_category_unknown(
    sole, vocabularies
):
    ledger = _ledger({RECOGNITION_CATEGORY: "runtime", ACCOUNTABLE_AUTHORITY: AUTHORITY})
    result = _gap(sole, vocabularies=vocabularies, resolutions=ledger)
    assert "recognises nothing" in _resolution_statements(result)
    assert UNDECLARED in _statements(result, "runtime")


def test_an_entry_naming_no_accountable_authority_is_reported(sole, vocabularies):
    ledger = _ledger(_entry("runtime", "p.sole", authority=" "))
    result = _gap(sole, vocabularies=vocabularies, resolutions=ledger)
    assert ACCOUNTABLE_AUTHORITY in _resolution_statements(result)
    assert (
        _state(_integrity(sole, vocabularies=vocabularies, resolutions=ledger), "runtime").state
        == UNKNOWN
    )


def test_a_category_recognised_twice_resolves_to_no_recognition_at_all(sole, vocabularies):
    """Two entries claiming one category — the scenario that needed a declared side.

    An ambiguous declaration must not be arbitrated by read order. Dropping both is the
    one disposition that cannot turn a contradiction into a pass.
    """
    ledger = _ledger(_entry("runtime", "p.sole"), _entry("runtime", "p.other"))
    result = _gap(sole, vocabularies=vocabularies, resolutions=ledger)
    assert "more than once" in _resolution_statements(result)
    assert _resolution_statements(result).count("more than once") == 1
    assert (
        _state(_integrity(sole, vocabularies=vocabularies, resolutions=ledger), "runtime").state
        == UNKNOWN
    )


def test_an_entry_that_is_not_a_mapping_is_counted_and_reported(sole, vocabularies):
    ledger = _ledger("runtime", _entry("runtime", "p.sole"))
    result = _gap(sole, vocabularies=vocabularies, resolutions=ledger)
    assert "cannot be read as an entry" in _resolution_statements(result)


def test_a_declared_section_that_recognises_nothing_is_reported(sole, vocabularies):
    result = _gap(sole, vocabularies=vocabularies, resolutions=_ledger())
    assert f"states no {RECOGNITIONS}" in _resolution_statements(result)


# --- the three separations the resolution may not collapse --------------------------


def test_naming_a_measured_provider_as_the_accountable_authority_is_reported(sole, vocabularies):
    """Provider is not Owner (`PHASE-UCF-012` D5).

    Substituting the one for the other is exactly the move that let `PHASE-UCF-005`'s
    contamination through, and a ledger written that way would encode the defect into
    governance rather than catch it.
    """
    ledger = _ledger(_entry("runtime", "p.sole", authority="p.sole"))
    statements = _statements(_gap(sole, vocabularies=vocabularies, resolutions=ledger), "runtime")
    assert PROVIDER_AS_OWNER in statements


def test_a_provider_of_another_category_is_also_refused_as_an_authority(mint_object, vocabularies):
    """The substitution is the same whether or not the provider populates the category."""
    root = urn_for("test", "ROOT")
    here = mint_object("H", derives_from=root, category="runtime", provider="p.sole")
    elsewhere = mint_object("E", derives_from=root, category="policy", provider="p.other")
    ledger = _ledger(_entry("runtime", "p.sole", authority="p.other"))
    statements = _statements(
        _gap(here, elsewhere, vocabularies=vocabularies, resolutions=ledger), "runtime"
    )
    assert PROVIDER_AS_OWNER in statements


def test_a_recognised_plurality_is_reported_rather_than_closed(mint_object, vocabularies):
    """Recognition is not a disposal mechanism (`PHASE-UCF-012` D9).

    A ledger that simply listed both populators of a contested category would make the
    contamination finding disappear without anyone having reconciled anything. The state
    is MATCH — both populators *are* recognised — and the plurality still stands reported,
    because a reconciliation requires a declared bounded question per populator, which is
    a conflict rule this phase deliberately does not invent.
    """
    root = urn_for("test", "ROOT")
    left = mint_object("L", derives_from=root, category="metadata", provider="p.one")
    right = mint_object("R", derives_from=root, category="metadata", provider="p.two")
    ledger = _ledger(_entry("metadata", "p.one", "p.two"))
    result = _gap(left, right, vocabularies=vocabularies, resolutions=ledger)
    statements = _statements(result, "metadata")
    assert PLURALITY in statements
    # the UNKNOWN wording is retired — something *has* now been declared about it — and
    # the plurality is carried forward by the replacement rather than dropped with it
    assert CONTAMINATION not in statements
    assert result.observations["categories_multi_provider"] == 1.0
    assert result.observations["categories_recognised"] == 1.0


def test_the_comparison_infers_no_ownership_from_population(sole, vocabularies):
    """The measured side stays a discovery fact; only the ledger declares accountability."""
    state = _state(_integrity(sole, vocabularies=vocabularies, resolutions=_ledger()), "runtime")
    assert state.recognition is None
    assert state.to_dict()["accountable_authority"] == ""
    assert state.to_dict()["recognised_populators"] == []


# --- the evidence model: every finding reproducible from four things ----------------


def test_every_state_is_reproducible_from_the_measurement_and_the_record(sole, vocabularies):
    """Category identity, provider identity, population measurement, resolution record."""
    ledger = _ledger(_entry("runtime", "p.sole"))
    state = _state(_integrity(sole, vocabularies=vocabularies, resolutions=ledger), "runtime")
    reported = state.to_dict()
    assert reported["category"] == "runtime"
    assert reported["measured_populators"] == ["p.sole"]
    assert reported["recognised_populators"] == ["p.sole"]
    assert reported["accountable_authority"] == AUTHORITY
    assert reported["evidence"] == CATEGORY_EVIDENCE
    assert reported["resolution"] == CATEGORY_OWNERSHIP_RESOLUTION
    # recomputed from the two facets the evidence names, and the record alone
    measured = {sole.discovery.provider} if sole.taxonomy.category == "runtime" else set()
    assert measured == set(reported["measured_populators"])
    assert state.recognition.to_dict() == _entry("runtime", "p.sole")


def test_no_finding_carries_a_confidence_or_an_invented_artifact(sole, vocabularies):
    result = _gap(sole, vocabularies=vocabularies, resolutions=_ledger(_entry("runtime", "p.sole")))
    for finding in result.findings:
        assert set(finding.to_dict()) == {"reasoning", "severity", "subject", "statement"}
        assert "confidence" not in finding.statement


def test_every_state_reports_at_observation_severity(mint_object, vocabularies):
    """Advisory at every state, including CONFLICT: promotion is a separate decision."""
    root = urn_for("test", "ROOT")
    matched = mint_object("M", derives_from=root, category="runtime", provider="p.sole")
    conflicted = mint_object("C", derives_from=root, category="policy", provider="p.actual")
    unknown = mint_object("U", derives_from=root, category="state", provider="p.new")
    ledger = _ledger(_entry("runtime", "p.sole"), _entry("policy", "p.declared"))
    result = _gap(matched, conflicted, unknown, vocabularies=vocabularies, resolutions=ledger)
    assert result.observations["categories_recognised"] == 1.0
    assert result.observations["categories_ownership_conflict"] == 1.0
    assert result.observations["categories_ownership_unknown"] == 1.0
    assert all(f.severity == OBSERVATION for f in result.findings)
    assert result.violations == ()
    assert result.clean is True


def test_the_comparison_is_deterministic_and_category_sorted(mint_object, vocabularies):
    root = urn_for("test", "ROOT")
    left = mint_object("L", derives_from=root, category="runtime", provider="p.one")
    right = mint_object("R", derives_from=root, category="metadata", provider="p.two")
    ledger = _ledger(_entry("metadata", "p.two"), _entry("runtime", "p.one"))
    first = _integrity(left, right, vocabularies=vocabularies, resolutions=ledger)
    second = _integrity(right, left, vocabularies=vocabularies, resolutions=ledger)
    assert [s.category for s in first] == ["metadata", "runtime"]
    assert [s.to_dict() for s in first] == [s.to_dict() for s in second]
    assert (
        _gap(left, right, vocabularies=vocabularies, resolutions=ledger).to_dict()
        == _gap(right, left, vocabularies=vocabularies, resolutions=ledger).to_dict()
    )


# --- the live repository: the ledger written, and what it must keep true -------------


def test_the_live_repository_recognises_every_category_it_populates(universe):
    """What `PHASE-UCF-015` moved: 21 UNKNOWN became 21 MATCH, and nothing else changed.

    Stated against the *measured* count rather than the literal 21, so the assertion is a
    coverage claim rather than a snapshot: a category populated tomorrow raises the
    measured count and fails here until it is recognised deliberately, which is the
    permanence `PHASE-UCF-014` R4a requires. Conflict stays at zero because the two planes
    agree, not because nothing is compared.
    """
    gap = universe.intelligence().reason("gap")
    populated = gap.observations["categories_populated"]
    assert gap.observations["categories_recognised"] == populated
    assert gap.observations["category_recognitions"] == populated
    assert gap.observations["categories_ownership_unknown"] == 0.0
    assert gap.observations["categories_without_declared_owner"] == 0.0
    assert gap.observations["categories_ownership_conflict"] == 0.0
    assert gap.violations == ()
    assert gap.clean is True


def test_the_live_ledger_recognises_exactly_the_providers_the_registry_measures(universe):
    """The regression fixture `PHASE-UCF-010` (d) asked for, measured on both sides.

    Neither side is a literal. The measured side is recomputed here from the two facets
    `CATEGORY_EVIDENCE` names; the recognised side is read from the binding. A fifth
    provider that lands in an existing category fails this the moment it is discovered —
    which is `PHASE-UCF-005`'s defect with a declared side to contradict it — and a
    recognition of something nothing populates fails it from the other direction.
    """
    measured: dict[str, set[str]] = {}
    for obj in universe.registry.objects():
        measured.setdefault(obj.taxonomy.category, set()).add(obj.discovery.provider)
    entries = binding_reader().read(CATEGORY_OWNERSHIP_RESOLUTION).entries(RECOGNITIONS)
    recognised = {
        entry[RECOGNITION_CATEGORY]: set(entry[RECOGNISED_POPULATORS]) for entry in entries
    }
    assert recognised == measured
    assert universe.discovery.providers_found == tuple(
        sorted({provider for providers in measured.values() for provider in providers})
    )


def test_no_recognition_carries_a_copied_measurement(universe):
    """A recognition references a measurement; it never mirrors one (`PHASE-UCF-014` D14-4).

    The rule is not stylistic. The only two copied measurements in this binding are the
    only two facts in it that have since gone stale (`PHASE-UCF-014` §10.4), and 21 entries
    carrying 21 object counts would acquire that defect 21 times over, silently, because
    nothing recomputes them.
    """
    section = binding_reader().read(CATEGORY_OWNERSHIP_RESOLUTION)
    for entry in section.entries(RECOGNITIONS):
        assert set(entry) == {
            RECOGNITION_CATEGORY,
            RECOGNISED_POPULATORS,
            ACCOUNTABLE_AUTHORITY,
            "basis",
        }
        assert not any(isinstance(value, int | float) for value in entry.values())
    # and the ledger names no state of its own: the state is computed, never authored
    assert "recognitions" in section.body
    assert not {"conflict", "disposition", "resolution_state", "exceptions"} & set(section.body)


def test_the_live_universe_is_unchanged_by_the_capability(universe):
    """Four providers, no admission failure, and a certification indifferent to all of it."""
    from engine.uckp.validation import validate_universe

    assert universe.discovery.providers_found == (
        "engine.uckp.alignment",
        "engine.uckp.capabilities",
        "engine.uckp.constitution",
        "engine.uckp.uga_projection",
    )
    assert universe.discovery.failures == ()
    assert universe.discovery.objects_admitted == len(universe.objects())
    assert validate_universe(universe).certified is True
    assert universe.intelligence().report()["clean"] is True


def test_the_live_join_is_total_over_the_live_population(universe):
    """Total over the union of both sides, and no recognition names a category nothing has.

    The category lists agreeing is the second half of the claim: a recognition of an
    unpopulated category would appear here as an extra state the population does not have,
    and would report CONFLICT rather than passing unnoticed.
    """
    states = universe.intelligence().category_integrity()
    populations = universe.intelligence().category_populations()
    assert [s.category for s in states] == [p.category for p in populations]
    assert all(s.state == MATCH for s in states)
    assert all(s.recognition is not None for s in states)
    assert all(s.unrecognised == () and s.unmeasured == () for s in states)


def test_the_live_ledger_names_no_provider_as_an_owner(universe):
    """Provider ≠ Owner ≠ Authority, checked against the file the repository actually has.

    The accountable authority is the instrument that owns the governed-category vocabulary
    and refuses every value outside it, on every admission. Naming a measured provider
    instead would be the `PHASE-UCF-005` substitution written into governance rather than
    caught by it, and the reasoner reports it — so this asserts both the value and the
    silence of the finding that would fire if it were wrong.
    """
    entries = binding_reader().read(CATEGORY_OWNERSHIP_RESOLUTION).entries(RECOGNITIONS)
    authorities = {entry[ACCOUNTABLE_AUTHORITY] for entry in entries}
    assert authorities == {LAW}
    assert not authorities & set(universe.discovery.providers_found)
    gap = universe.intelligence().reason("gap")
    assert PROVIDER_AS_OWNER not in "\n".join(f.statement for f in gap.findings)


def test_reading_a_resolution_mutates_no_canonical_state(universe):
    """Article 15 permits the universe to reason about itself, not to change itself."""
    before_ids = universe.registry.ids()
    before_seal = universe.seal()
    universe.intelligence().category_integrity()
    universe.intelligence().reason("gap")
    assert universe.registry.ids() == before_ids
    assert universe.seal() == before_seal
    # the ledger is read, never written: the section is present, and reasoning over it
    # mints nothing — the population it recognises is the population it was written from
    assert binding_reader().read(CATEGORY_OWNERSHIP_RESOLUTION).state == PRESENT
    assert len(universe.registry.ids()) == universe.discovery.objects_admitted


def test_an_entry_naming_no_category_or_a_blank_populator_recognises_nothing(sole, vocabularies):
    """AN ENTRY IS READ AS A RECOGNITION OR AS NOTHING, AND EVERY FIELD CAN COST IT.

    The missing accountable authority was tested; the other two field checks were not. A
    category that is not a non-empty string names nothing to recognise, and a populator list
    holding a blank name recognises a provider with no identity — which would then "match" any
    provider whose name normalises to nothing. Both drop the entry rather than repairing it,
    and the position is reported so a reader can find the line: the reader is total and
    silent about WHY, because a complaint needs the entry's position and the reader does not
    have it.
    """
    for defective in (
        _entry("   ", "p.sole"),
        {**_entry("runtime", "p.sole"), RECOGNITION_CATEGORY: 7},
        _entry("runtime", "p.sole", "  "),
        {**_entry("runtime", "p.sole"), RECOGNISED_POPULATORS: []},
        {**_entry("runtime", "p.sole"), RECOGNISED_POPULATORS: "p.sole"},
    ):
        ledger = _ledger(defective)
        result = _gap(sole, vocabularies=vocabularies, resolutions=ledger)
        assert "recognises nothing" in _resolution_statements(result), defective
        assert (
            _state(_integrity(sole, vocabularies=vocabularies, resolutions=ledger), "runtime").state
            == UNKNOWN
        )


def test_a_category_recognised_three_times_is_still_complained_about_once(sole, vocabularies):
    """THE COMPLAINT IS ABOUT THE CATEGORY, NOT ABOUT EACH ENTRY THAT NAMES IT.

    Two entries claiming one category was tested, which reaches the guard on its first
    duplicate. A third reaches the arm that KEEPS QUIET: the category is already known to be
    ambiguous, and repeating the complaint per entry would make a declaration with twenty
    duplicates twenty times as loud about one fault. Every one of them is still dropped, so
    the disposition is unchanged however many there are.
    """
    ledger = _ledger(
        _entry("runtime", "p.sole"), _entry("runtime", "p.other"), _entry("runtime", "p.third")
    )

    result = _gap(sole, vocabularies=vocabularies, resolutions=ledger)

    assert _resolution_statements(result).count("more than once") == 1
    assert (
        _state(_integrity(sole, vocabularies=vocabularies, resolutions=ledger), "runtime").state
        == UNKNOWN
    )


def test_a_recognition_cites_itself_as_a_finding_may_quote_it(sole, vocabularies):
    """A FINDING THAT NAMES NO POPULATOR AND NO AUTHORITY IS UNACTIONABLE.

    The citation is the recognition's own rendering for use inside a finding — the declared
    populators and who answers for them — and nothing called it. Without it a reader is told
    that a category is recognised and not by whom, which is the half of the recognition that
    makes it reviewable.
    """
    recognition = CategoryRecognition("runtime", ("p.sole", "p.other"), AUTHORITY)

    assert recognition.cite() == f"[p.sole, p.other] accountable to {AUTHORITY}"
    assert recognition.recognises("p.sole") is True
    assert recognition.recognises("p.absent") is False


def test_a_reader_cites_the_source_it_read_from(tmp_path):
    """A RESOLUTION IS ONLY REVIEWABLE IF ITS SOURCE CAN BE NAMED.

    Every reader here is built with a source and none of them was ever asked for it. It is
    what a finding quotes so a reader can go and look: "<no ledger>" and a real path are
    different answers, and a finding that reports neither cannot be traced to the declaration
    it came from.
    """
    document = tmp_path / "binding.json"
    document.write_text("{}", encoding="utf-8")

    assert ResolutionReader.from_path(document).source == str(document)
    assert ResolutionReader.from_document({}, source="<no ledger>").source == "<no ledger>"
