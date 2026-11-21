"""UOBC-000001 conformance tests — identity before existence.

Organised around the four prohibitions the contract exists to enforce, because those
are the claims that would otherwise be prose. The most load-bearing tests are the ones
proving a *refusal*: an undeclared namespace, an inadmissible initial state, an
overwrite of a born identity, and an attempt to replace identity during evolution.

``test_provisional_check_does_not_flag_engine_temporal`` is a regression test for a real
defect found by running the gate: matching provisional markers as substrings flagged
``engine.temporal`` for containing ``temp``. A check that cries wolf on a legitimate
name gets switched off rather than fixed, so the segment-matching behaviour is pinned.
"""

from __future__ import annotations

import dataclasses
import json

import pytest

import engine.object_birth.model as model
from engine.object_birth import (
    BIRTH_CONTRACT,
    LAW_CHECKS,
    MANDATORY_FIELD_NAMES,
    BirthError,
    BirthRecord,
    append,
    assess,
    birth,
    derive_identity,
    dumps,
    empty_ledger,
    evolve,
    expected_urn,
    identity_uuid,
    load,
    load_contract,
    local_name_of,
    namespace_of,
    records,
    save,
    supersede,
)
from engine.object_birth.contract import load_declaration
from engine.object_birth.contract import load_declaration as loader
from engine.object_birth.gate import EXIT_CLOSED, EXIT_FAULT, EXIT_OPEN, main, measure
from engine.object_birth.ledger import FORBIDDEN_MINT_MARKER, LEDGER_SCHEMA
from engine.object_birth.model import BirthContract
from engine.object_birth.scope import load_policy
from engine.temporal import TemporalCoordinate

STAMP = TemporalCoordinate.logical(
    484, system_identifier="ucos-repository-history", authority="test"
).qualified

CONTEXT = {"existence": "actual", "temporal": "logical repository history"}


@pytest.fixture(name="contract")
def _contract():
    return load_contract()


def _birth(contract, local="TEST-OBJECT", ns="ucos.determination", **kw):
    params = {
        "namespace": ns,
        "local_name": local,
        "owner": "UCOS-REPOSITORY-ROOT",
        "creation_timestamp": STAMP,
        "creation_context": CONTEXT,
        "parent_identity": None,
        "lifecycle_binding": "UCIC-001 (owner) · UCL-000001 (derived)",
        "initial_state": "ACTIVE",
        "certification_boundary": "certifies nothing",
        "root": True,
    }
    params.update(kw)
    return birth(contract, **params)


# ------------------------------------------------------------------ declaration


def test_contract_loads_and_is_sound(contract) -> None:
    assert contract.artifact_id == "UOBC-000001"
    assert contract.validate(frozenset(LAW_CHECKS)) == ()


def test_contract_declares_nine_mandatory_fields(contract) -> None:
    assert len(contract.fields) == 9
    assert tuple(f.field for f in contract.fields) == MANDATORY_FIELD_NAMES


def test_contract_declares_seven_stages_and_identity_flips_once(contract) -> None:
    assert len(contract.stages) == 7
    assert contract.identity_stage.stage_id == "UOBC-S-04"
    flags = [s.identity_exists for s in contract.stages]
    assert flags == [False, False, False, True, True, True, True]


def test_every_law_names_an_implemented_check(contract) -> None:
    assert len(contract.laws) == 8
    for law in contract.laws:
        assert law.check in LAW_CHECKS


def test_contract_consumes_no_counter(contract) -> None:
    assert contract.counter_consumed is False
    assert BIRTH_CONTRACT["advances_counter"] is False
    assert BIRTH_CONTRACT["mints_repository_serial"] is False


def test_declaration_delegates_to_the_supreme_identity_plane(contract) -> None:
    assert contract.identity_home == "engine/uckp/identity.py"


def test_unsound_contract_is_refused() -> None:
    doc = load_declaration()
    doc["stages"][0]["identity_exists"] = True  # identity before intent discovery

    problems = BirthContract.from_declaration(doc).validate(frozenset(LAW_CHECKS))
    assert any("first stage already holds identity" in p for p in problems)


def test_declaration_missing_a_key_is_refused() -> None:
    with pytest.raises(BirthError, match="unusable"):
        BirthContract.from_declaration({"artifact_id": "X"})


