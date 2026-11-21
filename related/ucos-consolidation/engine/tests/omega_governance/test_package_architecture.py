"""Ω∞ governance — the claims the packages make about themselves, measured.

THE CLAIM THIS MODULE EXISTS FOR is in ``reference/__init__.py``: "Nothing in this package imports
``engine.omega_governance.temporal``, so Time is not the root of the architecture." The docstring
then says ``openworld.no_domain_is_privileged`` checks it. There is no ``openworld`` module. The
architecture's central claim was therefore asserted in prose and checked by nothing, which is the
exact shape of defect the whole Ω programme exists to eliminate — a list that agrees with itself.

It is checked here instead, over the parsed source rather than over a docstring, so a future import
that quietly made Time the root would fail this suite rather than contradict a paragraph nobody
re-reads.
"""

from __future__ import annotations

import ast
import pathlib

import engine.omega_governance
import engine.omega_governance.reference
import engine.omega_governance.temporal

PACKAGE_ROOT = pathlib.Path(engine.omega_governance.__file__).parent


def _imported_modules(source: pathlib.Path) -> set[str]:
    """Every dotted module name this file imports, from its AST rather than from a text search."""
    names: set[str] = set()
    tree = ast.parse(source.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module and not node.level:
            names.add(node.module)
    return names


def _index_entries(docstring: str) -> set[str]:
    """The module names an index BLOCK lists, which is not every ``.py`` the docstring mentions.

    An index entry is the first token of an indented line — the ``name.py   description`` shape.
    Prose that discusses a module by name mid-sentence is deliberately not an index entry, because a
    docstring naming a module it says is ABSENT would otherwise be read as promising it.
    """
    entries: set[str] = set()
    for line in docstring.splitlines():
        if not line.startswith("    ") or not line.strip():
            continue
        token = line.split()[0].strip("`,.")
        if token.endswith(".py") and "/" not in token:
            entries.add(token)
    return entries


def _modules_under(subpackage: str) -> list[pathlib.Path]:
    return sorted((PACKAGE_ROOT / subpackage).rglob("*.py"))


def test_every_subpackage_declares_that_it_holds_no_authority() -> None:
    """These packages classify, resolve and record. None certifies anything, and each says so in a
    value rather than only in prose.

    THE LITERAL IS THE ONE UCOS-UCAF-001 CLASSIFIES (UCAF-TC-02, "the derived-truth tier records and
    asserts nothing"). It was ``"NONE"`` — the same standing in a spelling no token class carried —
    and the authority-realization gate reported three tokens minted in the executable plane and
    classified nowhere, which closed UCAF-VAL-17 and, downstream of it, UCAF-VAL-14. Asserting the
    exact literal here is what stops the two spellings from diverging again.
    """
    expected = "NONE (DERIVED TRUTH)"
    assert engine.omega_governance.AUTHORITY == expected
    assert engine.omega_governance.reference.AUTHORITY == expected
    assert engine.omega_governance.temporal.AUTHORITY == expected


def test_no_domain_is_privileged_because_reference_never_imports_temporal() -> None:
    """The dependency direction IS the non-privilege claim, and it is the one property that would
    quietly stop being true: adding ``from ..temporal.coordinate import TemporalCoordinate`` to a
    reference module is a one-line change that makes Time the root of the architecture."""
    offenders = {
        module.relative_to(PACKAGE_ROOT).as_posix(): sorted(
            name
            for name in _imported_modules(module)
            if name.startswith("engine.omega_governance.temporal")
        )
        for module in _modules_under("reference")
    }
    named = {path: imports for path, imports in offenders.items() if imports}
    assert not named, (
        f"reference imports temporal in {named}; Time would then be the root of the architecture "
        "rather than one registered domain among fourteen"
    )


def test_temporal_does_import_reference_so_the_direction_is_real_and_not_merely_absent() -> None:
    """Non-vacuity for the test above. Two packages that simply never speak to each other would pass
    a one-directional check while establishing nothing about which is subordinate."""
    reached = set()
    for module in _modules_under("temporal"):
        reached.update(
            name
            for name in _imported_modules(module)
            if name.startswith("engine.omega_governance.reference")
        )
    assert reached, "temporal imports nothing from reference, so the claimed direction is untested"


def test_a_deployment_registering_no_clock_still_has_a_complete_architecture() -> None:
    """``temporal`` is one registered domain among fourteen, so the reference layer must be fully
    usable without it — that is what "not the root" means operationally rather than structurally."""
    from engine.omega_governance.reference.capability import ORDERABLE
    from engine.omega_governance.reference.domain import default_domains
    from engine.omega_governance.reference.encoding import default_encoding

    domains = default_domains()
    domains.assert_authority_total()
    assert len(domains) == 14
    assert domains.capable(ORDERABLE)
    assert default_encoding().fingerprint({"a": 1})


def test_the_governance_layer_reaches_the_reference_layer_for_its_own_values() -> None:
    """``state`` and ``authority`` record temporal coordinates and encode values, so the governance
    layer sits ABOVE both — which is the ordering the package docstring claims."""
    reached = set()
    for module in (PACKAGE_ROOT / "state.py", PACKAGE_ROOT / "authority.py"):
        reached.update(
            name
            for name in _imported_modules(module)
            if name.startswith("engine.omega_governance.")
        )
    assert any(name.startswith("engine.omega_governance.temporal") for name in reached)


def test_the_package_index_names_only_modules_that_exist() -> None:
    """A READ IN THIS ORDER list is a promise about the tree. ``omega_governance`` promised eleven
    modules and shipped two of them, so a reader following the index reached for files that were
    never written — and nothing said so, because a docstring is not measured.

    Checked against the ``.py`` names the docstring actually cites, so adding a module keeps the
    index honest in the other direction too.
    """
    for package in (
        engine.omega_governance,
        engine.omega_governance.reference,
        engine.omega_governance.temporal,
    ):
        root = pathlib.Path(package.__file__).parent
        present = {path.name for path in root.glob("*.py")}
        cited = _index_entries(package.__doc__ or "")
        missing = sorted(cited - present)
        assert not missing, (
            f"{package.__name__} documents {missing}, which the tree does not contain; a reader "
            "following the index reaches for a file that was never written"
        )
