"""UCOS-CTRL-000001 — Governance (Wave 2) and Certification (Wave 3).

The two engines share a shape — a declared rule set evaluated over a normalised
fact bag — so they share a suite. What is being pinned in both cases is that the
verdict is *earned*: a subject missing a required fact is denied, a subject
nobody adjudicated is neither governed nor certified, and a failure is always
attributable to the declared rule that produced it.
"""

from __future__ import annotations

from platform.tests.control_plane_helpers import FIXTURE_ARTIFACTS, build_substrate
from platform.universal_control_plane.certification import (
    CONTROL_PLANE_BLUEPRINT,
    CertificationEngine,
    CertificationSubject,
    certification_subjects,
)
from platform.universal_control_plane.errors import (
    CertificationStateError,
    GovernanceStateError,
    ObjectNotFoundError,
    StateTransitionError,
)
from platform.universal_control_plane.governance import (
    EVENT_GOVERNANCE_RESOLVED,
    EVENT_GOVERNANCE_TRANSITIONED,
    EVENT_GOVERNANCE_VIOLATED,
    VERDICT_AUTHORIZED,
    VERDICT_BLOCKED,
    GovernanceEngine,
    GovernanceSubject,
    governance_subjects,
)
from platform.universal_control_plane.ontology import (
    CERTIFICATION_CERTIFIED,
    CERTIFICATION_NOT_CERTIFIED,
    CERTIFICATION_UNCERTIFIED,
    GOVERNANCE_GOVERNED,
    GOVERNANCE_NOT_GOVERNED,
    GOVERNANCE_UNGOVERNED,
    LIFECYCLE_ACTIVE,
    LIFECYCLE_COMPLETE,
    ArtifactRecord,
)
from platform.universal_control_plane.trace import (
    DeterminationEngine,
    EvidenceEngine,
    HistoryEngine,
)
from platform.universal_control_plane.truth import RepositoryTruthEngine

import pytest


@pytest.fixture(scope="module")
def artifacts(tmp_path_factory):
    root = tmp_path_factory.mktemp("gov-substrate")
    repository_root, data_dir = build_substrate(root)
    engine = RepositoryTruthEngine.discover(data_dir=data_dir, repository_root=repository_root)
    return engine.artifacts()


def _compliant(subject_id: str = "S-1", **overrides) -> GovernanceSubject:
    """A subject that satisfies every rule the shipped manifest declares."""
    defaults = {
        "subject_id": subject_id,
        "kind": "Object",
        "owner": "OWNER-1",
        "registered": True,
        "version": "1.0.0",
        "canonical_home": True,
        "evidence_ids": ("EV-1",),
        "lifecycle_state": LIFECYCLE_ACTIVE,
    }
    return GovernanceSubject(**{**defaults, **overrides})


# ---------------------------------------------------------------------------
# Governance
# ---------------------------------------------------------------------------


