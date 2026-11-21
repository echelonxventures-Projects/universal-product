"""UCON-000001 Part 08 — the extensibility audit. It measures; it does not migrate.

This module locates every closure mechanism in the declared roots and reports it with its
module, symbol, form, member count, risk tier, declared owner, extensibility limitation and
proposed migration path. It edits nothing, rewrites nothing and migrates nothing — the
requirement it answers says *measure first*, and a scanner that also fixed things would make
the measurement unrepeatable, because the second run would be measuring the first run's edits.

Five closure forms are detected, each declared in the audit section of the declaration together
with what it *costs* and how it would be *opened*. That pairing matters: a bare count of enums
is a statistic, while a count joined to a limitation and a migration path is an inventory
somebody can act on. The detectors are two-way bound to the declared forms, so a declared form
nothing detects and a detector no form declares are both hard failures.

Risk is **declared, never inferred**. ``audit.declared_tiers`` maps a module prefix to a tier
and an owner, resolved by longest prefix so that declaring a narrower owner does not depend on
list order. A module no prefix claims takes the declared ``undeclared_tier`` and is counted in
the backlog. Inferring a tier from a keyword would manufacture exactly the classification the
audit exists to measure, and it would do so invisibly.

The enforcement is a **ratchet with two halves**, because a single global gate demanding zero
closures would have been closed on the day it was written and would then have been deleted —
UISD-000001 §ISD-L-07 established that failure mode in this repository:

    inside ``governed_scope``   every closure must be DISCLOSED, with an intentional flag, a
                                closing invariant and an admission path. An undisclosed closure
                                is a violation. A disclosure whose closure is no longer present
                                is *also* a violation, so the disclosures cannot rot into claims
                                about the past.

    outside ``governed_scope``  the population per form may not EXCEED the declared baseline. It
                                may hold, and it may fall. Widening ``governed_scope`` is how
                                backlog becomes enforcement, one named owner at a time.

Governed scope initially contains exactly this capability. A capability that ratcheted every
other owner's code before its own would have inverted the obligation.
"""

from __future__ import annotations

import ast
import os
from collections.abc import Iterator, Mapping
from dataclasses import dataclass
from typing import Any

from engine.construct.declaration import AuditSpec, Declaration, load_declaration, repo_root
from engine.construct.model import ConstructError
from engine.uckp.canonical import canonical_json, content_hash

#: The AST base names that make a class a closed enumeration.
_ENUM_BASES = frozenset({"Enum", "IntEnum", "StrEnum", "Flag", "IntFlag"})

#: Detector results memoised on the CONTENT DIGEST of the source, never on a path or an mtime.
#: The audit is a pure function of the bytes it reads, so two files with the same content have
#: the same closures by definition — which makes this memoisation correct by construction rather
#: than correct by assumption. Keying on a path would serve a stale answer after an edit, and
#: keying on an mtime would serve one after an edit that preserved the timestamp; keying on the
#: content cannot, because a changed byte is a changed key. The cache exists because the laws
#: measure the same tree several times per run (UCON-L-15 and UCON-L-16 both scan it, and
#: UCON-L-16 scans it twice on purpose), and parsing several hundred modules repeatedly was the
#: dominant cost of the gate.
_FINDINGS: dict[tuple[str, str], tuple[tuple[str, int, int], ...]] = {}


class AuditError(ConstructError):
    """A source root could not be read. A fault, never a closure finding."""


@dataclass(frozen=True, slots=True)
class Closure:
    """One located closure mechanism, joined to its declared tier, owner and remedy."""

    module: str
    symbol: str
    form: str
    line: int
    members: int
    tier: str
    owner: str
    governed: bool
    disclosed: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "disclosed": self.disclosed,
            "form": self.form,
            "governed": self.governed,
            "line": self.line,
            "members": self.members,
            "module": self.module,
            "owner": self.owner,
            "symbol": self.symbol,
            "tier": self.tier,
        }


# --- the detectors -------------------------------------------------------------------------------
#
# One generator per declared closure form. Each yields ``(symbol, line, members)``. They are
# deliberately syntactic: the audit reads source, never imports it, so scanning cannot execute
# repository code and a module that fails to import is still measured.


def _assignments(tree: ast.Module) -> Iterator[tuple[str, ast.expr, int]]:
    """Module-level UPPER_SNAKE assignments, plain and annotated, as (name, value, line)."""
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            target = node.targets[0]
            if isinstance(target, ast.Name) and target.id.isupper() and node.value is not None:
                yield target.id, node.value, node.lineno
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            if node.target.id.isupper() and node.value is not None:
                yield node.target.id, node.value, node.lineno


