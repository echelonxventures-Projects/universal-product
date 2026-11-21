"""UEC-000001 Part 2 — discovery. The enforcement surface, located by rule.

DISCOVERY IS BY RULE, NEVER BY LIST. A hand-written list of gates would be the defect it is
meant to detect: it would agree with itself forever. Every artifact below is located by a
declared rule over the tracked tree, and the declaration's governed inventory is compared
against what the rules find (UEC-L-02 / UEC-L-03). Two independently derived sets, compared —
that is the only shape in which "a gate disappeared" is a computable fact.

VERSION CONTROL IS THE BOUNDARY. ``git ls-files`` decides what exists, not a filesystem walk.
This is the same boundary ``00-BOOK/tools/ukb.py:_repo_artifact_paths`` uses, and it is chosen
for the same reason: an untracked file is not yet a repository artifact, and a gitignored tree
is not part of the repository's answer. Copying the boundary rather than importing it is
deliberate — ``ukb.py`` lives under an ``EXCLUDE_DIR_PREFIXES`` entry, so importing it would
bind the new plane's correctness to a module the old plane cannot see.
"""

from __future__ import annotations

import ast
import functools
import os
import re
from collections.abc import Iterable, Mapping, Sequence

from engine.enforcement_closure.model import (
    KIND_DECLARATION,
    KIND_ENGINE,
    KIND_MODULE_GATE,
    Artifact,
    EnforcementError,
    Rule,
)
from engine.omega_infinite.git_provider import GitDiscoveryProvider
from engine.omega_infinite.provider import ProviderError

#: ``run_stage "<label>"`` — the same regex ``engine/verification_intelligence/gate.py:100``,
#: ``platform/tests/test_canonical_validation_evidence.py`` and
#: ``.github/workflows/uisd-gate.yml`` apply to ``verify.sh``. A fourth independent reader
#: agreeing on one derivation is what keeps the stage contract from drifting.
STAGE_LABEL = re.compile(r'^\s*run_stage "([^"]+)"', re.M)

#: A Makefile target definition. ``(?!=)`` excludes ``VAR := value``.
MAKE_TARGET = re.compile(r"(?m)^([A-Za-z0-9_.-]+)\s*:(?!=)")


def repo_root() -> str:
    """The repository root, derived from this file's location rather than a cwd guess."""
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _tracked_paths_uncached(root: str) -> tuple[str, ...]:
    """Every path version control carries, sorted. The eligibility boundary for every rule.

    A missing git work tree is a FAULT, not an empty world. Falling back to a filesystem walk
    would make the enforcement plane's population depend on whatever happened to be lying in
    the directory, which is the vacuity this programme exists to refuse.
    """
    # THE PROVIDER, NOT THE TOOL. This asks TRACKED_CONTENT with the provider's own flags, and it
    # keeps the property the docstring above insists on: the provider RAISES rather than returning
    # an empty tuple, so a missing work tree stays a fault and never becomes an empty world.
    #
    # The module docstring's reason for copying rather than importing was about `ukb.py`, which
    # lives under an EXCLUDE_DIR_PREFIXES entry the enforcement plane cannot see. That reason does
    # not reach the provider: engine/omega_infinite is in governed scope, and the import graph was
    # walked before this change to confirm nothing there imports back into this package.
    try:
        artifacts = GitDiscoveryProvider(root=root).enumerate()
    except ProviderError as exc:  # pragma: no cover - environment
        raise EnforcementError(
            "the enforcement plane cannot be measured without a git work tree: "
            "the tracked-content provider did not resolve, so the population is unknown"
        ) from exc
    return tuple(sorted(a.location.locator for a in artifacts))


def read_text(root: str, relative: str) -> str:
    path = os.path.join(root, relative)
    try:
        with open(path, encoding="utf-8") as handle:
            return handle.read()
    except OSError as exc:
        raise EnforcementError(f"an enforcement substrate does not resolve: {relative}") from exc


# --- per-strategy locators ----------------------------------------------------------------
#
# Each returns the artifacts one rule locates. A strategy that raises is a FAULT; a strategy
# that returns nothing is a REFUSAL under UEC-L-01, never a pass.


