"""ULP Part 03 — the projection generator and its validation.

Composition, not collection. Each family is built from the source that OWNS that meaning:

    structure     ← artifacts.json parent, via the typed edges already projected from it
    dependency    ← declared metadata rows, via the same typed edges
    derivation    ← generated-artifact-registry producer + input_closure
    supersession  ← change-ledger lineage predecessors/successors
    transformation← change-ledger change_events  (EVENTS, never edges)

Determinism is structural rather than promised: every collection is sorted on a total key
before it is emitted, nothing reads a clock, and no path or machine identifier enters the
document. Two builds over one repository state produce identical bytes, and
:func:`verify` proves it by building twice.

The generator writes NOTHING. A lineage store is what ``UCI-001 XVI.5`` forbids — *"lineage
and evolution are DERIVED projections over recorded history; no new store is created"* — so
the document exists to be compared and queried, not to be kept.
"""

from __future__ import annotations

import json
import os
from typing import Any

from engine.lineage.model import (
    ANCESTOR_FROM,
    Classification,
    LineageEdge,
    LineageError,
    LineageEvent,
    LineageProjection,
)
from engine.lineage.sources import (
    SOURCE_FILES,
    declared_relations,
    load_sources,
    primary_relations,
    repo_root,
)
from engine.uckp.canonical import canonical_json, content_hash

_CLASSIFICATION = os.path.join("engine", "lineage", "families.json")

#: Source labels carried on every edge, so an answer can always cite where it came from.
SRC_RELATIONSHIPS = "00-BOOK/DATA/relationships.json"
SRC_GENERATED = "00-BOOK/DATA/generated-artifact-registry.json"
SRC_CHANGE_LEDGER = "00-BOOK/DATA/change-ledger.json"


def load_classification(path: str | None = None, repo: str | None = None) -> Classification:
    """Load the family classification and refuse one the vocabulary owner does not back."""
    repo = repo or repo_root()
    target = path or os.path.join(repo, _CLASSIFICATION)
    try:
        with open(target, encoding="utf-8") as handle:
            document = json.load(handle)
    except FileNotFoundError:
        raise LineageError("the lineage classification is absent", subject=target) from None
    except json.JSONDecodeError as error:
        raise LineageError(f"the lineage classification is not valid JSON ({error})") from None

    classification = Classification.of(document)
    declared = declared_relations(repo)
    invented = sorted(classification.classified - declared)
    if invented:
        raise LineageError(
            "the classification names relations the vocabulary owner does not declare: "
            + ", ".join(invented)
        )
    unclassified = sorted(declared - classification.classified)
    if unclassified:
        raise LineageError(
            "declared relations that the classification accounts for neither as lineage nor "
            "as non-lineage: " + ", ".join(unclassified)
        )
    return classification


def build(
    repo: str | None = None, classification: Classification | None = None
) -> LineageProjection:
    """Compose the projection from the governed sources. Reads only."""
    repo = repo or repo_root()
    classification = classification or load_classification(repo=repo)
    sources = load_sources(repo)
    rules = classification.rules

    edges: list[LineageEdge] = []

    # structure + dependency + any other classified family already carried as a typed edge.
    for edge in sources["edges"]:
        rule = rules.get(str(edge.get("type")))
        if rule is None:
            continue
        head, tail = str(edge.get("from", "")), str(edge.get("to", ""))
        if not head or not tail:
            continue
        ancestor, descendant = (head, tail) if rule.ancestor == ANCESTOR_FROM else (tail, head)
        edges.append(
            LineageEdge(
                descendant=descendant,
                ancestor=ancestor,
                relation=rule.relation,
                family=rule.family,
                source=SRC_RELATIONSHIPS,
            )
        )

    # derivation — the producer and its declared input closure own this meaning.
    derivation = _family_named(classification, "derivation")
    produced_by = _relation_named(derivation, "Produced-By") if derivation else None
    derived_from = _relation_named(derivation, "Derived-From") if derivation else None
    for entry in sources["generated"]:
        artifact = str(entry.get("canonical_path", ""))
        producer = str(entry.get("producer", ""))
        if artifact and producer and produced_by is not None:
            edges.append(
                LineageEdge(
                    descendant=artifact,
                    ancestor=producer,
                    relation=produced_by.relation,
                    family=produced_by.family,
                    source=SRC_GENERATED,
                )
            )
        if artifact and derived_from is not None:
            for source_input in entry.get("input_closure") or ():
                edges.append(
                    LineageEdge(
                        descendant=artifact,
                        ancestor=str(source_input),
                        relation=derived_from.relation,
                        family=derived_from.family,
                        source=SRC_GENERATED,
                    )
                )

    # supersession — the change ledger owns which object replaced which.
    supersession = _family_named(classification, "supersession")
    supersedes = _relation_named(supersession, "Supersedes") if supersession else None
    if supersedes is not None:
        for subject, record in sources["change_lineage"].items():
            for predecessor in record.get("predecessors") or ():
                edges.append(
                    LineageEdge(
                        descendant=str(subject),
                        ancestor=str(predecessor),
                        relation=supersedes.relation,
                        family=supersedes.family,
                        source=SRC_CHANGE_LEDGER,
                    )
                )

    events = [
        LineageEvent(
            subject=str(event.get("subject", "")),
            kind=str(event.get("kind", "")),
            at=str(event.get("at", "")),
            sequence=int(event.get("snapshot_seq") or 0),
            source=SRC_CHANGE_LEDGER,
        )
        for event in sources["change_events"]
        if event.get("subject")
    ]

    return LineageProjection(
        classification=classification,
        edges=_one_edge_per_fact(edges, primary_relations(repo)),
        events=tuple(sorted(events, key=_event_key)),
        sources={
            "artifacts": len(sources["artifacts"]),
            "births": len(sources["births"]),
            "change_events": len(sources["change_events"]),
            "change_lineage": len(sources["change_lineage"]),
            "generated": len(sources["generated"]),
            "identity_history": len(sources["history"]),
            "typed_edges": len(sources["edges"]),
        },
    )


