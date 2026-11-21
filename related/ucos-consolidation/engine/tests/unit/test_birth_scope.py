"""UOBC-BSP-001 — birth scope, measured in both directions.

Each law is exercised where it holds over the repository as it stands, and against a
policy or context deliberately broken in the one way that law exists to catch. A law
tested only where it passes is a law nobody has shown can fail.

The mandated case matrix is covered explicitly: a capability and a programme with birth
records PASS; a generated projection and a derived register without birth records PASS
*because* they are absent; a required-and-mandatory kind without birth FAILs; an
independent birth for a generated artifact FAILs; and an unknown object kind FAILs.
"""

from __future__ import annotations

import ast
import dataclasses
import json
import os
import pathlib
from types import MappingProxyType

import pytest

from engine.object_birth import scope
from engine.object_birth.model import BirthError
from engine.object_birth.scope import (
    EXCEPTION,
    FAIL,
    MANDATORY_ABSENCE,
    PASS,
    SCOPE_LAW_CHECKS,
    SELECTOR_OPERATORS,
    VALIDATION_RULES,
    ScopePolicy,
    assess_scope,
    classify,
    evaluate,
    load_context,
    load_policy,
    repo_root,
    resolve_subject,
    summarize,
)


@pytest.fixture(name="policy")
def _policy() -> ScopePolicy:
    return load_policy()


@pytest.fixture(name="ctx")
def _ctx() -> dict:
    return load_context()


@pytest.fixture(name="document")
def _document() -> dict:
    with open(
        os.path.join(repo_root(), "00-MASTER", "UOBC-000001", "birth-scope-policy.json"),
        encoding="utf-8",
    ) as handle:
        return json.load(handle)


def _run(name: str, policy: ScopePolicy, ctx: dict) -> tuple[str, ...]:
    return SCOPE_LAW_CHECKS[name](policy, ctx)


def _first_of_kind(policy: ScopePolicy, ctx: dict, kind_name: str) -> str:
    for obj in ctx["objects"]:
        kind = classify(policy, obj, ctx)
        if kind is not None and kind.object_kind == kind_name:
            return str(obj["path"])
    raise AssertionError(f"no object classifies as {kind_name}")


# --- the repository as it stands ------------------------------------------------------


def test_every_scope_law_holds_over_the_repository(policy, ctx):
    for law_id, _title, violations in assess_scope(policy, ctx):
        assert violations == (), f"{law_id}: {violations}"


def test_the_policy_and_the_implemented_checks_agree(policy):
    assert policy.validate(frozenset(SCOPE_LAW_CHECKS)) == []


def test_measuring_twice_produces_the_same_summary(policy, ctx):
    assert summarize(policy, ctx) == summarize(policy, load_context())


def test_the_summary_accounts_for_every_governed_object(policy, ctx):
    summary = summarize(policy, ctx)
    assert sum(summary["kinds"].values()) == summary["objects"]
    assert sum(summary["verdicts"].values()) == summary["objects"]


def test_no_object_is_left_unclassified(policy, ctx):
    assert [o["path"] for o in ctx["objects"] if classify(policy, o, ctx) is None] == []


# --- the mandated PASS cases ----------------------------------------------------------


def test_a_capability_with_a_birth_record_passes(policy, ctx):
    verdict = evaluate("engine/root_ontology/__init__.py", policy, ctx)
    assert verdict.object_kind == "CAPABILITY_PACKAGE"
    assert verdict.birth_required is True
    assert verdict.verdict == PASS


def test_a_test_suite_with_a_birth_record_passes(policy, ctx):
    verdict = evaluate("engine/tests/unit/test_root_ontology.py", policy, ctx)
    assert verdict.object_kind == "TEST_SUITE"
    assert verdict.verdict == PASS


def test_a_generated_projection_without_a_birth_record_passes(policy, ctx):
    path = _first_of_kind(policy, ctx, "GENERATED_ARTIFACT")
    verdict = evaluate(path, policy, ctx)
    assert verdict.birth_required is False
    assert verdict.verdict == PASS


def test_a_derived_register_is_forbidden_from_being_born(policy):
    """The kind exists as a second net even when the generated registry has not listed it."""
    kind = policy.kind("DERIVED_REGISTER")
    assert kind is not None
    assert kind.enforcement == MANDATORY_ABSENCE
    assert kind.birth_required is False


