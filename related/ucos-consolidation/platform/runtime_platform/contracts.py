"""EPIC-007 (Terminal T7) — Universal Runtime Platform contracts & vocabulary.

The immutable, deterministic contract surface of the Universal Runtime Platform. It
**reuses** the Platform Foundation contract machinery verbatim
(:class:`~platform.foundation.contracts.ContractRef`, :func:`platform_contract`,
:func:`content_hash`) and declares:

    * :data:`RUNTIME_PLATFORM_CONTRACT_VERSION` / :data:`RUNTIME_PLATFORM_GROUP`.
    * :class:`RuntimeServiceKind` — the canonical platform runtime services this plane
      realizes (execution scheduling, workload placement, runtime lifecycle, capacity
      governance, workflow resolution/execution, event publication/delivery, execution
      registration), mirroring the ratified ``PRS-001..004`` / ``PRS-026..030`` /
      ``PRS-013/015`` / ``PRS-022`` runtime-service topology.
    * :class:`ConsumedCapability` and :data:`CONSUMED_CONTRACTS` — the certified
      upstream engines the platform consumes **by reference**: Registry, Knowledge,
      Measurement, Validation, and Certification.
    * :class:`WorkloadAttestation` — the immutable, content-addressed evidence a caller
      supplies to prove a workload was Registered, Knowledge-linked, Measured,
      Validated, and Certified upstream. It is the admission token the runtime plane
      gates on (VALIDATED ∧ CERTIFIED, fail-closed) and the lineage it records.
    * The runtime-service :class:`~engine.foundation.contracts.contract.Contract`
      builders and :data:`RUNTIME_PLATFORM_CONTRACTS`.

Every type is **immutable, typed, deterministic, and serializable** and holds no
runtime state. Nothing here selects a technology, runtime, or product (PEP-010).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from platform.foundation.contracts import Contract, ContractRef, content_hash, platform_contract
from platform.runtime_platform.errors import RuntimePlatformContractError
from typing import Any

#: The semantic version of the Universal Runtime Platform contract surface.
RUNTIME_PLATFORM_CONTRACT_VERSION = "1.0.0"

#: The capability group under which runtime-platform actions authorize (RBAC row).
RUNTIME_PLATFORM_GROUP = "runtime-platform"


class RuntimeServiceKind(Enum):
    """The canonical platform runtime services realized by the Universal Runtime Platform.

    Each maps 1:1 to a ratified Platform Runtime Service (``PRS``) in the Runtime &
    Compute / Workflow / Messaging / Registry runtime domains; the platform plane is a
    governance/record realization of these service topologies, not a product.
    """

    EXECUTION_SCHEDULING = "execution-scheduling"  # PRS-001
    WORKLOAD_PLACEMENT = "workload-placement"  # PRS-002
    RUNTIME_LIFECYCLE = "runtime-lifecycle"  # PRS-003
    CAPACITY_GOVERNANCE = "capacity-governance"  # PRS-004
    WORKFLOW_RESOLUTION = "workflow-resolution"  # PRS-026
    WORKFLOW_EXECUTION = "workflow-execution"  # PRS-027
    EVENT_PUBLICATION = "event-publication"  # PRS-013
    EVENT_DELIVERY = "event-delivery"  # PRS-015
    EXECUTION_REGISTRATION = "execution-registration"  # PRS-022 (registry-first)

    @property
    def service_name(self) -> str:
        """The stable, fully-qualified runtime-service contract name."""
        return f"platform.runtime_platform.{self.value.replace('-', '_')}"


def all_runtime_service_kinds() -> tuple[RuntimeServiceKind, ...]:
    """Every runtime-service kind in a stable, deterministic order."""
    return tuple(RuntimeServiceKind)


class ConsumedCapability(Enum):
    """The certified upstream engines the runtime platform consumes **by reference**."""

    REGISTRY = "engine.registry.read"
    KNOWLEDGE = "engine.knowledge.graph"
    MEASUREMENT = "engine.measurement.measure"
    VALIDATION = "engine.validation.validate"
    CERTIFICATION = "engine.certification.certify"


#: The read-only contract references the runtime platform binds to consume the certified
#: upstream capabilities. The platform accesses these engines *only* through these
#: references (additive, registry-only, no upstream modification): Registry (existence),
#: Knowledge (lineage/meaning), Measurement (metrics), Validation (fitness), and
#: Certification (attested fitness). Registration and validation/certification are the
#: hard admission inputs (see :class:`WorkloadAttestation`).
CONSUMED_CONTRACTS: tuple[ContractRef, ...] = tuple(
    ContractRef(capability.value, "1.0.0") for capability in ConsumedCapability
)


@dataclass(frozen=True, slots=True)
class WorkloadAttestation:
    """Immutable, content-addressed upstream attestation for a workload (admission token).

    The caller supplies this to prove — *by reference* to the certified upstream engines
    — that a workload was Registered (``registry_id``), Knowledge-linked
    (``knowledge_id``), Measured (``measurement_id``), Validated (``validated``), and
    Certified (``certified``). The runtime plane records it as lineage and admits the
    workload only when it is both ``validated`` and ``certified`` (fail-closed). It holds
    no business data and re-derives no upstream datum.
    """

    workload_id: str
    registry_id: str
    validated: bool
    certified: bool
    knowledge_id: str | None = None
    measurement_id: str | None = None
    attestation_id: str = ""

    def __post_init__(self) -> None:
        if not isinstance(self.workload_id, str) or not self.workload_id:
            raise RuntimePlatformContractError("attestation workload_id is required")
        if not isinstance(self.registry_id, str) or not self.registry_id:
            raise RuntimePlatformContractError(
                "attestation registry_id is required (Registry-First)",
                workload_id=self.workload_id,
            )
        if not isinstance(self.validated, bool) or not isinstance(self.certified, bool):
            raise RuntimePlatformContractError(
                "attestation validated/certified must be booleans",
                workload_id=self.workload_id,
            )
        if not self.attestation_id:
            object.__setattr__(
                self, "attestation_id", f"UCOS-URPA-{content_hash(self._core())[:16]}"
            )

    def _core(self) -> dict[str, Any]:
        return {
            "workload_id": self.workload_id,
            "registry_id": self.registry_id,
            "validated": self.validated,
            "certified": self.certified,
            "knowledge_id": self.knowledge_id,
            "measurement_id": self.measurement_id,
        }

    @property
    def admissible(self) -> bool:
        """True iff the workload is both VALIDATED and CERTIFIED upstream (fail-closed gate)."""
        return self.validated and self.certified

    def consumed_capabilities(self) -> tuple[ConsumedCapability, ...]:
        """Which upstream capabilities this attestation carries evidence for (deterministic)."""
        present: list[ConsumedCapability] = [ConsumedCapability.REGISTRY]
        if self.knowledge_id is not None:
            present.append(ConsumedCapability.KNOWLEDGE)
        if self.measurement_id is not None:
            present.append(ConsumedCapability.MEASUREMENT)
        if self.validated:
            present.append(ConsumedCapability.VALIDATION)
        if self.certified:
            present.append(ConsumedCapability.CERTIFICATION)
        return tuple(present)

    def to_dict(self) -> dict[str, Any]:
        payload = self._core()
        payload["attestation_id"] = self.attestation_id
        payload["admissible"] = self.admissible
        return payload

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())


class RuntimePlatformAction(Enum):
    """The governed verbs the Universal Runtime Platform exposes (verb→permission map)."""

    SUBMIT = "submit"  # submit an execution / run a workflow (write)
    INSPECT = "inspect"  # inspect a recorded execution (read)
    DISCOVER = "discover"  # discover/filter executions (read)
    VIEW_LEDGER = "view-ledger"  # view the execution-registry ledger (read)
    VIEW_LINEAGE = "view-lineage"  # view execution lineage (read)


def runtime_platform_contract(kind: RuntimeServiceKind, description: str = "") -> Contract:
    """Build the versioned runtime-service :class:`Contract` for a service kind."""
    if not isinstance(kind, RuntimeServiceKind):
        raise RuntimePlatformContractError(
            "runtime_platform_contract requires a RuntimeServiceKind"
        )
    return platform_contract(
        kind.service_name,
        RUNTIME_PLATFORM_CONTRACT_VERSION,
        description or f"UCOS Universal Runtime Platform service: {kind.value}.",
    )


def default_runtime_platform_contracts() -> tuple[Contract, ...]:
    """Every runtime-service contract in deterministic (kind) order."""
    return tuple(runtime_platform_contract(kind) for kind in all_runtime_service_kinds())


#: The runtime-service contract references the platform publishes (by name), in order.
RUNTIME_PLATFORM_CONTRACTS: tuple[ContractRef, ...] = tuple(
    ContractRef(kind.service_name, RUNTIME_PLATFORM_CONTRACT_VERSION)
    for kind in all_runtime_service_kinds()
)


@dataclass(frozen=True, slots=True)
class RuntimeServiceView:
    """An immutable read projection of a declared runtime service (discovery)."""

    kind: RuntimeServiceKind
    service_name: str
    capabilities: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": self.kind.value,
            "service_name": self.service_name,
            "capabilities": list(self.capabilities),
        }


__all__ = [
    "RUNTIME_PLATFORM_CONTRACT_VERSION",
    "RUNTIME_PLATFORM_GROUP",
    "RuntimeServiceKind",
    "all_runtime_service_kinds",
    "ConsumedCapability",
    "CONSUMED_CONTRACTS",
    "WorkloadAttestation",
    "RuntimePlatformAction",
    "runtime_platform_contract",
    "default_runtime_platform_contracts",
    "RUNTIME_PLATFORM_CONTRACTS",
    "RuntimeServiceView",
]
