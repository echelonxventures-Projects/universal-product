"""Mandate conformance — the Self-Evolving Constitutional Substrate Architecture (Layers 0-15).

227 mandates over 23 sections. The document's eight forbidden hard-codings (LYR-NEG) are
bound in `engine/tests/kernel/test_compliance.py`, against the kernel that can decide a
negative by refusing to seed a token. Nothing here restates them.
"""

from __future__ import annotations

import pytest

from engine.tests.conformance.mandate_corpus import (
    assert_homes_exist,
    assert_named_by_nothing,
    assert_partitions,
    repo_root,
    section,
)
from engine.uckp.facets import Facet

# --- LYR-L12V / LYR-L12C — Layer 12, verification and certification --------------
#
# Layer 12 opens "No trust without proof" and then splits into two lists that are easy to
# read as one. They are not. VERIFICATION names six MEANS of establishing proof;
# CERTIFICATION names four STANDINGS an artifact can hold once proof exists. A means is an
# instrument that runs; a standing is a record something carries. Binding them into one tier
# would let six running instruments cover for four missing records, or the reverse.

#: Verification means -> the instrument that performs it.
VERIFICATION_MEANS = {
    "LYR-L12V/VF-01": "engine/certification/evidence.py",  # Evidence
    "LYR-L12V/VF-02": "engine/validation",  # Validation
    "LYR-L12V/VF-03": "verify.sh",  # Testing -- the repository-standard entry point
    "LYR-L12V/VF-04": "engine/determinism/reproduce.py",  # Replay
    "LYR-L12V/VF-05": "engine/omega_infinite/contradiction.py",  # Consistency
    "LYR-L12V/VF-06": "engine/certification_integrity",  # Integrity
}

#: Certification standing -> the record that carries it.
CERTIFICATION_STANDING = {
    "LYR-L12C/CF-01": "00-BOOK/DATA/certification.json",  # Certified State
    "LYR-L12C/CF-02": "00-BOOK/DATA/baseline-authority.json",  # Baseline
    "LYR-L12C/CF-03": "00-MASTER/RELEASE-001",  # Release
}

#: Evolution Approval is a standing nothing records. The repository HAS an evolution
#: constitution (CEP-009) and an evolution engine, and neither produces an approval an
#: artifact can carry: evolution here is measured and gated, never approved. That is a
#: coherent design and it is not what the mandate says, so it is recorded as absent.
CERTIFICATION_ABSENT = {
    "LYR-L12C/CF-04": "evolution approval",
}


def test_every_verification_means_has_an_instrument() -> None:
    mandates = section("LYR-L12V")
    assert len(mandates) == 6, f"layer 12 names 6 verification means, corpus has {len(mandates)}"
    assert_partitions("LYR-L12V", mandates, VERIFICATION_MEANS)
    assert_homes_exist("LYR-L12V", VERIFICATION_MEANS)


def test_every_verification_instrument_is_executable_rather_than_descriptive() -> None:
    """A means of proof that is a document proves nothing. Each home must be code or a
    runnable gate."""
    for mandate, home in VERIFICATION_MEANS.items():
        path = repo_root() / home
        if path.is_dir():
            assert any(path.rglob("*.py")), f"{mandate}: {home} carries no code"
        else:
            assert path.suffix in {
                ".py",
                ".sh",
            }, f"{mandate}: {home} is neither a module nor a script, so nothing runs it"


def test_the_six_means_are_six_distinct_instruments() -> None:
    """NON-VACUITY. Six means pointing at one instrument would mean five are unlocated."""
    homes = list(VERIFICATION_MEANS.values())
    duplicated = sorted({h for h in homes if homes.count(h) > 1})
    assert not duplicated, f"one instrument claimed for several means of proof: {duplicated}"


def test_every_certification_standing_is_recorded_or_declared_absent() -> None:
    mandates = section("LYR-L12C")
    assert len(mandates) == 4, f"layer 12 names 4 standings, corpus has {len(mandates)}"
    assert_partitions("LYR-L12C", mandates, CERTIFICATION_STANDING, CERTIFICATION_ABSENT)
    assert_homes_exist("LYR-L12C", CERTIFICATION_STANDING)


def test_a_standing_is_a_record_and_never_an_instrument() -> None:
    """The distinction the split rests on. A standing carried by a module would mean the
    repository can compute it on demand and never stores it, which is not a standing."""
    instruments = set(VERIFICATION_MEANS.values())
    overlap = instruments & set(CERTIFICATION_STANDING.values())
    assert not overlap, f"a verification instrument is also claimed as a standing: {overlap}"
    for mandate, home in CERTIFICATION_STANDING.items():
        path = repo_root() / home
        if not path.is_dir():
            assert path.suffix in {".json", ".md"}, (
                f"{mandate}: {home} is executable, so it computes a standing rather than "
                "recording one"
            )


def test_evolution_approval_is_recorded_by_nothing() -> None:
    """NON-VACUITY for the one absent standing, checked in both populations: no module is
    named for it, and the evolution instruments that exist do not emit an approval."""
    assert_named_by_nothing("LYR-L12C", CERTIFICATION_ABSENT)
    evolution = (repo_root() / "engine" / "constitution" / "evolution.py").read_text(
        encoding="utf-8"
    )
    assert "approval" not in evolution.lower(), (
        "the evolution engine now speaks of approval; LYR-L12C/CF-04 may be recorded after "
        "all and must be re-decided rather than left declared absent"
    )


def test_the_naming_rule_this_suite_relies_on_can_find_something() -> None:
    from engine.tests.conformance.mandate_corpus import assert_absence_rule_can_find_something

    assert_absence_rule_can_find_something("certification integrity")


# --- LYR-L2 — the fourteen context dimensions -----------------------------------
#
# Layer 2 lists fourteen context dimensions and closes the list with "Future Context Types",
# which is the instruction rather than a fourteenth dimension. UCXI-000001 owns exactly this
# question and answers it the same way: the context taxonomy is "the open classification
# tree over context kinds", and its declaration says of the kinds it recognises today that
# they "are not a closed list, and no consumer branches on a particular kind."
#
# Twelve of the thirteen real dimensions are already `ContextKind` members, by name. One is
# not, and is admissible by the declared extension mechanism -- which is the same answer,
# arrived at by the mechanism instead of by the seed.

#: Dimension -> the ContextKind value that is it.
CONTEXT_KIND_SEEDED = {
    "LYR-L2/CX-01": "spatial",
    "LYR-L2/CX-02": "temporal",
    "LYR-L2/CX-04": "environmental",
    "LYR-L2/CX-05": "cultural",
    "LYR-L2/CX-06": "linguistic",
    "LYR-L2/CX-07": "economic",
    "LYR-L2/CX-08": "governance",
    "LYR-L2/CX-09": "regulatory",
    "LYR-L2/CX-10": "identity",
    "LYR-L2/CX-11": "security",
    "LYR-L2/CX-12": "knowledge",
    "LYR-L2/CX-13": "computational",
}

