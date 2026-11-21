"""UCOS-URTF-001 — Subject projection from declared Truth documents.

Every project keeps its population somewhere: a concept model, a capability inventory, a
registry export, a gap register. Historically each engine grew its own reader bound to one
file name and one schema. This module removes that coupling: a :class:`ProjectionSpec`
*declares* where the population lives inside any JSON document, and
:class:`SubjectProjection` turns it into
:class:`~platform.universal_truth.contracts.Subject` values that every Foundation
framework already consumes.

The projection reads Truth and never authors it. It fabricates nothing: a record missing
its declared identity field fails closed rather than being silently dropped or invented.
"""

from __future__ import annotations

import json
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from platform.foundation.contracts import content_hash
from platform.universal_truth.contracts import Subject
from platform.universal_truth.errors import TruthProjectionError
from typing import Any


def _walk(document: Mapping[str, Any], pointer: str) -> Any:
    """Resolve a dotted ``pointer`` inside ``document`` (declared, not guessed)."""
    node: Any = document
    for part in pointer.split("."):
        if not isinstance(node, Mapping) or part not in node:
            raise TruthProjectionError("declared collection not found", pointer=pointer)
        node = node[part]
    return node


def _flatten(value: Any) -> tuple[str, ...]:
    """Flatten a declared locator field into a tuple of strings, honestly."""
    if value is None:
        return ()
    if isinstance(value, str):
        return (value,) if value.strip() else ()
    if isinstance(value, Mapping):
        return tuple(item for key in sorted(value) for item in _flatten(value[key]))
    if isinstance(value, Iterable):
        return tuple(item for element in value for item in _flatten(element))
    return (str(value),)


@dataclass(frozen=True, slots=True)
class ProjectionSpec:
    """A declaration of where a population lives inside a Truth document."""

    collection: str
    identity_field: str
    locator_fields: tuple[str, ...] = ()
    attribute_fields: tuple[str, ...] = ()
    role_fields: tuple[tuple[str, tuple[str, ...]], ...] = ()
    spec_id: str = ""

    @classmethod
    def create(
        cls,
        collection: str,
        identity_field: str,
        *,
        locator_fields: Iterable[str] = (),
        attribute_fields: Iterable[str] = (),
        role_fields: Mapping[str, Iterable[str]] | None = None,
    ) -> ProjectionSpec:
        """Build a validated projection specification with a content-addressed identity."""
        if not isinstance(collection, str) or not collection.strip():
            raise TruthProjectionError("projection requires a collection pointer")
        if not isinstance(identity_field, str) or not identity_field.strip():
            raise TruthProjectionError("projection requires an identity field")
        locators = tuple(str(item) for item in locator_fields if str(item).strip())
        attributes = tuple(str(item) for item in attribute_fields if str(item).strip())
        roles: dict[str, tuple[str, ...]] = {}
        for name, fields in dict(role_fields or {}).items():
            role_name = str(name).strip()
            if not role_name or role_name.startswith("$"):
                # A '$'-prefixed key is a declaration comment, never a role.
                continue
            members = tuple(str(item) for item in fields if str(item).strip())
            if not members:
                raise TruthProjectionError("role declaration names no field", role=role_name)
            roles[role_name] = members
        role_pairs = tuple(sorted(roles.items()))
        core = {
            "collection": collection.strip(),
            "identity_field": identity_field.strip(),
            "locator_fields": list(locators),
            "attribute_fields": list(attributes),
            "role_fields": {name: list(fields) for name, fields in role_pairs},
        }
        return cls(
            collection=collection.strip(),
            identity_field=identity_field.strip(),
            locator_fields=locators,
            attribute_fields=attributes,
            role_fields=role_pairs,
            spec_id=f"UCOS-URTX-{content_hash(core)[:16]}",
        )

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> ProjectionSpec:
        """Build a specification from a declared mapping."""
        if not isinstance(payload, Mapping):
            raise TruthProjectionError("projection declaration must be a mapping")
        missing = [key for key in ("collection", "identity_field") if key not in payload]
        if missing:
            raise TruthProjectionError(
                "projection declaration is incomplete", missing=",".join(missing)
            )
        return cls.create(
            str(payload["collection"]),
            str(payload["identity_field"]),
            locator_fields=payload.get("locator_fields", ()),
            attribute_fields=payload.get("attribute_fields", ()),
            role_fields=payload.get("role_fields"),
        )

    def role_names(self) -> tuple[str, ...]:
        """Every declared role name, in order."""
        return tuple(name for name, _ in self.role_fields)

    def to_dict(self) -> dict[str, Any]:
        """A JSON-serialisable projection of this specification."""
        return {
            "spec_id": self.spec_id,
            "collection": self.collection,
            "identity_field": self.identity_field,
            "locator_fields": list(self.locator_fields),
            "attribute_fields": list(self.attribute_fields),
            "role_fields": {name: list(fields) for name, fields in self.role_fields},
        }

    def fingerprint(self) -> str:
        """The deterministic content fingerprint of this specification."""
        return content_hash(self.to_dict())


