"""UVI-000001 Part 10 — regenerating the measured cost table.

The cost table is a MEASUREMENT, and this module is how it is taken rather than
authored. It reads a ``pytest --durations=0`` transcript and derives, per test object:
its total measured duration, and — for an object over the declared split threshold —
the duration of each of its nodes together with the content hash the object carried when
it was measured.

Three properties the derivation depends on, each stated because each is a way the table
could quietly become wrong:

* **pytest hides durations below 0.005s.** Every collectible object IS measured in the
  run; the fast ones simply produce no line. Their true total is the residual between
  the suite's own wall clock and the sum of the visible durations, and they are recorded
  at that average rather than left unpriced. The distinction matters: unpriced means "no
  one has measured this", which is deliberately over-priced so an unknown cannot be
  packed into a full shard, while these were measured and found negligible.
* **A node id is only usable while it is current.** Each split entry records the
  object's ``content_hash`` as UCOS-UGA-001 published it, and the planner splits only
  while that hash still matches. A changed file falls back to whole-file placement.
* **Nothing here is a gate.** A stale table produces a slower plan, never a wrong one,
  which is why this runs on demand and not inside any verification mode.
"""

from __future__ import annotations

import argparse
import collections
import json
import os
import re
import sys

from engine.verification_intelligence.constitution import COST_MODEL, repo_root
from engine.verification_intelligence.model import VerificationIntelligenceError
from engine.verification_intelligence.registry import (
    DEFAULT_COST_SECONDS,
    build_test_registry,
    load_substrates,
)

SCHEMA = "ucos-verification-test-cost-model"

#: ``0.42s call     path/to/test_x.py::test_y[param]``
#:
#: The node part is matched non-greedily to end of line rather than as ``\S+``. A
#: parametrised id may contain a space — ``test_x[a b]`` — and a whitespace-free pattern
#: drops exactly those lines, which silently under-counts the objects most likely to be
#: parametrised and therefore most likely to be the ones worth splitting.
DURATION = re.compile(r"^([\d.]+)s\s+(?:call|setup|teardown)\s+(\S+\.py)::(.+?)\s*$", re.M)

#: ``11628 passed, 3 skipped in 1588.54s (0:26:28)``
WALL_CLOCK = re.compile(r"\bin ([\d.]+)s\b")

#: An object costing more than this is placed as its nodes rather than as one unit.
DEFAULT_SPLIT_THRESHOLD = 60.0


def derive(transcript: str, root: str | None = None, threshold: float | None = None) -> dict:
    """Derive the cost table from a durations transcript.

    Raises:
        VerificationIntelligenceError: the transcript carries no durations, so it is not
            the output of a ``--durations`` run and would silently produce an empty table.
    """
    base = root or repo_root()
    split_threshold = DEFAULT_SPLIT_THRESHOLD if threshold is None else threshold

    per_file: collections.Counter[str] = collections.Counter()
    per_node: dict[str, collections.Counter[str]] = collections.defaultdict(collections.Counter)
    for seconds, path, node in DURATION.findall(transcript):
        per_file[path] += float(seconds)
        per_node[path][f"{path}::{node}"] += float(seconds)
    if not per_file:
        raise VerificationIntelligenceError(
            "the transcript carries no durations; it is not the output of a --durations run"
        )

    substrates = load_substrates(base)
    registry = build_test_registry(substrates, base)
    collectible = set(registry.paths)

    visible = sum(value for path, value in per_file.items() if path in collectible)
    wall_clock = max((float(value) for value in WALL_CLOCK.findall(transcript)), default=visible)
    unpriced = sorted(collectible - set(per_file))
    residual = max(wall_clock - visible, 0.0)
    below_resolution = round(residual / len(unpriced), 4) if unpriced else 0.0

    costs = {path: round(value, 3) for path, value in per_file.items() if path in collectible}
    for path in unpriced:
        costs[path] = below_resolution

    split = {}
    for path, total in sorted(per_file.items()):
        if path not in collectible or total <= split_threshold:
            continue
        content_hash = substrates.objects[path].get("content_hash")
        if not content_hash:
            continue
        split[path] = {
            "content_hash": content_hash,
            "measured_seconds": round(total, 3),
            "nodes": {node: round(value, 3) for node, value in sorted(per_node[path].items())},
        }

    return {
        "artifact_id": "UVI-000001",
        "schema": SCHEMA,
        "version": "1.0",
        "authority": (
            "NONE — DERIVED TRUTH. A MEASUREMENT, not a fact about the repository. The shard "
            "planner reads it only to balance shards. A stale or absent entry makes a plan "
            "slower, never wrong: UVI-L-08 measures that the partition is exactly the "
            "selection whatever the prices say."
        ),
        "$measurement": (
            "pytest --durations=0 over the whole suite, then summed per object across setup, "
            f"call and teardown. Suite wall clock {round(wall_clock, 2)}s; visible durations "
            f"{round(visible, 1)}s over {len(per_file)} objects."
        ),
        "$below_resolution": (
            f"pytest hides any duration below 0.005s, so {len(unpriced)} of {len(collectible)} "
            "collectible objects produced no line. They WERE measured; their total is the "
            f"residual ({round(residual, 1)}s), so each is recorded at {below_resolution}s rather "
            f"than left unpriced. An unpriced object is one nobody has measured and is "
            f"over-priced at the {DEFAULT_COST_SECONDS}s default so it cannot be packed into a "
            "full shard; these are measured and negligible, and pricing them as unknown would "
            "put more fiction into the plan than the suite contains work."
        ),
        "$split": (
            "An object above the threshold is placed as its individual nodes, because one file "
            "is otherwise a floor on the whole run. Each entry records the content_hash the "
            "object carried when measured; the planner splits only while that hash still "
            "matches, and a changed file falls back to whole-file placement. Nothing here is a "
            "selection: every node of a split object runs, in exactly one shard."
        ),
        "$not_a_gate": (
            "Nothing fails because a measurement moved. Re-measure with `make verify-cost-model`."
        ),
        "units": "seconds",
        "below_resolution_seconds": below_resolution,
        "split_threshold_seconds": split_threshold,
        "costs": dict(sorted(costs.items())),
        "split": split,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m engine.verification_intelligence.cost_model",
        description="Derive the shard cost table from a pytest --durations transcript.",
    )
    parser.add_argument("--from", dest="source", required=True, help="the durations transcript")
    parser.add_argument("--out", default=None, help="where to write (default: the declared table)")
    parser.add_argument("--threshold", type=float, default=None, help="split threshold override")
    args = parser.parse_args(argv)

    try:
        with open(args.source, encoding="utf-8", errors="replace") as handle:
            transcript = handle.read()
        document = derive(transcript, threshold=args.threshold)
    except (OSError, VerificationIntelligenceError) as exc:
        print(f"UVI FAULT: {exc}", file=sys.stderr)
        return 2

    target = args.out or os.path.join(repo_root(), COST_MODEL)
    with open(target, "w", encoding="utf-8") as handle:
        json.dump(document, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
    print(
        f"cost model: {len(document['costs'])} object(s) priced, "
        f"{len(document['split'])} split above {document['split_threshold_seconds']}s"
    )
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI dispatch
    raise SystemExit(main())