def _glob_paths(paths: Sequence[str], pattern: str) -> list[str]:
    """Paths matching a declared shell-style pattern, evaluated over the tracked set."""
    regex = re.compile(
        "^"
        + pattern.replace(".", r"\.").replace("**/", "\0").replace("*", "[^/]*").replace("\0", ".*")
        + "$"
    )
    return [p for p in paths if regex.match(p)]


def locate_paths(rule: Rule, paths: Sequence[str], root: str) -> list[Artifact]:
    """Tracked paths matching the rule that ALSO exist on disk.

    The index is the governance boundary; the filesystem decides existence. Both halves are
    load-bearing and the distinction is the one that makes deletion detectable.

    ``git ls-files`` still lists a file that has been deleted from the working tree, so
    discovering from the index alone would report a deleted workflow as present and UEC-L-02
    would never fire — the gate would fault on the unreadable file instead of refusing, and a
    fault is a weaker and less actionable answer than "a governed protection is gone".

    This is the same filter ``00-BOOK/tools/ukb.py:_iter_files`` applies for the same reason,
    where it is commented "index entry with no working-tree file (e.g. staged delete)".
    """
    return [
        Artifact(identity=p, kind=rule.kind, rule_id=rule.rule_id)
        for p in _glob_paths(paths, rule.pattern)
        if os.path.isfile(os.path.join(root, p))
    ]


def locate_make_targets(rule: Rule, root: str) -> list[Artifact]:
    """Makefile targets whose name matches the declared pattern, with their recipe bodies.

    The recipe is captured because UEC-L-04 needs to know what a target INVOKES, not merely
    that it exists. A target whose recipe no longer names its engine is a target that stopped
    enforcing while continuing to exist.
    """
    body = read_text(root, "Makefile")
    lines = body.splitlines()
    regex = re.compile(rule.pattern)
    found: list[Artifact] = []
    for index, line in enumerate(lines):
        match = MAKE_TARGET.match(line)
        if match is None or not regex.match(match.group(1)):
            continue
        recipe: list[str] = []
        for follow in lines[index + 1 :]:
            if follow.startswith(("\t", "    ")) or not follow.strip():
                recipe.append(follow.strip())
                continue
            break
        found.append(
            Artifact(
                identity=match.group(1),
                kind=rule.kind,
                rule_id=rule.rule_id,
                detail={"line": index + 1, "recipe": "\n".join(recipe)},
            )
        )
    # `make help` echoes every target name; a target may also be declared twice. Dedupe on
    # identity, keeping the first definition, which is the one make itself honours.
    seen: set[str] = set()
    unique: list[Artifact] = []
    for artifact in found:
        if artifact.identity in seen:
            continue
        seen.add(artifact.identity)
        unique.append(artifact)
    return unique


def locate_verify_stages(rule: Rule, root: str) -> list[Artifact]:
    body = read_text(root, rule.root or "verify.sh")
    return [
        Artifact(identity=label, kind=rule.kind, rule_id=rule.rule_id, detail={"order": order})
        for order, label in enumerate(STAGE_LABEL.findall(body), start=1)
    ]


STRATEGIES = {
    "tracked_glob": "locate_paths",
    "make_targets": "locate_make_targets",
    "verify_stages": "locate_verify_stages",
}


def discover(rules: Iterable[Rule], root: str, paths: Sequence[str]) -> dict[str, list[Artifact]]:
    """Every artifact every rule locates, keyed by rule id.

    An unknown strategy is a FAULT. Silently skipping it would mean a declaration could
    disable a rule by misspelling its strategy — omission dressed as configuration.
    """
    located: dict[str, list[Artifact]] = {}
    for rule in rules:
        if rule.strategy == "tracked_glob":
            located[rule.rule_id] = locate_paths(rule, paths, root)
        elif rule.strategy == "make_targets":
            located[rule.rule_id] = locate_make_targets(rule, root)
        elif rule.strategy == "verify_stages":
            located[rule.rule_id] = locate_verify_stages(rule, root)
        else:
            raise EnforcementError(
                f"discovery rule {rule.rule_id} names an unknown strategy {rule.strategy!r}; "
                f"known strategies are {sorted(STRATEGIES)}"
            )
    return located


