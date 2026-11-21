"""Provider Certification tests (Terminal-04).

Certification must be *sound*: it may attest only what validation substantiated, and
it may never confer authority that evidence does not support. The tests therefore
concentrate on the soundness refusals and on the tier→authority mapping.
"""

from __future__ import annotations

from dataclasses import replace
from platform.tests.universal_provider_helpers import MemoProvider, memo_descriptor
from platform.universal_provider.certification import (
    SEAL_LENGTH,
    CertificationLedger,
    CertificationTier,
    ProviderCertificate,
    ProviderCertifier,
    tier_for,
)
from platform.universal_provider.errors import ProviderCertificationError
from platform.universal_provider.lifecycle import GENESIS_HASH, ProviderLifecycle, ProviderPhase
from platform.universal_provider.registry import ProviderRegistry
from platform.universal_provider.validation import (
    ProviderValidator,
    ValidationReport,
    ValidationSubject,
)

import pytest


def _governed_subject(descriptor=None) -> ValidationSubject:
    descriptor = descriptor or memo_descriptor()
    registry = ProviderRegistry.from_descriptors([descriptor])
    lifecycle = ProviderLifecycle()
    lifecycle.declare(descriptor.qualified_id)
    lifecycle.transition(descriptor.qualified_id, ProviderPhase.REGISTERED)
    return ValidationSubject(
        descriptor=descriptor,
        instance=MemoProvider(descriptor),
        registry=registry,
        lifecycle=lifecycle,
    )


def _passing_report(descriptor=None) -> tuple[object, ValidationReport]:
    subject = _governed_subject(descriptor)
    return subject.descriptor, ProviderValidator().validate(subject)


def _incomplete_report():
    descriptor = memo_descriptor(entry_point="")
    registry = ProviderRegistry.from_descriptors([descriptor])
    lifecycle = ProviderLifecycle()
    lifecycle.declare(descriptor.qualified_id)
    lifecycle.transition(descriptor.qualified_id, ProviderPhase.REGISTERED)
    subject = ValidationSubject(descriptor=descriptor, registry=registry, lifecycle=lifecycle)
    return descriptor, ProviderValidator().validate(subject)


def test_a_fully_evidenced_provider_certifies_universal_and_may_serve() -> None:
    descriptor, report = _passing_report()
    certificate = ProviderCertifier().certify(descriptor, report)
    assert certificate.tier is CertificationTier.UNIVERSAL
    assert certificate.authorizes_activation is True
    assert certificate.gates_passed == 14
    assert certificate.gates_failed == 0
    assert certificate.gates_indeterminate == 0
    assert certificate.findings == ()
    assert len(certificate.seal) == SEAL_LENGTH
    assert certificate.certificate_id.startswith(certificate.seal)


def test_incomplete_evidence_certifies_provisional_and_authorizes_nothing() -> None:
    descriptor, report = _incomplete_report()
    certificate = ProviderCertifier().certify(descriptor, report)
    assert certificate.tier is CertificationTier.PROVISIONAL
    assert certificate.authorizes_activation is False
    assert certificate.gates_indeterminate > 0
    assert certificate.gates_failed == 0
    assert any("indeterminate" in finding for finding in certificate.findings)


def test_a_blocking_failure_is_refused_certification() -> None:
    descriptor = memo_descriptor(source_of_record="", entry_point="")
    report = ProviderValidator().validate(ValidationSubject(descriptor=descriptor))
    certificate = ProviderCertifier().certify(descriptor, report)
    assert certificate.tier is CertificationTier.REFUSED
    assert certificate.authorizes_activation is False
    assert certificate.gates_failed > 0


def test_tier_for_maps_each_validation_status() -> None:
    _, passing = _passing_report()
    _, incomplete = _incomplete_report()
    assert tier_for(passing) is CertificationTier.UNIVERSAL
    assert tier_for(incomplete) is CertificationTier.PROVISIONAL


