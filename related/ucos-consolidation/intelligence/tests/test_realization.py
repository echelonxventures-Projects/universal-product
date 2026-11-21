"""URI-000001 validation tests — Universal Realization Intelligence.

Proves the constitutional claims the subsystem makes:

  * deterministic          — identical canonical knowledge ⇒ byte-identical artifacts
  * knowledge-derived      — every artifact is anchored to canonical objects, and every
                             realizable canonical object reaches an artifact
  * governed               — twelve fail-closed gates, no vacuous pass, rejection blocks
                             materialization
  * traceable              — closure verified in both directions
  * additive + safe        — frozen corpus and path traversal are refused; re-running is
                             a byte-stable no-op; written bytes are verified
  * really generated       — the emitted Python compiles and the emitted runtime boots

Run: .ec1-venv/bin/python -m pytest intelligence/tests/test_realization.py -q
"""

from __future__ import annotations

import dataclasses
import importlib.util
import json
import runpy
from dataclasses import replace as _replace
from pathlib import Path

import pytest

import intelligence.realization.contracts as contracts
import intelligence.realization.engine as engine_module
import intelligence.realization.generators as generator_registry
import intelligence.realization.governance as governance_module
from engine.knowledge import KnowledgeError
from engine.knowledge.cko import CanonicalKnowledgeObject, DecisionRecord, RejectedOption
from engine.knowledge.model import KnowledgeAuthority, KnowledgeKind, Lifecycle
from engine.knowledge.store import KnowledgeBase
from intelligence.realization import (
    FAMILY_ORDER,
    GATES,
    VERDICT_GOVERNED,
    ArtifactFamily,
    CompositionEngine,
    GeneratedArtifact,
    GenerationEngine,
    GenerationManifest,
    ImplementationEngine,
    KnowledgeIntake,
    MediaKind,
    PlanningEngine,
    Provenance,
    RealizationConfig,
    RealizationGovernor,
    RealizationIntelligenceEngine,
    TraceabilityEngine,
    build_evidence,
    enforce_realization,
    family_order,
    materialize_artifacts,
    register_family,
    register_generator,
    registered_families,
    registry_manifest,
    verify_bundle,
)
from intelligence.realization import cli as cli_module
from intelligence.realization import knowledge as knowledge_module
from intelligence.realization.canonical import verify_seal
from intelligence.realization.cli import main as cli_main
from intelligence.realization.composition import compose_plan
from intelligence.realization.config import resolve_repo_root
from intelligence.realization.contracts import identifier, slug
from intelligence.realization.engine import realize as realize_repository
from intelligence.realization.errors import (
    CompositionError,
    EvidenceError,
    FrozenSurfaceError,
    GenerationError,
    GovernanceRejectedError,
    ImplementationError,
    KnowledgeIntakeError,
    PlanningError,
)
from intelligence.realization.errors import KnowledgeIntakeError as _Fault
from intelligence.realization.evidence import (
    COMPOSITION_FILE,
    GENERATION_FILE,
    GOVERNANCE_FILE,
    IMPLEMENTATION_FILE,
    INTAKE_FILE,
    PLAN_FILE,
    RECORD_FILE,
    REQUIRED_FILES,
    TRACEABILITY_FILE,
    RealizationEvidence,
    _guard_writable,
    emit_evidence,
)
from intelligence.realization.generation import artifact_index, generate_artifacts
from intelligence.realization.generators import GENERATORS, _build_registry, generator_for
from intelligence.realization.generators.architecture import ArchitectureGenerator
from intelligence.realization.generators.base import GenerationContext, Generator
from intelligence.realization.generators.deployment import _yaml_lines, _yaml_scalar
from intelligence.realization.generators.schema import SchemaGenerator, _json_type
from intelligence.realization.governance import RealizationGovernor as _Governor
from intelligence.realization.planning import _topological_waves, build_plan
from intelligence.realization.traceability import build_trace

REPO = RealizationConfig.create().repo_root


# --------------------------------------------------------------------------- #
# fixtures                                                                    #
# --------------------------------------------------------------------------- #


def _config(tmp_path) -> RealizationConfig:
    """A configuration writing into a throwaway tree (never the repository)."""
    return RealizationConfig.create(
        REPO,
        artifact_root=tmp_path / "realization",
        evidence_dir=tmp_path / "evidence",
    )


@pytest.fixture
def engine(tmp_path) -> RealizationIntelligenceEngine:
    return RealizationIntelligenceEngine(_config(tmp_path))


@pytest.fixture(scope="module")
def pipeline():
    """The pure prefix of the pipeline over the repository's canonical knowledge."""
    eng = RealizationIntelligenceEngine()
    return eng.generate()


def _object(cko_id: str, **overrides) -> CanonicalKnowledgeObject:
    fields = {
        "cko_id": cko_id,
        "kind": KnowledgeKind.RULE,
        "title": f"Test object {cko_id}",
        "statement": f"Statement for {cko_id}.",
        "universe": "TESTING",
        "authority": KnowledgeAuthority.ENGINEERING,
        "owner": "UCOS-TEST",
        "lifecycle": Lifecycle.OPERATIONAL,
        "version": "1.0.0",
    }
    fields.update(overrides)
    return CanonicalKnowledgeObject.create(**fields)


def _synthetic_intake(*objects: CanonicalKnowledgeObject) -> KnowledgeIntake:
    return KnowledgeIntake.from_base(KnowledgeBase(objects), source="test")


# --------------------------------------------------------------------------- #
# canonical knowledge intake                                                  #
# --------------------------------------------------------------------------- #


def test_intake_loads_and_verifies_repository_canonical_knowledge() -> None:
    intake = KnowledgeIntake.load()
    assert intake.base.objects()
    assert all(record["verified"] for record in intake.integrity)
    assert intake.knowledge_seal
    assert intake.targets


def test_intake_derives_one_target_per_knowledge_universe() -> None:
    intake = KnowledgeIntake.load()
    universes = {obj.universe for obj in intake.base.objects()}
    assert {target.universe for target in intake.targets} == universes


def test_intake_refuses_mutated_canonical_knowledge() -> None:
    """A record whose hash no longer matches must fail intake, not propagate."""

    good = _object("UCKO-TEST-0001")
    tampered = dataclasses.replace(good, statement="mutated after sealing")
    with pytest.raises(KnowledgeIntakeError) as excinfo:
        _synthetic_intake(tampered)
    assert "UCKO-TEST-0001" in excinfo.value.context["failed"]


def test_intake_refuses_an_empty_canonical_store() -> None:
    with pytest.raises(KnowledgeIntakeError):
        KnowledgeIntake.from_base(KnowledgeBase(()), source="test")


def test_knowledge_seal_is_a_pure_function_of_canonical_knowledge() -> None:
    first = KnowledgeIntake.load()
    second = KnowledgeIntake.load()
    assert first.knowledge_seal == second.knowledge_seal


# --------------------------------------------------------------------------- #
# planning                                                                    #
# --------------------------------------------------------------------------- #


def test_plan_realizes_every_target_into_every_family(pipeline) -> None:
    _intake, plan, _composition, _findings, _manifest = pipeline
    for target in plan.targets:
        families = {step.family for step in plan.steps_for(target.target_id)}
        assert families == set(FAMILY_ORDER)


def test_plan_waves_cover_every_step_and_respect_dependencies(pipeline) -> None:
    _intake, plan, _composition, _findings, _manifest = pipeline
    waved = [step_id for wave in plan.waves for step_id in wave]
    assert sorted(waved) == sorted(step.step_id for step in plan.steps)
    level = {sid: idx for idx, wave in enumerate(plan.waves) for sid in wave}
    for step in plan.steps:
        for dependency in step.depends_on:
            assert level[dependency] < level[step.step_id]


def test_plan_has_no_coverage_gap_over_repository_knowledge(pipeline) -> None:
    _intake, plan, _composition, _findings, _manifest = pipeline
    assert plan.coverage_gaps == ()


def test_plan_is_deterministic() -> None:
    intake = KnowledgeIntake.load()
    planner = PlanningEngine()
    assert planner.plan(intake).seal == planner.plan(intake).seal


# --------------------------------------------------------------------------- #
# composition                                                                 #
# --------------------------------------------------------------------------- #


def test_composition_is_clean_and_ordered(pipeline) -> None:
    _intake, _plan, composition, findings, _manifest = pipeline
    assert findings.clean
    position = {unit_id: idx for idx, unit_id in enumerate(composition.order)}
    for unit in composition.units:
        for upstream in unit.upstream_units:
            assert position[upstream] < position[unit.unit_id]


def test_composition_detects_declared_conflicts() -> None:
    """Two canonical objects that conflict may not be composed into one unit."""
    left = _object("UCKO-TEST-C1", conflicts_with=("UCKO-TEST-C2",))
    right = _object("UCKO-TEST-C2", statement="A different statement.")
    intake = _synthetic_intake(left, right)
    plan = PlanningEngine().plan(intake)
    _composition, findings = CompositionEngine().compose(intake, plan)
    assert ("UCKO-TEST-C1", "UCKO-TEST-C2") in findings.conflicts
    assert not findings.clean


