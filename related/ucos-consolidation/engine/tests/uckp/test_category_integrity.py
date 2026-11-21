"""Provider category integrity, observed (`PHASE-UCF-011`).

`PHASE-UCF-005` added a fourth provider that populated `metadata`, `runtime` and
`artifact` — three categories already exclusively populated by native providers. Nothing
in the constitution refused it: a category is a classification, not a claim of identity,
so two providers populating one breaches no declared invariant. It was caught by an
unrelated assertion that happened to pin `by_category("metadata") == 33`, which is luck,
not a gate. These tests are the designed replacement for that luck.

The capability is *observational*, and the tests hold it to exactly that: it reports at
OBSERVATION severity and it cannot move a certification verdict. What it detects without
any declared side at all, and what these tests prove it detects, is the population
collision itself.

Every fixture pass here reads a deliberately **empty** resolution, because this module is
about the stage before a recognition exists: measurement, and what measurement alone may
say about it. `PHASE-UCF-015` has since written the repository's own
`category_ownership_resolution`, so defaulting to the live binding would make an assertion
about an undeclared category depend on which categories the repository happens to
recognise — the join against a *declared* side is `test_category_ownership_resolution.py`'s
subject, and the two must not drift into testing each other.

`RegistryView` is used rather than a real registry for the same reason the intelligence
suite already uses it: it puts the reasoner in front of a population the real admission
path would build only across several providers, without weakening admission itself.
"""

from __future__ import annotations

import dataclasses

import pytest

from engine.tests.uckp.doubles import RegistryView
from engine.uckp.identity import urn_for
from engine.uckp.intelligence import CATEGORY_EVIDENCE, OBSERVATION, build_intelligence
from engine.uckp.resolution import ResolutionReader
from engine.uckp.ucko import UCKO

CONTAMINATION = "and no declared owner reconciles them"
UNDECLARED = "an undeclared default, not a decision"
UNATTRIBUTED = "cannot be attributed to anyone"


def _undeclared() -> ResolutionReader:
    """A reader over a document that declares nothing — the observational stage, exactly.

    Absence is a lawful state that produces no complaint, so this is the *stage* under
    test rather than a stub of it: the same read path production uses, over a document
    that recognises nothing about any category.
    """
    return ResolutionReader.from_document({}, source="<no ledger>")


def _gap(*objects, vocabularies):
    view = RegistryView(objects, vocabularies=vocabularies)
    return build_intelligence(view, _undeclared()).reason("gap")


def _without_provider(obj: UCKO) -> UCKO:
    """An object naming no provider — unreachable through ``mint``, which coerces it."""
    return dataclasses.replace(obj, discovery=dataclasses.replace(obj.discovery, provider=""))


def _statements(result, category: str) -> str:
    """Every statement the reasoner made about one category, joined."""
    subject = f"category:{category}"
    return "\n".join(f.statement for f in result.findings if f.subject == subject)


# --- the contamination case: the defect PHASE-UCF-005 actually produced -------------


def test_two_providers_populating_one_category_are_reported(mint_object, vocabularies):
    """The `PHASE-UCF-005` defect class, in front of the check that exists to catch it."""
    root = urn_for("test", "ROOT")
    native = mint_object(
        "NATIVE", derives_from=root, category="metadata", provider="engine.uckp.constitution"
    )
    intruder = mint_object(
        "INTRUDER", derives_from=root, category="metadata", provider="engine.uckp.newcomer"
    )
    result = _gap(native, intruder, vocabularies=vocabularies)
    statements = _statements(result, "metadata")
    assert CONTAMINATION in statements
    assert "2 providers" in statements
    assert "engine.uckp.constitution (1), engine.uckp.newcomer (1)" in statements
    assert CATEGORY_EVIDENCE in statements
    assert result.observations["categories_multi_provider"] == 1.0


def test_a_contaminated_category_is_not_also_reported_as_merely_undeclared(
    mint_object, vocabularies
):
    """The two conditions are distinct; reporting both of one category would be noise."""
    root = urn_for("test", "ROOT")
    left = mint_object("L", derives_from=root, category="policy", provider="p.one")
    right = mint_object("R", derives_from=root, category="policy", provider="p.two")
    statements = _statements(_gap(left, right, vocabularies=vocabularies), "policy")
    assert CONTAMINATION in statements
    assert UNDECLARED not in statements


