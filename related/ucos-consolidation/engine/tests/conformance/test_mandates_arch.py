"""Mandate conformance — the Absolute Universal Constitutional Architecture diagram.

176 mandates over 14 sections. Each suite below takes one section, locates what the
repository actually holds for it, and declares what it cannot prove.
"""

from __future__ import annotations

from engine.tests.conformance.mandate_corpus import (
    assert_absence_rule_can_find_something,
    assert_homes_exist,
    assert_named_by_nothing,
    assert_partitions,
    section,
)
from engine.uckp.facets import REQUIRED_FACETS, Facet

# --- ARCH-CERTV — the eight certification verdicts ------------------------------
#
# The Quality & Trust Fabric ends in Universal Certification and names its verdict set:
# PASS, REUSE, EXTEND, CREATE, SUPERSEDE, DEPRECATE, BLOCKED, NOT_APPLICABLE, under the
# rule "No mandatory obligation may fail." A verdict set is the one part of a governance
# diagram that must exist as VALUES a running instrument can return -- a verdict nothing
# emits is a verdict nobody can receive.
#
# So this binding asks a narrow, checkable question of each: does some instrument in this
# repository emit this verdict? Two do not, and the reasons differ enough to matter.

#: Verdict -> the module that emits it, and the symbol carrying the value.
VERDICT_EMITTED = {
    "ARCH-CERTV/CV-01": ("engine/certification/closure.py", "PASS"),
    "ARCH-CERTV/CV-02": ("engine/constitution/assimilation.py", "REUSE"),
    "ARCH-CERTV/CV-04": ("engine/constitution/assimilation.py", "CREATE"),
    "ARCH-CERTV/CV-05": ("engine/registry/universal/records.py", "SUPERSEDE"),
    "ARCH-CERTV/CV-06": ("engine/registry/universal/records.py", "DEPRECATE"),
    "ARCH-CERTV/CV-07": ("engine/registry/models.py", "BLOCKED"),
}

#: EXTEND is not a verdict here; it is REUSE carrying targets. `AssimilationVerdict.status`
#: returns exactly CREATE or REUSE, and `reuse_targets` is documented as "the existing
#: subjects the caller should extend instead". The instruction the diagram spells EXTEND is
#: delivered -- under another name and in another field -- so recording it as absent would
#: be false and recording it as emitted would be false too.
VERDICT_EXPRESSED_DIFFERENTLY = {
    "ARCH-CERTV/CV-03": (
        "engine/constitution/assimilation.py",
        "reuse_targets",
        "status returns CREATE or REUSE only; the extend instruction rides on reuse_targets",
    ),
}

#: Emitted by nothing. NOT_APPLICABLE is the verdict that lets an obligation be dismissed
#: without being met, which is exactly why its absence is worth stating: the rule "no
#: mandatory obligation may fail" has no escape hatch here, by omission rather than design.
VERDICT_ABSENT = {
    "ARCH-CERTV/CV-08": "NOT_APPLICABLE",
}


def test_every_certification_verdict_is_emitted_expressed_or_absent() -> None:
    mandates = section("ARCH-CERTV")
    assert len(mandates) == 8, f"the diagram names 8 verdicts, corpus has {len(mandates)}"
    assert_partitions(
        "ARCH-CERTV",
        mandates,
        VERDICT_EMITTED,
        VERDICT_EXPRESSED_DIFFERENTLY,
        VERDICT_ABSENT,
    )


def test_every_emitted_verdict_appears_as_a_value_in_its_module() -> None:
    """The verdict must be a VALUE, not a word in a comment. Each is checked as a quoted
    string literal, which is how a returnable verdict is written in this codebase."""
    from engine.tests.conformance.mandate_corpus import repo_root

    homes = {m: home for m, (home, _symbol) in VERDICT_EMITTED.items()}
    assert_homes_exist("ARCH-CERTV", homes)
    for mandate, (home, symbol) in VERDICT_EMITTED.items():
        text = (repo_root() / home).read_text(encoding="utf-8")
        assert f'"{symbol}"' in text, (
            f"ARCH-CERTV/{mandate}: {home} is declared to emit {symbol!r} and carries no "
            "such value; a verdict nothing emits is a verdict nobody can receive"
        )


def test_the_assimilation_gate_really_returns_only_create_or_reuse() -> None:
    """NON-VACUITY for CV-03. The claim is that EXTEND is not a status this gate can
    return. If it ever becomes one, the row moves to EMITTED and this tiering is wrong."""
    import inspect

    from engine.constitution.assimilation import AssimilationVerdict

    body = inspect.getsource(AssimilationVerdict.status.fget)
    assert '"CREATE"' in body and '"REUSE"' in body
    assert '"EXTEND"' not in body, (
        "the assimilation gate now returns EXTEND as a status; ARCH-CERTV/CV-03 is emitted "
        "rather than expressed differently"
    )
    assert "extend" in (AssimilationVerdict.reuse_targets.fget.__doc__ or "").lower(), (
        "reuse_targets no longer documents itself as what the caller should extend; the "
        "claim that the EXTEND instruction rides on it is no longer supported"
    )


def test_the_absent_verdict_is_emitted_by_nothing() -> None:
    """NON-VACUITY. Searched as a quoted value across every tracked Python file, because
    the question is whether anything can RETURN it, not whether anything mentions it."""
    from engine.tests.conformance.mandate_corpus import repo_root, tracked

    for mandate, verdict in VERDICT_ABSENT.items():
        emitters = [
            path
            for path in tracked()
            if path.endswith(".py")
            and "/tests/" not in path
            and f'"{verdict}"' in (repo_root() / path).read_text(encoding="utf-8", errors="ignore")
        ]
        assert (
            not emitters
        ), f"ARCH-CERTV/{mandate}: {verdict} is declared absent but is emitted by {emitters}"


def test_the_naming_rule_this_suite_relies_on_can_find_something() -> None:
    assert_absence_rule_can_find_something("constitution assimilation")


def test_absence_search_does_not_silently_match_nothing() -> None:
    assert_named_by_nothing("ARCH-CERTV", {"ARCH-CERTV/CV-08": "not applicable verdict"})


# --- ARCH-UCMM — the thirty concepts of the Universal Constitutional Meta Model --
#
# The diagram places the UCMM directly beneath the Absolute Constitutional Kernel and lists
# thirty universals in three columns. A meta-model is not a component inventory: it is the
# set of things every object in the system must be describable IN. Article 6 answers exactly
# that question with thirty-three facets -- "a question every constitutional object must be
# able to answer about itself" -- so the facets are the natural respondent, and the concepts
# they do not cover are the honest measure of the gap between diagram and law.
#
# Three tiers, and the boundary between the first two carries the weight. A FACET is
# carried by every object; a MODULE is a capability the substrate has. "Universal Trust"
# answered by `platform/foundation/trust.py` is a real answer and a weaker one than
# "Universal Identity" answered by a facet every UCKO must fill, and flattening them would
# report a meta-model that is complete when it is not.

