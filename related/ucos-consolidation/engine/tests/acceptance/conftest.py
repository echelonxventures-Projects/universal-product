"""Fixtures for the Repository Acceptance Engine test suite.

Builds a fully-acceptable repository facts mapping and its assimilated
:class:`RepositorySubject` — the golden subject over which every built-in gate
passes — so negative tests can mutate a single dimension and assert the fail-closed
rejection it triggers.
"""

from __future__ import annotations

import dataclasses

import pytest

from engine.acceptance.contracts import RepositorySubject
from engine.acceptance.engine import AcceptanceEngine


@pytest.fixture
def acceptable_facts() -> dict:
    """A repository facts mapping over which every built-in acceptance gate passes."""
    trace = ["requirement", "design", "implementation", "test", "certification"]
    return {
        "repository_id": "UCOS-REPO-0001",
        "epic_id": "EPIC-VAL-002",
        "context_assimilated": True,
        "constitution_discovered": True,
        "discovered_repositories": ["UCOS-REPO-0001"],
        "units": [
            {
                "unit_id": "UNIT-A",
                "owner": "UCOS-PROGRAM-CUSTODIAN",
                "implemented": True,
                "validated": True,
                "certified": True,
                "registered": True,
                "traceability": trace,
            },
            {
                "unit_id": "UNIT-B",
                "owner": "UCOS-PROGRAM-CUSTODIAN",
                "implemented": True,
                "validated": True,
                "certified": True,
                "registered": True,
                "traceability": trace,
            },
        ],
        "dependencies": [
            {"dependency_id": "DEP-1", "resolved": True, "pinned": True},
        ],
        "reuse": [
            {"capability": "hashing", "reused": True, "justified": False},
            {"capability": "bespoke", "reused": False, "justified": True},
        ],
        "inventory": {
            "expected": ["UNIT-A", "UNIT-B"],
            "present": ["UNIT-A", "UNIT-B"],
            "content_hashes": {"UNIT-A": "aa", "UNIT-B": "bb"},
            "responsibilities": {"persist": ["UNIT-A"], "serve": ["UNIT-B"]},
        },
        "coverage": [
            {"name": "statements", "covered": 100, "total": 100},
            {"name": "branches", "covered": 40, "total": 40},
            {"name": "functions", "covered": 20, "total": 20},
            {"name": "public_api", "covered": 10, "total": 10},
            {"name": "exception_paths", "covered": 5, "total": 5},
            {"name": "repository", "covered": 2, "total": 2},
        ],
        "integrations": [
            {"point": "EPIC-007->EPIC-VAL-002", "satisfied": True},
        ],
        "architecture_violations": [],
        "health": {"critical_issues": [], "warnings": ["stale-branch"]},
        "freeze_blockers": [],
    }


@pytest.fixture
def valid_subject(acceptable_facts) -> RepositorySubject:
    return RepositorySubject.from_mapping(acceptable_facts)


@pytest.fixture
def accepted_decision(valid_subject):
    return AcceptanceEngine().accept(valid_subject)


def mutate(subject: RepositorySubject, **changes) -> RepositorySubject:
    """Return a copy of ``subject`` with fields replaced (for negative tests)."""
    return dataclasses.replace(subject, **changes)
