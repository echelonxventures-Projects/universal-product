"""EC3-B13-U10 — Universal Infrastructure Integration meta-model constants (UIMM closure).

Read-only projections of INFRASTRUCTURE-001 (Constitution), INFRASTRUCTURE-003 (Ontology),
INFRASTRUCTURE-005 (Meta-Model / UIMM), and INFRASTRUCTURE-018 (Infrastructure Master
Registry — the frozen concern/dependency registries).

This module carries, as executable constants, the fixed identifiers of the frozen
Infrastructure Foundation that the Universal Infrastructure Integration realization must
conform to. It **defines no new law, redefines no foundation concept, and re-implements no
concern** (UIL-02 / UIL-15). It only names — *by reference* — the nine already-CERTIFIED
Band-13 concern units (EC3-B13-U01…U09) and the canonical, downward-only dependency graph
that composes them, so the integration can be checked against the frozen meta-model
deterministically. The shared Infrastructure vocabulary (lifecycle states, admitted
relationships, the fifteen Infrastructure Laws, the twelve well-formedness rules, the seven
compliance conditions, the leaf-meta-class closure, and the CCE gate ids) is **imported by
reference** from the first Band-13 unit (:mod:`infrastructure.capability_meta`) and never
redefined.

The **one** leaf meta-class this unit realizes (INFRASTRUCTURE-005 §2) is
**InfrastructureDependency** ``«⊑ ENG-005 reference, by ref»`` — *the typed, identified,
downward-only, non-mutating reference by which one infrastructure construct depends on
another*. Its sole mandatory bespoke meta-attribute is ``downwardOnly = true`` (invariant;
INFRASTRUCTURE-005 §3) and it is realized through the ``dependsOn`` meta-relationship
(``InfrastructureConstruct → InfrastructureConstruct``, downward-only, acyclic —
INFRASTRUCTURE-005 §4 / WF-3). Realizing it **completes the UIMM leaf-meta-class closure
17 / 17**: the nine certified concerns own the other sixteen leaves (INFRASTRUCTURE-005 §7),
and ``InfrastructureDependency`` is the last, integration-bearing leaf.

This is engineering execution only (DE-05 / CCE-LAW-009). It asserts no constitutional
finality, selects no technology, embeds no secret, grants no access, mints no new
primitive/authority/registry/identifier/lifecycle (WF-11), and mutates no certified
concern (reuse-by-reference only).
"""

from __future__ import annotations

# --- Infrastructure vocabulary reused by reference from the first Band-13 unit ---
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

# ===========================================================================
# Identity binding (ENG-001 / WF-1)
# ===========================================================================

#: The realization unit this module set realizes (EC-3 Band 13, Unit 10 — the
#: integration/UIMM-closure unit).
REALIZATION_UNIT = "EC3-B13-U10"

#: The single Infrastructure leaf meta-class realized by this unit (INFRASTRUCTURE-005 §2).
#: Every construct instantiates exactly this one meta-class (WF-1).
DEPENDENCY_META_CLASS = "InfrastructureDependency"

#: The shared id-family prefix every Infrastructure construct id begins with (ENG-001).
#: Reused verbatim from the family established by EC3-B13-U01 — **not** a new id scheme
#: (WF-11 / no duplicated identifier system).
INFRA_DEPENDENCY_ID_FAMILY = "UCOS-INFRA-"

#: The deterministic id prefix for a realized InfrastructureDependency construct.
INFRA_DEPENDENCY_ID_PREFIX = "UCOS-INFRA-DEPENDENCY"

# ===========================================================================
# Ownership (CEP-002 single-owner) — non-constitutive (UIL-15 / WF-11)
# ===========================================================================

#: The single owner of this realization unit (CEP-002 single-owner rule).
OWNER = "EC-3 execution (AP-1)"

#: The authority this unit holds — engineering execution only; confers nothing (AUTH-06).
AUTHORITY = "ENGINEERING-EXECUTION-ONLY"

# ---------------------------------------------------------------------------
# Traceability anchors (No-Orphan spine — EC-3-B13-P01 §5 / §11; GOV-001-T3)
# ---------------------------------------------------------------------------