#: Meta-model concept -> the universal facet that carries it on every object.
META_MODEL_FACET = {
    "ARCH-UCMM/UM-01": Facet.IDENTITY,  # Universal Identity
    "ARCH-UCMM/UM-02": Facet.RELATIONSHIPS,  # Universal Relationships
    "ARCH-UCMM/UM-03": Facet.CONTEXT,  # Universal Context
    "ARCH-UCMM/UM-04": Facet.SEMANTIC_IDENTITY,  # Universal Meaning
    "ARCH-UCMM/UM-05": Facet.CONSTRAINTS,  # Universal Constraints
    "ARCH-UCMM/UM-06": Facet.POLICIES,  # Universal Rules
    "ARCH-UCMM/UM-07": Facet.KNOWLEDGE_CONTEXT,  # Universal Knowledge
    "ARCH-UCMM/UM-16": Facet.TEMPORAL_HISTORY,  # Universal Event
    "ARCH-UCMM/UM-17": Facet.LIFECYCLE,  # Universal Lifecycle
    "ARCH-UCMM/UM-18": Facet.EVOLUTION_HISTORY,  # Universal Evolution
    "ARCH-UCMM/UM-19": Facet.GOVERNANCE_CONTEXT,  # Universal Governance
    "ARCH-UCMM/UM-20": Facet.AUTHORITY,  # Universal Authority
    "ARCH-UCMM/UM-21": Facet.OWNERSHIP,  # Universal Ownership
    "ARCH-UCMM/UM-22": Facet.SECURITY_CONTEXT,  # Universal Security
    "ARCH-UCMM/UM-27": Facet.RUNTIME_BINDINGS,  # Universal Runtime
    "ARCH-UCMM/UM-30": Facet.PROJECTION_BINDINGS,  # Universal Projection
}

#: Carried by a module the substrate has, not by a question every object answers.
META_MODEL_MODULE = {
    "ARCH-UCMM/UM-09": "engine/uckp/vocabulary.py",  # Universal Semantics
    "ARCH-UCMM/UM-12": "platform/universal_measurement",  # Universal Measurement
    "ARCH-UCMM/UM-13": "engine/uckp/capabilities.py",  # Universal Capability
    "ARCH-UCMM/UM-15": "engine/uckp/state.py",  # Universal State
    "ARCH-UCMM/UM-24": "platform/foundation/trust.py",  # Universal Trust
    "ARCH-UCMM/UM-26": "platform/commercial_intelligence",  # Universal Commerce
    "ARCH-UCMM/UM-28": "engine/uckp/intelligence.py",  # Universal Intelligence
}

#: Named by neither. Seven of thirty, and the set is worth reading whole: the meta-model
#: mandates Logic and Mathematics as first-class universals and the substrate has neither,
#: which means nothing in it can state a rule formally or measure a quantity dimensionally.
#: Information, Behaviour, Privacy and Economics repeat the gaps QM-CONST records under
#: other names -- the same holes seen from a second document.
META_MODEL_ABSENT = {
    "ARCH-UCMM/UM-08": "information",  # Universal Information
    "ARCH-UCMM/UM-10": "logic",  # Universal Logic
    "ARCH-UCMM/UM-11": "mathematics",  # Universal Mathematics
    "ARCH-UCMM/UM-14": "behaviour",  # Universal Behaviour
    "ARCH-UCMM/UM-23": "privacy",  # Universal Privacy
    "ARCH-UCMM/UM-25": "economics",  # Universal Economics
    "ARCH-UCMM/UM-29": "automation",  # Universal Automation
}


def test_every_meta_model_concept_is_a_facet_a_module_or_absent() -> None:
    mandates = section("ARCH-UCMM")
    assert len(mandates) == 30, f"the UCMM lists 30 universals, corpus has {len(mandates)}"
    assert_partitions(
        "ARCH-UCMM",
        mandates,
        META_MODEL_FACET,
        META_MODEL_MODULE,
        META_MODEL_ABSENT,
    )


def test_each_facet_backed_universal_is_required_and_carried_by_the_object() -> None:
    import dataclasses

    from engine.uckp.ucko import UniversalConstitutionalKnowledgeObject as UCKO

    fields = {f.name for f in dataclasses.fields(UCKO)}
    for mandate, facet in META_MODEL_FACET.items():
        assert facet in REQUIRED_FACETS, f"{mandate}: {facet} is not a required facet"
        assert facet.attribute in fields, (
            f"{mandate}: facet {facet.value!r} is declared but no UCKO field carries it, so "
            "the meta-model concept is not in fact universal over objects"
        )


def test_the_facet_mapping_is_injective() -> None:
    """NON-VACUITY. Meaning and Semantics are listed as separate universals; answering both
    with SEMANTIC_IDENTITY would report two concepts covered by one answer."""
    facets = list(META_MODEL_FACET.values())
    duplicated = sorted({f.value for f in facets if facets.count(f) > 1})
    assert not duplicated, f"facets claimed by more than one universal: {duplicated}"


def test_every_module_backed_universal_is_tracked_and_is_not_a_facet() -> None:
    """The tier boundary, asserted. A concept in the module tier that a facet also answers
    would be understated, and one in the facet tier without a field would be overstated."""
    assert_homes_exist("ARCH-UCMM", META_MODEL_MODULE)
    mandates = section("ARCH-UCMM")
    facet_names = {facet.value.replace("-", " ") for facet in Facet}
    for mandate in META_MODEL_MODULE:
        concept = mandates[mandate].removeprefix("Universal ").lower()
        assert concept not in facet_names, (
            f"{mandate}: {concept!r} is answered by a facet after all and is understated "
            "as a module"
        )


def test_the_absent_universals_are_named_by_no_module_and_no_facet() -> None:
    """NON-VACUITY in both directions. Either check alone would let a real answer read as
    missing -- a facet with no module, or a module with no facet."""
    facet_names = {facet.value.replace("-", "") for facet in Facet}
    for mandate, concept in META_MODEL_ABSENT.items():
        assert (
            concept not in facet_names
        ), f"{mandate}: {concept!r} is declared absent but a facet is named for it"
    assert_named_by_nothing("ARCH-UCMM", META_MODEL_ABSENT)


def test_the_meta_model_gaps_agree_with_the_interrogative_model() -> None:
    """Two documents, one repository.

    The UCMM and the interrogative model each mandate Information, Behaviour, Privacy and
    Economics, and each suite located them independently. If the two ever disagree, one has
    mis-located something -- which is a finding about the suites, not about the repository,
    and worth catching before it is read as a change in coverage. Behaviour is compared on
    its stem because the documents spell it differently.
    """
    from engine.tests.conformance.test_mandates_model import CONSTITUTION_ABSENT

    def stems(values):
        return {v.replace("behaviour", "behavio").replace("behavior", "behavio") for v in values}

    shared = {"information", "behavio", "privacy", "economics"}
    here, there = stems(META_MODEL_ABSENT.values()), stems(CONSTITUTION_ABSENT.values())

    assert shared <= here, f"the UCMM suite no longer reports absent: {sorted(shared - here)}"
    assert shared <= there, f"QM-CONST no longer reports absent: {sorted(shared - there)}"


# --- ARCH-VALID — the twenty-one validations ------------------------------------
#
# The Quality & Trust Fabric lists twenty-one validations and opens the section with an
# instruction rather than a description: "Automatically discover every constitutionally
# applicable activity." Thirteen have an instrument. Eight do not, and six of those eight
# are the non-functional axes -- Privacy, Risk, Performance, Reliability, Scalability,
# Interoperability. That is the shape of the gap and it is worth stating as one: the
# repository validates what it IS thoroughly and validates how it BEHAVES not at all.

