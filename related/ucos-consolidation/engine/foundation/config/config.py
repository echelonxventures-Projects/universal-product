"""TASK-000005 — Configuration loader.

Environment-scoped, immutable configuration with **secrets by reference only**.

Constitutional basis:
    * SEC-04 / ID-04 — no secret material in source, config, or logs. Inline secret
      values are rejected; secret-typed keys must carry a :class:`SecretRef`
      (e.g. ``env://DB_PASSWORD``) that is resolved at call time and never stored.
    * DE-03 — explicit environment parity across development…production.
    * TP-05 — stdlib only.

Precedence (lowest → highest): file (JSON) < process environment (``UCOS_`` prefix).
"""

from __future__ import annotations

import json
import os
import re
from collections.abc import Mapping
from enum import Enum
from pathlib import Path
from typing import Any

from engine.foundation.obs.errors import ConfigurationError, SecurityViolation

_ENV_VAR = "UCOS_ENV"
_ENV_PREFIX = "UCOS_"

# Keys whose values are treated as secrets and therefore forbidden inline (SEC-04).
_SECRET_KEY_PATTERN = re.compile(
    r"(password|passwd|secret|token|api[_-]?key|apikey|credential|"
    r"private[_-]?key|access[_-]?key)",
    re.IGNORECASE,
)

_TRUE = frozenset({"1", "true", "yes", "on"})
_FALSE = frozenset({"0", "false", "no", "off"})


class Environment(str, Enum):
    """The five parity environments (DE-03)."""

    DEVELOPMENT = "development"
    TESTING = "testing"
    QA = "qa"
    STAGING = "staging"
    PRODUCTION = "production"

    @classmethod
    def from_str(cls, value: str) -> Environment:
        try:
            return cls(str(value).strip().lower())
        except ValueError as exc:
            valid = ", ".join(member.value for member in cls)
            raise ConfigurationError("unknown environment", value=value, valid=valid) from exc


class SecretRef:
    """An opaque, resolve-on-demand reference to a secret (SEC-04, ID-04).

    The secret value is never held on the instance and never rendered in
    ``repr``/``str`` output, so it cannot leak into logs.
    """

    __slots__ = ("scheme", "locator")
    _SUPPORTED = ("env",)

    def __init__(self, reference: str) -> None:
        if not isinstance(reference, str) or "://" not in reference:
            raise ConfigurationError(
                "secret reference must be '<scheme>://<locator>'", reference=str(reference)
            )
        scheme, locator = reference.split("://", 1)
        scheme = scheme.strip().lower()
        if scheme not in self._SUPPORTED:
            raise ConfigurationError(
                "unsupported secret scheme", scheme=scheme, supported=list(self._SUPPORTED)
            )
        if not locator:
            raise ConfigurationError("secret reference locator is empty", reference=reference)
        self.scheme = scheme
        self.locator = locator

    @staticmethod
    def is_reference(value: Any) -> bool:
        """True iff ``value`` is a string using a supported secret scheme."""
        return (
            isinstance(value, str)
            and "://" in value
            and value.split("://", 1)[0].strip().lower() in SecretRef._SUPPORTED
        )

    def resolve(self) -> str:
        """Resolve the secret from its source, or raise if unavailable."""
        if self.scheme == "env":
            try:
                return os.environ[self.locator]
            except KeyError as exc:
                raise ConfigurationError(
                    "secret source absent from environment", locator=self.locator
                ) from exc
        raise ConfigurationError("unsupported secret scheme", scheme=self.scheme)

    def __repr__(self) -> str:
        return f"SecretRef(scheme={self.scheme!r}, locator='***')"

    __str__ = __repr__

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, SecretRef)
            and other.scheme == self.scheme
            and other.locator == self.locator
        )

    def __hash__(self) -> int:
        return hash((self.scheme, self.locator))


