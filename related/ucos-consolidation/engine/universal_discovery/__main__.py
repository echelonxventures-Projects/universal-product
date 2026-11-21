"""UCOS-OMEGA-001 CLI — ``python -m engine.universal_discovery``.

READ-ONLY BY DEFAULT. ``--seal`` is the only writing mode and it writes exactly two paths, both
inside ``00-MASTER/UCOS-OMEGA-001/``. Nothing here reads the wall clock, the commit identity or
the working-tree status, so two runs over one tree produce identical bytes.
"""

from __future__ import annotations

import argparse
import json
import sys

from engine.universal_discovery import discovery, gate
from engine.universal_discovery.model import OmegaError


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m engine.universal_discovery",
        description=(
            "Universal Discovery (UCOS-OMEGA-001): governance derived from `git ls-files '*.py'` "
            "rather than compared against a curated list."
        ),
    )
    parser.add_argument("--root", default=".", help="repository root (default: .)")
    parser.add_argument("--json", action="store_true", help="emit the surface document")
    parser.add_argument(
        "--seal",
        action="store_true",
        help="write the surface and advance the ratchet from this measurement",
    )
    parser.add_argument(
        "--scope",
        action="store_true",
        help="print the derived coverage scope and test roots, and nothing else",
    )
    arguments = parser.parse_args(argv)

    try:
        if arguments.scope:
            return _scope(arguments.root)
        verdict = gate.evaluate(arguments.root)
    except OmegaError as error:
        print(f"UCOS-OMEGA-001 FAULT: {error}", file=sys.stderr)
        return 2

    if arguments.json:
        print(json.dumps(verdict.omega.as_document(), indent=2, sort_keys=True, ensure_ascii=False))
    else:
        print(gate.render(verdict), end="")

    if arguments.seal:
        for path in gate.seal(arguments.root, verdict):
            print(f"sealed {path}")
    return verdict.exit_code


def _scope(root: str) -> int:
    """The derived scope, for a reader who wants to see what replaced the 78 ``--cov=`` flags."""
    from engine.universal_discovery import graph

    paths = discovery.tracked_python(root)
    import_graph = graph.ImportGraph(root, paths)
    test_roots = discovery.derive_test_roots(paths, graph.imported_by_path(import_graph, paths))
    exemptions, transient = discovery.read_declared(root)
    packages = discovery.derive_measurable_packages(paths, test_roots, exemptions=exemptions)
    print(
        json.dumps(
            {
                "tracked_python": len(paths),
                "roots": list(discovery.derive_roots(paths)),
                "test_roots": list(test_roots),
                "measurable_packages": list(packages),
                "declared_exemptions": exemptions,
                "declared_transient": transient,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":  # pragma: no cover - process entry
    raise SystemExit(main())
