"""Fixtures for the Repository Governance Pipeline test suite (EPIC-VAL-003).

Drives the pipeline end to end against a **genuine** artifact: it assembles a real
runtime unit from a published compiler package (reusing the root ``published_package``
+ ``runtime_signer`` fixtures) and projects it into a Validation Subject, so the
pipeline is exercised over real validation → certification → acceptance output, never
a hand-built stand-in. The golden governance input is fully governable so negative
tests can mutate a single dimension and assert the fail-closed refusal it triggers.
"""

from __future__ import annotations

import dataclasses

import pytest

from engine.governance.contracts import GovernanceInput, GovernanceUnit
from engine.governance.pipeline import RepositoryGovernancePipeline
from engine.runtime import assemble
from engine.validation.contracts import ValidationSubject

_TRACE = ("requirement", "design", "implementation", "test", "certification")


@pytest.fixture
def runtime_unit(published_package, runtime_signer):
    return assemble(published_package, verify_with=runtime_signer)


@pytest.fixture
def valid_subject(runtime_unit) -> ValidationSubject:
    return ValidationSubject.from_runtime_unit(runtime_unit, blueprint_class="BP-DATA")


@pytest.fixture
def governance_units(valid_subject) -> tuple[GovernanceUnit, ...]:
    """Two governable units sharing the genuine validation subject."""
    return (
        GovernanceUnit(
            unit_id="UNIT-A",
            subject=valid_subject,
            version="1.0.0",
            owner="UCOS-PROGRAM-CUSTODIAN",
            registered=True,
            traceability=_TRACE,
        ),
        GovernanceUnit(
            unit_id="UNIT-B",
            subject=valid_subject,
            version="1.0.0",
            owner="UCOS-PROGRAM-CUSTODIAN",
            registered=True,
            traceability=_TRACE,
        ),
    )


@pytest.fixture
def repository_facts() -> dict:
    """Repository-level acceptance facts over which every gate passes (units derived)."""
    return {
        "context_assimilated": True,
        "constitution_discovered": True,
        "discovered_repositories": ["UCOS-REPO-0003"],
        "dependencies": [
            {"dependency_id": "DEP-1", "resolved": True, "pinned": True},
        ],
        "reuse": [
            {"capability": "validation", "reused": True, "justified": False},
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
            {"point": "EPIC-008->EPIC-VAL-003", "satisfied": True},
        ],
        "architecture_violations": [],
        "health": {"critical_issues": [], "warnings": ["stale-branch"]},
        "freeze_blockers": [],
    }


@pytest.fixture
def valid_input(governance_units, repository_facts) -> GovernanceInput:
    return GovernanceInput(
        repository_id="UCOS-REPO-0003",
        epic_id="EPIC-VAL-003",
        units=governance_units,
        repository_facts=repository_facts,
    )


@pytest.fixture
def governed_report(valid_input):
    return RepositoryGovernancePipeline().govern(valid_input)


def replace_facts(facts: dict, **changes) -> dict:
    """Return a copy of the repository facts mapping with keys replaced."""
    merged = dict(facts)
    merged.update(changes)
    return merged


def mutate(obj, **changes):
    """Return a copy of a frozen dataclass with fields replaced (negative tests)."""
    return dataclasses.replace(obj, **changes)
