"""UCOS-UMPF-001 — Measurement policy bootstrap & service registration.

Publishes the policy measurement engine as a platform service, so a measurement is something
a project *registers* rather than something an engine hardcodes.

The composition is **declared**: :func:`bootstrap_measurement_policies` builds from the
packaged policy declaration (``catalog/ucos-measurement-policies.json``), so which
measurements bind and how strongly each one binds is data (UFC-04). Passing an explicit
registry still overrides it, and passing an explicit document specialises it for a project.
"""

from __future__ import annotations

from pathlib import Path
from platform.foundation.contracts import platform_contract
from platform.foundation.services import ServiceDescriptor, ServiceRegistry
from platform.universal_measurement.contracts import POLICY_CONTRACT_VERSION, UMPF_ID
from platform.universal_measurement.engine import (
    MeasurementPolicyRegistry,
    PolicyMeasurementEngine,
    build_policy_engine,
)
from platform.universal_measurement.policies import (
    declared_measurement_policies,
    load_measurement_policies,
)

#: The service name under which policy-driven measurement is published.
POLICY_SERVICE_NAME = "universal.measurement.policy"


def bootstrap_measurement_policies(
    registry: MeasurementPolicyRegistry | None = None,
    *,
    document: Path | str | None = None,
) -> PolicyMeasurementEngine:
    """Build the policy measurement engine from the declared composition.

    ``registry`` overrides the declaration entirely; ``document`` specialises it. With
    neither, the packaged declaration governs — never a hardcoded policy list.
    """
    if registry is not None:
        return build_policy_engine(registry)
    policies = (
        declared_measurement_policies() if document is None else load_measurement_policies(document)
    )
    return build_policy_engine(MeasurementPolicyRegistry(policies))


def policy_service_descriptor() -> ServiceDescriptor:
    """The published service descriptor for policy-driven measurement."""
    return ServiceDescriptor(
        name=POLICY_SERVICE_NAME,
        contract=platform_contract(
            "measurement.policy.suite",
            POLICY_CONTRACT_VERSION,
            "Evaluate registered measurement policies over Foundation determinations.",
        ),
        capabilities=(UMPF_ID,),
        description="Universal Measurement Policy Framework — measurements as policies.",
    )


def register_measurement_policies(
    registry: ServiceRegistry,
    *,
    policies: MeasurementPolicyRegistry | None = None,
    document: Path | str | None = None,
) -> ServiceDescriptor:
    """Register policy-driven measurement into ``registry`` (lazy, memoised)."""
    return registry.register(
        policy_service_descriptor(),
        lambda: bootstrap_measurement_policies(policies, document=document),
    )


__all__ = [
    "POLICY_SERVICE_NAME",
    "bootstrap_measurement_policies",
    "policy_service_descriptor",
    "register_measurement_policies",
]
