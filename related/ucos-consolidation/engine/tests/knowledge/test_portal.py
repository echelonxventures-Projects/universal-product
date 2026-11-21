"""Tests for the EPIC-DOC-002 Universal Constitutional Knowledge Portal."""

from __future__ import annotations

from engine.knowledge.intelligence import KnowledgeIntelligence
from engine.knowledge.portal import (
    ARCHITECTURE_PORTAL,
    CAPABILITY_PORTAL,
    CERTIFICATION_PORTAL,
    COVERAGE_PORTAL,
    DEPENDENCY_PORTAL,
    EPIC_PORTAL,
    EXECUTION_PORTAL,
    GOVERNANCE_PORTAL,
    IMPLEMENTATION_PORTAL,
    PORTAL_INDEX,
    PORTALS,
    REPOSITORY_PORTAL,
    SEARCH_PORTAL,
    TRACEABILITY_PORTAL,
    UNIVERSE_PORTAL,
    VALIDATION_PORTAL,
    VISUALIZATION_PORTAL,
    KnowledgePortal,
)
from engine.knowledge.store import KnowledgeBase

from .conftest import make_cko

_ALL_PAGES = {
    PORTAL_INDEX,
    ARCHITECTURE_PORTAL,
    CAPABILITY_PORTAL,
    UNIVERSE_PORTAL,
    EPIC_PORTAL,
    IMPLEMENTATION_PORTAL,
    VALIDATION_PORTAL,
    CERTIFICATION_PORTAL,
    TRACEABILITY_PORTAL,
    REPOSITORY_PORTAL,
    DEPENDENCY_PORTAL,
    EXECUTION_PORTAL,
    COVERAGE_PORTAL,
    GOVERNANCE_PORTAL,
    SEARCH_PORTAL,
    VISUALIZATION_PORTAL,
}


# -- structure ----------------------------------------------------------------


def test_render_all_keys(seed_base):
    rendered = KnowledgePortal(seed_base).render_all()
    assert set(rendered) == _ALL_PAGES
    # 15 portals plus the navigable home.
    assert len(PORTALS) == 15
    assert len(rendered) == 16


def test_every_page_is_navigable_and_generated(seed_base):
    rendered = KnowledgePortal(seed_base).render_all()
    for filename, content in rendered.items():
        # generated banner (never hand-authored) and the portal marker.
        assert "GENERATED CONSTITUTIONAL KNOWLEDGE PORTAL" in content
        assert "EPIC-DOC-002" in content
        # every page carries a navigation bar linking every sibling portal.
        assert "**Portals:**" in content
        for other, title, _ in PORTALS:
            if other == filename:
                assert f"**{title}**" in content
            else:
                assert f"[{title}]({other})" in content
        # non-home pages link back to the home; home links out to all portals.
        if filename != PORTAL_INDEX:
            assert f"[Home]({PORTAL_INDEX})" in content
        else:
            assert "**Home**" in content


def test_index_lists_every_portal(seed_base):
    index = KnowledgePortal(seed_base).index()
    for filename, title, purpose in PORTALS:
        assert f"[{title}]({filename})" in index
        assert purpose in index
    assert "Canonical state" in index


# -- content projections ------------------------------------------------------


def test_portals_project_seed_knowledge(seed_base):
    rendered = KnowledgePortal(seed_base).render_all()

    # Architecture projects ratified principles.
    assert "Knowledge Once Principle" in rendered[ARCHITECTURE_PORTAL]

    # Capability = DECISION objects, with constitutional origin.
    capability = rendered[CAPABILITY_PORTAL]
    assert "UCKO-DEC-0001" in capability
    assert "UKDA-DEC-0001" in capability  # linked decision record
    assert "UCKO-PRIN-0001" in capability  # constitutional origin

    # Universe groups by the universe field.
    universe = rendered[UNIVERSE_PORTAL]
    assert "Universe: GOVERNANCE" in universe
    assert "Universe: ARCHITECTURE" in universe

    # EPIC groups by decision record.
    assert "UKDA-DEC-0001" in rendered[EPIC_PORTAL]

    # Implementation surfaces operational objects.
    assert "UCKO-STD-0001" in rendered[IMPLEMENTATION_PORTAL]

    # Traceability exposes the constitutional chain.
    trace = rendered[TRACEABILITY_PORTAL]
    assert "Constitutional chains" in trace
    assert "UCKO-PRIN-0001" in trace

    # Repository maps owners.
    assert "UCOS-ARCHITECTURE-BOARD" in rendered[REPOSITORY_PORTAL]

    # Execution shows the constitutional execution path.
    execution = rendered[EXECUTION_PORTAL]
    assert "Constitutional execution path" in execution
    assert "UKI-LAW-" in execution

    # Governance grounding table.
    assert "Governance grounding" in rendered[GOVERNANCE_PORTAL]

    # Visualization is a Mermaid diagram.
    assert "```mermaid" in rendered[VISUALIZATION_PORTAL]