#: Validation -> the instrument that performs it.
VALIDATION_INSTRUMENT = {
    "ARCH-VALID/VL-01": "scripts/ucos-env.sh",  # Static Analysis -- the ruff gate
    "ARCH-VALID/VL-02": "verify.sh",  # Dynamic Analysis -- the suite under the floor
    # Semantic Analysis
    "ARCH-VALID/VL-03": "00-MASTER/UAKOS-CLOSURE-008/02-SEMANTIC-EQUIVALENCE-REGISTER.md",
    "ARCH-VALID/VL-04": "00-MASTER/UAIE-000001/uaie.json",  # Architecture Validation
    "ARCH-VALID/VL-05": "engine/uckp/validation.py",  # Constitutional Validation
    # Requirement Validation
    "ARCH-VALID/VL-06": "00-MASTER/UAKOS-CLOSURE-009/requirement_engine.py",
    "ARCH-VALID/VL-07": "engine/validation/checks.py",  # Dependency Validation
    "ARCH-VALID/VL-08": "engine/foundation/config",  # Configuration Validation
    "ARCH-VALID/VL-09": "engine/validation/checks.py",  # Identity Validation
    "ARCH-VALID/VL-10": "engine/graph/validation.py",  # Relationship Validation
    "ARCH-VALID/VL-11": "engine/kernel/governance.py",  # Policy Validation
    "ARCH-VALID/VL-12": "engine/kernel/compliance.py",  # Compliance Validation
    "ARCH-VALID/VL-13": "engine/validation/checks.py",  # Security Validation
    "ARCH-VALID/VL-15": "engine/constitution/legality.py",  # Legal Validation
    "ARCH-VALID/VL-20": "platform/validation_intelligence/compatibility.py",  # Compatibility
}

#: Performed by nothing. Six of the seven are behavioural axes, which is the finding.
VALIDATION_ABSENT = {
    "ARCH-VALID/VL-14": "privacy",
    "ARCH-VALID/VL-16": "risk",
    "ARCH-VALID/VL-17": "performance",
    "ARCH-VALID/VL-18": "reliability",
    "ARCH-VALID/VL-19": "scalability",
    "ARCH-VALID/VL-21": "interoperability",
}


def test_every_mandated_validation_is_performed_or_absent() -> None:
    mandates = section("ARCH-VALID")
    assert len(mandates) == 21, f"the fabric lists 21 validations, corpus has {len(mandates)}"
    assert_partitions("ARCH-VALID", mandates, VALIDATION_INSTRUMENT, VALIDATION_ABSENT)


def test_every_performing_instrument_is_tracked_and_executable_or_declared_data() -> None:
    """A validation carried by a register is a record of one having been done; a validation
    carried by code is one that can be done again. Both count, and the difference is
    recorded rather than flattened."""
    assert_homes_exist("ARCH-VALID", VALIDATION_INSTRUMENT)
    executable = [home for home in VALIDATION_INSTRUMENT.values() if home.endswith((".py", ".sh"))]
    assert len(executable) >= 10, (
        f"only {len(executable)} of the located validations are executable; the rest are "
        "records of a validation having happened once"
    )


def test_the_three_checks_module_validations_name_distinct_checks() -> None:
    """NON-VACUITY for the one home claimed three times. Dependency, Identity and Security
    all resolve to `engine/validation/checks.py`, which is only honest if that module
    carries three different checks."""
    from engine.validation.checks import default_checks

    names = {type(check).__name__ for check in default_checks()}
    for expected in ("DependencyClosureCheck", "IdentityCheck", "SignatureCheck"):
        assert expected in names, (
            f"{expected} is not among the default checks {sorted(names)}; one of the three "
            "validations mapped to that module is not actually performed"
        )


def test_the_absent_validations_are_performed_by_nothing() -> None:
    """NON-VACUITY. `engine/constitution/legality.py` is why this is searched rather than
    assumed: Legal Validation reads as an obvious gap and the repository has one."""
    assert_named_by_nothing("ARCH-VALID", VALIDATION_ABSENT)


def test_the_gap_is_behavioural_rather_than_scattered() -> None:
    """The finding, asserted so it cannot quietly stop being true.

    Six of the seven absent validations are non-functional axes. If a performance or
    scalability validator ever lands, this assertion fails and the characterisation above
    has to be rewritten rather than left standing as stale narrative.
    """
    behavioural = {"performance", "reliability", "scalability", "interoperability", "risk"}
    assert behavioural <= set(VALIDATION_ABSENT.values()), (
        "a behavioural validator now exists; the claim that this repository validates what "
        "it is and not how it behaves no longer holds"
    )


# --- ARCH-TEST — the fourteen kinds of testing ----------------------------------
#
# Fourteen testing kinds under Universal Testing. Five have a suite named for them, two are
# not suites at all but MODES of the repository-standard command, and seven have nothing.
#
# The seven divide in a way that matters. Component and End-to-End are testing this
# repository could do and does not. Performance, Chaos, Billing and Analytics are testing it
# could not do if it wanted to: there is no billing to test, no analytics to test, and
# ARCH-VALID already records that nothing validates performance either. A missing test for
# a missing capability is one gap, not two, and this suite asserts the pairing so it is read
# as one.

#: Testing kind -> the suite named for it.
TESTING_SUITE = {
    "ARCH-TEST/TS-01": "engine/tests/unit",  # Unit Testing
    "ARCH-TEST/TS-03": "engine/tests/integration",  # Integration Testing
    "ARCH-TEST/TS-08": "application/tests/test_security.py",  # Security Testing
    "ARCH-TEST/TS-10": "engine/tests/unit/test_execution_recovery.py",  # Recovery Testing
    "ARCH-TEST/TS-14": "engine/tests/integration/test_runtime.py",  # Runtime Testing
}

#: Testing kind -> the verify.sh mode that performs it. Not a suite: a claim about WHICH
#: tests run and under what floor, which is what distinguishes system and regression testing
#: from the suites they are made of.
TESTING_MODE = {
    "ARCH-TEST/TS-04": "--integration",  # System Testing -- whole suite under the floor
    "ARCH-TEST/TS-06": "--full",  # Regression Testing -- release certification, what CI runs
}

#: Testing this repository could do and does not.
TESTING_ABSENT_CAPABLE = {
    "ARCH-TEST/TS-02": "component",
    "ARCH-TEST/TS-05": "end to end",
}

#: Testing with nothing to test. Each names the capability whose absence makes it moot.
TESTING_ABSENT_NO_SUBJECT = {
    "ARCH-TEST/TS-07": "performance",  # ARCH-VALID/VL-17 -- nothing validates it either
    "ARCH-TEST/TS-09": "chaos",  # no fault-injection surface exists
    "ARCH-TEST/TS-11": "billing",  # PRD-ECON/ECON-03 -- there is no billing
    "ARCH-TEST/TS-12": "licensing",  # licensing exists; no test names it
    "ARCH-TEST/TS-13": "analytics",  # MI-002/C-25 -- analytics is unconstituted
}


def test_every_testing_kind_has_a_suite_a_mode_or_neither() -> None:
    mandates = section("ARCH-TEST")
    assert len(mandates) == 14, f"the fabric lists 14 testing kinds, corpus has {len(mandates)}"
    assert_partitions(
        "ARCH-TEST",
        mandates,
        TESTING_SUITE,
        TESTING_MODE,
        TESTING_ABSENT_CAPABLE,
        TESTING_ABSENT_NO_SUBJECT,
    )


