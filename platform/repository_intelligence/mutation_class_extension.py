"""REQ-VIOLATION-4: Mutation Classification Extensibility Implementation.

This module implements Violation 4 resolution: Add GOVERNED_ANALYSIS as the 9th
mutation class and implement extensibility mechanism for future classes.

Current state: 8 mutation classes (CONSTITUTIONAL_TRUTH through AUTHORED_DOCUMENT)
Target state: 9 classes + dynamic extension capability

Authority: Violation 4, MASTER-EXECUTION-ADMISSION-MATRIX.md, Phase 1B authorization
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

# Violation 4 Resolution: Add GOVERNED_ANALYSIS as 9th mutation class
GOVERNED_ANALYSIS_CLASS = {
    "class": "GOVERNED_ANALYSIS",
    "examples": [
        "*-DETERMINATION.md",
        "*-DETERMINATION-REPORT.md",
        "*-ANALYSIS.md",
        "*-ASSESSMENT-DETERMINATION.md",
        "PHASE-*-EXECUTION-COMPLETION-REPORT.md",
        "MASTER-EXECUTION-ADMISSION-MATRIX.md",
        "BLOCKER-ELIMINATION-DETERMINATION.md",
        "100-PERCENT-IMPLEMENTATION-READINESS-CERTIFICATION.md",
    ],
    "governed_by": (
        "the authority the analysis declares of itself (owner-parameterised, "
        "read from Authority field) → Repository Intelligence → verify.sh "
        "(observation only)"
    ),
    "membership_criteria": [
        "markdown — the path ends .md",
        "authored — absent from producer_homes",
        "repository-controlled — tracked by version control",
        "non-generated — absent from generated-artifact-registry.json canonical_path",
        (
            "analysis-artifact — carries determination/analysis/assessment/execution/"
            "matrix/readiness/admission/blocker/gap in filename"
        ),
        "self-declared-authority — carries Authority field in opening metadata block",
    ],
    "grants_only_mutation_ownership": (
        "Class 8 defines WHO MAY MUTATE a governed analysis artifact and nothing else. "
        "It grants no certification authority, no ratification authority and no freeze authority. "
        "Certification remains with the existing chain."
    ),
    "does_not_govern": [
        "certification, ratification or freeze of the artifact",
        "verify.sh, which observes an analysis and may never author one",
        "artifacts that are generated, which remain GENERATED_ARTIFACT",
    ],
    "$why_this_class_was_added": (
        "Phase 1B Violation 4 resolution. Determination, analysis, and assessment artifacts "
        "are a distinct class from AUTHORED_DOCUMENT (which covers ADRs, constitutions, "
        "general documentation). Analysis artifacts follow specific governance patterns: "
        "they document findings, they reference evidence, they have determinations, and they "
        "are often superseded by newer analyses. Separating them into GOVERNED_ANALYSIS "
        "provides explicit governance for analytical work products."
    ),
}

GOVERNED_ANALYSIS_RULE = {
    # PRECEDENCE IS ASCENDING, AND THAT IS WHY THIS IS 8 AND NOT 9. The boundary register
    # declares first-matching-rule order over precedence 1..9, so a LOWER number is
    # evaluated EARLIER. GOVERNED_ANALYSIS must be decided before AUTHORED_DOCUMENT or
    # every determination is swallowed by R-08 first -- the measured form of that error was
    # GOVERNED_ANALYSIS claiming 0 of 6751 tracked paths. At 8, ahead of R-08's 9, it claims
    # 209 of 7165. The register at 00-BOOK/DATA/mutation-governance-boundary.json is the
    # source of truth for both values below; this module must never disagree with it.
    "precedence": 8,
    "id": "R-09",
    "class": "GOVERNED_ANALYSIS",
    "predicate": (
        "subject is a tracked, non-generated markdown path with "
        "(determination|analysis|assessment|execution|matrix|readiness|admission|blocker|gap) "
        "in the filename, satisfying the six membership_criteria declared on GOVERNED_ANALYSIS"
    ),
}


def extend_mutation_governance_boundary(
    boundary_path: str | Path = "00-BOOK/DATA/mutation-governance-boundary.json",
    *,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Extend mutation governance boundary with GOVERNED_ANALYSIS class.

    Args:
        boundary_path: Path to mutation-governance-boundary.json
        dry_run: If True, return extended document without writing

    Returns:
        Extended boundary document

    Raises:
        FileNotFoundError: boundary file not found
        json.JSONDecodeError: boundary file invalid JSON
        ValueError: GOVERNED_ANALYSIS already exists
    """
    boundary_path = Path(boundary_path)

    # Load existing boundary
    if not boundary_path.exists():
        raise FileNotFoundError(f"Mutation governance boundary not found: {boundary_path}")

    with boundary_path.open("r", encoding="utf-8") as f:
        boundary = json.load(f)

    # Validate: GOVERNED_ANALYSIS not already present
    existing_classes = {cls["class"] for cls in boundary.get("mutation_classes", [])}
    if "GOVERNED_ANALYSIS" in existing_classes:
        raise ValueError("GOVERNED_ANALYSIS already exists in mutation_classes")

    existing_rules = {
        rule["id"] for rule in boundary.get("classification_rules", {}).get("rules", [])
    }
    if "R-09" in existing_rules:
        raise ValueError("R-09 already exists in classification_rules")

    # Extend: Add GOVERNED_ANALYSIS class
    boundary.setdefault("mutation_classes", []).append(GOVERNED_ANALYSIS_CLASS)

    # Extend: Add R-09 rule
    boundary.setdefault("classification_rules", {}).setdefault("rules", []).append(
        GOVERNED_ANALYSIS_RULE
    )

    # Update: Increment version
    current_version = boundary.get("version", "1.0.0")
    major, minor, patch = map(int, current_version.split("."))
    boundary["version"] = f"{major}.{minor + 1}.{patch}"  # minor bump for new class

    # Write: Extended boundary (unless dry_run)
    if not dry_run:
        with boundary_path.open("w", encoding="utf-8") as f:
            json.dump(boundary, f, indent=2, ensure_ascii=False)
            f.write("\n")  # trailing newline

    return boundary


