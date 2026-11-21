"""UCOS-EPIC-005 — Universal Validation configuration (Terminal T5).

Everything the validation runtime does is **configuration driven** (no hardcoding):
the target under validation, the domain facts, and the (optional) subset of domains to
run are declared in a JSON or TOML file and assimilated into an immutable
:class:`UniversalValidationConfig`. Parsing uses the Python standard library only
(``json`` / ``tomllib``), so the loader is vendor-neutral and deterministic.

The config carries the same domain-keyed ``facts`` shape as a
:class:`~platform.universal_validation.contracts.ValidationTarget`; :meth:`build_target`
projects it into one. When ``domains`` is declared, only those domains' rules run;
otherwise the full universal suite runs.
"""

from __future__ import annotations

import json
import tomllib
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from platform.foundation.contracts import content_hash
from platform.universal_validation.contracts import ValidationDomain, ValidationTarget
from platform.universal_validation.errors import ValidationConfigError
from typing import Any


@dataclass(frozen=True, slots=True)
class UniversalValidationConfig:
    """The whole declarative universal-validation configuration (single source of truth)."""

    target_id: str
    facts: Mapping[str, Mapping[str, Any]]
    domains: tuple[ValidationDomain, ...] = ()

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any]) -> UniversalValidationConfig:
        """Assimilate a configuration mapping into a normalized config.

        Raises:
            ValidationConfigError: if the mapping is malformed, lacks a target id, has
                non-mapping facts, or declares an unknown/duplicate domain.
        """
        if not isinstance(raw, Mapping):
            raise ValidationConfigError("universal-validation config must be a mapping")
        target_id = raw.get("target_id")
        if not target_id or not isinstance(target_id, str):
            raise ValidationConfigError("config requires a non-empty target_id")
        raw_facts = raw.get("facts", {})
        if not isinstance(raw_facts, Mapping):
            raise ValidationConfigError("config facts must be a mapping", target_id=target_id)

        domains: tuple[ValidationDomain, ...] = ()
        raw_domains = raw.get("domains")
        if raw_domains is not None:
            if not isinstance(raw_domains, Sequence) or isinstance(raw_domains, str | bytes):
                raise ValidationConfigError("config 'domains' must be a list", target_id=target_id)
            parsed: list[ValidationDomain] = []
            seen: set[ValidationDomain] = set()
            for value in raw_domains:
                try:
                    domain = ValidationDomain(value)
                except ValueError as exc:
                    raise ValidationConfigError(
                        "config declares an unknown domain",
                        target_id=target_id,
                        domain=value,
                        supported=[d.value for d in ValidationDomain],
                    ) from exc
                if domain in seen:
                    raise ValidationConfigError(
                        "config declares a duplicate domain",
                        target_id=target_id,
                        domain=domain.value,
                    )
                seen.add(domain)
                parsed.append(domain)
            domains = tuple(parsed)

        # Reuse the target's own assimilation to validate the facts shape.
        target = ValidationTarget.from_mapping({"target_id": target_id, "facts": raw_facts})
        return cls(target_id=target.target_id, facts=target.facts, domains=domains)

    def build_target(self) -> ValidationTarget:
        """Project the configuration into an immutable :class:`ValidationTarget`."""
        return ValidationTarget(target_id=self.target_id, facts=self.facts)

    def selected_domains(self) -> tuple[ValidationDomain, ...] | None:
        """The declared domain subset, or ``None`` when the full suite should run."""
        return self.domains or None

    def to_dict(self) -> dict[str, Any]:
        return {
            "target_id": self.target_id,
            "domains": [d.value for d in self.domains],
            "facts": {key: dict(value) for key, value in sorted(self.facts.items())},
        }

    def digest(self) -> str:
        """The deterministic content hash of the configuration."""
        return content_hash(self.to_dict())


def parse_config(raw: Mapping[str, Any]) -> UniversalValidationConfig:
    """Assimilate an in-memory mapping into a :class:`UniversalValidationConfig`."""
    return UniversalValidationConfig.from_mapping(raw)


def load_config(path: str | Path) -> UniversalValidationConfig:
    """Load and assimilate a universal-validation config from a JSON or TOML file.

    Raises:
        ValidationConfigError: if the file is absent, unreadable, of an unsupported
            type, or not valid JSON/TOML.
    """
    config_path = Path(path)
    if not config_path.is_file():
        raise ValidationConfigError("configuration file not found", path=str(config_path))

    suffix = config_path.suffix.lower()
    try:
        if suffix == ".json":
            raw = json.loads(config_path.read_text(encoding="utf-8"))
        elif suffix == ".toml":
            raw = tomllib.loads(config_path.read_text(encoding="utf-8"))
        else:
            raise ValidationConfigError(
                "unsupported configuration file type (expected .json or .toml)",
                path=str(config_path),
                suffix=suffix,
            )
    except (json.JSONDecodeError, tomllib.TOMLDecodeError, OSError, UnicodeDecodeError) as exc:
        raise ValidationConfigError(
            "configuration file could not be read or parsed",
            path=str(config_path),
            detail=str(exc),
        ) from exc

    if not isinstance(raw, Mapping):
        raise ValidationConfigError(
            "configuration root must be a mapping/table", path=str(config_path)
        )
    return parse_config(raw)


__all__ = ["UniversalValidationConfig", "parse_config", "load_config"]
