"""UVI-000001 — the Universal Verification Intelligence, measured.

What these tests are for
------------------------
A verification selector's dangerous failure is not slowness. It is a green run that
skipped the affected test, because the symptom of that is indistinguishable from
success. So the tests below are weighted toward the refusals rather than the happy path:
every one of them is a way the intelligence could make a run report more than it
measured, pinned so it fails here instead of shipping as a faster green run.

The four that matter most:

* :func:`test_an_unbounded_change_always_widens` — the fail-wide asymmetry, over every
  class of change no graph in this repository can bound.
* :func:`test_a_partition_never_loses_a_test_object` — topology neutrality at every
  worker count, including the split-file case where a unit is a node rather than a file.
* :func:`test_a_certification_mode_can_never_reach_a_reuse_decision` — a certification
  that reuses a result certifies a cache.
* :func:`test_the_baseline_contract_is_a_ratchet` — every gate the certification default
  ran before this rework is still declared and still admitted by every certifying mode.
"""

from __future__ import annotations

import dataclasses
import io
import itertools
import json
import os
import re
import runpy
import stat
import subprocess
import sys
import textwrap
from dataclasses import replace

import pytest

from engine.certification_integrity import immutable
from engine.universal_discovery import discovery as discovery_module
from engine.universal_discovery.discovery import clear_derived_scope_cache
from engine.verification_impact.graph import ImpactError
from engine.verification_intelligence import cli, evidence
from engine.verification_intelligence import execution as execution_module
from engine.verification_intelligence import gate as uvi_gate
from engine.verification_intelligence import plan as plan_module
from engine.verification_intelligence import registry as registry_module
from engine.verification_intelligence import selection as selection_module
from engine.verification_intelligence.cli import main
from engine.verification_intelligence.constitution import (
    COST_MODEL,
    execution_contract,
    load_constitution,
    load_declaration,
    repo_root,
    verify_source,
)
from engine.verification_intelligence.evidence import (
    EVIDENCE_VERSION,
    WHOLE_BOUNDARY,
    decide,
    input_digest,
    lookup,
    record,
    resolve_prefix,
)
from engine.verification_intelligence.execution import (
    FALLBACK_SHARD_MEMORY_BUDGET_MB,
    _combine_and_evaluate,
    _export_shard_data,
    _shard_argv,
    assert_topology_neutral,
    combine_shards,
    concurrency_limit,
    memory_headroom_bytes,
    plan_shards,
    resolve_workers,
    run_tests,
    shard_indices_present,
    shard_memory_budget_bytes,
    split_currency,
    unit_file,
)
from engine.verification_intelligence.gate import (
    every_declared_read_set_resolves,
    every_stage_declares_a_read_set,
)
from engine.verification_intelligence.model import (
    Action,
    Coverage,
    Selection,
    SelectionResult,
    Shard,
    VerificationIntelligenceError,
)
from engine.verification_intelligence.plan import (
    build_plan,
    evidence_home,
    plan_digest,
    plan_json,
    plan_tsv,
)
from engine.verification_intelligence.registry import (
    CAPABILITY_CATALOG,
    DEFAULT_COST_SECONDS,
    EXECUTABLE_REGISTRY,
    RELATIONSHIP_GRAPH,
    UNIVERSAL_REGISTRY,
    TestObjectRegistry,
    build_test_registry,
    collection_roots,
    is_collectible,
    load_cost_model,
    load_substrates,
)
from engine.verification_intelligence.selection import (
    SELF_PREFIXES,
    UNBOUNDED_PREFIXES,
    _capability_location,
    _test_mirror,
    select,
    stages_reading,
    unbounded_prefixes,
)

REPO = repo_root()


@pytest.fixture(scope="module")
def substrates():
    return load_substrates()


@pytest.fixture(scope="module")
def tests_registry(substrates):
    return build_test_registry(substrates)


@pytest.fixture(scope="module")
def constitution():
    return load_constitution(checks=frozenset(uvi_gate.CHECKS))


# --- the constitution ---------------------------------------------------------------


def test_the_declaration_constructs_and_binds_every_law_to_a_check(constitution) -> None:
    """A law naming a check nothing implements would be governance by assertion."""
    assert constitution.artifact_id == "UVI-000001"
    assert {law.check for law in constitution.laws} == set(uvi_gate.CHECKS)


def test_a_law_naming_a_missing_check_refuses_to_construct(tmp_path) -> None:
    document = load_declaration()
    document["laws"].append(
        {"id": "X", "title": "t", "statement": "s", "check": "no_such_check_exists"}
    )
    path = tmp_path / "declaration.json"
    path.write_text(json.dumps(document), encoding="utf-8")
    with pytest.raises(VerificationIntelligenceError, match="not implemented"):
        load_constitution(str(path), checks=frozenset(uvi_gate.CHECKS))


def test_a_reusable_stage_with_no_declared_inputs_refuses_to_construct(tmp_path) -> None:
    """A cache key covering nothing is a permanent false hit, so it is refused up front."""
    document = load_declaration()
    for stage in document["stage_registry"]["stages"]:
        stage["reusable"] = True
        stage.pop("reuse_inputs", None)
    path = tmp_path / "declaration.json"
    path.write_text(json.dumps(document), encoding="utf-8")
    with pytest.raises(VerificationIntelligenceError, match="reuse_inputs"):
        load_constitution(str(path))


def test_two_stages_may_not_share_one_label(tmp_path) -> None:
    """The label is the join key to verify.sh and to the canonical validation record."""
    document = load_declaration()
    stages = document["stage_registry"]["stages"]
    stages[1]["label"] = stages[0]["label"]
    path = tmp_path / "declaration.json"
    path.write_text(json.dumps(document), encoding="utf-8")
    with pytest.raises(VerificationIntelligenceError, match="label"):
        load_constitution(str(path))


def test_a_mode_listing_an_undeclared_stage_is_refused(tmp_path, constitution) -> None:
    document = load_declaration()
    for mode in document["mode_constitution"]["modes"]:
        mode["stages"] = ["a-stage-that-does-not-exist"]
    path = tmp_path / "declaration.json"
    path.write_text(json.dumps(document), encoding="utf-8")
    broken = load_constitution(str(path))
    with pytest.raises(VerificationIntelligenceError, match="undeclared stage"):
        broken.stages_for(broken.mode("fast"))


def test_an_absent_declaration_is_a_fault_and_not_a_default(tmp_path) -> None:
    """There is deliberately no fallback constitution; one would be a second constitution."""
    with pytest.raises(VerificationIntelligenceError, match="unreadable"):
        load_constitution(str(tmp_path / "absent.json"))


def test_every_certification_mode_runs_the_whole_suite_under_the_floor(constitution) -> None:
    for mode in constitution.modes:
        if mode.certification_eligible:
            assert mode.selection is Selection.WHOLE_SUITE
            assert mode.coverage is Coverage.FLOOR_90
            assert not mode.evidence_reuse
        else:
            assert mode.claims_not, f"--{mode.mode_id} states nothing it does not claim"


# --- the Test Object Registry -------------------------------------------------------


def test_the_registry_projects_exactly_what_pytest_collects(tests_registry) -> None:
    roots = collection_roots()
    for path in tests_registry.paths:
        assert is_collectible(path, roots)
    assert tests_registry.objects, "the projection is empty"


def test_a_test_object_that_pytest_would_not_collect_is_not_selectable() -> None:
    roots = ("engine/tests",)
    assert is_collectible("engine/tests/unit/test_x.py", roots)
    assert not is_collectible("engine/tests/unit/helpers.py", roots)
    assert not is_collectible("engine/tests/unit/__init__.py", roots)
    assert not is_collectible("platform/tests/test_x.py", roots)
    assert not is_collectible("engine/tests/unit/test_x.txt", roots)


def test_an_unmeasured_object_is_over_priced_rather_than_assumed_cheap(tests_registry) -> None:
    """Under-pricing an unknown packs it into a shard the whole run then waits on."""

    assert tests_registry.cost_of("engine/tests/unit/a_file_nobody_measured.py") == (
        DEFAULT_COST_SECONDS
    )


# --- selection ----------------------------------------------------------------------


@pytest.mark.parametrize(
    ("description", "path"),
    [
        ("a registry or declaration with no import edges", "00-BOOK/DATA/uvi-probe.json"),
        ("a file type carrying no edges at all", "docs/uvi-probe.md"),
        ("a Python file absent from the executable registry", "engine/uvi_probe.py"),
        ("the selector's own substrate", "00-MASTER/UCOS-UGA-001/uvi-probe.py"),
        ("the build contract", "pyproject.toml"),
    ],
)
def test_an_unbounded_change_always_widens(description, path, substrates, tests_registry) -> None:
    """THE asymmetry. Every path no graph can bound runs the whole suite, and says why."""
    result = select((path,), substrates=substrates, tests=tests_registry)
    assert result.selection is Selection.WHOLE_SUITE, description
    assert result.test_paths == tests_registry.paths
    assert result.escalations, "it widened without naming a reason"


def test_a_bounded_change_selects_a_proper_subset(substrates, tests_registry) -> None:
    """A change with resolvable edges must not run everything, or selection is theatre."""
    result = select(("engine/uaue/gate.py",), substrates=substrates, tests=tests_registry)
    assert result.selection is Selection.IMPACT
    assert 0 < len(result.test_paths) < len(tests_registry.paths)
    assert not result.escalations


def test_the_selection_reaches_the_test_that_imports_the_change(substrates, tests_registry) -> None:
    result = select(("engine/uaue/gate.py",), substrates=substrates, tests=tests_registry)
    assert "engine/tests/unit/test_uaue_controller.py" in result.test_paths


def test_every_declared_substrate_layer_is_reported(substrates, tests_registry) -> None:
    """A layer that runs but reports nothing cannot be audited for over- or under-reach."""
    result = select(("engine/uaue/gate.py",), substrates=substrates, tests=tests_registry)
    assert [name for name, _ in result.layers] == [
        "IDENTITY",
        "DEPENDENCY",
        "OWNERSHIP",
        "CAPABILITY",
        "RELATIONSHIP",
    ]


def test_no_change_selects_nothing_and_claims_nothing(substrates, tests_registry) -> None:
    result = select((), substrates=substrates, tests=tests_registry)
    assert result.test_paths == ()
    assert result.selection is Selection.IMPACT


def test_a_change_to_the_selector_itself_escalates(substrates, tests_registry) -> None:
    """Self-application: the selector cannot be verified by asking it what to verify."""
    result = select(
        ("engine/verification_intelligence/selection.py",),
        substrates=substrates,
        tests=tests_registry,
    )
    assert result.selection is Selection.WHOLE_SUITE
    assert any("selector" in reason for reason in result.escalations)


# --- sharding and topology ----------------------------------------------------------


@pytest.mark.parametrize("workers", [1, 2, 3, 5, 12, 64])
def test_a_partition_never_loses_a_test_object(workers, tests_registry) -> None:
    """The failure that could turn a green run into a false one, at every worker count."""
    units = tests_registry.units_for(tests_registry.paths)
    shards = plan_shards(units, tests_registry, workers)
    placed = [unit for shard in shards for unit in shard.test_paths]
    assert len(placed) == len(set(placed)), "a unit was placed twice"
    assert sorted({unit_file(unit) for unit in placed}) == sorted(tests_registry.paths)


def test_partitioning_twice_produces_identical_shards(tests_registry) -> None:
    units = tests_registry.units_for(tests_registry.paths)
    first = plan_shards(units, tests_registry, 7)
    second = plan_shards(units, tests_registry, 7)
    assert [shard.test_paths for shard in first] == [shard.test_paths for shard in second]


def test_an_oversized_test_object_is_split_into_its_nodes(tests_registry) -> None:
    """One file was 46% of the whole suite; no shard count can finish sooner than that."""
    if not tests_registry.splittable:
        pytest.skip("no measured object exceeds the declared split threshold")
    split = sorted(tests_registry.splittable)[0]
    units = tests_registry.units_for((split,))
    assert len(units) > 1
    assert all(unit.startswith(f"{split}::") for unit in units)
    assert all(unit_file(unit) == split for unit in units)


def test_a_partition_that_splits_a_file_without_a_remainder_shard_is_refused() -> None:
    """Nodes in one shard and no remainder means the file's unmeasured tests run nowhere."""
    shards = (
        Shard(index=0, test_paths=("a/test_x.py::test_one",), cost_seconds=1.0),
        Shard(index=1, test_paths=("a/test_y.py",), cost_seconds=1.0),
    )
    with pytest.raises(VerificationIntelligenceError, match="would run twice"):
        assert_topology_neutral(shards, ("a/test_x.py", "a/test_y.py"))


def test_a_partition_whose_deselects_do_not_match_its_nodes_is_refused() -> None:
    """A node both deselected and unplaced runs nowhere; one placed twice runs twice."""
    shards = (
        Shard(index=0, test_paths=("a/test_x.py",), cost_seconds=1.0, deselect=("a/test_x.py::b",)),
        Shard(index=1, test_paths=("a/test_x.py::c",), cost_seconds=1.0),
    )
    with pytest.raises(VerificationIntelligenceError, match="run nowhere"):
        assert_topology_neutral(shards, ("a/test_x.py",))


def test_a_split_file_with_a_remainder_shard_is_accepted() -> None:
    """The legitimate shape: one shard holds the file minus exactly what the others took."""
    shards = (
        Shard(
            index=0,
            test_paths=("a/test_x.py",),
            cost_seconds=1.0,
            deselect=("a/test_x.py::two",),
        ),
        Shard(index=1, test_paths=("a/test_x.py::two",), cost_seconds=1.0),
    )
    assert_topology_neutral(shards, ("a/test_x.py",))


def test_a_partition_that_drops_a_test_object_is_refused() -> None:
    shards = (Shard(index=0, test_paths=("a/test_x.py",), cost_seconds=1.0),)
    with pytest.raises(VerificationIntelligenceError, match="missing"):
        assert_topology_neutral(shards, ("a/test_x.py", "a/test_y.py"))


def test_a_partition_that_duplicates_a_unit_is_refused() -> None:
    shards = (
        Shard(index=0, test_paths=("a/test_x.py",), cost_seconds=1.0),
        Shard(index=1, test_paths=("a/test_x.py",), cost_seconds=1.0),
    )
    with pytest.raises(VerificationIntelligenceError, match="more than once"):
        assert_topology_neutral(shards, ("a/test_x.py",))


def test_worker_resolution_never_exceeds_the_work_or_the_ceiling() -> None:
    assert resolve_workers(3, max_workers=12) <= 3
    assert resolve_workers(1000, max_workers=4) == 4
    assert resolve_workers(0, max_workers=4) == 1
    assert resolve_workers(1000, max_workers=4, override="2") == 2
    with pytest.raises(VerificationIntelligenceError):
        resolve_workers(10, max_workers=4, override="not-a-number")
    with pytest.raises(VerificationIntelligenceError):
        resolve_workers(10, max_workers=4, override="0")


def test_a_shard_plan_with_no_workers_is_refused(tests_registry) -> None:
    with pytest.raises(VerificationIntelligenceError, match="at least one worker"):
        plan_shards(tests_registry.paths, tests_registry, 0)


# --- execution concurrency ----------------------------------------------------------
#
# The planner may not read these, and that separation is the whole point: UVI-L-10 binds
# the PLAN to byte-identical reproduction, while UVI-L-08 says the schedule changes no
# obligation. So headroom — which moves between two reads — may bound execution and may
# never reach a plan.


def test_the_declared_shard_budget_is_read_from_the_declaration() -> None:
    assert shard_memory_budget_bytes() == 1536 * 1024 * 1024


@pytest.mark.parametrize(
    "document",
    [
        "{ not json",
        json.dumps({"execution": {}}),
        json.dumps({"execution": {"test_sharding": {"shard_memory_budget_mb": 0}}}),
        json.dumps({"execution": {"test_sharding": {"shard_memory_budget_mb": True}}}),
        json.dumps({"execution": {"test_sharding": {"shard_memory_budget_mb": "big"}}}),
    ],
)
def test_an_unreadable_budget_falls_back_rather_than_removing_the_bound(tmp_path, document) -> None:
    """A bound nobody can read is still better than no bound at all."""
    target = tmp_path / "00-MASTER" / "UVI-000001"
    target.mkdir(parents=True)
    (target / "uvi-declaration.json").write_text(document, encoding="utf-8")
    budget = shard_memory_budget_bytes(root=str(tmp_path))
    assert budget == FALLBACK_SHARD_MEMORY_BUDGET_MB * 1024 * 1024


def test_a_missing_declaration_falls_back(tmp_path) -> None:
    assert shard_memory_budget_bytes(root=str(tmp_path)) > 0


def test_concurrency_is_pinned_by_the_environment(monkeypatch) -> None:
    monkeypatch.setenv("UVI_CONCURRENCY", "3")
    assert concurrency_limit(12) == 3
    assert concurrency_limit(2) == 2, "the pin never exceeds the wave"
    assert concurrency_limit(0) == 1


@pytest.mark.parametrize("value", ["not-a-number", "0", "-4"])
def test_a_malformed_concurrency_pin_is_refused(monkeypatch, value) -> None:
    monkeypatch.setenv("UVI_CONCURRENCY", value)
    with pytest.raises(VerificationIntelligenceError):
        concurrency_limit(8)


def test_unknown_headroom_leaves_the_wave_unbounded(monkeypatch) -> None:
    """None means UNKNOWN, never `none available` — a healthy host is not serialised."""
    monkeypatch.delenv("UVI_CONCURRENCY", raising=False)
    monkeypatch.setattr(execution_module, "memory_headroom_bytes", lambda: None)
    assert concurrency_limit(12) == 12


def test_headroom_bounds_the_wave_and_never_reaches_zero(monkeypatch) -> None:
    monkeypatch.delenv("UVI_CONCURRENCY", raising=False)
    monkeypatch.setattr(execution_module, "shard_memory_budget_bytes", lambda root=None: 1024)
    monkeypatch.setattr(execution_module, "memory_headroom_bytes", lambda: 4096)
    assert concurrency_limit(12) == 4
    monkeypatch.setattr(execution_module, "memory_headroom_bytes", lambda: 0)
    assert concurrency_limit(12) == 1, "a host too small for one shard still runs them in turn"


def test_headroom_is_read_on_this_host_or_reported_unknown() -> None:
    headroom = memory_headroom_bytes()
    assert headroom is None or headroom >= 0