#: Implementation substrate anchor: the certified/frozen baseline this unit builds upon
#: (EC-1 engine CERTIFIED + EC-2 platform FROZEN + Band-10 data CERTIFIED-COMPLETE +
#: Band-11 service FROZEN + Band-12 application FROZEN + Band-13 U01…U07 CERTIFIED &
#: COMPLETE + U08 Security & U09 Governance CERTIFIED & PROVISIONALLY RATIFIED).
IMPLEMENTATION_ANCHOR = "5ed500b"

#: The backward-lineage tail every realized construct records after its meta-class root.
#: InfrastructureDependency is a foundation meta-model construct (INFRASTRUCTURE-005 §2),
#: so its lineage closes through the meta-model + constitution to the frozen anchor. The
#: master registry (INFRASTRUCTURE-018) is cited as the integration/composition basis.
TRACE_TAIL: tuple[str, ...] = (
    "INFRASTRUCTURE-018",  # Infrastructure Master Registry (concern + dependency registry)
    "INFRASTRUCTURE-005",  # Universal Infrastructure Meta-Model (UIMM) — defines the leaf
    "INFRASTRUCTURE-001",  # Universal Infrastructure Constitution (UIL-01…15)
    "ARCH-INFRASTRUCTURE-001",  # Governing Infrastructure architecture constitution
    f"13-INFRASTRUCTURE@{CONSTITUTIONAL_ANCHOR}",  # frozen specification set
)

#: The frozen foundations the InfrastructureDependency constructs reuse by reference
#: (UIL-02): ENG-001…005 (EL-1). A dependency ``«⊑ ENG-005 reference»`` introduces no new
#: connection construct (UIL-09) — it is a specialization of the frozen ENG-005 reference.
SUBSTRATE_REFS: tuple[str, ...] = (
    "ENG-001",  # Identity (identified-by)
    "ENG-002",  # Object (a dependency is borne as an ENG-002 object)
    "ENG-003",  # Value (value fidelity)
    "ENG-004",  # Type (typed construct, UIL-03)
    "ENG-005",  # Relationship/Reference — the dependency IS a specialization of this
)

#: The map of frozen-foundation primitives these constructs reuse by reference.
FOUNDATION_REUSE: dict[str, str] = {
    "ENG-001": "engine.certification.contracts.content_hash (deterministic identity)",
    "ENG-002": "python frozen object (immutable objecthood; the dependency as object)",
    "ENG-003": "engine.certification.contracts.canonical_json (value fidelity)",
    "ENG-004": "infrastructure.integration type_tag (typed construct)",
    "ENG-005": "the dependsOn reference itself — specialization of the frozen reference",
}

# ===========================================================================
# INFRASTRUCTURE-005 §7 / §2 — leaf-meta-class ownership per certified concern
# ===========================================================================


class ConcernUnit:
    """A read-only, reference-only descriptor of a CERTIFIED Band-13 concern unit.

    This is **not** a new construct or primitive (WF-11). It is a projection that names an
    already-certified unit (by its ``EC3-B13-U0N`` id and Python realization module) and the
    leaf meta-class(es) it owns, so the integration can compose the nine concerns *by
    reference* without re-implementing or mutating any of them.
    """

    __slots__ = ("unit", "index", "module", "title", "meta_classes")

    def __init__(
        self,
        unit: str,
        index: int,
        module: str,
        title: str,
        meta_classes: tuple[str, ...],
    ) -> None:
        self.unit = unit
        self.index = index
        self.module = module
        self.title = title
        self.meta_classes = meta_classes

    @property
    def ref(self) -> str:
        """The abstract ENG-005 reference to this concern unit (technology-neutral)."""
        return f"ENG-005:{self.unit}:infrastructure.{self.module}"

    def to_dict(self) -> dict[str, object]:
        return {
            "unit": self.unit,
            "index": self.index,
            "module": self.module,
            "title": self.title,
            "meta_classes": list(self.meta_classes),
            "ref": self.ref,
        }


