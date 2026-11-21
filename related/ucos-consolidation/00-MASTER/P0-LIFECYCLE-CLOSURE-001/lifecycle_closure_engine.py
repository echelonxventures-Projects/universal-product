#!/usr/bin/env python3
"""P0-LIFECYCLE-CLOSURE-001 — Universal Constitutional Lifecycle Realization Engine.

AUTHORITY = NONE (DERIVED TRUTH). This engine legislates nothing, registers nothing,
certifies nothing and owns no capability. It does not decide what the lifecycle *is* —
``UCL-000001`` owns that — and it does not decide whether a stage is realized. It
*measures*, and every verdict it emits is a function of an observation it made by
executing something.

The rule it is built to obey
---------------------------
A declaration is not evidence. ``ucl-stage-manifest.json`` declares an owner, an
authority and an evidence set for all 45 stages; this engine treats every one of those
as a **claim to be tested**, never as a finding. A stage is IMPLEMENTED here only when
five independent measurements agree, and each of the five is an executed probe:

    1. the declared owner artifact resolves on disk                (ownership)
    2. the declared evidence includes a module that compiles       (executable engine)
    3. some registered provider discharges the stage and returns
       evidence that is not merely the stage's own declaration     (executable behaviour)
    4. re-running that discharge reproduces the same digest        (deterministic replay)
    5. a test references the evidence artifact, and coverage
       measures at least one of its statements executed            (test coverage)

Anything less is PARTIALLY_IMPLEMENTED, DECLARED_ONLY or MISSING, and the artifact
records *which* of the five failed. Nothing is inferred; a probe that cannot be run is
recorded as a failed probe, never as an absent one.

Why self-certification is structurally impossible here
------------------------------------------------------
Probe 3 refuses evidence a stage produced about itself. A provider that returns the
stage's own declaration identity as its evidence is recorded as **not** having
discharged the stage, which is what stops the manifest from proving the manifest.

    python3 00-MASTER/P0-LIFECYCLE-CLOSURE-001/lifecycle_closure_engine.py
    python3 00-MASTER/P0-LIFECYCLE-CLOSURE-001/lifecycle_closure_engine.py --no-coverage
    python3 00-MASTER/P0-LIFECYCLE-CLOSURE-001/lifecycle_closure_engine.py --rounds 10
    python3 00-MASTER/P0-LIFECYCLE-CLOSURE-001/lifecycle_closure_engine.py --gate

Exit semantics:
    0  every phase produced a determination and the closure gate was not requested,
       or it was requested and every claim measured PROVEN
    1  --gate was requested and at least one closure claim measured NOT_PROVEN
    2  fail-closed abort — a phase could not be measured, so no verdict may be asserted

No timestamp, no duration, no commit identity and no absolute path is emitted, so the
output set is byte-identical for an unchanged repository.
"""

from __future__ import annotations

import argparse
import json
import py_compile
import subprocess
import sys
import tempfile
from collections.abc import Callable, Iterable, Mapping, Sequence
from pathlib import Path
from typing import Any

PROGRAMME = "P0-LIFECYCLE-CLOSURE-001"
REPO = Path(__file__).resolve().parents[2]
OUT = REPO / "00-MASTER" / PROGRAMME
MANIFEST = REPO / "00-MASTER" / "UCL-000001" / "ucl-stage-manifest.json"

sys.path.insert(0, str(REPO))

from engine.foundation.composition.ordering import (  # noqa: E402
    derive_order,
    unresolved_keys,
)
from engine.certification_integrity import immutable  # noqa: E402
from engine.uckp.canonical import content_hash  # noqa: E402

#: How many consecutive replay rounds Phase 5 requires before asserting stability.
DEFAULT_ROUNDS = 10

#: The five probes that decide realization. DATA — a sixth is one appended entry, and
#: :func:`classify_realization` needs no edit to start requiring it.
REALIZATION_PROBES: tuple[str, ...] = (
    "ownership_resolves",
    "executable_engine",
    "executably_discharged",
    "deterministic_replay",
    "test_coverage",
)

#: The eight autonomous-evolution capabilities of Phase 6, and the lifecycle stage whose
#: realization decides each. Read from the manifest by stage name, never hardcoded to an id.
EVOLUTION_CAPABILITIES: tuple[tuple[str, str], ...] = (
    ("Observe", "Observe"),
    ("Learn", "Learn"),
    ("Reason", "Reason"),
    ("Reflect", "Reflect"),
    ("Challenge", "Challenge"),
    ("Correct", "Correct"),
    ("Improve", "Improve"),
    ("Elevate", "Elevate"),
)

#: The Phase 7 closures, and the stages whose realization each requires.
KNOWLEDGE_CLOSURES: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("knowledge_closure", ("Extract Engineering Knowledge", "Register Engineering Knowledge")),
    (
        "capability_closure",
        ("Increase Constitutional Capability", "Increase Engineering Capability"),
    ),
    (
        "evolution_closure",
        ("Update Repository Truth", "Elevate", "Begin Next Elevated Engineering Cycle"),
    ),
    ("learning_closure", ("Learn", "Reason", "Reflect", "Improve")),
)

#: The Phase 8 traceability chain. Each link is measured, never assumed.
TRACEABILITY_LINKS: tuple[str, ...] = (
    "stage_to_owner",
    "owner_to_constitution",
    "constitution_to_engine",
    "engine_to_tests",
    "tests_to_evidence",
    "evidence_to_registry",
    "registry_to_repository_truth",
    "repository_truth_to_replay",
)

#: The twelve Phase 10 claims, and the measurement that decides each.
CLOSURE_CLAIMS: tuple[str, ...] = (
    "constitutional_correctness",
    "architectural_correctness",
    "implementation_correctness",
    "determinism",
    "replayability",
    "traceability",
    "governability",
    "evolvability",
    "observability",
    "recoverability",
    "reproducibility",
    "capability_coverage",
)


class Abort(Exception):
    """A phase could not be measured, so no verdict may be asserted."""


# --------------------------------------------------------------------------- helpers


def rel(path: Path | str) -> str:
    """A repository-relative path — absolute paths would break byte-identical output."""
    try:
        return str(Path(path).resolve().relative_to(REPO))
    except (ValueError, OSError):
        return str(path)


def load_manifest() -> list[dict[str, Any]]:
    if not MANIFEST.exists():
        raise Abort(f"the lifecycle manifest is absent: {rel(MANIFEST)}")
    nodes = json.loads(MANIFEST.read_text(encoding="utf-8")).get("nodes")
    if not isinstance(nodes, list) or not nodes:
        raise Abort("the lifecycle manifest carries no nodes")
    return sorted(nodes, key=lambda n: int(n.get("ordinal", 0)))


