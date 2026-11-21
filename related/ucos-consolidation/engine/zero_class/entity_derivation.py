"""ZX-02 — where a decision asks the FILENAME what something is, rather than the entity.

UCKP-ART-15 requires every conclusion to be derived from the declared universe rather than a
hardcoded assumption, and engine/omega_infinite/classification.py already declares how an
artifact's type is decided: four rules in precedence order, Ω∞-T-01 provider-declared, Ω∞-T-02
content interpreter, Ω∞-T-03 content structure, Ω∞-T-04 suffix. The suffix is the LAST resort.

A module that branches on `path.endswith(".py")` has skipped the first three rules. It reaches the
right answer for every file whose name happens to match, and no answer at all for a Python file
with a shebang and no extension — which is why the edge deriver carried that defect until it was
keyed on the classified type instead.

NOT EVERY SUFFIX TEST IS THAT DEFECT, AND THE DETECTOR MUST NOT PRETEND OTHERWISE. Two populations
share the same syntax and only one is wrong:

  A FILENAME CONVENTION is a rule about names, and a name is the right thing to ask.
  `name.startswith("test_") and name.endswith(".py")` is pytest's contract; a test file IS
  defined by what it is called. Deriving that from a classifier would be worse, not better.

  A DECLARED SCOPE names several kinds at once — `(".yml", ".yaml", ".sh", ".py", ".mk")` — which
  is a statement about which file kinds a measurement covers, not a question about what one file
  is.

  A TYPE DECISION is a bare single-suffix test standing alone. That is the one asking the
  filename a question the classifier answers properly.

Measured when this was written: 4 conventions, and the rest type decisions. A count that fell by
"fixing" a convention would be the false progress adr/0042 forbids, so the detector separates them
rather than counting everything that looks alike.
"""

from __future__ import annotations

import ast
import json
import os
import pathlib

UCON_DECLARATION = "00-MASTER/UCON-000001/ucon-declaration.json"

#: MOVEMENTS
#:   (established) 51  Baseline measured by AST over the declared source roots, excluding tests.
#:                     Conventions and declared scopes are excluded BY THE PREDICATE rather than by
#:                     a list, so the number counts decisions that could be derived and are not.
#:
#:                     THE FIRST CEILING WAS 57 AND WAS WRONG, from a looser scan that counted a
#:                     `.endswith` anywhere in a module rather than one standing alone. Setting a
#:                     ceiling above the measurement leaves room a later regression could occupy
#:                     silently, which is the opposite of what a ratchet is for.
TYPE_DECISION_CEILING = 51


def roots(base: pathlib.Path) -> tuple[str, ...]:
    """The source roots to scan, read from the declaration that already names them."""
    document = json.loads((base / UCON_DECLARATION).read_text(encoding="utf-8"))
    declared = document.get("audit", {}).get("roots")
    if not isinstance(declared, list) or not declared:
        raise RuntimeError(f"{UCON_DECLARATION} declares no audit roots to scan")
    return tuple(str(entry) for entry in declared) + ("00-BOOK/tools", "00-MASTER")


def _suffix_tests(node: ast.AST):
    """Every `.endswith(...)` call whose arguments name file suffixes."""
    for inner in ast.walk(node):
        if not isinstance(inner, ast.Call):
            continue
        func = inner.func
        name = func.attr if isinstance(func, ast.Attribute) else getattr(func, "id", "")
        if name != "endswith":
            continue
        values: list[ast.expr] = []
        for argument in inner.args:
            if isinstance(argument, ast.Constant):
                values.append(argument)
            elif isinstance(argument, ast.Tuple | ast.List):
                values.extend(argument.elts)
        suffixes = [
            v.value
            for v in values
            if isinstance(v, ast.Constant) and isinstance(v.value, str) and v.value.startswith(".")
        ]
        if suffixes:
            yield inner, suffixes


def _names_a_prefix(node: ast.AST) -> bool:
    """Whether this expression also tests a name or path prefix — the mark of a convention."""
    for inner in ast.walk(node):
        if isinstance(inner, ast.Call):
            func = inner.func
            name = func.attr if isinstance(func, ast.Attribute) else getattr(func, "id", "")
            if name == "startswith":
                return True
    return False


def type_decisions_in(path: pathlib.Path) -> tuple[int, ...]:
    """Line numbers where this module asks a filename what something is."""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="ignore"))
    except (SyntaxError, OSError):  # pragma: no cover - unparseable file
        return ()
    excused: set[int] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.BoolOp) and _names_a_prefix(node):
            excused.update(call.lineno for call, _ in _suffix_tests(node))
    found = []
    for call, suffixes in _suffix_tests(tree):
        if call.lineno in excused:
            continue  # a filename convention: a rule about names
        if len(suffixes) > 1:
            continue  # a declared scope: several kinds named at once
        found.append(call.lineno)
    return tuple(sorted(set(found)))


def asks_the_filename(path: pathlib.Path) -> bool:
    """Predicate form, for the zero-class register's must_catch / must_not_catch cases."""
    return bool(type_decisions_in(path))


def type_decisions(root: str | None = None) -> tuple[str, ...]:
    """Every module deciding a type by filename, as ``path:line``."""
    base = pathlib.Path(root or os.getcwd())
    found: list[str] = []
    for top in roots(base):
        directory = base / top
        if not directory.exists():
            continue
        for path in directory.rglob("*.py"):
            relative = path.relative_to(base).as_posix()
            if {"test", "tests"} & set(path.parts) or path.name.startswith(("test_", "conftest")):
                continue
            if "__pycache__" in relative:
                continue
            found.extend(f"{relative}:{line}" for line in type_decisions_in(path))
    return tuple(sorted(found))


__all__ = [
    "TYPE_DECISION_CEILING",
    "asks_the_filename",
    "roots",
    "type_decisions",
    "type_decisions_in",
]
