"""EX-016 — the classifier that makes EX-015's declared rules decidable.

The bar these tests hold is the one the register itself sets: a rule nobody evaluates is
prose, and prose is what let ``uisd-declaration.json`` be authored, owned, engine-consumed
and unclassified while six of its mutations were certified. So every declared rule is
exercised against a real subject, the terminal is exercised, and the two-sided coverage
check is exercised in both directions.

``UNRESOLVED`` is asserted to be diagnostic — never a class, never an authority, never a
default — because a permissive default is precisely how two mutation classes came to be
missing in the first place.
"""

from __future__ import annotations

import copy
import hashlib
import json
import subprocess
from pathlib import Path
from platform.repository_intelligence import mutation_classification as mc
from platform.repository_intelligence import mutation_gate as mg

import pytest

REPO = Path(__file__).resolve().parents[2]

UISD = "00-MASTER/UISD-000001/uisd-declaration.json"

#: The subject the terminal tests classify, and it deliberately names nothing that exists.
#: It used to be `README.md`, chosen because nothing classified it -- and then UCOS-UCTX-001
#: began emitting a README as a generated projection, the exclusion register gave it a class,
#: and three tests about the UNRESOLVED terminal started asserting that a correctly classified
#: artifact was unclassifiable. An example picked because the repository happens not to hold it
#: is a test that fails the day the repository grows one. No rule can ever claim this path: it
#: sits under no declared home and carries no declared extension.
UNCLASSIFIABLE = "no-such-declared-home/nothing-claims-this.unknown"


@pytest.fixture(scope="module")
def repo() -> mc.Repository:
    return mc.Repository(REPO)


@pytest.fixture(scope="module")
def boundary(repo: mc.Repository) -> dict:
    return mc.load_boundary(repo.root)


# ------------------------------------------------------------------ rule coverage


def test_every_declared_rule_has_a_predicate_and_every_predicate_a_rule(boundary: dict) -> None:
    """Two-sided, exactly like LAW_CHECKS: neither direction may drift."""
    assert mc.validate_rule_coverage(boundary) == ()


def test_a_declared_rule_with_no_predicate_is_refused(boundary: dict) -> None:
    doc = {"classification_rules": {"rules": [{"id": "R-99", "class": "X"}]}}
    problems = mc.validate_rule_coverage(doc)
    assert any("no predicate implements it" in p for p in problems)


def test_a_predicate_no_rule_declares_is_refused() -> None:
    doc = {"classification_rules": {"rules": [{"id": "R-01", "class": "REPOSITORY_STATE"}]}}
    problems = mc.validate_rule_coverage(doc)
    assert any("no rule declares it" in p for p in problems)


# ------------------------------------------------------- classes 0..5, each resolved


def test_class_0_constitutional_truth_resolves_from_an_object_subject(
    repo: mc.Repository, boundary: dict
) -> None:
    result = mc.classify(mc.Subject.of_object("population/alpha", "Population"), repo, boundary)
    assert result.status == mc.CLASSIFIED
    assert result.mutation_class == "CONSTITUTIONAL_TRUTH"
    assert result.rule_id == "R-05"
    assert result.authority == "UCOS-CMG-EXEC-000001"


def test_class_0_is_an_object_predicate_not_a_path_predicate(
    repo: mc.Repository, boundary: dict
) -> None:
    """A path never satisfies R-05; the register states the domain and the code honours it."""
    result = mc.classify("engine/constitution/gateway.py", repo, boundary)
    assert result.mutation_class != "CONSTITUTIONAL_TRUTH"


def test_class_1_source_resolves(repo: mc.Repository, boundary: dict) -> None:
    for path in ("engine/nucleus/lifecycle.py", "verify.sh", "pyproject.toml"):
        result = mc.classify(path, repo, boundary)
        assert result.status == mc.CLASSIFIED, path
        assert result.mutation_class == "SOURCE", path
        assert result.rule_id == "R-07", path


def test_class_2_generated_artifact_resolves(repo: mc.Repository, boundary: dict) -> None:
    result = mc.classify("intelligence/UCOS-RIE-MODEL.json", repo, boundary)
    assert result.status == mc.CLASSIFIED
    assert result.mutation_class == "GENERATED_ARTIFACT"
    assert result.rule_id == "R-04"


def test_class_3_exclusion_resolves(repo: mc.Repository, boundary: dict) -> None:
    result = mc.classify(".gitignore", repo, boundary)
    assert result.status == mc.CLASSIFIED
    assert result.mutation_class == "EXCLUSION"
    assert result.rule_id == "R-02"


def test_class_4_repository_state_resolves(repo: mc.Repository, boundary: dict) -> None:
    result = mc.classify(".git/index", repo, boundary)
    assert result.status == mc.CLASSIFIED
    assert result.mutation_class == "REPOSITORY_STATE"
    assert result.rule_id == "R-01"


def test_class_5_corpus_registration_resolves(repo: mc.Repository, boundary: dict) -> None:
    for path in ("00-BOOK/DATA/id-ledger.json", "00-BOOK/DATA/artifacts.json"):
        result = mc.classify(path, repo, boundary)
        assert result.status == mc.CLASSIFIED, path
        assert result.mutation_class == "CORPUS_REGISTRATION", path
        assert result.rule_id == "R-03", path


# --------------------------------------------------------------- class 6, positive


def test_class_6_the_uisd_declaration_resolves_to_governed_declaration(
    repo: mc.Repository, boundary: dict
) -> None:
    """The artifact whose unclassifiability was the whole reason for EX-015 and EX-016."""
    result = mc.classify(UISD, repo, boundary)
    assert result.status == mc.CLASSIFIED
    assert result.mutation_class == "GOVERNED_DECLARATION"
    assert result.rule_id == "R-06"
    assert "owning programme" in result.authority


