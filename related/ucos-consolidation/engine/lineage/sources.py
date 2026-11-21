"""ULP Part 02 — the source authorities, read and never written.

Six governed records answer lineage between them. This module reads them and does nothing
else: it opens no counter, writes no file and holds no cache that outlives a call.

Each source keeps its own meaning. ``artifacts.json`` owns containment, the change ledger
owns supersession and transformation, the generated-artifact registry owns derivation, and
the declared metadata rows — already projected into ``relationships.json`` — own dependency.
The projection composes them; it never merges them into one relation.

The relation VOCABULARY is read from its owner, ``00-BOOK/tools/config.py``, rather than
restated here. That file is a tool outside the ``engine`` package, so it is loaded by path;
importing the owner is what keeps the classification honest, because a relation this layer
names but the owner does not declare is then a load-time failure rather than a silent
invention.
"""

from __future__ import annotations

import importlib.util
import json
import os
from typing import Any

from engine.lineage.model import LineageError

_ARTIFACTS = os.path.join("00-BOOK", "DATA", "artifacts.json")
_RELATIONSHIPS = os.path.join("00-BOOK", "DATA", "relationships.json")
_CHANGE_LEDGER = os.path.join("00-BOOK", "DATA", "change-ledger.json")
_GENERATED = os.path.join("00-BOOK", "DATA", "generated-artifact-registry.json")
_BIRTHS = os.path.join("00-MASTER", "UOBC-000001", "birth-ledger.json")
_ID_LEDGER = os.path.join("00-BOOK", "DATA", "id-ledger.json")
_VOCABULARY = os.path.join("00-BOOK", "tools", "config.py")

#: Every source this projection reads, in the order it reads them. Named so the report can
#: say what it composed rather than leaving a reader to infer it from the code.
SOURCE_FILES: tuple[str, ...] = (
    _ARTIFACTS,
    _RELATIONSHIPS,
    _CHANGE_LEDGER,
    _GENERATED,
    _BIRTHS,
    _ID_LEDGER,
)


def repo_root() -> str:
    """The repository root, derived from this file's location."""
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _read_json(repo: str, relpath: str, *, required: bool) -> Any:
    target = os.path.join(repo, relpath)
    try:
        with open(target, encoding="utf-8") as handle:
            return json.load(handle)
    except FileNotFoundError:
        if required:
            raise LineageError("a declared lineage source is absent", subject=relpath) from None
        return None
    except json.JSONDecodeError as error:
        raise LineageError(
            f"a lineage source is not valid JSON ({error})", subject=relpath
        ) from None


def primary_relations(repo: str | None = None) -> frozenset[str]:
    """The FORWARD relation of each declared inverse pair, per the vocabulary owner.

    ``RELATIONSHIP_TYPES`` declares each pair as ``type`` (forward) and ``inverse``. An
    ancestry FACT is expressed twice in the corpus graph — once per direction — so the
    projection keeps the forward name and reports the fact once. Which name is forward is
    the owner's decision, read here rather than chosen.
    """
    return frozenset(str(spec["type"]) for spec in _vocabulary(repo))


def _vocabulary(repo: str | None = None) -> list[Any]:
    """The owner's RELATIONSHIP_TYPES list, loaded by path."""
    repo = repo or repo_root()
    target = os.path.join(repo, _VOCABULARY)
    spec = importlib.util.spec_from_file_location("_ulp_vocabulary", target)
    if spec is None or spec.loader is None:
        raise LineageError("the relationship vocabulary cannot be loaded", subject=_VOCABULARY)
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except Exception as error:  # pragma: no cover - a broken owner is a fault, not a verdict
        raise LineageError(f"the relationship vocabulary failed to load ({error})") from None
    types = getattr(module, "RELATIONSHIP_TYPES", None)
    if not types:
        raise LineageError("the vocabulary owner declares no RELATIONSHIP_TYPES")
    return list(types)


def declared_relations(repo: str | None = None) -> frozenset[str]:
    """Every directed relation name the corpus vocabulary OWNER declares.

    Loaded from ``00-BOOK/tools/config.py`` by path. Returning the owner's own set is what
    lets the classification be checked rather than trusted.
    """
    names: set[str] = set()
    for spec_entry in _vocabulary(repo):
        names.add(str(spec_entry["type"]))
        names.add(str(spec_entry["inverse"]))
    return frozenset(names)


def load_sources(repo: str | None = None) -> dict[str, Any]:
    """Read every governed source the projection composes. Reads only."""
    repo = repo or repo_root()
    artifacts_doc = _read_json(repo, _ARTIFACTS, required=True) or {}
    artifacts = artifacts_doc.get("artifacts") or []
    artifacts = list(artifacts) if isinstance(artifacts, list) else list(artifacts.values())

    relationships_doc = _read_json(repo, _RELATIONSHIPS, required=True) or {}
    edges = relationships_doc.get("relationships") or []

    change_doc = _read_json(repo, _CHANGE_LEDGER, required=True) or {}
    generated_doc = _read_json(repo, _GENERATED, required=True) or {}
    births_doc = _read_json(repo, _BIRTHS, required=False) or {}
    id_ledger = _read_json(repo, _ID_LEDGER, required=False) or {}

    return {
        "repo": repo,
        "artifacts": artifacts,
        "artifacts_by_id": {a["universal_id"]: a for a in artifacts if a.get("universal_id")},
        "edges": list(edges) if isinstance(edges, list) else list(edges.values()),
        "change_events": list(change_doc.get("change_events") or []),
        "change_lineage": dict(change_doc.get("lineage") or {}),
        "generated": list(generated_doc.get("entries") or []),
        "births": dict(births_doc.get("births") or {}),
        "history": dict(id_ledger.get("history") or {}),
    }


__all__ = [
    "SOURCE_FILES",
    "declared_relations",
    "load_sources",
    "primary_relations",
    "repo_root",
]
