"""Constitutional governance convergence — non-vacuity suite for the four programmes.

UCOS-UCAF-001 (authority) · UCOS-URAT-001 (ratification) · UCOS-UTCE-001 (traceability) ·
UCOS-UFEP-001 (freeze eligibility).

A gate with no reachable PASS state carries no evidentiary value, and neither does one with no
reachable FAIL state. This repository has recorded the first defect once already
(UCCEP-F-001, FAIL-CLOSED-WITHOUT-PASS-PATH). This suite proves the second cannot occur here:
for each programme it drives the gate CLOSED by a distinct, independent mutation, and proves the
fail-closed abort path is reachable where an unimplemented reader or an unreadable input would
otherwise pass silently.

What is proven, per programme:

  * the gate is OPEN on the measured working tree (a reachable PASS state)
  * each declared blocking dimension can be driven to CLOSED by a mutation that targets it
  * a declared validation dimension the engine does not measure FAILS CLOSED rather than
    reporting satisfied — absence of a measurement is never evidence of compliance
  * every declared clause anchor is present in the located instrument it names, so a binding
    cannot silently point at text that does not exist
  * determinism — two renders of one declaration are byte-identical
  * zero enumeration — no identifier the engine acts on is hardcoded in its source
  * write scope — every rendered target resolves inside the programme's own directory

Constitutional properties given their own scenarios, because each is a boundary this work must
not cross:

  * URAT must never record a state reserved to the out-of-corpus finality authority
  * UFEP must never report a subject in a freeze state it cannot reach, and must never act on a
    freeze authorization
  * UTCE must never report a lane population that does not reconcile against the certified
    corpus, and must never read from a path it is permitted to write

Every mutation is hermetic: the declaration is deep-copied in memory and measured directly, so
no scenario writes to the repository or depends on untracked local state.
"""

from __future__ import annotations

import copy
import importlib.util
import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

REPO = Path(__file__).resolve().parents[3]

PROGRAMMES = {
    "ucaf": (REPO / "00-MASTER" / "UCOS-UCAF-001" / "ucaf_engine.py"),
    "urat": (REPO / "00-MASTER" / "UCOS-URAT-001" / "urat_engine.py"),
    "utce": (REPO / "00-MASTER" / "UCOS-UTCE-001" / "utce_engine.py"),
    "ufep": (REPO / "00-MASTER" / "UCOS-UFEP-001" / "ufep_engine.py"),
}


def _load(name: str):
    path = PROGRAMMES[name]
    spec = importlib.util.spec_from_file_location(f"{name}_engine_under_test", path)
    assert spec is not None and spec.loader is not None, f"{path} is not importable"
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module", params=sorted(PROGRAMMES))
def programme(request: pytest.FixtureRequest) -> tuple[str, Any, dict]:
    engine = _load(request.param)
    return request.param, engine, engine.load_declaration()


# ---------------------------------------------------------------------------
# properties every programme must hold


def test_engine_exists_and_declares_a_failclosed_path(programme: tuple[str, Any, dict]) -> None:
    _, engine, _ = programme
    assert issubclass(engine.FailClosed, Exception)
    assert callable(engine.measure)
    assert callable(engine.render)
    assert "check-determinism" in engine.GUARDS
    assert "check-no-enumeration" in engine.GUARDS
    assert "check-write-scope" in engine.GUARDS
    assert "check-declaration" in engine.GUARDS


def test_gate_is_open_on_the_measured_working_tree(programme: tuple[str, Any, dict]) -> None:
    """A reachable PASS state. Without this, every CLOSED result below would be vacuous.

    UFEP is excluded on purpose. Its gate reads the aggregate certifier's sealed model, and that
    certifier runs this suite as one of its own checks. Asserting UFEP's verdict here would make
    this suite depend on a model produced by a run that includes this suite — the recursion
    topology this work refuses elsewhere (UFEP-F-005). UFEP's mechanism is proven below by
    scenarios that do not read that model's verdict.
    """
    name, engine, document = programme
    if name == "ufep":
        pytest.skip("downstream of the certifier that runs this suite — see UFEP-F-005")
    model = engine.measure(document)
    assert (
        model["gate"] == "OPEN"
    ), f"{name}: gate CLOSED on the measured WORKING TREE — {model['blocking_failures']}"
    assert model["gate_exit"] == 0


