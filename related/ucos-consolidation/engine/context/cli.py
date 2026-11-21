"""UCXI-000001 Part 14 — Universal Context Intelligence CLI (``ucos-context``).

The single operational surface over the context layer. Every command is read-only over
the repository, deterministic, and emits canonical JSON, so its output can be diffed,
sealed and used as CI evidence:

    python -m engine.context.cli constitution              # the twelve laws
    python -m engine.context.cli taxonomy                  # the classification tree
    python -m engine.context.cli ontology                  # the declared shapes
    python -m engine.context.cli registry                  # the bootstrapped registry
    python -m engine.context.cli resolve temporal          # resolve one kind
    python -m engine.context.cli resolve-all               # resolvability of all kinds
    python -m engine.context.cli compose                   # bounded, isolated composition
    python -m engine.context.cli graph                     # context graph summary
    python -m engine.context.cli impact <context-id>       # change-impact query
    python -m engine.context.cli runtime                   # activation trace exemplar
    python -m engine.context.cli validate                  # the twelve rules (gate)
    python -m engine.context.cli certify                   # the eight dimensions (gate)
    python -m engine.context.cli evidence --out <path>     # the whole evidence document
    python -m engine.context.cli frames                    # the declared reference frames
    python -m engine.context.cli location --frame <key>    # resolve one frame (gate)
    python -m engine.context.cli rebase --frames a b       # re-resolve across frames
    python -m engine.context.cli location-validate         # the location rules (gate)
    python -m engine.context.cli location-certify          # the location dimensions (gate)
    python -m engine.context.cli location-replay           # the location fixed point (gate)

Exit codes are gate semantics, not decoration: ``0`` the assertion holds, ``1`` it does
not (validation findings, no certificate, unresolvable kind), ``2`` the request could not
be assessed at all (a refused context operation).
"""

from __future__ import annotations

import argparse
import json
from typing import Any

from engine.context.catalog import bootstrap_registry
from engine.context.certification import certify
from engine.context.composition import compose
from engine.context.constitution import CONTEXT_CONSTITUTION
from engine.context.errors import ContextError
from engine.context.evidence import build_evidence, evidence_index, write_evidence
from engine.context.graph import build_context_graph
from engine.context.location import build_context_registry, build_frame_registry
from engine.context.location import to_document as location_document
from engine.context.location_assurance import (
    certify_location,
    replay_location,
    validate_location,
)
from engine.context.registry import ContextRegistry
from engine.context.resolution import ContextRequest, resolution_report, resolve
from engine.context.runtime import ContextRuntime
from engine.context.validation import validate


def _emit(payload: Any) -> None:
    print(json.dumps(payload, sort_keys=True, indent=2, ensure_ascii=False))


def _registry(args: argparse.Namespace) -> ContextRegistry:
    """The context set every command operates on (the universal catalog)."""
    if getattr(args, "empty", False):
        return ContextRegistry()
    return bootstrap_registry()


def _cmd_constitution(args: argparse.Namespace) -> int:
    registry = _registry(args)
    assessment = CONTEXT_CONSTITUTION.assess(registry, graph=build_context_graph(registry))
    _emit({"constitution": CONTEXT_CONSTITUTION.to_dict(), "assessment": assessment.to_dict()})
    return 0 if assessment.compliant else 1


def _cmd_taxonomy(args: argparse.Namespace) -> int:
    _emit(_registry(args).taxonomy.to_dict())
    return 0


def _cmd_ontology(args: argparse.Namespace) -> int:
    _emit(_registry(args).ontology.to_dict())
    return 0


def _cmd_registry(args: argparse.Namespace) -> int:
    registry = _registry(args)
    payload: dict[str, Any] = {"summary": registry.summary(), "seal": registry.seal()}
    if args.verbose:
        payload["contexts"] = [record.to_dict() for record in registry.records()]
        payload["relations"] = [edge.to_dict() for edge in registry.relations()]
        payload["audit"] = [entry.to_dict() for entry in registry.audit()]
    _emit(payload)
    return 0 if not registry.verify_audit() else 1


