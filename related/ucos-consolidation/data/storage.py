"""EC3-B10-U05 — The Universal Storage construct (DMC-06).

Realizes the meta-model construct **DMC-06 Storage** (DATA-005 §2; DATA-010 §3):

    the implementation-independent **abstract topology** by which data is persisted
    and retrieved — the conceptual model of *where* and *how durably* represented data
    endures and *how* it is reached, expressed **without any engine, format, or
    vendor** (the ontology root DOE-06; UDL-11 Storage Independence). A storage
    construct is an ENG-002 Object classified by an ENG-004 Type, binding persistence
    behavior *by reference* to the frozen RUNTIME state concern (DMR-11). Storage is
    neither the data it persists (DOE-01/02) nor a database product — it is the
    **abstract persistence topology**.

The construct is **additive over the CERTIFIED EC-1 foundation *and* the CERTIFIED
DMC-02 Entity + DMC-05 Schema**, reusing all *by reference* (UDL-02 / DMI-05):

* Identity is derived through the EC-1 certified deterministic encoding
  (:func:`engine.certification.contracts.canonical_json` /
  :func:`~engine.certification.contracts.content_hash`) — no second identity scheme.
* The persisted set (DMR-05 ``persists``) is a tuple of **references to CERTIFIED
  :class:`~data.entity.Entity` objects**, each tagged with the CERTIFIED
  :class:`~data.schema.Schema` it conforms to (DTA-07 / DTA-K3 schema alignment),
  **never owned, embedded, or copied** (DTA-09; DMX-02 non-absorbing).
* Persistence behavior is a **RUNTIME state reference** only (DMR-11 / DTA-02 / DTA-K2)
  — no execution, state engine, event broker, or orchestration is defined.

**No engine, database, file/serialization format, query language, broker,
warehouse/lake, cache, cloud data service, or vendor is selected** (UDL-11 / DTA-01 /
DTA-K5) — enforced fail-closed by a technology-marker scan over the whole construct.

A :class:`Storage` is *immutable* (frozen — ENG-002 objecthood), *typed* (ENG-004,
DTA-01/DTA-K1/UDL-03), *identified* (ENG-001, DTA-K1/UDL-04), *placement-explicit*
(a declared, decidable locus set — DTA-03/DTA-C1), *durability-declared*
(DTA-04/DTA-C2), *schema-aligned* (DTA-07/DTA-K3), *classified* by one DXH-06 kind,
*versioned*, and holds a *forward-only lifecycle state* (DOS-01…05, UDL-12).
Constructing a :class:`Storage` enforces DTA-K1/K3/K5, the topology rules
DTA-C1/C2/C3/C4, and UDL-11/03/04/05 **fail-closed**: an ill-formed topology cannot
exist.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any

# --- DMC-02 / DMC-05 reuse by reference (UDL-02) — never redefined ----------------
from data.entity import Entity
from data.schema import Schema
from data.storage_meta import (
    LIFECYCLE_ORDER,
    STORAGE_META_CLASS,
    STORAGE_RELATIONSHIPS,
    STORAGE_SUBSTRATE_REFS,
    DurabilityLevel,
    StorageKind,
    StorageState,
)

# --- EC-1 reuse by reference (UDL-02 / DMI-05) — imported, never redefined --------
from engine.certification.contracts import canonical_json, content_hash

#: The deterministic id prefix for a realized Storage (mirrors EC-1 UCOS-<KIND>-<hex16>).
STORAGE_ID_PREFIX = "UCOS-STORAGE"

#: The reference prefix a storage topology presents its persistence binding (DMR-11).
RUNTIME_REF_PREFIX = "UCOS-RUNTIME-REF"

#: The identity-reference prefix a persisted Entity carries (DMR-05 ``persists`` target).
ENTITY_ID_PREFIX = "UCOS-ENTITY"

#: The identity-reference prefix a conformance Schema carries (DTA-07 alignment target).
SCHEMA_ID_PREFIX = "UCOS-SCHEMA"

#: The map of EC-1 / DMC-02 / DMC-05 primitives this construct reuses *by reference*
#: (never redefined). Recorded for the reuse-integrity check (UDL-02 / DMI-05 / VC-5).
REUSE_REFS: dict[str, str] = {
    "ENG-001": "engine.certification.contracts.content_hash (deterministic identity derivation)",
    "ENG-002": "python frozen object (immutable objecthood bearing the topology)",
    "ENG-004": "data.storage_meta.StorageKind + type_tag (ENG-004 typing discipline)",
    "ENG-005": "persisted-entity + schema + RUNTIME-state identity references (DMR-05/11)",
    "DMC-02": "data.entity.Entity — the CERTIFIED persists target (DMR-05); referenced only",
    "DMC-05": "data.schema.Schema — the CERTIFIED conformance schema (DTA-07); referenced only",
    "RL-F2": "RUNTIME state concern — persistence behavior bound by reference (DMR-11/DTA-02)",
}

#: Conservative secret markers used to enforce UDL-15 / DTA-09 / RR-07 (embed no secret).
_SECRET_MARKERS: tuple[str, ...] = (
    "password",
    "secret",
    "private_key",
    "privatekey",
    "api_key",
    "apikey",
    "access_token",
    "credential",
    "-----begin",
)

#: Conservative storage-technology markers used to enforce **UDL-11 / DTA-01 / DTA-K5**
#: (select no engine/database/format/query language/broker/warehouse/vendor). A storage
#: topology naming any of these is rejected fail-closed — storage is abstract topology
#: only. This is the material exercise of UDL-11 Storage Independence.
_TECH_MARKERS: tuple[str, ...] = (
    "postgres",
    "mysql",
    "mariadb",
    "sqlite",
    "mongodb",
    "mongo",
    "redis",
    "cassandra",
    "dynamodb",
    "couchdb",
    "neo4j",
    "elasticsearch",
    "opensearch",
    "kafka",
    "rabbitmq",
    "oracle",
    "sqlserver",
    "mssql",
    "snowflake",
    "bigquery",
    "redshift",
    "clickhouse",
    "parquet",
    "avro",
    "protobuf",
    "jdbc",
    "odbc",
    "amazon s3",
    "aws s3",
    "s3://",
    "gcs://",
    "azure blob",
    " sql ",
    "nosql",
    "innodb",
    "rocksdb",
    "leveldb",
)


def runtime_ref_for(concept: str) -> str:
    """The reference a storage topology presents to bind RUNTIME persistence (DMR-11).

    A storage construct's persistence/retrieval behavior is a *reference* to the frozen
    RL-F2 state concern (DTA-02 / DTA-K2), never a redefined engine.
    """
    return f"{RUNTIME_REF_PREFIX}:{concept}"


class StorageError(ValueError):
    """Raised when a value cannot be realized as a well-formed :class:`Storage`.

    A :class:`Storage` is fail-closed (TRACK-001): an ill-formed persistence topology —
    or any topology that names a storage technology — is rejected at construction rather
    than admitted as an invalid, non-abstract, or technology-bound topology.
    """


@dataclass(frozen=True, slots=True)
class PersistedEntityRef:
    """A reference to a CERTIFIED schema-conformant Entity a topology ``persists`` (DMR-05).

    Records **only** the persisted entity's identity, structural fingerprint, name,
    type, meta-class, and the CERTIFIED Schema it conforms to (DTA-07) — never its
    implementation — so the topology references, and never owns or absorbs, the data
    it persists (DTA-09; DMX-02 non-absorbing; UDL-02 reuse-by-reference).
    """

    entity_id: str
    structure_digest: str
    name: str
    type_tag: str
    meta_class: str
    schema_ref: str

    @classmethod
    def from_entity(cls, entity: Entity, schema: Schema) -> PersistedEntityRef:
        """Project a CERTIFIED :class:`~data.entity.Entity` (+ its :class:`~data.schema.Schema`).

        The entity **must conform** to the schema (DTA-07 / DTA-C4 / DTA-K3); a
        non-conformant pairing is rejected fail-closed.
        """
        if not isinstance(entity, Entity):
            raise StorageError("a topology persists a data.entity.Entity (DMR-05)")
        if not isinstance(schema, Schema):
            raise StorageError("persisted data must reference a data.schema.Schema (DTA-07)")
        if not schema.conforms_entity(entity):
            raise StorageError("persisted entity does not conform to its schema (DTA-K3 / DTA-C4)")
        return cls(
            entity_id=entity.entity_id,
            structure_digest=entity.structure_digest,
            name=entity.name,
            type_tag=entity.type_tag,
            meta_class=entity.meta_class,
            schema_ref=schema.schema_id,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "entity_id": self.entity_id,
            "structure_digest": self.structure_digest,
            "name": self.name,
            "type_tag": self.type_tag,
            "meta_class": self.meta_class,
            "schema_ref": self.schema_ref,
            "binding": "DMR-05:persists",
            "owned": False,  # DTA-09 — persisted by reference, never owned
            "absorbing": False,  # DMX-02 — referenced, not absorbed
        }


@dataclass(frozen=True, slots=True)
class Storage:
    """DMC-06 — an immutable, typed, identified, technology-neutral abstract topology.

    Fields:
        name:          the explicit topology name (DTA-03; part of identity).
        type_tag:      the ENG-004 Type of the topology (DTA-01 / DTA-K1; UDL-03).
        kind:          the DXH-06 classification (DMR-09 classified-by).
        loci:          the explicit, decidable locus set / placement (DTA-03 / DTA-C1).
                       Non-empty; no duplicate loci. Cardinality is consistent with kind
                       (Local=1; Distributed≥2; Tiered≥1 with tiered durability).
        durability:    the declared, decidable durability level (DTA-04 / DTA-C2).
        persisted_refs:the CERTIFIED schema-conformant entities the topology persists
                       (DMR-05; DTA-09 non-owning). Non-empty.
        runtime_ref:   the RUNTIME state reference persistence binds to (DMR-11 / DTA-02
                       / DTA-K2). A reference obligation only — no engine is defined.
        state:         the DOS-01…05 forward-only lifecycle state (UDL-12).
        version:       the topology version (supersession on breaking change; UDL-12/15).
        supersedes:    the id of a superseded topology, recorded on breaking change.
    """

    name: str
    type_tag: str
    kind: StorageKind
    loci: tuple[str, ...]
    durability: DurabilityLevel
    persisted_refs: tuple[PersistedEntityRef, ...]
    runtime_ref: str
    state: StorageState = StorageState.DEFINED
    version: str = "1.0.0"
    supersedes: str = ""

    def __post_init__(self) -> None:
        # DTA-03 — explicit, decidable name.
        if not isinstance(self.name, str) or not self.name.strip():
            raise StorageError("storage must have an explicit name (DTA-03)")
        # DTA-01 / DTA-K1 / DMK-01 / UDL-03 — typed (ENG-004): a decidable, non-empty type.
        if not isinstance(self.type_tag, str) or not self.type_tag.strip():
            raise StorageError("storage must be typed with a non-empty ENG-004 type_tag (DTA-K1)")
        # DXH-06 / DMR-09 — classified by exactly one Storage kind.
        if not isinstance(self.kind, StorageKind):
            raise StorageError("storage kind must be a DXH-06 StorageKind (DMR-09)")
        # DTA-03 / DTA-C1 — an explicit, non-empty, decidable locus set.
        if not isinstance(self.loci, tuple) or not self.loci:
            raise StorageError("storage must declare an explicit, non-empty locus set (DTA-C1)")
        seen_loci: set[str] = set()
        for locus in self.loci:
            if not isinstance(locus, str) or not locus.strip():
                raise StorageError("a storage locus must be a non-empty placement concept (DTA-03)")
            if locus in seen_loci:
                raise StorageError("storage locus set has a duplicate member (DTA-C1)")
            seen_loci.add(locus)
        # DTA-04 / DTA-C2 — declared, decidable durability.
        if not isinstance(self.durability, DurabilityLevel):
            raise StorageError("storage durability must be a declared DurabilityLevel (DTA-04)")
        # DXH-06 / DTA-C3 — topology cardinality/durability consistent with the kind.
        if self.kind is StorageKind.LOCAL and len(self.loci) != 1:
            raise StorageError("a Local-Topology declares exactly one locus (DXH-06 / DTA-C3)")
        if self.kind is StorageKind.DISTRIBUTED and len(self.loci) < 2:
            raise StorageError("a Distributed-Topology declares ≥2 loci (DXH-06 / DTA-C3)")
        if self.kind is StorageKind.TIERED and self.durability is not DurabilityLevel.TIERED:
            raise StorageError("a Tiered-Topology declares tiered durability (DXH-06 / DTA-04)")
        # DMR-05 — persisted subjects are reference-only projections of CERTIFIED entities.
        if not isinstance(self.persisted_refs, tuple) or not self.persisted_refs:
            raise StorageError("storage must persist ≥1 CERTIFIED entity by reference (DMR-05)")
        seen_entities: set[str] = set()
        for ref in self.persisted_refs:
            if not isinstance(ref, PersistedEntityRef):
                raise StorageError("persisted subjects are PersistedEntityRef references (DMR-05)")
            if not ref.entity_id.startswith(f"{ENTITY_ID_PREFIX}-"):
                raise StorageError("a persisted subject is not a CERTIFIED Entity id (DMR-05)")
            if len(ref.structure_digest) != 64 or any(
                c not in "0123456789abcdef" for c in ref.structure_digest
            ):
                raise StorageError("a persisted subject carries no structural digest (UDL-06)")
            # DTA-07 / DTA-C4 / DTA-K3 — stored data is schema-conformant (schema referenced).
            if not ref.schema_ref.startswith(f"{SCHEMA_ID_PREFIX}-"):
                raise StorageError("persisted data is not schema-aligned (DTA-07 / DTA-K3)")
            if ref.entity_id in seen_entities:
                raise StorageError("storage persists a duplicate entity (DTA-C1)")
            seen_entities.add(ref.entity_id)
        # DMR-11 / DTA-02 / DTA-K2 — persistence binds a RUNTIME state reference.
        if not isinstance(self.runtime_ref, str) or not self.runtime_ref.startswith(
            f"{RUNTIME_REF_PREFIX}:"
        ):
            raise StorageError("persistence must bind a RUNTIME state reference (DMR-11 / DTA-K2)")
        # V5 / UDL-12 — a valid forward-only lifecycle state.
        if not isinstance(self.state, StorageState):
            raise StorageError("storage state must be a DOS-01…05 state (UDL-12)")
        # DSA-06-analog — a topology records an explicit, non-empty version.
        if not isinstance(self.version, str) or not self.version.strip():
            raise StorageError("storage must record an explicit version (DTA-08 / UDL-12)")
        if not isinstance(self.supersedes, str):
            raise StorageError("storage supersedes reference must be a string (UDL-12)")
        # UDL-11 / DTA-01 / DTA-K5 — names no storage technology (material, fail-closed).
        if self._scan_technology():
            raise StorageError(
                "storage names a storage technology/engine/format/vendor (UDL-11 / DTA-01 / DTA-K5)"
            )

    # -- technology-neutrality (UDL-11, material) ------------------------------

    def _scan_technology(self) -> bool:
        """True iff any technology marker appears in the topology's declared surface."""
        haystack = canonical_json(self.canonical_core()).lower()
        return any(marker in haystack for marker in _TECH_MARKERS)

    def names_technology(self) -> bool:
        """UDL-11 / DTA-01 / DTA-K5 / C6 — True iff the topology names a storage technology."""
        return self._scan_technology()

    # -- identity (ENG-001) borne by object (ENG-002), by reference ------------

    def canonical_core(self) -> dict[str, Any]:
        """The canonical, hashable core of the topology (structure + persisted references)."""
        return {
            "meta_class": STORAGE_META_CLASS,
            "name": self.name,
            "type_tag": self.type_tag,
            "kind": self.kind.value,
            "loci": list(self.loci),
            "durability": self.durability.value,
            "persisted_refs": [
                {
                    "entity_id": r.entity_id,
                    "structure_digest": r.structure_digest,
                    "name": r.name,
                    "type_tag": r.type_tag,
                    "meta_class": r.meta_class,
                    "schema_ref": r.schema_ref,
                }
                for r in self.persisted_refs
            ],
            "runtime_ref": self.runtime_ref,
            "version": self.version,
            "supersedes": self.supersedes,
        }

    @property
    def structure_digest(self) -> str:
        """The EC-1 content hash of the topology core — its structural fingerprint."""
        return content_hash(self.canonical_core())

    @property
    def storage_id(self) -> str:
        """The deterministic ENG-001 identity of the topology (borne by this object).

        Derived through the CERTIFIED EC-1 ``content_hash`` (UDL-04 — no second identity
        scheme): identical topology always yields the identical id, so identity is
        reproducible and byte-stable (determinism, VC-4).
        """
        return f"{STORAGE_ID_PREFIX}-{self.name}-{self.structure_digest[:16]}"

    # -- meta-model participation (DATA-005 / DATA-010) ------------------------

    @property
    def meta_class(self) -> str:
        """V1 — the single meta-class this construct instantiates (DMC-06)."""
        return STORAGE_META_CLASS

    def meta_relationships(self) -> tuple[str, ...]:
        """V2 — the DMR-01…12 relationships the topology participates in."""
        return STORAGE_RELATIONSHIPS

    def placement_loci(self) -> tuple[str, ...]:
        """The explicit locus set of the topology (DTA-03)."""
        return self.loci

    @property
    def locus_count(self) -> int:
        """The size of the topology's declared locus set (DTA-03)."""
        return len(self.loci)

    def persisted_entity_ids(self) -> tuple[str, ...]:
        """The identities of the entities this topology persists (DMR-05; by reference)."""
        return tuple(r.entity_id for r in self.persisted_refs)

    def schema_refs(self) -> tuple[str, ...]:
        """The schema references the persisted data conforms to (DTA-07)."""
        return tuple(r.schema_ref for r in self.persisted_refs)

    def is_placement_explicit(self) -> bool:
        """DTA-03 / DTA-C1 — the locus set is explicit, non-empty, and decidable."""
        return bool(self.loci) and len(set(self.loci)) == len(self.loci)

    def is_durability_declared(self) -> bool:
        """DTA-04 / DTA-C2 — durability is a declared, decidable property."""
        return isinstance(self.durability, DurabilityLevel)

    def is_schema_aligned(self) -> bool:
        """DTA-07 / DTA-C4 / DTA-K3 — every persisted entity references a conformance schema."""
        return bool(self.persisted_refs) and all(
            r.schema_ref.startswith(f"{SCHEMA_ID_PREFIX}-") for r in self.persisted_refs
        )

    def is_topology_consistent(self) -> bool:
        """DXH-06 / DTA-C3 — locus cardinality / durability consistent with the kind."""
        if self.kind is StorageKind.LOCAL:
            return self.locus_count == 1
        if self.kind is StorageKind.DISTRIBUTED:
            return self.locus_count >= 2
        return self.durability is DurabilityLevel.TIERED  # TIERED

    def binds_runtime_by_reference(self) -> bool:
        """DMR-11 / DTA-02 / DTA-K2 — persistence binds a RUNTIME state reference only."""
        return self.runtime_ref.startswith(f"{RUNTIME_REF_PREFIX}:")

    def is_founding_acyclic(self) -> bool:
        """V4 / DMK-03 / DTA-C3 — the founding/persistence graph is acyclic.

        The topology's founding references (``persists`` → entities, ``behaves-as`` →
        RUNTIME state, schema alignment) are recorded by *identity reference*; none may
        reference the topology itself, so the founding graph is a DAG.
        """
        own = self.storage_id
        refs = set(self.persisted_entity_ids())
        refs.update(self.schema_refs())
        refs.add(self.runtime_ref)
        return own not in refs

    def persists_entity(self, entity_id: str) -> bool:
        """DMR-05 — whether this topology persists the entity identified by ``entity_id``."""
        return entity_id in self.persisted_entity_ids()

    def absorbs_persisted(self) -> bool:
        """DTA-09 / DMX-02 — the topology references the data it persists, never owns it."""
        return False

    # -- non-constitutiveness (UDL-15 / DTA-09) --------------------------------

    def confers_authority(self) -> bool:
        """UDL-15 / DTA-09 / C7 — a topology confers no authority (structurally none)."""
        return False

    def embeds_secret(self) -> bool:
        """UDL-15 / DTA-09 / RR-07 / C7 — True iff the topology appears to embed a secret."""
        haystack = canonical_json(self.canonical_core()).lower()
        return any(marker in haystack for marker in _SECRET_MARKERS)

    def redefines_el1(self) -> bool:
        """UDL-02 / DMI-05 / VC-5 — a topology redefines no EL-1/DMC-02/05/RL-F2 model."""
        return False

    def selects_technology(self) -> bool:
        """UDL-11 / DTA-01 / DTA-K5 — a topology selects no storage technology (material)."""
        return self._scan_technology()

    # -- lifecycle (UDL-12, forward-only) --------------------------------------

    def transition(self, to_state: StorageState) -> Storage:
        """Return a new topology advanced to ``to_state`` (forward-only; UDL-12).

        Raises:
            StorageError: on a backward transition (breaking change is supersession,
                never in-place mutation — DATA-010 §8; UDL-12/15).
        """
        if not isinstance(to_state, StorageState):
            raise StorageError("target state must be a DOS-01…05 state (UDL-12)")
        here = LIFECYCLE_ORDER.index(self.state)
        there = LIFECYCLE_ORDER.index(to_state)
        if there < here:
            raise StorageError(
                f"lifecycle is forward-only (UDL-12): "
                f"{self.state.value} → {to_state.value} is backward"
            )
        return replace(self, state=to_state)

    # -- serialization ----------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """A deterministic, serializable projection of the topology."""
        return {
            "storage_id": self.storage_id,
            "meta_class": self.meta_class,
            "name": self.name,
            "type_tag": self.type_tag,
            "kind": self.kind.value,
            "loci": list(self.loci),
            "locus_count": self.locus_count,
            "placement_explicit": self.is_placement_explicit(),
            "durability": self.durability.value,
            "durability_declared": self.is_durability_declared(),
            "persisted_refs": [r.to_dict() for r in self.persisted_refs],
            "persisted_entity_ids": list(self.persisted_entity_ids()),
            "schema_refs": list(self.schema_refs()),
            "schema_aligned": self.is_schema_aligned(),
            "topology_consistent": self.is_topology_consistent(),
            "runtime_ref": self.runtime_ref,
            "binds_runtime_by_reference": self.binds_runtime_by_reference(),
            "names_technology": self.names_technology(),
            "version": self.version,
            "supersedes": self.supersedes,
            "state": self.state.value,
            "relationships": list(self.meta_relationships()),
            "substrate_refs": list(STORAGE_SUBSTRATE_REFS),
            "absorbs_persisted": self.absorbs_persisted(),
        }


