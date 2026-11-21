"""UCPA-000001 — the constitutional primitive alignment gate, measured.

Each law is exercised in both directions: it holds over the repository as it stands, and
it refuses a contract deliberately broken in the one way that law exists to catch. A law
tested only where it passes is a law nobody has shown can fail.
"""

from __future__ import annotations

import ast
import dataclasses
import json
import pathlib

import pytest

from engine.root_ontology import contract as contract_module
from engine.root_ontology.contract import (
    LAW_CHECKS,
    assess,
    load_contract,
    load_declaration,
    repo_root,
)
from engine.root_ontology.gate import EXIT_CLOSED, EXIT_FAULT, EXIT_OPEN, main, measure
from engine.root_ontology.model import (
    AXIOM,
    LAYER,
    ROLE_AUTHORITY,
    ROLE_SUPERSEDED,
    AlignmentContract,
    AlignmentError,
    Primitive,
    Projection,
    Reduction,
)


@pytest.fixture(name="repo")
def _repo() -> str:
    return repo_root()


@pytest.fixture(name="contract")
def _contract() -> AlignmentContract:
    return load_contract()


@pytest.fixture(name="document")
def _document() -> dict:
    return load_declaration()


def _run(name: str, contract: AlignmentContract, repo: str) -> tuple[str, ...]:
    """Measure one law check by name."""
    return LAW_CHECKS[name](contract, repo)


# --- the repository as it stands ------------------------------------------------------


def test_the_gate_is_open_over_the_repository_as_it_stands(contract, repo):
    for law_id, _title, violations in assess(contract, repo):
        assert violations == (), f"{law_id}: {violations}"


def test_the_report_counts_what_it_measured(contract):
    report = measure()
    assert report["open"] is True
    assert report["laws_measured"] == len(contract.laws)
    assert report["laws_holding"] == report["laws_measured"]
    assert report["primitives"] == len(contract.primitives)
    assert report["facets_reduced"] == len(contract.reductions)


def test_measuring_twice_produces_the_same_report():
    assert measure() == measure()


def test_the_cli_reports_open(capsys):
    assert main(["--quiet"]) == EXIT_OPEN


def test_the_cli_can_emit_json(capsys):
    assert main(["--json", "--quiet"]) == EXIT_OPEN
    payload = json.loads(capsys.readouterr().out)
    assert payload["artifact_id"] == "UCPA-000001"
    assert payload["open"] is True


def test_an_unusable_declaration_is_a_fault_not_a_verdict(tmp_path, capsys):
    broken = tmp_path / "ucpa-declaration.json"
    broken.write_text("{ not json", encoding="utf-8")
    assert main(["--declaration", str(broken), "--quiet"]) == EXIT_FAULT
    assert "FAULT" in capsys.readouterr().err


def test_a_missing_declaration_is_a_fault(tmp_path):
    with pytest.raises(AlignmentError):
        load_declaration(str(tmp_path / "absent.json"))


def test_a_declaration_that_is_not_an_object_is_a_fault(tmp_path):
    path = tmp_path / "ucpa-declaration.json"
    path.write_text("[]", encoding="utf-8")
    with pytest.raises(AlignmentError):
        load_declaration(str(path))


# --- UCPA-L-01 ------------------------------------------------------------------------


def test_l01_refuses_a_primitive_the_register_does_not_declare(contract, repo):
    invented = Primitive(
        identifier="ONT-99",
        element="INVENTED-PRIMITIVE",
        standing=LAYER,
        layer_order=9,
        ratified_by="none",
        basis="test",
    )
    broken = contract.extended_with(invented)
    violations = _run("primitives_are_declared_by_the_register", broken, repo)
    assert any("ONT-99" in v for v in violations)


def test_l01_refuses_a_register_that_carries_the_id_but_not_the_element(contract, repo):
    renamed = dataclasses.replace(contract.primitives[1], element="NOT-THE-ELEMENT-NAME")
    broken = dataclasses.replace(
        contract, primitives=(contract.primitives[0], renamed, *contract.primitives[2:])
    )
    violations = _run("primitives_are_declared_by_the_register", broken, repo)
    assert any("element name" in v for v in violations)