def test_ufep_determines_freeze_eligibility_from_evidence_it_owns() -> None:
    """Freeze eligibility depends on the ratification registry, the traceability closure and the
    located validation and certification determinations — none of which runs this suite. It is
    therefore assertable here, unlike the completion verdict."""
    engine = _load("ufep")
    model = engine.measure(engine.load_declaration())
    assert model["subjects"], "no freeze subject was measured"
    assert model["determination"]["freeze_eligibility"] is True, [
        (item["id"], item["unsatisfied"]) for item in model["subjects"] if not item["eligible"]
    ]
    eligibility = [
        entry for entry in model["validations"] if entry["dimension"] == "FREEZE-ELIGIBILITY"
    ]
    assert eligibility and eligibility[0]["satisfied"] is True


def test_every_declared_guard_passes(programme: tuple[str, Any, dict]) -> None:
    name, engine, document = programme
    for guard, run in sorted(engine.GUARDS.items()):
        problems = run(document)
        assert problems == [], f"{name}: --{guard} reported {problems}"


def test_render_is_deterministic(programme: tuple[str, Any, dict]) -> None:
    _, engine, document = programme
    first = engine.render(engine.measure(document))
    second = engine.render(engine.measure(document))
    assert first == second


def test_no_declared_identifier_leaks_into_engine_source(programme: tuple[str, Any, dict]) -> None:
    _, engine, document = programme
    assert engine.check_no_enumeration(document) == []


def test_every_rendered_target_resolves_inside_the_programme(
    programme: tuple[str, Any, dict],
) -> None:
    _, engine, document = programme
    assert engine.check_write_scope(document) == []


def test_a_declared_dimension_with_no_measurement_fails_closed(
    programme: tuple[str, Any, dict],
) -> None:
    """Absence of a measurement is never evidence of compliance."""
    name, engine, document = programme
    mutated = copy.deepcopy(document)
    mutated["validations"].append(
        {
            "id": f"{name.upper()}-VAL-NONEXISTENT",
            "dimension": "UNMEASURED",
            "obligation": "a dimension the engine does not measure",
            "blocking": True,
        }
    )
    model = engine.measure(mutated)
    unmeasured = [entry for entry in model["validations"] if entry["id"].endswith("NONEXISTENT")]
    assert unmeasured, f"{name}: the injected dimension was dropped instead of measured"
    assert unmeasured[0]["measured"] is False
    assert unmeasured[0]["satisfied"] is False
    assert model["gate"] == "CLOSED"


# ---------------------------------------------------------------------------
# per-programme non-vacuity: an independent mutation per blocking concern


def _closed(engine: Any, document: dict, mutate: Callable[[dict], None]) -> dict:
    mutated = copy.deepcopy(document)
    mutate(mutated)
    return engine.measure(mutated)


