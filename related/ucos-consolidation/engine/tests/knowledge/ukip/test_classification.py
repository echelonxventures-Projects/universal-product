"""UKIP Part 04 — total, deterministic, explained classification."""

from __future__ import annotations

import pytest

from engine.knowledge.model import KnowledgeAuthority, KnowledgeKind, Lifecycle
from engine.knowledge.ukip.classification import (
    DEFAULT_OWNER,
    DEFAULT_RULES,
    DEFAULT_UNIVERSE,
    DEFAULT_VERSION,
    FACETS,
    ClassificationRule,
    Facet,
    KnowledgeClassifier,
    classify_unit,
)
from engine.knowledge.ukip.contracts import ProviderKind
from engine.knowledge.ukip.errors import ClassificationError
from engine.tests.knowledge.ukip.conftest import make_source, make_unclassified, make_unit

# ---------------------------------------------------------------------------
# totality (UKIP-LAW-005)
# ---------------------------------------------------------------------------


def test_classification_is_total_for_a_bare_unit():
    """Every facet must be decided; there is no 'unknown' bucket."""
    result = classify_unit(make_unclassified("bare"))
    assert result.kind in set(KnowledgeKind)
    assert result.authority in set(KnowledgeAuthority)
    assert result.lifecycle in set(Lifecycle)
    assert result.universe and result.owner and result.version
    assert {d.facet for d in result.decisions} == set(FACETS)


def test_applying_a_classification_marks_the_unit_classified():
    unit = make_unclassified("bare")
    assert not unit.is_classified
    assert classify_unit(unit).apply(unit).is_classified


def test_every_facet_records_a_rule_and_evidence():
    result = classify_unit(make_unclassified("bare"))
    for decision in result.decisions:
        assert decision.rule_id
        assert decision.evidence


def test_fallbacks_are_real_values_not_placeholders():
    result = classify_unit(make_unclassified("nothing", title="zzz", statement="qqq wwww eeee."))
    assert result.universe == DEFAULT_UNIVERSE
    assert result.owner == DEFAULT_OWNER
    assert result.version == DEFAULT_VERSION


# ---------------------------------------------------------------------------
# provider-declared facets win
# ---------------------------------------------------------------------------


def test_provider_declared_facets_are_never_second_guessed():
    """A provider that already knows the answer must not be overridden."""
    unit = make_unit(
        "declared",
        statement="This constitutional principle governs architecture.",
        kind=KnowledgeKind.ANTI_PATTERN,
        authority=KnowledgeAuthority.ADVISORY,
        lifecycle=Lifecycle.ARCHIVED,
        universe="MINE",
        owner="ME",
        version="7.7.7",
    )
    result = classify_unit(unit)
    assert result.kind is KnowledgeKind.ANTI_PATTERN
    assert result.authority is KnowledgeAuthority.ADVISORY
    assert result.lifecycle is Lifecycle.ARCHIVED
    assert result.universe == "MINE"
    assert result.owner == "ME"
    assert result.version == "7.7.7"
    assert set(result.rule_ids()) == {"provider-declared"}


def test_partially_declared_units_only_infer_the_rest():
    unit = make_unclassified("partial", statement="A policy about deployment.")
    unit = unit.with_classification(
        kind=KnowledgeKind.POLICY,
        authority=KnowledgeAuthority.ENGINEERING,
        lifecycle=Lifecycle.OPERATIONAL,
        universe="",
        owner="",
        version="",
    )
    result = classify_unit(unit)
    assert result.decision(Facet.KIND).rule_id == "provider-declared"
    assert result.decision(Facet.UNIVERSE).rule_id != "provider-declared"


# ---------------------------------------------------------------------------
# rule resolution
# ---------------------------------------------------------------------------


def test_attribute_hint_beats_textual_signal():
    unit = make_unclassified(
        "hinted",
        statement="A pattern for structuring things.",
        attributes=(("kind_hint", "decision"),),
    )
    result = classify_unit(unit)
    assert result.kind is KnowledgeKind.DECISION
    assert result.decision(Facet.KIND).rule_id == "kind-hint-attribute"


def test_provider_kind_decides_when_text_is_silent():
    unit = make_unclassified(
        "from-log",
        statement="Chosen approach recorded here.",
        source=make_source(locator="d-1", kind=ProviderKind.DECISION_LOG),
    )
    result = classify_unit(unit)
    assert result.kind is KnowledgeKind.DECISION


def test_tag_signal_decides_authority():
    unit = make_unclassified("tagged", statement="Neutral wording.", tags=("constitution",))
    assert classify_unit(unit).authority is KnowledgeAuthority.CONSTITUTIONAL


def test_textual_signals_pick_specific_kinds():
    cases = {
        "This is an anti-pattern to avoid.": KnowledgeKind.ANTI_PATTERN,
        "A best practice for teams.": KnowledgeKind.BEST_PRACTICE,
        "The guiding principle of the system.": KnowledgeKind.PRINCIPLE,
        "A constraint: callers must not block.": KnowledgeKind.CONSTRAINT,
        "The retention policy applies.": KnowledgeKind.POLICY,
        "An exception was granted here.": KnowledgeKind.EXCEPTION,
    }
    for statement, expected in cases.items():
        assert classify_unit(make_unclassified("k", statement=statement)).kind is expected


