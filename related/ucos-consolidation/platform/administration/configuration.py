"""EC2-CAP-ADMIN-001 — Administrative Configuration (Administration Runtime).

The deterministic, append-only store of **operational configuration** — administrative
settings and operational controls scoped to the platform, a tenant, or a workspace. A
setting's identity is its ``(scope, tenant, key)`` triple (content-addressed
``setting_id``), so writes are idempotent-keyed and reproducible. Every change is
recorded as an ordered, append-only :class:`ConfigurationEvent` (no wall-clock; a
caller-supplied logical ``tick``) so configuration history is reproducible and
auditable (OP-C3).

Configuration is **value data only**: it carries no authority, models no governance or
constitutional state, and holds no secret material (SEC-04). It enforces no
authorization (that is the Identity Layer, applied by the service) — it is the
substrate the :class:`~platform.administration.service.AdministrationService` composes.
"""

from __future__ import annotations

from dataclasses import dataclass
from platform.administration.contracts import AdministrativeScope
from platform.administration.errors import AdministrationConfigurationError
from platform.foundation.contracts import content_hash
from typing import Any


def _require_key(key: str) -> str:
    if not isinstance(key, str) or not key:
        raise AdministrationConfigurationError("configuration key is required")
    normalized = key.strip()
    if not normalized or any(c.isspace() for c in normalized):
        raise AdministrationConfigurationError(
            "configuration key must be non-empty and whitespace-free"
        )
    return normalized


def _scope_key(
    scope: AdministrativeScope, tenant: str | None, key: str
) -> tuple[str, str | None, str]:
    if not isinstance(scope, AdministrativeScope):
        raise AdministrationConfigurationError("scope must be an AdministrativeScope")
    return (scope.value, tenant, key)


@dataclass(frozen=True, slots=True)
class AdministrativeSetting:
    """An immutable, content-addressed operational setting (a scoped key/value)."""

    setting_id: str
    scope: AdministrativeScope
    tenant: str | None
    key: str
    value: str

    @classmethod
    def create(
        cls,
        scope: AdministrativeScope,
        key: str,
        value: str,
        *,
        tenant: str | None = None,
    ) -> AdministrativeSetting:
        """Build a setting with a deterministic id (keyed by scope + tenant + key)."""
        if not isinstance(scope, AdministrativeScope):
            raise AdministrationConfigurationError("setting scope must be an AdministrativeScope")
        normalized_key = _require_key(key)
        if not isinstance(value, str):
            raise AdministrationConfigurationError(
                "setting value must be a string", key=normalized_key
            )
        identity = {"scope": scope.value, "tenant": tenant, "key": normalized_key}
        return cls(
            setting_id=f"UCOS-ASET-{content_hash(identity)[:16]}",
            scope=scope,
            tenant=tenant,
            key=normalized_key,
            value=value,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "setting_id": self.setting_id,
            "scope": self.scope.value,
            "tenant": self.tenant,
            "key": self.key,
            "value": self.value,
        }


@dataclass(frozen=True, slots=True)
class ConfigurationEvent:
    """An immutable, ordered record of a configuration change (append-only)."""

    sequence: int
    setting_id: str
    scope: AdministrativeScope
    tenant: str | None
    key: str
    action: str
    tick: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "sequence": self.sequence,
            "setting_id": self.setting_id,
            "scope": self.scope.value,
            "tenant": self.tenant,
            "key": self.key,
            "action": self.action,
            "tick": self.tick,
        }


class AdministrativeConfiguration:
    """A deterministic, append-only registry of operational settings/controls."""

    __slots__ = ("_by_key", "_log")

    def __init__(self) -> None:
        # (scope, tenant, key) -> AdministrativeSetting
        self._by_key: dict[tuple[str, str | None, str], AdministrativeSetting] = {}
        self._log: list[ConfigurationEvent] = []

    def set(
        self,
        scope: AdministrativeScope,
        key: str,
        value: str,
        *,
        tick: int,
        tenant: str | None = None,
    ) -> AdministrativeSetting:
        """Set (create or replace) an operational setting; record the change."""
        setting = AdministrativeSetting.create(scope, key, value, tenant=tenant)
        composite = _scope_key(scope, tenant, setting.key)
        action = "updated" if composite in self._by_key else "created"
        self._by_key[composite] = setting
        self._record(setting, action, tick)
        return setting

    def get(
        self, scope: AdministrativeScope, key: str, *, tenant: str | None = None
    ) -> AdministrativeSetting:
        """Resolve a setting by scope + tenant + key (fail-closed on absent)."""
        composite = _scope_key(scope, tenant, _require_key(key))
        setting = self._by_key.get(composite)
        if setting is None:
            raise AdministrationConfigurationError(
                "no such setting", scope=scope.value, tenant=tenant, key=key
            )
        return setting

    def has(self, scope: AdministrativeScope, key: str, *, tenant: str | None = None) -> bool:
        """True iff a setting exists for scope + tenant + key."""
        return _scope_key(scope, tenant, _require_key(key)) in self._by_key

    def value_of(
        self,
        scope: AdministrativeScope,
        key: str,
        *,
        tenant: str | None = None,
        default: str | None = None,
    ) -> str | None:
        """Return a setting's value, or ``default`` when it is not present."""
        composite = _scope_key(scope, tenant, _require_key(key))
        setting = self._by_key.get(composite)
        return setting.value if setting is not None else default

    def remove(
        self, scope: AdministrativeScope, key: str, *, tick: int, tenant: str | None = None
    ) -> AdministrativeSetting:
        """Remove a setting (fail-closed on absent); record the change."""
        composite = _scope_key(scope, tenant, _require_key(key))
        setting = self._by_key.get(composite)
        if setting is None:
            raise AdministrationConfigurationError(
                "no such setting", scope=scope.value, tenant=tenant, key=key
            )
        del self._by_key[composite]
        self._record(setting, "removed", tick)
        return setting

    def settings_in(
        self, scope: AdministrativeScope, *, tenant: str | None = None
    ) -> tuple[AdministrativeSetting, ...]:
        """Every current setting in a scope (+tenant) in stable (key) order."""
        if not isinstance(scope, AdministrativeScope):
            raise AdministrationConfigurationError("scope must be an AdministrativeScope")
        selected = [
            setting
            for (s, t, _k), setting in self._by_key.items()
            if s == scope.value and t == tenant
        ]
        return tuple(sorted(selected, key=lambda s: s.key))

    def all(self) -> tuple[AdministrativeSetting, ...]:
        """Every current setting in stable (id) order."""
        return tuple(sorted(self._by_key.values(), key=lambda s: s.setting_id))

    @property
    def events(self) -> tuple[ConfigurationEvent, ...]:
        """An immutable snapshot of the append-only configuration event log (in order)."""
        return tuple(self._log)

    def __len__(self) -> int:
        return len(self._by_key)

    def to_dict(self) -> dict[str, Any]:
        return {
            "setting_count": len(self._by_key),
            "settings": [s.to_dict() for s in self.all()],
        }

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())

    def _record(self, setting: AdministrativeSetting, action: str, tick: int) -> None:
        self._log.append(
            ConfigurationEvent(
                sequence=len(self._log),
                setting_id=setting.setting_id,
                scope=setting.scope,
                tenant=setting.tenant,
                key=setting.key,
                action=action,
                tick=tick,
            )
        )


__all__ = ["AdministrativeSetting", "ConfigurationEvent", "AdministrativeConfiguration"]
