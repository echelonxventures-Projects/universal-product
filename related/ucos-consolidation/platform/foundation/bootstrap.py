"""EC2-TASK-000062 — Platform Bootstrap Architecture (EC2-EPIC-001).

Composes the Platform Foundation into a single, deterministic
:class:`PlatformContext` that every future EC-2 epic receives and builds on. The
bootstrap:

    1. loads/accepts the platform configuration (TASK-000056);
    2. creates the platform contract registry (TASK-000055);
    3. creates the service registry (TASK-000058) over that contract registry;
    4. seeds the capability catalog with the certified EC-1 engine capabilities and
       the platform-native capabilities, then **validates** it (TASK-000061 + the
       dependency model, TASK-000059);
    5. creates the append-only event bus (TASK-000060);
    6. emits a deterministic ``platform.bootstrap.completed`` event and returns the
       context.

The bootstrap is **fail-closed** (any contract/dependency/capability error aborts
with :class:`BootstrapError`) and **deterministic**: the same configuration yields a
context with the same :meth:`PlatformContext.fingerprint`. It reuses EC-1
observability (structured logging + telemetry span) additively.

**Scope guardrail:** bootstrap composes the *foundation only*. It starts no server,
opens no socket, renders no UI, and implements no portal, workspace, dashboard, or
runtime operation. It never writes to the certified corpus (DP-03) and never
modifies EC-1.
"""

from __future__ import annotations

from dataclasses import dataclass
from platform.foundation.capabilities import (
    CapabilityCatalog,
    CapabilityKind,
    default_capability_catalog,
)
from platform.foundation.config import PlatformConfig, load_platform_config
from platform.foundation.contracts import (
    ENGINE_CONTRACTS,
    PLATFORM_CONTRACT_VERSION,
    content_hash,
)
from platform.foundation.errors import BootstrapError
from platform.foundation.events import EventBus
from platform.foundation.services import ServiceRegistry
from typing import Any

from engine.foundation.obs.logging import get_logger
from engine.foundation.obs.telemetry import trace

_logger = get_logger("platform.bootstrap")

#: The event type emitted when the platform foundation is composed.
BOOTSTRAP_EVENT = "platform.bootstrap.completed"


@dataclass(frozen=True, slots=True)
class PlatformContext:
    """The composed Platform Foundation shared by every EC-2 epic.

    Immutable references to the foundational subsystems: configuration, the contract
    registry, the service registry, the capability catalog, and the event bus. The
    subsystems themselves are mutable registries (services/events accrete over the
    platform's life), but the context binding is fixed at bootstrap.
    """

    config: PlatformConfig
    services: ServiceRegistry
    capabilities: CapabilityCatalog
    events: EventBus

    @property
    def contracts(self):  # -> ContractRegistry
        """The platform contract registry (owned by the service registry)."""
        return self.services.contracts

    @property
    def program_id(self) -> str:
        return self.config.program_id

    @property
    def platform_name(self) -> str:
        return self.config.platform_name

    def engine_contract_refs(self) -> tuple[str, ...]:
        """The EC-1 engine contracts this platform is permitted to consume."""
        return tuple(ref.name for ref in ENGINE_CONTRACTS)

    def summary(self) -> dict[str, Any]:
        """A small, loggable, deterministic summary of the composed foundation."""
        return {
            "program_id": self.config.program_id,
            "platform_name": self.config.platform_name,
            "environment": self.config.environment.value,
            "contract_version": PLATFORM_CONTRACT_VERSION,
            "capabilities": len(self.capabilities),
            "engine_capabilities": len(self.capabilities.of_kind(CapabilityKind.ENGINE)),
            "services": len(self.services),
            "engine_contracts": list(self.engine_contract_refs()),
        }

    def fingerprint(self) -> str:
        """A deterministic content hash proving reproducible composition."""
        return content_hash(
            {
                "config": self.config.fingerprint(),
                "capabilities": self.capabilities.to_dict(),
                "services": self.services.to_dict(),
                "engine_contracts": [r.to_dict() for r in ENGINE_CONTRACTS],
            }
        )


def bootstrap_platform(
    config: PlatformConfig | None = None,
    *,
    seed_capabilities: bool = True,
) -> PlatformContext:
    """Compose and return the Platform Foundation :class:`PlatformContext`.

    Args:
        config: an explicit :class:`PlatformConfig`; when ``None`` it is loaded via
            the EC-1 config loader (:func:`load_platform_config`).
        seed_capabilities: when True (default) the capability catalog is seeded with
            the certified EC-1 engine capabilities and the platform-native
            capabilities, then validated.

    Raises:
        BootstrapError: on any configuration, contract, dependency, or capability
            failure (fail-closed — a foundation that cannot be validly composed is
            never returned).
    """
    with trace("platform.bootstrap"):
        try:
            platform_config = config if config is not None else load_platform_config()
            services = ServiceRegistry()
            capabilities = (
                default_capability_catalog() if seed_capabilities else CapabilityCatalog()
            )
            # A seeded catalog is already validated by default_capability_catalog();
            # re-validate defensively so a caller-supplied unseeded catalog is safe.
            capabilities.validate()
            services.validate()
            events = EventBus()
            context = PlatformContext(
                config=platform_config,
                services=services,
                capabilities=capabilities,
                events=events,
            )
        except BootstrapError:
            raise
        except Exception as exc:  # noqa: BLE001 — normalize into a fail-closed error
            raise BootstrapError("platform foundation bootstrap failed", detail=str(exc)) from exc

        events.publish(
            BOOTSTRAP_EVENT,
            source="platform.bootstrap",
            subject=platform_config.program_id,
            payload={
                "platform_name": platform_config.platform_name,
                "environment": platform_config.environment.value,
                "contract_version": PLATFORM_CONTRACT_VERSION,
                "capabilities": len(capabilities),
                "fingerprint": context.fingerprint(),
            },
        )

    _logger.info(
        "platform.bootstrap.completed",
        program_id=platform_config.program_id,
        environment=platform_config.environment.value,
        capabilities=len(capabilities),
        fingerprint=context.fingerprint(),
    )
    return context


__all__ = ["BOOTSTRAP_EVENT", "PlatformContext", "bootstrap_platform"]
