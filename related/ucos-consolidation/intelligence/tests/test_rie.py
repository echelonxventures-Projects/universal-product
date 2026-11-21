"""RIE validation tests.

Proves the constitutional requirements:
  * deterministic + reproducible: identical state ⇒ identical outputs
  * repository-derived: reported facts equal the evidence sources (not hardcoded)
  * no duplicate authority: every output declares AUTHORITY = NONE (derived truth)
  * composition: the engine reads existing evidence, produces only additive JSON

Run: .ec1-venv/bin/python -m pytest intelligence/tests -q
"""

from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

import pytest

from intelligence.rie import census, discovery, drift
from intelligence.rie.__main__ import main as cli_main
from intelligence.rie.canonical import canonical_json, sha256_file, sha256_text
from intelligence.rie.config import MemorySink, RepoConfig, resolve_repo_root
from intelligence.rie.engine import RepositoryIntelligenceEngine, build_model
from intelligence.rie.evidence import EvidenceReader

REPO = RepoConfig.create().repo_root


def _engine() -> RepositoryIntelligenceEngine:
    return RepositoryIntelligenceEngine(RepoConfig.create(REPO))


def test_determinism_identical_state_identical_outputs() -> None:
    eng = _engine()
    result = eng.verify_determinism()
    assert result["deterministic"] is True
    assert result["mismatches"] == []


def test_outputs_byte_identical_across_two_sinks() -> None:
    a, b = MemorySink(), MemorySink()
    _engine().write(a)
    _engine().write(b)
    assert a.store.keys() == b.store.keys()
    for name in a.store:
        assert a.store[name] == b.store[name], f"non-deterministic output: {name}"


def test_repository_derived_not_hardcoded() -> None:
    """Reported corpus/coverage equal the evidence files (proves derivation)."""
    eng = _engine()
    model = eng.model()
    ct = json.loads((REPO / "00-BOOK/DATA/control-tower.json").read_text(encoding="utf-8"))
    assert model["health"]["corpus"]["artifacts"] == ct["portfolio"]["total_artifacts"]
    assert model["health"]["corpus"]["edges"] == ct["portfolio"]["total_edges"]
    cert = json.loads((REPO / "00-BOOK/DATA/certification.json").read_text(encoding="utf-8"))
    assert model["health"]["certification"]["digital_twin_verdict"] == cert["verdict"]


def test_no_duplicate_authority() -> None:
    for payload in _engine().outputs().values():
        assert payload["authority"] == "NONE (derived truth)"


def test_all_outputs_are_valid_json_and_sealed() -> None:
    for name, payload in _engine().outputs().items():
        assert name.endswith(".json")
        text = canonical_json(payload)
        reloaded = json.loads(text)
        assert reloaded["content_hash"] == payload["content_hash"]


def test_rib_is_a_generated_output() -> None:
    outputs = _engine().outputs()
    assert "UCOS-IMP-BASELINE-001.rib.json" in outputs
    assert outputs["UCOS-IMP-BASELINE-001.rib.json"]["artifact_id"] == "UCOS-IMP-BASELINE-001"


def test_engine_writes_only_under_intelligence_dir(tmp_path: Path) -> None:
    """Writes are contained under the configured intelligence directory.

    Proven in two halves, neither of which touches Repository Truth:

      (a) the DEFAULT output directory is under ``intelligence/`` — asserted without
          writing anything, because the location of a directory is a property of the
          configuration, not of a file that must exist;
      (b) an ACTUAL write is contained by the directory it was configured with — proven
          against a temporary output root, with the real reader and the real model, so
          the write path is exercised rather than mocked.

    Both halves were previously one line that called ``write()`` against the live
    repository. It proved the property and, on every certification run, rewrote four
    tracked artifacts — UCOS-RIE-MODEL, UCOS-RIE-HEALTH, UCOS-RIE-CAPABILITY-CATALOG and
    UCOS-IMP-BASELINE-001.rib — so ``./verify.sh --full`` could not certify the tree it
    had measured. A certification that edits what it certifies is not an observation.
    """
    assert "intelligence" in RepoConfig.create(REPO).output_dir.parts

    sandbox = tmp_path / "intelligence"
    engine = RepositoryIntelligenceEngine(replace(RepoConfig.create(REPO), output_dir=sandbox))
    written = engine.write()
    assert written, "the engine wrote nothing, so containment is vacuous"
    for path in written:
        assert "intelligence" in Path(path).parts, f"write escaped intelligence/: {path}"
        assert Path(path).parent == sandbox, f"write escaped its configured directory: {path}"


