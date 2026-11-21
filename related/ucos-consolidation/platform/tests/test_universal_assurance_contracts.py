"""UCOS-EPIC-014 — tests for the Universal Assurance contract vocabulary (Terminal T7).

The contracts module is the package's dependency-independent floor: it imports only the
error taxonomy and the two reused engine vocabularies, and every other assurance module
is built on top of it. What it promises is therefore what the whole capability inherits,
and these tests prove the promises rather than the spelling.

**Immutability.** Subjects, stage records, reports and dashboards are frozen value
objects. A verdict that could be edited after it was reached is not a verdict.

**Determinism (IMP-007 §5).** Identity is a pure function of declared content. The same
subject hashes identically across independent construction; the same stage outcomes hash
identically regardless of the order the stages completed in; and volatile summary detail
is deliberately excluded from identity, so attaching diagnostics cannot silently rewrite
a report's hash.

**Fail-closed assimilation.** ``AssuranceSubject.from_mapping`` is the boundary where
untrusted facts enter the capability. Every malformed shape raises
:class:`AssuranceSubjectError` — the contract never repairs a subject, and never accepts
one it cannot fully normalize.

**Fail-closed aggregation.** A blocking failure anywhere forces FAIL / ``NOT-ASSURED`` /
``CLOSED``; advisory failures never do. This is the asymmetry the whole assurance gate
rests on, so it is exercised from both directions.

**Projection without translation.** A subject projects directly onto the reused
``ValidationTarget`` and ``IntelligenceTarget``, proving no second target vocabulary was
introduced here.

Nothing in these tests hardcodes a domain, dimension or subject shape as *the* one:
domains and dimensions are drawn from the reused enums, so admitting a new one to those
vocabularies does not falsify a single assertion here.
"""

from __future__ import annotations

import dataclasses
from platform.foundation.contracts import content_hash
from platform.universal_assurance.contracts import (
    ASSURANCE_AUTHORITY,
    ASSURANCE_DASHBOARD_FORMAT,
    ASSURANCE_REPORT_FORMAT,
    DETERMINATION_ASSURED,
    DETERMINATION_NOT_ASSURED,
    UNIVERSAL_ASSURANCE_CONTRACT_VERSION,
    AssuranceDashboard,
    AssuranceReport,
    AssuranceStage,
    AssuranceSubject,
    GateStatus,
    ObligationKind,
    Outcome,
    Severity,
    StageRecord,
    Verdict,
)
from platform.universal_assurance.errors import AssuranceSubjectError
from platform.universal_validation.contracts import ValidationDomain, ValidationTarget
from platform.universal_validation.errors import ValidationTargetError
from platform.validation_intelligence.contracts import IntelligenceDimension, IntelligenceTarget
from typing import Any

import pytest

# --- discovered vocabulary (never hardcoded) -------------------------------------

#: Two domains chosen from the reused enum in *reverse* canonical order, so an
#: ordering assertion fails if the contract stops sorting.
_DOMAINS = sorted(ValidationDomain, key=lambda d: d.order)
_FIRST_DOMAIN, _LAST_DOMAIN = _DOMAINS[0], _DOMAINS[-1]

_DIMENSIONS = sorted(IntelligenceDimension, key=lambda d: d.order)
_FIRST_DIMENSION, _LAST_DIMENSION = _DIMENSIONS[0], _DIMENSIONS[-1]


def _subject_mapping(**overrides: Any) -> dict[str, Any]:
    """A well-formed subject mapping built from the *reused* vocabularies."""
    base: dict[str, Any] = {
        "subject_id": "SUBJ-001",
        "version": "1.0.0",
        "blueprint_id": "BP-001",
        "validation_facts": {_FIRST_DOMAIN.value: {"declared": True}},
        "intelligence_facts": {_FIRST_DIMENSION.value: {"consistent": True}},
        "repository_truth": {"closed": True},
        "observations": {"coverage": 0.94},
    }
    base.update(overrides)
    return base


def _record(
    stage: AssuranceStage,
    *,
    blocking: tuple[str, ...] = (),
    advisory: tuple[str, ...] = (),
    total: int = 2,
    satisfied: int = 2,
) -> StageRecord:
    return StageRecord.create(
        stage=stage,
        obligations_total=total,
        obligations_satisfied=satisfied,
        blocking_failures=blocking,
        advisory_failures=advisory,
        artifact_sha256=content_hash({"stage": stage.value}),
    )


