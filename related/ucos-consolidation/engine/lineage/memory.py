"""ULP Part 05 — universal persistent evolutionary graph memory, resolved by projection.

Lineage answers **"how did this become this?"** for one family of relations at a time.
Memory answers the wider question **"what does the repository remember about this?"** — and
it answers it by asking the owners that already remember, in a declared order:

    identity → context → relationship → knowledge → evidence → decision → evolution

**This module is not a memory engine and must never become one.** It creates no store,
opens no counter, mints no identifier, declares no relation and writes no file. It obeys the
same law the rest of this package obeys, ``UCI-001 Part XVI.5``: *"lineage and evolution are
DERIVED projections over recorded history; no new store is created."* Every value it returns
cites the governed record it came from, so a caller can follow any answer back to the owner
that declared it. A value that cannot name its source is not returned.

The layer set is **data**, not code — ``engine/lineage/memory-layers.json``. A seven-member
layer set written into source would be an undisclosed finite assumption about how many kinds
of memory can exist (``ADR-0007``). Declared as data, an eighth layer is admitted by naming
its owner, its record and its access shape, with no code change here.

Two properties are load-bearing and are asserted by the verification suite rather than
assumed:

**Open world.** An unknown subject is not an error and not a guess. Every declared layer
resolves, and a layer with nothing recorded for that subject comes back empty with
``recorded=False``. The distinction between *"the owner records nothing"* and *"the record is
absent"* is kept, because collapsing them would hide a missing register behind a normal-
looking empty answer.

**No clock.** Ordering uses each owner's own recorded sequence. Where an owner records a
wall-clock string it is carried verbatim as opaque data and never parsed, compared or
normalised — parsing it would import a calendar, and ``engine/temporal/operations.py``
refuses a clock read for exactly that reason.
"""

from __future__ import annotations

import json
import os
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from engine.lineage.model import LineageError
from engine.lineage.sources import repo_root

#: The layer declaration. Data, so a future layer needs no code change here.
MEMORY_LAYERS_FILE = "memory-layers.json"

#: The access modes the declaration may name. Declared here because a mode is a SHAPE this
#: module can read, not a policy; a mode the declaration invents is refused rather than
#: silently ignored, so an unreadable layer can never masquerade as an empty one.
MODE_MAP_OF_LISTS = "map-of-lists"
MODE_LIST_MATCH = "list-match"
ACCESS_MODES: frozenset[str] = frozenset({MODE_MAP_OF_LISTS, MODE_LIST_MATCH})


def _require(entry: Mapping[str, Any], key: str, context: str) -> Any:
    value = entry.get(key)
    if value in (None, "", [], {}):
        raise LineageError(f"{context}: field {key!r} is absent or empty")
    return value


@dataclass(frozen=True, slots=True)
class MemoryAccess:
    """How one layer's record is read. A shape, never a policy."""

    mode: str
    at: tuple[str, ...]
    match_fields: tuple[str, ...]
    contains_fields: tuple[str, ...]
    kind_field: str
    sequence_field: str
    value_fields: tuple[str, ...]

    @classmethod
    def of(cls, entry: Mapping[str, Any], layer: str) -> MemoryAccess:
        mode = str(_require(entry, "mode", f"{layer} access"))
        if mode not in ACCESS_MODES:
            raise LineageError(
                f"{layer} access: mode {mode!r} is not a declared access mode "
                f"({sorted(ACCESS_MODES)})"
            )
        at = tuple(str(x) for x in _require(entry, "at", f"{layer} access"))
        match_fields = tuple(str(x) for x in entry.get("match_fields") or ())
        if mode == MODE_LIST_MATCH and not match_fields:
            raise LineageError(f"{layer} access: {MODE_LIST_MATCH} requires match_fields")
        return cls(
            mode=mode,
            at=at,
            match_fields=match_fields,
            contains_fields=tuple(str(x) for x in entry.get("contains_fields") or ()),
            kind_field=str(entry.get("kind_field") or ""),
            sequence_field=str(entry.get("sequence_field") or ""),
            value_fields=tuple(str(x) for x in entry.get("value_fields") or ()),
        )