#: Recognised by no seeded kind, and admissible as data. Not a gap: the declaration's own
#: extension path, exercised.
CONTEXT_KIND_BY_EXTENSION = {"LYR-L2/CX-03": "physical"}

#: The openness claim itself, which is not a dimension.
CONTEXT_OPENNESS = {"LYR-L2/CX-14": "Future Context Types"}


def test_every_context_dimension_is_a_kind_extensible_or_the_openness_claim() -> None:
    mandates = section("LYR-L2")
    assert len(mandates) == 14, f"layer 2 lists 14 dimensions, corpus has {len(mandates)}"
    assert_partitions(
        "LYR-L2",
        mandates,
        CONTEXT_KIND_SEEDED,
        CONTEXT_KIND_BY_EXTENSION,
        CONTEXT_OPENNESS,
    )


def test_every_seeded_dimension_is_a_context_kind_under_its_own_name() -> None:
    from engine.context.taxonomy import ContextKind

    kinds = {kind.value for kind in ContextKind}
    mandates = section("LYR-L2")
    for mandate, value in CONTEXT_KIND_SEEDED.items():
        assert value in kinds, f"{mandate}: {value!r} is not a recognised context kind"
        assert (
            mandates[mandate].lower().startswith(value)
        ), f"{mandate}: {mandates[mandate]!r} was mapped to {value!r}, which is not its own name"
    claimed = list(CONTEXT_KIND_SEEDED.values())
    assert len(claimed) == len(set(claimed)), "one context kind claimed by two dimensions"


def test_the_extensible_dimension_is_genuinely_not_a_seeded_kind() -> None:
    """NON-VACUITY. If `physical` is ever seeded, this row belongs a tier up and the claim
    that the taxonomy had to be extended for it is false."""
    from engine.context.taxonomy import ContextKind

    kinds = {kind.value for kind in ContextKind}
    for mandate, value in CONTEXT_KIND_BY_EXTENSION.items():
        assert value not in kinds, (
            f"{mandate}: {value!r} is now a seeded context kind and is understated as an "
            "extension"
        )


def test_the_taxonomy_declares_itself_open_and_offers_the_extension_path() -> None:
    """CX-14 is the whole point of the section, so it is checked against the declaration
    that owns the question rather than against a module that happens to allow it."""
    import json

    from engine.context.taxonomy import UNIVERSAL_TAXONOMY

    declaration = json.loads(
        (repo_root() / "00-MASTER" / "UCXI-000001" / "ucxi-declaration.json").read_text(
            encoding="utf-8"
        )
    )
    openness = declaration["openness"]
    assert (
        openness["closed_set"] is False
    ), "UCXI now declares the context kinds a closed set; LYR-L2/CX-14 is unsatisfied"
    assert openness["upper_limit"] is None
    assert "extend" in openness["extension_mechanism"]
    assert hasattr(UNIVERSAL_TAXONOMY, "extend"), (
        "the declaration names ContextTaxonomy.extend as the extension mechanism and the "
        "taxonomy does not have it"
    )


# --- LYR-L4C — the thirteen commerce capabilities -------------------------------
#
# Layer 4 opens "Everything is a capability. No fixed application modules." and then gives
# Commerce as a WORKED EXAMPLE of composition -- thirteen capabilities that compose into a
# marketplace. The example is the mandate: not that the substrate ship a Cart, but that
# thirteen capabilities of this shape compose without the substrate knowing what commerce is.
#
# Three of the thirteen settle it. `product`, `tax` and `customer` are among the eighteen
# tokens the kernel REFUSES to seed as concrete categories. A Product Capability built into
# the substrate is the fixed-industry breach P-001 and LYR-NEG/LN-05 forbid -- and all three
# compose as registered capabilities anyway, which is the distinction the layer is making.

COMMERCE_CAPABILITY_PREFIX = "Capability-"


def _capability_key(label: str) -> str:
    words = label.removesuffix(" Capability").split()
    return COMMERCE_CAPABILITY_PREFIX + "".join(word.capitalize() for word in words)


def test_the_commerce_example_is_thirteen_capabilities() -> None:
    mandates = section("LYR-L4C")
    assert len(mandates) == 13, f"the example lists 13 capabilities, corpus has {len(mandates)}"
    assert all(
        label.endswith(" Capability") for label in mandates.values()
    ), f"a row is not a capability: {sorted(mandates.values())}"


def test_every_commerce_capability_composes_with_the_kernel_unchanged() -> None:
    """The mandate as written. Composition, not construction: the kernel's source
    fingerprint is required to be identical after all thirteen are registered."""
    from engine.kernel.compliance import kernel_source_fingerprint
    from engine.provider.framework import ProviderFramework

    labels = list(section("LYR-L4C").values())
    framework = ProviderFramework()
    before = kernel_source_fingerprint()

    for label in labels:
        framework.register_category(
            _capability_key(label), name=label, description=f"composed capability: {label}"
        )

    assert kernel_source_fingerprint() == before, (
        "composing the commerce capabilities changed the kernel's source, so they were built "
        "as application modules -- which is what 'No fixed application modules' forbids"
    )
    registered = set(framework.category_keys())
    refused = sorted(label for label in labels if _capability_key(label) not in registered)
    assert not refused, f"capabilities the framework would not admit: {refused}"


def test_three_of_them_name_tokens_the_kernel_refuses_to_seed() -> None:
    """The sharp end, and the reason the example is Commerce rather than something neutral.

    Product, Tax and Customer are exactly the concrete categories a commerce platform would
    hard-code. The kernel refuses all three by name and composes all three as capabilities,
    which is the whole difference between a substrate and an eCommerce platform.
    """
    from engine.kernel.compliance import PROHIBITED_TOKENS
    from engine.kernel.seed import FOUNDING_METATYPES

    labels = {label.removesuffix(" Capability").lower() for label in section("LYR-L4C").values()}
    refused = sorted(labels & set(PROHIBITED_TOKENS))
    assert refused == ["customer", "product", "tax"], (
        f"the prohibited overlap changed: {refused}; the example no longer demonstrates what "
        "it was chosen to demonstrate"
    )
    # The intersection with the founding meta-types is NAMED rather than forbidden, for the
    # same reason it is named for the object classes: `Evolution` is a universal engineering
    # abstraction that happens to appear in a commerce list, and seeding it is not a
    # commerce assumption. What would be a breach is the kernel seeding a capability it
    # could only have got from this example -- Cart, Listing, Checkout.
    founding = {key.lower() for key, _n, _d in FOUNDING_METATYPES}
    shared = sorted(labels & founding)
    assert shared == ["evolution"], (
        f"the kernel now seeds commerce capabilities beyond the universal abstraction "
        f"Evolution: {shared}"
    )
    assert labels - founding, "every commerce capability is seeded, so nothing is composed"