def test_a_configuration_object_needs_no_birth(policy, ctx):
    verdict = evaluate(".gitignore", policy, ctx)
    assert verdict.object_kind == "CONFIGURATION"
    assert verdict.verdict == PASS


# --- the mandated FAIL cases ----------------------------------------------------------


def test_a_required_kind_with_mandatory_adoption_and_no_birth_fails(policy, ctx):
    """Deferred adoption is an EXCEPTION; mandatory adoption with no birth is a FAIL."""
    kind = policy.kind("CAPABILITY_PACKAGE")
    hardened = dataclasses.replace(kind, adoption="MANDATORY", adoption_gap=None)
    kinds = tuple(hardened if k is kind else k for k in policy.kinds)
    strict = dataclasses.replace(policy, kinds=kinds)
    unborn = next(
        str(o["path"])
        for o in ctx["objects"]
        if classify(strict, o, ctx) is not None
        and classify(strict, o, ctx).object_kind == "CAPABILITY_PACKAGE"
        and evaluate(str(o["path"]), policy, ctx).verdict == EXCEPTION
    )
    assert evaluate(unborn, strict, ctx).verdict == FAIL


def test_an_unborn_capability_is_an_exception_naming_its_gap(policy, ctx):
    unborn = next(
        v
        for v in (evaluate(str(o["path"]), policy, ctx) for o in ctx["objects"])
        if v.object_kind == "CAPABILITY_PACKAGE" and v.verdict == EXCEPTION
    )
    assert "G11" in unborn.reason


def test_a_fake_independent_birth_for_a_generated_artifact_fails(policy, ctx):
    """The mandate's central prohibition, exercised."""
    path = _first_of_kind(policy, ctx, "GENERATED_ARTIFACT")
    forged = dict(ctx)
    forged["births"] = dict(ctx["births"])
    forged["births"][f"urn:ucos:ucko:ucos.determination:{path[:-3]}"] = {}
    violations = _run("no_derived_object_is_born", policy, forged)
    assert any(path in v for v in violations)
    assert evaluate(path, policy, forged).verdict == FAIL


def test_an_unknown_object_kind_fails(policy, ctx):
    """With the catch-all removed, an object matching nothing is refused, never assumed."""
    truncated = dataclasses.replace(policy, kinds=policy.kinds[:-1])
    assert evaluate("00-MASTER/UCOS-UGA-001/uga_engine.py", truncated, ctx).verdict == FAIL
    assert any("classify to no kind" in v for v in _run("classification_is_total", truncated, ctx))


def test_an_object_outside_the_governed_registry_fails(policy, ctx):
    assert evaluate("no/such/path.py", policy, ctx).verdict == FAIL


# --- BSP-L-01 -------------------------------------------------------------------------


def test_l01_refuses_a_selector_naming_an_unimplemented_operator(policy):
    kind = policy.kinds[0]
    broken = dataclasses.replace(kind, selector={"not_an_operator": True})
    mutated = dataclasses.replace(policy, kinds=(broken, *policy.kinds[1:]))
    assert any("not implemented" in v for v in _run("policy_is_structurally_usable", mutated, {}))


def test_l01_refuses_a_validation_rule_that_is_not_implemented(policy):
    kind = policy.kinds[0]
    broken = dataclasses.replace(kind, validation_rule="invented_rule")
    mutated = dataclasses.replace(policy, kinds=(broken, *policy.kinds[1:]))
    assert any(
        "is not implemented" in v for v in _run("policy_is_structurally_usable", mutated, {})
    )


def test_l01_refuses_a_validation_rule_that_contradicts_its_enforcement(policy):
    """A kind may not claim it forbids birth while naming the rule that only reports."""
    kind = policy.kind("GENERATED_ARTIFACT")
    broken = dataclasses.replace(kind, validation_rule="birth_coverage_disclosed")
    mutated = dataclasses.replace(
        policy, kinds=tuple(broken if k is kind else k for k in policy.kinds)
    )
    assert any("which implements" in v for v in _run("policy_is_structurally_usable", mutated, {}))


def test_l01_refuses_an_implemented_rule_no_kind_claims(policy):
    kinds = tuple(
        dataclasses.replace(k, validation_rule="not_required", enforcement="NOT_REQUIRED")
        for k in policy.kinds
    )
    mutated = dataclasses.replace(policy, kinds=kinds)
    problems = _run("policy_is_structurally_usable", mutated, {})
    assert any("no kind claims it" in v for v in problems)


