"""UKIP Part 11 — the refusal half of the fail-closed validation gate.

WHY THIS MODULE EXISTS, STATED AS A MEASUREMENT. Sixteen checks were exercised by a
registry that satisfies all sixteen, so every ``_failed`` return in the suite was
unexecuted: the gate had been shown to pass and had never been shown to refuse. A gate
observed only in agreement with its subject is indistinguishable from one that returns
PASS unconditionally, which is the false green this apparatus exists to prevent.

Each test below drives exactly one check into FAIL and asserts the offenders it names,
because a refusal that cannot say *what* offended is not actionable.

TWO FAILURES ARE FORGED RATHER THAN ARRANGED, and the reason is recorded where it
happens: the registry refuses a duplicate home at admission and the constitution is
authored data, so neither condition is reachable through the public API. A branch nothing
can reach is still a branch nobody has shown can fire, and forging the state is the only
honest way to show it.
"""

from __future__ import annotations

from dataclasses import fields, replace

import pytest

from engine.knowledge.model import KnowledgeKind, Lifecycle, RelationType
from engine.knowledge.ukip.constitution import KnowledgeCapability
from engine.knowledge.ukip.contracts import RelationDeclaration
from engine.knowledge.ukip.registry import KnowledgeRegistry, RegisteredKnowledge
from engine.knowledge.ukip.relationships import Relationship, RelationshipSet
from engine.knowledge.ukip.validation import (
    AcyclicFamiliesCheck,
    CanonicalKnowledgeOnlyCheck,
    ConstitutionCompleteCheck,
    ContentDerivedIdentityCheck,
    GraphResolvedCheck,
    KnowledgeIntelligenceValidator,
    ProjectedBaseCheck,
    ProvenanceCompleteCheck,
    ProvenanceGroundedCheck,
    ProvenanceIntactCheck,
    ProviderAttributionCheck,
    RecordIntegrityCheck,
    RelationshipsNavigableCheck,
    RelationshipsResolvedCheck,
    SingleCanonicalHomeCheck,
    TotalClassificationCheck,
    UniversalDiscoverabilityCheck,
    ValidationSubject,
    default_checks,
    validate_assimilation,
    validate_registry,
)
from engine.knowledge.validation import CheckStatus, Severity, Verdict

from .conftest import make_unit, register


def _subject(*units) -> ValidationSubject:
    return ValidationSubject.of(register(units))


def _sole_record(subject: ValidationSubject) -> RegisteredKnowledge:
    (record,) = subject.registry.records()
    return record


def _subject_over(*records: RegisteredKnowledge) -> ValidationSubject:
    return ValidationSubject.of(KnowledgeRegistry(records))


def _rebuild(record: RegisteredKnowledge, **changes) -> RegisteredKnowledge:
    """A record with fields replaced and its seal deliberately NOT recomputed."""
    return replace(record, **changes)


# -- registry invariants --------------------------------------------------------------


def test_a_registry_that_satisfies_every_law_is_valid():
    report = validate_registry(register((make_unit("a", statement="Alpha statement."),)))
    assert report.verdict is Verdict.VALID
    assert report.accepted is True
    assert report.blocking_failures == ()
    assert report.uncovered_laws() == ()


def test_an_identifier_not_derived_from_content_is_refused():
    record = _sole_record(_subject(make_unit("a", statement="Alpha statement.")))
    subject = _subject_over(_rebuild(record, knowledge_id="UKID-000000000000"))
    finding = ContentDerivedIdentityCheck().evaluate(subject)
    assert finding.status is CheckStatus.FAIL
    assert finding.offenders == ("UKID-000000000000",)


def test_a_record_whose_content_no_longer_matches_its_seal_is_refused():
    record = _sole_record(_subject(make_unit("a", statement="Alpha statement.")))
    tampered = _rebuild(record, title="a title nobody sealed")
    subject = _subject_over(tampered)
    finding = RecordIntegrityCheck().evaluate(subject)
    assert finding.status is CheckStatus.FAIL
    assert finding.offenders == (tampered.knowledge_id,)


