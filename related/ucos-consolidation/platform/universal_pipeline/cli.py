"""UAPF-000001 — the declared entry point of the Universal Autonomous Pipeline Framework.

This module is where the filesystem lives. Every other module in this package is pure over
its inputs — that is the property that makes an identical declaration produce an identical
result in every environment — so *something* has to read bytes, and confining it to one small
module is what keeps the rest provably pure. The CLI reads a catalogue, hands the text to
:func:`platform.universal_pipeline.discovery.load_catalog`, and reports.

Why an entry point matters here
-------------------------------
The Repository Integration Blueprint measures a capability nothing names from a declared
entry point as a **dead engine** (``GAP-DEAD-ENGINE`` / ``VER-11``) and, because
``RCH-ENTRYPOINT`` is one of its reachability dimensions, simultaneously as an **orphan**
(``VER-09``). A framework reachable only from a test would be measured exactly that way, and
so would the catalogue it reads. This module is the discharge: it names UAPF from the same
``[project.scripts]`` / ``Makefile`` convention every other programme in this repository
already uses, and it makes the packaged catalogue a file something actually reads.

Authority
---------
``AUTHORITY = NONE (DERIVED TRUTH)``. Read-only: it opens the catalogue and writes nothing
anywhere — not the certified corpus (DP-03), not the registries, not a cache. Every number it
prints is derived at the moment it prints it.

Exit codes follow the repository convention: ``0`` gate OPEN, ``1`` gate CLOSED, ``2``
fail-closed abort (a malformed catalogue, an unreadable path).
"""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from pathlib import Path
from platform.universal_pipeline.discovery import DiscoveryReport
from platform.universal_pipeline.errors import UniversalPipelineError
from platform.universal_pipeline.service import UniversalPipelinePlatform
from typing import Any

#: The packaged canonical catalogue — the declaration of the Evolution and Build pipelines.
#: Resolved relative to this module so it is found whether the package is run from the
#: repository or from an installed wheel.
CANONICAL_CATALOG = Path(__file__).resolve().parent / "catalog" / "uapf-pipelines.json"

#: Exit code when a gate is open (or a report-only invocation succeeded).
EXIT_OPEN = 0

#: Exit code when a gate is closed — a real, measured finding.
EXIT_CLOSED = 1

#: Exit code when the invocation could not reach a verdict at all (fail-closed abort).
EXIT_ABORT = 2


def read_catalog(path: Path) -> str:
    """Read a catalogue document from ``path``.

    Raises:
        PipelineDiscoveryError-compatible failure is *not* raised here: this function only
            reads bytes. An unreadable path raises :class:`OSError`, which :func:`main`
            converts into a fail-closed abort so the caller sees a stated reason rather than
            a traceback.
    """
    return path.read_text(encoding="utf-8")


def load_platform(path: Path) -> tuple[UniversalPipelinePlatform, DiscoveryReport]:
    """Build a platform and discover ``path`` into it; return both."""
    platform_instance = UniversalPipelinePlatform()
    report = platform_instance.discover(read_catalog(path))
    return platform_instance, report


def gate(platform_instance: UniversalPipelinePlatform, report: DiscoveryReport) -> list[str]:
    """Evaluate every fail-closed check the catalogue can be held to; return the failures.

    Empty means the gate is open. Five independent checks, each decided by the engine that
    owns it rather than re-derived here:

        1. discovery refused nothing;
        2. the catalogue declared at least one pipeline (an empty catalogue is not a pass);
        3. every registered plan still follows from its declaration, recorded history is
           intact, the relationship graph is closed and acyclic, and the queue invariants
           hold (:meth:`UniversalPipelinePlatform.require_intact`);
        4. every required capability is provided by something (closure honesty);
        5. every stage of every registered pipeline names a resolvable handler — a stage with
           no realizer is a dead declaration.
    """
    failures: list[str] = []
    for reference, reason in report.refused:
        failures.append(f"declaration refused: {reference} — {reason}")
    if not platform_instance.registry.pipeline_ids:
        failures.append("catalogue declared no pipelines")
    try:
        platform_instance.require_intact()
    except UniversalPipelineError as exc:
        failures.append(f"integrity: {exc.code}: {exc.message}")
    for pipeline_id, capability_id in platform_instance.registry.unsatisfied_capabilities():
        failures.append(f"unsatisfied capability: {pipeline_id} requires {capability_id}")
    from platform.universal_pipeline.handlers import stage_handler_names

    known = set(stage_handler_names())
    for entry in platform_instance.registry.entries:
        for stage in entry.definition.stages:
            if stage.handler not in known:
                failures.append(
                    f"unresolvable handler: {entry.pipeline_id}.{stage.stage_id} "
                    f"names {stage.handler}"
                )
    return failures