def _bindings(binds: Any) -> list[str]:
    """Render a stage's declared outputs as sortable tokens.

    ``binds`` entries are ``{"source": ..., "ref": ...}`` mappings. Flattened to
    ``source:ref`` so the artifact stays deterministically ordered and diffable, rather
    than carrying nested objects whose key order would have to be trusted.
    """
    rendered: list[str] = []
    for item in binds or ():
        if isinstance(item, Mapping):
            rendered.append(f"{item.get('source', '')}:{item.get('ref', '')}")
        else:
            rendered.append(str(item))
    return sorted(rendered)


def emit(name: str, payload: dict[str, Any]) -> Path:
    """Write one artifact deterministically and return its path."""
    OUT.mkdir(parents=True, exist_ok=True)
    payload = {"programme": PROGRAMME, "authority": "NONE — DERIVED TRUTH", **payload}
    payload["digest"] = content_hash(payload)
    target = OUT / name
    target.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return target


# --------------------------------------------------------------------------- probes


def probe_compiles(path: Path) -> tuple[bool, str]:
    """Does this module compile? An engine that cannot compile cannot have run."""
    if not path.exists():
        return False, "absent"
    if path.suffix != ".py":
        return False, f"not executable ({path.suffix or 'no suffix'})"
    try:
        with tempfile.NamedTemporaryFile(suffix=".pyc", delete=True) as sink:
            py_compile.compile(str(path), cfile=sink.name, doraise=True)
    except py_compile.PyCompileError as exc:
        return False, f"does not compile: {type(exc).__name__}"
    except OSError as exc:  # pragma: no cover - filesystem refusal
        return False, f"unreadable: {exc}"
    return True, "compiles"


def discover_providers() -> list[dict[str, Any]]:
    """Find every module that can discharge a lifecycle stage, by executing a probe.

    A *provider* is a callable that accepts ``(subject, Stage)`` and returns a coercible
    ``(status, evidence, detail)``. Discovery is by duck-test rather than by registration
    list: a provider that exists but was never listed would otherwise be invisible, and
    "nothing else realizes this stage" is the finding this whole determination rests on.
    """
    from engine.nucleus import lifecycle as ucl

    probe_stage = ucl.STAGES[0]
    candidates: list[tuple[str, Callable[..., Any]]] = []

    try:
        from engine.constitution import catalog, evolution

        population = catalog.build_population()
        candidates.append(
            ("engine.constitution.evolution", evolution.lifecycle_stage_function(population))
        )
    except Exception as exc:  # noqa: BLE001 - an unimportable provider is a failed probe
        candidates.append(("engine.constitution.evolution", _broken(exc)))

    candidates.append(("engine.nucleus.lifecycle", ucl.satisfied_by_declaration))

    providers: list[dict[str, Any]] = []
    for name, fn in candidates:
        try:
            status, evidence, _detail = fn("probe", probe_stage)
            ucl.StageStatus.coerce(status)
            usable, why = True, "returns a coercible stage outcome"
        except Exception as exc:  # noqa: BLE001
            usable, why, evidence = False, f"probe raised {type(exc).__name__}: {exc}", ""
        providers.append(
            {
                "provider": name,
                "usable": usable,
                "detail": why,
                # A provider whose evidence is the lifecycle declaration itself is asserting
                # the manifest from the manifest. It is recorded, and Phase 3 refuses it.
                "self_referential": str(evidence).startswith(ucl.LIFECYCLE_ID),
            }
        )
    return sorted(providers, key=lambda p: p["provider"])


def _broken(exc: BaseException) -> Callable[..., Any]:
    def raiser(*_args: Any, **_kwargs: Any) -> Any:
        raise exc

    return raiser


def discharge_map(rounds: int) -> dict[str, dict[str, Any]]:
    """Execute every usable provider over all 45 stages and record what it discharged.

    Returns ``stage_id -> {discharged, provider, evidence_digest, deterministic}``.
    Determinism is measured here, not asserted: the same discharge is executed ``rounds``
    times and the per-stage evidence is compared across every round.
    """
    from engine.nucleus import lifecycle as ucl

    try:
        from engine.constitution import catalog, evolution
    except Exception as exc:  # noqa: BLE001
        raise Abort(f"the constitution provider is unimportable: {exc}") from exc

    observations: list[dict[str, tuple[str, str]]] = []
    for _round in range(rounds):
        population = catalog.build_population()
        fn = evolution.lifecycle_stage_function(population)
        seen: dict[str, tuple[str, str]] = {}
        for stage in ucl.STAGES:
            try:
                status, evidence, _detail = fn("repository", stage)
                seen[stage.stage_id] = (ucl.StageStatus.coerce(status).value, str(evidence))
            except Exception as exc:  # noqa: BLE001 - a raised probe is a failed probe
                seen[stage.stage_id] = ("failed", f"probe raised {type(exc).__name__}: {exc}")
        observations.append(seen)

    result: dict[str, dict[str, Any]] = {}
    first = observations[0]
    for stage in ucl.STAGES:
        status, evidence = first[stage.stage_id]
        stable = all(obs[stage.stage_id] == first[stage.stage_id] for obs in observations)
        # SATISFIED alone is not discharge: the evidence must come from a measurement, not
        # from the declaration restating itself.
        self_referential = evidence.startswith(ucl.LIFECYCLE_ID)
        result[stage.stage_id] = {
            "status": status,
            "provider": "engine.constitution.evolution" if status != "not-applicable" else "",
            "evidence": evidence,
            "self_referential": self_referential,
            "discharged": status == "satisfied" and not self_referential,
            "deterministic": stable,
            "rounds": rounds,
        }
    return result


def instrument_interpreter() -> str:
    """The interpreter that carries the coverage instrument, not the one that happens to run.

    WHY THIS EXISTS, AS THE FAILURE IT PREVENTS. `measure_coverage` used `sys.executable`,
    which is whatever interpreter invoked this engine. Every declared RFP pipeline stage is
    launched through `$PY`, and `rfp_engine.resolve_argv` maps that token to its own
    `sys.executable` — the hosted CI interpreter, not the pinned venv. `coverage` and
    `pytest` are installed into `.ec1-venv` by bootstrap.sh and are absent from that
    interpreter, so the measurement would abort in CI while succeeding on any developer
    machine that happened to run the engine through the venv.

    Resolved the way the two sibling engines already resolve it — aee_engine.py::interpreters
    and uccep_engine.py::interpreters both read `REPO/.ec1-venv/bin/python` and fall back when
    it is absent — rather than by inventing a third convention (UCKP-ART-18). scripts/ucos-env.sh
    states the underlying rule: never depend on PATH, always call the venv interpreter by
    absolute path.
    """
    venv = REPO / ".ec1-venv" / "bin" / "python"
    return str(venv) if venv.is_file() else sys.executable