def _one_edge_per_fact(
    edges: list[LineageEdge], primaries: frozenset[str]
) -> tuple[LineageEdge, ...]:
    """Collapse each ancestry FACT to one edge, preferring the owner's forward relation.

    The corpus graph expresses one containment twice — ``Parent`` and its inverse
    ``Child`` — and reporting both would make a single fact look like two ancestors. Which
    name is forward is read from the vocabulary owner, never chosen here. Measured on this
    corpus: ``Parent`` and inverted ``Child`` are exactly equal, and every ``Required-By``
    has a forward ``Depends-On``, so nothing is lost by keeping the forward name.
    """
    best: dict[tuple[str, str, str, str], LineageEdge] = {}
    for edge in edges:
        key = (edge.family, edge.descendant, edge.ancestor, edge.source)
        current = best.get(key)
        if current is None or (edge.relation in primaries and current.relation not in primaries):
            best[key] = edge
    return tuple(sorted(best.values(), key=_edge_key))


def _family_named(classification: Classification, name: str):
    for family in classification.families:
        if family.name == name:
            return family
    return None


def _relation_named(family, relation: str):
    if family is None:
        return None
    for rule in family.relations:
        if rule.relation == relation:
            return rule
    return None


def _edge_key(edge: LineageEdge) -> tuple[str, str, str, str, str]:
    return (edge.family, edge.relation, edge.descendant, edge.ancestor, edge.source)


def _event_key(event: LineageEvent) -> tuple[int, str, str, str]:
    return (event.sequence, event.subject, event.kind, event.at)


def to_document(projection: LineageProjection) -> dict[str, Any]:
    """Serialise the projection. No clock, no path, no machine identifier."""
    return {
        "schema": "ucos-universal-lineage-projection",
        "version": "1.0.0",
        "authority": (
            "NONE — DERIVED PROJECTION over recorded history (UCI-001 XVI.5). It creates no "
            "store, mints no identifier and owns no relation: every edge cites the governed "
            "source that declared it. Deleting this document changes no verdict."
        ),
        "classification": projection.classification.declaration_id,
        "sources": dict(sorted(projection.sources.items())),
        "families": [
            {
                "family": family.name,
                "question": family.question,
                "acyclic": family.acyclic,
                "relations": sorted(rule.relation for rule in family.relations),
                "edges": projection.by_family().get(family.name, 0),
            }
            for family in projection.classification.families
        ],
        # WHY THE EXCLUSIONS ARE IN THE REPORT AND NOT ONLY IN THE CLASSIFICATION. A reader
        # counting 8,773 lineage edges against 13,791 typed ones will ask where the difference
        # went, and a report that answers "some relations are not ancestry" without saying which
        # or why invites the reader to assume an omission. Carrying the reasons here makes the
        # boundary of lineage as citable as its contents.
        "non_lineage": [
            {"relation": relation, "reason": reason}
            for relation, reason in projection.classification.non_lineage_reasons
        ],
        "counts": {
            "edges": len(projection.edges),
            "events": len(projection.events),
            "nodes": len(
                {e.ancestor for e in projection.edges} | {e.descendant for e in projection.edges}
            ),
        },
        "edges": [edge.as_dict() for edge in projection.edges],
        "$transformation": (
            "change_events are carried as EVENTS, never as edges: 'what happened to this "
            "object' is a different question from 'what other object it came from'."
        ),
        "closed_set": False,
        "upper_limit": None,
    }


