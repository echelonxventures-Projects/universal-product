"""EC3-B11-U07 — Orchestration meta-model constants (read-only projections of SERVICE-001…011).

Carries, as executable constants, the fixed identifiers of the frozen Service Foundation
that the Universal **Orchestration** realization (SMC-07) must conform to. It **defines no new
law and redefines no foundation concept** (USL-02 / SMI-05 / USL-15); it only names the frozen
obligations so the realization can be checked deterministically.

Derived verbatim from the frozen ``11-SERVICE/`` specification at anchor ``b7e7657``:

* SMC-07 **Orchestration** models ontology entity **SOE-07** — *"the coordinated arrangement of
  operations and services toward an outcome"* (SERVICE-003 §2; SERVICE-011 §3) — the
  time-ordered / conditional coordination distinct from the structural assembly of Composition,
  classified by hierarchy **SXH-07** (Sequential / Parallel / Choreographed; SERVICE-004 /
  SERVICE-011 §5).
* An Orchestration **orchestrates** operations/services (SMR-06 orchestrates; SOR-06;
  reference-only), **composes** the coordinated set (SMR-05 composes; SOR-05; reference-only,
  founding-acyclic), is **bound-by** a composition contract (SMR-02; SOR-02; founding, acyclic),
  **behaves-as** the RUNTIME workflow/orchestration/event concern (SMR-11; SOR-11; RUNTIME-009/
  013/008, by reference), carries inter-step data via **operates-on** (SMR-13; SOR-13; DF-2, by
  reference), and is identified via **identified-by** (SMR-10; SOR-10; ENG-001 via ENG-002).
* Orchestration principles SOO-01…10 (SERVICE-011 §4) govern the construct; **USL-09**
  (composition by reference) and **USL-10** (execution by reference) are the governing laws,
  grounded in USL-02/06/11.
"""

from __future__ import annotations

from enum import Enum

from service.service_meta import (
    CONSTITUTIONAL_ANCHOR,
    LIFECYCLE_ORDER,
    META_RELATIONSHIPS,
    SERVICE_COMPLIANCE,
    SERVICE_LAWS,
    ServiceState,
)

# Re-export the frozen sets (single source of truth — no duplication).
__all_reexport__ = (
    CONSTITUTIONAL_ANCHOR,
    LIFECYCLE_ORDER,
    META_RELATIONSHIPS,
    SERVICE_COMPLIANCE,
    SERVICE_LAWS,
    ServiceState,
)

#: The Orchestration meta-class id (SERVICE-005 §2).
ORCHESTRATION_META_CLASS = "SMC-07"

#: Backward traceability chain every realized Orchestration records (SERVICE-005 → root).
TRACE_BACKWARD_ORCHESTRATION: tuple[str, ...] = (
    "SMC-07",  # SERVICE-005 §2 — Orchestration meta-class
    "SOE-07",  # SERVICE-003 §2 — Orchestration ontology entity
    "SERVICE-011",  # Universal Service Orchestration Architecture (concern architecture)
    "SERVICE-005",  # Universal Service Meta-Model
    "SERVICE-001",  # Universal Service Constitution (USL-01…15)
    "ARCH-SERVICE-001",  # Governing Service architecture model
    f"11-SERVICE@{CONSTITUTIONAL_ANCHOR}",  # frozen specification set
)

#: The frozen foundations an Orchestration reuses by reference (USL-02).
#:   ENG-001…005 (EL-1) · RL-F2 (workflow/orchestration/event behavior, SMR-11; RUNTIME-009/
#:   013/008) · DF-2 (inter-step data, SMR-13). Orchestration binds RUNTIME by reference
#:   (SMR-11 behaves-as), not PLATFORM composition (SMR-12) — PL-F2 is not reused here.
ORCHESTRATION_SUBSTRATE_REFS: tuple[str, ...] = (
    "ENG-001",  # Identity  (identified-by, SMR-10)
    "ENG-002",  # Object    (borne-as-object)
    "ENG-003",  # Value     (structural value fidelity)
    "ENG-004",  # Type      (typed orchestration, USL-03 / SOO-01)
    "ENG-005",  # Relationship/Reference (orchestrates/composes/bound-by refs; SMR-06/05/02)
    "RL-F2",  # Runtime workflow/orchestration/event (behaves-as, SMR-11; RUNTIME-009/013/008)
    "DF-2",  # Represented data (inter-step data flow, SMR-13; by reference)
)