def test_composition_is_open_beyond_the_thirteen_that_were_listed() -> None:
    """An example that admits only its own members is not an example of composition."""
    from engine.provider.framework import ProviderFramework

    framework = ProviderFramework()
    for label in section("LYR-L4C").values():
        framework.register_category(_capability_key(label), name=label, description="composed")
    unlisted = "Capability-NoDocumentHasNamedThisOne"
    framework.register_category(unlisted, name="unlisted", description="admitted")
    assert unlisted in framework.category_keys()


# --- LYR-L8 — the Universal Runtime ---------------------------------------------
#
# Five claims about WHAT the runtime carries -- any application, domain, capability,
# environment, infrastructure -- and seven about what it UNDERSTANDS: identity, context,
# relationships, policies, events, state, evolution. The two halves are different kinds of
# claim and are kept apart: the first is openness, the second is a facet the runtime can
# read.
#
# All seven understandings are Article 6 facets, which is the strongest possible answer --
# the runtime does not need to be taught them, because every object carries them.

RUNTIME_OPENNESS = {
    "LYR-L8/RT-01": "Any Application",
    "LYR-L8/RT-02": "Any Domain",
    "LYR-L8/RT-03": "Any Capability",
    "LYR-L8/RT-04": "Any Environment",
    "LYR-L8/RT-05": "Any Infrastructure",
}

RUNTIME_UNDERSTANDING = {
    "LYR-L8/RT-06": Facet.IDENTITY,
    "LYR-L8/RT-07": Facet.CONTEXT,
    "LYR-L8/RT-08": Facet.RELATIONSHIPS,
    "LYR-L8/RT-09": Facet.POLICIES,
    "LYR-L8/RT-10": Facet.TEMPORAL_HISTORY,
    "LYR-L8/RT-11": Facet.LIFECYCLE,
    "LYR-L8/RT-12": Facet.EVOLUTION_HISTORY,
}


def test_the_runtime_layer_is_five_opennesses_and_seven_understandings() -> None:
    mandates = section("LYR-L8")
    assert len(mandates) == 12, f"layer 8 states 12 claims, corpus has {len(mandates)}"
    assert_partitions("LYR-L8", mandates, RUNTIME_OPENNESS, RUNTIME_UNDERSTANDING)


def test_every_runtime_understanding_is_a_facet_the_object_carries() -> None:
    """The runtime does not need teaching: every object carries these by Article 6."""
    import dataclasses

    from engine.uckp.facets import REQUIRED_FACETS
    from engine.uckp.ucko import UniversalConstitutionalKnowledgeObject as UCKO

    fields = {f.name for f in dataclasses.fields(UCKO)}
    for mandate, facet in RUNTIME_UNDERSTANDING.items():
        assert facet in REQUIRED_FACETS, f"{mandate}: {facet} is not required"
        assert (
            facet.attribute in fields
        ), f"{mandate}: no UCKO field carries {facet.value!r}, so the runtime cannot read it"
    facets = list(RUNTIME_UNDERSTANDING.values())
    assert len(facets) == len(set(facets)), "one facet claimed by two runtime understandings"


def test_the_runtime_openness_is_the_admission_property_already_proven() -> None:
    """The five `Any X` claims are the same openness the kernel proof establishes, so they
    are bound to it rather than re-proven -- a second proof of one property would be a second
    authoring of it."""
    from engine.kernel.compliance import architectural_proof

    proof = architectural_proof()
    assert proof["kernel_unchanged"] is True
    proven = {record["category"] for record in proof["records"] if record["ok"]}
    assert {
        "CapabilityDomain",
        "ProviderCategory",
        "ExecutionModelUnknown",
    } <= proven, "the categories the runtime's openness rests on are no longer represented"
    assert len(RUNTIME_OPENNESS) == 5


# --- LYR-L1 — the thirteen kinds of existence -----------------------------------
#
# "Represent anything that exists. Not only Earth. Not only humans. Not only physical
# reality." Thirteen kinds follow, and the layer's worked example is Earth beside Mars under
# the caption "Same architecture. Different configuration."
#
# That caption is the mandate and the kernel already enforces it: `earth` is one of the
# eighteen tokens the kernel refuses to seed, while `planet` is not. A Planet KIND is
# representable; the planet Earth is not a category the substrate may hold. Ten of the
# thirteen have a located home, two are representable and deliberately unbuilt, and the
# thirteenth is the openness claim.

EXISTENCE_HOME = {
    "LYR-L1/EX-01": "engine/uckp/facets.py",  # Existence -- the existence-context facet
    "LYR-L1/EX-02": "engine/construct/reality.py",  # Reality
    "LYR-L1/EX-03": "engine/uckp/universe.py",  # Universe
    "LYR-L1/EX-06": "engine/execution_environment",  # Environment
    "LYR-L1/EX-07": "engine/context/location.py",  # Location
    "LYR-L1/EX-08": "engine/zero_class/entity_derivation.py",  # Entity
    "LYR-L1/EX-09": "engine/uckp/ucko.py",  # Object
    "LYR-L1/EX-10": "engine/uckp/values.py",  # Event -- TemporalEvent
    "LYR-L1/EX-11": "engine/graph/model.py",  # Relationship
    "LYR-L1/EX-12": "engine/uckp/state.py",  # State
}

#: Representable and deliberately unbuilt. A Galaxy class and a Planet class would be the
#: fixed-cosmology equivalent of a fixed industry, and the layer says so in its own caption.
EXISTENCE_REPRESENTABLE = {
    "LYR-L1/EX-04": "Galaxy",
    "LYR-L1/EX-05": "Planet",
}

EXISTENCE_OPENNESS = {"LYR-L1/EX-13": "Unknown Future Construct"}


def test_every_kind_of_existence_is_homed_representable_or_the_openness_claim() -> None:
    mandates = section("LYR-L1")
    assert len(mandates) == 13, f"layer 1 lists 13 kinds, corpus has {len(mandates)}"
    assert_partitions(
        "LYR-L1",
        mandates,
        EXISTENCE_HOME,
        EXISTENCE_REPRESENTABLE,
        EXISTENCE_OPENNESS,
    )


def test_every_homed_kind_is_tracked_and_distinct() -> None:
    assert_homes_exist("LYR-L1", EXISTENCE_HOME)
    homes = list(EXISTENCE_HOME.values())
    duplicated = sorted({h for h in homes if homes.count(h) > 1})
    assert not duplicated, f"one module claimed for several kinds of existence: {duplicated}"


