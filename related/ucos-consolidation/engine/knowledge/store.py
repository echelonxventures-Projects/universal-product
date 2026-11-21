"""UKDA Part 04/13 — Canonical Knowledge Store + in-memory Knowledge Base.

The single authoritative home for canonical knowledge. Knowledge is authored
**exactly once** here (the Knowledge Once Principle); everything else in the
repository is generated, derived, linked, validated, certified, or consumed from
this source.

    * :class:`KnowledgeBase` — an immutable, in-memory projection of the store:
      the canonical objects (Part 02) and decisions (Part 03), indexed for O(1)
      lookup and every classification query the higher layers need. It exposes the
      :class:`~engine.knowledge.graph.KnowledgeGraph` (Part 05) and rejects
      duplicate identities at authoring time (fail-closed against duplication).

    * :class:`KnowledgeStore` — a filesystem accessor that reads and writes the
      base as two deterministic JSON envelopes (``canonical-knowledge.json`` and
      ``decisions.json``). Writes are refused inside the frozen corpus (DP-03);
      serialization is stable (records sorted by id, no wall-clock) so a
      round-trip is byte-identical.
"""

from __future__ import annotations

import json
from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import TYPE_CHECKING, Any

from engine.foundation.guards.frozen_paths import find_frozen_writes
from engine.knowledge.cko import CanonicalKnowledgeObject, DecisionRecord
from engine.knowledge.errors import (
    DuplicateKnowledgeError,
    KnowledgeNotFoundError,
    KnowledgeSourceError,
)
from engine.knowledge.graph import KnowledgeGraph
from engine.knowledge.model import (
    KnowledgeAuthority,
    KnowledgeKind,
    Lifecycle,
)

if TYPE_CHECKING:  # pragma: no cover - typing only, avoids an import cycle
    # Deliberately not imported at module level here: engine.knowledge.ukip's package
    # __init__ eagerly imports assimilation.py, which imports this module — a real
    # circular import (confirmed by direct failure, not assumed). The two methods
    # that construct a ProvenanceChain import it locally, at call time, instead.
    from engine.knowledge.ukip.provenance import ProvenanceChain

#: Canonical store filenames and envelope schema identifiers.
CANON_FILE = "canonical-knowledge.json"
DECISIONS_FILE = "decisions.json"
HISTORY_FILE = "canonical-knowledge-history.json"
PROVENANCE_FILE = "provenance.json"
CANON_SCHEMA = "ucos-ukda-canonical-knowledge"
DECISIONS_SCHEMA = "ucos-ukda-decisions"
HISTORY_SCHEMA = "ucos-ukda-canonical-knowledge-history"
PROVENANCE_SCHEMA = "ucos-ukda-provenance"
STORE_VERSION = "1.0.0"

#: The default, mutable, non-corpus home for canonical knowledge (repo-root).
KNOWLEDGE_DIR = "knowledge"


def _repository_root() -> Path:
    """``engine/knowledge/store.py`` -> parents[2] is the repository root."""
    return Path(__file__).resolve().parents[2]


def default_store_dir() -> Path:
    """Return the default canonical knowledge directory (``<repo>/knowledge``)."""
    return _repository_root() / KNOWLEDGE_DIR


