"""UCOS-EPIC-014 — Universal Assurance run configuration (Terminal T7).

An assurance *run* is configuration driven, exactly as the reused validation and
intelligence engines are: the subject under assurance, the policy that governs it, and
where evidence may be written are declared in a JSON or TOML file and assimilated into an
immutable :class:`AssuranceConfig`. Parsing uses the Python standard library only
(``json`` / ``tomllib``), so the loader is vendor-neutral and deterministic.

The configuration separates the two authorities cleanly:

    * the **policy** (``policy_path``, defaulting to the canonical policy shipped with the
      package) declares *what must hold*, and
    * the **subject** (``subject``) supplies *the facts* it must hold over.

Neither can be inferred from the other, and a run that cannot resolve both is a malformed
configuration (an authoring fault) rather than a fail-closed verdict.
"""

from __future__ import annotations

import json
import tomllib
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from platform.foundation.contracts import content_hash
from platform.universal_assurance.contracts import AssuranceSubject
from platform.universal_assurance.errors import AssuranceConfigError, AssuranceSubjectError
from platform.universal_assurance.policy import (
    AssurancePolicy,
    load_default_policy,
    load_policy,
    package_data_path,
)
from typing import Any

#: The run configuration format identifier.
CONFIG_FORMAT = "ucos-assurance-config/1.0.0"

#: The self-check configuration shipped with the package (a known-good reference run).
SELFCHECK_CONFIG_FILENAME = "ucos-assurance-selfcheck.json"

_CONFIG_KEYS = frozenset(
    {"$schema", "$comment", "policy_path", "subject", "evidence_dir", "approver"}
)


@dataclass(frozen=True, slots=True)
class AssuranceConfig:
    """The whole declarative assurance-run configuration."""

    subject: AssuranceSubject
    policy_path: str = ""
    evidence_dir: str = ""
    approver: str = ""

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any]) -> AssuranceConfig:
        """Assimilate a configuration mapping into a normalized config.

        Raises:
            AssuranceConfigError: if the mapping is malformed, declares an unknown key, or
                omits the subject; or if the subject itself cannot be assimilated.
        """
        if not isinstance(raw, Mapping):
            raise AssuranceConfigError("assurance config must be a mapping")
        unknown = sorted(set(raw) - _CONFIG_KEYS)
        if unknown:
            raise AssuranceConfigError(
                "assurance config declares unknown keys",
                unknown=unknown,
                allowed=sorted(_CONFIG_KEYS),
            )
        raw_subject = raw.get("subject")
        if raw_subject is None:
            raise AssuranceConfigError("assurance config requires a 'subject' block")
        try:
            subject = AssuranceSubject.from_mapping(raw_subject)
        except AssuranceSubjectError as exc:
            raise AssuranceConfigError(
                "assurance config subject could not be assimilated", detail=str(exc)
            ) from exc
        return cls(
            subject=subject,
            policy_path=cls._optional_text(raw.get("policy_path"), "policy_path"),
            evidence_dir=cls._optional_text(raw.get("evidence_dir"), "evidence_dir"),
            approver=cls._optional_text(raw.get("approver"), "approver"),
        )

    @staticmethod
    def _optional_text(value: Any, field_name: str) -> str:
        if value is None:
            return ""
        if not isinstance(value, str):
            raise AssuranceConfigError("assurance config field must be a string", field=field_name)
        return value

    def load_policy(self) -> AssurancePolicy:
        """Load the governing policy — the declared one, or the canonical default."""
        if self.policy_path:
            return load_policy(self.policy_path)
        return load_default_policy()

    def resolved_evidence_dir(self, policy: AssurancePolicy) -> str:
        """The evidence directory: the config's, else the policy's declared root."""
        if self.evidence_dir:
            return self.evidence_dir
        return policy.binding("evidence_root", "")

    def to_dict(self) -> dict[str, Any]:
        return {
            "config_format": CONFIG_FORMAT,
            "policy_path": self.policy_path,
            "evidence_dir": self.evidence_dir,
            "approver": self.approver,
            "subject": self.subject.to_dict(),
        }

    def digest(self) -> str:
        """The deterministic content hash of the configuration."""
        return content_hash(self.to_dict())


def parse_config(raw: Mapping[str, Any]) -> AssuranceConfig:
    """Assimilate an in-memory mapping into an :class:`AssuranceConfig`."""
    return AssuranceConfig.from_mapping(raw)


def load_config(path: str | Path) -> AssuranceConfig:
    """Load and assimilate an assurance run configuration from JSON or TOML.

    Raises:
        AssuranceConfigError: if the file is absent, unreadable, of an unsupported type,
            or not valid JSON/TOML.
    """
    config_path = Path(path)
    if not config_path.is_file():
        raise AssuranceConfigError("configuration file not found", path=str(config_path))

    suffix = config_path.suffix.lower()
    try:
        if suffix == ".json":
            raw = json.loads(config_path.read_text(encoding="utf-8"))
        elif suffix == ".toml":
            raw = tomllib.loads(config_path.read_text(encoding="utf-8"))
        else:
            raise AssuranceConfigError(
                "unsupported configuration file type (expected .json or .toml)",
                path=str(config_path),
                suffix=suffix,
            )
    except (json.JSONDecodeError, tomllib.TOMLDecodeError, OSError, UnicodeDecodeError) as exc:
        raise AssuranceConfigError(
            "configuration file could not be read or parsed",
            path=str(config_path),
            detail=str(exc),
        ) from exc

    if not isinstance(raw, Mapping):
        raise AssuranceConfigError(
            "configuration root must be a mapping/table", path=str(config_path)
        )
    return parse_config(raw)


def selfcheck_config_path() -> Path:
    """The path of the reference self-check configuration shipped with the package."""
    return package_data_path(SELFCHECK_CONFIG_FILENAME)


def load_selfcheck_config() -> AssuranceConfig:
    """Load the reference self-check configuration (a known-good, gate-able run)."""
    return load_config(selfcheck_config_path())


__all__ = [
    "CONFIG_FORMAT",
    "SELFCHECK_CONFIG_FILENAME",
    "AssuranceConfig",
    "parse_config",
    "load_config",
    "selfcheck_config_path",
    "load_selfcheck_config",
]
