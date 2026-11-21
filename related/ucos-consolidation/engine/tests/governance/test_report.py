"""EPIC-VAL-003 — Repository Governance Report tests."""

from __future__ import annotations

import dataclasses

import pytest

from engine.governance.errors import GovernanceIntegrityError
from engine.governance.report import REPORT_FORMAT


def test_report_bundles_every_unified_artifact(governed_report):
    d = governed_report.to_dict()
    assert d["report_format"] == REPORT_FORMAT
    assert d["governed"] is True
    for key in (
        "repository_decision",
        "repository_acceptance",
        "repository_certificate",
        "repository_readiness",
        "governance_evidence",
        "freeze_recommendation",
        "ledger",
        "units",
    ):
        assert key in d
    assert d["authority"] == "ENGINEERING-EXECUTION-ONLY"


def test_governed_unit_to_dict(governed_report):
    unit = governed_report.units[0]
    d = unit.to_dict()
    assert d["validated"] is True
    assert d["certified"] is True
    assert d["validation_report"]["verdict"] == "pass"
    assert d["certification_decision"]["certified"] is True
    assert d["ledger_entry"]["sequence"] == 0


def test_report_root_hash_binds_subordinate_artifacts(governed_report):
    assert governed_report.verify_integrity() is True
    # Recomputing yields the stored root hash.
    assert governed_report.recompute_hash() == governed_report.governance_sha256


def test_report_detects_mutation(governed_report):
    tampered = dataclasses.replace(governed_report, repository_id="OTHER")
    assert tampered.verify_integrity() is False
    with pytest.raises(GovernanceIntegrityError) as exc:
        tampered.require_integrity()
    assert exc.value.context["repository_id"] == "OTHER"


def test_report_require_integrity_passes_when_intact(governed_report):
    # Does not raise.
    assert governed_report.require_integrity() is None
