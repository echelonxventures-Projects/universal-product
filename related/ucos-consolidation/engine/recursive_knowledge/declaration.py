"""URKE-000001 Part 02 — the declaration, read into values. The only module allowed to name keys.

Every vocabulary this capability governs is data, and this module turns that data into frozen values
and refuses it when incoherent. It is the single module the source-discipline law exempts from the
no-vocabulary-literal rule, because a parser that could not name the keys of the document it parses
could not be written, and a key name is the shape of a document rather than a member of a
vocabulary. No vocabulary *member* is exempt anywhere, including here.

:meth:`Declaration.validate` binds declared names to implemented symbols **in both directions** for
every declared binding kind: a law naming a check nothing implements is manual governance wearing a
law's clothes, and a check nothing claims is dead code wearing enforcement's. It also refuses a
terminal state, an unreachable state, a required attribute nothing can read, a discovery target no
source claims, an evolution subject with no operator, a reality omitting a declared dimension, a
profile requiring an unreadable attribute, a non-empty review exemption list, and a primitive count
above the declared bound.

Keys prefixed with ``$`` are prose for a reader and are skipped by every parse below. They exist so
the rationale for a row sits next to the row rather than in a document that drifts from it.
"""

from __future__ import annotations

import json
import os
from collections.abc import Mapping
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any

from engine.recursive_knowledge.model import RecursiveKnowledgeError
from engine.uckp.payload import canonical_payload

#: Parsed fields deliberately outside the certification identity, each with the reason it
#: cannot reach a verdict. Inclusion is the default: a field absent from the identity and
#: absent from here is a defect, and the suite fails in BOTH directions — on an undeclared
#: omission and on an exclusion naming a field this declaration no longer has.
DIGEST_EXCLUSIONS: Mapping[str, str] = {
    "source": (
        "the path the declaration was read from. A digest that changed with the reader would "
        "not be a digest of the declaration."
    ),
}

#: Where the declaration lives, relative to the repository root.
DECLARATION_PATH = os.path.join("00-MASTER", "URKE-000001", "urke-declaration.json")


class DeclarationError(RecursiveKnowledgeError):
    """The declaration is absent, unreadable, malformed or incoherent. Always a fault."""


def repo_root() -> str:
    """The repository root, derived from this file rather than the working directory."""
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _node(document: Mapping[str, Any], *path: str) -> Any:
    node: Any = document
    for step in path:
        if not isinstance(node, Mapping) or step not in node:
            raise DeclarationError(f"the declaration has no {'.'.join(path)!r}")
        node = node[step]
    return node


def _rows(document: Mapping[str, Any], *path: str) -> list[Mapping[str, Any]]:
    node = _node(document, *path)
    if not isinstance(node, list):
        raise DeclarationError(f"{'.'.join(path)!r} must be a list")
    return [row for row in node if isinstance(row, Mapping)]


def _text(row: Mapping[str, Any], key: str, *, where: str, required: bool = True) -> str:
    value = row.get(key)
    if value is None or (isinstance(value, str) and not value):
        if required:
            raise DeclarationError(f"{where} declares no {key!r}")
        return ""
    return str(value)


def _strings(row: Mapping[str, Any], key: str) -> tuple[str, ...]:
    value = row.get(key) or ()
    if isinstance(value, str):
        return (value,)
    return tuple(str(item) for item in value)


def _map(row: Mapping[str, Any], key: str) -> Mapping[str, Any] | None:
    value = row.get(key)
    return MappingProxyType(dict(value)) if isinstance(value, Mapping) else None


def _strmap(row: Mapping[str, Any], key: str) -> Mapping[str, str]:
    value = row.get(key) or {}
    return MappingProxyType({str(k): str(v) for k, v in dict(value).items()})


# --- declared specs -----------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class Primitive:
    """A structural primitive: one of the two things this capability's type system is made of."""

    primitive: str
    definition: str
    module: str
    symbol: str


@dataclass(frozen=True, slots=True)
class StateClassSpec:
    state_class: str
    definition: str
    binding_required: bool


@dataclass(frozen=True, slots=True)
class BindingOwner:
    """An authority owning a vocabulary this capability binds to, and the reader that reads it."""

    owner: str
    reader: str
    definition: str


@dataclass(frozen=True, slots=True)
class StateSpec:
    """One declared lifecycle state.

    ``terminal`` is parsed and then refused if true. It is present in the data so a future author
    who wants a terminal state must write ``true`` and watch a law refuse it, rather than
    discovering there was never a field for the idea and adding one quietly.
    """

    identifier: str
    title: str
    state_class: str
    definition: str
    terminal: bool
    successors: tuple[str, ...]
    binding: Mapping[str, Any] | None
    binding_gap: Mapping[str, Any] | None
    ucon_research_state: str


@dataclass(frozen=True, slots=True)
class AxisSpec:
    """One independent lifecycle axis, its declared values and its starting value."""

    axis: str
    definition: str
    initial: str
    values: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class QualifierSpec:
    """A declared attribute vocabulary: where a lifecycle state would otherwise have multiplied."""

    qualifier: str
    definition: str
    initial: str
    values: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class Named:
    """A declared vocabulary row that is nothing but an identifier and a definition."""

    identifier: str
    definition: str


@dataclass(frozen=True, slots=True)
class RelationSpec:
    relation: str
    definition: str
    inverse: str


@dataclass(frozen=True, slots=True)
class EntityClassSpec:
    """One of the two entity classes: what it requires, who governs it, how it reaches "
    "disposition."""

    entity_class: str
    title: str
    definition: str
    governance: str
    ucon_kind: str
    ucon_facet: str
    bridge_handler: str
    required_attributes: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class ProfileSpec:
    """The requirement set a subject carries because of what it is, keyed on its classification.

    This is the entity collapse in one type: a contradiction and a gap need different histories, and
    the difference is a row of data rather than a class in code.
    """

    profile: str
    required_attributes: tuple[str, ...]
    required_payload: tuple[str, ...]
    definition: str


@dataclass(frozen=True, slots=True)
class Condition:
    """A condition some directive named by hand, expressed as a composition rather than a type."""

    condition: str
    named_by: str
    state: str
    domain: str
    qualifiers: Mapping[str, str]
    axes: Mapping[str, str]

    def signature(self) -> tuple[Any, ...]:
        """What the ledger can actually tell apart. Two conditions sharing one are a collision."""
        return (
            self.state,
            self.domain,
            tuple(sorted(self.qualifiers.items())),
            tuple(sorted(self.axes.items())),
        )


@dataclass(frozen=True, slots=True)
class ContradictionClassSpec:
    identifier: str
    definition: str
    ucon_contradiction_class: str


@dataclass(frozen=True, slots=True)
class ResolutionStateSpec:
    identifier: str
    definition: str
    contradicting: bool
    ucon_resolution_state: str


@dataclass(frozen=True, slots=True)
class GapClassSpec:
    identifier: str
    definition: str
    ucon_unknown_class: str


@dataclass(frozen=True, slots=True)
class SeveritySpec:
    identifier: str
    rank: int
    definition: str


@dataclass(frozen=True, slots=True)
class DiscoverySource:
    source_id: str
    detector: str
    target: str
    priority: str
    impact: str
    definition: str


@dataclass(frozen=True, slots=True)
class OperatorSpec:
    """An evolution operator. ``implementation`` is the code symbol; ``identifier`` is "
    "vocabulary."""

    identifier: str
    definition: str
    implementation: str


@dataclass(frozen=True, slots=True)
class EvolutionSubject:
    identifier: str
    definition: str
    operators: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class Pair:
    """A declared row that names something and the symbol or subject it is bound to."""

    identifier: str
    bound_to: str


@dataclass(frozen=True, slots=True)
class MechanismSpec:
    """A named mechanism that must resolve to a live module symbol, or the claim is not "
    "implemented."""

    mechanism: str
    module: str
    symbol: str
    definition: str


@dataclass(frozen=True, slots=True)
class SubstrateElement:
    substrate_id: str
    mechanism: str
    module: str
    symbol: str


@dataclass(frozen=True, slots=True)
class FutureCapability:
    identifier: str
    requires: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class RealitySpec:
    identifier: str
    title: str
    residual: bool
    frame_kind: str
    frame_kind_gap: Mapping[str, Any] | None
    systems: Mapping[str, str]

    def unresolved(self, token: str) -> tuple[str, ...]:
        return tuple(sorted(name for name, value in self.systems.items() if value == token))