def test_every_named_suite_is_a_tracked_test_path() -> None:
    from engine.tests.conformance.mandate_corpus import tracked

    known = set(tracked())
    for mandate, home in TESTING_SUITE.items():
        present = home in known or any(p.startswith(home.rstrip("/") + "/") for p in known)
        assert present, f"{mandate}: {home} is not a tracked path"
        assert "test" in home, f"{mandate}: {home} is not a test path"


def test_every_named_mode_is_a_mode_verify_sh_accepts() -> None:
    """A mode the entry point does not accept is a claim nobody can run."""
    from engine.tests.conformance.mandate_corpus import repo_root

    verify = (repo_root() / "verify.sh").read_text(encoding="utf-8")
    for mandate, mode in TESTING_MODE.items():
        assert f"{mode})" in verify, (
            f"{mandate}: verify.sh accepts no {mode} argument, so this testing kind names a "
            "command that cannot be run"
        )


def test_the_absent_kinds_have_no_suite_named_for_them() -> None:
    """NON-VACUITY over the TEST paths specifically. Searching the whole tree would match
    `platform/commercial_intelligence/licensing.py` and report licensing testing that does
    not exist -- the capability is there and the test for it is not."""
    from engine.tests.conformance.mandate_corpus import _path_tokens, tracked

    test_paths = [p for p in tracked() if "/tests/" in p or "/test_" in p]
    assert test_paths, "no test paths are tracked, so this search is vacuous"
    for mandate, kind in {**TESTING_ABSENT_CAPABLE, **TESTING_ABSENT_NO_SUBJECT}.items():
        words = {w.rstrip("s") for w in kind.split()}
        found = [p for p in test_paths if words <= _path_tokens(p)]
        assert not found, f"{mandate}: {kind!r} is declared untested but {found} tests it"


def test_a_missing_test_for_a_missing_capability_is_one_gap_and_not_two() -> None:
    """The pairing, asserted across suites. Billing testing is absent because billing is
    absent, and performance testing because nothing validates performance either. If either
    capability lands, its test moves to the tier of things this repository could do and does
    not -- which is a different obligation."""
    from engine.tests.conformance.test_mandates_prd import ECONOMIC_FACULTY_ABSENT

    assert "billing" in set(
        ECONOMIC_FACULTY_ABSENT.values()
    ), "billing now exists, so ARCH-TEST/TS-11 is a missing test rather than a moot one"
    assert "performance" in set(
        VALIDATION_ABSENT.values()
    ), "performance validation now exists, so ARCH-TEST/TS-07 is a missing test"


# --- ARCH-GOVF — the eighteen steps of the Universal Governance Fabric -----------
#
# Eighteen steps from Approval to Go-Live Authorization. This is a PIPELINE, and this
# repository already declares one: UCL-000001's forty-five lifecycle stages include eight of
# these eighteen under their own names, word for word. So the join is made against the
# lifecycle rather than against modules, and `_ucl_stage_names` is imported from the QM-FLOW
# binding rather than rewritten -- one reader of `ucl.json`, not two.
#
# Nine more steps are performed by an instrument the lifecycle does not name as a stage. The
# eighteenth is the interesting one: Go-Live Authorization exists as a DETERMINATION that a
# go-live was accepted, which is a record after the fact and not an authorization gate in a
# pipeline. Counting it as the step would report an authority the repository does not have.

#: Governance step -> the UCL-000001 stage that performs it, by that stage's own name.
GOVERNANCE_LIFECYCLE_STAGE = {
    "ARCH-GOVF/GF-02": "Certify",  # Certification
    "ARCH-GOVF/GF-03": "Register",  # Registration
    # Universal Identity Assignment
    "ARCH-GOVF/GF-04": "Assign Universal Constitutional Identifier",
    # Dictionary Update
    "ARCH-GOVF/GF-05": "Update Universal Constitutional Identifier Dictionary",
    "ARCH-GOVF/GF-08": "Update Universal Registry",  # Registry Update
    "ARCH-GOVF/GF-13": "Update Universal Bookkeeping",  # Bookkeeping Update
    "ARCH-GOVF/GF-14": "Update Universal Lineage",  # Lineage Update
    "ARCH-GOVF/GF-16": "Update Repository Truth",  # Repository Truth Update
}

#: Governance step -> the instrument that performs it outside the declared lifecycle.
GOVERNANCE_INSTRUMENT = {
    "ARCH-GOVF/GF-01": "00-BOOK/DATA/allocation-permits.json",  # Approval
    "ARCH-GOVF/GF-06": "engine/context/ontology.py",  # Ontology Update
    "ARCH-GOVF/GF-07": "engine/context/taxonomy.py",  # Taxonomy Update
    "ARCH-GOVF/GF-09": "00-BOOK/DATA/relationships.json",  # Relationship Update
    "ARCH-GOVF/GF-10": "00-BOOK/DATA/relationships.json",  # Dependency Update -- Depends-On edges
    "ARCH-GOVF/GF-11": "intelligence/UCOS-RIE-CAPABILITY-CATALOG.json",  # Capability Update
    "ARCH-GOVF/GF-12": "00-BOOK/DATA/evidence-universe.json",  # Evidence Registration
    # Provenance Update. `provenance.json` is the richer answer and is NOT tracked -- it is
    # a generated input, re-derived by its producer and absent from a pristine clone. A step
    # of the governance fabric has to be carried by something Repository Truth holds.
    "ARCH-GOVF/GF-15": "00-MASTER/UAKOS-PHASE-001B/01-SOURCE-PROVENANCE-REGISTER.md",
    # Production Readiness
    "ARCH-GOVF/GF-17": "00-MASTER/UAKOS-CLOSURE-009/06-REPOSITORY-READINESS-MATRIX.md",
}

#: Recorded after the fact rather than performed as a step.
GOVERNANCE_DETERMINATION_ONLY = {
    "ARCH-GOVF/GF-18": "02-MASTER/UCOS-GO-LIVE-001-GO-LIVE-ACCEPTANCE-DETERMINATION.md",
}


def test_every_governance_step_is_a_stage_an_instrument_or_a_determination() -> None:
    mandates = section("ARCH-GOVF")
    assert len(mandates) == 18, f"the fabric lists 18 steps, corpus has {len(mandates)}"
    assert_partitions(
        "ARCH-GOVF",
        mandates,
        GOVERNANCE_LIFECYCLE_STAGE,
        GOVERNANCE_INSTRUMENT,
        GOVERNANCE_DETERMINATION_ONLY,
    )


def test_every_stage_backed_step_names_a_stage_ucl_declares() -> None:
    from engine.tests.conformance.test_mandates_model import _ucl_stage_names

    declared = _ucl_stage_names()
    for mandate, stage in GOVERNANCE_LIFECYCLE_STAGE.items():
        assert (
            stage in declared
        ), f"{mandate}: UCL-000001 declares no stage named {stage!r}; this join is stale"
    claimed = list(GOVERNANCE_LIFECYCLE_STAGE.values())
    assert len(claimed) == len(set(claimed)), "one lifecycle stage claimed by two steps"


