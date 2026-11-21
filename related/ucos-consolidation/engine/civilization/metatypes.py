"""Meta-Civilization vocabulary — expressed as DATA, seeded as kernel meta-types.

This layer introduces no new kernel code for civilization concepts. It *registers* a small
vocabulary of facet meta-types into the kernel, and then models:

    * a **dimension** as a registered kernel meta-type (open set) tagged with the role
      :data:`DIMENSION_ROLE`, plus a governed declaration object carrying its facets;
    * a **capability** as a registered ``MetaObject`` declaring what it requires, which
      dimensions it is bound to, and which policies govern it;
    * a **generation stratum** as a registered kernel meta-type ordered by a declared
      predecessor, so the generation chain may be refined without a code change; and
    * a **constitutional operating system** as a registered kernel meta-type — which is why
      the catalogue of operating systems is open and no list of them appears anywhere.

Adding a facet, a dimension, a capability, a stratum, or an operating system is therefore a
registration — never a change to this layer. Nothing here names a language, a currency, a
country, a calendar, a jurisdiction, a cloud, a vendor, a technology, a reality or an
existence model.
"""

from __future__ import annotations

#: Namespace for the civilization facet vocabulary meta-types.
CIVILIZATION_META_NS = "umk.civilization.meta"

#: Namespace for registered dimensions (each a kernel meta-type).
DIMENSION_META_NS = "umk.civilization.dimension.meta"

#: Namespace for dimension declaration objects (each classified by its dimension).
DIMENSION_NS = "umk.civilization.dimension"

#: Namespace for registered capability declarations.
CAPABILITY_NS = "umk.civilization.capability"

#: Namespace for registered generation strata (each a kernel meta-type).
STRATUM_META_NS = "umk.civilization.stratum.meta"

#: Namespace for registered constitutional operating systems (each a kernel meta-type).
OPERATING_SYSTEM_META_NS = "umk.civilization.os.meta"

#: Namespace for constitutional blueprints.
BLUEPRINT_NS = "umk.civilization.blueprint"

#: Namespace for generated stratum records.
GENERATION_NS = "umk.civilization.generation"

#: The attribute marker distinguishing a dimension meta-type from any other meta-type.
DIMENSION_ROLE = "civilization-dimension"

#: The attribute marker distinguishing a generation-stratum meta-type.
STRATUM_ROLE = "civilization-stratum"

#: The attribute marker distinguishing a constitutional-operating-system meta-type.
OPERATING_SYSTEM_ROLE = "constitutional-operating-system"

#: The relation asserting that a thing derives its authority from another thing. The
#: generation chain is expressed entirely in this one relation, so a longer or shorter
#: chain is a data change.
DERIVES_FROM = "derives-from"

#: The relation asserting dimensional specialization (unlimited specialization and, read in
#: reverse, unlimited generalization).
SPECIALIZES = "specializes"

#: The relation asserting that a thing is composed from another thing.
COMPOSES = "composes"

#: The relation asserting a capability dependency.
REQUIRES = "requires"

#: The mandatory facets every registered dimension satisfies, as DATA. These are the
#: properties the Universal Dimension Model requires of *every* dimension, present or
#: future; they are properties of dimensionhood, not a list of dimensions.
DIMENSION_FACETS: tuple[tuple[str, str], ...] = (
    ("discoverable", "The dimension is findable through registry discovery alone."),
    ("registerable", "The dimension is admitted by registration, never by a code edit."),
    ("governed", "Admission of the dimension is decided by governance."),
    ("composable", "The dimension composes with any other dimension."),
    ("extensible", "The dimension admits further specialization without redesign."),
    ("context-aware", "The dimension is interpreted within a declared context."),
    ("policy-aware", "Policy may bind to the dimension without altering it."),
    ("implementation-independent", "The dimension names no implementation."),
    ("unbounded", "The dimension declares no upper limit and no closed value set."),
)

#: The facet meta-type vocabulary registered into the kernel. Each names one facet of a
#: civilization concept; ordered for legibility only.
CIVILIZATION_FACETS: tuple[tuple[str, str], ...] = (
    ("Dimension", "An open axis along which any thing may be contextualized."),
    ("DimensionFacet", "A property every dimension satisfies."),
    ("DimensionComposition", "A dimension formed by composing other dimensions."),
    ("CapabilityDeclaration", "A declared capability with requirements and bindings."),
    ("CompositionPlan", "An execution order derived from declarations, not a pipeline."),
    ("CompositionStrategy", "A named rule by which a plan is derived from declarations."),
    ("GenerationStratum", "One ordered layer of the constitutional generation chain."),
    ("ConstitutionalBlueprint", "The declaration from which a system is generated."),
    ("ConstitutionalOperatingSystem", "A generated, self-governing constitutional system."),
    ("GeneratedArtefact", "A stratum record produced by constitutional generation."),
    ("MetaCivilization", "The layer that generates constitutional operating systems."),
)

#: The attribute keys a dimension declaration carries. Documented for legibility; the kernel
#: attribute map is open, so a dimension may carry additional keys without a layer change.
DIMENSION_ATTRIBUTE_KEYS: tuple[str, ...] = (
    "facets",
    "contexts",
    "policies",
)

#: Attribute keys a declaration may NOT carry. A dimension that legislates its own finite
#: value set, or a finite bound in *either* direction, contradicts the Universal Open-World
#: Expansion Principle, so it is refused at admission rather than accepted and documented as
#: an exception.
#:
#: The principle is directional-symmetric by its own terms — "no intrinsic limit in any
#: architectural direction" (DEC-MCOS-07) — so a floor is refused on the same ground as a
#: ceiling. A bound imposed by physical reality is not excluded from the model: it belongs to
#: a *policy over* a dimension, which is where a closed value set already belongs, never to
#: the axis itself.
FORBIDDEN_DIMENSION_KEYS: tuple[str, ...] = (
    # closed value set
    "closed_values",
    "allowed_values",
    "enum",
    # ceiling
    "max_cardinality",
    "upper_bound",
    # floor — the mirror of the two ceiling keys above
    "min_cardinality",
    "lower_bound",
    "minimum_values",
)


def facet_keys() -> tuple[str, ...]:
    """The natural keys of the civilization facet meta-types (deterministically ordered)."""
    return tuple(sorted(key for key, _desc in CIVILIZATION_FACETS))


def dimension_facet_keys() -> tuple[str, ...]:
    """The mandatory dimension facet names (deterministically ordered)."""
    return tuple(sorted(key for key, _desc in DIMENSION_FACETS))


__all__ = [
    "CIVILIZATION_META_NS",
    "DIMENSION_META_NS",
    "DIMENSION_NS",
    "CAPABILITY_NS",
    "STRATUM_META_NS",
    "OPERATING_SYSTEM_META_NS",
    "BLUEPRINT_NS",
    "GENERATION_NS",
    "DIMENSION_ROLE",
    "STRATUM_ROLE",
    "OPERATING_SYSTEM_ROLE",
    "DERIVES_FROM",
    "SPECIALIZES",
    "COMPOSES",
    "REQUIRES",
    "DIMENSION_FACETS",
    "CIVILIZATION_FACETS",
    "DIMENSION_ATTRIBUTE_KEYS",
    "FORBIDDEN_DIMENSION_KEYS",
    "facet_keys",
    "dimension_facet_keys",
]
