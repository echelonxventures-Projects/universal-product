"""EC2-TASK-000056 — Platform Configuration (EC2-EPIC-001).

Environment-scoped, immutable platform configuration with **secrets by reference
only**. The Platform Foundation **reuses** the EC-1 configuration loader
(:class:`~engine.foundation.config.config.Config`, :class:`Environment`,
:class:`SecretRef`, :func:`load_config`) additively — inheriting SEC-04 (no inline
secrets), DE-03 (environment parity), and TP-05 (stdlib-only) — and wraps it with a
typed :class:`PlatformConfig` that exposes the platform-level settings every future
EC-2 epic reads (program identity, API version, tenancy, feature flags).

Configuration is deterministic: given the same inputs (file + environment mapping)
it yields the same :class:`PlatformConfig`, and its ``fingerprint`` is a stable,
redacted content hash (no secret material) usable by TRACK-001.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from platform.foundation.contracts import (
    PLATFORM_CONTRACT_VERSION,
    PLATFORM_NAME,
    PLATFORM_PROGRAM_ID,
    content_hash,
)
from platform.foundation.errors import PlatformConfigError
from typing import Any

from engine.foundation.config.config import (
    Config,
    Environment,
    SecretRef,
    load_config,
)

#: Default platform settings (deterministic; overridable via config/env).
DEFAULT_API_VERSION = "1.0.0"
DEFAULT_MULTI_TENANT = True


@dataclass(frozen=True, slots=True)
class PlatformConfig:
    """Immutable, typed platform configuration bound to one :class:`Environment`.

    Wraps an EC-1 :class:`Config` (the raw, environment-scoped values) and exposes
    the platform-level settings. Secrets remain by reference only on the underlying
    ``Config`` (SEC-04); this wrapper never materializes a secret value.
    """

    environment: Environment
    program_id: str
    platform_name: str
    contract_version: str
    api_version: str
    multi_tenant: bool
    raw: Config

    @classmethod
    def from_config(cls, config: Config) -> PlatformConfig:
        """Project an EC-1 :class:`Config` into a typed :class:`PlatformConfig`."""
        if not isinstance(config, Config):
            raise PlatformConfigError("a valid EC-1 Config is required")
        api_version = str(config.get("platform_api_version", DEFAULT_API_VERSION))
        multi_tenant = config.get_bool("platform_multi_tenant", DEFAULT_MULTI_TENANT)
        return cls(
            environment=config.environment,
            program_id=PLATFORM_PROGRAM_ID,
            platform_name=str(config.get("platform_name", PLATFORM_NAME)),
            contract_version=PLATFORM_CONTRACT_VERSION,
            api_version=api_version,
            multi_tenant=bool(multi_tenant),
            raw=config,
        )

    def secret(self, key: str) -> SecretRef:
        """Return the :class:`SecretRef` for ``key`` (never a raw secret value)."""
        return self.raw.secret(key)

    def get(self, key: str, default: Any = None) -> Any:
        return self.raw.get(key, default)

    def to_dict(self) -> dict[str, Any]:
        """A redacted, serializable view safe to log (secrets -> '***')."""
        return {
            "program_id": self.program_id,
            "platform_name": self.platform_name,
            "environment": self.environment.value,
            "contract_version": self.contract_version,
            "api_version": self.api_version,
            "multi_tenant": self.multi_tenant,
            "settings": self.raw.as_dict(),
        }

    def fingerprint(self) -> str:
        """A deterministic, redacted content hash of the platform configuration."""
        return content_hash(self.to_dict())


def load_platform_config(
    environment: Environment | str | None = None,
    *,
    config_file: str | Path | None = None,
    environ: Mapping[str, str] | None = None,
) -> PlatformConfig:
    """Build a :class:`PlatformConfig` by delegating to the EC-1 config loader.

    Precedence and secret discipline are inherited verbatim from EC-1: file (JSON)
    < ``UCOS_``-prefixed environment; secret-typed keys must be references (SEC-04).
    """
    config = load_config(environment, config_file=config_file, environ=environ)
    return PlatformConfig.from_config(config)


__all__ = [
    "DEFAULT_API_VERSION",
    "DEFAULT_MULTI_TENANT",
    "Environment",
    "SecretRef",
    "PlatformConfig",
    "load_platform_config",
]
