"""UCOS-CEU-001 Part 04 — the seed catalogue. DATA, and the proof that DATA is enough.

Every concept the steering names — Observer, Perspective, Uncertainty, Possibility,
Pattern, Generation, Recursion, Scale, Temporal model, Unknown, Dependency, Constraint,
Resource, Intent, Purpose, Value, Boundary, Sovereignty, Authority, Contradiction — is
declared here as **data**, and enters the substrate through the ordinary registration
path. Not one of them is a class, a branch, an enum member or a special case.

That is the whole argument of CEU-038 made checkable: if these thirty-odd concepts can be
admitted without a line of new code, then the substrate is *sufficient*, and the next
concept — the one nobody has named — will be admitted the same way. If any of them had
needed code, the substrate would be insufficient and the right response would be to fix
the substrate rather than to special-case the concept.

Every form declares the primitives that express it (:mod:`engine.ceu.sufficiency`), so
"could this have been data?" is answered per row, by measurement, rather than by opinion.

Nothing here is privileged. This file is one catalogue; a deployment may register a
different one, register none, or supersede every row in it. The seeds are examples that
happen to be useful, not a fixed vocabulary.
"""

from __future__ import annotations

from typing import Any

from engine.ceu.existence import (
    ATTR_ACYCLIC,
    ATTR_FACULTIES,
    ATTR_SPECIALIZES,
    ATTR_SYMMETRIC,
    ATTR_TOPOLOGIES,
    ExistenceRegistry,
    ExistenceUnit,
    RelationshipView,
)
from engine.ceu.sufficiency import ATTR_EXPRESSED_BY

#: The attributes a unit declares its measurement system and its quantity in (ADR-0005).
ATTR_SYSTEM = "system"
ATTR_QUANTITY = "quantity"

