"""EC2-EPIC-006 — blueprint governance / reuse / boundary tests.

Asserts the additive, authority-neutral discipline: no new authority or capability
group is introduced (the two blueprint groups pre-exist in the certified Identity
Layer); the EC-1 engine is consumed only by contract reference (read-only, no live
call, no engine import); classification is recorded, never computed; and the runtime
writes nothing to the certified corpus.
"""

from __future__ import annotations

import ast
from pathlib import Path
from platform.blueprints.classification import CLASSIFICATION_CONTRACTS
from platform.blueprints.contracts import (
    BLUEPRINT_AUTHORING_GROUP,
    BLUEPRINT_CATALOG_GROUP,
)
from platform.foundation.contracts import ENGINE_CONTRACTS
from platform.identity.contracts import CapabilityGroup

_PKG = Path(__file__).resolve().parents[1] / "blueprints"


def test_reuses_existing_capability_groups_no_new_authority():
    # The two blueprint groups are the pre-existing §3.2 Identity groups (no new group).
    assert BLUEPRINT_AUTHORING_GROUP is CapabilityGroup.BLUEPRINT_AUTHORING
    assert BLUEPRINT_CATALOG_GROUP is CapabilityGroup.BLUEPRINT_CATALOG


def test_classification_binds_certified_engine_contracts_read_only():
    engine_names = {ref.name for ref in ENGINE_CONTRACTS}
    for ref in CLASSIFICATION_CONTRACTS:
        assert ref.name in engine_names  # bound by reference to the certified set
    assert {r.name for r in CLASSIFICATION_CONTRACTS} == {
        "engine.registry.read",
        "engine.compiler.compile",
    }


def _iter_source_files():
    return sorted(p for p in _PKG.glob("*.py"))


def test_runtime_never_imports_engine_modules_directly():
    # Additive over EC-1 (P10): the platform binds the engine by ContractRef only; it
    # must not import any engine.* module at runtime (mirrors the projects discipline).
    for path in _iter_source_files():
        tree = ast.parse(path.read_text(), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert not alias.name.startswith("engine."), f"{path.name}: {alias.name}"
            elif isinstance(node, ast.ImportFrom):
                assert not (node.module or "").startswith("engine."), f"{path.name}: {node.module}"


def test_runtime_declares_no_new_role_permission_or_capability_group():
    # Authority-neutral: the package defines no Role / Permission / CapabilityGroup enum.
    forbidden = ("class Role", "class Permission", "class CapabilityGroup")
    for path in _iter_source_files():
        text = path.read_text()
        for token in forbidden:
            assert token not in text, f"{path.name} declares {token!r}"


def test_runtime_writes_nothing_to_corpus_or_filesystem():
    # No filesystem writes, sockets, servers, or network egress (deterministic in-memory
    # runtime). Checked at the AST level so prose in docstrings (e.g. "opens no socket")
    # does not trip the guard — only real imports/calls count.
    banned_imports = {"socket", "urllib", "requests", "http", "pathlib", "os"}
    for path in _iter_source_files():
        tree = ast.parse(path.read_text(), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    root = alias.name.split(".")[0]
                    assert root not in banned_imports, f"{path.name}: import {alias.name}"
            elif isinstance(node, ast.ImportFrom):
                root = (node.module or "").split(".")[0]
                assert root not in banned_imports, f"{path.name}: from {node.module}"
            elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                assert node.func.id != "open", f"{path.name}: open() call"


def test_package_exposes_no_authority_verbs():
    # The runtime exposes no authorize/ratify/enact/grant/govern/override verb.
    import platform.blueprints as bp

    for verb in ("authorize", "ratify", "enact", "grant", "govern", "override"):
        assert not hasattr(bp, verb)
