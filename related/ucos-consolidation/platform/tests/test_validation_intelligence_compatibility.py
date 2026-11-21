"""UCOS-EPIC-013 — Compatibility Engine tests (Terminal T5).

The engine that decides whether a candidate may replace a baseline. Its governing rule
is that **absence of evidence is never evidence of compatibility**: every absent or
malformed input must produce a *breaking* finding, so each malformed-input test below is
a fail-closed regression guard, not merely a branch exercise.
"""

from __future__ import annotations

from platform.validation_intelligence.compatibility import (
    CompatibilityEngine,
    SemVer,
    build_compatibility_report,
)
from platform.validation_intelligence.contracts import (
    DimensionReport,
    FindingStatus,
    IntelligenceDimension,
    Severity,
    ValidationIntelligenceReport,
)
from platform.validation_intelligence.errors import CompatibilityError
from typing import Any

import pytest


@pytest.fixture
def engine() -> CompatibilityEngine:
    return CompatibilityEngine()


def _ids(findings) -> list[str]:
    return [f.check_id for f in findings]


def _only(findings):
    assert len(findings) == 1, _ids(findings)
    return findings[0]


def _by_id(findings, check_id: str):
    matches = [f for f in findings if f.check_id == check_id]
    assert matches, f"{check_id} not in {_ids(findings)}"
    return matches[0]


def _contract(name: str, version: str, required: list[str] | None = None) -> dict[str, Any]:
    entry: dict[str, Any] = {"name": name, "version": version}
    if required is not None:
        entry["required_fields"] = required
    return entry


# --- SemVer ----------------------------------------------------------------------
def test_semver_parses_a_well_formed_version():
    assert SemVer.parse("1.2.3") == SemVer(1, 2, 3)


def test_semver_str_round_trips():
    assert str(SemVer.parse("10.20.30")) == "10.20.30"


def test_semver_tolerates_surrounding_whitespace():
    assert SemVer.parse("  1.2.3  ") == SemVer(1, 2, 3)


@pytest.mark.parametrize("value", ["1.2", "1.2.3.4", "v1.2.3", "1.2.x", "", "1.2.3-rc1"])
def test_try_parse_returns_none_for_a_malformed_version(value):
    assert SemVer.try_parse(value) is None


@pytest.mark.parametrize("value", [None, 123, 1.2, ["1.2.3"], {"v": "1.2.3"}])
def test_try_parse_returns_none_for_a_non_string(value):
    assert SemVer.try_parse(value) is None


def test_parse_raises_on_a_malformed_version():
    with pytest.raises(CompatibilityError) as exc:
        SemVer.parse("not-a-version")
    assert exc.value.context["value"] == "not-a-version"


def test_semver_orders_by_major_then_minor_then_patch():
    assert SemVer.parse("1.0.0") < SemVer.parse("1.0.1")
    assert SemVer.parse("1.0.1") < SemVer.parse("1.1.0")
    assert SemVer.parse("1.1.0") < SemVer.parse("2.0.0")


# --- contract compatibility ------------------------------------------------------
@pytest.mark.parametrize("baseline,candidate", [(None, []), ([], None), ("x", []), ([], {"a": 1})])
def test_absent_or_malformed_contract_evidence_is_breaking(engine, baseline, candidate):
    finding = _only(engine.compare_contracts(baseline, candidate))
    assert finding.check_id == "contract_compatibility.evidence"
    assert finding.is_blocking_failure


def test_a_contract_declaration_without_a_name_is_breaking(engine):
    finding = _only(engine.compare_contracts([{"version": "1.0.0"}], []))
    assert finding.check_id == "contract_compatibility.evidence"
    assert finding.is_blocking_failure


def test_a_non_mapping_contract_entry_is_breaking(engine):
    finding = _only(engine.compare_contracts(["nope"], []))
    assert finding.is_blocking_failure


def test_empty_contract_sets_yield_no_findings(engine):
    assert engine.compare_contracts([], []) == ()


