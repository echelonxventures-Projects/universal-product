"""The assembled universe, and the seventeen invariants measured against it.

The most important tests here are the ones that break something. A validator that only
ever sees a lawful universe has no evidence it can detect an unlawful one — that is the
UCCEP-F-001 defect inverted, a gate with no reachable FAIL state. So for each invariant
that can be driven to failure by a local mutation, there is a test that drives it there.
"""

from __future__ import annotations

import dataclasses

import pytest

from engine.uckp.errors import LawViolation, UCKPValidationError
from engine.uckp.identity import urn_for
from engine.uckp.law import ROOT_LAW
from engine.uckp.registry import UniversalKnowledgeRegistry
from engine.uckp.ucko import UCKO
from engine.uckp.universe import (
    DEFAULT_DISCOVERY_ROOTS,
    ConstitutionalUniverse,
    build_universe,
    universe_execution_request,
)
from engine.uckp.validation import (
    CERTIFIED,
    REFUSED,
    SATISFIED,
    UNMEASURED,
    VIOLATED,
    ConstitutionalValidator,
    InvariantResult,
    report_json,
    require_certified,
    validate_universe,
)
from engine.uckp.values import Relationship
from engine.uckp.vocabulary import build_vocabulary_registry

# --- the assembled universe -----------------------------------------------------


def test_the_universe_is_assembled_by_discovery_and_never_enumerated(universe):
    """Article 8: a builder holding a list of objects is a builder that must be edited."""
    assert universe.discovery.providers_found
    assert universe.discovery.objects_admitted == len(universe.objects())
    assert universe.discovery.failures == ()
    assert DEFAULT_DISCOVERY_ROOTS == ("engine.uckp",)


def test_the_universe_carries_every_layer(universe):
    assert universe.law is ROOT_LAW
    assert len(universe.projections.kinds()) == 10
    assert len(universe.persistence) == 10
    assert len(universe.execution) == 10
    assert universe.timeline.states()
    assert universe.evolution.records()
    assert universe.governance.decisions()
    assert universe.intelligence() is not None


def test_the_universe_has_exactly_one_self_grounding_root(universe):
    assert universe.root_id() == urn_for("ucos", "UCKP-LAW-0001")
    assert universe.registry.root_ids() == (universe.root_id(),)


def test_the_constitution_is_present_inside_the_universe_it_governs(universe):
    """Article 2 exempts nothing, including the law itself."""
    for local_name in ("UCKP-LAW-0001", "UCKP-ART-01", "UCKP-INV-01", "UCKP-STOP-01"):
        assert universe.registry.get(urn_for("ucos", local_name)) is not None
    assert len(universe.registry.by_category("principle")) == len(ROOT_LAW.articles)
    assert len(universe.registry.by_category("constraint")) == len(ROOT_LAW.invariants)


def test_every_facet_and_every_capability_has_a_canonical_object(universe):
    assert len(universe.registry.by_category("metadata")) == 33
    assert len(universe.registry.by_category("governance")) == len(ROOT_LAW.articles)
    assert len(universe.registry.by_category("transition")) == 15


def test_the_universe_is_frozen(universe):
    with pytest.raises(dataclasses.FrozenInstanceError):
        universe.law = None  # type: ignore[misc]


def test_the_seal_and_fingerprint_are_deterministic(universe):
    assert universe.seal() == universe.seal()
    assert universe.fingerprint() == universe.fingerprint()
    assert universe.knowledge_digest() == universe.knowledge_digest()


def test_the_graph_is_derived_once_and_reused(universe):
    assert universe.graph() is universe.graph()


def test_two_independent_builds_agree_on_the_knowledge_they_contain(tmp_path):
    """Determinism across processes is the whole basis of cross-era replay."""
    first = build_universe(persistence_base=tmp_path / "a")
    second = build_universe(persistence_base=tmp_path / "b")
    assert first.seal() == second.seal()
    assert first.knowledge_digest() == second.knowledge_digest()
    assert first.graph().fingerprint() == second.graph().fingerprint()


def test_the_universe_describes_and_documents_itself(universe):
    described = universe.describe()
    assert described["law_id"] == "UCKP-LAW-0001"
    assert described["counts"]["objects"] == len(universe.objects())
    document = universe.to_document()
    for key in (
        "law",
        "registry",
        "graph",
        "projections",
        "persistence",
        "execution",
        "timeline",
        "evolution",
        "intelligence",
        "governance",
    ):
        assert key in document