class TestGovernanceResolution:
    def test_a_compliant_subject_is_governed(self):
        record = GovernanceEngine().resolve(_compliant())
        assert record.status == GOVERNANCE_GOVERNED
        assert record.governed is True
        assert record.violation_ids == ()
        assert len(record.satisfied_rules) == len(GovernanceEngine().rules)

    @pytest.mark.parametrize(
        ("override", "rule_id"),
        [
            ({"owner": ""}, "GOV-OWNED"),
            ({"registered": False}, "GOV-REGISTERED"),
            ({"version": ""}, "GOV-VERSIONED"),
            ({"canonical_home": False}, "GOV-CANONICAL-HOME"),
        ],
    )
    def test_a_missing_blocking_fact_denies_governance(self, override, rule_id):
        engine = GovernanceEngine()
        record = engine.resolve(_compliant(**override))
        assert record.status == GOVERNANCE_NOT_GOVERNED
        assert rule_id in record.attributes["blocking"]
        assert rule_id in record.rationale

    def test_an_advisory_failure_alone_does_not_deny_governance(self):
        engine = GovernanceEngine()
        record = engine.resolve(_compliant(evidence_ids=()))
        assert record.status == GOVERNANCE_GOVERNED
        assert "GOV-EVIDENCED" in {v.rule_id for v in engine.violations(record.subject_id)}
        assert "advisory rules failed" in record.rationale

    def test_every_violation_is_attributable_to_its_declared_rule(self):
        engine = GovernanceEngine()
        engine.resolve(_compliant(owner="", canonical_home=False))
        assert {v.rule_id for v in engine.violations("S-1")} == {
            "GOV-OWNED",
            "GOV-CANONICAL-HOME",
        }
        for violation in engine.violations("S-1"):
            assert violation.blocking is True
            assert violation.message
            assert violation.attributes["requires"]

    def test_an_empty_subject_id_is_refused(self):
        with pytest.raises(GovernanceStateError, match="non-empty subject_id"):
            GovernanceEngine().resolve(_compliant(subject_id="  "))

    def test_an_unresolved_subject_is_ungoverned_rather_than_absent(self):
        engine = GovernanceEngine()
        assert engine.status_of("never-seen") == GOVERNANCE_UNGOVERNED
        with pytest.raises(ObjectNotFoundError, match="no governance state resolved"):
            engine.state_of("never-seen")

    def test_resolution_order_is_independent_of_input_order(self):
        subjects = [_compliant("B"), _compliant("A"), _compliant("C")]
        assert [r.subject_id for r in GovernanceEngine().resolve_all(subjects)] == ["A", "B", "C"]

    def test_a_declared_rule_can_be_looked_up_and_an_undeclared_one_cannot(self):
        engine = GovernanceEngine()
        assert engine.rule("GOV-OWNED").requires == "owner"
        with pytest.raises(ObjectNotFoundError, match="rule not declared"):
            engine.rule("GOV-INVENTED")

    def test_an_unknown_fact_resolves_against_the_open_fact_bag(self):
        """Extending governance is a manifest edit: a rule naming a fact this
        module has never heard of still resolves, from the subject's own bag."""
        subject = _compliant(facts={"custom_fact": True})
        assert subject.fact("custom_fact") is True
        assert subject.fact("absent_fact") is None


class TestGovernanceFromArtifacts:
    def test_artifacts_project_into_subjects_deterministically(self, artifacts):
        subjects = governance_subjects(artifacts)
        assert [s.subject_id for s in subjects] == sorted(
            a["universal_id"] for a in FIXTURE_ARTIFACTS
        )
        assert all(s.kind == "Artifact" for s in subjects)

    def test_a_non_owning_truth_class_denies_governance(self, artifacts):
        engine = GovernanceEngine()
        engine.resolve_all(governance_subjects(artifacts))
        # 99-FREEZE is historical and 00-MASTER is operational memory: neither
        # may hold ownership, so neither artifact can be governed.
        assert engine.status_of("UCOS-CERTIF-000001") == GOVERNANCE_NOT_GOVERNED
        assert engine.status_of("UCOS-EES-000001") == GOVERNANCE_NOT_GOVERNED
        assert engine.status_of("UCOS-GOV-000001") == GOVERNANCE_GOVERNED

    def test_an_unowned_artifact_fails_the_ownership_rule(self, artifacts):
        engine = GovernanceEngine()
        engine.resolve_all(governance_subjects(artifacts))
        assert "GOV-OWNED" in {v.rule_id for v in engine.violations("UCOS-FINALD-000001")}

    def test_an_artifacts_status_becomes_its_governance_lifecycle(self, artifacts):
        engine = GovernanceEngine()
        engine.resolve_all(governance_subjects(artifacts))
        assert engine.state_of("UCOS-CERTIF-000001").lifecycle_state == "CERTIFIED"

    def test_a_status_free_artifact_falls_back_to_the_draft_lifecycle(self):
        record = ArtifactRecord(
            artifact_id="A", name="a", category="", status="", version="1", owner="o", locator=""
        )
        assert GovernanceSubject.from_artifact(record).lifecycle_state == "DRAFT"

    def test_governed_and_not_governed_partition_the_population(self, artifacts):
        engine = GovernanceEngine()
        engine.resolve_all(governance_subjects(artifacts))
        assert len(engine.governed()) + len(engine.not_governed()) == engine.count()
        assert engine.count() == len(artifacts)


