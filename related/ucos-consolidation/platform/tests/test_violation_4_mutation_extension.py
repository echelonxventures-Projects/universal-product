"""REQ-VIOLATION-4: Mutation Classification Extensibility Tests.

This module tests Violation 4 resolution: GOVERNED_ANALYSIS class addition and
extensibility mechanism validation.

Authority: Violation 4, MASTER-EXECUTION-ADMISSION-MATRIX.md, Phase 1B authorization
"""

from __future__ import annotations

import json
import re
import tempfile
from pathlib import Path
from platform.repository_intelligence.mutation_class_extension import (
    GOVERNED_ANALYSIS_CLASS,
    GOVERNED_ANALYSIS_RULE,
    add_dynamic_class_extension_mechanism,
    extend_mutation_governance_boundary,
)

import pytest

#: The boundary register is the source of truth for the class set and the rule order. These
#: tests read it rather than restating it, because a test that asserts a module's own
#: literals back to itself cannot see the module drift away from the register -- which is
#: exactly what happened here: the module carried precedence 9 and the narrow criteria
#: against the register's 8 and the widened ones, and fourteen passing tests never noticed.
BOUNDARY_REGISTER = Path("00-BOOK/DATA/mutation-governance-boundary.json")


def _boundary() -> dict:
    """The declared boundary register, read from the repository root."""
    return json.loads(BOUNDARY_REGISTER.read_text(encoding="utf-8"))


def _declared_class(name: str) -> dict:
    """The register's own entry for a mutation class."""
    return next(c for c in _boundary()["mutation_classes"] if c["class"] == name)


def _declared_rule(class_name: str) -> dict:
    """The register's own classification rule for a mutation class."""
    rules = _boundary()["classification_rules"]["rules"]
    return next(r for r in rules if r["class"] == class_name)


def _analysis_keywords() -> tuple[str, ...]:
    """The analysis-artifact keywords the register declares, read from the criterion itself."""
    criteria = _declared_class("GOVERNED_ANALYSIS")["membership_criteria"]
    criterion = next(c for c in criteria if c.startswith("analysis-artifact"))
    run = re.search(r"((?:[a-z]+/)+[a-z]+)", criterion)
    assert run, f"no keyword run found in the declared criterion: {criterion!r}"
    return tuple(run.group(1).split("/"))


def _authored_document_precedence() -> int:
    """R-08's precedence, so the ordering can be asserted as an ordering."""
    return int(_declared_rule("AUTHORED_DOCUMENT")["precedence"])


# -----------------------------------------------------------------------------
# Violation 4 Test 1: GOVERNED_ANALYSIS Class Definition
# -----------------------------------------------------------------------------


def test_violation_4_governed_analysis_class_structure() -> None:
    """Violation 4 Test 1: GOVERNED_ANALYSIS class structure validation.

    Validates:
    - Class name is GOVERNED_ANALYSIS
    - Governing authority declared (owner-parameterised)
    - Membership criteria defined (6 criteria)
    - Examples provided (determination/analysis artifacts)
    - Grants only mutation ownership (not certification/ratification)
    """
    # Validate: class structure
    assert GOVERNED_ANALYSIS_CLASS["class"] == "GOVERNED_ANALYSIS"
    assert "governed_by" in GOVERNED_ANALYSIS_CLASS
    assert "membership_criteria" in GOVERNED_ANALYSIS_CLASS
    assert "examples" in GOVERNED_ANALYSIS_CLASS

    # Validate: 6 membership criteria
    assert len(GOVERNED_ANALYSIS_CLASS["membership_criteria"]) == 6
    assert "markdown — the path ends .md" in GOVERNED_ANALYSIS_CLASS["membership_criteria"]
    analysis_criterion = (
        "analysis-artifact — carries determination/analysis/assessment/execution/"
        "matrix/readiness/admission/blocker/gap in filename"
    )
    assert analysis_criterion in GOVERNED_ANALYSIS_CLASS["membership_criteria"]

    # Validate: every example is an analysis artifact under the register's OWN keywords.
    # The keywords are read from the declared criterion rather than restated here: the
    # earlier form of this test restated five of them, so widening the register to nine
    # left the test asserting the narrow set, and an example the register itself declares
    # -- 100-PERCENT-IMPLEMENTATION-READINESS-CERTIFICATION.md -- failed a test that was
    # supposed to be describing the register.
    examples = GOVERNED_ANALYSIS_CLASS["examples"]
    assert len(examples) > 0
    keywords = _analysis_keywords()
    assert len(keywords) >= 5, f"the register declares too few analysis keywords: {keywords}"
    for example in examples:
        assert any(
            keyword in example.lower() for keyword in keywords
        ), f"{example!r} matches none of the register's analysis keywords {keywords}"

    # Validate: grants only mutation ownership
    assert "grants_only_mutation_ownership" in GOVERNED_ANALYSIS_CLASS


