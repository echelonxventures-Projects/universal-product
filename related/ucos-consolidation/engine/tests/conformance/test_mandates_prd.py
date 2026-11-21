"""Mandate conformance — the Product Requirements Document (Constitutional Foundation v1.0).

188 mandates over 18 sections. The PRD's negative principles and success criteria are bound
separately, in `engine/tests/kernel/test_compliance.py`, against the instrument that can
actually decide a negative: a running kernel whose source fingerprint is measured. Nothing
here re-states those; a second binding of the same claim is the duplication ART-03 voids.
"""

from __future__ import annotations

from engine.tests.conformance.mandate_corpus import (
    assert_absence_rule_can_find_something,
    assert_homes_exist,
    assert_partitions,
    section,
)

# --- PRD-ADM — the Universal Admission Framework --------------------------------
#
# Section 7 states nine things every new construct must support, and closes with the
# sentence that makes them testable rather than aspirational: "No manual platform redesign."
#
# Two different claims live in that section and this suite keeps them apart. The nine steps
# are CAPABILITIES -- each needs a located instrument. The closing sentence is a property of
# the platform as a whole, and it is already proven where it can be proven: the kernel
# admission tests measure a source fingerprint across an admission and require it unchanged.
# Restating that here would add a second authority for one claim without adding evidence.

#: Admission step -> the instrument that carries it.
ADMISSION_STEP_HOME = {
    "PRD-ADM/ADM-01": "engine/universal_discovery",  # Discovery
    "PRD-ADM/ADM-02": "engine/registry",  # Registration
    "PRD-ADM/ADM-03": "engine/knowledge/ukip/classification.py",  # Classification
    "PRD-ADM/ADM-04": "engine/validation",  # Validation
    "PRD-ADM/ADM-05": "engine/governance",  # Governance
    "PRD-ADM/ADM-06": "engine/uicm/observation.py",  # Observation
    "PRD-ADM/ADM-07": "engine/constitution/evolution.py",  # Evolution
    "PRD-ADM/ADM-08": "engine/certification",  # Certification
    "PRD-ADM/ADM-09": "intelligence/publication",  # Publication
}


def test_every_admission_step_has_a_located_instrument() -> None:
    mandates = section("PRD-ADM")
    assert len(mandates) == 9, f"section 7 states 9 admission steps, corpus has {len(mandates)}"
    assert_partitions("PRD-ADM", mandates, ADMISSION_STEP_HOME)
    assert_homes_exist("PRD-ADM", ADMISSION_STEP_HOME)


def test_every_admission_instrument_is_importable_code_not_a_specification() -> None:
    """An admission step whose home is prose is a described capability, not one a construct
    can pass through. Each home is required to carry Python that imports."""
    import importlib

    from engine.tests.conformance.mandate_corpus import repo_root

    for mandate, home in ADMISSION_STEP_HOME.items():
        path = repo_root() / home
        if path.is_dir():
            assert any(path.rglob("*.py")), f"{mandate}: {home} carries no code"
            module = home.replace("/", ".")
        else:
            assert path.suffix == ".py", f"{mandate}: {home} is not code"
            module = home[: -len(".py")].replace("/", ".")
        importlib.import_module(module)


def test_the_nine_steps_are_nine_distinct_instruments() -> None:
    """NON-VACUITY. Nine mandated capabilities all pointing at one module would mean eight
    of them are unlocated and the mapping is hiding it."""
    homes = list(ADMISSION_STEP_HOME.values())
    duplicated = sorted({h for h in homes if homes.count(h) > 1})
    assert not duplicated, f"one instrument claimed for several admission steps: {duplicated}"


def test_no_manual_platform_redesign_is_bound_elsewhere_and_not_restated_here() -> None:
    """The closing sentence of section 7 is a whole-platform property. It is decided by the
    kernel admission proof, which measures a source fingerprint across an admission -- the
    only instrument here that can decide it. This test asserts that binding still exists so
    the claim cannot go missing by being nobody's."""
    from engine.kernel.compliance import architectural_proof

    proof = architectural_proof()
    assert proof["kernel_unchanged"] is True, (
        "categories are represented but the kernel source changed, so 'no manual platform "
        "redesign' is false and every admission step above admits into a moving target"
    )


def test_the_naming_rule_this_suite_relies_on_can_find_something() -> None:
    assert_absence_rule_can_find_something("knowledge ukip classification")


# --- PRD-ECON — the Universal Economic Framework --------------------------------
#
# Section 13 has two halves and they mandate different things. Twelve FACULTIES -- "Every
# construct may support: Cost, Revenue, Billing, Settlement..." -- and nine TENURES,
# "Everything may be: Free, Paid, Owned, Shared, Leased, Licensed, Auctioned, Tokenized,
# Fractionalized." A faculty is machinery the substrate must have. A tenure is a state a
# thing may be held under, which is a vocabulary question and not a module question.
#
# Keeping them apart is what stops the section reading as twenty-one missing modules. It
# also isolates the real finding: of the twelve faculties, four are built and eight are
# not, and the eight are the ones money actually moves through -- Revenue, Billing,
# Settlement, Taxation. The substrate can price a thing and license it, and cannot charge
# for it.

#: Faculty -> the module that provides it.
ECONOMIC_FACULTY = {
    "PRD-ECON/ECON-01": "engine/verification_intelligence/cost_model.py",  # Cost
    "PRD-ECON/ECON-05": "platform/commercial_intelligence/pricing.py",  # Pricing
    "PRD-ECON/ECON-09": "engine/nucleus/ownership.py",  # Ownership
    "PRD-ECON/ECON-10": "platform/commercial_intelligence/licensing.py",  # Licensing
    "PRD-ECON/ECON-11": "platform/commercial_intelligence/marketplace.py",  # Marketplace
}

#: Faculty -> nothing. Seven of the twelve, and the settlement chain is all of it.
ECONOMIC_FACULTY_ABSENT = {
    "PRD-ECON/ECON-02": "revenue",
    "PRD-ECON/ECON-03": "billing",
    "PRD-ECON/ECON-04": "settlement",
    "PRD-ECON/ECON-06": "subscription",
    "PRD-ECON/ECON-07": "royalty",
    "PRD-ECON/ECON-08": "taxation",
    "PRD-ECON/ECON-12": "commerce",
}

#: The nine tenures. Not modules: a tenure is a state a thing is held under, and the
#: substrate's answer to "may everything be held this way" is its open vocabulary, the same
#: mechanism that answers the lifecycle. None of the nine is seeded, which is correct --
#: seeding `Auctioned` would fix a commercial model, and PRD principle P-001 forbids exactly
#: that. They are registrable, and that is the whole obligation.
ECONOMIC_TENURE = {
    "PRD-ECON/ECON-13": "Free",
    "PRD-ECON/ECON-14": "Paid",
    "PRD-ECON/ECON-15": "Owned",
    "PRD-ECON/ECON-16": "Shared",
    "PRD-ECON/ECON-17": "Leased",
    "PRD-ECON/ECON-18": "Licensed",
    "PRD-ECON/ECON-19": "Auctioned",
    "PRD-ECON/ECON-20": "Tokenized",
    "PRD-ECON/ECON-21": "Fractionalized",
}


def test_every_economic_mandate_is_a_faculty_or_a_tenure() -> None:
    mandates = section("PRD-ECON")
    assert (
        len(mandates) == 21
    ), f"section 13 states 21 economic mandates, corpus has {len(mandates)}"
    assert_partitions(
        "PRD-ECON",
        mandates,
        ECONOMIC_FACULTY,
        ECONOMIC_FACULTY_ABSENT,
        ECONOMIC_TENURE,
    )
    assert len(ECONOMIC_FACULTY) + len(ECONOMIC_FACULTY_ABSENT) == 12
    assert len(ECONOMIC_TENURE) == 9


def test_every_built_faculty_has_a_tracked_module() -> None:
    assert_homes_exist("PRD-ECON", ECONOMIC_FACULTY)


def test_the_absent_faculties_are_named_by_no_module() -> None:
    """NON-VACUITY. Cost and Ownership are why this is searched rather than assumed: both
    read as obvious gaps in a repository with no billing, and both exist."""
    from engine.tests.conformance.mandate_corpus import assert_named_by_nothing

    assert_named_by_nothing("PRD-ECON", ECONOMIC_FACULTY_ABSENT)


def test_the_settlement_chain_is_the_gap_rather_than_scattered_holes() -> None:
    """The finding, asserted so it cannot quietly stop being true. Revenue, Billing,
    Settlement and Taxation are the faculties money moves through, and none exists."""
    chain = {"revenue", "billing", "settlement", "taxation"}
    assert chain <= set(ECONOMIC_FACULTY_ABSENT.values()), (
        "part of the settlement chain now exists; the claim that this substrate can price "
        "a thing and cannot charge for it no longer holds"
    )