def test_class_6_every_declared_example_resolves(repo: mc.Repository, boundary: dict) -> None:
    examples = next(
        e["examples"] for e in boundary["mutation_classes"] if e["class"] == "GOVERNED_DECLARATION"
    )
    assert examples, "the class declares no example, so this test would be vacuous"
    for path in examples:
        result = mc.classify(path, repo, boundary)
        assert result.mutation_class == "GOVERNED_DECLARATION", f"{path}: {result.reason}"


def test_class_6_evaluates_criteria_and_never_matches_on_examples(
    repo: mc.Repository, boundary: dict
) -> None:
    """Examples are documentation. Membership is the seven criteria, each computed."""
    checks = mc.governed_declaration_checks(UISD, repo.declaration_document(UISD), repo)
    declared = next(
        e["membership_criteria"]
        for e in boundary["mutation_classes"]
        if e["class"] == "GOVERNED_DECLARATION"
    )
    assert len(checks) == len(declared)
    assert all(checks.values()), checks


# --------------------------------------------------------------- class 6, negative


def test_executable_source_is_not_a_governed_declaration(
    repo: mc.Repository, boundary: dict
) -> None:
    checks = mc.governed_declaration_checks("engine/nucleus/lifecycle.py", None, repo)
    assert checks["non-executable"] is False
    assert mc.classify("engine/nucleus/lifecycle.py", repo, boundary).mutation_class == "SOURCE"


def test_a_generated_artifact_is_not_a_governed_declaration(
    repo: mc.Repository, boundary: dict
) -> None:
    path = "intelligence/UCOS-RIE-MODEL.json"
    checks = mc.governed_declaration_checks(path, repo.declaration_document(path), repo)
    assert checks["non-generated"] is False
    assert mc.classify(path, repo, boundary).mutation_class == "GENERATED_ARTIFACT"


def test_an_artifact_with_no_owning_programme_is_not_a_governed_declaration(
    repo: mc.Repository, tmp_path: Path
) -> None:
    """Criterion 4 fails closed: no owner, no class. CEP-009 I.3 keeps ownership single."""
    document = {"laws": [{"id": "X"}]}
    checks = mc.governed_declaration_checks("nowhere/orphan.json", document, repo)
    assert checks["programme-owned"] is False


def test_a_declaration_bearing_file_outside_version_control_is_refused(
    repo: mc.Repository,
) -> None:
    checks = mc.governed_declaration_checks(
        "00-MASTER/NOT-TRACKED/x.json", {"programme": {"id": "P"}}, repo
    )
    assert checks["repository-controlled"] is False


# --------------------------------------------------------------- class 7, positive

ADR_DECIDERS = "adr/0003-constitutional-binding-of-ceu-and-ucxi.md"
CONSTITUTION_AUTHORITY = "00-CEP/CEP-002-CONSTITUTIONAL-GOVERNANCE-CONSTITUTION.md"
DETERMINATION_NO_AUTHORITY = "adr/0002-aeos-phase-1-architectural-determination.md"


def test_class_7_an_adr_using_the_deciders_convention_resolves(
    repo: mc.Repository, boundary: dict
) -> None:
    """Authored document classification — the ADR convention (Deciders, table form)."""
    result = mc.classify(ADR_DECIDERS, repo, boundary)
    assert result.status == mc.CLASSIFIED
    assert result.mutation_class == "AUTHORED_DOCUMENT"
    assert result.rule_id == "R-08"


def test_class_7_a_constitution_using_the_authority_convention_resolves(
    repo: mc.Repository, boundary: dict
) -> None:
    """Authored document classification — the constitution convention (AUTHORITY, table form,
    uppercase label — the field-name match is case-insensitive)."""
    result = mc.classify(CONSTITUTION_AUTHORITY, repo, boundary)
    assert result.status == mc.CLASSIFIED
    assert result.mutation_class == "AUTHORED_DOCUMENT"
    assert result.rule_id == "R-08"


def test_class_7_ownership_resolution_reads_the_documents_own_declaration(
    repo: mc.Repository,
) -> None:
    """Canonical owner: read from the artifact, Authority checked before Deciders."""
    assert mc.authored_document_owner(ADR_DECIDERS, repo) == "Constitutional Authority · UCOS Ω∞"
    owner = mc.authored_document_owner(CONSTITUTION_AUTHORITY, repo)
    assert owner.startswith("Supreme over all governance operation")


def test_class_7_authority_resolution_names_the_owner_parameterised_chain(
    repo: mc.Repository, boundary: dict
) -> None:
    """The fixed governance chain (Class 6's own pattern) plus the per-document owner."""
    result = mc.classify(ADR_DECIDERS, repo, boundary)
    assert "owner-parameterised" in result.authority
    assert "self-declared" in result.authority or "declares" in result.authority


def test_class_7_lifecycle_is_read_from_the_documents_own_status_field(
    repo: mc.Repository,
) -> None:
    """Lifecycle handling: open vocabulary, whatever the document states of itself."""
    assert mc.authored_document_lifecycle(ADR_DECIDERS, repo) == "Accepted"


def test_class_7_evaluates_criteria_and_never_matches_on_examples(
    repo: mc.Repository, boundary: dict
) -> None:
    """Examples are documentation, exactly like Class 6. Membership is the five criteria."""
    checks = mc.authored_document_checks(ADR_DECIDERS, repo)
    declared = next(
        e["membership_criteria"]
        for e in boundary["mutation_classes"]
        if e["class"] == "AUTHORED_DOCUMENT"
    )
    assert len(checks) == len(declared)
    assert all(checks.values()), checks


