"""UAPF-000001 — tests for discovery, the work orchestrator, the platform façade and the CLI.

This is where the framework is tested as a whole rather than engine by engine. The claims:

* a pipeline — and a whole pipeline **category** — is admitted from a *declaration*, so the
  packaged canonical catalogue is discovered and derived with no code that knows about it;
* orchestration is autonomous, self-correcting (a blocked unit is re-promoted when its
  predecessor completes) and *bounded* (a run that cannot progress stops, and one that never
  stops is a reported finding rather than a hang);
* the composed platform reaches ``git``-comparable determinism: identical declarations produce
  an identical registry fingerprint, which is what a determinism gate compares.

The packaged catalogue is read here rather than in :mod:`platform.universal_pipeline.discovery`
because discovery is pure over its inputs by design; the filesystem lives in the CLI and in
tests.
"""

from __future__ import annotations

import json
from pathlib import Path
from platform.universal_pipeline import (
    GovernanceVerdict,
    PipelineAssurance,
    PipelineGovernance,
    PipelineQueueManager,
    PipelineRuntime,
    QueueEntry,
    RecoveryPoint,
    UniversalPipelineGateway,
    cli,
)
from platform.universal_pipeline.contracts import (
    PipelineDefinition,
    PipelineGateSpec,
    PipelineSecuritySpec,
    StageDefinition,
    pipeline_types,
)
from platform.universal_pipeline.discovery import (
    CATALOG_FORMAT,
    DiscoveryReport,
    PipelineDiscovery,
    load_catalog,
)
from platform.universal_pipeline.errors import (
    PipelineDiscoveryError,
    PipelineExceptionEscalation,
    PipelineGovernanceError,
    PipelineOrchestrationError,
    PipelinePlatformError,
    PipelineRegistryError,
    PipelineStateError,
    UniversalPipelineError,
)
from platform.universal_pipeline.events import PipelineEventBus
from platform.universal_pipeline.orchestrator import (
    DEFAULT_MAX_TICKS,
    OrchestrationTick,
    ReadinessContext,
    UniversalWorkOrchestrator,
    _handlers_resolvable,
    evaluate_readiness,
    readiness_predicate_names,
    register_readiness_predicate,
)
from platform.universal_pipeline.registry import PipelineRegistry
from platform.universal_pipeline.service import UniversalPipelinePlatform

import pytest

CANONICAL_CATALOG = (
    Path(__file__).resolve().parents[1] / "universal_pipeline" / "catalog" / "uapf-pipelines.json"
)


def _declaration(pipeline_id: str, pipeline_type: str = "evolution", **extra: object) -> dict:
    declaration: dict = {
        "pipeline_id": pipeline_id,
        "pipeline_type": pipeline_type,
        "version": "1.0.0",
        "stages": [{"stage_id": "only", "handler": "uapf.record"}],
    }
    declaration.update(extra)
    return declaration


def _catalog(*declarations: dict, **extra: object) -> str:
    document: dict = {"catalog_id": "test.catalog", "pipelines": list(declarations)}
    document.update(extra)
    return json.dumps(document)


# ----------------------------------------------------------------------------- discovery


def test_load_catalog_normalizes_text_and_mappings_alike() -> None:
    normalized = load_catalog(_catalog(_declaration("p")))
    assert normalized["catalog_id"] == "test.catalog"
    assert normalized["format"] == CATALOG_FORMAT
    assert len(normalized["pipelines"]) == 1
    assert normalized["pipeline_types"] == []
    assert load_catalog({"pipelines": []})["catalog_id"] == "uapf.catalog"


@pytest.mark.parametrize(
    ("document", "match"),
    [
        ("{not json", "not valid JSON"),
        ('["a list"]', "must be a mapping"),
        ("{}", "declares no 'pipelines' key"),
        ('{"pipelines": {}}', "'pipelines' must be a list"),
        ('{"pipelines": [], "pipeline_types": {}}', "'pipeline_types' must be a list"),
    ],
)
def test_a_malformed_catalogue_document_fails_closed(document: str, match: str) -> None:
    with pytest.raises(PipelineDiscoveryError, match=match):
        load_catalog(document)


def test_a_catalogue_may_introduce_a_whole_new_pipeline_category() -> None:
    registry = PipelineRegistry()
    report = PipelineDiscovery(registry).discover(
        _catalog(
            _declaration("p.novel", "test-catalogue-declared-category"),
            pipeline_types=[
                {
                    "pipeline_type": "test-catalogue-declared-category",
                    "description": "admitted by data, with no code change",
                }
            ],
        )
    )
    assert report.types_registered == ("test-catalogue-declared-category",)
    assert report.admitted == ("p.novel@1.0.0",)
    assert "test-catalogue-declared-category" in pipeline_types()
    assert report.clean
    report.require_clean()


def test_types_may_be_declared_as_bare_strings() -> None:
    registry = PipelineRegistry()
    report = PipelineDiscovery(registry).discover(
        _catalog(
            _declaration("p.bare", "test-bare-string-category"),
            pipeline_types=["test-bare-string-category"],
        )
    )
    assert report.types_registered == ("test-bare-string-category",)


def test_a_type_declaration_must_name_a_type() -> None:
    with pytest.raises(PipelineDiscoveryError, match="must name a type"):
        PipelineDiscovery(PipelineRegistry()).discover(
            _catalog(pipeline_types=[{"description": "no term"}])
        )


