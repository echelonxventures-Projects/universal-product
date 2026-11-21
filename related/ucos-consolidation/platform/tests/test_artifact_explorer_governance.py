"""EC2-EPIC-009 — artifact-explorer governance validation tests.

Asserts the constitutional/governance invariants the mission mandates: no new authority
(the reused ARTIFACT_EXPLORER capability group, no new capability group, no new
Role/Permission, no new classification model), read-only discipline (no artifact
generation, no artifact mutation, no engine execution, no destructive registry verbs),
no duplicate provenance implementation (the explorer projects the certified
RequestProvenance by reference and reuses its id), no direct EC-1 runtime import,
deterministic in-memory model (no server/socket/file writes), no secret material in
records, and that pure reads do not invoke an authorization decision.
"""

from __future__ import annotations

from pathlib import Path
from platform.artifact_explorer.contracts import ARTIFACT_EXPLORER_GROUP, ArtifactFamily
from platform.artifact_explorer.lineage import ArtifactProvenance
from platform.artifact_explorer.service import build_artifact_explorer_service
from platform.blueprints.contracts import BlueprintFamily
from platform.foundation.identity import Permission as FoundationPermission
from platform.identity.contracts import CapabilityGroup as IdentityCapabilityGroup
from platform.identity.service import build_authorization_service
from platform.tests.artifact_explorer_helpers import (
    explorer,
    seeded_artifact,
)

_EXPLORER_PKG = Path(__file__).resolve().parents[1] / "artifact_explorer"

#: Verbs the explorer runtime must never expose (authority-neutral + read-only).
_FORBIDDEN_OPERATIONS = (
    "authorize",
    "authorize_principal",
    "generate",
    "create_artifact",
    "mutate",
    "update_artifact",
    "delete_artifact",
    "execute",
    "dispatch_request",
    "grant",
    "govern",
    "override",
)


def test_reuses_the_existing_capability_group_no_new_group():
    assert ARTIFACT_EXPLORER_GROUP is IdentityCapabilityGroup.ARTIFACT_EXPLORER


def test_defines_no_new_role_permission_or_classification_vocabulary():
    from platform.artifact_explorer import contracts as contracts_module

    assert contracts_module.Permission is FoundationPermission
    assert contracts_module.CapabilityGroup.__module__ == "platform.identity.contracts"
    # No new classification model: the family vocabulary IS the frozen BlueprintFamily.
    assert ArtifactFamily is BlueprintFamily


def test_service_exposes_no_authority_or_mutation_operation():
    service = build_artifact_explorer_service(authorization=build_authorization_service())
    for verb in _FORBIDDEN_OPERATIONS:
        assert not hasattr(service, verb), f"explorer runtime must not expose '{verb}'"


def test_explorer_does_not_own_a_registry_mutation_surface():
    # The explorer consumes the EPIC-007 registry read-only; it exposes no record store.
    service = build_artifact_explorer_service(authorization=build_authorization_service())
    for verb in ("record", "register", "delete", "remove", "drop", "clear", "transition"):
        assert not hasattr(service, verb)


def test_provenance_projection_reuses_id_not_a_duplicate_model():
    _, registry, dispatch, provenance, _ = explorer()
    req = seeded_artifact(registry, dispatch, provenance)
    prov = provenance.get(req.request_id)
    projection = ArtifactProvenance.from_provenance(prov)
    # No duplicate provenance implementation: the projection reuses the certified id
    # and reproduces the certified edge byte-for-byte.
    assert projection.provenance_id == prov.provenance_id
    assert projection.edge() == prov.trace_edge()


def test_runtime_never_imports_engine_modules_directly():
    for path in _EXPLORER_PKG.glob("*.py"):
        source = path.read_text(encoding="utf-8")
        for line in source.splitlines():
            stripped = line.strip()
            assert not stripped.startswith("import engine"), f"{path.name}: {stripped}"
            assert not stripped.startswith("from engine"), f"{path.name}: {stripped}"


def test_no_filesystem_write_or_server_in_source():
    for path in _EXPLORER_PKG.glob("*.py"):
        source = path.read_text(encoding="utf-8")
        assert "open(" not in source
        assert "import socket" not in source
        assert "http.server" not in source
        assert ".write(" not in source


def test_no_secret_material_is_stored_in_views():
    _, registry, dispatch, provenance, service = explorer()
    req = seeded_artifact(registry, dispatch, provenance)
    serialized = str(service.view_of(req.request_id).to_dict())
    for token in ("password", "secret", "token", "apikey", "api_key", "private_key"):
        assert token not in serialized.lower()


def test_reads_do_not_invoke_authorization_decision(monkeypatch):
    from platform.identity.service import AuthorizationService

    auth, registry, dispatch, provenance, service = explorer()
    req = seeded_artifact(registry, dispatch, provenance)

    def _boom(*args, **kwargs):  # pragma: no cover - must never be invoked
        raise AssertionError("a pure read must not invoke an authorization decision")

    monkeypatch.setattr(AuthorizationService, "authorize", _boom, raising=True)
    monkeypatch.setattr(AuthorizationService, "authorize_principal", _boom, raising=True)
    assert service.reference_of(req.request_id).request_ref == req.request_id
    assert service.summary_of(req.request_id).request_ref == req.request_id
    assert service.view_of(req.request_id).request_ref == req.request_id
    assert service.status_of(req.request_id).request_id == req.request_id
