"""UEG-000001 Part 04 — the environment fingerprint cache.

WHAT THIS CACHE IS ALLOWED TO DO, AND WHAT IT IS NOT. It may skip exactly one measurement:
EEG-06's scan of every pinned distribution's ``RECORD``, which is the only step in the gate
whose cost is measurable rather than microseconds. It may never skip a verdict, never supply
a check result, and never answer VALID on its own — a hit supplies the previous scan's
observed tool records and every check is then computed over them exactly as it would have
been over a fresh scan.

EEG-01 through EEG-05 are recomputed on EVERY invocation regardless of cache state. They are
in-process property reads, and they are the checks that catch a wrong interpreter — the one
condition a cache must never be able to hide.

THE TRIGGER KEY, AND ITS HONEST LIMIT. Deciding whether the dependency state changed without
scanning it requires a proxy, and the proxy is stated rather than implied: the interpreter
fingerprint, the configuration fingerprint (pyproject, the environment library, this
declaration, pyvenv.cfg), and the modification times of the site-packages and script
directories. Installing, removing or re-versioning a distribution rewrites a ``.dist-info``
directory and therefore moves the site-packages mtime, so every ordinary path through pip is
caught. What the proxy does NOT catch is an in-place edit of a file inside an already
installed package that leaves both directory mtimes untouched. Two things close that: the
installing entry points (``bootstrap.sh``, ``doctor.sh --fix``) invalidate the cache after
they run, and ``--refresh`` forces a full scan on demand.
"""

from __future__ import annotations

import json
import os
import sys
import sysconfig
from pathlib import Path
from typing import Any

from engine.execution_environment.discovery import configuration_fingerprint
from engine.execution_environment.model import (
    Declaration,
    ExecutionEnvironment,
    RuntimeIdentity,
    ToolRecord,
    _digest,
)

CACHE_VERSION = 1

STATE_HIT = "HIT"
STATE_MISS = "MISS"
STATE_STALE = "STALE"
STATE_DISABLED = "DISABLED"


def cache_path(repository: str | Path, declaration: Declaration) -> Path:
    """Return the declared cache location under *repository*."""
    return Path(repository) / declaration.cache_path


def _directory_mtime(path: Path) -> str:
    """Return *path*'s modification time as a string, or ABSENT.

    A directory rather than its contents: pip rewrites a ``.dist-info`` directory for every
    install, uninstall and version change, which moves the parent's mtime. Walking the tree
    instead would cost more than the scan this cache exists to avoid.
    """
    try:
        return f"{path.stat().st_mtime_ns}"
    except OSError:
        return "ABSENT"


def trigger_key(
    repository: str | Path, declaration: Declaration, venv_directory: str | Path
) -> str:
    """Return the digest of every declared invalidation trigger, computed cheaply.

    Deliberately excludes the repository commit: making it a trigger would invalidate the
    cache on every commit — that is, on every run — producing a cache that never hits and a
    false claim that the environment changed when only the source did.
    """
    runtime = RuntimeIdentity(
        language="python",
        version=sys.version,
        series=f"{sys.version_info[0]}.{sys.version_info[1]}",
        interpreter_path=str(Path(sys.executable).resolve()),
        prefix=str(Path(sys.prefix).resolve()),
        base_prefix=str(Path(sys.base_prefix).resolve()),
    )
    purelib = Path(sysconfig.get_path("purelib"))
    scripts = Path(sysconfig.get_path("scripts"))
    return _digest(
        f"v{CACHE_VERSION}",
        runtime.fingerprint,
        sys.version,
        configuration_fingerprint(repository, venv_directory),
        _directory_mtime(purelib),
        _directory_mtime(scripts),
    )


def load(path: str | Path) -> dict[str, Any] | None:
    """Return the cached payload, or None when it is absent or unusable.

    An unreadable or malformed cache is a MISS, never an error: a cache is an optimisation,
    and an optimisation that can fail a run is a liability. It is also never a pass.
    """
    try:
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(payload, dict) or payload.get("cache_version") != CACHE_VERSION:
        return None
    return payload


def reusable_tool_records(
    payload: dict[str, Any] | None, key: str
) -> tuple[ToolRecord, ...] | None:
    """Return the cached tool records iff *payload* was recorded under exactly *key*."""
    if payload is None or payload.get("trigger_key") != key:
        return None
    records: list[ToolRecord] = []
    for item in payload.get("tools", ()):
        try:
            records.append(
                ToolRecord(
                    name=item["name"],
                    distribution=item["distribution"],
                    expected_version=item["expected_version"],
                    installed_version=item["installed_version"],
                    importable=bool(item["importable"]),
                    declared_scripts=tuple(item.get("declared_scripts", ())),
                    missing_scripts=tuple(item.get("missing_scripts", ())),
                    non_executable_scripts=tuple(item.get("non_executable_scripts", ())),
                    record_readable=bool(item.get("record_readable", True)),
                )
            )
        except (KeyError, TypeError):
            return None
    return tuple(records) or None


def store(path: str | Path, environment: ExecutionEnvironment, key: str) -> Path:
    """Write the fingerprint for *environment* under *key*, atomically.

    Written through a temporary file and replaced, because a cache torn by an interrupted
    run would be read on the next one — and the whole point of the cache is to be trusted
    only when it is exactly what it claims to be.

    Stores what the declaration lists and nothing more: no timestamp, no commit, no machine
    path beyond the interpreter's own. A fingerprint carrying a clock is not a fingerprint.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    pytest_tool = environment.toolchain.tool("pytest")
    payload = {
        "cache_version": CACHE_VERSION,
        "trigger_key": key,
        "environment_id": environment.environment_id,
        "interpreter_fingerprint": environment.runtime.fingerprint,
        "python_version": environment.runtime.version,
        "pytest_version": pytest_tool.installed_version if pytest_tool else None,
        "dependency_fingerprint": environment.dependencies.fingerprint,
        "configuration_fingerprint": environment.repository.configuration_fingerprint,
        "repository": {
            "root": environment.repository.root,
            "branch": environment.repository.branch,
            "commit": environment.repository.commit,
        },
        "tools": [tool.as_dict() for tool in environment.toolchain.tools],
    }
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temporary, path)
    return path


def invalidate(path: str | Path) -> bool:
    """Delete the cache. Returns whether a cache was actually removed.

    Called by the entry points that INSTALL, which are the only acts that can change the
    dependency state in a way the trigger key's directory-mtime proxy could conceivably
    miss. Invalidating after a repair is cheaper and more honest than a proxy that tries to
    be exhaustive.
    """
    try:
        Path(path).unlink()
        return True
    except OSError:
        return False


__all__ = [
    "CACHE_VERSION",
    "STATE_DISABLED",
    "STATE_HIT",
    "STATE_MISS",
    "STATE_STALE",
    "cache_path",
    "invalidate",
    "load",
    "reusable_tool_records",
    "store",
    "trigger_key",
]