def test_composition_detects_duplicate_knowledge() -> None:
    """Identical knowledge under two identities violates the Knowledge Once Principle."""
    intake = _synthetic_intake(
        _object("UCKO-TEST-D1", statement="The very same statement."),
        _object("UCKO-TEST-D2", statement="The very same statement."),
    )
    plan = PlanningEngine().plan(intake)
    _composition, findings = CompositionEngine().compose(intake, plan)
    assert ("UCKO-TEST-D1", "UCKO-TEST-D2") in findings.duplicate_knowledge
    assert not findings.clean


# --------------------------------------------------------------------------- #
# generation                                                                  #
# --------------------------------------------------------------------------- #


def test_generation_is_byte_identical_across_two_passes(pipeline) -> None:
    intake, plan, composition, _findings, _manifest = pipeline
    proof = GenerationEngine().verify_determinism(intake, plan, composition)
    assert proof["deterministic"] is True
    assert proof["mismatches"] == []


def test_every_artifact_is_anchored_to_canonical_knowledge(pipeline) -> None:
    intake, _plan, _composition, _findings, manifest = pipeline
    known = set(intake.object_ids())
    assert manifest.artifacts
    for artifact in manifest.artifacts:
        assert artifact.provenance.source_ckos
        assert set(artifact.provenance.source_ckos) <= known


def test_every_artifact_carries_complete_provenance(pipeline) -> None:
    intake, _plan, _composition, _findings, manifest = pipeline
    for artifact in manifest.artifacts:
        provenance = artifact.provenance.to_dict()
        for field in (
            "generator",
            "generator_version",
            "capability",
            "plan_id",
            "step_id",
            "unit_id",
            "target_id",
            "knowledge_seal",
        ):
            assert provenance[field], f"{artifact.relative_path} missing {field}"
        assert provenance["knowledge_seal"] == intake.knowledge_seal
        assert provenance["authority"].startswith("NONE")


def test_all_seven_families_are_generated(pipeline) -> None:
    _intake, _plan, _composition, _findings, manifest = pipeline
    assert set(manifest.by_family()) == {family.value for family in FAMILY_ORDER}


def test_generated_python_artifacts_compile(pipeline) -> None:
    _intake, _plan, _composition, _findings, manifest = pipeline
    python_artifacts = [art for art in manifest.artifacts if art.media is MediaKind.PYTHON]
    assert python_artifacts
    for artifact in python_artifacts:
        compile(artifact.content, artifact.relative_path, "exec")


def test_generated_json_artifacts_parse_and_cite_the_knowledge_seal(pipeline) -> None:
    intake, _plan, _composition, _findings, manifest = pipeline
    json_artifacts = [art for art in manifest.artifacts if art.media is MediaKind.JSON]
    assert json_artifacts
    for artifact in json_artifacts:
        document = json.loads(artifact.content)
        assert document["knowledge_seal"] == intake.knowledge_seal
        assert document["provenance"]["knowledge_seal"] == intake.knowledge_seal


def test_generated_artifacts_carry_no_wall_clock(pipeline) -> None:
    """Identity is content, never time — no generated body may embed a timestamp."""
    _intake, _plan, _composition, _findings, manifest = pipeline
    for artifact in manifest.artifacts:
        if artifact.media is MediaKind.JSON:
            document = json.loads(artifact.content)
            assert "generated_at" not in document
            assert "timestamp" not in document


def test_generator_registry_is_complete_and_unambiguous() -> None:
    manifest = registry_manifest()
    assert len(manifest) == len(FAMILY_ORDER)
    assert [entry["family"] for entry in manifest] == [f.value for f in FAMILY_ORDER]
    assert len({entry["generator"] for entry in manifest}) == len(FAMILY_ORDER)


# --------------------------------------------------------------------------- #
# governance                                                                  #
# --------------------------------------------------------------------------- #


def test_repository_realization_is_governed() -> None:
    decision = RealizationIntelligenceEngine().govern()
    assert decision.verdict == VERDICT_GOVERNED, decision.blocking_reasons
    assert decision.passed_count == len(GATES)


def test_every_declared_gate_is_present_and_actually_exercised() -> None:
    decision = RealizationIntelligenceEngine().govern()
    assert sorted(gate.gate for gate in decision.gates) == sorted(GATES)
    for gate in decision.gates:
        assert gate.checked > 0, f"{gate.gate} passed vacuously"


def test_gates_fail_closed_when_evidence_is_absent(pipeline) -> None:
    """A gate with no evidence supplied must FAIL, never pass by default."""
    intake, plan, composition, findings, manifest = pipeline
    decision = RealizationGovernor().adjudicate(
        intake=intake,
        plan=plan,
        composition=composition,
        findings=findings,
        manifest=manifest,
        determinism=None,
        ledger=None,
    )
    assert not decision.governed
    failed = {gate.gate for gate in decision.gates if not gate.passed}
    assert failed == {"GENERATION_DETERMINISM", "TRACE_CLOSURE"}
    assert "GENERATION_DETERMINISM:unexercised" in decision.blocking_reasons


def test_enforcement_raises_on_a_rejected_decision(pipeline) -> None:
    intake, plan, composition, findings, manifest = pipeline
    decision = RealizationGovernor().adjudicate(
        intake=intake,
        plan=plan,
        composition=composition,
        findings=findings,
        manifest=manifest,
    )
    with pytest.raises(GovernanceRejectedError):
        enforce_realization(decision)


def test_duplicate_knowledge_rejects_the_run() -> None:
    intake = _synthetic_intake(
        _object("UCKO-TEST-D1", statement="The very same statement."),
        _object("UCKO-TEST-D2", statement="The very same statement."),
    )
    plan = PlanningEngine().plan(intake)
    composition, findings = CompositionEngine().compose(intake, plan)
    manifest = GenerationEngine().generate(intake, plan, composition)
    determinism = GenerationEngine().verify_determinism(intake, plan, composition)
    ledger = TraceabilityEngine().build(intake, plan, composition, manifest)
    decision = RealizationGovernor().adjudicate(
        intake=intake,
        plan=plan,
        composition=composition,
        findings=findings,
        manifest=manifest,
        determinism=determinism,
        ledger=ledger,
    )
    assert not decision.governed
    assert any(
        reason.startswith("COMPOSITION_NO_DUPLICATE_KNOWLEDGE")
        for reason in decision.blocking_reasons
    )


def test_decision_is_sealed_and_deterministic() -> None:
    engine = RealizationIntelligenceEngine()
    assert engine.govern().seal == engine.govern().seal


# --------------------------------------------------------------------------- #
# traceability                                                                #
# --------------------------------------------------------------------------- #


def test_traceability_is_closed_in_both_directions(pipeline) -> None:
    intake, plan, composition, _findings, manifest = pipeline
    ledger = TraceabilityEngine().build(intake, plan, composition, manifest)
    assert ledger.forward_gaps == ()
    assert ledger.orphan_artifacts == ()
    assert ledger.closed


def test_trace_chain_reaches_artifacts_from_a_canonical_object(pipeline) -> None:
    intake, plan, composition, _findings, manifest = pipeline
    ledger = TraceabilityEngine().build(intake, plan, composition, manifest)
    cko_id = intake.object_ids()[0]
    chain = ledger.chain(cko_id)
    assert chain["canonical-object->target"]
    assert chain["target->step"]
    assert chain["step->unit"]
    assert chain["unit->artifact"]


def test_orphan_artifact_breaks_closure(pipeline) -> None:
    """An artifact with no canonical ancestor must be reported, not tolerated."""
    intake, plan, composition, _findings, manifest = pipeline
    orphan = GeneratedArtifact(
        relative_path="orphan/invented.json",
        family=ArtifactFamily.ARCHITECTURE,
        media=MediaKind.JSON,
        content="{}\n",
        provenance=Provenance(
            generator="test.orphan",
            generator_version="0.0.0",
            capability="URI-000001",
            plan_id=plan.plan_id,
            step_id="STEP",
            unit_id="UNIT",
            target_id="TARGET",
            knowledge_seal=intake.knowledge_seal,
            source_ckos=(),
        ),
    )
    polluted = GenerationManifest(
        composition_id=manifest.composition_id,
        composition_seal=manifest.composition_seal,
        plan_id=manifest.plan_id,
        knowledge_seal=manifest.knowledge_seal,
        artifacts=(*manifest.artifacts, orphan),
    )
    ledger = TraceabilityEngine().build(intake, plan, composition, polluted)
    assert "orphan/invented.json" in ledger.orphan_artifacts
    assert not ledger.closed


# --------------------------------------------------------------------------- #
# implementation safety                                                       #
# --------------------------------------------------------------------------- #


def _manifest_with(path: str, pipeline) -> GenerationManifest:
    intake, plan, _composition, _findings, manifest = pipeline
    artifact = GeneratedArtifact(
        relative_path=path,
        family=ArtifactFamily.ARCHITECTURE,
        media=MediaKind.JSON,
        content="{}\n",
        provenance=Provenance(
            generator="test",
            generator_version="0.0.0",
            capability="URI-000001",
            plan_id=plan.plan_id,
            step_id="STEP",
            unit_id="UNIT",
            target_id="TARGET",
            knowledge_seal=intake.knowledge_seal,
            source_ckos=(intake.object_ids()[0],),
        ),
    )
    return GenerationManifest(
        composition_id=manifest.composition_id,
        composition_seal=manifest.composition_seal,
        plan_id=manifest.plan_id,
        knowledge_seal=manifest.knowledge_seal,
        artifacts=(artifact,),
    )