def test_require_coherent_refuses_a_universe_with_a_dangling_relationship(tmp_path):
    ghost = urn_for("test", "GHOST")
    registry = UniversalKnowledgeRegistry(vocabularies=build_vocabulary_registry())
    root_urn = urn_for("test", "ROOT")
    registry.register(
        UCKO.mint(
            namespace="test",
            local_name="ROOT",
            concept="root",
            definition="a test root pointing at nothing",
            kind="law",
            category="law",
            authority_tier="constitutional",
            derives_from=root_urn,
            owner="o",
            relationships=(Relationship("references", ghost, "knowledge"),),
        )
    )
    broken = dataclasses.replace(
        build_universe(persistence_base=tmp_path / "broken"), registry=registry, _graph=[]
    )
    with pytest.raises(LawViolation, match="point at objects that do not exist"):
        broken.require_coherent()


def test_additional_objects_enter_through_the_same_admission_rules(tmp_path, mint_object):
    """An assimilated object is not a second class of citizen."""
    extra = mint_object("EXTRA-OBJECT", derives_from=urn_for("ucos", "UCKP-LAW-0001"))
    assembled = build_universe(persistence_base=tmp_path / "extra", additional_objects=(extra,))
    assert assembled.registry.get(extra.ucko_id) is not None
    assert "engine.uckp.assimilation" in assembled.registry.providers()


def test_the_execution_request_helper_is_pure():
    assert universe_execution_request("describe", "urn:x").digest() == (
        universe_execution_request("describe", "urn:x").digest()
    )


# --- the validator: coverage ----------------------------------------------------


def test_every_declared_invariant_has_a_probe(universe):
    """A declaration with no probe is unmeasured, and unmeasured is not satisfied."""
    validator = ConstitutionalValidator(universe)
    assert validator.unprobed() == ()
    assert set(validator.probes()) == set(ROOT_LAW.invariant_ids())


def test_no_probe_measures_something_the_law_does_not_declare(universe):
    assert ConstitutionalValidator(universe).orphan_probes() == ()


# --- the validator: the lawful universe -----------------------------------------


def test_the_constitutional_universe_satisfies_all_seventeen_invariants(validated_universe):
    report = validated_universe
    assert report.verdict == CERTIFIED
    assert report.satisfied_count() == 17
    assert report.blocking_failures() == ()
    assert report.unmeasured() == ()
    require_certified(report)


def test_every_stop_condition_is_met_on_the_lawful_universe(validated_universe):
    report = validated_universe
    assert report.all_stop_conditions_met()
    assert len(report.stop_conditions()) == 13


@pytest.mark.parametrize("invariant_id", list(ROOT_LAW.invariant_ids()))
def test_each_invariant_reports_the_measurements_its_verdict_rests_on(
    validated_universe, invariant_id
):
    result = validated_universe.result(invariant_id)
    assert result.verdict == SATISFIED
    assert result.evidence, f"{invariant_id} reports a verdict with no measurements"
    assert result.statement == ROOT_LAW.invariant(invariant_id).statement


def test_the_report_is_deterministic_and_content_addressed(universe):
    left = validate_universe(universe)
    right = validate_universe(universe)
    assert left.digest() == right.digest()
    assert report_json(left) == report_json(right)


def test_the_report_serializes_and_summarizes(validated_universe):
    report = validated_universe
    record = report.to_dict()
    assert record["verdict"] == CERTIFIED
    assert record["counts"]["invariants"] == 17
    assert len(record["invariants"]) == 17
    summary = report.summary()
    assert "CERTIFIED" in summary
    assert "13/13" in summary


def test_asking_for_an_unknown_invariant_is_refused(validated_universe):
    with pytest.raises(UCKPValidationError):
        validated_universe.result("UCKP-INV-99")


# --- the validator: reachable failure -------------------------------------------


def _mutated_validator(universe, **changes) -> ConstitutionalValidator:
    return ConstitutionalValidator(dataclasses.replace(universe, **changes))


def test_an_unmeasured_invariant_fails_closed_rather_than_reporting_satisfied(universe):
    """The symmetric defect to a gate with no PASS path: a gate that never looked."""

    class Blinded(ConstitutionalValidator):
        def probes(self):
            return {key: value for key, value in super().probes().items() if key != "UCKP-INV-11"}

    validator = Blinded(universe)
    assert validator.unprobed() == ("UCKP-INV-11",)
    report = validator.validate()
    result = report.result("UCKP-INV-11")
    assert result.verdict == UNMEASURED
    assert result.blocks
    assert report.verdict == REFUSED
    with pytest.raises(UCKPValidationError):
        require_certified(report)


