"""UCOS-CAA-001 — the repository stands under exactly one constitutional authority.

The condition these tests pin, measured before the fix
-----------------------------------------------------
105 tracked JSON instruments carried a top-level ``authority``. 98 of them claimed
nothing — 49 disclaiming outright (``NONE — DERIVED TRUTH``), 48 disclosing
execution-only standing (``ENGINEERING-EXECUTION-ONLY``) and one conveying an assignment
made elsewhere — all under tokens UCOS-UCAF-001 had already classed non-constitutional.
Seven claimed authority outright, each saying it was "upstream of every engine that
reads it", and **not one named the authority it was upstream UNDER**.

Every one of those claims was true about what it authored. Together they were seven
roots, and ``UCKP-ART-01`` admits one. The same missing edge left the two duplications
unmeasurable: ``00-BOOK/DATA/id-ledger.json`` and ``engine/uckp/identity.py`` both mint,
and ``UCOS-UGA-001`` emits a relationship graph while ``engine/uckp/graph.py`` declares
what a relationship IS. Neither was a rival implementation. Both were UNDECLARED
SUBORDINATIONS, which is what a rival looks like to anything that has to check.

What is tested here
-------------------
The repository-level facts, independent of the engine that also measures them:
every claim is bound, every bound instrument carries the block, the derivation is
injective over the real ledger, no second mint exists, and no identifier moved.
:func:`test_the_uga_gate_enforces_every_alignment_invariant` is the one that matters
most — it proves the invariants are wired into the gate ``verify.sh`` already runs,
rather than being measurable only on request.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
BINDING = REPO / "00-BOOK" / "DATA" / "constitutional-authority-alignment.json"
LEDGER = REPO / "00-BOOK" / "DATA" / "id-ledger.json"
LAW = REPO / "engine" / "uckp" / "law.py"
UGA_DECLARATION = REPO / "00-MASTER" / "UCOS-UGA-001" / "uga-declaration.json"
UGA_ENGINE = REPO / "00-MASTER" / "UCOS-UGA-001" / "uga_engine.py"

ALIGNMENT_INVARIANTS = (
    "CAA-INV-01",
    "CAA-INV-02",
    "CAA-INV-03",
    "CAA-INV-04",
    "CAA-INV-05",
    "CAA-INV-06",
    "CAA-INV-07",
)


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def binding() -> dict:
    return _load(BINDING)


@pytest.fixture(scope="module")
def tracked_json() -> list[Path]:
    out = subprocess.run(  # noqa: S603
        ["git", "-C", str(REPO), "ls-files", "-z", "--cached", "--exclude-standard"],  # noqa: S607
        capture_output=True,
        text=True,
        check=True,
    )
    return [REPO / p for p in out.stdout.split("\0") if p.endswith(".json")]


@pytest.fixture(scope="module")
def claims(binding, tracked_json) -> dict[str, str]:
    """Every tracked instrument that claims authority rather than disclaiming it."""
    prefixes = tuple(
        p["prefix"].upper() for p in binding["authority_claim_scan"]["disclaiming_prefixes"]
    )
    found: dict[str, str] = {}
    for path in tracked_json:
        try:
            document = _load(path)
        except ValueError:  # pragma: no cover - a malformed instrument fails the gate
            continue
        value = document.get("authority") if isinstance(document, dict) else None
        if isinstance(value, str) and not value.strip().upper().startswith(prefixes):
            found[path.relative_to(REPO).as_posix()] = value
    return found


# --- the binding itself -------------------------------------------------------------


def test_the_binding_is_authored_truth_held_subordinate(binding) -> None:
    assert binding["schema"] == "ucos-constitutional-authority-alignment"
    assert "AUTHORED REPOSITORY TRUTH" in binding["authority"]
    assert binding["constitutional_superior"]["authority"] == "UCKP-LAW-0001"


def test_the_binding_creates_no_authority(binding) -> None:
    """A binding that conferred authority would be the eighth root, not the fix."""
    goals = " ".join(binding["non_goals"]).lower()
    assert "creating an authority" in goals
    assert binding["authority_roles"]["DERIVED"]["may_hold_authority"] is False


def test_the_binding_agrees_with_the_law_it_derives_under(binding) -> None:
    from engine.uckp.alignment import verify_binding

    assert verify_binding(binding) == ()


def test_the_supreme_authority_is_the_law_in_its_own_home(binding) -> None:
    supreme = binding["supreme_authority"]
    assert supreme["id"] == "UCKP-LAW-0001"
    assert (REPO / supreme["home"]).is_file()
    assert f'LAW_ID = "{supreme["id"]}"' in LAW.read_text(encoding="utf-8")


# --- every claim is bound -----------------------------------------------------------


def test_every_authority_claim_is_bound_to_a_superior(binding, claims) -> None:
    """The whole condition, as one assertion."""
    bound = {entry["instrument"] for entry in binding["subordinate_instruments"]}
    unbound = sorted(set(claims) - bound)
    assert unbound == [], "instruments claiming authority under no superior:\n  " + "\n  ".join(
        unbound
    )


def test_every_bound_instrument_still_claims_authority(binding, claims) -> None:
    """A binding entry for a file that claims nothing is stale, not harmless.

    Role ORTHOGONAL is exempt: by definition (CAA-INV-08) it names no superior to
    claim, and its instrument need not even be JSON — CMG-000001 is markdown.
    """
    stale = sorted(
        entry["instrument"]
        for entry in binding["subordinate_instruments"]
        if entry["instrument"] not in claims and entry["role"] != "ORTHOGONAL"
    )
    assert stale == []


def test_every_bound_instrument_carries_the_block_the_binding_says_it_does(binding) -> None:
    for entry in binding["subordinate_instruments"]:
        if entry["role"] == "ORTHOGONAL":
            continue
        document = _load(REPO / entry["instrument"])
        superior = document["constitutional_superior"]
        assert superior["authority"] == "UCKP-LAW-0001", entry["instrument"]
        assert superior["role"] == entry["role"], entry["instrument"]
        assert superior["articles"] == entry["derives_under"], entry["instrument"]


def test_no_bound_instrument_holds_a_role_that_may_hold_authority(binding) -> None:
    roles = binding["authority_roles"]
    for entry in binding["subordinate_instruments"]:
        assert roles[entry["role"]]["may_hold_authority"] is False, entry["id"]


def test_the_binding_binds_itself(binding) -> None:
    """An alignment register exempt from its own rule is the first parallel authority."""
    instruments = {e["instrument"] for e in binding["subordinate_instruments"]}
    assert BINDING.relative_to(REPO).as_posix() in instruments


# --- identity: one authority, two planes, every id preserved ------------------------


def test_exactly_one_file_holds_the_identity_mint(binding, tracked_json) -> None:
    markers = set(binding["identity_authority_resolution"]["mint_markers"])
    holders = []
    for path in tracked_json:
        try:
            document = _load(path)
        except ValueError:  # pragma: no cover
            continue
        if isinstance(document, dict) and markers & set(document):
            holders.append(path.relative_to(REPO).as_posix())
    assert holders == [LEDGER.relative_to(REPO).as_posix()]


def test_the_ledger_is_declared_a_persistence_binding_not_a_rival(binding) -> None:
    planes = {p["plane"]: p for p in binding["identity_authority_resolution"]["planes"]}
    assert planes["CONSTITUTIONAL_OBJECT"]["role"].startswith("SUPREME")
    assert planes["REPOSITORY_OBJECT"]["role"].startswith("PERSISTENCE")
    assert planes["REPOSITORY_OBJECT"]["home"] == LEDGER.relative_to(REPO).as_posix()


def test_every_repository_identity_derives_into_the_object_model(binding) -> None:
    from engine.uckp.alignment import derivation_is_injective

    ledger = _load(LEDGER)
    identifiers = [
        value
        for name in binding["identity_authority_resolution"]["planes"][1]["maps"]
        for record in ledger[name].values()
        for key in ("universal_id", "observation_id")
        if isinstance(value := record.get(key), str)
    ]
    assert len(identifiers) > 5000, "the population is smaller than the ledger holds"
    assert derivation_is_injective(identifiers) == ()


def test_no_identifier_was_rewritten_to_make_the_derivation_work(binding) -> None:
    """Article 5: an identity once minted never changes. Verbatim is the whole claim."""
    from engine.uckp.alignment import repository_local_urn

    for record in _load(LEDGER)["by_object"].values():
        identifier = record["universal_id"]
        assert repository_local_urn(identifier).endswith(f":{identifier}")


# --- the relationship graph model ---------------------------------------------------


def test_uga_declares_itself_a_projection_of_the_graph_model(binding) -> None:
    declaration = _load(UGA_DECLARATION)
    ownership = declaration["relationship_graph_ownership"]
    assert ownership["model_owner"]["authority"] == "UCKP-ART-07"
    assert ownership["model_owner"]["home"] == "engine/uckp/graph.py"
    assert (REPO / ownership["model_owner"]["home"]).is_file()
    assert declaration["constitutional_superior"]["role"] == "PROJECTION"


def test_every_emitted_relationship_kind_is_bound_to_the_model(binding) -> None:
    graph = _load(REPO / "00-MASTER" / "UCOS-UGA-001" / "04-RELATIONSHIP-GRAPH.json")
    declared = binding["relationship_graph_resolution"]["relationship_kind_bindings"]
    emitted = {edge["kind"] for edge in graph["relationships"]}
    assert emitted, "the projection emitted no edge, so nothing was measured"
    assert emitted <= set(declared), sorted(emitted - set(declared))


def test_the_graph_surface_disclaims_the_model_it_projects() -> None:
    graph = _load(REPO / "00-MASTER" / "UCOS-UGA-001" / "04-RELATIONSHIP-GRAPH.json")
    assert graph["authority"].startswith("NONE")
    assert graph["model_owner"]["home"] == "engine/uckp/graph.py"
    assert "PROJECTION" in graph["standing"]


# --- evidence and observation stay apart --------------------------------------------


def test_every_observation_kind_binds_to_one_of_the_five_evidence_classes() -> None:
    evidence = _load(REPO / "00-BOOK" / "DATA" / "evidence-universe.json")
    observation = _load(REPO / "00-BOOK" / "DATA" / "observation-universe.json")
    classes = set(evidence["evidence_classes"])
    assert len(classes) == 5
    for kind, spec in observation["observation_kinds"].items():
        assert spec["evidence_class"] in classes, kind


def test_neither_register_declares_the_others_subject() -> None:
    evidence = _load(REPO / "00-BOOK" / "DATA" / "evidence-universe.json")
    observation = _load(REPO / "00-BOOK" / "DATA" / "observation-universe.json")
    assert "observation_kinds" not in evidence
    assert "evidence_classes" not in observation


def test_each_of_the_four_truths_names_a_governing_article(binding) -> None:
    """Resolved against the law's own source, so a cited article really exists."""
    law = LAW.read_text(encoding="utf-8")
    separation = binding["evidence_observation_separation"]
    for truth in ("identity_truth", "observation_truth", "evidence_truth", "decision_truth"):
        for article in [separation[truth]["article"], *separation[truth].get("also", [])]:
            assert f'"{article}"' in law, f"{truth} cites {article}"