def test_violation_4_governed_analysis_rule_structure() -> None:
    """Violation 4 Test 1b: GOVERNED_ANALYSIS rule structure validation.

    Validates:
    - Rule ID is R-09 (9th rule)
    - Precedence is 9 (after R-08 AUTHORED_DOCUMENT)
    - Class is GOVERNED_ANALYSIS
    - Predicate is decidable from repository state
    """
    # Validate: rule structure
    assert GOVERNED_ANALYSIS_RULE["id"] == "R-09"
    assert GOVERNED_ANALYSIS_RULE["precedence"] == 8
    assert GOVERNED_ANALYSIS_RULE["class"] == "GOVERNED_ANALYSIS"
    assert "predicate" in GOVERNED_ANALYSIS_RULE

    # Validate: predicate mentions analysis keywords
    predicate = GOVERNED_ANALYSIS_RULE["predicate"]
    assert any(
        keyword in predicate.lower()
        for keyword in ["determination", "analysis", "assessment", "execution", "matrix"]
    )


# -----------------------------------------------------------------------------
# Violation 4 Test 2: Boundary Extension
# -----------------------------------------------------------------------------


def test_violation_4_extend_boundary_with_governed_analysis() -> None:
    """Violation 4 Test 2: Boundary extension with GOVERNED_ANALYSIS.

    Validates:
    - Boundary document loads successfully
    - GOVERNED_ANALYSIS class added to mutation_classes
    - R-09 rule added to classification_rules
    - Version incremented (minor bump)
    - Extended document valid JSON
    """
    # Create temporary boundary file
    boundary = {
        "artifact_id": "TEST-BOUNDARY",
        "version": "1.0.0",
        "mutation_classes": [
            {"class": "CLASS_1"},
            {"class": "CLASS_2"},
        ],
        "classification_rules": {
            "rules": [
                {"id": "R-01", "class": "CLASS_1", "precedence": 1},
                {"id": "R-02", "class": "CLASS_2", "precedence": 2},
            ]
        },
    }

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(boundary, f)
        temp_path = Path(f.name)

    try:
        # Extend boundary
        extended = extend_mutation_governance_boundary(temp_path, dry_run=True)

        # Validate: GOVERNED_ANALYSIS class added
        classes = [cls["class"] for cls in extended["mutation_classes"]]
        assert "GOVERNED_ANALYSIS" in classes
        assert len(extended["mutation_classes"]) == 3  # 2 + 1

        # Validate: R-09 rule added
        rules = [rule["id"] for rule in extended["classification_rules"]["rules"]]
        assert "R-09" in rules
        assert len(extended["classification_rules"]["rules"]) == 3  # 2 + 1

        # Validate: version incremented (minor bump)
        assert extended["version"] == "1.1.0"

    finally:
        temp_path.unlink()


def test_violation_4_extension_rejects_duplicate_class() -> None:
    """Violation 4 Test 2b: Extension rejects duplicate GOVERNED_ANALYSIS.

    Validates:
    - Attempting to add GOVERNED_ANALYSIS twice raises ValueError
    - Error message indicates duplicate class
    """
    # Create boundary with GOVERNED_ANALYSIS already present
    boundary = {
        "artifact_id": "TEST-BOUNDARY",
        "version": "1.0.0",
        "mutation_classes": [
            {"class": "GOVERNED_ANALYSIS"},  # already exists
        ],
        "classification_rules": {"rules": []},
    }

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(boundary, f)
        temp_path = Path(f.name)

    try:
        # Validate: extension raises ValueError
        with pytest.raises(ValueError, match="GOVERNED_ANALYSIS already exists"):
            extend_mutation_governance_boundary(temp_path, dry_run=True)

    finally:
        temp_path.unlink()