def test_no_tenure_is_seeded_as_a_commercial_model() -> None:
    """The tenures are answered by refusing to fix them.

    Seeding `Auctioned` or `Tokenized` as a built-in would be a fixed business model, which
    PRD principle P-001 forbids in its first line and LYR-NEG/LN-07 forbids again. So the
    obligation is that none is hard-coded and every one is registrable -- proven the same
    way the object classes and the lifecycle states are proven.
    """
    from engine.kernel.compliance import kernel_source_fingerprint
    from engine.kernel.kernel import MetaKernel
    from engine.kernel.seed import FOUNDING_METATYPES

    tenures = list(ECONOMIC_TENURE.values())
    founding = {key.lower() for key, _name, _description in FOUNDING_METATYPES}
    leaked = sorted(t for t in tenures if t.lower() in founding)
    assert not leaked, f"tenures seeded as founding meta-types, fixing a business model: {leaked}"

    kernel = MetaKernel()
    before = kernel_source_fingerprint()
    for tenure in tenures:
        kernel.register_metatype(f"Tenure-{tenure}", name=tenure, description=f"tenure: {tenure}")
    assert kernel_source_fingerprint() == before, (
        "admitting the tenures changed the kernel's source, so they were built as business "
        "models rather than registered"
    )
    registered = {obj.natural_key for obj in kernel.metatypes()}
    refused = sorted(t for t in tenures if f"Tenure-{t}" not in registered)
    assert not refused, f"tenures the kernel would not admit: {refused}"


def test_the_three_tenures_dispositioned_create_are_admissions_not_gaps() -> None:
    """Auctioned, Tokenized and Fractionalized are three of the seventeen CREATE concepts.
    Building them is what LN-07 forbids, so the disposition is answered by admission -- the
    same correction Monorepo and Polyrepo needed."""
    assert {"Auctioned", "Tokenized", "Fractionalized"} <= set(ECONOMIC_TENURE.values())


def test_royalty_stays_a_genuine_gap_because_it_is_a_faculty_not_a_tenure() -> None:
    """The fourth CREATE concept in this section does NOT get the same answer, and the
    difference is the point: a royalty is machinery that computes and pays, not a state a
    thing is held under. Admitting the word would prove nothing about the faculty."""
    assert "PRD-ECON/ECON-07" in ECONOMIC_FACULTY_ABSENT
    assert "royalty" not in {t.lower() for t in ECONOMIC_TENURE.values()}


# --- PRD-MD — Universal Multi-Dimensional Support -------------------------------
#
# Fourteen dimensions "without limits". None of them is a feature, and treating them as
# features is the breach: shipping Multi-Currency means the substrate knows what a currency
# IS, and `currency` is one of the eighteen tokens the kernel refuses to seed. The mandate
# is satisfied by NOT knowing -- by refusing the fixed category and representing the axis by
# registration instead.
#
# So each dimension is answered one of two ways, and both are already instruments in this
# repository: a PROHIBITED TOKEN the kernel will not seed as a concrete category, or an
# UNKNOWN CATEGORY the architectural proof represents with the kernel unchanged. Five are
# answered by neither, and those five are the finding.

#: Dimension -> the token the kernel refuses to seed, which is how the axis stays open.
DIMENSION_REFUSED_TOKEN = {
    "PRD-MD/MD-02": "company",  # Multi-Organization
    "PRD-MD/MD-03": "language",  # Multi-Language
    "PRD-MD/MD-05": "currency",  # Multi-Currency
    "PRD-MD/MD-06": "tax",  # Multi-Tax
    "PRD-MD/MD-08": "cloud",  # Multi-Cloud
}

#: Dimension -> the unknown category the architectural proof represents.
DIMENSION_UNKNOWN_CATEGORY = {
    "PRD-MD/MD-04": "Civilization",  # Multi-Culture
    "PRD-MD/MD-07": "GovernanceModel",  # Multi-Jurisdiction
    "PRD-MD/MD-10": "CapabilityDomain",  # Multi-Reality
    "PRD-MD/MD-12": "TemporalModel",  # Multi-Timeline
}

#: Neither refused nor represented. The substrate has no axis for these at all, which means
#: nothing stops one of them being hard-coded tomorrow -- the gap is the absence of a
#: refusal, not the absence of a feature.
DIMENSION_UNHELD = {
    "PRD-MD/MD-01": "Multi-Tenant",
    "PRD-MD/MD-09": "Multi-Edge",
    "PRD-MD/MD-11": "Multi-Existence",
    "PRD-MD/MD-13": "Multi-Universe",
    "PRD-MD/MD-14": "Multi-Dimension",
}


def test_every_dimension_is_refused_represented_or_unheld() -> None:
    mandates = section("PRD-MD")
    assert len(mandates) == 14, f"section 19 states 14 dimensions, corpus has {len(mandates)}"
    assert_partitions(
        "PRD-MD",
        mandates,
        DIMENSION_REFUSED_TOKEN,
        DIMENSION_UNKNOWN_CATEGORY,
        DIMENSION_UNHELD,
    )


def test_every_token_backed_dimension_names_a_token_the_kernel_refuses_to_seed() -> None:
    from engine.kernel.compliance import PROHIBITED_TOKENS
    from engine.kernel.seed import FOUNDING_METATYPES

    founding = {key.lower() for key, _n, _d in FOUNDING_METATYPES}
    for mandate, token in DIMENSION_REFUSED_TOKEN.items():
        assert token in PROHIBITED_TOKENS, (
            f"{mandate}: {token!r} is not a prohibited token, so nothing stops this "
            "dimension being fixed to one value"
        )
        assert token not in founding, f"{mandate}: {token!r} is seeded as a founding meta-type"


def test_every_category_backed_dimension_is_proven_with_the_kernel_unchanged() -> None:
    from engine.kernel.compliance import architectural_proof

    proof = architectural_proof()
    proven = {record["category"] for record in proof["records"] if record["ok"]}
    for mandate, category in DIMENSION_UNKNOWN_CATEGORY.items():
        assert (
            category in proven
        ), f"{mandate}: {category!r} is not among the represented categories {sorted(proven)}"
    assert proof["kernel_unchanged"] is True, (
        "the categories are represented but the kernel source changed, so 'without limits' "
        "is false for every dimension bound above"
    )


def test_the_two_mechanisms_are_not_the_same_claim_twice() -> None:
    """NON-VACUITY. A refused token keeps an axis open by forbidding a value; a represented
    category keeps it open by admitting one. A dimension answered by both would be
    double-counted, and one answered by neither would hide in the overlap."""
    assert not (set(DIMENSION_REFUSED_TOKEN) & set(DIMENSION_UNKNOWN_CATEGORY))
    tokens = set(DIMENSION_REFUSED_TOKEN.values())
    categories = {c.lower() for c in DIMENSION_UNKNOWN_CATEGORY.values()}
    assert not (tokens & categories)


def test_the_unheld_dimensions_are_refused_by_nothing_and_represented_by_nothing() -> None:
    """NON-VACUITY for the tier that matters most here.

    These five have no refusal, which is a different and quieter failure than a missing
    feature: nothing in the kernel would object if `tenant` or `edge` were seeded as a
    concrete category tomorrow, and the mandate would be silently broken.
    """
    from engine.kernel.compliance import PROHIBITED_TOKENS, UNKNOWN_CATEGORIES

    categories = {key.lower() for key, _i, _a in UNKNOWN_CATEGORIES}
    for mandate, dimension in DIMENSION_UNHELD.items():
        axis = dimension.removeprefix("Multi-").lower()
        assert (
            axis not in PROHIBITED_TOKENS
        ), f"{mandate}: {axis!r} is now a prohibited token and this dimension is held"
        assert not any(
            axis in category for category in categories
        ), f"{mandate}: {axis!r} is now represented by an unknown category"


# --- PRD-SELF — the fourteen self-* requirements --------------------------------
#
# "Platform must be: Self Discovering, Self Registering..." The prefix is the whole mandate.
# A repository that validates OTHER things is not self-validating, and an optimiser that
# improves the code it compiles is not self-optimising. So a row is admitted only when the
# instrument's SUBJECT is this repository, and the two that fail that test fail it for
# reasons worth naming rather than for want of a module.

#: Requirement -> the instrument whose subject is this repository.
SELF_INSTRUMENT = {
    "PRD-SELF/SELF-01": "engine/universal_discovery",  # Self Discovering
    "PRD-SELF/SELF-02": "00-BOOK/tools/register.sh",  # Self Registering
    "PRD-SELF/SELF-03": "00-BOOK/tools/config.py",  # Self Classifying -- CLASSIFY_RULES
    "PRD-SELF/SELF-04": "00-BOOK/tools/ukb.py",  # Self Documenting -- it writes its own book
    "PRD-SELF/SELF-05": "engine/constitution/gateway.py",  # Self Governing
    "PRD-SELF/SELF-06": "engine/validation",  # Self Validating
    "PRD-SELF/SELF-07": "verify.sh",  # Self Verifying
    # Self Certifying
    "PRD-SELF/SELF-08": "00-MASTER/P0-FINAL-CLOSURE-002/final_closure_engine.py",
    "PRD-SELF/SELF-09": "00-MASTER/UCOS-UGA-001/06-SELF-OBSERVATION.json",  # Self Monitoring
    "PRD-SELF/SELF-12": "00-MASTER/UCOS-AEE-001/aee_engine.py",  # Self Evolving
    "PRD-SELF/SELF-13": "intelligence/publication",  # Self Publishing
    "PRD-SELF/SELF-14": "00-BOOK/DATA/canonical-observation-audit.json",  # Self Auditing
}

#: Requirement -> (the nearest instrument, why it is NOT the self-* capability). Both of
#: these would pass a keyword sweep and neither does what the prefix demands.
SELF_NEAR_MISS = {
    "PRD-SELF/SELF-10": (
        "engine/runtime/execution/health.py",
        "health is DETECTED and nothing acts on the detection; detecting is not healing",
    ),
    "PRD-SELF/SELF-11": (
        "engine/compiler/optimization.py",
        "the compiler optimises the output it emits, not the platform that emits it",
    ),
}


