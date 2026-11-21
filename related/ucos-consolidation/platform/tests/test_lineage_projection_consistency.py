"""F-1 — lineage projection consistency.

A projection may not assert an ancestry its source does not declare.

`ukb validate` already proved that a declared parent RESOLVES. It never proved that a
projected `Parent` edge is BACKED by a declared parent, and that silence is exactly how
F-1 survived 11,914 tests: a relationship row headed with prose ("Parent lineage") matched
the `PARENT` label, every reference in the cell was attributed to that label, and a
`Depends-On` target was emitted as a *second* `Parent` edge. Two artifacts carried two
parents each and nothing in the corpus could say so.

These tests hold the corrected state AND reconstruct the pre-correction state to prove the
rule refuses it. A rule that has never been shown to fail is not a rule.
"""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
ARTIFACTS = REPO / "00-BOOK" / "DATA" / "artifacts.json"
RELATIONSHIPS = REPO / "00-BOOK" / "DATA" / "relationships.json"

#: The two artifacts F-1 was found on, kept as data so the assertions below read as
#: measurements rather than as a story about two files.
F1_SUBJECTS = ("UCOS-EVOUSIS015-000002", "UCOS-EVOUSIS016-000002")


def _load() -> tuple[dict[str, dict], list[dict]]:
    artifacts = json.loads(ARTIFACTS.read_text(encoding="utf-8"))["artifacts"]
    artifacts = artifacts if isinstance(artifacts, list) else list(artifacts.values())
    edges = json.loads(RELATIONSHIPS.read_text(encoding="utf-8"))["relationships"]
    return {a["universal_id"]: a for a in artifacts}, edges


def _unbacked(by_uid: dict[str, dict], edges: list[dict]) -> list[tuple[str, str, str]]:
    """Every projected Parent edge whose target is not the declared parent."""
    findings = []
    for edge in edges:
        if edge.get("type") != "Parent":
            continue
        child, parent = edge.get("from"), edge.get("to")
        declared = by_uid.get(child, {}).get("parent")
        if child in by_uid and declared != parent:
            findings.append((child, parent, str(edge.get("note"))))
    return findings


def _multi_parent(edges: list[dict]) -> dict[str, set[str]]:
    seen: dict[str, set[str]] = defaultdict(set)
    for edge in edges:
        if edge.get("type") == "Parent":
            seen[edge["from"]].add(edge["to"])
    return {child: parents for child, parents in seen.items() if len(parents) > 1}


# --- the corrected state ---------------------------------------------------------------


def test_every_projected_parent_edge_is_backed_by_a_declared_parent() -> None:
    by_uid, edges = _load()
    findings = _unbacked(by_uid, edges)
    assert findings == [], (
        "a projection asserts an ancestry its source does not declare:\n  "
        + "\n  ".join(f"{c} -> {p} (note: {n})" for c, p, n in findings)
    )


def test_no_artifact_has_more_than_one_projected_parent() -> None:
    _, edges = _load()
    conflicting = _multi_parent(edges)
    assert conflicting == {}, f"artifacts with conflicting ancestry: {conflicting}"


def test_parent_and_child_edges_remain_exact_inverses() -> None:
    """The correction must not have unbalanced the graph."""
    _, edges = _load()
    parents = {(e["from"], e["to"]) for e in edges if e["type"] == "Parent"}
    children = {(e["to"], e["from"]) for e in edges if e["type"] == "Child"}
    assert parents == children


def test_the_f1_subjects_carry_the_declared_parent_and_a_dependency() -> None:
    """The specific outcome F-1 was closed to produce."""
    by_uid, edges = _load()
    for uid in F1_SUBJECTS:
        assert uid in by_uid, f"{uid} is no longer registered"
        outgoing = {(e["type"], e["to"]) for e in edges if e["from"] == uid}
        parents = {to for kind, to in outgoing if kind == "Parent"}
        depends = {to for kind, to in outgoing if kind == "Depends-On"}
        assert parents == {
            by_uid[uid]["parent"]
        }, f"{uid} projects {parents}, declared parent is {by_uid[uid]['parent']}"
        assert depends, f"{uid} declares a Depends-On that the projection does not carry"


def test_no_parent_edge_is_sourced_from_parent_metadata() -> None:
    """Structural containment is the only thing that may emit a Parent edge here.

    Not a prohibition on metadata edges in general — it records that, after F-1, no
    `Parent` edge in this corpus originates from a relationship-row label.
    """
    _, edges = _load()
    from_metadata = [
        (e["from"], e["to"], e.get("note"))
        for e in edges
        if e.get("type") == "Parent" and str(e.get("note", "")).startswith("metadata:")
    ]
    assert from_metadata == [], f"Parent edges emitted from metadata rows: {from_metadata}"


# --- the pre-correction state must be refused -------------------------------------------


def test_the_rule_refuses_the_pre_correction_state() -> None:
    """E-6: reconstruct F-1 exactly as it stood and prove the rule fails on it."""
    by_uid, edges = _load()
    pre = list(edges) + [
        {
            "edge_id": "UEDGE-TEST-1",
            "from": "UCOS-EVOUSIS015-000002",
            "to": "UCOS-USIS-000017",
            "type": "Parent",
            "inverse_of": None,
            "note": "metadata:PARENT",
        },
        {
            "edge_id": "UEDGE-TEST-2",
            "from": "UCOS-EVOUSIS016-000002",
            "to": "UCOS-USIS-000018",
            "type": "Parent",
            "inverse_of": None,
            "note": "metadata:PARENT",
        },
    ]
    findings = _unbacked(by_uid, pre)
    assert len(findings) == 2, f"the rule did not refuse the original defect: {findings}"
    assert {c for c, _, _ in findings} == set(F1_SUBJECTS)
    assert set(_multi_parent(pre)) == set(F1_SUBJECTS)


@pytest.mark.parametrize(
    "child,parent",
    [
        ("UCOS-EVOUSIS015-000002", "UCOS-USIS-000017"),
        ("UCOS-EVOUSIS016-000002", "UCOS-USIS-000018"),
    ],
)
def test_each_original_divergent_edge_is_individually_refused(child: str, parent: str) -> None:
    by_uid, edges = _load()
    pre = [*edges, {"from": child, "to": parent, "type": "Parent", "note": "metadata:PARENT"}]
    assert any(c == child and p == parent for c, p, _ in _unbacked(by_uid, pre))


def test_an_orphan_projected_edge_is_refused() -> None:
    """A Parent edge for a child the source does not register at all."""
    by_uid, edges = _load()
    subject = F1_SUBJECTS[0]
    pre = [*edges, {"from": subject, "to": "UCOS-NOT-A-REAL-ID", "type": "Parent", "note": "x"}]
    assert any(p == "UCOS-NOT-A-REAL-ID" for _, p, _ in _unbacked(by_uid, pre))