#: The forms of existence, as ``(key, code, title, expressing primitives)``.
#: A code is ignored when the one identity authority already knows the name — reuse, not
#: a second grammar. Ordered so a reader can see the constitutional shape at a glance.
SEED_FORMS: tuple[tuple[str, str, str, tuple[str, ...]], ...] = (
    # -- the four the blocking constraint named -------------------------------
    ("entity", "ENTY", "Entity", ("existence", "identity")),
    ("classification", "CLSS", "Classification", ("classification", "identity")),
    ("relationship-type", "RLTY", "Relationship Type", ("relationship", "classification")),
    ("relationship", "REL", "Relationship", ("relationship", "identity")),
    ("topology", "TOPO", "Topology", ("topology", "relationship")),
    # -- context, observation, perspective (CEU-006, CEU-007) ------------------
    ("context", "CTX", "Context", ("context",)),
    ("observer", "OBSV", "Observer", ("existence", "context")),
    ("perspective", "PRSP", "Perspective", ("context", "knowledge")),
    # -- knowledge and its certainty (CEU-008) ---------------------------------
    ("knowledge", "KNW", "Knowledge", ("knowledge",)),
    ("knowledge-state", "KNST", "Knowledge State", ("knowledge", "classification")),
    ("epistemic-state", "EPST", "Epistemic State", ("knowledge", "evidence")),
    # -- existence states and possibility (CEU-009, CEU-017) -------------------
    ("existence-state", "EXST", "Existence State", ("existence", "classification")),
    # -- pattern and generation (CEU-010, CEU-011) -----------------------------
    ("pattern", "PTRN", "Pattern", ("knowledge", "classification")),
    ("generator", "GENR", "Generator", ("capability", "evolution")),
    # -- scale and time (CEU-013, CEU-014) -------------------------------------
    ("scale", "SCAL", "Scale", ("context", "classification")),
    ("temporal-model", "TMPM", "Temporal Model", ("context", "classification")),
    # -- capability, governance, evidence --------------------------------------
    ("capability", "CAP", "Capability", ("capability",)),
    ("governance", "GOVN", "Governance", ("governance",)),
    ("policy", "POL", "Policy", ("governance",)),
    ("rule", "RULE", "Rule", ("governance",)),
    ("authority", "AUTH", "Authority", ("governance", "identity")),
    ("evidence", "EV", "Evidence", ("evidence",)),
    ("measurement", "MSMT", "Measurement", ("evidence", "context")),
    # -- what a measurement is expressed in (ADR-0005) -------------------------
    ("measurement-system", "MSYS", "Measurement System", ("context", "classification")),
    ("quantity", "QNTY", "Quantity", ("context", "classification")),
    ("unit", "UNIT", "Unit", ("context", "identity")),
    # -- dependency, constraint, resource (CEU-031, CEU-032) -------------------
    ("dependency", "DEP", "Dependency", ("relationship", "governance")),
    ("constraint", "CNST", "Constraint", ("governance", "relationship")),
    ("resource", "RSRC", "Resource", ("existence", "capability")),
    # -- intent, purpose, value, boundary, sovereignty -------------------------
    ("intent", "INTN", "Intent", ("knowledge", "governance")),
    ("purpose", "PRPS", "Purpose", ("knowledge", "governance")),
    ("value", "VALU", "Value", ("context", "knowledge")),
    ("boundary", "BNDY", "Boundary", ("topology", "context")),
    ("sovereignty", "SVRN", "Sovereignty", ("governance", "topology")),
    # -- contradiction and recovery (CEU-043, CEU-042) -------------------------
    ("contradiction", "CNTR", "Contradiction", ("knowledge", "evidence")),
    ("recovery", "RCVY", "Recovery", ("lineage", "evolution")),
    # -- trust, consent, risk --------------------------------------------------
    ("trust", "TRST", "Trust", ("governance", "evidence")),
    ("consent", "CNSN", "Consent", ("governance", "lineage")),
    ("risk", "RISK", "Risk", ("governance", "knowledge")),
    # -- prediction, simulation (never truth until verified) -------------------
    ("prediction", "PRED", "Prediction", ("knowledge", "evidence")),
    ("simulation", "SIML", "Simulation", ("existence", "context")),
    # -- goal, decision, state, causality --------------------------------------
    ("goal", "GOAL", "Goal", ("governance", "knowledge")),
    ("decision", "DCSN", "Decision", ("governance", "evidence")),
    ("state", "STAT", "State", ("existence", "lineage")),
    ("causality", "CAUS", "Causality", ("relationship", "context")),
    ("observation", "OBSN", "Observation", ("evidence", "context")),
    # -- the registries and the architecture itself (CEU-019) ------------------
    ("registry", "REG", "Registry", ("identity", "lineage")),
    ("dictionary", "DICT", "Dictionary", ("identity", "knowledge")),
    ("event", "EVNT", "Event", ("existence", "lineage")),
    ("architecture", "ARCH", "Architecture", ("existence", "evolution")),
    # -- realities, universes, civilisations (CEU-005, UCEP-005) ---------------
    ("reality", "RLT", "Reality", ("existence", "context")),
    ("universe", "UNV", "Universe", ("existence", "context")),
    ("civilization", "CIV", "Civilization", ("existence", "context")),
)

#: Topologies (CEU-004, S-007). Every one of these is a row, not a graph implementation.
SEED_TOPOLOGIES: tuple[tuple[str, str], ...] = (
    ("hierarchy", "Nested containment, one parent per member."),
    ("layered", "Ordered strata. One arrangement among many, never mandatory (CEU-005)."),
    ("layerless", "The explicit absence of strata, so 'no layers' is declarable."),
    ("network", "Arbitrary connection without containment."),
    ("graph", "Directed connection, cycles permitted unless a type forbids them."),
    ("mesh", "Every member reachable from every other."),
    ("matrix", "Membership along two or more independent axes at once."),
    ("lattice", "Partially ordered membership with meets and joins."),
    ("recursive", "Members that contain arrangements of the same kind (CEU-012)."),
    ("fractal", "Self-similar arrangement across scales (CEU-013)."),
    ("swarm", "Transient membership with no fixed structure."),
    ("federation", "Sovereign members cooperating without a centre (CEU-051)."),
    ("temporal", "Arrangement by time model rather than by structure (CEU-014)."),
    ("spatial", "Arrangement by existence coordinate rather than geography."),
    ("semantic", "Arrangement by meaning, which is observer-relative (CEU-033)."),
    ("knowledge", "Arrangement by what is known about what."),
    ("ownership", "Arrangement by who answers for what."),
)

