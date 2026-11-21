"""UCOS-NUC-001 — validation, certification, the identifier dictionary, and the CLI."""

from __future__ import annotations

import json

import pytest

from engine.context.location import AXIS_DERIVATION, build_frame_registry
from engine.nucleus import certification, cli
from engine.nucleus.certification import AUTHORITY_VACANCY, Verdict, certify, validate
from engine.nucleus.context import evolve_in_context
from engine.nucleus.errors import CertificationError
from engine.nucleus.evolution import EvolutionLedger, state_must_grow
from engine.nucleus.lineage import ledger_for
from engine.nucleus.model import CapabilityDeclaration, CapabilityRecord, SubjectDeclaration
from engine.nucleus.registry import NucleusRegistry, build_seed_registry
from engine.registry.universal.dictionary import (
    IdentifierDictionary,
    IdentifierEntry,
    dictionary_for,
)
from engine.registry.universal.errors import RegistrationValidationError
from engine.registry.universal.identity import (
    RegistryKind,
    deterministic_id,
    is_well_formed,
    kind_names,
    parse_kind,
    parse_kind_name,
    register_kind,
    resolve_kind_code,
)

# -- identifier architecture ------------------------------------------------- #


def test_the_structural_kinds_mint_under_the_one_authority():
    for kind, prefix in (
        (RegistryKind.NUCLEUS, "UCOS-NUC-"),
        (RegistryKind.LAYER, "UCOS-LYR-"),
        (RegistryKind.COMPOSITION, "UCOS-CMPO-"),
        (RegistryKind.LOCATION, "UCOS-LOC-"),
    ):
        minted = deterministic_id(kind, "ucos.probe", "k")
        assert minted.startswith(prefix)
        assert parse_kind(minted) is kind
        assert parse_kind_name(minted) == kind.value
        assert is_well_formed(minted)


def test_every_kind_code_is_unique():
    codes = [k.code for k in RegistryKind]
    assert len(codes) == len(set(codes))
    assert len(codes) >= 29


def test_a_future_kind_is_admitted_by_registration_not_by_editing_the_enum():
    code = register_kind("GLYPH", "GLY")
    assert code == "GLY"
    assert register_kind("GLYPH", "GLY") == "GLY"
    minted = deterministic_id("GLYPH", "ucos.probe", "k")
    assert minted.startswith("UCOS-GLY-")
    assert parse_kind_name(minted) == "GLYPH"
    assert "GLYPH" in kind_names()
    assert resolve_kind_code("GLYPH") == "GLY"
    with pytest.raises(RegistrationValidationError):
        parse_kind(minted)


def test_kind_registration_refuses_collisions_and_malformed_codes():
    with pytest.raises(RegistrationValidationError):
        register_kind("SERVICE", "SV2")
    with pytest.raises(RegistrationValidationError):
        register_kind("OTHER", "NUC")
    with pytest.raises(RegistrationValidationError):
        register_kind("OTHER", "lower")
    with pytest.raises(RegistrationValidationError):
        register_kind("", "AB")
    register_kind("REBIND", "RBD")
    with pytest.raises(RegistrationValidationError):
        register_kind("REBIND", "RBX")


def test_malformed_identifiers_are_refused():
    for bad in ("", "UCOS", "UCOS-NUC", "OTHER-NUC-abc", "UCOS-ZZZZ-abc", "UCOS-NUC-"):
        assert is_well_formed(bad) is False
        with pytest.raises(RegistrationValidationError):
            parse_kind_name(bad)


# -- the identifier dictionary ----------------------------------------------- #


def test_every_registered_thing_appears_in_the_dictionary_exactly_once():
    registry = build_seed_registry()
    dictionary = dictionary_for(registry)
    expected = registry.counts()["subjects"] + registry.counts()["capabilities"]
    assert len(dictionary) == expected
    assert len(set(dictionary.identifiers())) == expected
    assert dictionary.is_verified
    verification = dictionary.verify()
    assert verification["status"] == "PASS"
    assert verification["unreproducible"] == []
    assert verification["unparsed"] == []
    assert verification["duplicated_natural_keys"] == []
    assert verification["parse_coverage"] == 1.0


def test_the_dictionary_resolves_by_identifier_and_by_identity_tuple():
    registry = build_seed_registry()
    dictionary = dictionary_for(registry)
    nucleus = registry.nucleus("payment")
    entry = dictionary.resolve(nucleus.universal_id)
    assert entry.natural_key == "payment"
    assert entry.kind == "NUCLEUS"
    assert dictionary.lookup("NUCLEUS", entry.namespace, "payment") == entry
    assert nucleus.universal_id in dictionary
    with pytest.raises(RegistrationValidationError):
        dictionary.resolve("UCOS-NUC-ffffffffffff")