# ---------------------------------------------------------------------- identity


def test_identity_is_derived_before_any_artifact_exists() -> None:
    """The whole point: an id for a thing that does not exist yet."""
    urn = derive_identity("ucos.cmg", "CMG-999999-NOT-A-FILE")
    assert urn == "urn:ucos:ucko:ucos.cmg:CMG-999999-NOT-A-FILE"


def test_identity_is_pure_and_reproducible() -> None:
    assert derive_identity("ucos.cmg", "X") == derive_identity("ucos.cmg", "X")


def test_identity_uuid_is_deterministic() -> None:
    urn = derive_identity("ucos.cmg", "X")
    assert identity_uuid(urn) == identity_uuid(urn)


def test_identity_has_no_path_input() -> None:
    """Two artifacts at different paths with the same name share one identity."""
    assert expected_urn("ucos.cmg", "CMG-000012") == derive_identity("ucos.cmg", "CMG-000012")


def test_namespace_and_local_name_round_trip() -> None:
    urn = derive_identity("ucos.engine", "engine.temporal")
    assert namespace_of(urn) == "ucos.engine"
    assert local_name_of(urn) == "engine.temporal"


@pytest.mark.parametrize("bad", ["not-a-urn", "urn:ucos:ucko:only-three", "a:b:c:d:e"])
def test_malformed_urn_is_refused(bad: str) -> None:
    with pytest.raises(BirthError, match="not a UCKO universal identity"):
        namespace_of(bad)


# ------------------------------------------------------------------------- birth


def test_birth_produces_all_nine_fields(contract) -> None:
    record = _birth(contract)
    body = record.to_dict()
    assert set(body) == set(MANDATORY_FIELD_NAMES)


def test_birth_refuses_an_undeclared_namespace(contract) -> None:
    with pytest.raises(BirthError, match="not declared in the birth contract"):
        _birth(contract, ns="invented.namespace")


def test_birth_refuses_an_inadmissible_initial_state(contract) -> None:
    with pytest.raises(BirthError, match="not admissible at birth"):
        _birth(contract, initial_state="SUPERSEDED")


def test_birth_refuses_empty_creation_context(contract) -> None:
    with pytest.raises(BirthError, match="context assimilation produced nothing"):
        _birth(contract, creation_context={})


def test_birth_refuses_a_non_root_without_a_parent(contract) -> None:
    with pytest.raises(BirthError, match="not declared a root"):
        _birth(contract, root=False, parent_identity=None)


def test_birth_accepts_a_declared_child(contract) -> None:
    parent = _birth(contract, local="PARENT")
    child = _birth(contract, local="CHILD", parent_identity=parent.universal_id, root=False)
    assert child.parent_identity == parent.universal_id


def test_creation_timestamp_is_a_qualified_coordinate(contract) -> None:
    """A bare value would have mandated a representation; the frame travels with it."""
    record = _birth(contract)
    assert "#" in record.creation_timestamp
    assert record.creation_timestamp.startswith("logical:")


# --------------------------------------------------------------------- evolution


def test_evolution_preserves_identity(contract) -> None:
    record = _birth(contract)
    evolved = evolve(record, owner="NEW-OWNER")
    assert evolved.universal_id == record.universal_id
    assert evolved.owner == "NEW-OWNER"


def test_evolution_preserves_immutable_fields(contract) -> None:
    record = _birth(contract)
    evolved = evolve(record, owner="OTHER", certification_boundary="changed")
    assert evolved.creation_timestamp == record.creation_timestamp
    assert evolved.parent_identity == record.parent_identity
    assert evolved.initial_state == record.initial_state
    assert evolved.creation_context == record.creation_context


def test_evolution_with_no_changes_is_the_same_object(contract) -> None:
    record = _birth(contract)
    assert evolve(record).to_dict() == record.to_dict()


def test_evolution_refuses_a_tampered_identity(contract) -> None:
    record = _birth(contract)
    tampered = BirthRecord(
        **{
            **record.to_dict(),
            "universal_id": "urn:ucos:ucko:ucos.cmg:OTHER",
            "creation_context": record.creation_context,
        }
    )
    with pytest.raises(BirthError, match="would replace identity"):
        evolve(tampered)


# ------------------------------------------------------------------------ ledger