def test_removing_a_contract_is_breaking(engine):
    finding = _only(engine.compare_contracts([_contract("c1", "1.0.0")], []))
    assert finding.check_id == "contract_compatibility.c1"
    assert finding.is_blocking_failure
    assert finding.details["contract"] == "c1"


def test_adding_a_contract_is_backward_compatible(engine):
    finding = _only(engine.compare_contracts([], [_contract("c2", "1.0.0")]))
    assert finding.check_id == "contract_compatibility.c2"
    assert finding.status is FindingStatus.PASS


def test_a_minor_bump_is_backward_compatible(engine):
    finding = _only(
        engine.compare_contracts([_contract("c1", "1.0.0")], [_contract("c1", "1.1.0")])
    )
    assert finding.passed


@pytest.mark.parametrize("baseline,candidate", [("bad", "1.0.0"), ("1.0.0", None), (None, None)])
def test_an_absent_or_malformed_contract_version_is_breaking(engine, baseline, candidate):
    base = {"name": "c1", "version": baseline}
    cand = {"name": "c1", "version": candidate}
    finding = _only(engine.compare_contracts([base], [cand]))
    assert finding.is_blocking_failure


def test_a_version_regression_is_breaking(engine):
    finding = _only(
        engine.compare_contracts([_contract("c1", "1.2.0")], [_contract("c1", "1.1.0")])
    )
    assert finding.is_blocking_failure
    assert finding.details["baseline"] == "1.2.0"
    assert finding.details["candidate"] == "1.1.0"


def test_removing_a_required_field_without_a_major_bump_is_breaking(engine):
    finding = _only(
        engine.compare_contracts(
            [_contract("c1", "1.0.0", ["a", "b"])], [_contract("c1", "1.1.0", ["a"])]
        )
    )
    assert finding.is_blocking_failure
    assert finding.details["removed_fields"] == ["b"]


def test_adding_a_required_field_without_a_major_bump_is_breaking(engine):
    """A newly-required field breaks existing producers."""
    finding = _only(
        engine.compare_contracts(
            [_contract("c1", "1.0.0", ["a"])], [_contract("c1", "1.1.0", ["a", "b"])]
        )
    )
    assert finding.is_blocking_failure
    assert finding.details["added_required"] == ["b"]


def test_a_major_bump_licenses_removing_a_required_field(engine):
    finding = _only(
        engine.compare_contracts(
            [_contract("c1", "1.0.0", ["a", "b"])], [_contract("c1", "2.0.0", ["a"])]
        )
    )
    assert finding.passed


def test_a_major_bump_licenses_adding_a_required_field(engine):
    finding = _only(
        engine.compare_contracts(
            [_contract("c1", "1.0.0", ["a"])], [_contract("c1", "2.0.0", ["a", "b"])]
        )
    )
    assert finding.passed


def test_malformed_required_fields_are_treated_as_an_empty_promise(engine):
    """A non-sequence required_fields must not crash the comparison."""
    base = {"name": "c1", "version": "1.0.0", "required_fields": "not-a-list"}
    cand = {"name": "c1", "version": "1.1.0", "required_fields": "not-a-list"}
    assert _only(engine.compare_contracts([base], [cand])).passed


def test_contracts_are_compared_in_deterministic_name_order(engine):
    findings = engine.compare_contracts(
        [_contract("z", "1.0.0"), _contract("a", "1.0.0")],
        [_contract("z", "1.0.0"), _contract("a", "1.0.0")],
    )
    assert _ids(findings) == ["contract_compatibility.a", "contract_compatibility.z"]


# --- runtime compatibility -------------------------------------------------------
@pytest.mark.parametrize("required,provided", [(None, {}), ({}, None), ("x", {}), ([], {})])
def test_absent_or_malformed_runtime_evidence_is_breaking(engine, required, provided):
    finding = _only(engine.compare_runtime(required, provided))
    assert finding.check_id == "runtime_compatibility.evidence"
    assert finding.is_blocking_failure


def test_a_dropped_runtime_interface_is_breaking(engine):
    findings = engine.compare_runtime(
        {"interfaces": ["a", "b"], "abi": "1.0.0"}, {"interfaces": ["a"], "abi": "1.0.0"}
    )
    finding = _by_id(findings, "runtime_compatibility.interfaces")
    assert finding.is_blocking_failure
    assert finding.details["missing"] == ["b"]


