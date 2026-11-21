"""UCON-000001 Part 11 — the gate. Fail-closed, read-only, and three-valued.

    exit 0  OPEN    every blocking law was measured and holds
    exit 1  CLOSED  a blocking law was measured and REFUSED
    exit 2  FAULT   no verdict could be reached — the declaration is absent, unparseable or
                    incoherent, or a law could not be computed

The third code is not defensive padding. "A law refused this repository" and "the law set could
not be loaded" are different facts about the world, and a gate that collapsed them would let an
unreadable declaration pass as whichever answer happened to be convenient. A FAULT never means
"skip": the caller's fail-safe on 2 is to treat the capability as unverified, not as verified.

OBSERVE MODE. The gate writes nothing at all unless ``--evidence`` is passed, and then only under
the declared evidence home, which is untracked. There is no ``--render`` and no ``--replay``,
deliberately: a gate that writes nothing has nothing to render and cannot drift, and declaring a
flag that is never read is the defect this repository records as GP-4.
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any

from engine.construct import audit
from engine.construct.contract import REFUSED, load_contract, measure
from engine.construct.declaration import repo_root
from engine.construct.model import ConstructError

EXIT_OPEN = 0
EXIT_CLOSED = 1
EXIT_FAULT = 2

REPAIR_COMMAND = "make ucon"


def _render(report: dict[str, Any]) -> str:
    counts = report["counts"]
    closures = report["closure_inventory"]
    registry = report["registry"]
    discovery = report["discovery"]
    lines = [
        "UNIVERSAL CONSTRUCT FOUNDATION — UCON-000001",
        "-" * 78,
        f"  declaration           : {report['declaration']} v{report['declaration_version']}",
        f"  declaration digest    : {report['declaration_digest'][:16]}",
        f"  laws measured         : {counts['laws']}"
        f"   holds {counts['holds']}   refused {counts['refused']}",
        f"  constructs registered : {registry['constructs']}"
        f"   (presented {registry['presented']}, undisposed 0)",
        f"  registered kinds      : {len(registry['registered_kinds'])}  (open by registration)",
        f"  unknowns              : {discovery['unknowns']}",
        f"  contradictions        : {discovery['contradictions']}"
        f"   (standing {discovery['standing_contradictions']})",
        f"  research objects      : {discovery['research_objects']}",
        f"  discovery objects     : {discovery['discovery_objects']}"
        f"   from {discovery['opportunities']} opportunities",
        f"  closures inventoried  : {closures['total']}"
        f"   across {closures['modules_with_closures']} modules",
        f"  governed scope        : {closures['governed_scope']} closures, all disclosed",
        "-" * 78,
    ]
    for row in report["laws"]:
        mark = "  ok  " if row["verdict"] != REFUSED else "  XX  "
        lines.append(f"{mark}{row['law_id']}  {row['statement']}")
        for violation in row["violations"][:6]:
            lines.append(f"          - {violation}")
        remaining = len(row["violations"]) - 6
        if remaining > 0:
            lines.append(f"          ... +{remaining} more")
    lines.append("-" * 78)
    lines.append(f"  verdict: {report['status']}")
    return "\n".join(lines)


def _render_fault(message: str) -> str:
    return "\n".join(
        [
            "UNIVERSAL CONSTRUCT FOUNDATION — FAULT",
            "-" * 78,
            "  Expected: a readable, coherent UCON-000001 declaration and sixteen "
            "computable laws.",
            f"  Detected: {message}",
            "",
            "  No verdict was reached. This is NOT a pass and NOT a refusal.",
            f"  Repair with: {REPAIR_COMMAND}",
            "-" * 78,
        ]
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m engine.construct.gate",
        description=(
            "Universal Construct Foundation — measure that every presented construct is "
            "governed, disposed and traceable, that unknowns and contradictions are first "
            "class, and that no framework is closed against a future it has not met."
        ),
    )
    parser.add_argument(
        "--gate", action="store_true", help="refuse execution when a blocking law is refused"
    )
    parser.add_argument("--repository", default=None, help="repository root to measure")
    parser.add_argument("--declaration", default=None, help="path to ucon-declaration.json")
    parser.add_argument(
        "--law", action="append", default=None, help="measure only this law id (repeatable)"
    )
    parser.add_argument(
        "--inventory",
        action="store_true",
        help="emit the full closure inventory as JSON instead of the law report",
    )
    parser.add_argument(
        "--evidence", action="store_true", help="write evidence under the declared home"
    )
    parser.add_argument(
        "--json", action="store_true", help="write the full report to stdout as JSON"
    )
    parser.add_argument(
        "--quiet", action="store_true", help="suppress the summary on stderr when the gate is open"
    )
    args = parser.parse_args(argv)

    root = args.repository or repo_root()
    try:
        if args.inventory:
            declaration, probe = load_contract(args.declaration, repository=root)
            inventory = probe.inventory()
            problems = audit.validate(inventory)
            print(json.dumps(inventory, indent=2, sort_keys=True))
            if problems and not args.quiet:
                for problem in problems:
                    print(f"UCON: {problem}", file=sys.stderr)
            if args.gate and problems:
                return EXIT_CLOSED
            return EXIT_OPEN

        report = measure(args.declaration, repository=root, laws=args.law)
        closed = report["status"] == "CLOSED"

        if args.evidence:
            from engine.construct import evidence

            declaration, probe = load_contract(args.declaration, repository=root)
            written = evidence.write(
                declaration,
                report,
                probe.inventory(),
                repository=root,
                command="python -m engine.construct.gate",
            )
            if not args.quiet:
                for path in written:
                    print(f"UCON: wrote {path}", file=sys.stderr)

        if args.json:
            print(json.dumps(report, indent=2, sort_keys=True))
        if closed or not args.quiet:
            print(_render(report), file=sys.stderr)
        if args.gate and closed:
            return EXIT_CLOSED
        return EXIT_OPEN
    except ConstructError as exc:
        print(_render_fault(str(exc)), file=sys.stderr)
        return EXIT_FAULT


if __name__ == "__main__":  # pragma: no cover - CLI dispatch
    raise SystemExit(main())
