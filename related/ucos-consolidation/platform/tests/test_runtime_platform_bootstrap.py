"""EPIC-007 (T7) — Runtime platform bootstrap tests."""

from __future__ import annotations

from platform.foundation.bootstrap import bootstrap_platform
from platform.runtime_platform.bootstrap import (
    RUNTIME_PLATFORM_BOOTSTRAP_EVENT,
    bootstrap_runtime_platform,
)
from platform.runtime_platform.contracts import RuntimeServiceKind
from platform.runtime_platform.service import RuntimePlatformService
from platform.tests.runtime_platform_helpers import request


def test_bootstrap_composes_service_onto_context():
    context = bootstrap_platform()
    service = bootstrap_runtime_platform(context)
    assert isinstance(service, RuntimePlatformService)
    # runtime services are declared into the shared foundation service registry
    for kind in RuntimeServiceKind:
        assert kind.service_name in context.services


def test_bootstrap_emits_completed_event_bound_to_context_bus():
    context = bootstrap_platform()
    bootstrap_runtime_platform(context)
    emitted = [e for e in context.events.events if e.event_type == RUNTIME_PLATFORM_BOOTSTRAP_EVENT]
    assert len(emitted) == 1
    payload = emitted[0].payload
    assert len(payload["consumed_contracts"]) == 5
    assert len(payload["runtime_services"]) == 9


def test_bootstrapped_service_is_operational():
    context = bootstrap_platform()
    service = bootstrap_runtime_platform(context)
    record = service.submit_execution(request("w"))
    assert record.succeeded
    # governed runtime signals flow onto the shared context event bus
    assert any(e.source == "platform.runtime_platform.runtime" for e in context.events.events)


def test_bootstrap_is_idempotent_on_service_declarations():
    context = bootstrap_platform()
    bootstrap_runtime_platform(context)
    # second bootstrap onto the same context must not raise on duplicate declarations
    second = bootstrap_runtime_platform(context)
    assert isinstance(second, RuntimePlatformService)
