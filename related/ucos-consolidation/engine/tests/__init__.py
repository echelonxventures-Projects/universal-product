"""Shared test infrastructure for the repository's two families of unproven refusal.

WHY THIS LIVES HERE AND EXACTLY ONCE. Twenty-three validation modules across `data/`,
`infrastructure/` and `platform/` declare some five hundred blocking checks between them,
and every one of them was observed only PASSING. A check whose failure arm never executes
is indistinguishable from ``return self._passed()``: it would satisfy the suite exactly as
well while policing nothing at all. That is the defect UEC-L-14 names one layer up — no
verifier is trusted on the strength of being named — and it is the same argument, so it is
authored once (UCKP-ART-03) in the package every one of those consumers already depends on
for ``engine.validation``, and referenced from there (UCKP-ART-18).

``refusal_witnesses`` DERIVES a witness for each check rather than enumerating them by
hand, because a hand table is a second authoring of what the checks already say and goes
stale the moment a check is added (ART-15: no conclusion rests on a hardcoded assumption).
It mutates one declared field of a valid subject at a time, observes which checks that
offends, and reports the first mutation that reached each failure arm. What it cannot reach
it names, and the caller fails on the names.

THE SECOND FAMILY IS THE CONSTRUCTOR GUARD, and it is the same defect wearing different
clothes. Across the repository, 609 `raise` statements were never executed — 149 of them in
a ``__post_init__`` and 33 in a ``from_mapping`` — and a guard that never fires polices
nothing exactly as a check that never fails polices nothing. ``guard_witnesses`` proves them
by IDENTITY rather than by message: every mutation that raises is attributed to a `raise`
statement through ``exc.__traceback__``'s deepest frame in the class's own file, so a guard
counts as proven only when that precise statement executed. Nothing is matched on the text
of an error, which means a reworded message cannot silently retire a proof.
"""

from __future__ import annotations

import ast
import inspect
import sys
import textwrap
from collections.abc import Iterator, Mapping, Sequence
from dataclasses import fields, is_dataclass, replace
from enum import Enum
from typing import Any

#: A value that is well-formed as a string and a member of no declared vocabulary, so a
#: check that admits an enumeration refuses it while a check that only wants non-empty
#: text accepts it. Both outcomes are informative; neither is an accident of formatting.
HOSTILE = "ucos.invented.value"

#: An object of no declared type at all. A ``__post_init__`` guard is written against a TYPE
#: as often as against a value — ``not isinstance(x, int)`` has no hostile INTEGER — so the
#: search has to be able to offer something that is not any of the declared types.
ALIEN = object()

#: The three places a constitutional dataclass in this repository puts a guard: the constructor
#: it validates itself in, and the two assimilation entry points UCKP-ART-19 requires it to
#: offer. A class that guards somewhere else is not covered by ``guarded_methods`` and the
#: caller has to name that method, which is the honest outcome — an unnamed method would be
#: silently unproven instead.
GUARD_METHODS = ("__post_init__", "from_mapping", "from_sequence")


def _candidates(value: Any) -> tuple[Any, ...]:
    """Hostile values for one field, chosen from the type of what is already there.

    Derived from the subject, never declared: a field added to a subject dataclass is
    mutated by this driver on the next run with no edit here.
    """
    if isinstance(value, bool):  # before int — bool IS an int in Python
        return (not value,)
    if isinstance(value, Enum):
        # BEFORE str, BECAUSE A STRING ENUM IS A STRING. `class Verdict(str, Enum)` satisfies
        # `isinstance(value, str)`, so an arm placed after that test would never see one, and the
        # OTHER MEMBERS OF THE SAME ENUMERATION are what a mode guard needs: `if self.model is
        # PERPETUAL and self.term_days` is opened only by another DECLARED mode, never by junk.
        return (*(member for member in type(value) if member is not value), value.value)
    if isinstance(value, str):
        # A 64-character non-hex string is the interesting hostile digest: it defeats the
        # alphabet test while satisfying any check that only measures length.
        return ("", HOSTILE, "z" * 64) if len(value) == 64 else ("", HOSTILE)
    if isinstance(value, tuple):
        # THREE HOSTILE SHAPES AND NOT ONE. An empty collection, a collection of the wrong
        # members, and a collection one of whose members is empty are different offences:
        # `any(not t.strip() for t in tags)` is reached only by the third, and truncating to
        # the first member is what reaches a check that reads a chain's head but wants its
        # tail (a lineage rooted correctly that never closes to its anchor).
        return ((), (HOSTILE,), ("",), value[:1]) if value else ((HOSTILE,), ("",))
    if isinstance(value, list):
        # The same three shapes in the concrete type a raw JSON document actually carries. A
        # list is not a tuple and `isinstance(value, tuple)` above never sees one, which is why
        # this arm exists rather than a widened test: a declared field keeps the type it
        # declared, and a mutation that changed tuple to list would be testing the container.
        return ([], [HOSTILE], [""], value[:1]) if value else ([HOSTILE], [""])
    if isinstance(value, Mapping):
        return ({},)
    if isinstance(value, int):
        return (-1,)
    return ()


