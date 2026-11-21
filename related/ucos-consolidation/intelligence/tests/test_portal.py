"""EPIC-DOC-003 (Terminal T4) — Repository Intelligence Portal tests.

Proves the mission's constitutional requirements for the portal:
  * everything generated — no page is hand-authored (every page carries the banner)
  * everything linked   — every page carries a nav bar linking every sibling page
  * everything traceable — every page cites its evidence fingerprint + derivation
  * everything searchable — a working deterministic inverted index exists
  * 100% deterministic  — identical repository state ⇒ byte-identical pages
  * reuse, not rebuild  — the T3 acceptance engine is reused verbatim over a subject
                          assimilated from the RIE model (nothing re-derived)

Run: .ec1-venv/bin/python -m pytest intelligence/tests -q
"""

from __future__ import annotations

import copy
from dataclasses import replace

import pytest

from intelligence.portal import (
    ACCEPTANCE_PORTAL,
    CAPABILITY_PORTAL,
    CERTIFICATION_PORTAL,
    COVERAGE_PORTAL,
    DEPENDENCY_PORTAL,
    DRIFT_PORTAL,
    EVIDENCE_PORTAL,
    EXECUTION_PORTAL,
    FREEZE_PORTAL,
    FRONTIER_PORTAL,
    HEALTH_PORTAL,
    PAGES,
    PORTAL_INDEX,
    READINESS_PORTAL,
    SEARCH_PORTAL,
    VALIDATION_PORTAL,
    WORKSTREAMS_PORTAL,
    RepositoryIntelligencePortal,
    _freeze_blockers,
    build_acceptance_facts,
)
from intelligence.portal import (
    main as portal_main,
)
from intelligence.rie.config import RepoConfig
from intelligence.rie.engine import RepositoryIntelligenceEngine

REPO = RepoConfig.create().repo_root

_ALL_PAGES = {
    PORTAL_INDEX,
    HEALTH_PORTAL,
    READINESS_PORTAL,
    EXECUTION_PORTAL,
    ACCEPTANCE_PORTAL,
    VALIDATION_PORTAL,
    CERTIFICATION_PORTAL,
    FRONTIER_PORTAL,
    WORKSTREAMS_PORTAL,
    DRIFT_PORTAL,
    COVERAGE_PORTAL,
    FREEZE_PORTAL,
    CAPABILITY_PORTAL,
    DEPENDENCY_PORTAL,
    SEARCH_PORTAL,
    EVIDENCE_PORTAL,
}


def _portal() -> RepositoryIntelligencePortal:
    return RepositoryIntelligencePortal(RepositoryIntelligenceEngine(RepoConfig.create(REPO)))


@pytest.fixture(scope="module")
def portal() -> RepositoryIntelligencePortal:
    return _portal()


@pytest.fixture(scope="module")
def rendered(portal: RepositoryIntelligencePortal) -> dict[str, str]:
    return portal.render_all()


# -- structure ----------------------------------------------------------------


def test_render_all_keys(rendered: dict[str, str]) -> None:
    assert set(rendered) == _ALL_PAGES
    # 15 objective/supporting pages plus the navigable home.
    assert len(PAGES) == 15
    assert len(rendered) == 16


def test_page_titles_are_unique() -> None:
    titles = [title for _, title, _ in PAGES]
    assert len(titles) == len(set(titles))


def test_every_page_is_generated_navigable_and_traceable(rendered: dict[str, str]) -> None:
    for filename, content in rendered.items():
        # generated banner (never hand-authored) + the epic marker.
        assert "GENERATED REPOSITORY INTELLIGENCE PORTAL" in content
        assert "EPIC-DOC-003" in content
        # every page carries a navigation bar linking every sibling page.
        assert "**Intelligence:**" in content
        for other, title, _ in PAGES:
            if other == filename:
                assert f"**{title}**" in content
            else:
                assert f"[{title}]({other})" in content
        # non-home pages link home; home links out to every page.
        if filename != PORTAL_INDEX:
            assert f"[Home]({PORTAL_INDEX})" in content
        else:
            assert "**Home**" in content
        # traceable: every page carries the evidence fingerprint + non-authority.
        assert "Evidence:" in content
        assert "content-hash" in content
        assert "NONE (derived truth)" in content
        # linked to the sibling constitutional knowledge portal (EPIC-DOC-002).
        assert "Constitutional Knowledge Portal" in content