@pytest.mark.parametrize("facet", ["universe", "owner", "version"])
def test_an_undecided_classification_facet_is_refused(facet):
    record = _sole_record(_subject(make_unit("a", statement="Alpha statement.")))
    subject = _subject_over(_rebuild(record, **{facet: ""}))
    finding = TotalClassificationCheck().evaluate(subject)
    assert finding.status is CheckStatus.FAIL
    assert finding.offenders == (record.knowledge_id,)


def test_a_record_no_provider_vouches_for_is_refused():
    """Attribution is forged: every admission path attaches the source it came from, so
    an unattributed record cannot be built by submitting one."""

    class _Unattributed(RegisteredKnowledge):
        __slots__ = ()

        @property
        def provider_ids(self) -> tuple[str, ...]:
            return ()

    record = _sole_record(_subject(make_unit("a", statement="Alpha statement.")))
    unattributed = _Unattributed(**{f.name: getattr(record, f.name) for f in fields(record)})
    finding = ProviderAttributionCheck().evaluate(_subject_over(unattributed))
    assert finding.status is CheckStatus.FAIL
    assert finding.offenders == (record.knowledge_id,)


def test_draft_or_review_knowledge_is_reported_without_blocking():
    record = _sole_record(_subject(make_unit("a", statement="Alpha statement.")))
    check = CanonicalKnowledgeOnlyCheck()
    finding = check.evaluate(_subject_over(_rebuild(record, lifecycle=Lifecycle.DRAFT)))
    assert finding.status is CheckStatus.FAIL
    assert check.severity is Severity.ADVISORY
    assert finding.is_blocking_failure is False


def test_identical_knowledge_homed_twice_is_refused():
    """Forged: :meth:`KnowledgeRegistry._install` raises ``DuplicateHomeError`` before a
    second home can exist, so the only way to show the check firing is to hand it a
    registry that reports what the real one refuses to build."""
    subject = _subject(make_unit("a", statement="Alpha statement."))
    record = _sole_record(subject)

    class _TwoHomes:
        def records(self):
            return (record,)

        def duplicate_homes(self):
            return (("UKID-AAAAAAAAAAAA", "UKID-BBBBBBBBBBBB"),)

        def __len__(self):
            return 2

    finding = SingleCanonicalHomeCheck().evaluate(replace(subject, registry=_TwoHomes()))
    assert finding.status is CheckStatus.FAIL
    assert finding.offenders == ("UKID-AAAAAAAAAAAA+UKID-BBBBBBBBBBBB",)


# -- provenance -----------------------------------------------------------------------


def test_an_incomplete_provenance_chain_is_refused():
    record = _sole_record(_subject(make_unit("a", statement="Alpha statement.")))
    truncated = _rebuild(
        record, provenance=replace(record.provenance, steps=record.provenance.steps[:1])
    )
    finding = ProvenanceCompleteCheck().evaluate(_subject_over(truncated))
    assert finding.status is CheckStatus.FAIL
    assert finding.offenders == (record.knowledge_id,)


def test_a_provenance_chain_whose_hash_links_are_broken_is_refused():
    record = _sole_record(_subject(make_unit("a", statement="Alpha statement.")))
    steps = list(record.provenance.steps)
    steps[-1] = replace(steps[-1], previous_sha256="0" * 64)
    broken = _rebuild(record, provenance=replace(record.provenance, steps=tuple(steps)))
    assert broken.provenance.verify() is False
    finding = ProvenanceIntactCheck().evaluate(_subject_over(broken))
    assert finding.status is CheckStatus.FAIL
    assert finding.offenders == (record.knowledge_id,)


def test_a_provenance_chain_citing_no_content_addressed_source_is_refused():
    record = _sole_record(_subject(make_unit("a", statement="Alpha statement.")))
    ungrounded = _rebuild(
        record,
        provenance=replace(
            record.provenance,
            steps=tuple(replace(step, source=None) for step in record.provenance.steps),
        ),
    )
    assert ungrounded.provenance.is_grounded is False
    finding = ProvenanceGroundedCheck().evaluate(_subject_over(ungrounded))
    assert finding.status is CheckStatus.FAIL
    assert finding.offenders == (record.knowledge_id,)


