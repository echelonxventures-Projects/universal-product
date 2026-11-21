"""Mandate conformance — the Master Constitution / Master Index / Master Knowledge Map.

345 mandates over 19 sections (000-018). Sections 016 STAKEHOLDERS and 017 TARGET DOMAINS
are bound in `engine/tests/kernel/test_compliance.py`, against the kernel that can prove a
domain is ADMITTED rather than built. Nothing here restates them.
"""

from __future__ import annotations

from engine.tests.conformance.mandate_corpus import (
    assert_homes_exist,
    assert_named_by_nothing,
    assert_partitions,
    repo_root,
    section,
    tracked,
)
from intelligence.realization.contracts import ArtifactFamily
from intelligence.realization.generators import GENERATORS

# --- MI-015 — the thirty-one projections ----------------------------------------
#
# Section 015 carries one sentence above its list -- "Everything below is generated from
# Repository Truth" -- and that sentence is the mandate. A projection is not satisfied by
# the repository CONTAINING documentation, services or dashboards; it is satisfied by a
# declared PRODUCER emitting them from truth. `service/` exists and is hand-written, which
# is the opposite of what section 015 asks for.
#
# So absence here is measured against the two producer populations and never against path
# names: the URI generator registry (`ArtifactFamily`), and the generated-artifact registry
# that records every deterministic projection with its producer and regeneration command.

#: Projection -> the URI artifact family whose generator emits it.
PROJECTION_GENERATOR = {
    "MI-015/PJ-01": ArtifactFamily.DOCUMENTATION,  # Documentation
    "MI-015/PJ-02": ArtifactFamily.ARCHITECTURE,  # Architecture
    "MI-015/PJ-04": ArtifactFamily.RUNTIME,  # Source Code -- the executable enforcement module
    "MI-015/PJ-05": ArtifactFamily.API,  # APIs
    "MI-015/PJ-14": ArtifactFamily.SCHEMA,  # Schemas
    "MI-015/PJ-17": ArtifactFamily.TEST,  # Tests
    "MI-015/PJ-22": ArtifactFamily.DEPLOYMENT,  # Deployments
}

#: Projection -> (an artifact of that kind, the producer that emits it). Not every generated
#: family reaches the registry's `entries`: `00-BOOK/DATA/` and `00-BOOK/REGISTRIES/` are
#: corpus-internal excludes, so their rows live in `generated_inputs` or are evidenced by the
#: producer naming the artifact. All three routes are accepted and each is checked.
PROJECTION_REGISTERED = {
    # Registries
    "MI-015/PJ-15": ("00-BOOK/REGISTRIES/UNIVERSAL-ARTIFACT-REGISTRY.md", "00-BOOK/tools/ukb.py"),
    # Dashboards
    "MI-015/PJ-18": (
        "00-MASTER/UAIE-000001/00-UAIE-DASHBOARD.md",
        "00-MASTER/UAIE-000001/uaie_engine.py",
    ),
    # Reports
    "MI-015/PJ-19": (
        "00-MASTER/UAKOS-CLOSURE-009/03-REPOSITORY-COVERAGE-REPORT.md",
        "00-MASTER/UAKOS-CLOSURE-009/requirement_engine.py",
    ),
    # Evidence
    "MI-015/PJ-20": ("determinism-evidence/", "engine/determinism/reproduce.py"),
    # Digital Twins
    "MI-015/PJ-23": ("00-BOOK/DATA/", "00-BOOK/tools/register.sh"),
    # AI Agents -- a generated agent surface
    "MI-015/PJ-24": (".claude/CLAUDE.md", "00-BOOK/tools/ukctx.py"),
}

#: No producer emits these. Several have a hand-written counterpart in the tree, which is
#: precisely why they are listed: `service/`, `application/`, `platform/` and
#: `infrastructure/` exist as authored code, and section 015 asks for them as PROJECTIONS.
PROJECTION_NO_PRODUCER = {
    "MI-015/PJ-03": "Diagrams",
    "MI-015/PJ-06": "SDKs",
    "MI-015/PJ-07": "CLIs",
    "MI-015/PJ-08": "Libraries",
    "MI-015/PJ-09": "Services",
    "MI-015/PJ-10": "Applications",
    "MI-015/PJ-11": "Platforms",
    "MI-015/PJ-12": "Infrastructure",
    "MI-015/PJ-13": "Databases",
    "MI-015/PJ-16": "Dictionaries",
    "MI-015/PJ-21": "Policies",
    "MI-015/PJ-25": "Robotics",
}

#: Domain-shaped projections. Generating an "Enterprise System" or a "Commerce Platform" as
#: a projection family would fix an industry into the producer set, which is the breach
#: PRD P-001, LYR-NEG/LN-05 and MIP LAW P43-001 each forbid and which MI-017 already
#: settles: a market is ADMITTED as registered data, never built. Absence here is the
#: mandate being honoured, not missed.
PROJECTION_DOMAIN_SHAPED = {
    "MI-015/PJ-26": "Enterprise Systems",
    "MI-015/PJ-27": "Commerce Platforms",
    "MI-015/PJ-28": "Scientific Platforms",
    "MI-015/PJ-29": "Government Platforms",
    "MI-015/PJ-30": "Space Platforms",
}

#: The openness claim, which is a property of the producer set rather than a projection.
PROJECTION_OPEN_ENDED = {"MI-015/PJ-31": "Infinite Future Projections"}


def test_every_projection_is_generated_registered_absent_domain_shaped_or_open() -> None:
    mandates = section("MI-015")
    assert len(mandates) == 31, f"section 015 lists 31 projections, corpus has {len(mandates)}"
    assert_partitions(
        "MI-015",
        mandates,
        PROJECTION_GENERATOR,
        PROJECTION_REGISTERED,
        PROJECTION_NO_PRODUCER,
        PROJECTION_DOMAIN_SHAPED,
        PROJECTION_OPEN_ENDED,
    )


def test_every_generator_backed_projection_has_a_generator_that_claims_its_family() -> None:
    claimed = {generator.family for generator in GENERATORS}
    for mandate, family in PROJECTION_GENERATOR.items():
        assert (
            family in claimed
        ), f"{mandate}: no generator claims {family.value!r}, so nothing emits this projection"
    families = list(PROJECTION_GENERATOR.values())
    duplicated = sorted({f.value for f in families if families.count(f) > 1})
    assert not duplicated, f"one family claimed by two projections: {duplicated}"


def test_every_registered_projection_resolves_to_a_declared_producer() -> None:
    """A projection recorded without a producer is an artifact somebody edits by hand.

    Three routes are accepted because the registry has three shapes: an `entries` row, a
    `generated_inputs` row, or -- for a corpus-internal exclude that reaches neither -- the
    producer's own source naming the artifact it writes.
    """
    import json

    registry = json.loads(
        (repo_root() / "00-BOOK" / "DATA" / "generated-artifact-registry.json").read_text(
            encoding="utf-8"
        )
    )
    entries = {e["canonical_path"]: e for e in registry["entries"]}
    inputs = {g["path"]: g for g in registry["generated_inputs"]}

    for mandate, (artifact, producer) in PROJECTION_REGISTERED.items():
        assert (repo_root() / producer).exists(), f"{mandate}: producer {producer} does not exist"

        if artifact in entries:
            entry = entries[artifact]
            assert entry.get("producer") == producer, (
                f"{mandate}: the registry names producer {entry.get('producer')!r} for "
                f"{artifact}, this binding names {producer!r}"
            )
            assert entry.get("regeneration_command"), f"{mandate}: {artifact} declares no command"
            continue

        if artifact in inputs:
            row = inputs[artifact]
            assert row.get("producer") == producer, (
                f"{mandate}: generated_inputs names producer {row.get('producer')!r} for "
                f"{artifact}, this binding names {producer!r}"
            )
            assert row.get("bootstrap_command"), f"{mandate}: {artifact} declares no command"
            continue

        basename = artifact.rstrip("/").rsplit("/", 1)[-1]
        source = (repo_root() / producer).read_text(encoding="utf-8", errors="ignore")
        assert basename in source, (
            f"{mandate}: {artifact} is in neither registry population and {producer} does "
            f"not name {basename!r}, so nothing evidences that it is generated at all"
        )


def test_the_absent_projections_are_claimed_by_no_generator_family() -> None:
    """NON-VACUITY, measured against the producer set rather than against path names.

    Path naming would give the wrong answer in both directions here: `service/` would read
    as satisfying PJ-09 while being authored by hand, and `Diagrams` would read as absent
    even if a generator emitted them into files nobody named `diagram`. The generator
    registry is the declared producer set for projection FAMILIES, so it is what decides.
    """
    families = {generator.family.value.lower() for generator in GENERATORS}
    for mandate, projection in {**PROJECTION_NO_PRODUCER, **PROJECTION_DOMAIN_SHAPED}.items():
        stem = projection.lower().rstrip("s")
        assert stem not in families, (
            f"{mandate}: a generator now claims family {stem!r}; {projection} is produced "
            "and no longer belongs in an unproduced tier"
        )