def test_contamination_is_reported_for_each_contested_category_independently(
    mint_object, vocabularies
):
    root = urn_for("test", "ROOT")
    objects = (
        mint_object("A", derives_from=root, category="metadata", provider="p.one"),
        mint_object("B", derives_from=root, category="metadata", provider="p.two"),
        mint_object("C", derives_from=root, category="runtime", provider="p.one"),
        mint_object("D", derives_from=root, category="runtime", provider="p.three"),
        mint_object("E", derives_from=root, category="policy", provider="p.one"),
    )
    result = _gap(*objects, vocabularies=vocabularies)
    assert CONTAMINATION in _statements(result, "metadata")
    assert CONTAMINATION in _statements(result, "runtime")
    assert CONTAMINATION not in _statements(result, "policy")
    assert result.observations["categories_multi_provider"] == 2.0


# --- the positive case: one provider, one category, nothing to reconcile ------------


def test_one_provider_populating_a_category_many_times_is_not_contamination(
    mint_object, vocabularies
):
    """Volume is not plurality. Ten objects from one provider contest nothing."""
    root = urn_for("test", "ROOT")
    objects = tuple(
        mint_object(f"OBJ-{index}", derives_from=root, category="runtime", provider="p.sole")
        for index in range(10)
    )
    result = _gap(*objects, vocabularies=vocabularies)
    assert CONTAMINATION not in _statements(result, "runtime")
    assert result.observations["categories_multi_provider"] == 0.0


def test_one_provider_spanning_several_categories_is_not_contamination(mint_object, vocabularies):
    """A provider may own breadth; the question is who else is in each category."""
    root = urn_for("test", "ROOT")
    objects = tuple(
        mint_object(f"OBJ-{category}", derives_from=root, category=category, provider="p.sole")
        for category in ("metadata", "runtime", "policy", "state")
    )
    result = _gap(*objects, vocabularies=vocabularies)
    assert result.observations["categories_multi_provider"] == 0.0
    assert result.observations["categories_populated"] == 4.0


# --- the unknown case: populated, uncontested, and never actually declared ----------


def test_an_uncontested_category_is_reported_as_undeclared_not_as_agreed(mint_object, vocabularies):
    """The distinction the whole observational stage exists to preserve.

    One populating provider is not evidence of authority — it is evidence of one
    populator. Reporting it as a pass would certify an undeclared default as a decision.
    """
    obj = mint_object(
        "ALONE", derives_from=urn_for("test", "ROOT"), category="runtime", provider="p.sole"
    )
    statements = _statements(_gap(obj, vocabularies=vocabularies), "runtime")
    assert UNDECLARED in statements
    assert "p.sole" in statements


def test_every_populated_category_counts_as_undeclared_while_no_owner_exists(
    mint_object, vocabularies
):
    root = urn_for("test", "ROOT")
    objects = tuple(
        mint_object(f"OBJ-{category}", derives_from=root, category=category, provider="p.sole")
        for category in ("metadata", "runtime", "policy")
    )
    result = _gap(*objects, vocabularies=vocabularies)
    assert result.observations["categories_without_declared_owner"] == 3.0


def test_an_unpopulated_governed_category_is_not_reported_as_undeclared(mint_object, vocabularies):
    """A category nobody populates has no ownership question to answer yet."""
    obj = mint_object(
        "ONLY", derives_from=urn_for("test", "ROOT"), category="runtime", provider="p.sole"
    )
    result = _gap(obj, vocabularies=vocabularies)
    assert UNDECLARED not in _statements(result, "metadata")
    assert "no canonical object yet" in _statements(result, "metadata")


# --- the blind spot: objects that name no provider at all ---------------------------


def test_an_object_naming_no_provider_is_reported_rather_than_skipped(mint_object, vocabularies):
    """The unattributed branch, put in front of a condition admission cannot produce.

    ``UCKO.mint`` coerces an empty provider to ``engine.uckp``, so this object cannot
    arrive through registration — stripping the field breaks the seal and the registry
    refuses it. That is exactly why ``RegistryView`` exists: dropping unattributed
    objects would let the reasoner report a clean attribution for a population it had
    not attributed, and a branch that never executes is a claim rather than a check.
    """
    obj = _without_provider(
        mint_object("NAMELESS", derives_from=urn_for("test", "ROOT"), category="runtime")
    )
    result = _gap(obj, vocabularies=vocabularies)
    statements = _statements(result, "runtime")
    assert UNATTRIBUTED in statements
    assert UNDECLARED not in statements
    assert result.observations["categories_unattributed"] == 1.0
    assert result.observations["categories_without_declared_owner"] == 0.0


def test_a_partly_attributed_category_reports_both_its_provider_and_its_shortfall(
    mint_object, vocabularies
):
    root = urn_for("test", "ROOT")
    named = mint_object("NAMED", derives_from=root, category="runtime", provider="p.sole")
    nameless = _without_provider(mint_object("NAMELESS", derives_from=root, category="runtime"))
    statements = _statements(_gap(named, nameless, vocabularies=vocabularies), "runtime")
    assert UNDECLARED in statements
    assert UNATTRIBUTED in statements
    assert "1 of its 2 objects name no provider" in statements


