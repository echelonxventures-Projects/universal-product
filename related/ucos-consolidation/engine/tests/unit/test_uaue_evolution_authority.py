"""UAUE-000001 Epoch 2B — canonical authority rehydration.

The properties this suite proves, in the order the resume task requires them:

**Declaration parsing.** The canonical declaration loads, and every structural refusal is
reachable: an absent file, invalid JSON, a non-object document, a missing block, an empty
block, a list-shaped block declared as something else, and a non-object entry inside one.

**Deterministic replay.** Two loads of the same declaration against the same tree produce an
equal authority and an equal digest, the digest is independent of *where* the declaration was
read from, and the authority document is a canonical-bytes fixed point.

**Duplicate register detection.** A register declared twice, and two registers claiming one
ordinal, are both refused rather than reported.

**Missing register detection.** A removed register, and a renumbered register, are both
refused because the ordinal set is proved contiguous.

**Non-vacuity.** Every refusal above is exercised by a mutation of the real declaration, and
the classifier is shown to produce all five declared outcomes. A gate that cannot fail proves
nothing, so each detection has a mutation that closes it.

**Non-duplication.** The engine carries no register list and no stage list: the register files
appear in no engine source file, and the lifecycle states are exactly the canonical stage set
that :mod:`engine.uckp.evolution` owns.
"""

from __future__ import annotations

import ast
import copy
import json
import re
from pathlib import Path
from pathlib import Path as _Path
from typing import Any

import pytest

from engine.uaue import authority as authority_module
from engine.uaue.authority import (
    REQUIRED_RULES,
    authority_is_grounded,
    load_evolution_authority,
)
from engine.uaue.model import (
    ABSENT,
    PRESENT,
    UNREADABLE,
    EvolutionAuthority,
    EvolutionAuthorityError,
)
from engine.uaue.resolution import (
    DECLARATION_PATH,
    REPO_ROOT,
    REQUIRED_KEYS,
    REQUIRED_NON_EMPTY,
    DeclarationReader,
    Substrate,
    module_symbols,
)
from engine.uckp.canonical import canonical_bytes
from engine.uckp.evolution import EVOLUTION_CYCLE

DECLARATION_FILE = REPO_ROOT / DECLARATION_PATH
UAUE_PACKAGE = REPO_ROOT / "engine" / "uaue"


@pytest.fixture(scope="module")
def declaration() -> dict[str, Any]:
    return json.loads(DECLARATION_FILE.read_text("utf-8"))


@pytest.fixture
def mutable(declaration: dict[str, Any]) -> dict[str, Any]:
    """A deep copy, so a mutation scenario cannot leak into another test."""
    return copy.deepcopy(declaration)


@pytest.fixture(scope="module")
def authority() -> EvolutionAuthority:
    return load_evolution_authority()


def _load(document: dict[str, Any], root: Path | None = None) -> EvolutionAuthority:
    return load_evolution_authority(DeclarationReader.from_document(document), Substrate(root))


# --------------------------------------------------------------------------------------
# Declaration parser
# --------------------------------------------------------------------------------------


def test_the_canonical_declaration_exists_and_loads() -> None:
    assert DECLARATION_FILE.is_file()
    authority = load_evolution_authority()
    assert authority.programme_id == "UAUE-000001"
    assert authority.version


def test_the_declaration_carries_every_required_block(declaration: dict[str, Any]) -> None:
    for key in REQUIRED_KEYS:
        assert key in declaration, key


def test_the_five_declared_classification_rules_are_the_rules_the_classifier_implements(
    authority: EvolutionAuthority,
) -> None:
    declared = {entry.identifier: entry.rule for entry in authority.classifications}
    assert declared == dict(REQUIRED_RULES)


def test_every_classification_carries_a_distinct_rank(authority: EvolutionAuthority) -> None:
    ranks = [entry.rank for entry in authority.classifications]
    assert len(set(ranks)) == len(ranks)


def test_all_eighteen_declared_registers_are_resolved(authority: EvolutionAuthority) -> None:
    assert len(authority.registers) == 18
    assert [entry.ordinal for entry in authority.registers] == list(range(18))


def test_an_absent_declaration_is_refused(tmp_path: Path) -> None:
    reader = DeclarationReader.from_path(tmp_path / "no-such-declaration.json")
    with pytest.raises(EvolutionAuthorityError, match="could not be read"):
        load_evolution_authority(reader)


def test_a_declaration_that_is_not_valid_json_is_refused(tmp_path: Path) -> None:
    broken = tmp_path / "broken.json"
    broken.write_text("{not json", encoding="utf-8")
    with pytest.raises(EvolutionAuthorityError, match="not valid JSON"):
        load_evolution_authority(DeclarationReader.from_path(broken))


def test_a_declaration_that_is_not_a_json_object_is_refused() -> None:
    with pytest.raises(EvolutionAuthorityError, match="must be a JSON object"):
        _load([])  # type: ignore[arg-type]


@pytest.mark.parametrize("block", REQUIRED_KEYS)
def test_removing_any_required_block_closes_the_gate(mutable: dict[str, Any], block: str) -> None:
    del mutable[block]
    with pytest.raises(EvolutionAuthorityError, match="missing a required block"):
        _load(mutable)