def test_every_self_requirement_is_instrumented_or_a_near_miss() -> None:
    mandates = section("PRD-SELF")
    assert (
        len(mandates) == 14
    ), f"section 20 states 14 self-* requirements, corpus has {len(mandates)}"
    assert_partitions("PRD-SELF", mandates, SELF_INSTRUMENT, SELF_NEAR_MISS)


def test_every_self_instrument_is_tracked_and_distinct() -> None:
    """Twelve capabilities pointing at one instrument would mean eleven are unlocated."""
    assert_homes_exist("PRD-SELF", SELF_INSTRUMENT)
    homes = list(SELF_INSTRUMENT.values())
    duplicated = sorted({h for h in homes if homes.count(h) > 1})
    assert not duplicated, f"one instrument claimed for several self-* requirements: {duplicated}"


def test_the_self_classifying_and_self_documenting_claims_name_what_does_the_work() -> None:
    """NON-VACUITY for the two rows that rest on a file rather than a package. Both are
    large modules and the claim is about a specific thing inside each."""
    from engine.tests.conformance.mandate_corpus import repo_root

    config = (repo_root() / "00-BOOK" / "tools" / "config.py").read_text(encoding="utf-8")
    assert (
        "CLASSIFY_RULES" in config
    ), "PRD-SELF/SELF-03 rests on config.py carrying CLASSIFY_RULES; it does not"
    book = (repo_root() / "00-BOOK" / "tools" / "ukb.py").read_text(encoding="utf-8")
    assert (
        "UNIVERSAL-ARTIFACT-REGISTRY.md" in book
    ), "PRD-SELF/SELF-04 rests on ukb.py writing the repository's own registry; it does not"


def test_the_near_misses_are_near_and_are_misses() -> None:
    """NON-VACUITY in both directions, which is the point of the tier.

    The named instrument must exist -- otherwise the row is plain absence and the
    explanation is decoration. And nothing may be named for the self-* capability itself,
    or the near miss is a hit that was overlooked.
    """
    from engine.tests.conformance.mandate_corpus import assert_named_by_nothing

    assert_homes_exist("PRD-SELF", {m: home for m, (home, _why) in SELF_NEAR_MISS.items()})
    for mandate, (_home, why) in SELF_NEAR_MISS.items():
        assert len(why) > 40, f"{mandate}: tiered a near miss without a stated reason"
    assert_named_by_nothing(
        "PRD-SELF",
        {"PRD-SELF/SELF-10": "self healing", "PRD-SELF/SELF-11": "self optimizing"},
    )


def test_self_optimizing_stays_a_genuine_gap() -> None:
    """One of the ten remaining CREATE concepts, and it stays one: unlike the tenures and
    the environments, nothing in any document forbids a platform optimising itself."""
    assert "PRD-SELF/SELF-11" in SELF_NEAR_MISS


# --- PRD-DISC — the Universal Discovery Framework -------------------------------
#
# Section 10: "The platform shall automatically discover" twelve things. Six have an
# instrument. Six do not, and five of those six are the outward-looking ones -- risk,
# opportunity, pattern, anomaly and emergent behaviour. MI-005 mandates three of the same
# five from the Master Index, so the gap is measured twice and the two suites are asserted
# to agree.

CONSTRUCT_DISCOVERY_INSTRUMENT = {
    "PRD-DISC/DISC-01": "engine/universal_discovery",  # Construct Discovery
    "PRD-DISC/DISC-02": "engine/uckp/resolution.py",  # Relationship Discovery
    "PRD-DISC/DISC-03": "engine/uckp/capabilities.py",  # Capability Discovery
    "PRD-DISC/DISC-04": "engine/context/resolution.py",  # Context Discovery
    "PRD-DISC/DISC-05": "engine/knowledge/integration/dependency.py",  # Dependency Discovery
    "PRD-DISC/DISC-06": "engine/knowledge/ukip/discovery.py",  # Knowledge Discovery
    "PRD-DISC/DISC-07": "engine/kernel/governance.py",  # Policy Discovery
}

CONSTRUCT_DISCOVERY_ABSENT = {
    "PRD-DISC/DISC-08": "risk",
    "PRD-DISC/DISC-09": "opportunity",
    "PRD-DISC/DISC-10": "pattern",
    "PRD-DISC/DISC-11": "anomaly",
    "PRD-DISC/DISC-12": "emergent",
}


def test_every_mandated_discovery_is_instrumented_or_absent() -> None:
    mandates = section("PRD-DISC")
    assert len(mandates) == 12, f"section 10 lists 12 discoveries, corpus has {len(mandates)}"
    assert_partitions(
        "PRD-DISC",
        mandates,
        CONSTRUCT_DISCOVERY_INSTRUMENT,
        CONSTRUCT_DISCOVERY_ABSENT,
    )


def test_every_discovery_instrument_is_tracked_and_distinct() -> None:
    assert_homes_exist("PRD-DISC", CONSTRUCT_DISCOVERY_INSTRUMENT)
    homes = list(CONSTRUCT_DISCOVERY_INSTRUMENT.values())
    duplicated = sorted({h for h in homes if homes.count(h) > 1})
    assert not duplicated, f"one instrument claimed for several discoveries: {duplicated}"


def test_the_absent_discoveries_are_performed_by_nothing() -> None:
    from engine.tests.conformance.mandate_corpus import assert_named_by_nothing

    assert_named_by_nothing("PRD-DISC", CONSTRUCT_DISCOVERY_ABSENT)


def test_the_platform_discovers_what_is_and_not_what_might_be() -> None:
    """The finding, asserted so it cannot quietly stop being true. Every discovery the
    platform performs is of something already present in the corpus; every one it does not
    perform is a judgement about what is not there -- a risk, an opportunity, an
    alternative, a pattern, an anomaly, an emergent behaviour."""
    outward = {"risk", "opportunity", "pattern", "anomaly", "emergent"}
    assert outward <= set(CONSTRUCT_DISCOVERY_ABSENT.values()), (
        "an outward-looking discovery now exists; the claim that this platform discovers "
        "what is and not what might be no longer holds"
    )


# --- PRD-PUB — the Universal Publication Framework ------------------------------
#
# "Automatically generate" eleven kinds of document. `intelligence/publication` declares
# twenty-three built-in FORMATS across eleven genres, each with its required sections and a
# renderer, so ten of the eleven are answered by a declared genre.
#
# TWO OF THESE ARE ON THE CREATE LIST AND SHOULD NOT BE. CAEM-001 dispositions `Whitepapers`
# and `Research Papers` as genuine greenfield gaps -- the only disposition that authorises
# new construction -- because it searched the document's spelling. The repository writes
# them `White Paper` and `Research Paper`, two words each, and declares both as built-in
# formats with academic section sets. Building either would be a second authoring of a
# format that already exists, void under UCKP-ART-03.

#: Publication kind -> the genre that produces it.
PUBLICATION_GENRE = {
    "PRD-PUB/PUB-01": "technical-article",  # Technical Documents
    "PRD-PUB/PUB-03": "standards",  # Specifications
    "PRD-PUB/PUB-04": "standards",  # Standards -- the same genre; see the test below
    "PRD-PUB/PUB-05": "white-paper",  # Whitepapers
    "PRD-PUB/PUB-06": "paper",  # Research Papers
    "PRD-PUB/PUB-07": "journal",  # Journal Publications
    "PRD-PUB/PUB-08": "patent",  # Patent Applications
    "PRD-PUB/PUB-11": "technical-article",  # Training Materials -- the Tutorial format
}

#: Produced outside the publication engine.
PUBLICATION_ELSEWHERE = {
    "PRD-PUB/PUB-02": "intelligence/realization/generators/architecture.py",  # Architecture Docs
    # Knowledge Artifacts
    "PRD-PUB/PUB-10": "00-BOOK/UCOS-BOOK-000000-UNIVERSAL-MASTER-KNOWLEDGE-BOOK.md",
}

#: No genre and no producer. A regulatory submission has a recipient and a filing format,
#: and the engine models neither.
PUBLICATION_ABSENT = {"PRD-PUB/PUB-09": "regulatory"}


def test_every_publication_kind_is_a_genre_produced_elsewhere_or_absent() -> None:
    mandates = section("PRD-PUB")
    assert len(mandates) == 11, f"section 14 lists 11 publication kinds, corpus has {len(mandates)}"
    assert_partitions(
        "PRD-PUB",
        mandates,
        PUBLICATION_GENRE,
        PUBLICATION_ELSEWHERE,
        PUBLICATION_ABSENT,
    )


def test_every_named_genre_is_declared_with_a_renderer_and_required_sections() -> None:
    """A genre with no renderer generates nothing, and a format with no required sections
    would accept an empty document."""
    from intelligence.publication.formats import BUILT_IN_FORMATS

    by_genre: dict[str, list[dict]] = {}
    for fmt in BUILT_IN_FORMATS:
        by_genre.setdefault(fmt["genre"], []).append(fmt)

    for mandate, genre in PUBLICATION_GENRE.items():
        assert genre in by_genre, f"{mandate}: no built-in format declares genre {genre!r}"
        for fmt in by_genre[genre]:
            assert fmt.get("renderer"), f"{mandate}: format {fmt['label']!r} has no renderer"
            assert fmt.get("required"), f"{mandate}: format {fmt['label']!r} requires no sections"