@dataclass(frozen=True, slots=True)
class TemporalSpec:
    identifier: str
    title: str
    system_type: str
    chronology_model: str
    epoch: str
    calendar_system: str
    causality_model: str
    reference_frame: str
    conversion_authority: str
    epoch_gap: Mapping[str, Any] | None


@dataclass(frozen=True, slots=True)
class ExtensionPoint:
    point_id: str
    subject: str
    owner: str
    admission: str
    evolution_subject: str


@dataclass(frozen=True, slots=True)
class Law:
    law_id: str
    statement: str
    check: str
    blocking: bool


@dataclass(frozen=True, slots=True)
class DisclosedGap:
    """A gap this declaration states about itself, admitted into the ledger as a governed "
    "subject."""

    gap_id: str
    classification: str
    severity: str
    finding: str
    referred_to: str
    remediation: str
    source: str


@dataclass(frozen=True, slots=True)
class GapDisclosureSource:
    source: str
    classification: str
    severity: str
    definition: str


@dataclass(frozen=True, slots=True)
class SeededPopulation:
    population: str
    reader: str
    entity_class: str


@dataclass(frozen=True, slots=True)
class RealityProbe:
    probe_id: str
    probe: str
    declared: str
    measured: str
    on_conflict: str


@dataclass(frozen=True, slots=True)
class ParityLayer:
    layer: str
    evidence: str
    measured_by: str


@dataclass(frozen=True, slots=True)
class SourceDiscipline:
    package: str
    scanned_vocabularies: tuple[str, ...]
    binding_kinds: tuple[Mapping[str, Any], ...]
    exempt_modules: tuple[str, ...]