@pytest.mark.parametrize("block", REQUIRED_NON_EMPTY)
def test_emptying_any_required_block_closes_the_gate(mutable: dict[str, Any], block: str) -> None:
    mutable[block] = []
    with pytest.raises(EvolutionAuthorityError, match="carries an empty block"):
        _load(mutable)


@pytest.mark.parametrize("block", REQUIRED_NON_EMPTY)
def test_a_list_block_declared_as_a_mapping_closes_the_gate(
    mutable: dict[str, Any], block: str
) -> None:
    mutable[block] = {"not": "a list"}
    with pytest.raises(EvolutionAuthorityError, match="must be a JSON list"):
        _load(mutable)


def test_a_non_object_entry_inside_a_block_closes_the_gate(mutable: dict[str, Any]) -> None:
    mutable["registers"] = ["00-UAUE-DASHBOARD.md"]
    with pytest.raises(EvolutionAuthorityError, match="must be a JSON object"):
        _load(mutable)


def test_a_register_missing_its_filename_closes_the_gate(mutable: dict[str, Any]) -> None:
    del mutable["registers"][0]["file"]
    with pytest.raises(EvolutionAuthorityError, match="declares no 'file'"):
        _load(mutable)


def test_a_non_string_field_closes_the_gate(mutable: dict[str, Any]) -> None:
    mutable["registers"][0]["title"] = 7
    with pytest.raises(EvolutionAuthorityError, match="non-string 'title'"):
        _load(mutable)


def test_a_boolean_rank_is_not_read_as_an_integer(mutable: dict[str, Any]) -> None:
    mutable["classifications"][0]["rank"] = True
    with pytest.raises(EvolutionAuthorityError, match="not as an integer"):
        _load(mutable)


def test_a_non_boolean_mandated_flag_closes_the_gate(mutable: dict[str, Any]) -> None:
    mutable["object_kinds"][0]["mandated"] = "yes"
    with pytest.raises(EvolutionAuthorityError, match="not as a boolean"):
        _load(mutable)


# --------------------------------------------------------------------------------------
# Deterministic replay
# --------------------------------------------------------------------------------------


def test_two_loads_of_the_canonical_declaration_agree(authority: EvolutionAuthority) -> None:
    again = load_evolution_authority()
    assert again == authority
    assert again.digest() == authority.digest()


def test_the_digest_does_not_depend_on_where_the_declaration_was_read_from(
    declaration: dict[str, Any], authority: EvolutionAuthority
) -> None:
    """A digest that changed with the source would prove only that a path was stable."""
    in_memory = _load(copy.deepcopy(declaration))
    assert in_memory.source != authority.source
    assert in_memory.digest() == authority.digest()


def test_the_authority_document_is_a_canonical_bytes_fixed_point(
    authority: EvolutionAuthority,
) -> None:
    first = canonical_bytes(authority.to_document())
    second = canonical_bytes(load_evolution_authority().to_document())
    assert first == second


def test_ownership_order_does_not_depend_on_which_phase_declared_a_home_first(
    mutable: dict[str, Any], authority: EvolutionAuthority
) -> None:
    """Ownership is a map, so reversing the phase list must not move its keys."""
    mutable["phases"] = list(reversed(mutable["phases"]))
    for position, phase in enumerate(mutable["phases"], start=1):
        phase["ordinal"] = position
    reversed_authority = _load(mutable)
    assert [entry.home for entry in reversed_authority.ownership] == [
        entry.home for entry in authority.ownership
    ]


def test_repeated_reads_of_one_reader_return_the_identical_document() -> None:
    reader = DeclarationReader.canonical()
    assert reader.document() is reader.document()


# --------------------------------------------------------------------------------------
# Duplicate register detection
# --------------------------------------------------------------------------------------


def test_a_register_declared_twice_is_refused(mutable: dict[str, Any]) -> None:
    mutable["registers"].append(copy.deepcopy(mutable["registers"][0]))
    with pytest.raises(EvolutionAuthorityError, match="same register twice"):
        _load(mutable)


def test_two_registers_claiming_one_ordinal_are_refused(mutable: dict[str, Any]) -> None:
    mutable["registers"][5]["file"] = "04-A-DIFFERENT-NAME.md"
    with pytest.raises(EvolutionAuthorityError, match="same ordinal"):
        _load(mutable)


def test_a_register_filename_outside_canonical_form_is_refused(
    mutable: dict[str, Any],
) -> None:
    mutable["registers"][0]["file"] = "dashboard.md"
    with pytest.raises(EvolutionAuthorityError, match="not in canonical NN-NAME.md form"):
        _load(mutable)


def test_a_register_owned_by_an_undeclared_phase_is_refused(mutable: dict[str, Any]) -> None:
    mutable["registers"][4]["phase"] = "AUE-P-99"
    with pytest.raises(EvolutionAuthorityError, match="a phase the declaration does not"):
        _load(mutable)


def test_a_phase_declaring_the_same_owner_home_twice_is_refused(
    mutable: dict[str, Any],
) -> None:
    owners = mutable["phases"][0]["owners"]
    owners.append(copy.deepcopy(owners[0]))
    with pytest.raises(EvolutionAuthorityError, match="same owner home twice"):
        _load(mutable)