#: Relationship types (CEU-003, CEU-007). Unconstrained unless a row declares otherwise:
#: the substrate imposes no valid-pair table, so any form may relate to any form.
SEED_RELATIONSHIP_TYPES: tuple[tuple[str, str, dict[str, Any]], ...] = (
    ("composes", "Selects and assembles.", {ATTR_ACYCLIC: True, ATTR_TOPOLOGIES: ("hierarchy",)}),
    (
        "contains",
        "Holds within, to unlimited depth (CEU-012).",
        {ATTR_ACYCLIC: True, ATTR_TOPOLOGIES: ("recursive", "hierarchy")},
    ),
    ("organizes", "Files without owning (CEU-005).", {ATTR_TOPOLOGIES: ("layered",)}),
    (
        "owns",
        "Answers for. Admissibility is the owner's registered faculty, not its form.",
        {ATTR_TOPOLOGIES: ("ownership",)},
    ),
    (
        "depends-on",
        "Requires in order to exist or operate (CEU-031).",
        {ATTR_ACYCLIC: True, ATTR_TOPOLOGIES: ("graph",)},
    ),
    ("constrains", "Bounds what the target may be or do (CEU-032).", {}),
    ("governs", "Holds authority over.", {ATTR_TOPOLOGIES: ("ownership",)}),
    ("evidences", "Supports as evidence (CEU-046).", {ATTR_TOPOLOGIES: ("knowledge",)}),
    (
        "contradicts",
        "Asserts an incompatible truth. Symmetric, and lawful to leave unresolved (CEU-043).",
        {ATTR_SYMMETRIC: True, ATTR_TOPOLOGIES: ("knowledge",)},
    ),
    ("observes", "Takes as object of observation (CEU-006).", {}),
    ("generates", "Brings into existence (CEU-011).", {ATTR_TOPOLOGIES: ("graph",)}),
    (
        "expresses",
        "Carries as meaning, observer-relative (CEU-033).",
        {ATTR_TOPOLOGIES: ("semantic",)},
    ),
    (
        "causes",
        "Brings about, in a stated context. Causality is contextual, so this "
        "type is not globally acyclic.",
        {ATTR_TOPOLOGIES: ("graph",)},
    ),
    ("trusts", "Extends trust to, measurably and revocably.", {}),
    (
        "verifies",
        "Independently confirms. What moves a prediction toward truth.",
        {ATTR_TOPOLOGIES: ("knowledge",)},
    ),
    (
        "converts-to",
        "Expresses the same quantity in another unit. A conversion is a relationship "
        "carrying its own terms, never a table the substrate knows about (ADR-0005).",
        {ATTR_TOPOLOGIES: ("graph",)},
    ),
    ("relates-to", "The unconstrained default: anything to anything (CEU-007).", {}),
)

#: Classifications. Nucleus and Layer appear here as *rows* — the demotion CEU-002 and
#: S-012 require. Nucleus holds the ownership faculty; Layer does not; neither is
#: privileged by anything except what this data says.
SEED_CLASSIFICATIONS: tuple[tuple[str, str, dict[str, Any]], ...] = (
    ("nucleus", "A canonical capability authority.", {ATTR_FACULTIES: ("own-capability",)}),
    ("micro-nucleus", "A nucleus at finer grain.", {ATTR_SPECIALIZES: "nucleus"}),
    ("nano-nucleus", "A micro-nucleus at finer grain still.", {ATTR_SPECIALIZES: "micro-nucleus"}),
    ("layer", "An organising stratum. Owns nothing, and is optional (CEU-005).", {}),
    (
        "composition",
        "A selection of nuclei plus configuration. Owns nothing.",
        {ATTR_FACULTIES: ("select-units",)},
    ),
    ("service", "An operable surface over capabilities.", {ATTR_SPECIALIZES: "nucleus"}),
    ("engine", "A deterministic transformer.", {ATTR_SPECIALIZES: "nucleus"}),
    ("platform", "A configured composition.", {ATTR_SPECIALIZES: "composition"}),
    ("domain", "A bounded area of concern.", {}),
    ("agent", "An autonomous actor.", {ATTR_FACULTIES: ("observe", "act")}),
)

