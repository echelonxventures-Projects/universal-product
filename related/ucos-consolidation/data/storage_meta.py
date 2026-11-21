"""EC3-B10-U05 — Storage meta-model constants (read-only projections of DATA-010).

This module carries, as executable constants, the fixed identifiers of the frozen
Data Foundation and the ACTIVE Storage Architecture (DATA-001 Constitution, DATA-004
Taxonomy, DATA-005 Meta-Model, **DATA-010 Universal Data Storage Architecture**) that
the Storage realization (**DMC-06**) must conform to. It **defines no new law and
redefines no foundation concept** (UDL-02 / DMI-05 / UDL-15); it only names the frozen
obligations so the realization can be checked against them deterministically.

Everything here is derived verbatim from the frozen ``10-DATA/`` specification at the
constitutional anchor ``b7e7657`` (DATA-010 §3…§17) — no obligation is invented, none
is dropped. Storage is **abstract topology only** — it selects no engine, database,
file/serialization format, query language, broker, warehouse/lake, cache, cloud data
service, or vendor (UDL-11). Shared foundation constants (anchors, laws, compliance
conditions, meta-validity gate, CCE gates, lifecycle states) are **reused by reference**
from the CERTIFIED DMC-01 surface (:mod:`data.meta`); re-exported, never re-defined.
"""

from __future__ import annotations

from enum import Enum

# --- DMC-01 reuse by reference (UDL-02) — shared foundation constants, never re-defined
from data.meta import (
    CCE_GATES,
    CONSTITUTIONAL_ANCHOR,
    DATA_COMPLIANCE,
    DATA_LAWS,
    IMPLEMENTATION_ANCHOR,
    LIFECYCLE_ORDER,
    META_CLASSES,
    META_RELATIONSHIPS,
    META_VALIDITY_CHECKS,
    DatumState,
)

# ---------------------------------------------------------------------------
# The Storage lifecycle reuses the frozen ontology lifecycle DOS-01…05.
# DATA-010 §8 — a storage topology follows DOS-01…05 forward-only (DOI-05; UDL-12).
# Identical forward-only state machine as the Datum/Attribute/Entity/Schema, so it is
# reused by reference (no parallel lifecycle model).
# ---------------------------------------------------------------------------

#: The Storage lifecycle state type (reused DOS-01…05; DATA-010 §8, UDL-12).
StorageState = DatumState

# ---------------------------------------------------------------------------
# DATA-005 §2 / DATA-010 §3 — the Storage meta-class and its founding units
# ---------------------------------------------------------------------------

#: The Storage meta-class id (DATA-005 §2; DMC-06).
STORAGE_META_CLASS = "DMC-06"

#: The CERTIFIED founding unit whose schema the Storage aligns to (DTA-07 / DTA-K3).
#: A storage topology persists **schema-conformant** data; it references the CERTIFIED
#: DMC-05 Schema **by reference** and carries no separate structural model (DTA-07).
SCHEMA_FOUNDING_UNIT = "EC3-B10-U04"
#: The certification id of the CERTIFIED DMC-05 Schema construct (founding-unit anchor).
SCHEMA_CERTIFICATION_ID = "UCOS-CERT-DMC-05-e9edc215907c8695"

#: The CERTIFIED unit whose construct the Storage ``persists`` (DMR-05, reference-only).
ENTITY_FOUNDING_UNIT = "EC3-B10-U03"
#: The certification id of the CERTIFIED DMC-02 Entity construct (persists anchor).
ENTITY_CERTIFICATION_ID = "UCOS-CERT-DMC-02-def41470d3bac196"

#: The transitively-closed founding roots (persists → Entity bears Attribute values Datum).
ATTRIBUTE_FOUNDING_UNIT = "EC3-B10-U02"
ATTRIBUTE_CERTIFICATION_ID = "UCOS-CERT-DMC-03-c57d36d3dbb2763d"
DATUM_FOUNDING_UNIT = "EC3-B10-U01"
DATUM_CERTIFICATION_ID = "UCOS-CERT-DMC-01-51e5964b38741e30"

# ---------------------------------------------------------------------------
# Traceability anchors (No-Orphan spine — derived from DATA-010 §16)
# ---------------------------------------------------------------------------

#: The backward traceability chain every realized Storage records (DATA-010 → root).
TRACE_BACKWARD_STORAGE: tuple[str, ...] = (
    "DMC-06",  # DATA-005 §2 / DATA-010 §3 — Storage meta-class
    "DATA-010",  # Universal Data Storage Architecture (UDTA)
    "DATA-005",  # Universal Data Meta-Model
    "DATA-001",  # Universal Data Constitution (UDL-01…15; esp. UDL-11)
    "ARCH-DATA-001",  # Governing Data architecture model
    f"10-DATA@{CONSTITUTIONAL_ANCHOR}",  # frozen specification set
)