def test_providing_every_required_interface_passes(engine):
    findings = engine.compare_runtime(
        {"interfaces": ["a"], "abi": "1.0.0"}, {"interfaces": ["a", "b"], "abi": "1.0.0"}
    )
    assert _by_id(findings, "runtime_compatibility.interfaces").passed


def test_an_absent_abi_is_breaking(engine):
    findings = engine.compare_runtime({"interfaces": []}, {"interfaces": []})
    assert _by_id(findings, "runtime_compatibility.abi").is_blocking_failure


def test_an_abi_major_change_is_breaking(engine):
    findings = engine.compare_runtime(
        {"interfaces": [], "abi": "1.0.0"}, {"interfaces": [], "abi": "2.0.0"}
    )
    finding = _by_id(findings, "runtime_compatibility.abi")
    assert finding.is_blocking_failure
    assert finding.details == {"required": "1.0.0", "provided": "2.0.0"}


def test_an_abi_below_the_required_floor_is_breaking(engine):
    findings = engine.compare_runtime(
        {"interfaces": [], "abi": "1.2.0"}, {"interfaces": [], "abi": "1.1.0"}
    )
    assert _by_id(findings, "runtime_compatibility.abi").is_blocking_failure


def test_an_abi_at_or_above_the_floor_in_the_same_major_passes(engine):
    findings = engine.compare_runtime(
        {"interfaces": [], "abi": "1.1.0"}, {"interfaces": [], "abi": "1.4.2"}
    )
    assert _by_id(findings, "runtime_compatibility.abi").passed


def test_runtime_comparison_reports_interfaces_then_abi(engine):
    findings = engine.compare_runtime(
        {"interfaces": ["a"], "abi": "1.0.0"}, {"interfaces": ["a"], "abi": "1.0.0"}
    )
    assert _ids(findings) == ["runtime_compatibility.interfaces", "runtime_compatibility.abi"]


# --- version compatibility -------------------------------------------------------
@pytest.mark.parametrize("components", [None, "x", {"id": "a"}])
def test_absent_or_malformed_components_are_breaking(engine, components):
    finding = _only(engine.compare_versions(components))
    assert finding.check_id == "version_compatibility.evidence"
    assert finding.is_blocking_failure


@pytest.mark.parametrize("component", ["nope", {"version": "1.0.0"}, {}])
def test_a_malformed_component_declaration_is_breaking(engine, component):
    finding = _only(engine.compare_versions([component]))
    assert finding.check_id == "version_compatibility.evidence"
    assert finding.is_blocking_failure


def test_a_component_without_a_valid_version_is_breaking(engine):
    finding = _only(engine.compare_versions([{"id": "a", "version": "bad"}]))
    assert finding.details["component"] == "a"
    assert finding.is_blocking_failure


def test_components_without_requirements_yield_an_explicit_finding(engine):
    """Silence is not a pass: the no-requirements case is recorded as evidence."""
    finding = _only(engine.compare_versions([{"id": "a", "version": "1.0.0"}]))
    assert finding.check_id == "version_compatibility.no-requirements"
    assert finding.passed
    assert finding.details["components"] == 1


def test_an_empty_component_set_yields_the_no_requirements_finding(engine):
    finding = _only(engine.compare_versions([]))
    assert finding.check_id == "version_compatibility.no-requirements"
    assert finding.details["components"] == 0


def test_malformed_requirements_are_breaking(engine):
    finding = _only(
        engine.compare_versions([{"id": "a", "version": "1.0.0", "requires": "not-a-mapping"}])
    )
    assert finding.check_id == "version_compatibility.a"
    assert finding.is_blocking_failure


def test_requiring_an_unknown_component_is_breaking(engine):
    finding = _only(
        engine.compare_versions([{"id": "a", "version": "1.0.0", "requires": {"ghost": "^1.0.0"}}])
    )
    assert finding.check_id == "version_compatibility.a->ghost"
    assert finding.is_blocking_failure


