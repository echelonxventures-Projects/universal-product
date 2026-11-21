"""UCOS-UFC-001 — Ω Nucleus completeness (UFC-17).

The measurement's whole point is the distinction between *absent* and *undeclared*: a facet a
nucleus declares inapplicable, with a reason, is honestly complete; a facet that resolves to
nothing at all is not. Only the first is a determination. So what is proven here is that each
of the three resolution kinds reaches the right one of three verdicts, and that every way a
facet can fail to resolve produces MISSING with a detail naming why — never a silent pass.

The second claim is compositional: gate-resolved facets read the verdict the Constitution
already reached rather than re-deriving it, so completeness can never report a facet proven
that conformance reports failed. That is checked by handing the engine a conformance
determination in which the gate failed, and requiring the facet to fail with it.
"""

from __future__ import annotations

import json
from platform.universal_foundation.conformance import (
    CapabilityConformance,
    CapabilityRegister,
    ConformanceDetermination,
    GateResult,
    Verdict,
    default_capability_register,
)
from platform.universal_foundation.constitution import foundation_constitution
from platform.universal_foundation.errors import FoundationNucleusError
from platform.universal_foundation.nucleus import (
    DEFAULT_NUCLEUS_FILENAME,
    GATE_NUCLEUS_COMPLETE,
    FacetResolution,
    FacetResult,
    FacetVerdict,
    NucleusCompleteness,
    NucleusCompletenessEngine,
    NucleusContract,
    NucleusDetermination,
    NucleusFacet,
    bootstrap_nucleus_completeness,
    catalog_path,
    default_nucleus_contract,
    load_nucleus_contract,
)

import pytest

#: A gate the Constitution declares, so a GATE facet can name it without inventing one.
DECLARED_GATE = "FG-09-EVOLUTION-ADDITIVE"


def facet(
    facet_id: str = "NF-01",
    *,
    resolution: FacetResolution = FacetResolution.DECLARATION,
    evidence: str = "identity",
    name: str = "Identity",
    rationale: str = "",
) -> NucleusFacet:
    return NucleusFacet(
        facet_id=facet_id,
        name=name,
        resolution=resolution,
        evidence=evidence,
        rationale=rationale,
    )


def contract(*facets: NucleusFacet, contract_id: str = "TEST-UNC-001") -> NucleusContract:
    return NucleusContract(
        contract_id,
        name="Test contract",
        version="1.0.0",
        profile_field="nucleus",
        facets=facets or (facet(),),
    )


def gate_result(gate: str = DECLARED_GATE, verdict: Verdict = Verdict.PASS) -> GateResult:
    return GateResult.create(gate, "UFC-09", "UCOS-UNG-001", verdict)


@pytest.fixture(scope="module")
def register() -> CapabilityRegister:
    return default_capability_register()


@pytest.fixture(scope="module")
def declaration(register):
    return register.require("UCOS-UNG-001")


def conformance_for(declaration, *results: GateResult) -> ConformanceDetermination:
    """A conformance determination carrying exactly the supplied gate results."""
    return ConformanceDetermination.create(
        foundation_constitution(),
        [CapabilityConformance.create(declaration, results)],
    )


# ---------------------------------------------------------------------------
# FacetResolution
# ---------------------------------------------------------------------------


def test_a_resolution_kind_is_returned_unchanged():
    assert FacetResolution.coerce(FacetResolution.GATE) is FacetResolution.GATE


def test_a_declared_resolution_string_resolves():
    assert FacetResolution.coerce("profile") is FacetResolution.PROFILE


def test_an_unknown_resolution_kind_is_refused_and_names_its_subject():
    with pytest.raises(FoundationNucleusError) as exc:
        FacetResolution.coerce("intuition", subject="NF-42")
    assert "NF-42" in str(exc.value)


def test_a_non_string_resolution_kind_is_refused():
    with pytest.raises(FoundationNucleusError):
        FacetResolution.coerce(3)


