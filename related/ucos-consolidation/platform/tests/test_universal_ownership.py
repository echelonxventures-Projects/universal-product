"""Tests — Universal Ownership Framework (UCOS-UOF-001)."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from platform.foundation.services import ServiceRegistry
from platform.universal_ownership import (
    OWNERSHIP_CONTRACTS,
    REASON_CONTEST_UNSETTLED,
    REASON_INELIGIBLE_ZONE,
    REASON_NO_CONSTITUTIVE_DECLARATION,
    REASON_NO_EVIDENCE,
    REASON_SUBJECT_NOT_REGISTERED,
    RULE_CONTEST_SETTLED,
    RULE_SOLE_DECLARATION,
    UNASSIGNED_OWNER,
    CallableEvidenceProvider,
    DeclaredAssignmentProvider,
    DeclaredIdentityProvider,
    DefinitionalLocatorProvider,
    EvidenceKind,
    EvidenceProviderDescriptor,
    EvidenceProviderRegistry,
    OwnershipDeclaration,
    OwnershipDeclarationContract,
    OwnershipDetermination,
    OwnershipDeterminationEngine,
    OwnershipEvidence,
    OwnershipRecord,
    OwnershipRequirement,
    OwnershipStanding,
    RegistrationEvidenceProvider,
    bootstrap_ownership,
    declared_identities,
    default_ownership_contract,
    ownership_contract_names,
    register_ownership,
)
from platform.universal_ownership.bootstrap import catalog_path, default_evidence_providers
from platform.universal_ownership.cli import _print_summary
from platform.universal_ownership.cli import main as ownership_main
from platform.universal_ownership.contracts import OwnershipGranularity
from platform.universal_ownership.determination import CANONICAL_HOME_REFUSER
from platform.universal_ownership.errors import (
    OwnershipContractError,
    OwnershipDeterminationError,
    OwnershipEvidenceError,
    OwnershipFabricationError,
    OwnershipProviderConflictError,
)
from platform.universal_ownership.evidence import (
    EvidenceRefusal,
    RoleLocatorProvider,
    read_declared_identities,
)
from platform.universal_truth import Subject, TruthPolicy, TruthZone, default_truth_policy
from platform.universal_truth.eligibility import CanonicalHomePolicy, EligibilityLedger

import pytest

HOME = "02-MASTER/UCOS-COMP-000000-CONSTITUTION.md"
EVIDENCE_ONLY = "00-SOURCE/VISION/UCOS-COMP-000001.docx"


def _policy() -> TruthPolicy:
    return default_truth_policy()


def _subject(subject_id: str, *locators: str) -> Subject:
    return Subject.create(subject_id, locators=locators)


def _engine(*providers: object, **kwargs: object) -> OwnershipDeterminationEngine:
    return OwnershipDeterminationEngine(
        EvidenceProviderRegistry(providers),  # type: ignore[arg-type]
        policy=kwargs.pop("policy", _policy()),
        **kwargs,  # type: ignore[arg-type]
    )


# --------------------------------------------------------------------------- vocabulary


def test_evidence_kind_constitutive_split() -> None:
    assert EvidenceKind.DECLARED_ASSIGNMENT.constitutive is True
    assert EvidenceKind.DEFINITIONAL_LOCATOR.constitutive is True
    assert EvidenceKind.REGISTRATION.constitutive is False
    assert EvidenceKind.CORROBORATION.constitutive is False
    assert EvidenceKind.coerce("delegation") is EvidenceKind.DELEGATION
    assert EvidenceKind.coerce(EvidenceKind.DELEGATION) is EvidenceKind.DELEGATION
    with pytest.raises(OwnershipContractError):
        EvidenceKind.coerce("invented")
    with pytest.raises(OwnershipContractError):
        EvidenceKind.coerce(1)


def test_evidence_contract_guards() -> None:
    with pytest.raises(OwnershipContractError):
        OwnershipEvidence.create(" ", "owner", EvidenceKind.DELEGATION)
    with pytest.raises(OwnershipContractError):
        OwnershipEvidence.create("S", " ", EvidenceKind.DELEGATION)
    with pytest.raises(OwnershipContractError):
        OwnershipEvidence.create("S", UNASSIGNED_OWNER, EvidenceKind.DELEGATION)
    with pytest.raises(OwnershipContractError):
        OwnershipEvidence.create("S", "owner", EvidenceKind.DELEGATION, precedence="high")
    evidence = OwnershipEvidence.create(
        "S", "owner", "delegation", locator="a.md", provider_id="p", authority="A"
    )
    assert evidence.evidence_id.startswith("UCOS-UOFE-")
    assert evidence.constitutive is True
    assert evidence.order_key[0] == -100
    assert evidence.to_dict()["constitutive"] is True
    assert evidence.fingerprint()


# --------------------------------------------------------------------------- contract


def test_ownership_declaration_contract_is_published() -> None:
    contract = default_ownership_contract()
    assert contract.requirement_ids == tuple(f"OWN-REQ-00{n}" for n in range(1, 8))
    assert contract.mandatory_ids() == contract.requirement_ids
    assert contract.requirement("OWN-REQ-001").statement
    assert contract.contract_id.startswith("UCOS-UOFC-")
    assert contract.fingerprint()
    assert contract.to_dict()["version"] == "1.0.0"
    with pytest.raises(OwnershipContractError):
        contract.requirement("OWN-REQ-999")


def test_contract_construction_guards() -> None:
    with pytest.raises(OwnershipContractError):
        OwnershipDeclarationContract.create(())
    with pytest.raises(OwnershipContractError):
        OwnershipDeclarationContract.create(("nope",))  # type: ignore[arg-type]
    duplicate = OwnershipRequirement("R", "statement")
    with pytest.raises(OwnershipContractError):
        OwnershipDeclarationContract.create((duplicate, duplicate))


def test_declaration_refuses_to_exist_without_evidence_or_authority() -> None:
    with pytest.raises(OwnershipContractError):
        OwnershipDeclaration.create("S", "owner", authority="A", kind=EvidenceKind.DELEGATION)
    with pytest.raises(OwnershipContractError):
        OwnershipDeclaration.create(
            "S", "owner", authority=" ", kind=EvidenceKind.DELEGATION, evidence_ids=("e",)
        )
    with pytest.raises(OwnershipContractError):
        OwnershipDeclaration.create(
            "S", "owner", authority="A", kind=EvidenceKind.REGISTRATION, evidence_ids=("e",)
        )
    declaration = OwnershipDeclaration.create(
        "S", "owner", authority="A", kind=EvidenceKind.DELEGATION, evidence_ids=("e",)
    )
    assert declaration.declaration_id.startswith("UCOS-UOFD-")
    assert declaration.rule == RULE_SOLE_DECLARATION
    assert declaration.fingerprint()


def test_record_guards_and_projection() -> None:
    declaration = OwnershipDeclaration.create(
        "S", "owner", authority="A", kind=EvidenceKind.DELEGATION, evidence_ids=("e",)
    )
    with pytest.raises(OwnershipContractError):
        OwnershipRecord.create("S", "declared")  # type: ignore[arg-type]
    with pytest.raises(OwnershipContractError):
        OwnershipRecord.create("S", OwnershipStanding.DECLARED)
    with pytest.raises(OwnershipContractError):
        OwnershipRecord.create(
            "S", OwnershipStanding.UNRESOLVED, declaration=declaration, reasons=("R",)
        )
    with pytest.raises(OwnershipContractError):
        OwnershipRecord.create("S", OwnershipStanding.UNRESOLVED)
    record = OwnershipRecord.create("S", OwnershipStanding.DECLARED, declaration=declaration)
    assert record.owner == "owner"
    assert record.declared is True
    assert record.record_id.startswith("UCOS-UOFR-")
    assert record.fingerprint()
    absent = OwnershipRecord.create(
        "T", OwnershipStanding.UNRESOLVED, reasons=(REASON_NO_EVIDENCE,)
    )
    assert absent.owner == UNASSIGNED_OWNER
    assert absent.to_dict()["declaration"] is None


def test_determination_views() -> None:
    declaration = OwnershipDeclaration.create(
        "A", "owner", authority="Auth", kind=EvidenceKind.DELEGATION, evidence_ids=("e",)
    )
    determination = OwnershipDetermination.create(
        [
            OwnershipRecord.create("A", OwnershipStanding.DECLARED, declaration=declaration),
            OwnershipRecord.create(
                "B", OwnershipStanding.UNRESOLVED, reasons=(REASON_NO_EVIDENCE,)
            ),
            OwnershipRecord.create(
                "C", OwnershipStanding.CONTESTED, reasons=(REASON_CONTEST_UNSETTLED,)
            ),
        ],
        contract_id="c",
    )
    assert determination.total == 3
    assert determination.coverage == 33.3333
    assert determination.closed is False
    assert determination.index() == {"A": "owner"}
    assert determination.by_owner() == {"owner": 1}
    assert determination.by_reason()[REASON_NO_EVIDENCE] == 1
    assert determination.counts()["contested"] == 1
    assert determination.record("A").subject_id == "A"
    assert determination.determination_id.startswith("UCOS-UOFT-")
    assert determination.fingerprint()
    assert determination.to_dict()["closed"] is False
    with pytest.raises(OwnershipContractError):
        determination.record("Z")
    with pytest.raises(OwnershipContractError):
        OwnershipDetermination.create(
            [
                OwnershipRecord.create(
                    "A", OwnershipStanding.UNRESOLVED, reasons=(REASON_NO_EVIDENCE,)
                ),
                OwnershipRecord.create(
                    "A", OwnershipStanding.UNRESOLVED, reasons=(REASON_NO_EVIDENCE,)
                ),
            ]
        )
    assert OwnershipDetermination.create([]).closed is False
    assert OwnershipDetermination.create([]).coverage == 0.0


# --------------------------------------------------------------------------- providers


def test_declared_assignment_provider_reads_a_governed_catalogue(tmp_path: Path) -> None:
    document = {
        "authority": "Governed Authority",
        "precedence": 950,
        "provider_id": "ownership.custom",
        "assignments": {"S": {"owner": "Owner A", "locator": HOME, "detail": "GOV-001"}},
    }
    path = tmp_path / "declarations.json"
    path.write_text(json.dumps(document), "utf-8")
    provider = DeclaredAssignmentProvider.from_file(path)
    assert provider.count == 1
    assert provider.descriptor().provider_id == "ownership.custom"
    evidence = provider.collect(_subject("S", HOME))
    assert evidence[0].owner == "Owner A"
    assert evidence[0].kind is EvidenceKind.DECLARED_ASSIGNMENT
    assert provider.collect(_subject("T")) == ()


def test_declared_assignment_provider_failure_modes(tmp_path: Path) -> None:
    with pytest.raises(OwnershipEvidenceError):
        DeclaredAssignmentProvider("nope")  # type: ignore[arg-type]
    with pytest.raises(OwnershipEvidenceError):
        DeclaredAssignmentProvider.from_document("nope")
    with pytest.raises(OwnershipEvidenceError):
        DeclaredAssignmentProvider.from_document({"assignments": []})
    with pytest.raises(OwnershipEvidenceError):
        DeclaredAssignmentProvider.from_file(tmp_path / "missing.json")
    provider = DeclaredAssignmentProvider({"S": {"owner": "  "}})
    with pytest.raises(OwnershipEvidenceError):
        provider.collect(_subject("S"))


def test_definitional_locator_provider_binds_owner_to_declared_zone_authority() -> None:
    provider = DefinitionalLocatorProvider(_policy())
    assert provider.policy is not None
    evidence = provider.collect(_subject("UCOS-COMP-000000", HOME))
    assert len(evidence) == 1
    assert evidence[0].authority.startswith("Constitutional Authority")
    assert evidence[0].kind is EvidenceKind.DEFINITIONAL_LOCATOR
    # Evidence zones can never yield a home, so no evidence is produced there.
    assert provider.collect(_subject("UCOS-COMP-000001", EVIDENCE_ONLY)) == ()
    # A locator that is not definitional for the subject yields nothing.
    assert provider.collect(_subject("UCOS-COMP-000000", "02-MASTER/other.md")) == ()
    with pytest.raises(OwnershipEvidenceError):
        DefinitionalLocatorProvider("nope")  # type: ignore[arg-type]


def test_definitional_locator_accepts_declared_qualifier_separators() -> None:
    provider = DefinitionalLocatorProvider(_policy())
    for locator in (
        "02-MASTER/UCOS-COMP-000000.md",
        "02-MASTER/UCOS-COMP-000000-TITLE.md",
        "02-MASTER/UCOS-COMP-000000_TITLE.md",
    ):
        assert provider.collect(_subject("UCOS-COMP-000000", locator))


def test_declared_identity_provider_reads_content_not_the_filesystem() -> None:
    policy = _policy()
    content = {
        "02-MASTER/anything.md": "| ARTIFACT ID | `UCOS-COMP-000000` |",
        EVIDENCE_ONLY: "ARTIFACT-ID: UCOS-COMP-000001",
        "02-MASTER/silent.md": "no declaration here",
        "02-MASTER/binary.md": 7,
    }
    identities = declared_identities(content)
    assert identities == {
        "02-MASTER/anything.md": "UCOS-COMP-000000",
        EVIDENCE_ONLY: "UCOS-COMP-000001",
    }
    provider = DeclaredIdentityProvider(identities, policy)
    assert provider.count == 2
    evidence = provider.collect(_subject("UCOS-COMP-000000"))
    assert evidence[0].kind is EvidenceKind.DECLARED_IDENTITY
    assert evidence[0].authority.startswith("Constitutional Authority")
    # A declaration inside an evidence zone establishes nothing.
    assert provider.collect(_subject("UCOS-COMP-000001")) == ()
    assert provider.collect(_subject("UNDECLARED")) == ()
    assert declared_identities({"a.md": "OWNS: X-1"}, labels=("OWNS",)) == {"a.md": "X-1"}
    with pytest.raises(OwnershipEvidenceError):
        DeclaredIdentityProvider("nope", policy)  # type: ignore[arg-type]
    with pytest.raises(OwnershipEvidenceError):
        DeclaredIdentityProvider({}, "nope")  # type: ignore[arg-type]


def test_declared_identity_outranks_a_definitional_filename() -> None:
    policy = _policy()
    engine = _engine(
        DeclaredIdentityProvider({"02-MASTER/declared.md": "S"}, policy),
        DefinitionalLocatorProvider(policy),
    )
    record = engine.determine_subject(_subject("S", "02-MASTER/S.md"))
    assert record.declared is True
    assert record.declaration is not None
    assert record.declaration.kind is EvidenceKind.DECLARED_IDENTITY


def test_registration_provider_is_corroborative_only() -> None:
    provider = RegistrationEvidenceProvider({"S": "Registrar"})
    assert provider.subject_ids == frozenset({"S"})
    evidence = provider.collect(_subject("S"))
    assert evidence[0].constitutive is False
    assert provider.collect(_subject("T")) == ()
    anonymous = RegistrationEvidenceProvider(["S"])
    assert anonymous.collect(_subject("S")) == ()


def test_callable_provider_and_protocol_enforcement() -> None:
    descriptor = EvidenceProviderDescriptor(
        provider_id="p", kind=EvidenceKind.DELEGATION, authority="A"
    )
    good = CallableEvidenceProvider(
        descriptor,
        lambda subject: (
            OwnershipEvidence.create(
                subject.subject_id, "Owner", EvidenceKind.DELEGATION, provider_id="p"
            ),
        ),
    )
    assert good.collect(_subject("S"))[0].owner == "Owner"
    assert good.evidence("S", "Owner").provider_id == "p"

    exploding = CallableEvidenceProvider(descriptor, lambda subject: 1 / 0)
    with pytest.raises(OwnershipEvidenceError):
        exploding.collect(_subject("S"))

    wrong_type = CallableEvidenceProvider(descriptor, lambda subject: ("nope",))
    with pytest.raises(OwnershipEvidenceError):
        wrong_type.collect(_subject("S"))

    wrong_provider = CallableEvidenceProvider(
        descriptor,
        lambda subject: (
            OwnershipEvidence.create(
                subject.subject_id, "Owner", EvidenceKind.DELEGATION, provider_id="other"
            ),
        ),
    )
    with pytest.raises(OwnershipEvidenceError):
        wrong_provider.collect(_subject("S"))

    wrong_subject = CallableEvidenceProvider(
        descriptor,
        lambda subject: (
            OwnershipEvidence.create("OTHER", "Owner", EvidenceKind.DELEGATION, provider_id="p"),
        ),
    )
    with pytest.raises(OwnershipEvidenceError):
        wrong_subject.collect(_subject("S"))

    with pytest.raises(OwnershipEvidenceError):
        good.collect("not-a-subject")  # type: ignore[arg-type]
    with pytest.raises(OwnershipEvidenceError):
        CallableEvidenceProvider("nope", lambda subject: ())  # type: ignore[arg-type]
    with pytest.raises(OwnershipEvidenceError):
        CallableEvidenceProvider(descriptor, "nope")  # type: ignore[arg-type]


def test_provider_descriptor_guards() -> None:
    with pytest.raises(OwnershipEvidenceError):
        EvidenceProviderDescriptor(provider_id=" ", kind=EvidenceKind.DELEGATION)
    with pytest.raises(OwnershipEvidenceError):
        EvidenceProviderDescriptor(provider_id="p", kind="delegation")  # type: ignore[arg-type]
    with pytest.raises(OwnershipEvidenceError):
        EvidenceProviderDescriptor(
            provider_id="p",
            kind=EvidenceKind.DELEGATION,
            precedence="high",  # type: ignore[arg-type]
        )
    descriptor = EvidenceProviderDescriptor(provider_id="p", kind=EvidenceKind.DELEGATION)
    assert descriptor.to_dict()["constitutive"] is True
    assert descriptor.fingerprint()


def test_registry_ordering_and_fail_closed_registration() -> None:
    policy = _policy()
    definitional = DefinitionalLocatorProvider(policy)
    declared = DeclaredAssignmentProvider({}, authority="A")
    registry = EvidenceProviderRegistry([definitional, declared])
    assert registry.count == 2
    assert registry.add(declared) is declared
    assert [descriptor.provider_id for descriptor in registry.descriptors()] == [
        "ownership.declared-assignment",
        "ownership.definitional-locator",
    ]
    assert len(registry.constitutive()) == 2
    assert registry.require("ownership.declared-assignment") is declared
    assert registry.get("missing") is None
    assert registry.to_dict()["provider_count"] == 2
    assert registry.fingerprint()
    with pytest.raises(OwnershipProviderConflictError):
        registry.add(DeclaredAssignmentProvider({"X": {"owner": "Y"}}))
    with pytest.raises(OwnershipEvidenceError):
        registry.add("nope")  # type: ignore[arg-type]
    with pytest.raises(OwnershipEvidenceError):
        registry.require("missing")
    registry.remove("ownership.declared-assignment")
    assert registry.count == 1
    with pytest.raises(OwnershipEvidenceError):
        registry.remove("ownership.declared-assignment")
    assert registry.collect_all([_subject("UCOS-COMP-000000", HOME)])["UCOS-COMP-000000"]


# --------------------------------------------------------------------------- determination


def test_sole_declaration_is_declared() -> None:
    engine = _engine(DefinitionalLocatorProvider(_policy()))
    record = engine.determine_subject(_subject("UCOS-COMP-000000", HOME))
    assert record.standing is OwnershipStanding.DECLARED
    assert record.declaration is not None
    assert record.declaration.rule == RULE_SOLE_DECLARATION
    assert record.declaration.satisfied == default_ownership_contract().mandatory_ids()
    assert engine.require_owner(_subject("UCOS-COMP-000000", HOME)) == record.owner


def test_evidence_only_subject_is_unresolved_not_invented() -> None:
    engine = _engine(DefinitionalLocatorProvider(_policy()))
    record = engine.determine_subject(_subject("UCOS-COMP-000001", EVIDENCE_ONLY))
    assert record.standing is OwnershipStanding.UNRESOLVED
    assert record.reasons == (REASON_INELIGIBLE_ZONE,)
    assert record.unmet == ("OWN-REQ-003",)
    with pytest.raises(OwnershipFabricationError):
        engine.require_owner(_subject("UCOS-COMP-000001", EVIDENCE_ONLY))


def test_subject_without_any_evidence_is_unresolved() -> None:
    engine = _engine(DefinitionalLocatorProvider(_policy()))
    record = engine.determine_subject(_subject("ORPHAN"))
    assert record.reasons == (REASON_NO_EVIDENCE,)


def test_corroboration_alone_never_establishes_ownership() -> None:
    engine = _engine(RegistrationEvidenceProvider({"S": "Registrar"}))
    record = engine.determine_subject(_subject("S", HOME))
    assert record.standing is OwnershipStanding.UNRESOLVED
    assert record.reasons == (REASON_NO_CONSTITUTIVE_DECLARATION,)
    assert record.unmet == ("OWN-REQ-001",)


def test_evidence_outside_a_home_zone_is_inadmissible() -> None:
    descriptor = EvidenceProviderDescriptor(
        provider_id="p", kind=EvidenceKind.DECLARED_ASSIGNMENT, authority="A"
    )
    provider = CallableEvidenceProvider(
        descriptor,
        lambda subject: (
            OwnershipEvidence.create(
                subject.subject_id,
                "Owner",
                EvidenceKind.DECLARED_ASSIGNMENT,
                locator="00-MASTER/programme/x.md",
                provider_id="p",
            ),
        ),
    )
    engine = _engine(provider)
    record = engine.determine_subject(_subject("S"))
    assert record.reasons == (REASON_INELIGIBLE_ZONE,)


def test_contest_is_settled_only_by_declared_precedence() -> None:
    def claim(owner: str, precedence: int, provider_id: str) -> CallableEvidenceProvider:
        descriptor = EvidenceProviderDescriptor(
            provider_id=provider_id,
            kind=EvidenceKind.DECLARED_ASSIGNMENT,
            precedence=precedence,
            authority=owner,
        )
        return CallableEvidenceProvider(
            descriptor,
            lambda subject, owner=owner, precedence=precedence, provider_id=provider_id: (
                OwnershipEvidence.create(
                    subject.subject_id,
                    owner,
                    EvidenceKind.DECLARED_ASSIGNMENT,
                    locator=HOME,
                    provider_id=provider_id,
                    authority=owner,
                    precedence=precedence,
                ),
            ),
        )

    settled = _engine(claim("Owner A", 900, "a"), claim("Owner B", 100, "b"))
    record = settled.determine_subject(_subject("S"))
    assert record.standing is OwnershipStanding.DECLARED
    assert record.owner == "Owner A"
    assert record.declaration is not None
    assert record.declaration.rule == RULE_CONTEST_SETTLED
    assert dict(record.claims) == {"Owner A": 1, "Owner B": 1}

    tied = _engine(claim("Owner A", 500, "a"), claim("Owner B", 500, "b"))
    contested = tied.determine_subject(_subject("S"))
    assert contested.standing is OwnershipStanding.CONTESTED
    assert contested.reasons == (REASON_CONTEST_UNSETTLED,)
    assert contested.unmet == ("OWN-REQ-002", "OWN-REQ-005")


def test_registration_is_eligibility_when_declared() -> None:
    engine = OwnershipDeterminationEngine(
        EvidenceProviderRegistry([DefinitionalLocatorProvider(_policy())]),
        policy=_policy(),
        registered=("OTHER",),
    )
    record = engine.determine_subject(_subject("UCOS-COMP-000000", HOME))
    assert record.reasons == (REASON_SUBJECT_NOT_REGISTERED,)
    assert record.unmet == ("OWN-REQ-004",)


def test_engine_without_policy_admits_any_locator() -> None:
    descriptor = EvidenceProviderDescriptor(
        provider_id="p", kind=EvidenceKind.DECLARED_ASSIGNMENT, authority="A"
    )
    provider = CallableEvidenceProvider(
        descriptor,
        lambda subject: (
            OwnershipEvidence.create(
                subject.subject_id,
                "Owner",
                EvidenceKind.DECLARED_ASSIGNMENT,
                locator="anywhere/at/all.md",
                provider_id="p",
            ),
        ),
    )
    engine = OwnershipDeterminationEngine(EvidenceProviderRegistry([provider]))
    assert engine.determine_subject(_subject("S")).declared is True
    assert engine.policy is None
    assert engine.contract.contract_id


def test_engine_construction_guards() -> None:
    with pytest.raises(OwnershipDeterminationError):
        OwnershipDeterminationEngine("nope")  # type: ignore[arg-type]
    with pytest.raises(OwnershipDeterminationError):
        OwnershipDeterminationEngine(EvidenceProviderRegistry(), policy="nope")  # type: ignore[arg-type]
    engine = OwnershipDeterminationEngine(EvidenceProviderRegistry())
    with pytest.raises(OwnershipDeterminationError):
        engine.determine_subject("nope")  # type: ignore[arg-type]


def test_determination_over_a_population() -> None:
    engine = _engine(DefinitionalLocatorProvider(_policy()))
    determination = engine.determine(
        [
            _subject("UCOS-COMP-000000", HOME),
            _subject("UCOS-COMP-000001", EVIDENCE_ONLY),
        ]
    )
    assert determination.counts() == {
        "total": 2,
        "declared": 1,
        "contested": 0,
        "unresolved": 1,
        "remediable": 1,
    }
    assert determination.contract_id == engine.contract.contract_id


# --------------------------------------------------------------------------- wiring


def test_contract_surface_is_published() -> None:
    assert ownership_contract_names()
    assert len(OWNERSHIP_CONTRACTS) == len(ownership_contract_names())


def test_bootstrap_composition_and_registration(tmp_path: Path) -> None:
    engine = bootstrap_ownership()
    ids = [descriptor.provider_id for descriptor in engine.providers.descriptors()]
    assert "ownership.declared-assignment" in ids
    assert "ownership.definitional-locator" in ids
    assert catalog_path().exists()

    with_ledger = bootstrap_ownership(registered=("A",), require_registration=True)
    assert with_ledger.determine_subject(_subject("B")).reasons == (REASON_SUBJECT_NOT_REGISTERED,)

    missing = tmp_path / "absent.json"
    providers = default_evidence_providers(_policy(), declarations=missing)
    assert all(
        descriptor.provider_id != "ownership.declared-assignment"
        for descriptor in EvidenceProviderRegistry(providers).descriptors()
    )

    registry = ServiceRegistry()
    descriptor = register_ownership(registry)
    assert descriptor.name == "universal.ownership"
    assert isinstance(registry.resolve("universal.ownership"), OwnershipDeterminationEngine)


def test_definitional_provider_ignores_locators_without_segments() -> None:
    policy = TruthPolicy(
        [
            TruthZone.create(
                "home",
                "canonical",
                [{"kind": "root", "value": "zone"}],
                authority="Authority",
                canonical_home_eligible=True,
            )
        ]
    )
    provider = DefinitionalLocatorProvider(policy)
    assert provider.collect(Subject.create("S", locators=["zone/S.md"]))
    assert provider.collect(Subject.create("S", locators=["other/S.md"])) == ()


# --------------------------------------------------------------------------- cli


def test_cli_contract_and_providers(capsys: pytest.CaptureFixture[str]) -> None:
    assert ownership_main(["contract", "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert len(payload["requirements"]) == 7
    assert ownership_main(["providers", "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["provider_count"] >= 1


def test_cli_determine_gate_and_faults(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    document = {
        "concepts": [
            {"id": "UCOS-COMP-000000", "files": [HOME]},
            {"id": "UCOS-COMP-000001", "files": [EVIDENCE_ONLY]},
        ]
    }
    path = tmp_path / "model.json"
    path.write_text(json.dumps(document), "utf-8")
    assert (
        ownership_main(
            [
                "determine",
                "--subjects",
                str(path),
                "--collection",
                "concepts",
                "--identity-field",
                "id",
                "--locator-field",
                "files",
                "--json",
            ]
        )
        == 0
    )
    payload = json.loads(capsys.readouterr().out)
    assert payload["counts"]["declared"] == 1
    assert payload["counts"]["unresolved"] == 1
    assert ownership_main(["determine", "--subjects", str(path), "--gate"]) == 1
    assert ownership_main(["determine"]) == 2
    assert ownership_main(["providers", "--policy", str(tmp_path / "missing.json")]) == 2


# ------------------------------------------------------------------- refusal diagnosis


UNREGISTERED_HOME = "02-MASTER/UCOS-COMP-000002-CONSTITUTION.md"


def _gated_home(*registered: str):
    """A canonical-home policy requiring registration and Markdown form.

    A decoy registration is always present because a declared registration requirement with an
    empty ledger fails closed by design — the ledger refuses to *decide* without data, which is
    a different (and correct) behaviour from refusing a locator.
    """

    return CanonicalHomePolicy(
        _policy(),
        EligibilityLedger.create(
            ledger_id="test.refusal",
            registered=(*registered, "00-BOOK/DECOY-REGISTRATION.md"),
            admitted_suffixes=(".md",),
            excluded_segments=("_evidence/",),
        ),
    )


def test_a_refusal_requires_a_located_provenance_and_reason() -> None:
    refusal = EvidenceRefusal(
        provider_id="p", subject_id="S", locator="a/b.md", reason="LOCATOR-NOT-REGISTERED"
    )
    assert refusal.order_key == ("a/b.md", "p", "LOCATOR-NOT-REGISTERED")
    assert refusal.refusal_id.startswith("UCOS-UOFX-")
    assert refusal.to_dict()["reason"] == "LOCATOR-NOT-REGISTERED"
    for field in ("provider_id", "subject_id", "locator", "reason"):
        with pytest.raises(OwnershipEvidenceError):
            EvidenceRefusal(**{**refusal.to_dict(), field: "  "})


def test_a_provider_that_applies_no_gate_reports_no_refusal() -> None:
    provider = DeclaredAssignmentProvider({"S": {"owner": "o"}})
    assert provider.collect_refusals(_subject("S", HOME)) == ()


def test_a_home_gated_provider_diagnoses_every_candidate_it_had_to_discard() -> None:
    """The whole point: 'no evidence' and 'refused evidence' stop being the same answer."""
    provider = DefinitionalLocatorProvider(_gated_home())
    subject = _subject("UCOS-COMP-000002", UNREGISTERED_HOME)
    assert provider.collect(subject) == ()
    refusals = provider.collect_refusals(subject)
    assert [item.reason for item in refusals] == ["LOCATOR-NOT-REGISTERED"]
    assert refusals[0].locator == UNREGISTERED_HOME
    assert refusals[0].provider_id == "ownership.definitional-locator"


def test_an_admitted_candidate_is_never_also_a_refusal() -> None:
    provider = DefinitionalLocatorProvider(_gated_home(UNREGISTERED_HOME))
    subject = _subject("UCOS-COMP-000002", UNREGISTERED_HOME)
    assert len(provider.collect(subject)) == 1
    assert provider.collect_refusals(subject) == ()


def test_a_role_provider_and_an_identity_provider_diagnose_through_the_same_gate() -> None:
    """One eligibility gate, written once: three providers cannot answer it differently."""
    home = _gated_home()
    subject = Subject.create(
        "UCOS-COMP-000002", locators=(UNREGISTERED_HOME,), roles={"home": (UNREGISTERED_HOME,)}
    )
    role = RoleLocatorProvider("home", home)
    identity = DeclaredIdentityProvider({UNREGISTERED_HOME: "UCOS-COMP-000002"}, home)
    for provider in (role, identity):
        assert provider.collect(subject) == ()
        assert [item.reason for item in provider.collect_refusals(subject)] == [
            "LOCATOR-NOT-REGISTERED"
        ]


def test_a_faulting_diagnosis_is_contained_and_never_silent() -> None:
    class Faulty(DefinitionalLocatorProvider):
        def candidates(self, subject: Subject) -> tuple[str, ...]:
            raise RuntimeError("boom")

    with pytest.raises(OwnershipEvidenceError):
        Faulty(_gated_home()).collect_refusals(_subject("S", HOME))


def test_a_provider_may_not_forge_a_refusal_for_another_provider_or_subject() -> None:
    class Forger(DefinitionalLocatorProvider):
        def refusals(self, subject: Subject):
            return (
                EvidenceRefusal(
                    provider_id="somebody.else",
                    subject_id=subject.subject_id,
                    locator="a.md",
                    reason="LOCATOR-NOT-REGISTERED",
                ),
            )

    class WrongSubject(DefinitionalLocatorProvider):
        def refusals(self, subject: Subject):
            return (
                EvidenceRefusal(
                    provider_id="ownership.definitional-locator",
                    subject_id="OTHER",
                    locator="a.md",
                    reason="LOCATOR-NOT-REGISTERED",
                ),
            )

    class NotARefusal(DefinitionalLocatorProvider):
        def refusals(self, subject: Subject):
            return ("nope",)  # type: ignore[return-value]

    home = _gated_home()
    for cls in (Forger, WrongSubject, NotARefusal):
        with pytest.raises(OwnershipEvidenceError):
            cls(home).collect_refusals(_subject("S", HOME))
    with pytest.raises(OwnershipEvidenceError):
        DefinitionalLocatorProvider(home).collect_refusals("not-a-subject")  # type: ignore[arg-type]


def test_the_registry_aggregates_refusals_deterministically() -> None:
    home = _gated_home()
    subject = Subject.create(
        "UCOS-COMP-000002", locators=(UNREGISTERED_HOME,), roles={"home": (UNREGISTERED_HOME,)}
    )
    registry = EvidenceProviderRegistry(
        (DefinitionalLocatorProvider(home), RoleLocatorProvider("home", home))
    )
    first = registry.refusals(subject)
    assert len(first) == 2
    assert [item.order_key for item in first] == sorted(item.order_key for item in first)
    assert registry.refusals(subject) == first


def test_the_record_carries_the_diagnosis_without_changing_its_identity() -> None:
    """A refusal is diagnosis, so it must not move the record's content address (UFC-08)."""
    plain = OwnershipRecord.create(
        "S", OwnershipStanding.UNRESOLVED, reasons=(REASON_INELIGIBLE_ZONE,)
    )
    diagnosed = OwnershipRecord.create(
        "S",
        OwnershipStanding.UNRESOLVED,
        reasons=(REASON_INELIGIBLE_ZONE,),
        refusals=(("a.md", "LOCATOR-NOT-REGISTERED", "p"),),
    )
    assert diagnosed.record_id == plain.record_id
    assert diagnosed.fingerprint() != plain.fingerprint()
    assert diagnosed.refusal_reasons == ("LOCATOR-NOT-REGISTERED",)
    assert diagnosed.refused_locators == ("a.md",)
    assert diagnosed.remediable is True
    assert plain.remediable is False
    assert diagnosed.to_dict()["refusals"] == [
        {"locator": "a.md", "reason": "LOCATOR-NOT-REGISTERED", "provider_id": "p"}
    ]


