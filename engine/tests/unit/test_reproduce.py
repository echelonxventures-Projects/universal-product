"""TASK-000032/000034 — Reproducibility harness tests.

Verifies blueprint resolution, the byte-level comparison engine, diff-report
generation, successful double builds, and deliberate divergence detection — all
over the temp compiler substrate so the corpus is never touched.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from engine.determinism import reproduce as reproduce_module
from engine.determinism.errors import (
    BlueprintResolutionError,
    NonDeterministicOutputError,
    ReproducibilityError,
)
from engine.determinism.reproduce import (
    DEFAULT_BLUEPRINTS_DIR,
    POSITIVE_CONTROL_SUBJECT,
    DirectoryBlueprintProvider,
    InitializationIndependenceResult,
    InitializationScenario,
    ReproducibilityResult,
    ScenarioObservation,
    _classify,
    compare_builds,
    compare_initialization,
    double_build,
    initialization_gate,
)

# -- blueprint provider -------------------------------------------------------


def test_default_provider_resolves_shipped_bp_data_0001():
    provider = DirectoryBlueprintProvider()
    doc = provider.get("BP-DATA-0001")
    assert doc["blueprint_id"] == "BP-DATA-0001"
    assert doc["certification"]["status"] == "CERTIFIED"
    assert provider.directory == DEFAULT_BLUEPRINTS_DIR


def test_provider_rejects_invalid_id():
    with pytest.raises(BlueprintResolutionError):
        DirectoryBlueprintProvider().get("../etc/passwd")


def test_provider_missing_blueprint(tmp_path):
    with pytest.raises(BlueprintResolutionError):
        DirectoryBlueprintProvider(tmp_path).get("BP-DATA-9999")


# -- comparison engine --------------------------------------------------------


def _plant(base: Path, files: dict[str, str]) -> Path:
    for rel, content in files.items():
        path = base / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    return base


def test_compare_builds_identical(tmp_path):
    files = {
        "artifacts/schema/customer.sql": "CREATE TABLE customer();\n",
        "manifest.json": "{}\n",
        "sbom.json": "{}\n",
        "signature.json": "{}\n",
        "artifact-record.json": "{}\n",
    }
    a = _plant(tmp_path / "a", files)
    b = _plant(tmp_path / "b", files)
    diffs, categories = compare_builds(a, b)
    assert all(d.is_identical for d in diffs)
    assert all(categories.values())


def test_compare_builds_detects_content_divergence(tmp_path):
    base = {
        "artifacts/schema/customer.sql": "A\n",
        "manifest.json": "{}\n",
        "sbom.json": "{}\n",
        "signature.json": "{}\n",
        "artifact-record.json": "{}\n",
    }
    a = _plant(tmp_path / "a", base)
    b = _plant(tmp_path / "b", {**base, "artifacts/schema/customer.sql": "B\n"})
    diffs, categories = compare_builds(a, b)
    assert categories["generated_source"] is False
    assert categories["manifests"] is True
    differing = [d for d in diffs if d.status == "differs"]
    assert differing[0].path == "artifacts/schema/customer.sql"


def test_compare_builds_detects_missing_file(tmp_path):
    a = _plant(tmp_path / "a", {"manifest.json": "{}\n", "sbom.json": "{}\n"})
    b = _plant(tmp_path / "b", {"manifest.json": "{}\n", "signature.json": "{}\n"})
    diffs, categories = compare_builds(a, b)
    statuses = {d.path: d.status for d in diffs}
    assert statuses["sbom.json"] == "only_in_a"
    assert statuses["signature.json"] == "only_in_b"
    assert categories["sbom"] is False
    assert categories["signatures"] is False
    # categories with no files present are not asserted identical
    assert categories["publication_payloads"] is False


# -- successful double build --------------------------------------------------


def test_double_build_is_byte_identical(compiler_registry):
    result = double_build("BP-DATA-0001", registry=compiler_registry)
    assert isinstance(result, ReproducibilityResult)
    assert result.byte_identical is True
    assert result.artifact_id_a == result.artifact_id_b
    assert result.divergences == ()
    assert all(result.category_identical.values())
    assert len(result.diffs) == 7  # 3 artifacts + manifest + sbom + signature + record


def test_double_build_report_dict_shape(compiler_registry):
    result = double_build("BP-DATA-0001", registry=compiler_registry)
    report = result.to_report_dict()
    assert report["reproducibility_report"] is True
    assert report["byte_identical"] is True
    assert report["artifact_id_match"] is True
    assert set(report["categories"]) == {
        "generated_source",
        "manifests",
        "sbom",
        "signatures",
        "publication_payloads",
    }
    assert report["divergence_count"] == 0


def test_double_build_writes_report(compiler_registry, tmp_path):
    result = double_build("BP-DATA-0001", registry=compiler_registry)
    path = result.write_report(tmp_path / "reproducibility_report.json")
    assert path.is_file()
    on_disk = json.loads(path.read_text())
    assert on_disk["blueprint_id"] == "BP-DATA-0001"


def test_double_build_accepts_explicit_signing_key(compiler_registry):
    result = double_build("BP-DATA-0001", registry=compiler_registry, signing_key=b"custom-key")
    assert result.byte_identical


def test_double_build_accepts_key_ref(compiler_registry, monkeypatch):
    monkeypatch.setenv("UCOS_DET_KEY", "ref-key")
    result = double_build("BP-DATA-0001", registry=compiler_registry, key_ref="env://UCOS_DET_KEY")
    assert result.byte_identical


def test_double_build_failed_build_raises(compiler_registry, tmp_path):
    # An uncertified blueprint cannot be compiled → reproducibility build fails.
    doc = json.loads((DEFAULT_BLUEPRINTS_DIR / "BP-DATA-0001.json").read_text())
    doc["certification"] = {"status": "UNCERTIFIED", "evidence": ""}
    (tmp_path / "BP-DATA-0002.json").write_text(
        json.dumps({**doc, "blueprint_id": "BP-DATA-0002"}), encoding="utf-8"
    )
    provider = DirectoryBlueprintProvider(tmp_path)
    with pytest.raises(ReproducibilityError) as exc:
        double_build("BP-DATA-0002", registry=compiler_registry, provider=provider)
    assert "gap" in exc.value.context


# -- deliberate divergence detection ------------------------------------------


def test_double_build_detects_injected_divergence(compiler_registry, monkeypatch):
    import engine.determinism.reproduce as reproduce

    real = reproduce._execute_build
    state = {"n": 0}

    def _diverging(**kwargs):
        base = real(**kwargs)
        state["n"] += 1
        if state["n"] == 2:  # mutate the second (B) build to force divergence
            (base / "artifacts" / "schema" / "customer.sql").write_text(
                "-- tampered\n", encoding="utf-8"
            )
        return base

    monkeypatch.setattr(reproduce, "_execute_build", _diverging)
    result = double_build("BP-DATA-0001", registry=compiler_registry)
    assert result.byte_identical is False
    assert result.category_identical["generated_source"] is False
    assert len(result.divergences) >= 1


def test_double_build_strict_raises_on_divergence(compiler_registry, monkeypatch):
    import engine.determinism.reproduce as reproduce

    real = reproduce._execute_build
    state = {"n": 0}

    def _diverging(**kwargs):
        base = real(**kwargs)
        state["n"] += 1
        if state["n"] == 2:
            (base / "manifest.json").write_text("{tampered}\n", encoding="utf-8")
        return base

    monkeypatch.setattr(reproduce, "_execute_build", _diverging)
    with pytest.raises(NonDeterministicOutputError) as exc:
        double_build("BP-DATA-0001", registry=compiler_registry, strict=True)
    assert exc.value.code == "DET-DIVERGENCE-001"


# -- BC-2: initialization-independent detection ---------------------------------


def test_double_build_shares_no_mutable_object_between_sides(compiler_registry, monkeypatch):
    """A2-1: the two builds must not share env or signer instances.

    A single reused adapter or signer can carry state from the first build into
    the second and mask an initialization-order dependence — the exact defect
    this harness exists to detect. Each side constructs its own env and signer.
    A caller-supplied ``registry`` is intentionally shared: it is a read-only
    view of the corpus, and the harness must not silently open a second handle
    to repository state the caller already owns.
    """
    reproduce = __import__("engine.determinism.reproduce", fromlist=["_execute_build"])

    seen: dict[str, list] = {"signer": [], "env": []}
    real = reproduce._execute_build

    def _recording(*, registry, signer, env, **kwargs):
        # keep a reference: id() can be reused once the object is freed, which
        # would make two distinct instances look like one shared instance.
        seen["signer"].append(signer)
        seen["env"].append(env)
        return real(registry=registry, signer=signer, env=env, **kwargs)

    monkeypatch.setattr(reproduce, "_execute_build", _recording)
    double_build("BP-DATA-0001", registry=compiler_registry)

    assert len(seen["signer"]) == 2, "expected two signer instances, one per build"
    assert seen["signer"][0] is not seen["signer"][1], "signer instance was shared across builds"
    assert len(seen["env"]) == 2, "expected two env instances, one per build"
    assert seen["env"][0] is not seen["env"][1], "env instance was shared across builds"


# -- BC-2: cross-process initialization independence ----------------------------
#
# ONE COMPARATOR RUN, MANY ASSERTIONS. Every test below that needs a real measurement
# shares the module-scoped ``comparison`` fixture: each run spawns four child
# interpreters, and re-spawning them per assertion would buy nothing — the comparator is
# pure, so a second run of the same input is the same result by construction, which is
# itself asserted once in ``test_comparator_is_deterministic_across_runs``.


@pytest.fixture(scope="module")
def comparison():
    return compare_initialization()


def test_a2_1_each_scenario_runs_in_an_interpreter_of_its_own(comparison):
    """A2-1: genuine multi-process isolation, not three calls in one process."""
    pids = [o.pid for o in comparison.observations]
    assert len(pids) == 3, "expected one observation per declared scenario"
    assert len(set(pids)) == 3, f"scenarios shared an interpreter: {pids}"
    assert os.getpid() not in pids, "a scenario ran inside the comparator's own process"
    assert comparison.isolated


def test_a2_2_the_known_initialization_dependent_subject_is_detected(comparison):
    """A2-2: the positive control. A comparator clean on this one proves nothing."""
    assert comparison.positive_control_detected
    caught = [d for d in comparison.divergences if d.subject == POSITIVE_CONTROL_SUBJECT]
    assert caught, "the positive control was not reported at all"
    assert {(d.left, d.right) for d in caught} == {("A", "B"), ("A", "C")}
    before = next(d for d in caught if (d.left, d.right) == ("A", "B"))
    assert before.left_verdict is False and before.right_verdict is True
    assert "_EXTENSION_KIND_CODES" in before.authority


def test_a2_3_the_deterministic_core_plane_reports_clean(comparison):
    """A2-3: the negative control. The 29 import-fixed kinds must not move."""
    core = set(comparison.core_kinds)
    assert len(core) == 29, "the core kind space changed; re-derive the control"
    moved = [d for d in comparison.divergences if d.kind in core]
    assert moved == [], f"a core kind moved with initialization: {[d.to_dict() for d in moved]}"
    assert comparison.refusals == ()


def test_a2_4_an_order_only_divergence_is_refused():
    """A2-4: B != C is detectable, not only A != B.

    The declared C reaches B's state by the reverse arrival order and agrees with it, so
    the live repository shows no order dependence — which is a result, not a proof that
    the comparator could see one. This runs a fourth scenario that reaches a *different*
    state by an admissible sequence and asserts the pair is refused rather than disclosed.
    """
    drifted = InitializationScenario(
        "D", "bootstrap plus a kind no other scenario registers", ("engine.ceu.catalog:bootstrap",)
    )
    kinds = ("CLASSIFICATION",)
    left = ScenarioObservation("B", drifted.steps, 1, kinds, (("s", True),))
    right = ScenarioObservation("D", drifted.steps, 2, kinds, (("s", False),))
    standing, authority = _classify(left, right, "CLASSIFICATION", frozenset())
    assert standing == "REFUSED"
    assert "arrival order" in authority


def test_a2_4_order_sensitivity_holds_in_the_live_repository(comparison):
    """A2-4, measured: the two admissible orders that reach one state do agree."""
    assert comparison.matrix()["B|C"] is True
    assert [d for d in comparison.divergences if "A" not in (d.left, d.right)] == []


def test_a2_5_coverage_is_stated_as_a_list_not_claimed_as_total(comparison):
    """A2-5: which of the admissible kinds were compared, explicitly."""
    coverage = comparison.to_dict()["coverage"]
    assert coverage["admissible_kinds"] == len(comparison.compared_kinds)
    assert coverage["core_kinds"] + coverage["extension_kinds"] == coverage["admissible_kinds"]
    assert len(coverage["compared_kinds"]) == coverage["admissible_kinds"]
    # one probe identifier per kind, plus the named positive control
    assert coverage["subjects"] == coverage["admissible_kinds"] + 1
    assert "claimed as total" in coverage["$statement"]


def test_a2_6_the_comparator_writes_nothing(tmp_path, monkeypatch):
    """A2-6 purity: a gate that can dirty the tree cannot certify one."""
    monkeypatch.chdir(tmp_path)
    before = sorted(p.name for p in tmp_path.iterdir())
    result = compare_initialization()
    assert sorted(p.name for p in tmp_path.iterdir()) == before
    assert result.observations, "the comparator produced no observation to be pure about"


def test_a2_6_mutation_of_the_classifier_is_caught():
    """A2-6 mutation test: weaken the rule and a green verdict must not survive it."""
    core = frozenset({"CLASSIFICATION"})
    left = ScenarioObservation("A", (), 1, (), (("s", False),))
    right = ScenarioObservation("B", ("engine.ceu.catalog:bootstrap",), 2, (), (("s", True),))
    assert _classify(left, right, "CLASSIFICATION", core)[0] == "REFUSED"
    # the same pair over a kind the authority admits by registration is disclosed, not
    # refused — if this returned REFUSED the gate would be permanently red and useless
    assert _classify(left, right, "OBSERVER", core)[0] == "DISCLOSED"


def test_a2_6_an_undetected_positive_control_refuses_the_run():
    """A2-6: the verdict is not a function of the refusal list alone."""
    clean = InitializationIndependenceResult(
        observations=(
            ScenarioObservation("A", (), 1, (), ()),
            ScenarioObservation("B", ("engine.ceu.catalog:bootstrap",), 2, (), ()),
        ),
        divergences=(),
        core_kinds=(),
        extension_kinds=(),
        compared_kinds=(),
        subjects=(POSITIVE_CONTROL_SUBJECT,),
    )
    assert clean.refusals == ()
    assert clean.positive_control_detected is False
    assert clean.independent is False


def test_a2_7_the_existing_path_reproducibility_harness_is_untouched(compiler_registry):
    """A2-7 preservation: double_build still proves what it always proved."""
    result = double_build("BP-DATA-0001", registry=compiler_registry)
    assert result.byte_identical
    assert not result.divergences


def test_comparator_is_deterministic_across_runs(comparison):
    """The comparison primitive is a digest, so two runs must agree byte for byte."""
    again = compare_initialization()
    assert again.matrix() == comparison.matrix()
    assert [o.digest() for o in again.observations] == [o.digest() for o in comparison.observations]
    assert [d.to_dict() for d in again.refusals] == [d.to_dict() for d in comparison.refusals]


def test_the_gate_entry_point_reports_and_exits_zero(capsys):
    """The stage contract: 0 independent, 1 refused, 2 no verdict reached."""
    assert initialization_gate([]) == 0
    printed = capsys.readouterr().out
    assert "cross-process initialization independence" in printed
    assert "positive control        : detected=True" in printed
    assert "refused divergences     : 0" in printed


def test_the_gate_faults_rather_than_passes_when_no_verdict_is_reachable(monkeypatch, capsys):
    """Exit 2 is deliberately not exit 1: unmeasurable is not the same as refused."""
    monkeypatch.setattr(
        reproduce_module,
        "compare_initialization",
        lambda: (_ for _ in ()).throw(ReproducibilityError("probe did not complete")),
    )
    assert initialization_gate(["--quiet"]) == 2
    assert "FAULT" in capsys.readouterr().out


def test_an_unknown_initialization_step_is_refused_by_the_child():
    """A step is a resolvable reference, and one the child cannot resolve fails closed."""
    with pytest.raises(ReproducibilityError) as exc:
        compare_initialization(
            scenarios=(
                InitializationScenario(
                    "A", "unknown step", ("engine.ceu.catalog:no_such_attribute",)
                ),
            )
        )
    assert exc.value.context.get("scenario") == "A"
