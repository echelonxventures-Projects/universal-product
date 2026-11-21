"""Tests for EC3-B13-U10 Universal Infrastructure Integration realization + evidence."""

from __future__ import annotations

import importlib as _il
import json
import tempfile
from pathlib import Path

import pytest as _pytest

from infrastructure.integration_meta import (
    CONCERN_COUNT,
    EDGE_COUNT,
    LEAF_META_CLASSES,
    REALIZATION_UNIT,
)
from infrastructure.integration_realize import (
    Composition,
    RealizationResult,
    build_canonical_composition,
    determinism_check,
    emit_evidence,
    realize,
)


class TestComposition:
    def test_build_canonical_composition(self):
        comp = build_canonical_composition()
        assert isinstance(comp, Composition)
        assert len(comp.ordered()) == EDGE_COUNT == 24

    def test_all_edges_downward_only(self):
        for edge in build_canonical_composition().ordered():
            assert edge.is_downward_only()
            assert edge.source_index > edge.target_index

    def test_all_edges_single_meta_class(self):
        metas = {e.meta_class for e in build_canonical_composition().ordered()}
        assert metas == {"InfrastructureDependency"}


class TestRealization:
    def test_realize_returns_result(self):
        result = realize()
        assert isinstance(result, RealizationResult)
        assert len(result.realizations) == 24

    def test_all_accepted_certified_traceable(self):
        result = realize()
        assert result.all_accepted()
        assert result.all_certified()
        assert result.all_traceable()

    def test_all_concerns_certified_by_reference(self):
        result = realize()
        assert result.all_concerns_certified()
        assert len(result.concern_bindings) == CONCERN_COUNT == 9
        assert all(b["certified"] for b in result.concern_bindings)

    def test_leaf_closure_complete(self):
        result = realize()
        assert result.leaf_closure_complete()
        assert set(LEAF_META_CLASSES) == set(
            mc for b in result.concern_bindings for mc in b["meta_classes"]
        ) | {"InfrastructureDependency"}

    def test_no_duplication_guarantees(self):
        for key, ok in realize().no_duplication().items():
            assert ok, f"duplication guarantee failed: {key}"

    def test_graph_acyclic_and_downward(self):
        result = realize()
        assert result.graph_is_acyclic()
        assert result.graph_is_downward_only()
        assert result.all_concern_nodes_present()

    def test_meta_validity_passes(self):
        for wf, ok in realize().meta_validity().items():
            assert ok, f"WF {wf} failed"

    def test_uil_conformance_passes(self):
        for law, ok in realize().uil_conformance().items():
            assert ok, f"UIL {law} failed"

    def test_compliance_passes(self):
        for cid, ok in realize().integration_compliance().items():
            assert ok, f"compliance {cid} failed"

    def test_determination_complete(self):
        assert realize().determination(byte_identical=True) == "COMPLETE"

    def test_distinct_certification_ids(self):
        cids = realize().certification_ids()
        assert len(cids) == 24
        assert len(set(cids.values())) == 24


class TestDeliverables:
    def test_dependency_graph(self):
        g = realize().dependency_graph()
        assert g["edge_count"] == 24
        assert g["node_count"] == 9
        assert g["downward_only"] and g["acyclic"] and g["all_nodes_present"]

    def test_composition_model_closure(self):
        m = realize().composition_model()
        assert m["leaf_meta_class_closure"]["complete"]
        assert m["ownership_disjoint"]

    def test_capability_interaction_matrix(self):
        mtx = realize().capability_interaction_matrix()
        assert len(mtx["axis"]) == 9
        assert mtx["interaction_count"] == 24
        # governance depends on all eight lower concerns (outdegree 8).
        assert mtx["outdegree"]["governance"] == 8
        # capability is depended-upon by 3 resources (reuses) + security + governance = 5.
        assert mtx["indegree"]["capability"] == 5
        assert mtx["outdegree"]["capability"] == 0

    def test_integration_registry(self):
        reg = realize().integration_registry()
        assert len(reg["dependency_constructs"]) == 24
        assert len(reg["concern_units"]) == 9
        assert reg["leaf_closure_complete"]


