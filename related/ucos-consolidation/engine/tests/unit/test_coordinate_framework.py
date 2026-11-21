"""UCCFA-000001 — the coordinate framework alignment gate.

Every law is exercised in BOTH directions. A law that only ever passes is a law nobody has
shown can fail, so each check below is also handed a declaration that violates it and must
refuse: `engine/coordinate_framework/gate.py` is a detector, and a detector with no failing
case is a detector nobody has shown can fail.
"""

from __future__ import annotations

import copy
import json

import pytest

# The private helpers belong to the module that defines them rather than to the package's
# public surface, so they are named from there instead of being re-exported to suit a test.
import engine.coordinate_framework.contract as contract_module
from engine.coordinate_framework import (
    CoordinateAlignmentError,
    CoordinateContract,
    assess,
    declaration_path,
    load_contract,
    load_declaration,
    repo_root,
)
from engine.coordinate_framework.contract import (
    _part,
    _primitive_elements,
    _row,
)
from engine.coordinate_framework.contract import (
    check_every_absolute_law_is_counted_where_it_is_carried as l07,
)
from engine.coordinate_framework.gate import EXIT_CLOSED, EXIT_FAULT, EXIT_OPEN, main, measure


@pytest.fixture(scope="module")
def document() -> dict:
    return load_declaration()


@pytest.fixture(scope="module")
def repo() -> str:
    return repo_root()


def _elsewhere(tmp_path, document: dict) -> str:
    target = tmp_path / "uccfa-declaration.json"
    target.write_text(json.dumps(document), encoding="utf-8")
    return str(target)


def _measure(tmp_path, document: dict) -> dict:
    return measure(_elsewhere(tmp_path, document))


def _refusals(report: dict, law_id: str) -> list[str]:
    return next(law["violations"] for law in report["laws"] if law["law_id"] == law_id)


# --- the declaration as it stands -------------------------------------------------------


def test_the_gate_is_open_over_the_repository_as_it_stands():
    report = measure()
    assert report["holds"], [law for law in report["laws"] if not law["holds"]]
    assert report["coordinates"] == 5


def test_measuring_twice_produces_the_same_report():
    # No clock, no network, no subprocess: one state must yield one report, or the digest
    # below identifies nothing.
    assert measure() == measure()


def test_a_changed_declaration_changes_the_reported_identity(tmp_path, document):
    altered = copy.deepcopy(document)
    altered["version"] = "9.9"
    assert measure()["declaration_digest"] != _measure(tmp_path, altered)["declaration_digest"]


def test_every_declared_law_is_measured_and_every_check_is_declared(document, repo):
    contract = CoordinateContract.of(document)
    assessed = {law_id for law_id, _, _ in assess(contract, repo)}
    assert assessed == {str(law["id"]) for law in document["laws"]}


# --- each law refuses what it exists to refuse -------------------------------------------


def test_l01_refuses_a_coordinate_the_register_does_not_carry(tmp_path, document):
    altered = copy.deepcopy(document)
    altered["coordinate_binding"][0]["element"] = "HYPERSPACE"
    assert _refusals(_measure(tmp_path, altered), "UCCFA-L-01")


def test_l02_refuses_a_standing_the_ratification_record_does_not_grant(tmp_path, document):
    altered = copy.deepcopy(document)
    altered["ratified_standing"][0]["evidence_phrase"] = "ratified as a root primitive"
    assert _refusals(_measure(tmp_path, altered), "UCCFA-L-02")


def test_l03_refuses_an_element_bound_as_both_primitive_and_coordinate(tmp_path, document):
    altered = copy.deepcopy(document)
    altered["coordinate_binding"][0]["element"] = "TRANSFORMATION"
    assert _refusals(_measure(tmp_path, altered), "UCCFA-L-03")


def test_l04_refuses_an_equation_term_bound_by_nothing(tmp_path, document):
    altered = copy.deepcopy(document)
    altered["coordinate_binding"] = altered["coordinate_binding"][:-1]
    assert _refusals(_measure(tmp_path, altered), "UCCFA-L-04")