def test_l01_refuses_a_duplicated_kind(policy):
    mutated = dataclasses.replace(policy, kinds=(*policy.kinds, policy.kinds[0]))
    assert any("more than once" in v for v in _run("policy_is_structurally_usable", mutated, {}))


def test_every_implemented_rule_and_operator_is_reachable(policy):
    assert set(VALIDATION_RULES) == {k.validation_rule for k in policy.kinds}
    used = {op for k in policy.kinds for op in k.selector}
    assert used <= set(SELECTOR_OPERATORS)


# --- BSP-L-02 -------------------------------------------------------------------------


def test_l02_refuses_two_catch_alls(policy, ctx):
    extra = dataclasses.replace(policy.kinds[0], selector={"catch_all": True})
    mutated = dataclasses.replace(policy, kinds=(*policy.kinds, extra))
    assert any("catch_all" in v for v in _run("classification_is_total", mutated, ctx))


def test_l02_refuses_a_catch_all_that_is_not_last(policy, ctx):
    reordered = (policy.kinds[-1], *policy.kinds[:-1])
    mutated = dataclasses.replace(policy, kinds=reordered)
    assert any("not declared last" in v for v in _run("classification_is_total", mutated, ctx))


def test_first_match_wins_so_classification_is_single_valued(policy, ctx):
    """A determination that is also a corpus document classifies as the earlier kind."""
    determination = _first_of_kind(policy, ctx, "DETERMINATION")
    assert evaluate(determination, policy, ctx).object_kind == "DETERMINATION"


# --- BSP-L-04 -------------------------------------------------------------------------


def test_l04_refuses_a_birth_naming_a_subject_that_does_not_exist(policy, ctx):
    forged = dict(ctx)
    forged["births"] = dict(ctx["births"])
    forged["births"]["urn:ucos:ucko:ucos.determination:NO-SUCH-DETERMINATION"] = {}
    assert any(
        "does not exist" in v for v in _run("every_birth_subject_may_be_born", policy, forged)
    )


def test_l04_refuses_a_birth_in_an_unresolvable_namespace(policy, ctx):
    forged = dict(ctx)
    forged["births"] = dict(ctx["births"])
    forged["births"]["urn:ucos:ucko:ucos.invented:THING"] = {}
    assert any(
        "no declared subject_resolution rule" in v
        for v in _run("every_birth_subject_may_be_born", policy, forged)
    )


def test_every_declared_namespace_resolves_a_real_birth(policy, ctx):
    for urn in ctx["births"]:
        assert resolve_subject(policy, urn) is not None, urn


def test_a_malformed_urn_resolves_to_nothing(policy):
    assert resolve_subject(policy, "not-a-urn") is None


# --- BSP-L-05 -------------------------------------------------------------------------


def test_l05_refuses_a_required_kind_with_no_adoption_state(policy):
    kind = policy.kind("CAPABILITY_PACKAGE")
    broken = dataclasses.replace(kind, adoption=None)
    mutated = dataclasses.replace(
        policy, kinds=tuple(broken if k is kind else k for k in policy.kinds)
    )
    assert any("discloses no adoption" in v for v in _run("adoption_is_disclosed", mutated, {}))


def test_l05_refuses_a_deferred_adoption_naming_no_gap(policy):
    kind = policy.kind("CAPABILITY_PACKAGE")
    broken = dataclasses.replace(kind, adoption_gap=None)
    mutated = dataclasses.replace(
        policy, kinds=tuple(broken if k is kind else k for k in policy.kinds)
    )
    assert any("undisclosed" in v for v in _run("adoption_is_disclosed", mutated, {}))


# --- BSP-L-06 -------------------------------------------------------------------------


def test_l06_refuses_a_regression_below_a_declared_floor(policy, ctx):
    thinned = dict(ctx)
    thinned["births"] = {
        urn: rec for urn, rec in ctx["births"].items() if ":ucos.engine:engine." not in urn
    }
    assert any(
        "below the declared floor" in v for v in _run("coverage_does_not_regress", policy, thinned)
    )


