"""EC3-B13-U05 — Environment & Provisioning construct tests (six leaf meta-classes).

Covers WF-1/2/3/4/6/11/12 + UIL-03/04/05/07/09/10/15 over Locality, IsolationBoundary,
Node, Cluster, Environment, and ProvisioningProcess, plus the shared base behavior and the
composition-level ``contains``-graph acyclicity (WF-3 / IENV-03).
"""

from __future__ import annotations

import pytest

from infrastructure.capability import InfrastructureError
from infrastructure.environment import (
    DEFAULT_PROVISIONING_WORKFLOW_REF,
    Cluster,
    Environment,
    IsolationBoundary,
    Locality,
    Node,
    ProvisioningProcess,
    containment_graph_acyclic,
    make_cluster,
    make_environment,
    make_isolation_boundary,
    make_locality,
    make_node,
    make_provisioning_process,
)
from infrastructure.environment_meta import InfrastructureState

LOC = "ENG-005:INFRASTRUCTURE-011:locality.foundation"
BOUND = "ENG-005:INFRASTRUCTURE-011:isolation.boundary.a"
RES = "ENG-005:INFRASTRUCTURE-007:compute.resource"


# --- Locality ---------------------------------------------------------------


def test_locality_is_typed_identified_and_foundational():
    loc = make_locality("ucos.demo.locality")
    assert loc.meta_class == "Locality"  # WF-1
    assert loc.type_tag == "ucos.demo.locality"  # UIL-03
    assert loc.construct_id.startswith("UCOS-INFRA-LOCALITY-")  # UIL-04
    assert len(loc.value_digest) == 64  # ENG-003
    assert loc.scope == "region"
    assert loc.meta_relationships() == ()  # foundational — participates in no founding edge
    assert loc.is_hosting_structure() is False
    assert loc.declares_mandatory_attributes() is True
    assert loc.references_resolve() is True  # WF-2 — no required refs (vacuous)
    assert loc.to_dict()["scope"] == "region"


def test_locality_rejects_empty_type_and_scope_and_bad_state():
    with pytest.raises(InfrastructureError):
        make_locality("")  # UIL-03
    with pytest.raises(InfrastructureError):
        Locality(type_tag="t", scope="")  # abstract scope required
    with pytest.raises(InfrastructureError):
        Locality(type_tag="t", scope="   ")
    with pytest.raises(InfrastructureError):
        Locality(type_tag="t", state="BAD")  # type: ignore[arg-type]


# --- IsolationBoundary ------------------------------------------------------


def test_isolation_boundary_is_typed_identified_and_foundational():
    b = make_isolation_boundary("ucos.demo.boundary")
    assert b.meta_class == "IsolationBoundary"
    assert b.construct_id.startswith("UCOS-INFRA-BOUNDARY-")
    assert b.meta_relationships() == ()
    assert b.is_hosting_structure() is False
    assert b.declares_mandatory_attributes() is True
    assert b.to_dict()["meta_class"] == "IsolationBoundary"


def test_isolation_boundary_rejects_empty_type_and_bad_state():
    with pytest.raises(InfrastructureError):
        make_isolation_boundary("")
    with pytest.raises(InfrastructureError):
        IsolationBoundary(type_tag="t", state="BAD")  # type: ignore[arg-type]


# --- Node -------------------------------------------------------------------


def test_node_contains_resources_and_is_located():
    n = make_node("ucos.demo.node", LOC, contains=(RES,))
    assert n.meta_class == "Node"
    assert n.construct_id.startswith("UCOS-INFRA-NODE-")
    assert n.meta_relationships() == ("contains", "locatedAt")
    assert n.is_hosting_structure() is True
    assert n.located_by_reference() is True
    assert n.contains_by_reference() is True
    assert n.declares_mandatory_attributes() is True
    assert n.references_resolve() is True
    payload = n.to_dict()
    assert payload["locality_ref"] == LOC
    assert payload["contains"] == [RES]


def test_node_rejects_missing_locality_empty_contains_and_bad_refs():
    with pytest.raises(InfrastructureError):
        make_node("", LOC, contains=(RES,))  # UIL-03
    with pytest.raises(InfrastructureError):
        make_node("t", "", contains=(RES,))  # locatedAt required
    with pytest.raises(InfrastructureError):
        Node(type_tag="t", locality_ref=LOC, contains=())  # WF-2 — ≥1 contained
    with pytest.raises(InfrastructureError):
        Node(type_tag="t", locality_ref=LOC, contains=[RES])  # type: ignore[arg-type] — not a tuple
    with pytest.raises(InfrastructureError):
        Node(type_tag="t", locality_ref=LOC, contains=("",))  # empty ref
    with pytest.raises(InfrastructureError):
        Node(type_tag="t", locality_ref=LOC, contains=(RES,), state="BAD")  # type: ignore[arg-type]


