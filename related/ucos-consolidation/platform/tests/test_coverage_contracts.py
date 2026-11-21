"""ZG-P-02 — coverage vocabulary/contract tests."""

from __future__ import annotations

from platform.coverage.contracts import (
    COVERAGE_CONTRACTS,
    COVERAGE_SPINE,
    GOVERNANCE_AUTHORITIES,
    CoverageEdge,
    CoverageNode,
    CoverageNodeKind,
    CoverageStatus,
    coverage_contract_names,
    edge_kind_label,
    is_adjacent,
)
from platform.coverage.errors import CoverageContractError

import pytest

K = CoverageNodeKind


def test_spine_is_eight_ordered_tiers():
    assert len(COVERAGE_SPINE) == 8
    assert COVERAGE_SPINE[0] is K.UNIVERSE
    assert COVERAGE_SPINE[-1] is K.RUNTIME_ASSET


def test_adjacency_rules():
    assert is_adjacent(K.UNIVERSE, K.PHASE)
    assert is_adjacent(K.CODE_ASSET, K.RUNTIME_ASSET)
    assert not is_adjacent(K.UNIVERSE, K.PROGRAM)
    assert not is_adjacent(K.PHASE, K.UNIVERSE)
    assert not is_adjacent(K.RUNTIME_ASSET, K.UNIVERSE)
    assert edge_kind_label(K.UNIVERSE, K.PHASE) == "universe->phase"


def test_node_is_content_addressed_and_deterministic():
    a = CoverageNode.create(K.UNIVERSE, "UNI-001", label="Being", authority="cat")
    b = CoverageNode.create(K.UNIVERSE, "UNI-001", label="ignored-diff", authority="other")
    # node_id depends only on (kind, ref).
    assert a.node_id == b.node_id
    assert a.node_id.startswith("UCOS-COVN-")
    assert a.to_dict()["ref"] == "UNI-001"
    assert a.fingerprint() != b.fingerprint()  # authority/label differ


def test_node_metadata_and_default_label():
    n = CoverageNode.create(K.PHASE, "IMP-005", metadata={"tier": "0"})
    assert n.label == "IMP-005"
    assert n.to_dict()["metadata"] == {"tier": "0"}


@pytest.mark.parametrize(
    "kwargs",
    [
        {"kind": "not-a-kind", "ref": "x"},
        {"kind": K.UNIVERSE, "ref": ""},
        {"kind": K.UNIVERSE, "ref": "   "},
    ],
)
def test_node_creation_fails_closed(kwargs):
    with pytest.raises(CoverageContractError):
        CoverageNode.create(**kwargs)


def test_node_metadata_must_be_str_map():
    with pytest.raises(CoverageContractError):
        CoverageNode.create(K.UNIVERSE, "UNI-1", metadata={"k": 5})  # type: ignore[dict-item]


def test_edge_is_content_addressed_and_traceable():
    e = CoverageEdge.create(
        source_kind=K.UNIVERSE,
        source_ref="UNI-010",
        target_kind=K.PHASE,
        target_ref="IMP-005",
        authority="universe-catalog",
        evidence="row",
        tick=7,
    )
    assert e.edge_id.startswith("UCOS-COVE-")
    assert e.kind_label == "universe->phase"
    trace = e.trace()
    assert trace["source"] == {"kind": "universe", "ref": "UNI-010"}
    assert trace["target"] == {"kind": "phase", "ref": "IMP-005"}
    assert trace["authority"] == "universe-catalog"
    assert trace["timestamp"] == 7
    assert trace["fingerprint"] == e.fingerprint()
    # tick is excluded from identity + fingerprint (determinism).
    e0 = CoverageEdge.create(
        source_kind=K.UNIVERSE,
        source_ref="UNI-010",
        target_kind=K.PHASE,
        target_ref="IMP-005",
        authority="universe-catalog",
        evidence="row",
        tick=0,
    )
    assert e0.edge_id == e.edge_id
    assert e0.fingerprint() == e.fingerprint()


def test_edge_endpoint_node_ids_match_node_creation():
    e = CoverageEdge.create(
        source_kind=K.MODULE,
        source_ref="m.py",
        target_kind=K.CODE_ASSET,
        target_ref="m.py::f",
        authority="a",
        evidence="e",
    )
    assert e.source_node_id() == CoverageNode.create(K.MODULE, "m.py").node_id
    assert e.target_node_id() == CoverageNode.create(K.CODE_ASSET, "m.py::f").node_id


def test_edge_rejects_non_adjacent_tiers():
    with pytest.raises(CoverageContractError):
        CoverageEdge.create(
            source_kind=K.UNIVERSE,
            source_ref="UNI-1",
            target_kind=K.PROGRAM,
            target_ref="p",
            authority="a",
            evidence="e",
        )


@pytest.mark.parametrize(
    "field,value",
    [("source_ref", ""), ("target_ref", " "), ("authority", ""), ("evidence", "")],
)
def test_edge_rejects_empty_mandatory_fields(field, value):
    kwargs = dict(
        source_kind=K.UNIVERSE,
        source_ref="UNI-1",
        target_kind=K.PHASE,
        target_ref="IMP-1",
        authority="a",
        evidence="e",
    )
    kwargs[field] = value
    with pytest.raises(CoverageContractError):
        CoverageEdge.create(**kwargs)


def test_edge_rejects_bad_kinds_and_tick():
    with pytest.raises(CoverageContractError):
        CoverageEdge.create(
            source_kind="x",  # type: ignore[arg-type]
            source_ref="a",
            target_kind=K.PHASE,
            target_ref="b",
            authority="a",
            evidence="e",
        )
    with pytest.raises(CoverageContractError):
        CoverageEdge.create(
            source_kind=K.UNIVERSE,
            source_ref="UNI-1",
            target_kind=K.PHASE,
            target_ref="IMP-1",
            authority="a",
            evidence="e",
            tick=-1,
        )
    with pytest.raises(CoverageContractError):
        CoverageEdge.create(
            source_kind=K.UNIVERSE,
            source_ref="UNI-1",
            target_kind=K.PHASE,
            target_ref="IMP-1",
            authority="a",
            evidence="e",
            tick=True,  # bool rejected
        )


def test_published_contracts_and_authorities():
    names = coverage_contract_names()
    assert "coverage.engine.compute" in names
    assert len(COVERAGE_CONTRACTS) == len(names) == 5
    assert "MIP-ZG-001" in GOVERNANCE_AUTHORITIES
    assert "GOV-002" in GOVERNANCE_AUTHORITIES


def test_status_enum_values():
    assert {s.value for s in CoverageStatus} == {
        "covered",
        "partial",
        "uncovered",
        "orphaned",
    }