def test_a_probe_that_cannot_conclude_is_a_violation_not_a_pass(universe):
    class Exploding(ConstitutionalValidator):
        def probes(self):
            def boom():
                raise RuntimeError("the measurement apparatus broke")

            return {**super().probes(), "UCKP-INV-01": boom}

    report = Exploding(universe).validate()
    result = report.result("UCKP-INV-01")
    assert result.verdict == VIOLATED
    assert "could not conclude" in result.findings[0]
    assert report.verdict == REFUSED


def test_inv_03_detects_a_reimplementation_of_the_canonical_primitive(universe, tmp_path):
    """The probe that reaches outside the universe, at the tree that contains one."""
    package = tmp_path / "engine"
    package.mkdir()
    (package / "rogue.py").write_text(
        "import hashlib\n"
        "import json\n"
        "def content_hash(payload):\n"
        "    return hashlib.sha256(json.dumps(payload).encode()).hexdigest()\n",
        encoding="utf-8",
    )
    validator = ConstitutionalValidator(universe, source_root=tmp_path)
    result = validator.validate_invariant("UCKP-INV-03")
    assert result.verdict == VIOLATED
    assert any("rogue.py" in finding for finding in result.findings)


def test_inv_03_does_not_flag_a_module_that_forwards_to_layer_zero(universe, tmp_path):
    """A re-export is the remedy, so flagging it would make the invariant unsatisfiable."""
    package = tmp_path / "engine"
    package.mkdir()
    (package / "forwarder.py").write_text(
        "from engine.uckp.canonical import content_hash as _ch\n"
        "def content_hash(payload):\n"
        "    return _ch(payload)\n",
        encoding="utf-8",
    )
    result = ConstitutionalValidator(universe, source_root=tmp_path).validate_invariant(
        "UCKP-INV-03"
    )
    assert result.verdict == SATISFIED


def test_inv_03_fails_closed_when_no_source_can_be_read(universe, tmp_path):
    """Absence of a measurement is never evidence of compliance."""
    result = ConstitutionalValidator(universe, source_root=tmp_path).validate_invariant(
        "UCKP-INV-03"
    )
    assert result.verdict == VIOLATED
    assert any("unmeasured" in finding for finding in result.findings)


def test_the_repository_source_tree_currently_defines_the_primitive_exactly_once(
    universe, repo_root
):
    result = ConstitutionalValidator(universe, source_root=repo_root).validate_invariant(
        "UCKP-INV-03"
    )
    assert result.verdict == SATISFIED
    assert dict(result.evidence)["primitive_redefinitions"] == "0"
    assert int(dict(result.evidence)["source_files_scanned"]) > 500


def test_inv_09_and_inv_11_fail_when_only_one_technology_exists(universe):
    single_execution = _mutated_validator(universe, execution=universe.execution[:1])
    assert single_execution.validate_invariant("UCKP-INV-09").verdict == VIOLATED
    single_persistence = _mutated_validator(universe, persistence=universe.persistence[:1])
    assert single_persistence.validate_invariant("UCKP-INV-11").verdict == VIOLATED


def test_inv_12_fails_when_an_object_binds_exactly_one_runtime(universe, tmp_path, mint_object):
    locked = mint_object(
        "RUNTIME-LOCKED",
        derives_from=urn_for("ucos", "UCKP-LAW-0001"),
        runtime_bindings=(
            __import__("engine.uckp.values", fromlist=["RuntimeBinding"]).RuntimeBinding(
                "python", "resolve", "a"
            ),
        ),
    )
    assembled = build_universe(persistence_base=tmp_path / "locked", additional_objects=(locked,))
    result = ConstitutionalValidator(assembled).validate_invariant("UCKP-INV-12")
    assert result.verdict == VIOLATED
    assert any("exactly one runtime" in finding for finding in result.findings)


def test_inv_13_fails_when_the_ledger_reports_itself_terminated(universe):
    class Terminated:
        def __getattr__(self, name):
            return getattr(universe.evolution, name)

        def is_terminated(self):
            return True

    result = _mutated_validator(universe, evolution=Terminated()).validate_invariant("UCKP-INV-13")
    assert result.verdict == VIOLATED


