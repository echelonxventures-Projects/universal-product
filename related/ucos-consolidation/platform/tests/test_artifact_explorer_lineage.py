"""EC2-TASK-000129 — Artifact lineage / provenance / trace projection tests (EC2-EPIC-009).

Covers the navigation projections derived by reference from EC2-EPIC-007 records: the
:class:`ArtifactProvenance` link-4 projection (which reuses the existing provenance id and
reproduces the certified trace edge), the ordered :class:`ArtifactLineage`, and the full
generation→execution :class:`ArtifactTrace`.
"""

from __future__ import annotations

from platform.artifact_explorer.context import ArtifactContext
from platform.artifact_explorer.errors import (
    ArtifactLineageError,
    ArtifactProvenanceError,
    ArtifactServiceError,
    ArtifactTraceError,
)
from platform.artifact_explorer.lineage import (
    ArtifactLineage,
    ArtifactProvenance,
    ArtifactTrace,
)
from platform.artifact_explorer.references import ArtifactView
from platform.blueprints.contracts import BlueprintFamily
from platform.foundation.identity import Principal, Role
from platform.generation.dispatch import DispatchRecord
from platform.generation.provenance import RequestProvenance
from platform.generation.registry import GenerationRequestRegistry

import pytest


def _request():
    reg = GenerationRequestRegistry()
    return reg.create(
        "artifact-1",
        "UCOS-BLPR-1",
        "UCOS-WSPC-1",
        "arch@x",
        BlueprintFamily.DATA,
        submitted_tick=1,
        tenant="acme",
    )


def _dispatch(request):
    return DispatchRecord.create(
        request_ref=request.request_id,
        blueprint_ref=request.blueprint_ref,
        family=request.family,
        content_hash="c0ffee",
        tick=5,
    )


def _provenance(request):
    return RequestProvenance.create(
        request_ref=request.request_id,
        blueprint_ref=request.blueprint_ref,
        family=request.family,
        generation_reference="GEN-DATA-001",
        generation_artifact_id="BP-DATA-0001",
        blueprint_provenance_ref="UCOS-BPRV-xyz",
        implementation_target="platform/generation",
        content_hash="c0ffee",
        dependency_chain=("EPIC-006",),
    )


# --------------------------------------------------------------------------- #
# ArtifactProvenance                                                          #
# --------------------------------------------------------------------------- #


def test_provenance_projection_reuses_id_and_reproduces_edge():
    req = _request()
    prov = _provenance(req)
    projection = ArtifactProvenance.from_provenance(prov)
    # Reuses the existing provenance id (no duplicate provenance model).
    assert projection.provenance_id == prov.provenance_id
    assert projection.is_traceable is True
    # The edge is byte-for-byte the certified trace edge (faithful projection).
    assert projection.edge() == prov.trace_edge()
    assert projection.to_dict()["generation_artifact_id"] == "BP-DATA-0001"
    assert projection.fingerprint() == ArtifactProvenance.from_provenance(prov).fingerprint()


def test_provenance_projection_rejects_bad_input():
    with pytest.raises(ArtifactProvenanceError):
        ArtifactProvenance.from_provenance("nope")  # type: ignore[arg-type]


# --------------------------------------------------------------------------- #
# ArtifactLineage                                                             #
# --------------------------------------------------------------------------- #


def test_lineage_complete_with_provenance():
    req = _request()
    lineage = ArtifactLineage.from_request(req, provenance=_provenance(req))
    assert lineage.lineage_id.startswith("UCOS-AXLN-")
    assert lineage.is_complete is True
    kinds = [kind for kind, _ in lineage.nodes]
    assert kinds == ["generation", "blueprint", "request", "implementation"]
    assert lineage.dependency_chain == ("EPIC-006",)
    edge = lineage.edge()
    assert edge["link"] == "artifact-lineage"
    assert edge["complete"] is True
    assert lineage.to_dict()["is_complete"] is True
    assert (
        lineage.fingerprint()
        == ArtifactLineage.from_request(req, provenance=_provenance(req)).fingerprint()
    )