def catalog_summary(
    platform_instance: UniversalPipelinePlatform, report: DiscoveryReport
) -> dict[str, Any]:
    """The derived summary of a discovered catalogue (evidence, not decoration)."""
    return {
        "catalog_id": report.catalog_id,
        "discovery": report.to_dict(),
        "pipelines": [
            {
                "pipeline_id": entry.pipeline_id,
                "pipeline_type": entry.pipeline_type,
                "version": entry.version,
                "stages": len(entry.definition.stages),
                "waves": entry.plan.wave_count,
                "max_parallelism": entry.plan.max_parallelism,
                "strategy": entry.plan.strategy,
                "plan_fingerprint": entry.plan.fingerprint(),
            }
            for entry in platform_instance.registry.entries
        ],
        "capability_graph": platform_instance.registry.capability_graph(),
        "pipeline_dependencies": {
            pid: list(providers)
            for pid, providers in platform_instance.registry.pipeline_dependencies().items()
        },
        "registry_fingerprint": platform_instance.registry.fingerprint(),
    }


def check_determinism(path: Path) -> tuple[bool, str, str]:
    """Discover ``path`` twice into fresh platforms; compare the registry fingerprints.

    The *registry* fingerprint is the right comparison. It covers every declaration, every
    derived plan and both derived graphs, and it is independent of process-wide vocabulary
    state — so a second discovery in the same process is a fair comparison. Comparing whole
    platform fingerprints would not be: the recorded event history legitimately differs,
    because the second pass admits no *new* pipeline types and says so.
    """
    document = read_catalog(path)
    first = UniversalPipelinePlatform()
    first.discover(document)
    second = UniversalPipelinePlatform()
    second.discover(document)
    left, right = first.registry.fingerprint(), second.registry.fingerprint()
    return left == right, left, right


def build_parser() -> argparse.ArgumentParser:
    """The argument surface. One catalogue, four mutually compatible reports."""
    parser = argparse.ArgumentParser(
        prog="ucos-uapf",
        description=(
            "UAPF-000001 Universal Autonomous Pipeline Framework — discover the declared "
            "pipeline catalogue, derive every plan, and report or gate. "
            "AUTHORITY = NONE (DERIVED TRUTH); writes nothing."
        ),
    )
    parser.add_argument(
        "--catalog",
        type=Path,
        default=CANONICAL_CATALOG,
        help="catalogue to discover (default: the packaged canonical catalogue)",
    )
    parser.add_argument(
        "--gate",
        action="store_true",
        help="fail-closed gate: exit 1 on any refusal, integrity failure, "
        "unsatisfied capability or unresolvable handler",
    )
    parser.add_argument(
        "--state",
        action="store_true",
        help="print every synchronized dimension as JSON (repository synchronization view)",
    )
    parser.add_argument(
        "--check-determinism",
        action="store_true",
        help="discover the catalogue twice and prove the derived registry is identical",
    )
    parser.add_argument(
        "--taxonomy",
        action="store_true",
        help="print the open vocabularies: pipeline types, event categories, handlers, "
        "object kinds and readiness predicates",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the CLI. Returns the process exit code rather than calling ``sys.exit``.

    Returning the code keeps the whole entry point testable in-process: a test asserts on the
    integer instead of catching ``SystemExit``.
    """
    args = build_parser().parse_args(argv)
    try:
        if args.check_determinism:
            identical, left, right = check_determinism(args.catalog)
            print(
                json.dumps(
                    {
                        "check": "determinism",
                        "identical": identical,
                        "first": left,
                        "second": right,
                    },
                    indent=2,
                )
            )
            return EXIT_OPEN if identical else EXIT_CLOSED
        platform_instance, report = load_platform(args.catalog)
    except OSError as exc:
        print(f"UAPF-000001: ABORT — catalogue could not be read: {exc}", file=sys.stderr)
        return EXIT_ABORT
    except UniversalPipelineError as exc:
        print(f"UAPF-000001: ABORT — {exc}", file=sys.stderr)
        return EXIT_ABORT

    if args.taxonomy:
        print(json.dumps(platform_instance.state()["taxonomy"], indent=2))
        return EXIT_OPEN
    if args.state:
        print(json.dumps(platform_instance.state(), indent=2, sort_keys=True))
        return EXIT_OPEN

    summary = catalog_summary(platform_instance, report)
    if not args.gate:
        print(json.dumps(summary, indent=2))
        return EXIT_OPEN

    failures = gate(platform_instance, report)
    verdict = "OPEN" if not failures else "CLOSED"
    print(
        f"UAPF-000001: {verdict} | catalog={summary['catalog_id']} "
        f"| pipelines={len(summary['pipelines'])} "
        f"| stages={sum(p['stages'] for p in summary['pipelines'])} "
        f"| findings={len(failures)} "
        f"| registry={summary['registry_fingerprint'][:16]}"
    )
    for failure in failures:
        print(f"  FINDING: {failure}", file=sys.stderr)
    return EXIT_OPEN if not failures else EXIT_CLOSED


if __name__ == "__main__":  # pragma: no cover — exercised through main().
    raise SystemExit(main())