# --- the binding graph --------------------------------------------------------------------


def module_path(relative: str) -> str:
    """``engine/construct/gate.py`` -> ``engine.construct.gate`` — how an invoker names it."""
    return relative[: -len(".py")].replace("/", ".")


def source_evidence(text: str) -> str:
    """What a Python module ACTUALLY references, with prose excluded.

    A docstring naming an engine is documentation. A string constant naming one is a binding.
    Scanning raw text cannot tell them apart, and the difference is not academic: the first
    draft of this module counted its OWN docstrings — which name ``ceu-declaration.json``,
    ``urr-declaration.json`` and ``ucxi-declaration.json`` while explaining that nothing loads
    them — as evidence that something loads them. The detector was satisfied by its own prose,
    which is the exact defect class it exists to refuse, reproduced inside the fix.

    The same distinction is drawn by ``engine/verification_intelligence/gate.py``'s
    ``_evaluated_strings`` for the same reason, and is copied here rather than imported so the
    two planes do not become co-dependent.

    Returns the evaluated string constants and the imported dotted names, joined. A module that
    will not parse contributes nothing rather than contributing its comments.
    """
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return ""
    docstrings: set[int] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Module | ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef):
            continue
        body = getattr(node, "body", None)
        if not body:
            continue
        first = body[0]
        if isinstance(first, ast.Expr) and isinstance(first.value, ast.Constant):
            if isinstance(first.value.value, str):
                docstrings.add(id(first.value))
    parts: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            if id(node) not in docstrings:
                parts.append(node.value)
        elif isinstance(node, ast.Import):
            parts.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                parts.append(node.module)
                parts.extend(f"{node.module}.{alias.name}" for alias in node.names)
        elif isinstance(node, ast.Attribute):
            parts.append(node.attr)
        elif isinstance(node, ast.Name):
            parts.append(node.id)
    return "\n".join(parts)


def _invocation_corpus_uncached(root: str, workflows: Sequence[Artifact]) -> dict[str, str]:
    """Every text in which an invocation of an enforcement artifact could appear.

    Four independent planes: the Makefile (local), the workflow set (CI), ``verify.sh`` (the
    certification contract) and ``scripts/ucos-env.sh`` (the shared gate helper both the
    canonical path and the pre-commit hook execute). UEC-L-06 requires two of them, because the
    repository's present shape — a Makefile target and a workflow step holding two independent
    COPIES of one command string, neither derived from the other — is not redundancy. It is two
    single points of failure, and deleting either leaves the other unaware.

    ``scripts/ucos-env.sh`` WAS MISSING, AND ITS ABSENCE REPORTED A PROTECTION THAT EXISTS AS ONE
    THAT DOES NOT. ``verify.sh`` does not name ``engine.execution_environment.gate`` anywhere; it
    sources this helper, and line 426 of the helper issues the command. So the execution
    environment gate — the Stage 0 refusal that decides whether the interpreter may be trusted at
    all — was measured as reachable from the Makefile alone and stood in UEC-L-06's population as
    a single point of failure it was never a single point of failure of. That is a FALSE
    DEFICIENCY, and a law that cries wolf is disabled by whoever has to look at it, which is the
    failure mode ``_needles`` already records as having retired more real gates here than any
    deletion. Widening the corpus clears exactly that one artifact and adds none, measured; the
    ceiling moved 16 -> 15 in the same change, because a repair that does not tighten the ratchet
    leaves slack for a future violation to occupy.
    """
    corpus = {
        "Makefile": read_text(root, "Makefile"),
        "verify.sh": read_text(root, "verify.sh"),
        "scripts/ucos-env.sh": read_text(root, "scripts/ucos-env.sh"),
    }
    for workflow in workflows:
        corpus[workflow.identity] = read_text(root, workflow.identity)
    return corpus


