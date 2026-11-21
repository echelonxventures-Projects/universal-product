"""EC3-B13-U01 — Infrastructure Capability meta-model constants.

Read-only projections of INFRASTRUCTURE-001 (Constitution), INFRASTRUCTURE-003
(Ontology), INFRASTRUCTURE-005 (Meta-Model), and INFRASTRUCTURE-006 (Capability
concern architecture).

This module carries, as executable constants, the fixed identifiers of the frozen
Infrastructure Foundation (IF-1 = INFRASTRUCTURE-001…005, frozen by INFRASTRUCTURE-015)
that the Universal Infrastructure Capability realization must conform to. It **defines
no new law and redefines no foundation concept** (UIL-02 / UIL-15); it only names the
frozen obligations so the realization can be checked against them deterministically.

Everything here is derived verbatim from the frozen ``13-INFRASTRUCTURE/`` specification
at the constitutional anchor ``b7e7657``:

* The **InfrastructureCapability** leaf meta-class (INFRASTRUCTURE-005 §2) — *"the
  implementation-independent hosting/delivery ability an infrastructure realizes"*
  ``«⊑ PLATFORM-006 / SF-2 capability, by ref»`` — INFRASTRUCTURE-006 §1.
* Its capability constructs (INFRASTRUCTURE-006 §2): Hosting / Delivery / Provisioning
  / Scaling / Resilience — the classification kinds of an infrastructure capability.
* Its concern rules ICAP-01…05 (INFRASTRUCTURE-006 §3) and the twelve well-formedness
  rules WF-1…12 (INFRASTRUCTURE-005 §5) it is validated against.
"""

from __future__ import annotations

from enum import Enum

# ---------------------------------------------------------------------------
# Traceability anchors (No-Orphan spine — EC-3-B13-P01 §5 / §11; GOV-001-T3)
# ---------------------------------------------------------------------------

#: Constitutional anchor: the frozen 13-INFRASTRUCTURE/ specification commit
#: (where INFRASTRUCTURE-001…018 + GOV-000 + EXEC-001 are authoritative).
CONSTITUTIONAL_ANCHOR = "b7e7657"

#: Implementation substrate anchor: the certified/frozen baseline this builds upon
#: (EC-1 ``engine/**`` CERTIFIED + EC-2 ``platform/**`` FROZEN + Band-10 ``data/**``
#: CERTIFIED-COMPLETE + Band-11 ``service/**`` FROZEN + Band-12 ``application/**``
#: FROZEN at HEAD ``aec646f``).
IMPLEMENTATION_ANCHOR = "aec646f"

#: The Infrastructure leaf meta-class id realized by this unit (INFRASTRUCTURE-005 §2).
INFRASTRUCTURE_META_CLASS = "InfrastructureCapability"

#: The backward traceability chain every realized Infrastructure Capability records
#: (INFRASTRUCTURE-006 → root).
TRACE_BACKWARD: tuple[str, ...] = (
    "InfrastructureCapability",  # INFRASTRUCTURE-005 §2 — leaf meta-class
    "INFRASTRUCTURE-006",  # Universal Infrastructure Capability Architecture
    "INFRASTRUCTURE-005",  # Universal Infrastructure Meta-Model (UIMM)
    "INFRASTRUCTURE-001",  # Universal Infrastructure Constitution (UIL-01…15)
    "ARCH-INFRASTRUCTURE-001",  # Governing Infrastructure architecture constitution
    f"13-INFRASTRUCTURE@{CONSTITUTIONAL_ANCHOR}",  # frozen specification set
)

#: The frozen foundations the Infrastructure Capability reuses by reference (UIL-02).
#:   ENG-001…005 (EL-1) · RL-F2 (behavior) · PL-F2/PLATFORM-006 (capability composition)
#:   · SF-2 (hosted operation capability). DF-2 storage-hosting is scoped to the
#:   Storage-Hosting unit; AF-3 delivery-hosting is exercised by the Delivery kind's
#:   enable target. A capability declares no capacity/locality (those are Resource
#:   meta-attributes, INFRASTRUCTURE-005 §3, scoped to the Resource units).
SUBSTRATE_REFS: tuple[str, ...] = (
    "ENG-001",  # Identity  (identified-by)
    "ENG-002",  # Object    (borne-as-object)
    "ENG-003",  # Value     (value fidelity)
    "ENG-004",  # Type      (typed, UIL-03)
    "ENG-005",  # Relationship/Reference (reuse/enable/dependsOn references)
    "RL-F2",  # Runtime behavior (the ability to perform hosting/delivery work; UIL-10)
    "PL-F2",  # Platform composition (PLATFORM-006 capability construct, by reference; ICAP-01)
    "SF-2",  # Service capability (hosted/delivered operation capability, by reference; UIL-06)
)

