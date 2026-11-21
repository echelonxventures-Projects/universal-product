"""TASK-000017 — Universal Compiler intermediate representation (EPIC-003).

The IR is the single, immutable in-memory form every compilation stage operates
on. A blueprint document (TASK-000019 parses it) becomes a :class:`BlueprintIR`;
validation (TASK-000020), resolution (TASK-000021), and lowering (TASK-000023)
all consume the IR and never the raw document.

Design invariants:
    * **Immutable** — every node is a frozen dataclass, so a stage cannot mutate
      another stage's input; determinism (IMP-007 §5) is structural.
    * **Provenance-complete** — every :class:`BlueprintIR` carries the full
      backward-traceability chain (IMP-007 §1): Blueprint → Reference Architecture
      → Runtime Catalog → Architecture Constitution → Universal Ontology, plus the
      canonical source asset and its Generation Framework. No orphan artifacts
      (IP-03; Mandatory Rule 6 — all provenance preserved).
    * **No invention** — the IR models only what a declarative blueprint declares
      (TP-01). Construction enforces light structural invariants; certification and
      registry conformance are enforced by the Validation Engine.

EPIC-003 implements the **BP-DATA** family end-to-end. The IR models the closed
blueprint-family vocabulary so later epics extend it without redesign
(Mandatory Rules 1 & 2).
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from enum import Enum

from engine.compiler.errors import ParseError
from engine.compiler.types import DataType

#: Current IR schema version (semantic; consumed by serialization TASK-000018).
IR_VERSION = "1.0.0"


class BlueprintFamily(str, Enum):
    """The six registered blueprint families plus the API contract family.

    IMP-007 §2 — the compiler compiles these families and only these. EPIC-003
    implements ``BP-DATA``; the remaining members are modelled for forward
    compatibility (no redesign later).
    """

    DATA = "BP-DATA"
    EVENT = "BP-EVENT"
    API = "BP-API"
    CONTRACT = "BP-CONTRACT"
    WORKFLOW = "BP-WORKFLOW"
    SERVICE = "BP-SERVICE"
    APPLICATION = "BP-APPLICATION"

    @classmethod
    def coerce(cls, value: object, *, context: str) -> BlueprintFamily:
        try:
            return cls(str(value))
        except ValueError as exc:
            raise ParseError(
                "unknown blueprint family",
                value=value,
                at=context,
                allowed=[m.value for m in cls],
            ) from exc


class CertificationStatus(str, Enum):
    """Certification posture a blueprint declares for itself.

    IMP-007 §14/§16 — only ``CERTIFIED`` blueprints are compiled. Every other
    value is an uncertified input and is rejected by the Validation Engine.
    """

    CERTIFIED = "CERTIFIED"
    UNCERTIFIED = "UNCERTIFIED"
    PENDING = "PENDING"
    REVOKED = "REVOKED"

    @classmethod
    def coerce(cls, value: object, *, context: str) -> CertificationStatus:
        try:
            return cls(str(value))
        except ValueError as exc:
            raise ParseError(
                "unknown certification status",
                value=value,
                at=context,
                allowed=[m.value for m in cls],
            ) from exc


class RelationshipKind(str, Enum):
    """Cardinality of a data relationship between blueprints."""

    ONE_TO_ONE = "one_to_one"
    ONE_TO_MANY = "one_to_many"
    MANY_TO_ONE = "many_to_one"
    MANY_TO_MANY = "many_to_many"

    @classmethod
    def coerce(cls, value: object, *, context: str) -> RelationshipKind:
        try:
            return cls(str(value))
        except ValueError as exc:
            raise ParseError(
                "unknown relationship kind",
                value=value,
                at=context,
                allowed=[m.value for m in cls],
            ) from exc


def _require_identifier(value: object, *, field_name: str, at: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ParseError("expected a non-empty identifier", field=field_name, at=at)
    return value


@dataclass(frozen=True, slots=True)
class Provenance:
    """The complete backward-traceability chain of a blueprint (IMP-007 §1).

    Every field is a registered artifact id (``UCOS-*``) resolved against the
    Registry Adapter during validation. The chain is embedded, verbatim, into
    every artifact the compiler emits (Mandatory Rule 6).
    """

    canonical_source: str
    reference_architecture: str
    runtime_catalog: str
    architecture_constitution: str
    ontology_root: str
    generation_framework: str

    def __post_init__(self) -> None:
        for name in (
            "canonical_source",
            "reference_architecture",
            "runtime_catalog",
            "architecture_constitution",
            "ontology_root",
            "generation_framework",
        ):
            _require_identifier(getattr(self, name), field_name=name, at="provenance")

    def references(self) -> tuple[str, ...]:
        """Return every registered id in the chain, in canonical order."""
        return (
            self.canonical_source,
            self.reference_architecture,
            self.runtime_catalog,
            self.architecture_constitution,
            self.ontology_root,
            self.generation_framework,
        )


@dataclass(frozen=True, slots=True)
class Certification:
    """A blueprint's declared certification (IMP-007 §14)."""

    status: CertificationStatus
    evidence: str = ""

    @property
    def is_certified(self) -> bool:
        """True iff the blueprint declares itself ``CERTIFIED``."""
        return self.status is CertificationStatus.CERTIFIED


