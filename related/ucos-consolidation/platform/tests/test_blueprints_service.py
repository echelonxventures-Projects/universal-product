"""EC2-TASK-000106 — Blueprint service tests (EC2-EPIC-006).

Covers the governed L3/L6 composition point end to end: fail-closed construction and
component validation, authorization-gated authoring scoped to an active parent
workspace with owner recording, the read-only EC-1 classification façade, structural
validation with fail-closed gap-report rejection (P4), link-4 cataloging (provenance
mandatory), versioning, supersession, retirement, association add/remove, the composed
access decision (identity ∧ isolation ∧ owner/administrator scoping) — including every
denial reason — selection/context, discovery/search, deterministic status, trace
(link-4 evidence), health, deterministic evidence (P5), and governed-action emission.
"""

from __future__ import annotations

from platform.blueprints.associations import BlueprintAssociationKind, BlueprintAssociationRegistry
from platform.blueprints.catalog import BlueprintCatalog
from platform.blueprints.classification import ClassificationLedger
from platform.blueprints.contracts import BlueprintAction, BlueprintFamily, BlueprintStatus
from platform.blueprints.errors import (
    BlueprintAccessError,
    BlueprintProvenanceError,
    BlueprintServiceError,
    BlueprintValidationError,
)
from platform.blueprints.health import BlueprintHealth, blueprint_health_checks
from platform.blueprints.provenance import BlueprintProvenance, ProvenanceLedger
from platform.blueprints.registry import BlueprintRegistry
from platform.blueprints.search import BlueprintSearch
from platform.blueprints.service import (
    BLUEPRINT_ACCESS_EVENT,
    BLUEPRINT_AUTHORED_EVENT,
    BLUEPRINT_CATALOGUED_EVENT,
    BLUEPRINT_TRACEABILITY_LINKED_EVENT,
    BlueprintService,
    build_blueprint_service,
)
from platform.foundation.bootstrap import bootstrap_platform
from platform.foundation.identity import Permission, Principal, Role
from platform.identity.contracts import CapabilityGroup
from platform.identity.roles import (
    RoleDefinition,
    RoleGrant,
    RoleRegistry,
    default_role_definitions,
)
from platform.identity.service import build_authorization_service
from platform.observability.health import HealthRegistry
from platform.observability.service import build_observability_service
from platform.workspace.contracts import WorkspaceStatus
from platform.workspace.errors import WorkspaceRegistryError
from platform.workspace.registration import WorkspaceRegistry

import pytest

# --------------------------------------------------------------------------- #
# Helpers                                                                      #
# --------------------------------------------------------------------------- #


def _fixture(*, events=None, observability=None, authorization=None):
    auth = authorization or build_authorization_service(events=events)
    workspaces = WorkspaceRegistry()
    service = build_blueprint_service(
        authorization=auth,
        workspaces=workspaces,
        observability=observability,
        events=events,
    )
    return auth, workspaces, service


def _session(auth, role, subject="arch@x", tenant=None):
    return auth.establish_session(
        Principal.create(subject, [role], tenant=tenant), issued_at=0, ttl=1000
    )


def _workspace(workspaces, *, tenant=None, slug="team"):
    return workspaces.create(slug, slug.title(), "owner@x", tenant=tenant)


def _authored(auth, workspaces, service, *, subject="arch@x", tenant=None, slug="bp-1"):
    ws = _workspace(workspaces, tenant=tenant, slug=f"ws-{slug}")
    session = _session(auth, Role.ARCHITECT, subject=subject, tenant=tenant)
    bp = service.author_blueprint(
        session.session_id, slug, "BP", ws.workspace_id, BlueprintFamily.DATA, now=1
    )
    return session, bp


def _provenance(blueprint_id):
    return BlueprintProvenance.create(
        blueprint_ref=blueprint_id,
        family=BlueprintFamily.DATA,
        generation_reference="GEN-DATA-001",
        generation_artifact_id="BP-DATA-0001",
        generation_source="05-GENERATION/GEN-DATA-001",
        implementation_target="platform/blueprints",
        content_hash="c0ffee",
        generation_lineage=("data",),
        implementation_lineage=("EC2-EPIC-006",),
        dependency_chain=("EPIC-005",),
    )


