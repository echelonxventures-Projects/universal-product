"""EC3-B10-U08 — Quality traceability record (No-Orphan closure, GOV-001-T3).

Every realized Quality object records a closed lineage (DATA-013 §16):

* **Backward:** ``DMC-09 → DATA-013 → DATA-005 → DATA-001 → ARCH-DATA-001 → 10-DATA@b7e7657``.
* **Founding unit:** ``measures → DMC-02`` — the CERTIFIED Entity construct
  (EC3-B10-U03; ``UCOS-CERT-DMC-02-def41470d3bac196``), referenced not owned. The
  founding root closes transitively through ``measures → Entity bears Attribute values
  Datum`` (DMC-03/DMC-01; U02/U01). A schema-relative measure additionally cites the
  CERTIFIED DMC-05 Schema (EC3-B10-U04) by reference (DQA-05 / DQA-C2).
* **Substrate:** EC-1 ``engine/**`` realizing ``ENG-001/002/004/005`` + the frozen RL-F2
  RUNTIME policy concern (measurement by reference, DMR-11 / DQA-06) — referenced, not
  redefined (UDL-02).
* **Forward:** the realized Quality construct + its validation/certification evidence +
  completion report.

The record **reuses the CERTIFIED DMC-01 lineage type**
(:class:`data.traceability.TraceabilityRecord`) — no parallel traceability model — and is
deterministic and content-addressed via the CERTIFIED EC-1 ``content_hash``.
"""

from __future__ import annotations

from data.quality import REUSE_REFS, QualityObject
from data.quality_meta import (
    ATTRIBUTE_CERTIFICATION_ID,
    ATTRIBUTE_FOUNDING_UNIT,
    CONSTITUTIONAL_ANCHOR,
    DATUM_CERTIFICATION_ID,
    DATUM_FOUNDING_UNIT,
    ENTITY_CERTIFICATION_ID,
    ENTITY_FOUNDING_UNIT,
    IMPLEMENTATION_ANCHOR,
    QUALITY_SUBSTRATE_REFS,
    SCHEMA_CERTIFICATION_ID,
    SCHEMA_FOUNDING_UNIT,
    TRACE_BACKWARD_QUALITY,
)

# --- DMC-01 reuse by reference (UDL-02) — the certified lineage type, never redefined
from data.traceability import TraceabilityRecord

#: The founding-unit citation recorded in every Quality lineage (measures → DMC-02).
FOUNDING_UNIT_REF: dict[str, str] = {
    "unit": ENTITY_FOUNDING_UNIT,
    "meta_class": "DMC-02",
    "relationship": "DMR-08:measures",
    "certification_id": ENTITY_CERTIFICATION_ID,
    "reuse": "referenced, not owned (DQA-C3 / UDL-02 / DMX-02)",
    "transitive_root": (
        f"measures → Entity bears Attribute values Datum "
        f"({ATTRIBUTE_FOUNDING_UNIT}/DMC-03; {DATUM_FOUNDING_UNIT}/DMC-01)"
    ),
    "schema_relative_ref": (
        f"{SCHEMA_FOUNDING_UNIT} (DMC-05; {SCHEMA_CERTIFICATION_ID}) — declared schema, "
        f"cited by reference for completeness/consistency (DQA-05 / DQA-C2)"
    ),
}


def build_quality_traceability(
    quality: QualityObject, *, unit: str, forward: tuple[str, ...]
) -> TraceabilityRecord:
    """Assemble the closed No-Orphan lineage record for ``quality``.

    The founding-unit anchor (``measures → DMC-02``) is recorded in the substrate-reuse
    map so the lineage cites the CERTIFIED Entity unit it measures (§16), reusing the
    DMC-01 :class:`TraceabilityRecord` type by reference.
    """
    substrate_reuse = dict(REUSE_REFS)
    substrate_reuse["founding_unit"] = (
        f"{ENTITY_FOUNDING_UNIT} (DMC-02; {ENTITY_CERTIFICATION_ID}) — measures target, DMR-08"
    )
    substrate_reuse["founding_root"] = (
        f"{ATTRIBUTE_FOUNDING_UNIT} (DMC-03; {ATTRIBUTE_CERTIFICATION_ID}) → "
        f"{DATUM_FOUNDING_UNIT} (DMC-01; {DATUM_CERTIFICATION_ID}) — transitive measures root"
    )
    substrate_reuse["schema_reference"] = (
        f"{SCHEMA_FOUNDING_UNIT} (DMC-05; {SCHEMA_CERTIFICATION_ID}) — schema-relative "
        f"measurement reference (DQA-05 / DQA-C2)"
    )
    return TraceabilityRecord(
        target_id=quality.quality_id,
        unit=unit,
        meta_class=quality.meta_class,
        backward=TRACE_BACKWARD_QUALITY,
        substrate=QUALITY_SUBSTRATE_REFS,
        substrate_reuse=substrate_reuse,
        constitutional_anchor=CONSTITUTIONAL_ANCHOR,
        implementation_anchor=IMPLEMENTATION_ANCHOR,
        forward=tuple(forward),
    )


__all__ = ["FOUNDING_UNIT_REF", "build_quality_traceability"]