# ---------------------------------------------------------------------------
# UCOS-P0-FCL-002-FIX-001 — coverage isolation regression tests
#
# coverage.xml is TEST_EXECUTION_STATE / QUALITY_MEASUREMENT: an environmental
# output of the test runner that is absent from every pristine clone (the bootstrap
# never runs the test suite). Including it in the canonical identity fingerprint
# caused every clone regeneration to produce a different input_hash and therefore a
# different catalog SHA256, making Phase-9 pristine-clone certification
# irreproducible across all four variance dimensions:
#   registry_variance / ordering_variance / certification_variance / dictionary_variance
#
# Fix: coverage_measurement is excluded from state_fingerprint(). That closed the
# fingerprint route only; UCOS-CL-005 below closes the remaining route through
# analysis.py and asserts the invariant over the serialized canonical model.
# ---------------------------------------------------------------------------


def test_canonical_identity_independent_of_coverage() -> None:
    """UCOS-P0-FCL-002-FIX-001: coverage.xml must not influence canonical artifact identity.

    Three invariants proven:
      (a) structural  — coverage_measurement absent from state_fingerprint() keys
      (b) input domain — state_fingerprint() contains exactly the 5 canonical DATA files
      (c) behavioral  — input_hash is stable across re-derivations (no coverage leakage)
    """

    config = RepoConfig.create(REPO)
    reader = EvidenceReader(config)
    fp = reader.state_fingerprint()

    # (a) coverage_measurement must not be a top-level key in the fingerprint
    assert "coverage_measurement" not in fp, (
        "coverage_measurement must not appear in state_fingerprint() — "
        "it is TEST_EXECUTION_STATE and must not influence canonical artifact identity"
    )

    # (b) the only key is evidence_files, mapping exactly the 5 canonical DATA files
    assert set(fp.keys()) == {
        "evidence_files"
    }, f"state_fingerprint() must contain only 'evidence_files', got: {set(fp.keys())}"
    expected_files = {
        "00-BOOK/DATA/control-tower.json",
        "00-BOOK/DATA/artifacts.json",
        "00-BOOK/DATA/certification.json",
        "00-BOOK/DATA/twin.json",
        "00-BOOK/DATA/volumes.json",
    }
    assert set(fp["evidence_files"].keys()) == expected_files, (
        f"evidence_files keys mismatch.\n"
        f"  expected: {sorted(expected_files)}\n"
        f"  got:      {sorted(fp['evidence_files'].keys())}"
    )

    # (c) input_hash is stable across re-derivations — no wall-clock or env leakage
    h1 = reader.generation_state()["input_hash"]
    reader._cache.pop("generation_state", None)  # force re-derivation
    h2 = reader.generation_state()["input_hash"]
    assert h1 == h2, (
        f"input_hash is not stable across calls: {h1!r} != {h2!r}\n"
        "A non-deterministic input (coverage, wall-clock, environment) has leaked "
        "back into canonical identity."
    )


# ---------------------------------------------------------------------------
# UCOS-CL-005 — canonical identity is invariant under environmental state.
#
# The two tests above assert the SHAPE of state_fingerprint(). That is necessary
# but not sufficient, and it is not what the architecture promises. Neither of
# them fails while coverage still reaches canonical output bytes by another
# route, which is exactly what happened: be46a300 removed coverage from the
# fingerprint while analysis.py went on writing coverage_line_pct into
# health.code, so the model digest still moved with coverage.xml and Phase-9
# variance survived the fix that was supposed to remove it.
#
# The test below is the invariant itself, asserted at the boundary where it is
# claimed to hold: the serialized canonical model. It compares a build that can
# see coverage.xml against a build that cannot, which is precisely the
# difference between this working tree and a pristine clone.
# ---------------------------------------------------------------------------