# --------------------------------------------------------------- class 7, negative
# and fail-closed classification


def test_class_7_a_document_declaring_no_authority_or_deciders_is_unresolved(
    repo: mc.Repository, boundary: dict
) -> None:
    """Fail-closed: a determination document that states 'AUTHORITY = NONE' inline prose,
    not as a self-declared Authority/Deciders field, earns no class rather than one by
    default — the same discipline GOVERNED_DECLARATION applies to an ownerless JSON file."""
    checks = mc.authored_document_checks(DETERMINATION_NO_AUTHORITY, repo)
    assert checks["self-declared-authority"] is False
    result = mc.classify(DETERMINATION_NO_AUTHORITY, repo, boundary)
    assert result.mutation_class != "AUTHORED_DOCUMENT"
    assert result.status == mc.UNRESOLVED


def test_class_7_a_json_declaration_is_never_also_an_authored_document(
    repo: mc.Repository, boundary: dict
) -> None:
    """Structural exclusivity: R-06 (JSON declaration) precedes R-08, and a JSON path never
    satisfies the markdown criterion — the two classes cannot both claim one subject."""
    assert mc.authored_document_checks(UISD, repo)["markdown"] is False
    result = mc.classify(UISD, repo, boundary)
    assert result.mutation_class == "GOVERNED_DECLARATION"


def test_class_7_a_source_file_is_never_an_authored_document(
    repo: mc.Repository, boundary: dict
) -> None:
    checks = mc.authored_document_checks("engine/nucleus/lifecycle.py", repo)
    assert checks["markdown"] is False
    assert mc.classify("engine/nucleus/lifecycle.py", repo, boundary).mutation_class == "SOURCE"


def test_class_7_an_untracked_markdown_document_is_refused(repo: mc.Repository) -> None:
    checks = mc.authored_document_checks("nowhere/orphan.md", repo)
    assert checks["repository-controlled"] is False


def test_class_7_no_duplicate_mutation_authority_with_class_6(boundary: dict) -> None:
    """The invariant test_2 in test_mutation_governance_boundary.py checks this at the
    register level; this checks it at the classifier level — the two owner-parameterised
    classes (6 and 7) never resolve the same subject, and their governed_by chains, while
    both owner-parameterised, are declared as two distinct class entries, never one merged
    authority."""
    classes = [e["class"] for e in boundary["mutation_classes"]]
    assert classes.count("GOVERNED_DECLARATION") == 1
    assert classes.count("AUTHORED_DOCUMENT") == 1
    governed_decl = mc.authority_for(boundary, "GOVERNED_DECLARATION")
    authored_doc = mc.authority_for(boundary, "AUTHORED_DOCUMENT")
    assert governed_decl != authored_doc


# ------------------------------------------------------------------- the terminal


def test_an_unknown_artifact_returns_unresolved(repo: mc.Repository, boundary: dict) -> None:
    result = mc.classify(UNCLASSIFIABLE, repo, boundary)
    assert result.status == mc.UNRESOLVED
    assert result.mutation_class == ""
    assert result.rule_id == ""
    assert result.authority == ""
    assert "FAILS CLOSED" in result.reason


def test_unresolved_confers_no_class_and_no_authority(repo: mc.Repository, boundary: dict) -> None:
    """UNRESOLVED is diagnostic. It must never read as a permissive default."""
    declared = {e["class"] for e in boundary["mutation_classes"]}
    result = mc.classify(UNCLASSIFIABLE, repo, boundary)
    assert result.mutation_class not in declared
    assert mc.UNRESOLVED not in declared


def test_unresolved_reports_the_subjects_for_a_fail_closed_consumer(
    repo: mc.Repository,
) -> None:
    results = mc.classify_all([UNCLASSIFIABLE, UISD], repo)
    assert mc.unresolved(results) == (UNCLASSIFIABLE,)


# -------------------------------------------------------------------- determinism


def test_repeated_evaluation_is_identical(repo: mc.Repository, boundary: dict) -> None:
    for path in (UISD, "engine/nucleus/lifecycle.py", UNCLASSIFIABLE, ".gitignore"):
        first = mc.classify(path, repo, boundary)
        second = mc.classify(path, repo, boundary)
        assert first == second, path


def test_result_is_independent_of_the_order_subjects_are_presented(
    repo: mc.Repository,
) -> None:
    forward = mc.classify_all([UISD, UNCLASSIFIABLE, ".gitignore"], repo)
    reverse = mc.classify_all([".gitignore", UNCLASSIFIABLE, UISD], repo)
    assert forward == reverse


def test_a_second_repository_view_of_the_same_state_agrees(boundary: dict) -> None:
    """No cached state leaks between views; the result is a function of the repository."""
    a, b = mc.Repository(REPO), mc.Repository(REPO)
    assert mc.classify(UISD, a, boundary) == mc.classify(UISD, b, boundary)


def test_the_result_carries_no_clock_or_environment(repo: mc.Repository, boundary: dict) -> None:
    payload = mc.classify(UISD, repo, boundary).to_dict()
    assert set(payload) == {
        "artifact",
        "mutation_class",
        "rule_id",
        "authority",
        "status",
        "reason",
    }


# ------------------------------------------------------------------------- faults


def test_an_unreadable_boundary_is_an_error_not_a_classification(tmp_path: Path) -> None:
    result = mc.classify("anything", mc.Repository(tmp_path))
    assert result.status == mc.ERROR
    assert result.mutation_class == ""


def test_a_boundary_without_classification_rules_fails_closed(tmp_path: Path) -> None:
    target = tmp_path / "00-BOOK" / "DATA"
    target.mkdir(parents=True)
    (target / "mutation-governance-boundary.json").write_text("{}", encoding="utf-8")
    with pytest.raises(mc.ClassificationError):
        mc.load_boundary(tmp_path)


