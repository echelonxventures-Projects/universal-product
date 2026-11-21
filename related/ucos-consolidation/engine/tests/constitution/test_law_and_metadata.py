"""UCOS-CEL-0001 — the law is data, and the metadata mandate refuses incompleteness.

Two properties are load-bearing for everything else in the package and are asserted here
rather than assumed: that extending the law is a data edit (so no function branches on a
clause), and that an incomplete artifact is refused all four faculties at once rather than
being quietly executable-but-not-certifiable.
"""

from __future__ import annotations

import dataclasses

import pytest

from engine.constitution import (
    acceptance,
    assimilation,
    authority,
    evolution,
    gateway,
    law,
    legality,
    metadata,
    planner,
    replay,
    state,
)
from engine.constitution.errors import ConstitutionalError, MetadataIncomplete
from engine.tests.constitution.conftest import declare, population


def test_the_law_is_deterministic_and_addressable() -> None:
    assert law.digest() == law.digest()
    assert law.clause("CEL-01").realized_by == "UCOS-CDG-000001"
    assert law.invariant("CEL-INV-07").clause_id == "CEL-05"
    assert set(law.blocking_invariant_ids()) == {i.invariant_id for i in law.EXECUTION_INVARIANTS}


def test_every_acceptance_criterion_names_a_declared_invariant() -> None:
    """A criterion measured by nothing is prose, which the law does not admit."""
    declared = {i.invariant_id for i in law.EXECUTION_INVARIANTS}
    for criterion in law.ACCEPTANCE_CRITERIA:
        assert criterion.invariant_id in declared, criterion.criterion_id


def test_every_clause_names_the_engine_that_realizes_it() -> None:
    for clause in law.EXECUTION_CLAUSES:
        assert clause.realized_by, clause.clause_id
        assert clause.refuses, clause.clause_id


def test_unknown_clause_and_invariant_fail_closed() -> None:
    with pytest.raises(ConstitutionalError):
        law.clause("CEL-99")
    with pytest.raises(ConstitutionalError):
        law.invariant("CEL-INV-99")


def test_the_mandate_declares_fifteen_facets() -> None:
    assert len(metadata.MANDATED_FACETS) == 15
    assert metadata.facet("canonical_owner").singular
    assert "canonical_owner" in metadata.graph_bearing_facets()
    assert "replay_rules" not in metadata.graph_bearing_facets()


def test_an_incomplete_artifact_loses_all_four_faculties_together() -> None:
    partial = metadata.ConstitutionalMetadata.declare(
        "partial", universal_id="", canonical_owner=("ext:owner",)
    )
    assert not partial.complete
    assert not partial.executable
    assert not partial.governable
    assert not partial.certifiable
    assert not partial.registerable
    assert "dependencies" in partial.missing_facets()

    with pytest.raises(MetadataIncomplete) as excinfo:
        metadata.require_complete(partial)
    assert "dependencies" in excinfo.value.detail["missing_facets"]


def test_two_owners_is_as_incomplete_as_none() -> None:
    """NL-04's shape, restated for CEL-09: the question must have exactly one answer."""
    two = declare("two", canonical_owner=("ext:a", "ext:b"))
    assert "canonical_owner" in two.missing_facets()
    assert two.canonical_owner == ""


def test_an_unknown_facet_is_refused_rather_than_ignored() -> None:
    """A typo'd facet would otherwise read as a silently absent obligation."""
    with pytest.raises(ConstitutionalError) as excinfo:
        metadata.ConstitutionalMetadata.declare("x", universal_id="y", dependancies=("a",))
    assert excinfo.value.detail["unknown"] == ["dependancies"]


def test_external_references_terminate_rather_than_dangle() -> None:
    record = declare("terminal")
    assert record.referents("authorities") == ()
    assert record.external_references("authorities") == ("ext:UCOS-DETERMINATION-TEST",)
    assert "authorities" in record.terminal_facets()
    assert metadata.is_external("ext:anything")
    assert not metadata.is_external("subject.key")


def test_a_population_refuses_two_declarations_of_one_subject() -> None:
    with pytest.raises(ConstitutionalError) as excinfo:
        metadata.Population.of([declare("same"), declare("same")])
    assert excinfo.value.detail["subject"] == "same"


def test_a_population_is_immutable_and_with_records_returns_a_new_one() -> None:
    base = metadata.Population.of([declare("a")])
    grown = base.with_records([declare("b")])
    assert base.subjects() == ("a",)
    assert grown.subjects() == ("a", "b")
    assert base.digest() != grown.digest()