def test_the_dictionary_is_idempotent_and_refuses_rebinding():
    dictionary = IdentifierDictionary()
    first = dictionary.assign(RegistryKind.NUCLEUS, "ucos.probe", "payment")
    assert dictionary.assign(RegistryKind.NUCLEUS, "ucos.probe", "payment") == first
    forged = IdentifierEntry(
        universal_id=first.universal_id,
        kind="NUCLEUS",
        namespace="ucos.probe",
        natural_key="different",
    )
    with pytest.raises(RegistrationValidationError):
        dictionary.add(forged)
    assert dictionary.unreproducible() == ()


def test_the_dictionary_refuses_a_foreign_identifier():
    with pytest.raises(RegistrationValidationError):
        IdentifierEntry(
            universal_id="NOT-A-UCOS-ID", kind="NUCLEUS", namespace="ucos.probe", natural_key="k"
        )


def test_the_dictionary_replays_from_its_own_document():
    registry = build_seed_registry()
    dictionary = dictionary_for(registry)
    document = dictionary.to_document()
    rebuilt = IdentifierDictionary.from_document(document)
    assert rebuilt.digest() == dictionary.digest()
    assert rebuilt.to_json() == dictionary.to_json()
    assert document["closed_set"] is False
    with pytest.raises(RegistrationValidationError):
        IdentifierDictionary.from_document({})


def test_the_dictionary_reports_its_population_by_kind():
    dictionary = dictionary_for(build_seed_registry())
    by_kind = dictionary.by_kind()
    assert by_kind["NUCLEUS"] == 43
    assert by_kind["COMPOSITION"] == 26
    assert by_kind["LAYER"] == 14
    assert len(dictionary.entries(kind=RegistryKind.NUCLEUS)) == 43
    assert dictionary.entries(namespace="ucos.capability")


def test_a_detectably_corrupt_entry_is_reported():
    dictionary = IdentifierDictionary()
    entry = IdentifierEntry(
        universal_id=deterministic_id(RegistryKind.NUCLEUS, "ucos.probe", "a"),
        kind="NUCLEUS",
        namespace="ucos.probe",
        natural_key="b",
    )
    dictionary.add(entry)
    assert dictionary.unreproducible() == (entry.universal_id,)
    assert dictionary.verify()["status"] == "FAIL"
    assert dictionary.is_verified is False


# -- validation + certification ---------------------------------------------- #


def test_the_seed_population_validates():
    report = validate(build_seed_registry())
    assert report.status == "VALID"
    assert report.failures == ()
    # CV-01…CV-10 structural, CV-13…CV-16 contextual. The context axis is unconditional:
    # nothing in this system executes outside a resolved reality, so it is not opt-in.
    assert len(report.checks) == 14
    assert {c.check_id for c in report.checks} >= {"CV-13", "CV-14", "CV-15", "CV-16"}
    assert report.digest() == report.digest()
    assert report.to_dict()["ownership_gate"]["status"] == "PASS"


def test_validation_includes_evolution_when_supplied():
    registry = build_seed_registry()
    ledger = ledger_for(registry)
    evolution = EvolutionLedger(lineage=ledger, validator=state_must_grow)
    evolve_in_context(
        evolution,
        build_frame_registry().resolve("planetary-a1"),
        subject_id=registry.nucleus("payment").universal_id,
        subject_key="payment",
        change="c",
        authority="A",
        state={"capability": 1},
    )
    report = validate(registry, lineage=ledger, evolution=evolution)
    assert report.passed
    assert {c.check_id for c in report.checks} >= {"CV-11", "CV-12", "CV-18"}


def test_certification_is_capped_at_provisional_and_says_why():
    certificate = certify(build_seed_registry())
    assert certificate.verdict is Verdict.CERTIFIED_PROVISIONAL
    assert certificate.certified is True
    assert certificate.ceiling_reason == AUTHORITY_VACANCY
    payload = certificate.to_dict()
    assert payload["verdict_ceiling"] == Verdict.CERTIFIED_PROVISIONAL.value
    assert "FINALIZED" not in {v.value for v in Verdict}
    assert certificate.certificate_id.startswith("UCOS-CERT-")
    assert certificate.digest() == certificate.digest()


def test_certification_is_deterministic_across_identical_populations():
    first = certify(build_seed_registry())
    second = certify(build_seed_registry())
    assert first.certificate_id == second.certificate_id
    assert first.digest() == second.digest()