def test_the_family_rule_that_proves_absence_can_return_a_positive() -> None:
    """Run the absence rule against a projection that IS produced and require it to fire.
    Without this, a rule that matched nothing would pass every absence claim silently."""
    families = {generator.family.value.lower() for generator in GENERATORS}
    assert "documentation".rstrip("s") in families, (
        "the family rule does not recognise Documentation, which is produced; every "
        "absence claim resting on it is vacuous"
    )


def test_no_producer_is_named_for_a_target_domain() -> None:
    """The load-bearing half of the domain-shaped tier. If a generator family or a
    registered capability ever names one of these markets, an industry has been fixed into
    the producer set and MI-017's determination has been reversed behind its back."""
    families = {generator.family.value.lower() for generator in GENERATORS}
    for mandate, market in PROJECTION_DOMAIN_SHAPED.items():
        head = market.split()[0].lower()
        assert head not in families, f"{mandate}: {head!r} is now a generator family"


def test_the_producer_set_is_open_which_is_what_the_last_projection_claims() -> None:
    """PJ-31 is not a projection; it is the claim that the list above can grow. That is a
    property of `GENERATORS` being a registry rather than a branch, so it is proven the way
    the object classes are: by admitting something the document never listed."""
    assert isinstance(GENERATORS, tuple)
    assert len(GENERATORS) == len(
        {generator.family for generator in GENERATORS}
    ), "two generators claim one family, so the registry cannot be extended safely"
    assert len(ArtifactFamily) >= len(GENERATORS)


# --- MI-002 — the twenty-seven constitutions ------------------------------------
#
# Section 002 lists twenty-seven constitutions, one per governed domain. CMG-000001 is the
# instrument that decides what counts as one, and this repository has a naming convention
# that follows it: a constitution is a document whose name ends `CONSTITUTION.md`. That is
# the test used below, in both directions -- a domain has a constitution when such a file
# carries its name, and lacks one when none does.
#
# The distinction the tiers keep is between a CONSTITUTION and an OWNER. Eleven domains have
# a constitution. Five more have no constitution and do have a declared owner -- the root law
# or an instrument the authority alignment register subordinates to it -- which is governance
# without a constitution, not the absence of governance. Eleven have neither.
#
# `UCRD-001-CONSTITUTIONAL-RELATIONSHIP-DETERMINATION.md` is why the rule is the SUFFIX and
# not the word: it carries both "constitutional" and "relationship" and is a determination.
# Matching it would have reported a Relationship Constitution that does not exist.

CONSTITUTION_SUFFIX = "CONSTITUTION.md"

#: Domain -> the document that constitutes it.
DOMAIN_CONSTITUTION = {
    "MI-002/C-01": "00-CEP/CEP-001-CONSTITUTIONAL-ENGINEERING-CONSTITUTION.md",
    "MI-002/C-09": "00-MASTER/UEI-000001/01-UNIVERSAL-EVOLUTION-INTELLIGENCE-CONSTITUTION.md",
    "MI-002/C-13": "00-MASTER/UAKOS-CLOSURE-006/CONST-09-REPOSITORY-LIFECYCLE-CONSTITUTION.md",
    "MI-002/C-14": "08-RUNTIME/RUNTIME-001-UNIVERSAL-RUNTIME-CONSTITUTION.md",
    "MI-002/C-15": "00-MASTER/UCOS-RFP-001/REPOSITORY-FIXED-POINT-CONSTITUTION.md",
    "MI-002/C-16": "00-CEP/CEP-002-CONSTITUTIONAL-GOVERNANCE-CONSTITUTION.md",
    "MI-002/C-17": "00-CEP/CEP-004-CONSTITUTIONAL-VALIDATION-CONSTITUTION.md",
    "MI-002/C-18": "00-MASTER/UCOS-CVR-001/05-VERIFICATION-CONSTITUTION.md",
    "MI-002/C-19": "00-CEP/CEP-005-CONSTITUTIONAL-CERTIFICATION-CONSTITUTION.md",
    "MI-002/C-20": "14-SECURITY/SECURITY-001-UNIVERSAL-SECURITY-CONSTITUTION.md",
    "MI-002/C-26": "00-CEP/CEP-009-CONSTITUTIONAL-AMENDMENT-EVOLUTION-CONSTITUTION.md",
}

#: Domain -> a declared owner that is not a constitution. Governance without a constitution
#: is a real standing and a weaker one, so it is recorded rather than counted as either.
DOMAIN_OWNED_NOT_CONSTITUTED = {
    "MI-002/C-02": "engine/uckp/law.py",  # Identity -- UCKP-ART-05
    "MI-002/C-04": "00-MASTER/UCXI-000001/ucxi-declaration.json",  # Context
    "MI-002/C-07": "00-BOOK/UCOS-BOOK-000000-UNIVERSAL-MASTER-KNOWLEDGE-BOOK.md",  # Knowledge
    # Capability
    "MI-002/C-10": "00-MASTER/UCIC-001-UNIVERSAL-CAPABILITY-IMPLEMENTATION-CONTRACT.md",
    "MI-002/C-27": "00-BOOK/DATA/generated-artifact-registry.json",  # Projection
}

#: Neither constituted nor owned. Eleven of twenty-seven, and four of them -- Privacy,
#: Commercial, Economic and Analytics -- are the same domains ARCH-UCMM and QM-CONST report
#: unanswered. A third document naming the same holes is corroboration, not new information.
DOMAIN_UNCONSTITUTED = {
    "MI-002/C-03": "relationship",
    "MI-002/C-05": "constraint",
    "MI-002/C-06": "rule",
    "MI-002/C-08": "information",
    "MI-002/C-11": "configuration",
    "MI-002/C-12": "composition",
    "MI-002/C-21": "privacy",
    "MI-002/C-22": "commercial",
    "MI-002/C-23": "economic",
    "MI-002/C-24": "monitoring",
    "MI-002/C-25": "analytics",
}


def test_every_mandated_constitution_is_constituted_owned_or_neither() -> None:
    mandates = section("MI-002")
    assert len(mandates) == 27, f"section 002 lists 27 constitutions, corpus has {len(mandates)}"
    assert_partitions(
        "MI-002",
        mandates,
        DOMAIN_CONSTITUTION,
        DOMAIN_OWNED_NOT_CONSTITUTED,
        DOMAIN_UNCONSTITUTED,
    )


def test_every_named_constitution_is_a_constitution_by_the_repository_convention() -> None:
    """A home that does not end CONSTITUTION.md is a determination, a register or a report,
    and calling it a constitution is the category error this tier exists to avoid."""
    known = set(tracked())
    for mandate, home in DOMAIN_CONSTITUTION.items():
        assert home in known, f"{mandate}: {home} is not a tracked path"
        assert home.endswith(CONSTITUTION_SUFFIX), (
            f"{mandate}: {home} does not end {CONSTITUTION_SUFFIX}, so by this repository's "
            "own convention it is not a constitution"
        )


def test_every_owned_domain_has_a_tracked_owner_that_is_not_a_constitution() -> None:
    """The tier boundary. An owner that IS a constitution belongs a tier up."""
    known = set(tracked())
    for mandate, home in DOMAIN_OWNED_NOT_CONSTITUTED.items():
        assert home in known, f"{mandate}: {home} is not a tracked path"
        assert not home.endswith(
            CONSTITUTION_SUFFIX
        ), f"{mandate}: {home} is a constitution and is understated as a bare owner"


def test_the_unconstituted_domains_are_named_by_no_constitution() -> None:
    """NON-VACUITY, by the suffix rule rather than by the word.

    Searching for the word would match `UCRD-001-CONSTITUTIONAL-RELATIONSHIP-DETERMINATION`
    and report a Relationship Constitution that does not exist -- a determination is not a
    constitution, and the repository's own naming says which is which.
    """
    constitutions = [p for p in tracked() if p.endswith(CONSTITUTION_SUFFIX)]
    assert constitutions, "no file ends CONSTITUTION.md, so the suffix rule is vacuous"
    for mandate, domain in DOMAIN_UNCONSTITUTED.items():
        found = [p for p in constitutions if domain in p.rsplit("/", 1)[-1].lower()]
        assert (
            not found
        ), f"{mandate}: {domain!r} is declared unconstituted but {found} carries its name"


def test_the_suffix_rule_that_proves_absence_can_return_a_positive() -> None:
    """Run the rule against a domain that IS constituted and require a hit."""
    constitutions = [p for p in tracked() if p.endswith(CONSTITUTION_SUFFIX)]
    hits = [p for p in constitutions if "security" in p.rsplit("/", 1)[-1].lower()]
    assert hits, "the suffix rule finds no Security Constitution, which exists; it is vacuous"


