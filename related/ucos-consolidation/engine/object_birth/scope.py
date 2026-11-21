"""UOBC-BSP-001 — birth scope, measured.

``SCOPE-B-BIRTH-GOVERNANCE-DETERMINATION.md`` §1.2 determined which object kinds require
a birth record and which must never hold one independently. That determination lived only
in prose, so nothing computed it: a generated artifact could be given an independent
constitutional identity, a birth record could name a subject that does not exist, and the
adoption gap could widen with no signal. This module measures the rule.

It legislates nothing. Every kind, selector, floor, gap id and adoption state is DATA in
``00-MASTER/UOBC-000001/birth-scope-policy.json``. There is no object kind, no path, no
floor and no gap id anywhere below — only the generic *operators* a selector may use, and
``BSP-L-01`` refuses a selector naming an operator that is not implemented.

Two design choices are worth stating, because they are what make the classification
trustworthy rather than merely present.

**Ordered, first-match-wins classification.** Kinds are evaluated in declared order. That
makes the result single-valued *by construction* rather than by a uniqueness check that
could pass while two selectors silently overlapped, and total *by construction* through a
final catch-all kind that ``BSP-L-02`` requires to exist and to be last.

**EXCEPTION is a verdict, not a failure.** A kind may require birth while its adoption is
DEFERRED to a named gap. Reporting that as PASS would hide a real obligation; reporting it
as FAIL would demand the corpus-wide backfill ``G11`` explicitly forbids. It is reported as
EXCEPTION carrying the gap id as its authorized reason, so the obligation stays visible and
countable without closing the gate on work nobody has authorized.
"""

from __future__ import annotations

import json
import os
import re
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Any

from engine.object_birth.model import BirthError

#: Verdicts. PASS — the requirement is satisfied. FAIL — it is violated. EXCEPTION — the
#: requirement stands but its adoption is deferred to a declared gap.
PASS = "PASS"  # noqa: S105 — a verdict name, not a credential; bandit matches on "PASS"
FAIL = "FAIL"
EXCEPTION = "EXCEPTION"

#: Enforcement modes a kind may declare.
MANDATORY_ABSENCE = "MANDATORY_ABSENCE"
DISCLOSED_ADOPTION = "DISCLOSED_ADOPTION"
GOVERNED_ELSEWHERE = "GOVERNED_ELSEWHERE"
NOT_REQUIRED = "NOT_REQUIRED"

_POLICY = os.path.join("00-MASTER", "UOBC-000001", "birth-scope-policy.json")
_LEDGER = os.path.join("00-MASTER", "UOBC-000001", "birth-ledger.json")
_OBJECTS = os.path.join("00-MASTER", "UCOS-UGA-001", "02-UNIVERSAL-OBJECT-REGISTRY.json")
_GENERATED = os.path.join("00-BOOK", "DATA", "generated-artifact-registry.json")

_REQUIRED_KIND_FIELDS = (
    "object_kind",
    "birth_required",
    "reason",
    "authority",
    "validation_rule",
    "producer_relationship",
)


def _require_text(entry: Mapping[str, Any], key: str, context: str) -> str:
    """Return a non-empty string field, or fail closed."""
    value = entry.get(key)
    if not isinstance(value, str) or not value.strip():
        raise BirthError(f"{context}: field {key!r} is absent or empty")
    return value


