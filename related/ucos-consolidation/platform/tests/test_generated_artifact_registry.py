"""UCOS-CL-015 — the generated-artifact registry invariants.

The defect these guard against is on record. UCOS-RECON-C2 found the eleven UCOS-RIE-001
outputs registered as authored corpus artifacts, each given a permanent identity, because
``00-BOOK/tools/config.py::EXCLUDE_DIR_PREFIXES`` enumerated generated outputs only where
they lived under ``00-BOOK/`` — and ``intelligence/`` did not exist when that list was
written. That is the same root cause UCOS-RECON-C1 had already closed one leg of. The list
could not be wrong about a directory it had never heard of; the architecture was wrong to
have three lists.

Test 12 (``test_a_new_artifact_needs_one_entry_not_several_lists``) is the one that matters
most: it asserts the property whose absence made the earlier drift possible.
"""

from __future__ import annotations

import importlib.util
import itertools
import json
import subprocess
from pathlib import Path
from platform.repository_intelligence import evidence_universe
from platform.repository_intelligence.generated_artifacts import (
    CANONICAL_SAFE_INPUTS,
    EXECUTION_OBSERVATION_CLASSIFICATIONS,
    IDENTITY_ROLES,
    INPUT_CLASSIFICATIONS,
    REGISTRY_PATH,
    load,
    paths_for_owner,
    producer_of,
    reconcile_owner_view,
    validate,
)

import pytest

REPO = Path(__file__).resolve().parents[2]


@pytest.fixture(scope="module")
def artifacts():
    return load(REPO)


def test_registry_exists_and_is_authored() -> None:
    doc = json.loads((REPO / REGISTRY_PATH).read_text(encoding="utf-8"))
    assert doc["schema"] == "ucos-generated-artifact-registry"
    assert doc["version"]
    assert "AUTHORED REPOSITORY TRUTH" in doc["authority"]
    assert doc["entries"], "registry declares no artifacts"


def test_1_every_generated_path_resolves_to_exactly_one_producer(artifacts) -> None:
    seen: dict[str, str] = {}
    for a in artifacts:
        assert (
            a.canonical_path not in seen
        ), f"{a.canonical_path} claimed by {seen.get(a.canonical_path)} and {a.producer}"
        seen[a.canonical_path] = a.producer
    assert producer_of(REPO, "intelligence/UCOS-RIE-MODEL.json") == "intelligence/rie/engine.py"


def test_2_no_two_producers_claim_the_same_canonical_path(artifacts) -> None:
    paths = [a.canonical_path for a in artifacts]
    assert len(paths) == len(set(paths))


def test_3_every_artifact_has_an_owner(artifacts) -> None:
    assert all(a.owner for a in artifacts)


def test_4_every_artifact_has_a_lifecycle(artifacts) -> None:
    assert all(a.lifecycle for a in artifacts)


def test_5_every_artifact_has_an_explicit_input_closure(artifacts) -> None:
    for a in artifacts:
        assert a.input_closure, f"{a.canonical_path} declares no inputs"


def test_6_every_input_carries_a_classification(artifacts) -> None:
    for a in artifacts:
        for inp in a.input_closure:
            klass = a.input_classification.get(inp)
            assert (
                klass in INPUT_CLASSIFICATIONS
            ), f"{a.canonical_path}: input {inp!r} classified {klass!r}"


