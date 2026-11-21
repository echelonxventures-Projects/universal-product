"""Tests for EC3-B13-U08 Infrastructure Security validation.

Covers the mission-required checks:
- no-secret-material (ISEC-03 / RR-07)
- authority-boundary (ISEC-04/06 / AUTH-06)
- security-evaluative-nonenforcing (WF-10 / UIL-14)
- deterministic validation (repeated validation is identical)
"""

from __future__ import annotations

import pytest

from engine.tests import assert_every_check_can_refuse
from infrastructure.security import SecurityFacet, SecurityFacetKind, make_security_facet
from infrastructure.security_meta import REALIZATION_UNIT
from infrastructure.security_traceability import build_traceability
from infrastructure.security_validation import (
    SecurityValidationSubject,
    security_checks,
    validate_construct,
)

_ALL_FACETS = (
    SecurityFacetKind.ISOLATION,
    SecurityFacetKind.AUTHENTICATION,
    SecurityFacetKind.AUTHORIZATION,
    SecurityFacetKind.CONFIDENTIALITY,
    SecurityFacetKind.INTEGRITY,
)


def _validate(facet: SecurityFacetKind):
    sf = make_security_facet(f"t.{facet.value}", facet)
    trace = build_traceability(sf, unit=REALIZATION_UNIT, forward=(sf.construct_id, "EVID"))
    return validate_construct(sf, trace)


@pytest.mark.parametrize("facet", _ALL_FACETS)
def test_facet_validation_accepted(facet: SecurityFacetKind) -> None:
    result = _validate(facet)
    assert result.accepted
    assert result.report.verdict.value == "pass"
    blocking = [f.check_id for f in result.report.findings if f.is_blocking_failure]
    assert not blocking, f"blocking failures: {blocking}"


def test_required_checks_present() -> None:
    ids = {c.check_id for c in security_checks()}
    for required in (
        "no-secret-material",
        "authority-boundary",
        "security-evaluative-nonenforcing",
        "security-evaluates-objectbound",
        "technology-independence",
        "non-constitutive",
        "traceability-rooted",
    ):
        assert required in ids, f"missing required check: {required}"


def test_all_checks_blocking() -> None:
    from engine.validation.contracts import Severity

    for c in security_checks():
        assert c.severity == Severity.BLOCKING


def test_no_secret_material_check_fails_on_secret() -> None:
    sf = SecurityFacet(
        type_tag="t.leak",
        facet=SecurityFacetKind.CONFIDENTIALITY,
        evaluates=("ENG-005:ENG-002:api_key=abcd1234",),
    )
    trace = build_traceability(sf, unit=REALIZATION_UNIT, forward=(sf.construct_id, "EVID"))
    result = validate_construct(sf, trace)
    assert not result.accepted
    blocking = {f.check_id for f in result.report.findings if f.is_blocking_failure}
    assert "no-secret-material" in blocking


def test_technology_independence_check_fails_on_technology() -> None:
    sf = SecurityFacet(
        type_tag="t.tech",
        facet=SecurityFacetKind.AUTHENTICATION,
        evaluates=("ENG-005:ENG-002:aws.iam.role",),
    )
    trace = build_traceability(sf, unit=REALIZATION_UNIT, forward=(sf.construct_id, "EVID"))
    result = validate_construct(sf, trace)
    assert not result.accepted
    blocking = {f.check_id for f in result.report.findings if f.is_blocking_failure}
    assert "technology-independence" in blocking


def test_authority_boundary_and_nonenforcing_pass() -> None:
    result = _validate(SecurityFacetKind.AUTHORIZATION)
    passed = {f.check_id for f in result.report.findings if f.passed}
    assert "authority-boundary" in passed
    assert "security-evaluative-nonenforcing" in passed


def test_validation_is_deterministic() -> None:
    a = _validate(SecurityFacetKind.INTEGRITY)
    b = _validate(SecurityFacetKind.INTEGRITY)
    assert a.report.to_dict() == b.report.to_dict()
    assert a.evidence.to_dict() == b.evidence.to_dict()


def test_every_check_can_refuse_something():
    """Each declared check has a reachable failure arm — see engine/tests/__init__.py."""
    _c = make_security_facet("t.isolation", SecurityFacetKind.ISOLATION)
    _t = build_traceability(_c, unit=REALIZATION_UNIT, forward=(_c.construct_id, "EVID"))
    assert_every_check_can_refuse(
        SecurityValidationSubject.from_construct(_c, _t), security_checks()
    )
