"""EC3-B13-U03 — Infrastructure Network meta-model constants.

Read-only projections of INFRASTRUCTURE-001 (Constitution), INFRASTRUCTURE-003
(Ontology), INFRASTRUCTURE-005 (Meta-Model), and INFRASTRUCTURE-008 (Network concern
architecture).

This module carries, as executable constants, the fixed identifiers of the frozen
Infrastructure Foundation (IF-1 = INFRASTRUCTURE-001…005, frozen by INFRASTRUCTURE-015)
that the Universal Infrastructure Network realization must conform to. It **defines no
new law and redefines no foundation concept** (UIL-02 / UIL-15); it only names the
frozen obligations so the realization can be checked against them deterministically. The
shared Infrastructure vocabulary (lifecycle states, admitted relationships, the fifteen
Infrastructure Laws, the twelve well-formedness rules, the seven compliance conditions,
and the CCE gate ids) is **imported by reference** from the first Band-13 unit
(:mod:`infrastructure.capability_meta`) and never redefined.

Everything here is derived verbatim from the frozen ``13-INFRASTRUCTURE/`` specification
at the constitutional anchor ``b7e7657``:

* The **NetworkResource** leaf meta-class (INFRASTRUCTURE-005 §2/§7) — *the
  implementation-independent abstraction of connectivity between hosted constructs: the
  typed arrangement by which resources, nodes, clusters, and environments are reachable
  from one another* (INFRASTRUCTURE-008 §1).
* Its network constructs (INFRASTRUCTURE-008 §2): Network Resource / Connectivity Link /
  Network Boundary / Reachability Arrangement / Connectivity Class.
* Its concern rules ICNW-01…05 (INFRASTRUCTURE-008 §3) and the well-formedness / law /
  compliance obligations it is validated against (INFRASTRUCTURE-005 §5; INFRASTRUCTURE-001
  §7/§12).
"""

from __future__ import annotations

# --- Infrastructure vocabulary reused by reference from the first Band-13 unit ---
#     (UIL-02 — imported, never redefined).
from infrastructure.capability_meta import (
    ADMITTED_META_RELATIONSHIPS,
    CCE_GATES,
    CONSTITUTIONAL_ANCHOR,
    INFRASTRUCTURE_COMPLIANCE,
    INFRASTRUCTURE_LAWS,
    LEAF_META_CLASSES,
    LIFECYCLE_ORDER,
    WELL_FORMEDNESS_RULES,
    InfrastructureState,
)

#: The realization unit this module belongs to (EC-3 Band 13, Unit 03). Declared here —
#: never in ``infrastructure/__init__.py`` (whose ``REALIZATION_UNIT`` pins the first
#: unit, EC3-B13-U01, and is left untouched, per the Band-10/11/12 precedent).
REALIZATION_UNIT = "EC3-B13-U03"

# ---------------------------------------------------------------------------
# Traceability anchors (No-Orphan spine — EC-3-B13-P01 §5 / §11; GOV-001-T3)
# ---------------------------------------------------------------------------

#: Implementation substrate anchor: the certified/frozen baseline this unit builds upon
#: (EC-1 ``engine/**`` CERTIFIED + EC-2 ``platform/**`` FROZEN + Band-10 ``data/**``
#: CERTIFIED-COMPLETE + Band-11 ``service/**`` FROZEN + Band-12 ``application/**`` FROZEN
#: + Band-13 ``infrastructure.capability`` (EC3-B13-U01) + ``infrastructure.compute``
#: (EC3-B13-U02) CERTIFIED, at HEAD ``42a0c50``).
IMPLEMENTATION_ANCHOR = "42a0c50"

#: The Infrastructure leaf meta-class id realized by this unit (INFRASTRUCTURE-005 §2/§7).
INFRASTRUCTURE_META_CLASS = "NetworkResource"

