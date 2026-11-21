"""UCOS-EPIC-005 — Universal Validation rule tests (Terminal T5).

Each rule is exercised on both its passing path and at least one fail-closed path
(absent/malformed evidence), because "absence of evidence is never evidence of
correctness" is the mission mandate.
"""

from __future__ import annotations

from platform.tests.universal_validation_helpers import passing_facts
from platform.universal_validation.contracts import (
    RuleStatus,
    ValidationDomain,
    ValidationTarget,
)
from platform.universal_validation.rules import (
    ArchitectureAcyclicRule,
    CoverageThresholdRule,
    DependenciesPinnedRule,
    DependenciesResolvedRule,
    DependencyAcyclicRule,
    DisclosurePresentRule,
    EntrypointsResolvedRule,
    LayeringRespectedRule,
    LayersDeclaredRule,
    LintCleanRule,
    ModulesPresentRule,
    NoFrozenWritesRule,
    NoOpenMarkersRule,
    RecordsConformRule,
    RegistryEntriesWellFormedRule,
    RegistryIdsUniqueRule,
    RegistryReferentialIntegrityRule,
    RuntimeIdentityRule,
    RuntimeImagePinnedRule,
    SchemaVersionedRule,
    TestsPassingRule,
    _detect_cycle,
    default_rules,
)

import pytest


def _target(domain: ValidationDomain, facts: dict) -> ValidationTarget:
    return ValidationTarget(target_id="T", facts={domain.value: facts})


def _facts(domain: ValidationDomain) -> dict:
    return dict(passing_facts()[domain.value])


# -- suite composition --------------------------------------------------------
def test_default_rules_ordered_and_complete():
    rules = default_rules()
    assert len(rules) == 21
    # every domain covered
    assert {r.domain for r in rules} == set(ValidationDomain)
    # ordered by (domain order, rule id)
    keys = [(r.domain.order, r.rule_id) for r in rules]
    assert keys == sorted(keys)


def test_detect_cycle_finds_and_clears():
    assert _detect_cycle([("a", "b"), ("b", "c")]) is None
    cycle = _detect_cycle([("a", "b"), ("b", "a")])
    assert cycle is not None and cycle[0] == cycle[-1]


def test_detect_cycle_handles_revisited_node():
    # A diamond (a->b, a->c, b->d, c->d) revisits an already-finished node with no cycle.
    assert _detect_cycle([("a", "b"), ("a", "c"), ("b", "d"), ("c", "d")]) is None


# -- architecture -------------------------------------------------------------
def test_layers_declared_rule():
    ok = LayersDeclaredRule().evaluate(
        _target(ValidationDomain.ARCHITECTURE, _facts(ValidationDomain.ARCHITECTURE))
    )
    assert ok.status is RuleStatus.PASS
    assert LayersDeclaredRule().evaluate(_target(ValidationDomain.ARCHITECTURE, {})).failed
    dup = LayersDeclaredRule().evaluate(
        _target(ValidationDomain.ARCHITECTURE, {"layers": ["a", "a"]})
    )
    assert dup.failed
    empty = LayersDeclaredRule().evaluate(
        _target(ValidationDomain.ARCHITECTURE, {"layers": ["", "b"]})
    )
    assert empty.failed


def test_architecture_acyclic_rule():
    ok = ArchitectureAcyclicRule().evaluate(
        _target(ValidationDomain.ARCHITECTURE, _facts(ValidationDomain.ARCHITECTURE))
    )
    assert ok.status is RuleStatus.PASS
    assert ArchitectureAcyclicRule().evaluate(_target(ValidationDomain.ARCHITECTURE, {})).failed
    malformed = ArchitectureAcyclicRule().evaluate(
        _target(ValidationDomain.ARCHITECTURE, {"dependencies": [{"from": "a"}]})
    )
    assert malformed.failed
    cyclic = ArchitectureAcyclicRule().evaluate(
        _target(
            ValidationDomain.ARCHITECTURE,
            {"dependencies": [{"from": "a", "to": "b"}, {"from": "b", "to": "a"}]},
        )
    )
    assert cyclic.failed and "cycle" in cyclic.details