class Config:
    """Immutable, typed configuration bound to one :class:`Environment`."""

    __slots__ = ("_values", "_environment")

    def __init__(self, values: Mapping[str, Any], environment: Environment) -> None:
        self._values: dict[str, Any] = dict(values)
        self._environment = environment

    @property
    def environment(self) -> Environment:
        return self._environment

    def __contains__(self, key: str) -> bool:
        return key in self._values

    def get(self, key: str, default: Any = None) -> Any:
        return self._values.get(key, default)

    def require(self, key: str) -> Any:
        """Return the value for ``key`` or raise if it is absent."""
        if key not in self._values:
            raise ConfigurationError(
                "required configuration key missing",
                key=key,
                environment=self._environment.value,
            )
        return self._values[key]

    def get_int(self, key: str, default: int | None = None) -> int | None:
        if key not in self._values:
            return default
        raw = self._values[key]
        try:
            return int(raw)
        except (TypeError, ValueError) as exc:
            raise ConfigurationError("expected an integer", key=key, value=raw) from exc

    def get_float(self, key: str, default: float | None = None) -> float | None:
        if key not in self._values:
            return default
        raw = self._values[key]
        try:
            return float(raw)
        except (TypeError, ValueError) as exc:
            raise ConfigurationError("expected a float", key=key, value=raw) from exc

    def get_bool(self, key: str, default: bool | None = None) -> bool | None:
        if key not in self._values:
            return default
        raw = self._values[key]
        if isinstance(raw, bool):
            return raw
        token = str(raw).strip().lower()
        if token in _TRUE:
            return True
        if token in _FALSE:
            return False
        raise ConfigurationError("expected a boolean", key=key, value=raw)

    def secret(self, key: str) -> SecretRef:
        """Return the :class:`SecretRef` for ``key`` (never a raw value)."""
        value = self.require(key)
        if not isinstance(value, SecretRef):
            raise ConfigurationError("configuration value is not a secret reference", key=key)
        return value

    def as_dict(self) -> dict[str, Any]:
        """Return a redacted copy safe to log (SecretRef -> '***')."""
        return {
            key: ("***" if isinstance(value, SecretRef) else value)
            for key, value in self._values.items()
        }

    def __repr__(self) -> str:
        return f"Config(environment={self._environment.value!r}, keys={sorted(self._values)})"


def _load_file(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise ConfigurationError("config file not found", path=str(path))
    if path.suffix != ".json":
        raise ConfigurationError("unsupported config file type (only .json)", path=str(path))
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ConfigurationError("invalid JSON config", path=str(path), detail=str(exc)) from exc
    if not isinstance(data, dict):
        raise ConfigurationError("config root must be a JSON object", path=str(path))
    return {str(key): value for key, value in data.items()}


def _coerce_secrets(values: Mapping[str, Any]) -> dict[str, Any]:
    processed: dict[str, Any] = {}
    for key, value in values.items():
        if _SECRET_KEY_PATTERN.search(key):
            if isinstance(value, SecretRef):
                processed[key] = value
            elif SecretRef.is_reference(value):
                processed[key] = SecretRef(value)
            else:
                raise SecurityViolation(
                    "inline secret values are forbidden; use a reference such as env://VAR",
                    key=key,
                )
        else:
            processed[key] = value
    return processed


def load_config(
    environment: Environment | str | None = None,
    *,
    config_file: str | Path | None = None,
    environ: Mapping[str, str] | None = None,
) -> Config:
    """Build a :class:`Config`.

    Args:
        environment: explicit environment; when ``None`` it is read from
            ``UCOS_ENV`` (default ``development``).
        config_file: optional JSON file providing base values (lowest precedence).
        environ: environment mapping to read (defaults to ``os.environ``); values
            under the ``UCOS_`` prefix override file values.
    """
    source_environ = os.environ if environ is None else environ

    if environment is None:
        environment = source_environ.get(_ENV_VAR, Environment.DEVELOPMENT.value)
    env = environment if isinstance(environment, Environment) else Environment.from_str(environment)

    values: dict[str, Any] = {}
    if config_file is not None:
        values.update(_load_file(Path(config_file)))

    for name, value in source_environ.items():
        if name.startswith(_ENV_PREFIX) and name != _ENV_VAR:
            values[name[len(_ENV_PREFIX) :].lower()] = value

    return Config(_coerce_secrets(values), env)


__all__ = ["Environment", "SecretRef", "Config", "load_config"]
