"""EC2-TASK-000113 — Generation request provenance tests (EC2-EPIC-007).

Covers the link-4 trace continuation: RequestProvenance carrying the
Generation→Blueprint→Request→Implementation edge by reference, fail-closed field
validation, the traceability predicate, and the append-only ProvenanceLedger.
"""

from __future__ import annotations

from platform.blueprints.contracts import BlueprintFamily
from platform.generation.errors import RequestProvenanceError
from platform.generation.provenance import ProvenanceLedger, RequestProvenance

import pytest


def _prov(**kw):
    base = dict(
        request_ref="UCOS-GREQ-1",
        blueprint_ref="UCOS-BLPR-abc",
        family=BlueprintFamily.DATA,
        generation_reference="GEN-DATA-001",
        generation_artifact_id="BP-DATA-0001",
        blueprint_provenance_ref="UCOS-BPRV-xyz",
        implementation_target="platform/generation",
        content_hash="c0ffee",
        dependency_chain=("EPIC-006",),
    )
    base.update(kw)
    return RequestProvenance.create(**base)


def test_provenance_is_content_addressed_and_traceable():
    p = _prov()
    assert p.provenance_id.startswith("UCOS-GPRV-")
    assert p.is_traceable is True
    assert _prov().provenance_id == p.provenance_id


def test_trace_edge_carries_full_chain():
    edge = _prov().trace_edge()
    assert edge["link"] == "GOV-002-link-4"
    assert edge["generation"]["artifact_id"] == "BP-DATA-0001"
    assert edge["blueprint"]["provenance_ref"] == "UCOS-BPRV-xyz"
    assert edge["request"]["request_ref"] == "UCOS-GREQ-1"
    assert edge["implementation"]["target"] == "platform/generation"
    assert edge["traceable"] is True


@pytest.mark.parametrize(
    "kw",
    [
        {"request_ref": ""},
        {"blueprint_ref": " "},
        {"family": "data"},
        {"generation_reference": ""},
        {"generation_artifact_id": ""},
        {"blueprint_provenance_ref": ""},
        {"implementation_target": ""},
        {"content_hash": ""},
        {"dependency_chain": ("",)},
        {"provenance_metadata": {"": "v"}},
        {"provenance_metadata": {"k": 1}},
        {"audit_metadata": {"k": 1}},
    ],
)
def test_provenance_rejects_malformed(kw):
    with pytest.raises(RequestProvenanceError):
        _prov(**kw)


def test_to_dict_and_fingerprint_deterministic():
    a = _prov(provenance_metadata={"x": "1"}, audit_metadata={"a": "b"})
    b = _prov(provenance_metadata={"x": "1"}, audit_metadata={"a": "b"})
    assert a.fingerprint() == b.fingerprint()
    assert a.to_dict()["provenance_id"] == a.provenance_id


def test_ledger_record_get_trace():
    ledger = ProvenanceLedger()
    p = _prov()
    assert ledger.record(p) is p
    assert ledger.has("UCOS-GREQ-1")
    assert "UCOS-GREQ-1" in ledger
    assert ledger.get("UCOS-GREQ-1") is p
    assert ledger.trace("UCOS-GREQ-1")["traceable"] is True
    assert len(ledger) == 1
    assert ledger.request_refs == ("UCOS-GREQ-1",)
    assert len(ledger.all()) == 1


def test_ledger_idempotent_and_conflict():
    ledger = ProvenanceLedger()
    ledger.record(_prov())
    assert ledger.record(_prov()) is not None  # identical ⇒ returns stored
    with pytest.raises(RequestProvenanceError):
        ledger.record(_prov(content_hash="different"))


def test_ledger_rejects_non_provenance_and_absent():
    ledger = ProvenanceLedger()
    with pytest.raises(RequestProvenanceError):
        ledger.record("nope")  # type: ignore[arg-type]
    with pytest.raises(RequestProvenanceError):
        ledger.get("UCOS-GREQ-missing")


def test_ledger_refuses_untraceable_record():
    # An untraceable provenance can only exist by bypassing create(); construct directly.
    untraceable = RequestProvenance(
        request_ref="UCOS-GREQ-1",
        blueprint_ref="UCOS-BLPR-abc",
        family=BlueprintFamily.DATA,
        generation_reference="",
        generation_artifact_id="",
        blueprint_provenance_ref="",
        implementation_target="",
        dependency_chain=(),
        content_hash="c0ffee",
        provenance_metadata={},
        audit_metadata={},
        provenance_id="UCOS-GPRV-fake",
    )
    assert untraceable.is_traceable is False
    with pytest.raises(RequestProvenanceError):
        ProvenanceLedger().record(untraceable)


def test_ledger_fingerprint_deterministic():
    def build():
        ledger = ProvenanceLedger()
        ledger.record(_prov(request_ref="UCOS-GREQ-1"))
        return ledger

    assert build().fingerprint() == build().fingerprint()