#: The meta-relationships an Orchestration intrinsically participates in (SERVICE-011 §6;
#: all within SMR-01…13):
#:   SMR-02 bound-by      (Orchestration → Composition-Contract — founding, acyclic; SOR-02)
#:   SMR-05 composes      (Orchestration → coordinated set — reference-only, acyclic; SOR-05)
#:   SMR-06 orchestrates  (Orchestration → Operation/Service — reference-only; SOR-06)
#:   SMR-10 identified-by (ENG-001 via ENG-002; SOR-10)
#:   SMR-11 behaves-as    (Orchestration → RUNTIME workflow/orchestration RUNTIME-009/013; SOR-11)
#:   SMR-13 operates-on   (inter-step data flow → DATA DF-2, by reference; SOR-13)
ORCHESTRATION_RELATIONSHIPS: tuple[str, ...] = (
    "SMR-02",
    "SMR-05",
    "SMR-06",
    "SMR-10",
    "SMR-11",
    "SMR-13",
)


class OrchestrationKind(str, Enum):
    """SXH-07 Orchestration Hierarchy (SERVICE-004 / SERVICE-011 §5) — single-facet (SXC-02).

    Membership is decidable and single-facet; each kind carries a distinct coordination
    topology and reuses a distinct RUNTIME concern by reference (SOO-03 / SOO-C3):

    * ``SEQUENTIAL``    — ordered operations; the coordination graph induces one total order
                          (RUNTIME workflow, RUNTIME-009, by reference).
    * ``PARALLEL``      — concurrent operations toward one outcome; no inter-step founding
                          dependency (RUNTIME orchestration, RUNTIME-013, by reference).
    * ``CHOREOGRAPHED`` — event-driven coordination with no central driver; a partial,
                          acyclic order (RUNTIME event, RUNTIME-008, by reference).
    """

    SEQUENTIAL = "Sequential-Orchestration"  # ordered steps (RUNTIME workflow by reference)
    PARALLEL = "Parallel-Orchestration"  # concurrent steps toward one outcome
    CHOREOGRAPHED = "Choreographed-Coordination"  # event-driven coordination (no central driver)


#: The RUNTIME concern each orchestration kind reuses by reference (SERVICE-011 §7 / SOO-03).
#: The orchestration re-founds no runtime concern; it references RUNTIME-009 (workflow),
#: RUNTIME-013 (orchestration) or RUNTIME-008 (event) via RL-F2 (SMR-11 behaves-as).
KIND_RUNTIME_CONCERN: dict[OrchestrationKind, str] = {
    OrchestrationKind.SEQUENTIAL: "RUNTIME-009",  # workflow — ordered steps
    OrchestrationKind.PARALLEL: "RUNTIME-013",  # orchestration — multi-service coordination
    OrchestrationKind.CHOREOGRAPHED: "RUNTIME-008",  # event — event-driven coordination
}

#: The abstract RUNTIME behavior reference suffix per kind (the reused §7 binding).
KIND_BEHAVIOR_SUFFIX: dict[OrchestrationKind, str] = {
    OrchestrationKind.SEQUENTIAL: "workflow",
    OrchestrationKind.PARALLEL: "orchestration",
    OrchestrationKind.CHOREOGRAPHED: "event",
}

#: Orchestration principles SOO-01…10 (SERVICE-011 §4), each mapped to its short statement.
ORCHESTRATION_PRINCIPLES: dict[str, str] = {
    "SOO-01": "Orchestration Typedness — classified by an ENG-004 Type.",
    "SOO-02": "Orchestration Identity — an ENG-002 Object bearing an ENG-001 identity.",
    "SOO-03": "Runtime Reuse — reuses the RUNTIME workflow/orchestration concern by reference.",
    "SOO-04": "Coordinates Operations — coordinates operations/services via SOR-06; defines none.",
    "SOO-05": "Contracted Steps — each coordinated step is a contracted operation (SERVICE-007).",
    "SOO-06": "Well-Formed Coordination — the founding coordination graph is acyclic.",
    "SOO-07": "Data by Reference — inter-step data references DF-2 constructs by reference.",
    "SOO-08": "Additive Growth — new orchestration kinds append additively (SXH-07); no renumber.",
    "SOO-09": "Non-Constitutiveness — confers no authority, embeds no secret, selects no tech.",
    "SOO-10": "Reuse Labelling — consumed source assets are labelled INPUT, never COMPLETION.",
}

