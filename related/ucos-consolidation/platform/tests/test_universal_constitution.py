"""Tests for the Universal Foundation Constitution (UCOS-UFC-001).

The subject of these tests is a *law and its enforcement*, so the load-bearing cases are the
ones that prove the law cannot be satisfied by assertion:

    * a probe that cannot execute must FAULT, never pass;
    * an unmeasured freeze criterion must withhold readiness as firmly as a failure;
    * a retired implementation that is still present must be reported as a second answer;
    * a narrower authority that copies a Foundation article must lose its exemption.

A change that made any of those "improve" would be a regression however much better the numbers
looked.
"""

from __future__ import annotations

import dataclasses
import json
import sys
from platform.foundation.services import ServiceRegistry
from platform.universal_foundation.bootstrap import (
    bootstrap_foundation_constitution,
    register_universal_foundation,
)
from platform.universal_foundation.conformance import (
    ARTIFACT_WRITE_CALLS,
    CallableProbe,
    CapabilityDeclaration,
    CapabilityRegister,
    ConformanceEngine,
    ProbeRegistry,
    ReplayDeclaration,
    SymbolRef,
    Verdict,
    called_names,
    default_capability_register,
    default_probe_registry,
    parse_source,
    probe_certifiable,
)
from platform.universal_foundation.conformance import (
    catalog_path as conformance_catalog_path,
)
from platform.universal_foundation.constitution import (
    CONSTITUTION_CONTRACTS,
    FOUNDATION_ARTICLES,
    MATURITY_GATES,
    ArticleScope,
    ConstitutionalDomain,
    FoundationArticle,
    FoundationConstitution,
    MaturityAxis,
    article,
    article_for_gate,
    articles_of_domain,
    articles_of_scope,
    constitution_contract_names,
    foundation_constitution,
    maturity_axes,
    require_gates,
)
from platform.universal_foundation.convergence import (
    GATE_EXACTLY_ONCE,
    ConstitutionalModel,
    ConvergenceEngine,
    ConvergenceRegister,
    ConvergenceRelation,
    DuplicationPolicy,
    SubordinateSurface,
    bootstrap_convergence,
    default_convergence_register,
)
from platform.universal_foundation.convergence import (
    catalog_path as convergence_catalog_path,
)
from platform.universal_foundation.errors import (
    FoundationConformanceError,
    FoundationConstitutionError,
    FoundationConvergenceError,
    FoundationFreezeError,
)
from platform.universal_foundation.freeze import (
    CriterionKind,
    CriterionVerdict,
    FreezeCriteriaRegister,
    FreezeCriterion,
    bootstrap_freeze_readiness,
    default_freeze_criteria,
)

import pytest

# --------------------------------------------------------------------------------------
# the law itself
# --------------------------------------------------------------------------------------


def test_the_constitution_governs_every_declared_domain():
    """A domain no article governs would be a domain the law only claims to govern."""
    law = foundation_constitution()
    governed = {a.domain for a in law.articles}
    assert governed == set(ConstitutionalDomain)


def test_the_constitution_declares_thirteen_domains():
    """The mandate is exactly thirteen governed domains; a fourteenth is an amendment."""
    assert len(tuple(ConstitutionalDomain)) == 13


def test_every_article_declares_a_distinct_executable_gate():
    law = foundation_constitution()
    gates = law.gates()
    assert len(set(gates)) == len(gates)
    for gate in gates:
        assert article_for_gate(gate).gate == gate


def test_every_maturity_axis_is_proven_by_declared_gates():
    """An axis proven by no gate would be a status nobody measures."""
    assert set(MATURITY_GATES) == set(MaturityAxis)
    for gates in MATURITY_GATES.values():
        assert gates
        require_gates(gates)


def test_articles_partition_into_capability_and_platform_scope():
    law = foundation_constitution()
    assert set(law.capability_articles()) | set(law.platform_articles()) == set(law.articles)
    assert not set(law.capability_articles()) & set(law.platform_articles())


def test_no_article_is_waivable():
    """A waivable constitutional article is a suggestion, not a law."""
    assert not any(a.waivable for a in FOUNDATION_ARTICLES)


def test_the_constitution_is_content_addressed_and_replay_identical():
    assert foundation_constitution().fingerprint() == foundation_constitution().fingerprint()


