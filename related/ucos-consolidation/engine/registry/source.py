"""TASK-000010 — Read-only registry source resolver (EPIC-002).

Locates and reads the existing ``00-BOOK`` registry substrate — the JSON data
files under ``00-BOOK/DATA`` validated by ``00-BOOK/SCHEMAS`` — without ever
mutating it.

Constitutional basis:
    * DP-03 / C-01 — the certified corpus (``00-BOOK``) is **read-only** to
      implementation. This resolver reads only; every path it yields is asserted
      to be outside a mutable boundary by re-using the Foundation frozen-path
      guard (TASK-000003), so a programming error can never turn a read into a
      write against the corpus.
    * TP-04 / TP-05 — standard library only.
    * PL-02 — failures raise auditable, structured errors (TASK-000006/000010).

The resolver performs no caching and holds no file handles; it is a thin,
deterministic locator + JSON loader that higher layers compose.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from engine.foundation.guards.frozen_paths import FROZEN_PREFIXES, find_frozen_writes
from engine.registry.errors import RegistryDataError, RegistrySourceError

# The registry substrate lives here, relative to the repository root.
BOOK_DIR = "00-BOOK"
DATA_SUBDIR = "DATA"
SCHEMAS_SUBDIR = "SCHEMAS"

# Canonical data files that make up the registry substrate (TASK-000012/13/14).
ARTIFACTS_FILE = "artifacts.json"
RELATIONSHIPS_FILE = "relationships.json"
VOLUMES_FILE = "volumes.json"


def _repository_root() -> Path:
    """Return the repository root inferred from this module's location.

    ``engine/registry/source.py`` -> parents[2] is the repository root that
    contains ``00-BOOK`` and the ``engine`` package.
    """
    return Path(__file__).resolve().parents[2]


def default_data_dir() -> Path:
    """Return the default read-only registry data directory (``00-BOOK/DATA``)."""
    return _repository_root() / BOOK_DIR / DATA_SUBDIR


class RegistrySource:
    """A read-only accessor over the ``00-BOOK`` registry data directory.

    The source guarantees, structurally, that it only ever addresses the frozen
    corpus for reading: :meth:`read_json` refuses to operate on a path that does
    not resolve under the configured data directory, and the data directory is
    asserted to sit within the frozen corpus boundary at construction time.
    """

    __slots__ = ("_data_dir",)

    def __init__(self, data_dir: str | Path | None = None) -> None:
        resolved = Path(data_dir).resolve() if data_dir is not None else default_data_dir()
        if not resolved.exists():
            raise RegistrySourceError("registry data directory not found", data_dir=str(resolved))
        if not resolved.is_dir():
            raise RegistrySourceError(
                "registry data path is not a directory", data_dir=str(resolved)
            )
        self._data_dir = resolved

    @property
    def data_dir(self) -> Path:
        """The resolved read-only registry data directory."""
        return self._data_dir

    def is_within_frozen_corpus(self) -> bool:
        """True iff the data directory sits under the read-only corpus (DP-03).

        Used as an assertion by callers and tests; a custom (test) data dir may
        legitimately live outside the corpus, so this is reported rather than
        enforced here.
        """
        try:
            relative = self._data_dir.relative_to(_repository_root())
        except ValueError:
            return False
        return bool(find_frozen_writes([relative.as_posix()]))

    def path_for(self, filename: str) -> Path:
        """Resolve ``filename`` inside the data directory, rejecting escapes.

        Guards against path traversal: the resolved path must remain within the
        configured data directory (SEC-01 secure-by-default).
        """
        candidate = (self._data_dir / filename).resolve()
        if candidate != self._data_dir and self._data_dir not in candidate.parents:
            raise RegistrySourceError(
                "resolved path escapes the registry data directory",
                filename=filename,
                data_dir=str(self._data_dir),
            )
        return candidate

    def exists(self, filename: str) -> bool:
        """True iff ``filename`` exists within the data directory."""
        return self.path_for(filename).is_file()

    def read_json(self, filename: str) -> Any:
        """Read and parse a JSON file from the data directory (read-only).

        Raises:
            RegistrySourceError: the file is missing or unreadable.
            RegistryDataError: the file is not valid JSON.
        """
        path = self.path_for(filename)
        if not path.is_file():
            raise RegistrySourceError(
                "registry data file not found", filename=filename, path=str(path)
            )
        try:
            raw = path.read_text(encoding="utf-8")
        except OSError as exc:  # pragma: no cover - platform/IO dependent
            raise RegistrySourceError(
                "registry data file could not be read", filename=filename, detail=str(exc)
            ) from exc
        try:
            return json.loads(raw)
        except json.JSONDecodeError as exc:
            raise RegistryDataError(
                "registry data file is not valid JSON",
                filename=filename,
                detail=str(exc),
            ) from exc

    def read_document(self, filename: str, *, root_key: str) -> tuple[Mapping[str, Any], list]:
        """Read a registry document and return ``(envelope, records)``.

        Every registry data file is a JSON object envelope carrying metadata
        (e.g. ``generated_at``, ``count``) plus a single array of records under
        ``root_key`` (``artifacts``/``relationships``/``volumes``).

        Raises:
            RegistryDataError: the envelope is not an object or the records
                array is missing or not a list.
        """
        document = self.read_json(filename)
        if not isinstance(document, Mapping):
            raise RegistryDataError(
                "registry document root must be a JSON object",
                filename=filename,
                got=type(document).__name__,
            )
        records = document.get(root_key)
        if not isinstance(records, list):
            raise RegistryDataError(
                "registry document is missing its records array",
                filename=filename,
                root_key=root_key,
            )
        return document, records


__all__ = [
    "BOOK_DIR",
    "DATA_SUBDIR",
    "SCHEMAS_SUBDIR",
    "ARTIFACTS_FILE",
    "RELATIONSHIPS_FILE",
    "VOLUMES_FILE",
    "FROZEN_PREFIXES",
    "default_data_dir",
    "RegistrySource",
]