def _model_without_coverage() -> dict:
    """The canonical model as a pristine clone derives it — no coverage.xml on disk."""
    base = RepoConfig.create(REPO)
    absent = replace(base, coverage_xml=REPO / "__absent__" / "coverage.xml")
    assert not absent.coverage_xml.exists(), "fixture must point at a non-existent path"
    return build_model(EvidenceReader(absent))


def test_canonical_model_bytes_invariant_under_coverage_presence() -> None:
    """UCOS-CL-005: coverage.xml must not change one byte of canonical output.

    coverage.xml is TEST_EXECUTION_STATE: gitignored, environmental, and absent from
    every pristine clone because the bootstrap never runs the suite. If it reaches the
    canonical model, the same commit yields different artifact bytes in the clone than
    in a working tree where tests have run — which is irreproducibility, measured by
    Phase-9 as registry / ordering / certification / dictionary variance.

    Asserted over the serialized bytes rather than over any single field, so the whole
    class is covered rather than the one field that happened to leak.
    """
    with_coverage = build_model(EvidenceReader(RepoConfig.create(REPO)))
    without_coverage = _model_without_coverage()

    a, b = canonical_json(with_coverage), canonical_json(without_coverage)
    if a != b:
        diff = [
            k
            for k in set(with_coverage) | set(without_coverage)
            if with_coverage.get(k) != without_coverage.get(k)
        ]
        raise AssertionError(
            "canonical model bytes changed with coverage.xml presence — an environmental "
            f"input has reached canonical identity. Divergent top-level sections: {sorted(diff)}"
        )


def test_canonical_identity_hashes_invariant_under_coverage_presence() -> None:
    """The derived identities must be invariant for the same reason as the bytes.

    input_hash was already fixed at be46a300; content identity was not. Both are
    asserted here so a future change cannot repair one and regress the other.
    """
    with_coverage = build_model(EvidenceReader(RepoConfig.create(REPO)))
    without_coverage = _model_without_coverage()

    assert (
        with_coverage["generation"]["input_hash"] == without_coverage["generation"]["input_hash"]
    ), "input_hash moved with coverage.xml presence"

    assert sha256_text(canonical_json(with_coverage)) == sha256_text(
        canonical_json(without_coverage)
    ), "canonical content hash moved with coverage.xml presence"


def test_no_canonical_output_carries_a_coverage_field() -> None:
    """Structural backstop: no coverage-derived key may appear anywhere in the model.

    The byte test above catches a leak only when the two builds actually differ. A
    coverage field that happens to hold the same value in both builds — an absent
    coverage.xml on a machine that never ran tests, say — would slip past it. This
    closes that gap by forbidding the key outright, at any depth.
    """
    model = build_model(EvidenceReader(RepoConfig.create(REPO)))
    forbidden = (
        "coverage_line_pct",
        "coverage_branch_pct",
        "coverage_measurement",
        "lines_covered",
        "lines_valid",
        "coverage_full",
    )
    found: list[str] = []

    def walk(node: object, path: str) -> None:
        if isinstance(node, dict):
            for key, value in node.items():
                if key in forbidden:
                    found.append(f"{path}.{key}")
                walk(value, f"{path}.{key}")
        elif isinstance(node, list):
            for i, value in enumerate(node):
                walk(value, f"{path}[{i}]")

    walk(model, "model")
    assert not found, (
        "canonical model carries coverage-derived fields, which makes its identity a "
        f"function of test-execution state: {found}"
    )


# --------------------------------------------------------------------------- the CLI
#
# ``python -m intelligence.rie`` was 62 units at 0.0%, and the cost of that was not academic:
# ``answer`` — one of the five subcommands its own docstring documents — raised
# ``KeyError: 'coverage_line_pct'`` on every invocation. UCOS-CL-005 correctly removed that key
# from the canonical model (see the four tests above); the projection that read it was never
# updated, and nothing executed the projection, so a broken documented command shipped.
#
# Each test below therefore calls ``main`` with the argv an operator would type, and the first
# one asserts the whole answer document is serialisable rather than only that the call returned 0.


