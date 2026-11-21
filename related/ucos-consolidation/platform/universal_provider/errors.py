"""UPA-000001 — Universal Provider Architecture errors (Terminal-04).

Every failure across the Provider Framework raises a typed, structured, auditable
error derived from :class:`ProviderFrameworkError` (PL-02). Errors carry a stable
``code`` and a deterministic, JSON-serializable ``detail`` mapping so a failure is
as reproducible and as evidenceable as a success.

The framework is **fail-closed** (Constitution PC-07): an unknown provider, an
undeclared capability, an unresolved dependency, an unmet lifecycle precondition, or
an uncertified activation is an *error*, never a silent default.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any


class ProviderFrameworkError(Exception):
    """Base class for every Provider Framework failure.

    Holds a stable machine-readable ``code`` plus a deterministic ``detail`` map.
    Never holds runtime handles, wall-clock values, or provider instances, so an
    error can be serialized into an evidence bundle verbatim.
    """

    #: Stable machine-readable error code (overridden per subclass).
    code = "UPA-ERROR"

    def __init__(self, message: str, detail: Mapping[str, Any] | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.detail: dict[str, Any] = dict(detail or {})

    def to_dict(self) -> dict[str, Any]:
        """Return the deterministic, serializable projection of this error."""
        return {"code": self.code, "message": self.message, "detail": dict(self.detail)}

    def __str__(self) -> str:  # pragma: no cover - trivial formatting
        return f"[{self.code}] {self.message}"


class ProviderConstitutionError(ProviderFrameworkError):
    """A constitutional article was violated or referenced incorrectly."""

    code = "UPA-CONSTITUTION"


class ProviderContractError(ProviderFrameworkError):
    """A provider contract value was malformed, absent, or version-incompatible."""

    code = "UPA-CONTRACT"


class ProviderInterfaceError(ProviderFrameworkError):
    """An object does not satisfy the one constitutional provider interface."""

    code = "UPA-INTERFACE"


class ProviderCapabilityError(ProviderFrameworkError):
    """A capability was invoked that the provider did not declare (PC-04)."""

    code = "UPA-CAPABILITY"


class ProviderRegistryError(ProviderFrameworkError):
    """A registration was rejected, duplicated, or could not be resolved."""

    code = "UPA-REGISTRY"


class ProviderDiscoveryError(ProviderFrameworkError):
    """A discovery source was unreadable or yielded a malformed declaration."""

    code = "UPA-DISCOVERY"


class ProviderLifecycleError(ProviderFrameworkError):
    """An illegal lifecycle transition was attempted (PC-10)."""

    code = "UPA-LIFECYCLE"


class ProviderValidationError(ProviderFrameworkError):
    """Validation could not be executed against the subject."""

    code = "UPA-VALIDATION"


class ProviderCertificationError(ProviderFrameworkError):
    """Certification was requested without a sound validation basis (PC-11)."""

    code = "UPA-CERTIFICATION"


class ProviderCompositionError(ProviderFrameworkError):
    """A composition is cyclic, unresolvable, or strategy-incompatible (PC-12)."""

    code = "UPA-COMPOSITION"


class ProviderExecutionError(ProviderFrameworkError):
    """A provider operation failed. Isolated by the framework (PC-09)."""

    code = "UPA-EXECUTION"


class ProviderEvidenceError(ProviderFrameworkError):
    """An evidence bundle could not be produced or verified."""

    code = "UPA-EVIDENCE"


__all__ = [
    "ProviderFrameworkError",
    "ProviderConstitutionError",
    "ProviderContractError",
    "ProviderInterfaceError",
    "ProviderCapabilityError",
    "ProviderRegistryError",
    "ProviderDiscoveryError",
    "ProviderLifecycleError",
    "ProviderValidationError",
    "ProviderCertificationError",
    "ProviderCompositionError",
    "ProviderExecutionError",
    "ProviderEvidenceError",
]