def _vocabulary(checks: Sequence[Any]) -> tuple[str, ...]:
    """Every string the checks' own modules declare in a module-level collection.

    A GUARD OPENS ON A DECLARED VALUE, NEVER ON A HOSTILE ONE. ``if lifecycle_state in
    _ACTIVE_OR_BEYOND and not schema_described`` is unreachable by any mutation this driver
    would invent, because the arm is behind a membership test that only a member passes. So
    the vocabulary is read out of the module that declares it — the enumerations, the state
    sets, the relationship names — which keeps the search derived from the declared universe
    (ART-15) instead of from a table somebody has to remember to update.
    """
    words: set[str] = set()
    for module_name in {type(check).__module__ for check in checks}:
        module = sys.modules.get(module_name)
        for name, value in vars(module or object()).items():
            if name.startswith("__") or not isinstance(value, frozenset | set | tuple | list):
                continue
            if value and all(isinstance(member, str) for member in value):
                words |= set(value)
    return tuple(sorted(words))


def _refused_by(subject: Any, checks: Sequence[Any]) -> frozenset[str]:
    """The ids of the checks that refuse ``subject``, evaluated one predicate at a time.

    Each check is called directly rather than through the engine: the engine's ordering and
    report assembly are proven elsewhere, and a check that raises on a mutation of an
    unrelated field must not take the whole sweep down with it.
    """
    refused: set[str] = set()
    for check in checks:
        try:
            if not check.evaluate(subject).passed:
                refused.add(check.check_id)
        except Exception:  # noqa: S112 — a raise is not a refusal; this mutation proves nothing
            continue
    return frozenset(refused)


def refusal_witnesses(subject: Any, checks: Sequence[Any]) -> dict[str, tuple[str, Any]]:
    """Map each check id that can be made to fail to the mutation that did it.

    Three passes, cheapest first, each paying only for what the one before it left unproven:
    type-derived mutations of one field; then values drawn from the modules' own declared
    vocabularies; then pairs, for the arms that sit behind a guard. The last two passes
    evaluate ONLY the checks still unproven, which is what keeps a search over a few hundred
    mutations from becoming a search over all of them times every check.
    """
    baseline = _refused_by(subject, checks)
    assert not baseline, f"the subject must be valid first: it already refused {sorted(baseline)}"

    declared = [field.name for field in fields(subject)]
    witnesses: dict[str, tuple[str, Any]] = {}
    observed: list[tuple[str, Any]] = []
    quiet: list[tuple[str, Any]] = []

    def sweep(mutations: list[tuple[str, Any]], against: Sequence[Any]) -> None:
        for name, candidate in mutations:
            try:
                refused = _refused_by(replace(subject, **{name: candidate}), against)
            except (TypeError, ValueError):  # the dataclass itself rejected the value
                continue
            observed.append((name, candidate))
            if not refused:
                quiet.append((name, candidate))
            for check_id in refused:
                witnesses.setdefault(check_id, (name, candidate))

    def unproven() -> tuple[Any, ...]:
        return tuple(check for check in checks if check.check_id not in witnesses)

    sweep(
        [
            (name, candidate)
            for name in declared
            for candidate in _candidates(getattr(subject, name))
        ],
        checks,
    )
    if remaining := unproven():
        sweep(
            [
                (name, word)
                for name in declared
                if isinstance(getattr(subject, name), str)
                for word in _vocabulary(checks)
                if word != getattr(subject, name)
            ],
            remaining,
        )

    # A GUARDED ARM NEEDS ITS GUARD OPENED FIRST. `if kind == RELATIONAL: if not
    # references_entity:` is unreachable by mutating either field alone — the kind selects
    # the mode and offends nothing by itself, and the empty reference is only read inside
    # that mode. The mutations that offended NOTHING are therefore the candidate mode
    # selectors, and pairing each with every other observed mutation opens the guarded arms
    # without searching the whole product of the fields.
    for selector in list(quiet):
        remaining = unproven()
        if not remaining:
            break
        for other in list(observed):
            if other[0] == selector[0]:
                continue
            paired = {selector[0]: selector[1], other[0]: other[1]}
            try:
                refused = _refused_by(replace(subject, **paired), remaining)
            except (TypeError, ValueError):
                continue
            for check_id in refused:
                witnesses.setdefault(check_id, (f"{selector[0]}+{other[0]}", paired))
            if refused:
                remaining = unproven()
                if not remaining:
                    break
    return witnesses


def assert_every_check_can_refuse(
    subject: Any, checks: Sequence[Any], *, unreachable: Sequence[str] = ()
) -> dict[str, tuple[str, Any]]:
    """Every declared check refuses something, so none of them is decoration.

    ``unreachable`` names check ids the caller has ARGUED cannot be reached by mutating one or
    two declared fields of a valid subject — a check that compares a pure function with itself,
    or one whose condition another check's guard already guarantees. Naming one is a claim in the
    test that a reader can check and disagree with; the alternative is an arm that quietly went
    unproven, which is the whole defect this driver exists to catch.
    """
    witnesses = refusal_witnesses(subject, checks)
    unproven = sorted({check.check_id for check in checks} - set(witnesses) - set(unreachable))
    assert not unproven, (
        "no single- or paired-field mutation of a valid subject made these checks fail, so "
        f"their refusal arms are unproven and may be unreachable: {unproven}"
    )
    return witnesses


# --- Constructor and assimilation guards ------------------------------------------------


def _valid_variants(value: Any, limit: int = 8) -> tuple[Any, ...]:
    """WELL-FORMED alternatives to a nested dataclass, for the guards that read INTO a member.

    ``a price book may not mix currencies`` is offended by a ``Money`` that the ``Money`` class
    itself is perfectly happy with, so the value the outer guard needs is not malformed — it is
    valid and wrong. Anything the inner class refuses is discarded here rather than reported,
    because an inner refusal proves an inner guard and this is the outer one's search.
    """
    if not is_dataclass(value) or isinstance(value, type):
        return ()
    variants: list[Any] = []
    for field in fields(value):
        if not field.init:
            continue
        for candidate in _candidates(getattr(value, field.name)):
            try:
                variants.append(replace(value, **{field.name: candidate}))
            except Exception:  # noqa: BLE001,S112 — the inner class refused; not this search's arm
                continue
            if len(variants) >= limit:
                return tuple(variants)
    return tuple(variants)