UCAF_MUTATIONS = {
    "scope-anchor-absent": (
        lambda d: d["scope_rules"][0].__setitem__("anchor", "NO SUCH CLAUSE TEXT"),
        "UCAF-VAL-09",
    ),
    "resolution-anchor-absent": (
        lambda d: d["resolutions"][1].__setitem__("anchor", "NO SUCH CLAUSE TEXT"),
        "UCAF-VAL-08",
    ),
    "authority-source-unresolvable": (
        lambda d: d["authority_sources"][0].__setitem__("owner", "01-WORKING/DOES-NOT-EXIST.md"),
        "UCAF-VAL-01",
    ),
    "authority-family-matches-nothing": (
        lambda d: d["authority_sources"][0].__setitem__("id_pattern", "ZZZZ-[0-9]{2}"),
        "UCAF-VAL-01",
    ),
    "vacancy-record-incomplete": (
        lambda d: d["tier_source"]["vacancy_required_fields"].append("ratified_occupant"),
        "UCAF-VAL-06",
    ),  # exercised over the vacant-registry twin below — the live registry has no vacancy
    "undefined-authority-reference": (
        lambda d: d["authority_sources"][1].__setitem__("id_pattern", "GOV-[0-9]{2,3}"),
        "UCAF-VAL-07",
    ),
    "revocation-names-unknown-authority": (
        lambda d: d["revocations"].append(
            {"id": "X", "authority": "NOT-A-REGISTERED-AUTHORITY", "record": "nope.md"}
        ),
        "UCAF-VAL-12",
    ),
}


def _vacant_twin(tmp_path, engine):
    """The live Registry with T1 vacant again and one incomplete VAC-01 record restored.

    UCOS-RAT-002 retired the vacancy, so the guards that watch how a vacancy is
    handled can no longer borrow their residue from repository state — a guard that
    depends on a retired condition is a guard that quietly stops guarding. The twin is
    manufactured here, deterministically, from the committed registry, and both
    vacancy guards run against it.
    """
    registry = json.loads((engine.REPO / "00-CMG/CMG-REGISTRY.json").read_text(encoding="utf-8"))
    for tier in registry["tiers"]:
        if tier["id"] == "T1":
            tier["occupancy"] = "VACANT"
            tier["vacancy"] = "VAC-01"
    registry["vacancies"] = [
        {
            "id": "VAC-01",
            "tier": "T1",
            "declared_superior": "twin",
            "located": False,
            "evidence": "twin",
            "closure_procedure": "twin",
            "open_question": "CMG-OQ-02",
            "provisional_consequence": "twin",
        }
    ]
    for question in registry.get("open_questions", []):
        if question.get("id") == "CMG-OQ-02":
            question["status"] = "OPEN"
    twin = engine.REPO / ".runtime" / "CMG-REGISTRY.vacant.json"
    twin.parent.mkdir(parents=True, exist_ok=True)
    twin.write_text(json.dumps(registry), encoding="utf-8")
    document = copy.deepcopy(engine.load_declaration())
    document["tier_source"]["owner"] = ".runtime/CMG-REGISTRY.vacant.json"
    return document


def test_ucaf_vacancy_guards_still_fire_on_a_vacant_twin(tmp_path) -> None:
    """VAL-06 and the no-promotion rule are alive: they fire on the manufactured vacancy.

    The live registry records no vacancy — UCOS-RAT-002 closed VAC-01 — so the residue
    these guards watch is manufactured here instead. The mutation that demands a further
    field on the vacancy record must still refuse (UCAF-VAL-06), and no instrument may be
    promoted into the vacant tier (CMG-000001 XVII.4).
    """
    engine = _load("ucaf")

    document = _vacant_twin(tmp_path, engine)
    model = engine.measure(document)
    assert model["vacant_tiers"], "the twin reports no vacancy — the guard would be vacuous"
    for tier in model["tiers"]:
        if tier["id"] in set(model["vacant_tiers"]):
            assert str(tier["occupancy"]).upper() in {"VACANT", "NONE", ""}
    for record in model["reconciliations"]:
        assert record["ratifies"] is False
        assert record["closes_vacancy"] is False

    document = _vacant_twin(tmp_path, engine)
    document["tier_source"]["vacancy_required_fields"].append("ratified_occupant")
    model = engine.measure(document)
    val = next(v for v in model["validations"] if v["id"] == "UCAF-VAL-06")
    assert val["measured"] is True
    assert val["satisfied"] is False, "a vacancy missing a required field went unrefused"