def test_empty_ledger_is_well_formed_and_holds_no_counter() -> None:
    ledger = empty_ledger()
    assert ledger["schema"] == LEDGER_SCHEMA
    assert ledger["keyed_by"] == "universal_id"
    assert FORBIDDEN_MINT_MARKER not in ledger


def test_append_then_read_round_trips(contract) -> None:
    ledger = append(empty_ledger(), _birth(contract))
    assert len(records(ledger)) == 1


def test_identical_reappend_is_idempotent(contract) -> None:
    record = _birth(contract)
    ledger = append(append(empty_ledger(), record), record)
    assert len(records(ledger)) == 1


def test_conflicting_append_is_refused(contract) -> None:
    record = _birth(contract)
    ledger = append(empty_ledger(), record)
    with pytest.raises(BirthError, match="append-only"):
        append(ledger, evolve(record, owner="DIFFERENT"))


def test_supersede_preserves_the_prior_state(contract) -> None:
    record = _birth(contract)
    ledger = append(empty_ledger(), record)
    ledger = supersede(ledger, evolve(record, owner="NEW"), reason="ownership transfer")
    assert len(ledger["supersessions"]) == 1
    assert ledger["supersessions"][0]["superseded"]["owner"] == "UCOS-REPOSITORY-ROOT"
    assert records(ledger)[0].owner == "NEW"
    assert records(ledger)[0].universal_id == record.universal_id


def test_supersede_refuses_an_unborn_identity(contract) -> None:
    with pytest.raises(BirthError, match="never born"):
        supersede(empty_ledger(), _birth(contract), reason="x")


def test_ledger_serialisation_is_byte_stable(contract) -> None:
    ledger = append(empty_ledger(), _birth(contract))
    assert dumps(ledger) == dumps(json.loads(dumps(ledger)))
    assert dumps(ledger).endswith("\n")


def test_absent_ledger_loads_as_empty(tmp_path) -> None:
    assert load(str(tmp_path / "nothing.json"))["births"] == {}


def test_ledger_holding_the_mint_marker_is_refused(tmp_path) -> None:
    path = tmp_path / "rival.json"
    path.write_text(json.dumps({"schema": LEDGER_SCHEMA, "births": {}, FORBIDDEN_MINT_MARKER: {}}))
    with pytest.raises(BirthError, match="second mint"):
        load(str(path))


def test_ledger_with_wrong_schema_is_refused(tmp_path) -> None:
    path = tmp_path / "wrong.json"
    path.write_text(json.dumps({"schema": "something-else", "births": {}}))
    with pytest.raises(BirthError, match="schema is not"):
        load(str(path))


def test_unreadable_ledger_is_refused(tmp_path) -> None:
    path = tmp_path / "broken.json"
    path.write_text("{not json")
    with pytest.raises(BirthError, match="unreadable"):
        load(str(path))


def test_record_missing_a_mandatory_field_is_refused() -> None:
    with pytest.raises(BirthError, match="missing mandatory field"):
        BirthRecord.from_dict({"universal_id": "urn:ucos:ucko:a:b"})


# -------------------------------------------------------------------- law checks


def test_provisional_check_does_not_flag_engine_temporal(contract) -> None:
    """Regression: substring matching flagged 'temporal' for containing 'temp'."""
    ledger = append(empty_ledger(), _birth(contract, ns="ucos.engine", local="engine.temporal"))
    violations = LAW_CHECKS["no_temporary_identity"](contract, ledger, records(ledger))
    assert violations == ()


@pytest.mark.parametrize("name", ["TMP-THING", "thing.draft", "wip_thing", "PLACEHOLDER-X"])
def test_provisional_segments_are_flagged(contract, name: str) -> None:
    ledger = append(empty_ledger(), _birth(contract, local=name))
    violations = LAW_CHECKS["no_temporary_identity"](contract, ledger, records(ledger))
    assert any("provisional name segment" in v for v in violations)


def test_anonymous_check_flags_an_empty_field(contract) -> None:
    record = _birth(contract)
    hollow = BirthRecord(
        **{**record.to_dict(), "owner": "", "creation_context": record.creation_context}
    )
    ledger = {**empty_ledger()}
    body = hollow.to_dict()
    body.pop("universal_id")
    ledger["births"] = {hollow.universal_id: body}
    violations = LAW_CHECKS["no_anonymous_object"](contract, ledger, (hollow,))
    assert any("'owner' is empty" in v for v in violations)