class TestGovernanceTraceability:
    def test_resolution_lands_in_the_wired_traceability_engines(self):
        determinations, evidence, history = (
            DeterminationEngine(),
            EvidenceEngine(),
            HistoryEngine(),
        )
        engine = GovernanceEngine(
            determination_engine=determinations,
            evidence_engine=evidence,
            history_engine=history,
        )
        engine.resolve(_compliant())
        assert determinations.count() == 1
        assert evidence.count() == 1
        assert history.count() == 1

    def test_a_governed_subject_records_an_authorized_determination(self):
        engine = GovernanceEngine()
        engine.resolve(_compliant())
        assert engine.determinations("S-1")[0].verdict == VERDICT_AUTHORIZED

    def test_a_denied_subject_records_a_blocked_determination(self):
        engine = GovernanceEngine()
        engine.resolve(_compliant(owner=""))
        assert engine.determinations("S-1")[0].verdict == VERDICT_BLOCKED

    def test_evidence_digest_covers_the_subject_and_its_violations(self):
        engine = GovernanceEngine()
        engine.resolve(_compliant("A"))
        engine.resolve(_compliant("B", owner=""))
        digests = {e.payload_digest for e in engine.evidence()}
        assert len(digests) == 2

    def test_history_records_both_the_violation_and_the_resolution(self):
        engine = GovernanceEngine()
        engine.resolve(_compliant(owner=""))
        events = [e.event for e in engine.history("S-1")]
        assert EVENT_GOVERNANCE_VIOLATED in events
        assert EVENT_GOVERNANCE_RESOLVED in events

    def test_history_and_evidence_can_be_read_unfiltered(self):
        engine = GovernanceEngine()
        engine.resolve(_compliant("A"))
        engine.resolve(_compliant("B"))
        assert len(engine.history()) == 2
        assert len(engine.evidence()) == 2
        assert len(engine.determinations()) == 2
        assert [s.subject_id for s in engine.subjects()] == ["A", "B"]

    def test_a_re_resolution_does_not_break_on_the_traceability_engines(self):
        """Re-resolving a subject is legitimate; the append-only engines refuse
        the duplicate, and governance must treat that as their business."""
        engine = GovernanceEngine(
            determination_engine=DeterminationEngine(), evidence_engine=EvidenceEngine()
        )
        engine.resolve(_compliant())
        engine.resolve(_compliant())
        assert engine.count() == 1

    def test_blocking_violations_are_separable_from_advisory_ones(self):
        engine = GovernanceEngine()
        engine.resolve(_compliant("A", owner="", evidence_ids=()))
        assert {v.rule_id for v in engine.blocking_violations()} == {"GOV-OWNED"}
        assert len(engine.violations()) == 2


class TestGovernanceLifecycle:
    def test_a_permitted_event_advances_the_governance_lifecycle(self):
        engine = GovernanceEngine()
        engine.resolve(_compliant())
        advanced = engine.advance("S-1", "COMPLETE", tick=3)
        assert advanced.lifecycle_state == LIFECYCLE_COMPLETE
        assert advanced.status == GOVERNANCE_GOVERNED
        assert advanced.tick == 3
        assert engine.state_of("S-1").lifecycle_state == LIFECYCLE_COMPLETE

    def test_advancing_appends_a_transition_to_history(self):
        engine = GovernanceEngine()
        engine.resolve(_compliant())
        engine.advance("S-1", "PAUSE")
        assert EVENT_GOVERNANCE_TRANSITIONED in {e.event for e in engine.history("S-1")}

    def test_an_unregistered_transition_is_refused(self):
        engine = GovernanceEngine()
        engine.resolve(_compliant())
        with pytest.raises(StateTransitionError):
            engine.advance("S-1", "TELEPORT")

    def test_advancing_an_unresolved_subject_is_an_absence(self):
        with pytest.raises(ObjectNotFoundError):
            GovernanceEngine().advance("never-seen", "COMPLETE")


