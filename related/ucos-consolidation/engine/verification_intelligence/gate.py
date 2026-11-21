"""UVI-000001 Part 08 — the fail-closed verification intelligence gate.

Exit codes follow the repository convention so a caller can distinguish the three
outcomes that matter:

    0  COHERENT    every law holds
    1  INCOHERENT  a law was measured and refused
    2  FAULT       no verdict could be reached (the declaration is unusable)

The distinction between 1 and 2 is deliberate. "A mode claims more than it measures" and
"the declaration could not be read" are different facts, and collapsing them would let an
unreadable declaration pass as whichever was more convenient.

OBSERVE MODE — READ ONLY. It loads the declaration, reads ``verify.sh`` and the engine's
own sources, plans in memory, and writes nothing — including to gitignored paths. No
clock, no network, no subprocess, so it cannot dirty the tree and cannot flake.

Every law is COMPUTED. UVI-L-07 and UVI-L-08 in particular are behavioural: the gate
performs a selection over a synthetic unbounded change and checks that it widened, and
partitions the whole suite at several worker counts and checks that nothing was lost.
A law about behaviour that is checked by reading a docstring is not checked.
"""

from __future__ import annotations

import argparse
import ast
import io
import json
import os
import re
import sys
import tempfile
from typing import Any

from engine.verification_intelligence.constitution import (
    Constitution,
    execution_contract,
    load_constitution,
    load_declaration,
    repo_root,
)
from engine.verification_intelligence.evidence import (
    decide,
    input_digest,
    resolve_prefix,
    store_home,
)
from engine.verification_intelligence.execution import (
    combine_shards,
    plan_shards,
    run_tests,
    unit_file,
)
from engine.verification_intelligence.model import (
    Coverage,
    Selection,
    VerificationIntelligenceError,
)
from engine.verification_intelligence.plan import build_plan, plan_json
from engine.verification_intelligence.registry import (
    Substrates,
    TestObjectRegistry,
    build_test_registry,
    load_substrates,
)
from engine.verification_intelligence.selection import select

EXIT_COHERENT = 0
EXIT_INCOHERENT = 1
EXIT_FAULT = 2

#: The one entry point whose declared stages this programme classifies.
VERIFY = "verify.sh"

#: The engine's own sources, scanned by UVI-L-06 for an authored test path.
ENGINE_DIR = "engine/verification_intelligence"

#: The one declaration path permitted to name a test object — see selection_is_derived.
SCHEDULING_EXCEPTION = "execution.test_sharding.isolated"

#: A literal naming a specific test FILE. Its presence in the selector would mean a
#: hand-maintained list wearing an engine's costume, which is the condition L-06 refuses.
TEST_LITERAL = re.compile(r"\btests?/[\w./-]*test_\w+\.py\b")


class Findings(list):
    """A law's violations. Empty means the law holds."""


def _verify_source(root: str) -> str:
    try:
        with open(os.path.join(root, VERIFY), encoding="utf-8") as handle:
            return handle.read()
    except OSError as exc:  # pragma: no cover - only on a broken checkout
        raise VerificationIntelligenceError(f"{VERIFY} is unreadable") from exc


def _declared_stage_labels(source: str) -> list[str]:
    """Every ``run_stage "…"`` literal, in source order.

    The same derivation ``platform/tests/test_canonical_validation_evidence.py`` and
    ``.github/workflows/uisd-gate.yml`` perform, deliberately reproduced rather than
    imported: three readers agreeing on one regex over one file is the property that
    keeps the contract, the record and this registry from drifting apart.
    """
    return re.findall(r'^\s*run_stage "([^"]+)"', source, re.M)


def _accepted_flags(source: str) -> set[str]:
    """Every mode flag the script's own argument parser admits."""
    arms = re.findall(r"^\s*(--[a-z]+)\)\s*_set_mode", source, re.M)
    return set(arms)


# --- the laws -----------------------------------------------------------------------