# --- Cluster ----------------------------------------------------------------


def test_cluster_contains_nodes_and_is_located():
    n = make_node("ucos.demo.node", LOC, contains=(RES,))
    c = make_cluster("ucos.demo.cluster", LOC, contains=(n.construct_id,))
    assert c.meta_class == "Cluster"
    assert c.construct_id.startswith("UCOS-INFRA-CLUSTER-")
    assert c.meta_relationships() == ("contains", "locatedAt")
    assert c.is_hosting_structure() is True
    assert c.located_by_reference() is True
    assert c.contains_by_reference() is True
    assert c.declares_mandatory_attributes() is True
    assert c.to_dict()["contains"] == [n.construct_id]


def test_cluster_rejects_bad_inputs():
    with pytest.raises(InfrastructureError):
        make_cluster("", LOC, contains=(RES,))
    with pytest.raises(InfrastructureError):
        make_cluster("t", "", contains=(RES,))
    with pytest.raises(InfrastructureError):
        Cluster(type_tag="t", locality_ref=LOC, contains=())
    with pytest.raises(InfrastructureError):
        Cluster(type_tag="t", locality_ref=LOC, contains=(RES,), state="BAD")  # type: ignore[arg-type]


# --- Environment ------------------------------------------------------------


def test_environment_declares_single_boundary_and_contains():
    e = make_environment("ucos.demo.env", BOUND, LOC, contains=(RES,))
    assert e.meta_class == "Environment"
    assert e.construct_id.startswith("UCOS-INFRA-ENVIRONMENT-")
    assert e.meta_relationships() == ("contains", "locatedAt")
    assert e.is_hosting_structure() is True
    assert e.declares_single_boundary() is True  # WF-4 / UIL-07 — governing rule
    assert e.located_by_reference() is True
    assert e.contains_by_reference() is True
    assert e.declares_mandatory_attributes() is True
    payload = e.to_dict()
    assert payload["boundary_ref"] == BOUND
    assert payload["locality_ref"] == LOC
    assert payload["contains"] == [RES]


def test_environment_rejects_missing_boundary_locality_contains():
    with pytest.raises(InfrastructureError):
        make_environment("", BOUND, LOC, contains=(RES,))  # UIL-03
    with pytest.raises(InfrastructureError):
        make_environment("t", "", LOC, contains=(RES,))  # WF-4 — must declare boundary
    with pytest.raises(InfrastructureError):
        make_environment("t", BOUND, "", contains=(RES,))  # locatedAt required
    with pytest.raises(InfrastructureError):
        Environment(type_tag="t", boundary_ref=BOUND, locality_ref=LOC, contains=())  # ≥1
    with pytest.raises(InfrastructureError):
        Environment(
            type_tag="t",
            boundary_ref=BOUND,
            locality_ref=LOC,
            contains=(RES,),
            state="BAD",  # type: ignore[arg-type]
        )


# --- ProvisioningProcess ----------------------------------------------------


def test_provisioning_process_provisions_and_binds_runtime_workflow():
    p = make_provisioning_process("ucos.demo.prov", provisions=(RES,))
    assert p.meta_class == "ProvisioningProcess"
    assert p.construct_id.startswith("UCOS-INFRA-PROVISIONING-")
    assert p.meta_relationships() == ("provisions",)
    assert p.is_hosting_structure() is False
    assert p.binds_runtime_workflow() is True  # WF-6 / UIL-10 — governing rule
    assert p.provisions_by_reference() is True
    assert p.workflow_ref == DEFAULT_PROVISIONING_WORKFLOW_REF
    assert p.declares_mandatory_attributes() is True
    payload = p.to_dict()
    assert payload["provisions"] == [RES]
    assert payload["workflow_ref"] == DEFAULT_PROVISIONING_WORKFLOW_REF


def test_provisioning_process_rejects_bad_inputs():
    with pytest.raises(InfrastructureError):
        make_provisioning_process("", provisions=(RES,))  # UIL-03
    with pytest.raises(InfrastructureError):
        ProvisioningProcess(type_tag="t", provisions=())  # WF-2 — ≥1 provisioned
    with pytest.raises(InfrastructureError):
        ProvisioningProcess(type_tag="t", provisions=(RES,), workflow_ref="")  # WF-6
    with pytest.raises(InfrastructureError):
        ProvisioningProcess(type_tag="t", provisions=(RES,), state="BAD")  # type: ignore[arg-type]


# --- shared base behavior (identity, determinism, non-constitutiveness) -----