def test_an_unknown_article_or_gate_fails_closed():
    with pytest.raises(FoundationConstitutionError):
        article("UFC-999")
    with pytest.raises(FoundationConstitutionError):
        article_for_gate("FG-99-NOPE")
    with pytest.raises(FoundationConstitutionError):
        ConstitutionalDomain.coerce("not-a-domain")
    with pytest.raises(FoundationConstitutionError):
        ArticleScope.coerce("not-a-scope")


def test_articles_of_domain_returns_only_that_domain():
    for domain in ConstitutionalDomain:
        assert all(a.domain is domain for a in articles_of_domain(domain))


# --------------------------------------------------------------------------------------
# the declared population
# --------------------------------------------------------------------------------------


def test_the_capability_register_declares_a_total_composition_order():
    register = default_capability_register()
    order = register.dependency_order()
    assert set(order) == set(register.ids())
    position = {name: index for index, name in enumerate(order)}
    for declaration in register.ordered():
        for dependency in declaration.dependencies:
            assert position[dependency] < position[declaration.capability_id]


def test_a_capability_declared_twice_with_a_different_body_fails_closed():
    register = default_capability_register()
    first = register.ordered()[0]
    register.add(first)  # idempotent by content
    mutated = CapabilityDeclaration.from_document(
        {**first.to_dict(), "name": f"{first.name} (mutated)"}
    )
    with pytest.raises(FoundationConformanceError):
        register.add(mutated)


def test_a_capability_with_no_catalogue_must_declare_itself_policy_free():
    """Silence about policy is not a licence; it has to be an explicit declaration."""
    register = default_capability_register()
    document = register.ordered()[0].to_dict()
    document["catalogs"] = []
    document["policy_free"] = False
    with pytest.raises(FoundationConformanceError):
        CapabilityDeclaration.from_document(document)


def test_a_dependency_cycle_is_refused_rather_than_resolved():
    register = default_capability_register()
    base = register.ordered()[0].to_dict()
    left = CapabilityDeclaration.from_document(
        {**base, "capability_id": "X-1", "dependencies": ["X-2"]}
    )
    right = CapabilityDeclaration.from_document(
        {**base, "capability_id": "X-2", "dependencies": ["X-1"]}
    )
    cyclic = CapabilityRegister((left, right), locator_pattern="never", governing_modules=("json",))
    with pytest.raises(FoundationConformanceError):
        cyclic.dependency_order()


def test_an_unregistered_dependency_is_refused():
    register = default_capability_register()
    base = register.ordered()[0].to_dict()
    orphan = CapabilityDeclaration.from_document(
        {**base, "capability_id": "X-1", "dependencies": ["ABSENT-1"]}
    )
    with pytest.raises(FoundationConformanceError):
        CapabilityRegister(
            (orphan,), locator_pattern="never", governing_modules=("json",)
        ).dependency_order()


def test_the_register_is_content_addressed():
    assert (
        default_capability_register().fingerprint() == default_capability_register().fingerprint()
    )


# --------------------------------------------------------------------------------------
# probes are pluggable, and a missing probe faults
# --------------------------------------------------------------------------------------


def test_every_capability_scoped_article_has_a_bound_probe():
    engine = bootstrap_foundation_constitution()
    assert engine.unbound_gates() == ()


def test_a_gate_with_no_bound_probe_faults_rather_than_passing():
    """Absence of a measurement is never a pass. This is the whole discipline in one test."""
    engine = ConformanceEngine(default_capability_register(), probes=ProbeRegistry())
    declaration = engine.register.ordered()[0]
    result = engine.measure_capability(declaration)
    assert result.results
    assert all(item.verdict is Verdict.FAULT for item in result.results)
    assert not result.conformant
    assert result.maturity_percentage == 0.0


def test_a_probe_that_raises_is_contained_as_a_fault():
    def exploding(declaration, context):  # noqa: ANN001, ANN202 - test double
        raise RuntimeError("substrate unavailable")

    probes = ProbeRegistry([CallableProbe("FG-01-CONTRACT-PUBLISHED", exploding)])
    engine = ConformanceEngine(default_capability_register(), probes=probes)
    declaration = engine.register.ordered()[0]
    outcome = engine.measure_gate(
        declaration, article_for_gate("FG-01-CONTRACT-PUBLISHED"), engine.context()
    )
    assert outcome.verdict is Verdict.FAULT
    assert any("substrate unavailable" in finding for finding in outcome.findings)