def test_declarations_normalize_deterministically() -> None:
    """Duplicate and whitespace-only entries collapse, so a digest is stable."""
    messy = declare("messy", constraints=("  a  ", "a", "", "b"))
    assert messy.entries("constraints") == ("a", "b")
    assert messy.digest() == declare("messy", constraints=("a", "b")).digest()


# ---------------------------------------------------------------------------------------
# Every engine describes itself, and the description is a measurement rather than prose
# ---------------------------------------------------------------------------------------
#
# Ten modules in this package publish a `to_document()` and a `digest()`. They are the
# machine-readable answer to "what does this engine enforce", and every governance surface
# outside the package reads them rather than the source. Not one had a caller in the suite,
# so ten self-descriptions could have gone stale, gone empty, or stopped being deterministic
# with no failure anywhere — the exact shape of an unmeasured claim.


#: The nine engines that publish one, named as MODULE OBJECTS rather than as strings.
#
# A string list would have to be resolved with `importlib.import_module`, whose argument
# is then computed — and Ω-3 counts a dynamic import with a computed argument as an
# UNRESOLVED site, because no edge can be measured through it. Four such calls raised
# `unresolved_dynamic_sites` from 22 to 26 and the Ω-4 ratchet refused the run. Naming the
# modules is the same test with a resolvable import graph.
CONSTITUTIONAL_DOCUMENTS = (
    acceptance,
    assimilation,
    authority,
    evolution,
    gateway,
    legality,
    planner,
    replay,
    state,
)


@pytest.mark.parametrize(
    "module",
    CONSTITUTIONAL_DOCUMENTS,
    ids=[m.__name__.rsplit(".", 1)[-1] for m in CONSTITUTIONAL_DOCUMENTS],
)
def test_every_engine_publishes_a_deterministic_self_description(module) -> None:
    """Each document names its own schema and its own engine, and hashes to one value.

    DETERMINISM IS THE PART THAT MATTERS. These digests are what an external gate compares
    against a sealed expectation, so a document built from an unsorted set or carrying a
    clock would make every such comparison fail intermittently and be silenced rather than
    fixed. Two calls in one process is the cheapest witness that the bytes are a function of
    the declaration and of nothing else.
    """
    document = module.to_document()
    assert document["schema"].startswith("ucos-constitutional-")
    assert document["version"]
    assert document == module.to_document(), "the self-description is not deterministic"

    assert module.digest() == module.digest()
    assert len(module.digest()) == 64


def test_no_two_engines_claim_the_same_schema_or_the_same_digest() -> None:
    """Nine documents, nine schemas, nine digests.

    A shared schema would make two engines indistinguishable to a consumer reading their
    documents, and a shared digest would mean two different enforcement models hash alike —
    which would let one be swapped for the other under a comparison that still passed.
    """

    schemas = [module.to_document()["schema"] for module in CONSTITUTIONAL_DOCUMENTS]
    assert len(set(schemas)) == len(schemas), sorted(schemas)

    digests = [module.digest() for module in CONSTITUTIONAL_DOCUMENTS]
    assert len(set(digests)) == len(digests)


def test_every_engine_declares_its_set_open_to_registration() -> None:
    """``closed_set: False`` is a constitutional claim, not a formatting detail.

    UCKP-ART-17 admits an unknown future category by REGISTRATION and never by amendment,
    so an engine publishing a closed set would be declaring that its own vocabulary is
    final. Asserting it here means the claim is measured in the one place a consumer reads.

    ``acceptance`` states no ``closed_set`` and is not made to: it publishes counts of the
    invariants and criteria it MEASURES rather than a vocabulary it admits into, so the
    question the key answers is not one it is asked. Whichever documents declare the key
    must declare it False, and at least one must — otherwise this test passes by finding
    nothing.
    """

    declaring = 0
    for module in CONSTITUTIONAL_DOCUMENTS:
        document = module.to_document()
        if "closed_set" in document:
            declaring += 1
            assert document["closed_set"] is False, module.__name__
    assert declaring >= len(CONSTITUTIONAL_DOCUMENTS) - 1


# ---------------------------------------------------------------------------------------
# The mandate's own lookups and coercions, driven into their refusals
# ---------------------------------------------------------------------------------------