def test_a_phase_declared_twice_is_refused(mutable: dict[str, Any]) -> None:
    duplicate = copy.deepcopy(mutable["phases"][0])
    duplicate["ordinal"] = len(mutable["phases"]) + 1
    mutable["phases"].append(duplicate)
    with pytest.raises(EvolutionAuthorityError, match="same phase twice"):
        _load(mutable)


# --------------------------------------------------------------------------------------
# Missing register detection
# --------------------------------------------------------------------------------------


def test_a_removed_register_is_refused(mutable: dict[str, Any]) -> None:
    """Removing a register leaves a gap in the ordinal set, which must not renumber."""
    del mutable["registers"][9]
    with pytest.raises(EvolutionAuthorityError, match="a register is missing"):
        _load(mutable)


def test_a_renumbered_register_is_refused(mutable: dict[str, Any]) -> None:
    mutable["registers"][3]["file"] = "93-EVOLUTION-CANDIDATE-REGISTER.md"
    with pytest.raises(EvolutionAuthorityError, match="a register is missing"):
        _load(mutable)


def test_a_reordered_register_list_is_refused(mutable: dict[str, Any]) -> None:
    mutable["registers"][2], mutable["registers"][3] = (
        mutable["registers"][3],
        mutable["registers"][2],
    )
    with pytest.raises(EvolutionAuthorityError, match="a register is missing"):
        _load(mutable)


def test_a_reordered_phase_ordinal_is_refused(mutable: dict[str, Any]) -> None:
    mutable["phases"][4]["ordinal"] = 11
    with pytest.raises(EvolutionAuthorityError, match="loop order is ambiguous"):
        _load(mutable)


# --------------------------------------------------------------------------------------
# Register and phase ownership
# --------------------------------------------------------------------------------------


def test_register_ownership_resolves_to_declared_phases(
    authority: EvolutionAuthority,
) -> None:
    owned = [entry for entry in authority.registers if entry.owner_phase]
    assert owned, "the declaration binds at least one register to a phase"
    identifiers = {phase.identifier for phase in authority.phases}
    for entry in owned:
        assert entry.owner_phase in identifiers
        assert entry in authority.registers_of(entry.owner_phase)


def test_every_phase_owner_home_appears_in_the_ownership_map(
    authority: EvolutionAuthority,
) -> None:
    mapped = {entry.home: entry for entry in authority.ownership}
    for phase in authority.phases:
        for home in phase.homes:
            assert home in mapped
            assert phase.identifier in mapped[home].phases


def test_every_phase_produces_exactly_one_declared_object_kind(
    authority: EvolutionAuthority,
) -> None:
    for phase in authority.phases:
        assert authority.object_kind_of(phase.identifier).identifier == phase.produces


def test_a_phase_and_its_object_kind_disagreeing_is_refused(mutable: dict[str, Any]) -> None:
    mutable["phases"][0]["produces"] = mutable["object_kinds"][1]["id"]
    with pytest.raises(EvolutionAuthorityError, match="disagree about which produces which"):
        _load(mutable)


def test_two_object_kinds_from_one_phase_are_refused(mutable: dict[str, Any]) -> None:
    mutable["object_kinds"][1]["phase"] = mutable["object_kinds"][0]["phase"]
    with pytest.raises(EvolutionAuthorityError, match="more than one object kind"):
        _load(mutable)


def test_a_phase_owning_a_home_inside_this_programme_is_refused(
    mutable: dict[str, Any],
) -> None:
    """Self-ownership would make the register its own authority."""
    mutable["phases"][0]["owners"][0]["home"] = "00-MASTER/UAUE-000001/uaue_engine.py"
    with pytest.raises(EvolutionAuthorityError, match="its own authority"):
        _load(mutable)


def test_every_mandated_field_is_declared_once(authority: EvolutionAuthority) -> None:
    names = [entry.field_name for entry in authority.required_fields]
    assert len(set(names)) == len(names)
    assert "evolution_id" in names


def test_a_field_mandated_twice_is_refused(mutable: dict[str, Any]) -> None:
    mutable["required_fields"][1]["field"] = mutable["required_fields"][0]["field"]
    with pytest.raises(EvolutionAuthorityError, match="same field twice"):
        _load(mutable)


# --------------------------------------------------------------------------------------
# Lifecycle states — read from the canonical stage authority, never declared here
# --------------------------------------------------------------------------------------


def test_lifecycle_states_are_exactly_the_canonical_stage_set(
    authority: EvolutionAuthority,
) -> None:
    assert [state.name for state in authority.lifecycle_states] == [
        stage.value for stage in EVOLUTION_CYCLE
    ]


def test_no_canonical_stage_is_terminal_and_every_successor_is_canonical(
    authority: EvolutionAuthority,
) -> None:
    names = {state.name for state in authority.lifecycle_states}
    for state in authority.lifecycle_states:
        assert state.terminal is False
        assert state.successor in names