def test_a_declared_record_is_never_remediable() -> None:
    engine = _engine(DefinitionalLocatorProvider(_policy()))
    record = engine.determine_subject(_subject("UCOS-COMP-000000", HOME))
    assert record.declared is True
    assert record.remediable is False


def test_a_malformed_refusal_triple_is_refused() -> None:
    for bad in ((("a.md", "R"),), (("a.md", "R", "  "),)):
        with pytest.raises(OwnershipContractError):
            OwnershipRecord.create("S", OwnershipStanding.UNRESOLVED, reasons=("R",), refusals=bad)


def test_the_determination_attributes_a_whole_subject_refusal_to_the_canonical_home() -> None:
    """When no provider had a candidate, the policy refused the subject — say so.

    And exactly once: a locator a provider already diagnosed is not re-attributed to the
    policy, so each refused locator carries one refusal naming its most specific refuser.
    """

    engine = _engine(DefinitionalLocatorProvider(_policy()), policy=_policy())
    recognised = engine.determine_subject(_subject("UCOS-COMP-000001", EVIDENCE_ONLY))
    assert recognised.reasons == (REASON_INELIGIBLE_ZONE,)
    assert recognised.unmet == ("OWN-REQ-003",)
    assert recognised.refusals == (
        (EVIDENCE_ONLY, "ZONE-NOT-CANONICAL-HOME-ELIGIBLE", "ownership.definitional-locator"),
    )

    unrecognised = engine.determine_subject(_subject("SOMETHING-ELSE", EVIDENCE_ONLY))
    assert unrecognised.refusals == (
        (EVIDENCE_ONLY, "ZONE-NOT-CANONICAL-HOME-ELIGIBLE", CANONICAL_HOME_REFUSER),
    )