def test_l01_fails_closed_when_the_canonical_owner_cannot_be_read(contract, tmp_path):
    violations = _run("primitives_are_declared_by_the_register", contract, str(tmp_path))
    assert any("cannot be read" in v for v in violations)


# --- UCPA-L-02 ------------------------------------------------------------------------


def test_l02_refuses_a_standing_the_ratification_record_contradicts(contract, repo):
    axiom = next(p for p in contract.primitives if p.is_axiom)
    promoted = dataclasses.replace(axiom, standing=LAYER, layer_order=0)
    broken = dataclasses.replace(
        contract, primitives=(promoted, *(p for p in contract.primitives if not p.is_axiom))
    )
    violations = _run("standing_matches_the_ratification_record", broken, repo)
    assert any("ratifies it as" in v for v in violations)


def test_l02_refuses_a_supersession_row_the_record_does_not_carry(contract, repo):
    absent = dataclasses.replace(contract.ratified_standing[0], supersession_id="SUP-NOT-A-ROW")
    broken = dataclasses.replace(contract, ratified_standing=(absent,))
    violations = _run("standing_matches_the_ratification_record", broken, repo)
    assert any("names this supersession" in v for v in violations)


def test_l02_refuses_a_row_whose_evidence_phrase_is_absent(contract, repo):
    wrong = dataclasses.replace(
        contract.ratified_standing[0], evidence_phrase="a phrase the record does not contain"
    )
    broken = dataclasses.replace(contract, ratified_standing=(wrong,))
    violations = _run("standing_matches_the_ratification_record", broken, repo)
    assert any("evidence phrase" in v for v in violations)


def test_l02_refuses_a_ratified_element_no_primitive_binds(contract, repo):
    unbound = dataclasses.replace(contract.ratified_standing[0], element="EXISTENCE")
    broken = dataclasses.replace(
        contract,
        ratified_standing=(unbound,),
        primitives=tuple(p for p in contract.primitives if p.element != "EXISTENCE"),
    )
    violations = _run("standing_matches_the_ratification_record", broken, repo)
    assert any("which no primitive binds" in v for v in violations)


def test_l02_fails_closed_when_the_ratification_record_cannot_be_read(contract, tmp_path):
    violations = _run("standing_matches_the_ratification_record", contract, str(tmp_path))
    assert any("cannot be read" in v for v in violations)


# --- UCPA-L-03 ------------------------------------------------------------------------


def test_l03_refuses_an_uncovered_facet(contract, repo):
    broken = dataclasses.replace(contract, reductions=contract.reductions[:-1])
    violations = _run("facet_reduction_covers_the_facet_model", broken, repo)
    assert any("no reduction covers it" in v for v in violations)


def test_l03_refuses_a_facet_the_model_does_not_declare(contract, repo):
    stray = Reduction(facet="not-a-facet", primitive=contract.primitives[1].identifier, basis="x")
    broken = dataclasses.replace(contract, reductions=(*contract.reductions, stray))
    violations = _run("facet_reduction_covers_the_facet_model", broken, repo)
    assert any("not a facet the facet model declares" in v for v in violations)


def test_l03_refuses_a_facet_reduced_twice(contract, repo):
    duplicate = contract.reductions[0]
    broken = dataclasses.replace(contract, reductions=(*contract.reductions, duplicate))
    violations = _run("facet_reduction_covers_the_facet_model", broken, repo)
    assert any("reduced more than once" in v for v in violations)


def test_l03_refuses_a_reduction_to_an_unbound_primitive(contract, repo):
    dangling = dataclasses.replace(contract.reductions[0], primitive="ONT-404")
    broken = dataclasses.replace(contract, reductions=(dangling, *contract.reductions[1:]))
    violations = _run("facet_reduction_covers_the_facet_model", broken, repo)
    assert any("which no primitive binds" in v for v in violations)


def test_l03_covers_the_live_facet_enumeration_exactly(contract):
    assert {r.facet for r in contract.reductions} == {f.value for f in Facet}


# --- UCPA-L-04 ------------------------------------------------------------------------


