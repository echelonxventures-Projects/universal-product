"""EC2-CAP-SEC-001 / SEC-CLASS — bootstrap composition tests.

Covers :func:`bootstrap_security_classification`: composition onto a
:class:`PlatformContext`, reuse of the certified L7 seam, publication of the SEC-CLASS
contracts into the service registry, governed bootstrap-event emission, idempotency,
and fail-closed behavior.
"""

from __future__ import annotations

from platform.foundation.bootstrap import bootstrap_platform
from platform.identity.service import build_authorization_service
from platform.security.bootstrap import (
    SECURITY_CLASSIFICATION_BOOTSTRAP_EVENT,
    bootstrap_security_classification,
)
from platform.security.contracts import (
    SECURITY_CLASSIFICATION_CONTRACTS,
    ClassificationKind,
    SubjectLayer,
)
from platform.security.errors import SecurityBootstrapError
from platform.security.service import SecurityClassificationService

import pytest


def test_bootstrap_composes_the_runtime_and_binds_the_seam():
    context = bootstrap_platform()
    service = bootstrap_security_classification(context)
    assert isinstance(service, SecurityClassificationService)
    assert service.authorization_bound is True


def test_bootstrap_publishes_the_classification_contracts():
    context = bootstrap_platform()
    bootstrap_security_classification(context)
    for ref in SECURITY_CLASSIFICATION_CONTRACTS:
        assert ref.name in context.services


def test_bootstrap_emits_a_completion_event():
    context = bootstrap_platform()
    bootstrap_security_classification(context)
    events = context.events.events_of(SECURITY_CLASSIFICATION_BOOTSTRAP_EVENT)
    assert len(events) == 1
    payload = events[0].payload
    assert payload["authorization_bound"] is True
    assert set(payload["classification_contracts"]) == {
        r.name for r in SECURITY_CLASSIFICATION_CONTRACTS
    }


def test_bootstrap_accepts_a_prebuilt_authorization_seam():
    context = bootstrap_platform()
    authz = build_authorization_service(events=context.events)
    service = bootstrap_security_classification(context, authorization=authz)
    assert service.authorization_bound is True


def test_bootstrap_is_idempotent_on_contract_registration():
    context = bootstrap_platform()
    authz = build_authorization_service(events=context.events)
    bootstrap_security_classification(context, authorization=authz)
    # A second bootstrap must not raise on duplicate contract registration.
    bootstrap_security_classification(context, authorization=authz)
    for ref in SECURITY_CLASSIFICATION_CONTRACTS:
        assert ref.name in context.services


def test_bootstrapped_service_records_end_to_end():
    context = bootstrap_platform()
    service = bootstrap_security_classification(context)
    c = service.classify(
        ClassificationKind.CONFIDENTIALITY, SubjectLayer.DATA, "UCOS-DATA-000001", "restricted"
    )
    assert c.classification_id in service.ledger


def test_bootstrap_is_fail_closed_on_bad_context():
    class _BadContext:
        # Missing .events / .services / .program_id — bootstrap must fail-closed.
        pass

    with pytest.raises(SecurityBootstrapError):
        bootstrap_security_classification(_BadContext())


def test_bootstrap_reraises_a_security_bootstrap_error_without_double_wrapping(monkeypatch):
    import platform.security.bootstrap as boot

    sentinel = SecurityBootstrapError("inner seam failure")

    def _raise(_context):
        raise sentinel

    monkeypatch.setattr(boot, "bootstrap_identity", _raise, raising=True)
    context = bootstrap_platform()
    with pytest.raises(SecurityBootstrapError) as excinfo:
        bootstrap_security_classification(context)
    assert excinfo.value is sentinel