def test_planet_is_representable_and_earth_is_refused() -> None:
    """The layer's own example, executed.

    "Not only Earth" is enforced by the kernel refusing `earth` as a seedable category,
    while `planet` is not refused -- so a Planet KIND registers and the planet Earth cannot
    become one. If `planet` is ever prohibited the kind becomes unrepresentable, and if
    `earth` is ever permitted the caption stops being true; both directions are asserted.
    """
    from engine.kernel.compliance import PROHIBITED_TOKENS, kernel_source_fingerprint
    from engine.kernel.kernel import MetaKernel

    assert (
        "earth" in PROHIBITED_TOKENS
    ), "`earth` is no longer refused; 'Not only Earth' is no longer enforced by anything"
    for kind in EXISTENCE_REPRESENTABLE.values():
        assert (
            kind.lower() not in PROHIBITED_TOKENS
        ), f"{kind!r} is now refused, so this kind of existence cannot be represented at all"

    kernel = MetaKernel()
    before = kernel_source_fingerprint()
    for kind in EXISTENCE_REPRESENTABLE.values():
        kernel.register_metatype(f"Existence-{kind}", name=kind, description=f"existence: {kind}")
    assert kernel_source_fingerprint() == before
    registered = {obj.natural_key for obj in kernel.metatypes()}
    assert {"Existence-Galaxy", "Existence-Planet"} <= registered


def test_the_representable_kinds_are_not_built_as_classes() -> None:
    """NON-VACUITY. Representable-and-unbuilt is only a finding if nothing builds them."""
    assert_named_by_nothing(
        "LYR-L1",
        {m: kind.lower() for m, kind in EXISTENCE_REPRESENTABLE.items()},
    )


def test_the_existence_set_is_open() -> None:
    """EX-13 is not a kind; it is the claim the list can grow."""
    from engine.kernel.compliance import kernel_source_fingerprint
    from engine.kernel.kernel import MetaKernel

    kernel = MetaKernel()
    before = kernel_source_fingerprint()
    unlisted = "Existence-KindNoDocumentHasNamedYet"
    kernel.register_metatype(unlisted, name="unlisted", description="admitted by registration")
    assert unlisted in {obj.natural_key for obj in kernel.metatypes()}
    assert kernel_source_fingerprint() == before


# --- LYR-L15 — the fifteen-step evolution lifecycle -----------------------------
#
# Layer 15 calls itself "the most important layer" and lists fifteen steps. UCL-000001
# declares this repository's lifecycle in forty-five stages, and TWELVE of the fifteen are
# the same word: Understand, Measure, Learn, Reason, Challenge, Improve, Architect, Verify,
# Certify, Integrate, Replay, Elevate.
#
# That is the highest verbatim agreement anywhere in the corpus, and it is asserted as a
# count rather than described, so drift between the two documents fails instead of passing.
# The three that differ differ for stated reasons: two are performed by instruments the
# lifecycle does not name as stages, and `Repeat` is the loop itself, which UCL spells
# "Begin Next Elevated Engineering Cycle".

EVOLUTION_LIFECYCLE_VERBATIM = {
    "LYR-L15/EL-02": "Understand",
    "LYR-L15/EL-03": "Measure",
    "LYR-L15/EL-04": "Learn",
    "LYR-L15/EL-05": "Reason",
    "LYR-L15/EL-06": "Challenge",
    "LYR-L15/EL-07": "Improve",
    "LYR-L15/EL-08": "Architect",
    "LYR-L15/EL-10": "Verify",
    "LYR-L15/EL-11": "Certify",
    "LYR-L15/EL-12": "Integrate",
    "LYR-L15/EL-13": "Replay",
    "LYR-L15/EL-14": "Elevate",
}

#: The loop. Not a step but the instruction to run the fourteen again, which UCL names.
EVOLUTION_LIFECYCLE_LOOP = {"LYR-L15/EL-15": "Begin Next Elevated Engineering Cycle"}

#: Performed by an instrument the lifecycle does not name as a stage.
EVOLUTION_LIFECYCLE_INSTRUMENT = {
    "LYR-L15/EL-01": "engine/universal_discovery",  # Discover
    "LYR-L15/EL-09": "intelligence/realization/generators",  # Generate
}


def test_every_evolution_step_is_verbatim_the_loop_or_an_instrument() -> None:
    mandates = section("LYR-L15")
    assert len(mandates) == 15, f"layer 15 lists 15 steps, corpus has {len(mandates)}"
    assert_partitions(
        "LYR-L15",
        mandates,
        EVOLUTION_LIFECYCLE_VERBATIM,
        EVOLUTION_LIFECYCLE_LOOP,
        EVOLUTION_LIFECYCLE_INSTRUMENT,
    )


def test_twelve_steps_are_the_lifecycle_stage_name_exactly() -> None:
    """The finding, asserted as an exact set. Two documents written apart, twelve identical
    single words -- and the mandate label must BE the stage name, not merely resolve to it."""
    from engine.tests.conformance.test_mandates_model import _ucl_stage_names

    declared = _ucl_stage_names()
    mandates = section("LYR-L15")
    for mandate, stage in EVOLUTION_LIFECYCLE_VERBATIM.items():
        assert stage in declared, f"{mandate}: UCL declares no stage named {stage!r}"
        assert mandates[mandate] == stage, (
            f"{mandate}: the mandate reads {mandates[mandate]!r} and the stage {stage!r}; "
            "this tier is for verbatim agreement only"
        )
    assert len(EVOLUTION_LIFECYCLE_VERBATIM) == 12, (
        "the verbatim count changed; the two documents have drifted and the tiers need "
        "re-reading rather than re-baselining"
    )


def test_the_loop_step_names_the_stage_that_closes_the_cycle() -> None:
    """NON-VACUITY for the loop. `Repeat` is not a step and mapping it to one would report a
    fifteenth activity where there are fourteen and an instruction to run them again."""
    from engine.tests.conformance.test_mandates_model import _ucl_stage_names

    declared = _ucl_stage_names()
    mandates = section("LYR-L15")
    for mandate, stage in EVOLUTION_LIFECYCLE_LOOP.items():
        assert stage in declared, f"{mandate}: UCL declares no stage named {stage!r}"
        assert mandates[mandate] == "Repeat"
        assert (
            mandates[mandate] != stage
        ), "the loop is a verbatim match after all and belongs in the verbatim tier"


def test_the_two_instrument_steps_are_not_lifecycle_stages() -> None:
    from engine.tests.conformance.test_mandates_model import _ucl_stage_names

    assert_homes_exist("LYR-L15", EVOLUTION_LIFECYCLE_INSTRUMENT)
    declared = _ucl_stage_names()
    mandates = section("LYR-L15")
    for mandate in EVOLUTION_LIFECYCLE_INSTRUMENT:
        assert mandates[mandate] not in declared, (
            f"{mandate}: {mandates[mandate]!r} IS a declared stage and belongs in the "
            "verbatim tier"
        )


# --- LYR-L4 — the nine capability domains ---------------------------------------
#
# Layer 4 opens "Everything is a capability. No fixed application modules." and lists nine
# domains: Identity, Commerce, Mobility, Finance, Communication, Knowledge, Manufacturing,
# Governance, Future Capability.
#
# Seven of the nine are MARKETS under capability names. Commerce, Finance and Manufacturing
# are three of the twenty-seven target domains MI-017 lists, and MI-017 already settles what
# a market is owed: admission, never construction. The ninth entry is not a domain at all --
# `Future Capability` is the openness claim, exactly as MI-017 ends with Future Unknown
# Domains and UAKP-ENV with Future Unknown Environment.