def test_l04_refuses_a_facet_anchored_to_the_axiom(contract, repo):
    axiom = next(p for p in contract.primitives if p.is_axiom)
    anchored = dataclasses.replace(contract.reductions[0], primitive=axiom.identifier)
    broken = dataclasses.replace(contract, reductions=(anchored, *contract.reductions[1:]))
    violations = _run("no_reduction_targets_the_axiom", broken, repo)
    assert any("is the axiom" in v for v in violations)


def test_l04_holds_because_exactly_one_primitive_is_the_axiom(contract):
    assert sum(1 for p in contract.primitives if p.is_axiom) == 1


# --- UCPA-L-05 ------------------------------------------------------------------------


def test_l05_refuses_a_projection_pointing_at_nothing(contract, repo):
    ghost = Projection(
        identifier="X", path="no/such/file.md", role="PROJECTION", superseded_by=None
    )
    broken = dataclasses.replace(contract, projections=(*contract.projections, ghost))
    violations = _run("projections_resolve_and_supersessions_are_real", broken, repo)
    assert any("cannot be read" in v for v in violations)


def test_l05_refuses_a_superseded_projection_naming_no_instrument(contract, repo):
    orphan = Projection(
        identifier="X",
        path=contract.source.canonical_owner,
        role=ROLE_SUPERSEDED,
        superseded_by=None,
    )
    broken = dataclasses.replace(contract, projections=(*contract.projections, orphan))
    violations = _run("projections_resolve_and_supersessions_are_real", broken, repo)
    assert any("names no superseding instrument" in v for v in violations)


def test_l05_refuses_a_superseding_instrument_that_does_not_exist(contract, repo):
    dangling = Projection(
        identifier="X",
        path=contract.source.canonical_owner,
        role=ROLE_SUPERSEDED,
        superseded_by="no/such/determination.md",
    )
    broken = dataclasses.replace(contract, projections=(*contract.projections, dangling))
    violations = _run("projections_resolve_and_supersessions_are_real", broken, repo)
    assert any("which cannot be read" in v for v in violations)


def test_l05_refuses_a_supersession_that_never_names_its_subject(contract, tmp_path):
    """A determination that does not name what it supersedes has superseded nothing."""
    (tmp_path / "subject.md").write_text("the artifact being superseded", encoding="utf-8")
    (tmp_path / "superseder.md").write_text("a determination naming nothing", encoding="utf-8")
    unnamed = Projection(
        identifier="X", path="subject.md", role=ROLE_SUPERSEDED, superseded_by="superseder.md"
    )
    broken = dataclasses.replace(contract, projections=(unnamed,))
    violations = _run("projections_resolve_and_supersessions_are_real", broken, str(tmp_path))
    assert any("does not name the artifact" in v for v in violations)


# --- UCPA-L-06 ------------------------------------------------------------------------


def test_l06_refuses_two_authorities(contract, repo):
    second = dataclasses.replace(contract.projections[1], role=ROLE_AUTHORITY)
    broken = dataclasses.replace(
        contract, projections=(contract.projections[0], second, *contract.projections[2:])
    )
    violations = _run("authority_is_single_and_matches_the_owner_binding", broken, repo)
    assert any("exactly one projection must hold role" in v for v in violations)


def test_l06_refuses_no_authority_at_all(contract, repo):
    demoted = tuple(
        dataclasses.replace(p, role="PROJECTION") if p.role == ROLE_AUTHORITY else p
        for p in contract.projections
    )
    broken = dataclasses.replace(contract, projections=demoted)
    violations = _run("authority_is_single_and_matches_the_owner_binding", broken, repo)
    assert any("exactly one projection must hold role" in v for v in violations)


def test_l06_refuses_an_authority_that_is_not_the_declared_owner(contract, repo):
    moved = tuple(
        dataclasses.replace(p, path=contract.source.ratification_record)
        if p.role == ROLE_AUTHORITY
        else p
        for p in contract.projections
    )
    broken = dataclasses.replace(contract, projections=moved)
    violations = _run("authority_is_single_and_matches_the_owner_binding", broken, repo)
    assert any("but the declared" in v for v in violations)


