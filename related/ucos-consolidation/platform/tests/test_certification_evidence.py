"""EC2-TASK-000157 — Certification console runtime-evidence tests (EC2-EPIC-011).

Covers the deterministic, content-addressed console runtime evidence value type
(distinct from the per-target EC-1 certification evidence it surfaces).
"""

from __future__ import annotations

from platform.certification.evidence import CertificationConsoleEvidence


def _evidence(**kw):
    base = dict(
        registry_fingerprint="rf",
        ledger_fingerprint="lf",
        record_count=2,
        certified_count=1,
        not_certified_count=1,
        ledger_entry_count=2,
        ledger_intact=True,
        inspection_count=3,
        access_evaluation_count=4,
        status_census=(("certified", 1), ("not_certified", 1), ("total", 2)),
        health_status="healthy",
    )
    base.update(kw)
    return CertificationConsoleEvidence.create(**base)


def test_evidence_is_content_addressed_and_serializable():
    ev = _evidence()
    assert ev.evidence_id.startswith("UCOS-CEVD-")
    d = ev.to_dict()
    assert d["record_count"] == 2
    assert d["ledger_entry_count"] == 2
    assert d["ledger_intact"] is True
    assert d["status_census"] == {"certified": 1, "not_certified": 1, "total": 2}
    assert d["health_status"] == "healthy"


def test_evidence_is_deterministic():
    assert _evidence().evidence_id == _evidence().evidence_id
    assert _evidence().fingerprint() == _evidence().fingerprint()


def test_evidence_changes_with_state():
    assert _evidence().evidence_id != _evidence(record_count=5).evidence_id
    assert _evidence().evidence_id != _evidence(ledger_intact=False).evidence_id