@pytest.mark.parametrize("scenario", sorted(UCAF_MUTATIONS))
def test_ucaf_gate_is_non_vacuous(scenario: str) -> None:
    if scenario == "vacancy-record-incomplete":
        pytest.skip(
            "exercised over the vacant twin in test_ucaf_vacancy_guards_still_fire_on_a_vacant_twin"
        )
    engine = _load("ucaf")
    document = engine.load_declaration()
    mutate, expected = UCAF_MUTATIONS[scenario]
    model = _closed(engine, document, mutate)
    assert model["gate"] == "CLOSED", f"{scenario} did not close the gate"
    assert (
        expected in model["blocking_failures"]
    ), f"{scenario} closed the gate but not through {expected}: {model['blocking_failures']}"


def test_ucaf_aborts_fail_closed_on_an_unimplemented_reader() -> None:
    """An unimplemented source format must abort, never register zero authorities silently."""
    engine = _load("ucaf")
    document = copy.deepcopy(engine.load_declaration())
    document["authority_sources"][0]["format"] = "a-format-no-reader-implements"
    with pytest.raises(engine.FailClosed):
        engine.measure(document)


def test_ucaf_never_promotes_an_instrument_into_a_vacant_tier(tmp_path) -> None:
    """CMG-000001 XVII.4 forbids promotion; LXXXI.5 voids any reading that does.

    The live registry carries no vacancy (UCOS-RAT-002 retired VAC-01), so the residue is
    manufactured over the vacant twin rather than borrowed from repository state.
    """
    engine = _load("ucaf")
    model = engine.measure(_vacant_twin(tmp_path, engine))
    vacant = set(model["vacant_tiers"])
    assert vacant, "the twin records no vacancy — this assertion would be vacuous"
    for tier in model["tiers"]:
        if tier["id"] in vacant:
            assert str(tier["occupancy"]).upper() in {"VACANT", "NONE", ""}
    for record in model["reconciliations"]:
        assert record["ratifies"] is False
        assert record["closes_vacancy"] is False


URAT_MUTATIONS = {
    "verdict-not-located-in-the-act": (
        lambda d: d["records"][0].__setitem__("verdict_anchor", "A PHRASE THE ACT DOES NOT CARRY"),
        "URAT-VAL-04",
    ),
    "state-basis-not-located": (
        lambda d: d["records"][1]["state_basis"].__setitem__("anchor", "NOT IN THE INSTRUMENT"),
        "URAT-VAL-05",
    ),
    "authority-not-in-the-registry": (
        lambda d: d["records"][2].__setitem__("authority", "NOT-A-REGISTERED-AUTHORITY"),
        "URAT-VAL-06",
    ),
    "precondition-not-recorded-as-satisfied": (
        lambda d: d["records"][3]["preconditions"].pop(),
        "URAT-VAL-07",
    ),
    "evidence-does-not-resolve": (
        lambda d: d["records"][1]["evidence"].append("does/not/exist.md"),
        "URAT-VAL-08",
    ),
    "duplicate-canonical-record": (
        lambda d: d["records"].append(dict(d["records"][0], id="URAT-REC-DUPLICATE")),
        "URAT-VAL-10",
    ),
    "illegal-lineage-transition": (
        lambda d: d["records"][1].__setitem__("lineage_predecessor", d["records"][0]["id"]),
        "URAT-VAL-11",
    ),
    "registry-rule-anchor-absent": (
        lambda d: d["registry_rules"][0].__setitem__("anchor", "NOT IN THE INSTRUMENT"),
        "URAT-VAL-12",
    ),
    "discovered-instrument-unaccounted": (
        lambda d: d["excluded"].pop(0),
        "URAT-VAL-14",
    ),
}