def test_only_a_missing_facet_leaves_a_nucleus_incomplete():
    assert FacetVerdict.RESOLVED.complete
    assert FacetVerdict.DECLARED_ABSENT.complete
    assert not FacetVerdict.MISSING.complete


# ---------------------------------------------------------------------------
# NucleusFacet
# ---------------------------------------------------------------------------


def test_a_facet_declaration_round_trips_through_its_projection():
    original = facet("NF-07", resolution=FacetResolution.GATE, evidence=DECLARED_GATE)
    assert NucleusFacet.from_document(original.to_dict()) == original


def test_a_facet_declaration_that_is_not_a_mapping_is_refused():
    with pytest.raises(FoundationNucleusError):
        NucleusFacet.from_document(["NF-01"])  # type: ignore[arg-type]


def test_a_facet_declaration_missing_a_required_key_names_what_is_missing():
    with pytest.raises(FoundationNucleusError) as exc:
        NucleusFacet.from_document({"facet_id": "NF-01", "name": "Identity"})
    message = str(exc.value)
    assert "resolution" in message and "evidence" in message


@pytest.mark.parametrize("blank", ("facet_id", "evidence"))
def test_a_facet_with_no_identity_or_no_evidence_reference_is_refused(blank):
    payload = {
        "facet_id": "NF-01",
        "name": "Identity",
        "resolution": "declaration",
        "evidence": "identity",
    }
    payload[blank] = "  "
    with pytest.raises(FoundationNucleusError):
        NucleusFacet.from_document(payload)


def test_a_facet_projection_carries_every_declared_field():
    payload = facet("NF-03", rationale="because").to_dict()
    assert payload == {
        "facet_id": "NF-03",
        "name": "Identity",
        "resolution": "declaration",
        "evidence": "identity",
        "rationale": "because",
    }


# ---------------------------------------------------------------------------
# NucleusContract
# ---------------------------------------------------------------------------


def test_a_contract_requires_an_identity():
    with pytest.raises(FoundationNucleusError):
        NucleusContract("   ", profile_field="nucleus")


def test_a_contract_requires_the_field_a_nucleus_states_its_profile_in():
    """Without it a PROFILE facet has nowhere to look, and would resolve to nothing silently."""
    with pytest.raises(FoundationNucleusError) as exc:
        NucleusContract("TEST-UNC-001", profile_field="  ")
    assert "TEST-UNC-001" in str(exc.value)


def test_a_contract_reports_what_it_was_declared_as():
    built = contract()
    assert built.contract_id == "TEST-UNC-001"
    assert built.name == "Test contract"
    assert built.version == "1.0.0"
    assert built.profile_field == "nucleus"
    assert built.count == 1


def test_only_a_nucleus_facet_may_be_registered():
    with pytest.raises(FoundationNucleusError):
        contract().add({"facet_id": "NF-02"})  # type: ignore[arg-type]


def test_declaring_the_same_facet_twice_identically_is_idempotent():
    built = contract(facet("NF-01"))
    built.add(facet("NF-01"))
    assert built.count == 1


def test_a_facet_redeclared_with_a_different_body_is_refused():
    built = contract(facet("NF-01", evidence="identity"))
    with pytest.raises(FoundationNucleusError) as exc:
        built.add(facet("NF-01", evidence="capability_id"))
    assert "NF-01" in str(exc.value)


def test_get_returns_a_declared_facet_and_reports_an_undeclared_one_as_absent():
    built = contract(facet("NF-01"))
    assert built.get("NF-01").facet_id == "NF-01"
    assert built.get("NF-99") is None


def test_require_returns_a_declared_facet():
    built = contract(facet("NF-01"))
    assert built.require("NF-01") is built.get("NF-01")


def test_require_refuses_an_undeclared_facet():
    with pytest.raises(FoundationNucleusError) as exc:
        contract().require("NF-99")
    assert "NF-99" in str(exc.value)


def test_facets_are_ordered_by_identity_never_by_insertion():
    built = contract(facet("NF-09"), facet("NF-01"))
    assert built.ids() == ("NF-01", "NF-09")
    assert [item.facet_id for item in built.ordered()] == ["NF-01", "NF-09"]