#: Observer kinds (CEU-006). Human is one row among nine, and 'unknown' is one of them,
#: because CEU-017 makes unknown a valid state rather than an absence.
SEED_OBSERVERS: tuple[tuple[str, str], ...] = (
    ("human", "An individual person."),
    ("organization", "A constituted group."),
    ("machine", "A deterministic instrument."),
    ("ai", "A learning system."),
    ("civilization", "A civilisation observing itself."),
    ("reality", "A reality as its own observer."),
    ("universe", "A universe as its own observer."),
    ("collective-intelligence", "An emergent collective."),
    ("unknown", "An observer whose nature is not established (CEU-017)."),
)

#: Existence states (CEU-009) — what it means for something to be.
SEED_EXISTENCE_STATES: tuple[tuple[str, str], ...] = (
    ("actual", "Observed to be the case."),
    ("potential", "Capable of being the case."),
    ("possible", "Not excluded by known constraints."),
    ("predicted", "Expected on the basis of a model."),
    ("simulated", "The case within a simulation."),
    ("alternative", "The case in a different branch."),
    ("counterfactual", "Would have been the case under other conditions."),
    ("historical-reconstruction", "Inferred to have been the case."),
    ("hypothetical", "Entertained without commitment."),
    ("unknown", "Existence state not established. Valid, and not an absence (CEU-017)."),
)

#: Knowledge certainty states (CEU-008).
SEED_KNOWLEDGE_STATES: tuple[tuple[str, str], ...] = (
    ("certainty", "Held without reservation."),
    ("uncertainty", "Held with acknowledged doubt."),
    ("confidence", "Held with a stated degree."),
    ("probability", "Held with a quantified likelihood."),
    ("assumption", "Taken as given, pending evidence."),
    ("belief", "Held without decisive evidence."),
    ("hypothesis", "Proposed for testing (CEU-046: truth without evidence stays here)."),
    ("estimation", "Derived approximately."),
    ("prediction", "Asserted about what is not yet observed."),
)

#: Epistemic states (CEU-045). These are *six distinct states*, never collapsed to one
#: falsy value — which is the entire point of the principle.
SEED_EPISTEMIC_STATES: tuple[tuple[str, str], ...] = (
    ("unknown", "Nothing is established. Not absence, not failure (CEU-017)."),
    ("unobserved", "No observation has been attempted."),
    ("unmeasured", "Observed, but no measurement taken."),
    ("unverified", "Measured, but not independently confirmed."),
    ("contradicted", "Confirmed claims conflict, and the conflict stands (CEU-043)."),
    ("impossible", "Excluded by a stated constraint."),
)

#: Scales (CEU-013) and temporal models (CEU-014). Neither is a unit system; both are
#: registered frames a measurement resolves through.
SEED_SCALES: tuple[tuple[str, str], ...] = (
    ("quantum", "At the scale of quanta."),
    ("atomic", "At the scale of atoms."),
    ("human", "At the scale of a person. One row, not the default."),
    ("planetary", "At the scale of a world."),
    ("galactic", "At the scale of a galaxy."),
    ("universal", "At the scale of a universe."),
    ("multi-universal", "Across universes."),
    ("unknown", "Scale not established (CEU-017)."),
)

SEED_TEMPORAL_MODELS: tuple[tuple[str, str], ...] = (
    ("historical", "Ordered by what has been recorded."),
    ("predicted", "Ordered by what a model expects."),
    ("alternative", "Ordered within a different branch."),
    ("simulated", "Ordered within a simulation."),
    ("branching", "Ordered along diverging futures."),
    ("recursive", "Ordered with self-reference."),
    ("unknown", "Temporal model not established (CEU-017)."),
)

