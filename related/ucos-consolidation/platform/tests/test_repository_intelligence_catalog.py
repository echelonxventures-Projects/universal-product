"""Ω-E06 W3-2 — what "phantom" is allowed to mean.

Stage-1 C-02 recorded four phantom catalog capabilities (``engine``, ``engine.tests``,
``platform``, ``platform.tests``) with disposition CONSOLIDATE; the live measurement had
grown to thirty-seven. Not one of them was absent. Every claimed location existed and held
tracked modules.

The rule compared catalog names against ``implementation_capabilities`` — a set that
deliberately drops the bare code roots and the test packages, and whose own docstring says
including them "would manufacture false catalog omissions". The exclusion was applied in
one direction only: it suppressed false *omissions* while manufacturing false *phantoms*
out of the very same entries. The remaining thirty-three were nested sub-packages, which
the catalog names at their real depth and which ``_capability_name`` attributes to a
depth-1 owner.

Neither producer was wrong. The catalog is authoritative for capability identity — the
discovery module states twice that it never re-derives it — and the capability model is a
derived, deliberately narrower view. What was wrong was asking one question and reading
the other's answer.

A phantom is a catalog entry whose declared ``canonical_location`` is not in the
substrate. Nothing else. This suite pins that, and pins that a real location at a
granularity the model does not carry is reported as an advisory rather than silently
dropped.
"""

from __future__ import annotations

from pathlib import Path
from platform.repository_intelligence.config import RepositoryIntelligenceConfig
from platform.repository_intelligence.discovery import (
    CATALOG_GRANULARITY,
    CATALOG_PHANTOM,
    discover_capabilities,
    discover_conflicts,
)
from platform.repository_intelligence.substrate import (
    Declarations,
    ModuleFact,
    RepositorySubstrate,
)

import pytest

CATALOG_SOURCE = "test-catalog"


def module(path: str, capability: str, *, is_test: bool = False) -> ModuleFact:
    dotted = path[: -len(".py")].replace("/", ".").removesuffix(".__init__")
    return ModuleFact(
        module=dotted,
        capability=capability,
        root=path.split("/", 1)[0],
        path=path,
        loc=10,
        content_sha256="0" * 64,
        docline="A capability.",
        is_test=is_test,
    )


def entry(name: str, location: str, category: str = "engine") -> dict[str, object]:
    return {
        "canonical_name": name,
        "canonical_location": location,
        "category": category,
        "authority": "TEST",
        "reuse": "REUSE/EXTEND",
        "replacement_prohibited": False,
        "implementation_status": "IMPLEMENTED",
        "description": "d",
        "evidence_present": True,
    }


def substrate_with(modules: tuple[ModuleFact, ...], catalog: tuple[dict, ...]):
    config = RepositoryIntelligenceConfig(
        repository_root=Path("/nonexistent"),
        repository_id="TEST",
        _validated=True,
    )
    return RepositorySubstrate(
        config=config,
        modules=modules,
        zones={},
        declarations=Declarations(),
        catalog=catalog,
        catalog_source=CATALOG_SOURCE,
    )


def codes(findings, code: str) -> list[str]:
    return sorted(f.subject for f in findings if f.code == code)


# ---------------------------------------------------------------- location_is_populated
class TestLocationIsPopulated:
    def test_a_location_holding_a_tracked_module_is_populated(self) -> None:
        sub = substrate_with(
            (module("engine/foundation/config/__init__.py", "engine.foundation"),), ()
        )
        assert sub.location_is_populated("engine/foundation/config")

    def test_a_location_with_no_tracked_module_is_not_populated(self) -> None:
        sub = substrate_with((module("engine/foundation/__init__.py", "engine.foundation"),), ())
        assert not sub.location_is_populated("engine/absent")

    def test_an_exact_module_path_counts(self) -> None:
        sub = substrate_with((module("engine/foundation/config.py", "engine.foundation"),), ())
        assert sub.location_is_populated("engine/foundation/config.py")

    def test_a_prefix_that_is_not_a_path_segment_does_not_count(self) -> None:
        """``engine/found`` must not match ``engine/foundation`` — that would make any
        truncation of a real path look populated."""
        sub = substrate_with((module("engine/foundation/__init__.py", "engine.foundation"),), ())
        assert not sub.location_is_populated("engine/found")

    @pytest.mark.parametrize("blank", ["", "   ", "/"])
    def test_an_empty_location_is_never_populated(self, blank: str) -> None:
        """A catalog entry that declares no location cannot be proven present, so it must
        stay a phantom rather than pass vacuously."""
        sub = substrate_with((module("engine/foundation/__init__.py", "engine.foundation"),), ())
        assert not sub.location_is_populated(blank)

    def test_surrounding_slashes_are_tolerated(self) -> None:
        sub = substrate_with((module("engine/foundation/__init__.py", "engine.foundation"),), ())
        assert sub.location_is_populated("/engine/foundation/")


