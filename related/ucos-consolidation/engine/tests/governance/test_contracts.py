"""EPIC-VAL-003 — Repository Governance Pipeline contract tests."""

from __future__ import annotations

import pytest

from engine.governance.contracts import (
    GOVERNANCE_STAGES,
    GovernanceInput,
    GovernanceStatus,
    GovernanceUnit,
    RepositoryDecision,
    StageOutcome,
)
from engine.governance.errors import GovernanceInputError
from engine.runtime.disclosure import build_disclosure

# --- GovernanceUnit ----------------------------------------------------------


def test_governance_unit_requires_unit_id(valid_subject):
    with pytest.raises(GovernanceInputError):
        GovernanceUnit(unit_id="", subject=valid_subject)


def test_governance_unit_requires_subject():
    with pytest.raises(GovernanceInputError) as exc:
        GovernanceUnit(unit_id="UNIT-X", subject=None)
    assert exc.value.context["unit_id"] == "UNIT-X"


def test_governance_unit_to_dict(valid_subject):
    unit = GovernanceUnit(unit_id="UNIT-A", subject=valid_subject, owner="o")
    d = unit.to_dict()
    assert d["unit_id"] == "UNIT-A"
    assert d["owner"] == "o"
    assert d["certification_class"] == "engineering-readiness"
    assert d["subject"]["target_id"] == valid_subject.target_id


# --- GovernanceInput ---------------------------------------------------------


def test_governance_input_requires_identity(governance_units):
    with pytest.raises(GovernanceInputError):
        GovernanceInput(repository_id="", epic_id="E", units=governance_units)


def test_governance_input_requires_units():
    with pytest.raises(GovernanceInputError):
        GovernanceInput(repository_id="R", epic_id="E", units=())


def test_governance_input_rejects_non_mapping_facts(governance_units):
    with pytest.raises(GovernanceInputError):
        GovernanceInput(
            repository_id="R",
            epic_id="E",
            units=governance_units,
            repository_facts=["not", "a", "mapping"],  # type: ignore[arg-type]
        )


def test_governance_input_rejects_duplicate_units(valid_subject):
    dup = (
        GovernanceUnit(unit_id="UNIT-A", subject=valid_subject),
        GovernanceUnit(unit_id="UNIT-A", subject=valid_subject),
    )
    with pytest.raises(GovernanceInputError) as exc:
        GovernanceInput(repository_id="R", epic_id="E", units=dup)
    assert exc.value.context["unit_id"] == "UNIT-A"


def test_governance_input_orders_units(valid_subject):
    units = (
        GovernanceUnit(unit_id="UNIT-B", subject=valid_subject),
        GovernanceUnit(unit_id="UNIT-A", subject=valid_subject),
    )
    gi = GovernanceInput(repository_id="R", epic_id="E", units=units)
    assert tuple(u.unit_id for u in gi.ordered_units()) == ("UNIT-A", "UNIT-B")
    assert gi.to_dict()["units"][0]["unit_id"] == "UNIT-A"


# --- StageOutcome ------------------------------------------------------------


def test_stage_outcome_passes_when_all_pass():
    outcome = StageOutcome.of("validation", total=3, failures=())
    assert outcome.passed is True
    assert outcome.passed_count == 3
    assert outcome.to_dict()["failed"] == 0


def test_stage_outcome_fails_on_failure():
    outcome = StageOutcome.of("validation", total=3, failures=("UNIT-A",))
    assert outcome.passed is False
    assert outcome.passed_count == 2
    assert outcome.to_dict()["failures"] == ["UNIT-A"]


def test_stage_outcome_empty_never_passes():
    outcome = StageOutcome.of("validation", total=0, failures=())
    assert outcome.passed is False


# --- RepositoryDecision ------------------------------------------------------


def _stages(v_fail=(), c_fail=(), a_fail=()):
    return (
        StageOutcome.of("validation", total=2, failures=v_fail),
        StageOutcome.of("certification", total=2, failures=c_fail),
        StageOutcome.of("acceptance", total=20, failures=a_fail),
    )


def test_decision_governed_when_all_stages_pass():
    v, c, a = _stages()
    decision = RepositoryDecision.create(
        repository_id="R",
        epic_id="E",
        validation=v,
        certification=c,
        acceptance=a,
        disclosure=build_disclosure(),
    )
    assert decision.status is GovernanceStatus.GOVERNED
    assert decision.governed is True
    assert decision.blocking_reasons == ()
    assert decision.verify_integrity() is True
    assert decision.to_dict()["governed"] is True


def test_decision_not_governed_on_any_stage_failure():
    v, c, a = _stages(c_fail=("UNIT-B",))
    decision = RepositoryDecision.create(
        repository_id="R",
        epic_id="E",
        validation=v,
        certification=c,
        acceptance=a,
        disclosure=build_disclosure(),
    )
    assert decision.status is GovernanceStatus.NOT_GOVERNED
    assert decision.governed is False
    assert "certification:UNIT-B" in decision.blocking_reasons


def test_decision_is_deterministic():
    v, c, a = _stages()
    args = dict(
        repository_id="R",
        epic_id="E",
        validation=v,
        certification=c,
        acceptance=a,
        disclosure=build_disclosure(),
    )
    assert (
        RepositoryDecision.create(**args).decision_sha256
        == RepositoryDecision.create(**args).decision_sha256
    )


def test_decision_detects_mutation():
    import dataclasses

    v, c, a = _stages()
    decision = RepositoryDecision.create(
        repository_id="R",
        epic_id="E",
        validation=v,
        certification=c,
        acceptance=a,
        disclosure=build_disclosure(),
    )
    tampered = dataclasses.replace(decision, repository_id="OTHER")
    assert tampered.verify_integrity() is False


def test_governance_stages_constant():
    assert GOVERNANCE_STAGES == ("validation", "certification", "acceptance")