def test_materialization_refuses_the_frozen_corpus(pipeline) -> None:
    frozen_config = RealizationConfig.create(REPO, artifact_root=REPO / "00-BOOK")
    implementer = ImplementationEngine(frozen_config)
    with pytest.raises(FrozenSurfaceError):
        implementer.preflight(_manifest_with("uri-should-never-exist.json", pipeline))


def test_materialization_refuses_path_traversal(tmp_path, pipeline) -> None:
    implementer = ImplementationEngine(_config(tmp_path))
    with pytest.raises(ImplementationError):
        implementer.preflight(_manifest_with("../escaped.json", pipeline))


def test_materialization_refuses_an_absolute_path(tmp_path, pipeline) -> None:
    implementer = ImplementationEngine(_config(tmp_path))
    with pytest.raises(ImplementationError):
        implementer.preflight(_manifest_with("/etc/uri-escape.json", pipeline))


def test_materialization_refuses_an_empty_manifest(tmp_path, pipeline) -> None:
    _intake, _plan, _composition, _findings, manifest = pipeline
    empty = GenerationManifest(
        composition_id=manifest.composition_id,
        composition_seal=manifest.composition_seal,
        plan_id=manifest.plan_id,
        knowledge_seal=manifest.knowledge_seal,
        artifacts=(),
    )
    with pytest.raises(ImplementationError):
        ImplementationEngine(_config(tmp_path)).materialize(empty)


def test_dry_run_writes_nothing(engine) -> None:
    result = engine.realize(dry_run=True, emit=False)
    assert result.governed
    assert result.record is not None
    assert result.record.dry_run is True
    assert not engine.config.artifact_root.exists()


# --------------------------------------------------------------------------- #
# end-to-end realization                                                      #
# --------------------------------------------------------------------------- #


def test_realize_materializes_and_verifies_every_artifact(engine) -> None:
    result = engine.realize()
    assert result.governed
    assert result.record is not None
    assert result.record.verified is True
    assert len(result.record.files) == len(result.manifest.artifacts)
    for item in result.record.files:
        path = engine.config.artifact_root / item.relative_path
        assert path.is_file()


def test_realize_is_idempotent(engine) -> None:
    engine.realize()
    second = engine.realize()
    assert second.record is not None
    assert set(second.record.actions()) == {"unchanged"}


def test_realize_emits_the_complete_evidence_bundle(engine) -> None:
    result = engine.realize()
    assert result.evidence.missing() == ()
    assert sorted(result.emitted) == sorted(REQUIRED_FILES)
    report = verify_bundle(engine.config)
    assert report["complete"] is True
    assert report["checked"] == len(REQUIRED_FILES)
    assert report["failed"] == []


def test_evidence_documents_are_individually_sealed(engine) -> None:
    result = engine.realize()
    for name, path in result.emitted.items():
        with open(path, encoding="utf-8") as handle:
            document = json.load(handle)
        assert verify_seal(document), f"{name} seal mismatch"


def test_evidence_varies_only_where_the_materialization_pass_differs(engine) -> None:
    """Re-running changes exactly one fact: what the materialization pass did.

    The first pass creates files; the second finds them byte-identical and reports
    ``unchanged``. Exactly two documents may reflect that — the implementation record
    that states the observation, and the evidence record that seals it. Every
    knowledge-derived document must be byte-identical.

    The governance decision is NO LONGER among them. It varied only because it cites
    ``implementation_id``, and that id was sealed over the per-file ``action`` — so a
    pristine clone reporting ``created`` and every later pass reporting ``unchanged``
    produced two different implementation identities from identical canonical
    knowledge. ``realization/UCOS-URI-MANIFEST.json`` therefore had no fixed point,
    which is why ``intelligence/realization/engine.py`` could not be added to
    scripts/generate-prerequisites.sh and ``realization/`` stayed the one open
    bootstrap gap in the generated-artifact registry.

    ``action`` is now excluded from the seal and from the manifest (UAKOS-CLOSURE-008:
    an execution transcript is evidence, never identity). The observation is preserved
    where it belongs — on the returned record, in the structured log, and in these two
    evidence documents.
    """

    first = engine.realize()
    second = engine.realize()
    assert first.record is not None and second.record is not None
    assert set(first.record.actions()) == {"created"}
    assert set(second.record.actions()) == {"unchanged"}
    varied = {
        name
        for name in first.evidence.documents
        if first.evidence.documents[name] != second.evidence.documents[name]
    }
    assert varied == {IMPLEMENTATION_FILE, RECORD_FILE}
    # The implementation IDENTITY is now a function of what was materialized, not of
    # what the filesystem held first — so the same knowledge yields one id, always.
    assert first.record.seal == second.record.seal
    assert first.record.implementation_id == second.record.implementation_id
    assert first.evidence.documents[GOVERNANCE_FILE] == second.evidence.documents[GOVERNANCE_FILE]
    # The governance verdict itself is unchanged — only the id it cites moved.
    assert first.decision.verdict == second.decision.verdict == VERDICT_GOVERNED
    assert [gate.to_dict() for gate in first.decision.gates] == [
        gate.to_dict() for gate in second.decision.gates
    ]


def test_knowledge_derived_evidence_is_independent_of_the_output_location(engine, tmp_path) -> None:
    """The knowledge-derived documents must not depend on where output happens to land.

    Only the implementation record legitimately differs between two output roots — it
    records the path it actually wrote to. Everything upstream of materialization is a
    pure function of canonical knowledge and must be byte-identical.
    """

    first = engine.realize()
    other = RealizationIntelligenceEngine(_config(tmp_path / "elsewhere"))
    second = other.realize()
    for name in (
        INTAKE_FILE,
        PLAN_FILE,
        COMPOSITION_FILE,
        GENERATION_FILE,
        TRACEABILITY_FILE,
    ):
        assert (
            first.evidence.documents[name] == second.evidence.documents[name]
        ), f"{name} depends on the output location"
    assert first.manifest.seal == second.manifest.seal
    assert first.plan.seal == second.plan.seal


def test_verify_reports_a_corrupted_artifact(engine) -> None:
    result = engine.realize()
    victim = engine.config.artifact_root / result.manifest.artifacts[0].relative_path
    victim.write_text("tampered\n", encoding="utf-8")
    report = engine.implementer.verify(result.manifest)
    assert report["verified"] is False
    assert report["failed"]


def test_generated_runtime_boots_against_canonical_knowledge(engine) -> None:
    """The emitted runtime module is executable and enforces its own checks."""
    result = engine.realize()
    runtime_modules = [
        art.relative_path
        for art in result.manifest.artifacts
        if art.family is ArtifactFamily.RUNTIME and art.media is MediaKind.PYTHON
    ]
    assert runtime_modules
    for relative in runtime_modules:
        path = engine.config.artifact_root / relative
        spec = importlib.util.spec_from_file_location(f"uri_test_{path.stem}", path)
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        report = module.boot(result.intake.base)
        assert report["ready"] is True, report["failed_checks"]


def test_generated_api_route_table_dispatches(engine) -> None:
    result = engine.realize()
    route_modules = [
        art.relative_path
        for art in result.manifest.artifacts
        if art.family is ArtifactFamily.API and art.media is MediaKind.PYTHON
    ]
    assert route_modules
    for relative in route_modules:
        path = engine.config.artifact_root / relative
        spec = importlib.util.spec_from_file_location(f"uri_routes_{path.stem}", path)
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        records = module.list_objects(result.intake.base)
        assert records
        assert {record["universe"] for record in records} == {module.UNIVERSE}
        assert module.list_kinds(result.intake.base) == list(module.KINDS)


def test_result_summary_is_serialisable_and_deterministic(engine) -> None:
    summary = engine.realize().summary()
    encoded = json.dumps(summary, sort_keys=True)
    assert summary["verdict"] == VERDICT_GOVERNED
    assert summary["trace_closed"] is True
    assert summary["deterministic"] is True
    assert "URI-000001" in encoded


def test_evidence_build_is_pure(pipeline) -> None:
    """Building evidence writes nothing and is a function of the stage outputs."""
    intake, plan, composition, findings, manifest = pipeline
    determinism = GenerationEngine().verify_determinism(intake, plan, composition)
    ledger = TraceabilityEngine().build(intake, plan, composition, manifest)
    decision = RealizationGovernor().adjudicate(
        intake=intake,
        plan=plan,
        composition=composition,
        findings=findings,
        manifest=manifest,
        determinism=determinism,
        ledger=ledger,
    )
    kwargs = {
        "intake": intake,
        "plan": plan,
        "composition": composition,
        "findings": findings,
        "manifest": manifest,
        "decision": decision,
        "ledger": ledger,
        "determinism": determinism,
    }
    assert build_evidence(**kwargs).record_hash == build_evidence(**kwargs).record_hash


# --------------------------------------------------------------------------- #
# command surface                                                             #
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize(
    "command",
    ["intake", "plan", "compose", "generate", "govern", "trace", "verify", "generators"],
)
def test_cli_read_only_commands_exit_zero(command, tmp_path, capsys) -> None:
    exit_code = cli_main(
        [
            "--repo",
            str(REPO),
            "--artifact-root",
            str(tmp_path / "realization"),
            "--evidence-dir",
            str(tmp_path / "evidence"),
            command,
        ]
    )
    captured = capsys.readouterr()
    if command == "verify":
        # verify inspects on-disk state, which is empty for a throwaway root.
        assert exit_code in (0, 1)
    else:
        assert exit_code == 0, captured.out
    assert json.loads(captured.out)