def _run(capsys, *argv: str) -> tuple[int, str]:  # noqa: ANN001 - pytest fixture type
    code = cli_main(list(argv))
    return code, capsys.readouterr().out


def test_the_answer_subcommand_answers_instead_of_raising(capsys) -> None:  # noqa: ANN001
    """The regression witness for ``KeyError: 'coverage_line_pct'``."""
    code, out = _run(capsys, "answer")
    assert code == 0
    answers = json.loads(out)
    assert set(answers) == {
        "what_exists",
        "what_is_implemented",
        "what_remains",
        "what_is_blocked",
        "what_is_executable",
        "critical_path",
        "current_repository_state",
        "is_aeos_ready",
    }
    assert "coverage" not in canonical_json(answers), (
        "the answer document must not quote a coverage figure: coverage.xml is "
        "TEST_EXECUTION_STATE, so an answer carrying it would differ in a pristine clone"
    )
    assert answers["what_is_implemented"].startswith("engine EC-1 + platform EC-2")


def test_the_snapshot_subcommand_emits_the_sealed_snapshot(capsys) -> None:  # noqa: ANN001
    code, out = _run(capsys, "snapshot")
    assert code == 0
    snapshot = json.loads(out)
    assert snapshot["authority"] == "NONE (derived truth)"
    assert snapshot["content_hash"] == _engine().outputs()["UCOS-RIE-SNAPSHOT.json"]["content_hash"]


def test_the_verify_subcommand_returns_the_determinism_verdict(capsys) -> None:  # noqa: ANN001
    code, out = _run(capsys, "verify")
    result = json.loads(out)
    assert (code == 0) is (result["deterministic"] is True), (
        "the exit code must be the report's own verdict; deciding it separately would let the "
        "shell and the document disagree about one run"
    )
    assert code == 0


def test_the_build_subcommand_writes_into_the_repo_it_is_given(
    tmp_path: Path,
    capsys,  # noqa: ANN001
) -> None:
    """``--repo`` is honoured, so the build is provable without touching Repository Truth.

    ``build`` against the live tree would rewrite four tracked artifacts mid-certification —
    the defect ``test_engine_writes_only_under_intelligence_dir`` above exists to prevent — so
    the subcommand is exercised against a copy of the evidence the engine reads.
    """
    for relative in (
        "00-BOOK/DATA/control-tower.json",
        "00-BOOK/DATA/artifacts.json",
        "00-BOOK/DATA/certification.json",
        "00-BOOK/DATA/twin.json",
        "00-BOOK/DATA/volumes.json",
    ):
        target = tmp_path / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((REPO / relative).read_bytes())

    code, out = _run(capsys, "--repo", str(tmp_path), "build")
    assert code == 0
    assert "RIE: regenerated" in out
    assert out.count("  - ") >= 1, "a build that names no artifact reports nothing"
    written = sorted(p.name for p in (tmp_path / "intelligence").rglob("*.json"))
    assert written, "the build reported outputs it did not write"
    assert not list((REPO / "intelligence").glob("__absent__")), "sanity: no stray write path"


def test_the_portal_subcommand_generates_pages_where_it_is_told(
    tmp_path: Path,
    capsys,  # noqa: ANN001
) -> None:
    out_dir = tmp_path / "portal"
    code, out = _run(capsys, "portal", "--out", str(out_dir))
    assert code == 0
    assert "RIE portal: generated" in out
    pages = sorted(p.name for p in out_dir.iterdir())
    assert pages, "the portal reported pages it did not write"
    for page in pages:
        assert f"  - {page}" in out, f"{page} was written but not reported"


