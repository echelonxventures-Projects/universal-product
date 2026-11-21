"""EC2-TASK-000099 — Blueprint classification façade tests (EC2-EPIC-006).

Covers the read-only L4 EC-1 classification façade: it binds to the certified
``engine.registry.read`` + ``engine.compiler.compile`` contract references and *records*
the EC-1 result (family, resolved, gap report) — it computes nothing. Also covers the
validity predicate, the gap report, and the append-only classification ledger.
"""

from __future__ import annotations

from platform.blueprints.classification import (
    CLASSIFICATION_CONTRACTS,
    COMPILER_CONTRACT,
    REGISTRY_CONTRACT,
    BlueprintClassification,
    ClassificationLedger,
    classify,
)
from platform.blueprints.contracts import BlueprintFamily
from platform.blueprints.errors import BlueprintClassificationError

import pytest


def test_classification_binds_certified_engine_contracts_by_reference():
    names = {ref.name for ref in CLASSIFICATION_CONTRACTS}
    assert names == {REGISTRY_CONTRACT, COMPILER_CONTRACT}
    assert REGISTRY_CONTRACT == "engine.registry.read"
    assert COMPILER_CONTRACT == "engine.compiler.compile"
    for ref in CLASSIFICATION_CONTRACTS:
        assert ref.version == "1.0.0"


def test_records_valid_classification():
    c = classify("UCOS-BLPR-1", BlueprintFamily.DATA)
    assert c.valid is True
    assert c.resolved is True
    assert c.defects == ()
    assert c.classification_id.startswith("UCOS-BCLS-")
    assert set(c.contracts) == {REGISTRY_CONTRACT, COMPILER_CONTRACT}
    assert c.gap_report()["valid"] is True


def test_records_invalid_classification_with_gap_report():
    c = classify("UCOS-BLPR-1", BlueprintFamily.API, resolved=True, defects=["missing-field"])
    assert c.valid is False
    assert c.gap_report()["defects"] == ["missing-field"]
    unresolved = classify("UCOS-BLPR-2", BlueprintFamily.API, resolved=False)
    assert unresolved.valid is False


def test_classification_is_deterministic():
    a = classify("UCOS-BLPR-1", BlueprintFamily.DATA)
    b = classify("UCOS-BLPR-1", BlueprintFamily.DATA)
    assert a.classification_id == b.classification_id
    assert a.fingerprint() == b.fingerprint()


@pytest.mark.parametrize(
    "kwargs",
    [
        {"blueprint_ref": ""},
        {"family": "data"},
        {"resolved": "yes"},
        {"defects": [""]},
    ],
)
def test_classification_rejects_malformed(kwargs):
    base = {"blueprint_ref": "UCOS-BLPR-1", "family": BlueprintFamily.DATA, "resolved": True}
    base.update(kwargs)
    with pytest.raises(BlueprintClassificationError):
        BlueprintClassification.create(**base)


def test_classification_to_dict():
    c = classify("UCOS-BLPR-1", BlueprintFamily.SERVICE)
    d = c.to_dict()
    assert d["family"] == "service"
    assert d["valid"] is True


# --------------------------------------------------------------------------- #
# Ledger                                                                       #
# --------------------------------------------------------------------------- #


def test_ledger_records_and_resolves():
    ledger = ClassificationLedger()
    c = classify("UCOS-BLPR-1", BlueprintFamily.DATA)
    assert ledger.record(c) is c
    assert "UCOS-BLPR-1" in ledger
    assert len(ledger) == 1
    assert ledger.get("UCOS-BLPR-1") is c
    assert ledger.blueprint_refs == ("UCOS-BLPR-1",)
    assert ledger.to_dict()["classification_count"] == 1
    assert isinstance(ledger.fingerprint(), str)


def test_ledger_record_is_idempotent_by_id():
    ledger = ClassificationLedger()
    c = classify("UCOS-BLPR-1", BlueprintFamily.DATA)
    ledger.record(c)
    assert ledger.record(classify("UCOS-BLPR-1", BlueprintFamily.DATA)) is c
    assert len(ledger) == 1


def test_ledger_rejects_conflicting_and_bad_records():
    ledger = ClassificationLedger()
    ledger.record(classify("UCOS-BLPR-1", BlueprintFamily.DATA))
    with pytest.raises(BlueprintClassificationError):
        ledger.record(classify("UCOS-BLPR-1", BlueprintFamily.EVENT))
    with pytest.raises(BlueprintClassificationError):
        ledger.record("nope")  # type: ignore[arg-type]
    with pytest.raises(BlueprintClassificationError):
        ledger.get("UCOS-BLPR-missing")
