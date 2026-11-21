"""UCOS-USAF-001 — Assimilation Framework bootstrap & service registration.

Composes the one assimilation pipeline from the shipped adapters, the open source-kind
registry and the declared Repository Truth policy, and publishes it as a platform service so
no engine ever needs to grow its own ingestion path again.
"""

from __future__ import annotations

from platform.foundation.contracts import platform_contract
from platform.foundation.services import ServiceDescriptor, ServiceRegistry
from platform.universal_assimilation.adapters import (
    SourceAdapterRegistry,
    default_adapter_registry,
)
from platform.universal_assimilation.contracts import (
    ASSIMILATION_CONTRACT_VERSION,
    USAF_ID,
    SourceKindRegistry,
    default_source_kind_registry,
)
from platform.universal_assimilation.pipeline import AssimilationPipeline
from platform.universal_truth.policy import TruthPolicy, default_truth_policy

#: The service name under which source assimilation is published.
ASSIMILATION_SERVICE_NAME = "universal.assimilation"


def bootstrap_assimilation(
    *,
    policy: TruthPolicy | None = None,
    adapters: SourceAdapterRegistry | None = None,
    kinds: SourceKindRegistry | None = None,
) -> AssimilationPipeline:
    """Build the assimilation pipeline from declared policy and registered adapters."""
    return AssimilationPipeline(
        adapters or default_adapter_registry(),
        policy=policy or default_truth_policy(),
        kinds=kinds or default_source_kind_registry(),
    )


def assimilation_service_descriptor() -> ServiceDescriptor:
    """The published service descriptor for source assimilation."""
    return ServiceDescriptor(
        name=ASSIMILATION_SERVICE_NAME,
        contract=platform_contract(
            "assimilation.pipeline.assimilate",
            ASSIMILATION_CONTRACT_VERSION,
            "Assimilate any source through one framework.",
        ),
        capabilities=(USAF_ID,),
        description="Universal Source Assimilation Framework — one road for every source.",
    )


def register_assimilation(
    registry: ServiceRegistry, *, policy: TruthPolicy | None = None
) -> ServiceDescriptor:
    """Register source assimilation into ``registry`` (lazy, memoised)."""
    return registry.register(
        assimilation_service_descriptor(), lambda: bootstrap_assimilation(policy=policy)
    )


__all__ = [
    "ASSIMILATION_SERVICE_NAME",
    "bootstrap_assimilation",
    "assimilation_service_descriptor",
    "register_assimilation",
]
