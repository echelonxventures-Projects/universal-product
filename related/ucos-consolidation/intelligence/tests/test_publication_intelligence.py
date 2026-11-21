"""UCOS-UPI-001 Publication Intelligence validation tests.

Proves the three properties the mission demands:
  * everything generated from canonical knowledge — every block resolves to a
    canonical record and carries that record's locator and content hash
  * no duplicated content — a specification cannot hold prose; a reference is never
    repeated inside a document; a reference cited by N publications yields ONE
    citation record
  * unlimited publication formats — a format and a renderer registered at runtime,
    from data alone, generate and validate with no change to any engine

Run: .ec1-venv/bin/python -m pytest intelligence/tests -q
"""

from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

import pytest

from intelligence.kernel.canonical import canonical_json
from intelligence.kernel.config import MemorySink, subsystem_config
from intelligence.kernel.errors import (
    FormatUnknownError,
    IdentityDivergenceError,
    KernelError,
    UnresolvedReferenceError,
)
from intelligence.publication import GENERATED_BANNER
from intelligence.publication.__main__ import main as cli_main
from intelligence.publication.composer import PublicationComposer
from intelligence.publication.engine import (
    DOCUMENTS_DIR,
    EXIT_ABORT,
    FORMAT_EXTENSION_FILE,
    OUTPUT_DIR,
    PublicationIntelligenceEngine,
)
from intelligence.publication.formats import FormatRegistry
from intelligence.publication.generators import (
    NAMED_DELIVERABLES,
    PublicationGenerator,
    PublicationScope,
    descriptor_for_deliverable,
)
from intelligence.publication.model import ComposedBlock, ComposedDocument
from intelligence.publication.registry import PublicationRegistry
from intelligence.publication.renderers import (
    get_renderer,
    register_renderer,
    render_html,
    render_latex,
    render_markdown,
    renderer_ids,
)
from intelligence.publication.validation import PublicationValidationEngine

REPO = subsystem_config(OUTPUT_DIR).repo_root


def _engine() -> PublicationIntelligenceEngine:
    return PublicationIntelligenceEngine(subsystem_config(OUTPUT_DIR, REPO))


@pytest.fixture(scope="module")
def engine() -> PublicationIntelligenceEngine:
    return _engine()


# -- generation coverage -----------------------------------------------------


def test_every_registered_format_is_generated(engine) -> None:
    publications = engine.publications()
    assert set(publications.format_ids()) == set(engine.formats.format_ids())
    assert len(publications.documents) == len(publications.specs)
    assert len(publications.rendered) == len(publications.specs)


def test_named_deliverables_all_generate(engine) -> None:
    """Every deliverable the mission names resolves to a real, composed document."""
    for name, format_id in sorted(NAMED_DELIVERABLES.items()):
        spec = engine.generator.build(format_id, engine.scope())
        document, body = engine.composer.render(spec)
        assert document.resolved_total() > 0, name
        assert GENERATED_BANNER in body, name
        assert document.title, name


def test_required_sections_are_satisfied(engine) -> None:
    for document in engine.publications().documents:
        descriptor = engine.formats.get(document.format_id)
        for block in document.blocks:
            if block.section_key in descriptor.required and not block.structural:
                assert not block.is_empty, f"{document.format_id}/{block.section_key}"


def test_genres_cover_the_mission_deliverables(engine) -> None:
    genres = engine.formats.genres()
    for genre in (
        "paper",
        "journal",
        "conference",
        "white-paper",
        "technical-article",
        "patent",
        "standards",
    ):
        assert genre in genres, genre
        assert genres[genre]


# -- generated from canonical knowledge --------------------------------------


def test_every_block_resolves_to_a_canonical_record(engine) -> None:
    for document in engine.publications().documents:
        assert document.unresolved == ()
        for block in document.blocks:
            for resolved in block.resolved:
                assert resolved.text
                assert resolved.source_locator
                assert len(resolved.source_content_sha256) == 64
                assert engine.resolver.exists(resolved.ref)


def test_document_title_comes_from_canonical_knowledge(engine) -> None:
    for document in engine.publications().documents:
        assert document.title_ref.startswith(("cko:", "decision:"))
        assert document.title == engine.resolver.resolve(document.title_ref).text


def test_rendered_documents_declare_they_are_generated(engine) -> None:
    for name, body in engine.publications().rendered.items():
        assert GENERATED_BANNER in body, name


# -- no duplicated content ---------------------------------------------------


def test_specification_carries_no_canonical_prose(engine) -> None:
    for spec in engine.publications().specs:
        serialized = canonical_json(spec.to_dict())
        assert engine.resolver.copied_prose(serialized) == [], spec.format_id


def test_no_reference_repeats_inside_a_document(engine) -> None:
    for spec in engine.publications().specs:
        refs = [ref for section in spec.sections for ref in section.ref_strings]
        assert len(refs) == len(set(refs)), spec.format_id


def test_shared_citation_is_registered_exactly_once(engine) -> None:
    report = engine.registry().shared_citation_report()
    assert report["duplicate_citation_records"] == 0
    assert report["registered_citation_records"] == report["distinct_references"]
    # The whole point: many publications, one record per canonical reference.
    assert report["total_citation_uses"] > report["distinct_references"]
    assert report["reuse_factor"] > 1.0


def test_registry_integrity(engine) -> None:
    integrity = engine.registry().verify()
    assert integrity["chain_intact"] is True
    assert integrity["knowledge_once_holds"] is True
    assert integrity["intact"] is True


# -- unlimited formats -------------------------------------------------------


def test_new_format_registered_from_data_generates_without_code_change(engine) -> None:
    registry = FormatRegistry()
    before = len(registry.format_ids())
    registry.register_format(
        {
            "format_id": "test-newsletter",
            "genre": "newsletter",
            "label": "Engineering Newsletter",
            "sections": ["title-block", "executive-summary", "results", "provenance"],
            "required": ["title-block", "executive-summary", "provenance"],
            "renderer": "markdown",
            "extension": "md",
        }
    )
    assert len(registry.format_ids()) == before + 1
    probe = PublicationIntelligenceEngine(subsystem_config(OUTPUT_DIR, REPO), registry)
    spec = probe.generator.build("test-newsletter", probe.scope())
    document, body = probe.composer.render(spec)
    assert document.resolved_total() > 0
    assert "Engineering Newsletter" in body


