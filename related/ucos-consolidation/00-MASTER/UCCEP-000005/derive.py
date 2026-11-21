#!/usr/bin/env python3
"""UCCEP-000005 — Repository Dependency Remediation Execution Programme.

Deterministic re-derivation driver. AUTHORITY = NONE (DERIVED TRUTH).

This module creates **no** graph engine, **no** validator and **no** registry. It
opens the located owners and records what they report:

    * ``engine.graph.adapter.KnowledgeGraphAdapter``  — the certified projection of
      Registry Truth (``00-BOOK/DATA``), owner ``engine/graph`` (UCOS-EPIC-002).
    * ``engine.graph.validation.validate_graph``       — the located dependency gate.
    * ``engine.graph.architecture.algorithms``         — the located SCC /
      condensation / longest-path algorithms (UCOS-EPIC-010).
    * ``engine.graph.architecture.critical_path``      — the located Critical Path
      Engine.

Read-only over the corpus (DP-03). Writes only inside
``00-MASTER/UCCEP-000005/`` (programme operational memory).

Usage::

    python3 00-MASTER/UCCEP-000005/derive.py --stage baseline
    python3 00-MASTER/UCCEP-000005/derive.py --stage post
"""

from __future__ import annotations

import argparse
import json
import logging
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
OUT = REPO / "00-MASTER" / "UCCEP-000005"
sys.path.insert(0, str(REPO))

logging.disable(logging.CRITICAL)

from engine.graph.adapter import KnowledgeGraphAdapter  # noqa: E402
from engine.graph.architecture.algorithms import (  # noqa: E402
    normalise_adjacency,
    strongly_connected_components,
)
from engine.graph.architecture.critical_path import CriticalPathEngine  # noqa: E402
from engine.graph.engine import DEPENDS_ON  # noqa: E402
from engine.graph.model import KIND_ARTIFACT  # noqa: E402
from engine.graph.validation import validate_graph  # noqa: E402

CHAIN_NOTE = "structural:chain"


def _git(*args: str) -> str:
    return subprocess.run(  # noqa: S603 — fixed argv, no shell, no user input
        ["git", *args],  # noqa: S607 — resolved from PATH by design, as CI does
        cwd=REPO,
        capture_output=True,
        text=True,
        check=False,
    ).stdout.strip()


def _dependency_view() -> dict[str, object]:
    """Everything the located owners report about the Depends-On projection."""
    adapter = KnowledgeGraphAdapter.open(None)
    core = adapter.core
    artifacts = {n.node_id for n in core.nodes_of_kind(KIND_ARTIFACT)}

    raw: list[tuple[str, str]] = []
    duplicates: dict[tuple[str, str], int] = {}
    self_loops: list[str] = []
    malformed: list[dict[str, str]] = []
    for edge in core.edges_of_type(DEPENDS_ON):
        pair = (edge.source, edge.target)
        if edge.source not in artifacts or edge.target not in artifacts:
            malformed.append(
                {"edge_id": edge.edge_id, "source": edge.source, "target": edge.target}
            )
            continue
        if edge.source == edge.target:
            self_loops.append(edge.source)
        duplicates[pair] = duplicates.get(pair, 0) + 1
        raw.append(pair)

    adjacency = normalise_adjacency(artifacts, raw)
    sccs = strongly_connected_components(adjacency)
    multi = [list(s) for s in sccs if len(s) > 1]

    # Deterministic dependency ordering (Kahn, sorted frontier) + parallel groups
    # (each group = the set of artifacts whose dependencies are all satisfied by
    # the preceding groups; every member of a group is independent of the others).
    dependencies: dict[str, set[str]] = {n: set(adjacency[n]) for n in adjacency}
    dependents: dict[str, set[str]] = {n: set() for n in adjacency}
    for node, targets in adjacency.items():
        for target in targets:
            dependents[target].add(node)

    remaining = {n: set(d) for n, d in dependencies.items()}
    groups: list[list[str]] = []
    ordering: list[str] = []
    while True:
        frontier = sorted(n for n, deps in remaining.items() if not deps)
        if not frontier:
            break
        groups.append(frontier)
        ordering.extend(frontier)
        for node in frontier:
            del remaining[node]
            for dependent in dependents[node]:
                if dependent in remaining:
                    remaining[dependent].discard(node)
    unordered = sorted(remaining)

    critical = CriticalPathEngine(core).critical_path()

    return {
        "artifact_nodes": len(artifacts),
        "depends_on_edges": len(raw),
        "duplicate_dependency_edges": sorted(
            [f"{s} -> {t}" for (s, t), n in duplicates.items() if n > 1]
        ),
        "malformed_dependency_edges": malformed,
        "self_loops": sorted(set(self_loops)),
        "scc_total": len(sccs),
        "scc_gt1_count": len(multi),
        "scc_gt1_members": multi,
        "acyclic": not multi and not self_loops,
        "dependency_ordering_count": len(ordering),
        "dependency_ordering_complete": not unordered,
        "unordered_nodes": unordered,
        "parallel_group_count": len(groups),
        "parallel_groups": groups,
        "critical_path": critical.to_dict()["path"],
        "critical_path_length": critical.length,
        "critical_path_cyclic": critical.cyclic,
        "validation_report": validate_graph(core).to_dict(),
    }