@dataclass(frozen=True, slots=True)
class MemoryLayer:
    """One layer of memory: a question, the owner that answers it, and its record."""

    layer: str
    ordinal: int
    question: str
    owner: str
    record: str
    access: MemoryAccess

    @classmethod
    def of(cls, entry: Mapping[str, Any]) -> MemoryLayer:
        layer = str(_require(entry, "layer", "layer"))
        return cls(
            layer=layer,
            ordinal=int(_require(entry, "ordinal", layer)),
            question=str(_require(entry, "question", layer)),
            owner=str(_require(entry, "owner", layer)),
            record=str(_require(entry, "record", layer)),
            access=MemoryAccess.of(_require(entry, "access", layer), layer),
        )


@dataclass(frozen=True, slots=True)
class MemoryDeclaration:
    """The declared layer set, rehydrated and structurally usable."""

    declaration_id: str
    layers: tuple[MemoryLayer, ...]

    @classmethod
    def of(cls, document: Mapping[str, Any]) -> MemoryDeclaration:
        layers = tuple(
            MemoryLayer.of(entry) for entry in _require(document, "layers", "memory declaration")
        )
        seen: set[str] = set()
        for layer in layers:
            if layer.layer in seen:
                raise LineageError(f"layer {layer.layer!r} is declared twice")
            seen.add(layer.layer)
        ordinals = [layer.ordinal for layer in layers]
        if len(set(ordinals)) != len(ordinals):
            raise LineageError("two layers share one ordinal; the resolution order is ambiguous")
        return cls(
            declaration_id=str(_require(document, "declaration_id", "memory declaration")),
            layers=tuple(sorted(layers, key=lambda x: x.ordinal)),
        )

    @property
    def names(self) -> tuple[str, ...]:
        """Every declared layer, in resolution order."""
        return tuple(layer.layer for layer in self.layers)

    def layer_of(self, name: str) -> MemoryLayer | None:
        for layer in self.layers:
            if layer.layer == name:
                return layer
        return None

    def extend(self, layer: MemoryLayer) -> MemoryDeclaration:
        """The declaration with one further layer. Returns a NEW declaration; mutates none.

        This is the extensibility path ``ADR-0013`` claims: a layer the repository has never
        named is admitted here without amending this module.
        """
        return MemoryDeclaration.of(
            {
                "declaration_id": self.declaration_id,
                "layers": [_layer_document(x) for x in (*self.layers, layer)],
            }
        )


def _layer_document(layer: MemoryLayer) -> dict[str, Any]:
    access: dict[str, Any] = {"mode": layer.access.mode, "at": list(layer.access.at)}
    if layer.access.match_fields:
        access["match_fields"] = list(layer.access.match_fields)
    if layer.access.contains_fields:
        access["contains_fields"] = list(layer.access.contains_fields)
    if layer.access.kind_field:
        access["kind_field"] = layer.access.kind_field
    if layer.access.sequence_field:
        access["sequence_field"] = layer.access.sequence_field
    if layer.access.value_fields:
        access["value_fields"] = list(layer.access.value_fields)
    return {
        "layer": layer.layer,
        "ordinal": layer.ordinal,
        "question": layer.question,
        "owner": layer.owner,
        "record": layer.record,
        "access": access,
    }


@dataclass(frozen=True, slots=True)
class MemoryEntry:
    """One remembered fact, carrying the owner and the record that declared it.

    ``values`` holds the owner's own fields verbatim. Nothing is renamed into a vocabulary
    this layer would then own, and nothing is parsed — a wall-clock string an owner recorded
    stays a string.
    """

    layer: str
    subject: str
    kind: str
    sequence: int
    owner: str
    source: str
    values: tuple[tuple[str, str], ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "kind": self.kind,
            "layer": self.layer,
            "owner": self.owner,
            "sequence": self.sequence,
            "source": self.source,
            "subject": self.subject,
            "values": {k: v for k, v in self.values},
        }