@dataclass(frozen=True, slots=True)
class Kind:
    """One declared object kind and the rule that governs its birth."""

    object_kind: str
    birth_required: bool
    enforcement: str
    selector: Mapping[str, Any]
    reason: str
    authority: str
    validation_rule: str
    producer_relationship: str
    adoption: str | None
    adoption_gap: str | None

    @property
    def is_catch_all(self) -> bool:
        """True when this kind claims every object the kinds above it did not."""
        return bool(self.selector.get("catch_all"))

    @classmethod
    def of(cls, entry: Mapping[str, Any]) -> Kind:
        """Rehydrate a kind, refusing one that could not be measured."""
        for field in _REQUIRED_KIND_FIELDS:
            if field not in entry:
                raise BirthError(f"kind {entry.get('object_kind')!r}: missing {field!r}")
        object_kind = _require_text(entry, "object_kind", "kind")
        if not isinstance(entry.get("birth_required"), bool):
            raise BirthError(f"{object_kind}: birth_required is not a boolean")
        selector = entry.get("selector")
        if not isinstance(selector, Mapping) or not selector:
            raise BirthError(f"{object_kind}: selector is absent or empty")
        return cls(
            object_kind=object_kind,
            birth_required=bool(entry["birth_required"]),
            enforcement=_require_text(entry, "enforcement", object_kind),
            selector=dict(selector),
            reason=_require_text(entry, "reason", object_kind),
            authority=_require_text(entry, "authority", object_kind),
            validation_rule=_require_text(entry, "validation_rule", object_kind),
            producer_relationship=_require_text(entry, "producer_relationship", object_kind),
            adoption=entry.get("adoption"),
            adoption_gap=entry.get("adoption_gap"),
        )


@dataclass(frozen=True, slots=True)
class SubjectRule:
    """How a birth record's URN maps back to the object it names."""

    namespace: str
    local_name_pattern: str
    resolves_to: str
    path_from: str

    @classmethod
    def of(cls, entry: Mapping[str, Any]) -> SubjectRule:
        """Rehydrate a subject-resolution rule."""
        namespace = _require_text(entry, "namespace", "subject_resolution")
        return cls(
            namespace=namespace,
            local_name_pattern=_require_text(entry, "local_name_pattern", namespace),
            resolves_to=_require_text(entry, "resolves_to", namespace),
            path_from=_require_text(entry, "path_from", namespace),
        )


@dataclass(frozen=True, slots=True)
class Floor:
    """The number of birth records of one subject class that may never decrease."""

    subject_class: str
    born_at_baseline: int

    @classmethod
    def of(cls, entry: Mapping[str, Any]) -> Floor:
        """Rehydrate a coverage floor."""
        subject_class = _require_text(entry, "subject_class", "coverage_floor")
        value = entry.get("born_at_baseline")
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            raise BirthError(f"{subject_class}: born_at_baseline is not a whole number")
        return cls(subject_class=subject_class, born_at_baseline=value)


@dataclass(frozen=True, slots=True)
class ScopeLaw:
    """One birth-scope law and the check that computes it."""

    law_id: str
    title: str
    statement: str
    check: str

    @classmethod
    def of(cls, entry: Mapping[str, Any]) -> ScopeLaw:
        """Rehydrate a law, refusing one that names no check."""
        law_id = _require_text(entry, "id", "law")
        return cls(
            law_id=law_id,
            title=_require_text(entry, "title", law_id),
            statement=_require_text(entry, "statement", law_id),
            check=_require_text(entry, "check", law_id),
        )


@dataclass(frozen=True, slots=True)
class Verdict:
    """The answer for one object: does it need birth, does it have one, is that right."""

    path: str
    object_kind: str
    birth_required: bool
    verdict: str
    reason: str
    authority: str


@dataclass(frozen=True, slots=True)
class ScopePolicy:
    """The whole policy, rehydrated and structurally usable."""

    policy_id: str
    kinds: tuple[Kind, ...]
    subject_rules: tuple[SubjectRule, ...]
    floors: tuple[Floor, ...]
    laws: tuple[ScopeLaw, ...]

    @classmethod
    def of(cls, document: Mapping[str, Any]) -> ScopePolicy:
        """Rehydrate a policy from a parsed declaration."""
        for section in ("kinds", "subject_resolution", "coverage_floors", "laws"):
            value = document.get(section)
            if not isinstance(value, list) or not value:
                raise BirthError(f"policy section {section!r} is absent or not a non-empty list")
        return cls(
            policy_id=_require_text(document, "policy_id", "policy"),
            kinds=tuple(Kind.of(entry) for entry in document["kinds"]),
            subject_rules=tuple(SubjectRule.of(e) for e in document["subject_resolution"]),
            floors=tuple(Floor.of(entry) for entry in document["coverage_floors"]),
            laws=tuple(ScopeLaw.of(entry) for entry in document["laws"]),
        )

    def kind(self, object_kind: str) -> Kind | None:
        """Return the declared kind with this name, or None."""
        for candidate in self.kinds:
            if candidate.object_kind == object_kind:
                return candidate
        return None

    def validate(self, implemented: frozenset[str]) -> list[str]:
        """Return every structural problem, refusing in both directions."""
        problems: list[str] = []
        claimed = {law.check for law in self.laws}
        for law in sorted(self.laws, key=lambda entry: entry.law_id):
            if law.check not in implemented:
                problems.append(
                    f"{law.law_id}: names check {law.check!r}, which is not implemented"
                )
        for orphan in sorted(implemented - claimed):
            problems.append(f"check {orphan!r} is implemented but no law claims it")
        return problems