def test_an_explicit_repo_root_is_resolved_rather_than_assumed(capsys) -> None:  # noqa: ANN001
    """``--repo .`` must reach the same snapshot as the auto-resolved default."""
    code, explicit = _run(capsys, "--repo", str(REPO), "snapshot")
    assert code == 0
    code, implicit = _run(capsys, "snapshot")
    assert code == 0
    assert json.loads(explicit)["content_hash"] == json.loads(implicit)["content_hash"]


def test_a_subcommand_is_required() -> None:
    with pytest.raises(SystemExit) as raised:
        cli_main([])
    assert raised.value.code == 2, "argparse.error exits 2; a caller must not read it as a pass"


# --------------------------------------------------------------------------- the evidence reader
#
# Every test above reads the model the engine derived, so the reader underneath it was
# exercised only through the surfaces the model happens to use. Git answers here, the
# coverage report has been produced, and every source file parses — so each arm that answers
# for a repository where one of those is false had never run.


def _reader() -> EvidenceReader:
    return EvidenceReader(RepoConfig.create(REPO))


def test_every_git_fact_the_reader_reports_comes_from_git() -> None:
    """FOUR GIT READERS AND NONE OF THEM HAD A CALLER IN THIS SUITE.

    The commit, the short commit, the committer date and the branch are what bind a derived
    output to the source state it was derived at — the generation timestamp is taken from the
    commit precisely so that regenerating an unchanged repository produces identical bytes.
    Each answers ``UNKNOWN`` rather than raising when git cannot say, because an
    observational surface must degrade rather than abort.
    """
    reader = _reader()

    assert reader.head_commit().startswith(reader.head())
    assert len(reader.head_commit()) == 40
    assert reader.head_committed_at()[:2] == "20"
    assert reader.branch()
    assert reader.twin() == reader.data("twin.json")


def test_a_repository_git_cannot_read_reports_unknown_rather_than_raising(tmp_path) -> None:
    """GIT IS NOT A DEPENDENCY OF BEING ABLE TO ANSWER.

    Every git read goes through one runner that returns the empty string when the process
    cannot be started at all, and each reader turns that into ``UNKNOWN``. Letting the OSError
    escape would make the whole intelligence surface unavailable on a machine without git,
    for facts that are provenance rather than content.
    """
    config = RepoConfig.create(tmp_path)
    reader = EvidenceReader(replace(config, repo_root=tmp_path / "never-created"))

    assert reader.head() == "UNKNOWN"
    assert reader.head_commit() == "UNKNOWN"
    assert reader.head_committed_at() == "UNKNOWN"
    assert reader.branch() == "UNKNOWN"
    assert reader.tracked("*.py") == []


def test_coverage_is_read_when_present_and_reported_unavailable_when_it_is_not(
    tmp_path, monkeypatch
) -> None:
    """COVERAGE IS ENVIRONMENTAL, and all three of its answers matter.

    ``coverage.xml`` is gitignored, produced by the test runner and absent from every
    pristine clone — so "no report" is the NORMAL state, not an error, and the reader
    degrades to unavailable rather than aborting a caller that is not asking about coverage.
    An unreadable report degrades the same way, because an environmental artifact that
    cannot be parsed must never take down an observational surface.

    THE PRESENT CASE BUILDS ITS OWN REPORT, AND THE DOCSTRING ABOVE IS WHY. It used to read
    the repository's own coverage.xml and assert it was there, which asserts the presence of
    exactly the environmental artifact this test exists to say may be absent. It passed on
    any machine that had run the suite before and failed on a pristine checkout: measured in
    CI, shard 1 of a sharded --full run, where every shard writes its coverage data to a
    private path OUTSIDE the repository and the combined report is emitted later, so
    coverage.xml genuinely did not exist yet. A fixture makes the assertion about the READER,
    which is the subject, rather than about whether someone has run the tests here before.
    """
    report = tmp_path / "present" / "coverage.xml"
    report.parent.mkdir()
    report.write_text(
        '<coverage line-rate="0.94" branch-rate="0.88" lines-covered="47" '
        'lines-valid="50" branches-covered="22" branches-valid="25"/>',
        encoding="utf-8",
    )
    present = EvidenceReader(RepoConfig.create(report.parent)).coverage()
    assert present.available is True
    assert present.lines_valid > 0

    absent = EvidenceReader(RepoConfig.create(tmp_path)).coverage()
    assert absent.available is False
    assert absent.lines_valid == 0

    malformed = tmp_path / "coverage.xml"
    malformed.write_text("<not-cobertura/>", encoding="utf-8")
    unreadable = EvidenceReader(RepoConfig.create(tmp_path)).coverage()
    assert unreadable.available is False