def _catalogued(auth, workspaces, service, **kw):
    session, bp = _authored(auth, workspaces, service, **kw)
    service.classify(session.session_id, bp.blueprint_id, BlueprintFamily.DATA, now=2)
    service.validate(session.session_id, bp.blueprint_id, now=3)
    service.catalog_blueprint(
        session.session_id, bp.blueprint_id, _provenance(bp.blueprint_id), now=4
    )
    return session, bp


def _valid_kwargs(auth, workspaces):
    reg = BlueprintRegistry()
    cls = ClassificationLedger()
    prov = ProvenanceLedger()
    assoc = BlueprintAssociationRegistry()
    hr = HealthRegistry()
    for check in blueprint_health_checks():
        hr.register(check)
    return {
        "registry": reg,
        "classifications": cls,
        "provenance": prov,
        "associations": assoc,
        "catalog": BlueprintCatalog(reg, prov),
        "authorization": auth,
        "workspaces": workspaces,
        "search": BlueprintSearch(reg, auth),
        "health": BlueprintHealth(reg, prov, assoc),
        "health_registry": hr,
    }


# --------------------------------------------------------------------------- #
# Construction                                                                 #
# --------------------------------------------------------------------------- #


def test_build_requires_authorization_and_workspaces():
    with pytest.raises(BlueprintServiceError):
        build_blueprint_service(authorization="nope", workspaces=WorkspaceRegistry())  # type: ignore[arg-type]
    with pytest.raises(BlueprintServiceError):
        build_blueprint_service(authorization=build_authorization_service(), workspaces="nope")  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "field",
    [
        "registry",
        "classifications",
        "provenance",
        "associations",
        "catalog",
        "authorization",
        "workspaces",
        "search",
        "health",
        "health_registry",
    ],
)
def test_service_rejects_each_invalid_required_component(field):
    auth = build_authorization_service()
    workspaces = WorkspaceRegistry()
    kwargs = _valid_kwargs(auth, workspaces)
    kwargs[field] = "nope"
    with pytest.raises(BlueprintServiceError):
        BlueprintService(**kwargs)  # type: ignore[arg-type]


@pytest.mark.parametrize("field", ["observability", "events"])
def test_service_rejects_each_invalid_optional_component(field):
    auth = build_authorization_service()
    workspaces = WorkspaceRegistry()
    kwargs = _valid_kwargs(auth, workspaces)
    kwargs[field] = "nope"
    with pytest.raises(BlueprintServiceError):
        BlueprintService(**kwargs)  # type: ignore[arg-type]


def test_component_property_getters():
    auth, _, service = _fixture()
    assert service.registry is not None
    assert service.classifications is not None
    assert service.provenance is not None
    assert service.associations is not None
    assert service.catalog is not None
    assert service.authorization is auth
    assert service.workspaces is not None
    assert service.health is not None
    assert service.observability is None
    assert service.access_evaluation_count == 0


# --------------------------------------------------------------------------- #
# Authoring                                                                    #
# --------------------------------------------------------------------------- #


def test_author_records_owner_and_emits_event():
    events = bootstrap_platform().events
    auth, workspaces, service = _fixture(events=events)
    ws = _workspace(workspaces, tenant="acme")
    session = _session(auth, Role.ARCHITECT, subject="arch@x", tenant="acme")
    bp = service.author_blueprint(
        session.session_id, "bp", "BP", ws.workspace_id, BlueprintFamily.DATA, now=1
    )
    assert bp.owner_subject == "arch@x"
    assert bp.status is BlueprintStatus.DRAFT
    assert bp.tenant == "acme"
    assert len(events.events_of(BLUEPRINT_AUTHORED_EVENT)) == 1


def test_author_denied_without_create_grant():
    auth, workspaces, service = _fixture()
    ws = _workspace(workspaces)
    session = _session(auth, Role.OPERATOR)  # no authoring CREATE
    with pytest.raises(BlueprintAccessError):
        service.author_blueprint(
            session.session_id, "bp", "BP", ws.workspace_id, BlueprintFamily.DATA, now=1
        )


def test_author_denied_cross_tenant():
    auth, workspaces, service = _fixture()
    ws = _workspace(workspaces, tenant="beta")
    session = _session(auth, Role.ARCHITECT, subject="arch@x", tenant="acme")
    with pytest.raises(BlueprintAccessError):
        service.author_blueprint(
            session.session_id, "bp", "BP", ws.workspace_id, BlueprintFamily.DATA, now=1
        )


