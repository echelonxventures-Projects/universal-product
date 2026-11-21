"""Tests for the Universal Portal Documentation Portal (UCOS-EPIC-008 / T8)."""

from __future__ import annotations

from platform.universal_portal.contracts import (
    UNIVERSAL_PORTAL_CONTRACTS,
    PortalApplication,
    all_portal_applications,
)
from platform.universal_portal.documentation import (
    DocumentationIndex,
    DocumentationPage,
    DocumentationPortal,
)
from platform.universal_portal.errors import DocumentationPortalError

import pytest


def test_index_has_a_page_per_application_and_per_contract():
    index = DocumentationPortal().index()
    assert isinstance(index, DocumentationIndex)
    assert index.page_count == len(all_portal_applications()) + len(UNIVERSAL_PORTAL_CONTRACTS)
    assert index.index_id.startswith("UCOS-T8IDX-")
    for app in all_portal_applications():
        assert app.value in index.slugs


def test_index_is_deterministic():
    a = DocumentationPortal().index()
    b = DocumentationPortal().index()
    assert a.fingerprint() == b.fingerprint()


def test_page_resolution_and_content():
    portal = DocumentationPortal()
    page = portal.page("administration-portal")
    assert isinstance(page, DocumentationPage)
    assert page.title == "Administration Portal"
    assert page.references  # consumed contracts
    assert page.page_id.startswith("UCOS-T8DOC-")


def test_page_for_application():
    page = DocumentationPortal().page_for(PortalApplication.VALIDATION_DASHBOARD)
    assert page.slug == "validation-dashboard"


def test_page_unknown_slug_fails_closed():
    with pytest.raises(DocumentationPortalError):
        DocumentationPortal().page("does-not-exist")


def test_page_requires_slug():
    with pytest.raises(DocumentationPortalError):
        DocumentationPortal().page("")


def test_page_for_rejects_bad_input():
    with pytest.raises(DocumentationPortalError):
        DocumentationPortal().page_for("nope")


def test_documentation_page_requires_slug_and_title():
    with pytest.raises(DocumentationPortalError):
        DocumentationPage.create(slug="", title="t", section="s", body="b", references=())