def test_inv_15_fails_when_the_timeline_is_empty(universe):
    from engine.uckp.state import ConstitutionalTimeline

    result = _mutated_validator(universe, timeline=ConstitutionalTimeline()).validate_invariant(
        "UCKP-INV-15"
    )
    assert result.verdict == VIOLATED
    assert any("timeline is empty" in finding for finding in result.findings)


def test_inv_16_fails_when_discovery_found_no_provider(universe):
    from engine.uckp.registry import DiscoveryReport

    blind = DiscoveryReport(
        roots=("engine.uckp",),
        modules_scanned=0,
        providers_found=(),
        objects_admitted=0,
        failures=("import exploded",),
    )
    result = _mutated_validator(universe, discovery=blind).validate_invariant("UCKP-INV-16")
    assert result.verdict == VIOLATED
    assert any("enumerated by hand" in finding for finding in result.findings)


def test_inv_08_fails_when_an_object_binds_an_unimplemented_projection_kind(
    universe, tmp_path, mint_object
):
    from engine.uckp.values import ProjectionBinding

    bogus = mint_object(
        "PROJECTION-GHOST",
        derives_from=urn_for("ucos", "UCKP-LAW-0001"),
        projection_bindings=(ProjectionBinding("holo-deck", "t", True, False),),
    )
    assembled = build_universe(persistence_base=tmp_path / "ghost", additional_objects=(bogus,))
    result = ConstitutionalValidator(assembled).validate_invariant("UCKP-INV-08")
    assert result.verdict == VIOLATED
    assert any("no projection implements" in finding for finding in result.findings)


def test_an_invariant_result_refuses_a_verdict_outside_the_closed_set():
    with pytest.raises(UCKPValidationError, match="not machine-checkable"):
        InvariantResult(
            invariant_id="UCKP-INV-01",
            name="n",
            statement="s",
            blocking=True,
            verdict="probably-fine",
        )


def test_a_stop_condition_is_unmet_when_an_invariant_it_names_is_unmet(universe):
    class Blinded(ConstitutionalValidator):
        def probes(self):
            return {key: value for key, value in super().probes().items() if key != "UCKP-INV-11"}

    report = Blinded(universe).validate()
    unmet = [item for item in report.stop_conditions() if not item["met"]]
    assert unmet
    assert any("UCKP-INV-11" in item["unmet_invariants"] for item in unmet)
    assert not report.all_stop_conditions_met()


def test_validate_invariant_accepts_an_id_or_a_declaration(universe):
    validator = ConstitutionalValidator(universe)
    by_id = validator.validate_invariant("UCKP-INV-01")
    by_value = validator.validate_invariant(ROOT_LAW.invariant("UCKP-INV-01"))
    assert by_id.to_dict() == by_value.to_dict()


def test_the_universe_type_is_what_the_validator_expects(universe):
    assert isinstance(universe, ConstitutionalUniverse)


# --- the universe: coherence refusals and the default persistence root ------------


def test_require_coherent_refuses_a_universe_holding_an_object_the_root_cannot_reach(
    universe,
):
    """Article 5 at assembly time.

    Reached with a double: the single-root, dangling-edge and acyclicity checks in front
    of this one make an orphan unconstructible from real objects — an object that reaches
    no root *is* a second root, and is refused earlier. The guard still needs a test,
    because a refusal that has never fired is a comment.
    """
    from engine.tests.uckp.doubles import Proxy

    stray = urn_for("test", "UNREACHABLE")
    orphaned = dataclasses.replace(
        universe, _graph=[Proxy(universe.graph(), orphans=lambda root_id: (stray,))]
    )
    with pytest.raises(LawViolation, match="unreachable from the root law"):
        orphaned.require_coherent()


def test_a_universe_built_without_a_persistence_root_provides_its_own():
    """No caller should have to know where the mechanisms keep their copies."""
    from pathlib import Path

    assembled = build_universe()
    base = Path(assembled.persistence_base)
    assert base.is_dir()
    assert base.name.startswith("uckp-universe-")
    assert len(assembled.persistence) == 10


def test_the_coherence_guard_can_be_stood_down_to_study_an_incoherent_universe(tmp_path):
    """The guard is a parameter, not a hardcoded assumption: the validator needs both."""
    assembled = build_universe(persistence_base=tmp_path / "ungated", require_coherent=False)
    assembled.require_coherent()
    assert validate_universe(assembled).verdict == CERTIFIED