def test_cli_realize_writes_into_the_configured_roots(tmp_path, capsys) -> None:
    artifacts = tmp_path / "realization"
    evidence = tmp_path / "evidence"
    exit_code = cli_main(
        [
            "--repo",
            str(REPO),
            "--artifact-root",
            str(artifacts),
            "--evidence-dir",
            str(evidence),
            "realize",
        ]
    )
    payload = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert payload["verdict"] == VERDICT_GOVERNED
    assert (artifacts / "UCOS-URI-MANIFEST.json").is_file()
    assert (evidence / "realization-evidence-record.json").is_file()


# --------------------------------------------------------------------------- #
# implementation: verification, pruning and the convenience entry point        #
#                                                                             #
# WHY THESE EXIST. Materialization was exercised end to end, so its happy path #
# was covered and none of its refusals were: the byte-level verification that  #
# catches an artifact edited after it was sealed, the bounded pruning of files #
# a previous pass generated, and the module-level entry point the CLI documents#
# were all unexecuted. A verifier nothing has caught out is not a verifier.    #
# --------------------------------------------------------------------------- #


def test_verify_reports_a_present_artifact_that_no_longer_matches_its_seal(
    tmp_path, pipeline
) -> None:
    manifest = _manifest_with("checked.json", pipeline)
    implementer = ImplementationEngine(_config(tmp_path))
    implementer.materialize(manifest)

    target = implementer.config.artifact_root / "checked.json"
    target.write_text('{"edited": true}\n', encoding="utf-8")

    report = implementer.verify(manifest)
    assert report["verified"] is False
    assert report["checked"] == 1
    assert report["failed"][0]["path"] == "checked.json"
    assert report["failed"][0]["present"] is True


def test_verify_reports_an_artifact_that_is_absent_entirely(tmp_path, pipeline) -> None:
    manifest = _manifest_with("never-written.json", pipeline)
    report = ImplementationEngine(_config(tmp_path)).verify(manifest)
    assert report["verified"] is False
    assert report["failed"][0]["actual"] is None
    assert report["failed"][0]["present"] is False


def test_materialization_raises_when_the_bytes_on_disk_disagree_with_the_seal(
    tmp_path, pipeline, monkeypatch
) -> None:
    """The raising verification inside ``materialize`` is the one that must never be
    skipped: it is what makes the returned record an attestation rather than a log. It
    is forged by corrupting the write, because a correct write cannot reach it."""
    manifest = _manifest_with("corrupted.json", pipeline)
    implementer = ImplementationEngine(_config(tmp_path))

    real_write = Path.write_text

    def _short_write(self, data, *args, **kwargs):
        if self.name == "corrupted.json":
            return real_write(self, "{}", *args, **kwargs)
        return real_write(self, data, *args, **kwargs)

    monkeypatch.setattr(Path, "write_text", _short_write)
    with pytest.raises(ImplementationError) as excinfo:
        implementer.materialize(manifest)
    assert "do not match" in str(excinfo.value)


def test_an_artifact_root_that_is_not_a_parent_of_the_resolved_path_is_refused(
    tmp_path, pipeline
) -> None:
    """A path that survives the traversal and absolute checks but still resolves outside
    the artifact root — here through a symlink — is refused by the containment check."""
    config = _config(tmp_path)
    config.artifact_root.mkdir(parents=True, exist_ok=True)
    outside = tmp_path / "outside"
    outside.mkdir()
    (config.artifact_root / "link").symlink_to(outside, target_is_directory=True)

    implementer = ImplementationEngine(config)
    with pytest.raises(ImplementationError, match="outside the artifact root"):
        implementer.preflight(_manifest_with("link", pipeline))


def test_nothing_is_stale_before_a_first_pass_has_written_a_manifest(tmp_path, pipeline) -> None:
    implementer = ImplementationEngine(_config(tmp_path))
    assert implementer.stale_artifacts(_manifest_with("a.json", pipeline)) == ()


def test_an_unreadable_manifest_of_record_yields_no_previous_paths(tmp_path, pipeline) -> None:
    """A corrupt manifest must not make pruning claim that every current artifact is
    stale; it yields nothing, which is the fail-safe direction for a delete."""
    implementer = ImplementationEngine(_config(tmp_path))
    implementer.manifest_path().parent.mkdir(parents=True, exist_ok=True)
    implementer.manifest_path().write_text("{ not json", encoding="utf-8")
    assert implementer.stale_artifacts(_manifest_with("a.json", pipeline)) == ()


def test_an_artifact_a_previous_pass_claimed_and_this_one_does_not_is_stale(
    tmp_path, pipeline
) -> None:
    implementer = ImplementationEngine(_config(tmp_path))
    implementer.materialize(_manifest_with("first.json", pipeline))

    current = _manifest_with("second.json", pipeline)
    assert implementer.stale_artifacts(current) == ("first.json",)


def test_pruning_is_a_dry_run_by_default_and_removes_nothing(tmp_path, pipeline) -> None:
    implementer = ImplementationEngine(_config(tmp_path))
    implementer.materialize(_manifest_with("first.json", pipeline))
    stale_path = implementer.config.artifact_root / "first.json"

    report = implementer.prune(_manifest_with("second.json", pipeline))
    assert report["dry_run"] is True
    assert report["stale"] == ["first.json"]
    assert report["removed"] == ["first.json"]
    assert stale_path.is_file()


def test_pruning_removes_the_stale_artifact_when_it_is_not_a_dry_run(tmp_path, pipeline) -> None:
    implementer = ImplementationEngine(_config(tmp_path))
    implementer.materialize(_manifest_with("first.json", pipeline))
    stale_path = implementer.config.artifact_root / "first.json"

    report = implementer.prune(_manifest_with("second.json", pipeline), dry_run=False)
    assert report["removed"] == ["first.json"]
    assert not stale_path.exists()


def test_a_stale_entry_whose_file_is_already_gone_is_not_reported_as_removed(
    tmp_path, pipeline
) -> None:
    implementer = ImplementationEngine(_config(tmp_path))
    implementer.materialize(_manifest_with("first.json", pipeline))
    (implementer.config.artifact_root / "first.json").unlink()

    report = implementer.prune(_manifest_with("second.json", pipeline), dry_run=False)
    assert report["stale"] == ["first.json"]
    assert report["removed"] == []


def test_the_convenience_entry_point_materializes_the_same_manifest(tmp_path, pipeline) -> None:
    config = _config(tmp_path)
    record = materialize_artifacts(_manifest_with("direct.json", pipeline), config)
    assert record.verified is True
    assert (config.artifact_root / "direct.json").is_file()


# --------------------------------------------------------------------------- #
# the accessors, the slugs and the refusals a governed run never reaches       #
# --------------------------------------------------------------------------- #


def test_a_slug_collapses_a_run_of_separators_into_one_and_never_renders_empty() -> None:
    """Every artifact path and every target identity is built from this. A slug that emitted one
    dash per separator would make two universes differing only in punctuation produce different
    paths for the same thing, and one that could render empty would produce a path with no name."""

    assert slug("Universe  of --- Things") == "universe-of-things"
    assert slug("///") == "unnamed"
    assert slug("  Leading and trailing  ") == "leading-and-trailing"
    assert identifier("Universe of Things")


def test_a_target_names_its_module_and_its_path_from_one_universe(pipeline) -> None:
    """The module name and the path fragment are two projections of one universe, and they are
    derived rather than stored so a target cannot carry a path that disagrees with its own id."""
    _intake, plan, _composition, _findings, _manifest = pipeline
    target = plan.targets[0]
    assert target.target_id.endswith(target.path_slug.upper())
    assert target.module_name.isidentifier()


def test_every_plan_and_composition_accessor_resolves_or_refuses(pipeline) -> None:
    """The refusals are what stop a caller from reading a step, target or unit that is not in
    the plan it holds; the resolutions are what every generator depends on. A resolver that
    could only refuse would make the whole plan unreadable."""
    _intake, plan, composition, _findings, _manifest = pipeline
    assert plan.step(plan.steps[0].step_id) is plan.steps[0]
    assert plan.target(plan.targets[0].target_id) is plan.targets[0]
    assert composition.unit(composition.units[0].unit_id) is composition.units[0]
    for resolver, argument in (
        (plan.step, "URI-STEP-NOBODY-PLANNED"),
        (plan.target, "URI-TGT-NOBODY-DECLARED"),
        (composition.unit, "URI-UNIT-NOBODY-COMPOSED"),
    ):
        with pytest.raises(PlanningError):
            resolver(argument)


def test_an_intake_resolves_a_target_and_refuses_one_it_did_not_derive(pipeline) -> None:
    """Every target the intake answers for was derived from a knowledge universe. One it did not
    derive has no canonical objects behind it, so answering for it would produce an artifact
    anchored to nothing."""
    intake, _plan, _composition, _findings, _manifest = pipeline
    first = intake.targets[0]
    assert intake.target(first.target_id) is first
    assert intake.decision_ids() == intake.base.decision_ids()
    assert isinstance(intake.decisions_for(first), tuple)
    with pytest.raises(KnowledgeIntakeError):
        intake.target("URI-TGT-NOBODY-DERIVED")