# ------------------------------------------------- hermetic views and fault paths
#
# Repository._overrides exists so a test can state a repository rather than discover one.
# Exercising it here is what keeps these cases hermetic: no git, no filesystem walk, and a
# subject whose classification depends only on the stated view.


def _view(**overrides: object) -> mc.Repository:
    base: dict[str, object] = {
        "tracked": set(),
        "generated": set(),
        "producer_homes": set(),
        "python_corpus": "",
    }
    base.update(overrides)
    return mc.Repository(REPO, base)


def test_a_stated_view_drives_classification_without_touching_git(boundary: dict) -> None:
    view = _view(
        tracked={"00-MASTER/X-000001/x-declaration.json"}, python_corpus='"x-declaration.json"'
    )
    result = mc.classify("00-MASTER/X-000001/x-declaration.json", view, boundary)
    assert result.status in {mc.CLASSIFIED, mc.UNRESOLVED}
    assert view.tracked == {"00-MASTER/X-000001/x-declaration.json"}
    assert view.generated == frozenset()
    assert view.producer_homes == frozenset()


def test_a_generated_path_in_the_stated_view_wins_precedence(boundary: dict) -> None:
    view = _view(generated={"00-MASTER/X-000001/x-declaration.json"})
    result = mc.classify("00-MASTER/X-000001/x-declaration.json", view, boundary)
    assert result.mutation_class == "GENERATED_ARTIFACT"
    assert result.rule_id == "R-04"


def test_an_unparseable_json_artifact_is_not_declaration_bearing(repo: mc.Repository) -> None:
    assert repo.declaration_document("engine/nucleus/lifecycle.py") is None
    assert repo.declaration_document("00-BOOK/DATA/does-not-exist.json") is None


def test_object_subjects_are_refused_by_path_only_rules(
    repo: mc.Repository, boundary: dict
) -> None:
    """R-01 and R-06 are path predicates; an object subject must fall through them."""
    subject = mc.Subject.of_object("population/beta", "NotAConstitutionalType")
    result = mc.classify(subject, repo, boundary)
    assert result.status == mc.UNRESOLVED


def test_a_boundary_whose_rules_do_not_match_the_predicates_is_an_error(
    repo: mc.Repository,
) -> None:
    doc = {"classification_rules": {"rules": [{"id": "R-01", "class": "REPOSITORY_STATE"}]}}
    result = mc.classify("anything", repo, doc)
    assert result.status == mc.ERROR
    assert "no rule declares it" in result.reason


def test_a_predicate_that_raises_is_reported_as_a_fault_not_a_class(
    repo: mc.Repository, boundary: dict, monkeypatch: pytest.MonkeyPatch
) -> None:
    def explode(subject, repository, doc):  # noqa: ANN001, ANN202
        raise RuntimeError("predicate is unevaluable")

    monkeypatch.setitem(mc.RULE_PREDICATES, "R-01", explode)
    result = mc.classify("anything", repo, boundary)
    assert result.status == mc.ERROR
    assert result.rule_id == "R-01"
    assert "RuntimeError" in result.reason


def test_authority_for_an_unknown_class_is_empty(boundary: dict) -> None:
    assert mc.authority_for(boundary, "NO_SUCH_CLASS") == ""


# ------------------------------------------------- version-control path fidelity
# Regression cover for the tracked-path parsing defect: `git ls-files` C-quotes and
# octal-escapes any path holding a non-ASCII byte, so a tracked `…UCOS-Ω∞-…` artifact
# arrived as `"…UCOS-\316\251\342\210\236-…"` and never equalled its own path. It then
# tested as untracked, and because R-01 claims any existing path absent from `tracked`,
# 117 real artifacts were absorbed into REPOSITORY_STATE before the rule that owns them
# was ever evaluated — a WRONG authority, strictly worse than the fail-closed terminal.
#
# Every test above this line drives `Repository` through `_overrides["tracked"]` with
# ASCII-only fixtures, which is precisely why none of them could see the defect. These
# drive the real `git ls-files` subprocess against real non-ASCII names.

#: Tracked, non-generated, non-ASCII. Declares no Authority/Deciders field, so Class 7
#: correctly refuses it and it fails closed — the point is that it is not REPOSITORY_STATE.
OMEGA_NO_AUTHORITY = "02-MASTER/UCOS-Ω∞-TECHNOLOGY-CONSTITUTION.md"

#: Tracked, non-generated, non-ASCII, and self-declaring an Authority — resolves to Class 7.
OMEGA_AUTHORED = "02-MASTER/UCOS-Ω∞-ABSOLUTE-IDENTITY-FEDERATION-AND-CONTINUITY-CONSTITUTION.md"


def _git_repo_with(tmp_path: Path, *names: str) -> Path:
    """A real git work tree holding real files, staged. Index alone drives `ls-files`."""
    subprocess.run(  # noqa: S603
        ["git", "init", "-q"],  # noqa: S607 — resolved from PATH, as the module under test does
        cwd=tmp_path,
        check=True,
    )
    for name in names:
        target = tmp_path / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("# fixture\n", encoding="utf-8")
    subprocess.run(  # noqa: S603
        ["git", "add", "-A"],  # noqa: S607 — resolved from PATH, as the module under test does
        cwd=tmp_path,
        check=True,
    )
    return tmp_path