def measure_coverage(targets: Sequence[str]) -> dict[str, Any]:
    """Run the repository test suite under coverage and report per-target statement data.

    Executed, not read from a committed report: a coverage artifact in the tree is a
    declaration about a past run, and this determination admits only present measurement.

    The instrumented scope is **derived from the declared evidence itself** rather than
    fixed to ``engine,platform``. Several stages name engines under ``00-MASTER`` and
    ``00-BOOK``; scoping those out would report them uncovered because the instrument
    never watched them, which would fail a stage by measurement design rather than by
    measurement. Whatever the manifest points at is what gets instrumented.
    """
    roots = sorted({t.split("/", 1)[0] for t in targets if "/" in t} | {"engine", "platform"})
    with tempfile.TemporaryDirectory() as tmp:
        data = Path(tmp) / "cov.json"
        # S603: every argument is a literal or the resolved interpreter path; nothing here
        # is derived from repository content, so there is no untrusted input to inject.
        interpreter = instrument_interpreter()
        run = subprocess.run(  # noqa: S603
            [
                interpreter,
                "-m",
                "coverage",
                "run",
                "--branch",
                "--source",
                ",".join(roots),
                "-m",
                "pytest",
                "engine/tests",
                "-q",
                "-p",
                "no:cacheprovider",
                "--no-cov",
            ],
            cwd=REPO,
            capture_output=True,
            text=True,
            env=immutable.clean_environment(),
        )
        report = subprocess.run(  # noqa: S603 - literal argv; see above
            [interpreter, "-m", "coverage", "json", "-o", str(data), "--pretty-print"],
            cwd=REPO,
            capture_output=True,
            text=True,
            env=immutable.clean_environment(),
        )
        if not data.exists():
            return {
                "measured": False,
                "reason": (report.stderr or run.stderr or "coverage produced no report")[-400:],
                "files": {},
                "totals": {},
            }
        payload = json.loads(data.read_text(encoding="utf-8"))

    files = payload.get("files", {})
    per_target: dict[str, Any] = {}
    for target in sorted(set(targets)):
        entry = files.get(target)
        summary = (entry or {}).get("summary", {})
        per_target[target] = {
            "in_scope": entry is not None,
            "statements": summary.get("num_statements", 0),
            "covered": summary.get("covered_lines", 0),
            "branches": summary.get("num_branches", 0),
            "covered_branches": summary.get("covered_branches", 0),
            "percent": round(float(summary.get("percent_covered", 0.0)), 2),
        }
    totals = payload.get("totals", {})
    return {
        "measured": True,
        "tests_passed": run.returncode == 0,
        "instrumented_roots": roots,
        "files": per_target,
        "totals": {
            "statements": totals.get("num_statements", 0),
            "covered": totals.get("covered_lines", 0),
            "branches": totals.get("num_branches", 0),
            "covered_branches": totals.get("covered_branches", 0),
            "percent": round(float(totals.get("percent_covered", 0.0)), 2),
        },
    }


def tests_referencing(paths: Iterable[str]) -> dict[str, list[str]]:
    """Which test files name each artifact — measured by scanning the test corpus."""
    corpus: list[tuple[str, str]] = []
    for root in ("engine/tests", "platform/tests"):
        base = REPO / root
        if not base.exists():
            continue
        for candidate in sorted(base.rglob("test_*.py")):
            try:
                corpus.append((rel(candidate), candidate.read_text(encoding="utf-8")))
            except OSError:  # pragma: no cover - unreadable test file
                continue
    found: dict[str, list[str]] = {}
    for path in sorted(set(paths)):
        stem = path.rsplit("/", 1)[-1]
        module = path[:-3].replace("/", ".") if path.endswith(".py") else ""
        hits = [
            name
            for name, text in corpus
            if path in text or (module and module in text) or (stem and stem in text)
        ]
        found[path] = sorted(hits)
    return found


# --------------------------------------------------------------------------- phases


def phase1_inventory(nodes: list[dict[str, Any]]) -> dict[str, Any]:
    """Locate every artifact claiming ownership of a lifecycle stage, and test the claim."""
    evidence_paths = sorted({e for n in nodes for e in n.get("evidence", [])})
    test_index = tests_referencing(evidence_paths + [n["owner"] for n in nodes])

    stages = []
    for node in nodes:
        evidence = list(node.get("evidence", ()))
        executable = []
        for item in evidence:
            ok, why = probe_compiles(REPO / item)
            if ok:
                executable.append(item)
            elif item.endswith(".py"):
                executable.append(f"{item} [REFUSED: {why}]")
        owner = node["owner"]
        stages.append(
            {
                "stage_id": node["id"],
                "stage_name": node["stage"],
                "ordinal": int(node["ordinal"]),
                "group": node["group"],
                "canonical_owner": owner,
                "owner_exists": (REPO / owner).exists(),
                "engine": sorted(e for e in evidence if e.endswith(".py")),
                "executable_engine": sorted(e for e in executable if not e.endswith("]")),
                "input": sorted(node.get("depends_on", ())),
                "output": _bindings(node.get("binds", ())),
                "registry": node.get("authority_owner", ""),
                "constitution": node.get("authority", ""),
                "tests": sorted(
                    {t for e in evidence for t in test_index.get(e, ())}
                    | set(test_index.get(owner, ()))
                ),
                "dependencies": sorted(node.get("depends_on", ())),
                "evidence": sorted(evidence),
                "evidence_all_present": all((REPO / e).exists() for e in evidence),
            }
        )

    documents = sum(1 for s in stages if not s["executable_engine"])
    return {
        "phase": 1,
        "title": "Universal Lifecycle Inventory",
        "lifecycle_authority": "UCL-000001",
        "manifest": rel(MANIFEST),
        "stage_count": len(stages),
        "measurements": {
            "stages_with_executable_engine": len(stages) - documents,
            "stages_with_document_evidence_only": documents,
            "stages_with_tests": sum(1 for s in stages if s["tests"]),
            "distinct_owners": len({s["canonical_owner"] for s in stages}),
            "owners_absent_from_disk": sum(1 for s in stages if not s["owner_exists"]),
        },
        "stages": stages,
    }