def test_layering_respected_rule():
    ok = LayeringRespectedRule().evaluate(
        _target(ValidationDomain.ARCHITECTURE, _facts(ValidationDomain.ARCHITECTURE))
    )
    assert ok.status is RuleStatus.PASS
    assert LayeringRespectedRule().evaluate(_target(ValidationDomain.ARCHITECTURE, {})).failed
    upward = LayeringRespectedRule().evaluate(
        _target(
            ValidationDomain.ARCHITECTURE,
            {"layers": ["a", "b"], "dependencies": [{"from": "b", "to": "a"}]},
        )
    )
    assert upward.failed and upward.details["violations"]
    undeclared = LayeringRespectedRule().evaluate(
        _target(
            ValidationDomain.ARCHITECTURE,
            {"layers": ["a"], "dependencies": [{"from": "a", "to": "z"}]},
        )
    )
    assert undeclared.failed
    malformed = LayeringRespectedRule().evaluate(
        _target(ValidationDomain.ARCHITECTURE, {"layers": ["a"], "dependencies": ["x"]})
    )
    assert malformed.failed


def test_no_frozen_writes_rule():
    ok = NoFrozenWritesRule().evaluate(
        _target(ValidationDomain.ARCHITECTURE, _facts(ValidationDomain.ARCHITECTURE))
    )
    assert ok.status is RuleStatus.PASS
    assert NoFrozenWritesRule().evaluate(_target(ValidationDomain.ARCHITECTURE, {})).failed
    violation = NoFrozenWritesRule().evaluate(
        _target(ValidationDomain.ARCHITECTURE, {"changed_paths": ["00-BOOK/x.md"]})
    )
    assert violation.failed and violation.details["violations"] == ["00-BOOK/x.md"]


# -- implementation -----------------------------------------------------------
def test_modules_present_rule():
    ok = ModulesPresentRule().evaluate(
        _target(ValidationDomain.IMPLEMENTATION, _facts(ValidationDomain.IMPLEMENTATION))
    )
    assert ok.status is RuleStatus.PASS
    assert ModulesPresentRule().evaluate(_target(ValidationDomain.IMPLEMENTATION, {})).failed
    missing = ModulesPresentRule().evaluate(
        _target(ValidationDomain.IMPLEMENTATION, {"modules": [{"id": "m", "present": False}]})
    )
    assert missing.failed and missing.details["missing"] == ["m"]
    malformed = ModulesPresentRule().evaluate(
        _target(ValidationDomain.IMPLEMENTATION, {"modules": [{"present": True}]})
    )
    assert malformed.failed


def test_entrypoints_resolved_rule():
    ok = EntrypointsResolvedRule().evaluate(
        _target(ValidationDomain.IMPLEMENTATION, _facts(ValidationDomain.IMPLEMENTATION))
    )
    assert ok.status is RuleStatus.PASS
    assert EntrypointsResolvedRule().evaluate(_target(ValidationDomain.IMPLEMENTATION, {})).failed
    unresolved = EntrypointsResolvedRule().evaluate(
        _target(
            ValidationDomain.IMPLEMENTATION, {"entrypoints": [{"name": "e", "resolved": False}]}
        )
    )
    assert unresolved.failed
    malformed = EntrypointsResolvedRule().evaluate(
        _target(ValidationDomain.IMPLEMENTATION, {"entrypoints": [{"resolved": True}]})
    )
    assert malformed.failed


def test_no_open_markers_rule_is_advisory():
    rule = NoOpenMarkersRule()
    assert (
        rule.evaluate(_target(ValidationDomain.IMPLEMENTATION, {"open_markers": 0})).status
        is RuleStatus.PASS
    )
    assert rule.evaluate(_target(ValidationDomain.IMPLEMENTATION, {"open_markers": 3})).failed
    assert rule.evaluate(_target(ValidationDomain.IMPLEMENTATION, {})).failed
    assert rule.evaluate(_target(ValidationDomain.IMPLEMENTATION, {"open_markers": True})).failed