# ---------------------------------------------------------------------------
# INFRASTRUCTURE-005 §2 — leaf meta-class closure
# ---------------------------------------------------------------------------

#: The sixteen leaf meta-classes admitted by the frozen UIMM (INFRASTRUCTURE-005 §2).
#: InfrastructureCapability is realized by this unit (EC3-B13-U01).
LEAF_META_CLASSES: tuple[str, ...] = (
    "Environment",
    "Cluster",
    "Node",
    "ComputeResource",
    "NetworkResource",
    "StorageHostingResource",
    "Topology",
    "Distribution",
    "ScalingArrangement",
    "AvailabilityTopology",
    "ProvisioningProcess",
    "Locality",
    "IsolationBoundary",
    "InfrastructureCapability",
    "InfrastructureDependency",
    "SecurityFacet",
    "GovernanceFacet",
)

#: The eight admitted meta-relationships (INFRASTRUCTURE-005 §4). All are
#: specializations of ``ENG-005::Reference`` (no new connection construct — UIL-09).
ADMITTED_META_RELATIONSHIPS: tuple[str, ...] = (
    "contains",
    "hosts",
    "locatedAt",
    "provisions",
    "scales",
    "sustains",
    "dependsOn",
    "evaluates",
)

#: The meta-relationships an Infrastructure Capability intrinsically participates in.
#: A capability reuses PLATFORM-006/SF-2 and enables a frozen lower construct **by
#: reference** — realized as downward-only ``dependsOn`` references (ENG-005). It is the
#: domain of no ``contains``/``hosts``/``locatedAt``/``provisions``/``scales``/``sustains``/
#: ``evaluates`` edge (those are HostingStructure/Resource/Process/Arrangement/Facet
#: concerns, INFRASTRUCTURE-005 §4).
CAPABILITY_RELATIONSHIPS: tuple[str, ...] = ("dependsOn",)


class InfrastructureCapabilityKind(str, Enum):
    """INFRASTRUCTURE-006 §2 — the classification of an Infrastructure Capability.

    A capability is classified by exactly one kind (single-facet). Each kind names the
    frozen construct family it enables **by reference** (ICAP-03):
    """

    HOSTING = "Hosting-Capability"  # host a lower-layer construct within a resource
    DELIVERY = "Delivery-Capability"  # deliver hosted experience/operations to actors
    PROVISIONING = "Provisioning-Capability"  # bring a resource into/out of existence
    SCALING = "Scaling-Capability"  # expand/contract capacity (evaluative, unbounded)
    RESILIENCE = "Resilience-Capability"  # sustain continuity across failure


class InfrastructureState(str, Enum):
    """INFRASTRUCTURE-003 §3 — the forward-only infrastructure lifecycle states.

    The only state vocabulary the frozen Infrastructure Foundation defines
    (``provisioningState``: defined → provisioned → active → decommissioned;
    INFRASTRUCTURE-005 §3 / INFRASTRUCTURE-003 §3). Reused verbatim — not invented —
    as the forward-only lifecycle of an infrastructure construct.
    """

    DEFINED = "DEFINED"  # declared but not yet provisioned
    PROVISIONED = "PROVISIONED"  # brought into existence, not yet active
    ACTIVE = "ACTIVE"  # hosting/delivering (authoritative)
    DECOMMISSIONED = "DECOMMISSIONED"  # brought out of existence, retained for history


#: The forward-only lifecycle order (no in-place reversal; INFRASTRUCTURE-003 §3).
LIFECYCLE_ORDER: tuple[InfrastructureState, ...] = (
    InfrastructureState.DEFINED,
    InfrastructureState.PROVISIONED,
    InfrastructureState.ACTIVE,
    InfrastructureState.DECOMMISSIONED,
)