CAPABILITY_DOMAIN_PREFIX = "Domain-"


def test_the_capability_layer_is_eight_domains_and_an_openness_claim() -> None:
    mandates = section("LYR-L4")
    assert len(mandates) == 9, f"layer 4 lists 9 capabilities, corpus has {len(mandates)}"
    labels = list(mandates.values())
    assert (
        labels[-1] == "Future Capability"
    ), f"the list no longer ends with the openness claim: {labels[-1]!r}"


def test_three_of_them_are_target_domains_the_master_index_already_settles() -> None:
    """The overlap is the argument. If these were built as capability modules they would be
    the fixed industries MI-017 refuses, so the overlap is asserted as a floor rather than
    described."""
    mandates = section("LYR-L4")
    here = {label.removesuffix(" Capability").lower() for label in mandates.values()}
    domains = {label.lower() for label in section("MI-017").values()}
    shared = sorted(here & domains)
    assert len(shared) >= 3, (
        f"the capability layer no longer overlaps the target domains; found {shared}. The "
        "argument that these are markets rather than modules rests on that overlap."
    )


def test_every_capability_domain_is_admissible_with_the_kernel_unchanged() -> None:
    from engine.kernel.compliance import kernel_source_fingerprint
    from engine.kernel.kernel import MetaKernel

    labels = list(section("LYR-L4").values())
    kernel = MetaKernel()
    before = kernel_source_fingerprint()
    for label in labels:
        key = CAPABILITY_DOMAIN_PREFIX + "".join(w.capitalize() for w in label.split())
        kernel.register_metatype(key, name=label, description=f"capability domain: {label}")

    assert kernel_source_fingerprint() == before, (
        "admitting the capability domains changed the kernel's source, so they were built as "
        "application modules -- which is what 'No fixed application modules' forbids"
    )
    registered = {obj.natural_key for obj in kernel.metatypes()}
    refused = sorted(
        label
        for label in labels
        if CAPABILITY_DOMAIN_PREFIX + "".join(w.capitalize() for w in label.split())
        not in registered
    )
    assert not refused, f"capability domains the kernel would not admit: {refused}"


def test_no_capability_domain_is_seeded_and_none_names_a_permitted_industry() -> None:
    """NON-VACUITY. None is a founding meta-type, and `industry` -- the token that would let
    one be seeded as a concrete market -- is still refused."""
    from engine.kernel.compliance import PROHIBITED_TOKENS
    from engine.kernel.seed import FOUNDING_METATYPES

    labels = {label.removesuffix(" Capability").lower() for label in section("LYR-L4").values()}
    founding = {key.lower() for key, _n, _d in FOUNDING_METATYPES}
    leaked = sorted(labels & founding - {"knowledge", "governance", "identity"})
    assert not leaked, f"capability domains seeded beyond the universal abstractions: {leaked}"
    assert "industry" in PROHIBITED_TOKENS, (
        "`industry` is no longer refused, so a capability domain could be seeded as a "
        "concrete market and LYR-NEG/LN-05 would be unenforced"
    )


# --- LYR-L14 — the eight interfaces ---------------------------------------------
#
# "Interfaces are generated." Eight follow, ending in Future Interface. One of the eight is
# generated; one exists and is hand-written; five are neither; and the eighth is an openness
# claim that this repository does not currently satisfy.
#
# THE OPENNESS CLAIM IS THE FINDING. Everywhere else in this corpus an open set is open by
# REGISTRATION -- metatypes, context kinds, lifecycle stages, provider categories all admit
# a member no document named, with the kernel unchanged. The generator families are not:
# `ArtifactFamily` is a closed Enum of seven, so adding a Web or Voice generator is a code
# edit, which is exactly what "Future Interface" promises it will not be.

INTERFACE_GENERATED = {"LYR-L14/IF-06": "api"}  # API -> ArtifactFamily.API

#: Exists and is not generated. CLIs are written by hand throughout the repository, and
#: `ArtifactFamily` has no cli member -- so the interface is present and the claim
#: "interfaces are generated" is not true of it.
INTERFACE_HAND_WRITTEN = {"LYR-L14/IF-07": "CLI"}

#: Neither generated nor present. Each would need a new artifact family, which is a code
#: edit rather than a registration.
INTERFACE_ABSENT = {
    "LYR-L14/IF-01": "web",
    "LYR-L14/IF-02": "mobile",
    "LYR-L14/IF-03": "voice",
    "LYR-L14/IF-04": "ar",
    "LYR-L14/IF-05": "vr",
}

INTERFACE_OPENNESS = {"LYR-L14/IF-08": "Future Interface"}


def test_every_interface_is_generated_hand_written_absent_or_the_openness_claim() -> None:
    mandates = section("LYR-L14")
    assert len(mandates) == 8, f"layer 14 lists 8 interfaces, corpus has {len(mandates)}"
    assert_partitions(
        "LYR-L14",
        mandates,
        INTERFACE_GENERATED,
        INTERFACE_HAND_WRITTEN,
        INTERFACE_ABSENT,
        INTERFACE_OPENNESS,
    )


def test_the_generated_interface_names_a_family_a_generator_claims() -> None:
    from intelligence.realization.contracts import ArtifactFamily
    from intelligence.realization.generators import GENERATORS

    claimed = {generator.family.value for generator in GENERATORS}
    for mandate, family in INTERFACE_GENERATED.items():
        assert family in {f.value for f in ArtifactFamily}, f"{mandate}: no {family!r} family"
        assert family in claimed, f"{mandate}: no generator claims {family!r}"


def test_clis_exist_and_are_not_generated() -> None:
    """NON-VACUITY for the hand-written tier, in both directions. CLIs are everywhere and no
    artifact family emits them, so the interface is present and the layer's claim about it
    is false."""
    from engine.tests.conformance.mandate_corpus import tracked
    from intelligence.realization.contracts import ArtifactFamily

    clis = [path for path in tracked() if path.endswith("cli.py") and "/tests/" not in path]
    assert len(clis) >= 5, f"only {len(clis)} CLI modules; the hand-written claim is thin"
    assert "cli" not in {
        f.value for f in ArtifactFamily
    }, "a cli artifact family now exists; LYR-L14/IF-07 is generated and belongs a tier up"


def test_the_absent_interfaces_have_no_family_and_no_module() -> None:
    from intelligence.realization.contracts import ArtifactFamily

    families = {f.value for f in ArtifactFamily}
    for mandate, interface in INTERFACE_ABSENT.items():
        assert interface not in families, f"{mandate}: a {interface!r} family now exists"
    # `ar` and `vr` are two-letter tokens and a two-letter token is not a searchable
    # requirement, so only the three that can be searched are searched.
    assert_named_by_nothing(
        "LYR-L14",
        {m: i for m, i in INTERFACE_ABSENT.items() if len(i) > 2},
    )