def test_whitepapers_and_research_papers_are_declared_formats_not_gaps() -> None:
    """The correction this binding exists to make.

    Both are dispositioned CREATE by CAEM-001 -- new construction -- because the search used
    the document's one-word spelling. The repository writes them as two words and declares
    each as a built-in format. This test names the exact labels, so if either is ever
    removed the CREATE disposition becomes true again and this assertion fails.
    """
    from intelligence.publication.formats import BUILT_IN_FORMATS

    labels = {fmt["label"] for fmt in BUILT_IN_FORMATS}
    assert (
        "White Paper" in labels
    ), "no White Paper format is declared; PRD-PUB/PUB-05 is a genuine gap after all"
    assert (
        "Research Paper" in labels
    ), "no Research Paper format is declared; PRD-PUB/PUB-06 is a genuine gap after all"
    mandates = section("PRD-PUB")
    assert mandates["PRD-PUB/PUB-05"] == "Whitepapers"
    assert mandates["PRD-PUB/PUB-06"] == "Research Papers"


def test_specifications_and_standards_share_a_genre_and_that_is_stated() -> None:
    """NON-VACUITY for the one genre claimed twice. The standards genre carries two formats
    -- a Standards Proposal and an RFC-style Memo -- so two mandates resolving to it is two
    documents, not one answer counted twice."""
    from intelligence.publication.formats import BUILT_IN_FORMATS

    claimed = list(PUBLICATION_GENRE.values())
    doubled = sorted({g for g in claimed if claimed.count(g) > 1})
    assert doubled == ["standards", "technical-article"], f"unexpected doubling: {doubled}"
    for genre in doubled:
        formats = [f for f in BUILT_IN_FORMATS if f["genre"] == genre]
        assert (
            len(formats) >= 2
        ), f"genre {genre!r} answers two mandates and declares only {len(formats)} format"


def test_the_absent_publication_kind_has_no_genre_and_no_producer() -> None:
    from engine.tests.conformance.mandate_corpus import assert_named_by_nothing
    from intelligence.publication.formats import BUILT_IN_FORMATS

    genres = {fmt["genre"] for fmt in BUILT_IN_FORMATS}
    for mandate, kind in PUBLICATION_ABSENT.items():
        assert not any(kind in genre for genre in genres), f"{mandate}: a {kind!r} genre now exists"
    assert_named_by_nothing("PRD-PUB", PUBLICATION_ABSENT)


def test_every_elsewhere_producer_is_tracked() -> None:
    assert_homes_exist("PRD-PUB", PUBLICATION_ELSEWHERE)


# --- PRD-NFR — the eleven non-functional requirements ---------------------------
#
# Each of the eleven carries a one-line claim in the document, and the claim is what makes
# it checkable: Scalability is "no architectural upper limit", Reliability is "deterministic
# operation", Portability is "technology agnostic". A module named for the quality proves
# nothing; the instrument has to make the CLAIM.
#
# PORTABILITY IS ON THE CREATE LIST AND SHOULD NOT BE. It is dispositioned new construction
# because nothing is named `portability`. The claim is "technology agnostic", and
# `engine/conformance` is the agnosticism conformance harness -- UAC-000001, which measures
# whether a contract discriminates between implementations and whose own docstring says
# "Nothing below names a technology, a language, a database or an interpreter."

#: Quality -> (the instrument, the claim it makes).
NFR_INSTRUMENT = {
    "PRD-NFR/NFR-01": ("engine/infinite_scope", "no architectural upper limit"),
    "PRD-NFR/NFR-03": ("engine/determinism", "deterministic operation"),
    "PRD-NFR/NFR-04": ("14-SECURITY/SECURITY-001-UNIVERSAL-SECURITY-CONSTITUTION.md", "zero trust"),
    "PRD-NFR/NFR-05": ("engine/conformance", "technology agnostic"),
    "PRD-NFR/NFR-09": ("platform/observability", "full-stack observability"),
    "PRD-NFR/NFR-10": ("engine/governance", "full governance"),
    "PRD-NFR/NFR-11": ("00-BOOK/DATA/canonical-observation-audit.json", "full audit trail"),
}

#: Quality -> the quality gate that refuses its violation. Stronger than an instrument: a
#: gate fails the build rather than being available to call.
NFR_GATE = {
    "PRD-NFR/NFR-07": "unknown-future-compatibility",  # Evolvability -- no terminal architecture
    "PRD-NFR/NFR-08": "no-finite-enumeration",  # Extensibility -- infinite extensibility
}

#: Availability's claim is "autonomous failover" and nothing fails over; `resilience` records
#: that a unit survived, which is not the same as one taking over. Interoperability repeats
#: the gap ARCH-VALID/VL-21 records -- nothing validates it either.
NFR_ABSENT = {
    "PRD-NFR/NFR-02": "failover",
    "PRD-NFR/NFR-06": "interoperability",
}


def test_every_non_functional_requirement_is_instrumented_gated_or_absent() -> None:
    mandates = section("PRD-NFR")
    assert len(mandates) == 11, f"section 21 states 11 qualities, corpus has {len(mandates)}"
    assert_partitions("PRD-NFR", mandates, NFR_INSTRUMENT, NFR_GATE, NFR_ABSENT)


def test_every_instrumented_quality_has_a_tracked_home_and_a_stated_claim() -> None:
    assert_homes_exist("PRD-NFR", {m: home for m, (home, _c) in NFR_INSTRUMENT.items()})
    homes = [home for home, _c in NFR_INSTRUMENT.values()]
    duplicated = sorted({h for h in homes if homes.count(h) > 1})
    assert not duplicated, f"one instrument claimed for several qualities: {duplicated}"
    for mandate, (_home, claim) in NFR_INSTRUMENT.items():
        assert len(claim) > 8, f"{mandate}: no claim stated, so nothing distinguishes the row"


def test_portability_is_answered_by_the_agnosticism_harness_and_is_not_a_gap() -> None:
    """The correction this binding makes.

    Portability is dispositioned CREATE because nothing is named `portability`. Its claim is
    "technology agnostic", and UAC-000001 measures exactly that: it reads a declared axis
    register and asks whether each contract DISCRIMINATES between implementations, refusing
    to name a technology anywhere in the process. Building a portability module would be a
    second authoring of a harness that already exists.
    """
    from engine.conformance.measure import REGISTER_PATH, load_register
    from engine.tests.conformance.mandate_corpus import repo_root

    register = load_register(REGISTER_PATH)
    assert register, "the agnosticism axis register is empty; the harness measures nothing"
    home, claim = NFR_INSTRUMENT["PRD-NFR/NFR-05"]
    assert home == "engine/conformance" and claim == "technology agnostic"
    source = (repo_root() / "engine" / "conformance" / "measure.py").read_text(encoding="utf-8")
    assert "names a technology" in source, (
        "the harness no longer states that it names no technology; the portability claim it "
        "answers rests on that property"
    )


def test_every_gated_quality_names_a_gate_that_passes() -> None:
    """A gate is stronger than an instrument: it refuses rather than being available."""
    from engine.kernel.compliance import quality_gates

    gates = {gate["id"]: gate for gate in quality_gates()["gates"]}
    for mandate, gate_id in NFR_GATE.items():
        assert gate_id in gates, f"{mandate}: no gate named {gate_id!r}"
        assert gates[gate_id]["passed"] is True, f"{mandate}: gate {gate_id!r} fails"
    assert not (set(NFR_GATE) & set(NFR_INSTRUMENT)), "a quality is both gated and instrumented"


def test_availability_and_interoperability_are_answered_by_nothing() -> None:
    """NON-VACUITY, and the distinction Availability needs.

    `infrastructure/resilience.py` exists and records that a unit survived. The claim is
    "autonomous failover" -- one unit taking over from another -- and nothing does that. A
    keyword sweep would have called this satisfied.
    """
    from engine.tests.conformance.mandate_corpus import assert_named_by_nothing

    assert_named_by_nothing("PRD-NFR", NFR_ABSENT)
    from engine.tests.conformance.test_mandates_arch import VALIDATION_ABSENT

    assert "interoperability" in set(
        VALIDATION_ABSENT.values()
    ), "interoperability validation now exists; PRD-NFR/NFR-06 may be answered"


# --- PRD-SEC — the Universal Security Framework ---------------------------------
#
# Eight principles the document calls MANDATORY. Three are stated by the Universal Security
# Constitution in its own words, one is realized by a module, and four are stated nowhere and
# realized by nothing.
#
# The four that are absent are not evenly absent. Continuous Verification and Post Quantum
# Readiness have no instrument but the substrate is not incapable of them -- verify.sh runs
# continuously and crypto agility exists. Autonomous Threat Detection and Autonomous Response
# require a threat model, and the substrate has none, so those two are absent at a deeper
# level: there is nothing for them to act on.

#: Principle -> the constitution that states it, by the phrase it uses.
SECURITY_CONSTITUTED = {
    "PRD-SEC/SEC-01": "Zero Trust",
    "PRD-SEC/SEC-02": "Least Privilege",
    "PRD-SEC/SEC-04": "Defense in Depth",
}

#: Principle -> the module that realizes it.
SECURITY_REALIZED = {
    "PRD-SEC/SEC-05": "platform/foundation/crypto_agility.py",  # Cryptographic Trust
}

#: Stated nowhere, realized by nothing, and the substrate could do it.
SECURITY_UNREALIZED = {
    "PRD-SEC/SEC-03": "continuous verification",
    "PRD-SEC/SEC-06": "post quantum readiness",
}

#: Absent at a deeper level: no threat model exists for these to act on.
SECURITY_NO_THREAT_MODEL = {
    "PRD-SEC/SEC-07": "threat detection",
    "PRD-SEC/SEC-08": "autonomous response",
}

