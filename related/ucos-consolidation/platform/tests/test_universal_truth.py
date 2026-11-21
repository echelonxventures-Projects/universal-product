"""Tests — Universal Repository Truth Framework (UCOS-URTF-001)."""

from __future__ import annotations

import json
from pathlib import Path
from platform.foundation.services import ServiceRegistry
from platform.universal_truth import (
    NON_HOME_TRUTH_CLASSES,
    TRUTH_CONTRACTS,
    PathSelector,
    SelectorKind,
    Subject,
    TruthClass,
    TruthClassification,
    TruthPolicy,
    TruthZone,
    bootstrap_repository_truth,
    default_truth_policy,
    locator_segments,
    normalize_locator,
    register_repository_truth,
    truth_contract_names,
    truth_service_descriptor,
)
from platform.universal_truth.cli import main as truth_main
from platform.universal_truth.eligibility import (
    REASON_ELIGIBLE,
    REASON_NOT_REGISTERED,
    REASON_ZONE_INELIGIBLE,
    CanonicalHomePolicy,
    EligibilityLedger,
    load_eligibility_ledger,
    open_ledger,
)
from platform.universal_truth.errors import (
    TruthContractError,
    TruthEligibilityError,
    TruthPolicyError,
    TruthProjectionError,
)
from platform.universal_truth.policy import TruthPartition, catalog_path, load_truth_policy
from platform.universal_truth.projection import (
    ProjectionSpec,
    SubjectProjection,
    project_subjects,
)

import pytest


def _zone(zone_id: str, truth_class: str, value: str, **kwargs: object) -> TruthZone:
    return TruthZone.create(zone_id, truth_class, [{"kind": "root", "value": value}], **kwargs)


# --------------------------------------------------------------------------- locators


def test_normalize_locator_is_separator_agnostic() -> None:
    assert normalize_locator("./a\\b/c.md") == "a/b/c.md"
    assert normalize_locator("/a/./b/") == "a/b"
    assert locator_segments("a/b/c.md") == ("a", "b", "c.md")
    assert locator_segments("") == ()


def test_normalize_locator_rejects_non_string() -> None:
    with pytest.raises(TruthContractError):
        normalize_locator(7)


# --------------------------------------------------------------------------- selectors


@pytest.mark.parametrize(
    ("kind", "value", "locator", "expected"),
    [
        ("root", "engine", "engine/x.py", True),
        ("root", "engine", "platform/x.py", False),
        ("root-file", "*.md", "README.md", True),
        ("root-file", "*.md", "docs/README.md", False),
        ("segment", "__pycache__", "a/__pycache__/b.pyc", True),
        ("segment", "__pycache__", "a/b.pyc", False),
        ("prefix", "a/b", "a/b/c", True),
        ("prefix", "a/b", "a/bc", False),
        ("suffix", ".egg-info", "x.egg-info", True),
        ("glob", "a/*/c.md", "a/b/c.md", True),
        ("exact", "a/b.md", "a/b.md", True),
        ("exact", "a/b.md", "a/b/c.md", False),
    ],
)
def test_selector_matching(kind: str, value: str, locator: str, expected: bool) -> None:
    assert PathSelector.create(kind, value).matches(locator) is expected


def test_selector_identity_and_projection() -> None:
    selector = PathSelector.create(SelectorKind.ROOT, "engine")
    assert selector.selector_id.startswith("UCOS-URTS-")
    assert selector.to_dict()["kind"] == "root"
    assert selector.fingerprint() == PathSelector.create("root", "engine").fingerprint()
    assert selector.matches("") is False


def test_selector_rejects_malformed_declarations() -> None:
    with pytest.raises(TruthContractError):
        PathSelector.create("root", "  ")
    with pytest.raises(TruthContractError):
        PathSelector.create("root", "a/b")
    with pytest.raises(TruthContractError):
        PathSelector.create("nonsense", "a")
    with pytest.raises(TruthContractError):
        PathSelector.create(7, "a")
    with pytest.raises(TruthContractError):
        PathSelector.from_dict({"kind": "root"})
    with pytest.raises(TruthContractError):
        PathSelector.from_dict("root")


def test_truth_class_coercion() -> None:
    assert TruthClass.coerce("canonical") is TruthClass.CANONICAL
    assert TruthClass.coerce(TruthClass.EVIDENCE) is TruthClass.EVIDENCE
    with pytest.raises(TruthContractError):
        TruthClass.coerce("not-a-class")
    with pytest.raises(TruthContractError):
        TruthClass.coerce(3)


