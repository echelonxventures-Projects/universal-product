"""UISD-000001 — the Universal Infinite Scope and Direction contract, measured.

Organised around the one question that matters for a gate: **can each law fail?** A law
that cannot be made to fail is decoration, and a decorative law would be worse than
none because they would licence the belief that the property had been checked. So for
every law there is at least one test that constructs the violating condition and asserts
the specific refusal.

The other load-bearing tests are:

* :func:`test_the_live_declaration_is_sound_and_open` — the committed declaration measures
  every declared law and refuses none. If this fails, the repository has a real finding.
* :func:`test_measuring_writes_nothing` — the gate is OBSERVE MODE. Proven by hashing the
  whole scanned surface before and after, not by reading the docstring that claims it.
* :func:`test_a_check_no_law_claims_is_refused` — dead code wearing the appearance of
  enforcement is refused in the same breath as a law with no check.
"""

from __future__ import annotations

import copy
import hashlib
import json
import os
import sys
import types
from typing import Any

import pytest

from engine.infinite_scope import contract as contract_module
from engine.infinite_scope import gate as gate_module
from engine.infinite_scope.contract import (
    DECLARATION_PATH,
    LAW_CHECKS,
    assess,
    candidate_files,
    check_scope_expansion_capacity,
    load_contract,
    load_declaration,
    repo_root,
    scan_occurrences,
)
from engine.infinite_scope.model import (
    ExerciseConsumer,
    FreezeScan,
    InfiniteScopeContract,
    InfiniteScopeError,
    Law,
    PreservedSite,
)

REPO = repo_root()


# --------------------------------------------------------------------------- fixtures


@pytest.fixture(scope="module")
def declaration() -> dict[str, Any]:
    """The committed declaration, loaded once."""
    return load_declaration()


@pytest.fixture()
def doc(declaration: dict[str, Any]) -> dict[str, Any]:
    """A deep copy of the declaration, safe to mutate."""
    return copy.deepcopy(declaration)


def build(doc: dict[str, Any]) -> InfiniteScopeContract:
    """Rehydrate a contract from a mutated declaration without validating it."""
    return InfiniteScopeContract.from_declaration(doc)


def run(check_name: str, doc: dict[str, Any], repo: str = REPO) -> tuple[str, ...]:
    """Run one named check against a mutated declaration."""
    return LAW_CHECKS[check_name](build(doc), repo)


def write_declaration(tmp_path: Any, doc: dict[str, Any]) -> str:
    """Write a declaration to a temporary path and return it."""
    target = os.path.join(str(tmp_path), "uisd-declaration.json")
    with open(target, "w", encoding="utf-8") as handle:
        json.dump(doc, handle)
    return target


# ------------------------------------------------------------- the live declaration


def test_the_live_declaration_is_sound_and_open() -> None:
    """The committed declaration constructs, measures every declared law, and refuses none.

    The expectation is DERIVED from the declaration, never written here. A literal count
    would make admitting a law an engine-plane change, which is the hardcoded expectation
    UCKP-ART-15 exists to prevent and ISD-L-01 exists to measure. What the count was ever
    worth is already measured by InfiniteScopeContract.validate, which refuses a law with
    no check AND a check no law claims; the literal only added staleness on top of it.
    """
    contract = load_contract()
    report = gate_module.measure()
    assert report["verdict"] == "OPEN", report["laws"]
    assert report["laws_measured"] == len(contract.laws)
    assert report["laws_refused"] == 0
    assert report["self_applied"] is True
    assert report["capability_model_final"] is False


def test_every_law_is_measured_by_a_declared_axis(declaration: dict[str, Any]) -> None:
    """Each declared expansion axis names a law that exists, and no law is unreferenced."""
    contract = load_contract()
    law_ids = {law.law_id for law in contract.laws}
    measured = {axis.measured_by for axis in contract.axes}
    assert measured <= law_ids
    assert law_ids == measured, "a law no axis references is a law nobody asked for"


def test_the_declaration_holds_no_law_text_in_code() -> None:
    """Laws live in the declaration, not in the engine."""
    source = ""
    for name in ("model.py", "contract.py", "gate.py", "__init__.py"):
        with open(os.path.join(REPO, "engine", "infinite_scope", name), encoding="utf-8") as fh:
            source += fh.read()
    contract = load_contract()
    for law in contract.laws:
        assert law.statement not in source, f"{law.law_id} statement is duplicated into code"


def test_the_gate_declares_it_writes_nothing(declaration: dict[str, Any]) -> None:
    """The declaration's own gate block claims the observation plane and an empty write set."""
    assert declaration["gate"]["writes"] == []
    assert declaration["gate"]["fail_closed"] is True
    assert "OBSERVE" in declaration["gate"]["plane"]


def test_measuring_writes_nothing() -> None:
    """OBSERVE MODE, proven by hashing the scanned surface before and after."""
    contract = load_contract()

    def fingerprint() -> str:
        digest = hashlib.sha256()
        for relpath in candidate_files(REPO, contract.freeze_scan):
            digest.update(relpath.encode("utf-8"))
            try:
                with open(os.path.join(REPO, relpath), "rb") as handle:
                    digest.update(handle.read())
            except OSError:  # pragma: no cover - a file vanishing mid-test
                continue
        return digest.hexdigest()

    before = fingerprint()
    gate_module.measure()
    gate_module.measure()
    assert fingerprint() == before


# ---------------------------------------------------------------- contract soundness


def test_a_law_naming_a_missing_check_is_refused(doc: dict[str, Any]) -> None:
    """A law whose compliance nobody computes is manual governance."""
    doc["laws"][0]["check"] = "check_that_does_not_exist"
    problems = build(doc).validate(frozenset(LAW_CHECKS))
    assert any("is not implemented" in problem for problem in problems)


def test_a_check_no_law_claims_is_refused(doc: dict[str, Any]) -> None:
    """An implemented check that no law claims is dead code that looks like enforcement."""
    doc["laws"] = [law for law in doc["laws"] if law["check"] != "capability_seed_openness"]
    problems = build(doc).validate(frozenset(LAW_CHECKS))
    assert any("no law claims it" in problem for problem in problems)


def test_a_declaration_with_no_laws_is_refused(doc: dict[str, Any]) -> None:
    """A gate over zero laws measures nothing."""
    doc["laws"] = []
    problems = build(doc).validate(frozenset())
    assert any("holds no law" in problem for problem in problems)


def test_a_duplicated_law_id_is_refused(doc: dict[str, Any]) -> None:
    """Two laws sharing an id make one of them unaddressable."""
    doc["laws"].append(copy.deepcopy(doc["laws"][0]))
    problems = build(doc).validate(frozenset(LAW_CHECKS))
    assert any("declared more than once" in problem for problem in problems)


def test_an_axis_naming_no_law_is_refused(doc: dict[str, Any]) -> None:
    """An axis measured by a law that does not exist is unmeasured."""
    doc["expansion_axes"][0]["measured_by"] = "ISD-L-99"
    problems = build(doc).validate(frozenset(LAW_CHECKS))
    assert any("which is not a law" in problem for problem in problems)


def test_a_count_enforced_class_that_is_undeclared_is_refused(doc: dict[str, Any]) -> None:
    """Enforcing counts for a class nobody defined cannot be reasoned about."""
    doc["freeze_scan"]["count_enforced_classes"].append("Z")
    problems = build(doc).validate(frozenset(LAW_CHECKS))
    assert any("is not a declared class" in problem for problem in problems)


def test_load_contract_refuses_an_unsound_declaration(tmp_path: Any, doc: dict[str, Any]) -> None:
    """load_contract reports every reason at once rather than one per run."""
    doc["laws"][0]["check"] = "absent_one"
    doc["laws"][1]["check"] = "absent_two"
    target = write_declaration(tmp_path, doc)
    with pytest.raises(InfiniteScopeError) as caught:
        load_contract(target)
    assert "absent_one" in str(caught.value)
    assert "absent_two" in str(caught.value)


@pytest.mark.parametrize(
    "section", ["laws", "expansion_axes", "closed_enumeration_disclosures", "freeze_scan"]
)
def test_a_missing_section_is_a_fault(doc: dict[str, Any], section: str) -> None:
    """A declaration that has lost a section fails loudly rather than measuring less."""
    doc.pop(section)
    with pytest.raises(InfiniteScopeError):
        build(doc)


def test_a_non_mapping_declaration_is_a_fault() -> None:
    """A list is not a declaration."""
    with pytest.raises(InfiniteScopeError):
        InfiniteScopeContract.from_declaration([])  # type: ignore[arg-type]


def test_an_unreadable_declaration_is_a_fault(tmp_path: Any) -> None:
    """Fail closed: a declaration that cannot be read permits nothing."""
    with pytest.raises(InfiniteScopeError):
        load_declaration(os.path.join(str(tmp_path), "absent.json"))
    broken = os.path.join(str(tmp_path), "broken.json")
    with open(broken, "w", encoding="utf-8") as handle:
        handle.write("{not json")
    with pytest.raises(InfiniteScopeError):
        load_declaration(broken)
    listy = os.path.join(str(tmp_path), "list.json")
    with open(listy, "w", encoding="utf-8") as handle:
        handle.write("[]")
    with pytest.raises(InfiniteScopeError):
        load_declaration(listy)


def test_a_law_missing_a_field_is_a_fault() -> None:
    """Every law field is mandatory."""
    with pytest.raises(InfiniteScopeError):
        Law.of({"id": "ISD-L-01", "title": "t", "statement": "s"})


def test_a_site_without_a_count_is_a_fault() -> None:
    """A preserved site with no occurrence count cannot be ratcheted."""
    with pytest.raises(InfiniteScopeError):
        PreservedSite.of({"id": "R-01", "path": "p", "class": "B", "reason": "r"})
    with pytest.raises(InfiniteScopeError):
        PreservedSite.of(
            {"id": "R-01", "path": "p", "class": "B", "reason": "r", "occurrences": -1}
        )


