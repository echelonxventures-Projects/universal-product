"""``ucos-uprf`` — the Universal Provider Framework command line.

Subcommands (all deterministic; no wall-clock in any output):

    describe   print the framework's self-description
    prove      run the constitutional quality gates + mandatory architectural proof
    certify    print the framework self-certification
    evidence   write the deliverable evidence files into a directory

Exit semantics of ``prove``:
    0  constitutionally compliant (every gate passed; kernel + framework unchanged)
    1  a gate failed
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from engine.kernel.identity import canonical_json
from engine.provider.compliance import architectural_proof, constitutional_report
from engine.provider.framework import ProviderFramework


def _emit(payload: object) -> None:
    print(canonical_json(payload))


def cmd_describe(_args: argparse.Namespace) -> int:
    """Print the framework self-description."""
    _emit(ProviderFramework().describe())
    return 0


def cmd_certify(_args: argparse.Namespace) -> int:
    """Print the framework self-certification."""
    _emit(ProviderFramework().certify())
    return 0


def cmd_prove(_args: argparse.Namespace) -> int:
    """Run the constitutional gates + architectural proof; exit 0 iff compliant."""
    report = constitutional_report()
    _emit(report)
    return 0 if report["passed"] else 1


def cmd_evidence(args: argparse.Namespace) -> int:
    """Write the deliverable evidence files into a directory."""
    directory = Path(args.directory)
    directory.mkdir(parents=True, exist_ok=True)
    report = constitutional_report()
    artifacts = {
        "uprf-constitutional-compliance.json": report,
        "uprf-quality-gates.json": report["quality_gates"],
        "uprf-architectural-proof.json": architectural_proof(),
        "uprf-framework-certification.json": ProviderFramework().certify(),
        "uprf-framework-description.json": ProviderFramework().describe(),
    }
    written: list[str] = []
    for name, payload in artifacts.items():
        path = directory / name
        path.write_text(canonical_json(payload) + "\n", encoding="utf-8")
        written.append(str(path))
    _emit({"written": sorted(written), "verdict": report["verdict"]})
    return 0 if report["passed"] else 1


def build_parser() -> argparse.ArgumentParser:
    """Build the ``ucos-uprf`` argument parser."""
    parser = argparse.ArgumentParser(prog="ucos-uprf", description=__doc__)
    parser.add_argument("--gate", action="store_true", help="alias for 'prove'")
    sub = parser.add_subparsers(dest="command")
    sub.add_parser("describe", help="print the framework self-description").set_defaults(
        func=cmd_describe
    )
    sub.add_parser("certify", help="print the framework self-certification").set_defaults(
        func=cmd_certify
    )
    sub.add_parser("prove", help="constitutional gates + architectural proof").set_defaults(
        func=cmd_prove
    )
    ev = sub.add_parser("evidence", help="write deliverable evidence files")
    ev.add_argument("directory", help="output directory for evidence artifacts")
    ev.set_defaults(func=cmd_evidence)
    return parser


def main(argv: list[str] | None = None) -> int:
    """Entry point for the ``ucos-uprf`` console script."""
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.gate and not getattr(args, "command", None):
        return cmd_prove(args)
    if not getattr(args, "func", None):
        parser.print_help()
        return 0
    return int(args.func(args))


if __name__ == "__main__":
    sys.exit(main())
