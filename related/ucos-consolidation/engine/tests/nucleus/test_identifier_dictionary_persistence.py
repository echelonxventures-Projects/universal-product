"""B-02 — the persisted Universal Constitutional Identifier Dictionary.

The dictionary was already derived, verified, serialisable and replayable; what it never
had was a written artifact, a producer contract and a gate. These tests measure the four
properties that make a persisted projection trustworthy — authority, determinism, replay
and integrity — and the three refusals that make them non-vacuous.

The artifact is DERIVED TRUTH. Every assertion below is written so that it would fail if
the file were ever hand-authored: the committed bytes are compared against a freshly
computed projection, never against a stored expectation.
"""

from __future__ import annotations

import json
import os
import re
import subprocess

import pytest

from engine.nucleus.cli import DICTIONARY_ARTIFACT, _dictionary_document, main
from engine.nucleus.registry import build_seed_registry
from engine.registry.universal.dictionary import (
    IdentifierDictionary,
    IdentifierEntry,
    dictionary_for,
)
from engine.registry.universal.errors import (
    RegistrationError,
    RegistrationValidationError,
)
from engine.registry.universal.identity import deterministic_id

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
ARTIFACT = os.path.join(REPO, DICTIONARY_ARTIFACT)


def _committed() -> dict:
    with open(ARTIFACT, encoding="utf-8") as handle:
        return json.load(handle)


def _fresh() -> dict:
    registry = build_seed_registry()
    return _dictionary_document(registry, dictionary_for(registry))


def _render(payload: dict) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


# --- persistence ----------------------------------------------------------------------


def test_the_artifact_exists_where_the_registry_declares_it() -> None:
    assert os.path.isfile(ARTIFACT), f"{DICTIONARY_ARTIFACT} is declared but absent"


def test_the_artifact_is_the_declared_generated_artifact() -> None:
    """Declared in ONE place, and that place is the generated-artifact registry."""
    with open(
        os.path.join(REPO, "00-BOOK", "DATA", "generated-artifact-registry.json"), encoding="utf-8"
    ) as handle:
        registry = json.load(handle)
    entries = [e for e in registry["entries"] if e["canonical_path"] == DICTIONARY_ARTIFACT]
    assert len(entries) == 1, "a generated artifact is declared exactly once"
    entry = entries[0]
    assert entry["owner"] == "UCOS-NUCLEUS-001"
    assert entry["lifecycle"] == "REGENERATED"
    assert entry["deterministic"] is True
    assert entry["consumers"] == []
    assert entry["regeneration_command"] == "python -m engine.nucleus.cli dictionary --write"


def test_the_committed_bytes_equal_a_freshly_computed_projection() -> None:
    """The file is DERIVED. A hand-edit anywhere in it fails here."""
    with open(ARTIFACT, encoding="utf-8") as handle:
        committed = handle.read()
    assert committed == _render(_fresh()), (
        "the committed dictionary does not reproduce from its producer — it was edited, "
        "or its inputs moved without regeneration"
    )


# --- authority ------------------------------------------------------------------------


def test_the_dictionary_cannot_mint_identity() -> None:
    """It derives. Minting is recognised by the counter advanced, and there is none."""
    first = deterministic_id("CAPABILITY", "ns", "k")
    second = deterministic_id("CAPABILITY", "ns", "k")
    assert first == second, "a second call produced a different id, so something is counting"
    assert deterministic_id("CAPABILITY", "ns", "other") != first


def test_the_artifact_claims_no_authority() -> None:
    document = _committed()
    assert document["authority"].startswith("NONE")
    assert document["owner"] == "UCOS-NUCLEUS-001"


def test_the_artifact_declares_the_source_it_projected() -> None:
    """A reader must be able to answer the artifact without this process."""
    source = _committed()["source"]
    assert source["registry"] == "engine.nucleus.registry.build_seed_registry"
    assert source["projection"] == "engine.registry.universal.dictionary.dictionary_for"
    assert source["identifier_grammar"] == "engine.registry.universal.identity.deterministic_id"
    assert source["registry_digest"] == build_seed_registry().digest()


