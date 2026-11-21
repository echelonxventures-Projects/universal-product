"""EPIC-VAL-003 — Unified Governance Evidence tests."""

from __future__ import annotations

import dataclasses

from engine.governance.evidence import EVIDENCE_FORMAT


def test_governance_evidence_format(governed_report):
    assert governed_report.governance_evidence.to_dict()["evidence_format"] == EVIDENCE_FORMAT


def test_governance_evidence_embeds_every_stage(governed_report):
    evidence = governed_report.governance_evidence
    n = len(governed_report.units)
    assert len(evidence.validation_evidence) == n
    assert len(evidence.certification_evidence) == n
    assert evidence.acceptance_evidence["accepted"] is True
    assert evidence.ledger["count"] == n
    assert evidence.counts == {"units": n, "validated": n, "certified": n}


def test_governance_evidence_refs_match_content(governed_report):
    """Each embedded evidence record hashes to its declared reference (traceable)."""
    from engine.governance.contracts import content_hash

    evidence = governed_report.governance_evidence
    for record, ref in zip(
        evidence.validation_evidence, evidence.validation_evidence_refs, strict=True
    ):
        assert content_hash(record) == ref


def test_governance_evidence_is_deterministic(valid_input):
    from engine.governance.pipeline import RepositoryGovernancePipeline

    a = RepositoryGovernancePipeline().govern(valid_input).governance_evidence
    b = RepositoryGovernancePipeline().govern(valid_input).governance_evidence
    assert a.evidence_sha256 == b.evidence_sha256
    assert a.to_dict() == b.to_dict()


def test_governance_evidence_detects_mutation(governed_report):
    evidence = governed_report.governance_evidence
    assert evidence.verify_integrity() is True
    tampered = dataclasses.replace(evidence, repository_id="OTHER")
    assert tampered.verify_integrity() is False
