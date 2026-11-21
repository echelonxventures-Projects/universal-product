"""UCI-000001 — non-vacuity suite for the certification integrity programme.

A gate with no reachable PASS state carries no evidentiary value, and neither does one with no
reachable FAIL state. This suite proves both directions for every law, and it proves them by
MUTATING the measured input rather than by calling the law with hand-built arguments: a law tested
against a fixture it never sees in production is a law tested against a different function.

WHAT IS PROVEN

  * the gate is OPEN on the measured working tree (a reachable PASS)
  * every law REFUSES when its debt grows by one (a reachable FAIL, per law)
  * the ratchet is ONE-sided — a repayment is accepted with no edit anywhere, because Ω-4 replaced
    a two-sided ceiling that refused any measurement below the declared value and so made every
    improvement a chore indistinguishable from a retreat
  * a declared ceiling that binds no measurement is refused
  * the coverage reader reproduces coverage.py's own totals, so it is reading and not guessing
  * the coverage comparison detects a single moved line, which is the granularity Rules 8/10/11
    depend on and the granularity a percentage comparison does not have
  * statement attribution PARTITIONS: object counts sum to the set the surface distributed
    (the AST statements, intersected with coverage's own countable lines when a report names
    the file), and never exceed the file's AST count
  * the shuffle plugin is inactive without a seed, reproducible with one, and genuinely reorders
  * the extraction seal is deterministic, and the fingerprint detects a moved tree
  * an empty or single shard partition is refused rather than silently measured

The suite deliberately does NOT run the test suite, build a virtualenv or measure coverage. Those
are the expensive measurements the programme exists to take; asserting them here would make this
file a second, slower copy of them.
"""

from __future__ import annotations

import ast
import copy
import dataclasses
import json
import os
import random
import re
import subprocess
import textwrap
from pathlib import Path
from typing import Any

import pytest

from engine.certification_integrity import (
    contract,
    coverage_data,
    immutable,
    inventory,
    pytest_shuffle,
    surface,
)
from engine.certification_integrity.equivalence import discover_test_modules, partition
from engine.certification_integrity.model import (
    FILE_ARCHIVED,
    FILE_EXECUTABLE,
    FILE_TEST,
    FILE_TOOLING,
    PLANE_TYPES,
    REMEDY,
    FileRecord,
    IntegrityError,
    Provenance,
    UncoveredLine,
)
from engine.universal_discovery import discovery as omega_discovery
from engine.universal_discovery import ratchet as omega_ratchet
from engine.universal_discovery import ratchet as ratchet_module
from engine.universal_discovery.model import OmegaError

REPO = Path(__file__).resolve().parents[3]


@pytest.fixture(scope="module")
def built() -> inventory.Inventory:
    """One inventory for the whole module. Building it is the expensive part, not the assertions."""
    return inventory.build(str(REPO))


@pytest.fixture(scope="module")
def declaration() -> contract.Declaration:
    return contract.load_declaration(str(REPO))


@pytest.fixture(scope="module")
def report() -> dict[str, Any]:
    """One measurement for the whole module. Rebuilding it per test cost 10s a time."""
    return contract.measure(str(REPO))


# --------------------------------------------------------------- the reachable PASS state


def test_the_gate_is_open_on_the_measured_working_tree(report: dict[str, Any]) -> None:
    """Without this, every refusal below could be asserting over nothing.

    THE SUBJECT IS THE WORKING TREE, NOT THE COMMIT, and saying so is the whole of this change.
    The `report` fixture is `contract.measure(str(REPO))`, which reads the checkout as it stands —
    committed, staged and modified content alike. This test was named for "the committed
    repository" and its failure message said so, which is true only when the tree happens to be
    clean. On a dirty tree it attributed uncommitted work to HEAD and sent a reader to `git log`
    for a cause sitting in `git status`; the measured refusal named `00-BOOK/tools/*` offenders
    that are present in the checkout and absent from the commit.

    MEASURING THE COMMIT INSTEAD WOULD MAKE THE OLD NAME TRUE AND THE TEST VACUOUS, which is why
    the name was corrected rather than the subject. A frozen extraction of HEAD carries HEAD's
    declaration, whose ratchet keys are NUMBERS — `contract` refuses that as a FAULT under Ω-4 —
    and carries no sealed state at all, so `best` is None, no bound can be exceeded, and no law
    can refuse. A test that cannot fail is not a guard.

    The assertion itself is unchanged: OPEN, or name every refusal.
    """
    state = immutable.fingerprint(str(REPO))
    refused = [law for law in report["laws"] if law["status"] == contract.REFUSED]
    assert report["status"] == contract.OPEN, (
        f"the WORKING TREE does not satisfy its own declaration — HEAD {state.head[:8]} with "
        f"{state.dirty_entries} uncommitted path(s), so this verdict is about the checkout and "
        f"not about the commit: {[(law['law'], law['detail']) for law in refused]}"
    )


def test_the_inventory_is_not_empty(built: inventory.Inventory) -> None:
    """A measurement over nothing reports no violations and means nothing."""
    assert len(built.files) > 1000, f"only {len(built.files)} files enumerated"
    assert len(built.objects) > 10000, f"only {len(built.objects)} objects enumerated"
    assert built.totals["executable_statements"] > 100000


def test_every_declared_ceiling_binds_a_measurement(
    declaration: contract.Declaration,
) -> None:
    assert set(declaration.ratchet) == set(contract.RATCHETED), (
        "the declaration and the measurement table disagree: "
        f"only declared {sorted(set(declaration.ratchet) - set(contract.RATCHETED))}; "
        f"only measured {sorted(set(contract.RATCHETED) - set(declaration.ratchet))}"
    )


def test_every_law_in_the_table_is_declared(declaration: contract.Declaration) -> None:
    """A law the declaration does not name is a law nobody agreed to."""
    declared = {law["id"] for law in declaration.raw["laws"]}
    bound = {law_id for law_id, _fn in contract.RATCHETED.values()}
    assert bound <= declared, f"laws measured but not declared: {sorted(bound - declared)}"


def test_no_law_is_non_blocking(declaration: contract.Declaration) -> None:
    """A law that can be switched off is reachable by the mutation it detects."""
    for law in declaration.raw["laws"]:
        assert law["blocking"] is True, f"{law['id']} is declared non-blocking"


# ------------------------------------------------------------------- NON-VACUITY, per law
# Each law is forged into failure by growing its own population by one.
#
# UNDER Ω-4 THE COMPARISON IS A DIRECTION, NOT A CEILING, so these tests supply the sealed state the
# comparison reads. What changed is which mutations refuse:
#
#   debt GROWS beyond the best-ever value          REFUSED, as before
#   debt is REPAID below the best-ever value       ACCEPTED — it used to be refused as "slack",
#                                                  which made every improvement fail the gate until
#                                                  somebody committed a new number. That fired on
#                                                  the commit introducing Ω: the denominator went
#                                                  from 65 to 64 and the gate closed.
#   the ratchet declares no KIND                   REFUSED, as before


def _sealed_state(declaration: contract.Declaration, **best: float) -> omega_ratchet.Ratchet:
    """A ratchet state holding ``best`` for the given metrics, with the declared kinds."""
    return omega_ratchet.Ratchet(
        {
            "best": dict(best),
            "kinds": {key: declaration.ratchet[key] for key in best if key in declaration.ratchet},
            "holds": {},
            "justifications": [],
            "floors": [],
        }
    )


@pytest.mark.parametrize("key", sorted(contract.RATCHETED))
def test_each_law_refuses_when_its_debt_grows(
    key: str, built: inventory.Inventory, declaration: contract.Declaration
) -> None:
    """One more offender than this repository's own best must refuse, and must name the law."""
    law_id, measurement = contract.RATCHETED[key]
    offenders = measurement(built)
    inflated = _inventory_with(built, key, offenders + ["invented/offender.py"])
    state = _sealed_state(declaration, **{key: float(len(offenders))})
    result = contract._ratcheted(inflated, declaration, key, state)
    assert result.status == contract.REFUSED, f"{law_id} tolerated a new violation"
    assert "REGRESSED" in result.detail
    assert result.measured == len(offenders) + 1


