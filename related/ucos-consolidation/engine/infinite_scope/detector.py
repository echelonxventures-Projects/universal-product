"""UISD-000001 — the structural detector for closed enumerations.

ISD-L-01 measures that every *disclosed* closed enumeration names a closing invariant
and an admission path. It does not, and cannot, tell you whether the disclosure list is
complete — its own declaration says so:

    ISD-L-01 measures that each entry names a closing invariant and an admission path,
    not that the list is exhaustive — a claim of exhaustiveness would be the very finite
    assumption the principle prohibits.

That reasoning is correct and it leaves a hole the size of the repository. "Unbounded" was
being measured only where somebody had remembered to declare boundedness: eleven
disclosures against a tree that structurally contains hundreds of closed enumerations,
including ``KNOWN_EXECUTION_KINDS`` in the constitutional kernel, whose comment claims
"Open by registration (Article 17)" while no registration function exists anywhere.

WHAT CHANGES, AND WHAT DOES NOT. Exhaustiveness still cannot be proven — you cannot prove
the absence of a finite assumption you have not thought of. But you *can* enumerate the
SHAPES a closed enumeration takes in Python and require every occurrence of a shape to be
disclosed or refused. That converts an unbounded proof-of-absence into a bounded
proof-of-disclosure, which is decidable. A list of known violations is finite and goes
stale; a detector for the violation's shape does not, and catches the one somebody adds
next year without reading any of this.

THREE SHAPES, AND WHY ONLY THESE THREE. An ``enum.Enum`` subclass, a module-level constant
bound to a literal collection of strings, and a ``typing.Literal[...]`` of constants. Each
is a set whose membership is fixed at import and can only be changed by editing the
module — which is precisely what UCKP-ART-17 forbids ("admitted by registration, never by
amendment"). Shapes that are *not* detected are as deliberate: a set built by calling a
registry, a frozenset comprehension over declared data, and a collection of non-strings
are all either open or not an identifier space, and reporting them would train the reader
to ignore the report.

IT MUST NOT MATCH ITSELF. :func:`check_no_active_permanence_declaration` records what
happens when a detector is its own first finding, and it avoids the literal token it
detects. This module has the same exposure and answers it structurally rather than by
evasion: detection is by AST shape, so a docstring naming a shape is not an instance of
it, and this module declares no module-level literal string collection for the detector to
find. The test suite asserts that, because a comment promising it is not evidence.

Pure: reads files, parses them, returns findings. No clock, no network, no subprocess, no
write — a verdict is reproducible and a gate built on it cannot dirty the tree.
"""

from __future__ import annotations

import ast
import os
from dataclasses import dataclass

#: Shortest collection that reads as an enumeration. A one-member tuple is a value with
#: brackets around it, not a set of admitted members, and reporting it would bury the
#: findings that matter under a very long tail of singletons.
MIN_MEMBERS = 2


@dataclass(frozen=True, slots=True)
class Closure:
    """One structurally closed enumeration, located."""

    path: str
    line: int
    shape: str
    name: str
    members: int

    @property
    def key(self) -> tuple[str, str]:
        """What a disclosure must name to cover this: the file and the binding."""
        return (self.path, self.name)

    def describe(self) -> str:
        return f"{self.path}:{self.line} {self.shape} {self.name} ({self.members} members)"


def _string_members(node: ast.expr) -> int:
    """Member count when `node` is a literal collection of strings, else 0."""
    elts: list[ast.expr] | None = None
    if isinstance(node, ast.Tuple | ast.List | ast.Set):
        elts = list(node.elts)
    elif (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id in ("frozenset", "set", "tuple", "list")
        and node.args
        and isinstance(node.args[0], ast.Tuple | ast.List | ast.Set)
    ):
        elts = list(node.args[0].elts)
    if not elts:
        return 0
    if all(isinstance(e, ast.Constant) and isinstance(e.value, str) for e in elts):
        return len(elts)
    return 0


def closures_in_source(source: str, path: str) -> list[Closure]:
    """Every closed enumeration in one module, by shape."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        # A file that does not parse is not a finding: it is a different defect, owned by
        # the lint gate. Reporting it here would attribute a syntax error to the wrong law.
        return []

    found: list[Closure] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            if any("Enum" in ast.unparse(base) for base in node.bases):
                members = [
                    stmt.targets[0].id
                    for stmt in node.body
                    if isinstance(stmt, ast.Assign)
                    and stmt.targets
                    and isinstance(stmt.targets[0], ast.Name)
                    and not stmt.targets[0].id.startswith("_")
                ]
                if len(members) >= MIN_MEMBERS:
                    found.append(Closure(path, node.lineno, "enum", node.name, len(members)))
            continue

        if isinstance(node, ast.Assign | ast.AnnAssign):
            target = node.targets[0] if isinstance(node, ast.Assign) else node.target
            if not isinstance(target, ast.Name) or node.value is None:
                continue
            # UPPER_CASE marks a module constant. A lowercase local built from a literal is
            # a value in a function body, not a declared identifier space.
            if not (target.id.isupper() and len(target.id) > 1):
                continue
            count = _string_members(node.value)
            if count >= MIN_MEMBERS:
                found.append(Closure(path, node.lineno, "literal-set", target.id, count))
            continue

        if isinstance(node, ast.Subscript) and "Literal" in ast.unparse(node.value):
            slc = node.slice
            elts = list(slc.elts) if isinstance(slc, ast.Tuple) else [slc]
            if len(elts) >= MIN_MEMBERS and all(isinstance(e, ast.Constant) for e in elts):
                label = ast.unparse(node)[:60]
                found.append(Closure(path, node.lineno, "literal-type", label, len(elts)))
    return found


def detect(
    repo: str,
    roots: tuple[str, ...],
    excluded_dir_names: frozenset[str],
    excluded_path_fragments: tuple[str, ...],
) -> list[Closure]:
    """Every closed enumeration under `roots`, sorted for a stable verdict.

    Test modules are excluded by fragment, not by guesswork: a test that pins a vocabulary
    is asserting a fact about the vocabulary, and the vocabulary is where the obligation
    to disclose lives. Counting the assertion as a second closure would double-count one
    boundary and make the ceiling meaningless.
    """
    found: list[Closure] = []
    for root in roots:
        base = os.path.join(repo, root)
        if not os.path.isdir(base):
            continue
        for dirpath, dirnames, filenames in os.walk(base):
            dirnames[:] = [
                d for d in dirnames if d not in excluded_dir_names and not d.startswith(".")
            ]
            for filename in filenames:
                if not filename.endswith(".py"):
                    continue
                full = os.path.join(dirpath, filename)
                rel = os.path.relpath(full, repo)
                if any(fragment in rel for fragment in excluded_path_fragments):
                    continue
                try:
                    with open(full, encoding="utf-8") as handle:
                        source = handle.read()
                except OSError:
                    continue
                found.extend(closures_in_source(source, rel))
    return sorted(found, key=lambda c: (c.path, c.line, c.name))


def undisclosed(found: list[Closure], disclosed_keys: frozenset[tuple[str, str]]) -> list[Closure]:
    """The findings no disclosure covers.

    A disclosure covers a closure when it names the same file and the same binding. Matching
    on the file alone would let one disclosure absolve every enumeration in a module, which
    is how a disclosure list becomes a suppression list.
    """
    return [c for c in found if c.key not in disclosed_keys]


__all__ = ["MIN_MEMBERS", "Closure", "closures_in_source", "detect", "undisclosed"]