def _needles(artifact: Artifact) -> tuple[str, ...]:
    """The strings by which an invoker or a test would name this artifact.

    Deliberately generous. A needle set that is too narrow reports a false deficiency, and a
    law that cries wolf is disabled by whoever has to look at it — the failure mode that
    retired more real gates in this repository than any deletion. Generosity here weakens
    UEC-L-05 toward its necessary condition ("something names this engine") and no further,
    which is why the sufficient condition is carried by UEC-L-09's mutation requirement
    instead of being claimed here.
    """
    if artifact.kind == KIND_ENGINE:
        # `00-MASTER/UIS-001/uis_engine.py` is invoked by path; a workflow names its programme
        # directory; a test names the programme id (`UIS-001`) or the module (`uis_engine`).
        directory = os.path.dirname(artifact.identity)
        return (
            artifact.identity,
            directory,
            os.path.basename(directory),
            os.path.basename(artifact.identity)[: -len(".py")],
        )
    if artifact.kind == KIND_MODULE_GATE:
        # `engine/construct/gate.py` is invoked as `-m engine.construct.gate`; a test almost
        # always imports a sibling module, so the PACKAGE is the honest needle.
        package = os.path.dirname(artifact.identity)
        return (
            module_path(artifact.identity),
            package.replace("/", "."),
            package,
            artifact.identity,
        )
    if artifact.kind == KIND_DECLARATION:
        directory = os.path.dirname(artifact.identity)
        return (
            artifact.identity,
            directory,
            os.path.basename(directory),
            os.path.basename(artifact.identity),
        )
    return (artifact.identity,)


def _invocation_needles(artifact: Artifact) -> tuple[str, ...]:
    """The strings by which something would actually RUN this artifact.

    SEPARATE FROM :func:`_needles`, AND THE SEPARATION IS THE POINT. That function is
    deliberately generous because it also answers "does a test name this engine", where a
    package or a programme id is honest evidence. Generosity is wrong for invocation, and a
    hostile audit measured the cost: pointing every caller of ``engine/recursive_knowledge/gate.py``
    at ``engine.recursive_knowledge.NOTHING`` — in the Makefile, in ``verify.sh`` and in the
    workflow at once — left UEC-L-04 satisfied and the gate exit 0, because the bare package
    ``engine.recursive_knowledge`` was still a needle and still appeared in every one of those
    lines. The gate had stopped running and nothing said so, which is the same observable state
    as deleting it and the one this programme exists to refuse.

    So an invoker must name the artifact in a form that could execute it: the dotted module path
    for a module gate (what ``-m`` takes), or the file path. A package name in prose is not an
    invocation.
    """
    if artifact.kind == KIND_MODULE_GATE:
        return (module_path(artifact.identity), artifact.identity)
    if artifact.kind == KIND_ENGINE:
        return (artifact.identity, os.path.basename(artifact.identity)[: -len(".py")])
    return _needles(artifact)


def invokers(artifact: Artifact, corpus: Mapping[str, str]) -> tuple[str, ...]:
    """Which invocation planes actually name this artifact.

    The artifact's own file is excluded from its own evidence: a module that mentions its own
    dotted path in a docstring would otherwise invoke itself, which is the self-certifying
    shape UEC exists to refuse.
    """
    needles = _invocation_needles(artifact)
    found = []
    for where, text in corpus.items():
        if where == artifact.identity:
            continue
        if any(needle and needle in text for needle in needles):
            found.append(where)
    return tuple(sorted(found))


def test_bindings(artifact: Artifact, tests: Mapping[str, str]) -> tuple[str, ...]:
    """Which test files actually reference this artifact.

    Measured over ``source_evidence`` rather than raw text, so a test whose DOCSTRING names an
    engine does not count as testing it. This suite's own docstrings name ``uis_engine.py`` and
    ``acee_engine.py`` while explaining that nothing tests them; before this exclusion those two
    engines appeared covered, and the measured deficit fell from 18 to 16 for no reason but
    prose.

    Naming is necessary and not sufficient: a test that references an engine has not been shown
    to kill a mutant in it. UEC-L-05 measures the necessary condition and says so; the sufficient
    condition is carried by UEC-L-09 over UEC's own surface and by this suite's forged
    violations. Recording that distinction is the difference between a law and a green tick.
    """
    needles = _needles(artifact)
    return tuple(
        sorted(
            where
            for where, text in tests.items()
            if where != artifact.identity and any(needle and needle in text for needle in needles)
        )
    )