class KnowledgeBase:
    """An immutable, indexed projection of the canonical knowledge store."""

    __slots__ = ("_objects", "_decisions", "_by_object", "_by_decision")

    def __init__(
        self,
        objects: Iterable[CanonicalKnowledgeObject] = (),
        decisions: Iterable[DecisionRecord] = (),
    ) -> None:
        by_object: dict[str, CanonicalKnowledgeObject] = {}
        for obj in objects:
            if obj.cko_id in by_object:
                raise DuplicateKnowledgeError(
                    "canonical object authored more than once", cko_id=obj.cko_id
                )
            by_object[obj.cko_id] = obj
        by_decision: dict[str, DecisionRecord] = {}
        for dec in decisions:
            if dec.decision_id in by_decision:
                raise DuplicateKnowledgeError(
                    "decision authored more than once", decision_id=dec.decision_id
                )
            by_decision[dec.decision_id] = dec
        self._by_object = by_object
        self._by_decision = by_decision
        self._objects = tuple(by_object[k] for k in sorted(by_object))
        self._decisions = tuple(by_decision[k] for k in sorted(by_decision))

    # -- collections -----------------------------------------------------------

    def objects(self) -> tuple[CanonicalKnowledgeObject, ...]:
        return self._objects

    def decisions(self) -> tuple[DecisionRecord, ...]:
        return self._decisions

    def object_ids(self) -> tuple[str, ...]:
        return tuple(o.cko_id for o in self._objects)

    def decision_ids(self) -> tuple[str, ...]:
        return tuple(d.decision_id for d in self._decisions)

    def __len__(self) -> int:
        return len(self._objects) + len(self._decisions)

    # -- lookups ---------------------------------------------------------------

    def get_object(self, cko_id: str) -> CanonicalKnowledgeObject | None:
        return self._by_object.get(cko_id)

    def get_decision(self, decision_id: str) -> DecisionRecord | None:
        return self._by_decision.get(decision_id)

    def require_object(self, cko_id: str) -> CanonicalKnowledgeObject:
        obj = self._by_object.get(cko_id)
        if obj is None:
            raise KnowledgeNotFoundError("canonical object not found", cko_id=cko_id)
        return obj

    def require_decision(self, decision_id: str) -> DecisionRecord:
        dec = self._by_decision.get(decision_id)
        if dec is None:
            raise KnowledgeNotFoundError("decision not found", decision_id=decision_id)
        return dec

    def has_object(self, cko_id: str) -> bool:
        return cko_id in self._by_object

    def has_decision(self, decision_id: str) -> bool:
        return decision_id in self._by_decision

    # -- classification queries ------------------------------------------------

    def by_kind(self, kind: KnowledgeKind) -> tuple[CanonicalKnowledgeObject, ...]:
        return tuple(o for o in self._objects if o.kind is kind)

    def by_authority(self, authority: KnowledgeAuthority) -> tuple[CanonicalKnowledgeObject, ...]:
        return tuple(o for o in self._objects if o.authority is authority)

    def by_lifecycle(self, lifecycle: Lifecycle) -> tuple[CanonicalKnowledgeObject, ...]:
        return tuple(o for o in self._objects if o.lifecycle is lifecycle)

    def by_universe(self, universe: str) -> tuple[CanonicalKnowledgeObject, ...]:
        return tuple(o for o in self._objects if o.universe == universe)

    def by_owner(self, owner: str) -> tuple[CanonicalKnowledgeObject, ...]:
        return tuple(o for o in self._objects if o.owner == owner)

    def active_objects(self) -> tuple[CanonicalKnowledgeObject, ...]:
        return tuple(o for o in self._objects if o.is_active)

    # -- derived views ---------------------------------------------------------

    def graph(self) -> KnowledgeGraph:
        """The Universal Knowledge Graph projected from the canonical objects."""
        return KnowledgeGraph.from_objects(self._objects)

    # -- authoring (returns a new, immutable base) -----------------------------

    def with_object(self, obj: CanonicalKnowledgeObject) -> KnowledgeBase:
        """Return a new base with ``obj`` added, rejecting a duplicate identity."""
        if obj.cko_id in self._by_object:
            raise DuplicateKnowledgeError("canonical object already exists", cko_id=obj.cko_id)
        return KnowledgeBase((*self._objects, obj), self._decisions)

    def with_decision(self, dec: DecisionRecord) -> KnowledgeBase:
        """Return a new base with ``dec`` added, rejecting a duplicate identity."""
        if dec.decision_id in self._by_decision:
            raise DuplicateKnowledgeError("decision already exists", decision_id=dec.decision_id)
        return KnowledgeBase(self._objects, (*self._decisions, dec))

    def replace_object(self, obj: CanonicalKnowledgeObject) -> KnowledgeBase:
        """Return a new base with ``obj`` replacing the existing same-id object."""
        if obj.cko_id not in self._by_object:
            raise KnowledgeNotFoundError("canonical object not found", cko_id=obj.cko_id)
        others = [o for o in self._objects if o.cko_id != obj.cko_id]
        return KnowledgeBase((*others, obj), self._decisions)

    # -- serialization ---------------------------------------------------------

    def to_canon_document(self) -> dict[str, Any]:
        return {
            "schema": CANON_SCHEMA,
            "version": STORE_VERSION,
            "count": len(self._objects),
            "objects": [o.to_dict() for o in self._objects],
        }

    def to_decisions_document(self) -> dict[str, Any]:
        return {
            "schema": DECISIONS_SCHEMA,
            "version": STORE_VERSION,
            "count": len(self._decisions),
            "decisions": [d.to_dict() for d in self._decisions],
        }