@dataclass(frozen=True, slots=True)
class LayerMemory:
    """One layer's answer for one subject, including the honest empty answer."""

    layer: str
    question: str
    owner: str
    source: str
    record_present: bool
    entries: tuple[MemoryEntry, ...]

    @property
    def recorded(self) -> bool:
        """Whether the owner records anything about this subject in this layer."""
        return bool(self.entries)

    def as_dict(self) -> dict[str, Any]:
        return {
            "entries": [e.as_dict() for e in self.entries],
            "layer": self.layer,
            "owner": self.owner,
            "question": self.question,
            "record_present": self.record_present,
            "recorded": self.recorded,
            "source": self.source,
        }


@dataclass(frozen=True, slots=True)
class SubjectMemory:
    """Everything the repository remembers about one subject, layer by layer.

    Derived truth. It owns nothing it reports, and it reports nothing it cannot source.
    """

    subject: str
    declaration_id: str
    layers: tuple[LayerMemory, ...]

    def layer(self, name: str) -> LayerMemory | None:
        for found in self.layers:
            if found.layer == name:
                return found
        return None

    def entries(self) -> tuple[MemoryEntry, ...]:
        """Every entry across every layer, in declared resolution order."""
        return tuple(entry for layer in self.layers for entry in layer.entries)

    def recorded_layers(self) -> tuple[str, ...]:
        return tuple(x.layer for x in self.layers if x.recorded)

    def empty_layers(self) -> tuple[str, ...]:
        return tuple(x.layer for x in self.layers if not x.recorded)

    def absent_records(self) -> tuple[str, ...]:
        """Layers whose governed record is not present at all — a different fact from empty."""
        return tuple(x.layer for x in self.layers if not x.record_present)

    @property
    def is_remembered(self) -> bool:
        """Whether any layer remembers this subject."""
        return any(x.recorded for x in self.layers)

    def sources(self) -> tuple[str, ...]:
        """Every governed record consulted, deduplicated and ordered."""
        return tuple(sorted({x.source for x in self.layers}))

    def as_dict(self) -> dict[str, Any]:
        return {
            "declaration_id": self.declaration_id,
            "empty_layers": list(self.empty_layers()),
            "is_remembered": self.is_remembered,
            "layers": [x.as_dict() for x in self.layers],
            "recorded_layers": list(self.recorded_layers()),
            "subject": self.subject,
        }


# -- declaration loading ---------------------------------------------------- #


def load_declaration(path: str | None = None) -> MemoryDeclaration:
    """Read the layer declaration. Reads only."""
    target = path or os.path.join(os.path.dirname(os.path.abspath(__file__)), MEMORY_LAYERS_FILE)
    try:
        with open(target, encoding="utf-8") as handle:
            document = json.load(handle)
    except FileNotFoundError:
        raise LineageError("the memory layer declaration is absent", subject=target) from None
    except json.JSONDecodeError as error:
        raise LineageError(f"the memory layer declaration is not valid JSON ({error})") from None
    return MemoryDeclaration.of(document)


# -- record reading --------------------------------------------------------- #


def _read_record(repo: str, relpath: str) -> Any | None:
    """Read one owner's record. An absent record is a fact, not a fault."""
    target = os.path.join(repo, relpath)
    try:
        with open(target, encoding="utf-8") as handle:
            return json.load(handle)
    except FileNotFoundError:
        return None
    except json.JSONDecodeError as error:
        raise LineageError(
            f"a memory record is not valid JSON ({error})", subject=relpath
        ) from None


def _descend(document: Any, at: Sequence[str]) -> Any | None:
    found: Any = document
    for step in at:
        if not isinstance(found, Mapping) or step not in found:
            return None
        found = found[step]
    return found


def _scalar(value: Any) -> str:
    """Render one field as an opaque string. Never parsed, never normalised."""
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int | float):
        return str(value)
    if isinstance(value, Mapping):
        return json.dumps({str(k): _scalar(v) for k, v in sorted(value.items())}, sort_keys=True)
    if isinstance(value, Iterable):
        return json.dumps([_scalar(v) for v in value])
    return str(value)


def _values(record: Mapping[str, Any], fields: Sequence[str]) -> tuple[tuple[str, str], ...]:
    chosen = fields or tuple(sorted(str(k) for k in record))
    return tuple((str(f), _scalar(record.get(f))) for f in chosen if f in record)