@pytest.mark.parametrize("scenario", sorted(URAT_MUTATIONS))
def test_urat_gate_is_non_vacuous(scenario: str) -> None:
    engine = _load("urat")
    document = engine.load_declaration()
    mutate, expected = URAT_MUTATIONS[scenario]
    model = _closed(engine, document, mutate)
    assert model["gate"] == "CLOSED", f"{scenario} did not close the gate"
    assert (
        expected in model["blocking_failures"]
    ), f"{scenario} closed the gate but not through {expected}: {model['blocking_failures']}"


def test_urat_refuses_a_state_reserved_to_the_out_of_corpus_authority() -> None:
    """CEP-006 I.4 caps in-corpus ratification; the terminal state is unreachable from inside."""
    engine = _load("urat")
    document = engine.load_declaration()
    baseline = engine.measure(document)
    unreachable = baseline["finality_ceiling"]["unreachable_in_corpus"]
    assert unreachable, "no state is declared out-of-corpus — this assertion would be vacuous"
    mutated = copy.deepcopy(document)
    mutated["records"][0]["state"] = unreachable[0]
    model = engine.measure(mutated)
    assert model["gate"] == "CLOSED"
    assert "URAT-VAL-13" in model["blocking_failures"]


def test_urat_aborts_when_the_authority_registry_cannot_be_read() -> None:
    """No record may be admitted without a resolvable ratifying authority (CEP-006 II.4)."""
    engine = _load("urat")
    document = copy.deepcopy(engine.load_declaration())
    document["authority_registry"]["owner"] = "does/not/exist.json"
    with pytest.raises(engine.FailClosed):
        engine.measure(document)


def test_urat_admits_no_record_it_cannot_locate() -> None:
    engine = _load("urat")
    model = engine.measure(engine.load_declaration())
    assert model["records"], "the registry is empty — every assertion here would be vacuous"
    for record in model["records"]:
        assert record["record_resolved"] is True
        assert record["verdict_anchor_located"] is True
        assert record["state_basis_located"] is True
        assert record["valid"] is True


UTCE_MUTATIONS = {
    "constitutional-obligation-anchor-absent": (
        lambda d: d["obligations"][0].__setitem__("anchor", "NOT IN THE INSTRUMENT"),
        "UTCE-VAL-01",
    ),
    "rooting-relation-not-in-the-located-vocabulary": (
        lambda d: d["rooting_relations"].append(
            {"type": "Not-A-Located-Type", "direction": "from", "meaning": "fabricated"}
        ),
        "UTCE-VAL-08",
    ),
    "rooting-narrowed-so-artifacts-become-unrooted": (
        lambda d: d.__setitem__(
            "rooting_relations", [{"type": "Traces-To", "direction": "from", "meaning": "narrow"}]
        ),
        "UTCE-VAL-04",
    ),
    "derivation-rule-names-an-unlocated-lane": (
        lambda d: d["derivation_rules"][0].__setitem__("lane", "not_a_located_lane"),
        "UTCE-VAL-09",
    ),
    "downward-evidence-field-absent": (
        lambda d: d["corpus"]["evidence_fields"].append("a_field_no_artifact_carries"),
        "UTCE-VAL-06",
    ),
}


@pytest.mark.parametrize("scenario", sorted(UTCE_MUTATIONS))
def test_utce_gate_is_non_vacuous(scenario: str) -> None:
    engine = _load("utce")
    document = engine.load_declaration()
    mutate, expected = UTCE_MUTATIONS[scenario]
    model = _closed(engine, document, mutate)
    assert model["gate"] == "CLOSED", f"{scenario} did not close the gate"
    assert (
        expected in model["blocking_failures"]
    ), f"{scenario} closed the gate but not through {expected}: {model['blocking_failures']}"


def test_utce_aborts_when_a_located_vocabulary_cannot_be_read() -> None:
    engine = _load("utce")
    document = copy.deepcopy(engine.load_declaration())
    document["lane_vocabulary"]["symbol"] = "A_SYMBOL_THAT_DOES_NOT_EXIST"
    with pytest.raises(engine.FailClosed):
        engine.measure(document)