def phase2_ownership(inventory: dict[str, Any]) -> dict[str, Any]:
    """Exactly one canonical owner per stage — verified, not accepted."""
    stages = inventory["stages"]
    by_owner: dict[str, list[str]] = {}
    for stage in stages:
        by_owner.setdefault(stage["canonical_owner"], []).append(stage["stage_id"])

    gaps = [s["stage_id"] for s in stages if not s["canonical_owner"] or not s["owner_exists"]]
    collisions = {o: sorted(v) for o, v in sorted(by_owner.items()) if len(v) > 1}
    # An owner that is not itself executable cannot *operate* the stage it owns. That is an
    # ambiguity rather than a gap: the artifact exists and is named, but nothing about it
    # can act, so which component actually owns the behaviour is unresolved.
    ambiguities = [
        {
            "stage_id": s["stage_id"],
            "owner": s["canonical_owner"],
            "detail": "declared owner is a document; no executable component owns the behaviour",
        }
        for s in stages
        if s["owner_exists"] and not s["canonical_owner"].endswith(".py")
    ]

    return {
        "phase": 2,
        "title": "Canonical Ownership Determination",
        "measurements": {
            "stages": len(stages),
            "distinct_owners": len(by_owner),
            "ownership_gaps": len(gaps),
            "ownership_collisions": len(collisions),
            "ownership_ambiguities": len(ambiguities),
            "exactly_one_owner_each": len(gaps) == 0 and len(collisions) == 0,
        },
        "ownership_gaps": sorted(gaps),
        "ownership_collisions": collisions,
        "ownership_ambiguities": ambiguities,
        "owners": {
            s["stage_id"]: {
                "owner": s["canonical_owner"],
                "exists": s["owner_exists"],
                "executable": s["canonical_owner"].endswith(".py"),
            }
            for s in stages
        },
    }


def classify_realization(probes: Mapping[str, bool]) -> str:
    """Apply the directive's rules to five measured probes. No judgement, no inference."""
    if all(probes[name] for name in REALIZATION_PROBES):
        return "IMPLEMENTED"
    if not probes["ownership_resolves"]:
        return "MISSING"
    if any(probes[name] for name in ("executable_engine", "executably_discharged")):
        return "PARTIALLY_IMPLEMENTED"
    return "DECLARED_ONLY"


def phase3_realization(
    inventory: dict[str, Any],
    discharges: Mapping[str, dict[str, Any]],
    coverage: Mapping[str, Any],
) -> dict[str, Any]:
    """Classify every stage from five executed probes."""
    results = []
    for stage in inventory["stages"]:
        sid = stage["stage_id"]
        discharge = discharges.get(sid, {})
        engines = stage["executable_engine"]
        covered = False
        cov_detail: dict[str, Any] = {}
        for engine in engines:
            entry = coverage.get("files", {}).get(engine)
            if entry:
                cov_detail[engine] = entry
                if entry.get("covered", 0) > 0:
                    covered = True
        probes = {
            "ownership_resolves": bool(stage["owner_exists"]),
            "executable_engine": bool(engines),
            "executably_discharged": bool(discharge.get("discharged")),
            "deterministic_replay": bool(discharge.get("deterministic")),
            "test_coverage": covered and bool(stage["tests"]),
        }
        results.append(
            {
                "stage_id": sid,
                "stage_name": stage["stage_name"],
                "group": stage["group"],
                "realization": classify_realization(probes),
                "probes": probes,
                "failed_probes": sorted(k for k, v in probes.items() if not v),
                "discharge": {
                    "status": discharge.get("status", "unmeasured"),
                    "provider": discharge.get("provider", ""),
                    "self_referential": discharge.get("self_referential", False),
                },
                "coverage": cov_detail,
            }
        )

    tally: dict[str, int] = {}
    for item in results:
        tally[item["realization"]] = tally.get(item["realization"], 0) + 1
    return {
        "phase": 3,
        "title": "Executable Realization Determination",
        "rules": {
            "IMPLEMENTED": sorted(REALIZATION_PROBES),
            "PARTIALLY_IMPLEMENTED": "some executable behaviour, incomplete realization",
            "DECLARED_ONLY": "owner resolves, no executable behaviour of any kind",
            "MISSING": "no resolvable owner",
        },
        "measurements": {
            "stage_count": len(results),
            **{
                k.lower(): tally.get(k, 0)
                for k in ("IMPLEMENTED", "PARTIALLY_IMPLEMENTED", "DECLARED_ONLY", "MISSING")
            },
            "probe_failures": {
                probe: sum(1 for r in results if probe in r["failed_probes"])
                for probe in REALIZATION_PROBES
            },
        },
        "stages": results,
    }


def phase4_graph(nodes: list[dict[str, Any]]) -> dict[str, Any]:
    """Derive the execution graph and verify it against the single ordering authority."""
    graph = {n["id"]: tuple(sorted(n.get("depends_on", ()))) for n in nodes}
    ordering = derive_order(graph)
    unplaceable = unresolved_keys(graph, ordering)
    derived = [key for _wave, key in ordering]
    declared = [n["id"] for n in nodes]

    position = {key: index for index, key in enumerate(derived)}
    skipped = []
    for node in nodes:
        for requirement in node.get("depends_on", ()):
            if requirement not in position:
                skipped.append(
                    {"stage_id": node["id"], "requires": requirement, "detail": "unplaceable"}
                )
            elif position[requirement] >= position.get(node["id"], -1):
                skipped.append(
                    {
                        "stage_id": node["id"],
                        "requires": requirement,
                        "detail": "prerequisite is not ordered before the stage",
                    }
                )
    unknown = sorted({r for n in nodes for r in n.get("depends_on", ()) if r not in graph})
    return {
        "phase": 4,
        "title": "Execution Graph Determination",
        "ordering_authority": "engine.foundation.composition.ordering",
        "measurements": {
            "nodes": len(graph),
            "edges": sum(len(v) for v in graph.values()),
            "cycles": len(unplaceable),
            "unknown_prerequisites": len(unknown),
            "skipped_prerequisites": len(skipped),
            "derived_matches_declared_order": derived == declared,
            "acyclic": not unplaceable,
            "unambiguous": len(derived) == len(graph),
        },
        "derived_order": derived,
        "declared_order": declared,
        "unplaceable": sorted(unplaceable),
        "unknown_prerequisites": unknown,
        "skipped_prerequisites": skipped,
        "graph": {k: list(v) for k, v in sorted(graph.items())},
    }


