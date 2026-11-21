"""Tests for engine.knowledge.integration.constitution — Deliverable 1."""

from __future__ import annotations

from engine.knowledge.certification import certify_base
from engine.knowledge.integration.constitution import (
    INTEGRATION_DECISION_OBJECT_ID,
    INTEGRATION_DECISION_RECORD_ID,
    INTEGRATION_LAWS,
    INTEGRATION_PRINCIPLE_ID,
    constitution_objects,
    extend_base_with_constitution,
    integration_constitution,
)
from engine.knowledge.integration.contracts import ConstitutionalLayer, SequenceStage
from engine.knowledge.seed import build_seed_base
from engine.knowledge.validation import validate_base


def test_constitution_shape():
    const = integration_constitution()
    assert len(const.layers) == 21
    assert len(const.laws) == 10
    assert [law.law_id for law in const.laws] == [f"UKI-LAW-{i:03d}" for i in range(1, 11)]
    assert len(const.sequence) == 10
    d = const.to_dict()
    assert d["laws"][0]["law_id"] == "UKI-LAW-001"


def test_law_queries():
    const = integration_constitution()
    assert const.law("UKI-LAW-002").title == "Discover Before Create"
    assert const.law("UKI-LAW-999") is None
    discover_laws = const.laws_for_stage(SequenceStage.DISCOVER)
    assert any(law.law_id == "UKI-LAW-002" for law in discover_laws)
    assert const.covers_layer(ConstitutionalLayer.REGISTRY)
    # every law carries at least one governed layer
    assert all(law.layers for law in INTEGRATION_LAWS)


def test_constitution_objects_wellformed():
    objects, decisions = constitution_objects()
    ids = {o.cko_id for o in objects}
    assert ids == {INTEGRATION_PRINCIPLE_ID, INTEGRATION_DECISION_OBJECT_ID}
    assert decisions[0].decision_id == INTEGRATION_DECISION_RECORD_ID
    assert decisions[0].is_reviewable
    for obj in objects:
        assert obj.verify_integrity()


def test_extend_base_is_idempotent_and_valid():
    base = build_seed_base()
    merged = extend_base_with_constitution(base)
    assert merged.has_object(INTEGRATION_PRINCIPLE_ID)
    assert merged.has_decision(INTEGRATION_DECISION_RECORD_ID)
    # merging twice adds nothing (no duplicate authored)
    twice = extend_base_with_constitution(merged)
    assert len(twice.objects()) == len(merged.objects())
    assert len(twice.decisions()) == len(merged.decisions())
    # the merged base still validates and certifies clean
    assert validate_base(merged).accepted
    assert certify_base(merged).certified