#: The nine CERTIFIED Band-13 concern units, in canonical founding order (INFRASTRUCTURE-005
#: §7; INFRASTRUCTURE-018 §2). Each owns a disjoint set of UIMM leaf meta-classes. Named by
#: reference only — none is re-implemented here.
CONCERN_REGISTRY: tuple[ConcernUnit, ...] = (
    ConcernUnit("EC3-B13-U01", 1, "capability", "Universal Infrastructure Capability",
                ("InfrastructureCapability",)),
    ConcernUnit("EC3-B13-U02", 2, "compute", "Universal Infrastructure Compute",
                ("ComputeResource",)),
    ConcernUnit("EC3-B13-U03", 3, "network", "Universal Infrastructure Network",
                ("NetworkResource",)),
    ConcernUnit("EC3-B13-U04", 4, "storage", "Universal Infrastructure Storage-Hosting",
                ("StorageHostingResource",)),
    ConcernUnit("EC3-B13-U05", 5, "environment",
                "Universal Infrastructure Environment & Provisioning",
                ("Locality", "IsolationBoundary", "Node", "Cluster", "Environment",
                 "ProvisioningProcess")),
    ConcernUnit("EC3-B13-U06", 6, "topology",
                "Universal Infrastructure Topology & Distribution",
                ("Topology", "Distribution")),
    ConcernUnit("EC3-B13-U07", 7, "resilience",
                "Universal Infrastructure Resilience & Availability",
                ("AvailabilityTopology", "ScalingArrangement")),
    ConcernUnit("EC3-B13-U08", 8, "security", "Universal Infrastructure Security",
                ("SecurityFacet",)),
    ConcernUnit("EC3-B13-U09", 9, "governance", "Universal Infrastructure Governance",
                ("GovernanceFacet",)),
)

#: The number of certified concern units the integration composes (INFRASTRUCTURE-018 §2).
CONCERN_COUNT = len(CONCERN_REGISTRY)

#: Fast lookup of a concern descriptor by its Python realization module name.
CONCERN_BY_MODULE: dict[str, ConcernUnit] = {c.module: c for c in CONCERN_REGISTRY}

#: The leaf meta-class this unit itself realizes, completing the closure (17th leaf).
INTEGRATION_META_CLASSES: tuple[str, ...] = (DEPENDENCY_META_CLASS,)

# ===========================================================================
# INFRASTRUCTURE-005 §4 / WF-3 — the canonical downward-only dependency graph
# ===========================================================================

#: The admitted grounding bases for a concern-to-concern dependency edge. Each names the
#: frozen INFRASTRUCTURE-005 §4 meta-relationship that *grounds* the ``dependsOn`` edge
#: (the edge itself is always a ``dependsOn`` reference — the InfrastructureDependency leaf).
DEPENDENCY_BASES: tuple[str, ...] = (
    "reuses",       # a Resource reuses the Capability ability by reference (UIL-06 / ICAP-01)
    "contains",     # a HostingStructure contains Resources (INFRASTRUCTURE-005 §4)
    "provisions",   # a ProvisioningProcess provisions Resources (§4)
    "arranges",     # an Arrangement (Topology) arranges HostingStructures (§4)
    "sustains",     # an AvailabilityTopology sustains {Resource, Cluster} (§4)
    "scales",       # a ScalingArrangement scales Resources (§4)
    "evaluates",    # an EvaluativeFacet evaluates the hosting substrate (§4, non-enforcing)
)