def test_every_instrument_backed_step_is_tracked_and_is_not_a_declared_stage() -> None:
    """The tier boundary. A step UCL declares belongs in the lifecycle tier."""
    from engine.tests.conformance.test_mandates_model import _ucl_stage_names

    assert_homes_exist("ARCH-GOVF", GOVERNANCE_INSTRUMENT)
    declared = {name.lower() for name in _ucl_stage_names()}
    mandates = section("ARCH-GOVF")
    for mandate in GOVERNANCE_INSTRUMENT:
        assert (
            mandates[mandate].lower() not in declared
        ), f"{mandate}: {mandates[mandate]!r} IS a declared stage and is understated"


def test_relationship_and_dependency_share_one_register_because_a_dependency_is_an_edge() -> None:
    """NON-VACUITY for the only home claimed twice. Article 7 says it outright -- "every
    dependency an edge" -- so one relationship register carrying both is the law's own
    shape, not a shortcut. Any OTHER doubled home would be."""
    from engine.uckp.law import ROOT_LAW

    homes = list(GOVERNANCE_INSTRUMENT.values())
    doubled = sorted({h for h in homes if homes.count(h) > 1})
    assert doubled == ["00-BOOK/DATA/relationships.json"], f"unexpected doubled homes: {doubled}"
    article = next(a for a in ROOT_LAW.articles if a.article_id == "UCKP-ART-07")
    assert "every dependency an edge" in article.clause, (
        "Article 7 no longer makes a dependency an edge, so one register carrying both is "
        "no longer the law's shape"
    )


def test_go_live_is_a_determination_and_not_an_authorization_gate() -> None:
    """NON-VACUITY for the last step, and the distinction it rests on.

    A determination records that a go-live was accepted. An authorization step refuses one
    that is not. If a gate ever appears, this row moves and the fabric gains its final step;
    until then, counting the determination as the step would report an authority nothing has.
    """
    from engine.tests.conformance.mandate_corpus import tracked

    assert_homes_exist("ARCH-GOVF", GOVERNANCE_DETERMINATION_ONLY)
    gates = [
        path
        for path in tracked()
        if path.endswith((".py", ".sh"))
        and "golive" in path.lower().replace("-", "").replace("_", "")
    ]
    assert not gates, f"a go-live gate now exists: {gates}; ARCH-GOVF/GF-18 must be re-tiered"


# --- ARCH-EVOF — the seventeen steps of the Universal Evolution Fabric -----------
#
# Nine of the seventeen are UCL lifecycle stages, two are carried by Layer Zero, and six are
# absent. The six do not divide by accident.
#
# TWO ARE REFUSED BY LAW, not missing. Article 14 says evolution "appends; it never
# rewrites", and the lifecycle vocabulary implements that as a successor graph with no
# backward edge: `archived` reaches only `historical`, and `historical` reaches nothing. So
# Downgrade and Restore are not gaps -- they are operations this constitution forbids, and
# building them would breach the article that mandates the fabric they appear in.
#
# FOUR ARE GENUINELY ABSENT: Optimization, Upgrade, Migration and Transformation.

EVOLUTION_LIFECYCLE_STAGE = {
    "ARCH-EVOF/VF2-01": "Extract Engineering Knowledge",  # Knowledge Extraction
    "ARCH-EVOF/VF2-02": "Learn",  # Learning
    "ARCH-EVOF/VF2-03": "Reason",  # Reasoning
    "ARCH-EVOF/VF2-04": "Improve",  # Improvement
    "ARCH-EVOF/VF2-13": "Replay",  # Replay
    "ARCH-EVOF/VF2-14": "Deterministic Fixed Point",  # Deterministic Fixed Point
    "ARCH-EVOF/VF2-15": "Elevate",  # Capability Elevation
    "ARCH-EVOF/VF2-16": "Register Engineering Knowledge",  # Engineering Knowledge Registration
    "ARCH-EVOF/VF2-17": "Observe",  # Repository Observation
}

EVOLUTION_INSTRUMENT = {
    "ARCH-EVOF/VF2-06": "engine/uckp/evolution.py",  # Versioning -- the state chain
    "ARCH-EVOF/VF2-11": "engine/uckp/vocabulary.py",  # Archive -- the `archived` stage
}

#: Refused by Article 14, not missing. Each names the transition the lifecycle will not make.
EVOLUTION_REFUSED_BY_LAW = {
    "ARCH-EVOF/VF2-08": ("archived", "ratified"),  # Downgrade
    "ARCH-EVOF/VF2-12": ("archived", "operational"),  # Restore
}

#: A module carries the word and does something else with it. Both would pass a keyword
#: sweep and neither is an evolution step.
EVOLUTION_NEAR_MISS = {
    "ARCH-EVOF/VF2-05": (
        "engine/compiler/optimization.py",
        "the compiler optimises the output it emits, not the substrate that emits it -- the "
        "same near miss PRD-SELF/SELF-11 records for Self Optimizing",
    ),
    "ARCH-EVOF/VF2-10": (
        "engine/omega_governance/reference/transformation.py",
        "a reference transformation maps one representation to another; it does not evolve "
        "the thing represented",
    ),
}

EVOLUTION_ABSENT = {
    "ARCH-EVOF/VF2-07": "upgrade",
    "ARCH-EVOF/VF2-09": "migration",
}


def test_every_evolution_step_is_a_stage_an_instrument_refused_or_absent() -> None:
    mandates = section("ARCH-EVOF")
    assert len(mandates) == 17, f"the fabric lists 17 steps, corpus has {len(mandates)}"
    assert_partitions(
        "ARCH-EVOF",
        mandates,
        EVOLUTION_LIFECYCLE_STAGE,
        EVOLUTION_INSTRUMENT,
        EVOLUTION_REFUSED_BY_LAW,
        EVOLUTION_NEAR_MISS,
        EVOLUTION_ABSENT,
    )


def test_every_evolution_stage_names_a_stage_ucl_declares() -> None:
    from engine.tests.conformance.test_mandates_model import _ucl_stage_names

    declared = _ucl_stage_names()
    for mandate, stage in EVOLUTION_LIFECYCLE_STAGE.items():
        assert stage in declared, f"{mandate}: UCL declares no stage named {stage!r}"
    claimed = list(EVOLUTION_LIFECYCLE_STAGE.values())
    assert len(claimed) == len(set(claimed)), "one stage claimed by two evolution steps"


def test_the_refused_steps_name_a_transition_the_lifecycle_will_not_make() -> None:
    """The claim is that these two are forbidden, not missing -- so the refusal is executed.

    Each row names a transition; the vocabulary must refuse it. If a backward edge is ever
    added, Downgrade and Restore become buildable and this tier is wrong.
    """
    from engine.uckp.vocabulary import DEFAULT_VOCABULARIES, LIFECYCLE_STAGE

    vocabulary = DEFAULT_VOCABULARIES.require(LIFECYCLE_STAGE)
    for mandate, (source, target) in EVOLUTION_REFUSED_BY_LAW.items():
        assert vocabulary.has(source) and vocabulary.has(target)
        assert not vocabulary.can_transition(source, target), (
            f"{mandate}: the lifecycle now admits {source!r} -> {target!r}, so this step is "
            "buildable and is no longer refused by law"
        )