def test_the_contract_reports_every_gate_it_resolves_a_facet_through_once():
    built = contract(
        facet("NF-01"),
        facet("NF-02", resolution=FacetResolution.GATE, evidence=DECLARED_GATE),
        facet("NF-03", resolution=FacetResolution.GATE, evidence=DECLARED_GATE),
    )
    assert built.gates() == (DECLARED_GATE,)


def test_a_contract_document_round_trips_through_its_projection():
    original = contract(facet("NF-01"), facet("NF-02", evidence="capability_id"))
    rebuilt = NucleusContract.from_document(original.to_dict())
    assert rebuilt.to_dict() == original.to_dict()
    assert rebuilt.fingerprint() == original.fingerprint()


def test_a_contract_document_that_is_not_a_mapping_is_refused():
    with pytest.raises(FoundationNucleusError):
        NucleusContract.from_document([])  # type: ignore[arg-type]


@pytest.mark.parametrize("facets", ([], "NF-01", None))
def test_a_contract_document_declaring_no_facet_is_refused(facets):
    """An empty contract would declare every nucleus complete by requiring nothing."""
    with pytest.raises(FoundationNucleusError):
        NucleusContract.from_document({"contract_id": "X", "facets": facets})


# ---------------------------------------------------------------------------
# loading the declared contract
# ---------------------------------------------------------------------------


def test_the_packaged_catalogue_declares_the_facet_contract():
    built = default_nucleus_contract()
    assert catalog_path().name == DEFAULT_NUCLEUS_FILENAME
    assert built.count > 0
    assert built.profile_field
    # Every gate the contract resolves through is a gate the Constitution declares; the
    # engine's composition already refuses otherwise, so this states the invariant.
    declared = {gate for article in foundation_constitution().articles for gate in (article.gate,)}
    assert set(built.gates()) <= declared


def test_a_contract_loaded_from_a_document_matches_one_built_in_memory(tmp_path):
    path = tmp_path / "contract.json"
    original = contract(facet("NF-01"))
    path.write_text(json.dumps(original.to_dict()), encoding="utf-8")
    assert load_nucleus_contract(path).to_dict() == original.to_dict()


def test_an_absent_contract_document_is_a_refusal_naming_the_path(tmp_path):
    missing = tmp_path / "absent.json"
    with pytest.raises(FoundationNucleusError) as exc:
        load_nucleus_contract(missing)
    assert str(missing) in str(exc.value)


def test_a_malformed_contract_document_is_a_refusal(tmp_path):
    path = tmp_path / "contract.json"
    path.write_text("{ not json", encoding="utf-8")
    with pytest.raises(FoundationNucleusError):
        load_nucleus_contract(path)


# ---------------------------------------------------------------------------
# results and records
# ---------------------------------------------------------------------------


def test_a_facet_result_is_content_addressed_over_its_subject_and_verdict():
    first = FacetResult.create(facet(), FacetVerdict.RESOLVED, subject="A", detail="d")
    same = FacetResult.create(facet(), FacetVerdict.RESOLVED, subject="A", detail="d")
    other = FacetResult.create(facet(), FacetVerdict.RESOLVED, subject="B", detail="d")
    assert first.result_id == same.result_id != other.result_id
    assert first.result_id.startswith("UCOS-UNCF-")
    assert first.complete
    assert first.to_dict()["verdict"] == "RESOLVED"


def test_a_nucleus_with_no_facet_measured_reports_no_completeness(declaration):
    """Nothing measured is 0%, not 100%: an unasked question is not a satisfied one."""
    record = NucleusCompleteness.create(declaration, [])
    assert record.completeness_percentage == 0.0
    assert record.missing() == ()
    assert record.counts() == {"RESOLVED": 0, "DECLARED-ABSENT": 0, "MISSING": 0}