SECURITY_CONSTITUTION = "14-SECURITY/SECURITY-001-UNIVERSAL-SECURITY-CONSTITUTION.md"


def test_every_security_principle_is_constituted_realized_or_absent() -> None:
    mandates = section("PRD-SEC")
    assert len(mandates) == 8, f"section 17 states 8 principles, corpus has {len(mandates)}"
    assert_partitions(
        "PRD-SEC",
        mandates,
        SECURITY_CONSTITUTED,
        SECURITY_REALIZED,
        SECURITY_UNREALIZED,
        SECURITY_NO_THREAT_MODEL,
    )


def test_every_constituted_principle_is_stated_in_the_constitution_verbatim() -> None:
    """A principle the constitution does not name is not constituted by it. Each row carries
    the exact phrase, so a rewording breaks the binding instead of passing."""
    from engine.tests.conformance.mandate_corpus import repo_root

    text = (repo_root() / SECURITY_CONSTITUTION).read_text(encoding="utf-8")
    for mandate, phrase in SECURITY_CONSTITUTED.items():
        assert phrase in text, (
            f"{mandate}: the security constitution no longer states {phrase!r}; this "
            "principle is constituted by nothing"
        )


def test_cryptographic_trust_is_realized_by_an_agility_module_not_an_algorithm() -> None:
    """NON-VACUITY, and the reason this row is realized rather than constituted.

    Naming an algorithm would be the technology assumption UAKP-IND/ID-03 forbids. Crypto
    agility is the constitutional form of cryptographic trust: algorithm-tagged digests and
    witnessed rollover, so identity survives an algorithm breaking.
    """
    from engine.tests.conformance.mandate_corpus import repo_root

    home = SECURITY_REALIZED["PRD-SEC/SEC-05"]
    # Whitespace-normalised: the claim is a sentence in a wrapped docstring, so matching the
    # raw text would depend on where the line happens to break.
    source = " ".join((repo_root() / home).read_text(encoding="utf-8").split())
    assert "rollover" in source, f"{home} no longer provides algorithm rollover"
    assert "identity is opaque and survives algorithm breakage" in source, (
        f"{home} no longer claims identity survives algorithm breakage, which is what makes "
        "it cryptographic TRUST rather than a cryptography module"
    )


def test_the_unrealized_principles_are_stated_by_nothing_and_built_by_nothing() -> None:
    from engine.tests.conformance.mandate_corpus import assert_named_by_nothing, repo_root

    text = (repo_root() / SECURITY_CONSTITUTION).read_text(encoding="utf-8").lower()
    for mandate, principle in {**SECURITY_UNREALIZED, **SECURITY_NO_THREAT_MODEL}.items():
        assert principle not in text, (
            f"{mandate}: the security constitution now states {principle!r} and this row "
            "belongs in the constituted tier"
        )
    assert_named_by_nothing("PRD-SEC", SECURITY_UNREALIZED)
    assert_named_by_nothing("PRD-SEC", SECURITY_NO_THREAT_MODEL)


def test_the_autonomous_security_principles_have_no_threat_model_to_act_on() -> None:
    """The distinction between the two absent tiers, asserted.

    Detection and response are not two missing modules; they are two operations with no
    subject. ARCH-OPF records Security Monitoring unbuilt and PRD-DISC records Risk
    Discovery absent, so nothing produces the signal either would consume. If a risk or
    threat surface ever lands, these become ordinary gaps.
    """
    from engine.tests.conformance.test_mandates_arch import OPERATION_UNBUILT

    assert "ARCH-OPF/OF-12" in OPERATION_UNBUILT, (
        "security monitoring now exists; the autonomous security principles have a signal "
        "to act on and are ordinary gaps rather than subjectless ones"
    )
    assert "risk" in set(
        CONSTRUCT_DISCOVERY_ABSENT.values()
    ), "risk discovery now exists; the same re-tiering applies"


# --- PRD-COMP — the nine modes of composition -----------------------------------
#
# "Composition must support" nine modes. They are not nine composers: they are nine things
# that can DRIVE one composition, and the repository's autonomous composer is driven by
# several of them at once. So each row names the driver rather than a module, and the driver
# has to be visible in the composer's own signature or in a module composition reaches.
#
# Six are driven. Three are not, and they share a shape: Static, Dynamic and Event Driven
# are all about WHEN composition happens. The substrate composes when asked and has no
# notion of composition bound to declaration time, to runtime change, or to an event.

#: Mode -> (the module that drives it, the symbol that shows the driver).
COMPOSITION_DRIVER = {
    # Runtime Composition
    "PRD-COMP/COMP-03": ("engine/runtime/orchestration.py", ""),
    # Intent Driven -- the composer's entry point takes an ArtifactIntent
    "PRD-COMP/COMP-05": ("engine/knowledge/integration/contracts.py", "ArtifactIntent"),
    # Policy Driven
    "PRD-COMP/COMP-06": ("engine/kernel/governance.py", "Policy"),
    # Knowledge Driven -- the composer is constructed over a KnowledgeBase
    "PRD-COMP/COMP-07": ("engine/knowledge/integration/composition.py", "AutonomousComposer"),
    # Autonomous
    "PRD-COMP/COMP-08": ("engine/knowledge/integration/composition.py", "AutonomousComposer"),
    # Recursive
    "PRD-COMP/COMP-09": ("engine/recursive_knowledge/composition.py", ""),
}

#: Undriven, and all three are about WHEN.
COMPOSITION_UNDRIVEN = {
    "PRD-COMP/COMP-01": "static composition",
    "PRD-COMP/COMP-02": "dynamic composition",
    "PRD-COMP/COMP-04": "event driven composition",
}


def test_every_composition_mode_is_driven_or_undriven() -> None:
    mandates = section("PRD-COMP")
    assert len(mandates) == 9, f"section 8 states 9 composition modes, corpus has {len(mandates)}"
    assert_partitions("PRD-COMP", mandates, COMPOSITION_DRIVER, COMPOSITION_UNDRIVEN)


def test_every_driven_mode_names_a_module_and_a_symbol_it_defines() -> None:
    """A driver that is a path is a guess; a driver that is a named class in that path is a
    driver. Where no symbol is named the module itself is the driver."""
    import ast

    from engine.tests.conformance.mandate_corpus import repo_root

    assert_homes_exist("PRD-COMP", {m: home for m, (home, _s) in COMPOSITION_DRIVER.items()})
    for mandate, (home, symbol) in COMPOSITION_DRIVER.items():
        if not symbol:
            continue
        tree = ast.parse((repo_root() / home).read_text(encoding="utf-8"))
        defined = {n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)}
        assert symbol in defined, f"{mandate}: {home} defines no {symbol!r}"


def test_the_composer_is_driven_by_intent_and_knowledge_at_once() -> None:
    """NON-VACUITY for the two rows that share a module. Intent Driven and Knowledge Driven
    are not the same claim: the composer is CONSTRUCTED over a knowledge base and CALLED
    with an intent, so both drivers are visible in its own signature."""
    import inspect

    from engine.knowledge.integration.composition import AutonomousComposer

    init = inspect.signature(AutonomousComposer.__init__)
    assert (
        "base" in init.parameters
    ), "the composer no longer takes a knowledge base; the Knowledge Driven row rests on it"
    source = inspect.getsource(AutonomousComposer)
    assert (
        "ArtifactIntent" in source
    ), "the composer no longer takes an ArtifactIntent; the Intent Driven row rests on it"


def test_the_undriven_modes_are_all_about_when_composition_happens() -> None:
    """The finding, asserted rather than described. Static, Dynamic and Event Driven all
    answer WHEN; the substrate composes when asked. If a scheduler or an event-driven
    composer ever lands, this characterisation has to be rewritten."""
    from engine.tests.conformance.mandate_corpus import assert_named_by_nothing, tracked

    assert set(COMPOSITION_UNDRIVEN) == {
        "PRD-COMP/COMP-01",
        "PRD-COMP/COMP-02",
        "PRD-COMP/COMP-04",
    }
    assert_named_by_nothing("PRD-COMP", COMPOSITION_UNDRIVEN)
    event_composers = [
        path
        for path in tracked()
        if path.endswith(".py")
        and "/tests/" not in path
        and "event" in path.lower()
        and "compos" in path.lower()
    ]
    assert (
        not event_composers
    ), f"an event-driven composer now exists: {event_composers}; COMP-04 is driven"


# --- PRD-INT — the Universal Intelligence Framework -----------------------------
#
# Seven intelligence forms under one rule: "No intelligence assumptions." This is the
# least-answered section in the corpus, and the repository already knows it -- the kernel
# suite declares three mandates UNCOVERED for exactly this reason, in its own words: "no
# AI-model token and no AI-model category; nothing refuses one" and "UNKNOWN_CATEGORIES
# carries no intelligence-model category".
#
# One form is refused: `human` is among the eighteen tokens the kernel will not seed, so
# Human Intelligence cannot be hard-coded. The other six are neither refused nor
# represented, which means the framework's rule is unenforced: nothing stops an
# intelligence assumption being seeded tomorrow.

#: Form -> the token the kernel refuses to seed.
INTELLIGENCE_REFUSED = {"PRD-INT/INT-01": "human"}  # Human Intelligence

#: Forms the kernel suite has already declared UNCOVERED, by the mandate that records it.
INTELLIGENCE_DECLARED_UNCOVERED = {
    "PRD-INT/INT-03": "UAKP-IND/ID-06",  # AI Intelligence
    "PRD-INT/INT-06": "PRD-SC/SC-07",  # Future Intelligence Models
}