# --------------------------------------------------------------------------- zones


def test_zone_declaration_and_matching() -> None:
    zone = _zone(
        "canonical.impl",
        "canonical",
        "engine",
        authority="Implementation Authority",
        canonical_home_eligible=True,
        description="impl",
    )
    assert zone.authoritative is True
    assert zone.matches("engine/x.py") is True
    assert zone.matching_selector("engine/x.py") is not None
    assert zone.matching_selector("platform/x.py") is None
    assert zone.order_key == (-100, "canonical.impl")
    assert zone.to_dict()["canonical_home_eligible"] is True
    assert zone.fingerprint()


@pytest.mark.parametrize("truth_class", [item.value for item in NON_HOME_TRUTH_CLASSES])
def test_non_owning_classes_can_never_be_declared_a_home(truth_class: str) -> None:
    with pytest.raises(TruthContractError):
        _zone("z", truth_class, "x", canonical_home_eligible=True)


def test_authoritative_zone_requires_an_authority() -> None:
    with pytest.raises(TruthContractError):
        _zone("z", "canonical", "x")


def test_zone_rejects_malformed_declarations() -> None:
    with pytest.raises(TruthContractError):
        TruthZone.create(" ", "derived", [{"kind": "root", "value": "x"}])
    with pytest.raises(TruthContractError):
        TruthZone.create("z", "derived", [])
    with pytest.raises(TruthContractError):
        TruthZone.create("z", "derived", [{"kind": "root", "value": "x"}], precedence="high")
    with pytest.raises(TruthContractError):
        TruthZone.from_dict({"zone_id": "z"})
    with pytest.raises(TruthContractError):
        TruthZone.from_dict({"zone_id": "z", "truth_class": "derived", "selectors": "root"})
    with pytest.raises(TruthContractError):
        TruthZone.from_dict("z")
    with pytest.raises(TruthContractError):
        TruthZone(
            zone_id="z",
            truth_class=TruthClass.DERIVED,
            selectors=("not-a-selector",),  # type: ignore[arg-type]
        )
    with pytest.raises(TruthContractError):
        TruthZone(zone_id="z", truth_class="derived", selectors=())  # type: ignore[arg-type]


def test_zone_deduplicates_selectors() -> None:
    zone = TruthZone.create(
        "z",
        "derived",
        [{"kind": "root", "value": "x"}, {"kind": "root", "value": "x"}],
    )
    assert len(zone.selectors) == 1


# --------------------------------------------------------------------------- policy


def test_policy_resolves_by_declared_precedence_not_insertion_order() -> None:
    low = _zone("low", "derived", "engine", precedence=10)
    high = TruthZone.create(
        "high",
        "canonical",
        [{"kind": "segment", "value": "src"}],
        precedence=900,
        authority="Impl",
        canonical_home_eligible=True,
    )
    forward = TruthPolicy([low, high])
    backward = TruthPolicy([high, low])
    for policy in (forward, backward):
        classification = policy.classify("engine/src/x.py")
        assert classification.zone_id == "high"
        assert classification.canonical_home_eligible is True
    assert forward.zone_ids() == ("high", "low")


def test_policy_reports_honest_absence_for_undeclared_locators() -> None:
    policy = TruthPolicy([_zone("z", "derived", "engine")])
    classification = policy.classify("elsewhere/x.md")
    assert classification.truth_class is TruthClass.UNCLASSIFIED
    assert classification.classified is False
    assert classification.rule == "NO-DECLARED-ZONE"
    assert classification.authoritative is False


def test_policy_registration_is_append_only_and_fail_closed() -> None:
    zone = _zone("z", "derived", "engine")
    policy = TruthPolicy([zone])
    assert policy.register(zone) is zone
    assert policy.count == 1
    with pytest.raises(TruthPolicyError):
        policy.register(_zone("z", "derived", "platform"))
    with pytest.raises(TruthPolicyError):
        policy.register("zone")  # type: ignore[arg-type]
    with pytest.raises(TruthPolicyError):
        policy.zone("missing")
    with pytest.raises(TruthPolicyError):
        policy.classify("   ")