def test_re_reading_a_catalogue_admits_nothing_new() -> None:
    registry = PipelineRegistry()
    discovery = PipelineDiscovery(registry)
    document = _catalog(_declaration("p.idempotent"))
    first = discovery.discover(document)
    second = discovery.discover(document)
    assert first.admitted == ("p.idempotent@1.0.0",)
    assert second.admitted == ()
    assert second.already_registered == ("p.idempotent@1.0.0",)
    assert second.clean
    assert len(registry) == 1


def test_a_conflicting_redeclaration_at_one_version_is_refused() -> None:
    registry = PipelineRegistry()
    discovery = PipelineDiscovery(registry)
    discovery.discover(_catalog(_declaration("p.conflict")))
    changed = _declaration("p.conflict")
    changed["stages"] = [{"stage_id": "different", "handler": "uapf.record"}]
    report = discovery.discover(_catalog(changed))
    assert report.refused == (
        ("p.conflict@1.0.0", "a different declaration is already registered at this version"),
    )
    assert not report.clean
    with pytest.raises(PipelineDiscoveryError, match="refused declarations"):
        report.require_clean()


def test_one_malformed_declaration_does_not_lose_the_others() -> None:
    registry = PipelineRegistry()
    report = PipelineDiscovery(registry).discover(
        _catalog(
            _declaration("p.good"),
            _declaration("p.bad", "no-such-type-anywhere"),
            {"pipeline_id": "p.stageless", "pipeline_type": "evolution", "version": "1.0.0"},
            "not even a mapping",
            _declaration("p.also-good", "research"),
        )
    )
    assert report.admitted == ("p.good@1.0.0", "p.also-good@1.0.0")
    assert report.considered == 5
    refused = dict(report.refused)
    assert "p.bad@1.0.0" in refused
    assert "p.stageless@1.0.0" in refused
    assert "#3" in refused


def test_discovery_records_its_report_and_validates_construction() -> None:
    bus = PipelineEventBus()
    registry = PipelineRegistry()
    report = PipelineDiscovery(registry, bus=bus).discover(_catalog(_declaration("p.recorded")))
    assert len(bus.events_of("uapf.catalog.discovered")) == 1
    assert report.identity.kind == "discovery-report"
    assert report.fingerprint() == report.fingerprint()
    with pytest.raises(PipelineDiscoveryError, match="requires a PipelineRegistry"):
        PipelineDiscovery("registry")  # type: ignore[arg-type]
    with pytest.raises(PipelineDiscoveryError, match="must be a PipelineEventBus"):
        PipelineDiscovery(registry, bus="bus")  # type: ignore[arg-type]


def test_discovery_report_validates_its_own_shape() -> None:
    with pytest.raises(PipelineDiscoveryError, match="catalogue id is required"):
        DiscoveryReport(catalog_id="")
    with pytest.raises(PipelineDiscoveryError, match="admitted must be a tuple"):
        DiscoveryReport(catalog_id="c", admitted=["p"])  # type: ignore[arg-type]


# -------------------------------------------------------------- the canonical catalogue


def test_the_packaged_canonical_catalogue_is_discovered_and_derived() -> None:
    platform_instance = UniversalPipelinePlatform()
    report = platform_instance.discover(CANONICAL_CATALOG.read_text(encoding="utf-8"))
    report.require_clean()
    assert set(report.admitted) == {"uapf.evolution@1.0.0", "uapf.build@1.0.0"}
    evolution = platform_instance.registry.get("uapf.evolution")
    build = platform_instance.registry.get("uapf.build")
    # The mission names seventeen evolution acts and seventeen build acts.
    assert len(evolution.definition.stages) == 17
    assert len(build.definition.stages) == 17
    # The order is derived from the declared edges, not authored.
    assert evolution.plan.stages_in_wave(0) == ("context-assimilation",)
    assert evolution.plan.stage_ids[-1] == "implementation-readiness-assessment"
    assert "certification" in evolution.definition.stage_ids
    # Nothing may be registered before it is certified.
    plan_order = list(evolution.plan.stage_ids)
    assert plan_order.index("certification") < plan_order.index("canonical-registration")
    # The seven synchronization projections are independent and share one wave.
    assert len(build.plan.stages_in_wave(7)) == 8
    assert build.plan.stage_ids[-1] == "execute-verify-sh"
    # The inter-pipeline dependency is derived from the capability declarations.
    assert platform_instance.registry.pipeline_dependencies()["uapf.build"] == ("uapf.evolution",)
    assert platform_instance.registry.unsatisfied_capabilities() == ()
    platform_instance.require_intact()


# -------------------------------------------------------------------------- orchestrator


def _platform(**kwargs: object) -> UniversalPipelinePlatform:
    platform_instance = UniversalPipelinePlatform(**kwargs)  # type: ignore[arg-type]
    platform_instance.register(
        PipelineDefinition(
            pipeline_id="test.orchestrated",
            pipeline_type="implementation",
            version="1.0.0",
            stages=(
                StageDefinition(stage_id="a", handler="uapf.record"),
                StageDefinition(stage_id="b", handler="uapf.record", requires=("a",)),
            ),
        )
    )
    return platform_instance


def test_the_three_seeded_readiness_predicates_are_registered() -> None:
    assert {
        "p1.dependencies-complete",
        "p2.pipeline-registered",
        "p4.handlers-resolvable",
    } <= set(readiness_predicate_names())


