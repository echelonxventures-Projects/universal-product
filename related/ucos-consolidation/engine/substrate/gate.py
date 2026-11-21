"""UCOS measured by the substrate it consumes.

Builds a substrate Graph from UCOS's own registers, runs the substrate's shipped
contradiction rules over it, and holds the result as a two-sided ratchet.

WHY THIS IS NOT A SECOND OMEGA GATE. Ω measures UCOS with UCOS's machinery, over the
population UCOS's machinery can see — which is Python. This measures UCOS with machinery
that has never heard of UCOS, over every artifact regardless of language or format. When the
two agree that is corroboration; when they differ the difference is the finding.

FAULT IS NOT FAILURE AND NEITHER IS A PASS. An absent substrate, an unreadable register or a
rule that raises all produce exit 2 and no verdict. A gate that reports OPEN because it could
not examine its subject is the defect every instrument here exists to refuse.
"""

from __future__ import annotations

import collections
import hashlib
import json
import os
import sys
from typing import Any

DECLARATION = os.path.join("00-MASTER", "UCOS-SUB-001", "sub-declaration.json")
EXIT_OPEN, EXIT_CLOSED, EXIT_FAULT = 0, 1, 2


def declaration_digest(declaration: dict[str, Any]) -> str:
    """The certification identity of UCOS-SUB-001's declaration.

    UEC-L-08 asks whether the package that OWNS a declaration mints a digest at all, and
    UEC-L-13 asks the harder question: whether a semantic edit MOVES it. Hashing the canonical
    form of the WHOLE document answers both, and the choice is deliberate. A digest over a
    projection — the ratchet alone, or a curated subset of fields — certifies two different
    declarations with one value, which is the defect UEC-L-13 exists to catch and which
    engine/construct was measured carrying: flipping a law's `blocking` flag left its
    declaration_digest byte-identical while the verdict depended on it.

    Canonical form is `json.dumps(sort_keys=True)` per UCKP-ART-13, so identical inputs
    produce identical bytes on any machine, in any interpreter, in any order the file was
    written. Commentary keys participate too: a `$why` that no longer describes what the
    instrument does is a semantic change, and a digest that ignored it would say otherwise.
    """
    canonical = json.dumps(declaration, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def main(argv: list[str] | None = None) -> int:
    root = os.getcwd()
    try:
        with open(os.path.join(root, DECLARATION), encoding="utf-8") as handle:
            declaration = json.load(handle)
        ceiling = int(declaration["ratchet"]["contradictions"])
    except (OSError, ValueError, KeyError) as exc:
        print(f"FAULT — the declaration is unusable: {exc}", file=sys.stderr)
        return EXIT_FAULT

    try:
        from uakp import rules
        from uakp.core.contradiction import detect
        from uakp.core.graph import Graph

        from engine.substrate import adapter
    except ImportError as exc:
        print(
            f"FAULT — the substrate is not importable: {exc}\n"
            f"  UCOS consumes {declaration['requires']}, which publishes no release yet and is\n"
            f"  installed from a local path. This is a FAULT and never a pass: a gate that\n"
            f"  reported OPEN because it could not load its subject would be a false green.",
            file=sys.stderr,
        )
        return EXIT_FAULT

    try:
        graph = Graph.of(artifacts=adapter.artifacts(root), authorities=adapter.authorities(root))
        findings = list(detect(graph, rules.SHIPPED))
    except Exception as exc:  # noqa: BLE001 — any failure here means nothing was measured
        print(
            f"FAULT — the measurement did not complete: {type(exc).__name__}: {exc}",
            file=sys.stderr,
        )
        return EXIT_FAULT

    measured = len(findings)
    by_rule = collections.Counter(finding.rule for finding in findings)
    print("UCOS-SUB-001 — UCOS measured by the substrate it consumes")
    print(f"  declaration     : {declaration_digest(declaration)}")
    print(f"  artifacts       : {len(graph.artifacts):,}")
    for name, authority in sorted(graph.authorities.items()):
        print(f"  {name:26} governs {len(authority.governs):,}")
    print(f"  contradictions  : {measured} (ceiling {ceiling})")
    for rule, count in by_rule.most_common():
        print(f"      {count:5}  {rule}")

    if measured > ceiling:
        print(
            f"\nCLOSED — {measured - ceiling} new contradiction(s). The class may not grow.",
            file=sys.stderr,
        )
        for finding in findings[:5]:
            print(f"    {finding.subject}: {finding.statement[:90]}", file=sys.stderr)
        return EXIT_CLOSED
    if measured < ceiling:
        print(
            f"\nCLOSED — {ceiling - measured} of slack. Debt was repaid without tightening the\n"
            f"  ratchet, leaving room a future regression can occupy in silence. Lower\n"
            f"  ratchet.contradictions to {measured}.",
            file=sys.stderr,
        )
        return EXIT_CLOSED
    print("\nOPEN — the ratchet holds.")
    return EXIT_OPEN


if __name__ == "__main__":
    raise SystemExit(main())