def test_new_section_type_registered_from_data(engine) -> None:
    registry = FormatRegistry()
    registry.register_section(
        {
            "key": "test-open-questions",
            "label": "Open Questions",
            "rule": {"source": "claims", "claim_classes": ["negative-result"], "ref": "claim_ref"},
        }
    )
    registry.register_format(
        {
            "format_id": "test-position-paper",
            "genre": "position",
            "label": "Position Paper",
            "sections": ["title-block", "abstract", "test-open-questions", "provenance"],
            "required": ["title-block", "abstract", "provenance"],
        }
    )
    probe = PublicationIntelligenceEngine(subsystem_config(OUTPUT_DIR, REPO), registry)
    spec = probe.generator.build("test-position-paper", probe.scope())
    assert "test-open-questions" in spec.section_keys()
    document, body = probe.composer.render(spec)
    assert "Open Questions" in body


def test_format_declaration_file_extends_the_registry(tmp_path: Path) -> None:
    declaration = {
        "sections": [
            {
                "key": "test-glossary",
                "label": "Glossary",
                "rule": {"source": "claims", "ref": "subject_ref", "limit": 5},
            }
        ],
        "formats": [
            {
                "format_id": "test-field-guide",
                "genre": "guide",
                "label": "Field Guide",
                "sections": ["title-block", "test-glossary", "provenance"],
                "required": ["title-block", "test-glossary", "provenance"],
                "renderer": "plaintext",
                "extension": "txt",
            }
        ],
    }
    path = tmp_path / "publication-formats.json"
    path.write_text(json.dumps(declaration), encoding="utf-8")
    registry = FormatRegistry()
    added = registry.load_file(path)
    assert [d.format_id for d in added] == ["test-field-guide"]
    probe = PublicationIntelligenceEngine(subsystem_config(OUTPUT_DIR, REPO), registry)
    spec = probe.generator.build("test-field-guide", probe.scope())
    _document, body = probe.composer.render(spec)
    assert "GLOSSARY" in body


def test_new_renderer_registered_at_runtime(engine) -> None:
    marker = "TEST-RENDERER-OUTPUT"

    def _render(document, descriptor) -> str:  # noqa: ANN001 - test-local renderer
        return f"{GENERATED_BANNER}\n{marker}\n{descriptor.format_id}\n{document.title}\n"

    register_renderer("test-renderer", _render)
    assert "test-renderer" in renderer_ids()
    registry = FormatRegistry()
    registry.register_format(
        {
            "format_id": "test-custom-syntax",
            "genre": "custom",
            "label": "Custom Syntax Document",
            "sections": ["title-block", "abstract", "provenance"],
            "required": ["title-block", "abstract", "provenance"],
            "renderer": "test-renderer",
            "extension": "custom",
        }
    )
    probe = PublicationIntelligenceEngine(subsystem_config(OUTPUT_DIR, REPO), registry)
    spec = probe.generator.build("test-custom-syntax", probe.scope())
    _document, body = probe.composer.render(spec)
    assert marker in body


def test_openness_probe_is_executed_not_asserted(engine) -> None:
    result = engine.openness_probe()
    assert result["code_changed"] is False
    assert result["generated"] is True
    assert result["rendered"] is True
    assert result["required_sections_satisfied"] is True


def test_unknown_format_is_rejected(engine) -> None:
    with pytest.raises(FormatUnknownError):
        engine.formats.get("no-such-format")


def test_format_referencing_an_undeclared_section_is_rejected() -> None:
    registry = FormatRegistry()
    with pytest.raises(KernelError):
        registry.register_format(
            {
                "format_id": "test-broken",
                "sections": ["title-block", "not-a-declared-section"],
                "required": [],
            }
        )


# -- scopes ------------------------------------------------------------------


def test_publications_can_be_scoped_to_a_research_area(engine) -> None:
    scopes = engine.generator.scopes()
    assert len(scopes) == 1 + len(engine.research.corpus().units)
    area = next(s for s in scopes if s.unit_id)
    spec = engine.generator.build("technical-article", area)
    assert spec.area_label == area.area_label
    assert spec.unit_id == area.unit_id


def test_scope_partitions_the_corpus(engine) -> None:
    corpus = engine.research.corpus()
    whole = PublicationScope.whole_corpus(corpus)
    assert len(whole.claims) == len(corpus.claims)
    per_area = [PublicationScope.for_unit(corpus, u) for u in corpus.units]
    assert sum(len(s.claims) for s in per_area) == len(corpus.claims)


# -- determinism -------------------------------------------------------------


def test_determinism_of_outputs_and_documents(engine) -> None:
    result = engine.verify_determinism()
    assert result["deterministic"] is True
    assert result["output_mismatches"] == []
    assert result["document_mismatches"] == []


def test_rendering_is_byte_identical_across_two_sinks() -> None:
    a, b = MemorySink(), MemorySink()
    _engine().write(a)
    _engine().write(b)
    assert a.store.keys() == b.store.keys()
    for name in a.store:
        assert a.store[name] == b.store[name], f"non-deterministic artifact: {name}"


# -- authority + sealing -----------------------------------------------------


def test_no_duplicate_authority(engine) -> None:
    for payload in engine.outputs().values():
        assert payload["authority"] == "NONE (derived truth)"
        assert payload["programme"] == "UCOS-UPI-001"


def test_outputs_are_sealed(engine) -> None:
    for payload in engine.outputs().values():
        assert json.loads(canonical_json(payload))["content_hash"] == payload["content_hash"]


# -- validation + gate -------------------------------------------------------


def test_validation_certifies_the_publication_set(engine) -> None:
    report = engine.validation()
    assert report.verdict == "CERTIFIED", [c.check_id for c in report.blocking_failures()]
    assert len(report.checks) == 14
    assert report.exit_code == 0


def test_gate_opens_and_reports_a_seal(engine) -> None:
    code, line = engine.gate()
    assert code == 0
    assert "gate=OPEN" in line
    assert "seal=" in line


# -- write scope -------------------------------------------------------------


def test_engine_writes_only_inside_its_own_directory() -> None:
    written = _engine().write()
    for path in written:
        parts = Path(path).parts
        assert "intelligence" in parts
        assert OUTPUT_DIR in parts, f"write escaped {OUTPUT_DIR}: {path}"
    assert any(DOCUMENTS_DIR in Path(p).parts for p in written)