#: Consent states, which possess lineage: each is a state a consent may be *in*, and the
#: move between them is a registered event rather than a field being overwritten.
SEED_CONSENT_STATES: tuple[tuple[str, str], ...] = (
    ("granted", "Given, and currently in force."),
    ("denied", "Withheld."),
    ("delegated", "Given, and exercisable by another."),
    ("revoked", "Given, then withdrawn. The grant stays in lineage."),
    ("expired", "Given, then lapsed by its own terms."),
)

#: Risk states (identified → measured → governed → mitigated | accepted | transferred).
SEED_RISK_STATES: tuple[tuple[str, str], ...] = (
    ("identified", "Named, not yet quantified."),
    ("measured", "Quantified against a stated model."),
    ("governed", "Under a declared authority."),
    ("mitigated", "Reduced by a recorded action."),
    ("accepted", "Retained by a named authority."),
    ("transferred", "Assumed by another party."),
)

#: Quantities (ADR-0005) — *what* is measured, before any unit or system is chosen.
#: Separating the quantity from the unit is what lets two systems disagree about units
#: while agreeing about what they are measuring.
SEED_QUANTITIES: tuple[tuple[str, str], ...] = (
    ("length", "Extent along one spatial dimension."),
    ("mass", "Quantity of matter."),
    ("duration", "Extent along a temporal dimension, in whatever temporal model (CEU-014)."),
    ("speed", "Length per duration."),
    ("temperature", "Thermal state."),
    ("energy", "Capacity to do work."),
    ("information", "Quantity of distinguishable state."),
    ("complexity", "Cost of description, or of computation."),
    ("uncertainty", "The spread of what is not established (CEU-017)."),
    ("value", "What something is worth, in a stated economic context."),
    ("count", "Cardinality. Dimensionless."),
    ("proportion", "A measured part of a measured whole. Dimensionless."),
    ("unknown", "The quantity measured is not established. Valid, not an absence (CEU-017)."),
)

#: Measurement systems (ADR-0005). Every row is a peer. SI is one of them and is not the
#: default; ``non-human`` is declarable before anyone has met one; ``unknown`` is a state,
#: not an absence. A system nobody has proposed is admitted by appending a row.
SEED_MEASUREMENT_SYSTEMS: tuple[tuple[str, str], ...] = (
    ("si", "The International System of Units. One system among many, never the default."),
    ("imperial", "The imperial system."),
    ("natural", "Units fixed by physical constants rather than by artefact or convention."),
    ("planck", "Units derived from the Planck constants."),
    ("binary-information", "Units of distinguishable state, base two."),
    ("dimensionless", "Pure numbers — counts, ratios and digests carry no unit."),
    ("repository", "This platform's own system: commits, files and digests."),
    ("non-human", "A system originating outside human civilisation (CEU-005, UCKP-ART-20)."),
    ("unknown", "The system in force is not established (CEU-017)."),
)

#: Units as ``(key, title, system, quantity)`` (ADR-0005). A unit is an entity that names
#: the system it belongs to and the quantity it measures — both by registered key, so a
#: unit of a system this file has never heard of registers exactly the same way.
SEED_UNITS: tuple[tuple[str, str, str, str], ...] = (
    ("metre", "Metre", "si", "length"),
    ("kilogram", "Kilogram", "si", "mass"),
    ("second", "Second", "si", "duration"),
    ("kelvin", "Kelvin", "si", "temperature"),
    ("joule", "Joule", "si", "energy"),
    ("foot", "Foot", "imperial", "length"),
    ("pound", "Pound", "imperial", "mass"),
    ("degree-fahrenheit", "Degree Fahrenheit", "imperial", "temperature"),
    ("planck-length", "Planck Length", "planck", "length"),
    ("planck-time", "Planck Time", "planck", "duration"),
    ("bit", "Bit", "binary-information", "information"),
    ("byte", "Byte", "binary-information", "information"),
    ("cardinal", "Cardinal", "dimensionless", "count"),
    ("ratio", "Ratio", "dimensionless", "proportion"),
    ("commit-ordinal", "Commit Ordinal", "repository", "duration"),
)

