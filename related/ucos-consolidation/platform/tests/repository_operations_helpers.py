"""Shared fixtures for the EPIC-PLAT-003 Repository Operations tests (Terminal T5)."""

from __future__ import annotations

from collections.abc import Sequence
from platform.repository_operations.commands import CommandRunner
from typing import Any

from engine.runtime.disclosure import build_disclosure


def constant_runner(code: int) -> CommandRunner:
    """A deterministic in-memory command runner that always returns ``code``."""

    def _run(_argv: Sequence[str]) -> int:
        return code

    return _run


def accepted_facts() -> dict[str, Any]:
    """A repository facts mapping that satisfies every acceptance gate (ACCEPTED)."""
    return {
        "repository_id": "UCOS-CONSOLIDATION",
        "epic_id": "EPIC-PLAT-003",
        "context_assimilated": True,
        "constitution_discovered": True,
        "discovered_repositories": ["UCOS-CONSOLIDATION"],
        "units": [
            {
                "unit_id": "u1",
                "owner": "platform",
                "implemented": True,
                "validated": True,
                "certified": True,
                "registered": True,
                "traceability": [
                    "requirement",
                    "design",
                    "implementation",
                    "test",
                    "certification",
                ],
            }
        ],
        "dependencies": [{"dependency_id": "engine.acceptance", "resolved": True, "pinned": True}],
        "reuse": [{"capability": "verification", "reused": True, "justified": True}],
        "inventory": {
            "expected": ["u1"],
            "present": ["u1"],
            "content_hashes": {"u1": "h1"},
            "responsibilities": {"verify": ["u1"]},
        },
        "coverage": [
            {"name": "statements", "covered": 1, "total": 1},
            {"name": "branches", "covered": 1, "total": 1},
            {"name": "functions", "covered": 1, "total": 1},
            {"name": "public_api", "covered": 1, "total": 1},
            {"name": "exception_paths", "covered": 1, "total": 1},
            {"name": "repository", "covered": 1, "total": 1},
        ],
        "integrations": [{"point": "engine.acceptance", "satisfied": True}],
        "architecture_violations": [],
        "health": {"critical_issues": [], "warnings": []},
        "freeze_blockers": [],
    }


def rejected_facts() -> dict[str, Any]:
    """A minimal facts mapping that is REJECTED (missing every satisfied dimension)."""
    return {"repository_id": "R", "epic_id": "E"}


def acceptance_stage(stage_id: str = "acceptance") -> dict[str, Any]:
    """A stage declaration running the acceptance engine over fully-accepted facts."""
    return {"stage_id": stage_id, "kind": "acceptance", "params": {"facts": accepted_facts()}}


def valid_validation_subject() -> dict[str, Any]:
    """A validation subject facts mapping that passes every check (verdict PASS)."""
    return {
        "target_id": "T-1",
        "blueprint_id": "BP-1",
        "provenance_chain": ["BP-1", "gen"],
        "signature": {"algorithm": "ed25519", "value": "sig", "payload_sha256": "abc"},
        "sbom": {"sbom_format": "cyclonedx-1.5", "components": [{"name": "c"}]},
        "dependency_closure": [
            {"role": "root", "blueprint_id": "BP-1", "package_sha256": "deadbeef"}
        ],
        "disclosure": build_disclosure(),
        "package_sha256": "deadbeef",
        "image_reference": "registry/img@sha256:deadbeef",
        "runtime_id": "UCOS-RUN-BP-1-0123456789abcdef",
        "blueprint_class": "service",
    }


def invalid_validation_subject() -> dict[str, Any]:
    """A validation subject that fails a blocking check (no signature → verdict FAIL)."""
    subject = valid_validation_subject()
    subject["signature"] = {}
    return subject


#: A minimal, well-formed Cobertura coverage document (100% line + branch).
COVERAGE_XML_FULL = (
    '<?xml version="1.0" ?>\n'
    '<coverage line-rate="1.0" branch-rate="1.0" lines-covered="10" lines-valid="10" '
    'branches-covered="4" branches-valid="4" version="7.15.2"></coverage>\n'
)

#: A well-formed Cobertura document below a 90% line threshold.
COVERAGE_XML_LOW = (
    '<coverage line-rate="0.5" branch-rate="0.4" lines-covered="5" lines-valid="10" '
    'branches-covered="2" branches-valid="5"></coverage>\n'
)


__all__ = [
    "constant_runner",
    "accepted_facts",
    "rejected_facts",
    "acceptance_stage",
    "valid_validation_subject",
    "invalid_validation_subject",
    "COVERAGE_XML_FULL",
    "COVERAGE_XML_LOW",
]