@pytest.mark.parametrize("key", sorted(contract.RATCHETED))
def test_each_law_accepts_repaid_debt_with_no_edit_anywhere(
    key: str, built: inventory.Inventory, declaration: contract.Declaration
) -> None:
    """THE DEFECT Ω-4 REPLACED, asserted as the new behaviour rather than described.

    The two-sided ceiling refused a measurement BELOW the declared value on the grounds that the
    declaration was carrying slack. The instinct was right and the implementation made improving the
    repository a chore: every repayment closed the gate until a human committed the new number, and
    the commit was indistinguishable from a retreat. Improving now requires no edit at all.
    """
    _law_id, measurement = contract.RATCHETED[key]
    offenders = measurement(built)
    if not offenders:
        pytest.skip(f"{key} is already zero, so there is no debt to repay")
    reduced = _inventory_with(built, key, offenders[:-1])
    state = _sealed_state(declaration, **{key: float(len(offenders))})
    result = contract._ratcheted(reduced, declaration, key, state)
    assert result.status == contract.HOLDS, "repaying debt was refused"
    assert "IMPROVED" in result.detail
    assert result.measured == len(offenders) - 1


@pytest.mark.parametrize("key", sorted(contract.RATCHETED))
def test_each_law_refuses_when_no_ratchet_kind_is_declared(
    key: str, built: inventory.Inventory, declaration: contract.Declaration
) -> None:
    """A measurement with no declared direction is recorded and enforced by nothing."""
    stripped = contract.Declaration(
        version=declaration.version,
        ratchet={k: v for k, v in declaration.ratchet.items() if k != key},
        source=declaration.source,
        raw=declaration.raw,
    )
    result = contract._ratcheted(built, stripped, key, omega_ratchet.Ratchet({}))
    assert result.status == contract.REFUSED
    assert "declares no KIND" in result.detail


def _inventory_with(
    base: inventory.Inventory, key: str, offenders: list[str]
) -> inventory.Inventory:
    """Rebuild an inventory whose ``key`` measurement returns exactly ``offenders``.

    The mutation is applied to the DATA the measurement reads, not to the measurement, so the test
    exercises the real function. Each law reads a different field, so each gets the shape it needs.
    """
    files = list(base.files)
    if key == "executable_outside_denominator":
        return _replace(base, executable_outside_denominator=tuple(offenders))
    if key == "ungoverned_executables":
        return _replace(base, ungoverned_files=tuple(offenders))
    if key in ("unmeasured_governance_engines", "engines_without_tests", "single_plane_engines"):
        keep = [f for f in files if not f.governing_authority.startswith("UEC-000001")]
        made = []
        for path in offenders:
            if key == "unmeasured_governance_engines":
                measured, sources = False, ("test", "make", "ci")
            elif key == "engines_without_tests":
                measured, sources = True, ("make", "ci")
            else:
                measured, sources = True, ("test", "make")
            made.append(
                _file(
                    path,
                    authority="UEC-000001 (enforcement closure inventory)",
                    measured=measured,
                    invocation_sources=sources,
                )
            )
        return _replace(base, files=tuple(keep + made))
    if key == "files_with_no_execution_path":
        keep = [
            f
            for f in files
            if not (
                f.measured
                and f.ast_statements > 20
                and not f.execution_paths
                and f.classification in (FILE_EXECUTABLE, FILE_TOOLING)
            )
        ]
        made = [
            _file(path, measured=True, statements=99, execution_paths=(), authority="x")
            for path in offenders
        ]
        return _replace(base, files=tuple(keep + made))
    raise AssertionError(f"no mutation defined for {key}")


def _file(
    path: str,
    *,
    authority: str = "NONE — no authority claims this file",
    measured: bool = False,
    statements: int = 10,
    execution_paths: tuple[str, ...] = ("f",),
    invocation_sources: tuple[str, ...] = (),
    ast_statements: int | None = None,
) -> Any:
    return FileRecord(
        path=path,
        classification=FILE_EXECUTABLE,
        statements=statements,
        covered=0,
        missing=statements,
        measured=measured,
        execution_paths=execution_paths,
        invocation_sources=invocation_sources,
        governing_authority=authority,
        exclusion_reason=None,
        # UCI-L-06 sizes files by their AST count, never by the coverage-intersected count, so a
        # synthetic offender must carry it or the law correctly declines to flag it.
        ast_statements=statements if ast_statements is None else ast_statements,
    )


def _replace(base: inventory.Inventory, **changes: Any) -> inventory.Inventory:
    return inventory.Inventory(
        files=changes.get("files", base.files),
        objects=base.objects,
        totals=base.totals,
        executable_outside_denominator=changes.get(
            "executable_outside_denominator", base.executable_outside_denominator
        ),
        ungoverned_files=changes.get("ungoverned_files", base.ungoverned_files),
        scope_drift=base.scope_drift,
    )


def test_an_orphan_ceiling_is_refused(tmp_path: Path) -> None:
    """A ratchet naming no measurement looks like enforcement and is not.

    The orphan is now a KIND rather than a number, because Ω-4 refuses a numeric ratchet before it
    ever reaches the orphan check — so injecting ``3`` would have tested the wrong refusal.
    """
    document = json.loads((REPO / contract.DECLARATION_RELATIVE).read_text(encoding="utf-8"))
    document["ratchet"]["invented_measurement"] = "CONVERGENT"
    root = tmp_path / "repo"
    (root / os.path.dirname(contract.DECLARATION_RELATIVE)).mkdir(parents=True)
    (root / contract.DECLARATION_RELATIVE).write_text(json.dumps(document), encoding="utf-8")
    loaded = contract.load_declaration(str(root))
    assert "invented_measurement" in loaded.ratchet
    assert set(loaded.ratchet) - set(contract.RATCHETED) == {"invented_measurement"}


def test_a_numeric_ratchet_is_refused(tmp_path: Path) -> None:
    """Ω-4: a ratchet declares a DIRECTION. A number is a snapshot of one afternoon.

    The premise inverted. This test used to require ceilings to be non-negative integers, which was
    the right rule for the wrong model: 65, 27, 39, 25, 14 and 10 were all valid under it, and two
    them had been 607 and 570 a week earlier. Every value below is now refused, including the ones
    that used to be the only accepted shape.
    """
    for bad in (-1, 0, 3, "3", 2.5, True, "WHATEVER", None):
        document = {"version": "1", "ratchet": {"engines_without_tests": bad}}
        root = tmp_path / f"repo-{bad!r}"
        (root / os.path.dirname(contract.DECLARATION_RELATIVE)).mkdir(parents=True)
        (root / contract.DECLARATION_RELATIVE).write_text(json.dumps(document), encoding="utf-8")
        with pytest.raises(IntegrityError, match="declares its KIND"):
            contract.load_declaration(str(root))


def test_every_declared_ratchet_kind_is_accepted(tmp_path: Path) -> None:
    """NON-VACUITY for the refusal above: the four legitimate directions must load."""
    for kind in ("MONOTONIC", "CONVERGENT", "DENSITY", "ENTROPY"):
        document = {"version": "1", "ratchet": {"engines_without_tests": kind}}
        root = tmp_path / f"repo-{kind}"
        (root / os.path.dirname(contract.DECLARATION_RELATIVE)).mkdir(parents=True)
        (root / contract.DECLARATION_RELATIVE).write_text(json.dumps(document), encoding="utf-8")
        assert contract.load_declaration(str(root)).ratchet == {"engines_without_tests": kind}


def test_an_absent_declaration_is_a_fault(tmp_path: Path) -> None:
    """Absence must not read as 'no violations'."""
    with pytest.raises(IntegrityError, match="is absent"):
        contract.load_declaration(str(tmp_path))


# ------------------------------------------------------------------ the coverage reader


def test_the_coverage_reader_reproduces_coveragepy_totals(tmp_path: Path) -> None:
    """Proof the reader reads. Hand-built XML with known totals, checked against them."""
    xml = tmp_path / "coverage.xml"
    xml.write_text(
        textwrap.dedent(
            """\
            <?xml version="1.0" ?>
            <coverage branches-valid="4" branches-covered="2">
              <sources><source>/nowhere</source></sources>
              <packages><package><classes>
                <class filename="a.py"><lines>
                  <line number="1" hits="1"/><line number="2" hits="0"/>
                  <line number="3" hits="1"/>
                </lines></class>
                <class filename="b.py"><lines>
                  <line number="7" hits="0"/>
                </lines></class>
              </classes></package></packages>
            </coverage>
            """
        ),
        encoding="utf-8",
    )
    report = coverage_data.parse(str(xml), repository=str(tmp_path))
    assert report.statements == 4
    assert report.covered == 2
    assert report.percent == 50.0
    assert report.branch_percent == 50.0
    assert report.files["a.py"].hit == frozenset({1, 3})
    assert report.files["a.py"].missed == frozenset({2})


def test_an_unparseable_coverage_document_is_a_fault(tmp_path: Path) -> None:
    """The measured incident: two processes wrote one coverage.xml and produced valid-looking
    bytes with a second document appended. Salvaging the first document would have yielded a
    valid-but-wrong report, so the reader refuses instead."""
    xml = tmp_path / "coverage.xml"
    xml.write_text("<coverage></coverage>\n<line number='1' hits='1'/>\n", encoding="utf-8")
    with pytest.raises(IntegrityError, match="not parseable coverage XML"):
        coverage_data.parse(str(xml), repository=str(tmp_path))


