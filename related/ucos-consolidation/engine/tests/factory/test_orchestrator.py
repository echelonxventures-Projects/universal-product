"""TASK-000045 — Generation orchestrator tests (TASK-000041/000042)."""

from __future__ import annotations

import json

import pytest

from engine.factory.contracts import FactoryRequest, GenerationStatus
from engine.factory.errors import BlueprintResolutionError

# -- BP-DATA: full, real generation -------------------------------------------


def test_generate_bp_data_produces_real_artifacts(orchestrator):
    result = orchestrator.generate(FactoryRequest("BP-DATA-0001"))
    assert result.status is GenerationStatus.GENERATED
    assert result.success is True
    assert result.blueprint_class == "BP-DATA"
    assert result.factory_name == "data-factory"
    assert result.artifact_id.startswith("UCOS-CMP-BP-DATA-0001-")
    assert result.runtime_id.startswith("UCOS-RUN-BP-DATA-0001-")
    assert result.package_sha256
    assert result.image_reference.startswith("ucos-runtime/bp-data-0001@sha256:")
    assert result.disclosure_present is True
    assert result.gap is None


def test_generate_records_evidence(orchestrator):
    result = orchestrator.generate(FactoryRequest("BP-DATA-0001"))
    evidence = result.evidence
    assert evidence["blueprint"]["blueprint_id"] == "BP-DATA-0001"
    assert evidence["classification"]["blueprint_class"] == "BP-DATA"
    assert evidence["compiler_artifact"]["artifact_id"] == result.artifact_id
    assert evidence["runtime_artifact"]["runtime_id"] == result.runtime_id
    assert evidence["disclosure_state"]["present"] is True
    assert evidence["disclosure_state"]["gate"] == "EC-1"


# -- BP-API / BP-SERVICE / BP-APPLICATION: classified, routed, faithful gap ----


@pytest.mark.parametrize(
    ("blueprint_id", "blueprint_class", "factory_name"),
    [
        ("BP-API-0001", "BP-API", "api-factory"),
        ("BP-EVENT-0001", "BP-EVENT", "event-factory"),
        ("BP-WORKFLOW-0001", "BP-WORKFLOW", "workflow-factory"),
        ("BP-SERVICE-0001", "BP-SERVICE", "service-factory"),
        ("BP-APPLICATION-0001", "BP-APPLICATION", "application-factory"),
    ],
)
def test_generate_defers_unsupported_families_as_gap(
    orchestrator, blueprint_id, blueprint_class, factory_name
):
    result = orchestrator.generate(FactoryRequest(blueprint_id))
    # classification + routing succeeded through the uniform path ...
    assert result.blueprint_class == blueprint_class
    assert result.factory_name == factory_name
    # ... but the compiler defers the family; no artifact is invented.
    assert result.status is GenerationStatus.GAP
    assert result.success is False
    assert result.artifact_id is None
    assert result.runtime_id is None
    assert result.gap is not None
    assert result.evidence["compiler_artifact"] is None
    assert result.evidence["gap"] is not None


def test_unresolvable_blueprint_raises(orchestrator):
    with pytest.raises(BlueprintResolutionError):
        orchestrator.generate(FactoryRequest("BP-DATA-9999"))


def test_classification_uses_document_metadata_when_unregistered(orchestrator, compiler_registry):
    # BP-DATA-0001 is NOT a registered artifact, so the document's declared
    # metadata drives classification (both paths are metadata-driven).
    assert compiler_registry.artifacts.find("BP-DATA-0001") is None
    result = orchestrator.generate(FactoryRequest("BP-DATA-0001"))
    assert result.blueprint_class == "BP-DATA"


def test_orchestrator_exposes_factory_registry(orchestrator, factory_registry):
    assert orchestrator.factories is factory_registry


def test_classification_prefers_registry_metadata(
    tmp_path, factory_registry, provider, runtime_signer
):
    # When the blueprint id resolves to a registered artifact, its registry
    # metadata drives classification — even over the document's declared family.

    from engine.factory import GenerationOrchestrator
    from engine.registry.adapter import RegistryAdapter
    from engine.registry.source import ARTIFACTS_FILE, RELATIONSHIPS_FILE, VOLUMES_FILE

    artifact = {
        "universal_id": "BP-DATA-0001",
        "name": "Customer",
        "volume": "VOL-006",
        "page_start": 1,
        "page_end": 1,
        "status": "ACTIVE",
        "version": "1.0.0",
        "path": "p",
        "category": "DATA",
        "tags": ["BP-DATA"],
    }
    (tmp_path / ARTIFACTS_FILE).write_text(json.dumps({"count": 1, "artifacts": [artifact]}))
    (tmp_path / RELATIONSHIPS_FILE).write_text(json.dumps({"count": 0, "relationships": []}))
    (tmp_path / VOLUMES_FILE).write_text(json.dumps({"count": 0, "volumes": []}))
    registry = RegistryAdapter.open(tmp_path)
    orch = GenerationOrchestrator(
        registry=registry,
        factories=factory_registry,
        signer=runtime_signer,
        output_dir=tmp_path / "o",
        provider=provider,
    )
    # document says BP-API, but the registered artifact classifies it as BP-DATA
    classification = orch._classify("BP-DATA-0001", {"family": "BP-API"})
    assert classification.value == "BP-DATA"


# -- determinism --------------------------------------------------------------


def test_generation_is_deterministic(orchestrator):
    a = orchestrator.generate(FactoryRequest("BP-DATA-0001"))
    b = orchestrator.generate(FactoryRequest("BP-DATA-0001"))
    assert a.runtime_id == b.runtime_id
    assert a.artifact_id == b.artifact_id
    assert json.dumps(a.to_dict(), sort_keys=True) == json.dumps(b.to_dict(), sort_keys=True)


def test_factory_delegates_to_shared_execution_path(factory_registry):
    # BaseFactory.generate() must route through the injected execution path,
    # proving all factories reuse one execution path (no duplicated logic).
    from engine.factory.classifier import resolve_blueprint_class
    from engine.factory.contracts import FactoryResult
    from engine.factory.factories.base import ExecutionContext

    factory = factory_registry.resolve_factory("BP-DATA")
    context = ExecutionContext(
        request=FactoryRequest("BP-DATA-0001"),
        document={"version": "1.0.0"},
        classification=resolve_blueprint_class({"family": "BP-DATA"}),
        descriptor=factory.descriptor,
    )
    calls: list[str] = []

    class SpyExecution:
        def execute(self, ctx: ExecutionContext) -> FactoryResult:
            calls.append(ctx.request.blueprint_id)
            return FactoryResult(
                blueprint_id=ctx.request.blueprint_id,
                blueprint_class=ctx.classification.value,
                factory_name=ctx.descriptor.name,
                status=GenerationStatus.GENERATED,
                success=True,
            )

    result = factory.generate(context, SpyExecution())
    assert calls == ["BP-DATA-0001"]
    assert result.factory_name == "data-factory"
