"""TASK-000038 — Factory Contracts (EPIC-006).

The value types that flow across the Factory Layer boundary. Every type here is
**immutable, typed, deterministic, and serializable** and holds **no runtime
state** (no registry handles, signers, file handles, or wall-clock data): they
describe *what was requested* and *what was produced*, so identical inputs yield
identical, byte-reproducible contract objects (IMP-007 §5).

    * :class:`FactoryRequest` — a request to generate one blueprint.
    * :class:`FactoryCapability` — what a factory can do (the pipeline stages it
      participates in for a blueprint class); the substrate of capability discovery.
    * :class:`FactoryDescriptor` — the immutable identity of a registered factory.
    * :class:`FactoryResult` — the outcome of a generation (real artifacts on
      success, a faithful gap on deferral).

These contracts are pure data; the Foundation contract-versioning discipline
(AR-03, PL-05) is expressed through :data:`FACTORY_CONTRACT_VERSION`.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

#: The semantic version of the Factory Layer contract surface (AR-03/PL-05).
FACTORY_CONTRACT_VERSION = "1.0.0"


class GenerationStatus(str, Enum):
    """The outcome status of a generation request."""

    #: The compiler and runtime produced real, certified artifacts.
    GENERATED = "generated"
    #: The class is classified and routed, but the compiler defers it (e.g. a
    #: family not yet compilable in the current compiler scope). A Gap Report is
    #: attached; no artifacts are invented (TP-01).
    GAP = "gap"


@dataclass(frozen=True, slots=True)
class FactoryRequest:
    """An immutable request to generate a single blueprint (no runtime state)."""

    blueprint_id: str
    environment: str = "runtime"

    def to_dict(self) -> dict[str, Any]:
        return {"blueprint_id": self.blueprint_id, "environment": self.environment}


@dataclass(frozen=True, slots=True)
class FactoryCapability:
    """What a factory can do for a blueprint class — the unit of discovery."""

    blueprint_class: str
    stages: tuple[str, ...]
    description: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "blueprint_class": self.blueprint_class,
            "stages": list(self.stages),
            "description": self.description,
        }


@dataclass(frozen=True, slots=True)
class FactoryDescriptor:
    """The immutable identity of a registered factory (a registration record)."""

    name: str
    blueprint_class: str
    capability: FactoryCapability
    contract_version: str = FACTORY_CONTRACT_VERSION

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "blueprint_class": self.blueprint_class,
            "capability": self.capability.to_dict(),
            "contract_version": self.contract_version,
        }


@dataclass(frozen=True, slots=True)
class FactoryResult:
    """The immutable outcome of a generation request (deterministic + serializable)."""

    blueprint_id: str
    blueprint_class: str
    factory_name: str
    status: GenerationStatus
    success: bool
    artifact_id: str | None = None
    runtime_id: str | None = None
    package_sha256: str | None = None
    image_reference: str | None = None
    dependency_closure: tuple[Mapping[str, Any], ...] = ()
    disclosure_present: bool = False
    evidence: Mapping[str, Any] = field(default_factory=dict)
    gap: Mapping[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "blueprint_id": self.blueprint_id,
            "blueprint_class": self.blueprint_class,
            "factory_name": self.factory_name,
            "status": self.status.value,
            "success": self.success,
            "artifact_id": self.artifact_id,
            "runtime_id": self.runtime_id,
            "package_sha256": self.package_sha256,
            "image_reference": self.image_reference,
            "dependency_closure": [dict(entry) for entry in self.dependency_closure],
            "disclosure_present": self.disclosure_present,
            "evidence": dict(self.evidence),
            "gap": dict(self.gap) if self.gap is not None else None,
        }


__all__ = [
    "FACTORY_CONTRACT_VERSION",
    "GenerationStatus",
    "FactoryRequest",
    "FactoryCapability",
    "FactoryDescriptor",
    "FactoryResult",
]