def test_the_interface_set_is_not_open_by_registration_and_the_layer_claims_it_is() -> None:
    """The finding, asserted so it cannot quietly stop being true.

    Every other open set in this corpus admits a member no document named, with the kernel
    unchanged: metatypes, context kinds, lifecycle stages, provider categories. The artifact
    families do not -- `ArtifactFamily` is a closed Enum, so a Future Interface costs a code
    edit. If the family set ever becomes registrable, this assertion fails and IF-08 is
    satisfied.
    """
    import enum

    from intelligence.realization.contracts import ArtifactFamily

    assert issubclass(ArtifactFamily, enum.Enum)
    assert len(ArtifactFamily) == 7, (
        f"the family set has changed size to {len(ArtifactFamily)}; if it became open by "
        "registration, LYR-L14/IF-08 is satisfied and this tier is wrong"
    )
    with pytest.raises(ValueError):
        ArtifactFamily("interface-no-document-has-named-yet")


# --- LYR-L0R — the six kernel responsibilities ----------------------------------
#
# Layer 0 lists six things the kernel is responsible for. All six are discharged, which
# makes this the third fully-answered section -- and, as with the other two, the six must
# resolve to six DISTINCT instruments or the completeness is an artefact of the mapping.

KERNEL_RESPONSIBILITY = {
    "LYR-L0R/KR-01": "engine/uckp/law.py",  # Define universal rules
    "LYR-L0R/KR-02": "engine/uckp/validation.py",  # Maintain consistency
    "LYR-L0R/KR-03": "engine/omega_infinite/contradiction.py",  # Prevent contradictions
    "LYR-L0R/KR-04": "engine/constitution/evolution.py",  # Govern evolution
    "LYR-L0R/KR-05": "00-BOOK/REGISTRIES/CHANGE-VERSION-LINEAGE-REGISTRY.md",  # Preserve lineage
    "LYR-L0R/KR-06": "engine/determinism",  # Enable replay
}


def test_every_kernel_responsibility_is_discharged_by_a_distinct_instrument() -> None:
    mandates = section("LYR-L0R")
    assert len(mandates) == 6, f"layer 0 lists 6 responsibilities, corpus has {len(mandates)}"
    assert_partitions("LYR-L0R", mandates, KERNEL_RESPONSIBILITY)
    assert_homes_exist("LYR-L0R", KERNEL_RESPONSIBILITY)
    homes = list(KERNEL_RESPONSIBILITY.values())
    assert len(set(homes)) == 6, f"six responsibilities, {len(set(homes))} instruments"


def test_maintaining_consistency_and_preventing_contradictions_are_two_things() -> None:
    """NON-VACUITY for the pair most likely to collapse.

    Consistency is about ONE object satisfying the law; contradiction is about TWO claims
    that cannot both be true. The repository separates them -- `require_coherent` refuses an
    incoherent state, and the contradiction engine compares claims that already exist -- and
    folding them together would report one responsibility discharged twice.
    """
    from engine.uckp.law import ROOT_LAW

    assert hasattr(
        ROOT_LAW, "require_coherent"
    ), "the root law no longer offers a coherence check; KR-02 rests on it"
    assert KERNEL_RESPONSIBILITY["LYR-L0R/KR-02"] != KERNEL_RESPONSIBILITY["LYR-L0R/KR-03"]
    contradiction = (repo_root() / KERNEL_RESPONSIBILITY["LYR-L0R/KR-03"]).read_text(
        encoding="utf-8"
    )
    assert "compares claims that already exist" in " ".join(contradiction.split()), (
        "the contradiction engine no longer describes itself as comparing existing claims, "
        "which is what distinguishes it from a coherence check"
    )


# --- LYR-L5N — the seven names for a structural container -----------------------
#
# "Even 'Nucleus' is not a hard-coded concept. The architecture supports configurable
# structural containers." Seven possible names follow, ending in Future Name.
#
# The repository hard-codes the first one. `engine/nucleus` is a package, so the single name
# the document offers as its example of what must NOT be fixed is the one that is. The other
# five register as meta-types with the kernel unchanged, and the seventh is the openness
# claim -- so the layer is satisfied for six of seven and contradicted by its own example.

CONTAINER_NAME_FIXED = {"LYR-L5N/UN-01": "engine/nucleus"}  # Nucleus

CONTAINER_NAME_REGISTRABLE = {
    "LYR-L5N/UN-02": "Domain",
    "LYR-L5N/UN-03": "Universe",
    "LYR-L5N/UN-04": "Module",
    "LYR-L5N/UN-05": "Realm",
    "LYR-L5N/UN-06": "Capability Cluster",
}

CONTAINER_NAME_OPENNESS = {"LYR-L5N/UN-07": "Future Name"}


def test_every_container_name_is_fixed_registrable_or_the_openness_claim() -> None:
    mandates = section("LYR-L5N")
    assert len(mandates) == 7, f"layer 5 lists 7 names, corpus has {len(mandates)}"
    assert_partitions(
        "LYR-L5N",
        mandates,
        CONTAINER_NAME_FIXED,
        CONTAINER_NAME_REGISTRABLE,
        CONTAINER_NAME_OPENNESS,
    )


def test_the_one_name_the_document_offers_as_an_example_is_the_one_fixed() -> None:
    """The finding, and it is about this repository rather than about the document.

    Layer 5 names Nucleus specifically to say it is not hard-coded. `engine/nucleus` is a
    package, which fixes it in the one place a name cannot be configured away. If the
    package is ever renamed or made configurable, this row moves to the registrable tier.
    """
    from engine.tests.conformance.mandate_corpus import tracked

    known = set(tracked())
    for mandate, home in CONTAINER_NAME_FIXED.items():
        assert any(
            path.startswith(home + "/") for path in known
        ), f"{mandate}: {home} is no longer a package; the name may be configurable now"


def test_the_other_five_names_register_with_the_kernel_unchanged() -> None:
    from engine.kernel.compliance import kernel_source_fingerprint
    from engine.kernel.kernel import MetaKernel

    kernel = MetaKernel()
    before = kernel_source_fingerprint()
    for name in CONTAINER_NAME_REGISTRABLE.values():
        key = "Container-" + "".join(word.capitalize() for word in name.split())
        kernel.register_metatype(key, name=name, description=f"structural container: {name}")
    assert kernel_source_fingerprint() == before
    registered = {obj.natural_key for obj in kernel.metatypes()}
    refused = sorted(
        name
        for name in CONTAINER_NAME_REGISTRABLE.values()
        if "Container-" + "".join(w.capitalize() for w in name.split()) not in registered
    )
    assert not refused, f"container names the kernel would not admit: {refused}"

    unlisted = "Container-NameNoDocumentHasOffered"
    kernel.register_metatype(unlisted, name="unlisted", description="admitted")
    assert unlisted in {obj.natural_key for obj in kernel.metatypes()}