def test_a_non_ascii_tracked_path_is_read_unescaped_from_version_control(
    tmp_path: Path,
) -> None:
    """The parsing correction itself, against the real subprocess.

    Asserted on the *real path*, and on the absence of any escaped form — a fix that
    merely unquoted the outer quotes would still leave the octal escapes behind.
    """
    root = _git_repo_with(tmp_path, "UCOS-Ω∞-FIXTURE.md", "plain-ascii.md")
    tracked = mc.Repository(root).tracked

    assert "UCOS-Ω∞-FIXTURE.md" in tracked
    assert "plain-ascii.md" in tracked, "ASCII paths must be unaffected by the correction"
    assert not any(p.startswith('"') for p in tracked), f"a quoted path survived: {tracked}"
    assert not any(
        "\\316" in p or "\\342" in p for p in tracked
    ), f"an octal-escaped path survived: {tracked}"


def test_an_omega_infinity_document_is_not_absorbed_into_repository_state(
    repo: mc.Repository, boundary: dict
) -> None:
    """The defect's actual consequence, on a real repository artifact.

    Before the correction this resolved to REPOSITORY_STATE via R-01 — governed by
    UCOS-RIB-001 GATE-02/12 rather than by its own authority. It declares no
    Authority/Deciders field, so the correct outcome is the fail-closed terminal: no
    authority, rather than someone else's.
    """
    assert OMEGA_NO_AUTHORITY in repo.tracked

    result = mc.classify(OMEGA_NO_AUTHORITY, repo, boundary)
    assert result.mutation_class != "REPOSITORY_STATE"
    assert result.status == mc.UNRESOLVED
    assert result.authority == "", "the terminal confers no authority"


def test_an_omega_infinity_authored_document_resolves_to_class_7(
    repo: mc.Repository, boundary: dict
) -> None:
    """Authored-document detection survives the correction for non-ASCII paths.

    R-08 requires `repository-controlled`, which is exactly the criterion the defect
    falsified — so a self-declaring Ω∞ constitution could never reach Class 7 before.
    """
    checks = mc.authored_document_checks(OMEGA_AUTHORED, repo)
    assert checks["repository-controlled"] is True
    assert all(checks.values()), checks

    result = mc.classify(OMEGA_AUTHORED, repo, boundary)
    assert result.status == mc.CLASSIFIED
    assert result.mutation_class == "AUTHORED_DOCUMENT"
    assert result.rule_id == "R-08"
    assert mc.authored_document_owner(OMEGA_AUTHORED, repo) != ""


def test_an_untracked_path_is_still_detected_as_untracked(tmp_path: Path) -> None:
    """The correction must not weaken the check it repairs.

    A path git does not carry must stay outside `tracked` — in a synthetic tree and in
    the real repository — or R-01's precedence and Class 6/7's `repository-controlled`
    criterion would both silently become permissive.
    """
    root = _git_repo_with(tmp_path, "UCOS-Ω∞-STAGED.md")
    (root / "UCOS-Ω∞-UNSTAGED.md").write_text("# not added\n", encoding="utf-8")
    tracked = mc.Repository(root).tracked

    assert "UCOS-Ω∞-STAGED.md" in tracked
    assert "UCOS-Ω∞-UNSTAGED.md" not in tracked

    real = mc.Repository(REPO)
    assert "nowhere/orphan.md" not in real.tracked
    assert "02-MASTER/UCOS-Ω∞-DOES-NOT-EXIST.md" not in real.tracked


def test_repository_state_claims_only_genuinely_untracked_paths(
    repo: mc.Repository, boundary: dict
) -> None:
    """R-01 precedence, both directions.

    R-01 runs first, so if it over-claims nothing downstream is ever consulted. It must
    claim an existing-but-untracked path, and must NOT claim a tracked one — including a
    tracked non-ASCII one, which is the case the defect inverted.
    """
    subject = mc.Subject.of_path(OMEGA_NO_AUTHORITY)
    assert mc._r01_repository_state(subject, repo, boundary) is False

    untracked = mc.Subject.of_path(".git/HEAD")
    assert mc._r01_repository_state(untracked, repo, boundary) is True
    assert mc.classify(untracked, repo, boundary).mutation_class == "REPOSITORY_STATE"

    for path in (OMEGA_NO_AUTHORITY, OMEGA_AUTHORED):
        assert mc.classify(path, repo, boundary).mutation_class != "REPOSITORY_STATE"


# ------------------------------------------------- reachability: the third coverage side
#
# THE DEFECT THESE PIN. R-09 was declared, implemented, covered — and unreachable. Its six
# criteria are R-08's five plus `analysis-artifact`, so R-09 strictly implied R-08, and R-08
# was evaluated first. GOVERNED_ANALYSIS claimed 0 of 6751 tracked paths while
# `validate_rule_coverage` reported no problem and this suite passed 49/49, because nothing
# here named R-09 at all. A two-sided declared/implemented check cannot see a rule that is
# both and still cannot fire; these tests are the side that can.


def test_a_shadowed_rule_is_refused_as_unreachable(boundary: dict) -> None:
    """The exact historical defect, reconstructed: R-08 before R-09 makes Class 8 empty."""
    doc = copy.deepcopy(boundary)
    for rule in doc["classification_rules"]["rules"]:
        if rule["id"] == "R-08":
            rule["precedence"] = 8
        elif rule["id"] == "R-09":
            rule["precedence"] = 9
    problems = mc.validate_rule_reachability(doc)
    assert any("'R-09'" in p and "can never match" in p for p in problems)
    assert any("'R-08'" in p and "plus ['analysis-artifact']" in p for p in problems)


def test_an_unreachable_rule_makes_classify_fail_closed(
    repo: mc.Repository, boundary: dict
) -> None:
    """A shadowed register yields ERROR, never a quietly wrong class. FAULT, not verdict."""
    doc = copy.deepcopy(boundary)
    for rule in doc["classification_rules"]["rules"]:
        if rule["id"] == "R-08":
            rule["precedence"] = 8
        elif rule["id"] == "R-09":
            rule["precedence"] = 9
    result = mc.classify("SELF-COVERAGE-GAPS.md", repo, doc)
    assert result.status == mc.ERROR
    assert result.mutation_class == ""
    assert "can never match" in result.reason