def test_a_coverage_document_measuring_nothing_is_a_fault(tmp_path: Path) -> None:
    xml = tmp_path / "coverage.xml"
    xml.write_text("<coverage><packages></packages></coverage>", encoding="utf-8")
    with pytest.raises(IntegrityError, match="names no measured file"):
        coverage_data.parse(str(xml), repository=str(tmp_path))


def test_an_absent_coverage_document_is_a_fault(tmp_path: Path) -> None:
    with pytest.raises(IntegrityError, match="refusing to report a coverage figure"):
        coverage_data.parse(str(tmp_path / "nope.xml"), repository=str(tmp_path))


def _report(files: dict[str, tuple[set[int], set[int]]]) -> coverage_data.CoverageReport:
    return coverage_data.CoverageReport(
        files={
            path: coverage_data.FileCoverage(path, frozenset(hit), frozenset(missed))
            for path, (hit, missed) in files.items()
        },
        branches_valid=0,
        branches_covered=0,
    )


def test_the_comparison_detects_a_single_moved_line() -> None:
    """The granularity Rules 8, 10 and 11 rest on, and the one a percentage does not have."""
    left = _report({"a.py": ({1, 2}, {3})})
    right = _report({"a.py": ({1, 3}, {2})})
    assert left.percent == right.percent, "the fixture must hold the ratio equal to be meaningful"
    diff = coverage_data.compare(left, right)
    assert diff["identical"] is False
    assert diff["files_with_differing_lines"]["a.py"] == {
        "covered_only_in_first": [2],
        "covered_only_in_second": [3],
    }


def test_the_comparison_detects_a_file_that_stopped_being_measured() -> None:
    left = _report({"a.py": ({1}, set()), "b.py": ({1}, set())})
    right = _report({"a.py": ({1}, set())})
    diff = coverage_data.compare(left, right)
    assert diff["identical"] is False
    assert diff["files_only_in_first"] == ["b.py"]


def test_identical_measurements_compare_identical() -> None:
    left = _report({"a.py": ({1, 2}, {3})})
    right = _report({"a.py": ({1, 2}, {3})})
    assert coverage_data.compare(left, right)["identical"] is True
    assert left.digest() == right.digest()


def test_the_digest_separates_unmeasured_from_uncovered() -> None:
    """Rule 11 lists 'measured files change' and 'coverage changes' as distinct failures."""
    measured_and_uncovered = _report({"a.py": (set(), {1, 2})})
    not_measured_at_all = _report({"a.py": (set(), set())})
    assert measured_and_uncovered.digest() != not_measured_at_all.digest()


# ------------------------------------------------------------------- surface attribution


def test_statement_attribution_partitions_rather_than_nests() -> None:
    """A method's statements belong to the method, not also to its class and its module.

    Nesting would let one statement be covered three times and make object totals exceed the
    file, which would silently inflate every aggregate built from them.

    THE COMPARISON IS AGAINST THE SET THE SURFACE ACTUALLY DISTRIBUTES, not against the raw AST
    statement set, and the difference is the whole reason this test was a false green. `surface`
    builds the AST set as a deliberate SUPERSET and then joins it (`surface.py:599-601`):

        countable = _statement_lines(tree)
        if file_coverage is not None:
            countable &= file_coverage.hit | file_coverage.missed

    so whenever `coverage.xml` names the module, every line coverage.py does not count as a
    statement is dropped before attribution — for `model.py` that is exactly its 8 docstrings,
    which `ast.stmt` counts and coverage.py does not. Comparing against the raw AST set
    therefore asserted `104 == 112` and could only ever pass when NO coverage document named
    the module.

    That precondition was never stated, and for a long time it was satisfied by accident: under
    the coverage-source-root collision (fixed in `pytest_scope`), `coverage xml` keyed this file
    as bare `model.py` rather than `engine/certification_integrity/model.py`, so the lookup
    missed, no join happened, and the assertion held. Rendering the document correctly unmasked
    it. One defect was hiding another, so this test is written against the invariant it
    documents — an exact partition, in BOTH regimes — rather than against one of them.
    """

    scope = surface.read_scope(str(REPO))
    built = surface.build(
        str(REPO),
        paths=[
            "engine/certification_integrity/model.py",
            "engine/certification_integrity/contract.py",
            "pyproject.toml",
        ],
    )
    assert scope.flag_packages

    # Read the join through `surface`'s own helpers. A second parser here would make this test
    # assert that two implementations agree, which is not the property under test.
    candidate = REPO / "coverage.xml"
    report = (
        coverage_data.parse(str(candidate), repository=str(REPO)) if candidate.exists() else None
    )

    for module in ("engine/certification_integrity/model.py",):
        objects = [o for o in built.objects if o.module == module]
        assert objects, f"{module} produced no objects"
        own = sum(o.statements for o in objects)

        tree = ast.parse((REPO / module).read_text(encoding="utf-8"))
        countable = surface._statement_lines(tree)
        ast_total = len(countable)
        joined = report.files.get(module) if report else None
        if joined is not None:
            countable = countable & (set(joined.hit) | set(joined.missed))

        assert own == len(countable), (
            f"attribution does not partition for {module}: objects sum to {own}, the surface "
            f"distributed {len(countable)} line(s)"
        )
        # The anti-nesting property itself, stated independently of the join: attribution can
        # never manufacture a line the file does not have.
        assert own <= ast_total, (
            f"attribution EXCEEDS the file for {module}: objects sum to {own}, the AST has "
            f"{ast_total} — a statement is being counted by more than one object"
        )


def test_docstrings_are_not_invocation_evidence() -> None:
    """A module that DESCRIBES an engine has not invoked it.

    UEC-000001 records that counting docstrings as evidence moved its untested-engine deficit
    from 18 to 16 on prose alone. The same rule is measured here rather than assumed.
    """
    prose = '"""This module mentions engine.certification_integrity.gate at length."""\n'
    code = "import engine.certification_integrity.gate\n"
    assert "certification_integrity" not in surface._evidence(prose)
    assert "engine.certification_integrity.gate" in surface._evidence(code)


def test_every_object_reports_only_declared_plane_types(built: inventory.Inventory) -> None:
    for record in built.files:
        for plane in record.invocation_sources:
            assert plane in PLANE_TYPES, f"{record.path} reports unknown plane {plane!r}"


def test_unmeasured_files_report_none_rather_than_zero_coverage(
    built: inventory.Inventory,
) -> None:
    """Zero and unmeasured are different facts, and a float cannot hold both."""
    unmeasured = [r for r in built.files if not r.measured]
    assert unmeasured, "the fixture is vacuous: every file is measured"
    assert all(r.coverage_percent is None for r in unmeasured)


def test_a_tracked_boundary_that_cannot_be_established_is_a_fault(tmp_path: Path) -> None:
    """An empty world is the state in which every 'no violations' claim is true."""
    with pytest.raises(IntegrityError, match="tracked-path boundary could not be established"):
        surface.tracked_paths(str(tmp_path))


# ------------------------------------------------------------------------ the shuffle plugin


def test_the_shuffle_is_inactive_without_a_seed() -> None:
    assert pytest_shuffle.seed_from_environment({}) is None
    items = [1, 2, 3, 4, 5]
    original = list(items)
    pytest_shuffle.pytest_collection_modifyitems(items)
    assert items == original, "the plugin reordered a run that declared no seed"


def test_a_malformed_seed_is_ignored_rather_than_guessed_at() -> None:
    """Inventing a seed would report a permutation nobody chose and nobody can replay."""
    assert pytest_shuffle.seed_from_environment({"UCI_SHUFFLE_SEED": "banana"}) is None


def test_the_shuffle_is_reproducible_under_one_seed() -> None:
    items = list(range(50))
    assert pytest_shuffle.shuffled(items, 7) == pytest_shuffle.shuffled(items, 7)


def test_the_shuffle_is_not_vacuous() -> None:
    """A permutation that never permutes would make Rule 9 pass over the declared order."""
    items = list(range(50))
    assert pytest_shuffle.shuffled(items, 7) != items
    assert pytest_shuffle.shuffled(items, 7) != pytest_shuffle.shuffled(items, 8)
    assert sorted(pytest_shuffle.shuffled(items, 7)) == items, "the permutation lost items"


def test_the_shuffle_reports_its_seed(monkeypatch: pytest.MonkeyPatch) -> None:
    """An order-dependent failure that cannot be replayed is an anecdote."""
    monkeypatch.setenv(pytest_shuffle.SEED_VARIABLE, "1234")
    header = pytest_shuffle.pytest_report_header()
    assert header is not None and "seed=1234" in header and "replay" in header


