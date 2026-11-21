"""TASK-000011 — Registry domain models (EPIC-002).

Immutable, typed value objects mirroring the ``00-BOOK`` registry schemas
(``artifact.schema.json``, ``relationship.schema.json``, ``volume.schema.json``).
The models are a *read* projection: they parse defensively and never mutate the
underlying corpus (DP-03). Unknown fields are ignored so the append-only,
forward-compatible corpus (open vocabularies per UMB-006) can evolve without
breaking the adapter.

Parsing raises :class:`RegistryValidationError` (rooted in FoundationError) for
records that violate their required shape, so malformed input fails loudly and
auditably rather than silently producing partial objects.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from engine.registry.errors import RegistryValidationError


class LifecycleStatus(str, Enum):
    """Artifact/volume lifecycle status (artifact.schema.json ``status`` enum)."""

    NOT_STARTED = "NOT_STARTED"
    PLANNED = "PLANNED"
    IN_PROGRESS = "IN_PROGRESS"
    BLOCKED = "BLOCKED"
    UNDER_REVIEW = "UNDER_REVIEW"
    APPROVED = "APPROVED"
    IMPLEMENTED = "IMPLEMENTED"
    TESTED = "TESTED"
    CERTIFIED = "CERTIFIED"
    DEPLOYED = "DEPLOYED"
    PRODUCTION = "PRODUCTION"
    FROZEN = "FROZEN"
    SUPERSEDED = "SUPERSEDED"
    RETIRED = "RETIRED"
    ACTIVE = "ACTIVE"
    COMPLETE = "COMPLETE"
    FINAL = "FINAL"

    @classmethod
    def coerce(cls, value: Any, *, context: str) -> LifecycleStatus:
        """Return the enum member for ``value`` or raise a validation error."""
        try:
            return cls(str(value))
        except ValueError as exc:
            raise RegistryValidationError(
                "unknown lifecycle status", value=value, at=context
            ) from exc


# The thirteen ordered stages of the traceability chain (artifact.schema.json).
TRACE_STAGES: tuple[str, ...] = (
    "requirement",
    "architecture",
    "design",
    "implementation",
    "source_code",
    "unit_test",
    "integration_test",
    "functional_test",
    "security_test",
    "certification",
    "deployment",
    "production",
    "operations",
)


def _require(record: Mapping[str, Any], key: str, *, at: str) -> Any:
    if key not in record or record[key] is None:
        raise RegistryValidationError("required field missing", field=key, at=at)
    return record[key]


def _as_str(value: Any, *, field_name: str, at: str) -> str:
    if not isinstance(value, str) or not value:
        raise RegistryValidationError("expected a non-empty string", field=field_name, at=at)
    return value


def _as_int(value: Any, *, field_name: str, at: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise RegistryValidationError("expected an integer", field=field_name, at=at)
    return value


def _as_str_list(value: Any, *, field_name: str, at: str) -> tuple[str, ...]:
    if value is None:
        return ()
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        raise RegistryValidationError("expected an array of strings", field=field_name, at=at)
    return tuple(value)


@dataclass(frozen=True, slots=True)
class Traceability:
    """The requirement-to-operations traceability chain of an artifact."""

    stages: Mapping[str, tuple[str, ...]] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, raw: Any, *, at: str) -> Traceability:
        if raw is None:
            return cls(stages={stage: () for stage in TRACE_STAGES})
        if not isinstance(raw, Mapping):
            raise RegistryValidationError("traceability must be an object", at=at)
        stages = {
            stage: _as_str_list(raw.get(stage), field_name=f"traceability.{stage}", at=at)
            for stage in TRACE_STAGES
        }
        return cls(stages=stages)

    def stage(self, name: str) -> tuple[str, ...]:
        """Return the references recorded for a traceability ``name`` stage."""
        if name not in TRACE_STAGES:
            raise RegistryValidationError("unknown traceability stage", stage=name)
        return self.stages.get(name, ())

    def references(self) -> tuple[str, ...]:
        """Return every reference across all stages, de-duplicated and ordered."""
        seen: dict[str, None] = {}
        for stage in TRACE_STAGES:
            for ref in self.stages.get(stage, ()):
                seen.setdefault(ref, None)
        return tuple(seen)


@dataclass(frozen=True, slots=True)
class Artifact:
    """A single Universal Artifact record (artifact.schema.json)."""

    universal_id: str
    name: str
    volume: str
    page_start: int
    page_end: int
    status: LifecycleStatus
    version: str
    path: str
    native_id: str | None = None
    description: str = ""
    category: str = ""
    parent: str | None = None
    dependencies: tuple[str, ...] = ()
    program: str = ""
    owner: str = "UNASSIGNED"
    tags: tuple[str, ...] = ()
    return_link: str = ""
    content_hash: str | None = None
    traceability: Traceability = field(default_factory=Traceability)

    @classmethod
    def from_dict(cls, record: Mapping[str, Any]) -> Artifact:
        if not isinstance(record, Mapping):
            raise RegistryValidationError("artifact record must be an object")
        uid = _as_str(
            _require(record, "universal_id", at="artifact"),
            field_name="universal_id",
            at="artifact",
        )
        native = record.get("native_id")
        if native is not None and not isinstance(native, str):
            raise RegistryValidationError("native_id must be a string or null", at=uid)
        return cls(
            universal_id=uid,
            name=_as_str(_require(record, "name", at=uid), field_name="name", at=uid),
            volume=_as_str(_require(record, "volume", at=uid), field_name="volume", at=uid),
            page_start=_as_int(
                _require(record, "page_start", at=uid), field_name="page_start", at=uid
            ),
            page_end=_as_int(_require(record, "page_end", at=uid), field_name="page_end", at=uid),
            status=LifecycleStatus.coerce(_require(record, "status", at=uid), context=uid),
            version=_as_str(_require(record, "version", at=uid), field_name="version", at=uid),
            path=_as_str(_require(record, "path", at=uid), field_name="path", at=uid),
            native_id=native,
            description=record.get("description") or "",
            category=record.get("category") or "",
            parent=record.get("parent"),
            dependencies=_as_str_list(
                record.get("dependencies"), field_name="dependencies", at=uid
            ),
            program=record.get("program") or "",
            owner=record.get("owner") or "UNASSIGNED",
            tags=_as_str_list(record.get("tags"), field_name="tags", at=uid),
            return_link=record.get("return_link") or "",
            content_hash=record.get("content_hash"),
            traceability=Traceability.from_dict(record.get("traceability"), at=uid),
        )


@dataclass(frozen=True, slots=True)
class Relationship:
    """A first-class knowledge-graph edge (relationship.schema.json)."""

    edge_id: str
    source: str
    target: str
    type: str
    inverse_of: str | None = None
    note: str = ""

    @classmethod
    def from_dict(cls, record: Mapping[str, Any]) -> Relationship:
        if not isinstance(record, Mapping):
            raise RegistryValidationError("relationship record must be an object")
        edge_id = _as_str(
            _require(record, "edge_id", at="relationship"),
            field_name="edge_id",
            at="relationship",
        )
        inverse = record.get("inverse_of")
        if inverse is not None and not isinstance(inverse, str):
            raise RegistryValidationError("inverse_of must be a string or null", at=edge_id)
        return cls(
            edge_id=edge_id,
            source=_as_str(_require(record, "from", at=edge_id), field_name="from", at=edge_id),
            target=_as_str(_require(record, "to", at=edge_id), field_name="to", at=edge_id),
            type=_as_str(_require(record, "type", at=edge_id), field_name="type", at=edge_id),
            inverse_of=inverse,
            note=record.get("note") or "",
        )


@dataclass(frozen=True, slots=True)
class Volume:
    """A root Volume of the Universal Master Knowledge Book (volume.schema.json)."""

    volume_id: str
    serial: int
    name: str
    category: str
    status: LifecycleStatus
    description: str = ""
    artifact_count: int = 0
    page_range_start: int | None = None
    page_range_end: int | None = None
    index_path: str = ""

    @classmethod
    def from_dict(cls, record: Mapping[str, Any]) -> Volume:
        if not isinstance(record, Mapping):
            raise RegistryValidationError("volume record must be an object")
        vid = _as_str(
            _require(record, "volume_id", at="volume"),
            field_name="volume_id",
            at="volume",
        )
        page_start = record.get("page_range_start")
        page_end = record.get("page_range_end")
        if page_start is not None:
            page_start = _as_int(page_start, field_name="page_range_start", at=vid)
        if page_end is not None:
            page_end = _as_int(page_end, field_name="page_range_end", at=vid)
        return cls(
            volume_id=vid,
            serial=_as_int(_require(record, "serial", at=vid), field_name="serial", at=vid),
            name=_as_str(_require(record, "name", at=vid), field_name="name", at=vid),
            category=_as_str(_require(record, "category", at=vid), field_name="category", at=vid),
            status=LifecycleStatus.coerce(_require(record, "status", at=vid), context=vid),
            description=record.get("description") or "",
            artifact_count=record.get("artifact_count") or 0,
            page_range_start=page_start,
            page_range_end=page_end,
            index_path=record.get("index_path") or "",
        )


__all__ = [
    "LifecycleStatus",
    "TRACE_STAGES",
    "Traceability",
    "Artifact",
    "Relationship",
    "Volume",
]