#: The canonical, downward-only, acyclic integration dependency graph over the nine certified
#: concerns (INFRASTRUCTURE-005 §4 ``dependsOn`` — downward-only, acyclic; WF-3). Each entry
#: ``(source_module, target_module, basis)`` yields exactly one InfrastructureDependency
#: construct. Every edge points from a higher-founded concern to a strictly lower-founded one
#: (source index > target index), so the graph is acyclic by construction and every
#: ``downwardOnly`` invariant holds.
CANONICAL_EDGES: tuple[tuple[str, str, str], ...] = (
    # Resources reuse the foundational Capability ability (UIL-06 / ICAP-01).
    ("compute", "capability", "reuses"),
    ("network", "capability", "reuses"),
    ("storage", "capability", "reuses"),
    # Environment & Provisioning contains / provisions the resources.
    ("environment", "compute", "contains"),
    ("environment", "network", "contains"),
    ("environment", "storage", "provisions"),
    # Topology & Distribution arranges the hosting structures.
    ("topology", "environment", "arranges"),
    # Resilience & Availability sustains clusters and builds over the topology arrangement.
    ("resilience", "environment", "sustains"),
    ("resilience", "topology", "arranges"),
    # Security evaluates the whole hosting substrate (evaluative, non-enforcing).
    ("security", "capability", "evaluates"),
    ("security", "compute", "evaluates"),
    ("security", "network", "evaluates"),
    ("security", "storage", "evaluates"),
    ("security", "environment", "evaluates"),
    ("security", "topology", "evaluates"),
    ("security", "resilience", "evaluates"),
    # Governance evaluates all concerns, including Security (evaluative, non-enforcing).
    ("governance", "capability", "evaluates"),
    ("governance", "compute", "evaluates"),
    ("governance", "network", "evaluates"),
    ("governance", "storage", "evaluates"),
    ("governance", "environment", "evaluates"),
    ("governance", "topology", "evaluates"),
    ("governance", "resilience", "evaluates"),
    ("governance", "security", "evaluates"),
)

#: The number of canonical dependency edges (constructs) the integration realizes.
EDGE_COUNT = len(CANONICAL_EDGES)

# ---------------------------------------------------------------------------
# INFRASTRUCTURE-005 §4 — meta-relationships each construct participates in
# ---------------------------------------------------------------------------

#: The admitted meta-relationships an InfrastructureDependency participates in as a domain
#: (INFRASTRUCTURE-005 §4). A dependency IS a ``dependsOn`` reference; it is the domain of no
#: ``contains``/``hosts``/``locatedAt``/``provisions``/``scales``/``sustains``/``evaluates``
#: founding edge.
CONSTRUCT_RELATIONSHIPS: dict[str, tuple[str, ...]] = {
    "InfrastructureDependency": ("dependsOn",),
}

# ---------------------------------------------------------------------------
# INFRASTRUCTURE-005 §3 — the mandatory bespoke meta-attribute
# ---------------------------------------------------------------------------

#: InfrastructureDependency's mandatory bespoke meta-attribute (INFRASTRUCTURE-005 §3):
#: ``downwardOnly`` is a boolean invariant fixed true. A dependency may only point at a
#: strictly lower-founded construct.
DOWNWARD_ONLY_INVARIANT = True

# ---------------------------------------------------------------------------
# INFRASTRUCTURE-005 §4 / §7 — concern integration rules (IINT-01…06)
# ---------------------------------------------------------------------------

#: The six Infrastructure Integration concern rules (derived by reference from the frozen
#: meta-model + master registry; this unit introduces no new law — UIL-15 / WF-11).
INTEGRATION_CONCERN_RULES: dict[str, str] = {
    "IINT-01": "Composition is reuse-by-reference only; no concern is re-implemented (UIL-02).",
    "IINT-02": "Every dependency is a typed, identified ENG-005 reference (UIL-03/04/09).",
    "IINT-03": "Every dependency is downwardOnly=true; the dependsOn graph is acyclic (WF-3).",
    "IINT-04": "No duplicated ownership: each leaf meta-class is owned by exactly one concern.",
    "IINT-05": "One engine/runtime/registry/identifier reused; none duplicated (WF-11).",
    "IINT-06": "Non-constitutive: mints no primitive/authority, selects no technology (UIL-15).",
}

# ---------------------------------------------------------------------------
# INFRASTRUCTURE-001 §7 — applicable Infrastructure Laws (UIL) for the integration
# ---------------------------------------------------------------------------

#: The Infrastructure laws the InfrastructureDependency constructs are directly obligated by.
#: Universal laws (UIL-01…05, UIL-15) + UIL-09 (references reuse ENG-005; founding acyclic;
#: no new construct — the governing law for this leaf).
INTEGRATION_APPLICABLE_LAWS: tuple[str, ...] = (
    "UIL-01",
    "UIL-02",
    "UIL-03",
    "UIL-04",
    "UIL-05",
    "UIL-09",
    "UIL-15",
)