def test_the_shuffle_does_not_disturb_the_global_random_stream() -> None:
    """Seeding the global stream would make this measurement a cause of instability."""

    random.seed(99)
    expected = [random.random() for _ in range(3)]  # noqa: S311 - stream identity, not crypto
    random.seed(99)
    pytest_shuffle.shuffled(list(range(100)), 5)
    assert [random.random() for _ in range(3)] == expected  # noqa: S311


# --------------------------------------------------------------------- the frozen extraction


def test_the_seal_is_deterministic(tmp_path: Path) -> None:
    """Two extractions of one content must agree, or Rule 8's equality compares clocks."""
    shas = []
    for name in ("one", "two"):
        target = tmp_path / name
        target.mkdir()
        (target / "a.txt").write_text("content\n", encoding="utf-8")
        (target / "pyproject.toml").write_text("[project]\nname='x'\n", encoding="utf-8")
        shas.append(immutable.seal(str(target)))
    assert shas[0] == shas[1], f"the seal is not content-addressed: {shas}"


def test_the_seal_leaves_the_extraction_clean(tmp_path: Path) -> None:
    """A purity check inside the extraction must not report the harness as contamination."""
    target = tmp_path / "repo"
    target.mkdir()
    (target / "a.txt").write_text("content\n", encoding="utf-8")
    immutable.seal(str(target))
    (target / ".uci-venv").mkdir()
    (target / ".uci-coverage-x.xml").write_text("x", encoding="utf-8")
    status = subprocess.run(  # noqa: S603
        ["git", "status", "--porcelain"],  # noqa: S607
        cwd=target,
        capture_output=True,
        text=True,
        check=True,
    )
    assert status.stdout.strip() == "", f"the extraction reports dirty: {status.stdout!r}"


def test_a_sealed_extraction_differs_when_content_differs(tmp_path: Path) -> None:
    shas = []
    for name, body in (("one", "a\n"), ("two", "b\n")):
        target = tmp_path / name
        target.mkdir()
        (target / "a.txt").write_text(body, encoding="utf-8")
        shas.append(immutable.seal(str(target)))
    assert shas[0] != shas[1], "the seal does not distinguish different content"


def test_the_fingerprint_detects_a_changed_tree(tmp_path: Path) -> None:
    """Rule 7's failure condition, measured rather than asserted."""
    target = tmp_path / "repo"
    target.mkdir()
    (target / "a.txt").write_text("one\n", encoding="utf-8")
    immutable.seal(str(target))
    before = immutable.fingerprint(str(target))
    (target / "b.txt").write_text("two\n", encoding="utf-8")
    after = immutable.fingerprint(str(target))
    assert before != after
    assert before.head == after.head, "the fixture changed HEAD, so it is not testing dirtiness"
    assert after.dirty_entries > before.dirty_entries


def test_require_stable_refuses_a_run_whose_tree_moved() -> None:
    moved = immutable.FrozenRun(
        sha="a" * 40,
        command=("true",),
        exit_code=0,
        duration_seconds=1.0,
        stdout_tail="",
        stderr_tail="",
        before=immutable.Fingerprint("a" * 40, "x", "y", 0),
        after=immutable.Fingerprint("b" * 40, "x", "y", 3),
        extraction=immutable.Extraction("a" * 40, "unused", "python", False, 0.0),
    )
    assert moved.tree_stable is False
    with pytest.raises(IntegrityError, match="changed while a certification run was in flight"):
        immutable.require_stable([moved])


# ------------------------------------------------------------------------ shard partitioning


def test_a_single_shard_partition_is_refused() -> None:
    with pytest.raises(IntegrityError, match="at least two shards"):
        partition(["a", "b"], 1)


def test_an_empty_shard_is_refused() -> None:
    """An empty shard contributes no data and makes the combined total silently smaller."""
    with pytest.raises(IntegrityError, match="received no tests"):
        partition(["a", "b"], 4)


def test_the_partition_is_a_permutation_of_its_input() -> None:
    modules = [f"test_{i}.py" for i in range(23)]
    groups = partition(modules, 4)
    flattened = sorted(item for group in groups for item in group)
    assert flattened == sorted(modules), "the partition lost or duplicated a module"
    assert len({len(g) for g in groups}) <= 2, "the partition is badly unbalanced"


def test_a_shard_proof_over_an_empty_suite_is_refused(tmp_path: Path) -> None:
    with pytest.raises(IntegrityError, match="no test modules found"):
        discover_test_modules(str(tmp_path), ["nowhere"])


def test_the_repository_offers_test_modules_to_shard() -> None:
    found = discover_test_modules(str(REPO), ["engine/tests"])
    assert len(found) > 100
    assert all(name.endswith(".py") for name in found)


# ------------------------------------------------------------------------- classification


def test_the_default_classification_is_executable() -> None:
    """The cheap classification must be the one that costs work."""
    classification, rule, reason = inventory._classify(
        "engine/whatever/thing.py", "x = 1\n", {}, is_test=False
    )
    assert (classification, rule, reason) == (FILE_EXECUTABLE, "UCI-C-00", None)


def test_a_declared_exclusion_carries_its_reason_through() -> None:
    classification, _rule, reason = inventory._classify(
        "engine/uicm/thing.py", "x = 1\n", {"engine.uicm": "stated reason"}, is_test=False
    )
    assert classification == "intentionally_excluded"
    assert reason == "stated reason"


def test_a_generated_marker_is_detected_by_content_not_path() -> None:
    classification, rule, _ = inventory._classify(
        "engine/x/y.py", "# DO NOT EDIT - auto-generated\nx = 1\n", {}, is_test=False
    )
    assert (classification, rule) == ("generated", "UCI-C-02")


def test_the_inventory_document_is_deterministic(built: inventory.Inventory) -> None:
    """Rule 7 records an inventory digest; a digest over unstable bytes records nothing."""
    again = inventory.build(str(REPO))
    assert built.digest() == again.digest()
    assert json.dumps(built.as_document(), sort_keys=True) == json.dumps(
        again.as_document(), sort_keys=True
    )


def test_the_inventory_declares_no_authority(built: inventory.Inventory) -> None:
    document = built.as_document()
    assert document["authority"].startswith("NONE")
    assert "determinism" in document


def test_no_wall_clock_or_machine_path_leaks_into_the_inventory(
    built: inventory.Inventory,
) -> None:
    """A register carrying a timestamp cannot be a fixed point."""
    encoded = json.dumps(built.as_document())
    assert str(REPO) not in encoded, "an absolute machine path leaked into the inventory"

    assert not re.search(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}", encoded), "a timestamp leaked in"


def test_measuring_does_not_mutate_the_declaration_it_reads(
    declaration: contract.Declaration, report: dict[str, Any]
) -> None:
    """Guards against a law that repairs its own expectation as a side effect."""
    snapshot = copy.deepcopy(dict(declaration.ratchet))
    # ``ratchet_declared`` became ``ratchet_kinds`` when the declaration stopped carrying numbers.
    # The bounds moved to the sealed state and are reported separately as ``ratchet_best``.
    assert report["ratchet_kinds"] == snapshot
    assert dict(contract.load_declaration(str(REPO)).ratchet) == snapshot
    assert set(report["ratchet_best"]) == set(
        contract.RATCHETED
    ), "every measured law must report the bound it was held to"


# ------------------------------------------------ the reader's remaining shapes and refusals


def test_a_file_measuring_nothing_reports_a_hundred_percent_rather_than_a_division(
    tmp_path: Path,
) -> None:
    """Zero statements is a real state — an empty ``__init__.py`` is fully covered — and the
    alternative is a ZeroDivisionError inside the reader, which would take the measurement down
    over a file with nothing in it."""
    empty = coverage_data.FileCoverage("empty.py", frozenset(), frozenset())
    assert empty.statements == 0
    assert empty.percent == 100.0
    assert _report({"a.py": ({1}, {2, 3})}).missing == 2


def test_a_document_declaring_no_branches_reports_no_branch_percentage(tmp_path: Path) -> None:
    """None rather than 100.0: a run measured without branch coverage has no branch figure, and
    reporting one would put a number nobody measured next to the ones somebody did."""
    assert _report({"a.py": ({1}, set())}).branch_percent is None