def test_an_unregistered_subject_still_carries_its_diagnosis() -> None:
    engine = _engine(
        DefinitionalLocatorProvider(_gated_home()),
        policy=_gated_home(),
        registered=("SOMEBODY-ELSE",),
    )
    record = engine.determine_subject(_subject("UCOS-COMP-000002", UNREGISTERED_HOME))
    assert record.reasons == (REASON_SUBJECT_NOT_REGISTERED,)
    assert record.refusal_reasons == ("LOCATOR-NOT-REGISTERED",)


def test_the_population_projection_publishes_the_diagnosis() -> None:
    engine = _engine(DefinitionalLocatorProvider(_policy()), policy=_policy())
    determination = engine.determine(
        [_subject("UCOS-COMP-000000", HOME), _subject("UCOS-COMP-000001", EVIDENCE_ONLY)]
    )
    assert determination.counts()["remediable"] == 1
    assert determination.by_refusal() == {"ZONE-NOT-CANONICAL-HOME-ELIGIBLE": 1}
    assert determination.refusal_index() == {
        "UCOS-COMP-000001": {EVIDENCE_ONLY: "ZONE-NOT-CANONICAL-HOME-ELIGIBLE"}
    }
    assert [record.subject_id for record in determination.remediable] == ["UCOS-COMP-000001"]
    assert determination.to_dict()["by_refusal"] == determination.by_refusal()


