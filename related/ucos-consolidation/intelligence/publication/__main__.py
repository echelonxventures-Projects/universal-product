"""Publication Intelligence command-line interface (head-less, AI-agnostic).

    python -m intelligence.publication build             regenerate every publication
    python -m intelligence.publication formats           print the format catalog
    python -m intelligence.publication generate <fmt>    print one rendered publication
    python -m intelligence.publication set               print the generated set (JSON)
    python -m intelligence.publication registry          print the Publication Registry
    python -m intelligence.publication validate          print the validation report
    python -m intelligence.publication snapshot          print the compact snapshot
    python -m intelligence.publication verify            prove deterministic regeneration
    python -m intelligence.publication gate              fail-closed gate

The format space is open: pass ``--formats-file <path>`` to any command to register
additional section types and formats from a JSON declaration, or drop the file at
``intelligence/UCOS-UPI-001/publication-formats.json`` to have it loaded automatically.

Exit codes: 0 gate open · 1 gate closed · 2 fail-closed abort.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from intelligence.kernel.canonical import canonical_json
from intelligence.kernel.config import subsystem_config
from intelligence.kernel.errors import KernelError
from intelligence.kernel.validation import EXIT_ABORT
from intelligence.publication.engine import OUTPUT_DIR, PublicationIntelligenceEngine
from intelligence.publication.formats import FormatRegistry
from intelligence.publication.generators import NAMED_DELIVERABLES


def _engine(args: argparse.Namespace) -> PublicationIntelligenceEngine:
    root = Path(args.repo).resolve() if args.repo else None
    config = subsystem_config(OUTPUT_DIR, root)
    formats: FormatRegistry | None = None
    if getattr(args, "formats_file", None):
        formats = FormatRegistry()
        formats.load_file(args.formats_file)
    return PublicationIntelligenceEngine(config, formats)


def _emit(payload: object) -> int:
    print(canonical_json(payload), end="")
    return 0


def _cmd_build(args: argparse.Namespace) -> int:
    engine = _engine(args)
    written = engine.write()
    print(f"UPI: regenerated {len(written)} artifacts under {engine.config.output_dir}:")
    for path in written:
        print(f"  - {Path(path).relative_to(engine.config.output_dir)}")
    return 0


def _cmd_formats(args: argparse.Namespace) -> int:
    return _emit(_engine(args).formats.catalog())


def _cmd_generate(args: argparse.Namespace) -> int:
    engine = _engine(args)
    format_id = NAMED_DELIVERABLES.get(args.format, args.format)
    spec = engine.generator.build(format_id, engine.scope())
    _document, body = engine.composer.render(spec)
    print(body, end="" if body.endswith("\n") else "\n")
    return 0


def _cmd_set(args: argparse.Namespace) -> int:
    return _emit(_engine(args).publications().to_dict())


def _cmd_registry(args: argparse.Namespace) -> int:
    return _emit(_engine(args).registry().document())


def _cmd_validate(args: argparse.Namespace) -> int:
    report = _engine(args).validation()
    _emit(report.to_dict())
    return report.exit_code


def _cmd_snapshot(args: argparse.Namespace) -> int:
    return _emit(_engine(args).outputs()["UCOS-UPI-SNAPSHOT.json"])


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
        prog="intelligence.publication",
        description="UCOS-UPI-001 Universal Publication Intelligence",
    )
    parser.add_argument("--repo", help="repository root (default: auto-resolve)")
    parser.add_argument(
        "--formats-file",
        help="JSON declaration of additional section types and publication formats",
    )
    sub = parser.add_subparsers(dest="command", required=True)
    for name, fn, help_text in (
        ("build", _cmd_build, "regenerate every publication and its evidence"),
        ("formats", _cmd_formats, "print the open format catalog"),
        ("set", _cmd_set, "print the generated publication set"),
        ("registry", _cmd_registry, "print the Publication Registry document"),
        ("validate", _cmd_validate, "print the Publication Validation report"),
        ("snapshot", _cmd_snapshot, "print the compact snapshot"),
        ("verify", _cmd_verify, "prove deterministic regeneration"),
        ("gate", _cmd_gate, "fail-closed publication gate"),
    ):
        parser_sub = sub.add_parser(name, help=help_text)
        parser_sub.set_defaults(func=fn)
    parser_generate = sub.add_parser("generate", help="render a single publication to stdout")
    parser_generate.add_argument(
        "format",
        help="format id or named deliverable " f"({', '.join(sorted(NAMED_DELIVERABLES))})",
    )
    parser_generate.set_defaults(func=_cmd_generate)
    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except KernelError as exc:
        print(f"UCOS-UPI-001: FAIL-CLOSED ABORT | {exc}", file=sys.stderr)
        return EXIT_ABORT


if __name__ == "__main__":
    sys.exit(main())