def test_author_denied_when_workspace_not_active():
    auth, workspaces, service = _fixture()
    ws = _workspace(workspaces)
    workspaces.transition(ws.workspace_id, WorkspaceStatus.SUSPENDED, tick=0)
    session = _session(auth, Role.ARCHITECT)
    with pytest.raises(BlueprintAccessError):
        service.author_blueprint(
            session.session_id, "bp", "BP", ws.workspace_id, BlueprintFamily.DATA, now=1
        )


def test_author_unknown_workspace_fail_closed():
    auth, _, service = _fixture()
    session = _session(auth, Role.ARCHITECT)
    with pytest.raises(WorkspaceRegistryError):
        service.author_blueprint(
            session.session_id, "bp", "BP", "UCOS-WSPC-missing", BlueprintFamily.DATA, now=1
        )


# --------------------------------------------------------------------------- #
# Classify / validate (P4)                                                     #
# --------------------------------------------------------------------------- #


def test_classify_then_validate_promotes_to_validated():
    events = bootstrap_platform().events
    auth, workspaces, service = _fixture(events=events)
    session, bp = _authored(auth, workspaces, service)
    c = service.classify(session.session_id, bp.blueprint_id, BlueprintFamily.DATA, now=2)
    assert c.valid is True
    result = service.validate(session.session_id, bp.blueprint_id, now=3)
    assert result.valid is True
    assert service.registry.get(bp.blueprint_id).status is BlueprintStatus.VALIDATED


def test_invalid_blueprint_rejected_with_gap_report_and_stays_out_of_catalog():
    auth, workspaces, service = _fixture()
    session, bp = _authored(auth, workspaces, service)
    service.classify(
        session.session_id, bp.blueprint_id, BlueprintFamily.DATA, now=2, defects=("bad-schema",)
    )
    with pytest.raises(BlueprintValidationError):
        service.validate(session.session_id, bp.blueprint_id, now=3)
    # remains DRAFT, never cataloged (P4)
    assert service.registry.get(bp.blueprint_id).status is BlueprintStatus.DRAFT
    assert bp.blueprint_id not in service.catalog


def test_classify_denied_without_authoring_grant():
    auth, workspaces, service = _fixture()
    _, bp = _authored(auth, workspaces, service)
    op = _session(auth, Role.OPERATOR, subject="op@x")
    with pytest.raises(BlueprintAccessError):
        service.classify(op.session_id, bp.blueprint_id, BlueprintFamily.DATA, now=2)


# --------------------------------------------------------------------------- #
# Catalog (link-4)                                                             #
# --------------------------------------------------------------------------- #


def test_catalog_requires_provenance_and_links_traceability():
    events = bootstrap_platform().events
    auth, workspaces, service = _fixture(events=events)
    session, bp = _authored(auth, workspaces, service)
    service.classify(session.session_id, bp.blueprint_id, BlueprintFamily.DATA, now=2)
    service.validate(session.session_id, bp.blueprint_id, now=3)
    entry = service.catalog_blueprint(
        session.session_id, bp.blueprint_id, _provenance(bp.blueprint_id), now=4
    )
    assert entry.is_traceable is True
    assert service.registry.get(bp.blueprint_id).status is BlueprintStatus.CATALOGUED
    assert len(events.events_of(BLUEPRINT_CATALOGUED_EVENT)) == 1
    assert len(events.events_of(BLUEPRINT_TRACEABILITY_LINKED_EVENT)) == 1


def test_catalog_rejects_non_provenance_and_mismatched_ref():
    auth, workspaces, service = _fixture()
    session, bp = _authored(auth, workspaces, service)
    service.classify(session.session_id, bp.blueprint_id, BlueprintFamily.DATA, now=2)
    service.validate(session.session_id, bp.blueprint_id, now=3)
    with pytest.raises(BlueprintServiceError):
        service.catalog_blueprint(session.session_id, bp.blueprint_id, "nope", now=4)  # type: ignore[arg-type]
    with pytest.raises(BlueprintProvenanceError):
        service.catalog_blueprint(
            session.session_id, bp.blueprint_id, _provenance("UCOS-BLPR-other"), now=4
        )


