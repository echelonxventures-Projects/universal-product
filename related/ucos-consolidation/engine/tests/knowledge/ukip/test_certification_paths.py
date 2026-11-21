"""UKIP Part 12 — the three certification verdicts, each shown to be reachable.

WHY THIS MODULE EXISTS. Certification has three outcomes and only one of them had ever
been produced: CERTIFIED. DENIED (a blocking validation failure) and INCOMPLETE (every
law satisfied, a criterion unmet) were unexecuted branches, and so was the INCOMPLETE
per-capability verdict a narrowed criterion set produces. A certifier observed only
granting is not distinguishable from one that grants unconditionally.
"""

from __future__ import annotations

from dataclasses import replace

from engine.knowledge.ukip.certification import (
    CRITERIA,
    CertStatus,
    Criterion,
    KnowledgeIntelligenceCertifier,
    certify_assimilation,
    certify_registry,
)
from engine.knowledge.ukip.constitution import KNOWLEDGE_CAPABILITIES, KnowledgeCapability
from engine.knowledge.ukip.registry import KnowledgeRegistry

from .conftest import make_unit, register


def _registry() -> KnowledgeRegistry:
    return register((make_unit("a", statement="Alpha statement."),))


# -- CERTIFIED ------------------------------------------------------------------------


def test_a_lawful_registry_is_certified_and_every_capability_with_it():
    certificate = certify_registry(_registry())
    assert certificate.status is CertStatus.CERTIFIED
    assert certificate.certified is True
    assert certificate.unsatisfied() == ()
    assert certificate.uncertified_capabilities() == ()
    assert len(certificate.certified_capabilities()) == len(KNOWLEDGE_CAPABILITIES)
    counts = certificate.counts()
    assert counts["criteria"] == len(CRITERIA)
    assert counts["unsatisfied"] == 0
    assert counts["capabilities_certified"] == counts["capabilities_total"]


def test_a_criterion_result_is_addressable_by_id_and_an_unknown_one_is_not_invented():
    certificate = certify_registry(_registry())
    known = CRITERIA[0].criterion_id
    result = certificate.result(known)
    assert result is not None
    assert result.criterion_id == known
    assert certificate.result("not-a-criterion") is None


def test_the_certifier_reports_the_criteria_it_will_evaluate_in_stable_order():
    certifier = KnowledgeIntelligenceCertifier(tuple(reversed(CRITERIA)))
    assert certifier.criterion_ids == tuple(sorted(c.criterion_id for c in CRITERIA))


# -- DENIED ---------------------------------------------------------------------------


def test_a_blocking_validation_failure_denies_certification_outright():
    """DENIED is not INCOMPLETE: a registry that failed a BLOCKING law is refused even
    where individual criteria happen to hold."""
    (record,) = _registry().records()
    broken = KnowledgeRegistry((replace(record, universe=""),))
    certificate = certify_registry(broken)
    assert certificate.status is CertStatus.DENIED
    assert certificate.certified is False
    assert certificate.unsatisfied()
    assert certificate.uncertified_capabilities()


# -- INCOMPLETE -----------------------------------------------------------------------


def test_an_unmet_criterion_over_a_valid_registry_is_incomplete_rather_than_denied():
    unmeetable = Criterion(
        "never-satisfied",
        KnowledgeCapability.REGISTRY,
        "UKIP-LAW-001",
        "A criterion no registry can meet, so the INCOMPLETE verdict is reachable.",
        lambda _subject: False,
    )
    certificate = KnowledgeIntelligenceCertifier((*CRITERIA, unmeetable)).certify(_registry())
    assert certificate.status is CertStatus.INCOMPLETE
    assert certificate.certified is False
    assert [r.criterion_id for r in certificate.unsatisfied()] == ["never-satisfied"]
    assert "registry" in certificate.uncertified_capabilities()


def test_a_capability_no_criterion_binds_is_incomplete_rather_than_certified():
    """A narrowed criterion set leaves capabilities unevaluated; unevaluated is not
    certified, which is the whole difference between a gate and a report."""
    single = next(c for c in CRITERIA if c.capability is KnowledgeCapability.REGISTRY)
    certificate = KnowledgeIntelligenceCertifier((single,)).certify(_registry())
    statuses = certificate.capability_status()
    assert statuses[KnowledgeCapability.REGISTRY.value] == CertStatus.CERTIFIED.value
    unbound = [
        capability.value
        for capability in KNOWLEDGE_CAPABILITIES
        if capability is not KnowledgeCapability.REGISTRY
    ]
    assert all(statuses[name] == CertStatus.INCOMPLETE.value for name in unbound)
    assert set(certificate.uncertified_capabilities()) == set(unbound)


# -- serialisation --------------------------------------------------------------------


def test_a_criterion_serialises_the_law_and_capability_it_binds():
    payload = CRITERIA[0].to_dict()
    assert set(payload) == {"criterion_id", "capability", "law_id", "description"}
    assert payload["criterion_id"] == CRITERIA[0].criterion_id


def test_the_certificate_seals_exactly_the_facts_it_asserts():
    certificate = certify_registry(_registry())
    assert len(certificate.seal()) == 64
    assert certify_registry(_registry()).seal() == certificate.seal()
    moved = replace(certificate, status=CertStatus.DENIED)
    assert moved.seal() != certificate.seal()


def test_the_certificate_serialises_its_verdict_counts_and_capability_status():
    payload = certify_registry(_registry()).to_dict()
    assert payload["certified"] is True
    assert payload["uncertified_capabilities"] == []
    assert len(payload["results"]) == len(CRITERIA)
    assert set(payload["capability_status"]) == {c.value for c in KNOWLEDGE_CAPABILITIES}
    assert payload["seal"] == certify_registry(_registry()).seal()
    assert set(payload["results"][0]) == {
        "criterion_id",
        "capability",
        "law_id",
        "satisfied",
        "description",
    }


def test_certifying_an_assimilation_carries_its_decision_records(seed_report):
    certificate = certify_assimilation(seed_report)
    assert certificate.status is CertStatus.CERTIFIED
    assert certificate.record_count == len(seed_report.registry)