def test_l06_refuses_an_owner_the_binding_register_does_not_record(contract, repo):
    source = dataclasses.replace(contract.source, owner_binding_id="D-NOT-A-BINDING")
    broken = dataclasses.replace(contract, source=source)
    violations = _run("authority_is_single_and_matches_the_owner_binding", broken, repo)
    assert any("declares no canonical owner" in v for v in violations)


def test_l06_refuses_an_owner_the_binding_register_names_differently(contract, repo):
    """The drift this law exists to catch: the binding moved and the declaration did not."""
    source = dataclasses.replace(
        contract.source, canonical_owner=contract.source.ratification_record
    )
    broken = dataclasses.replace(contract, source=source)
    violations = _run("authority_is_single_and_matches_the_owner_binding", broken, repo)
    assert any("as canonical owner, not" in v for v in violations)


def test_l06_fails_closed_when_the_owner_binding_is_not_json(contract, tmp_path):
    binding = tmp_path / contract.source.owner_binding
    binding.parent.mkdir(parents=True, exist_ok=True)
    binding.write_text("not json at all", encoding="utf-8")
    violations = _run("authority_is_single_and_matches_the_owner_binding", contract, str(tmp_path))
    assert any("owner binding cannot be read" in v for v in violations)


def test_l06_fails_closed_when_the_owner_binding_cannot_be_read(contract, tmp_path):
    violations = _run("authority_is_single_and_matches_the_owner_binding", contract, str(tmp_path))
    assert any("owner binding cannot be read" in v for v in violations)


def test_l06_reads_the_owner_from_the_binding_file_rather_than_the_declaration(contract, repo):
    """The law must follow the binding register, not a copy of it."""
    binding = contract_module._read_json(repo, contract.source.owner_binding)
    owners = contract_module._owners_named_by(binding, contract.source.owner_binding_id)
    assert contract.source.canonical_owner in owners


# --- UCPA-L-07 ------------------------------------------------------------------------


def test_l07_holds_and_leaves_the_declared_binding_untouched(contract, repo):
    before = contract.primitives
    assert _run("the_primitive_set_admits_a_future_member", contract, repo) == ()
    assert contract.primitives == before


def test_l07_refuses_a_set_that_already_holds_the_probe(contract, repo):
    probe = Primitive(
        identifier=contract.openness.probe_id,
        element=contract.openness.probe_element,
        standing=LAYER,
        layer_order=99,
        ratified_by="x",
        basis="x",
    )
    broken = contract.extended_with(probe)
    violations = _run("the_primitive_set_admits_a_future_member", broken, repo)
    assert any("so it is closed" in v for v in violations)


def test_admission_is_an_append_that_alters_no_sibling(contract):
    probe = Primitive(
        identifier="ONT-FUTURE",
        element="FUTURE",
        standing=LAYER,
        layer_order=42,
        ratified_by="x",
        basis="x",
    )
    extended = contract.extended_with(probe)
    for original in contract.primitives:
        assert extended.primitive(original.identifier) == original


# --- UCPA-L-08 ------------------------------------------------------------------------


def test_l08_refuses_a_programme_reducing_to_an_unbound_primitive(contract, repo):
    broken = dataclasses.replace(
        contract,
        self_application=dataclasses.replace(contract.self_application, reduces_to="ONT-404"),
    )
    violations = _run("the_programme_reduces_to_a_declared_primitive", broken, repo)
    assert any("which no primitive binds" in v for v in violations)


def test_l08_refuses_a_programme_reducing_to_the_axiom(contract, repo):
    axiom = next(p for p in contract.primitives if p.is_axiom)
    broken = dataclasses.replace(
        contract,
        self_application=dataclasses.replace(
            contract.self_application, reduces_to=axiom.identifier
        ),
    )
    violations = _run("the_programme_reduces_to_a_declared_primitive", broken, repo)
    assert any("reduces to the axiom" in v for v in violations)


def test_l08_refuses_a_measure_that_is_not_a_declared_law(contract, repo):
    broken = dataclasses.replace(
        contract,
        self_application=dataclasses.replace(contract.self_application, measured_by="UCPA-L-99"),
    )
    violations = _run("the_programme_reduces_to_a_declared_primitive", broken, repo)
    assert any("not a declared law" in v for v in violations)


# --- the model refuses in both directions ---------------------------------------------