def test_identity_immutable_check_flags_a_namespace_disagreement(contract) -> None:
    record = _birth(contract)
    wrong = BirthRecord(
        **{**record.to_dict(), "namespace": "ucos.cmg", "creation_context": record.creation_context}
    )
    violations = LAW_CHECKS["identity_immutable"](contract, empty_ledger(), (wrong,))
    assert any("disagrees with the identity it carries" in v for v in violations)


def test_append_only_check_flags_a_path_keyed_ledger(contract) -> None:
    ledger = {**empty_ledger(), "keyed_by": "path"}
    violations = LAW_CHECKS["append_only_history"](contract, ledger, ())
    assert any("not by identity" in v for v in violations)


def test_evolution_check_flags_a_reasonless_supersession(contract) -> None:
    record = _birth(contract)
    ledger = append(empty_ledger(), record)
    ledger["supersessions"] = [
        {"universal_id": record.universal_id, "superseded": {}, "reason": ""}
    ]
    violations = LAW_CHECKS["evolution_preserves_identity"](contract, ledger, records(ledger))
    assert any("no reason" in v for v in violations)


def test_assess_measures_every_law(contract) -> None:
    ledger = append(empty_ledger(), _birth(contract))
    assessments = assess(contract, ledger, records(ledger))
    assert len(assessments) == 8
    assert all(not violations for _, _, violations in assessments)


# -------------------------------------------------------------------------- gate


def test_gate_measures_the_committed_ledger() -> None:
    report = measure()
    assert report["artifact_id"] == "UOBC-000001"
    assert report["births"] >= 8, "the committed ledger must not be vacuous"


def test_gate_measures_every_law_both_instruments_declare() -> None:
    """Derived, never pinned.

    The gate measures the birth CONTRACT and the birth SCOPE policy in one pass, because
    scope is part of the contract rather than a separate subject. A pinned literal here
    would have to be edited every time either instrument gained a law, and an expectation
    that must be edited to stay true is an expectation that stops being checked.
    """

    report = measure()
    expected = len(load_contract().laws) + len(load_policy().laws)
    assert report["laws_measured"] == expected
    measured = {law["law_id"] for law in report["laws"]}
    declared = {law.law_id for law in load_contract().laws} | {
        law.law_id for law in load_policy().laws
    }
    assert measured == declared


def test_committed_ledger_passes_every_law() -> None:
    report = measure()
    refused = [law["law_id"] for law in report["laws"] if not law["holds"]]
    assert refused == [], f"laws refused: {refused}"
    assert report["verdict"] == "OPEN"


def test_gate_cli_returns_open(capsys) -> None:
    assert main(["--quiet"]) == EXIT_OPEN


def test_gate_cli_emits_json(capsys) -> None:
    assert main(["--json"]) == EXIT_OPEN
    assert json.loads(capsys.readouterr().out)["artifact_id"] == "UOBC-000001"


def test_gate_renders_a_report(capsys) -> None:
    main([])
    assert "GATE PASSED" in capsys.readouterr().out


def test_gate_faults_on_an_unreadable_declaration(tmp_path, capsys) -> None:
    """A declaration that cannot be read is a FAULT, never a pass."""
    assert main(["--declaration", str(tmp_path / "absent.json")]) == EXIT_FAULT
    assert "FAULT" in capsys.readouterr().err


def test_gate_closes_on_a_violating_ledger(tmp_path, capsys) -> None:
    path = tmp_path / "bad-ledger.json"
    bad = {**empty_ledger(), "keyed_by": "path"}
    path.write_text(dumps(bad))
    assert main(["--ledger", str(path), "--quiet"]) == EXIT_CLOSED


# ------------------------------------------------- declaration refusal coverage
# Every from_declaration is a fail-closed boundary. An unusable declaration must
# raise rather than construct a half-built object that later fails somewhere less
# obvious, so each boundary gets a test.


