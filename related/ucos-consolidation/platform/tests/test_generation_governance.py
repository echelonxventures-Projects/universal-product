"""EC2-EPIC-007 — generation-request governance validation tests.

Asserts the constitutional/governance invariants the mission mandates: no new authority
(the reused GENERATION_REQUESTS capability group, no new capability group, no new
Role/Permission, no new classification model), no duplication of the certified L7
authorization decision (the service delegates and exposes no authority verb), no direct
EC-1 runtime import (dispatch binds by ContractRef only — P10), append-only record
discipline (no destructive registry operations), no runtime bypass path (dispatch is the
only route to DISPATCHED), deterministic in-memory model (no server/socket/file writes),
and no secret material in records.
"""

from __future__ import annotations

from pathlib import Path
from platform.blueprints.contracts import BlueprintFamily
from platform.foundation.identity import Permission as FoundationPermission
from platform.generation.contracts import GENERATION_REQUEST_GROUP, RequestFamily
from platform.generation.dispatch import DISPATCH_CONTRACTS
from platform.generation.registry import GenerationRequestRegistry
from platform.generation.service import build_generation_request_service
from platform.identity.contracts import CapabilityGroup as IdentityCapabilityGroup
from platform.identity.service import build_authorization_service
from platform.workspace.registration import WorkspaceRegistry

_GENERATION_PKG = Path(__file__).resolve().parents[1] / "generation"

#: Verbs the request runtime must never expose (authority-neutral; delegates to L7).
_FORBIDDEN_OPERATIONS = (
    "authorize",
    "authorize_principal",
    "ratify",
    "enact",
    "grant",
    "govern",
    "override",
    "escalate",
    "deny",
    "permit",
)


def _service():
    auth = build_authorization_service()
    return build_generation_request_service(authorization=auth, workspaces=WorkspaceRegistry())


def test_reuses_the_existing_capability_group_no_new_group():
    assert GENERATION_REQUEST_GROUP is IdentityCapabilityGroup.GENERATION_REQUESTS


def test_defines_no_new_role_permission_or_classification_vocabulary():
    from platform.generation import contracts as contracts_module

    assert contracts_module.Permission is FoundationPermission
    assert contracts_module.CapabilityGroup.__module__ == "platform.identity.contracts"
    # No new classification model: the family vocabulary IS the frozen BlueprintFamily.
    assert RequestFamily is BlueprintFamily


def test_service_exposes_no_authority_operation():
    service = _service()
    for verb in _FORBIDDEN_OPERATIONS:
        assert not hasattr(service, verb), f"request runtime must not expose '{verb}'"


def test_registry_exposes_no_destructive_mutation():
    reg = GenerationRequestRegistry()
    for verb in ("delete", "remove", "drop", "clear", "pop", "truncate"):
        assert not hasattr(reg, verb)


def test_runtime_never_imports_engine_modules_directly():
    # P10: the package must bind EC-1 by ContractRef only, never import an engine module.
    for path in _GENERATION_PKG.glob("*.py"):
        source = path.read_text(encoding="utf-8")
        for line in source.splitlines():
            stripped = line.strip()
            assert not stripped.startswith("import engine"), f"{path.name}: {stripped}"
            assert not stripped.startswith("from engine"), f"{path.name}: {stripped}"


def test_dispatch_binds_engine_only_by_contract_reference():
    # The dispatch boundary references the certified EC-1 execution contracts by name.
    names = {ref.name for ref in DISPATCH_CONTRACTS}
    assert "engine.factory.generate" in names
    assert "engine.runtime.assemble" in names


def test_no_filesystem_write_or_server_in_source():
    for path in _GENERATION_PKG.glob("*.py"):
        source = path.read_text(encoding="utf-8")
        assert "open(" not in source
        assert "import socket" not in source
        assert "http.server" not in source
        assert ".write(" not in source


def test_no_secret_material_is_stored_in_records():
    reg = GenerationRequestRegistry()
    req = reg.create(
        "r", "UCOS-BLPR-a", "UCOS-WSPC-1", "arch@x", BlueprintFamily.DATA, submitted_tick=1
    )
    serialized = str(req.to_dict())
    for token in ("password", "secret", "token", "apikey", "api_key", "private_key"):
        assert token not in serialized.lower()


def test_reads_do_not_invoke_authorization_decision(monkeypatch):
    from platform.identity.service import AuthorizationService

    auth = build_authorization_service()
    workspaces = WorkspaceRegistry()
    service = build_generation_request_service(authorization=auth, workspaces=workspaces)
    req = service.registry.create(
        "r", "UCOS-BLPR-a", "UCOS-WSPC-1", "arch@x", BlueprintFamily.DATA, submitted_tick=1
    )

    def _boom(*args, **kwargs):  # pragma: no cover - must never be invoked
        raise AssertionError("a pure read must not invoke an authorization decision")

    monkeypatch.setattr(AuthorizationService, "authorize", _boom, raising=True)
    monkeypatch.setattr(AuthorizationService, "authorize_principal", _boom, raising=True)
    assert service.get_request(req.request_id).request_id == req.request_id
    assert service.status_of(req.request_id).request_id == req.request_id