def test_orchestration_is_autonomous_and_self_correcting() -> None:
    platform_instance = _platform()
    platform_instance.admit_unit("first", "test.orchestrated", wave=1)
    platform_instance.admit_unit("second", "test.orchestrated", wave=2, depends_on=("first",))
    ticks = platform_instance.run()
    # Tick 0 promotes and certifies the root, and blocks the dependent one.
    assert ticks[0].promoted == ("first",)
    assert ticks[0].certified == ("first",)
    assert [unit for unit, _reason in ticks[0].blocked] == ["second"]
    # Tick 1 re-promotes the previously blocked unit, because its predecessor completed.
    assert ticks[1].promoted == ("second",)
    assert ticks[1].certified == ("second",)
    # The run stops as soon as a tick cannot progress.
    assert not ticks[-1].progressed
    assert platform_instance.assurance.is_certified("first")
    assert platform_instance.assurance.is_certified("second")
    assert [e.unit_id for e in platform_instance.queue.completed] == ["first", "second"]
    platform_instance.require_intact()


def test_a_permanently_blocked_unit_terminates_the_run_rather_than_hanging() -> None:
    platform_instance = _platform()
    platform_instance.admit_unit("orphaned", "test.orchestrated", depends_on=("never-admitted",))
    ticks = platform_instance.run()
    assert not ticks[-1].progressed
    assert [e.unit_id for e in platform_instance.queue.blocked_set] == ["orphaned"]
    # Still blocked on the next tick, and still reported as no progress — not as new work.
    assert platform_instance.tick().progressed is False


def test_readiness_reports_which_predicate_failed() -> None:
    platform_instance = _platform()
    platform_instance.admit_unit("waiting", "test.orchestrated", depends_on=("absent",))
    assert platform_instance.orchestrator.readiness("waiting") == ("p1.dependencies-complete",)
    platform_instance.admit_unit("ready", "test.orchestrated")
    assert platform_instance.orchestrator.readiness("ready") == ()


def test_a_registered_predicate_tightens_readiness_everywhere() -> None:
    def refuses_everything(context: ReadinessContext) -> bool:
        return context.unit_id != "test-blocked-by-custom-predicate"

    register_readiness_predicate("test.custom-predicate", refuses_everything, "a test predicate")
    platform_instance = _platform()
    platform_instance.admit_unit("test-blocked-by-custom-predicate", "test.orchestrated")
    assert platform_instance.orchestrator.readiness("test-blocked-by-custom-predicate") == (
        "test.custom-predicate",
    )
    ticks = platform_instance.run()
    assert [unit for unit, _r in ticks[0].blocked] == ["test-blocked-by-custom-predicate"]


def test_readiness_predicates_are_validated_and_append_only() -> None:
    with pytest.raises(PipelineOrchestrationError, match="must be callable"):
        register_readiness_predicate("test.not-callable", "nope")  # type: ignore[arg-type]
    register_readiness_predicate("test.duplicate-predicate", lambda context: True)
    with pytest.raises(PipelineOrchestrationError, match="already registered"):
        register_readiness_predicate("test.duplicate-predicate", lambda context: True)


def test_a_unit_naming_an_unresolvable_handler_is_blocked_not_dispatched() -> None:
    platform_instance = UniversalPipelinePlatform()
    platform_instance.register(
        PipelineDefinition(
            pipeline_id="test.unresolvable",
            pipeline_type="implementation",
            version="1.0.0",
            stages=(StageDefinition(stage_id="s", handler="test.handler.does-not-exist-anywhere"),),
        )
    )
    platform_instance.admit_unit("u", "test.unresolvable")
    assert platform_instance.orchestrator.readiness("u") == ("p4.handlers-resolvable",)
    context = ReadinessContext(
        entry=platform_instance.queue.entry("u"), registry=platform_instance.registry
    )
    assert "p4.handlers-resolvable" in evaluate_readiness(context)


def test_a_failing_unit_is_retried_and_then_escalated_never_dropped() -> None:
    platform_instance = UniversalPipelinePlatform(max_retry=2)
    platform_instance.register(
        PipelineDefinition(
            pipeline_id="test.always-fails",
            pipeline_type="implementation",
            version="1.0.0",
            stages=(
                StageDefinition(
                    stage_id="gate",
                    handler="uapf.gate",
                    gates=(PipelineGateSpec("G", "never.supplied"),),
                ),
            ),
        )
    )
    platform_instance.admit_unit("doomed", "test.always-fails")
    ticks = platform_instance.run()
    failed_units = [unit for tick in ticks for unit, _reason in tick.failed]
    escalated = [unit for tick in ticks for unit, _reason in tick.escalated]
    retried = [unit for tick in ticks for unit in tick.retried]
    assert failed_units.count("doomed") == 3  # initial attempt plus two retries
    assert retried.count("doomed") == 2
    assert escalated == ["doomed"]
    assert platform_instance.queue.entry("doomed").state == "ARCHIVED"
    assert len(platform_instance.bus.events_of("uapf.escalation.raised")) == 1


def test_escalation_is_the_single_autonomy_exit_and_names_its_reason() -> None:
    platform_instance = _platform()
    with pytest.raises(PipelineExceptionEscalation, match="human intervention required"):
        platform_instance.orchestrator.escalate("subject", "constitutional-ambiguity")
    assert len(platform_instance.bus.events_of("uapf.escalation.raised")) == 1
    with pytest.raises(PipelineStateError, match="unknown escalation reason"):
        platform_instance.orchestrator.escalate("subject", "i-felt-like-it")


