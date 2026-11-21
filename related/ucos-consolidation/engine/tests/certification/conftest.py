"""Fixtures for the Certification Layer test suite.

Drives the layer end to end against a **genuine** artifact: it assembles a real
runtime unit from a published compiler package (reusing the root ``published_package``
+ ``runtime_signer`` fixtures), validates it through the real Validation Layer
(EPIC-007), builds the Validation Evidence, and projects both into a certification
subject — so certification is exercised over real validation output, never a
hand-built stand-in.
"""

from __future__ import annotations

import dataclasses

import pytest

from engine.certification.contracts import CertificationSubject
from engine.certification.engine import CertificationEngine
from engine.runtime import assemble
from engine.validation import ValidationEngine, build_validation_evidence


@pytest.fixture
def runtime_unit(published_package, runtime_signer):
    return assemble(published_package, verify_with=runtime_signer)


@pytest.fixture
def valid_report(runtime_unit):
    from engine.validation.contracts import ValidationSubject

    subject = ValidationSubject.from_runtime_unit(runtime_unit, blueprint_class="BP-DATA")
    return ValidationEngine().validate(subject)


@pytest.fixture
def valid_evidence(valid_report):
    return build_validation_evidence(valid_report)


@pytest.fixture
def artifact_version(runtime_unit) -> str:
    return runtime_unit.version


@pytest.fixture
def valid_subject(valid_report, valid_evidence, artifact_version) -> CertificationSubject:
    return CertificationSubject.from_validation(
        valid_report, valid_evidence, version=artifact_version
    )


@pytest.fixture
def certified_decision(valid_subject):
    return CertificationEngine().certify(valid_subject)


def mutate(subject: CertificationSubject, **changes) -> CertificationSubject:
    """Return a copy of ``subject`` with fields replaced (for negative tests)."""
    return dataclasses.replace(subject, **changes)