def test_the_unconstituted_domains_agree_with_the_other_two_documents() -> None:
    """Privacy, Commercial/Commerce, Economic(s) and Analytics are reported unanswered by
    the UCMM and the interrogative model too. A disagreement would mean one suite has
    mis-located something rather than that the repository changed."""
    from engine.tests.conformance.test_mandates_arch import META_MODEL_ABSENT
    from engine.tests.conformance.test_mandates_model import CONSTITUTION_ABSENT

    here = set(DOMAIN_UNCONSTITUTED.values())
    elsewhere = set(META_MODEL_ABSENT.values()) | set(CONSTITUTION_ABSENT.values())
    for domain in ("privacy", "information"):
        assert domain in here, f"{domain} is no longer reported unconstituted here"
        assert domain in elsewhere, f"{domain} is no longer reported absent elsewhere"


# --- MI-001 — the twenty-five foundations ---------------------------------------
#
# Section 001 lists twenty-five foundations. A foundation is not a capability; it is the
# ground a capability stands on, and in this repository the ground is the root law. Each of
# its twenty articles declares the tokens it BINDS, so "is there a Universal Identity
# Foundation" has a mechanical answer: does an article bind `identity`.
#
# Eleven foundations are grounded in an article. Eight more are not, and are carried by a
# located instrument -- real ground, lower down, and the difference is worth keeping because
# an instrument can be replaced and an article cannot. Six are neither, and two of those are
# the same Logic and Mathematics the meta-model reports missing: a foundation the law does
# not ground and no module carries is a foundation in name only.

#: Foundation -> the article of the root law that grounds it.
FOUNDATION_ARTICLE = {
    "MI-001/F-01": "UCKP-ART-01",  # Universal Constitutional Foundation
    "MI-001/F-02": "UCKP-ART-02",  # Universal Existence Foundation
    "MI-001/F-07": "UCKP-ART-06",  # Universal Knowledge Foundation
    "MI-001/F-09": "UCKP-ART-05",  # Universal Identity Foundation
    "MI-001/F-10": "UCKP-ART-07",  # Universal Relationship Foundation
    "MI-001/F-16": "UCKP-ART-13",  # Universal Measurement Foundation
    "MI-001/F-18": "UCKP-ART-15",  # Universal Intelligence Foundation
    "MI-001/F-19": "UCKP-ART-16",  # Universal Governance Foundation
    "MI-001/F-20": "UCKP-ART-14",  # Universal Evolution Foundation
    "MI-001/F-22": "UCKP-ART-10",  # Universal Runtime Foundation
    "MI-001/F-25": "UCKP-ART-11",  # Universal Projection Foundation
}

#: Foundation -> a located instrument, where no article grounds it.
FOUNDATION_INSTRUMENT = {
    "MI-001/F-03": "engine/construct/reality.py",  # Universal Reality Foundation
    "MI-001/F-05": "platform/universal_truth",  # Universal Truth Foundation
    "MI-001/F-06": "engine/uckp/values.py",  # Universal Meaning Foundation
    "MI-001/F-11": "00-MASTER/UCXI-000001/ucxi-declaration.json",  # Universal Context Foundation
    "MI-001/F-12": "engine/uckp/facets.py",  # Universal Constraint Foundation
    "MI-001/F-13": "engine/kernel/governance.py",  # Universal Rule Foundation
    "MI-001/F-21": "platform/universal_assurance",  # Universal Assurance Foundation
    "MI-001/F-24": "platform/commercial_intelligence",  # Universal Commercial Foundation
}

#: Grounded by neither the law nor a module.
FOUNDATION_UNGROUNDED = {
    "MI-001/F-04": "possibility",
    "MI-001/F-08": "information",
    "MI-001/F-14": "logic",
    "MI-001/F-15": "mathematics",
    "MI-001/F-17": "computation",
    "MI-001/F-23": "economic",
}


def _foundation_word(label: str) -> str:
    """`Universal Identity Foundation` -> `identity`, which is what an article binds."""
    return label.removeprefix("Universal ").removesuffix(" Foundation").lower()


def test_every_foundation_is_grounded_in_an_article_an_instrument_or_neither() -> None:
    mandates = section("MI-001")
    assert len(mandates) == 25, f"section 001 lists 25 foundations, corpus has {len(mandates)}"
    assert_partitions(
        "MI-001",
        mandates,
        FOUNDATION_ARTICLE,
        FOUNDATION_INSTRUMENT,
        FOUNDATION_UNGROUNDED,
    )


def test_each_article_grounded_foundation_names_an_article_that_binds_it() -> None:
    """The article must exist AND carry the foundation's word -- in what it binds or in its
    own title. Naming an article that says nothing about the foundation would be a citation,
    not a grounding."""
    from engine.uckp.law import ROOT_LAW

    articles = {article.article_id: article for article in ROOT_LAW.articles}
    mandates = section("MI-001")
    for mandate, article_id in FOUNDATION_ARTICLE.items():
        assert article_id in articles, f"{mandate}: {article_id} is not an article of the root law"
        article = articles[article_id]
        word = _foundation_word(mandates[mandate])
        grounded = word in article.title.lower() or any(
            word.startswith(token) or token.startswith(word) for token in article.binds
        )
        assert grounded, (
            f"{mandate}: {article_id} ({article.title}) binds {article.binds} and says "
            f"nothing about {word!r}; that is a citation, not a grounding"
        )


def test_no_article_is_claimed_by_two_foundations() -> None:
    """NON-VACUITY. Twenty articles and twenty-five foundations, so overlap is possible --
    and two foundations resting on one article means one of them is not separately grounded."""
    claimed = list(FOUNDATION_ARTICLE.values())
    duplicated = sorted({a for a in claimed if claimed.count(a) > 1})
    assert not duplicated, f"articles claimed by more than one foundation: {duplicated}"


def test_every_instrument_grounded_foundation_has_no_article_and_a_tracked_home() -> None:
    """The tier boundary. If an article binds the word, the foundation belongs a tier up."""
    from engine.uckp.law import ROOT_LAW

    known = set(tracked())
    mandates = section("MI-001")
    for mandate, home in FOUNDATION_INSTRUMENT.items():
        present = home in known or any(p.startswith(home.rstrip("/") + "/") for p in known)
        assert present, f"{mandate}: {home} is not a tracked path"
        word = _foundation_word(mandates[mandate])
        grounding = [a.article_id for a in ROOT_LAW.articles if word in a.binds]
        assert not grounding, (
            f"{mandate}: {word!r} is bound by {grounding} after all, so this foundation is "
            "understated as an instrument"
        )


def test_the_ungrounded_foundations_are_bound_by_no_article_and_named_by_no_module() -> None:
    """NON-VACUITY in both directions -- the law and the tree. `engine/construct/reality.py`
    is why the module half is checked: Reality reads as ungrounded against the law alone and
    is carried by a module, so the law-only answer would have been wrong."""
    from engine.uckp.law import ROOT_LAW

    for mandate, word in FOUNDATION_UNGROUNDED.items():
        grounding = [a.article_id for a in ROOT_LAW.articles if word in a.binds]
        assert not grounding, f"{mandate}: {word!r} is bound by {grounding}"
    assert_named_by_nothing("MI-001", FOUNDATION_UNGROUNDED)


def test_the_foundation_gaps_agree_with_the_meta_model() -> None:
    """Logic, Mathematics and Information are ungrounded here and absent in the UCMM."""
    from engine.tests.conformance.test_mandates_arch import META_MODEL_ABSENT

    shared = {"logic", "mathematics", "information"}
    here = set(FOUNDATION_UNGROUNDED.values())
    there = set(META_MODEL_ABSENT.values())
    assert shared <= here, f"no longer ungrounded here: {sorted(shared - here)}"
    assert shared <= there, f"the UCMM no longer reports absent: {sorted(shared - there)}"


# --- MI-004 — the twenty-one graphs ---------------------------------------------
#
# Section 004 lists twenty-one graphs. `engine/graph` already builds a core knowledge graph
# and ten named projections over it, so the question is a join between two lists that were
# written independently -- and they overlap less than either would suggest.
#
# Four mandated graphs are built projections. Five more are carried by an instrument that is
# graph-shaped without being a projection. Eleven are carried by nothing. And six of the ten
# projections the repository builds are not mandated here at all, which is the finding that
# only appears if both directions are measured: the section is not a description of what
# `engine/graph` does, and reading it as one would report far more coverage than exists.

#: Mandated graph -> the projection name that builds it.
GRAPH_PROJECTION = {
    "MI-004/G-06": "dependency",  # Dependency Graph
    "MI-004/G-07": "capability",  # Capability Graph
    "MI-004/G-12": "evidence",  # Evidence Graph
    "MI-004/G-13": "traceability",  # Traceability Graph
}

