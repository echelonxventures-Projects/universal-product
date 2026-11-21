"""URI-000001 — the Realization Intelligence command surface.

    python -m intelligence.realization intake      canonical knowledge state + integrity
    python -m intelligence.realization plan        derive the realization plan
    python -m intelligence.realization compose      compose the plan into units
    python -m intelligence.realization generate     generate artifacts in memory (no writes)
    python -m intelligence.realization govern       adjudicate the twelve gates
    python -m intelligence.realization trace        traceability closure both directions
    python -m intelligence.realization realize      the full pipeline (writes artifacts)
    python -m intelligence.realization realize --dry-run   plan the writes, write nothing
    python -m intelligence.realization verify       determinism + artifact + evidence proof
    python -m intelligence.realization evidence     re-emit the consolidated bundle
    python -m intelligence.realization generators   the wired generator registry

Exit codes follow the repository convention: ``0`` pass, ``1`` fail-closed verdict
(rejected / non-deterministic / unclosed trace), ``2`` a raised engine error.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from engine.foundation.obs.errors import FoundationError
from intelligence.realization.config import RealizationConfig
from intelligence.realization.engine import RealizationIntelligenceEngine
from intelligence.realization.errors import GovernanceRejectedError
from intelligence.realization.evidence import verify_bundle
from intelligence.realization.generators import registry_manifest
from intelligence.realization.traceability import coverage_summary


def _emit(payload: Any) -> None:
    print(json.dumps(payload, sort_keys=True, indent=2, ensure_ascii=False))


def _engine(args: argparse.Namespace) -> RealizationIntelligenceEngine:
    config = RealizationConfig.create(
        Path(args.repo).resolve() if args.repo else None,
        artifact_root=args.artifact_root,
        evidence_dir=args.evidence_dir,
        knowledge_dir=args.knowledge_dir,
    )
    return RealizationIntelligenceEngine(config)


# -- commands ----------------------------------------------------------------


def _cmd_intake(args: argparse.Namespace) -> int:
    intake = _engine(args).intake()
    _emit(intake.to_dict())
    return 0


def _cmd_plan(args: argparse.Namespace) -> int:
    engine = _engine(args)
    plan = engine.plan()
    _emit(plan.to_dict())
    return 0 if not plan.coverage_gaps else 1


def _cmd_compose(args: argparse.Namespace) -> int:
    engine = _engine(args)
    intake = engine.intake()
    plan = engine.planner.plan(intake)
    composition, findings = engine.composer.compose(intake, plan)
    _emit({"composition": composition.to_dict(), "findings": findings.to_dict()})
    return 0 if findings.clean else 1


def _cmd_generate(args: argparse.Namespace) -> int:
    engine = _engine(args)
    intake, plan, composition, _findings, manifest = engine.generate()
    payload: dict[str, Any] = {"generation": manifest.to_dict()}
    if args.show_content:
        payload["contents"] = {
            artifact.relative_path: artifact.content for artifact in manifest.artifacts
        }
    payload["determinism"] = engine.generator.verify_determinism(intake, plan, composition)
    _emit(payload)
    return 0 if payload["determinism"]["deterministic"] else 1


def _cmd_govern(args: argparse.Namespace) -> int:
    decision = _engine(args).govern()
    _emit(decision.to_dict())
    return 0 if decision.governed else 1


def _cmd_trace(args: argparse.Namespace) -> int:
    engine = _engine(args)
    ledger = engine.trace()
    payload = ledger.to_dict()
    if not args.edges:
        payload.pop("edges", None)
    payload["coverage"] = dict(coverage_summary(ledger, engine.intake()))
    _emit(payload)
    return 0 if ledger.closed else 1


def _cmd_realize(args: argparse.Namespace) -> int:
    engine = _engine(args)
    try:
        result = engine.realize(
            dry_run=args.dry_run,
            strict=not args.no_strict,
            emit=not args.no_evidence,
            prune=args.prune,
        )
    except GovernanceRejectedError as exc:
        _emit(exc.to_dict())
        return 1
    _emit(result.summary())
    return 0 if result.governed else 1


def _cmd_verify(args: argparse.Namespace) -> int:
    report = _engine(args).verify()
    _emit(report)
    return 0 if report["verified"] else 1


def _cmd_evidence(args: argparse.Namespace) -> int:
    engine = _engine(args)
    if args.check_only:
        report = verify_bundle(engine.config)
        _emit(report)
        return 0 if report["complete"] else 1
    result = engine.realize(dry_run=True, strict=False, emit=True)
    _emit(
        {
            "evidence_id": result.evidence.evidence_id,
            "verdict": result.decision.verdict,
            "emitted": sorted(result.emitted),
            "directory": engine.config.rel(engine.config.evidence_dir),
        }
    )
    return 0 if result.governed else 1


def _cmd_generators(_args: argparse.Namespace) -> int:
    _emit({"generators": registry_manifest(), "count": len(registry_manifest())})
    return 0


# -- parser ------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ucos-realize",
        description=(
            "URI-000001 Universal Realization Intelligence — realize canonical knowledge "
            "into governed, traceable, deterministically regenerable artifacts."
        ),
    )
    parser.add_argument("--repo", help="repository root (default: auto-resolve)")
    parser.add_argument("--knowledge-dir", help="canonical knowledge store directory (read-only)")
    parser.add_argument(
        "--artifact-root", help="generated-artifact root (default: <repo>/realization)"
    )
    parser.add_argument(
        "--evidence-dir",
        help="evidence bundle directory (default: <repo>/data/_evidence/URI-000001)",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    for name, handler, help_text in (
        ("intake", _cmd_intake, "show the canonical knowledge state and its integrity"),
        ("plan", _cmd_plan, "derive the realization plan"),
        ("compose", _cmd_compose, "compose the plan into sealed units"),
        ("govern", _cmd_govern, "adjudicate the twelve fail-closed gates"),
        ("verify", _cmd_verify, "prove determinism, artifacts and evidence"),
        ("generators", _cmd_generators, "list the wired generator registry"),
    ):
        node = sub.add_parser(name, help=help_text)
        node.set_defaults(func=handler)

    node_generate = sub.add_parser("generate", help="generate artifacts in memory without writing")
    node_generate.add_argument(
        "--show-content",
        action="store_true",
        help="include full artifact bodies in the output",
    )
    node_generate.set_defaults(func=_cmd_generate)

    node_trace = sub.add_parser("trace", help="traceability closure in both directions")
    node_trace.add_argument(
        "--edges", action="store_true", help="include every trace edge in the output"
    )
    node_trace.set_defaults(func=_cmd_trace)

    node_realize = sub.add_parser("realize", help="run the full realization pipeline")
    node_realize.add_argument(
        "--dry-run", action="store_true", help="compute the writes without performing them"
    )
    node_realize.add_argument(
        "--no-strict",
        action="store_true",
        help="report a rejection instead of raising (still writes nothing when rejected)",
    )
    node_realize.add_argument(
        "--no-evidence", action="store_true", help="skip emitting the evidence bundle"
    )
    node_realize.add_argument(
        "--prune",
        action="store_true",
        help="remove artifacts a previous pass generated that are no longer claimed",
    )
    node_realize.set_defaults(func=_cmd_realize)

    node_evidence = sub.add_parser("evidence", help="emit or check the evidence bundle")
    node_evidence.add_argument(
        "--check-only",
        action="store_true",
        help="verify the on-disk bundle instead of re-emitting it",
    )
    node_evidence.set_defaults(func=_cmd_evidence)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except FoundationError as exc:
        print(json.dumps(exc.to_dict(), sort_keys=True, indent=2, ensure_ascii=False))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = ["build_parser", "main"]