def test_a_line_with_no_number_and_a_class_with_no_filename_are_skipped(tmp_path: Path) -> None:
    """A row the reader cannot key contributes nothing rather than a partial entry. The totals
    stay correct, which is the whole reason a rendering defect is reported and not raised."""
    xml = tmp_path / "coverage.xml"
    xml.write_text(
        textwrap.dedent(
            """\
            <?xml version="1.0" ?>
            <coverage branches-valid="0" branches-covered="0">
              <sources><source>/nowhere</source></sources>
              <packages><package><classes>
                <class><lines><line number="1" hits="1"/></lines></class>
                <class filename="a.py"><lines>
                  <line hits="1"/><line number="2" hits="1"/>
                </lines></class>
              </classes></package></packages>
            </coverage>
            """
        ),
        encoding="utf-8",
    )
    report = coverage_data.parse(str(xml), repository=str(tmp_path))
    assert set(report.files) == {"a.py"}
    assert report.files["a.py"].hit == frozenset({2})


def test_one_file_measured_under_two_source_roots_is_merged_rather_than_overwritten(
    tmp_path: Path,
) -> None:
    """Merging by union rather than overwriting keeps a re-measured file from LOSING hits, which
    would understate coverage and manufacture a drift finding out of a shard combination."""
    xml = tmp_path / "coverage.xml"
    xml.write_text(
        textwrap.dedent(
            """\
            <?xml version="1.0" ?>
            <coverage branches-valid="0" branches-covered="0">
              <sources><source>/nowhere</source></sources>
              <packages>
                <package name="one"><classes>
                  <class filename="a.py"><lines>
                    <line number="1" hits="1"/><line number="2" hits="0"/>
                  </lines></class>
                </classes></package>
                <package name="two"><classes>
                  <class filename="a.py"><lines>
                    <line number="1" hits="0"/><line number="2" hits="1"/>
                  </lines></class>
                </classes></package>
              </packages>
            </coverage>
            """
        ),
        encoding="utf-8",
    )
    report = coverage_data.parse(str(xml), repository=str(tmp_path))
    assert report.files["a.py"].hit == frozenset({1, 2})
    assert report.files["a.py"].missed == frozenset()


def test_an_absolute_filename_inside_and_outside_the_repository_both_resolve(
    tmp_path: Path,
) -> None:
    """A path under the repository becomes relative to it, so the key is comparable across
    machines. One outside is kept as it was given — inventing a relative form for a file the
    repository does not contain would file it under a path that is not there."""
    inside = tmp_path / "engine" / "a.py"
    inside.parent.mkdir(parents=True)
    inside.write_text("x = 1\n", encoding="utf-8")
    xml = tmp_path / "coverage.xml"
    xml.write_text(
        f"""<?xml version="1.0" ?>
        <coverage branches-valid="0" branches-covered="0">
          <sources><source>{tmp_path}</source></sources>
          <packages><package><classes>
            <class filename="{inside}"><lines><line number="1" hits="1"/></lines></class>
            <class filename="/elsewhere/b.py"><lines><line number="1" hits="1"/></lines></class>
          </classes></package></packages>
        </coverage>
        """,
        encoding="utf-8",
    )
    report = coverage_data.parse(str(xml), repository=str(tmp_path))
    assert "engine/a.py" in report.files
    assert "/elsewhere/b.py" in report.files


def test_a_name_two_source_roots_both_carry_is_marked_ambiguous_or_resolved_by_its_package(
    tmp_path: Path,
) -> None:
    """Guessing "the first root where a file of this name exists" produced a false drift finding
    over 19 files whose per-file line sets were identical. So an ambiguous name resolves to a
    STABLE, MARKED key — stable so two runs of one state still compare equal, marked so the
    ambiguity is visible rather than silently attributed to one candidate. A package name that
    picks out exactly one candidate resolves it instead."""
    for package in ("one", "two"):
        target = tmp_path / package / "shared.py"
        target.parent.mkdir(parents=True)
        target.write_text("x = 1\n", encoding="utf-8")

    def _document(package_name: str) -> str:
        return f"""<?xml version="1.0" ?>
        <coverage branches-valid="0" branches-covered="0">
          <sources><source>{tmp_path / "one"}</source><source>{tmp_path / "two"}</source></sources>
          <packages><package name="{package_name}"><classes>
            <class filename="shared.py"><lines><line number="1" hits="1"/></lines></class>
          </classes></package></packages>
        </coverage>
        """

    ambiguous = tmp_path / "ambiguous.xml"
    ambiguous.write_text(_document(""), encoding="utf-8")
    report = coverage_data.parse(str(ambiguous), repository=str(tmp_path))
    assert report.ambiguous_files
    assert all(name.startswith(coverage_data.AMBIGUOUS_PREFIX) for name in report.ambiguous_files)

    hinted = tmp_path / "hinted.xml"
    hinted.write_text(_document("one"), encoding="utf-8")
    assert "one/shared.py" in coverage_data.parse(str(hinted), repository=str(tmp_path)).files

    # A hint that picks out no candidate leaves the name ambiguous rather than resolving it to
    # whichever root sorted first, which is the guess that manufactured the false drift finding.
    unhelpful = tmp_path / "unhelpful.xml"
    unhelpful.write_text(_document("three"), encoding="utf-8")
    assert coverage_data.parse(str(unhelpful), repository=str(tmp_path)).ambiguous_files


def test_a_name_no_source_root_carries_is_resolved_against_the_repository_root(
    tmp_path: Path,
) -> None:
    """The last resort before keeping the declared name: a file the roots do not carry may still
    be under the repository, and resolving it there is what keeps a key comparable rather than
    synthesised."""
    target = tmp_path / "top-level.py"
    target.write_text("x = 1\n", encoding="utf-8")
    xml = tmp_path / "coverage.xml"
    xml.write_text(
        f"""<?xml version="1.0" ?>
        <coverage branches-valid="0" branches-covered="0">
          <sources><source>{tmp_path / "absent"}</source></sources>
          <packages><package><classes>
            <class filename="top-level.py"><lines><line number="1" hits="1"/></lines></class>
          </classes></package></packages>
        </coverage>
        """,
        encoding="utf-8",
    )
    assert "top-level.py" in coverage_data.parse(str(xml), repository=str(tmp_path)).files


# ---------------------------------------------------- the surface reader's faults and skips


def test_a_pyproject_that_cannot_be_read_or_declares_no_policy_is_a_fault(tmp_path: Path) -> None:
    """The denominator is DECLARED. An unreadable declaration is not an empty denominator, and
    reading it as one would put every law into the empty-world state where no-violations is
    true because nothing was measured."""
    with pytest.raises(IntegrityError, match="undeclared or unparseable"):
        surface.read_scope(str(tmp_path))
    (tmp_path / "pyproject.toml").write_text("[tool.other]\nkey = 1\n", encoding="utf-8")
    with pytest.raises(IntegrityError, match="no coverage report policy"):
        surface.read_scope(str(tmp_path))