def _consistency() -> dict[str, object]:
    """Declared (artifacts.json) vs projected (relationships.json) dependency parity.

    A *hidden* dependency is a projected ``Depends-On`` edge with no counterpart in
    the source-of-record; an *unprojected* dependency is the converse. Both are
    reported so the two registers can be shown to agree rather than assumed to.
    """
    data = REPO / "00-BOOK" / "DATA"
    artifacts = json.loads((data / "artifacts.json").read_text())["artifacts"]
    rels = json.loads((data / "relationships.json").read_text())["relationships"]

    declared: set[tuple[str, str]] = set()
    parents: set[tuple[str, str]] = set()
    for a in artifacts:
        for dep in a.get("dependencies") or []:
            declared.add((a["universal_id"], dep))
        if a.get("parent"):
            parents.add((a["universal_id"], a["parent"]))

    projected: set[tuple[str, str]] = set()
    edge_ids: list[str] = []
    for r in rels:
        edge_ids.append(r["edge_id"])
        if r.get("type") == "Depends-On":
            projected.add((r["from"], r["to"]))

    known = {a["universal_id"] for a in artifacts}
    return {
        "declared_dependency_pairs": len(declared),
        "projected_depends_on_pairs": len(projected),
        "declared_not_projected": sorted(f"{s} -> {t}" for s, t in declared - projected),
        # metadata-derived edges legitimately exceed the artifacts.json list; report
        # the count and the ENG family explicitly rather than asserting equality.
        "projected_not_declared_count": len(projected - declared),
        "eng_projected_not_declared": sorted(
            f"{s} -> {t}" for s, t in projected - declared if s.startswith("UCOS-ENG-")
        ),
        "duplicate_edge_ids": sorted({e for e in edge_ids if edge_ids.count(e) > 1}),
        "dependency_endpoints_unknown": sorted(
            {x for pair in projected for x in pair if x not in known}
        ),
        "parent_pairs": len(parents),
    }


def _eng_chain_edges() -> list[dict[str, str]]:
    data = json.loads((REPO / "00-BOOK" / "DATA" / "relationships.json").read_text())
    eng = {f"UCOS-ENG-{i:06d}" for i in range(1, 10)}
    return [
        r
        for r in data["relationships"]
        if r.get("from") in eng and r.get("to") in eng and r.get("type") == "Depends-On"
    ]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="uccep-000005-derive")
    parser.add_argument("--stage", required=True, choices=["baseline", "post"])
    args = parser.parse_args(argv)

    payload = {
        "programme": "UCCEP-000005",
        "stage": args.stage,
        "authority": "NONE — DERIVED TRUTH",
        "head": _git("rev-parse", "HEAD"),
        "branch": _git("branch", "--show-current"),
        "worktree_entries": len([x for x in _git("status", "--porcelain").splitlines() if x]),
        "eng_depends_on_edges": _eng_chain_edges(),
        "consistency": _consistency(),
        "dependency": _dependency_view(),
    }
    target = OUT / "evidence" / f"{args.stage}" / "dependency-derivation.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")

    dep = payload["dependency"]
    print(
        json.dumps(
            {
                "stage": args.stage,
                "acyclic": dep["acyclic"],
                "scc_gt1_count": dep["scc_gt1_count"],
                "is_valid": dep["validation_report"]["is_valid"],
                "dependency_cycle": dep["validation_report"]["dependency_cycle"],
                "critical_path_length": dep["critical_path_length"],
                "parallel_group_count": dep["parallel_group_count"],
                "ordering_complete": dep["dependency_ordering_complete"],
                "wrote": str(target.relative_to(REPO)),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