# --- one object model ---------------------------------------------------------------


def test_only_one_object_model_is_declared(binding) -> None:
    model = binding["object_model"]
    assert model["model"] == "UCKO"
    assert (REPO / model["home"]).is_file()
    declaration = _load(UGA_DECLARATION)
    assert declaration["object_classes"], "the declaration lost its object classes"
    assert model["model"] in declaration["object_model"]["model"]
    assert declaration["object_model"]["home"] == model["home"]


# --- the gate ------------------------------------------------------------------------


def test_the_uga_gate_enforces_every_alignment_invariant() -> None:
    """The invariants must run inside the gate verify.sh already invokes.

    A second gate for the invariants that forbid a second authority would be the joke
    told with a straight face, so this asserts they are in the existing one.
    """
    run = subprocess.run(  # noqa: S603
        [sys.executable, str(UGA_ENGINE), "gate"],  # noqa: S607
        cwd=REPO,
        capture_output=True,
        text=True,
        check=False,
    )
    assert run.returncode == 0, run.stdout + run.stderr
    for invariant in ALIGNMENT_INVARIANTS:
        assert f"[PASS] {invariant}" in run.stdout, run.stdout


def test_verify_sh_reaches_the_alignment_invariants_through_the_existing_stage() -> None:
    """No new stage was added: Stage 6b is still the one and only object-governance gate."""
    verify = (REPO / "verify.sh").read_text(encoding="utf-8")
    assert 'uga_engine.py" gate' in verify or "uga_engine.py gate" in verify
    assert verify.count("uga_engine.py") == 1
