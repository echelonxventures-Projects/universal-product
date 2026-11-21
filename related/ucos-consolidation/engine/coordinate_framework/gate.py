"""UCCFA-000001 — the fail-closed coordinate framework alignment gate.

    0  OPEN    every law holds
    1  CLOSED  a law was measured and refused
    2  FAULT   no verdict could be reached (the declaration is unusable)

The distinction between 1 and 2 is deliberate: "a coordinate is not the one the register
declares" and "the declaration could not be read" are different facts, and collapsing them
would let an unreadable declaration pass as whichever was more convenient.

OBSERVE MODE — READ ONLY. It loads the declaration, reads the declared surfaces, computes, and
writes nothing, including to gitignored paths. No clock, no network, no subprocess. No
``--render`` and no ``--replay``, because a gate that writes nothing has nothing to render and
cannot drift.

THE REPORT NAMES THE STATE IT IS A REPORT OF. Without the digest below, two different
declarations reaching two opposite verdicts would produce reports nothing could tell apart, and
nothing could later say WHICH declaration a recorded PASS was a pass of.
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any

from engine.coordinate_framework import (
    CoordinateAlignmentError,
    assess,
    load_contract,
    load_declaration,
    repo_root,
)
from engine.uckp.canonical import content_hash

EXIT_OPEN = 0
EXIT_CLOSED = 1
EXIT_FAULT = 2


def measure(declaration: str | None = None, repository: str | None = None) -> dict[str, Any]:
    """Measure every law and return the report.

    Raises:
        CoordinateAlignmentError: the declaration is unusable, which is a FAULT rather than a
            verdict.
    """
    contract = load_contract(declaration)
    repository = repository or repo_root()
    laws = [
        {"law_id": law_id, "title": title, "violations": list(violations), "holds": not violations}
        for law_id, title, violations in assess(contract, repository)
    ]
    return {
        "artifact_id": contract.artifact_id,
        "declaration_digest": content_hash(load_declaration(declaration)),
        "coordinates": len(contract.coordinates),
        "laws": laws,
        "holds": all(law["holds"] for law in laws),
    }


def _render(report: dict[str, Any]) -> str:
    lines = [
        f"{report['artifact_id']} — OBSERVE MODE — READ ONLY",
        "-" * 72,
        f"  declaration digest : {report['declaration_digest'][:16]}",
        f"  coordinates bound  : {report['coordinates']}",
        "-" * 72,
    ]
    for law in report["laws"]:
        lines.append(f"  {'ok ' if law['holds'] else 'XX '} {law['law_id']}  {law['title']}")
        lines.extend(f"          - {violation}" for violation in law["violations"])
    holds = sum(1 for law in report["laws"] if law["holds"])
    lines.append("-" * 72)
    verdict = "OPEN" if report["holds"] else "CLOSED"
    lines.append(f"  VERDICT: {verdict} ({holds}/{len(report['laws'])} laws hold)")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m engine.coordinate_framework.gate",
        description="UCCFA-000001 — coordinate framework alignment (observe only).",
    )
    parser.add_argument("--declaration", default=None, help="measure this declaration instead")
    parser.add_argument("--json", action="store_true", help="emit the report as JSON")
    args = parser.parse_args(argv)
    try:
        report = measure(args.declaration)
    except CoordinateAlignmentError as exc:
        print(f"UCCFA FAULT: {exc}", file=sys.stderr)
        return EXIT_FAULT
    print(json.dumps(report, indent=2, sort_keys=True) if args.json else _render(report))
    return EXIT_OPEN if report["holds"] else EXIT_CLOSED


if __name__ == "__main__":  # pragma: no cover - CLI dispatch
    raise SystemExit(main())
