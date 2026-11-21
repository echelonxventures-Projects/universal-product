"""UAIE-000001 — architectural intelligence binding and register-plane validation suite.

Proves the capability, not a description of it:

  * every architectural faculty named in the declaration is bound to a home that resolves
  * every declared symbol exists in one of that faculty's homes (AST, never by import)
  * every faculty is realised by at least one analysis registered in the located analysis
    registry, and that analysis's own home resolves
  * exactly one canonical owner per faculty, and no owner is claimed by two faculties
  * reuse before create — no faculty is bound to an artifact this programme owns
  * the faculty dependency relation is closed, acyclic, and layers into a total order
  * every declared register of the plane resolves, parses, and is claimed by a faculty
  * cross-register consistency — every path any probed register references still exists
  * ontology integration is a binding: every anchor is an element the ontology register
    already declares, so nothing is added to the ontology
  * no parallel authority — the programme is measurably absent from the meta-constitutional
    plane, which is what its SUBSTANTIVE classification requires
  * every contributed analysis is registered under this programme and collides with no
    analysis already registered to another owner
  * every Constitutional Evolution Contract obligation binds to a located owner, a named gate
    and evidence that resolves — the obligation's VERDICT stays with its own gate
  * the change classification, release state and baseline are members of the located registers
    that own those vocabularies, so none of the three can be invented here
  * NON-VACUITY — thirty-three distinct mutations each close the gate; a gate that cannot fail
    proves nothing
  * a declared dimension that is never measured FAILS CLOSED rather than reporting satisfied
  * determinism — two renders of one declaration are byte-identical, and the committed
    registers are the replay of the committed declaration
  * no enumeration — no faculty, owner, home, register, path or anchor is hardcoded
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
PROGRAM_DIR = REPO / "00-MASTER" / "UAIE-000001"
ENGINE_PATH = PROGRAM_DIR / "uaie_engine.py"
DECLARATION_PATH = PROGRAM_DIR / "uaie-architecture.json"


def _load_engine():
    spec = importlib.util.spec_from_file_location("uaie_engine_under_test", ENGINE_PATH)
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


def _faculty(document: dict[str, Any], index: int) -> dict[str, Any]:
    return document["faculties"][index]


# --------------------------------------------------------------------------------------
# the substrate exists
# --------------------------------------------------------------------------------------
def test_the_programme_substrate_is_present():
    assert ENGINE_PATH.is_file(), ENGINE_PATH
    assert DECLARATION_PATH.is_file(), DECLARATION_PATH


def test_the_declaration_declares_its_authority_as_none(declaration):
    """The register must not claim authority it does not hold."""
    assert declaration["programme"]["authority"].startswith("NONE")


def test_creation_is_not_an_admissible_disposition(declaration):
    """A programme that may create cannot prove it reused."""
    assert "CREATE" not in {d["id"] for d in declaration["dispositions"]}


# --------------------------------------------------------------------------------------
# the binding holds on the committed declaration
# --------------------------------------------------------------------------------------
def test_the_gate_is_open_on_the_committed_declaration(engine, declaration):
    model = engine.measure(declaration)
    assert model["blocking_failures"] == [], model["blocking_failures"]
    assert model["gate"] == "OPEN"


def test_every_declared_dimension_is_actually_measured(engine, declaration):
    model = engine.measure(declaration)
    unmeasured = [v["id"] for v in model["validations"] if not v["measured"]]
    assert unmeasured == [], unmeasured


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
    for faculty in declaration["faculties"]:
        available: set[str] = set()
        for home in faculty["homes"]:
            path = REPO / home
            if path.suffix == ".py" and path.is_file():
                available |= engine.module_symbols(path)
        for symbol in faculty["symbols"]:
            assert symbol in available, f"{faculty['id']}: {symbol}"


def test_every_faculty_is_realised_by_a_registered_analysis(engine, declaration):
    """A faculty nobody analyses is a name, not a capability."""
    analyses = engine.registered_analyses(declaration)
    assert analyses, "the located analysis registry could not be read"
    for faculty in declaration["faculties"]:
        assert faculty["analyses"], faculty["id"]
        for identifier in faculty["analyses"]:
            record = analyses.get(identifier)
            assert record is not None, f"{faculty['id']}: {identifier}"
            assert (REPO / record["home"]).exists(), f"{identifier}: {record['home']}"


def test_each_faculty_has_exactly_one_located_canonical_owner(engine, declaration):
    model = engine.measure(declaration)
    owners = [b["canonical_owner"] for b in model["bindings"]]
    assert len(set(owners)) == len(owners), owners
    for owner in owners:
        assert (REPO / owner).exists(), owner


def test_every_faculty_carries_exactly_one_declared_disposition(declaration):
    declared = {d["id"] for d in declaration["dispositions"]}
    for faculty in declaration["faculties"]:
        assert faculty["disposition"] in declared, faculty["id"]


def test_no_faculty_is_left_unbound(declaration):
    for faculty in declaration["faculties"]:
        assert faculty["homes"], faculty["id"]


def test_every_recorded_gap_states_why_it_is_not_closed(declaration):
    """An absence must be disclosed with a reason, not left as a bare flag."""
    for faculty in declaration["faculties"]:
        gap = faculty.get("gap", "")
        if gap:
            assert len(gap.split()) >= 4, faculty["id"]


# --------------------------------------------------------------------------------------
# reuse before create
# --------------------------------------------------------------------------------------
def test_no_faculty_is_bound_to_an_artifact_this_programme_owns(engine, declaration):
    """If this programme realised a faculty itself, that would be creation, not reuse."""
    model = engine.measure(declaration)
    assert engine.check_reuse_before_create(model) == []


def test_a_protected_owner_is_reused_rather_than_replaced(engine, declaration):
    """Every faculty citing a replacement-prohibited record must resolve its homes."""
    model = engine.measure(declaration)
    protected = [b for b in model["bindings"] if b["replacement_prohibited"]]
    assert protected, "no faculty cites a protected catalogue record, so reuse is unproven"
    for binding in protected:
        assert binding["homes_resolved"] > 0, binding["id"]


def test_every_contributed_analysis_is_registered_under_this_programme(engine, declaration):
    model = engine.measure(declaration)
    assert model["contributed_analyses"], "the programme discloses no contribution"
    for contribution in model["contributed_analyses"]:
        assert contribution["registered"], contribution["id"]
        assert contribution["collisions"] == [], contribution["id"]


def test_the_programme_is_absent_from_the_meta_constitutional_plane(engine, declaration):
    """A substantive programme that appeared there would claim standing it does not hold."""
    model = engine.measure(declaration)
    assert model["admission"]["classification"] == "SUBSTANTIVE"
    assert model["admission"]["declared_admitted_to_meta_registry"] is False
    assert model["admission"]["measured_admitted_to_meta_registry"] is False
    assert model["admission"]["meta_identifiers_read"] > 0
    assert engine.check_no_parallel_authority(model) == []


# --------------------------------------------------------------------------------------
# the register plane
# --------------------------------------------------------------------------------------
def test_every_declared_register_resolves_and_is_claimed(engine, declaration):
    model = engine.measure(declaration)
    assert engine.check_register_plane(model) == []
    assert model["counts"]["registers_resolved"] == model["counts"]["registers"]


def test_cross_register_references_all_resolve(engine, declaration):
    """The one measurement no located owner performed: registers read against each other."""
    model = engine.measure(declaration)
    assert model["counts"]["register_references"] > 0, "no register was probed at all"
    broken = [
        f"{f['id']}:{f['references_unresolved']}"
        for f in model["registers"]
        if f["references_unresolved"]
    ]
    assert broken == [], broken


def test_every_ontology_anchor_is_an_element_the_register_already_declares(engine, declaration):
    model = engine.measure(declaration)
    absent = [a["id"] for a in model["ontology_anchors"] if not a["present"]]
    assert absent == [], absent
    assert model["counts"]["ontology_anchors_present"] == model["counts"]["ontology_anchors"]


def test_the_faculty_dependency_relation_is_closed_and_acyclic(engine, declaration):
    model = engine.measure(declaration)
    known = {b["id"] for b in model["bindings"]}
    for node, targets in model["dependency"]["relation"].items():
        for target in targets:
            assert target in known, f"{node} -> {target}"
    assert model["dependency"]["acyclic"] is True
    layered = {node for layer in model["dependency"]["layers"] for node in layer}
    assert layered == known


def test_the_declared_register_roles_are_all_present(engine, declaration):
    for role in (
        engine.ROLE_ANALYSES,
        engine.ROLE_CATALOGUE,
        engine.ROLE_META,
        engine.ROLE_ONTOLOGY,
        engine.ROLE_EVOLUTION,
        engine.ROLE_RELEASE,
        engine.ROLE_BASELINE,
    ):
        assert engine.register_by_role(declaration, role) is not None, role


# --------------------------------------------------------------------------------------
# the Constitutional Evolution Contract
# --------------------------------------------------------------------------------------
def test_every_evolution_obligation_binds_to_a_located_owner_and_gate(engine, declaration):
    """The verdict of an obligation stays with its gate; the binding is what is measured here."""
    model = engine.measure(declaration)
    contract = model["evolution_contract"]
    assert len(contract["obligations"]) == 10, contract["obligations"]
    for obligation in contract["obligations"]:
        assert obligation["owner_paths"], obligation["id"]
        assert obligation["gate"].strip(), obligation["id"]
        assert obligation["discharge"].strip(), obligation["id"]
        assert obligation["owner_paths_resolved"] == len(obligation["owner_paths"]), obligation
        assert obligation["evidence_resolved"] == len(obligation["evidence"]), obligation
    assert engine.check_evolution_contract(model) == []


def test_every_obligation_status_comes_from_the_declared_vocabulary(engine, declaration):
    model = engine.measure(declaration)
    contract = model["evolution_contract"]
    declared = {s["id"] for s in contract["statuses"]}
    for obligation in contract["obligations"]:
        assert obligation["status"] in declared, obligation["id"]


def test_the_classification_release_state_and_baseline_are_owned_vocabulary(engine, declaration):
    """Declaring a class, state or baseline no register admits would be inventing one."""
    model = engine.measure(declaration)
    contract = model["evolution_contract"]
    evolution = engine.register_text(declaration, engine.ROLE_EVOLUTION)
    release = engine.register_text(declaration, engine.ROLE_RELEASE)
    baseline = engine.register_text(declaration, engine.ROLE_BASELINE)
    assert evolution and release and baseline
    assert contract["change_classification"]["label"] in evolution
    assert contract["change_classification"]["token"] in release
    assert contract["release_state"]["state"] in release
    assert contract["baseline"]["id"] in baseline


def test_an_obligation_owner_that_does_not_resolve_closes_the_gate(engine, mutable):
    mutable["evolution_contract"]["obligations"][0]["owner_paths"] = ["00-MASTER/NO-SUCH-OWNER"]
    model = engine.measure(mutable)
    assert model["gate"] == "CLOSED"
    assert "UAIE-VAL-18" in model["blocking_failures"]
    assert engine.check_evolution_contract(model) != []


def test_obligation_evidence_that_does_not_resolve_closes_the_gate(engine, mutable):
    mutable["evolution_contract"]["obligations"][5]["evidence"] = ["no-such-evidence.md"]
    model = engine.measure(mutable)
    assert model["gate"] == "CLOSED"
    assert "UAIE-VAL-18" in model["blocking_failures"]


def test_an_obligation_with_no_located_owner_closes_the_gate(engine, mutable):
    mutable["evolution_contract"]["obligations"][3]["owner_paths"] = []
    model = engine.measure(mutable)
    assert model["gate"] == "CLOSED"
    assert "UAIE-VAL-18" in model["blocking_failures"]


def test_an_undeclared_obligation_status_closes_the_gate(engine, mutable):
    """A status outside the declared vocabulary would let an obligation self-certify."""
    mutable["evolution_contract"]["obligations"][4]["status"] = "PROBABLY-FINE"
    model = engine.measure(mutable)
    assert model["gate"] == "CLOSED"
    assert "UAIE-VAL-18" in model["blocking_failures"]


def test_an_obligation_with_no_named_gate_closes_the_gate(engine, mutable):
    mutable["evolution_contract"]["obligations"][7]["gate"] = ""
    model = engine.measure(mutable)
    assert model["gate"] == "CLOSED"
    assert "UAIE-VAL-18" in model["blocking_failures"]


def test_a_change_class_no_register_admits_closes_the_gate(engine, mutable):
    mutable["evolution_contract"]["change_classification"]["label"] = "Vibe-driven rewrite"
    model = engine.measure(mutable)
    assert model["gate"] == "CLOSED"
    assert "UAIE-VAL-19" in model["blocking_failures"]


def test_a_release_state_no_register_admits_closes_the_gate(engine, mutable):
    mutable["evolution_contract"]["release_state"]["state"] = "SHIPPED-ANYWAY"
    model = engine.measure(mutable)
    assert model["gate"] == "CLOSED"
    assert "UAIE-VAL-19" in model["blocking_failures"]


def test_a_baseline_the_registry_does_not_carry_closes_the_gate(engine, mutable):
    """Rule R-1: a baseline is a row in the registry, never an assertion made elsewhere."""
    mutable["evolution_contract"]["baseline"]["id"] = "UCOS-BASELINE-999"
    model = engine.measure(mutable)
    assert model["gate"] == "CLOSED"
    assert "UAIE-VAL-19" in model["blocking_failures"]


def test_the_contract_referencing_an_undeclared_register_closes_the_gate(engine, mutable):
    mutable["evolution_contract"]["baseline"]["register"] = "UAIE-REG-NOT-DECLARED"
    model = engine.measure(mutable)
    assert model["gate"] == "CLOSED"
    assert "UAIE-VAL-19" in model["blocking_failures"]


# --------------------------------------------------------------------------------------
# NON-VACUITY — the gate must be able to fail
# --------------------------------------------------------------------------------------
def test_a_home_that_does_not_exist_closes_the_gate(engine, mutable):
    _faculty(mutable, 0)["homes"] = ["engine/graph/no_such_module.py"]
    model = engine.measure(mutable)
    assert model["gate"] == "CLOSED"
    assert "UAIE-VAL-01" in model["blocking_failures"]


def test_a_symbol_that_does_not_exist_closes_the_gate(engine, mutable):
    _faculty(mutable, 1)["symbols"] = ["ClassDeletedByRefactor"]
    model = engine.measure(mutable)
    assert model["gate"] == "CLOSED"
    assert "UAIE-VAL-02" in model["blocking_failures"]


def test_an_analysis_that_is_not_registered_closes_the_gate(engine, mutable):
    _faculty(mutable, 2)["analyses"] = ["UAR-NOT-REGISTERED-99"]
    model = engine.measure(mutable)
    assert model["gate"] == "CLOSED"
    assert "UAIE-VAL-03" in model["blocking_failures"]


def test_a_faculty_citing_no_analysis_closes_the_gate(engine, mutable):
    _faculty(mutable, 3)["analyses"] = []
    model = engine.measure(mutable)
    assert model["gate"] == "CLOSED"
    assert "UAIE-VAL-03" in model["blocking_failures"]


def test_a_faculty_bound_to_this_programme_is_rejected(engine, mutable):
    _faculty(mutable, 0)["homes"] = ["00-MASTER/UAIE-000001/uaie_engine.py"]
    model = engine.measure(mutable)
    assert model["gate"] == "CLOSED"
    assert "UAIE-VAL-04" in model["blocking_failures"]
    assert engine.check_reuse_before_create(model) != []


def test_an_unknown_disposition_closes_the_gate(engine, mutable):
    _faculty(mutable, 4)["disposition"] = "CREATE"
    model = engine.measure(mutable)
    assert model["gate"] == "CLOSED"
    assert "UAIE-VAL-05" in model["blocking_failures"]


def test_an_unbound_faculty_closes_the_gate(engine, mutable):
    _faculty(mutable, 5)["homes"] = []
    model = engine.measure(mutable)
    assert model["gate"] == "CLOSED"
    assert "UAIE-VAL-06" in model["blocking_failures"]


def test_two_faculties_claiming_one_home_set_close_the_gate(engine, mutable):
    """An identical binding for two faculties would be duplicate authority over one home."""
    _faculty(mutable, 6)["homes"] = list(_faculty(mutable, 5)["homes"])
    model = engine.measure(mutable)
    assert model["gate"] == "CLOSED"
    assert "UAIE-VAL-07" in model["blocking_failures"]


def test_two_faculties_sharing_a_canonical_owner_close_the_gate(engine, mutable):
    """A shared canonical owner means two faculties are one faculty under two names."""
    _faculty(mutable, 7)["canonical_owner"] = _faculty(mutable, 6)["canonical_owner"]
    model = engine.measure(mutable)
    assert model["gate"] == "CLOSED"
    assert "UAIE-VAL-08" in model["blocking_failures"]


def test_a_canonical_owner_that_does_not_resolve_closes_the_gate(engine, mutable):
    _faculty(mutable, 8)["canonical_owner"] = "engine/no_such_package"
    model = engine.measure(mutable)
    assert model["gate"] == "CLOSED"
    assert "UAIE-VAL-08" in model["blocking_failures"]


def test_a_cycle_in_the_faculty_relation_closes_the_gate(engine, mutable):
    first, second = _faculty(mutable, 0), _faculty(mutable, 1)
    first["depends_on"] = [second["id"]]
    second["depends_on"] = [first["id"]]
    model = engine.measure(mutable)
    assert model["gate"] == "CLOSED"
    assert "UAIE-VAL-09" in model["blocking_failures"]
    assert model["dependency"]["acyclic"] is False


def test_a_dependency_on_an_undeclared_faculty_closes_the_gate(engine, mutable):
    _faculty(mutable, 1)["depends_on"] = ["UAIE-FAC-NONEXISTENT"]
    model = engine.measure(mutable)
    assert model["gate"] == "CLOSED"
    assert "UAIE-VAL-09" in model["blocking_failures"]


def test_a_register_that_does_not_resolve_closes_the_gate(engine, mutable):
    mutable["registers"][0]["path"] = "00-BOOK/DATA/no-such-register.json"
    model = engine.measure(mutable)
    assert model["gate"] == "CLOSED"
    assert "UAIE-VAL-10" in model["blocking_failures"]


def test_a_register_declared_as_data_that_does_not_parse_closes_the_gate(engine, mutable):
    """A register that cannot be read cannot be reasoned over."""
    markdown = next(r for r in mutable["registers"] if r["form"] == "markdown")
    markdown["form"] = "json"
    model = engine.measure(mutable)
    assert model["gate"] == "CLOSED"
    assert "UAIE-VAL-10" in model["blocking_failures"]


def test_a_register_referencing_a_path_that_is_gone_closes_the_gate(engine, mutable):
    """Cross-register drift must be visible even while each owner stays green."""
    probed = next(r for r in mutable["registers"] if r.get("probe"))
    probed["probe"] = {"collection": probed["probe"]["collection"], "field": "name"}
    model = engine.measure(mutable)
    assert model["gate"] == "CLOSED"
    assert "UAIE-VAL-11" in model["blocking_failures"]


def test_an_absent_catalogue_record_closes_the_gate(engine, mutable):
    _faculty(mutable, 1)["catalogue_ids"] = ["RC-does-not-exist"]
    model = engine.measure(mutable)
    assert model["gate"] == "CLOSED"
    assert "UAIE-VAL-12" in model["blocking_failures"]


def test_an_ontology_anchor_that_is_absent_from_the_register_closes_the_gate(engine, mutable):
    mutable["ontology_anchors"][0]["id"] = "ONT-NOT-IN-THE-REGISTER-9999"
    model = engine.measure(mutable)
    assert model["gate"] == "CLOSED"
    assert "UAIE-VAL-13" in model["blocking_failures"]


def test_a_contributed_analysis_that_is_not_registered_closes_the_gate(engine, mutable):
    mutable["contributed_analyses"][0]["id"] = "UAR-AIE-UNREGISTERED"
    model = engine.measure(mutable)
    assert model["gate"] == "CLOSED"
    assert "UAIE-VAL-14" in model["blocking_failures"]


def test_a_contributed_analysis_whose_name_is_already_owned_closes_the_gate(engine, mutable):
    """Adding a name another owner already holds would be a duplicate capability."""
    analyses = engine.registered_analyses(mutable)
    taken = next(
        record["name"]
        for record in analyses.values()
        if not record["home"].startswith("00-MASTER/UAIE-000001/")
    )
    mutable["contributed_analyses"][0]["name"] = taken
    model = engine.measure(mutable)
    assert model["gate"] == "CLOSED"
    assert "UAIE-VAL-14" in model["blocking_failures"]


def test_an_undisclosed_gap_closes_the_gate(engine, mutable):
    _faculty(mutable, 0)["gap"] = "missing"
    model = engine.measure(mutable)
    assert model["gate"] == "CLOSED"
    assert "UAIE-VAL-15" in model["blocking_failures"]


def test_claiming_admission_to_the_meta_constitutional_registry_closes_the_gate(engine, mutable):
    """The declared admission determination must match what the meta plane actually holds."""
    mutable["admission_determination"]["admitted_to_meta_registry"] = True
    model = engine.measure(mutable)
    assert model["gate"] == "CLOSED"
    assert "UAIE-VAL-16" in model["blocking_failures"]
    assert engine.check_no_parallel_authority(model) != []


def test_a_register_no_faculty_claims_closes_the_gate(engine, mutable):
    """A subject the mission requires must actually be reasoned over by some faculty."""
    orphan = mutable["registers"][0]["id"]
    for faculty in mutable["faculties"]:
        faculty["registers"] = [r for r in faculty["registers"] if r != orphan]
    model = engine.measure(mutable)
    assert model["gate"] == "CLOSED"
    assert "UAIE-VAL-17" in model["blocking_failures"]


def test_a_faculty_referencing_an_undeclared_register_closes_the_gate(engine, mutable):
    _faculty(mutable, 0)["registers"].append("UAIE-REG-NOT-DECLARED")
    model = engine.measure(mutable)
    assert model["gate"] == "CLOSED"
    assert "UAIE-VAL-17" in model["blocking_failures"]


def test_a_declared_dimension_with_no_measurement_fails_closed(engine, mutable):
    """Absence of evidence is never evidence: an unmeasured dimension must not report PASS."""
    mutable["validations"].append(
        {
            "id": "UAIE-VAL-NEVER-MEASURED",
            "dimension": "an invented dimension",
            "obligation": "never measured by the engine",
            "blocking": True,
        }
    )
    model = engine.measure(mutable)
    invented = next(v for v in model["validations"] if v["id"] == "UAIE-VAL-NEVER-MEASURED")
    assert invented["measured"] is False
    assert invented["satisfied"] is False
    assert model["gate"] == "CLOSED"


# --------------------------------------------------------------------------------------
# fail-closed on an unusable declaration
# --------------------------------------------------------------------------------------
def test_a_declaration_missing_a_required_key_aborts_fail_closed(engine, mutable, monkeypatch):
    """An unusable declaration yields no determination at all, not a passing one."""
    del mutable["faculties"]
    monkeypatch.setattr(engine, "load_declaration", lambda: mutable)
    with pytest.raises(KeyError):
        engine.measure(mutable)


def test_the_loader_rejects_a_declaration_without_faculties(engine, tmp_path, monkeypatch):
    broken = tmp_path / "uaie-architecture.json"
    broken.write_text(
        json.dumps(
            {
                "programme": {},
                "admission_determination": {},
                "dispositions": [],
                "ontology_anchors": [],
                "registers": [{"id": "R"}],
                "faculties": [],
                "contributed_analyses": [],
                "validations": [],
            }
        ),
        "utf-8",
    )
    monkeypatch.setattr(engine, "DECLARATION", broken)
    with pytest.raises(engine.FailClosed):
        engine.load_declaration()


# --------------------------------------------------------------------------------------
# determinism, enumeration, write scope, replay
# --------------------------------------------------------------------------------------
def test_two_renders_of_one_declaration_are_byte_identical(engine, declaration):
    first = engine.render(engine.measure(declaration))
    second = engine.render(engine.measure(copy.deepcopy(declaration)))
    assert first == second


def test_the_seal_changes_when_a_measured_fact_changes(engine, declaration, mutable):
    """A seal that does not move with the measurement would certify nothing."""
    baseline = engine.measure(declaration)["seal_sha256"]
    _faculty(mutable, 0)["homes"] = ["engine/graph/no_such_module.py"]
    assert engine.measure(mutable)["seal_sha256"] != baseline


def test_no_declared_identifier_name_or_path_is_hardcoded_in_the_engine(engine, declaration):
    """Adding a faculty or a register must be a data edit; the engine may not carry the list."""
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


def test_the_declaration_guard_accepts_the_committed_declaration(engine, declaration):
    assert engine.check_declaration(declaration) == []
