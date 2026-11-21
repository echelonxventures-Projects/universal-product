"""UEC-000001 — the non-vacuity and mutation-resistance suite.

WHY THIS FILE IS THE LOAD-BEARING HALF OF THE PROGRAMME.

Twelve laws that hold and cannot be made to fail would measure nothing. That is not a
hypothetical here: it was measured. A one-line ``return True`` inserted into ``compare()`` in
``00-MASTER/UIS-001/uis_engine.py`` and ``00-MASTER/ACEE-000001/acee_engine.py`` flipped both
gates from exit 1 (CLOSED) to exit 0 (OPEN); all nine of UIS's own ``--check-*`` self-guards
still passed; and zero test files in the entire repository reference either programme, so
nothing could kill the mutant.

The same technique applied to UVI's anti-removal laws was killed by five tests
(``test_l03_refuses_a_stage_the_script_does_not_declare`` and four others). That contrast is the
whole finding: the repository already knows how to write a mutation-resistant guard, and had
done it exactly once. This file generalises the pattern to the closure mechanism itself, because
a guard-of-guards that could not refuse would be the most expensive kind of decoration.

STRUCTURE. One reachable PASS (without it every refusal assertion below would be vacuous), then
one independent forged violation per law, then the digest-completeness mutations, then
determinism. Every mutation is applied to a COPY of the declaration or to a throwaway worktree —
never to the repository under test.
"""

from __future__ import annotations

import copy
import importlib
import json
import subprocess
import sys
import types
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

from engine.construct.declaration import Declaration as ConstructDeclaration
from engine.enforcement_closure import contract, discovery, gate
from engine.enforcement_closure.contract import LAW_CHECKS, Probe, load_contract, measure
from engine.enforcement_closure.declaration import DIGEST_EXCLUSIONS, load, parse
from engine.enforcement_closure.discovery import _invocation_needles, _needles
from engine.enforcement_closure.model import (
    KIND_MAKE_TARGET,
    KIND_MODULE_GATE,
    REFUSED,
    Artifact,
    DeclarationError,
    EnforcementError,
    Rule,
)
from engine.uckp.canonical import content_hash

ROOT = discovery.repo_root()
DECLARATION_PATH = Path(ROOT) / "00-MASTER" / "UEC-000001" / "uec-declaration.json"