def test_catalog_denied_for_developer_without_catalog_create():
    # Developer has authoring CREATE but only READ on blueprint-catalog.
    auth, workspaces, service = _fixture()
    ws = _workspace(workspaces)
    dev = _session(auth, Role.DEVELOPER, subject="dev@x")
    bp = service.author_blueprint(
        dev.session_id, "bp", "BP", ws.workspace_id, BlueprintFamily.DATA, now=1
    )
    service.classify(dev.session_id, bp.blueprint_id, BlueprintFamily.DATA, now=2)
    service.validate(dev.session_id, bp.blueprint_id, now=3)
    with pytest.raises(BlueprintAccessError):
        service.catalog_blueprint(
            dev.session_id, bp.blueprint_id, _provenance(bp.blueprint_id), now=4
        )


# --------------------------------------------------------------------------- #
# Versioning / supersession / retirement / metadata                           #
# --------------------------------------------------------------------------- #


def test_version_supersede_retire_flow():
    auth, workspaces, service = _fixture()
    session, bp = _catalogued(auth, workspaces, service)
    v1 = service.version(session.session_id, bp.blueprint_id, "h1", now=5)
    v2 = service.version(session.session_id, bp.blueprint_id, "h2", now=6)
    assert (v1.revision, v2.revision) == (1, 2)
    superseded = service.supersede(session.session_id, bp.blueprint_id, now=7)
    assert superseded.status is BlueprintStatus.SUPERSEDED
    retired = service.retire(session.session_id, bp.blueprint_id, now=8)
    assert retired.status is BlueprintStatus.RETIRED


def test_update_metadata_requires_authoring():
    auth, workspaces, service = _fixture()
    session, bp = _authored(auth, workspaces, service)
    from platform.blueprints.metadata import BlueprintMetadata

    updated = service.update_metadata(
        session.session_id, bp.blueprint_id, BlueprintMetadata.create(description="d"), now=2
    )
    assert updated.metadata.description == "d"
    with pytest.raises(BlueprintServiceError):
        service.update_metadata(session.session_id, bp.blueprint_id, "nope", now=3)  # type: ignore[arg-type]


def test_mutation_denied_on_retired_blueprint():
    auth, workspaces, service = _fixture()
    session, bp = _catalogued(auth, workspaces, service)
    service.retire(session.session_id, bp.blueprint_id, now=5)
    access = service.evaluate_access(
        session.session_id, bp.blueprint_id, BlueprintAction.VERSION, now=6
    )
    assert access.granted is False
    assert access.reason == "blueprint-retired"


# --------------------------------------------------------------------------- #
# Associations                                                                 #
# --------------------------------------------------------------------------- #


def test_associate_and_dissociate():
    auth, workspaces, service = _fixture()
    session, bp = _catalogued(auth, workspaces, service)
    assoc = service.associate(
        session.session_id,
        bp.blueprint_id,
        BlueprintAssociationKind.GENERATION_ARTIFACT,
        "BP-DATA-0001",
        now=5,
    )
    assert assoc.ref_id == "BP-DATA-0001"
    removed = service.dissociate(
        session.session_id,
        bp.blueprint_id,
        BlueprintAssociationKind.GENERATION_ARTIFACT,
        "BP-DATA-0001",
        now=6,
    )
    assert removed.ref_id == "BP-DATA-0001"


# --------------------------------------------------------------------------- #
# Access composition (identity ∧ isolation ∧ owner/admin)                      #
# --------------------------------------------------------------------------- #


def test_access_granted_for_owner_inspect_and_emits_event():
    events = bootstrap_platform().events
    auth, workspaces, service = _fixture(events=events)
    session, bp = _authored(auth, workspaces, service)
    access = service.evaluate_access(
        session.session_id, bp.blueprint_id, BlueprintAction.INSPECT, now=2
    )
    assert access.granted is True
    assert access.is_owner is True
    assert access.access_id.startswith("UCOS-BACC-")
    assert access.to_dict()["granted"] is True
    assert len(events.events_of(BLUEPRINT_ACCESS_EVENT)) == 1


def test_access_denied_authorization_refused():
    auth, workspaces, service = _fixture()
    _, bp = _authored(auth, workspaces, service)
    op = _session(auth, Role.OPERATOR, subject="op@x")
    access = service.evaluate_access(
        op.session_id, bp.blueprint_id, BlueprintAction.CLASSIFY, now=2
    )
    assert access.granted is False
    assert access.reason == "no-grant"