def test_linux_headroom_is_read_from_meminfo(monkeypatch, tmp_path) -> None:
    meminfo = tmp_path / "meminfo"
    meminfo.write_text("MemTotal: 100 kB\nMemAvailable: 2048 kB\n", encoding="utf-8")
    monkeypatch.setattr(execution_module.sys, "platform", "linux")
    real_open = open
    monkeypatch.setattr(
        "builtins.open",
        lambda path, *a, **k: real_open(meminfo if path == "/proc/meminfo" else path, *a, **k),
    )
    assert memory_headroom_bytes() == 2048 * 1024


def test_linux_headroom_without_the_field_is_unknown(monkeypatch, tmp_path) -> None:
    meminfo = tmp_path / "meminfo"
    meminfo.write_text("MemTotal: 100 kB\n", encoding="utf-8")
    monkeypatch.setattr(execution_module.sys, "platform", "linux")
    real_open = open
    monkeypatch.setattr(
        "builtins.open",
        lambda path, *a, **k: real_open(meminfo if path == "/proc/meminfo" else path, *a, **k),
    )
    assert memory_headroom_bytes() is None


def test_linux_headroom_that_cannot_be_read_is_unknown(monkeypatch) -> None:
    monkeypatch.setattr(execution_module.sys, "platform", "linux")
    monkeypatch.setattr(
        "builtins.open", lambda *a, **k: (_ for _ in ()).throw(OSError("no /proc here"))
    )
    assert memory_headroom_bytes() is None


def test_darwin_headroom_counts_reclaimable_pages(monkeypatch) -> None:
    """Free alone understates a warm machine badly, so inactive and speculative count."""
    stdout = (
        "Mach Virtual Memory Statistics: (page size of 4096 bytes)\n"
        "Pages free:                     100.\n"
        "Pages inactive:                 200.\n"
        "Pages speculative:               50.\n"
        "Pages wired down:              9999.\n"
    )
    monkeypatch.setattr(execution_module.sys, "platform", "darwin")
    monkeypatch.setattr(
        execution_module.subprocess,
        "run",
        lambda *a, **k: subprocess.CompletedProcess([], 0, stdout=stdout),
    )
    assert memory_headroom_bytes() == 350 * 4096


def test_darwin_headroom_is_unknown_when_vm_stat_fails(monkeypatch) -> None:
    monkeypatch.setattr(execution_module.sys, "platform", "darwin")
    monkeypatch.setattr(
        execution_module.subprocess,
        "run",
        lambda *a, **k: subprocess.CompletedProcess([], 1, stdout=""),
    )
    assert memory_headroom_bytes() is None


def test_darwin_headroom_is_unknown_when_vm_stat_is_absent(monkeypatch) -> None:
    monkeypatch.setattr(execution_module.sys, "platform", "darwin")
    monkeypatch.setattr(
        execution_module.subprocess,
        "run",
        lambda *a, **k: (_ for _ in ()).throw(OSError("no vm_stat")),
    )
    assert memory_headroom_bytes() is None


def test_an_unrecognised_platform_reports_unknown(monkeypatch) -> None:
    monkeypatch.setattr(execution_module.sys, "platform", "sunos5")
    assert memory_headroom_bytes() is None


# --- evidence -----------------------------------------------------------------------


def test_a_certification_mode_can_never_reach_a_reuse_decision(
    constitution, substrates, tmp_path
) -> None:
    """A certification that reuses a result certifies a cache."""
    for mode in constitution.modes:
        if not mode.certification_eligible:
            continue
        for stage in constitution.stages_for(mode):
            reuse, reason, digest = decide(mode, stage, substrates, home=str(tmp_path))
            assert reuse is False
            assert digest is None
            assert "never reuses" in reason


def test_a_recorded_pass_is_reused_and_a_changed_input_is_not(
    constitution, substrates, tmp_path
) -> None:
    mode = constitution.mode("change")
    stage = next(s for s in constitution.stages_for(mode) if s.reusable)
    digest = input_digest(stage, substrates, contract=execution_contract(stage.label))
    assert digest is not None

    reuse, _, _ = decide(mode, stage, substrates, home=str(tmp_path))
    assert reuse is False, "an empty store must not be a hit"

    record(str(tmp_path), stage.stage_id, digest, "PASS")
    reuse, reason, hit = decide(mode, stage, substrates, home=str(tmp_path))
    assert reuse is True and hit == digest and "already passed" in reason

    # A different input is a different key, and therefore a miss.
    assert lookup(str(tmp_path), stage.stage_id, "0" * 64) is None


def test_a_recorded_failure_is_never_reused(constitution, substrates, tmp_path) -> None:
    mode = constitution.mode("change")
    stage = next(s for s in constitution.stages_for(mode) if s.reusable)
    digest = input_digest(stage, substrates, contract=execution_contract(stage.label))
    record(str(tmp_path), stage.stage_id, digest, "FAIL")
    reuse, reason, _ = decide(mode, stage, substrates, home=str(tmp_path))
    assert reuse is False and "not PASS" in reason


def test_an_entry_from_another_engine_version_is_not_a_hit(
    constitution, substrates, tmp_path
) -> None:
    """A result produced under a different execution contract answers a different question."""
    stage = next(s for s in constitution.stages if s.reusable)
    digest = input_digest(stage, substrates, contract=execution_contract(stage.label))
    record(str(tmp_path), stage.stage_id, digest, "PASS")
    target = os.path.join(str(tmp_path), stage.stage_id, f"{digest}.json")
    document = json.loads(open(target, encoding="utf-8").read())
    document["engine_version"] = f"{EVIDENCE_VERSION}-other"
    open(target, "w", encoding="utf-8").write(json.dumps(document))
    assert lookup(str(tmp_path), stage.stage_id, digest) is None


def test_a_non_reusable_stage_takes_no_digest(constitution, substrates) -> None:
    stage = next(s for s in constitution.stages if not s.reusable)
    assert input_digest(stage, substrates, contract=execution_contract(stage.label)) is None


def test_a_prefix_matching_no_registered_object_takes_no_digest(constitution, substrates) -> None:
    """A key that covers nothing would be a hit on every run, forever."""

    stage = replace(
        next(s for s in constitution.stages if s.reusable),
        read_set=("a/path/that/is/not/registered/",),
        reuse_inputs=("a/path/that/is/not/registered/",),
    )
    assert input_digest(stage, substrates, contract=("x",)) is None


# --- read-set / reuse-policy separation (Step 3) --------------------------------------


def test_step3_every_stage_declares_a_read_set(constitution) -> None:
    """Mandatory for all fifteen, not for the eight that happen to be cacheable."""
    missing = [s.stage_id for s in constitution.stages if not s.read_set]
    assert missing == [], f"stages with no read_set: {missing}"
    non_reusable = [s for s in constitution.stages if not s.reusable]
    assert non_reusable, "fixture assumption: some stages are non-reusable"
    assert all(s.read_set for s in non_reusable), "a non-reusable stage must still declare reads"


def test_step3_removing_a_read_set_is_refused(constitution, substrates) -> None:
    """MUTATION — remove read-set → refusal.

    Both refusals matter and they differ: the law refuses the DECLARATION, and
    ``input_digest`` refuses the KEY. A stage stripped of its read-set must fail both.
    """

    ctx = uvi_gate._Context()
    assert every_stage_declares_a_read_set(ctx) == []
    stripped = replace(ctx.constitution.stages[0], read_set=(), reuse_inputs=())
    ctx.constitution = replace(ctx.constitution, stages=(stripped, *ctx.constitution.stages[1:]))
    findings = every_stage_declares_a_read_set(ctx)
    assert findings and stripped.stage_id in findings[0]

    keyable = next(
        s
        for s in constitution.stages
        if s.reusable and input_digest(s, substrates, contract=execution_contract(s.label))
    )
    blank = replace(keyable, read_set=(), reuse_inputs=())
    assert input_digest(blank, substrates, contract=execution_contract(blank.label)) is None


def test_step3_a_read_set_makes_a_previously_invisible_stage_reachable(
    constitution, substrates
) -> None:
    """MUTATION — add a read-set to a previously unbounded stage → the relation changes.

    Before the separation the seven non-reusable stages declared nothing, so no change
    could be related to them. Measured directly: the same query over the old coupled
    field and over the declared read-set.
    """
    probe = ("00-BOOK/SCHEMAS/artifact.schema.json",)
    coupled = [
        s.stage_id
        for s in constitution.stages
        if any(set(resolve_prefix(substrates, p)) & set(probe) for p in (s.reuse_inputs or ()))
    ]
    declared = stages_reading(constitution.stages, substrates, probe)
    assert set(coupled) < set(declared), "the read-set must reach strictly more stages"
    newly = set(declared) - set(coupled)
    assert any(
        not next(s for s in constitution.stages if s.stage_id == sid).reusable for sid in newly
    ), "the stages the separation reveals must include non-reusable ones"


def test_step3_toggling_reuse_leaves_the_dependency_relation_unchanged(
    constitution, substrates
) -> None:
    """MUTATION — toggle the reuse flag → dependency relation unchanged, on every stage."""

    probe = ("00-BOOK/SCHEMAS/artifact.schema.json", "engine/uckp/facets.py")
    before = stages_reading(constitution.stages, substrates, probe)
    flipped = tuple(replace(s, reusable=not s.reusable) for s in constitution.stages)
    assert stages_reading(flipped, substrates, probe) == before
    for original, toggled in zip(constitution.stages, flipped, strict=True):
        assert original.reads == toggled.reads
        assert original.reusable is not toggled.reusable


def test_step3_changing_the_read_set_changes_the_digest(constitution, substrates) -> None:
    """MUTATION — change read-set → digest changes, in both directions."""

    stage = next(
        s
        for s in constitution.stages
        if s.reusable
        and len(s.reads) > 1
        and input_digest(s, substrates, contract=execution_contract(s.label))
    )
    contract = execution_contract(stage.label)
    baseline = input_digest(stage, substrates, contract=contract)
    widened = replace(stage, read_set=(*stage.reads, "00-BOOK/tools/"))
    narrowed = replace(stage, read_set=tuple(sorted(stage.reads))[:-1])
    assert input_digest(widened, substrates, contract=contract) != baseline
    assert input_digest(narrowed, substrates, contract=contract) != baseline


def test_step3_reuse_inputs_still_resolves_without_a_read_set(constitution, substrates) -> None:
    """COMPATIBILITY — ``reuse_inputs`` was not removed; a declaration lacking read_set keys."""

    stage = next(s for s in constitution.stages if s.reusable and s.reuse_inputs)
    legacy = replace(stage, read_set=())
    assert legacy.reads == stage.reuse_inputs
    assert input_digest(legacy, substrates, contract=execution_contract(legacy.label)) is not None


def test_step3_the_whole_boundary_token_resolves_to_the_whole_boundary(substrates) -> None:
    """``**`` is the declared token for a stage whose subject IS the tree."""
    assert set(resolve_prefix(substrates, WHOLE_BOUNDARY)) == set(substrates.universal)
    assert len(resolve_prefix(substrates, WHOLE_BOUNDARY)) > len(substrates.objects)


# --- read-set resolution and withheld hashes (A5 / A6) -------------------------------


def test_A6_the_read_set_resolves_against_the_universal_registry(substrates) -> None:
    """A6 — the executable projection is a subset, and a read-set is not confined to it.

    01 omits every DOCUMENT_ARTIFACT. Two declared prefixes name trees made entirely of
    documents, so against 01 they matched nothing at all while the objects sat, tracked
    and hashed, in 02.
    """
    assert len(substrates.universal) > len(substrates.objects)
    assert set(substrates.objects) <= set(substrates.universal), "02 must be a superset of 01"
    for prefix in ("00-SOURCE/", "00-BOOK/SCHEMAS/"):
        in_executable = [p for p in substrates.objects if p.startswith(prefix)]
        resolved = resolve_prefix(substrates, prefix)
        assert not in_executable, "fixture assumption: these are documents, absent from 01"
        assert resolved, f"{prefix} must resolve against the universal registry"


def test_A6_every_reusable_stage_now_takes_a_key(constitution, substrates) -> None:
    """A6 — the three permanently-keyless stages are keyless no longer.

    governance-pre, registry-validate and meta-constitutional could never compute a key.
    Every stage the declaration calls reusable must now produce one, or reuse is a
    promise the engine cannot keep.
    """
    source = verify_source()
    keyless = [
        stage.stage_id
        for stage in constitution.stages
        if stage.reusable
        and input_digest(stage, substrates, contract=execution_contract(stage.label, source=source))
        is None
    ]
    assert keyless == [], f"stages declared reusable but unable to key: {keyless}"


def test_A5_a_withheld_hash_contributes_a_constant_rather_than_refusing(
    constitution, substrates
) -> None:
    """A5 — withheld is a declared property of the object, not an absent measurement.

    Eleven surfaces carry ``content_hash_withheld: SELF_REFERENTIAL`` because a file
    cannot contain its own hash. Treating that as "unmeasured" refused the key for every
    stage whose read-set contained one, permanently and silently.
    """
    withheld = {
        path: entry
        for path, entry in substrates.universal.items()
        if not entry.get("content_hash") and entry.get("content_hash_withheld")
    }
    assert withheld, "fixture assumption: the registry declares withheld hashes"

    # No object may carry neither a hash nor a declared reason — that is the case that
    # must still refuse, and it must not exist in a healthy registry.
    unexplained = [
        path
        for path, entry in substrates.universal.items()
        if not entry.get("content_hash") and not entry.get("content_hash_withheld")
    ]
    assert unexplained == [], f"objects with no hash and no declared reason: {unexplained[:5]}"

    # meta-constitutional reads 00-BOOK/DATA/, which contains a withheld object.
    stage = next(s for s in constitution.stages if s.stage_id == "meta-constitutional")
    assert any(p in withheld for p in resolve_prefix(substrates, "00-BOOK/DATA/"))
    assert input_digest(stage, substrates, contract=execution_contract(stage.label)) is not None


def test_A5_an_unexplained_missing_hash_still_refuses(constitution, substrates) -> None:
    """A5 — the distinction is withheld vs MISSING, and missing must still refuse."""

    stage = replace(
        next(s for s in constitution.stages if s.reusable),
        reuse_inputs=("engine/verification_intelligence/",),
    )
    contract = execution_contract(stage.label)
    assert input_digest(stage, substrates, contract=contract) is not None

    victim = next(iter(resolve_prefix(substrates, "engine/verification_intelligence/")))
    original = substrates.universal[victim]
    substrates.universal[victim] = {
        k: v for k, v in original.items() if k not in ("content_hash", "content_hash_withheld")
    }
    try:
        assert input_digest(stage, substrates, contract=contract) is None
    finally:
        substrates.universal[victim] = original


def test_A5_withheld_and_hashed_are_not_the_same_key(constitution, substrates) -> None:
    """A5 — a withheld marker must not collide with a real hash of the same text."""

    stage = replace(
        next(s for s in constitution.stages if s.reusable),
        reuse_inputs=("engine/verification_intelligence/",),
    )
    contract = execution_contract(stage.label)
    victim = next(iter(resolve_prefix(substrates, "engine/verification_intelligence/")))
    original = substrates.universal[victim]
    marker = "SELF_REFERENTIAL"
    try:
        substrates.universal[victim] = {**original, "content_hash": marker}
        as_hash = input_digest(stage, substrates, contract=contract)
        substrates.universal[victim] = {
            **{k: v for k, v in original.items() if k != "content_hash"},
            "content_hash_withheld": marker,
        }
        as_withheld = input_digest(stage, substrates, contract=contract)
        assert as_hash != as_withheld
    finally:
        substrates.universal[victim] = original


def test_UVI_L_11_fires_on_a_read_set_that_resolves_to_nothing(substrates) -> None:
    """UVI-L-11 — mutation proof: the law must fail when the condition it names is present."""
    ctx = uvi_gate._Context()
    assert every_declared_read_set_resolves(ctx) == [], "the law must hold as the tree stands"

    bogus = replace(
        ctx.constitution.stages[0],
        read_set=("no/such/tree/",),
        reuse_inputs=("no/such/tree/",),
    )
    ctx.constitution = replace(ctx.constitution, stages=(bogus, *ctx.constitution.stages[1:]))
    findings = every_declared_read_set_resolves(ctx)
    assert findings, "the law did not fire on an unresolvable read-set"
    assert "no/such/tree/" in findings[0]


# --- the execution contract in the evidence key (Step 1) ----------------------------
#
# The key used to cover what a stage READS but not what it RUNS. A stage is both, and a
# cache keyed on only one of them answers a question nobody asked. Every test below
# computes a real key from the real declaration and the real script; none asserts a
# hardcoded digest, because a hardcoded digest would freeze the composition rather than
# measure it.


def _reusable_keyable(constitution, substrates):
    """A declared stage that is reusable AND whose declared inputs actually resolve."""
    for stage in constitution.stages:
        if not stage.reusable:
            continue
        contract = execution_contract(stage.label)
        if contract and input_digest(stage, substrates, contract=contract):
            return stage, contract
    raise AssertionError("no reusable stage takes a digest; the fixture cannot measure reuse")


def test_the_contract_of_every_declared_stage_resolves(constitution) -> None:
    """A stage whose command cannot be read has no identity to key on."""
    source = verify_source()
    for stage in constitution.stages:
        contract = execution_contract(stage.label, source=source)
        assert contract, f"no execution contract resolved for {stage.stage_id}"
        assert all(token for token in contract), f"empty argv token in {stage.stage_id}"


def test_A_same_inputs_same_command_is_one_key_and_a_hit(
    constitution, substrates, tmp_path
) -> None:
    """A — identical inputs and identical command: identical key, reuse allowed."""
    stage, contract = _reusable_keyable(constitution, substrates)
    first = input_digest(stage, substrates, contract=contract)
    second = input_digest(stage, substrates, contract=contract)
    assert first == second, "the same contract must produce the same key"

    mode = constitution.mode("change")
    record(str(tmp_path), stage.stage_id, first, "PASS")
    reuse, reason, hit = decide(mode, stage, substrates, home=str(tmp_path), verify=verify_source())
    assert reuse is True and hit == first and "already passed" in reason