def test_identity_is_deterministic_and_core_derived():
    a = make_locality("t")
    b = make_locality("t")
    c = make_locality("t", scope="zone")
    assert a.construct_id == b.construct_id  # same core → same ENG-001 identity
    assert a.construct_id != c.construct_id  # different scope → different id


def test_constructs_are_immutable_objecthood():
    loc = make_locality("t")
    with pytest.raises((AttributeError, TypeError)):
        loc.type_tag = "other"  # frozen object (ENG-002)


def test_all_constructs_are_not_resource_not_facet_and_founding_acyclic():
    constructs = (
        make_locality("t"),
        make_isolation_boundary("t"),
        make_node("t", LOC, contains=(RES,)),
        make_cluster("t", LOC, contains=(RES,)),
        make_environment("t", BOUND, LOC, contains=(RES,)),
        make_provisioning_process("t", provisions=(RES,)),
    )
    for c in constructs:
        assert c.is_resource() is False  # WF-5 N/A
        assert c.is_evaluative_facet() is False  # WF-10 N/A
        assert c.is_founding_acyclic() is True  # WF-3
        assert c.confers_authority() is False  # UIL-15
        assert c.enacts_enforcement() is False  # UIL-14
        assert c.redefines_foundation() is False  # UIL-02
        assert c.projects_completion() is False  # WF-12
        assert c.is_new_primitive() is False  # WF-11
        assert c.selects_technology() is False  # UIL-15 (abstract refs only)
        assert c.embeds_secret() is False
        assert c.to_dict()["substrate_refs"][0] == "ENG-001"


def test_technology_and_secret_are_detected():
    techy = make_node("t", LOC, contains=("ENG-005:kubernetes:pod",))
    assert techy.selects_technology() is True  # UIL-15 / IENV-06
    leaky = make_node("t", "ENG-005:INFRASTRUCTURE-011:password-store", contains=(RES,))
    assert leaky.embeds_secret() is True  # UIL-15 / RR-07


def test_lifecycle_is_forward_only_and_rejects_non_state_target():
    p = make_provisioning_process("t", provisions=(RES,), state=InfrastructureState.DEFINED)
    provisioned = p.transition(InfrastructureState.PROVISIONED)
    assert provisioned.state is InfrastructureState.PROVISIONED
    active = provisioned.transition(InfrastructureState.ACTIVE)
    assert active.state is InfrastructureState.ACTIVE
    with pytest.raises(InfrastructureError):
        active.transition(InfrastructureState.DEFINED)  # forward-only
    with pytest.raises(InfrastructureError):
        p.transition("ACTIVE")  # type: ignore[arg-type]


def test_transition_preserves_construct_type():
    loc = make_locality("t")
    assert isinstance(loc.transition(InfrastructureState.PROVISIONED), Locality)


# --- containment-graph acyclicity (WF-3 / UIL-09 / IENV-03) -----------------


def test_containment_graph_is_acyclic_for_a_well_formed_composition():
    loc = make_locality("t")
    node = make_node("t", loc.construct_id, contains=(RES,))
    cluster = make_cluster("t", loc.construct_id, contains=(node.construct_id,))
    boundary = make_isolation_boundary("t")
    env = make_environment(
        "t", boundary.construct_id, loc.construct_id, contains=(cluster.construct_id,)
    )
    prov = make_provisioning_process("t", provisions=(RES,))
    assert containment_graph_acyclic((loc, boundary, node, cluster, env, prov)) is True


class _FakeHostingStructure:
    """A duck-typed hosting structure used to force a containment cycle (WF-3 negative)."""

    def __init__(self, construct_id: str, contains: tuple[str, ...]) -> None:
        self._id = construct_id
        self.contains = contains

    def is_hosting_structure(self) -> bool:
        return True

    @property
    def construct_id(self) -> str:
        return self._id


def test_containment_graph_detects_a_direct_cycle():
    a = _FakeHostingStructure("A", ("B",))
    b = _FakeHostingStructure("B", ("A",))  # A → B → A
    assert containment_graph_acyclic((a, b)) is False  # type: ignore[arg-type]


def test_containment_graph_detects_a_transitive_cycle():
    a = _FakeHostingStructure("A", ("B",))
    b = _FakeHostingStructure("B", ("C",))
    c = _FakeHostingStructure("C", ("A",))  # A → B → C → A
    assert containment_graph_acyclic((a, b, c)) is False  # type: ignore[arg-type]


def test_containment_graph_ignores_non_hosting_structures():
    # A Locality has no contains edge; the graph over it alone is trivially acyclic.
    assert containment_graph_acyclic((make_locality("t"),)) is True