@pytest.fixture(scope="module")
def document() -> dict[str, Any]:
    return json.loads(DECLARATION_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def report() -> dict[str, Any]:
    return measure(repository=ROOT)


def _probe(document: dict[str, Any]) -> Probe:
    """A probe over a mutated declaration, measured against the real repository."""
    return Probe(parse(document, source="test"), repository=ROOT)


def _git_status() -> str:
    return subprocess.run(  # noqa: S603 - fixed argv, no shell
        ["git", "status", "--porcelain"],  # noqa: S607 - git from PATH by design
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout


def _run(document: dict[str, Any], check: str) -> list[str]:
    return list(LAW_CHECKS[check](_probe(document)))


# ---------------------------------------------------------------------------
# a reachable PASS. Without this, every refusal assertion below would be vacuous.


def test_the_gate_is_open_on_the_measured_working_tree(report: dict[str, Any]) -> None:
    """The adopted state must be reachable, or the ratchet was declared against fiction."""
    refusals = [row for row in report["laws"] if row["verdict"] == REFUSED and row["blocking"]]
    assert not refusals, "blocking refusals on the measured WORKING TREE: " + json.dumps(
        [{"law": row["law_id"], "violations": row["violations"][:4]} for row in refusals], indent=1
    )
    assert report["status"] == "OPEN"


def test_every_declared_law_is_measured_and_every_check_is_declared(
    report: dict[str, Any], document: dict[str, Any]
) -> None:
    """Two-way binding. One-way binding is how BC-1 happened: R-01..R-09 declared, R-01..R-08
    implemented, and ``classify()`` returning ERROR for every subject."""
    measured = {row["law_id"] for row in report["laws"]}
    declared = {row["law_id"] for row in document["laws"]}
    assert measured == declared
    assert {row["check"] for row in document["laws"]} == set(LAW_CHECKS)


def test_the_enforcement_plane_is_not_empty(report: dict[str, Any]) -> None:
    """The population floor, asserted independently of the law that enforces it."""
    counts = report["counts"]
    assert counts["artifacts"] >= 100, counts
    assert counts["engines"] >= 30, counts
    assert counts["declarations"] >= 15, counts
    assert counts["tracked"] >= 1000, counts


def test_the_ratchet_has_no_slack_in_either_direction(report: dict[str, Any]) -> None:
    """measured == ceiling, exactly. A ceiling above reality is room for a silent regression."""
    declared, measured = report["ratchet_declared"], report["ratchet_measured"]
    for key, value in measured.items():
        assert key in declared, f"{key} has no declared ceiling"
        assert value == declared[key], (
            f"{key}: measured {value}, ceiling {declared[key]}. The satisfied state is equality; "
            "a higher ceiling absorbs the next violation and a lower one is a repair nobody "
            "recorded."
        )


# ---------------------------------------------------------------------------
# UEC-L-01 — vacuity. A discoverer that went blind must not report success.


@pytest.mark.parametrize("pattern", ["00-MASTER/*/NO_SUCH_ENGINE.py", "does/not/exist/*.py"])
def test_l01_refuses_a_discovery_rule_that_matches_nothing(
    document: dict[str, Any], pattern: str
) -> None:
    mutated = copy.deepcopy(document)
    mutated["discovery_rules"][0]["pattern"] = pattern
    violations = _run(mutated, "discovery_rules_are_non_vacuous")
    assert violations, "a rule matching nothing was accepted as satisfied"
    assert "stopped seeing" in " ".join(violations)


def test_l01_refuses_a_floor_of_zero_at_parse_time(document: dict[str, Any]) -> None:
    """A floor of zero is not a floor. Refused before any law runs, so it cannot be argued."""
    mutated = copy.deepcopy(document)
    mutated["discovery_rules"][0]["floor"] = 0
    with pytest.raises(DeclarationError, match="floor of zero"):
        parse(mutated, source="test")


def test_l01_refuses_a_negative_floor(document: dict[str, Any]) -> None:
    mutated = copy.deepcopy(document)
    mutated["discovery_rules"][0]["floor"] = -1
    with pytest.raises(DeclarationError):
        parse(mutated, source="test")


def test_l01_refuses_a_floor_that_is_not_an_integer(document: dict[str, Any]) -> None:
    mutated = copy.deepcopy(document)
    mutated["discovery_rules"][0]["floor"] = "many"
    with pytest.raises(DeclarationError, match="integer floor"):
        parse(mutated, source="test")


def test_l01_refuses_a_floor_raised_above_the_measured_population(document: dict[str, Any]) -> None:
    """The floor works upward too: a rule cannot claim a population it does not have."""
    mutated = copy.deepcopy(document)
    mutated["discovery_rules"][0]["floor"] = 10_000
    assert _run(mutated, "discovery_rules_are_non_vacuous")


# ---------------------------------------------------------------------------
# UEC-L-02 — deletion. The measured E4 defect, as an assertion.


def test_l02_refuses_a_governed_artifact_that_is_gone(document: dict[str, Any]) -> None:
    mutated = copy.deepcopy(document)
    mutated["governed_enforcement"].append(
        {
            "identity": ".github/workflows/deleted-by-someone.yml",
            "kind": "WORKFLOW",
            "owner": "gate owner",
            "rule_id": "UEC-R-03",
        }
    )
    violations = _run(mutated, "declared_enforcement_exists")
    assert any("deleted-by-someone" in item for item in violations)


def test_l02_refuses_an_artifact_that_is_both_governed_and_withdrawn(
    document: dict[str, Any],
) -> None:
    """Required and released at once is not a state; it is a contradiction that hides a deletion."""
    mutated = copy.deepcopy(document)
    victim = next(row for row in mutated["governed_enforcement"] if row["kind"] == "WORKFLOW")
    mutated["withdrawals"]["entries"].append(
        {
            "identity": victim["identity"],
            "kind": victim["kind"],
            "owner": "someone",
            "reason": "hiding a deletion behind a withdrawal",
            "date": "2026-01-01",
        }
    )
    # Still present on disk, so UEC-L-12 must also refuse it.
    assert _run(mutated, "withdrawals_are_reasoned_and_capped")


def test_l02_holds_when_a_missing_artifact_is_properly_withdrawn(document: dict[str, Any]) -> None:
    """The escape hatch works, and its shape is deliberate.

    A withdrawal REMOVES the artifact from ``governed_enforcement`` and records why in
    ``withdrawals.entries``. It does not mark a governed entry as withdrawn — "required and
    released at once" is not a state, and ``test_l02_refuses_an_artifact_that_is_both_governed_
    and_withdrawn`` asserts that contradiction is refused.

    So removing a protection costs FOUR coordinated edits to one governed file: delete the
    artifact, drop its inventory entry, decrement ``ratchet.governed_artifacts``, and add a
    withdrawal carrying an owner, a reason and a date. All four land in one ``git diff``. That is
    the entire difference from the measured baseline, where deleting seven workflow files and six
    Makefile gate targets produced a byte-identical test outcome and no diff anyone had to read.
    """
    mutated = copy.deepcopy(document)
    mutated["withdrawals"]["entries"].append(
        {
            "identity": ".github/workflows/retired.yml",
            "kind": "WORKFLOW",
            "owner": "gate owner",
            "reason": "superseded by the aggregate leg; recorded rather than deleted",
            "date": "2026-08-28",
        }
    )
    assert not _run(mutated, "declared_enforcement_exists")
    assert not _run(mutated, "withdrawals_are_reasoned_and_capped")


def test_removing_an_artifact_from_the_inventory_still_fails_on_the_governed_count(
    document: dict[str, Any],
) -> None:
    """The cheapest bypass, closed.

    Deleting a workflow AND quietly dropping its inventory row would satisfy UEC-L-02 and
    UEC-L-03. ``ratchet.governed_artifacts`` is what refuses it: the count and the inventory
    length must agree, so the shrink cannot happen without also editing the number that guards
    it — and UEC-L-11 reports the disagreement by name.
    """
    mutated = copy.deepcopy(document)
    mutated["governed_enforcement"] = mutated["governed_enforcement"][:-1]
    violations = _run(mutated, "no_assurance_reduction")
    assert any("governed_artifacts" in item for item in violations), violations


# ---------------------------------------------------------------------------
# UEC-L-03 — ungoverned addition. The other direction, without which the inventory
# could be bypassed by adding rather than removing.


def test_l03_refuses_an_ungoverned_enforcement_artifact(document: dict[str, Any]) -> None:
    mutated = copy.deepcopy(document)
    removed = mutated["governed_enforcement"].pop()
    violations = _run(mutated, "discovered_enforcement_is_governed")
    assert any(removed["identity"] in item for item in violations), violations


def test_l03_refuses_when_the_whole_inventory_is_emptied(document: dict[str, Any]) -> None:
    """An empty inventory must not read as "nothing to govern"."""
    mutated = copy.deepcopy(document)
    mutated["governed_enforcement"] = [mutated["governed_enforcement"][0]]
    violations = _run(mutated, "discovered_enforcement_is_governed")
    assert len(violations) > 100, "emptying the inventory produced almost no findings"


# ---------------------------------------------------------------------------
# UEC-L-04 / L-05 / L-06 — dead, untested and single-pointed enforcement.


def test_l04_refuses_an_engine_nothing_invokes(document: dict[str, Any]) -> None:
    """Measured by pointing the engine rule at a module no invocation plane names."""
    mutated = copy.deepcopy(document)
    rule = next(r for r in mutated["discovery_rules"] if r["rule_id"] == "UEC-R-02")
    rule["pattern"] = "engine/*/model.py"
    rule["floor"] = 1
    probe = _probe(mutated)
    violations = list(LAW_CHECKS["every_engine_has_an_invoker"](probe))
    assert violations, "a module no plane invokes was accepted as enforcing"


@pytest.mark.parametrize(
    "key,check",
    [
        ("engines_without_a_test", "every_engine_has_a_test"),
        ("artifacts_with_one_invocation_plane", "no_single_invocation_plane"),
        ("declarations_no_code_consumes", "every_declaration_is_consumed"),
        ("declarations_without_a_certification_identity", "certification_identity_exists"),
    ],
)
def test_a_lowered_ceiling_refuses_and_a_raised_ceiling_is_caught_by_l11(
    document: dict[str, Any], key: str, check: str
) -> None:
    """Both halves of the ratchet, for every ratcheted law.

    Lowering the ceiling below reality must refuse (that is what happens when a NEW violation
    appears). Raising it above reality must ALSO refuse, via UEC-L-11 — otherwise a generous
    ceiling would silently absorb the next violation, which is how a ratchet becomes decoration.

    A CEILING OF ZERO HAS NO LOWER HALF, AND CLAMPING IS NOT THE ANSWER. This assertion used to
    read `max(ceiling - 1, 0)`, which was correct while every ceiling was positive and became
    silently vacuous the moment one reached zero: `max(-1, 0)` is the ceiling the declaration
    already carries, so the mutated document was the committed one and the refusal being asserted
    was the absence of a change. `declarations_without_a_certification_identity` reached zero when
    both offenders were repaired, and the test kept passing for a reason unrelated to the property
    it names. A fully repaired class is therefore skipped EXPLICITLY here, with the upper half —
    the half that still means something once a class is at zero — asserted below.
    """
    lowered = copy.deepcopy(document)
    ceiling = lowered["ratchet"][key]
    if ceiling > 0:
        lowered["ratchet"][key] = ceiling - 1
        assert _run(lowered, check), f"{check} accepted a population above its ceiling"
    else:
        assert not _run(lowered, check), (
            f"{key} declares a ceiling of 0, so the class is fully repaired and the law must "
            "hold over the committed declaration; it does not"
        )

    raised = copy.deepcopy(document)
    raised["ratchet"][key] = ceiling + 5
    slack = _run(raised, "no_assurance_reduction")
    assert any(key in item for item in slack), f"UEC-L-11 tolerated slack in {key}"


def test_a_ratcheted_law_with_no_declared_ceiling_refuses(document: dict[str, Any]) -> None:
    """A measurement with no ceiling is enforced by nothing. Absence must not read as zero."""
    mutated = copy.deepcopy(document)
    del mutated["ratchet"]["engines_without_a_test"]
    violations = _run(mutated, "every_engine_has_a_test")
    assert any("no declared ceiling" in item for item in violations)


def test_l11_refuses_a_governed_count_that_disagrees_with_the_inventory(
    document: dict[str, Any],
) -> None:
    mutated = copy.deepcopy(document)
    mutated["ratchet"]["governed_artifacts"] = mutated["ratchet"]["governed_artifacts"] + 7
    violations = _run(mutated, "no_assurance_reduction")
    assert any("governed_artifacts" in item for item in violations)


# ---------------------------------------------------------------------------
# UEC-L-09 — self-coverage. Discovery D-09 as an executable invariant.


def test_l09_holds_on_the_measured_working_tree() -> None:
    """UEC is inside UEC. If this ever fails, the closure mechanism has left its own closure."""
    report = measure(repository=ROOT, laws=["UEC-L-09"])
    row = report["laws"][0]
    assert row["verdict"] != REFUSED, row["violations"]


def test_l09_refuses_when_uec_removes_itself_from_its_own_inventory(
    document: dict[str, Any],
) -> None:
    mutated = copy.deepcopy(document)
    mutated["governed_enforcement"] = [
        row
        for row in mutated["governed_enforcement"]
        if "UEC-000001" not in row["identity"]
        and "enforcement_closure" not in row["identity"]
        and row["identity"] != "uec-gate"
    ]
    violations = _run(mutated, "self_coverage_is_a_fixed_point")
    assert violations, "UEC accepted being outside its own governed inventory"


def test_l09_refuses_an_empty_self_coverage_declaration(document: dict[str, Any]) -> None:
    """A law that describes nothing holds by describing nothing. Refused explicitly."""
    mutated = copy.deepcopy(document)
    mutated["self_coverage"] = {"artifacts": []}
    violations = _run(mutated, "self_coverage_is_a_fixed_point")
    assert any("describing nothing" in item for item in violations)


def test_l09_refuses_a_self_coverage_artifact_that_does_not_exist(document: dict[str, Any]) -> None:
    mutated = copy.deepcopy(document)
    mutated["self_coverage"]["artifacts"].append(
        {"identity": "engine/enforcement_closure/absent.py", "kind": "MODULE_GATE"}
    )
    assert _run(mutated, "self_coverage_is_a_fixed_point")


def test_uec_own_gate_is_invoked_from_at_least_two_planes() -> None:
    """The law UEC applies to everything else, applied to UEC, asserted independently of it."""
    _declaration, probe = load_contract(repository=ROOT)
    own = next(
        artifact
        for artifact in probe.artifacts
        if artifact.identity == "engine/enforcement_closure/gate.py"
    )
    planes = probe.invokers(own)
    assert len(planes) >= 2, f"UEC's own gate has one invocation plane: {planes}"
    assert probe.test_bindings(own), "UEC's own gate has no test binding"


# ---------------------------------------------------------------------------
# UEC-L-10 / L-12 — plane partition and the escape hatch.


def test_l10_refuses_an_enforcement_artifact_inside_the_corpus_boundary(
    document: dict[str, Any],
) -> None:
    """Two closure mechanisms may not each claim one object and answer differently about it."""
    mutated = copy.deepcopy(document)
    mutated["corpus_plane"]["exclude_dir_prefixes"] = [".git/"]
    violations = _run(mutated, "planes_are_disjoint")
    assert violations, "an artifact in both planes was accepted"


def test_l10_refuses_an_undeclared_corpus_boundary(document: dict[str, Any]) -> None:
    mutated = copy.deepcopy(document)
    mutated["corpus_plane"]["include_extensions"] = []
    violations = _run(mutated, "planes_are_disjoint")
    assert any("cannot be measured" in item for item in violations)


def test_l12_refuses_more_withdrawals_than_the_declared_cap(document: dict[str, Any]) -> None:
    mutated = copy.deepcopy(document)
    mutated["withdrawals"]["cap"] = 0
    mutated["withdrawals"]["entries"] = [
        {
            "identity": ".github/workflows/gone.yml",
            "kind": "WORKFLOW",
            "owner": "o",
            "reason": "r",
            "date": "2026-01-01",
        }
    ]
    assert _run(mutated, "withdrawals_are_reasoned_and_capped")


@pytest.mark.parametrize("field", ["owner", "reason", "date"])
def test_l12_refuses_a_withdrawal_missing_owner_reason_or_date(
    document: dict[str, Any], field: str
) -> None:
    """The escape hatch is expensive by construction. A blank field would make it free."""
    mutated = copy.deepcopy(document)
    entry = {
        "identity": ".github/workflows/gone.yml",
        "kind": "WORKFLOW",
        "owner": "o",
        "reason": "r",
        "date": "2026-01-01",
    }
    entry[field] = ""
    mutated["withdrawals"]["entries"] = [entry]
    with pytest.raises(DeclarationError, match=field):
        parse(mutated, source="test")


# ---------------------------------------------------------------------------
# DIGEST COMPLETENESS. The measured UCON defect, refused here by mutation.
#
# `engine/tests/unit/test_construct_foundation.py:263-265,922-930` asserts that UCON's digest is
# STABLE. Stability is the half that cannot detect this defect class: flipping `blocking` on
# UCON-L-01, rewriting rule UCON-DR-01's assigned disposition and zeroing an evidence floor all
# leave `declaration_digest` at 192c63af… byte-identical, while `contract.py:1018` makes the
# verdict depend on `blocking`. These tests assert the other half — that a semantic edit MOVES it.


def _digest(document: dict[str, Any]) -> str:
    return content_hash(parse(document, source="test").digest_payload())


SEMANTIC_MUTATIONS: dict[str, Callable[[dict[str, Any]], None]] = {
    "flip a law's blocking flag": lambda d: d["laws"][0].__setitem__("blocking", False),
    "rename a law's check": lambda d: d["laws"][0].__setitem__("check", "planes_are_disjoint"),
    "raise a ratchet ceiling": lambda d: d["ratchet"].__setitem__("engines_without_a_test", 99),
    "lower a discovery floor": lambda d: d["discovery_rules"][0].__setitem__("floor", 1),
    "widen a discovery pattern": lambda d: d["discovery_rules"][0].__setitem__(
        "pattern", "**/*.py"
    ),
    "raise the withdrawal cap": lambda d: d["withdrawals"].__setitem__("cap", 99),
    "add a withdrawal": lambda d: d["withdrawals"]["entries"].append(
        {"identity": "x", "kind": "WORKFLOW", "owner": "o", "reason": "r", "date": "d"}
    ),
    "drop a governed artifact": lambda d: d["governed_enforcement"].pop(),
    "drop a self-coverage artifact": lambda d: d["self_coverage"]["artifacts"].pop(),
    "widen the corpus boundary": lambda d: d["corpus_plane"]["exclude_dir_prefixes"].append("x/"),
    "change the declared authority": lambda d: d.__setitem__("authority", "SOMETHING ELSE"),
    "drop a testpath": lambda d: d["testpaths"].pop(),
}


@pytest.mark.parametrize("name", sorted(SEMANTIC_MUTATIONS))
def test_every_semantic_mutation_moves_the_certification_identity(
    document: dict[str, Any], name: str
) -> None:
    baseline = _digest(document)
    mutated = copy.deepcopy(document)
    SEMANTIC_MUTATIONS[name](mutated)
    assert _digest(mutated) != baseline, (
        f"{name!r} changed the declaration's meaning and left the certification identity "
        "unchanged. A field that can alter a verdict must be inside the identity."
    )


def test_the_digest_is_stable_under_the_declared_exclusions(document: dict[str, Any]) -> None:
    """The other half. Both halves are required; only one of them was ever asserted."""
    baseline = _digest(document)
    mutated = copy.deepcopy(document)
    mutated["$comment"] = "prose may change freely; it reaches no law"
    assert _digest(mutated) == baseline


def test_the_digest_covers_every_field_except_the_enumerated_exclusions(
    document: dict[str, Any],
) -> None:
    """Inclusion is the default. Any key absent from the payload must be a declared exclusion."""
    payload = parse(document, source="test").digest_payload()
    missing = set(document) - set(payload)
    assert missing <= set(DIGEST_EXCLUSIONS), (
        "fields silently absent from the certification identity: "
        f"{sorted(missing - set(DIGEST_EXCLUSIONS))}"
    )


def test_a_stale_digest_exclusion_is_refused(document: dict[str, Any], monkeypatch) -> None:
    """An exclusion matching nothing cannot be justified and may silently widen later."""
    monkeypatch.setitem(DIGEST_EXCLUSIONS, "no_such_field", "stale")
    with pytest.raises(DeclarationError, match="no_such_field"):
        parse(copy.deepcopy(document), source="test")


def test_the_digest_is_independent_of_the_path_it_was_read_from(document: dict[str, Any]) -> None:
    left = parse(copy.deepcopy(document), source="a/uec-declaration.json")
    right = parse(copy.deepcopy(document), source="b/uec-declaration.json")
    assert content_hash(left.digest_payload()) == content_hash(right.digest_payload())


# ---------------------------------------------------------------------------
# structural refusals at parse time.


def test_a_declaration_missing_any_section_faults(document: dict[str, Any]) -> None:
    for section in (
        "discovery_rules",
        "governed_enforcement",
        "laws",
        "ratchet",
        "corpus_plane",
        "self_coverage",
        "testpaths",
        "gate",
    ):
        mutated = copy.deepcopy(document)
        del mutated[section]
        with pytest.raises(DeclarationError, match=section):
            parse(mutated, source="test")


def test_a_law_without_an_explicit_blocking_boolean_faults(document: dict[str, Any]) -> None:
    """Leaving `blocking` implicit is how a law becomes advisory without anyone deciding it."""
    mutated = copy.deepcopy(document)
    del mutated["laws"][0]["blocking"]
    with pytest.raises(DeclarationError, match="blocking"):
        parse(mutated, source="test")


def test_a_law_naming_an_unimplemented_check_faults(document: dict[str, Any], tmp_path) -> None:
    """One-way law binding is the BC-1 shape: declared R-01..R-09, implemented R-01..R-08."""
    mutated = copy.deepcopy(document)
    mutated["laws"][0]["check"] = "a_check_nobody_wrote"
    path = tmp_path / "uec-declaration.json"
    path.write_text(json.dumps(mutated), encoding="utf-8")
    with pytest.raises(EnforcementError, match="not two-way bound"):
        load_contract(str(path), repository=ROOT)


def test_a_governed_entry_naming_an_undeclared_rule_faults(document: dict[str, Any]) -> None:
    mutated = copy.deepcopy(document)
    mutated["governed_enforcement"][0]["rule_id"] = "UEC-R-99"
    with pytest.raises(DeclarationError, match="UEC-R-99"):
        parse(mutated, source="test")


def test_a_duplicated_governed_entry_faults(document: dict[str, Any]) -> None:
    mutated = copy.deepcopy(document)
    mutated["governed_enforcement"].append(dict(mutated["governed_enforcement"][0]))
    with pytest.raises(DeclarationError, match="twice"):
        parse(mutated, source="test")


def test_an_unknown_discovery_strategy_faults(document: dict[str, Any]) -> None:
    """Skipping it silently would let a declaration disable a rule by misspelling it."""
    mutated = copy.deepcopy(document)
    mutated["discovery_rules"][0]["strategy"] = "vibes"
    with pytest.raises(EnforcementError, match="unknown strategy"):
        _probe(mutated)


def test_an_absent_declaration_faults_rather_than_passing() -> None:
    with pytest.raises(DeclarationError, match="does not resolve"):
        load("00-MASTER/NOPE/uec-declaration.json", repository=ROOT)


# ---------------------------------------------------------------------------
# determinism and purity.


def test_two_measurements_of_one_state_are_byte_identical() -> None:
    left = json.dumps(measure(repository=ROOT), sort_keys=True)
    right = json.dumps(measure(repository=ROOT), sort_keys=True)
    assert left == right


def test_the_gate_writes_nothing() -> None:
    """READ_ONLY is measured, not declared.

    An evidence store inside the tracked tree is a second answer to "did this pass", and the
    gate declares it writes nothing at all — so the claim is checked rather than believed.
    """
    before = _git_status()
    subprocess.run(  # noqa: S603 - fixed argv, no shell
        [sys.executable, "-m", "engine.enforcement_closure.gate", "--json", "--quiet"],
        cwd=ROOT,
        capture_output=True,
        check=False,
    )
    assert before == _git_status()


def test_the_report_embeds_no_clock_and_no_machine_path(report: dict[str, Any]) -> None:
    body = json.dumps(report)
    assert "/Users/" not in body and "/home/" not in body
    assert not any(
        part.count("-") == 2 and "T" in part for part in body.split('"') if len(part) == 19
    )


def test_the_inventory_command_does_not_rewrite_the_declaration() -> None:
    """The bypass this programme exists to close.

    If the observation could rewrite the expectation, deleting a workflow and re-running the
    generator would produce a green gate. Adoption must be a human paste into a governed file.
    """
    before = DECLARATION_PATH.read_bytes()
    contract.inventory(repository=ROOT)
    assert DECLARATION_PATH.read_bytes() == before


def test_the_gate_module_declares_three_distinct_exit_codes() -> None:
    assert (gate.EXIT_OPEN, gate.EXIT_CLOSED, gate.EXIT_FAULT) == (0, 1, 2)


def test_a_fault_is_not_reported_as_a_pass(tmp_path) -> None:
    """exit 2 must be reachable and must differ from exit 0. Collapsing them would let an
    unreadable declaration pass as whichever answer happened to be convenient."""
    broken = tmp_path / "uec-declaration.json"
    broken.write_text("{ not json", encoding="utf-8")
    assert gate.main(["--gate", "--quiet", "--declaration", str(broken)]) == gate.EXIT_FAULT


def test_declaration_module_exposes_no_hardcoded_authority() -> None:
    """UVI reports a hardcoded ``"NONE — DERIVED TRUTH"`` at ``gate.py:634`` while its
    declaration carries a 400-character governed statement. The report must be DERIVED."""
    report = measure(repository=ROOT)
    assert report["authority"] == load(repository=ROOT).authority
    assert len(report["authority"]) > 100, "the reported authority is not the declared one"


# ---------------------------------------------------------------------------
# UEC-L-13 — the SUFFICIENT condition of certification identity, over the whole governed
# population rather than over this programme alone.
#
# The tests above prove UEC's OWN identity is mutation-complete. That was the whole of the
# property until UEC-L-13 existed, and scoping a detector to its own author is the
# single-point-of-failure this programme refuses: the law could never fire for anybody else, and
# `engine/construct` and `engine/recursive_knowledge` both carried the exact defect the tests
# above were written to describe while every gate in the repository reported green.
#
# These tests hold the generalised law to the same standard as every other one here: a reachable
# pass, then an independent forged violation for each way it can be defeated.


def test_l13_passes_over_the_measured_working_tree(report: dict[str, Any]) -> None:
    """The reachable PASS. Without it every refusal below would be vacuous."""
    row = next(r for r in report["laws"] if r["law_id"] == "UEC-L-13")
    assert row["verdict"] != REFUSED, row["violations"]
    assert row["blocking"] is True


def test_l13_measures_a_non_empty_population(document: dict[str, Any]) -> None:
    """A law quantified over nothing holds by describing nothing."""
    owners = contract._uniform_identity_owners(_probe(copy.deepcopy(document)))
    assert owners, "no declaration exposes the uniform identity interface, so L-13 is vacuous"
    assert len(owners) == document["ratchet"]["declarations_with_uniform_identity"]


def test_l13_refuses_a_declaration_whose_identity_is_a_projection(
    document: dict[str, Any], monkeypatch: pytest.MonkeyPatch
) -> None:
    """The measured defect, restored on purpose. This is the mutant the law exists to kill.

    Before the remedy, `engine/construct` listed eleven keys by hand and collapsed ten of them to
    bare identifiers, so flipping `blocking` on UCON-L-01 — the flag its own contract reads to
    choose OPEN or CLOSED — left `declaration_digest` byte-identical at 192c63af…. Reinstating
    that projection here must be refused, or the law would not have detected the defect it was
    written for.
    """
    monkeypatch.setattr(
        ConstructDeclaration,
        "digest_payload",
        lambda self: {
            "artifact_id": self.artifact_id,
            "laws": [law.law_id for law in self.laws],
            "rules": [rule.rule_id for rule in self.rules],
            "version": self.version,
        },
    )
    violations = _run(copy.deepcopy(document), "certification_identity_is_complete")
    assert violations, "a projection-based identity passed the law that exists to refuse it"
    assert any("ucon-declaration.json" in violation for violation in violations)
    assert any("blocking" in violation for violation in violations)


def test_l13_refuses_a_population_that_moved_without_a_governance_act(
    document: dict[str, Any],
) -> None:
    """Two-sided. A package silently JOINING the measured set is as much a change as leaving."""
    mutated = copy.deepcopy(document)
    mutated["ratchet"]["declarations_with_uniform_identity"] += 1
    assert _run(mutated, "certification_identity_is_complete")

    mutated = copy.deepcopy(document)
    mutated["ratchet"]["declarations_with_uniform_identity"] -= 1
    assert _run(mutated, "certification_identity_is_complete")


def test_l13_refuses_a_removed_ceiling(document: dict[str, Any]) -> None:
    """Threshold removal. A measurement with no ceiling is recorded and enforced by nothing."""
    mutated = copy.deepcopy(document)
    del mutated["ratchet"]["declarations_with_uniform_identity"]
    violations = _run(mutated, "certification_identity_is_complete")
    assert violations
    assert any("no declared ceiling" in violation for violation in violations)


def test_l13_mutations_target_values_that_actually_decide_a_verdict(
    document: dict[str, Any],
) -> None:
    """A mutation set aimed at inert fields would pass while proving nothing.

    Every mutation must name a value some programme's contract reads to reach a verdict. The
    check is structural rather than a restatement: each mutation is applied to UEC's own
    declaration and must move UEC's own identity, which is the same property the law asserts of
    everybody else.
    """
    assert contract.IDENTITY_MUTATIONS, "the mutation set is empty, so the law tests nothing"
    baseline = _digest(document)
    applied = 0
    for name, (guard, mutate) in contract.IDENTITY_MUTATIONS.items():
        mutated = copy.deepcopy(document)
        if not guard(mutated):
            continue
        applied += 1
        mutate(mutated)
        assert _digest(mutated) != baseline, f"mutation {name!r} reaches no part of the identity"
    assert applied == len(contract.IDENTITY_MUTATIONS), (
        "UEC's own declaration must carry every field the mutation set targets; a guard that "
        "skips here would mean the law is being held to a weaker standard by its own author "
        f"than by the population it measures ({applied} of {len(contract.IDENTITY_MUTATIONS)})"
    )
    assert applied >= contract.IDENTITY_MUTATION_FLOOR


def test_l13_treats_an_unmeasurable_identity_as_a_failure_not_a_pass(
    document: dict[str, Any], monkeypatch: pytest.MonkeyPatch
) -> None:
    """Fail-closed. An identity that cannot be measured is never silently accepted."""

    def explode(self: Any) -> dict[str, Any]:
        raise RuntimeError("the identity cannot be computed")

    monkeypatch.setattr(ConstructDeclaration, "digest_payload", explode)
    violations = _run(copy.deepcopy(document), "certification_identity_is_complete")
    assert violations
    assert any("could not be measured" in violation for violation in violations)


# ---------------------------------------------------------------------------
# A RATCHET AT ZERO STILL HAS TO BE ABLE TO REFUSE.
#
# `declarations_without_a_certification_identity` reached 0 when both offenders were repaired,
# and a mutation campaign immediately found what that cost: neutering
# `certification_identity_exists` to `return []` left this suite green. With no offender in the
# repository, "the law found none" and "the law was deleted" became the same observation. The
# same hole opens for every ratcheted law the day its class is repaired, so the test is
# parametrised over all of them rather than written for the one that hit zero first.


@pytest.mark.parametrize(
    "key,check",
    [
        ("engines_without_a_test", "every_engine_has_a_test"),
        ("artifacts_with_one_invocation_plane", "no_single_invocation_plane"),
        ("declarations_no_code_consumes", "every_declaration_is_consumed"),
        ("declarations_without_a_certification_identity", "certification_identity_exists"),
    ],
)
def test_a_ratcheted_law_refuses_a_population_above_its_ceiling(
    document: dict[str, Any], key: str, check: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Forge one more offender than the ceiling allows; the law must name it.

    This is the half a neutered law cannot satisfy. The offender is injected at the measurement
    the law reads, so the law is exercised exactly as it would be on the day a real violation
    appears — which is the day it has to work.
    """
    ceiling = document["ratchet"][key]
    _law_id, measure = contract.RATCHETED[key]
    forged = [f"forged/offender-{n}" for n in range(ceiling + 1)]
    monkeypatch.setitem(contract.RATCHETED, key, (_law_id, lambda probe: list(forged)))

    violations = _run(copy.deepcopy(document), check)
    assert violations, f"{check} accepted {len(forged)} offenders against a ceiling of {ceiling}"
    assert any("forged/offender-0" in item for item in violations), violations[:2]


def test_a_non_blocking_law_is_a_fault_not_a_verdict(document: dict[str, Any]) -> None:
    """A law switched off in data must be refused BEFORE any law is measured.

    Written as a law first, and a hostile audit walked through it: `measure()` closes the gate
    only on a law that is REFUSED *and* blocking, so flipping `blocking` on the law that carried
    the check made the check report the violation and made the report unable to close anything.
    Any law-level formulation has that hole, whichever law hosts it, because the attacker picks
    the host. The refusal therefore belongs at load, where it is a FAULT.
    """
    for index in range(len(document["laws"])):
        mutated = copy.deepcopy(document)
        mutated["laws"][index]["blocking"] = False
        with pytest.raises(EnforcementError, match="non-blocking"):
            contract._require_every_law_blocks(parse(mutated, source="test"))


def test_the_committed_declaration_switches_no_law_off(document: dict[str, Any]) -> None:
    """The reachable pass. Without it the refusal above could be asserting over nothing."""
    assert document["laws"], "the declaration declares no law at all"
    contract._require_every_law_blocks(parse(copy.deepcopy(document), source="test"))


def test_lowering_any_discovery_floor_is_refused(document: dict[str, Any]) -> None:
    """A floor that can be edited downward guarantees nothing.

    The audit set every floor to 1 and UEC-L-01 stayed green: each rule still located far more
    than one artifact, so the non-vacuity guarantee vanished while the measurement kept
    reporting satisfaction. The floors are ratcheted on their total, two-sided.
    """
    # LOWERED BY ANY AMOUNT, not assigned a literal. The original mutation set every floor to
    # 1, which silently stopped being a mutation for a rule whose floor is ALREADY 1 — and a
    # rule naming a single artifact (UEC-R-07/08/09, the mutation governance plane) can have no
    # other floor. Against those the assignment was a no-op, the total did not move, and the
    # test failed while reporting that the lowering had been "accepted".
    #
    # TWO REFUSAL PATHS, AND BOTH ARE ASSERTED. Above 1 the floor-total ratchet refuses. At 1
    # the only lowering available is to 0, and that is refused EARLIER and more strongly — the
    # declaration will not parse at all, because a floor of zero would permit a rule to match
    # nothing and still be satisfied. A rule at the minimum is therefore the most tightly
    # ratcheted, not the least, and the property under test is the one that holds at every
    # floor: no floor can be lowered by any amount without a refusal.
    for index, rule in enumerate(document["discovery_rules"]):
        for lowered in sorted({1, rule["floor"] - 1} & set(range(rule["floor"]))):
            mutated = copy.deepcopy(document)
            mutated["discovery_rules"][index]["floor"] = lowered
            if lowered == 0:
                # Refused at parse time, and already pinned by
                # test_l01_refuses_a_floor_of_zero_at_parse_time. Asserting it a second time
                # here would restate that test rather than add to it.
                continue
            violations = _run(mutated, "discovery_rules_are_non_vacuous")
            assert any("floors total" in item for item in violations), (
                f"lowering the floor of rule {index} from {rule['floor']} to {lowered} was "
                f"accepted: {violations}"
            )

    raised = copy.deepcopy(document)
    raised["discovery_rules"][0]["floor"] += 5
    assert any("floors total" in item for item in _run(raised, "discovery_rules_are_non_vacuous"))


def test_a_missing_floor_ratchet_is_refused(document: dict[str, Any]) -> None:
    """Absence must not read as satisfaction — the same rule every other ceiling follows."""
    mutated = copy.deepcopy(document)
    del mutated["ratchet"]["discovery_floor_total"]
    violations = _run(mutated, "discovery_rules_are_non_vacuous")
    assert any("discovery_floor_total" in item for item in violations)


def test_invocation_needles_require_an_executable_form(document: dict[str, Any]) -> None:
    """A package name in prose is not an invocation.

    The audit pointed the Makefile target, the verify.sh stage and the workflow of a live gate at
    `engine.recursive_knowledge.NOTHING` — all three at once — and UEC-L-04 stayed green, because
    the bare package was still a needle and still appeared in every one of those lines. The gate
    had stopped running and nothing said so.
    """

    gate = Artifact(
        identity="engine/recursive_knowledge/gate.py", kind=KIND_MODULE_GATE, rule_id="UEC-R-02"
    )
    invocation = set(_invocation_needles(gate))
    assert "engine.recursive_knowledge" not in invocation, (
        "the bare package is an invocation needle again, so a gate pointed at a module that does "
        "not exist would still read as invoked"
    )
    assert "engine.recursive_knowledge.gate" in invocation
    # The generous set is unchanged: it also answers "does a TEST name this engine", where a
    # package is honest evidence. Narrowing that would report false test deficiencies.
    assert "engine.recursive_knowledge" in set(_needles(gate))


# --------------------------------------------------------------------------------
# UEC-L-14 — no verifier is trusted on the strength of being named.
#
# This module's own `test_bindings` states the gap it closes: "Naming is necessary and not
# sufficient: a test that references an engine has not been shown to kill a mutant in it.
# UEC-L-05 measures the necessary condition and says so." Nothing measured the other side,
# so a verifier could be invoked from two planes, named by a test, counted as governed — and
# still incapable of refusing anything.
# --------------------------------------------------------------------------------
_WITNESS = {
    "raise_names": ("raises",),
    "finding_names": ("problems", "findings", "violations"),
    "closed_exits": (1, 2),
}


def test_refusal_shapes_reads_a_raised_refusal() -> None:
    got = discovery.refusal_shapes(
        "import pytest\ndef t():\n    with pytest.raises(ValueError):\n        run()\n", **_WITNESS
    )
    assert "raises" in got


def test_refusal_shapes_reads_an_asserted_finding() -> None:
    got = discovery.refusal_shapes("def t():\n    assert problems\n", **_WITNESS)
    assert "asserts_findings" in got


def test_refusal_shapes_reads_an_asserted_closed_exit() -> None:
    got = discovery.refusal_shapes("def t():\n    assert main() == 1\n", **_WITNESS)
    assert "asserts_closed_exit" in got


def test_prose_describing_a_refusal_is_not_a_refusal() -> None:
    """The defect `source_evidence` exists to refuse, reproduced one layer up.

    Raw-text scanning would count a docstring that EXPLAINS a forged refusal as performing
    one — the detector satisfied by its own prose. Reading the AST is what separates a value
    from a call.
    """
    prose = '''
def t():
    """This test uses pytest.raises and asserts problems and checks == 1."""
    run()
'''
    assert discovery.refusal_shapes(prose, **_WITNESS) == frozenset()


def test_a_test_that_only_names_an_engine_is_not_a_witness() -> None:
    """Naming is the necessary condition UEC-L-05 already holds. This is the other half."""
    naming_only = 'def t():\n    engine = "00-MASTER/X-000001/x_engine.py"\n    assert engine\n'
    assert discovery.refusal_shapes(naming_only, **_WITNESS) == frozenset()


@pytest.fixture(scope="module")
def live_probe(document: dict[str, Any]) -> Probe:
    """One probe for the witness laws. Building it walks the tree, so it is built once."""
    return _probe(document)


def test_the_witness_population_is_measured_and_is_not_everything(live_probe: Probe) -> None:
    """A measurement that returns every engine, or none, is broken rather than satisfied."""
    probe = live_probe
    unwitnessed = contract.engines_without_a_refusal_witness(probe)
    assert 0 < len(unwitnessed) < len(probe.engines)


def test_being_named_is_strictly_weaker_than_being_witnessed(live_probe: Probe) -> None:
    """The gap between the two counters is the finding, and it must never invert.

    engines_without_a_test counts engines no test mentions. This counts engines no test has
    been shown to make refuse. The second set must CONTAIN the first: an engine nothing names
    cannot have been witnessed. An inversion would mean an unnamed engine was somehow
    witnessed, which would mean the witness is not external.
    """
    probe = live_probe
    named_by_nothing = set(contract.engines_without_a_test(probe))
    unwitnessed = set(contract.engines_without_a_refusal_witness(probe))
    assert (
        named_by_nothing <= unwitnessed
    ), "an engine no test names was counted as witnessed, so the witness is not external"


def test_no_verifier_can_witness_itself(live_probe: Probe) -> None:
    """`test_bindings` excludes the artifact's own identity, which is what makes 'no verifier
    is self-authoritative' computable rather than a cycle of mutual attestations."""
    for artifact in live_probe.engines:
        assert artifact.identity not in live_probe.test_bindings(artifact)


# ---------------------------------------------------------------------------------------
# the gate's SURFACE — the renderer and the argument plane
#
# WHY THESE EXIST. Every test above measures the LAWS. Nothing measured the thing an
# operator actually sees: `_render` builds the whole human-readable determination — the
# ratchet table, the per-law rows, the truncated violation list — and no test had ever
# executed a line of it. A gate whose report is unexercised can print anything at all,
# including a verdict that disagrees with the report it was handed, and the suite would
# stay green. The renderer is driven here from a SYNTHETIC report, so the three shapes
# that only appear when something is wrong (a broken ratchet, a refused blocking law, a
# refused non-blocking one, more violations than fit) are shown rather than waited for.
# ---------------------------------------------------------------------------------------


def _synthetic_report(**overrides: Any) -> dict[str, Any]:
    report: dict[str, Any] = {
        "declaration": "UEC-000001",
        "declaration_version": "1.0.0",
        "declaration_digest": "0" * 64,
        "counts": {
            "laws": 2,
            "holds": 1,
            "refused": 1,
            "tracked": 7,
            "artifacts": 5,
            "governed": 4,
            "withdrawn": 1,
            "engines": 3,
            "declarations": 2,
            "tests": 6,
        },
        "by_kind": {"gate_engine": 3, "workflow": 2},
        "ratchet_declared": {"engines_with_no_invoker": 6, "withdrawn": 1},
        "ratchet_measured": {"engines_with_no_invoker": 6, "withdrawn": 2},
        "laws": [
            {
                "law_id": "UEC-L-01",
                "statement": "every protection is governed",
                "verdict": "HOLDS",
                "blocking": True,
                "violations": [],
            },
            {
                "law_id": "UEC-L-02",
                "statement": "every engine is invoked twice",
                "verdict": REFUSED,
                "blocking": True,
                "violations": [f"violation {n}" for n in range(9)],
            },
            {
                "law_id": "UEC-L-99",
                "statement": "an advisory law",
                "verdict": REFUSED,
                "blocking": False,
                "violations": ["one advisory violation"],
            },
        ],
        "status": "CLOSED",
    }
    report.update(overrides)
    return report


def test_the_renderer_marks_a_ratchet_that_moved_and_one_that_did_not() -> None:
    text = gate._render(_synthetic_report())
    assert "  ok  engines_with_no_invoker" in text.replace("   ", "  ")
    assert "XX " in text  # the measured `withdrawn` disagrees with its declared ceiling
    assert "2 / 1" in text


def test_the_renderer_distinguishes_a_blocking_refusal_from_an_advisory_one() -> None:
    rows = {
        line.split()[1]: line.split()[0]
        for line in gate._render(_synthetic_report()).splitlines()
        if line.startswith(("  ok  UEC", "  XX  UEC", "  !!  UEC"))
    }
    assert rows["UEC-L-01"] == "ok"
    assert rows["UEC-L-02"] == "XX"
    assert rows["UEC-L-99"] == "!!"


def test_the_renderer_truncates_a_long_violation_list_and_says_how_many_it_dropped() -> None:
    text = gate._render(_synthetic_report())
    assert "- violation 5" in text
    assert "- violation 6" not in text
    assert "... +3 more" in text


def test_the_renderer_reports_the_counts_and_the_verdict_it_was_handed() -> None:
    text = gate._render(_synthetic_report(status="OPEN"))
    assert "laws measured      : 2   holds 1   refused 1" in text
    assert "tracked paths      : 7" in text
    assert "5 artifacts   (4 governed, 1 withdrawn)" in text
    assert "gate_engine          3" in text
    assert text.strip().endswith("verdict: OPEN")


def test_a_fault_names_the_repair_command_and_refuses_to_read_as_a_pass() -> None:
    text = gate._render_fault("the declaration is unreadable")
    assert "the declaration is unreadable" in text
    assert "NOT a pass and NOT a refusal" in text
    assert gate.REPAIR_COMMAND in text


def test_the_inventory_command_prints_json_and_exits_open(monkeypatch, capsys) -> None:
    monkeypatch.setattr(gate, "inventory", lambda _decl, repository: {"artifacts": ["a"]})
    assert gate.main(["--inventory"]) == gate.EXIT_OPEN
    assert json.loads(capsys.readouterr().out) == {"artifacts": ["a"]}


def test_an_open_gate_is_quiet_when_asked_to_be(monkeypatch, capsys) -> None:
    monkeypatch.setattr(
        gate, "measure", lambda _decl, repository, laws: _synthetic_report(status="OPEN")
    )
    assert gate.main(["--quiet"]) == gate.EXIT_OPEN
    captured = capsys.readouterr()
    assert captured.err == ""
    assert captured.out == ""


def test_a_closed_gate_reports_even_when_asked_to_be_quiet(monkeypatch, capsys) -> None:
    """`--quiet` suppresses the summary of a gate that is OPEN. Suppressing the summary of
    one that is CLOSED would hide the only explanation of the refusal."""
    monkeypatch.setattr(gate, "measure", lambda _decl, repository, laws: _synthetic_report())
    assert gate.main(["--quiet"]) == gate.EXIT_OPEN  # reporting is not refusing
    assert "verdict: CLOSED" in capsys.readouterr().err


def test_only_the_gate_flag_turns_a_closed_measurement_into_a_refusal(monkeypatch, capsys) -> None:
    monkeypatch.setattr(gate, "measure", lambda _decl, repository, laws: _synthetic_report())
    assert gate.main(["--gate"]) == gate.EXIT_CLOSED
    capsys.readouterr()


def test_the_json_report_is_the_report_the_summary_describes(monkeypatch, capsys) -> None:
    monkeypatch.setattr(gate, "measure", lambda _decl, repository, laws: _synthetic_report())
    assert gate.main(["--json"]) == gate.EXIT_OPEN
    captured = capsys.readouterr()
    assert json.loads(captured.out)["status"] == "CLOSED"
    assert "verdict: CLOSED" in captured.err


def test_an_enforcement_error_is_a_fault_and_never_a_verdict(monkeypatch, capsys) -> None:
    def _raise(*_args: Any, **_kwargs: Any) -> None:
        raise EnforcementError("the declaration names an unknown discovery strategy")

    monkeypatch.setattr(gate, "measure", _raise)
    assert gate.main([]) == gate.EXIT_FAULT
    assert "unknown discovery strategy" in capsys.readouterr().err


def test_a_law_filter_is_passed_through_to_the_measurement(monkeypatch) -> None:
    seen: dict[str, Any] = {}

    def _capture(declaration, repository, laws):
        seen.update(declaration=declaration, repository=repository, laws=laws)
        return _synthetic_report(status="OPEN")

    monkeypatch.setattr(gate, "measure", _capture)
    gate.main(["--quiet", "--repository", "elsewhere", "--law", "UEC-L-01", "--law", "UEC-L-02"])
    assert seen["repository"] == "elsewhere"
    assert seen["laws"] == ["UEC-L-01", "UEC-L-02"]
    assert seen["declaration"] is None


def test_the_memoized_scans_equal_their_uncached_form(document: dict[str, Any]) -> None:
    """The cache is measured against the thing it replaces, not argued for in a comment.

    `discovery` memoizes three repository-wide scans so that a mutation suite building many
    probes over one repository stops re-reading the same two thousand files per probe. The
    property that makes that sound — a cached result is the result the uncached function would
    have returned — is asserted here, because a cache justified only by prose is a cache nobody
    can refute.

    `invocation_corpus` is deliberately absent: it is not memoized, for the reason its own
    docstring records.
    """
    declaration = parse(document, source="test")
    paths = discovery.tracked_paths(ROOT)
    testpaths = tuple(declaration.testpaths)

    assert paths == discovery._tracked_paths_uncached(ROOT)
    assert discovery.source_corpus(ROOT, paths, exclude=testpaths) == (
        discovery._source_corpus_uncached(ROOT, paths, exclude=testpaths)
    )
    assert discovery.test_corpus(ROOT, paths, testpaths) == (
        discovery._test_corpus_uncached(ROOT, paths, testpaths)
    )


def test_a_cached_mapping_cannot_be_aliased_by_its_consumer(document: dict[str, Any]) -> None:
    """Two callers must not share one mutable dict, or one probe's consumer edits another's.

    The scans return `dict`, and a cache handing out the same instance twice would make that
    aliasing possible for the first time. The public functions copy on the way out; this
    measures the copy rather than trusting it.
    """
    paths = discovery.tracked_paths(ROOT)
    testpaths = tuple(parse(document, source="test").testpaths)
    first = discovery.test_corpus(ROOT, paths, testpaths)
    second = discovery.test_corpus(ROOT, paths, testpaths)
    assert first == second
    assert first is not second
    first.clear()
    assert discovery.test_corpus(ROOT, paths, testpaths) == second


# UEC-L-15 — a gate only CI can run is one the standard command cannot see.


def test_the_canonical_lane_population_is_measured_and_is_not_everything(
    live_probe: Probe,
) -> None:
    """A measure returning every engine, or none, is broken rather than satisfied."""
    probe = live_probe
    outside = contract.engines_outside_the_canonical_lane(probe)
    assert 0 < len(outside) < len(probe.engines)


def test_an_engine_invoked_by_nothing_is_not_counted_as_ci_only(live_probe: Probe) -> None:
    """UEC-L-04 owns 'invoked by nothing'. This law owns 'CI can, the lane cannot'.

    Counting the uninvoked here would double-count them and make the two ceilings move
    together, so a single migration would appear to buy two improvements.
    """
    probe = live_probe
    uninvoked = set(contract.engines_with_no_invoker(probe))
    outside = set(contract.engines_outside_the_canonical_lane(probe))
    assert not (uninvoked & outside), "an engine no plane invokes was counted as CI-only"


def test_reachability_counts_the_module_form_not_only_the_path(live_probe: Probe) -> None:
    """verify.sh invokes engines as `-m engine.<package>`, never by gate-file path.

    THE FIRST VERSION OF THIS MEASURE MATCHED PATHS ONLY and reported 42 engines outside
    the lane against a true 41 — a false gap of one, produced by the matcher rather than
    the repository. A detector that cannot spare cannot reach its floor honestly, so both
    forms are pinned here.
    """
    probe = live_probe
    lane = probe.canonical_lane_text()
    assert lane, "the declared canonical entry point did not resolve"
    module_form = [
        artifact
        for artifact in probe.engines
        if probe.reaches_canonical_lane(artifact, lane)
        and artifact.key().split("::", 1)[-1] not in lane
    ]
    assert module_form, (
        "no engine resolved by its module form, so the matcher is path-only and would "
        "report a false gap"
    )


def test_the_law_refuses_when_the_lane_cannot_be_read(live_probe: Probe) -> None:
    """Forge the violation: an unreadable lane must not read as full reachability.

    An entry point that does not resolve means NOTHING is reachable from it, and the law
    must say so rather than silently pass. A measure that treats an absent lane as a clean
    one is the vacuity UEC-L-14 exists to refuse, arriving through a missing file.
    """
    probe = live_probe
    with_ci = [
        artifact
        for artifact in probe.engines
        if any(str(name).startswith(".github/workflows/") for name in probe.invokers(artifact))
    ]
    assert with_ci, "no engine is invoked by a workflow, so this law measures nothing"
    for artifact in with_ci[:5]:
        assert not probe.reaches_canonical_lane(artifact, "")


# UEC-L-16 — a workflow a runner rejects is a plane that does not exist.


BROKEN_SCALAR = """name: x
on: [push]
jobs:
  a:
    runs-on: ubuntu-latest
    steps:
      - name: s
        run: echo "enforcement closure: governed, self-covered, and mutation-resistant"
"""

DANGLING_NEEDS = """name: x
on: [push]
jobs:
  a:
    runs-on: ubuntu-latest
    steps:
      - run: 'true'
  b:
    needs: [a, deleted-job]
    runs-on: ubuntu-latest
    steps:
      - run: 'true'
"""

WELL_FORMED = """name: x
on: [push]
jobs:
  a:
    runs-on: ubuntu-latest
    steps:
      - run: 'echo "one: two"' 
  b:
    needs: [a]
    runs-on: ubuntu-latest
    steps:
      - run: 'true'
"""


def test_l16_catches_the_two_shapes_that_actually_broke_this_repository() -> None:
    """Both fixtures are the real defects, reduced. Neither is invented.

    The first is uec-gate.yml's unquoted scalar, which no parser accepts and which meant
    UEC-000001 had never run in CI. The second is urke-gate.yml's dangling needs after
    an edit deleted the job it depended on — that file PARSED, so a parse check alone would
    have passed it.
    """
    assert contract._workflow_defects("w", BROKEN_SCALAR)
    assert contract._workflow_defects("w", DANGLING_NEEDS)


def test_l16_spares_a_quoted_colon_and_a_resolved_need() -> None:
    """It must spare, or its floor of zero is unreachable except by deleting workflows.

    run: echo "one: two" is a QUOTED scalar and legal; a needs naming a declared
    job is the ordinary case. A detector that cannot spare these would refuse most of the
    repository's real workflows.
    """
    assert contract._workflow_defects("w", WELL_FORMED) == []


def test_l16_the_live_workflow_set_is_measured_and_clean(live_probe: Probe) -> None:
    """And the measurement reaches the real population rather than an empty one."""
    probe = live_probe
    workflows = [a for a in probe.artifacts if a.identity.startswith(".github/workflows/")]
    assert len(workflows) > 30, "the workflow population was not discovered"
    assert contract.workflows_that_cannot_run(probe) == []


# ---------------------------------------------------------------------------
# the declaration reader's own refusals
#
# Every one of these is a shape the reader must FAULT on rather than absorb. A section
# absorbed at the wrong type does not stay wrong quietly: `_rows` over a string iterates
# its characters, and every later check then quantifies over single letters and passes.


def test_the_module_entry_point_reaches_the_gate() -> None:
    """``python -m engine.enforcement_closure`` is a second invocation plane, and UEC-L-06
    requires two. A dispatcher that stopped importing its gate would fail at run time in CI
    rather than here."""

    module = importlib.import_module("engine.enforcement_closure.__main__")
    assert module.main is gate.main


def test_a_discovery_rule_with_no_identity_is_refused() -> None:
    """The model refuses it as well as the reader. A rule with no id cannot be named by a
    governed entry, so nothing could ever be attributed to it."""

    with pytest.raises(DeclarationError, match="needs a rule_id"):
        Rule(rule_id="", kind="gate", strategy="glob", floor=1)


def test_a_declaration_that_is_not_an_object_is_refused() -> None:
    with pytest.raises(DeclarationError, match="must be a JSON object"):
        parse(["not", "an", "object"], source="test")  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("mutate", "message"),
    [
        (
            lambda d: d.__setitem__("discovery_rules", "a string where a list belongs"),
            "must be a non-empty list",
        ),
        (
            lambda d: d.__setitem__("discovery_rules", ["not a mapping"]),
            "must be an object",
        ),
        (
            lambda d: d["discovery_rules"].append(copy.deepcopy(d["discovery_rules"][0])),
            "share a rule_id",
        ),
        (lambda d: d.__setitem__("withdrawals", ["not an object"]), "must be an object"),
        (lambda d: d["withdrawals"].__setitem__("cap", "many"), "non-negative integer"),
        (lambda d: d["withdrawals"].__setitem__("cap", -1), "non-negative integer"),
        (
            lambda d: d["withdrawals"].__setitem__("entries", "a string"),
            "'withdrawals.entries' must be a list",
        ),
        (lambda d: d["laws"].append(copy.deepcopy(d["laws"][0])), "share a law_id"),
        (lambda d: d.__setitem__("ratchet", ["not an object"]), "'ratchet' must be an object"),
        (
            lambda d: d["ratchet"].__setitem__("a_ceiling", -1),
            "must be a non-negative integer",
        ),
        (
            lambda d: d.__setitem__("testpaths", "engine/tests"),
            "must be a list of strings",
        ),
        (lambda d: d.__setitem__("testpaths", ["   "]), "must be a non-empty string"),
    ],
    ids=[
        "rules-not-a-list",
        "rule-row-not-an-object",
        "duplicate-rule-id",
        "withdrawals-not-an-object",
        "cap-not-an-integer",
        "cap-negative",
        "entries-not-a-list",
        "duplicate-law-id",
        "ratchet-not-an-object",
        "ratchet-value-negative",
        "testpaths-not-a-list",
        "testpaths-entry-empty",
    ],
)
def test_the_reader_refuses_every_malformed_section(
    document: dict[str, Any], mutate: Callable[[dict[str, Any]], None], message: str
) -> None:
    forged = copy.deepcopy(document)
    mutate(forged)
    with pytest.raises(DeclarationError, match=message):
        parse(forged, source="test")


def test_a_governed_entry_naming_a_kind_no_rule_locates_is_refused(
    document: dict[str, Any],
) -> None:
    """The rule_id and the kind are two independent bindings. An entry naming a declared rule
    under a kind nothing locates would be governed by a discovery that can never find it."""
    forged = copy.deepcopy(document)
    forged["governed_enforcement"][0]["kind"] = "a-kind-no-rule-locates"
    with pytest.raises(DeclarationError, match="which no discovery rule locates"):
        parse(forged, source="test")


def test_a_declared_rule_resolves_by_id_and_an_undeclared_one_refuses(
    document: dict[str, Any],
) -> None:
    """Both halves of the accessor. The refusal is what stops a governed entry from silently
    naming nothing; the resolution is what every caller depends on."""
    declaration = parse(copy.deepcopy(document), source="test")
    first = declaration.rules[0]
    assert declaration.rule(first.rule_id) is first
    with pytest.raises(DeclarationError, match="no discovery rule"):
        declaration.rule("a-rule-nobody-declared")


# ---------------------------------------------------------------------------
# discovery: the substrate reader, and the shapes a healthy tree never presents


def test_a_substrate_that_does_not_resolve_is_a_fault(tmp_path: Path) -> None:
    """A missing substrate is a FAULT and never an empty population: an unread Makefile would
    locate no target, and no target is what a repository with nothing to enforce looks like."""
    with pytest.raises(EnforcementError, match="does not resolve"):
        discovery.read_text(str(tmp_path), "a-file-nobody-wrote")


def test_a_target_declared_twice_is_located_once(tmp_path: Path) -> None:
    """`make help` echoes every target name, and a target may be defined twice. Two artifacts
    under one identity would make every per-artifact law count the same thing twice."""

    (tmp_path / "Makefile").write_text(
        "uec-gate:\n\t@echo first\n\nuec-gate:\n\t@echo second\n", encoding="utf-8"
    )
    rule = Rule(
        rule_id="r", kind="make_target", strategy="make_targets", floor=1, pattern=r"uec-.*"
    )
    located = discovery.locate_make_targets(rule, str(tmp_path))
    assert [artifact.identity for artifact in located] == ["uec-gate"]
    assert "first" in located[0].detail["recipe"], "the first definition is the one make honours"


def test_a_module_that_will_not_parse_contributes_no_evidence() -> None:
    """It contributes nothing rather than contributing its comments. A raw-text fallback would
    let a docstring naming an engine count as something loading it, which is the exact defect
    this detector exists to refuse."""
    assert discovery.source_evidence("def (:::\n") == ""
    assert discovery.refusal_shapes("def (:::\n", **_WITNESS) == frozenset()


def test_a_module_with_no_body_contributes_no_docstring() -> None:
    """An empty module has no first statement to read as a docstring, and indexing one would
    take the whole corpus scan down on the first empty ``__init__.py``."""
    assert discovery.source_evidence("") == ""


def test_an_index_entry_with_no_working_tree_file_is_skipped(tmp_path: Path) -> None:
    """A tracked path with no file is an ordinary state — a deletion staged, or a checkout in
    progress — and reading it would turn the corpus scan into a fault over a working tree that
    is merely mid-edit."""
    discovery.clear_caches()
    absent = ("engine/a-module-no-checkout-carries.py",)
    assert discovery.source_corpus(str(tmp_path), absent) == {}
    assert discovery.test_corpus(str(tmp_path), absent, ("engine/",)) == {}


def test_the_memoized_scans_can_be_dropped_for_a_caller_that_changes_the_tree() -> None:
    """The scans are memoized per root, so a caller that mutates the tree in-process would keep
    reading the pre-mutation answer. Clearing is what makes an in-process worktree test honest."""
    discovery.clear_caches()
    assert discovery.tracked_paths(ROOT), "the tracked population is empty after clearing"


# ---------------------------------------------------------------------------
# the laws' remaining refusals, and the probe's own edges


@pytest.fixture(scope="module", name="probe")
def _live_probe(document: dict[str, Any]) -> Probe:
    return Probe(parse(copy.deepcopy(document), source="test"), repository=ROOT)


def test_an_unreadable_canonical_entry_point_reads_as_empty_rather_than_faulting(
    document: dict[str, Any],
) -> None:
    """The lane's path comes from the declaration, so a repository that renames its entry point
    says so there. A rename this reader could not follow must produce an empty lane — under
    which UEC-L-15 refuses every engine — rather than an exception that takes the gate down."""
    forged = copy.deepcopy(document)
    forged["programme"] = {"canonical_entry_point": "an-entry-point-nobody-wrote.sh"}
    assert Probe(parse(forged, source="test"), repository=ROOT).canonical_lane_text() == ""


def test_an_artifact_whose_identity_is_not_a_path_has_no_module_form(probe: Probe) -> None:
    """A make target's identity is a target name, not a path, so there is no `package.module`
    to look for in the lane. Splitting one anyway would compare the lane against a package
    named after half a target."""

    artifact = Artifact(identity="uec-probe-target", kind=KIND_MAKE_TARGET, rule_id="probe")
    probe._invokers[artifact.key()] = ()
    assert probe.reaches_canonical_lane(artifact, "a lane that names nothing") is False


def test_a_witness_declaring_no_accepted_shape_refuses_every_engine(
    document: dict[str, Any],
) -> None:
    """The accepted shapes are the whole vocabulary of the law. With none declared, no test
    could ever witness a refusal — so the honest answer is that every engine is unwitnessed,
    not that the law holds."""
    forged = copy.deepcopy(document)
    forged["refusal_witness"]["accepted_shapes"] = []
    findings = _run(forged, "every_engine_is_witnessed_refusing")
    assert findings, "an empty witness vocabulary reported no unwitnessed engine"


def test_a_declaration_no_package_digests_is_reported(probe: Probe, monkeypatch) -> None:
    """Three markers, because the repository mints digests three ways. A law recognising one of
    them would report a false absence for two thirds of the surface — which is why the markers
    are the thing under test rather than the law's arithmetic."""
    monkeypatch.setattr(contract, "DIGEST_MARKERS", ("a-marker-no-module-carries",))
    assert contract.declarations_without_a_certification_identity(probe)


def test_a_workflow_file_that_reads_as_empty_is_skipped(probe: Probe, monkeypatch) -> None:
    """An empty read is not a defect-free workflow: it is a workflow nobody read. Reporting it
    as clean and reporting it as broken are both wrong, so it contributes nothing and the
    population laws above account for its absence."""
    monkeypatch.setattr(discovery, "read_text", lambda root, relative: "")
    assert contract.workflows_that_cannot_run(probe) == []


def test_a_needs_list_with_a_trailing_separator_names_no_extra_job() -> None:
    """`needs: [a, ]` splits to a name and an empty string. An empty dependency compared against
    the declared jobs would report every well-formed workflow as depending on a job called ""."""
    workflow = (
        "on: push\njobs:\n"
        "  a:\n    runs-on: ubuntu-latest\n    steps:\n      - run: 'true'\n"
        "  b:\n    needs: [a, ]\n    runs-on: ubuntu-latest\n    steps:\n      - run: 'true'\n"
    )
    assert contract._workflow_defects("w", workflow) == []


def test_an_empty_enforcement_plane_is_refused(probe: Probe) -> None:
    """Every law below UEC-L-01 quantifies over the located population. Over an empty one they
    all hold, which is the vacuity the whole programme exists to refuse."""
    hollow = copy.copy(probe)
    hollow.artifacts = ()
    hollow.located = {}
    findings = contract.discovery_rules_are_non_vacuous(hollow)
    assert any("the enforcement plane is empty" in f for f in findings)


def test_an_artifact_both_governed_and_withdrawn_is_refused(document: dict[str, Any]) -> None:
    """Withdrawal releases an artifact from the inventory. An entry that is both required and
    released leaves the reader no way to decide whether its absence is a defect."""
    forged = copy.deepcopy(document)
    row = copy.deepcopy(forged["governed_enforcement"][0])
    row["identity"] = "engine/enforcement_closure/a-file-nobody-wrote.py"
    forged["governed_enforcement"].append(row)
    forged["withdrawals"]["cap"] = max(2, forged["withdrawals"].get("cap", 0))
    forged["withdrawals"]["entries"].append(
        {
            "identity": row["identity"],
            "kind": row["kind"],
            "reason": "a withdrawal declared for an artifact the inventory still requires",
            "owner": "test",
            "date": "2026-09-09",
        }
    )
    findings = _run(forged, "declared_enforcement_exists")
    assert any("both governed and withdrawn" in f for f in findings)


def test_a_package_exposing_no_uniform_parse_is_counted_rather_than_faulted(
    probe: Probe, monkeypatch
) -> None:
    """A package with no `declaration.parse` does not expose the uniform interface, which is a
    measured fact reported by the ratchet. Nothing is logged, because a log line is an output
    and an output varying with the import environment would make two measurements differ."""

    monkeypatch.setattr(
        contract.importlib, "import_module", lambda name: types.ModuleType("hollow")
    )
    assert contract._uniform_identity_owners(probe) == {}


def test_a_mutation_the_declaration_refuses_is_a_killed_mutant_not_a_finding(
    probe: Probe, monkeypatch
) -> None:
    """A declaration that REFUSES the edit at parse is a declaration that edit cannot silently
    pass through — the property under test. The failure this law reports is the opposite case:
    an edit that parsed cleanly and left the identity where it was."""

    def _refusing(document: dict[str, Any]) -> None:
        raise DeclarationError("this edit is refused at parse")

    monkeypatch.setattr(
        contract, "IDENTITY_MUTATIONS", {"refused": (lambda document: True, _refusing)}
    )
    monkeypatch.setattr(contract, "IDENTITY_MUTATION_FLOOR", 1)
    assert contract.certification_identity_is_complete(probe) == []


def test_a_declaration_no_meaningful_edit_reaches_is_refused(probe: Probe, monkeypatch) -> None:
    """Below the floor the law holds by describing nothing: no semantic mutation applied, so its
    identity was never shown to move under ANY edit that changes what it means."""
    monkeypatch.setattr(
        contract, "IDENTITY_MUTATIONS", {"absent": (lambda document: False, lambda d: None)}
    )
    findings = contract.certification_identity_is_complete(probe)
    assert any("below the floor" in f for f in findings)


def test_uec_own_artifact_that_its_rules_do_not_locate_is_refused(
    document: dict[str, Any],
) -> None:
    """A closure mechanism outside its own closure is the D-09 defect, named and made
    executable: UEC lists itself, and refuses if its own rules cannot find what it listed."""
    forged = copy.deepcopy(document)
    entry = copy.deepcopy(forged["self_coverage"]["artifacts"][0])
    entry["identity"] = "MAKE-TARGET-UEC-NEVER-DECLARED"
    entry["kind"] = "MAKE_GATE_TARGET"
    forged["self_coverage"]["artifacts"].append(entry)
    findings = _run(forged, "self_coverage_is_a_fixed_point")
    assert any("not located by UEC's own discovery rules" in f for f in findings)


def test_uec_own_gate_without_a_test_or_two_planes_is_refused(probe: Probe) -> None:
    """The registrar must satisfy the laws it applies to everything else, and both of its own
    obligations are measured by removing the evidence for them rather than by assertion."""
    hollow = copy.copy(probe)
    hollow._tests = dict.fromkeys(probe._tests, ())
    hollow._invokers = dict.fromkeys(probe._invokers, ())
    findings = contract.self_coverage_is_a_fixed_point(hollow)
    assert any("has no test binding" in f for f in findings)
    assert any("fewer than two invocation planes" in f for f in findings)


def test_a_ratchet_key_nobody_declared_is_skipped_rather_than_read_as_zero(
    document: dict[str, Any],
) -> None:
    """A ceiling of zero and no ceiling at all are different. Reading an absent key as zero would
    make every measured violation an assurance reduction on a law nobody has ratcheted yet."""
    forged = copy.deepcopy(document)
    for key in list(contract.RATCHETED):
        forged["ratchet"].pop(key, None)
    assert _run(forged, "no_assurance_reduction") == []
