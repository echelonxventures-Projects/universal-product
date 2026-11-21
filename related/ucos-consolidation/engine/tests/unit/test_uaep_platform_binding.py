"""UAEP-000001 — platform capability binding validation suite.

Proves the capability, not a description of it:

  * every capability named in the declaration is bound to a home that resolves on disk
  * every declared symbol actually exists in one of that capability's homes (AST, no import)
  * every declared disposition comes from the declared closed set   (totality)
  * reuse before create — no capability is bound to an artifact this programme owns
  * every declared vocabulary is open: its registrar exists in its declared home
  * every declared pipeline category is seeded by the framework, not by this programme
  * NON-VACUITY — a fabricated home, a fabricated symbol, a self-binding and a declared
    dimension with no measurement each close the gate; a gate that cannot fail proves nothing
  * a declared dimension that is never measured FAILS CLOSED rather than reporting satisfied
  * determinism — two renders of one declaration are byte-identical
  * no enumeration — no capability id or name is hardcoded in the engine source
  * write scope — every rendered target is a plain filename inside the programme directory

The mutation scenarios are hermetic: the declaration is deep-copied in memory and measured
directly, so no scenario writes to the repository or depends on untracked local state.
"""

from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
from typing import Any

import pytest

REPO = Path(__file__).resolve().parents[3]
PROGRAM_DIR = REPO / "00-MASTER" / "UAEP-000001"
ENGINE_PATH = PROGRAM_DIR / "uaep_engine.py"
DECLARATION_PATH = PROGRAM_DIR / "uaep-platform.json"