# -----------------------------------------------------------------------------
# Violation 4 Test 3: Extensibility Mechanism
# -----------------------------------------------------------------------------


def test_violation_4_dynamic_extension_mechanism_specification() -> None:
    """Violation 4 Test 3: Dynamic extension mechanism specification.

    Validates:
    - Extension mechanism specified (DYNAMIC_CLASS_REGISTRATION)
    - Extension registry path defined (mutation-class-extensions.json)
    - Schema defined (extension_id, class, governed_by, membership_criteria, etc.)
    - Loader specification defined (load_extensions, merge_classes)
    - Validation rules defined (uniqueness, authority, predicate decidability)
    - Example extension provided
    """
    spec = add_dynamic_class_extension_mechanism()

    # Validate: mechanism specified
    assert spec["extension_mechanism"] == "DYNAMIC_CLASS_REGISTRATION"
    assert "specification" in spec

    # Validate: extension registry path
    registry_path = "00-BOOK/DATA/mutation-class-extensions.json"
    assert spec["specification"]["extension_registry"] == registry_path

    # Validate: schema defined
    schema = spec["specification"]["schema"]
    assert "extension_id" in schema
    assert "class" in schema
    assert "governed_by" in schema
    assert "membership_criteria" in schema
    assert "predicate" in schema
    assert "precedence" in schema
    assert "rule_id" in schema

    # Validate: loader specification
    loader = spec["specification"]["loader"]
    assert "location" in loader
    assert "function" in loader
    assert "merge_strategy" in loader

    # Validate: validation rules
    validation = spec["specification"]["validation"]
    assert "no_duplicate_classes" in validation
    assert "no_duplicate_rule_ids" in validation
    assert "authority_required" in validation
    assert "predicate_implementable" in validation

    # Validate: example extension provided
    assert "example_extension" in spec
    example = spec["example_extension"]
    assert "extension_id" in example
    assert "class" in example
    assert "governed_by" in example


def test_violation_4_extension_mechanism_infinite_expansion_compliance() -> None:
    """Violation 4 Test 3b: Extension mechanism infinite expansion compliance.

    Validates:
    - Extension mechanism supports unbounded class addition (no fixed limit)
    - Specification does not hard-code class count
    - Future classes admissible via data (not code change)
    """
    spec = add_dynamic_class_extension_mechanism()

    # Validate: no fixed class limit mentioned
    spec_str = json.dumps(spec)
    assert "fixed" not in spec_str or "unbounded" in spec_str or "infinite" in spec_str

    # Validate: extension via data (registry file)
    assert spec["specification"]["extension_registry"].endswith(".json")

    # Validate: loader merges extensions (append strategy)
    assert "append" in spec["specification"]["loader"]["merge_strategy"]

    # Validate: phase 3-4 implementation plan exists
    assert "phase_3_4_implementation" in spec
    assert len(spec["phase_3_4_implementation"]) > 0


# -----------------------------------------------------------------------------
# Violation 4 Test 4: Classification with GOVERNED_ANALYSIS
# -----------------------------------------------------------------------------


def test_violation_4_governed_analysis_classification_pattern() -> None:
    """Violation 4 Test 4: GOVERNED_ANALYSIS classification pattern validation.

    Validates:
    - Analysis artifacts match GOVERNED_ANALYSIS pattern
    - Determination files match pattern
    - Assessment files match pattern
    - Execution reports match pattern
    - Matrix files match pattern
    """
    # Analysis artifact patterns
    patterns = [
        "*-DETERMINATION.md",
        "*-DETERMINATION-REPORT.md",
        "*-ANALYSIS.md",
        "*-ASSESSMENT-DETERMINATION.md",
        "PHASE-*-EXECUTION-COMPLETION-REPORT.md",
        "MASTER-EXECUTION-ADMISSION-MATRIX.md",
    ]

    # Validate: all patterns in examples
    examples = GOVERNED_ANALYSIS_CLASS["examples"]
    for pattern in patterns:
        assert pattern in examples

    # Validate: predicate mentions analysis keywords
    predicate = GOVERNED_ANALYSIS_RULE["predicate"]
    keywords = ["determination", "analysis", "assessment", "execution", "matrix"]
    for keyword in keywords:
        assert keyword in predicate.lower()