def test_a_run_that_never_stops_is_a_reported_finding() -> None:
    """Reaching the bound while still progressing is a finding, never a silent truncation.

    Provoked with a real workload rather than a globally-refusing predicate: the readiness
    vocabulary is process-wide, so a predicate that refused everything would silently block
    every other test in this process — exactly the coupling the one-namespace design implies
    and a test must respect.
    """
    platform_instance = _platform()
    platform_instance.admit_unit("first", "test.orchestrated", wave=1)
    platform_instance.admit_unit("second", "test.orchestrated", wave=2, depends_on=("first",))
    # Tick 0 certifies "first" and blocks "second", so it progressed and work remains.
    with pytest.raises(PipelineOrchestrationError, match="bound reached while still making") as e:
        platform_instance.run(max_ticks=1)
    assert e.value.context["max_ticks"] == 1


def test_orchestration_bound_is_validated() -> None:
    platform_instance = _platform()
    with pytest.raises(PipelineOrchestrationError, match="max_ticks must be a positive integer"):
        platform_instance.run(max_ticks=0)
    assert DEFAULT_MAX_TICKS > 0


def test_orchestrator_construction_is_validated() -> None:
    platform_instance = _platform()
    with pytest.raises(PipelineOrchestrationError, match="requires a"):
        UniversalWorkOrchestrator(
            "registry",  # type: ignore[arg-type]
            platform_instance.queue,
            platform_instance.gateway,
            platform_instance.runtime,
            platform_instance.assurance,
        )
    with pytest.raises(PipelineOrchestrationError, match="max_batch must be a positive integer"):
        UniversalWorkOrchestrator(
            platform_instance.registry,
            platform_instance.queue,
            platform_instance.gateway,
            platform_instance.runtime,
            platform_instance.assurance,
            max_batch=0,
        )


def test_a_batch_cap_limits_how_much_one_tick_dispatches() -> None:
    platform_instance = _platform(max_batch=1)
    platform_instance.admit_unit("one", "test.orchestrated")
    platform_instance.admit_unit("two", "test.orchestrated")
    first = platform_instance.tick()
    assert len(first.cut) == 1
    assert len(platform_instance.tick().cut) == 1


def test_stage_inputs_may_be_supplied_per_unit_per_tick() -> None:
    platform_instance = _platform()
    platform_instance.admit_unit("u", "test.orchestrated")
    tick = platform_instance.tick(inputs={"u": {"supplied": True}})
    assert tick.certified == ("u",)


def test_tick_evidence_is_deterministic_and_validated() -> None:
    tick = OrchestrationTick(index=0, promoted=("u",))
    assert tick.progressed
    assert tick.identity.kind == "orchestration-tick"
    assert tick.fingerprint() == OrchestrationTick(index=0, promoted=("u",)).fingerprint()
    assert tick.to_dict()["promoted"] == ["u"]
    assert not OrchestrationTick(index=1).progressed
    with pytest.raises(PipelineOrchestrationError, match="non-negative integer"):
        OrchestrationTick(index=-1)


# ----------------------------------------------------------------------- platform façade


def test_the_façade_exposes_every_engine_rather_than_wrapping_it() -> None:
    platform_instance = _platform()
    assert platform_instance.registry is platform_instance.orchestrator._registry  # noqa: SLF001
    for attribute in (
        "bus",
        "registry",
        "queue",
        "dependencies",
        "scheduler",
        "governance",
        "assurance",
        "observability",
        "gateway",
        "runtime",
        "discovery",
        "orchestrator",
    ):
        assert getattr(platform_instance, attribute) is not None
    assert platform_instance.identity.kind == "platform"


def test_the_façade_synchronizes_every_declared_dimension() -> None:
    platform_instance = _platform()
    platform_instance.admit_unit("u", "test.orchestrated")
    platform_instance.run()
    state = platform_instance.state()
    for dimension in (
        "identity",
        "taxonomy",
        "ontology",
        "registries",
        "dependency_graph",
        "queues",
        "governance",
        "assurance",
        "observability",
        "gateway",
        "orchestration",
        "evidence",
    ):
        assert dimension in state
    assert state["ontology"]["lifecycle"]["authority"] == "06-IMPLEMENTATION-STATE-MACHINE.md"
    summary = platform_instance.summary()
    assert summary["certified"] == 1
    assert summary["completed"] == 1
    assert summary["health"] == "HEALTHY"
    assert summary["fingerprint"] == platform_instance.fingerprint()


def test_registering_a_type_through_the_façade_is_idempotent() -> None:
    platform_instance = UniversalPipelinePlatform()
    platform_instance.register_type("test-facade-type", "registered once")
    platform_instance.register_type("test-facade-type", "again, harmlessly")
    assert "test-facade-type" in pipeline_types()


def test_admitting_a_unit_requires_a_registered_pipeline_and_happens_once() -> None:
    platform_instance = _platform()
    with pytest.raises(PipelineRegistryError, match="no such pipeline registered"):
        platform_instance.admit_unit("u", "never.registered")
    platform_instance.admit_unit("u", "test.orchestrated")
    with pytest.raises(PipelinePlatformError, match="already admitted"):
        platform_instance.admit_unit("u", "test.orchestrated")