# --- selector operators ---------------------------------------------------------------
#
# GENERIC OPERATORS ONLY. Each reads a field the source registries already carry; none
# names an object kind, a path or a value. The values live in the policy.


def _op_catch_all(_expected: Any, _obj: Mapping[str, Any], _ctx: Mapping[str, Any]) -> bool:
    return True


def _op_in_generated_registry(
    expected: Any, obj: Mapping[str, Any], ctx: Mapping[str, Any]
) -> bool:
    return (obj.get("path") in ctx["generated_paths"]) is bool(expected)


def _op_uga_lifecycle(expected: Any, obj: Mapping[str, Any], _ctx: Mapping[str, Any]) -> bool:
    return obj.get("lifecycle") == expected


def _op_uga_object_class(expected: Any, obj: Mapping[str, Any], _ctx: Mapping[str, Any]) -> bool:
    return obj.get("object_class") == expected


def _op_path_prefix(expected: Any, obj: Mapping[str, Any], _ctx: Mapping[str, Any]) -> bool:
    return str(obj.get("path", "")).startswith(str(expected))


def _op_path_suffix(expected: Any, obj: Mapping[str, Any], _ctx: Mapping[str, Any]) -> bool:
    return str(obj.get("path", "")).endswith(str(expected))


def _op_basename(expected: Any, obj: Mapping[str, Any], _ctx: Mapping[str, Any]) -> bool:
    return os.path.basename(str(obj.get("path", ""))) == expected


#: Every validation rule a kind may name, and the enforcement mode each one implements.
#: A kind's ``validation_rule`` is not decorative: BSP-L-01 refuses a rule that is not
#: implemented here, AND refuses a rule whose enforcement disagrees with the kind's own
#: ``enforcement`` field. Without that second half a kind could declare it forbids birth
#: while naming the rule that merely reports coverage, and the disagreement would never
#: surface.
VALIDATION_RULES: dict[str, str] = {
    "no_birth_record_exists": MANDATORY_ABSENCE,
    "birth_coverage_disclosed": DISCLOSED_ADOPTION,
    "governed_elsewhere": GOVERNED_ELSEWHERE,
    "not_required": NOT_REQUIRED,
}


#: Every selector operator a kind may name. BSP-L-01 refuses a selector naming an operator
#: absent from this mapping — which is how a new operator stays a code change while a new
#: kind stays a data change.
SELECTOR_OPERATORS: dict[str, Callable[[Any, Mapping[str, Any], Mapping[str, Any]], bool]] = {
    "catch_all": _op_catch_all,
    "in_generated_registry": _op_in_generated_registry,
    "uga_lifecycle": _op_uga_lifecycle,
    "uga_object_class": _op_uga_object_class,
    "path_prefix": _op_path_prefix,
    "path_suffix": _op_path_suffix,
    "basename": _op_basename,
}


def _selector_matches(kind: Kind, obj: Mapping[str, Any], ctx: Mapping[str, Any]) -> bool:
    """True when every operator in the kind's selector holds for this object."""
    for operator, expected in kind.selector.items():
        handler = SELECTOR_OPERATORS.get(operator)
        if handler is None or not handler(expected, obj, ctx):
            return False
    return True


