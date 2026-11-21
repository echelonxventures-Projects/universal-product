"""UCOS-URTF-001 — Repository Truth Framework bootstrap & service registration.

Composes the framework from a *declared* policy document and publishes it as a first-class
platform service so every consumer resolves the same determination of Truth instead of
re-deriving one. Discovery of Truth is a reusable Foundation service, not the first step of
every implementation.
"""

from __future__ import annotations

from pathlib import Path
from platform.foundation.contracts import platform_contract
from platform.foundation.services import ServiceDescriptor, ServiceRegistry
from platform.universal_truth.contracts import TRUTH_CONTRACT_VERSION, URTF_ID
from platform.universal_truth.policy import (
    TruthPolicy,
    default_truth_policy,
    load_truth_policy,
)

#: The service name under which Repository Truth determination is published.
TRUTH_SERVICE_NAME = "universal.truth"


def bootstrap_repository_truth(document: Path | str | None = None) -> TruthPolicy:
    """Load the declared Repository Truth policy (packaged catalogue by default)."""
    if document is None:
        return default_truth_policy()
    return load_truth_policy(document)


def truth_service_descriptor() -> ServiceDescriptor:
    """The published service descriptor for Repository Truth determination."""
    return ServiceDescriptor(
        name=TRUTH_SERVICE_NAME,
        contract=platform_contract(
            "truth.policy.classify",
            TRUTH_CONTRACT_VERSION,
            "Classify any locator against declared Repository Truth zones.",
        ),
        capabilities=(URTF_ID,),
        description="Universal Repository Truth Framework — policy-determined Truth.",
    )


def register_repository_truth(
    registry: ServiceRegistry, *, document: Path | str | None = None
) -> ServiceDescriptor:
    """Register Repository Truth determination into ``registry`` (lazy, memoised)."""
    return registry.register(
        truth_service_descriptor(), lambda: bootstrap_repository_truth(document)
    )


__all__ = [
    "TRUTH_SERVICE_NAME",
    "bootstrap_repository_truth",
    "truth_service_descriptor",
    "register_repository_truth",
]