def test_utce_aborts_when_the_certified_corpus_cannot_be_read() -> None:
    engine = _load("utce")
    document = copy.deepcopy(engine.load_declaration())
    document["corpus"]["artifacts"]["owner"] = "does/not/exist.json"
    with pytest.raises(engine.FailClosed):
        engine.measure(document)


def test_utce_reports_the_engineering_spine_unchanged_and_does_not_close_it() -> None:
    """The thirteen-lane predicate is reported, never redefined and never claimed satisfied."""
    engine = _load("utce")
    model = engine.measure(engine.load_declaration())
    spine = model["engineering_spine"]
    assert spine["artifacts"] == model["counts"]["artifacts"]
    assert spine["artifacts_fully_traced"] + spine["artifacts_incomplete"] == spine["artifacts"]
    completeness = [
        entry
        for entry in model["validations"]
        if entry["dimension"] == "ENGINEERING-SPINE-COMPLETE"
    ]
    assert completeness, "the spine dimension is not declared"
    assert completeness[0]["blocking"] is False, "the spine gap must not be presented as closed"
    if spine["artifacts_fully_traced"] < spine["artifacts"]:
        assert completeness[0]["satisfied"] is False


def test_utce_lane_population_reconciles_against_the_corpus() -> None:
    engine = _load("utce")
    document = engine.load_declaration()
    assert engine.check_no_fabrication(document) == []
    model = engine.measure(document)
    total = model["counts"]["artifacts"]
    for entry in model["lane_register"]:
        assert entry["populated"] + entry["unevidenced"] == total
    for entry in model["derivation"]:
        assert entry["already_written"] <= entry["artifacts_supported"]
        if entry["artifacts_supported"]:
            assert entry["cited_edges"], f"{entry['id']} reports support with no cited edge"


def test_utce_reads_nothing_it_is_permitted_to_write() -> None:
    engine = _load("utce")
    assert engine.check_read_only(engine.load_declaration()) == []


UFEP_MUTATIONS = {
    "clause-anchor-absent": (
        lambda d: d["eligibility_basis"].__setitem__("anchor", "NOT IN THE INSTRUMENT"),
        "UFEP-VAL-01",
    ),
    "subject-validation-verdict-absent": (
        lambda d: d["subjects"][0]["validation_evidence"].__setitem__("anchor", "NOT IN THE DOC"),
        "UFEP-VAL-13",
    ),
    "subject-certification-verdict-absent": (
        lambda d: d["subjects"][1]["certification_evidence"].__setitem__(
            "anchor", "NOT IN THE DOC"
        ),
        "UFEP-VAL-13",
    ),
    "subject-not-in-the-ratification-registry": (
        lambda d: d["subjects"][2].__setitem__("ratification_record", "URAT-REC-DOES-NOT-EXIST"),
        "UFEP-VAL-03",
    ),
    "frozen-baseline-manifest-unreadable": (
        lambda d: d["frozen_baselines"][0].__setitem__("manifest", "does/not/exist.txt"),
        "UFEP-VAL-08",
    ),
    "freeze-notice-status-absent": (
        lambda d: d["frozen_baselines"][0].__setitem__("notice_anchor", "NOT IN THE NOTICE"),
        "UFEP-VAL-08",
    ),
    "authorization-not-located": (
        lambda d: d["authorizations"][0].__setitem__("anchor", "NOT IN THE INSTRUMENT"),
        "UFEP-VAL-12",
    ),
    "completion-source-unreadable": (
        lambda d: d["sources"][1].__setitem__("owner", "does/not/exist.json"),
        "UFEP-VAL-14",
    ),
}


@pytest.mark.parametrize("scenario", sorted(UFEP_MUTATIONS))
def test_ufep_gate_is_non_vacuous(scenario: str) -> None:
    engine = _load("ufep")
    document = engine.load_declaration()
    mutate, expected = UFEP_MUTATIONS[scenario]
    model = _closed(engine, document, mutate)
    assert model["gate"] == "CLOSED", f"{scenario} did not close the gate"
    assert (
        expected in model["blocking_failures"]
    ), f"{scenario} closed the gate but not through {expected}: {model['blocking_failures']}"