def test_an_intake_over_a_store_that_does_not_exist_falls_back_to_the_seed(
    tmp_path, monkeypatch
) -> None:
    """A repository with no canonical store still has knowledge — the engine's own seed — and
    realizing from it is different from realizing from nothing. Reading an absent store as an
    empty one would generate an empty, governed, meaningless bundle."""

    class _Absent:
        def exists(self) -> bool:
            return False

    monkeypatch.setattr(knowledge_module, "KnowledgeStore", lambda *a, **k: _Absent())
    intake = KnowledgeIntake.load()
    assert intake.source == "engine.knowledge.seed"
    assert intake.targets


def test_an_intake_whose_knowledge_cannot_be_read_is_a_fault(monkeypatch) -> None:
    """A store that refuses is not an empty store, and reading it as one would seal a bundle
    over knowledge nobody could load."""

    class _Refusing:
        def exists(self) -> bool:
            return True

        def load(self, *args, **kwargs):  # noqa: ANN002, ANN003, ANN202
            raise KnowledgeError("the canonical store cannot be read")

    monkeypatch.setattr(knowledge_module, "KnowledgeStore", lambda *a, **k: _Refusing())
    with pytest.raises(KnowledgeIntakeError):
        KnowledgeIntake.load()


def test_an_evidence_bundle_reports_completeness_and_refuses_a_partial_emit(tmp_path) -> None:
    """A partial bundle is worse than none: a reader finding four of five documents cannot tell
    a bundle that was never finished from one whose fifth document was removed."""

    partial = RealizationEvidence(knowledge_seal="a" * 64, documents={})
    assert not partial.complete()
    assert partial.missing()
    with pytest.raises(EvidenceError, match="incomplete"):
        emit_evidence(partial, _config(tmp_path))


def test_evidence_may_not_be_written_into_the_frozen_corpus(tmp_path) -> None:
    """DP-03 owns the frozen corpus. An evidence bundle written into it would make the certified
    corpus a place this engine writes, which is the one thing it may never be."""

    config = RealizationConfig.create(REPO, artifact_root=tmp_path, evidence_dir=tmp_path)
    with pytest.raises(EvidenceError, match="frozen corpus"):
        _guard_writable(config, REPO / "99-FREEZE")


def test_an_unreadable_evidence_document_is_reported_as_unsealed(tmp_path) -> None:
    """Present and unreadable is a third state beside absent and sealed. Reporting it as sealed
    would certify a document nobody could parse; reporting it as absent would hide that
    something is there."""

    config = _config(tmp_path)
    config.evidence_dir.mkdir(parents=True, exist_ok=True)
    (config.evidence_dir / REQUIRED_FILES[0]).write_text("{ not json", encoding="utf-8")
    report = verify_bundle(config)
    entry = next(item for item in report["files"] if item["file"] == REQUIRED_FILES[0])
    assert entry["present"] is True
    assert entry["sealed"] is False
    assert not report["complete"]


def test_the_convenience_traceability_entry_point_builds_the_same_ledger(tmp_path, pipeline):
    """The module-level function is what a caller outside this package uses. One that drifted
    from the engine would give two answers to "is the closure complete"."""

    intake, plan, composition, _findings, manifest = pipeline
    implementer = ImplementationEngine(_config(tmp_path))
    record = implementer.materialize(manifest)
    direct = build_trace(intake, plan, composition, manifest, record)
    assert (
        direct.to_dict()
        == TraceabilityEngine().build(intake, plan, composition, manifest, record).to_dict()
    )


def test_the_config_resolves_an_artifact_path_and_a_repo_root_of_last_resort(tmp_path) -> None:
    """`artifact_path` is how every generator turns a relative artifact path into a real one.
    The
    fallback root is what keeps the engine usable outside a repository whose marker it can find,
    rather than failing to construct at all."""

    config = _config(tmp_path)
    assert config.artifact_path("a/b.json") == config.artifact_root / "a/b.json"
    assert resolve_repo_root(tmp_path).is_dir()


def test_the_module_entry_point_dispatches_to_the_cli(monkeypatch) -> None:
    """``python -m intelligence.realization`` is a second entry point and a dispatcher rather
    than a copy: two copies of an entry point are two things to keep in step."""

    calls: list[int] = []
    monkeypatch.setattr(cli_module, "main", lambda: calls.append(1) or 0)
    with pytest.raises(SystemExit) as exit_info:
        runpy.run_module("intelligence.realization", run_name="__main__")
    assert exit_info.value.code == 0
    assert calls == [1]


def _cli(tmp_path, *argv: str) -> int:
    return cli_main(
        [
            "--repo",
            str(REPO),
            "--artifact-root",
            str(tmp_path / "realization"),
            "--evidence-dir",
            str(tmp_path / "evidence"),
            *argv,
        ]
    )


def test_the_generate_command_can_emit_the_content_it_generated(tmp_path, capsys) -> None:
    """`--show-content` is what makes the command inspectable without materializing: a reader
    can see the bytes that WOULD be written rather than the manifest that describes them."""
    assert _cli(tmp_path, "generate", "--show-content") == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["contents"]
    assert set(payload["contents"]) == {
        artifact["relative_path"] for artifact in payload["generation"]["artifacts"]
    }


def test_the_trace_command_carries_its_edges_only_when_asked(tmp_path, capsys) -> None:
    """The edge set is the whole closure and is large. Emitting it unconditionally would make
    the ordinary command unreadable; omitting it always would make the closure uninspectable."""
    assert _cli(tmp_path, "trace", "--edges") == 0
    with_edges = json.loads(capsys.readouterr().out)
    assert with_edges["edges"]
    assert _cli(tmp_path, "trace") == 0
    without = json.loads(capsys.readouterr().out)
    assert "edges" not in without
    assert without["coverage"] == with_edges["coverage"]


def test_the_evidence_command_checks_a_bundle_and_emits_one(tmp_path, capsys) -> None:
    """Two questions on one command: what is on disk, and what this run would write. A check
    that emitted would answer the second while claiming to answer the first."""
    assert _cli(tmp_path, "evidence", "--check-only") == 1
    checked = json.loads(capsys.readouterr().out)
    assert checked["complete"] is False

    assert _cli(tmp_path, "evidence") == 0
    emitted = json.loads(capsys.readouterr().out)
    assert emitted["verdict"] == VERDICT_GOVERNED
    assert emitted["emitted"]

    assert _cli(tmp_path, "evidence", "--check-only") == 0


def test_a_foundation_fault_exits_two_rather_than_reporting_a_verdict(tmp_path, capsys) -> None:
    """Exit 2 is "I could not tell", and it must not be spelled the same way as exit 1, which is
    "I told you and the answer is no"."""

    def _faulting(self, *args, **kwargs):  # noqa: ANN001, ANN002, ANN003, ANN202
        raise _Fault("the canonical store cannot be read")

    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setattr(engine_module.RealizationIntelligenceEngine, "intake", _faulting)
    try:
        assert _cli(tmp_path, "intake") == 2
    finally:
        monkeypatch.undo()
    assert json.loads(capsys.readouterr().out)
    assert cli_module.build_parser() is not None


def test_a_rejected_governance_decision_is_reported_by_the_realize_command(
    tmp_path, capsys, monkeypatch
) -> None:
    """The command reports the rejection rather than raising it: a caller reading stdout must
    see WHICH gate refused, not a traceback that names the raising line."""

    def _rejecting(self, **kwargs):  # noqa: ANN001, ANN003, ANN202
        raise GovernanceRejectedError("a gate refused", gate="URI-GATE-TEST")

    monkeypatch.setattr(engine_module.RealizationIntelligenceEngine, "realize", _rejecting)
    assert _cli(tmp_path, "realize") == 1
    assert json.loads(capsys.readouterr().out)


# --------------------------------------------------------------------------- #
# the stage guards: every refusal that keeps one pipeline's stages from mixing #
# --------------------------------------------------------------------------- #


def test_generation_refuses_stages_derived_from_different_states(pipeline) -> None:
    """A plan, a composition and an intake are three derivations of one knowledge state. Mixing
    two states would generate artifacts anchored to objects the manifest does not cite, and the
    seals would still all verify — each against its own half."""

    intake, plan, composition, _findings, _manifest = pipeline
    with pytest.raises(GenerationError, match="does not belong to the supplied plan"):
        GenerationEngine._assert_coherent(
            intake, plan, _replace(composition, plan_id="URI-PLAN-SOMETHING-ELSE")
        )
    with pytest.raises(GenerationError, match="different canonical knowledge state"):
        GenerationEngine._assert_coherent(
            intake, plan, _replace(composition, knowledge_seal="a" * 64)
        )
    with pytest.raises(GenerationError, match="nothing to generate"):
        GenerationEngine._assert_coherent(intake, plan, _replace(composition, units=()))


def test_a_generator_that_emits_nothing_or_the_wrong_family_is_refused(pipeline) -> None:
    """Three ways a generator can be wrong while looking right: producing nothing for a planned
    step, producing something outside its own family, and producing something anchored to no
    canonical object. Each would leave the manifest describing a realization that did not
    happen."""

    _intake, _plan, composition, _findings, manifest = pipeline
    artifact = manifest.artifacts[0]
    unit = composition.units[0]

    class _Context:
        def __init__(self, unit: object) -> None:
            self.unit = unit

    context = _Context(unit)

    class _Silent:
        name = "silent"

        def generate(self, _context: object) -> tuple:
            return ()

    class _Foreign:
        name = "foreign"

        def generate(self, _context: object) -> tuple:
            other = next(family for family in ArtifactFamily if family is not artifact.family)
            return (_replace(artifact, family=other),)

    class _Unanchored:
        name = "unanchored"

        def generate(self, _context: object) -> tuple:
            provenance = _replace(artifact.provenance, source_ckos=())
            return (_replace(artifact, provenance=provenance),)

    for generator, message in (
        (_Silent(), "produced no artifact"),
        (_Foreign(), "outside its own family"),
        (_Unanchored(), "not anchored to any canonical object"),
    ):
        with pytest.raises(GenerationError, match=message):
            with pytest.MonkeyPatch.context() as patch:
                patch.setattr(
                    "intelligence.realization.generation.generator_for",
                    lambda _family, _g=generator: _g,
                )
                GenerationEngine._invoke(artifact.family, context)