def test_policy_views_and_document_round_trip() -> None:
    policy = default_truth_policy()
    assert policy.policy_id == "ucos.repository.truth"
    assert policy.version == "1.0.0"
    assert policy.count == len(policy.zones())
    assert policy.of_class(TruthClass.EVIDENCE)
    assert policy.home_zones()
    assert policy.register_all(()) == policy.zones()
    rebuilt = TruthPolicy.from_document(policy.to_document())
    assert rebuilt.fingerprint() == policy.fingerprint()
    assert policy.zone("evidence.admitted-sources").truth_class is TruthClass.EVIDENCE


def test_policy_document_validation() -> None:
    with pytest.raises(TruthPolicyError):
        TruthPolicy.from_document("nope")
    with pytest.raises(TruthPolicyError):
        TruthPolicy.from_document({"policy_id": "x"})
    with pytest.raises(TruthPolicyError):
        TruthPolicy.from_document({"policy_id": "x", "zones": []})


def test_load_truth_policy_failure_modes(tmp_path: Path) -> None:
    with pytest.raises(TruthPolicyError):
        load_truth_policy(tmp_path / "missing.json")
    broken = tmp_path / "broken.json"
    broken.write_text("{", "utf-8")
    with pytest.raises(TruthPolicyError):
        load_truth_policy(broken)


def test_default_policy_classifies_the_declared_repository_zones() -> None:
    policy = default_truth_policy()
    expectations = {
        "00-SOURCE/VISION/x.docx": (TruthClass.EVIDENCE, False),
        "00-MASTER/UAKOS/closure.json": (TruthClass.OPERATIONAL_MEMORY, False),
        "00-MASTER/UCCEP/_evidence/a.md": (TruthClass.DERIVED, False),
        "02-MASTER/UCOS-COMP-000000.md": (TruthClass.DECLARATION, True),
        "platform/universal_truth/policy.py": (TruthClass.CANONICAL, True),
        "knowledge/canonical-knowledge.json": (TruthClass.GENERATED, True),
        "99-FREEZE/SOURCE-FILES.txt": (TruthClass.HISTORICAL, False),
        "platform/x/__pycache__/y.pyc": (TruthClass.TRANSIENT, False),
        "01-READINESS-ASSESSMENT.md": (TruthClass.DERIVED, False),
    }
    for locator, (expected_class, expected_home) in expectations.items():
        classification = policy.classify(locator)
        assert classification.truth_class is expected_class, locator
        assert classification.canonical_home_eligible is expected_home, locator
    assert policy.is_canonical_home("02-MASTER/x.md") is True
    assert policy.is_canonical_home("00-SOURCE/x.docx") is False


def test_partition_projection_and_counts() -> None:
    policy = default_truth_policy()
    partition = policy.classify_all(
        [
            "00-SOURCE/a.docx",
            "00-SOURCE/a.docx",
            "02-MASTER/b.md",
            "nowhere/c.txt",
            "",
        ]
    )
    assert partition.total == 3
    assert partition.count(TruthClass.EVIDENCE) == 1
    assert partition.count("unclassified") == 1
    assert len(partition.of_class(TruthClass.DECLARATION)) == 1
    assert len(partition.canonical_home_eligible()) == 1
    assert [item.locator for item in partition.unclassified()] == ["nowhere/c.txt"]
    payload = partition.to_dict()
    assert payload["total"] == 3
    assert partition.partition_id.startswith("UCOS-URTP-")
    assert partition.fingerprint()
    assert TruthPartition.create(()).total == 0


def test_classification_contract_guards() -> None:
    with pytest.raises(TruthContractError):
        TruthClassification.create("", TruthClass.CANONICAL)
    with pytest.raises(TruthContractError):
        TruthClassification.create("a.md", TruthClass.EVIDENCE, canonical_home_eligible=True)
    classification = TruthClassification.create(
        "a.md", TruthClass.CANONICAL, zone_id="z", canonical_home_eligible=True
    )
    assert classification.classification_id.startswith("UCOS-URTC-")
    assert classification.classified is True
    assert classification.fingerprint()


# --------------------------------------------------------------------------- subjects