# ------------------------------------------------------------------- the phantom verdict
class TestPhantomVerdict:
    def test_an_absent_location_is_still_a_phantom(self) -> None:
        """The fail-closed case must survive the reconciliation.

        ``discover_capabilities`` marks the record ``present_on_disk=False``;
        ``discover_conflicts`` is what turns that into the blocking CATALOG_PHANTOM
        finding, so this asserts the record and the absence of an excuse for it.
        """
        sub = substrate_with(
            (module("engine/foundation/__init__.py", "engine.foundation"),),
            (entry("engine.ghost", "engine/ghost"),),
        )
        records, result = discover_capabilities(sub)
        ghost = [r for r in records if r.name == "engine.ghost"]
        assert ghost, "a catalog entry with no location in the substrate must be recorded"
        assert ghost[0].present_on_disk is False
        assert "engine.ghost" not in codes(result.findings, CATALOG_GRANULARITY)

    def test_the_phantom_record_reaches_the_blocking_conflict(self) -> None:
        """End-to-end: an absent location must still close the gate."""
        sub = substrate_with(
            (module("engine/foundation/__init__.py", "engine.foundation"),),
            (entry("engine.ghost", "engine/ghost"),),
        )
        records, _ = discover_capabilities(sub)
        conflicts = discover_conflicts(sub, records, ())
        assert "engine.ghost" in codes(conflicts.findings, CATALOG_PHANTOM)
        assert any(f.is_blocking_failure for f in conflicts.findings if f.code == CATALOG_PHANTOM)

    def test_a_nested_subpackage_is_not_a_phantom(self) -> None:
        """The 33-entry majority: the catalog names a real package at a depth the
        capability model attributes to its parent."""
        sub = substrate_with(
            (
                module("engine/foundation/__init__.py", "engine.foundation"),
                module("engine/foundation/config/__init__.py", "engine.foundation"),
            ),
            (entry("engine.foundation.config", "engine/foundation/config"),),
        )
        records, result = discover_capabilities(sub)
        assert not [r for r in records if r.name == "engine.foundation.config"]
        assert "engine.foundation.config" in codes(result.findings, CATALOG_GRANULARITY)

    def test_a_test_package_is_not_a_phantom(self) -> None:
        """Two of Stage-1's original four. ``implementation_capabilities`` drops test
        packages so they cannot be false omissions; they must not become false phantoms."""
        sub = substrate_with(
            (
                module("engine/foundation/__init__.py", "engine.foundation"),
                module("engine/tests/unit/test_x.py", "engine.tests", is_test=True),
            ),
            (entry("engine.tests", "engine/tests"),),
        )
        records, result = discover_capabilities(sub)
        assert not [r for r in records if r.name == "engine.tests"]
        assert "engine.tests" in codes(result.findings, CATALOG_GRANULARITY)

    def test_a_bare_code_root_is_not_a_phantom(self) -> None:
        """The other two of Stage-1's original four."""
        sub = substrate_with(
            (module("engine/foundation/__init__.py", "engine.foundation"),),
            (entry("engine", "engine"),),
        )
        records, result = discover_capabilities(sub)
        assert not [r for r in records if r.name == "engine"]
        assert "engine" in codes(result.findings, CATALOG_GRANULARITY)

    def test_a_granularity_advisory_never_blocks(self) -> None:
        """The divergence is real and stays reported — but it is not a contradiction, so
        it must not close the gate."""
        sub = substrate_with(
            (
                module("engine/foundation/__init__.py", "engine.foundation"),
                module("engine/foundation/config/__init__.py", "engine.foundation"),
            ),
            (entry("engine.foundation.config", "engine/foundation/config"),),
        )
        _, result = discover_capabilities(sub)
        granularity = [f for f in result.findings if f.code == CATALOG_GRANULARITY]
        assert granularity
        assert not any(f.is_blocking_failure for f in granularity)

    def test_an_entry_outside_the_code_roots_is_ignored_entirely(self) -> None:
        sub = substrate_with(
            (module("engine/foundation/__init__.py", "engine.foundation"),),
            (entry("data.warehouse", "data/warehouse", category="data"),),
        )
        records, result = discover_capabilities(sub)
        assert not [r for r in records if r.name == "data.warehouse"]
        assert "data.warehouse" not in codes(result.findings, CATALOG_GRANULARITY)