def test_a_disclosure_with_a_non_integer_population_is_a_fault(doc: dict[str, Any]) -> None:
    """A population is an integer or null; a string is neither."""
    doc["closed_enumeration_disclosures"][0]["population"] = "many"
    with pytest.raises(InfiniteScopeError):
        build(doc)


@pytest.mark.parametrize(
    "mutation",
    [
        {"phrases": [], "status_pattern": ""},
        {"roots": []},
        {"extensions": []},
    ],
)
def test_a_scan_that_would_measure_nothing_is_a_fault(
    doc: dict[str, Any], mutation: dict[str, Any]
) -> None:
    """A scan with no patterns, no roots or no extensions is vacuous by construction."""
    doc["freeze_scan"].update(mutation)
    with pytest.raises(InfiniteScopeError):
        build(doc)


def test_a_scan_without_classes_is_a_fault(doc: dict[str, Any]) -> None:
    """Classification requires declared classes."""
    doc["freeze_scan"].pop("classes")
    with pytest.raises(InfiniteScopeError):
        build(doc)


# ------------------------------------------------------- ISD-L-01 scope expansion


def test_no_disclosure_at_all_is_vacuous_not_satisfied(doc: dict[str, Any]) -> None:
    """An empty disclosure list would pass trivially, so it is refused."""
    doc["closed_enumeration_disclosures"] = []
    problems = run("scope_expansion_capacity", doc)
    assert any("vacuous" in problem for problem in problems)


def test_a_closure_with_no_closing_invariant_is_refused(doc: dict[str, Any]) -> None:
    """Closure without a named closing invariant is silent closure."""
    doc["closed_enumeration_disclosures"][0]["closing_invariant"] = "  "
    assert any("no closing invariant" in p for p in run("scope_expansion_capacity", doc))


def test_a_closure_with_no_admission_path_is_refused(doc: dict[str, Any]) -> None:
    """An enumeration nobody can add to is a finite assumption."""
    doc["closed_enumeration_disclosures"][0]["admission"] = ""
    assert any("no admission path" in p for p in run("scope_expansion_capacity", doc))


def test_a_closure_declared_at_a_missing_path_is_refused(doc: dict[str, Any]) -> None:
    """A disclosure must point at something that exists."""
    doc["closed_enumeration_disclosures"][0]["declared_at"] = "engine/does/not/exist.py"
    assert any("does not exist" in p for p in run("scope_expansion_capacity", doc))


def test_an_unintentional_closure_without_a_gap_is_refused(doc: dict[str, Any]) -> None:
    """Accidental closure must at least be recorded as a gap."""
    entry = doc["closed_enumeration_disclosures"][0]
    entry["intentional"] = False
    entry.pop("gap", None)
    assert any("names no gap" in p for p in run("scope_expansion_capacity", doc))


def test_the_live_disclosures_record_their_one_unintentional_closure() -> None:
    """Every unintentional closure is disclosed WITH its gap, not hidden.

    This asserted a count of one until the axis list disclosed itself. A count was the
    wrong assertion: it made an honest new disclosure fail, which is backwards — the
    incentive it creates is to leave a closure undisclosed rather than to record it. The
    obligation ISD-L-01 actually carries is that an unintentional closure names the gap
    that owns it, and that is what is asserted now, over all of them.
    """
    contract = load_contract()
    unintentional = [d for d in contract.closed_enumerations if not d.intentional]
    assert (
        unintentional
    ), "no unintentional closure is recorded, which would be a claim of completeness"
    for disclosure in unintentional:
        assert disclosure.gap, f"{disclosure.disclosure_id}: unintentional closure names no gap"
    by_name = {d.enumeration: d for d in unintentional}
    assert by_name["KnowledgeCapability"].gap == "ISD-G-01"


# --------------------------------------------------- ISD-L-02 direction expansion


def test_an_enum_on_relationship_type_closes_the_direction_space(
    tmp_path: Any, doc: dict[str, Any]
) -> None:
    """A relationship type constrained by an enumeration is a finite direction space."""
    schema = {"properties": {"type": {"enum": ["Depends-On"], "pattern": "^.*$"}}}
    rel = os.path.join(str(tmp_path), "schema.json")
    with open(rel, "w", encoding="utf-8") as handle:
        json.dump(schema, handle)
    doc["direction_expansion"]["edge_schema"] = "schema.json"
    problems = run("direction_expansion_capacity", doc, repo=str(tmp_path))
    assert any("closes the" in problem for problem in problems)


def test_a_relationship_type_without_a_pattern_is_refused(
    tmp_path: Any, doc: dict[str, Any]
) -> None:
    """An unconstrained type is not the same as an openly constrained one."""
    with open(os.path.join(str(tmp_path), "schema.json"), "w", encoding="utf-8") as handle:
        json.dump({"properties": {"type": {"description": "d"}}}, handle)
    doc["direction_expansion"]["edge_schema"] = "schema.json"
    problems = run("direction_expansion_capacity", doc, repo=str(tmp_path))
    assert any("declares no 'pattern'" in problem for problem in problems)


def test_a_missing_edge_schema_is_refused(doc: dict[str, Any]) -> None:
    """The schema is the measurement surface; absence is a finding."""
    doc["direction_expansion"]["edge_schema"] = "nope.json"
    assert any("unparseable" in p for p in run("direction_expansion_capacity", doc))


def test_a_missing_type_property_path_is_refused(tmp_path: Any, doc: dict[str, Any]) -> None:
    """A schema without the declared property path cannot be measured."""
    with open(os.path.join(str(tmp_path), "schema.json"), "w", encoding="utf-8") as handle:
        json.dump({"properties": {}}, handle)
    doc["direction_expansion"]["edge_schema"] = "schema.json"
    problems = run("direction_expansion_capacity", doc, str(tmp_path))
    assert any("no property path" in problem for problem in problems)


def test_a_missing_freeform_label_is_refused(doc: dict[str, Any]) -> None:
    """Without the freeform label, a new relationship type needs a configuration edit."""
    doc["direction_expansion"]["freeform_admission"]["expected"] = "NOT-THE-LABEL"
    assert any("does not bind" in p for p in run("direction_expansion_capacity", doc))


def test_no_freeform_admission_block_is_refused(doc: dict[str, Any]) -> None:
    """The zero-cost admission path must be declared."""
    doc["direction_expansion"].pop("freeform_admission")
    assert any("no freeform admission" in p for p in run("direction_expansion_capacity", doc))


# ------------------------------------------------------ ISD-L-03 self-application


def test_a_principle_that_exempts_itself_is_refused(doc: dict[str, Any]) -> None:
    """The principle that everything evolves cannot exempt the instrument stating it."""
    doc["self_application"]["subject_of_own_laws"] = []
    assert any("exempts itself" in p for p in run("principle_inherits_itself", doc))


def test_a_principle_claiming_authority_is_refused(doc: dict[str, Any]) -> None:
    """It is a pervasive property, not an authority layer over CMG-000001 or UCIC-001."""
    doc["self_application"]["declares_authority_over"] = ["UCIC-001"]
    assert any("claims authority over" in p for p in run("principle_inherits_itself", doc))


def test_a_principle_declaring_its_own_lifecycle_is_refused(doc: dict[str, Any]) -> None:
    """Declaring an independent lifecycle is opting out of universal inheritance."""
    doc["self_application"]["declares_independent_lifecycle"] = True
    doc["lifecycle_inheritance"]["independent_lifecycle_defined"] = True
    problems = run("principle_inherits_itself", doc)
    assert any("independent_lifecycle false" in p for p in problems)
    assert any("independent_lifecycle_defined false" in p for p in problems)


def test_a_principle_with_no_lifecycle_owner_is_refused(doc: dict[str, Any]) -> None:
    """Inheritance requires a named owner."""
    doc["lifecycle_inheritance"]["lifecycle_owner"] = ""
    assert any("no lifecycle owner" in p for p in run("principle_inherits_itself", doc))


def test_a_principle_without_a_birth_record_is_anonymous(doc: dict[str, Any]) -> None:
    """No anonymous existence, including for the principle itself."""
    doc["self_application"]["birth_identity"] = "urn:ucos:ucko:ucos.master:NOT-BORN"
    assert any("anonymously" in p for p in run("principle_inherits_itself", doc))


def test_a_missing_birth_ledger_is_refused(doc: dict[str, Any]) -> None:
    """The ledger is the measurement surface for identity at creation."""
    doc["self_application"]["birth_ledger"] = "nowhere/birth-ledger.json"
    assert any("unparseable" in p for p in run("principle_inherits_itself", doc))


def test_the_principle_holds_a_birth_record_at_this_cycles_coordinate() -> None:
    """The principle is born, with a qualified temporal coordinate, like any other object."""
    ledger_path = os.path.join(REPO, "00-MASTER/UOBC-000001/birth-ledger.json")
    with open(ledger_path, encoding="utf-8") as fh:
        ledger = json.load(fh)
    record = ledger["births"]["urn:ucos:ucko:ucos.master:UISD-000001"]
    assert record["creation_timestamp"] == "logical:ucos-repository-history@1#485"
    assert record["lifecycle_binding"].startswith("UCIC-001")
    assert record["parent_identity"] is not None


# ------------------------------------------------------ ISD-L-04 lifecycle itself


def test_a_lifecycle_manifest_declaring_itself_closed_is_refused(doc: dict[str, Any]) -> None:
    """A closed stage graph is a finite lifecycle."""
    doc["lifecycle_openness"]["required_manifest_flags"] = {"closed_enumeration": True}
    assert any("closed_enumeration" in p for p in run("lifecycle_applies_to_itself", doc))


def test_a_lifecycle_manifest_without_an_admission_clause_is_refused(doc: dict[str, Any]) -> None:
    """Openness without an admission path is a claim, not a capability."""
    doc["lifecycle_openness"]["required_manifest_fields"] = ["no_such_field"]
    assert any("declares no 'no_such_field'" in p for p in run("lifecycle_applies_to_itself", doc))


def test_a_missing_lifecycle_manifest_is_refused(doc: dict[str, Any]) -> None:
    """No manifest, no measurement."""
    doc["lifecycle_openness"]["manifest"] = "absent.json"
    assert any("unparseable" in p for p in run("lifecycle_applies_to_itself", doc))