def test_a_completeness_record_counts_each_verdict_and_names_what_is_missing(declaration):
    record = NucleusCompleteness.create(
        declaration,
        [
            FacetResult.create(facet("NF-01"), FacetVerdict.RESOLVED, subject="A"),
            FacetResult.create(facet("NF-02"), FacetVerdict.DECLARED_ABSENT, subject="A"),
            FacetResult.create(facet("NF-03"), FacetVerdict.MISSING, subject="A"),
        ],
    )
    assert record.counts() == {"RESOLVED": 1, "DECLARED-ABSENT": 1, "MISSING": 1}
    assert not record.complete
    assert [item.facet_id for item in record.missing()] == ["NF-03"]
    assert record.completeness_percentage == pytest.approx(66.6667, abs=1e-3)
    assert record.to_dict()["complete"] is False


def test_a_determination_over_no_nucleus_is_not_complete():
    """An empty population cannot be a complete one — there is nothing to have measured."""
    determination = NucleusDetermination.create(contract(), [], [])
    assert determination.complete is False
    assert determination.completeness_percentage == 0.0
    assert determination.counts()["nuclei"] == 0


def test_a_determination_fingerprints_over_the_facts_it_asserts(declaration):
    record = NucleusCompleteness.create(
        declaration, [FacetResult.create(facet(), FacetVerdict.RESOLVED, subject="A")]
    )
    first = NucleusDetermination.create(contract(), [record], [gate_result()])
    second = NucleusDetermination.create(contract(), [record], [gate_result()])
    assert first.fingerprint() == second.fingerprint()
    assert first.determination_id == second.determination_id


# ---------------------------------------------------------------------------
# the engine's composition
# ---------------------------------------------------------------------------


def test_the_engine_requires_a_declared_contract(register):
    with pytest.raises(FoundationNucleusError):
        NucleusCompletenessEngine({"facets": []}, register)  # type: ignore[arg-type]


def test_the_engine_requires_the_capability_register(declaration):
    with pytest.raises(FoundationNucleusError):
        NucleusCompletenessEngine(contract(), [declaration])  # type: ignore[arg-type]


def test_a_facet_naming_a_gate_the_constitution_does_not_declare_fails_at_composition(register):
    """A facet cannot be proven by a gate no article owns."""
    with pytest.raises(Exception) as exc:
        NucleusCompletenessEngine(
            contract(facet("NF-01", resolution=FacetResolution.GATE, evidence="FG-99-INVENTED")),
            register,
        )
    assert "FG-99-INVENTED" in str(exc.value)


def test_the_engine_exposes_what_it_was_composed_from(register):
    built = contract()
    engine = NucleusCompletenessEngine(built, register)
    assert engine.contract is built
    assert engine.register is register
    assert engine.constitution.constitution_id == foundation_constitution().constitution_id
    assert engine.to_dict().keys() == {"contract", "register", "constitution"}
    assert engine.fingerprint() == NucleusCompletenessEngine(built, register).fingerprint()


# ---------------------------------------------------------------------------
# measuring one facet
# ---------------------------------------------------------------------------


def engine_for(*facets: NucleusFacet, register: CapabilityRegister) -> NucleusCompletenessEngine:
    return NucleusCompletenessEngine(contract(*facets), register)


def test_a_gate_facet_resolves_to_the_verdict_the_constitution_already_reached(
    register, declaration
):
    engine = engine_for(
        facet("NF-01", resolution=FacetResolution.GATE, evidence=DECLARED_GATE), register=register
    )
    result = engine.measure_facet(
        declaration,
        engine.contract.require("NF-01"),
        {DECLARED_GATE: gate_result(verdict=Verdict.PASS)},
    )
    assert result.verdict is FacetVerdict.RESOLVED
    assert DECLARED_GATE in result.detail


def test_a_gate_facet_cannot_report_proven_when_the_gate_failed(register, declaration):
    """Completeness reads the Constitution's verdict; it never reaches a second, weaker one."""
    engine = engine_for(
        facet("NF-01", resolution=FacetResolution.GATE, evidence=DECLARED_GATE), register=register
    )
    result = engine.measure_facet(
        declaration,
        engine.contract.require("NF-01"),
        {DECLARED_GATE: gate_result(verdict=Verdict.FAIL)},
    )
    assert result.verdict is FacetVerdict.MISSING
    assert "FAIL" in result.detail


