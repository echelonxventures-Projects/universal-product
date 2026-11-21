"""EC3-B11-U01 — Service meta-model constants (read-only projections of SERVICE-001/003/004/005).

This module carries, as executable constants, the fixed identifiers of the frozen
Service Foundation (SERVICE-001 Constitution, SERVICE-003 Ontology, SERVICE-004
Taxonomy, SERVICE-005 Meta-Model) that the Universal Service realization must conform
to. It **defines no new law and redefines no foundation concept** (USL-02 / SMI-05 /
USL-15); it only names the frozen obligations so the realization can be checked
against them deterministically.

Everything here is derived verbatim from the frozen ``11-SERVICE/`` specification at
the constitutional anchor ``b7e7657`` — no obligation is invented, none is dropped.
"""

from __future__ import annotations

from enum import Enum

# ---------------------------------------------------------------------------
# Traceability anchors (No-Orphan spine — EC-3-AP-3 §5/§9)
# ---------------------------------------------------------------------------

#: Constitutional anchor: the frozen 11-SERVICE/ specification commit.
CONSTITUTIONAL_ANCHOR = "b7e7657"

#: Implementation substrate anchor: the certified baseline this builds upon
#: (EC-1 ``engine/**`` CERTIFIED + EC-2 ``platform/**`` FROZEN + Band-10 ``data/**``
#: CERTIFIED-COMPLETE at HEAD ``0595a91``).
IMPLEMENTATION_ANCHOR = "0595a91"

#: The backward traceability chain every realized Service records (SERVICE-005 → root).
TRACE_BACKWARD: tuple[str, ...] = (
    "SMC-01",  # SERVICE-005 §2 — Service meta-class (root)
    "SERVICE-005",  # Universal Service Meta-Model
    "SERVICE-001",  # Universal Service Constitution (USL-01…15)
    "ARCH-SERVICE-001",  # Governing Service architecture model
    f"11-SERVICE@{CONSTITUTIONAL_ANCHOR}",  # frozen specification set
)

#: The frozen foundations the Service reuses by reference (USL-02).
#:   ENG-001…005 (EL-1) · RL-F2 (behavior) · PL-F2 (composition) · DF-2 (data).
SUBSTRATE_REFS: tuple[str, ...] = (
    "ENG-001",  # Identity  (identified-by, SMR-10)
    "ENG-002",  # Object    (borne-as-object)
    "ENG-003",  # Value     (value fidelity)
    "ENG-004",  # Type      (typed, USL-03)
    "ENG-005",  # Relationship/Reference (composition/reference, SMR-05/10)
    "RL-F2",  # Runtime behavior (behaves-as / executes, SMR-11/07)
    "PL-F2",  # Platform composition (composed-as, SMR-12; PLATFORM-008)
    "DF-2",  # Represented data (operates-on, SMR-13; scoped to the Operation unit)
)

# ---------------------------------------------------------------------------
# SERVICE-005 — Meta-model closure sets
# ---------------------------------------------------------------------------

#: The ten admitted meta-classes (SMI-01 closure). Service is SMC-01.
META_CLASSES: tuple[str, ...] = tuple(f"SMC-{n:02d}" for n in range(1, 11))

#: The Service meta-class id (SERVICE-005 §2).
SERVICE_META_CLASS = "SMC-01"

#: The thirteen admitted meta-relationships (SMI-02 closure).
META_RELATIONSHIPS: tuple[str, ...] = tuple(f"SMR-{n:02d}" for n in range(1, 14))

#: The meta-relationships a standalone Service root intrinsically participates in
#: (SERVICE-003 §3; all reference-only, requiring no realized peer at U01):
#:   SMR-01 realizes      (Service → Capability, by reference)
#:   SMR-10 identified-by (ENG-001 via ENG-002)
#:   SMR-11 behaves-as    (RUNTIME construct, by reference)
#:   SMR-12 composed-as   (PLATFORM composition, by reference; PLATFORM-008)
SERVICE_RELATIONSHIPS: tuple[str, ...] = ("SMR-01", "SMR-10", "SMR-11", "SMR-12")


