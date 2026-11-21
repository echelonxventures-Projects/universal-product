"""TASK-000018 — IR serialization (EPIC-003).

Deterministic, byte-reproducible serialization of the :class:`BlueprintIR`
(TASK-000017) to and from JSON. Serialization is a compilation invariant
(IMP-007 §5): identical IR yields **byte-identical** output, achieved by

    * sorting object keys (``sort_keys=True``);
    * fixed, compact separators (no ambient whitespace);
    * a stable field ordering that mirrors the IR structure;
    * no timestamps or ambient state embedded in the encoded form.

The canonical byte form produced here is the substrate the content hash and
signature (TASK-000026) are computed over, so reproducibility is structural.

``deserialize`` reconstructs a fully-validated IR (all node ``__post_init__``
invariants run), so a malformed encoded document fails loudly with a
:class:`SerializationError`.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any

from engine.compiler.errors import ParseError, SerializationError
from engine.compiler.ir import (
    Attribute,
    BlueprintFamily,
    BlueprintIR,
    Certification,
    CertificationStatus,
    DataRelationship,
    Entity,
    Index,
    Provenance,
    RelationshipKind,
)
from engine.compiler.types import DataType


def to_canonical_dict(ir: BlueprintIR) -> dict[str, Any]:
    """Return a deterministic, JSON-ready dict representation of ``ir``."""
    return {
        "ir_version": ir.ir_version,
        "blueprint_id": ir.blueprint_id,
        "family": ir.family.value,
        "name": ir.name,
        "version": ir.version,
        "description": ir.description,
        "certification": {
            "status": ir.certification.status.value,
            "evidence": ir.certification.evidence,
        },
        "provenance": {
            "canonical_source": ir.provenance.canonical_source,
            "reference_architecture": ir.provenance.reference_architecture,
            "runtime_catalog": ir.provenance.runtime_catalog,
            "architecture_constitution": ir.provenance.architecture_constitution,
            "ontology_root": ir.provenance.ontology_root,
            "generation_framework": ir.provenance.generation_framework,
        },
        "dependencies": list(ir.dependencies),
        "entity": {
            "name": ir.entity.name,
            "table": ir.entity.table,
            "attributes": [
                {
                    "name": a.name,
                    "data_type": a.data_type.value,
                    "nullable": a.nullable,
                    "primary_key": a.primary_key,
                    "unique": a.unique,
                    "max_length": a.max_length,
                    "default": a.default,
                    "description": a.description,
                }
                for a in ir.entity.attributes
            ],
            "indexes": [
                {"name": i.name, "columns": list(i.columns), "unique": i.unique}
                for i in ir.entity.indexes
            ],
            "relationships": [
                {"name": r.name, "target": r.target, "kind": r.kind.value}
                for r in ir.entity.relationships
            ],
        },
    }


def serialize(ir: BlueprintIR) -> str:
    """Serialize ``ir`` to a canonical, deterministic JSON string."""
    try:
        return json.dumps(
            to_canonical_dict(ir),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        )
    except (TypeError, ValueError) as exc:  # pragma: no cover - defensive
        raise SerializationError(
            "failed to serialize IR", blueprint_id=ir.blueprint_id, detail=str(exc)
        ) from exc


def serialize_bytes(ir: BlueprintIR) -> bytes:
    """Serialize ``ir`` to canonical UTF-8 bytes (hash/signature substrate)."""
    return serialize(ir).encode("utf-8")


def _require(record: Mapping[str, Any], key: str, *, at: str) -> Any:
    if key not in record or record[key] is None:
        raise SerializationError("required field missing", field=key, at=at)
    return record[key]


def _entity_from_dict(raw: Any, *, at: str) -> Entity:
    if not isinstance(raw, Mapping):
        raise SerializationError("entity must be an object", at=at)
    attributes_raw = _require(raw, "attributes", at=at)
    if not isinstance(attributes_raw, list):
        raise SerializationError("entity.attributes must be an array", at=at)
    attributes = tuple(
        Attribute(
            name=str(_require(a, "name", at=at)),
            data_type=DataType.coerce(_require(a, "data_type", at=at), context=at),
            nullable=bool(a.get("nullable", True)),
            primary_key=bool(a.get("primary_key", False)),
            unique=bool(a.get("unique", False)),
            max_length=a.get("max_length"),
            default=a.get("default"),
            description=a.get("description") or "",
        )
        for a in attributes_raw
        if isinstance(a, Mapping)
    )
    indexes_raw = raw.get("indexes") or []
    indexes = tuple(
        Index(
            name=str(_require(i, "name", at=at)),
            columns=tuple(i.get("columns") or ()),
            unique=bool(i.get("unique", False)),
        )
        for i in indexes_raw
        if isinstance(i, Mapping)
    )
    relationships_raw = raw.get("relationships") or []
    relationships = tuple(
        DataRelationship(
            name=str(_require(r, "name", at=at)),
            target=str(_require(r, "target", at=at)),
            kind=RelationshipKind.coerce(_require(r, "kind", at=at), context=at),
        )
        for r in relationships_raw
        if isinstance(r, Mapping)
    )
    return Entity(
        name=str(_require(raw, "name", at=at)),
        table=str(_require(raw, "table", at=at)),
        attributes=attributes,
        indexes=indexes,
        relationships=relationships,
    )


def from_dict(record: Mapping[str, Any]) -> BlueprintIR:
    """Reconstruct a fully-validated :class:`BlueprintIR` from a mapping."""
    if not isinstance(record, Mapping):
        raise SerializationError("IR document must be an object")
    at = str(record.get("blueprint_id", "blueprint"))
    cert_raw = _require(record, "certification", at=at)
    if not isinstance(cert_raw, Mapping):
        raise SerializationError("certification must be an object", at=at)
    prov_raw = _require(record, "provenance", at=at)
    if not isinstance(prov_raw, Mapping):
        raise SerializationError("provenance must be an object", at=at)
    try:
        return BlueprintIR(
            blueprint_id=str(_require(record, "blueprint_id", at=at)),
            family=BlueprintFamily.coerce(_require(record, "family", at=at), context=at),
            name=str(_require(record, "name", at=at)),
            version=str(_require(record, "version", at=at)),
            description=record.get("description") or "",
            certification=Certification(
                status=CertificationStatus.coerce(_require(cert_raw, "status", at=at), context=at),
                evidence=cert_raw.get("evidence") or "",
            ),
            provenance=Provenance(
                canonical_source=str(_require(prov_raw, "canonical_source", at=at)),
                reference_architecture=str(_require(prov_raw, "reference_architecture", at=at)),
                runtime_catalog=str(_require(prov_raw, "runtime_catalog", at=at)),
                architecture_constitution=str(
                    _require(prov_raw, "architecture_constitution", at=at)
                ),
                ontology_root=str(_require(prov_raw, "ontology_root", at=at)),
                generation_framework=str(_require(prov_raw, "generation_framework", at=at)),
            ),
            entity=_entity_from_dict(_require(record, "entity", at=at), at=at),
            dependencies=tuple(record.get("dependencies") or ()),
            ir_version=str(record.get("ir_version") or ""),
        )
    except ParseError as exc:
        # A structurally-parseable document that violates an IR invariant is a
        # serialization-level failure when reconstructing (fail loud, auditable).
        raise SerializationError(
            "encoded IR violates an IR invariant",
            at=at,
            detail=exc.message,
            context=exc.context,
        ) from exc


def deserialize(text: str) -> BlueprintIR:
    """Deserialize a canonical JSON string back into a validated IR."""
    try:
        document = json.loads(text)
    except json.JSONDecodeError as exc:
        raise SerializationError("IR document is not valid JSON", detail=str(exc)) from exc
    return from_dict(document)


__all__ = [
    "to_canonical_dict",
    "serialize",
    "serialize_bytes",
    "from_dict",
    "deserialize",
]
