"""UKIP Part 10 — assimilation when a provider, a unit or a screen says no.

WHY THIS MODULE EXISTS. Assimilation's design claim is containment: one broken provider
must not corrupt the run, and one unclassifiable unit must not lose the other units in
the same batch. Both are implemented as ledger entries with a FAILED disposition — and
neither had ever been produced by a test, so the containment was asserted in prose and
demonstrated nowhere. ``strict=True`` is the paired claim (contain nothing, raise
instead) and was equally unexercised, as was the screening path that withholds a *near*
duplicate while admitting an exact one as corroboration.
"""

from __future__ import annotations

import pytest

from engine.knowledge.ukip.assimilation import (
    Disposition,
    KnowledgeAssimilator,
    assimilate_base,
)
from engine.knowledge.ukip.classification import KnowledgeClassifier
from engine.knowledge.ukip.contracts import ProviderKind
from engine.knowledge.ukip.errors import AssimilationError, ProviderError
from engine.knowledge.ukip.providers import (
    CallableProvider,
    ProviderDescriptor,
    ProviderRegistry,
)

from .conftest import make_provider, unit_from


def _descriptor(provider_id: str, **overrides) -> ProviderDescriptor:
    return ProviderDescriptor(
        provider_id=provider_id,
        kind=ProviderKind.DOCUMENT,
        title=f"Provider {provider_id}",
        **overrides,
    )


def _failing_provider(provider_id: str = "broken") -> CallableProvider:
    def _raise() -> None:
        raise RuntimeError("the source could not be read")

    return CallableProvider(_descriptor(provider_id), _raise)


# -- a provider that fails ------------------------------------------------------------


def test_a_failing_provider_is_contained_and_the_rest_of_the_run_completes():
    good = make_provider("good", (unit_from("good", "a", "Alpha statement."),))
    report = KnowledgeAssimilator().assimilate(ProviderRegistry((_failing_provider(), good)))

    assert len(report.registry) == 1
    assert [e.provider_id for e in report.failures] == ["broken"]
    (failure,) = report.failures
    assert failure.disposition is Disposition.FAILED
    assert failure.unit_key == "*"
    assert failure.reason.startswith("provider error:")
    assert report.entries_for("broken") == report.failures
    assert len(report.entries_for("good")) == 1
    assert report.accepted is False


def test_strict_mode_raises_rather_than_containing_a_failing_provider():
    with pytest.raises(AssimilationError) as excinfo:
        KnowledgeAssimilator(strict=True).assimilate(ProviderRegistry((_failing_provider(),)))
    assert "provider failed during assimilation" in str(excinfo.value)


def test_a_provider_that_returns_something_that_is_not_units_is_a_provider_error():
    provider = CallableProvider(_descriptor("stringy"), lambda: "not units")
    with pytest.raises(ProviderError):
        provider.units()
    report = KnowledgeAssimilator().assimilate(ProviderRegistry((provider,)))
    assert [e.disposition for e in report.ledger] == [Disposition.FAILED]


# -- a unit that cannot be classified -------------------------------------------------


class _RefusingClassifier(KnowledgeClassifier):
    """A classifier that refuses one nominated unit and classifies everything else."""

    def __init__(self, refuse_key: str) -> None:
        super().__init__()
        self._refuse_key = refuse_key

    def classify(self, unit):  # type: ignore[override]
        if unit.key == self._refuse_key:
            raise ValueError("no rule decided this unit")
        return super().classify(unit)


def test_an_unclassifiable_unit_is_contained_and_its_batch_mates_still_land():
    provider = make_provider(
        "mixed",
        (
            unit_from("mixed", "keep", "Keepable statement."),
            unit_from("mixed", "refuse", "Refusable statement."),
        ),
    )
    report = KnowledgeAssimilator(classifier=_RefusingClassifier("refuse")).assimilate(
        ProviderRegistry((provider,))
    )
    assert len(report.registry) == 1
    (failure,) = report.failures
    assert failure.unit_key == "refuse"
    assert failure.disposition is Disposition.FAILED
    assert failure.reason.startswith("classification error:")