class TestDeterminism:
    def test_determinism_check_passes(self):
        byte_identical, a, b = determinism_check()
        assert byte_identical
        assert a == b

    def test_double_realize_identical(self):
        assert realize().to_bundle(byte_identical=True) == realize().to_bundle(byte_identical=True)


class TestEvidence:
    def test_emit_evidence_complete(self):
        with tempfile.TemporaryDirectory() as tmp:
            summary = emit_evidence(Path(tmp) / "_evidence" / REALIZATION_UNIT)
            assert summary["determination"] == "COMPLETE"
            assert summary["validation_accepted"]
            assert summary["certified"]
            assert summary["traceability_closed"]
            assert summary["concerns_certified"]
            assert summary["byte_identical"]
            assert summary["leaf_closure_complete"]
            assert all(summary["no_duplication"].values())

    def test_all_evidence_files_written(self):
        with tempfile.TemporaryDirectory() as tmp:
            evidence_dir = Path(tmp) / "_evidence" / REALIZATION_UNIT
            emit_evidence(evidence_dir)
            expected = [
                "realization-evidence.json",
                "validation-report.json",
                "validation-evidence.json",
                "acceptance-decision.json",
                "cce-certification.json",
                "certification-evidence.json",
                "certification-ledger.json",
                "infrastructure-compliance.json",
                "traceability.json",
                "determinism.json",
                "repository-verification.json",
                "integration-architecture.json",
                "dependency-graph.json",
                "composition-model.json",
                "capability-interaction-matrix.json",
                "integration-registry.json",
                "twin-sync.json",
            ]
            for name in expected:
                p = evidence_dir / name
                assert p.exists(), f"Missing: {name}"
                assert json.loads(p.read_text(encoding="utf-8")) is not None


def test_determination_ladder_answers_below_complete() -> None:
    """The ladder below COMPLETE — conditions and refusal — had no case on this band.

    The real bundle always realizes to COMPLETE, so the two lower rungs were never observed.
    A determination with three outcomes and one measured path is two outcomes pretending.
    The conditions rung is reached by withholding the determinism claim; the refusal rung by
    a result whose acceptance roll-up says otherwise — the shape a broken future realization
    would take, forced here rather than assumed.
    """

    result = realize()
    assert result.determination(byte_identical=False) == "COMPLETE WITH CONDITIONS"

    class _NeverAccepted(RealizationResult):
        def all_accepted(self) -> bool:
            return False

    weakened = _NeverAccepted(
        result.composition,
        result.realizations,
        result.concern_bindings,
        result.ledger,
    )
    assert weakened.determination(byte_identical=True) == "NOT COMPLETE"


def test_unknown_lookup_raises_instead_of_returning_a_default() -> None:
    """A lookup that answered None would turn a miss into a silent pass downstream."""

    result = realize()
    with _pytest.raises(KeyError):
        result.by_type_tag("NO-SUCH-TAG")


def test_a_concern_that_fails_to_bind_is_recorded_as_an_error_not_a_halt(monkeypatch) -> None:
    """Reuse-by-reference binding must survive a concern that raises, and SAY so.

    The loop's except-arm converts any failure into `ERROR:<type>` so a broken concern cannot
    silently vanish from the binding table — and cannot take the integration down with it.
    Only a raised import makes that arm real, so the import is raised here for one concern.
    """

    from infrastructure import integration_realize as band

    first = band.CONCERN_REGISTRY[0].module
    real_import = _il.import_module

    def flaky(name: str):
        if name.endswith(f".{first}_realize"):
            raise RuntimeError("concern unavailable")
        return real_import(name)

    monkeypatch.setattr(band.importlib, "import_module", flaky)
    bindings = band.bind_certified_concerns()
    assert bindings[0]["determination"] == "ERROR:RuntimeError"
    assert all("unit" in b and "determination" in b for b in bindings)