# --- the declaration ----------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class Declaration:
    """Every declared vocabulary, law, binding, bound and disclosure, as frozen values."""

    artifact_id: str
    name: str
    version: str
    authority: str
    constitutional_superior: str
    strategic_superior: str
    principle: Mapping[str, Any]
    design_rule: Mapping[str, Any]
    primitives: tuple[Primitive, ...]
    supporting_devices: tuple[Primitive, ...]
    primitive_bound: int
    entity_class_bound: int
    state_bound: int
    namespace: str
    key_domain: str
    initial_state: str
    settled_states: tuple[str, ...]
    state_classes: tuple[StateClassSpec, ...]
    binding_owners: tuple[BindingOwner, ...]
    states: tuple[StateSpec, ...]
    lifecycle_axes: tuple[AxisSpec, ...]
    qualifiers: tuple[QualifierSpec, ...]
    residual_domain: str
    domains: tuple[Named, ...]
    residual_relation: str
    relations: tuple[RelationSpec, ...]
    universal_entity_class: str
    link_entity_class: str
    confidence_qualifier: str
    entity_classes: tuple[EntityClassSpec, ...]
    default_profile: str
    profile_roles: Mapping[str, str]
    profiles: tuple[ProfileSpec, ...]
    context_root: str
    context_kinds: tuple[Named, ...]
    residual_context_kind: str
    conditions: tuple[Condition, ...]
    minimum_positions: int
    affected_dimensions: tuple[str, ...]
    contradiction_generates: tuple[str, ...]
    verification_requires: tuple[str, ...]
    contradiction_classes: tuple[ContradictionClassSpec, ...]
    resolution_states: tuple[ResolutionStateSpec, ...]
    gap_classes: tuple[GapClassSpec, ...]
    ucon_unknown_bindings: tuple[Mapping[str, Any], ...]
    residual_gap_class: str
    severities: tuple[SeveritySpec, ...]
    closure_rule: str
    review_cadence_unit: str
    default_review_cadence: int
    minimum_review_cadence: int
    discovery_write_scope: tuple[str, ...]
    discovery_scope_excludes_role: str
    forbidden_write_calls: tuple[str, ...]
    priority_scale: tuple[str, ...]
    impact_scale: tuple[str, ...]
    discovery_targets: tuple[Named, ...]
    discovery_sources: tuple[DiscoverySource, ...]
    evolution_entry_point: str
    operators: tuple[OperatorSpec, ...]
    evolution_subjects: tuple[EvolutionSubject, ...]
    self_evolution_subjects: tuple[Pair, ...]
    self_improvement: tuple[MechanismSpec, ...]
    learning_stages: tuple[Named, ...]
    learning_reversal_operator: str
    meta_relation: str
    meta_subjects: tuple[Pair, ...]
    unresolved_token: str
    reality_dimensions: tuple[Named, ...]
    frame_kind_owner: str
    realities: tuple[RealitySpec, ...]
    temporal_unresolved_token: str
    system_type_owner: str
    chronology_owner: str
    forbidden_source_literals: tuple[str, ...]
    temporal_exempt_modules: tuple[str, ...]
    stability_properties: tuple[Mapping[str, Any], ...]
    stability_exemptions: tuple[str, ...]
    temporal_systems: tuple[TemporalSpec, ...]
    unassigned_owner: str
    ownership_roles: tuple[Named, ...]
    extension_points: tuple[ExtensionPoint, ...]
    future_domain_subjects: tuple[Pair, ...]
    admissibility_question: str
    admissibility_subjects: tuple[str, ...]
    substrate_elements: tuple[SubstrateElement, ...]
    future_capabilities: tuple[FutureCapability, ...]
    anti_finite_mechanisms: tuple[MechanismSpec, ...]
    forbidden_outcomes: tuple[Named, ...]
    architecture_tiers: tuple[Mapping[str, Any], ...]
    proposal_requirements: tuple[str, ...]
    default_rule: tuple[str, ...]
    reality_probes: tuple[RealityProbe, ...]
    conflict_contradiction_class: str
    conflict_owner: str
    parity_layers: tuple[ParityLayer, ...]
    self_review_gap: str
    review_exemptions: tuple[str, ...]
    gap_disclosure_sources: tuple[GapDisclosureSource, ...]
    closure_criterion_template: str
    disclosure_review_cadence: int
    disclosed_gaps: tuple[DisclosedGap, ...]
    forbidden_phrases: tuple[str, ...]
    preserved_sites: tuple[str, ...]
    stated_non_goals: tuple[str, ...]
    seeded_populations: tuple[SeededPopulation, ...]
    reported_metrics: tuple[str, ...]
    source_discipline: SourceDiscipline
    evidence_home: str
    evidence_records: tuple[Mapping[str, Any], ...]
    gate: Mapping[str, Any]
    closed_set: bool
    upper_limit: Any
    source: str = field(default="", compare=False, repr=False)

    # --- accessors that never default -----------------------------------------------------

    @property
    def state_ids(self) -> tuple[str, ...]:
        return tuple(spec.identifier for spec in self.states)

    @property
    def domain_ids(self) -> tuple[str, ...]:
        return tuple(spec.identifier for spec in self.domains)

    @property
    def relation_ids(self) -> tuple[str, ...]:
        return tuple(spec.relation for spec in self.relations)

    @property
    def entity_class_ids(self) -> tuple[str, ...]:
        return tuple(spec.entity_class for spec in self.entity_classes)

    @property
    def profile_ids(self) -> tuple[str, ...]:
        return tuple(spec.profile for spec in self.profiles)

    @property
    def qualifier_ids(self) -> tuple[str, ...]:
        return tuple(spec.qualifier for spec in self.qualifiers)

    @property
    def axis_ids(self) -> tuple[str, ...]:
        return tuple(spec.axis for spec in self.lifecycle_axes)

    @property
    def gap_class_ids(self) -> tuple[str, ...]:
        return tuple(spec.identifier for spec in self.gap_classes)

    @property
    def severity_ids(self) -> tuple[str, ...]:
        return tuple(spec.identifier for spec in self.severities)

    @property
    def reality_ids(self) -> tuple[str, ...]:
        return tuple(spec.identifier for spec in self.realities)

    @property
    def temporal_ids(self) -> tuple[str, ...]:
        return tuple(spec.identifier for spec in self.temporal_systems)

    @property
    def context_kind_ids(self) -> tuple[str, ...]:
        return tuple(spec.identifier for spec in self.context_kinds)

    def _find(self, rows: Any, attribute: str, value: str, label: str) -> Any:
        for spec in rows:
            if getattr(spec, attribute) == value:
                return spec
        raise DeclarationError(f"{value!r} is not a declared {label}")

    def state(self, identifier: str) -> StateSpec:
        return self._find(self.states, "identifier", identifier, "state")

    def axis(self, identifier: str) -> AxisSpec:
        return self._find(self.lifecycle_axes, "axis", identifier, "lifecycle axis")

    def qualifier(self, identifier: str) -> QualifierSpec:
        return self._find(self.qualifiers, "qualifier", identifier, "qualifier")

    def domain(self, identifier: str) -> Named:
        return self._find(self.domains, "identifier", identifier, "domain")

    def relation(self, identifier: str) -> RelationSpec:
        return self._find(self.relations, "relation", identifier, "relation")

    def entity_class(self, identifier: str) -> EntityClassSpec:
        return self._find(self.entity_classes, "entity_class", identifier, "entity class")

    def profile(self, identifier: str) -> ProfileSpec:
        return self._find(self.profiles, "profile", identifier, "profile")

    @property
    def research_facets(self) -> tuple[str, ...]:
        """The payload keys a research subject must carry, read from its profile rather than "
        "copied."""
        return self.profile(self.profile_for("investigation")).required_payload

    def profile_for(self, role: str) -> str:
        """The profile a code role addresses. How a module reaches a profile without naming it."""
        profile = self.profile_roles.get(role)
        if profile is None:
            raise DeclarationError(f"no profile role {role!r} is declared")
        return profile

    def gap_class(self, identifier: str) -> GapClassSpec:
        return self._find(self.gap_classes, "identifier", identifier, "gap class")

    def severity(self, identifier: str) -> SeveritySpec:
        return self._find(self.severities, "identifier", identifier, "severity")

    def contradiction_class(self, identifier: str) -> ContradictionClassSpec:
        return self._find(
            self.contradiction_classes, "identifier", identifier, "contradiction class"
        )

    def resolution_state(self, identifier: str) -> ResolutionStateSpec:
        return self._find(self.resolution_states, "identifier", identifier, "resolution state")

    def reality(self, identifier: str) -> RealitySpec:
        return self._find(self.realities, "identifier", identifier, "reality")

    def temporal_system(self, identifier: str) -> TemporalSpec:
        return self._find(self.temporal_systems, "identifier", identifier, "temporal system")

    def law(self, law_id: str) -> Law:
        return self._find(self.laws, "law_id", law_id, "law")

    def substrate(self, substrate_id: str) -> SubstrateElement:
        return self._find(
            self.substrate_elements, "substrate_id", substrate_id, "substrate element"
        )

    def point_for_admission(self, admission: str) -> ExtensionPoint:
        """The extension point an admission serves.

        This is how an admission function learns what it admits and which evolution subject the
        admission belongs to, without ever writing a vocabulary member in code.
        """
        for spec in self.extension_points:
            if spec.admission == admission:
                return spec
        raise DeclarationError(f"no extension point declares the admission {admission!r}")

    laws: tuple[Law, ...] = ()

    # --- derived views --------------------------------------------------------------------

    def required_for(
        self, entity_class: str, profile: str
    ) -> tuple[tuple[str, ...], tuple[str, ...]]:
        """The attributes and payload keys a subject of this class and profile must carry."""
        structural = self.entity_class(entity_class).required_attributes
        spec = self.profile(profile)
        merged = list(structural)
        for attribute in spec.required_attributes:
            if attribute not in merged:
                merged.append(attribute)
        return tuple(merged), spec.required_payload

    def all_disclosed_gaps(self) -> tuple[DisclosedGap, ...]:
        """Every gap this declaration discloses, from any disclosure site, in identifier order.

        Three inline sites contribute — a state binding to no owner, a reality whose frame binding
        is approximate or absent, and a temporal system with no epoch — plus the gaps stated
        directly. Collecting them here is what lets URKE-L-25 measure that every one is a governed
        subject rather than a sentence in a document.
        """
        by_source = {spec.source: spec for spec in self.gap_disclosure_sources}
        collected: list[DisclosedGap] = list(self.disclosed_gaps)
        sites = (
            ("state_binding", [spec.binding_gap for spec in self.states]),
            ("reality_frame_binding", [spec.frame_kind_gap for spec in self.realities]),
            ("temporal_epoch", [spec.epoch_gap for spec in self.temporal_systems]),
        )
        for source, gaps in sites:
            template = by_source.get(source)
            if template is None:
                raise DeclarationError(
                    f"gap_disclosure declares no source {source!r}, so gaps found there cannot be "
                    "attributed a classification or a severity"
                )
            for entry in gaps:
                if entry is None:
                    continue
                collected.append(
                    DisclosedGap(
                        gap_id=str(entry.get("gap_id") or ""),
                        classification=template.classification,
                        severity=template.severity,
                        finding=str(entry.get("finding") or ""),
                        referred_to=str(entry.get("referred_to") or ""),
                        remediation=str(entry.get("remediation") or ""),
                        source=source,
                    )
                )
        return tuple(sorted(collected, key=lambda spec: spec.gap_id))

    def declared_bindings(self) -> Mapping[str, frozenset[str]]:
        """The declared name set for every binding kind, keyed by the declared kind label."""
        return MappingProxyType(
            {
                "law check": frozenset(spec.check for spec in self.laws),
                "detector": frozenset(spec.detector for spec in self.discovery_sources),
                "admission": frozenset(
                    [spec.admission for spec in self.extension_points]
                    + [spec.bound_to for spec in self.self_evolution_subjects]
                    + [spec.bound_to for spec in self.future_domain_subjects]
                ),
                "operator": frozenset(spec.implementation for spec in self.operators),
                "bridge handler": frozenset(spec.bridge_handler for spec in self.entity_classes),
                "population reader": frozenset(spec.reader for spec in self.seeded_populations),
                "attribute reader": frozenset(
                    [a for spec in self.entity_classes for a in spec.required_attributes]
                    + [a for spec in self.profiles for a in spec.required_attributes]
                ),
                "vocabulary owner reader": frozenset(spec.reader for spec in self.binding_owners),
                "parity measure": frozenset(spec.measured_by for spec in self.parity_layers),
                "reality probe": frozenset(spec.probe for spec in self.reality_probes),
            }
        )

    def metrics(self) -> dict[str, int | float]:
        """The complexity budget, computed. Reported every run so architecture growth is visible."""
        qualifier_values = sum(len(spec.values) for spec in self.qualifiers)
        data_rows = (
            len(self.domains)
            + len(self.relations)
            + len(self.profiles)
            + len(self.qualifiers)
            + qualifier_values
            + len(self.realities)
            + len(self.temporal_systems)
            + len(self.context_kinds)
            + len(self.gap_classes)
            + len(self.discovery_sources)
            + len(self.evolution_subjects)
            + len(self.learning_stages)
            + len(self.conditions)
        )
        primitives = len(self.primitives)
        return {
            "axis_count": len(self.lifecycle_axes),
            "complexity_ratio": round(len(self.conditions) / primitives, 3) if primitives else 0.0,
            "condition_count": len(self.conditions),
            "data_row_count": data_rows,
            "domain_count": len(self.domains),
            "entity_class_count": len(self.entity_classes),
            "law_count": len(self.laws),
            "primitive_count": primitives,
            "profile_count": len(self.profiles),
            "qualifier_count": len(self.qualifiers),
            "qualifier_value_count": qualifier_values,
            "relation_count": len(self.relations),
            "state_count": len(self.states),
        }

    def digest_payload(self) -> dict[str, Any]:
        """The declaration's certification identity: the WHOLE parsed declaration, minus
        the exclusions ``DIGEST_EXCLUSIONS`` names and states a reason for.

        THIS USED TO BE A PROJECTION OF THIRTEEN KEYS, AND IT CARRIED THE DEFECT UEC-000001
        MEASURED IN ``engine/construct``. Every one of those keys collapsed its specs to bare
        identifiers, so the declaration could change its meaning without changing its identity.
        Executed against the previous surface: flipping ``blocking`` on ``URKE-L-01`` — the flag
        ``contract.py`` reads to choose ``OPEN`` or ``CLOSED`` — left the digest byte-identical
        at ``af30af45…``. One hundred and one of the one hundred and fifteen parsed fields were
        outside the identity entirely.

        Inclusion is now the default, derived from :func:`dataclasses.fields`, so a field added
        to :class:`Declaration` is inside the identity on the day it is written; omitting one
        requires writing it into ``DIGEST_EXCLUSIONS`` with the reason it cannot reach a
        verdict. ``test_recursive_knowledge.py`` refuses a stale exclusion in the other
        direction, so the disclosure cannot outlive the field it describes.
        """
        return canonical_payload(self, exclude=tuple(DIGEST_EXCLUSIONS))

    # --- coherence ------------------------------------------------------------------------

    def validate(self, implemented: Mapping[str, frozenset[str]]) -> list[str]:
        """Return every incoherence found, or an empty list. Never raises for a finding."""
        problems: list[str] = []
        problems.extend(self._validate_bindings(implemented))
        problems.extend(self._validate_states())
        problems.extend(self._validate_composition())
        problems.extend(self._validate_discovery())
        problems.extend(self._validate_evolution())
        problems.extend(self._validate_reality_and_time())
        problems.extend(self._validate_bounds())
        problems.extend(self._validate_governance())
        return problems

    def _validate_bindings(self, implemented: Mapping[str, frozenset[str]]) -> list[str]:
        problems: list[str] = []
        declared = self.declared_bindings()
        for kind in sorted(declared):
            live = implemented.get(kind)
            if live is None:
                problems.append(f"nothing supplied the implemented set for binding kind {kind!r}")
                continue
            for name in sorted(declared[kind] - live):
                problems.append(f"{kind} {name!r} is declared and not implemented")
            for name in sorted(live - declared[kind]):
                problems.append(f"{kind} {name!r} is implemented and no declaration claims it")
        return problems

    def _validate_states(self) -> list[str]:
        problems: list[str] = []
        ids = set(self.state_ids)
        if not ids:
            problems.append("no state is declared")
        if self.initial_state not in ids:
            problems.append(f"the initial state {self.initial_state!r} is not declared")
        classes = {spec.state_class for spec in self.state_classes}
        for spec in self.states:
            if spec.terminal:
                problems.append(f"state {spec.identifier!r} declares itself terminal")
            if not spec.successors:
                problems.append(f"state {spec.identifier!r} declares no successor")
            for successor in spec.successors:
                if successor not in ids:
                    problems.append(
                        f"state {spec.identifier!r} names undeclared successor {successor!r}"
                    )
            if spec.state_class not in classes:
                problems.append(
                    f"state {spec.identifier!r} names undeclared state class {spec.state_class!r}"
                )
            if spec.binding is None and spec.binding_gap is None:
                problems.append(
                    f"state {spec.identifier!r} binds to no vocabulary owner and discloses no gap"
                )
            if spec.binding is not None:
                owners = {owner.owner for owner in self.binding_owners}
                if str(spec.binding.get("owner")) not in owners:
                    problems.append(
                        f"state {spec.identifier!r} binds to undeclared owner "
                        f"{spec.binding.get('owner')!r}"
                    )
        reachable = self._reachable(self.initial_state)
        for identifier in sorted(ids - reachable - {self.initial_state}):
            problems.append(
                f"state {identifier!r} is unreachable from the initial state, so nothing can ever "
                "be moved into it"
            )
        for state in self.settled_states:
            if state not in ids:
                problems.append(f"the settled list names undeclared state {state!r}")
        if len(self.settled_states) >= len(ids):
            problems.append("every state is declared settled, so nothing would ever be discovered")
        if not self.settled_states:
            problems.append("no state is declared settled, so nothing could ever come to rest")
        return problems

    def _reachable(self, start: str) -> set[str]:
        seen: set[str] = set()
        frontier = [start]
        while frontier:
            current = frontier.pop()
            for spec in self.states:
                if spec.identifier != current:
                    continue
                for successor in spec.successors:
                    if successor not in seen:
                        seen.add(successor)
                        frontier.append(successor)
        return seen

    def _validate_composition(self) -> list[str]:
        problems: list[str] = []
        states, domains = set(self.state_ids), set(self.domain_ids)
        axes = {spec.axis: set(spec.values) for spec in self.lifecycle_axes}
        quals = {spec.qualifier: set(spec.values) for spec in self.qualifiers}
        if not self.lifecycle_axes:
            problems.append("no lifecycle axis is declared")
        for spec in self.lifecycle_axes:
            if len(spec.values) < 2:
                problems.append(
                    f"axis {spec.axis!r} declares fewer than two values, so it cannot vary and "
                    "records nothing"
                )
            if spec.initial not in spec.values:
                problems.append(
                    f"axis {spec.axis!r} starts at {spec.initial!r}, which is not one of its values"
                )
        for spec in self.qualifiers:
            if spec.initial not in spec.values:
                problems.append(
                    f"qualifier {spec.qualifier!r} starts at {spec.initial!r}, which is not one of "
                    "its values"
                )
        if self.residual_domain not in domains:
            problems.append(
                "the residual domain is not declared, so an unclassifiable subject has "
                "nowhere to rest"
            )
        if self.residual_relation not in set(self.relation_ids):
            problems.append("the residual relation is not declared")
        if self.default_profile not in set(self.profile_ids):
            problems.append("the default profile is not declared")
        for role, profile in sorted(self.profile_roles.items()):
            if profile not in set(self.profile_ids):
                problems.append(f"profile role {role!r} names undeclared profile {profile!r}")
        if not self.profile_roles:
            problems.append(
                "no profile role is declared, so no module could address a profile without "
                "hardcoding its name"
            )
        if self.universal_entity_class not in set(self.entity_class_ids):
            problems.append("the universal entity class is not declared")
        if self.residual_context_kind not in set(self.context_kind_ids):
            problems.append("the residual context kind is not declared")
        if not self.conditions:
            problems.append(
                "the condition catalogue is empty, so the claim that collapsing the taxonomy cost "
                "no expressive power would be untested"
            )
        for spec in self.conditions:
            if spec.state not in states:
                problems.append(
                    f"condition {spec.condition!r} names undeclared state {spec.state!r}"
                )
            if spec.domain not in domains:
                problems.append(
                    f"condition {spec.condition!r} names undeclared domain {spec.domain!r}"
                )
            for axis, value in spec.axes.items():
                if axis not in axes:
                    problems.append(f"condition {spec.condition!r} names undeclared axis {axis!r}")
                elif value not in axes[axis]:
                    problems.append(
                        f"condition {spec.condition!r} sets axis {axis!r} to undeclared value "
                        f"{value!r}"
                    )
            for qualifier, value in spec.qualifiers.items():
                if qualifier not in quals:
                    problems.append(
                        f"condition {spec.condition!r} names undeclared qualifier {qualifier!r}"
                    )
                elif value not in quals[qualifier]:
                    problems.append(
                        f"condition {spec.condition!r} sets qualifier {qualifier!r} to undeclared "
                        f"value {value!r}"
                    )
        for spec in self.profiles:
            for attribute in spec.required_attributes:
                if not attribute.strip():
                    problems.append(f"profile {spec.profile!r} requires an unnamed attribute")
        return problems

    def _validate_discovery(self) -> list[str]:
        problems: list[str] = []
        targets = {spec.identifier for spec in self.discovery_targets}
        claimed = {spec.target for spec in self.discovery_sources}
        for target in sorted(targets - claimed):
            problems.append(
                f"discovery target {target!r} is declared and no source claims it, so "
                f"nothing would "
                "ever find one"
            )
        for target in sorted(claimed - targets):
            problems.append(f"a discovery source claims undeclared target {target!r}")
        for spec in self.discovery_sources:
            if spec.priority not in set(self.priority_scale):
                problems.append(
                    f"source {spec.source_id!r} declares off-scale priority {spec.priority!r}"
                )
            if spec.impact not in set(self.impact_scale):
                problems.append(
                    f"source {spec.source_id!r} declares off-scale impact {spec.impact!r}"
                )
        if not self.forbidden_write_calls:
            problems.append(
                "no forbidden write call is declared, so the discovery write-scope law would "
                "measure nothing"
            )
        return problems

    def _validate_evolution(self) -> list[str]:
        problems: list[str] = []
        operator_ids = {spec.identifier for spec in self.operators}
        used: set[str] = set()
        for spec in self.evolution_subjects:
            if not spec.operators:
                problems.append(f"evolution subject {spec.identifier!r} declares no operator")
            for operator in spec.operators:
                if operator not in operator_ids:
                    problems.append(
                        f"evolution subject {spec.identifier!r} names undeclared operator "
                        f"{operator!r}"
                    )
                used.add(operator)
        for operator in sorted(operator_ids - used):
            problems.append(f"operator {operator!r} is declared and no subject uses it")
        subjects = {spec.identifier for spec in self.evolution_subjects}
        for point in self.extension_points:
            if point.evolution_subject not in subjects:
                problems.append(
                    f"extension point {point.point_id!r} names undeclared evolution subject "
                    f"{point.evolution_subject!r}"
                )
        if self.learning_reversal_operator not in operator_ids:
            problems.append(
                f"learning reversal names undeclared operator {self.learning_reversal_operator!r}"
            )
        if len(self.learning_stages) < 2:
            problems.append("the learning pipeline declares fewer than two stages")
        if self.meta_relation not in set(self.relation_ids):
            problems.append(f"meta-knowledge names undeclared relation {self.meta_relation!r}")
        if not self.meta_subjects:
            problems.append("no reflexive meta-knowledge subject is declared")
        required = {item for spec in self.future_capabilities for item in spec.requires}
        declared = {spec.substrate_id for spec in self.substrate_elements}
        for item in sorted(required - declared):
            problems.append(f"a future capability requires undeclared substrate element {item!r}")
        for item in sorted(declared - required):
            problems.append(
                f"substrate element {item!r} is declared and no future capability requires it"
            )
        if not self.anti_finite_mechanisms:
            problems.append("no anti-finite mechanism is declared")
        if not self.self_improvement:
            problems.append("no self-improvement mechanism is declared")
        if not self.proposal_requirements:
            problems.append(
                "no architectural proposal requirement is declared, so architecture could change "
                "with nothing to satisfy"
            )
        if not self.default_rule:
            problems.append("no default rule is declared for a novel construct")
        return problems

    def _validate_reality_and_time(self) -> list[str]:
        problems: list[str] = []
        dimensions = {spec.identifier for spec in self.reality_dimensions}
        if not dimensions:
            problems.append("no reality dimension is declared")
        for spec in self.realities:
            for dimension in sorted(dimensions - set(spec.systems)):
                problems.append(
                    f"reality {spec.identifier!r} omits declared dimension {dimension!r}; an "
                    "omitted dimension is a silent default, which is what the unresolved token is "
                    "for"
                )
            for dimension in sorted(set(spec.systems) - dimensions):
                problems.append(
                    f"reality {spec.identifier!r} declares undeclared dimension {dimension!r}"
                )
            if not spec.frame_kind and spec.frame_kind_gap is None:
                problems.append(
                    f"reality {spec.identifier!r} binds to no frame kind and discloses no gap"
                )
        if not any(spec.residual for spec in self.realities):
            problems.append(
                "no reality is declared residual, so a reality nobody has met has nowhere to rest"
            )
        if self.context_root not in set(self.reality_ids):
            problems.append(
                f"the root context {self.context_root!r} is not a declared reality, so the context "
                "chain would bottom out in nothing"
            )
        for spec in self.temporal_systems:
            if not spec.system_type.strip():
                problems.append(f"temporal system {spec.identifier!r} declares no system type")
            if not spec.chronology_model.strip():
                problems.append(f"temporal system {spec.identifier!r} declares no chronology model")
        if not any(spec.epoch_gap is not None for spec in self.temporal_systems):
            problems.append(
                "no temporal system discloses an epoch gap, so the residual chronology would be "
                "claiming an epoch it cannot have"
            )
        if not self.forbidden_source_literals:
            problems.append(
                "no forbidden temporal literal is declared, so the temporal-assumption law would "
                "measure nothing"
            )
        return problems

    def _validate_bounds(self) -> list[str]:
        problems: list[str] = []
        if len(self.primitives) > self.primitive_bound:
            problems.append(
                f"{len(self.primitives)} structural primitives are declared and the bound is "
                f"{self.primitive_bound}"
            )
        if len(self.entity_classes) > self.entity_class_bound:
            problems.append(
                f"{len(self.entity_classes)} entity classes are declared and the bound is "
                f"{self.entity_class_bound}"
            )
        if len(self.states) > self.state_bound:
            problems.append(
                f"{len(self.states)} states are declared and the bound is {self.state_bound}"
            )
        for label, bound in (
            ("primitive", self.primitive_bound),
            ("entity class", self.entity_class_bound),
            ("state", self.state_bound),
        ):
            if bound < 1:
                problems.append(
                    f"the {label} bound is {bound}, which forbids the foundation itself"
                )
        if not self.reported_metrics:
            problems.append("no complexity metric is declared for reporting")
        return problems

    def _validate_governance(self) -> list[str]:
        problems: list[str] = []
        roles = {spec.identifier for spec in self.ownership_roles}
        if self.unassigned_owner not in roles:
            problems.append(
                f"the unassigned owner token {self.unassigned_owner!r} is not a declared role, so "
                "an unowned subject could not be admitted and would instead be dropped"
            )
        if not self.laws:
            problems.append("no law is declared")
        for spec in self.laws:
            if not spec.blocking:
                problems.append(
                    f"law {spec.law_id!r} is non-blocking; a law that cannot close the gate is a "
                    "report"
                )
            if not spec.statement.strip():
                problems.append(f"law {spec.law_id!r} states nothing")
        if self.review_exemptions:
            problems.append(
                "the review exemption list is not empty; an exemption mechanism that exists is an "
                "exemption mechanism that will be used"
            )
        if not self.parity_layers:
            problems.append("no parity layer is declared")
        if not self.reality_probes:
            problems.append(
                "no reality probe is declared, so the declaration would never be compared against "
                "the measured world"
            )
        if not self.forbidden_phrases:
            problems.append("no forbidden phrase is declared, so the non-goal law would be vacuous")
        if not self.forbidden_outcomes:
            problems.append("no forbidden outcome is declared")
        if self.minimum_positions < 2:
            problems.append(
                "a contradiction is declared to need fewer than two positions, which would make a "
                "one-sided disagreement recordable as a contradiction"
            )
        if not any(spec.contradicting for spec in self.resolution_states):
            problems.append("no resolution state leaves a contradiction standing")
        if not any(not spec.contradicting for spec in self.resolution_states):
            problems.append("no resolution state resolves a contradiction")
        if self.residual_gap_class not in set(self.gap_class_ids):
            problems.append("the residual gap class is not declared")
        if self.closed_set:
            problems.append("the declaration marks itself a closed set")
        if self.upper_limit is not None:
            problems.append(f"the declaration declares an upper limit of {self.upper_limit!r}")
        if not self.evidence_home.strip():
            problems.append("no evidence home is declared")
        if not str(self.gate.get("verify_stage_label") or "").strip():
            problems.append("the gate declares no verify stage label")
        return problems

    def require_valid(self, implemented: Mapping[str, frozenset[str]]) -> None:
        """Raise :class:`DeclarationError` unless the declaration is coherent."""
        problems = self.validate(implemented)
        if problems:
            head = "; ".join(problems[:8])
            tail = f" (+{len(problems) - 8} more)" if len(problems) > 8 else ""
            raise DeclarationError("the declaration is incoherent: " + head + tail)