def test_every_declared_law_names_an_implemented_check(contract):
    assert contract.validate(frozenset(LAW_CHECKS)) == []


def test_a_law_naming_an_absent_check_is_refused(contract):
    problems = contract.validate(frozenset(LAW_CHECKS) - {contract.laws[0].check})
    assert any("which is not implemented" in p for p in problems)


def test_a_check_no_law_claims_is_refused(contract):
    problems = contract.validate(frozenset(LAW_CHECKS) | {"an_orphan_check"})
    assert any("no law claims it" in p for p in problems)


def test_a_duplicated_law_id_is_refused(contract):
    broken = dataclasses.replace(contract, laws=(*contract.laws, contract.laws[0]))
    assert any("declared more than once" in p for p in broken.validate(frozenset(LAW_CHECKS)))


def test_loading_a_contract_whose_checks_disagree_is_a_fault(tmp_path, document):
    document["laws"][0]["check"] = "a_check_that_does_not_exist"
    path = tmp_path / "ucpa-declaration.json"
    path.write_text(json.dumps(document), encoding="utf-8")
    with pytest.raises(AlignmentError, match="disagree"):
        load_contract(str(path))


# --- the model refuses an unusable declaration ----------------------------------------


@pytest.mark.parametrize(
    "section",
    [
        "ontology_source",
        "primitive_binding",
        "ratified_standing",
        "facet_reduction",
        "projections",
        "openness",
        "self_application",
        "laws",
    ],
)
def test_a_declaration_missing_a_section_is_refused(document, section):
    document.pop(section)
    with pytest.raises(AlignmentError):
        AlignmentContract.of(document)


def test_a_primitive_with_an_unknown_standing_is_refused(document):
    document["primitive_binding"][0]["standing"] = "SOMETHING-ELSE"
    with pytest.raises(AlignmentError, match="standing"):
        AlignmentContract.of(document)


def test_a_layer_without_an_order_is_refused(document):
    layer = next(p for p in document["primitive_binding"] if p["standing"] == LAYER)
    layer["layer_order"] = None
    with pytest.raises(AlignmentError, match="layer order"):
        AlignmentContract.of(document)


def test_an_axiom_carrying_a_layer_order_is_refused(document):
    axiom = next(p for p in document["primitive_binding"] if p["standing"] == AXIOM)
    axiom["layer_order"] = 0
    with pytest.raises(AlignmentError, match="not a layer"):
        AlignmentContract.of(document)


def test_a_reduction_without_a_basis_is_refused(document):
    document["facet_reduction"][0]["basis"] = "  "
    with pytest.raises(AlignmentError):
        AlignmentContract.of(document)


def test_a_law_without_a_check_is_refused(document):
    document["laws"][0].pop("check")
    with pytest.raises(AlignmentError):
        AlignmentContract.of(document)


def test_a_projection_with_a_non_string_supersession_is_refused(document):
    document["projections"][0]["superseded_by"] = 7
    with pytest.raises(AlignmentError, match="not a path"):
        AlignmentContract.of(document)


def test_an_unknown_probe_standing_is_refused(document):
    document["openness"]["probe_standing"] = "NEITHER"
    with pytest.raises(AlignmentError, match="probe standing"):
        AlignmentContract.of(document)


def test_a_ratified_standing_with_an_unknown_requirement_is_refused(document):
    document["ratified_standing"][0]["requires_standing"] = "NEITHER"
    with pytest.raises(AlignmentError, match="required standing"):
        AlignmentContract.of(document)


def test_an_empty_section_is_refused(document):
    document["laws"] = []
    with pytest.raises(AlignmentError):
        AlignmentContract.of(document)


# --- the gate itself -------------------------------------------------------------------


def test_the_gate_closes_when_a_law_refuses(tmp_path, document, capsys):
    document["facet_reduction"].pop()
    path = tmp_path / "ucpa-declaration.json"
    path.write_text(json.dumps(document), encoding="utf-8")
    assert main(["--declaration", str(path), "--quiet"]) == EXIT_CLOSED
    assert "FAIL" in capsys.readouterr().err


