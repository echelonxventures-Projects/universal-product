"""UCOS-UAR-001 Universal Analysis Registry — non-vacuity suite.

A gate with no reachable PASS state carries no evidentiary value, and neither does one
with no reachable FAIL state. This suite proves the analysis registry gate is reachable
in BOTH directions, which is the binding `.github/workflows/uar-gate.yml` asserts and
which `REG-AUTO-001` P7 requires of anything used as enforcement ("enforceability by
tooling gates, not author discipline").

What is proven:

  * the declaration is satisfied on the measured working tree (a reachable PASS state)
  * a duplicate analysis id drives the check FAIL (ids are actually enforced unique)
  * an unresolvable home drives the check FAIL (a home is actually resolved on disk)
  * an empty declaration FAILS CLOSED rather than reporting success over nothing —
    absence of analyses is never evidence of a bound registry
  * determinism: two renders of one declaration are byte-identical
  * zero enumeration: no declared analysis id appears as a literal in the engine source
  * the rendered registry accounts for every declared analysis, so the projection can
    never silently drop one

Every scenario is hermetic: the declaration is deep-copied in memory and the loader is
redirected at it, so nothing writes to the repository and no scenario depends on
untracked local state.
"""

from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
from typing import Any

import pytest

REPO = Path(__file__).resolve().parents[3]
ENGINE = REPO / "00-MASTER" / "UCOS-UAR-001" / "uar_engine.py"


def _load() -> Any:
    spec = importlib.util.spec_from_file_location("uar_engine_under_test", ENGINE)
    assert spec is not None and spec.loader is not None, f"{ENGINE} is not importable"
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def engine() -> Any:
    return _load()


@pytest.fixture
def declaration(engine: Any) -> dict:
    return copy.deepcopy(engine._load_declaration())


def _with(engine: Any, monkeypatch: pytest.MonkeyPatch, decl: dict) -> None:
    """Redirect the engine's loader at an in-memory declaration."""
    monkeypatch.setattr(engine, "_load_declaration", lambda: decl)


# --------------------------------------------------------------- reachable PASS
def test_committed_declaration_satisfies_the_check(engine: Any) -> None:
    """The PASS state is reachable on the repository as committed."""
    assert engine._check_declaration() is True


def test_every_declared_home_resolves(engine: Any, declaration: dict) -> None:
    unresolved = [a["id"] for a in declaration["analyses"] if not (REPO / a["home"]).exists()]
    assert unresolved == [], f"declared homes that no longer resolve: {unresolved}"


# --------------------------------------------------------------- reachable FAIL
def test_duplicate_id_drives_the_check_closed(
    engine: Any, declaration: dict, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Uniqueness is enforced, not assumed."""
    analyses = declaration["analyses"]
    assert len(analyses) >= 2, "the declaration must hold at least two analyses to collide"
    declaration["analyses"] = [*analyses, copy.deepcopy(analyses[0])]
    _with(engine, monkeypatch, declaration)
    assert engine._check_declaration() is False


def test_unresolvable_home_drives_the_check_closed(
    engine: Any, declaration: dict, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A home is resolved against the tree, not merely declared."""
    declaration["analyses"][0]["home"] = "this/path/does/not/exist.py"
    _with(engine, monkeypatch, declaration)
    assert engine._check_declaration() is False


def test_empty_declaration_fails_closed(
    engine: Any, declaration: dict, monkeypatch: pytest.MonkeyPatch
) -> None:
    """No analyses is a fail-closed abort, never a satisfied registry."""
    declaration["analyses"] = []
    _with(engine, monkeypatch, declaration)
    with pytest.raises(SystemExit) as exit_info:
        engine._check_declaration()
    assert exit_info.value.code == 2


# ------------------------------------------------- constitutional self-guards
def test_rendering_is_deterministic(engine: Any) -> None:
    """Two renders of one declaration are byte-identical — no clock, no ordering drift."""
    assert engine._generate() == engine._generate()


def test_no_declared_id_is_hardcoded_in_the_engine(engine: Any, declaration: dict) -> None:
    """Adding an analysis must be an edit to data, never to code."""
    source = ENGINE.read_text(encoding="utf-8")
    leaked = sorted(a["id"] for a in declaration["analyses"] if a["id"] in source)
    assert leaked == [], f"declared ids present as literals in the engine: {leaked}"


def test_projection_accounts_for_every_declared_analysis(engine: Any, declaration: dict) -> None:
    """The registry may not silently drop an analysis it was given."""
    rendered = json.loads(engine._generate())
    assert rendered["total_analyses"] == len(declaration["analyses"])
    counted = sum(rendered["by_kind"].values())
    assert counted == len(
        declaration["analyses"]
    ), "the by-kind projection does not account for every declared analysis"
    assert sum(rendered["by_owner"].values()) == len(
        declaration["analyses"]
    ), "the by-owner projection does not account for every declared analysis"