#: Neither refused, represented, nor formally recorded as uncovered.
INTELLIGENCE_UNHELD = {
    "PRD-INT/INT-02": "machine intelligence",
    "PRD-INT/INT-04": "collective intelligence",
    "PRD-INT/INT-05": "synthetic intelligence",
    "PRD-INT/INT-07": "unknown intelligence",
}


def test_every_intelligence_form_is_refused_declared_uncovered_or_unheld() -> None:
    mandates = section("PRD-INT")
    assert len(mandates) == 7, f"section 12 states 7 forms, corpus has {len(mandates)}"
    assert_partitions(
        "PRD-INT",
        mandates,
        INTELLIGENCE_REFUSED,
        INTELLIGENCE_DECLARED_UNCOVERED,
        INTELLIGENCE_UNHELD,
    )


def test_human_intelligence_is_refused_as_a_seedable_category() -> None:
    from engine.kernel.compliance import PROHIBITED_TOKENS
    from engine.kernel.seed import FOUNDING_METATYPES

    for mandate, token in INTELLIGENCE_REFUSED.items():
        assert token in PROHIBITED_TOKENS, (
            f"{mandate}: `{token}` is no longer refused, so a human-intelligence model could "
            "be seeded and the framework's rule would be unenforced for it too"
        )
        assert token not in {k.lower() for k, _n, _d in FOUNDING_METATYPES}


def test_the_uncovered_forms_are_the_ones_the_kernel_suite_already_records() -> None:
    """The join. These two are not new findings -- they are the same holes the kernel suite
    declares UNCOVERED, reached from a second document. If either is ever bound there, it
    stops being uncovered here."""
    from engine.tests.kernel.test_compliance import (
        BOUND_TO_GATE,
        BOUND_TO_PROHIBITED_TOKEN,
        BOUND_TO_UNKNOWN_CATEGORY,
        UNCOVERED,
    )

    bound = set(BOUND_TO_PROHIBITED_TOKEN) | set(BOUND_TO_UNKNOWN_CATEGORY) | set(BOUND_TO_GATE)
    for mandate, recorded in INTELLIGENCE_DECLARED_UNCOVERED.items():
        assert (
            recorded in UNCOVERED
        ), f"{mandate}: {recorded} is no longer declared uncovered by the kernel suite"
        assert recorded not in bound, f"{mandate}: {recorded} is now bound and is covered"
        assert "intelligence" in UNCOVERED[recorded] or "AI" in UNCOVERED[recorded]


def test_no_intelligence_category_exists_so_the_rule_is_unenforced() -> None:
    """The finding, and the sharpest form of it.

    "No intelligence assumptions" is a negative mandate, and a negative mandate is enforced
    by a refusal. UNKNOWN_CATEGORIES represents eleven unknowns and none of them is an
    intelligence model; PROHIBITED_TOKENS refuses eighteen and none is an AI token. So
    nothing in the kernel would object if an intelligence model were seeded tomorrow.
    """
    from engine.kernel.compliance import PROHIBITED_TOKENS, UNKNOWN_CATEGORIES

    categories = {key.lower() for key, _i, _a in UNKNOWN_CATEGORIES}
    assert not [c for c in categories if "intelligence" in c], (
        "an intelligence-model category now exists; the framework's rule is enforced and "
        "PRD-SC/SC-07 is no longer uncovered"
    )
    assert (
        "ai" not in PROHIBITED_TOKENS
    ), "an AI token is now refused; UAKP-IND/ID-06 is no longer uncovered"


def test_the_unheld_forms_are_named_by_nothing() -> None:
    from engine.tests.conformance.mandate_corpus import assert_named_by_nothing

    assert_named_by_nothing("PRD-INT", INTELLIGENCE_UNHELD)


# --- PRD-GOV — the Universal Governance Framework -------------------------------
#
# Ten things governance includes, and one sentence under them that is easy to read past:
# "Governance itself must be governable." All ten are located, which would be the whole
# binding -- except that the closing sentence is the harder claim, and this repository
# satisfies it in a specific, checkable way.
#
# UCOS-CAA-001 is the register of which instrument holds which standing. It carries a
# top-level `authority` of its own, and therefore appears in its own claim scan; CAA-INV-02
# is the invariant that refuses an authority-carrying register that is not bound. Its own
# words: "An alignment register exempt from the rule it enforces is the first parallel
# authority anyone would build, so it is measured by CAA-INV-02". That is governance
# governing itself, and it is what the closing sentence asks for.

GOVERNANCE_ELEMENT = {
    "PRD-GOV/GOV-01": "engine/kernel/governance.py",  # Policy
    "PRD-GOV/GOV-02": "engine/uckp/governance.py",  # Rule
    "PRD-GOV/GOV-03": "engine/uckp/law.py",  # Law
    "PRD-GOV/GOV-04": "00-CEP/CEP-001-CONSTITUTIONAL-ENGINEERING-CONSTITUTION.md",  # Constitution
    "PRD-GOV/GOV-05": "engine/kernel/compliance.py",  # Compliance
    "PRD-GOV/GOV-06": "engine/certification",  # Certification
    "PRD-GOV/GOV-07": "engine/enforcement_closure",  # Enforcement
    "PRD-GOV/GOV-08": "00-BOOK/DATA/canonical-observation-audit.json",  # Audit
    "PRD-GOV/GOV-09": "00-BOOK/REGISTRIES/CHANGE-VERSION-LINEAGE-REGISTRY.md",  # Lineage
    "PRD-GOV/GOV-10": "00-MASTER/UCOS-UCAF-001/ucaf.json",  # Accountability
}


def test_every_governance_element_is_located_and_distinct() -> None:
    mandates = section("PRD-GOV")
    assert len(mandates) == 10, f"section 9 lists 10 elements, corpus has {len(mandates)}"
    assert_partitions("PRD-GOV", mandates, GOVERNANCE_ELEMENT)
    assert_homes_exist("PRD-GOV", GOVERNANCE_ELEMENT)
    homes = list(GOVERNANCE_ELEMENT.values())
    duplicated = sorted({h for h in homes if homes.count(h) > 1})
    assert not duplicated, f"one instrument claimed for several elements: {duplicated}"


def test_policy_and_rule_are_two_instruments_and_not_one() -> None:
    """NON-VACUITY for the pair most likely to collapse. The document lists Policy and Rule
    as separate elements; if one module carried both, one of them would be unlocated."""
    import ast

    from engine.tests.conformance.mandate_corpus import repo_root

    policy_home = GOVERNANCE_ELEMENT["PRD-GOV/GOV-01"]
    rule_home = GOVERNANCE_ELEMENT["PRD-GOV/GOV-02"]
    assert policy_home != rule_home
    for home in (policy_home, rule_home):
        tree = ast.parse((repo_root() / home).read_text(encoding="utf-8"))
        assert any(
            isinstance(n, ast.ClassDef) for n in ast.walk(tree)
        ), f"{home} defines no class, so it carries no governance element"


def test_governance_governs_itself() -> None:
    """The closing sentence, which is the section's real claim.

    The alignment register carries a top-level `authority`, is bound as a subordinate
    instrument of the root law, and binds ITSELF -- it appears in its own subordinate list
    rather than sitting outside the rule it enforces. A register exempt from its own rule is
    the first parallel authority anyone would build.
    """
    import json

    from engine.tests.conformance.mandate_corpus import repo_root

    path = "00-BOOK/DATA/constitutional-authority-alignment.json"
    alignment = json.loads((repo_root() / path).read_text(encoding="utf-8"))

    assert alignment.get("authority"), f"{path} carries no top-level authority"
    bound = {entry["id"]: entry for entry in alignment["subordinate_instruments"]}
    assert "UCOS-CAA-001" in bound, (
        "the alignment register no longer binds itself; governance is no longer governable "
        "by the mechanism this section rests on"
    )
    assert bound["UCOS-CAA-001"]["instrument"] == path
    assert bound["UCOS-CAA-001"]["may_never_own"], (
        "the self-binding no longer declares what it may never own, which is the half that "
        "stops it becoming an authority of its own"
    )


def test_the_root_law_is_above_the_register_that_records_standings() -> None:
    """NON-VACUITY for the self-binding. Self-governance is only lawful if something is
    still above it: the register derives UNDER the root law and confers no authority."""
    import json

    from engine.tests.conformance.mandate_corpus import repo_root
    from engine.uckp.law import ROOT_LAW

    alignment = json.loads(
        (repo_root() / "00-BOOK" / "DATA" / "constitutional-authority-alignment.json").read_text(
            encoding="utf-8"
        )
    )
    supreme = alignment.get("supreme_authority")
    assert supreme, "the alignment register names no supreme authority"
    assert ROOT_LAW.law_id in json.dumps(supreme), (
        f"the register's supreme authority is not {ROOT_LAW.law_id}; the self-binding would "
        "make it answerable to nothing"
    )


# --- PRD-TWIN — the Universal Digital Twin Framework ----------------------------
#
# "Anything may possess" six kinds of twin, and "No restriction on twin types." One kind
# exists, one is architecture without an instance, and four are absent -- so the closing
# rule is true by vacuity rather than by design: nothing restricts twin types because
# nothing produces more than one.
#
# The operational twin that does exist carries its own limit, and CAEM-001 recorded it
# before this suite did: GAP-6, "twin subject set narrow, fixture-fed", carried by
# WP-UCDA-012. Eight subjects and fifteen signals, sourced from a fixed timestamp. That is
# recorded as part of the row rather than left for a reader to discover.

