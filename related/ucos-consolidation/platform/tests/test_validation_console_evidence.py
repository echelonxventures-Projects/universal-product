"""EC2-TASK-000148 — Validation console runtime-evidence tests (EC2-EPIC-010).

Covers the deterministic, content-addressed console runtime evidence value type
(distinct from the per-target EC-1 validation evidence it surfaces).
"""

from __future__ import annotations

from platform.validation.evidence import ValidationConsoleEvidence


def _evidence(**kw):
    base = dict(
        registry_fingerprint="rf",
        record_count=2,
        accepted_count=1,
        rejected_count=1,
        inspection_count=3,
        access_evaluation_count=4,
        verdict_census=(("accepted", 1), ("rejected", 1), ("total", 2)),
        health_status="healthy",
    )
    base.update(kw)
    return ValidationConsoleEvidence.create(**base)


def test_evidence_is_content_addressed_and_serializable():
    ev = _evidence()
    assert ev.evidence_id.startswith("UCOS-VEVD-")
    d = ev.to_dict()
    assert d["record_count"] == 2
    assert d["verdict_census"] == {"accepted": 1, "rejected": 1, "total": 2}
    assert d["health_status"] == "healthy"


def test_evidence_is_deterministic():
    assert _evidence().evidence_id == _evidence().evidence_id
    assert _evidence().fingerprint() == _evidence().fingerprint()


def test_evidence_changes_with_state():
    assert _evidence().evidence_id != _evidence(record_count=5).evidence_id