# --------------------------------------------------------------------------- the CLI
#
# ``python -m intelligence.publication`` was 73 statements measured at 0.0%. The engine below it
# had 349 lines of tests and the surface an operator actually types had none, so every exit code
# in the module docstring was a claim about untested code. Each test here calls ``main`` with the
# argv an operator would type and asserts the LITERAL exit code, because a gate's exit code is
# its whole interface to the shell and an attribute reference proves nothing about its value.


def _run(capsys: pytest.CaptureFixture[str], *argv: str) -> tuple[int, str, str]:
    code = cli_main(list(argv))
    captured = capsys.readouterr()
    return code, captured.out, captured.err


def test_the_cli_prints_the_open_format_catalog(capsys: pytest.CaptureFixture[str]) -> None:
    code, out, _ = _run(capsys, "formats")
    assert code == 0
    catalog = json.loads(out)
    assert catalog, "an empty catalog would mean the format space is closed, not open"


def test_the_cli_renders_a_named_deliverable(capsys: pytest.CaptureFixture[str]) -> None:
    """One render through the CLI; the other names are checked against the registry below,
    because building the engine once per deliverable buys the same assurance six times."""
    code, out, _ = _run(capsys, "generate", sorted(NAMED_DELIVERABLES)[0])
    assert code == 0
    assert out.strip(), "the deliverable rendered an empty document"
    assert out.endswith("\n"), "a rendered document must end in a newline"


def test_every_named_deliverable_resolves_to_a_registered_format() -> None:
    registry = FormatRegistry()
    for name, format_id in sorted(NAMED_DELIVERABLES.items()):
        assert registry.has(format_id), f"{name} names {format_id}, which no format declares"


def test_the_cli_accepts_a_format_id_as_well_as_a_deliverable_name(
    capsys: pytest.CaptureFixture[str],
) -> None:
    format_id = NAMED_DELIVERABLES[sorted(NAMED_DELIVERABLES)[0]]
    code, out, _ = _run(capsys, "generate", format_id)
    assert code == 0 and out.strip()


def test_the_cli_emits_the_set_registry_snapshot_and_validation(
    capsys: pytest.CaptureFixture[str],
) -> None:
    for command in ("set", "registry", "snapshot"):
        code, out, _ = _run(capsys, command)
        assert code == 0, command
        assert json.loads(out), f"{command} emitted an empty document"
    code, out, _ = _run(capsys, "validate")
    report = json.loads(out)
    assert (code == 0) is (report["gate"] == "OPEN"), (
        "the CLI must return the report's own verdict; deciding it separately would let the "
        "shell and the document disagree about the same run"
    )
    assert code in (0, 1)


def test_the_cli_gate_agrees_with_the_engine_gate(capsys: pytest.CaptureFixture[str]) -> None:
    expected, line = _engine().gate()
    code, out, _ = _run(capsys, "gate")
    assert code == expected
    assert code in (0, 1), "the gate is two-valued unless it aborts, and an abort is exit 2"
    assert out.strip() == line.strip()


def test_the_cli_verify_proves_deterministic_regeneration(
    capsys: pytest.CaptureFixture[str],
) -> None:
    code, out, _ = _run(capsys, "verify")
    assert code == 0
    assert json.loads(out)["deterministic"] is True


def test_the_cli_build_reports_what_it_wrote(capsys: pytest.CaptureFixture[str]) -> None:
    """Regeneration is idempotent by construction — ``verify`` above proves it — so this run
    rewrites byte-identical files rather than mutating the tree."""
    code, out, _ = _run(capsys, "build")
    assert code == 0
    assert "UPI: regenerated" in out
    assert out.count("  - ") >= 1, "a build that names no artifact reports nothing"


