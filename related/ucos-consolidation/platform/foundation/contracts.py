"""EC2-TASK-000055 — Platform Contracts (EC2-EPIC-001).

Every inter-module and platform↔engine interaction crosses a **documented,
semantically versioned contract** (AR-03 / PL-05). The Platform Foundation
**reuses** the EC-1 contract machinery (:class:`~engine.foundation.contracts.contract.Version`,
:class:`Contract`, :class:`ContractRegistry`) verbatim and additively — it does not
re-implement or modify it — and layers on the platform-specific contract surface:

    * :data:`PLATFORM_CONTRACT_VERSION` — the platform foundation contract version.
    * :class:`ContractRef` — an immutable *reference* to a required contract
      (name + minimum version) used by the service, dependency, and capability models.
    * :func:`platform_contract` — a helper that builds a versioned platform
      :class:`Contract`.
    * :func:`canonical_json` / :func:`content_hash` — the single deterministic
      serialization + hashing used across the foundation for content-addressed,
      reproducible identities (IMP-007 §5).
    * :data:`ENGINE_CONTRACTS` — the canonical, read-only set of EC-1 engine
      contracts the platform is permitted to consume (registry-only, additive).

All types are **immutable, typed, deterministic, and serializable** and hold no
runtime state.
"""

from __future__ import annotations

from dataclasses import dataclass
from platform.foundation.errors import PlatformContractError

from engine.foundation.contracts.contract import Contract, ContractRegistry, Version

# The canonical serialization primitive has exactly one definition, in UCKP Layer Zero
# (UCKP-LAW-0001 Art-13, UCKP-INV-03). Re-exported unchanged, so every platform caller
# of ``platform.foundation.contracts.content_hash`` keeps working against one
# implementation instead of a byte-identical copy of it.
from engine.uckp.canonical import canonical_json, content_hash

#: The semantic version of the Platform Foundation contract surface (AR-03/PL-05).
PLATFORM_CONTRACT_VERSION = "1.0.0"

#: Stable identity of the platform foundation itself.
PLATFORM_NAME = "UCOS Platform"
PLATFORM_PROGRAM_ID = "EC-2"


@dataclass(frozen=True, slots=True)
class ContractRef:
    """An immutable reference to a required contract (name + minimum version).

    Consumers declare the contracts they depend on by reference; the platform
    contract registry resolves a backward-compatible provider (PL-05).
    """

    name: str
    version: str = PLATFORM_CONTRACT_VERSION

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name:
            raise PlatformContractError("contract reference name is required")
        # Validate the version parses as a semantic version (reuses EC-1 discipline).
        Version.parse(self.version)

    def as_version(self) -> Version:
        return Version.parse(self.version)

    def to_dict(self) -> dict[str, str]:
        return {"name": self.name, "version": self.version}


def platform_contract(name: str, version: str, description: str = "") -> Contract:
    """Build a versioned platform :class:`Contract` (reuses EC-1 ``Contract``)."""
    if not isinstance(name, str) or not name:
        raise PlatformContractError("platform contract name is required")
    return Contract(name=name, version=Version.parse(version), description=description)


#: The canonical set of **EC-1 engine contracts** the platform may consume. These
#: mirror the certified EC-1 capabilities; the platform accesses the engine *only*
#: through these references (additive, registry-only, no EC-1 modification). The
#: registry read contract is the one EC-1 publishes today (``registry.read`` v1);
#: the remainder are the platform-side capability contract identities the Execution
#: Layer (L4 façade) binds to the corresponding certified engine modules.
ENGINE_CONTRACTS: tuple[ContractRef, ...] = (
    ContractRef("engine.registry.read", "1.0.0"),
    ContractRef("engine.compiler.compile", "1.0.0"),
    ContractRef("engine.determinism.reproduce", "1.0.0"),
    ContractRef("engine.runtime.assemble", "1.0.0"),
    ContractRef("engine.runtime.deploy", "1.0.0"),
    ContractRef("engine.factory.generate", "1.0.0"),
    ContractRef("engine.validation.validate", "1.0.0"),
    ContractRef("engine.certification.certify", "1.0.0"),
)


def platform_contract_registry() -> ContractRegistry:
    """Return a fresh :class:`ContractRegistry` (the platform's contract registry).

    Reuses the EC-1 registry verbatim so the platform inherits the same versioning
    discipline (reject duplicates; refuse older versions within a major line).
    """
    return ContractRegistry()


__all__ = [
    "PLATFORM_CONTRACT_VERSION",
    "PLATFORM_NAME",
    "PLATFORM_PROGRAM_ID",
    "Version",
    "Contract",
    "ContractRegistry",
    "ContractRef",
    "platform_contract",
    "platform_contract_registry",
    "canonical_json",
    "content_hash",
    "ENGINE_CONTRACTS",
]
