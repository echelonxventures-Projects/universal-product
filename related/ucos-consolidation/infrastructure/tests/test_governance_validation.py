"""Tests for EC3-B13-U09 Infrastructure Governance validation.

Covers the mission-required checks:
- no-secret-material (UIL-15 / IGOV-06)
- authority-boundary (IGOV-01/04 / AUTH-06)
- governance-evaluative-nonenforcing (WF-10 / UIL-14 / IGOV-01)
- deterministic validation (repeated validation is identical)
"""

from __future__ import annotations

import pytest

from engine.tests import assert_every_check_can_refuse
from infrastructure.governance import GovernanceFacet, GovernanceFacetKind, make_governance_facet
from infrastructure.governance_meta import REALIZATION_UNIT
from infrastructure.governance_traceability import build_traceability
from infrastructure.governance_validation import (
    GovernanceValidationSubject,
    governance_checks,
    validate_construct,
)

_ALL_FACETS = (
    GovernanceFacetKind.CONFORMANCE,
    GovernanceFacetKind.LIFECYCLE,
    GovernanceFacetKind.POLICY,
    GovernanceFacetKind.GAP_REPORT,
    GovernanceFacetKind.CHANGE_RECORD,
)


def _validate(facet: GovernanceFacetKind):
    gf = make_governance_facet(f"t.{facet.value}", facet)
    trace = build_traceability(gf, unit=REALIZATION_UNIT, forward=(gf.construct_id, "EVID"))
    return validate_construct(gf, trace)


@pytest.mark.parametrize("facet", _ALL_FACETS)
def test_facet_validation_accepted(facet: GovernanceFacetKind) -> None:
    result = _validate(facet)
    assert result.accepted
    assert result.report.verdict.value == "pass"
    blocking = [f.check_id for f in result.report.findings if f.is_blocking_failure]
    assert not blocking, f"blocking failures: {blocking}"


def test_required_checks_present() -> None:
    ids = {c.check_id for c in governance_checks()}
    for required in (
        "no-secret-material",
        "authority-boundary",
        "governance-evaluative-nonenforcing",
        "governance-evaluates-objectbound",
        "technology-independence",
        "non-constitutive",
        "traceability-rooted",
    ):
        assert required in ids, f"missing required check: {required}"


def test_eighteen_checks() -> None:
    assert len(governance_checks()) == 18


def test_all_checks_blocking() -> None:
    from engine.validation.contracts import Severity

    for c in governance_checks():
        assert c.severity == Severity.BLOCKING


def test_no_secret_material_check_fails_on_secret() -> None:
    gf = GovernanceFacet(
        type_tag="t.leak",
        facet=GovernanceFacetKind.POLICY,
        evaluates=("ENG-005:ENG-002:api_key=abcd1234",),
    )
    trace = build_traceability(gf, unit=REALIZATION_UNIT, forward=(gf.construct_id, "EVID"))
    result = validate_construct(gf, trace)
    assert not result.accepted
    blocking = {f.check_id for f in result.report.findings if f.is_blocking_failure}
    assert "no-secret-material" in blocking


def test_technology_independence_check_fails_on_technology() -> None:
    gf = GovernanceFacet(
        type_tag="t.tech",
        facet=GovernanceFacetKind.POLICY,
        evaluates=("ENG-005:ENG-002:aws.iam.role",),
    )
    trace = build_traceability(gf, unit=REALIZATION_UNIT, forward=(gf.construct_id, "EVID"))
    result = validate_construct(gf, trace)
    assert not result.accepted
    blocking = {f.check_id for f in result.report.findings if f.is_blocking_failure}
    assert "technology-independence" in blocking


def test_authority_boundary_and_nonenforcing_pass() -> None:
    result = _validate(GovernanceFacetKind.POLICY)
    passed = {f.check_id for f in result.report.findings if f.passed}
    assert "authority-boundary" in passed
    assert "governance-evaluative-nonenforcing" in passed


def test_validation_is_deterministic() -> None:
    a = _validate(GovernanceFacetKind.CONFORMANCE)
    b = _validate(GovernanceFacetKind.CONFORMANCE)
    assert a.report.to_dict() == b.report.to_dict()
    assert a.evidence.to_dict() == b.evidence.to_dict()


def test_every_check_can_refuse_something():
    """Each declared check has a reachable failure arm — see engine/tests/__init__.py."""
    _c = make_governance_facet("t.policy", GovernanceFacetKind.POLICY)
    _t = build_traceability(_c, unit=REALIZATION_UNIT, forward=(_c.construct_id, "EVID"))
    assert_every_check_can_refuse(
        GovernanceValidationSubject.from_construct(_c, _t), governance_checks()
    )
