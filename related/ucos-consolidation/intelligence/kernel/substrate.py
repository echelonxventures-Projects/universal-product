"""Declaration-driven, read-only access to Repository Truth.

Every fact a derived subsystem may state must come from a **declared** substrate
surface. Adding a surface is an edit to :data:`SUBSTRATE_DECLARATION` (data), not
to any engine — the zero-enumeration discipline the programme engines already
follow. A surface that is absent is reported as ``available = False`` and makes
the dependent verdict ``INDETERMINATE``; it is never replaced by an invented
value (no-fabrication).

The reader never writes. It composes surfaces that certified producers already
emit (compose-never-duplicate).
"""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from intelligence.kernel.canonical import canonical_json, sha256_file, sha256_text
from intelligence.kernel.config import RepoConfig
from intelligence.kernel.errors import SubstrateDeclarationError, SubstrateUnavailableError

#: Allowed keys of a substrate declaration entry (fail-closed schema).
_DECLARATION_KEYS = frozenset(
    {"key", "locator", "media", "root_key", "authority", "role", "required", "glob"}
)

#: Allowed media types.
_MEDIA = frozenset({"json", "directory", "text"})

#: Allowed authority classes of a substrate surface.
_AUTHORITY = frozenset({"CANONICAL", "DERIVED", "GENERATED"})

#: THE substrate declaration. Every research/publication fact resolves to one of
#: these surfaces. Adding a surface here requires NO engine change.
SUBSTRATE_DECLARATION: tuple[dict[str, Any], ...] = (
    {
        "key": "canonical-knowledge",
        "locator": "knowledge/canonical-knowledge.json",
        "media": "json",
        "root_key": "objects",
        "authority": "CANONICAL",
        "role": "The single authoritative home of canonical knowledge objects (UKDA Part 04).",
        "required": True,
    },
    {
        "key": "canonical-decisions",
        "locator": "knowledge/decisions.json",
        "media": "json",
        "root_key": "decisions",
        "authority": "CANONICAL",
        "role": "The permanent record of architectural decisions (UKDA Part 03).",
        "required": True,
    },
    {
        "key": "concept-closure",
        "locator": "00-MASTER/UAKOS-CLOSURE-002/closure.json",
        "media": "json",
        "root_key": "concepts",
        "authority": "DERIVED",
        "role": "Repository concept closure: every concept, its family, disposition and homes.",
        "required": True,
    },
    {
        "key": "concept-graph",
        "locator": "00-BOOK/DATA/relationships.json",
        "media": "json",
        "root_key": "relationships",
        "authority": "GENERATED",
        "role": "The canonical typed relationship graph over corpus artifacts.",
        "required": False,
    },
    {
        "key": "corpus-artifacts",
        "locator": "00-BOOK/DATA/artifacts.json",
        "media": "json",
        "root_key": "artifacts",
        "authority": "GENERATED",
        "role": "The universal artifact register projection (corpus scale + programme map).",
        "required": False,
    },
    {
        "key": "corpus-control-tower",
        "locator": "00-BOOK/DATA/control-tower.json",
        "media": "json",
        "root_key": None,
        "authority": "GENERATED",
        "role": "Portfolio-scale corpus measurements (artifacts, pages, volumes, edges).",
        "required": False,
    },
    {
        "key": "corpus-certification",
        "locator": "00-BOOK/DATA/certification.json",
        "media": "json",
        "root_key": None,
        "authority": "GENERATED",
        "role": "Digital-twin certification verdict over the corpus domains.",
        "required": False,
    },
    {
        "key": "science-registries",
        "locator": "15-UNIVERSAL-SCIENCE-INTELLIGENCE/04-REGISTRIES",
        "media": "directory",
        "root_key": None,
        "authority": "CANONICAL",
        "role": "The Universal Science Intelligence programme registries (USIS-REG-*).",
        "required": False,
        "glob": "USIS-REG-*.md",
    },
    {
        "key": "science-constitution",
        "locator": "15-UNIVERSAL-SCIENCE-INTELLIGENCE/00-CONSTITUTION",
        "media": "directory",
        "root_key": None,
        "authority": "CANONICAL",
        "role": "The Universal Science Intelligence constitution (governing instrument).",
        "required": False,
        "glob": "USIS-*.md",
    },
)


@dataclass(frozen=True, slots=True)
class SubstrateSurface:
    """A single declared surface: what it is, whether it is there, and its hash."""

    key: str
    locator: str
    media: str
    authority: str
    role: str
    required: bool
    available: bool
    content_sha256: str
    record_count: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "key": self.key,
            "locator": self.locator,
            "media": self.media,
            "authority": self.authority,
            "role": self.role,
            "required": self.required,
            "available": self.available,
            "content_sha256": self.content_sha256,
            "record_count": self.record_count,
        }


def _validate(entry: Mapping[str, Any]) -> None:
    unknown = sorted(set(entry) - _DECLARATION_KEYS)
    if unknown:
        raise SubstrateDeclarationError("unknown substrate declaration keys", keys=unknown)
    for field in ("key", "locator", "media", "authority", "role"):
        if not isinstance(entry.get(field), str) or not entry[field]:
            raise SubstrateDeclarationError(
                "substrate field must be a non-empty string", field=field, entry=entry.get("key")
            )
    if entry["media"] not in _MEDIA:
        raise SubstrateDeclarationError(
            "unknown substrate media", media=entry["media"], allowed=sorted(_MEDIA)
        )
    if entry["authority"] not in _AUTHORITY:
        raise SubstrateDeclarationError(
            "unknown substrate authority", authority=entry["authority"], allowed=sorted(_AUTHORITY)
        )
    if not isinstance(entry.get("required"), bool):
        raise SubstrateDeclarationError(
            "substrate 'required' must be a boolean", entry=entry.get("key")
        )


