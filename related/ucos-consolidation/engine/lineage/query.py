"""ULP Part 04 — the query surface: six questions, every answer citing its source.

The architecture determination fixed the contract: *every answer cites the source authority
it came from and the family it belongs to; an answer that cannot name its source is not
returned.* That is what keeps a projection from becoming a quiet second opinion — a caller
can always follow an answer back to the governed record that declared it.

Nothing here computes lineage. It reads the composed projection and the same governed
sources, and reports.
"""

from __future__ import annotations

from typing import Any

from engine.lineage.model import LineageProjection
from engine.lineage.sources import load_sources, repo_root


def owner_of(node: str, sources: dict[str, Any]) -> dict[str, str] | None:
    """Who is accountable for this, and which record says so."""
    artifact = sources["artifacts_by_id"].get(node)
    if artifact and artifact.get("owner"):
        return {"owner": str(artifact["owner"]), "source": "00-BOOK/DATA/artifacts.json"}
    return None


def origin_of(
    node: str, projection: LineageProjection, sources: dict[str, Any]
) -> list[dict[str, str]]:
    """Where this came from — every ancestry edge, each naming its family and source."""
    found = [
        {
            "ancestor": edge.ancestor,
            "family": edge.family,
            "relation": edge.relation,
            "source": edge.source,
        }
        for edge in projection.ancestors_of(node)
    ]
    record = sources["change_lineage"].get(node)
    if record and record.get("birth"):
        found.append(
            {
                "ancestor": str(record.get("origin") or node),
                "family": "supersession",
                "relation": "origin",
                "source": "00-BOOK/DATA/change-ledger.json",
            }
        )
    return sorted(found, key=lambda f: (f["family"], f["relation"], f["ancestor"]))


def answer(
    node: str, projection: LineageProjection | None = None, repo: str | None = None
) -> dict[str, Any]:
    """Answer the six lineage questions for one node.

    Every value carries the record that supplied it. An unanswerable question returns an
    empty answer rather than a guess.
    """
    from engine.lineage.projection import build

    repo = repo or repo_root()
    projection = projection or build(repo)
    sources = load_sources(repo)
    artifact = sources["artifacts_by_id"].get(node)
    history = sources["history"].get(node) or []

    return {
        "node": node,
        "what_is_this": (
            {
                "category": str(artifact.get("category") or ""),
                "name": str(artifact.get("name") or ""),
                "source": "00-BOOK/DATA/artifacts.json",
            }
            if artifact
            else {}
        ),
        "who_owns_this": owner_of(node, sources) or {},
        "where_did_it_come_from": origin_of(node, projection, sources),
        "when_was_it_created": (
            {"at": str(history[0].get("at", "")), "source": "00-BOOK/DATA/id-ledger.json"}
            if history
            else {}
        ),
        "what_has_it_become": [
            {"kind": e.kind, "at": e.at, "sequence": e.sequence, "source": e.source}
            for e in projection.events_for(node)
        ],
        "what_depends_on_it": [
            {
                "descendant": edge.descendant,
                "family": edge.family,
                "relation": edge.relation,
                "source": edge.source,
            }
            for edge in projection.descendants_of(node)
        ],
    }


__all__ = ["answer", "origin_of", "owner_of"]