class ServiceKind(str, Enum):
    """SXH-01 Service Hierarchy (SERVICE-004 §3) — the classification of a Service.

    A Service is classified by exactly one kind (single-facet, SXC-02):
    """

    ATOMIC = "Atomic-Service"  # provides a single cohesive capability
    COMPOSITE = "Composite-Service"  # composed from other services/operations (SOR-05)
    ORCHESTRATED = "Orchestrated-Service"  # coordinates operations via orchestration (SOR-06)


class ServiceState(str, Enum):
    """SOS-01…06 (SERVICE-003 §4) — the forward-only service lifecycle states (USL-12)."""

    DEFINED = "DEFINED"  # SOS-01 — declared but not yet contracted
    CONTRACTED = "CONTRACTED"  # SOS-02 — an explicit typed contract is fixed
    EXECUTABLE = "EXECUTABLE"  # SOS-03 — exposed, composed, available (authoritative)
    DEPRECATED = "DEPRECATED"  # SOS-04 — superseded-in-waiting
    SUPERSEDED = "SUPERSEDED"  # SOS-05 — replaced by a new identity (lineage recorded)
    RETIRED = "RETIRED"  # SOS-06 — removed from active use, retained for history


#: The forward-only lifecycle order (USL-12 / SOI-05: no in-place reversal).
LIFECYCLE_ORDER: tuple[ServiceState, ...] = (
    ServiceState.DEFINED,
    ServiceState.CONTRACTED,
    ServiceState.EXECUTABLE,
    ServiceState.DEPRECATED,
    ServiceState.SUPERSEDED,
    ServiceState.RETIRED,
)

# ---------------------------------------------------------------------------
# SERVICE-001 §7 — Service Laws (USL-01…15) and §12 — Compliance (C1…C7)
# ---------------------------------------------------------------------------

#: The fifteen Service Laws (SERVICE-001 §7), each mapped to its short obligation.
SERVICE_LAWS: dict[str, str] = {
    "USL-01": "Service is an operation layer founded on the frozen EL-1/RL-F2/PL-F2/DF-2.",
    "USL-02": "Every construct reuses ENG-001…005/runtime/platform/data by reference; redefines 0.",
    "USL-03": "Every service construct is classified by an ENG-004 Type; none is untyped.",
    "USL-04": "A construct-as-thing bears an ENG-001 Identity via an ENG-002 Object; one scheme.",
    "USL-05": "Every service construct-as-thing IS an ENG-002 Object; no parallel thing-model.",
    "USL-06": "Every operation/service is specified by an explicit, typed contract.",
    "USL-07": "Every interface is a typed surface; operations are addressed only through it.",
    "USL-08": "Every operation declares typed I/O, defined effects, and declared faults.",
    "USL-09": "Composition/orchestration reuse PL-F2/ENG-005 references; founding is acyclic.",
    "USL-10": "Service execution/transaction/state binds to frozen RL-F2 by reference.",
    "USL-11": "Every operation's I/O is DF-2-represented data referenced by contract.",
    "USL-12": "Every service/operation has a decidable, forward-only, recorded lifecycle.",
    "USL-13": "Service policy is declarative, evaluative, non-enforcing; confers no authority.",
    "USL-14": "Service security is a decidable evaluative facet; enacts no enforcement.",
    "USL-15": "Non-constitutive: no new primitive, no authority, no secret, no technology.",
}