def test_B_a_changed_command_is_a_different_key_and_a_miss(
    constitution, substrates, tmp_path
) -> None:
    """B — same inputs, changed command: different key, and the recorded PASS is unreachable.

    This is the defect the step closes, performed rather than described: the entry is
    recorded under the real contract, the command is then edited exactly as a maintainer
    would edit it, and the edited stage must NOT reach that entry.
    """
    stage, contract = _reusable_keyable(constitution, substrates)
    original = input_digest(stage, substrates, contract=contract)
    record(str(tmp_path), stage.stage_id, original, "PASS")

    mutations = (
        contract + ("--newly-added-flag",),
        contract[:-1],
        ("different-interpreter",) + contract[1:],
    )
    for mutated in mutations:
        assert mutated != contract
        key = input_digest(stage, substrates, contract=mutated)
        assert key is not None
        assert key != original, f"a changed command produced the same key: {mutated}"
        assert (
            lookup(str(tmp_path), stage.stage_id, key) is None
        ), "a changed command reached a result it never produced"


def test_C_argument_order_is_significant(constitution, substrates) -> None:
    """C — reordering arguments changes the key.

    A shell passes argv in the order written. Nothing here may assume the receiving
    parser is order-insensitive, so order is part of the identity.
    """
    stage, contract = _reusable_keyable(constitution, substrates)
    flagged = contract + ("--alpha", "--beta")
    swapped = contract + ("--beta", "--alpha")
    assert input_digest(stage, substrates, contract=flagged) != input_digest(
        stage, substrates, contract=swapped
    )


def test_C_token_boundaries_cannot_be_forged(constitution, substrates) -> None:
    """C — two tokens are never the same key as the one token that concatenates them."""
    stage, contract = _reusable_keyable(constitution, substrates)
    split = contract + ("--gate", "--quiet")
    joined = contract + ("--gate --quiet",)
    assert input_digest(stage, substrates, contract=split) != input_digest(
        stage, substrates, contract=joined
    )


def test_D_equivalent_serialisations_of_one_command_are_one_key(constitution, substrates) -> None:
    """D — how the invocation is WRITTEN does not change the key; what it RUNS does.

    Line-wrapping, indentation, repeated spaces and quoting style are all serialisation.
    A maintainer who re-wraps a long invocation must not invalidate its evidence.
    """
    stage, _ = _reusable_keyable(constitution, substrates)
    label = stage.label
    variants = (
        f'run_stage "{label}" "$PY" -m pkg.mod --gate --quiet\n',
        f'run_stage "{label}" \\\n  "$PY" -m pkg.mod --gate --quiet\n',
        f'run_stage "{label}"    $PY    -m   pkg.mod   --gate   --quiet\n',
        f'run_stage "{label}" \\\n    "$PY" \\\n    -m pkg.mod \\\n    --gate --quiet\n',
    )
    contracts = {execution_contract(label, source=v) for v in variants}
    assert len(contracts) == 1, f"serialisation changed the contract: {contracts}"
    keys = {input_digest(stage, substrates, contract=c) for c in contracts}
    assert len(keys) == 1


def test_E_no_clock_host_path_or_environment_reaches_the_key(constitution, substrates) -> None:
    """E — the key carries no observation of the machine that computed it.

    The contract is taken from the script's SOURCE TEXT, so ``"$PY"`` stays the literal
    ``$PY`` and never becomes this checkout's absolute venv path. Were it otherwise the
    key would differ between two machines verifying identical trees, and UVI-L-10's
    prohibition on an absolute path reaching a plan would be broken by the field added
    to make the plan honest.
    """
    source = verify_source()
    for stage in constitution.stages:
        contract = execution_contract(stage.label, source=source)
        assert contract is not None
        for token in contract:
            assert not os.path.isabs(token), f"absolute path in contract: {token}"
            assert repo_root() not in token, f"checkout path in contract: {token}"
            assert not token.startswith("~"), f"home-relative path in contract: {token}"
            assert "\n" not in token

    # The key is a pure function of (declaration, registry, script). Recomputing it in a
    # second process must land on the same value: nothing observed at runtime enters it.
    stage, contract = _reusable_keyable(constitution, substrates)
    expected = input_digest(stage, substrates, contract=contract)
    program = (
        "from engine.verification_intelligence.constitution import "
        "load_constitution, execution_contract\n"
        "from engine.verification_intelligence.registry import load_substrates\n"
        "from engine.verification_intelligence.evidence import input_digest\n"
        "c = load_constitution(); s = load_substrates()\n"
        f"st = next(x for x in c.stages if x.stage_id == {stage.stage_id!r})\n"
        "print(input_digest(st, s, contract=execution_contract(st.label)))\n"
    )
    completed = subprocess.run(  # noqa: S603
        [sys.executable, "-c", program],
        cwd=repo_root(),
        capture_output=True,
        text=True,
        check=True,
    )
    assert completed.stdout.strip() == expected


def test_a_certification_mode_never_resolves_a_contract_at_all(
    constitution, substrates, tmp_path
) -> None:
    """UVI-L-09 is evaluated BEFORE the contract, and this step did not move it.

    A certification-eligible mode must return without reading the script, the store or a
    digest. Passing a deliberately broken script proves the refusal happens first: if the
    contract were resolved before the mode check, this would raise or return a digest.
    """
    for mode in constitution.modes:
        if not mode.certification_eligible:
            continue
        for stage in constitution.stages_for(mode):
            reuse, reason, digest = decide(
                mode, stage, substrates, home=str(tmp_path), verify="not a shell script at all"
            )
            assert reuse is False
            assert digest is None
            assert "never reuses" in reason


def test_an_unresolvable_contract_refuses_the_key_rather_than_guessing(
    constitution, substrates, tmp_path
) -> None:
    """Unknown widens. A label the script does not declare exactly once has no contract."""
    stage, _ = _reusable_keyable(constitution, substrates)
    assert execution_contract(stage.label, source="") is None
    duplicated = f'run_stage "{stage.label}" a\n' f'run_stage "{stage.label}" b\n'
    assert execution_contract(stage.label, source=duplicated) is None
    unbalanced = f'run_stage "{stage.label}" "never-closed\n'
    assert execution_contract(stage.label, source=unbalanced) is None

    mode = constitution.mode("change")
    reuse, reason, digest = decide(mode, stage, substrates, home=str(tmp_path), verify="")
    assert reuse is False and digest is None
    assert "execution contract" in reason


# --- the plan -----------------------------------------------------------------------


@pytest.mark.parametrize("mode_id", ["fast", "change", "integration", "full"])
def test_planning_twice_produces_identical_bytes(mode_id, constitution, substrates, tests_registry):
    first = build_plan(
        mode_id, constitution=constitution, substrates=substrates, tests=tests_registry, changed=()
    )
    second = build_plan(
        mode_id, constitution=constitution, substrates=substrates, tests=tests_registry, changed=()
    )
    assert plan_json(first) == plan_json(second)
    assert plan_digest(first) == plan_digest(second)


@pytest.mark.parametrize("mode_id", ["fast", "change", "integration", "full"])
def test_a_plan_carries_no_observation_of_the_run(
    mode_id, constitution, substrates, tests_registry
) -> None:
    """A clock or a machine path would make two plans of one state differ."""

    body = plan_json(
        build_plan(
            mode_id,
            constitution=constitution,
            substrates=substrates,
            tests=tests_registry,
            changed=(),
        )
    )
    assert not re.findall(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}", body)
    assert REPO not in body


def test_every_declared_stage_appears_in_every_plan(constitution, substrates, tests_registry):
    """A stage absent from the plan would be executed by the shell's fail-safe default."""
    for mode in constitution.modes:
        plan = build_plan(
            mode.mode_id,
            constitution=constitution,
            substrates=substrates,
            tests=tests_registry,
            changed=(),
        )
        assert [entry.stage.label for entry in plan.stages] == list(constitution.stage_labels)


def test_a_developer_mode_that_escalates_is_run_under_the_floor(
    constitution, substrates, tests_registry
) -> None:
    """Running the whole suite WITHOUT the floor would be less than the old default did."""
    plan = build_plan(
        "change",
        constitution=constitution,
        substrates=substrates,
        tests=tests_registry,
        changed=("00-BOOK/DATA/uvi-probe.json",),
    )
    assert plan.selection.escalated
    assert plan.coverage is Coverage.FLOOR_90
    assert plan.escalated_coverage
    coverage_report = next(e for e in plan.stages if e.stage.stage_id == "coverage-report")
    assert coverage_report.action is Action.RUN


def test_a_developer_mode_that_does_not_escalate_owns_no_floor(
    constitution, substrates, tests_registry
) -> None:
    plan = build_plan(
        "change",
        constitution=constitution,
        substrates=substrates,
        tests=tests_registry,
        changed=("engine/uaue/gate.py",),
    )
    assert plan.coverage is Coverage.NOT_EVALUATED
    coverage_report = next(e for e in plan.stages if e.stage.stage_id == "coverage-report")
    assert coverage_report.action is Action.SKIP


def test_only_full_admits_the_registration_observation(
    constitution, substrates, tests_registry
) -> None:
    for mode in constitution.modes:
        plan = build_plan(
            mode.mode_id,
            constitution=constitution,
            substrates=substrates,
            tests=tests_registry,
            changed=(),
        )
        entry = next(e for e in plan.stages if e.stage.stage_id == "registration-observation")
        expected = Action.RUN if mode.mode_id == "full" else Action.SKIP
        assert entry.action is expected


def test_the_plan_the_shell_reads_is_looked_up_by_the_stage_label(
    constitution, substrates, tests_registry
) -> None:
    """One string identifies a stage in verify.sh, in the record, and in the plan."""
    plan = build_plan(
        "full", constitution=constitution, substrates=substrates, tests=tests_registry, changed=()
    )
    rows = [line.split("\t") for line in plan_tsv(plan).strip().splitlines()]
    assert [row[3] for row in rows] == list(constitution.stage_labels)
    assert all(row[0] in {"RUN", "SKIP", "REUSE"} for row in rows)
    assert all("\t" not in row[3] for row in rows)


def test_a_selection_fault_is_answered_with_the_whole_suite(
    constitution, substrates, tests_registry, monkeypatch
) -> None:
    """The caller's alternative to a wide plan is no plan at all, never a narrow one."""

    def _fault(*args, **kwargs):
        raise VerificationIntelligenceError("the substrate is unreadable")

    monkeypatch.setattr("engine.verification_intelligence.plan.select", _fault)
    plan = build_plan(
        "change", constitution=constitution, substrates=substrates, tests=tests_registry
    )
    assert plan.selection.selection is Selection.WHOLE_SUITE
    assert plan.selection.test_paths == tests_registry.paths


# --- the gate -----------------------------------------------------------------------


def test_every_law_holds_over_the_live_repository() -> None:
    """The gate verify.sh runs, run here so a refusal is a test failure with a name."""
    report = uvi_gate.measure()
    refused = [law for law in report["laws"] if not law["holds"]]
    assert refused == [], "refused laws:\n" + "\n".join(
        f"  {law['law_id']} {law['title']}: {law['violations']}" for law in refused
    )
    assert report["verdict"] == "COHERENT"


def test_the_baseline_contract_is_a_ratchet() -> None:
    """Every gate the certification default ran before this rework must still run."""
    document = load_declaration()
    baseline = document["no_assurance_reduction"]["baseline_stages"]
    assert baseline, "no baseline contract is declared"
    constitution = load_constitution()
    for mode in constitution.modes:
        if not mode.certification_eligible:
            continue
        admitted = {stage.label for stage in constitution.stages_for(mode)}
        assert set(baseline) <= admitted, f"--{mode.mode_id} dropped a baseline gate"


def test_the_stage_registry_and_the_script_declare_the_same_contract() -> None:
    source = open(os.path.join(REPO, "verify.sh"), encoding="utf-8").read()
    assert uvi_gate._declared_stage_labels(source) == list(load_constitution().stage_labels)


def test_the_script_accepts_exactly_the_declared_modes() -> None:
    source = open(os.path.join(REPO, "verify.sh"), encoding="utf-8").read()
    assert uvi_gate._accepted_flags(source) == set(load_constitution().flags)


def test_the_bare_invocation_is_the_declared_default() -> None:
    source = open(os.path.join(REPO, "verify.sh"), encoding="utf-8").read()
    assert f'MODE="{load_constitution().default_mode_id}"' in source


def test_the_gate_reports_a_fault_rather_than_a_verdict_on_a_broken_declaration(tmp_path) -> None:
    """'A law was refused' and 'the declaration is unreadable' are different facts."""
    path = tmp_path / "declaration.json"
    path.write_text("{not json", encoding="utf-8")
    assert uvi_gate.main(["--gate", "--quiet", "--declaration", str(path)]) == uvi_gate.EXIT_FAULT


def test_the_gate_exits_zero_when_every_law_holds() -> None:
    assert uvi_gate.main(["--gate", "--quiet"]) == uvi_gate.EXIT_COHERENT


def test_the_gate_emits_json_and_a_rendered_report(capsys) -> None:
    assert uvi_gate.main(["--json"]) == uvi_gate.EXIT_COHERENT
    report = json.loads(capsys.readouterr().out)
    declared = len(load_declaration()["laws"])
    assert report["laws_measured"] == len(report["laws"]) == declared
    assert uvi_gate.main([]) == uvi_gate.EXIT_COHERENT
    assert "VERDICT" in capsys.readouterr().out


def test_the_gate_writes_nothing(tmp_path) -> None:
    """OBSERVE MODE. A gate that writes can drift, and this one measures drift."""

    before = subprocess.run(  # noqa: S603
        ["git", "status", "--porcelain"],  # noqa: S607
        cwd=REPO,
        capture_output=True,
        text=True,
        check=False,
    ).stdout
    subprocess.run(  # noqa: S603
        [sys.executable, "-m", "engine.verification_intelligence.gate", "--quiet"],
        cwd=REPO,
        capture_output=True,
        text=True,
        check=False,
    )
    after = subprocess.run(  # noqa: S603
        ["git", "status", "--porcelain"],  # noqa: S607
        cwd=REPO,
        capture_output=True,
        text=True,
        check=False,
    ).stdout
    assert before == after


# --- the CLI ------------------------------------------------------------------------


def test_the_cli_emits_a_plan_the_shell_can_read(tmp_path) -> None:
    out = tmp_path / "plan.tsv"
    assert main(["plan", "--mode", "full", "--tsv", "--out", str(out), "--path", "README.md"]) == 0
    rows = [line.split("\t") for line in out.read_text(encoding="utf-8").strip().splitlines()]
    assert rows and all(len(row) == 4 for row in rows)


def test_the_cli_refuses_to_record_against_an_undeclared_stage() -> None:
    assert (
        main(["record", "--stage-label", "no such stage", "--result", "PASS", "--digest", "x"]) == 2
    )


# --- execution, actually executed ---------------------------------------------------
#
# The section that matters most and is easiest to skip. plan_shards and the neutrality
# assertion above are pure and cheap to test; run_tests spawns processes, and it is the
# code that could report a pass over tests that never ran. So it is exercised here for
# real, over a throwaway suite, rather than described.


def _throwaway_suite(tmp_path, *, failing: bool = False) -> tuple:
    """A tiny real pytest suite in a scratch directory, plus shards over it."""
    (tmp_path / "test_alpha.py").write_text(
        "def test_alpha():\n    assert True\n", encoding="utf-8"
    )
    (tmp_path / "test_beta.py").write_text(
        "def test_beta():\n    assert %s\n" % ("False" if failing else "True"), encoding="utf-8"
    )
    return (
        Shard(index=0, test_paths=("test_alpha.py",), cost_seconds=0.1),
        Shard(index=1, test_paths=("test_beta.py",), cost_seconds=0.1),
    )


def test_run_tests_executes_every_shard_and_passes_when_they_pass(tmp_path) -> None:
    shards = _throwaway_suite(tmp_path)
    stream = io.StringIO()
    code = run_tests(
        shards,
        Coverage.NOT_EVALUATED,
        root=str(tmp_path),
        python=sys.executable,
        selection=("test_alpha.py", "test_beta.py"),
        stream=stream,
    )
    assert code == 0
    body = stream.getvalue()
    assert "shard 0" in body and "shard 1" in body
    assert "2 shard(s) running concurrently" in body


def test_a_throttled_wave_runs_every_shard_and_says_so(tmp_path, monkeypatch) -> None:
    """The bound changes the rate, never the selection — UVI-L-08 over one host.

    Pinned to one seat, so the second shard can only start once the first has finished:
    this is the path that was missing when twelve interpreters started together and the
    operating system, not a gate, decided which of them survived.
    """
    monkeypatch.setenv("UVI_CONCURRENCY", "1")
    shards = _throwaway_suite(tmp_path)
    stream = io.StringIO()
    code = run_tests(
        shards,
        Coverage.NOT_EVALUATED,
        root=str(tmp_path),
        python=sys.executable,
        selection=("test_alpha.py", "test_beta.py"),
        stream=stream,
    )
    assert code == 0
    body = stream.getvalue()
    assert "[throttled to 1 at once]" in body
    # Every unit still ran, and the transcript is still in index order.
    assert "shard 0" in body and "shard 1" in body
    assert body.index("shard 0") < body.index("shard 1")


def test_run_tests_fails_when_any_shard_fails(tmp_path) -> None:
    shards = _throwaway_suite(tmp_path, failing=True)
    stream = io.StringIO()
    code = run_tests(
        shards,
        Coverage.NOT_EVALUATED,
        root=str(tmp_path),
        python=sys.executable,
        selection=("test_alpha.py", "test_beta.py"),
        stream=stream,
    )
    assert code == 1
    assert "shard(s) FAILED: [1]" in stream.getvalue()


def test_run_tests_refuses_a_partition_that_is_not_the_selection(tmp_path) -> None:
    """The check that stands between a dropped shard and a green run."""

    shards = _throwaway_suite(tmp_path)[:1]
    with pytest.raises(VerificationIntelligenceError, match="missing"):
        run_tests(
            shards,
            Coverage.NOT_EVALUATED,
            root=str(tmp_path),
            python=sys.executable,
            selection=("test_alpha.py", "test_beta.py"),
            stream=io.StringIO(),
        )


def test_run_tests_refuses_to_report_a_pass_over_nothing(tmp_path) -> None:
    """An empty partition is the one thing that must never look like success."""

    stream = io.StringIO()
    assert (
        run_tests(
            (), Coverage.NOT_EVALUATED, root=str(tmp_path), python=sys.executable, stream=stream
        )
        == 1
    )
    assert "refusing to report a pass" in stream.getvalue()