def _guard_candidates(value: Any) -> tuple[Any, ...]:
    """Hostile values for one constructor argument.

    A ``__post_init__`` guard is written against a TYPE and a RANGE rather than against a
    vocabulary: ``isinstance(x, bool) or not isinstance(x, int) or x < 1`` is three arms, and
    opening all three needs ``True``, a non-integer and a negative. ``None`` and `ALIEN` are
    therefore offered whatever the field holds, and a duplicate member is offered for every
    non-empty sequence, because ``if member in seen: raise`` is the most common guard in the
    repository and no mutation of a single member can reach it.
    """
    universal: tuple[Any, ...] = (None, ALIEN)
    if isinstance(value, bool):  # before int — bool IS an int in Python
        return (*universal, not value, 0, "")
    if isinstance(value, Enum):  # before str — a string enum is a string
        return (*universal, *_candidates(value))
    if isinstance(value, int):
        return (*universal, True, -1, 0, "1", 2**63)
    if isinstance(value, str):
        return (*universal, "", HOSTILE, 0, ("x",), "z" * 64 if len(value) == 64 else " ")
    if isinstance(value, Mapping):
        candidates = [*universal, {}, "not-a-mapping", (), {HOSTILE: HOSTILE}]
        if value:
            key = next(iter(value))
            candidates += [{**value, key: variant} for variant in _valid_variants(value[key])]
        return tuple(candidates)
    if isinstance(value, tuple):
        candidates = [*universal, (), (HOSTILE,), ("",), (None,), (ALIEN,), "not-a-sequence"]
        if value:
            candidates += [value[:1], (*value, value[0]), (*value[:1], *value[:1])]
            candidates += [(*value[:1], variant) for variant in _valid_variants(value[0])]
        return tuple(candidates)
    if isinstance(value, Sequence) and not isinstance(value, str | bytes):
        # A LIST IS THE SHAPE A DOCUMENT ARRIVES IN, and it is not a tuple. The same offences
        # apply — empty, wrong member, duplicated member, truncated — but a mutation that also
        # changed the container type would be testing the container instead of the guard.
        members = list(value)
        candidates = [*universal, [], [HOSTILE], [""], [None], [ALIEN], "not-a-sequence"]
        if members:
            candidates += [members[:1], [*members, members[0]], members[:1] + members[:1]]
            candidates += [[*members[:1], variant] for variant in _valid_variants(members[0])]
        return tuple(candidates)
    if is_dataclass(value) and not isinstance(value, type):
        return (*universal, "not-a-dataclass", 0, *_valid_variants(value))
    return universal


def _raise_spans(func: Any) -> dict[int, int]:
    """Every ``raise`` statement ``func`` declares, as first line → last line.

    THE SPAN AND NOT THE LINE. A multi-line ``raise Error("...", context=...)`` reports its
    traceback against whichever line the interpreter was executing, while coverage and the AST
    both name the first; accepting the whole span makes the attribution independent of that
    detail instead of dependent on the formatter.
    """
    try:
        lines, first = inspect.getsourcelines(func)
    except (OSError, TypeError):
        return {}
    try:
        tree = ast.parse(textwrap.dedent("".join(lines)))
    except SyntaxError:  # pragma: no cover — a class body that does not parse alone
        return {}
    return {
        first + node.lineno - 1: first + (node.end_lineno or node.lineno) - 1
        for node in ast.walk(tree)
        if isinstance(node, ast.Raise)
    }


def _attributed(exc: BaseException, filename: str, spans: Mapping[int, int]) -> int | None:
    """Which declared ``raise`` this exception came out of, or None if it came from elsewhere.

    The DEEPEST frame in the class's own file is the one that matters: when a nested class
    refuses first, its own file holds the raise and the outer frame holds only the call, so an
    inner refusal cannot be miscredited to an outer guard. A line that is in the file but in no
    declared span — an ``AttributeError`` from a mapping of the wrong member type, say — proves
    nothing and is reported as nothing.
    """
    line: int | None = None
    traceback = exc.__traceback__
    while traceback is not None:
        if traceback.tb_frame.f_code.co_filename == filename:
            line = traceback.tb_lineno
        traceback = traceback.tb_next
    if line is None:
        return None
    return next((start for start, end in spans.items() if start <= line <= end), None)


def _declared_raises(cls: type, methods: Sequence[str]) -> dict[int, tuple[int, str]]:
    """Union of the ``raise`` spans of the named methods, as first line → (last line, method)."""
    declared: dict[int, tuple[int, str]] = {}
    for name in methods:
        member = getattr(cls, name, None)
        if member is None:
            continue
        for start, end in _raise_spans(member).items():
            declared[start] = (end, name)
    return declared


def guarded_methods(cls: type, methods: Sequence[str] = GUARD_METHODS) -> tuple[str, ...]:
    """Which of ``methods`` this class both declares AND raises inside.

    THE COMPLETENESS TEST'S HALF OF THE DERIVATION. A driver that is handed its subjects by name
    proves whatever it was handed and stays silent about a class nobody remembered; asking the
    package which of its classes declare a guard turns that silence into a failure. A method that
    exists and never raises is not reported, because there is nothing there to prove.
    """
    return tuple(
        name
        for name in methods
        if getattr(cls, name, None) is not None and _raise_spans(getattr(cls, name))
    )


