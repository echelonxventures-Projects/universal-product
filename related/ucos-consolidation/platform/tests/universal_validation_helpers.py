"""UCOS-EPIC-005 — shared test fixtures for the Universal Validation Engine (Terminal T5)."""

from __future__ import annotations

from platform.universal_validation.contracts import ValidationTarget
from typing import Any

from engine.runtime.disclosure import build_disclosure

#: A deterministic package hash used to digest-pin the runtime image fixture.
PACKAGE_SHA256 = "a" * 64


def passing_facts() -> dict[str, dict[str, Any]]:
    """Return domain-keyed facts that satisfy every built-in rule (all-PASS)."""
    return {
        "architecture": {
            "layers": ["application", "service", "data"],
            "dependencies": [
                {"from": "application", "to": "service"},
                {"from": "service", "to": "data"},
            ],
            "changed_paths": ["platform/universal_validation/engine.py"],
        },
        "implementation": {
            "modules": [
                {"id": "engine", "present": True},
                {"id": "rules", "present": True},
            ],
            "entrypoints": [{"name": "ucos-validate", "resolved": True}],
            "open_markers": 0,
        },
        "dependency": {
            "dependencies": [
                {"id": "foundation", "version": "1.0.0", "provider": "ec1"},
            ],
            "providers": ["ec1"],
            "edges": [{"from": "foundation", "to": "obs"}],
        },
        "registry": {
            "entries": [
                {"id": "bp-1", "kind": "blueprint", "content_hash": "h1"},
                {"id": "bp-2", "kind": "blueprint", "content_hash": "h2"},
            ],
            "references": [{"from": "bp-2", "to": "bp-1"}],
        },
        "schema": {
            "schemas": {"unit": {"version": "1.0.0", "required": ["id", "kind"]}},
            "records": [{"schema": "unit", "fields": {"id": "x", "kind": "blueprint"}}],
        },
        "runtime": {
            "disclosure": build_disclosure(),
            "units": [
                {
                    "runtime_id": "UCOS-RUN-bp1-0123456789abcdef",
                    "image_reference": f"registry.example/img@sha256:{PACKAGE_SHA256}",
                    "package_sha256": PACKAGE_SHA256,
                }
            ],
        },
        "quality": {
            "line_percent": 99.86,
            "min_percent": 90.0,
            "tests": {"passed": 1575, "failed": 0},
            "lint_violations": 0,
        },
    }


def passing_target(target_id: str = "UCOS-EPIC-005") -> ValidationTarget:
    """A validation target whose facts satisfy every built-in rule."""
    return ValidationTarget(target_id=target_id, facts=passing_facts())