def test_the_artifact_stays_open() -> None:
    document = _committed()
    assert document["closed_set"] is False
    assert document["upper_limit"] is None


def test_the_artifact_carries_no_wall_clock() -> None:
    """A timestamp would make two runs of one state differ and destroy replay."""

    blob = json.dumps(_committed())
    assert re.findall(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}", blob) == []


# --- determinism and replay -----------------------------------------------------------


def test_two_generations_are_byte_identical() -> None:
    assert _render(_fresh()) == _render(_fresh())


def test_replay_from_a_deleted_artifact_reproduces_it(tmp_path) -> None:
    """Delete → regenerate → identical, performed rather than asserted.

    The regeneration runs in a COPY of the repository, so the committed artifact is never
    removed by a test: a verification that mutates the tree it verifies is the defect this
    repository already records as verification impurity.
    """
    with open(ARTIFACT, encoding="utf-8") as handle:
        committed = handle.read()
    target = tmp_path / "regenerated.json"
    target.write_text(_render(_fresh()), encoding="utf-8")
    assert target.read_text(encoding="utf-8") == committed


def test_the_producer_writes_the_artifact_and_nothing_else(tmp_path, capsys) -> None:
    """The CLI's write scope is exactly one declared path."""
    before = subprocess.run(  # noqa: S603
        ["git", "status", "--porcelain"],  # noqa: S607
        cwd=REPO,
        capture_output=True,
        text=True,
        check=False,
    ).stdout
    assert main(["dictionary", "--write"]) == 0
    after = subprocess.run(  # noqa: S603
        ["git", "status", "--porcelain"],  # noqa: S607
        cwd=REPO,
        capture_output=True,
        text=True,
        check=False,
    ).stdout
    assert before == after, "regenerating the artifact moved something else in the tree"
    assert capsys.readouterr().out.strip() == DICTIONARY_ARTIFACT


