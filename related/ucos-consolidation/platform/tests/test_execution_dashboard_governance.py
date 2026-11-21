"""EC2-EPIC-008 — execution-dashboard governance validation tests.

Asserts the constitutional/governance invariants the mission mandates: no new authority
(the reused EXECUTION_DASHBOARD capability group, no new capability group, no new
Role/Permission), no duplicate lifecycle/registry/status definition (the dashboard surfaces
the frozen EPIC-007 vocabulary verbatim), no direct EC-1 engine import (P10), no execution /
generation / mutation logic (read/observability only), a deterministic in-memory model (no
server/socket/file writes), and no secret material in surfaced views.
"""

from __future__ import annotations

from pathlib import Path
from platform.execution_dashboard.contracts import (
    EXECUTION_DASHBOARD_GROUP,
    DashboardExecutionState,
    DashboardRequestPosture,
    DashboardRequestStatus,
)
from platform.execution_dashboard.service import build_execution_dashboard_service
from platform.generation.contracts import ExecutionState, RequestStatus
from platform.generation.service import build_generation_request_service
from platform.generation.status import RequestPosture
from platform.identity.contracts import CapabilityGroup as IdentityCapabilityGroup
from platform.identity.service import build_authorization_service
from platform.workspace.registration import WorkspaceRegistry

_DASHBOARD_PKG = Path(__file__).resolve().parents[1] / "execution_dashboard"

#: Verbs the dashboard runtime must never expose (authority-neutral; delegates to L7).
_FORBIDDEN_AUTHORITY = (
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

#: Mutation/lifecycle verbs the read-only dashboard must never expose.
_FORBIDDEN_MUTATION = (
    "submit_request",
    "submit",
    "create",
    "register",
    "transition",
    "dispatch_request",
    "dispatch",
    "approve",
    "enqueue",
    "cancel_request",
    "complete",
    "fail",
    "delete",
    "remove",
    "update_metadata",
)


def _service():
    auth = build_authorization_service()
    generation = build_generation_request_service(
        authorization=auth, workspaces=WorkspaceRegistry()
    )
    return build_execution_dashboard_service(generation=generation, authorization=auth)


def test_reuses_the_existing_capability_group_no_new_group():
    assert EXECUTION_DASHBOARD_GROUP is IdentityCapabilityGroup.EXECUTION_DASHBOARD


def test_surfaces_epic_007_vocabulary_without_redefinition():
    assert DashboardRequestStatus is RequestStatus
    assert DashboardExecutionState is ExecutionState
    assert DashboardRequestPosture is RequestPosture


def test_service_exposes_no_authority_operation():
    service = _service()
    for verb in _FORBIDDEN_AUTHORITY:
        assert not hasattr(service, verb), f"dashboard must not expose authority '{verb}'"


def test_service_exposes_no_mutation_operation():
    service = _service()
    for verb in _FORBIDDEN_MUTATION:
        assert not hasattr(service, verb), f"dashboard must not expose mutation '{verb}'"


def test_runtime_never_imports_engine_modules_directly():
    # P10: the package must consume EC-1/generation by reference, never import engine.
    for path in _DASHBOARD_PKG.glob("*.py"):
        source = path.read_text(encoding="utf-8")
        for line in source.splitlines():
            stripped = line.strip()
            assert not stripped.startswith("import engine"), f"{path.name}: {stripped}"
            assert not stripped.startswith("from engine"), f"{path.name}: {stripped}"


def test_no_filesystem_write_or_server_in_source():
    for path in _DASHBOARD_PKG.glob("*.py"):
        source = path.read_text(encoding="utf-8")
        assert "open(" not in source
        assert "import socket" not in source
        assert "http.server" not in source
        assert ".write(" not in source


def test_dashboard_authorizes_on_its_own_group_not_generation():
    # Source-verify the dashboard binds EXECUTION_DASHBOARD_GROUP (never generation-requests)
    # for its own access decisions.
    for name in ("service.py", "search.py"):
        source = (_DASHBOARD_PKG / name).read_text(encoding="utf-8")
        assert "EXECUTION_DASHBOARD_GROUP" in source
        # The dashboard must never authorize against the generation-requests group symbol.
        assert "GENERATION_REQUEST_GROUP" not in source


def test_no_secret_material_is_surfaced_in_views():
    from platform.blueprints.contracts import BlueprintFamily
    from platform.execution_dashboard.views import ExecutionSnapshot
    from platform.generation.registry import GenerationRequestRegistry
    from platform.generation.status import derive_status

    reg = GenerationRequestRegistry()
    req = reg.create(
        "r", "UCOS-BLPR-a", "UCOS-WSPC-1", "arch@x", BlueprintFamily.DATA, submitted_tick=1
    )
    snapshot = ExecutionSnapshot.from_request(
        req, derive_status(req, has_dispatch=False, has_provenance=False)
    )
    serialized = str(snapshot.to_dict())
    for token in ("password", "secret", "token", "apikey", "api_key", "private_key"):
        assert token not in serialized.lower()