# -- dependency ---------------------------------------------------------------
def test_dependencies_pinned_rule():
    ok = DependenciesPinnedRule().evaluate(
        _target(ValidationDomain.DEPENDENCY, _facts(ValidationDomain.DEPENDENCY))
    )
    assert ok.status is RuleStatus.PASS
    assert DependenciesPinnedRule().evaluate(_target(ValidationDomain.DEPENDENCY, {})).failed
    unpinned = DependenciesPinnedRule().evaluate(
        _target(ValidationDomain.DEPENDENCY, {"dependencies": [{"id": "d"}]})
    )
    assert unpinned.failed and unpinned.details["unpinned"] == ["d"]
    digest_ok = DependenciesPinnedRule().evaluate(
        _target(ValidationDomain.DEPENDENCY, {"dependencies": [{"id": "d", "digest": "x"}]})
    )
    assert digest_ok.status is RuleStatus.PASS
    malformed = DependenciesPinnedRule().evaluate(
        _target(ValidationDomain.DEPENDENCY, {"dependencies": [{"version": "1.0.0"}]})
    )
    assert malformed.failed


def test_dependencies_resolved_rule():
    ok = DependenciesResolvedRule().evaluate(
        _target(ValidationDomain.DEPENDENCY, _facts(ValidationDomain.DEPENDENCY))
    )
    assert ok.status is RuleStatus.PASS
    assert DependenciesResolvedRule().evaluate(_target(ValidationDomain.DEPENDENCY, {})).failed
    unresolved = DependenciesResolvedRule().evaluate(
        _target(
            ValidationDomain.DEPENDENCY,
            {"dependencies": [{"id": "d", "provider": "missing"}], "providers": ["other"]},
        )
    )
    assert unresolved.failed
    malformed = DependenciesResolvedRule().evaluate(
        _target(ValidationDomain.DEPENDENCY, {"dependencies": [{}], "providers": []})
    )
    assert malformed.failed


def test_dependency_acyclic_rule():
    ok = DependencyAcyclicRule().evaluate(
        _target(ValidationDomain.DEPENDENCY, _facts(ValidationDomain.DEPENDENCY))
    )
    assert ok.status is RuleStatus.PASS
    assert DependencyAcyclicRule().evaluate(_target(ValidationDomain.DEPENDENCY, {})).failed
    cyclic = DependencyAcyclicRule().evaluate(
        _target(
            ValidationDomain.DEPENDENCY,
            {"edges": [{"from": "a", "to": "b"}, {"from": "b", "to": "a"}]},
        )
    )
    assert cyclic.failed
    malformed = DependencyAcyclicRule().evaluate(
        _target(ValidationDomain.DEPENDENCY, {"edges": [{"from": "a"}]})
    )
    assert malformed.failed


# -- registry -----------------------------------------------------------------
def test_registry_entries_well_formed_rule():
    ok = RegistryEntriesWellFormedRule().evaluate(
        _target(ValidationDomain.REGISTRY, _facts(ValidationDomain.REGISTRY))
    )
    assert ok.status is RuleStatus.PASS
    assert RegistryEntriesWellFormedRule().evaluate(_target(ValidationDomain.REGISTRY, {})).failed
    malformed = RegistryEntriesWellFormedRule().evaluate(
        _target(ValidationDomain.REGISTRY, {"entries": [{"id": "e", "kind": "k"}]})
    )
    assert malformed.failed


