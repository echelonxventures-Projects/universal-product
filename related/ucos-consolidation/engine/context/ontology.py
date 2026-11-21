"""UCXI-000001 Part 03 — Context Ontology: what a context *is*, structurally.

Where the Taxonomy (Part 02) classifies, the Ontology specifies. It declares, as
DATA:

    * the **entity types** of the context universe (context, dimension, value,
      frame, observer, taxon) — the only things that may appear as a node;
    * the **dimensions** each context kind is made of, each with a value type and a
      required/optional flag, so "a temporal context" has a checkable shape rather
      than a vibe;
    * the **relation rules** — which relation types may connect which kinds, which
      must stay acyclic, and which are symmetric — so an illegal edge is refused at
      construction rather than discovered later in the graph.

Every universal kind declares three required dimensions (its irreducible shape) and
one optional ``note`` dimension carrying human rationale. Unknown dimensions are
refused: a context may not smuggle in an undeclared field, because an undeclared
field is an unbounded assumption (the same discipline the programme gates apply to
their declarations).

The ontology is **open** in exactly the way the taxonomy is: :meth:`extend` admits a
future kind's dimensions and returns a new immutable ontology. No control flow here
branches on a specific kind.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import Any

from engine.context.errors import OntologyError
from engine.context.taxonomy import ContextKind, ContextRelation

#: The entity types of the context universe. Nothing else may be a graph node.
ENTITY_TYPES: tuple[str, ...] = (
    "Context",
    "ContextDimension",
    "ContextValue",
    "ContextFrame",
    "Observer",
    "ContextTaxon",
)

#: The value types a dimension may carry. JSON-representable by construction, so a
#: context is always canonically serialisable (and therefore sealable).
VALUE_TYPES: tuple[str, ...] = ("string", "number", "boolean", "list", "mapping")

#: The sentinel a dimension carries when its value is genuinely unknown. A universal
#: kind is never *absent*; an unknown dimension is stated, not omitted (CXL-01).
UNKNOWN = "unknown"

_PY_TYPES: dict[str, tuple[type, ...]] = {
    "string": (str,),
    "number": (int, float),
    "boolean": (bool,),
    "list": (list, tuple),
    "mapping": (dict,),
}


@dataclass(frozen=True, slots=True)
class DimensionSpec:
    """The declared shape of one dimension of one context kind."""

    name: str
    value_type: str
    required: bool
    description: str = ""

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name.strip():
            raise OntologyError("dimension name must be a non-empty string", name=self.name)
        if self.value_type not in VALUE_TYPES:
            raise OntologyError(
                "unknown dimension value type",
                name=self.name,
                value_type=self.value_type,
                allowed=list(VALUE_TYPES),
            )

    def accepts(self, value: Any) -> bool:
        """True iff ``value`` matches the declared type (or is the unknown sentinel)."""
        if value == UNKNOWN:
            return True
        expected = _PY_TYPES[self.value_type]
        if self.value_type == "number" and isinstance(value, bool):
            return False  # a bool is not a number here — types are checked, not coerced
        return isinstance(value, expected)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "value_type": self.value_type,
            "required": self.required,
            "description": self.description,
        }


@dataclass(frozen=True, slots=True)
class RelationRule:
    """Which kinds a relation may connect, and the shape it must preserve.

    Empty ``sources``/``targets`` means *any classified kind*. ``acyclic`` marks a
    relation that must remain a hierarchy; ``symmetric`` marks one that reads the
    same in both directions.
    """

    relation: ContextRelation
    sources: tuple[str, ...] = ()
    targets: tuple[str, ...] = ()
    acyclic: bool = False
    symmetric: bool = False
    description: str = ""

    def permits(self, source_kind: str, target_kind: str) -> bool:
        """True iff an edge from ``source_kind`` to ``target_kind`` is admissible."""
        if self.sources and source_kind not in self.sources:
            return False
        return not (self.targets and target_kind not in self.targets)

    def to_dict(self) -> dict[str, Any]:
        return {
            "relation": self.relation.value,
            "sources": list(self.sources),
            "targets": list(self.targets),
            "acyclic": self.acyclic,
            "symmetric": self.symmetric,
            "description": self.description,
        }


def _dim(name: str, value_type: str, description: str, *, required: bool = True) -> DimensionSpec:
    return DimensionSpec(
        name=name, value_type=value_type, required=required, description=description
    )


#: The optional rationale dimension every kind carries.
_NOTE = _dim("note", "string", "Human rationale for this context assertion.", required=False)


#: The irreducible shape of each universal kind (DATA — Part 03 §2).
UNIVERSAL_DIMENSIONS: dict[str, tuple[DimensionSpec, ...]] = {
    ContextKind.EXISTENCE.value: (
        _dim("existence_mode", "string", "actual · potential · former · negated"),
        _dim("substrate", "string", "That in which the subject exists."),
        _dim("boundary", "string", "What separates the subject from what it is not."),
        _NOTE,
    ),
    ContextKind.REALITY.value: (
        _dim("reality_mode", "string", "actual · modelled · simulated · planned · hypothetical"),
        _dim("fidelity", "string", "How faithfully the representation tracks the actual."),
        _dim("verifiability", "string", "How an observer could check the claim."),
        _NOTE,
    ),
    ContextKind.OBSERVER.value: (
        _dim("observer_id", "string", "Who or what observes."),
        _dim("vantage", "string", "The position from which observation happens."),
        _dim("epistemic_access", "string", "What this observer can and cannot know."),
        _NOTE,
    ),
    ContextKind.TEMPORAL.value: (
        _dim("reference_frame", "string", "The clock or epoch the assertion is relative to."),
        _dim("ordering", "string", "How events are ordered (causal · sequence · none)."),
        _dim("resolution", "string", "The granularity at which time is distinguished."),
        _NOTE,
    ),
    ContextKind.SPATIAL.value: (
        _dim("reference_frame", "string", "The coordinate or topological frame."),
        _dim("extent", "string", "The region the subject occupies."),
        _dim("locality", "string", "Where the subject is with respect to the observer."),
        _NOTE,
    ),
    ContextKind.IDENTITY.value: (
        _dim("subject", "string", "The thing identified."),
        _dim("identifier", "string", "The identifier borne under the naming authority."),
        _dim("authority", "string", "The authority that assigns the identifier."),
        _NOTE,
    ),
    ContextKind.GOVERNANCE.value: (
        _dim("authority", "string", "The instrument that governs."),
        _dim("policy", "string", "The governing rule in force."),
        _dim("decision_rights", "string", "Who may decide what, and within what bounds."),
        _NOTE,
    ),
    ContextKind.SECURITY.value: (
        _dim("classification", "string", "Sensitivity classification of the subject."),
        _dim("trust_boundary", "string", "The boundary across which trust is not assumed."),
        _dim("controls", "list", "The controls in force at this boundary."),
        _NOTE,
    ),
    ContextKind.KNOWLEDGE.value: (
        _dim("source", "string", "Where the knowledge comes from."),
        _dim("provenance", "string", "The derivation chain of the knowledge."),
        _dim("confidence", "string", "How strongly the knowledge is held, and why."),
        _NOTE,
    ),
    ContextKind.COMPUTATIONAL.value: (
        _dim("substrate", "string", "The execution substrate."),
        _dim("execution_model", "string", "How computation proceeds on that substrate."),
        _dim("resources", "mapping", "The resource envelope available."),
        _NOTE,
    ),
    ContextKind.ENVIRONMENTAL.value: (
        _dim("medium", "string", "The surrounding medium."),
        _dim("conditions", "mapping", "The prevailing conditions."),
        _dim("constraints", "list", "Physical constraints the environment imposes."),
        _NOTE,
    ),
    ContextKind.ECONOMIC.value: (
        _dim("cost_model", "string", "How cost accrues."),
        _dim("value_basis", "string", "What makes the subject valuable, and to whom."),
        _dim("scarcity", "string", "What is scarce, and how that binds choice."),
        _NOTE,
    ),
    ContextKind.REGULATORY.value: (
        _dim("jurisdiction", "string", "The jurisdiction whose rules apply."),
        _dim("obligations", "list", "The obligations imposed."),
        _dim("compliance_state", "string", "The current compliance position."),
        _NOTE,
    ),
    ContextKind.LINGUISTIC.value: (
        _dim("language", "string", "The language in force."),
        _dim("register", "string", "The register or genre of expression."),
        _dim("encoding", "string", "The encoding carrying the expression."),
        _NOTE,
    ),
    ContextKind.CULTURAL.value: (
        _dim("locale", "string", "The cultural locale."),
        _dim("norms", "list", "The norms shaping interpretation."),
        _dim("conventions", "list", "The conventions in force."),
        _NOTE,
    ),
    ContextKind.MEASUREMENT.value: (
        _dim("measurement_system", "string", "The system of measurement in force."),
        _dim("units", "mapping", "Quantity kind -> the unit identity in force for it."),
        _dim("scale", "string", "The scale frame through which a measurement resolves."),
        _NOTE,
    ),
}


def _relation_rules() -> tuple[RelationRule, ...]:
    """The relation rules of the context universe (DATA — Part 03 §3)."""
    constraining = (
        ContextKind.GOVERNANCE.value,
        ContextKind.SECURITY.value,
        ContextKind.REGULATORY.value,
    )
    return (
        RelationRule(
            relation=ContextRelation.CONTAINS,
            acyclic=True,
            description="A broader context contains a narrower one of any kind.",
        ),
        RelationRule(
            relation=ContextRelation.REFINES,
            acyclic=True,
            description="A context refines another of the same kind, narrowing it.",
        ),
        RelationRule(
            relation=ContextRelation.DERIVES_FROM,
            acyclic=True,
            description="A context is derived from another, inheriting its provenance.",
        ),
        RelationRule(
            relation=ContextRelation.DEPENDS_ON,
            acyclic=True,
            description="A context cannot be resolved without another being resolved.",
        ),
        RelationRule(
            relation=ContextRelation.CONSTRAINS,
            sources=constraining,
            description="Governance, security and regulatory context constrain others.",
        ),
        RelationRule(
            relation=ContextRelation.OBSERVES,
            sources=(ContextKind.OBSERVER.value,),
            description="Only an observer context observes; observation confers no authority.",
        ),
        RelationRule(
            relation=ContextRelation.FEDERATES,
            description="An explicit, authorised reference across a context boundary.",
        ),
        RelationRule(
            relation=ContextRelation.SUPERSEDES,
            acyclic=True,
            description="A context replaces an earlier one of the same kind.",
        ),
        RelationRule(
            relation=ContextRelation.CLASSIFIED_AS,
            acyclic=True,
            description="A context is classified by exactly one taxon.",
        ),
        RelationRule(
            relation=ContextRelation.EQUIVALENT_TO,
            symmetric=True,
            description="Two contexts assert the same thing under different names.",
        ),
        RelationRule(
            relation=ContextRelation.CONFLICTS_WITH,
            symmetric=True,
            description="Two contexts cannot both hold; composition must refuse or resolve.",
        ),
    )


RELATION_RULES: tuple[RelationRule, ...] = _relation_rules()


class ContextOntology:
    """The immutable structural specification of every context kind.

    Construct with the universal dimensions (the default) and extend for future
    kinds. Validation is pure: it reports findings rather than raising, so a caller
    can collect every problem in one pass, with :meth:`require_valid` provided for
    the fail-closed path.
    """

    __slots__ = ("_dimensions", "_rules")

    def __init__(
        self,
        dimensions: Mapping[str, tuple[DimensionSpec, ...]] | None = None,
        rules: tuple[RelationRule, ...] = RELATION_RULES,
    ) -> None:
        source = UNIVERSAL_DIMENSIONS if dimensions is None else dimensions
        normalised: dict[str, tuple[DimensionSpec, ...]] = {}
        for kind, specs in source.items():
            if not specs:
                raise OntologyError("a context kind must declare at least one dimension", kind=kind)
            seen: set[str] = set()
            for spec in specs:
                if spec.name in seen:
                    raise OntologyError(
                        "duplicate dimension in a context kind", kind=kind, dimension=spec.name
                    )
                seen.add(spec.name)
            if not any(spec.required for spec in specs):
                raise OntologyError(
                    "a context kind must declare at least one required dimension", kind=kind
                )
            normalised[kind] = tuple(sorted(specs, key=lambda s: s.name))
        by_relation: dict[ContextRelation, RelationRule] = {}
        for rule in rules:
            if rule.relation in by_relation:
                raise OntologyError("duplicate relation rule", relation=rule.relation.value)
            by_relation[rule.relation] = rule
        missing = [r.value for r in ContextRelation if r not in by_relation]
        if missing:
            raise OntologyError("relation without a rule (unbounded edge)", relations=missing)
        self._dimensions = dict(sorted(normalised.items()))
        self._rules = by_relation

    # -- extension ---------------------------------------------------------- #

    def extend(self, kind: str, dimensions: Iterable[DimensionSpec]) -> ContextOntology:
        """Declare the shape of a **future context kind** and return a new ontology.

        Raises:
            OntologyError: the kind is already specified, or the shape is unusable.
        """
        kind_value = kind.value if isinstance(kind, ContextKind) else str(kind)
        if kind_value in self._dimensions:
            raise OntologyError("context kind is already specified", kind=kind_value)
        specs = tuple(dimensions)
        if not specs:
            raise OntologyError(
                "a future context kind must declare its dimensions", kind=kind_value
            )
        merged = dict(self._dimensions)
        merged[kind_value] = specs
        return ContextOntology(merged, tuple(self._rules.values()))

    # -- lookups ------------------------------------------------------------ #

    def kinds(self) -> tuple[str, ...]:
        """Every kind with a declared shape, ordered."""
        return tuple(self._dimensions)

    def specifies(self, kind: str) -> bool:
        kind_value = kind.value if isinstance(kind, ContextKind) else str(kind)
        return kind_value in self._dimensions

    def dimensions_for(self, kind: str) -> tuple[DimensionSpec, ...]:
        """The declared dimensions of ``kind`` or raise :class:`OntologyError`."""
        kind_value = kind.value if isinstance(kind, ContextKind) else str(kind)
        try:
            return self._dimensions[kind_value]
        except KeyError as exc:
            raise OntologyError("context kind has no declared shape", kind=kind_value) from exc

    def required_for(self, kind: str) -> tuple[str, ...]:
        """The names of the required dimensions of ``kind``, ordered."""
        return tuple(spec.name for spec in self.dimensions_for(kind) if spec.required)

    def spec_for(self, kind: str, dimension: str) -> DimensionSpec | None:
        """The spec of one dimension of one kind, or ``None`` if undeclared."""
        for spec in self.dimensions_for(kind):
            if spec.name == dimension:
                return spec
        return None

    def rule_for(self, relation: ContextRelation) -> RelationRule:
        """The rule governing ``relation``."""
        return self._rules[ContextRelation.coerce(relation)]

    def rules(self) -> tuple[RelationRule, ...]:
        """Every relation rule, ordered by relation value."""
        return tuple(sorted(self._rules.values(), key=lambda r: r.relation.value))

    # -- validation --------------------------------------------------------- #

    def check_values(self, kind: str, values: Mapping[str, Any], *, at: str = "") -> list[str]:
        """Return findings for a kind's value mapping (empty means conformant).

        Checks completeness (every required dimension present), closure (no
        undeclared dimension), and type conformance (declared value type honoured,
        with the explicit ``unknown`` sentinel always admissible).
        """
        subject = at or kind
        findings: list[str] = []
        if not self.specifies(kind):
            return [f"{subject}: kind {kind!r} has no declared ontological shape"]
        specs = {spec.name: spec for spec in self.dimensions_for(kind)}
        for name in self.required_for(kind):
            if name not in values:
                findings.append(f"{subject}: required dimension {name!r} is absent")
        for name, value in sorted(values.items()):
            spec = specs.get(name)
            if spec is None:
                findings.append(f"{subject}: dimension {name!r} is not declared for kind {kind!r}")
                continue
            if not spec.accepts(value):
                findings.append(
                    f"{subject}: dimension {name!r} expects {spec.value_type}, "
                    f"got {type(value).__name__}"
                )
        return findings

    def require_values(self, kind: str, values: Mapping[str, Any], *, at: str = "") -> None:
        """Fail-closed form of :meth:`check_values`."""
        findings = self.check_values(kind, values, at=at)
        if findings:
            raise OntologyError(
                "context does not conform to its ontological shape",
                kind=kind,
                at=at or kind,
                findings=findings,
            )

    def check_relation(
        self, relation: ContextRelation, source_kind: str, target_kind: str
    ) -> list[str]:
        """Return findings for one relation edge (empty means admissible)."""
        rule = self.rule_for(relation)
        if rule.permits(source_kind, target_kind):
            return []
        return [
            f"relation {rule.relation.value!r} is not admissible from {source_kind!r} "
            f"to {target_kind!r}"
        ]

    def require_relation(
        self, relation: ContextRelation, source_kind: str, target_kind: str
    ) -> None:
        """Fail-closed form of :meth:`check_relation`."""
        findings = self.check_relation(relation, source_kind, target_kind)
        if findings:
            raise OntologyError(
                "inadmissible context relation",
                relation=ContextRelation.coerce(relation).value,
                source_kind=source_kind,
                target_kind=target_kind,
                findings=findings,
            )

    # -- serialisation ------------------------------------------------------ #

    def to_dict(self) -> dict[str, Any]:
        return {
            "entity_types": list(ENTITY_TYPES),
            "value_types": list(VALUE_TYPES),
            "unknown_sentinel": UNKNOWN,
            "dimensions": {
                kind: [spec.to_dict() for spec in specs] for kind, specs in self._dimensions.items()
            },
            "relations": [rule.to_dict() for rule in self.rules()],
        }


#: The default ontology: the declared shape of the sixteen universal kinds.
UNIVERSAL_ONTOLOGY = ContextOntology()


__all__ = [
    "ENTITY_TYPES",
    "VALUE_TYPES",
    "UNKNOWN",
    "DimensionSpec",
    "RelationRule",
    "RELATION_RULES",
    "UNIVERSAL_DIMENSIONS",
    "ContextOntology",
    "UNIVERSAL_ONTOLOGY",
]