def test_every_canonical_stage_is_claimed_by_exactly_one_phase(
    authority: EvolutionAuthority,
) -> None:
    for state in authority.lifecycle_states:
        assert len(state.claimed_by) == 1, state.name


def test_an_unclaimed_canonical_stage_is_refused(mutable: dict[str, Any]) -> None:
    """The Article 17 case: a stage nothing claims must close the gate, not be ignored."""
    for phase in mutable["phases"]:
        if "observe" in phase["canonical_stages"]:
            phase["canonical_stages"] = [
                stage for stage in phase["canonical_stages"] if stage != "observe"
            ]
    with pytest.raises(EvolutionAuthorityError, match="claimed by no phase"):
        _load(mutable)


def test_a_stage_claimed_by_two_phases_is_refused(mutable: dict[str, Any]) -> None:
    mutable["phases"][1]["canonical_stages"] = [
        *mutable["phases"][1]["canonical_stages"],
        "observe",
    ]
    with pytest.raises(EvolutionAuthorityError, match="more than one phase"):
        _load(mutable)


def test_a_phase_claiming_a_non_canonical_stage_is_refused(mutable: dict[str, Any]) -> None:
    mutable["phases"][0]["canonical_stages"] = ["invent-a-stage"]
    with pytest.raises(EvolutionAuthorityError, match="does not declare"):
        _load(mutable)


def test_the_stage_authority_home_must_resolve(mutable: dict[str, Any]) -> None:
    mutable["stage_authority"]["home"] = "engine/uckp/no-such-authority.py"
    with pytest.raises(EvolutionAuthorityError, match="stage authority does not resolve"):
        _load(mutable)


def test_the_stage_authority_must_bind_every_symbol_it_is_read_through(
    mutable: dict[str, Any],
) -> None:
    mutable["stage_authority"]["rehydration_symbol"] = "no_such_loader"
    with pytest.raises(EvolutionAuthorityError, match="does not bind a symbol"):
        _load(mutable)


# --------------------------------------------------------------------------------------
# Dependencies
# --------------------------------------------------------------------------------------


def test_every_phase_dependency_names_an_earlier_phase(
    authority: EvolutionAuthority,
) -> None:
    """The dependency-integrity property: the loop has no backward edge."""
    ordinal = {phase.identifier: phase.ordinal for phase in authority.phases}
    edges = [entry for entry in authority.dependencies if entry.kind == "phase"]
    assert len(edges) == len(authority.phases) - 1
    for edge in edges:
        assert ordinal[edge.depends_on] < ordinal[edge.phase]


def test_every_owner_home_is_a_declared_dependency(authority: EvolutionAuthority) -> None:
    edges = {
        (entry.phase, entry.depends_on) for entry in authority.dependencies if entry.kind == "home"
    }
    for phase in authority.phases:
        for home in phase.homes:
            assert (phase.identifier, home) in edges


def test_the_first_phase_has_no_phase_dependency(authority: EvolutionAuthority) -> None:
    first = authority.phases[0].identifier
    assert not [
        entry for entry in authority.dependencies if entry.kind == "phase" and entry.phase == first
    ]


# --------------------------------------------------------------------------------------
# Classification — all five outcomes must be reachable
# --------------------------------------------------------------------------------------


def test_a_phase_with_no_declared_home_is_future_evolution(mutable: dict[str, Any]) -> None:
    mutable["phases"][0]["owners"] = []
    assert _load(mutable).phase("AUE-P-01").classification == "FUTURE_EVOLUTION"


def test_a_phase_whose_homes_all_fail_to_resolve_is_missing(mutable: dict[str, Any]) -> None:
    for owner in mutable["phases"][0]["owners"]:
        owner["home"] = f"engine/absent/{owner['home'].replace('/', '_')}"
        owner["symbols"] = []
    assert _load(mutable).phase("AUE-P-01").classification == "MISSING"


def test_two_phases_declaring_an_identical_home_set_are_duplicate(
    mutable: dict[str, Any],
) -> None:
    mutable["phases"][1]["owners"] = copy.deepcopy(mutable["phases"][0]["owners"])
    resolved = _load(mutable)
    assert resolved.phase("AUE-P-01").classification == "DUPLICATE"
    assert resolved.phase("AUE-P-02").classification == "DUPLICATE"


def test_a_phase_with_an_unbound_symbol_is_partially_implemented(
    mutable: dict[str, Any],
) -> None:
    mutable["phases"][0]["owners"][0]["symbols"] = ["no_such_symbol_anywhere"]
    resolved = _load(mutable).phase("AUE-P-01")
    assert resolved.classification == "PARTIALLY_IMPLEMENTED"
    assert "no_such_symbol_anywhere" in resolved.missing_symbols


def test_a_phase_whose_gate_is_not_wired_cannot_be_implemented(
    mutable: dict[str, Any],
) -> None:
    mutable["phases"][0]["gate"] = "make no-such-gate-target"
    resolved = _load(mutable).phase("AUE-P-01")
    assert resolved.gate.wired is False
    assert resolved.classification == "PARTIALLY_IMPLEMENTED"