def _cmd_resolve(args: argparse.Namespace) -> int:
    registry = _registry(args)
    resolved = resolve(
        registry,
        ContextRequest(kind=args.kind, namespace=args.namespace, boundary=args.boundary),
    )
    _emit(resolved.to_dict())
    return 0


def _cmd_resolve_all(args: argparse.Namespace) -> int:
    report = resolution_report(_registry(args))
    _emit(report)
    return 0 if report["all_resolvable"] else 1


def _cmd_compose(args: argparse.Namespace) -> int:
    registry = _registry(args)
    composed = compose(registry, require_universal=args.require_universal)
    _emit(composed.to_dict() if args.verbose else composed.summary())
    return 0 if composed.is_universally_complete else 1


def _cmd_graph(args: argparse.Namespace) -> int:
    graph = build_context_graph(_registry(args))
    _emit(graph.to_dict() if args.verbose else graph.summary())
    return 0 if not graph.validate() else 1


def _cmd_impact(args: argparse.Namespace) -> int:
    graph = build_context_graph(_registry(args))
    if not graph.graph.has_node(args.context_id):
        _emit({"error": "context not in graph", "context_id": args.context_id})
        return 1
    _emit(
        {
            "context_id": args.context_id,
            "taxon": graph.taxon_of(args.context_id),
            "dependencies": list(graph.dependencies_of(args.context_id)),
            "dependents": list(graph.dependents_of(args.context_id)),
            "transitive_dependencies": list(graph.transitive_dependencies(args.context_id)),
            "impacted": list(graph.impact_of(args.context_id)),
            "blast_radius": graph.blast_radius(args.context_id),
            "contained_by": list(graph.contained_by(args.context_id)),
            "constrained_by": list(graph.constrained_by(args.context_id)),
        }
    )
    return 0


def _cmd_runtime(args: argparse.Namespace) -> int:
    registry = _registry(args)
    composed = compose(registry)
    runtime = ContextRuntime()
    with runtime.activate(composed) as activation:
        payload = {
            "activation": activation.to_dict(),
            "trace": runtime.trace(),
            "frames": list(runtime.frames()),
            "kinds": list(composed.kinds()),
        }
    payload["released"] = runtime.current() is None
    _emit(payload)
    return 0


def _cmd_validate(args: argparse.Namespace) -> int:
    registry = _registry(args)
    report = validate(registry)
    _emit(report.to_dict() if args.verbose else report.summary())
    if args.strict:
        return 0 if report.is_clean else 1
    return 0 if report.is_valid else 1


def _cmd_certify(args: argparse.Namespace) -> int:
    certificate = certify(_registry(args))
    _emit(certificate.to_dict() if args.verbose else certificate.summary())
    return 0 if certificate.certified else 1


def _cmd_evidence(args: argparse.Namespace) -> int:
    evidence = build_evidence(_registry(args))
    if args.out:
        path = write_evidence(evidence, args.out)
        index = evidence_index(evidence)
        if args.index_out:
            write_evidence(index, args.index_out)
        _emit({"wrote": str(path), "index": index})
    else:
        _emit(evidence if args.verbose else evidence_index(evidence))
    return 0 if evidence["operational"] else 1


def _cmd_frames(args: argparse.Namespace) -> int:
    frames = build_frame_registry()
    _emit(frames.to_document() if args.verbose else frames.coverage())
    return 0


def _cmd_location(args: argparse.Namespace) -> int:
    """Resolve one frame, or report the whole architecture.

    A frame that leaves an axis unresolved exits non-zero: an incomplete context is a
    gate failure, never a context with holes in it.
    """
    frames = build_frame_registry()
    if not args.frame:
        _emit(location_document(frames))
        return 0
    resolution = frames.resolve(args.frame)
    payload = resolution.to_dict()
    payload["digest"] = resolution.digest()
    if args.verbose:
        payload["registered"] = [
            record.to_dict()
            for record in build_context_registry(args.frame, frames=frames).records()
        ]
    _emit(payload)
    return 0 if resolution.complete else 1


def _cmd_rebase(args: argparse.Namespace) -> int:
    frames = build_frame_registry()
    report = frames.rebase(args.subject, frame_keys=args.frames)
    _emit(report)
    return 0 if report["differing_count"] else 1


