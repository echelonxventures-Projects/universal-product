"""EC3-B11-U02 — Capability meta-model constants (read-only projections of SERVICE-001/003/004/005).

This module carries, as executable constants, the fixed identifiers of the frozen
Service Foundation that the Universal **Capability** realization (SMC-02) must conform
to. It **defines no new law and redefines no foundation concept** (USL-02 / SMI-05 /
USL-15); it only names the frozen obligations so the realization can be checked against
them deterministically.

Everything here is derived verbatim from the frozen ``11-SERVICE/`` specification at the
constitutional anchor ``b7e7657``:

* SMC-02 **Capability** models ontology entity **SOE-02** — *"the implementation-independent
  ability to perform work a service realizes (reuses PLATFORM-006 by reference)"* (SERVICE-003 §2)
  — classified by hierarchy **SXH-02** (Functional / Query / Command; SERVICE-004 §3).
* A Capability is the **target of SMR-01 realizes** (Service → Capability, reference-only),
  binds a RUNTIME behavior by reference (**SMR-11 behaves-as**; "ability to perform work"),
  and reuses the PLATFORM capability construct **PLATFORM-006** by reference
  (**SMR-12 composed-as**). Identity is via **SMR-10 identified-by** (ENG-001 via ENG-002).
"""

from __future__ import annotations

from enum import Enum

from service.service_meta import (
    CONSTITUTIONAL_ANCHOR,
    IMPLEMENTATION_ANCHOR,
    LIFECYCLE_ORDER,
    META_CLASSES,
    META_RELATIONSHIPS,
    SERVICE_COMPLIANCE,
    SERVICE_LAWS,
    ServiceState,
)

# Re-export the frozen anchors/closure sets (single source of truth — no duplication).
__all_reexport__ = (
    CONSTITUTIONAL_ANCHOR,
    IMPLEMENTATION_ANCHOR,
    LIFECYCLE_ORDER,
    META_CLASSES,
    META_RELATIONSHIPS,
    SERVICE_COMPLIANCE,
    SERVICE_LAWS,
    ServiceState,
)

#: The Capability meta-class id (SERVICE-005 §2).
CAPABILITY_META_CLASS = "SMC-02"

#: The backward traceability chain every realized Capability records (SERVICE-005 → root).
TRACE_BACKWARD_CAPABILITY: tuple[str, ...] = (
    "SMC-02",  # SERVICE-005 §2 — Capability meta-class
    "SOE-02",  # SERVICE-003 §2 — Capability ontology entity
    "SERVICE-005",  # Universal Service Meta-Model
    "SERVICE-001",  # Universal Service Constitution (USL-01…15)
    "ARCH-SERVICE-001",  # Governing Service architecture model
    f"11-SERVICE@{CONSTITUTIONAL_ANCHOR}",  # frozen specification set
)

#: The frozen foundations a Capability reuses by reference (USL-02).
#:   ENG-001…005 (EL-1) · RL-F2 (behavior) · PL-F2/PLATFORM-006 (capability composition).
#: DF-2 is scoped to the Operation unit (SMC-05); a Capability does not operate on data.
CAPABILITY_SUBSTRATE_REFS: tuple[str, ...] = (
    "ENG-001",  # Identity  (identified-by, SMR-10)
    "ENG-002",  # Object    (borne-as-object)
    "ENG-003",  # Value     (value fidelity)
    "ENG-004",  # Type      (typed, USL-03)
    "ENG-005",  # Relationship/Reference (realized-by/composed-as, SMR-01/12)
    "RL-F2",  # Runtime behavior (behaves-as, SMR-11) — the ability to perform work, by reference
    "PL-F2",  # Platform composition (PLATFORM-006 capability construct, SMR-12; by reference)
)