def test_lifecycle_and_universe_signals():
    ratified = classify_unit(make_unclassified("r", statement="This ratified rule is in force."))
    assert ratified.lifecycle is Lifecycle.RATIFIED
    ops = classify_unit(make_unclassified("o", statement="Deployment operations runbook steps."))
    assert ops.universe == "OPERATIONS"


def test_precedence_orders_rules_deterministically():
    classifier = KnowledgeClassifier()
    kind_rules = classifier.rules_for(Facet.KIND)
    precedences = [r.precedence for r in kind_rules]
    assert precedences == sorted(precedences)


def test_rules_are_globally_sorted_by_precedence_then_id():
    classifier = KnowledgeClassifier()
    keys = [r.order_key for r in classifier.rules]
    assert keys == sorted(keys)


# ---------------------------------------------------------------------------
# extensibility without modification
# ---------------------------------------------------------------------------


def test_extra_rules_can_pre_empt_a_built_in_rule():
    override = ClassificationRule(
        rule_id="custom-owner",
        facet=Facet.OWNER,
        value="TEAM-CUSTOM",
        terms=("widget",),
        precedence=1,
    )
    classifier = KnowledgeClassifier(extra_rules=[override])
    result = classifier.classify(make_unclassified("w", statement="A widget behaviour."))
    assert result.owner == "TEAM-CUSTOM"
    assert result.decision(Facet.OWNER).rule_id == "custom-owner"


def test_extra_rule_with_an_existing_id_replaces_it():
    replacement = ClassificationRule(
        rule_id="universe-governance",
        facet=Facet.UNIVERSE,
        value="REPLACED",
        terms=("governance",),
        precedence=10,
    )
    classifier = KnowledgeClassifier(extra_rules=[replacement])
    assert len(classifier.rules) == len(DEFAULT_RULES)
    result = classifier.classify(make_unclassified("g", statement="A governance concern here."))
    assert result.universe == "REPLACED"


def test_a_wholly_custom_rule_set_is_accepted():
    only = ClassificationRule(
        rule_id="only", facet=Facet.KIND, value=KnowledgeKind.RULE.value, terms=("x",)
    )
    classifier = KnowledgeClassifier(rules=[only])
    assert classifier.rules == (only,)
    result = classifier.classify(make_unclassified("k", statement="x marks it."))
    assert result.kind is KnowledgeKind.RULE


def test_custom_fallback_kind_is_honoured():
    classifier = KnowledgeClassifier(rules=[], fallback_kind=KnowledgeKind.REFERENCE)
    result = classifier.classify(make_unclassified("k", statement="zzz qqq."))
    assert result.kind is KnowledgeKind.REFERENCE


def test_strict_mode_rejects_an_undecidable_facet():
    classifier = KnowledgeClassifier(rules=[], strict=True)
    with pytest.raises(ClassificationError):
        classifier.classify(make_unclassified("k", statement="zzz qqq."))


def test_strict_mode_accepts_a_fully_declared_unit():
    classifier = KnowledgeClassifier(rules=[], strict=True)
    result = classifier.classify(make_unit("declared"))
    assert result.kind is KnowledgeKind.FACT


# ---------------------------------------------------------------------------
# determinism + serialization
# ---------------------------------------------------------------------------


def test_classification_is_reproducible():
    unit = make_unclassified("k", statement="A repeated architectural decision.")
    assert classify_unit(unit).to_dict() == classify_unit(unit).to_dict()


def test_classify_all_applies_and_reports():
    units = (make_unclassified("a"), make_unclassified("b"))
    results = KnowledgeClassifier().classify_all(units)
    assert len(results) == 2
    for unit, classification in results:
        assert unit.is_classified
        assert classification.decisions


def test_rule_and_classifier_serialization():
    classifier = KnowledgeClassifier()
    document = classifier.to_dict()
    assert document["rule_count"] == len(classifier.rules)
    assert document["facets"] == [f.value for f in FACETS]
    assert len(document["rules"]) == len(classifier.rules)
    rule = next(r for r in classifier.rules if r.attribute is not None)
    assert rule.to_dict()["attribute"] == list(rule.attribute)


def test_classification_to_dict_shape():
    document = classify_unit(make_unit("k")).to_dict()
    assert set(document) == {
        "kind",
        "authority",
        "lifecycle",
        "universe",
        "owner",
        "version",
        "decisions",
    }
    assert document["decisions"][0]["facet"] in {f.value for f in FACETS}


def test_missing_facet_decision_lookup_returns_none():
    classifier = KnowledgeClassifier(rules=[])
    result = classifier.classify(make_unit("k"))
    assert result.decision(Facet.KIND) is not None
    stripped = type(result)(
        kind=result.kind,
        authority=result.authority,
        lifecycle=result.lifecycle,
        universe=result.universe,
        owner=result.owner,
        version=result.version,
        decisions=(),
    )
    assert stripped.decision(Facet.KIND) is None
    assert stripped.rule_ids() == ()