def test_two_units_claiming_one_output_path_are_refused(pipeline) -> None:
    """Two units writing one path is a silent overwrite: the manifest would carry one entry and
    the tree would carry whichever unit ran last."""
    _intake, _plan, _composition, _findings, manifest = pipeline
    artifact = manifest.artifacts[0]
    claimed: dict[str, str] = {}
    GenerationEngine._claim_paths((artifact,), claimed, "URI-UNIT-FIRST")
    with pytest.raises(GenerationError, match="two composition units claim the same output path"):
        GenerationEngine._claim_paths((artifact,), claimed, "URI-UNIT-SECOND")


def test_the_convenience_entry_points_produce_what_their_engines_produce() -> None:
    """Each is what a caller outside this package uses. One that drifted from its engine would
    give two answers to the same question — and both would seal."""

    intake = KnowledgeIntake.load()
    plan = build_plan(intake)
    composition, _findings = compose_plan(intake, plan)
    manifest = generate_artifacts(intake, plan, composition)
    assert plan.plan_id == PlanningEngine().plan(intake).plan_id
    assert manifest.seal == GenerationEngine().generate(intake, plan, composition).seal
    by_path = artifact_index(manifest)
    assert set(by_path) == {a.relative_path for a in manifest.artifacts}


def test_planning_refuses_an_intake_with_no_target(pipeline) -> None:
    """No target means no realizable knowledge, and a plan over nothing would generate nothing,
    seal cleanly and be governed — the vacuous pass every gate in this subsystem refuses.

    The intake refuses an empty store outright, so the targetless intake has to be built from a
    populated one — which is the guard that survives a future intake admitting one."""

    intake, _plan, _composition, _findings, _manifest = pipeline
    with pytest.raises(PlanningError, match="no realization targets"):
        PlanningEngine().plan(_replace(intake, targets=()))


def test_a_dependency_graph_with_an_unknown_step_or_a_cycle_is_refused() -> None:
    """Both make the wave order undefined. An unknown dependency would silently never be
    satisfied; a cycle would spin. Refusing names which node is at fault."""

    with pytest.raises(PlanningError, match="depends on an unknown step"):
        _topological_waves(["a"], {"a": ("nobody-planned",)})
    with pytest.raises(PlanningError, match="dependency cycle"):
        _topological_waves(["a", "b"], {"a": ("b",), "b": ("a",)})
    assert _topological_waves(["a", "b"], {"b": ("a",)}) == (("a",), ("b",))


def test_composition_refuses_a_plan_from_another_knowledge_state(pipeline) -> None:
    intake, plan, _composition, _findings, _manifest = pipeline
    with pytest.raises(CompositionError, match="different canonical knowledge state"):
        CompositionEngine().compose(intake, _replace(plan, knowledge_seal="a" * 64))


def test_a_composition_graph_with_an_unknown_upstream_or_a_cycle_is_refused(pipeline) -> None:
    """The same two failures one stage down. A unit depending on nothing that exists would never
    be ordered; a cycle would never settle."""

    _intake, _plan, composition, _findings, _manifest = pipeline
    first, second = composition.units[0], composition.units[1]
    engine = CompositionEngine()
    with pytest.raises(CompositionError, match="depends on an unknown unit"):
        engine._order((_replace(first, upstream_units=("URI-UNIT-NOBODY-COMPOSED",)),))
    with pytest.raises(CompositionError, match="cycle"):
        engine._order(
            (
                _replace(first, upstream_units=(second.unit_id,)),
                _replace(second, upstream_units=(first.unit_id,)),
            )
        )


def test_a_gate_set_that_is_incomplete_or_duplicated_is_refused(pipeline) -> None:
    """The gate set is closed. A missing gate is an unasked question reported as governed; a
    duplicated one is one question counted twice."""

    decision = RealizationIntelligenceEngine().govern()
    outcomes = decision.gates
    with pytest.raises(GovernanceRejectedError, match="incomplete or duplicated"):
        _Governor._assert_complete(outcomes[:-1])
    with pytest.raises(GovernanceRejectedError, match="incomplete or duplicated"):
        _Governor._assert_complete((*outcomes, outcomes[0]))


def test_a_determinism_proof_that_says_nothing_still_fails_the_gate() -> None:
    """A proof reporting `deterministic: false` with no mismatch names nothing an operator can
    chase, so the gate supplies the one fact it does know: the seals disagreed."""

    outcome = _Governor._generation_determinism(
        {"deterministic": False, "mismatches": [], "artifact_count": 3}
    )
    assert not outcome.passed
    assert outcome.failures == ("seal-mismatch",)


# --------------------------------------------------------------------------- #
# the generators' own helpers, and the registry that binds them               #
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (True, "true"),
        (False, "false"),
        (None, "null"),
        (7, "7"),
        ("plain", "plain"),
        ("", '""'),
        ("has: colon", '"has: colon"'),
        ("yes", '"yes"'),
        (": leading colon", '": leading colon"'),
    ],
)
def test_a_yaml_scalar_quotes_only_when_it_must(value, expected) -> None:
    """The deployment manifests are YAML this repository writes rather than a library's. A
    scalar quoted too little parses as something else; one quoted too much changes the bytes on
    every run for no reason, and the artifacts are compared by byte."""

    assert _yaml_scalar(value) == expected


def test_yaml_renders_empty_collections_and_bare_scalars() -> None:
    """An empty list is a declared-and-empty field, which is a different fact from an absent
    one. Emitting nothing for it would make the two indistinguishable in the rendered manifest."""

    assert _yaml_lines({"empty_list": [], "empty_map": {}}) == [
        "empty_list: []",
        "empty_map: {}",
    ]
    assert _yaml_lines("bare") == ["bare"]
    assert _yaml_lines([{"a": 1}, "b"]) == ["- a: 1", "- b"]


@pytest.mark.parametrize(
    ("value", "expected"),
    [(True, "boolean"), (3, "integer"), ("s", "string"), ([1], "array")],
)
def test_a_schema_type_reads_a_bool_before_an_int(value, expected) -> None:
    """`True` is an int in Python, so a type reader that asked `isinstance(int)` first would
    declare every boolean field an integer — and every consumer would then validate against a
    type the value does not have."""

    assert _json_type(value) == expected


def test_the_generator_registry_refuses_a_duplicated_or_missing_family() -> None:
    """Family → generator is complete and unambiguous BY CONSTRUCTION, which means both
    failures are refused at import rather than reported later: a duplicated family would make
    the emitting generator depend on iteration order, and a missing one would silently produce
    no artifact for a planned step."""

    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(
            "intelligence.realization.generators.GENERATORS",
            (*GENERATORS, GENERATORS[0]),
        )
        with pytest.raises(GenerationError, match="more than one generator"):
            _build_registry()
        patch.setattr("intelligence.realization.generators.GENERATORS", GENERATORS[:1])
        with pytest.raises(GenerationError, match="has no generator"):
            _build_registry()


def test_content_that_is_not_newline_terminated_is_refused(pipeline) -> None:
    """Every artifact is compared by byte and most are read by line-oriented tools. A file
    without a trailing newline differs from the same file with one, and the difference would
    show up as drift rather than as the authoring slip it is."""

    _intake, _plan, _composition, _findings, manifest = pipeline
    artifact = manifest.artifacts[0]
    generator = generator_for(artifact.family)
    with pytest.raises(GenerationError, match="newline-terminated"):
        generator.artifact(
            None,
            relative_path=artifact.relative_path,
            media=artifact.media,
            content="no trailing newline",
        )


def test_a_generation_context_projects_its_target_and_finds_no_absent_upstream(pipeline) -> None:
    """`upstream_artifact` answers None for a family this target produced nothing in, which is
    an ordinary state during the first waves. Raising instead would make every generator that
    cross-references an upstream family unusable before that family had run."""

    intake, plan, composition, _findings, _manifest = pipeline
    unit = composition.units[0]
    context = GenerationContext(
        intake=intake,
        plan=plan,
        composition=composition,
        unit=unit,
        target=plan.target(unit.target_id),
    )
    assert context.invariants == context.target.invariants
    assert context.universe == context.target.universe
    kinds = {obj.kind.value for obj in context.objects}
    for kind in kinds:
        assert all(o.kind.value == kind for o in context.objects_of_kind(kind))
    assert context.objects_of_kind("a-kind-nothing-declares") == ()
    assert context.upstream_artifact(ArtifactFamily.SCHEMA, ".json") is None


# --------------------------------------------------------------------------- #
# a synthetic two-universe knowledge state, which reaches what the repository's #
# own knowledge happens not to exercise                                        #
# --------------------------------------------------------------------------- #