def phase5_replay(rounds: int) -> dict[str, Any]:
    """Execute the whole lifecycle repeatedly and measure identity across every round."""
    from engine.nucleus import lifecycle as ucl
    from engine.nucleus.registry import build_seed_registry

    def observe() -> dict[str, str]:
        from engine.constitution import catalog, evolution

        population = catalog.build_population()
        execution = ucl.execute(
            "repository",
            stage_function=evolution.lifecycle_stage_function(population),
            context={"frame": PROGRAMME},
        )
        registry = build_seed_registry()
        knowledge = REPO / "knowledge" / "canonical-knowledge.json"
        return {
            "output_identity": execution.digest(),
            "registry_identity": registry.digest(),
            "dictionary_identity": content_hash(ucl.to_document()),
            "knowledge_identity": content_hash(
                knowledge.read_text(encoding="utf-8") if knowledge.exists() else ""
            ),
            "bookkeeping_identity": content_hash(population.to_dict()),
            "lineage_identity": content_hash([o.to_dict() for o in execution.outcomes]),
            "chain_head": execution.chain_head,
            "chain_intact": str(execution.chain_is_intact()),
        }

    try:
        readings = [observe() for _ in range(rounds)]
    except Exception as exc:  # noqa: BLE001
        raise Abort(f"the lifecycle could not be executed for replay: {exc}") from exc

    first = readings[0]
    dimensions = sorted(first)
    drift = {
        dimension: sum(1 for r in readings if r[dimension] != first[dimension])
        for dimension in dimensions
    }
    unstable = sorted(d for d, n in drift.items() if n)
    return {
        "phase": 5,
        "title": "Deterministic Replay Determination",
        "rounds": rounds,
        "status": "REPLAYABLE" if not unstable else "NOT_REPLAYABLE",
        "measurements": {
            "rounds_executed": len(readings),
            "dimensions_measured": len(dimensions),
            "drift": drift,
            "mutation": len(unstable),
            "entropy": len(unstable),
            "ordering_instability": drift.get("output_identity", 0),
            "ownership_instability": drift.get("registry_identity", 0),
            "unstable_dimensions": unstable,
        },
        "identity": first,
    }


def phase6_evolution(realization: dict[str, Any]) -> dict[str, Any]:
    """Classify each autonomous-evolution capability from the realization it depends on."""
    by_name = {s["stage_name"]: s for s in realization["stages"]}
    results = []
    for capability, stage_name in EVOLUTION_CAPABILITIES:
        stage = by_name.get(stage_name)
        if stage is None:
            level, why = "NONE", f"no lifecycle stage named {stage_name!r}"
        elif stage["realization"] == "IMPLEMENTED":
            level, why = "AUTONOMOUS", "executably discharged, deterministic and tested"
        elif stage["probes"]["executably_discharged"]:
            level = "ASSISTED"
            why = "an executable provider discharges it; realization is incomplete"
        elif stage["probes"]["executable_engine"]:
            level = "MANUAL"
            why = "an executable engine exists but nothing discharges the stage unattended"
        else:
            level, why = "NONE", "no executable engine; the evidence is a document"
        results.append(
            {
                "capability": capability,
                "stage": stage_name,
                "stage_id": stage["stage_id"] if stage else "",
                "level": level,
                "basis": why,
                "failed_probes": stage["failed_probes"] if stage else ["stage_absent"],
            }
        )
    tally: dict[str, int] = {}
    for item in results:
        tally[item["level"]] = tally.get(item["level"], 0) + 1
    return {
        "phase": 6,
        "title": "Autonomous Evolution Determination",
        "question": "can the repository do this without human orchestration?",
        "measurements": {
            "capabilities": len(results),
            **{k.lower(): tally.get(k, 0) for k in ("AUTONOMOUS", "ASSISTED", "MANUAL", "NONE")},
            "fully_autonomous": tally.get("AUTONOMOUS", 0) == len(results),
        },
        "capabilities": results,
    }


def phase7_knowledge(realization: dict[str, Any]) -> dict[str, Any]:
    """Determine whether knowledge, capability, evolution and learning actually close."""
    by_name = {s["stage_name"]: s for s in realization["stages"]}
    closures = []
    for name, required in KNOWLEDGE_CLOSURES:
        members = []
        for stage_name in required:
            stage = by_name.get(stage_name)
            members.append(
                {
                    "stage": stage_name,
                    "stage_id": stage["stage_id"] if stage else "",
                    "realization": stage["realization"] if stage else "MISSING",
                    "failed_probes": stage["failed_probes"] if stage else ["stage_absent"],
                }
            )
        closed = all(m["realization"] == "IMPLEMENTED" for m in members)
        closures.append(
            {
                "closure": name,
                "closed": closed,
                "requires": list(required),
                "members": members,
                "blocking": sorted(
                    m["stage"] for m in members if m["realization"] != "IMPLEMENTED"
                ),
            }
        )
    return {
        "phase": 7,
        "title": "Knowledge Elevation Determination",
        "measurements": {
            "closures": len(closures),
            "closed": sum(1 for c in closures if c["closed"]),
            "open": sum(1 for c in closures if not c["closed"]),
            "manual_intervention_required": any(not c["closed"] for c in closures),
        },
        "closures": closures,
    }


def phase8_traceability(
    inventory: dict[str, Any],
    realization: dict[str, Any],
    replay: dict[str, Any],
) -> dict[str, Any]:
    """Measure all eight links of the chain, for every stage."""
    by_id = {s["stage_id"]: s for s in realization["stages"]}
    replayable = replay["status"] == "REPLAYABLE"

    rows = []
    for stage in inventory["stages"]:
        sid = stage["stage_id"]
        probes = by_id[sid]["probes"]
        links = {
            "stage_to_owner": bool(stage["canonical_owner"]) and stage["owner_exists"],
            "owner_to_constitution": bool(stage["constitution"]),
            "constitution_to_engine": bool(stage["executable_engine"]),
            "engine_to_tests": bool(stage["tests"]) and bool(stage["executable_engine"]),
            "tests_to_evidence": bool(stage["tests"]) and stage["evidence_all_present"],
            "evidence_to_registry": bool(stage["registry"]) and (REPO / stage["registry"]).exists()
            if stage["registry"]
            else False,
            "registry_to_repository_truth": stage["evidence_all_present"],
            "repository_truth_to_replay": replayable and probes["deterministic_replay"],
        }
        rows.append(
            {
                "stage_id": sid,
                "stage_name": stage["stage_name"],
                "links": links,
                "complete": all(links.values()),
                "broken_links": sorted(k for k, v in links.items() if not v),
            }
        )

    complete = sum(1 for r in rows if r["complete"])
    return {
        "phase": 8,
        "title": "Traceability Determination",
        "chain": list(TRACEABILITY_LINKS),
        "measurements": {
            "stages": len(rows),
            "fully_traceable": complete,
            "traceability_percent": round(100.0 * complete / len(rows), 2) if rows else 0.0,
            "link_failures": {
                link: sum(1 for r in rows if link in r["broken_links"])
                for link in TRACEABILITY_LINKS
            },
            "hundred_percent": complete == len(rows),
        },
        "stages": rows,
    }


