"""EC3-B10-U07 — Governance traceability record (No-Orphan closure, GOV-001-T3).

Every realized Governance object records a closed lineage (DATA-012 §16):

* **Backward:** ``DMC-08 → DATA-012 → DATA-005 → DATA-001 → ARCH-DATA-001 → 10-DATA@b7e7657``.
* **Founding unit:** ``governs → DMC-02`` — the CERTIFIED Entity construct
  (EC3-B10-U03; ``UCOS-CERT-DMC-02-def41470d3bac196``), referenced not owned. The
  founding root closes transitively through ``governs → Entity bears Attribute values
  Datum`` (DMC-03/DMC-01; U02/U01).
* **Substrate:** EC-1 ``engine/**`` realizing ``ENG-001/002/004/005`` + the frozen RL-F2
  RUNTIME policy concern (evaluation by reference, DMR-11 / DGA-07) — referenced, not
  redefined (UDL-02).
* **Forward:** the realized Governance construct + its validation/certification evidence +
  completion report.

The record **reuses the CERTIFIED DMC-01 lineage type**
(:class:`data.traceability.TraceabilityRecord`) — no parallel traceability model —
and is deterministic and content-addressed via the CERTIFIED EC-1 ``content_hash``.
"""

from __future__ import annotations

from data.governance import REUSE_REFS, GovernanceObject
from data.governance_meta import (
    ATTRIBUTE_CERTIFICATION_ID,
    ATTRIBUTE_FOUNDING_UNIT,
    CONSTITUTIONAL_ANCHOR,
    DATUM_CERTIFICATION_ID,
    DATUM_FOUNDING_UNIT,
    ENTITY_CERTIFICATION_ID,
    ENTITY_FOUNDING_UNIT,
    GOVERNANCE_SUBSTRATE_REFS,
    IMPLEMENTATION_ANCHOR,
    TRACE_BACKWARD_GOVERNANCE,
)

# --- DMC-01 reuse by reference (UDL-02) — the certified lineage type, never redefined
from data.traceability import TraceabilityRecord

#: The founding-unit citation recorded in every Governance lineage (governs → DMC-02).
FOUNDING_UNIT_REF: dict[str, str] = {
    "unit": ENTITY_FOUNDING_UNIT,
    "meta_class": "DMC-02",
    "relationship": "DMR-07:governs",
    "certification_id": ENTITY_CERTIFICATION_ID,
    "reuse": "referenced, not owned (DGA-C4 / UDL-02 / DMX-02)",
    "transitive_root": (
        f"governs → Entity bears Attribute values Datum "
        f"({ATTRIBUTE_FOUNDING_UNIT}/DMC-03; {DATUM_FOUNDING_UNIT}/DMC-01)"
    ),
}


def build_governance_traceability(
    governance: GovernanceObject, *, unit: str, forward: tuple[str, ...]
) -> TraceabilityRecord:
    """Assemble the closed No-Orphan lineage record for ``governance``.

    The founding-unit anchor (``governs → DMC-02``) is recorded in the substrate-reuse
    map so the lineage cites the CERTIFIED Entity unit it evaluates (§16), reusing the
    DMC-01 :class:`TraceabilityRecord` type by reference.
    """
    substrate_reuse = dict(REUSE_REFS)
    substrate_reuse["founding_unit"] = (
        f"{ENTITY_FOUNDING_UNIT} (DMC-02; {ENTITY_CERTIFICATION_ID}) — governs target, DMR-07"
    )
    substrate_reuse["founding_root"] = (
        f"{ATTRIBUTE_FOUNDING_UNIT} (DMC-03; {ATTRIBUTE_CERTIFICATION_ID}) → "
        f"{DATUM_FOUNDING_UNIT} (DMC-01; {DATUM_CERTIFICATION_ID}) — transitive governs root"
    )
    return TraceabilityRecord(
        target_id=governance.governance_id,
        unit=unit,
        meta_class=governance.meta_class,
        backward=TRACE_BACKWARD_GOVERNANCE,
        substrate=GOVERNANCE_SUBSTRATE_REFS,
        substrate_reuse=substrate_reuse,
        constitutional_anchor=CONSTITUTIONAL_ANCHOR,
        implementation_anchor=IMPLEMENTATION_ANCHOR,
        forward=tuple(forward),
    )


__all__ = ["FOUNDING_UNIT_REF", "build_governance_traceability"]
