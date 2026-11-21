"""EC3-B11-U08 — Execution meta-model constants (read-only projections of SERVICE-001…012).

Carries, as executable constants, the fixed identifiers of the frozen Service Foundation
that the Universal **Execution** realization (SMC-08) must conform to. It **defines no new
law and redefines no foundation concept** (USL-02 / SMI-05 / USL-15); it only names the
frozen obligations so the realization can be checked deterministically.

Derived verbatim from the frozen ``11-SERVICE/`` specification at anchor ``b7e7657``:

* SMC-08 **Execution** models ontology entity **SOE-08** — *"the carrying-out of an invoked
  operation — the act by which a contracted operation is performed, distinct from the
  operation's definition and the orchestration that sequences it"* (SERVICE-003 §2;
  SERVICE-012 §3) — classified by hierarchy **SXH-08** (Synchronous / Asynchronous /
  Transactional; SERVICE-004 / SERVICE-012 §5).
* An Execution is **executed** by exactly the operation that references it (SMR-07 executes;
  SOR-07; reference-only; SEX-04), **behaves-as** the RUNTIME execution/state/workflow concern
  (SMR-11 behaves-as; SOR-11; RUNTIME-006/007/009, by reference; §7 / SEX-03), carries the
  DF-2-represented data it reads/writes via **operates-on** (SMR-13; SOR-13; by reference;
  SEX-07), is **governed-by** a declarative policy (SMR-08; SOR-08; reference-only; §11), and
  is identified via **identified-by** (SMR-10; SOR-10; ENG-001 via ENG-002).
* Execution principles SEX-01…10 (SERVICE-012 §4) govern the construct; **USL-10** (execution
  by reference) is THE governing law, grounded in USL-06 (contract fulfilment) and USL-11
  (data by reference).
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

#: The Execution meta-class id (SERVICE-005 §2).
EXECUTION_META_CLASS = "SMC-08"

#: Backward traceability chain every realized Execution records (SERVICE-005 → root).
TRACE_BACKWARD_EXECUTION: tuple[str, ...] = (
    "SMC-08",  # SERVICE-005 §2 — Execution meta-class
    "SOE-08",  # SERVICE-003 §2 — Execution ontology entity
    "SERVICE-012",  # Universal Service Execution Architecture (concern architecture)
    "SERVICE-005",  # Universal Service Meta-Model
    "SERVICE-001",  # Universal Service Constitution (USL-01…15)
    "ARCH-SERVICE-001",  # Governing Service architecture model
    f"11-SERVICE@{CONSTITUTIONAL_ANCHOR}",  # frozen specification set
)

#: The frozen foundations an Execution reuses by reference (USL-02).
#:   ENG-001…005 (EL-1) · RL-F2 (execution/state/workflow behavior, SMR-11; RUNTIME-006/007/
#:   009/008) · DF-2 (read/written data, SMR-13). An execution does not compose (PL-F2 N/A —
#:   composition is the SMC-06 concern) nor coordinate (that is the SMC-07 concern).
EXECUTION_SUBSTRATE_REFS: tuple[str, ...] = (
    "ENG-001",  # Identity  (identified-by, SMR-10)
    "ENG-002",  # Object    (borne-as-object)
    "ENG-003",  # Value     (structural value fidelity)
    "ENG-004",  # Type      (typed execution, USL-03 / SEX-01)
    "ENG-005",  # Relationship/Reference (executed/behaves-as/operates-on/governed-by refs)
    "RL-F2",  # Runtime execution/state/workflow (behaves-as, SMR-11; RUNTIME-006/007/009/008)
    "DF-2",  # Represented data (read/written data, SMR-13; by reference)
)

#: The meta-relationships an Execution intrinsically participates in (SERVICE-012 §6;
#: all within SMR-01…13):
#:   SMR-07 executes      (Operation → Execution — reference-only; SOR-07; SEX-04)
#:   SMR-08 governed-by   (Execution → Policy — declarative, reference-only; SOR-08; §11)
#:   SMR-10 identified-by (ENG-001 via ENG-002; SOR-10)
#:   SMR-11 behaves-as    (Execution → RUNTIME execution/state/workflow RUNTIME-006/007/009; SOR-11)
#:   SMR-13 operates-on   (read/written data → DATA DF-2, by reference; SOR-13)
EXECUTION_RELATIONSHIPS: tuple[str, ...] = (
    "SMR-07",
    "SMR-08",
    "SMR-10",
    "SMR-11",
    "SMR-13",
)


class ExecutionKind(str, Enum):
    """SXH-08 Execution Hierarchy (SERVICE-004 / SERVICE-012 §5) — single-facet (SXC-02).

    Membership is decidable and single-facet; each kind reuses a distinct RUNTIME concern by
    reference (SEX-03 / §7):

    * ``SYNCHRONOUS``   — the invoker awaits completion; the carrying-out is the RUNTIME
                          execution concern (RUNTIME-006, by reference; §7 execution-run).
    * ``ASYNCHRONOUS``  — completion is decoupled from invocation and signalled via a RUNTIME
                          event (RUNTIME-008, by reference; §7 execution-emit; SEX-C4).
    * ``TRANSACTIONAL`` — an atomic multi-step execution; atomicity/consistency are RUNTIME
                          workflow properties (RUNTIME-009, by reference; §7 execution-transact;
                          SEX-06 / SEX-C1).
    """

    SYNCHRONOUS = "Synchronous-Execution"  # invoker awaits completion (RUNTIME execution)
    ASYNCHRONOUS = "Asynchronous-Execution"  # completion decoupled (RUNTIME event by reference)
    TRANSACTIONAL = "Transactional-Execution"  # atomic multi-step (RUNTIME workflow by reference)


#: The RUNTIME concern each execution kind reuses by reference (SERVICE-012 §7 / SEX-03).
#: The execution re-founds no runtime concern; it references RUNTIME-006 (execution),
#: RUNTIME-008 (event) or RUNTIME-009 (workflow) via RL-F2 (SMR-11 behaves-as).
KIND_RUNTIME_CONCERN: dict[ExecutionKind, str] = {
    ExecutionKind.SYNCHRONOUS: "RUNTIME-006",  # execution — carry out an operation, awaited
    ExecutionKind.ASYNCHRONOUS: "RUNTIME-008",  # event — completion signalled asynchronously
    ExecutionKind.TRANSACTIONAL: "RUNTIME-009",  # workflow — atomic multi-step execution
}

#: The abstract RUNTIME behavior binding suffix per kind (§7 execution-run/emit/transact).
KIND_BEHAVIOR_SUFFIX: dict[ExecutionKind, str] = {
    ExecutionKind.SYNCHRONOUS: "run",  # §7 execution-run (RUNTIME-006)
    ExecutionKind.ASYNCHRONOUS: "emit",  # §7 execution-emit (RUNTIME-008)
    ExecutionKind.TRANSACTIONAL: "transact",  # §7 execution-transact (RUNTIME-009)
}

#: The RUNTIME state concern an execution reuses by reference for state transitions
#: (SERVICE-012 §7 execution-state / SEX-C2). Referenced, never redefined.
RUNTIME_STATE_CONCERN = "RUNTIME-007"

#: Execution principles SEX-01…10 (SERVICE-012 §4), each mapped to its short statement.
EXECUTION_PRINCIPLES: dict[str, str] = {
    "SEX-01": "Execution Typedness — classified by an ENG-004 Type.",
    "SEX-02": "Execution Identity — an ENG-002 Object bearing an ENG-001 identity.",
    "SEX-03": "Runtime Reuse — reuses the RUNTIME execution/state/workflow concern by reference.",
    "SEX-04": "Operation-Bound — carries out exactly the operation that references it (SOR-07).",
    "SEX-05": "Contract Fulfilment — fulfils its operation's contract; effects/faults only as "
    "contracted.",
    "SEX-06": "Transactionality by Reference — atomicity is a RUNTIME workflow property by "
    "reference.",
    "SEX-07": "Data by Reference — reads/writes DF-2-represented data by reference; redefines 0.",
    "SEX-08": "Lifecycle Recording — emits an `executed` event (SOV-07); transitions recorded.",
    "SEX-09": "Non-Constitutiveness — confers no authority, embeds no secret, selects no tech.",
    "SEX-10": "Reuse Labelling — consumed source assets are labelled INPUT, never COMPLETION.",
}

#: The Service laws an Execution construct is directly obligated by (per Stage-1 discovery).
#: USL-10 (execution by reference) is THE governing law; USL-06 (contract fulfilment, SEX-05)
#: and USL-11 (data by reference, SEX-07) are grounded here too. USL-07 (interface typedness)
#: is scoped to the Interface unit (SMC-04), USL-08 (operation boundedness) to the Operation
#: unit (SMC-05), and USL-09 (composition) to the Composition/Orchestration units (SMC-06/07);
#: all three recorded N/A.
EXECUTION_APPLICABLE_LAWS: tuple[str, ...] = (
    "USL-01",
    "USL-02",
    "USL-03",
    "USL-04",
    "USL-05",
    "USL-06",
    "USL-10",
    "USL-11",
    "USL-12",
    "USL-13",
    "USL-14",
    "USL-15",
)

#: Laws scoped to other concern units, N/A to the Execution.
EXECUTION_INAPPLICABLE_LAWS: tuple[str, ...] = ("USL-07", "USL-08", "USL-09")

#: Meta-constraints an Execution is bound by (SERVICE-005 §4 / SERVICE-012 §10 SEX-K1…K5).
#:   SMK-01 typed/identified/object · SMK-02 fulfils a contracted operation · SMK-03 founding
#:   (executed/behaves-as) acyclic · SMK-05 runtime reference resolves · SMK-07 data reference
#:   resolves · SMK-08 no technology / no authority.
EXECUTION_META_CONSTRAINTS: dict[str, str] = {
    "SMK-01": "Typed (ENG-004), identified (ENG-001), objecthood-bound (ENG-002). [SEX-K1]",
    "SMK-02": "Fulfils a contracted operation (SMR-07 / SOR-07). [SEX-K2]",
    "SMK-03": "The founding graph (executed / behaves-as) is acyclic. [SMI-04]",
    "SMK-05": "Every execution/behavior reference resolves to an RL-F2 construct; none "
    "redefined. [SEX-K3]",
    "SMK-07": "Every data reference resolves to a DF-2 construct; none redefined. [SEX-K4]",
    "SMK-08": "No execution selects technology or confers authority. [SEX-K5]",
}

#: Meta-constraints scoped to other concern units, N/A to the Execution.
#:   SMK-04 (exposed-through-interface) is scoped to the Operation unit (SMC-05); SMK-06
#:   (platform composition reference) is scoped to Composition (SMC-06) — an Execution binds
#:   RUNTIME by reference (SMR-11), not PLATFORM composition (SMR-12).
EXECUTION_INAPPLICABLE_CONSTRAINTS: tuple[str, ...] = ("SMK-04", "SMK-06")

#: The five meta-validity checks (SERVICE-005 §8) — a construct is META-VALID iff all hold.
META_VALIDITY_CHECKS: dict[str, str] = {
    "V1": "Instantiates exactly one meta-class (Execution → SMC-08).",
    "V2": "All relationships used are within SMR-01…13.",
    "V3": "Satisfies all applicable meta-constraints (SMK-01/02/03/05/07/08).",
    "V4": "Founding graph is acyclic (SMK-03 / SMI-04).",
    "V5": "Every construct has a valid lifecycle state (SOS-01…06).",
}

__all__ = [
    "EXECUTION_META_CLASS",
    "TRACE_BACKWARD_EXECUTION",
    "EXECUTION_SUBSTRATE_REFS",
    "EXECUTION_RELATIONSHIPS",
    "ExecutionKind",
    "KIND_RUNTIME_CONCERN",
    "KIND_BEHAVIOR_SUFFIX",
    "RUNTIME_STATE_CONCERN",
    "EXECUTION_PRINCIPLES",
    "EXECUTION_APPLICABLE_LAWS",
    "EXECUTION_INAPPLICABLE_LAWS",
    "EXECUTION_META_CONSTRAINTS",
    "EXECUTION_INAPPLICABLE_CONSTRAINTS",
    "META_VALIDITY_CHECKS",
    "LIFECYCLE_ORDER",
    "ServiceState",
]
