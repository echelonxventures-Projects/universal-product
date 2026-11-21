"""UCXI-000001 Parts 02/03 — taxonomy and ontology tests.

The properties asserted here are the ones the rest of the layer relies on: the fifteen
universal kinds are classified and specified, unknown values fail loudly rather than
defaulting, and both structures are *open* — a future context type is admitted as data
and immediately behaves like any other kind.
"""

from __future__ import annotations

import pytest

from engine.context.errors import LifecycleTransitionError, OntologyError, TaxonomyError
from engine.context.ontology import (
    UNIVERSAL_DIMENSIONS,
    UNIVERSAL_ONTOLOGY,
    UNKNOWN,
    ContextOntology,
    DimensionSpec,
    RelationRule,
)
from engine.context.taxonomy import (
    ROOT_TAXON,
    UNIVERSAL_KINDS,
    UNIVERSAL_TAXA,
    UNIVERSAL_TAXONOMY,
    ContextAuthority,
    ContextKind,
    ContextLifecycle,
    ContextRelation,
    ContextTaxon,
    ContextTaxonomy,
)
from engine.tests.context.conftest import future_dimensions, future_taxon

# --------------------------------------------------------------------------- kinds


def test_sixteen_universal_kinds_are_declared() -> None:
    assert len(UNIVERSAL_KINDS) == 16
    assert ContextKind.EXISTENCE.value == "existence"
    assert "cultural" in ContextKind.values()
    # The sixteenth (ADR-0005). Measurement is universal because every assertion is
    # made in some system of measurement; leaving it implicit assumes one.
    assert "measurement" in ContextKind.values()


def test_unknown_kind_fails_loudly() -> None:
    with pytest.raises(TaxonomyError):
        ContextKind.coerce("astral")


def test_kind_coercion_is_idempotent() -> None:
    assert ContextKind.coerce(ContextKind.TEMPORAL) is ContextKind.TEMPORAL
    assert ContextKind.coerce("temporal") is ContextKind.TEMPORAL


# --------------------------------------------------------------------- authority


def test_authority_precedence_is_total_and_ordered() -> None:
    ranks = [authority.rank for authority in ContextAuthority]
    assert ranks == sorted(ranks)
    assert len(set(ranks)) == len(ranks)
    assert ContextAuthority.CONSTITUTIONAL.outranks(ContextAuthority.OBSERVED)
    assert not ContextAuthority.INFERRED.outranks(ContextAuthority.OPERATIONAL)


def test_unknown_authority_fails_loudly() -> None:
    with pytest.raises(TaxonomyError):
        ContextAuthority.coerce("vibes")


# --------------------------------------------------------------------- lifecycle


def test_lifecycle_transitions_are_enforced() -> None:
    assert ContextLifecycle.DECLARED.can_transition_to(ContextLifecycle.REGISTERED)
    assert not ContextLifecycle.DECLARED.can_transition_to(ContextLifecycle.ACTIVE)
    with pytest.raises(LifecycleTransitionError):
        ContextLifecycle.DECLARED.require_transition(ContextLifecycle.ACTIVE)
    ContextLifecycle.REGISTERED.require_transition(ContextLifecycle.RESOLVED)


def test_lifecycle_active_and_terminal_flags() -> None:
    assert ContextLifecycle.ACTIVE.is_active
    assert not ContextLifecycle.ARCHIVED.is_active
    assert ContextLifecycle.ARCHIVED.is_terminal
    assert not ContextLifecycle.ACTIVE.is_terminal


def test_unknown_lifecycle_fails_loudly() -> None:
    with pytest.raises(TaxonomyError):
        ContextLifecycle.coerce("mothballed")


# ---------------------------------------------------------------------- relations


def test_relation_classes() -> None:
    assert ContextRelation.EQUIVALENT_TO.is_symmetric
    assert not ContextRelation.CONTAINS.is_symmetric
    assert ContextRelation.CONTAINS.is_hierarchical
    assert not ContextRelation.FEDERATES.is_hierarchical
    with pytest.raises(TaxonomyError):
        ContextRelation.coerce("vibes-with")


# ---------------------------------------------------------------------- taxonomy