def _detect_enum_class(tree: ast.Module) -> Iterator[tuple[str, int, int]]:
    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef):
            continue
        bases = {ast.unparse(base).split(".")[-1] for base in node.bases}
        if bases & _ENUM_BASES:
            members = sum(
                1 for statement in node.body if isinstance(statement, ast.Assign | ast.AnnAssign)
            )
            yield node.name, node.lineno, members


def _detect_frozen_membership_set(tree: ast.Module) -> Iterator[tuple[str, int, int]]:
    for name, value, line in _assignments(tree):
        if isinstance(value, ast.Set):
            yield name, line, len(value.elts)
        elif (
            isinstance(value, ast.Call)
            and isinstance(value.func, ast.Name)
            and value.func.id == "frozenset"
        ):
            yield name, line, _cardinality(value.args[0] if value.args else None)


def _detect_fixed_vocabulary_tuple(tree: ast.Module) -> Iterator[tuple[str, int, int]]:
    for name, value, line in _assignments(tree):
        if isinstance(value, ast.Tuple) and value.elts:
            if all(isinstance(element, ast.Constant | ast.Tuple) for element in value.elts):
                yield name, line, len(value.elts)


def _detect_fixed_dispatch_table(tree: ast.Module) -> Iterator[tuple[str, int, int]]:
    for name, value, line in _assignments(tree):
        if isinstance(value, ast.Dict) and value.keys:
            yield name, line, len(value.keys)


def _detect_population_assertion(tree: ast.Module) -> Iterator[tuple[str, int, int]]:
    for node in ast.walk(tree):
        if not isinstance(node, ast.Compare) or len(node.ops) != 1:
            continue
        if not isinstance(node.ops[0], ast.Eq):
            continue
        right = node.comparators[0]
        if not (isinstance(right, ast.Constant) and isinstance(right.value, int)):
            continue
        if isinstance(right.value, bool):
            continue
        left = node.left
        if isinstance(left, ast.Call) and isinstance(left.func, ast.Name) and left.func.id == "len":
            yield ast.unparse(left), node.lineno, right.value
        elif isinstance(left, ast.Name | ast.Attribute) and "count" in ast.unparse(left).lower():
            yield ast.unparse(left), node.lineno, right.value


def _cardinality(node: ast.expr | None) -> int:
    if isinstance(node, ast.Set | ast.Tuple | ast.List):
        return len(node.elts)
    return 0


#: The implemented detectors, keyed by the closure form the declaration names. Two-way bound:
#: a declared form nothing detects and a detector no form declares are both refused at load.
DETECTORS: Mapping[str, Any] = {
    "ENUM_CLASS": _detect_enum_class,
    "FIXED_DISPATCH_TABLE": _detect_fixed_dispatch_table,
    "FIXED_VOCABULARY_TUPLE": _detect_fixed_vocabulary_tuple,
    "FROZEN_MEMBERSHIP_SET": _detect_frozen_membership_set,
    "POPULATION_ASSERTION": _detect_population_assertion,
}


def available_forms() -> frozenset[str]:
    """The closure forms this module can detect — the set the declaration is bound against."""
    return frozenset(DETECTORS)


# --- the scan ------------------------------------------------------------------------------


def _sources(spec: AuditSpec, repo: str) -> tuple[str, ...]:
    """Every source file in the declared roots, relative to the repository, sorted.

    Sorted so the inventory is byte-stable across filesystems: ``os.walk`` order is not
    guaranteed, and an inventory whose row order depended on the filesystem would produce a
    different digest on a different machine while describing the same repository.
    """
    found: list[str] = []
    for root in spec.roots:
        base = os.path.join(repo, root)
        if not os.path.isdir(base):
            continue
        for dirpath, dirnames, filenames in os.walk(base):
            dirnames[:] = sorted(
                name
                for name in dirnames
                if name not in spec.exclude_dir_names
                and not any(name.startswith(prefix) for prefix in spec.exclude_dir_prefixes)
            )
            for filename in sorted(filenames):
                if any(filename.endswith(extension) for extension in spec.extensions):
                    found.append(os.path.relpath(os.path.join(dirpath, filename), repo))
    return tuple(sorted(found))


class _Unparseable(Exception):
    """A file the parser could not read. Reported by the inventory, never crashes the audit."""


def _read(root: str, relpath: str) -> tuple[str, str] | None:
    """The source and its content digest, or None when the file cannot be read at all."""
    try:
        with open(os.path.join(root, relpath), encoding="utf-8") as handle:
            source = handle.read()
    except (OSError, ValueError):
        return None
    return source, content_hash(source)