# -- relationships --------------------------------------------------------------------


def test_a_relationship_target_that_resolves_to_nothing_is_refused():
    subject = _subject(
        make_unit(
            "a",
            statement="Alpha statement.",
            relations=(RelationDeclaration(RelationType.DEPENDS_ON, "nowhere"),),
        )
    )
    finding = RelationshipsResolvedCheck().evaluate(subject)
    assert finding.status is CheckStatus.FAIL
    assert finding.offenders == (f"{_sole_record(subject).knowledge_id}-depends-on->nowhere",)


def test_a_cycle_in_an_acyclic_relation_family_is_refused():
    subject = ValidationSubject.of(
        register(
            (
                make_unit(
                    "a",
                    statement="Alpha statement.",
                    relations=(RelationDeclaration(RelationType.DEPENDS_ON, "b"),),
                ),
                make_unit(
                    "b",
                    statement="Beta statement.",
                    relations=(RelationDeclaration(RelationType.DEPENDS_ON, "a"),),
                ),
            )
        )
    )
    finding = AcyclicFamiliesCheck().evaluate(subject)
    assert finding.status is CheckStatus.FAIL
    assert finding.offenders and finding.offenders[0].startswith("dependency:")


def test_a_symmetric_relationship_without_its_mirror_is_not_navigable():
    subject = _subject(
        make_unit("a", statement="Alpha statement."), make_unit("b", statement="Beta statement.")
    )
    left, right = subject.registry.knowledge_ids()
    half = RelationshipSet((Relationship(left, right, RelationType.RELATED_TO),))
    assert len(half.unnavigable()) == 1
    finding = RelationshipsNavigableCheck().evaluate(replace(subject, relationships=half))
    assert finding.status is CheckStatus.FAIL
    assert finding.offenders == (f"{left}-related-to->{right}",)


def test_a_graph_edge_pointing_at_no_record_is_refused():
    subject = _subject(make_unit("a", statement="Alpha statement."))
    identifier = _sole_record(subject).knowledge_id
    broken = replace(
        subject,
        graph=type(subject.graph)(
            subject.registry,
            RelationshipSet((Relationship(identifier, "UKID-ABSENT", RelationType.DEPENDS_ON),)),
        ),
    )
    finding = GraphResolvedCheck().evaluate(broken)
    assert finding.status is CheckStatus.FAIL
    assert finding.offenders == ("UKID-ABSENT",)


# -- discovery ------------------------------------------------------------------------


def test_a_record_that_search_cannot_find_is_refused():
    """A title carrying no searchable term is findable by identifier and by digest but
    not by search, and discoverability is the conjunction of all three."""
    subject = _subject(make_unit("a", title="---", statement="Alpha statement."))
    finding = UniversalDiscoverabilityCheck().evaluate(subject)
    assert finding.status is CheckStatus.FAIL
    assert finding.offenders == (_sole_record(subject).knowledge_id,)


# -- constitution and the delegated suite ---------------------------------------------


def test_a_capability_no_law_governs_is_refused(monkeypatch):
    """Forged: the constitution is authored data in which every capability IS governed,
    so the gap is introduced at the boundary the check reads it through."""
    subject = _subject(make_unit("a", statement="Alpha statement."))
    real = ConstitutionCompleteCheck().evaluate(subject)
    assert real.status is CheckStatus.PASS

    class _Gapped:
        laws = ()

        def ungoverned_capabilities(self):
            return (KnowledgeCapability.REGISTRY,)

    monkeypatch.setattr(
        "engine.knowledge.ukip.validation.knowledge_constitution", lambda: _Gapped()
    )
    finding = ConstitutionCompleteCheck().evaluate(subject)
    assert finding.status is CheckStatus.FAIL
    assert finding.offenders == (KnowledgeCapability.REGISTRY.value,)


