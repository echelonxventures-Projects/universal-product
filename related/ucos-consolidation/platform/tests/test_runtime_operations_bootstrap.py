"""EC2-TASK-000172 — Runtime Operations bootstrap tests (EC2-EPIC-012).

Covers composition onto a platform context: default (internal identity/observability)
composition, composition over supplied identity/observability services with contracts
published + health checks registered, the bootstrap event emitted, and idempotency (the
contract- and health-skip branches) on a repeated composition.
"""

from __future__ import annotations

from platform.foundation.bootstrap import bootstrap_platform
from platform.identity.service import bootstrap_identity
from platform.observability.service import bootstrap_observability
from platform.runtime_operations.bootstrap import (
    RUNTIME_OPERATIONS_BOOTSTRAP_EVENT,
    bootstrap_runtime_operations,
)
from platform.runtime_operations.contracts import RUNTIME_OPERATIONS_CONTRACTS
from platform.runtime_operations.health import runtime_operations_health_checks
from platform.runtime_operations.service import RuntimeOperationsService


def test_bootstrap_default_internal_composition():
    context = bootstrap_platform()
    service = bootstrap_runtime_operations(context)
    assert isinstance(service, RuntimeOperationsService)
    for ref in RUNTIME_OPERATIONS_CONTRACTS:
        assert ref.name in context.services
    assert len(context.events.events_of(RUNTIME_OPERATIONS_BOOTSTRAP_EVENT)) == 1


def test_bootstrap_over_supplied_identity_and_observability():
    context = bootstrap_platform()
    auth = bootstrap_identity(context)
    obs = bootstrap_observability(context)
    service = bootstrap_runtime_operations(context, authorization=auth, observability=obs)
    assert service.authorization is auth
    assert service.observability is obs
    for check in runtime_operations_health_checks():
        assert check.name in obs.health
    for ref in RUNTIME_OPERATIONS_CONTRACTS:
        assert ref.name in context.services


def test_bootstrap_is_idempotent_on_contracts_and_health():
    context = bootstrap_platform()
    auth = bootstrap_identity(context)
    obs = bootstrap_observability(context)
    bootstrap_runtime_operations(context, authorization=auth, observability=obs)
    # A second composition with the same services exercises the contract- and health-skip
    # branches and must not raise on duplicates.
    service = bootstrap_runtime_operations(context, authorization=auth, observability=obs)
    assert isinstance(service, RuntimeOperationsService)
    for ref in RUNTIME_OPERATIONS_CONTRACTS:
        assert ref.name in context.services
    for check in runtime_operations_health_checks():
        assert check.name in obs.health
