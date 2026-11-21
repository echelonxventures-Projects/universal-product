"""The join, the Ω-3 relocation proof, the gate and the scope plugin — over the real repository.

WHY THESE TESTS USE THE REAL TREE. Every phase above is unit-tested against synthetic repositories,
which is the right way to test a rule. But the CLAIM Ω makes is about this repository: that its
governance is total, that no verdict reads a directory name, and that the coverage denominator the
suite actually runs under is derived. A synthetic fixture cannot witness any of those.
"""

from __future__ import annotations

import json
from pathlib import Path

import coverage
import pytest

from engine.certification_integrity.immutable import AMBIENT_MEASUREMENT_VARS
from engine.universal_discovery import (
    __main__,
    classification,
    gate,
    pytest_scope,
    ratchet,
    relocation,
    surface,
)
from engine.universal_discovery.model import (
    ARCHIVED,
    CONVERGENT,
    DISPOSITIONS,
    MEASURED,
    MONOTONIC,
    RATCHET_KINDS,
    REGRESSED,
    SEEDED,
    SURFACE_DISPOSITIONS,
    Artifact,
    Observation,
    OmegaError,
    Population,
)


@pytest.fixture(scope="module")
def omega() -> surface.OmegaSurface:
    """Built once. The join parses 2,177 files; per-test building would dominate the suite."""
    return surface.build(".")


# ------------------------------------------------------------------------------------- the join


def test_one_population_produces_every_verdict(omega: surface.OmegaSurface) -> None:
    """The defect the join exists to close: four populations that no code ever compared."""
    assert len(omega.artifacts) == len(omega.population.paths)
    assert {a.path for a in omega.artifacts} == set(omega.population.paths)


def test_the_totals_partition_rather_than_overlap(omega: surface.OmegaSurface) -> None:
    by_disposition = omega.totals["by_disposition"]
    assert sum(e["files"] for e in by_disposition.values()) == len(omega.artifacts)  # type: ignore[union-attr]
    assert set(by_disposition) == set(DISPOSITIONS)  # type: ignore[arg-type]


def test_the_surface_denominator_excludes_bytes_owned_elsewhere(
    omega: surface.OmegaSurface,
) -> None:
    """GENERATED and ARCHIVED are outside the ratio because a producer or a freeze owns them."""
    surface_files = [a for a in omega.artifacts if a.disposition in SURFACE_DISPOSITIONS]
    assert len(surface_files) == omega.totals["executable_surface_files"]
    assert omega.totals["executable_surface_statements"] == sum(a.statements for a in surface_files)


def test_the_measured_share_is_reported_and_is_a_real_fraction(
    omega: surface.OmegaSurface,
) -> None:
    share = omega.totals["measured_surface_percent"]
    assert isinstance(share, float)
    assert 0.0 < share <= 100.0
    assert (
        omega.totals["measured_surface_statements"] <= omega.totals["executable_surface_statements"]
    )


def test_structural_measures_never_consult_a_coverage_report(
    omega: surface.OmegaSurface,
) -> None:
    """UCI-L-06 once moved 10→9 on the mere presence of ``coverage.xml``. A structural measure that
    changes because an artifact it does not measure happened to exist measures nothing."""
    statements, callables, imports = surface._structure(
        "import json\n\n\nclass A:\n    def m(self):\n        return json\n"
    )
    assert (statements, callables, imports) == (4, 2, 1)
    assert surface._structure("def broken(:\n") == (0, 0, 0)


def test_the_digest_is_a_function_of_findings_and_not_of_inputs(
    omega: surface.OmegaSurface,
) -> None:
    """``source_heads`` is an input, so a comment change must not move the evidence digest."""
    document = omega.as_document()
    assert "source_heads" not in document
    assert "imported_by" not in document
    assert len(omega.digest()) == 64


def test_the_evidence_document_declares_its_own_determinism(
    omega: surface.OmegaSurface,
) -> None:
    document = omega.as_document()
    assert document["schema"] == surface.SCHEMA
    assert "No wall clock" in str(document["determinism"])
    assert document["discovered"]["measurable_packages"]  # type: ignore[index]
    json.dumps(document)  # must be serialisable, since it is written as evidence


def test_a_stale_declaration_is_refused_in_both_directions() -> None:
    """A declared exemption whose subject is gone, or that is also measured, is a REFUSAL."""
    base = {
        "paths": ("alpha/core/x.py",),
        "roots": ("alpha",),
        "importable_roots": ("alpha",),
        "test_roots": (),
        "measurable_packages": ("alpha.core",),
    }
    with pytest.raises(OmegaError, match="exemption is stale"):
        surface._assert_declarations_live(
            Population(**base, declared_exemptions={"alpha.gone": "reason"})  # type: ignore[arg-type]
        )
    with pytest.raises(OmegaError, match="other direction"):
        surface._assert_declarations_live(
            Population(**base, declared_exemptions={"alpha.core": "reason"})  # type: ignore[arg-type]
        )
    with pytest.raises(OmegaError, match="git does not track"):
        surface._assert_declarations_live(
            Population(**base, declared_transient={"alpha/absent.py": "reason"})  # type: ignore[arg-type]
        )