def test_article_fourteen_still_forbids_rewriting() -> None:
    """NON-VACUITY for the refused tier. The transitions above are the mechanism; this is
    the law they implement, read rather than cited."""
    from engine.uckp.law import ROOT_LAW

    article = next(a for a in ROOT_LAW.articles if a.article_id == "UCKP-ART-14")
    assert "it never rewrites" in article.clause, (
        "Article 14 no longer forbids rewriting; Downgrade and Restore may be buildable and "
        "must be re-tiered rather than left declared refused"
    )
    # Each refusal must be a BACKWARD edge, or it is not evidence of append-only: a
    # forward transition the lifecycle happens not to declare would refuse for a different
    # reason entirely.
    from engine.uckp.vocabulary import DEFAULT_VOCABULARIES, LIFECYCLE_STAGE

    vocabulary = DEFAULT_VOCABULARIES.require(LIFECYCLE_STAGE)
    for mandate, (source, target) in EVOLUTION_REFUSED_BY_LAW.items():
        assert vocabulary.can_transition(target, "deprecated") or target == "ratified", (
            f"{mandate}: {target!r} is not an earlier lifecycle state than {source!r}, so "
            "refusing the transition is not evidence that evolution never rewrites"
        )


def test_the_near_misses_are_near_and_are_misses() -> None:
    """Both directions. The named module must exist, or the explanation is decoration; and
    the reason has to be stated, because "a module carries the word" is the finding this
    tier exists to refuse.

    Optimization is the same near miss PRD-SELF records for Self Optimizing, so the two are
    asserted to agree -- one module, two mandates, one reason.
    """
    from engine.tests.conformance.test_mandates_prd import SELF_NEAR_MISS

    assert_homes_exist("ARCH-EVOF", {m: home for m, (home, _w) in EVOLUTION_NEAR_MISS.items()})
    for mandate, (_home, why) in EVOLUTION_NEAR_MISS.items():
        assert len(why) > 40, f"{mandate}: tiered a near miss without a stated reason"

    optimiser = EVOLUTION_NEAR_MISS["ARCH-EVOF/VF2-05"][0]
    assert SELF_NEAR_MISS["PRD-SELF/SELF-11"][0] == optimiser, (
        "the two sections no longer name the same module for Optimization; one of the two "
        "near misses has been re-located and the pair must be re-read"
    )


def test_the_absent_steps_are_performed_by_nothing() -> None:
    """NON-VACUITY over the two with no module at all. Upgrade and Migration are the only
    evolution steps nothing in the tree is even named for."""
    assert_named_by_nothing("ARCH-EVOF", EVOLUTION_ABSENT)


# --- ARCH-OPF — the eighteen steps of the Universal Operation Fabric -------------
#
# Deployment through Commercialization. Twelve are located, and the six that are not divide
# into two kinds worth keeping apart.
#
# THREE HAVE NOTHING TO OPERATE ON. Billing and Metering are moot in a substrate with no
# settlement chain -- PRD-ECON records Revenue, Billing, Settlement and Taxation all absent
# -- and Fraud Monitoring is moot without transactions to monitor. THREE ARE GENUINELY
# UNBUILT: Provisioning, Security Monitoring and Tracing. `platform/observability/traces.py`
# exists and stores traces; nothing traces.

OPERATION_INSTRUMENT = {
    "ARCH-OPF/OF-01": "intelligence/realization/generators/deployment.py",  # Deployment
    "ARCH-OPF/OF-03": "00-MASTER/UIS-001/uis-declaration.json",  # Activation
    "ARCH-OPF/OF-04": "engine/uckp/execution.py",  # Execution
    "ARCH-OPF/OF-05": "engine/runtime",  # Runtime
    "ARCH-OPF/OF-06": "engine/uicm/observation.py",  # Observation
    "ARCH-OPF/OF-07": "platform/observability/metrics.py",  # Monitoring
    "ARCH-OPF/OF-08": "engine/foundation/obs/telemetry.py",  # Telemetry
    "ARCH-OPF/OF-09": "engine/foundation/obs/logging.py",  # Logging
    "ARCH-OPF/OF-11": "intelligence/rie/analysis.py",  # Analytics
    "ARCH-OPF/OF-14": "engine/kernel/compliance.py",  # Compliance Monitoring
    "ARCH-OPF/OF-17": "platform/commercial_intelligence/licensing.py",  # Licensing
    "ARCH-OPF/OF-18": "platform/commercial_intelligence",  # Commercialization
}

#: Nothing to operate on. Each names the capability whose absence makes the step moot.
OPERATION_NO_SUBJECT = {
    "ARCH-OPF/OF-13": "fraud",  # no transactions to monitor
    "ARCH-OPF/OF-15": "billing",  # PRD-ECON/ECON-03 -- no billing exists
    "ARCH-OPF/OF-16": "metering",  # nothing is metered because nothing is billed
}

#: Genuinely unbuilt, with something to operate on if they existed.
OPERATION_UNBUILT = {
    "ARCH-OPF/OF-02": "provisioning",
    "ARCH-OPF/OF-10": "tracing",
    "ARCH-OPF/OF-12": "security monitoring",
}


def test_every_operation_step_is_instrumented_moot_or_unbuilt() -> None:
    mandates = section("ARCH-OPF")
    assert len(mandates) == 18, f"the fabric lists 18 steps, corpus has {len(mandates)}"
    assert_partitions(
        "ARCH-OPF",
        mandates,
        OPERATION_INSTRUMENT,
        OPERATION_NO_SUBJECT,
        OPERATION_UNBUILT,
    )


def test_every_operating_instrument_is_tracked_and_distinct() -> None:
    assert_homes_exist("ARCH-OPF", OPERATION_INSTRUMENT)
    homes = list(OPERATION_INSTRUMENT.values())
    duplicated = sorted({h for h in homes if homes.count(h) > 1})
    assert not duplicated, f"one instrument claimed for several operation steps: {duplicated}"


def test_the_moot_steps_are_moot_because_their_subject_is_absent() -> None:
    """The pairing, asserted across suites. Billing operation is absent because billing is
    absent -- one gap, not two. If the settlement chain ever lands, these move to the
    unbuilt tier, which is a different obligation."""
    from engine.tests.conformance.test_mandates_prd import ECONOMIC_FACULTY_ABSENT

    absent_faculties = set(ECONOMIC_FACULTY_ABSENT.values())
    assert (
        "billing" in absent_faculties
    ), "billing now exists, so ARCH-OPF/OF-15 is an unbuilt step rather than a moot one"
    assert {"revenue", "settlement"} <= absent_faculties, (
        "the settlement chain has partially landed; the fraud and metering rows rest on its "
        "absence and must be re-read"
    )


def test_tracing_is_unbuilt_even_though_traces_are_stored() -> None:
    """NON-VACUITY, and the distinction that keeps Tracing out of the located tier.

    `platform/observability/traces.py` exists and would satisfy a keyword sweep. Storing a
    trace is not producing one: the telemetry module has the `trace` context manager that
    emits spans, and it is bound to Telemetry, not to Tracing. Nothing correlates spans
    across a request, which is what the fabric's Tracing step means.
    """
    from engine.tests.conformance.mandate_corpus import repo_root, tracked

    assert "platform/observability/traces.py" in set(tracked())
    telemetry = (repo_root() / "engine" / "foundation" / "obs" / "telemetry.py").read_text(
        encoding="utf-8"
    )
    assert (
        "def trace(" in telemetry
    ), "the telemetry module no longer emits spans; the Telemetry row rests on it"
    assert OPERATION_INSTRUMENT["ARCH-OPF/OF-08"].endswith("telemetry.py")
    assert "ARCH-OPF/OF-10" in OPERATION_UNBUILT