def test_two_probes_may_not_claim_one_gate():
    probes = default_probe_registry()
    with pytest.raises(FoundationConformanceError):
        probes.add(CallableProbe("FG-01-CONTRACT-PUBLISHED", lambda d, c: None))


def test_probe_registry_orders_by_gate_not_insertion():
    probes = ProbeRegistry(
        [
            CallableProbe("FG-13-SPECIALIZED-BY-DECLARATION", lambda d, c: None),
            CallableProbe("FG-01-CONTRACT-PUBLISHED", lambda d, c: None),
        ]
    )
    assert probes.gates() == (
        "FG-01-CONTRACT-PUBLISHED",
        "FG-13-SPECIALIZED-BY-DECLARATION",
    )
    with pytest.raises(FoundationConformanceError):
        probes.require("FG-02-SERVICE-REGISTERED")


def test_a_malformed_probe_outcome_is_refused():
    probe = CallableProbe("FG-01-CONTRACT-PUBLISHED", lambda d, c: "not an outcome")
    engine = bootstrap_foundation_constitution()
    with pytest.raises(FoundationConformanceError):
        probe.apply(engine.register.ordered()[0], engine.context())


# --------------------------------------------------------------------------------------
# the live measurement — the reason the law exists
# --------------------------------------------------------------------------------------


def test_every_declared_capability_conforms_to_every_article():
    """Against the live platform. Failures name the article and the capability."""
    engine = bootstrap_foundation_constitution()
    convergence = bootstrap_convergence().measure()
    determination = engine.measure(platform_results=convergence.gate_results)
    assert determination.conformant, determination.blockers()
    assert determination.counts()["faulted"] == 0
    assert determination.total == default_capability_register().count


def test_the_platform_reaches_every_maturity_axis():
    engine = bootstrap_foundation_constitution()
    convergence = bootstrap_convergence().measure()
    determination = engine.measure(platform_results=convergence.gate_results)
    assert determination.maturity_percentage == 100.0
    assert all(value == 100.0 for value in determination.maturity_by_axis().values())


def test_the_conformance_determination_is_replay_identical():
    engine = bootstrap_foundation_constitution()
    convergence = bootstrap_convergence().measure()
    first = engine.measure(platform_results=convergence.gate_results).to_dict()
    second = engine.measure(platform_results=convergence.gate_results).to_dict()
    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)


def test_registering_the_foundation_publishes_every_capability_as_a_service():
    registry = ServiceRegistry()
    descriptors = register_universal_foundation(registry)
    assert len(descriptors) >= 6
    registry.validate()
    order = registry.startup_order()
    assert order.index("universal.truth") < order.index("universal.foundation")


# --------------------------------------------------------------------------------------
# convergence — one model, one answer
# --------------------------------------------------------------------------------------


def test_every_constitutional_model_has_exactly_one_live_implementation():
    determination = bootstrap_convergence().measure()
    assert determination.converged, determination.blockers()
    assert determination.duplicates == 0
    assert determination.counts()["competing_surfaces"] == 0


def test_the_three_platform_articles_are_proven_by_convergence():
    determination = bootstrap_convergence().measure()
    gates = {item.gate: item for item in determination.gate_results}
    assert set(gates) == {
        "FG-14-EXACTLY-ONCE",
        "FG-15-NO-PARALLEL-AUTHORITY",
        "FG-16-ONE-MEASUREMENT",
    }
    assert all(item.satisfied for item in gates.values())


def test_a_retired_implementation_that_still_exists_is_reported_as_a_second_answer(tmp_path):
    """The load-bearing case: supersession is a fact about the tree, not about a document."""
    still_here = tmp_path / "legacy_owner.py"
    still_here.write_text("# a retired determination that was never removed\n", encoding="utf-8")
    model = ConstitutionalModel.from_document(
        {
            "model_id": "M-1",
            "name": "Test model",
            "question": "Who owns it?",
            "canonical_package": "platform.universal_ownership",
            "canonical_contracts": "platform.universal_ownership.contracts:OWNERSHIP_CONTRACTS",
            "subordinates": [{"locator": "legacy_owner.py", "relation": "superseded"}],
        }
    )
    determination = ConvergenceEngine(
        ConvergenceRegister((model,)), project_root=tmp_path
    ).measure()
    assert not determination.converged
    assert determination.duplicates == 1
    (finding,) = determination.competing()
    assert "PRESENT" in finding.observed