def test_a_file_that_is_absent_hashes_to_a_stable_sentinel(tmp_path) -> None:
    """AN ABSENT FILE HAS A CONTENT HASH AND IT IS NOT A HASH OF NOTHING.

    Returning the digest of the empty string would make "the file is missing" and "the file
    is empty" the same evidence value. ``absent`` is a sentinel no digest can collide with,
    so a snapshot records which of the two it saw.
    """
    written = tmp_path / "present.json"
    written.write_text("{}", encoding="utf-8")

    assert sha256_file(tmp_path / "never-written.json") == "absent"
    assert sha256_file(written) != "absent"


def test_a_path_outside_the_repository_is_rendered_whole(tmp_path) -> None:
    """A RELATIVE RENDER OF AN UNRELATED PATH WOULD BE A LIE ABOUT WHERE IT IS.

    Every path this engine renders lies inside the repository, so the fallback had no case.
    A path outside it has no repository-relative form, and inventing one with ``..``
    components would produce a string that reads like a repository location and is not one.
    """
    config = RepoConfig.create(REPO)

    assert config.rel(REPO / "engine" / "uckp") == "engine/uckp"
    assert config.rel(tmp_path / "elsewhere") == str(tmp_path / "elsewhere")


def test_the_repository_root_falls_back_when_no_marker_is_found(tmp_path) -> None:
    """THE MARKERS ARE THE ANSWER AND THE PACKAGE'S OWN LOCATION IS THE LAST RESORT.

    Resolution walks upward looking for the evidence markers, and it finds them from
    anywhere inside this repository — so the fallback had never run. It answers for a start
    path outside any repository at all, where returning None or raising would leave a caller
    with no root rather than with the one this package is installed under.
    """
    assert resolve_repo_root(REPO / "intelligence" / "rie") == REPO
    assert resolve_repo_root(tmp_path) == REPO


# --------------------------------------------------------------------------- drift
#
# Drift is the one derivation that depends on a PRIOR snapshot, and this repository's
# `.runtime` directory holds none while the suite runs — so every drift call took the
# baseline arm and the whole comparison was unmeasured.


def _model(*, capabilities=(), verdict="CERTIFIED", domains=1, edges=10) -> dict:
    return {
        "capabilities": [
            {"canonical_name": name, "implementation_status": status}
            for name, status in capabilities
        ],
        "health": {
            "certification": {"digital_twin_verdict": verdict, "domains": domains},
            "corpus": {"edges": edges},
        },
    }


def test_with_no_prior_snapshot_drift_reports_a_baseline_rather_than_change() -> None:
    report = drift.detect(_model(capabilities=[("engine.alpha", "IMPLEMENTED")]), None)

    assert report["baseline"] is True
    assert report["implementation_drift"] == []
    assert report["certification_drift"] == []
    assert report["dependency_drift"] == []