def _operative_strings(source_text: str) -> list[str]:
    """Return every string literal the code actually uses, excluding docstrings.

    Docstrings are documentation and are expected to cite the registers, primitives and
    paths this package reasons about — that is how the repository explains itself. What
    must never happen is an ontology fact reaching *executable* code, where it would
    become an answer the gate gives without measuring anything.
    """

    tree = ast.parse(source_text)
    docstrings: set[int] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Module | ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef):
            body = getattr(node, "body", [])
            if (
                body
                and isinstance(body[0], ast.Expr)
                and isinstance(body[0].value, ast.Constant)
                and isinstance(body[0].value.value, str)
            ):
                docstrings.add(id(body[0].value))
    return [
        node.value
        for node in ast.walk(tree)
        if isinstance(node, ast.Constant)
        and isinstance(node.value, str)
        and id(node) not in docstrings
    ]


def test_the_gate_holds_no_ontology_knowledge_in_its_executable_source():
    """No primitive name, facet name or ONT id may reach executable code.

    The declaration is data; the package is a measuring instrument. An instrument that
    already knows the answer is not measuring.
    """

    package = pathlib.Path(repo_root()) / "engine" / "root_ontology"
    forbidden = (
        "ONT-0",
        "ONT-1",
        "01-WORKING/",
        "00-CEP/",
        "02-MASTER/",
        "existence-context",
        "BEING",
        "EXISTENCE",
        "TRANSFORMATION",
    )
    for source in sorted(package.glob("*.py")):
        for literal in _operative_strings(source.read_text(encoding="utf-8")):
            for needle in forbidden:
                assert needle not in literal, f"{source.name} hard-codes {needle!r} in {literal!r}"


def test_the_extension_probe_is_never_persisted(contract):
    assert contract.primitive(contract.openness.probe_id) is None


# --- certification identity ------------------------------------------------------------------
#
# This package measured eight laws and returned a verdict attributable to NO state: nothing in
# it minted a digest, so two different declarations reaching two opposite verdicts produced
# reports that could not be told apart. UEC-000001 counted it under
# `declarations_without_a_certification_identity`, and closing that count exposed a second
# defect only the SUFFICIENT condition could see — the declaration stated a name, a version, an
# authority and a principle about itself and `AlignmentContract` parsed none of them, so
# rewriting the declared authority left the identity byte-identical at 6c09cf89….
#
# Both halves are asserted here: the identity must MOVE when the declaration's meaning moves,
# and must NOT move for anything declared inert.

import copy as _copy  # noqa: E402

from engine.root_ontology.declaration import DIGEST_EXCLUSIONS  # noqa: E402
from engine.root_ontology.declaration import parse as parse_declaration  # noqa: E402
from engine.uckp.canonical import content_hash  # noqa: E402
from engine.uckp.facets import Facet  # noqa: E402

IDENTITY_MUTATIONS = {
    "change the declared authority": lambda d: d.__setitem__("authority", "SOMETHING ELSE"),
    "change the declared version": lambda d: d.__setitem__("version", "9.9.9"),
    "change the declared name": lambda d: d.__setitem__("name", "Something Else"),
    "rewrite the declared principle": lambda d: d.__setitem__("principle", "something else"),
    "rewrite a law's statement": lambda d: d["laws"][0].__setitem__("statement", "something else"),
    "rebind a law to another check": lambda d: d["laws"][0].__setitem__("check", "other_check"),
    "retarget a facet reduction": lambda d: d["facet_reduction"][0].__setitem__(
        "primitive", "ONT-99"
    ),
    "change the canonical owner": lambda d: d["ontology_source"].__setitem__(
        "canonical_owner", "somewhere/else.md"
    ),
}


def _identity(document: dict) -> str:
    return content_hash(parse_declaration(document, source="test").digest_payload())


@pytest.mark.parametrize("name", sorted(IDENTITY_MUTATIONS))
def test_every_semantic_mutation_moves_the_certification_identity(
    document: dict, name: str
) -> None:
    """A value that can alter a verdict must be inside the identity that certifies it."""
    baseline = _identity(_copy.deepcopy(document))
    mutated = _copy.deepcopy(document)
    IDENTITY_MUTATIONS[name](mutated)
    assert _identity(mutated) != baseline, (
        f"{name!r} changed the declaration's meaning and left the certification identity at "
        f"{baseline[:16]}…. The same digest now certifies two different declarations."
    )