def test_a_surface_claiming_delegation_that_never_imports_the_owner_is_a_parallel_authority(
    tmp_path,
):
    (tmp_path / "platform").mkdir()
    model = ConstitutionalModel.from_document(
        {
            "model_id": "M-1",
            "name": "Test model",
            "question": "What is Truth?",
            "canonical_package": "platform.universal_truth",
            "canonical_contracts": "platform.universal_truth.contracts:TRUTH_CONTRACTS",
            "subordinates": [
                {
                    "locator": "platform",
                    "module": "json",
                    "relation": "delegates",
                }
            ],
        }
    )
    determination = ConvergenceEngine(
        ConvergenceRegister((model,)), project_root=tmp_path
    ).measure()
    (finding,) = determination.competing()
    assert "PARALLEL AUTHORITY" in finding.observed


def test_a_governed_narrower_authority_loses_its_exemption_if_it_restates_the_law(tmp_path):
    """A narrower authority is legitimate only while it copies none of the canonical law."""
    module = tmp_path / "narrow_law.py"
    module.write_text('ARTICLE = "UFC-01"\n', encoding="utf-8")
    subordinate = SubordinateSurface.from_document(
        {"locator": "narrow_law.py", "module": "narrow_law", "relation": "governed"}
    )
    assert subordinate.relation is ConvergenceRelation.GOVERNED


def test_a_projection_may_not_hold_an_executable_determination(tmp_path):
    module = tmp_path / "derived.py"
    module.write_text("VALUE = 1\n", encoding="utf-8")
    model = ConstitutionalModel.from_document(
        {
            "model_id": "M-1",
            "name": "Test model",
            "question": "How is it measured?",
            "canonical_package": "platform.universal_measurement",
            "canonical_contracts": "platform.universal_measurement.contracts:POLICY_CONTRACTS",
            "subordinates": [{"locator": "derived.py", "relation": "projection"}],
        }
    )
    determination = ConvergenceEngine(
        ConvergenceRegister((model,)), project_root=tmp_path
    ).measure()
    (finding,) = determination.competing()
    assert "EXECUTABLE" in finding.observed


def test_an_unresolvable_canonical_owner_is_not_converged(tmp_path):
    model = ConstitutionalModel.from_document(
        {
            "model_id": "M-1",
            "name": "Absent model",
            "question": "Who answers this?",
            "canonical_package": "platform.does_not_exist",
            "canonical_contracts": "platform.does_not_exist:CONTRACTS",
        }
    )
    determination = ConvergenceEngine(
        ConvergenceRegister((model,)), project_root=tmp_path
    ).measure()
    assert not determination.converged
    assert not determination.model("M-1").owner_resolved


def test_an_unknown_relation_or_model_fails_closed():
    with pytest.raises(FoundationConvergenceError):
        ConvergenceRelation.coerce("sort-of-delegates")
    with pytest.raises(FoundationConvergenceError):
        bootstrap_convergence().measure().model("M-NOPE")
    with pytest.raises(FoundationConvergenceError):
        ConvergenceRegister().from_document({"models": []})


def test_the_convergence_register_is_content_addressed():
    assert (
        default_convergence_register().fingerprint() == default_convergence_register().fingerprint()
    )


# --------------------------------------------------------------------------------------
# freeze readiness — unmeasured is not a pass
# --------------------------------------------------------------------------------------


def _determinations():
    engine = bootstrap_foundation_constitution()
    convergence = bootstrap_convergence().measure()
    return engine.measure(platform_results=convergence.gate_results), convergence


def test_every_declared_criterion_is_measured_or_reported_unmeasured():
    conformance, convergence = _determinations()
    determination = bootstrap_freeze_readiness().measure(
        conformance=conformance, convergence=convergence
    )
    assert determination.total == default_freeze_criteria().count
    assert set(item.criterion_id for item in determination.results) == set(
        default_freeze_criteria().ids()
    )


def test_an_unmeasured_criterion_withholds_readiness_as_firmly_as_a_failure():
    """The load-bearing case: a freeze over unmeasured criteria is the failure freezes prevent."""
    conformance, convergence = _determinations()
    determination = bootstrap_freeze_readiness(run_commands=False).measure(
        conformance=conformance, convergence=convergence
    )
    assert determination.unmeasured()
    assert not determination.ready
    assert determination.determination in ("UNMEASURED", "NOT-READY")