def test_access_denied_cross_tenant_isolation():
    auth, workspaces, service = _fixture()
    _, bp = _authored(auth, workspaces, service, subject="arch@x", tenant="beta")
    intruder = _session(auth, Role.ARCHITECT, subject="x@x", tenant="acme")
    access = service.evaluate_access(
        intruder.session_id, bp.blueprint_id, BlueprintAction.INSPECT, now=2
    )
    assert access.granted is False
    assert access.reason == "tenant-isolation-violation"


def test_access_denied_not_owner_for_mutation():
    auth, workspaces, service = _fixture()
    _, bp = _authored(auth, workspaces, service, subject="arch@x")
    other = _session(auth, Role.ARCHITECT, subject="other@x")  # has CREATE, not owner
    access = service.evaluate_access(
        other.session_id, bp.blueprint_id, BlueprintAction.CLASSIFY, now=2
    )
    assert access.granted is False
    assert access.reason == "not-an-owner"


def test_access_administrator_override_for_mutation():
    # Build a custom RBAC matrix that grants ADMINISTER on blueprint-authoring so the
    # administrator-override branch (mutation without ownership) is exercised.
    definitions = [
        d for d in default_role_definitions() if d.role is not Role.PLATFORM_ADMINISTRATOR
    ]
    admin_grants = {
        CapabilityGroup.BLUEPRINT_AUTHORING: RoleGrant(
            group=CapabilityGroup.BLUEPRINT_AUTHORING,
            permissions=frozenset({Permission.CREATE, Permission.READ, Permission.ADMINISTER}),
        ),
        CapabilityGroup.BLUEPRINT_CATALOG: RoleGrant(
            group=CapabilityGroup.BLUEPRINT_CATALOG,
            permissions=frozenset({Permission.CREATE, Permission.READ, Permission.ADMINISTER}),
        ),
        CapabilityGroup.WORKSPACE_PROJECT_LIFECYCLE: RoleGrant(
            group=CapabilityGroup.WORKSPACE_PROJECT_LIFECYCLE,
            permissions=frozenset({Permission.CREATE, Permission.READ, Permission.ADMINISTER}),
        ),
    }
    definitions.append(RoleDefinition(role=Role.PLATFORM_ADMINISTRATOR, grants=admin_grants))
    roles = RoleRegistry()
    roles.register_all(definitions)
    auth = build_authorization_service(roles=roles)
    _, workspaces, service = _fixture(authorization=auth)
    _, bp = _authored(auth, workspaces, service, subject="arch@x")
    admin = _session(auth, Role.PLATFORM_ADMINISTRATOR, subject="admin@x")
    access = service.evaluate_access(
        admin.session_id, bp.blueprint_id, BlueprintAction.CLASSIFY, now=2
    )
    assert access.granted is True
    assert access.is_owner is False


def test_evaluate_access_rejects_bad_action_and_unknown_blueprint():
    auth, workspaces, service = _fixture()
    session, bp = _authored(auth, workspaces, service)
    with pytest.raises(BlueprintServiceError):
        service.evaluate_access(session.session_id, bp.blueprint_id, "inspect", now=2)  # type: ignore[arg-type]
    with pytest.raises(Exception):  # noqa: B017 - registry error
        service.evaluate_access(
            session.session_id, "UCOS-BLPR-missing", BlueprintAction.INSPECT, now=2
        )


# --------------------------------------------------------------------------- #
# Selection / discovery / trace / status / search                             #
# --------------------------------------------------------------------------- #


def test_select_blueprint_returns_context():
    auth, workspaces, service = _fixture()
    session, bp = _catalogued(auth, workspaces, service)
    ctx = service.select_blueprint(session.session_id, bp.blueprint_id, now=5)
    assert ctx.blueprint_id == bp.blueprint_id
    assert ctx.is_owner is True
    assert ctx.is_catalogued is True


def test_select_denied_cross_tenant():
    auth, workspaces, service = _fixture()
    _, bp = _authored(auth, workspaces, service, subject="arch@x", tenant="beta")
    intruder = _session(auth, Role.ARCHITECT, subject="x@x", tenant="acme")
    with pytest.raises(BlueprintAccessError):
        service.select_blueprint(intruder.session_id, bp.blueprint_id, now=2)