def mode_constitution_completeness(ctx: _Context) -> Findings:
    """UVI-L-01 — the script and the constitution admit exactly the same modes."""
    findings = Findings()
    declared = set(ctx.constitution.flags)
    accepted = _accepted_flags(ctx.verify)
    for flag in sorted(declared - accepted):
        findings.append(f"{flag} is declared in the constitution but {VERIFY} does not accept it")
    for flag in sorted(accepted - declared):
        findings.append(f"{VERIFY} accepts {flag} but the constitution does not declare it")
    return findings


def exactly_one_default(ctx: _Context) -> Findings:
    """UVI-L-02 — one declared default, and the bare invocation resolves to it."""
    findings = Findings()
    declared = ctx.constitution.default_mode_id
    initial = re.search(r'^MODE="([a-z]+)"', ctx.verify, re.M)
    if initial is None:
        findings.append(f"{VERIFY} declares no initial MODE, so its default cannot be established")
        return findings
    if initial.group(1) != declared:
        findings.append(
            f"{VERIFY} defaults to {initial.group(1)!r} but the constitution declares "
            f"{declared!r} as the default mode"
        )
    return findings


def stage_registry_reconciliation(ctx: _Context) -> Findings:
    """UVI-L-03 — the registry and the script declare the same stages, in the same order."""
    findings = Findings()
    script = _declared_stage_labels(ctx.verify)
    registry = list(ctx.constitution.stage_labels)
    if script != registry:
        for label in registry:
            if label not in script:
                findings.append(
                    f"the registry classifies a stage {VERIFY} does not declare: {label}"
                )
        for label in script:
            if label not in registry:
                findings.append(
                    f"{VERIFY} declares a stage the registry does not classify: {label}"
                )
        if not findings:
            findings.append(
                "the registry and the script declare the same stages in DIFFERENT order; the "
                "order is part of the contract the canonical validation record digests"
            )
    return findings


def no_assurance_reduction(ctx: _Context) -> Findings:
    """UVI-L-04 — every baseline gate still exists and is still certified against."""
    findings = Findings()
    baseline = [
        str(label)
        for label in (ctx.document.get("no_assurance_reduction") or {}).get("baseline_stages") or ()
    ]
    if not baseline:
        findings.append("no baseline contract is declared, so no reduction could be detected")
        return findings
    declared = set(ctx.constitution.stage_labels)
    certification_modes = [mode for mode in ctx.constitution.modes if mode.certification_eligible]
    if not certification_modes:
        findings.append("no mode is certification-eligible, so the contract is owned by nothing")
    for label in baseline:
        if label not in declared:
            findings.append(f"a baseline gate is no longer a declared stage: {label}")
            continue
        for mode in certification_modes:
            admitted = {stage.label for stage in ctx.constitution.stages_for(mode)}
            if label not in admitted:
                findings.append(
                    f"certification-eligible mode --{mode.mode_id} no longer runs a baseline "
                    f"gate: {label}"
                )
    return findings


def no_mode_claims_more_than_it_measures(ctx: _Context) -> Findings:
    """UVI-L-05 — certification needs the whole suite and the floor; nothing else may claim them."""
    findings = Findings()
    for mode in ctx.constitution.modes:
        if mode.certification_eligible:
            if mode.selection is not Selection.WHOLE_SUITE:
                findings.append(
                    f"--{mode.mode_id} is certification-eligible but selects "
                    f"{mode.selection.value}, so it would certify a subset"
                )
            if mode.coverage is not Coverage.FLOOR_90:
                findings.append(
                    f"--{mode.mode_id} is certification-eligible but does not evaluate the floor"
                )
            if mode.evidence_reuse:
                findings.append(
                    f"--{mode.mode_id} is certification-eligible and permits evidence reuse, so "
                    "it could certify a cache"
                )
        else:
            if not mode.claims_not:
                findings.append(
                    f"--{mode.mode_id} is not certification-eligible and states nothing it does "
                    "not claim, so a reader cannot tell what its green result excludes"
                )
            if mode.coverage is Coverage.FLOOR_90:
                findings.append(
                    f"--{mode.mode_id} evaluates the coverage floor but is not certification-"
                    "eligible; the floor would then have two owners"
                )
    return findings