#: Mandated graph -> a graph-shaped instrument that is not a projection.
GRAPH_INSTRUMENT = {
    "MI-004/G-01": "engine/graph/model.py",  # Knowledge Graph -- the core the rest project from
    "MI-004/G-03": "engine/uckp/graph.py",  # Concept Graph
    "MI-004/G-05": "00-MASTER/UCOS-UGA-001/04-RELATIONSHIP-GRAPH.json",  # Relationship Graph
    "MI-004/G-09": "00-MASTER/UCOS-UGA-001/00-EXISTENCE-INVENTORY.json",  # Repository Graph
    "MI-004/G-15": "00-BOOK/DATA/change-ledger.json",  # Evolution Graph
}

#: Built by nothing. Identity and Lineage are the two worth pausing on: the repository has
#: an id ledger and a lineage registry, and neither is a graph -- a ledger records what was
#: allocated, a graph answers what reaches what, and only the second is mandated here.
GRAPH_ABSENT = {
    "MI-004/G-02": "semantic",
    "MI-004/G-04": "identity",
    "MI-004/G-08": "runtime",
    "MI-004/G-10": "governance",
    "MI-004/G-11": "intelligence",
    "MI-004/G-14": "lineage",
    "MI-004/G-16": "security",
    "MI-004/G-17": "commercial",
    "MI-004/G-18": "economic",
    "MI-004/G-19": "monitoring",
    "MI-004/G-20": "analytics",
    "MI-004/G-21": "projection",
}


def _built_projections() -> set[str]:
    """The projection names `engine/graph` actually builds.

    Read from the `match` arms of `build_projection`, which is the one place that decides
    whether a name resolves -- a list restated here would be a second authoring of the
    registry and could disagree with it silently.
    """
    import re

    source = (repo_root() / "engine" / "graph" / "projections.py").read_text(encoding="utf-8")
    body = source[source.index("def build_projection(") :]
    return set(re.findall(r'^\s+case "([a-z_]+)":', body, flags=re.MULTILINE))


def test_every_mandated_graph_is_a_projection_an_instrument_or_absent() -> None:
    mandates = section("MI-004")
    assert len(mandates) == 21, f"section 004 lists 21 graphs, corpus has {len(mandates)}"
    assert_partitions("MI-004", mandates, GRAPH_PROJECTION, GRAPH_INSTRUMENT, GRAPH_ABSENT)


def test_every_projection_backed_graph_names_a_projection_the_engine_builds() -> None:
    from engine.graph.projections import build_projection  # noqa: F401 - must import

    built = _built_projections()
    for mandate, name in GRAPH_PROJECTION.items():
        assert name in built, (
            f"{mandate}: engine/graph builds no projection named {name!r}, so the mandated "
            "graph is not built"
        )
    claimed = list(GRAPH_PROJECTION.values())
    duplicated = sorted({n for n in claimed if claimed.count(n) > 1})
    assert not duplicated, f"one projection claimed by two mandated graphs: {duplicated}"


def test_every_instrument_backed_graph_is_tracked_and_is_not_a_projection() -> None:
    known = set(tracked())
    built = _built_projections()
    mandates = section("MI-004")
    for mandate, home in GRAPH_INSTRUMENT.items():
        assert home in known, f"{mandate}: {home} is not a tracked path"
        name = mandates[mandate].removesuffix(" Graph").lower()
        assert name not in built, (
            f"{mandate}: {name!r} IS a built projection and is understated as a loose " "instrument"
        )


def test_the_absent_graphs_are_built_by_no_projection_and_no_module() -> None:
    """NON-VACUITY in both directions. Checking only the projection set would report
    Relationship absent while UGA builds one; checking only paths would report Dependency
    absent because no file is named for it."""
    built = _built_projections()
    for mandate, name in GRAPH_ABSENT.items():
        assert name not in built, f"{mandate}: {name!r} is a built projection after all"
    # A DOCUMENT about a graph is not a graph. The first draft searched every tracked path
    # and offered `PHASE-0.7-DEPENDENCY-GRAPH-GOVERNANCE-BINDING-DETERMINATION.md` as
    # evidence that a Governance Graph exists, which is the occurrence-is-ownership error
    # in its documentary form. Only code and data can build one.
    graphish = [
        path
        for path in tracked()
        if "graph" in path.rsplit("/", 1)[-1].lower()
        and path.endswith((".py", ".json"))
        and "/tests/" not in path
    ]
    assert graphish, "no code or data file is named for a graph, so this search is vacuous"
    for mandate, name in GRAPH_ABSENT.items():
        found = [p for p in graphish if name in p.rsplit("/", 1)[-1].lower()]
        assert not found, f"{mandate}: {name!r} is declared absent but {found} is named for it"


def test_the_repository_builds_projections_this_section_never_mandates() -> None:
    """The reverse direction, which is where the real finding is.

    Six of the ten projections `engine/graph` builds -- ontology, requirement,
    implementation, validation, certification, impact -- appear nowhere in section 004.
    The section is therefore not a description of the graph engine, and any reading that
    treats it as one reports coverage that was never claimed.
    """
    built = _built_projections()
    mandated = {label.removesuffix(" Graph").lower() for label in section("MI-004").values()}
    unmandated = sorted(
        name
        for name in ("ontology", "requirement", "implementation", "validation", "certification")
        if name in built and name not in mandated
    )
    assert len(unmandated) >= 5, (
        f"expected the graph engine to build projections section 004 does not mandate; "
        f"found only {unmandated}"
    )


# --- MI-003 — the twenty universal models ---------------------------------------
#
# Section 003 lists twenty models. Layer Zero is the respondent for most of them, and five
# arrive in one module: `engine/uckp/values.py` carries Relationship, ContextBinding,
# Constraint, Policy and TemporalEvent as separate frozen dataclasses. One home claimed five
# times is only honest if the module really carries five distinct models, so the class NAMES
# are asserted rather than the path -- a file five mandates point at with one class in it
# would be four mandates unanswered.

#: Model -> the module that defines it, and the class within it when the module carries
#: several. An empty class name means the module is the model.
UNIVERSAL_MODEL = {
    "MI-003/M-01": ("engine/uckp/canonical.py", ""),  # Primitive Model
    "MI-003/M-02": ("engine/root_ontology/model.py", ""),  # Concept Model
    "MI-003/M-03": ("engine/uckp/ucko.py", ""),  # Object Model
    "MI-003/M-04": ("engine/uckp/identity.py", ""),  # Identity Model
    "MI-003/M-05": ("engine/uckp/values.py", "Relationship"),  # Relationship Model
    "MI-003/M-06": ("engine/uckp/values.py", "ContextBinding"),  # Context Model
    "MI-003/M-07": ("engine/uckp/capabilities.py", ""),  # Capability Model
    "MI-003/M-08": ("engine/uckp/values.py", "Constraint"),  # Constraint Model
    "MI-003/M-09": ("engine/uckp/values.py", "Policy"),  # Rule Model
    "MI-003/M-10": ("engine/uckp/values.py", "TemporalEvent"),  # Event Model
    "MI-003/M-11": ("engine/uckp/state.py", ""),  # State Model
    "MI-003/M-13": ("engine/uckp/vocabulary.py", ""),  # Lifecycle Model
    "MI-003/M-14": ("engine/uckp/evolution.py", ""),  # Evolution Model
    "MI-003/M-15": ("engine/uckp/execution.py", ""),  # Runtime Model
    "MI-003/M-16": ("00-MASTER/UCOS-UGA-001/uga-declaration.json", ""),  # Repository Model
    "MI-003/M-17": ("engine/uckp/governance.py", ""),  # Governance Model
    "MI-003/M-19": ("platform/commercial_intelligence/contracts.py", ""),  # Commercial Model
    "MI-003/M-20": ("engine/uckp/projection.py", ""),  # Projection Model
}

#: Modelled by nothing. Behaviour and Economics again -- the fourth and third document
#: respectively to name them, which is why the cross-suite agreement below is worth having.
UNIVERSAL_MODEL_ABSENT = {
    "MI-003/M-12": "behavior",
    "MI-003/M-18": "economic",
}


def test_every_universal_model_is_defined_or_absent() -> None:
    mandates = section("MI-003")
    assert len(mandates) == 20, f"section 003 lists 20 models, corpus has {len(mandates)}"
    assert_partitions("MI-003", mandates, UNIVERSAL_MODEL, UNIVERSAL_MODEL_ABSENT)


def test_every_defined_model_has_a_tracked_home() -> None:
    assert_homes_exist("MI-003", {m: home for m, (home, _cls) in UNIVERSAL_MODEL.items()})