# --- the evidence model: no anonymous findings --------------------------------------


def test_every_category_finding_names_its_subject_category_and_evidence_source(
    mint_object, vocabularies
):
    """A finding whose evidence cannot be recomputed by its reader is an assertion.

    Each observation must carry, in the fields the `Finding` model already has: which
    reasoning produced it, what it is about, the category, the providers, the source the
    claim was measured from, and the severity that states how far it may be relied on.
    """
    root = urn_for("test", "ROOT")
    left = mint_object("L", derives_from=root, category="metadata", provider="p.one")
    right = mint_object("R", derives_from=root, category="metadata", provider="p.two")
    result = _gap(left, right, vocabularies=vocabularies)
    finding = next(f for f in result.findings if f.subject == "category:metadata")
    assert finding.reasoning == "gap"
    assert finding.severity == OBSERVATION
    assert finding.subject == "category:metadata"
    assert "p.one" in finding.statement and "p.two" in finding.statement
    assert CATEGORY_EVIDENCE in finding.statement
    assert set(finding.to_dict()) == {"reasoning", "severity", "subject", "statement"}


def test_the_population_map_can_be_recomputed_from_the_evidence_a_finding_cites(
    mint_object, vocabularies
):
    """The cited source must actually be sufficient to reproduce the claim."""
    root = urn_for("test", "ROOT")
    objects = (
        mint_object("A", derives_from=root, category="metadata", provider="p.one"),
        mint_object("B", derives_from=root, category="metadata", provider="p.two"),
        mint_object("C", derives_from=root, category="metadata", provider="p.two"),
    )
    intelligence = build_intelligence(RegistryView(objects, vocabularies=vocabularies))
    recomputed: dict[str, dict[str, int]] = {}
    for obj in objects:  # using only the two facets CATEGORY_EVIDENCE names
        bucket = recomputed.setdefault(obj.taxonomy.category, {})
        bucket[obj.discovery.provider] = bucket.get(obj.discovery.provider, 0) + 1
    population = next(p for p in intelligence.category_populations() if p.category == "metadata")
    assert population.to_dict()["providers"] == recomputed["metadata"]
    assert population.to_dict()["evidence"] == CATEGORY_EVIDENCE
    assert population.objects == 3


def test_the_population_map_is_deterministic_and_provider_sorted(mint_object, vocabularies):
    root = urn_for("test", "ROOT")
    objects = (
        mint_object("A", derives_from=root, category="runtime", provider="p.zeta"),
        mint_object("B", derives_from=root, category="runtime", provider="p.alpha"),
    )
    intelligence = build_intelligence(RegistryView(objects, vocabularies=vocabularies))
    population = intelligence.category_populations()[0]
    assert population.providers == ("p.alpha", "p.zeta")
    assert population.by_provider == (("p.alpha", 1), ("p.zeta", 1))


def test_category_usage_discovery_infers_no_ownership(mint_object, vocabularies):
    """Population is a discovery fact (Facet 21), never an authority or ownership one.

    The map must not acquire an owner field by convenience: `PHASE-UCF-008` established
    that treating a Provider fact as an Owner fact is exactly the substitution that let
    `PHASE-UCF-005`'s contamination through in the first place.
    """
    obj = mint_object(
        "SOLE",
        derives_from=urn_for("test", "ROOT"),
        category="runtime",
        provider="p.sole",
        owner="someone-else",
    )
    intelligence = build_intelligence(RegistryView((obj,), vocabularies=vocabularies))
    population = intelligence.category_populations()[0]
    assert set(population.to_dict()) == {
        "category",
        "providers",
        "unattributed",
        "objects",
        "evidence",
    }
    assert "owner" not in population.to_dict()
    assert "someone-else" not in _statements(_gap(obj, vocabularies=vocabularies), "runtime")


# --- the capability observes; it never gates ----------------------------------------


def test_every_category_integrity_finding_is_an_observation(mint_object, vocabularies):
    """Advisory by construction: a violation here would gate certification."""
    root = urn_for("test", "ROOT")
    left = mint_object("L", derives_from=root, category="metadata", provider="p.one")
    right = mint_object("R", derives_from=root, category="metadata", provider="p.two")
    nameless = _without_provider(mint_object("N", derives_from=root, category="runtime"))
    sole = mint_object("S", derives_from=root, category="policy", provider="p.three")
    result = _gap(left, right, nameless, sole, vocabularies=vocabularies)
    category_findings = [f for f in result.findings if f.subject.startswith("category:")]
    statements = "\n".join(f.statement for f in category_findings)
    assert CONTAMINATION in statements
    assert UNDECLARED in statements
    assert UNATTRIBUTED in statements
    assert all(f.severity == OBSERVATION for f in category_findings)
    assert result.violations == ()
    assert result.clean is True