def test_strict_mode_raises_rather_than_containing_an_unclassifiable_unit():
    provider = make_provider("mixed", (unit_from("mixed", "refuse", "Refusable statement."),))
    assimilator = KnowledgeAssimilator(classifier=_RefusingClassifier("refuse"), strict=True)
    with pytest.raises(AssimilationError) as excinfo:
        assimilator.assimilate(ProviderRegistry((provider,)))
    assert "unit could not be classified" in str(excinfo.value)


def test_the_classifier_in_use_is_the_one_that_was_supplied():
    classifier = _RefusingClassifier("nothing")
    assert KnowledgeAssimilator(classifier=classifier).classifier is classifier
    assert isinstance(KnowledgeAssimilator().classifier, KnowledgeClassifier)


# -- screening ------------------------------------------------------------------------


def test_screening_withholds_a_near_duplicate_and_names_what_to_reuse_instead():
    first = unit_from(
        "alpha",
        "canonical",
        "Deterministic canonical ordering keeps every emitted artifact stable.",
    )
    near = unit_from(
        "beta",
        "restated",
        "Deterministic canonical ordering keeps every emitted artifact stable indeed.",
        title=first.title,
        rationale=first.rationale,
    )
    report = KnowledgeAssimilator(screen=True).assimilate(
        ProviderRegistry((make_provider("alpha", (first,)), make_provider("beta", (near,))))
    )
    skipped = report.skipped()
    assert len(skipped) == 1
    assert skipped[0].provider_id == "beta"
    assert skipped[0].reason.startswith("reuse ")
    assert skipped[0].knowledge_id in report.registry
    assert len(report.registry) == 1


def test_screening_admits_an_exact_duplicate_as_corroboration_rather_than_skipping_it():
    left = unit_from("alpha", "shared", "One statement two providers agree on.")
    right = unit_from("beta", "shared", "One statement two providers agree on.")
    report = KnowledgeAssimilator(screen=True).assimilate(
        ProviderRegistry((make_provider("alpha", (left,)), make_provider("beta", (right,))))
    )
    assert report.skipped() == ()
    assert len(report.corroborated()) == 1
    (record,) = report.registry.records()
    assert record.provider_ids == ("alpha", "beta")


def test_an_authoritative_provider_is_never_screened():
    first = unit_from(
        "alpha",
        "canonical",
        "Deterministic canonical ordering keeps every emitted artifact stable.",
    )
    near = unit_from(
        "beta",
        "restated",
        "Deterministic canonical ordering keeps every emitted artifact stable indeed.",
        title=first.title,
        rationale=first.rationale,
    )
    report = KnowledgeAssimilator(screen=True).assimilate(
        ProviderRegistry(
            (
                make_provider("alpha", (first,), priority=1),
                make_provider("beta", (near,), authoritative=True, priority=2),
            )
        )
    )
    assert report.skipped() == ()
    assert len(report.registry) == 2


# -- the report -----------------------------------------------------------------------


def test_an_unrelated_record_gets_no_relationship_provenance_step():
    """The RELATED stage is appended only for records that ended up wired into the
    graph; a record in no relationship is skipped rather than given an empty step."""
    report = KnowledgeAssimilator().assimilate(
        ProviderRegistry((make_provider("solo", (unit_from("solo", "a", "Alpha statement."),)),))
    )
    (record,) = report.registry.records()
    assert report.relationships.degree(record.knowledge_id) == 0
    assert all(step.stage.value != "related" for step in record.provenance.steps)


def test_assimilation_creates_no_duplicate_records(seed_report):
    assert seed_report.duplicates_created == 0
    assert seed_report.accepted is True
    assert seed_report.failures == ()


def test_the_report_projects_the_registry_as_a_ukda_base(seed_report):
    base = seed_report.to_knowledge_base()
    assert len(base.objects()) == len(seed_report.registry)
    assert base.decisions() == seed_report.decisions


def test_the_convenience_entry_point_composes_canonical_and_extra_providers(seed_base):
    extra = make_provider("extra", (unit_from("extra", "x", "Extra provider statement."),))
    report = assimilate_base(seed_base, extra_providers=(extra,))
    assert "extra" in report.provider_ids
    assert report.decisions == tuple(seed_base.decisions())
    assert any(e.provider_id == "extra" for e in report.ledger)
