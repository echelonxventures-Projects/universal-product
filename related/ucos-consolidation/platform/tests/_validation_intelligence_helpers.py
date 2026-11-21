"""UCOS-EPIC-013 — shared fixtures for the Continuous Validation Intelligence suite.

One canonical **all-pass** target plus small, explicit mutators. Every failure test
starts from :func:`passing_facts` and perturbs exactly one dimension, so a test's name
and its single mutation together state the invariant under proof — and a regression in
any other dimension surfaces as a distinct failure rather than being masked.

The facts are pure data (no wall-clock, no ambient state), so a target built here is
byte-identical across processes and the determinism assertions are meaningful.
"""

from __future__ import annotations

from copy import deepcopy
from platform.validation_intelligence.contracts import IntelligenceTarget
from typing import Any

from engine.foundation.contracts.disclosure import build_disclosure


def passing_facts() -> dict[str, dict[str, Any]]:
    """Dimension-keyed facts that satisfy every check in the built-in suite."""
    return {
        "cross_capability_consistency": {
            "capabilities": [
                {"id": "cap-a", "provides": ["contract.x"], "requires": []},
                {"id": "cap-b", "provides": ["contract.y"], "requires": ["contract.x"]},
            ]
        },
        "repository_completeness": {
            "required_artifacts": [
                {"id": "artifact-1", "present": True},
                {"id": "artifact-2", "present": True},
            ],
            "gaps": 0,
            "coverage": {"covered": 12, "total": 12},
        },
        "contract_compatibility": {
            "baseline": [{"name": "c1", "version": "1.0.0", "required_fields": ["a"]}],
            "candidate": [{"name": "c1", "version": "1.1.0", "required_fields": ["a"]}],
        },
        "architecture_compliance": {
            "policies": [{"id": "policy-1", "compliant": True}],
            "changed_paths": ["platform/validation_intelligence/engine.py"],
        },
        "runtime_compatibility": {
            "required": {"interfaces": ["iface.a"], "abi": "1.0.0"},
            "provided": {"interfaces": ["iface.a", "iface.b"], "abi": "1.2.0"},
        },
        "version_compatibility": {
            "components": [
                {"id": "comp-a", "version": "1.2.0", "requires": {"comp-b": "^2.0.0"}},
                {"id": "comp-b", "version": "2.1.0"},
            ]
        },
        "governance_compliance": {
            "controls": [{"id": "control-1", "satisfied": True}],
            "authority": "ENGINEERING-EXECUTION-ONLY",
            "disclosure": build_disclosure(),
        },
    }


def passing_target(target_id: str = "target-pass") -> IntelligenceTarget:
    """The canonical target whose every dimension passes."""
    return IntelligenceTarget(target_id=target_id, facts=passing_facts())


def facts_with(dimension: str, **overrides: Any) -> dict[str, dict[str, Any]]:
    """The all-pass facts with ``dimension``'s entries replaced by ``overrides``."""
    facts = deepcopy(passing_facts())
    facts[dimension].update(overrides)
    return facts


def target_with(dimension: str, *, target_id: str = "target-mutated", **overrides: Any):
    """A target that passes everywhere except ``dimension``, which carries ``overrides``."""
    return IntelligenceTarget(target_id=target_id, facts=facts_with(dimension, **overrides))


def passing_config_mapping(target_id: str = "target-pass") -> dict[str, Any]:
    """A configuration mapping equivalent to :func:`passing_target`."""
    return {"target_id": target_id, "facts": passing_facts()}
