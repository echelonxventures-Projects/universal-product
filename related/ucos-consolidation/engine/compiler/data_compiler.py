"""TASK-000023 — Data Blueprint Compiler (EPIC-003, IMP-007 §3/§6).

Lowers a validated BP-DATA :class:`BlueprintIR` into concrete, deterministic
implementation artifacts:

    * a **database schema** (ANSI ``CREATE TABLE`` DDL with primary key, unique
      constraints, and secondary indexes);
    * **persistence source** (an immutable entity dataclass + a read repository
      protocol, derived faithfully from the declared attributes);
    * a **configuration** document (table + provenance metadata).

Every artifact is a deterministic lowering of the blueprint (IMP-007 §5) and
embeds the complete backward-traceability chain (IMP-007 §1; Mandatory Rule 6):
``artifact → Blueprint → Reference Architecture → Runtime Catalog → Architecture
Constitution → Universal Ontology`` (with the Generation Framework noted).

**No invented behaviour** (TP-01; Mandatory Rule 7): the compiler emits only what
the blueprint declares — no business logic, no fields, no relations beyond the IR.
Output is stdlib-only, byte-reproducible text.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from enum import Enum

from engine.compiler.errors import CompilationError
from engine.compiler.ir import Attribute, BlueprintIR, Entity
from engine.compiler.types import python_type, sql_type
from engine.foundation.obs.logging import get_logger
from engine.foundation.obs.telemetry import trace

_logger = get_logger("compiler.data")

_SNAKE_1 = re.compile(r"(.)([A-Z][a-z]+)")
_SNAKE_2 = re.compile(r"([a-z0-9])([A-Z])")


class ArtifactKind(str, Enum):
    """The kind of artifact the data compiler emits."""

    SQL_SCHEMA = "sql_schema"
    SOURCE = "source"
    CONFIG = "config"


@dataclass(frozen=True, slots=True)
class CompiledArtifact:
    """A single deterministic output artifact with an embedded content hash."""

    path: str
    kind: ArtifactKind
    content: str

    @property
    def content_hash(self) -> str:
        """The SHA-256 of the artifact's UTF-8 content (integrity, IMP-007 §12)."""
        return hashlib.sha256(self.content.encode("utf-8")).hexdigest()

    @property
    def byte_length(self) -> int:
        return len(self.content.encode("utf-8"))


@dataclass(frozen=True, slots=True)
class CompiledBlueprint:
    """The full set of artifacts compiled from one blueprint, with provenance."""

    blueprint_id: str
    provenance_chain: tuple[str, ...]
    generation_framework: str
    artifacts: tuple[CompiledArtifact, ...]

    def artifact(self, kind: ArtifactKind) -> CompiledArtifact:
        """Return the single artifact of ``kind`` (raises if absent)."""
        for artifact in self.artifacts:
            if artifact.kind is kind:
                return artifact
        raise CompilationError(
            "no compiled artifact of that kind",
            blueprint_id=self.blueprint_id,
            kind=kind.value,
        )


def snake_case(name: str) -> str:
    """Convert an identifier to deterministic ``snake_case``."""
    partial = _SNAKE_1.sub(r"\1_\2", name)
    return _SNAKE_2.sub(r"\1_\2", partial).replace("-", "_").replace(" ", "_").lower()


def provenance_chain(ir: BlueprintIR) -> tuple[str, ...]:
    """Return the ordered backward-traceability chain for ``ir`` (IMP-007 §1)."""
    return (
        ir.blueprint_id,
        ir.provenance.canonical_source,
        ir.provenance.reference_architecture,
        ir.provenance.runtime_catalog,
        ir.provenance.architecture_constitution,
        ir.provenance.ontology_root,
    )


def _provenance_line(ir: BlueprintIR) -> str:
    chain = " <- ".join(provenance_chain(ir))
    return f"{chain} (generation-framework: {ir.provenance.generation_framework})"