def test_the_relationship_graph_holds_pipelines_and_units_in_two_namespaces() -> None:
    platform_instance = _platform()
    platform_instance.admit_unit("u", "test.orchestrated")
    nodes = platform_instance.dependencies.node_ids
    assert "u" in nodes
    assert "pipeline:test.orchestrated" in nodes
    schedule = platform_instance.schedule()
    assert "u" in schedule.unit_ids
    assert "pipeline:test.orchestrated" in schedule.unit_ids
    assert len(platform_instance.bus.events_of("uapf.dependency.declared")) == 1


def test_the_façade_submits_through_the_gateway() -> None:
    platform_instance = _platform()
    transaction = platform_instance.submit("test.orchestrated", "u", inputs={"a": 1})
    assert transaction.verify()


def test_façade_construction_is_validated() -> None:
    with pytest.raises(PipelinePlatformError, match="max_batch must be a positive integer"):
        UniversalPipelinePlatform(max_batch=0)
    with pytest.raises(PipelinePlatformError, match="max_retry must be a non-negative integer"):
        UniversalPipelinePlatform(max_retry=-1)
    assert UniversalPipelinePlatform(source="TEST").bus.source == "TEST"


def test_an_empty_platform_is_intact() -> None:
    """An empty relationship graph is trivially valid, and must not be reported otherwise."""
    UniversalPipelinePlatform().require_intact()


def test_identical_declarations_produce_an_identical_derived_registry() -> None:
    document = CANONICAL_CATALOG.read_text(encoding="utf-8")
    left, right = UniversalPipelinePlatform(), UniversalPipelinePlatform()
    left.discover(document)
    right.discover(document)
    assert left.registry.fingerprint() == right.registry.fingerprint()
    assert left.dependencies.fingerprint() == right.dependencies.fingerprint()


# ------------------------------------------------------------------------------- the CLI


def test_the_cli_gate_opens_on_the_canonical_catalogue(capsys) -> None:
    assert cli.CANONICAL_CATALOG == CANONICAL_CATALOG
    assert cli.main(["--gate"]) == cli.EXIT_OPEN
    captured = capsys.readouterr()
    assert "UAPF-000001: OPEN" in captured.out
    assert "pipelines=2" in captured.out
    assert "stages=34" in captured.out


def test_the_cli_reports_the_derived_catalogue_by_default(capsys) -> None:
    assert cli.main([]) == cli.EXIT_OPEN
    reported = json.loads(capsys.readouterr().out)
    assert reported["catalog_id"] == "uapf.canonical"
    assert {p["pipeline_id"] for p in reported["pipelines"]} == {
        "uapf.evolution",
        "uapf.build",
    }
    assert reported["pipeline_dependencies"]["uapf.build"] == ["uapf.evolution"]


def test_the_cli_prints_the_taxonomy_and_the_state(capsys) -> None:
    assert cli.main(["--taxonomy"]) == cli.EXIT_OPEN
    taxonomy = json.loads(capsys.readouterr().out)
    assert "evolution" in taxonomy["pipeline_types"]
    assert "uapf.record" in taxonomy["stage_handlers"]
    assert cli.main(["--state"]) == cli.EXIT_OPEN
    state = json.loads(capsys.readouterr().out)
    assert state["registries"]["entry_count"] == 2


def test_the_cli_proves_the_derived_registry_is_reproducible(capsys) -> None:
    assert cli.main(["--check-determinism"]) == cli.EXIT_OPEN
    result = json.loads(capsys.readouterr().out)
    assert result["identical"] is True
    assert result["first"] == result["second"]


def test_the_cli_gate_closes_on_a_catalogue_with_findings(tmp_path: Path, capsys) -> None:
    catalog = tmp_path / "findings.json"
    catalog.write_text(
        _catalog(
            _declaration("p.good"),
            _declaration("p.bad", "no-such-type-at-all"),
        ),
        encoding="utf-8",
    )
    assert cli.main(["--catalog", str(catalog), "--gate"]) == cli.EXIT_CLOSED
    captured = capsys.readouterr()
    assert "UAPF-000001: CLOSED" in captured.out
    assert "declaration refused" in captured.err


def test_the_cli_gate_reports_an_unsatisfied_capability(tmp_path: Path, capsys) -> None:
    catalog = tmp_path / "unsatisfied.json"
    catalog.write_text(
        _catalog(
            _declaration(
                "p.consumer",
                capabilities=[
                    {
                        "capability_id": "cap.nobody-provides",
                        "contract": {"name": "c"},
                        "direction": "requires",
                    }
                ],
            )
        ),
        encoding="utf-8",
    )
    assert cli.main(["--catalog", str(catalog), "--gate"]) == cli.EXIT_CLOSED
    assert "unsatisfied capability" in capsys.readouterr().err


def test_the_cli_gate_closes_on_an_empty_catalogue(tmp_path: Path, capsys) -> None:
    catalog = tmp_path / "empty.json"
    catalog.write_text(_catalog(), encoding="utf-8")
    assert cli.main(["--catalog", str(catalog), "--gate"]) == cli.EXIT_CLOSED
    assert "declared no pipelines" in capsys.readouterr().err


def test_the_cli_gate_reports_an_unresolvable_handler(tmp_path: Path, capsys) -> None:
    catalog = tmp_path / "handler.json"
    declaration = _declaration("p.unresolvable")
    declaration["stages"] = [{"stage_id": "s", "handler": "test.handler.absent-from-registry"}]
    catalog.write_text(_catalog(declaration), encoding="utf-8")
    assert cli.main(["--catalog", str(catalog), "--gate"]) == cli.EXIT_CLOSED
    assert "unresolvable handler" in capsys.readouterr().err


