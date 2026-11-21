"""EC3-B11-U11 — Meta-model traceability record (No-Orphan closure, GOV-001-T3).

Every realized Universal Service Meta-Model records a closed lineage (SERVICE-005 §10):

* **Backward:** ``USM → SERVICE-005 → SERVICE-004 → SERVICE-003 → SERVICE-001 →
  ARCH-SERVICE-001 → 11-SERVICE@b7e7657``.
* **Founding units:** the meta-model integrates the **ten CERTIFIED concern meta-class
  realizations** (SMC-01…10; units U01…U10), each cited by unit + certification id and
  referenced, not owned (SMX-02 / USL-02).
* **Substrate:** EC-1 ``engine/**`` realizing ``ENG-001/002/004/005`` + the frozen RL-F2
  RUNTIME concern (SMR-11 behaves-as / SMR-07 executes) + the frozen PL-F2 PLATFORM concern
  (SMR-12 composed-as) + the frozen DF-2 DATA concern (SMR-13 operates-on) — referenced, not
  redefined (USL-02 / SMI-05).
* **Forward:** the realized meta-model construct + its validation/certification evidence +
  completion report.

The record **reuses the CERTIFIED SMC-01 lineage type**
(:class:`service.service_traceability.TraceabilityRecord`) — no parallel traceability model
— and is deterministic and content-addressed via the CERTIFIED EC-1 ``content_hash``.
"""

from __future__ import annotations

from service.model import REUSE_REFS, MetaModel
from service.model_meta import (
    CONSTITUTIONAL_ANCHOR,
    IMPLEMENTATION_ANCHOR,
    MODEL_SUBSTRATE_REFS,
    TRACE_BACKWARD_MODEL,
)

# --- SMC-01 reuse by reference (USL-02) — the certified lineage type, never redefined
from service.service_traceability import TraceabilityRecord


def build_model_traceability(
    model: MetaModel, *, unit: str, forward: tuple[str, ...]
) -> TraceabilityRecord:
    """Assemble the closed No-Orphan lineage record for ``model``.

    The ten founding-unit anchors (the CERTIFIED SMC-01…10 realizations the model
    integrates) are recorded in the substrate-reuse map so the lineage cites every member it
    composes (§10), reusing the SMC-01 :class:`TraceabilityRecord` type by reference.
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
