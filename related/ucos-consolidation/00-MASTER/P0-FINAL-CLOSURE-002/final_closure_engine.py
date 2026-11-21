#!/usr/bin/env python3
"""P0-FINAL-CLOSURE-002 — Phase 8 fixed-point and Phase 9 pristine-clone measurement.

AUTHORITY = NONE (DERIVED TRUTH). This engine legislates nothing, registers nothing,
certifies nothing and owns no capability. It runs the located regeneration chain, measures
what changed, and records the result. It cannot make a state converge and cannot make a
clone agree; where either fails it emits the failure.

Phase 8 — the fixed point
-------------------------
A *round* is one execution of the located regeneration chain. Zero drift means the round
changed nothing: the repository regenerated itself and produced byte-identical output.
Eight variance dimensions are measured separately rather than as one digest, because
"something moved" is not an actionable finding — *which* identity moved is.

The measurement is only valid with **no concurrent writer**. The prior attempt at this
phase was contaminated by exactly that and correctly refused to derive a claim from it, so
this engine takes a working-tree fingerprint before and after every round and fails closed
if anything it did not run has written into the tree.

Phase 9 — the pristine clones
-----------------------------
Each clone is an independent ``git clone`` of the canonical repository at HEAD, verified on
its own and then compared against the canonical identities. A clone that regenerates to a
different digest means the output depends on something outside version control, which is
the defect this phase exists to detect.

    python3 00-MASTER/P0-FINAL-CLOSURE-002/final_closure_engine.py
    python3 00-MASTER/P0-FINAL-CLOSURE-002/final_closure_engine.py --rounds 5 --clones 3
    python3 00-MASTER/P0-FINAL-CLOSURE-002/final_closure_engine.py --phase 8
    python3 00-MASTER/P0-FINAL-CLOSURE-002/final_closure_engine.py --gate

Exit semantics:
    0  both phases measured and every requirement met (or --gate not requested)
    1  --gate requested and a requirement was not met
    2  fail-closed abort — a concurrent writer, or a phase that could not be measured

No timestamp, no duration, no commit identity and no absolute path is emitted, so the
artifact set is byte-identical for an unchanged repository.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

PROGRAMME = "P0-FINAL-CLOSURE-002"
REPO = Path(__file__).resolve().parents[2]
OUT = REPO / "00-MASTER" / PROGRAMME

#: The located regeneration chain, in the order the repository declares it. Each entry is
#: run as a subprocess exactly as its Makefile target runs it, so this engine measures the
#: real chain rather than a reimplementation of it.
CHAIN: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("rib", ("00-MASTER/UCOS-RIB-001/rib_engine.py",)),
    ("aee", ("00-MASTER/UCOS-AEE-001/aee_engine.py", "--tier", "standard")),
)

#: The eight variance dimensions Phase 8 requires, each bound to the artifact whose digest
#: carries it. DATA — a ninth dimension is one appended entry.
DIMENSIONS: Mapping[str, str] = {
    "registry_variance": "00-MASTER/UCOS-RIB-001/rib.json",
    "authority_variance": "00-MASTER/UCCEP-000000/uccep.json",
    "certification_variance": "00-MASTER/UCOS-AEE-001/aee.json",
    "bookkeeping_variance": "00-MASTER/UCL-000001/ucl.json",
    "lineage_variance": "00-MASTER/ACEE-000001/acee.json",
    "dictionary_variance": "intelligence/UCOS-RIE-CAPABILITY-CATALOG.json",
    "ordering_variance": "00-MASTER/UCOS-RIB-001/10-IMPLEMENTATION-QUEUE.md",
    "replay_variance": "00-MASTER/P0-LIFECYCLE-CLOSURE-001/UCOS-LIFECYCLE-REPLAY.json",
}

#: What Phase 9 compares between a clone and the canonical repository.
CLONE_IDENTITIES: Mapping[str, str] = dict(DIMENSIONS)

#: The bootstrap a pristine clone requires before the chain can run at all.
#:
#: Several substrates the chain declares REQUIRED are generated artifacts the repository
#: deliberately does not track (``/knowledge/`` and the ``UAKOS-CLOSURE-002`` outputs are
#: excluded by ``.gitignore`` under a stated generated-artifact policy). A clone therefore
#: does not contain them, and the chain fail-closed aborts rather than measuring a
#: repository it cannot see — correctly.
#:
#: Phase 9 requires each clone to be *bootstrapped independently*, and this is that
#: bootstrap: the located generators that produce the untracked substrates, run in the
#: clone, from the clone's own tracked content. Nothing is copied in from the canonical
#: repository — copying would make the clone a mirror rather than an independent
#: reproduction, and would prove nothing about reproducibility.
#: UCOS-RC-002 — the canonical toolchain is part of the bootstrap, not a precondition.
#:
#: DETERMINATION (Option A). UCOS-AEE-001 resolves its actuator interpreter as
#: ``REPO/.ec1-venv/bin/python`` (aee_engine.py::interpreters, the ``$PY`` slot).
#: ``.ec1-venv/`` is gitignored, so it is absent from every pristine clone, and this list
#: did not create it. The measured consequence at HEAD 382b65e8: all seventeen required
#: actuators returned ``executed=false, verdict=UNAVAILABLE, reason="the declared
#: interpreter is not present in this environment"``, which drove blocking_violations from
#: 0 to 17, violated CONV-02, and turned AEE's determination from CONVERGED-PROVISIONAL
#: into NOT-CONVERGED. That is the whole of Phase-9 certification_variance.
#:
#: Option A rather than "declare it an external prerequisite", because the repository has
#: already made that choice everywhere else: ``verify.sh`` states that a brand-new terminal
#: runs it with no manual activation and no tribal knowledge because it *self-heals* the
#: canonical venv, and ``.ec1-venv/`` is excluded on exactly the same ground as
#: ``/knowledge/`` and ``/realization/`` — deterministically re-derivable output, not
#: authored truth. An environment the repository can rebuild from its own declarations is
#: inside the reproducibility contract by construction; this list was simply incomplete.
#:
#: The provisioner is INVOKED, never reimplemented. ``ucos_ensure_venv`` in
#: scripts/ucos-env.sh is the single canonical definition — it pins the Python series and
#: the toolchain versions — so a second copy here would be exactly the drift this closure
#: has spent its effort removing. It runs first: every later bootstrap step and the whole
#: chain depend on the interpreter existing.
BOOTSTRAP: tuple[tuple[str, tuple[str, ...]], ...] = (
    (
        "toolchain",
        (
            "-c",
            "import subprocess,sys;"
            "sys.exit(subprocess.run(['bash','-c',"
            "'set -e; source scripts/ucos-env.sh; ucos_ensure_venv']).returncode)",
        ),
    ),
    #: UCOS-RC-004 — the prerequisite set is INVOKED, not restated.
    #:
    #: This tuple used to name five producers directly: closure, phase2, phase3, rie, and
    #: `knowledge capabilities --write`. That was a second, independent copy of a list the
    #: repository already owns. scripts/generate-prerequisites.sh declares itself "THE one
    #: definition of 're-derive the generated inputs the gates read'" and runs SEVEN steps,
    #: including the knowledge store's full three-step pipeline — `init --force`, then
    #: `capabilities --write`, then `docs` — plus determinism evidence. That script's own
    #: header records why all three knowledge steps are required: running `init` alone
    #: leaves the store at 11 CKOs of 121, "so every consumer measured a store truncated to
    #: 9% of itself".
    #:
    #: This copy ran ONLY `capabilities --write` — step two of three, without step one. So
    #: every clone carried a knowledge store that had never been seeded. Measured at
    #: 3af66dcc: UCDA's decision DEC-UKDA-DEC-0001 reported
    #: `evidence_unresolved: ['knowledge/decisions.json', 'knowledge/canonical-knowledge.json']`,
    #: dropping dimensions_covered from 278 to 272 and mutating all nine UCDA outputs. The
    #: same mechanism moved URRC, UPF, MCOS, UMK and UAKOS-CLOSURE-008 — 23 paths — which
    #: cycle-2 RIB then observed as a dirty tree, closing its gate (source OPEN, clone
    #: CLOSED) and carrying AEE with it. That is the whole of registry_variance,
    #: ordering_variance and certification_variance.
    #:
    #: The defect was never in the producers. It was in maintaining two lists of them.
    (
        "prerequisites",
        (
            "-c",
            "import subprocess,sys;"
            "sys.exit(subprocess.run(['bash','scripts/generate-prerequisites.sh']).returncode)",
        ),
    ),
    ("rie", ("-m", "intelligence.rie", "build")),
)


class Abort(Exception):
    """A phase could not be measured, so no verdict may be asserted."""


def _git() -> str:
    """The absolute path to git, resolved once.

    Resolved rather than invoked by bare name: a partial executable path takes whatever
    ``PATH`` happens to offer, and a measurement engine that can be pointed at a different
    binary by an environment variable is not measuring the repository.
    """
    found = shutil.which("git")
    if not found:
        raise Abort("git is not available; repository state cannot be measured")
    return found


def rel(path: Path | str) -> str:
    try:
        return str(Path(path).resolve().relative_to(REPO))
    except (ValueError, OSError):
        return str(path)


def sha256(path: Path) -> str:
    """The content digest of one artifact, or ``"absent"`` when it does not exist."""
    if not path.is_file():
        return "absent"
    return hashlib.sha256(path.read_bytes()).hexdigest()


def identities(root: Path, mapping: Mapping[str, str] = DIMENSIONS) -> dict[str, str]:
    """The digest of every measured artifact under ``root``."""
    return {name: sha256(root / target) for name, target in sorted(mapping.items())}


def porcelain(root: Path) -> list[str]:
    """The working-tree state as git reports it, sorted."""
    run = subprocess.run(  # noqa: S603 - resolved absolute argv
        [_git(), "status", "--porcelain"],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    return sorted(line for line in run.stdout.splitlines() if line.strip())


def _integrity_snapshot(root: Path) -> dict[str, Any]:
    """Read-only repository integrity signal: HEAD, index presence, and file counts.

    Three git subprocess calls (``rev-parse``, ``ls-files``, and ``porcelain``'s own
    ``status``) plus one path check, all read-only. This function writes nothing, stages
    nothing, regenerates nothing, and never mutates git state.
    """
    head = subprocess.run(  # noqa: S603 - resolved absolute argv
        [_git(), "rev-parse", "HEAD"], cwd=root, capture_output=True, text=True, check=False
    ).stdout.strip()
    ls_files_count = len(
        subprocess.run(  # noqa: S603 - resolved absolute argv
            [_git(), "ls-files"], cwd=root, capture_output=True, text=True, check=False
        ).stdout.splitlines()
    )
    return {
        "head": head,
        "index_exists": (root / ".git" / "index").is_file(),
        "ls_files_count": ls_files_count,
        "porcelain_count": len(porcelain(root)),
    }


def _integrity_violations(before: Mapping[str, Any], after: Mapping[str, Any]) -> list[str]:
    """The three specific failure modes a checkpoint detects — nothing broader.

    Deliberately narrow: ordinary generated-file drift changes ``porcelain_count`` on every
    legitimate round and is never treated as corruption. Only a missing index, a collapsed
    ``ls-files`` count, or a moved HEAD ever are — the three signatures the forensic
    investigation (P0-FINAL-CLOSURE-002 index-corruption finding) actually observed.
    """
    violations: list[str] = []
    if not after["index_exists"]:
        violations.append("`.git/index` is missing")
    if before["ls_files_count"] > 0 and after["ls_files_count"] == 0:
        violations.append(f"git ls-files count dropped to zero (was {before['ls_files_count']})")
    if before["head"] != after["head"]:
        violations.append(f"HEAD changed: {before['head']!r} -> {after['head']!r}")
    return violations


def run_chain(
    root: Path,
    chain: Sequence[tuple[str, tuple[str, ...]]] = CHAIN,
    *,
    integrity_context: tuple[int, int] | None = None,
) -> tuple[dict[str, int], dict[str, str]]:
    """Execute a located chain once. Returns each actuator's exit code and its refusal.

    The refusal text is captured, not discarded. An actuator that fail-closed aborts is
    reporting *why* the repository could not be measured, and a phase that recorded only
    the exit code would turn a diagnosable cause into an anonymous number.

    ``integrity_context``, given as ``(phase, round_index)``, additionally checkpoints git
    integrity immediately after every actuator and fails closed the instant one is violated
    — HEAD moves, ``.git/index`` disappears, or ``git ls-files`` collapses to zero — instead
    of letting a corrupted mid-round state propagate silently into a later round's drift
    reading. Only Phase 8 passes this. Phase 9's chain runs inside a disposable clone, where
    this class of finding is exactly what Phase 9 already reports on its own terms, so its
    calls (here and via ``BOOTSTRAP``) leave this parameter at its default and are
    unaffected.
    """
    codes: dict[str, int] = {}
    refusals: dict[str, str] = {}
    for name, argv in chain:
        before = _integrity_snapshot(root) if integrity_context is not None else None
        run = subprocess.run(  # noqa: S603 - argv is literal; root is a repository path
            [sys.executable, *argv],
            cwd=root,
            capture_output=True,
            text=True,
            check=False,
        )
        codes[name] = run.returncode
        if run.returncode not in (0, 1):
            message = (run.stderr or run.stdout or "").strip().splitlines()
            refusals[name] = message[-1][:300] if message else "no diagnostic emitted"
        if integrity_context is not None:
            phase, round_index = integrity_context
            after = _integrity_snapshot(root)
            violations = _integrity_violations(before, after)
            if violations:
                raise Abort(
                    f"integrity checkpoint failed — phase {phase}, round {round_index}, "
                    f"executor {name!r}, at "
                    f"{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}: "
                    + "; ".join(violations)
                    + f" | before={before} | after={after}"
                )
    return codes, refusals


# --------------------------------------------------------------------------- phase 8


def phase8(rounds: int) -> dict[str, Any]:
    """Run the chain ``rounds`` times and measure drift across every dimension.

    Fails closed on a concurrent writer: if the tree changes between the end of one round
    and the start of the next, something other than this engine wrote, and drift measured
    under concurrent mutation is not attributable to the regeneration pipeline.
    """
    before_tree = porcelain(REPO)
    if before_tree:
        raise Abort(
            "the working tree is not clean; a fixed point measured over uncommitted state "
            f"would certify an arbitrary snapshot ({len(before_tree)} dirty entries)"
        )

    baseline = identities(REPO)
    observed: list[dict[str, Any]] = []
    previous_tree = before_tree

    for index in range(1, rounds + 1):
        if porcelain(REPO) != previous_tree:
            raise Abort(f"a concurrent writer mutated the tree before round {index}")
        codes, refusals = run_chain(REPO, integrity_context=(8, index))
        tree = porcelain(REPO)
        current = identities(REPO)
        drifted = sorted(k for k, v in current.items() if v != baseline[k])
        observed.append(
            {
                "round": index,
                "actuators": codes,
                "actuator_failures": sorted(k for k, v in codes.items() if v not in (0, 1)),
                "actuator_refusals": refusals,
                "mutation": len(tree),
                "mutated_paths": [line[3:] for line in tree][:20],
                "drift": len(drifted),
                "drifted_dimensions": drifted,
                "identities": current,
            }
        )
        previous_tree = tree

    zero_drift = [r for r in observed if r["drift"] == 0 and r["mutation"] == 0]
    consecutive = 0
    best = 0
    for record in observed:
        if record["drift"] == 0 and record["mutation"] == 0:
            consecutive += 1
            best = max(best, consecutive)
        else:
            consecutive = 0

    variance = {
        name: sum(1 for r in observed if name in r["drifted_dimensions"]) for name in DIMENSIONS
    }
    met = best >= rounds and not any(r["actuator_failures"] for r in observed)
    return {
        "phase": 8,
        "title": "Five-Round Fixed-Point Certification",
        "authority": "NONE — DERIVED TRUTH. Measurement only.",
        "requirement": f"{rounds} consecutive rounds, 0 drift, 0 mutation, 0 variance",
        "verdict": "FIXED POINT CERTIFIED" if met else "NOT PROVEN",
        "met": met,
        "rounds_executed": len(observed),
        "consecutive_zero_drift_rounds": best,
        "zero_drift_rounds": len(zero_drift),
        "concurrent_writer_detected": False,
        "chain": [{"actuator": n, "argv": list(a)} for n, a in CHAIN],
        "variance": variance,
        "dimensions": dict(sorted(DIMENSIONS.items())),
        "baseline_identities": baseline,
        "rounds": observed,
    }


# --------------------------------------------------------------------------- phase 9


def _clone(index: int, workdir: Path) -> Path:
    target = workdir / f"clone-{index}"
    run = subprocess.run(  # noqa: S603 - resolved absolute argv
        [_git(), "clone", "--quiet", "--local", "--no-hardlinks", str(REPO), str(target)],
        capture_output=True,
        text=True,
        check=False,
    )
    if run.returncode != 0 or not target.exists():
        raise Abort(f"clone {index} could not be created: {run.stderr[-300:]}")
    return target


def phase9(clones: int, cycles: int) -> dict[str, Any]:
    """Create ``clones`` pristine clones, run ``cycles`` verification cycles in each.

    Each cycle runs the same located chain the canonical repository runs. A clone is
    byte-identical when every measured identity matches the canonical one after every
    cycle — which is what proves the output depends on version-controlled content and
    nothing else.
    """
    canonical = identities(REPO, CLONE_IDENTITIES)
    results: list[dict[str, Any]] = []

    with tempfile.TemporaryDirectory(prefix="ucos-pristine-") as tmp:
        workdir = Path(tmp)
        for index in range(1, clones + 1):
            target = _clone(index, workdir)
            boot_codes, boot_refusals = run_chain(target, BOOTSTRAP)
            cycle_records: list[dict[str, Any]] = []
            for cycle in range(1, cycles + 1):
                codes, refusals = run_chain(target)
                observed = identities(target, CLONE_IDENTITIES)
                mismatched = sorted(k for k, v in observed.items() if v != canonical[k])
                cycle_records.append(
                    {
                        "cycle": cycle,
                        "actuators": codes,
                        "actuator_failures": sorted(k for k, v in codes.items() if v not in (0, 1)),
                        "mismatched_identities": mismatched,
                        "byte_identical": not mismatched,
                        "mutation": len(porcelain(target)),
                    }
                )
            identical = all(c["byte_identical"] for c in cycle_records)
            results.append(
                {
                    "clone": index,
                    "bootstrap": boot_codes,
                    "bootstrap_refusals": boot_refusals,
                    "cycles_executed": len(cycle_records),
                    "byte_identical_every_cycle": identical,
                    "cycles": cycle_records,
                }
            )
            shutil.rmtree(target, ignore_errors=True)

    met = bool(results) and all(c["byte_identical_every_cycle"] for c in results)
    return {
        "phase": 9,
        "title": "Pristine Clone Certification",
        "authority": "NONE — DERIVED TRUTH. Measurement only.",
        "requirement": f"{clones} independent clones, {cycles} verification cycles each",
        "verdict": "REPRODUCIBILITY CERTIFIED" if met else "NOT PROVEN",
        "met": met,
        "clones": len(results),
        "cycles_per_clone": cycles,
        "total_cycles": sum(c["cycles_executed"] for c in results),
        "identities_compared": sorted(CLONE_IDENTITIES),
        "canonical_identities": canonical,
        "results": results,
    }


# --------------------------------------------------------------------------- driver


def emit(name: str, payload: dict[str, Any]) -> str:
    OUT.mkdir(parents=True, exist_ok=True)
    payload = {"programme": PROGRAMME, **payload}
    payload["digest"] = hashlib.sha256(
        json.dumps(payload, sort_keys=True, ensure_ascii=False).encode()
    ).hexdigest()
    target = OUT / name
    target.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return rel(target)


def main(argv: Sequence[str] | None = None) -> int:
    # --- The declared re-entrancy guard (UCOS-RFP-001, CYC-RECURSE) -------------------
    #
    # THIS ENGINE MEASURES CONVERGENCE BY RE-RUNNING DECLARED PRODUCERS. `PRODUCERS` names
    # 00-MASTER/UCOS-RIB-001/rib_engine.py and the prerequisite script, and it executes both
    # as subprocesses in the working tree to observe whether their output varies. Inside the
    # fixed-point pipeline that is a recursive generator: STAGE-RIB already runs rib_engine,
    # and this engine runs it again through a path the pipeline does not declare.
    #
    # MEASURED, NOT HYPOTHETICAL. UCOS-RFP-001 reported this file as CYC-PRODUCER writing 16
    # tracked paths, every one of them inside 00-MASTER/UCOS-RIB-001/ -- a write zone
    # STAGE-RIB already owns. It counted in undeclared_producers and closed CLO-07/CLO-09.
    #
    # WHY THE GUARD RATHER THAN A STAGE DECLARATION. The bytes are not authored here; they
    # are authored by the declared producer this engine invokes to measure it. Declaring
    # this as a stage would put two stages in one write zone, trading CLO-09 for CLO-11 and
    # CLO-13. The aggregate excluding itself is what RFP-6's own remediation asks for.
    #
    # The guard name is printed because rfp_engine.py::honours_guard requires BOTH a
    # non-zero exit AND the declared guard name in the output before recording exclusion.
    if os.environ.get("UCOS_RFP_ACTIVE"):
        sys.stderr.write(
            "final_closure_engine: refusing to run — UCOS_RFP_ACTIVE is set.\n"
            "  This engine re-executes declared pipeline producers (rib_engine.py,\n"
            "  generate-prerequisites.sh) to measure their convergence. Running it inside\n"
            "  the fixed-point pipeline is a recursive generator (RFP-6 / CYC-RECURSE).\n"
        )
        return 3

    parser = argparse.ArgumentParser(
        prog="final_closure_engine",
        description=(
            "Phase 8 fixed-point and Phase 9 pristine-clone measurement. "
            "AUTHORITY = NONE; executable evidence only."
        ),
    )
    parser.add_argument("--rounds", type=int, default=5)
    parser.add_argument("--clones", type=int, default=3)
    parser.add_argument("--cycles", type=int, default=5)
    parser.add_argument("--phase", type=int, choices=(8, 9), default=0)
    parser.add_argument("--gate", action="store_true")
    args = parser.parse_args(argv)

    written: list[str] = []
    verdicts: dict[str, bool] = {}
    try:
        if args.phase in (0, 8):
            result = phase8(args.rounds)
            written.append(emit("UCOS-FIXED-POINT-CERTIFICATION.json", result))
            verdicts["phase8"] = result["met"]
        if args.phase in (0, 9):
            result = phase9(args.clones, args.cycles)
            written.append(emit("UCOS-PRISTINE-CLONE-CERTIFICATION.json", result))
            verdicts["phase9"] = result["met"]
    except Abort as exc:
        print(f"FAIL-CLOSED: {exc}", file=sys.stderr)
        return 2

    print(
        json.dumps(
            {"programme": PROGRAMME, "artifacts": written, "verdicts": verdicts},
            indent=2,
            sort_keys=True,
        )
    )
    if args.gate and not all(verdicts.values()):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
