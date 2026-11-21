"""EC2-TASK-000155 — Certification console EC-1 façade tests (EC2-EPIC-011).

Covers the read-only L4 façade that consumes ``engine.certification`` by reference:
contract binding, read-only reproduction over the upstream validation output, the
surfaced bundle, and the machine-checkable fidelity predicate (byte-for-byte equality
with a fresh certified reproduction, P6).
"""

from __future__ import annotations

from platform.certification.contracts import ENGINE_CERTIFICATION_CONTRACT
from platform.certification.errors import CertificationFidelityError
from platform.certification.facade import (
    CERTIFICATION_ENGINE_CONTRACTS,
    CertificationFacade,
    SurfacedCertification,
)
from platform.foundation.contracts import ENGINE_CONTRACTS, content_hash
from platform.tests.certification_console_helpers import (
    VERSION,
    certified_output,
    not_certified_output,
)

import pytest

from engine.certification.engine import CertificationEngine


def test_facade_binds_engine_certification_contract_by_reference():
    facade = CertificationFacade()
    assert facade.engine_contract == ENGINE_CERTIFICATION_CONTRACT
    assert CERTIFICATION_ENGINE_CONTRACTS
    assert all(ref.name == ENGINE_CERTIFICATION_CONTRACT for ref in CERTIFICATION_ENGINE_CONTRACTS)
    assert CERTIFICATION_ENGINE_CONTRACTS[0] in ENGINE_CONTRACTS


def test_facade_criterion_ids_are_the_certified_suite():
    facade = CertificationFacade()
    assert facade.criterion_ids() == CertificationEngine().criterion_ids
    assert facade.engine_contracts == CERTIFICATION_ENGINE_CONTRACTS


def test_facade_rejects_non_engine():
    with pytest.raises(CertificationFidelityError):
        CertificationFacade(engine="nope")  # type: ignore[arg-type]


def test_facade_accepts_explicit_engine():
    facade = CertificationFacade(engine=CertificationEngine())
    assert facade.criterion_ids()


def test_surface_reproduces_certified_outputs():
    facade = CertificationFacade()
    report, evidence = certified_output()
    surfaced = facade.surface(report, evidence, version=VERSION)
    assert isinstance(surfaced, SurfacedCertification)
    assert surfaced.engine_contract == ENGINE_CERTIFICATION_CONTRACT
    expected = facade.reproduce(report, evidence, version=VERSION)
    assert content_hash(surfaced.record.to_dict()) == content_hash(expected.record.to_dict())
    assert surfaced.record_fingerprint() == expected.record.content_sha256
    assert surfaced.to_dict()["record"]["status"] == "certified"
    assert surfaced.decision.certified is True
    assert surfaced.version == VERSION


def test_reproduce_rejects_bad_report_and_evidence():
    facade = CertificationFacade()
    report, evidence = certified_output()
    with pytest.raises(CertificationFidelityError):
        facade.reproduce("nope", evidence, version=VERSION)  # type: ignore[arg-type]
    with pytest.raises(CertificationFidelityError):
        facade.reproduce(report, "nope", version=VERSION)  # type: ignore[arg-type]


def test_verify_fidelity_true_for_matching_record():
    facade = CertificationFacade()
    report, evidence = certified_output()
    decision = facade.reproduce(report, evidence, version=VERSION)
    assert facade.verify_fidelity(decision.record, report, evidence, version=VERSION) is True


def test_verify_fidelity_false_when_output_diverges():
    facade = CertificationFacade()
    certified_report, certified_ev = certified_output()
    decision = facade.reproduce(certified_report, certified_ev, version=VERSION)
    # Verify the certified record against different (not-certified) validation output.
    other_report, other_ev = not_certified_output()
    assert facade.verify_fidelity(decision.record, other_report, other_ev, version=VERSION) is False


def test_verify_fidelity_rejects_bad_record():
    facade = CertificationFacade()
    report, evidence = certified_output()
    with pytest.raises(CertificationFidelityError):
        facade.verify_fidelity("nope", report, evidence, version=VERSION)  # type: ignore[arg-type]