def selection_is_derived(ctx: _Context) -> Findings:
    """UVI-L-06 — no authored test path, and every declared substrate is actually read.

    The scan is over STRING CONSTANTS the engine evaluates, not over its source text.
    A docstring or a comment naming a test file is documentation — this very module's
    docstrings name several — while a string constant naming one is a hand-maintained
    selection wearing an engine's costume. Scanning the raw text cannot tell those apart,
    so it is parsed instead and docstrings are excluded by position.
    """
    findings = Findings()
    root = ctx.root
    engine_dir = os.path.join(root, ENGINE_DIR)
    sources: list[str] = []
    for name in sorted(os.listdir(engine_dir)):
        if not name.endswith(".py"):
            continue
        with open(os.path.join(engine_dir, name), encoding="utf-8") as handle:
            body = handle.read()
        sources.append(body)
        for literal in _evaluated_strings(body, f"{ENGINE_DIR}/{name}", findings):
            for match in TEST_LITERAL.findall(literal):
                findings.append(f"{ENGINE_DIR}/{name} names a specific test file: {match}")

    # ONE part of the declaration is allowed to name a test object, and the exception is
    # narrow on purpose. `execution.test_sharding.isolated` is SCHEDULING: it says an
    # object may not run beside anything else, never that it may not run. A blanket
    # exemption would be a hole, so the entries are held to a stricter test instead —
    # each must resolve to a currently collectible object, so a stale prefix is a failure
    # rather than a silently inert line, and each must carry the measurement that
    # justifies the cost of isolating it.
    for key, value in _declared_strings(ctx.document):
        if key.startswith(f"{SCHEDULING_EXCEPTION}["):
            continue
        for match in TEST_LITERAL.findall(value):
            findings.append(f"the declaration names a specific test file at {key}: {match}")

    # The declaration states that the evidence store is untracked. That is a claim about
    # the repository, so it is measured rather than believed: an evidence store inside the
    # tracked tree is a second answer to "did this pass", and UCOS-UGA-001 measured every
    # entry in it as an unidentified object the first time this ran without the rule.
    ignore_file = os.path.join(root, ".gitignore")
    home = ctx.constitution.evidence_home.rstrip("/")
    try:
        with open(ignore_file, encoding="utf-8") as handle:
            ignored = {line.strip().rstrip("/") for line in handle if not line.startswith("#")}
    except OSError:
        ignored = set()
    if home not in ignored:
        findings.append(
            f"the evidence registry home {ctx.constitution.evidence_home} is not excluded by "
            ".gitignore, so a cache of results would enter the tracked tree"
        )

    for entry in ctx.constitution.sharding.get("isolated") or ():
        if not isinstance(entry, dict):
            findings.append("an isolation entry is not an object")
            continue
        prefix = str(entry.get("prefix") or "")
        if not prefix:
            findings.append("an isolation entry names no prefix")
            continue
        if not any(path.startswith(prefix) for path in ctx.tests.paths):
            findings.append(
                f"{prefix} is declared isolated but matches no collectible test object, so the "
                "declaration is carrying a scheduling exception for something that is not there"
            )
        if not str(entry.get("$measured") or "").strip():
            findings.append(
                f"{prefix} is declared isolated with no measurement justifying it; isolation "
                "serialises its cost onto every run and may not rest on a suspicion"
            )

    joined = "".join(sources)
    for substrate in ctx.constitution.substrates:
        source = str(substrate.get("source") or "")
        if source and source not in joined:
            findings.append(
                f"substrate {substrate.get('id')} declares {source} but no module reads it, so "
                "the declaration claims a derivation that does not happen"
            )
    return findings