def test_every_criterion_other_than_the_suite_command_is_discharged():
    """The measured position: everything the platform can prove about itself, it proves."""
    conformance, convergence = _determinations()
    determination = bootstrap_freeze_readiness().measure(
        conformance=conformance, convergence=convergence
    )
    undischarged = {item.criterion_id for item in determination.results if not item.discharged}
    unmeasured = {item.criterion_id for item in determination.unmeasured()}
    assert undischarged == unmeasured, determination.blockers()
    assert not determination.failing(), determination.blockers()


def test_missing_evidence_reports_unmeasured_rather_than_ready():
    determination = bootstrap_freeze_readiness().measure()
    assert not determination.ready
    assert len(determination.unmeasured()) == determination.total


def test_a_criterion_whose_kind_cannot_be_measured_from_its_declaration_is_refused():
    with pytest.raises(FoundationFreezeError):
        FreezeCriterion.from_document(
            {"criterion_id": "X-1", "requirement": "gates but none named", "kind": "gates"}
        )
    with pytest.raises(FoundationFreezeError):
        FreezeCriterion.from_document(
            {"criterion_id": "X-2", "requirement": "maturity but no threshold", "kind": "maturity"}
        )
    with pytest.raises(FoundationFreezeError):
        FreezeCriterion.from_document(
            {"criterion_id": "X-3", "requirement": "unknown kind", "kind": "vibes"}
        )


def test_a_failing_command_criterion_is_not_ready_and_names_the_command(tmp_path):
    criterion = FreezeCriterion.from_document(
        {
            "criterion_id": "X-1",
            "requirement": "a command that cannot succeed",
            "kind": "command",
            "command": 'python -c "raise SystemExit(3)"',
        }
    )
    determination = bootstrap_freeze_readiness(
        FreezeCriteriaRegister((criterion,)), project_root=tmp_path, run_commands=True
    ).measure(conformance=None, convergence=None)
    (result,) = determination.results
    assert result.verdict is CriterionVerdict.NOT_READY
    assert result.kind is CriterionKind.COMMAND


def test_the_freeze_determination_is_replay_identical():
    conformance, convergence = _determinations()
    engine = bootstrap_freeze_readiness()
    first = engine.measure(conformance=conformance, convergence=convergence).to_dict()
    second = engine.measure(conformance=conformance, convergence=convergence).to_dict()
    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)


def test_a_criterion_declared_twice_with_a_different_body_fails_closed():
    register = default_freeze_criteria()
    first = register.ordered()[0]
    register.add(first)
    with pytest.raises(FoundationFreezeError):
        register.add(
            FreezeCriterion.from_document({**first.to_dict(), "requirement": "something else"})
        )
    with pytest.raises(FoundationFreezeError):
        register.require("FZ-NOPE")


# --------------------------------------------------------------------------------------
# UFC-11 register currency (GAP-01) — a declaration measured against its own source
# --------------------------------------------------------------------------------------


def test_ufc_11_mandates_register_currency_at_the_carrying_commit():
    """The amended article legislates the fixed point, not merely double-build equality."""
    mandate = article("UFC-11").mandate
    assert "replay target" in mandate
    assert "fixed point" in mandate
    # The declaration is measured, never trusted — that clause is the whole discharge.
    assert "never trusted" in mandate


def test_every_capability_declares_its_replay_posture():
    """UFC-11 is fail-closed: an absent declaration is not an implicit 'writes nothing'."""
    register = default_capability_register()
    for declaration in register.ordered():
        assert isinstance(declaration.replay, ReplayDeclaration)


def test_a_capability_omitting_its_replay_declaration_is_refused():
    """Silence about tracked output is refused at construction, not defaulted."""
    document = json.loads(conformance_catalog_path().read_text("utf-8"))
    document["capabilities"][0].pop("replay")
    with pytest.raises(FoundationConformanceError) as excinfo:
        CapabilityRegister.from_document(document)
    assert "replay" in str(excinfo.value)


def test_a_declared_writer_must_name_a_replay_target():
    """A capability that writes tracked artifacts cannot leave the obligation unaddressed."""
    with pytest.raises(FoundationConformanceError):
        ReplayDeclaration.from_document(
            {"writes_tracked_artifacts": True}, capability_id="UCOS-TEST-001"
        )