def test_universal_taxonomy_shape() -> None:
    assert len(UNIVERSAL_TAXONOMY) == 17  # the root plus sixteen universal taxa
    assert UNIVERSAL_TAXONOMY.has(ROOT_TAXON)
    assert len(UNIVERSAL_TAXONOMY.universal_kinds()) == 16
    assert UNIVERSAL_TAXONOMY.future_kinds() == ()
    assert UNIVERSAL_TAXONOMY.depth("CTX-TEMPORAL") == 1
    assert UNIVERSAL_TAXONOMY.ancestors("CTX-TEMPORAL") == (ROOT_TAXON,)
    assert len(UNIVERSAL_TAXONOMY.descendants(ROOT_TAXON)) == 16
    assert UNIVERSAL_TAXONOMY.children(ROOT_TAXON)


def test_taxon_lookup_by_kind_and_universality() -> None:
    taxon = UNIVERSAL_TAXONOMY.taxon_for_kind(ContextKind.SECURITY)
    assert taxon.taxon_id == "CTX-SECURITY"
    assert UNIVERSAL_TAXONOMY.is_universal("security")
    assert not UNIVERSAL_TAXONOMY.is_universal("quantum")
    with pytest.raises(TaxonomyError):
        UNIVERSAL_TAXONOMY.taxon_for_kind("quantum")
    with pytest.raises(TaxonomyError):
        UNIVERSAL_TAXONOMY.taxon("CTX-NOPE")


def test_taxonomy_admits_a_future_context_type() -> None:
    extended = UNIVERSAL_TAXONOMY.extend(future_taxon())
    assert len(extended) == 18
    assert extended.future_kinds() == ("quantum",)
    assert extended.is_universal("quantum") is False
    assert extended.taxon_for_kind("quantum").title == "Quantum Context"
    # extension is non-mutating: the universal instance is untouched
    assert len(UNIVERSAL_TAXONOMY) == 17


def test_taxonomy_extension_is_bounded() -> None:
    with pytest.raises(TaxonomyError):  # duplicate taxon
        UNIVERSAL_TAXONOMY.extend(
            ContextTaxon(taxon_id="CTX-TEMPORAL", kind="x", title="X", parent=ROOT_TAXON)
        )
    with pytest.raises(TaxonomyError):  # universality cannot be granted
        UNIVERSAL_TAXONOMY.extend(
            ContextTaxon(taxon_id="CTX-X", kind="x", title="X", parent=ROOT_TAXON, universal=True)
        )
    with pytest.raises(TaxonomyError):  # a second root
        UNIVERSAL_TAXONOMY.extend(ContextTaxon(taxon_id="CTX-X", kind="x", title="X"))
    with pytest.raises(TaxonomyError):  # unknown parent
        UNIVERSAL_TAXONOMY.extend(
            ContextTaxon(taxon_id="CTX-X", kind="x", title="X", parent="CTX-NOPE")
        )
    with pytest.raises(TaxonomyError):  # kind already claimed
        UNIVERSAL_TAXONOMY.extend(
            ContextTaxon(taxon_id="CTX-X", kind="temporal", title="X", parent=ROOT_TAXON)
        )


def test_taxon_requires_non_empty_fields() -> None:
    with pytest.raises(TaxonomyError):
        ContextTaxon(taxon_id="", kind="x", title="X", parent=ROOT_TAXON)
    with pytest.raises(TaxonomyError):
        ContextTaxon(taxon_id="CTX-X", kind="x", title="X", parent="")


def test_taxonomy_refuses_a_cycle_and_a_detached_branch() -> None:
    taxa = (
        ContextTaxon(taxon_id=ROOT_TAXON, kind="context", title="root", universal=True),
        ContextTaxon(taxon_id="A", kind="a", title="A", parent="B"),
        ContextTaxon(taxon_id="B", kind="b", title="B", parent="A"),
    )
    with pytest.raises(TaxonomyError):
        ContextTaxonomy(taxa)


def test_taxonomy_serialises_deterministically() -> None:
    first = UNIVERSAL_TAXONOMY.to_dict()
    assert first == UNIVERSAL_TAXONOMY.to_dict()
    assert first["root"] == ROOT_TAXON
    assert len(first["taxa"]) == 17


# ---------------------------------------------------------------------- ontology


def test_every_universal_kind_has_a_declared_shape() -> None:
    for kind in UNIVERSAL_KINDS:
        specs = UNIVERSAL_ONTOLOGY.dimensions_for(kind)
        assert specs
        assert UNIVERSAL_ONTOLOGY.required_for(kind)
        assert any(spec.name == "note" and not spec.required for spec in specs)
    assert set(UNIVERSAL_ONTOLOGY.kinds()) == set(UNIVERSAL_DIMENSIONS)