# --- module constants ------------------------------------------------------------


def test_contract_surface_declares_a_semantic_version() -> None:
    """AR-03/PL-05: the contract surface is versioned, so consumers can bind to it."""
    assert UNIVERSAL_ASSURANCE_CONTRACT_VERSION == "1.0.0"
    assert ASSURANCE_REPORT_FORMAT == "ucos-universal-assurance-report/1.0.0"
    assert ASSURANCE_DASHBOARD_FORMAT == "ucos-universal-assurance-dashboard/1.0.0"


def test_the_capability_disclaims_constitutional_authority() -> None:
    """DE-05 / IP-01: a run records engineering readiness and confers nothing else."""
    assert ASSURANCE_AUTHORITY == "ENGINEERING-EXECUTION-ONLY"


def test_the_two_determinations_are_distinct() -> None:
    """A run is assured or it is not; there is no third, softer determination."""
    assert DETERMINATION_ASSURED == "ASSURED"
    assert DETERMINATION_NOT_ASSURED == "NOT-ASSURED"
    assert DETERMINATION_ASSURED != DETERMINATION_NOT_ASSURED


# --- AssuranceStage --------------------------------------------------------------


def test_the_ten_owned_stages_are_declared_in_mission_order() -> None:
    """The stage enum *is* the capability inventory; its order is the run order."""
    assert [stage.value for stage in AssuranceStage] == [
        "validation-planning",
        "validation-generation",
        "validation-execution",
        "evidence-collection",
        "certification-planning",
        "certification-execution",
        "certification-evidence",
        "certification-registry",
        "validation-intelligence",
        "certification-intelligence",
    ]


def test_stage_order_is_the_declaration_index() -> None:
    """Deterministic ordering: ``order`` is total, gap-free, and declaration-derived."""
    orders = [stage.order for stage in AssuranceStage]
    assert orders == list(range(len(AssuranceStage)))


@pytest.mark.parametrize("stage", list(AssuranceStage), ids=lambda s: s.value)
def test_stage_parse_round_trips_every_declared_stage(stage: AssuranceStage) -> None:
    """Parsing a stage's own wire value yields the identical member."""
    assert AssuranceStage.parse(stage.value) is stage
    assert AssuranceStage.parse(stage) is stage


def test_stage_parse_fails_closed_on_an_unknown_stage() -> None:
    """An unknown stage is an authoring fault and names the supported set (auditable)."""
    with pytest.raises(AssuranceSubjectError) as caught:
        AssuranceStage.parse("certification-teatime")
    assert caught.value.context["stage"] == "certification-teatime"
    assert caught.value.context["supported"] == [s.value for s in AssuranceStage]


def test_stage_is_a_string_enum_so_it_serializes_without_translation() -> None:
    """Stages travel as their wire value in any JSON projection."""
    assert AssuranceStage.EVIDENCE_COLLECTION == "evidence-collection"


# --- ObligationKind / Severity / Outcome / Verdict / GateStatus ------------------


def test_obligation_kinds_bind_to_the_four_reused_executors() -> None:
    """Each kind names a *reused* mechanism; a fifth kind would mean a new engine."""
    assert [kind.value for kind in ObligationKind] == [
        "validation-rule",
        "intelligence-dimension",
        "certification-criterion",
        "certification-frame",
    ]
    assert [kind.order for kind in ObligationKind] == list(range(len(ObligationKind)))


def test_severity_separates_blocking_from_advisory() -> None:
    """The gate turns on exactly this distinction."""
    assert [s.value for s in Severity] == ["blocking", "advisory"]


def test_outcome_and_verdict_are_fail_closed_binaries() -> None:
    """No 'unknown', 'skipped' or 'partial': an undischarged obligation is a FAIL."""
    assert [o.value for o in Outcome] == ["pass", "fail"]
    assert [v.value for v in Verdict] == ["pass", "fail"]


def test_gate_status_is_open_or_closed() -> None:
    assert [g.value for g in GateStatus] == ["OPEN", "CLOSED"]


# --- AssuranceSubject: assimilation ----------------------------------------------


