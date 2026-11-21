"""Governance / invariant tests for the Universal Portal (UCOS-EPIC-008 / T8).

Asserts the Extended Invariant for the T8 layer: additive-only, read/inspection-only,
creates no new authority, consumes only published APIs, and is fail-closed.
"""

from __future__ import annotations

from platform.administration.contracts import ADMINISTRATION_CONTRACTS
from platform.certification.contracts import CERTIFICATION_CONSOLE_CONTRACTS
from platform.coverage.contracts import COVERAGE_CONTRACTS
from platform.foundation.errors import PlatformError
from platform.foundation.identity import Permission
from platform.identity.contracts import all_capability_groups
from platform.portal.contracts import PORTAL_CONTRACTS
from platform.tests.universal_portal_helpers import build_service, session
from platform.universal_portal.contracts import (
    UNIVERSAL_PORTAL_CONTRACTS,
    PortalApplication,
    all_portal_applications,
    application_group,
    consumed_contract_refs,
    required_permission,
)
from platform.universal_portal.errors import UniversalPortalError
from platform.validation.contracts import VALIDATION_CONSOLE_CONTRACTS


def test_all_surfaces_are_read_only():
    for app in all_portal_applications():
        assert required_permission(app) is Permission.READ


def test_portal_creates_no_new_authority():
    known = set(all_capability_groups())
    for app in all_portal_applications():
        assert application_group(app) in known


def test_every_consumed_contract_is_a_published_reference():
    published = {r.name for r in ADMINISTRATION_CONTRACTS}
    published |= {r.name for r in VALIDATION_CONSOLE_CONTRACTS}
    published |= {r.name for r in CERTIFICATION_CONSOLE_CONTRACTS}
    published |= {r.name for r in COVERAGE_CONTRACTS}
    published |= {r.name for r in PORTAL_CONTRACTS}
    published |= {r.name for r in UNIVERSAL_PORTAL_CONTRACTS}
    published |= {"registry.read", "knowledge.ukda"}  # certified engine contracts
    for app in all_portal_applications():
        for ref in consumed_contract_refs(app):
            assert ref.name in published, f"{app}: {ref.name} is not a published contract"


def test_error_taxonomy_is_rooted_in_platform_error():
    assert issubclass(UniversalPortalError, PlatformError)


def test_unauthorized_access_is_fail_closed_across_surfaces():
    from platform.foundation.identity import Role

    auth, service = build_service()
    # A principal with only self/session access holds none of the T8 surface grants.
    sid = session(auth, role=Role.OPERATOR, subject="op@x")
    denied = 0
    for app in PortalApplication:
        view = service.open(sid, app, now=1)
        if not view.authorized:
            assert view.snapshot is None
            denied += 1
    assert denied >= 1  # at least the administration surface is denied to a non-admin


def test_snapshot_is_only_served_when_authorized_and_bound():
    from platform.foundation.identity import Role

    auth, service = build_service(providers={})  # nothing bound but dev/doc
    admin_sid = session(auth, role=Role.PLATFORM_ADMINISTRATOR)
    # Authorized but unbound → available False, no snapshot.
    view = service.measurement(admin_sid, now=1)
    assert view.authorized is True
    assert view.available is False
    assert view.snapshot is None