class TestGovernanceDecision:
    def test_the_roll_up_reuses_the_canonical_repository_decision(self):
        engine = GovernanceEngine()
        engine.resolve_all([_compliant("A"), _compliant("B")])
        decision = engine.decision(
            certification_failures=(),
            certification_total=2,
            acceptance_failures=(),
            acceptance_total=2,
        )
        assert decision.status.value == "governed"
        assert decision.decision_sha256
        assert decision.verify_integrity() is True

    def test_a_denied_object_denies_the_repository(self):
        engine = GovernanceEngine()
        engine.resolve_all([_compliant("A"), _compliant("B", owner="")])
        decision = engine.decision(certification_total=2, acceptance_total=2)
        assert decision.status.value == "not-governed"
        assert "validation:B" in decision.blocking_reasons

    def test_an_empty_stage_never_passes_vacuously(self):
        """Fail-closed: supplying no certification evidence must not be read as
        certification having succeeded."""
        engine = GovernanceEngine()
        engine.resolve(_compliant())
        decision = engine.decision(certification_total=0, acceptance_total=0)
        assert decision.status.value == "not-governed"

    def test_the_projection_reports_rules_counts_and_violations(self):
        engine = GovernanceEngine()
        engine.resolve(_compliant(owner=""))
        projection = engine.to_dict()
        assert projection["engine"] == "GovernanceEngine"
        assert projection["counts"]["not_governed"] == 1
        assert projection["counts"]["blocking_violations"] == 1
        assert len(projection["rules"]) == len(engine.rules)
        assert projection["violations"][0]["rule_id"] == "GOV-OWNED"

    def test_a_subject_projects_every_fact_it_carries(self):
        assert _compliant().to_dict()["owner"] == "OWNER-1"


# ---------------------------------------------------------------------------
# Certification
# ---------------------------------------------------------------------------


def _governed(engine: GovernanceEngine, subject_id: str = "S-1", **overrides):
    return engine.resolve(_compliant(subject_id, **overrides))