def test_a_well_formed_mapping_assimilates_into_a_normalized_subject() -> None:
    """The happy path normalizes every block without altering declared content."""
    subject = AssuranceSubject.from_mapping(_subject_mapping())
    assert subject.subject_id == "SUBJ-001"
    assert subject.version == "1.0.0"
    assert subject.blueprint_id == "BP-001"
    assert subject.validation_facts == {_FIRST_DOMAIN.value: {"declared": True}}
    assert subject.intelligence_facts == {_FIRST_DIMENSION.value: {"consistent": True}}
    assert subject.repository_truth == {"closed": True}
    assert subject.observations == {"coverage": 0.94}


def test_a_subject_is_immutable() -> None:
    """A subject under assurance cannot be edited while it is being assured."""
    subject = AssuranceSubject.from_mapping(_subject_mapping())
    with pytest.raises(dataclasses.FrozenInstanceError):
        subject.subject_id = "SUBJ-002"  # type: ignore[misc]


def test_optional_blocks_default_to_empty_rather_than_none() -> None:
    """Absent facts are an empty declaration, never a null every consumer must guard."""
    subject = AssuranceSubject.from_mapping({"subject_id": "S", "version": "1"})
    assert subject.validation_facts == {}
    assert subject.intelligence_facts == {}
    assert subject.repository_truth == {}
    assert subject.observations == {}
    assert subject.declared_domains() == ()
    assert subject.declared_dimensions() == ()


def test_blueprint_id_defaults_to_the_subject_id() -> None:
    """A subject that declares no blueprint is its own blueprint — never unidentified."""
    subject = AssuranceSubject.from_mapping(
        {"subject_id": "SUBJ-009", "version": "2.0.0", "blueprint_id": None}
    )
    assert subject.blueprint_id == "SUBJ-009"


def test_assimilated_facts_are_copied_not_aliased() -> None:
    """Mutating the source mapping afterwards cannot retroactively change the subject."""
    raw = _subject_mapping()
    subject = AssuranceSubject.from_mapping(raw)
    raw["validation_facts"][_FIRST_DOMAIN.value]["declared"] = False
    raw["repository_truth"]["closed"] = False
    assert subject.validation_facts[_FIRST_DOMAIN.value] == {"declared": True}
    assert subject.repository_truth == {"closed": True}


@pytest.mark.parametrize(
    ("raw", "reason"),
    [
        pytest.param("not-a-mapping", "a subject must be a mapping", id="not-a-mapping"),
        pytest.param({"version": "1"}, "subject_id is absent", id="missing-subject-id"),
        pytest.param({"subject_id": "", "version": "1"}, "subject_id is empty", id="empty-id"),
        pytest.param(
            {"subject_id": 17, "version": "1"}, "subject_id is not a string", id="non-str-id"
        ),
        pytest.param({"subject_id": "S"}, "version is absent", id="missing-version"),
        pytest.param({"subject_id": "S", "version": ""}, "version is empty", id="empty-version"),
        pytest.param(
            {"subject_id": "S", "version": 1}, "version is not a string", id="non-str-version"
        ),
        pytest.param(
            {"subject_id": "S", "version": "1", "blueprint_id": 42},
            "blueprint_id is not a string",
            id="non-str-blueprint",
        ),
        pytest.param(
            {"subject_id": "S", "version": "1", "validation_facts": "nope"},
            "validation_facts is not a mapping",
            id="facts-not-mapping",
        ),
        pytest.param(
            {"subject_id": "S", "version": "1", "validation_facts": {"": {}}},
            "a fact key is empty",
            id="empty-fact-key",
        ),
        pytest.param(
            {"subject_id": "S", "version": "1", "validation_facts": {7: {}}},
            "a fact key is not a string",
            id="non-str-fact-key",
        ),
        pytest.param(
            {"subject_id": "S", "version": "1", "validation_facts": {"architecture": "nope"}},
            "a fact entry is not a mapping",
            id="fact-entry-not-mapping",
        ),
        pytest.param(
            {"subject_id": "S", "version": "1", "intelligence_facts": {"not-a-dimension": {}}},
            "an unknown intelligence dimension",
            id="unknown-dimension",
        ),
        pytest.param(
            {"subject_id": "S", "version": "1", "repository_truth": ["closed"]},
            "repository_truth is not a mapping",
            id="truth-not-mapping",
        ),
        pytest.param(
            {"subject_id": "S", "version": "1", "observations": "nope"},
            "observations is not a mapping",
            id="observations-not-mapping",
        ),
        pytest.param(
            {"subject_id": "S", "version": "1", "observations": {"": 1.0}},
            "an observation key is empty",
            id="empty-observation-key",
        ),
        pytest.param(
            {"subject_id": "S", "version": "1", "observations": {3: 1.0}},
            "an observation key is not a string",
            id="non-str-observation-key",
        ),
        pytest.param(
            {"subject_id": "S", "version": "1", "observations": {"coverage": True}},
            "a boolean is not a measurement",
            id="bool-observation",
        ),
        pytest.param(
            {"subject_id": "S", "version": "1", "observations": {"coverage": "high"}},
            "an observation value is not numeric",
            id="non-numeric-observation",
        ),
    ],
)
def test_malformed_subjects_fail_closed(raw: Any, reason: str) -> None:
    """The assimilation boundary refuses every shape it cannot fully normalize."""
    with pytest.raises(AssuranceSubjectError):
        AssuranceSubject.from_mapping(raw)