def test_the_unbuilt_steps_are_named_by_no_module() -> None:
    """NON-VACUITY over the two with no near-miss. Provisioning and Security Monitoring have
    nothing in the tree named for them at all."""
    assert_named_by_nothing(
        "ARCH-OPF",
        {
            "ARCH-OPF/OF-02": "provisioning",
            "ARCH-OPF/OF-12": "security monitoring",
        },
    )


# --- ARCH-DISCF — the twelve steps of the Universal Discovery Fabric -------------
#
# Six of the twelve are UCL-000001 stages; six are not, and the six that are not are the
# COGNITIVE ones -- Discover, Recognize, Identify, Classify, Resolve Relationships, Resolve
# Rules. The lifecycle names the stages where something is looked up or written down, and
# not the stages where something is judged.
#
# Five of those six are still performed, by instruments the lifecycle does not stage. The
# sixth is not performed at all.

DISCOVERY_FABRIC_STAGE = {
    "ARCH-DISCF/DF-01": "Observe",  # Observe
    "ARCH-DISCF/DF-03": "Perceive",  # Recognize
    "ARCH-DISCF/DF-06": "Context Assimilation",  # Resolve Context
    "ARCH-DISCF/DF-08": "Constraint Discovery",  # Resolve Constraints
    "ARCH-DISCF/DF-10": "Dependency Discovery",  # Resolve Dependencies
    "ARCH-DISCF/DF-12": "Update Repository Truth",  # Repository Truth
}

DISCOVERY_FABRIC_INSTRUMENT = {
    "ARCH-DISCF/DF-02": "engine/universal_discovery",  # Discover
    "ARCH-DISCF/DF-04": "engine/uckp/identity.py",  # Identify
    "ARCH-DISCF/DF-05": "engine/knowledge/ukip/classification.py",  # Classify
    "ARCH-DISCF/DF-07": "engine/uckp/resolution.py",  # Resolve Relationships
    "ARCH-DISCF/DF-11": "engine/uckp/assimilation.py",  # Knowledge Assimilation
}

#: Rules are declared as policies and never RESOLVED: nothing takes a subject and returns
#: the rules that apply to it. `engine/kernel/governance.py` holds Policy and Rule as
#: objects, which is declaration, not resolution.
DISCOVERY_FABRIC_ABSENT = {"ARCH-DISCF/DF-09": "rule resolution"}


def test_every_discovery_fabric_step_is_a_stage_an_instrument_or_absent() -> None:
    mandates = section("ARCH-DISCF")
    assert len(mandates) == 12, f"the fabric lists 12 steps, corpus has {len(mandates)}"
    assert_partitions(
        "ARCH-DISCF",
        mandates,
        DISCOVERY_FABRIC_STAGE,
        DISCOVERY_FABRIC_INSTRUMENT,
        DISCOVERY_FABRIC_ABSENT,
    )


def test_every_fabric_stage_names_a_stage_ucl_declares() -> None:
    from engine.tests.conformance.test_mandates_model import _ucl_stage_names

    declared = _ucl_stage_names()
    for mandate, stage in DISCOVERY_FABRIC_STAGE.items():
        assert stage in declared, f"{mandate}: UCL declares no stage named {stage!r}"
    claimed = list(DISCOVERY_FABRIC_STAGE.values())
    assert len(claimed) == len(set(claimed)), "one stage claimed by two fabric steps"


def test_the_instrument_steps_are_the_cognitive_ones_the_lifecycle_does_not_stage() -> None:
    """The finding. The lifecycle stages what is looked up or written down; it does not stage
    judgement. If UCL ever adds a Classify or Identify stage, that step moves up a tier and
    this characterisation has to be rewritten rather than left standing."""
    from engine.tests.conformance.mandate_corpus import repo_root, tracked
    from engine.tests.conformance.test_mandates_model import _ucl_stage_names

    declared = {name.lower() for name in _ucl_stage_names()}
    mandates = section("ARCH-DISCF")
    known = set(tracked())
    for mandate, home in DISCOVERY_FABRIC_INSTRUMENT.items():
        present = home in known or any(p.startswith(home.rstrip("/") + "/") for p in known)
        assert present, f"{mandate}: {home} is not a tracked path"
        assert (
            mandates[mandate].lower() not in declared
        ), f"{mandate}: {mandates[mandate]!r} IS a declared stage now and is understated"
    assert (repo_root() / "engine" / "uckp" / "identity.py").exists()


def test_rule_resolution_is_absent_although_rules_are_declared() -> None:
    """NON-VACUITY, and the distinction that keeps it out of the located tier.

    `engine/kernel/governance.py` carries Policy and Rule as objects and would satisfy a
    keyword sweep. Declaring a rule is not resolving one: the fabric's step takes a subject
    and returns the rules that apply to it, and nothing does that.
    """
    import ast

    from engine.tests.conformance.mandate_corpus import repo_root

    source = (repo_root() / "engine" / "kernel" / "governance.py").read_text(encoding="utf-8")
    defined = {n.name for n in ast.walk(ast.parse(source)) if isinstance(n, ast.ClassDef)}
    assert "Rule" in defined or "Policy" in defined, (
        "governance.py no longer declares a Rule or Policy; the near-miss this row rests on "
        "has changed"
    )
    functions = {n.name for n in ast.walk(ast.parse(source)) if isinstance(n, ast.FunctionDef)}
    resolvers = sorted(f for f in functions if "resolve" in f and "rule" in f)
    assert (
        not resolvers
    ), f"a rule resolver now exists: {resolvers}; ARCH-DISCF/DF-09 must be re-tiered"


# --- ARCH-ASSUR — the eight assurance domains -----------------------------------
#
# Universal Assurance names eight domains. All eight are located, which makes this the
# second fully-answered section in the corpus -- and as with MI-009, "all located" is the
# claim a sweep produces by accident, so the eight must resolve to eight DISTINCT owners.
#
# Assurance is not validation: the Quality & Trust Fabric lists them as siblings. An
# assurance domain answers "is this kind of thing sound", and a validation answers "does
# this instance meet its declared shape". The two tiers below keep that apart by requiring
# each assurance owner to be an authority or a programme, never a single check.

ASSURANCE_OWNER = {
    "ARCH-ASSUR/AS-01": "engine/uckp/law.py",  # Constitutional Assurance
    "ARCH-ASSUR/AS-02": "engine/knowledge/ukip/validation.py",  # Knowledge Assurance
    # Engineering Assurance
    "ARCH-ASSUR/AS-04": "00-MASTER/UCOS-EG-001/01-ENGINEERING-GOVERNANCE-CONSTITUTION.md",
    "ARCH-ASSUR/AS-05": "platform/runtime_operations",  # Runtime Assurance
    # Security Assurance
    "ARCH-ASSUR/AS-06": "14-SECURITY/SECURITY-001-UNIVERSAL-SECURITY-CONSTITUTION.md",
    "ARCH-ASSUR/AS-07": "platform/commercial_intelligence/validation.py",  # Commercial Assurance
    "ARCH-ASSUR/AS-08": "00-MASTER/UEI-000001/uei.json",  # Evolution Assurance
}


#: Architecture is the one domain where assurance and validation resolve to the SAME
#: instrument. `UAIE-000001` derives architectural intelligence and is what ARCH-VALID/VL-04
#: names for Architecture Validation too. The fabric lists the two as siblings and this
#: repository does not distinguish them, which is a finding about the repository rather than
#: a mapping error -- recorded here instead of being papered over with a second owner chosen
#: to satisfy a tier rule.
ASSURANCE_SHARED_WITH_VALIDATION = {
    "ARCH-ASSUR/AS-03": "00-MASTER/UAIE-000001/uaie.json",  # Architecture Assurance
}