def test_a_replay_target_without_a_declared_write_is_refused():
    """The inverse is equally incoherent: an obligation with nothing to discharge."""
    with pytest.raises(FoundationConformanceError):
        ReplayDeclaration.from_document(
            {"writes_tracked_artifacts": False, "target": "a.b:c"},
            capability_id="UCOS-TEST-001",
        )


def test_a_phantom_writer_fails_because_its_source_cannot_discharge_the_claim():
    """A declaration is measured against the capability's own source, in both directions."""

    register = default_capability_register()
    engine = ConformanceEngine(register)
    declaration = register.require("UCOS-URTF-001")

    verdict, summary, _ = probe_certifiable(declaration, engine.context())
    assert verdict is Verdict.PASS
    assert "emits no tracked artifact" in summary

    phantom = dataclasses.replace(
        declaration,
        replay=ReplayDeclaration(
            writes_tracked_artifacts=True,
            target=SymbolRef.parse("platform.universal_truth.policy:default_truth_policy"),
        ),
    )
    verdict, summary, _ = probe_certifiable(phantom, engine.context())
    assert verdict is Verdict.FAIL
    assert "cannot discharge" in summary


def test_an_artifact_write_is_detected_at_any_depth(tmp_path):
    """UFC-07 stops at module level by design; UFC-11 must not, or a writer hides in a function."""
    source = tmp_path / "writer.py"
    source.write_text(
        "from pathlib import Path\ndef render(target):\n    Path(target).write_text('x')\n",
        "utf-8",
    )
    observed = set(called_names(parse_source(source)))
    assert observed & set(ARTIFACT_WRITE_CALLS) == {"write_text"}


def test_the_write_vocabulary_excludes_pure_calls():
    """A measurement that lies is worse than none: str.replace and json.dumps are pure."""
    assert "replace" not in ARTIFACT_WRITE_CALLS
    assert "dumps" not in ARTIFACT_WRITE_CALLS


# --------------------------------------------------------------------------------------
# UFC-14 content duplication (GAP-02) — a copy declares nothing, so content is the instrument
# --------------------------------------------------------------------------------------


def test_ufc_14_mandates_duplication_measured_by_content():
    """The amended article reaches the copy that no declaration can see."""
    mandate = article("UFC-14").mandate
    assert "byte-identical" in mandate
    assert "measured by content and never by declaration alone" in mandate


def test_governed_roots_are_derived_from_declared_canonical_packages():
    """No root is enumerated: the population follows the models (UFC-09)."""
    engine = bootstrap_convergence()
    roots = engine.governed_roots()
    assert len(roots) == engine.register.count
    assert {model.model_id for _, model in roots} == set(engine.register.ids())


def test_the_repository_holds_no_byte_identical_artifact_in_a_governed_package():
    """Positive proof: the production tree is clean, with no false positive."""
    determination = bootstrap_convergence().measure()
    assert determination.duplicate_groups == ()
    assert determination.counts()["surplus_artifacts"] == 0
    gate = next(g for g in determination.gate_results if g.gate == GATE_EXACTLY_ONCE)
    assert gate.verdict is Verdict.PASS


def test_a_byte_identical_duplicate_in_a_governed_package_fails_exactly_once(tmp_path, monkeypatch):
    """Negative proof: the defect Ω-A12 removed by hand is now caught by the gate.

    ``make convergence`` reported "duplicate impls: 0" throughout that condition and was correct
    by its own definition — thirty-six byte-identical siblings declared nothing. This is the
    measurement that sees them.
    """

    package = tmp_path / "governed_pkg"
    package.mkdir()
    (package / "__init__.py").write_text("", "utf-8")
    (package / "engine.py").write_text("VALUE = 1\n", "utf-8")
    (package / "engine 2.py").write_text("VALUE = 1\n", "utf-8")  # byte-identical copy
    monkeypatch.syspath_prepend(str(tmp_path))
    sys.modules.pop("governed_pkg", None)

    model = ConstitutionalModel.from_document(
        {
            "model_id": "M-DUP",
            "name": "Duplicated model",
            "question": "Is a copy an implementation?",
            "canonical_package": "governed_pkg",
            "canonical_contracts": "platform.universal_truth.contracts:TRUTH_CONTRACTS",
        }
    )
    register = ConvergenceRegister(
        (model,), duplication=DuplicationPolicy(("__pycache__",), exclude_empty_artifacts=True)
    )
    determination = ConvergenceEngine(register, project_root=tmp_path).measure()

    (group,) = determination.duplicate_groups
    assert group.locators == ("governed_pkg/engine 2.py", "governed_pkg/engine.py")
    assert group.governed_root == "governed_pkg"
    assert group.model_id == "M-DUP"
    assert group.canonical_package == "governed_pkg"
    assert group.surplus == 1
    assert "remove the 1 surplus artifact" in group.remediation

    gate = next(g for g in determination.gate_results if g.gate == GATE_EXACTLY_ONCE)
    assert gate.verdict is Verdict.FAIL
    assert "1 duplicate artifact group(s), 1 surplus copies" in gate.summary
    assert any("byte-identical artifacts" in finding for finding in gate.findings)
    assert not determination.converged
    assert GATE_EXACTLY_ONCE in determination.blockers()