#: The Service laws an Orchestration construct is directly obligated by (per Stage-1 discovery).
#: USL-09 (composition by reference) + USL-10 (execution by reference) are THE governing laws;
#: USL-06 (contract explicitness of coordinated steps, SOO-05) and USL-11 (data by reference,
#: SOO-07) are grounded here too. USL-07 (interface typedness) is scoped to the Interface unit
#: (SMC-04) and USL-08 (operation boundedness) to the Operation unit (SMC-05); both recorded N/A.
ORCHESTRATION_APPLICABLE_LAWS: tuple[str, ...] = (
    "USL-01",
    "USL-02",
    "USL-03",
    "USL-04",
    "USL-05",
    "USL-06",
    "USL-09",
    "USL-10",
    "USL-11",
    "USL-12",
    "USL-13",
    "USL-14",
    "USL-15",
)

#: Laws scoped to other concern units, N/A to the Orchestration.
ORCHESTRATION_INAPPLICABLE_LAWS: tuple[str, ...] = ("USL-07", "USL-08")

#: Meta-constraints an Orchestration is bound by (SERVICE-005 §4 / SERVICE-011 §10 SOO-K1…K5).
#:   SMK-01 typed/identified/object · SMK-02 contract-bound · SMK-03 founding coordination graph
#:   acyclic · SMK-05 runtime reference resolves · SMK-07 data reference resolves · SMK-08 no
#:   technology / no authority.
ORCHESTRATION_META_CONSTRAINTS: dict[str, str] = {
    "SMK-01": "Typed (ENG-004), identified (ENG-001), objecthood-bound (ENG-002). [SOO-K1]",
    "SMK-02": "Bounded by a composition contract (SMR-02). [SOO-K2]",
    "SMK-03": "The founding coordination graph (orchestrates/composes) is acyclic. [SOO-K3]",
    "SMK-05": "Every runtime behavior reference resolves to an RL-F2 construct; none redefined.",
    "SMK-07": "Every data reference resolves to a DF-2 construct; none redefined. [SOO-K4]",
    "SMK-08": "No orchestration selects technology or confers authority. [SOO-K5]",
}

#: Meta-constraints scoped to other concern units, N/A to the Orchestration.
#:   SMK-04 (exposed-through-interface) is scoped to the Operation unit (SMC-05); SMK-06
#:   (platform composition reference) is scoped to Composition (SMC-06) — Orchestration binds
#:   RUNTIME by reference (SMR-11), not PLATFORM composition (SMR-12).
ORCHESTRATION_INAPPLICABLE_CONSTRAINTS: tuple[str, ...] = ("SMK-04", "SMK-06")

#: The five meta-validity checks (SERVICE-005 §8) — a construct is META-VALID iff all hold.
META_VALIDITY_CHECKS: dict[str, str] = {
    "V1": "Instantiates exactly one meta-class (Orchestration → SMC-07).",
    "V2": "All relationships used are within SMR-01…13.",
    "V3": "Satisfies all applicable meta-constraints (SMK-01/02/03/05/07/08).",
    "V4": "Founding coordination graph is acyclic (SMK-03 / SMI-04 / SOO-C1).",
    "V5": "Every construct has a valid lifecycle state (SOS-01…06).",
}

__all__ = [
    "ORCHESTRATION_META_CLASS",
    "TRACE_BACKWARD_ORCHESTRATION",
    "ORCHESTRATION_SUBSTRATE_REFS",
    "ORCHESTRATION_RELATIONSHIPS",
    "OrchestrationKind",
    "KIND_RUNTIME_CONCERN",
    "KIND_BEHAVIOR_SUFFIX",
    "ORCHESTRATION_PRINCIPLES",
    "ORCHESTRATION_APPLICABLE_LAWS",
    "ORCHESTRATION_INAPPLICABLE_LAWS",
    "ORCHESTRATION_META_CONSTRAINTS",
    "ORCHESTRATION_INAPPLICABLE_CONSTRAINTS",
    "META_VALIDITY_CHECKS",
    "LIFECYCLE_ORDER",
    "ServiceState",
]
