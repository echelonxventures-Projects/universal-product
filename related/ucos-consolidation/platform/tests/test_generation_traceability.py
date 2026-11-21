"""EC2-EPIC-007 — generation-request traceability tests (GOV-002 link-4 continuation).

Asserts that a generation request materializes the ``Generation Artifact → Blueprint →
Request → Implementation Artifact`` trace edge: EPIC-006 closed the generation→blueprint
edge; EPIC-007 continues it through the Request node via RequestProvenance, so the full
chain is machine-checkable and the dispatch boundary carries the request→execution edge.
"""

from __future__ import annotations

from platform.blueprints.contracts import BlueprintFamily
from platform.foundation.bootstrap import bootstrap_platform
from platform.foundation.identity import Principal, Role
from platform.generation.bootstrap import bootstrap_generation_requests
from platform.generation.provenance import RequestProvenance
from platform.identity.service import bootstrap_identity


def _service_with_completed_request():
    ctx = bootstrap_platform()
    auth = bootstrap_identity(ctx)
    svc = bootstrap_generation_requests(ctx, authorization=auth)
    arch = Principal.create("arch@x", [Role.ARCHITECT])
    sess = auth.establish_session(arch, issued_at=0, ttl=1000)
    ws = svc.workspaces.create("team", "Team", "arch@x")
    req = svc.submit_request(
        sess.session_id, "req-1", "UCOS-BLPR-1", ws.workspace_id, BlueprintFamily.DATA, now=1
    )
    svc.start_validation(sess.session_id, req.request_id, now=2)
    svc.approve(sess.session_id, req.request_id, now=3)
    svc.enqueue(sess.session_id, req.request_id, now=4)
    svc.dispatch_request(sess.session_id, req.request_id, now=5, content_hash="c0ffee")
    return svc, sess, req


def _provenance(request_id):
    return RequestProvenance.create(
        request_ref=request_id,
        blueprint_ref="UCOS-BLPR-1",
        family=BlueprintFamily.DATA,
        generation_reference="GEN-DATA-001",
        generation_artifact_id="BP-DATA-0001",
        blueprint_provenance_ref="UCOS-BPRV-xyz",
        implementation_target="platform/generation",
        content_hash="c0ffee",
        dependency_chain=("EPIC-006",),
    )


def test_full_generation_to_implementation_chain_is_materialized():
    svc, sess, req = _service_with_completed_request()
    svc.record_provenance(sess.session_id, req.request_id, _provenance(req.request_id), now=6)
    edge = svc.trace(sess.session_id, req.request_id, now=7)
    # Backward: 05-GENERATION origin + the EPIC-006 blueprint provenance.
    assert edge["generation"]["artifact_id"] == "BP-DATA-0001"
    assert edge["blueprint"]["provenance_ref"] == "UCOS-BPRV-xyz"
    # Subject: this request. Forward: the implementation target.
    assert edge["request"]["request_ref"] == req.request_id
    assert edge["implementation"]["target"] == "platform/generation"
    assert edge["traceable"] is True


def test_dispatch_record_carries_request_to_execution_edge():
    svc, _, req = _service_with_completed_request()
    record = svc.dispatch.get(req.request_id)
    handoff = record.handoff_edge()
    assert handoff["request"]["request_ref"] == req.request_id
    assert handoff["blueprint"]["blueprint_ref"] == "UCOS-BLPR-1"
    assert "engine.runtime.assemble" in handoff["execution"]["engine_contracts"]


def test_status_reports_traceable_once_dispatched_and_provenance_recorded():
    svc, sess, req = _service_with_completed_request()
    # Dispatched but no provenance yet ⇒ not traceable.
    assert svc.status_of(req.request_id).is_traceable is False
    svc.record_provenance(sess.session_id, req.request_id, _provenance(req.request_id), now=6)
    assert svc.status_of(req.request_id).is_traceable is True


def test_mandatory_link4_fields_are_carried():
    prov = _provenance("UCOS-GREQ-1")
    d = prov.to_dict()
    for field in (
        "request_ref",
        "blueprint_ref",
        "generation_reference",
        "generation_artifact_id",
        "blueprint_provenance_ref",
        "implementation_target",
        "content_hash",
    ):
        assert d[field]
