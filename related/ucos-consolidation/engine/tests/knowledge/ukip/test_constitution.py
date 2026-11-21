"""UKIP Part 02 — the Knowledge Constitution."""

from __future__ import annotations

from engine.knowledge.integration.constitution import (
    INTEGRATION_LAWS,
    INTEGRATION_PRINCIPLE_ID,
    KNOWLEDGE_ONCE_PRINCIPLE,
)
from engine.knowledge.model import KnowledgeAuthority, KnowledgeKind, Lifecycle
from engine.knowledge.seed import build_seed_base
from engine.knowledge.ukip.constitution import (
    INHERITED_LAWS,
    KNOWLEDGE_CAPABILITIES,
    KNOWLEDGE_INTELLIGENCE_DECISION_OBJECT_ID,
    KNOWLEDGE_INTELLIGENCE_DECISION_RECORD_ID,
    KNOWLEDGE_INTELLIGENCE_PRINCIPLE_ID,
    KNOWLEDGE_LAWS,
    KnowledgeCapability,
    constitution_objects,
    extend_base_with_knowledge_constitution,
    knowledge_constitution,
)
from engine.knowledge.validation import validate_base


def test_eleven_capabilities_match_the_mission():
    assert len(KNOWLEDGE_CAPABILITIES) == 11
    assert {c.value for c in KNOWLEDGE_CAPABILITIES} == {
        "constitution",
        "graph",
        "registry",
        "discovery",
        "assimilation",
        "relationships",
        "classification",
        "provenance",
        "evidence",
        "validation",
        "certification",
    }


def test_laws_are_sequentially_identified():
    assert [law.law_id for law in KNOWLEDGE_LAWS] == [
        f"UKIP-LAW-{i:03d}" for i in range(1, len(KNOWLEDGE_LAWS) + 1)
    ]


def test_every_capability_is_governed():
    constitution = knowledge_constitution()
    assert constitution.is_complete
    assert constitution.ungoverned_capabilities() == ()
    matrix = constitution.capability_matrix()
    assert len(matrix) == 11
    assert all(law_ids for law_ids in matrix.values())


def test_integration_laws_are_inherited_not_restated():
    """The UKI laws must be referenced, so a change there is a change here."""
    assert INHERITED_LAWS is INTEGRATION_LAWS
    authored = {law.law_id for law in KNOWLEDGE_LAWS}
    inherited = {law.law_id for law in INHERITED_LAWS}
    assert not authored & inherited


def test_laws_derive_from_the_founding_principle_or_an_inherited_law():
    inherited = {law.law_id for law in INHERITED_LAWS}
    allowed = inherited | {KNOWLEDGE_ONCE_PRINCIPLE, INTEGRATION_PRINCIPLE_ID}
    for law in KNOWLEDGE_LAWS:
        for parent in law.derives_from:
            assert parent in allowed, f"{law.law_id} derives from unknown {parent}"


def test_at_least_one_law_derives_from_the_knowledge_once_principle():
    assert any(KNOWLEDGE_ONCE_PRINCIPLE in law.derives_from for law in KNOWLEDGE_LAWS)


def test_law_lookup_and_governs():
    constitution = knowledge_constitution()
    law = constitution.law("UKIP-LAW-001")
    assert law is not None
    assert law.title == "Unlimited Providers"
    assert law.governs(KnowledgeCapability.REGISTRY)
    assert not law.governs(KnowledgeCapability.CONSTITUTION)
    assert constitution.law("UKIP-LAW-999") is None


def test_laws_for_capability():
    constitution = knowledge_constitution()
    laws = constitution.laws_for(KnowledgeCapability.PROVENANCE)
    assert any(law.law_id == "UKIP-LAW-004" for law in laws)


def test_to_dict_is_serializable_and_complete():
    document = knowledge_constitution().to_dict()
    assert document["complete"] is True
    assert len(document["laws"]) == len(KNOWLEDGE_LAWS)
    assert len(document["inherited_laws"]) == len(INTEGRATION_LAWS)
    assert len(document["capability_matrix"]) == 11
    assert document["laws"][0]["law_id"] == "UKIP-LAW-001"


# ---------------------------------------------------------------------------
# projection into the corpus it governs (UKIP-LAW-012)
# ---------------------------------------------------------------------------


def test_constitution_objects_are_constitutional_and_ratified():
    objects, decisions = constitution_objects()
    assert len(objects) == 2
    assert len(decisions) == 1
    for obj in objects:
        assert obj.authority is KnowledgeAuthority.CONSTITUTIONAL
        assert obj.lifecycle is Lifecycle.RATIFIED
        assert obj.verify_integrity()
    assert decisions[0].verify_integrity()
    assert decisions[0].is_reviewable


def test_projected_ids_are_the_declared_ones():
    objects, decisions = constitution_objects()
    ids = {obj.cko_id for obj in objects}
    assert ids == {
        KNOWLEDGE_INTELLIGENCE_PRINCIPLE_ID,
        KNOWLEDGE_INTELLIGENCE_DECISION_OBJECT_ID,
    }
    assert decisions[0].decision_id == KNOWLEDGE_INTELLIGENCE_DECISION_RECORD_ID


def test_principle_is_subordinate_to_the_founding_principle():
    objects, _ = constitution_objects()
    principle = next(o for o in objects if o.cko_id == KNOWLEDGE_INTELLIGENCE_PRINCIPLE_ID)
    assert KNOWLEDGE_ONCE_PRINCIPLE in principle.dependencies
    assert INTEGRATION_PRINCIPLE_ID in principle.dependencies


def test_decision_object_links_its_record():
    objects, _ = constitution_objects()
    decision = next(o for o in objects if o.cko_id == KNOWLEDGE_INTELLIGENCE_DECISION_OBJECT_ID)
    assert decision.kind is KnowledgeKind.DECISION
    assert KNOWLEDGE_INTELLIGENCE_DECISION_RECORD_ID in decision.decision_links


def test_every_law_title_appears_in_the_projected_statement():
    """The projection must not silently omit a law it claims to record."""
    objects, _ = constitution_objects()
    principle = next(o for o in objects if o.cko_id == KNOWLEDGE_INTELLIGENCE_PRINCIPLE_ID)
    for law in KNOWLEDGE_LAWS:
        assert law.law_id in principle.statement
        assert law.title in principle.statement


def test_extend_base_is_additive_and_idempotent():
    base = build_seed_base()
    once = extend_base_with_knowledge_constitution(base)
    twice = extend_base_with_knowledge_constitution(once)
    # UKIP's two objects plus the UKI integration constitution it is subordinate to.
    assert len(once.objects()) > len(base.objects()) + 2
    assert once.has_object(KNOWLEDGE_INTELLIGENCE_PRINCIPLE_ID)
    assert once.has_object(INTEGRATION_PRINCIPLE_ID)
    assert once.object_ids() == twice.object_ids()
    assert once.decision_ids() == twice.decision_ids()
    # the original base is untouched (immutability)
    assert not base.has_object(KNOWLEDGE_INTELLIGENCE_PRINCIPLE_ID)


def test_extended_base_passes_ukda_validation():
    """The constitution must satisfy the rules it imposes on everything else."""
    extended = extend_base_with_knowledge_constitution(build_seed_base())
    report = validate_base(extended)
    assert report.accepted, report.to_dict()["findings"]