def test_a_gate_facet_that_was_never_measured_is_missing_not_assumed(register, declaration):
    engine = engine_for(
        facet("NF-01", resolution=FacetResolution.GATE, evidence=DECLARED_GATE), register=register
    )
    result = engine.measure_facet(declaration, engine.contract.require("NF-01"), {})
    assert result.verdict is FacetVerdict.MISSING
    assert "was not measured" in result.detail


def test_a_declaration_facet_resolves_from_a_named_field(register, declaration):
    engine = engine_for(facet("NF-01", evidence="capability_id"), register=register)
    result = engine.measure_facet(declaration, engine.contract.require("NF-01"), {})
    assert result.verdict is FacetVerdict.RESOLVED
    assert "capability_id" in result.detail


def test_a_declaration_facet_that_leads_nowhere_is_missing(register, declaration):
    engine = engine_for(facet("NF-01", evidence="no.such.field"), register=register)
    result = engine.measure_facet(declaration, engine.contract.require("NF-01"), {})
    assert result.verdict is FacetVerdict.MISSING
    assert "absent or empty" in result.detail


def test_a_declaration_facet_that_is_declared_but_empty_is_missing(register, declaration):
    """A key somebody wrote and left empty is not a determination."""
    engine = engine_for(facet("NF-01", evidence="dependencies"), register=register)
    result = engine.measure_facet(declaration, engine.contract.require("NF-01"), {})
    empty = declaration.to_dict().get("dependencies") in (None, "", [], {})
    assert (result.verdict is FacetVerdict.MISSING) is empty


def test_a_profile_facet_resolves_to_the_evidence_the_nucleus_states(register, declaration):
    present = next(item for item in declaration.nucleus.entries if item.status.value == "present")
    engine = engine_for(
        facet("NF-01", resolution=FacetResolution.PROFILE, evidence=present.path),
        register=register,
    )
    result = engine.measure_facet(declaration, engine.contract.require("NF-01"), {})
    assert result.verdict is FacetVerdict.RESOLVED
    assert result.detail == present.detail


def test_a_profile_facet_declared_inapplicable_is_honestly_complete(register, declaration):
    absent = next(
        item for item in declaration.nucleus.entries if item.status.value == "not-applicable"
    )
    engine = engine_for(
        facet("NF-01", resolution=FacetResolution.PROFILE, evidence=absent.path),
        register=register,
    )
    result = engine.measure_facet(declaration, engine.contract.require("NF-01"), {})
    assert result.verdict is FacetVerdict.DECLARED_ABSENT
    assert result.complete
    assert result.detail == absent.detail


def test_a_profile_facet_the_nucleus_says_nothing_about_is_missing(register, declaration):
    """Undeclared is not the same fact as absent, and only absent is a determination."""
    engine = engine_for(
        facet("NF-01", resolution=FacetResolution.PROFILE, evidence="nothing.is.here"),
        register=register,
    )
    result = engine.measure_facet(declaration, engine.contract.require("NF-01"), {})
    assert result.verdict is FacetVerdict.MISSING
    assert "states nothing" in result.detail


# ---------------------------------------------------------------------------
# measuring the population
# ---------------------------------------------------------------------------


def test_measuring_requires_the_conformance_determination_gate_facets_read(register):
    with pytest.raises(FoundationNucleusError) as exc:
        engine_for(facet(), register=register).measure(conformance={"capabilities": []})
    assert "ConformanceDetermination" in str(exc.value)


def test_a_registered_nucleus_that_conformance_never_measured_is_a_refusal(register, declaration):
    """Measuring completeness against a population conformance skipped would report a guess."""
    engine = engine_for(facet(), register=register)
    empty = ConformanceDetermination.create(foundation_constitution(), [])
    with pytest.raises(FoundationNucleusError) as exc:
        engine.measure(conformance=empty)
    assert "was not measured for conformance" in str(exc.value)