#: The frozen EL-1 substrate the Storage reuses by reference (UDL-02; DATA-010 §3):
#:   ENG-001 Identity (identified topology — DTA-K1); ENG-002 Object (the topology IS an
#:   object); ENG-004 Type (topology + kind typing — DTA-01); ENG-005 Reference (persists
#:   entities + binds RUNTIME state/PLATFORM by reference — DMR-05/11/12).
STORAGE_SUBSTRATE_REFS: tuple[str, ...] = (
    "ENG-001",  # Identity   (identified topology — DTA-K1 / UDL-04)
    "ENG-002",  # Object     (the topology IS an ENG-002 object — UDL-05)
    "ENG-004",  # Type       (topology + kind typedness — DTA-01 / UDL-03)
    "ENG-005",  # Reference  (persists + RUNTIME/PLATFORM references — DMR-05/11/12)
)

# ---------------------------------------------------------------------------
# DATA-004 §3 / DATA-010 §5 — DXH-06 Storage Hierarchy (abstract topology)
# ---------------------------------------------------------------------------


class StorageKind(str, Enum):
    """DXH-06 Storage Hierarchy (DATA-004 §3; DATA-010 §5) — abstract topology only.

    A storage topology is classified by exactly one kind (single-facet, DXC-02); none
    names or implies a product (UDL-11):
    """

    LOCAL = "Local-Topology"  # single-locus persistence concept
    DISTRIBUTED = "Distributed-Topology"  # multi-locus persistence concept (partition/replicate)
    TIERED = "Tiered-Topology"  # durability/latency-tiered persistence concept


class DurabilityLevel(str, Enum):
    """DTA-04 — the declared, decidable durability property of a topology.

    Durability is a *declared* concept, never assumed (DTA-C2); it names no product.
    """

    TRANSIENT = "Transient"  # non-durable placement concept (ephemeral)
    DURABLE = "Durable"  # durable placement concept
    TIERED = "Tiered"  # durability/latency-tiered placement concept


# ---------------------------------------------------------------------------
# DATA-010 §6 — Storage relationships (within the DMR-01…12 closure)
# ---------------------------------------------------------------------------

#: The meta-relationships in which the *minimal* Storage participates (DATA-010 §6):
#:   DMR-05 persists     (Storage ← Entity; reference-only; MATERIAL — persists the entity)
#:   DMR-10 identified-by(Storage → ENG-001 via ENG-002; MATERIAL)
#:   DMR-11 behaves-as   (Storage → RUNTIME state persistence; reference-only; MATERIAL —
#:                        persistence behavior binds by reference, DTA-02/DTA-K2)
#: The composition relationship (DMR-12 composed-as → PLATFORM deployment topology) is
#: **reference-only** (DATA-010 §6/§7) and out of scope for the minimal topology; it is
#: recorded as deferred. No relationship outside DMR-01…12 is admitted (DOI-01 / DMI-02).
STORAGE_RELATIONSHIPS: tuple[str, ...] = ("DMR-05", "DMR-10", "DMR-11")

#: Reference-only relationships a storage topology may cite but never redefine (§6/§7).
STORAGE_DEFERRED_RELATIONSHIPS: tuple[str, ...] = ("DMR-12",)

# ---------------------------------------------------------------------------
# DATA-010 §4 — Storage principles (DTA-01…10)
# ---------------------------------------------------------------------------

#: The ten Storage principles (DATA-010 §4), each mapped to its short obligation.
STORAGE_PRINCIPLES: dict[str, str] = {
    "DTA-01": "Storage Independence — abstract topology only; no engine/format/query/vendor.",
    "DTA-02": "Persistence by Reference — persistence binds by reference to RUNTIME state.",
    "DTA-03": "Placement Explicitness — the conceptual placement (locus) is declared.",
    "DTA-04": "Durability Declaration — durability (transient/durable/tiered) is declared.",
    "DTA-05": "Distribution Neutrality — distribution/replication are topology concepts.",
    "DTA-06": "Retrieval as Concept — retrieval is query-as-concept; no query language.",
    "DTA-07": "Schema Alignment — stored data is schema-conformant (DATA-009); no separate model.",
    "DTA-08": "Additive Growth — new topologies append additively (DXH-06); no renumber.",
    "DTA-09": "Non-Constitutiveness — confers no authority, embeds no secret, selects no tech.",
    "DTA-10": "Reuse Labelling — a consumed ARCH/CAT/… asset is INPUT, never COMPLETION.",
}

# ---------------------------------------------------------------------------
# DATA-010 §9 — Storage topology rules (DTA-C1…C5)
# ---------------------------------------------------------------------------

#: The five topology rules (DATA-010 §9).
STORAGE_TOPOLOGY_RULES: dict[str, str] = {
    "DTA-C1": "A topology declares its locus set (placement) explicitly (DTA-03).",
    "DTA-C2": "Durability is a declared, decidable property, not assumed (DTA-04).",
    "DTA-C3": "Distribution/replication are topology concepts; no product named (DTA-05).",
    "DTA-C4": "Stored data conforms to a DATA-009 schema; adds no structural model (DTA-07).",
    "DTA-C5": "Retrieval is query-as-concept; no query language/index/engine selected (DTA-06).",
}

