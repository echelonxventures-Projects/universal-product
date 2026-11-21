"""EC3-B11-U04 — Interface meta-model constants (read-only projections of SERVICE-001…008).

Carries, as executable constants, the fixed identifiers of the frozen Service Foundation
that the Universal **Interface** realization (SMC-04) must conform to. It **defines no new
law and redefines no foundation concept** (USL-02 / SMI-05 / USL-15); it only names the
frozen obligations so the realization can be checked deterministically.

Derived verbatim from the frozen ``11-SERVICE/`` specification at anchor ``b7e7657``:

* SMC-04 **Interface** models ontology entity **SOE-04** — *"the typed surface through
  which a service's operations are addressed — the shape by which capability is requested,
  distinct from the endpoint (an abstract addressable locus) that locates it and from the
  contract that specifies it"* (SERVICE-003 §2; SERVICE-008 §3) — classified by hierarchy
  **SXH-04** (Request-Response / Event / Stream; SERVICE-004 §3 / SERVICE-008 §5).
* An Interface is the **target of SMR-03 exposes** (Service → Interface, founding, acyclic),
  references its interaction behavior via **SMR-11 behaves-as** (RL-F2, by reference),
  references its carried I/O data via **SMR-13 operates-on** (DF-2, by reference), and is
  identified via **SMR-10 identified-by** (ENG-001 via ENG-002).
* Interface principles SIN-01…10 (SERVICE-008 §4) govern the construct.
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

#: The Interface meta-class id (SERVICE-005 §2).
INTERFACE_META_CLASS = "SMC-04"

#: Backward traceability chain every realized Interface records (SERVICE-005 → root).
TRACE_BACKWARD_INTERFACE: tuple[str, ...] = (
    "SMC-04",  # SERVICE-005 §2 — Interface meta-class
    "SOE-04",  # SERVICE-003 §2 — Interface ontology entity
    "SERVICE-008",  # Universal Service Interface Architecture (concern architecture)
    "SERVICE-005",  # Universal Service Meta-Model
    "SERVICE-001",  # Universal Service Constitution (USL-01…15)
    "ARCH-SERVICE-001",  # Governing Service architecture model
    f"11-SERVICE@{CONSTITUTIONAL_ANCHOR}",  # frozen specification set
)

#: The frozen foundations an Interface reuses by reference (USL-02).
#:   ENG-001…005 (EL-1) · RL-F2 (interaction behavior, SMR-11) · DF-2 (carried I/O, SMR-13).
#: An interface does not compose (PL-F2 N/A — composition is the SMC-06 concern).
INTERFACE_SUBSTRATE_REFS: tuple[str, ...] = (
    "ENG-001",  # Identity  (identified-by, SMR-10)
    "ENG-002",  # Object    (borne-as-object)
    "ENG-003",  # Value     (typed surface value fidelity)
    "ENG-004",  # Type      (typed surface, USL-07)
    "ENG-005",  # Relationship/Reference (exposes/behaves-as/operates-on refs)
    "RL-F2",  # Runtime behavior (interaction bound by reference; SMR-11)
    "DF-2",  # Represented data (interface-carried I/O references DATA, SMR-13; by reference)
)

#: The meta-relationships an Interface intrinsically participates in (SERVICE-008 §6;
#: all within SMR-01…13):
#:   SMR-03 exposes       (Service → Interface — Interface is the exposed target; founding)
#:   SMR-10 identified-by (ENG-001 via ENG-002)
#:   SMR-11 behaves-as    (Interface interaction → RUNTIME construct RL-F2, by reference)
#:   SMR-13 operates-on   (Interface-carried I/O → DATA DF-2, by reference)
INTERFACE_RELATIONSHIPS: tuple[str, ...] = ("SMR-03", "SMR-10", "SMR-11", "SMR-13")


class InterfaceKind(str, Enum):
    """SXH-04 Interface Hierarchy (SERVICE-004 §3 / SERVICE-008 §5) — single-facet (SXC-02)."""

    REQUEST_RESPONSE = "Request-Response-Interface"  # synchronous request/response surface
    EVENT = "Event-Interface"  # command/event surface (RUNTIME event by reference)
    STREAM = "Stream-Interface"  # continuous interaction surface


#: Interface principles SIN-01…10 (SERVICE-008 §4), each mapped to its short statement.
INTERFACE_PRINCIPLES: dict[str, str] = {
    "SIN-01": "Interface Typedness — a typed surface (ENG-004); operations are typed on it.",
    "SIN-02": "Interface Identity — an ENG-002 Object bearing an ENG-001 identity.",
    "SIN-03": "Sole-Surface — an operation is addressable only through a declared interface.",
    "SIN-04": "Contract Presentation — presents operations under their contracts (SERVICE-007).",
    "SIN-05": "Endpoint Abstraction — the endpoint is an abstract locus; no URL/protocol/port.",
    "SIN-06": "Interaction Style — declares request-response / event / stream as a concept.",
    "SIN-07": "Data by Reference — interface-carried I/O references DF-2 data; none redefined.",
    "SIN-08": "Versioned Supersession — a breaking change is a new versioned interface.",
    "SIN-09": "Non-Constitutiveness — confers no authority, embeds no secret, selects no tech.",
    "SIN-10": "Reuse Labelling — consumed source assets are labelled INPUT, never COMPLETION.",
}

#: The Service laws an Interface construct is directly obligated by (per Stage-1 discovery).
#: USL-07 (interface typedness) is THE governing law here. USL-06/08/09/10 (contract /
#: operation-I/O / composition / execution) are scoped to the Contract/Operation/
#: Composition/Execution units (SMC-03/05/06/08); recorded N/A.
INTERFACE_APPLICABLE_LAWS: tuple[str, ...] = (
    "USL-01",
    "USL-02",
    "USL-03",
    "USL-04",
    "USL-05",
    "USL-07",
    "USL-11",
    "USL-12",
    "USL-13",
    "USL-14",
    "USL-15",
)

#: Laws scoped to other concern units, N/A to the Interface.
INTERFACE_INAPPLICABLE_LAWS: tuple[str, ...] = ("USL-06", "USL-08", "USL-09", "USL-10")

#: Meta-constraints an Interface is bound by (SERVICE-005 §4 / SERVICE-008 §10 SIN-K1…K5).
#:   SMK-01 typed/identified/object · SMK-03 founding (exposes) acyclic · SMK-05 behavior/
#:   data references resolve, none redefined.
INTERFACE_META_CONSTRAINTS: dict[str, str] = {
    "SMK-01": "Typed (ENG-004), identified (ENG-001), objecthood-bound (ENG-002).",
    "SMK-03": "The founding meta-relationship graph (exposes) is acyclic (a DAG).",
    "SMK-05": "Every behavior/data reference resolves to an RL-F2/DF-2 construct; none redefined.",
}

#: Meta-constraints scoped to other units, N/A to the Interface.
INTERFACE_INAPPLICABLE_CONSTRAINTS: tuple[str, ...] = ("SMK-02", "SMK-04", "SMK-06", "SMK-07")

#: The five meta-validity checks (SERVICE-005 §8) — a construct is META-VALID iff all hold.
META_VALIDITY_CHECKS: dict[str, str] = {
    "V1": "Instantiates exactly one meta-class (Interface → SMC-04).",
    "V2": "All relationships used are within SMR-01…13.",
    "V3": "Satisfies all applicable meta-constraints (SMK-01/03/05).",
    "V4": "Founding graph is acyclic (SMK-03 / SMI-04).",
    "V5": "Every construct has a valid lifecycle state (SOS-01…06).",
}

__all__ = [
    "INTERFACE_META_CLASS",
    "TRACE_BACKWARD_INTERFACE",
    "INTERFACE_SUBSTRATE_REFS",
    "INTERFACE_RELATIONSHIPS",
    "InterfaceKind",
    "INTERFACE_PRINCIPLES",
    "INTERFACE_APPLICABLE_LAWS",
    "INTERFACE_INAPPLICABLE_LAWS",
    "INTERFACE_META_CONSTRAINTS",
    "INTERFACE_INAPPLICABLE_CONSTRAINTS",
    "META_VALIDITY_CHECKS",
    "LIFECYCLE_ORDER",
    "ServiceState",
]