def test_index_lists_every_page(portal: RepositoryIntelligencePortal) -> None:
    index = portal.index()
    for filename, title, purpose in PAGES:
        assert f"[{title}]({filename})" in index
        assert purpose in index
    assert "Repository posture" in index


# -- objective coverage (the eleven mission objectives) -----------------------


def test_pages_project_every_mission_objective(rendered: dict[str, str]) -> None:
    # Repository Health
    assert "Overall" in rendered[HEALTH_PORTAL]
    assert "Knowledge-graph edges" in rendered[HEALTH_PORTAL]
    # Repository Readiness (T3 + AEOS)
    assert "freeze readiness" in rendered[READINESS_PORTAL].lower()
    assert "AEOS foundation readiness" in rendered[READINESS_PORTAL]
    # Execution Status
    assert "Per-dimension execution status" in rendered[EXECUTION_PORTAL]
    assert "Digital-twin projection" in rendered[EXECUTION_PORTAL]
    # Acceptance Status
    assert "Gate findings" in rendered[ACCEPTANCE_PORTAL]
    assert "UCOS-ACCEPT-EPIC-DOC-003" in rendered[ACCEPTANCE_PORTAL]
    # Validation Status
    assert "Unit validation" in rendered[VALIDATION_PORTAL]
    # Certification Status
    assert "Digital-twin verdict" in rendered[CERTIFICATION_PORTAL]
    # Implementation Frontier
    assert "Next executable capability" in rendered[FRONTIER_PORTAL]
    assert "Critical path" in rendered[FRONTIER_PORTAL]
    # Active Workstreams
    assert "Single active frontier" in rendered[WORKSTREAMS_PORTAL]
    # Repository Drift
    assert "Duplicate findings" in rendered[DRIFT_PORTAL]
    assert "Stale evidence" in rendered[DRIFT_PORTAL]
    # Coverage
    assert "Line coverage" in rendered[COVERAGE_PORTAL]
    assert "Per-root census" in rendered[COVERAGE_PORTAL]
    # Architecture Freeze Readiness
    assert "Freeze verdict" in rendered[FREEZE_PORTAL]
    assert "Known spine gaps" in rendered[FREEZE_PORTAL]


def test_supporting_pages_project_their_source(rendered: dict[str, str]) -> None:
    assert "reuse policy" in rendered[CAPABILITY_PORTAL]
    assert "```mermaid" in rendered[DEPENDENCY_PORTAL]
    assert "Layered architecture" in rendered[DEPENDENCY_PORTAL]
    assert "Inverted index" in rendered[SEARCH_PORTAL]
    assert "Evidence files" in rendered[EVIDENCE_PORTAL]


# -- reuse of the T3 acceptance engine (not rebuilt) --------------------------


def test_acceptance_is_reused_verbatim(portal: RepositoryIntelligencePortal) -> None:
    decision = portal.decision
    readiness = portal.acceptance_readiness
    # The decision is the genuine T3 fail-closed decision over 20 built-in gates.
    assert decision.counts()["total"] == 20
    assert decision.record.verify_integrity() is True
    # Readiness is derived from the same decision (single source of the verdict).
    assert readiness.gates_total == decision.counts()["total"]
    assert readiness.accepted == decision.accepted
    # The freeze verdict is fail-closed: ready iff accepted.
    assert (readiness.verdict == "READY") == decision.accepted


def test_acceptance_facts_are_derived_and_deterministic() -> None:
    engine = RepositoryIntelligenceEngine(RepoConfig.create(REPO))
    outputs = engine.outputs()
    model = {**outputs["UCOS-RIE-MODEL.json"], "_drift": outputs["UCOS-RIE-SNAPSHOT.json"]["drift"]}
    a = build_acceptance_facts(model, "REPO")
    b = build_acceptance_facts(model, "REPO")
    assert a == b
    # Derived, not hand-listed: units come from the discovered capabilities.
    assert a["repository_id"] == "REPO"
    assert a["epic_id"] == "EPIC-DOC-003"
    assert len(a["units"]) > 0
    # Freeze blockers surface the AEOS spine gaps (derived from the model).
    assert any("not implemented" in b for b in a["freeze_blockers"])