def _sequence(record: Mapping[str, Any], field: str, fallback: int) -> int:
    if not field:
        return fallback
    raw = record.get(field)
    if isinstance(raw, bool) or raw is None:
        return fallback
    if isinstance(raw, int):
        return raw
    if isinstance(raw, str) and raw.strip().lstrip("-").isdigit():
        return int(raw.strip())
    return fallback


def _matches(record: Mapping[str, Any], subject: str, access: MemoryAccess) -> bool:
    for field in access.match_fields:
        if field in record and _scalar(record.get(field)) == subject:
            return True
    for field in access.contains_fields:
        raw = record.get(field)
        if isinstance(raw, str):
            if raw == subject:
                return True
        elif isinstance(raw, Iterable) and not isinstance(raw, Mapping):
            if any(_scalar(item) == subject for item in raw):
                return True
    return False


def _entries_for(subject: str, layer: MemoryLayer, document: Any) -> tuple[MemoryEntry, ...]:
    access = layer.access
    holder = _descend(document, access.at)
    if holder is None:
        return ()
    found: list[MemoryEntry] = []

    if access.mode == MODE_MAP_OF_LISTS:
        if not isinstance(holder, Mapping):
            return ()
        recorded = holder.get(subject)
        if recorded is None:
            return ()
        rows = recorded if isinstance(recorded, list) else [recorded]
        for position, row in enumerate(rows, start=1):
            if not isinstance(row, Mapping):
                continue
            found.append(
                MemoryEntry(
                    layer=layer.layer,
                    subject=subject,
                    kind=_scalar(row.get(access.kind_field)) if access.kind_field else "",
                    sequence=_sequence(row, access.sequence_field, position),
                    owner=layer.owner,
                    source=layer.record,
                    values=_values(row, access.value_fields),
                )
            )
    else:  # MODE_LIST_MATCH
        rows = holder if isinstance(holder, list) else list(holder.values())
        position = 0
        for row in rows:
            if not isinstance(row, Mapping) or not _matches(row, subject, access):
                continue
            position += 1
            found.append(
                MemoryEntry(
                    layer=layer.layer,
                    subject=subject,
                    kind=_scalar(row.get(access.kind_field)) if access.kind_field else "",
                    sequence=_sequence(row, access.sequence_field, position),
                    owner=layer.owner,
                    source=layer.record,
                    values=_values(row, access.value_fields),
                )
            )

    # Deterministic order from the owner's own sequence, then by rendered content. No clock.
    return tuple(sorted(found, key=lambda e: (e.sequence, e.kind, e.values)))


# -- the resolution surface ------------------------------------------------- #


def resolve(
    subject: str,
    *,
    repo: str | None = None,
    declaration: MemoryDeclaration | None = None,
) -> SubjectMemory:
    """Resolve every declared memory layer for one subject.

    Open world by construction: an unknown subject yields a complete answer in which every
    layer is present and empty. It never raises for an unknown subject, and it never invents
    an entry. A layer whose governed record is absent is reported ``record_present=False``,
    which is a different fact from the owner recording nothing.
    """
    repo = repo or repo_root()
    declaration = declaration or load_declaration()
    subject = str(subject)

    layers: list[LayerMemory] = []
    for layer in declaration.layers:
        document = _read_record(repo, layer.record)
        layers.append(
            LayerMemory(
                layer=layer.layer,
                question=layer.question,
                owner=layer.owner,
                source=layer.record,
                record_present=document is not None,
                entries=() if document is None else _entries_for(subject, layer, document),
            )
        )

    return SubjectMemory(
        subject=subject,
        declaration_id=declaration.declaration_id,
        layers=tuple(layers),
    )


def owners(declaration: MemoryDeclaration | None = None) -> dict[str, str]:
    """Which owner answers which layer. The ownership map, derived from the declaration."""
    declaration = declaration or load_declaration()
    return {layer.layer: layer.owner for layer in declaration.layers}