# --- parsing ------------------------------------------------------------------------------


def _named(document: Mapping[str, Any], *path: str, key: str = "identifier") -> tuple[Named, ...]:
    return tuple(
        Named(
            identifier=_text(row, key, where=f"a {path[-1]} row"),
            definition=_text(row, "definition", where=f"a {path[-1]} row", required=False),
        )
        for row in _rows(document, *path)
    )


def _pairs(document: Mapping[str, Any], *path: str, key: str, bound: str) -> tuple[Pair, ...]:
    return tuple(
        Pair(
            identifier=_text(row, key, where=f"a {path[-1]} row"),
            bound_to=_text(row, bound, where=f"a {path[-1]} row"),
        )
        for row in _rows(document, *path)
    )


def _mechanisms(document: Mapping[str, Any], *path: str) -> tuple[MechanismSpec, ...]:
    return tuple(
        MechanismSpec(
            mechanism=_text(row, "mechanism", where="a mechanism row"),
            module=_text(row, "module", where="a mechanism row"),
            symbol=_text(row, "symbol", where="a mechanism row"),
            definition=_text(row, "definition", where="a mechanism row", required=False)
            or _text(row, "behaviour", where="a mechanism row", required=False),
        )
        for row in _rows(document, *path)
    )


def parse(document: Mapping[str, Any], *, source: str = "") -> Declaration:
    """Turn a declaration document into a :class:`Declaration`. Raises on anything malformed."""
    gate = _node(document, "gate")
    if not isinstance(gate, Mapping):
        raise DeclarationError("the declaration has no gate block")
    discipline = _node(document, "source_discipline")
    if not isinstance(discipline, Mapping):
        raise DeclarationError("the declaration has no source_discipline block")
    review = dict(_node(document, "strategic_direction", "review"))
    gap_review = dict(_node(document, "gaps", "review"))
    primitives_block = dict(_node(document, "primitives"))

    return Declaration(
        artifact_id=_text(document, "artifact_id", where="the declaration"),
        name=_text(document, "name", where="the declaration"),
        version=_text(document, "version", where="the declaration"),
        authority=_text(document, "authority", where="the declaration"),
        constitutional_superior=_text(document, "constitutional_superior", where="the declaration"),
        strategic_superior=_text(document, "strategic_superior", where="the declaration"),
        principle=MappingProxyType(dict(_node(document, "principle"))),
        design_rule=MappingProxyType(dict(_node(document, "design_rule"))),
        primitives=tuple(
            Primitive(
                primitive=_text(row, "primitive", where="a primitive"),
                definition=_text(row, "definition", where="a primitive"),
                module=_text(row, "module", where="a primitive"),
                symbol=_text(row, "symbol", where="a primitive"),
            )
            for row in _rows(document, "primitives", "elements")
        ),
        supporting_devices=tuple(
            Primitive(
                primitive=_text(row, "device", where="a supporting device"),
                definition=_text(row, "definition", where="a supporting device"),
                module=_text(row, "module", where="a supporting device"),
                symbol=_text(row, "symbol", where="a supporting device"),
            )
            for row in _rows(document, "primitives", "supporting")
        ),
        primitive_bound=int(primitives_block.get("bound") or 0),
        entity_class_bound=int(primitives_block.get("entity_class_bound") or 0),
        state_bound=int(primitives_block.get("state_bound") or 0),
        namespace=_text(dict(_node(document, "identity")), "namespace", where="the identity block"),
        key_domain=_text(
            dict(_node(document, "identity")), "key_domain", where="the identity block"
        ),
        initial_state=_text(dict(_node(document, "states")), "initial", where="the state block"),
        settled_states=_strings(dict(_node(document, "states")), "settled"),
        state_classes=tuple(
            StateClassSpec(
                state_class=_text(row, "class", where="a state class"),
                definition=_text(row, "definition", where="a state class"),
                binding_required=bool(row.get("binding_required")),
            )
            for row in _rows(document, "states", "classes")
        ),
        binding_owners=tuple(
            BindingOwner(
                owner=_text(row, "owner", where="a binding owner"),
                reader=_text(row, "reader", where="a binding owner"),
                definition=_text(row, "definition", where="a binding owner"),
            )
            for row in _rows(document, "states", "binding_owners")
        ),
        states=tuple(
            StateSpec(
                identifier=_text(row, "identifier", where="a state"),
                title=_text(row, "title", where="a state", required=False),
                state_class=_text(row, "state_class", where="a state"),
                definition=_text(row, "definition", where="a state"),
                terminal=bool(row.get("terminal")),
                successors=_strings(row, "successors"),
                binding=_map(row, "binding"),
                binding_gap=_map(row, "binding_gap"),
                ucon_research_state=_text(row, "ucon_research_state", where="a state"),
            )
            for row in _rows(document, "states", "seed")
        ),
        lifecycle_axes=tuple(
            AxisSpec(
                axis=_text(row, "axis", where="a lifecycle axis"),
                definition=_text(row, "definition", where="a lifecycle axis"),
                initial=_text(row, "initial", where="a lifecycle axis"),
                values=_strings(row, "values"),
            )
            for row in _rows(document, "lifecycle_axes", "seed")
        ),
        qualifiers=tuple(
            QualifierSpec(
                qualifier=_text(row, "qualifier", where="a qualifier"),
                definition=_text(row, "definition", where="a qualifier"),
                initial=_text(row, "initial", where="a qualifier"),
                values=_strings(row, "values"),
            )
            for row in _rows(document, "qualifiers", "seed")
        ),
        residual_domain=_text(
            dict(_node(document, "domains")), "residual", where="the domain block"
        ),
        domains=_named(document, "domains", "seed"),
        residual_relation=_text(
            dict(_node(document, "relations")), "residual", where="the relation block"
        ),
        relations=tuple(
            RelationSpec(
                relation=_text(row, "relation", where="a relation"),
                definition=_text(row, "definition", where="a relation"),
                inverse=_text(row, "inverse", where="a relation"),
            )
            for row in _rows(document, "relations", "seed")
        ),
        universal_entity_class=_text(
            dict(_node(document, "entity_classes")), "universal", where="the entity class block"
        ),
        link_entity_class=_text(
            dict(_node(document, "entity_classes")), "link", where="the entity class block"
        ),
        confidence_qualifier=_text(
            dict(_node(document, "qualifiers")), "confidence_qualifier", where="the qualifier block"
        ),
        entity_classes=tuple(
            EntityClassSpec(
                entity_class=_text(row, "entity_class", where="an entity class"),
                title=_text(row, "title", where="an entity class", required=False),
                definition=_text(row, "definition", where="an entity class"),
                governance=_text(row, "governance", where="an entity class"),
                ucon_kind=_text(row, "ucon_kind", where="an entity class"),
                ucon_facet=_text(row, "ucon_facet", where="an entity class"),
                bridge_handler=_text(row, "bridge_handler", where="an entity class"),
                required_attributes=_strings(row, "required_attributes"),
            )
            for row in _rows(document, "entity_classes", "seed")
        ),
        default_profile=_text(
            dict(_node(document, "profiles")), "default", where="the profile block"
        ),
        profile_roles=MappingProxyType(
            {
                _text(row, "role", where="a profile role"): _text(
                    row, "profile", where="a profile role"
                )
                for row in _rows(document, "profiles", "roles")
            }
        ),
        profiles=tuple(
            ProfileSpec(
                profile=_text(row, "profile", where="a profile"),
                required_attributes=_strings(row, "required_attributes"),
                required_payload=_strings(row, "required_payload"),
                definition=_text(row, "definition", where="a profile"),
            )
            for row in _rows(document, "profiles", "seed")
        ),
        context_root=_text(dict(_node(document, "context")), "root", where="the context block"),
        context_kinds=_named(document, "context", "kinds", key="kind"),
        residual_context_kind=_text(
            dict(_node(document, "context")), "residual_kind", where="the context block"
        ),
        conditions=tuple(
            Condition(
                condition=_text(row, "condition", where="a catalogued condition"),
                named_by=_text(row, "named_by", where="a catalogued condition"),
                state=_text(row, "state", where="a catalogued condition"),
                domain=_text(row, "domain", where="a catalogued condition"),
                qualifiers=_strmap(row, "qualifiers"),
                axes=_strmap(row, "axes"),
            )
            for row in _rows(document, "condition_catalogue", "conditions")
        ),
        minimum_positions=int(dict(_node(document, "contradiction")).get("minimum_positions") or 0),
        affected_dimensions=_strings(dict(_node(document, "contradiction")), "affected_dimensions"),
        contradiction_generates=_strings(dict(_node(document, "contradiction")), "generates"),
        verification_requires=_strings(
            dict(_node(document, "contradiction")), "verification_requires"
        ),
        contradiction_classes=tuple(
            ContradictionClassSpec(
                identifier=_text(row, "identifier", where="a contradiction class"),
                definition=_text(row, "definition", where="a contradiction class"),
                ucon_contradiction_class=_text(
                    row, "ucon_contradiction_class", where="a contradiction class"
                ),
            )
            for row in _rows(document, "contradiction", "classes")
        ),
        resolution_states=tuple(
            ResolutionStateSpec(
                identifier=_text(row, "identifier", where="a resolution state"),
                definition=_text(row, "definition", where="a resolution state"),
                contradicting=bool(row.get("contradicting")),
                ucon_resolution_state=_text(
                    row, "ucon_resolution_state", where="a resolution state"
                ),
            )
            for row in _rows(document, "contradiction", "resolution_states")
        ),
        gap_classes=tuple(
            GapClassSpec(
                identifier=_text(row, "identifier", where="a gap class"),
                definition=_text(row, "definition", where="a gap class"),
                ucon_unknown_class=_text(row, "ucon_unknown_class", where="a gap class"),
            )
            for row in _rows(document, "gaps", "classes")
        ),
        ucon_unknown_bindings=tuple(
            MappingProxyType(dict(row))
            for row in _rows(document, "bound_vocabularies", "ucon_unknown_classes")
        ),
        residual_gap_class=_text(dict(_node(document, "gaps")), "residual", where="the gap block"),
        severities=tuple(
            SeveritySpec(
                identifier=_text(row, "identifier", where="a severity"),
                rank=int(row.get("rank") or 0),
                definition=_text(row, "definition", where="a severity"),
            )
            for row in _rows(document, "gaps", "severities")
        ),
        closure_rule=_text(dict(_node(document, "gaps")), "closure_rule", where="the gap block"),
        review_cadence_unit=str(gap_review.get("cadence_unit") or ""),
        default_review_cadence=int(gap_review.get("default_cadence") or 0),
        minimum_review_cadence=int(gap_review.get("minimum_cadence") or 0),
        discovery_write_scope=_strings(dict(_node(document, "discovery")), "write_scope"),
        discovery_scope_excludes_role=_text(
            dict(_node(document, "discovery")), "scope_excludes_role", where="the discovery block"
        ),
        forbidden_write_calls=_strings(dict(_node(document, "discovery")), "forbidden_write_calls"),
        priority_scale=_strings(dict(_node(document, "discovery")), "priority_scale"),
        impact_scale=_strings(dict(_node(document, "discovery")), "impact_scale"),
        discovery_targets=_named(document, "discovery", "targets"),
        discovery_sources=tuple(
            DiscoverySource(
                source_id=_text(row, "source_id", where="a discovery source"),
                detector=_text(row, "detector", where="a discovery source"),
                target=_text(row, "target", where="a discovery source"),
                priority=_text(row, "priority", where="a discovery source"),
                impact=_text(row, "impact", where="a discovery source"),
                definition=_text(row, "definition", where="a discovery source"),
            )
            for row in _rows(document, "discovery", "sources")
        ),
        evolution_entry_point=_text(
            dict(_node(document, "evolution")), "entry_point", where="the evolution block"
        ),
        operators=tuple(
            OperatorSpec(
                identifier=_text(row, "identifier", where="an operator"),
                definition=_text(row, "definition", where="an operator"),
                implementation=_text(row, "implementation", where="an operator"),
            )
            for row in _rows(document, "evolution", "operators")
        ),
        evolution_subjects=tuple(
            EvolutionSubject(
                identifier=_text(row, "identifier", where="an evolution subject"),
                definition=_text(row, "definition", where="an evolution subject"),
                operators=_strings(row, "operators"),
            )
            for row in _rows(document, "evolution", "subjects")
        ),
        self_evolution_subjects=_pairs(
            document, "self_evolution", "subjects", key="identifier", bound="exercised_by"
        ),
        self_improvement=_mechanisms(document, "self_improvement", "mechanisms"),
        learning_stages=_named(document, "learning", "stages", key="stage"),
        learning_reversal_operator=_text(
            dict(_node(document, "learning")), "reversal_operator", where="the learning block"
        ),
        meta_relation=_text(
            dict(_node(document, "meta_knowledge")), "relation", where="the meta block"
        ),
        meta_subjects=_pairs(
            document, "meta_knowledge", "subjects", key="identifier", bound="reflects_on"
        ),
        unresolved_token=_text(
            dict(_node(document, "reality")), "unresolved_token", where="the reality block"
        ),
        reality_dimensions=_named(document, "reality", "dimensions"),
        frame_kind_owner=_text(
            dict(_node(document, "reality")), "frame_kind_owner", where="the reality block"
        ),
        realities=tuple(
            RealitySpec(
                identifier=_text(row, "identifier", where="a reality"),
                title=_text(row, "title", where="a reality", required=False),
                residual=bool(row.get("residual")),
                frame_kind=_text(row, "frame_kind", where="a reality", required=False),
                frame_kind_gap=_map(row, "frame_kind_gap"),
                systems=_strmap(row, "systems"),
            )
            for row in _rows(document, "reality", "seed")
        ),
        temporal_unresolved_token=_text(
            dict(_node(document, "temporal")), "unresolved_token", where="the temporal block"
        ),
        system_type_owner=_text(
            dict(_node(document, "temporal")), "system_type_owner", where="the temporal block"
        ),
        chronology_owner=_text(
            dict(_node(document, "temporal")), "chronology_owner", where="the temporal block"
        ),
        forbidden_source_literals=_strings(
            dict(_node(document, "temporal")), "forbidden_source_literals"
        ),
        temporal_exempt_modules=_strings(dict(_node(document, "temporal")), "exempt_modules"),
        stability_properties=tuple(
            MappingProxyType(dict(row)) for row in _rows(document, "stability", "properties")
        ),
        stability_exemptions=tuple(
            str(item) for item in (dict(_node(document, "stability")).get("exempt") or ())
        ),
        temporal_systems=tuple(
            TemporalSpec(
                identifier=_text(row, "identifier", where="a temporal system"),
                title=_text(row, "title", where="a temporal system", required=False),
                system_type=_text(row, "system_type", where="a temporal system"),
                chronology_model=_text(row, "chronology_model", where="a temporal system"),
                epoch=_text(row, "epoch", where="a temporal system"),
                calendar_system=_text(row, "calendar_system", where="a temporal system"),
                causality_model=_text(row, "causality_model", where="a temporal system"),
                reference_frame=_text(row, "reference_frame", where="a temporal system"),
                conversion_authority=_text(row, "conversion_authority", where="a temporal system"),
                epoch_gap=_map(row, "epoch_gap"),
            )
            for row in _rows(document, "temporal", "seed")
        ),
        unassigned_owner=_text(
            dict(_node(document, "ownership")), "unassigned_token", where="the ownership block"
        ),
        ownership_roles=_named(document, "ownership", "roles"),
        extension_points=tuple(
            ExtensionPoint(
                point_id=_text(row, "point_id", where="an extension point"),
                subject=_text(row, "subject", where="an extension point"),
                owner=_text(row, "owner", where="an extension point"),
                admission=_text(row, "admission", where="an extension point"),
                evolution_subject=_text(row, "evolution_subject", where="an extension point"),
            )
            for row in _rows(document, "extension_points")
        ),
        future_domain_subjects=_pairs(
            document, "future_domain_subjects", key="identifier", bound="admission"
        ),
        admissibility_question=_text(
            dict(_node(document, "admissibility_test")), "question", where="the admissibility block"
        ),
        admissibility_subjects=_strings(dict(_node(document, "admissibility_test")), "subjects"),
        substrate_elements=tuple(
            SubstrateElement(
                substrate_id=_text(row, "substrate_id", where="a substrate element"),
                mechanism=_text(row, "mechanism", where="a substrate element"),
                module=_text(row, "module", where="a substrate element"),
                symbol=_text(row, "symbol", where="a substrate element"),
            )
            for row in _rows(document, "substrate", "elements")
        ),
        future_capabilities=tuple(
            FutureCapability(
                identifier=_text(row, "identifier", where="a future capability"),
                requires=_strings(row, "requires"),
            )
            for row in _rows(document, "future_capabilities", "seed")
        ),
        anti_finite_mechanisms=_mechanisms(document, "anti_finite_mechanisms", "mechanisms"),
        forbidden_outcomes=_named(document, "forbidden_outcomes", "outcomes", key="outcome"),
        architecture_tiers=tuple(
            MappingProxyType(dict(row))
            for row in _rows(document, "architecture_evolution", "tiers")
        ),
        proposal_requirements=_strings(
            dict(_node(document, "architecture_evolution")), "proposal_requirements"
        ),
        default_rule=_strings(dict(_node(document, "architecture_evolution")), "default_rule"),
        reality_probes=tuple(
            RealityProbe(
                probe_id=_text(row, "probe_id", where="a reality probe"),
                probe=_text(row, "probe", where="a reality probe"),
                declared=_text(row, "declared", where="a reality probe"),
                measured=_text(row, "measured", where="a reality probe"),
                on_conflict=_text(row, "on_conflict", where="a reality probe"),
            )
            for row in _rows(document, "strategic_direction", "reality_probes")
        ),
        conflict_contradiction_class=_text(
            dict(_node(document, "strategic_direction")),
            "conflict_contradiction_class",
            where="the strategic direction block",
        ),
        conflict_owner=_text(
            dict(_node(document, "strategic_direction")),
            "conflict_owner",
            where="the strategic direction block",
        ),
        parity_layers=tuple(
            ParityLayer(
                layer=_text(row, "layer", where="a parity layer"),
                evidence=_text(row, "evidence", where="a parity layer"),
                measured_by=_text(row, "measured_by", where="a parity layer"),
            )
            for row in _rows(document, "strategic_direction", "parity_layers")
        ),
        self_review_gap=str(review.get("self_review_gap") or ""),
        review_exemptions=tuple(str(item) for item in (review.get("exempt") or ())),
        gap_disclosure_sources=tuple(
            GapDisclosureSource(
                source=_text(row, "source", where="a gap disclosure source"),
                classification=_text(row, "classification", where="a gap disclosure source"),
                severity=_text(row, "severity", where="a gap disclosure source"),
                definition=_text(row, "definition", where="a gap disclosure source"),
            )
            for row in _rows(document, "gap_disclosure", "sources")
        ),
        closure_criterion_template=_text(
            dict(_node(document, "gap_disclosure")),
            "closure_criterion_template",
            where="the gap disclosure block",
        ),
        disclosure_review_cadence=int(
            dict(_node(document, "gap_disclosure")).get("review_cadence") or 0
        ),
        disclosed_gaps=tuple(
            DisclosedGap(
                gap_id=_text(row, "gap_id", where="a disclosed gap"),
                classification=_text(row, "classification", where="a disclosed gap"),
                severity=_text(row, "severity", where="a disclosed gap"),
                finding=_text(row, "finding", where="a disclosed gap"),
                referred_to=_text(row, "referred_to", where="a disclosed gap"),
                remediation=_text(row, "remediation", where="a disclosed gap"),
                source="declared",
            )
            for row in _rows(document, "disclosed_gaps")
        ),
        forbidden_phrases=_strings(dict(_node(document, "non_goals")), "forbidden_phrases"),
        preserved_sites=_strings(dict(_node(document, "non_goals")), "preserved_sites"),
        stated_non_goals=_strings(dict(_node(document, "non_goals")), "stated_non_goals"),
        seeded_populations=tuple(
            SeededPopulation(
                population=_text(row, "population", where="a seeded population"),
                reader=_text(row, "reader", where="a seeded population"),
                entity_class=_text(row, "entity_class", where="a seeded population"),
            )
            for row in _rows(document, "self_application", "seeded_populations")
        ),
        reported_metrics=_strings(dict(_node(document, "metrics")), "reported"),
        source_discipline=SourceDiscipline(
            package=_text(discipline, "package", where="the source discipline block"),
            scanned_vocabularies=_strings(discipline, "scanned_vocabularies"),
            binding_kinds=tuple(
                MappingProxyType(dict(row))
                for row in (discipline.get("binding_kinds") or ())
                if isinstance(row, Mapping)
            ),
            exempt_modules=_strings(discipline, "exempt_modules"),
        ),
        evidence_home=_text(dict(_node(document, "evidence")), "home", where="the evidence block"),
        evidence_records=tuple(
            MappingProxyType(dict(row)) for row in _rows(document, "evidence", "records")
        ),
        gate=MappingProxyType(dict(gate)),
        closed_set=bool(document.get("closed_set")),
        upper_limit=document.get("upper_limit"),
        laws=tuple(
            Law(
                law_id=_text(row, "law_id", where="a law"),
                statement=_text(row, "statement", where="a law"),
                check=_text(row, "check", where="a law"),
                blocking=bool(row.get("blocking")),
            )
            for row in _rows(document, "laws")
        ),
        source=source,
    )


