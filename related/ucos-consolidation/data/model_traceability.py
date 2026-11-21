"""EC3-B10-U11 — Meta-model traceability record (No-Orphan closure, GOV-001-T3).

Every realized Universal Data Meta-Model records a closed lineage (DATA-005 §10):

* **Backward:** ``UDM → DATA-005 → DATA-004 → DATA-003 → DATA-001 → ARCH-DATA-001 →
  10-DATA@b7e7657``.
* **Founding units:** the meta-model integrates the **ten CERTIFIED concern meta-class
  realizations** (DMC-01…10; units U01…U10), each cited by unit + certification id and
  referenced, not owned (DMX-02 / UDL-02).
* **Substrate:** EC-1 ``engine/**`` realizing ``ENG-001/002/004/005`` + the frozen RL-F2
  RUNTIME concern (DMR-11 behaves-as) + the frozen PL-F2 PLATFORM concern (DMR-12
  composed-as) — referenced, not redefined (UDL-02 / DMI-05).
* **Forward:** the realized meta-model construct + its validation/certification evidence +
  completion report.

The record **reuses the CERTIFIED DMC-01 lineage type**
(:class:`data.traceability.TraceabilityRecord`) — no parallel traceability model — and is
deterministic and content-addressed via the CERTIFIED EC-1 ``content_hash``.
"""

from __future__ import annotations

from data.model import REUSE_REFS, MetaModel
from data.model_meta import (
    CONSTITUTIONAL_ANCHOR,
    IMPLEMENTATION_ANCHOR,
    MODEL_SUBSTRATE_REFS,
    TRACE_BACKWARD_MODEL,
)

# --- DMC-01 reuse by reference (UDL-02) — the certified lineage type, never redefined
from data.traceability import TraceabilityRecord


def build_model_traceability(
    model: MetaModel, *, unit: str, forward: tuple[str, ...]
) -> TraceabilityRecord:
    """Assemble the closed No-Orphan lineage record for ``model``.

    The ten founding-unit anchors (the CERTIFIED DMC-01…10 realizations the model
    integrates) are recorded in the substrate-reuse map so the lineage cites every member
    it composes (§10), reusing the DMC-01 :class:`TraceabilityRecord` type by reference.
    """
    substrate_reuse = dict(REUSE_REFS)
    for member in sorted(model.members, key=lambda m: m.meta_class):
        substrate_reuse[f"member_{member.meta_class}"] = (
            f"{member.unit} ({member.meta_class} {member.name}; {member.certification_id}) — "
            f"integrated by reference, not owned"
        )
    return TraceabilityRecord(
        target_id=model.model_id,
        unit=unit,
        meta_class=model.meta_class,
        backward=TRACE_BACKWARD_MODEL,
        substrate=MODEL_SUBSTRATE_REFS,
        substrate_reuse=substrate_reuse,
        constitutional_anchor=CONSTITUTIONAL_ANCHOR,
        implementation_anchor=IMPLEMENTATION_ANCHOR,
        forward=tuple(forward),
    )


__all__ = ["build_model_traceability"]