# --------------------------------------------------------------------------- cli: the
# specialised commands
#
# WHY THESE EXIST. `contract`, `providers` and `determine` were exercised; `homing` and
# `recommend` were not, and they are the two that carry the project's DECLARED
# SPECIALISATION — the composition path where the population, the ledger, the eligibility
# rules and the ownership grain all come from one document. Every line of that path, and
# the whole `recommend` summary an operator reads, was unexecuted. So was the fault arm
# that refuses a specialisation projecting no population, which is the one thing that
# stands between this command and a vacuous determination over nothing.


def test_cli_homing_determines_over_the_declared_specialisation(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert ownership_main(["homing", "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["subjects"] > 0
    assert payload["counts"]["total"] == payload["subjects"]
    assert payload["providers"]["provider_count"] >= 1
    # the summary, not the detail: per-record rows are withheld unless asked for
    assert "records" not in payload


def test_cli_homing_detail_carries_the_per_record_rows(capsys: pytest.CaptureFixture[str]) -> None:
    assert ownership_main(["homing", "--detail", "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert len(payload["records"]) == payload["counts"]["total"]


def test_cli_homing_summarises_the_determination_on_stderr(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert ownership_main(["homing"]) == 0
    captured = capsys.readouterr()
    assert "UCOS-UOF-001 CANONICAL OWNERSHIP" in captured.err
    assert "command: homing" in captured.err
    assert "subjects:" in captured.err
    assert "coverage:" in captured.err
    assert captured.out == ""


def test_cli_recommend_reduces_the_governance_workload(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert ownership_main(["recommend", "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    counts = payload["counts"]
    assert counts["open"] >= counts["governance_minimum"]
    assert 0.0 <= payload["reduction_percentage"] <= 100.0
    assert 0.0 <= payload["determinable_percentage"] <= 100.0


def test_cli_recommend_summarises_the_reduction_it_computed(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert ownership_main(["recommend"]) == 0
    err = capsys.readouterr().err
    assert "command: recommend" in err
    assert "open subjects:" in err
    assert "governance min:" in err
    assert "reduction:" in err
    assert "determinable:" in err


def test_cli_recommend_detail_and_draft_are_different_documents(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert ownership_main(["recommend", "--detail", "--json"]) == 0
    detail = json.loads(capsys.readouterr().out)
    assert ownership_main(["recommend", "--draft", "--json"]) == 0
    draft = json.loads(capsys.readouterr().out)
    assert detail != draft
    # a draft is a non-binding proposal a governing authority would review, and says so
    assert "NOT BINDING" in draft["$comment"]
    assert "assignments" in draft
    assert "$comment" not in detail


def test_cli_recommend_is_deterministic(capsys: pytest.CaptureFixture[str]) -> None:
    ownership_main(["recommend", "--json"])
    first = capsys.readouterr().out
    ownership_main(["recommend", "--json"])
    assert capsys.readouterr().out == first


def test_cli_refuses_a_specialisation_that_projects_no_population(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A determination over an empty population would report perfect closure over nothing,
    which is the vacuous pass the whole framework exists to refuse."""
    (tmp_path / "population.json").write_text(json.dumps({"concepts": []}), "utf-8")
    document = tmp_path / "specialisation.json"
    document.write_text(
        json.dumps(
            {
                "project_id": "EMPTY-PROJECT",
                "population_document": "population.json",
                "projection": {
                    "collection": "concepts",
                    "identity_field": "id",
                    "locator_fields": ["files"],
                },
            }
        ),
        "utf-8",
    )
    assert (
        ownership_main(["homing", "--specialization", str(document), "--root", str(tmp_path)]) == 2
    )
    assert "projects no population" in capsys.readouterr().err


# --------------------------------------------------------------------------- the quiet arms
#
# The declared catalogue supplies every optional field, every locator has segments, every
# artifact on disk is readable, and this repository's governance minimum is empty. Each arm
# below answers for a project where one of those is not so.


def test_a_declaration_omitting_every_optional_field_takes_the_provider_defaults(
    tmp_path: Path,
) -> None:
    """THREE OPTIONAL FIELDS, AND THE ONLY TESTED DOCUMENT SUPPLIES ALL THREE.

    A governed catalogue may declare its authority, its provider id and its precedence — or
    none of them, and take the provider's own. Reading an absent key as an empty authority or
    a precedence of zero would silently demote a declaration below every other provider,
    which is the kind of change nobody reviews because nothing in the document says it
    happened.
    """
    minimal = DeclaredAssignmentProvider.from_document(
        {"assignments": {"S": {"owner": "Owner A", "locator": HOME}}}
    )
    declared = DeclaredAssignmentProvider.from_document(
        {
            "authority": "Governed Authority",
            "provider_id": "ownership.custom",
            "precedence": 950,
            "assignments": {"S": {"owner": "Owner A", "locator": HOME}},
        }
    )

    assert minimal.count == 1
    assert minimal.descriptor().provider_id != declared.descriptor().provider_id
    assert minimal.descriptor().precedence != 950
    assert minimal.collect(_subject("S", HOME))[0].owner == "Owner A"


def test_a_locator_with_no_segments_is_not_a_definitional_candidate() -> None:
    """A LOCATOR THAT NAMES NOTHING CANNOT BE DEFINITIONAL OF ANYTHING.

    Every tested subject carries real paths, so the skip had no case — and without it the
    basename check would be run against the last element of an empty tuple and raise from
    inside a provider whose contract is to return candidates. An empty locator is a real
    shape: a declaration with a trailing separator, or a projection field that was blank.
    """
    provider = DefinitionalLocatorProvider(_policy())

    assert provider.candidates(_subject("UCOS-COMP-000000", "", "/", HOME)) == (HOME,)


def test_a_role_provider_reports_the_role_it_reads() -> None:
    """A PROVIDER READING A DECLARED ROLE MUST BE ABLE TO SAY WHICH ROLE.

    The role is supplied at construction and appears in the provider's own description, so
    nothing ever asked the provider back for it — and it is what a registry listing several
    role providers uses to tell them apart. Two providers reading two roles are otherwise
    identical from the outside.
    """
    provider = RoleLocatorProvider("owner", _policy())

    assert provider.role == "owner"
    assert provider.home is not None
    assert "owner" in provider.descriptor().description


def test_a_blank_locator_is_read_from_nothing_rather_than_from_the_root(tmp_path: Path) -> None:
    """READING A BLANK LOCATOR WOULD READ THE ROOT DIRECTORY ITSELF.

    The unreadable-locator skip below it is exercised by every missing file; the blank one
    was not, and it is the more dangerous of the two: ``root / ""`` is the root, so a blank
    entry would attempt to read the whole checkout as one artifact's front matter. Dropping
    it is the same fail-closed rule the module already states — an absent declaration must
    never resolve to an assertion.
    """
    (tmp_path / "declared.md").write_text("id: UCOS-COMP-000000\n", encoding="utf-8")

    found = read_declared_identities(
        ["", "   ", "declared.md", "never-written.md"], root=tmp_path, labels=("id",)
    )

    assert set(found) == {"declared.md"}


def test_a_granularity_that_is_not_a_string_is_refused() -> None:
    """A GRANULARITY IS AN ENUM MEMBER OR THE STRING THAT SPELLS ONE.

    Both string arms were tested; the value that is neither was not, and it is refused before
    it reaches the enum constructor — because the ValueError raised from inside would say
    "not a valid OwnershipGranularity" about an integer, naming the wrong problem at a
    boundary whose contract is to name it exactly.
    """
    assert OwnershipGranularity.coerce(OwnershipGranularity.LOCATOR) is (
        OwnershipGranularity.LOCATOR
    )
    assert OwnershipGranularity.coerce("locator") is OwnershipGranularity.LOCATOR

    with pytest.raises(OwnershipContractError, match="unknown ownership granularity"):
        OwnershipGranularity.coerce("not-a-granularity")
    with pytest.raises(OwnershipContractError, match="must be a string"):
        OwnershipGranularity.coerce(7)


def test_the_recommend_summary_names_the_governance_minimum_when_there_is_one(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """THE ONE BLOCK THIS REPOSITORY CANNOT PRODUCE.

    The governance minimum is the residue no provider can propose an owner for and no
    declared rule names a deficit against — the subjects an authority must decide from first
    principles. It is EMPTY here, which is the programme working, and that is exactly why the
    block announcing it had never been rendered. It is reached by rendering a payload that
    carries one, because forging a subject the whole provider set is silent about would mean
    disabling the providers rather than exercising the report.
    """
    assert ownership_main(["recommend"]) == 0
    assert "GOVERNANCE MINIMUM" not in capsys.readouterr().err

    _print_summary(
        "recommend",
        {"counts": {}, "governance_minimum": ["UCOS-COMP-000000", "UCOS-COMP-000001"]},
        sys.stderr,
    )

    rendered = capsys.readouterr().err
    assert "GOVERNANCE MINIMUM (2)" in rendered
    assert "authority to decide from first principles" in rendered


def test_a_declared_eligibility_ledger_is_composed_onto_an_existing_home_policy() -> None:
    """A HOME POLICY MAY ARRIVE ALREADY COMPOSED, AND AN ELIGIBILITY LEDGER STILL BINDS.

    Two of the three composition shapes were exercised: a bare Truth policy with a ledger,
    and a composed policy with none. The third — a composed policy AND a ledger — had no
    case, and it is what a project specialising a foundation it did not build takes. Ignoring
    the ledger there would drop a declared eligibility requirement silently, which is the
    Zero Silent Repair failure the whole framework refuses.
    """
    ledger = EligibilityLedger.create(registered=[HOME], require_registration=True)
    composed = CanonicalHomePolicy(default_truth_policy())

    engine = bootstrap_ownership(policy=composed, eligibility=ledger)

    assert engine.home.ledger is ledger
    assert engine.home.policy is composed.policy


def test_a_typed_refusal_fault_passes_through_without_being_wrapped_again() -> None:
    """AN ERROR THAT ALREADY NAMES ITS PROVIDER MUST NOT BE RE-NAMED BY THE CONTAINMENT.

    The untyped fault is contained and re-raised as a framework error — tested. This is the
    arm above it: a provider that raises the framework's OWN error while diagnosing has
    already said which provider, which subject and what was wrong, and wrapping it a second
    time would bury that detail inside a generic "failed while diagnosing a refusal". The
    containment exists to make an unknown failure legible, not to overwrite a legible one.
    """

    class Refusing(DefinitionalLocatorProvider):
        def refusals(self, subject: Subject):
            raise OwnershipEvidenceError(
                "the ledger this provider reads is unavailable",
                provider_id="ownership.definitional-locator",
                subject=subject.subject_id,
            )

    with pytest.raises(OwnershipEvidenceError) as raised:
        Refusing(_gated_home()).collect_refusals(_subject("S", HOME))

    assert "the ledger this provider reads is unavailable" in str(raised.value)
    assert "failed while diagnosing" not in str(raised.value)


def test_the_workload_rendering_prints_every_counted_section(capsys) -> None:
    """The recommend summary prints deficits, owners, minimums — the arms with no empty state.

    The live population is closed, so these lines only fire on a payload that still carries
    open work; the renderer is exercised against one directly, exactly the shape the engine
    emits before ratification.
    """

    payload = {
        "counts": {
            "subjects": 10,
            "declared": 3,
            "contested": 0,
            "unresolved": 7,
            "remediable": 6,
            "open": 7,
            "ratifiable": 5,
            "irreducible": 2,
            "governance_minimum": 1,
        },
        "reduction_percentage": 71.4,
        "determinable_percentage": 100.0,
        "by_deficit": {"ZONE-NOT-CANONICAL-HOME-ELIGIBLE": 4},
        "by_proposed_owner": {"Constitutional Authority (02-MASTER)": 5},
    }
    _print_summary("recommend", payload, __import__("sys").stdout)
    out = capsys.readouterr().out
    assert "refused by declared rule" in out
    assert "would be owned by" in out
    assert "neither proposable nor remediable" in out