def test_a_manifest_without_its_manifest_block_is_refused(
    tmp_path: Any, doc: dict[str, Any]
) -> None:
    """The declared flags live in the manifest block."""
    with open(os.path.join(str(tmp_path), "m.json"), "w", encoding="utf-8") as handle:
        json.dump({"nodes": []}, handle)
    doc["lifecycle_openness"]["manifest"] = "m.json"
    problems = run("lifecycle_applies_to_itself", doc, repo=str(tmp_path))
    assert any("no manifest block" in problem for problem in problems)


def test_an_unavailable_alignment_function_is_refused(doc: dict[str, Any]) -> None:
    """The projection check is not optional."""
    doc["lifecycle_openness"]["alignment_function"] = "no_such_function"
    assert any("is unavailable" in p for p in run("lifecycle_applies_to_itself", doc))


def test_a_diverging_lifecycle_projection_is_refused(doc: dict[str, Any], monkeypatch) -> None:
    """A projection that has drifted from its manifest is a second, silent stage list."""
    fake = types.ModuleType("fake_alignment")
    fake.verify_manifest_alignment = lambda manifest: ("stage 'X' is absent from the engine",)
    monkeypatch.setitem(sys.modules, "fake_alignment", fake)
    doc["lifecycle_openness"]["alignment_module"] = "fake_alignment"
    assert any("diverges from its manifest" in p for p in run("lifecycle_applies_to_itself", doc))


# ------------------------------------------------------ ISD-L-05 evolution itself


def _fake_evolution(stages: tuple[str, ...], *, terminal: bool = False, wrap: bool = True) -> Any:
    """Build a fake evolution module with controllable terminality and wrapping."""
    module = types.ModuleType("fake_evolution")
    module.EVOLUTION_CYCLE = stages
    module.is_terminal = lambda stage: terminal
    if wrap:
        module.next_stage = lambda stage: stages[(stages.index(stage) + 1) % len(stages)]
    else:
        module.next_stage = lambda stage: stages[min(stages.index(stage) + 1, len(stages) - 1)]
    return module


def test_a_terminal_evolution_stage_is_refused(doc: dict[str, Any], monkeypatch) -> None:
    """Evolution that can end has exempted itself from continuation."""
    monkeypatch.setitem(sys.modules, "fake_evolution", _fake_evolution(("a", "b"), terminal=True))
    doc["evolution_openness"]["module"] = "fake_evolution"
    assert any("is terminal" in p for p in run("evolution_applies_to_itself", doc))


def test_an_evolution_cycle_that_does_not_wrap_is_refused(doc: dict[str, Any], monkeypatch) -> None:
    """A cycle whose last stage does not return to the first is a line, not a cycle."""
    monkeypatch.setitem(sys.modules, "fake_evolution", _fake_evolution(("a", "b"), wrap=False))
    doc["evolution_openness"]["module"] = "fake_evolution"
    assert any("does not wrap" in p for p in run("evolution_applies_to_itself", doc))


def test_an_evolution_cycle_below_the_minimum_is_refused(doc: dict[str, Any], monkeypatch) -> None:
    """One stage is not a cycle."""
    monkeypatch.setitem(sys.modules, "fake_evolution", _fake_evolution(("only",)))
    doc["evolution_openness"]["module"] = "fake_evolution"
    doc["evolution_openness"]["minimum_stages"] = 5
    assert any("fewer than 5" in p for p in run("evolution_applies_to_itself", doc))


def test_an_empty_evolution_cycle_reports_and_stops(doc: dict[str, Any], monkeypatch) -> None:
    """An empty cycle is reported once rather than crashing the measurement."""
    module = types.ModuleType("fake_evolution")
    module.EVOLUTION_CYCLE = ()
    module.is_terminal = lambda stage: False
    module.next_stage = lambda stage: stage
    monkeypatch.setitem(sys.modules, "fake_evolution", module)
    doc["evolution_openness"]["module"] = "fake_evolution"
    problems = run("evolution_applies_to_itself", doc)
    assert any("fewer than" in problem for problem in problems)


def test_a_successor_outside_the_cycle_is_refused(doc: dict[str, Any], monkeypatch) -> None:
    """A stage leading out of the cycle is an undeclared exit."""
    module = types.ModuleType("fake_evolution")
    module.EVOLUTION_CYCLE = ("a", "b")
    module.is_terminal = lambda stage: False
    module.next_stage = lambda stage: "escaped"
    monkeypatch.setitem(sys.modules, "fake_evolution", module)
    doc["evolution_openness"]["module"] = "fake_evolution"
    assert any("outside the cycle" in p for p in run("evolution_applies_to_itself", doc))


def test_an_unusable_evolution_module_is_refused(doc: dict[str, Any]) -> None:
    """A declared module that cannot be imported is a finding, not a pass."""
    doc["evolution_openness"]["module"] = "engine.no_such_evolution_module"
    assert any("is unusable" in p for p in run("evolution_applies_to_itself", doc))


# --------------------------------------------------- ISD-L-06 relationship model


class _Term:
    """A minimal term stand-in."""

    def __init__(self, term_id: str, definition: str) -> None:
        self.term_id = term_id
        self.definition = definition


class _Vocabulary:
    """A vocabulary whose extension behaviour is configurable, to falsify the law."""

    def __init__(
        self, terms: list[_Term], *, mutating: bool = False, refusing: bool = False
    ) -> None:
        self.terms = terms
        self._mutating = mutating
        self._refusing = refusing

    def has(self, term_id: str) -> bool:
        return any(term.term_id == term_id for term in self.terms)

    def extended_with(self, term: _Term) -> _Vocabulary:
        if self._refusing:
            return _Vocabulary(list(self.terms))
        if self._mutating:
            self.terms.append(term)
            return self
        return _Vocabulary([*self.terms, term])


def _fake_vocabulary_module(**vocabularies: _Vocabulary) -> Any:
    """Build a fake vocabulary module exposing Term and the given vocabularies."""
    module = types.ModuleType("fake_vocab")
    module.Term = _Term
    for name, vocabulary in vocabularies.items():
        setattr(module, name, vocabulary)
    return module


def _point_at_fake_vocabulary(doc: dict[str, Any], vocabulary: _Vocabulary, monkeypatch) -> None:
    """Rewire the declaration at a single fake vocabulary."""
    monkeypatch.setitem(sys.modules, "fake_vocab", _fake_vocabulary_module(V=vocabulary))
    doc["relationship_expansion"]["module"] = "fake_vocab"
    doc["relationship_expansion"]["vocabularies"] = [
        {"symbol": "V", "tier": "test", "population_at_baseline": 1}
    ]


def test_a_vocabulary_that_refuses_a_term_is_a_closed_tier(
    doc: dict[str, Any], monkeypatch
) -> None:
    """A tier that will not admit a well-formed term is closed."""
    _point_at_fake_vocabulary(doc, _Vocabulary([_Term("a", "d")], refusing=True), monkeypatch)
    assert any("the tier is closed" in p for p in run("relationship_model_expands", doc))


def test_a_vocabulary_mutated_by_extension_is_refused(doc: dict[str, Any], monkeypatch) -> None:
    """Append-only means the original does not move."""
    _point_at_fake_vocabulary(doc, _Vocabulary([_Term("a", "d")], mutating=True), monkeypatch)
    problems = run("relationship_model_expands", doc)
    assert any("mutated the original" in problem for problem in problems)
    assert any("returned the original" in problem for problem in problems)


def test_a_shrinking_vocabulary_is_refused(doc: dict[str, Any], monkeypatch) -> None:
    """An append-only vocabulary cannot lose a term."""
    monkeypatch.setitem(sys.modules, "fake_vocab", _fake_vocabulary_module(V=_Vocabulary([])))
    doc["relationship_expansion"]["module"] = "fake_vocab"
    doc["relationship_expansion"]["vocabularies"] = [
        {"symbol": "V", "tier": "test", "population_at_baseline": 17}
    ]
    assert any("cannot shrink" in p for p in run("relationship_model_expands", doc))


def test_a_growing_vocabulary_is_not_a_violation(doc: dict[str, Any], monkeypatch) -> None:
    """Registering a new relation type must not fail the law that says registration works."""
    _point_at_fake_vocabulary(
        doc, _Vocabulary([_Term("a", "d"), _Term("b", "d"), _Term("c", "d")]), monkeypatch
    )
    assert run("relationship_model_expands", doc) == ()


def test_no_declared_vocabulary_is_refused(doc: dict[str, Any]) -> None:
    """Expansion nobody measures is unmeasured."""
    doc["relationship_expansion"]["vocabularies"] = []
    assert any("no relationship vocabulary" in p for p in run("relationship_model_expands", doc))


def test_an_unusable_vocabulary_symbol_is_refused(doc: dict[str, Any]) -> None:
    """A declared vocabulary that is absent is a finding."""
    doc["relationship_expansion"]["vocabularies"] = [{"symbol": "NOT_A_VOCABULARY"}]
    assert any("unusable" in p for p in run("relationship_model_expands", doc))


def test_an_unusable_vocabulary_module_is_refused(doc: dict[str, Any]) -> None:
    """A declared module that cannot be imported is a finding."""
    doc["relationship_expansion"]["module"] = "engine.no_such_vocabulary"
    assert any("is unusable" in p for p in run("relationship_model_expands", doc))


def test_the_live_relationship_tiers_include_the_class_tier() -> None:
    """Self-application: the model carries a vocabulary of registers OF relationships."""
    contract = load_contract()
    symbols = {str(entry["symbol"]) for entry in contract.relationship_expansion["vocabularies"]}
    assert "RELATIONSHIP_CLASS_VOCABULARY" in symbols
    assert "RELATION_TYPE_VOCABULARY" in symbols


# ------------------------------------------------------------- ISD-L-07 the ratchet