def test_every_kind_of_change_between_two_snapshots_is_named(tmp_path) -> None:
    """FOUR COMPARISONS, NONE OF WHICH HAD EVER RUN, and each says something different.

    A capability that appears is ADDED; one whose status moves is a STATUS change carrying
    both ends; one that disappears is REMOVED carrying what it was. Reporting the first two
    and not the third would make a capability's disappearance invisible — the one change a
    reader most needs to see. Certification drift is reported per FIELD, so a verdict change
    and a domain-count change are separate findings rather than one "certification changed".
    And the comparison is keyed on the canonical NAME rather than on the catalogue ordinal,
    because inserting a capability shifts every later id and a report keyed on it would
    attribute the change to the wrong capability.
    """
    was = _model(
        capabilities=[("engine.gone", "IMPLEMENTED"), ("engine.moved", "PARTIAL")],
        verdict="CERTIFIED",
        domains=3,
        edges=10,
    )
    now = _model(
        capabilities=[("engine.moved", "IMPLEMENTED"), ("engine.new", "PARTIAL")],
        verdict="REFUSED",
        domains=4,
        edges=11,
    )

    report = drift.detect(now, was)

    assert report["baseline"] is False
    assert report["implementation_drift"] == [
        {"capability": "engine.moved", "change": "STATUS", "from": "PARTIAL", "to": "IMPLEMENTED"},
        {"capability": "engine.new", "change": "ADDED", "status": "PARTIAL"},
        {"capability": "engine.gone", "change": "REMOVED", "was": "IMPLEMENTED"},
    ]
    assert report["certification_drift"] == [
        {"field": "digital_twin_verdict", "from": "CERTIFIED", "to": "REFUSED"},
        {"field": "domains", "from": 3, "to": 4},
    ]
    assert report["dependency_drift"] == [{"metric": "corpus_edges", "from": 10, "to": 11}]


def test_two_identical_snapshots_produce_no_drift_at_all() -> None:
    """A comparison that always finds something is not a comparison. The equal case is what
    makes a drift report readable: an unchanged repository must produce three empty lists,
    or every run would report noise and the real changes would stop standing out.
    """
    same = _model(capabilities=[("engine.alpha", "IMPLEMENTED")])

    report = drift.detect(same, dict(same))

    assert report["implementation_drift"] == []
    assert report["certification_drift"] == []
    assert report["dependency_drift"] == []


def test_a_prior_snapshot_that_cannot_be_parsed_is_treated_as_no_prior(tmp_path) -> None:
    """AN UNREADABLE PRIOR IS A BASELINE, NEVER A FAULT.

    The snapshot is the engine's own previous output, and a truncated or hand-edited one is
    a real state. Raising would make the engine unable to produce a model at all because of
    a file that only affects the drift section; reporting it as a baseline says "there is
    nothing to compare against", which is exactly the truth.
    """
    config = RepoConfig.create(tmp_path, output_subdir="out")
    engine = RepositoryIntelligenceEngine(config)
    assert engine._prior_model() is None

    config.output_dir.mkdir(parents=True, exist_ok=True)
    (config.output_dir / "UCOS-RIE-MODEL.json").write_text("{ truncated", encoding="utf-8")

    assert engine._prior_model() is None


# --------------------------------------------------------------------------- discovery + census
#
# Both walk the repository through git, over source files that all parse. The arms below
# answer for a checkout git cannot enumerate and for paths that cannot be read as Python —
# which is what "derive the catalogue from whatever is there" means in practice.


def _untracked_repo(tmp_path: Path, root: str) -> tuple[EvidenceReader, Path]:
    """A reader over a directory git does not track, so every ``tracked`` call is empty."""
    base = tmp_path / root
    base.mkdir(parents=True)
    return EvidenceReader(RepoConfig.create(tmp_path, code_roots=(root,))), base


def test_a_module_that_cannot_be_parsed_contributes_no_docstring(tmp_path: Path) -> None:
    """A CATALOGUE ENTRY IS DESCRIBED BY ITS PACKAGE DOCSTRING OR BY NOTHING.

    Every tracked ``__init__.py`` in this repository parses, so the failure arm had no case.
    A file that is not valid Python, or a path that is not a readable file at all, must
    contribute an empty description rather than aborting discovery — a catalogue that cannot
    be built because one package has a syntax error answers no question at all.
    """
    broken = tmp_path / "__init__.py"
    broken.write_text("def (:\n", encoding="utf-8")
    assert discovery._docstring(broken) == ""
    assert discovery._docstring(tmp_path / "not-a-file") == ""

    good = tmp_path / "good.py"
    good.write_text('"""A described package."""\n', encoding="utf-8")
    assert discovery._docstring(good) == "A described package."