# ---------------------------------------------------------------------------
# INFRASTRUCTURE-001 §7 — Infrastructure Laws (UIL-01…15) and §12 — Compliance (C1…C7)
# ---------------------------------------------------------------------------

#: The fifteen Infrastructure Laws (INFRASTRUCTURE-001 §7), each mapped to its short
#: obligation.
INFRASTRUCTURE_LAWS: dict[str, str] = {
    "UIL-01": "Realization-environment layer founded on frozen EL-1/RL-F2/PL-F2/DF-2/SF-2/AF-3.",
    "UIL-02": "Reuses ENG-001…005/runtime/platform/data/service/application by reference.",
    "UIL-03": "Every infrastructure construct is classified by an ENG-004 Type; none untyped.",
    "UIL-04": "A construct-as-thing bears an ENG-001 Identity via an ENG-002 Object; one scheme.",
    "UIL-05": "Every construct-as-thing IS an ENG-002 Object; no parallel thing-model.",
    "UIL-06": "Hosting/delivery consumes PL-F2/SF-2/AF-3 by reference; re-founds none.",
    "UIL-07": "Every environment is bounded, cohesive, isolated; declares its boundary.",
    "UIL-08": "Every resource declares type, capacity, locality, and hosted constructs.",
    "UIL-09": "Topology reuses PL-F2 + ENG-005 references; founding acyclic; no new construct.",
    "UIL-10": "Provisioning binds frozen RL-F2 by reference; re-founds no PLATFORM-012/013.",
    "UIL-11": "Storage-hosting hosts DF-2 data (DATA-010) by reference; redefines no data.",
    "UIL-12": "Distribution/delivery typed, hosts AF-3/SF-2 by reference; no transport tech.",
    "UIL-13": "Resilience/availability/scaling evaluative RL-F2-bound; scaling unbounded.",
    "UIL-14": "Security/governance evaluative, non-enforcing; grant/enforce nothing.",
    "UIL-15": "Non-constitutive: no new primitive, authority, secret, or technology.",
}

#: The Infrastructure laws a bare Infrastructure Capability construct is directly
#: obligated by. UIL-07/08/09/11/12/14 (environment/resource/topology/storage/
#: distribution/security-governance) apply to the Environment/Resource/Topology/
#: Storage-Hosting/Distribution/Facet units; they are recorded not-applicable-to-the-
#: Capability with rationale. UIL-13 applies to the Scaling capability kind.
CAPABILITY_APPLICABLE_LAWS: tuple[str, ...] = (
    "UIL-01",
    "UIL-02",
    "UIL-03",
    "UIL-04",
    "UIL-05",
    "UIL-06",
    "UIL-10",
    "UIL-13",
    "UIL-15",
)

#: Laws scoped to Environment/Resource/Topology/Storage/Distribution/Facet units,
#: N/A to the Capability.
CAPABILITY_INAPPLICABLE_LAWS: tuple[str, ...] = (
    "UIL-07",
    "UIL-08",
    "UIL-09",
    "UIL-11",
    "UIL-12",
    "UIL-14",
)

#: The seven Infrastructure compliance conditions (INFRASTRUCTURE-001 §12). A construct
#: is COMPLIANT iff all applicable conditions hold, decided on evidence deterministically.
INFRASTRUCTURE_COMPLIANCE: dict[str, str] = {
    "C1": "Typed (UIL-03), identified and objecthood-bound (UIL-04/05).",
    "C2": "Reuses frozen foundations by reference without redefinition (UIL-02).",
    "C3": "Hosts/delivers PL-F2/SF-2/AF-3 by reference; hosted data DF-2 by ref (UIL-06/11).",
    "C4": "Environments bounded/isolated, resources explicit, distribution typed (UIL-07/08/12).",
    "C5": "Topology uses ENG-005 references; founding structure is acyclic (UIL-09).",
    "C6": "Provisioning/scaling bind RL-F2/DF-2 by ref; no artificial ceiling (UIL-10/11/13).",
    "C7": "Selects no technology, confers no authority, embeds no secret (UIL-15).",
}