def test_l05_refuses_a_superseded_element_resolving_into_an_unbound_coordinate(tmp_path, document):
    altered = copy.deepcopy(document)
    altered["superseded_root_element"]["resolves_into"] = ["ONT-06", "ONT-99"]
    assert _refusals(_measure(tmp_path, altered), "UCCFA-L-05")


def test_l05_refuses_a_superseded_element_the_register_does_not_carry(tmp_path, document):
    altered = copy.deepcopy(document)
    altered["superseded_root_element"]["id"] = "ONT-99"
    assert _refusals(_measure(tmp_path, altered), "UCCFA-L-05")


def test_l06_refuses_a_bound_element_the_omega_law_does_not_name(tmp_path, document):
    altered = copy.deepcopy(document)
    altered["omega_law_binding"]["dimensions"] = [
        name for name in altered["omega_law_binding"]["dimensions"] if name != "SCALE"
    ]
    assert _refusals(_measure(tmp_path, altered), "UCCFA-L-06")


def test_l06_refuses_when_the_law_carries_no_row(tmp_path, document):
    altered = copy.deepcopy(document)
    altered["omega_law_binding"]["law_id"] = "Ω∞-999"
    assert _refusals(_measure(tmp_path, altered), "UCCFA-L-06")


def test_l07_counts_exactly_the_twenty_one_absolute_laws():
    # The register carries the twenty-one ratified laws, Ω∞-000 through Ω∞-020, and the
    # check must count every one of them exactly once: a law the count omitted would read
    # as ratified-and-unmeasured, which is the state UCCFA-L-07 exists to refuse.
    assert l07(load_contract(), repo_root()) == ()


def test_l07_refuses_a_law_the_register_no_longer_carries(tmp_path, monkeypatch):
    register = f"{repo_root()}/02-MASTER/UCOS-ABSOLUTE-CONSTITUTIONAL-LAWS-REGISTER.md"
    with open(register, encoding="utf-8") as handle:
        text = handle.read()
    stripped = "\n".join(line for line in text.splitlines() if "**Ω∞-014**" not in line)
    monkeypatch.setattr(
        contract_module, "_read", lambda repo, rel: stripped if "LAWS-REGISTER" in rel else ""
    )
    findings = l07(load_contract(), ".")
    assert any("Ω∞-014: carried by no row" in f for f in findings), findings


def test_l07_refuses_a_duplicate_law_row(tmp_path, monkeypatch):
    register = f"{repo_root()}/02-MASTER/UCOS-ABSOLUTE-CONSTITUTIONAL-LAWS-REGISTER.md"
    with open(register, encoding="utf-8") as handle:
        lines = handle.read().splitlines()
    row = next(line for line in lines if "**Ω∞-020**" in line)
    doubled = "\n".join([*lines, row])
    monkeypatch.setattr(
        contract_module, "_read", lambda repo, rel: doubled if "LAWS-REGISTER" in rel else ""
    )
    findings = l07(load_contract(), ".")
    assert any("Ω∞-020: carried by 2 rows" in f for f in findings), findings


def test_l07_refuses_a_row_the_named_set_does_not_carry(tmp_path, monkeypatch) -> None:
    """A row whose id is outside Ω∞-000…020 is refused, not counted.

    The named expectation is what makes the count informative: a register that grew an
    extra law would otherwise be "fully measured" while the programme silently ignored
    one of its rows.
    """
    register = f"{repo_root()}/02-MASTER/UCOS-ABSOLUTE-CONSTITUTIONAL-LAWS-REGISTER.md"
    with open(register, encoding="utf-8") as handle:
        lines = handle.read().splitlines()
    widened = "\n".join([*lines, "| **Ω∞-999** | A law outside the ratified set. |"])
    monkeypatch.setattr(
        contract_module, "_read", lambda repo, rel: widened if "LAWS-REGISTER" in rel else ""
    )
    findings = l07(load_contract(), ".")
    assert any("Ω∞-999" in f and "does not carry" in f for f in findings), findings