def test_an_unknown_validation_domain_is_refused_by_the_reused_vocabulary() -> None:
    """No second domain vocabulary: the reused enum adjudicates, and it fails closed."""
    with pytest.raises(ValidationTargetError):
        AssuranceSubject.from_mapping(
            {"subject_id": "S", "version": "1", "validation_facts": {"not-a-domain": {}}}
        )


def test_integer_observations_are_normalized_to_float() -> None:
    """One numeric type crosses the boundary, so metric comparison is type-stable."""
    subject = AssuranceSubject.from_mapping(
        {"subject_id": "S", "version": "1", "observations": {"count": 7}}
    )
    assert subject.observations == {"count": 7.0}
    assert isinstance(subject.observations["count"], float)


# --- AssuranceSubject: projection and identity -----------------------------------


def test_declared_domains_are_returned_in_canonical_order() -> None:
    """Declaration order in the source mapping never leaks into the projection."""
    subject = AssuranceSubject.from_mapping(
        _subject_mapping(
            validation_facts={_LAST_DOMAIN.value: {"a": 1}, _FIRST_DOMAIN.value: {"b": 2}}
        )
    )
    assert subject.declared_domains() == (_FIRST_DOMAIN, _LAST_DOMAIN)


def test_declared_dimensions_are_returned_in_canonical_order() -> None:
    subject = AssuranceSubject.from_mapping(
        _subject_mapping(
            intelligence_facts={_LAST_DIMENSION.value: {"a": 1}, _FIRST_DIMENSION.value: {"b": 2}}
        )
    )
    assert subject.declared_dimensions() == (_FIRST_DIMENSION, _LAST_DIMENSION)


def test_a_subject_projects_onto_the_reused_validation_target() -> None:
    """Reuse First: the subject *is* a validation target, with no translation layer."""
    subject = AssuranceSubject.from_mapping(_subject_mapping())
    target = subject.build_validation_target()
    assert isinstance(target, ValidationTarget)
    assert target.target_id == "SUBJ-001"
    assert target.facts == subject.validation_facts


def test_a_subject_projects_onto_the_reused_intelligence_target() -> None:
    subject = AssuranceSubject.from_mapping(_subject_mapping())
    target = subject.build_intelligence_target()
    assert isinstance(target, IntelligenceTarget)
    assert target.target_id == "SUBJ-001"
    assert target.facts == subject.intelligence_facts


def test_subject_to_dict_sorts_every_keyed_block() -> None:
    """Canonical key order is what makes the digest independent of authoring order."""
    subject = AssuranceSubject.from_mapping(
        _subject_mapping(
            validation_facts={_LAST_DOMAIN.value: {"a": 1}, _FIRST_DOMAIN.value: {"b": 2}},
            intelligence_facts={_LAST_DIMENSION.value: {"a": 1}, _FIRST_DIMENSION.value: {"b": 2}},
            observations={"z": 1.0, "a": 2.0},
        )
    )
    payload = subject.to_dict()
    assert list(payload["validation_facts"]) == [_FIRST_DOMAIN.value, _LAST_DOMAIN.value]
    assert list(payload["intelligence_facts"]) == [_FIRST_DIMENSION.value, _LAST_DIMENSION.value]
    assert list(payload["observations"]) == ["a", "z"]


