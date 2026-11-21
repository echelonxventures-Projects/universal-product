"""EC2-TASK-000103/000104 — Blueprint provenance tests (EC2-EPIC-006, GOV-002 link-4).

Covers the provenance-by-reference record that discharges the link-4 Generation →
Implementation traceability break: the required trace fields, the traceability
predicate, the trace edge, and the append-only provenance ledger (fail-closed).
"""

from __future__ import annotations

from platform.blueprints.contracts import BlueprintFamily
from platform.blueprints.errors import BlueprintProvenanceError
from platform.blueprints.provenance import BlueprintProvenance, ProvenanceLedger

import pytest


def _prov(blueprint_ref="UCOS-BLPR-1", **overrides):
    base = dict(
        blueprint_ref=blueprint_ref,
        family=BlueprintFamily.DATA,
        generation_reference="GEN-DATA-001",
        generation_artifact_id="BP-DATA-0001",
        generation_source="05-GENERATION/GEN-DATA-001",
        implementation_target="platform/blueprints",
        content_hash="c0ffee",
        generation_lineage=("data",),
        implementation_lineage=("EC2-EPIC-006",),
        dependency_chain=("EPIC-005",),
        provenance_metadata={"k": "v"},
        audit_metadata={"by": "arch@x"},
    )
    base.update(overrides)
    return BlueprintProvenance.create(**base)


def test_provenance_carries_all_link4_fields():
    p = _prov()
    assert p.provenance_id.startswith("UCOS-BPRV-")
    assert p.generation_reference == "GEN-DATA-001"
    assert p.generation_artifact_id == "BP-DATA-0001"
    assert p.generation_source.startswith("05-GENERATION")
    assert p.generation_lineage == ("data",)
    assert p.implementation_target == "platform/blueprints"
    assert p.implementation_lineage == ("EC2-EPIC-006",)
    assert p.dependency_chain == ("EPIC-005",)
    assert p.content_hash == "c0ffee"
    assert p.provenance_metadata["k"] == "v"
    assert p.audit_metadata["by"] == "arch@x"
    assert p.is_traceable is True


def test_trace_edge_is_evidence_backed():
    edge = _prov().trace_edge()
    assert edge["link"] == "GOV-002-link-4"
    assert edge["generation"]["artifact_id"] == "BP-DATA-0001"
    assert edge["implementation"]["target"] == "platform/blueprints"
    assert edge["traceable"] is True


def test_provenance_is_deterministic():
    assert _prov().provenance_id == _prov().provenance_id
    assert _prov().fingerprint() == _prov().fingerprint()


@pytest.mark.parametrize(
    "overrides",
    [
        {"blueprint_ref": ""},
        {"family": "data"},
        {"generation_reference": ""},
        {"generation_artifact_id": ""},
        {"generation_source": ""},
        {"implementation_target": ""},
        {"content_hash": ""},
        {"generation_lineage": ("",)},
        {"provenance_metadata": {"": "v"}},
        {"provenance_metadata": {"k": 1}},
    ],
)
def test_provenance_rejects_malformed(overrides):
    with pytest.raises(BlueprintProvenanceError):
        _prov(**overrides)


def test_provenance_optional_collections_default_empty():
    p = _prov(
        generation_lineage=None,
        implementation_lineage=None,
        dependency_chain=None,
        provenance_metadata=None,
        audit_metadata=None,
    )
    assert p.generation_lineage == ()
    assert p.to_dict()["provenance_metadata"] == {}


# --------------------------------------------------------------------------- #
# Ledger                                                                       #
# --------------------------------------------------------------------------- #


def test_ledger_records_resolves_and_traces():
    ledger = ProvenanceLedger()
    p = _prov()
    assert ledger.record(p) is p
    assert ledger.has("UCOS-BLPR-1") is True
    assert "UCOS-BLPR-1" in ledger
    assert len(ledger) == 1
    assert ledger.get("UCOS-BLPR-1") is p
    assert ledger.blueprint_refs == ("UCOS-BLPR-1",)
    assert ledger.all() == (p,)
    assert ledger.trace("UCOS-BLPR-1")["traceable"] is True
    assert ledger.to_dict()["provenance_count"] == 1
    assert isinstance(ledger.fingerprint(), str)


def test_ledger_record_idempotent_and_conflict_fail_closed():
    ledger = ProvenanceLedger()
    ledger.record(_prov())
    assert ledger.record(_prov()) is not None  # idempotent
    assert len(ledger) == 1
    with pytest.raises(BlueprintProvenanceError):
        ledger.record(_prov(content_hash="different"))  # distinct provenance for same blueprint


def test_ledger_rejects_bad_and_untraceable_and_missing():
    ledger = ProvenanceLedger()
    with pytest.raises(BlueprintProvenanceError):
        ledger.record("nope")  # type: ignore[arg-type]
    with pytest.raises(BlueprintProvenanceError):
        ledger.get("UCOS-BLPR-missing")
    # A raw (bypass-create) untraceable provenance is refused (fail-closed).
    untraceable = BlueprintProvenance(
        blueprint_ref="UCOS-BLPR-1",
        family=BlueprintFamily.DATA,
        generation_reference="",
        generation_artifact_id="",
        generation_source="",
        generation_lineage=(),
        implementation_target="",
        implementation_lineage=(),
        dependency_chain=(),
        content_hash="",
        provenance_metadata={},
        audit_metadata={},
        provenance_id="UCOS-BPRV-raw",
    )
    assert untraceable.is_traceable is False
    with pytest.raises(BlueprintProvenanceError):
        ledger.record(untraceable)
