"""URI-000001 — the Schema Generator.

Realizes the *structural contract* of canonical knowledge. The field set, the nullability
of each field, and the permitted value of each enumerated field are all **inferred from
the canonical records themselves** — not from a hand-maintained schema that could drift
from the store it claims to describe.

Two projections of one inference:

* a JSON Schema (2020-12) that validates a canonical record of this universe;
* an ANSI-SQL DDL projection with ``CHECK`` constraints mirroring the same enums, so a
  relational store cannot accept a record the JSON Schema would reject.

Because both are derived from the same inference pass, they cannot disagree.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from intelligence.realization.contracts import (
    ArtifactFamily,
    GeneratedArtifact,
    MediaKind,
    identifier,
)
from intelligence.realization.generators.base import GenerationContext, Generator

SCHEMA_FORMAT = "https://json-schema.org/draft/2020-12/schema"
SCHEMA_DOCUMENT_FORMAT = "ucos-uri-schema/1.0.0"

#: Fields whose values are drawn from a controlled vocabulary. The permitted set is
#: taken from the values actually present in this universe, so the schema is exact.
_ENUM_FIELDS = ("kind", "authority", "lifecycle", "universe")

#: Fields that identify a record. Always required, never null.
_IDENTITY_FIELDS = ("cko_id", "content_sha256")

_SQL_TYPES = {
    "string": "TEXT",
    "array": "TEXT",
    "boolean": "BOOLEAN",
    "integer": "BIGINT",
}


def _json_type(value: Any) -> str:
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, int):
        return "integer"
    if isinstance(value, list):
        return "array"
    return "string"


class SchemaGenerator(Generator):
    """Infers and emits the structural contract for one realization target."""

    family = ArtifactFamily.SCHEMA
    name = "uri.schema"
    version = "1.0.0"

    def generate(self, context: GenerationContext) -> tuple[GeneratedArtifact, ...]:
        fields = self._infer_fields(context)
        slug = context.target.path_slug
        schema = self._json_schema(context, fields)
        return (
            self.json_artifact(
                context,
                relative_path=f"schema/{slug}.schema.json",
                payload=schema,
            ),
            self.text_artifact(
                context,
                relative_path=f"schema/{slug}.sql",
                media=MediaKind.SQL,
                lines=self._ddl(context, fields),
            ),
        )

    # -- inference ------------------------------------------------------------

    def _infer_fields(self, context: GenerationContext) -> list[dict[str, Any]]:
        """Infer the field set, types, nullability, and enums from the actual records."""
        records = [obj.to_dict() for obj in context.objects]
        names = sorted({key for record in records for key in record})
        fields: list[dict[str, Any]] = []
        for field_name in names:
            present = [record.get(field_name) for record in records]
            observed = [value for value in present if value is not None]
            types = sorted({_json_type(value) for value in observed}) or ["string"]
            nullable = any(value is None for value in present) and (
                field_name not in _IDENTITY_FIELDS
            )
            entry: dict[str, Any] = {
                "name": field_name,
                "type": types[0] if len(types) == 1 else "string",
                "nullable": nullable,
                "required": field_name in _IDENTITY_FIELDS
                or not any(value is None for value in present),
            }
            if field_name in _ENUM_FIELDS:
                entry["enum"] = sorted({str(value) for value in observed})
            if entry["type"] == "array":
                entry["items"] = "string"
            fields.append(entry)
        return fields

    # -- JSON Schema ----------------------------------------------------------

    def _property(self, field: dict[str, Any]) -> dict[str, Any]:
        if field["type"] == "array":
            base: dict[str, Any] = {"type": "array", "items": {"type": "string"}}
        else:
            base = {"type": field["type"]}
        if "enum" in field:
            base["enum"] = field["enum"]
        if field["name"] in _IDENTITY_FIELDS:
            base["minLength"] = 1
        if field["nullable"]:
            base = {"anyOf": [base, {"type": "null"}]}
        if "enum" in field:
            base["description"] = (
                f"Canonical field '{field['name']}', constrained to the "
                f"{len(field['enum'])} value(s) present in this universe."
            )
        else:
            base["description"] = f"Canonical field '{field['name']}' of the UKDA record."
        return base

    def _json_schema(
        self, context: GenerationContext, fields: list[dict[str, Any]]
    ) -> dict[str, Any]:
        target = context.target
        payload = context.envelope(
            artifact_id=f"UCOS-URI-SCHEMA-{target.path_slug.upper()}",
            title=f"{target.universe} — Realized Canonical Record Schema",
            document_format=SCHEMA_DOCUMENT_FORMAT,
        )
        payload.update(
            {
                "$schema": SCHEMA_FORMAT,
                "$id": f"urn:ucos:uri:schema:{target.path_slug}",
                "type": "object",
                "title": f"{target.universe} canonical record",
                "description": (
                    f"Structural contract inferred from the {len(context.objects)} "
                    f"canonical object(s) homed in the {target.universe} universe."
                ),
                "additionalProperties": False,
                "required": sorted(f["name"] for f in fields if f["required"]),
                "properties": {f["name"]: self._property(f) for f in fields},
                "x-ucos-inference": {
                    "record_count": len(context.objects),
                    "field_count": len(fields),
                    "enumerated_fields": sorted(f["name"] for f in fields if "enum" in f),
                    "source_ckos": list(target.cko_ids),
                    "target_seal": target.seal,
                },
            }
        )
        return payload

    # -- SQL ------------------------------------------------------------------

    def _ddl(self, context: GenerationContext, fields: list[dict[str, Any]]) -> list[str]:
        target = context.target
        table = f"ucos_canonical_{identifier(target.universe)}"
        lines = self.provenance_comment(context, "--")
        lines += [
            "--",
            f"-- ANSI SQL projection of the {target.universe} canonical record contract.",
            "-- Array-valued canonical fields are stored as canonical JSON text so the",
            "-- projection stays vendor-neutral (TP-04 / UCKO-PRIN-0003).",
            "",
            f"CREATE TABLE IF NOT EXISTS {table} (",
        ]
        column_lines: list[str] = []
        for field in fields:
            sql_type = _SQL_TYPES[field["type"]]
            null = "" if field["nullable"] else " NOT NULL"
            pk = " PRIMARY KEY" if field["name"] == "cko_id" else ""
            column_lines.append(f"  {field['name']} {sql_type}{null}{pk}")
        for field in fields:
            if "enum" in field and field["enum"]:
                allowed = ", ".join(f"'{value}'" for value in field["enum"])
                column_lines.append(
                    f"  CONSTRAINT chk_{table}_{field['name']} "
                    f"CHECK ({field['name']} IN ({allowed}))"
                )
        lines.extend(self._comma_separated(column_lines))
        lines += [");", ""]
        for field_name in ("kind", "authority", "lifecycle"):
            if any(f["name"] == field_name for f in fields):
                lines.append(
                    f"CREATE INDEX IF NOT EXISTS idx_{table}_{field_name} "
                    f"ON {table} ({field_name});"
                )
        lines.append("")
        return lines

    @staticmethod
    def _comma_separated(entries: Iterable[str]) -> list[str]:
        items = list(entries)
        return [f"{item}," if index < len(items) - 1 else item for index, item in enumerate(items)]


__all__ = ["SCHEMA_DOCUMENT_FORMAT", "SCHEMA_FORMAT", "SchemaGenerator"]