def test_subject_digest_is_independent_of_authoring_order() -> None:
    """IMP-007 §5: identity follows declared content, not the order it was written in."""
    forward = AssuranceSubject.from_mapping(_subject_mapping(observations={"a": 1.0, "z": 2.0}))
    reversed_ = AssuranceSubject.from_mapping(_subject_mapping(observations={"z": 2.0, "a": 1.0}))
    assert forward.digest() == reversed_.digest()


def test_subject_digest_changes_when_declared_content_changes() -> None:
    """A digest that ignored a fact would let an unassured change pass as assured."""
    baseline = AssuranceSubject.from_mapping(_subject_mapping())
    for override in (
        {"subject_id": "SUBJ-002"},
        {"version": "2.0.0"},
        {"blueprint_id": "BP-002"},
        {"repository_truth": {"closed": False}},
        {"observations": {"coverage": 0.93}},
        {"validation_facts": {_FIRST_DOMAIN.value: {"declared": False}}},
        {"intelligence_facts": {_FIRST_DIMENSION.value: {"consistent": False}}},
    ):
        altered = AssuranceSubject.from_mapping(_subject_mapping(**override))
        assert altered.digest() != baseline.digest(), override


def test_subject_digest_is_stable_across_independent_construction() -> None:
    """No wall-clock, RNG or ambient state leaks into a subject's identity."""
    first = AssuranceSubject.from_mapping(_subject_mapping())
    second = AssuranceSubject.from_mapping(_subject_mapping())
    assert first.digest() == second.digest()
    assert first.digest() == content_hash(first.to_dict())


# --- StageRecord -----------------------------------------------------------------


def test_a_stage_with_no_blocking_failure_passes() -> None:
    record = _record(AssuranceStage.VALIDATION_PLANNING, advisory=("style-drift",))
    assert record.verdict is Verdict.PASS
    assert record.passed is True
    assert record.advisory_failures == ("style-drift",)


def test_a_single_blocking_failure_fails_the_stage() -> None:
    """Fail-closed: one undischarged blocking obligation is sufficient."""
    record = _record(AssuranceStage.VALIDATION_PLANNING, blocking=("unbound-rule",))
    assert record.verdict is Verdict.FAIL
    assert record.passed is False


def test_stage_failures_are_deduplicated_and_sorted() -> None:
    """Identity is content-derived, so the same failure set always records identically."""
    record = _record(
        AssuranceStage.VALIDATION_EXECUTION,
        blocking=("z-rule", "a-rule", "z-rule"),
        advisory=("y-hint", "b-hint", "b-hint"),
    )
    assert record.blocking_failures == ("a-rule", "z-rule")
    assert record.advisory_failures == ("b-hint", "y-hint")


def test_stage_failure_order_does_not_affect_identity() -> None:
    forward = _record(AssuranceStage.EVIDENCE_COLLECTION, blocking=("a", "b"))
    backward = _record(AssuranceStage.EVIDENCE_COLLECTION, blocking=("b", "a"))
    assert content_hash(forward.core()) == content_hash(backward.core())


def test_stage_coverage_is_the_satisfied_ratio() -> None:
    record = _record(AssuranceStage.CERTIFICATION_PLANNING, total=4, satisfied=3)
    assert record.coverage == 0.75


def test_a_stage_with_no_obligations_is_fully_covered() -> None:
    """Vacuous truth, stated explicitly: zero of zero obligations is 1.0, not a ZeroDivision."""
    assert _record(AssuranceStage.CERTIFICATION_PLANNING, total=0, satisfied=0).coverage == 1.0
    assert _record(AssuranceStage.CERTIFICATION_PLANNING, total=-1, satisfied=0).coverage == 1.0


def test_stage_summary_defaults_to_empty_and_is_copied_when_supplied() -> None:
    """Both summary branches: absent becomes ``{}``; supplied is snapshotted."""
    assert _record(AssuranceStage.CERTIFICATION_REGISTRY).summary == {}
    supplied = {"detail": "registered"}
    record = StageRecord.create(
        stage=AssuranceStage.CERTIFICATION_REGISTRY,
        obligations_total=1,
        obligations_satisfied=1,
        artifact_sha256="abc",
        summary=supplied,
    )
    supplied["detail"] = "mutated"
    assert record.summary == {"detail": "registered"}