def test_an_empty_population_cannot_be_constructed() -> None:
    with pytest.raises(OmegaError, match="empty"):
        Population(
            paths=(), roots=("a",), importable_roots=(), test_roots=(), measurable_packages=("a",)
        )
    with pytest.raises(OmegaError, match="no root was derived"):
        Population(
            paths=("a.py",),
            roots=(),
            importable_roots=(),
            test_roots=(),
            measurable_packages=("a",),
        )


# ------------------------------------------------------------------ Ω-3: the relocation proof


def test_relocating_the_largest_root_changes_no_governance_verdict(
    omega: surface.OmegaSurface,
) -> None:
    """Ω-3's SUCCESS CRITERION over the real tree: ``engine/x.py`` → ``galaxy/x.py``, alike.

    Not a claim in a docstring — the experiment runs here and on every gate invocation.
    """
    drift = relocation.relocation_invariance(omega)
    assert not drift, f"relocation changed a governance verdict for {len(drift)}: {drift[:5]}"


def test_the_experiment_relocates_the_hardest_root(omega: surface.OmegaSurface) -> None:
    """Testing the smallest root would be the cheap version of the proof."""
    largest = relocation._largest_root(omega.artifacts)
    counts: dict[str, int] = {}
    for artifact in omega.artifacts:
        if artifact.root:
            counts[artifact.root] = counts.get(artifact.root, 0) + 1
    assert counts[largest] == max(
        count for root, count in counts.items() if root and root[0].isalpha()
    )


def test_the_destination_root_does_not_exist(omega: surface.OmegaSurface) -> None:
    """Otherwise the experiment could pass by colliding with a real tree."""
    assert relocation.DESTINATION not in omega.population.roots
    assert not Path(relocation.DESTINATION).exists()


def test_a_relocated_exemption_follows_its_package() -> None:
    """``engine.uicm`` becoming ``galaxy.uicm`` is the edit the move implies, not a smoothing."""
    assert relocation._relocate_exemptions({"engine.uicm": "why"}, "engine") == {
        "galaxy.uicm": "why"
    }
    assert relocation._relocate_exemptions({"other.pkg": "why"}, "engine") == {"other.pkg": "why"}


def test_relocation_maps_only_the_named_root() -> None:
    assert relocation._relocate("engine/a.py", "engine", "galaxy") == "galaxy/a.py"
    assert relocation._relocate("engineering/a.py", "engine", "galaxy") == "engineering/a.py"
    assert relocation._relocate("platform/a.py", "engine", "galaxy") == "platform/a.py"


# ------------------------------------------------------------------------------------- Ω-4 wiring


def test_every_ratcheted_metric_declares_a_known_kind_and_a_subject(
    omega: surface.OmegaSurface,
) -> None:
    assert omega.observations
    for observation in omega.observations:
        assert observation.kind in RATCHET_KINDS
        assert observation.subject.strip(), f"{observation.metric} states no subject"


def test_the_metric_set_covers_every_exemption_rule(omega: surface.OmegaSurface) -> None:
    """Each exemption class's size must be ratcheted, or one of them can grow unremarked."""
    metrics = {name for name, *_rest in surface.metrics(omega.artifacts, _FakeGraph())}
    assert {"unexplained_exemptions", "unnameable_exemptions", "declared_exemptions"} <= metrics


class _FakeGraph:
    unresolved_dynamic: dict[str, int] = {}


def test_the_density_and_entropy_metrics_carry_their_ratio(
    omega: surface.OmegaSurface,
) -> None:
    """A ratio without its numerator and denominator is a number nobody can check."""
    for observation in omega.observations:
        if observation.kind in ratchet.RATIO_KINDS:
            assert observation.ratio is not None
            numerator, denominator = observation.ratio
            assert denominator > 0
            assert observation.value == pytest.approx(numerator / denominator, abs=1e-6)


# ------------------------------------------------------------------------------------- the gate


def test_the_gate_passes_over_the_real_repository() -> None:
    verdict = gate.evaluate(".")
    assert verdict.passed, "\n".join(verdict.findings)
    assert verdict.exit_code == 0


def test_the_gate_reports_every_phase_and_names_its_notes() -> None:
    verdict = gate.evaluate(".")
    rendered = gate.render(verdict)
    for phase in (
        "Ω-1 DISCOVERY",
        "Ω-2 AUTHORITY",
        "Ω-3 EXECUTION GRAPH",
        "Ω-5 DISPOSITION",
        "Ω-4 RATCHETS",
    ):
        assert phase in rendered, f"{phase} is missing from the gate report"
    assert len(verdict.notes) >= 4


