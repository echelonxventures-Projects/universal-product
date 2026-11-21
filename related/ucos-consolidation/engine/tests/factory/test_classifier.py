"""TASK-000045 — Blueprint classification resolution tests (TASK-000039)."""

from __future__ import annotations

import pytest

from engine.compiler.ir import BlueprintFamily
from engine.factory.classifier import BlueprintClassification, resolve_blueprint_class
from engine.factory.errors import ClassificationError
from engine.registry.models import Artifact, LifecycleStatus


def test_classify_by_explicit_family():
    result = resolve_blueprint_class({"family": "BP-DATA"})
    assert result.blueprint_class is BlueprintFamily.DATA
    assert result.source == "family"
    assert result.value == "BP-DATA"
    assert result.to_dict() == {
        "blueprint_class": "BP-DATA",
        "source": "family",
        "token": "BP-DATA",
    }


@pytest.mark.parametrize(
    ("family", "expected"),
    [
        ("BP-DATA", BlueprintFamily.DATA),
        ("BP-API", BlueprintFamily.API),
        ("BP-CONTRACT", BlueprintFamily.CONTRACT),
        ("BP-WORKFLOW", BlueprintFamily.WORKFLOW),
        ("BP-SERVICE", BlueprintFamily.SERVICE),
        ("BP-APPLICATION", BlueprintFamily.APPLICATION),
    ],
)
def test_classify_all_required_families(family, expected):
    assert resolve_blueprint_class({"family": family}).blueprint_class is expected


def test_classify_by_id_prefix():
    result = resolve_blueprint_class({"blueprint_id": "BP-APPLICATION-0001"})
    assert result.blueprint_class is BlueprintFamily.APPLICATION
    assert result.source == "blueprint_id"


def test_classify_by_universal_id_prefix():
    result = resolve_blueprint_class({"universal_id": "BP-SERVICE-0007"})
    assert result.blueprint_class is BlueprintFamily.SERVICE
    assert result.source == "universal_id"


def test_classify_by_category_bare_suffix():
    result = resolve_blueprint_class({"category": "DATA"})
    assert result.blueprint_class is BlueprintFamily.DATA
    assert result.source == "category"


def test_classify_by_category_full_value():
    result = resolve_blueprint_class({"category": "BP-API"})
    assert result.blueprint_class is BlueprintFamily.API
    assert result.source == "category"


def test_classify_by_tag():
    result = resolve_blueprint_class({"tags": ["misc", "BP-WORKFLOW"]})
    assert result.blueprint_class is BlueprintFamily.WORKFLOW
    assert result.source == "tag"


def test_classify_from_registry_artifact():
    artifact = Artifact(
        universal_id="BP-DATA-9001",
        name="X",
        volume="VOL-006",
        page_start=1,
        page_end=1,
        status=LifecycleStatus.ACTIVE,
        version="1.0.0",
        path="p",
        category="DATA",
        tags=("BP-DATA",),
    )
    result = resolve_blueprint_class(artifact)
    # id prefix wins over category/tag in precedence
    assert result.blueprint_class is BlueprintFamily.DATA
    assert result.source == "universal_id"


def test_family_precedence_over_id():
    # explicit family is authoritative even if id suggests another class
    result = resolve_blueprint_class({"family": "BP-API", "blueprint_id": "BP-DATA-1"})
    assert result.blueprint_class is BlueprintFamily.API
    assert result.source == "family"


def test_unknown_declared_family_rejected():
    with pytest.raises(ClassificationError) as exc:
        resolve_blueprint_class({"family": "BP-QUANTUM"})
    assert "not a registered blueprint family" in exc.value.message


def test_no_metadata_rejected():
    with pytest.raises(ClassificationError) as exc:
        resolve_blueprint_class({"unrelated": "value"})
    assert "could not derive" in exc.value.message


def test_non_mapping_rejected():
    with pytest.raises(ClassificationError):
        resolve_blueprint_class(42)  # type: ignore[arg-type]


def test_blank_and_nonstring_fields_skft_to_next_source():
    # blank family + non-string id fall through to a usable tag
    result = resolve_blueprint_class({"family": "  ", "blueprint_id": 123, "tags": ["BP-SERVICE"]})
    assert result.blueprint_class is BlueprintFamily.SERVICE
    assert result.source == "tag"


def test_classification_is_frozen():
    result = resolve_blueprint_class({"family": "BP-DATA"})
    assert isinstance(result, BlueprintClassification)
    with pytest.raises((AttributeError, TypeError)):
        result.source = "mutated"  # type: ignore[misc]


def test_nonmatching_id_falls_through_to_tag():
    # id present but not a family token → fall through to a matching tag
    result = resolve_blueprint_class({"blueprint_id": "XYZ-123", "tags": ["BP-API"]})
    assert result.blueprint_class is BlueprintFamily.API
    assert result.source == "tag"


def test_nonmatching_category_falls_through_to_tag():
    result = resolve_blueprint_class({"category": "MISC", "tags": ["BP-SERVICE"]})
    assert result.blueprint_class is BlueprintFamily.SERVICE
    assert result.source == "tag"


def test_nonmatching_tags_and_nonstring_tags_reach_error():
    with pytest.raises(ClassificationError):
        resolve_blueprint_class({"tags": ["misc", 42, "still-nothing"]})


def test_match_family_token_blank_returns_none():
    from engine.factory.classifier import _match_family_token

    assert _match_family_token("   ") is None
    assert _match_family_token("nope") is None