def test_an_undeclared_permanence_site_closes_the_gate(tmp_path: Any, doc: dict[str, Any]) -> None:
    """A new permanence declaration entering the scanned roots is refused."""
    with open(os.path.join(str(tmp_path), "NEW.md"), "w", encoding="utf-8") as handle:
        handle.write("This artifact is under permanent freeze.\n")
    doc["freeze_scan"]["roots"] = ["."]
    doc["freeze_scan"]["root_depth_zero_only"] = ["."]
    doc["freeze_scan"]["preserved_sites"] = []
    problems = run("no_active_permanence_declaration", doc, repo=str(tmp_path))
    assert any("not a declared preserved site" in problem for problem in problems)


def test_a_site_classified_a_is_refused(doc: dict[str, Any]) -> None:
    """Class A is not a category a site may be preserved in."""
    doc["freeze_scan"]["preserved_sites"][0]["class"] = "A"
    assert any("classified A" in p for p in run("no_active_permanence_declaration", doc))


def test_an_undeclared_class_is_refused(doc: dict[str, Any]) -> None:
    """A class outside the declared taxonomy cannot be reasoned about."""
    doc["freeze_scan"]["preserved_sites"][0]["class"] = "Q"
    assert any("is not declared" in p for p in run("no_active_permanence_declaration", doc))


def test_a_changed_count_on_a_historical_site_is_refused(doc: dict[str, Any]) -> None:
    """Historical evidence, identity-bearing names and constitutional text do not change."""
    enforced = next(
        site
        for site in doc["freeze_scan"]["preserved_sites"]
        if site["class"] in doc["freeze_scan"]["count_enforced_classes"]
    )
    enforced["occurrences"] += 3
    problems = run("no_active_permanence_declaration", doc)
    assert any("count-enforced" in problem for problem in problems)


def test_a_changed_count_on_a_commentary_site_is_not_enforced(doc: dict[str, Any]) -> None:
    """Class E registers legitimately grow as they classify more; the gate must not fire."""
    commentary = next(
        site for site in doc["freeze_scan"]["preserved_sites"] if site["class"] == "E"
    )
    commentary["occurrences"] += 99
    assert run("no_active_permanence_declaration", doc) == ()


def test_a_duplicated_preserved_path_is_refused(doc: dict[str, Any]) -> None:
    """Two classifications for one path make the effective class ambiguous."""
    duplicate = copy.deepcopy(doc["freeze_scan"]["preserved_sites"][0])
    duplicate["id"] = "R-DUP"
    doc["freeze_scan"]["preserved_sites"].append(duplicate)
    assert any(
        "more than once" in problem for problem in run("no_active_permanence_declaration", doc)
    )


def test_the_live_scan_finds_no_class_a_site() -> None:
    """The measured conclusion of Workstream 6: zero active permanence declarations."""
    contract = load_contract()
    assert all(site.site_class != "A" for site in contract.freeze_scan.preserved_sites)
    found = scan_occurrences(REPO, contract.freeze_scan)
    declared = {site.path for site in contract.freeze_scan.preserved_sites}
    assert set(found) <= declared


def test_identity_immutability_wording_is_not_scanned() -> None:
    """'never changes' is excluded: it is the inverse of freeze semantics."""
    contract = load_contract()
    assert all("never change" not in phrase for phrase in contract.freeze_scan.phrases)


def test_the_scan_respects_extensions_and_excluded_directories(tmp_path: Any) -> None:
    """The scan covers what it declares and nothing else."""
    base = str(tmp_path)
    os.makedirs(os.path.join(base, "pkg", "__pycache__"))
    os.makedirs(os.path.join(base, ".hidden"))
    for relpath in (
        "top.md",
        "top.rst",
        "pkg/inner.md",
        "pkg/__pycache__/cached.md",
        ".hidden/secret.md",
    ):
        with open(os.path.join(base, relpath), "w", encoding="utf-8") as handle:
            handle.write("permanent freeze\n")
    scan = FreezeScan.of(
        {
            "roots": [".", "pkg"],
            "root_depth_zero_only": ["."],
            "extensions": [".md"],
            "excluded_directory_names": ["__pycache__"],
            "excluded_dot_directories": True,
            "phrases": ["permanent freeze"],
            "status_pattern": "",
            "classes": {"E": "commentary"},
            "count_enforced_classes": [],
            "preserved_sites": [],
        }
    )
    found = scan_occurrences(base, scan)
    assert set(found) == {"top.md", "pkg/inner.md"}
    assert found["top.md"] == 1


def test_a_missing_scan_root_is_skipped_not_fatal(tmp_path: Any) -> None:
    """A declared root that does not exist yields no findings rather than an exception."""
    scan = FreezeScan.of(
        {
            "roots": ["absent-dir", "also-absent"],
            "root_depth_zero_only": ["also-absent"],
            "extensions": [".md"],
            "phrases": ["permanent freeze"],
            "status_pattern": "",
            "classes": {"E": "commentary"},
            "count_enforced_classes": [],
            "preserved_sites": [],
        }
    )
    assert scan_occurrences(str(tmp_path), scan) == {}


def test_the_status_pattern_matches_an_assignment_not_a_bare_token(tmp_path: Any) -> None:
    """A state named in a vocabulary is not a state claimed as terminal."""
    contract = load_contract()
    base = str(tmp_path)
    with open(os.path.join(base, "claim.md"), "w", encoding="utf-8") as handle:
        handle.write("Status: FROZEN\n")
    with open(os.path.join(base, "vocab.md"), "w", encoding="utf-8") as handle:
        handle.write("The declared states are NOT_ELIGIBLE, FREEZING, FROZEN, SUPERSEDED.\n")
    scan = FreezeScan.of(
        {
            "roots": ["."],
            "root_depth_zero_only": ["."],
            "extensions": [".md"],
            "phrases": [],
            "status_pattern": contract.freeze_scan.status_pattern,
            "classes": {"E": "commentary"},
            "count_enforced_classes": [],
            "preserved_sites": [],
        }
    )
    assert set(scan_occurrences(base, scan)) == {"claim.md"}


# ------------------------------------------------- ISD-L-08 baseline temporality


def test_a_qualified_surface_whose_sample_does_not_parse_is_refused(doc: dict[str, Any]) -> None:
    """A coordinate that names no reference system mandates a representation."""
    surface = next(s for s in doc["baseline_temporal_requirement"]["surfaces"] if s["qualified"])
    surface["sample"] = "2026-07-30"
    problems = run("baseline_temporal_qualification", doc)
    assert any("does not parse" in problem for problem in problems)


def test_a_qualified_surface_without_a_sample_is_refused(doc: dict[str, Any]) -> None:
    """A qualification claim needs an instance."""
    surface = next(s for s in doc["baseline_temporal_requirement"]["surfaces"] if s["qualified"])
    surface.pop("sample")
    assert any("carries no sample" in p for p in run("baseline_temporal_qualification", doc))


def test_a_sample_absent_from_its_surface_is_refused(doc: dict[str, Any]) -> None:
    """The disclosure must describe a coordinate the surface actually records."""
    surface = next(s for s in doc["baseline_temporal_requirement"]["surfaces"] if s["qualified"])
    surface["sample"] = "logical:not-in-that-file@1#1"
    assert any("is absent from" in p for p in run("baseline_temporal_qualification", doc))


def test_undisclosed_non_conformance_is_refused(doc: dict[str, Any]) -> None:
    """Non-conformance is admissible; hiding it is not."""
    surface = next(
        s for s in doc["baseline_temporal_requirement"]["surfaces"] if not s["qualified"]
    )
    surface.pop("deferred_to", None)
    surface.pop("gap", None)
    problems = run("baseline_temporal_qualification", doc)
    assert any("undisclosed" in problem for problem in problems)
    assert any("records no gap" in problem for problem in problems)


def test_a_missing_baseline_surface_is_refused(doc: dict[str, Any]) -> None:
    """A surface that does not exist cannot carry a coordinate."""
    doc["baseline_temporal_requirement"]["surfaces"][0]["surface"] = "no/such/file.json"
    assert any("does not exist" in p for p in run("baseline_temporal_qualification", doc))


def test_no_baseline_surfaces_is_vacuous(doc: dict[str, Any]) -> None:
    """An empty surface list would pass trivially."""
    doc["baseline_temporal_requirement"]["surfaces"] = []
    assert any("unmeasured" in p for p in run("baseline_temporal_qualification", doc))


def test_an_unavailable_temporal_resolver_is_refused(doc: dict[str, Any]) -> None:
    """CMG-000002 conformance is measured through the located resolver."""
    doc["baseline_temporal_requirement"]["coordinate_resolver_function"] = "no_such_parser"
    assert any("is unavailable" in p for p in run("baseline_temporal_qualification", doc))


def test_the_live_surfaces_disclose_the_baseline_temporal_gap() -> None:
    """ISD-G-03 and ISD-G-02 are recorded, not silently carried."""
    contract = load_contract()
    gaps = {s.gap for s in contract.baseline_surfaces if not s.qualified}
    assert "ISD-G-03" in gaps
    assert "ISD-G-02" in gaps
    assert all(s.deferred_to for s in contract.baseline_surfaces if not s.qualified)


# ------------------------------------------------------------- ISD-L-09 technology