def test_an_invalid_population_cannot_be_certified():
    fresh = NucleusRegistry()
    fresh.register_subject(SubjectDeclaration(key="payment", title="Payment", concept="payment"))
    layer = fresh.register_subject(SubjectDeclaration(key="platform", title="Platform Layer"))
    fresh.register_capability(
        CapabilityDeclaration(key="invoice", title="Invoice", owner="payment")
    )
    record = fresh.capability("invoice")
    fresh._capabilities["invoice"] = CapabilityRecord(  # noqa: SLF001 - forced unlawful state
        universal_id=record.universal_id,
        key=record.key,
        title=record.title,
        owner_key=layer.key,
        owner_id=layer.universal_id,
        namespace=record.namespace,
    )
    with pytest.raises(CertificationError) as exc:
        certify(fresh)
    assert "CV-01" in exc.value.detail["failures"]


def test_checks_serialise_with_their_measurement():
    report = validate(build_seed_registry())
    payload = report.checks[0].to_dict()
    assert payload["status"] == "PASS"
    assert set(payload) == {"check_id", "name", "status", "measured", "expected", "detail"}
    assert certification.AUTHORITY_VACANCY


# -- the CLI ----------------------------------------------------------------- #


@pytest.mark.parametrize(
    "argv",
    [
        ["law"],
        ["catalog"],
        ["registry"],
        ["gate"],
        ["order"],
        ["lineage"],
        ["dictionary"],
        ["validate"],
        ["certify"],
        ["compose"],
        ["compose", "--composition", "commerce"],
        ["lifecycle"],
        ["lifecycle", "--subject", "UCOS-NUC-000000000001"],
        ["evolve", "--subject", "payment"],
        ["context"],
        ["context", "--frame", "planetary-a1"],
        ["rebase", "--subject", "s", "--frames", "planetary-a1", "planetary-b4"],
        ["dictionary", "--with-context"],
        ["validate", "--frame", "planetary-a1"],
        ["certify", "--frame", "planetary-a1"],
        ["evolve", "--subject", "payment", "--frame", "planetary-a1"],
        ["context-validate"],
        ["context-certify"],
        ["replay"],
        ["replay", "--frame", "planetary-a1"],
    ],
)
def test_every_subcommand_succeeds_and_emits_canonical_json(argv, capsys):
    assert cli.main(argv) == 0
    payload = json.loads(capsys.readouterr().out)
    assert isinstance(payload, dict)


def test_the_cli_reports_an_incomplete_frame_as_a_failure(capsys):
    assert cli.main(["context", "--frame", "unresolved"]) == 1
    payload = json.loads(capsys.readouterr().out)
    assert payload["complete"] is False
    # Every declared axis, whatever the axis set currently is — asserting a literal count
    # here would make adding a nineteenth axis look like a regression.
    assert len(payload["unresolved"]) == len(AXIS_DERIVATION)
    assert payload["reality_context_resolved"] is False


def test_the_cli_refuses_to_certify_in_an_incomplete_frame(capsys):
    assert cli.main(["certify", "--frame", "partial-frame-p0"]) == 1
    payload = json.loads(capsys.readouterr().out)
    assert payload["error"] == "ContextBindingViolation"
    assert payload["detail"]["unresolved"]


def test_the_cli_refuses_to_validate_in_an_incomplete_frame(capsys):
    assert cli.main(["validate", "--frame", "unresolved"]) == 1
    assert json.loads(capsys.readouterr().out)["error"] == "ContextBindingViolation"


def test_a_rebase_that_changes_nothing_is_a_gate_failure(capsys):
    assert cli.main(["rebase", "--subject", "s", "--frames", "planetary-a1", "planetary-a1"]) == 1
    assert json.loads(capsys.readouterr().out)["differing_count"] == 0


def test_the_replay_command_proves_the_whole_fixed_point(capsys):
    assert cli.main(["replay", "--frame", "planetary-a1"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["fixed_point"] is True
    assert payload["lifecycle"]["fixed_point"] is True
    assert payload["location"]["fixed_point"] is True
    assert payload["certification"]["fixed_point"] is True
    assert payload["frame"] == "planetary-a1"


def test_the_dictionary_enumerates_frames_only_when_asked(capsys):
    assert cli.main(["dictionary"]) == 0
    without = json.loads(capsys.readouterr().out)["by_kind"]
    assert cli.main(["dictionary", "--with-context"]) == 0
    with_context = json.loads(capsys.readouterr().out)["by_kind"]
    assert "LOCATION" not in without
    assert with_context["LOCATION"] > 0 and with_context["CONTEXT"] > 0


def test_the_cli_translates_a_constitutional_refusal(capsys):
    assert cli.main(["evolve", "--subject", "absent-subject"]) == 1
    payload = json.loads(capsys.readouterr().out)
    assert payload["error"] == "RegistrationError"


def test_the_cli_requires_a_command():
    with pytest.raises(SystemExit):
        cli.main([])