def guard_witnesses(
    subject: Any, *, methods: Sequence[str] = ("__post_init__",)
) -> dict[int, tuple[str, Any]]:
    """Map each declared ``raise`` line to the single field mutation that reached it.

    Singles first, then pairs seeded by the mutations that raised NOTHING, for the same reason
    the refusal driver needs them: ``if self.kind is DERIVED and not self.sources`` is opened by
    no mutation of either field alone.
    """
    cls = type(subject)
    filename = inspect.getsourcefile(cls) or ""
    declared = _declared_raises(cls, methods)
    spans = {start: end for start, (end, _) in declared.items()}
    witnesses: dict[int, tuple[str, Any]] = {}
    observed: list[tuple[str, Any]] = []
    quiet: list[tuple[str, Any]] = []

    def attempt(mutation: Mapping[str, Any], label: str) -> bool:
        """True when the subject ACCEPTED the mutation, so it is a candidate mode selector."""
        try:
            replace(subject, **mutation)
        except BaseException as exc:  # noqa: BLE001 — every refusal is a candidate witness
            line = _attributed(exc, filename, spans)
            if line is not None:
                witnesses.setdefault(line, (label, dict(mutation)))
            return False
        return True

    for field in fields(subject):
        if not field.init:
            continue
        for candidate in _guard_candidates(getattr(subject, field.name)):
            observed.append((field.name, candidate))
            if attempt({field.name: candidate}, field.name):
                quiet.append((field.name, candidate))

    for selector in quiet:
        if len(witnesses) == len(declared):
            break
        for other in observed:
            if other[0] == selector[0]:
                continue
            paired = {selector[0]: selector[1], other[0]: other[1]}
            attempt(paired, f"{selector[0]}+{other[0]}")
    return witnesses


def assert_every_guard_can_refuse(
    subject: Any,
    *modes: Any,
    methods: Sequence[str] = ("__post_init__",),
    unreachable: Sequence[int] = (),
) -> dict[int, tuple[str, Any]]:
    """Every ``raise`` the subject's constructor declares is reached by some hostile argument.

    EXTRA SUBJECTS ARE MODES, NOT REPETITION. ``if self.breach_effect is REQUIRES_APPROVAL and
    not self.approval_role`` cannot be reached from a policy that already names a role and
    already requires approval — every single mutation lands on the earlier guard instead — but it
    falls to one mutation of a policy in the other mode. A class with modes needs one valid
    instance per mode, which is what the fixtures already hold.

    ``unreachable`` takes LINE NUMBERS of guards a caller has argued are unreachable by argument
    mutation — a guard on a member no mutation of a DECLARED value can forge. Naming one is a
    claim in the test that a reader can check, which is the point: the alternative is a guard
    that quietly went unproven.
    """
    cls = type(subject)
    declared = _declared_raises(cls, methods)
    witnesses: dict[int, tuple[str, Any]] = {}
    for mode in (subject, *modes):
        if len(witnesses) == len(declared):
            break
        for line, witness in guard_witnesses(mode, methods=methods).items():
            witnesses.setdefault(line, witness)
    unproven = sorted(set(declared) - set(witnesses) - set(unreachable))
    assert not unproven, (
        f"{cls.__module__}.{cls.__qualname__} declares guards no single- or paired-argument "
        "mutation of a valid instance could reach, so they may be unreachable — "
        f"{inspect.getsourcefile(cls)} lines {unproven}"
    )
    return witnesses


def assert_assimilation_is_invertible_and_guarded(
    subject: Any,
    *,
    project: str = "to_dict",
    assimilate: str = "from_mapping",
    document: Any = None,
    invertible: bool = True,
    unreachable: Sequence[int] = (),
) -> dict[int, tuple[str, Any]]:
    """``from_mapping(to_dict(x)) == x``, and every guard in ``from_mapping`` fires.

    UCKP-ART-19 requires assimilation to be invertible, and the pair of methods every one of
    these dataclasses declares is where that promise is kept or broken. Round-tripping the
    subject exercises the projection; then the projected mapping is attacked one place at a time,
    which is exactly the shape of the malformed document ``from_mapping`` exists to refuse. The
    whole argument is attacked too, because ``if not isinstance(raw, Mapping)`` is reachable no
    other way.

    ``document`` supplies the assimilation input explicitly, for the classes where ``to_dict`` is
    a REPORT and not the inverse of ``from_mapping`` — a projection that computes coverage and
    concentration is not the specification the object was assimilated from, and asserting they
    round-trip would assert something the class never promised. Passing it also turns
    invertibility off unless the caller asks for it, because the caller has just said these two
    methods are not a pair.
    """
    cls = type(subject)
    filename = inspect.getsourcefile(cls) or ""
    raw = getattr(subject, project)() if document is None else document
    restored = getattr(cls, assimilate)(raw)
    if invertible and document is None:
        assert restored == subject, (
            f"{cls.__qualname__}.{project} then .{assimilate} did not return the same object, so "
            f"the projection loses information: {restored!r} != {subject!r}"
        )
    declared = _declared_raises(cls, (assimilate,))
    spans = {start: end for start, (end, _) in declared.items()}
    witnesses: dict[int, tuple[str, Any]] = {}

    def attempt(argument: Any, label: str) -> None:
        try:
            getattr(cls, assimilate)(argument)
        except BaseException as exc:  # noqa: BLE001 — every refusal is a candidate witness
            line = _attributed(exc, filename, spans)
            if line is not None:
                witnesses.setdefault(line, (label, argument))

    for argument in (None, ALIEN, "not-a-mapping", (), 0):
        attempt(argument, "the whole document")
    for label, mutated in document_mutations(raw):
        if len(witnesses) == len(declared):
            break
        attempt(mutated, label)

    unproven = sorted(set(declared) - set(witnesses) - set(unreachable))
    assert not unproven, (
        f"{cls.__module__}.{cls.__qualname__}.{assimilate} declares guards that no removal or "
        "corruption of one projected key could reach, so they may be unreachable — "
        f"{filename} lines {unproven}"
    )
    return witnesses