@pytest.mark.parametrize(
    ("cls_name", "payload"),
    [
        ("BirthStage", {"id": "S", "ordinal": "not-an-int"}),
        ("MandatoryField", {"id": "F"}),
        ("BirthLaw", {"id": "L"}),
        ("Namespace", {"namespace": "n"}),
        ("Boundary", {"id": "B"}),
    ],
)
def test_declaration_entries_fail_closed(cls_name: str, payload: dict) -> None:
    cls = getattr(model, cls_name)
    with pytest.raises(BirthError, match="unusable"):
        cls.from_declaration(payload)


def test_contract_without_stages_is_refused() -> None:
    doc = load_declaration()
    doc["stages"] = []
    problems = BirthContract.from_declaration(doc).validate(frozenset(LAW_CHECKS))
    assert any("declares no stage" in p for p in problems)


def test_contract_with_unordered_stages_is_refused() -> None:
    doc = load_declaration()
    doc["stages"] = list(reversed(doc["stages"]))
    problems = BirthContract.from_declaration(doc).validate(frozenset(LAW_CHECKS))
    assert any("not in ordinal order" in p for p in problems)


def test_contract_with_duplicate_ordinals_is_refused() -> None:
    doc = load_declaration()
    doc["stages"][1]["ordinal"] = doc["stages"][0]["ordinal"]
    problems = BirthContract.from_declaration(doc).validate(frozenset(LAW_CHECKS))
    assert any("share an ordinal" in p for p in problems)


def test_contract_whose_final_stage_lacks_identity_is_refused() -> None:
    doc = load_declaration()
    doc["stages"][-1]["identity_exists"] = False
    problems = BirthContract.from_declaration(doc).validate(frozenset(LAW_CHECKS))
    assert any("final stage holds no identity" in p for p in problems)


def test_contract_with_extra_flips_is_refused() -> None:
    doc = load_declaration()
    doc["stages"][5]["identity_exists"] = False  # True, True, False, True
    problems = BirthContract.from_declaration(doc).validate(frozenset(LAW_CHECKS))
    assert any("flips" in p for p in problems)


def test_contract_with_mismatched_fields_is_refused() -> None:
    doc = load_declaration()
    doc["mandatory_fields"] = doc["mandatory_fields"][:-1]
    problems = BirthContract.from_declaration(doc).validate(frozenset(LAW_CHECKS))
    assert any("do not match the record model" in p for p in problems)


def test_contract_with_no_laws_is_refused() -> None:
    doc = load_declaration()
    doc["laws"] = []
    problems = BirthContract.from_declaration(doc).validate(frozenset(LAW_CHECKS))
    assert any("declares no law" in p for p in problems)


def test_contract_naming_an_unimplemented_check_is_refused() -> None:
    doc = load_declaration()
    doc["laws"][0]["check"] = "no_such_check"
    problems = BirthContract.from_declaration(doc).validate(frozenset(LAW_CHECKS))
    assert any("not implemented" in p for p in problems)


def test_contract_claiming_a_counter_is_refused() -> None:
    doc = load_declaration()
    doc["identity_plane"]["counter_consumed"] = True
    problems = BirthContract.from_declaration(doc).validate(frozenset(LAW_CHECKS))
    assert any("second mint" in p for p in problems)


def test_contract_with_no_initial_states_is_refused() -> None:
    doc = load_declaration()
    doc["initial_states"] = []
    problems = BirthContract.from_declaration(doc).validate(frozenset(LAW_CHECKS))
    assert any("no admissible initial state" in p for p in problems)


def test_contract_with_an_unrecorded_identity_input_is_refused() -> None:
    doc = load_declaration()
    doc["identity_inputs"] = ["namespace", "not_a_field"]
    problems = BirthContract.from_declaration(doc).validate(frozenset(LAW_CHECKS))
    assert any("is not a recorded field" in p for p in problems)


def test_contract_with_no_identity_stage_raises() -> None:
    doc = load_declaration()
    for stage in doc["stages"]:
        stage["identity_exists"] = False
    contract = BirthContract.from_declaration(doc)
    with pytest.raises(BirthError, match="no declared stage derives identity"):
        _ = contract.identity_stage


def test_unreadable_declaration_is_refused(tmp_path) -> None:
    path = tmp_path / "broken.json"
    path.write_text("{oops")
    with pytest.raises(BirthError, match="unreadable"):
        loader(str(path))


def test_non_mapping_declaration_is_refused(tmp_path) -> None:
    path = tmp_path / "list.json"
    path.write_text("[]")
    with pytest.raises(BirthError, match="not a mapping"):
        loader(str(path))