def test_l07_refuses_a_register_row_that_states_nothing(tmp_path, monkeypatch) -> None:
    """An empty statement cell is not a ratified law; it is a lost one.

    The check counts rows, and a row that carries no text would make the count right and
    the knowledge absent — the exact shape UCKP-ART-06 refuses.
    """
    register = f"{repo_root()}/02-MASTER/UCOS-ABSOLUTE-CONSTITUTIONAL-LAWS-REGISTER.md"
    with open(register, encoding="utf-8") as handle:
        lines = handle.read().splitlines()
    emptied = ["| **Ω∞-002** |  |" if "**Ω∞-002**" in ln else ln for ln in lines]
    monkeypatch.setattr(
        contract_module,
        "_read",
        lambda repo, rel: "\n".join(emptied) if "LAWS-REGISTER" in rel else "",
    )
    findings = l07(load_contract(), ".")
    assert any("states nothing" in f for f in findings), findings


# --- faults are not verdicts --------------------------------------------------------------


def test_an_absent_declaration_is_a_fault(tmp_path, capsys):
    assert main(["--declaration", str(tmp_path / "nowhere.json")]) == EXIT_FAULT
    assert "FAULT" in capsys.readouterr().err


def test_a_declaration_that_is_not_json_is_a_fault(tmp_path, capsys):
    target = tmp_path / "uccfa-declaration.json"
    target.write_text("{not json", encoding="utf-8")
    assert main(["--declaration", str(target)]) == EXIT_FAULT
    assert "not valid JSON" in capsys.readouterr().err


def test_a_declaration_missing_a_required_section_is_a_fault(tmp_path, document, capsys):
    altered = copy.deepcopy(document)
    del altered["coordinate_binding"]
    assert main(["--declaration", _elsewhere(tmp_path, altered)]) == EXIT_FAULT
    assert "coordinate_binding" in capsys.readouterr().err


def test_a_declared_law_that_names_no_check_is_a_fault(document, repo):
    altered = copy.deepcopy(document)
    altered["laws"] = [*altered["laws"], {"id": "UCCFA-L-99", "title": "invented"}]
    with pytest.raises(CoordinateAlignmentError, match="names no check"):
        assess(CoordinateContract.of(altered), repo)


def test_a_declared_law_naming_a_check_that_does_not_exist_is_a_fault(document, repo):
    # Distinct from the case above and worth distinguishing: a law that forgot to name its
    # check and a law naming one nobody wrote are different mistakes, and a single message
    # for both would send the reader to the wrong file.
    altered = copy.deepcopy(document)
    altered["laws"] = [
        *altered["laws"],
        {"id": "UCCFA-L-99", "title": "invented", "check": "a_check_nobody_wrote"},
    ]
    with pytest.raises(CoordinateAlignmentError, match="no check implements"):
        assess(CoordinateContract.of(altered), repo)


def test_a_check_no_declared_law_names_is_a_fault(document, repo):
    altered = copy.deepcopy(document)
    altered["laws"] = altered["laws"][:-1]
    with pytest.raises(CoordinateAlignmentError, match="no declared law names"):
        assess(CoordinateContract.of(altered), repo)


# --- the CLI --------------------------------------------------------------------------------


def test_the_cli_reports_open(capsys):
    assert main([]) == EXIT_OPEN
    assert "VERDICT: OPEN" in capsys.readouterr().out


def test_the_cli_can_emit_json(capsys):
    assert main(["--json"]) == EXIT_OPEN
    assert json.loads(capsys.readouterr().out)["artifact_id"] == "UCCFA-000001"


def test_the_cli_closes_on_a_refused_law(tmp_path, document, capsys):
    altered = copy.deepcopy(document)
    altered["coordinate_binding"][0]["element"] = "HYPERSPACE"
    assert main(["--declaration", _elsewhere(tmp_path, altered)]) == EXIT_CLOSED
    assert "VERDICT: CLOSED" in capsys.readouterr().out


def test_the_declaration_path_is_the_binding():
    assert declaration_path().endswith("00-MASTER/UCCFA-000001/uccfa-declaration.json")
    assert load_contract().artifact_id == "UCCFA-000001"


def test_a_declaration_that_is_not_an_object_is_a_fault(tmp_path):
    target = tmp_path / "uccfa-declaration.json"
    target.write_text("[]", encoding="utf-8")
    with pytest.raises(CoordinateAlignmentError, match="not an object"):
        load_declaration(str(target))


