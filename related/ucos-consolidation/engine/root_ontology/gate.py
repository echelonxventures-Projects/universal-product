"""UCPA-000001 Part 03 — the fail-closed constitutional primitive alignment gate.

Exit codes follow the repository convention so a caller can distinguish the three
outcomes that matter:

    0  OPEN    every law holds
    1  CLOSED  a law was measured and refused
    2  FAULT   no verdict could be reached (the declaration is unusable)

The distinction between 1 and 2 is deliberate. "A primitive is not the one the register
declares" and "the declaration could not be read" are different facts, and collapsing
them would let an unreadable declaration pass as whichever was more convenient.

OBSERVE MODE — READ ONLY. It loads the declaration, reads declared files, imports the
facet model in-process, computes, and writes nothing — including to gitignored paths. No
clock, no network, no subprocess. No ``--render`` and no ``--replay`` are declared,
because a gate that writes nothing has nothing to render and cannot drift; declaring an
unread flag is the ``GP-4`` defect recorded in ``GATE-PURITY-DETERMINATION.md``.
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any

from engine.root_ontology.contract import assess, load_contract, repo_root
from engine.root_ontology.model import AlignmentError
from engine.uckp.canonical import content_hash

EXIT_OPEN = 0
EXIT_CLOSED = 1
EXIT_FAULT = 2


def measure(declaration: str | None = None, repository: str | None = None) -> dict[str, Any]:
    """Measure every law and return the report.

    Raises:
        AlignmentError: the declaration is unusable, which is a FAULT rather than a
            verdict.
    """
    contract = load_contract(declaration)
    repository = repository or repo_root()
    assessments = assess(contract, repository)

    laws = [
        {
            "law_id": law_id,
            "title": title,
            "violations": list(violations),
            "holds": not violations,
        }
        for law_id, title, violations in assessments
    ]
    return {
        "artifact_id": contract.artifact_id,
        # THE REPORT NOW NAMES THE STATE IT IS A REPORT OF. Without this the eight laws below
        # returned a verdict attributable to nothing: two different declarations reaching two
        # opposite verdicts produced reports that could not be told apart, and a recorded PASS
        # could never say WHICH declaration it was a pass of. UEC-L-13 measures by mutation that
        # this digest MOVES whenever the declaration's meaning does.
        "declaration_digest": content_hash(contract.digest_payload()),
        "declaration_version": contract.version,
        "canonical_owner": contract.source.canonical_owner,
        "primitives": len(contract.primitives),
        "facets_reduced": len(contract.reductions),
        "projections": len(contract.projections),
        "laws": laws,
        "laws_measured": len(laws),
        "laws_holding": sum(1 for law in laws if law["holds"]),
        "open": all(law["holds"] for law in laws),
    }


def _render(report: dict[str, Any]) -> str:
    """Return the human-readable summary written to stderr."""
    lines = [
        f"{report['artifact_id']} — constitutional primitive alignment",
        f"  canonical owner : {report['canonical_owner']}",
        f"  primitives bound: {report['primitives']}",
        f"  facets reduced  : {report['facets_reduced']}",
        f"  projections     : {report['projections']}",
        f"  laws            : {report['laws_holding']}/{report['laws_measured']} hold",
    ]
    for law in report["laws"]:
        mark = "OK  " if law["holds"] else "FAIL"
        lines.append(f"  {mark} {law['law_id']}  {law['title']}")
        for violation in law["violations"]:
            lines.append(f"         - {violation}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    """CLI entry point. Returns OPEN, CLOSED or FAULT."""
    parser = argparse.ArgumentParser(
        prog="python -m engine.root_ontology.gate",
        description=(
            "Measure UCPA-000001: the constitutional primitives against the register "
            "that owns them, and the facet model against the primitives."
        ),
    )
    parser.add_argument("--declaration", default=None, help="path to ucpa-declaration.json")
    parser.add_argument("--repository", default=None, help="repository root to measure")
    parser.add_argument("--json", action="store_true", help="write the report to stdout as JSON")
    parser.add_argument("--quiet", action="store_true", help="suppress the summary on stderr")
    args = parser.parse_args(argv)

    try:
        report = measure(args.declaration, args.repository)
    except AlignmentError as error:
        print(f"UCPA gate FAULT: {error}", file=sys.stderr)
        return EXIT_FAULT

    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    if not args.quiet or not report["open"]:
        print(_render(report), file=sys.stderr)
    return EXIT_OPEN if report["open"] else EXIT_CLOSED


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())


__all__ = ["EXIT_CLOSED", "EXIT_FAULT", "EXIT_OPEN", "main", "measure"]
