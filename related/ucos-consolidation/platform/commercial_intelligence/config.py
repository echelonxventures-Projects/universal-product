"""UCOS-EPIC-014 — Commercial Intelligence configuration (Terminal T5).

Everything the commercial runtime does is **configuration driven** (no hardcoding): the
commercial surface under analysis, its per-domain facts, and the optional subset of
domains to run are declared in a JSON or TOML file and assimilated into an immutable
:class:`CommercialConfig`. Parsing uses the Python standard library only
(``json`` / ``tomllib``), so the loader is vendor-neutral and deterministic.

The config carries the same domain-keyed ``facts`` shape as a
:class:`~platform.commercial_intelligence.contracts.CommercialTarget`;
:meth:`build_target` projects it into one. When ``domains`` is declared, only those
domains' analyzers run; otherwise the full fourteen-domain suite runs — and a partial run
is visible in the report, so a narrowed scope can never masquerade as a full one.
"""

from __future__ import annotations

import json
import tomllib
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from platform.commercial_intelligence.contracts import CommercialDomain, CommercialTarget
from platform.commercial_intelligence.errors import CommercialConfigError
from platform.foundation.contracts import content_hash
from typing import Any


@dataclass(frozen=True, slots=True)
class CommercialConfig:
    """The whole declarative commercial-intelligence configuration (single source of truth)."""

    target_id: str
    facts: Mapping[str, Mapping[str, Any]]
    domains: tuple[CommercialDomain, ...] = ()

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any]) -> CommercialConfig:
        """Assimilate a configuration mapping into a normalized config.

        Raises:
            CommercialConfigError: if the mapping is malformed, lacks a target id, has
                non-mapping facts, or declares an unknown/duplicate domain.
        """
        if not isinstance(raw, Mapping):
            raise CommercialConfigError("commercial-intelligence config must be a mapping")
        target_id = raw.get("target_id")
        if not target_id or not isinstance(target_id, str):
            raise CommercialConfigError("config requires a non-empty target_id")
        raw_facts = raw.get("facts", {})
        if not isinstance(raw_facts, Mapping):
            raise CommercialConfigError("config facts must be a mapping", target_id=target_id)

        domains = cls._parse_domains(raw.get("domains"), target_id)
        # Reuse the target's own assimilation to validate the facts shape.
        target = CommercialTarget.from_mapping({"target_id": target_id, "facts": raw_facts})
        return cls(target_id=target.target_id, facts=target.facts, domains=domains)

    @staticmethod
    def _parse_domains(raw_domains: Any, target_id: str) -> tuple[CommercialDomain, ...]:
        if raw_domains is None:
            return ()
        if not isinstance(raw_domains, Sequence) or isinstance(raw_domains, str | bytes):
            raise CommercialConfigError("config 'domains' must be a list", target_id=target_id)
        parsed: list[CommercialDomain] = []
        seen: set[CommercialDomain] = set()
        for value in raw_domains:
            try:
                domain = CommercialDomain(value)
            except ValueError as exc:
                raise CommercialConfigError(
                    "config declares an unknown commercial domain",
                    target_id=target_id,
                    domain=value,
                    supported=[d.value for d in CommercialDomain],
                ) from exc
            if domain in seen:
                raise CommercialConfigError(
                    "config declares a duplicate commercial domain",
                    target_id=target_id,
                    domain=domain.value,
                )
            seen.add(domain)
            parsed.append(domain)
        return tuple(parsed)

    def build_target(self) -> CommercialTarget:
        """Project the configuration into an immutable :class:`CommercialTarget`."""
        return CommercialTarget(target_id=self.target_id, facts=self.facts)

    def selected_domains(self) -> tuple[CommercialDomain, ...] | None:
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


def parse_config(raw: Mapping[str, Any]) -> CommercialConfig:
    """Assimilate an in-memory mapping into a :class:`CommercialConfig`."""
    return CommercialConfig.from_mapping(raw)


def load_config(path: str | Path) -> CommercialConfig:
    """Load and assimilate a commercial-intelligence config from a JSON or TOML file.

    Raises:
        CommercialConfigError: if the file is absent, unreadable, of an unsupported type,
            or not valid JSON/TOML.
    """
    config_path = Path(path)
    if not config_path.is_file():
        raise CommercialConfigError("configuration file not found", path=str(config_path))

    suffix = config_path.suffix.lower()
    try:
        if suffix == ".json":
            raw = json.loads(config_path.read_text(encoding="utf-8"))
        elif suffix == ".toml":
            raw = tomllib.loads(config_path.read_text(encoding="utf-8"))
        else:
            raise CommercialConfigError(
                "unsupported configuration file type (expected .json or .toml)",
                path=str(config_path),
                suffix=suffix,
            )
    except (json.JSONDecodeError, tomllib.TOMLDecodeError, OSError, UnicodeDecodeError) as exc:
        raise CommercialConfigError(
            "configuration file could not be read or parsed",
            path=str(config_path),
            detail=str(exc),
        ) from exc

    if not isinstance(raw, Mapping):
        raise CommercialConfigError(
            "configuration root must be a mapping/table", path=str(config_path)
        )
    return parse_config(raw)


__all__ = ["CommercialConfig", "parse_config", "load_config"]