def test_the_floor_is_evaluated_over_combined_data_and_refuses_when_there_is_none(
    tmp_path,
) -> None:
    """No coverage data cannot be answered with a pass; the floor would be a claim about air."""

    stream = io.StringIO()
    empty = tmp_path / "no-data"
    empty.mkdir()
    assert _combine_and_evaluate(sys.executable, str(tmp_path), str(empty), stream) == 1
    assert "no coverage data" in stream.getvalue()


def test_the_floor_refuses_an_interpreter_that_cannot_measure_it(tmp_path) -> None:
    """A toolchain that cannot evaluate the floor must FAULT, not fail thirteen times.

    Every shard inherits the caller's interpreter, and every floor-mode argv carries pytest-cov's
    options. Under an interpreter without pytest-cov all shards exit 4 on `unrecognized
    arguments` before collecting anything, and the run reported `shard(s) FAILED` — which reads
    as a test failure rather than as a toolchain that cannot measure. Measured: a bare `python3`
    on a machine whose default series is not the pinned one reproduces it exactly.
    """

    # An "interpreter" that cannot import pytest_cov. Standing in for a real one keeps the test
    # portable: the probe only asks whether `<python> -c "import pytest_cov"` succeeds.
    shim = tmp_path / "python-without-pytest-cov"
    shim.write_text("#!/bin/sh\nexit 1\n", encoding="utf-8")
    shim.chmod(shim.stat().st_mode | stat.S_IEXEC)

    shard = Shard(index=0, test_paths=("a/test_x.py",), cost_seconds=1.0)
    out = io.StringIO()
    code = run_tests((shard,), Coverage.FLOOR_90, python=str(shim), stream=out)

    assert code == 2, "an unmeasurable floor is a FAULT (2), never a test failure (1)"
    assert "cannot import pytest_cov" in out.getvalue()
    assert (
        "shard" not in out.getvalue().lower().split("cannot import")[0]
    ), "the refusal must come BEFORE any shard is spawned"

    # Without the floor the plugin is not needed, so the same interpreter must NOT be refused
    # here — requiring it would reject developer runs that would have worked.
    without = io.StringIO()
    assert (
        run_tests((shard,), Coverage.NOT_EVALUATED, python=str(shim), stream=without) != 2
        or "cannot import pytest_cov" not in without.getvalue()
    )


def test_the_shard_command_keeps_addopts_under_the_floor_and_drops_them_without_it() -> None:
    """The denominator must not depend on how the run was scheduled."""

    shard = Shard(index=0, test_paths=("a/test_x.py",), cost_seconds=1.0)
    under_floor = _shard_argv("py", shard, Coverage.FLOOR_90, report_path="uvi-coverage-x/s0.xml")
    assert "-o" not in under_floor, "clearing addopts would drop every --cov argument"
    assert "--cov-fail-under=0" in under_floor, "the floor is evaluated once, over combined data"
    # The XML report is REDIRECTED, never cleared. `--cov-report=` does not suppress
    # anything once addopts has already named a report: pytest-cov keys reports by TYPE
    # and only collapses to none when the empty entry is the only one. Naming `xml` again
    # replaces it, which is what keeps twelve concurrent shards from each writing
    # `coverage.xml` into the repository root — the file the UCI gate reads as evidence.
    assert "--cov-report=xml:uvi-coverage-x/s0.xml" in under_floor
    assert "--cov-report=" not in under_floor, "an empty report entry suppresses nothing here"
    assert under_floor[-1] == "a/test_x.py"

    # No report path is still accepted, and still never writes into the repository.
    assert "--cov-report=" in _shard_argv("py", shard, Coverage.FLOOR_90)

    without = _shard_argv("py", shard, Coverage.NOT_EVALUATED)
    assert without[3:5] == ["-o", "addopts="] and "--no-cov" in without


# --- every law must be able to refuse -----------------------------------------------
#
# A check that cannot fail is not a check. Each test below breaks exactly one declared
# property and asserts that the law responsible names it — so a law that silently stopped
# measuring anything fails here rather than reporting COHERENT forever.


def _ctx(tmp_path, mutate) -> object:
    document = load_declaration()
    mutate(document)
    path = tmp_path / "declaration.json"
    path.write_text(json.dumps(document), encoding="utf-8")
    return uvi_gate._Context(declaration=str(path))


def test_l01_refuses_a_mode_the_script_does_not_accept(tmp_path) -> None:
    def mutate(document):
        document["mode_constitution"]["modes"][0]["flag"] = "--nonexistent"

    findings = uvi_gate.mode_constitution_completeness(_ctx(tmp_path, mutate))
    assert any("does not accept it" in f for f in findings)


def test_l02_refuses_a_default_the_script_does_not_resolve_to(tmp_path) -> None:
    def mutate(document):
        document["mode_constitution"]["default_mode"] = "integration"

    findings = uvi_gate.exactly_one_default(_ctx(tmp_path, mutate))
    assert any("defaults to" in f for f in findings)


def test_l03_refuses_a_stage_the_script_does_not_declare(tmp_path) -> None:
    def mutate(document):
        document["stage_registry"]["stages"][0]["label"] = "a stage nothing declares"

    findings = uvi_gate.stage_registry_reconciliation(_ctx(tmp_path, mutate))
    assert any("does not declare" in f for f in findings)
    assert any("does not classify" in f for f in findings)


def test_l03_refuses_a_reordered_contract(tmp_path) -> None:
    """Order is part of the contract the canonical validation record digests."""

    def mutate(document):
        stages = document["stage_registry"]["stages"]
        stages[0], stages[1] = stages[1], stages[0]

    findings = uvi_gate.stage_registry_reconciliation(_ctx(tmp_path, mutate))
    assert any("DIFFERENT order" in f for f in findings)


def test_l04_refuses_dropping_a_baseline_gate_from_a_certifying_mode(tmp_path) -> None:
    """THE ratchet. Removing a gate from --full must fail here, not be noticed later."""

    def mutate(document):
        baseline = document["no_assurance_reduction"]["baseline_stages"][0]
        for stage in document["stage_registry"]["stages"]:
            if stage["label"] == baseline:
                stage["modes"] = ["fast"]

    findings = uvi_gate.no_assurance_reduction(_ctx(tmp_path, mutate))
    assert any("no longer runs a baseline gate" in f for f in findings)


def test_l04_refuses_deleting_a_baseline_gate_outright(tmp_path) -> None:
    def mutate(document):
        baseline = document["no_assurance_reduction"]["baseline_stages"][0]
        document["stage_registry"]["stages"] = [
            stage for stage in document["stage_registry"]["stages"] if stage["label"] != baseline
        ]

    findings = uvi_gate.no_assurance_reduction(_ctx(tmp_path, mutate))
    assert any("no longer a declared stage" in f for f in findings)


def test_l04_refuses_a_repository_where_nothing_certifies(tmp_path) -> None:
    def mutate(document):
        for mode in document["mode_constitution"]["modes"]:
            mode["certification_eligible"] = False

    findings = uvi_gate.no_assurance_reduction(_ctx(tmp_path, mutate))
    assert any("owned by nothing" in f for f in findings)


def test_l05_refuses_a_mode_that_certifies_a_subset(tmp_path) -> None:
    def mutate(document):
        for mode in document["mode_constitution"]["modes"]:
            if mode["id"] == "change":
                mode["certification_eligible"] = True

    findings = uvi_gate.no_mode_claims_more_than_it_measures(_ctx(tmp_path, mutate))
    assert any("would certify a subset" in f for f in findings)
    assert any("does not evaluate the floor" in f for f in findings)
    assert any("could certify a cache" in f for f in findings)


def test_l05_refuses_a_second_owner_of_the_floor(tmp_path) -> None:
    def mutate(document):
        for mode in document["mode_constitution"]["modes"]:
            if mode["id"] == "fast":
                mode["coverage"] = "FLOOR_90"

    findings = uvi_gate.no_mode_claims_more_than_it_measures(_ctx(tmp_path, mutate))
    assert any("two owners" in f for f in findings)


def test_l05_refuses_a_mode_that_states_nothing_it_does_not_claim(tmp_path) -> None:
    def mutate(document):
        for mode in document["mode_constitution"]["modes"]:
            if mode["id"] == "fast":
                mode["claims_not"] = []

    findings = uvi_gate.no_mode_claims_more_than_it_measures(_ctx(tmp_path, mutate))
    assert any("does not claim" in f for f in findings)


def test_l06_refuses_a_declared_substrate_that_nothing_reads(tmp_path) -> None:
    """A declaration claiming a derivation that does not happen is worse than silence."""

    def mutate(document):
        document["selection"]["substrates"].append(
            {"id": "invented", "source": "00-BOOK/DATA/a-substrate-nothing-reads.json"}
        )

    findings = uvi_gate.selection_is_derived(_ctx(tmp_path, mutate))
    assert any("no module reads it" in f for f in findings)


def test_l06_refuses_an_authored_test_path_in_the_declaration(tmp_path) -> None:
    def mutate(document):
        document["selection"]["layers"][0]["rule"] = "run engine/tests/unit/test_something.py"

    findings = uvi_gate.selection_is_derived(_ctx(tmp_path, mutate))
    assert any("names a specific test file" in f for f in findings)


def test_l06_ignores_a_test_path_inside_declared_rationale(tmp_path) -> None:
    """A `$`-prefixed key is prose. Prose may discuss a test file; a declaration may not."""

    def mutate(document):
        document["selection"]["$example"] = "for instance engine/tests/unit/test_thing.py"

    assert not [
        f for f in uvi_gate.selection_is_derived(_ctx(tmp_path, mutate)) if "test_thing" in f
    ]


def test_l09_refuses_reuse_conditions_that_omit_the_digest_or_the_result(tmp_path) -> None:
    def mutate(document):
        document["evidence_registry"]["reuse_conditions"] = ["the stage feels fine"]

    findings = uvi_gate.evidence_reuse_integrity(_ctx(tmp_path, mutate))
    assert any("input digest" in f for f in findings)
    assert any("PASS" in f for f in findings)


def test_l10_refuses_a_plan_that_is_not_reproducible(tmp_path, monkeypatch) -> None:
    """The law must be able to see non-determinism, or it is decoration."""

    counter = itertools.count()
    real = uvi_gate.build_plan

    def _drifting(*args, **kwargs):
        plan = real(*args, **kwargs)

        return replace(plan, notes=(f"run {next(counter)}",))

    monkeypatch.setattr(uvi_gate, "build_plan", _drifting)
    findings = uvi_gate.deterministic_planning(uvi_gate._Context())
    assert any("different bytes" in f for f in findings)


def test_the_gate_exits_one_when_a_law_is_refused(tmp_path) -> None:
    document = load_declaration()
    document["mode_constitution"]["default_mode"] = "integration"
    path = tmp_path / "declaration.json"
    path.write_text(json.dumps(document), encoding="utf-8")
    assert (
        uvi_gate.main(["--gate", "--quiet", "--declaration", str(path)]) == uvi_gate.EXIT_INCOHERENT
    )


def test_without_the_gate_flag_a_refusal_is_reported_but_does_not_fail(tmp_path) -> None:
    """`--gate` is what makes it fail closed; without it the gate is a measurement."""
    document = load_declaration()
    document["mode_constitution"]["default_mode"] = "integration"
    path = tmp_path / "declaration.json"
    path.write_text(json.dumps(document), encoding="utf-8")
    assert uvi_gate.main(["--quiet", "--declaration", str(path)]) == uvi_gate.EXIT_COHERENT


# --- the surfaces the shell actually calls ------------------------------------------


def test_the_report_surface_explains_the_plan_it_would_execute(capsys) -> None:
    """`--explain` is only useful if it shows the same decision run-tests will act on."""

    assert main(["report", "--mode", "change", "--path", "engine/uaue/gate.py"]) == 0
    body = capsys.readouterr().out
    assert "VERIFICATION PLAN" in body
    assert "mode                  : --change" in body
    assert "selection layers:" in body
    for label in load_constitution().stage_labels:
        assert label in body


def test_the_report_names_every_escalation_it_widened_on(capsys) -> None:
    assert main(["report", "--mode", "change", "--path", "00-BOOK/DATA/uvi-probe.json"]) == 0
    body = capsys.readouterr().out
    assert "escalations:" in body
    assert "WHOLE_SUITE" in body


def test_the_plan_surface_emits_json_and_a_rendered_form(capsys) -> None:
    assert main(["plan", "--mode", "full", "--json", "--path", "README.md"]) == 0
    document = json.loads(capsys.readouterr().out)
    assert document["artifact_id"] == "UVI-000001"
    assert document["mode"]["id"] == "full"
    assert main(["plan", "--mode", "fast", "--path", "README.md"]) == 0
    assert "VERIFICATION PLAN" in capsys.readouterr().out


def test_the_cli_reports_a_fault_rather_than_a_narrow_plan(monkeypatch, capsys) -> None:
    def _fault(*args, **kwargs):
        raise VerificationIntelligenceError("the substrate is unreadable")

    monkeypatch.setattr(cli, "build_plan", _fault)
    assert cli.main(["plan", "--mode", "fast"]) == 2
    assert "UVI FAULT" in capsys.readouterr().err