def test_registry_ids_unique_rule():
    ok = RegistryIdsUniqueRule().evaluate(
        _target(ValidationDomain.REGISTRY, _facts(ValidationDomain.REGISTRY))
    )
    assert ok.status is RuleStatus.PASS
    assert RegistryIdsUniqueRule().evaluate(_target(ValidationDomain.REGISTRY, {})).failed
    dup = RegistryIdsUniqueRule().evaluate(
        _target(
            ValidationDomain.REGISTRY,
            {"entries": [{"id": "e", "kind": "k", "content_hash": "h"}, {"id": "e"}]},
        )
    )
    assert dup.failed and dup.details["duplicates"] == ["e"]
    malformed = RegistryIdsUniqueRule().evaluate(
        _target(ValidationDomain.REGISTRY, {"entries": [{"kind": "k"}]})
    )
    assert malformed.failed


def test_registry_referential_integrity_rule():
    ok = RegistryReferentialIntegrityRule().evaluate(
        _target(ValidationDomain.REGISTRY, _facts(ValidationDomain.REGISTRY))
    )
    assert ok.status is RuleStatus.PASS
    assert (
        RegistryReferentialIntegrityRule().evaluate(_target(ValidationDomain.REGISTRY, {})).failed
    )
    dangling = RegistryReferentialIntegrityRule().evaluate(
        _target(
            ValidationDomain.REGISTRY,
            {
                "entries": [{"id": "e", "kind": "k", "content_hash": "h"}],
                "references": [{"from": "e", "to": "z"}],
            },
        )
    )
    assert dangling.failed
    malformed = RegistryReferentialIntegrityRule().evaluate(
        _target(ValidationDomain.REGISTRY, {"entries": [], "references": [{"from": "a"}]})
    )
    assert malformed.failed


# -- schema -------------------------------------------------------------------
def test_schema_versioned_rule():
    ok = SchemaVersionedRule().evaluate(
        _target(ValidationDomain.SCHEMA, _facts(ValidationDomain.SCHEMA))
    )
    assert ok.status is RuleStatus.PASS
    assert SchemaVersionedRule().evaluate(_target(ValidationDomain.SCHEMA, {})).failed
    unversioned = SchemaVersionedRule().evaluate(
        _target(ValidationDomain.SCHEMA, {"schemas": {"s": {"required": []}}})
    )
    assert unversioned.failed


def test_records_conform_rule():
    ok = RecordsConformRule().evaluate(
        _target(ValidationDomain.SCHEMA, _facts(ValidationDomain.SCHEMA))
    )
    assert ok.status is RuleStatus.PASS
    assert RecordsConformRule().evaluate(_target(ValidationDomain.SCHEMA, {})).failed
    unknown = RecordsConformRule().evaluate(
        _target(
            ValidationDomain.SCHEMA,
            {"schemas": {}, "records": [{"schema": "missing", "fields": {}}]},
        )
    )
    assert unknown.failed
    missing_field = RecordsConformRule().evaluate(
        _target(
            ValidationDomain.SCHEMA,
            {
                "schemas": {"s": {"version": "1", "required": ["a"]}},
                "records": [{"schema": "s", "fields": {}}],
            },
        )
    )
    assert missing_field.failed
    malformed = RecordsConformRule().evaluate(
        _target(ValidationDomain.SCHEMA, {"schemas": {"s": {"version": "1"}}, "records": [{}]})
    )
    assert malformed.failed


# -- runtime ------------------------------------------------------------------
def test_disclosure_present_rule():
    ok = DisclosurePresentRule().evaluate(
        _target(ValidationDomain.RUNTIME, _facts(ValidationDomain.RUNTIME))
    )
    assert ok.status is RuleStatus.PASS
    assert DisclosurePresentRule().evaluate(_target(ValidationDomain.RUNTIME, {})).failed
    bad = DisclosurePresentRule().evaluate(
        _target(ValidationDomain.RUNTIME, {"disclosure": {"disclosure_id": "wrong"}})
    )
    assert bad.failed


