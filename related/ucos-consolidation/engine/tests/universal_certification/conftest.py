"""Fixtures for the Universal Certification Engine test suite.

Drives the engine end to end against a **genuine** artifact for the validation
dimension: it assembles a real runtime unit from a published compiler package (reusing
the root ``published_package`` + ``runtime_signer`` fixtures), validates it through the
real Validation Layer (EPIC-007), builds the Validation Evidence, and projects both
into a :class:`ValidationInput`. The Measurement and Repository-Truth dimensions are
constructed as deterministic, decidable inputs — so certification is exercised over
real validation output plus controlled measurement/repository-truth attestations.
"""

from __future__ import annotations

import dataclasses

import pytest

from engine.universal_certification import (
    CertificationPipeline,
    Measurement,
    MeasurementComparator,
    MeasurementInput,
    RepositoryTruthInput,
    RuleSeverity,
    UniversalCertificationEngine,
    UniversalCertificationSubject,
    ValidationInput,
)


@pytest.fixture
def runtime_unit(published_package, runtime_signer):
    from engine.runtime import assemble

    return assemble(published_package, verify_with=runtime_signer)


@pytest.fixture
def valid_report(runtime_unit):
    from engine.validation import ValidationEngine
    from engine.validation.contracts import ValidationSubject

    subject = ValidationSubject.from_runtime_unit(runtime_unit, blueprint_class="BP-DATA")
    return ValidationEngine().validate(subject)


@pytest.fixture
def valid_evidence(valid_report):
    from engine.validation import build_validation_evidence

    return build_validation_evidence(valid_report)


@pytest.fixture
def artifact_version(runtime_unit) -> str:
    return runtime_unit.version


@pytest.fixture
def validation_input(valid_report, valid_evidence) -> ValidationInput:
    return ValidationInput.from_validation(valid_report, valid_evidence)


@pytest.fixture
def measurement_input() -> MeasurementInput:
    """A satisfied measurement set (blocking + advisory) built by real comparison."""
    return MeasurementInput.create(
        (
            Measurement.evaluate(
                metric_id="test-coverage",
                value=99.7,
                threshold=90.0,
                comparator=MeasurementComparator.GE,
                severity=RuleSeverity.BLOCKING,
                unit="percent",
            ),
            Measurement.evaluate(
                metric_id="lint-errors",
                value=0,
                threshold=0,
                comparator=MeasurementComparator.LE,
                severity=RuleSeverity.BLOCKING,
                unit="count",
            ),
            Measurement.evaluate(
                metric_id="doc-coverage",
                value=95.0,
                threshold=80.0,
                comparator=MeasurementComparator.GE,
                severity=RuleSeverity.ADVISORY,
                unit="percent",
            ),
        ),
        source="ucos-measurement-suite",
    )


@pytest.fixture
def repository_truth_input() -> RepositoryTruthInput:
    """A consistent repository-truth closure attestation (closed, homed, zero gaps)."""
    return RepositoryTruthInput.create(
        snapshot_id="UAKOS-CLOSURE-002",
        content_sha256="a" * 64,
        total_concepts=398,
        homed_concepts=398,
        gaps={
            "conversation_only": 0,
            "duplicate_canonical_homes": 0,
            "in_repo_unhomed": 0,
            "not_homed_concepts": 0,
            "orphan_concepts": 0,
            "ukda_content_hash_duplicates": 0,
            "upload_only": 0,
        },
        closed=True,
    )


@pytest.fixture
def subject(
    validation_input, measurement_input, repository_truth_input, artifact_version
) -> UniversalCertificationSubject:
    return UniversalCertificationSubject.create(
        validation=validation_input,
        measurement=measurement_input,
        repository_truth=repository_truth_input,
        version=artifact_version,
    )


@pytest.fixture
def engine() -> UniversalCertificationEngine:
    return UniversalCertificationEngine()


@pytest.fixture
def certified_decision(engine, subject):
    return engine.certify(subject)


@pytest.fixture
def pipeline() -> CertificationPipeline:
    return CertificationPipeline()


def mutate(obj, **changes):
    """Return a copy of a frozen dataclass with fields replaced (for negative tests)."""
    return dataclasses.replace(obj, **changes)


def broken_evidence(subject):
    """Return the subject with validation evidence removed (a not-certified case)."""
    validation = dataclasses.replace(subject.validation, evidence_present=False, evidence_sha256="")
    return dataclasses.replace(subject, validation=validation)


def shortfall_measurement():
    """A measurement input with a single unsatisfied blocking measurement."""
    return MeasurementInput.create(
        (
            Measurement.evaluate(
                metric_id="x",
                value=1,
                threshold=0,
                comparator=MeasurementComparator.LE,
            ),
        )
    )


def inconsistent_repository_truth():
    """A repository-truth attestation with an open gap (inconsistent)."""
    return RepositoryTruthInput.create(
        snapshot_id="s",
        content_sha256="h",
        total_concepts=10,
        homed_concepts=10,
        gaps={"x": 1},
        closed=True,
    )
