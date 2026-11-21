"""EC2-TASK-000128 — Artifact reference/summary/view projection tests (EC2-EPIC-009).

Covers the read-only projections of a generation artifact: the by-reference
:class:`ArtifactReference`, the lightweight :class:`ArtifactSummary`, and the full
:class:`ArtifactView` — including the with/without dispatch/provenance branches,
deterministic content-addressing, and fail-closed validation.
"""

from __future__ import annotations

from platform.artifact_explorer.errors import ArtifactReferenceError
from platform.artifact_explorer.references import (
    ArtifactReference,
    ArtifactSummary,
    ArtifactView,
)
from platform.blueprints.contracts import BlueprintFamily
from platform.generation.dispatch import DispatchRecord
from platform.generation.provenance import RequestProvenance
from platform.generation.registry import GenerationRequestRegistry

import pytest


def _request(tenant=None):
    reg = GenerationRequestRegistry()
    return reg.create(
        "artifact-1",
        "UCOS-BLPR-1",
        "UCOS-WSPC-1",
        "arch@x",
        BlueprintFamily.DATA,
        submitted_tick=1,
        tenant=tenant,
        project_id="UCOS-PROJ-1",
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
# ArtifactReference                                                            #
# --------------------------------------------------------------------------- #


def test_reference_bare_has_no_generation_or_content():
    ref = ArtifactReference.create(_request())
    assert ref.reference_id.startswith("UCOS-AXRF-")
    assert ref.generation_artifact_id == ""
    assert ref.implementation_target == ""
    assert ref.content_hash == ""
    assert ref.has_dispatch is False
    assert ref.has_provenance is False


def test_reference_content_hash_from_dispatch_only():
    req = _request()
    ref = ArtifactReference.create(req, dispatch=_dispatch(req))
    assert ref.has_dispatch is True
    assert ref.content_hash == "c0ffee"
    assert ref.generation_artifact_id == ""


def test_reference_prefers_provenance_citations():
    req = _request()
    ref = ArtifactReference.create(req, dispatch=_dispatch(req), provenance=_provenance(req))
    assert ref.has_provenance is True
    assert ref.generation_artifact_id == "BP-DATA-0001"
    assert ref.implementation_target == "platform/generation"
    assert ref.content_hash == "c0ffee"
    assert ref.to_dict()["reference_id"] == ref.reference_id
    assert (
        ref.fingerprint()
        == ArtifactReference.create(
            req, dispatch=_dispatch(req), provenance=_provenance(req)
        ).fingerprint()
    )


def test_reference_rejects_bad_inputs():
    req = _request()
    with pytest.raises(ArtifactReferenceError):
        ArtifactReference.create("nope")  # type: ignore[arg-type]
    with pytest.raises(ArtifactReferenceError):
        ArtifactReference.create(req, dispatch="nope")  # type: ignore[arg-type]
    with pytest.raises(ArtifactReferenceError):
        ArtifactReference.create(req, provenance="nope")  # type: ignore[arg-type]


# --------------------------------------------------------------------------- #
# ArtifactSummary                                                              #
# --------------------------------------------------------------------------- #


def test_summary_projection_is_deterministic():
    req = _request(tenant="acme")
    a = ArtifactSummary.from_request(req, has_dispatch=True, has_provenance=True)
    b = ArtifactSummary.from_request(req, has_dispatch=True, has_provenance=True)
    assert a.summary_id == b.summary_id
    assert a.summary_id.startswith("UCOS-AXSM-")
    assert a.is_traceable is True
    assert a.tenant == "acme"
    assert a.to_dict()["owner_subject"] == "arch@x"
    assert a.fingerprint() == b.fingerprint()


def test_summary_not_traceable_without_both():
    req = _request()
    s = ArtifactSummary.from_request(req, has_dispatch=True, has_provenance=False)
    assert s.is_traceable is False


def test_summary_rejects_non_bool_flags():
    req = _request()
    with pytest.raises(ArtifactReferenceError):
        ArtifactSummary.from_request(req, has_dispatch="yes", has_provenance=True)  # type: ignore[arg-type]
    with pytest.raises(ArtifactReferenceError):
        ArtifactSummary.from_request(req, has_dispatch=True, has_provenance="no")  # type: ignore[arg-type]
    with pytest.raises(ArtifactReferenceError):
        ArtifactSummary.from_request("nope", has_dispatch=True, has_provenance=True)  # type: ignore[arg-type]


# --------------------------------------------------------------------------- #
# ArtifactView                                                                 #
# --------------------------------------------------------------------------- #


def test_view_full_projection_and_summary_roundtrip():
    req = _request(tenant="acme")
    view = ArtifactView.from_request(req, dispatch=_dispatch(req), provenance=_provenance(req))
    assert view.view_id.startswith("UCOS-AXVW-")
    assert view.has_dispatch is True
    assert view.has_provenance is True
    assert view.is_traceable is True
    assert view.reference.generation_artifact_id == "BP-DATA-0001"
    summary = view.summary()
    assert summary.summary_id.startswith("UCOS-AXSM-")
    # The view's summary matches a direct summary projection (faithful).
    direct = ArtifactSummary.from_request(req, has_dispatch=True, has_provenance=True)
    assert summary.summary_id == direct.summary_id
    assert view.to_dict()["reference"]["reference_id"] == view.reference.reference_id
    assert (
        view.fingerprint()
        == ArtifactView.from_request(
            req, dispatch=_dispatch(req), provenance=_provenance(req)
        ).fingerprint()
    )


def test_view_bare_request_is_partial():
    view = ArtifactView.from_request(_request())
    assert view.has_dispatch is False
    assert view.has_provenance is False
    assert view.is_traceable is False
    assert view.reference.content_hash == ""


def test_view_rejects_bad_request():
    with pytest.raises(ArtifactReferenceError):
        ArtifactView.from_request("nope")  # type: ignore[arg-type]