def test_the_cli_aborts_on_an_unreadable_or_malformed_catalogue(tmp_path: Path, capsys) -> None:
    assert cli.main(["--catalog", str(tmp_path / "absent.json")]) == cli.EXIT_ABORT
    assert "could not be read" in capsys.readouterr().err
    malformed = tmp_path / "malformed.json"
    malformed.write_text("{not json", encoding="utf-8")
    assert cli.main(["--catalog", str(malformed)]) == cli.EXIT_ABORT
    assert "ABORT" in capsys.readouterr().err


def test_the_cli_determinism_check_aborts_on_an_unreadable_catalogue(tmp_path: Path) -> None:
    with pytest.raises(OSError):
        cli.check_determinism(tmp_path / "absent.json")


def test_the_cli_security_declaration_is_honoured_by_the_gate(tmp_path: Path) -> None:
    """A pipeline declaring a permission is still admissible to the registry and the gate."""
    catalog = tmp_path / "secure.json"
    catalog.write_text(
        _catalog(_declaration("p.secure", security=PipelineSecuritySpec(("execute",)).to_dict())),
        encoding="utf-8",
    )
    assert cli.main(["--catalog", str(catalog), "--gate"]) == cli.EXIT_OPEN


# -------------------------------------------------------------- orchestration evidence


def test_orchestration_history_is_readable_and_fingerprints_deterministically() -> None:
    """THE TICK LOG IS THE EVIDENCE THAT AUTONOMY WAS GOVERNED.

    ``ticks`` is how a reader replays what the orchestrator decided and ``fingerprint`` is
    what an external gate compares against a sealed expectation. Neither had a caller, so a
    history could have gone empty, gone unordered, or stopped hashing deterministically with
    no failure — and the whole claim of self-correcting orchestration rests on being able to
    read back what it corrected.
    """
    platform_instance = _platform()
    platform_instance.admit_unit("first", "test.orchestrated", wave=1)
    platform_instance.run()

    orchestrator = platform_instance.orchestrator
    assert orchestrator.ticks
    assert [tick.index for tick in orchestrator.ticks] == list(range(len(orchestrator.ticks)))
    assert orchestrator.to_dict()["tick_count"] == len(orchestrator.ticks)

    assert orchestrator.fingerprint() == orchestrator.fingerprint()
    assert len(orchestrator.fingerprint()) == 64


def test_the_handler_predicate_short_circuits_on_an_unregistered_pipeline() -> None:
    """P4 ASKS ABOUT HANDLERS, AND A UNIT WITH NO PIPELINE HAS NO STAGES TO ASK ABOUT.

    The predicate short-circuits on registration rather than looking the pipeline up and
    raising. ``admit_unit`` refuses an unregistered pipeline outright, so this state arises
    from a registry that lost the definition after admission — and without the short-circuit
    a readiness question would become a registry error, aborting the tick instead of
    reporting the unit as blocked.
    """

    platform_instance = _platform()
    platform_instance.admit_unit("admitted", "test.orchestrated")
    entry = platform_instance.queue.entry("admitted")

    class _Forgetful:
        """A registry that holds nothing. Membership is asked with ``in``, so that is
        the one operator the stand-in has to answer."""

        @staticmethod
        def __contains__(_key: object) -> bool:
            return False

        def __getattr__(self, name: str):
            return getattr(platform_instance.registry, name)

    context = ReadinessContext(entry=entry, registry=_Forgetful())
    assert _handlers_resolvable(context) is False


def test_a_failed_unit_is_retried_only_while_its_budget_and_readiness_both_hold() -> None:
    """TWO GUARDS ON RETRY, and each skips a different unit.

    R1–R3: a unit that has exhausted its attempts is not retried, or a permanently failing
    unit would be re-queued forever and the run would never stop making "progress". A unit
    still within budget but no longer READY is not retried either — re-queueing it would put
    a unit into the ready set that the readiness predicates have just refused.
    """
    platform_instance = _platform(max_retry=1)
    platform_instance.admit_unit("exhausted", "test.orchestrated")
    platform_instance.admit_unit("unready", "test.orchestrated", depends_on=("never-admitted",))

    queue = platform_instance.queue
    for unit_id in ("exhausted", "unready"):
        queue.promote(unit_id)
        queue.advance(unit_id, "EXECUTING")
        queue.fail(unit_id, reason="deliberate")

    # Spend the retry budget so the FIRST guard refuses this one.
    queue.retry("exhausted")
    queue.advance("exhausted", "EXECUTING")
    queue.fail("exhausted", reason="deliberate again")
    assert queue.entry("exhausted").attempts >= 1

    tick = platform_instance.tick()

    # "exhausted" is out of budget; "unready" is within it and fails readiness.
    assert "exhausted" not in tick.retried
    assert "unready" not in tick.retried


# ------------------------------------------------------------------- governance evidence