def test_l06_holds_when_adoption_rises(policy, ctx):
    grown = dict(ctx)
    grown["births"] = dict(ctx["births"])
    grown["births"]["urn:ucos:ucko:ucos.engine:engine.uckp"] = {}
    assert _run("coverage_does_not_regress", policy, grown) == ()


def test_the_floors_match_what_is_measured_today(policy, ctx):
    measured = summarize(policy, ctx)["births_by_subject_class"]
    for floor in policy.floors:
        assert measured.get(floor.subject_class, 0) >= floor.born_at_baseline


# --- the policy refuses an unusable declaration ---------------------------------------


@pytest.mark.parametrize("section", ["kinds", "subject_resolution", "coverage_floors", "laws"])
def test_a_policy_missing_a_section_is_refused(document, section):
    document.pop(section)
    with pytest.raises(BirthError):
        ScopePolicy.of(document)


@pytest.mark.parametrize(
    "field", ["reason", "authority", "validation_rule", "producer_relationship"]
)
def test_a_kind_missing_a_required_field_is_refused(document, field):
    document["kinds"][0].pop(field)
    with pytest.raises(BirthError, match="missing"):
        ScopePolicy.of(document)


def test_a_kind_with_a_non_boolean_birth_required_is_refused(document):
    document["kinds"][0]["birth_required"] = "yes"
    with pytest.raises(BirthError, match="birth_required"):
        ScopePolicy.of(document)


def test_a_kind_with_an_empty_selector_is_refused(document):
    document["kinds"][0]["selector"] = {}
    with pytest.raises(BirthError, match="selector"):
        ScopePolicy.of(document)


def test_a_negative_floor_is_refused(document):
    document["coverage_floors"][0]["born_at_baseline"] = -1
    with pytest.raises(BirthError, match="whole number"):
        ScopePolicy.of(document)


def test_a_boolean_floor_is_refused(document):
    document["coverage_floors"][0]["born_at_baseline"] = True
    with pytest.raises(BirthError, match="whole number"):
        ScopePolicy.of(document)


def test_a_law_without_a_check_is_refused(document):
    document["laws"][0].pop("check")
    with pytest.raises(BirthError):
        ScopePolicy.of(document)


def test_loading_a_policy_whose_checks_disagree_is_a_fault(tmp_path, document):
    document["laws"][0]["check"] = "a_check_that_does_not_exist"
    path = tmp_path / "birth-scope-policy.json"
    path.write_text(json.dumps(document), encoding="utf-8")
    with pytest.raises(BirthError, match="disagree"):
        load_policy(str(path))


def test_a_missing_policy_is_a_fault(tmp_path):
    with pytest.raises(BirthError, match="absent"):
        load_policy(str(tmp_path / "absent.json"))


def test_an_unparseable_policy_is_a_fault(tmp_path):
    path = tmp_path / "birth-scope-policy.json"
    path.write_text("{ not json", encoding="utf-8")
    with pytest.raises(BirthError, match="valid JSON"):
        load_policy(str(path))


def test_a_policy_that_is_not_an_object_is_a_fault(tmp_path):
    path = tmp_path / "birth-scope-policy.json"
    path.write_text("[]", encoding="utf-8")
    with pytest.raises(BirthError, match="not an object"):
        load_policy(str(path))


# --- no hard-coded reality ------------------------------------------------------------


def test_the_module_holds_no_object_kind_path_or_gap_in_executable_code(policy):
    """Kinds, gap ids and repository paths are DATA. Only generic operators are code."""

    source = (pathlib.Path(repo_root()) / "engine" / "object_birth" / "scope.py").read_text(
        encoding="utf-8"
    )
    tree = ast.parse(source)
    docstrings = set()
    for node in ast.walk(tree):
        body = getattr(node, "body", None)
        if isinstance(node, ast.Module | ast.ClassDef | ast.FunctionDef) and body:
            first = body[0]
            if isinstance(first, ast.Expr) and isinstance(first.value, ast.Constant):
                docstrings.add(id(first.value))
    literals = [
        n.value
        for n in ast.walk(tree)
        if isinstance(n, ast.Constant) and isinstance(n.value, str) and id(n) not in docstrings
    ]
    forbidden = [k.object_kind for k in policy.kinds] + ["G11", "engine/", "00-BOOK/DATA/g"]
    for literal in literals:
        for needle in forbidden:
            assert needle not in literal, f"scope.py hard-codes {needle!r} in {literal!r}"


