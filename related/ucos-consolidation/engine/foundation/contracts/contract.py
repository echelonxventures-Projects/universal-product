"""TASK-000008 — Versioned interface contracts.

All inter-module interaction in the EC-1 engine occurs through documented,
semantically versioned contracts (AR-03). Contracts evolve backward-compatibly;
breaking changes require a new major version (PL-05). The registry enforces this
discipline: it rejects duplicate registrations and refuses to register an older
version within an existing major line.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from engine.foundation.obs.errors import ContractViolation

_SEMVER = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")


@dataclass(frozen=True, order=True)
class Version:
    """A semantic version ``MAJOR.MINOR.PATCH`` (ordered)."""

    major: int
    minor: int
    patch: int

    @classmethod
    def parse(cls, text: str) -> Version:
        match = _SEMVER.match(str(text).strip())
        if not match:
            raise ContractViolation("invalid semantic version", value=text)
        return cls(int(match.group(1)), int(match.group(2)), int(match.group(3)))

    def is_backward_compatible_with(self, other: Version) -> bool:
        """True iff a consumer requiring ``other`` can be served by ``self``.

        Same major line and ``self`` is at least ``other`` (PL-05).
        """
        return self.major == other.major and (self.minor, self.patch) >= (
            other.minor,
            other.patch,
        )

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"


@dataclass(frozen=True)
class Contract:
    """A named, versioned interface identity."""

    name: str
    version: Version
    description: str = field(default="")

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name:
            raise ContractViolation("contract name is required")
        if not isinstance(self.version, Version):
            raise ContractViolation("contract version must be a Version", name=self.name)


class ContractRegistry:
    """A registry of contracts keyed by name and version (RG-05 auditability)."""

    def __init__(self) -> None:
        self._by_name: dict[str, dict[Version, Contract]] = {}

    def register(self, contract: Contract) -> None:
        """Register a contract, enforcing versioning discipline (PL-05)."""
        versions = self._by_name.setdefault(contract.name, {})
        if contract.version in versions:
            raise ContractViolation(
                "contract version already registered",
                name=contract.name,
                version=str(contract.version),
            )
        same_major = [v for v in versions if v.major == contract.version.major]
        if same_major and contract.version < max(same_major):
            raise ContractViolation(
                "cannot register an older version within an existing major line",
                name=contract.name,
                version=str(contract.version),
                highest=str(max(same_major)),
            )
        versions[contract.version] = contract

    def get(self, name: str, version: str | Version | None = None) -> Contract:
        """Return a registered contract; the latest version when unspecified."""
        versions = self._by_name.get(name)
        if not versions:
            raise ContractViolation("no such contract", name=name)
        if version is None:
            return versions[max(versions)]
        resolved = Version.parse(version) if isinstance(version, str) else version
        if resolved not in versions:
            raise ContractViolation("no such contract version", name=name, version=str(resolved))
        return versions[resolved]

    def check_compatibility(self, name: str, required: str | Version) -> Contract:
        """Return a registered version able to serve ``required`` (PL-05), else raise."""
        needed = Version.parse(required) if isinstance(required, str) else required
        versions = self._by_name.get(name)
        if not versions:
            raise ContractViolation("no such contract", name=name)
        candidates = [versions[v] for v in versions if v.is_backward_compatible_with(needed)]
        if not candidates:
            raise ContractViolation(
                "no backward-compatible version available",
                name=name,
                required=str(needed),
                available=[str(v) for v in sorted(versions)],
            )
        return max(candidates, key=lambda c: c.version)

    def names(self) -> list[str]:
        return sorted(self._by_name)

    def versions(self, name: str) -> list[Version]:
        return sorted(self._by_name.get(name, {}))


__all__ = ["Version", "Contract", "ContractRegistry"]