#: Conversions as ``(source unit, target unit, terms)`` (ADR-0005). Each becomes a
#: *relationship instance*, not a lookup table: the terms live on the relationship, so a
#: conversion that needs an offset, a context or a provenance carries it without any
#: schema here changing. Terms are strings so the registered content is exact and the
#: substrate never has to interpret a float it did not compute.
SEED_CONVERSIONS: tuple[tuple[str, str, dict[str, Any]], ...] = (
    ("foot", "metre", {"factor": "0.3048"}),
    ("pound", "kilogram", {"factor": "0.45359237"}),
    ("byte", "bit", {"factor": "8"}),
    (
        "degree-fahrenheit",
        "kelvin",
        {"factor": "5/9", "offset": "459.67", "form": "(F + offset) * factor"},
    ),
)

#: ``form key -> the rows registered under it``. Data, so adding a population is a tuple.
SEED_POPULATIONS: tuple[tuple[str, tuple[tuple[str, str], ...]], ...] = (
    ("observer", SEED_OBSERVERS),
    ("consent", SEED_CONSENT_STATES),
    ("risk", SEED_RISK_STATES),
    ("existence-state", SEED_EXISTENCE_STATES),
    ("knowledge-state", SEED_KNOWLEDGE_STATES),
    ("epistemic-state", SEED_EPISTEMIC_STATES),
    ("scale", SEED_SCALES),
    ("temporal-model", SEED_TEMPORAL_MODELS),
    ("quantity", SEED_QUANTITIES),
    ("measurement-system", SEED_MEASUREMENT_SYSTEMS),
)


def bootstrap(registry: ExistenceRegistry | None = None) -> ExistenceRegistry:
    """Register the whole seed catalogue through the ordinary registration path.

    Every row goes through :meth:`ExistenceRegistry.register` — the same call an unknown
    future concept uses. There is no seeding shortcut, which is what makes a green run of
    this function evidence that the path works rather than evidence that the seeds were
    special-cased in.
    """
    target = registry if registry is not None else ExistenceRegistry()

    for key, code, title, expressed_by in SEED_FORMS:
        target.declare_form(
            key,
            title=title,
            code=code,
            attributes={ATTR_EXPRESSED_BY: expressed_by},
        )

    for key, definition in SEED_TOPOLOGIES:
        target.register(
            ExistenceUnit(form="topology", key=key, title=key.title(), definition=definition)
        )

    for key, definition, attributes in SEED_RELATIONSHIP_TYPES:
        target.register(
            ExistenceUnit(
                form="relationship-type",
                key=key,
                title=key.replace("-", " ").title(),
                definition=definition,
                attributes=attributes,
            )
        )

    # Classifications may specialize one another, so a parent's identifier has to be
    # resolved after it is registered — hence the two-pass shape rather than one.
    minted: dict[str, str] = {}
    for key, definition, attributes in SEED_CLASSIFICATIONS:
        resolved = dict(attributes)
        parent = resolved.get(ATTR_SPECIALIZES)
        if parent is not None:
            resolved[ATTR_SPECIALIZES] = minted[str(parent)]
        unit = target.register(
            ExistenceUnit(
                form="classification",
                key=key,
                title=key.replace("-", " ").title(),
                definition=definition,
                attributes=resolved,
            )
        )
        minted[key] = unit.universal_id

    for form, population in SEED_POPULATIONS:
        for key, definition in population:
            target.register(
                ExistenceUnit(
                    form=form,
                    key=key,
                    title=key.replace("-", " ").title(),
                    definition=definition,
                )
            )

    # Units name the system they belong to and the quantity they measure, both by
    # registered key. Registered after the populations above so both endpoints exist.
    for key, title, system, quantity in SEED_UNITS:
        target.register(
            ExistenceUnit(
                form="unit",
                key=key,
                title=title,
                definition=f"A unit of {quantity} in the {system} system.",
                attributes={ATTR_SYSTEM: system, ATTR_QUANTITY: quantity},
            )
        )

    return target