class DataBlueprintCompiler:
    """Compiles a validated BP-DATA IR into deterministic implementation artifacts."""

    __slots__ = ()

    def compile(self, ir: BlueprintIR) -> CompiledBlueprint:
        """Lower ``ir`` into its schema, source, and config artifacts."""
        with trace("compiler.compile", blueprint=ir.blueprint_id):
            table = ir.entity.table
            artifacts = (
                CompiledArtifact(
                    path=f"schema/{table}.sql",
                    kind=ArtifactKind.SQL_SCHEMA,
                    content=self._render_sql(ir),
                ),
                CompiledArtifact(
                    path=f"persistence/{snake_case(ir.entity.name)}_repository.py",
                    kind=ArtifactKind.SOURCE,
                    content=self._render_source(ir),
                ),
                CompiledArtifact(
                    path=f"config/{ir.blueprint_id}.json",
                    kind=ArtifactKind.CONFIG,
                    content=self._render_config(ir),
                ),
            )
        _logger.info(
            "compiler.blueprint.compiled",
            blueprint=ir.blueprint_id,
            artifacts=len(artifacts),
        )
        return CompiledBlueprint(
            blueprint_id=ir.blueprint_id,
            provenance_chain=provenance_chain(ir),
            generation_framework=ir.provenance.generation_framework,
            artifacts=artifacts,
        )

    # -- renderers (pure, deterministic) --------------------------------------

    def _render_sql(self, ir: BlueprintIR) -> str:
        entity = ir.entity
        lines = [
            f"-- provenance: {_provenance_line(ir)}",
            f"-- blueprint: {ir.blueprint_id} v{ir.version}",
            f"CREATE TABLE {entity.table} (",
        ]
        column_defs = [self._column_def(a) for a in entity.attributes]
        primary = entity.primary_key[0]
        column_defs.append(f"    PRIMARY KEY ({primary.name})")
        lines.append(",\n".join(column_defs))
        lines.append(");")
        for index in entity.indexes:
            unique = "UNIQUE " if index.unique else ""
            columns = ", ".join(index.columns)
            lines.append(f"CREATE {unique}INDEX {index.name} ON {entity.table} ({columns});")
        return "\n".join(lines) + "\n"

    @staticmethod
    def _column_def(attribute: Attribute) -> str:
        column_type = sql_type(attribute.data_type, max_length=attribute.max_length)
        parts = [f"    {attribute.name}", column_type]
        if not attribute.nullable:
            parts.append("NOT NULL")
        if attribute.unique and not attribute.primary_key:
            parts.append("UNIQUE")
        if attribute.default is not None:
            parts.append(f"DEFAULT {attribute.default}")
        return " ".join(parts)

    def _render_source(self, ir: BlueprintIR) -> str:
        entity = ir.entity
        class_name = self._class_name(entity)
        fields = [
            f"    {a.name}: {python_type(a.data_type)}" + (" | None" if a.nullable else "")
            for a in entity.attributes
        ]
        primary = entity.primary_key[0]
        header = [
            '"""Generated persistence source — DO NOT EDIT.',
            "",
            f"provenance: {_provenance_line(ir)}",
            f"blueprint: {ir.blueprint_id} v{ir.version}",
            "Generated deterministically by the UCOS Ω∞ Universal Compiler (IMP-007).",
            '"""',
            "from __future__ import annotations",
            "",
            "import datetime  # noqa: F401 (used by generated type hints)",
            "import decimal  # noqa: F401",
            "import uuid  # noqa: F401",
            "from dataclasses import dataclass",
            "from typing import Protocol",
            "",
            "",
            "@dataclass(frozen=True, slots=True)",
            f"class {class_name}:",
            f'    """Immutable row model for table ``{entity.table}``."""',
            "",
            *fields,
            "",
            "",
            f"class {class_name}Repository(Protocol):",
            f'    """Read repository protocol for :class:`{class_name}`."""',
            "",
            f"    def get(self, {primary.name}: {python_type(primary.data_type)})"
            f" -> {class_name} | None:",
            f'        """Return the {entity.name} with the given primary key, or None."""',
            "        ...",
            "",
            f"    def list(self, *, limit: int = 100, offset: int = 0)"
            f" -> tuple[{class_name}, ...]:",
            f'        """Return a page of {entity.name} rows in a stable order."""',
            "        ...",
        ]
        return "\n".join(header) + "\n"

    def _render_config(self, ir: BlueprintIR) -> str:
        entity = ir.entity
        config = {
            "blueprint_id": ir.blueprint_id,
            "family": ir.family.value,
            "version": ir.version,
            "table": entity.table,
            "entity": entity.name,
            "primary_key": entity.primary_key[0].name,
            "columns": [a.name for a in entity.attributes],
            "provenance": {
                "chain": list(provenance_chain(ir)),
                "generation_framework": ir.provenance.generation_framework,
            },
            "relationships": [
                {"name": r.name, "target": r.target, "kind": r.kind.value}
                for r in entity.relationships
            ],
        }
        return json.dumps(config, sort_keys=True, indent=2, ensure_ascii=False) + "\n"

    @staticmethod
    def _class_name(entity: Entity) -> str:
        parts = re.split(r"[_\-\s]+", snake_case(entity.name))
        return "".join(part.capitalize() for part in parts if part) or "Entity"


__all__ = [
    "ArtifactKind",
    "CompiledArtifact",
    "CompiledBlueprint",
    "DataBlueprintCompiler",
    "snake_case",
    "provenance_chain",
]