def _findings(
    source: str, digest: str, form: str, relpath: str
) -> tuple[tuple[str, int, int], ...]:
    """The closures of one form in one source, memoised on the content digest."""
    key = (digest, form)
    cached = _FINDINGS.get(key)
    if cached is not None:
        return cached
    detector = DETECTORS.get(form)
    if detector is None:
        raise AuditError(f"closure form {form!r} is declared but no detector implements it")
    try:
        tree = ast.parse(source, filename=relpath)
    except (SyntaxError, ValueError):
        raise _Unparseable(relpath) from None
    result = tuple(detector(tree))
    _FINDINGS[key] = result
    return result


def scan(declaration: Declaration | None = None, repo: str | None = None) -> tuple[Closure, ...]:
    """Every located closure, ordered by (module, line, symbol). Reads source; imports nothing."""
    spec = (declaration or load_declaration()).audit
    root = repo or repo_root()
    disclosures = {
        (disclosure.module, disclosure.symbol): disclosure.closure_id
        for disclosure in spec.disclosures
    }
    found: list[Closure] = []
    for relpath in _sources(spec, root):
        read = _read(root, relpath)
        if read is None:
            # A file that cannot be read is reported as unscannable by the inventory rather than
            # crashing the audit: one malformed module must not make the repository unmeasurable,
            # and silently skipping it would be worse than counting it.
            continue
        source, digest = read
        declared_tier, declared_owner = spec.tier_for(relpath)
        governed = spec.in_governed_scope(relpath)
        for form in spec.forms:
            try:
                located = _findings(source, digest, form.form, relpath)
            except _Unparseable:
                break
            for symbol, line, members in located:
                disclosed = disclosures.get((relpath, symbol), "")
                found.append(
                    Closure(
                        module=relpath,
                        symbol=symbol,
                        form=form.form,
                        line=line,
                        members=members,
                        # The declared criterion for R4 is "appears in disclosed_closures with
                        # intentional true", so a disclosed closure takes R4 regardless of its
                        # module's prefix. Assigning it the prefix tier instead would have left
                        # R4 permanently empty — a declared tier nothing can ever occupy, which
                        # is a closure in the risk model itself.
                        tier=(
                            spec.deliberate_tier
                            if disclosed in spec.intentional_disclosures
                            else (declared_tier or spec.undeclared_tier)
                        ),
                        owner=declared_owner,
                        governed=governed,
                        disclosed=disclosed,
                    )
                )
    return tuple(sorted(found, key=lambda c: (c.module, c.line, c.symbol, c.form)))


def unscannable(declaration: Declaration | None = None, repo: str | None = None) -> tuple[str, ...]:
    """Files in the declared roots the parser could not read. Reported, never ignored."""
    spec = (declaration or load_declaration()).audit
    root = repo or repo_root()
    broken: list[str] = []
    for relpath in _sources(spec, root):
        read = _read(root, relpath)
        if read is None:
            broken.append(relpath)
            continue
        source, digest = read
        try:
            _findings(source, digest, next(iter(DETECTORS)), relpath)
        except _Unparseable:
            broken.append(relpath)
    return tuple(broken)


