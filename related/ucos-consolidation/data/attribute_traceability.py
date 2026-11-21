"""EC3-B10-U02 — Attribute traceability record (No-Orphan closure, GOV-001-T3).

Every realized Attribute records a closed lineage (package §6):

* **Backward:** ``DMC-03 → DATA-007 → DATA-005 → DATA-001 → ARCH-DATA-001 → 10-DATA@b7e7657``.
* **Founding unit:** ``values → DMC-01`` — the CERTIFIED Datum construct
  (EC3-B10-U01; ``UCOS-CERT-DMC-01-51e5964b38741e30``), referenced not redefined.
* **Substrate:** EC-1 ``engine/**`` realizing ``ENG-001/003/004/005`` — referenced,
  not redefined (UDL-02).
* **Forward:** the realized Attribute construct + its validation/certification
  evidence + completion report.

The record **reuses the CERTIFIED DMC-01 lineage type**
(:class:`data.traceability.TraceabilityRecord`) — no parallel traceability model —
and is deterministic and content-addressed via the CERTIFIED EC-1 ``content_hash``.
"""

from __future__ import annotations

from data.attribute import REUSE_REFS, Attribute
from data.attribute_meta import (
    ATTRIBUTE_SUBSTRATE_REFS,
    CONSTITUTIONAL_ANCHOR,
    DATUM_CERTIFICATION_ID,
    DATUM_FOUNDING_UNIT,
    IMPLEMENTATION_ANCHOR,
    TRACE_BACKWARD_ATTRIBUTE,
)

# --- DMC-01 reuse by reference (UDL-02) — the certified lineage type, never redefined
from data.traceability import TraceabilityRecord

#: The founding-unit citation recorded in every Attribute lineage (values → DMC-01).
FOUNDING_UNIT_REF: dict[str, str] = {
    "unit": DATUM_FOUNDING_UNIT,
    "meta_class": "DMC-01",
    "relationship": "DMR-02:values",
    "certification_id": DATUM_CERTIFICATION_ID,
    "reuse": "referenced, not redefined (UDL-06 / UDL-02 / DMX-02)",
}


def build_attribute_traceability(
    attribute: Attribute, *, unit: str, forward: tuple[str, ...]
) -> TraceabilityRecord:
    """Assemble the closed No-Orphan lineage record for ``attribute``.

    The founding-unit anchor (``values → DMC-01``) is recorded in the substrate-reuse
    map so the lineage cites the CERTIFIED Datum unit it builds upon (§6), reusing
    the DMC-01 :class:`TraceabilityRecord` type by reference.
    """
    substrate_reuse = dict(REUSE_REFS)
    substrate_reuse["founding_unit"] = (
        f"{DATUM_FOUNDING_UNIT} (DMC-01; {DATUM_CERTIFICATION_ID}) — values target, DMR-02"
    )
    return TraceabilityRecord(
        target_id=attribute.attribute_id,
        unit=unit,
        meta_class=attribute.meta_class,
        backward=TRACE_BACKWARD_ATTRIBUTE,
        substrate=ATTRIBUTE_SUBSTRATE_REFS,
        substrate_reuse=substrate_reuse,
        constitutional_anchor=CONSTITUTIONAL_ANCHOR,
        implementation_anchor=IMPLEMENTATION_ANCHOR,
        forward=tuple(forward),
    )


__all__ = ["FOUNDING_UNIT_REF", "build_attribute_traceability"]