class SubstrateReader:
    """Reads (never writes) the declared Repository Truth surfaces."""

    def __init__(
        self,
        config: RepoConfig,
        declaration: Sequence[Mapping[str, Any]] = SUBSTRATE_DECLARATION,
    ) -> None:
        self.config = config
        entries: dict[str, dict[str, Any]] = {}
        for raw in declaration:
            _validate(raw)
            key = str(raw["key"])
            if key in entries:
                raise SubstrateDeclarationError("substrate key declared twice", key=key)
            entries[key] = dict(raw)
        if not entries:
            raise SubstrateDeclarationError("substrate declaration is empty")
        self._entries = entries
        self._cache: dict[str, Any] = {}

    # -- declaration -----------------------------------------------------------

    def keys(self) -> tuple[str, ...]:
        return tuple(sorted(self._entries))

    def declaration(self, key: str) -> dict[str, Any]:
        try:
            return dict(self._entries[key])
        except KeyError as exc:
            raise SubstrateDeclarationError("substrate key not declared", key=key) from exc

    def path(self, key: str) -> Path:
        return self.config.repo_root / self.declaration(key)["locator"]

    # -- surfaces --------------------------------------------------------------

    def surface(self, key: str) -> SubstrateSurface:
        cache_key = f"surface:{key}"
        if cache_key not in self._cache:
            entry = self.declaration(key)
            path = self.path(key)
            if entry["media"] == "directory":
                available = path.is_dir()
                names = self._directory_names(key) if available else ()
                digest = (
                    sha256_text(canonical_json({n: sha256_file(path / n) for n in names}))
                    if available
                    else "absent"
                )
                count = len(names)
            else:
                available = path.is_file()
                digest = sha256_file(path)
                count = len(self.records(key)) if available else 0
            self._cache[cache_key] = SubstrateSurface(
                key=key,
                locator=entry["locator"],
                media=entry["media"],
                authority=entry["authority"],
                role=entry["role"],
                required=bool(entry["required"]),
                available=available,
                content_sha256=digest,
                record_count=count,
            )
        return self._cache[cache_key]

    def available(self, key: str) -> bool:
        return self.surface(key).available

    def require(self, key: str) -> SubstrateSurface:
        surface = self.surface(key)
        if not surface.available:
            raise SubstrateUnavailableError(
                "declared substrate surface is unavailable — no verdict may be asserted",
                key=key,
                locator=surface.locator,
            )
        return surface

    # -- payloads --------------------------------------------------------------

    def payload(self, key: str) -> dict[str, Any]:
        """The parsed JSON document for a surface, or ``{}`` when unavailable."""
        cache_key = f"payload:{key}"
        if cache_key not in self._cache:
            entry = self.declaration(key)
            if entry["media"] != "json":
                raise SubstrateDeclarationError("surface is not a JSON document", key=key)
            path = self.path(key)
            if not path.is_file():
                self._cache[cache_key] = {}
            else:
                try:
                    parsed = json.loads(path.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError) as exc:
                    raise SubstrateUnavailableError(
                        "declared substrate surface is not readable JSON",
                        key=key,
                        locator=entry["locator"],
                        detail=str(exc),
                    ) from exc
                self._cache[cache_key] = parsed if isinstance(parsed, dict) else {}
        return self._cache[cache_key]

    def records(self, key: str) -> list[dict[str, Any]]:
        """The record array of a surface (``root_key``), or ``[]`` when absent."""
        entry = self.declaration(key)
        root_key = entry.get("root_key")
        if not root_key:
            return []
        rows = self.payload(key).get(root_key)
        if not isinstance(rows, list):
            return []
        return [row for row in rows if isinstance(row, dict)]

    def _directory_names(self, key: str) -> tuple[str, ...]:
        entry = self.declaration(key)
        path = self.path(key)
        if not path.is_dir():
            return ()
        pattern = entry.get("glob") or "*"
        return tuple(sorted(p.name for p in path.glob(pattern) if p.is_file()))

    def directory_names(self, key: str) -> tuple[str, ...]:
        cache_key = f"dirnames:{key}"
        if cache_key not in self._cache:
            self._cache[cache_key] = self._directory_names(key)
        return self._cache[cache_key]

    # -- determinism -----------------------------------------------------------

    def inventory(self) -> list[dict[str, Any]]:
        return [self.surface(k).to_dict() for k in self.keys()]

    def fingerprint(self) -> dict[str, str]:
        """Content fingerprint of every declared surface (identical state ⇒ identical)."""
        return {self.surface(k).locator: self.surface(k).content_sha256 for k in self.keys()}

    def missing_required(self) -> list[str]:
        return [k for k in self.keys() if self._entries[k]["required"] and not self.available(k)]


__all__ = [
    "SUBSTRATE_DECLARATION",
    "SubstrateReader",
    "SubstrateSurface",
]
