"""UEC-000001 Part 5 — the gate. Fail-closed, read-only, three-valued.

    exit 0  OPEN    every blocking law was measured and holds
    exit 1  CLOSED  a blocking law was measured and REFUSED
    exit 2  FAULT   no verdict could be reached — the declaration is absent, unparseable or
                    incoherent, a discovery rule names an unknown strategy, or the tracked-path
                    boundary could not be established

The third code is load-bearing. "The enforcement plane is complete" and "the enforcement plane
could not be measured" are different facts, and a gate that collapsed them would let a broken
discoverer certify an empty repository — which is precisely the vacuity ``UEC-L-01`` refuses. A
FAULT is never "skip": the caller's fail-safe on 2 is to treat enforcement closure as UNPROVEN.

WRITES NOTHING. There is no ``--render`` and no ``--write``. A gate that emits no artifact cannot
drift from the artifact it emitted, and cannot be satisfied by regenerating its own expectation.
``--inventory`` prints the discovered surface to stdout for a human to paste into the governed
declaration; it does not edit the declaration, because an observation that could rewrite its own
expectation is not a measurement.
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any

from engine.enforcement_closure.contract import (
    REFUSED,
    inventory,
    measure,
)
from engine.enforcement_closure.discovery import repo_root
from engine.enforcement_closure.model import EnforcementError

EXIT_OPEN = 0
EXIT_CLOSED = 1
EXIT_FAULT = 2

REPAIR_COMMAND = "make uec"


def _render(report: dict[str, Any]) -> str:
    counts = report["counts"]
    lines = [
        "UNIVERSAL ENFORCEMENT CLOSURE — UEC-000001",
        "-" * 78,
        f"  declaration        : {report['declaration']} v{report['declaration_version']}",
        f"  declaration digest : {report['declaration_digest'][:16]}",
        f"  laws measured      : {counts['laws']}"
        f"   holds {counts['holds']}   refused {counts['refused']}",
        f"  tracked paths      : {counts['tracked']}",
        f"  enforcement plane  : {counts['artifacts']} artifacts"
        f"   ({counts['governed']} governed, {counts['withdrawn']} withdrawn)",
        f"  gate engines       : {counts['engines']}"
        f"   declarations {counts['declarations']}   test modules {counts['tests']}",
        "-" * 78,
        "  by kind:",
    ]
    for kind, total in report["by_kind"].items():
        lines.append(f"      {kind:20s} {total}")
    lines.append("-" * 78)
    lines.append("  ratchet (measured / declared ceiling — must be EQUAL):")
    declared = report["ratchet_declared"]
    for key, value in report["ratchet_measured"].items():
        ceiling = declared.get(key)
        mark = "  ok " if ceiling == value else "  XX "
        lines.append(f"    {mark} {key:46s} {value} / {ceiling}")
    lines.append("-" * 78)
    for row in report["laws"]:
        mark = (
            "  ok  " if row["verdict"] != REFUSED else ("  XX  " if row["blocking"] else "  !!  ")
        )
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
            "UNIVERSAL ENFORCEMENT CLOSURE — FAULT",
            "-" * 78,
            "  Expected: a readable, coherent UEC-000001 declaration, a git work tree, and "
            "twelve computable laws.",
            f"  Detected: {message}",
            "",
            "  No verdict was reached. This is NOT a pass and NOT a refusal.",
            "  Enforcement closure is UNPROVEN until this fault is repaired.",
            f"  Repair with: {REPAIR_COMMAND}",
            "-" * 78,
        ]
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m engine.enforcement_closure.gate",
        description=(
            "Universal Enforcement Closure — measure that every enforcement artifact is "
            "governed, invoked from two independent planes, covered by a test, and inside its "
            "own closure; and that no protection can disappear, be added ungoverned, or become "
            "vacuous without a fail-closed signal."
        ),
    )
    parser.add_argument(
        "--gate", action="store_true", help="refuse execution when a blocking law is refused"
    )
    parser.add_argument("--repository", default=None, help="repository root to measure")
    parser.add_argument("--declaration", default=None, help="path to uec-declaration.json")
    parser.add_argument(
        "--law", action="append", default=None, help="measure only this law id (repeatable)"
    )
    parser.add_argument(
        "--inventory",
        action="store_true",
        help="print the discovered enforcement surface as JSON, for adoption into the "
        "governed declaration by hand (writes nothing)",
    )
    parser.add_argument("--json", action="store_true", help="write the full report as JSON")
    parser.add_argument(
        "--quiet", action="store_true", help="suppress the summary on stderr when the gate is open"
    )
    args = parser.parse_args(argv)

    root = args.repository or repo_root()
    try:
        if args.inventory:
            print(
                json.dumps(inventory(args.declaration, repository=root), indent=1, sort_keys=True)
            )
            return EXIT_OPEN

        report = measure(args.declaration, repository=root, laws=args.law)
        closed = report["status"] == "CLOSED"
        if args.json:
            print(json.dumps(report, indent=2, sort_keys=True))
        if closed or not args.quiet:
            print(_render(report), file=sys.stderr)
        if args.gate and closed:
            return EXIT_CLOSED
        return EXIT_OPEN
    except EnforcementError as exc:
        print(_render_fault(str(exc)), file=sys.stderr)
        return EXIT_FAULT


if __name__ == "__main__":  # pragma: no cover - CLI dispatch
    raise SystemExit(main())
