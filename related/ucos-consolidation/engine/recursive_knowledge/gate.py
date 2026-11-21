"""URKE-000001 Part 15 — the gate. Fail-closed, read-only, three-valued.

    exit 0  OPEN    every blocking law was measured and holds
    exit 1  CLOSED  a blocking law was measured and REFUSED
    exit 2  FAULT   no verdict could be reached — the declaration is absent, unreadable or
                    incoherent, or a law could not be computed

The third code is not padding. "A law refused this repository" and "the law set could not be loaded"
are different facts, and a gate that collapsed them would let an unreadable declaration pass as
whichever answer was convenient. A FAULT never means skip: the caller's fail-safe on 2 is to treat
the capability as unverified.

The gate writes nothing unless ``--evidence`` is passed, and then only under the declared evidence
home, which is untracked. There is no ``--render`` and no ``--replay``, deliberately: a gate that
writes nothing has nothing to render and cannot drift, and a flag that is never read is a defect of
its own.
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any

from engine.recursive_knowledge.contract import REFUSED, load_contract, measure
from engine.recursive_knowledge.declaration import repo_root
from engine.recursive_knowledge.model import RecursiveKnowledgeError

EXIT_OPEN = 0
EXIT_CLOSED = 1
EXIT_FAULT = 2

REPAIR_COMMAND = "make urke"


def _render(report: dict[str, Any]) -> str:
    counts = report["counts"]
    metrics = report["metrics"]
    ledger = report["ledger"]
    found = report["discovery_report"]
    lines = [
        "UNIVERSAL RECURSIVE KNOWLEDGE FOUNDATION — URKE-000001",
        "-" * 78,
        f"  declaration          : {report['declaration']} v{report['declaration_version']}",
        f"  declaration digest   : {report['declaration_digest'][:16]}",
        f"  laws measured        : {counts['laws']}"
        f"   holds {counts['holds']}   refused {counts['refused']}",
        f"  primitives           : {metrics['primitive_count']}"
        f"   entity classes {metrics['entity_class_count']}   states {metrics['state_count']}",
        f"  data rows            : {metrics['data_row_count']}"
        f"   conditions {metrics['condition_count']}"
        f"   complexity ratio {metrics['complexity_ratio']}",
        f"  governed subjects    : {ledger['subjects']}"
        f"   journal {ledger['journal_entries']}   chain {ledger['chain_head'][:12]}",
        f"  discovery            : {found['findings']} findings from {found['sources']} sources",
        f"  ledger verification  : {report['ledger_verification']['status']}",
        "-" * 78,
    ]
    for row in report["laws"]:
        mark = "  ok  " if row["verdict"] != REFUSED else "  XX  "
        lines.append(f"{mark}{row['law_id']}  {row['check']}")
        for violation in row["violations"][:6]:
            lines.append(f"          - {violation}")
        remaining = len(row["violations"]) - 6
        if remaining > 0:
            lines.append(f"          ... +{remaining} more")
    lines.append("-" * 78)
    parity = report["parity"]
    absent = sorted(name for name, present in parity.items() if not present)
    lines.append(
        f"  parity: {len(parity) - len(absent)}/{len(parity)} layers present"
        + (f"   absent: {', '.join(absent)}" if absent else "")
    )
    lines.append(f"  standing: {report['standing']}")
    lines.append(f"  verdict: {report['status']}")
    return "\n".join(lines)


def _render_fault(message: str) -> str:
    return "\n".join(
        [
            "UNIVERSAL RECURSIVE KNOWLEDGE FOUNDATION — FAULT",
            "-" * 78,
            "  Expected: a readable, coherent URKE-000001 declaration and thirty-two computable "
            "laws.",
            f"  Detected: {message}",
            "",
            "  No verdict was reached. This is NOT a pass and NOT a refusal.",
            f"  Repair with: {REPAIR_COMMAND}",
            "-" * 78,
        ]
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m engine.recursive_knowledge.gate",
        description=(
            "Universal Recursive Knowledge Foundation — measure that every identified unknown, "
            "contradiction and gap is governed, that discovery converges, that evolution is "
            "traceable, and that no mechanism is closed against a future domain it has not met."
        ),
    )
    parser.add_argument(
        "--gate", action="store_true", help="refuse execution when a blocking law is refused"
    )
    parser.add_argument("--repository", default=None, help="repository root to measure")
    parser.add_argument("--declaration", default=None, help="path to urke-declaration.json")
    parser.add_argument(
        "--law", action="append", default=None, help="measure only this law id (repeatable)"
    )
    parser.add_argument(
        "--evidence", action="store_true", help="write evidence under the declared home"
    )
    parser.add_argument("--json", action="store_true", help="write the report to stdout as JSON")
    parser.add_argument(
        "--metrics", action="store_true", help="write only the complexity metrics as JSON"
    )
    parser.add_argument(
        "--quiet", action="store_true", help="suppress the summary on stderr when the gate is open"
    )
    args = parser.parse_args(argv)

    root = args.repository or repo_root()
    try:
        if args.metrics:
            declaration, _ = load_contract(args.declaration, repository=root)
            print(json.dumps(declaration.metrics(), indent=2, sort_keys=True))
            return EXIT_OPEN

        report = measure(args.declaration, repository=root, laws=args.law)
        closed = report["status"] == "CLOSED"

        if args.evidence:
            from engine.recursive_knowledge import evidence

            declaration, probe = load_contract(args.declaration, repository=root)
            written = evidence.write(
                declaration,
                report,
                probe.seeded(),
                repository=root,
                command="python -m engine.recursive_knowledge.gate",
            )
            if not args.quiet:
                for path in written:
                    print(f"URKE: wrote {path}", file=sys.stderr)

        if args.json:
            print(json.dumps(report, indent=2, sort_keys=True))
        if closed or not args.quiet:
            print(_render(report), file=sys.stderr)
        if args.gate and closed:
            return EXIT_CLOSED
        return EXIT_OPEN
    except RecursiveKnowledgeError as exc:
        print(_render_fault(str(exc)), file=sys.stderr)
        return EXIT_FAULT


if __name__ == "__main__":  # pragma: no cover - CLI dispatch
    raise SystemExit(main())