def classify(policy: ScopePolicy, obj: Mapping[str, Any], ctx: Mapping[str, Any]) -> Kind | None:
    """Return the first kind whose selector matches, in declared order."""
    for kind in policy.kinds:
        if _selector_matches(kind, obj, ctx):
            return kind
    return None


# --- loading --------------------------------------------------------------------------


def repo_root() -> str:
    """Return the repository root, derived from this file's location."""
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _read_json(repo: str, relpath: str) -> Any:
    """Return the parsed JSON at ``relpath``, or None when it cannot be read."""
    try:
        with open(os.path.join(repo, relpath), encoding="utf-8") as handle:
            return json.load(handle)
    except (FileNotFoundError, IsADirectoryError, PermissionError, json.JSONDecodeError):
        return None


def load_policy(path: str | None = None) -> ScopePolicy:
    """Read, rehydrate and structurally validate the policy, or fail closed."""
    target = path or os.path.join(repo_root(), _POLICY)
    try:
        with open(target, encoding="utf-8") as handle:
            document = json.load(handle)
    except FileNotFoundError as error:
        raise BirthError(f"the birth scope policy is absent: {target}") from error
    except json.JSONDecodeError as error:
        raise BirthError(f"the birth scope policy is not valid JSON: {error}") from error
    if not isinstance(document, dict):
        raise BirthError("the birth scope policy is not an object")
    policy = ScopePolicy.of(document)
    problems = policy.validate(frozenset(SCOPE_LAW_CHECKS))
    if problems:
        raise BirthError("the policy and the implemented checks disagree: " + "; ".join(problems))
    return policy


def load_context(repo: str | None = None) -> dict[str, Any]:
    """Load the registries the selectors and laws read. Reads only."""
    repo = repo or repo_root()
    objects_doc = _read_json(repo, _OBJECTS) or {}
    entries = objects_doc.get("entries") or []
    objects = list(entries) if isinstance(entries, list) else list(entries.values())
    generated_doc = _read_json(repo, _GENERATED) or {}
    generated = generated_doc.get("entries") or []
    ledger = _read_json(repo, _LEDGER) or {}
    by_path: dict[str, Mapping[str, Any]] = {}
    by_basename: dict[str, list[str]] = {}
    for obj in objects:
        path = str(obj.get("path", ""))
        by_path[path] = obj
        by_basename.setdefault(os.path.basename(path), []).append(path)
    return {
        "repo": repo,
        "objects": objects,
        "by_path": by_path,
        "by_basename": by_basename,
        "generated_paths": {
            str(e.get("canonical_path")) for e in generated if isinstance(e, Mapping)
        },
        "births": dict(ledger.get("births") or {}),
    }


# --- subject resolution ---------------------------------------------------------------


def _split_urn(urn: str) -> tuple[str, str] | None:
    """Return ``(namespace, local_name)`` for a UCKO urn, or None when malformed."""
    parts = urn.split(":", 4)
    if len(parts) != 5:
        return None
    return parts[3], parts[4]


def resolve_subject(policy: ScopePolicy, urn: str) -> tuple[SubjectRule, str] | None:
    """Return the rule and the repository path a birth record names, or None."""
    split = _split_urn(urn)
    if split is None:
        return None
    namespace, local_name = split
    for rule in policy.subject_rules:
        if rule.namespace != namespace:
            continue
        # The pattern is declared as a regular expression, so it is matched as one. An
        # earlier draft stripped the anchor and compared prefixes, which silently failed
        # every escaped pattern (``^engine\.``) and reported zero resolved packages.
        try:
            if re.search(rule.local_name_pattern, local_name) is None:
                continue
        except re.error:
            continue
        if rule.path_from == "dots_to_slashes":
            return rule, local_name.replace(".", "/")
        if rule.path_from == "test_basename":
            return rule, local_name + ".py"
        if rule.path_from == "name_plus_md":
            return rule, local_name + ".md"
        if rule.path_from == "master_dir":
            return rule, os.path.join("00-MASTER", local_name)
        return None
    return None