# --- LYR-L11 — the nine measurements --------------------------------------------
#
# "Everything measurable." Nine measures follow, and four exist. The five that do not are
# Performance, Accuracy, Usage, Reliability -- and the shape is the same one ARCH-VALID
# found from the validation side: this repository measures what it IS and does not measure
# how it BEHAVES. Two sections, two vocabularies, one hole.

MEASUREMENT_INSTRUMENT = {
    "LYR-L11/ME-02": "engine/kernel/compliance.py",  # Quality -- the quality gates
    "LYR-L11/ME-04": "engine/verification_intelligence/cost_model.py",  # Cost
    "LYR-L11/ME-07": "00-MASTER/UEI-000001/uei.json",  # Evolution
    "LYR-L11/ME-09": "engine/runtime/execution/health.py",  # Health
}

#: Impact is measured by a graph projection rather than a module.
MEASUREMENT_PROJECTION = {"LYR-L11/ME-08": "impact"}  # Impact

MEASUREMENT_ABSENT = {
    "LYR-L11/ME-01": "performance",
    "LYR-L11/ME-03": "accuracy",
    "LYR-L11/ME-05": "usage",
    "LYR-L11/ME-06": "reliability",
}


def test_every_measurement_is_instrumented_projected_or_absent() -> None:
    mandates = section("LYR-L11")
    assert len(mandates) == 9, f"layer 11 lists 9 measurements, corpus has {len(mandates)}"
    assert_partitions(
        "LYR-L11",
        mandates,
        MEASUREMENT_INSTRUMENT,
        MEASUREMENT_PROJECTION,
        MEASUREMENT_ABSENT,
    )
    assert_homes_exist("LYR-L11", MEASUREMENT_INSTRUMENT)


def test_impact_is_measured_by_a_projection_the_graph_engine_builds() -> None:
    """NON-VACUITY for the one row that is not a module. A projection name that
    `build_projection` does not resolve would measure nothing."""
    from engine.tests.conformance.test_mandates_index import _built_projections

    built = _built_projections()
    for mandate, projection in MEASUREMENT_PROJECTION.items():
        assert projection in built, (
            f"{mandate}: engine/graph builds no {projection!r} projection, so nothing "
            "measures impact"
        )


def test_the_measurement_gap_is_the_behavioural_one_arch_valid_already_found() -> None:
    """The finding, asserted across two sections that use different words for it.

    ARCH-VALID records Performance, Reliability, Scalability and Interoperability as
    unvalidated; this section records Performance, Accuracy, Usage and Reliability as
    unmeasured. The overlap is not a coincidence -- you cannot validate what you do not
    measure -- so the two are asserted together and neither reads as a lone gap.
    """
    from engine.tests.conformance.test_mandates_arch import VALIDATION_ABSENT

    assert_named_by_nothing("LYR-L11", MEASUREMENT_ABSENT)
    unvalidated = set(VALIDATION_ABSENT.values())
    unmeasured = set(MEASUREMENT_ABSENT.values())
    assert {"performance", "reliability"} <= unvalidated & unmeasured, (
        "performance or reliability is now measured or validated; the claim that this "
        "repository measures what it is and not how it behaves must be re-read"
    )


# --- LYR-STACK — the six boxes of the architecture ------------------------------
#
# The layer document opens with a six-box stack, kernel at the bottom and generated
# applications at the top. All six are located, which is what one would hope of a diagram of
# the system's own spine -- and the six must be six DISTINCT instruments, or the stack has
# fewer layers than it draws.

ARCHITECTURE_BOX = {
    "LYR-STACK/LS-01": "engine/kernel",  # Universal Constitutional Kernel
    "LYR-STACK/LS-02": "engine/context",  # Universal Existence and Context Engine
    "LYR-STACK/LS-03": "engine/uckp/universe.py",  # Universal Knowledge Universe
    "LYR-STACK/LS-04": "engine/provider/framework.py",  # Universal Capability Composer
    "LYR-STACK/LS-05": "00-MASTER/UCOS-AEE-001/aee_engine.py",  # Universal Evolution Engine
    "LYR-STACK/LS-06": "intelligence/realization",  # Generated Reality Applications
}


def test_every_architecture_box_is_located_and_distinct() -> None:
    mandates = section("LYR-STACK")
    assert len(mandates) == 6, f"the stack draws 6 boxes, corpus has {len(mandates)}"
    assert_partitions("LYR-STACK", mandates, ARCHITECTURE_BOX)
    assert_homes_exist("LYR-STACK", ARCHITECTURE_BOX)
    homes = list(ARCHITECTURE_BOX.values())
    assert len(set(homes)) == 6, f"six boxes, {len(set(homes))} instruments"


def test_the_capability_composer_is_the_thing_that_composes_without_building() -> None:
    """NON-VACUITY for the box the whole architecture turns on. A composer that changed the
    kernel would make every 'admitted, not built' finding in this suite false."""
    from engine.kernel.compliance import kernel_source_fingerprint
    from engine.provider.framework import ProviderFramework

    framework = ProviderFramework()
    before = kernel_source_fingerprint()
    framework.register_category("Box-CompositionProof", name="proof", description="composed")
    assert kernel_source_fingerprint() == before, (
        "the capability composer changes the kernel when it composes; every admission proof "
        "in this suite rests on it not doing that"
    )
    assert "Box-CompositionProof" in framework.category_keys()


def test_the_top_box_is_generated_and_the_bottom_box_is_not() -> None:
    """The stack's direction, asserted. Generated Reality Applications sit above the kernel
    because they are PRODUCED from it; if the kernel were itself generated the stack would
    have no ground."""
    import json

    registry = json.loads(
        (repo_root() / "00-BOOK" / "DATA" / "generated-artifact-registry.json").read_text(
            encoding="utf-8"
        )
    )
    generated = {entry["canonical_path"] for entry in registry["entries"]}
    kernel = ARCHITECTURE_BOX["LYR-STACK/LS-01"]
    assert not [p for p in generated if p.startswith(kernel + "/")], (
        f"{kernel} now contains generated artifacts; the bottom of the stack is produced by "
        "something and the diagram has no ground"
    )


# --- LYR-L3 — the six parts of the Knowledge Universe ---------------------------
#
# All six located. The third part is worth a note: `Dynamic Knowledge Nuclei` is the same
# `nucleus` name LYR-L5N offers as its example of a container name that must not be fixed.
# Here the knowledge layer uses it as a structural term, and `engine/nucleus` is what
# answers -- so the two layers are consistent with each other and both are inconsistent
# with L5N's own caption.

KNOWLEDGE_UNIVERSE_PART = {
    "LYR-L3/KU-01": "engine/uckp/universe.py",  # Universal Knowledge Universe
    "LYR-L3/KU-02": "engine/knowledge/ukip/registry.py",  # Knowledge Domain Registry
    "LYR-L3/KU-03": "engine/nucleus",  # Dynamic Knowledge Nuclei
    "LYR-L3/KU-04": "engine/uckp/ucko.py",  # Knowledge Objects
    "LYR-L3/KU-05": "engine/knowledge/ukip/relationships.py",  # Knowledge Relationships
    "LYR-L3/KU-06": "engine/uckp/evolution.py",  # Knowledge Evolution
}