def test_every_relation_has_a_rule() -> None:
    rules = {rule.relation for rule in UNIVERSAL_ONTOLOGY.rules()}
    assert rules == set(ContextRelation)


def test_value_checks_report_completeness_closure_and_type() -> None:
    findings = UNIVERSAL_ONTOLOGY.check_values(
        "temporal", {"reference_frame": "utc", "ordering": "causal"}
    )
    assert any("resolution" in finding for finding in findings)

    findings = UNIVERSAL_ONTOLOGY.check_values(
        "temporal",
        {"reference_frame": "utc", "ordering": "causal", "resolution": "s", "extra": 1},
    )
    assert any("not declared" in finding for finding in findings)

    findings = UNIVERSAL_ONTOLOGY.check_values(
        "temporal", {"reference_frame": 7, "ordering": "causal", "resolution": "s"}
    )
    assert any("expects string" in finding for finding in findings)


def test_unknown_sentinel_satisfies_any_dimension() -> None:
    findings = UNIVERSAL_ONTOLOGY.check_values(
        "security",
        {"classification": UNKNOWN, "trust_boundary": UNKNOWN, "controls": UNKNOWN},
    )
    assert findings == []


def test_require_values_is_fail_closed() -> None:
    with pytest.raises(OntologyError):
        UNIVERSAL_ONTOLOGY.require_values("temporal", {}, at="subject")
    with pytest.raises(OntologyError):
        UNIVERSAL_ONTOLOGY.dimensions_for("quantum")
    assert UNIVERSAL_ONTOLOGY.check_values("quantum", {}) == [
        "quantum: kind 'quantum' has no declared ontological shape"
    ]


def test_relation_rules_constrain_source_kinds() -> None:
    assert UNIVERSAL_ONTOLOGY.check_relation(ContextRelation.OBSERVES, "observer", "temporal") == []
    findings = UNIVERSAL_ONTOLOGY.check_relation(ContextRelation.OBSERVES, "temporal", "temporal")
    assert findings
    with pytest.raises(OntologyError):
        UNIVERSAL_ONTOLOGY.require_relation(ContextRelation.CONSTRAINS, "temporal", "spatial")
    UNIVERSAL_ONTOLOGY.require_relation(ContextRelation.CONSTRAINS, "governance", "spatial")


def test_spec_lookup_and_number_is_not_boolean() -> None:
    spec = UNIVERSAL_ONTOLOGY.spec_for("temporal", "resolution")
    assert spec is not None and spec.required
    assert UNIVERSAL_ONTOLOGY.spec_for("temporal", "nope") is None
    number = DimensionSpec(name="n", value_type="number", required=True)
    assert number.accepts(3) and number.accepts(1.5)
    assert not number.accepts(True)


def test_ontology_admits_a_future_kind() -> None:
    extended = UNIVERSAL_ONTOLOGY.extend("quantum", future_dimensions())
    assert extended.specifies("quantum")
    assert extended.required_for("quantum") == ("basis",)
    assert extended.check_values("quantum", {"basis": "z"}) == []
    assert not UNIVERSAL_ONTOLOGY.specifies("quantum")  # non-mutating
    with pytest.raises(OntologyError):
        extended.extend("quantum", future_dimensions())
    with pytest.raises(OntologyError):
        UNIVERSAL_ONTOLOGY.extend("quantum", ())


def test_ontology_construction_refuses_bad_declarations() -> None:
    with pytest.raises(OntologyError):
        ContextOntology({"x": ()})
    with pytest.raises(OntologyError):
        ContextOntology(
            {
                "x": (
                    DimensionSpec(name="a", value_type="string", required=True),
                    DimensionSpec(name="a", value_type="string", required=False),
                )
            }
        )
    with pytest.raises(OntologyError):
        ContextOntology({"x": (DimensionSpec(name="a", value_type="string", required=False),)})
    with pytest.raises(OntologyError):
        DimensionSpec(name="a", value_type="quaternion", required=True)
    with pytest.raises(OntologyError):
        DimensionSpec(name=" ", value_type="string", required=True)