def test_resolve_and_discover():
    auth, workspaces, service = _fixture()
    session, bp = _authored(auth, workspaces, service, tenant="acme")
    assert service.resolve("bp-1", bp.workspace_id).blueprint_id == bp.blueprint_id
    seen = service.discover(session.session_id, now=2, tenant="acme")
    assert bp.blueprint_id in {b.blueprint_id for b in seen}


def test_discover_empty_for_invalid_session_and_unauthorized():
    auth, _, service = _fixture()
    assert service.discover("UCOS-SESS-missing", now=1) == ()
    op = _session(auth, Role.OPERATOR, subject="op@x")
    assert service.discover(op.session_id, now=1) == ()


def test_trace_returns_link4_edge():
    auth, workspaces, service = _fixture()
    session, bp = _catalogued(auth, workspaces, service)
    edge = service.trace(session.session_id, bp.blueprint_id, now=5)
    assert edge["link"] == "GOV-002-link-4"
    assert edge["traceable"] is True


def test_trace_denied_cross_tenant():
    auth, workspaces, service = _fixture()
    session, bp = _catalogued(auth, workspaces, service, subject="arch@x", tenant="beta")
    intruder = _session(auth, Role.ARCHITECT, subject="x@x", tenant="acme")
    with pytest.raises(BlueprintAccessError):
        service.trace(intruder.session_id, bp.blueprint_id, now=9)


def test_status_of_reflects_lifecycle_and_provenance():
    auth, workspaces, service = _fixture()
    session, bp = _authored(auth, workspaces, service)
    assert service.status_of(bp.blueprint_id).posture.value == "draft"
    session2, bp2 = _catalogued(auth, workspaces, service, slug="bp-2")
    st = service.status_of(bp2.blueprint_id)
    assert st.posture.value == "catalogued"
    assert st.is_traceable is True


def test_search_delegates():
    auth, workspaces, service = _fixture()
    session, bp = _authored(auth, workspaces, service)
    resp = service.search(session.session_id, "bp", now=2)
    assert resp.authorized is True


# --------------------------------------------------------------------------- #
# Health / evidence / summary                                                  #
# --------------------------------------------------------------------------- #


def test_health_report_and_evidence_deterministic():
    def run() -> str:
        auth, workspaces, service = _fixture()
        _catalogued(auth, workspaces, service)
        return service.evidence().fingerprint()

    assert run() == run()
    auth, workspaces, service = _fixture()
    _catalogued(auth, workspaces, service)
    report = service.health_report()
    assert report["healthy"] is True
    evidence = service.evidence()
    assert evidence.blueprint_count == 1
    assert evidence.catalogued_count == 1
    assert evidence.provenance_count == 1
    assert evidence.evidence_id.startswith("UCOS-BEVT-")
    assert evidence.health_status in {"healthy", "degraded", "unhealthy"}


def test_health_changed_event_emitted_when_status_changes():
    from platform.blueprints.service import BLUEPRINT_HEALTH_CHANGED_EVENT

    events = bootstrap_platform().events
    auth, workspaces, service = _fixture(events=events)
    session, bp = _catalogued(auth, workspaces, service)  # healthy baseline
    # Induce an integrity fault directly on the shared registry the health probe reads:
    # a second blueprint promoted to CATALOGUED without provenance is uncited (unhealthy).
    bp2 = service.registry.create("bp-x", "X", bp.workspace_id, "arch@x", BlueprintFamily.DATA)
    service.registry.transition(bp2.blueprint_id, BlueprintStatus.VALIDATED, tick=5)
    service.registry.transition(bp2.blueprint_id, BlueprintStatus.CATALOGUED, tick=6)
    # A governed mutation now re-probes health and emits health.changed (healthy → unhealthy).
    service.retire(session.session_id, bp.blueprint_id, now=7)
    assert len(events.events_of(BLUEPRINT_HEALTH_CHANGED_EVENT)) == 1


def test_to_dict_summary_reports_observability_binding():
    events = bootstrap_platform().events
    observability = build_observability_service(events=events)
    auth, workspaces, service = _fixture(events=events, observability=observability)
    _catalogued(auth, workspaces, service)
    summary = service.to_dict()
    assert summary["blueprint_count"] == 1
    assert summary["observability_bound"] is True
    assert service.observability is observability