#: The backward traceability chain every realized Network Resource records
#: (INFRASTRUCTURE-008 → root).
TRACE_BACKWARD: tuple[str, ...] = (
    "NetworkResource",  # INFRASTRUCTURE-005 §2 — leaf meta-class
    "INFRASTRUCTURE-008",  # Universal Infrastructure Network Architecture
    "INFRASTRUCTURE-005",  # Universal Infrastructure Meta-Model (UIMM)
    "INFRASTRUCTURE-001",  # Universal Infrastructure Constitution (UIL-01…15)
    "ARCH-INFRASTRUCTURE-001",  # Governing Infrastructure architecture constitution
    f"13-INFRASTRUCTURE@{CONSTITUTIONAL_ANCHOR}",  # frozen specification set
)

#: The frozen foundations the Network Resource reuses by reference (UIL-02):
#:   ENG-001…005 (EL-1) only. Connectivity is expressed **purely** as typed ENG-005
#:   references between hosted constructs (ICNW-01 / UIL-09) — a Network Resource binds
#:   no RL-F2 behavior (it is not a ProvisioningProcess and hosts no execution), hosts no
#:   DATA-010 datum (that is Storage-Hosting), and delivers no SF-2/AF-3 (that is
#:   Distribution). It declares its locality by an intra-band ENG-005 reference to a
#:   Locality (realized by the INFRASTRUCTURE-011 unit) and honors isolation boundaries by
#:   ENG-005 reference to an IsolationBoundary (likewise INFRASTRUCTURE-011).
SUBSTRATE_REFS: tuple[str, ...] = (
    "ENG-001",  # Identity  (identified-by)
    "ENG-002",  # Object    (borne-as-object)
    "ENG-003",  # Value     (capacity / value fidelity)
    "ENG-004",  # Type      (typed Connectivity Class, UIL-03)
    "ENG-005",  # Relationship/Reference (locatedAt / connectivity / boundary references)
)

# ---------------------------------------------------------------------------
# INFRASTRUCTURE-005 §2 — leaf meta-class closure (re-exported for local checks)
# ---------------------------------------------------------------------------

#: The meta-relationships a Network Resource intrinsically participates in.
#: A Resource is the domain of ``hosts`` ({Resource,Distribution} → FrozenLowerConstruct,
#: 1..*, downward-only/non-mutating) and ``locatedAt`` ({HostingStructure,Resource} →
#: Locality, multiplicity 1, total) — INFRASTRUCTURE-005 §4. For a Network Resource the
#: ``hosts`` edges are realized as its **connectivity links** — the typed ENG-005
#: reachability references to the hosted constructs it connects (ICNW-01/02; no new
#: connection construct — UIL-09). It is the domain of no ``contains``/``provisions``/
#: ``scales``/``sustains``/``evaluates`` edge (those are HostingStructure/Process/
#: Arrangement/Facet concerns); the evaluative Reachability Arrangement is the Topology
#: (INFRASTRUCTURE-010 / U06) it is referenced by, never founded here.
NETWORK_RELATIONSHIPS: tuple[str, ...] = ("hosts", "locatedAt")

# Re-export the shared, frozen vocabulary so downstream network modules import it from
# a single place without redefining any of it (UIL-02).
__SHARED__ = (
    ADMITTED_META_RELATIONSHIPS,
    LEAF_META_CLASSES,
    LIFECYCLE_ORDER,
    InfrastructureState,
)

# ---------------------------------------------------------------------------
# INFRASTRUCTURE-001 §7 — applicable Infrastructure Laws (UIL) for the Network Resource
# ---------------------------------------------------------------------------

#: The Infrastructure laws a Network Resource construct is directly obligated by.
#: The universal laws (UIL-01…05, UIL-15) plus the Resource/Network laws mapped from the
#: concern rules: UIL-07 (connectivity honors isolation boundaries; cross-boundary links
#: declared and typed — ICNW-03, the distinguishing Network law), UIL-08 (a resource
#: declares type/capacity/locality/connected endpoints — ICNW-02), UIL-09 (connectivity is
#: a typed ENG-005 reference; founding acyclic; no new connection construct — ICNW-01),
#: UIL-12 (typed connectivity selects no transport/protocol — ICNW-01/05), UIL-13 (network
#: capacity scaling unbounded — ICNW-04).
NETWORK_APPLICABLE_LAWS: tuple[str, ...] = (
    "UIL-01",
    "UIL-02",
    "UIL-03",
    "UIL-04",
    "UIL-05",
    "UIL-07",
    "UIL-08",
    "UIL-09",
    "UIL-12",
    "UIL-13",
    "UIL-15",
)

