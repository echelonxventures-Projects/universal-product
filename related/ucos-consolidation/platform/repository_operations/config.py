"""EPIC-PLAT-003 — Repository Operations configuration loader (Terminal T5).

Everything the runtime does is **configuration driven** (no hardcoding): the pipeline
of stages is declared in a JSON or TOML file and assimilated into an immutable
:class:`~platform.repository_operations.contracts.OperationsConfig`. Parsing uses the
Python standard library only (``json`` / ``tomllib``), so the loader is vendor-neutral
and deterministic.
"""

from __future__ import annotations

import json
import tomllib
from collections.abc import Mapping
from pathlib import Path
from platform.repository_operations.contracts import OperationsConfig
from platform.repository_operations.errors import OperationsConfigError
from typing import Any


def parse_config(raw: Mapping[str, Any]) -> OperationsConfig:
    """Assimilate an in-memory configuration mapping into an :class:`OperationsConfig`."""
    return OperationsConfig.from_mapping(raw)


def load_config(path: str | Path) -> OperationsConfig:
    """Load and assimilate a repository-operations config from a JSON or TOML file.

    Raises:
        OperationsConfigError: if the file is absent, unreadable, of an unsupported
            type, or not valid JSON/TOML.
    """
    config_path = Path(path)
    if not config_path.is_file():
        raise OperationsConfigError("configuration file not found", path=str(config_path))

    suffix = config_path.suffix.lower()
    try:
        if suffix == ".json":
            raw = json.loads(config_path.read_text(encoding="utf-8"))
        elif suffix == ".toml":
            raw = tomllib.loads(config_path.read_text(encoding="utf-8"))
        else:
            raise OperationsConfigError(
                "unsupported configuration file type (expected .json or .toml)",
                path=str(config_path),
                suffix=suffix,
            )
    except (json.JSONDecodeError, tomllib.TOMLDecodeError, OSError, UnicodeDecodeError) as exc:
        raise OperationsConfigError(
            "configuration file could not be read or parsed",
            path=str(config_path),
            detail=str(exc),
        ) from exc

    if not isinstance(raw, Mapping):
        raise OperationsConfigError(
            "configuration root must be a mapping/table", path=str(config_path)
        )
    return parse_config(raw)


__all__ = ["parse_config", "load_config"]
