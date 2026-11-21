"""UCOS-EPIC-003 — Universal Discovery Engine CLI.

The operational command-line surface over registry-driven, deterministic discovery.
It is the entry point CI, governance, and agents use to discover the corpus and to
emit coverage reports and evidence:

    python -m engine.discovery.cli discover                       # full report (all dimensions)
    python -m engine.discovery.cli dimension dependency           # a single dimension
    python -m engine.discovery.cli coverage                       # coverage report only
    python -m engine.discovery.cli evidence --out DIR             # write the evidence bundle

Every command reads the read-only registry substrate (defaults to ``00-BOOK/DATA``;
override with ``--data-dir``). Output is deterministic JSON. Discovery exits non-zero
only when coverage is incomplete (a substrate gap), so CI can gate on universality.
"""

from __future__ import annotations

import argparse
import json
from typing import Any

from engine.discovery.contracts import DiscoveryKind
from engine.discovery.engine import UniversalDiscoveryEngine
from engine.discovery.evidence import build_coverage_document, emit_evidence
from engine.foundation.obs.errors import FoundationError


def _emit(payload: Any) -> None:
    print(json.dumps(payload, sort_keys=True, indent=2, ensure_ascii=False))


def _engine(args: argparse.Namespace) -> UniversalDiscoveryEngine:
    return UniversalDiscoveryEngine.open(args.data_dir)


def _cmd_discover(args: argparse.Namespace) -> int:
    report = _engine(args).discover()
    _emit(report.to_dict())
    return 0 if report.complete else 1


def _cmd_dimension(args: argparse.Namespace) -> int:
    result = _engine(args).discover_dimension(DiscoveryKind.coerce(args.dimension))
    _emit(result.to_dict())
    return 0 if result.complete else 1


def _cmd_coverage(args: argparse.Namespace) -> int:
    report = _engine(args).discover()
    _emit(build_coverage_document(report))
    return 0 if report.complete else 1


def _cmd_evidence(args: argparse.Namespace) -> int:
    report = _engine(args).discover()
    written = emit_evidence(report, args.out)
    _emit({"complete": report.complete, "artifacts": written})
    return 0 if report.complete else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ucos-discovery",
        description="UCOS Ω∞ Universal Discovery Engine (EPIC-003) — registry-driven discovery.",
    )
    parser.add_argument(
        "--data-dir",
        default=None,
        help="registry data directory (defaults to the read-only 00-BOOK/DATA)",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("discover", help="run universal discovery across all dimensions").set_defaults(
        func=_cmd_discover
    )

    p_dim = sub.add_parser("dimension", help="discover a single dimension")
    p_dim.add_argument(
        "dimension",
        choices=[k.value for k in DiscoveryKind],
        help="the discovery dimension to run",
    )
    p_dim.set_defaults(func=_cmd_dimension)

    sub.add_parser("coverage", help="print the aggregate coverage report").set_defaults(
        func=_cmd_coverage
    )

    p_evidence = sub.add_parser("evidence", help="write the deterministic evidence bundle")
    p_evidence.add_argument("--out", required=True, help="output directory for the evidence bundle")
    p_evidence.set_defaults(func=_cmd_evidence)

    return parser


def main(argv: list[str] | None = None) -> int:
    """CLI entry point: ``python -m engine.discovery.cli <command>``."""
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except FoundationError as exc:
        print(json.dumps(exc.to_dict(), sort_keys=True, ensure_ascii=False))
        return 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())


__all__ = ["build_parser", "main"]