#: The meta-relationships a standalone Capability intrinsically participates in
#: (SERVICE-003 §3; all reference-only, requiring no realized peer at this unit):
#:   SMR-01 realizes      (Service → Capability — Capability is the realized target)
#:   SMR-10 identified-by (ENG-001 via ENG-002)
#:   SMR-11 behaves-as    (RUNTIME behavior, by reference — "ability to perform work")
#:   SMR-12 composed-as   (PLATFORM-006 capability construct, by reference)
CAPABILITY_RELATIONSHIPS: tuple[str, ...] = ("SMR-01", "SMR-10", "SMR-11", "SMR-12")


class CapabilityKind(str, Enum):
    """SXH-02 Capability Hierarchy (SERVICE-004 §3) — the classification of a Capability.

    A Capability is classified by exactly one kind (single-facet, SXC-02):
    """

    FUNCTIONAL = "Functional-Capability"  # performs domain work
    QUERY = "Query-Capability"  # retrieves/derives represented data (read-side)
    COMMAND = "Command-Capability"  # intends a represented state change (write-side)


#: The Service laws a bare Capability construct is directly obligated by.
#: USL-06/07/08/11 (contract/interface/operation/operation-I/O) apply to the
#: Contract/Interface/Operation units (SMC-03/04/05); they are recorded as
#: not-applicable-to-the-Capability with rationale.
CAPABILITY_APPLICABLE_LAWS: tuple[str, ...] = (
    "USL-01",
    "USL-02",
    "USL-03",
    "USL-04",
    "USL-05",
    "USL-09",
    "USL-10",
    "USL-12",
    "USL-13",
    "USL-14",
    "USL-15",
)

#: Laws scoped to Contract/Interface/Operation concerns, N/A to the Capability.
CAPABILITY_INAPPLICABLE_LAWS: tuple[str, ...] = ("USL-06", "USL-07", "USL-08", "USL-11")

#: Meta-constraints a Capability is bound by (SERVICE-005 §4). SMK-02/04/07
#: (operation bound-by-contract / exposed-through-interface / operation I/O) are scoped
#: to the Operation unit (SMC-05) and are recorded not-applicable-to-the-Capability.
CAPABILITY_META_CONSTRAINTS: dict[str, str] = {
    "SMK-01": "Typed (ENG-004), identified (ENG-001), objecthood-bound (ENG-002).",
    "SMK-03": "The founding meta-relationship graph is acyclic (a DAG).",
    "SMK-05": "Every behavior reference (SMR-11) resolves to an RL-F2 construct; none redefined.",
    "SMK-06": "Every composition reference (SMR-12) resolves to a PL-F2 construct; none redefined.",
    "SMK-08": "No modelled construct selects technology or confers authority.",
}

#: Meta-constraints scoped to the Operation unit (SMC-05), N/A to the Capability.
CAPABILITY_INAPPLICABLE_CONSTRAINTS: tuple[str, ...] = ("SMK-02", "SMK-04", "SMK-07")

#: The five meta-validity checks (SERVICE-005 §8) — a construct is META-VALID iff all hold.
META_VALIDITY_CHECKS: dict[str, str] = {
    "V1": "Instantiates exactly one meta-class (Capability → SMC-02).",
    "V2": "All relationships used are within SMR-01…13.",
    "V3": "Satisfies all applicable meta-constraints (SMK-01…08).",
    "V4": "Founding graph is acyclic (SMK-03 / SMI-04).",
    "V5": "Every construct has a valid lifecycle state (SOS-01…06).",
}

__all__ = [
    "CAPABILITY_META_CLASS",
    "TRACE_BACKWARD_CAPABILITY",
    "CAPABILITY_SUBSTRATE_REFS",
    "CAPABILITY_RELATIONSHIPS",
    "CapabilityKind",
    "CAPABILITY_APPLICABLE_LAWS",
    "CAPABILITY_INAPPLICABLE_LAWS",
    "CAPABILITY_META_CONSTRAINTS",
    "CAPABILITY_INAPPLICABLE_CONSTRAINTS",
    "META_VALIDITY_CHECKS",
    "LIFECYCLE_ORDER",
    "ServiceState",
]
