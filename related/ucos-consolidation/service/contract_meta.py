"""EC3-B11-U03 — Contract meta-model constants (read-only projections of SERVICE-001…007).

Carries, as executable constants, the fixed identifiers of the frozen Service Foundation
that the Universal **Contract** realization (SMC-03) must conform to. It **defines no new
law and redefines no foundation concept** (USL-02 / SMI-05 / USL-15); it only names the
frozen obligations so the realization can be checked deterministically.

Derived verbatim from the frozen ``11-SERVICE/`` specification at anchor ``b7e7657``:

* SMC-03 **Contract** models ontology entity **SOE-03** — *"the binding, typed,
  implementation-independent specification of an operation or service — declaring typed
  inputs and outputs (DF-2 by reference), defined effects, declared faults,
  pre/post-conditions, and applicable policy"* (SERVICE-003 §2; SERVICE-007 §3) —
  classified by hierarchy **SXH-03** (Operation / Service / Composition; SERVICE-004 §3).
* A Contract is the **target of SMR-02 bound-by** (Operation/Service → Contract, founding,
  acyclic), references its I/O data via **SMR-13 operates-on** (DF-2), declares applicable
  policy via **SMR-08 governed-by** (SOE-09, evaluative/non-enforcing), and is identified
  via **SMR-10 identified-by** (ENG-001 via ENG-002).
* Contract principles SCN-01…10 (SERVICE-007 §4) govern the construct.
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

#: The Contract meta-class id (SERVICE-005 §2).
CONTRACT_META_CLASS = "SMC-03"

#: Backward traceability chain every realized Contract records (SERVICE-005 → root).
TRACE_BACKWARD_CONTRACT: tuple[str, ...] = (
    "SMC-03",  # SERVICE-005 §2 — Contract meta-class
    "SOE-03",  # SERVICE-003 §2 — Contract ontology entity
    "SERVICE-007",  # Universal Service Contract Architecture (concern architecture)
    "SERVICE-005",  # Universal Service Meta-Model
    "SERVICE-001",  # Universal Service Constitution (USL-01…15)
    "ARCH-SERVICE-001",  # Governing Service architecture model
    f"11-SERVICE@{CONSTITUTIONAL_ANCHOR}",  # frozen specification set
)

#: The frozen foundations a Contract reuses by reference (USL-02).
#:   ENG-001…005 (EL-1) · DF-2 (represented I/O data, SMR-13, by reference).
#: A contract binds no execution (USL-10 N/A — fulfilment is the Operation/Execution concern).
CONTRACT_SUBSTRATE_REFS: tuple[str, ...] = (
    "ENG-001",  # Identity  (identified-by, SMR-10)
    "ENG-002",  # Object    (borne-as-object)
    "ENG-003",  # Value     (typed I/O value fidelity)
    "ENG-004",  # Type      (typed, USL-03; typed I/O)
    "ENG-005",  # Relationship/Reference (bound-by/governed-by/operates-on refs)
    "DF-2",  # Represented data (contract I/O references DATA, SMR-13; by reference)
)

#: The meta-relationships a Contract intrinsically participates in (SERVICE-007 §6;
#: all within SMR-01…13):
#:   SMR-02 bound-by      (Operation/Service → Contract — Contract is the bound-to target)
#:   SMR-08 governed-by   (Contract → Policy SOE-09, by reference; evaluative/non-enforcing)
#:   SMR-10 identified-by (ENG-001 via ENG-002)
#:   SMR-13 operates-on   (Contract I/O → DATA DF-2, by reference)
CONTRACT_RELATIONSHIPS: tuple[str, ...] = ("SMR-02", "SMR-08", "SMR-10", "SMR-13")


class ContractKind(str, Enum):
    """SXH-03 Contract Hierarchy (SERVICE-004 §3 / SERVICE-007 §5) — single-facet (SXC-02)."""

    OPERATION = "Operation-Contract"  # specifies a single operation (I/O, effects, faults)
    SERVICE = "Service-Contract"  # specifies a service's exposed operation set
    COMPOSITION = "Composition-Contract"  # obligations across composed/orchestrated services


#: Contract principles SCN-01…10 (SERVICE-007 §4), each mapped to its short statement.
CONTRACT_PRINCIPLES: dict[str, str] = {
    "SCN-01": "Contract Typedness — classified by an ENG-004 Type; inputs/outputs typed.",
    "SCN-02": "Contract Identity — an ENG-002 Object bearing an ENG-001 identity.",
    "SCN-03": "Explicitness — an explicit contract specifies the operation/service; none implicit.",
    "SCN-04": "I/O by Data Reference — inputs/outputs reference DF-2 data; no data redefined.",
    "SCN-05": "Effect & Fault Declaration — declares effects and the faults it may raise.",
    "SCN-06": "Policy Binding — declares applicable policy (SOE-09) by reference; non-enforcing.",
    "SCN-07": "Operation Binding — binds exactly the operations it specifies (SOR-02).",
    "SCN-08": "Versioned Supersession — a breaking change is a new versioned contract.",
    "SCN-09": "Non-Constitutiveness — confers no authority, embeds no secret, selects no tech.",
    "SCN-10": "Reuse Labelling — consumed source assets are labelled INPUT, never COMPLETION.",
}

#: The Service laws a Contract construct is directly obligated by (per Stage-1 discovery).
#: USL-07/08/09/10 (interface/operation-I/O/composition/execution) are scoped to the
#: Interface/Operation/Composition/Execution units (SMC-04/05/06/08); recorded N/A.
CONTRACT_APPLICABLE_LAWS: tuple[str, ...] = (
    "USL-01",
    "USL-02",
    "USL-03",
    "USL-04",
    "USL-05",
    "USL-06",
    "USL-11",
    "USL-12",
    "USL-13",
    "USL-14",
    "USL-15",
)

#: Laws scoped to other concern units, N/A to the Contract.
CONTRACT_INAPPLICABLE_LAWS: tuple[str, ...] = ("USL-07", "USL-08", "USL-09", "USL-10")

#: Meta-constraints a Contract is bound by (SERVICE-005 §4).
#:   SMK-01 typed/identified/object · SMK-02 operation bound-by-contract + declares typed
#:   I/O, effects, faults (the contract is what provides this) · SMK-03 founding acyclic.
CONTRACT_META_CONSTRAINTS: dict[str, str] = {
    "SMK-01": "Typed (ENG-004), identified (ENG-001), objecthood-bound (ENG-002).",
    "SMK-02": "Declares typed I/O (ENG-003 value; DF-2 by reference), effects, and faults.",
    "SMK-03": "The founding meta-relationship graph (bound-by) is acyclic (a DAG).",
}

#: Meta-constraints scoped to other units, N/A to the Contract.
CONTRACT_INAPPLICABLE_CONSTRAINTS: tuple[str, ...] = ("SMK-04", "SMK-05", "SMK-06", "SMK-07")

#: The five meta-validity checks (SERVICE-005 §8) — a construct is META-VALID iff all hold.
META_VALIDITY_CHECKS: dict[str, str] = {
    "V1": "Instantiates exactly one meta-class (Contract → SMC-03).",
    "V2": "All relationships used are within SMR-01…13.",
    "V3": "Satisfies all applicable meta-constraints (SMK-01/02/03).",
    "V4": "Founding graph is acyclic (SMK-03 / SMI-04).",
    "V5": "Every construct has a valid lifecycle state (SOS-01…06).",
}

__all__ = [
    "CONTRACT_META_CLASS",
    "TRACE_BACKWARD_CONTRACT",
    "CONTRACT_SUBSTRATE_REFS",
    "CONTRACT_RELATIONSHIPS",
    "ContractKind",
    "CONTRACT_PRINCIPLES",
    "CONTRACT_APPLICABLE_LAWS",
    "CONTRACT_INAPPLICABLE_LAWS",
    "CONTRACT_META_CONSTRAINTS",
    "CONTRACT_INAPPLICABLE_CONSTRAINTS",
    "META_VALIDITY_CHECKS",
    "LIFECYCLE_ORDER",
    "ServiceState",
]