def test_two_rules_sharing_a_precedence_are_refused(boundary: dict) -> None:
    """An undefined order over overlapping predicates makes a class depend on file layout."""
    doc = copy.deepcopy(boundary)
    for rule in doc["classification_rules"]["rules"]:
        if rule["id"] == "R-08":
            rule["precedence"] = 8
    problems = mc.validate_rule_reachability(doc)
    assert any("both declare precedence 8" in p for p in problems)


def test_a_rule_with_no_usable_precedence_is_refused(boundary: dict) -> None:
    doc = copy.deepcopy(boundary)
    for rule in doc["classification_rules"]["rules"]:
        if rule["id"] == "R-09":
            rule["precedence"] = "eighth"
    problems = mc.validate_rule_reachability(doc)
    assert any("no usable precedence" in p for p in problems)


def test_precedence_decides_evaluation_order_not_the_array_order(boundary: dict) -> None:
    """`precedence` is the only order there is.

    `classify` once iterated the JSON array, so the declared field was authoritative only
    while somebody kept the array hand-sorted. Reversing the array must change nothing.
    """
    doc = copy.deepcopy(boundary)
    doc["classification_rules"]["rules"].reverse()
    assert [r["id"] for r in mc.ordered_rules(doc)] == [r["id"] for r in mc.ordered_rules(boundary)]


def test_r09_precedes_r08_so_neither_class_is_vacuous(boundary: dict) -> None:
    """Specific before general. The reverse order is the only one that empties a class."""
    order, problems = mc.rule_precedence(boundary)
    assert problems == ()
    assert order["R-09"] < order["R-08"]


def test_an_artifact_satisfying_both_classes_resolves_to_governed_analysis(
    repo: mc.Repository, boundary: dict
) -> None:
    """The witness that was classified AUTHORED_DOCUMENT while Class 8 claimed nothing."""
    target = "SELF-COVERAGE-GAPS.md"
    assert all(mc.governed_analysis_checks(target, repo, boundary).values())
    assert all(mc.authored_document_checks(target, repo).values())
    result = mc.classify(target, repo, boundary)
    assert result.status == mc.CLASSIFIED
    assert result.mutation_class == "GOVERNED_ANALYSIS"
    assert result.rule_id == "R-09"


# --------------------------------------------- population: reachable AND actually reached


def test_every_declared_rule_claims_a_subject_over_the_live_corpus(
    repo: mc.Repository, boundary: dict
) -> None:
    """Reachable in principle is not the same as reached in fact.

    A criterion narrowed until nothing satisfies it passes every static check and still
    classifies nothing. The register excuses exactly two rules, each with a stated reason;
    any other rule claiming zero is a refusal here.
    """
    results = mc.classify_all(sorted(repo.tracked), repo)
    assert mc.validate_rule_population(results, boundary) == ()


def test_governed_analysis_is_not_vacuous_over_the_live_corpus(repo: mc.Repository) -> None:
    """The measurement that was 0 of 6751. A regression here means Class 8 is empty again."""
    results = mc.classify_all(sorted(repo.tracked), repo)
    claimed = [r.artifact for r in results if r.mutation_class == "GOVERNED_ANALYSIS"]
    assert claimed, "GOVERNED_ANALYSIS claimed no subject: Class 8 is vacuous again"
    assert all(r.rule_id == "R-09" for r in results if r.mutation_class == "GOVERNED_ANALYSIS")


def test_a_rule_claiming_nothing_without_a_declared_reason_is_refused(
    repo: mc.Repository, boundary: dict
) -> None:
    """Withdraw R-09's excuse-free zero and the population check must notice."""
    doc = copy.deepcopy(boundary)
    doc["classification_rules"]["$rules_expected_to_claim_no_tracked_path"] = {}
    results = tuple(
        r for r in mc.classify_all(sorted(repo.tracked), repo) if r.rule_id not in {"R-09"}
    )
    problems = mc.validate_rule_population(results, doc)
    assert any("'R-09'" in p and "claimed no subject" in p for p in problems)


def test_a_stale_excuse_is_refused(repo: mc.Repository, boundary: dict) -> None:
    """An excuse that stops being true is itself a refusal, so the list cannot rot."""
    doc = copy.deepcopy(boundary)
    doc["classification_rules"]["$rules_expected_to_claim_no_tracked_path"]["R-07"] = "stale"
    results = mc.classify_all(sorted(repo.tracked), repo)
    problems = mc.validate_rule_population(results, doc)
    assert any("'R-07'" in p and "stale" in p for p in problems)


# ------------------------------------------------------------------ EX-018, the gate
#
# The classifier was decidable and decided nothing: one importer outside its own module, and
# no row in UEC-000001's inventory, so it and its register could both be deleted with every
# gate in the repository green. These pin the gate that closed that, including the two
# refusals whose distinction carries the meaning — CLOSED is "a law refused", FAULT is "no
# law could be measured", and collapsing them would let an unreadable register pass as
# whichever answer happened to be convenient.


def test_the_gate_is_open_on_the_live_register() -> None:
    report = mg.measure(REPO)
    assert report["verdict"] == "OPEN", report["laws"]
    assert [law["law_id"] for law in report["laws"]] == ["MGB-L-01", "MGB-L-02", "MGB-L-03"]
    assert all(law["holds"] for law in report["laws"])