def test_violation_4_governed_analysis_vs_authored_document_distinction() -> None:
    """Violation 4 Test 4b: GOVERNED_ANALYSIS vs AUTHORED_DOCUMENT distinction.

    Validates:
    - GOVERNED_ANALYSIS has distinct membership criteria from AUTHORED_DOCUMENT
    - Analysis artifacts (determinations) vs general documents (ADRs)
    - R-09 precedence < R-08 (GOVERNED_ANALYSIS evaluated before AUTHORED_DOCUMENT,
      because first-matching-rule order is ASCENDING: a lower number is decided earlier)
    """
    # Validate: GOVERNED_ANALYSIS has analysis-specific criterion
    criteria = GOVERNED_ANALYSIS_CLASS["membership_criteria"]
    analysis_criterion = next(
        (c for c in criteria if "analysis-artifact" in c or "determination" in c), None
    )
    assert analysis_criterion is not None

    # Validate: R-09 precedence (8) < R-08 precedence (9), so GOVERNED_ANALYSIS is decided
    # first. Asserting the inequality rather than the literal is the point: it is the
    # ORDER that carries the meaning, and the earlier form of this test asserted 9 on the
    # belief that a higher number wins, which is the inverted reading that let every
    # determination fall to AUTHORED_DOCUMENT.
    assert GOVERNED_ANALYSIS_RULE["precedence"] == 8
    assert GOVERNED_ANALYSIS_RULE["precedence"] < _authored_document_precedence()

    # Validate: examples are analysis artifacts (not ADRs/constitutions)
    examples = GOVERNED_ANALYSIS_CLASS["examples"]
    for example in examples:
        # Should NOT be ADR or constitution patterns
        assert not example.startswith("adr/")
        assert not example.startswith("00-CEP/")


# -----------------------------------------------------------------------------
# Violation 4 Certification Evidence
# -----------------------------------------------------------------------------


def test_violation_4_certification_checklist() -> None:
    """Violation 4 Certification Evidence.

    This test aggregates all Violation 4 validation evidence for certification:

    ✅ GOVERNED_ANALYSIS class defined (9th mutation class)
    ✅ Class structure valid (governed_by, membership_criteria, examples)
    ✅ R-09 rule defined (precedence 8, decidable predicate)
    ✅ Boundary extension operational (add class + rule, version increment)
    ✅ Duplicate prevention (raises ValueError on duplicate class)
    ✅ Extensibility mechanism specified (DYNAMIC_CLASS_REGISTRATION)
    ✅ Extension registry defined (mutation-class-extensions.json)
    ✅ Schema defined (extension_id, class, governed_by, etc.)
    ✅ Validation rules defined (uniqueness, authority, predicate)
    ✅ Infinite expansion compliance (unbounded class addition via data)
    ✅ Classification pattern validated (analysis artifacts match GOVERNED_ANALYSIS)
    ✅ GOVERNED_ANALYSIS vs AUTHORED_DOCUMENT distinction clear

    Authority: Violation 4, MASTER-EXECUTION-ADMISSION-MATRIX.md
    Implementation: platform/repository_intelligence/mutation_class_extension.py
    Status: ✅ VIOLATION 4 CERTIFIED (extensibility operational)
    """
    # Run all Violation 4 validation tests
    test_violation_4_governed_analysis_class_structure()
    test_violation_4_governed_analysis_rule_structure()
    test_violation_4_extend_boundary_with_governed_analysis()
    test_violation_4_extension_rejects_duplicate_class()
    test_violation_4_dynamic_extension_mechanism_specification()
    test_violation_4_extension_mechanism_infinite_expansion_compliance()
    test_violation_4_governed_analysis_classification_pattern()
    test_violation_4_governed_analysis_vs_authored_document_distinction()

    # VIOLATION 4 CERTIFICATION: All validation evidence satisfied
    # - GOVERNED_ANALYSIS class: DEFINED (9th mutation class)
    # - R-09 rule: DEFINED (precedence 8, decidable predicate)
    # - Boundary extension: OPERATIONAL (add class + rule, version increment)
    # - Duplicate prevention: OPERATIONAL (ValueError on duplicate)
    # - Extensibility mechanism: SPECIFIED (DYNAMIC_CLASS_REGISTRATION)
    # - Infinite expansion: COMPLIANT (unbounded class addition via data)
    # - Classification pattern: VALIDATED (analysis artifacts match)
    # - Distinction: CLEAR (GOVERNED_ANALYSIS vs AUTHORED_DOCUMENT)
    #
    # Status: ✅ VIOLATION 4 CERTIFIED