def _evaluated_strings(body: str, where: str, findings: Findings) -> list[str]:
    """Every string constant the module evaluates, with docstrings excluded."""
    try:
        tree = ast.parse(body)
    except SyntaxError as exc:  # pragma: no cover - ruff would have refused it first
        findings.append(f"{where} does not parse: {exc}")
        return []
    docstrings = {
        id(node.body[0].value)
        for node in ast.walk(tree)
        if isinstance(node, ast.Module | ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef)
        and node.body
        and isinstance(node.body[0], ast.Expr)
        and isinstance(node.body[0].value, ast.Constant)
        and isinstance(node.body[0].value.value, str)
    }
    return [
        node.value
        for node in ast.walk(tree)
        if isinstance(node, ast.Constant)
        and isinstance(node.value, str)
        and id(node) not in docstrings
    ]


def _declared_strings(document: Any, prefix: str = "") -> list[tuple[str, str]]:
    """Every string the declaration states, excluding its ``$``-prefixed prose keys.

    A key beginning with ``$`` is this repository's convention for rationale — prose
    that explains a declaration rather than participating in it. Prose may name a test
    file; a declared value may not.
    """
    found: list[tuple[str, str]] = []
    if isinstance(document, dict):
        for key, value in document.items():
            if str(key).startswith("$"):
                continue
            found.extend(_declared_strings(value, f"{prefix}.{key}" if prefix else str(key)))
    elif isinstance(document, list):
        for index, value in enumerate(document):
            found.extend(_declared_strings(value, f"{prefix}[{index}]"))
    elif isinstance(document, str):
        found.append((prefix, document))
    return found


def fail_wide(ctx: _Context) -> Findings:
    """UVI-L-07 — computed, not asserted: an unbounded change must widen.

    Three synthetic change sets, each one a condition no graph in this repository can
    bound. Every one of them must produce the whole suite. The paths are synthetic on
    purpose — the law is about the CLASS of change, and a real path would make the check
    depend on that file continuing to exist.
    """
    findings = Findings()
    cases = {
        "a declaration or registry with no import edges": "00-BOOK/DATA/uvi-synthetic-probe.json",
        "a file type that carries no edges at all": "docs/uvi-synthetic-probe.md",
        "a Python file absent from the executable registry": "engine/uvi_synthetic_probe.py",
    }
    for description, path in cases.items():
        try:
            result = select((path,), substrates=ctx.substrates, tests=ctx.tests, root=ctx.root)
        except VerificationIntelligenceError as exc:
            findings.append(f"selection faulted on {description}: {exc}")
            continue
        if result.selection is not Selection.WHOLE_SUITE:
            findings.append(
                f"{description} produced a narrow plan of {len(result.test_paths)} test object(s); "
                "an unbounded change must widen"
            )
        if not result.escalations:
            findings.append(f"{description} widened without naming a reason")
    return findings