def test_load_contract_refuses_an_unsound_declaration(tmp_path) -> None:
    doc = load_declaration()
    doc["laws"][0]["check"] = "missing"
    path = tmp_path / "unsound.json"
    path.write_text(json.dumps(doc))
    with pytest.raises(BirthError, match="unsound"):
        load_contract(str(path))


# ------------------------------------------------------- remaining check branches


def test_identity_precedes_existence_without_an_instantiation_stage(contract) -> None:
    doc = load_declaration()
    for stage in doc["stages"]:
        if stage["produces"] == "artifact":
            stage["produces"] = "something_else"
    altered = BirthContract.from_declaration(doc)
    violations = LAW_CHECKS["identity_precedes_existence"](altered, empty_ledger(), ())
    assert violations == ("no declared stage instantiates an artifact",)


def test_identity_precedes_existence_flags_early_instantiation() -> None:
    doc = load_declaration()
    doc["stages"][0]["produces"] = "artifact"  # ordinal 10, before identity at 40
    altered = BirthContract.from_declaration(doc)
    violations = LAW_CHECKS["identity_precedes_existence"](altered, empty_ledger(), ())
    assert any("not after identity" in v for v in violations)
    assert any("without identity" in v for v in violations)


def test_no_post_creation_registration_without_a_registration_stage() -> None:
    doc = load_declaration()
    for stage in doc["stages"]:
        if stage["produces"] == "registry_entry":
            stage["produces"] = "other"
    altered = BirthContract.from_declaration(doc)
    violations = LAW_CHECKS["no_post_creation_registration"](altered, empty_ledger(), ())
    assert violations == ("no declared stage produces a registry entry",)


def test_no_post_creation_registration_flags_early_registration() -> None:
    doc = load_declaration()
    doc["stages"][0]["produces"] = "registry_entry"
    altered = BirthContract.from_declaration(doc)
    violations = LAW_CHECKS["no_post_creation_registration"](altered, empty_ledger(), ())
    assert any("registers before identity exists" in v for v in violations)


def test_rival_counter_check_flags_a_wrong_identity_home() -> None:
    doc = load_declaration()
    doc["identity_plane"]["home"] = "engine/somewhere_else.py"
    altered = BirthContract.from_declaration(doc)
    violations = LAW_CHECKS["no_rival_counter"](altered, empty_ledger(), ())
    assert any("not delegated to the supreme plane" in v for v in violations)


def test_rival_counter_check_flags_a_counter_holding_ledger(contract) -> None:
    ledger = {**empty_ledger(), FORBIDDEN_MINT_MARKER: {"X": 1}}
    violations = LAW_CHECKS["no_rival_counter"](contract, ledger, ())
    assert any("declared mint marker" in v for v in violations)


def test_identity_immutable_check_flags_a_malformed_identity(contract) -> None:
    record = _birth(contract)
    broken = BirthRecord(
        **{
            **record.to_dict(),
            "universal_id": "not-a-urn",
            "creation_context": record.creation_context,
        }
    )
    violations = LAW_CHECKS["identity_immutable"](contract, empty_ledger(), (broken,))
    assert any("not a UCKO universal identity" in v for v in violations)


def test_evolution_check_flags_an_unknown_supersession_subject(contract) -> None:
    ledger = {
        **empty_ledger(),
        "supersessions": [
            {
                "universal_id": "urn:ucos:ucko:ucos.cmg:GHOST",
                "superseded": {"owner": "x"},
                "reason": "r",
            }
        ],
    }
    violations = LAW_CHECKS["evolution_preserves_identity"](contract, ledger, ())
    assert any("not born" in v for v in violations)


def test_evolution_check_flags_a_missing_prior_state(contract) -> None:
    record = _birth(contract)
    ledger = append(empty_ledger(), record)
    ledger["supersessions"] = [
        {"universal_id": record.universal_id, "superseded": None, "reason": "r"}
    ]
    violations = LAW_CHECKS["evolution_preserves_identity"](contract, ledger, records(ledger))
    assert any("records no prior state" in v for v in violations)


def test_append_only_check_flags_a_missing_supersessions_list(contract) -> None:
    ledger = {**empty_ledger()}
    ledger.pop("supersessions")
    violations = LAW_CHECKS["append_only_history"](contract, ledger, ())
    assert any("history cannot grow" in v for v in violations)