def test_stage_core_excludes_volatile_summary_detail() -> None:
    """Diagnostics must never be able to rewrite a stage's identity."""
    plain = _record(AssuranceStage.VALIDATION_INTELLIGENCE)
    annotated = StageRecord.create(
        stage=AssuranceStage.VALIDATION_INTELLIGENCE,
        obligations_total=2,
        obligations_satisfied=2,
        artifact_sha256=content_hash({"stage": AssuranceStage.VALIDATION_INTELLIGENCE.value}),
        summary={"notes": "anything at all"},
    )
    assert plain.core() == annotated.core()
    assert "summary" not in plain.core()
    assert annotated.to_dict()["summary"] == {"notes": "anything at all"}


def test_stage_to_dict_carries_the_core_plus_derived_detail() -> None:
    record = _record(AssuranceStage.CERTIFICATION_EXECUTION, total=4, satisfied=1)
    payload = record.to_dict()
    assert payload["stage"] == "certification-execution"
    assert payload["verdict"] == "pass"
    assert payload["coverage"] == 0.25
    assert payload["obligations_total"] == 4
    assert payload["obligations_satisfied"] == 1


def test_a_stage_record_is_immutable() -> None:
    record = _record(AssuranceStage.VALIDATION_PLANNING)
    with pytest.raises(dataclasses.FrozenInstanceError):
        record.verdict = Verdict.FAIL  # type: ignore[misc]


# --- AssuranceReport -------------------------------------------------------------


def _passing_report() -> AssuranceReport:
    return AssuranceReport.create(
        subject_id="SUBJ-001",
        subject_digest="subject-digest",
        policy_digest="policy-digest",
        stage_records=[_record(stage) for stage in AssuranceStage],
    )


def test_a_report_over_passing_stages_is_assured_and_opens_the_gate() -> None:
    report = _passing_report()
    assert report.verdict is Verdict.PASS
    assert report.passed is True
    assert report.determination == DETERMINATION_ASSURED
    assert report.gate is GateStatus.OPEN


def test_one_blocking_stage_failure_closes_the_whole_gate() -> None:
    """The asymmetry the assurance gate rests on, exercised from the failing side."""
    records = [_record(stage) for stage in AssuranceStage]
    records[4] = _record(AssuranceStage.CERTIFICATION_PLANNING, blocking=("criterion-unbound",))
    report = AssuranceReport.create(
        subject_id="SUBJ-001",
        subject_digest="subject-digest",
        policy_digest="policy-digest",
        stage_records=records,
    )
    assert report.verdict is Verdict.FAIL
    assert report.passed is False
    assert report.determination == DETERMINATION_NOT_ASSURED
    assert report.gate is GateStatus.CLOSED


def test_advisory_failures_alone_never_close_the_gate() -> None:
    """Advisory findings are reported honestly and are still not blocking."""
    report = AssuranceReport.create(
        subject_id="SUBJ-001",
        subject_digest="d",
        policy_digest="p",
        stage_records=[_record(stage, advisory=("hint",)) for stage in AssuranceStage],
    )
    assert report.gate is GateStatus.OPEN
    assert report.determination == DETERMINATION_ASSURED
    assert len(report.advisory_failures()) == len(AssuranceStage)


def test_stage_records_are_reordered_into_canonical_stage_order() -> None:
    """Completion order must not change the report; only the declared order counts."""
    shuffled = list(reversed([_record(stage) for stage in AssuranceStage]))
    report = AssuranceReport.create(
        subject_id="SUBJ-001",
        subject_digest="d",
        policy_digest="p",
        stage_records=shuffled,
    )
    assert report.stages_run() == tuple(stage.value for stage in AssuranceStage)


def test_report_identity_is_independent_of_completion_order() -> None:
    """IMP-007 §5: identical outcomes hash identically however the run interleaved."""
    records = [_record(stage) for stage in AssuranceStage]
    forward = AssuranceReport.create(
        subject_id="S", subject_digest="d", policy_digest="p", stage_records=records
    )
    backward = AssuranceReport.create(
        subject_id="S", subject_digest="d", policy_digest="p", stage_records=list(reversed(records))
    )
    assert forward.report_sha256 == backward.report_sha256