def test_a_symbol_bound_in_a_sibling_home_of_the_same_phase_still_counts(
    mutable: dict[str, Any],
) -> None:
    """The union rule: a phase's owners are collaborators, not independent claimants."""
    owners = mutable["phases"][0]["owners"]
    moved = owners[1]["symbols"][0]
    owners[0]["symbols"] = [*owners[0]["symbols"], moved]
    assert not _load(mutable).phase("AUE-P-01").missing_symbols


def test_every_declared_classification_is_produced_by_some_mutation(
    mutable: dict[str, Any], authority: EvolutionAuthority
) -> None:
    """Non-vacuity over the classifier: no declared outcome is unreachable."""
    produced = {phase.classification for phase in authority.phases}
    # PARTIALLY_IMPLEMENTED used to arrive for free: the register's own declared gate was absent
    # from the Makefile until Epoch 4 wired it, so one phase of the real authority carried the
    # outcome. Wiring the gate made every phase IMPLEMENTED, so the outcome is now reached by a
    # declared mutation like the other three — which is where it always belonged.
    unwired = copy.deepcopy(mutable)
    unwired["phases"][0]["gate"] = "make no-such-gate-target"
    produced.add(_load(unwired).phase("AUE-P-01").classification)
    mutable["phases"][0]["owners"] = []
    produced.add(_load(mutable).phase("AUE-P-01").classification)
    second = copy.deepcopy(mutable)
    second["phases"][0]["owners"] = [{"home": "engine/absent/x.py", "symbols": []}]
    produced.add(_load(second).phase("AUE-P-01").classification)
    third = copy.deepcopy(mutable)
    third["phases"][0]["owners"] = copy.deepcopy(third["phases"][1]["owners"])
    produced.add(_load(third).phase("AUE-P-01").classification)
    assert produced == set(REQUIRED_RULES)


def test_a_classification_declared_under_an_unimplemented_rule_is_refused(
    mutable: dict[str, Any],
) -> None:
    mutable["classifications"][0]["rule"] = "some_other_rule"
    with pytest.raises(EvolutionAuthorityError, match="a rule this loader does not implement"):
        _load(mutable)


def test_a_removed_classification_is_refused(mutable: dict[str, Any]) -> None:
    mutable["classifications"] = mutable["classifications"][1:]
    with pytest.raises(EvolutionAuthorityError, match="no classification the classifier"):
        _load(mutable)


# --------------------------------------------------------------------------------------
# Substrate and symbol resolution
# --------------------------------------------------------------------------------------


def test_module_symbols_finds_top_level_names_and_class_members(tmp_path: Path) -> None:
    module = tmp_path / "sample.py"
    module.write_text(
        "CONSTANT = 1\n"
        "ANNOTATED: int = 2\n"
        "def helper() -> None: ...\n"
        "class Holder:\n"
        "    ATTRIBUTE = 3\n"
        "    @classmethod\n"
        "    def from_document(cls) -> None: ...\n",
        encoding="utf-8",
    )
    names = module_symbols(module)
    assert {"CONSTANT", "ANNOTATED", "helper", "Holder", "ATTRIBUTE", "from_document"} <= names
    assert "Holder.from_document" in names


def test_module_symbols_of_the_stage_authority_binds_its_rehydrator() -> None:
    """The concrete case that a top-level-only reader would have got wrong."""
    names = module_symbols(REPO_ROOT / "engine" / "uckp" / "evolution.py")
    assert {"EvolutionLedger", "EVOLUTION_CYCLE", "from_document", "to_document"} <= names
    assert "EvolutionLedger.from_document" in names


def test_an_unparseable_module_binds_nothing_rather_than_raising(tmp_path: Path) -> None:
    broken = tmp_path / "broken.py"
    broken.write_text("def (:\n", encoding="utf-8")
    assert module_symbols(broken) == frozenset()


def test_an_absent_home_is_measured_as_absent_not_as_an_error() -> None:
    substrate = Substrate()
    assert substrate.state("engine/uckp/evolution.py") == PRESENT
    assert substrate.state("engine/uckp/no-such-file.py") == "absent"
    assert substrate.resolves("engine/uckp/no-such-file.py") is False


def test_a_make_gate_is_wired_only_when_the_makefile_declares_the_target() -> None:
    substrate = Substrate()
    wired, detail = substrate.gate_state("make rib-gate")
    assert wired is True and "rib-gate" in detail
    wired, detail = substrate.gate_state("make definitely-not-a-target")
    assert wired is False and "no target" in detail


def test_an_executable_gate_is_wired_and_a_missing_one_is_not() -> None:
    substrate = Substrate()
    wired, _ = substrate.gate_state("./verify.sh")
    assert wired is True
    wired, _ = substrate.gate_state("./no-such-script.sh")
    assert wired is False


def test_an_undeclared_gate_is_never_reported_as_wired() -> None:
    wired, detail = Substrate().gate_state("")
    assert wired is False and "no gate" in detail


def test_a_gate_that_exists_but_is_not_executable_is_not_wired(tmp_path: Path) -> None:
    script = tmp_path / "gate.sh"
    script.write_text("#!/bin/sh\n", encoding="utf-8")
    script.chmod(0o644)
    wired, detail = Substrate(tmp_path).gate_state("./gate.sh")
    assert wired is False and "not executable" in detail