# -- searchable ---------------------------------------------------------------


def test_search_index_maps_terms_back_to_documents(portal: RepositoryIntelligencePortal) -> None:
    search = portal.search()
    assert "Inverted index" in search
    # A capability id is a document; a gate id is a document; both are indexed.
    assert "gate:" in search
    # An engine capability term resolves in the index.
    assert "engine" in search


# -- determinism --------------------------------------------------------------


def test_render_is_pure(portal: RepositoryIntelligencePortal) -> None:
    assert portal.render_all() == portal.render_all()


def test_two_portals_render_byte_identical() -> None:
    first = _portal().render_all()
    second = _portal().render_all()
    assert first.keys() == second.keys()
    for filename in first:
        assert first[filename] == second[filename], f"non-deterministic page: {filename}"


def test_write_all_is_deterministic(tmp_path) -> None:
    portal = _portal()
    a = portal.write_all(tmp_path / "a")
    portal.write_all(tmp_path / "b")
    assert len(a) == 16
    for filename in _ALL_PAGES:
        assert (tmp_path / "a" / filename).read_text() == (tmp_path / "b" / filename).read_text()


# --------------------------------------------------------------------------- #
# the empty repository — every page's "nothing to report" branch               #
#                                                                             #
# WHY THESE EXIST. Every page above is rendered over THIS repository, which has#
# certified capabilities, blocked dimensions, drift and a critical path. The   #
# branch each page takes when its section is EMPTY was therefore never taken,  #
# and an empty section is exactly the state a page must survive: a portal that #
# renders only when there is something to render is a portal that breaks on the#
# day the news is good.                                                        #
# --------------------------------------------------------------------------- #


def _emptied(portal: RepositoryIntelligencePortal) -> RepositoryIntelligencePortal:
    """The same portal over a model that reports nothing.

    The model is replaced rather than the engine stubbed, because the pages under test
    are a projection of the model and nothing else — which is the property the portal
    claims for itself ("zero re-derivation").
    """
    empty = RepositoryIntelligencePortal.__new__(RepositoryIntelligencePortal)
    empty._engine = portal._engine
    empty._repo_id = portal._repo_id
    empty._outputs = portal._outputs
    empty._model = {}
    empty._drift = {}
    empty._decision = portal._decision
    empty._readiness = portal._readiness
    return empty


def test_every_page_renders_over_a_model_that_reports_nothing(portal) -> None:
    pages = _emptied(portal).render_all()
    assert set(pages) == _ALL_PAGES
    for filename, content in pages.items():
        assert content.strip(), filename
        assert "GENERATED REPOSITORY INTELLIGENCE PORTAL" in content


def test_the_empty_pages_say_so_rather_than_rendering_an_empty_table(portal) -> None:
    pages = _emptied(portal).render_all()
    assert "| _none_ | — | — |" in pages[CERTIFICATION_PORTAL]
    assert "_Nothing blocked._" in pages[FRONTIER_PORTAL]
    assert "_No critical path derived._" in pages[FRONTIER_PORTAL]


def test_a_validation_dimension_the_model_does_not_carry_is_skipped(portal) -> None:
    """The page iterates the dimension NAMES it declares and reads each from the model;
    a name the model has no entry for is skipped rather than rendered as a blank row."""
    partial = _emptied(portal)
    partial._model = {"progress": {"per_dimension": {}}}
    assert "| None |" not in partial.validation()


def test_constitutional_finality_that_is_blocked_is_reported_as_a_freeze_blocker() -> None:
    blockers = _freeze_blockers(
        {},
        [],
        {"constitutional_finality": "BLOCKED — three gaps remain"},
        {},
    )
    assert blockers == ["constitutional finality BLOCKED — three gaps remain"]


def test_finality_that_is_not_blocked_contributes_no_freeze_blocker() -> None:
    assert _freeze_blockers({}, [], {"constitutional_finality": "ACHIEVED"}, {}) == []
    assert _freeze_blockers({}, [], {}, {}) == []