def test_a_tracked_file_that_cannot_be_parsed_contributes_no_symbols(tmp_path: Path) -> None:
    """THE SYMBOL SURFACE IS WHAT PARSES, and the file that does not is skipped rather than
    fatal — but its STEM is still recorded, because the module exists whether or not this
    reader can read it. Dropping the file entirely would understate the surface; raising
    would make one unparseable module cost the whole catalogue.
    """
    reader, base = _untracked_repo(tmp_path, "pkg")
    (base / "sound.py").write_text("class Alpha: pass\ndef beta(): pass\ndef _private(): pass\n")
    (base / "broken.py").write_text("def (:\n", encoding="utf-8")

    class _Tracking:
        config = reader.config

        @staticmethod
        def tracked(_pattern: str) -> list[str]:
            return ["pkg/sound.py", "pkg/broken.py"]

    symbols = discovery._symbols(_Tracking(), "pkg")

    assert "Alpha" in symbols and "beta" in symbols
    assert "_private" not in symbols
    assert "broken" in symbols and "sound" in symbols


def test_package_locations_fall_back_to_the_filesystem_when_git_lists_nothing(
    tmp_path: Path,
) -> None:
    """GIT IS THE ELIGIBILITY BOUNDARY AND THE FILESYSTEM IS THE FALLBACK.

    Discovery reads tracked paths so the catalogue obeys the same version-control boundary
    registration does — which means in this repository the tracked branch always answers and
    the walk beneath it never ran. It is what keeps the engine usable on an export, a
    worktree git cannot enumerate, or a root that is not there at all: a missing root is an
    empty list rather than an exception, and a present one is walked deterministically with
    dot-directories excluded.
    """
    reader, base = _untracked_repo(tmp_path, "pkg")
    (base / "__init__.py").write_text("", encoding="utf-8")
    (base / "child").mkdir()
    (base / "child" / "__init__.py").write_text("", encoding="utf-8")
    (base / ".hidden").mkdir()
    (base / ".hidden" / "__init__.py").write_text("", encoding="utf-8")

    assert discovery._package_locations(reader, "pkg") == ["pkg/child"]
    assert discovery._package_locations(reader, "no-such-root") == []


def test_the_census_walks_the_filesystem_and_survives_a_path_it_cannot_read(
    tmp_path: Path,
) -> None:
    """A CENSUS IS A COUNT AND A COUNT MUST NOT ABORT.

    Like discovery, the census prefers git and falls back to a deterministic walk — and the
    walk had never run. Both of its read loops skip a path that cannot be read as text: a
    directory whose name ends in ``.py`` matches the walk and is not a file, which is the
    ordinary shape of this. Raising there would make one such path cost the entire census,
    reporting nothing about the roots that were perfectly countable.
    """
    reader, base = _untracked_repo(tmp_path, "pkg")
    (base / "module.py").write_text("one\ntwo\nthree\n", encoding="utf-8")
    (base / "unreadable.py").mkdir()
    tests = base / "tests"
    tests.mkdir()
    (tests / "test_real.py").write_text("def test_alpha():\n    pass\n", encoding="utf-8")
    (tests / "test_unreadable.py").mkdir()

    counted = census.census_for(reader, "pkg")

    assert counted.source_files == 2
    assert counted.test_files == 2
    assert counted.loc == 3
    assert counted.test_functions == 1


def test_a_virtual_path_climbs_and_skips_dot_segments_without_touching_disk() -> None:
    """_resolve_virtual answers for paths that do not exist yet; ``..`` must actually pop.

    The pop arm fires only when a ``..`` arrives with something to remove, and the skip
    arm only for ``.`` — a resolver that got either wrong would let a not-yet-created
    directory escape the root it is confined to.
    """

    from intelligence.kernel.config import NestedFileSink

    resolve = NestedFileSink._resolve_virtual
    assert resolve(Path("a/b/../c")) == Path("a/c")
    dot = type("WithDot", (), {"parts": (".", "x")})()
    assert resolve(dot) == Path("x")
    assert resolve(Path("..")) == Path("/")