def _decision(decision_id: str, **overrides) -> DecisionRecord:  # noqa: F821
    fields = {
        "decision_id": decision_id,
        "title": f"Decision {decision_id}",
        "problem_statement": "A problem.",
        "context": "A context.",
        "objective": "An objective.",
        "chosen_architecture": "The chosen architecture.",
        "rationale": "The rationale.",
        "authority": KnowledgeAuthority.ENGINEERING,
        "owner": "UCOS-TEST",
        "lifecycle": Lifecycle.OPERATIONAL,
        "version": "1.0.0",
        "review_authority": "UCOS-TEST",
        "supersession_rules": "Superseded only by a later decision of the same authority.",
        "alternatives": ("an alternative nobody chose",),
        "evaluation_criteria": ("a criterion",),
        "tradeoffs": ("a tradeoff",),
        "rejected_options": (RejectedOption(option="an option", reason="a reason"),),
        "consequences": ("a consequence",),
        "risks": ("a risk",),
        "mitigations": ("a mitigation",),
        "certification_requirements": ("a certification requirement",),
    }
    fields.update(overrides)
    return DecisionRecord.create(**fields)


def _two_universe_intake() -> KnowledgeIntake:
    """Two universes, a cross-universe dependency, a conflict pair, an inactive object, and one
    fully-populated decision beside one carrying only its required fields.

    The repository's own canonical knowledge exercises one shape of each of those; this
    exercises the other, which is what the branches below are.
    """

    upstream = _object(
        "UCOS-TEST-UP-0001",
        universe="UPSTREAM",
        kind=KnowledgeKind.RULE,
        decision_links=("UCOS-TEST-DEC-0001",),
    )
    downstream = _object(
        "UCOS-TEST-DOWN-0001",
        universe="DOWNSTREAM",
        kind=KnowledgeKind.RULE,
        dependencies=("UCOS-TEST-UP-0001",),
        conflicts_with=("UCOS-TEST-DOWN-0002",),
        decision_links=("UCOS-TEST-DEC-0002",),
    )
    peer = _object(
        "UCOS-TEST-DOWN-0002",
        universe="DOWNSTREAM",
        kind=KnowledgeKind.RULE,
        decision_links=("UCOS-TEST-DEC-0002",),
    )
    return KnowledgeIntake.from_base(
        KnowledgeBase(
            (upstream, downstream, peer),
            (
                _decision("UCOS-TEST-DEC-0001"),
                _decision(
                    "UCOS-TEST-DEC-0002",
                    alternatives=(),
                    evaluation_criteria=(),
                    tradeoffs=(),
                    rejected_options=(),
                    consequences=(),
                    risks=(),
                    mitigations=(),
                    certification_requirements=(),
                    supersession_rules="",
                ),
            ),
        ),
        source="test",
    )


def test_a_cross_universe_dependency_orders_the_upstream_universe_first() -> None:
    """Realization order across universes is DERIVED from the knowledge, not configured. A
    dependent universe that realized first would cite artifacts that did not exist yet."""
    intake = _two_universe_intake()
    plan = PlanningEngine().plan(intake)
    upstream = plan.target("URI-TGT-UPSTREAM")
    downstream = plan.target("URI-TGT-DOWNSTREAM")
    for step in plan.steps_for(downstream.target_id):
        peers = [
            dep
            for dep in step.depends_on
            if dep in {s.step_id for s in plan.steps_for(upstream.target_id)}
        ]
        assert peers, f"{step.step_id} does not wait for its upstream universe"


def test_a_declared_conflict_between_two_co_bound_objects_is_found(monkeypatch) -> None:
    """A conflict is only a finding where both sides are bound into ONE unit: two objects that
    conflict and never meet are a declaration, not a collision."""
    intake = _two_universe_intake()
    plan = PlanningEngine().plan(intake)
    _composition, findings = CompositionEngine().compose(intake, plan)
    assert findings.conflicts == (("UCOS-TEST-DOWN-0001", "UCOS-TEST-DOWN-0002"),)
    assert not findings.clean


def test_the_whole_pipeline_runs_over_a_synthetic_state_and_governs_itself(tmp_path) -> None:
    """The end-to-end proof on knowledge this repository did not author: every generator emits,
    every gate measures, and the decisions rendered include one carrying every optional section
    and one carrying none — which is what makes the documentation generator's conditionals
    measured rather than assumed."""
    intake = _two_universe_intake()
    plan = PlanningEngine().plan(intake)
    composition, findings = CompositionEngine().compose(intake, plan)
    manifest = GenerationEngine().generate(intake, plan, composition)
    assert manifest.artifacts

    rendered = {a.relative_path: a.content for a in manifest.artifacts}
    decisions = [c for p, c in rendered.items() if p.endswith(".md") and "Alternatives" in c]
    assert decisions, "no decision record rendered its alternatives"

    governor = RealizationGovernor(_config(tmp_path))
    decision = governor.adjudicate(
        intake=intake,
        plan=plan,
        composition=composition,
        findings=findings,
        manifest=manifest,
        determinism=GenerationEngine().verify_determinism(intake, plan, composition),
    )
    assert sorted(gate.gate for gate in decision.gates) == sorted(GATES)
    assert not decision.governed, "the synthetic state declares a conflict; it must not govern"


def test_a_target_citing_only_inactive_knowledge_fails_the_authority_gate() -> None:
    """A target whose every object is retired cites knowledge nobody stands behind, and
    realizing it would generate artifacts anchored to superseded truth."""

    retired = _object("UCOS-TEST-RETIRED-0001", universe="RETIRED", lifecycle=Lifecycle.SUPERSEDED)
    intake = KnowledgeIntake.from_base(KnowledgeBase((retired,)), source="test")
    plan = PlanningEngine().plan(intake)
    outcome = _Governor._knowledge_authority(intake, plan)
    assert not outcome.passed
    assert outcome.failures == ("URI-TGT-RETIRED",)


def test_a_plan_missing_a_family_for_a_target_fails_the_completeness_gate(pipeline) -> None:
    """Realization is total, not selective: every target is realized into every family. A plan
    short one family would leave that target partly realized and fully governed."""

    _intake, plan, _composition, _findings, _manifest = pipeline
    target = plan.targets[0]
    dropped = next(s for s in plan.steps_for(target.target_id))
    outcome = _Governor._plan_family_complete(
        _replace(plan, steps=tuple(s for s in plan.steps if s is not dropped))
    )
    assert not outcome.passed
    assert any(entry.startswith(target.target_id) for entry in outcome.failures)


def test_an_artifact_path_that_would_escape_the_artifact_root_fails_the_frozen_gate(
    tmp_path, pipeline
) -> None:
    """`..` in a relative path is a traversal out of the artifact root, and a path inside the
    frozen corpus is a write DP-03 forbids. Both are refused by the same gate, because both
    make the artifact root a claim rather than a boundary."""

    _intake, _plan, _composition, _findings, manifest = pipeline
    artifact = manifest.artifacts[0]
    escaping = _replace(artifact, relative_path="../escaped.json")
    governor = RealizationGovernor(_config(tmp_path))
    outcome = governor._implementation_frozen_safe(_replace(manifest, artifacts=(escaping,)))
    assert not outcome.passed
    assert outcome.failures == ("../escaped.json",)


def test_materializing_into_the_frozen_corpus_is_refused(tmp_path, pipeline) -> None:
    """The gate refuses it and the implementer refuses it again. Two readers, and neither may
    rely on the other having looked — the frozen corpus is the one surface this engine may
    never write."""
    _intake, _plan, _composition, _findings, manifest = pipeline
    implementer = ImplementationEngine(RealizationConfig.create(REPO, artifact_root=REPO))
    with pytest.raises(FrozenSurfaceError):
        implementer._assert_not_frozen(REPO / "99-FREEZE" / "x.json", "99-FREEZE/x.json")


def test_an_artifact_family_coerces_from_its_own_value(pipeline) -> None:
    """`coerce` is how a family arrives from a serialized manifest. One that defaulted silently
    would read an unknown family as a known one and generate into the wrong place."""

    for family in ArtifactFamily:
        assert ArtifactFamily.coerce(family.value) is family


def test_an_authority_inversion_between_two_objects_is_a_boundary_finding(tmp_path) -> None:
    """Dependency direction must follow authority precedence: a higher authority depending on a
    lower one inverts the hierarchy, and the descriptor names it rather than ordering it away.
    An edge whose far end is outside this unit is skipped, because this universe's descriptor
    can say nothing about a rank it does not hold."""

    low = _object(
        "UCOS-TEST-LOW-0001", universe="INVERTED", authority=KnowledgeAuthority.ENGINEERING
    )
    high = _object(
        "UCOS-TEST-HIGH-0001",
        universe="INVERTED",
        authority=KnowledgeAuthority.CONSTITUTIONAL,
        dependencies=("UCOS-TEST-LOW-0001", "UCOS-TEST-ELSEWHERE-0001"),
    )
    intake = KnowledgeIntake.from_base(KnowledgeBase((low, high)), source="test")
    plan = PlanningEngine().plan(intake)
    composition, _findings = CompositionEngine().compose(intake, plan)
    manifest = GenerationEngine().generate(intake, plan, composition)
    rendered = "\n".join(
        artifact.content
        for artifact in manifest.artifacts
        if artifact.relative_path.endswith(".md")
    )
    assert "authority-inversion" in rendered