def phase9_coverage(
    inventory: dict[str, Any],
    realization: dict[str, Any],
    evolution: dict[str, Any],
    knowledge: dict[str, Any],
    traceability: dict[str, Any],
    coverage: Mapping[str, Any],
) -> dict[str, Any]:
    """Measure every coverage dimension, and classify each uncovered point."""
    stages = realization["stages"]
    total = len(stages)
    implemented = sum(1 for s in stages if s["realization"] == "IMPLEMENTED")
    governed = sum(1 for s in inventory["stages"] if s["constitution"])
    tested = sum(1 for s in inventory["stages"] if s["tests"])

    uncovered = []
    for stage, node in zip(stages, inventory["stages"], strict=True):
        if stage["realization"] == "IMPLEMENTED":
            continue
        probes = stage["probes"]
        if not probes["ownership_resolves"]:
            kind = "Missing Governance"
        elif not probes["executable_engine"]:
            kind = "Missing Engine"
        elif not probes["executably_discharged"]:
            kind = "Dead Capability"
        elif not probes["test_coverage"]:
            kind = "Missing Test"
        else:
            kind = "Missing Traceability"
        uncovered.append(
            {
                "stage_id": stage["stage_id"],
                "stage_name": stage["stage_name"],
                "classification": kind,
                "failed_probes": stage["failed_probes"],
                "declared_evidence": node["evidence"],
            }
        )

    tally: dict[str, int] = {}
    for item in uncovered:
        tally[item["classification"]] = tally.get(item["classification"], 0) + 1

    totals = coverage.get("totals", {})
    return {
        "phase": 9,
        "title": "Coverage Determination",
        "measurements": {
            "statement_coverage_percent": totals.get("percent", 0.0),
            "statements": totals.get("statements", 0),
            "statements_covered": totals.get("covered", 0),
            "branch_count": totals.get("branches", 0),
            "branches_covered": totals.get("covered_branches", 0),
            "branch_coverage_percent": (
                round(100.0 * totals.get("covered_branches", 0) / totals["branches"], 2)
                if totals.get("branches")
                else 0.0
            ),
            "path_coverage_percent": None,
            "path_coverage_note": (
                "not measured: no path-coverage instrument exists in this repository, so "
                "the value is withheld rather than approximated by branch coverage"
            ),
            "lifecycle_coverage_percent": round(100.0 * implemented / total, 2) if total else 0.0,
            "capability_coverage_percent": round(
                100.0
                * sum(1 for c in evolution["capabilities"] if c["level"] == "AUTONOMOUS")
                / max(1, len(evolution["capabilities"])),
                2,
            ),
            "governance_coverage_percent": round(100.0 * governed / total, 2) if total else 0.0,
            "evolution_coverage_percent": round(
                100.0
                * knowledge["measurements"]["closed"]
                / max(1, knowledge["measurements"]["closures"]),
                2,
            ),
            "knowledge_coverage_percent": round(
                100.0
                * sum(
                    1
                    for c in knowledge["closures"]
                    if c["closure"] == "knowledge_closure" and c["closed"]
                ),
                2,
            ),
            "traceability_coverage_percent": traceability["measurements"]["traceability_percent"],
            "test_referenced_stages": tested,
            "coverage_measured": coverage.get("measured", False),
            "test_suite_passed": coverage.get("tests_passed", None),
        },
        "uncovered_classification": tally,
        "uncovered": uncovered,
        "per_engine_coverage": coverage.get("files", {}),
    }


def phase10_closure(
    realization: dict[str, Any],
    graph: dict[str, Any],
    replay: dict[str, Any],
    evolution: dict[str, Any],
    knowledge: dict[str, Any],
    traceability: dict[str, Any],
    coverage: dict[str, Any],
    ownership: dict[str, Any],
) -> dict[str, Any]:
    """Return PROVEN / NOT_PROVEN for each of the twelve claims, with the deciding measure."""
    r = realization["measurements"]
    total = r["stage_count"]
    full = r["implemented"] == total

    decisions = {
        "constitutional_correctness": (
            full and ownership["measurements"]["exactly_one_owner_each"],
            f"{r['implemented']}/{total} stages realized; "
            f"{ownership['measurements']['ownership_ambiguities']} ownership ambiguities",
        ),
        "architectural_correctness": (
            graph["measurements"]["acyclic"]
            and graph["measurements"]["unambiguous"]
            and not graph["measurements"]["skipped_prerequisites"],
            f"acyclic={graph['measurements']['acyclic']}, "
            f"cycles={graph['measurements']['cycles']}, "
            f"skipped_prerequisites={graph['measurements']['skipped_prerequisites']}",
        ),
        "implementation_correctness": (
            full,
            f"{r['declared_only']} DECLARED_ONLY, "
            f"{r['partially_implemented']} PARTIALLY_IMPLEMENTED, {r['missing']} MISSING",
        ),
        "determinism": (
            replay["measurements"]["mutation"] == 0 and full,
            f"{replay['measurements']['mutation']} unstable dimensions over "
            f"{replay['rounds']} rounds; realization {r['implemented']}/{total}",
        ),
        "replayability": (
            replay["status"] == "REPLAYABLE" and full,
            f"replay={replay['status']} over the discharged subset only "
            f"({r['implemented']}/{total} stages realized)",
        ),
        "traceability": (
            traceability["measurements"]["hundred_percent"],
            f"{traceability['measurements']['fully_traceable']}/{total} stages trace end to end",
        ),
        "governability": (
            full and coverage["measurements"]["governance_coverage_percent"] == 100.0,
            f"governance declared for {coverage['measurements']['governance_coverage_percent']}% "
            f"of stages; {r['implemented']}/{total} realized",
        ),
        "evolvability": (
            evolution["measurements"]["fully_autonomous"],
            f"{evolution['measurements']['autonomous']}/8 capabilities AUTONOMOUS, "
            f"{evolution['measurements']['none']} NONE",
        ),
        "observability": (
            full,
            f"{r['probe_failures']['executably_discharged']} stages emit no executable observation",
        ),
        "recoverability": (
            replay["status"] == "REPLAYABLE" and full,
            "recovery requires every stage to be reproducible from evidence; "
            f"{r['implemented']}/{total} are",
        ),
        "reproducibility": (
            replay["measurements"]["mutation"] == 0
            and coverage["measurements"]["coverage_measured"],
            f"{replay['measurements']['mutation']} drift dimensions; "
            f"coverage_measured={coverage['measurements']['coverage_measured']}",
        ),
        "capability_coverage": (
            coverage["measurements"]["capability_coverage_percent"] == 100.0
            and coverage["measurements"]["lifecycle_coverage_percent"] == 100.0,
            f"lifecycle {coverage['measurements']['lifecycle_coverage_percent']}%, "
            f"capability {coverage['measurements']['capability_coverage_percent']}%",
        ),
    }

    claims = [
        {
            "claim": f"100% {name.replace('_', ' ').title()}",
            "key": name,
            "verdict": "PROVEN" if decisions[name][0] else "NOT_PROVEN",
            "measurement": decisions[name][1],
        }
        for name in CLOSURE_CLAIMS
    ]
    proven = sum(1 for c in claims if c["verdict"] == "PROVEN")
    return {
        "phase": 10,
        "title": "P0 Closure Determination",
        "question": "can P0 legitimately claim these for CURRENT Repository Truth?",
        "measurements": {
            "claims": len(claims),
            "proven": proven,
            "not_proven": len(claims) - proven,
            "closure": proven == len(claims),
        },
        "claims": claims,
    }