def topology_neutrality(ctx: _Context) -> Findings:
    """UVI-L-08 — computed: no worker count loses, duplicates or invents a test."""
    findings = Findings()
    suite = ctx.tests.paths
    units = ctx.tests.units_for(suite)
    for workers in (1, 2, 3, 7, 12, len(units)):
        try:
            shards = plan_shards(units, ctx.tests, workers)
        except VerificationIntelligenceError as exc:
            findings.append(f"partitioning the suite across {workers} shard(s) was refused: {exc}")
            continue
        placed = [unit for shard in shards for unit in shard.test_paths]
        if sorted({unit_file(unit) for unit in placed}) != sorted(suite):
            findings.append(f"the {workers}-shard partition does not cover exactly the suite")
        if len(placed) != len(set(placed)):
            findings.append(f"the {workers}-shard partition places a unit twice")
    first = plan_shards(units, ctx.tests, 7)
    second = plan_shards(units, ctx.tests, 7)
    if [shard.test_paths for shard in first] != [shard.test_paths for shard in second]:
        findings.append("partitioning the same suite twice produced different shards")

    # --- the same law where a shard is a JOB rather than a process ----------------------
    #
    # Sharding across jobs obeys this law on a WEAKER substrate, and the weakness is the
    # reason these are measured rather than argued. In one process a shard that dies
    # before writing coverage data also exits non-zero, so the run is already failing and
    # nothing false can be minted. A combine job sees ARTIFACTS, NOT EXIT CODES: a shard
    # that was cancelled, skipped, or whose upload failed is indistinguishable from one
    # that measured nothing, and the coverage tool would happily report a floor over the
    # fragment that arrived.
    for workers in (1, 2, 3, 7, 12):
        shards = plan_shards(units, ctx.tests, workers)
        indices = sorted(shard.index for shard in shards)
        # ADDRESSING MUST BE TOTAL. A CI matrix names shards by index, and the obvious
        # matrix is built from the worker count — but `plan_shards` returns one shard per
        # worker PLUS one per isolated wave, so `range(workers)` does not name every
        # shard. The loss is silent: the unaddressed shard's tests simply never run, while
        # every job's topology proof still passes, because that proof measures the PLAN
        # and not which shards were EXECUTED. Requiring contiguity from zero is what makes
        # `range(len(shards))` a total addressing, so a matrix built from the plan's own
        # length cannot skip one.
        if indices != list(range(len(shards))):
            findings.append(
                f"the {workers}-shard plan is not addressable by index: it holds "
                f"{indices}, so a matrix over range({len(shards)}) would not name every shard"
            )
        # Narrowing to one shard per job must lose nothing the whole plan placed.
        per_job = [
            unit
            for index in indices
            for shard in shards
            if shard.index == index
            for unit in shard.test_paths
        ]
        whole = [unit for shard in shards for unit in shard.test_paths]
        if sorted(per_job) != sorted(whole):
            findings.append(
                f"executing the {workers}-shard plan one shard per job does not cover "
                f"what the plan places"
            )

    # A shard index the plan does not contain must FAULT, not run something else.
    unaddressable = max(shard.index for shard in first) + 1
    refused = run_tests(
        first,
        Coverage.FLOOR_90,
        only=unaddressable,
        coverage_out=os.devnull,
        stream=io.StringIO(),
    )
    if refused == 0:
        findings.append(
            f"executing shard {unaddressable}, which the plan does not contain, was not refused"
        )

    # A combine that is missing a shard must refuse rather than report a floor.
    with tempfile.TemporaryDirectory() as empty:
        if combine_shards(tuple(indices), empty, stream=io.StringIO()) == 0:
            findings.append("combining coverage with every shard's data missing reported a verdict")
    return findings


def evidence_reuse_integrity(ctx: _Context) -> Findings:
    """UVI-L-09 — certification never reaches a reuse decision, and a miss is a miss."""
    findings = Findings()
    home = store_home(ctx.root, ctx.constitution.evidence_home)
    for mode in ctx.constitution.modes:
        for stage in ctx.constitution.stages_for(mode):
            reuse, reason, _ = decide(
                mode, stage, ctx.substrates, home=home, root=ctx.root, verify=ctx.verify
            )
            if mode.certification_eligible and reuse:
                findings.append(
                    f"--{mode.mode_id} is certification-eligible and reached a reuse decision "
                    f"for {stage.stage_id}: {reason}"
                )
            if reuse and not stage.reusable:
                findings.append(f"{stage.stage_id} is not reusable but was reused")
    conditions = ctx.constitution.evidence_reuse_conditions
    for condition in ("input digest", "PASS"):
        if not any(condition.split()[0] in text for text in conditions):
            findings.append(f"the declared reuse conditions do not mention {condition}")
    return findings