def test_ontology_refuses_duplicate_or_missing_relation_rules() -> None:
    duplicate = (
        RelationRule(relation=ContextRelation.CONTAINS),
        RelationRule(relation=ContextRelation.CONTAINS),
    )
    with pytest.raises(OntologyError):
        ContextOntology(UNIVERSAL_DIMENSIONS, duplicate)
    with pytest.raises(OntologyError):
        ContextOntology(UNIVERSAL_DIMENSIONS, (RelationRule(relation=ContextRelation.CONTAINS),))


def test_ontology_serialises_deterministically() -> None:
    payload = UNIVERSAL_ONTOLOGY.to_dict()
    assert payload == UNIVERSAL_ONTOLOGY.to_dict()
    assert payload["unknown_sentinel"] == UNKNOWN
    assert len(payload["relations"]) == len(ContextRelation)


# ---------------------------------------------------------------------------------------
# The taxonomy's constructor refuses a malformed classification before it is ever consulted
#
# CXL-01 says the classification of all context has exactly one root and that every taxon
# reaches it. That is asserted at CONSTRUCTION rather than by a separate validator, so the
# refusals live in `__init__` — and because every existing test builds the universal
# taxonomy or extends it lawfully, not one of them had run. A taxonomy that admitted a
# cycle would make `_assert_reaches` loop, and one that admitted two roots would make
# "the classification of all context" two classifications.
# ---------------------------------------------------------------------------------------


def _taxon(taxon_id: str, kind: str, parent: str | None = "CTX-ROOT") -> ContextTaxon:
    return ContextTaxon(
        taxon_id=taxon_id,
        kind=kind,
        title=f"Taxon {taxon_id}",
        parent=parent,
        description="A taxon declared for a refusal test.",
    )


def _root() -> ContextTaxon:
    return _taxon("CTX-ROOT", "root", parent=None)


def test_two_taxa_under_one_identifier_are_refused() -> None:
    """An identifier is what every registration, relation and evidence record cites. Two
    taxa sharing one would make every citation ambiguous, and the later declaration would
    silently win — a redefinition that reads as a registration."""
    with pytest.raises(TaxonomyError, match="duplicate taxon identifier") as excinfo:
        ContextTaxonomy((_root(), _taxon("CTX-A", "alpha"), _taxon("CTX-A", "beta")))
    assert excinfo.value.context["taxon"] == "CTX-A"


def test_two_taxa_claiming_one_context_kind_are_refused() -> None:
    """A KIND HAS EXACTLY ONE CLASSIFIER. Lookup by kind is how a declaration finds its
    taxon, so two claimants would make that lookup answer arbitrarily — and a context would
    be classified differently depending on which taxon happened to be indexed last."""
    with pytest.raises(TaxonomyError, match="same context kind") as excinfo:
        ContextTaxonomy((_root(), _taxon("CTX-A", "alpha"), _taxon("CTX-B", "alpha")))
    assert excinfo.value.context["kind"] == "alpha"
    assert excinfo.value.context["existing"] == "CTX-A"


@pytest.mark.parametrize(
    "taxa",
    [
        pytest.param((), id="no-root"),
        pytest.param(
            (_root(), ContextTaxon(taxon_id="CTX-OTHER", kind="other", title="t", parent=None)),
            id="two-roots",
        ),
    ],
)
def test_a_classification_without_exactly_one_root_is_refused(taxa) -> None:
    """Zero roots is a forest with no top; two is two classifications wearing one name. Both
    make "the classification of ALL context" false, and the count is checked rather than the
    first root being taken."""
    with pytest.raises(TaxonomyError, match="exactly one root"):
        ContextTaxonomy(taxa)


def test_a_taxon_naming_a_parent_nobody_declared_is_refused() -> None:
    """OPEN CLASSIFICATION IS NOT UNGROUNDED CLASSIFICATION. A future kind may be admitted
    at any time, and it still has to attach somewhere — a taxon whose parent does not exist
    is detached from the tree, so nothing above it governs it."""
    with pytest.raises(TaxonomyError, match="parent is not a declared taxon") as excinfo:
        ContextTaxonomy((_root(), _taxon("CTX-ORPHAN", "orphan", parent="CTX-GHOST")))
    assert excinfo.value.context["parent"] == "CTX-GHOST"