def _subject_exists(repo: str, rule: SubjectRule, path: str, objects: Mapping[str, list]) -> bool:
    """True when the thing a birth record names is actually present."""
    if rule.path_from == "test_basename":
        # The registry index is the fast path, and the filesystem is the truth. A test
        # suite added in this change is on disk but not yet in the object registry, and
        # registry lag is a legitimate state — every other subject class here is resolved
        # against the filesystem, so resolving this one against the registry alone would
        # report a file that plainly exists as absent.
        if objects.get(path):
            return True
        for root, _dirs, files in os.walk(repo):
            if ".git" in root:
                continue
            if path in files:
                return True
        return False
    if rule.path_from == "dots_to_slashes":
        return os.path.isdir(os.path.join(repo, path))
    if rule.path_from == "master_dir":
        return os.path.isdir(os.path.join(repo, path))
    return os.path.exists(os.path.join(repo, path))


def _object_at(path: str, ctx: Mapping[str, Any]) -> Mapping[str, Any] | None:
    """Return the registry entry for a path, or None. Indexed, never scanned."""
    index = ctx.get("by_path")
    if isinstance(index, Mapping):
        return index.get(path)
    for obj in ctx["objects"]:
        if obj.get("path") == path:
            return obj
    return None


# --- the public capability ------------------------------------------------------------


def evaluate(path: str, policy: ScopePolicy, ctx: Mapping[str, Any]) -> Verdict:
    """Answer, for one governed object, whether its birth state is correct.

    Returns PASS when the requirement is satisfied, FAIL when it is violated, and
    EXCEPTION when birth is required but its adoption is deferred to a declared gap.
    """
    obj = _object_at(path, ctx)
    if obj is None:
        return Verdict(path, "", False, FAIL, "not a governed object", "")
    kind = classify(policy, obj, ctx)
    if kind is None:
        return Verdict(path, "", False, FAIL, "classifies to no declared kind", "")

    born = _born_paths(policy, ctx)
    is_born = path in born

    if kind.enforcement == MANDATORY_ABSENCE:
        if is_born:
            return Verdict(
                path,
                kind.object_kind,
                False,
                FAIL,
                "holds an independent birth record; its identity is its producer's",
                kind.authority,
            )
        return Verdict(path, kind.object_kind, False, PASS, kind.reason, kind.authority)

    if not kind.birth_required:
        return Verdict(path, kind.object_kind, False, PASS, kind.reason, kind.authority)

    if is_born:
        return Verdict(path, kind.object_kind, True, PASS, "birth record present", kind.authority)
    if kind.adoption == "DEFERRED" and kind.adoption_gap:
        return Verdict(
            path,
            kind.object_kind,
            True,
            EXCEPTION,
            f"birth required; adoption deferred under {kind.adoption_gap}",
            kind.authority,
        )
    return Verdict(
        path,
        kind.object_kind,
        True,
        FAIL,
        "birth required and no birth record exists",
        kind.authority,
    )


def _born_paths(policy: ScopePolicy, ctx: Mapping[str, Any]) -> set[str]:
    """Return the repository paths that a birth record names.

    Memoised on the context. ``evaluate`` is called once per governed object, so
    recomputing this per call turned a 6,079-object sweep into a quadratic scan.
    """
    # Keyed on the births themselves, never merely on presence. A caller that shallow-
    # copies the context and substitutes a different ledger would otherwise inherit this
    # cache and be answered about the ledger it replaced.
    key = frozenset(ctx["births"])
    cached = ctx.get("_born_paths")
    if isinstance(cached, tuple) and cached[0] == key:
        return cached[1]
    by_basename = ctx.get("by_basename") or {}
    paths: set[str] = set()
    for urn in ctx["births"]:
        resolved = resolve_subject(policy, urn)
        if resolved is None:
            continue
        rule, path = resolved
        if rule.path_from == "dots_to_slashes":
            paths.add(os.path.join(path, "__init__.py"))
        elif rule.path_from == "test_basename":
            paths.update(by_basename.get(path, []))
        else:
            paths.add(path)
    if isinstance(ctx, dict):
        ctx["_born_paths"] = (key, paths)
    return paths