def make_storage(
    name: str,
    type_tag: str,
    loci: tuple[str, ...],
    persisted: tuple[tuple[Entity, Schema] | PersistedEntityRef, ...],
    runtime_ref: str,
    *,
    kind: StorageKind = StorageKind.LOCAL,
    durability: DurabilityLevel = DurabilityLevel.DURABLE,
    state: StorageState = StorageState.DEFINED,
    version: str = "1.0.0",
    supersedes: str = "",
) -> Storage:
    """Construct a well-formed :class:`Storage` (fail-closed factory).

    ``persisted`` is the set the topology persists — each item either a CERTIFIED
    ``(Entity, Schema)`` pair (reused by reference — the DMR-05 ``persists`` target,
    verified schema-conformant) or an already-projected :class:`PersistedEntityRef`.
    """
    refs = tuple(
        p if isinstance(p, PersistedEntityRef) else PersistedEntityRef.from_entity(p[0], p[1])
        for p in persisted
    )
    return Storage(
        name=name,
        type_tag=type_tag,
        kind=kind,
        loci=tuple(loci),
        durability=durability,
        persisted_refs=refs,
        runtime_ref=runtime_ref,
        state=state,
        version=version,
        supersedes=supersedes,
    )


__all__ = [
    "STORAGE_ID_PREFIX",
    "RUNTIME_REF_PREFIX",
    "ENTITY_ID_PREFIX",
    "SCHEMA_ID_PREFIX",
    "REUSE_REFS",
    "runtime_ref_for",
    "StorageError",
    "PersistedEntityRef",
    "Storage",
    "make_storage",
]