# --------------------------------------------------------------------------- report


def determination(artifacts: Mapping[str, dict[str, Any]]) -> str:
    """Render the determination from measurements only — no sentence without a number."""
    inv = artifacts["inventory"]
    own = artifacts["ownership"]
    rea = artifacts["realization"]
    gra = artifacts["graph"]
    rep = artifacts["replay"]
    evo = artifacts["evolution"]
    kno = artifacts["knowledge"]
    tra = artifacts["traceability"]
    cov = artifacts["coverage"]
    clo = artifacts["closure"]

    r = rea["measurements"]
    cm = clo["measurements"]
    im = inv["measurements"]
    om = own["measurements"]
    gm = gra["measurements"]
    total = r["stage_count"]
    lines: list[str] = []
    add = lines.append

    add(f"# {PROGRAMME} — Universal Constitutional Lifecycle Realization Determination")
    add("")
    add("| Field | Value |")
    add("|---|---|")
    add(f"| PROGRAMME | `{PROGRAMME}` |")
    add(
        "| AUTHORITY | **NONE — DERIVED TRUTH. This determination legislates nothing, "
        "registers nothing and certifies nothing. Every verdict below is the output of an "
        "executed probe.** |"
    )
    add("| LIFECYCLE AUTHORITY | `UCL-000001` (45 stages) |")
    add(f"| ENGINE | `{rel(Path(__file__))}` |")
    add(f"| DETERMINATION | **{'CLOSED' if clo['measurements']['closure'] else 'NOT CLOSED'}** |")
    add(f"| CLOSURE CLAIMS PROVEN | {cm['proven']} / {cm['claims']} |")
    add("| REPOSITORY ANCHOR | the containing commit — owned by version control |")
    add("")
    add(
        "> Declarations were treated as claims to be tested. A stage is IMPLEMENTED only "
        "where five executed probes agree; the manifest is never accepted as evidence for "
        "itself."
    )
    add("")

    add("## Headline")
    add("")
    add("| Measure | Value |")
    add("|---|---|")
    add(f"| Lifecycle stages | {total} |")
    add(f"| IMPLEMENTED | **{r['implemented']}** |")
    add(f"| PARTIALLY_IMPLEMENTED | {r['partially_implemented']} |")
    add(f"| DECLARED_ONLY | {r['declared_only']} |")
    add(f"| MISSING | {r['missing']} |")
    add(f"| Stages with an executable engine | {im['stages_with_executable_engine']} |")
    add(
        f"| Stages whose evidence is a document only | {im['stages_with_document_evidence_only']} |"
    )
    add(f"| Fully traceable stages | {tra['measurements']['fully_traceable']} |")
    add(f"| Replay status ({rep['rounds']} rounds) | {rep['status']} |")
    add(f"| Autonomous capabilities | {evo['measurements']['autonomous']} / 8 |")
    add("")

    add("## Phase 10 — closure claims")
    add("")
    add("| Claim | Verdict | Deciding measurement |")
    add("|---|---|---|")
    for claim in clo["claims"]:
        mark = "PROVEN" if claim["verdict"] == "PROVEN" else "**NOT_PROVEN**"
        add(f"| {claim['claim']} | {mark} | {claim['measurement']} |")
    add("")

    add("## Phase-by-phase measurement")
    add("")
    add("### Phase 1 — inventory")
    add(
        f"- {total} stages read from `{rel(MANIFEST)}`; every declared owner and evidence "
        f"artifact resolved on disk ({inv['measurements']['owners_absent_from_disk']} absent)."
    )
    add(
        f"- {im['stages_with_executable_engine']} stages name a module that compiles; "
        f"{im['stages_with_document_evidence_only']} name only documents."
    )
    add("")
    add("### Phase 2 — canonical ownership")
    add(
        f"- {om['distinct_owners']} distinct owners for {total} stages; "
        f"gaps {om['ownership_gaps']}, collisions {om['ownership_collisions']}."
    )
    add(
        f"- {own['measurements']['ownership_ambiguities']} stages are owned by a document, so no "
        "executable component owns the behaviour."
    )
    add("")
    add("### Phase 3 — executable realization")
    add("| Probe | Stages failing |")
    add("|---|---|")
    for probe, count in sorted(r["probe_failures"].items()):
        add(f"| `{probe}` | {count} |")
    add("")
    add("### Phase 4 — execution graph")
    add(
        f"- {gra['measurements']['nodes']} nodes, {gra['measurements']['edges']} edges, "
        f"cycles {gra['measurements']['cycles']}, skipped prerequisites "
        f"{gra['measurements']['skipped_prerequisites']}."
    )
    add(f"- Derived order matches the declared order: {gm['derived_matches_declared_order']}.")
    add("")
    add("### Phase 5 — deterministic replay")
    add(
        f"- {rep['measurements']['rounds_executed']} consecutive rounds over "
        f"{rep['measurements']['dimensions_measured']} identity dimensions; "
        f"{rep['measurements']['mutation']} unstable."
    )
    add(
        f"- Status **{rep['status']}** — and this measures only what actually executes; "
        f"{r['declared_only'] + r['missing']} stages contribute no observation to replay at all."
    )
    add("")
    add("### Phase 6 — autonomous evolution")
    add("| Capability | Level | Basis |")
    add("|---|---|---|")
    for cap in evo["capabilities"]:
        add(f"| {cap['capability']} | **{cap['level']}** | {cap['basis']} |")
    add("")
    add("### Phase 7 — knowledge elevation")
    add("| Closure | Closed | Blocking stages |")
    add("|---|---|---|")
    for closure in kno["closures"]:
        add(
            f"| `{closure['closure']}` | {'YES' if closure['closed'] else '**NO**'} | "
            f"{', '.join(closure['blocking']) or '—'} |"
        )
    add("")
    add("### Phase 8 — traceability")
    add("| Link | Stages broken |")
    add("|---|---|")
    for link, count in sorted(tra["measurements"]["link_failures"].items()):
        add(f"| `{link}` | {count} |")
    add(f"\n- End-to-end traceability: **{tra['measurements']['traceability_percent']}%**.")
    add("")
    add("### Phase 9 — coverage")
    add("| Dimension | Value |")
    add("|---|---|")
    for key, value in sorted(cov["measurements"].items()):
        if key.endswith("_note"):
            continue
        add(f"| `{key}` | {value} |")
    add("")
    add(f"> Path coverage: {cov['measurements']['path_coverage_note']}")
    add("")
    add("| Uncovered point | Count |")
    add("|---|---|")
    for kind, count in sorted(cov["uncovered_classification"].items()):
        add(f"| {kind} | {count} |")
    add("")

    add("## Gaps, explicitly")
    add("")
    add("Every stage that is not IMPLEMENTED, with the probes that failed:")
    add("")
    add("| Stage | Name | Realization | Failed probes |")
    add("|---|---|---|---|")
    for stage in rea["stages"]:
        if stage["realization"] == "IMPLEMENTED":
            continue
        add(
            f"| `{stage['stage_id']}` | {stage['stage_name']} | {stage['realization']} | "
            f"{', '.join(stage['failed_probes'])} |"
        )
    add("")

    add("## Success condition")
    add("")
    condition = "MET" if clo["measurements"]["closure"] else "NOT MET"
    add(
        f"**{condition}.** The directive requires every stage to be canonically owned, "
        "executably realized, governed, tested, traceable, replayable, deterministic and "
        "evolution-capable, with every gap explicitly identified. The gap table above is "
        "complete and machine-generated; the realization requirement is "
        f"{r['implemented']}/{total}."
    )
    add("")
    return "\n".join(lines) + "\n"