def add_dynamic_class_extension_mechanism() -> dict[str, Any]:
    """Define dynamic class extension mechanism for future mutation classes.

    Returns specification for future class registration without code modification.

    This is a SPECIFICATION, not an implementation. Implementation would require:
    1. Extension registry (00-BOOK/DATA/mutation-class-extensions.json)
    2. Loader in mutation_classification.py to merge extensions
    3. Validation: extension predicates implementable, no duplicate classes
    4. Authority validation: every extension names governing authority

    For Phase 1B: Document the extension pattern, defer implementation to Phase 3-4.
    """
    return {
        "extension_mechanism": "DYNAMIC_CLASS_REGISTRATION",
        "status": "SPECIFIED (implementation deferred to Phase 3-4)",
        "specification": {
            "extension_registry": "00-BOOK/DATA/mutation-class-extensions.json",
            "schema": {
                "extension_id": "string (unique identifier)",
                "class": "string (mutation class name, must be unique)",
                "governed_by": "string (authority chain)",
                "membership_criteria": "array[string] (predicates)",
                "examples": "array[string] (example paths)",
                "predicate": "string (decidable from repository state)",
                "precedence": (
                    "integer, ascending = evaluated earlier (first-matching-rule order). "
                    "A class that must be decided before an existing one takes a LOWER "
                    "number than it, not a higher one"
                ),
                "rule_id": "string (R-10, R-11, ...)",
            },
            "loader": {
                "location": "platform/repository_intelligence/mutation_classification.py",
                "function": "load_extensions() -> list[ExtensionClass]",
                "merge_strategy": "append extensions after declared classes, validate uniqueness",
            },
            "validation": {
                "no_duplicate_classes": "extension class name must not exist in base classes",
                "no_duplicate_rule_ids": "extension rule ID must not exist in base rules",
                "authority_required": "every extension must name governing authority",
                "predicate_implementable": (
                    "extension predicates must be decidable from repository state"
                ),
            },
        },
        "example_extension": {
            "extension_id": "MUTATION-EXT-001",
            "class": "HYPOTHETICAL_CLASS",
            "governed_by": "Future Authority Chain",
            "membership_criteria": ["criteria 1", "criteria 2"],
            "examples": ["example/path/*.ext"],
            "predicate": "subject matches hypothetical pattern",
            "precedence": 10,
            "rule_id": "R-10",
        },
        "phase_3_4_implementation": [
            "Create extension registry (00-BOOK/DATA/mutation-class-extensions.json)",
            "Implement load_extensions() in mutation_classification.py",
            "Implement merge_classes() to combine base + extensions",
            "Add validation: uniqueness, authority, predicate decidability",
            "Add tests: extension loading, validation, classification with extensions",
            "Document extension process in mutation governance documentation",
        ],
    }


__all__ = [
    "GOVERNED_ANALYSIS_CLASS",
    "GOVERNED_ANALYSIS_RULE",
    "extend_mutation_governance_boundary",
    "add_dynamic_class_extension_mechanism",
]
