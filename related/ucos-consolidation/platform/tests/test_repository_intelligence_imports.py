"""Ω-E06 W3-1 — what counts as a dependency when the question is "can this cycle happen".

Stage-1 recorded C-01 as a real import cycle in engine code
(``certification -> validation -> runtime``) with disposition CONSOLIDATE. It was not.
Two of its three edges existed only inside ``if TYPE_CHECKING:`` blocks whose own comments
read *"typing only, avoids import cycles"*, and the second reported cycle
(``universal_foundation -> universal_measurement -> universal_ownership``) was closed by a
single function-local import in ``universal_ownership/cli.py``. Both are the standard cures
for a circular import. The extractor counted every ``Import`` node reachable from
``ast.walk`` and so reported the cure as the disease — which would have driven a
restructuring of engine code that was already correct.

An import cycle is a property of module *initialisation*. This suite pins the distinction:
a target is at-import only when the interpreter must resolve it to finish importing the
module. Everything else is deferred and cannot deadlock anything.

These are hermetic unit tests over source strings — no repository scan, no git, no
filesystem — so they state the rule rather than re-measuring whatever the tree happens to
contain today.
"""

from __future__ import annotations

import ast
from platform.repository_intelligence.substrate import _imports

import pytest


def classify(source: str, package: str = "pkg.mod") -> tuple[set[str], set[str]]:
    """Return ``(every target, at-import targets)`` for a module source."""
    every, at_import = _imports(ast.parse(source), package)
    return set(every), set(at_import)


# --------------------------------------------------------------- resolved at import time
def test_a_module_level_import_is_resolved_at_import() -> None:
    every, at_import = classify("import engine.runtime\n")
    assert every == {"engine.runtime"}
    assert at_import == {"engine.runtime"}


def test_a_module_level_from_import_is_resolved_at_import() -> None:
    _, at_import = classify("from engine.runtime import Unit\n")
    assert at_import == {"engine.runtime"}


def test_a_class_body_import_is_resolved_at_import() -> None:
    """A class body executes while the module is being imported — unlike a function body."""
    _, at_import = classify("class A:\n    from engine.runtime import Unit\n")
    assert at_import == {"engine.runtime"}


def test_an_import_in_a_conditional_that_is_not_type_checking_is_at_import() -> None:
    _, at_import = classify("import sys\nif sys.version_info >= (3, 12):\n    import tomllib\n")
    assert "tomllib" in at_import


# ------------------------------------------------------------------------------ deferred
def test_a_type_checking_import_is_deferred() -> None:
    source = (
        "from typing import TYPE_CHECKING\nif TYPE_CHECKING:\n    from engine.runtime import U\n"
    )
    every, at_import = classify(source)
    assert "engine.runtime" in every, "the target is still a fact about the module"
    assert "engine.runtime" not in at_import


def test_the_qualified_typing_type_checking_spelling_is_recognised() -> None:
    source = "import typing\nif typing.TYPE_CHECKING:\n    from engine.runtime import U\n"
    _, at_import = classify(source)
    assert "engine.runtime" not in at_import


def test_a_function_body_import_is_deferred() -> None:
    """Deferring an import into a function is THE cure for a circular import."""
    source = "def build():\n    from engine.runtime import U\n    return U\n"
    every, at_import = classify(source)
    assert every == {"engine.runtime"}
    assert at_import == set()


def test_an_async_function_body_import_is_deferred() -> None:
    source = "async def build():\n    from engine.runtime import U\n    return U\n"
    _, at_import = classify(source)
    assert at_import == set()


def test_a_nested_function_body_import_is_deferred() -> None:
    source = "def outer():\n    def inner():\n        import engine.runtime\n    return inner\n"
    _, at_import = classify(source)
    assert at_import == set()


def test_a_method_body_import_is_deferred_even_though_the_class_body_is_not() -> None:
    source = (
        "class A:\n    def build(self):\n        from engine.runtime import U\n        return U\n"
    )
    _, at_import = classify(source)
    assert at_import == set()


def test_a_type_checking_block_inside_a_function_is_deferred() -> None:
    source = (
        "from typing import TYPE_CHECKING\n"
        "def build():\n"
        "    if TYPE_CHECKING:\n"
        "        from engine.runtime import U\n"
    )
    _, at_import = classify(source)
    assert "engine.runtime" not in at_import


# ------------------------------------------------------- the else-arm is NOT deferred
def test_the_else_arm_of_a_type_checking_block_is_resolved_at_import() -> None:
    """The ``else:`` of ``if TYPE_CHECKING:`` is exactly the branch that DOES run.

    Deferring it would erase a real dependency — the same error in the opposite
    direction, and the one that would hide a genuine cycle.
    """
    source = (
        "from typing import TYPE_CHECKING\n"
        "if TYPE_CHECKING:\n"
        "    from engine.runtime import U\n"
        "else:\n"
        "    from engine.fallback import U\n"
    )
    _, at_import = classify(source)
    assert "engine.fallback" in at_import
    assert "engine.runtime" not in at_import


# ------------------------------------------------------------------ one real edge wins
def test_a_target_imported_both_ways_is_at_import() -> None:
    """One unguarded module-level statement makes the dependency load-bearing; deferring
    it somewhere else does not undo that."""
    source = (
        "from typing import TYPE_CHECKING\n"
        "from engine.runtime import A\n"
        "if TYPE_CHECKING:\n"
        "    from engine.runtime import B\n"
        "def build():\n"
        "    from engine.runtime import C\n"
    )
    _, at_import = classify(source)
    assert "engine.runtime" in at_import


@pytest.mark.parametrize("order", ["deferred_first", "module_first"])
def test_the_verdict_does_not_depend_on_source_order(order: str) -> None:
    """``ast`` traversal order must not decide the answer — set membership does."""
    deferred = "def build():\n    from engine.runtime import C\n"
    module_level = "from engine.runtime import A\n"
    source = deferred + module_level if order == "deferred_first" else module_level + deferred
    _, at_import = classify(source)
    assert at_import == {"engine.runtime"}


# ------------------------------------------------------------------------ relative form
def test_relative_imports_resolve_against_the_owning_package() -> None:
    _, at_import = classify("from .sibling import thing\n", package="engine.validation")
    assert at_import == {"engine.validation.sibling"}


def test_a_bare_relative_import_resolves_to_the_package_itself() -> None:
    """``from . import x`` records the PACKAGE, not ``package.x``.

    Pinned as existing behaviour rather than endorsed: the imported name is not appended,
    so the edge is attributed one level up. It does not affect cycle detection — both
    forms attribute to the same capability — but a reader comparing this graph against the
    source would otherwise be surprised, and a future fix should break this test loudly.
    """
    _, at_import = classify("from . import sibling\n", package="engine.validation")
    assert at_import == {"engine.validation"}


def test_a_deferred_relative_import_still_resolves_but_is_not_at_import() -> None:
    source = "def build():\n    from .sibling import thing\n"
    every, at_import = classify(source, package="engine.validation")
    assert every == {"engine.validation.sibling"}
    assert at_import == set()


# ----------------------------------------------------------------------------- degenerate
def test_a_module_with_no_imports_yields_nothing() -> None:
    assert classify("x = 1\n") == (set(), set())
