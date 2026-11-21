"""UCOS-URI-001 Research Intelligence validation tests.

Proves the constitutional requirements of the subsystem:
  * deterministic + reproducible: identical state ⇒ byte-identical outputs
  * repository-derived: every count equals the substrate it was read from
  * no duplicate authority: every output declares AUTHORITY = NONE (derived truth)
  * ZERO DUPLICATION: no research record carries canonical prose
  * append-only registry: Knowledge-Once holds and the hash chain recomputes
  * fail-closed: a non-resolving reference is an error, never a substitution

Run: .ec1-venv/bin/python -m pytest intelligence/tests -q
"""

from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

import pytest

from engine.knowledge import (
    CanonicalKnowledgeObject,
    KnowledgeAuthority,
    KnowledgeKind,
    KnowledgeSourceError,
    Lifecycle,
)
from intelligence.kernel.canonical import canonical_json
from intelligence.kernel.config import MemorySink, subsystem_config
from intelligence.kernel.errors import (
    DuplicateRecordError,
    IdentityDivergenceError,
    KnowledgeOnceViolation,
    SubstrateUnavailableError,
    UnresolvedReferenceError,
)
from intelligence.kernel.ids import ArtifactClass, artifact_id, parse_class
from intelligence.kernel.ledger import GENESIS_HASH, LedgerRegistry
from intelligence.research import assimilation, model, registry, standards, validation
from intelligence.research.__main__ import main as cli_main
from intelligence.research.engine import OUTPUT_DIR, ResearchIntelligenceEngine

REPO = subsystem_config(OUTPUT_DIR).repo_root


def _engine() -> ResearchIntelligenceEngine:
    return ResearchIntelligenceEngine(subsystem_config(OUTPUT_DIR, REPO))


@pytest.fixture(scope="module")
def engine() -> ResearchIntelligenceEngine:
    return _engine()


# -- determinism -------------------------------------------------------------


def test_determinism_identical_state_identical_outputs(engine) -> None:
    result = engine.verify_determinism()
    assert result["deterministic"] is True
    assert result["mismatches"] == []


def test_outputs_byte_identical_across_two_sinks() -> None:
    a, b = MemorySink(), MemorySink()
    _engine().write(a)
    _engine().write(b)
    assert a.store.keys() == b.store.keys()
    for name in a.store:
        assert a.store[name] == b.store[name], f"non-deterministic output: {name}"


def test_corpus_is_reproducible(engine) -> None:
    first = canonical_json(engine.corpus().to_dict())
    second = canonical_json(_engine().corpus().to_dict())
    assert first == second


# -- derivation --------------------------------------------------------------


def test_counts_are_derived_not_hardcoded(engine) -> None:
    corpus = engine.corpus()
    canon = json.loads((REPO / "knowledge/canonical-knowledge.json").read_text(encoding="utf-8"))
    closure = json.loads(
        (REPO / "00-MASTER/UAKOS-CLOSURE-002/closure.json").read_text(encoding="utf-8")
    )
    decisions = json.loads((REPO / "knowledge/decisions.json").read_text(encoding="utf-8"))
    assert len(corpus.claims) == canon["count"] + decisions["count"]
    assert sum(c.concept_count for c in corpus.contributions) == closure["concept_total"]
    assert len(corpus.contributions) == len(closure["families"])


def test_findings_carry_evidence_hashes(engine) -> None:
    for finding in engine.corpus().findings:
        assert finding.basis_content_sha256
        assert finding.basis_content_sha256 != "absent"
        assert finding.basis_locator


def test_substrate_inventory_reports_availability(engine) -> None:
    inventory = {row["key"]: row for row in engine.substrate.inventory()}
    assert inventory["canonical-knowledge"]["available"] is True
    assert engine.substrate.missing_required() == []


# -- authority + sealing -----------------------------------------------------


def test_no_duplicate_authority(engine) -> None:
    for payload in engine.outputs().values():
        assert payload["authority"] == "NONE (derived truth)"
        assert payload["programme"] == "UCOS-URI-001"


def test_all_outputs_are_valid_json_and_sealed(engine) -> None:
    for name, payload in engine.outputs().items():
        assert name.endswith(".json")
        reloaded = json.loads(canonical_json(payload))
        assert reloaded["content_hash"] == payload["content_hash"]


# -- zero duplication -------------------------------------------------------


