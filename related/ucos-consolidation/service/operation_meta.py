"""EC3-B11-U05 — Operation meta-model constants (read-only projections of SERVICE-001…009).

Carries, as executable constants, the fixed identifiers of the frozen Service Foundation
that the Universal **Operation** realization (SMC-05) must conform to. It **defines no new
law and redefines no foundation concept** (USL-02 / SMI-05 / USL-15); it only names the
frozen obligations so the realization can be checked deterministically.

Derived verbatim from the frozen ``11-SERVICE/`` specification at anchor ``b7e7657``:

* SMC-05 **Operation** models ontology entity **SOE-05** — *"a single, named, invocable unit
  of work with typed inputs and outputs, defined effects, and declared faults — the atomic
  act a service offers"* (SERVICE-003 §2; SERVICE-009 §3) — classified by hierarchy
  **SXH-05** (Query / Command / Event; SERVICE-004 §3 / SERVICE-009 §5).
* An Operation is **provided-by a service** (SMR-04 provides; founding, acyclic), **bound-by
  a contract** (SMR-02 bound-by; founding, acyclic), **addressed-through an interface**
  (SMR-03; SOP-05 / SMK-04), **executes** by reference (SMR-07; RL-F2), references its
  behavior via **SMR-11 behaves-as** (RL-F2, by reference), **operates-on** DF-2 data via
  **SMR-13** (by reference), and is identified via **SMR-10 identified-by** (ENG-001 via
  ENG-002).
* Operation principles SOP-01…10 (SERVICE-009 §4) govern the construct; USL-08 (operation
  boundedness) is the governing law, grounded in USL-06/10/11.
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

#: The Operation meta-class id (SERVICE-005 §2).
OPERATION_META_CLASS = "SMC-05"

#: Backward traceability chain every realized Operation records (SERVICE-005 → root).
TRACE_BACKWARD_OPERATION: tuple[str, ...] = (
    "SMC-05",  # SERVICE-005 §2 — Operation meta-class
    "SOE-05",  # SERVICE-003 §2 — Operation ontology entity
    "SERVICE-009",  # Universal Service Operation Architecture (concern architecture)
    "SERVICE-005",  # Universal Service Meta-Model
    "SERVICE-001",  # Universal Service Constitution (USL-01…15)
    "ARCH-SERVICE-001",  # Governing Service architecture model
    f"11-SERVICE@{CONSTITUTIONAL_ANCHOR}",  # frozen specification set
)

#: The frozen foundations an Operation reuses by reference (USL-02).
#:   ENG-001…005 (EL-1) · RL-F2 (execution/behavior, SMR-07/11) · DF-2 (typed I/O, SMR-13).
#: An operation does not compose (PL-F2 N/A — composition is the SMC-06 concern).
OPERATION_SUBSTRATE_REFS: tuple[str, ...] = (
    "ENG-001",  # Identity  (identified-by, SMR-10)
    "ENG-002",  # Object    (borne-as-object)
    "ENG-003",  # Value     (typed-signature value fidelity)
    "ENG-004",  # Type      (typed operation, USL-08)
    "ENG-005",  # Relationship/Reference (provides/bound-by/exposes/executes refs)
    "RL-F2",  # Runtime behavior (execution/invocation bound by reference; SMR-07/11)
    "DF-2",  # Represented data (operation I/O references DATA, SMR-13; by reference)
)

#: The meta-relationships an Operation intrinsically participates in (SERVICE-009 §6;
#: all within SMR-01…13):
#:   SMR-02 bound-by      (Operation → Contract — founding, acyclic; SOP-04)
#:   SMR-03 addressed-through (Operation ↔ Interface — SOP-05 / SMK-04)
#:   SMR-04 provided-by   (Service → Operation — Operation is the provided target; founding)
#:   SMR-07 executes      (Operation → Execution — RL-F2, by reference; SOP-06)
#:   SMR-10 identified-by (ENG-001 via ENG-002)
#:   SMR-11 behaves-as    (Operation behavior → RUNTIME construct RL-F2, by reference)
#:   SMR-13 operates-on   (Operation I/O → DATA DF-2, by reference; SOP-07)
OPERATION_RELATIONSHIPS: tuple[str, ...] = (
    "SMR-02",
    "SMR-03",
    "SMR-04",
    "SMR-07",
    "SMR-10",
    "SMR-11",
    "SMR-13",
)


class OperationKind(str, Enum):
    """SXH-05 Operation Hierarchy (SERVICE-004 §3 / SERVICE-009 §5) — single-facet (SXC-02)."""

    QUERY = "Query-Operation"  # reads/derives; no represented state change
    COMMAND = "Command-Operation"  # intends a represented state change
    EVENT = "Event-Operation"  # emits/consumes an event (RUNTIME event by reference)


class EffectKind(str, Enum):
    """The decidable declared-effect vocabulary (SERVICE-009 §5/§8/§9 — effect honesty).

    An operation's effects are declared explicitly (SOP-03); a query declares no
    state-changing effect (SOP-08). Effects are declarative facts about the operation's
    signature, not runtime behavior (which binds RL-F2 by reference).
    """

    READ = "read"  # reads/derives represented state; no change (query-admissible)
    WRITE = "write"  # intends a represented state change (command)
    EMIT = "emit"  # emits an event (event-operation)
    CONSUME = "consume"  # consumes an event (event-operation)


#: Operation principles SOP-01…10 (SERVICE-009 §4), each mapped to its short statement.
OPERATION_PRINCIPLES: dict[str, str] = {
    "SOP-01": "Operation Typedness — classified by an ENG-004 Type; its signature is typed.",
    "SOP-02": "Operation Identity — an ENG-002 Object bearing an ENG-001 identity.",
    "SOP-03": "Signature Boundedness — declares typed I/O, defined effects, declared faults.",
    "SOP-04": "Contract Binding — bound by exactly one contract (SMR-02); none is uncontracted.",
    "SOP-05": "Interface Addressing — addressed only through an interface (SMR-03).",
    "SOP-06": "Execution by Reference — invocation/execution binds RL-F2 by reference (SMR-07).",
    "SOP-07": "Data by Reference — operation I/O references DF-2 data; none redefined (SMR-13).",
    "SOP-08": "Effect Honesty — kinds are declared; a query declares no state-changing effect.",
    "SOP-09": "Non-Constitutiveness — confers no authority, embeds no secret, selects no tech.",
    "SOP-10": "Reuse Labelling — consumed source assets are labelled INPUT, never COMPLETION.",
}

#: The Service laws an Operation construct is directly obligated by (per Stage-1 discovery).
#: USL-08 (operation boundedness) is THE governing law; USL-06 (contract explicitness),
#: USL-10 (execution by reference) and USL-11 (data by reference) are grounded here too.
#: USL-07 (interface typedness) is scoped to the Interface unit (SMC-04); USL-09
#: (composition) to the Composition unit (SMC-06); both recorded N/A.
OPERATION_APPLICABLE_LAWS: tuple[str, ...] = (
    "USL-01",
    "USL-02",
    "USL-03",
    "USL-04",
    "USL-05",
    "USL-06",
    "USL-08",
    "USL-10",
    "USL-11",
    "USL-12",
    "USL-13",
    "USL-14",
    "USL-15",
)

#: Laws scoped to other concern units, N/A to the Operation.
OPERATION_INAPPLICABLE_LAWS: tuple[str, ...] = ("USL-07", "USL-09")

#: Meta-constraints an Operation is bound by (SERVICE-005 §4 / SERVICE-009 §10 SOP-K1…K5).
#:   SMK-01 typed/identified/object · SMK-02 contract-bound + typed I/O · SMK-03 founding
#:   (provides/bound-by/exposes) acyclic · SMK-04 interface-addressed · SMK-05/07 behavior/
#:   execution/data references resolve, none redefined.
OPERATION_META_CONSTRAINTS: dict[str, str] = {
    "SMK-01": "Typed (ENG-004), identified (ENG-001), objecthood-bound (ENG-002).",
    "SMK-02": "Contract-bound (SMR-02) and declares typed I/O (DF-2), effects, faults.",
    "SMK-03": "The founding meta-relationship graph (provides/bound-by/exposes) is acyclic.",
    "SMK-04": "Interface-addressed before EXECUTABLE (SMR-03).",
    "SMK-05": "Every behavior/execution reference resolves to an RL-F2 construct; none redefined.",
    "SMK-07": "Every data reference resolves to a DF-2 construct; none redefined.",
}

#: Meta-constraints scoped to other units, N/A to the Operation.
OPERATION_INAPPLICABLE_CONSTRAINTS: tuple[str, ...] = ("SMK-06",)

#: The five meta-validity checks (SERVICE-005 §8) — a construct is META-VALID iff all hold.
META_VALIDITY_CHECKS: dict[str, str] = {
    "V1": "Instantiates exactly one meta-class (Operation → SMC-05).",
    "V2": "All relationships used are within SMR-01…13.",
    "V3": "Satisfies all applicable meta-constraints (SMK-01/02/03/04/05/07).",
    "V4": "Founding graph is acyclic (SMK-03 / SMI-04).",
    "V5": "Every construct has a valid lifecycle state (SOS-01…06).",
}

__all__ = [
    "OPERATION_META_CLASS",
    "TRACE_BACKWARD_OPERATION",
    "OPERATION_SUBSTRATE_REFS",
    "OPERATION_RELATIONSHIPS",
    "OperationKind",
    "EffectKind",
    "OPERATION_PRINCIPLES",
    "OPERATION_APPLICABLE_LAWS",
    "OPERATION_INAPPLICABLE_LAWS",
    "OPERATION_META_CONSTRAINTS",
    "OPERATION_INAPPLICABLE_CONSTRAINTS",
    "META_VALIDITY_CHECKS",
    "LIFECYCLE_ORDER",
    "ServiceState",
]