#: Twin -> the instrument that produces it.
TWIN_PRODUCED = {"PRD-TWIN/TWIN-02": "00-BOOK/DATA/twin.json"}  # Operational Twin

#: Architecture without an instance. UMB-002 specifies the twin; nothing emits this kind.
TWIN_SPECIFIED_ONLY = {
    "PRD-TWIN/TWIN-01": "00-BOOK/MASTER-BOOK/UMB-002-DIGITAL-TWIN-ARCHITECTURE.md",
}

TWIN_ABSENT = {
    "PRD-TWIN/TWIN-03": "behavioral twin",
    "PRD-TWIN/TWIN-04": "predictive twin",
    "PRD-TWIN/TWIN-05": "simulation twin",
    "PRD-TWIN/TWIN-06": "evolution twin",
}


def test_every_twin_kind_is_produced_specified_or_absent() -> None:
    mandates = section("PRD-TWIN")
    assert len(mandates) == 6, f"section 18 states 6 twin kinds, corpus has {len(mandates)}"
    assert_partitions("PRD-TWIN", mandates, TWIN_PRODUCED, TWIN_SPECIFIED_ONLY, TWIN_ABSENT)
    assert_homes_exist("PRD-TWIN", TWIN_PRODUCED)
    assert_homes_exist("PRD-TWIN", TWIN_SPECIFIED_ONLY)


def test_the_operational_twin_carries_the_narrow_subject_set_caem_recorded() -> None:
    """The row and its limit together. CAEM-001 GAP-6 records the twin subject set as narrow
    and fixture-fed; this asserts the shape of that limit so the row cannot read as a fully
    realized operational twin, and so the assertion fails if the twin ever grows.
    """
    import json

    from engine.tests.conformance.mandate_corpus import repo_root

    twin = json.loads((repo_root() / TWIN_PRODUCED["PRD-TWIN/TWIN-02"]).read_text(encoding="utf-8"))
    assert twin["subject_count"] < 100, (
        f"the twin now covers {twin['subject_count']} subjects; CAEM-001 GAP-6 recorded the "
        "set as narrow and that limit no longer holds -- re-read the row"
    )
    assert twin["dimensions"], "the twin declares no dimensions, so it records no state"
    assert "operational" in twin["dimensions"], (
        "the twin no longer carries an operational dimension, which is what makes it the "
        "OPERATIONAL twin rather than some other kind"
    )


def test_the_specified_twin_is_architecture_and_not_an_instance() -> None:
    """NON-VACUITY for the specified tier. A document is a specification; if a producer ever
    emits representation twins, this row moves up."""
    home = TWIN_SPECIFIED_ONLY["PRD-TWIN/TWIN-01"]
    assert home.endswith(".md"), f"{home} is not a document, so this row is not specification"
    from engine.tests.conformance.mandate_corpus import assert_named_by_nothing

    assert_named_by_nothing("PRD-TWIN", {"PRD-TWIN/TWIN-01": "representation twin"})


def test_no_restriction_on_twin_types_is_true_by_vacuity() -> None:
    """The section's closing rule, read honestly.

    "No restriction on twin types" is satisfied -- nothing restricts them. It is satisfied
    because nothing produces more than one kind, which is not the same as being satisfied by
    design. If a second producer ever lands, this assertion fails and the rule starts being
    a real claim about an extensible twin set.
    """
    from engine.tests.conformance.mandate_corpus import assert_named_by_nothing

    assert len(TWIN_PRODUCED) == 1, (
        "more than one twin kind is now produced; 'no restriction on twin types' is a claim "
        "about a real set and must be proven the way the other open sets are"
    )
    assert_named_by_nothing("PRD-TWIN", TWIN_ABSENT)


# --- PRD-KN — the Universal Knowledge Framework ---------------------------------
#
# Nine stages of the knowledge lifecycle. Seven have an instrument in the knowledge plane;
# two do not, and the pair is worth naming: Capture and Verification.
#
# Verification's absence is the same shape the maturity lattice shows. UAKP-MAT records M5
# as `VALIDATED-OR-VERIFIED`, one level for two stages; here the knowledge plane has
# `validation.py` and `certification.py` and no verification module at all. Two documents,
# one missing distinction between checking a thing against its shape and checking it
# against reality.

KNOWLEDGE_STAGE = {
    "PRD-KN/KN-02": "platform/universal_assimilation",  # Knowledge Ingestion
    "PRD-KN/KN-03": "engine/knowledge/ukip/assimilation.py",  # Knowledge Assimilation
    "PRD-KN/KN-04": "engine/knowledge/ukip/classification.py",  # Knowledge Classification
    "PRD-KN/KN-05": "engine/knowledge/ukip/validation.py",  # Knowledge Validation
    "PRD-KN/KN-07": "engine/knowledge/ukip/certification.py",  # Knowledge Certification
    "PRD-KN/KN-08": "engine/uckp/evolution.py",  # Knowledge Evolution
    "PRD-KN/KN-09": "engine/registry/universal/records.py",  # Knowledge Retirement
}

KNOWLEDGE_ABSENT = {
    "PRD-KN/KN-01": "knowledge capture",
    "PRD-KN/KN-06": "knowledge verification",
}


def test_every_knowledge_stage_is_instrumented_or_absent() -> None:
    mandates = section("PRD-KN")
    assert len(mandates) == 9, f"section 11 states 9 stages, corpus has {len(mandates)}"
    assert_partitions("PRD-KN", mandates, KNOWLEDGE_STAGE, KNOWLEDGE_ABSENT)
    assert_homes_exist("PRD-KN", KNOWLEDGE_STAGE)


def test_the_knowledge_plane_validates_and_certifies_and_does_not_verify() -> None:
    """NON-VACUITY, and the finding. The knowledge plane has a validation module and a
    certification module beside each other and no verification module -- so the stage
    between them has no instrument. If one ever appears, this row moves."""
    from engine.tests.conformance.mandate_corpus import tracked

    ukip = [p for p in tracked() if p.startswith("engine/knowledge/ukip/") and p.endswith(".py")]
    assert "engine/knowledge/ukip/validation.py" in ukip
    assert "engine/knowledge/ukip/certification.py" in ukip
    assert "engine/knowledge/ukip/verification.py" not in ukip, (
        "the knowledge plane now verifies; PRD-KN/KN-06 has an instrument and must be " "re-tiered"
    )


def test_the_missing_verification_is_the_same_distinction_the_lattice_collapses() -> None:
    """Two documents, one missing distinction. The maturity lattice names M5
    `VALIDATED-OR-VERIFIED` -- one level for two stages -- and the knowledge plane has no
    verification module. Asserted together so the pair reads as one finding."""
    from engine.tests.conformance.test_mandates_uakp import MATURITY_COLLAPSED

    assert "UAKP-MAT/MT-07" in MATURITY_COLLAPSED, (
        "the lattice now separates validated from verified; the knowledge plane's missing "
        "verification is a lone gap rather than half of one finding"
    )
    assert "PRD-KN/KN-06" in KNOWLEDGE_ABSENT


def test_the_absent_knowledge_stages_are_named_by_nothing() -> None:
    from engine.tests.conformance.mandate_corpus import assert_named_by_nothing

    assert_named_by_nothing("PRD-KN", KNOWLEDGE_ABSENT)


# --- PRD-OBS — the Universal Observability Framework ----------------------------
#
# Seven things the framework must support. Five exist, two do not, and Traces needs a
# distinction this suite has already drawn from the other side.
#
# ARCH-OPF/OF-10 records Tracing as UNBUILT because nothing correlates spans across a
# request. `platform/observability/traces.py` is still a real answer HERE, because the two
# sections ask different questions: the operation fabric asks whether the platform TRACES,
# and the observability framework asks whether a trace is a thing it can observe. One
# module, two verdicts, and both are correct.

OBSERVABILITY_SIGNAL = {
    "PRD-OBS/OBS-01": "platform/observability/metrics.py",  # Metrics
    "PRD-OBS/OBS-02": "platform/foundation/events.py",  # Events
    "PRD-OBS/OBS-03": "platform/observability/logs.py",  # Logs
    "PRD-OBS/OBS-04": "platform/observability/traces.py",  # Traces
    "PRD-OBS/OBS-05": "00-BOOK/DATA/signals.json",  # Signals
}

#: Absent, and both are inferences rather than records. Everything the framework observes is
#: something that happened; nothing it observes is something inferred.
OBSERVABILITY_ABSENT = {
    "PRD-OBS/OBS-06": "predictions",
    "PRD-OBS/OBS-07": "anomalies",
}


def test_every_observable_is_present_or_absent() -> None:
    mandates = section("PRD-OBS")
    assert len(mandates) == 7, f"section 16 states 7 observables, corpus has {len(mandates)}"
    assert_partitions("PRD-OBS", mandates, OBSERVABILITY_SIGNAL, OBSERVABILITY_ABSENT)
    assert_homes_exist("PRD-OBS", OBSERVABILITY_SIGNAL)
    homes = list(OBSERVABILITY_SIGNAL.values())
    assert len(set(homes)) == len(homes), "one module claimed for two observables"