def assert_sequence_assimilation_is_guarded(
    cls: type,
    members: Sequence[Any],
    *,
    assimilate: str = "from_sequence",
    unreachable: Sequence[int] = (),
) -> dict[int, tuple[str, Any]]:
    """Every guard in a register's ``from_sequence`` fires for some corrupted member list.

    A register assimilates many documents at once, so its guards are the ones no single document
    can offend: a member that is not a mapping, a duplicate id, an empty roll. The corruptions
    are the same one-place corruptions, applied to the list.
    """
    filename = inspect.getsourcefile(cls) or ""
    declared = _declared_raises(cls, (assimilate,))
    spans = {start: end for start, (end, _) in declared.items()}
    witnesses: dict[int, tuple[str, Any]] = {}

    def attempt(argument: Any, label: str) -> None:
        try:
            getattr(cls, assimilate)(argument)
        except BaseException as exc:  # noqa: BLE001 — every refusal is a candidate witness
            line = _attributed(exc, filename, spans)
            if line is not None:
                witnesses.setdefault(line, (label, argument))

    for argument in (None, ALIEN, "not-a-sequence", 0, [ALIEN], [None], [""]):
        attempt(argument, "the whole roll")
    for label, mutated in document_mutations(list(members)):
        if len(witnesses) == len(declared):
            break
        attempt(mutated, label)

    unproven = sorted(set(declared) - set(witnesses) - set(unreachable))
    assert not unproven, (
        f"{cls.__module__}.{cls.__qualname__}.{assimilate} declares guards that no corruption of "
        f"the member list could reach, so they may be unreachable — {filename} lines {unproven}"
    )
    return witnesses


# --- Analyzer failure arms --------------------------------------------------------------
#
# THE THIRD FAMILY DOES NOT RAISE AND DOES NOT RETURN A BOOLEAN. An analyzer reads a document
# of declared facts and returns one finding per invariant, `passed(...)` or `failed(...)`, and
# a `failed(...)` arm that never executes is the same unproven refusal in a third costume: the
# analyzer would report a clean commercial position for a target that has none. The declared
# universe here is the set of ids that appear as the first argument of a failure constructor,
# read out of the analyzers' own source; the search is every one-key corruption of the fact
# document. Neither side is written by hand.

#: The names a failure constructor goes by in this repository. Read from the call site rather
#: than from the returned object, because the id of an arm that never ran is observable only in
#: the source. A name absent here is a family this instrument does not yet claim to cover.
FAILURE_CONSTRUCTORS = frozenset({"failed", "failure", "_failed", "fail", "blocking", "_blocking"})


def declared_failure_ids(*modules: Any) -> frozenset[str]:
    """Every check id some ``failed("...", …)`` call in these modules names."""
    ids: set[str] = set()
    for module in modules:
        try:
            tree = ast.parse(inspect.getsource(module))
        except (OSError, TypeError, SyntaxError):
            continue
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call) or not node.args:
                continue
            func = node.func
            name = func.attr if isinstance(func, ast.Attribute) else getattr(func, "id", "")
            first = node.args[0]
            if name in FAILURE_CONSTRUCTORS and isinstance(first, ast.Constant):
                if isinstance(first.value, str):
                    ids.add(first.value)
    return frozenset(ids)


def _brief(value: Any) -> str:
    """A mutation label short enough to read in a failure message."""
    text = "ALIEN" if value is ALIEN else repr(value)
    return text if len(text) <= 40 else text[:37] + "..."


def _document_words(document: Any) -> frozenset[str]:
    """Every string the compliant document itself contains, keys and leaves alike.

    THE CHEAPEST DECLARED VOCABULARY IS THE SUBJECT. A guard that cross-references two facts —
    ``the policy governing this package denies it`` — is opened by moving a value the document
    already declares somewhere it does not belong, and no module needs to be consulted to find
    such a value. It is free, it is derived, and it goes stale only if the fixture does.
    """
    if isinstance(document, str):
        return frozenset({document})
    if isinstance(document, Mapping):
        words = {str(key) for key in document}
        for value in document.values():
            words |= _document_words(value)
        return frozenset(words)
    if isinstance(document, Sequence) and not isinstance(document, bytes):
        words: set[str] = set()
        for member in document:
            words |= _document_words(member)
        return frozenset(words)
    return frozenset()


def _declared_words(*modules: Any) -> tuple[str, ...]:
    """Every string these modules declare: constants, members of collections, Enum values.

    A GUARD OPENS ON A DECLARED VALUE, NEVER ON A HOSTILE ONE — the same argument
    ``_vocabulary`` makes for the check suites, in the shape a fact document takes. ``an action
    no policy governs is refused`` is proven only by a policy that DOES govern the probe action,
    and that action's name is a constant in the analyzer's own module. Junk cannot reach it and
    a hand table would go stale; the module is asked instead.
    """
    words: set[str] = set()
    for module in modules:
        for name, value in vars(module).items():
            if name.startswith("__"):
                continue
            if isinstance(value, str):
                words.add(value)
            elif isinstance(value, frozenset | set | tuple | list):
                words |= {member for member in value if isinstance(member, str)}
            elif isinstance(value, type) and issubclass(value, Enum):
                words |= {member.value for member in value if isinstance(member.value, str)}
    return tuple(sorted(words))