# --------------------------------------------------------------------------- #
# the CLI                                                                      #
# --------------------------------------------------------------------------- #


def test_cli_writes_every_page_into_the_directory_it_was_given(tmp_path, capsys) -> None:
    out = tmp_path / "portal"
    assert portal_main(["--repo", str(REPO), "--out", str(out)]) == 0
    written = {path.name for path in out.iterdir()}
    assert written == _ALL_PAGES
    printed = capsys.readouterr().out
    assert f"generated {len(_ALL_PAGES)} pages" in printed
    assert PORTAL_INDEX in printed


def test_cli_defaults_the_output_directory_under_the_engine_output_root(
    tmp_path, capsys, monkeypatch
) -> None:
    """The default is derived from the engine's configured output directory, so pointing
    the repository elsewhere moves the pages with it and never writes into this tree."""
    engine = RepositoryIntelligenceEngine(RepoConfig.create(REPO))
    monkeypatch.setattr(
        "intelligence.portal.RepoConfig",
        type(
            "_Redirected",
            (),
            {
                "create": staticmethod(
                    lambda root=None: replace(engine.config, output_dir=tmp_path / "out")
                )
            },
        ),
    )
    assert portal_main(["--repo", str(REPO)]) == 0
    assert (tmp_path / "out" / "portal" / PORTAL_INDEX).is_file()
    capsys.readouterr()


def test_the_search_page_renders_an_explicit_empty_index(monkeypatch) -> None:
    """An empty corpus is stated in the table, not silently rendered as a blank section.

    The inverted index is built from the documents the portal can read; with none, the page
    must say `_empty_` rather than show a header over nothing — the difference between a
    measured absence and an unrendered one.
    """
    portal = _portal()
    monkeypatch.setattr(type(portal), "_search_documents", lambda self: [])
    page = portal.search()
    assert "_empty_" in page


def test_a_validation_dimension_missing_from_the_projection_is_skipped_not_rendered() -> None:
    """`per_dimension` is published data, not a contract with four keys.

    A projection that has not yet evaluated a dimension must be skipped, and the page
    must not present the absence as a verdict — while the gate finding, absent from the
    decision, must leave its section out too.
    """
    portal = _portal()
    model = copy.deepcopy(portal._model)
    model["progress"] = {
        "unit_validation_pct": 50,
        "per_dimension": {
            "unit_testing": {
                "status": "GREEN",
                "source": "fixture",
                "stale": False,
                "reconciled_score": 1.0,
            }
        },
    }
    lean = replace(
        portal._decision,
        findings=tuple(fl for fl in portal._decision.findings if fl.gate_id != "validation-passed"),
    )
    original_model, original_decision = portal._model, portal._decision
    try:
        object.__setattr__(portal, "_model", model)
        object.__setattr__(portal, "_decision", lean)
        page = portal.validation()
    finally:
        object.__setattr__(portal, "_model", original_model)
        object.__setattr__(portal, "_decision", original_decision)
    assert "integration_testing" not in page
    assert "| unit_testing |" in page
    assert "Acceptance validation gate" not in page


def test_a_full_validation_projection_renders_every_dimension() -> None:
    """The other side of the same loop: every named dimension that is present is a row.

    The skip arm only means anything against the render arm — one projection with all
    four dimensions must produce all four rows, so the walk is shown to include as well
    as to omit.
    """
    portal = _portal()
    model = copy.deepcopy(portal._model)
    model["progress"] = {
        "unit_validation_pct": 100,
        "per_dimension": {
            name: {
                "status": "GREEN",
                "source": "fixture",
                "stale": False,
                "reconciled_score": 1.0,
            }
            for name in (
                "unit_testing",
                "integration_testing",
                "functional_testing",
                "performance_testing",
            )
        },
    }
    original = portal._model
    try:
        object.__setattr__(portal, "_model", model)
        page = portal.validation()
    finally:
        object.__setattr__(portal, "_model", original)
    for name in ("unit_testing", "integration_testing", "functional_testing", "performance_testing"):
        assert f"| {name} |" in page