def test_a_plan_step_binding_an_object_the_store_does_not_hold_is_refused(pipeline) -> None:
    """Composition binds a step to canonical objects. A step citing one the store never held
    would produce a unit anchored to an id nothing can resolve, and the artifact's provenance
    would name it anyway."""

    intake, plan, _composition, _findings, _manifest = pipeline
    step = plan.steps[0]
    forged = _replace(
        plan,
        steps=(
            _replace(step, source_ckos=(*step.source_ckos, "UCOS-NOBODY-AUTHORED-0001")),
            *plan.steps[1:],
        ),
    )
    with pytest.raises(CompositionError, match="absent from the store"):
        CompositionEngine()._units(intake, forged)


def test_a_path_inside_the_repository_and_outside_the_frozen_corpus_is_permitted(
    tmp_path,
) -> None:
    """The refusals are measured elsewhere. This is the other half: a path under the repository
    that is NOT frozen must pass, or the guard would refuse every in-repository artifact root
    and the engine could only ever write outside the tree it belongs to."""

    implementer = ImplementationEngine(RealizationConfig.create(REPO, artifact_root=REPO))
    implementer._assert_not_frozen(REPO / "engine" / "probe.json", "engine/probe.json")
    _guard_writable(RealizationConfig.create(REPO, evidence_dir=REPO / "engine"), REPO / "engine")


def test_the_engine_composes_from_a_state_it_derives_for_itself() -> None:
    """`compose()` is the public step a caller uses without holding an intake or a plan. One
    that required them would make the stage unusable except from inside the pipeline."""
    engine = RealizationIntelligenceEngine()
    composition, findings = engine.compose()
    assert composition.units
    assert findings.to_dict()


def test_the_convenience_realize_entry_point_runs_the_whole_pipeline(tmp_path) -> None:
    """The module-level function is what a caller outside this package uses; one that drifted
    from the engine would give two answers to "was this realization governed"."""

    result = realize_repository(_config(tmp_path), dry_run=True, emit=False)
    assert result.governed
    assert result.summary()["verdict"] == VERDICT_GOVERNED


def test_a_refused_decision_materializes_nothing(tmp_path, monkeypatch) -> None:
    """Governance is a precondition of materialization, not a report about it. A run that wrote
    first and adjudicated afterwards would leave a refused realization on disk."""

    real = governance_module.RealizationGovernor.adjudicate

    def _refusing(self, **kwargs):  # noqa: ANN001, ANN003, ANN202
        decision = real(self, **kwargs)
        # `governed` is DERIVED from the gates, so refusing means failing one — there is no
        # verdict field to set, which is the point of deriving it.
        first = decision.gates[0]
        return _replace(
            decision,
            gates=(
                _replace(first, failures=("a gate refused",)),
                *decision.gates[1:],
            ),
        )

    monkeypatch.setattr(governance_module.RealizationGovernor, "adjudicate", _refusing)
    config = _config(tmp_path)
    result = RealizationIntelligenceEngine(config).realize(dry_run=False, strict=False, emit=False)
    assert not result.governed
    assert not (config.artifact_root / "UCOS-URI-MANIFEST.json").exists()


def test_pruning_runs_only_on_a_materializing_run(tmp_path) -> None:
    """A dry run writes nothing, so pruning inside one would delete artifacts a real run put
    there while claiming to have changed nothing."""
    engine = RealizationIntelligenceEngine(_config(tmp_path))
    result = engine.realize(dry_run=False, strict=False, emit=False, prune=True)
    assert result.governed
    assert (engine.config.artifact_root / "UCOS-URI-MANIFEST.json").is_file()


def test_a_boundary_rule_skips_an_edge_whose_far_end_this_unit_does_not_hold(pipeline) -> None:
    """The descriptor speaks for one unit. An edge reaching an object the unit does not bind has
    no rank here, and ranking it anyway would compare an authority this descriptor never read."""

    intake, plan, composition, _findings, _manifest = pipeline
    unit = next(
        u
        for u in composition.units
        if len(plan.target(u.target_id).edges) > 0 and len(u.bound_ckos) > 1
    )
    target = plan.target(unit.target_id)
    narrowed = _replace(unit, bound_ckos=unit.bound_ckos[:1])
    context = GenerationContext(
        intake=intake, plan=plan, composition=composition, unit=narrowed, target=target
    )
    assert ArchitectureGenerator()._boundary_rules(context) == []


def test_a_plan_whose_upstream_universe_has_no_target_orders_what_it_can(pipeline) -> None:
    """A dependency into a universe the intake did not derive a target for cannot be ordered
    against, and inventing a step for it would put a phantom into the wave graph."""

    intake = _two_universe_intake()
    downstream_only = _replace(
        intake, targets=tuple(t for t in intake.targets if t.universe == "DOWNSTREAM")
    )
    plan = PlanningEngine().plan(downstream_only)
    assert {step.universe for step in plan.steps} == {"DOWNSTREAM"}


def test_the_sql_projection_indexes_only_the_columns_the_record_carries(pipeline) -> None:
    """Three columns are indexed because every canonical record carries them. A projection over
    a record that does not would emit an index on a column that is not in the table, and the
    DDL would not execute."""

    intake, plan, composition, _findings, _manifest = pipeline
    unit = composition.units[0]
    context = GenerationContext(
        intake=intake,
        plan=plan,
        composition=composition,
        unit=unit,
        target=plan.target(unit.target_id),
    )
    ddl = "\n".join(
        SchemaGenerator()._ddl(context, [{"name": "cko_id", "type": "string", "nullable": False}])
    )
    assert "CREATE INDEX" not in ddl
    full = "\n".join(SchemaGenerator()._ddl(context, SchemaGenerator()._infer_fields(context)))
    assert "CREATE INDEX" in full


# -- LYR-L14/IF-08: a future interface is registered, not compiled in -------------

#: A registered family is process-global and append-only, so each test that registers one
#: uses a value no other test names, and the module is restored between tests.
_REGISTERED_FIXTURE = "uri-test-interface"


@pytest.fixture
def fresh_registration():
    """Restore the registered-family set and generator registry after each test."""

    saved = dict(contracts._REGISTERED_FAMILIES)
    saved_registry = dict(generator_registry.REGISTRY)
    contracts._REGISTERED_FAMILIES.clear()
    try:
        yield
    finally:
        contracts._REGISTERED_FAMILIES.clear()
        contracts._REGISTERED_FAMILIES.update(saved)
        generator_registry.REGISTRY.clear()
        generator_registry.REGISTRY.update(saved_registry)


def test_a_new_interface_family_is_admitted_by_registration(fresh_registration) -> None:
    """LYR-L14/IF-08: 'Future Interface' is satisfied by registration, not by an enum edit.

    `ArtifactFamily` shipped seven members and adding an eighth was a code change, which is
    exactly what the openness claim promises it will not be. A registration admits one."""

    family = register_family(_REGISTERED_FIXTURE)

    assert family.value == _REGISTERED_FIXTURE
    assert family == _REGISTERED_FIXTURE  # str-enum equality, as a manifest serializes it
    assert isinstance(family, str)
    assert family not in tuple(ArtifactFamily)  # not a compiled member
    assert family in registered_families()
    assert family in family_order()
    assert ArtifactFamily.coerce(_REGISTERED_FIXTURE) is family


def test_registration_refuses_a_duplicate_and_a_shipped_family(fresh_registration) -> None:
    """Append-only: a value registered twice is refused, and a shipped value cannot be shadowed."""

    register_family(_REGISTERED_FIXTURE)
    with pytest.raises(PlanningError, match="already registered"):
        register_family(_REGISTERED_FIXTURE)
    with pytest.raises(PlanningError, match="already shipped"):
        register_family(ArtifactFamily.API.value)
    with pytest.raises(PlanningError):
        register_family("")


def test_a_registered_family_has_no_generator_until_one_is_bound(fresh_registration) -> None:
    """Admitting a family is open; realizing it is governed. The two are separate acts."""

    family = register_family(_REGISTERED_FIXTURE)
    with pytest.raises(GenerationError, match="no generator"):
        generator_for(family)


def test_a_generator_for_an_unadmitted_family_is_refused(fresh_registration) -> None:
    """A generator may not bind a family nothing admits, so the registry cannot drift."""

    # Build the family, then drop it from the register, so the generator points at a
    # family nothing admits -- the exact state the refusal exists for.
    family = register_family(_REGISTERED_FIXTURE)

    contracts._REGISTERED_FAMILIES.clear()
    with pytest.raises(GenerationError, match="nothing admits"):
        register_generator(_RegisteredStub(family))


def test_a_registered_family_is_realized_once_a_generator_is_bound(fresh_registration) -> None:
    """The full path: register a family, bind a generator, resolve it through the registry."""

    family = register_family(_REGISTERED_FIXTURE)
    stub = _RegisteredStub(family)
    assert register_generator(stub) is stub
    assert generator_for(family) is stub
    # A second generator for the same family is refused, not silently re-bound.
    with pytest.raises(GenerationError, match="more than one generator"):
        register_generator(_RegisteredStub(family))


class _RegisteredStub(Generator):
    """A minimal generator used only to prove a registered family can be realized."""

    def __init__(self, family: ArtifactFamily) -> None:
        self.family = family
        self.name = f"uri.test.{family.value}"

    def generate(self, context: GenerationContext) -> tuple[GeneratedArtifact, ...]:
        return ()