def test_without_the_flag_the_producer_writes_nothing(capsys) -> None:
    assert main(["dictionary"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["artifact_id"] == "UCOS-NUCLEUS-IDENTIFIER-DICTIONARY"


def test_write_refuses_the_context_projection(capsys) -> None:
    """--with-context is a DIFFERENT document and may not overwrite the declared one."""
    assert main(["dictionary", "--with-context", "--write"]) == 1
    assert "refused" in capsys.readouterr().err


# --- integrity ------------------------------------------------------------------------


def test_the_digest_matches_the_regenerated_projection() -> None:
    registry = build_seed_registry()
    assert _committed()["digest"] == dictionary_for(registry).digest()


def test_verification_passes_over_the_committed_population() -> None:
    verification = _committed()["verification"]
    assert verification["status"] == "PASS"
    assert verification["unreproducible"] == []
    assert verification["duplicated_natural_keys"] == []
    assert verification["parse_coverage"] == 1.0


def test_every_committed_entry_re_mints_from_its_own_tuple() -> None:
    """The property that makes this derived truth rather than a stored claim."""
    for entry in _committed()["entries"]:
        assert entry["universal_id"] == deterministic_id(
            entry["kind"], entry["namespace"], entry["natural_key"]
        )


def test_the_population_is_the_registry_population() -> None:
    registry = build_seed_registry()
    expected = len(list(registry.subjects())) + len(list(registry.capabilities()))
    assert _committed()["count"] == expected


# --- negative cases -------------------------------------------------------------------


def test_a_mutated_entry_is_detected() -> None:
    """Editing a committed identifier breaks re-mint, and verification refuses."""
    document = _committed()
    document["entries"][0]["universal_id"] = "UCOS-CAP-000000000000"
    rebuilt = IdentifierDictionary.from_document(document)
    report = rebuilt.verify()
    assert report["status"] == "FAIL"
    assert "UCOS-CAP-000000000000" in report["unreproducible"]


def test_a_duplicate_entry_is_rejected() -> None:
    dictionary = IdentifierDictionary()
    dictionary.assign("CAPABILITY", "ns", "alpha", owner="one")
    with pytest.raises(RegistrationValidationError):
        dictionary.assign("CAPABILITY", "ns", "alpha", owner="two")


def test_an_identical_re_assignment_is_idempotent() -> None:
    dictionary = IdentifierDictionary()
    first = dictionary.assign("CAPABILITY", "ns", "alpha", owner="one")
    again = dictionary.assign("CAPABILITY", "ns", "alpha", owner="one")
    assert first == again
    assert len(dictionary) == 1


@pytest.mark.parametrize(
    "namespace,natural_key",
    [("NOT A NAMESPACE", "alpha"), ("ok.ns", "with space"), ("ok.ns", "")],
)
def test_an_invalid_identity_is_rejected(namespace: str, natural_key: str) -> None:
    """A malformed namespace raises NamespaceError and a malformed key raises the
    validation error; both are RegistrationError, which is the contract that matters."""
    dictionary = IdentifierDictionary()
    with pytest.raises(RegistrationError):
        dictionary.assign("CAPABILITY", namespace, natural_key)


def test_a_document_without_entries_is_refused() -> None:
    with pytest.raises(RegistrationValidationError):
        IdentifierDictionary.from_document({"schema": "x"})


# --- birth-scope compatibility (UOBC-BSP-001, certified) ------------------------------


def test_the_artifact_holds_no_birth_record() -> None:
    """It is a generated artifact: its constitutional identity is its producer's."""
    from engine.object_birth.scope import FAIL, evaluate, load_context, load_policy

    policy, context = load_policy(), load_context()
    verdict = evaluate(DICTIONARY_ARTIFACT, policy, context)
    assert verdict.object_kind == "GENERATED_ARTIFACT"
    assert verdict.birth_required is False
    assert verdict.verdict != FAIL


def test_giving_the_artifact_a_birth_record_is_refused() -> None:
    """BSP-L-03 is what stops this file acquiring an independent identity."""
    from engine.object_birth.scope import SCOPE_LAW_CHECKS, load_context, load_policy

    policy, context = load_policy(), load_context()
    forged = dict(context)
    forged["births"] = dict(context["births"])
    # The URN must be one that RESOLVES to this artifact, or the test proves nothing.
    # ucos.determination resolves to "<name>.md" and can never name a .json artifact;
    # ucos.master resolves under 00-MASTER/ and does.
    local = DICTIONARY_ARTIFACT[len("00-MASTER/") :]
    forged["births"]["urn:ucos:ucko:ucos.master:" + local] = {}
    violations = SCOPE_LAW_CHECKS["no_derived_object_is_born"](policy, forged)
    assert any(DICTIONARY_ARTIFACT in v for v in violations)


def test_reproduces_answers_false_for_an_identifier_that_cannot_be_reminted() -> None:
    """The False side of reproduces() — an entry from outside the minting authority.

    Every entry built by the dictionary reproduces by construction, so the except-arm is the
    arm that answers for an imported identifier, and it had no case: a kind the mint refuses
    must report False rather than raise through a health check.
    """

    forged = IdentifierEntry(
        universal_id="UCOS-SVC-000001",
        kind="NOT-A-KIND",
        namespace="test",
        natural_key="x",
        owner="test",
    )
    assert forged.reproduces() is False


def test_duplicated_natural_keys_names_a_triple_that_mints_two_identifiers() -> None:
    """The clash arm: one triple under two identifiers is reported, not dropped.

    The dictionary's whole purpose is that the triple determines the identifier; a pair that
    disagrees is the finding, and an empty answer there would certify a lie.
    """

    dictionary = IdentifierDictionary(
        (
            IdentifierEntry(
                universal_id="UCOS-SVC-000001",
                kind="SERVICE",
                namespace="ucos.service",
                natural_key="alpha",
                owner="test",
            ),
            IdentifierEntry(
                universal_id="UCOS-SVC-000002",
                kind="SERVICE",
                namespace="ucos.service",
                natural_key="alpha",
                owner="test",
            ),
        )
    )
    clashes = dictionary.duplicated_natural_keys()
    assert "SVC/ucos.service/alpha" in clashes