def test_every_knowledge_universe_part_is_located_and_distinct() -> None:
    mandates = section("LYR-L3")
    assert len(mandates) == 6, f"layer 3 lists 6 parts, corpus has {len(mandates)}"
    assert_partitions("LYR-L3", mandates, KNOWLEDGE_UNIVERSE_PART)
    assert_homes_exist("LYR-L3", KNOWLEDGE_UNIVERSE_PART)
    homes = list(KNOWLEDGE_UNIVERSE_PART.values())
    assert len(set(homes)) == 6, f"six parts, {len(set(homes))} instruments"


def test_the_nuclei_part_uses_the_one_container_name_layer_five_says_is_not_fixed() -> None:
    """The cross-layer note, asserted so it cannot drift.

    Layer 5 names Nucleus as its example of a container name that must NOT be hard-coded.
    Layer 3 uses `Dynamic Knowledge Nuclei` as a structural term and `engine/nucleus`
    answers it. The two layers agree with each other and both sit against L5N's caption --
    which is a finding about the documents as much as about the repository.
    """
    assert KNOWLEDGE_UNIVERSE_PART["LYR-L3/KU-03"] == CONTAINER_NAME_FIXED["LYR-L5N/UN-01"], (
        "the nuclei part and the fixed container name no longer resolve to the same package; "
        "the cross-layer note has drifted and needs re-reading"
    )


# --- LYR-L5 / L9 / L10 / L13 / L0 / L6 — the layer remainder ---------------------
#
# What is left of the layer document. Three of the four commercialization rows repeat the
# shape this corpus has met at every turn: Product is a market token the kernel refuses,
# Service and License are real modules, and Distribution is absent -- the same absence
# PRD-ECON records as the settlement chain, one step further out.

LAYER_REMAINDER = {
    # L5 Universal Structure
    "LYR-L5/US-07": "intelligence/realization/generators",  # Generator
    "LYR-L5/US-09": "engine/acceptance/contracts.py",  # Contracts
    # L9 Data & Knowledge Architecture
    "LYR-L9/KG-01": "engine/graph/model.py",  # Universal Knowledge Graph
    "LYR-L9/KG-02": "engine/uckp/ucko.py",  # Objects
    "LYR-L9/KG-06": "engine/uckp/values.py",  # History -- TemporalEvent
    # L10 Universal Governance System
    "LYR-L10/GV-03": "platform/administration/permissions.py",  # Permissions
    "LYR-L10/GV-08": "00-MASTER/UCOS-AB-001/07-CHANGE-CONTROL-CONSTITUTION.md",  # Change Control
    # Evolution Rules
    "LYR-L10/GV-09": "00-CEP/CEP-009-CONSTITUTIONAL-AMENDMENT-EVOLUTION-CONSTITUTION.md",
    # L13 Commercialization
    "LYR-L13/CM-02": "platform/commercial_intelligence/service.py",  # Service
    "LYR-L13/CM-05": "platform/commercial_intelligence/licensing.py",  # License
    # L0 core concepts
    "LYR-L0/K-13": "engine/uckp/vocabulary.py",  # Lifecycle -- the stage vocabulary
    # L6 Automation Engine
    "LYR-L6/AU-02": "engine/uckp/assimilation.py",  # Assimilation
}

#: Interfaces resolve through LYR-L14 rather than being re-located.
LAYER_REMAINDER_VIA_SECTION = {"LYR-L5/US-11": "LYR-L14"}  # Interfaces

#: `product` is a token the kernel refuses to seed.
LAYER_REMAINDER_MARKET_SHAPED = {"LYR-L13/CM-01": "Product"}

#: Distribution is the settlement chain one step further out: there is nothing to distribute
#: because nothing is sold.
LAYER_REMAINDER_ABSENT = {"LYR-L13/CM-10": "distribution"}


def test_the_layer_remainder_is_located_joined_market_shaped_or_absent() -> None:
    mandates: dict[str, str] = {}
    for name in ("LYR-L5", "LYR-L9", "LYR-L10", "LYR-L13", "LYR-L0", "LYR-L6"):
        mandates.update(section(name))
    covered = {
        **LAYER_REMAINDER,
        **LAYER_REMAINDER_VIA_SECTION,
        **LAYER_REMAINDER_MARKET_SHAPED,
        **LAYER_REMAINDER_ABSENT,
    }
    foreign = sorted(set(covered) - set(mandates))
    assert not foreign, f"tiered identifiers that are not layer mandates: {foreign}"
    assert_homes_exist("LYR-remainder", LAYER_REMAINDER)
    homes = list(LAYER_REMAINDER.values())
    assert len(set(homes)) == len(homes), "one instrument claimed for two remainder rows"


def test_interfaces_resolve_through_the_interface_layer() -> None:
    """The join. Layer 5 lists Interfaces as a part of the universal structure and Layer 14
    is the section that owns them -- including the finding that the generator families are a
    closed set. Re-locating them here would lose that."""
    assert LAYER_REMAINDER_VIA_SECTION["LYR-L5/US-11"] == "LYR-L14"
    assert (
        len(INTERFACE_ABSENT) == 5
    ), "the interface layer's absent set has changed size; the Layer 5 row rests on it"


def test_product_is_refused_and_distribution_has_nothing_to_distribute() -> None:
    """The commercialization layer, and it fails the same way PRD-ECON does one step out.

    Product is a market token the kernel will not seed. Distribution is absent because
    nothing is sold: PRD-ECON records Revenue, Billing and Settlement all missing, so there
    is no transaction for a distribution to follow.
    """
    from engine.kernel.compliance import PROHIBITED_TOKENS
    from engine.tests.conformance.test_mandates_prd import ECONOMIC_FACULTY_ABSENT

    assert "product" in PROHIBITED_TOKENS
    assert {"revenue", "billing", "settlement"} <= set(ECONOMIC_FACULTY_ABSENT.values()), (
        "the settlement chain has landed; Distribution has a transaction to follow and is a "
        "missing module rather than a moot one"
    )
    assert_named_by_nothing("LYR-remainder", LAYER_REMAINDER_ABSENT)


def test_the_lifecycle_core_concept_is_the_open_vocabulary_not_an_enum() -> None:
    """Layer 0 lists Lifecycle among the kernel's core concepts, and the concept this
    repository holds is the OPEN one: an append-only stage vocabulary, not a fixed enum.
    UAKP-STATE proves the openness; this row names the same instrument."""
    from engine.uckp.vocabulary import DEFAULT_VOCABULARIES, LIFECYCLE_STAGE

    assert LAYER_REMAINDER["LYR-L0/K-13"] == "engine/uckp/vocabulary.py"
    vocabulary = DEFAULT_VOCABULARIES.require(LIFECYCLE_STAGE)
    assert len(vocabulary.term_ids()) >= 10, "the lifecycle vocabulary has lost its stages"
