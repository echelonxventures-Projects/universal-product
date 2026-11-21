"""TASK-000045 — Factory Layer test fixtures.

Provides an in-memory blueprint provider and IR-shaped blueprint documents for
four classes (BP-DATA, BP-API, BP-SERVICE, BP-APPLICATION), plus a wired
:class:`GenerationOrchestrator` over the certified compiler substrate. BP-DATA is
fully compilable (real artifacts); the other three parse but are deferred by the
compiler's family gate, so the factory path produces a faithful gap — never an
invented artifact.
"""

from __future__ import annotations

import copy

import pytest

from engine.determinism.reproduce import BlueprintProvider
from engine.factory import build_default_registry
from engine.factory.orchestrator import GenerationOrchestrator


class InMemoryBlueprintProvider(BlueprintProvider):
    """Resolves blueprint documents from an in-memory mapping (no filesystem)."""

    def __init__(self, documents: dict[str, dict]) -> None:
        self._documents = {bp: copy.deepcopy(doc) for bp, doc in documents.items()}

    def get(self, blueprint_id: str):
        if blueprint_id not in self._documents:
            raise KeyError(blueprint_id)
        return copy.deepcopy(self._documents[blueprint_id])


def _reclass(base: dict, *, blueprint_id: str, family: str, name: str) -> dict:
    """Copy a BP-DATA document into another family (IR-shaped, parses cleanly)."""
    doc = copy.deepcopy(base)
    doc["blueprint_id"] = blueprint_id
    doc["family"] = family
    doc["name"] = name
    doc["entity"] = copy.deepcopy(base["entity"])
    doc["entity"]["relationships"] = []
    return doc


@pytest.fixture
def api_blueprint(data_blueprint) -> dict:
    return _reclass(data_blueprint, blueprint_id="BP-API-0001", family="BP-API", name="CustomerApi")


@pytest.fixture
def event_blueprint(data_blueprint) -> dict:
    return _reclass(
        data_blueprint, blueprint_id="BP-EVENT-0001", family="BP-EVENT", name="CustomerEvent"
    )


@pytest.fixture
def workflow_blueprint(data_blueprint) -> dict:
    return _reclass(
        data_blueprint,
        blueprint_id="BP-WORKFLOW-0001",
        family="BP-WORKFLOW",
        name="CustomerWorkflow",
    )


@pytest.fixture
def service_blueprint(data_blueprint) -> dict:
    return _reclass(
        data_blueprint, blueprint_id="BP-SERVICE-0001", family="BP-SERVICE", name="CustomerService"
    )


@pytest.fixture
def application_blueprint(data_blueprint) -> dict:
    return _reclass(
        data_blueprint,
        blueprint_id="BP-APPLICATION-0001",
        family="BP-APPLICATION",
        name="CustomerApp",
    )


@pytest.fixture
def blueprint_documents(
    data_blueprint,
    api_blueprint,
    event_blueprint,
    workflow_blueprint,
    service_blueprint,
    application_blueprint,
) -> dict[str, dict]:
    return {
        "BP-DATA-0001": data_blueprint,
        "BP-API-0001": api_blueprint,
        "BP-EVENT-0001": event_blueprint,
        "BP-WORKFLOW-0001": workflow_blueprint,
        "BP-SERVICE-0001": service_blueprint,
        "BP-APPLICATION-0001": application_blueprint,
    }


@pytest.fixture
def provider(blueprint_documents) -> InMemoryBlueprintProvider:
    return InMemoryBlueprintProvider(blueprint_documents)


@pytest.fixture
def factory_registry():
    return build_default_registry()


@pytest.fixture
def orchestrator(tmp_path, compiler_registry, factory_registry, provider, runtime_signer):
    return GenerationOrchestrator(
        registry=compiler_registry,
        factories=factory_registry,
        signer=runtime_signer,
        output_dir=tmp_path / "factory-out",
        provider=provider,
    )
