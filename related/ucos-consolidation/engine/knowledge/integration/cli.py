"""UKI — Constitutional Integration CLI (EPIC-UKDA-002).

The operational command-line surface over the Universal Constitutional Knowledge
Integration. It is the entry point CI, governance, and agents use to route an
artifact intent through the constitutional execution path:

    python -m engine.knowledge.integration.cli constitution        # D1: laws/layers/sequence
    python -m engine.knowledge.integration.cli discover  --intent i.json  # D2
    python -m engine.knowledge.integration.cli screen    --intent i.json  # D6 (exit 1 on violation)
    python -m engine.knowledge.integration.cli reuse     --intent i.json  # D5
    python -m engine.knowledge.integration.cli depends   CKO_ID            # D4
    python -m engine.knowledge.integration.cli trace     CKO_ID            # D7
    python -m engine.knowledge.integration.cli govern    CKO_ID            # D8
    python -m engine.knowledge.integration.cli register  --intent i.json  # D9
    python -m engine.knowledge.integration.cli compose   --intent i.json  # D10
    python -m engine.knowledge.integration.cli pipeline  --intent i.json  # path (exit 1 if blocked)
    python -m engine.knowledge.integration.cli assimilate REPO_PATH       # EPIC-UKDA-004

Every command loads the canonical store when present, else the seed base, and (by
default) merges the integration constitution so the backbone is present on a fresh
clone. Output is deterministic JSON.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from engine.knowledge.errors import KnowledgeError
from engine.knowledge.integration.composition import AutonomousComposer
from engine.knowledge.integration.constitution import (
    extend_base_with_constitution,
    integration_constitution,
)
from engine.knowledge.integration.contracts import ArtifactIntent
from engine.knowledge.integration.dependency import DependencyIntegration
from engine.knowledge.integration.discovery import DiscoveryProtocol
from engine.knowledge.integration.duplication import DuplicatePreventionEngine
from engine.knowledge.integration.governance import GovernanceIntegration
from engine.knowledge.integration.pipeline import ConstitutionalPipeline
from engine.knowledge.integration.registration import RegistrationIntegration
from engine.knowledge.integration.reuse import ReuseEngine
from engine.knowledge.integration.traceability import TraceabilityEngine
from engine.knowledge.seed import build_seed_base
from engine.knowledge.store import KnowledgeBase, KnowledgeStore


def _emit(payload: Any) -> None:
    print(json.dumps(payload, sort_keys=True, indent=2, ensure_ascii=False))


def _load_base(store_dir: str | None, *, with_constitution: bool) -> KnowledgeBase:
    store = KnowledgeStore(store_dir)
    base = store.load() if store.exists() else build_seed_base()
    if with_constitution:
        base = extend_base_with_constitution(base)
    return base


def _load_intent(path: str) -> ArtifactIntent:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return ArtifactIntent.from_dict(data)


def _cmd_constitution(args: argparse.Namespace) -> int:
    _emit(integration_constitution().to_dict())
    return 0


def _cmd_discover(args: argparse.Namespace) -> int:
    base = _load_base(args.store, with_constitution=not args.no_constitution)
    result = DiscoveryProtocol(base).discover(_load_intent(args.intent))
    _emit(result.to_dict())
    return 0


def _cmd_screen(args: argparse.Namespace) -> int:
    base = _load_base(args.store, with_constitution=not args.no_constitution)
    report = DuplicatePreventionEngine(base).screen(_load_intent(args.intent))
    _emit(report.to_dict())
    return 0 if report.clean else 1


def _cmd_reuse(args: argparse.Namespace) -> int:
    base = _load_base(args.store, with_constitution=not args.no_constitution)
    _emit(ReuseEngine(base).assess(_load_intent(args.intent)).to_dict())
    return 0


def _cmd_depends(args: argparse.Namespace) -> int:
    base = _load_base(args.store, with_constitution=not args.no_constitution)
    _emit(DependencyIntegration(base).view(args.cko_id).to_dict())
    return 0


def _cmd_trace(args: argparse.Namespace) -> int:
    base = _load_base(args.store, with_constitution=not args.no_constitution)
    _emit(TraceabilityEngine(base).trace(args.cko_id).to_dict())
    return 0


def _cmd_govern(args: argparse.Namespace) -> int:
    base = _load_base(args.store, with_constitution=not args.no_constitution)
    _emit(GovernanceIntegration(base).bind_object(args.cko_id).to_dict())
    return 0


def _cmd_register(args: argparse.Namespace) -> int:
    base = _load_base(args.store, with_constitution=not args.no_constitution)
    _emit(RegistrationIntegration(base).plan_intent(_load_intent(args.intent)).to_dict())
    return 0


def _cmd_compose(args: argparse.Namespace) -> int:
    base = _load_base(args.store, with_constitution=not args.no_constitution)
    result = AutonomousComposer(base).compose(_load_intent(args.intent))
    _emit(result.to_dict())
    return 0 if result.sufficient else 1


def _cmd_pipeline(args: argparse.Namespace) -> int:
    base = _load_base(args.store, with_constitution=not args.no_constitution)
    decision = ConstitutionalPipeline(base).execute(_load_intent(args.intent))
    _emit(decision.to_dict())
    return 0 if decision.accepted else 1


def _cmd_assimilate(args: argparse.Namespace) -> int:
    base = _load_base(args.store, with_constitution=not args.no_constitution)
    subject = ConstitutionalPipeline(base).assimilate(args.repository)
    if args.evidence_dir:
        from engine.knowledge.integration.repository import emit_evidence

        written = emit_evidence(subject, args.evidence_dir)
        _emit({"subject": subject.to_dict(), "artifacts": written})
    else:
        _emit(subject.to_dict())
    return 0 if subject.assimilated else 1


def _add_intent(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--intent", required=True, help="path to an artifact-intent JSON file")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ucos-knowledge-integration",
        description="UCOS Ω∞ Universal Constitutional Knowledge Integration (UKI) CLI.",
    )
    parser.add_argument("--store", default=None, help="canonical knowledge store directory")
    parser.add_argument(
        "--no-constitution",
        action="store_true",
        help="do not merge the integration constitution into the loaded base",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("constitution", help="print the integration constitution (D1)").set_defaults(
        func=_cmd_constitution
    )

    p_discover = sub.add_parser("discover", help="mandatory discovery (D2)")
    _add_intent(p_discover)
    p_discover.set_defaults(func=_cmd_discover)

    p_screen = sub.add_parser("screen", help="duplicate prevention (D6)")
    _add_intent(p_screen)
    p_screen.set_defaults(func=_cmd_screen)

    p_reuse = sub.add_parser("reuse", help="reuse determination (D5)")
    _add_intent(p_reuse)
    p_reuse.set_defaults(func=_cmd_reuse)

    p_depends = sub.add_parser("depends", help="dependency view (D4)")
    p_depends.add_argument("cko_id", help="canonical object id")
    p_depends.set_defaults(func=_cmd_depends)

    p_trace = sub.add_parser("trace", help="constitutional traceability (D7)")
    p_trace.add_argument("cko_id", help="canonical object id")
    p_trace.set_defaults(func=_cmd_trace)

    p_govern = sub.add_parser("govern", help="governance grounding (D8)")
    p_govern.add_argument("cko_id", help="governance object id")
    p_govern.set_defaults(func=_cmd_govern)

    p_register = sub.add_parser("register", help="registration plan (D9)")
    _add_intent(p_register)
    p_register.set_defaults(func=_cmd_register)

    p_compose = sub.add_parser("compose", help="autonomous composition (D10)")
    _add_intent(p_compose)
    p_compose.set_defaults(func=_cmd_compose)

    p_pipeline = sub.add_parser("pipeline", help="constitutional execution path")
    _add_intent(p_pipeline)
    p_pipeline.set_defaults(func=_cmd_pipeline)

    p_assimilate = sub.add_parser(
        "assimilate", help="assimilate a live repository into a RepositorySubject (EPIC-UKDA-004)"
    )
    p_assimilate.add_argument("repository", help="path to the live repository root")
    p_assimilate.add_argument(
        "--evidence-dir",
        default=None,
        help="directory to write the four repository report artifacts into",
    )
    p_assimilate.set_defaults(func=_cmd_assimilate)

    return parser


def main(argv: list[str] | None = None) -> int:
    """CLI entry point: ``python -m engine.knowledge.integration.cli <command>``."""
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except KnowledgeError as exc:
        print(json.dumps(exc.to_dict(), sort_keys=True, ensure_ascii=False))
        return 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())


__all__ = ["build_parser", "main"]