def test_a_governance_verdict_mints_its_own_identity_from_its_own_content() -> None:
    """A VERDICT IS EVIDENCE, so it carries an identity derived from what it decided.

    The fingerprint hashes the subject, the outcome and the obligations considered and
    discharged — not the findings prose, which is why two verdicts that decided the same
    thing for the same subject are one artifact. Neither the identity nor the fingerprint had
    a caller, so an identity that stopped being a function of the decision would have gone
    unnoticed by everything that stores one.
    """

    verdict = GovernanceVerdict(
        subject="unit",
        approved=True,
        considered=("o1", "o2"),
        discharged=("o1", "o2"),
        undischarged=(),
        findings=(),
    )
    same = GovernanceVerdict(
        subject="unit",
        approved=True,
        considered=("o1", "o2"),
        discharged=("o1", "o2"),
        undischarged=(),
        findings=(),
    )
    other = GovernanceVerdict(
        subject="other",
        approved=True,
        considered=("o1", "o2"),
        discharged=("o1", "o2"),
        undischarged=(),
        findings=(),
    )

    assert verdict.fingerprint() == same.fingerprint()
    assert verdict.fingerprint() != other.fingerprint()
    assert verdict.identity.value
    assert verdict.identity.value == same.identity.value
    assert verdict.identity.value != other.identity.value


def test_a_recovery_point_must_name_the_subject_it_recovers() -> None:
    """A recovery point with no subject is a resumption target attached to nothing — it
    would be recorded, found by nothing, and the recovery it promises could never be run."""

    for nameless in ("", None, 7):
        with pytest.raises(PipelineGovernanceError, match="subject is required"):
            RecoveryPoint(subject=nameless, state="READY", checkpoint="h", ordinal=0)


def test_the_governance_ledger_lists_the_recovery_points_it_holds() -> None:
    """``recovery_points`` is the audit trail a reader replays a recovery from, and it had no
    caller — so "which points exist" was answerable only by asking for the latest one by
    subject, which cannot tell you what other subjects were recorded."""

    governance = PipelineGovernance()
    governance.record_recovery_point("first", "READY", detail={"stage": "a"})
    governance.record_recovery_point("second", "EXECUTING", detail={"stage": "b"})

    points = governance.recovery_points
    assert [p.subject for p in points] == ["first", "second"]
    assert [p.ordinal for p in points] == [0, 1]
    assert governance.latest_recovery_point("first").detail["stage"] == "a"


def test_the_orchestrator_runs_without_a_bus_governance_or_observability() -> None:
    """THE THREE OPTIONAL COLLABORATORS ARE OPTIONAL, and the platform supplies all three —
    which is why every ``is not None`` arm was tested on only one side.

    An orchestrator composed without them must still promote, execute, certify and record
    ticks: the event bus, the governance ledger and the observability sink are places a run
    is REPORTED to, not things a run depends on. If any of them were load-bearing, a caller
    composing a minimal orchestrator would get an AttributeError instead of a run.
    """

    registry = PipelineRegistry()
    registry.register(
        PipelineDefinition(
            pipeline_id="test.bare",
            pipeline_type="implementation",
            version="1.0.0",
            stages=(StageDefinition(stage_id="a", handler="uapf.record"),),
        )
    )
    queue = PipelineQueueManager()
    assurance = PipelineAssurance()
    gateway = UniversalPipelineGateway(registry)
    runtime = PipelineRuntime(registry, queue=queue)
    orchestrator = UniversalWorkOrchestrator(registry, queue, gateway, runtime, assurance)

    queue.enqueue(QueueEntry(unit_id="bare-unit", pipeline_id="test.bare", version="1.0.0"))

    tick = orchestrator.tick()

    assert "bare-unit" in tick.promoted
    assert orchestrator.ticks
    assert orchestrator.fingerprint()


def test_a_unit_that_executes_but_does_not_certify_is_implemented_and_not_certified() -> None:
    """IMPLEMENTED AND CERTIFIED ARE TWO FACTS, and the tick reports them separately.

    A unit whose stages ran is implemented; a unit whose assurance chain completed is
    certified. They normally move together, which is why the loop's "implemented but not
    certified" arm was dead — and treating them as one would let a tick report a unit as
    certified because its stages happened to run, which is the whole thing certification is
    supposed to be independent of.
    """

    registry = PipelineRegistry()
    registry.register(
        PipelineDefinition(
            pipeline_id="test.uncertified",
            pipeline_type="implementation",
            version="1.0.0",
            stages=(StageDefinition(stage_id="a", handler="uapf.record"),),
        )
    )
    queue = PipelineQueueManager()

    class _NeverCertified(PipelineAssurance):
        def is_certified(self, subject: str) -> bool:
            return False

    assurance = _NeverCertified()
    orchestrator = UniversalWorkOrchestrator(
        registry,
        queue,
        UniversalPipelineGateway(registry),
        PipelineRuntime(registry, queue=queue),
        assurance,
    )
    queue.enqueue(
        QueueEntry(unit_id="uncertified", pipeline_id="test.uncertified", version="1.0.0")
    )

    ticks = [orchestrator.tick(), orchestrator.tick()]
    implemented = [t for t in ticks if t.implemented]

    assert implemented, [t.to_dict() for t in ticks]
    assert "uncertified" in implemented[0].implemented
    assert "uncertified" not in implemented[0].certified