@pytest.mark.parametrize("spec", ["^1.0.0", ">=1.0.0", "=1.0.0", "1.0.0"])
def test_a_satisfied_requirement_passes_for_every_spec_form(engine, spec):
    findings = engine.compare_versions(
        [
            {"id": "a", "version": "1.0.0", "requires": {"b": spec}},
            {"id": "b", "version": "1.2.0"},
        ]
    )
    finding = _by_id(findings, "version_compatibility.a->b")
    assert finding.passed
    assert finding.details["spec"] == spec


@pytest.mark.parametrize("spec", ["^2.0.0", ">=2.0.0", "=2.0.0", "2.0.0"])
def test_a_cross_major_resolution_is_never_compatible(engine, spec):
    findings = engine.compare_versions(
        [
            {"id": "a", "version": "1.0.0", "requires": {"b": spec}},
            {"id": "b", "version": "1.9.9"},
        ]
    )
    assert _by_id(findings, "version_compatibility.a->b").is_blocking_failure


@pytest.mark.parametrize("spec", ["^1.5.0", ">=1.5.0", "=1.5.0"])
def test_a_resolution_below_the_floor_is_breaking(engine, spec):
    findings = engine.compare_versions(
        [
            {"id": "a", "version": "1.0.0", "requires": {"b": spec}},
            {"id": "b", "version": "1.4.0"},
        ]
    )
    finding = _by_id(findings, "version_compatibility.a->b")
    assert finding.is_blocking_failure
    assert finding.details["resolved"] == "1.4.0"


@pytest.mark.parametrize("spec", ["~1.0.0", "1.x", "", "not-a-spec", ">1.0.0"])
def test_a_malformed_version_spec_is_breaking(engine, spec):
    findings = engine.compare_versions(
        [
            {"id": "a", "version": "1.0.0", "requires": {"b": spec}},
            {"id": "b", "version": "1.0.0"},
        ]
    )
    assert _by_id(findings, "version_compatibility.a->b").is_blocking_failure


def test_a_non_string_spec_is_breaking(engine):
    findings = engine.compare_versions(
        [
            {"id": "a", "version": "1.0.0", "requires": {"b": 17}},
            {"id": "b", "version": "1.0.0"},
        ]
    )
    assert _by_id(findings, "version_compatibility.a->b").is_blocking_failure


def test_requirements_are_checked_in_deterministic_component_and_dependency_order(engine):
    findings = engine.compare_versions(
        [
            {"id": "z", "version": "1.0.0", "requires": {"b": "^1.0.0", "a": "^1.0.0"}},
            {"id": "a", "version": "1.0.0", "requires": {"b": "^1.0.0"}},
            {"id": "b", "version": "1.0.0"},
        ]
    )
    assert _ids(findings) == [
        "version_compatibility.a->b",
        "version_compatibility.z->a",
        "version_compatibility.z->b",
    ]


# --- report projection -----------------------------------------------------------
def test_build_compatibility_report_projects_the_compatibility_dimensions():
    dimension = IntelligenceDimension.CONTRACT_COMPATIBILITY
    findings = CompatibilityEngine().compare_contracts(
        [_contract("c1", "1.0.0")], [_contract("c1", "1.0.0")]
    )
    report = ValidationIntelligenceReport.create(
        target_id="t",
        target_digest="d",
        dimension_reports=(DimensionReport.create(dimension, findings),),
    )
    projected = build_compatibility_report(report)
    assert projected.compatible is True
    assert projected.dimension_verdicts == {dimension.value: "pass"}


def test_every_compatibility_finding_is_blocking():
    """The Compatibility Engine issues no advisory findings — a break always blocks."""
    engine = CompatibilityEngine()
    findings = (
        engine.compare_contracts([_contract("c", "1.0.0")], [])
        + engine.compare_runtime({"interfaces": ["a"], "abi": "1.0.0"}, {"interfaces": []})
        + engine.compare_versions([{"id": "a", "version": "1.0.0"}])
    )
    assert findings
    assert all(f.severity is Severity.BLOCKING for f in findings)
