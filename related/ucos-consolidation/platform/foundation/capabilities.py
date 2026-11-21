"""EC2-TASK-000061 — Platform Capability Model (EC2-EPIC-001).

Models the platform's capabilities and, crucially, the **mapping** from each
platform capability to the certified EC-1 engine capability it consumes. This is the
authoritative, machine-readable encoding of the EC-1 ↔ EC-2 boundary declared in the
Program (§2.1/§4.3): the platform exposes capabilities; those backed by the engine
bind to a certified EC-1 capability by contract reference — never by re-implementing
it (additive, no EC-1 modification).

Two capability kinds are modeled:
    * :attr:`CapabilityKind.ENGINE` — a certified EC-1 capability (the 13 capabilities
      the EC-1 Program Closure certified) surfaced through the Execution Layer façade.
    * :attr:`CapabilityKind.PLATFORM` — a platform-native capability (PC-01…PC-18).

The :class:`CapabilityCatalog` is deterministic and validates that every declared
capability dependency resolves; it can order capabilities via the dependency model.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from enum import Enum
from platform.foundation.contracts import ContractRef
from platform.foundation.dependencies import DependencyGraph
from platform.foundation.errors import CapabilityError
from typing import Any


class CapabilityKind(str, Enum):
    """Whether a capability is engine-backed (EC-1) or platform-native."""

    ENGINE = "engine"
    PLATFORM = "platform"


@dataclass(frozen=True, slots=True)
class Capability:
    """An immutable capability declaration."""

    capability_id: str
    name: str
    kind: CapabilityKind
    description: str = ""
    engine_contract: ContractRef | None = None
    depends_on: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.capability_id, str) or not self.capability_id:
            raise CapabilityError("capability_id is required")
        if self.kind is CapabilityKind.ENGINE and self.engine_contract is None:
            raise CapabilityError(
                "an engine capability must bind an engine contract",
                capability_id=self.capability_id,
            )
        if self.kind is CapabilityKind.PLATFORM and self.engine_contract is not None:
            raise CapabilityError(
                "a platform-native capability must not bind an engine contract",
                capability_id=self.capability_id,
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "capability_id": self.capability_id,
            "name": self.name,
            "kind": self.kind.value,
            "description": self.description,
            "engine_contract": self.engine_contract.to_dict() if self.engine_contract else None,
            "depends_on": list(self.depends_on),
        }


class CapabilityCatalog:
    """A deterministic catalog of platform + engine capabilities."""

    __slots__ = ("_capabilities",)

    def __init__(self) -> None:
        self._capabilities: dict[str, Capability] = {}

    def register(self, capability: Capability) -> Capability:
        if capability.capability_id in self._capabilities:
            raise CapabilityError(
                "capability already registered", capability_id=capability.capability_id
            )
        self._capabilities[capability.capability_id] = capability
        return capability

    def register_all(self, capabilities: Iterable[Capability]) -> None:
        for capability in capabilities:
            self.register(capability)

    def __contains__(self, capability_id: str) -> bool:
        return capability_id in self._capabilities

    def __len__(self) -> int:
        return len(self._capabilities)

    def get(self, capability_id: str) -> Capability:
        capability = self._capabilities.get(capability_id)
        if capability is None:
            raise CapabilityError("no such capability", capability_id=capability_id)
        return capability

    @property
    def ids(self) -> tuple[str, ...]:
        return tuple(sorted(self._capabilities))

    def of_kind(self, kind: CapabilityKind) -> tuple[Capability, ...]:
        return tuple(
            self._capabilities[cid] for cid in self.ids if self._capabilities[cid].kind is kind
        )

    def validate(self) -> None:
        """Validate that every declared capability dependency resolves (no cycles)."""
        graph = DependencyGraph()
        for cid in self.ids:
            graph.add(cid, self._capabilities[cid].depends_on)
        graph.validate()

    def order(self) -> tuple[str, ...]:
        """Return a deterministic dependency-honest capability order."""
        graph = DependencyGraph()
        for cid in self.ids:
            graph.add(cid, self._capabilities[cid].depends_on)
        return graph.topological_order()

    def to_dict(self) -> dict[str, Any]:
        return {
            "capability_count": len(self._capabilities),
            "capabilities": [self._capabilities[cid].to_dict() for cid in self.ids],
        }


# --------------------------------------------------------------------------- #
# Canonical capability sets — the EC-1 ↔ EC-2 boundary, encoded.               #
# --------------------------------------------------------------------------- #

#: The 13 certified EC-1 engine capabilities (EC-1 Program Closure), each bound to
#: the engine contract the Execution Layer façade consumes (registry-only, additive).
_ENGINE_CAPABILITIES: tuple[tuple[str, str, str], ...] = (
    ("ENG-CAP-01", "Registry Resolution", "engine.registry.read"),
    ("ENG-CAP-02", "Blueprint Classification", "engine.compiler.compile"),
    ("ENG-CAP-03", "Compilation", "engine.compiler.compile"),
    ("ENG-CAP-04", "Deterministic Build", "engine.determinism.reproduce"),
    ("ENG-CAP-05", "Signing", "engine.compiler.compile"),
    ("ENG-CAP-06", "SBOM", "engine.compiler.compile"),
    ("ENG-CAP-07", "Runtime Assembly", "engine.runtime.assemble"),
    ("ENG-CAP-08", "Deployment Descriptor", "engine.runtime.deploy"),
    ("ENG-CAP-09", "Rollback Descriptor", "engine.runtime.deploy"),
    ("ENG-CAP-10", "Factory Generation", "engine.factory.generate"),
    ("ENG-CAP-11", "Validation", "engine.validation.validate"),
    ("ENG-CAP-12", "Certification", "engine.certification.certify"),
    ("ENG-CAP-13", "Certification Ledger", "engine.certification.certify"),
)

#: The 18 platform-native capabilities (PC-01…PC-18 of the Program).
_PLATFORM_CAPABILITIES: tuple[tuple[str, str], ...] = (
    ("PC-01", "Authentication & session management"),
    ("PC-02", "Authorization & RBAC"),
    ("PC-03", "Workspace & project lifecycle"),
    ("PC-04", "Blueprint authoring & validation"),
    ("PC-05", "Blueprint catalog"),
    ("PC-06", "Generation request orchestration"),
    ("PC-07", "Pipeline execution & status"),
    ("PC-08", "Artifact inspection"),
    ("PC-09", "Validation inspection"),
    ("PC-10", "Certification inspection & ledger"),
    ("PC-11", "Runtime deploy/rollback operations"),
    ("PC-12", "Monitoring & observability"),
    ("PC-13", "Search & discovery"),
    ("PC-14", "Notifications & events"),
    ("PC-15", "Administration & policy"),
    ("PC-16", "Audit & traceability"),
    ("PC-17", "API access"),
    ("PC-18", "Determinism & reproducibility preservation"),
)


def default_engine_capabilities() -> tuple[Capability, ...]:
    """The certified EC-1 engine capabilities, each bound to an engine contract."""
    return tuple(
        Capability(
            capability_id=cid,
            name=name,
            kind=CapabilityKind.ENGINE,
            description=f"Certified EC-1 capability: {name}.",
            engine_contract=ContractRef(contract, "1.0.0"),
        )
        for cid, name, contract in _ENGINE_CAPABILITIES
    )


def default_platform_capabilities() -> tuple[Capability, ...]:
    """The platform-native capabilities (PC-01…PC-18)."""
    return tuple(
        Capability(
            capability_id=cid,
            name=name,
            kind=CapabilityKind.PLATFORM,
            description=f"Platform capability: {name}.",
        )
        for cid, name in _PLATFORM_CAPABILITIES
    )


def default_capability_catalog() -> CapabilityCatalog:
    """A catalog seeded with all engine + platform capabilities (validated)."""
    catalog = CapabilityCatalog()
    catalog.register_all(default_engine_capabilities())
    catalog.register_all(default_platform_capabilities())
    catalog.validate()
    return catalog


__all__ = [
    "CapabilityKind",
    "Capability",
    "CapabilityCatalog",
    "default_engine_capabilities",
    "default_platform_capabilities",
    "default_capability_catalog",
]