def test_certification_is_reproducible() -> None:
    descriptor, report = _passing_report()
    first = ProviderCertifier().certify(descriptor, report)
    descriptor_again, report_again = _passing_report()
    second = ProviderCertifier().certify(descriptor_again, report_again)
    assert first.certificate_id == second.certificate_id
    assert first.to_dict() == second.to_dict()


def test_the_certificate_pins_the_constitution_it_was_measured_against() -> None:
    descriptor, report = _passing_report()
    certificate = ProviderCertifier().certify(descriptor, report, constitution_hash="abc123")
    assert certificate.constitution_hash == "abc123"
    assert certificate.constitution_id == "UCOS-PROVIDER-CONSTITUTION"
    without = ProviderCertifier().certify(descriptor, report)
    assert without.certificate_id != certificate.certificate_id


def test_certification_refuses_a_report_about_another_provider() -> None:
    descriptor, report = _passing_report()
    other = memo_descriptor(provider_id="fixture.other")
    with pytest.raises(ProviderCertificationError) as exc:
        ProviderCertifier().certify(other, report)
    assert exc.value.detail["report_subject"] == descriptor.qualified_id


def test_certification_refuses_a_report_computed_over_another_revision() -> None:
    descriptor, report = _passing_report()
    drifted = memo_descriptor(source_of_record="a substrate nobody measured")
    with pytest.raises(ProviderCertificationError) as exc:
        ProviderCertifier().certify(drifted, report)
    assert "different descriptor revision" in exc.value.message
    assert descriptor.qualified_id == drifted.qualified_id


def test_certification_refuses_an_empty_validation_pass() -> None:
    descriptor = memo_descriptor()
    empty = ValidationReport(
        qualified_id=descriptor.qualified_id,
        descriptor_hash=descriptor.content_hash(),
        constitution_id="UCOS-PROVIDER-CONSTITUTION",
        constitution_version="1.0.0",
    )
    with pytest.raises(ProviderCertificationError) as exc:
        ProviderCertifier().certify(descriptor, empty)
    assert "PC-11" in exc.value.message


def test_certification_refuses_wrongly_typed_inputs() -> None:
    descriptor, report = _passing_report()
    with pytest.raises(ProviderCertificationError):
        ProviderCertifier().certify("nope", report)  # type: ignore[arg-type]
    with pytest.raises(ProviderCertificationError):
        ProviderCertifier().certify(descriptor, "nope")  # type: ignore[arg-type]


def test_the_ledger_is_append_only_and_hash_chained() -> None:
    certifier = ProviderCertifier()
    descriptor, report = _passing_report()
    other_descriptor, other_report = _passing_report(memo_descriptor(provider_id="fixture.other"))
    certifier.certify(descriptor, report)
    certifier.certify(other_descriptor, other_report)
    ledger = certifier.ledger
    assert len(ledger) == 2
    assert ledger.entries[0].previous_hash == GENESIS_HASH
    assert ledger.entries[1].previous_hash == ledger.entries[0].entry_hash
    assert ledger.head_hash == ledger.entries[-1].entry_hash
    assert ledger.verify() is True
    ledger.require_intact()
    assert ledger.entries[0].recompute_hash() == ledger.entries[0].entry_hash
    assert len(ledger.certificates()) == 2
    assert ledger.to_dict()["count"] == 2
    assert ledger.ledger_hash() == ledger.ledger_hash()


def test_the_ledger_detects_tampering_and_resequencing() -> None:
    certifier = ProviderCertifier()
    descriptor, report = _passing_report()
    certifier.certify(descriptor, report)
    ledger = certifier.ledger
    original = ledger.entries[0]
    tampered = original.__class__(
        sequence=original.sequence,
        certificate=ProviderCertificate(
            qualified_id=original.certificate.qualified_id,
            descriptor_hash=original.certificate.descriptor_hash,
            report_hash=original.certificate.report_hash,
            tier=CertificationTier.UNIVERSAL,
            gates_total=1,
            gates_passed=1,
            gates_failed=0,
            gates_indeterminate=0,
        ),
        previous_hash=original.previous_hash,
        entry_hash=original.entry_hash,
    )
    ledger._entries[0] = tampered  # noqa: SLF001 - tamper simulation
    assert ledger.verify() is False
    with pytest.raises(ProviderCertificationError):
        ledger.require_intact()