def test_traces_are_observable_here_and_unproduced_in_the_operation_fabric() -> None:
    """One module, two verdicts, both correct -- and the reason is stated so neither reads
    as a contradiction. The operation fabric asks whether the platform TRACES; this section
    asks whether a trace is a thing it can observe."""
    from engine.tests.conformance.test_mandates_arch import OPERATION_UNBUILT

    assert (
        "ARCH-OPF/OF-10" in OPERATION_UNBUILT
    ), "tracing is now produced; the two verdicts have converged and this note is stale"
    assert OBSERVABILITY_SIGNAL["PRD-OBS/OBS-04"] == "platform/observability/traces.py"


def test_the_framework_observes_what_happened_and_not_what_is_inferred() -> None:
    """The finding. Metrics, events, logs, traces and signals are all records of something
    that occurred. Predictions and anomalies are inferences, and the framework makes
    neither -- the same hole PRD-DISC records as Anomaly Discovery."""
    from engine.tests.conformance.mandate_corpus import assert_named_by_nothing

    assert_named_by_nothing("PRD-OBS", OBSERVABILITY_ABSENT)
    assert "anomaly" in set(
        CONSTRUCT_DISCOVERY_ABSENT.values()
    ), "anomaly discovery now exists; the observability framework may infer after all"


# --- PRD-P — the ten constitutional principles ----------------------------------
#
# Three of the ten are negative -- No Terminal Ontology, Taxonomy, Architecture -- and are
# bound in the kernel suite to gates that refuse the violation. The seven below are the
# positive ones, and four of them have the strongest answer available in this repository:
# they are FACETS. "Everything must be observable / traceable / certifiable / evolvable" is
# satisfied by every object carrying the facet, not by a module that could be called.
#
# One is absent, and it is the same absence PRD-ECON records: Universal Monetization has no
# instrument because the settlement chain does not exist.

#: Principle -> the facet that makes it true of every object.
PRINCIPLE_FACET = {
    "PRD-P/P-006": "observer-context",  # Universal Observability
    "PRD-P/P-007": "traceability",  # Universal Traceability
    "PRD-P/P-008": "certification",  # Universal Certifiability
    "PRD-P/P-010": "evolution-history",  # Universal Evolvability
}

#: Principle -> the instrument that carries it.
PRINCIPLE_INSTRUMENT = {
    "PRD-P/P-004": "engine/infinite_scope",  # Infinite Composition
    "PRD-P/P-005": "engine/constitution/gateway.py",  # Constitutional Governance
}

#: Bound in the kernel suite, to a gate that refuses the violation.
PRINCIPLE_GATED_ELSEWHERE = {
    "PRD-P/P-001": "no-closed-registries",
    "PRD-P/P-002": "no-finite-enumeration",
    "PRD-P/P-003": "unknown-future-compatibility",
}

PRINCIPLE_ABSENT = {"PRD-P/P-009": "monetization"}  # Universal Monetization


def test_every_constitutional_principle_is_a_facet_instrumented_gated_or_absent() -> None:
    mandates = section("PRD-P")
    assert len(mandates) == 10, f"section 4 states 10 principles, corpus has {len(mandates)}"
    assert_partitions(
        "PRD-P",
        mandates,
        PRINCIPLE_FACET,
        PRINCIPLE_INSTRUMENT,
        PRINCIPLE_GATED_ELSEWHERE,
        PRINCIPLE_ABSENT,
    )


def test_the_four_universal_principles_are_carried_by_every_object() -> None:
    """The strongest answer available: not a module that could be called, but a question
    every object must be able to answer about itself."""
    import dataclasses

    from engine.uckp.facets import REQUIRED_FACETS, Facet
    from engine.uckp.ucko import UniversalConstitutionalKnowledgeObject as UCKO

    fields = {f.name for f in dataclasses.fields(UCKO)}
    for mandate, value in PRINCIPLE_FACET.items():
        facet = Facet.coerce(value)
        assert facet in REQUIRED_FACETS, f"{mandate}: {value!r} is not a required facet"
        assert facet.attribute in fields, (
            f"{mandate}: no UCKO field carries {value!r}, so the principle is not true of "
            "every object"
        )
    values = list(PRINCIPLE_FACET.values())
    assert len(values) == len(set(values)), "one facet claimed by two principles"


def test_the_negative_principles_stay_bound_in_the_kernel_suite() -> None:
    """Corpus search cannot decide a negative. These three are bound where they can be
    decided -- to a gate that fails the build -- and this suite asserts the binding rather
    than restating it."""
    from engine.kernel.compliance import quality_gates
    from engine.tests.kernel.test_compliance import BOUND_TO_GATE

    gates = {gate["id"]: gate for gate in quality_gates()["gates"]}
    for mandate, gate_id in PRINCIPLE_GATED_ELSEWHERE.items():
        assert (
            BOUND_TO_GATE.get(mandate) == gate_id
        ), f"{mandate}: the kernel suite no longer binds this to {gate_id!r}"
        assert gates[gate_id]["passed"] is True, f"{mandate}: gate {gate_id!r} fails"


def test_universal_monetization_is_the_settlement_chain_gap_stated_as_a_principle() -> None:
    """The one absent principle, and it is not a lone gap.

    PRD-ECON records Revenue, Billing, Settlement and Taxation all absent. "Everything must
    be monetizable" is that same hole stated as a principle, so the two are asserted
    together -- and if the chain ever lands, this principle is answered by it.
    """
    from engine.tests.conformance.mandate_corpus import assert_named_by_nothing

    assert {"revenue", "billing", "settlement", "taxation"} <= set(
        ECONOMIC_FACULTY_ABSENT.values()
    ), "the settlement chain has landed; P-009 may be answered and must be re-tiered"
    assert_named_by_nothing("PRD-P", PRINCIPLE_ABSENT)


# --- PRD-FR / PRD-CERT — the last of the PRD -------------------------------------
#
# Section 6's thirteen fundamental requirements are the PRD's own summary of everything
# below it, so eleven of them resolve through the sections that own them rather than being
# re-located. Two do not: Representation is the object model, and Monetization is the one
# fundamental requirement with no instrument -- the settlement chain again, stated at the
# top of the document this time.

FUNDAMENTAL_VIA_SECTION = {
    "PRD-FR/FR-01": "PRD-ADM",  # Admission -- the nine admission steps
    "PRD-FR/FR-13": "PRD-KN",  # Retirement -- knowledge retirement owns the lifecycle end
}

FUNDAMENTAL_INSTRUMENT = {
    "PRD-FR/FR-02": "engine/uckp/ucko.py",  # Representation
}

FUNDAMENTAL_ABSENT = {"PRD-FR/FR-10": "monetization"}  # Monetization

#: Certification renewal and revocation. A certification that cannot be withdrawn is a
#: certification nothing can correct, and neither operation exists.
CERTIFICATION_LIFECYCLE_ABSENT = {
    "PRD-CERT/CERT-05": "renewal",
    "PRD-CERT/CERT-06": "revocation",
}


def test_the_last_prd_mandates_are_joined_instrumented_or_absent() -> None:
    mandates: dict[str, str] = {}
    for name in ("PRD-FR", "PRD-CERT"):
        mandates.update(section(name))
    covered = {
        **FUNDAMENTAL_VIA_SECTION,
        **FUNDAMENTAL_INSTRUMENT,
        **FUNDAMENTAL_ABSENT,
        **CERTIFICATION_LIFECYCLE_ABSENT,
    }
    foreign = sorted(set(covered) - set(mandates))
    assert not foreign, f"tiered identifiers that are not PRD mandates: {foreign}"
    assert_homes_exist("PRD-last", FUNDAMENTAL_INSTRUMENT)


def test_admission_and_retirement_resolve_through_the_sections_that_own_them() -> None:
    """The join. Section 6 summarises the document; re-locating its rows here would author
    each finding twice and let the summary drift from what it summarises."""
    assert (
        len(ADMISSION_STEP_HOME) == 9
    ), "the admission framework no longer states nine steps; PRD-FR/FR-01 rests on it"
    assert (
        "PRD-KN/KN-09" in KNOWLEDGE_STAGE
    ), "knowledge retirement is no longer located; PRD-FR/FR-13 rests on it"


def test_monetization_is_the_one_fundamental_requirement_with_no_instrument() -> None:
    """Stated at the top of the document and absent at the bottom of it. PRD-P/P-009 says
    the same thing as a principle and PRD-ECON as a settlement chain -- three sightings of
    one hole, asserted together."""
    from engine.tests.conformance.mandate_corpus import assert_named_by_nothing

    assert (
        "PRD-P/P-009" in PRINCIPLE_ABSENT
    ), "the monetization principle is no longer absent; this row must be re-read"
    assert {"revenue", "billing", "settlement"} <= set(ECONOMIC_FACULTY_ABSENT.values())
    assert_named_by_nothing("PRD-last", FUNDAMENTAL_ABSENT)


def test_certification_can_be_granted_and_neither_renewed_nor_revoked() -> None:
    """NON-VACUITY, and the finding. The certification framework's other five operations are
    located; these two are the ones that would CORRECT a certification after the fact, and a
    certification that cannot be withdrawn is one nothing can correct.
    """
    from engine.tests.conformance.mandate_corpus import assert_named_by_nothing

    assert_named_by_nothing("PRD-last", CERTIFICATION_LIFECYCLE_ABSENT)
    from engine.registry.universal.records import AuditAct, RegistrationState

    assert "RETIRE" in {act.name for act in AuditAct}, (
        "the registry can no longer retire a registration, which is the nearest thing to a "
        "revocation this repository has and is what makes its absence specific"
    )
    assert "RETIRED" in {state.name for state in RegistrationState}