def test_a_derivation_that_faults_is_reported_as_an_integrity_fault(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """`OmegaError` is re-raised as `IntegrityError` so "discovery could not run" can never be
    read as "discovery found nothing" — the empty-world state in which every no-violations claim
    is true."""

    (tmp_path / "pyproject.toml").write_text(
        "[tool.coverage.report]\nfail_under = 90\n", encoding="utf-8"
    )

    def _faulting(root: str):  # noqa: ANN202
        raise OmegaError("the tracked population could not be derived")

    monkeypatch.setattr(omega_discovery, "derived_scope", _faulting)
    with pytest.raises(IntegrityError, match="denominator derivation failed"):
        surface.read_scope(str(tmp_path))


def test_a_tree_git_reports_as_empty_is_refused_rather_than_measured(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """An empty world reports zero violations of everything. Refusing it is what keeps a
    no-violations claim a claim about a population rather than about the absence of one."""
    monkeypatch.setattr(surface.GitDiscoveryProvider, "enumerate", lambda self: (), raising=False)
    with pytest.raises(IntegrityError, match="refusing to measure an empty world"):
        surface.tracked_paths(str(tmp_path))


def test_a_file_that_cannot_be_read_contributes_no_text(tmp_path: Path) -> None:
    """Unreadable contributes nothing rather than raising: one undecodable file must not take
    the whole surface measurement down."""
    binary = tmp_path / "binary.py"
    binary.write_bytes(b"\xff\xfe not utf-8 \x00")
    assert surface.read_text(str(tmp_path), "binary.py") == ""
    assert surface.read_text(str(tmp_path), "absent.py") == ""


def test_a_module_that_does_not_parse_carries_no_executable_code_and_no_evidence(
    tmp_path: Path,
) -> None:
    """Three readers, one rule: a file that does not parse contributes nothing rather than
    contributing its raw text. Counting a docstring as evidence moved a sibling package's
    untested-engine deficit by two files on prose alone."""
    broken = tmp_path / "broken.py"
    broken.write_text("def (:::\n", encoding="utf-8")
    assert surface._has_executable_code(str(tmp_path), "broken.py") is False
    assert surface._evidence("def (:::\n") == ""
    assert (
        surface._objects_for(
            "broken.py",
            root=str(tmp_path),
            scope=surface.read_scope(str(REPO)),
            report=None,
            corpus={},
            test_corpus={},
            source_corpus={},
        )
        == []
    )


def test_a_pyproject_with_no_entry_points_declares_none(tmp_path: Path) -> None:
    """An unreadable or absent pyproject declares no console script, which is different from a
    fault: entry points are additive surface, and their absence is an ordinary state."""
    assert surface._entry_points(str(tmp_path)) == {}


def test_a_surface_projects_its_objects_by_kind() -> None:
    """`by_kind` is how a per-kind reader consults the surface. A projection that returned the
    whole population would make every such reader measure every kind."""
    projected = surface.build(str(REPO))
    kinds = {o.kind for o in projected.objects}
    assert kinds
    for kind in kinds:
        selected = projected.by_kind(kind)
        assert selected
        assert all(o.kind == kind for o in selected)


# ------------------------------------------- the contract's faults, its seal and its inventory


def test_an_unparseable_declaration_is_a_fault(tmp_path: Path) -> None:
    """Absent and unparseable are different failures with the same consequence: there is no
    governed expectation to measure against, and neither may be read as "nothing is declared"."""
    root = tmp_path / "repo"
    (root / os.path.dirname(contract.DECLARATION_RELATIVE)).mkdir(parents=True)
    (root / contract.DECLARATION_RELATIVE).write_text("{ not json", encoding="utf-8")
    with pytest.raises(IntegrityError, match="is unparseable"):
        contract.load_declaration(str(root))


def test_an_orphan_ceiling_closes_the_gate_that_declares_it(monkeypatch: pytest.MonkeyPatch):
    """The load-time check names the key; this is the MEASUREMENT-time refusal, which is the one
    a gate run reports. A ratchet key measured by nothing is a declaration that looks like
    enforcement and is not."""
    real = contract.load_declaration

    def _with_orphan(root: str) -> contract.Declaration:
        declaration = real(root)
        return replace_declaration(declaration)

    def replace_declaration(declaration: contract.Declaration) -> contract.Declaration:
        return dataclasses.replace(
            declaration,
            ratchet={**declaration.ratchet, "invented_measurement": "CONVERGENT"},
        )

    monkeypatch.setattr(contract, "load_declaration", _with_orphan)
    report = contract.measure(str(REPO))
    assert report["status"] == contract.CLOSED
    refusals = [law for law in report["laws"] if law["status"] == contract.REFUSED]
    assert any("measured by nothing" in law["detail"] for law in refusals)


def test_a_first_measurement_of_a_key_is_seeded_rather_than_refused(tmp_path: Path) -> None:
    """SEEDED is the state a ratchet enters the first time a key is measured: every future run
    is held to this value or better, with no number authored by hand. Refusing it would make a
    new law unaddable without hand-writing the ceiling the whole design removes."""

    state = ratchet_module.load(str(tmp_path / "absent.json"))
    key = sorted(contract.RATCHETED)[0]
    law, measurement = contract.RATCHETED[key]
    declaration = contract.load_declaration(str(REPO))
    observation = state.observe(key, declaration.ratchet[key], 7.0, contract.LAWS[law].question)
    assert observation.verdict == ratchet_module.SEEDED


def test_sealing_advances_the_ratchet_from_a_measurement_and_writes_one_path(
    built: inventory.Inventory, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Sealing is not a way to make a refusal pass: `sealed` only ever moves `best` DOWNWARD and
    `assert_sealed_from_measurement` refuses a state looser than the run that wrote it. The write
    is redirected here because this test measures the SEAL, not the repository's own state file."""

    written: dict[str, object] = {}
    monkeypatch.setattr(inventory, "build", lambda root, coverage_xml=None: built)
    monkeypatch.setattr(
        ratchet_module,
        "write",
        lambda path, document: written.update({"path": path, "document": document}),
    )
    assert contract.seal_ratchet(str(REPO)) == contract.RATCHET_STATE_RELATIVE
    assert written["path"].endswith(contract.RATCHET_STATE_RELATIVE)
    assert written["document"]


@pytest.mark.parametrize(
    ("body", "expected"),
    [(None, None), ("{ not xml", {"parseable": False})],
    ids=["absent", "unparseable"],
)
def test_the_coverage_document_report_is_absent_or_marks_itself_unparseable(
    tmp_path: Path, body: str | None, expected: object
) -> None:
    """Deliberately NOT a ratcheted law: the defect is in `coverage xml`'s rendering, not in this
    repository's code. It is surfaced because it is invisible to every summary — the header
    totals agree exactly while the body is missing 46% of the files."""
    candidate = tmp_path / "coverage.xml"
    if body is not None:
        candidate.write_text(body, encoding="utf-8")
    assert contract._coverage_document(str(tmp_path), str(candidate)) == expected


def test_the_inventory_writes_one_document_and_returns_what_it_wrote(
    built: inventory.Inventory, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """The written document is the one artifact this programme emits, and no law reads it back —
    so regenerating it cannot turn a refusal into a pass."""
    monkeypatch.setattr(inventory, "build", lambda root, coverage_xml=None: built)
    destination = tmp_path / "nested" / "coverage_gap_inventory.json"
    returned = inventory.write(str(REPO), str(destination))
    assert returned is built
    assert json.loads(destination.read_text(encoding="utf-8"))


def test_a_test_module_is_classified_as_one_and_owned_by_the_scope_that_omits_it() -> None:
    """A test file is not executable surface: it is the thing that exercises it. Classifying it
    as executable would put every test module into the denominator it is measuring."""

    classification, rule_id, reason = inventory._classify(
        "engine/tests/unit/test_x.py", text="", excluded_packages={}, is_test=True
    )
    assert classification == FILE_TEST
    assert rule_id == "UCI-C-05"
    assert reason is None
    assert "omit list" in inventory._authority(
        "engine/tests/unit/test_x.py", False, classification, rule_id
    )


def test_an_archived_file_is_owned_by_the_frozen_path_guard() -> None:
    """DP-03 owns the frozen corpus. Reporting it as unowned would put the certified corpus into
    the undeclared-surface finding, which is a governance claim about somebody else's decision."""

    assert "frozen-path guard" in inventory._authority(
        "99-FREEZE/a.py", False, FILE_ARCHIVED, "UCI-C-04"
    )


def test_a_module_that_does_not_parse_counts_no_statements() -> None:
    """The AST count is independent of any coverage measurement, and a file that does not parse
    contributes zero rather than taking the inventory down."""
    assert inventory._ast_statements("def (:::\n") == 0


def test_the_shuffle_reorders_only_when_a_seed_is_present(monkeypatch: pytest.MonkeyPatch) -> None:
    """Inactive without a seed, so an ordinary run is not made non-deterministic by the plugin
    that exists to detect order dependence — and active with one, so the permutation is
    replayable from the header it prints."""
    items = list(range(40))
    monkeypatch.delenv(pytest_shuffle.SEED_VARIABLE, raising=False)
    unchanged = list(items)
    pytest_shuffle.pytest_collection_modifyitems(unchanged)
    assert unchanged == items
    assert "inactive" in pytest_shuffle.pytest_report_header()

    monkeypatch.setenv(pytest_shuffle.SEED_VARIABLE, "7")
    reordered = list(items)
    pytest_shuffle.pytest_collection_modifyitems(reordered)
    assert sorted(reordered) == items
    assert reordered != items
    assert "seed=7" in pytest_shuffle.pytest_report_header()


def test_an_uncovered_line_carries_its_remedy_and_records_itself() -> None:
    """The remedy is derived from the classification rather than written per line, so a
    classification that changed meaning cannot leave a line carrying the previous remedy."""

    classification = sorted(REMEDY)[0]
    line = UncoveredLine(
        path="engine/a.py",
        line=7,
        owner="UCI-000001",
        source="return 1",
        classification=classification,
        justification="measured",
    )
    assert line.remedy == REMEDY[classification]
    assert line.as_record()["remedy"] == REMEDY[classification]
    assert line.as_record()["line"] == 7


# --------------------------------------------------- the frozen-run harness, without the cost


def _tiny_repo(tmp_path: Path, name: str = "origin") -> Path:
    """A real one-commit repository. The harness extracts through `git archive`, so nothing
    smaller than a real repository exercises the path it actually takes."""
    root = tmp_path / name
    root.mkdir()
    (root / "a.py").write_text("VALUE = 1\n", encoding="utf-8")
    (root / "pyproject.toml").write_text("[project]\nname='x'\nversion='0'\n", encoding="utf-8")
    for args in (
        ["init", "-q", "--initial-branch=main"],
        ["-c", "user.email=t@ucos", "-c", "user.name=Test", "add", "-A"],
        [
            "-c",
            "user.email=t@ucos",
            "-c",
            "user.name=Test",
            "commit",
            "-q",
            "--no-verify",
            "-m",
            "one",
        ],
    ):
        subprocess.run(["git", *args], cwd=root, check=True, capture_output=True)  # noqa: S603,S607
    return root


def _frozen_run(**overrides: Any) -> immutable.FrozenRun:
    fields = {
        "sha": "a" * 40,
        "command": ("true",),
        "exit_code": 0,
        "duration_seconds": 1.0,
        "stdout_tail": "",
        "stderr_tail": "",
        "before": immutable.Fingerprint("a" * 40, "x", "y", 0),
        "after": immutable.Fingerprint("a" * 40, "x", "y", 0),
        "extraction": immutable.Extraction("a" * 40, "unused", "python", False, 0.0),
    }
    fields.update(overrides)
    return immutable.FrozenRun(**fields)


def test_a_frozen_run_records_every_fact_a_reader_would_need_to_reproduce_it() -> None:
    """The record is what a certification cites. A field missing from it is a fact the citation
    cannot carry, and `tree_stable` in particular is the difference between a measurement
    attributable to a commit and one attributable to nothing."""
    record = _frozen_run(artifacts={"coverage.xml": "/out/coverage.xml"}).as_record()
    assert record["tree_stable"] is True
    assert record["command"] == ["true"]
    assert record["artifacts"] == {"coverage.xml": "/out/coverage.xml"}
    assert record["extraction"]["source_sha"] == "a" * 40


def test_a_run_whose_tree_did_not_move_is_accepted() -> None:
    """The refusal is measured elsewhere. Without this, `require_stable` could refuse every run
    and the suite would not notice."""
    immutable.require_stable([_frozen_run()])


def test_an_extraction_of_a_revision_that_does_not_exist_is_a_fault(tmp_path: Path) -> None:
    """The archive step fails and the extraction is refused. Continuing with an empty
    destination would produce a measurement attributed to a commit that was never extracted."""
    root = _tiny_repo(tmp_path)
    destination = tmp_path / "extraction"
    destination.mkdir()
    with pytest.raises(IntegrityError, match="git archive"):
        immutable.extract(str(root), "0" * 40, str(destination))


def test_an_extraction_whose_unpacking_fails_is_a_fault(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Two processes, two failure modes. The archive succeeding and the unpack failing leaves a
    partial tree, and measuring one would attribute a partial extraction to a whole commit."""
    root = _tiny_repo(tmp_path)
    destination = tmp_path / "extraction"
    destination.mkdir()
    real = subprocess.Popen

    def _tar_refuses(argv, **kwargs):  # noqa: ANN001, ANN202
        if argv and argv[0] == "tar":
            # Consumes the archive so `git archive` still succeeds, then refuses. Exiting
            # without reading would break the pipe and fail the archive instead, which is the
            # OTHER refusal and already measured.
            return real(["sh", "-c", "cat >/dev/null; exit 3"], **kwargs)  # noqa: S607
        return real(argv, **kwargs)

    monkeypatch.setattr(immutable.subprocess, "Popen", _tar_refuses)
    with pytest.raises(IntegrityError, match="extracting"):
        immutable.extract(str(root), immutable.resolve_sha(str(root)), str(destination))


def test_an_archive_process_that_offers_no_pipe_is_still_reaped(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """`Popen` with `stdout=PIPE` always yields a pipe, so the guard that closes it has only
    ever taken one branch. It is the one that keeps the close from raising on a process object
    that did not give us one — and reaching it means handing the extractor exactly that.
    """
    root = _tiny_repo(tmp_path)
    destination = tmp_path / "extraction"
    destination.mkdir()
    real = subprocess.Popen

    class _NoPipe:
        def __init__(self, process: object) -> None:
            self._process = process

        stdout = None

        def __getattr__(self, name: str) -> object:
            return getattr(self._process, name)

    def _pipeless(argv, **kwargs):  # noqa: ANN001, ANN202
        process = real(argv, **kwargs)
        return _NoPipe(process) if argv[:2] == ["git", "archive"] else process

    monkeypatch.setattr(immutable.subprocess, "Popen", _pipeless)
    # WHAT IS UNDER TEST IS THE GUARD, NOT TAR'S OPINION OF EMPTY INPUT. Handed no pipe, the
    # extractor must reach `if archive.stdout is not None` and decline to close what it was
    # never given; whether the tar it then reaps calls empty input acceptable is a property of
    # the tar on the machine, not of this repository. bsdtar exits 0 and GNU tar exits non-zero
    # with "This does not look like a tar archive", so asserting the quiet return asserted macOS.
    # Either outcome proves the guard held: the failure this test exists to catch is an
    # AttributeError on None, which neither branch below can reach.
    try:
        immutable.extract(str(root), immutable.resolve_sha(str(root)), str(destination))
    except IntegrityError as exc:
        assert "extracting" in str(exc), f"the guard raised on the pipe, not on tar: {exc}"
    # Nothing was piped, so nothing was unpacked, on either tar.
    assert list(destination.iterdir()) == []


def test_sealing_a_destination_git_refuses_is_a_fault(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The seal is what makes an extraction content-addressed. A seal that failed silently would
    leave the extraction unsealed and every later fingerprint comparing an unsealed tree."""
    real = subprocess.run

    def _refusing(argv, **kwargs):  # noqa: ANN001, ANN202
        if argv[:2] == ["git", "init"]:
            return subprocess.CompletedProcess(argv, 1, "", "git declined to initialise")
        return real(argv, **kwargs)

    monkeypatch.setattr(immutable.subprocess, "run", _refusing)
    target = tmp_path / "extraction"
    target.mkdir()
    with pytest.raises(IntegrityError, match="could not seal the extraction"):
        immutable.seal(str(target))


def test_a_readiness_marker_that_cannot_be_read_forces_a_fresh_extraction(
    tmp_path: Path,
) -> None:
    """An unreadable marker is not a valid reuse claim. Reading it as one would reuse a tree
    whose provenance nobody can state."""
    root = _tiny_repo(tmp_path)
    sha = immutable.resolve_sha(str(root))
    workspace = tmp_path / "workspace"
    destination = workspace / sha
    destination.mkdir(parents=True)
    (destination / immutable.READY_MARKER).write_text("{ not json", encoding="utf-8")
    extraction = immutable.prepare(
        str(root), sha, workspace=str(workspace), build_venv=False, reuse=True
    )
    assert extraction.reused is False
    assert (Path(extraction.root) / "a.py").is_file()


def test_a_marker_naming_the_same_content_is_reused_without_re_extracting(
    tmp_path: Path,
) -> None:
    """Reuse is keyed on the commit AND the dependency digest, so an extraction prepared under
    different dependencies is rebuilt rather than reused with the wrong environment."""
    root = _tiny_repo(tmp_path)
    sha = immutable.resolve_sha(str(root))
    workspace = tmp_path / "workspace"
    first = immutable.prepare(
        str(root), sha, workspace=str(workspace), build_venv=False, reuse=True
    )
    assert first.reused is False
    second = immutable.prepare(
        str(root), sha, workspace=str(workspace), build_venv=False, reuse=True
    )
    assert second.reused is True
    assert second.sealed_sha == first.sealed_sha


def test_a_virtualenv_the_extraction_cannot_build_or_populate_is_a_fault(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Building an environment is not a measurement and must contribute nothing to one — which
    is why it is scrubbed — but a build that FAILED must be a fault: a measurement taken inside
    an extraction whose dependencies are not the extraction's own is attributable to nothing."""
    real = subprocess.run

    def _venv_fails(argv, **kwargs):  # noqa: ANN001, ANN202
        if len(argv) > 2 and argv[1:3] == ["-m", "venv"]:
            return subprocess.CompletedProcess(argv, 1, "", "no venv module")
        return real(argv, **kwargs)

    monkeypatch.setattr(immutable.subprocess, "run", _venv_fails)
    with pytest.raises(IntegrityError, match="could not create a virtualenv"):
        immutable._build_venv(str(tmp_path))

    def _install_fails(argv, **kwargs):  # noqa: ANN001, ANN202
        if len(argv) > 2 and argv[1:3] == ["-m", "venv"]:
            venv = Path(argv[3])
            (venv / "bin").mkdir(parents=True, exist_ok=True)
            (venv / "bin" / "python").write_text("#!/bin/sh\n", encoding="utf-8")
            return subprocess.CompletedProcess(argv, 0, "", "")
        if "pip" in argv:
            return subprocess.CompletedProcess(argv, 1, "", "no index")
        return real(argv, **kwargs)

    monkeypatch.setattr(immutable.subprocess, "run", _install_fails)
    with pytest.raises(IntegrityError, match="dependencies could not be installed"):
        immutable._build_venv(str(tmp_path))


def test_a_frozen_run_inherits_the_declared_environment_and_collects_what_exists(
    tmp_path: Path,
) -> None:
    """The extraction inherits no ambient measurement environment at all, and the caller's own
    variables are applied on top of the scrubbed one. `collect` copies out only what the run
    actually produced: naming an artifact that was not written must not manufacture one."""
    root = _tiny_repo(tmp_path)
    out = tmp_path / "collected.txt"
    frozen = immutable.run(
        str(root),
        [
            immutable.PYTHON_PLACEHOLDER,
            "-c",
            "import os, pathlib;"
            "pathlib.Path('produced.txt').write_text(os.environ['UCI_PROBE'])",
        ],
        workspace=str(tmp_path / "workspace"),
        env={"UCI_PROBE": "declared"},
        collect={"produced.txt": str(out), "never-written.txt": str(tmp_path / "absent.txt")},
        build_venv=False,
        reuse=False,
    )
    assert frozen.exit_code == 0
    assert out.read_text(encoding="utf-8") == "declared"
    assert "never-written.txt" not in frozen.artifacts
    assert not (tmp_path / "absent.txt").exists()


def test_a_git_command_that_cannot_run_is_a_fault_naming_the_tree(tmp_path: Path) -> None:
    """A tree git refuses to answer for has no resolvable revision, and inventing one would
    attribute a measurement to a commit that does not exist."""
    with pytest.raises(IntegrityError, match="failed in"):
        immutable.resolve_sha(str(tmp_path))


def test_a_virtualenv_that_builds_and_installs_returns_its_interpreter(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The success path, which the real one pays a `pip install -e .[dev]` for. Both subprocesses
    are scrubbed of the ambient measurement environment for the reason `run_frozen` is: building
    an environment is not a measurement and must contribute nothing to one."""
    real = subprocess.run
    seen: list[dict[str, object]] = []

    def _succeeding(argv, **kwargs):  # noqa: ANN001, ANN202
        seen.append({"argv": list(argv), "env": kwargs.get("env")})
        if len(argv) > 2 and argv[1:3] == ["-m", "venv"]:
            binaries = Path(argv[3]) / "bin"
            binaries.mkdir(parents=True, exist_ok=True)
            (binaries / "python").write_text("#!/bin/sh\n", encoding="utf-8")
            return subprocess.CompletedProcess(argv, 0, "", "")
        if "pip" in argv:
            return subprocess.CompletedProcess(argv, 0, "", "")
        return real(argv, **kwargs)

    monkeypatch.setattr(immutable.subprocess, "run", _succeeding)
    python = immutable._build_venv(str(tmp_path))
    assert python.endswith("/bin/python")
    assert Path(python).exists()
    venv_call = next(call for call in seen if call["argv"][1:3] == ["-m", "venv"])
    assert "COV_CORE_CONFIG" not in (venv_call["env"] or {})


def test_an_extraction_prepared_with_an_interpreter_reuses_it_on_the_next_call(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Reuse is keyed on the commit, the dependency digest AND the interpreter still existing. An
    extraction whose interpreter has gone is rebuilt, because a measurement taken with a missing
    interpreter is attributable to nothing."""
    root = _tiny_repo(tmp_path)
    sha = immutable.resolve_sha(str(root))
    workspace = tmp_path / "workspace"

    def _fake_venv(destination: str) -> str:
        binaries = Path(destination) / ".uci-venv" / "bin"
        binaries.mkdir(parents=True, exist_ok=True)
        interpreter = binaries / "python"
        interpreter.write_text("#!/bin/sh\n", encoding="utf-8")
        return str(interpreter)

    monkeypatch.setattr(immutable, "_build_venv", _fake_venv)
    first = immutable.prepare(str(root), sha, workspace=str(workspace), build_venv=True, reuse=True)
    assert first.reused is False
    assert Path(first.python).exists()

    second = immutable.prepare(
        str(root), sha, workspace=str(workspace), build_venv=True, reuse=True
    )
    assert second.reused is True
    assert second.python == first.python


def test_a_coverage_figure_records_what_it_is_a_figure_of() -> None:
    """A percentage with no provenance is not reproducible even in principle: it does not say
    which tree it measured, which interpreter ran it, or how many tests contributed."""

    record = Provenance(
        commit_sha="a" * 40,
        dirty=False,
        coverage_percent=98.5,
        statements=100,
        covered=98,
        missing=2,
        branch_percent=95.0,
        test_count=19_000,
        duration_seconds=3600.0,
        environment_hash="b" * 16,
        python_version="3.12.13",
        platform="darwin",
        inventory_digest="c" * 16,
        coverage_digest="d" * 16,
    ).as_record()
    assert record["commit_sha"] == "a" * 40
    assert record["dirty"] is False
    assert record["test_count"] == 19_000
    assert record["coverage_digest"] == "d" * 16


def test_a_surface_built_with_no_coverage_document_reports_every_object_unmeasured(
    tmp_path: Path,
) -> None:
    """Measured-and-zero is a coverage gap; unmeasured-and-zero is a governance gap, and they
    have different remedies. A surface built where no report exists must say the second."""
    built_without = surface.build(str(REPO), coverage_xml=str(tmp_path / "absent.xml"))
    assert built_without.coverage is None
    assert all(not o.measured or o.covered == 0 for o in built_without.objects)


def test_a_module_is_not_evidence_of_its_own_invocation() -> None:
    """A file that names an engine has invoked it — unless the file IS the engine, in which case
    the mention is its own definition. Counting that would make every engine self-invoking, and
    the untested-engine finding would collapse to zero without a single test being written."""
    own = "engine/uci_probe.py"
    assert (
        surface._planes_for_needles((own,), {own: (surface.PLANE_CI, own)}, {own: own}, {}, own)
        == set()
    )
    other = "engine/some_other.py"
    assert surface._planes_for_needles(
        (own,), {other: (surface.PLANE_CI, own)}, {other: own}, {other: own}, own
    ) == {surface.PLANE_CI, surface.PLANE_PYTHON, surface.PLANE_TEST}


def test_a_key_measured_for_the_first_time_is_seeded_rather_than_refused(
    built: inventory.Inventory, declaration: contract.Declaration
) -> None:
    """SEEDED is the state a ratchet enters the first time a key is measured, and it must HOLD:
    refusing it would make a new law unaddable without hand-writing the ceiling this whole design
    exists to remove. Every future run is then held to the seeded value or better."""

    key = sorted(contract.RATCHETED)[0]
    empty = ratchet_module.load("/nonexistent/uci-ratchet.json")
    result = contract._ratcheted(built, declaration, key, empty)
    assert result.holds
    assert result.detail.startswith("SEEDED at ")


def test_an_extraction_whose_interpreter_has_gone_is_rebuilt_rather_than_reused(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Reuse is keyed on the commit, the dependency digest AND the interpreter still being
    there. A measurement taken with an interpreter that no longer exists is attributable to
    nothing, so its absence has to reopen the extraction rather than be read as a hit."""
    root = _tiny_repo(tmp_path)
    sha = immutable.resolve_sha(str(root))
    workspace = tmp_path / "workspace"

    def _fake_venv(destination: str) -> str:
        binaries = Path(destination) / ".uci-venv" / "bin"
        binaries.mkdir(parents=True, exist_ok=True)
        interpreter = binaries / "python"
        interpreter.write_text("#!/bin/sh\n", encoding="utf-8")
        return str(interpreter)

    monkeypatch.setattr(immutable, "_build_venv", _fake_venv)
    first = immutable.prepare(str(root), sha, workspace=str(workspace), build_venv=True, reuse=True)
    Path(first.python).unlink()
    rebuilt = immutable.prepare(
        str(root), sha, workspace=str(workspace), build_venv=True, reuse=True
    )
    assert rebuilt.reused is False
    assert Path(rebuilt.python).exists()


def test_an_owner_that_is_not_a_string_is_not_collected_into_the_binding_set() -> None:
    """_owners_named_by must refuse a non-string canonical_owner without raising.

    The corpus holds registries where a binding id appears in several places; a document
    that carries an owner as a mapping or number is malformed for this walk, and the walk
    must keep looking rather than poison the set or explode.
    """
    from engine.root_ontology.contract import _owners_named_by

    assert _owners_named_by({"id": "BIND-X", "canonical_owner": 7}, "BIND-X") == set()
    assert _owners_named_by({"id": "BIND-X", "canonical_owner": "Str"}, "BIND-X") == {"Str"}