def consumers(artifact: Artifact, sources: Mapping[str, str]) -> tuple[str, ...]:
    """Which modules actually load this declaration.

    The honest binding for both "is this declaration enforced" (UEC-L-07) and "does its owner
    mint a certification identity" (UEC-L-08). Deriving the owner from the declaration's NAME
    was tried and is wrong: ``UCON-000001`` is owned by ``engine/construct/`` and
    ``UISD-000001`` by ``engine/infinite_scope/``, so a name-based guess reported UCON — which
    demonstrably has a digest — as having none.
    """
    name = os.path.basename(artifact.identity)
    return tuple(sorted(where for where, evidence in sources.items() if name in evidence))


def _source_corpus_uncached(
    root: str, paths: Sequence[str], *, exclude: Sequence[str] = ()
) -> dict[str, str]:
    """``source_evidence`` for every tracked Python module outside the excluded prefixes."""
    corpus: dict[str, str] = {}
    for path in paths:
        if not path.endswith(".py"):
            continue
        if any(path.startswith(prefix) for prefix in exclude):
            continue
        if not os.path.isfile(os.path.join(root, path)):
            continue  # index entry with no working-tree file
        corpus[path] = source_evidence(read_text(root, path))
    return corpus


def refusal_shapes(
    text: str,
    *,
    raise_names: Sequence[str],
    finding_names: Sequence[str],
    closed_exits: Sequence[int],
) -> frozenset[str]:
    """Which REFUSAL shapes a test module actually contains, read structurally.

    ``source_evidence`` cannot answer this — it keeps string constants and imports, and a
    forged refusal is a code shape, not a string. Raw text cannot answer it either, for the
    reason that module records: a docstring explaining that a test asserts ``pytest.raises``
    would count as the test doing so, which is the detector being satisfied by prose. So this
    reads the AST, where a docstring is a value and a call is a call.

    Three shapes, and the vocabulary of each is supplied by the caller from the declaration
    rather than written here — a verification plane that refuses in a way nobody has yet
    invented is admitted by naming its vocabulary, not by editing this function.
    """
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return frozenset()
    raises, findings, exits = set(raise_names), set(finding_names), set(closed_exits)
    found: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            name = func.attr if isinstance(func, ast.Attribute) else getattr(func, "id", "")
            if name in raises:
                found.add("raises")
        elif isinstance(node, ast.Assert):
            for inner in ast.walk(node.test):
                ident = (
                    inner.attr
                    if isinstance(inner, ast.Attribute)
                    else getattr(inner, "id", "")
                    if isinstance(inner, ast.Name)
                    else ""
                )
                if ident in findings:
                    found.add("asserts_findings")
                if (
                    isinstance(inner, ast.Constant)
                    and isinstance(inner.value, int)
                    and not isinstance(inner.value, bool)
                    and inner.value in exits
                ):
                    found.add("asserts_closed_exit")
    return frozenset(found)


def _test_corpus_uncached(
    root: str, paths: Sequence[str], testpaths: Sequence[str]
) -> dict[str, str]:
    """``source_evidence`` for every tracked test module under the declared test roots."""
    corpus: dict[str, str] = {}
    for path in paths:
        if not path.endswith(".py"):
            continue
        if not any(path.startswith(prefix) for prefix in testpaths):
            continue
        if not os.path.isfile(os.path.join(root, path)):
            continue  # index entry with no working-tree file
        if os.path.basename(path).startswith("test_") or path.endswith("conftest.py"):
            corpus[path] = source_evidence(read_text(root, path))
    return corpus


