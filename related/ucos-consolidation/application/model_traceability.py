"""EC3-B12-U11 — Meta-model traceability record (No-Orphan closure, GOV-001-T3).

Every realized Universal Application Meta-Model records a closed lineage (APPLICATION-005 §10):

* **Backward:** ``UAM → APPLICATION-005 → APPLICATION-004 → APPLICATION-003 → APPLICATION-001 →
  ARCH-APPLICATION-001 → 12-APPLICATION@b7e7657``.
* **Founding units:** the meta-model integrates the **ten CERTIFIED concern meta-class
  realizations** (AMC-01…10; units U01…U10), each cited by unit + certification id and
  referenced, not owned (UAL-02).
* **Substrate:** EC-1 ``engine/**`` realizing ``ENG-001/002/004/005`` + the frozen RL-F2
  RUNTIME concern (AMR-11 behaves-as / AMR-06 holds-state) + the frozen PL-F2 PLATFORM concern
  (AMR-07 assembled-by / AMR-12 composed-as) + the frozen SF-2 SERVICE concern (AMR-13
  consumes-operation) + the frozen DF-2 DATA concern (AMR-14 presents-data) — referenced, not
  redefined (UAL-02 / AMI-05).
* **Forward:** the realized meta-model construct + its validation/certification evidence +
  completion report.

The record **reuses the CERTIFIED AMC-01 lineage type**
(:class:`application.application_traceability.TraceabilityRecord`) — no parallel traceability
model — and is deterministic and content-addressed via the CERTIFIED EC-1 ``content_hash``.
"""

from __future__ import annotations

# --- AMC-01 reuse by reference (UAL-02) — the certified lineage type, never redefined
from application.application_traceability import TraceabilityRecord
from application.model import REUSE_REFS, MetaModel
from application.model_meta import (
    CONSTITUTIONAL_ANCHOR,
    IMPLEMENTATION_ANCHOR,
    MODEL_SUBSTRATE_REFS,
    TRACE_BACKWARD_MODEL,
)


def build_model_traceability(
    model: MetaModel, *, unit: str, forward: tuple[str, ...]
) -> TraceabilityRecord:
    """Assemble the closed No-Orphan lineage record for ``model``.

    The ten founding-unit anchors (the CERTIFIED AMC-01…10 realizations the model integrates)
    are recorded in the substrate-reuse map so the lineage cites every member it composes
    (§10), reusing the AMC-01 :class:`TraceabilityRecord` type by reference.
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