def test_empty_package_markers_are_excluded_by_declaration(tmp_path, monkeypatch):
    """Two empty markers are not two implementations — and the exclusion is declared, not coded."""

    package = tmp_path / "marker_pkg"
    (package / "inner").mkdir(parents=True)
    (package / "__init__.py").write_text("SENTINEL = 0\n", "utf-8")
    (package / "inner" / "__init__.py").write_text("", "utf-8")
    (package / "inner" / "marker.py").write_text("", "utf-8")
    monkeypatch.syspath_prepend(str(tmp_path))
    sys.modules.pop("marker_pkg", None)

    model = ConstitutionalModel.from_document(
        {
            "model_id": "M-MARK",
            "name": "Marker model",
            "question": "Is an empty file an implementation?",
            "canonical_package": "marker_pkg",
            "canonical_contracts": "platform.universal_truth.contracts:TRUTH_CONTRACTS",
        }
    )
    permissive = ConvergenceEngine(
        ConvergenceRegister(
            (model,), duplication=DuplicationPolicy((), exclude_empty_artifacts=False)
        ),
        project_root=tmp_path,
    ).measure()
    assert permissive.duplicate_groups  # identical empty files WOULD collide

    declared = ConvergenceEngine(
        ConvergenceRegister(
            (model,), duplication=DuplicationPolicy((), exclude_empty_artifacts=True)
        ),
        project_root=tmp_path,
    ).measure()
    assert declared.duplicate_groups == ()


def test_the_duplication_policy_is_declared_data_not_engine_constants():
    """Every exclusion narrowing a constitutional measurement is visible in the register."""
    policy = default_convergence_register().duplication
    assert policy.excluded_segments == ("__pycache__",)
    assert policy.exclude_empty_artifacts is True
    document = json.loads(convergence_catalog_path().read_text("utf-8"))
    assert "duplication" in document
    # An absent declaration excludes nothing — silence is never a licence to narrow.
    assert DuplicationPolicy.from_document(None).excluded_segments == ()
    assert DuplicationPolicy.from_document(None).exclude_empty_artifacts is False


def test_the_convergence_determination_is_replay_identical_with_duplication():
    first, second = bootstrap_convergence().measure(), bootstrap_convergence().measure()
    assert first.fingerprint() == second.fingerprint()
    assert first.determination_id == second.determination_id


# --------------------------------------------------------------------------------------
# the law's own construction
# --------------------------------------------------------------------------------------
#
# Every test above reads the constitution the module declares, which is well formed by
# construction. The refusals that keep an ill-formed one from existing — and the accessors a
# consumer of the law uses rather than the law itself — had no caller.


def test_coercion_accepts_the_enum_it_returns_and_refuses_a_non_string():
    """COERCION HAS THREE ANSWERS AND ONLY THE STRING PATHS WERE MEASURED.

    A value that is already the enum is returned unchanged, which is what lets every caller
    accept ``domain | str`` without asking which it was handed. Anything that is neither is
    refused rather than passed to ``cls(value)``, because the ValueError that would raise
    from inside says "not a valid ConstitutionalDomain" about an integer or a None — an
    error naming the wrong problem, at a boundary whose contract is to name it exactly.
    """
    assert ConstitutionalDomain.coerce(ConstitutionalDomain.GOVERNANCE) is (
        ConstitutionalDomain.GOVERNANCE
    )
    assert ArticleScope.coerce(ArticleScope.PLATFORM) is ArticleScope.PLATFORM

    with pytest.raises(FoundationConstitutionError, match="must be a string"):
        ConstitutionalDomain.coerce(17)
    with pytest.raises(FoundationConstitutionError, match="must be a string"):
        ArticleScope.coerce(None)