#: Laws scoped to hosting/resource/storage/distribution/provisioning/scaling/facet units,
#: N/A to the dependency reference construct.
INTEGRATION_INAPPLICABLE_LAWS: tuple[str, ...] = (
    "UIL-06",
    "UIL-07",
    "UIL-08",
    "UIL-10",
    "UIL-11",
    "UIL-12",
    "UIL-13",
    "UIL-14",
)

# ---------------------------------------------------------------------------
# INFRASTRUCTURE-005 §5 — applicable well-formedness rules (WF) for the integration
# ---------------------------------------------------------------------------

#: The WF rules the dependency constructs are directly subject to. WF-3 (the dependsOn graph
#: is acyclic — THE governing rule for this leaf) + WF-1/2/11/12.
INTEGRATION_APPLICABLE_WF: tuple[str, ...] = (
    "WF-1",
    "WF-2",
    "WF-3",
    "WF-11",
    "WF-12",
)

#: WF rules scoped to other leaf meta-classes, N/A to the dependency construct.
INTEGRATION_INAPPLICABLE_WF: tuple[str, ...] = (
    "WF-4",
    "WF-5",
    "WF-6",
    "WF-7",
    "WF-8",
    "WF-9",
    "WF-10",
)


def owned_meta_classes() -> tuple[str, ...]:
    """The full set of leaf meta-classes owned by the nine concerns + this unit (sorted).

    The union of the nine concerns' meta-classes plus ``InfrastructureDependency`` is exactly
    the frozen leaf-meta-class closure (INFRASTRUCTURE-005 §2 / §7) — 17 / 17.
    """
    owned: set[str] = set(INTEGRATION_META_CLASSES)
    for concern in CONCERN_REGISTRY:
        owned.update(concern.meta_classes)
    return tuple(sorted(owned))


def leaf_closure_complete() -> bool:
    """True iff concerns + this unit cover the full frozen leaf-meta-class closure (17/17)."""
    return set(owned_meta_classes()) == set(LEAF_META_CLASSES)


def ownership_is_disjoint() -> bool:
    """True iff no leaf meta-class is owned by more than one unit (no duplicated ownership)."""
    seen: set[str] = set()
    for concern in CONCERN_REGISTRY:
        for mc in concern.meta_classes:
            if mc in seen:
                return False
            seen.add(mc)
    return not (set(INTEGRATION_META_CLASSES) & seen)


__all__ = [
    "REALIZATION_UNIT",
    "DEPENDENCY_META_CLASS",
    "INFRA_DEPENDENCY_ID_FAMILY",
    "INFRA_DEPENDENCY_ID_PREFIX",
    "OWNER",
    "AUTHORITY",
    "CONSTITUTIONAL_ANCHOR",
    "IMPLEMENTATION_ANCHOR",
    "TRACE_TAIL",
    "SUBSTRATE_REFS",
    "FOUNDATION_REUSE",
    "ConcernUnit",
    "CONCERN_REGISTRY",
    "CONCERN_COUNT",
    "CONCERN_BY_MODULE",
    "INTEGRATION_META_CLASSES",
    "DEPENDENCY_BASES",
    "CANONICAL_EDGES",
    "EDGE_COUNT",
    "CONSTRUCT_RELATIONSHIPS",
    "DOWNWARD_ONLY_INVARIANT",
    "INTEGRATION_CONCERN_RULES",
    "INTEGRATION_APPLICABLE_LAWS",
    "INTEGRATION_INAPPLICABLE_LAWS",
    "INTEGRATION_APPLICABLE_WF",
    "INTEGRATION_INAPPLICABLE_WF",
    "ADMITTED_META_RELATIONSHIPS",
    "LEAF_META_CLASSES",
    "LIFECYCLE_ORDER",
    "InfrastructureState",
    "INFRASTRUCTURE_LAWS",
    "INFRASTRUCTURE_COMPLIANCE",
    "WELL_FORMEDNESS_RULES",
    "CCE_GATES",
    "owned_meta_classes",
    "leaf_closure_complete",
    "ownership_is_disjoint",
]