@dataclass(frozen=True, slots=True)
class Attribute:
    """A single data attribute of an entity (a column)."""

    name: str
    data_type: DataType
    nullable: bool = True
    primary_key: bool = False
    unique: bool = False
    max_length: int | None = None
    default: str | None = None
    description: str = ""

    def __post_init__(self) -> None:
        _require_identifier(self.name, field_name="attribute.name", at="attribute")
        if not isinstance(self.data_type, DataType):
            raise ParseError("attribute data_type must be a DataType", at=self.name)
        if self.max_length is not None and (
            isinstance(self.max_length, bool)
            or not isinstance(self.max_length, int)
            or self.max_length <= 0
        ):
            raise ParseError("max_length must be a positive integer", at=self.name)
        if self.primary_key and self.nullable:
            raise ParseError("a primary key attribute cannot be nullable", at=self.name)


@dataclass(frozen=True, slots=True)
class Index:
    """A secondary index over one or more entity attributes."""

    name: str
    columns: tuple[str, ...]
    unique: bool = False

    def __post_init__(self) -> None:
        _require_identifier(self.name, field_name="index.name", at="index")
        if not self.columns:
            raise ParseError("an index must reference at least one column", at=self.name)


@dataclass(frozen=True, slots=True)
class DataRelationship:
    """A declared relationship from this entity to another blueprint's entity."""

    name: str
    target: str
    kind: RelationshipKind

    def __post_init__(self) -> None:
        _require_identifier(self.name, field_name="relationship.name", at="relationship")
        _require_identifier(self.target, field_name="relationship.target", at=self.name)
        if not isinstance(self.kind, RelationshipKind):
            raise ParseError("relationship kind must be a RelationshipKind", at=self.name)


@dataclass(frozen=True, slots=True)
class Entity:
    """The persistent entity a BP-DATA blueprint declares."""

    name: str
    table: str
    attributes: tuple[Attribute, ...]
    indexes: tuple[Index, ...] = ()
    relationships: tuple[DataRelationship, ...] = ()

    def __post_init__(self) -> None:
        _require_identifier(self.name, field_name="entity.name", at="entity")
        _require_identifier(self.table, field_name="entity.table", at=self.name)
        if not self.attributes:
            raise ParseError("an entity must declare at least one attribute", at=self.name)
        seen: set[str] = set()
        for attribute in self.attributes:
            if attribute.name in seen:
                raise ParseError("duplicate attribute name", at=self.name, attribute=attribute.name)
            seen.add(attribute.name)
        # Validate index columns reference declared attributes (no invention).
        for index in self.indexes:
            for column in index.columns:
                if column not in seen:
                    raise ParseError(
                        "index references an unknown attribute",
                        at=self.name,
                        index=index.name,
                        column=column,
                    )

    @property
    def primary_key(self) -> tuple[Attribute, ...]:
        """The attribute(s) marked as primary key, in declaration order."""
        return tuple(a for a in self.attributes if a.primary_key)


@dataclass(frozen=True, slots=True)
class BlueprintIR:
    """The immutable intermediate representation of a single blueprint."""

    blueprint_id: str
    family: BlueprintFamily
    name: str
    version: str
    certification: Certification
    provenance: Provenance
    entity: Entity
    dependencies: tuple[str, ...] = ()
    description: str = ""
    ir_version: str = IR_VERSION

    def __post_init__(self) -> None:
        _require_identifier(self.blueprint_id, field_name="blueprint_id", at="blueprint")
        _require_identifier(self.version, field_name="version", at=self.blueprint_id)
        _require_identifier(self.name, field_name="name", at=self.blueprint_id)
        if not isinstance(self.family, BlueprintFamily):
            raise ParseError("family must be a BlueprintFamily", at=self.blueprint_id)
        if not self.blueprint_id.startswith(self.family.value):
            raise ParseError(
                "blueprint_id does not match its family prefix",
                at=self.blueprint_id,
                family=self.family.value,
            )
        if not isinstance(self.certification, Certification):
            raise ParseError("certification must be a Certification", at=self.blueprint_id)
        if not isinstance(self.provenance, Provenance):
            raise ParseError("provenance must be a Provenance", at=self.blueprint_id)
        if not isinstance(self.entity, Entity):
            raise ParseError("entity must be an Entity", at=self.blueprint_id)
        # dependencies must be unique, non-self, non-empty identifiers.
        seen: set[str] = set()
        for dep in self.dependencies:
            _require_identifier(dep, field_name="dependency", at=self.blueprint_id)
            if dep == self.blueprint_id:
                raise ParseError("a blueprint cannot depend on itself", at=self.blueprint_id)
            if dep in seen:
                raise ParseError("duplicate dependency", at=self.blueprint_id, dependency=dep)
            seen.add(dep)

    @classmethod
    def create(
        cls,
        *,
        blueprint_id: str,
        family: BlueprintFamily,
        name: str,
        version: str,
        certification: Certification,
        provenance: Provenance,
        entity: Entity,
        dependencies: Iterable[str] = (),
        description: str = "",
        ir_version: str = IR_VERSION,
    ) -> BlueprintIR:
        """Keyword-only constructor that normalises ``dependencies`` to a tuple."""
        return cls(
            blueprint_id=blueprint_id,
            family=family,
            name=name,
            version=version,
            certification=certification,
            provenance=provenance,
            entity=entity,
            dependencies=tuple(dependencies),
            description=description,
            ir_version=ir_version,
        )


__all__ = [
    "IR_VERSION",
    "BlueprintFamily",
    "CertificationStatus",
    "RelationshipKind",
    "Provenance",
    "Certification",
    "Attribute",
    "Index",
    "DataRelationship",
    "Entity",
    "BlueprintIR",
]
