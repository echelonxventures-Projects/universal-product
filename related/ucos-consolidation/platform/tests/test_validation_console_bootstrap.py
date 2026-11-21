"""EC2-TASK-000152 — Validation console bootstrap tests (EC2-EPIC-010).

Covers composition onto a PlatformContext: identity/observability reuse, health-check
registration, contract publication into the service registry, the bootstrap event,
idempotence, and an end-to-end surface through the bootstrapped service.
"""

from __future__ import annotations

from platform.foundation.bootstrap import bootstrap_platform
from platform.foundation.identity import Principal, Role
from platform.identity.service import bootstrap_identity
from platform.observability.service import bootstrap_observability
from platform.tests.validation_console_helpers import accepted_subject
from platform.validation.bootstrap import (
    VALIDATION_CONSOLE_BOOTSTRAP_EVENT,
    bootstrap_validation_console,
)
from platform.validation.contracts import VALIDATION_CONSOLE_CONTRACTS
from platform.validation.health import validation_console_health_checks
from platform.validation.service import ValidationConsoleService


def test_bootstrap_composes_and_publishes_contracts():
    ctx = bootstrap_platform()
    service = bootstrap_validation_console(ctx)
    assert isinstance(service, ValidationConsoleService)
    for ref in VALIDATION_CONSOLE_CONTRACTS:
        assert ref.name in ctx.services
    probe_names = set(service.health.probe())
    for check in validation_console_health_checks():
        assert check.name in probe_names


def test_bootstrap_registers_health_checks_into_observability():
    ctx = bootstrap_platform()
    obs = bootstrap_observability(ctx)
    bootstrap_validation_console(ctx, observability=obs)
    for check in validation_console_health_checks():
        assert check.name in obs.health


def test_bootstrap_emits_event():
    ctx = bootstrap_platform()
    bootstrap_validation_console(ctx)
    assert len(ctx.events.events_of(VALIDATION_CONSOLE_BOOTSTRAP_EVENT)) == 1


def test_bootstrap_is_idempotent_on_contracts_and_health():
    ctx = bootstrap_platform()
    auth = bootstrap_identity(ctx)
    obs = bootstrap_observability(ctx)
    bootstrap_validation_console(ctx, authorization=auth, observability=obs)
    # second composition must not raise (idempotent contract + health registration)
    bootstrap_validation_console(ctx, authorization=auth, observability=obs)
    for ref in VALIDATION_CONSOLE_CONTRACTS:
        assert ref.name in ctx.services


def test_bootstrapped_service_surfaces_end_to_end():
    ctx = bootstrap_platform()
    auth = bootstrap_identity(ctx)
    service = bootstrap_validation_console(ctx, authorization=auth)
    arch = Principal.create("arch@x", [Role.ARCHITECT], tenant="acme")
    sess = auth.establish_session(arch, issued_at=0, ttl=1000)
    rec = service.surface_validation(sess.session_id, accepted_subject(), now=1, tenant="acme")
    assert service.verify_fidelity(rec.record_id) is True