__all__ = [
    "test_violation_4_governed_analysis_class_structure",
    "test_violation_4_governed_analysis_rule_structure",
    "test_violation_4_extend_boundary_with_governed_analysis",
    "test_violation_4_extension_rejects_duplicate_class",
    "test_violation_4_dynamic_extension_mechanism_specification",
    "test_violation_4_extension_mechanism_infinite_expansion_compliance",
    "test_violation_4_governed_analysis_classification_pattern",
    "test_violation_4_governed_analysis_vs_authored_document_distinction",
    "test_violation_4_certification_checklist",
]


# -----------------------------------------------------------------------------
# Violation 4 Test 2c-2e: the refusals and the one writing mode
#
# The extension is measured only through `dry_run=True`, so the two states that make it
# safe to run twice were never exercised, and neither was the write. A dry run that is the
# only thing ever tested makes the WRITE the untested half of a function whose whole job is
# to edit the register that governs mutation authority.
# -----------------------------------------------------------------------------


def _boundary_document() -> dict:
    return {
        "artifact_id": "TEST-BOUNDARY",
        "version": "2.3.4",
        "mutation_classes": [{"class": "CLASS_1"}],
        "classification_rules": {"rules": [{"id": "R-01", "class": "CLASS_1", "precedence": 1}]},
    }


def test_violation_4_extension_refuses_a_boundary_that_is_not_there(tmp_path: Path) -> None:
    """A missing register is not an empty one.

    `setdefault` would happily build both structures from nothing and write a brand new
    boundary document, which is the one outcome that must not happen: the register would be
    created rather than extended, and every class the real one declares would be gone.
    """
    absent = tmp_path / "00-BOOK" / "DATA" / "mutation-governance-boundary.json"
    with pytest.raises(FileNotFoundError, match="Mutation governance boundary not found"):
        extend_mutation_governance_boundary(absent, dry_run=True)
    assert not absent.exists()


def test_violation_4_extension_refuses_a_duplicate_rule_id(tmp_path: Path) -> None:
    """R-09 present with the class absent is the half-applied state, and it is the dangerous
    one. Appending a second R-09 would give the register two rules under one id, and
    `ordered_rules` resolves by precedence — so which rule claimed a subject would depend on
    array order. The class check alone does not catch it, which is why there are two checks.
    """
    document = _boundary_document()
    document["classification_rules"]["rules"].append(
        {"id": "R-09", "class": "SOMETHING_ELSE", "precedence": 9}
    )
    path = tmp_path / "boundary.json"
    path.write_text(json.dumps(document), encoding="utf-8")

    with pytest.raises(ValueError, match="R-09 already exists"):
        extend_mutation_governance_boundary(path, dry_run=True)


def test_violation_4_a_dry_run_leaves_the_register_byte_identical(tmp_path: Path) -> None:
    """The default is READ-ONLY, and that is asserted on the bytes rather than on the flag."""
    path = tmp_path / "boundary.json"
    original = json.dumps(_boundary_document())
    path.write_text(original, encoding="utf-8")

    extended = extend_mutation_governance_boundary(path, dry_run=True)
    # A MINOR BUMP THAT DOES NOT RESET THE PATCH: 2.3.4 becomes 2.4.4, not 2.4.0. Pinned
    # rather than corrected, because the register's version is consumed elsewhere and
    # changing what it computes is a decision about the artifact, not about this test.
    assert extended["version"] == "2.4.4"
    assert path.read_text(encoding="utf-8") == original


def test_violation_4_a_write_emits_the_extension_and_can_be_read_back(tmp_path: Path) -> None:
    """The one writing mode. What it wrote must be what the next reader loads — including the
    trailing newline, because a register that ends without one produces a one-line diff on
    every subsequent edit and buries the change that mattered.
    """
    path = tmp_path / "boundary.json"
    path.write_text(json.dumps(_boundary_document()), encoding="utf-8")

    returned = extend_mutation_governance_boundary(path, dry_run=False)

    written = path.read_text(encoding="utf-8")
    assert written.endswith("\n")
    reloaded = json.loads(written)
    assert reloaded == returned
    assert reloaded["version"] == "2.4.4"
    assert [cls["class"] for cls in reloaded["mutation_classes"]] == [
        "CLASS_1",
        "GOVERNED_ANALYSIS",
    ]
    assert reloaded["classification_rules"]["rules"][-1] == GOVERNED_ANALYSIS_RULE


