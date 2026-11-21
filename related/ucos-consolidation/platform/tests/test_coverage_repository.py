"""ZG-P-02 — repository evidence source tests (parsers + synthetic + real repo)."""

from __future__ import annotations

from pathlib import Path
from platform.coverage.contracts import CoverageNodeKind
from platform.coverage.errors import CoverageEvidenceError
from platform.coverage.graph import CoverageGraph
from platform.coverage.repository import (
    RepositoryEvidenceSource,
    best_match,
    discover_repo_root,
    parse_imp_names,
    parse_universe_rows,
    top_level_symbols,
)

import pytest

K = CoverageNodeKind
_REAL_ROOT = Path(__file__).resolve().parents[2]


# --------------------------------------------------------------------------- #
# Pure helper tests                                                           #
# --------------------------------------------------------------------------- #


def test_parse_universe_rows_extracts_phase_and_skips_malformed():
    md = "\n".join(
        [
            "| ID | Name | Class | Parent | Dep | Reg | Tier | Phase | Desc |",
            "| UNI-201 | A | CL | p | d | R | T | IMP-005 | desc |",
            "| UNI-202 | B | CL | p | d | R | T | none-here | desc |",  # no IMP → skip
            "| UNI-203 | too | short |",  # < 9 cols → skip
            "| DOM-9 | not a universe row |",  # not UNI → skip
            "free text line",
        ]
    )
    rows = parse_universe_rows(md)
    assert rows == (("UNI-201", "IMP-005"),)


def test_parse_imp_names_dedupes():
    md = "\n".join(
        [
            "### IMP-005 — Identity Platform",
            "#### IMP-006 : Knowledge Base",
            "### IMP-005 — Duplicate Header Ignored",
        ]
    )
    names = parse_imp_names(md)
    assert names["IMP-005"] == "Identity Platform"
    assert names["IMP-006"] == "Knowledge Base"


def test_top_level_symbols_public_only_and_syntax_error():
    src = "def public():\n    pass\n\nclass Public:\n    pass\n\ndef _private():\n    pass\n"
    assert top_level_symbols(src) == ("Public", "public")
    assert top_level_symbols("def (:::") == ()  # SyntaxError → empty


def test_best_match_overlap_none_and_tiebreak():
    cands = {"b": frozenset({"x"}), "a": frozenset({"x"})}
    assert best_match(frozenset({"x"}), cands) == "a"  # tie → sorted key
    assert best_match(frozenset({"z"}), cands) is None
    assert best_match(frozenset(), {}) is None


def test_discover_repo_root_finds_real_root_and_fails_closed(tmp_path):
    assert discover_repo_root(Path(__file__)) == _REAL_ROOT
    with pytest.raises(CoverageEvidenceError):
        discover_repo_root(tmp_path)  # no markers anywhere above tmp


# --------------------------------------------------------------------------- #
# Synthetic repository (full collect branch coverage)                         #
# --------------------------------------------------------------------------- #


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _make_repo(root: Path) -> None:
    # Markers for discover_repo_root.
    (root / "platform").mkdir(parents=True, exist_ok=True)
    (root / "02-MASTER").mkdir(parents=True, exist_ok=True)

    # Universe catalog: covered (IMP-005), no-imp-name (IMP-009), program-no-pkg (IMP-007),
    # no-doc phase (IMP-008), knowledge-no-epic (IMP-006), runtime-absent (IMP-004).
    rows = [
        "| ID | Name | Class | Parent | Dep | Reg | Tier | Phase | Desc |",
        "| UNI-201 | A | CL | p | d | R | T | IMP-005 | desc |",
        "| UNI-202 | B | CL | p | d | R | T | IMP-006 | desc |",
        "| UNI-203 | C | CL | p | d | R | T | IMP-007 | desc |",
        "| UNI-204 | D | CL | p | d | R | T | IMP-008 | desc |",
        "| UNI-205 | E | CL | p | d | R | T | IMP-009 | desc |",
        "| UNI-206 | F | CL | p | d | R | T | IMP-004 | desc |",
    ]
    _write(root / "02-MASTER" / "UCOS-Ω∞-UNIVERSAL-UNIVERSE-CATALOG.md", "\n".join(rows))

    # Tracker headers (omit IMP-009 → phase→program skip via imp_names.get None).
    tracker = "\n".join(
        [
            "### IMP-005 — Identity Platform",
            "### IMP-006 — Knowledge Base",
            "### IMP-007 — Compiler Thing",
            "### IMP-008 — Zzzz Unmatched",
            "### IMP-004 — Registryx Store",
        ]
    )
    _write(root / "02-MASTER" / "UCOS-Ω∞-IMPLEMENTATION-PROGRAM-TRACKER.md", tracker)

    # 06-IMPLEMENTATION program docs (IMP-008 has no doc → phase→program None).
    impl = root / "06-IMPLEMENTATION"
    for name in ("UCOS-IDENTITY", "UCOS-KNOWLEDGE", "UCOS-COMPILER", "UCOS-REGISTRYX"):
        _write(impl / f"{name}.md", f"# {name}\n")

    # platform/identity — fully covered (completion report + test).
    ident = root / "platform" / "identity"
    _write(ident / "service.py", "class AuthorizationService:\n    pass\n")
    _write(ident / "__init__.py", "from x import y  # no top-level symbol\n")
    _write(ident / "EC2-EPIC-002-COMPLETION-REPORT.md", "done\n")
    _write(root / "platform" / "tests" / "test_identity_syn.py", "def test_x():\n    pass\n")

    # platform/knowledge — matched implementation but NO completion report (no epic).
    _write(root / "platform" / "knowledge" / "kb.py", "def query():\n    pass\n")

    # platform/registryx — completion report but NO test → runtime evidence absent.
    # Also seed a non-matching completion-report filename (empty prefix) that sorts
    # before the valid one, exercising the parser's skip-and-continue path.
    reg = root / "platform" / "registryx"
    _write(reg / "reg.py", "def allocate():\n    pass\n")
    _write(reg / "-COMPLETION-REPORT.md", "not a valid epic id\n")
    _write(reg / "EC2-EPIC-004-COMPLETION-REPORT.md", "done\n")

    # Stray non-package entries (skipped by iterdir filters).
    _write(root / "platform" / "README.md", "not a package\n")
    (root / "platform" / "__pycache__").mkdir(parents=True, exist_ok=True)


