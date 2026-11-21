"""EC2-TASK-000147 — Validation console EC-1 façade tests (EC2-EPIC-010).

Covers the read-only L4 façade that consumes ``engine.validation`` by reference:
contract binding, read-only reproduction, the surfaced bundle, and the machine-checkable
fidelity predicate (byte-for-byte equality with a fresh certified reproduction, P6).
"""

from __future__ import annotations

from platform.foundation.contracts import ENGINE_CONTRACTS, content_hash
from platform.tests.validation_console_helpers import accepted_subject, rejected_subject
from platform.validation.contracts import ENGINE_VALIDATION_CONTRACT
from platform.validation.errors import ValidationFidelityError
from platform.validation.facade import (
    VALIDATION_ENGINE_CONTRACTS,
    SurfacedValidation,
    ValidationFacade,
)

import pytest

from engine.validation.executor import ValidationEngine


def test_facade_binds_engine_validation_contract_by_reference():
    facade = ValidationFacade()
    assert facade.engine_contract == ENGINE_VALIDATION_CONTRACT
    assert VALIDATION_ENGINE_CONTRACTS
    assert all(ref.name == ENGINE_VALIDATION_CONTRACT for ref in VALIDATION_ENGINE_CONTRACTS)
    # The contract reference is the certified one already published in ENGINE_CONTRACTS.
    assert VALIDATION_ENGINE_CONTRACTS[0] in ENGINE_CONTRACTS


def test_facade_check_ids_are_the_certified_suite():
    facade = ValidationFacade()
    assert facade.check_ids() == ValidationEngine().check_ids
    assert facade.engine_contracts == VALIDATION_ENGINE_CONTRACTS


def test_facade_rejects_non_engine():
    with pytest.raises(ValidationFidelityError):
        ValidationFacade(engine="nope")  # type: ignore[arg-type]


def test_facade_accepts_explicit_engine():
    facade = ValidationFacade(engine=ValidationEngine())
    assert facade.check_ids()


def test_surface_reproduces_certified_outputs():
    facade = ValidationFacade()
    subject = accepted_subject()
    surfaced = facade.surface(subject)
    assert isinstance(surfaced, SurfacedValidation)
    assert surfaced.engine_contract == ENGINE_VALIDATION_CONTRACT
    # byte-for-byte equal to a direct engine run (fidelity mechanism, P6)
    expected = ValidationEngine().validate(subject)
    assert content_hash(surfaced.report.to_dict()) == content_hash(expected.to_dict())
    assert surfaced.report_fingerprint() == content_hash(expected.to_dict())
    assert surfaced.to_dict()["report"]["verdict"] == "pass"


def test_reproduce_rejects_bad_subject():
    facade = ValidationFacade()
    with pytest.raises(ValidationFidelityError):
        facade.reproduce("nope")  # type: ignore[arg-type]


def test_verify_fidelity_true_for_matching_report_and_subject():
    facade = ValidationFacade()
    subject = rejected_subject()
    report = facade.reproduce(subject)
    assert facade.verify_fidelity(report, subject) is True


def test_verify_fidelity_false_when_report_and_subject_diverge():
    facade = ValidationFacade()
    accepted = accepted_subject()
    # Report produced for the accepted subject; verify against a different (rejected)
    # subject with a *different* target — reproduction diverges → infidelic.
    report = facade.reproduce(accepted)
    assert facade.verify_fidelity(report, rejected_subject()) is False


def test_verify_fidelity_rejects_bad_report():
    facade = ValidationFacade()
    with pytest.raises(ValidationFidelityError):
        facade.verify_fidelity("nope", accepted_subject())  # type: ignore[arg-type]
