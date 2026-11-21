"""``ucos-mcos`` — the command surface of the Universal Meta-Civilization layer.

Every subcommand emits canonical JSON on stdout, so output is diffable and machine-readable:

    ucos-mcos describe             the platform's self-description
    ucos-mcos prove                run the constitutional gates + architectural proof
    ucos-mcos certify              the platform's self-certification
    ucos-mcos evidence <dir>       write the full evidence set to a directory

``prove`` (and the top-level ``--gate`` alias) exits 0 when compliant and 1 when a gate fails,
so it is usable directly as a gate without a wrapper.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

from engine.civilization.compliance import (
    architectural_proof,
    constitutional_report,
    quality_gates,
)
from engine.civilization.mcos import MetaCivilizationPlatform
from engine.kernel.identity import canonical_json


def _emit(payload: Any) -> None:
    """Print a payload as canonical JSON."""
    print(canonical_json(payload))


def cmd_describe() -> int:
    """Emit the platform's deterministic self-description."""
    _emit(MetaCivilizationPlatform().describe())
    return 0


def cmd_prove() -> int:
    """Run the constitutional gates and the architectural proof; exit non-zero on failure."""
    report = constitutional_report()
    _emit(report)
    return 0 if report["passed"] else 1


def cmd_certify() -> int:
    """Emit the platform's deterministic self-certification."""
    _emit(MetaCivilizationPlatform().certify())
    return 0


def cmd_evidence(directory: str) -> int:
    """Write the full evidence set as canonical JSON files into ``directory``."""
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    platform = MetaCivilizationPlatform()
    artifacts = {
        "mcos-constitutional-compliance.json": constitutional_report(),
        "mcos-quality-gates.json": quality_gates(),
        "mcos-architectural-proof.json": architectural_proof(),
        "mcos-self-certification.json": platform.certify(),
        "mcos-platform-description.json": platform.describe(),
        "mcos-kernel-snapshot.json": platform.kernel.registry.snapshot(),
    }
    for name, payload in artifacts.items():
        (target / name).write_text(canonical_json(payload) + "\n", encoding="utf-8")
    _emit({"written": sorted(artifacts), "directory": str(target)})
    return 0


def build_parser() -> argparse.ArgumentParser:
    """The ``ucos-mcos`` argument parser."""
    parser = argparse.ArgumentParser(prog="ucos-mcos", description=__doc__)
    parser.add_argument("--gate", action="store_true", help="alias for the prove subcommand")
    sub = parser.add_subparsers(dest="command")
    sub.add_parser("describe", help="emit the platform self-description")
    sub.add_parser("prove", help="run the constitutional gates + architectural proof")
    sub.add_parser("certify", help="emit the platform self-certification")
    evidence = sub.add_parser("evidence", help="write the evidence set to a directory")
    evidence.add_argument("directory", help="destination directory")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Entry point for the ``ucos-mcos`` console script."""
    args = build_parser().parse_args(argv)
    if args.command == "describe":
        return cmd_describe()
    if args.command == "certify":
        return cmd_certify()
    if args.command == "evidence":
        return cmd_evidence(args.directory)
    # `prove`, the --gate alias, and the no-argument default all run the gate: the most
    # useful default for a constitutional layer is to prove itself.
    return cmd_prove()


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