def test_a_taxon_that_cannot_reach_the_root_is_refused() -> None:
    """Reachability is checked for EVERY taxon, not only for the ones just added.

    A branch whose members all name each other satisfies "my parent is declared" and still
    never reaches the root. It would be a second classification hiding inside the first, and
    the walk that finds it is the same one every ancestry query uses.
    """
    detached = (
        _root(),
        _taxon("CTX-A", "alpha", parent="CTX-B"),
        _taxon("CTX-B", "beta", parent="CTX-A"),
    )
    with pytest.raises(TaxonomyError) as excinfo:
        ContextTaxonomy(detached)
    assert "cycle in the classification tree" in str(excinfo.value)
    assert excinfo.value.context["taxon"] in {"CTX-A", "CTX-B"}


def test_the_taxonomy_exposes_the_taxa_it_holds() -> None:
    """The accessor every consumer reads the classification through. A taxonomy whose
    contents could only be reached one lookup at a time would make "is this classification
    complete" a question nobody could ask."""
    taxonomy = ContextTaxonomy()
    listed = taxonomy.taxa()

    assert len(listed) == len(UNIVERSAL_TAXA)
    assert {t.taxon_id for t in listed} == {t.taxon_id for t in UNIVERSAL_TAXA}
    assert listed == taxonomy.taxa(), "the listing is not stable"


def test_the_taxonomy_lists_the_identifiers_it_holds() -> None:
    """``taxon_ids`` is the cheap enumeration — the ids alone, for a consumer that only needs
    to know what exists. Without it, "which taxa are declared" costs a full object list."""
    taxonomy = ContextTaxonomy()

    assert taxonomy.taxon_ids() == tuple(t.taxon_id for t in taxonomy.taxa())
    assert ROOT_TAXON in taxonomy.taxon_ids()
    assert len(taxonomy.taxon_ids()) == len(taxonomy)


def test_a_taxon_whose_chain_ends_somewhere_other_than_the_root_is_refused() -> None:
    """A WALK THAT ENDS WITHOUT REACHING THE ROOT AND WITHOUT REPEATING ITSELF.

    Constructing that shape is impossible through the constructor — a chain terminating at a
    parentless taxon means a SECOND root, and the one-root check refuses that first. So the
    branch is reached by walking a taxonomy mutated after construction, which is the state a
    caller reaching into ``_taxa`` produces. The two refusals are separate because they mean
    different things: a cycle is a loop, and this is a detached branch.
    """
    taxonomy = ContextTaxonomy(
        (
            _root(),
            _taxon("CTX-A", "alpha"),
        )
    )
    detached = ContextTaxon(
        taxon_id="CTX-A", kind="alpha", title="A", parent=None, description="detached"
    )
    taxonomy._taxa["CTX-A"] = detached  # noqa: SLF001 - deliberate corruption

    with pytest.raises(TaxonomyError, match="does not reach the root") as excinfo:
        taxonomy._assert_reaches("CTX-A", ROOT_TAXON)  # noqa: SLF001
    assert excinfo.value.context["taxon"] == "CTX-A"


# ------------------------------------------------- the Layer-2 mandate, bound to the code
#
# The Substrate Layer Architecture mandates fourteen Context Dimensions at Layer 2. Until
# now nothing tied that mandate to UCXI-000001, so a requirements sweep could locate the
# CODE (engine/context/taxonomy.py) and the WORDS (prose determinations under 00-MASTER/)
# without either one answering for the other. These three tests are that binding, and they
# are deliberately written to fail if the mandate and the implementation drift apart.
#
# Measured when written: twelve of the fourteen resolve to a universal kind, one names the
# extension mechanism rather than a kind, and exactly one — Physical Context — has no
# universal kind at all. That last one is not papered over below; it is the case that
# proves the open-taxonomy property on a real mandate instead of on a fixture.

MANDATED_CONTEXT_DIMENSIONS = (
    "Spatial Context",
    "Temporal Context",
    "Physical Context",
    "Environmental Context",
    "Cultural Context",
    "Linguistic Context",
    "Economic Context",
    "Governance Context",
    "Regulatory Context",
    "Identity Context",
    "Security Context",
    "Knowledge Context",
    "Computational Context",
    "Future Context Types",
)