def declare_forms_reversed(registry: ExistenceRegistry | None = None) -> ExistenceRegistry:
    """Declare every seed form last row first — the same state, a different arrival order.

    :func:`bootstrap` fixes one arrival order for the catalogue, and an instrument that
    only ever sees that order cannot tell a declared state apart from the sequence that
    produced it. This reaches the identical kind space through the identical
    ``declare_form`` path with the rows reversed, so any difference an observer measures
    between the two is arrival order and nothing else. It is the alternative admissible
    sequence BC-2's cross-process comparator runs as its third scenario.
    """
    target = registry if registry is not None else ExistenceRegistry()
    for key, code, title, expressed_by in reversed(SEED_FORMS):
        target.declare_form(
            key,
            title=title,
            code=code,
            attributes={ATTR_EXPRESSED_BY: expressed_by},
        )
    return target


def register_conversions(
    registry: ExistenceRegistry, conversions: tuple[tuple[str, str, dict[str, Any]], ...] = ()
) -> tuple[ExistenceUnit, ...]:
    """Assert unit conversions as relationship *instances* over a seeded registry.

    Separate from :func:`bootstrap` on purpose. The seed catalogue is vocabulary — forms,
    types and populations — and asserting an instance is a different act with a different
    authority, so a deployment that wants SI-to-imperial conversions asks for them rather
    than inheriting them.

    Each conversion becomes an ordinary unit of the relationship form (ADR-0005): it is
    identified, journaled, supersedable and evolvable like every other unit, and its terms
    live on the relationship. Nothing here converts anything — the substrate records the
    terms, and a caller that needs the arithmetic does the arithmetic. A conversion needing
    an offset, a context or a provenance carries it without a schema change, which is why
    conversions are relationships and not a table.

    ``conversions`` defaults to :data:`SEED_CONVERSIONS`; pass another tuple to register a
    different set, including between units of a system this file has never named.
    """
    view = relationship_view(registry)
    units = {unit.key: unit.universal_id for unit in registry.units(form="unit")}
    registered: list[ExistenceUnit] = []
    for source, destination, terms in conversions or SEED_CONVERSIONS:
        registered.append(
            view.relate(
                "converts-to",
                units[source],
                units[destination],
                authority="engine/ceu/catalog.py SEED_CONVERSIONS",
                attributes=terms,
                note=f"{source} expressed in {destination}.",
            )
        )
    return tuple(registered)


def relationship_view(registry: ExistenceRegistry) -> RelationshipView:
    """The relationship surface over a catalogue-seeded registry."""
    return RelationshipView(
        registry,
        type_form="relationship-type",
        relationship_form="relationship",
        topology_form="topology",
    )


def to_document(registry: ExistenceRegistry | None = None) -> dict[str, Any]:
    """The seeded substrate as one deterministic document."""
    target = registry if registry is not None else bootstrap()
    return {
        "schema": "ucos-ceu-catalog",
        "version": "1.0.0",
        "counts": target.counts(),
        "forms": [u.key for u in target.forms()],
        "registry": target.to_document(),
        "closed_set": False,
        "upper_limit": None,
    }


__all__ = [
    "SEED_FORMS",
    "declare_forms_reversed",
    "SEED_TOPOLOGIES",
    "SEED_RELATIONSHIP_TYPES",
    "SEED_CLASSIFICATIONS",
    "SEED_OBSERVERS",
    "SEED_EXISTENCE_STATES",
    "SEED_KNOWLEDGE_STATES",
    "SEED_EPISTEMIC_STATES",
    "SEED_SCALES",
    "SEED_TEMPORAL_MODELS",
    "SEED_QUANTITIES",
    "SEED_MEASUREMENT_SYSTEMS",
    "SEED_UNITS",
    "SEED_CONVERSIONS",
    "register_conversions",
    "ATTR_SYSTEM",
    "ATTR_QUANTITY",
    "SEED_CONSENT_STATES",
    "SEED_RISK_STATES",
    "SEED_POPULATIONS",
    "bootstrap",
    "relationship_view",
    "to_document",
]