def inventory(declaration: Declaration | None = None, repo: str | None = None) -> dict[str, Any]:
    """The complete extensibility inventory: every closure, joined to tier, owner and remedy."""
    resolved = declaration or load_declaration()
    spec = resolved.audit
    root = repo or repo_root()
    closures = scan(resolved, root)
    limitations = {form.form: form.limitation for form in spec.forms}
    migrations = {form.form: form.migration for form in spec.forms}

    by_form: dict[str, int] = {form.form: 0 for form in spec.forms}
    by_tier: dict[str, int] = {str(row["tier"]): 0 for row in spec.risk_tiers}
    by_owner: dict[str, int] = {}
    by_module: dict[str, int] = {}
    outside: dict[str, int] = {form.form: 0 for form in spec.forms}
    inside: list[Closure] = []
    for closure in closures:
        by_form[closure.form] = by_form.get(closure.form, 0) + 1
        by_tier[closure.tier] = by_tier.get(closure.tier, 0) + 1
        key = closure.owner or "UNDECLARED"
        by_owner[key] = by_owner.get(key, 0) + 1
        by_module[closure.module] = by_module.get(closure.module, 0) + 1
        if closure.governed:
            inside.append(closure)
        else:
            outside[closure.form] = outside.get(closure.form, 0) + 1

    undisclosed = [c for c in inside if not c.disclosed]
    located = {(c.module, c.symbol) for c in closures}
    stale = [
        disclosure.closure_id
        for disclosure in spec.disclosures
        if (disclosure.module, disclosure.symbol) not in located
    ]
    exceeded = {
        form: {"baseline": spec.baseline[form], "measured": count}
        for form, count in sorted(outside.items())
        if form in spec.baseline and count > spec.baseline[form]
    }

    return {
        "schema": "ucos-construct-closure-inventory",
        "version": "1.0.0",
        "authority": "NONE — DERIVED EXTENSIBILITY INTELLIGENCE. This inventory certifies "
        "no closure, licenses no closure and migrates no closure. It measures.",
        "declaration": resolved.artifact_id,
        "declaration_version": resolved.version,
        "baseline": dict(sorted(spec.baseline.items())),
        "baseline_exceeded": exceeded,
        "closures": [closure.as_dict() for closure in closures],
        "counts": {
            "by_form": dict(sorted(by_form.items())),
            "by_owner": dict(sorted(by_owner.items())),
            "by_tier": dict(sorted(by_tier.items())),
            "governed_scope": len(inside),
            "modules_with_closures": len(by_module),
            "outside_governed_scope": dict(sorted(outside.items())),
            "total": len(closures),
        },
        "disclosures": [
            {
                "admission": disclosure.admission,
                "closing_invariant": disclosure.closing_invariant,
                "closure_id": disclosure.closure_id,
                "form": disclosure.form,
                "gap": disclosure.gap,
                "intentional": disclosure.intentional,
                "module": disclosure.module,
                "symbol": disclosure.symbol,
            }
            for disclosure in sorted(spec.disclosures, key=lambda d: d.closure_id)
        ],
        "governed_scope": list(spec.governed_scope),
        "limitations": dict(sorted(limitations.items())),
        "migrations": dict(sorted(migrations.items())),
        "risk_tiers": [dict(sorted(row.items())) for row in spec.risk_tiers],
        "stale_disclosures": sorted(stale),
        "top_modules": [
            {"closures": count, "module": module}
            for module, count in sorted(by_module.items(), key=lambda kv: (-kv[1], kv[0]))[:25]
        ],
        "undeclared_tier": spec.undeclared_tier,
        "undisclosed_in_governed_scope": [closure.as_dict() for closure in undisclosed],
        "unscannable": list(unscannable(resolved, root)),
        "closed_set": False,
        "upper_limit": None,
    }


def validate(report: Mapping[str, Any]) -> list[str]:
    """Every ratchet violation in ``report``, or an empty list.

    Three ways to fail, and the second and third are what make this a ratchet rather than a
    snapshot: an undisclosed closure inside governed scope, a disclosure whose closure has
    disappeared, and a population outside governed scope above its declared baseline.
    """
    problems: list[str] = []
    for closure in report.get("undisclosed_in_governed_scope") or ():
        problems.append(
            f"{closure['module']}:{closure['line']} {closure['symbol']} ({closure['form']}) is "
            "a closure inside governed scope with no disclosure; declare its closing invariant "
            "and admission path"
        )
    for closure_id in report.get("stale_disclosures") or ():
        problems.append(
            f"{closure_id} discloses a closure that is no longer present; the disclosure is "
            "stale and must be removed rather than left as a claim about the past"
        )
    for form, counts in (report.get("baseline_exceeded") or {}).items():
        problems.append(
            f"{form}: {counts['measured']} outside governed scope exceeds the declared baseline "
            f"of {counts['baseline']}; the ratchet may hold or fall, never rise"
        )
    return problems


def rendered(report: Mapping[str, Any]) -> str:
    """Canonical serialisation, from Layer Zero (UCKP-LAW-0001 §Art-13)."""
    return canonical_json(report)


def digest(report: Mapping[str, Any]) -> str:
    return content_hash(report)


def verify(declaration: Declaration | None = None, repo: str | None = None) -> dict[str, Any]:
    """Build the inventory twice and report determinism alongside the ratchet verdict."""
    resolved = declaration or load_declaration()
    root = repo or repo_root()
    first = inventory(resolved, root)
    second = inventory(resolved, root)
    problems = validate(first)
    return {
        "counts": first["counts"],
        "deterministic": rendered(first) == rendered(second) and digest(first) == digest(second),
        "digest": digest(first),
        "problems": problems,
        "status": "PASS" if not problems else "FAIL",
    }


__all__ = [
    "DETECTORS",
    "AuditError",
    "Closure",
    "available_forms",
    "digest",
    "inventory",
    "rendered",
    "scan",
    "unscannable",
    "validate",
    "verify",
]