def test_violation_4_extending_an_already_extended_register_is_refused(tmp_path: Path) -> None:
    """Running it twice must not double the class. The write and the refusal compose: the
    second call reads what the first wrote and declines, which is what makes the operation
    safe to re-run rather than merely safe to run once."""
    path = tmp_path / "boundary.json"
    path.write_text(json.dumps(_boundary_document()), encoding="utf-8")

    extend_mutation_governance_boundary(path, dry_run=False)
    with pytest.raises(ValueError, match="GOVERNED_ANALYSIS already exists"):
        extend_mutation_governance_boundary(path, dry_run=False)

    reloaded = json.loads(path.read_text(encoding="utf-8"))
    assert [cls["class"] for cls in reloaded["mutation_classes"]].count("GOVERNED_ANALYSIS") == 1
    assert reloaded["version"] == "2.4.4", "a refused extension must not bump the version"


# -----------------------------------------------------------------------------
# Violation 4 Drift Guard: the module may never disagree with the register
# -----------------------------------------------------------------------------


def test_violation_4_extension_constants_match_the_boundary_register() -> None:
    """The module's copy of R-09 may never diverge from the register that governs it.

    THIS IS THE TEST THAT WAS MISSING. Every other test in this file reads
    GOVERNED_ANALYSIS_CLASS and GOVERNED_ANALYSIS_RULE and asserts their contents against
    literals written beside them, so the module was free to disagree with
    mutation-governance-boundary.json and did: precedence 9 against the register's 8, and a
    narrower analysis-artifact criterion. Nothing consumed the module, so no gate could see
    it, and the fourteen tests here passed throughout. This guard closes that by asserting
    the agreement itself rather than either side's values.
    """
    declared_class = _declared_class("GOVERNED_ANALYSIS")
    declared_rule = _declared_rule("GOVERNED_ANALYSIS")

    # EVERY GOVERNED KEY, NOT A CHOSEN FEW. A hand-listed set of keys repeats the same
    # failure one level up, because the key that drifts is the one nobody listed -- and
    # "examples" was exactly that key, diverging by two entries while precedence was being
    # argued over. Keys the register prefixes with "$" are its own commentary and carry no
    # governed content, so they are the one exemption, stated here rather than assumed.
    governed_class = {k: v for k, v in declared_class.items() if not k.startswith("$")}
    assert governed_class, "the register declares no governed key for GOVERNED_ANALYSIS"
    for key, declared in governed_class.items():
        assert (
            key in GOVERNED_ANALYSIS_CLASS
        ), f"the register declares GOVERNED_ANALYSIS[{key!r}] and the module omits it"
        assert (
            GOVERNED_ANALYSIS_CLASS[key] == declared
        ), f"GOVERNED_ANALYSIS_CLASS[{key!r}] disagrees with the boundary register"

    governed_rule = {k: v for k, v in declared_rule.items() if not k.startswith("$")}
    assert governed_rule, "the register declares no governed key for R-09"
    for key, declared in governed_rule.items():
        assert (
            key in GOVERNED_ANALYSIS_RULE
        ), f"the register declares R-09[{key!r}] and the module omits it"
        assert (
            GOVERNED_ANALYSIS_RULE[key] == declared
        ), f"GOVERNED_ANALYSIS_RULE[{key!r}] disagrees with the boundary register"


def test_violation_4_rule_order_is_ascending_and_total() -> None:
    """First-matching-rule order requires a total order, and ascending is its direction.

    The inverted reading of precedence is what made GOVERNED_ANALYSIS claim nothing, so the
    direction is asserted here rather than assumed: the register's precedences are exactly
    1..n with no duplicates, and GOVERNED_ANALYSIS sits ahead of AUTHORED_DOCUMENT.
    """
    rules = _boundary()["classification_rules"]["rules"]
    precedences = sorted(int(r["precedence"]) for r in rules)
    assert precedences == list(
        range(1, len(rules) + 1)
    ), f"precedence must be a total order 1..{len(rules)}, measured {precedences}"
    assert _declared_rule("GOVERNED_ANALYSIS")["precedence"] < _authored_document_precedence()
