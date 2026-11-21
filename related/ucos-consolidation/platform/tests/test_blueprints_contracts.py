"""EC2-TASK-000097 — Blueprint contracts + metadata tests (EC2-EPIC-006).

Covers the immutable core vocabulary: the six frozen generation families, the lifecycle
statuses, the governed actions and their verb→(capability group, permission) map bound
to the two existing ``blueprint-authoring`` / ``blueprint-catalog`` groups (no new
authority), the content-addressed ``Blueprint`` value type (creation, validation,
immutable copies, determinism), the ``BlueprintMetadata`` value type, and the published
versioned contract surface.
"""

from __future__ import annotations

from platform.blueprints.contracts import (
    BLUEPRINT_AUTHORING_GROUP,
    BLUEPRINT_CATALOG_GROUP,
    BLUEPRINT_CONTRACT_VERSION,
    BLUEPRINT_CONTRACTS,
    MUTATING_ACTIONS,
    Blueprint,
    BlueprintAction,
    BlueprintFamily,
    BlueprintStatus,
    all_blueprint_actions,
    all_blueprint_families,
    all_blueprint_statuses,
    authority_for,
    blueprint_contract,
    default_blueprint_contracts,
    group_for,
    permission_for,
)
from platform.blueprints.errors import BlueprintContractError, BlueprintMetadataError
from platform.blueprints.metadata import EMPTY_METADATA, BlueprintMetadata
from platform.foundation.identity import Permission
from platform.identity.contracts import CapabilityGroup

import pytest

# --------------------------------------------------------------------------- #
# Vocabulary                                                                   #
# --------------------------------------------------------------------------- #


def test_six_frozen_generation_families():
    families = all_blueprint_families()
    assert [f.value for f in families] == [
        "data",
        "event",
        "api",
        "workflow",
        "service",
        "application",
    ]
    assert len(families) == 6


def test_statuses_and_actions_enumerated():
    assert [s.value for s in all_blueprint_statuses()] == [
        "draft",
        "validated",
        "catalogued",
        "superseded",
        "retired",
    ]
    assert len(all_blueprint_actions()) == 12


def test_groups_are_the_two_existing_capability_groups():
    assert BLUEPRINT_AUTHORING_GROUP is CapabilityGroup.BLUEPRINT_AUTHORING
    assert BLUEPRINT_CATALOG_GROUP is CapabilityGroup.BLUEPRINT_CATALOG


@pytest.mark.parametrize(
    ("action", "group", "permission"),
    [
        (BlueprintAction.AUTHOR, CapabilityGroup.BLUEPRINT_AUTHORING, Permission.CREATE),
        (BlueprintAction.CLASSIFY, CapabilityGroup.BLUEPRINT_AUTHORING, Permission.CREATE),
        (BlueprintAction.VALIDATE, CapabilityGroup.BLUEPRINT_AUTHORING, Permission.CREATE),
        (BlueprintAction.VERSION, CapabilityGroup.BLUEPRINT_AUTHORING, Permission.CREATE),
        (BlueprintAction.INSPECT, CapabilityGroup.BLUEPRINT_CATALOG, Permission.READ),
        (BlueprintAction.DISCOVER, CapabilityGroup.BLUEPRINT_CATALOG, Permission.READ),
        (BlueprintAction.SEARCH, CapabilityGroup.BLUEPRINT_CATALOG, Permission.READ),
        (BlueprintAction.TRACE, CapabilityGroup.BLUEPRINT_CATALOG, Permission.READ),
        (BlueprintAction.CATALOG, CapabilityGroup.BLUEPRINT_CATALOG, Permission.CREATE),
        (BlueprintAction.RETIRE, CapabilityGroup.BLUEPRINT_CATALOG, Permission.CREATE),
        (BlueprintAction.ASSOCIATE, CapabilityGroup.BLUEPRINT_CATALOG, Permission.CREATE),
        (BlueprintAction.DISSOCIATE, CapabilityGroup.BLUEPRINT_CATALOG, Permission.CREATE),
    ],
)
def test_authority_map(action, group, permission):
    assert authority_for(action) == (group, permission)
    assert group_for(action) is group
    assert permission_for(action) is permission


def test_authority_rejects_non_action():
    with pytest.raises(BlueprintContractError):
        authority_for("author")  # type: ignore[arg-type]


def test_mutating_actions_set():
    assert BlueprintAction.AUTHOR in MUTATING_ACTIONS
    assert BlueprintAction.CATALOG in MUTATING_ACTIONS
    assert BlueprintAction.INSPECT not in MUTATING_ACTIONS
    assert BlueprintAction.TRACE not in MUTATING_ACTIONS


# --------------------------------------------------------------------------- #
# Blueprint value type                                                         #
# --------------------------------------------------------------------------- #


def test_blueprint_create_is_content_addressed_and_deterministic():
    a = Blueprint.create("bp-1", "BP One", "UCOS-WSPC-1", "arch@x", BlueprintFamily.DATA)
    b = Blueprint.create("BP-1", "different name", "UCOS-WSPC-1", "other@x", BlueprintFamily.EVENT)
    assert a.blueprint_id == b.blueprint_id  # id depends only on {slug, workspace}
    assert a.blueprint_id.startswith("UCOS-BLPR-")
    assert a.slug == "bp-1"
    assert a.status is BlueprintStatus.DRAFT


