"""Tests for docs (Part 07/08), bootstrap (Part 06/14), and the canonical seed."""

from __future__ import annotations

from engine.knowledge.bootstrap import BOOTSTRAP_SECTIONS, build_digest
from engine.knowledge.certification import certify_base
from engine.knowledge.docs import (
    API_HANDBOOK,
    ARCHITECTURE_HANDBOOK,
    DECISION_HANDBOOK,
    DEPENDENCY_REPORT,
    DEVELOPER_HANDBOOK,
    GOVERNANCE_HANDBOOK,
    KNOWLEDGE_GRAPH,
    KNOWLEDGE_INDEX,
    RUNTIME_HANDBOOK,
    TRACEABILITY_REPORT,
    DocumentationEngine,
)
from engine.knowledge.model import KnowledgeKind
from engine.knowledge.seed import build_seed_base
from engine.knowledge.store import KnowledgeBase
from engine.knowledge.validation import validate_base

from .conftest import make_cko, make_decision

# -- docs ---------------------------------------------------------------------


def test_render_all_keys(seed_base):
    rendered = DocumentationEngine(seed_base).render_all()
    assert set(rendered) == {
        ARCHITECTURE_HANDBOOK,
        API_HANDBOOK,
        DECISION_HANDBOOK,
        DEPENDENCY_REPORT,
        DEVELOPER_HANDBOOK,
        GOVERNANCE_HANDBOOK,
        KNOWLEDGE_GRAPH,
        KNOWLEDGE_INDEX,
        RUNTIME_HANDBOOK,
        TRACEABILITY_REPORT,
    }
    assert "Knowledge Once Principle" in rendered[ARCHITECTURE_HANDBOOK]
    assert "UKDA-DEC-0001" in rendered[DECISION_HANDBOOK]
    assert "Anti-patterns" in rendered[DEVELOPER_HANDBOOK]


def test_generated_reports_project_canonical_knowledge(seed_base):
    rendered = DocumentationEngine(seed_base).render_all()

    # API handbook surfaces the contract standards and the consumed surface.
    api = rendered[API_HANDBOOK]
    assert "API & Contract Handbook" in api
    assert "UCKO-STD-0001" in api  # a standard
    assert "Published contract surface" in api
    assert "UCKO-PRIN-0001" in api  # depended on by others -> in the surface

    # Runtime handbook projects operational authorities + enforced rules.
    runtime = rendered[RUNTIME_HANDBOOK]
    assert "Runtime Handbook" in runtime
    assert "Operational authorities" in runtime
    assert "UCKO-RULE-0001" in runtime  # enforced runtime rule
    assert "UCKO-PRIN-0001" in runtime  # constitutional guarantee

    # Traceability links objects to their decisions and dependencies.
    trace = rendered[TRACEABILITY_REPORT]
    assert "Traceability Report" in trace
    assert "UKDA-DEC-0001" in trace  # decision traceability
    assert "UCKO-DEC-0001" in trace  # object that references the decision

    # Dependency report exposes graph analytics + health.
    dep = rendered[DEPENDENCY_REPORT]
    assert "Dependency Report" in dep
    assert "Relationship inventory" in dep
    assert "Graph health" in dep
    assert "depends-on" in dep

    # Knowledge graph visualization is a deterministic Mermaid diagram.
    graph_doc = rendered[KNOWLEDGE_GRAPH]
    assert "```mermaid" in graph_doc
    assert "graph LR" in graph_doc
    assert "UCKO_PRIN_0001" in graph_doc  # sanitized node id


def test_generated_reports_handle_empty_base():
    rendered = DocumentationEngine(KnowledgeBase([])).render_all()
    assert "No consumed contracts recorded yet" in rendered[API_HANDBOOK]
    assert "No operational authorities recorded yet" in rendered[RUNTIME_HANDBOOK]
    assert "none ratified yet" in rendered[RUNTIME_HANDBOOK]
    assert "No decisions recorded yet" in rendered[TRACEABILITY_REPORT]
    assert "_none_" in rendered[DEPENDENCY_REPORT]


def test_dependency_report_flags_broken_references():
    base = KnowledgeBase([make_cko("A1", dependencies=("MISSING-1",))])
    dep = DocumentationEngine(base).dependency_report()
    assert "A1 → MISSING-1" in dep


def test_write_all_is_deterministic(seed_base, tmp_path):
    engine = DocumentationEngine(seed_base)
    first = engine.write_all(tmp_path / "a")
    engine.write_all(tmp_path / "b")
    assert len(first) == 10
    for name in (
        ARCHITECTURE_HANDBOOK,
        DECISION_HANDBOOK,
        API_HANDBOOK,
        RUNTIME_HANDBOOK,
        TRACEABILITY_REPORT,
        DEPENDENCY_REPORT,
        KNOWLEDGE_GRAPH,
    ):
        assert (tmp_path / "a" / name).read_text() == (tmp_path / "b" / name).read_text()


