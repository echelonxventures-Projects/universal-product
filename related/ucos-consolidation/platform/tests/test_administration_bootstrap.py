"""EC2-CAP-ADMIN-001 — Administration bootstrap tests.

Covers composing the Administration Runtime onto a PlatformContext: contract
publication into the Foundation service registry (PL-05), cross-runtime health
integration into the Observability layer (G1/OP-C1), governed-action observability
(the bootstrap event + administrative actions captured by L8 audit — PC-16/OP-C3),
idempotency, and end-to-end determinism.
"""

from __future__ import annotations

from platform.administration.bootstrap import (
    ADMINISTRATION_BOOTSTRAP_EVENT,
    bootstrap_administration,
)
from platform.administration.contracts import ADMINISTRATION_CONTRACTS, AdministrativeScope
from platform.administration.health import CONFIGURATION_CHECK, INTEGRITY_CHECK
from platform.administration.service import AdministrationService
from platform.foundation.bootstrap import bootstrap_platform
from platform.foundation.identity import Principal, Role
from platform.identity.service import bootstrap_identity
from platform.observability.service import bootstrap_observability


def test_bootstrap_returns_service_and_publishes_contracts():
    context = bootstrap_platform()
    service = bootstrap_administration(context)
    assert isinstance(service, AdministrationService)
    for ref in ADMINISTRATION_CONTRACTS:
        assert ref.name in context.services


def test_bootstrap_registers_health_checks_into_observability():
    context = bootstrap_platform()
    obs = bootstrap_observability(context)
    bootstrap_administration(context, observability=obs)
    assert CONFIGURATION_CHECK in obs.health
    assert INTEGRITY_CHECK in obs.health


def test_bootstrap_emits_completion_event():
    context = bootstrap_platform()
    bootstrap_administration(context)
    assert len(context.events.events_of(ADMINISTRATION_BOOTSTRAP_EVENT)) == 1


def test_bootstrap_is_idempotent_on_contracts_and_health_checks():
    context = bootstrap_platform()
    obs = bootstrap_observability(context)
    auth = bootstrap_identity(context)
    bootstrap_administration(context, authorization=auth, observability=obs)
    # A second composition must not raise on duplicate contracts/health checks.
    bootstrap_administration(context, authorization=auth, observability=obs)
    for ref in ADMINISTRATION_CONTRACTS:
        assert ref.name in context.services


def test_administrative_actions_are_observed_as_governed_audit():
    context = bootstrap_platform()
    obs = bootstrap_observability(context)
    service = bootstrap_administration(context, observability=obs)
    admin = Principal.create("admin@x", [Role.PLATFORM_ADMINISTRATOR])
    session = service.authorization.establish_session(admin, issued_at=0, ttl=1000)
    before = obs.audit.verify()
    service.set_configuration(session.session_id, AdministrativeScope.PLATFORM, "flag", "on", now=1)
    # The configuration change and its access evaluation are captured by L8 audit.
    assert before is True
    assert obs.audit.verify() is True
    assert obs.governed_action_count >= 2


def test_bootstrap_is_deterministic_end_to_end():
    def run() -> str:
        context = bootstrap_platform()
        service = bootstrap_administration(context)
        admin = Principal.create("admin@x", [Role.PLATFORM_ADMINISTRATOR])
        session = service.authorization.establish_session(admin, issued_at=0, ttl=1000)
        service.set_configuration(session.session_id, AdministrativeScope.PLATFORM, "k", "v", now=1)
        return service.evidence().fingerprint()

    assert run() == run()