#: The mandate's label, and the ContextKind it resolves to. "Future Context Types" and
#: "Physical Context" are absent by measurement, and each has its own test below.
MANDATE_TO_KIND = {
    "Spatial Context": ContextKind.SPATIAL,
    "Temporal Context": ContextKind.TEMPORAL,
    "Environmental Context": ContextKind.ENVIRONMENTAL,
    "Cultural Context": ContextKind.CULTURAL,
    "Linguistic Context": ContextKind.LINGUISTIC,
    "Economic Context": ContextKind.ECONOMIC,
    "Governance Context": ContextKind.GOVERNANCE,
    "Regulatory Context": ContextKind.REGULATORY,
    "Identity Context": ContextKind.IDENTITY,
    "Security Context": ContextKind.SECURITY,
    "Knowledge Context": ContextKind.KNOWLEDGE,
    "Computational Context": ContextKind.COMPUTATIONAL,
}


def test_every_mandated_context_dimension_resolves_to_a_declared_kind() -> None:
    """Twelve of the fourteen are universal taxa, reachable by the mandate's own name."""
    assert len(MANDATED_CONTEXT_DIMENSIONS) == 14, "the Layer-2 mandate lists fourteen"

    for label, kind in MANDATE_TO_KIND.items():
        taxon = UNIVERSAL_TAXONOMY.taxon_for_kind(kind)
        assert UNIVERSAL_TAXONOMY.is_universal(kind.value), (
            f"the mandated dimension {label!r} resolves to kind {kind.value!r}, which the "
            "taxonomy does not carry as universal"
        )
        assert taxon.title, f"{label!r} resolves to a taxon with no title"

    # Non-vacuity: the map must not have quietly lost a dimension. Two are accounted for
    # by the two tests below, and every remaining mandate must appear here.
    accounted = set(MANDATE_TO_KIND) | {"Physical Context", "Future Context Types"}
    assert accounted == set(MANDATED_CONTEXT_DIMENSIONS), (
        "a mandated Layer-2 dimension is neither mapped to a kind nor separately "
        f"accounted for: {sorted(set(MANDATED_CONTEXT_DIMENSIONS) - accounted)}"
    )


def test_future_context_types_names_the_extension_mechanism_not_a_kind() -> None:
    """The fourteenth mandate is a PROPERTY of the taxonomy, so it must not be a taxon.

    Declaring `future` as a universal kind would be the error the mandate warns against:
    a terminal taxonomy that has merely reserved a slot labelled "future".
    """
    assert "future" not in {kind.value for kind in ContextKind}
    assert UNIVERSAL_TAXONOMY.future_kinds() == (), (
        "the universal taxonomy ships with a future kind already in it, so 'future types' "
        "has been seeded rather than left open"
    )
    assert hasattr(UNIVERSAL_TAXONOMY, "extend"), "no admission mechanism for a future type"


def test_the_one_mandated_dimension_the_universal_set_lacks_is_admitted_as_data() -> None:
    """Physical Context — the P-002 'No Terminal Taxonomy' claim, on a real mandate.

    Layer 2 mandates it; the sixteen universal kinds do not carry it. The claim under test
    is NOT that the taxonomy already knows every dimension — it is that a dimension it does
    not know is admitted **without editing this layer**. So the gap is the experiment.

    If a later change makes `physical` universal, the first assertion fails and this test
    must be rewritten to pick another absent dimension. That is intended: the property
    needs a genuinely unknown kind to be proved against, and a fixture kind like `quantum`
    proves less than a kind the mandate actually asks for.
    """
    assert "physical" not in {kind.value for kind in ContextKind}, (
        "physical is now a universal kind — this test's premise is gone and it must be "
        "re-pointed at a dimension the universal set genuinely lacks"
    )

    extended = UNIVERSAL_TAXONOMY.extend(
        ContextTaxon(
            taxon_id="CTX-PHYSICAL",
            kind="physical",
            title="Physical Context",
            parent=ROOT_TAXON,
            description="Layer-2 mandated dimension, admitted as data (CXL-02).",
        )
    )

    assert extended.taxon_for_kind("physical").title == "Physical Context"
    assert extended.future_kinds() == ("physical",)
    assert extended.is_universal("physical") is False, (
        "extension granted universality, which would let a later mandate rewrite the "
        "constitutionally-present set from outside"
    )
    assert len(extended) == len(UNIVERSAL_TAXONOMY) + 1
    # Non-mutating, so admitting a dimension cannot change what every other caller sees.
    assert len(UNIVERSAL_TAXONOMY) == 17
    assert UNIVERSAL_TAXONOMY.future_kinds() == ()
