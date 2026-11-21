"""Research Intelligence command-line interface (head-less, AI-agnostic).

    python -m intelligence.research build       regenerate every research output
    python -m intelligence.research corpus      print the assimilated research corpus
    python -m intelligence.research registry    print the Research Registry document
    python -m intelligence.research standards   print the Standards Analysis
    python -m intelligence.research validate    print the Research Validation report
    python -m intelligence.research snapshot    print the compact snapshot
    python -m intelligence.research verify      prove deterministic regeneration
    python -m intelligence.research gate        fail-closed gate (0 open / 1 closed / 2 abort)

Exit codes follow the repository-wide programme convention:
    0 gate open · 1 gate closed · 2 fail-closed abort (no verdict assertable).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from intelligence.kernel.canonical import canonical_json
from intelligence.kernel.config import subsystem_config
from intelligence.kernel.errors import KernelError
from intelligence.kernel.validation import EXIT_ABORT
from intelligence.research.engine import OUTPUT_DIR, ResearchIntelligenceEngine


def _engine(args: argparse.Namespace) -> ResearchIntelligenceEngine:
    root = Path(args.repo).resolve() if args.repo else None
    return ResearchIntelligenceEngine(subsystem_config(OUTPUT_DIR, root))


def _emit(payload: object) -> int:
    print(canonical_json(payload), end="")
    return 0


def _cmd_build(args: argparse.Namespace) -> int:
    engine = _engine(args)
    written = engine.write()
    print(f"URI: regenerated {len(written)} research outputs under {engine.config.output_dir}:")
    for path in written:
        print(f"  - {Path(path).name}")
    return 0


def _cmd_corpus(args: argparse.Namespace) -> int:
    return _emit(_engine(args).corpus().to_dict())


def _cmd_registry(args: argparse.Namespace) -> int:
    return _emit(_engine(args).registry().document())


def _cmd_standards(args: argparse.Namespace) -> int:
    return _emit(_engine(args).standards().model())


def _cmd_validate(args: argparse.Namespace) -> int:
    report = _engine(args).validation()
    _emit(report.to_dict())
    return report.exit_code


def _cmd_snapshot(args: argparse.Namespace) -> int:
    return _emit(_engine(args).outputs()["UCOS-URI-SNAPSHOT.json"])


def _cmd_verify(args: argparse.Namespace) -> int:
    result = _engine(args).verify_determinism()
    _emit(result)
    return 0 if result["deterministic"] else 1


def _cmd_gate(args: argparse.Namespace) -> int:
    code, line = _engine(args).gate()
    print(line)
    return code


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="intelligence.research",
        description="UCOS-URI-001 Universal Research Intelligence",
    )
    parser.add_argument("--repo", help="repository root (default: auto-resolve)")
    sub = parser.add_subparsers(dest="command", required=True)
    for name, fn, help_text in (
        ("build", _cmd_build, "regenerate every research output"),
        ("corpus", _cmd_corpus, "print the assimilated research corpus"),
        ("registry", _cmd_registry, "print the Research Registry document"),
        ("standards", _cmd_standards, "print the Standards Analysis"),
        ("validate", _cmd_validate, "print the Research Validation report"),
        ("snapshot", _cmd_snapshot, "print the compact snapshot"),
        ("verify", _cmd_verify, "prove deterministic regeneration"),
        ("gate", _cmd_gate, "fail-closed research gate"),
    ):
        parser_sub = sub.add_parser(name, help=help_text)
        parser_sub.set_defaults(func=fn)
    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except KernelError as exc:
        print(f"UCOS-URI-001: FAIL-CLOSED ABORT | {exc}", file=sys.stderr)
        return EXIT_ABORT


if __name__ == "__main__":
    sys.exit(main())