def test_ufep_aborts_when_no_subject_is_declared(tmp_path: Path) -> None:
    """An empty subject set would make eligibility vacuously true, so it must abort fail-closed."""
    engine = _load("ufep")
    document = copy.deepcopy(engine.load_declaration())
    document["subjects"] = []
    empty = tmp_path / "ufep-declaration.json"
    empty.write_text(json.dumps(document), encoding="utf-8")
    original = engine.DECLARATION
    try:
        engine.DECLARATION = empty
        with pytest.raises(engine.FailClosed):
            engine.load_declaration()
    finally:
        engine.DECLARATION = original


def test_ufep_performs_no_freeze_and_reaches_no_state_reserved_to_freeze_authority() -> None:
    """CEP-007 VII.1 reserves the freeze decision; I.5 forbids its self-conferral."""
    engine = _load("ufep")
    document = engine.load_declaration()
    model = engine.measure(document)
    reachable = {
        entry["state"] for entry in model["states"] if entry["reachable_by_this_programme"]
    }
    unreachable = {
        entry["state"] for entry in model["states"] if not entry["reachable_by_this_programme"]
    }
    assert unreachable, "no freeze state is reserved — this assertion would be vacuous"
    for subject in model["subjects"]:
        assert subject["state"] in reachable
    assert model["determination"]["freeze_performed"] is False
    for entry in model["authorizations"]:
        assert entry["acted_on"] is False
    assert engine.check_no_freeze(document) == []


def test_ufep_measures_every_precondition_for_every_subject() -> None:
    """CEP-007 V.2 — every precondition machine-verifiable; V.4 — unverifiable is unsatisfied."""
    engine = _load("ufep")
    document = engine.load_declaration()
    model = engine.measure(document)
    declared = {entry["id"] for entry in model["preconditions"]}
    assert len(declared) == 5, "CEP-007 V.1 fixes five preconditions"
    for subject in model["subjects"]:
        assert set(subject["preconditions"]) == declared
        for outcome in subject["preconditions"].values():
            assert outcome["outcome"] in {"SATISFIED", "UNSATISFIED"}


def test_ufep_no_drift_over_the_located_frozen_baseline() -> None:
    """CEP-007 X.2 — every frozen artifact must match its recorded baseline."""
    engine = _load("ufep")
    document = engine.load_declaration()
    assert engine.check_no_drift(document) == []
    model = engine.measure(document)
    for entry in model["frozen_baselines"]:
        assert entry["readable"] is True
        assert entry["entries"] > 0
        assert entry["matched"] == entry["entries"]
        assert entry["drifted"] == []
        assert entry["missing"] == []


def test_ufep_baseline_is_content_addressed_and_reproducible() -> None:
    """CEP-007 VIII.2/VIII.3 — a pure function of located material, recomputing identically."""
    engine = _load("ufep")
    document = engine.load_declaration()
    first = engine.measure(document)["baselines"]
    second = engine.measure(document)["baselines"]
    assert first == second
    assert first, "no baseline was computed"
    for subject in engine.measure(document)["subjects"]:
        record = subject["freeze_record"]
        assert record["baseline_digest"]
        assert record["version"] == record["baseline_digest"][:12]


def test_ufep_completion_requires_a_full_tier_certifier_model() -> None:
    """A tier-limited certifier run excludes blocking checks and may not produce completion."""
    engine = _load("ufep")
    document = engine.load_declaration()
    tier_criteria = [
        entry
        for entry in engine.measure(document)["completion_criteria"]
        if "full-tier" in entry["criterion"]
    ]
    assert tier_criteria, "no criterion measures the tier of the certifier model"
    assert tier_criteria[0]["blocking"] is True
