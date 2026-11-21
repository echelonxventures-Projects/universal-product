"""UAKOS-CLOSURE-009 — Universal Constitutional Assimilation Programme validation suite.

This suite exists because UCOS-RIB-001 measured the programme's engine as BOTH a dead
engine (``VER-11`` / ``GAP-DEAD-ENGINE``: no declared entry point named it) and an orphan
capability (``VER-09``: unreachable in every declared reachability dimension). REG-AUTO-001
P7 requires enforceability by *tooling gates* rather than author discipline — at least one
Makefile target, at least one workflow and at least one test. This file is the test leg of
that discharge, and it is deliberately not a smoke test: the consequence of the engine being
unreachable was that nothing re-ran it, so its committed registers were left rendered
against a stale HEAD and reported 89 inherited concept gaps that Repository Truth had
already closed. An engine no target names is an engine nobody re-runs, and a register nobody
re-runs is a register that silently stops being true.

What is proven here, in the order the defects actually appeared:

  * committed registers are CURRENT       — they agree with the closure register they measure
  * replay is stable across the commit    — the recorded HEAD is reused, never re-read
  * requirement identity is derived       — RR-<CONCEPT-ID>, total and injective, CREATE = 0
  * measurement is fail-closed            — an absent required input asserts no verdict
  * no wall-clock is emitted              — regeneration is reproducible
  * reachability is mechanized            — the Makefile and workflow legs cannot regress

The suite is read-only over the repository: it never invokes the engine's writing path, so
running it cannot modify a single register.
"""

from __future__ import annotations

import importlib.util
import json
import re
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
PROGRAM_DIR = REPO / "00-MASTER" / "UAKOS-CLOSURE-009"
ENGINE_PATH = PROGRAM_DIR / "requirement_engine.py"
RECORD_PATH = PROGRAM_DIR / "requirements.json"
CLOSURE_PATH = REPO / "00-MASTER" / "UAKOS-CLOSURE-002" / "closure.json"