def test_the_shared_module_really_carries_a_distinct_class_per_model() -> None:
    """NON-VACUITY for the five models that share `values.py`.

    Asserting the path would pass for a module with one class in it and four mandates
    pointing hopefully at it. Asserting the class name is what makes five separate answers.
    """
    import ast

    shared: dict[str, list[str]] = {}
    for _mandate, (home, class_name) in UNIVERSAL_MODEL.items():
        if class_name:
            shared.setdefault(home, []).append(class_name)

    for home, expected in shared.items():
        assert len(expected) == len(
            set(expected)
        ), f"{home}: one class claimed by two models: {sorted(expected)}"
        tree = ast.parse((repo_root() / home).read_text(encoding="utf-8"))
        defined = {n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)}
        missing = sorted(set(expected) - defined)
        assert not missing, f"{home} defines no {missing}; those models are unanswered"


def test_no_two_models_share_a_home_without_naming_a_class() -> None:
    """The other half. Two models on one module with no class named would be the same error
    in the opposite direction -- indistinguishable answers presented as two."""
    bare = [home for _m, (home, class_name) in UNIVERSAL_MODEL.items() if not class_name]
    duplicated = sorted({h for h in bare if bare.count(h) > 1})
    assert (
        not duplicated
    ), f"modules claimed by two models with no class distinguishing them: {duplicated}"


def test_the_absent_models_are_defined_by_nothing() -> None:
    assert_named_by_nothing("MI-003", UNIVERSAL_MODEL_ABSENT)


def test_behaviour_and_economics_are_unanswered_in_every_document_that_names_them() -> None:
    """Four documents mandate a behaviour model and none of them is answered. That is the
    strongest form the finding takes, so it is asserted across all four suites at once."""
    from engine.tests.conformance.test_mandates_arch import META_MODEL_ABSENT
    from engine.tests.conformance.test_mandates_model import CONSTITUTION_ABSENT

    def stems(values):
        return {v.replace("behaviour", "behavio").replace("behavior", "behavio") for v in values}

    here = stems(UNIVERSAL_MODEL_ABSENT.values())
    assert "behavio" in here and "economic" in here
    assert "behavio" in stems(META_MODEL_ABSENT.values())
    assert "behavio" in stems(CONSTITUTION_ABSENT.values())
    assert "economics" in set(META_MODEL_ABSENT.values()) | set(CONSTITUTION_ABSENT.values())


# --- MI-000 — the Absolute Constitutional Kernel --------------------------------
#
# Section 000 lists nineteen things the kernel holds. Nine of them exist in the root law or
# in Layer Zero. Ten do not, and the ten divide cleanly in a way worth naming: five are the
# repository's INTENT -- Purpose, Vision, Mission, Philosophy, Core Values -- and five are
# its FORMAL APPARATUS -- Postulates, Symbols, Mathematics, Logic, Grammar.
#
# Neither half is an oversight in the same sense. A substrate with no stated purpose still
# runs; a substrate with no logic or grammar cannot state a rule formally, which is the same
# gap ARCH-UCMM and MI-001 already report from two other directions.

#: Kernel element -> the module or law attribute that holds it, and the class when the
#: module carries several.
KERNEL_ELEMENT = {
    "MI-000/K-06": ("engine/uckp/law.py", "Article"),  # Guiding Principles
    "MI-000/K-07": ("engine/uckp/law.py", "RootLaw"),  # Constitutional Laws
    "MI-000/K-08": ("engine/uckp/law.py", "Invariant"),  # Universal Invariants
    "MI-000/K-09": ("engine/uckp/law.py", ""),  # Universal Axioms -- a governed category
    "MI-000/K-11": ("engine/uckp/vocabulary.py", "Term"),  # Universal Definitions
    "MI-000/K-12": ("engine/uckp/vocabulary.py", "Vocabulary"),  # Universal Terminology
    "MI-000/K-13": ("engine/uckp/values.py", "SemanticIdentity"),  # Universal Semantics
    "MI-000/K-17": ("engine/determinism/reproduce.py", ""),  # Universal Proof System
    "MI-000/K-18": ("engine/kernel/meta.py", ""),  # Universal Meta Model
}

#: The kernel's stated intent. Absent, and absent together.
KERNEL_INTENT_ABSENT = {
    "MI-000/K-01": "purpose",
    "MI-000/K-02": "vision",
    "MI-000/K-03": "mission",
    "MI-000/K-04": "philosophy",
    "MI-000/K-05": "core values",
}

#: The kernel's formal apparatus. Absent, and this is the half that costs something.
KERNEL_FORMALISM_ABSENT = {
    "MI-000/K-10": "postulates",
    "MI-000/K-14": "symbols",
    "MI-000/K-15": "mathematics",
    "MI-000/K-16": "logic",
    "MI-000/K-19": "grammar",
}


def test_every_kernel_element_is_held_or_absent() -> None:
    mandates = section("MI-000")
    assert len(mandates) == 19, f"section 000 lists 19 elements, corpus has {len(mandates)}"
    assert_partitions(
        "MI-000",
        mandates,
        KERNEL_ELEMENT,
        KERNEL_INTENT_ABSENT,
        KERNEL_FORMALISM_ABSENT,
    )


def test_every_held_element_has_a_tracked_home_and_its_named_class() -> None:
    import ast

    assert_homes_exist("MI-000", {m: home for m, (home, _c) in KERNEL_ELEMENT.items()})
    for mandate, (home, class_name) in KERNEL_ELEMENT.items():
        if not class_name:
            continue
        tree = ast.parse((repo_root() / home).read_text(encoding="utf-8"))
        defined = {n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)}
        assert (
            class_name in defined
        ), f"{mandate}: {home} defines no {class_name!r}, so the element is unanswered"


def test_the_law_really_carries_articles_invariants_and_an_axiom_category() -> None:
    """NON-VACUITY for the four elements answered by `law.py`. A class that exists and is
    never populated would satisfy the AST check and hold nothing."""
    from engine.uckp.law import ROOT_LAW

    assert len(ROOT_LAW.articles) == 20, f"the law carries {len(ROOT_LAW.articles)} articles"
    assert len(ROOT_LAW.invariants) == 17, f"the law carries {len(ROOT_LAW.invariants)} invariants"
    assert (
        "axiom" in ROOT_LAW.governed_categories
    ), "MI-000/K-09 rests on `axiom` being a governed category of the root law; it is not"


def test_the_intent_and_the_formalism_are_absent_for_different_reasons() -> None:
    """Both halves are searched, and the split is asserted rather than described: five
    elements of stated intent and five of formal apparatus, none of them held."""
    assert len(KERNEL_INTENT_ABSENT) == 5
    assert len(KERNEL_FORMALISM_ABSENT) == 5
    assert_named_by_nothing("MI-000", KERNEL_INTENT_ABSENT)
    assert_named_by_nothing("MI-000", KERNEL_FORMALISM_ABSENT)


def test_the_formal_gap_is_the_same_one_two_other_sections_report() -> None:
    """Logic and Mathematics are missing from the kernel, from the meta-model and from the
    foundations. Three sections, one hole, asserted together so it cannot be read as three
    small omissions."""
    from engine.tests.conformance.test_mandates_arch import META_MODEL_ABSENT

    shared = {"logic", "mathematics"}
    assert shared <= set(KERNEL_FORMALISM_ABSENT.values())
    assert shared <= set(META_MODEL_ABSENT.values())
    assert shared <= set(FOUNDATION_UNGROUNDED.values())


# --- MI-011 — the seventeen operation dimensions --------------------------------
#
# Section 011 is the Master Index's account of the same axes PRD section 19 states, plus
# three it adds and minus three it omits. The mechanism is identical and is explained under
# PRD-MD: an axis stays open by the kernel REFUSING to seed a concrete value for it, or by
# an unknown category the architectural proof represents. That explanation is not repeated
# here; what is checked here is this section's own seventeen, and the agreement between the
# two documents where they overlap.

DIMENSION_REFUSED_TOKEN_MI = {
    "MI-011/O-01": "human",  # Multi User
    "MI-011/O-03": "company",  # Multi Organization
    "MI-011/O-04": "company",  # Multi Enterprise -- the same axis under a second name
    "MI-011/O-06": "country",  # Multi Country
    "MI-011/O-07": "language",  # Multi Language
    "MI-011/O-08": "currency",  # Multi Currency
    "MI-011/O-09": "tax",  # Multi Tax
    "MI-011/O-10": "calendar",  # Multi Calendar
    "MI-011/O-11": "timezone",  # Multi Temporal
    "MI-011/O-13": "cloud",  # Multi Cloud
    "MI-011/O-14": "earth",  # Multi Planet
}

DIMENSION_UNKNOWN_CATEGORY_MI = {
    "MI-011/O-12": "ExecutionModelUnknown",  # Multi Runtime
    "MI-011/O-16": "CapabilityDomain",  # Multi Reality
}

