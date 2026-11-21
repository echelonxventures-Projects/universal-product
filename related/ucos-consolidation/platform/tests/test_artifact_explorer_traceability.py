"""EC2-EPIC-009 — artifact-explorer traceability tests (GOV-002 link continuation).

Asserts that the explorer surfaces — read-only, by reference — the full
``Generation Artifact → Blueprint → Request → Implementation Artifact`` lineage/provenance
edge produced by EC2-EPIC-007, plus the ``Request → Execution Runtime`` dispatch handoff,
so an artifact is navigable end to end without re-deriving or mutating any record.
"""

from __future__ import annotations

from platform.artifact_explorer.bootstrap import bootstrap_artifact_explorer
from platform.blueprints.contracts import BlueprintFamily
from platform.foundation.bootstrap import bootstrap_platform
from platform.foundation.identity import Principal, Role
from platform.generation.bootstrap import bootstrap_generation_requests
from platform.generation.provenance import RequestProvenance
from platform.identity.service import bootstrap_identity


def _fixture():
    ctx = bootstrap_platform()
    auth = bootstrap_identity(ctx)
    generation = bootstrap_generation_requests(ctx, authorization=auth)
    explorer = bootstrap_artifact_explorer(ctx, authorization=auth, generation=generation)
    arch = Principal.create("arch@x", [Role.ARCHITECT])
    sess = auth.establish_session(arch, issued_at=0, ttl=1000)
    ws = generation.workspaces.create("team", "Team", "arch@x")
    req = generation.submit_request(
        sess.session_id, "req-1", "UCOS-BLPR-1", ws.workspace_id, BlueprintFamily.DATA, now=1
    )
    generation.start_validation(sess.session_id, req.request_id, now=2)
    generation.approve(sess.session_id, req.request_id, now=3)
    generation.enqueue(sess.session_id, req.request_id, now=4)
    generation.dispatch_request(sess.session_id, req.request_id, now=5, content_hash="c0ffee")
    generation.record_provenance(
        sess.session_id,
        req.request_id,
        RequestProvenance.create(
            request_ref=req.request_id,
            blueprint_ref="UCOS-BLPR-1",
            family=BlueprintFamily.DATA,
            generation_reference="GEN-DATA-001",
            generation_artifact_id="BP-DATA-0001",
            blueprint_provenance_ref="UCOS-BPRV-xyz",
            implementation_target="platform/generation",
            content_hash="c0ffee",
            dependency_chain=("EPIC-006",),
        ),
        now=6,
    )
    return explorer, sess, req


def test_lineage_materializes_full_chain():
    explorer, sess, req = _fixture()
    lineage = explorer.lineage(sess.session_id, req.request_id, now=7)
    kinds = [kind for kind, _ in lineage.nodes]
    assert kinds == ["generation", "blueprint", "request", "implementation"]
    assert lineage.is_complete is True
    assert lineage.dependency_chain == ("EPIC-006",)


def test_provenance_projection_is_faithful_to_certified_edge():
    explorer, sess, req = _fixture()
    projection = explorer.artifact_provenance(sess.session_id, req.request_id, now=7)
    certified = explorer.provenance.get(req.request_id)
    assert projection.provenance_id == certified.provenance_id
    assert projection.edge() == certified.trace_edge()
    assert projection.edge()["generation"]["artifact_id"] == "BP-DATA-0001"
    assert projection.edge()["implementation"]["target"] == "platform/generation"


def test_trace_navigates_generation_to_execution():
    explorer, sess, req = _fixture()
    trace = explorer.trace(sess.session_id, req.request_id, now=7)
    assert trace.is_traceable is True
    assert trace.provenance_edge["link"] == "GOV-002-link-4"
    assert "engine.runtime.assemble" in trace.dispatch_edge["execution"]["engine_contracts"]


def test_view_reports_traceable_once_dispatched_and_provenance_recorded():
    explorer, sess, req = _fixture()
    view = explorer.get_artifact(sess.session_id, req.request_id, now=7)
    assert view.has_dispatch is True
    assert view.has_provenance is True
    assert view.is_traceable is True
    assert view.reference.implementation_target == "platform/generation"