def test_lineage_partial_without_provenance():
    req = _request()
    lineage = ArtifactLineage.from_request(req)
    kinds = [kind for kind, _ in lineage.nodes]
    assert kinds == ["blueprint", "request"]
    assert lineage.is_complete is False
    assert lineage.dependency_chain == ()


def test_lineage_rejects_bad_inputs():
    with pytest.raises(ArtifactLineageError):
        ArtifactLineage.from_request("nope")  # type: ignore[arg-type]
    with pytest.raises(ArtifactLineageError):
        ArtifactLineage.from_request(_request(), provenance="nope")  # type: ignore[arg-type]


# --------------------------------------------------------------------------- #
# ArtifactTrace                                                               #
# --------------------------------------------------------------------------- #


def test_trace_full_when_provenance_and_dispatch_present():
    req = _request()
    trace = ArtifactTrace.from_parts(req, provenance=_provenance(req), dispatch=_dispatch(req))
    assert trace.trace_id.startswith("UCOS-AXTR-")
    assert trace.has_provenance is True
    assert trace.has_dispatch is True
    assert trace.is_traceable is True
    assert trace.provenance_edge["link"] == "GOV-002-link-4"
    assert "engine.runtime.assemble" in trace.dispatch_edge["execution"]["engine_contracts"]
    assert trace.edge()["traceable"] is True
    assert trace.to_dict()["is_traceable"] is True
    assert (
        trace.fingerprint()
        == ArtifactTrace.from_parts(
            req, provenance=_provenance(req), dispatch=_dispatch(req)
        ).fingerprint()
    )


def test_trace_not_traceable_without_dispatch():
    req = _request()
    trace = ArtifactTrace.from_parts(req, provenance=_provenance(req))
    assert trace.has_dispatch is False
    assert trace.dispatch_edge is None
    assert trace.is_traceable is False


def test_trace_empty_when_nothing_recorded():
    trace = ArtifactTrace.from_parts(_request())
    assert trace.provenance_edge is None
    assert trace.dispatch_edge is None
    assert trace.is_traceable is False


def test_trace_rejects_bad_inputs():
    req = _request()
    with pytest.raises(ArtifactTraceError):
        ArtifactTrace.from_parts("nope")  # type: ignore[arg-type]
    with pytest.raises(ArtifactTraceError):
        ArtifactTrace.from_parts(req, provenance="nope")  # type: ignore[arg-type]
    with pytest.raises(ArtifactTraceError):
        ArtifactTrace.from_parts(req, dispatch="nope")  # type: ignore[arg-type]


# --------------------------------------------------------------------------- #
# ArtifactContext                                                             #
# --------------------------------------------------------------------------- #


def test_context_binds_view_and_principal():
    req = _request()
    view = ArtifactView.from_request(req, dispatch=_dispatch(req), provenance=_provenance(req))
    principal = Principal.create("arch@x", [Role.ARCHITECT], tenant="acme")
    ctx = ArtifactContext.create(view, principal, is_owner=True)
    assert ctx.context_id.startswith("UCOS-AXCX-")
    assert ctx.is_owner is True
    assert ctx.is_traceable is True
    assert ctx.subject == "arch@x"
    assert ctx.to_dict()["context_id"] == ctx.context_id
    assert ctx.fingerprint() == ArtifactContext.create(view, principal, is_owner=True).fingerprint()


def test_context_rejects_bad_inputs():
    req = _request()
    view = ArtifactView.from_request(req)
    principal = Principal.create("arch@x", [Role.ARCHITECT])
    with pytest.raises(ArtifactServiceError):
        ArtifactContext.create("nope", principal)  # type: ignore[arg-type]
    with pytest.raises(ArtifactServiceError):
        ArtifactContext.create(view, "nope")  # type: ignore[arg-type]
    with pytest.raises(ArtifactServiceError):
        ArtifactContext.create(view, principal, is_owner="yes")  # type: ignore[arg-type]
