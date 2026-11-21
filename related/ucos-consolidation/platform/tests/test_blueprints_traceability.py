"""EC2-EPIC-006 — GOV-002 link-4 trace-closure tests.

The primary objective of EPIC-006: discharge the ``05-GENERATION → 06-IMPLEMENTATION``
(Generation Framework → Implementation Program) traceability BREAK (GOV-002 §6 link-4;
GOV-004 BLK-AUTH-TRC-01; EXEC-001 RSK-01). These tests assert the evidence-backed,
machine-checkable ``Generation Artifact → Blueprint → Request → Implementation
Artifact`` trace edge is materially present for every cataloged blueprint — no synthetic
and no inferred linkage.
"""

from __future__ import annotations

from platform.blueprints.associations import BlueprintAssociationKind
from platform.blueprints.contracts import BlueprintFamily
from platform.blueprints.provenance import BlueprintProvenance
from platform.foundation.bootstrap import bootstrap_platform
from platform.foundation.identity import Principal, Role
from platform.identity.service import bootstrap_identity

import pytest

# The mandatory link-4 provenance fields (mission traceability requirement).
_REQUIRED_FIELDS = (
    "generation_reference",
    "generation_artifact_id",
    "generation_source",
    "generation_lineage",
    "implementation_target",
    "implementation_lineage",
    "dependency_chain",
    "content_hash",
    "provenance_metadata",
    "audit_metadata",
)


def _service():
    ctx = bootstrap_platform()
    auth = bootstrap_identity(ctx)
    from platform.blueprints.bootstrap import bootstrap_blueprints

    service = bootstrap_blueprints(ctx, authorization=auth)
    arch = Principal.create("arch@x", [Role.ARCHITECT])
    sess = auth.establish_session(arch, issued_at=0, ttl=1000)
    ws = service.workspaces.create("team", "Team", "arch@x")
    return service, sess, ws


def _provenance(blueprint_id):
    return BlueprintProvenance.create(
        blueprint_ref=blueprint_id,
        family=BlueprintFamily.DATA,
        generation_reference="GEN-DATA-001",
        generation_artifact_id="BP-DATA-0001",
        generation_source="05-GENERATION/UCOS-GEN-DATA-001",
        implementation_target="platform/blueprints/EC2-EPIC-006",
        content_hash="deadbeef",
        generation_lineage=("data",),
        implementation_lineage=("EC2-EPIC-006", "EC2-TASK-000104"),
        dependency_chain=("EC2-EPIC-005", "EC-1 registry/classification"),
        provenance_metadata={"framework": "GEN-DATA-001"},
        audit_metadata={"authored_by": "arch@x"},
    )


def test_provenance_carries_all_mandatory_link4_fields():
    p = _provenance("UCOS-BLPR-1")
    for field in _REQUIRED_FIELDS:
        assert hasattr(p, field)
    d = p.to_dict()
    for field in _REQUIRED_FIELDS:
        assert field in d


def test_cataloged_blueprint_materialises_generation_to_implementation_edge():
    service, sess, ws = _service()
    bp = service.author_blueprint(
        sess.session_id, "bp-data-1", "Data BP", ws.workspace_id, BlueprintFamily.DATA, now=1
    )
    service.classify(sess.session_id, bp.blueprint_id, BlueprintFamily.DATA, now=2)
    service.validate(sess.session_id, bp.blueprint_id, now=3)
    entry = service.catalog_blueprint(
        sess.session_id, bp.blueprint_id, _provenance(bp.blueprint_id), now=4
    )

    edge = entry.trace_edge()
    # Generation origin present (backward edge).
    assert edge["generation"]["reference"] == "GEN-DATA-001"
    assert edge["generation"]["artifact_id"] == "BP-DATA-0001"
    assert edge["generation"]["source"].startswith("05-GENERATION")
    # Implementation target present (forward edge) — the previously-absent citation.
    assert edge["implementation"]["target"] == "platform/blueprints/EC2-EPIC-006"
    # The blueprint is the middle node.
    assert edge["blueprint"]["blueprint_ref"] == bp.blueprint_id
    # link-4 is materially PRESENT.
    assert edge["link"] == "GOV-002-link-4"
    assert edge["traceable"] is True


def test_full_generation_blueprint_request_implementation_chain():
    service, sess, ws = _service()
    bp = service.author_blueprint(
        sess.session_id, "bp-data-1", "Data BP", ws.workspace_id, BlueprintFamily.DATA, now=1
    )
    service.classify(sess.session_id, bp.blueprint_id, BlueprintFamily.DATA, now=2)
    service.validate(sess.session_id, bp.blueprint_id, now=3)
    service.catalog_blueprint(sess.session_id, bp.blueprint_id, _provenance(bp.blueprint_id), now=4)
    # Generation Artifact → Blueprint (backward), Blueprint → Request/Implementation (forward).
    service.associate(
        sess.session_id,
        bp.blueprint_id,
        BlueprintAssociationKind.GENERATION_ARTIFACT,
        "BP-DATA-0001",
        now=5,
    )
    service.associate(
        sess.session_id, bp.blueprint_id, BlueprintAssociationKind.REQUEST, "REQ-1", now=6
    )
    service.associate(
        sess.session_id,
        bp.blueprint_id,
        BlueprintAssociationKind.IMPLEMENTATION,
        "IMPL-1",
        now=7,
    )
    kinds = {a.kind for a in service.associations.associations_of(bp.blueprint_id)}
    assert BlueprintAssociationKind.GENERATION_ARTIFACT in kinds
    assert BlueprintAssociationKind.REQUEST in kinds
    assert BlueprintAssociationKind.IMPLEMENTATION in kinds
    # Trace edge remains present and machine-checkable.
    assert service.trace(sess.session_id, bp.blueprint_id, now=8)["traceable"] is True


def test_link4_closure_requires_provenance_no_synthetic_linkage():
    # A cataloged blueprint cannot exist without an explicit provenance citation:
    # cataloging without provenance is refused, so no synthetic/inferred edge is possible.
    service, sess, ws = _service()
    bp = service.author_blueprint(
        sess.session_id, "bp-data-1", "Data BP", ws.workspace_id, BlueprintFamily.DATA, now=1
    )
    service.classify(sess.session_id, bp.blueprint_id, BlueprintFamily.DATA, now=2)
    service.validate(sess.session_id, bp.blueprint_id, now=3)
    with pytest.raises(Exception):  # noqa: B017 - service/provenance error
        service.catalog_blueprint(sess.session_id, bp.blueprint_id, None, now=4)  # type: ignore[arg-type]
    assert bp.blueprint_id not in service.catalog


def test_provenance_health_probe_guards_link4_admissibility():
    service, sess, ws = _service()
    bp = service.author_blueprint(
        sess.session_id, "bp-data-1", "Data BP", ws.workspace_id, BlueprintFamily.DATA, now=1
    )
    service.classify(sess.session_id, bp.blueprint_id, BlueprintFamily.DATA, now=2)
    service.validate(sess.session_id, bp.blueprint_id, now=3)
    service.catalog_blueprint(sess.session_id, bp.blueprint_id, _provenance(bp.blueprint_id), now=4)
    # Every cataloged blueprint carries provenance ⇒ provenance-integrity check healthy.
    assert service.health.uncited_catalogued_blueprints() == ()
    assert service.health.healthy is True