def test_append_only_check_flags_a_self_duplicating_entry(contract) -> None:
    record = _birth(contract)
    ledger = {**empty_ledger(), "births": {record.universal_id: record.to_dict()}}
    violations = LAW_CHECKS["append_only_history"](contract, ledger, ())
    assert any("duplicates its own key" in v for v in violations)


def test_append_only_check_flags_a_non_mapping_entry(contract) -> None:
    ledger = {**empty_ledger(), "births": {"urn:ucos:ucko:a:b": "not-a-mapping"}}
    violations = LAW_CHECKS["append_only_history"](contract, ledger, ())
    assert any("not a mapping" in v for v in violations)


# ------------------------------------------------------------- ledger edge cases


def test_ledger_without_a_births_mapping_is_refused(tmp_path) -> None:
    path = tmp_path / "no-births.json"
    path.write_text(json.dumps({"schema": LEDGER_SCHEMA, "births": []}))
    with pytest.raises(BirthError, match="no births mapping"):
        load(str(path))


def test_non_mapping_ledger_is_refused(tmp_path) -> None:
    path = tmp_path / "list.json"
    path.write_text("[]")
    with pytest.raises(BirthError, match="not a mapping"):
        load(str(path))


def test_records_refuses_a_non_mapping_entry() -> None:
    ledger = {**empty_ledger(), "births": {"urn:ucos:ucko:a:b": 42}}
    with pytest.raises(BirthError, match="not a mapping"):
        records(ledger)


def test_record_with_non_mapping_context_is_refused() -> None:
    with pytest.raises(BirthError, match="must be a mapping"):
        BirthRecord.from_dict(
            {
                "universal_id": "urn:ucos:ucko:a:b",
                "namespace": "a",
                "owner": "o",
                "creation_timestamp": STAMP,
                "creation_context": "not-a-mapping",
                "parent_identity": None,
                "lifecycle_binding": "l",
                "initial_state": "ACTIVE",
                "certification_boundary": "c",
            }
        )


def test_save_and_reload_round_trips(tmp_path, contract) -> None:
    path = tmp_path / "nested" / "ledger.json"
    ledger = append(empty_ledger(), _birth(contract))
    save(str(path), ledger)
    assert len(records(load(str(path)))) == 1


def test_expected_urn_matches_derived_identity() -> None:
    assert expected_urn("ucos.cmg", "Z") == derive_identity("ucos.cmg", "Z")


# ------------------------------------------------- the laws' remaining refusals
#
# Each law below is measured over the committed ledger, which satisfies all eight. The arms
# reached here are the ones that answer for a ledger or a declaration that does not.


def test_local_name_of_refuses_a_urn_that_is_not_a_ucko_identity() -> None:
    """BOTH ACCESSORS REFUSE, AND ONLY ONE HAD BEEN SHOWN TO.

    ``check_identity_immutable`` calls ``namespace_of`` first, so a malformed identity is
    always refused there and ``local_name_of``'s own guard never ran — while it is called
    directly by ``check_no_temporary_identity`` and by the scope resolver, where nothing has
    validated the urn beforehand. Returning ``parts[4]`` from a string of the wrong shape
    would hand back an arbitrary substring, or raise IndexError, in place of a local name.
    """
    assert local_name_of("urn:ucos:ucko:ucos.determination:TEST-OBJECT") == "TEST-OBJECT"

    for malformed in ("not-a-urn", "urn:ucos:ucko:only-four", "urn:ucos:other:ns:LOCAL"):
        with pytest.raises(BirthError, match="not a UCKO universal identity"):
            local_name_of(malformed)


def test_a_contract_claiming_to_consume_a_counter_is_a_rival_mint(contract) -> None:
    """UOBC-L-02 REFUSES A SECOND MINT, and its first violation had no case.

    ``from_declaration`` already refuses a declaration claiming a counter, so a contract
    holding that flag cannot be loaded — which is exactly why the law's own check for it had
    never run. The law is what measures a contract handed to it any other way, and the
    distinction it protects is the whole point of the birth plane: birth RECORDS an identity
    that ``engine/uckp/identity.py`` derived, and a plane that advanced a counter of its own
    would be a second source of identity for the same objects.
    """
    rival = dataclasses.replace(contract, counter_consumed=True)

    violations = LAW_CHECKS["no_rival_counter"](rival, empty_ledger(), ())

    assert any("claims to consume a counter" in v for v in violations)


