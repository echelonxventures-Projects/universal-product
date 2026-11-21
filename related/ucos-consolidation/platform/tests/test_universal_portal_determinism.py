"""Determinism tests for the Universal Portal (UCOS-EPIC-008 / T8)."""

from __future__ import annotations

from platform.foundation.bootstrap import bootstrap_platform
from platform.tests.universal_portal_helpers import all_providers, build_service, session
from platform.universal_portal.contracts import PortalApplication
from platform.universal_portal.service import bootstrap_universal_portal


def test_identical_builds_yield_identical_evidence():
    _a1, s1 = build_service(providers=all_providers())
    _a2, s2 = build_service(providers=all_providers())
    assert s1.evidence().fingerprint() == s2.evidence().fingerprint()


def test_identical_call_sequences_yield_identical_evidence():
    a1, s1 = build_service(providers=all_providers())
    a2, s2 = build_service(providers=all_providers())
    for auth, svc in ((a1, s1), (a2, s2)):
        sid = session(auth)
        svc.enter(sid, now=1)
        svc.administration(sid, now=1)
        svc.validation(sid, now=1)
    assert s1.evidence().fingerprint() == s2.evidence().fingerprint()


def test_bootstrap_catalogs_are_reproducible_across_processes():
    s1 = bootstrap_universal_portal(bootstrap_platform())
    s2 = bootstrap_universal_portal(bootstrap_platform())
    assert s1.applications_registry.fingerprint() == s2.applications_registry.fingerprint()
    assert (
        s1.developer_portal.catalog().fingerprint() == s2.developer_portal.catalog().fingerprint()
    )
    assert (
        s1.documentation_portal.index().fingerprint()
        == s2.documentation_portal.index().fingerprint()
    )


def test_view_ids_are_stable_for_equivalent_state():
    a1, s1 = build_service(providers=all_providers())
    a2, s2 = build_service(providers=all_providers())
    v1 = s1.open(session(a1), PortalApplication.MEASUREMENT_DASHBOARD, now=1)
    v2 = s2.open(session(a2), PortalApplication.MEASUREMENT_DASHBOARD, now=1)
    assert v1.view_id == v2.view_id