def test_asking_for_a_facet_the_mandate_does_not_declare_names_what_is_allowed() -> None:
    """A typo'd facet id is the realistic caller error, and returning None would make it a
    silently absent obligation — the exact failure CEL-09 exists to remove. The refusal
    lists every allowed id, so the caller is corrected rather than merely stopped."""
    assert metadata.facet("dependencies").facet_id == "dependencies"

    with pytest.raises(ConstitutionalError) as excinfo:
        metadata.facet("dependancies")
    assert excinfo.value.detail["facet_id"] == "dependancies"
    assert set(excinfo.value.detail["allowed"]) == set(metadata.facet_ids())


def test_asking_a_population_for_a_subject_it_does_not_declare_fails_closed() -> None:
    """``get`` is the resolving accessor every engine in this package calls. Returning None
    would push the absence downstream, where it becomes an AttributeError inside whichever
    proof happened to touch it first — an error naming the proof rather than the gap."""
    people = population(declare("root"))
    assert people.get("root").subject == "root"

    with pytest.raises(ConstitutionalError) as excinfo:
        people.get("ghost")
    assert excinfo.value.detail["subject"] == "ghost"


def test_a_facet_value_that_is_neither_a_string_nor_an_iterable_of_them_is_refused() -> None:
    """COERCION IS NOT PARSING. A facet is a set of subject tokens, and anything that is not
    one is refused with the value shown, because the alternative — ``str()`` on whatever
    arrived — would turn ``7`` into the token ``"7"`` and a real declaration error into a
    relation pointing at a subject nobody named."""
    assert declare("ok", constraints="deterministic").entries("constraints") == ("deterministic",)
    assert declare("ok", constraints=None).entries("constraints") == ()

    with pytest.raises(ConstitutionalError) as excinfo:
        declare("bad", constraints=7)
    assert excinfo.value.detail["facet_id"] == "constraints"
    assert "7" in excinfo.value.detail["value"]

    with pytest.raises(ConstitutionalError) as excinfo:
        declare("bad", constraints=("deterministic", 7))
    assert "entry must be a string" in str(excinfo.value)


def test_a_declaration_that_names_no_subject_is_refused() -> None:
    """An unnamed declaration is an obligation attached to nothing. It would enter a
    population under an empty key and satisfy every count while governing no artifact."""
    for nameless in ("", "   ", None, 7):
        with pytest.raises(ConstitutionalError, match="must name its subject"):
            metadata.ConstitutionalMetadata.declare(nameless, universal_id="x")


def test_a_non_blocking_facet_can_be_absent_without_making_the_artifact_incomplete(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """MANDATED AND BLOCKING ARE DIFFERENT WORDS, and the distinction has no instance today.

    Every facet is mandated — a facet may be unattested but never absent — and only the
    BLOCKING ones make an artifact non-executable when unsatisfied. All fifteen currently
    declared facets are blocking, so the skip in ``missing_facets`` has never run and the
    distinction exists only in the type. It is exercised here by declaring a non-blocking
    facet, which is the shape the mandate would take the first time an obligation is
    recorded as reportable rather than fatal; without the skip that facet would make every
    artifact in the repository incomplete on the commit that introduced it.
    """
    assert not [
        f for f in metadata.MANDATED_FACETS if not f.blocking
    ], "a non-blocking facet now exists; assert it directly instead of synthesising one"

    reportable = dataclasses.replace(metadata.MANDATED_FACETS[0], blocking=False)
    extended = (reportable, *metadata.MANDATED_FACETS[1:])
    monkeypatch.setattr(metadata, "MANDATED_FACETS", extended)

    stripped = declare("stripped", **{reportable.facet_id: ()})
    assert reportable.facet_id not in stripped.missing_facets()
    assert metadata.require_complete(stripped) is stripped


def test_a_complete_declaration_passes_the_fail_closed_entry_point_unchanged() -> None:
    """``require_complete`` returns the SAME object rather than a copy, so a caller may use
    it as a checkpoint in an expression without the value changing identity underneath them.
    Only its refusal had a test, which left the passing arm — the one every lawful
    declaration takes — unexecuted."""
    complete = declare("complete")
    assert complete.missing_facets() == ()
    assert metadata.require_complete(complete) is complete

    incomplete = declare("incomplete", dependencies=())
    with pytest.raises(MetadataIncomplete) as excinfo:
        metadata.require_complete(incomplete)
    assert "dependencies" in excinfo.value.detail["missing_facets"]