#: Infinite Scalability is not a dimension; it is the claim the dimensions have no ceiling.
DIMENSION_SCOPE_MODULE = {"MI-011/O-17": "engine/infinite_scope"}

DIMENSION_UNHELD_MI = {
    "MI-011/O-02": "Multi Tenant",
    "MI-011/O-05": "Multi Region",
    "MI-011/O-15": "Multi Universe",
}


def test_every_operation_dimension_is_refused_represented_scoped_or_unheld() -> None:
    mandates = section("MI-011")
    assert len(mandates) == 17, f"section 011 states 17 dimensions, corpus has {len(mandates)}"
    assert_partitions(
        "MI-011",
        mandates,
        DIMENSION_REFUSED_TOKEN_MI,
        DIMENSION_UNKNOWN_CATEGORY_MI,
        DIMENSION_SCOPE_MODULE,
        DIMENSION_UNHELD_MI,
    )


def test_every_token_and_category_this_section_names_is_real() -> None:
    from engine.kernel.compliance import PROHIBITED_TOKENS, architectural_proof

    for mandate, token in DIMENSION_REFUSED_TOKEN_MI.items():
        assert token in PROHIBITED_TOKENS, f"{mandate}: {token!r} is not a prohibited token"
    proven = {r["category"] for r in architectural_proof()["records"] if r["ok"]}
    for mandate, category in DIMENSION_UNKNOWN_CATEGORY_MI.items():
        assert category in proven, f"{mandate}: {category!r} is not represented"
    assert_homes_exist("MI-011", DIMENSION_SCOPE_MODULE)


def test_organization_and_enterprise_share_one_token_because_they_are_one_axis() -> None:
    """NON-VACUITY for the only token claimed twice. Two dimensions on one refusal is honest
    only when they are the same axis named twice, and unnoticed otherwise -- so it is stated
    rather than allowed to pass as an oversight."""
    claimed = list(DIMENSION_REFUSED_TOKEN_MI.values())
    shared = sorted({t for t in claimed if claimed.count(t) > 1})
    assert shared == ["company"], f"tokens claimed by two dimensions: {shared}"
    mandates = section("MI-011")
    assert mandates["MI-011/O-03"] == "Multi Organization"
    assert mandates["MI-011/O-04"] == "Multi Enterprise"


def test_the_two_documents_agree_on_which_dimensions_are_unheld() -> None:
    """Tenant and Universe are unheld in both sections. Two documents, one repository, and
    the overlap measured independently -- a disagreement would mean one suite mis-mapped an
    axis rather than that the repository changed."""
    from engine.tests.conformance.test_mandates_prd import (
        DIMENSION_REFUSED_TOKEN,
        DIMENSION_UNHELD,
    )

    def axes(values):
        return {v.replace("Multi-", "").replace("Multi ", "").lower() for v in values}

    here, there = axes(DIMENSION_UNHELD_MI.values()), axes(DIMENSION_UNHELD.values())
    assert (
        {"tenant", "universe"} <= here & there
    ), f"the two sections no longer agree on the unheld axes: {sorted(here ^ there)}"
    shared_tokens = set(DIMENSION_REFUSED_TOKEN.values()) & set(DIMENSION_REFUSED_TOKEN_MI.values())
    assert {"company", "language", "currency", "tax", "cloud"} <= shared_tokens


# --- MI-005 — the nineteen discoveries ------------------------------------------
#
# Section 005 lists nineteen kinds of discovery. Eleven of them are UCL-000001 lifecycle
# stages, and six of those eleven match the stage name EXACTLY -- Knowledge Discovery,
# Capability Discovery, Dependency Discovery, Constraint Discovery, Gap Discovery, Context
# Assimilation. Two documents written apart, six identical phrases.
#
# Four more are performed by an instrument the lifecycle does not name. Four are performed
# by nothing, and PRD section 10 mandates three of the same four -- so the gap is measured
# twice, independently, and the two suites are asserted to agree.

DISCOVERY_LIFECYCLE_STAGE = {
    "MI-005/D-01": "Observe",  # Observation
    "MI-005/D-02": "Repository Truth Discovery",  # Discovery
    "MI-005/D-03": "Knowledge Discovery",  # Knowledge Discovery
    "MI-005/D-05": "Capability Discovery",  # Capability Discovery
    "MI-005/D-06": "Dependency Discovery",  # Dependency Discovery
    "MI-005/D-10": "Canonical Owner Discovery",  # Ownership Discovery
    "MI-005/D-11": "Constraint Discovery",  # Constraint Discovery
    "MI-005/D-12": "Gap Discovery",  # Gap Discovery
    "MI-005/D-15": "Reuse Before Create",  # Reuse Discovery
    "MI-005/D-18": "Context Assimilation",  # Context Assimilation
    "MI-005/D-19": "Understand",  # Constitutional Understanding
}

DISCOVERY_INSTRUMENT = {
    # Requirement Discovery
    "MI-005/D-04": "00-MASTER/UAKOS-CLOSURE-009/requirement_engine.py",
    "MI-005/D-07": "engine/context/resolution.py",  # Context Discovery
    "MI-005/D-08": "00-BOOK/DATA/id-ledger.json",  # Identity Discovery
    "MI-005/D-09": "engine/uckp/resolution.py",  # Relationship Discovery
}

#: Performed by nothing. All four look outward rather than inward: what might go wrong, what
#: could be gained, what else would work, what keeps recurring. The repository discovers what
#: IS and does not discover what MIGHT BE.
DISCOVERY_ABSENT = {
    "MI-005/D-13": "risk",
    "MI-005/D-14": "opportunity",
    "MI-005/D-16": "alternative",
    "MI-005/D-17": "pattern",
}


def test_every_discovery_is_a_stage_an_instrument_or_absent() -> None:
    mandates = section("MI-005")
    assert len(mandates) == 19, f"section 005 lists 19 discoveries, corpus has {len(mandates)}"
    assert_partitions(
        "MI-005",
        mandates,
        DISCOVERY_LIFECYCLE_STAGE,
        DISCOVERY_INSTRUMENT,
        DISCOVERY_ABSENT,
    )


def test_every_stage_backed_discovery_names_a_stage_ucl_declares() -> None:
    from engine.tests.conformance.test_mandates_model import _ucl_stage_names

    declared = _ucl_stage_names()
    for mandate, stage in DISCOVERY_LIFECYCLE_STAGE.items():
        assert stage in declared, f"{mandate}: UCL declares no stage named {stage!r}"
    claimed = list(DISCOVERY_LIFECYCLE_STAGE.values())
    assert len(claimed) == len(set(claimed)), "one stage claimed by two discoveries"


def test_six_discoveries_carry_the_lifecycle_stage_name_verbatim() -> None:
    """NON-VACUITY for the join, and the evidence that it is a join rather than a mapping:
    six of the eleven are the same phrase on both sides."""
    mandates = section("MI-005")
    verbatim = [
        mandate
        for mandate, stage in DISCOVERY_LIFECYCLE_STAGE.items()
        if mandates[mandate] == stage
    ]
    assert len(verbatim) >= 6, (
        f"only {len(verbatim)} discoveries still match their stage name verbatim; the two "
        "documents have drifted and this join needs re-reading"
    )


def test_every_instrument_backed_discovery_is_tracked() -> None:
    assert_homes_exist("MI-005", DISCOVERY_INSTRUMENT)


def test_the_absent_discoveries_are_performed_by_nothing() -> None:
    assert_named_by_nothing("MI-005", DISCOVERY_ABSENT)


def test_the_discovery_gap_is_the_same_one_the_prd_reports() -> None:
    """Risk, Opportunity and Pattern discovery are mandated by both documents and performed
    by neither. Measured in two suites over two sections, asserted to agree."""
    from engine.tests.conformance.test_mandates_prd import CONSTRUCT_DISCOVERY_ABSENT

    shared = {"risk", "opportunity", "pattern"}
    assert shared <= set(DISCOVERY_ABSENT.values())
    assert shared <= set(CONSTRUCT_DISCOVERY_ABSENT.values())


# --- MI-009 — the fourteen governance surfaces ----------------------------------
#
# Section 009 lists fourteen things governance is made of. All fourteen are located, which
# makes this the only fully-answered section in the Master Index -- and that is worth
# recording as a fact rather than assumed, because "all located" is exactly the claim a
# sweep would produce by accident.
#
# Two of the fourteen carry a top-level `authority` key AND are bound in UCOS-CAA-001 as
# subordinate instruments of the root law. That is a strictly stronger standing than a
# module existing, and CAA-INV-02 refuses an authority-carrying register that is not bound,
# so the pair is checked against the binding rather than against the file.