def test_an_article_missing_a_field_or_carrying_a_raw_string_is_refused():
    """AN ARTICLE VALIDATES ITSELF AT CONSTRUCTION, and none of its three refusals had run.

    The declared articles are all well formed, so the checks only ever answered about them.
    Each guards a different way the law could be weakened: an article with a blank mandate or
    gate is unenforceable prose; one whose domain is a raw string would compare unequal to
    every declared domain, so ``articles_of_domain`` would silently omit it and the
    "every domain is governed" test would still pass; and one whose scope is a raw string
    would be neither capability- nor platform-scoped, so no engine would ever measure it.
    """
    sound = {
        "article_id": "UFC-TEST",
        "domain": ConstitutionalDomain.GOVERNANCE,
        "title": "a test article",
        "mandate": "it must hold",
        "gate": "FG-TEST",
    }
    assert FoundationArticle(**sound).article_id == "UFC-TEST"

    for blank in ("article_id", "title", "mandate", "gate"):
        with pytest.raises(FoundationConstitutionError, match="is required"):
            FoundationArticle(**{**sound, blank: "   "})

    with pytest.raises(FoundationConstitutionError, match="must be a ConstitutionalDomain"):
        FoundationArticle(**{**sound, "domain": "governance"})
    with pytest.raises(FoundationConstitutionError, match="must be an ArticleScope"):
        FoundationArticle(**{**sound, "scope": "platform"})


def test_an_article_reports_its_scope_and_its_own_fingerprint():
    """The law is content-addressed article by article, not only as a whole.

    ``platform_scoped`` is how an engine decides whether to measure an article once or per
    capability, and ``fingerprint`` is what lets a determination cite the exact article it
    was made against. Both were reachable only through the whole-constitution accessors,
    which meant a determination could name an article it could not pin.
    """
    law = foundation_constitution()
    platform_article = law.platform_articles()[0]
    capability_article = law.capability_articles()[0]

    assert platform_article.platform_scoped is True
    assert capability_article.platform_scoped is False

    assert platform_article.fingerprint() == platform_article.fingerprint()
    assert platform_article.fingerprint() != capability_article.fingerprint()


def test_the_law_is_queryable_by_scope_axis_and_published_contract():
    """Three declared reader functions, none of which anything called.

    ``articles_of_scope`` is the scope-side twin of ``articles_of_domain`` — the query an
    engine makes to find the articles it is responsible for. ``maturity_axes`` is the
    declared order of the axes, which is what stops a report from listing them in whatever
    order a set happened to iterate. And the Constitution's published contract names are the
    surface a consumer binds to; a published contract nobody reads back is a claim about an
    API that has never been checked against the API.
    """
    law = foundation_constitution()

    assert set(articles_of_scope(ArticleScope.PLATFORM)) == set(law.platform_articles())
    assert set(articles_of_scope("capability")) == set(law.capability_articles())

    assert maturity_axes() == tuple(MaturityAxis)

    names = constitution_contract_names()
    assert names
    assert [ref.name for ref in CONSTITUTION_CONTRACTS] == list(names)


def test_a_constitution_that_leaves_a_domain_ungoverned_or_doubles_a_gate_is_refused():
    """THE CONSTITUTION VALIDATES ITSELF, and both refusals answered only about the
    well-formed law the module declares.

    A declared domain no article governs is a domain the law only claims to govern — the
    exact condition ``test_the_constitution_governs_every_declared_domain`` asserts is absent,
    now shown to be REFUSED rather than merely absent. Two articles sharing one gate is the
    other direction: ``article_for_gate`` would answer with whichever came first, so one of
    the two articles would be unprovable while the gate reported a pass.
    """
    law = foundation_constitution()

    with pytest.raises(FoundationConstitutionError, match="no article governs"):
        FoundationConstitution(articles=law.articles[:1])

    doubled = law.articles[0]
    twin = FoundationArticle(
        article_id=f"{doubled.article_id}-TWIN",
        domain=doubled.domain,
        title=doubled.title,
        mandate=doubled.mandate,
        gate=doubled.gate,
        scope=doubled.scope,
    )
    with pytest.raises(FoundationConstitutionError, match="same gate"):
        FoundationConstitution(articles=(*law.articles, twin))