@pytest.mark.parametrize("field", ["artifact_id", "name", "version", "authority", "principle"])
def test_a_declaration_missing_a_stated_field_is_a_fault(document, field):
    altered = copy.deepcopy(document)
    del altered[field]
    with pytest.raises(CoordinateAlignmentError, match=field):
        CoordinateContract.of(altered)


@pytest.mark.parametrize(
    "section", ["ontology_source", "superseded_root_element", "omega_law_binding"]
)
def test_a_declaration_missing_a_stated_object_is_a_fault(document, section):
    altered = copy.deepcopy(document)
    altered[section] = {}
    with pytest.raises(CoordinateAlignmentError, match=section):
        CoordinateContract.of(altered)


def test_an_unreadable_declared_surface_is_a_fault(tmp_path, document):
    altered = copy.deepcopy(document)
    altered["ontology_source"]["canonical_owner"] = "01-WORKING/NO-SUCH-REGISTER.md"
    with pytest.raises(CoordinateAlignmentError, match="unreadable"):
        measure(_elsewhere(tmp_path, altered))


# --- the helpers, exercised where a whole-declaration case cannot reach them ---------------


def test_a_section_that_runs_to_the_end_of_the_document_is_read_whole():
    # PART B is not the last section of the real register, so the loop always breaks there.
    # A document whose section IS last exercises the other exit.
    document = "## PART A — ROOT\n| ONT-01 | BEING |\n## PART B — COORD\n| ONT-06 | SPACE |"
    body = _part(document, "PART B")
    assert body.strip() == "| ONT-06 | SPACE |"


def test_a_row_the_register_does_not_carry_is_the_empty_string():
    assert _row("| ONT-06 | SPACE |", "ONT-99") == ""


def test_an_unreadable_ucpa_declaration_is_a_fault(tmp_path):
    # Reached directly: every law that consults UCPA is preceded by one that reads the
    # register, so a repository without UCPA fails earlier for a different reason.
    with pytest.raises(CoordinateAlignmentError, match="UCPA-000001 declaration is unreadable"):
        _primitive_elements(str(tmp_path))


def test_l02_refuses_a_ratification_id_the_record_does_not_carry(tmp_path, document):
    altered = copy.deepcopy(document)
    altered["ontology_source"]["ratified_by"] = "SUP-99"
    assert "carries no row" in _refusals(_measure(tmp_path, altered), "UCCFA-L-02")[0]


def test_l05_refuses_when_part_a_does_not_record_the_supersession(tmp_path, document):
    altered = copy.deepcopy(document)
    altered["superseded_root_element"]["superseded_by"] = "SUP-99"
    assert any("does not record" in f for f in _refusals(_measure(tmp_path, altered), "UCCFA-L-05"))


def test_l05_refuses_an_evidence_phrase_part_a_does_not_carry(tmp_path, document):
    altered = copy.deepcopy(document)
    altered["superseded_root_element"]["evidence_phrase"] = "ratified as a root primitive"
    assert any("does not carry" in f for f in _refusals(_measure(tmp_path, altered), "UCCFA-L-05"))


def test_l05_refuses_a_superseded_element_ucpa_still_binds(tmp_path, document):
    altered = copy.deepcopy(document)
    altered["superseded_root_element"]["element"] = "TRANSFORMATION"
    refusals = _refusals(_measure(tmp_path, altered), "UCCFA-L-05")
    assert any("bound as a primitive" in f for f in refusals)


def test_l05_refuses_a_superseded_element_this_declaration_binds(tmp_path, document):
    altered = copy.deepcopy(document)
    altered["superseded_root_element"]["element"] = "SPACE"
    refusals = _refusals(_measure(tmp_path, altered), "UCCFA-L-05")
    assert any("bound as a coordinate" in f for f in refusals)


def test_l06_refuses_a_dimension_the_law_does_not_name(tmp_path, document):
    altered = copy.deepcopy(document)
    dimensions = altered["omega_law_binding"]["dimensions"]
    altered["omega_law_binding"]["dimensions"] = [*dimensions, "FLAVOUR"]
    assert any("not named by" in f for f in _refusals(_measure(tmp_path, altered), "UCCFA-L-06"))