def test_an_identity_that_does_not_re_derive_from_its_own_inputs_is_refused(
    contract, monkeypatch
) -> None:
    """UOBC-L-03 IS THE PURITY CHECK, and purity is why it cannot fail today.

    ``derive_identity`` is a total function of the namespace and local name, and both are
    read back OUT of the urn being checked — so the recomputation reproduces the urn by
    construction and this arm is unreachable through any record. It is reached here by making
    identity derivation impure, which is the one condition it exists to detect: the day
    derivation acquires a clock, a counter or a path, every existing record stops re-deriving
    and this is the check that says so instead of the ledger quietly becoming unreplayable.
    """
    record = _birth(contract)
    monkeypatch.setattr(
        "engine.object_birth.contract.derive_identity",
        lambda namespace, local: f"urn:ucos:ucko:{namespace}:{local}-DRIFTED",
    )

    violations = LAW_CHECKS["identity_immutable"](contract, empty_ledger(), (record,))

    assert any("does not re-derive from its own inputs" in v for v in violations)


def test_an_undeclared_namespace_and_an_inadmissible_state_are_both_refused(contract) -> None:
    """UOBC-L-05 CARRIES FOUR VIOLATIONS AND TWO HAD NEVER RUN.

    A namespace nobody declared has no owner, so a record in it names an object no authority
    answers for — the anonymous object UGA-INV-01 exists to prevent, arriving through the
    ledger instead of through the filesystem. An initial state outside the declared set is
    the same failure at the lifecycle end: the record would enter the ledger in a state no
    transition table can move it out of. Neither can be produced by ``birth()``, which
    refuses both up front; both are reachable by a record rehydrated from a ledger.
    """
    record = _birth(contract)
    body = record.to_dict()
    stray = BirthRecord.from_dict(
        {
            **body,
            "universal_id": "urn:ucos:ucko:ucos.namespace.nobody.declared:STRAY",
            "namespace": "ucos.namespace.nobody.declared",
            "initial_state": "PROVISIONALLY-ALIVE",
        }
    )

    violations = LAW_CHECKS["no_temporary_identity"](contract, empty_ledger(), (stray,))

    assert any("is undeclared" in v for v in violations)
    assert any("is inadmissible" in v for v in violations)


def test_a_malformed_identity_stops_the_temporary_name_scan_for_that_record(contract) -> None:
    """A RECORD WHOSE URN CANNOT BE READ IS REPORTED ONCE AND NOT SCANNED FURTHER.

    ``check_no_temporary_identity`` has to read the local name out of the urn before it can
    look for provisional segments in it. When that read fails the record is reported and the
    walk moves on, because scanning a name that could not be extracted would either invent
    segments or raise out of a law whose contract is to return every problem it found. The
    namespace problem raised above it is still reported — the record is refused for both
    reasons, not for whichever was noticed first.
    """
    record = _birth(contract)
    broken = BirthRecord(
        **{
            **record.to_dict(),
            "universal_id": "not-a-urn",
            "creation_context": record.creation_context,
        }
    )

    violations = LAW_CHECKS["no_temporary_identity"](contract, empty_ledger(), (broken,))

    assert any("not a UCKO universal identity" in v for v in violations)


def test_a_closed_gate_renders_its_report_once_and_not_twice(tmp_path, capsys) -> None:
    """THE REPORT GOES TO STDERR ONLY WHEN NOTHING ELSE PRINTED IT.

    ``--quiet`` suppresses the report on the way through and the closed path re-emits it on
    stderr, so a quiet run still says WHY it closed. Without ``--quiet`` the report has
    already been printed to stdout, and the guard is what stops it being printed a second
    time — a duplicated report reads as two findings, and the diff of a gate log stops being
    a diff of what the gate found.
    """
    path = tmp_path / "bad-ledger.json"
    path.write_text(dumps({**empty_ledger(), "keyed_by": "path"}))

    assert main(["--ledger", str(path)]) == EXIT_CLOSED

    captured = capsys.readouterr()
    assert "GATE" in captured.out
    assert captured.err == ""