#: Returned instead of a mutated object when the mutation could not be built at all. A
#: corruption is offered from inside a generator, and a constructor that refuses it must not end
#: the sweep for every arm that came after.
_UNAVAILABLE = object()


def _swapped(subject: Any, field: str, value: Any) -> Any:
    """``dataclasses.replace`` that declines instead of raising."""
    try:
        return replace(subject, **{field: value})
    except Exception:  # noqa: BLE001 — an unbuildable corruption is simply not offered
        return _UNAVAILABLE


def _dataclass_mutations(
    document: Any,
    path: tuple[str, ...],
    offer: Any,
    candidates: Any,
    structural: bool,
) -> Iterator[tuple[str, Any]]:
    """Every one-place corruption of a PARSED document.

    A PARSED DECLARATION IS A DOCUMENT ONE LAYER UP, and it has to be corrupted there. A strict
    parser refuses most corruptions of the JSON before any verdict is computed — a missing
    required key is a fault, not a finding — so an arm of ``validate`` that reads a field the
    parser also checks is unreachable from the bytes and reachable from the object. A field
    cannot be removed from a dataclass, so there is no removal arm; otherwise this is the mapping
    case with ``replace`` in place of ``{**document, key: ...}``.

    DIRECT CORRUPTIONS OF EVERY FIELD COME BEFORE ANY RECURSION, which the mapping case does not
    do, because here the subtrees are of wildly unequal size: a declaration with a hundred and
    fifteen fields has one field holding a thousand parsed rows, and depth-first order would
    spend an entire budget inside it before offering the ninety-ninth field its first corruption.
    """
    swaps = [(field.name, getattr(document, field.name, None)) for field in fields(document)]
    for name, value in swaps:
        label = ".".join((*path, name))
        for candidate in offer(value):
            if (mutated := _swapped(document, name, candidate)) is not _UNAVAILABLE:
                yield f"{label}={_brief(candidate)}", mutated
    for name, value in swaps:
        for inner_label, inner in document_mutations(
            value, path=(*path, name), candidates=candidates, structural=structural
        ):
            if (mutated := _swapped(document, name, inner)) is not _UNAVAILABLE:
                yield inner_label, mutated


def document_mutations(
    document: Any,
    *,
    path: tuple[str, ...] = (),
    candidates: Any = None,
    structural: bool = True,
) -> Iterator[tuple[str, Any]]:
    """Every one-place corruption of a nested fact document, lazily and labelled by path.

    A fact document is mappings and sequences all the way down, and an analyzer reads it one
    key at a time, so the corruptions that matter are: a key removed, a key replaced by
    something hostile, a member removed, a member duplicated, a member NEARLY duplicated — at
    every depth. It is a GENERATOR because the caller stops as soon as every declared arm has
    been reached; the whole product is available but is almost never paid for.

    ``candidates`` overrides where hostile values come from, so the caller can run a second,
    narrower pass over the same shape — declared vocabulary instead of type-derived junk —
    without re-paying for the first. ``structural=False`` withholds the removals and
    duplications on that second pass for the same reason.

    A dataclass is a document too, and is corrupted through ``replace``; see
    :func:`_dataclass_mutations` for why a parsed object has to be reachable at all.
    """
    offer = candidates or _guard_candidates
    if is_dataclass(document) and not isinstance(document, type):
        yield from _dataclass_mutations(document, path, offer, candidates, structural)
    elif isinstance(document, Mapping):
        for key in list(document):
            here = (*path, str(key))
            label = ".".join(here)
            if structural:
                yield f"-{label}", {k: v for k, v in document.items() if k != key}
            for candidate in offer(document[key]):
                yield f"{label}={_brief(candidate)}", {**document, key: candidate}
            for inner_label, inner in document_mutations(
                document[key], path=here, candidates=candidates, structural=structural
            ):
                yield inner_label, {**document, key: inner}
    elif isinstance(document, Sequence) and not isinstance(document, str | bytes):
        members = list(document)
        # A CORRUPTION OF ONE MEMBER MUST NOT ALSO CHANGE THE CONTAINER. A JSON document arrives
        # holding lists and a parsed one holds tuples; rebuilding either as a list would test the
        # container's type against a field annotated `tuple[...]` instead of testing the member.
        rebuild: Any = tuple if isinstance(document, tuple) else list
        for index, member in enumerate(members):
            here = (*path, str(index))
            label = ".".join(here)
            if structural:
                yield f"-{label}", rebuild(members[:index] + members[index + 1 :])
                yield f"+{label}", rebuild([*members, member])
                # A NEAR-DUPLICATE IS NOT A DUPLICATE. `if (subject, digest) in seen: raise` is
                # reached only by a second entry that agrees on the pair and differs in its own
                # id, so an exact copy — which an id-keyed assimilation usually collapses or
                # refuses outright — never opens the arm that catches evidence recorded twice.
                if isinstance(member, Mapping):
                    for key in member:
                        yield f"+{label}~{key}", rebuild([*members, {**member, key: HOSTILE}])
                elif is_dataclass(member) and not isinstance(member, type):
                    for field in fields(member):
                        near = _swapped(member, field.name, HOSTILE)
                        if near is not _UNAVAILABLE:
                            yield f"+{label}~{field.name}", rebuild([*members, near])
            for candidate in offer(member):
                yield (
                    f"{label}={_brief(candidate)}",
                    rebuild(
                        [
                            *members[:index],
                            candidate,
                            *members[index + 1 :],
                        ]
                    ),
                )
            for inner_label, inner in document_mutations(
                member, path=here, candidates=candidates, structural=structural
            ):
                yield inner_label, rebuild([*members[:index], inner, *members[index + 1 :]])