def test_report_identity_binds_the_subject_and_the_policy() -> None:
    """A report is a claim about *this* subject under *this* policy, and hashes as one."""
    baseline = _passing_report()
    other_subject = AssuranceReport.create(
        subject_id="SUBJ-001",
        subject_digest="other-subject-digest",
        policy_digest="policy-digest",
        stage_records=[_record(stage) for stage in AssuranceStage],
    )
    other_policy = AssuranceReport.create(
        subject_id="SUBJ-001",
        subject_digest="subject-digest",
        policy_digest="other-policy-digest",
        stage_records=[_record(stage) for stage in AssuranceStage],
    )
    assert other_subject.report_sha256 != baseline.report_sha256
    assert other_policy.report_sha256 != baseline.report_sha256


def test_report_identity_ignores_volatile_summary_detail() -> None:
    """Attaching diagnostics after the fact cannot silently rewrite a determination."""
    plain = _passing_report()
    annotated = AssuranceReport.create(
        subject_id="SUBJ-001",
        subject_digest="subject-digest",
        policy_digest="policy-digest",
        stage_records=[
            StageRecord.create(
                stage=stage,
                obligations_total=2,
                obligations_satisfied=2,
                artifact_sha256=content_hash({"stage": stage.value}),
                summary={"notes": f"diagnostics for {stage.value}"},
            )
            for stage in AssuranceStage
        ],
    )
    assert annotated.report_sha256 == plain.report_sha256


def test_report_identity_is_reproducible_across_independent_construction() -> None:
    assert _passing_report().report_sha256 == _passing_report().report_sha256


def test_a_report_asserts_engineering_authority_and_carries_the_disclosure() -> None:
    """DE-05 / IP-01: the provisional-state disclosure travels with every report."""
    report = _passing_report()
    assert report.authority == ASSURANCE_AUTHORITY
    assert report.disclosure
    assert report.disclosure["asserts_constitutional_finality"] is False


def test_stage_verdicts_project_every_stage_that_ran() -> None:
    report = _passing_report()
    assert report.stage_verdicts() == {stage.value: "pass" for stage in AssuranceStage}


def test_record_for_returns_the_matching_stage() -> None:
    report = _passing_report()
    record = report.record_for(AssuranceStage.CERTIFICATION_REGISTRY)
    assert record is not None
    assert record.stage is AssuranceStage.CERTIFICATION_REGISTRY


def test_record_for_returns_none_when_a_stage_did_not_run() -> None:
    """A partial run reports the absence honestly instead of fabricating a record."""
    report = AssuranceReport.create(
        subject_id="S",
        subject_digest="d",
        policy_digest="p",
        stage_records=[_record(AssuranceStage.VALIDATION_PLANNING)],
    )
    assert report.record_for(AssuranceStage.CERTIFICATION_INTELLIGENCE) is None
    assert report.record_for(AssuranceStage.VALIDATION_PLANNING) is not None


def test_failures_are_reported_qualified_by_their_stage() -> None:
    """An unqualified failure id is unattributable; the report qualifies every one."""
    report = AssuranceReport.create(
        subject_id="S",
        subject_digest="d",
        policy_digest="p",
        stage_records=[
            _record(AssuranceStage.VALIDATION_EXECUTION, blocking=("rule-a",)),
            _record(AssuranceStage.VALIDATION_INTELLIGENCE, advisory=("hint-b",)),
        ],
    )
    assert report.blocking_failures() == ("validation-execution:rule-a",)
    assert report.advisory_failures() == ("validation-intelligence:hint-b",)


def test_report_counts_aggregate_stages_and_obligations() -> None:
    report = AssuranceReport.create(
        subject_id="S",
        subject_digest="d",
        policy_digest="p",
        stage_records=[
            _record(AssuranceStage.VALIDATION_PLANNING, total=3, satisfied=3),
            _record(AssuranceStage.VALIDATION_EXECUTION, total=5, satisfied=2, blocking=("r",)),
            _record(AssuranceStage.VALIDATION_INTELLIGENCE, total=1, satisfied=1, advisory=("h",)),
        ],
    )
    assert report.counts() == {
        "stages": 3,
        "stages_passed": 2,
        "stages_failed": 1,
        "obligations_total": 9,
        "obligations_satisfied": 6,
        "blocking_failed": 1,
        "advisory_failed": 1,
    }


