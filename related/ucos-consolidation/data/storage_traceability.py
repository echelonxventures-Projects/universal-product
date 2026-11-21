"""EC3-B10-U05 — Storage traceability record (No-Orphan closure, GOV-001-T3).

Every realized Storage records a closed lineage (DATA-010 §16):

* **Backward:** ``DMC-06 → DATA-010 → DATA-005 → DATA-001 → ARCH-DATA-001 → 10-DATA@b7e7657``.
* **Founding unit:** ``schema-aligned → DMC-05`` — the CERTIFIED Schema construct
  (EC3-B10-U04; ``UCOS-CERT-DMC-05-e9edc215907c8695``), referenced not owned; and
  ``persists → DMC-02`` — the CERTIFIED Entity construct (EC3-B10-U03;
  ``UCOS-CERT-DMC-02-def41470d3bac196``). The founding root closes transitively through
  ``persists → Entity bears Attribute values Datum`` (DMC-03/DMC-01; U02/U01).
* **Substrate:** EC-1 ``engine/**`` realizing ``ENG-001/002/004/005`` + the frozen RL-F2
  RUNTIME state concern (persistence by reference, DMR-11) — referenced, not redefined
  (UDL-02).
* **Forward:** the realized Storage construct + its validation/certification evidence +
  completion report.

The record **reuses the CERTIFIED DMC-01 lineage type**
(:class:`data.traceability.TraceabilityRecord`) — no parallel traceability model —
and is deterministic and content-addressed via the CERTIFIED EC-1 ``content_hash``.
"""

from __future__ import annotations

from data.storage import REUSE_REFS, Storage
from data.storage_meta import (
    ATTRIBUTE_CERTIFICATION_ID,
    ATTRIBUTE_FOUNDING_UNIT,
    CONSTITUTIONAL_ANCHOR,
    DATUM_CERTIFICATION_ID,
    DATUM_FOUNDING_UNIT,
    ENTITY_CERTIFICATION_ID,
    ENTITY_FOUNDING_UNIT,
    IMPLEMENTATION_ANCHOR,
    SCHEMA_CERTIFICATION_ID,
    SCHEMA_FOUNDING_UNIT,
    STORAGE_SUBSTRATE_REFS,
    TRACE_BACKWARD_STORAGE,
)

# --- DMC-01 reuse by reference (UDL-02) — the certified lineage type, never redefined
from data.traceability import TraceabilityRecord

#: The founding-unit citation recorded in every Storage lineage (schema-aligned → DMC-05).
FOUNDING_UNIT_REF: dict[str, str] = {
    "unit": SCHEMA_FOUNDING_UNIT,
    "meta_class": "DMC-05",
    "relationship": "DTA-07:schema-aligned",
    "certification_id": SCHEMA_CERTIFICATION_ID,
    "reuse": "referenced, not owned (DTA-09 / UDL-02 / DMX-02)",
    "persists": (
        f"persists → DMC-02 ({ENTITY_FOUNDING_UNIT}; {ENTITY_CERTIFICATION_ID}) — DMR-05"
    ),
    "transitive_root": (
        f"persists → Entity bears Attribute values Datum "
        f"({ATTRIBUTE_FOUNDING_UNIT}/DMC-03; {DATUM_FOUNDING_UNIT}/DMC-01)"
    ),
}


def build_storage_traceability(
    storage: Storage, *, unit: str, forward: tuple[str, ...]
) -> TraceabilityRecord:
    """Assemble the closed No-Orphan lineage record for ``storage``.

    The founding-unit anchors (``schema-aligned → DMC-05`` and ``persists → DMC-02``) are
    recorded in the substrate-reuse map so the lineage cites the CERTIFIED Schema and
    Entity units it builds upon (§16), reusing the DMC-01 :class:`TraceabilityRecord`
    type by reference.
    """
    substrate_reuse = dict(REUSE_REFS)
    substrate_reuse["founding_unit"] = (
        f"{SCHEMA_FOUNDING_UNIT} (DMC-05; {SCHEMA_CERTIFICATION_ID}) — schema-aligned, DTA-07"
    )
    substrate_reuse["founding_persists"] = (
        f"{ENTITY_FOUNDING_UNIT} (DMC-02; {ENTITY_CERTIFICATION_ID}) — persists target, DMR-05"
    )
    substrate_reuse["founding_root"] = (
        f"{ATTRIBUTE_FOUNDING_UNIT} (DMC-03; {ATTRIBUTE_CERTIFICATION_ID}) → "
        f"{DATUM_FOUNDING_UNIT} (DMC-01; {DATUM_CERTIFICATION_ID}) — transitive persists root"
    )
    return TraceabilityRecord(
        target_id=storage.storage_id,
        unit=unit,
        meta_class=storage.meta_class,
        backward=TRACE_BACKWARD_STORAGE,
        substrate=STORAGE_SUBSTRATE_REFS,
        substrate_reuse=substrate_reuse,
        constitutional_anchor=CONSTITUTIONAL_ANCHOR,
        implementation_anchor=IMPLEMENTATION_ANCHOR,
        forward=tuple(forward),
    )


__all__ = ["FOUNDING_UNIT_REF", "build_storage_traceability"]
