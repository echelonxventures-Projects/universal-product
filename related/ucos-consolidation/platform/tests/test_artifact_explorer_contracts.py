"""EC2-TASK-000127 — Artifact Explorer contracts + domain-vocabulary tests (EC2-EPIC-009).

Covers the versioned contract surface and the read-only vocabulary: the reused
``artifact-explorer`` capability group, the READ-only verb→permission map, and the
published contract references.
"""

from __future__ import annotations

from platform.artifact_explorer.contracts import (
    ARTIFACT_EXPLORER_CONTRACT_VERSION,
    ARTIFACT_EXPLORER_CONTRACTS,
    ARTIFACT_EXPLORER_GROUP,
    ArtifactFamily,
    ExplorerAction,
    all_explorer_actions,
    artifact_explorer_contract,
    default_artifact_explorer_contracts,
    permission_for,
)
from platform.artifact_explorer.errors import ArtifactContractError
from platform.blueprints.contracts import BlueprintFamily
from platform.foundation.identity import Permission
from platform.identity.contracts import CapabilityGroup

import pytest


def test_reuses_existing_artifact_explorer_group():
    assert ARTIFACT_EXPLORER_GROUP is CapabilityGroup.ARTIFACT_EXPLORER
    assert ArtifactFamily is BlueprintFamily


def test_every_action_requires_read_only():
    for action in all_explorer_actions():
        assert permission_for(action) is Permission.READ
    assert set(all_explorer_actions()) == set(ExplorerAction)


def test_permission_for_rejects_bad_action():
    with pytest.raises(ArtifactContractError):
        permission_for("lookup")  # type: ignore[arg-type]


def test_contract_surface_is_versioned_and_complete():
    assert ARTIFACT_EXPLORER_CONTRACT_VERSION == "1.0.0"
    names = {ref.name for ref in ARTIFACT_EXPLORER_CONTRACTS}
    assert "artifacts.runtime.service" in names
    assert "artifacts.search.query" in names
    assert "artifacts.lineage.navigate" in names
    assert "artifacts.provenance.navigate" in names
    assert "artifacts.trace.navigate" in names
    assert len(ARTIFACT_EXPLORER_CONTRACTS) == 7
    for ref in ARTIFACT_EXPLORER_CONTRACTS:
        assert ref.version == ARTIFACT_EXPLORER_CONTRACT_VERSION


def test_default_contracts_build_and_name_matches():
    contracts = default_artifact_explorer_contracts()
    assert len(contracts) == len(ARTIFACT_EXPLORER_CONTRACTS)
    built = artifact_explorer_contract("artifacts.runtime.service", "desc")
    assert built.name == "artifacts.runtime.service"


def test_artifact_explorer_contract_rejects_empty_name():
    with pytest.raises(ArtifactContractError):
        artifact_explorer_contract("")
