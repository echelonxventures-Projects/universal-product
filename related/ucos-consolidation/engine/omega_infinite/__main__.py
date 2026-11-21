"""UCOS Ω∞ Phase 1 CLI — ``python -m engine.omega_infinite``.

READ-ONLY. THERE IS NO WRITING MODE, and the absence is deliberate: the Phase 1 directive forbids
issuing certification, resealing governance artifacts and modifying production governance
decisions, so this module has no ``--seal``, touches no ratchet and writes no evidence file. A
reader can verify that claim by observing that ``open`` is never called for writing anywhere in
this package.

EXIT CODES. 0 when all five criteria hold, 1 when any fails, 2 when the layer could not run at all.
The last is separate on purpose: "the abstraction refused" and "the abstraction is broken" are
different facts, and collapsing them would let an import error read as a governance failure.
"""

from __future__ import annotations

import argparse
import json
import sys

from engine.omega_infinite import evidence
from engine.omega_infinite.capability import CapabilityError
from engine.omega_infinite.knowledge_space import KnowledgeSpaceError
from engine.omega_infinite.provider import ProviderError


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m engine.omega_infinite",
        description=(
            "UCOS Ω∞ Phase 1 — Universal Discovery Abstraction Layer. Demonstrates that discovery "
            "operates through providers, artifacts, classifiers and knowledge spaces rather than "
            "through git, Python, filesystems and repository roots. Read-only."
        ),
    )
    parser.add_argument("--root", default=".", help="the knowledge space to resolve (default: .)")
    parser.add_argument("--json", action="store_true", help="emit the evidence document")
    parser.add_argument(
        "--providers",
        action="store_true",
        help="print the provider capability matrix and exit",
    )
    parser.add_argument(
        "--no-compare",
        action="store_true",
        help="skip the Ω-1 equivalence measurement (Deliverable 7)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    arguments = build_parser().parse_args(argv)
    try:
        built = evidence.build(arguments.root, compare=not arguments.no_compare)
    except (CapabilityError, KnowledgeSpaceError, ProviderError) as exc:
        print(f"UCOS Ω∞ Phase 1 could not run: {exc}", file=sys.stderr)
        return 2

    if arguments.providers:
        print(json.dumps(built.registry, indent=2, sort_keys=True, ensure_ascii=False))
        return 0 if built.passed else 1

    if arguments.json:
        print(json.dumps(built.as_document(), indent=2, sort_keys=True, ensure_ascii=False))
        return 0 if built.passed else 1

    print(evidence.render(built), end="")
    return 0 if built.passed else 1


if __name__ == "__main__":  # pragma: no cover - exercised via `python -m`
    raise SystemExit(main())