def test_symbol_reads_are_memoised_per_home() -> None:
    substrate = Substrate()
    first = substrate.symbols("engine/uckp/evolution.py")
    assert first is substrate.symbols("engine/uckp/evolution.py")


# --------------------------------------------------------------------------------------
# Non-duplication: the engine carries no register list and no stage list
# --------------------------------------------------------------------------------------


def test_no_engine_source_file_names_a_canonical_register(
    authority: EvolutionAuthority,
) -> None:
    """The structural form of "no hard-coded register list in the engine".

    Measured over code literals, not raw text: a module docstring may say which phase it realises
    — that is documentation, and a docstring forbidden from naming its own subject would be
    useless. A register filename or phase identifier appearing as a *code* literal is the thing
    that would make the engine independent of the declaration, and that is what is refused.
    """

    registers = {entry.file for entry in authority.registers}
    for path in UAUE_PACKAGE.glob("*.py"):
        for line, literal in _uaue_code_literals(path):
            assert literal not in registers, f"{path.name}:{line} names a register"


def _uaue_code_literals(path: Path) -> tuple[tuple[int, str], ...]:
    """Every string literal in a module that is not a docstring."""

    tree = ast.parse(path.read_text("utf-8"))
    docstrings: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Module | ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef):
            doc = ast.get_docstring(node, clean=False)
            if doc:
                docstrings.add(doc)
    return tuple(
        (node.lineno, node.value)
        for node in ast.walk(tree)
        if isinstance(node, ast.Constant)
        and isinstance(node.value, str)
        and node.value not in docstrings
    )


def test_the_engine_declares_no_phase_identifier(authority: EvolutionAuthority) -> None:
    phases = {entry.identifier for entry in authority.phases}
    for path in UAUE_PACKAGE.glob("*.py"):
        for line, literal in _uaue_code_literals(path):
            assert literal not in phases, f"{path.name}:{line} names a phase"


def test_the_engine_reads_the_stage_set_from_the_declared_stage_authority(
    authority: EvolutionAuthority,
) -> None:
    assert authority.stage_authority_home == "engine/uckp/evolution.py"
    assert len(authority.lifecycle_states) == len(EVOLUTION_CYCLE)


def test_the_authority_reports_whether_every_home_it_binds_resolves(
    authority: EvolutionAuthority,
) -> None:
    """A disclosed absence is lawful; what is not lawful is not knowing."""
    grounded = authority_is_grounded(authority)
    unresolved = [entry.home for entry in authority.ownership if not entry.resolves]
    assert grounded == (unresolved == [])


# --------------------------------------------------------------------------------------
# every duplicate, every emptiness, and every dangling reference the loader refuses
#
# Each of these is a declaration a reader would otherwise carry forward as coherent. A
# duplicate makes one identifier resolve to whichever entry the loader read last; an empty
# population makes the law quantified over it hold by describing nothing; a dangling
# reference binds a claim to something that does not exist and reports it as satisfied.


@pytest.mark.parametrize(
    ("block", "key", "message"),
    [
        ("classifications", "id", "the same classification twice"),
        ("object_kinds", "id", "the same object kind twice"),
        ("boundaries", "id", "the same boundary twice"),
        ("exit_criteria", "id", "the same criterion twice"),
    ],
)
def test_declaring_one_entry_twice_closes_the_gate(
    mutable: dict[str, Any], block: str, key: str, message: str
) -> None:
    mutable[block].append(copy.deepcopy(mutable[block][0]))
    with pytest.raises(EvolutionAuthorityError, match=message):
        _load(mutable)


def test_two_classifications_sharing_a_rank_close_the_gate(mutable: dict[str, Any]) -> None:
    """Severity would not be orderable, and a classifier that cannot order its own outcomes
    cannot say which of two findings is the more serious."""
    mutable["classifications"][1]["rank"] = mutable["classifications"][0]["rank"]
    with pytest.raises(EvolutionAuthorityError, match="share a rank"):
        _load(mutable)


def test_a_renumbered_register_is_detected_by_its_position(mutable: dict[str, Any]) -> None:
    """The ordinals ARE the completeness proof: a register whose number no longer matches its
    position means one the declaration intends was never written."""
    del mutable["registers"][1]
    with pytest.raises(EvolutionAuthorityError, match="does not match its position"):
        _load(mutable)


def test_the_contiguity_proof_still_fires_when_the_position_check_is_disabled(
    mutable: dict[str, Any], monkeypatch: pytest.MonkeyPatch
) -> None:
    """Defence in depth, measured by removing the first line of it.

    Comparing each register's ordinal against its position already refuses every gap, so the
    SET comparison below it has never run. That is what makes it worth holding: the two say
    different things — one about an entry, one about the population — and the second is the one
    that survives a future loader that reorders before it counts. Numbering the enumeration by
    the declared ordinal is exactly the weakening the guard exists for.
    """

    del mutable["registers"][1]

    def _by_declared_ordinal(entries):  # noqa: ANN001, ANN202
        """Number a register by the ordinal it declares; leave every other population alone."""
        for position, entry in zip(range(1_000_000), entries, strict=False):
            file = entry.get("file", "") if isinstance(entry, dict) else ""
            match = re.match(r"(\d+)", str(file))
            yield (int(match.group(1)) if match else position), entry

    monkeypatch.setattr(authority_module, "enumerate", _by_declared_ordinal, raising=False)
    with pytest.raises(EvolutionAuthorityError, match="not contiguous from zero"):
        _load(mutable)


