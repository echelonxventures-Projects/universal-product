"""UCOS-EPIC-002 (Terminal T2) — Universal Knowledge Graph CLI.

The single command-line surface over the Universal Knowledge Graph. It is a
read-only operational entry point (CI, governance, developer/agent onboarding):

    python -m engine.graph.cli summary                    # whole-graph summary
    python -m engine.graph.cli projections                 # per-projection sizes
    python -m engine.graph.cli node UCOS-BOOK-000000        # inspect one node
    python -m engine.graph.cli neighbors UCOS-REG-000001     # adjacency
    python -m engine.graph.cli deps UCOS-ENG-000001          # dependencies/dependents
    python -m engine.graph.cli impact UCOS-REG-000001        # blast radius
    python -m engine.graph.cli trace UCOS-IMP-000009         # traceability chain
    python -m engine.graph.cli validate                       # invariants gate
    python -m engine.graph.cli visualize --projection dependency --format dot
    python -m engine.graph.cli evidence --out .runtime/kg/evidence.json

Output is deterministic JSON (or DOT/Mermaid for ``visualize``). Every command is
read-only over the certified corpus (DP-03).
"""

from __future__ import annotations

import argparse
import json
from typing import Any

from engine.graph.adapter import KnowledgeGraphAdapter
from engine.graph.errors import GraphError
from engine.graph.evidence import build_evidence, write_evidence
from engine.graph.projections import PROJECTION_NAMES
from engine.graph.visualization import VISUALIZATION_FORMATS


def _emit(payload: Any) -> None:
    print(json.dumps(payload, sort_keys=True, indent=2, ensure_ascii=False))


def _adapter(args: argparse.Namespace) -> KnowledgeGraphAdapter:
    return KnowledgeGraphAdapter.open(getattr(args, "data_dir", None))


def _cmd_summary(args: argparse.Namespace) -> int:
    _emit(_adapter(args).summary())
    return 0


def _cmd_projections(args: argparse.Namespace) -> int:
    adapter = _adapter(args)
    _emit({name: adapter.projection(name).summary() for name in PROJECTION_NAMES})
    return 0


def _cmd_node(args: argparse.Namespace) -> int:
    node = _adapter(args).core.find(args.node_id)
    if node is None:
        _emit({"error": "node not found", "node_id": args.node_id})
        return 1
    _emit(node.to_dict())
    return 0


def _cmd_neighbors(args: argparse.Namespace) -> int:
    core = _adapter(args).core
    if not core.has_node(args.node_id):
        _emit({"error": "node not found", "node_id": args.node_id})
        return 1
    _emit(
        {
            "node": args.node_id,
            "successors": list(core.successors(args.node_id)),
            "predecessors": list(core.predecessors(args.node_id)),
            "degree": core.degree(args.node_id),
        }
    )
    return 0


def _cmd_deps(args: argparse.Namespace) -> int:
    dep = _adapter(args).dependency()
    if not dep.graph.has_node(args.node_id):
        _emit({"error": "node not in dependency projection", "node_id": args.node_id})
        return 1
    _emit(
        {
            "node": args.node_id,
            "dependencies": list(dep.dependencies_of(args.node_id)),
            "dependents": list(dep.dependents_of(args.node_id)),
            "transitive_dependencies": list(dep.transitive_dependencies(args.node_id)),
        }
    )
    return 0


def _cmd_impact(args: argparse.Namespace) -> int:
    impact = _adapter(args).impact()
    _emit(
        {
            "node": args.node_id,
            "blast_radius": impact.blast_radius(args.node_id),
            "impacted": list(impact.impact_of(args.node_id)),
            "upstream": list(impact.upstream_of(args.node_id)),
        }
    )
    return 0


def _cmd_trace(args: argparse.Namespace) -> int:
    trace = _adapter(args).traceability()
    _emit(
        {
            "node": args.node_id,
            "trace_forward": list(trace.trace_forward(args.node_id)),
            "trace_backward": list(trace.trace_backward(args.node_id)),
            "stages": {k: list(v) for k, v in trace.stages_of(args.node_id).items()},
        }
    )
    return 0


def _cmd_validate(args: argparse.Namespace) -> int:
    report = _adapter(args).validate()
    _emit(report.to_dict())
    return 0 if report.is_valid else 1


def _cmd_visualize(args: argparse.Namespace) -> int:
    output = _adapter(args).visualize(args.projection, fmt=args.format)
    print(output)
    return 0


def _cmd_evidence(args: argparse.Namespace) -> int:
    adapter = _adapter(args)
    evidence = build_evidence(adapter)
    if args.out:
        path = write_evidence(evidence, args.out)
        _emit({"wrote": str(path), "operational": evidence["operational"]})
    else:
        _emit(evidence)
    return 0 if evidence["operational"] else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ucos-knowledge-graph",
        description="Universal Knowledge Graph over Registry Truth (UCOS-EPIC-002, read-only).",
    )
    parser.add_argument(
        "--data-dir",
        dest="data_dir",
        default=None,
        help="registry data directory (defaults to 00-BOOK/DATA)",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("summary", help="whole-graph summary").set_defaults(func=_cmd_summary)
    sub.add_parser("projections", help="per-projection sizes").set_defaults(func=_cmd_projections)

    p_node = sub.add_parser("node", help="inspect one node")
    p_node.add_argument("node_id")
    p_node.set_defaults(func=_cmd_node)

    p_nb = sub.add_parser("neighbors", help="adjacency of a node")
    p_nb.add_argument("node_id")
    p_nb.set_defaults(func=_cmd_neighbors)

    p_deps = sub.add_parser("deps", help="dependencies and dependents of a node")
    p_deps.add_argument("node_id")
    p_deps.set_defaults(func=_cmd_deps)

    p_imp = sub.add_parser("impact", help="change-impact blast radius of a node")
    p_imp.add_argument("node_id")
    p_imp.set_defaults(func=_cmd_impact)

    p_trace = sub.add_parser("trace", help="traceability chain of a node")
    p_trace.add_argument("node_id")
    p_trace.set_defaults(func=_cmd_trace)

    sub.add_parser("validate", help="validate graph invariants").set_defaults(func=_cmd_validate)

    p_vis = sub.add_parser("visualize", help="render the graph or a projection")
    p_vis.add_argument(
        "--projection",
        choices=PROJECTION_NAMES,
        default=None,
        help="projection to render (defaults to the full core graph)",
    )
    p_vis.add_argument("--format", choices=VISUALIZATION_FORMATS, default="json")
    p_vis.set_defaults(func=_cmd_visualize)

    p_ev = sub.add_parser("evidence", help="build the operational evidence document")
    p_ev.add_argument("--out", default=None, help="write evidence JSON to this path")
    p_ev.set_defaults(func=_cmd_evidence)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except GraphError as exc:
        _emit(exc.to_dict())
        return 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