def test_no_research_record_carries_canonical_prose(engine) -> None:
    resolver = engine.resolver
    corpus = engine.corpus()
    for group in (
        corpus.claims,
        corpus.findings,
        corpus.contributions,
        corpus.standards,
        corpus.units,
        corpus.sources,
    ):
        for record in group:
            assert (
                resolver.copied_prose(canonical_json(record.to_dict())) == []
            ), f"canonical prose copied into {type(record).__name__}"


def test_claims_reference_prose_instead_of_storing_it(engine) -> None:
    for claim in engine.corpus().claims:
        payload = claim.to_dict()
        assert claim.claim_ref.startswith(("cko:", "decision:"))
        long_text_fields = {k for k, v in payload.items() if isinstance(v, str) and len(v) > 200}
        assert long_text_fields == set()
        resolved = engine.resolver.resolve(claim.claim_ref)
        assert resolved.text


# -- registry ---------------------------------------------------------------


def test_registry_integrity(engine) -> None:
    integrity = engine.registry().verify()
    assert integrity["chain_intact"] is True
    assert integrity["knowledge_once_holds"] is True
    assert integrity["intact"] is True
    assert integrity["records"] == engine.registry().count()


def test_registry_covers_every_corpus_record(engine) -> None:
    registry = engine.registry()
    assert registry.count() == len(engine.corpus().record_ids())
    for claim in engine.corpus().claims:
        assert registry.get(claim.claim_id) is not None


def test_registry_ids_are_self_describing(engine) -> None:
    for entry in engine.registry().ledger.all():
        assert parse_class(entry.record_id).value == entry.artifact_class


def test_ledger_rejects_duplicate_identity() -> None:
    ledger = LedgerRegistry("TEST", "test-schema")
    assert ledger.head() == GENESIS_HASH
    ledger.register(ArtifactClass.RESEARCH_CLAIM, "k1", {"a": 1})
    with pytest.raises(DuplicateRecordError):
        ledger.register(ArtifactClass.RESEARCH_CLAIM, "k1", {"a": 2})


def test_ledger_rejects_duplicate_content() -> None:
    ledger = LedgerRegistry("TEST", "test-schema")
    ledger.register(ArtifactClass.RESEARCH_CLAIM, "k1", {"a": 1})
    with pytest.raises(KnowledgeOnceViolation):
        ledger.register(ArtifactClass.RESEARCH_CLAIM, "k2", {"a": 1})


def test_identity_is_deterministic_and_order_independent() -> None:
    first = artifact_id(ArtifactClass.RESEARCH_UNIT, "governance")
    second = artifact_id("RESEARCH_UNIT", "governance")
    assert first == second
    assert first.startswith("UCOS-RSCH-")


# -- resolution / fail-closed ------------------------------------------------


def test_unknown_reference_is_an_error_not_a_substitution(engine) -> None:
    with pytest.raises(UnresolvedReferenceError):
        engine.resolver.resolve("cko:UCKO-DOES-NOT-EXIST#statement")
    with pytest.raises(UnresolvedReferenceError):
        engine.resolver.resolve("nonsense-without-a-space")
    with pytest.raises(UnresolvedReferenceError):
        engine.resolver.resolve("metric:not.declared")


def test_every_corpus_reference_resolves(engine) -> None:
    for ref in engine.corpus().all_refs():
        assert engine.resolver.exists(ref), ref


# -- standards analysis -----------------------------------------------------


def test_standards_analysis_is_fail_closed(engine) -> None:
    analysis = engine.standards().model()
    assert analysis["standards_analysed"] == len(engine.corpus().standards)
    assert analysis["conformance_histogram"][model.CONFORMANCE_NON_CONFORMANT] == 0
    assert analysis["external_cross_reference"]["classification"].startswith("CURATED")
    assert analysis["programme_instruments"]["science_registry_count"] > 0


# -- validation + gate ------------------------------------------------------


def test_validation_certifies_the_corpus(engine) -> None:
    report = engine.validation()
    assert report.verdict == "CERTIFIED", [c.check_id for c in report.blocking_failures()]
    assert len(report.checks) == 13
    assert report.exit_code == 0


def test_gate_opens_and_reports_a_seal(engine) -> None:
    code, line = engine.gate()
    assert code == 0
    assert "gate=OPEN" in line
    assert "seal=" in line