def _corruption_sweep(
    run: Any,
    document: Any,
    identify: Any,
    wanted: frozenset[Any],
    modules: Sequence[Any],
    limit: int,
) -> dict[Any, str]:
    """The search every derived-refusal driver shares: which corruption reached which arm.

    ``run`` takes a corrupted document and returns whatever the subject under test returns;
    ``identify`` turns that into the set of arms it proves. Separating the two is what lets one
    search serve a check id, a violation string and a line number without a second authoring of
    the search itself (UCKP-ART-03).

    Three passes, cheapest first, each paying only for what the one before it left unproven.
    Type-derived corruptions reach the arms that read a fact's shape. The MODULES' declared
    constants come next and are tried before the document's own words because they are few and
    aimed: ``__ungoverned_probe__`` is a constant in the analyzer's module and appears nowhere in
    any compliant document. The document's own vocabulary is last and largest, and reaches the
    arms that cross-reference two facts. Every pass stops the moment the last wanted arm falls,
    so the expensive ones are usually not entered at all.
    """
    witnesses: dict[Any, str] = {}
    budget = limit

    def sweep(mutations: Iterator[tuple[str, Any]]) -> None:
        nonlocal budget
        for label, mutated in mutations:
            if budget <= 0 or len(witnesses) == len(wanted):
                return
            budget -= 1
            try:
                produced = run(mutated)
            except Exception:  # noqa: BLE001, S112 — a raise is not a refusal; it proves nothing
                continue
            for arm in identify(produced):
                if arm in wanted:
                    witnesses.setdefault(arm, label)

    def with_words(words: Sequence[str]) -> Iterator[tuple[str, Any]]:
        return document_mutations(
            document,
            candidates=lambda value: tuple(words) if isinstance(value, str) else (),
            structural=False,
        )

    sweep(document_mutations(document))
    declared = set(_declared_words(*modules))
    if len(witnesses) < len(wanted) and declared:
        sweep(with_words(sorted(declared)))
    if len(witnesses) < len(wanted):
        sweep(with_words(sorted(_document_words(document) - declared)))
    return witnesses


def failure_witnesses(
    run: Any, document: Any, wanted: frozenset[str], *modules: Any, limit: int = 60000
) -> dict[str, str]:
    """Map each wanted check id to the label of the first corruption that made it FAIL.

    ``run`` takes a corrupted document and returns findings — anything with a ``check_id`` and a
    ``passed`` that is false when the check could not be proved. An exception is not a failure:
    an analyzer that raises has been driven outside its contract by a corruption it never
    promised to survive, and that proves nothing about the arm under test.
    """

    def identify(findings: Any) -> frozenset[str]:
        return frozenset(
            finding.check_id
            for finding in findings
            if getattr(finding, "check_id", None) is not None
            and not getattr(finding, "passed", True)
        )

    return _corruption_sweep(run, document, identify, wanted, modules, limit)


def assert_every_failure_arm_is_reachable(
    run: Any,
    document: Any,
    *modules: Any,
    unreachable: Sequence[str] = (),
    limit: int = 60000,
) -> dict[str, str]:
    """Every id some ``failed(...)`` in these modules names is reached by corrupting the facts.

    ``unreachable`` names ids the caller has argued are unreachable by corruption — an arm that
    compares a pure function with itself, say. Naming one is a claim in the test that a reader
    can check; the alternative is an arm that quietly went unproven.
    """
    wanted = declared_failure_ids(*modules) - set(unreachable)
    witnesses = failure_witnesses(run, document, wanted, *modules, limit=limit)
    unproven = sorted(wanted - set(witnesses))
    assert not unproven, (
        "no one-place corruption of a fully compliant fact document made these checks fail, so "
        f"their failure arms are unproven and may be unreachable: {unproven}"
    )
    return witnesses


# --- Reason accumulators -----------------------------------------------------------------
#
# THE FOURTH FAMILY HAS NO IDENTIFIER AT ALL. A law in `engine/recursive_knowledge/contract.py`,
# a `_validate_*` method of a declaration, `assemble_package` — each builds a list of human
# readable reasons and returns it, and an empty list IS the verdict. There is no `check_id` to
# match and no `raise` to attribute a traceback to: the only name an arm has is its own line.
#
# So the arm is identified by its line and PROVEN through the literal fragments of the message it
# constructs, both harvested from the source by AST. That is not message-matching in the sense the
# guard driver refuses: nothing is written down in a test, so a reworded message rewords BOTH
# sides at once and the proof survives. What it cannot survive is an arm being deleted, which is
# the outcome wanted. Two arms whose literal fragments are indistinguishable are credited
# together and reported as one, because that is exactly what the evidence supports.

#: The names a reason accumulator goes by. A reason is APPENDED to a list, ADDED to a set or
#: EXTENDED onto a list; anything else is a family this instrument does not yet claim.
REASON_METHODS = frozenset({"append", "add", "extend"})

#: Literal fragments shorter than this are punctuation and connective tissue — ``": "``, ``" is
#: "`` — and would match any message at all. An arm whose every fragment is that short has no
#: usable fingerprint and is reported as having none, rather than being credited by accident.
MINIMUM_FRAGMENT = 4