def test_an_empty_ledger_is_well_formed() -> None:
    ledger = CertificationLedger()
    assert len(ledger) == 0
    assert ledger.head_hash == GENESIS_HASH
    assert ledger.verify() is True
    assert ledger.latest("absent@1.0.0") is None
    with pytest.raises(ProviderCertificationError):
        ledger.append("not a certificate")  # type: ignore[arg-type]


def test_latest_returns_the_most_recent_certification_for_a_provider() -> None:
    certifier = ProviderCertifier()
    descriptor, report = _passing_report()
    assert certifier.latest(descriptor.qualified_id) is None
    assert certifier.authorizes_activation(descriptor.qualified_id) is False
    certifier.certify(descriptor, report)
    certifier.certify(descriptor, report)
    assert len(certifier.ledger) == 2
    assert certifier.latest(descriptor.qualified_id) is not None
    assert certifier.authorizes_activation(descriptor.qualified_id) is True


def test_a_provisional_certificate_never_authorizes_activation() -> None:
    certifier = ProviderCertifier()
    descriptor, report = _incomplete_report()
    certifier.certify(descriptor, report)
    assert certifier.authorizes_activation(descriptor.qualified_id) is False


def test_the_certificate_summary_is_the_corpus_idiomatic_one_liner() -> None:
    descriptor, report = _passing_report()
    summary = ProviderCertifier().certify(descriptor, report).summary()
    assert "CERTIFIED-UNIVERSAL" in summary
    assert "gates=14/14 PASS" in summary
    assert "blocking=none" in summary
    assert "seal=" in summary


def test_a_ledger_whose_sequence_or_link_is_wrong_does_not_verify() -> None:
    """THREE WAYS A CHAIN BREAKS, and only the third had a test.

    A wrong sequence is an entry out of order; a wrong previous-hash is a splice; a wrong
    entry hash is an edit in place. The first two are checked together because both are
    facts about an entry's POSITION rather than its content — and an entry whose own hash
    still recomputes correctly would pass the third check while sitting in the wrong place.
    """
    certifier = ProviderCertifier()
    descriptor, report = _passing_report()
    certifier.certify(descriptor, report)
    certifier.certify(descriptor, report)
    ledger = certifier.ledger
    assert ledger.verify() is True

    entries = ledger._entries  # noqa: SLF001 - deliberate corruption
    genuine = entries[1]

    entries[1] = replace(genuine, sequence=99)
    assert ledger.verify() is False

    entries[1] = replace(genuine, previous_hash="0" * 64)
    assert ledger.verify() is False

    entries[1] = genuine
    assert ledger.verify() is True


def test_the_ledger_answers_for_a_provider_it_has_certified_and_one_it_has_not() -> None:
    """``latest`` walks backwards so the most recent certification wins, and only its
    "nothing found" arm had run. A lookup whose success path is unexercised is one that could
    return the WRONG entry — an earlier certification for the same provider, or another
    provider's — and every consumer reading a tier would read it from that."""
    certifier = ProviderCertifier()
    descriptor, report = _passing_report()
    certifier.certify(descriptor, report)
    certifier.certify(descriptor, report)
    ledger = certifier.ledger

    found = ledger.latest(descriptor.qualified_id)
    assert found is ledger._entries[-1]  # noqa: SLF001 - the most recent entry wins
    assert found is not ledger._entries[0]  # noqa: SLF001
    assert ledger.latest("fixture.never-certified@1.0.0") is None
    assert len(ledger.certificates()) == 2