def test_the_gate_reports_a_non_vacuous_governed_analysis_census() -> None:
    """The measurement that read 0. A census entry at zero here is Class 8 empty again."""
    report = mg.measure(REPO)
    assert report["census"]["GOVERNED_ANALYSIS"] > 0
    assert report["subjects"] > 0


def test_the_gate_reports_the_terminal_without_refusing_on_it() -> None:
    """UNRESOLVED is a governance question with an owner, not a defect this gate decides.

    Refusing on it would have the gate legislate a policy nobody adopted; hiding it would
    let the population grow unobserved. It is reported and does not move the verdict.
    """
    report = mg.measure(REPO)
    assert report["unresolved"] > 0
    assert report["verdict"] == "OPEN"
    assert "UNRESOLVED" in mg.render(report)


def test_an_unreadable_register_is_a_fault_not_a_closed_verdict(tmp_path) -> None:
    """Exit 2, never exit 1. No law was measured, which is not the same as one refusing."""
    with pytest.raises(mc.ClassificationError):
        mg.measure(tmp_path)
    assert mg.main(["--gate", "--repository", str(tmp_path)]) == mg.EXIT_FAULT


def test_the_gate_exits_open_on_the_live_register() -> None:
    assert mg.main(["--gate", "--quiet", "--repository", str(REPO)]) == mg.EXIT_OPEN


def test_the_gate_writes_nothing(tmp_path) -> None:
    """OBSERVE MODE, proven by hashing the register before and after rather than asserting it."""
    register = REPO / mc.BOUNDARY_PATH
    before = hashlib.sha256(register.read_bytes()).hexdigest()
    mg.main(["--json", "--quiet", "--repository", str(REPO)])
    assert hashlib.sha256(register.read_bytes()).hexdigest() == before


def test_two_measurements_of_one_state_are_identical() -> None:
    """Determinism: no clock, no environment, no traversal-order dependence."""
    assert mg.measure(REPO) == mg.measure(REPO)


# --- the gate's own refusals, over a register doctored one field at a time ----------------
#
# Every gate test above measures the LIVE register, which is complete and correct, so the
# arms that refuse an incomplete one never ran. The two-sided binding between declared laws
# and implemented measurements is the part that matters most and was the part with no test:
# it is the construction that stops a law from being declared and never evaluated, which is
# the exact defect — "a rule nobody evaluates is prose" — that this whole subsystem exists
# to end. A binding check nobody has seen refuse is prose about prose.


def _register(tmp_path: Path, boundary: dict) -> Path:
    """A real work tree holding nothing but a doctored boundary register.

    ``git init`` IS NOT OPTIONAL HERE. The population law classifies ``repository.tracked``,
    which is ``git ls-files``, so a plain directory makes the provider raise before any law
    is reached and the test would report a git failure instead of the refusal it is about.
    """
    root = tmp_path / "repo"
    (root / Path(mc.BOUNDARY_PATH).parent).mkdir(parents=True)
    (root / mc.BOUNDARY_PATH).write_text(json.dumps(boundary), encoding="utf-8")
    _git_repo_with(root)
    return root


def test_a_register_declaring_no_laws_is_a_fault_rather_than_an_open_gate(
    tmp_path: Path, boundary: dict
) -> None:
    """With no declared law the verdict would be this module's opinion, not a measurement.

    And it would be an OPEN one: nothing declared means nothing refused, so the failure mode
    of a benign answer here is a gate that passes on a register that governs nothing at all.
    """
    doctored = copy.deepcopy(boundary)
    doctored["gate"] = {"laws": []}
    with pytest.raises(mc.ClassificationError, match="declares no gate.laws"):
        mg.measure(str(_register(tmp_path, doctored)))


def test_a_declared_law_this_gate_cannot_measure_is_refused(tmp_path: Path, boundary: dict) -> None:
    """ "A declared law nobody evaluates is prose" — asserted against the gate itself.

    This is the register's own standard turned on the implementation that reads it: adding a
    law to the declaration and no measurement for it must fail loudly, or the register grows
    laws that are satisfied by not being checked.
    """
    doctored = copy.deepcopy(boundary)
    doctored["gate"]["laws"].append({"law_id": "MGB-L-99", "title": "measured by nothing"})
    with pytest.raises(mc.ClassificationError, match="MGB-L-99"):
        mg.measure(str(_register(tmp_path, doctored)))


def test_a_measurement_no_declaration_claims_is_refused(tmp_path: Path, boundary: dict) -> None:
    """The other direction, and the one a reader is likelier to forget. A finding attributed
    to no declared law is a verdict attributable to nothing — the gate would refuse, and the
    register a reader consults to find out why would not mention the law that refused."""
    doctored = copy.deepcopy(boundary)
    doctored["gate"]["laws"] = [
        law for law in doctored["gate"]["laws"] if law.get("law_id") != "MGB-L-03"
    ]
    with pytest.raises(mc.ClassificationError, match="MGB-L-03"):
        mg.measure(str(_register(tmp_path, doctored)))


def test_a_coverage_failure_stops_the_population_measurement_from_running(
    tmp_path: Path, boundary: dict
) -> None:
    """ORDERING, AND WHY IT IS NOT AN OPTIMISATION. Reading criteria functions for a rule that
    has no predicate is not meaningful, so MGB-L-03 is not measured when MGB-L-01 has already
    refused. The report still carries all three laws, with the un-run one holding vacuously —
    a reader must be able to see that it was not the thing that refused.
    """
    doctored = copy.deepcopy(boundary)
    doctored["classification_rules"]["rules"].append(
        {"rule_id": "R-99", "class": "NOT_A_CLASS", "precedence": 99, "subject": "nothing"}
    )
    root = _register(tmp_path, doctored)
    report = mg.measure(str(root))
    laws = {law["law_id"]: law for law in report["laws"]}
    assert not laws["MGB-L-01"]["holds"], "the coverage law was supposed to refuse"
    assert laws["MGB-L-03"]["violations"] == []
    assert report["verdict"] != "OPEN"