def _births_by_subject_class(policy: ScopePolicy, ctx: Mapping[str, Any]) -> dict[str, int]:
    """Count birth records by the subject class they resolve to."""
    counts: dict[str, int] = {}
    for urn in ctx["births"]:
        resolved = resolve_subject(policy, urn)
        if resolved is None:
            continue
        counts[resolved[0].resolves_to] = counts.get(resolved[0].resolves_to, 0) + 1
    return counts


# --- the six laws ---------------------------------------------------------------------


def check_policy_is_structurally_usable(
    policy: ScopePolicy, ctx: Mapping[str, Any]
) -> tuple[str, ...]:
    """BSP-L-01 — every kind is complete and every selector operator is implemented."""
    del ctx
    violations: list[str] = []
    seen: set[str] = set()
    claimed_rules: set[str] = set()
    for kind in policy.kinds:
        if kind.object_kind in seen:
            violations.append(f"{kind.object_kind}: declared more than once")
        seen.add(kind.object_kind)
        for operator in kind.selector:
            if operator not in SELECTOR_OPERATORS:
                violations.append(
                    f"{kind.object_kind}: selector names operator {operator!r}, "
                    f"which is not implemented"
                )
        claimed_rules.add(kind.validation_rule)
        implements = VALIDATION_RULES.get(kind.validation_rule)
        if implements is None:
            violations.append(
                f"{kind.object_kind}: validation_rule {kind.validation_rule!r} is not implemented"
            )
        elif implements != kind.enforcement:
            violations.append(
                f"{kind.object_kind}: declares enforcement {kind.enforcement!r} but names "
                f"validation_rule {kind.validation_rule!r}, which implements {implements!r}"
            )
    for orphan in sorted(set(VALIDATION_RULES) - claimed_rules):
        violations.append(f"validation rule {orphan!r} is implemented but no kind claims it")
    return tuple(violations)


def check_classification_is_total(policy: ScopePolicy, ctx: Mapping[str, Any]) -> tuple[str, ...]:
    """BSP-L-02 — exactly one catch-all, declared last, and nothing unresolved."""
    violations: list[str] = []
    catch_alls = [k for k in policy.kinds if k.is_catch_all]
    if len(catch_alls) != 1:
        violations.append(f"exactly one kind must declare catch_all; {len(catch_alls)} do")
    elif policy.kinds[-1] is not catch_alls[0]:
        violations.append(
            f"the catch-all kind {catch_alls[0].object_kind} is not declared last, so kinds "
            f"below it can never be reached"
        )
    unresolved = [
        str(obj.get("path")) for obj in ctx["objects"] if classify(policy, obj, ctx) is None
    ]
    if unresolved:
        violations.append(
            f"{len(unresolved)} governed objects classify to no kind, first: {unresolved[0]}"
        )
    return tuple(violations)


def check_no_derived_object_is_born(policy: ScopePolicy, ctx: Mapping[str, Any]) -> tuple[str, ...]:
    """BSP-L-03 — a generated or derived object may not hold an independent birth."""
    born = _born_paths(policy, ctx)
    violations: list[str] = []
    for obj in ctx["objects"]:
        kind = classify(policy, obj, ctx)
        if kind is None or kind.enforcement != MANDATORY_ABSENCE:
            continue
        path = str(obj.get("path"))
        if path in born:
            violations.append(
                f"{path}: classified {kind.object_kind} and holds an independent birth record"
            )
    return tuple(violations)


def check_every_birth_subject_may_be_born(
    policy: ScopePolicy, ctx: Mapping[str, Any]
) -> tuple[str, ...]:
    """BSP-L-04 — every birth names something that exists and may be born."""
    violations: list[str] = []
    for urn in sorted(ctx["births"]):
        resolved = resolve_subject(policy, urn)
        if resolved is None:
            violations.append(f"{urn}: no declared subject_resolution rule resolves it")
            continue
        rule, path = resolved
        if not _subject_exists(ctx["repo"], rule, path, ctx.get("by_basename") or {}):
            violations.append(f"{urn}: names {path}, which does not exist")
            continue
        obj = _object_at(path, ctx)
        if obj is None:
            continue
        kind = classify(policy, obj, ctx)
        if kind is not None and kind.enforcement == MANDATORY_ABSENCE:
            violations.append(
                f"{urn}: names {path}, which is {kind.object_kind} and may not be born"
            )
    return tuple(violations)