# ---------------------------------------------------------------------------
# DATA-010 §10 — Storage contracts & constraints (DTA-K1…K5)
# ---------------------------------------------------------------------------

#: The five Storage contracts / constraints (DATA-010 §10).
STORAGE_CONSTRAINTS: dict[str, str] = {
    "DTA-K1": "Every storage construct is typed (ENG-004) and identified (ENG-001) — DMK-01.",
    "DTA-K2": "Persistence resolves to a RUNTIME state reference; none redefined — DMK-05.",
    "DTA-K3": "Stored data is schema-conformant (DATA-009) — DMK-04.",
    "DTA-K4": "Composition/deployment topology resolves to a PL-F2 reference; none redefined.",
    "DTA-K5": "No storage construct selects engine/format/query language or confers authority.",
}

# ---------------------------------------------------------------------------
# DATA-001 §7 — Data Laws applicability for the Storage construct
# ---------------------------------------------------------------------------

#: The Data laws the Storage construct is directly obligated by (subset of UDL-*),
#: with **UDL-11 (Storage Independence) now materially in scope at the strongest level**.
STORAGE_APPLICABLE_LAWS: tuple[str, ...] = (
    "UDL-01",  # founded on frozen EL-1 (layer)
    "UDL-02",  # reuse by reference; redefine 0 (incl. RUNTIME state + certified Entity/Schema)
    "UDL-03",  # typed (topology + kind)
    "UDL-04",  # identified via object (one scheme)
    "UDL-05",  # objecthood
    "UDL-09",  # references via ENG-005; founding acyclic
    "UDL-11",  # STORAGE INDEPENDENCE — abstract topology only; no engine/format/query/vendor
    "UDL-12",  # forward-only lifecycle + supersession on breaking change
    "UDL-13",  # non-enforcing governance (record-only)
    "UDL-14",  # evaluative facets (quality)
    "UDL-15",  # non-constitutive
)

#: Laws scoped to units not realized here (deferred for the Storage construct):
#:   UDL-06 (ENG-003 value fidelity) is the Datum's obligation — storage persists data
#:   transitively; UDL-07 (entity boundedness) is the Entity unit's obligation; UDL-08
#:   (attribute typedness) is the Attribute unit's obligation; UDL-10 (schema
#:   explicitness) is the Schema unit's obligation (storage aligns to it by reference).
STORAGE_DEFERRED_LAWS: tuple[str, ...] = ("UDL-06", "UDL-07", "UDL-08", "UDL-10")

# ---------------------------------------------------------------------------
# DATA-005 §4 — meta-constraints the Storage is bound by
# ---------------------------------------------------------------------------

#: Meta-constraints a Storage is bound by (DATA-005 §4; DATA-010 §15).
STORAGE_META_CONSTRAINTS: dict[str, str] = {
    "DMK-01": "Typed (ENG-004), identified (ENG-001), objecthood-bound (ENG-002).",
    "DMK-03": "The founding/persistence meta-relationship graph is acyclic (a DAG).",
    "DMK-04": "Stored data is schema-conformant before ACTIVE (DATA-009 alignment).",
    "DMK-05": "Persistence behavior resolves to a RUNTIME state reference; none redefined.",
    "DMK-08": "Selects no technology and confers no authority.",
}

__all__ = [
    # reused-by-reference foundation constants (re-exported, not re-defined)
    "CCE_GATES",
    "CONSTITUTIONAL_ANCHOR",
    "DATA_COMPLIANCE",
    "DATA_LAWS",
    "IMPLEMENTATION_ANCHOR",
    "LIFECYCLE_ORDER",
    "META_CLASSES",
    "META_RELATIONSHIPS",
    "META_VALIDITY_CHECKS",
    "StorageState",
    # storage-specific projections
    "STORAGE_META_CLASS",
    "SCHEMA_FOUNDING_UNIT",
    "SCHEMA_CERTIFICATION_ID",
    "ENTITY_FOUNDING_UNIT",
    "ENTITY_CERTIFICATION_ID",
    "ATTRIBUTE_FOUNDING_UNIT",
    "ATTRIBUTE_CERTIFICATION_ID",
    "DATUM_FOUNDING_UNIT",
    "DATUM_CERTIFICATION_ID",
    "TRACE_BACKWARD_STORAGE",
    "STORAGE_SUBSTRATE_REFS",
    "StorageKind",
    "DurabilityLevel",
    "STORAGE_RELATIONSHIPS",
    "STORAGE_DEFERRED_RELATIONSHIPS",
    "STORAGE_PRINCIPLES",
    "STORAGE_TOPOLOGY_RULES",
    "STORAGE_CONSTRAINTS",
    "STORAGE_APPLICABLE_LAWS",
    "STORAGE_DEFERRED_LAWS",
    "STORAGE_META_CONSTRAINTS",
]
