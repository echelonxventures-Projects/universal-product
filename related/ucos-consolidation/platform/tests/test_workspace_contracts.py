"""EC2-TASK-000081 — Workspace contracts + metadata tests.

Covers the immutable, content-addressed workspace vocabulary (Workspace,
WorkspaceMember, statuses, member roles), workspace metadata normalization, the
published contract surface, and fail-closed validation.
"""

from __future__ import annotations

from platform.identity.contracts import CapabilityGroup
from platform.workspace.contracts import (
    WORKSPACE_CONTRACT_VERSION,
    WORKSPACE_CONTRACTS,
    WORKSPACE_GROUP,
    MemberRole,
    Workspace,
    WorkspaceMember,
    WorkspaceStatus,
    all_member_roles,
    all_workspace_statuses,
    default_workspace_contracts,
    workspace_contract,
)
from platform.workspace.errors import WorkspaceContractError, WorkspaceMetadataError
from platform.workspace.metadata import EMPTY_METADATA, WorkspaceMetadata

import pytest


def test_workspace_group_binds_to_the_matrix_row():
    assert WORKSPACE_GROUP is CapabilityGroup.WORKSPACE_PROJECT_LIFECYCLE


def test_workspace_is_content_addressed_by_slug_and_tenant():
    a = Workspace.create("acme-core", "Acme Core", "owner@x", tenant="acme")
    b = Workspace.create("acme-core", "Different Name", "other@x", tenant="acme")
    # Identity is slug+tenant; name/owner do not change the id.
    assert a.workspace_id == b.workspace_id
    assert a.workspace_id.startswith("UCOS-WSPC-")
    # A different tenant is a different workspace.
    assert Workspace.create("acme-core", "n", "o", tenant="other").workspace_id != a.workspace_id


def test_workspace_slug_is_normalized_and_validated():
    assert Workspace.create("Acme-Core", "n", "o").slug == "acme-core"
    with pytest.raises(WorkspaceContractError):
        Workspace.create("has space", "n", "o")
    with pytest.raises(WorkspaceContractError):
        Workspace.create("", "n", "o")


def test_workspace_requires_name_and_owner():
    with pytest.raises(WorkspaceContractError):
        Workspace.create("slug", "", "o")
    with pytest.raises(WorkspaceContractError):
        Workspace.create("slug", "n", "")


def test_workspace_defaults_to_active_and_immutable_transitions():
    ws = Workspace.create("s", "n", "o")
    assert ws.status is WorkspaceStatus.ACTIVE
    assert ws.is_active and ws.is_global
    archived = ws.with_status(WorkspaceStatus.ARCHIVED)
    assert archived.status is WorkspaceStatus.ARCHIVED
    assert archived.workspace_id == ws.workspace_id  # id preserved
    assert ws.status is WorkspaceStatus.ACTIVE  # original unchanged


def test_workspace_with_metadata_preserves_identity():
    ws = Workspace.create("s", "n", "o")
    md = WorkspaceMetadata.create(description="d", labels=["x"])
    updated = ws.with_metadata(md)
    assert updated.metadata is md
    assert updated.workspace_id == ws.workspace_id


def test_workspace_with_status_and_metadata_validate():
    ws = Workspace.create("s", "n", "o")
    with pytest.raises(WorkspaceContractError):
        ws.with_status("archived")  # type: ignore[arg-type]
    with pytest.raises(WorkspaceContractError):
        ws.with_metadata("nope")  # type: ignore[arg-type]
    with pytest.raises(WorkspaceContractError):
        Workspace.create("s", "n", "o", status="active")  # type: ignore[arg-type]
    with pytest.raises(WorkspaceContractError):
        Workspace.create("s", "n", "o", metadata="nope")  # type: ignore[arg-type]


def test_workspace_member_is_content_addressed():
    m = WorkspaceMember.create("UCOS-WSPC-x", "UCOS-PRIN-y", "sub", MemberRole.OWNER)
    assert m.member_id.startswith("UCOS-WMEM-")
    same = WorkspaceMember.create("UCOS-WSPC-x", "UCOS-PRIN-y", "sub", MemberRole.MEMBER)
    assert same.member_id == m.member_id  # keyed by workspace+principal only


def test_workspace_member_validation():
    with pytest.raises(WorkspaceContractError):
        WorkspaceMember.create("", "p", "s", MemberRole.OWNER)
    with pytest.raises(WorkspaceContractError):
        WorkspaceMember.create("w", "", "s", MemberRole.OWNER)
    with pytest.raises(WorkspaceContractError):
        WorkspaceMember.create("w", "p", "", MemberRole.OWNER)
    with pytest.raises(WorkspaceContractError):
        WorkspaceMember.create("w", "p", "s", "owner")  # type: ignore[arg-type]


def test_metadata_normalization_and_validation():
    md = WorkspaceMetadata.create(description="d", labels=["a", "b"], annotations={"k": "v"})
    assert md.has_label("a") and md.to_dict()["annotations"] == {"k": "v"}
    assert (
        md.fingerprint()
        == WorkspaceMetadata.create(
            description="d", labels=["b", "a"], annotations={"k": "v"}
        ).fingerprint()
    )
    assert EMPTY_METADATA.description == ""
    with pytest.raises(WorkspaceMetadataError):
        WorkspaceMetadata.create(description=123)  # type: ignore[arg-type]
    with pytest.raises(WorkspaceMetadataError):
        WorkspaceMetadata.create(labels=[""])
    with pytest.raises(WorkspaceMetadataError):
        WorkspaceMetadata.create(annotations={"k": 1})  # type: ignore[dict-item]


def test_published_contracts():
    contracts = default_workspace_contracts()
    assert len(contracts) == len(WORKSPACE_CONTRACTS) == 6
    names = {c.name for c in contracts}
    assert "workspace.registry.registry" in names
    assert "workspace.isolation.evaluate" in names
    assert all(str(c.version) == WORKSPACE_CONTRACT_VERSION for c in contracts)


def test_workspace_contract_rejects_empty_name():
    with pytest.raises(WorkspaceContractError):
        workspace_contract("")


def test_enum_helpers():
    assert len(all_workspace_statuses()) == 3
    assert len(all_member_roles()) == 3
    assert WorkspaceStatus.ACTIVE.value == "active"
    assert MemberRole.OWNER.value == "owner"