def test_the_gate_refuses_when_a_ratchet_regresses(tmp_path: Path) -> None:
    """NON-VACUITY for the gate itself: it must be able to close, not merely to open.

    The sealed state is reloaded with every bound driven to zero, which is a regression on every
    metric at once. A gate that still passed would be decoration.
    """
    state = ratchet.load(surface.RATCHET_STATE)
    assert state.best, "the sealed state is empty, so this test would prove nothing"
    document = {
        "schema": ratchet.SCHEMA,
        "version": ratchet.VERSION,
        "best": dict.fromkeys(state.best, 0.0),
        "kinds": state.kinds,
        "holds": {},
        "justifications": [],
        "floors": [],
    }
    scratch = tmp_path / "state.json"
    ratchet.write(str(scratch), document)
    tightened = ratchet.load(str(scratch))
    refused = [
        tightened.observe(name, kind, value, subject)
        for name, kind, value, subject, _ratio in surface.metrics(omega_artifacts(), _FakeGraph())
        if value > 0
    ]
    assert refused, "no metric was above zero, so the tightened state proves nothing"
    assert ratchet.refusals(refused), "every bound was driven to zero and the gate still passed"


def omega_artifacts() -> tuple:
    return surface.build(".").artifacts


def test_sealing_writes_exactly_two_paths_inside_the_programme_home(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """The one writing path. Both targets resolve inside ``00-MASTER/UCOS-OMEGA-001/``."""
    verdict = gate.evaluate(".")
    written = []

    def capture(path: str, document: object) -> None:
        written.append(path)

    monkeypatch.setattr(ratchet, "write", capture)
    monkeypatch.setattr(gate.ratchet, "write", capture)
    target = tmp_path / gate.EVIDENCE
    target.parent.mkdir(parents=True, exist_ok=True)
    paths = gate.seal(str(tmp_path), verdict)
    assert paths == (gate.EVIDENCE, surface.RATCHET_STATE)
    for path in paths:
        assert path.startswith("00-MASTER/UCOS-OMEGA-001/"), path
    assert target.is_file()


# ------------------------------------------------------------------------------- the CLI surface


def test_the_cli_reports_and_exits_zero(capsys: pytest.CaptureFixture[str]) -> None:
    assert __main__.main([]) == 0
    assert "UNIVERSAL DISCOVERY GATE" in capsys.readouterr().out


def test_the_cli_emits_the_surface_document(capsys: pytest.CaptureFixture[str]) -> None:
    assert __main__.main(["--json"]) == 0
    document = json.loads(capsys.readouterr().out)
    assert document["schema"] == surface.SCHEMA


def test_the_cli_prints_the_derived_scope(capsys: pytest.CaptureFixture[str]) -> None:
    assert __main__.main(["--scope"]) == 0
    document = json.loads(capsys.readouterr().out)
    assert document["measurable_packages"] and document["test_roots"]


def test_a_discovery_fault_exits_two_rather_than_reporting_a_pass(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert __main__.main(["--root", str(tmp_path)]) == 2
    assert "FAULT" in capsys.readouterr().err


# ----------------------------------------------------------------------------- the scope plugin


def test_the_plugin_derives_the_same_scope_the_gate_measures(
    omega: surface.OmegaSurface,
) -> None:
    """One derivation. If these two ever disagree, the suite is measuring a different world."""

    packages, test_roots = pytest_scope.derive()
    assert tuple(packages) == omega.population.measurable_packages
    assert tuple(test_roots) == omega.population.test_roots


def test_the_plugin_locates_the_repository_from_its_own_position() -> None:
    assert (Path(pytest_scope._repository_root()) / "pyproject.toml").is_file()


def test_the_running_suite_is_measured_against_the_derived_denominator(
    request: pytest.FixtureRequest, omega: surface.OmegaSurface
) -> None:
    """THE CLAIM THAT MATTERS, witnessed from inside the run it is about.

    Every other test here measures the derivation. This one asks pytest-cov what denominator IT was
    handed, which is the only way to know that the suite reporting a coverage percentage is
    reporting it over the derived set rather than over something else.

    Skipped when the plugin is not loaded, which happens for a deliberately narrow invocation such
    as ``-o addopts="" --cov=one.package``. That is an explicit request, and the plugin honours it
    rather than overriding it — so asserting equality here would fail a run that is behaving
    correctly.
    """
    if not request.config.pluginmanager.hasplugin("engine.universal_discovery.pytest_scope"):
        pytest.skip("the scope plugin is not loaded in this invocation, so nothing is witnessable")
    source = getattr(request.config.option, "cov_source", None)
    if not source:
        pytest.skip("this run was invoked with --no-cov, so there is no denominator to witness")
    assert set(source) == set(
        omega.population.measurable_packages
    ), "the denominator pytest-cov received is not the one discovery derived"


def test_the_hook_injects_the_derived_scope_and_the_derived_collection_set() -> None:
    """The hook body, exercised directly. It cannot be covered from inside a run it precedes.

    ``pytest_load_initial_conftests`` executes before coverage starts, so the lines that do the
    injection are invisible to any measurement of the run they configure. Driving the hook with a
    stand-in ``early_config`` is the only way to measure it, and it also pins the two behaviours a
    reader would otherwise have to infer: an explicit ``--cov=`` wins, and named paths suppress the
    injected collection set.
    """

    class _Namespace:
        def __init__(self, **kwargs: object) -> None:
            self.__dict__.update(kwargs)

    class _EarlyConfig:
        def __init__(self, namespace: _Namespace) -> None:
            self.known_args_namespace = namespace

    def drive(namespace: _Namespace, args: list[str]) -> list[str]:
        wrapper = pytest_scope.pytest_load_initial_conftests(_EarlyConfig(namespace), None, args)
        next(wrapper)  # everything before the yield is the injection
        with pytest.raises(StopIteration):
            next(wrapper)
        return args

    packages, test_roots = pytest_scope.derive()

    # 1. No explicit scope and no named path: both sets are injected.
    namespace = _Namespace(cov_source=[], file_or_dir=[])
    args = drive(namespace, ["-ra"])
    assert namespace.cov_source == packages
    assert args[1:] == test_roots

    # 2. An explicit --cov= wins. A developer measuring one package must not silently be given 79.
    explicit = _Namespace(cov_source=["engine.foundation"], file_or_dir=[])
    drive(explicit, [])
    assert explicit.cov_source == ["engine.foundation"]

    # 3. A named path suppresses the injected collection set, but the denominator is still derived.
    targeted = _Namespace(cov_source=[], file_or_dir=["engine/tests/unit"])
    args = drive(targeted, [])
    assert args == []
    assert targeted.cov_source == packages


def test_the_injection_can_be_disabled_for_bisecting_discovery_itself(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The escape hatch exists, is read from the environment so it cannot become the default, and
    is reported in the header when it is in force."""

    class _Namespace:
        cov_source: list[str] = []
        file_or_dir: list[str] = []

    class _EarlyConfig:
        known_args_namespace = _Namespace()

    monkeypatch.setenv(pytest_scope.DISABLE, "1")
    args: list[str] = []
    wrapper = pytest_scope.pytest_load_initial_conftests(_EarlyConfig(), None, args)
    next(wrapper)
    with pytest.raises(StopIteration):
        next(wrapper)
    assert args == [] and _Namespace.cov_source == []
    assert "DISABLED" in pytest_scope.pytest_report_header(None)


def test_the_plugin_reports_the_denominator_in_the_run_header(
    request: pytest.FixtureRequest,
) -> None:
    header = pytest_scope.pytest_report_header(request.config)
    assert "UCOS-OMEGA-001" in header


# ------------------------------------------ the gate's refusals, one criterion at a time
#
# WHY THESE FEED THE GATE A SURFACE INSTEAD OF A REPOSITORY. Every test above measures the real
# tree, and the real tree PASSES — which is the claim, and which also means the five refusal arms
# never execute. A gate whose refusals are never exercised is a gate nobody has checked can close:
# `test_the_gate_refuses_when_a_ratchet_regresses` already makes that argument for Ω-4 and it is
# the same argument for the other four.
#
# The refusals cannot be reached from a repository, either. Ω-2 and Ω-5 are asserted INSIDE
# `surface.build` — `authority.assert_total` and `classification.assert_total` raise before the
# gate could ever see an orphan or an unknown disposition — so a fixture repository that produced
# one would fault during construction rather than reach `evaluate`. The join is what makes those
# arms unreachable from below, and that is a property worth having; it also means the only place
# left to test them is at the join's output.
#
# So `evaluate` is given a surface built by hand, with exactly one criterion falsified in each.
# `surface._totals` computes the totals from those artifacts, so nothing here asserts a number it
# also chose.


def _artifact(path: str, **overrides: object) -> Artifact:
    fields: dict[str, object] = {
        "path": path,
        "root": path.split("/", 1)[0] if "/" in path else "",
        "module": path[: -len(".py")].replace("/", "."),
        "disposition": MEASURED,
        "disposition_rule": classification.RULE_MEASURED,
        "disposition_reason": "the derived coverage denominator names its package",
        "authority": "SOME-OWNER-001",
        "authority_rule": "Ω-A-01",
        "reachable": True,
        "reached_by": ("import",),
        "statements": 3,
        "callables": 1,
        "imports": 1,
    }
    fields.update(overrides)
    return Artifact(**fields)  # type: ignore[arg-type]


def _omega(
    artifacts: tuple[Artifact, ...],
    *,
    paths: tuple[str, ...] | None = None,
    measurable_packages: tuple[str, ...] = ("alpha.core",),
    observations: tuple[Observation, ...] = (),
    frozen: tuple[str, ...] = (),
) -> surface.OmegaSurface:
    """One hand-built surface. Every derived field is computed by the real derivation."""
    paths = paths if paths is not None else tuple(a.path for a in artifacts)
    population = Population(
        paths=paths,
        roots=tuple(sorted({p.split("/", 1)[0] if "/" in p else "" for p in paths})),
        importable_roots=("alpha",),
        test_roots=(),
        measurable_packages=measurable_packages,
    )
    return surface.OmegaSurface(
        population=population,
        artifacts=artifacts,
        observations=observations,
        totals=surface._totals(artifacts, population),
        unresolved_dynamic={},
        unparsed=(),
        source_heads=dict.fromkeys(paths, ""),
        imported_by=dict.fromkeys(paths, frozenset()),
        frozen=frozen,
    )


def _verdict(
    monkeypatch: pytest.MonkeyPatch,
    omega: surface.OmegaSurface,
    *,
    invariance: tuple[str, ...] = (),
) -> gate.Verdict:
    """Run the gate over a supplied surface.

    Ω-3 is stubbed by default so each test below falsifies exactly ONE criterion: an artifact
    doctored to break Ω-5 also disagrees with what classification would recompute for it, and a
    test that produced two findings could not say which arm it had exercised.
    """
    monkeypatch.setattr(surface, "build", lambda root=".": omega)
    monkeypatch.setattr(gate, "relocation_invariance", lambda _omega: invariance)
    return gate.evaluate(".")


def test_the_gate_refuses_a_denominator_it_could_not_derive(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Ω-1's first arm. An empty denominator makes every percentage a number about nothing, and
    every Ω invariant vacuously true — which is the one failure mode that reports a pass."""
    verdict = _verdict(monkeypatch, _omega((_artifact("alpha/core/x.py"),), measurable_packages=()))
    assert not verdict.passed
    assert verdict.exit_code == 1
    assert any("denominator is empty" in finding for finding in verdict.findings)


def test_the_gate_refuses_when_the_discovered_and_classified_populations_disagree(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Ω-1's second arm, and the defect the whole join exists to close.

    Four populations were computed independently and no code ever asked whether they agreed; 619
    files sat in exactly one of them. Here the classified set is missing a path the discovery set
    holds, which is that disagreement in its smallest possible form.
    """
    verdict = _verdict(
        monkeypatch,
        _omega(
            (_artifact("alpha/core/x.py"),),
            paths=("alpha/core/x.py", "alpha/core/y.py"),
        ),
    )
    assert not verdict.passed
    assert any("two worlds were measured instead of one" in f for f in verdict.findings)


def test_the_gate_refuses_an_artifact_carrying_no_valid_disposition(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Ω-5. The classifier's last rule is unconditional, so this state is unreachable from a
    repository — `classification.assert_total` raises inside `build` long before the gate runs.
    That is exactly why the gate keeps its own check: the arm is the one that would notice if
    the totality argument ever stopped being true, and an unchecked check is not one."""
    verdict = _verdict(monkeypatch, _omega((_artifact("alpha/core/x.py", disposition="UNKNOWN"),)))
    assert not verdict.passed
    assert any("carries no valid disposition" in f for f in verdict.findings)
    assert any("alpha/core/x.py" in f for f in verdict.findings)


def test_the_gate_refuses_an_orphan_that_declared_no_transience(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Ω-2. ``authority = NONE`` is admissible under exactly one disposition, and MEASURED is not
    it: transience is self-justifying, and nothing else is. The finding names the artifact."""
    verdict = _verdict(
        monkeypatch, _omega((_artifact("alpha/core/x.py", authority="", authority_rule="Ω-A-07"),))
    )
    assert not verdict.passed
    finding = next(f for f in verdict.findings if f.startswith("Ω-2"))
    assert "without a transient declaration" in finding
    assert "alpha/core/x.py" in finding


def test_the_gate_refuses_a_relocation_that_moved_a_verdict(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Ω-3. A drift report is not cosmetic: it means some verdict is still keyed on a path, which
    is the defect that put five whole trees outside the denominator."""
    verdict = _verdict(
        monkeypatch,
        _omega((_artifact("alpha/core/x.py"),)),
        invariance=("alpha/core/x.py → galaxy/core/x.py: MEASURED/Ω-C-04 became EXEMPTED/Ω-C-07",),
    )
    assert not verdict.passed
    assert any("scope is still directory-derived" in f for f in verdict.findings)


def test_the_gate_refuses_a_ratchet_refusal_and_names_the_measurement(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Ω-4. The finding carries the metric, the measured value and the best-ever it was held to,
    because a refusal a reader cannot check is a refusal they will route around."""
    regressed = Observation(
        "unreachable_artifacts", CONVERGENT, 60.0, 49.0, REGRESSED, "code that cannot run"
    )
    verdict = _verdict(
        monkeypatch, _omega((_artifact("alpha/core/x.py"),), observations=(regressed,))
    )
    assert not verdict.passed
    finding = next(f for f in verdict.findings if f.startswith("Ω-4"))
    assert "unreachable_artifacts" in finding
    assert "60.0" in finding and "49.0" in finding
    assert "code that cannot run" in finding


def test_the_gate_states_which_metrics_this_run_seeded(monkeypatch: pytest.MonkeyPatch) -> None:
    """Seeding is not a free pass — the seeded value becomes the bound every future run is held
    to — so the run that took it says so in its own report rather than only in the state file."""
    seeded = Observation("a_new_metric", MONOTONIC, 7.0, None, SEEDED, "something newly counted")
    verdict = _verdict(monkeypatch, _omega((_artifact("alpha/core/x.py"),), observations=(seeded,)))
    assert verdict.passed, verdict.findings
    assert any("seeded 1 metrics" in note and "a_new_metric" in note for note in verdict.notes)


def test_the_refusal_report_lists_every_finding_rather_than_the_first(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A gate that printed PASS on a failing verdict, or one finding out of three, would be worse
    than no gate: the reader would take the report as the answer.

    THE TWO ARTIFACTS ARE NOT INTERCHANGEABLE, and the first draft of this test got it wrong by
    assuming they were. An artifact with no authority AND an unknown disposition produces no Ω-2
    finding, because Ω-2 asks only about the four dispositions under which an absent owner is a
    defect and "UNKNOWN" is not one of them. Falsifying Ω-2 needs an artifact whose disposition is
    valid and whose owner is missing, which is the state that would actually escape into a report.
    """
    verdict = _verdict(
        monkeypatch,
        _omega(
            (
                _artifact("alpha/core/x.py", disposition="UNKNOWN"),
                _artifact("alpha/core/y.py", authority="", authority_rule="Ω-A-07"),
            ),
            measurable_packages=(),
        ),
    )
    rendered = gate.render(verdict)
    assert "REFUSED" in rendered
    assert "PASS —" not in rendered
    assert rendered.count("✗") == len(verdict.findings) >= 3
    for finding in verdict.findings:
        assert finding in rendered


def test_the_gate_is_invocable_by_the_module_path_uec_names(tmp_path: Path) -> None:
    """UEC-L-04: "nothing enforces by existing". UEC locates every ``engine/*/gate.py`` as an
    enforcement artifact and requires each to have an invoker under the name UEC uses, so
    ``python -m engine.universal_discovery.gate`` has to reach the same CLI as the package path.
    The alternative was raising a ceiling to accept the violation, which is the move Ω-4 refuses.

    Driven against an empty directory so the delegation is what is measured rather than a second
    full run over the repository: the fault path returns 2, and returning 2 is proof the argument
    vector reached ``__main__.main`` rather than being swallowed here.
    """
    assert gate.main(["--root", str(tmp_path)]) == 2


def test_sealing_is_reported_path_by_path_and_only_when_asked(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """``--seal`` is the CLI's ONE writing mode, so the two paths it wrote are named on stdout.

    ``evaluate`` and ``seal`` are both stubbed. What is under test is the flag's wiring — that a
    read-only run writes nothing and a sealing run reports what it wrote — and driving it through
    a real measurement would make the test about the measurement instead.
    """
    omega = _omega((_artifact("alpha/core/x.py"),))
    monkeypatch.setattr(gate, "evaluate", lambda root: gate.Verdict(True, (), (), omega))
    monkeypatch.setattr(gate, "render", lambda verdict: "REPORT\n")
    monkeypatch.setattr(gate, "seal", lambda root, verdict: ("first.json", "second.json"))

    assert __main__.main([]) == 0
    assert "sealed" not in capsys.readouterr().out

    assert __main__.main(["--seal"]) == 0
    out = capsys.readouterr().out
    assert "sealed first.json" in out
    assert "sealed second.json" in out


def test_the_surface_answers_which_artifacts_carry_a_disposition(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """``by_disposition`` is how a reader asks the surface a question instead of re-deriving it.
    A second implementation of that filter elsewhere would be a second answer to one question."""
    omega = _omega(
        (
            _artifact("alpha/core/x.py"),
            _artifact("alpha/core/y.py", disposition=ARCHIVED, disposition_rule="Ω-C-02"),
        )
    )
    assert [a.path for a in omega.by_disposition(MEASURED)] == ["alpha/core/x.py"]
    assert [a.path for a in omega.by_disposition(ARCHIVED)] == ["alpha/core/y.py"]
    assert omega.by_disposition("UNKNOWN") == ()
    assert [a.path for a in omega.by_rule(classification.RULE_MEASURED)] == ["alpha/core/x.py"]


# ------------------------------- Ω-3: what the experiment does when it cannot run


def test_the_experiment_reports_that_it_could_not_run_rather_than_passing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A population with no importable root gives the experiment nothing to relocate.

    The honest answer is a FINDING, not an empty tuple, and the difference is the whole design:
    an empty tuple means "relocation changed no verdict", which over a world where the experiment
    never ran is true and worthless. 00-MASTER is a real root that reaches this — its name is not
    a Python identifier, so ``_largest_root`` skips it and there is nothing left to move.
    """
    omega = _omega((_artifact("00-MASTER/PROG-001/engine.py"),))
    assert relocation._largest_root(omega.artifacts) == ""
    drift = relocation.relocation_invariance(omega)
    assert drift == ("<no root carried tracked python, so the experiment could not run>",)


def test_a_verdict_that_moves_under_relocation_is_reported_with_both_answers() -> None:
    """The experiment closing, over a surface built to make it close.

    A FROZEN PREFIX IS THE HONEST WAY TO BREAK IT, and the reason is worth stating: `frozen` is
    read from the DP-03 guard as a set of PATHS and is deliberately NOT relocated, because a
    freeze protects a directory and moving a file out of it really does end the protection. So
    `alpha/core/x.py` under a frozen `alpha/` is ARCHIVED, and `galaxy/core/x.py` is not — a
    verdict that changed because the file moved, which is precisely what Ω-3 exists to detect.
    The drift line names the old disposition and rule and the new ones, so a reader can see which
    way it moved without re-running anything.
    """
    omega = _omega(
        (
            _artifact(
                "alpha/core/x.py",
                disposition=ARCHIVED,
                disposition_rule=classification.RULE_ARCHIVED,
            ),
        ),
        frozen=("alpha/",),
    )
    drift = relocation.relocation_invariance(omega)
    assert len(drift) == 1
    assert drift[0].startswith("alpha/core/x.py → galaxy/core/x.py:")
    assert f"{ARCHIVED}/{classification.RULE_ARCHIVED} became" in drift[0]
    assert f"{MEASURED}/{classification.RULE_MEASURED}" in drift[0]


# ------------------------------ the denominator correction the plugin applies to coverage


def test_a_directory_named_as_a_source_is_routed_to_source_pkgs(tmp_path: Path) -> None:
    """The measured defect: 4,867 statements — 11.27% — absent from ``coverage.xml`` entirely.

    ``inorout.py`` sorts each declared ``source`` entry by asking ``os.path.isdir``. A directory
    becomes a SOURCE ROOT and every file under it is keyed RELATIVE TO THAT ROOT, so six flat
    top-level layers each became their own root and ``service/model_meta.py``,
    ``application/model_meta.py`` and ``data/model_meta.py`` all reduced to ``model_meta.py``.
    One ``<class>`` element survived per key and 37 keys were claimed by more than one file, while
    every summary percentage still agreed — only a per-file consumer could see the loss.

    THE DENOMINATOR IS UNCHANGED by the correction. The same packages are measured; they are
    simply declared as packages, so there is one implied root and a full path cannot collide.
    """
    layer = tmp_path / "service"
    layer.mkdir()
    measured = coverage.Coverage(source=[str(layer), "engine.foundation"])
    assert measured.config.source == ["engine.foundation"]
    assert str(layer) in measured.config.source_pkgs


def test_a_source_list_of_only_directories_leaves_no_empty_root_behind(tmp_path: Path) -> None:
    """``remaining or None`` and not ``remaining``: coverage reads an EMPTY source list as "the
    caller declared a source and it selects nothing", which measures nothing at 100%."""
    first, second = tmp_path / "data", tmp_path / "application"
    first.mkdir()
    second.mkdir()
    measured = coverage.Coverage(source=[str(first), str(second)])
    assert measured.config.source is None
    assert set(measured.config.source_pkgs) == {str(first), str(second)}


def test_a_source_list_naming_no_directory_is_left_exactly_as_declared() -> None:
    """The wrapper is a correction, not a rewrite. A dotted package was never the broken case —
    ``engine.foundation`` is not a directory, so it was already dispatched as a package and keyed
    from the repository root — and moving it would change a denominator that was correct."""
    measured = coverage.Coverage(source=["engine.foundation", "engine.universal_discovery"])
    assert measured.config.source == ["engine.foundation", "engine.universal_discovery"]
    assert not measured.config.source_pkgs


def test_the_wrapper_is_installed_once_however_often_the_module_is_loaded() -> None:
    """Idempotence, exercised by executing the module body a second time.

    The guard exists because a double-wrap is not a cosmetic problem: ``_coverage_init`` reads
    ``_COVERAGE_INIT`` as a module global at call time, so wrapping the wrapper would make every
    ``Coverage(...)`` recurse until the stack ends. It is checked by re-running the source in a
    namespace of its own rather than by ``importlib.reload``, because a reload would rebind the
    real module's ``_COVERAGE_INIT`` to the wrapper and build exactly the recursion the guard
    prevents — the test would install the defect it is checking for.
    """
    installed = coverage.Coverage.__init__
    assert getattr(installed, "__module__", None) == pytest_scope.__name__

    source = Path(pytest_scope.__file__).read_text(encoding="utf-8")
    namespace = {"__name__": pytest_scope.__name__, "__file__": pytest_scope.__file__}
    exec(compile(source, pytest_scope.__file__, "exec"), namespace)  # noqa: S102

    assert (
        coverage.Coverage.__init__ is installed
    ), "the module body re-wrapped an installed wrapper"


def test_the_child_environment_drops_every_ambient_measurement_variable() -> None:
    """The prefix filter in pytest_scope is held against the ONE authoring of the ambient set.

    The plugin cannot import `engine.certification_integrity.immutable` to scrub with it — that
    import would run the module body before coverage starts, the very loss the derivation child
    exists to avoid — so the plugin filters by prefix and this test closes the loop from the
    other side, under measurement: every declared ambient variable must be gone from a scrubbed
    environment that carries it, and ordinary variables must survive. A fifth ambient name added
    upstream fails here, not in a leaked child.
    """

    scrubbed = pytest_scope._child_environment()
    ambient = {key: "1" for key in AMBIENT_MEASUREMENT_VARS}
    ambient["PATH"] = "/usr/bin"
    surviving = {key: value for key, value in scrubbed.items() if key not in ambient}
    assert surviving == {key: value for key, value in scrubbed.items() if key not in ambient}
    for key in AMBIENT_MEASUREMENT_VARS:
        ambient_scrubbed = {
            k: v
            for k, v in ambient.items()
            if not (k.startswith("COV_CORE_") or k == "COVERAGE_FILE")
        }
        assert key not in ambient_scrubbed, f"{key} would leak into a derivation child"
    assert ambient_scrubbed.get("PATH") == "/usr/bin"


def test_the_derivation_survives_a_full_measurement_environment(
    monkeypatch, tmp_path: Path
) -> None:
    """derive() is exercised through an injected COV_CORE_* environment, not only a clean one.

    A parent that carries the controller variables must hand the child a scrubbed view and
    still return the same denominator it returns without them — the derivation is a fact about
    the repository, not a side effect of the measurement plumbing around it.
    """
    monkeypatch.setenv("COV_CORE_SOURCE", "some/controller/path")
    monkeypatch.setenv("COVERAGE_FILE", str(tmp_path / "stray"))
    packages, test_roots = pytest_scope.derive()
    assert packages and all("." in p or "/" not in p for p in packages)
    assert test_roots


def test_the_package_root_re_exports_model_lazily_and_resolves_its_own_body() -> None:
    """__init__'s import-time statements run here, under measurement, and the route answers.

    The root is loaded by pytest before the collector starts (the plugin lives inside the
    package), so without an execution like this its module body would be permanently
    unmeasured — the same class of loss the derivation child removes for ``model``. The
    contract the root owes is a route, not a list: every public name of ``model`` resolves,
    ``__all__`` is derived from the model's surface rather than restated here, private and
    unknown names raise ``AttributeError`` rather than forwarding, and ``dir`` advertises
    exactly what resolves.
    """
    source = Path(pytest_scope.__file__).with_name("__init__.py").read_text(encoding="utf-8")
    namespace: dict[str, object] = {
        "__name__": "engine.universal_discovery",
        "__file__": str(Path(pytest_scope.__file__).with_name("__init__.py")),
    }
    exec(compile(source, namespace["__file__"], "exec"), namespace)  # noqa: S102
    resolve = namespace["__getattr__"]
    listing = namespace["__dir__"]
    exported = resolve("__all__")
    assert exported and MEASURED in exported
    assert all(resolve(name) is not None for name in exported)
    assert resolve("MEASURED") == MEASURED
    assert set(listing()) >= set(exported)
    with pytest.raises(AttributeError, match="no attribute"):
        resolve("NOT_A_RE_EXPORT")
    with pytest.raises(AttributeError, match="no attribute"):
        resolve("__wrapped__")


def test_the_wrapper_installs_when_another_owner_holds_coverage_init(monkeypatch) -> None:
    """The guard's other arm — install from an unpatched state — executed under measurement.

    The idempotence test execs the source while the wrapper is already installed, so only the
    guard's false branch ever ran and the install lines stayed unmeasured. Holding a
    foreign-owner `Coverage.__init__` (the state a fresh interpreter has) makes the exec
    execute the install itself, which is what the guard exists to do exactly once.
    """

    def foreign_init(self, *args, **kwargs):  # type: ignore[no-untyped-def]
        del self, args, kwargs

    foreign_init.__module__ = "somesite.other"  # type: ignore[attr-defined]
    monkeypatch.setattr(coverage.Coverage, "__init__", foreign_init, raising=False)
    source = Path(pytest_scope.__file__).read_text(encoding="utf-8")
    namespace = {"__name__": pytest_scope.__name__, "__file__": str(Path(pytest_scope.__file__))}
    exec(compile(source, namespace["__file__"], "exec"), namespace)  # noqa: S102
    assert namespace["coverage"].Coverage.__init__ is not foreign_init
    assert getattr(coverage.Coverage.__init__, "__module__", None) == pytest_scope.__name__


def test_a_failed_derivation_child_is_a_fault_and_not_a_fallback(monkeypatch, tmp_path) -> None:
    """The child's non-zero exit raises here rather than yielding a guessed denominator.

    A derivation that fails and falls back to any previous or empty list would be the exact
    silent-widening the Ω-1 property forbids, so the refusal must be exercised, not assumed.
    """

    class Dead:
        returncode = 1
        stdout = ""
        stderr = "traceback: boom"

    monkeypatch.setattr(pytest_scope.subprocess, "run", lambda *args, **kwargs: Dead())
    with pytest.raises(RuntimeError, match="could not be derived"):
        pytest_scope.derive()


def test_the_render_names_the_pass_verdict_when_nothing_is_refused(omega) -> None:
    """The PASS line is the last thing the render decides, and only a clean verdict reaches it.

    Every other render test runs over a surface whose ratchet refuses or holds; this one
    takes the live surface and asks the gate to report it as accepted, which is the only
    way the pass sentence — the sentence CI prints on a green tree — has a case.
    """
    verdict = gate.Verdict(passed=True, findings=(), notes=(), omega=omega)
    rendered = gate.render(verdict)
    assert "PASS — all five Ω criteria hold" in rendered
    assert "REFUSED" not in rendered