def test_a_projected_base_that_fails_the_ukda_suite_is_refused(monkeypatch):
    """The delegation is the point: UKIP does not restate the UKDA rules, so its refusal
    must carry the UKDA check identifiers rather than invent its own."""
    subject = _subject(make_unit("a", statement="Alpha statement."))
    assert ProjectedBaseCheck().evaluate(subject).status is CheckStatus.PASS

    class _Rejected:
        accepted = False
        blocking_failures = (type("F", (), {"check_id": "ukda-decision-records-present"})(),)

    monkeypatch.setattr("engine.knowledge.ukip.validation.validate_base", lambda _base: _Rejected())
    finding = ProjectedBaseCheck().evaluate(subject)
    assert finding.status is CheckStatus.FAIL
    assert finding.offenders == ("ukda-decision-records-present",)


# -- the report -----------------------------------------------------------------------


def test_one_blocking_failure_makes_the_whole_registry_not_valid():
    record = _sole_record(_subject(make_unit("a", statement="Alpha statement.")))
    report = KnowledgeIntelligenceValidator().validate(
        KnowledgeRegistry((_rebuild(record, universe=""),))
    )
    assert report.verdict is Verdict.NOT_VALID
    assert report.accepted is False
    failed = {f.check_id for f in report.blocking_failures}
    # Blanking a sealed facet offends two laws at once, and reporting BOTH is the point:
    # the classification is undecided AND the record no longer verifies its own hash.
    assert failed == {"total-classification", "record-integrity"}
    assert report.counts()["blocking_failed"] == 2
    assert report.counts()["failed"] >= 2


def test_a_finding_is_addressable_by_check_id_and_an_unknown_one_is_not_invented():
    report = validate_registry(register((make_unit("a", statement="Alpha statement."),)))
    assert report.finding("record-integrity") is not None
    assert report.finding("not-a-check") is None


def test_a_narrowed_suite_reports_the_laws_it_leaves_unenforced():
    report = KnowledgeIntelligenceValidator((RecordIntegrityCheck(),)).validate(
        register((make_unit("a", statement="Alpha statement."),))
    )
    assert report.law_coverage == ("UKIP-LAW-011",)
    assert "UKIP-LAW-001" in report.uncovered_laws()
    assert report.counts()["laws_unenforced"] == len(report.uncovered_laws())


def test_the_suite_is_ordered_by_check_id_however_it_is_supplied():
    shuffled = tuple(reversed(default_checks()))
    assert KnowledgeIntelligenceValidator(shuffled).check_ids == tuple(
        sorted(c.check_id for c in default_checks())
    )


def test_a_check_serialises_the_law_and_capability_it_enforces():
    payload = RecordIntegrityCheck().to_dict()
    assert payload == {
        "check_id": "record-integrity",
        "severity": Severity.BLOCKING.value,
        "law_id": "UKIP-LAW-011",
        "capability": KnowledgeCapability.REGISTRY.value,
        "description": RecordIntegrityCheck.description,
    }


def test_the_report_serialises_its_verdict_counts_and_law_coverage():
    payload = validate_registry(register((make_unit("a", statement="Alpha statement."),))).to_dict()
    assert payload["verdict"] == Verdict.VALID.value
    assert payload["accepted"] is True
    assert payload["laws_unenforced"] == []
    assert len(payload["findings"]) == len(default_checks())
    assert payload["counts"]["total"] == len(default_checks())


def test_validating_an_assimilation_uses_the_decisions_it_carried(seed_report):
    report = validate_assimilation(seed_report)
    assert report.accepted is True
    assert report.counts()["failed"] == 0


def test_a_kind_facet_is_never_blank_because_classification_decides_it():
    """The classification facets the check reads are three of six; the other three are
    enum-typed and cannot be blank, which is why the check names only these."""
    record = _sole_record(_subject(make_unit("a", statement="Alpha statement.")))
    assert record.kind is KnowledgeKind.FACT
    assert TotalClassificationCheck().evaluate(_subject_over(record)).status is CheckStatus.PASS