class TestCertification:
    def test_a_governed_subject_with_every_criterion_is_certified(self):
        governance = GovernanceEngine()
        record = _governed(governance)
        state = CertificationEngine().assess(
            CertificationSubject.from_governance(record, version="1.0.0", lineage=("root",))
        )
        assert state.status == CERTIFICATION_CERTIFIED
        assert state.certified is True
        assert state.eligible is True
        assert state.blocking_failures == ()

    def test_an_ungoverned_subject_is_ineligible_not_merely_uncertified(self):
        governance = GovernanceEngine()
        record = _governed(governance, owner="")
        state = CertificationEngine().assess(
            CertificationSubject.from_governance(record, version="1.0.0")
        )
        assert state.eligible is False
        assert state.status == CERTIFICATION_NOT_CERTIFIED
        assert state.rationale == "ineligible: the subject is not governed"

    def test_a_governed_subject_missing_a_blocking_criterion_is_not_certified(self):
        subject = CertificationSubject(
            subject_id="S", governed=True, version="", evidence_ids=("E",)
        )
        state = CertificationEngine().assess(subject)
        assert state.status == CERTIFICATION_NOT_CERTIFIED
        assert "CERT-VERSION-PINNED" in state.blocking_failures
        assert "blocking criteria failed" in state.rationale

    def test_an_advisory_criterion_failing_alone_still_certifies(self):
        subject = CertificationSubject(
            subject_id="S", governed=True, version="1.0.0", evidence_ids=("E",), lineage=()
        )
        state = CertificationEngine().assess(subject)
        assert state.certified is True
        assert "CERT-LINEAGE-PRESENT" in {c.criterion_id for c in state.criteria if not c.passed}

    def test_an_empty_subject_id_is_refused(self):
        with pytest.raises(CertificationStateError, match="non-empty subject_id"):
            CertificationEngine().assess(CertificationSubject(subject_id="  "))

    def test_an_unassessed_subject_is_uncertified_rather_than_absent(self):
        engine = CertificationEngine()
        assert engine.status_of("never-seen") == CERTIFICATION_UNCERTIFIED
        assert engine.lineage_of("never-seen") == ()
        with pytest.raises(ObjectNotFoundError, match="no certification state assessed"):
            engine.state_of("never-seen")

    def test_a_declared_criterion_can_be_looked_up_and_an_invented_one_cannot(self):
        engine = CertificationEngine()
        assert engine.criterion("CERT-GOVERNED").requires == "governed"
        with pytest.raises(ObjectNotFoundError, match="criterion not declared"):
            engine.criterion("CERT-INVENTED")

    def test_an_unknown_fact_resolves_against_the_open_fact_bag(self):
        subject = CertificationSubject(subject_id="S", facts={"custom": 1})
        assert subject.fact("custom") == 1
        assert subject.fact("absent") is None

    def test_critical_violations_travel_from_governance_rather_than_being_recounted(self):
        governance = GovernanceEngine()
        record = _governed(governance, owner="", canonical_home=False)
        subject = CertificationSubject.from_governance(record)
        assert subject.critical_violations == 2
        assert subject.fact("no_critical_violation") is False


_FULL_SUBJECT = CertificationSubject(
    subject_id="S", governed=True, version="1.0.0", evidence_ids=("E",)
)


class TestCertificationHistoryAndLineage:
    def test_reassessment_appends_rather_than_overwrites(self):
        engine = CertificationEngine()
        subject = _FULL_SUBJECT
        first = engine.assess(subject)
        second = engine.assess(subject)
        assert len(engine.history_of("S")) == 2
        assert engine.state_of("S") is second
        assert first.identity in second.lineage

    def test_lineage_accumulates_across_assessments(self):
        engine = CertificationEngine()
        subject = _FULL_SUBJECT
        engine.assess(subject)
        engine.assess(subject)
        engine.assess(subject)
        assert len(engine.lineage_of("S")) == 2
        assert engine.state_of("S").attributes["revision"] == 3

    def test_each_assessment_records_its_own_evidence(self):
        engine = CertificationEngine(
            evidence_engine=EvidenceEngine(), history_engine=HistoryEngine()
        )
        subject = _FULL_SUBJECT
        engine.assess(subject)
        engine.assess(subject)
        assert len(engine.evidence("S")) == 2
        assert len(engine.evidence()) == 2
        assert len(engine.log()) == 2

    def test_evidence_recording_survives_a_refusing_evidence_engine(self):
        engine = CertificationEngine(evidence_engine=EvidenceEngine())
        subject = _FULL_SUBJECT
        engine.assess(subject)
        engine._history["S"].pop()  # force the next evidence id to collide
        engine.assess(subject)
        assert engine.count() == 1


