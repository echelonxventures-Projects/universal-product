"""EPIC-007 (Terminal T7) — Runtime Platform Bootstrap (Universal Runtime Platform).

Composes the Universal Runtime Platform onto a
:class:`~platform.foundation.bootstrap.PlatformContext`, registry-driven and
deterministic. The bootstrap:

    1. builds the :class:`~platform.runtime_platform.services.RuntimeServiceCatalog` over
       the context's shared Foundation service registry (so the runtime services are
       declared once into the platform-wide registry, PL-05);
    2. builds the :class:`~platform.runtime_platform.core.RuntimeKernel` over that catalog
       and a :class:`~platform.runtime_platform.events.RuntimeEventBus` bound to the
       context event bus (so every governed runtime signal is observed);
    3. composes the :class:`~platform.runtime_platform.service.RuntimePlatformService`; and
    4. emits a deterministic ``runtime.platform.bootstrap.completed`` event.

It is idempotent on service declarations, fail-closed, consumes the certified upstream
engines (Registry, Knowledge, Measurement, Validation, Certification) only by reference,
governs and records only (no live compute), starts no server, opens no socket, and never
writes to the certified corpus (DP-03).
"""

from __future__ import annotations

from platform.runtime_platform.contracts import CONSUMED_CONTRACTS, RUNTIME_PLATFORM_GROUP
from platform.runtime_platform.core import RuntimeKernel
from platform.runtime_platform.events import RuntimeEventBus
from platform.runtime_platform.service import RuntimePlatformService, build_runtime_platform_service
from platform.runtime_platform.services import RuntimeServiceCatalog
from typing import Any

#: The event emitted when the Universal Runtime Platform is composed onto a context.
RUNTIME_PLATFORM_BOOTSTRAP_EVENT = "runtime.platform.bootstrap.completed"


def bootstrap_runtime_platform(context: Any) -> RuntimePlatformService:
    """Compose the Universal Runtime Platform onto a :class:`PlatformContext`.

    The parameter is typed loosely to avoid a hard import cycle on the foundation
    bootstrap module. The runtime plane consumes the certified upstream engines by
    reference and governs/records executions and workflows only.
    """
    catalog = RuntimeServiceCatalog(context.services)
    kernel = RuntimeKernel(services=catalog, events=RuntimeEventBus(context.events))
    service = build_runtime_platform_service(kernel=kernel)

    context.events.publish(
        RUNTIME_PLATFORM_BOOTSTRAP_EVENT,
        source="platform.runtime_platform.bootstrap",
        subject=context.program_id,
        payload={
            "runtime_platform_group": RUNTIME_PLATFORM_GROUP,
            "runtime_services": list(catalog.names),
            "consumed_contracts": [ref.name for ref in CONSUMED_CONTRACTS],
            "kernel_fingerprint": kernel.fingerprint(),
        },
    )
    return service


__all__ = ["RUNTIME_PLATFORM_BOOTSTRAP_EVENT", "bootstrap_runtime_platform"]