def test_contamination_does_not_move_the_universe_verdict(universe):
    """The stage is observational: certification must be indifferent to these findings."""
    from engine.uckp.validation import validate_universe

    assert validate_universe(universe).certified is True
    assert universe.intelligence().report()["clean"] is True


def test_observing_category_integrity_mutates_no_canonical_state(universe):
    """Canonical safety: reasoning reports, and reporting must leave no trace.

    Registry population, object seals, the graph fingerprint and the certification
    verdict are each sampled before and after a full reasoning pass. Article 15 permits
    the universe to reason about itself; it does not permit reasoning to change it.
    """
    before_ids = universe.registry.ids()
    before_digests = {obj.ucko_id: obj.semantic_digest() for obj in universe.registry.objects()}
    before_fingerprint = universe.graph().fingerprint()

    universe.intelligence().category_populations()
    universe.intelligence().reason("gap")
    universe.intelligence().report()

    assert universe.registry.ids() == before_ids
    assert {
        obj.ucko_id: obj.semantic_digest() for obj in universe.registry.objects()
    } == before_digests
    assert universe.graph().fingerprint() == before_fingerprint
    assert all(obj.verify_integrity() for obj in universe.registry.objects())


def test_reasoning_twice_reports_identically(universe):
    """No accumulation: a second pass must not see the first one's output."""
    first = universe.intelligence().reason("gap")
    second = universe.intelligence().reason("gap")
    assert first.to_dict() == second.to_dict()


def test_category_integrity_reasoning_is_deterministic(mint_object, vocabularies):
    root = urn_for("test", "ROOT")
    left = mint_object("L", derives_from=root, category="metadata", provider="p.two")
    right = mint_object("R", derives_from=root, category="metadata", provider="p.one")
    first = _gap(left, right, vocabularies=vocabularies)
    second = _gap(right, left, vocabularies=vocabularies)
    assert first.to_dict() == second.to_dict()


# --- the real repository, measured rather than assumed ------------------------------


@pytest.fixture(scope="module")
def live_populations(universe):
    """The live provider-per-category map, measured from the assembled universe."""
    populations: dict[str, set[str]] = {}
    for obj in universe.registry.objects():
        populations.setdefault(obj.taxonomy.category, set()).add(obj.discovery.provider)
    return populations


def test_no_category_in_this_repository_is_populated_by_two_providers(live_populations):
    """The regression gate `PHASE-UCF-005` did not have.

    Measured, never a snapshot literal: a fifth provider that contaminates an existing
    category fails here by construction, and legitimate growth that adds *new* categories
    does not — which is the distinction the count assertion that caught `PHASE-UCF-005`
    by accident could not draw.
    """
    contested = {
        category: sorted(providers)
        for category, providers in live_populations.items()
        if len(providers) > 1
    }
    assert contested == {}, f"category contamination: {contested}"


def test_every_object_in_this_repository_names_the_provider_that_minted_it(live_populations):
    unattributed = sorted(
        category for category, providers in live_populations.items() if "" in providers
    )
    assert unattributed == []


def test_the_live_population_map_is_what_the_reasoner_reports(universe, live_populations):
    """The reasoner's own measurement must agree with a directly-computed one."""
    gap = universe.intelligence().reason("gap")
    assert gap.observations["categories_populated"] == float(len(live_populations))
    assert gap.observations["categories_multi_provider"] == 0.0
    assert gap.observations["categories_unattributed"] == 0.0
    assert gap.observations["categories_without_declared_owner"] == 0.0


def test_every_populated_category_now_carries_a_declared_recognition(universe, live_populations):
    """The Observational stage's precondition, and what `PHASE-UCF-015` did to it.

    This assertion used to read ``categories_without_declared_owner > 0`` and was written
    to be the first test that failed once a `category_ownership_resolution` ledger existed
    (`PHASE-UCF-010` B1–B3). The ledger now exists, so the signal has fired and the
    assertion is inverted rather than deleted: every category this repository populates is
    recognised, and the count that used to prove the absence now proves the coverage.

    It is still measured, never a snapshot literal — a category populated tomorrow by a
    provider nobody has recognised fails here, which is the property `PHASE-UCF-014` R4a
    requires the write to preserve.
    """
    gap = universe.intelligence().reason("gap")
    assert gap.observations["categories_without_declared_owner"] == 0.0
    assert gap.observations["categories_recognised"] == float(len(live_populations))
    assert gap.observations["categories_ownership_unknown"] == 0.0
    assert gap.observations["categories_ownership_conflict"] == 0.0
