"""EC2-CAP-SEC-001 / SEC-CLASS — governance validation tests.

Asserts the constitutional/governance invariants the mission mandates: authority
neutrality (no authorize/ratify/enact/govern/override operation), record-only
discipline (append-only, non-mutating), non-enforcement, secret-freedom (SEC-04/RR-07),
and no duplication of the certified L7 authorization decision.
"""

from __future__ import annotations

from platform.foundation.events import EventBus
from platform.foundation.identity import Permission
from platform.identity.contracts import CapabilityGroup
from platform.security import service as service_module
from platform.security.classification import ClassificationLedger, SecurityClassification
from platform.security.contracts import (
    ClassificationKind,
    EnforcementReference,
    SubjectLayer,
)
from platform.security.service import build_security_classification_service

#: Verbs SEC-CLASS must never expose (record-only, authority-neutral).
_FORBIDDEN_OPERATIONS = (
    "authorize",
    "authorize_principal",
    "ratify",
    "enact",
    "grant",
    "govern",
    "override",
    "escalate",
    "deny",
    "permit",
    "revoke",
)


def test_service_exposes_no_authority_operation():
    service = build_security_classification_service()
    for verb in _FORBIDDEN_OPERATIONS:
        assert not hasattr(service, verb), f"SEC-CLASS must not expose '{verb}'"


def test_classification_exposes_no_authority_operation():
    c = SecurityClassification.create(
        ClassificationKind.CONFIDENTIALITY, SubjectLayer.DATA, "UCOS-DATA-000001", "restricted"
    )
    for verb in _FORBIDDEN_OPERATIONS:
        assert not hasattr(c, verb)


def test_ledger_exposes_no_mutation_beyond_append():
    ledger = ClassificationLedger()
    for verb in ("delete", "remove", "update", "mutate", "clear", "pop", "override"):
        assert not hasattr(ledger, verb)


def test_every_classification_is_non_enforcing():
    service = build_security_classification_service()
    service.classify(
        ClassificationKind.AUTHORIZATION,
        SubjectLayer.SERVICE,
        "UCOS-SVC-000001",
        "required",
        enforcement_ref=EnforcementReference.create(
            CapabilityGroup.GENERATION_REQUESTS, Permission.EXECUTE
        ),
    )
    for c in service.ledger.classifications:
        assert c.non_enforcing is True
        assert c.classify()["enforced"] is False


def test_enforcement_reference_records_but_never_enacts():
    # The reference names the L7 seam but the recorded resolution enacts nothing.
    service = build_security_classification_service()
    resolution = service.resolve_enforcement_reference(
        EnforcementReference.create(CapabilityGroup.ADMINISTRATION_POLICY, Permission.ADMINISTER)
    )
    assert resolution["enacts"] is False
    assert resolution["seam"] == "platform.identity.AuthorizationService"


def test_governed_event_payload_declares_non_enactment():
    bus = EventBus()
    service = build_security_classification_service(events=bus)
    service.classify(
        ClassificationKind.CONFIDENTIALITY, SubjectLayer.DATA, "UCOS-DATA-000002", "restricted"
    )
    event = bus.events_of(service_module.CLASSIFICATION_RECORDED_EVENT)[0]
    assert event.payload["enacts"] is False


def test_service_never_calls_authorize_on_the_seam(monkeypatch):
    # Bind a real authorization seam, then make its decision methods explode if touched.
    from platform.identity.service import AuthorizationService, build_authorization_service

    authz = build_authorization_service()

    def _boom(*args, **kwargs):  # pragma: no cover - must never be invoked
        raise AssertionError("SEC-CLASS must never invoke an authorization decision")

    monkeypatch.setattr(AuthorizationService, "authorize", _boom, raising=True)
    monkeypatch.setattr(AuthorizationService, "authorize_principal", _boom, raising=True)

    service = build_security_classification_service(authorization=authz)
    # A full L7-bound classification flow must complete without any authorize call.
    service.classify(
        ClassificationKind.AUTHORIZATION,
        SubjectLayer.APPLICATION,
        "UCOS-APP-000001",
        "required",
        enforcement_ref=EnforcementReference.create(
            CapabilityGroup.GENERATION_REQUESTS, Permission.EXECUTE
        ),
    )


def test_no_secret_value_is_stored_anywhere():
    # SEC-04/RR-07: the classification records references and labels only, never secrets.
    service = build_security_classification_service()
    c = service.classify(
        ClassificationKind.CONFIDENTIALITY, SubjectLayer.DATA, "UCOS-DATA-000003", "restricted"
    )
    serialized = str(c.to_dict())
    for token in ("password", "secret", "token", "apikey", "api_key", "private_key"):
        assert token not in serialized.lower()