def deterministic_planning(ctx: _Context) -> Findings:
    """UVI-L-10 — plan twice, get identical bytes, and carry no observation."""
    findings = Findings()
    for mode in ctx.constitution.modes:
        first = plan_json(
            build_plan(
                mode.mode_id,
                constitution=ctx.constitution,
                substrates=ctx.substrates,
                tests=ctx.tests,
                changed=(),
                root=ctx.root,
            )
        )
        second = plan_json(
            build_plan(
                mode.mode_id,
                constitution=ctx.constitution,
                substrates=ctx.substrates,
                tests=ctx.tests,
                changed=(),
                root=ctx.root,
            )
        )
        if first != second:
            findings.append(f"planning --{mode.mode_id} twice produced different bytes")
        for stamp in re.findall(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}", first):
            findings.append(f"the --{mode.mode_id} plan carries a wall clock: {stamp}")
        if ctx.root in first:
            findings.append(f"the --{mode.mode_id} plan carries an absolute machine path")
    return findings


#: Every implemented check, bound to the declaration by name. The constitution refuses to
#: construct itself if a law names a check absent here, or if a check here is claimed by
#: no law — so this table and the declared law list cannot drift apart.
def every_declared_read_set_resolves(ctx: _Context) -> Findings:
    """UVI-L-11 — a declared read-set that matches nothing is a defect, not a cache miss.

    The condition this refuses is silent and permanent. ``input_digest`` correctly
    refuses a key it cannot take, so a prefix matching no registered object makes the
    stage run — safe, and indistinguishable from a cold cache. Three stages sat in that
    state indefinitely because two prefixes were resolved against the EXECUTABLE
    projection while the objects they name are DOCUMENT_ARTIFACTs carried only by the
    universal registry.

    Measured over every stage that declares reuse inputs, whether or not the stage is
    currently reusable: a read-set is a statement about what the stage READS, and it
    must resolve even for a stage policy forbids reusing.
    """
    findings = Findings()
    for stage in ctx.constitution.stages:
        for prefix in stage.reads:
            if not resolve_prefix(ctx.substrates, prefix):
                findings.append(
                    f"{stage.stage_id} declares read-set prefix {prefix!r}, which resolves "
                    f"to no registered object"
                )
    return findings


def every_stage_declares_a_read_set(ctx: _Context) -> Findings:
    """UVI-L-12 — a stage with no declared read-set is a stage nothing can reason about.

    Mandatory for EVERY stage, not only the cacheable ones. The read-set is a dependency
    relation; whether the stage may be answered from cache is a separate policy, and a
    stage that must always run still reads something knowable.
    """
    findings = Findings()
    for stage in ctx.constitution.stages:
        if not stage.read_set:
            findings.append(f"{stage.stage_id} declares no read_set")
    return findings


def read_set_is_independent_of_reuse_policy(ctx: _Context) -> Findings:
    """UVI-L-13 — computed, not asserted: the two declarations do not determine each other.

    Three properties, each of which failed before the separation:

    * a read-set exists for stages on BOTH sides of the reuse policy, so the policy
      cannot be inferred from the presence of a read-set and vice versa;
    * every NON-reusable stage resolves to a non-empty object population, so impact
      analysis can reach a stage that may never be cached;
    * toggling the reuse flag IN MEMORY changes neither the read-set nor the population
      it resolves to — performed here rather than described, because the whole defect
      was that one field silently answered both questions.
    """
    import dataclasses

    findings = Findings()
    reusable = [s for s in ctx.constitution.stages if s.reusable]
    non_reusable = [s for s in ctx.constitution.stages if not s.reusable]
    if not reusable or not non_reusable:
        findings.append("the stage registry cannot demonstrate independence: one side is empty")
    for stage in non_reusable:
        if not stage.read_set:
            findings.append(f"{stage.stage_id} is non-reusable and declares no read-set")
            continue
        population: set[str] = set()
        for prefix in stage.reads:
            population |= set(resolve_prefix(ctx.substrates, prefix))
        if not population:
            findings.append(
                f"{stage.stage_id} is non-reusable and its read-set reaches no object, so "
                f"impact analysis cannot relate any change to it"
            )
    for stage in ctx.constitution.stages:
        toggled = dataclasses.replace(stage, reusable=not stage.reusable)
        if toggled.reads != stage.reads:
            findings.append(f"{stage.stage_id}: toggling the reuse policy changed the read-set")
        before = {p for pre in stage.reads for p in resolve_prefix(ctx.substrates, pre)}
        after = {p for pre in toggled.reads for p in resolve_prefix(ctx.substrates, pre)}
        if before != after:
            findings.append(
                f"{stage.stage_id}: toggling the reuse policy changed the resolved population"
            )
    return findings