def duplicate_owners(declaration: MemoryDeclaration | None = None) -> dict[str, list[str]]:
    """Any owner claiming more than one layer for the SAME record — a duplication check.

    Two layers may lawfully share a record while asking different questions (knowledge and
    evidence both read the canonical knowledge register). What may not happen is one
    ``(owner, record)`` pair answering two layers, because that would be one authority
    holding one concern twice.
    """
    declaration = declaration or load_declaration()
    claims: dict[str, list[str]] = {}
    for layer in declaration.layers:
        claims.setdefault(f"{layer.owner}|{layer.record}", []).append(layer.layer)
    return {k: sorted(v) for k, v in sorted(claims.items()) if len(v) > 1}


def reconstruct(
    subject: str,
    *,
    repo: str | None = None,
    declaration: MemoryDeclaration | None = None,
) -> SubjectMemory:
    """Resolve twice and prove the two resolutions are identical.

    Historical reconstruction is only meaningful if it is repeatable. Because nothing here
    reads a clock or a random source, two resolutions over an unchanged repository must be
    byte-identical; if they are not, the projection has acquired hidden state and says so.
    """
    first = resolve(subject, repo=repo, declaration=declaration)
    second = resolve(subject, repo=repo, declaration=declaration)
    if first.as_dict() != second.as_dict():
        raise LineageError("memory resolution is not deterministic", subject=subject)
    return first


def declaration_document(declaration: MemoryDeclaration | None = None) -> dict[str, Any]:
    """The declared layer set as a portable document — the "graph restore" half of REQ-43.

    THIS CAPABILITY WAS CERTIFIED IN A CHECKLIST AND IMPLEMENTED NOWHERE.
    ``test_req_43_upeg_certification.py`` asserts "Declaration serializable to document" and
    aggregates that assertion into a certification checklist whose docstring reads
    "REQ-43 CERTIFIED (UPEG operational)". The only serializer in this module took a
    :class:`SubjectMemory` — a RESOLUTION — so the test called it with a declaration, raised
    ``TypeError``, and had been failing for long enough that the whole suite was red. A
    certification checklist that cannot run certifies nothing, and the gap it hid was real:
    there was no way to export the declared layer set at all.

    Round-trippable by construction: every key here is one :meth:`MemoryLayer.of` requires, so
    ``MemoryDeclaration.of(declaration_document(d))`` reconstructs ``d``. That is what makes
    this a restore path rather than a report.

    Emits no timestamp and reads no clock, so two calls over one declaration produce identical
    bytes.
    """
    declaration = declaration or load_declaration()
    return {
        "schema": "ucos-ulp-memory-declaration",
        "version": "1.0.0",
        "authority": "NONE — DERIVED TRUTH; a projection of the declared layer set",
        "projection_of": MEMORY_LAYERS_FILE,
        "declaration_id": declaration.declaration_id,
        "layers": [
            {
                "layer": layer.layer,
                "ordinal": layer.ordinal,
                "question": layer.question,
                "owner": layer.owner,
                "record": layer.record,
                "access": {
                    "mode": layer.access.mode,
                    "at": list(layer.access.at),
                    "match_fields": list(layer.access.match_fields),
                    "contains_fields": list(layer.access.contains_fields),
                    "kind_field": layer.access.kind_field,
                    "sequence_field": layer.access.sequence_field,
                    "value_fields": list(layer.access.value_fields),
                },
            }
            for layer in declaration.layers
        ],
    }


def to_document(memory: SubjectMemory) -> dict[str, Any]:
    """The resolution as a portable document. Emits no timestamp, so it is replayable."""
    return {
        "schema": "ucos-ulp-subject-memory",
        "version": "1.0.0",
        "authority": "NONE — DERIVED TRUTH; a projection over located owners",
        "projection_of": "engine/lineage/memory-layers.json",
        "memory": memory.as_dict(),
    }


__all__ = [
    "ACCESS_MODES",
    "MEMORY_LAYERS_FILE",
    "MODE_LIST_MATCH",
    "MODE_MAP_OF_LISTS",
    "LayerMemory",
    "MemoryAccess",
    "MemoryDeclaration",
    "MemoryEntry",
    "MemoryLayer",
    "SubjectMemory",
    "duplicate_owners",
    "load_declaration",
    "owners",
    "reconstruct",
    "resolve",
    "declaration_document",
    "to_document",
]