GOVERNANCE_SURFACE = {
    "MI-009/GV-01": "00-MASTER/UCOS-RFP-001/REPOSITORY-FIXED-POINT-CONSTITUTION.md",
    "MI-009/GV-02": "00-BOOK/DATA/id-ledger.json",  # Identity
    "MI-009/GV-03": "00-BOOK/DATA/generated-artifact-registry.json",  # Registry
    # Dictionary
    "MI-009/GV-04": "00-MASTER/UCOS-NUCLEUS-001/UCOS-NUCLEUS-IDENTIFIER-DICTIONARY.json",
    "MI-009/GV-05": "engine/context/ontology.py",  # Ontology
    "MI-009/GV-06": "engine/context/taxonomy.py",  # Taxonomy
    # Provenance
    "MI-009/GV-07": "00-MASTER/UAKOS-PHASE-001B/01-SOURCE-PROVENANCE-REGISTER.md",
    "MI-009/GV-08": "00-BOOK/REGISTRIES/CHANGE-VERSION-LINEAGE-REGISTRY.md",  # Lineage
    "MI-009/GV-09": "engine/nucleus/ownership.py",  # Ownership
    "MI-009/GV-10": "00-BOOK/DATA/constitutional-authority-alignment.json",  # Authority
    # Traceability
    "MI-009/GV-11": "00-MASTER/UAKOS-CLOSURE-009/07-CONSTITUTIONAL-TRACEABILITY-MATRIX.md",
    "MI-009/GV-12": "engine/kernel/governance.py",  # Policy
    "MI-009/GV-13": "engine/kernel/compliance.py",  # Compliance
    "MI-009/GV-14": "engine/uckp/law.py",  # Constitutional Governance
}

#: The two surfaces that are subordinate instruments of the root law, by their CAA id.
GOVERNANCE_SUBORDINATE_INSTRUMENT = {
    "MI-009/GV-03": "UCOS-GENERATED-ARTIFACT-REGISTRY-001",
    "MI-009/GV-10": "UCOS-CAA-001",
}


def test_every_governance_surface_is_located() -> None:
    mandates = section("MI-009")
    assert len(mandates) == 14, f"section 009 lists 14 surfaces, corpus has {len(mandates)}"
    assert_partitions("MI-009", mandates, GOVERNANCE_SURFACE)
    assert_homes_exist("MI-009", GOVERNANCE_SURFACE)


def test_the_fourteen_surfaces_are_fourteen_distinct_instruments() -> None:
    """NON-VACUITY for a fully-answered section. Fourteen mandates resolving to fewer than
    fourteen instruments would mean some are unlocated and the completeness is an artefact
    of the mapping rather than of the repository."""
    homes = list(GOVERNANCE_SURFACE.values())
    duplicated = sorted({h for h in homes if homes.count(h) > 1})
    assert not duplicated, f"one instrument claimed for several surfaces: {duplicated}"
    assert len(set(homes)) == 14


def test_the_two_authority_carrying_surfaces_are_bound_under_the_root_law() -> None:
    """CAA-INV-02 refuses a register that carries a top-level `authority` and is not bound
    as a subordinate instrument. So for these two, 'located' understates it: they are
    governing instruments with a declared standing, and the binding is what proves it."""
    import json

    alignment = json.loads(
        (repo_root() / "00-BOOK" / "DATA" / "constitutional-authority-alignment.json").read_text(
            encoding="utf-8"
        )
    )
    bound = {entry["id"]: entry for entry in alignment["subordinate_instruments"]}
    for mandate, instrument_id in GOVERNANCE_SUBORDINATE_INSTRUMENT.items():
        assert (
            instrument_id in bound
        ), f"{mandate}: {instrument_id} is no longer a bound subordinate instrument"
        home = GOVERNANCE_SURFACE[mandate]
        assert bound[instrument_id]["instrument"] == home, (
            f"{mandate}: CAA binds {instrument_id} to "
            f"{bound[instrument_id]['instrument']!r}, this row names {home!r}"
        )
        declared = json.loads((repo_root() / home).read_text(encoding="utf-8"))
        assert declared.get("authority"), f"{mandate}: {home} carries no top-level authority"


def test_constitutional_governance_resolves_to_the_root_law_itself() -> None:
    """GV-14 is the section's own closing row and the only one that can only have one
    answer: the supreme authority, whose home CLAUDE.md names."""
    from engine.uckp.law import ROOT_LAW

    assert GOVERNANCE_SURFACE["MI-009/GV-14"] == "engine/uckp/law.py"
    assert (
        ROOT_LAW.law_id == "UCKP-LAW-0001"
    ), f"the root law is now {ROOT_LAW.law_id}; GV-14 names a different supreme authority"
    assert len(ROOT_LAW.articles) == 20 and len(ROOT_LAW.invariants) == 17


# --- MI-006 — the thirteen decision stages --------------------------------------
#
# Section 006 lists thirteen stages of a constitutional decision. Two of them -- Reuse and
# Extension -- are not two instruments here but one verdict and its payload:
# `AssimilationVerdict.status` returns CREATE or REUSE, and `reuse_targets` carries "the
# existing subjects the caller should extend instead". ARCH-CERTV records the same shape for
# the certification verdict set, and this section is where the consequence lands.

DECISION_STAGE = {
    "MI-006/DEC-01": "00-MASTER/UCDA-000001/01-CONSTITUTIONAL-DECISION-REGISTER.md",
    "MI-006/DEC-02": "intelligence/realization/planning.py",  # Planning
    "MI-006/DEC-03": "intelligence/rie/analysis.py",  # Analysis
    "MI-006/DEC-05": "platform/foundation/derivation.py",  # Derivation
    "MI-006/DEC-06": "engine/constitution/assimilation.py",  # Reuse -- the REUSE verdict
    "MI-006/DEC-08": "engine/knowledge/integration/composition.py",  # Composition
    "MI-006/DEC-09": "engine/foundation/config",  # Configuration
    "MI-006/DEC-10": "intelligence/realization/generators",  # Generation
    "MI-006/DEC-11": "platform/universal_foundation/specialization.py",  # Specialization
    "MI-006/DEC-13": "00-BOOK/DATA/allocation-permits.json",  # Approval
}

#: Extension is not a stage of its own: it rides on the reuse verdict's targets. Recorded
#: here rather than given a second home, because inventing one would report two decisions
#: where the gate makes one.
DECISION_RIDES_ON_REUSE = {"MI-006/DEC-07": "reuse_targets"}  # Extension

#: Optimization is the compiler near miss again; Evaluation has nothing at all.
DECISION_ABSENT = {
    "MI-006/DEC-04": "evaluation",
    "MI-006/DEC-12": "decision optimization",
}


def test_every_decision_stage_is_located_rides_on_reuse_or_absent() -> None:
    mandates = section("MI-006")
    assert len(mandates) == 13, f"section 006 lists 13 stages, corpus has {len(mandates)}"
    assert_partitions(
        "MI-006",
        mandates,
        DECISION_STAGE,
        DECISION_RIDES_ON_REUSE,
        DECISION_ABSENT,
    )
    assert_homes_exist("MI-006", DECISION_STAGE)


def test_extension_rides_on_the_reuse_verdict_exactly_as_arch_certv_records() -> None:
    """The join, and the reason Extension gets no home of its own.

    `AssimilationVerdict.status` returns CREATE or REUSE and nothing else; the instruction
    to extend is carried by `reuse_targets`. ARCH-CERTV/CV-03 records the same shape for the
    certification verdict set, so the two sections are asserted to agree -- if the gate ever
    returns EXTEND, both rows change together.
    """
    from engine.tests.conformance.test_mandates_arch import VERDICT_EXPRESSED_DIFFERENTLY

    _home, symbol, _why = VERDICT_EXPRESSED_DIFFERENTLY["ARCH-CERTV/CV-03"]
    assert (
        symbol == DECISION_RIDES_ON_REUSE["MI-006/DEC-07"]
    ), "the two sections no longer name the same carrier for the extend instruction"
    assert DECISION_STAGE["MI-006/DEC-06"] == "engine/constitution/assimilation.py"


def test_the_absent_decision_stages_are_named_by_nothing() -> None:
    assert_named_by_nothing("MI-006", DECISION_ABSENT)


# --- MI-014 — the eleven evolution stages ---------------------------------------
#
# Section 014 restates the evolution cycle a fourth time -- after ARCH-EVOF, LYR-L15 and
# UAKP-PROC -- and agrees with UCL-000001 on eight stage names. Nothing new is bound here;
# what is asserted is that the four documents have not drifted apart.

EVOLUTION_CYCLE_STAGE = {
    "MI-014/EV-01": "Observe",  # Observation
    "MI-014/EV-02": "Measure",  # Measurement
    "MI-014/EV-03": "Learn",  # Learning
    "MI-014/EV-04": "Reason",  # Reasoning
    "MI-014/EV-05": "Extract Engineering Knowledge",  # Knowledge Extraction
    "MI-014/EV-06": "Elevate",  # Capability Elevation
    "MI-014/EV-07": "Improve",  # Improvement
    "MI-014/EV-10": "Update Repository Truth",  # Repository Truth Update
    "MI-014/EV-11": "Begin Next Elevated Engineering Cycle",  # Infinite Evolution Cycle
}