#: The Service laws the bare Service root construct is directly obligated by.
#: USL-06/07/08/11 (contract/interface/operation/operation-I/O) apply to the
#: Contract/Interface/Operation units (SMC-03/04/05); they are recorded as
#: not-applicable-to-the-Service-root with rationale.
SERVICE_APPLICABLE_LAWS: tuple[str, ...] = (
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

#: Laws scoped to Contract/Interface/Operation concerns (U03/U04/U05), N/A to the root.
SERVICE_INAPPLICABLE_LAWS: tuple[str, ...] = ("USL-06", "USL-07", "USL-08", "USL-11")

#: The seven Service compliance conditions (SERVICE-001 §12). A construct is COMPLIANT
#: iff all applicable conditions hold, decided on evidence and deterministically.
SERVICE_COMPLIANCE: dict[str, str] = {
    "C1": "Typed (USL-03), identified and objecthood-bound (USL-04/05).",
    "C2": "Reuses frozen foundations by reference without redefinition (USL-02).",
    "C3": "Carries ENG-003 value; operation I/O is DF-2 data by reference (USL-08/11).",
    "C4": "Contract/interface/operation structure is explicit (USL-06/07/08).",
    "C5": "Composition/orchestration uses ENG-005 references; founding acyclic (USL-09).",
    "C6": "Execution binds to RL-F2 by reference (USL-10).",
    "C7": "Selects no technology, confers no authority, embeds no secret (USL-15).",
}

# ---------------------------------------------------------------------------
# SERVICE-005 §8 — Meta-validity gate (V1…V5) and constraints (SMK-01…08)
# ---------------------------------------------------------------------------

#: The five meta-validity checks (SERVICE-005 §8) — a construct is META-VALID iff all hold.
META_VALIDITY_CHECKS: dict[str, str] = {
    "V1": "Instantiates exactly one meta-class (Service → SMC-01).",
    "V2": "All relationships used are within SMR-01…13.",
    "V3": "Satisfies all applicable meta-constraints (SMK-01…08).",
    "V4": "Founding graph is acyclic (SMK-03 / SMI-04).",
    "V5": "Every construct has a valid lifecycle state (SOS-01…06).",
}

#: Meta-constraints a Service root is bound by (SERVICE-005 §4). SMK-02/04/07
#: (operation bound-by-contract / exposed-through-interface / operation I/O) are
#: scoped to the Operation unit (SMC-05) and are recorded not-applicable-to-root.
SERVICE_META_CONSTRAINTS: dict[str, str] = {
    "SMK-01": "Typed (ENG-004), identified (ENG-001), objecthood-bound (ENG-002).",
    "SMK-03": "The founding meta-relationship graph is acyclic (a DAG).",
    "SMK-05": "Every behavior/execution reference resolves to an RL-F2 construct; none redefined.",
    "SMK-06": "Every composition reference resolves to a PL-F2 construct; none redefined.",
    "SMK-08": "No modelled construct selects technology or confers authority.",
}

#: Meta-constraints scoped to the Operation unit (SMC-05), N/A to the Service root.
SERVICE_INAPPLICABLE_CONSTRAINTS: tuple[str, ...] = ("SMK-02", "SMK-04", "SMK-07")

#: The CCE ten-gate identifiers (EC-3 AP-3 certification strategy, CC-1…CC-10).
CCE_GATES: tuple[str, ...] = tuple(f"CC-{n}" for n in range(1, 11))

__all__ = [
    "CONSTITUTIONAL_ANCHOR",
    "IMPLEMENTATION_ANCHOR",
    "TRACE_BACKWARD",
    "SUBSTRATE_REFS",
    "META_CLASSES",
    "SERVICE_META_CLASS",
    "META_RELATIONSHIPS",
    "SERVICE_RELATIONSHIPS",
    "ServiceKind",
    "ServiceState",
    "LIFECYCLE_ORDER",
    "SERVICE_LAWS",
    "SERVICE_APPLICABLE_LAWS",
    "SERVICE_INAPPLICABLE_LAWS",
    "SERVICE_COMPLIANCE",
    "META_VALIDITY_CHECKS",
    "SERVICE_META_CONSTRAINTS",
    "SERVICE_INAPPLICABLE_CONSTRAINTS",
    "CCE_GATES",
]