# -- write scope ------------------------------------------------------------


def test_engine_writes_only_inside_its_own_directory() -> None:
    written = _engine().write()
    for path in written:
        parts = Path(path).parts
        assert "intelligence" in parts
        assert OUTPUT_DIR in parts, f"write escaped {OUTPUT_DIR}: {path}"


# --------------------------------------------------------------------------- the CLI
#
# ``python -m intelligence.research`` was 55 statements at 0.0%: eight subcommands and three
# documented exit codes, none of which anything executed. The exit codes are asserted as LITERAL
# integers here — a test that compares against the module's own constant passes equally well when
# both are wrong.


def _run(capsys: pytest.CaptureFixture[str], *argv: str) -> tuple[int, str, str]:
    code = cli_main(list(argv))
    captured = capsys.readouterr()
    return code, captured.out, captured.err


def test_every_read_only_subcommand_emits_a_document(capsys: pytest.CaptureFixture[str]) -> None:
    for command in ("corpus", "registry", "standards", "snapshot"):
        code, out, _ = _run(capsys, command)
        assert code == 0, command
        assert json.loads(out), f"{command} emitted an empty document"


def test_the_cli_validation_returns_the_reports_own_verdict(
    capsys: pytest.CaptureFixture[str],
) -> None:
    code, out, _ = _run(capsys, "validate")
    report = json.loads(out)
    assert (code == 0) is (report["gate"] == "OPEN")
    assert code in (0, 1)


def test_the_cli_gate_agrees_with_the_engine_gate(capsys: pytest.CaptureFixture[str]) -> None:
    expected, line = _engine().gate()
    code, out, _ = _run(capsys, "gate")
    assert code == expected
    assert code in (0, 1)
    assert out.strip() == line.strip()


def test_the_cli_verify_proves_deterministic_regeneration(
    capsys: pytest.CaptureFixture[str],
) -> None:
    code, out, _ = _run(capsys, "verify")
    assert code == 0
    assert json.loads(out)["deterministic"] is True


def test_the_cli_build_reports_what_it_wrote(capsys: pytest.CaptureFixture[str]) -> None:
    code, out, _ = _run(capsys, "build")
    assert code == 0
    assert "URI: regenerated" in out
    assert out.count("  - ") >= 1