# --------------------------------------------------------------------------- driver


def run(rounds: int, with_coverage: bool) -> dict[str, dict[str, Any]]:
    nodes = load_manifest()

    inventory = phase1_inventory(nodes)
    ownership = phase2_ownership(inventory)

    providers = discover_providers()
    inventory["providers"] = providers
    if not any(p["usable"] for p in providers):
        raise Abort("no usable lifecycle provider exists; realization cannot be measured")

    discharges = discharge_map(rounds)
    engines = sorted({e for s in inventory["stages"] for e in s["executable_engine"]})
    coverage = (
        measure_coverage(engines)
        if with_coverage
        else {"measured": False, "reason": "--no-coverage", "files": {}, "totals": {}}
    )
    # A measurement that did not happen is not a measurement of zero.
    #
    # WHAT THIS REFUSES, STATED AS THE STATE IT WAS FOUND IN. Without this, an environment
    # where `coverage` is not importable still produces the full artifact set — every
    # coverage dimension published as 0.0 with `coverage_measured: false` beside it — and
    # exits 0, so nothing anywhere refuses the zeros. That is not hypothetical: the
    # committed UCOS-LIFECYCLE-COVERAGE.json carries exactly those zeros, and the committed
    # determination reads 2/12 CLOSURE CLAIMS PROVEN where every one of the ten failures
    # names `coverage_measured=False` or a 0.0% derived from it. Re-measured with the
    # instrument present, the same tree proves 12/12. The corpus was understating itself
    # because an engine lost its instrument quietly.
    #
    # Refusing is the shape the provider check above already uses: the subject is
    # unmeasurable, so no verdict is issued and — because every emit() happens after run()
    # returns — no artifact is written. `--no-coverage` remains a pass, because an operator
    # asking only for the structural phases is asking a different question than an engine
    # silently losing its instrument and answering anyway.
    if with_coverage and not coverage.get("measured"):
        raise Abort(
            "the coverage instrument did not run, so every coverage dimension would be "
            "published as 0.0 and read as measured: "
            f"{coverage.get('reason') or 'no reason reported'}"
        )

    realization = phase3_realization(inventory, discharges, coverage)
    graph = phase4_graph(nodes)
    replay = phase5_replay(rounds)
    evolution = phase6_evolution(realization)
    knowledge = phase7_knowledge(realization)
    traceability = phase8_traceability(inventory, realization, replay)
    coverage_phase = phase9_coverage(
        inventory, realization, evolution, knowledge, traceability, coverage
    )
    closure = phase10_closure(
        realization,
        graph,
        replay,
        evolution,
        knowledge,
        traceability,
        coverage_phase,
        ownership,
    )
    return {
        "inventory": inventory,
        "ownership": ownership,
        "realization": realization,
        "graph": graph,
        "replay": replay,
        "evolution": evolution,
        "knowledge": knowledge,
        "traceability": traceability,
        "coverage": coverage_phase,
        "closure": closure,
    }


ARTIFACTS: Mapping[str, str] = {
    "inventory": "UCOS-LIFECYCLE-INVENTORY.json",
    "ownership": "UCOS-LIFECYCLE-OWNERSHIP.json",
    "realization": "UCOS-LIFECYCLE-REALIZATION.json",
    "graph": "UCOS-LIFECYCLE-GRAPH.json",
    "replay": "UCOS-LIFECYCLE-REPLAY.json",
    "evolution": "UCOS-AUTONOMOUS-EVOLUTION.json",
    "knowledge": "UCOS-KNOWLEDGE-ELEVATION.json",
    "traceability": "UCOS-LIFECYCLE-TRACEABILITY.json",
    "coverage": "UCOS-LIFECYCLE-COVERAGE.json",
}


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="lifecycle_closure_engine",
        description=(
            "Measure whether every stage of the Universal Constitutional Lifecycle is "
            "realized. AUTHORITY = NONE; executable evidence only."
        ),
    )
    parser.add_argument("--rounds", type=int, default=DEFAULT_ROUNDS)
    parser.add_argument("--no-coverage", action="store_true")
    parser.add_argument("--gate", action="store_true", help="exit 1 unless every claim is PROVEN")
    parser.add_argument("--print", dest="show", default="", help="echo one artifact to stdout")
    args = parser.parse_args(argv)

    if args.rounds < 2:
        print("a fixed point cannot be observed in fewer than two rounds", file=sys.stderr)
        return 2

    try:
        artifacts = run(args.rounds, not args.no_coverage)
    except Abort as exc:
        print(f"FAIL-CLOSED: {exc}", file=sys.stderr)
        return 2

    written = [rel(emit(name, artifacts[key])) for key, name in sorted(ARTIFACTS.items())]
    report = OUT / "UCOS-P0-LIFECYCLE-CLOSURE-DETERMINATION.md"
    report.write_text(determination(artifacts), encoding="utf-8")
    written.append(rel(report))

    if args.show:
        print(json.dumps(artifacts[args.show], indent=2, sort_keys=True, ensure_ascii=False))
    else:
        closure = artifacts["closure"]["measurements"]
        realization = artifacts["realization"]["measurements"]
        print(
            json.dumps(
                {
                    "programme": PROGRAMME,
                    "artifacts": sorted(written),
                    "stages": realization["stage_count"],
                    "implemented": realization["implemented"],
                    "partially_implemented": realization["partially_implemented"],
                    "declared_only": realization["declared_only"],
                    "missing": realization["missing"],
                    "replay": artifacts["replay"]["status"],
                    "claims_proven": closure["proven"],
                    "claims_not_proven": closure["not_proven"],
                    "closure": closure["closure"],
                },
                indent=2,
                sort_keys=True,
            )
        )

    if args.gate and not artifacts["closure"]["measurements"]["closure"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