def _cmd_location_validate(args: argparse.Namespace) -> int:
    report = validate_location()
    _emit(report.to_dict() if args.verbose else report.summary())
    if args.strict:
        return 0 if report.is_clean else 1
    return 0 if report.is_valid else 1


def _cmd_location_certify(args: argparse.Namespace) -> int:
    certificate = certify_location()
    _emit(certificate.to_dict() if args.verbose else certificate.summary())
    return 0 if certificate.certified else 1


def _cmd_location_replay(_args: argparse.Namespace) -> int:
    replay = replay_location()
    _emit(replay)
    return 0 if replay["fixed_point"] else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ucos-context",
        description="Universal Context Intelligence (UCXI-000001) — read-only, deterministic.",
    )
    parser.add_argument(
        "--empty",
        action="store_true",
        help="operate on an empty registry instead of the universal catalog",
    )
    parser.add_argument("--verbose", action="store_true", help="emit the full document")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("constitution", help="the Context Constitution and its assessment").set_defaults(
        func=_cmd_constitution
    )
    sub.add_parser("taxonomy", help="the classification of all context").set_defaults(
        func=_cmd_taxonomy
    )
    sub.add_parser("ontology", help="the declared shape of every context kind").set_defaults(
        func=_cmd_ontology
    )

    p_reg = sub.add_parser("registry", help="the registered context set")
    p_reg.set_defaults(func=_cmd_registry)

    p_res = sub.add_parser("resolve", help="resolve one context kind")
    p_res.add_argument("kind")
    p_res.add_argument("--namespace", default=None)
    p_res.add_argument("--boundary", default=None)
    p_res.set_defaults(func=_cmd_resolve)

    sub.add_parser("resolve-all", help="resolvability of every universal kind").set_defaults(
        func=_cmd_resolve_all
    )

    p_comp = sub.add_parser("compose", help="compose a bounded, isolated context")
    p_comp.add_argument(
        "--require-universal",
        action="store_true",
        help="refuse a composition that does not cover every universal kind",
    )
    p_comp.set_defaults(func=_cmd_compose)

    sub.add_parser("graph", help="the context graph").set_defaults(func=_cmd_graph)

    p_imp = sub.add_parser("impact", help="change-impact query over one context")
    p_imp.add_argument("context_id")
    p_imp.set_defaults(func=_cmd_impact)

    sub.add_parser("runtime", help="activate the composed context and trace it").set_defaults(
        func=_cmd_runtime
    )

    p_val = sub.add_parser("validate", help="run the declared validation rules")
    p_val.add_argument(
        "--strict", action="store_true", help="fail on advisories as well as violations"
    )
    p_val.set_defaults(func=_cmd_validate)

    sub.add_parser("certify", help="compute the context certification").set_defaults(
        func=_cmd_certify
    )

    sub.add_parser("frames", help="the declared reference frames and their coverage").set_defaults(
        func=_cmd_frames
    )

    p_loc = sub.add_parser("location", help="resolve context from a reference frame")
    p_loc.add_argument("--frame", default="", help="frame key (default: the whole architecture)")
    p_loc.set_defaults(func=_cmd_location)

    p_reb = sub.add_parser("rebase", help="re-resolve one subject across several frames")
    p_reb.add_argument("--subject", default="ucos-context")
    p_reb.add_argument("--frames", nargs="+", required=True)
    p_reb.set_defaults(func=_cmd_rebase)

    p_lval = sub.add_parser("location-validate", help="run the declared location rules")
    p_lval.add_argument(
        "--strict", action="store_true", help="fail on advisories as well as violations"
    )
    p_lval.set_defaults(func=_cmd_location_validate)

    sub.add_parser("location-certify", help="compute the location certification").set_defaults(
        func=_cmd_location_certify
    )
    sub.add_parser("location-replay", help="prove the location fixed point").set_defaults(
        func=_cmd_location_replay
    )

    p_ev = sub.add_parser("evidence", help="build the context evidence document")
    p_ev.add_argument("--out", default=None, help="write the evidence document here")
    p_ev.add_argument("--index-out", default=None, help="write the evidence index here")
    p_ev.set_defaults(func=_cmd_evidence)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except ContextError as exc:
        _emit(exc.to_dict())
        return 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