def _records(document: Any, *, root_key: str, filename: str) -> list:
    if not isinstance(document, Mapping):
        raise KnowledgeSourceError("knowledge document root must be an object", filename=filename)
    records = document.get(root_key)
    if not isinstance(records, list):
        raise KnowledgeSourceError(
            "knowledge document is missing its records array",
            filename=filename,
            root_key=root_key,
        )
    return records


class KnowledgeStore:
    """A filesystem accessor for the canonical knowledge base (Part 04/13)."""

    __slots__ = ("_dir",)

    def __init__(self, store_dir: str | Path | None = None) -> None:
        self._dir = Path(store_dir).resolve() if store_dir is not None else default_store_dir()

    @property
    def directory(self) -> Path:
        return self._dir

    def _path(self, filename: str) -> Path:
        candidate = (self._dir / filename).resolve()
        if candidate != self._dir and self._dir not in candidate.parents:
            raise KnowledgeSourceError(
                "resolved path escapes the knowledge store", filename=filename
            )
        return candidate

    def exists(self) -> bool:
        return self._path(CANON_FILE).is_file()

    def _read_json(self, filename: str) -> Any:
        path = self._path(filename)
        if not path.is_file():
            raise KnowledgeSourceError(
                "knowledge data file not found", filename=filename, path=str(path)
            )
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise KnowledgeSourceError(
                "knowledge data file is not valid JSON", filename=filename, detail=str(exc)
            ) from exc

    def load(self) -> KnowledgeBase:
        """Read the canonical store into an immutable :class:`KnowledgeBase`."""
        canon = self._read_json(CANON_FILE)
        objects = [
            CanonicalKnowledgeObject.from_dict(r)
            for r in _records(canon, root_key="objects", filename=CANON_FILE)
        ]
        decisions: list[DecisionRecord] = []
        if self._path(DECISIONS_FILE).is_file():
            doc = self._read_json(DECISIONS_FILE)
            decisions = [
                DecisionRecord.from_dict(r)
                for r in _records(doc, root_key="decisions", filename=DECISIONS_FILE)
            ]
        return KnowledgeBase(objects, decisions)

    def _guard_writable(self) -> None:
        """Refuse to write anywhere inside the frozen corpus (DP-03)."""
        try:
            relative = self._dir.relative_to(_repository_root())
        except ValueError:
            return  # outside the repository (e.g. a test tmp dir) — allowed
        if find_frozen_writes([relative.as_posix()]):
            raise KnowledgeSourceError(
                "refusing to write canonical knowledge into the frozen corpus",
                directory=str(self._dir),
            )

    def _write_json(self, filename: str, document: Mapping[str, Any]) -> Path:
        path = self._path(filename)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(document, sort_keys=True, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        return path

    def save(self, base: KnowledgeBase) -> tuple[Path, Path]:
        """Write the base to the store as two deterministic JSON envelopes.

        Before either file is overwritten, any object already on disk whose content
        is about to change (or which is about to disappear from `base` entirely) is
        archived to `HISTORY_FILE` — `save()` no longer discards a prior version
        (P4-F-004, WP-UCDA-028). The live `CANON_FILE` still reflects only the
        current state, unchanged, exactly as `KnowledgeBase.replace_object()`'s real
        callers (`engine/runtime/bridge/bridge.py`, `engine/knowledge/integration/
        pipeline.py`) already rely on for their same-identity upsert pattern — this
        fix is entirely at the persistence boundary, not a change to that pattern.
        """
        self._guard_writable()
        self._dir.mkdir(parents=True, exist_ok=True)
        self._archive_replaced_versions(base)
        canon_path = self._write_json(CANON_FILE, base.to_canon_document())
        decisions_path = self._write_json(DECISIONS_FILE, base.to_decisions_document())
        return canon_path, decisions_path

    def _archive_replaced_versions(self, base: KnowledgeBase) -> None:
        """Append any on-disk object whose content is about to change to the history file."""
        if not self._path(CANON_FILE).is_file():
            return  # nothing on disk yet to lose
        try:
            current = self._read_json(CANON_FILE)
        except KnowledgeSourceError:
            return  # unreadable prior state cannot be archived; save() proceeds as before
        current_records = {
            r["cko_id"]: r
            for r in _records(current, root_key="objects", filename=CANON_FILE)
            if isinstance(r, Mapping) and r.get("cko_id")
        }
        incoming_hashes = {o.cko_id: o.content_sha256 for o in base.objects()}
        changed = [
            record
            for cko_id, record in current_records.items()
            if incoming_hashes.get(cko_id) != record.get("content_sha256")
        ]
        if not changed:
            return
        history_doc: dict[str, Any] = {"schema": HISTORY_SCHEMA, "version": STORE_VERSION}
        if self._path(HISTORY_FILE).is_file():
            try:
                history_doc = self._read_json(HISTORY_FILE)
            except KnowledgeSourceError:
                pass
        versions = history_doc.setdefault("versions", {})
        if not isinstance(versions, dict):
            versions = {}
            history_doc["versions"] = versions
        for record in changed:
            versions.setdefault(str(record["cko_id"]), []).append(record)
        self._write_json(HISTORY_FILE, history_doc)

    def history(self, cko_id: str) -> tuple[CanonicalKnowledgeObject, ...]:
        """Every prior version of `cko_id` archived by `save()`, oldest first.

        Empty when the object has never been overwritten, or `HISTORY_FILE` does not
        exist yet — never an error, matching `KnowledgeStore`'s existing fail-soft
        read discipline for optional files (see `DECISIONS_FILE` in `load()`).
        """
        if not self._path(HISTORY_FILE).is_file():
            return ()
        doc = self._read_json(HISTORY_FILE)
        versions = doc.get("versions") or {}
        records = versions.get(cko_id) or []
        return tuple(
            CanonicalKnowledgeObject.from_dict(r) for r in records if isinstance(r, Mapping)
        )

    # -- provenance persistence (P4-F-006, WP-UCDA-028) -------------------------

    def save_provenance(self, chains: Iterable[ProvenanceChain]) -> Path:
        """Persist provenance chains, keyed by their own `subject` field.

        Kept out of `CanonicalKnowledgeObject`'s content-addressed core deliberately
        — embedding a chain there would change every existing CKO's `content_sha256`
        and duplicate UKIP's own `ProvenanceChain` representation, the same reasoning
        `ADR-0016` already applied to knowledge confidence. This is a sibling file in
        the same store, using the same guard and write path as `CANON_FILE`/
        `DECISIONS_FILE` — not a new store.
        """
        self._guard_writable()
        self._dir.mkdir(parents=True, exist_ok=True)
        ordered = sorted(chains, key=lambda c: c.subject)
        document = {
            "schema": PROVENANCE_SCHEMA,
            "version": STORE_VERSION,
            "count": len(ordered),
            "chains": [c.to_dict() for c in ordered],
        }
        return self._write_json(PROVENANCE_FILE, document)

    def load_provenance(self) -> dict[str, ProvenanceChain]:
        """Every persisted provenance chain, keyed by subject. Empty if never saved."""
        # local import: see the TYPE_CHECKING block's note near the top of this file
        from engine.knowledge.ukip.provenance import ProvenanceChain

        if not self._path(PROVENANCE_FILE).is_file():
            return {}
        doc = self._read_json(PROVENANCE_FILE)
        chains = _records(doc, root_key="chains", filename=PROVENANCE_FILE)
        result: dict[str, ProvenanceChain] = {}
        for record in chains:
            chain = ProvenanceChain.from_dict(record)
            result[chain.subject] = chain
        return result


__all__ = [
    "CANON_FILE",
    "DECISIONS_FILE",
    "HISTORY_FILE",
    "PROVENANCE_FILE",
    "CANON_SCHEMA",
    "DECISIONS_SCHEMA",
    "HISTORY_SCHEMA",
    "PROVENANCE_SCHEMA",
    "STORE_VERSION",
    "KNOWLEDGE_DIR",
    "default_store_dir",
    "KnowledgeBase",
    "KnowledgeStore",
]
