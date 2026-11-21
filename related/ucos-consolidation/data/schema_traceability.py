"""EC3-B10-U04 — Schema traceability record (No-Orphan closure, GOV-001-T3).

Every realized Schema records a closed lineage (DATA-009 §16):

* **Backward:** ``DMC-05 → DATA-009 → DATA-005 → DATA-001 → ARCH-DATA-001 → 10-DATA@b7e7657``.
* **Founding unit:** ``describes → DMC-02`` — the CERTIFIED Entity construct
  (EC3-B10-U03; ``UCOS-CERT-DMC-02-def41470d3bac196``), referenced not owned. The
  founding root closes transitively through ``describes → Entity bears Attribute
  values Datum`` (DMC-03/DMC-01; EC3-B10-U02/U01).
* **Substrate:** EC-1 ``engine/**`` realizing ``ENG-001/002/004/005`` — referenced,
  not redefined (UDL-02).
* **Forward:** the realized Schema construct + its validation/certification evidence
  + completion report.

The record **reuses the CERTIFIED DMC-01 lineage type**
(:class:`data.traceability.TraceabilityRecord`) — no parallel traceability model —
and is deterministic and content-addressed via the CERTIFIED EC-1 ``content_hash``.
"""

from __future__ import annotations

from data.schema import REUSE_REFS, Schema
from data.schema_meta import (
    ATTRIBUTE_CERTIFICATION_ID,
    ATTRIBUTE_FOUNDING_UNIT,
    CONSTITUTIONAL_ANCHOR,
    DATUM_CERTIFICATION_ID,
    DATUM_FOUNDING_UNIT,
    ENTITY_CERTIFICATION_ID,
    ENTITY_FOUNDING_UNIT,
    IMPLEMENTATION_ANCHOR,
    SCHEMA_SUBSTRATE_REFS,
    TRACE_BACKWARD_SCHEMA,
)

# --- DMC-01 reuse by reference (UDL-02) — the certified lineage type, never redefined
from data.traceability import TraceabilityRecord

#: The founding-unit citation recorded in every Schema lineage (describes → DMC-02).
FOUNDING_UNIT_REF: dict[str, str] = {
    "unit": ENTITY_FOUNDING_UNIT,
    "meta_class": "DMC-02",
    "relationship": "DMR-04:describes",
    "certification_id": ENTITY_CERTIFICATION_ID,
    "reuse": "referenced, not owned (DSA-09 / UDL-02 / DMX-02)",
    "transitive_root": (
        f"describes → Entity bears Attribute values Datum "
        f"({ATTRIBUTE_FOUNDING_UNIT}/DMC-03; {DATUM_FOUNDING_UNIT}/DMC-01)"
    ),
}


def build_schema_traceability(
    schema: Schema, *, unit: str, forward: tuple[str, ...]
) -> TraceabilityRecord:
    """Assemble the closed No-Orphan lineage record for ``schema``.

    The founding-unit anchor (``describes → DMC-02``) is recorded in the
    substrate-reuse map so the lineage cites the CERTIFIED Entity unit it builds upon
    (§16), reusing the DMC-01 :class:`TraceabilityRecord` type by reference.
    """
    substrate_reuse = dict(REUSE_REFS)
    substrate_reuse["founding_unit"] = (
        f"{ENTITY_FOUNDING_UNIT} (DMC-02; {ENTITY_CERTIFICATION_ID}) — describes target, DMR-04"
    )
    substrate_reuse["founding_root"] = (
        f"{ATTRIBUTE_FOUNDING_UNIT} (DMC-03; {ATTRIBUTE_CERTIFICATION_ID}) → "
        f"{DATUM_FOUNDING_UNIT} (DMC-01; {DATUM_CERTIFICATION_ID}) — transitive describes root"
    )
    return TraceabilityRecord(
        target_id=schema.schema_id,
        unit=unit,
        meta_class=schema.meta_class,
        backward=TRACE_BACKWARD_SCHEMA,
        substrate=SCHEMA_SUBSTRATE_REFS,
        substrate_reuse=substrate_reuse,
        constitutional_anchor=CONSTITUTIONAL_ANCHOR,
        implementation_anchor=IMPLEMENTATION_ANCHOR,
        forward=tuple(forward),
    )


__all__ = ["FOUNDING_UNIT_REF", "build_schema_traceability"]