def _literal_fragments(node: ast.AST) -> tuple[str, ...]:
    """The literal text a string expression is guaranteed to produce, in source order.

    An f-string's interpolations are unknown until it runs, but the text BETWEEN them is fixed,
    and that text in that order is a fingerprint of the expression that built it. Concatenation
    and implicit adjacency are followed through for the same reason.
    """
    if isinstance(node, ast.Constant):
        return (node.value,) if isinstance(node.value, str) else ()
    if isinstance(node, ast.JoinedStr):
        return tuple(
            part.value
            for part in node.values
            if isinstance(part, ast.Constant) and isinstance(part.value, str)
        )
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        return _literal_fragments(node.left) + _literal_fragments(node.right)
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
        # ``", ".join(...)`` and ``"...".format(...)`` — the receiver is the literal part.
        return _literal_fragments(node.func.value) if node.func.attr == "format" else ()
    return ()


def reason_arms(source: Any, *, methods: Sequence[str] | None = None) -> dict[int, tuple[str, ...]]:
    """Every line that appends a reason, as line → the literal fragments its message contains.

    ``source`` is a function, a class or a module. ``methods`` narrows a class to named methods,
    which is what a declaration whose validation is split across a dozen ``_validate_*`` needs.
    An arm with no fragment long enough to be a fingerprint is omitted, so a caller that wants it
    proven has to say so — silence about what cannot be proven is the defect, not the arm.
    """
    if isinstance(source, type) and methods is not None:
        arms: dict[int, tuple[str, ...]] = {}
        for name in methods:
            if (member := getattr(source, name, None)) is not None:
                arms |= reason_arms(member)
        return arms
    try:
        lines, first = inspect.getsourcelines(source)
    except (OSError, TypeError):
        return {}
    try:
        tree = ast.parse(textwrap.dedent("".join(lines)))
    except SyntaxError:  # pragma: no cover — a body that does not parse in isolation
        return {}
    found: dict[int, tuple[str, ...]] = {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute):
            continue
        if node.func.attr not in REASON_METHODS or not node.args:
            continue
        argument = node.args[0]
        elements = argument.elts if isinstance(argument, ast.List | ast.Tuple) else [argument]
        for element in elements:
            fragments = tuple(
                fragment
                for fragment in _literal_fragments(element)
                if len(fragment.strip()) >= MINIMUM_FRAGMENT
            )
            if fragments:
                found[first + (getattr(element, "lineno", node.lineno)) - 1] = fragments
    return found


def _fingerprint_score(message: str, fragments: Sequence[str]) -> int:
    """How much of this arm the message accounts for, or 0 if it is not this arm's message.

    IN SOURCE ORDER, because an f-string emits its literal chunks in the order it declares them,
    and requiring the order costs nothing while refusing a coincidence that requiring mere
    presence would accept.
    """
    position = 0
    for fragment in fragments:
        found = message.find(fragment, position)
        if found < 0:
            return 0
        position = found + len(fragment)
    return sum(len(fragment) for fragment in fragments)


def credited_arms(messages: Sequence[str], arms: Mapping[int, tuple[str, ...]]) -> dict[int, str]:
    """Which arms these reasons came out of, crediting each reason to its best-matching arm.

    BEST-MATCHING AND NOT EVERY-MATCHING. One arm's fragments are often a prefix of another's —
    ``"documentation is incomplete"`` inside ``"documentation is incomplete — missing: "`` — and
    crediting both would let the general arm be proven by the specific one's message forever. The
    arm that accounts for the most literal text is the one that ran; a genuine tie is genuinely
    ambiguous and both are credited, which is what the evidence supports and no more.
    """
    proven: dict[int, str] = {}
    for message in messages:
        scored = [
            (score, line)
            for line, fragments in arms.items()
            if (score := _fingerprint_score(message, fragments))
        ]
        if not scored:
            continue
        best = max(score for score, _ in scored)
        for score, line in scored:
            if score == best:
                proven.setdefault(line, message)
    return proven


def reason_witnesses(
    run: Any,
    document: Any,
    arms: Mapping[int, tuple[str, ...]],
    *modules: Any,
    limit: int = 60000,
) -> dict[int, str]:
    """Map each reason arm's line to the label of the first corruption that reached it.

    ``run`` takes a corrupted document and returns the reasons — a sequence of strings, or
    anything whose members stringify to them.
    """

    def identify(produced: Any) -> frozenset[int]:
        if isinstance(produced, str) or produced is None:
            produced = [produced] if produced else []
        return frozenset(credited_arms([str(item) for item in produced], arms))

    return _corruption_sweep(run, document, identify, frozenset(arms), modules, limit)


def assert_every_reason_arm_is_reachable(
    run: Any,
    document: Any,
    source: Any,
    *modules: Any,
    methods: Sequence[str] | None = None,
    unreachable: Sequence[int] = (),
    limit: int = 60000,
) -> dict[int, str]:
    """Every reason ``source`` can append is appended by some one-place corruption of ``document``.

    ``unreachable`` takes LINE NUMBERS of arms the caller has argued no corruption can reach.
    Naming one is a claim a reader can check; the alternative is an arm that quietly went
    unproven, which is the whole defect.
    """
    arms = reason_arms(source, methods=methods)
    wanted = {line: fragments for line, fragments in arms.items() if line not in set(unreachable)}
    witnesses = reason_witnesses(run, document, wanted, *modules, limit=limit)
    unproven = sorted(set(wanted) - set(witnesses))
    where = inspect.getsourcefile(source) or repr(source)
    assert not unproven, (
        "no one-place corruption of a compliant document made these reasons appear, so the arms "
        f"that build them are unproven and may be unreachable — {where} lines {unproven}"
    )
    return witnesses