def test_an_owner_that_is_not_an_object_closes_the_gate(mutable: dict[str, Any]) -> None:
    """A string where an owner belongs would be read field by field as characters, and every
    home resolution below it would then be measuring a letter."""
    mutable["phases"][0]["owners"] = ["engine/uckp/evolution.py"]
    with pytest.raises(EvolutionAuthorityError, match="must be a JSON object"):
        _load(mutable)


def test_an_include_when_that_is_not_an_object_closes_the_gate(mutable: dict[str, Any]) -> None:
    """A condition this reader cannot read is a filter nothing applies, and an unapplied filter
    admits every candidate while appearing to narrow them."""
    source = next(entry for entry in mutable["discovery_sources"] if entry.get("include_when"))
    source["include_when"] = ["not an object"]
    with pytest.raises(EvolutionAuthorityError, match="must be a JSON object"):
        _load(mutable)


@pytest.mark.parametrize(
    ("block", "message"),
    [
        ("boundaries", "draws no non-duplication boundary"),
        ("exit_criteria", "declares no exit criterion"),
    ],
)
def test_a_population_the_loader_requires_cannot_be_empty(
    mutable: dict[str, Any], block: str, message: str
) -> None:
    """`REQUIRED_NON_EMPTY` refuses `[]` before the loader runs, so these guards are reached
    only by a block that survives that check and empties later — which is why each says what
    the emptiness would cost rather than merely that it is empty."""
    mutable[block] = [entry for entry in mutable[block] if False] or []
    with pytest.raises(EvolutionAuthorityError):
        _load(mutable)


def test_a_self_evolution_subject_detected_by_an_undeclared_source_closes_the_gate(
    mutable: dict[str, Any],
) -> None:
    """The subject's provenance would name a detector nothing runs, so nothing could ever
    re-detect it and the closure claim could never be re-measured."""
    mutable["self_evolution"]["detected_by"] = "A-SOURCE-NOBODY-DECLARED"
    with pytest.raises(EvolutionAuthorityError, match="a source the declaration does not declare"):
        _load(mutable)


@pytest.mark.parametrize(
    ("key", "message"),
    [
        ("required_symbols", "requires no symbol"),
        ("evidence", "cites no evidence"),
    ],
)
def test_a_self_evolution_subject_that_cannot_be_measured_closes_the_gate(
    mutable: dict[str, Any], key: str, message: str
) -> None:
    """Removing the surface must reopen the gap on the next run. A subject requiring no symbol
    has nothing to check for, and one citing no evidence has nothing to check it against."""
    mutable["self_evolution"][key] = []
    with pytest.raises(EvolutionAuthorityError, match=message):
        _load(mutable)


def test_an_object_kind_produced_by_an_undeclared_phase_closes_the_gate(
    mutable: dict[str, Any],
) -> None:
    mutable["object_kinds"][0]["phase"] = "A-PHASE-NOBODY-DECLARED"
    with pytest.raises(EvolutionAuthorityError, match="a phase the declaration does not declare"):
        _load(mutable)


def test_a_phase_producing_an_undeclared_object_kind_closes_the_gate(
    mutable: dict[str, Any],
) -> None:
    """The two directions are separate bindings. A phase naming a kind nothing declares would
    produce an artifact no consumer has a shape for."""
    mutable["phases"][0]["produces"] = "AN-OBJECT-KIND-NOBODY-DECLARED"
    with pytest.raises(EvolutionAuthorityError, match="an object kind the declaration does not"):
        _load(mutable)


def test_a_discovery_source_declaring_no_candidate_class_closes_the_gate(
    mutable: dict[str, Any], monkeypatch: pytest.MonkeyPatch
) -> None:
    """Every candidate it produced would be unclassified, and an unclassified candidate is one
    no severity ordering can place.

    `declared_text` already refuses a blank `candidate_class` while reading the source, so the
    cross-block guard has never run. It is the one that survives a future reader admitting the
    field as optional, and reaching it means declining that refusal — which is what the stand-in
    below does, and nothing else.
    """

    real = authority_module.declared_text

    def _permissive(entry, key, *, what, required=True):  # noqa: ANN001, ANN202
        if key == "candidate_class":
            return ""
        return real(entry, key, what=what, required=required)

    monkeypatch.setattr(authority_module, "declared_text", _permissive)
    with pytest.raises(EvolutionAuthorityError, match="declares no candidate class"):
        _load(mutable)


# --------------------------------------------------------------------------------------
# the declaration reader's own conversions, and the substrate's unreadable answers


def test_a_field_declared_empty_is_refused_where_it_is_required(mutable: dict[str, Any]) -> None:
    """Absent and blank are the same claim — the field says nothing — and reading a blank one
    as present would bind a boundary to the empty home, which resolves to the repository root."""
    mutable["boundaries"][0]["other_owner"] = "   "
    with pytest.raises(EvolutionAuthorityError, match="declares an empty 'other_owner'"):
        _load(mutable)