def test_every_assurance_domain_is_owned() -> None:
    mandates = section("ARCH-ASSUR")
    assert len(mandates) == 8, f"the fabric lists 8 assurance domains, corpus has {len(mandates)}"
    assert_partitions("ARCH-ASSUR", mandates, ASSURANCE_OWNER, ASSURANCE_SHARED_WITH_VALIDATION)
    assert_homes_exist("ARCH-ASSUR", ASSURANCE_OWNER)
    assert_homes_exist("ARCH-ASSUR", ASSURANCE_SHARED_WITH_VALIDATION)


def test_the_eight_domains_are_eight_distinct_owners() -> None:
    """NON-VACUITY for a fully-answered section, the same guard MI-009 needs. Eight mandates
    resolving to fewer than eight owners would make the completeness an artefact of the
    mapping rather than of the repository."""
    homes = list(ASSURANCE_OWNER.values()) + list(ASSURANCE_SHARED_WITH_VALIDATION.values())
    duplicated = sorted({h for h in homes if homes.count(h) > 1})
    assert not duplicated, f"one owner claimed for several assurance domains: {duplicated}"
    assert len(set(homes)) == 8


def test_no_assurance_owner_is_one_of_the_validations() -> None:
    """The distinction the fabric draws, asserted. Assurance and Validation are siblings in
    the diagram: assurance asks whether a KIND of thing is sound, validation whether an
    INSTANCE meets its shape. An assurance domain owned by a single validation instrument
    would collapse the two."""
    validations = set(VALIDATION_INSTRUMENT.values())
    overlap = sorted(set(ASSURANCE_OWNER.values()) & validations)
    assert not overlap, (
        f"these assurance domains are owned by a validation instrument: {overlap}; the "
        "fabric lists assurance and validation as siblings, not as one"
    )

    # The one domain that DOES share, named rather than hidden. The first draft put it in
    # the tier above and this assertion refused it, which is the tier rule working.
    shared = sorted(set(ASSURANCE_SHARED_WITH_VALIDATION.values()) & validations)
    assert shared == ["00-MASTER/UAIE-000001/uaie.json"], (
        f"the assurance/validation overlap changed: {shared}. Architecture was the only "
        "domain this repository does not separate; a new overlap needs reading, not tiering."
    )


def test_constitutional_assurance_is_the_root_law_and_nothing_smaller() -> None:
    """AS-01 is the assurance every other domain derives under, so it can only be owned by
    the supreme authority -- an assurance of the constitution owned by a subordinate
    instrument would be a subordinate checking its own superior."""
    from engine.uckp.law import ROOT_LAW

    assert ASSURANCE_OWNER["ARCH-ASSUR/AS-01"] == "engine/uckp/law.py"
    assert ROOT_LAW.law_id == "UCKP-LAW-0001"
    assert ROOT_LAW.supremacy, "the root law no longer declares supremacy"


# --- ARCH-ENGF / ARCH-VERIF / ARCH-STACK / ARCH-KERNEL / ARCH-UCG — the remainder -
#
# What is left of the architecture diagram. The engineering fabric contributes the third
# sighting of the Design gap; the verification fabric is fully answered; and three of the
# diagram's own boxes -- the stack, the kernel and the graph -- are bound to the instruments
# that are them.

ARCH_REMAINDER = {
    # ARCH-ENGF Engineering Fabric
    "ARCH-ENGF/EF-02": "00-MASTER/UAKOS-CLOSURE-009/requirement_engine.py",  # Requirements
    "ARCH-ENGF/EF-05": "00-MASTER/UCL-000001/ucl.json",  # Engineering -- the `Engineer` stage
    "ARCH-ENGF/EF-11": "engine/compiler/packaging.py",  # Packaging
    # ARCH-VERIF Universal Verification
    "ARCH-VERIF/VF-01": "engine/determinism",  # Determinism
    "ARCH-VERIF/VF-08": "engine/certification_integrity",  # Completeness
    "ARCH-VERIF/VF-10": "platform/coverage",  # Coverage
    # the diagram's own boxes
    "ARCH-KERNEL/AK-01": "engine/kernel",  # Absolute Constitutional Kernel
    "ARCH-UCG/UG-01": "engine/graph",  # Universal Constitutional Graph
}

#: The third sighting of Design, and the one stack layer nothing represents.
ARCH_REMAINDER_ABSENT = {
    "ARCH-ENGF/EF-04": "design",  # Design
    "ARCH-STACK/ST-02": "possibility",  # Possibility
}


def test_the_architecture_remainder_is_located_or_absent() -> None:
    mandates: dict[str, str] = {}
    for name in ("ARCH-ENGF", "ARCH-VERIF", "ARCH-STACK", "ARCH-KERNEL", "ARCH-UCG"):
        mandates.update(section(name))
    covered = {**ARCH_REMAINDER, **ARCH_REMAINDER_ABSENT}
    foreign = sorted(set(covered) - set(mandates))
    assert not foreign, f"tiered identifiers that are not architecture mandates: {foreign}"
    assert_homes_exist("ARCH-remainder", ARCH_REMAINDER)
    homes = list(ARCH_REMAINDER.values())
    assert len(set(homes)) == len(homes), "one instrument claimed for two remainder rows"


def test_the_kernel_box_and_the_graph_box_are_the_instruments_that_are_them() -> None:
    """The diagram's two named boxes. Each is a package rather than a document, because a
    box in an architecture diagram that resolves to prose is a box nothing implements."""
    from engine.tests.conformance.mandate_corpus import tracked

    known = set(tracked())
    for mandate in ("ARCH-KERNEL/AK-01", "ARCH-UCG/UG-01"):
        home = ARCH_REMAINDER[mandate]
        assert any(
            p.startswith(home + "/") and p.endswith(".py") for p in known
        ), f"{mandate}: {home} is not a package carrying code"


def test_design_is_absent_here_exactly_as_the_master_index_reports() -> None:
    """The third sighting, joined. Three documents mandate a design stage and nothing
    performs it; if one suite ever locates it, the others must too."""
    from engine.tests.conformance.test_mandates_index import MASTER_INDEX_ABSENT

    assert ARCH_REMAINDER_ABSENT["ARCH-ENGF/EF-04"] == "design"
    assert "design" in set(MASTER_INDEX_ABSENT.values()), (
        "the Master Index no longer reports Design absent; this suite disagrees with it and "
        "one of the two is wrong"
    )
    assert_named_by_nothing("ARCH-remainder", ARCH_REMAINDER_ABSENT)


def test_possibility_is_the_one_layer_of_the_stack_nothing_represents() -> None:
    """NON-VACUITY. The diagram's stack runs Potential, Possibility, Existence, Reality,
    Truth, Meaning. Possibility is the only one with no instrument, and MI-001 reports the
    same foundation ungrounded -- so the two are asserted together."""
    from engine.tests.conformance.test_mandates_index import FOUNDATION_UNGROUNDED

    assert "possibility" in set(FOUNDATION_UNGROUNDED.values()), (
        "MI-001 no longer reports the Possibility foundation ungrounded; the stack layer may "
        "be represented after all"
    )