# --- the readers underneath the laws --------------------------------------------------
#
# The six laws are exercised above. The helpers they are built from — the kind lookup, the
# registry readers, the subject resolver's error arms and the two ledger walks — are reached
# only through a repository whose registries are all present, well formed and in agreement,
# so each helper's "and if it is not" arm had never executed.


def test_an_undeclared_kind_is_absent_rather_than_invented(policy):
    """The lookup answers None for a kind the policy does not declare.

    Every caller in this module asks about a kind that classification just produced, so the
    miss arm was dead — and returning anything other than None (the first kind, a synthetic
    one) would give an undeclared kind an enforcement mode nobody wrote down.
    """
    declared = policy.kinds[0]

    assert policy.kind(declared.object_kind) is declared
    assert policy.kind("A-KIND-NO-POLICY-DECLARES") is None


def test_a_registry_that_cannot_be_read_is_absent_and_never_empty(tmp_path):
    """READING IS BEST-EFFORT AND THE ABSENCE IS THE ANSWER.

    ``load_context`` turns each None into an empty registry with ``or {}``, so an unreadable
    registry and an empty one are treated alike at the call site — but only after the reader
    has said which it was. All four refusals matter: a file that is not there, a directory
    where a file was expected, one the process may not read, and one that is not JSON. Any of
    them raising instead would make the scope gate unusable on a partial checkout; any of
    them returning ``{}`` from inside the reader would be indistinguishable from a registry
    that exists and declares nothing.
    """
    assert scope._read_json(str(tmp_path), "absent.json") is None
    assert scope._read_json(str(tmp_path), ".") is None

    malformed = tmp_path / "malformed.json"
    malformed.write_text("{ not json", encoding="utf-8")
    assert scope._read_json(str(tmp_path), "malformed.json") is None

    good = tmp_path / "good.json"
    good.write_text('{"a": 1}', encoding="utf-8")
    assert scope._read_json(str(tmp_path), "good.json") == {"a": 1}


def test_a_subject_rule_that_cannot_be_compiled_or_applied_resolves_nothing(policy):
    """A SELECTOR THAT CANNOT BE EVALUATED MATCHES NOTHING — it never matches everything.

    Two arms, both dead against the declared policy because every rule in it compiles and
    every ``path_from`` it names is implemented. A pattern that is not a valid regular
    expression is skipped rather than allowed to raise out of a resolver that walks the whole
    ledger, and a rule naming a path form this module does not implement resolves to None
    rather than falling through to the next rule — because the namespace already matched, and
    continuing would resolve the urn under a rule that was not written for it.
    """
    urn = "urn:ucos:ucko:test.namespace:SOMETHING"

    uncompilable = dataclasses.replace(
        policy.subject_rules[0],
        namespace="test.namespace",
        local_name_pattern="(unclosed",
    )
    assert resolve_subject(dataclasses.replace(policy, subject_rules=(uncompilable,)), urn) is None

    unimplemented = dataclasses.replace(
        policy.subject_rules[0],
        namespace="test.namespace",
        local_name_pattern=".",
        path_from="a_path_form_nothing_implements",
    )
    assert resolve_subject(dataclasses.replace(policy, subject_rules=(unimplemented,)), urn) is None


def test_a_test_suite_on_disk_but_not_in_the_registry_is_found_by_walking(policy, tmp_path):
    """REGISTRY LAG IS A LEGITIMATE STATE, and the walk is what keeps it from reading as a
    missing subject.

    A test suite added in a change is on disk immediately and enters the object registry
    later, so the index is the fast path and the filesystem is the truth. Every existing case
    resolves through the index, which left the whole fallback — the walk, the ``.git`` skip
    and the not-found answer — unexecuted. The ``.git`` skip is not an optimisation: a
    checkout's object store holds files under arbitrary names, and matching one would report
    a subject as present because git happened to be storing something.
    """
    rule = next(r for r in policy.subject_rules if r.path_from == "test_basename")
    repo = str(tmp_path)
    (tmp_path / "suite").mkdir()
    (tmp_path / "suite" / "test_walked.py").write_text("", encoding="utf-8")
    (tmp_path / ".git" / "objects").mkdir(parents=True)
    (tmp_path / ".git" / "objects" / "test_hidden.py").write_text("", encoding="utf-8")

    # the index answers first, and answers without touching the filesystem
    assert scope._subject_exists(repo, rule, "test_indexed.py", {"test_indexed.py": ["x/y.py"]})
    # absent from the index, present on disk
    assert scope._subject_exists(repo, rule, "test_walked.py", {})
    # present only inside .git, which is not the repository's content
    assert not scope._subject_exists(repo, rule, "test_hidden.py", {})
    assert not scope._subject_exists(repo, rule, "test_never_written.py", {})