def test_the_rendered_report_lists_each_violation_under_the_law_that_found_it(
    tmp_path: Path, boundary: dict
) -> None:
    """A refusal a reader cannot attribute is a refusal they cannot act on. The renderer's
    violation lines had never run, because every rendered report so far came from a register
    on which every law held."""
    doctored = copy.deepcopy(boundary)
    doctored["classification_rules"]["rules"].append(
        {"rule_id": "R-99", "class": "NOT_A_CLASS", "precedence": 99, "subject": "nothing"}
    )
    report = mg.measure(str(_register(tmp_path, doctored)))
    rendered = mg.render(report)
    assert "REFUSED" in rendered
    assert "MGB-L-01" in rendered
    for violation in report["laws"][0]["violations"]:
        assert violation in rendered


def test_quiet_suppresses_the_report_only_while_the_gate_is_open(
    tmp_path: Path, boundary: dict, capsys: pytest.CaptureFixture[str]
) -> None:
    """``--quiet`` is for the passing case. A CLOSED gate prints regardless, because the whole
    point of the exit code is to send somebody to the reason for it."""
    assert mg.main(["--quiet", "--repository", str(REPO)]) == mg.EXIT_OPEN
    assert capsys.readouterr().out == ""

    doctored = copy.deepcopy(boundary)
    doctored["classification_rules"]["rules"].append(
        {"rule_id": "R-99", "class": "NOT_A_CLASS", "precedence": 99, "subject": "nothing"}
    )
    root = _register(tmp_path, doctored)
    assert mg.main(["--quiet", "--gate", "--repository", str(root)]) == mg.EXIT_CLOSED
    assert "REFUSED" in capsys.readouterr().out


# --- the register is where the markers live, and the code must not restate them -----------


def test_the_analysis_markers_are_read_from_the_rule_that_declares_them(boundary: dict) -> None:
    """Class 8's filename markers come out of R-09's own predicate, never out of this module.

    That is what makes the criterion unable to drift from the rule it implements: the markers
    can change only by changing the declaration, so a reader who edits the register gets the
    behaviour the register now describes without touching any code.
    """
    markers = mc._analysis_markers(boundary)
    assert markers, "the live register declares no analysis markers"
    predicate = next(
        str(rule.get("predicate", ""))
        for rule in boundary["classification_rules"]["rules"]
        if str(rule.get("id")) == "R-09"
    )
    for marker in markers:
        assert marker in predicate


def test_a_rule_r09_that_states_no_alternation_is_a_fault_not_an_empty_vocabulary(
    boundary: dict,
) -> None:
    """AN EMPTY MARKER SET IS THE VACUITY THIS CLASSIFIER EXISTS TO REFUSE.

    Returning ``()`` would make ``analysis-artifact`` unsatisfiable, Class 8 would claim
    nothing, and every report would stay green while a whole mutation class quietly went
    empty — which is the exact shape of the defect that left two classes missing.
    """
    doctored = copy.deepcopy(boundary)
    for rule in doctored["classification_rules"]["rules"]:
        if str(rule.get("id")) == "R-09":
            rule["predicate"] = "a predicate naming no filename alternation at all"
    with pytest.raises(mc.ClassificationError, match="no filename-marker alternation"):
        mc._analysis_markers(doctored)


def test_a_register_with_no_rule_r09_cannot_answer_for_class_8(boundary: dict) -> None:
    """Falling off the end of the loop is a different fault from finding R-09 malformed, and
    both raise: "the register declares no rule R-09" tells the reader to add it, and the
    alternation message tells them to fix the one they have."""
    doctored = copy.deepcopy(boundary)
    doctored["classification_rules"]["rules"] = [
        rule for rule in doctored["classification_rules"]["rules"] if str(rule.get("id")) != "R-09"
    ]
    with pytest.raises(mc.ClassificationError, match="declares no rule R-09"):
        mc._analysis_markers(doctored)


def test_a_stated_view_can_supply_a_documents_text_without_a_filesystem(boundary: dict) -> None:
    """``markdown_texts`` is the override that makes a document's own declarations statable.

    Without it a test about what a document DECLARES has to write the document to disk, which
    makes it a test about the filesystem. With it the lifecycle, the authority and the
    deciders can be varied directly, and the classification depends on nothing else.
    """
    path = "00-MASTER/X-000001/ANALYSIS.md"
    view = _view(markdown_texts={path: "# Analysis\n\n**Status:** RATIFIED\n"})
    assert view.text_of(path) == "# Analysis\n\n**Status:** RATIFIED\n"
    # The label the classifier reads is `status`, matched case-insensitively, and the
    # vocabulary is OPEN: whatever the document states is the answer, never coerced into a
    # closed set the class does not declare.
    assert mc.authored_document_lifecycle(path, view) == "RATIFIED"
    assert mc.authored_document_lifecycle(path, _view(markdown_texts={path: "# no fields\n"})) == ""


def test_a_document_whose_text_cannot_be_read_declares_no_lifecycle() -> None:
    """ "Unreadable" and "declares nothing" have to give the same answer HERE and a different
    one elsewhere: the lifecycle is an open vocabulary, so ``""`` is a real value meaning the
    document states no stage. Raising would make an unreadable file un-classifiable rather
    than un-declared, and the classifier would fail on a repository it should simply report."""
    absent = "no-such-declared-home/nothing-is-here.md"
    view = _view()
    assert view.text_of(absent) is None
    assert mc.authored_document_lifecycle(absent, view) == ""