def load_declaration(path: str | None = None, *, repository: str | None = None) -> Declaration:
    """Read and parse the declaration. Every failure is a fault, never a verdict."""
    root = repository or repo_root()
    target = path or os.path.join(root, DECLARATION_PATH)
    try:
        with open(target, encoding="utf-8") as handle:
            document = json.load(handle)
    except FileNotFoundError as exc:
        raise DeclarationError(f"the declaration is absent at {target}") from exc
    except (OSError, json.JSONDecodeError) as exc:
        raise DeclarationError(f"the declaration cannot be read: {exc}") from exc
    if not isinstance(document, Mapping):
        raise DeclarationError("the declaration is not an object")
    try:
        return parse(document, source=target)
    except DeclarationError:
        raise
    except (KeyError, TypeError, ValueError) as exc:
        raise DeclarationError(f"the declaration is malformed: {exc}") from exc


def scanned_vocabulary(declaration: Declaration) -> dict[str, tuple[str, ...]]:
    """Every domain vocabulary member that must never appear as a source literal, by vocabulary.

    Keyed by the declared vocabulary path so a refusal can name which vocabulary was hardcoded
    rather than only which word was found. Bound both ways against the declared list: a vocabulary
    scanned here that the declaration does not list, or listed and unread, is a fault.
    """
    members: dict[str, tuple[str, ...]] = {
        "states.seed[].identifier": declaration.state_ids,
        "states.classes[].class": tuple(spec.state_class for spec in declaration.state_classes),
        "domains.seed[].identifier": declaration.domain_ids,
        "qualifiers.seed[].qualifier": declaration.qualifier_ids,
        "qualifiers.seed[].values[]": tuple(
            value for spec in declaration.qualifiers for value in spec.values
        ),
        "relations.seed[].relation": declaration.relation_ids,
        "profiles.seed[].profile": declaration.profile_ids,
        "entity_classes.seed[].entity_class": declaration.entity_class_ids,
        "lifecycle_axes.seed[].axis": declaration.axis_ids,
        "lifecycle_axes.seed[].values[]": tuple(
            value for spec in declaration.lifecycle_axes for value in spec.values
        ),
        "gaps.classes[].identifier": declaration.gap_class_ids,
        "gaps.severities[].identifier": declaration.severity_ids,
        "contradiction.classes[].identifier": tuple(
            spec.identifier for spec in declaration.contradiction_classes
        ),
        "contradiction.resolution_states[].identifier": tuple(
            spec.identifier for spec in declaration.resolution_states
        ),
        "reality.seed[].identifier": declaration.reality_ids,
        "reality.dimensions[].identifier": tuple(
            spec.identifier for spec in declaration.reality_dimensions
        ),
        "temporal.seed[].identifier": declaration.temporal_ids,
        "context.kinds[].kind": declaration.context_kind_ids,
        "evolution.subjects[].identifier": tuple(
            spec.identifier for spec in declaration.evolution_subjects
        ),
        "evolution.operators[].identifier": tuple(
            spec.identifier for spec in declaration.operators
        ),
        "discovery.targets[].identifier": tuple(
            spec.identifier for spec in declaration.discovery_targets
        ),
        "learning.stages[].stage": tuple(spec.identifier for spec in declaration.learning_stages),
        "future_capabilities.seed[].identifier": tuple(
            spec.identifier for spec in declaration.future_capabilities
        ),
        "meta_knowledge.subjects[].identifier": tuple(
            spec.identifier for spec in declaration.meta_subjects
        ),
    }
    declared = set(declaration.source_discipline.scanned_vocabularies)
    unknown = sorted(set(members) - declared)
    if unknown:
        raise DeclarationError(
            "this module scans vocabularies the declaration does not list: " + ", ".join(unknown)
        )
    missing = sorted(declared - set(members))
    if missing:
        raise DeclarationError(
            "the declaration lists scanned vocabularies nothing reads: " + ", ".join(missing)
        )
    return members


__all__ = [
    "DECLARATION_PATH",
    "AxisSpec",
    "BindingOwner",
    "Condition",
    "ContradictionClassSpec",
    "Declaration",
    "DeclarationError",
    "DisclosedGap",
    "DiscoverySource",
    "EntityClassSpec",
    "EvolutionSubject",
    "ExtensionPoint",
    "FutureCapability",
    "GapClassSpec",
    "GapDisclosureSource",
    "Law",
    "MechanismSpec",
    "Named",
    "OperatorSpec",
    "Pair",
    "ParityLayer",
    "Primitive",
    "ProfileSpec",
    "QualifierSpec",
    "RealityProbe",
    "RealitySpec",
    "RelationSpec",
    "ResolutionStateSpec",
    "SeededPopulation",
    "SeveritySpec",
    "SourceDiscipline",
    "StateClassSpec",
    "StateSpec",
    "SubstrateElement",
    "TemporalSpec",
    "load_declaration",
    "parse",
    "repo_root",
    "scanned_vocabulary",
]