def rendered(projection: LineageProjection) -> str:
    """The projection's canonical serialisation.

    Delegates to Layer Zero rather than serialising here. ``engine/uckp/canonical.py`` is
    the ONE permitted home of ``canonical_json``/``content_hash`` (UCKP Article 13), and
    ``UCKP-INV-03`` refuses a module-level redefinition anywhere under ``engine/`` or
    ``platform/``. An earlier draft of this module defined its own ``canonical_json`` and
    the invariant caught it — a second canonicaliser is a second authority over every hash
    it produces, which is exactly what a derived projection must never become.
    """
    return canonical_json(to_document(projection))


def digest(projection: LineageProjection) -> str:
    """The projection's content digest, from the canonical primitive."""
    return content_hash(to_document(projection))


# --- validation -----------------------------------------------------------------------


def validate(projection: LineageProjection, repo: str | None = None) -> list[str]:
    """Return every problem with the projection. Empty means healthy.

    Fail-closed on the properties the architecture named: source-backed relationships,
    relation-type correctness, and per-family acyclicity. Completeness and root
    reachability are deliberately NOT asserted here — they are recorded open gaps, and a
    check that quietly answered them would be a claim this projection has not earned.
    """
    repo = repo or repo_root()
    sources = load_sources(repo)
    problems: list[str] = []

    declared = declared_relations(repo)
    for edge in projection.edges:
        if edge.relation not in declared:
            problems.append(f"{edge.relation} is not a declared relation ({edge.descendant})")

    # Source-backed: a structural ancestry must equal the declared parent (the F-1 rule,
    # restated over the projection so it holds however the edge reached it).
    by_id = sources["artifacts_by_id"]
    structural = [e for e in projection.edges if e.family == "structure" and e.relation == "Parent"]
    for edge in structural:
        declared_parent = (by_id.get(edge.descendant) or {}).get("parent")
        if edge.descendant in by_id and declared_parent != edge.ancestor:
            problems.append(
                f"{edge.descendant}: projected structural ancestor {edge.ancestor} is not the "
                f"declared parent {declared_parent}"
            )
    seen: dict[str, set[str]] = {}
    for edge in structural:
        seen.setdefault(edge.descendant, set()).add(edge.ancestor)
    for node, ancestors in sorted(seen.items()):
        if len(ancestors) > 1:
            problems.append(f"{node} has conflicting structural ancestry: {sorted(ancestors)}")

    for family in projection.classification.families:
        if not family.acyclic:
            continue
        cycle = _find_cycle(projection, family.name)
        if cycle:
            problems.append(f"{family.name} family is not acyclic: {' -> '.join(cycle)}")
    return problems


def _find_cycle(projection: LineageProjection, family: str) -> list[str]:
    adjacency: dict[str, list[str]] = {}
    for edge in projection.edges:
        if edge.family == family:
            adjacency.setdefault(edge.descendant, []).append(edge.ancestor)
    state: dict[str, int] = {}
    stack: list[str] = []

    def walk(node: str) -> list[str]:
        state[node] = 1
        stack.append(node)
        for nxt in sorted(adjacency.get(node, ())):
            if state.get(nxt) == 1:
                return stack[stack.index(nxt) :] + [nxt]
            if state.get(nxt, 0) == 0:
                found = walk(nxt)
                if found:
                    return found
        stack.pop()
        state[node] = 2
        return []

    for node in sorted(adjacency):
        if state.get(node, 0) == 0:
            found = walk(node)
            if found:
                return found
    return []


def verify(repo: str | None = None) -> dict[str, Any]:
    """Build twice and report determinism, validation and the composed counts."""
    repo = repo or repo_root()
    first = build(repo)
    second = build(repo)
    problems = validate(first, repo)
    return {
        "schema": "ucos-universal-lineage-projection-verification",
        "version": "1.0.0",
        "deterministic": digest(first) == digest(second) and rendered(first) == rendered(second),
        "digest": digest(first),
        "sources": dict(sorted(first.sources.items())),
        "source_files": list(SOURCE_FILES),
        "families": dict(sorted(first.by_family().items())),
        "edges": len(first.edges),
        "events": len(first.events),
        "problems": problems,
        "status": "PASS" if not problems else "FAIL",
    }


__all__ = [
    "SRC_CHANGE_LEDGER",
    "SRC_GENERATED",
    "SRC_RELATIONSHIPS",
    "build",
    "digest",
    "rendered",
    "load_classification",
    "to_document",
    "validate",
    "verify",
]
