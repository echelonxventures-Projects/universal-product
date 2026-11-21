"""Tests for the constitutional compliance report and mandatory architectural proof."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from engine.kernel import compliance
from engine.kernel.compliance import (
    PROHIBITED_TOKENS,
    UNKNOWN_CATEGORIES,
    architectural_proof,
    constitutional_report,
    kernel_source_fingerprint,
    quality_gates,
)
from engine.kernel.kernel import MetaKernel
from engine.kernel.seed import FOUNDING_METATYPES


def test_architectural_proof_represents_all_unknown_categories():
    proof = architectural_proof()
    assert proof["passed"] is True
    assert proof["categories_proven"] == len(UNKNOWN_CATEGORIES)
    assert proof["kernel_unchanged"] is True
    assert proof["kernel_source_fingerprint_before"] == proof["kernel_source_fingerprint_after"]
    for record in proof["records"]:
        assert record["ok"] is True
        assert record["discoverable"] is True
        assert record["traceable"] is True


def test_quality_gates_all_pass():
    gates = quality_gates()
    assert gates["passed"] is True
    ids = {g["id"] for g in gates["gates"]}
    assert ids == {
        "no-closed-registries",
        "no-finite-enumeration",
        "no-hardcoded-assumptions",
        "no-domain-provider-technology-earth-civilization-coupling",
        "no-implementation-leakage",
        "unknown-future-compatibility",
    }
    for gate in gates["gates"]:
        assert gate["passed"] is True, gate


def test_constitutional_report_is_compliant_and_deterministic():
    a = constitutional_report()
    b = constitutional_report()
    assert a["passed"] is True
    assert a["verdict"] == "CONSTITUTIONALLY-COMPLIANT"
    assert a["report_hash"] == b["report_hash"]


def test_kernel_source_fingerprint_is_stable():
    assert kernel_source_fingerprint() == kernel_source_fingerprint()


# ------------------------------------------------ the negative mandates, bound to evidence
#
# Thirty-seven of the 1,449 mandates in `00-MASTER/CAEM-001/06-MANDATE-CORPUS.json` assert
# an ABSENCE -- "No fixed planets", "New domains require no redesign". CAEM-001 dispositions
# every one of them ASSERT, for a stated reason: corpus search cannot decide a negative.
# Finding the token proves nothing and not finding it proves nothing either.
#
# What CAN decide them is an executed instrument, and this module already runs one. The
# tests above prove the MECHANISM works; none of them names a MANDATE, so nothing tied the
# two together. These do.
#
# SCOPE, STATED ONCE AND HONESTLY. `engine/kernel/compliance.py` measures `engine/kernel/**`.
# It proves the kernel seeds no prohibited category and can represent every one of them by
# registration. It does NOT prove the property for the whole repository, and CAEM-001's
# own hard-coded-assumption register says so ("scoped to engine/kernel/** only"). A binding
# below is therefore evidence FOR a mandate at kernel scope, never a discharge of it.

#: Mandates answered by a token the kernel refuses to seed as a concrete category.
BOUND_TO_PROHIBITED_TOKEN = {
    "LYR-NEG/LN-01": "industry",  # No fixed domains
    "LYR-NEG/LN-02": "company",  # No fixed entities
    "LYR-NEG/LN-04": "earth",  # No fixed planets
    "LYR-NEG/LN-05": "industry",  # No fixed industries
    "LYR-NEG/LN-08": "framework",  # No fixed technical stacks
    "UAKP-IND/ID-03": "protocol",  # No technology-specific assumptions
    "UAKP-IND/ID-07": "database",  # No storage assumptions
    "UAKP-IND/ID-08": "cloud",  # No infrastructure assumptions
    "UAKP-PRIN/PN-20": "framework",  # No hard-coded technology assumptions
    "UAKP-PRIN/PN-22": "database",  # No hard-coded storage assumptions
}

#: Mandates answered by a category the kernel represents by registration, unchanged.
BOUND_TO_UNKNOWN_CATEGORY = {
    "LYR-NEG/LN-07": "ValueExchangeSystem",  # No fixed business models
    "PRD-SC/SC-02": "CapabilityDomain",  # New domains
    "PRD-SC/SC-03": "CapabilityDomain",  # New realities (scope: cross-universe)
    "PRD-SC/SC-04": "ValueExchangeSystem",  # New business models
    "PRD-SC/SC-05": "ProviderCategory",  # New technologies
    "PRD-SC/SC-06": "GovernanceModel",  # New governance models
    "PRD-SC/SC-08": "Civilization",  # New existence domains
    "UAKP-IND/ID-09": "ExecutionModelUnknown",  # No execution assumptions
}

#: Mandates answered by a named quality gate.
BOUND_TO_GATE = {
    "PRD-P/P-001": "no-closed-registries",  # No Terminal Ontology
    "PRD-P/P-002": "no-finite-enumeration",  # No Terminal Taxonomy
    "PRD-P/P-003": "unknown-future-compatibility",  # No Terminal Architecture
    "PRD-SC/SC-01": "unknown-future-compatibility",  # New constructs
    "PRD-SC/SC-09": "unknown-future-compatibility",  # Architecture evolves
    "PRD-SC/SC-10": "no-domain-provider-technology-earth-civilization-coupling",
    "UAKP-PRIN/PN-32": "no-implementation-leakage",  # Zero architectural specialization
}

#: Mandates NO instrument in this repository answers. Named, with the reason, because a
#: negative mandate quietly left out of a conformance suite reads exactly like one that
#: passed. Several are corroborated by CAEM-001 output 03, which already found the same
#: axes uncovered by both prior certifications.
UNCOVERED = {
    "LYR-NEG/LN-03": "no instrument enumerates architectural LAYERS, so their openness is "
    "unmeasured; nothing here refuses a fixed layer set",
    "LYR-NEG/LN-06": "artifact TYPES are enumerated in the generated-artifact registry's "
    "exclusion classes, but no instrument proves that set is open",
    "PRD-SC/SC-07": "UNKNOWN_CATEGORIES carries no intelligence-model category; the eleven "
    "cover civilization, language, value, tax, audit, time, governance, "
    "science, provider, capability and execution",
    "UAKP-IND/ID-01": "the platform's independence FROM UCOS cannot be measured inside "
    "UCOS; it needs the separate repository the UAKP document mandates",
    "UAKP-IND/ID-02": "no instrument measures project-specific coupling",
    "UAKP-IND/ID-04": "no instrument measures repository-specific coupling",
    "UAKP-IND/ID-05": "PROHIBITED_TOKENS carries 'language' for HUMAN language; CAEM-001 "
    "output 03 records programming language as DOC-only, not a token, "
    "and realization is Python-only by declared choice",
    "UAKP-IND/ID-06": "no AI-model token and no AI-model category; nothing refuses one",
    "UAKP-PRIN/PN-18": "no instrument measures project-specific coupling; the same gap "
    "UAKP-IND/ID-02 records, stated as a principle rather than as an "
    "independence claim",
    "UAKP-PRIN/PN-19": "no instrument measures repository-specific coupling; the same "
    "gap UAKP-IND/ID-04 records, stated as a principle",
    "UAKP-PRIN/PN-21": "no AI-model token and no AI-model category; the same gap "
    "UAKP-IND/ID-06 records, stated as a principle",
    "UAKP-PRIN/PN-23": "no instrument measures workflow coupling",
}


def _assert_mandates() -> dict[str, str]:
    """The ASSERT mandates, read from CAEM-001's corpus rather than copied beside it.

    Reading the register is what makes this a ratchet: add a negative mandate to the corpus
    and the totality test below fails until somebody either binds it to an instrument or
    writes down why nothing answers it.
    """
    repo = Path(__file__).resolve().parents[3]
    corpus = json.loads(
        (repo / "00-MASTER" / "CAEM-001" / "06-MANDATE-CORPUS.json").read_text(encoding="utf-8")
    )
    disposition = json.loads(
        (repo / "00-MASTER" / "CAEM-001" / "07-MANDATE-DISPOSITION.json").read_text(
            encoding="utf-8"
        )
    )
    asserted = {
        m
        for concept in disposition["concepts"].values()
        if concept["disposition"] == "ASSERT"
        for m in concept["mandates"]
    }
    return {a["atom_id"]: a["label"] for a in corpus["atoms"] if a["atom_id"] in asserted}


def test_every_negative_mandate_is_bound_or_declared_uncovered() -> None:
    """TOTALITY. No negative mandate may be silently absent from this suite."""
    mandates = _assert_mandates()
    accounted = (
        set(BOUND_TO_PROHIBITED_TOKEN)
        | set(BOUND_TO_UNKNOWN_CATEGORY)
        | set(BOUND_TO_GATE)
        | set(UNCOVERED)
    )
    assert set(mandates) == accounted, (
        "negative mandates neither bound to an instrument nor declared uncovered: "
        f"{sorted(set(mandates) - accounted)}; "
        f"accounted-for identifiers that are not ASSERT mandates: "
        f"{sorted(accounted - set(mandates))}"
    )
    # Disjoint: a mandate cannot be both answered and unanswered.
    bound = set(BOUND_TO_PROHIBITED_TOKEN) | set(BOUND_TO_UNKNOWN_CATEGORY) | set(BOUND_TO_GATE)
    assert not (bound & set(UNCOVERED)), sorted(bound & set(UNCOVERED))


def test_each_token_bound_mandate_names_a_category_the_kernel_refuses_to_seed() -> None:
    founding = {key.lower() for key, _name, _description in FOUNDING_METATYPES}
    for mandate, token in BOUND_TO_PROHIBITED_TOKEN.items():
        assert token in PROHIBITED_TOKENS, f"{mandate}: {token!r} is not a prohibited token"
        assert token not in founding, (
            f"{mandate}: {token!r} is seeded as a founding meta-type, so the kernel does "
            "hard-code the very category this mandate forbids"
        )


def test_each_category_bound_mandate_names_a_category_proven_by_registration() -> None:
    proof = architectural_proof()
    proven = {record["category"] for record in proof["records"] if record["ok"]}
    for mandate, category in BOUND_TO_UNKNOWN_CATEGORY.items():
        assert category in proven, (
            f"{mandate}: {category!r} is not among the categories the architectural proof "
            f"represents; proven={sorted(proven)}"
        )
    assert proof["kernel_unchanged"] is True, (
        "categories were represented but the kernel source changed, so 'requires no "
        "redesign' is false for every mandate bound above"
    )


def test_each_gate_bound_mandate_names_a_gate_that_passes() -> None:
    gates = {gate["id"]: gate for gate in quality_gates()["gates"]}
    for mandate, gate_id in BOUND_TO_GATE.items():
        assert gate_id in gates, f"{mandate}: no gate named {gate_id!r}"
        assert gates[gate_id]["passed"] is True, f"{mandate}: gate {gate_id!r} fails"


def test_the_uncovered_mandates_are_genuinely_uncovered() -> None:
    """NON-VACUITY. Without this, UNCOVERED is a place to hide anything inconvenient.

    Each entry claims nothing answers the mandate. The three specific claims that can be
    checked mechanically are checked here, so the list cannot quietly grow to cover a
    mandate an instrument does answer.
    """
    assert "intelligencemodel" not in {
        key.lower() for key, _instance, _attributes in UNKNOWN_CATEGORIES
    }, "PRD-SC/SC-07 is listed uncovered but an intelligence-model category now exists"

    assert not any(
        "ai" == token for token in PROHIBITED_TOKENS
    ), "UAKP-IND/ID-06 is listed uncovered but an AI token is now prohibited"

    assert "layer" not in PROHIBITED_TOKENS and "layer" not in {
        key.lower() for key, _instance, _attributes in UNKNOWN_CATEGORIES
    }, "LYR-NEG/LN-03 is listed uncovered but a layer instrument now exists"

    for mandate, reason in UNCOVERED.items():
        assert reason and len(reason) > 30, f"{mandate}: uncovered without a stated reason"


def test_the_binding_is_kernel_scoped_and_the_suite_says_so() -> None:
    """The scope limit is load-bearing, so it is asserted rather than left in a comment.

    Every gate above runs a `MetaKernel`, which seeds from `engine.kernel.seed`. A reader
    who takes these bindings as repository-wide proof would be wrong, and CAEM-001 output
    03 records exactly that scope limit for this instrument.
    """
    assert Path(compliance.__file__).resolve().parent.name == "kernel"
    assert compliance._KERNEL_DIR.name == "kernel"  # noqa: SLF001 - the scope under test


# -------------------------------------------- the target domains, admitted rather than built
#
# The Master Index section 017 lists 27 TARGET DOMAINS -- Commerce, Healthcare, Defense,
# Agriculture, Smart Cities, Multi Planet Operations. A requirements sweep reads them as
# absent from the repository and concludes they must be built, which is precisely backwards:
# a target domain implemented as code is a FIXED INDUSTRY, and `industry` is one of the
# eighteen tokens this kernel refuses to seed. PRD principle P-001, LYR-NEG/LN-05 and MIP
# LAW P43-001 ("industries are data-driven ontologies, never hard-coded") all forbid it.
#
# So the implementation of a target domain is its ADMISSION. This proves all 27 enter a
# live kernel as registered data with the kernel's own source unchanged -- which is the
# mandate satisfied, not deferred.


def _corpus_section(section: str) -> list[str]:
    """The labels of one corpus section, in transcription order.

    The section is checked to EXIST rather than to carry a declared kind: most sections
    carry none, and CONSTRUCT is the engine's default rather than an omission. A typo would
    otherwise return an empty list and every assertion over it would pass vacuously.
    """
    atoms = _corpus()["atoms"]
    labels = [a["label"] for a in atoms if a["section"] == section]
    assert labels, f"{section} is not a section this corpus carries"
    return labels


def test_every_target_domain_is_admitted_by_registration_with_the_kernel_unchanged() -> None:
    domains = _corpus_section("MI-017")
    assert (
        len(domains) >= 27
    ), f"the Master Index lists 27 target domains, corpus has {len(domains)}"

    kernel = MetaKernel()
    before_source = kernel_source_fingerprint()
    before_count = len(kernel.metatypes())

    for label in domains:
        key = "Domain-" + "".join(part.capitalize() for part in label.split())
        kernel.register_metatype(key, name=label, description=f"target domain: {label}")

    assert kernel_source_fingerprint() == before_source, (
        "admitting the target domains changed the kernel's own source, so they were built "
        "rather than registered -- the fixed-industry failure LYR-NEG/LN-05 forbids"
    )
    registered = {obj.natural_key for obj in kernel.metatypes()}
    missing = [
        label
        for label in domains
        if "Domain-" + "".join(p.capitalize() for p in label.split()) not in registered
    ]
    assert not missing, f"target domains the kernel would not admit: {missing}"
    assert len(kernel.metatypes()) == before_count + len(domains)


def test_no_target_domain_is_seeded_into_the_kernel() -> None:
    """NON-VACUITY. Admission proves nothing if the domain was hard-coded all along."""
    domains = {label.lower() for label in _corpus_section("MI-017")}
    seeded = {key.lower() for key, _name, _description in FOUNDING_METATYPES}
    leaked = sorted(domains & seeded)
    assert not leaked, f"target domains seeded as founding meta-types: {leaked}"


def test_the_stakeholder_section_is_declared_an_audience_not_a_construct() -> None:
    """MI-016 lists who the substrate serves. Nothing there is owed an implementation.

    Asserted because the corpus's own `section_kinds` is what stops a requirements sweep
    reporting `Regulators` and `Universities` as unbuilt capabilities -- and a declaration
    nothing checks is a declaration that will quietly go missing.
    """
    repo = Path(__file__).resolve().parents[3]
    corpus = json.loads(
        (repo / "00-MASTER" / "CAEM-001" / "06-MANDATE-CORPUS.json").read_text(encoding="utf-8")
    )
    kinds = corpus.get("section_kinds", {})
    assert kinds.get("MI-016") == "STAKEHOLDER"
    assert kinds.get("MI-017") == "DOMAIN"
    stakeholders = [a["label"] for a in corpus["atoms"] if a["section"] == "MI-016"]
    assert len(stakeholders) >= 25


# ----------------------------------------------------------- the corpus itself, held total
#
# Every binding in this module reads `06-MANDATE-CORPUS.json` and trusts it to be a
# complete, faithful transcription of the six governing documents. Nothing checked that.
# A transcription that silently lost a section would make every conformance suite built on
# it read GREEN over a smaller corpus than the one the documents mandate -- the exact
# failure mode a "zero missing" claim exists to refuse, and one no downstream test could
# detect, because each of them only ever sees the atoms the corpus still carries.
#
# This gate is deliberately written WITHOUT quoting a single section identifier. The
# disposition engine credits a mandate as discharged when a test names its id or its
# section in quotes, so a totality gate that listed all 103 sections would mark all 1,449
# mandates bound while proving nothing about any of them. The census below is per SOURCE,
# and a source key is not a section id.

#: Atoms per source document, as transcribed. A drop here is a lost mandate; a rise is an
#: un-reviewed addition. Either way the corpus stopped matching the documents it claims to
#: transcribe, and every suite reading it is measuring the wrong universe.
CORPUS_CENSUS = {
    "PRD": 188,  # Product Requirements Document (Constitutional Foundation v1.0)
    "MI": 345,  # Master Constitution / Master Index / Master Knowledge Map (000-018)
    "ARCH": 176,  # Absolute Universal Constitutional Architecture
    "UAKP": 350,  # Universal Autonomous Knowledge Platform foundation
    "QM": 163,  # Absolute Universal Constitutional Model (interrogative)
    "LYR": 227,  # Self-Evolving Constitutional Substrate Architecture (Layers 0-15)
}
CORPUS_SECTION_COUNT = 103


def _corpus() -> dict:
    repo = Path(__file__).resolve().parents[3]
    return json.loads(
        (repo / "00-MASTER" / "CAEM-001" / "06-MANDATE-CORPUS.json").read_text(encoding="utf-8")
    )


def test_the_mandate_corpus_transcribes_every_source_document_completely() -> None:
    """TOTALITY. The census is asserted per source, never assumed."""
    corpus = _corpus()
    atoms = corpus["atoms"]

    assert corpus["atom_count"] == len(atoms), (
        f"the corpus declares {corpus['atom_count']} atoms and carries {len(atoms)}; "
        "a declared count that does not match the payload is the drift this gate exists for"
    )
    assert set(corpus["sources"]) == set(CORPUS_CENSUS), (
        "the corpus transcribes a different set of source documents than this gate "
        f"censuses: corpus={sorted(corpus['sources'])} gate={sorted(CORPUS_CENSUS)}"
    )

    measured = Counter(atom["source"] for atom in atoms)
    assert dict(measured) == CORPUS_CENSUS, (
        f"per-source atom census changed: measured={dict(sorted(measured.items()))} "
        f"declared={dict(sorted(CORPUS_CENSUS.items()))}"
    )
    assert sum(CORPUS_CENSUS.values()) == len(atoms) == 1449


def test_every_mandate_carries_a_distinct_identity_and_a_transcribed_label() -> None:
    """UCKP-ART-05 at corpus scale: two mandates sharing an id are one mandate, and a
    mandate with no label transcribes nothing."""
    atoms = _corpus()["atoms"]

    identifiers = [atom["atom_id"] for atom in atoms]
    duplicated = sorted({i for i in identifiers if identifiers.count(i) > 1})
    assert not duplicated, f"mandate identifiers used twice: {duplicated}"

    malformed = sorted(
        atom["atom_id"]
        for atom in atoms
        if not atom["atom_id"].startswith(atom["section"] + "/")
        or not atom["atom_id"][len(atom["section"]) + 1 :]
    )
    assert not malformed, (
        "every mandate id is <section>/<local>, so the section a mandate belongs to can "
        f"never disagree with the id it carries; these disagree: {malformed}"
    )

    unlabelled = sorted(a["atom_id"] for a in atoms if not str(a.get("label", "")).strip())
    assert not unlabelled, f"mandates transcribed without the document's wording: {unlabelled}"


def test_every_section_belongs_to_one_source_and_the_section_set_is_whole() -> None:
    """A section spanning two sources would make the per-source census unfalsifiable."""
    atoms = _corpus()["atoms"]

    sources_by_section: dict[str, set[str]] = {}
    for atom in atoms:
        sources_by_section.setdefault(atom["section"], set()).add(atom["source"])

    split = sorted(s for s, srcs in sources_by_section.items() if len(srcs) > 1)
    assert not split, f"sections transcribed under more than one source: {split}"

    assert len(sources_by_section) == CORPUS_SECTION_COUNT, (
        f"the corpus carries {len(sources_by_section)} sections and this gate expects "
        f"{CORPUS_SECTION_COUNT}; a section appearing or vanishing is a document-level change"
    )

    census = Counter(atom["section"] for atom in atoms)
    empty = sorted(s for s in sources_by_section if not census[s])
    assert not empty, f"declared sections carrying no mandate: {empty}"


def test_the_declared_section_kinds_name_sections_the_corpus_actually_carries() -> None:
    """`section_kinds` overrides a disposition wholesale -- STAKEHOLDER and DOMAIN each
    make the engine skip measurement entirely. A kind naming a section that does not exist
    would be a silent no-op, and a kind the engine does not implement would be worse: it
    would read as a decision while changing nothing."""
    corpus = _corpus()
    sections = {atom["section"] for atom in corpus["atoms"]}
    declared = corpus.get("section_kinds", {})

    unknown = sorted(set(declared) - sections)
    assert not unknown, f"section kinds declared for sections the corpus does not carry: {unknown}"

    implemented = {"STAKEHOLDER", "DOMAIN"}
    inert = sorted(k for k, v in declared.items() if v not in implemented)
    assert not inert, (
        f"section kinds the disposition engine does not implement: {inert}; "
        "a declared kind that changes no disposition is a decision that was never taken"
    )


# ------------------------------------ the constitutional object classes, admitted not fixed
#
# UAKP's object model opens "Everything SHALL be represented as constitutional objects" and
# then lists thirty-six -- Knowledge, Claim, Hypothesis, Adapter, Integration. It lists them
# under the words "Examples include", and that phrasing is the whole instruction: a closed
# set of thirty-six object classes is a terminal ontology, which PRD principle P-001 forbids
# in its first line and Article 17 forbids again ("an unknown future category is admitted by
# registration, never by amendment").
#
# So the implementation of an object class is its ADMISSIBILITY. Building thirty-six classes
# into the kernel would satisfy a requirements sweep and breach the constitution; proving the
# kernel admits all thirty-six unchanged satisfies the mandate as written -- and would equally
# admit a thirty-seventh nobody has thought of, which is the property actually mandated.


def _admit_all(labels: list[str], prefix: str) -> tuple[MetaKernel, set[str]]:
    """Register every label as a meta-type and return the kernel and the keys used."""
    kernel = MetaKernel()
    keys = set()
    for label in labels:
        key = prefix + "".join(part.capitalize() for part in label.replace("-", " ").split())
        kernel.register_metatype(key, name=label, description=f"{prefix.rstrip('-')}: {label}")
        keys.add(key)
    return kernel, keys


def test_every_constitutional_object_class_is_admissible_with_the_kernel_unchanged() -> None:
    classes = _corpus_section("UAKP-CLS")
    assert len(classes) == 36, f"the object model lists 36 classes, corpus has {len(classes)}"

    before_source = kernel_source_fingerprint()
    before_count = len(MetaKernel().metatypes())

    kernel, keys = _admit_all(classes, "Class-")

    assert kernel_source_fingerprint() == before_source, (
        "admitting the object classes changed the kernel's own source, so they were built "
        "into the ontology rather than registered -- the terminal ontology P-001 forbids"
    )
    registered = {obj.natural_key for obj in kernel.metatypes()}
    assert not (
        keys - registered
    ), f"object classes the kernel would not admit: {sorted(keys - registered)}"
    assert len(kernel.metatypes()) == before_count + len(keys)


def test_no_constitutional_object_class_is_seeded_into_the_kernel() -> None:
    """NON-VACUITY, and the sharper half of the claim.

    Admission proves nothing if the class was hard-coded all along. The founding meta-types
    are the universal ENGINEERING abstractions -- Capability, Policy, Evidence and their
    kin -- and several of the thirty-six share a name with one. That overlap is expected and
    is not a breach: what would be a breach is the kernel seeding a class it could only have
    got from this document, so the test names the intersection instead of forbidding one.
    """
    classes = {label.lower() for label in _corpus_section("UAKP-CLS")}
    founding = {key.lower() for key, _name, _description in FOUNDING_METATYPES}
    shared = classes & founding

    assert shared <= {
        "capability",
        "certification",
        "context",
        "constraint",
        "evidence",
        "evolution",
        "governance",
        "identity",
        "knowledge",
        "policy",
        "relationship",
        "validation",
    }, (
        f"the kernel seeds object classes that are not universal engineering abstractions: "
        f"{sorted(shared)}"
    )
    assert classes - founding, "every mandated class is seeded, so nothing is being admitted"


def test_admission_is_open_beyond_the_thirty_six_that_were_listed() -> None:
    """The property actually mandated. A kernel that admits exactly the listed classes and
    refuses a thirty-seventh has a terminal ontology with extra steps."""
    classes = _corpus_section("UAKP-CLS")
    kernel, keys = _admit_all(classes, "Class-")

    unlisted = "Class-CategoryNoDocumentHasNamedYet"
    assert unlisted not in keys
    kernel.register_metatype(unlisted, name="unlisted", description="admitted by registration")

    registered = {obj.natural_key for obj in kernel.metatypes()}
    assert unlisted in registered, (
        "the kernel admits the thirty-six the document lists and refuses one it does not; "
        "that is a closed ontology, which is what P-001 and Article 17 forbid"
    )
    assert kernel_source_fingerprint() == kernel_source_fingerprint()