def test_a_declaration_the_registry_refuses_is_reported_and_the_rest_are_admitted() -> None:
    """ONE BAD DECLARATION MUST NOT LOSE THE OTHERS — the same discipline the catalogue
    parser already keeps, applied one layer down at REGISTRATION.

    The parser refuses a malformed declaration; this is the arm for a declaration that
    parses and the registry still refuses — a version collision, an unsatisfiable capability.
    It is recorded in ``refused`` with the registry's own code and message, and discovery
    continues, so one collision does not cost a whole catalogue.
    """

    registry = PipelineRegistry()

    # `PipelineDiscovery` type-checks its registry and `PipelineRegistry` is slotted, so
    # the refusal is installed on the CLASS for the duration of the call.
    def refusing(_self, _definition):
        raise PipelineRegistryError("the registry refuses this one", pipeline_id="x")

    discovery = PipelineDiscovery(registry)
    original = PipelineRegistry.register
    try:
        PipelineRegistry.register = refusing  # type: ignore[method-assign]
        report = discovery.discover(_catalog(_declaration("test.refused")))
    finally:
        PipelineRegistry.register = original  # type: ignore[method-assign]

    assert report.admitted == ()
    assert report.refused
    assert "the registry refuses this one" in report.refused[0][1]


def test_the_platform_reports_an_integrity_fault_as_a_named_failure() -> None:
    """THE CLI TURNS EVERY REFUSAL INTO A LINE, INCLUDING THE ONE FROM ITS OWN INTEGRITY
    CHECK.

    ``require_intact`` raises; the report must not. A caller reading the CLI's failure list
    is looking for everything wrong with the catalogue at once, and an exception escaping
    from the integrity step would end the report at that point with the remaining checks
    unrun — the same partial-answer problem the refusal list exists to avoid.
    """

    platform_instance = _platform()

    class _Broken:
        @staticmethod
        def require_intact() -> None:
            raise UniversalPipelineError("recorded history is not intact")

        def __getattr__(self, name: str):
            return getattr(platform_instance, name)

    report = platform_instance.discover(_catalog(_declaration("test.integrity")))
    failures = cli.gate(_Broken(), report)
    assert any("integrity:" in line for line in failures)
    assert any("recorded history is not intact" in line for line in failures)


def _bare_orchestrator(
    pipeline: PipelineDefinition, *, bind_queue: bool = True, **kwargs: object
) -> tuple[UniversalWorkOrchestrator, object]:
    """An orchestrator composed WITHOUT a bus and over a queue-less runtime.

    Every other orchestration test here goes through :class:`UniversalPipelinePlatform`,
    which always composes a bus and always binds the runtime to the queue — so the optional
    arms of both are never taken by the suite even though they are the documented default
    for a runtime used in isolation.
    """

    registry = PipelineRegistry()
    registry.register(pipeline)
    queue = PipelineQueueManager()
    orchestrator = UniversalWorkOrchestrator(
        registry,
        queue,
        UniversalPipelineGateway(registry),
        PipelineRuntime(registry, queue=queue if bind_queue else None),
        PipelineAssurance(),
        bus=None,
        **kwargs,  # type: ignore[arg-type]
    )
    return orchestrator, queue


def test_the_orchestrator_makes_the_implemented_transition_a_queue_less_runtime_never_made() -> (
    None
):
    """A UNIT REACHES VALIDATED FROM IMPLEMENTED OR IT DOES NOT REACH IT AT ALL.

    The runtime drives the lifecycle only when it is bound to the queue, and the platform
    always binds it — so by the time assurance ran, the unit had already left ``EXECUTING``
    and the orchestrator's own transition was dead code in every test. It is not dead in
    use: a runtime composed in isolation (the documented, testable-in-isolation form) leaves
    the unit in ``EXECUTING``, and ``EXECUTING → VALIDATED`` is not a legal transition, so
    without this the whole tick would fail closed on a lifecycle refusal.
    """

    orchestrator, queue = _bare_orchestrator(
        PipelineDefinition(
            pipeline_id="test.queue-less-runtime",
            pipeline_type="implementation",
            version="1.0.0",
            stages=(StageDefinition(stage_id="a", handler="uapf.record"),),
        ),
        bind_queue=False,
    )
    queue.enqueue(
        QueueEntry(unit_id="unbound", pipeline_id="test.queue-less-runtime", version="1.0.0")
    )

    tick = orchestrator.tick()

    assert "unbound" in tick.implemented
    assert "unbound" in tick.certified
    assert queue.entry("unbound").state == "CERTIFIED"


def test_escalation_and_exhaustion_are_unchanged_when_no_bus_is_composed() -> None:
    """THE BUS RECORDS AN ESCALATION; IT DOES NOT DECIDE ONE.

    Both escalation paths emit before they act, and both are guarded because the bus is
    optional — but every escalation test runs against the platform, which always has one, so
    the unguarded case had never executed. If either emission were unconditional, composing
    the orchestrator without a bus would turn an exhausted retry budget and the single
    autonomy exit into an ``AttributeError`` raised from inside the halt itself: the two
    moments where a clear failure matters most.
    """

    orchestrator, queue = _bare_orchestrator(
        PipelineDefinition(
            pipeline_id="test.bus-less-doomed",
            pipeline_type="implementation",
            version="1.0.0",
            stages=(
                StageDefinition(
                    stage_id="gate",
                    handler="uapf.gate",
                    gates=(PipelineGateSpec("G", "never.supplied"),),
                ),
            ),
        ),
        max_retry=1,
    )
    queue.enqueue(QueueEntry(unit_id="doomed", pipeline_id="test.bus-less-doomed", version="1.0.0"))

    ticks = orchestrator.run()
    escalated = [unit for tick in ticks for unit, _reason in tick.escalated]

    assert escalated == ["doomed"]
    assert queue.entry("doomed").state == "ARCHIVED"

    with pytest.raises(PipelineExceptionEscalation, match="human intervention required"):
        orchestrator.escalate("subject", "constitutional-ambiguity")