def test_runtime_identity_rule():
    ok = RuntimeIdentityRule().evaluate(
        _target(ValidationDomain.RUNTIME, _facts(ValidationDomain.RUNTIME))
    )
    assert ok.status is RuleStatus.PASS
    assert RuntimeIdentityRule().evaluate(_target(ValidationDomain.RUNTIME, {})).failed
    bad = RuntimeIdentityRule().evaluate(
        _target(ValidationDomain.RUNTIME, {"units": [{"runtime_id": "not-valid"}]})
    )
    assert bad.failed
    malformed = RuntimeIdentityRule().evaluate(_target(ValidationDomain.RUNTIME, {"units": ["x"]}))
    assert malformed.failed


def test_runtime_image_pinned_rule():
    ok = RuntimeImagePinnedRule().evaluate(
        _target(ValidationDomain.RUNTIME, _facts(ValidationDomain.RUNTIME))
    )
    assert ok.status is RuleStatus.PASS
    assert RuntimeImagePinnedRule().evaluate(_target(ValidationDomain.RUNTIME, {})).failed
    unpinned = RuntimeImagePinnedRule().evaluate(
        _target(
            ValidationDomain.RUNTIME,
            {
                "units": [
                    {"runtime_id": "r", "image_reference": "img:latest", "package_sha256": "h"}
                ]
            },
        )
    )
    assert unpinned.failed
    malformed = RuntimeImagePinnedRule().evaluate(
        _target(ValidationDomain.RUNTIME, {"units": ["x"]})
    )
    assert malformed.failed


# -- quality ------------------------------------------------------------------
def test_coverage_threshold_rule():
    ok = CoverageThresholdRule().evaluate(
        _target(ValidationDomain.QUALITY, _facts(ValidationDomain.QUALITY))
    )
    assert ok.status is RuleStatus.PASS
    assert CoverageThresholdRule().evaluate(_target(ValidationDomain.QUALITY, {})).failed
    below = CoverageThresholdRule().evaluate(
        _target(ValidationDomain.QUALITY, {"line_percent": 80.0, "min_percent": 90.0})
    )
    assert below.failed
    bad_min = CoverageThresholdRule().evaluate(
        _target(ValidationDomain.QUALITY, {"line_percent": 95.0, "min_percent": "x"})
    )
    assert bad_min.failed


def test_tests_passing_rule():
    ok = TestsPassingRule().evaluate(
        _target(ValidationDomain.QUALITY, _facts(ValidationDomain.QUALITY))
    )
    assert ok.status is RuleStatus.PASS
    assert TestsPassingRule().evaluate(_target(ValidationDomain.QUALITY, {})).failed
    failing = TestsPassingRule().evaluate(
        _target(ValidationDomain.QUALITY, {"tests": {"passed": 5, "failed": 2}})
    )
    assert failing.failed
    none_run = TestsPassingRule().evaluate(
        _target(ValidationDomain.QUALITY, {"tests": {"passed": 0, "failed": 0}})
    )
    assert none_run.failed
    malformed = TestsPassingRule().evaluate(
        _target(ValidationDomain.QUALITY, {"tests": {"passed": "x", "failed": 0}})
    )
    assert malformed.failed
    malformed_failed = TestsPassingRule().evaluate(
        _target(ValidationDomain.QUALITY, {"tests": {"passed": 1, "failed": "x"}})
    )
    assert malformed_failed.failed


def test_lint_clean_rule_is_advisory():
    rule = LintCleanRule()
    assert rule.severity.value == "advisory"
    assert (
        rule.evaluate(_target(ValidationDomain.QUALITY, {"lint_violations": 0})).status
        is RuleStatus.PASS
    )
    assert rule.evaluate(_target(ValidationDomain.QUALITY, {"lint_violations": 4})).failed
    assert rule.evaluate(_target(ValidationDomain.QUALITY, {})).failed


def test_abstract_rule_cannot_be_instantiated():
    from platform.universal_validation.rules import ValidationRule

    with pytest.raises(TypeError):
        ValidationRule()  # type: ignore[abstract]