def test_subject_normalises_locators_and_attributes() -> None:
    subject = Subject.create(
        " UCOS-COMP-000000 ",
        locators=["./a/b.md", "a/b.md", "", "c/d.md"],
        attributes={"family": "COMP"},
    )
    assert subject.subject_id == "UCOS-COMP-000000"
    assert subject.locators == ("a/b.md", "c/d.md")
    assert subject.attribute("family") == "COMP"
    assert subject.attribute("missing", "none") == "none"
    assert subject.subject_key.startswith("UCOS-URTJ-")
    assert subject.to_dict()["locators"] == ["a/b.md", "c/d.md"]
    assert subject.fingerprint()
    with pytest.raises(TruthContractError):
        Subject.create("  ")


# --------------------------------------------------------------------------- projection


def _document() -> dict[str, object]:
    return {
        "model": {
            "concepts": [
                {"id": "A", "files": ["x/a.md"], "homes": {"k": ["y/a.md"]}, "family": "F"},
                {"id": "A", "files": ["x/a2.md"]},
                {"id": "B", "files": []},
            ]
        }
    }


def test_projection_merges_records_and_flattens_locators() -> None:
    spec = ProjectionSpec.create(
        "model.concepts",
        "id",
        locator_fields=("files", "homes"),
        attribute_fields=("family",),
    )
    subjects = SubjectProjection(spec).project(_document())
    assert [subject.subject_id for subject in subjects] == ["A", "B"]
    assert subjects[0].locators == ("x/a.md", "x/a2.md", "y/a.md")
    assert subjects[0].attribute("family") == "F"
    assert subjects[1].locators == ()
    assert spec.spec_id.startswith("UCOS-URTX-")
    assert spec.fingerprint()
    assert SubjectProjection(spec).spec is spec


def test_projection_accepts_mapping_collections_and_declared_specs() -> None:
    document = {"concepts": {"b": {"id": "B"}, "a": {"id": "A", "files": ["a.md"]}}}
    subjects = project_subjects(
        document, {"collection": "concepts", "identity_field": "id", "locator_fields": ["files"]}
    )
    assert [subject.subject_id for subject in subjects] == ["A", "B"]


def test_projection_failure_modes(tmp_path: Path) -> None:
    spec = ProjectionSpec.create("concepts", "id")
    with pytest.raises(TruthProjectionError):
        SubjectProjection(spec).project({"other": []})
    with pytest.raises(TruthProjectionError):
        SubjectProjection(spec).project({"concepts": "nope"})
    with pytest.raises(TruthProjectionError):
        SubjectProjection(spec).project({"concepts": ["nope"]})
    with pytest.raises(TruthProjectionError):
        SubjectProjection(spec).project({"concepts": [{"nope": 1}]})
    with pytest.raises(TruthProjectionError):
        SubjectProjection(spec).project("nope")
    with pytest.raises(TruthProjectionError):
        SubjectProjection("nope")  # type: ignore[arg-type]
    with pytest.raises(TruthProjectionError):
        ProjectionSpec.create("", "id")
    with pytest.raises(TruthProjectionError):
        ProjectionSpec.create("c", " ")
    with pytest.raises(TruthProjectionError):
        ProjectionSpec.from_dict({"collection": "c"})
    with pytest.raises(TruthProjectionError):
        ProjectionSpec.from_dict("c")
    with pytest.raises(TruthProjectionError):
        SubjectProjection(spec).project_file(tmp_path / "missing.json")
    broken = tmp_path / "broken.json"
    broken.write_text("{", "utf-8")
    with pytest.raises(TruthProjectionError):
        SubjectProjection(spec).project_file(broken)


def test_projection_reads_a_declared_document(tmp_path: Path) -> None:
    path = tmp_path / "model.json"
    path.write_text(json.dumps({"concepts": [{"id": "A", "files": ["a.md"]}]}), "utf-8")
    spec = ProjectionSpec.create("concepts", "id", locator_fields=("files",))
    subjects = SubjectProjection(spec).project_file(path)
    assert subjects[0].locators == ("a.md",)


# --------------------------------------------------------------------------- wiring


def test_contract_surface_is_published() -> None:
    assert truth_contract_names()
    assert len(TRUTH_CONTRACTS) == len(truth_contract_names())
    assert all(ref.version == "1.0.0" for ref in TRUTH_CONTRACTS)


def test_bootstrap_and_service_registration() -> None:
    assert bootstrap_repository_truth().count == default_truth_policy().count
    assert bootstrap_repository_truth(catalog_path()).count == default_truth_policy().count
    registry = ServiceRegistry()
    descriptor = register_repository_truth(registry)
    assert descriptor.name == truth_service_descriptor().name
    resolved = registry.resolve("universal.truth")
    assert isinstance(resolved, TruthPolicy)