def _load_engine():
    spec = importlib.util.spec_from_file_location("uaep_engine_under_test", ENGINE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def engine():
    return _load_engine()


@pytest.fixture(scope="module")
def declaration() -> dict[str, Any]:
    return json.loads(DECLARATION_PATH.read_text("utf-8"))


@pytest.fixture
def mutable(declaration: dict[str, Any]) -> dict[str, Any]:
    """A private deep copy, so a mutation scenario can never touch the committed declaration."""
    return copy.deepcopy(declaration)


# --------------------------------------------------------------------------------------
# the substrate exists
# --------------------------------------------------------------------------------------
def test_the_programme_substrate_is_present():
    assert ENGINE_PATH.is_file(), ENGINE_PATH
    assert DECLARATION_PATH.is_file(), DECLARATION_PATH


def test_the_declaration_declares_its_authority_as_none(declaration):
    """The register must not claim authority it does not hold."""
    assert declaration["programme"]["authority"].startswith("NONE")


# --------------------------------------------------------------------------------------
# the binding holds on the committed declaration
# --------------------------------------------------------------------------------------
def test_the_gate_is_open_on_the_committed_declaration(engine, declaration):
    model = engine.measure(declaration)
    assert model["blocking_failures"] == [], model["blocking_failures"]
    assert model["gate"] == "OPEN"


def test_every_declared_home_resolves_on_disk(engine, declaration):
    model = engine.measure(declaration)
    unresolved = [
        f"{b['id']}:{home}"
        for b in model["bindings"]
        for home in b["homes"]
        if not (REPO / home).exists()
    ]
    assert unresolved == [], unresolved
    assert model["counts"]["homes_resolved"] == model["counts"]["homes_declared"]


def test_every_declared_symbol_exists_in_one_of_its_homes(engine, declaration):
    """Declared symbols are resolved by parsing, never by importing the measured module."""
    for capability in declaration["capabilities"]:
        available: set[str] = set()
        for home in capability["homes"]:
            path = REPO / home
            if path.suffix == ".py" and path.is_file():
                available |= engine.module_symbols(path)
        for symbol in capability["symbols"]:
            assert symbol in available, f"{capability['id']}: {symbol}"


def test_every_capability_carries_exactly_one_declared_disposition(engine, declaration):
    declared = {d["id"] for d in declaration["dispositions"]}
    for capability in declaration["capabilities"]:
        assert capability["disposition"] in declared, capability["id"]


def test_no_capability_is_left_unbound(declaration):
    for capability in declaration["capabilities"]:
        assert capability["homes"], capability["id"]


def test_every_recorded_gap_states_why_it_is_not_closed(declaration):
    """An absence must be disclosed with a reason, not left as a bare flag."""
    for capability in declaration["capabilities"]:
        gap = capability.get("gap", "")
        if gap:
            assert len(gap.split()) >= 4, capability["id"]


# --------------------------------------------------------------------------------------
# reuse before create
# --------------------------------------------------------------------------------------
def test_no_capability_is_bound_to_an_artifact_this_programme_owns(engine, declaration):
    """If this programme realised a capability itself, that would be creation, not reuse."""
    model = engine.measure(declaration)
    assert engine.check_reuse_before_create(model) == []


def test_a_protected_owner_is_reused_rather_than_replaced(engine, declaration):
    """Every capability citing a replacement-prohibited record must resolve its homes."""
    model = engine.measure(declaration)
    for binding in model["bindings"]:
        if binding["replacement_prohibited"]:
            assert binding["homes_resolved"] > 0, binding["id"]


# --------------------------------------------------------------------------------------
# open world
# --------------------------------------------------------------------------------------
def test_every_declared_vocabulary_registrar_exists(engine, declaration):
    for vocabulary in declaration["vocabularies"]:
        home = REPO / vocabulary["registrar_home"]
        assert home.is_file(), vocabulary["id"]
        assert vocabulary["registrar"] in engine.module_symbols(home), vocabulary["id"]


def test_every_declared_pipeline_category_is_seeded_by_the_framework(engine, declaration):
    """The categories must be admitted by the framework's own vocabulary, not by this register.

    This is what keeps the pipeline space open: a category is data in the framework, so this
    programme can name one only if the framework already admits it.
    """
    seeded = engine.seed_pipeline_types(declaration)
    assert seeded, "the framework seed vocabulary could not be read"
    missing = [t for t in declaration["declared_pipeline_types"] if t not in seeded]
    assert missing == [], missing


# --------------------------------------------------------------------------------------
# NON-VACUITY — the gate must be able to fail
# --------------------------------------------------------------------------------------
def test_a_home_that_does_not_exist_closes_the_gate(engine, mutable):
    mutable["capabilities"][0]["homes"] = ["platform/universal_pipeline/no_such_module.py"]
    model = engine.measure(mutable)
    assert model["gate"] == "CLOSED"
    assert "UAEP-VAL-01" in model["blocking_failures"]


def test_a_symbol_that_does_not_exist_closes_the_gate(engine, mutable):
    mutable["capabilities"][1]["symbols"] = ["ClassDeletedByRefactor"]
    model = engine.measure(mutable)
    assert model["gate"] == "CLOSED"
    assert "UAEP-VAL-03" in model["blocking_failures"]


def test_a_capability_bound_to_this_programme_is_rejected(engine, mutable):
    mutable["capabilities"][0]["homes"] = ["00-MASTER/UAEP-000001/uaep_engine.py"]
    model = engine.measure(mutable)
    assert model["gate"] == "CLOSED"
    assert "UAEP-VAL-04" in model["blocking_failures"]
    assert engine.check_reuse_before_create(model) != []


def test_an_unknown_disposition_closes_the_gate(engine, mutable):
    mutable["capabilities"][2]["disposition"] = "REPLACE"
    model = engine.measure(mutable)
    assert model["gate"] == "CLOSED"
    assert "UAEP-VAL-05" in model["blocking_failures"]


def test_an_absent_catalogue_record_closes_the_gate(engine, mutable):
    mutable["capabilities"][1]["catalogue_ids"] = ["RC-does-not-exist"]
    model = engine.measure(mutable)
    assert model["gate"] == "CLOSED"
    assert "UAEP-VAL-02" in model["blocking_failures"]


def test_two_capabilities_claiming_one_home_set_close_the_gate(engine, mutable):
    """An identical binding for two capabilities would be duplicate authority over one home."""
    mutable["capabilities"][4]["homes"] = list(mutable["capabilities"][3]["homes"])
    model = engine.measure(mutable)
    assert model["gate"] == "CLOSED"
    assert "UAEP-VAL-09" in model["blocking_failures"]


def test_a_declared_dimension_with_no_measurement_fails_closed(engine, mutable):
    """Absence of evidence is never evidence: an unmeasured dimension must not report PASS."""
    mutable["validations"].append(
        {
            "id": "UAEP-VAL-NEVER-MEASURED",
            "dimension": "an invented dimension",
            "obligation": "never measured by the engine",
            "blocking": True,
        }
    )
    model = engine.measure(mutable)
    invented = next(v for v in model["validations"] if v["id"] == "UAEP-VAL-NEVER-MEASURED")
    assert invented["measured"] is False
    assert invented["satisfied"] is False
    assert model["gate"] == "CLOSED"


def test_an_unseeded_pipeline_category_closes_the_gate(engine, mutable):
    mutable["declared_pipeline_types"].append("a-category-the-framework-does-not-admit")
    model = engine.measure(mutable)
    assert model["gate"] == "CLOSED"
    assert "UAEP-VAL-08" in model["blocking_failures"]


# --------------------------------------------------------------------------------------
# determinism, enumeration, write scope
# --------------------------------------------------------------------------------------
def test_two_renders_of_one_declaration_are_byte_identical(engine, declaration):
    first = engine.render(engine.measure(declaration))
    second = engine.render(engine.measure(copy.deepcopy(declaration)))
    assert first == second


def test_the_seal_changes_when_a_measured_fact_changes(engine, declaration, mutable):
    """A seal that does not move with the measurement would certify nothing."""
    baseline = engine.measure(declaration)["seal_sha256"]
    mutable["capabilities"][0]["homes"] = ["platform/universal_pipeline/no_such_module.py"]
    assert engine.measure(mutable)["seal_sha256"] != baseline


def test_no_capability_id_or_name_is_hardcoded_in_the_engine(engine, declaration):
    """Adding a capability must be a data edit; the engine may not carry the capability list."""
    assert engine.check_no_enumeration(declaration) == []


def test_every_rendered_target_is_a_plain_filename_inside_the_programme(engine, declaration):
    """The engine must not be able to write outside its own programme directory."""
    for name in engine.render(engine.measure(declaration)):
        assert "/" not in name and ".." not in name, name
        assert (PROGRAM_DIR / name).resolve().parent == PROGRAM_DIR.resolve()
    assert engine.check_write_scope() == []


def test_the_committed_registers_match_a_replay_of_the_committed_declaration(engine, declaration):
    """The registers in the tree must be the deterministic product of the declaration."""
    rendered = engine.render(engine.measure(declaration))
    for name, expected in rendered.items():
        committed = (PROGRAM_DIR / name).read_text("utf-8")
        body = expected if expected.endswith("\n") else expected + "\n"
        assert committed == body, name