def check_adoption_is_disclosed(policy: ScopePolicy, ctx: Mapping[str, Any]) -> tuple[str, ...]:
    """BSP-L-05 — a kind requiring birth must disclose its adoption state."""
    del ctx
    violations: list[str] = []
    for kind in policy.kinds:
        if not kind.birth_required:
            continue
        if not kind.adoption:
            violations.append(f"{kind.object_kind}: requires birth and discloses no adoption state")
        elif kind.adoption == "DEFERRED" and not kind.adoption_gap:
            violations.append(
                f"{kind.object_kind}: adoption is DEFERRED and names no gap, so the "
                f"deferral is undisclosed"
            )
    return tuple(violations)


def check_coverage_does_not_regress(policy: ScopePolicy, ctx: Mapping[str, Any]) -> tuple[str, ...]:
    """BSP-L-06 — adoption may rise and may hold; it may not fall."""
    measured = _births_by_subject_class(policy, ctx)
    violations: list[str] = []
    for floor in policy.floors:
        actual = measured.get(floor.subject_class, 0)
        if actual < floor.born_at_baseline:
            violations.append(
                f"{floor.subject_class}: {actual} birth records, below the declared "
                f"floor of {floor.born_at_baseline}"
            )
    return tuple(violations)


#: Every check the policy may name. The policy refuses a law naming a check absent from
#: this mapping, and a check here that no law claims.
SCOPE_LAW_CHECKS: dict[str, Callable[[ScopePolicy, Mapping[str, Any]], tuple[str, ...]]] = {
    "policy_is_structurally_usable": check_policy_is_structurally_usable,
    "classification_is_total": check_classification_is_total,
    "no_derived_object_is_born": check_no_derived_object_is_born,
    "every_birth_subject_may_be_born": check_every_birth_subject_may_be_born,
    "adoption_is_disclosed": check_adoption_is_disclosed,
    "coverage_does_not_regress": check_coverage_does_not_regress,
}


def assess_scope(
    policy: ScopePolicy, ctx: Mapping[str, Any]
) -> list[tuple[str, str, tuple[str, ...]]]:
    """Measure every law, returning ``(law_id, title, violations)`` in declared order."""
    return [
        (law.law_id, law.title, SCOPE_LAW_CHECKS[law.check](policy, ctx)) for law in policy.laws
    ]


def summarize(policy: ScopePolicy, ctx: Mapping[str, Any]) -> dict[str, Any]:
    """Return the population summary the gate reports."""
    counts: dict[str, int] = {}
    verdicts: dict[str, int] = {PASS: 0, FAIL: 0, EXCEPTION: 0}
    for obj in ctx["objects"]:
        kind = classify(policy, obj, ctx)
        name = kind.object_kind if kind is not None else ""
        counts[name] = counts.get(name, 0) + 1
    for path in sorted({str(o.get("path")) for o in ctx["objects"]}):
        verdicts[evaluate(path, policy, ctx).verdict] += 1
    return {
        "policy_id": policy.policy_id,
        "objects": len(ctx["objects"]),
        "births": len(ctx["births"]),
        "kinds": {k: counts.get(k, 0) for k in (kind.object_kind for kind in policy.kinds)},
        "verdicts": verdicts,
        "births_by_subject_class": _births_by_subject_class(policy, ctx),
    }


__all__ = [
    "EXCEPTION",
    "FAIL",
    "PASS",
    "SCOPE_LAW_CHECKS",
    "SELECTOR_OPERATORS",
    "VALIDATION_RULES",
    "Floor",
    "Kind",
    "ScopeLaw",
    "ScopePolicy",
    "SubjectRule",
    "Verdict",
    "assess_scope",
    "classify",
    "evaluate",
    "load_context",
    "load_policy",
    "resolve_subject",
    "summarize",
]