#: Laws scoped to Capability-reuse / Provisioning / Storage-Hosting / EvaluativeFacet
#: units, N/A to a Network Resource: UIL-06 (PL-F2/SF-2/AF-3 hosting/delivery — Capability/
#: Distribution), UIL-10 (provisioning binds RL-F2 — ProvisioningProcess; a NetworkResource
#: hosts no execution), UIL-11 (storage-hosting DATA-010 — Storage-Hosting), UIL-14
#: (security/governance evaluative non-enforcing — EvaluativeFacet; reachability-as-
#: evaluative is delegated to the Reachability Arrangement / Topology, U06, by reference).
NETWORK_INAPPLICABLE_LAWS: tuple[str, ...] = (
    "UIL-06",
    "UIL-10",
    "UIL-11",
    "UIL-14",
)

# ---------------------------------------------------------------------------
# INFRASTRUCTURE-008 §3 — concern rules (ICNW-01…05)
# ---------------------------------------------------------------------------

#: The five Network concern rules (INFRASTRUCTURE-008 §3).
NETWORK_CONCERN_RULES: dict[str, str] = {
    "ICNW-01": "Connectivity is a typed ENG-005 reference; no new connection construct; no "
    "protocol/transport selected.",
    "ICNW-02": "Every network resource declares type, capacity, locality, and connected "
    "endpoints.",
    "ICNW-03": "Connectivity honors isolation boundaries; cross-boundary links are declared "
    "and typed.",
    "ICNW-04": "Reachability is evaluative; network scaling is unbounded (no artificial "
    "ceiling).",
    "ICNW-05": "No transport/protocol/mesh/vendor selected; no authority conferred.",
}

# ---------------------------------------------------------------------------
# INFRASTRUCTURE-005 §5 — applicable well-formedness rules (WF) for the Network Resource
# ---------------------------------------------------------------------------

#: The WF rules a Network Resource is directly subject to. WF-5 (*every Resource declares
#: capacity and locality*) is the **governing, materially-exercised** rule for this unit,
#: alongside the Network-specific boundary-honoring obligation (ICNW-03 / UIL-07).
#: WF-4/6/7/8/9/10 are scoped to Environment/ProvisioningProcess/StorageHostingResource/
#: Distribution/ScalingArrangement/EvaluativeFacet constructs (INFRASTRUCTURE-005 §5) and
#: are recorded N/A to the Network Resource with rationale.
NETWORK_APPLICABLE_WF: tuple[str, ...] = ("WF-1", "WF-2", "WF-3", "WF-5", "WF-11", "WF-12")

#: WF rules scoped to other leaf meta-classes, N/A to the Network Resource.
NETWORK_INAPPLICABLE_WF: tuple[str, ...] = (
    "WF-4",
    "WF-6",
    "WF-7",
    "WF-8",
    "WF-9",
    "WF-10",
)

__all__ = [
    "REALIZATION_UNIT",
    "CONSTITUTIONAL_ANCHOR",
    "IMPLEMENTATION_ANCHOR",
    "INFRASTRUCTURE_META_CLASS",
    "TRACE_BACKWARD",
    "SUBSTRATE_REFS",
    "NETWORK_RELATIONSHIPS",
    "ADMITTED_META_RELATIONSHIPS",
    "LEAF_META_CLASSES",
    "LIFECYCLE_ORDER",
    "InfrastructureState",
    "INFRASTRUCTURE_LAWS",
    "NETWORK_APPLICABLE_LAWS",
    "NETWORK_INAPPLICABLE_LAWS",
    "INFRASTRUCTURE_COMPLIANCE",
    "NETWORK_CONCERN_RULES",
    "WELL_FORMEDNESS_RULES",
    "NETWORK_APPLICABLE_WF",
    "NETWORK_INAPPLICABLE_WF",
    "CCE_GATES",
]
