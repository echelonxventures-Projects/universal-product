"""Shared fixtures for the `platform.universal_assurance` suite (UCOS-EPIC-014).

The cluster is policy-driven end to end, so almost every test needs a *declared*
policy document rather than a constructed object. :func:`policy_mapping` builds the
smallest document that still exercises every section — identity, obligations across
all four :class:`ObligationKind` values, gates, metrics, evidence artifacts, bindings
and reproducibility — and :func:`make_policy` assimilates it.

Nothing here re-implements the package's own vocabulary: rule refs come from the
reused ``platform.universal_validation.rules`` catalogue and dimension refs from the
reused ``platform.validation_intelligence`` enum, so a fixture can never drift into
asserting against refs the platform does not actually ship.
"""

from __future__ import annotations

from platform.universal_assurance.contracts import AssuranceSubject
from platform.universal_assurance.policy import AssurancePolicy, parse_policy
from typing import Any

#: A rule the reused validation catalogue really ships (blocking, architecture domain).
REAL_RULE_REF = "architecture.layers-declared"
#: A second real rule, advisory in the reused implementation — used to prove that the
#: *policy's* severity governs where the two disagree.
REAL_ADVISORY_RULE_REF = "implementation.no-open-markers"
#: A dimension the reused intelligence engine really analyzes.
REAL_DIMENSION_REF = "architecture_compliance"
#: A certification rule and compliance frame the reused certifier really ships.
#: Guarded by ``test_every_fixture_ref_resolves_in_the_reused_catalogues`` — a ref that
#: silently stops resolving would leave the pipeline unbound and quietly turn the
#: certification tests into no-ops rather than failing them.
REAL_CRITERION_REF = "validation-complete"
REAL_FRAME_REF = "validation-conformance"


def policy_mapping(**overrides: Any) -> dict[str, Any]:
    """The smallest policy document that still touches every declared section."""
    document: dict[str, Any] = {
        "policy": {
            "id": "TEST-POLICY-001",
            "name": "Test Assurance Policy",
            "version": "1.0.0",
            "authority": "ENGINEERING-EXECUTION-ONLY",
            "fail_closed": True,
            "description": "a fixture policy",
        },
        "obligations": [
            {
                "id": "OB-RULE",
                "stage": "validation-execution",
                "kind": "validation-rule",
                "ref": REAL_RULE_REF,
                "severity": "blocking",
                "requires_facts": ["validation.architecture"],
                "rationale": "the architecture must declare its layers",
            },
            {
                "id": "OB-DIM",
                "stage": "validation-intelligence",
                "kind": "intelligence-dimension",
                "ref": REAL_DIMENSION_REF,
                "severity": "blocking",
                "requires_facts": ["intelligence.architecture_compliance"],
            },
            {
                "id": "OB-CRIT",
                "stage": "certification-execution",
                "kind": "certification-criterion",
                "ref": REAL_CRITERION_REF,
                "severity": "blocking",
                "requires_facts": ["repository_truth"],
            },
            {
                "id": "OB-FRAME",
                "stage": "certification-execution",
                "kind": "certification-frame",
                "ref": REAL_FRAME_REF,
                "severity": "advisory",
                "requires_facts": ["repository_truth"],
            },
        ],
        "gates": [
            {
                "id": "G-VALIDATION",
                "name": "validation gate",
                "stages": ["validation-execution"],
                "obligations": ["OB-RULE"],
            },
            {
                "id": "G-CERTIFICATION",
                "name": "certification gate",
                "stages": ["certification-execution"],
                "obligations": ["OB-CRIT", "OB-FRAME"],
            },
        ],
        "metrics": [
            {
                "id": "M-EXEC",
                "stage": "validation-execution",
                "observation": "execution.blocking_failures",
                "comparator": "le",
                "threshold": 0,
                "severity": "blocking",
                "unit": "count",
            },
            {
                "id": "M-COVERAGE",
                "stage": "validation-execution",
                "observation": "subject.coverage_line_percent",
                "comparator": "ge",
                "threshold": 90,
                "severity": "advisory",
                "unit": "percent",
            },
        ],
        "evidence": {
            "artifacts": [
                {
                    "id": "EV-PLAN",
                    "stage": "validation-planning",
                    "name": "validation-plan",
                    "required": True,
                },
                {
                    "id": "EV-OPTIONAL",
                    "stage": "evidence-collection",
                    "name": "optional-note",
                    "required": False,
                },
            ],
            "forbidden_write_prefixes": ["99-FREEZE", "00-BOOK"],
        },
        "bindings": {
            "registry_id": "TEST-REGISTRY",
            "certification_class": "universal-readiness",
            "measurement_source": "test-suite",
            "submitter": "test-runner",
            "disclosure_rule": "runtime.disclosure-present",
            "disclosure_check_id": "ec1-disclosure",
            "evidence_root": ".runtime/test-evidence",
        },
        "reproducibility": {"replays": 2, "byte_identical_required": True},
    }
    document.update(overrides)
    return document


def make_policy(**overrides: Any) -> AssurancePolicy:
    """Assimilate the fixture policy document."""
    return parse_policy(policy_mapping(**overrides))


def subject_mapping(**overrides: Any) -> dict[str, Any]:
    """A subject supplying facts for every address the fixture policy references."""
    document: dict[str, Any] = {
        "subject_id": "TEST-SUBJECT",
        "version": "1.0.0",
        "blueprint_id": "TEST-BLUEPRINT",
        "validation_facts": {
            "architecture": {
                "layers": ["platform", "engine"],
                "dependencies": [{"from": "platform", "to": "engine"}],
                "changed_paths": ["platform/universal_assurance/planning.py"],
            },
        },
        # The reused architecture-compliance analyzer requires declared policies and a
        # changed-path set; supplying them makes the planned dimension genuinely clean
        # rather than passing by accident on an unanalyzable fact block.
        "intelligence_facts": {
            "architecture_compliance": {
                "layers": ["platform", "engine"],
                "policies": [{"id": "AP-001", "compliant": True}],
                "changed_paths": ["platform/universal_assurance/planning.py"],
            },
        },
        "repository_truth": {
            "snapshot_id": "SNAP-001",
            "content_sha256": "a" * 64,
            "total_concepts": 10,
            "homed_concepts": 10,
            "gaps": {},
            "closed": True,
        },
        "observations": {"coverage_line_percent": 95.0},
    }
    document.update(overrides)
    return document


def make_subject(**overrides: Any) -> AssuranceSubject:
    """Assimilate the fixture subject."""
    return AssuranceSubject.from_mapping(subject_mapping(**overrides))


def factless_subject() -> AssuranceSubject:
    """A subject that supplies no facts at all — every obligation is undecidable."""
    return AssuranceSubject.from_mapping({"subject_id": "EMPTY-SUBJECT", "version": "1.0.0"})