def evidence_identity_depends_on_the_read_set(ctx: _Context) -> Findings:
    """UVI-L-14 — computed: a changed read-set is a changed evidence identity.

    The read-set is what the digest is taken over, so widening or narrowing it must
    produce a different key. Performed on every keyable stage rather than argued, because
    a read-set that did not reach the key would be a declaration with no consequence.
    """
    import dataclasses

    findings = Findings()
    measured = 0
    for stage in ctx.constitution.stages:
        contract = execution_contract(stage.label, root=ctx.root, source=ctx.verify)
        baseline = input_digest(stage, ctx.substrates, contract=contract)
        if baseline is None:
            continue
        measured += 1
        widened = dataclasses.replace(stage, read_set=(*stage.reads, "00-BOOK/tools/"))
        if input_digest(widened, ctx.substrates, contract=contract) == baseline:
            findings.append(f"{stage.stage_id}: widening the read-set did not change the key")
        if len(stage.reads) > 1:
            narrowed = dataclasses.replace(stage, read_set=tuple(sorted(stage.reads))[:-1])
            if input_digest(narrowed, ctx.substrates, contract=contract) == baseline:
                findings.append(f"{stage.stage_id}: narrowing the read-set did not change the key")
    if not measured:
        findings.append("no stage produced a key, so this law measured nothing")
    return findings


def non_reuse_is_argued(ctx: _Context) -> Findings:
    """UVI-L-14 — a stage that cannot be reused says why.

    THE MIRROR OF A REFUSAL THAT ALREADY EXISTS. ``constitution.py`` refuses a stage declared
    reusable that names no read-set, on the ground that its cache key would cover nothing and
    every run would be a false hit. Nothing refused the other omission, and six stages were
    non-reusable with no recorded reason — paying full cost on every run because the
    alternative had never been argued.

    THE ARGUMENT IS THE POINT, NOT THE FLAG. Reading the six reasons is how anyone learns
    whether a sound key is possible at all: the omega gate's subject is the tracked corpus, so
    no key narrower than every file is honest; the coverage report projects THIS run's data,
    so a reused one is wrong rather than stale; registration observation is --full only, where
    UVI-L-09 has already made reuse unreachable. Those are three different reasons and a bare
    ``false`` records none of them.
    """
    findings = Findings()
    stages = ctx.document.get("stage_registry", {})
    stages = stages.get("stages", stages) if isinstance(stages, dict) else stages
    measured = 0
    for stage in stages:
        if stage.get("reusable"):
            continue
        measured += 1
        if not str(stage.get("$not_reusable", "")).strip():
            findings.append(
                f"stage {stage.get('id')!r} is not reusable and records no reason, so its cost "
                "is paid on every run for an argument nobody has made"
            )
    if not measured:
        findings.append("no stage is non-reusable, so this law measured nothing")
    return findings


CHECKS = {
    "non_reuse_is_argued": non_reuse_is_argued,
    "mode_constitution_completeness": mode_constitution_completeness,
    "exactly_one_default": exactly_one_default,
    "stage_registry_reconciliation": stage_registry_reconciliation,
    "no_assurance_reduction": no_assurance_reduction,
    "no_mode_claims_more_than_it_measures": no_mode_claims_more_than_it_measures,
    "selection_is_derived": selection_is_derived,
    "fail_wide": fail_wide,
    "topology_neutrality": topology_neutrality,
    "evidence_reuse_integrity": evidence_reuse_integrity,
    "deterministic_planning": deterministic_planning,
    "every_declared_read_set_resolves": every_declared_read_set_resolves,
    "every_stage_declares_a_read_set": every_stage_declares_a_read_set,
    "read_set_is_independent_of_reuse_policy": read_set_is_independent_of_reuse_policy,
    "evidence_identity_depends_on_the_read_set": evidence_identity_depends_on_the_read_set,
}