def test_validation_and_certification_portals_reflect_the_gates(seed_base):
    rendered = KnowledgePortal(seed_base).render_all()
    # The seed base is designed to validate and certify cleanly.
    assert "accepted" in rendered[VALIDATION_PORTAL]
    assert "no-duplicate-knowledge" in rendered[VALIDATION_PORTAL]
    certification = rendered[CERTIFICATION_PORTAL]
    assert "certified" in certification
    assert "ENGINEERING-EXECUTION-ONLY" in certification


def test_coverage_portal_reports_distribution(seed_base):
    coverage = KnowledgePortal(seed_base).coverage()
    assert "Total objects" in coverage
    assert "Distribution" in coverage
    assert "Gaps" in coverage


def test_search_portal_builds_a_working_inverted_index(seed_base):
    search = KnowledgePortal(seed_base).search()
    assert "Inverted index" in search
    assert "Object terms" in search
    # A term from the founding principle maps back to its object.
    assert "knowledge" in search
    assert "UCKO-PRIN-0001" in search


def test_document_terms_are_sorted_and_unique(seed_base):
    intel = KnowledgeIntelligence(seed_base)
    obj = seed_base.require_object("UCKO-PRIN-0001")
    terms = intel.document_terms(obj)
    assert terms == tuple(sorted(set(terms)))
    assert "knowledge" in terms


# -- determinism --------------------------------------------------------------


def test_write_all_is_deterministic(seed_base, tmp_path):
    portal = KnowledgePortal(seed_base)
    first = portal.write_all(tmp_path / "a")
    portal.write_all(tmp_path / "b")
    assert len(first) == 16
    for filename in _ALL_PAGES:
        assert (tmp_path / "a" / filename).read_text() == (tmp_path / "b" / filename).read_text()


def test_render_is_pure(seed_base):
    portal = KnowledgePortal(seed_base)
    assert portal.render_all() == portal.render_all()


# -- empty base (graceful placeholders) ---------------------------------------


def test_empty_base_renders_placeholders():
    rendered = KnowledgePortal(KnowledgeBase([])).render_all()
    assert set(rendered) == _ALL_PAGES
    assert "_No capabilities recorded yet._" in rendered[CAPABILITY_PORTAL]
    assert "_No universes recorded yet._" in rendered[UNIVERSE_PORTAL]
    assert "_No decision records recorded yet._" in rendered[EPIC_PORTAL]
    assert (
        "_No implemented or operational knowledge recorded yet._"
        in (rendered[IMPLEMENTATION_PORTAL])
    )
    assert "No governance objects recorded yet" in rendered[GOVERNANCE_PORTAL]
    assert "No canonical objects recorded yet" in rendered[TRACEABILITY_PORTAL]
    assert "No canonical objects to index yet" in rendered[SEARCH_PORTAL]


def test_repository_ownership_overlap_is_surfaced():
    # Two active objects expressing identical knowledge under different owners.
    base = KnowledgeBase(
        [
            make_cko("A1", statement="identical knowledge.", owner="OWNER-X"),
            make_cko("A2", statement="identical knowledge.", owner="OWNER-Y"),
        ]
    )
    repository = KnowledgePortal(base).repository()
    assert "OWNER-X" in repository
    assert "OWNER-Y" in repository


def test_doc_body_falls_back_when_no_heading():
    # Defensive path: a body with no H1 is returned verbatim.
    lines = KnowledgePortal._doc_body("plain text\nno heading here")
    assert lines == ["plain text", "no heading here"]