def test_a_broken_formats_file_is_a_fail_closed_abort_and_not_a_pass(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A KernelError is exit 2: the run reached no verdict, which is not the same as CLOSED."""
    declaration = tmp_path / "formats.json"
    declaration.write_text('["not-an-object"]', encoding="utf-8")
    code, _out, err = _run(capsys, "--formats-file", str(declaration), "formats")
    assert code == 2
    assert "FAIL-CLOSED ABORT" in err


def test_an_extra_format_registered_from_a_file_reaches_the_catalog(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    declaration = tmp_path / "formats.json"
    declaration.write_text(json.dumps({"sections": [], "formats": []}), encoding="utf-8")
    code, out, _ = _run(capsys, "--formats-file", str(declaration), "formats")
    assert code == 0 and json.loads(out)


def test_an_unknown_format_is_refused_rather_than_substituted(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """``FormatUnknownError`` is a ``KernelError``, so the CLI converts it into exit 2 — a run
    that reached no verdict — rather than letting it look like a closed gate."""
    code, _out, err = _run(capsys, "generate", "no-such-format")
    assert code == 2
    assert "FAIL-CLOSED ABORT" in err
    assert "no-such-format" in err, "a refusal that does not name its subject cannot be acted on"


def test_a_subcommand_is_required() -> None:
    with pytest.raises(SystemExit) as raised:
        cli_main([])
    assert raised.value.code == 2


# -- the renderers over a document with nothing to render -------------------------------
#
# WHY THIS SECTION EXISTS. Every renderer is exercised over THIS repository's publications,
# which have citations, resolved blocks and no unresolved references. The branches that
# only fire when a document is EMPTY or INCOMPLETE were therefore unexecuted in all five
# syntaxes: the "no citations" note, the unresolved-reference list, the empty-block skip,
# and the `return []` a structural renderer gives for a section it does not own. Those are
# the branches a publication takes on the day a reference stops resolving, which is exactly
# when the output has to stay readable and honest.


def _empty_document(**overrides):
    fields = {
        "publication_id": "PUB-EMPTY",
        "format_id": "fmt",
        "genre": "genre",
        "format_label": "Format",
        "area_label": "Area",
        "title": "An Empty Publication",
        "title_ref": "cko:UCOS-X#title",
        "blocks": (
            ComposedBlock("title-block", "Title", 0, True, ()),
            ComposedBlock("references", "References", 1, True, ()),
            ComposedBlock("provenance", "Provenance", 2, True, ()),
            ComposedBlock("body", "Body", 3, False, ()),
            ComposedBlock("nobody-owns-this", "Foreign", 4, True, ()),
        ),
        "citations": (),
        "renderer": "markdown",
        "extension": "md",
        "citation_style": "numeric",
        "unresolved": ({"ref": "cko:GONE#statement", "reason": "not found"},),
    }
    fields.update(overrides)
    return ComposedDocument(**fields)


def _descriptor(engine):
    return engine.formats.get(engine.formats.format_ids()[0])


@pytest.mark.parametrize("renderer_id", ["markdown", "latex", "html", "plaintext", "json"])
def test_every_renderer_survives_a_document_with_nothing_resolved(engine, renderer_id) -> None:
    body = get_renderer(renderer_id)(_empty_document(), _descriptor(engine))
    assert isinstance(body, str)
    assert body.strip()


def test_the_markdown_renderer_says_there_are_no_citations_rather_than_printing_a_header(
    engine,
) -> None:
    body = render_markdown(_empty_document(), _descriptor(engine))
    assert "_no citations_" in body
    assert "| # | Canonical reference |" not in body


def test_the_markdown_renderer_lists_every_unresolved_reference_by_name(engine) -> None:
    """An unresolved reference is a fact about the publication, and hiding it would make an
    incomplete document indistinguishable from a complete one."""
    body = render_markdown(_empty_document(), _descriptor(engine))
    assert "### Unresolved references" in body
    assert "cko:GONE#statement" in body
    assert "not found" in body


def test_a_structural_section_no_renderer_owns_contributes_nothing(engine) -> None:
    document = _empty_document()
    descriptor = _descriptor(engine)
    for body in (
        render_markdown(document, descriptor),
        render_latex(document, descriptor),
        render_html(document, descriptor),
    ):
        assert "Foreign" not in body


def test_a_descriptor_that_carries_notes_renders_them_in_every_syntax(engine) -> None:
    descriptor = _descriptor(engine)
    noted = replace(descriptor, notes="A note the format declares about itself.")
    assert "A note the format declares" in render_latex(_empty_document(), noted)
    assert "A note the format declares" in render_html(_empty_document(), noted)


def test_a_renderer_must_have_an_id_and_be_callable() -> None:
    with pytest.raises(KernelError):
        register_renderer("", lambda document, descriptor: "")
    with pytest.raises(KernelError):
        register_renderer("not-callable", "this is not a renderer")


def test_an_unregistered_renderer_is_refused_and_names_what_is_registered() -> None:
    with pytest.raises(KernelError) as excinfo:
        get_renderer("no-such-renderer")
    assert excinfo.value.context["registered"] == renderer_ids()


# -- the named deliverables, called by the names the mission gives them -----------------
#
# WHY THIS SECTION EXISTS. `NAMED_DELIVERABLES` is exercised through the generic
# `build(format_id, ...)` path, which is the right thing to test — but it leaves the seven
# explicitly-named methods, the genre selector and the deliverable descriptor lookup as
# published API nothing calls. An API published and never invoked is an API whose next
# rename breaks a caller nobody warned.


def test_every_named_deliverable_method_builds_the_format_it_names(engine) -> None:
    generator = engine.generator
    by_method = {
        "paper": generator.generate_paper,
        "journal": generator.generate_journal_article,
        "conference-paper": generator.generate_conference_paper,
        "white-paper": generator.generate_white_paper,
        "technical-article": generator.generate_technical_article,
        "patent-draft": generator.generate_patent_draft,
        "standards-proposal": generator.generate_standards_proposal,
    }
    assert set(by_method) == set(NAMED_DELIVERABLES)
    for name, build in sorted(by_method.items()):
        spec = build(engine.scope())
        assert spec.format_id == NAMED_DELIVERABLES[name]
        assert descriptor_for_deliverable(name, engine.formats).format_id == spec.format_id


def test_a_deliverable_may_also_be_addressed_by_its_format_id(engine) -> None:
    assert descriptor_for_deliverable("research-paper", engine.formats).format_id == (
        "research-paper"
    )


def test_building_by_genre_builds_exactly_that_genre(engine) -> None:
    genre = engine.formats.get("research-paper").genre
    specs = engine.generator.build_by_genre(genre, engine.scope())
    expected = {f.format_id for f in engine.formats.by_genre(genre)}
    assert {s.format_id for s in specs} == expected
    assert expected


def test_a_title_falls_back_through_every_claim_before_reporting_none(engine) -> None:
    """The preferred claim classes are an ORDER, not a requirement: a corpus that declares
    none of them still gets a title from whatever claim it does have, and a corpus with no
    resolvable claim at all reports the absence rather than inventing one."""
    generator = engine.generator
    scope = engine.scope()
    assert generator._title_ref(scope)

    preferred = ("foundational-claim", "determination", "specification-claim")
    others = tuple(c for c in scope.claims if c.claim_class not in preferred)
    if others:
        assert generator._title_ref(replace(scope, claims=others))

    assert generator._title_ref(replace(scope, claims=())) == ""


# ---------------------------------------------------------------------------------------
# The registry is OPEN, and openness is what makes its refusals load-bearing
#
# A new format or section arrives as DATA — that is the whole design, and the tests above
# prove it works. The consequence is that the registry is the only thing standing between a
# declaration file somebody wrote and a publication built from it, so every one of its
# refusals is the difference between a typo being reported and a document being generated
# with a section that silently resolves to nothing. None of them had run.
# ---------------------------------------------------------------------------------------


def _section(**overrides) -> dict:
    entry = {
        "key": "test-section",
        "label": "Test Section",
        "rule": {"source": "claims", "ref": "claim_ref"},
    }
    entry.update(overrides)
    return entry


def _format(**overrides) -> dict:
    entry = {
        "format_id": "test-format",
        "genre": "test",
        "label": "Test Format",
        "sections": ["title-block", "provenance"],
        "required": ["title-block"],
    }
    entry.update(overrides)
    return entry


def test_a_section_declaration_with_an_unknown_key_is_refused() -> None:
    """A TYPO IS A SILENTLY ABSENT DECLARATION otherwise. ``labl`` instead of ``label`` would
    register a section with an empty label — which then fails the key-and-label check for a
    reason that names the missing label rather than the misspelled key that caused it, if it
    fails at all. The unknown key is named, so the reader is corrected at the source."""
    registry = FormatRegistry()
    with pytest.raises(KernelError) as excinfo:
        registry.register_section(_section(audiance="engineers"))
    assert excinfo.value.context["keys"] == ["audiance"]


def test_a_section_declaration_needs_both_a_key_and_a_label() -> None:
    """The key is how a format cites the section and the label is what a reader sees. A
    section with neither is unciteable; with one it is either invisible in the document or
    unreachable from any format."""
    registry = FormatRegistry()
    for missing in ({"key": ""}, {"label": ""}, {"key": "", "label": ""}):
        with pytest.raises(KernelError, match="requires a key and a label"):
            registry.register_section(_section(**missing))


def test_a_non_structural_section_must_carry_a_rule_object() -> None:
    """STRUCTURAL SECTIONS ARE THE EXCEPTION, and everything else needs a rule.

    A title block, a reference list and a provenance block are built by the composer itself;
    every other section is a query over canonical records, and a section with no rule is a
    heading that resolves to nothing. A rule that is not an object cannot be a query at all.
    """
    registry = FormatRegistry()
    with pytest.raises(KernelError, match="section rule must be an object"):
        registry.register_section(_section(rule="claims"))

    structural = registry.register_section(
        {"key": "test-structural", "label": "Structural", "structural": True}
    )
    assert structural.structural
    assert structural.rule == {}


@pytest.mark.parametrize(
    ("rule", "match"),
    [
        pytest.param({"source": "claims", "ref": "r", "limmit": 5}, "unknown section rule keys"),
        pytest.param({"source": "conjecture", "ref": "r"}, "unknown section rule source"),
        pytest.param({"source": "claims"}, "must name a ref field or a derived field"),
        pytest.param({"ref": "r"}, "unknown section rule source"),
    ],
)
def test_a_section_rule_is_checked_against_the_declared_vocabulary(rule, match) -> None:
    """Three separate defects, three messages. An unknown KEY is a typo in the rule; an
    unknown SOURCE names a record set that does not exist, so the query would return nothing
    forever; and a rule naming neither a ref field nor a derived field has no way to say what
    it selects — the section would render with a heading and no content, every time."""
    registry = FormatRegistry()
    with pytest.raises(KernelError, match=match):
        registry.register_section(_section(rule=rule))


def test_a_format_descriptor_with_an_unknown_key_or_no_identifier_is_refused() -> None:
    """The format_id is what every generator, renderer and citation index is keyed on. A
    descriptor without one would register under the empty string and be reachable by nothing,
    while still counting as a registered format."""
    registry = FormatRegistry()
    with pytest.raises(KernelError) as excinfo:
        registry.register_format(_format(rendrer="markdown"))
    assert excinfo.value.context["keys"] == ["rendrer"]

    with pytest.raises(KernelError, match="requires a format_id"):
        registry.register_format(_format(format_id=""))


def test_a_format_must_name_at_least_one_section() -> None:
    """A format with no sections renders an empty document. It would pass every required-
    section check vacuously, because there is nothing required and nothing to be missing."""
    registry = FormatRegistry()
    with pytest.raises(KernelError, match="requires at least one section"):
        registry.register_format(_format(sections=[]))


def test_a_required_section_outside_the_format_is_refused() -> None:
    """REQUIRING WHAT YOU DO NOT INCLUDE IS UNSATISFIABLE.

    The validation layer reports a document whose required sections are empty. A format
    requiring a section it never renders would fail that check on every document forever, and
    the failure would name the document rather than the declaration that made it impossible.
    """
    registry = FormatRegistry()
    with pytest.raises(KernelError) as excinfo:
        registry.register_format(_format(required=["title-block", "abstract"]))
    assert excinfo.value.context["outside"] == ["abstract"]


def test_asking_for_a_section_type_nobody_registered_names_what_is_registered() -> None:
    """The resolving accessor. Returning ``None`` would push the absence into the composer,
    where it becomes an attribute error naming the composer rather than the missing section —
    and the registered set is listed, so a caller with a typo is corrected rather than
    merely stopped."""
    registry = FormatRegistry()
    assert registry.section("title-block").key == "title-block"

    with pytest.raises(KernelError) as excinfo:
        registry.section("test-never-registered")
    assert excinfo.value.context["section"] == "test-never-registered"
    assert "title-block" in excinfo.value.context["registered"]


# ---------------------------------------------------------------------------------------
# Each PV check driven into its own refusal
#
# The generated publication set satisfies all fourteen, which is the claim — and it means
# every refusal arm was dead. A check that has only ever passed is a check nobody has seen
# work, and each of these is the difference between a defective publication being reported
# and one being emitted with the defect intact.
# ---------------------------------------------------------------------------------------


def _validator(engine, publications=None, **overrides):
    fields = {
        "publications": publications if publications is not None else engine.publications(),
        "formats": engine.formats,
        "resolver": engine.resolver,
        "registry": engine.registry(),
        "composer": engine.composer,
        "research_registry": engine.research.registry(),
    }
    fields.update(overrides)
    return PublicationValidationEngine(
        fields["publications"],
        fields["formats"],
        fields["resolver"],
        fields["registry"],
        fields["composer"],
        fields["research_registry"],
        openness_probe=fields.get("openness_probe"),
    )


def _check(validator, check_id: str):
    return next(c for c in validator.checks() if c.check_id == check_id)


def test_pv02_refuses_a_document_whose_required_section_resolved_nothing(engine) -> None:
    """AN UNFILLABLE REQUIRED SECTION IS A FAILED PUBLICATION.

    A format declaring a section required is asserting that the document cannot be published
    without it. A block that resolved no canonical reference renders as a heading with
    nothing under it — the document looks complete and asserts nothing where its own format
    said content was mandatory.
    """
    publications = engine.publications()
    document = publications.documents[0]
    descriptor = engine.formats.get(document.format_id)
    required_key = next(
        b.section_key
        for b in document.blocks
        if b.section_key in descriptor.required and not b.structural
    )
    emptied = replace(
        document,
        blocks=tuple(
            replace(b, resolved=()) if b.section_key == required_key else b for b in document.blocks
        ),
    )
    doctored = replace(publications, documents=(emptied, *publications.documents[1:]))

    check = _check(_validator(engine, doctored), "PV-02")
    assert check.passed is False
    assert check.detail["unsatisfied"]
    assert required_key in check.detail["unsatisfied"][0]["empty_required"]


def test_pv04_refuses_a_specification_that_carries_canonical_prose(engine) -> None:
    """A SPECIFICATION HOLDS IDS, NOT SENTENCES.

    Copying canonical prose into a spec authors the same knowledge a second time — the
    duplication the whole subsystem exists to prevent — and the copy then drifts from the
    record it was taken from with nothing to notice. The check names which canonical records
    the prose was copied FROM, so the fix is to cite them instead.
    """
    validator = _validator(engine)
    monkeyed = _validator(engine)
    monkeyed.resolver = type(
        "_Copied",
        (),
        {
            "copied_prose": staticmethod(lambda _serialized: ["UCKO-TEST-0001"]),
            "__getattr__": lambda self, name: getattr(engine.resolver, name),
        },
    )()

    assert _check(validator, "PV-04").passed is True
    check = _check(monkeyed, "PV-04")
    assert check.passed is False
    assert check.detail["violations"][0]["copied_from"] == ["UCKO-TEST-0001"]


def test_pv05_refuses_a_rendered_fragment_with_no_provenance(engine) -> None:
    """EVERY RENDERED FRAGMENT CARRIES ITS LOCATOR AND CONTENT HASH.

    Without both, a reader cannot go from the published sentence back to the canonical record
    it came from — the publication becomes prose that claims to be derived and cannot show
    it. Both halves are required, so stripping either one is a refusal.
    """
    publications = engine.publications()
    document = next(d for d in publications.documents if any(b.resolved for b in d.blocks))
    block = next(b for b in document.blocks if b.resolved)
    stripped = replace(
        document,
        blocks=tuple(
            replace(b, resolved=(replace(b.resolved[0], source_locator=""), *b.resolved[1:]))
            if b is block
            else b
            for b in document.blocks
        ),
    )
    doctored = replace(
        publications,
        documents=tuple(stripped if d is document else d for d in publications.documents),
    )

    check = _check(_validator(engine, doctored), "PV-05")
    assert check.passed is False
    assert check.detail["without_provenance"]


def test_pv06_is_unassessed_rather_than_satisfied_when_no_research_registry_is_supplied(
    engine,
) -> None:
    """UNASSESSED IS NOT PASSED. Citations trace to research records, and with no research
    registry there is nothing to trace to — so the check reports ``None`` and says why. A
    ``True`` there would let a publication with untraceable citations pass by being validated
    in a configuration that could not look."""
    check = _check(_validator(engine, research_registry=None), "PV-06")

    assert check.passed is None
    assert check.detail["reason"] == "no research registry supplied"


def test_pv14_is_unassessed_rather_than_satisfied_when_no_openness_probe_is_supplied(
    engine,
) -> None:
    """The same discipline for format openness. The claim is that a format registered at
    runtime generates and validates with no code change, and without a probe nothing has
    demonstrated it — reporting satisfied would assert the claim on no evidence."""
    check = _check(_validator(engine), "PV-14")

    assert check.passed is None
    assert check.detail["reason"] == "no openness probe supplied"


# ---------------------------------------------------------------------------------------
# The composer reports what it could not resolve rather than raising
# ---------------------------------------------------------------------------------------


class _RefusingResolver:
    """A resolver that refuses every reference, wrapping a real one for everything else."""

    def __init__(self, real, *, refuse: set[str] | None = None) -> None:
        self._real = real
        self._refuse = refuse

    def resolve(self, ref: str):
        if self._refuse is None or ref in self._refuse:
            raise UnresolvedReferenceError("no canonical record for this reference", ref=ref)
        return self._real.resolve(ref)

    def __getattr__(self, name: str):
        return getattr(self._real, name)


def test_a_reference_the_resolver_cannot_answer_is_reported_not_raised(engine) -> None:
    """COMPOSITION PRODUCES A DOCUMENT AND A LIST OF WHAT IS MISSING.

    Raising on the first unresolvable reference would abandon the whole publication over one
    gap, and the operator would fix them one run at a time. Collecting them means one run
    reports every reference the canonical layer cannot answer — and PV-05 and PV-02 then
    decide whether the resulting document is publishable. The section each unresolved
    reference belongs to is recorded, because a bare ref list is not actionable.
    """

    spec = next(s for s in engine.publications().specs if any(s2.ref_strings for s2 in s.sections))
    composer = PublicationComposer(_RefusingResolver(engine.resolver), engine.formats)
    document = composer.compose(spec)

    assert document.unresolved, "nothing was reported as unresolvable"
    sections = {entry["section"] for entry in document.unresolved}
    assert sections
    assert all(entry["reason"] for entry in document.unresolved)


def test_a_title_that_cannot_be_resolved_falls_back_to_the_area_label(engine) -> None:
    """A DOCUMENT WITH NO TITLE IS NOT PUBLISHABLE, so the composer supplies the one thing it
    knows — the area label — and records the failure. Two ways to get there and both are
    reported: a scope with no title subject at all, and a title reference the canonical layer
    cannot answer. Neither invents a title, because a fabricated title is worse than a
    generic one."""

    spec = next(s for s in engine.publications().specs if s.title_ref)

    refusing = PublicationComposer(
        _RefusingResolver(engine.resolver, refuse={spec.title_ref}), engine.formats
    )
    document = refusing.compose(spec)
    assert document.title == spec.area_label
    assert any(e["ref"] == spec.title_ref for e in document.unresolved)

    titleless = replace(spec, title_ref="")
    document = engine.composer.compose(titleless)
    assert document.title == titleless.area_label
    assert any(
        e["reason"] == "the scope contains no resolvable title subject" for e in document.unresolved
    )


def test_a_citation_reference_that_resolves_to_nothing_is_reported(engine) -> None:
    """A citation names a source the reader is meant to be able to follow. One that resolves
    to nothing would be printed as a reference to a record that does not exist, so it is
    reported against the references section rather than emitted."""

    spec = next(s for s in engine.publications().specs if s.citation_refs)
    absent = set(spec.citation_refs)
    composer = PublicationComposer(
        _RefusingResolver(engine.resolver, refuse=absent), engine.formats
    )
    document = composer.compose(spec)

    assert any(e["section"] == "references" for e in document.unresolved)


def test_the_composer_renders_a_document_it_already_composed(engine) -> None:
    """``render_document`` is the second entry point: render something already composed,
    without composing it again. Two paths to one output must agree, or a caller rendering a
    stored document would get different bytes from the one that composed it."""
    spec = engine.publications().specs[0]
    document, body = engine.composer.render(spec)

    assert engine.composer.render_document(document) == body
    assert engine.composer.filename(spec, "area").endswith(
        engine.formats.get(spec.format_id).extension
    )


def test_a_publication_set_answers_for_a_format_it_holds_and_one_it_does_not(engine) -> None:
    """The lookups every consumer reads a publication set through. ``None`` for an absent
    format is the honest answer — a set may legitimately not carry every registered format —
    and only by asking can a caller tell "not generated" from "generated and empty"."""
    publications = engine.publications()
    known = publications.format_ids()[0]

    assert publications.document(known).format_id == known
    assert publications.spec(known).format_id == known
    assert publications.document("test-never-generated") is None
    assert publications.spec("test-never-generated") is None


def test_a_specification_answers_for_one_of_its_sections_and_for_its_content_sections(
    engine,
) -> None:
    """``section`` resolves one key and ``content_sections`` drops the structural ones —
    which is what every validation check that reasons about resolvable content quantifies
    over. Without the filter, a title block would be measured as a section that resolved no
    canonical reference, which is exactly what a title block is supposed to do."""
    spec = engine.publications().specs[0]
    key = spec.section_keys()[0]

    assert spec.section(key).section_key == key
    assert spec.section("test-never-declared") is None

    content = spec.content_sections()
    assert all(not s.structural for s in content)
    assert len(content) <= len(spec.sections)


def test_the_registry_answers_for_its_citations_and_its_registered_classes(engine) -> None:
    """The four accessors a consumer reads the ledger through, none of which had a caller.
    A registry whose contents can only be reached by re-deriving them is one where "was this
    citation registered exactly once" — the knowledge-once claim PV-13 makes — is answerable
    only by rebuilding the thing being checked."""
    registry = engine.registry()
    refs = registry.citation_refs()

    assert refs == tuple(sorted(refs))
    assert all(registry.citation_record_id(ref) for ref in refs)
    assert registry.citation_record_id("ref:never-registered") is None
    assert registry.publication_ids()
    assert registry.format_ids()
    assert len(set(registry.publication_ids())) == len(registry.publication_ids())


def test_a_format_extension_file_beside_the_output_extends_the_registry(
    engine, tmp_path: Path, monkeypatch
) -> None:
    """THE OPENNESS CLAIM, AT THE ENGINE'S OWN BOOTSTRAP.

    `test_format_declaration_file_extends_the_registry` proves the registry can load one;
    this proves the ENGINE looks for one, beside its own output. Without the load the file
    would sit there being silently ignored, and "a format registered from data needs no code
    change" would be true of the registry and false of the only thing that builds it.
    """

    class _Config:
        output_dir = tmp_path

        def __getattr__(self, name: str):
            return getattr(engine.config, name)

    monkeypatch.setattr(engine, "config", _Config())
    assert "test-bootstrapped-brief" not in engine._load_formats().format_ids()

    (tmp_path / FORMAT_EXTENSION_FILE).write_text(
        json.dumps(
            {
                "sections": [
                    {
                        "key": "test-bootstrapped",
                        "label": "Bootstrapped",
                        "rule": {"source": "claims", "ref": "subject_ref"},
                    }
                ],
                "formats": [
                    {
                        "format_id": "test-bootstrapped-brief",
                        "genre": "brief",
                        "label": "Bootstrapped Brief",
                        "sections": ["title-block", "test-bootstrapped", "provenance"],
                        "required": ["title-block", "provenance"],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    extended = engine._load_formats()
    assert "test-bootstrapped-brief" in extended.format_ids()
    assert "test-bootstrapped" in extended.section_keys()


def test_the_gate_is_closed_by_an_upstream_research_verdict(engine, monkeypatch) -> None:
    """PUBLICATION IS DOWNSTREAM OF RESEARCH, and the two upstream outcomes are different.

    A research ABORT is fail-closed: something could not be measured, so this gate aborts
    too and says which upstream line caused it. A research gate that merely CLOSED is a
    verdict, so publication closes with exit 1 rather than aborting. Collapsing them would
    let "research could not run" be reported as "research says no", and an operator would go
    looking for a finding that does not exist.
    """

    monkeypatch.setattr(engine.research, "gate", lambda: (EXIT_ABORT, "research: ABORT | reason"))
    code, line = engine.gate()
    assert code == EXIT_ABORT
    assert "FAIL-CLOSED ABORT" in line
    assert "research: ABORT" in line

    monkeypatch.setattr(engine.research, "gate", lambda: (1, "research: CLOSED | reason"))
    code, line = engine.gate()
    assert code == 1
    assert "upstream research gate closed" in line


def test_the_gate_closes_on_non_deterministic_output_even_when_validation_passes(
    engine, monkeypatch
) -> None:
    """DETERMINISM IS A SEPARATE VERDICT FROM VALIDATION.

    A publication set can satisfy every obligation and still not reproduce, which means the
    bytes depend on something outside the canonical records — the one property the whole
    subsystem is built to guarantee. The gate reports the same line either way, so a reader
    sees the full measurement and the exit code that came from it.
    """
    monkeypatch.setattr(
        engine, "verify_determinism", lambda: {"deterministic": False, "document_mismatches": ["x"]}
    )
    code, line = engine.gate()

    assert code == 1
    assert "deterministic=false" in line


def test_a_section_ordering_a_source_declares_no_order_for_keeps_the_derived_order(
    engine,
) -> None:
    """DETERMINISTIC SELECTION IS THE POINT, and three sources declare an explicit key.

    Claims and standards order by authority, findings by metric key, contributions by area.
    Anything else keeps the order it was derived in — which is already deterministic, because
    it came from a sorted canonical query. Re-sorting it on a key that source does not carry
    would be an ordering that raises rather than one that stabilises.
    """

    records = ("gamma", "alpha", "beta")
    assert PublicationGenerator._ordered("sources", records) == records
    assert PublicationGenerator._ordered("test-unknown-source", records) == records


def test_a_section_rule_may_declare_the_role_its_references_carry(engine) -> None:
    """The role defaults from the SOURCE and a rule may name one explicitly. Without the
    override every section drawing on one source would carry one role, and a format that
    wanted the same records cited differently — as supporting rather than primary — would
    have no way to say so except by adding a source."""

    registry = FormatRegistry()
    registry.register_section(
        {
            "key": "test-supporting",
            "label": "Supporting",
            "rule": {"source": "claims", "ref": "subject_ref", "role": "supporting"},
        }
    )
    registry.register_format(
        {
            "format_id": "test-roled",
            "genre": "test",
            "label": "Roled",
            "sections": ["title-block", "test-supporting", "provenance"],
            "required": ["title-block", "provenance"],
        }
    )
    probe = PublicationIntelligenceEngine(subsystem_config(OUTPUT_DIR, REPO), registry)
    spec = probe.generator.build("test-roled", probe.scope())
    section = spec.section("test-supporting")

    assert section is not None
    assert all(ref.role == "supporting" for ref in section.refs)


def test_pv06_refuses_a_citation_that_traces_to_no_research_record(engine) -> None:
    """A CITATION IS A PROMISE THAT SOMETHING WAS MEASURED.

    It traces either directly to a research record or through the canonical subject that
    record governs, and both routes are tried before it is called untraceable. A citation
    satisfying neither points at nothing — the publication would cite a source no reader
    could reach, which is the one failure a citation cannot survive.
    """

    class _KnowsNothing:
        @staticmethod
        def citable_refs() -> tuple[str, ...]:
            return ()

        @staticmethod
        def record_id_for_ref(_ref: str) -> None:
            return None

    check = _check(_validator(engine, research_registry=_KnowsNothing()), "PV-06")

    assert check.passed is False
    assert check.detail["untraceable"]
    assert check.detail["citations_checked"] > 0


def test_pv07_refuses_one_reference_placed_in_two_sections_of_one_document(engine) -> None:
    """CONTENT IS STATED ONCE AND CROSS-REFERENCED.

    The same canonical reference in two sections of one publication states the same thing
    twice under two headings — the intra-document form of the duplication the whole
    subsystem exists to prevent. The refusal names the first section and the second, so the
    fix is to decide which one owns it.
    """
    publications = engine.publications()
    spec = next(
        s for s in publications.specs if len([sec for sec in s.sections if sec.ref_strings]) >= 2
    )
    sections = [sec for sec in spec.sections if sec.ref_strings]
    borrowed = sections[0].ref_strings[0]
    second = sections[1]
    repeated = replace(
        spec,
        sections=tuple(
            replace(sec, refs=(*sec.refs, replace(sec.refs[0], ref=borrowed)))
            if sec is second
            else sec
            for sec in spec.sections
        ),
    )
    doctored = replace(
        publications, specs=tuple(repeated if s is spec else s for s in publications.specs)
    )

    check = _check(_validator(engine, doctored), "PV-07")
    assert check.passed is False
    duplicated = check.detail["documents_with_repeats"][0]["duplicated"][0]
    assert duplicated["ref"] == borrowed
    assert duplicated["first"] != duplicated["again"]


def test_a_registered_identity_that_diverges_from_the_generated_one_is_refused() -> None:
    """AN IDENTITY IS DERIVED, SO A REGISTERED ONE THAT DIFFERS WAS NOT DERIVED.

    The registry mints each record's id from the record itself and then checks that what the
    ledger holds is that id. A divergence means the ledger carries an identity somebody
    supplied — after which two records could share one id, or one record could be reachable
    under two, and every knowledge-once claim built on the ledger would be about a different
    population than the one generated.
    """

    class _Entry:
        record_id = "PUB-supplied-by-hand"

    with pytest.raises(IdentityDivergenceError) as excinfo:
        PublicationRegistry._require_identity(_Entry(), "PUB-derived-from-content", "publication")

    assert excinfo.value.context["generated_id"] == "PUB-derived-from-content"
    assert excinfo.value.context["registered_id"] == "PUB-supplied-by-hand"
    assert excinfo.value.context["kind"] == "publication"


def test_the_title_subject_skips_candidates_the_canonical_layer_cannot_resolve(engine) -> None:
    """A TITLE ANCHORS THE PUBLICATION, so it must be a subject that actually exists.

    The search is ordered — foundational claims first, then determinations, then
    specification claims, then everything by priority — and at each step a candidate whose
    subject the canonical layer cannot resolve is SKIPPED rather than taken. Without the
    skip the document would be titled after a record nobody can open, which is worse than
    the area-label fallback because it looks like a real citation.

    Both loops are driven: the preferred-class walk and the everything-else walk beneath it.
    """
    scope = engine.scope()
    assert scope.claims, "the scope carries no claims, so this test would prove nothing"

    class _Selective:
        def __init__(self, real, allowed) -> None:
            self._real = real
            self._allowed = allowed

        def exists(self, ref: str) -> bool:
            return ref in self._allowed and self._real.exists(ref)

        def __getattr__(self, name: str):
            return getattr(self._real, name)

    resolvable = [c.subject_ref for c in scope.claims if engine.resolver.exists(c.subject_ref)]
    assert len(resolvable) > 1, "one resolvable subject only; the skip cannot be observed"

    generator = engine.generator
    original = generator.resolver
    try:
        # Only the LAST resolvable subject exists, so every earlier candidate is skipped in
        # whichever loop reaches it first.
        generator.resolver = _Selective(original, {resolvable[-1]})
        assert generator._title_ref(scope) == resolvable[-1]

        # Nothing resolves: both loops run to exhaustion and the honest answer is "".
        generator.resolver = _Selective(original, set())
        assert generator._title_ref(scope) == ""
    finally:
        generator.resolver = original


def test_a_derived_reference_whose_anchor_names_no_target_is_skipped(engine) -> None:
    """A DERIVED REF IS BUILT FROM AN ANCHOR'S TARGET, and an anchor with no target yields
    nothing to build from. Appending a ref with an empty target would produce a reference
    string pointing at the empty subject — which resolves to nothing and would then be
    reported as unresolvable, blaming the resolver for a reference the generator invented.
    """

    class _Anchorless:
        claim_ref = ""
        subject_ref = ""
        claim_class = "foundational-claim"

    class _Scope:
        claims = (_Anchorless(),)

        @staticmethod
        def collection(_source: str):
            return (_Anchorless(),)

    rule = {"source": "claims", "derive_space": "finding", "derive_field": "metric_key"}
    assert engine.generator._candidate_refs(rule, _Scope()) == []

    # And an anchor that DOES name a target still derives one, so the skip is a filter
    # rather than the whole behaviour.
    anchored = next(c for c in engine.scope().claims if c.subject_ref)

    class _Anchored:
        claim_ref = anchored.subject_ref
        subject_ref = anchored.subject_ref
        claim_class = anchored.claim_class

    class _AnchoredScope:
        claims = (_Anchored(),)

        @staticmethod
        def collection(_source: str):
            return (_Anchored(),)

    assert engine.generator._candidate_refs(rule, _AnchoredScope())
