"""UCOS-EPIC-014 — Repository Intelligence configuration (Terminal T5).

Everything Repository Intelligence does is **configuration driven and
repository-agnostic**: no absolute path is hardcoded, the repository root is *resolved*
from substrate markers, and every threshold a detector uses is a declared, overridable
field rather than a magic number buried in a comparison.

Root resolution deliberately uses **code-substrate markers** (``pyproject.toml`` plus the
declared code roots) rather than the corpus-evidence markers used by UCOS-RIE-001: this
subsystem reasons about the *code and declaration substrate*, so it must remain usable in
a repository that has code but no corpus. When both are present the two resolvers agree.

Parsing uses the Python standard library only (``json`` / ``tomllib``), so the loader is
vendor-neutral and deterministic (TP-04).
"""

from __future__ import annotations

import json
import tomllib
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from platform.foundation.contracts import content_hash
from platform.repository_intelligence.errors import IntelligenceConfigurationError
from typing import Any

#: Substrate markers that identify a repository root for *code* intelligence.
_ROOT_MARKERS: tuple[str, ...] = ("pyproject.toml",)

#: Directories never walked (build/tooling caches and version-control internals).
DEFAULT_IGNORED_DIRS: tuple[str, ...] = (
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    "__pycache__",
    "dist",
    "build",
)

#: Module basenames that are an established repository convention rather than a
#: duplication smell. Derived from the repository's own EC-2 subsystem layout
#: (``contracts``/``config``/``engine``/``errors``/``evidence``/``service``/``cli``).
DEFAULT_CONVENTION_MODULES: tuple[str, ...] = (
    "__init__",
    "__main__",
    "cli",
    "config",
    "contracts",
    "engine",
    "errors",
    "evidence",
    "service",
)


def resolve_repository_root(start: Path | None = None) -> Path:
    """Resolve the repository root by walking upward to the substrate markers.

    Falls back to the parent of the ``platform`` package when no marker is found, so the
    resolver never raises and never returns an unrelated ancestor.
    """
    here = (start or Path(__file__)).resolve()
    candidates = (here, *here.parents) if here.is_dir() else here.parents
    for candidate in candidates:
        if all((candidate / marker).exists() for marker in _ROOT_MARKERS):
            return candidate
    return Path(__file__).resolve().parents[2]


@dataclass(frozen=True, slots=True)
class RepositoryIntelligenceConfig:
    """The immutable, declarative configuration of a repository-intelligence run."""

    repository_root: Path
    repository_id: str
    code_roots: tuple[str, ...] = ("engine", "platform")
    test_dir_name: str = "tests"
    ignored_dirs: tuple[str, ...] = DEFAULT_IGNORED_DIRS
    convention_modules: tuple[str, ...] = DEFAULT_CONVENTION_MODULES
    output_subdir: str = ".runtime/repository-intelligence"
    capability_catalog: str = "intelligence/UCOS-RIE-CAPABILITY-CATALOG.json"
    pyproject_name: str = "pyproject.toml"
    #: Minimum lines of code before a byte-identical module pair is a duplicate finding.
    #: Below this, identical content is a trivial artefact (an empty package marker).
    duplicate_min_loc: int = 5
    #: Fraction of sibling capabilities that must carry a convention module before its
    #: absence in another sibling is reported as a completeness gap.
    convention_threshold: float = 0.5
    #: Extra evidence surfaces a caller wants fingerprinted into the substrate digest.
    extra_evidence: tuple[str, ...] = ()
    _validated: bool = field(default=False, repr=False, compare=False)

    @classmethod
    def create(
        cls,
        repository_root: str | Path | None = None,
        **overrides: Any,
    ) -> RepositoryIntelligenceConfig:
        """Build a config for ``repository_root`` (auto-resolved when omitted)."""
        root = Path(repository_root).resolve() if repository_root else resolve_repository_root()
        repository_id = str(overrides.pop("repository_id", None) or root.name)
        code_roots = _str_tuple(overrides.pop("code_roots", None)) or ("engine", "platform")
        config = cls(
            repository_root=root,
            repository_id=repository_id,
            code_roots=code_roots,
            test_dir_name=str(overrides.pop("test_dir_name", None) or "tests"),
            ignored_dirs=_str_tuple(overrides.pop("ignored_dirs", None)) or DEFAULT_IGNORED_DIRS,
            convention_modules=(
                _str_tuple(overrides.pop("convention_modules", None)) or DEFAULT_CONVENTION_MODULES
            ),
            output_subdir=str(
                overrides.pop("output_subdir", None) or ".runtime/repository-intelligence"
            ),
            capability_catalog=str(
                overrides.pop("capability_catalog", None)
                or "intelligence/UCOS-RIE-CAPABILITY-CATALOG.json"
            ),
            pyproject_name=str(overrides.pop("pyproject_name", None) or "pyproject.toml"),
            duplicate_min_loc=_positive_int(
                overrides.pop("duplicate_min_loc", 5), "duplicate_min_loc"
            ),
            convention_threshold=_fraction(
                overrides.pop("convention_threshold", 0.5), "convention_threshold"
            ),
            extra_evidence=_str_tuple(overrides.pop("extra_evidence", None)),
        )
        if overrides:
            raise IntelligenceConfigurationError(
                "unknown repository-intelligence configuration key(s)",
                keys=sorted(overrides),
            )
        return config

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any]) -> RepositoryIntelligenceConfig:
        """Assimilate a configuration mapping into an immutable config."""
        if not isinstance(raw, Mapping):
            raise IntelligenceConfigurationError("repository-intelligence config must be a mapping")
        options = dict(raw)
        root = options.pop("repository_root", None)
        return cls.create(root, **options)

    # -- resolved locations ----------------------------------------------
    @property
    def output_dir(self) -> Path:
        return self.repository_root / self.output_subdir

    @property
    def pyproject_path(self) -> Path:
        return self.repository_root / self.pyproject_name

    @property
    def capability_catalog_path(self) -> Path:
        return self.repository_root / self.capability_catalog

    def code_root_path(self, root: str) -> Path:
        return self.repository_root / root

    def rel(self, path: Path) -> str:
        """Return ``path`` repository-relative (absolute paths never leak into output)."""
        try:
            return path.resolve().relative_to(self.repository_root).as_posix()
        except ValueError:
            return path.as_posix()

    def is_ignored(self, path: Path) -> bool:
        """True iff any path component is an ignored directory."""
        return any(part in self.ignored_dirs for part in path.parts)

    def require_substrate(self) -> None:
        """Raise :class:`SubstrateError` if no declared code root exists.

        Fail-closed: intelligence over a repository with no readable code substrate would
        report a vacuous, all-passing verdict, which is worse than an explicit failure.
        """
        from platform.repository_intelligence.errors import SubstrateError

        present = [r for r in self.code_roots if self.code_root_path(r).is_dir()]
        if not present:
            raise SubstrateError(
                "no declared code root exists under the repository root",
                repository_root=str(self.repository_root),
                code_roots=list(self.code_roots),
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "repository_id": self.repository_id,
            "repository_root": self.repository_root.name,
            "code_roots": list(self.code_roots),
            "test_dir_name": self.test_dir_name,
            "ignored_dirs": list(self.ignored_dirs),
            "convention_modules": list(self.convention_modules),
            "output_subdir": self.output_subdir,
            "capability_catalog": self.capability_catalog,
            "pyproject_name": self.pyproject_name,
            "duplicate_min_loc": self.duplicate_min_loc,
            "convention_threshold": self.convention_threshold,
            "extra_evidence": list(self.extra_evidence),
        }

    def digest(self) -> str:
        """The deterministic content hash of the configuration.

        Only the repository *name* enters the digest, never the absolute path, so the
        same repository checked out at two locations yields the same identity.
        """
        return content_hash(self.to_dict())


