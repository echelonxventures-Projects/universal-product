"""UCOS-EPIC-013 — Continuous Validation Intelligence configuration (Terminal T5).

Everything the intelligence runtime does is **configuration driven** (no hardcoding):
the target under analysis, the dimension facts, and the (optional) subset of dimensions
to run are declared in a JSON or TOML file and assimilated into an immutable
:class:`ValidationIntelligenceConfig`. Parsing uses the Python standard library only
(``json`` / ``tomllib``), so the loader is vendor-neutral and deterministic.

The config carries the same dimension-keyed ``facts`` shape as an
:class:`~platform.validation_intelligence.contracts.IntelligenceTarget`;
:meth:`build_target` projects it into one. When ``dimensions`` is declared, only those
dimensions' analyzers run; otherwise the full universal suite runs.
"""

from __future__ import annotations

import json
import tomllib
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from platform.foundation.contracts import content_hash
from platform.validation_intelligence.contracts import IntelligenceDimension, IntelligenceTarget
from platform.validation_intelligence.errors import IntelligenceConfigError
from typing import Any


@dataclass(frozen=True, slots=True)
class ValidationIntelligenceConfig:
    """The whole declarative validation-intelligence configuration (single source of truth)."""

    target_id: str
    facts: Mapping[str, Mapping[str, Any]]
    dimensions: tuple[IntelligenceDimension, ...] = ()

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any]) -> ValidationIntelligenceConfig:
        """Assimilate a configuration mapping into a normalized config.

        Raises:
            IntelligenceConfigError: if the mapping is malformed, lacks a target id, has
                non-mapping facts, or declares an unknown/duplicate dimension.
        """
        if not isinstance(raw, Mapping):
            raise IntelligenceConfigError("validation-intelligence config must be a mapping")
        target_id = raw.get("target_id")
        if not target_id or not isinstance(target_id, str):
            raise IntelligenceConfigError("config requires a non-empty target_id")
        raw_facts = raw.get("facts", {})
        if not isinstance(raw_facts, Mapping):
            raise IntelligenceConfigError("config facts must be a mapping", target_id=target_id)

        dimensions = cls._parse_dimensions(raw.get("dimensions"), target_id)
        # Reuse the target's own assimilation to validate the facts shape.
        target = IntelligenceTarget.from_mapping({"target_id": target_id, "facts": raw_facts})
        return cls(target_id=target.target_id, facts=target.facts, dimensions=dimensions)

    @staticmethod
    def _parse_dimensions(raw_dimensions: Any, target_id: str) -> tuple[IntelligenceDimension, ...]:
        if raw_dimensions is None:
            return ()
        if not isinstance(raw_dimensions, Sequence) or isinstance(raw_dimensions, str | bytes):
            raise IntelligenceConfigError("config 'dimensions' must be a list", target_id=target_id)
        parsed: list[IntelligenceDimension] = []
        seen: set[IntelligenceDimension] = set()
        for value in raw_dimensions:
            try:
                dimension = IntelligenceDimension(value)
            except ValueError as exc:
                raise IntelligenceConfigError(
                    "config declares an unknown dimension",
                    target_id=target_id,
                    dimension=value,
                    supported=[d.value for d in IntelligenceDimension],
                ) from exc
            if dimension in seen:
                raise IntelligenceConfigError(
                    "config declares a duplicate dimension",
                    target_id=target_id,
                    dimension=dimension.value,
                )
            seen.add(dimension)
            parsed.append(dimension)
        return tuple(parsed)

    def build_target(self) -> IntelligenceTarget:
        """Project the configuration into an immutable :class:`IntelligenceTarget`."""
        return IntelligenceTarget(target_id=self.target_id, facts=self.facts)

    def selected_dimensions(self) -> tuple[IntelligenceDimension, ...] | None:
        """The declared dimension subset, or ``None`` when the full suite should run."""
        return self.dimensions or None

    def to_dict(self) -> dict[str, Any]:
        return {
            "target_id": self.target_id,
            "dimensions": [d.value for d in self.dimensions],
            "facts": {key: dict(value) for key, value in sorted(self.facts.items())},
        }

    def digest(self) -> str:
        """The deterministic content hash of the configuration."""
        return content_hash(self.to_dict())


def parse_config(raw: Mapping[str, Any]) -> ValidationIntelligenceConfig:
    """Assimilate an in-memory mapping into a :class:`ValidationIntelligenceConfig`."""
    return ValidationIntelligenceConfig.from_mapping(raw)


def load_config(path: str | Path) -> ValidationIntelligenceConfig:
    """Load and assimilate a validation-intelligence config from a JSON or TOML file.

    Raises:
        IntelligenceConfigError: if the file is absent, unreadable, of an unsupported
            type, or not valid JSON/TOML.
    """
    config_path = Path(path)
    if not config_path.is_file():
        raise IntelligenceConfigError("configuration file not found", path=str(config_path))

    suffix = config_path.suffix.lower()
    try:
        if suffix == ".json":
            raw = json.loads(config_path.read_text(encoding="utf-8"))
        elif suffix == ".toml":
            raw = tomllib.loads(config_path.read_text(encoding="utf-8"))
        else:
            raise IntelligenceConfigError(
                "unsupported configuration file type (expected .json or .toml)",
                path=str(config_path),
                suffix=suffix,
            )
    except (json.JSONDecodeError, tomllib.TOMLDecodeError, OSError, UnicodeDecodeError) as exc:
        raise IntelligenceConfigError(
            "configuration file could not be read or parsed",
            path=str(config_path),
            detail=str(exc),
        ) from exc

    if not isinstance(raw, Mapping):
        raise IntelligenceConfigError(
            "configuration root must be a mapping/table", path=str(config_path)
        )
    return parse_config(raw)


__all__ = ["ValidationIntelligenceConfig", "parse_config", "load_config"]