# --------------------------------------------------------------------------- cli


def test_cli_policy_and_classify(capsys: pytest.CaptureFixture[str]) -> None:
    assert truth_main(["policy", "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["policy_id"] == "ucos.repository.truth"
    assert truth_main(["classify", "00-SOURCE/a.docx", "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["classifications"][0]["truth_class"] == "evidence"


def test_cli_partition_gate_and_faults(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    listing = tmp_path / "locators.txt"
    listing.write_text("02-MASTER/a.md\nnowhere/b.md\n", "utf-8")
    assert truth_main(["partition", "--locators-file", str(listing), "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["unclassified"] == ["nowhere/b.md"]
    assert truth_main(["partition", "--locators-file", str(listing), "--require-classified"]) == 1
    assert truth_main(["classify", "02-MASTER/a.md", "--require-classified"]) == 0
    assert truth_main(["classify"]) == 0
    assert truth_main(["policy", "--policy", str(tmp_path / "missing.json")]) == 2


# --------------------------------------------------------------------------- roles and residues
#
# Roles are the newest half of the projection and the only declarations here that carry them
# are well formed, so the refusals that keep a role declaration honest — and the readers a
# consumer uses to ask which roles exist — had no case.


def test_a_role_declaring_no_field_or_no_name_is_refused() -> None:
    """A ROLE THAT NAMES NO FIELD NARROWS NOTHING.

    A role is a named subset of a subject's locators, so a declaration with an empty field
    list, or one whose fields are all blank, declares a role that can never be populated —
    every subject would carry it, empty, and a consumer filtering by it would get the whole
    population back. The ``$``-prefixed key is skipped rather than refused, because a
    declaration comment is not a role and refusing one would make declarations
    uncommentable.
    """
    with pytest.raises(TruthProjectionError, match="names no field") as raised:
        ProjectionSpec.create("concepts", "id", role_fields={"owner": []})
    assert raised.value.context["role"] == "owner"

    with pytest.raises(TruthProjectionError, match="names no field"):
        ProjectionSpec.create("concepts", "id", role_fields={"owner": ["", "  "]})

    commented = ProjectionSpec.create(
        "concepts", "id", role_fields={"$note": ["ignored"], "": ["ignored"], "owner": ["owners"]}
    )
    assert commented.role_names() == ("owner",)


def test_a_role_name_that_is_blank_is_refused_on_the_subject_too() -> None:
    """THE SAME CLAIM AT THE SUBJECT END, where a role is attached rather than declared.

    A subject may be constructed with roles directly — that is how a caller tags a population
    it projected itself — and a blank name there would attach a role nothing can ask for. A
    role whose members are all blank is DROPPED rather than refused, because an empty role on
    one subject is an ordinary absence: the subject simply holds none of that role's locators.
    """
    with pytest.raises(TruthContractError, match="role name must be a non-empty string"):
        Subject.create("UCOS-A", locators=["a.md"], roles={"  ": ["a.md"]})

    tagged = Subject.create(
        "UCOS-A", locators=["a.md"], roles={"owner": ["b.md"], "empty": ["", "  "]}
    )

    assert tagged.role_names() == ("owner",)
    assert tagged.role("owner") == ("b.md",)
    assert "b.md" in tagged.locators, "a role narrows the population and never introduces one"


def test_a_locator_field_holding_a_value_that_is_not_a_string_is_rendered_as_one() -> None:
    """A DECLARED LOCATOR FIELD IS FLATTENED HONESTLY, WHATEVER IT HOLDS.

    Strings, mappings and iterables each have an arm and each was exercised. The last one —
    a scalar that is none of those — had no case, and it is what a document holding a number
    or a boolean under a locator field produces. Rendering it as its string form keeps the
    projection total: dropping it would lose a declared locator silently, and raising would
    make one malformed field cost the whole document.
    """
    subjects = SubjectProjection(
        ProjectionSpec.create("concepts", "id", locator_fields=("files",))
    ).project({"concepts": [{"id": "A", "files": [7, "real.md", True]}]})

    assert subjects[0].locators == ("7", "True", "real.md")


def test_a_class_the_tally_does_not_carry_counts_zero() -> None:
    """AN ABSENT CLASS IS A COUNT OF ZERO, NOT A MISSING ANSWER.

    A partition built through ``create`` tallies EVERY declared class, zeros included, so the
    reader always finds the class it is asked about and its fallthrough is unreachable
    through any policy. It is the second defence for a partition assembled another way —
    rehydrated, or narrowed to the classes that were non-empty — where a caller asking about
    every declared class must still get a number for each. Returning None or raising would
    put a hole in a report wherever the repository happens to hold none of a class.
    """
    measured = default_truth_policy().classify_all(["00-BOOK/DATA/artifacts.json"])
    assert measured.total == 1
    assert {name for name, _ in measured.counts} == {member.value for member in TruthClass}

    narrowed = TruthPartition(
        classifications=measured.classifications,
        counts=tuple((name, value) for name, value in measured.counts if value),
    )

    absent = next(c for c in TruthClass if c.value not in {n for n, _ in narrowed.counts})
    assert narrowed.count(absent) == 0
    assert narrowed.of_class(absent) == ()


def test_zones_may_be_declared_in_one_call() -> None:
    """THE BULK DECLARATION HAD NO CALLER, and it is the form a catalogue takes.

    Every test registers zones one at a time. Declaring a whole catalogue is what the loader
    does, and it returns the zones in RESOLUTION order rather than in declaration order —
    which is the property that makes the result usable as evidence of what will match first.
    """
    registry = TruthPolicy()

    declared = registry.register_all(
        [
            _zone("test.b", "canonical", "02-MASTER", authority="UCOS-TEST"),
            _zone("test.a", "derived", "03-DERIVED"),
        ]
    )

    assert {zone.zone_id for zone in declared} == {"test.a", "test.b"}
    assert declared == registry.zones()


def test_a_duplicate_or_unnameable_locator_is_counted_once() -> None:
    """A VERDICT PER DISTINCT LOCATOR, AND DISTINCT IS AFTER NORMALISATION.

    The skip appears in BOTH readers — the ledger's own and the composed canonical-home
    policy's — and had no case in either, because every tested population is already distinct
    and non-empty.
    Two spellings of one path are one locator — that is what normalisation is for — and
    emitting a verdict for each would double-count the residue a triage is meant to size. An
    empty locator is dropped for the adjacent reason: it names nothing, so a verdict about it
    is a verdict about nothing.
    """
    ledger = EligibilityLedger.create(registered=["02-MASTER/a.md"], require_registration=True)
    composed = CanonicalHomePolicy(default_truth_policy(), ledger)

    for reader in (ledger, composed):
        verdicts = reader.verdicts(["./02-MASTER/a.md", "02-MASTER\\a.md", "", "   "])

        assert [verdict.locator for verdict in verdicts] == ["02-MASTER/a.md"]
        assert verdicts[0].to_dict() == {
            "locator": "02-MASTER/a.md",
            "eligible": verdicts[0].eligible,
            "reason": verdicts[0].reason,
        }


# -- the composition: CanonicalHomePolicy ---------------------------------------


def test_canonical_home_policy_rejects_a_non_policy() -> None:
    """The composition guard fires on both sides: a policy is a policy, a ledger is a ledger."""
    with pytest.raises(TruthEligibilityError):
        CanonicalHomePolicy("not-a-policy")  # type: ignore[arg-type]
    with pytest.raises(TruthEligibilityError):
        CanonicalHomePolicy(default_truth_policy(), "not-a-ledger")  # type: ignore[arg-type]


def test_canonical_home_policy_defaults_to_the_open_ledger() -> None:
    """With no ledger declared, every zone-eligible locator may own — and says so honestly."""
    composed = CanonicalHomePolicy(default_truth_policy())
    assert composed.ledger.enforces_anything is False
    # A canonical zone under the default policy admits its own locators.
    assert composed.admits("00-BOOK/DATA/id-ledger.json") is True
    assert composed.authority("00-BOOK/DATA/id-ledger.json") != ""


def test_canonical_home_policy_zone_loses_before_the_ledger_is_asked() -> None:
    """A non-owning class is refused by the zone alone; the ledger never gets a vote."""
    policy = TruthPolicy([_zone("evid", "evidence", "04-EVIDENCE")])
    composed = CanonicalHomePolicy(policy)
    verdict = composed.verdict("04-EVIDENCE/anything.md")
    assert verdict.eligible is False
    assert verdict.reason == REASON_ZONE_INELIGIBLE
    # A locator the zone never declares at all is also refused, not guessed about.
    assert composed.authority("nowhere/x.md") == ""


def test_canonical_home_policy_ledger_loses_after_the_zone_passes() -> None:
    """A zone-eligible locator can still be refused by the artifact eligibility ledger."""
    policy = TruthPolicy(
        [
            TruthZone.create(
                "book",
                "canonical",
                [{"kind": "root", "value": "00-BOOK"}],
                authority="UCKP-LAW-0001",
                canonical_home_eligible=True,
            )
        ]
    )
    ledger = EligibilityLedger.create(require_registration=True, registered=("00-BOOK/known.json",))
    composed = CanonicalHomePolicy(policy, ledger)

    known = composed.verdict("00-BOOK/known.json")
    unknown = composed.verdict("00-BOOK/other.json")
    assert known.eligible is True
    assert unknown.eligible is False
    assert unknown.reason == REASON_NOT_REGISTERED


def test_canonical_home_policy_triages_by_reason() -> None:
    """by_reason groups a mixed population so each cause of refusal is visible on its own."""
    policy = TruthPolicy(
        [
            TruthZone.create(
                "book",
                "canonical",
                [{"kind": "root", "value": "00-BOOK"}],
                authority="UCKP-LAW-0001",
                canonical_home_eligible=True,
            ),
            _zone("evid", "evidence", "04-EVIDENCE"),
        ]
    )
    ledger = EligibilityLedger.create(require_registration=True, registered=("00-BOOK/kept.md",))
    composed = CanonicalHomePolicy(policy, ledger)

    grouped = composed.by_reason(
        ["00-BOOK/kept.md", "00-BOOK/dropped.md", "04-EVIDENCE/any.md", ""]
    )
    assert grouped[REASON_ELIGIBLE] == ["00-BOOK/kept.md"]
    assert grouped[REASON_NOT_REGISTERED] == ["00-BOOK/dropped.md"]
    assert grouped[REASON_ZONE_INELIGIBLE] == ["04-EVIDENCE/any.md"]
    # The empty locator was dropped, not given a verdict about nothing.
    assert "" not in grouped.get(REASON_ELIGIBLE, [])


def test_canonical_home_policy_round_trips_and_is_stable() -> None:
    """to_dict is a projection of both declarations and fingerprint is deterministic."""
    policy = TruthPolicy(
        [
            TruthZone.create(
                "book",
                "canonical",
                [{"kind": "root", "value": "00-BOOK"}],
                authority="UCKP-LAW-0001",
                canonical_home_eligible=True,
            )
        ]
    )
    ledger = EligibilityLedger.create(
        require_registration=True, registered=("00-BOOK/a.md",), description="kept"
    )
    composed = CanonicalHomePolicy(policy, ledger)

    projection = composed.to_dict()
    assert (
        projection["policy"]["zones"] and projection["eligibility"]["require_registration"] is True
    )
    assert composed.fingerprint() == CanonicalHomePolicy(policy, ledger).fingerprint()
    assert composed.fingerprint() != CanonicalHomePolicy(policy, open_ledger()).fingerprint()


def test_load_eligibility_ledger_fails_closed_on_bad_input(tmp_path: Path) -> None:
    """An unreadable or malformed eligibility document is refused, never treated as open."""
    missing = tmp_path / "nope.json"
    with pytest.raises(TruthEligibilityError):
        load_eligibility_ledger(missing)

    malformed = tmp_path / "bad.json"
    malformed.write_text("{not json", encoding="utf-8")
    with pytest.raises(TruthEligibilityError):
        load_eligibility_ledger(malformed)

    wrong_shape = tmp_path / "wrong.json"
    wrong_shape.write_text(json.dumps({"admitted_suffixes": "not-a-sequence"}), encoding="utf-8")
    with pytest.raises(TruthEligibilityError):
        load_eligibility_ledger(wrong_shape)


def test_eligibility_ledger_reports_its_own_enforcement_state() -> None:
    """A ledger states whether it imposes anything, which is how an open one is told apart."""
    assert open_ledger().enforces_anything is False
    assert EligibilityLedger.create(admitted_suffixes=(".json",)).enforces_anything is True

    requiring = EligibilityLedger.create(require_registration=True, registered=("a.json",))
    with pytest.raises(TruthEligibilityError):
        EligibilityLedger.create(require_registration=True).verdict("a.json")
    assert requiring.verdict("a.json").eligible is True