def test_docs_on_empty_base_renders_placeholders():
    rendered = DocumentationEngine(KnowledgeBase([])).render_all()
    assert "No decisions recorded yet" in rendered[DECISION_HANDBOOK]
    assert "none recorded" in rendered[DEVELOPER_HANDBOOK]


def test_governance_handbook_renders_exceptions_and_skips_empty_kinds():
    base = KnowledgeBase(
        [
            make_cko("R1", kind=KnowledgeKind.RULE, rationale="r"),
            make_cko("E1", kind=KnowledgeKind.EXCEPTION, knowledge_links=("R1",)),
        ]
    )
    rendered = DocumentationEngine(base).render_all()
    gov = rendered[GOVERNANCE_HANDBOOK]
    assert "Documented exceptions" in gov
    assert "E1" in gov
    # architecture handbook skips kinds with no objects (no principles here)
    assert "Principles" not in rendered[ARCHITECTURE_HANDBOOK]


# -- bootstrap ----------------------------------------------------------------


def test_build_digest_sections(seed_base):
    digest = build_digest(seed_base)
    assert digest.constitution
    assert digest.principles
    assert digest.decisions
    d = digest.to_dict()
    assert set(BOOTSTRAP_SECTIONS) <= set(d)
    assert d["current_state"]["total_objects"] == len(seed_base.objects())


def test_digest_markdown_and_empty_base():
    md = build_digest(build_seed_base()).to_markdown()
    assert "Repository Bootstrap Brief" in md
    empty_md = build_digest(KnowledgeBase([])).to_markdown()
    assert "_none_" in empty_md


# -- seed ---------------------------------------------------------------------


def test_seed_validates_and_certifies():
    base = build_seed_base()
    assert validate_base(base).accepted
    assert certify_base(base).certified
    assert base.has_object("UCKO-PRIN-0001")
    assert base.has_decision("UKDA-DEC-0001")
    assert len(base.objects()) >= 10


def test_make_cko_helper_is_sane():
    assert make_cko("Z").verify_integrity()


def test_the_decision_handbook_omits_every_section_the_decision_left_empty():
    """FOUR OPTIONAL SECTIONS, and each of them omitted rather than rendered empty.

    Rejected options, consequences, risks and mitigations are all optional on a decision
    record, and the handbook is what a reader consults to decide whether a decision still
    holds. A **Risks.** heading with nothing under it reads as "no risks were identified",
    which is a claim; omitting the heading reads as "this decision does not record risks",
    which is the truth. The seed corpus fills all four, so all four omissions were dead.
    """

    bare = make_decision(
        "UDR-BARE",
        rejected_options=(),
        consequences=(),
        risks=(),
        mitigations=(),
    )
    rendered = DocumentationEngine(KnowledgeBase([], [bare])).render_all()[DECISION_HANDBOOK]
    for heading in ("Rejected options", "Consequences", "Risks", "Mitigations"):
        assert f"**{heading}.**" not in rendered, heading
    # The mandatory parts are still there, so the omissions are not a blank document.
    assert "The chosen architecture." in rendered
    assert "**Rationale.**" in rendered
    assert "**Supersession rules.**" in rendered

    full = make_decision(
        "UDR-FULL",
        consequences=("a consequence",),
        risks=("a risk",),
        mitigations=("a mitigation",),
    )
    complete = DocumentationEngine(KnowledgeBase([], [full])).render_all()[DECISION_HANDBOOK]
    for heading in ("Rejected options", "Consequences", "Risks", "Mitigations"):
        assert f"**{heading}.**" in complete, heading


def test_a_graph_node_that_is_neither_an_object_nor_a_decision_is_labelled_by_its_id():
    """The label falls back to the id, and the fallback is the honest answer.

    A node reached through a reference to something the base does not hold has no title to
    show. Rendering nothing would produce an unlabelled node in the knowledge graph, and
    inventing a title would name an object that does not exist — so the id, which is the one
    true thing known about it, is what the reader sees.
    """

    base = KnowledgeBase(
        [make_cko("A", dependencies=("MISSING-TARGET",))],
        [make_decision("UDR-1")],
    )
    engine = DocumentationEngine(base)
    assert engine._node_label("A") == "Title A"
    assert engine._node_label("UDR-1") == "Decision UDR-1"
    assert engine._node_label("MISSING-TARGET") == "MISSING-TARGET"
    assert "MISSING-TARGET" in engine.render_all()[KNOWLEDGE_GRAPH]