def test_the_registry_lookup_scans_when_it_is_handed_no_index(ctx):
    """THE INDEX IS AN OPTIMISATION AND THE SCAN IS THE DEFINITION.

    ``load_context`` always builds ``by_path``, so the scan below it had no caller — and it
    is what keeps ``_object_at`` correct for a context assembled any other way, including the
    hand-built contexts these laws are tested against. An index-only lookup would answer None
    for every object in such a context and every law reading it would silently see an empty
    repository.
    """
    path = str(ctx["objects"][0]["path"])
    without_index = {k: v for k, v in ctx.items() if k != "by_path"}

    assert scope._object_at(path, without_index) == ctx["by_path"][path]
    assert scope._object_at("no/such/path.txt", without_index) is None
    assert scope._object_at("no/such/path.txt", ctx) is None


def test_a_birth_no_rule_resolves_is_skipped_by_both_ledger_readers(policy, ctx):
    """A URN THE POLICY CANNOT PLACE IS NOT A PATH AND NOT A SUBJECT CLASS.

    Every birth in the committed ledger resolves — BSP-L-04 refuses one that does not — so
    both walks had only ever seen resolvable urns. Counting an unresolvable one anyway would
    put ``None`` into the born-path set (making coverage look higher than it is) or into the
    subject-class histogram under a key nothing declared.
    """
    unresolvable = "urn:ucos:ucko:namespace.no.rule.declares:SUBJECT"
    unknown = {**ctx, "births": {unresolvable: {}}}

    assert scope._born_paths(policy, unknown) == set()
    assert scope._births_by_subject_class(policy, unknown) == {}


def test_the_born_path_cache_is_only_written_where_it_can_be_written(policy, ctx):
    """THE CACHE IS AN OPTIMISATION AND MUST NEVER BE A REQUIREMENT.

    The result is memoised into the context, which is a plain dict on every real call — so
    the guard was dead. A read-only mapping is a legitimate context (it is how a caller says
    "answer about this, do not touch it"), and writing into one would raise from inside a
    helper whose contract is to read. The answer is identical either way; only the cache is
    not kept.
    """
    read_only = MappingProxyType(dict(ctx))

    answer = scope._born_paths(policy, read_only)

    assert answer == scope._born_paths(policy, dict(ctx))
    assert "_born_paths" not in read_only


def test_a_birth_naming_a_generated_artifact_is_refused_by_bsp_l_04(policy, ctx):
    """BSP-L-04 HAS THREE VIOLATIONS AND ONLY TWO HAD RUN.

    An unresolvable urn and a subject that does not exist were both tested. The third is the
    one the determination exists for: a birth record naming a subject that RESOLVES, EXISTS
    and is a kind whose enforcement is MANDATORY_ABSENCE. That is a generated artifact given
    an independent constitutional identity — the precise failure §1.2 was written to prevent
    — and it cannot be caught by either of the other two arms, because nothing about the urn
    or the path is wrong.
    """
    # Derived, never named: the kind whose enforcement is MANDATORY_ABSENCE is DATA in the
    # policy, and the ``name_plus_md`` rule is the one subject form that can resolve to it.
    rule = next(r for r in policy.subject_rules if r.path_from == "name_plus_md")
    generated = next(
        str(obj["path"])
        for obj in ctx["objects"]
        if str(obj.get("path", "")).endswith(".md")
        and (kind := classify(policy, obj, ctx)) is not None
        and kind.enforcement == MANDATORY_ABSENCE
    )
    urn = f"urn:ucos:ucko:{rule.namespace}:{generated[: -len('.md')]}"

    violations = _run("every_birth_subject_may_be_born", policy, {**ctx, "births": {urn: {}}})

    assert any("may not be born" in v for v in violations), violations
    assert any(generated in v for v in violations)