class SubjectProjection:
    """Projects declared Truth documents into subjects — one reader for every project."""

    __slots__ = ("_spec",)

    def __init__(self, spec: ProjectionSpec) -> None:
        if not isinstance(spec, ProjectionSpec):
            raise TruthProjectionError("SubjectProjection requires a ProjectionSpec")
        self._spec = spec

    @property
    def spec(self) -> ProjectionSpec:
        """The declared specification this projection applies."""
        return self._spec

    def project(self, document: Mapping[str, Any]) -> tuple[Subject, ...]:
        """Project ``document`` into deterministic, de-duplicated subjects."""
        if not isinstance(document, Mapping):
            raise TruthProjectionError("truth document must be a mapping")
        records = _walk(document, self._spec.collection)
        if isinstance(records, Mapping):
            rows: Sequence[Any] = tuple(records[key] for key in sorted(records))
        elif isinstance(records, Sequence) and not isinstance(records, str | bytes):
            rows = records
        else:
            raise TruthProjectionError(
                "declared collection is not a sequence or mapping",
                pointer=self._spec.collection,
            )
        merged: dict[str, dict[str, Any]] = {}
        for index, row in enumerate(rows):
            if not isinstance(row, Mapping):
                raise TruthProjectionError(
                    "population record must be a mapping",
                    pointer=self._spec.collection,
                    index=index,
                )
            identity = row.get(self._spec.identity_field)
            if not isinstance(identity, str) or not identity.strip():
                raise TruthProjectionError(
                    "population record declares no identity",
                    field=self._spec.identity_field,
                    index=index,
                )
            entry = merged.setdefault(
                identity.strip(), {"locators": set(), "attributes": {}, "roles": {}}
            )
            for field_name in self._spec.locator_fields:
                entry["locators"].update(_flatten(row.get(field_name)))
            for role_name, fields in self._spec.role_fields:
                tagged = entry["roles"].setdefault(role_name, set())
                for field_name in fields:
                    tagged.update(_flatten(row.get(field_name)))
            for field_name in self._spec.attribute_fields:
                value = row.get(field_name)
                if value is not None:
                    entry["attributes"][field_name] = str(value)
        return tuple(
            Subject.create(
                subject_id,
                locators=sorted(payload["locators"]),
                attributes=payload["attributes"],
                roles={
                    name: sorted(values)
                    for name, values in sorted(payload["roles"].items())
                    if values
                },
            )
            for subject_id, payload in sorted(merged.items())
        )

    def project_file(self, path: Path | str) -> tuple[Subject, ...]:
        """Project a declared Truth document read from ``path`` (fail-closed)."""
        target = Path(path)
        try:
            raw = target.read_text("utf-8")
        except OSError as exc:
            raise TruthProjectionError(
                "truth document could not be read", path=str(target), detail=str(exc)
            ) from exc
        try:
            document = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise TruthProjectionError(
                "truth document is not valid JSON", path=str(target), detail=str(exc)
            ) from exc
        return self.project(document)


def project_subjects(
    document: Mapping[str, Any], spec: ProjectionSpec | Mapping[str, Any]
) -> tuple[Subject, ...]:
    """Project ``document`` using ``spec`` (accepting the declared mapping form)."""
    resolved = spec if isinstance(spec, ProjectionSpec) else ProjectionSpec.from_dict(spec)
    return SubjectProjection(resolved).project(document)


__all__ = [
    "ProjectionSpec",
    "SubjectProjection",
    "project_subjects",
]