def _load_engine():
    spec = importlib.util.spec_from_file_location("uakos_closure_009_engine", ENGINE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


re_ = _load_engine()


@pytest.fixture(scope="module")
def record() -> dict:
    return json.loads(RECORD_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def closure() -> dict:
    return json.loads(CLOSURE_PATH.read_text(encoding="utf-8"))


# --------------------------------------------------------- the registers are still true
def test_committed_register_measures_the_current_closure_register(record, closure):
    """The concrete defect: a register left behind by an engine nobody re-ran.

    Every one of these fields is COPIED from the closure register at render time, so a
    disagreement means the committed register was rendered against a superseded substrate.

    P0-FINAL-CONVERGENCE-001. The commit sha is deliberately NOT compared for equality with
    the live closure register. It cannot be: `closure.json` records `git rev-parse --short
    HEAD` at generation time, so requiring the COMMITTED register to carry it demands that a
    committed artifact carry the sha of the commit that carries it — the exact impossibility
    `_head_commit` exists to prevent, in this module's own words. Git history shows the chase
    it produced, four generations deep: a5ff49a recorded 75166e2, c4a3a10 recorded 89d3baf,
    32a0f36 recorded 05ce974, b71b1e8 recorded d64fbb8 — every register naming its
    predecessor, one commit message reading "the register catches up to the commit that moved
    the corpus". The equality was therefore unsatisfiable at EVERY committed state, and once
    verify.sh regenerates closure.json on every run it fails at every commit rather than
    erroring on an absent file.

    What must agree is the MEASUREMENT the register copied, not the provenance sha. The three
    substantive fields below are what actually detect the original defect (a stale register
    reporting 89 phantom gaps Repository Truth had closed): a register rendered against a
    superseded substrate disagrees on determination, gap_total or concept_total. Detection is
    preserved; only the unsatisfiable provenance equality is dropped, and the sha is still
    required to be present and non-empty.
    """
    baseline = record["baseline"]
    assert str(baseline["closure_baseline_commit"]).strip(), "no closure baseline recorded"
    assert baseline["closure_determination"] == closure["determination"]
    assert baseline["closure_gap_total"] == closure["gap_total"]
    assert baseline["concept_total"] == closure["concept_total"]


def test_no_inherited_concept_gap_is_reported_once_closure_reports_none(record, closure):
    """The 89 phantom gaps. A stale register cannot invent a gap the closure has closed."""
    assert closure["gap_total"] == 0, "closure itself reports gaps — this assertion is void"
    inherited = [
        finding
        for finding in record["systemic_findings"]
        if "inherit" in json.dumps(finding).lower()
    ]
    for finding in inherited:
        assert finding.get("count", 0) == 0, f"stale inherited gap still reported: {finding}"


def test_every_requirement_is_homed_when_the_closure_homes_every_concept(record):
    unhomed = [r["requirement_id"] for r in record["requirements"] if not r["homed"]]
    assert unhomed == [], f"unhomed requirements: {unhomed[:10]}"


# ------------------------------------------------------------------- replay stability
def test_recorded_head_is_replayed_rather_than_re_read():
    """A committed artifact can never carry the sha of the commit that carries it.

    Without this the registers drift by exactly one field on every commit, which is why a
    byte-for-byte drift gate over this programme was previously unenforceable.
    """
    replayed = re_._head_commit({"baseline": {"head_commit": "deadbee"}})
    assert replayed == "deadbee"


def test_live_head_is_used_when_no_record_is_replayed():
    live = re_._head_commit(None)
    assert live and live != "deadbee"


def test_absent_or_blank_recorded_head_falls_back_and_never_yields_empty():
    for degenerate in ({}, {"baseline": {}}, {"baseline": {"head_commit": "  "}}):
        resolved = re_._head_commit(degenerate)
        assert resolved, f"{degenerate} produced an empty head commit"


def test_inherited_closure_facts_are_replayed_rather_than_re_read():
    """The head was not the only field that drifts; the inherited ones did too.

    ``closure.json`` is gitignored and rebuilt by whichever site ran last, so its
    ``baseline_commit`` and ``branch`` record THAT run's environment. The registers carried
    both verbatim, so the drift gate compared a committed ``closure_baseline_commit`` against
    the sha of whatever commit happened to be checked out — red on every commit after the one
    that wrote it, and red on every runner whose branch name differed. The head was replayed
    and these two, one line above it, were not.
    """
    record = {"baseline": {"closure_baseline_commit": "1713d64d", "branch": "main"}}
    assert re_._replayed_input_fact(record, "closure_baseline_commit", "0df90e1a") == "1713d64d"
    assert re_._replayed_input_fact(record, "branch", "some/other-branch") == "main"


#: Data artifacts sitting in an evidence position that no EVIDENCE_KINDS pattern reaches.
#: A ceiling, not a target: it equals the measurement, because headroom above a measurement is
#: exactly where a new blind spot lives unnoticed. Lower it by widening a pattern or by showing
#: the artifact is not evidence; never raise it to accommodate one.
EVIDENCE_BLIND_SPOT_CEILING = 56


def _evidence_blind_spots() -> list[str]:
    """Artifacts the repository files as evidence that the kind patterns cannot see."""
    position = re.compile(
        r"(?:^|/)_?evidence/|-evidence[^/]*\.json$|-report[^/]*\.(?:json|md)$"
        r"|(?:^|/)determinism|(?:^|/)certification|(?:^|/)validation|(?:^|/)verification",
        re.I,
    )
    tracked = subprocess.run(  # noqa: S603 - fixed argv, no shell
        ["git", "ls-files"],  # noqa: S607 - git from PATH, as the suite does elsewhere
        cwd=REPO,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.split()
    blind: list[str] = []
    for kind, pattern in re_.EVIDENCE_KINDS:
        for path in tracked:
            if (
                path.endswith((".json", ".md"))
                and kind.lower() in path.lower()
                and position.search(path)
                and not pattern.search(path)
            ):
                blind.append(f"{kind}: {path}")
    return sorted(blind)


def test_no_new_evidence_the_kind_patterns_cannot_see():
    """The census. Four blind spots were found by accident this session; this finds the fifth.

    Every one had the same shape — a pattern reading a narrower world than the repository
    writes. `determinism-evidence` matched while `determinism.json` did not, so BC-06 reported
    "0 of 318 implemented requirements carry determinism evidence" with 47 such files on disk.
    Validation accepted only `.json` while verification already accepted one `.md` name, so
    `05-VALIDATION-REPORT.md` was invisible beside its counted sibling. Each was discovered
    while chasing something else, which is not a method.

    A blind spot is not proof of a defect — an artifact may name a kind and not be evidence of
    it. It is proof that somebody should LOOK. The ratchet refuses growth so the looking
    happens when the artifact appears, rather than years later when a gate reports a zero
    nobody believes.
    """
    blind = _evidence_blind_spots()
    assert len(blind) <= EVIDENCE_BLIND_SPOT_CEILING, (
        f"{len(blind)} evidence artifacts are unreachable by any kind pattern, ceiling is "
        f"{EVIDENCE_BLIND_SPOT_CEILING}. Either widen the pattern or establish that these are "
        "not evidence:\n  " + "\n  ".join(blind[:15])
    )


def test_the_blind_spot_ceiling_equals_the_measurement():
    """A ceiling above the measurement is room a regression occupies in silence."""
    assert len(_evidence_blind_spots()) == EVIDENCE_BLIND_SPOT_CEILING


def test_identity_is_asked_of_the_identity_authority_not_the_corpus_registry():
    """A home outside the corpus still holds an identity, and RG-E03 must not deny it.

    `00-BOOK/DATA/artifacts.json` is the CORPUS REGISTRY: it answers which files are
    Repository Corpus. `00-BOOK/DATA/id-ledger.json` is the identity authority under
    UCKP-ART-05. The two populations differ BY DETERMINATION — config.py excludes 00-MASTER/
    because UCOS-RECON-C1 classes the Master Context System as Operational Memory, "execution
    state, not corpus: it must never consume permanent corpus identities".

    Reading identity from the registry alone therefore reported 15 requirements as having a
    canonical home carrying no universal identity when every one held one, and demanded a
    remedy — register them — that the same declaration forbids. That is a gap nobody could
    ever close by doing the thing it asked for. This pins the fix: every requirement whose
    home appears in the ledger resolves an identity, whichever register carries it.
    """
    record = json.loads(
        (REPO / "00-MASTER/UAKOS-CLOSURE-009/requirements.json").read_text(encoding="utf-8")
    )
    ledger = json.loads((REPO / "00-BOOK/DATA/id-ledger.json").read_text(encoding="utf-8"))
    identified = {
        path
        for scope in ("by_path", "by_object")
        for path, entry in (ledger.get(scope) or {}).items()
        if str((entry or {}).get("universal_id") or "").strip()
    }

    denied = [
        r["requirement_id"]
        for r in record["requirements"]
        if r["universal_id"] == "UNREGISTERED"
        and any(home in identified for home in (r.get("definitional_homes") or []))
    ]
    assert not denied, (
        "these requirements hold a home the id-ledger identifies, yet are reported as carrying "
        "no universal identity:\n  "
        + "\n  ".join(denied[:12])
        + "\nIdentity is the ledger's question; corpus membership is the registry's."
    )

    homeless = [r for r in record["requirements"] if not (r.get("definitional_homes") or [])]
    unregistered = [r for r in record["requirements"] if r["universal_id"] == "UNREGISTERED"]
    assert len(unregistered) == len(homeless), (
        f"{len(unregistered)} requirements are reported unregistered but {len(homeless)} have no "
        "home at all — the count must be one thing measured once, not two conflated"
    )


def test_the_band_unit_register_still_agrees_with_the_evidence_it_transcribes():
    """A register transcribed from evidence goes stale the moment the evidence moves.

    `02-MASTER/EC-3-BAND-REALIZATION-UNIT-REGISTER.md` is the definitional home of 47 EC-3
    band realization units, and every cell in it was transcribed from `*/_evidence/<unit>/`.
    It is committed rather than generated, deliberately: a generated artifact here is
    gitignored, absent from a fresh clone, and therefore cannot be a home. The cost of that
    choice is that nothing re-derives it, which is exactly how this programme's own registers
    were left rendered against a stale HEAD reporting 89 gaps Repository Truth had closed.

    So the transcription is checked rather than trusted: every unit the register claims must
    still have its evidence directory, and the blueprint and verdict it prints must still be
    what the evidence says. A unit whose evidence is deleted or whose acceptance changes
    fails here rather than being discovered later as an unowned concept.
    """
    register = REPO / "02-MASTER" / "EC-3-BAND-REALIZATION-UNIT-REGISTER.md"
    if not register.is_file():
        pytest.skip("the band unit register is not installed in this working tree")

    rows = re.findall(
        r"^\|\s*\*\*(EC3-B\d+-U\d+)\*\*\s*\|\s*`([^`]+)`\s*\|[^|]*\|\s*([^|]+?)\s*\|",
        register.read_text(encoding="utf-8"),
        re.M,
    )
    assert rows, "the register claims no units — the transcription check would be vacuous"

    drift = []
    for unit, blueprint, verdict in rows:
        matches = sorted(REPO.glob(f"*/_evidence/{unit}/acceptance-decision.json"))
        if not matches:
            drift.append(f"{unit}: register claims it, but no acceptance-decision.json remains")
            continue
        decision = json.loads(matches[0].read_text(encoding="utf-8"))
        if str(decision.get("blueprint_id")) != blueprint:
            drift.append(
                f"{unit}: register prints blueprint {blueprint}, evidence says "
                f"{decision.get('blueprint_id')}"
            )
        if str(decision.get("verdict")) != verdict.strip():
            drift.append(
                f"{unit}: register prints verdict {verdict.strip()}, evidence says "
                f"{decision.get('verdict')}"
            )

    assert not drift, (
        "the band unit register no longer agrees with the evidence it transcribes:\n  "
        + "\n  ".join(drift)
        + "\nRe-derive the register from */_evidence/ — a transcription nobody re-checks is a "
        "register that silently stops being true."
    )


def test_a_genuine_regeneration_still_advances_the_inherited_facts():
    """Replay preserves; regeneration must NOT, or the register could never become current."""
    assert re_._replayed_input_fact(None, "closure_baseline_commit", "0df90e1a") == "0df90e1a"
    for degenerate in ({}, {"baseline": {}}, {"baseline": {"branch": "   "}}):
        assert re_._replayed_input_fact(degenerate, "branch", "live-value") == "live-value"


def test_render_mode_is_declared_by_the_makefile_replay_target():
    makefile = (REPO / "Makefile").read_text(encoding="utf-8")
    assert "\nclosure009-replay:\n" in makefile
    assert "--render --quiet" in makefile


# ------------------------------------------------- the population bound this suite inherits
def test_every_closure_engine_invocation_declares_the_repo_only_scope():
    """The population document is only bounded by declaration if EVERY producer says so.

    This suite's requirements are derived from ``00-MASTER/UAKOS-CLOSURE-002/closure.json``,
    which is gitignored and therefore regenerated by whichever site ran last. That engine
    records one of three scan modes, and the disclosure it writes names this programme as an
    inheritor by name: "Consumers projecting this document as a population — notably the
    ownership determination — inherit this bound." The external corpus at ``../UCOS`` exists
    in no clone, so a site that does not declare ``CLOSURE_SKIP_CORPUS=1`` records
    ``repo-only (undeclared — corpus absent)`` with ``population_complete = False``: the same
    549 concepts, bounded by accident rather than by a constituent act. Two sites disagreeing
    is worse than either answer, because the disclosure then describes the last runner rather
    than the repository, and CI and a developer clone stop meaning the same thing.

    The declaration is therefore a property of the invocation SURFACE, not of a caller's
    shell, and this test is what makes a new undeclared site fail rather than silently
    narrow the population.
    """

    def declared(rel: str, lines: list[str], index: int) -> bool:
        line = lines[index]
        if "CLOSURE_SKIP_CORPUS" in line:
            return True  # an env prefix on the invocation itself
        if rel.endswith(".sh"):
            # a shell script keeps one environment, so an earlier export reaches this line
            return any("export CLOSURE_SKIP_CORPUS" in earlier for earlier in lines[:index])
        if rel.endswith(".yml"):
            # a workflow step's own `env:` block reaches it; a sibling step's does not, so
            # walk back only as far as the step this invocation belongs to
            for earlier in range(index, -1, -1):
                text = lines[earlier]
                if "CLOSURE_SKIP_CORPUS" in text:
                    return True
                if re.match(r"\s*-\s+(name|uses):", text):
                    return False
            return False
        if rel.endswith(".json"):
            # a declaration carries the invocation as an argv ARRAY, so the env prefix is a
            # sibling element a few lines above the engine path. Walk back only to the start
            # of this argv, so a neighbouring stage's declaration cannot vouch for this one.
            for earlier in range(index, -1, -1):
                text = lines[earlier]
                if "CLOSURE_SKIP_CORPUS" in text:
                    return True
                if '"argv"' in text:
                    return False
            return False
        # a Makefile runs every recipe line in a SEPARATE shell, so nothing but the line itself
        return False

    sites = []
    # THE SURFACE LIST IS ITSELF A SURFACE, AND IT WAS INCOMPLETE. This test names the
    # places an invocation can live, and the RFP pipeline declaration was not one of them
    # — so STAGE-CLOSURE invoked the engine undeclared for as long as it has existed, and
    # the disagreement this test exists to prevent ran unobserved: one pass produced
    # closure.json twice with two substances, and two registers oscillated between them.
    for rel in [
        "Makefile",
        "scripts/generate-prerequisites.sh",
        "00-MASTER/UCOS-RFP-001/rfp-declaration.json",
    ] + [
        str(path.relative_to(REPO)) for path in sorted((REPO / ".github/workflows").glob("*.yml"))
    ]:
        path = REPO / rel
        if not path.is_file():
            continue
        lines = path.read_text(encoding="utf-8").splitlines()
        for index, line in enumerate(lines):
            if "UAKOS-CLOSURE-002/closure_engine.py" not in line or line.lstrip().startswith("#"):
                continue
            sites.append((rel, index + 1, line, declared(rel, lines, index)))

    assert sites, "no closure_engine invocation site found — this law would be vacuous"
    undeclared = [f"{rel}:{number}: {line.strip()}" for rel, number, line, ok in sites if not ok]
    assert not undeclared, (
        "closure_engine.py is invoked without declaring the repo-only scope at:\n  "
        + "\n  ".join(undeclared)
        + "\nDeclare CLOSURE_SKIP_CORPUS=1 at the invocation site, or the population it "
        "writes is bounded by accident and this programme inherits that bound."
    )


# ------------------------------------------------------- derived, injective identity
def test_requirement_identity_is_a_derived_function_of_concept_identity(record):
    for requirement in record["requirements"]:
        assert requirement["requirement_id"] == f"RR-{requirement['concept_id']}"


def test_requirement_identity_is_injective_and_total_over_the_concepts(record, closure):
    ids = [r["requirement_id"] for r in record["requirements"]]
    concept_ids = [r["concept_id"] for r in record["requirements"]]
    assert len(set(ids)) == len(ids), "requirement identity is not injective"
    assert len(set(concept_ids)) == len(concept_ids)
    assert len(ids) == record["requirement_total"] == closure["concept_total"]


def test_the_programme_creates_no_concept(record):
    assimilation = record["assimilation"]
    assert assimilation["created_concepts"] == 0
    assert assimilation["reused_concepts"] == record["requirement_total"]


def test_every_requirement_carries_exactly_one_canonical_owner(record):
    for requirement in record["requirements"]:
        owner = requirement["canonical_owner"]
        assert isinstance(owner, str) and owner.strip(), requirement["requirement_id"]


# ------------------------------------------------------------------------ fail-closed
def test_a_required_input_that_is_absent_asserts_no_verdict(monkeypatch, tmp_path):
    """Exit 2, not a verdict. A measurement over an unknown substrate is not a measurement."""
    monkeypatch.setattr(re_, "REPO", tmp_path)
    assert re_.main([]) == 2


def test_gate_flags_are_recognised_by_the_engine():
    source = ENGINE_PATH.read_text(encoding="utf-8")
    for flag in ("--gate", "--baseline-gate", "--render", "--quiet"):
        assert flag in source, f"{flag} is not recognised"


# ------------------------------------------------------------------- reproducibility
def test_no_wall_clock_is_emitted():
    source = ENGINE_PATH.read_text(encoding="utf-8")
    for forbidden in ("datetime", "time.time", "strftime", "import random", "random."):
        assert forbidden not in source, f"{forbidden} would make regeneration irreproducible"


def test_the_record_carries_a_content_seal(record):
    seal = record["seal_sha256"]
    assert isinstance(seal, str) and len(seal) == 64


# ------------------------------------------------ REG-AUTO-001 P7, mechanized
# The dead-engine and orphan findings are only discharged while all three legs exist.
# Asserting them here is what stops the discharge from silently regressing: deleting the
# target or the workflow now breaks a test instead of quietly re-creating a dead engine.
def test_a_makefile_target_names_the_engine():
    makefile = (REPO / "Makefile").read_text(encoding="utf-8")
    assert "00-MASTER/UAKOS-CLOSURE-009/requirement_engine.py" in makefile
    for target in ("closure009", "closure009-gate", "closure009-baseline-gate"):
        assert f"\n{target}:" in makefile, f"{target} is not declared"


def test_the_engine_targets_depend_on_the_predecessor_model():
    """The engine measures the PHASE-002/003 models; an unregenerated predecessor would
    make it measure a superseded substrate."""
    makefile = (REPO / "Makefile").read_text(encoding="utf-8")
    for target in ("closure009", "closure009-gate", "closure009-baseline-gate"):
        assert f"\n{target}: closure-phase3\n" in makefile, f"{target} bypasses closure-phase3"
    assert "\nclosure-phase3:" in makefile


def test_a_workflow_names_the_engine():
    workflow = REPO / ".github" / "workflows" / "closure009-gate.yml"
    assert workflow.is_file(), "the CI leg of REG-AUTO-001 P7 is absent"
    body = workflow.read_text(encoding="utf-8")
    assert "00-MASTER/UAKOS-CLOSURE-009/requirement_engine.py" in body
    assert "closure009-replay" in body


def test_this_test_is_collected_by_the_canonical_test_runner():
    """This file sits inside a DISCOVERED test root, so `pytest` with no arguments runs it.

    UCOS-CL-008 — the assertion was a literal match on the full testpaths line, which made
    it a change-detector for that string rather than a check of the property it names: a
    legitimate ADDITION to the canonical collection broke it.

    UCI-000001 — and it broke again, the same way, for the same reason. Reading ``testpaths``
    as a single LINE is still a formatting assertion: when the list grew past one line (four
    more roots were admitted, wiring up 3,995 tests that no runner collected), ``startswith
    ("testpaths")`` matched ``testpaths = [`` and every root moved to a line this check never
    read. Twice is a pattern, so the scrape was replaced by a TOML parse.

    UCOS-OMEGA-001 — and a TOML parse broke it a THIRD time, because it was still a question
    about a LIST. ``testpaths`` no longer exists: Ω-1 derives the collection set from which
    directories hold suites, so the honest form of this check is to ask the derivation whether it
    collects this file. That question has no formatting to be sensitive to and no list to fall out
    of, and it now also covers the roots the old three-name check never mentioned.
    """
    from engine.universal_discovery import discovery, graph

    tracked = discovery.tracked_python(str(REPO))
    import_graph = graph.ImportGraph(str(REPO), tracked)
    test_roots = discovery.derive_test_roots(tracked, graph.imported_by_path(import_graph, tracked))
    discovery.assert_suite_exists(test_roots)

    relative = Path(__file__).resolve().relative_to(REPO).as_posix()
    assert any(relative.startswith(root + "/") for root in test_roots), (
        f"{relative} is inside no discovered test root, so the canonical runner does not collect "
        f"it: {test_roots}"
    )
    # The omission that left the RIE coverage-isolation regression collected by nothing, pinned by
    # name rather than described — and the four layers whose 3,995 passing tests no runner ran.
    for root in (
        "engine/tests",
        "platform/tests",
        "intelligence/tests",
        "service/tests",
        "data/tests",
        "application/tests",
        "infrastructure/tests",
    ):
        assert root in test_roots, f"{root} is not discovered as a test root: {test_roots}"