def test_synthetic_repo_collect_exercises_all_branches(tmp_path):
    _make_repo(tmp_path)
    src = RepositoryEvidenceSource(str(tmp_path))
    bundle = src.collect()
    graph = CoverageGraph(bundle)

    refs = {(n.kind, n.ref) for n in graph.nodes()}
    # 6 universes parsed.
    assert sum(1 for n in graph.nodes() if n.kind is K.UNIVERSE) == 6
    # identity chain fully covered.
    ident_uni = next(n for n in graph.nodes_of_kind(K.UNIVERSE) if n.ref == "UNI-201")
    from platform.coverage.contracts import CoverageStatus

    assert graph.status_of(ident_uni.node_id) is CoverageStatus.COVERED
    # runtime asset only for identity (registryx had no test).
    runtime_refs = {n.ref for n in graph.nodes_of_kind(K.RUNTIME_ASSET)}
    assert runtime_refs == {"runtime:platform/identity"}
    # knowledge implementation exists but has no epic (no completion report).
    assert (K.IMPLEMENTATION, "platform/knowledge") in refs
    assert not any(
        e.source_ref == "platform/knowledge" and e.target_kind is K.EPIC for e in graph.edges()
    )
    # compiler program exists but no implementation package matched.
    assert (K.PROGRAM, "06-IMPLEMENTATION/UCOS-COMPILER.md") in refs
    assert not any(
        e.source_ref == "06-IMPLEMENTATION/UCOS-COMPILER.md" and e.target_kind is K.IMPLEMENTATION
        for e in graph.edges()
    )
    # deterministic.
    assert src.collect().fingerprint() == bundle.fingerprint()
    assert src.root == tmp_path.resolve()


def test_missing_required_artifact_fails_closed(tmp_path):
    (tmp_path / "platform").mkdir()
    (tmp_path / "02-MASTER").mkdir()  # markers present, but catalog file absent
    src = RepositoryEvidenceSource(str(tmp_path))
    with pytest.raises(CoverageEvidenceError):
        src.collect()


def test_collect_without_impl_dir_yields_no_programs(tmp_path):
    # Markers + catalog + tracker present, but no 06-IMPLEMENTATION directory.
    (tmp_path / "platform").mkdir()
    _write(
        tmp_path / "02-MASTER" / "UCOS-Ω∞-UNIVERSAL-UNIVERSE-CATALOG.md",
        "| UNI-201 | A | CL | p | d | R | T | IMP-005 | desc |\n",
    )
    _write(
        tmp_path / "02-MASTER" / "UCOS-Ω∞-IMPLEMENTATION-PROGRAM-TRACKER.md",
        "### IMP-005 — Identity Platform\n",
    )
    bundle = RepositoryEvidenceSource(str(tmp_path)).collect()
    assert any(n.kind is K.UNIVERSE for n in bundle.nodes)
    assert not any(n.kind is K.PROGRAM for n in bundle.nodes)


# --------------------------------------------------------------------------- #
# Real repository integration                                                 #
# --------------------------------------------------------------------------- #


def test_real_repository_parses_universe_catalog():
    src = RepositoryEvidenceSource()  # default: discover from __file__
    bundle = src.collect()
    universes = [n for n in bundle.nodes if n.kind is K.UNIVERSE]
    # The committed catalog registers 112 universes (UNI-001..112).
    assert len(universes) == 112
    graph = CoverageGraph(bundle)
    assert graph.orphan_universes() == ()
    assert graph.orphan_code() == ()