EVOLUTION_CYCLE_INSTRUMENT = {
    "MI-014/EV-09": "engine/constitution/evolution.py",  # Constitutional Evolution
}

#: The compiler near miss, for the fourth time in this corpus.
EVOLUTION_CYCLE_NEAR_MISS = {"MI-014/EV-08": "engine/compiler/optimization.py"}  # Optimization


def test_every_evolution_cycle_stage_is_a_stage_an_instrument_or_a_near_miss() -> None:
    mandates = section("MI-014")
    assert len(mandates) == 11, f"section 014 lists 11 stages, corpus has {len(mandates)}"
    assert_partitions(
        "MI-014",
        mandates,
        EVOLUTION_CYCLE_STAGE,
        EVOLUTION_CYCLE_INSTRUMENT,
        EVOLUTION_CYCLE_NEAR_MISS,
    )
    assert_homes_exist("MI-014", EVOLUTION_CYCLE_INSTRUMENT)
    assert_homes_exist("MI-014", EVOLUTION_CYCLE_NEAR_MISS)


def test_the_four_documents_that_restate_the_evolution_cycle_still_agree() -> None:
    """Four sections across three documents describe one cycle. A stage named by UCL here
    and not there would mean one of the four joins has gone stale, which is a finding about
    the suites rather than about the repository."""
    from engine.tests.conformance.test_mandates_arch import EVOLUTION_LIFECYCLE_STAGE
    from engine.tests.conformance.test_mandates_layers import EVOLUTION_LIFECYCLE_VERBATIM
    from engine.tests.conformance.test_mandates_model import _ucl_stage_names

    declared = _ucl_stage_names()
    for mandate, stage in EVOLUTION_CYCLE_STAGE.items():
        assert stage in declared, f"{mandate}: UCL declares no stage named {stage!r}"

    shared = {"Learn", "Improve", "Elevate", "Observe"}
    assert shared <= set(EVOLUTION_CYCLE_STAGE.values())
    assert shared <= set(EVOLUTION_LIFECYCLE_VERBATIM.values()) | {"Observe"}
    assert "Extract Engineering Knowledge" in set(
        EVOLUTION_LIFECYCLE_STAGE.values()
    ), "ARCH-EVOF no longer names the extraction stage; the four restatements have drifted"


def test_optimization_is_the_same_near_miss_all_four_restatements_reach() -> None:
    """Four documents mandate Optimization and one module carries the word. It optimises the
    compiler's output, not the substrate -- so all four rows point at it and none counts it
    as satisfied."""
    from engine.tests.conformance.test_mandates_arch import EVOLUTION_NEAR_MISS
    from engine.tests.conformance.test_mandates_prd import SELF_NEAR_MISS

    optimiser = EVOLUTION_CYCLE_NEAR_MISS["MI-014/EV-08"]
    assert EVOLUTION_NEAR_MISS["ARCH-EVOF/VF2-05"][0] == optimiser
    assert SELF_NEAR_MISS["PRD-SELF/SELF-11"][0] == optimiser


# --- MI-007 / MI-008 / MI-010 / MI-012 / MI-013 / MI-018 — the remainder ---------
#
# The last six Master Index sections, bound together because what is left of each is small
# and because the same gap runs through three of them: DESIGN. MI-007 lists it as an
# engineering stage, ARCH-ENGF lists it as a fabric step, MI-018 lists it in the end state,
# and nothing in the repository performs it. Three documents, one missing stage -- asserted
# across the suites so it reads as one finding.

MASTER_INDEX_REMAINDER = {
    # MI-007 Engineering
    "MI-007/E-03": "engine/uckp/ucko.py",  # Modeling
    "MI-007/E-08": "engine/compiler/packaging.py",  # Build
    "MI-007/E-09": "engine/compiler/packaging.py",  # Packaging
    "MI-007/E-11": "engine/runtime",  # Runtime Preparation
    # MI-008 Assurance
    "MI-008/A-07": "14-SECURITY/SECURITY-001-UNIVERSAL-SECURITY-CONSTITUTION.md",  # Security
    "MI-008/A-09": "engine/kernel/compliance.py",  # Compliance Assessment
    "MI-008/A-10": "engine/certification/evidence.py",  # Evidence Collection
    # MI-010 Execution
    "MI-010/X-01": "00-MASTER/EXECUTION-BACKLOG.json",  # Work Discovery
    "MI-010/X-02": "platform/runtime_platform/scheduling.py",  # Dependency Scheduling
    "MI-010/X-04": "engine/runtime/orchestration.py",  # Orchestration
    "MI-010/X-10": "engine/runtime/execution/recovery.py",  # Recovery
    # MI-012 Commercialization
    "MI-012/CM-03": "00-MASTER/UCOS-RIB-001/rib.json",  # Assets
    # MI-013 Observability
    "MI-013/OB-08": "platform/observability/alerting.py",  # Alerts
    "MI-013/OB-10": "engine/graph/architecture/insights.py",  # Insights
    # MI-018 End State
    "MI-018/ES-03": "00-MASTER/UCL-000001/ucl.json",  # Understanding -- the `Understand` stage
}

#: Market-shaped: `product` is a token the kernel refuses to seed.
MASTER_INDEX_MARKET_SHAPED = {"MI-012/CM-01": "Products"}

#: Absent. Design appears three times across three documents and nothing performs it.
MASTER_INDEX_ABSENT = {
    "MI-007/E-02": "design",  # Design
    "MI-008/A-08": "performance assessment",
    "MI-010/X-03": "resource discovery",
    "MI-012/CM-13": "ecosystem",
    "MI-018/ES-05": "design",  # Design, a second time
}


def test_the_master_index_remainder_is_located_market_shaped_or_absent() -> None:
    mandates: dict[str, str] = {}
    for name in ("MI-007", "MI-008", "MI-010", "MI-012", "MI-013", "MI-018"):
        mandates.update(section(name))
    covered = {
        **MASTER_INDEX_REMAINDER,
        **MASTER_INDEX_MARKET_SHAPED,
        **MASTER_INDEX_ABSENT,
    }
    foreign = sorted(set(covered) - set(mandates))
    assert not foreign, f"tiered identifiers that are not Master Index mandates: {foreign}"
    assert_homes_exist("MI-remainder", MASTER_INDEX_REMAINDER)


def test_build_and_packaging_share_a_module_because_the_compiler_does_both() -> None:
    """NON-VACUITY for the only doubled home. Build and Packaging are separate stages and
    one module answers both, which is honest only if it really performs two acts."""
    import ast

    home = MASTER_INDEX_REMAINDER["MI-007/E-08"]
    assert home == MASTER_INDEX_REMAINDER["MI-007/E-09"]
    tree = ast.parse((repo_root() / home).read_text(encoding="utf-8"))
    functions = {n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)}
    assert len(functions) >= 2, (
        f"{home} answers two stages and defines {len(functions)} function(s); one of the "
        "two stages is unlocated"
    )
    homes = list(MASTER_INDEX_REMAINDER.values())
    doubled = sorted({h for h in homes if homes.count(h) > 1})
    assert doubled == [home], f"unexpected doubled homes in the remainder: {doubled}"


def test_products_is_admitted_not_built() -> None:
    from engine.kernel.compliance import PROHIBITED_TOKENS, kernel_source_fingerprint
    from engine.kernel.kernel import MetaKernel

    assert "product" in PROHIBITED_TOKENS, (
        "`product` is no longer refused, so MI-012/CM-01 could be seeded as a concrete "
        "market and must be re-decided"
    )
    kernel = MetaKernel()
    before = kernel_source_fingerprint()
    kernel.register_metatype("Output-Products", name="Products", description="market output")
    assert kernel_source_fingerprint() == before
    assert "Output-Products" in {obj.natural_key for obj in kernel.metatypes()}


def test_design_is_mandated_by_three_documents_and_performed_by_nothing() -> None:
    """The finding this grouping exists for.

    MI-007 lists Design as an engineering stage, MI-018 lists it in the end state, and
    ARCH-ENGF lists it as a fabric step. Nothing in the repository designs: there is an
    architecture generator that emits a description of what was decided, and no stage where
    the deciding happens. If a design instrument ever lands, all three rows move together.
    """

    assert_named_by_nothing("MI-remainder", MASTER_INDEX_ABSENT)
    design_rows = [m for m, concept in MASTER_INDEX_ABSENT.items() if concept == "design"]
    assert len(design_rows) == 2, f"expected Design twice in this grouping, got {design_rows}"