def test_7_unknown_input_classification_fails_closed(tmp_path: Path) -> None:
    """UNKNOWN is not a placeholder to be filled in later. It is a refusal."""
    repo = tmp_path / "r"
    (repo / "00-BOOK" / "DATA").mkdir(parents=True)
    (repo / REGISTRY_PATH).write_text(
        json.dumps(
            {
                "schema": "ucos-generated-artifact-registry",
                "entries": [
                    {
                        "artifact_id": "X",
                        "canonical_path": "out.json",
                        "producer": "p.py",
                        "owner": "OWN",
                        "lifecycle": "REGENERATED",
                        "input_closure": ["mystery"],
                        "input_classification": {"mystery": "UNKNOWN"},
                        "deterministic": True,
                        "canonical_identity_role": "CANONICAL",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    findings = validate(repo)
    assert any("UNKNOWN" in f for f in findings), findings


def test_8_a_canonical_artifact_may_not_declare_an_environmental_input(tmp_path: Path) -> None:
    """UCOS-CL-005 as a rule, not a repair.

    An RIE artifact that named coverage.xml in its input closure is now UNDECLARABLE. The
    leak is unrepresentable rather than merely removed once, which is the difference
    between fixing a defect and closing its class.
    """
    repo = tmp_path / "r"
    (repo / "00-BOOK" / "DATA").mkdir(parents=True)
    (repo / REGISTRY_PATH).write_text(
        json.dumps(
            {
                "schema": "ucos-generated-artifact-registry",
                "entries": [
                    {
                        "artifact_id": "RIE-HEALTH",
                        "canonical_path": "intelligence/UCOS-RIE-HEALTH.json",
                        "producer": "intelligence/rie/engine.py",
                        "owner": "UCOS-RIE-001",
                        "lifecycle": "REGENERATED",
                        "input_closure": ["coverage.xml"],
                        "input_classification": {"coverage.xml": "ENVIRONMENTAL"},
                        "deterministic": True,
                        "canonical_identity_role": "CANONICAL",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    findings = validate(repo)
    assert any("ENVIRONMENTAL" in f and "CANONICAL" in f for f in findings), findings


def test_9_rib_generated_view_equals_the_registry_view() -> None:
    """The engine's own idea of its outputs and the register's must be one fact."""

    spec = importlib.util.spec_from_file_location(
        "rib_under_test", REPO / "00-MASTER" / "UCOS-RIB-001" / "rib_engine.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    decl = json.loads(
        (REPO / "00-MASTER" / "UCOS-RIB-001" / "rib-blueprint.json").read_text(encoding="utf-8")
    )
    engine_view = module.own_generated_paths(decl)
    assert reconcile_owner_view(REPO, "UCOS-RIB-001", engine_view) == []


def test_10_live_registry_satisfies_every_invariant() -> None:
    findings = validate(REPO)
    assert findings == [], "generated-artifact registry invariants violated:\n  " + "\n  ".join(
        findings
    )


def test_11_every_canonical_artifact_is_tracked(artifacts) -> None:
    """A canonical generated artifact that is not in the tree is a declaration of nothing."""

    tracked = {
        p
        for p in subprocess.run(  # noqa: S603
            ["git", "ls-files", "-z"],  # noqa: S607
            cwd=REPO,
            capture_output=True,
            text=True,
            check=True,
        ).stdout.split("\0")
        if p
    }
    missing = [
        a.canonical_path for a in artifacts if a.canonical and a.canonical_path not in tracked
    ]
    assert not missing, f"canonical artifacts not tracked: {missing}"


def test_12_a_new_artifact_needs_one_entry_not_several_lists(tmp_path: Path) -> None:
    """THE structural property. Declaring a generated artifact is ONE edit.

    Before the registry, a new generated output had to be added to the producer's own
    declaration, to EXCLUDE_DIR_PREFIXES for registration eligibility, and to .gitignore.
    Missing any one of them produced a real, shipped defect. Here, one entry makes the
    artifact known to every derived view at once.
    """
    repo = tmp_path / "r"
    (repo / "00-BOOK" / "DATA").mkdir(parents=True)
    entry = {
        "artifact_id": "NEW",
        "canonical_path": "programme/NEW-OUTPUT.json",
        "producer": "programme/engine.py",
        "owner": "NEW-PROGRAMME",
        "lifecycle": "REGENERATED",
        "input_closure": ["programme/declaration.json"],
        "input_classification": {"programme/declaration.json": "TRACKED_DETERMINISTIC"},
        "deterministic": True,
        "canonical_identity_role": "CANONICAL",
    }
    (repo / REGISTRY_PATH).write_text(
        json.dumps({"schema": "ucos-generated-artifact-registry", "entries": [entry]}),
        encoding="utf-8",
    )
    assert validate(repo) == []
    assert paths_for_owner(repo, "NEW-PROGRAMME") == {"programme/NEW-OUTPUT.json"}
    assert producer_of(repo, "programme/NEW-OUTPUT.json") == "programme/engine.py"


def test_coverage_xml_is_declared_environmental_and_excluded(artifacts) -> None:
    """The register names coverage.xml explicitly, so the exclusion is visible."""
    cov = next(a for a in artifacts if a.canonical_path == "coverage.xml")
    assert cov.canonical_identity_role == "EXCLUDED"
    assert cov.deterministic is False
    assert cov.environmental_dependencies
    assert not cov.canonical


def test_every_producer_that_emits_tracked_artifacts_is_declared(artifacts) -> None:
    """AEE and UAIE declared no outputs at all before this register existed."""
    owners = {a.owner for a in artifacts}
    for required in ("UCOS-RIE-001", "UCOS-RIB-001", "UCOS-AEE-001", "UAIE-000001"):
        assert required in owners, f"{required} emits tracked artifacts but is not declared"


def test_canonical_safe_inputs_excludes_unknown() -> None:
    assert "UNKNOWN" not in CANONICAL_SAFE_INPUTS
    assert "ENVIRONMENTAL" not in CANONICAL_SAFE_INPUTS


# --- CANONICAL_ARTIFACT_INPUT_CLASSIFICATION (UAKOS-CLOSURE-008) --------------------------


def _evidence_universe(repo: Path) -> None:
    """A minimal evidence universe, so an evidence check has a register to consult."""
    (repo / "00-BOOK" / "DATA").mkdir(parents=True, exist_ok=True)
    (repo / "00-BOOK" / "DATA" / "evidence-universe.json").write_text(
        json.dumps(
            {
                "schema": "ucos-evidence-universe",
                "evidence_classes": dict.fromkeys(
                    ["AUDIT", "DEBUG", "IMPROVEMENT", "EXECUTION", "VALIDATION"], "x"
                ),
                "surfaces": [
                    {
                        "surface_id": "EV-TEST",
                        "path_pattern": "programme/evidence/*",
                        "evidence_class": "EXECUTION",
                        "owner": "PROGRAMME",
                        "producer": "programme/engine.py",
                        "retention": "PRESERVED",
                        "input_classification": "EXECUTION_TRANSCRIPT",
                        "canonical_identity_role": "NON_CANONICAL",
                        "may_affect_certification": False,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )


def _one_entry_registry(repo: Path, entry: dict) -> Path:
    (repo / "00-BOOK" / "DATA").mkdir(parents=True, exist_ok=True)
    (repo / REGISTRY_PATH).write_text(
        json.dumps({"schema": "ucos-generated-artifact-registry", "entries": [entry]}),
        encoding="utf-8",
    )
    _evidence_universe(repo)
    return repo


def _entry(**overrides) -> dict:
    entry = {
        "artifact_id": "REPORT",
        "canonical_path": "programme/REPORT.md",
        "producer": "programme/engine.py",
        "owner": "PROGRAMME",
        "lifecycle": "REGENERATED",
        "input_closure": ["programme/evidence/verify.log"],
        "input_classification": {"programme/evidence/verify.log": "EXECUTION_TRANSCRIPT"},
        "deterministic": True,
        "canonical_identity_role": "CANONICAL",
    }
    entry.update(overrides)
    return entry


@pytest.mark.parametrize(
    "classification",
    sorted(EXECUTION_OBSERVATION_CLASSIFICATIONS),
)
def test_13_a_canonical_artifact_may_not_consume_an_execution_observation(
    tmp_path: Path, classification: str
) -> None:
    """UAKOS-CLOSURE-008 as a rule, not a repair.

    Register 06 declared an execution transcript as an input in everything but name: it read
    ``evidence/verify.log`` at render time and embedded its tail, so canonical bytes moved
    whenever the command ran again. That declaration is now undeclarable.
    """
    repo = _one_entry_registry(
        tmp_path / "r",
        _entry(
            input_classification={"programme/evidence/verify.log": classification},
        ),
    )
    findings = validate(repo)
    assert any(
        "CANONICAL_ARTIFACT_INPUT_CLASSIFICATION" in f and classification in f for f in findings
    ), findings


def test_14_non_canonical_is_the_escape_so_evidence_is_kept_not_hidden(tmp_path: Path) -> None:
    """The evidence layer may depend on the run. It simply makes no identity claim.

    This is the half of the rule that keeps it honest: nothing forces a programme to delete or
    conceal an execution transcript to satisfy the invariant.
    """
    repo = _one_entry_registry(
        tmp_path / "r", _entry(canonical_identity_role="NON_CANONICAL", deterministic=False)
    )
    assert validate(repo) == []


def test_15_an_unrecognised_identity_role_fails_closed(tmp_path: Path) -> None:
    repo = _one_entry_registry(tmp_path / "r", _entry(canonical_identity_role="PROBABLY_FINE"))
    assert any("canonical_identity_role" in f for f in validate(repo))
    assert IDENTITY_ROLES == {"CANONICAL", "NON_CANONICAL", "EXCLUDED"}


def test_16_the_registers_declared_vocabulary_matches_the_module() -> None:
    """One fact, one owner. The register documents exactly the classes the code enforces."""
    doc = json.loads((REPO / REGISTRY_PATH).read_text(encoding="utf-8"))
    assert set(doc["input_classifications"]) == set(INPUT_CLASSIFICATIONS)
    assert any("CANONICAL_ARTIFACT_INPUT_CLASSIFICATION" in i for i in doc["invariants"])


def test_17_a_certification_artifact_may_not_consume_a_diagnosis(tmp_path: Path) -> None:
    """R-EV-4: DEBUG and IMPROVEMENT surfaces may support truth; they may not certify it.

    A diagnosis is a measurement of what went wrong and an improvement is a measurement of
    what could be better. Neither is a determination, so an artifact carrying a certification
    role must not take one as an input — the certificate would then rest on evidence produced
    to explain a failure rather than to decide one.

    The rule has THREE conditions and all three are load-bearing, so each is falsified here
    against the same register: an artifact with no certification role is unaffected, one whose
    role is explicitly NONE or QUALITY_GATE_ONLY is exempt by declaration, and one consuming a
    surface outside the forbidden classes is fine whatever its role.
    """
    forbidden = sorted(evidence_universe.CERTIFICATION_FORBIDDEN_CLASSES)
    assert forbidden, "the register forbids no evidence class, so this test would be vacuous"

    # A COUNTER, NOT THE PARAMETERS, names each repository. "" and "NONE" both rendered as
    # "none" and collided on a case-insensitive filesystem, which made two of these cases
    # silently reuse one tree.
    built = itertools.count()

    def _repo_with(*, evidence_class: str, certification_role: str) -> Path:
        repo = tmp_path / f"r{next(built)}"
        repo.mkdir(parents=True)
        _one_entry_registry(
            repo,
            _entry(canonical_identity_role="NON_CANONICAL", certification_role=certification_role),
        )
        registry = repo / "00-BOOK" / "DATA" / "evidence-universe.json"
        doc = json.loads(registry.read_text(encoding="utf-8"))
        doc["surfaces"][0]["evidence_class"] = evidence_class
        registry.write_text(json.dumps(doc), encoding="utf-8")
        return repo

    refused = validate(_repo_with(evidence_class=forbidden[0], certification_role="CERTIFYING"))
    assert any("R-EV-4" in f for f in refused), refused
    assert any(forbidden[0] in f for f in refused)

    # 1. No certification role at all: the artifact certifies nothing, so nothing is at stake.
    assert validate(_repo_with(evidence_class=forbidden[0], certification_role="")) == []
    # 2. A role the register declares exempt.
    for exempt in ("NONE", "QUALITY_GATE_ONLY"):
        assert validate(_repo_with(evidence_class=forbidden[0], certification_role=exempt)) == []
    # 3. A certifying artifact over a surface outside the forbidden classes.
    assert validate(_repo_with(evidence_class="EXECUTION", certification_role="CERTIFYING")) == []