# ---------------------------------------------------------------------------
# INFRASTRUCTURE-006 §3 — concern rules (ICAP-01…05)
# ---------------------------------------------------------------------------

#: The five Infrastructure Capability concern rules (INFRASTRUCTURE-006 §3).
CAPABILITY_CONCERN_RULES: dict[str, str] = {
    "ICAP-01": "Every capability reuses PLATFORM-006/SF-2 by reference; none is re-founded.",
    "ICAP-02": "Every capability is a typed, identified ENG-002 object.",
    "ICAP-03": "Hosting/delivery target frozen lower constructs by reference; never mutating.",
    "ICAP-04": "Scaling capability declares no artificial ceiling (physical reality only).",
    "ICAP-05": "Capability confers no authority; selects no technology.",
}

# ---------------------------------------------------------------------------
# INFRASTRUCTURE-005 §5/§6 — well-formedness rules (WF-1…12) + UIMM-CONF
# ---------------------------------------------------------------------------

#: The twelve UIMM well-formedness rules (INFRASTRUCTURE-005 §5).
WELL_FORMEDNESS_RULES: dict[str, str] = {
    "WF-1": "Instantiates exactly one leaf meta-class; declares all mandatory meta-attributes.",
    "WF-2": "Every hosts/locates/provisions range is a frozen lower construct, not redefined.",
    "WF-3": "The contains and dependsOn graphs are acyclic in founding structure.",
    "WF-4": "Every Environment has one boundary; cross-boundary hosts is a typed reference.",
    "WF-5": "Every Resource declares capacity and locality.",
    "WF-6": "Every ProvisioningProcess binds an RL-F2 workflow; re-founds no PLATFORM-012/013.",
    "WF-7": "Every StorageHostingResource hosts a DATA-010 datum by reference.",
    "WF-8": "Every Distribution hosts AF-3/SF-2 by reference; no transport technology selected.",
    "WF-9": "Every ScalingArrangement declares scalingPosture with no artificial ceiling.",
    "WF-10": "Every EvaluativeFacet has nonEnforcing = true.",
    "WF-11": "No construct is a new primitive/authority/registry/identifier/lifecycle.",
    "WF-12": "No construct projects architecture existence as implementation completion.",
}

#: The WF rules an Infrastructure Capability is directly subject to. WF-4…WF-10 are
#: scoped to Environment/Resource/Provisioning/Storage/Distribution/Scaling/
#: EvaluativeFacet constructs (INFRASTRUCTURE-005 §5) and are recorded N/A to the
#: Capability with rationale.
CAPABILITY_APPLICABLE_WF: tuple[str, ...] = ("WF-1", "WF-2", "WF-3", "WF-11", "WF-12")

#: WF rules scoped to other leaf meta-classes, N/A to the Capability.
CAPABILITY_INAPPLICABLE_WF: tuple[str, ...] = (
    "WF-4",
    "WF-5",
    "WF-6",
    "WF-7",
    "WF-8",
    "WF-9",
    "WF-10",
)

#: The CCE ten-gate identifiers (EC-3 certification strategy, CC-1…CC-10).
CCE_GATES: tuple[str, ...] = tuple(f"CC-{n}" for n in range(1, 11))

__all__ = [
    "CONSTITUTIONAL_ANCHOR",
    "IMPLEMENTATION_ANCHOR",
    "INFRASTRUCTURE_META_CLASS",
    "TRACE_BACKWARD",
    "SUBSTRATE_REFS",
    "LEAF_META_CLASSES",
    "ADMITTED_META_RELATIONSHIPS",
    "CAPABILITY_RELATIONSHIPS",
    "InfrastructureCapabilityKind",
    "InfrastructureState",
    "LIFECYCLE_ORDER",
    "INFRASTRUCTURE_LAWS",
    "CAPABILITY_APPLICABLE_LAWS",
    "CAPABILITY_INAPPLICABLE_LAWS",
    "INFRASTRUCTURE_COMPLIANCE",
    "CAPABILITY_CONCERN_RULES",
    "WELL_FORMEDNESS_RULES",
    "CAPABILITY_APPLICABLE_WF",
    "CAPABILITY_INAPPLICABLE_WF",
    "CCE_GATES",
]