def test_measuring_no_nucleus_at_all_faults_rather_than_passing_vacuously():
    """Zero nuclei is not zero findings — completeness cannot be asserted over nothing."""
    engine = NucleusCompletenessEngine(contract(), CapabilityRegister())
    determination = engine.measure(
        conformance=ConformanceDetermination.create(foundation_constitution(), [])
    )
    assert determination.complete is False
    assert determination.gate_results[0].gate == GATE_NUCLEUS_COMPLETE
    assert determination.gate_results[0].verdict is Verdict.FAULT
    assert "cannot be asserted" in determination.gate_results[0].summary


def test_a_missing_facet_fails_the_platform_gate_and_names_every_finding(register, declaration):
    one_nucleus = CapabilityRegister([declaration])
    engine = NucleusCompletenessEngine(
        contract(facet("NF-01", evidence="no.such.field", name="Nowhere")), one_nucleus
    )
    determination = engine.measure(conformance=conformance_for(declaration))
    gate = determination.gate_results[0]
    assert gate.verdict is Verdict.FAIL
    assert gate.findings
    assert "NF-01" in gate.findings[0] and "Nowhere" in gate.findings[0]
    assert determination.blockers() == (f"{declaration.capability_id}:NF-01",)
    assert determination.counts()["missing"] == 1
    assert determination.completeness_percentage == 0.0


def test_a_fully_resolved_population_passes_the_platform_gate(register, declaration):
    one_nucleus = CapabilityRegister([declaration])
    engine = NucleusCompletenessEngine(
        contract(facet("NF-01", evidence="capability_id")), one_nucleus
    )
    determination = engine.measure(conformance=conformance_for(declaration))
    gate = determination.gate_results[0]
    assert gate.verdict is Verdict.PASS
    assert gate.findings == ()
    assert determination.complete
    assert determination.completeness_percentage == 100.0
    assert determination.blockers() == ()


def test_the_full_projection_carries_the_per_facet_detail_the_summary_drops(register, declaration):
    engine = NucleusCompletenessEngine(
        contract(facet("NF-01", evidence="capability_id")), CapabilityRegister([declaration])
    )
    determination = engine.measure(conformance=conformance_for(declaration))
    full = determination.to_dict()
    compact = determination.summary()
    assert "results" in full["nuclei"][0]
    assert "results" not in compact["nuclei"][0]
    assert full["determination_id"] == compact["determination_id"]
    assert full["counts"] == compact["counts"]


def test_the_packaged_contract_finds_every_registered_nucleus_complete(register):
    """The repository's own reading, asserted as one rather than assumed."""
    from platform.universal_foundation.bootstrap import bootstrap_foundation_constitution

    conformance = bootstrap_foundation_constitution().measure()
    determination = bootstrap_nucleus_completeness().measure(conformance=conformance)
    assert determination.blockers() == ()
    assert determination.complete
    assert determination.counts()["nuclei"] == len(register.ordered())


# ---------------------------------------------------------------------------
# bootstrap
# ---------------------------------------------------------------------------


def test_bootstrapping_with_nothing_composes_the_packaged_declarations():
    engine = bootstrap_nucleus_completeness()
    assert engine.contract.to_dict() == default_nucleus_contract().to_dict()
    assert engine.register.to_dict() == default_capability_register().to_dict()


def test_bootstrapping_accepts_already_built_declarations(register):
    built = contract()
    engine = bootstrap_nucleus_completeness(built, register=register)
    assert engine.contract is built
    assert engine.register is register


def test_bootstrapping_accepts_paths_to_declared_documents(tmp_path):
    contract_path = tmp_path / "contract.json"
    contract_path.write_text(json.dumps(contract(facet("NF-01")).to_dict()), encoding="utf-8")
    register_path = tmp_path / "register.json"
    register_path.write_text(json.dumps(default_capability_register().to_dict()), encoding="utf-8")
    engine = bootstrap_nucleus_completeness(contract_path, register=register_path)
    assert engine.contract.ids() == ("NF-01",)
    assert engine.register.ordered()