def parse_config(raw: Mapping[str, Any]) -> RepositoryIntelligenceConfig:
    """Assimilate an in-memory mapping into a :class:`RepositoryIntelligenceConfig`."""
    return RepositoryIntelligenceConfig.from_mapping(raw)


def load_config(path: str | Path) -> RepositoryIntelligenceConfig:
    """Load and assimilate a repository-intelligence config from a JSON or TOML file."""
    config_path = Path(path)
    if not config_path.is_file():
        raise IntelligenceConfigurationError("configuration file not found", path=str(config_path))
    suffix = config_path.suffix.lower()
    try:
        if suffix == ".json":
            raw = json.loads(config_path.read_text(encoding="utf-8"))
        elif suffix == ".toml":
            raw = tomllib.loads(config_path.read_text(encoding="utf-8"))
        else:
            raise IntelligenceConfigurationError(
                "unsupported configuration file type (expected .json or .toml)",
                path=str(config_path),
                suffix=suffix,
            )
    except (json.JSONDecodeError, tomllib.TOMLDecodeError, OSError, UnicodeDecodeError) as exc:
        raise IntelligenceConfigurationError(
            "configuration file could not be read or parsed",
            path=str(config_path),
            detail=str(exc),
        ) from exc
    if not isinstance(raw, Mapping):
        raise IntelligenceConfigurationError(
            "configuration root must be a mapping/table", path=str(config_path)
        )
    return parse_config(raw)


# -- assimilation helpers ---------------------------------------------------
def _str_tuple(value: Any) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, str | bytes) or not isinstance(value, Sequence):
        raise IntelligenceConfigurationError("expected a list of strings", value=repr(value))
    return tuple(str(item) for item in value)


def _positive_int(value: Any, key: str) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise IntelligenceConfigurationError(
            "expected an integer", key=key, value=repr(value)
        ) from exc
    if parsed < 0:
        raise IntelligenceConfigurationError(
            "expected a non-negative integer", key=key, value=parsed
        )
    return parsed


def _fraction(value: Any, key: str) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError) as exc:
        raise IntelligenceConfigurationError(
            "expected a number", key=key, value=repr(value)
        ) from exc
    if not 0.0 <= parsed <= 1.0:
        raise IntelligenceConfigurationError("expected a fraction in [0,1]", key=key, value=parsed)
    return parsed


__all__ = [
    "DEFAULT_IGNORED_DIRS",
    "DEFAULT_CONVENTION_MODULES",
    "resolve_repository_root",
    "RepositoryIntelligenceConfig",
    "parse_config",
    "load_config",
]