def test_report_to_dict_is_a_complete_self_describing_projection() -> None:
    """The wire form names its own format, so a consumer never has to guess."""
    report = _passing_report()
    payload = report.to_dict()
    assert payload["report_format"] == ASSURANCE_REPORT_FORMAT
    assert payload["subject_id"] == "SUBJ-001"
    assert payload["verdict"] == "pass"
    assert payload["passed"] is True
    assert payload["determination"] == DETERMINATION_ASSURED
    assert payload["gate"] == "OPEN"
    assert payload["subject_digest"] == "subject-digest"
    assert payload["policy_digest"] == "policy-digest"
    assert payload["authority"] == ASSURANCE_AUTHORITY
    assert payload["report_sha256"] == report.report_sha256
    assert len(payload["stages"]) == len(AssuranceStage)


def test_a_report_is_immutable() -> None:
    report = _passing_report()
    with pytest.raises(dataclasses.FrozenInstanceError):
        report.determination = DETERMINATION_ASSURED  # type: ignore[misc]


# --- AssuranceDashboard ----------------------------------------------------------


def test_the_dashboard_projects_the_report_without_re_deciding_it() -> None:
    """The dashboard is a view: it reports the verdict, it never computes a new one."""
    report = _passing_report()
    dashboard = report.dashboard()
    assert isinstance(dashboard, AssuranceDashboard)
    assert dashboard.subject_id == report.subject_id
    assert dashboard.verdict is report.verdict
    assert dashboard.determination == report.determination
    assert dashboard.gate is report.gate
    assert dashboard.stage_verdicts == report.stage_verdicts()


def test_the_dashboard_carries_the_reports_aggregate_counts() -> None:
    records = [_record(stage) for stage in AssuranceStage]
    records[0] = _record(AssuranceStage.VALIDATION_PLANNING, total=4, satisfied=1, blocking=("r",))
    report = AssuranceReport.create(
        subject_id="S", subject_digest="d", policy_digest="p", stage_records=records
    )
    dashboard = report.dashboard()
    counts = report.counts()
    assert dashboard.stages_total == counts["stages"]
    assert dashboard.stages_passed == counts["stages_passed"]
    assert dashboard.obligations_total == counts["obligations_total"]
    assert dashboard.obligations_satisfied == counts["obligations_satisfied"]
    assert dashboard.blocking_failures == report.blocking_failures()
    assert dashboard.advisory_failures == report.advisory_failures()
    assert dashboard.gate is GateStatus.CLOSED


def test_from_report_and_the_dashboard_helper_agree() -> None:
    report = _passing_report()
    assert AssuranceDashboard.from_report(report) == report.dashboard()


def test_dashboard_identity_is_deterministic_and_content_derived() -> None:
    first = _passing_report().dashboard()
    second = _passing_report().dashboard()
    assert first.dashboard_sha256 == second.dashboard_sha256

    failing = AssuranceReport.create(
        subject_id="SUBJ-001",
        subject_digest="subject-digest",
        policy_digest="policy-digest",
        stage_records=[_record(stage, blocking=("r",)) for stage in AssuranceStage],
    ).dashboard()
    assert failing.dashboard_sha256 != first.dashboard_sha256


def test_dashboard_to_dict_is_a_complete_self_describing_projection() -> None:
    dashboard = _passing_report().dashboard()
    payload = dashboard.to_dict()
    assert payload["dashboard_format"] == ASSURANCE_DASHBOARD_FORMAT
    assert payload["subject_id"] == "SUBJ-001"
    assert payload["verdict"] == "pass"
    assert payload["determination"] == DETERMINATION_ASSURED
    assert payload["gate"] == "OPEN"
    assert payload["stages_total"] == len(AssuranceStage)
    assert payload["stages_passed"] == len(AssuranceStage)
    assert payload["blocking_failures"] == []
    assert payload["advisory_failures"] == []
    assert payload["dashboard_sha256"] == dashboard.dashboard_sha256


def test_a_dashboard_is_immutable() -> None:
    dashboard = _passing_report().dashboard()
    with pytest.raises(dataclasses.FrozenInstanceError):
        dashboard.stages_passed = 0  # type: ignore[misc]