def test_the_identity_is_independent_of_the_path_it_was_read_from(document: dict) -> None:
    """A digest that changed with the reader would not be a digest of the declaration."""
    left = _identity(_copy.deepcopy(document))
    right = content_hash(
        parse_declaration(_copy.deepcopy(document), source="/elsewhere.json").digest_payload()
    )
    assert left == right


def test_the_identity_covers_every_parsed_field_except_the_declared_exclusions(
    contract: AlignmentContract,
) -> None:
    """Inclusion is the default; an omission must be a declared, reasoned exclusion."""
    payload = contract.digest_payload()
    parsed = {field.name for field in dataclasses.fields(contract)}
    missing = parsed - set(payload)
    assert missing <= set(DIGEST_EXCLUSIONS), (
        "fields silently absent from the certification identity: "
        f"{sorted(missing - set(DIGEST_EXCLUSIONS))}"
    )


def test_a_stale_exclusion_is_refused(contract: AlignmentContract) -> None:
    """The other direction. An exclusion matching no field may silently widen later."""
    assert set(DIGEST_EXCLUSIONS) <= {field.name for field in dataclasses.fields(contract)}


def test_the_gate_report_carries_the_certification_identity() -> None:
    """An identity that never reaches a report certifies nothing."""
    report = measure()
    assert len(report["declaration_digest"]) == 64
    assert report["declaration_version"]


def _arm_probe(contract):
    return Primitive(
        identifier=contract.openness.probe_id,
        element=contract.openness.probe_element,
        standing=LAYER,
        layer_order=len(contract.primitives) + 1,
        ratified_by=contract.artifact_id,
        basis="synthetic probe",
    )


class _AdmissionProxy:
    """A contract whose extended copy misbehaves in exactly one of the three measured ways."""

    def __init__(self, real, probe, *, drop: bool = False, alter: bool = False) -> None:
        self._real = real
        self._probe = probe
        self._drop = drop
        self._alter = alter

    def __getattr__(self, name):
        return getattr(self._real, name)

    def primitive(self, identifier):
        return self._real.primitive(identifier)

    def extended_with(self, probe):
        real, target, drop, alter = self._real, self._probe, self._drop, self._alter

        class _Extended:
            def primitive(self, identifier):
                if drop and identifier == target.identifier:
                    return None
                if alter and identifier == real.primitives[0].identifier:
                    return dataclasses.replace(real.primitives[0], element="REWRITTEN")
                if identifier == target.identifier:
                    return target
                return real.primitive(identifier)

        return _Extended()


def test_l07_refuses_an_admission_that_silently_drops_the_probe(contract, repo) -> None:
    probe = _arm_probe(contract)
    findings = _run(
        "the_primitive_set_admits_a_future_member",
        _AdmissionProxy(contract, probe, drop=True),
        repo,
    )
    assert any("absent from the extended binding" in line for line in findings), findings


def test_l07_refuses_an_admission_that_rewrites_an_existing_primitive(contract, repo) -> None:
    probe = _arm_probe(contract)
    findings = _run(
        "the_primitive_set_admits_a_future_member",
        _AdmissionProxy(contract, probe, alter=True),
        repo,
    )
    assert any("altered an existing primitive" in line for line in findings), findings


def test_l07_refuses_a_probe_already_present_in_the_declared_binding(contract, repo) -> None:
    probe = _arm_probe(contract)
    leaked = dataclasses.replace(contract, primitives=(*contract.primitives, probe))
    findings = _run(
        "the_primitive_set_admits_a_future_member", _AdmissionProxy(leaked, probe), repo
    )
    assert any("leaked into the declared binding" in line for line in findings), findings


def _load_declaration_file():
    from engine.root_ontology.declaration import load

    return load()


def _load_declaration_file():
    from engine.root_ontology.declaration import load

    return load()


def test_load_reads_the_committed_declaration_through_the_public_helper() -> None:
    """`load()` is the one-line entry the gate module calls; it must answer for the real tree."""
    loaded = _load_declaration_file()
    assert loaded.artifact_id == "UCPA-000001"
    assert loaded.principle
