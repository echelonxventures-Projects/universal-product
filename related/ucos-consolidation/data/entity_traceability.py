"""EC3-B10-U03 — Entity traceability record (No-Orphan closure, GOV-001-T3).

Every realized Entity records a closed lineage (DATA-006 §16):

* **Backward:** ``DMC-02 → DATA-006 → DATA-005 → DATA-001 → ARCH-DATA-001 → 10-DATA@b7e7657``.
* **Founding unit:** ``bears → DMC-03`` — the CERTIFIED Attribute construct
  (EC3-B10-U02; ``UCOS-CERT-DMC-03-c57d36d3dbb2763d``), referenced not owned. The
  founding root closes transitively through ``bears → Attribute → values → Datum``
  (DMC-01; EC3-B10-U01; ``UCOS-CERT-DMC-01-51e5964b38741e30``).
* **Substrate:** EC-1 ``engine/**`` realizing ``ENG-001/002/004/005`` — referenced,
  not redefined (UDL-02).
* **Forward:** the realized Entity construct + its validation/certification evidence
  + completion report.

The record **reuses the CERTIFIED DMC-01 lineage type**
(:class:`data.traceability.TraceabilityRecord`) — no parallel traceability model —
and is deterministic and content-addressed via the CERTIFIED EC-1 ``content_hash``.
"""

from __future__ import annotations

from data.entity import REUSE_REFS, Entity
from data.entity_meta import (
    ATTRIBUTE_CERTIFICATION_ID,
    ATTRIBUTE_FOUNDING_UNIT,
    CONSTITUTIONAL_ANCHOR,
    DATUM_CERTIFICATION_ID,
    DATUM_FOUNDING_UNIT,
    ENTITY_SUBSTRATE_REFS,
    IMPLEMENTATION_ANCHOR,
    TRACE_BACKWARD_ENTITY,
)

# --- DMC-01 reuse by reference (UDL-02) — the certified lineage type, never redefined
from data.traceability import TraceabilityRecord

#: The founding-unit citation recorded in every Entity lineage (bears → DMC-03).
FOUNDING_UNIT_REF: dict[str, str] = {
    "unit": ATTRIBUTE_FOUNDING_UNIT,
    "meta_class": "DMC-03",
    "relationship": "DMR-01:bears",
    "certification_id": ATTRIBUTE_CERTIFICATION_ID,
    "reuse": "referenced, not owned (DEA-04 / UDL-02 / DMX-02)",
    "transitive_root": (
        f"bears → Attribute → values → Datum ({DATUM_FOUNDING_UNIT}; DMC-01; "
        f"{DATUM_CERTIFICATION_ID})"
    ),
}


def build_entity_traceability(
    entity: Entity, *, unit: str, forward: tuple[str, ...]
) -> TraceabilityRecord:
    """Assemble the closed No-Orphan lineage record for ``entity``.

    The founding-unit anchor (``bears → DMC-03``) is recorded in the substrate-reuse
    map so the lineage cites the CERTIFIED Attribute unit it builds upon (§16),
    reusing the DMC-01 :class:`TraceabilityRecord` type by reference.
    """
    substrate_reuse = dict(REUSE_REFS)
    substrate_reuse["founding_unit"] = (
        f"{ATTRIBUTE_FOUNDING_UNIT} (DMC-03; {ATTRIBUTE_CERTIFICATION_ID}) — bears target, DMR-01"
    )
    substrate_reuse["founding_root"] = (
        f"{DATUM_FOUNDING_UNIT} (DMC-01; {DATUM_CERTIFICATION_ID}) — transitive values target"
    )
    return TraceabilityRecord(
        target_id=entity.entity_id,
        unit=unit,
        meta_class=entity.meta_class,
        backward=TRACE_BACKWARD_ENTITY,
        substrate=ENTITY_SUBSTRATE_REFS,
        substrate_reuse=substrate_reuse,
        constitutional_anchor=CONSTITUTIONAL_ANCHOR,
        implementation_anchor=IMPLEMENTATION_ANCHOR,
        forward=tuple(forward),
    )


__all__ = ["FOUNDING_UNIT_REF", "build_entity_traceability"]