def test_recording_a_result_round_trips_through_the_declared_store(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(evidence, "store_home", lambda *a, **k: str(tmp_path))
    monkeypatch.setattr(cli, "store_home", lambda *a, **k: str(tmp_path))
    constitution = load_constitution()
    stage = next(s for s in constitution.stages if s.reusable)
    assert (
        cli.main(["record", "--stage-label", stage.label, "--result", "PASS", "--digest", "a" * 64])
        == 0
    )
    entry = lookup(str(tmp_path), stage.stage_id, "a" * 64)
    assert entry is not None and entry.passed


def test_a_store_that_cannot_be_written_does_not_fail_a_verification(tmp_path) -> None:
    """A cache is an optimisation. It may never be the reason a run fails."""
    blocked = tmp_path / "not-a-directory"
    blocked.write_text("", encoding="utf-8")
    record(str(blocked), "some-stage", "b" * 64, "PASS")
    assert lookup(str(blocked), "some-stage", "b" * 64) is None


# --- fail-closed substrate handling -------------------------------------------------


def test_an_unreadable_registry_is_a_fault_and_never_an_empty_selection(tmp_path) -> None:
    """The most dangerous possible failure is 'nothing to verify'. It must be impossible."""
    with pytest.raises(VerificationIntelligenceError, match="unreadable"):
        load_substrates(str(tmp_path))


def test_a_registry_with_no_dependency_edges_is_refused(tmp_path) -> None:
    target = tmp_path / EXECUTABLE_REGISTRY
    target.parent.mkdir(parents=True)
    target.write_text(
        json.dumps({"entries": [{"path": "a.py", "object_class": "EXECUTABLE_OBJECT"}]}),
        encoding="utf-8",
    )
    with pytest.raises(VerificationIntelligenceError, match="no dependency edges"):
        load_substrates(str(tmp_path))


def test_a_registry_holding_no_entries_is_refused(tmp_path) -> None:
    target = tmp_path / EXECUTABLE_REGISTRY
    target.parent.mkdir(parents=True)
    target.write_text(json.dumps({"entries": []}), encoding="utf-8")
    with pytest.raises(VerificationIntelligenceError, match="no entries"):
        load_substrates(str(tmp_path))


def test_a_tree_with_no_discoverable_suite_is_refused(tmp_path) -> None:
    """The premise moved from a declaration to a measurement, and the refusal is unchanged.

    This test used to write an empty ``[tool.pytest.ini_options]`` and require "no testpaths". Under
    UCOS-OMEGA-001 the collection set is derived from which directories hold suites, so the way to
    have no collectible set is to have no suite — and that is what is built here. A tree whose suite
    is invisible would be certified by running nothing, which is the state this refuses.
    """
    (tmp_path / "pyproject.toml").write_text("[tool.ucos]\n", encoding="utf-8")
    source = tmp_path / "layer" / "core"
    source.mkdir(parents=True)
    (source / "mod.py").write_text("VALUE = 1\n", encoding="utf-8")
    subprocess.run(  # noqa: S603
        ["git", "init", "-q"],  # noqa: S607
        cwd=tmp_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(  # noqa: S603
        ["git", "add", "-A"],  # noqa: S607
        cwd=tmp_path,
        check=True,
        capture_output=True,
    )
    clear_derived_scope_cache()
    with pytest.raises(VerificationIntelligenceError, match="invisible to discovery|no test root"):
        collection_roots(str(tmp_path))


def test_an_absent_cost_model_prices_everything_at_the_default(tmp_path, substrates) -> None:
    """A missing measurement makes a plan slower, never wrong."""

    costs, split, threshold = load_cost_model(str(tmp_path))
    assert costs == {} and split == {} and threshold == 0.0


def test_a_corrupt_cost_model_is_ignored_rather_than_fatal(tmp_path) -> None:
    target = tmp_path / COST_MODEL
    target.parent.mkdir(parents=True)
    target.write_text("{not json", encoding="utf-8")
    assert load_cost_model(str(tmp_path)) == ({}, {}, 0.0)


def test_a_split_entry_whose_content_hash_moved_falls_back_to_the_whole_file(
    substrates, monkeypatch
) -> None:
    """Stale node ids would fail a run; whole-file placement is slower and always correct."""

    real = registry_module.load_cost_model

    def _stale(root=None):
        costs, split, threshold = real(root)
        for entry in split.values():
            entry["content_hash"] = "0" * 64
        return costs, split, threshold

    monkeypatch.setattr(registry_module, "load_cost_model", _stale)
    projected = registry_module.build_test_registry(substrates)
    assert projected.splittable == {}
    assert projected.units_for(projected.paths) == projected.paths


# --- the constitution refuses every incoherence it can compute -----------------------
#
# A declaration that cannot be constructed is a FAULT, deliberately not a verdict: an
# unreadable or self-contradictory constitution must not resolve to whichever answer
# happened to be convenient.


@pytest.mark.parametrize(
    ("what", "mutate", "message"),
    [
        (
            "a stage naming an undeclared phase",
            lambda d: d["stage_registry"]["stages"][0].update(phase="WHENEVER"),
            "undeclared phase",
        ),
        (
            "a stage naming an undeclared plane",
            lambda d: d["stage_registry"]["stages"][0].update(plane="SOMEWHERE"),
            "undeclared plane",
        ),
        (
            "a stage depending on a stage that does not exist",
            lambda d: d["stage_registry"]["stages"][0].update(depends_on=["not-a-stage"]),
            "undeclared stage",
        ),
        (
            "a stage admitting a mode that does not exist",
            lambda d: d["stage_registry"]["stages"][0].update(modes=["turbo"]),
            "undeclared mode",
        ),
        (
            "two stages sharing one id",
            lambda d: d["stage_registry"]["stages"][1].update(
                id=d["stage_registry"]["stages"][0]["id"]
            ),
            "share one id",
        ),
        (
            "two modes sharing one id",
            lambda d: d["mode_constitution"]["modes"][1].update(
                id=d["mode_constitution"]["modes"][0]["id"]
            ),
            "share one id",
        ),
        (
            "a default that is not a declared mode",
            lambda d: d["mode_constitution"].update(default_mode="turbo"),
            "not a declared mode",
        ),
        (
            "a mode selecting from an unknown vocabulary",
            lambda d: d["mode_constitution"]["modes"][0].update(selection="SOME_OF_IT"),
            "unknown vocabulary",
        ),
        (
            "a mode with no coverage decision at all",
            lambda d: d["mode_constitution"]["modes"][0].update(coverage=""),
            "missing or empty",
        ),
        (
            "no modes",
            lambda d: d["mode_constitution"].update(modes=[]),
            "declares no modes",
        ),
        (
            "no stages",
            lambda d: d["stage_registry"].update(stages=[]),
            "declares no stages",
        ),
        (
            "no laws",
            lambda d: d.update(laws=[]),
            "states no laws",
        ),
        (
            "no mode constitution at all",
            lambda d: d.pop("mode_constitution"),
            "no mode_constitution",
        ),
    ],
)
def test_an_incoherent_constitution_is_refused(what, mutate, message, tmp_path) -> None:
    document = load_declaration()
    mutate(document)
    path = tmp_path / "declaration.json"
    path.write_text(json.dumps(document), encoding="utf-8")
    with pytest.raises(VerificationIntelligenceError, match=message):
        load_constitution(str(path))


def test_a_declaration_that_is_not_an_object_is_refused(tmp_path) -> None:
    path = tmp_path / "declaration.json"
    path.write_text("[1, 2, 3]", encoding="utf-8")
    with pytest.raises(VerificationIntelligenceError, match="not an object"):
        load_declaration(str(path))


def test_a_check_no_law_claims_is_refused(tmp_path) -> None:
    """Both directions. An unclaimed check is a measurement nothing acts on."""
    path = tmp_path / "declaration.json"
    path.write_text(json.dumps(load_declaration()), encoding="utf-8")
    with pytest.raises(VerificationIntelligenceError, match="claimed by no law"):
        load_constitution(str(path), checks=frozenset({*uvi_gate.CHECKS, "an_orphan_check"}))


def test_asking_for_a_mode_or_stage_that_does_not_exist_is_refused(constitution) -> None:
    with pytest.raises(VerificationIntelligenceError, match="no such declared mode"):
        constitution.mode("turbo")
    with pytest.raises(VerificationIntelligenceError, match="no such declared stage"):
        constitution.stage("not-a-stage")


def test_a_mode_declaring_an_unknown_stage_selector_is_refused(tmp_path) -> None:
    document = load_declaration()
    document["mode_constitution"]["modes"][0]["stages"] = "EVERYTHING_PLEASE"
    path = tmp_path / "declaration.json"
    path.write_text(json.dumps(document), encoding="utf-8")
    broken = load_constitution(str(path))
    with pytest.raises(VerificationIntelligenceError, match="unknown stage selector"):
        broken.stages_for(broken.modes[0])


# --- the floor, evaluated for real over combined shard data --------------------------


def test_the_floor_is_evaluated_once_over_the_union_of_the_shards(tmp_path) -> None:
    """Two shards, one combined total, one verdict — the property sharding must not break."""

    (tmp_path / "measured.py").write_text(
        textwrap.dedent(
            """
            def covered_by_shard_one():
                return 1

            def covered_by_shard_two():
                return 2

            def covered_by_nobody():
                return 3
            """
        ),
        encoding="utf-8",
    )
    (tmp_path / "test_one.py").write_text(
        "import measured\n\ndef test_one():\n    assert measured.covered_by_shard_one() == 1\n",
        encoding="utf-8",
    )
    (tmp_path / "test_two.py").write_text(
        "import measured\n\ndef test_two():\n    assert measured.covered_by_shard_two() == 2\n",
        encoding="utf-8",
    )
    (tmp_path / "pyproject.toml").write_text(
        textwrap.dedent(
            """
            [tool.pytest.ini_options]
            addopts = ["--cov=measured", "--cov-report=term", "--cov-fail-under=90"]

            [tool.coverage.run]
            source = ["."]
            omit = ["test_*.py"]

            [tool.coverage.report]
            fail_under = 90
            """
        ),
        encoding="utf-8",
    )
    shards = (
        Shard(index=0, test_paths=("test_one.py",), cost_seconds=0.1),
        Shard(index=1, test_paths=("test_two.py",), cost_seconds=0.1),
    )
    stream = io.StringIO()
    code = run_tests(
        shards,
        Coverage.FLOOR_90,
        root=str(tmp_path),
        python=sys.executable,
        selection=("test_one.py", "test_two.py"),
        stream=stream,
    )
    body = stream.getvalue()
    # One function is exercised by each shard and one by neither, so the combined total
    # must be below the floor — which is only true if the data was actually combined. A
    # per-shard evaluation would have failed for a different reason, and an uncombined
    # one would report a single shard's coverage as the whole.
    assert code == 1, body
    assert "below the declared floor" in body
    assert (tmp_path / "coverage.xml").is_file(), "the xml report must still be produced"


# --- capability resolution ------------------------------------------------------------


def test_an_owner_below_a_catalogued_capability_resolves_to_it(substrates) -> None:
    """A new subpackage under a known capability is attributed, not escalated."""

    catalogued = next(iter(sorted(substrates.capability_of_owner)))
    assert _capability_location(substrates, catalogued) == catalogued
    assert _capability_location(substrates, f"{catalogued}/a/new/subpackage") == catalogued
    assert _capability_location(substrates, "a-location-nothing-catalogues") is None


def test_the_test_mirror_is_derived_from_the_catalogue_shape() -> None:
    assert _test_mirror("engine/uckp") == "engine/tests/uckp"
    assert _test_mirror("engine") == "engine/tests"
    assert _test_mirror("engine/tests") is None, "a test location has no test mirror"
    assert _test_mirror("engine/tests/uckp") is None


# --- exclusive execution --------------------------------------------------------------


def test_a_declared_isolated_object_runs_alone_and_first(constitution, tests_registry) -> None:
    """Alone because the other shards perturb it; FIRST so it sees the tree as found."""
    isolated = tuple(
        str(entry["prefix"])
        for entry in constitution.sharding.get("isolated") or ()
        if entry.get("prefix")
    )
    if not isolated:
        pytest.skip("no object is declared isolated")
    shards = plan_shards(
        tests_registry.units_for(tests_registry.paths), tests_registry, 8, isolated=isolated
    )
    first_wave = [shard for shard in shards if shard.wave == min(s.wave for s in shards)]
    assert len(first_wave) == 1, "an exclusive wave with two shards is not exclusive"
    assert all(unit_file(unit).startswith(isolated) for unit in first_wave[0].test_paths)
    body = [shard for shard in shards if shard.wave > first_wave[0].wave]
    assert body, "the concurrent body must follow the exclusive wave"
    for shard in body:
        assert not any(unit_file(unit).startswith(isolated) for unit in shard.test_paths)
    assert [shard.index for shard in shards] == list(range(len(shards)))


def test_isolation_changes_the_schedule_and_never_the_scope(tests_registry) -> None:
    """The covered set must be identical whether or not anything is isolated.

    Stated over test OBJECTS rather than over units, because which shard becomes the
    remainder for a split file legitimately depends on the partition — and the remainder
    holds the file where the others hold nodes.
    """
    units = tests_registry.units_for(tests_registry.paths)
    without = plan_shards(units, tests_registry, 8)
    with_isolation = plan_shards(units, tests_registry, 8, isolated=("platform/tests/",))
    covered = lambda shards: sorted(  # noqa: E731
        {unit_file(unit) for shard in shards for unit in shard.test_paths}
    )
    assert covered(without) == covered(with_isolation) == sorted(tests_registry.paths)
    assert any(shard.wave > 0 for shard in with_isolation)


def test_every_declared_isolated_prefix_states_why_it_is_isolated(constitution) -> None:
    """Isolation is expensive, so the bar for adding one is a measurement, not a suspicion."""
    for entry in constitution.sharding.get("isolated") or ():
        assert entry.get("prefix")
        assert entry.get("$measured"), f"{entry.get('prefix')} is isolated without a measurement"


def test_l06_refuses_an_isolation_entry_for_an_object_that_is_not_there(tmp_path) -> None:
    """A stale scheduling exception must fail, not sit inert."""

    def mutate(document):
        document["execution"]["test_sharding"]["isolated"] = [
            {"prefix": "platform/tests/test_a_file_that_was_deleted.py", "$measured": "why"}
        ]

    findings = uvi_gate.selection_is_derived(_ctx(tmp_path, mutate))
    assert any("matches no collectible test object" in f for f in findings)


def test_l06_refuses_an_isolation_entry_with_no_measurement(tmp_path, constitution) -> None:
    def mutate(document):
        for entry in document["execution"]["test_sharding"]["isolated"]:
            entry.pop("$measured", None)

    findings = uvi_gate.selection_is_derived(_ctx(tmp_path, mutate))
    assert any("no measurement justifying it" in f for f in findings)


def test_running_the_tests_leaves_nothing_in_the_repository(tmp_path) -> None:
    """A verification run must not be able to dirty the thing it is verifying."""

    shards = _throwaway_suite(tmp_path)
    before = sorted(os.listdir(tmp_path))
    run_tests(
        shards,
        Coverage.NOT_EVALUATED,
        root=str(tmp_path),
        python=sys.executable,
        selection=("test_alpha.py", "test_beta.py"),
        stream=io.StringIO(),
    )
    left = sorted(set(os.listdir(tmp_path)) - set(before))
    assert not [
        name for name in left if name.startswith("uvi-")
    ], f"the run left working directories behind: {left}"


def test_the_evidence_store_is_excluded_from_the_tracked_tree(constitution) -> None:
    """A cache inside the tree is a second answer to 'did this pass'."""
    ignored = {
        line.strip().rstrip("/")
        for line in open(os.path.join(REPO, ".gitignore"), encoding="utf-8")
        if not line.startswith("#")
    }
    assert constitution.evidence_home.rstrip("/") in ignored


def test_l06_refuses_an_evidence_store_that_would_be_tracked(tmp_path) -> None:
    def mutate(document):
        document["evidence_registry"]["home"] = ".a-store-nothing-ignores/"

    findings = uvi_gate.selection_is_derived(_ctx(tmp_path, mutate))
    assert any("not excluded by .gitignore" in f for f in findings)


def test_the_test_stage_runs_in_a_phase_of_its_own(constitution) -> None:
    """Read-only is not sufficient for concurrency — see the stage's own $phase note."""
    pytest_stage = constitution.stage("pytest")
    others = [s for s in constitution.stages if s.phase == pytest_stage.phase]
    assert others == [pytest_stage], (
        "the suite regenerates derived views and takes the git index lock, so nothing may "
        "read the tree beside it"
    )


def test_the_shards_collect_exactly_the_tests_the_whole_suite_collects() -> None:
    """THE test. Everything else about sharding is an optimisation; this is correctness.

    Every property the plan asserts about itself is asserted at the granularity the plan
    reasons in. This one asks pytest, at the granularity pytest reasons in: collect the
    whole suite, collect every shard, and require the two sets to be equal.

    It is here because the file-level version of this check passed while the run was
    losing tests. A test object above the split threshold is placed as its measured
    nodes, and ``--durations`` hides anything under 0.005s — so 54 tests that were too
    fast to be measured were in no shard at all, and the suite reported 11 706 of 11 760
    as a pass. No amount of reasoning about the cost model would have found that; only
    asking the collector did.
    """

    def _collect(argv: list[str]) -> set[str]:
        # A COLLECTING SUBPROCESS MUST NOT INHERIT THE OUTER MEASUREMENT BOOTSTRAP, AND THE
        # REASON IS A NAME COLLISION THIS REPOSITORY CANNOT AVOID. `platform/` here is a local
        # package that SHADOWS the standard library's `platform`. pytest-cov's `.pth` restarts
        # coverage at interpreter startup in every child the `COV_CORE_*` variables reach, and
        # coverage imports the stdlib `platform` while doing it — so `sys.modules['platform']`
        # is bound to the stdlib module BEFORE the local package can win, and every later
        # `from platform.<anything> import ...` dies with "'platform' is not a package".
        #
        # 340 test modules import the local package, so a child that inherits the bootstrap
        # aborts collection on the first of them: pytest reports `Interrupted: 1 error during
        # collection`, exits 4 and prints NO node ids. This function would then read that empty
        # stdout as "the shard collects nothing" and the assertion below would report thousands
        # of tests as lost — a false alarm about the one property it exists to prove, which is
        # the worst possible failure for a correctness check. It was observed as exactly that:
        # "8360 test(s) are in no shard", while the shards themselves ran and passed in full.
        #
        # Stripping is correct rather than convenient: this subprocess is asked what pytest
        # COLLECTS, and coverage has no part in that answer. The parent's measurement is
        # unaffected — it is still running, and this child was never going to contribute to it.
        result = subprocess.run(  # noqa: S603
            [*argv[: argv.index("-q") + 1], "--collect-only", *argv[argv.index("-q") + 1 :]],
            cwd=REPO,
            capture_output=True,
            text=True,
            check=False,
            env=immutable.clean_environment(),
        )
        return {
            line.strip()
            for line in result.stdout.splitlines()
            if "::" in line and not line.startswith(" ")
        }

    # `-o addopts=` blanks the configured options, and under UCOS-OMEGA-001 that removes the
    # `-p engine.universal_discovery.pytest_scope` entry that DERIVES the collection set. So the
    # plugin is re-supplied explicitly: without it this baseline has neither the derived roots nor
    # a `testpaths` to fall back on, pytest collects the whole rootdir instead, and the gitignored
    # generated tree `realization/tests` contributes 90 tests that no shard can contain — a
    # difference in the BASELINE reported as tests missing from the shards.
    serial = _collect(
        [
            sys.executable,
            "-m",
            "pytest",
            "-o",
            "addopts=",
            "-p",
            "engine.universal_discovery.pytest_scope",
            "--no-cov",
            "-q",
        ]
    )
    assert serial, "the whole suite collected nothing; the comparison would be vacuous"

    plan = build_plan("integration")
    union: set[str] = set()
    placed = 0
    for shard in plan.shards:
        ids = _collect(_shard_argv(sys.executable, shard, Coverage.NOT_EVALUATED))
        placed += len(ids)
        union |= ids

    assert placed == len(union), f"{placed - len(union)} test(s) are collected by two shards"
    assert union == serial, (
        f"{len(serial - union)} test(s) are in no shard and would be silently skipped: "
        f"{sorted(serial - union)[:5]}; {len(union - serial)} are in a shard and not in the suite"
    )


# --- every substrate fails closed ----------------------------------------------------
#
# One shape per substrate. A selector missing one of its graphs must FAULT, because the
# alternative is that it silently reasons from the ones it still has and narrows a run.


def _substrate_fixture(tmp_path, **overrides):
    """A minimal but valid substrate tree, with one surface replaced by the caller."""

    executable_entries = [
        {"path": "a.py", "object_class": "EXECUTABLE_OBJECT", "dependencies": []},
        {
            "path": "engine/tests/test_a.py",
            "object_class": "TEST_OBJECT",
            "owner": "engine/tests",
            "universal_id": "UCOS-TESTOBJ-000001",
            "dependencies": ["a.py"],
            "content_hash": "0" * 64,
        },
    ]
    surfaces = {
        EXECUTABLE_REGISTRY: {"entries": executable_entries},
        # 02 is a superset of 01 in the repository, so the fixture models it as one:
        # the executable objects plus a DOCUMENT_ARTIFACT that 01 never carries.
        UNIVERSAL_REGISTRY: {
            "entries": [
                *executable_entries,
                {
                    "path": "doc/a.md",
                    "object_class": "DOCUMENT_ARTIFACT",
                    "owner": "doc",
                    "universal_id": "UCOS-EXDOC-000001",
                    "content_hash": "1" * 64,
                },
            ]
        },
        RELATIONSHIP_GRAPH: {"relationships": [{"from": "UCOS-TESTOBJ-000001", "to": "a.py"}]},
        CAPABILITY_CATALOG: {
            "capabilities": [{"canonical_location": "engine", "canonical_name": "engine"}]
        },
    }
    surfaces.update(overrides)
    for name, document in surfaces.items():
        target = tmp_path / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(document), encoding="utf-8")
    (tmp_path / "pyproject.toml").write_text("[tool.ucos]\n", encoding="utf-8")

    # THE COLLECTION SET IS NOW DERIVED, so this fixture must give the derivation something to
    # derive FROM. It used to declare `testpaths = ["engine/tests"]` and that was enough, because
    # `collection_roots` read the list. Under UCOS-OMEGA-001 there is no list: the roots come from
    # which directories hold suites in the TRACKED population, so the fixture writes a real test
    # module and initialises a real git repository. That is the same boundary the gate uses, and a
    # fixture that skipped git would exercise a path the gate never takes.
    suite = tmp_path / "engine" / "tests"
    suite.mkdir(parents=True, exist_ok=True)
    (suite / "test_a.py").write_text("def test_a():\n    pass\n", encoding="utf-8")
    (tmp_path / "a.py").write_text("VALUE = 1\n", encoding="utf-8")
    # A source package, so the derivation has a non-empty denominator. A repository with a suite and
    # no measurable source is refused by Ω-1 as "a number about nothing", which is correct for a
    # repository and wrong for a fixture claiming to be a VALID substrate tree.
    core = tmp_path / "engine" / "core"
    core.mkdir(parents=True, exist_ok=True)
    (core / "mod.py").write_text("def run():\n    return 1\n", encoding="utf-8")
    subprocess.run(  # noqa: S603 - fixed argv, no shell
        ["git", "init", "-q"],  # noqa: S607 - git from PATH by design
        cwd=tmp_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(  # noqa: S603
        ["git", "add", "-A"],  # noqa: S607
        cwd=tmp_path,
        check=True,
        capture_output=True,
    )
    # The derivation memoises per root. Each fixture gets a fresh tmp_path so the key differs, but
    # clearing is cheap and makes the fixture independent of that fact.
    clear_derived_scope_cache()
    return tmp_path


def test_a_valid_substrate_tree_loads(tmp_path) -> None:
    """The control. Without it the refusals below could pass for the wrong reason."""
    root = _substrate_fixture(tmp_path)
    substrates = load_substrates(str(root))
    assert substrates.capability_of_owner == {"engine": "engine"}
    assert substrates.related_identities({"UCOS-TESTOBJ-000001"}) == {"a.py"}
    registry = build_test_registry(substrates, str(root))
    assert registry.paths == ("engine/tests/test_a.py",)


@pytest.mark.parametrize(
    ("surface", "document", "message"),
    [
        ("RELATIONSHIP_GRAPH", {"relationships": []}, "no relationships"),
        ("RELATIONSHIP_GRAPH", {"relationships": "not-a-list"}, "no relationships"),
        ("CAPABILITY_CATALOG", {"capabilities": []}, "no capabilities"),
        ("CAPABILITY_CATALOG", {"nothing": True}, "no capabilities"),
    ],
)
def test_an_unusable_substrate_is_a_fault(surface, document, message, tmp_path) -> None:
    root = _substrate_fixture(tmp_path, **{getattr(registry_module, surface): document})
    with pytest.raises(VerificationIntelligenceError, match=message):
        load_substrates(str(root))


def test_a_surface_that_is_not_an_object_is_a_fault(tmp_path) -> None:
    root = _substrate_fixture(tmp_path)
    (root / EXECUTABLE_REGISTRY).write_text("[]", encoding="utf-8")
    with pytest.raises(VerificationIntelligenceError, match="not an object"):
        load_substrates(str(root))


def test_malformed_entries_are_skipped_rather_than_crashing(tmp_path) -> None:
    """A surface may carry a row this engine does not understand; it may not carry none."""

    root = _substrate_fixture(
        tmp_path,
        **{
            EXECUTABLE_REGISTRY: {
                "entries": [
                    "not-a-dict",
                    {"no_path": True},
                    {
                        "path": "engine/tests/test_a.py",
                        "object_class": "TEST_OBJECT",
                        "owner": "engine/tests",
                        "dependencies": ["a.py"],
                    },
                ]
            },
            RELATIONSHIP_GRAPH: {
                "relationships": ["not-a-dict", {"from": "", "to": ""}, {"from": "x", "to": "y"}]
            },
            CAPABILITY_CATALOG: {
                "capabilities": [
                    "not-a-dict",
                    {"canonical_location": ""},
                    {"canonical_location": "engine"},
                ]
            },
        },
    )
    substrates = load_substrates(str(root))
    assert set(substrates.objects) == {"engine/tests/test_a.py"}
    assert substrates.capability_of_owner == {"engine": "engine"}


def test_a_moved_suite_is_still_collected_rather_than_silently_dropped(tmp_path) -> None:
    """FAIL WIDE, re-asserted after the collection set became derived.

    The premise of the original test is now unreachable, and that is an improvement worth stating.
    It wrote ``testpaths = ["somewhere/else"]`` and expected "no collectible test object" — a
    registry projecting nothing because the declared root did not exist. Under UCOS-OMEGA-001 the
    roots are DERIVED FROM the test files themselves, so a discovered root always contains at least
    one collectible module and "points at nothing" is not a state a declaration can produce.

    What must still hold is the law that mattered: a test the registry does not know about is
    ADMITTED as unregistered, never dropped. So the suite is moved out from under its registry entry
    and the registry must contain the moved file and not the stale one.
    """
    root = _substrate_fixture(tmp_path)
    moved = root / "elsewhere" / "checks"
    moved.mkdir(parents=True, exist_ok=True)
    (moved / "test_a.py").write_text("def test_a():\n    pass\n", encoding="utf-8")
    (root / "engine" / "tests" / "test_a.py").unlink()
    subprocess.run(  # noqa: S603
        ["git", "add", "-A"],  # noqa: S607
        cwd=root,
        check=True,
        capture_output=True,
    )
    clear_derived_scope_cache()
    assert collection_roots(str(root)) == (
        "elsewhere",
    ), "the suite moved and discovery did not follow it, so this test proves nothing"

    registry = build_test_registry(load_substrates(str(root)), str(root))
    assert (
        "elsewhere/checks/test_a.py" in registry.paths
    ), "the moved test was dropped from the run, which is the defect FAIL WIDE exists to prevent"
    assert (
        "engine/tests/test_a.py" not in registry.paths
    ), "a registry entry for a file that no longer exists was projected as collectible"
    assert (
        "elsewhere/checks/test_a.py" in registry.unregistered
    ), "the moved test carries a registration it never received"


def test_a_registry_that_projects_nothing_is_still_a_fault(tmp_path, monkeypatch) -> None:
    """The refusal above must remain REACHABLE, or removing it would cost nothing.

    Discovery can no longer produce a root that holds no test module, so the branch is driven
    directly: a root that does not exist yields no collectible object and the projection must fault
    rather than return an empty run.
    """
    root = _substrate_fixture(tmp_path)

    monkeypatch.setattr(registry_module, "collection_roots", lambda _root=None: ("nowhere/at/all",))
    with pytest.raises(VerificationIntelligenceError, match="no collectible test object"):
        build_test_registry(load_substrates(str(root)), str(root))


def test_an_unreadable_declaration_is_a_fault(tmp_path) -> None:
    """A malformed ``pyproject.toml`` is a FAULT, never a default.

    The declared inputs Ω-1 still reads from that file — the exemption register and the coverage
    floor — are judgements, and an unparseable judgement must not silently become "no exemptions".
    """
    root = _substrate_fixture(tmp_path)
    (root / "pyproject.toml").write_text("[tool.pytest\n", encoding="utf-8")
    clear_derived_scope_cache()
    with pytest.raises(VerificationIntelligenceError, match="unreadable|could not be derived"):
        collection_roots(str(root))


def test_total_cost_prices_the_whole_suite_by_default(tests_registry) -> None:
    assert tests_registry.total_cost() == pytest.approx(
        tests_registry.total_cost(tests_registry.paths)
    )
    assert tests_registry.total_cost(()) == 0


# --------------------------------------------------------------------------------
# UVI-L-15 — non-reuse is argued, and law identities are unique.
#
# constitution.py refuses a stage declared REUSABLE that names no read-set, because its
# cache key would cover nothing and every run would be a false hit. Nothing refused the
# mirror omission, and six stages were non-reusable with no recorded reason — paying full
# cost on every run for an argument nobody had made.
# --------------------------------------------------------------------------------
def _declaration() -> dict:
    """The live declaration, read through the loader that owns its location."""

    return load_declaration()


def _stages(document: dict) -> list[dict]:
    registry = document["stage_registry"]
    return registry["stages"] if isinstance(registry, dict) else registry


def _write(tmp_path, document: dict) -> str:
    path = tmp_path / "forged.json"
    path.write_text(json.dumps(document), encoding="utf-8")
    return str(path)


def test_every_non_reusable_stage_records_a_reason() -> None:
    """The live declaration, held to its own law."""
    findings = uvi_gate.non_reuse_is_argued(type("Ctx", (), {"document": _declaration()})())
    assert list(findings) == []


def test_a_non_reusable_stage_with_no_reason_is_refused() -> None:
    document = _declaration()
    for stage in _stages(document):
        if not stage.get("reusable"):
            stage.pop("$not_reusable", None)
            break
    findings = list(uvi_gate.non_reuse_is_argued(type("Ctx", (), {"document": document})()))
    assert findings and "records no reason" in findings[0]


def test_a_law_over_no_non_reusable_stage_would_be_vacuous() -> None:
    """Every stage reusable means this law measured nothing, which is not the same as holding."""
    document = _declaration()
    for stage in _stages(document):
        stage["reusable"] = True
    findings = list(uvi_gate.non_reuse_is_argued(type("Ctx", (), {"document": document})()))
    assert findings and "measured nothing" in findings[0]


def test_a_duplicate_law_id_is_refused_at_load(tmp_path) -> None:
    """A shadowed verdict, accepted silently until it was forged.

    Adding a law that reused an existing id produced a report reading "15/15 laws hold" over
    fourteen distinct ids: two obligations answering to one name, so a reader auditing the
    verdict for that id could be shown either one.
    """
    document = _declaration()
    document["laws"][-1]["id"] = document["laws"][0]["id"]
    with pytest.raises(VerificationIntelligenceError, match="declared more than once"):
        load_constitution(_write(tmp_path, document))


def test_the_live_declaration_has_unique_law_ids() -> None:
    ids = [law["id"] for law in _declaration()["laws"]]
    assert len(ids) == len(set(ids))


# --- cross-job sharding: one shard is a JOB rather than a process ------------------------
#
# The properties below hold for free inside one process and stop holding the moment a shard
# becomes a job, because a job sees its neighbours' ARTIFACTS and never their exit codes.


def test_only_executes_exactly_one_shard_of_the_plan(tmp_path) -> None:
    shards = _throwaway_suite(tmp_path)
    stream = io.StringIO()
    code = run_tests(
        shards,
        Coverage.NOT_EVALUATED,
        root=str(tmp_path),
        python=sys.executable,
        selection=("test_alpha.py", "test_beta.py"),
        stream=stream,
        only=1,
    )
    body = stream.getvalue()
    assert code == 0
    assert "shard 1" in body
    assert "shard 0" not in body
    # The whole plan is still proved before the narrowing, so a job that cannot prove the
    # partition whole does not run its part of it.
    assert "1 shard(s) running concurrently" in body


def test_a_shard_index_the_plan_does_not_contain_is_refused(tmp_path) -> None:
    shards = _throwaway_suite(tmp_path)
    stream = io.StringIO()
    code = run_tests(
        shards,
        Coverage.NOT_EVALUATED,
        root=str(tmp_path),
        python=sys.executable,
        selection=("test_alpha.py", "test_beta.py"),
        stream=stream,
        only=2,
    )
    # `plan_shards` returns one shard per worker PLUS one per isolated wave, so a matrix
    # built from the worker count addresses one fewer shard than the plan holds. That loss
    # is silent — every job's topology proof passes, because it measures the plan and not
    # what was executed — so the index itself has to be refused.
    assert code == 2
    assert "not in this plan" in stream.getvalue()


def test_one_shard_under_the_floor_must_be_given_somewhere_to_leave_its_data(tmp_path) -> None:
    shards = _throwaway_suite(tmp_path)
    stream = io.StringIO()
    code = run_tests(
        shards,
        Coverage.FLOOR_90,
        root=str(tmp_path),
        python=sys.executable,
        selection=("test_alpha.py", "test_beta.py"),
        stream=stream,
        only=0,
    )
    assert code == 2
    assert "partial data and no verdict" in stream.getvalue()


def test_shard_data_is_named_by_the_index_that_produced_it(tmp_path) -> None:
    produced = tmp_path / "produced"
    produced.mkdir()
    (produced / ".coverage.7").write_text("data", encoding="utf-8")
    out = tmp_path / "exported"
    assert _export_shard_data(str(produced), 7, str(out), io.StringIO()) == 0
    # The combine's fails-closed question is "which shards arrived", and only a name that
    # carries the shard's identity can answer it.
    assert shard_indices_present(str(out)) == (7,)


def test_a_shard_that_measured_nothing_does_not_export_silence(tmp_path) -> None:
    empty = tmp_path / "produced"
    empty.mkdir()
    stream = io.StringIO()
    assert _export_shard_data(str(empty), 3, str(tmp_path / "out"), stream) == 1
    assert "produced no coverage data" in stream.getvalue()


def test_combine_refuses_when_a_shard_left_no_data(tmp_path) -> None:
    data = tmp_path / "data"
    data.mkdir()
    (data / ".coverage.shard-0").write_text("x", encoding="utf-8")
    stream = io.StringIO()
    # In one process a shard that dies before writing data also exits non-zero, so the run
    # is already failing. A combine job has no such backstop: a cancelled or skipped job is
    # indistinguishable from one that measured nothing, and the floor would be reported
    # over the fragment that arrived.
    assert combine_shards((0, 1, 2), str(data), root=str(tmp_path), stream=stream) == 1
    body = stream.getvalue()
    assert "left no coverage data: [1, 2]" in body
    assert "Refusing" in body


def test_combine_refuses_data_from_a_shard_the_plan_does_not_contain(tmp_path) -> None:
    data = tmp_path / "data"
    data.mkdir()
    for index in (0, 1, 9):
        (data / f".coverage.shard-{index}").write_text("x", encoding="utf-8")
    stream = io.StringIO()
    assert combine_shards((0, 1), str(data), root=str(tmp_path), stream=stream) == 1
    assert "does not contain" in stream.getvalue()


def test_combine_refuses_when_no_shard_was_expected(tmp_path) -> None:
    stream = io.StringIO()
    assert combine_shards((), str(tmp_path), root=str(tmp_path), stream=stream) == 1
    assert "no shard was expected" in stream.getvalue()


def test_combine_refuses_a_data_directory_that_is_not_there(tmp_path) -> None:
    stream = io.StringIO()
    missing = tmp_path / "never-downloaded"
    assert combine_shards((0,), str(missing), root=str(tmp_path), stream=stream) == 1
    assert "no coverage data directory" in stream.getvalue()


def test_a_whole_suite_plan_may_be_sharded_and_an_impact_plan_may_not() -> None:
    # An impact selection is derived from the diff, so two runners with different fetch
    # depths would partition different suites while each proved its own plan whole.
    assert build_plan("full").selection_is_impact is False
    assert build_plan("change").selection_is_impact is True


def test_the_ci_matrix_is_built_from_the_plan_and_not_from_the_worker_count() -> None:
    """The addressing defect would live in the workflow, so it is guarded there.

    `plan_shards` returns one shard per worker PLUS one per isolated wave. A matrix built
    from the worker count therefore addresses `range(workers)` and never names the last
    shard, whose tests then run nowhere — while every job's topology proof still passes,
    because that proof measures the plan and not what was executed. Nothing inside the
    engine can catch that; only the workflow can be wrong in this particular way.
    """
    workflow = os.path.join(uvi_gate.repo_root(), ".github", "workflows", "ec1-ci.yml")
    with open(workflow, encoding="utf-8") as handle:
        text = handle.read()

    # The matrix comes from the plan's own shard indices.
    assert "shard: ${{ fromJSON(needs.plan.outputs.shards) }}" in text

    # AND THAT PLAN IS BUILT BY THE CLI, NOT BY THE WORKFLOW. `workers_override` is an
    # explicit parameter that `build_plan` never reads from the environment, so a step that
    # constructs its own plan silently resolves workers from os.cpu_count() while every
    # shard job, going through the CLI, reads UVI_WORKERS -- and the matrix is then built
    # from one plan and executed against another. That is not hypothetical: it is what this
    # workflow did on its first run, and only the digest guard turned it into a red run
    # rather than a green one missing eight shards' tests.
    assert "plan --mode full --json" in text
    assert "plan --mode full --digest" in text
    # Stated as "imports no plan constructor" rather than "does not mention build_plan",
    # because the step's own comment names build_plan while explaining why it must not call
    # it, and an assertion that cannot tell prose from code would forbid the explanation.
    assert (
        "verification_intelligence.plan import" not in text
    ), "the workflow must not construct a plan of its own"

    # The topology is declared rather than inherited from whichever runner was allocated,
    # so the plan job and the shard jobs cannot partition differently.
    assert 'UVI_WORKERS: "12"' in text

    # The data files begin with a dot and upload-artifact has excluded dotfiles since
    # v4.4; without this the artifact uploads empty and combine refuses a shard that
    # actually measured everything asked of it.
    assert "include-hidden-files: true" in text

    # The floor is evaluated once, by a job that fails closed on a missing shard.
    assert "engine.verification_intelligence combine" in text
    assert "--plan-digest" in text
    # A sharded job must not also evaluate the floor itself.
    assert "UVI_SHARD: ${{ matrix.shard }}" in text


def test_a_sharded_run_records_no_stage_evidence() -> None:
    """Evidence is keyed by stage label and input digest, and neither knows about shards.

    A job that ran one shard and exited 0 would otherwise record PASS against the SAME key
    a whole-suite run writes, for the coverage stage, having evaluated no floor at all — and
    a later --change or --fast run may reuse a stored PASS.
    """
    with open(os.path.join(uvi_gate.repo_root(), "verify.sh"), encoding="utf-8") as handle:
        text = handle.read()
    guard = text.index('if [ -n "${UVI_SHARD:-}" ]; then\n    return 0')
    record = text.index("-m engine.verification_intelligence record")
    assert guard < record, "the sharded-run guard must precede the evidence write"


# --- the entry point, the accessors and the branches a healthy repository never takes ---


def test_the_module_entry_point_dispatches_to_the_cli(monkeypatch) -> None:
    """``python -m engine.verification_intelligence`` is a second entry point, and a dispatcher
    rather than a copy. If it stopped reaching ``cli.main`` the two would drift silently — the
    module runs, exits 0, and verifies nothing."""

    calls: list[int] = []
    monkeypatch.setattr(cli, "main", lambda: calls.append(1) or 0)
    with pytest.raises(SystemExit) as exit_info:
        runpy.run_module("engine.verification_intelligence", run_name="__main__")
    assert exit_info.value.code == 0
    assert calls == [1]


def test_a_contract_mode_runs_the_whole_declared_contract(constitution) -> None:
    """``is_contract`` is what separates a mode that runs the declared stage contract from one
    that names a subset. A mode that answered wrongly would run a subset under a contract label."""
    modes = {mode.mode_id: mode.is_contract for mode in constitution.modes}
    assert any(modes.values()), "no declared mode runs the whole contract"
    assert not all(modes.values()), "no declared mode runs a subset"


def test_a_priced_test_object_is_distinguishable_from_a_defaulted_one(tests_registry) -> None:
    """`is_priced` decides whether the packer is placing a measurement or a default. Reading it
    the same way for both would make an unmeasured object look like a cheap one."""
    priced = [obj for obj in tests_registry.objects.values() if obj.is_priced]
    unpriced = [obj for obj in tests_registry.objects.values() if not obj.is_priced]
    assert priced, "the registry prices nothing"
    assert all(obj.cost_seconds > 0 for obj in priced)
    assert all(obj.cost_seconds <= 0 for obj in unpriced)


def test_the_declaration_names_every_mode_and_resolves_its_default(constitution) -> None:
    """`mode_ids` and `default_mode` are how every caller reaches a mode by name. A default that
    did not resolve would be a verification with no mode at all."""
    assert constitution.default_mode_id in constitution.mode_ids
    assert constitution.default_mode.mode_id == constitution.default_mode_id


def test_a_declaration_field_that_is_not_a_list_refuses_to_construct(tmp_path) -> None:
    """A scalar where a list belongs would be iterated character by character, producing a
    vocabulary of single letters that every later check would compare against and pass."""
    document = load_declaration()
    document["stage_registry"]["stages"][0]["reuse_inputs"] = "00-BOOK/"
    path = tmp_path / "declaration.json"
    path.write_text(json.dumps(document), encoding="utf-8")
    with pytest.raises(VerificationIntelligenceError, match="expected a list"):
        load_constitution(str(path), checks=frozenset(uvi_gate.CHECKS))


def test_the_evidence_home_is_resolved_under_the_declared_store(constitution) -> None:
    """The plan reports where a reusable result would be read from. A home nobody can name is a
    cache nobody can inspect, clear or audit."""

    assert evidence_home(constitution, REPO).startswith(REPO)


def test_a_plan_whose_split_table_says_nothing_carries_no_currency_note(
    monkeypatch, substrates, tests_registry, constitution
) -> None:
    """A repository with no cost model has no split table, and a note saying `0/0 current` would
    be a line about nothing on every plan such a repository ever renders."""

    monkeypatch.setattr(plan_module, "split_currency", lambda registry: "")
    built = build_plan(
        constitution=constitution,
        mode_id="fast",
        substrates=substrates,
        tests=tests_registry,
        root=REPO,
    )
    assert not [note for note in built.notes if "split table" in note]


# --- the substrates' remaining refusals ------------------------------------------------


def test_a_universal_registry_holding_no_entries_is_refused(tmp_path) -> None:
    """02 is the registry the identity layer reads. Empty, every identity resolves to nothing and
    the identity layer of selection silently contributes no objects."""

    root = _substrate_fixture(tmp_path, **{UNIVERSAL_REGISTRY: {"entries": []}})
    with pytest.raises(VerificationIntelligenceError, match="no entries"):
        load_substrates(str(root))


def test_a_universal_entry_with_no_path_is_skipped_rather_than_crashing(tmp_path) -> None:
    """A published surface may carry a row this engine does not understand. It may not carry
    none, and it may not take the selector down."""

    root = _substrate_fixture(tmp_path)
    document = json.loads((root / UNIVERSAL_REGISTRY).read_text(encoding="utf-8"))
    document["entries"] = ["not-a-dict", {"no-path": True}, *document["entries"]]
    (root / UNIVERSAL_REGISTRY).write_text(json.dumps(document), encoding="utf-8")
    substrates = load_substrates(str(root))
    assert "a.py" in substrates.objects
    assert (root / EXECUTABLE_REGISTRY).exists()


def test_a_discovery_that_returns_no_test_root_is_refused(tmp_path, monkeypatch) -> None:
    """Discovery raising and discovery returning nothing are different failures. The second is
    the more dangerous one: it is a well-formed answer meaning "collect nothing"."""

    monkeypatch.setattr(discovery_module, "derived_scope", lambda base: ((), (), (), ()))
    with pytest.raises(VerificationIntelligenceError, match="no test root"):
        collection_roots(str(tmp_path))


# --- the evidence store's non-hits -----------------------------------------------------


def test_a_stage_whose_execution_contract_is_unresolvable_takes_no_key(constitution, substrates):
    """The key is taken over the declared inputs AND the argv the stage is invoked with. Taking
    it over the inputs alone would produce a hit across two different invocations of one stage."""
    stage = next(s for s in constitution.stages if s.reusable and s.reads)
    assert input_digest(stage, substrates, contract=None) is None


def test_an_entry_written_by_another_schema_is_not_a_hit(tmp_path) -> None:
    """A cache is only safe while the reader and the writer agree on what an entry means. An
    unrecognised schema must read as a miss, never as a pass."""
    home = str(tmp_path)
    record(home, "stage-x", "c" * 64, "PASS")
    target = tmp_path / "stage-x" / f"{'c' * 64}.json"
    document = json.loads(target.read_text(encoding="utf-8"))
    document["schema"] = "some-other-schema"
    target.write_text(json.dumps(document), encoding="utf-8")
    assert lookup(home, "stage-x", "c" * 64) is None


def test_an_entry_filed_under_a_key_it_does_not_carry_is_not_a_hit(tmp_path) -> None:
    """The key is in the path AND in the body. Trusting the path alone would make a moved or
    copied entry answer for an input it was never measured against."""
    home = str(tmp_path)
    record(home, "stage-x", "d" * 64, "PASS")
    target = tmp_path / "stage-x" / f"{'d' * 64}.json"
    document = json.loads(target.read_text(encoding="utf-8"))
    document["input_digest"] = "e" * 64
    target.write_text(json.dumps(document), encoding="utf-8")
    assert lookup(home, "stage-x", "d" * 64) is None


def test_a_stage_that_produces_no_key_is_executed_rather_than_reused(
    constitution, substrates, tmp_path, monkeypatch
) -> None:
    """No key means nothing to look the result up by. Reusing on that basis would be reusing on
    the basis of the stage's name, which every input change leaves unchanged."""

    mode = next(m for m in constitution.modes if m.evidence_reuse)
    stage = next(s for s in constitution.stages if s.reusable and s.reads)
    monkeypatch.setattr(evidence, "input_digest", lambda *a, **k: None)
    reuse, reason, digest = decide(mode, stage, substrates, home=str(tmp_path), root=REPO)
    assert reuse is False
    assert digest is None
    assert "no input digest" in reason


# --- the selection layers that a healthy catalogue never reaches ------------------------


def test_every_unbounded_prefix_is_reported_as_one_set(substrates, tests_registry) -> None:
    """The two families — what no graph can bound, and the selector's own surfaces — are declared
    separately and must be READABLE as one, or a caller checking "is this bounded" checks half."""

    combined = unbounded_prefixes()
    assert set(combined) == set(UNBOUNDED_PREFIXES) | set(SELF_PREFIXES)
    assert list(combined) == sorted(combined)


def test_an_unreadable_impact_graph_is_a_fault_and_never_a_narrow_selection(
    substrates, tests_registry, monkeypatch
) -> None:
    """Every caller resolves a fault to the whole suite. Letting the ImpactError through as its
    own type would reach a caller that does not know to widen for it."""

    def refusing(root=None):
        raise ImpactError("the relationship graph cannot be read")

    monkeypatch.setattr(selection_module, "load_graph", refusing)
    with pytest.raises(VerificationIntelligenceError, match="cannot be read"):
        select(("engine/uaue/gate.py",), substrates=substrates, tests=tests_registry)


def test_a_change_whose_owner_the_catalogue_does_not_know_widens(
    substrates, tests_registry, monkeypatch
) -> None:
    """The capability layer is what bounds a blast radius beyond the import graph. An owner the
    catalogue has never heard of has no radius this engine can compute, and the only honest
    answer for a thing it cannot bound is the whole suite."""

    monkeypatch.setattr(selection_module, "_capability_location", lambda substrates, owner: None)
    result = select(("engine/uaue/gate.py",), substrates=substrates, tests=tests_registry)
    assert result.selection is Selection.WHOLE_SUITE
    assert any("capability catalogue" in reason for reason in result.escalations)


def test_a_change_whose_capability_has_a_catalogued_test_mirror_reaches_it(
    substrates, tests_registry
) -> None:
    """`engine/uckp` and `engine/tests/uckp` are both catalogued, and the mirror is derived from
    that vocabulary rather than mapped by hand. A mirror that resolved and was not traversed
    would leave a capability's own tests out of its blast radius."""
    result = select(("engine/uckp/law.py",), substrates=substrates, tests=tests_registry)
    assert result.selection is Selection.IMPACT
    assert any(path.startswith("engine/tests/uckp/") for path in result.test_paths)


def test_a_bounded_change_reaching_no_test_widens_rather_than_verifying_nothing(
    substrates, tests_registry
) -> None:
    """Not "nothing to verify" — code that nothing exercises. That is a coverage question, and
    reading it as a licence to skip is the one failure this whole engine exists to refuse."""

    empty = TestObjectRegistry(roots=tests_registry.roots)
    result = select(("engine/uaue/gate.py",), substrates=substrates, tests=empty)
    assert result.selection is Selection.WHOLE_SUITE
    assert result.test_paths == ()


def test_a_split_entry_carrying_no_nodes_is_placed_whole(substrates, monkeypatch) -> None:
    """A current hash and an empty node list is a table that says "divisible" and names no
    division. Registering the object as splittable on that basis would produce a shard plan
    referring to nodes nobody measured."""

    real = registry_module.load_cost_model

    def _empty_nodes(root=None):
        costs, split, threshold = real(root)
        for entry in split.values():
            entry["nodes"] = {}
        return costs, split, threshold

    monkeypatch.setattr(registry_module, "load_cost_model", _empty_nodes)
    projected = registry_module.build_test_registry(substrates)
    assert projected.splittable == {}


def test_a_node_priced_with_something_that_is_not_a_number_is_not_priced(
    substrates, monkeypatch
) -> None:
    """The object is still splittable — the node ids are current — but a node whose price is not
    a number contributes no cost. Coercing it would put an invented number into the packer."""

    real = registry_module.load_cost_model

    def _unpriced_nodes(root=None):
        costs, split, threshold = real(root)
        for entry in split.values():
            entry["nodes"] = dict.fromkeys(entry["nodes"], "not-a-number")
        return costs, split, threshold

    monkeypatch.setattr(registry_module, "load_cost_model", _unpriced_nodes)
    projected = registry_module.build_test_registry(substrates)
    assert projected.splittable, "the objects stopped being splittable, so nothing was measured"
    assert projected.node_costs == {}


# --- sharding arithmetic, and the guards behind the guards ------------------------------


def test_a_registry_with_no_split_table_says_nothing_rather_than_zero_of_zero(
    tests_registry,
) -> None:
    """`0/0 current` on every plan a repository without a cost model renders would be a line
    about nothing, printed forever."""

    assert split_currency(TestObjectRegistry()) == ""


def test_a_split_table_with_nothing_stale_reports_only_what_it_can_use(tests_registry) -> None:
    """The stale clause is appended, not substituted. A currency line that named stale objects
    unconditionally would say `— stale, placed whole:` with nothing after it."""

    current = TestObjectRegistry(splittable={"a/test_x.py": ("a/test_x.py::one",)})
    line = split_currency(current)
    assert line == "UVI: split table 1/1 current"


def test_a_shard_plan_over_no_test_object_is_empty_rather_than_a_worker_of_nothing(
    tests_registry,
) -> None:
    """A selection that reaches nothing must produce no shard. One empty shard per worker would
    spawn processes to run nothing and report their success as the suite's."""
    assert plan_shards((), tests_registry, 4) == ()


def test_a_split_file_with_no_remainder_shard_anywhere_is_refused() -> None:
    """The deselects match the placements and the file is still nowhere whole, so the tests the
    cost model never saw — everything under 0.005s — would run in no shard at all."""
    shards = (
        Shard(
            index=0,
            test_paths=("a/test_y.py",),
            cost_seconds=1.0,
            deselect=("a/test_x.py::one",),
        ),
        Shard(index=1, test_paths=("a/test_x.py::one",), cost_seconds=1.0),
    )
    with pytest.raises(VerificationIntelligenceError, match="no remainder shard"):
        assert_topology_neutral(shards, ("a/test_x.py", "a/test_y.py"))


def test_the_whole_file_guard_still_fires_when_the_unit_guard_is_disabled(monkeypatch) -> None:
    """Defence in depth, measured by removing the first line of it.

    A file placed whole in two shards is ALSO a unit placed twice, so the duplicate-unit check
    above catches it first and this guard has never run. That is what makes it worth holding:
    the two checks say different things — one about units, one about test objects — and if the
    first is ever narrowed the second must still refuse. Neutralising the first check's
    set-comparison is the only way to ask the second whether it works.
    """

    monkeypatch.setattr(execution_module, "set", list, raising=False)
    shards = (
        Shard(index=0, test_paths=("a/test_x.py",), cost_seconds=1.0),
        Shard(index=1, test_paths=("a/test_x.py",), cost_seconds=1.0),
    )
    with pytest.raises(VerificationIntelligenceError, match="whole in more than one shard"):
        assert_topology_neutral(shards, ("a/test_x.py",))


def test_a_shard_whose_process_reports_no_stdout_is_still_reaped(tmp_path, monkeypatch) -> None:
    """`Popen` returns ``stdout=None`` whenever the caller redirects to a real file rather than
    to a pipe, which is exactly what this runner does — the handle is re-attached by hand purely
    so it can be closed. A shard whose process does not carry it must still be waited on and
    still have its log read, or a removed line of bookkeeping would turn into a leaked handle."""

    real_popen = subprocess.Popen

    class _NoStdout(real_popen):  # type: ignore[misc,valid-type]
        @property
        def stdout(self):
            return None

        @stdout.setter
        def stdout(self, value):
            pass

    monkeypatch.setattr(execution_module.subprocess, "Popen", _NoStdout)
    shards = _throwaway_suite(tmp_path)
    stream = io.StringIO()
    code = run_tests(
        shards,
        Coverage.NOT_EVALUATED,
        root=str(tmp_path),
        python=sys.executable,
        selection=("test_alpha.py", "test_beta.py"),
        stream=stream,
    )
    assert code == 0
    assert "shard 0" in stream.getvalue()


def test_a_single_shard_under_the_floor_exports_its_data_instead_of_judging(tmp_path) -> None:
    """A shard has measured one thirteenth of the suite. The floor is a property of the whole,
    so the shard leaves its data where the combine job can collect it and computes no verdict."""

    shards = _throwaway_suite(tmp_path)
    exported = tmp_path / "exported"
    stream = io.StringIO()
    code = run_tests(
        shards,
        Coverage.FLOOR_90,
        root=str(tmp_path),
        python=sys.executable,
        selection=("test_alpha.py", "test_beta.py"),
        stream=stream,
        only=0,
        coverage_out=str(exported),
    )
    body = stream.getvalue()
    assert "the floor is not evaluated by a shard" in body or "no coverage data" in body
    assert code in (0, 1)


def _canned_coverage(monkeypatch, results):
    """Drive ``_combine_and_evaluate``'s three subprocesses from a script.

    The alternative is producing real coverage data whose combine, xml and report steps fail on
    demand, which measures the coverage tool rather than this function's handling of it.
    """

    calls: list[list[str]] = []
    scripted = iter(results)

    def fake(argv, **kwargs):
        calls.append(list(argv))
        returncode, stdout, stderr = next(scripted)
        return subprocess.CompletedProcess(argv, returncode, stdout, stderr)

    monkeypatch.setattr(execution_module.subprocess, "run", fake)
    return calls


def _with_shard_data(tmp_path):
    data = tmp_path / "data"
    data.mkdir()
    (data / ".coverage.shard-0.0").write_text("not real coverage data", encoding="utf-8")
    return data


def test_a_combine_that_fails_refuses_rather_than_reporting_a_floor(tmp_path, monkeypatch):
    """Unusable shard data is not a low number; it is no number, and a floor computed over what
    happened to combine would be a verdict over a suite fragment."""

    _canned_coverage(monkeypatch, [(1, "", "cannot combine")])
    stream = io.StringIO()
    data = _with_shard_data(tmp_path)
    assert _combine_and_evaluate(sys.executable, str(tmp_path), str(data), stream) == 1
    assert "coverage combine failed" in stream.getvalue()


def test_an_xml_step_that_fails_refuses_rather_than_reporting_a_floor(tmp_path, monkeypatch):
    """The artifact and the verdict are separate obligations, and an unwritten artifact must not
    be reported as a met floor."""

    _canned_coverage(monkeypatch, [(0, "", ""), (1, "", "cannot write xml")])
    stream = io.StringIO()
    data = _with_shard_data(tmp_path)
    assert _combine_and_evaluate(sys.executable, str(tmp_path), str(data), stream) == 1
    assert "coverage xml failed" in stream.getvalue()


def test_a_met_floor_returns_zero_and_relays_what_the_tool_said(tmp_path, monkeypatch):
    """The success path, and the tool's stderr with it: a warning the coverage tool emits while
    still succeeding is the only notice that the measurement was partial, and swallowing it
    would make the one line worth reading the one line nobody sees."""

    calls = _canned_coverage(
        monkeypatch,
        [(0, "", ""), (0, "", ""), (0, "TOTAL   100%", "CoverageWarning: a module was skipped")],
    )
    stream = io.StringIO()
    data = _with_shard_data(tmp_path)
    assert _combine_and_evaluate(sys.executable, str(tmp_path), str(data), stream) == 0
    body = stream.getvalue()
    assert "TOTAL   100%" in body
    assert "CoverageWarning" in body
    assert (
        calls[1][-1] == "--fail-under=0"
    ), "the xml step must not evaluate the floor a second time"


def test_a_file_that_is_not_shard_data_is_not_read_as_a_shard(tmp_path) -> None:
    """The combine's fails-closed question is "which shards arrived", asked of file names. A name
    that does not carry a shard index answers it with nothing rather than with a guess."""

    data = tmp_path / "data"
    data.mkdir()
    (data / ".coverage.shard-3").write_text("x", encoding="utf-8")
    (data / "README.txt").write_text("x", encoding="utf-8")
    (data / ".coverage").write_text("x", encoding="utf-8")
    assert shard_indices_present(str(data)) == (3,)


def test_data_from_a_shard_the_plan_does_not_contain_is_refused(tmp_path) -> None:
    """The data and the plan then disagree about what ran, and combining them would evaluate the
    floor over a suite neither of them describes."""

    data = tmp_path / "data"
    data.mkdir()
    (data / ".coverage.shard-0").write_text("x", encoding="utf-8")
    (data / ".coverage.shard-9").write_text("x", encoding="utf-8")
    stream = io.StringIO()
    assert combine_shards((0,), str(data), root=str(tmp_path), stream=stream) == 1
    assert "does not contain" in stream.getvalue()


def test_every_expected_shard_present_combines_once_over_the_union(tmp_path, monkeypatch) -> None:
    """The only path on which a floor verdict is computed at all, and the one no test reached:
    every refusal above was measured and the acceptance was not."""

    data = tmp_path / "data"
    data.mkdir()
    (data / ".coverage.shard-0").write_text("x", encoding="utf-8")
    (data / ".coverage.shard-1").write_text("x", encoding="utf-8")
    _canned_coverage(monkeypatch, [(0, "", ""), (0, "", ""), (0, "TOTAL 100%", "")])
    stream = io.StringIO()
    assert combine_shards((0, 1), str(data), root=str(tmp_path), stream=stream) == 0
    assert "combining and evaluating the floor" in stream.getvalue()


# --- the command line ------------------------------------------------------------------


def test_the_plan_digest_is_emitted_alone_so_a_caller_can_bind_other_jobs_to_it(capsys):
    """`--digest` comes before `--json` on purpose: a caller asking for the identity of a plan
    wants that and nothing else on stdout, because it is about to pass it to another job."""

    assert cli.main(["plan", "--mode", "fast", "--digest"]) == 0
    printed = capsys.readouterr().out.strip().splitlines()
    assert len(printed) == 1
    assert len(printed[0]) == 64


def test_a_job_computing_a_different_plan_than_it_was_told_to_expect_faults(capsys) -> None:
    """Two jobs of one run partitioning the suite differently is the failure the digest exists to
    catch: each job proves its own plan whole, and their shards union to neither selection."""

    code = cli.main(
        ["combine", "--mode", "full", "--data-dir", "nowhere", "--plan-digest", "0" * 64]
    )
    assert code == 2
    assert "was told to expect" in capsys.readouterr().err


def test_sharding_an_impact_selection_is_refused(capsys) -> None:
    """An impact selection is derived from the diff, so two jobs with different fetch depths
    partition different things while each proves its own plan whole."""

    code = cli.main(
        ["run-tests", "--mode", "fast", "--path", "engine/uaue/gate.py", "--shard", "0"]
    )
    assert code == 2
    assert "Shard a whole-suite mode" in capsys.readouterr().err


def test_the_combine_command_binds_the_expected_shards_to_the_plan(monkeypatch, capsys) -> None:
    """`expected` comes from the plan's own shard indices and never from a worker count — the two
    differ whenever a wave is exclusive, and a matrix built from the second addresses one fewer
    shard than the plan holds."""

    seen: dict[str, object] = {}

    def fake(expected, data_dir, **kwargs):
        seen["expected"] = expected
        seen["data_dir"] = data_dir
        return 0

    monkeypatch.setattr(cli, "combine_shards", fake)
    assert cli.main(["combine", "--mode", "full", "--data-dir", "somewhere"]) == 0
    assert seen["data_dir"] == "somewhere"
    assert seen["expected"] == tuple(range(len(seen["expected"])))


def test_run_tests_receives_the_plan_it_printed(monkeypatch, capsys) -> None:
    """The rendered plan goes to stderr and the run happens on stdout's terms: an operator must
    be able to read what is about to run WHILE it runs, not after it finishes."""

    seen: dict[str, object] = {}

    def fake(shards, coverage, **kwargs):
        seen["shards"] = shards
        seen["selection"] = kwargs["selection"]
        return 0

    monkeypatch.setattr(cli, "run_tests", fake)
    assert cli.main(["run-tests", "--mode", "fast", "--path", "engine/uaue/gate.py"]) == 0
    rendered = capsys.readouterr().err
    assert "selection" in rendered
    assert seen["shards"], "the plan carried no shard"


def test_a_report_naming_more_escalations_than_it_prints_says_how_many_more(capsys) -> None:
    """Eight are shown and the rest are counted. Printing all of them would bury the verdict;
    printing eight in silence would report a smaller widening than the one that was measured."""

    argv = ["report", "--mode", "fast"]
    for index in range(9):
        argv += ["--path", f"docs/uvi-escalation-probe-{index}.md"]
    assert cli.main(argv) == 0
    body = capsys.readouterr().out
    assert "... +1 more" in body


def test_a_whole_suite_report_names_no_selection_layer(capsys) -> None:
    """A mode that runs everything computes no layers, and a `selection layers:` heading with
    nothing under it would suggest the layers ran and reached nothing."""

    assert cli.main(["report", "--mode", "full"]) == 0
    body = capsys.readouterr().out
    assert "selection layers:" not in body


# --- every gate law's remaining refusal -------------------------------------------------


def test_l02_faults_when_the_script_declares_no_initial_mode(tmp_path) -> None:
    """The default is established by reading the script, not by trusting the declaration. A
    script with no initial MODE has no default to compare against, and asserting a match on that
    basis would be asserting a match against nothing."""
    ctx = _ctx(tmp_path, lambda document: None)
    ctx.verify = "#!/usr/bin/env bash\nrun_stage 'x'\n"
    findings = uvi_gate.exactly_one_default(ctx)
    assert any("declares no initial MODE" in f for f in findings)


def test_l04_refuses_a_declaration_carrying_no_baseline_contract(tmp_path) -> None:
    """An empty baseline makes the law vacuous: every gate could be dropped and the check would
    still hold, because it holds over nothing."""

    def mutate(document):
        document["no_assurance_reduction"]["baseline_stages"] = []

    findings = uvi_gate.no_assurance_reduction(_ctx(tmp_path, mutate))
    assert any("no baseline contract is declared" in f for f in findings)


def test_l06_refuses_a_selector_source_that_names_a_test_file(tmp_path) -> None:
    """A hand-maintained list wearing an engine's costume. The engine's own sources are scanned
    because that is where such a list would go, and it has never been shown to be found."""
    engine_dir = tmp_path / "engine" / "verification_intelligence"
    engine_dir.mkdir(parents=True)
    (engine_dir / "authored.py").write_text(
        'ALWAYS = ("engine/tests/unit/test_authored_by_hand.py",)\n', encoding="utf-8"
    )
    ctx = _ctx(tmp_path, lambda document: None)
    ctx.root = str(tmp_path)
    findings = uvi_gate.selection_is_derived(ctx)
    assert any("names a specific test file" in f for f in findings)
    # And a tree with no .gitignore at all cannot show the evidence home is excluded.
    assert any("not excluded by" in f for f in findings)


@pytest.mark.parametrize(
    ("entry", "message"),
    [
        ("not-an-object", "is not an object"),
        ({"$measured": "some measurement"}, "names no prefix"),
    ],
)
def test_l06_refuses_a_malformed_isolation_entry(tmp_path, entry, message) -> None:
    """Scheduling isolation is the one exception permitted to name a test object, so its own
    shape is held to a stricter standard than the rule it excepts."""

    def mutate(document):
        document["execution"]["test_sharding"]["isolated"] = [entry]

    findings = uvi_gate.selection_is_derived(_ctx(tmp_path, mutate))
    assert any(message in f for f in findings)


def test_l07_reports_a_selection_that_faults_rather_than_crashing(tmp_path, monkeypatch) -> None:
    """A law that raised where it was supposed to report would leave the gate with no verdict on
    fail-wide at all — which reads, from the outside, exactly like the law holding."""

    def refusing(*args, **kwargs):
        raise VerificationIntelligenceError("the substrate is unreadable")

    monkeypatch.setattr(uvi_gate, "select", refusing)
    findings = uvi_gate.fail_wide(_ctx(tmp_path, lambda document: None))
    assert any("selection faulted on" in f for f in findings)


def test_l07_refuses_an_unbounded_change_that_produced_a_narrow_plan(tmp_path, monkeypatch):
    """THE asymmetry, falsified. A selector that narrowed on an unbounded change would skip the
    affected test, and a skipped test is indistinguishable from a passing one."""

    narrow = SelectionResult(
        selection=Selection.IMPACT,
        test_paths=("a/test_x.py",),
        changed=("a.py",),
        affected_objects=(),
        affected_owners=(),
        affected_capabilities=(),
        affected_evidence=(),
        affected_certification=(),
        escalations=(),
        superseded=(),
        layers=(),
    )

    monkeypatch.setattr(uvi_gate, "select", lambda *a, **k: narrow)
    findings = uvi_gate.fail_wide(_ctx(tmp_path, lambda document: None))
    assert any("produced a narrow plan" in f for f in findings)
    assert any("widened without naming a reason" in f for f in findings)


def test_l08_reports_a_partition_that_is_refused_rather_than_crashing(tmp_path, monkeypatch):
    """The partitioner refusing is a finding about the plan. Letting it out as an exception would
    take the whole gate down with no verdict on any law after this one."""

    real = uvi_gate.plan_shards
    calls = {"n": 0}

    def refusing(*args, **kwargs):
        calls["n"] += 1
        if calls["n"] == 1:
            raise VerificationIntelligenceError("no partition is possible")
        return real(*args, **kwargs)

    monkeypatch.setattr(uvi_gate, "plan_shards", refusing)
    findings = uvi_gate.topology_neutrality(_ctx(tmp_path, lambda document: None))
    assert any("was refused" in f for f in findings)


def test_l08_refuses_a_partition_that_loses_duplicates_or_misaddresses_a_test(
    tmp_path, monkeypatch
) -> None:
    """Every failure this law exists for, produced at once: a partition that does not cover the
    suite, one that places a unit twice, one whose indices are not a total addressing, and a
    partitioner that answers differently the second time it is asked."""

    calls = {"n": 0}

    def drifting(units, registry, workers, **kwargs):
        calls["n"] += 1
        return (
            Shard(
                index=7,
                test_paths=("a/test_x.py", "a/test_x.py", f"a/test_{calls['n']}.py"),
                cost_seconds=1.0,
            ),
        )

    monkeypatch.setattr(uvi_gate, "plan_shards", drifting)
    monkeypatch.setattr(uvi_gate, "run_tests", lambda *a, **k: 1)
    monkeypatch.setattr(uvi_gate, "combine_shards", lambda *a, **k: 1)
    findings = uvi_gate.topology_neutrality(_ctx(tmp_path, lambda document: None))
    assert any("does not cover exactly the suite" in f for f in findings)
    assert any("places a unit twice" in f for f in findings)
    assert any("not addressable by index" in f for f in findings)
    assert any("produced different shards" in f for f in findings)


def test_l08_refuses_a_partition_a_job_at_a_time_cannot_reproduce(tmp_path, monkeypatch) -> None:
    """Three failures of the cross-job substrate, which is weaker than the in-process one.

    A plan whose shards do not carry distinct indices cannot be executed one job per index: the
    matrix addresses each index once and the shards sharing it all run, so the union of the jobs
    is not the plan. And a shard index the plan does not contain must fault rather than run
    something else, while a combine missing every shard's data must refuse rather than report a
    floor over nothing — neither of which any test had shown these laws can detect.
    """

    def colliding(units, registry, workers, **kwargs):
        return (
            Shard(index=0, test_paths=("a/test_x.py",), cost_seconds=1.0),
            Shard(index=0, test_paths=("a/test_y.py",), cost_seconds=1.0),
        )

    monkeypatch.setattr(uvi_gate, "plan_shards", colliding)
    monkeypatch.setattr(uvi_gate, "run_tests", lambda *a, **k: 0)
    monkeypatch.setattr(uvi_gate, "combine_shards", lambda *a, **k: 0)
    findings = uvi_gate.topology_neutrality(_ctx(tmp_path, lambda document: None))
    assert any("one shard per job does not cover" in f for f in findings)
    assert any("was not refused" in f for f in findings)
    assert any("reported a verdict" in f for f in findings)


def test_l09_refuses_a_certification_mode_that_reached_a_reuse_decision(tmp_path, monkeypatch):
    """A certification that reuses a result certifies a cache. Nothing in the declaration can
    make this true today, which is exactly why the law has to be shown to fire."""

    monkeypatch.setattr(uvi_gate, "decide", lambda *a, **k: (True, "a cached PASS", "d" * 64))
    findings = uvi_gate.evidence_reuse_integrity(_ctx(tmp_path, lambda document: None))
    assert any("reached a reuse decision" in f for f in findings)
    assert any("is not reusable but was reused" in f for f in findings)


def test_l10_refuses_a_plan_carrying_a_clock_or_a_machine_path(tmp_path, monkeypatch) -> None:
    """Two plans of one repository must agree byte for byte. A wall clock makes them disagree on
    every run, and an absolute path makes them disagree between machines."""

    ctx = _ctx(tmp_path, lambda document: None)
    monkeypatch.setattr(
        uvi_gate,
        "plan_json",
        lambda plan: f'{{"at": "2026-09-09T10:00", "root": "{ctx.root}"}}',
    )
    findings = uvi_gate.deterministic_planning(ctx)
    assert any("carries a wall clock" in f for f in findings)
    assert any("carries an absolute machine path" in f for f in findings)


def test_l13_refuses_a_registry_that_is_reusable_on_one_side_only(tmp_path) -> None:
    """Independence cannot be demonstrated from one side. With every stage reusable, "the
    read-set does not follow the reuse policy" holds over a policy that never varies."""

    def mutate(document):
        for stage in document["stage_registry"]["stages"]:
            stage["reusable"] = True
            stage.setdefault("reuse_inputs", ["00-BOOK/"])

    findings = uvi_gate.read_set_is_independent_of_reuse_policy(_ctx(tmp_path, mutate))
    assert any("one side is empty" in f for f in findings)


def test_l13_refuses_a_non_reusable_stage_with_no_read_set(tmp_path) -> None:
    """A stage impact analysis cannot relate to any change is a stage no selection can reach."""

    def mutate(document):
        for stage in document["stage_registry"]["stages"]:
            if not stage.get("reusable"):
                stage["read_set"] = []

    findings = uvi_gate.read_set_is_independent_of_reuse_policy(_ctx(tmp_path, mutate))
    assert any("declares no read-set" in f for f in findings)


def test_l13_refuses_a_read_set_that_resolves_to_nothing(tmp_path) -> None:
    """A prefix that reaches no object is a declaration with no consequence, and a stale one is
    indistinguishable from a live one until something asks."""

    def mutate(document):
        for stage in document["stage_registry"]["stages"]:
            if not stage.get("reusable"):
                stage["read_set"] = ["a-prefix-no-object-in-this-repository-carries/"]

    findings = uvi_gate.read_set_is_independent_of_reuse_policy(_ctx(tmp_path, mutate))
    assert any("reaches no object" in f for f in findings)


def test_l13_refuses_a_read_set_that_follows_the_reuse_policy(tmp_path, monkeypatch) -> None:
    """The defect the separation was for: one field silently answering both questions, so that
    toggling the policy changed the read-set and the two could never be measured apart."""

    ctx = _ctx(tmp_path, lambda document: None)
    real = dataclasses.replace

    def coupled(obj, **changes):
        replaced = real(obj, **changes)
        if "reusable" in changes:
            replaced = real(replaced, read_set=("00-BOOK/tools/", *replaced.reads))
        return replaced

    # The law imports `dataclasses` inside its own body, so the name it resolves is the module
    # itself. Patching the module is therefore the only way to make the toggle couple.
    monkeypatch.setattr(dataclasses, "replace", coupled)
    findings = uvi_gate.read_set_is_independent_of_reuse_policy(ctx)
    assert any("changed the read-set" in f for f in findings)
    assert any("changed the resolved population" in f for f in findings)


def test_l14_refuses_a_key_that_does_not_move_with_the_read_set(tmp_path, monkeypatch) -> None:
    """The read-set is what the key is taken over. A key indifferent to it would hit across two
    stages reading different things, which is a cache answering for a run that never happened."""

    monkeypatch.setattr(uvi_gate, "input_digest", lambda *a, **k: "a-key-that-never-moves")
    findings = uvi_gate.evidence_identity_depends_on_the_read_set(
        _ctx(tmp_path, lambda document: None)
    )
    assert any("widening the read-set did not change the key" in f for f in findings)
    assert any("narrowing the read-set did not change the key" in f for f in findings)


def test_l14_refuses_a_registry_in_which_no_stage_produces_a_key(tmp_path, monkeypatch) -> None:
    """A law measuring nothing reports HOLDS, and HOLDS over an empty population is the shape
    every check in this package is written to refuse."""

    monkeypatch.setattr(uvi_gate, "input_digest", lambda *a, **k: None)
    findings = uvi_gate.evidence_identity_depends_on_the_read_set(
        _ctx(tmp_path, lambda document: None)
    )
    assert any("this law measured nothing" in f for f in findings)


def test_the_rendered_report_counts_the_violations_it_does_not_print() -> None:
    """Eight per law, and the rest counted: a report that printed them all would bury the
    verdict, and one that stopped at eight in silence would understate the refusal."""
    report = uvi_gate.measure()
    report["laws"][0]["holds"] = False
    report["laws"][0]["violations"] = [f"violation {index}" for index in range(11)]
    assert "... +3 more" in uvi_gate.render(report)


def test_a_refusal_is_rendered_once_to_stdout_when_the_gate_is_not_quiet(tmp_path, capsys):
    """--quiet redirects the report to stderr so a refusal is still readable. Without it the
    report has already gone to stdout and printing it twice would be the noise the flag exists
    to remove."""
    document = load_declaration()
    document["mode_constitution"]["default_mode"] = "integration"
    path = tmp_path / "declaration.json"
    path.write_text(json.dumps(document), encoding="utf-8")
    assert uvi_gate.main(["--gate", "--declaration", str(path)]) == uvi_gate.EXIT_INCOHERENT
    captured = capsys.readouterr()
    assert "REFUSED" in captured.out
    assert "REFUSED" not in captured.err


def test_a_job_computing_the_plan_it_was_told_to_expect_proceeds(monkeypatch, capsys) -> None:
    """The digest is a proof obligation, not a veto: a job that recomputed the same plan must
    carry on, or binding jobs together would make every run refuse itself."""

    assert cli.main(["plan", "--mode", "full", "--digest"]) == 0
    digest = capsys.readouterr().out.strip()
    monkeypatch.setattr(cli, "combine_shards", lambda *a, **k: 0)
    code = cli.main(
        ["combine", "--mode", "full", "--data-dir", "somewhere", "--plan-digest", digest]
    )
    assert code == 0