def _write_pyproject(tmp_path: Any, project: dict[str, Any]) -> str:
    """Write a minimal pyproject and return the directory holding it."""
    lines = ["[project]", f"requires-python = \"{project['requires-python']}\""]
    deps = ", ".join(f'"{d}"' for d in project.get("dependencies", []))
    lines.append(f"dependencies = [{deps}]")
    lines.append("[project.optional-dependencies]")
    dev = ", ".join(f'"{d}"' for d in project.get("dev", []))
    lines.append(f"dev = [{dev}]")
    with open(os.path.join(str(tmp_path), "pyproject.toml"), "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines) + "\n")
    return str(tmp_path)


def test_a_pinned_runtime_dependency_is_refused(tmp_path: Any, doc: dict[str, Any]) -> None:
    """A runtime dependency encodes a technology as constitutional truth."""
    repo = _write_pyproject(tmp_path, {"requires-python": ">=3.12", "dependencies": ["requests"]})
    doc["technology_evolution"]["declared_pins"] = []
    problems = run("technology_is_evolutionary_state", doc, repo=repo)
    assert any("runtime dependency" in problem for problem in problems)


def test_a_version_ceiling_is_refused(tmp_path: Any, doc: dict[str, Any]) -> None:
    """A ceiling makes the language version a constitutional truth rather than a state."""
    repo = _write_pyproject(tmp_path, {"requires-python": ">=3.12,<3.14"})
    doc["technology_evolution"]["declared_pins"] = []
    problems = run("technology_is_evolutionary_state", doc, repo=repo)
    assert any("carries '<'" in problem for problem in problems)


def test_an_undisclosed_pin_is_refused(tmp_path: Any, doc: dict[str, Any]) -> None:
    """A pin without a disclosed reason closes the gate."""
    repo = _write_pyproject(tmp_path, {"requires-python": ">=3.12", "dev": ["ruff==0.1.0"]})
    doc["technology_evolution"]["declared_pins"] = []
    problems = run("technology_is_evolutionary_state", doc, repo=repo)
    assert any("not disclosed with a reason" in problem for problem in problems)


def test_a_stale_disclosed_pin_is_refused(tmp_path: Any, doc: dict[str, Any]) -> None:
    """A disclosure that no longer describes the manifest is drift in the other direction."""
    repo = _write_pyproject(tmp_path, {"requires-python": ">=3.12", "dev": []})
    problems = run("technology_is_evolutionary_state", doc, repo=repo)
    assert any("no longer pinned" in problem for problem in problems)


def test_a_missing_requires_python_is_refused(tmp_path: Any, doc: dict[str, Any]) -> None:
    """The language floor must be declared."""
    with open(os.path.join(str(tmp_path), "pyproject.toml"), "w", encoding="utf-8") as handle:
        handle.write("[project]\ndependencies = []\n")
    doc["technology_evolution"]["declared_pins"] = []
    problems = run("technology_is_evolutionary_state", doc, repo=str(tmp_path))
    assert any("declares no requires-python" in problem for problem in problems)


def test_an_unreadable_technology_manifest_is_refused(doc: dict[str, Any]) -> None:
    """No manifest, no measurement."""
    doc["technology_evolution"]["manifest"] = "absent.toml"
    assert any("unreadable" in p for p in run("technology_is_evolutionary_state", doc))


def test_an_unparseable_technology_manifest_is_refused(tmp_path: Any, doc: dict[str, Any]) -> None:
    """Malformed TOML is a fault of the surface, reported as a finding."""
    with open(os.path.join(str(tmp_path), "pyproject.toml"), "w", encoding="utf-8") as handle:
        handle.write("this is not = = toml\n")
    assert any(
        "unparseable" in problem
        for problem in run("technology_is_evolutionary_state", doc, repo=str(tmp_path))
    )


def test_the_live_manifest_declares_no_runtime_dependency() -> None:
    """Stdlib-only runtime, measured: there is no runtime technology to be locked to."""
    with open(os.path.join(REPO, "pyproject.toml"), "rb") as handle:
        import tomllib

        manifest = tomllib.load(handle)
    assert manifest["project"]["dependencies"] == []
    assert "<" not in manifest["project"]["requires-python"]


# ------------------------------------------------------ ISD-L-10 capability seed


def test_a_final_capability_model_is_refused(doc: dict[str, Any]) -> None:
    """A final capability universe forecloses undiscovered capabilities."""
    doc["capability_seed_model"]["final"] = True
    assert any("declares itself final" in p for p in run("capability_seed_openness", doc))


def test_a_capability_enumeration_without_an_admission_path_is_refused(
    doc: dict[str, Any],
) -> None:
    """An enumeration nobody can add to is a closed universe."""
    doc["capability_seed_model"]["enumerations"][0]["admission"] = ""
    assert any("no admission path" in p for p in run("capability_seed_openness", doc))


def test_a_capability_enumeration_at_a_missing_path_is_refused(doc: dict[str, Any]) -> None:
    """A declared enumeration must exist."""
    doc["capability_seed_model"]["enumerations"][0]["declared_at"] = "no/such/place.json"
    assert any("does not exist" in p for p in run("capability_seed_openness", doc))


def test_a_seed_model_with_no_open_enumeration_cannot_grow(doc: dict[str, Any]) -> None:
    """If every enumeration is closed, 'seed' is a euphemism."""
    for entry in doc["capability_seed_model"]["enumerations"]:
        entry["open"] = False
    assert any("cannot grow" in p for p in run("capability_seed_openness", doc))


def test_no_capability_enumerations_is_vacuous(doc: dict[str, Any]) -> None:
    """An empty enumeration list would pass trivially."""
    doc["capability_seed_model"]["enumerations"] = []
    assert any("unmeasured" in p for p in run("capability_seed_openness", doc))


# ------------------------------------------- ISD-L-11 admission path exercisability


def exercises(doc: dict[str, Any]) -> list[dict[str, Any]]:
    """The declared exercises inside a mutable declaration."""
    return doc["admission_exercisability"]["exercises"]


def by_id(doc: dict[str, Any], exercise_id: str) -> dict[str, Any]:
    """One declared exercise, by id."""
    return next(entry for entry in exercises(doc) if entry["id"] == exercise_id)


def test_an_exercise_naming_an_unimplemented_form_is_refused(doc: dict[str, Any]) -> None:
    """An admission nobody can perform is an unexercised promise."""
    exercises(doc)[0]["form"] = "telepathy"
    problems = build(doc).validate(
        frozenset(LAW_CHECKS), frozenset(contract_module.ADMISSION_FORMS)
    )
    assert any("which is not implemented" in problem for problem in problems)


def test_a_form_no_exercise_names_is_refused(doc: dict[str, Any]) -> None:
    """A handler nothing claims is dead code wearing the appearance of exercisability."""
    problems = build(doc).validate(
        frozenset(LAW_CHECKS), frozenset(contract_module.ADMISSION_FORMS) | {"an_orphan_form"}
    )
    assert any("no exercise names it" in problem for problem in problems)


def test_the_live_contract_supplies_the_form_registry() -> None:
    """load_contract measures forms; the live path is never the unmeasured one."""
    contract = load_contract()
    assert (
        contract.validate(frozenset(LAW_CHECKS), frozenset(contract_module.ADMISSION_FORMS)) == ()
    )
    assert {exercise.form for exercise in contract.admission_exercises} == set(
        contract_module.ADMISSION_FORMS
    )


def test_an_exercise_whose_declared_owner_is_missing_is_refused(doc: dict[str, Any]) -> None:
    """An admission path into a document that does not exist cannot be walked."""
    exercises(doc)[0]["declared_owner"] = "00-MASTER/does/not/exist.json"
    assert any("does not exist" in problem for problem in run("admission_path_exercisability", doc))


def test_an_exercise_with_no_admission_text_is_refused(doc: dict[str, Any]) -> None:
    """A population whose admission nobody wrote down claims nothing that can be tested."""
    exercises(doc)[0]["admission"] = "   "
    assert any(
        "declares no admission path" in problem
        for problem in run("admission_path_exercisability", doc)
    )


def test_a_consumer_that_cannot_be_imported_is_reported(doc: dict[str, Any]) -> None:
    """A surface the law cannot re-read is named, never silently skipped."""
    consumer = by_id(doc, "ISD-AE-01")["consumers"][0]
    consumer["function"] = "no_such_function"
    consumer["expected_refusal"] = "present in manifest, absent from STAGES"
    assert any(
        "refuses differently from the record" in problem
        for problem in run("admission_path_exercisability", doc)
    )


def test_a_refusal_nobody_recorded_is_reported(doc: dict[str, Any]) -> None:
    """A NEW refusing component fails the law even while the known ones are recorded."""
    entry = by_id(doc, "ISD-AE-03")
    entry["consumers"].append(
        {
            "kind": "callable",
            "module": "engine.nucleus.lifecycle",
            "function": "verify_manifest_alignment",
            "required_owner": "a component nobody recorded",
        }
    )
    problems = run("admission_path_exercisability", doc)
    assert any("no refusal is recorded for it" in problem for problem in problems)


def test_a_finite_population_assertion_is_located(tmp_path: Any, doc: dict[str, Any]) -> None:
    """The static arm finds a literal count bound to the population, with file and line.

    Measured against a synthetic source, not against the live suite. This test used to
    require ISD-G-09's real assertion to still be present, which made it fail the moment
    the gap it recorded was CLOSED — a test that resists its own fix, and an incentive to
    leave the defect in place. What is under test is the locator's capability; the
    presence of a violation is what the ratchet is for.
    """
    source = tmp_path / "offender.py"
    source.write_text("def t():\n    assert len(unintentional) == 1\n", encoding="utf-8")
    consumer = ExerciseConsumer(
        kind="assertion_scan",
        module="",
        function="",
        paths=(str(source.relative_to(tmp_path)),),
        population_tokens=("unintentional",),
        required_owner="synthetic",
        expected_refusal="binds 1",
        gap="",
    )
    located = contract_module._population_literals(str(tmp_path), consumer)
    assert located, "the locator no longer finds a literal count bound to a population"
    assert any("binds 1" in item for item in located)


def test_a_recorded_refusal_that_no_longer_occurs_is_refused(doc: dict[str, Any]) -> None:
    """The ratchet turns the other way too: a stale record fails until it is corrected."""
    consumer = by_id(doc, "ISD-AE-03")["consumers"][0]
    consumer["expected_refusal"] = "a refusal that does not happen"
    consumer["gap"] = "ISD-G-99"
    problems = run("admission_path_exercisability", doc)
    assert any("no longer occurs" in problem for problem in problems)


def test_an_exercise_expecting_admission_while_recording_a_refusal_is_refused(
    doc: dict[str, Any],
) -> None:
    """A declaration cannot claim both that the path works and that it is blocked."""
    by_id(doc, "ISD-AE-03")["consumers"][0]["expected_refusal"] = "something"
    problems = build(doc).validate(
        frozenset(LAW_CHECKS), frozenset(contract_module.ADMISSION_FORMS)
    )
    assert any("expects admission while recording a refusal" in problem for problem in problems)


def test_a_recorded_refusal_with_no_gap_is_refused(doc: dict[str, Any]) -> None:
    """A refusal nobody routed to a gap is an undisclosed finite assumption."""
    by_id(doc, "ISD-AE-01")["consumers"][0]["gap"] = ""
    problems = build(doc).validate(
        frozenset(LAW_CHECKS), frozenset(contract_module.ADMISSION_FORMS)
    )
    assert any("names no gap" in problem for problem in problems)


def test_an_exercise_expecting_refusal_that_records_none_is_refused(doc: dict[str, Any]) -> None:
    """Expecting a refusal without naming the refusing component leaves the owner unrouted."""
    exercise = by_id(doc, "ISD-AE-02")
    exercise["expected"] = "refused"
    for consumer in exercise["consumers"]:
        consumer["expected_refusal"] = ""
    problems = build(doc).validate(
        frozenset(LAW_CHECKS), frozenset(contract_module.ADMISSION_FORMS)
    )
    assert any("records none" in problem for problem in problems)


def test_an_empty_exercise_list_is_refused(doc: dict[str, Any]) -> None:
    """A law over zero exercises would be vacuous rather than satisfied."""
    doc["admission_exercisability"]["exercises"] = []
    assert any(
        "would be vacuous" in problem for problem in run("admission_path_exercisability", doc)
    )


def test_a_probe_without_the_declared_prefix_is_refused(doc: dict[str, Any]) -> None:
    """A probe that could collide with a real member is refused before it is appended."""
    by_id(doc, "ISD-AE-01")["target"]["probe_overrides"]["id"] = "UCL-S-0455"
    assert any(
        "does not carry the declared" in problem
        for problem in run("admission_path_exercisability", doc)
    )


def test_the_live_exercises_hold_and_the_positive_control_admits() -> None:
    """ISD-L-11 holds, and at least one declared admission path is measured actually working."""
    contract = load_contract()
    assert LAW_CHECKS["admission_path_exercisability"](contract, REPO) == ()
    admitted = [e for e in contract.admission_exercises if e.expected == "admitted"]
    assert admitted, "a law that can only ever fail is indistinguishable from a broken law"
    for exercise in admitted:
        subject = contract_module.ADMISSION_FORMS[exercise.form](
            exercise, REPO, contract.probe_id_prefix
        )
        for consumer in exercise.consumers:
            assert contract_module._consumer_refusal(consumer, REPO, subject) == ""


def test_the_recorded_refusals_still_occur_and_name_their_owner() -> None:
    """Every exercise declared to refuse still refuses, and routes an owner and a gap."""
    contract = load_contract()
    refusing = [e for e in contract.admission_exercises if e.expected == "refused"]
    assert refusing
    for exercise in refusing:
        subject = contract_module.ADMISSION_FORMS[exercise.form](
            exercise, REPO, contract.probe_id_prefix
        )
        recorded = [c for c in exercise.consumers if c.refuses_today]
        assert recorded
        for consumer in recorded:
            actual = contract_module._consumer_refusal(consumer, REPO, subject)
            assert consumer.expected_refusal in actual
            assert consumer.required_owner.strip()
            assert consumer.gap.strip()


def test_exercising_every_admission_mutates_nothing_on_disk() -> None:
    """OBSERVE MODE across the new law: every declared owner is byte-identical afterwards."""
    contract = load_contract()
    watched = [exercise.declared_owner for exercise in contract.admission_exercises] + [
        "00-MASTER/UCOS-UGA-001/01-EXECUTABLE-OBJECT-REGISTRY.json",
        "00-BOOK/DATA/id-ledger.json",
    ]

    def digests() -> dict[str, str]:
        out: dict[str, str] = {}
        for relpath in watched:
            with open(os.path.join(REPO, relpath), "rb") as handle:
                out[relpath] = hashlib.sha256(handle.read()).hexdigest()
        return out

    before = digests()
    LAW_CHECKS["admission_path_exercisability"](contract, REPO)
    LAW_CHECKS["admission_path_exercisability"](contract, REPO)
    assert digests() == before


# ------------------------------------------------------------------------ the gate


def test_the_gate_exits_open_on_the_live_declaration(capsys) -> None:
    """Exit 0 and a rendered report naming every law."""
    assert gate_module.main([]) == gate_module.EXIT_OPEN
    rendered = capsys.readouterr().out
    assert "GATE PASSED" in rendered
    for law in load_contract().laws:
        assert law.law_id in rendered


def test_the_gate_emits_json_on_request(capsys) -> None:
    """The machine-readable report is a superset of the rendered one."""
    assert gate_module.main(["--json"]) == gate_module.EXIT_OPEN
    report = json.loads(capsys.readouterr().out)
    assert report["verdict"] == "OPEN"
    assert len(report["laws"]) == len(load_contract().laws)


def test_quiet_suppresses_the_report_when_open(capsys) -> None:
    """A passing quiet run says nothing."""
    assert gate_module.main(["--quiet"]) == gate_module.EXIT_OPEN
    assert capsys.readouterr().out == ""


def test_the_gate_exits_closed_and_explains_itself(
    tmp_path: Any, doc: dict[str, Any], capsys
) -> None:
    """Exit 1 on a refused law, and a quiet run still reports the reason on stderr."""
    doc["capability_seed_model"]["final"] = True
    target = write_declaration(tmp_path, doc)
    assert gate_module.main(["--declaration", target, "--quiet"]) == gate_module.EXIT_CLOSED
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "GATE CLOSED" in captured.err
    assert "declares itself final" in captured.err


def test_the_gate_faults_on_an_unusable_declaration(tmp_path: Any, capsys) -> None:
    """Exit 2 is a different answer from exit 1, deliberately."""
    broken = os.path.join(str(tmp_path), "broken.json")
    with open(broken, "w", encoding="utf-8") as handle:
        handle.write("{")
    assert gate_module.main(["--declaration", broken]) == gate_module.EXIT_FAULT
    assert "INFINITE SCOPE FAULT" in capsys.readouterr().err


def test_the_gate_accepts_a_repository_override(tmp_path: Any, doc: dict[str, Any]) -> None:
    """Measuring a different tree is how the checks are falsified in tests."""
    doc["freeze_scan"]["roots"] = ["."]
    doc["freeze_scan"]["root_depth_zero_only"] = ["."]
    target = write_declaration(tmp_path, doc)
    assert gate_module.main(["--declaration", target, "--repository", str(tmp_path), "--json"]) in (
        gate_module.EXIT_OPEN,
        gate_module.EXIT_CLOSED,
    )


def test_assess_returns_one_entry_per_law_in_declaration_order() -> None:
    """The report order is the declaration order, so a reader can follow along."""
    contract = load_contract()
    results = assess(contract, REPO)
    assert [law_id for law_id, _, _ in results] == [law.law_id for law in contract.laws]


def test_the_declaration_path_is_where_the_declaration_lives() -> None:
    """The engine finds its declaration without configuration."""
    assert DECLARATION_PATH == "00-MASTER/UISD-000001/uisd-declaration.json"
    assert os.path.exists(os.path.join(REPO, DECLARATION_PATH))


def test_reading_an_unreadable_file_is_survivable(tmp_path: Any) -> None:
    """A file that cannot be read yields None rather than raising mid-scan."""
    assert contract_module._read_text(str(tmp_path), "absent.md") is None
    assert contract_module._read_json(str(tmp_path), "absent.json") is None
    bad = os.path.join(str(tmp_path), "bad.json")
    with open(bad, "w", encoding="utf-8") as handle:
        handle.write("{oops")
    assert contract_module._read_json(str(tmp_path), "bad.json") is None


# --- certification identity ------------------------------------------------------------------
#
# This package measured eleven laws and returned a verdict attributable to NO state: nothing in
# it minted a digest, so two different declarations reaching two opposite verdicts produced
# reports that could not be told apart, and a recorded PASS could never say WHICH declaration it
# was a pass of. UEC-000001 counted it under `declarations_without_a_certification_identity`.
#
# Both halves are asserted: the identity must MOVE when the declaration's meaning moves, and
# must NOT move for anything declared inert.

from engine.infinite_scope.declaration import DIGEST_EXCLUSIONS  # noqa: E402
from engine.infinite_scope.declaration import parse as parse_declaration  # noqa: E402
from engine.uckp.canonical import content_hash  # noqa: E402

IDENTITY_MUTATIONS = {
    "change the declared authority": lambda d: d.__setitem__("authority", "SOMETHING ELSE"),
    "change the declared version": lambda d: d.__setitem__("version", "9.9.9"),
    "change the declared name": lambda d: d.__setitem__("name", "Something Else"),
    "rewrite a law's statement": lambda d: d["laws"][0].__setitem__("statement", "something else"),
    "rewrite a law's title": lambda d: d["laws"][0].__setitem__("title", "Something Else"),
    "drop an expansion axis": lambda d: d["expansion_axes"].pop(),
    "declare the capability model final": lambda d: d["capability_seed_model"].__setitem__(
        "final", True
    ),
    "drop a closed-enumeration disclosure": lambda d: d["closed_enumeration_disclosures"].pop(),
}


def _identity(document: dict[str, Any]) -> str:
    return content_hash(parse_declaration(document, source="test").digest_payload())


@pytest.mark.parametrize("name", sorted(IDENTITY_MUTATIONS))
def test_every_semantic_mutation_moves_the_certification_identity(
    doc: dict[str, Any], name: str
) -> None:
    """A value that can alter a verdict must be inside the identity that certifies it."""
    baseline = _identity(copy.deepcopy(doc))
    mutated = copy.deepcopy(doc)
    IDENTITY_MUTATIONS[name](mutated)
    assert _identity(mutated) != baseline, (
        f"{name!r} changed the declaration's meaning and left the certification identity at "
        f"{baseline[:16]}…. The same digest now certifies two different declarations."
    )


def test_the_identity_is_independent_of_the_path_it_was_read_from(doc: dict[str, Any]) -> None:
    """A digest that changed with the reader would not be a digest of the declaration."""
    left = _identity(copy.deepcopy(doc))
    right = content_hash(
        parse_declaration(copy.deepcopy(doc), source="/elsewhere.json").digest_payload()
    )
    assert left == right


def test_the_identity_covers_every_parsed_field_except_the_declared_exclusions(
    doc: dict[str, Any],
) -> None:
    """Inclusion is the default; an omission must be a declared, reasoned exclusion."""

    contract = parse_declaration(doc, source="test")
    payload = contract.digest_payload()
    parsed = {field.name for field in _dc.fields(contract)}
    missing = parsed - set(payload)
    assert missing <= set(DIGEST_EXCLUSIONS), (
        "fields silently absent from the certification identity: "
        f"{sorted(missing - set(DIGEST_EXCLUSIONS))}"
    )


def test_a_stale_exclusion_is_refused(doc: dict[str, Any]) -> None:
    """The other direction. An exclusion matching no field may silently widen later."""

    contract = parse_declaration(doc, source="test")
    assert set(DIGEST_EXCLUSIONS) <= {field.name for field in _dc.fields(contract)}


def test_the_gate_report_carries_the_certification_identity() -> None:
    """An identity that never reaches a report certifies nothing."""
    report = gate_module.measure()
    assert len(report["declaration_digest"]) == 64


# --------------------------------------------------------------------------------
# ISD-L-01, second half — the closure detector and its ratchet
#
# ISD-L-01 used to validate the DISCLOSURES and nothing else: each named a closing
# invariant, an admission path and an existing file. That measured the list against
# itself. The repository structurally contains 895 closed enumerations and the list
# covered six of them, so "no enumeration is closed silently" was true of the eleven
# somebody had remembered and unmeasured everywhere else — including
# KNOWN_EXECUTION_KINDS in the constitutional kernel, whose comment claims "Open by
# registration (Article 17)" over a frozen tuple no registration function can extend.
# --------------------------------------------------------------------------------
import dataclasses as _dc  # noqa: E402

from engine.infinite_scope import detector as _detector  # noqa: E402
from engine.infinite_scope.declaration import load  # noqa: E402
from engine.infinite_scope.detector import closures_in_source, detect  # noqa: E402


def _ceiling(doc: dict, value: int) -> dict:
    out = copy.deepcopy(doc)
    out["closure_detection"]["undisclosed_ceiling"] = value
    return out


def test_detector_finds_each_declared_shape() -> None:
    """All three shapes, and nothing that merely resembles them."""
    found = _detector.closures_in_source(
        "import enum\n"
        "class Kind(enum.Enum):\n    A = 'a'\n    B = 'b'\n"
        "NAMES = ('x', 'y', 'z')\n"
        "FROZEN = frozenset({'p', 'q'})\n"
        "ONE = ('solo',)\n"  # below MIN_MEMBERS: a value, not a set
        "NUMS = (1, 2, 3)\n"  # not an identifier space
        "OPEN = registry.load()\n"  # built by calling, therefore open
        "lower = ('a', 'b')\n",  # a local value, not a declared constant
        "sample.py",
    )
    assert {(c.shape, c.name) for c in found} == {
        ("enum", "Kind"),
        ("literal-set", "NAMES"),
        ("literal-set", "FROZEN"),
    }


def test_the_detector_is_not_its_own_first_finding(doc: dict) -> None:
    """check_no_active_permanence_declaration records what happens when a detector
    matches its own source. This module has the same exposure and answers it by shape
    rather than evasion — a docstring naming a shape is not an instance of it."""
    config = doc["closure_detection"]
    found = _detector.detect(
        REPO,
        tuple(config["roots"]),
        frozenset(config["excluded_directory_names"]),
        tuple(config["excluded_path_fragments"]),
    )
    mine = [c for c in found if c.path.endswith("infinite_scope/detector.py")]
    assert mine == [], f"the detector detected itself: {[c.describe() for c in mine]}"


def test_the_ratchet_refuses_a_new_undisclosed_closure(doc: dict) -> None:
    measured = doc["closure_detection"]["undisclosed_ceiling"]
    problems = check_scope_expansion_capacity(
        InfiniteScopeContract.from_declaration(_ceiling(doc, measured - 1)), REPO
    )
    assert any("exceed the declared ceiling" in p for p in problems)


def test_the_ratchet_refuses_slack_beneath_the_ceiling(doc: dict) -> None:
    """The lower side is the half that gets forgotten. Debt repaid without tightening
    leaves room a future regression occupies in silence."""
    measured = doc["closure_detection"]["undisclosed_ceiling"]
    problems = check_scope_expansion_capacity(
        InfiniteScopeContract.from_declaration(_ceiling(doc, measured + 11)), REPO
    )
    assert any("BELOW the declared ceiling" in p for p in problems)


def test_a_detector_that_finds_nothing_is_broken_not_satisfied(doc: dict) -> None:
    doc["closure_detection"]["roots"] = ["00-BOOK/DATA"]  # real, and holds no Python
    problems = check_scope_expansion_capacity(InfiniteScopeContract.from_declaration(doc), REPO)
    assert any("found nothing" in p or "located no closed enumeration" in p for p in problems)


def test_a_disclosure_covers_one_binding_not_a_whole_file() -> None:
    """Matching on the file alone would let one disclosure absolve every enumeration in
    a module, which is how a disclosure list becomes a suppression list."""
    found = [
        _detector.Closure("m.py", 1, "enum", "Disclosed", 3),
        _detector.Closure("m.py", 9, "literal-set", "UNDISCLOSED", 4),
    ]
    left = _detector.undisclosed(found, frozenset({("m.py", "Disclosed")}))
    assert [c.name for c in left] == ["UNDISCLOSED"]


def test_the_axis_list_discloses_itself(doc: dict) -> None:
    """The principle declares infinite directions; its own instrument enumerated eleven
    and did not disclose that it had. ISD-L-01 requires every closed enumeration to name
    what closes it, and nothing closes this one."""
    axes = [
        d for d in doc["closed_enumeration_disclosures"] if d["enumeration"] == "expansion_axes"
    ]
    assert axes, "expansion_axes is a closed enumeration this declaration does not disclose"
    assert axes[0]["admission"], "disclosed with no admission path"
    exercises = {e["id"] for e in doc["admission_exercisability"]["exercises"]}
    assert "ISD-AE-04" in exercises, "the axis admission path is asserted, never exercised"


# ------------------------------------------------ the branches a sound repository never takes


def test_a_scanned_file_that_cannot_be_read_is_skipped_rather_than_counted(
    declaration: dict[str, Any], monkeypatch: Any
) -> None:
    """A file the scanner cannot read has no occurrences to count, and counting it as zero and
    counting it as unreadable are the same number. Skipping it is what keeps the permanence
    census a count of what was read rather than of what was looked for."""
    scan = build(copy.deepcopy(declaration)).freeze_scan
    monkeypatch.setattr(contract_module, "_read_text", lambda repo, relpath: None)
    assert scan_occurrences(REPO, scan) == {}


def test_a_closure_ceiling_that_is_not_an_integer_is_refused(doc: dict[str, Any]) -> None:
    """The ceiling is a ratchet, and a ratchet compared against a non-number is a comparison
    nobody can lose. Refusing up front is what stops the law from silently holding."""
    doc["closure_detection"]["undisclosed_ceiling"] = "as few as possible"
    assert any(
        "no integer undisclosed_ceiling" in problem
        for problem in run("scope_expansion_capacity", doc)
    )


def test_an_edge_schema_whose_type_property_is_not_a_mapping_is_refused(
    tmp_path: Any, doc: dict[str, Any]
) -> None:
    """The forbidden and required key checks are membership tests over that mapping. Against a
    string they are substring tests, and `"enum" in "some string"` decides nothing about the
    direction space."""
    with open(os.path.join(str(tmp_path), "schema.json"), "w", encoding="utf-8") as handle:
        json.dump({"properties": {"type": "a string where an object belongs"}}, handle)
    doc["direction_expansion"]["edge_schema"] = "schema.json"
    problems = run("direction_expansion_capacity", doc, str(tmp_path))
    assert any("the type property is not a mapping" in problem for problem in problems)


# ------------------------------------------------------- the admission probe's own refusals


def _lone_exercise(doc: dict[str, Any], tmp_path: Any, **target: Any) -> dict[str, Any]:
    """Replace every declared exercise with one synthetic exercise over a scratch document.

    Deriving the probe from the live declaration would tie these tests to whichever population
    happens to be declared today; the failures under measurement are properties of the probe
    builder, not of any particular owner.
    """
    owner = "probe-owner.json"
    with open(os.path.join(str(tmp_path), owner), "w", encoding="utf-8") as handle:
        json.dump({"nodes": [{"id": "real-member"}]}, handle)
    exercise = {
        "id": "ISD-AE-PROBE",
        "population_id": "a scratch population",
        "declared_owner": owner,
        "admission": "append a member",
        "form": "document_append",
        "target": {
            "pointer": "/nodes",
            "id_field": "id",
            "probe_from_sibling": 0,
            "probe_overrides": {"id": "isd-admission-probe-1"},
        },
        "expected": "admitted",
        "consumers": [],
    }
    exercise["target"].update(target)
    doc["admission_exercisability"]["exercises"] = [exercise]
    return exercise


def test_a_probe_target_declaring_no_overrides_is_refused(doc: dict[str, Any], tmp_path: Any):
    """The overrides are what make the probe a probe: without them the appended member is a
    byte-identical copy of a real one, and admitting it would prove nothing about a NEW member."""
    exercise = _lone_exercise(doc, tmp_path)
    exercise["target"].pop("probe_overrides")
    problems = run("admission_path_exercisability", doc, str(tmp_path))
    assert any("declares no probe_overrides" in problem for problem in problems)


def test_a_probe_with_no_declared_sibling_is_built_from_nothing(doc: dict[str, Any], tmp_path: Any):
    """A population whose members this engine cannot pattern-match still gets a probe — built
    from the overrides alone. Refusing instead would make the law unusable for exactly the
    populations it exists to measure."""
    _lone_exercise(doc, tmp_path, probe_from_sibling=99)
    assert run("admission_path_exercisability", doc, str(tmp_path)) == ()


def test_a_sibling_that_is_not_a_mapping_is_refused(doc: dict[str, Any], tmp_path: Any) -> None:
    """A probe derived from a string cannot carry the declared overrides, and appending the
    overrides alone would silently measure a different population shape."""
    owner = "scalar-owner.json"
    with open(os.path.join(str(tmp_path), owner), "w", encoding="utf-8") as handle:
        json.dump({"nodes": ["a bare string member"]}, handle)
    _lone_exercise(doc, tmp_path)
    doc["admission_exercisability"]["exercises"][0]["declared_owner"] = owner
    problems = run("admission_path_exercisability", doc, str(tmp_path))
    assert any("sibling member is not a mapping" in problem for problem in problems)


def test_an_owner_that_exists_and_does_not_parse_is_refused(doc: dict[str, Any], tmp_path: Any):
    """Absent and unparseable are different failures. The absence check above cannot see the
    second, because the file is right there."""
    owner = "broken-owner.json"
    with open(os.path.join(str(tmp_path), owner), "w", encoding="utf-8") as handle:
        handle.write("{ not json")
    _lone_exercise(doc, tmp_path)
    doc["admission_exercisability"]["exercises"][0]["declared_owner"] = owner
    problems = run("admission_path_exercisability", doc, str(tmp_path))
    assert any("absent or unparseable" in problem for problem in problems)


def test_a_pointer_that_resolves_to_no_list_is_refused(doc: dict[str, Any], tmp_path: Any) -> None:
    """A pointer into nothing and a pointer into a scalar both mean the same thing: there is no
    population here to append a member to, so the admission path cannot be walked."""
    _lone_exercise(doc, tmp_path, pointer="/nodes/not/a/population")
    problems = run("admission_path_exercisability", doc, str(tmp_path))
    assert any("does not resolve to a list" in problem for problem in problems)


def test_a_reader_form_declaring_no_reader_is_refused(doc: dict[str, Any], tmp_path: Any) -> None:
    """The reader form exists because the reader is where the owner's structural validation
    lives. Naming the form and not the reader claims that validation without invoking it."""
    _lone_exercise(doc, tmp_path)
    doc["admission_exercisability"]["exercises"][0]["form"] = "reader_document_append"
    problems = run("admission_path_exercisability", doc, str(tmp_path))
    assert any("declares no reader" in problem for problem in problems)


def test_an_exercise_naming_a_form_nothing_implements_is_named_by_the_law(
    doc: dict[str, Any], tmp_path: Any
) -> None:
    """`validate` refuses this at load time. The law refuses it again at measurement time, and
    the second refusal is what protects a caller that reached the check some other way."""
    _lone_exercise(doc, tmp_path)
    doc["admission_exercisability"]["exercises"][0]["form"] = "telepathy"
    problems = run("admission_path_exercisability", doc, str(tmp_path))
    assert any("which is not implemented" in problem for problem in problems)


def test_an_admission_that_fails_in_an_unexpected_way_is_a_finding_not_a_crash(
    doc: dict[str, Any], tmp_path: Any
) -> None:
    """The handler is given a declaration this engine did not write. Every way it can fail is a
    finding about the declaration; letting one out as an exception would take the gate down with
    no verdict on this law or any law after it."""
    _lone_exercise(doc, tmp_path, reader_module="a.module.nobody.installed", reader_function="read")
    doc["admission_exercisability"]["exercises"][0]["form"] = "reader_document_append"
    problems = run("admission_path_exercisability", doc, str(tmp_path))
    assert any("ModuleNotFoundError" in problem for problem in problems)


def test_a_consumer_kind_this_law_cannot_re_evaluate_is_named(doc: dict[str, Any], tmp_path: Any):
    """A kind nobody can re-evaluate must not read as an admission: silence from an unrunnable
    consumer is indistinguishable from silence from one that admitted."""
    _lone_exercise(doc, tmp_path)
    doc["admission_exercisability"]["exercises"][0]["consumers"] = [
        {
            "kind": "divination",
            "required_owner": "somewhere",
            "expected_refusal": "",
            "gap": "",
        }
    ]
    problems = run("admission_path_exercisability", doc, str(tmp_path))
    assert any("is not a kind this law can re-evaluate" in problem for problem in problems)


def test_a_consumer_returning_a_single_refusal_string_is_read_as_one_refusal(
    doc: dict[str, Any],
) -> None:
    """Consumers answer in three shapes — a string, a sequence, or nothing — and a string that
    was joined character by character would report a refusal per letter."""
    consumer = ExerciseConsumer(
        kind="callable",
        module="os.path",
        function="basename",
        paths=(),
        population_tokens=(),
        required_owner="synthetic",
        expected_refusal="",
        gap="",
    )
    assert contract_module._callable_refusal(consumer, "a/refusal") == "refusal"


def test_a_consumer_path_that_cannot_be_read_or_parsed_is_reported(tmp_path: Any) -> None:
    """The assertion scan is a static read over declared paths. A path it cannot read is a stale
    declaration, and one that does not parse is a different defect owned by the lint gate —
    both of which must be said out loud rather than counted as "no literal found"."""
    unreadable = os.path.join(str(tmp_path), "unreadable.py")
    with open(unreadable, "w", encoding="utf-8") as handle:
        handle.write("COUNT = 1\n")
    os.chmod(unreadable, 0o000)
    with open(os.path.join(str(tmp_path), "broken.py"), "w", encoding="utf-8") as handle:
        handle.write("def (:::\n")
    consumer = ExerciseConsumer(
        kind="assertion_scan",
        module="",
        function="",
        paths=("unreadable.py", "broken.py"),
        population_tokens=("COUNT",),
        required_owner="synthetic",
        expected_refusal="",
        gap="",
    )
    located = contract_module._population_literals(str(tmp_path), consumer)
    assert any("is unreadable" in item for item in located)
    assert any("does not parse" in item for item in located)


def test_a_binding_chain_longer_than_the_locator_follows_is_not_followed_forever(
    tmp_path: Any,
) -> None:
    """The subject is resolved through local bindings, and the walk is bounded. An unbounded one
    would loop on a self-referential binding; a bounded one stops and reports nothing, which is
    the conservative direction for a locator whose findings are refusals."""
    source = os.path.join(str(tmp_path), "chained.py")
    with open(source, "w", encoding="utf-8") as handle:
        handle.write(
            "def test_chain():\n"
            "    a = STAGES\n"
            "    b = a\n"
            "    c = b\n"
            "    d = c\n"
            "    e = d\n"
            "    f = e\n"
            "    g = f\n"
            "    h = g\n"
            "    assert len(h) == 45\n"
        )
    consumer = ExerciseConsumer(
        kind="assertion_scan",
        module="",
        function="",
        paths=("chained.py",),
        population_tokens=("STAGES",),
        required_owner="synthetic",
        expected_refusal="",
        gap="",
    )
    assert contract_module._population_literals(str(tmp_path), consumer) == ()


# --------------------------------------------------------- the declaration's own refusals


def test_an_exercise_whose_consumers_are_not_a_list_is_a_fault(doc: dict[str, Any]) -> None:
    """A mapping where a list belongs would iterate its keys, and every consumer would be a
    string this engine then failed to read as a consumer."""
    exercises(doc)[0]["consumers"] = {"kind": "callable"}
    with pytest.raises(InfiniteScopeError, match="consumers is absent or not a list"):
        build(doc)


def test_a_duplicated_exercise_id_is_refused(doc: dict[str, Any]) -> None:
    """Two exercises under one id make the evidence unattributable: a recorded refusal cannot
    be routed back to the exercise that produced it."""
    exercises(doc).append(copy.deepcopy(exercises(doc)[0]))
    problems = build(doc).validate(
        frozenset(LAW_CHECKS), frozenset(contract_module.ADMISSION_FORMS)
    )
    assert any("declared more than once" in problem for problem in problems)


def test_an_exercise_expecting_something_other_than_admission_or_refusal_is_refused(
    doc: dict[str, Any],
) -> None:
    """Those are the two outcomes the ratchet is defined over. A third would be an expectation
    no measurement can confirm or contradict."""
    exercises(doc)[0]["expected"] = "probably fine"
    problems = build(doc).validate(
        frozenset(LAW_CHECKS), frozenset(contract_module.ADMISSION_FORMS)
    )
    assert any("expected" in problem for problem in problems)


def test_the_committed_declaration_is_loadable_by_path(tmp_path: Any, doc: dict[str, Any]) -> None:
    """`load` is the reader every caller outside this package uses; `parse` is the one the tests
    use. Measuring only the second would leave the real entry point unexercised."""

    contract = load(write_declaration(tmp_path, doc))
    assert contract.laws


# ------------------------------------------------------------ the closure detector's edges


def test_a_module_that_does_not_parse_yields_no_closure() -> None:
    """A syntax error is a different defect, owned by the lint gate. Reporting it here would
    attribute it to the wrong law and put a permanent finding in the closure census."""

    assert closures_in_source("def (:::\n", "broken.py") == []


def test_a_literal_type_carrying_a_non_constant_member_is_not_a_closure() -> None:
    """`Literal[SOME_NAME]` names something resolved elsewhere, so the set of values it admits
    is not visible here. Counting it would put a number on a population nobody enumerated."""

    source = "from typing import Literal\nA = 1\nB = 2\nKind = Literal[A, B, 'c']\n"
    assert not [c for c in closures_in_source(source, "m.py") if c.kind == "literal-type"]


def test_a_module_that_cannot_be_opened_is_skipped_rather_than_crashing_the_detector(
    tmp_path: Any,
) -> None:
    """The census walks the whole repository. One unreadable file must not be the reason the
    ceiling cannot be measured at all."""

    root = os.path.join(str(tmp_path), "layer")
    os.makedirs(root)
    unreadable = os.path.join(root, "closed.py")
    with open(unreadable, "w", encoding="utf-8") as handle:
        handle.write("MEMBERS = ('a', 'b', 'c', 'd', 'e')\n")
    os.chmod(unreadable, 0o000)
    assert detect(str(tmp_path), ("layer",), frozenset(), ()) == []