class TestCertificationRecord:
    def test_every_assessment_issues_a_canonical_certification_record(self):
        engine = CertificationEngine()
        engine.assess(
            CertificationSubject(
                subject_id="S", governed=True, version="2.0.0", evidence_ids=("E",)
            )
        )
        record = engine.record_for("S")
        assert record.target_id == "S"
        assert record.blueprint_id == CONTROL_PLANE_BLUEPRINT
        assert record.version == "2.0.0"
        assert record.status.value == "certified"
        assert record.verify_integrity() is True

    def test_a_denied_assessment_issues_a_not_certified_record(self):
        engine = CertificationEngine()
        engine.assess(CertificationSubject(subject_id="S", governed=False))
        assert engine.record_for("S").status.value == "not-certified"

    def test_a_version_free_subject_still_yields_a_versioned_record(self):
        engine = CertificationEngine()
        engine.assess(CertificationSubject(subject_id="S", governed=True))
        assert engine.record_for("S").version == "0.0.0"

    def test_an_unassessed_subject_has_no_record(self):
        with pytest.raises(ObjectNotFoundError, match="no certification record issued"):
            CertificationEngine().record_for("S")

    def test_criterion_severities_map_onto_the_canonical_vocabulary(self):
        engine = CertificationEngine()
        engine.assess(_FULL_SUBJECT)
        severities = {f.severity.value for f in engine.record_for("S").criteria}
        assert severities == {"blocking", "advisory"}


class TestCertificationPopulation:
    def test_governance_records_project_into_certification_subjects(self, artifacts):
        governance = GovernanceEngine()
        records = governance.resolve_all(governance_subjects(artifacts))
        versions = {a.artifact_id: a.version for a in artifacts}
        subjects = certification_subjects(records, versions=versions)
        assert [s.subject_id for s in subjects] == sorted(r.subject_id for r in records)
        assert subjects[0].version == versions[subjects[0].subject_id]

    def test_projection_without_versions_leaves_them_empty(self, artifacts):
        governance = GovernanceEngine()
        records = governance.resolve_all(governance_subjects(artifacts))
        assert all(s.version == "" for s in certification_subjects(records))

    def test_certified_and_not_certified_partition_the_population(self, artifacts):
        governance = GovernanceEngine()
        records = governance.resolve_all(governance_subjects(artifacts))
        engine = CertificationEngine()
        engine.assess_all(
            certification_subjects(
                records,
                versions={a.artifact_id: a.version for a in artifacts},
            )
        )
        assert len(engine.certified()) + len(engine.not_certified()) == engine.count()
        assert set(engine.failures()) == {s.subject_id for s in engine.not_certified()}
        assert len(engine.ineligible()) == len(governance.not_governed())

    def test_the_projection_reports_criteria_and_counts(self):
        engine = CertificationEngine()
        engine.assess(_FULL_SUBJECT)
        projection = engine.to_dict()
        assert projection["engine"] == "CertificationEngine"
        assert projection["counts"]["certified"] == 1
        assert len(projection["criteria"]) == len(engine.criteria)
        assert projection["states"][0]["subject_id"] == "S"

    def test_a_subject_projects_every_fact_it_carries(self):
        subject = CertificationSubject(subject_id="S", governed=True, lineage=("a",))
        assert subject.to_dict()["lineage"] == ["a"]


class TestQueryEdges:
    def test_evidence_and_history_are_filterable_by_subject(self):
        engine = GovernanceEngine()
        engine.resolve(_compliant("A"))
        engine.resolve(_compliant("B"))
        assert [e.subject_id for e in engine.evidence("A")] == ["A"]
        assert [e.subject_id for e in engine.history("B")] == ["B"]
        assert [d.subject_id for d in engine.determinations("A")] == ["A"]

    def test_a_recorded_linkage_is_retrievable(self):
        from platform.universal_control_plane.linkage import LinkageEngine
        from platform.universal_control_plane.manifest import default_manifest

        engine = LinkageEngine()
        links = {d: f"id-{d}" for d in default_manifest().linkage_dimensions}
        engine.link("S", links)
        assert engine.record_of("S").subject_id == "S"


def test_a_blank_member_of_a_string_sequence_is_dropped_by_the_cleaner() -> None:
    """_str_tuple skips "" and keeps the rest — the cleaning arm every list field runs.

    A reference list that carried whitespace would otherwise be inherited whole and fail
    somewhere far from where it was written.
    """
    from platform.universal_control_plane.manifest import _str_tuple

    assert _str_tuple(["a", "  ", "b", ""], at="test") == ("a", "b")
    assert _str_tuple([], at="test") == ()
