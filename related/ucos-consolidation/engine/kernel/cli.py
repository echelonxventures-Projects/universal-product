"""``ucos-kernel`` — the Universal Meta-Kernel command line.

Subcommands (all deterministic; no wall-clock in any output):

    describe   print the kernel's self-description
    prove      run the constitutional quality gates + mandatory architectural proof
    certify    print the kernel self-certification
    evidence   write the deliverable evidence files into a directory

Exit semantics of ``prove`` / ``--gate``:
    0  constitutionally compliant (every gate passed, kernel unchanged)
    1  a gate failed
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from engine.kernel.compliance import (
    architectural_proof,
    constitutional_report,
)
from engine.kernel.identity import canonical_json
from engine.kernel.kernel import MetaKernel


def _emit(payload: object) -> None:
    print(canonical_json(payload))


def cmd_describe(_args: argparse.Namespace) -> int:
    """Print the kernel's self-description."""
    _emit(MetaKernel().describe())
    return 0


def cmd_certify(_args: argparse.Namespace) -> int:
    """Print the kernel self-certification."""
    _emit(MetaKernel().certify())
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
        "constitutional-compliance-report.json": report,
        "quality-gates.json": report["quality_gates"],
        "architectural-proof.json": architectural_proof(),
        "kernel-self-certification.json": MetaKernel().certify(),
        "kernel-description.json": MetaKernel().describe(),
        "kernel-snapshot.json": MetaKernel().registry.snapshot(),
    }
    written: list[str] = []
    for name, payload in artifacts.items():
        path = directory / name
        path.write_text(canonical_json(payload) + "\n", encoding="utf-8")
        written.append(str(path))
    _emit({"written": sorted(written), "verdict": report["verdict"]})
    return 0 if report["passed"] else 1


def build_parser() -> argparse.ArgumentParser:
    """Build the ``ucos-kernel`` argument parser."""
    parser = argparse.ArgumentParser(prog="ucos-kernel", description=__doc__)
    parser.add_argument(
        "--gate",
        action="store_true",
        help="alias for 'prove': fail-closed constitutional gate",
    )
    sub = parser.add_subparsers(dest="command")
    sub.add_parser("describe", help="print the kernel self-description").set_defaults(
        func=cmd_describe
    )
    sub.add_parser("certify", help="print the kernel self-certification").set_defaults(
        func=cmd_certify
    )
    sub.add_parser("prove", help="run the constitutional gates + architectural proof").set_defaults(
        func=cmd_prove
    )
    ev = sub.add_parser("evidence", help="write deliverable evidence files")
    ev.add_argument("directory", help="output directory for evidence artifacts")
    ev.set_defaults(func=cmd_evidence)
    return parser


def main(argv: list[str] | None = None) -> int:
    """Entry point for the ``ucos-kernel`` console script."""
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