# ---------------------------------------------------------------------------
# Memoized repository scans.
#
# WHY THESE ARE CACHED AND `discover` IS NOT. `Probe.__init__` computes everything the laws
# measure, once per probe — which is right, because a law that re-derives its own population is
# a law whose population can disagree with its neighbour's. But the mutation suites build MANY
# probes over ONE repository: `test_lowering_any_discovery_floor_is_refused` constructs a probe
# per discovery rule per lowered floor, and each construction re-ran the repository-wide scans
# that the mutation cannot affect. Measured, that test alone cost 221s and its file 1,048s, on
# the critical path of a sharded run whose wall clock is its slowest shard.
#
# `discover` is deliberately NOT cached: it takes `declaration.rules`, which is exactly what a
# mutation changes, so caching it would be caching the thing under test.
#
# WHAT MAKES THE CACHE SOUND. The key is the FULL argument tuple, not just the root. Any change
# to what should be scanned — a different repository, a different tracked-path set, different
# testpaths or excludes — is a different key and recomputes. The 221s test recomputed identical
# results only because it varies `floor`, which appears in none of these signatures.
#
# THE ONE CONDITION THIS DOES NOT COVER, STATED RATHER THAN ASSUMED. Repository CONTENT changing
# inside one process is invisible to these caches. No caller does that: the enforcement suites
# mutate an in-memory declaration and never the tree, and the verification-purity suite exists to
# prove the tooling does not write what it did not dirty. `clear_caches` is the escape hatch for
# any future caller that needs one, and `test_the_memoized_scans_equal_their_uncached_form`
# measures the equality rather than asserting it in prose.
#
# DICTS ARE COPIED OUT. A cached mutable mapping shared across probes would let one probe's
# consumer alias another's. Copying a few thousand string entries is nothing against re-reading
# and re-parsing the files that produced them.


@functools.cache
def _tracked_paths_memo(root: str) -> tuple[str, ...]:
    return _tracked_paths_uncached(root)


@functools.cache
def _source_corpus_memo(
    root: str, paths: tuple[str, ...], exclude: tuple[str, ...]
) -> dict[str, str]:
    return _source_corpus_uncached(root, paths, exclude=exclude)


@functools.cache
def _test_corpus_memo(
    root: str, paths: tuple[str, ...], testpaths: tuple[str, ...]
) -> dict[str, str]:
    return _test_corpus_uncached(root, paths, testpaths)


def tracked_paths(root: str) -> tuple[str, ...]:
    """Every path version control carries, sorted. Memoized per repository root."""
    return _tracked_paths_memo(root)


def invocation_corpus(root: str, workflows: Sequence[Artifact]) -> dict[str, str]:
    """Every text in which an invocation could appear. NOT memoized, deliberately.

    `Artifact` carries a `detail: dict` field, so it is frozen but not hashable and cannot key
    a cache without a surrogate. That surrogate is not worth building: this scan reads the
    Makefile, `verify.sh`, `scripts/ucos-env.sh` and the workflow set — on the order of forty
    files, against the two thousand-odd that `source_corpus` reads. Excluding it keeps the
    memoization free of a hand-rolled key whose correctness would have to be argued separately.
    """
    return _invocation_corpus_uncached(root, workflows)


def source_corpus(
    root: str, paths: Sequence[str], *, exclude: Sequence[str] = ()
) -> dict[str, str]:
    """``source_evidence`` per tracked module outside ``exclude``. Memoized on all three."""
    return dict(_source_corpus_memo(root, tuple(paths), tuple(exclude)))


def test_corpus(root: str, paths: Sequence[str], testpaths: Sequence[str]) -> dict[str, str]:
    """``source_evidence`` per tracked test module. Memoized on all three."""
    return dict(_test_corpus_memo(root, tuple(paths), tuple(testpaths)))


def clear_caches() -> None:
    """Drop every memoized repository scan. For a caller that changes the tree in-process."""
    _tracked_paths_memo.cache_clear()
    _source_corpus_memo.cache_clear()
    _test_corpus_memo.cache_clear()