def test_a_kernel_error_is_a_fail_closed_abort_and_not_a_pass(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """Exit 2 is "no verdict was reachable", and it is not the same answer as a closed gate.

    The condition is FORGED rather than waited for. Every substrate failure this CLI can suffer
    today happens to raise from a lower layer, so the one handler that turns a fail-closed
    condition into the documented exit code was never executed by anything.
    """

    def refuse(self: ResearchIntelligenceEngine) -> None:
        raise SubstrateUnavailableError("the research substrate is unreadable", surface="corpus")

    monkeypatch.setattr(ResearchIntelligenceEngine, "corpus", refuse)
    code, _out, err = _run(capsys, "corpus")
    assert code == 2
    assert "FAIL-CLOSED ABORT" in err
    assert "unreadable" in err, "a refusal that does not say what failed cannot be acted on"


def test_a_directory_that_is_not_a_repository_reaches_no_verdict(tmp_path: Path) -> None:
    """``--repo <empty dir>`` raises out of the knowledge layer rather than returning a code.

    Recorded as an assertion rather than repaired here: the CLI catches ``KernelError``, and the
    substrate it reads raises ``engine.knowledge``'s own taxonomy, so an operator who points the
    tool at the wrong directory gets a traceback where the docstring promises exit 2. Widening
    the handler is a change to the fail-closed contract of every kernel CLI at once, which is a
    decision for the subsystem's owner and not a side effect of a coverage pass.
    """
    with pytest.raises(KnowledgeSourceError):
        cli_main(["--repo", str(tmp_path), "corpus"])


def test_a_subcommand_is_required() -> None:
    with pytest.raises(SystemExit) as raised:
        cli_main([])
    assert raised.value.code == 2


# --------------------------------------------------------------------------- the corpus indexes
#
# `model.ResearchCorpus` publishes five indexes over the assimilated population and nothing called
# any of them. They are the corpus's only read interface for a consumer that wants a SUBSET —
# the publication engine asks for claims by class, a unit asks for its own claims — and an
# index that has never been evaluated is a lookup nobody has checked returns the right rows.


def test_every_corpus_index_selects_from_the_population_it_indexes(engine) -> None:
    corpus = engine.corpus()
    first = corpus.claims[0]

    assert corpus.claim(first.claim_id) is first
    assert corpus.claim("UCOS-RSCH-NO-SUCH-CLAIM") is None

    by_class = corpus.claims_by_class(first.claim_class)
    assert first in by_class
    assert {c.claim_class for c in by_class} == {first.claim_class}
    assert corpus.claims_by_class() == ()

    by_universe = corpus.claims_by_universe(first.universe)
    assert first in by_universe
    assert {c.universe for c in by_universe} == {first.universe}
    assert corpus.claims_by_universe("no-such-universe") == ()

    finding = corpus.findings[0]
    assert finding in corpus.findings_by_class(finding.finding_class)
    assert corpus.findings_by_class() == ()

    unit = corpus.units[0]
    assert corpus.unit(unit.natural_key) is unit
    assert corpus.unit("no-such-area") is None


# --------------------------------------------------------------------------- the registry index
#
# The registry's whole purpose beyond the ledger is CITATION RESOLUTION: it remembers which
# registered record owns a content reference and which one owns a substrate locator, so a
# publication can cite a record rather than restate its content. Both maps were built on every
# run and neither was ever read.


def test_the_registry_resolves_a_citation_back_to_the_record_that_owns_it(engine) -> None:
    registry = engine.registry()

    citable = registry.citable_refs()
    assert citable
    owner = registry.record_id_for_ref(citable[0])
    assert owner is not None
    assert registry.get(owner) is not None
    assert registry.record_id_for_ref("cko:UCKO-DOES-NOT-EXIST#statement") is None

    locators = registry.source_locators()
    assert locators
    source_owner = registry.record_id_for_locator(locators[0])
    assert source_owner is not None
    assert parse_class(source_owner) is ArtifactClass.RESEARCH_SOURCE
    assert registry.record_id_for_locator("no/such/file.json") is None

    unit_ids = registry.unit_ids()
    assert set(unit_ids) == {u.unit_id for u in engine.corpus().units}


def test_an_unregistered_artifact_class_contributes_no_population(engine) -> None:
    """THE REGISTRATION ORDER IS THE POPULATION'S DEFINITION, and the fallthrough is what
    keeps that true.

    ``_register_all`` walks six classes and each has a branch, so the final ``return []``
    cannot be reached from any caller — it answers for a class the registry does not
    populate. Without it a seventh class added to the order would fall off the end of the
    function and register ``None``; with it the answer is "this registry holds none of
    those", which is the honest one and the one the ledger can act on.
    """
    registry = engine.registry()

    assert list(registry._population(ArtifactClass.PUBLICATION)) == []
    assert list(registry._population(ArtifactClass.CITATION)) == []


def test_an_identity_that_diverges_between_assimilation_and_registration_is_refused() -> None:
    """TWO PLACES DERIVE THE SAME ID FROM THE SAME NATURAL KEY, and this is the check that
    they agree.

    Assimilation mints a record's id; the ledger mints it again at registration from the
    natural key the record reports. They cannot disagree for a record built through
    ``from_surface``, which is why the arm was dead — but a record assembled any other way
    would enter the ledger under an id that nothing else in the corpus references, and every
    citation of it would resolve to nothing while the registry reported a clean chain.
    """
    diverged = model.ResearchSource(
        source_id="UCOS-RSCH-SRC-NOT-DERIVED-FROM-THE-KEY",
        substrate_key="canonical-knowledge",
        locator="knowledge/canonical-knowledge.json",
        media="application/json",
        authority="DECLARED",
        role="substrate",
        available=True,
        record_count=1,
        content_sha256="0" * 64,
    )

    with pytest.raises(IdentityDivergenceError) as raised:
        registry.ResearchRegistry(model.ResearchCorpus(sources=(diverged,)))

    assert raised.value.context["assimilated_id"] == diverged.source_id
    assert raised.value.context["registered_id"] != diverged.source_id
    assert raised.value.context["natural_key"] == diverged.natural_key


# --------------------------------------------------------------------------- standards analysis
#
# The repository's own standards all declare their enforcement points, so the analysis reached
# CONFORMANT for every one of them — and `test_standards_analysis_is_fail_closed` asserts the
# NON-CONFORMANT histogram bucket is empty, which is a claim about this repository rather than
# about the verdict. The verdict itself had never been shown to distinguish the three cases.


def _standard(cko_id: str, **fields: object) -> CanonicalKnowledgeObject:
    return CanonicalKnowledgeObject.create(
        cko_id=cko_id,
        kind=KnowledgeKind.STANDARD,
        title="a declared standard",
        statement="a standard is only a standard if something enforces it",
        universe="test",
        authority=KnowledgeAuthority.ENGINEERING,
        owner="test",
        lifecycle=Lifecycle.OPERATIONAL,
        version="1.0.0",
        **fields,
    )


def test_a_reference_resolves_as_an_id_a_concept_or_a_path_and_otherwise_does_not(
    engine,
) -> None:
    """FOUR WAYS TO RESOLVE AND ONE WAY NOT TO — and none of the four had run.

    Every enforcement point in this repository resolves, and the analysis only ever reports
    the verdict, so the predicate underneath it was never evaluated by a test at all. Each
    arm answers a different question: an id names a canonical object or a canonical decision,
    a concept names a closure entry, and everything else is tried as a repository path. The
    order matters — an id is checked before the filesystem — because a canonical id that
    happened to also be a filename would otherwise resolve for the wrong reason.
    """
    resolver = engine.resolver
    obj_id = resolver.objects()[0].cko_id
    concept = next(iter(resolver.concepts()))

    assert standards._resolves(obj_id, resolver) is True
    assert standards._resolves(concept, resolver) is True
    assert standards._resolves("knowledge/canonical-knowledge.json", resolver) is True
    assert standards._resolves("no/such/path/at/all.json", resolver) is False


def test_the_conformance_verdict_separates_indeterminate_from_conformant_and_not(engine) -> None:
    """A STANDARD THAT DECLARES NOTHING IS NOT A STANDARD THAT PASSES.

    Three verdicts, and only INDETERMINATE had ever been produced by a test. The distinction
    the other two carry is the whole point of the analysis: a standard whose enforcement
    reference resolves is CONFORMANT, and one whose reference does not is NON-CONFORMANT
    rather than INDETERMINATE, because a broken enforcement point is a worse finding than an
    absent one — it reads as enforced and enforces nothing.
    """
    resolver = engine.resolver

    silent = standards.analyse_standard(_standard("UCKO-TEST-STANDARD-SILENT"), resolver)
    assert silent.conformance == model.CONFORMANCE_INDETERMINATE
    assert silent.enforcement_refs == ()

    enforced = standards.analyse_standard(
        _standard(
            "UCKO-TEST-STANDARD-ENFORCED",
            evidence=("knowledge/canonical-knowledge.json",),
            certification="knowledge/decisions.json",
        ),
        resolver,
    )
    assert enforced.conformance == model.CONFORMANCE_CONFORMANT
    assert enforced.resolved_enforcement_refs == enforced.enforcement_refs

    broken = standards.analyse_standard(
        _standard(
            "UCKO-TEST-STANDARD-BROKEN",
            evidence=("knowledge/canonical-knowledge.json",),
            validation="evidence/never-produced.json",
        ),
        resolver,
    )
    assert broken.conformance == model.CONFORMANCE_NON_CONFORMANT
    assert broken.unresolved_enforcement_refs == ("evidence/never-produced.json",)


# --------------------------------------------------------------------------- assimilation arms
#
# Assimilation is a projection of whatever the repository happens to hold, and this repository
# holds all of it: every declared surface is present, the coverage report has been produced, and
# no canonical object supersedes another. Each absence below is a REAL state of a clone — a
# fresh checkout before the coverage gate has run, a repository whose closure has not been
# generated — and none of the arms that handle them had ever executed.


def test_an_object_that_supersedes_another_is_superseding_not_prior_art_linked() -> None:
    """THREE NOVELTY VERDICTS AND THEY ARE CHECKED IN ORDER.

    A superseding object almost always also carries knowledge links, so an unordered reading
    would classify it as PRIOR-ART-LINKED — the weaker statement — and the corpus would lose
    the fact that it REPLACES something. No canonical object in this repository supersedes
    another today, which is why the first arm had never been taken.
    """
    superseding = _standard(
        "UCKO-TEST-SUPERSEDES",
        supersedes=("UCKO-TEST-OLD",),
        knowledge_links=("UCKO-TEST-RELATED",),
    )
    linked = _standard("UCKO-TEST-LINKED", knowledge_links=("UCKO-TEST-RELATED",))
    alone = _standard("UCKO-TEST-ALONE")

    assert assimilation._novelty(superseding) == model.NOVELTY_SUPERSEDING
    assert assimilation._novelty(linked) == model.NOVELTY_PRIOR_ART_LINKED
    assert assimilation._novelty(alone) == model.NOVELTY_STANDALONE


def test_an_absent_coverage_report_produces_no_findings_and_is_reported_as_a_gap(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """EMPIRICAL FINDINGS ARE DERIVED FROM THE COVERAGE REPORT OR NOT DERIVED AT ALL.

    ``coverage.xml`` is a generated artifact that a pristine clone does not have until the
    coverage gate has run, and this checkout has one — so the two arms that answer for its
    absence were dead. They are the difference between a corpus that reports "the empirical
    findings are not produced, and here is why" and one that either invents them or crashes
    while reading a file that is not there.
    """
    research = _engine()
    monkeypatch.setattr(type(research.resolver), "coverage", lambda _self: None)
    assimilation = research.assimilation

    assert assimilation._coverage_findings() == []

    gap = next(g for g in assimilation.gaps() if g["substrate_key"] == "coverage-report")
    assert gap["required"] is False
    assert "not produced" in gap["consequence"]


def test_an_unavailable_concept_closure_yields_no_contributions_rather_than_an_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A CONTRIBUTION AREA IS DERIVED FROM THE CLOSURE OR IT IS NOT DERIVED.

    The closure is a declared surface and it is present here, so the guard above the
    derivation had never run. Reading records from an unavailable surface would either raise
    inside a projection whose contract is to survive whatever the repository contains, or
    silently produce zero areas with no signal that the input was missing — the gap register
    is where the absence is reported, and this is what routes it there.
    """
    assimilation = _engine().assimilation
    real_surface = assimilation.substrate.surface

    def unavailable(key: str):
        surface = real_surface(key)
        if key == "concept-closure":
            return replace(surface, available=False)
        return surface

    monkeypatch.setattr(assimilation.substrate, "surface", unavailable)

    assert assimilation.contributions() == ()


# --------------------------------------------------------------------------- the failing checks
#
# Thirteen obligations, and this corpus satisfies all thirteen — so `test_validation_certifies
# _the_corpus` proves the checks PASS on a corpus that passes and says nothing about whether
# any of them can fail. A check that has only ever returned True is not a check; each finding
# arm below is reached with a corpus defective in exactly the one way the check names.


def _validator(engine, corpus, **kwargs: object) -> validation.ResearchValidationEngine:
    return validation.ResearchValidationEngine(corpus, engine.resolver, engine.registry(), **kwargs)


def test_a_reference_that_does_not_resolve_is_reported_as_fabrication(engine) -> None:
    """RV-02 IS THE ANTI-FABRICATION CHECK, and it had only ever been run over refs that
    resolve. The finding names the ref AND the reason, because "something did not resolve" is
    not actionable and "cko:X#statement — no such object" is.
    """
    corpus = engine.corpus()
    fabricated = replace(corpus.claims[0], claim_ref="cko:UCKO-INVENTED-BY-A-TEST#statement")
    check = _validator(engine, replace(corpus, claims=(fabricated,)))._rv02()

    assert check.passed is False
    assert check.detail["unresolved"][0]["ref"] == "cko:UCKO-INVENTED-BY-A-TEST#statement"
    assert check.detail["unresolved"][0]["reason"]


def test_a_closure_that_declares_no_total_makes_the_reconciliation_indeterminate(
    engine, monkeypatch: pytest.MonkeyPatch
) -> None:
    """RV-07 RECONCILES AGAINST A DECLARED TOTAL, and without one there is nothing to
    reconcile against. The verdict is None — indeterminate — rather than a pass, because a
    check that passes when its reference value is missing would certify the corpus on the
    strength of the closure having said nothing.
    """
    real_payload = engine.resolver.substrate.payload

    def silent(key: str):
        return {} if key == "concept-closure" else real_payload(key)

    monkeypatch.setattr(engine.resolver.substrate, "payload", silent)
    check = _validator(engine, engine.corpus())._rv07()

    assert check.passed is None
    assert "does not declare concept_total" in check.detail["reason"]


def test_a_record_carrying_canonical_prose_is_a_zero_duplication_violation(engine) -> None:
    """RV-09 IS ZERO DUPLICATION ENFORCED MECHANICALLY, and its violation arm had no case.

    A research record may reference canonical prose and may never carry it, because a copy is
    a second authority that drifts from the first the moment either is edited. The violation
    names the group, the field and the canonical object the prose was copied FROM, so the
    finding points at both ends of the duplication rather than only at the copy.
    """
    corpus = engine.corpus()
    prose = engine.resolver.resolve(corpus.claims[0].claim_ref).text
    copied = replace(corpus.units[0], area_label=prose)
    check = _validator(engine, replace(corpus, units=(copied,)))._rv09()

    assert check.passed is False
    violation = check.detail["violations"][0]
    assert violation["group"] == "units"
    assert violation["field"] == "area_label"
    assert violation["copied_from"]


def test_determinism_is_indeterminate_when_no_second_assimilation_is_supplied(engine) -> None:
    """RV-10 NEEDS A WITNESS, and a validator constructed without one cannot produce it.

    The engine always supplies a re-assimilation callable, so the arm that answers for its
    absence was dead — and it is the arm that keeps the validator usable standalone, over a
    corpus handed to it rather than one it can regenerate. Answering None says the property
    was not examined; answering True would claim determinism was proven by not testing it.
    """
    check = _validator(engine, engine.corpus(), reassimilate=None)._rv10()

    assert check.passed is None
    assert check.check_id == "RV-10"


def test_a_unit_naming_an_unregistered_member_is_dangling(engine) -> None:
    """RV-12 IS THE MEMBERSHIP CHECK READ FROM THE UNIT END.

    RV-13 asks whether every record belongs to a unit; RV-12 asks whether every member a unit
    NAMES is a registered record. They are not the same question, and only RV-12 catches a
    unit that lists an id nothing holds — a member that renders as a citation to a record
    that was never registered.
    """
    corpus = engine.corpus()
    dangling = replace(corpus.units[0], claim_ids=("UCOS-RSCH-CLM-NEVER-REGISTERED",))
    check = _validator(engine, replace(corpus, units=(dangling,)))._rv12()

    assert check.passed is False
    assert check.detail["dangling"][0]["unit_id"] == dangling.unit_id
    assert check.detail["dangling"][0]["missing"] == ["UCOS-RSCH-CLM-NEVER-REGISTERED"]


# --------------------------------------------------------------------------- the gate's other codes
#
# `test_gate_opens_and_reports_a_seal` proves the gate opens on a healthy repository. The two
# arms that answer for an unhealthy one — the only two the docstring promises — had never run.


def test_a_missing_required_surface_aborts_the_gate_before_any_verdict(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """EXIT 2 IS NOT A CLOSED GATE, and reaching it early is the whole point.

    A required substrate surface is the input the verdict would be derived FROM, so with one
    missing there is no verdict to reach — validating anyway would produce a CLOSED gate that
    reads as "the corpus failed" when the truth is "the corpus could not be read". The abort
    line names the surfaces so an operator knows what to restore.
    """
    engine = _engine()
    monkeypatch.setattr(
        type(engine.substrate), "missing_required", lambda _self: ["canonical-knowledge"]
    )

    code, line = engine.gate()

    assert code == 2
    assert "FAIL-CLOSED ABORT" in line
    assert "canonical-knowledge" in line


def test_a_non_deterministic_assimilation_closes_the_gate_that_validation_would_open(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """DETERMINISM IS A GATE CONDITION IN ITS OWN RIGHT, not a line in the report.

    Validation can certify a corpus that is not reproducible — every check would pass over
    the one assimilation it was handed — so the gate re-asks the question and closes on a
    negative answer regardless of the verdict. The line is still emitted, with
    ``deterministic=false`` in it, so the code arrives with its reason attached.
    """
    engine = _engine()
    monkeypatch.setattr(
        type(engine),
        "verify_determinism",
        lambda _self: {"deterministic": False, "mismatches": ["research-model.json"]},
    )

    code, line = engine.gate()

    assert code == 1
    assert "deterministic=false" in line
    assert "seal=" in line