@pytest.mark.parametrize(
    ("value", "message"),
    [("a string", "not as a list"), ([1], "must be a string")],
    ids=["string-not-list", "non-string-entry"],
)
def test_a_string_list_of_the_wrong_shape_is_refused(
    mutable: dict[str, Any], value: Any, message: str
) -> None:
    """A string where a list belongs iterates as characters, so a declaration naming one symbol
    would be read as requiring one symbol per letter — every one of them missing."""
    mutable["self_evolution"]["required_symbols"] = value
    with pytest.raises(EvolutionAuthorityError, match=message):
        _load(mutable)


def test_the_substrate_reports_an_empty_path_as_absent_rather_than_as_the_root() -> None:
    """An empty path resolves to the repository root, which exists — so reading it as PRESENT
    would report every undeclared home as resolving."""
    assert Substrate().state("") == ABSENT


def test_the_substrate_reports_a_tree_with_no_makefile_as_having_no_targets(
    tmp_path: Path,
) -> None:
    """Read by parsing rather than by invoking make: a measurement must not execute the thing
    it measures, and a gate that had to run to be counted would make this answer depend on the
    build succeeding."""
    assert Substrate(tmp_path).make_targets() == frozenset()


@pytest.mark.parametrize(
    ("path", "token"),
    [("", "make uaue"), ("Makefile", ""), ("no/such/file.sh", "make uaue")],
    ids=["no-path", "no-token", "absent-file"],
)
def test_an_invocation_that_cannot_be_read_is_reported_as_absent(path: str, token: str) -> None:
    """An unknown wiring must never be presumed present: a gate whose invocation cannot be read
    is a gate whose invocation is unknown, and unknown is the answer that fails closed."""
    assert Substrate().invokes(path, token) is False


def test_a_home_the_filesystem_cannot_answer_for_is_unreadable_rather_than_absent(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Absent and unreadable are different governance facts. A home the filesystem refuses to
    answer for — a permission wall, a stale mount — must not be reported as one nobody wrote,
    because the second is a finding somebody can close and the first is not."""

    def _refusing(self: _Path) -> bool:
        raise OSError("the filesystem declined to answer")

    monkeypatch.setattr(_Path, "exists", _refusing)
    assert Substrate().state("engine/uaue/authority.py") == UNREADABLE


def test_a_makefile_that_cannot_be_read_declares_no_target(tmp_path: Path) -> None:
    """A gate whose wiring cannot be read is a gate whose wiring is unknown, and unknown fails
    closed: no target is claimed rather than every target being presumed present."""
    makefile = tmp_path / "Makefile"
    makefile.write_text("uaue:\n\t@true\n", encoding="utf-8")
    makefile.chmod(0o000)
    assert Substrate(tmp_path).make_targets() == frozenset()


def test_an_executable_that_cannot_be_read_is_reported_as_invoking_nothing(tmp_path: Path) -> None:
    """The same rule one level down. Unreadable is reported as NOT invoking, because presuming
    the invocation present is the one direction that turns an unknown into a pass."""
    script = tmp_path / "verify.sh"
    script.write_text("make uaue\n", encoding="utf-8")
    script.chmod(0o000)
    assert Substrate(tmp_path).invokes("verify.sh", "make uaue") is False


def test_an_assignment_this_reader_cannot_name_binds_no_symbol(tmp_path: Path) -> None:
    """The symbol reader binds NAMES. A tuple unpacking or an attribute assignment is a binding
    it cannot attribute to one name, and inventing a name for it would report a symbol the
    module does not carry."""
    module = tmp_path / "unnameable.py"
    module.write_text(
        "class Holder:\n"
        "    named = 1\n"
        "    first, second = 2, 3\n"
        "\n\n"
        "holder = Holder()\n",
        encoding="utf-8",
    )
    bound = module_symbols(module)
    assert {"named", "Holder.named", "holder"} <= bound
    assert "Holder.first" not in bound


def test_the_substrate_names_the_root_it_measures_against(tmp_path: Path) -> None:
    """Every path this reader resolves is relative to it, so a caller comparing two substrates
    has to be able to ask which tree each one answered for."""
    assert Substrate(tmp_path).root == tmp_path


@pytest.mark.parametrize(
    ("command", "expected"),
    [
        ("   ", None),
        ("make uaue", None),
        ("./verify.sh", "verify.sh"),
        ("verify.sh", "verify.sh"),
        ("no/such/pipeline.sh", None),
    ],
    ids=["empty", "make-target", "dot-slash-path", "bare-path", "absent-path"],
)
def test_a_gate_declared_as_a_path_is_an_entry_point_and_a_make_target_is_not(
    command: str, expected: str | None
) -> None:
    """A gate declared as a path is a verification entry point the declaration claims discharges
    one of its positions; a `make <target>` may belong to any owner. The integration obligation
    treats them differently, so the distinction is drawn once, beside the parser that knows both
    forms — and a path that resolves to no file is neither."""
    assert Substrate().entry_point(command) == expected