class _Context:
    """Everything the checks read, loaded once."""

    __slots__ = ("constitution", "document", "root", "substrates", "tests", "verify")

    def __init__(self, root: str | None = None, declaration: str | None = None) -> None:
        self.root = root or repo_root()
        self.document = load_declaration(declaration)
        self.constitution: Constitution = load_constitution(declaration, checks=frozenset(CHECKS))
        self.substrates: Substrates = load_substrates(self.root)
        self.tests: TestObjectRegistry = build_test_registry(self.substrates, self.root)
        self.verify = _verify_source(self.root)


def measure(root: str | None = None, declaration: str | None = None) -> dict[str, Any]:
    """Measure every declared law and return the report.

    Raises:
        VerificationIntelligenceError: the substrate is unusable, which is a FAULT
            rather than a verdict.
    """
    ctx = _Context(root, declaration)
    laws = []
    for law in ctx.constitution.laws:
        violations = list(CHECKS[law.check](ctx))
        laws.append(
            {
                "law_id": law.law_id,
                "title": law.title,
                "violations": violations,
                "holds": not violations,
            }
        )
    refused = [entry for entry in laws if not entry["holds"]]
    return {
        "artifact_id": ctx.constitution.artifact_id,
        "version": ctx.constitution.version,
        "authority": "NONE — DERIVED TRUTH",
        "plane": "OBSERVE MODE — READ ONLY",
        "modes_declared": len(ctx.constitution.modes),
        "default_mode": ctx.constitution.default_mode_id,
        "stages_declared": len(ctx.constitution.stages),
        "test_objects": len(ctx.tests.objects),
        "test_objects_priced": ctx.tests.priced,
        "laws": laws,
        "laws_measured": len(laws),
        "laws_refused": len(refused),
        "verdict": "COHERENT" if not refused else "INCOHERENT",
    }


def render(report: dict[str, Any]) -> str:
    lines = [
        f"{report['artifact_id']} — {report['plane']}",
        "-" * 72,
        f"  modes declared     : {report['modes_declared']} (default --{report['default_mode']})",
        f"  stages classified  : {report['stages_declared']}",
        f"  test objects       : {report['test_objects']} ({report['test_objects_priced']} priced)",
        "-" * 72,
    ]
    for law in report["laws"]:
        mark = "HOLDS " if law["holds"] else "REFUSED"
        lines.append(f"  {mark} {law['law_id']}  {law['title']}")
        for violation in law["violations"][:8]:
            lines.append(f"          - {violation}")
        remaining = len(law["violations"]) - 8
        if remaining > 0:
            lines.append(f"          ... +{remaining} more")
    lines.append("-" * 72)
    lines.append(
        f"  VERDICT: {report['verdict']} "
        f"({report['laws_measured'] - report['laws_refused']}/{report['laws_measured']} laws hold)"
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m engine.verification_intelligence.gate",
        description="Measure the Universal Verification Intelligence laws (read-only).",
    )
    parser.add_argument("--gate", action="store_true", help="fail closed on any refused law")
    parser.add_argument("--json", action="store_true", help="emit the report as JSON")
    parser.add_argument("--quiet", action="store_true", help="suppress the rendered report")
    parser.add_argument("--declaration", default=None, help="declaration path override")
    args = parser.parse_args(argv)

    try:
        report = measure(declaration=args.declaration)
    except VerificationIntelligenceError as exc:
        print(f"UVI FAULT: {exc}", file=sys.stderr)
        return EXIT_FAULT

    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    elif not args.quiet:
        print(render(report))

    if report["laws_refused"]:
        if args.quiet:
            print(render(report), file=sys.stderr)
        return EXIT_INCOHERENT if args.gate else EXIT_COHERENT
    return EXIT_COHERENT


if __name__ == "__main__":  # pragma: no cover - CLI dispatch
    raise SystemExit(main())