def test_blueprint_slug_normalised_and_validated():
    with pytest.raises(BlueprintContractError):
        Blueprint.create("", "n", "w", "o", BlueprintFamily.DATA)
    with pytest.raises(BlueprintContractError):
        Blueprint.create("has space", "n", "w", "o", BlueprintFamily.DATA)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"name": ""},
        {"workspace_id": ""},
        {"owner_subject": ""},
    ],
)
def test_blueprint_requires_core_fields(kwargs):
    base = {
        "slug": "bp",
        "name": "n",
        "workspace_id": "w",
        "owner_subject": "o",
        "family": BlueprintFamily.DATA,
    }
    base.update(kwargs)
    with pytest.raises(BlueprintContractError):
        Blueprint.create(
            base["slug"], base["name"], base["workspace_id"], base["owner_subject"], base["family"]
        )


def test_blueprint_rejects_bad_family_status_metadata_project():
    with pytest.raises(BlueprintContractError):
        Blueprint.create("bp", "n", "w", "o", "data")  # type: ignore[arg-type]
    with pytest.raises(BlueprintContractError):
        Blueprint.create("bp", "n", "w", "o", BlueprintFamily.DATA, status="draft")  # type: ignore[arg-type]
    with pytest.raises(BlueprintContractError):
        Blueprint.create("bp", "n", "w", "o", BlueprintFamily.DATA, metadata="x")  # type: ignore[arg-type]
    with pytest.raises(BlueprintContractError):
        Blueprint.create("bp", "n", "w", "o", BlueprintFamily.DATA, project_id="")


def test_blueprint_with_status_and_metadata_preserve_id():
    bp = Blueprint.create("bp", "n", "w", "o", BlueprintFamily.DATA, project_id="UCOS-PROJ-1")
    catalogued = bp.with_status(BlueprintStatus.VALIDATED)
    assert catalogued.blueprint_id == bp.blueprint_id
    assert catalogued.status is BlueprintStatus.VALIDATED
    md = BlueprintMetadata.create(description="d", labels=["x"])
    updated = bp.with_metadata(md)
    assert updated.blueprint_id == bp.blueprint_id
    assert updated.metadata is md
    assert bp.project_id == "UCOS-PROJ-1"


def test_blueprint_with_bad_arguments_rejected():
    bp = Blueprint.create("bp", "n", "w", "o", BlueprintFamily.DATA)
    with pytest.raises(BlueprintContractError):
        bp.with_status("x")  # type: ignore[arg-type]
    with pytest.raises(BlueprintContractError):
        bp.with_metadata("x")  # type: ignore[arg-type]


def test_blueprint_flags_and_serialisation():
    bp = Blueprint.create("bp", "n", "w", "o", BlueprintFamily.DATA)
    assert bp.is_catalogued is False
    assert bp.is_terminal is False
    assert bp.with_status(BlueprintStatus.CATALOGUED).is_catalogued is True
    assert bp.with_status(BlueprintStatus.RETIRED).is_terminal is True
    d = bp.to_dict()
    assert d["blueprint_id"] == bp.blueprint_id
    assert d["family"] == "data"
    assert isinstance(bp.fingerprint(), str)


# --------------------------------------------------------------------------- #
# Metadata                                                                     #
# --------------------------------------------------------------------------- #


def test_metadata_create_normalises_and_fingerprints():
    md = BlueprintMetadata.create(description="d", labels=["a", "b"], annotations={"k": "v"})
    assert md.has_label("a")
    assert md.to_dict()["labels"] == ["a", "b"]
    assert (
        md.fingerprint()
        == BlueprintMetadata.create(
            description="d", labels=["b", "a"], annotations={"k": "v"}
        ).fingerprint()
    )
    assert EMPTY_METADATA.description == ""


@pytest.mark.parametrize(
    "kwargs",
    [
        {"description": 5},
        {"labels": [""]},
        {"annotations": {"": "v"}},
        {"annotations": {"k": 1}},
    ],
)
def test_metadata_rejects_malformed(kwargs):
    with pytest.raises(BlueprintMetadataError):
        BlueprintMetadata.create(**kwargs)


# --------------------------------------------------------------------------- #
# Published contract surface                                                   #
# --------------------------------------------------------------------------- #


def test_contract_surface_is_versioned_and_named():
    assert BLUEPRINT_CONTRACT_VERSION == "1.0.0"
    assert len(BLUEPRINT_CONTRACTS) == 8
    names = {ref.name for ref in BLUEPRINT_CONTRACTS}
    assert "blueprints.catalog.index" in names
    assert "blueprints.provenance.trace" in names
    for ref in BLUEPRINT_CONTRACTS:
        assert ref.version == BLUEPRINT_CONTRACT_VERSION


def test_default_contracts_build_and_are_named():
    contracts = default_blueprint_contracts()
    assert len(contracts) == len(BLUEPRINT_CONTRACTS)
    assert blueprint_contract("blueprints.registry.registry").name == "blueprints.registry.registry"


def test_blueprint_contract_requires_name():
    with pytest.raises(BlueprintContractError):
        blueprint_contract("")
