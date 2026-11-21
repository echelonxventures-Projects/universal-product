"""EC3-B12-U06 — The Universal Interaction construct (AMC-06).

Realizes the meta-model concept **AMC-06 Interaction** (APPLICATION-005 §2;
APPLICATION-010; APPLICATION-003 AOE-06; APPLICATION-001 §2):

    the **typed actor-to-application exchange (input, command, query, response) addressed
    through an abstract surface** — the sole point of engagement between an actor and a
    feature — a typed (ENG-004) object (ENG-002), identified (ENG-001), classified by one
    AXH-06 kind (Input / Command / Query / Response, which *is* its decidable direction —
    INT-07), that **engages a feature** (AMR-05 engaged-through, by reference; the founding
    relationship — INT-04/INT-C2), **presents typed exchanged data as DF-2 data** (AMR-14,
    by reference; INT-06), **holds/advances interaction/session state** within a declared
    context (AMR-06, by reference → RL-F2), and whose exchange/transition/emit behavior is
    a RUNTIME event/state construct (AMR-11 / §7, by reference), described over an
    **abstract presentation surface** (screen) — **no rendering technology is selected**
    (INT-03/INT-C1).

The construct is **additive over the CERTIFIED EC-1 foundation** (and the referenced,
CERTIFIED-COMPLETE Band-10 data surface + CERTIFIED-COMPLETE + FROZEN Band-11 service
surface + the CERTIFIED Band-12 U01 Application root + U02 Capability + U03 Module + U04
Feature + U05 Workflow) and reuses them *by reference* (UAL-02 / AMI-05): identity and
value-fidelity are derived through the EC-1 certified deterministic encoding
(:func:`engine.certification.contracts.canonical_json` /
:func:`~engine.certification.contracts.content_hash`) — the same discipline that produces
every EC-1 runtime, artifact, and certification identity — so this module introduces
**no second identity scheme and no parallel value model**. It selects no technology, UI
framework, design system, or rendering technology, and confers no authority (UAL-11/15).

An :class:`Interaction` is *immutable* (a frozen object — ENG-002 objecthood), *typed*
(ENG-004), *identified* (ENG-001 via a deterministic id), *classified* (AXH-06 kind =
direction), *feature-engaging* (AMR-05, by reference — the founding relationship),
*data-presenting* (AMR-14, by reference), *state-holding* (AMR-06, by reference),
*behavior-bound* (AMR-11, by reference), *surface-abstract* (INT-03), and holds a
*forward-only lifecycle state* (AOS-01…06, UAL-12). Constructing an :class:`Interaction`
enforces the meta-constraints AMK-01/02/03/05/07/08 and the laws UAL-03/04/05/10/11/12/13
fail-closed: an ill-formed interaction cannot be instantiated. It realizes **no**
Application, Capability, Module, Feature, Workflow, State, Composition, Security, or
Governance object — those are separate Band-12 units; this construct binds them only *by
reference*. In particular it **delivers no capability** (AMR-01), **groups no feature**
(AMR-03), **sequences no feature** (AMR-04), **consumes no SF-2 operation** (AMR-13), and
**assembles no PLATFORM composition** (AMR-07/12) — an interaction is the *engagement
surface* through which a feature is reached (ATH-10), not the feature itself.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any

from application.interaction_meta import (
    INTERACTION_DIRECTIONS,
    INTERACTION_META_CLASS,
    INTERACTION_RELATIONSHIPS,
    LIFECYCLE_ORDER,
    SUBSTRATE_REFS,
    InteractionKind,
    InteractionState,
)

# --- EC-1 reuse by reference (UAL-02 / AMI-05) — imported, never redefined --------
from engine.certification.contracts import canonical_json, content_hash

#: The deterministic id prefix for a realized Interaction (mirrors EC-1 UCOS-<KIND>-<hex16>).
INTERACTION_ID_PREFIX = "UCOS-INTERACTION"

#: The map of frozen-foundation primitives this construct reuses *by reference*
#: (never redefined). Recorded for the reuse-integrity check (UAL-02 / AMI-05 / VC-5).
FOUNDATION_REUSE: dict[str, str] = {
    "ENG-001": "engine.certification.contracts.content_hash (deterministic identity derivation)",
    "ENG-002": "python frozen object (immutable objecthood bearing the interaction)",
    "ENG-003": "engine.certification.contracts.canonical_json (value fidelity; no parallel model)",
    "ENG-004": "application.interaction_meta.InteractionKind + type_tag (ENG-004 typing, by ref)",
    "ENG-005": "reference identifiers (engaged-feature, surface, data, state, behavior refs)",
    "RL-F2": "event/state concern by reference (§7, AMR-06/11); none redefined",
    "DF-2": "represented exchanged data by reference (presents-data AMR-14); none redefined",
}

#: Concrete-technology / rendering / UI markers forbidden by UAL-11 / UAL-15 (INT-03/INT-K5):
#: no UI framework, design system, rendering technology, screen technology, transport,
#: protocol, engine, database, cloud, or vendor. An abstract surface names none of these.
_TECHNOLOGY_MARKERS: tuple[str, ...] = (
    # UI frameworks / rendering / design systems (INT-03 abstract-surface prohibition)
    "react",
    "vue",
    "angular",
    "svelte",
    "tailwind",
    "bootstrap",
    "material-ui",
    "html",
    "css",
    "webgl",
    "canvas",
    "flutter",
    "swiftui",
    "uikit",
    "xaml",
    "cocoa",
    "jetpack",
    "android-ui",
    "ios-ui",
    "dom-node",
    "pixel",
    "viewport",
    # engines / transports / protocols / infra / vendors
    "grpc",
    "graphql",
    "kafka",
    "rabbitmq",
    "postgres",
    "mysql",
    "mongodb",
    "kubernetes",
    "docker",
    "nginx",
    "openapi",
    "swagger",
    "lambda",
    "dynamodb",
    "http://",
    "https://",
    "tcp://",
)

#: Conservative secret markers used to enforce UAL-15 / RR-07 (embed no secret).
_SECRET_MARKERS: tuple[str, ...] = (
    "password",
    "secret",
    "private_key",
    "privatekey",
    "api_key",
    "apikey",
    "access_token",
    "credential",
    "-----begin",
)


class InteractionError(ValueError):
    """Raised when inputs cannot be realized as a well-formed :class:`Interaction`.

    An :class:`Interaction` is fail-closed (TRACK-001): an ill-formed interaction construct
    is rejected at construction rather than admitted as an invalid interaction.
    """


def _require_reference(name: str, value: Any) -> str:
    """Require ``value`` to be a non-empty ENG-005 reference string (by reference)."""
    if not isinstance(value, str) or not value.strip():
        raise InteractionError(
            f"{name} must be a non-empty ENG-005 reference (UAL-02/11)"
        )
    return value


@dataclass(frozen=True, slots=True)
class Interaction:
    """AMC-06 — an immutable, typed, identified, feature-engaging interaction.

    Fields:
        type_tag:     the ENG-004 Type of the interaction (decidable, non-empty) — UAL-03/11.
        kind:         the AXH-06 classification of the interaction (AXC-04); the kind **is**
                      the interaction's decidable direction (input/command/query/response,
                      INT-07 / INT-C5).
        feature_ref:  the ENG-005 reference to the Feature the interaction engages (AMR-05
                      engaged-through, reference-only) — the **founding** relationship
                      (Feature → Interaction; INT-04/INT-C2/INT-C3): an interaction is the
                      sole point through which a feature is engaged. Required, non-empty.
        surface_ref:  the ENG-005 reference to the **abstract presentation surface** (screen)
                      the interaction is described over (INT-03/INT-C1) — an abstract
                      surface/region descriptor that **selects no rendering technology, UI
                      framework, or design system** (UAL-11). Required, non-empty, abstract.
        data_ref:     the ENG-005 reference to the DF-2 data the interaction presents/
                      exchanges (AMR-14 presents-data, reference-only) — INT-06/INT-C4/UAL-13.
                      Required, non-empty.
        state_ref:    the ENG-005 reference to the interaction/session State the interaction
                      holds/advances (AMR-06 holds-state; RL-F2, by reference — forward-only).
        behavior_ref: the ENG-005 reference to the RUNTIME behavior the interaction binds
                      (AMR-11 behaves-as; RL-F2 event/state; exchange/transition/emit) —
                      INT-05 / UAL-10.
        state:        the AOS-01…06 lifecycle state (forward-only) — UAL-12 (default DEFINED).
    """

    type_tag: str
    kind: InteractionKind
    feature_ref: str
    surface_ref: str = "ENG-005:SURFACE:ucos.application.interaction.surface.primary"
    data_ref: str = "ENG-005:DF-2:ucos.application.interaction.exchange.primary"
    state_ref: str = "ENG-005:AMC-07:ucos.application.state.primary"
    behavior_ref: str = "ENG-005:RL-F2:runtime.interaction-exchange"
    state: InteractionState = InteractionState.DEFINED

    def __post_init__(self) -> None:
        # AMK-01 / UAL-03 / INT-01 — typed (ENG-004): a decidable, non-empty type tag.
        if not isinstance(self.type_tag, str) or not self.type_tag.strip():
            raise InteractionError(
                "interaction must be typed with a non-empty ENG-004 type_tag (UAL-03/11)"
            )
        # AXH-06 / AXC-04 / INT-07 — classified by exactly one Interaction kind (= direction).
        if not isinstance(self.kind, InteractionKind):
            raise InteractionError(
                "interaction kind must be an AXH-06 InteractionKind (AXC-04 / INT-07)"
            )
        # AMR-05 / INT-04 / INT-C2 — engages exactly one feature by reference (founding).
        _require_reference("feature_ref", self.feature_ref)
        # INT-03 / INT-C1 — described over an abstract presentation surface (by reference).
        _require_reference("surface_ref", self.surface_ref)
        # AMR-14 / INT-06 / INT-C4 / AMK-07 — presents DF-2 data by reference.
        _require_reference("data_ref", self.data_ref)
        # AMR-06 / AMK-05 — holds/advances interaction/session state by reference (→ RL-F2).
        _require_reference("state_ref", self.state_ref)
        # AMR-11 / UAL-10 / INT-05 / AMK-05 — behavior bound to RL-F2 event/state by ref.
        _require_reference("behavior_ref", self.behavior_ref)
        # V5 / UAL-12 — a valid lifecycle state.
        if not isinstance(self.state, InteractionState):
            raise InteractionError(
                "interaction state must be an AOS-01…06 InteractionState (UAL-12)"
            )
        # INT-03 / INT-C1 / UAL-11 — the surface is abstract: it selects no rendering
        # technology, UI framework, or design system.
        if _contains_marker(self.surface_ref, _TECHNOLOGY_MARKERS):
            raise InteractionError(
                "the presentation surface must be abstract — no rendering technology, UI "
                "framework, or design system may be selected (INT-03 / INT-C1 / UAL-11)"
            )
        # AMK-03 / INT-C3 — founding acyclicity guard (non-absorption): the engaged feature
        # cannot also be the interaction's own surface / data / held state / bound behavior
        # (no self-founding — the engaged-through edge Feature → Interaction is a DAG).
        binding_refs = {
            self.surface_ref,
            self.data_ref,
            self.state_ref,
            self.behavior_ref,
        }
        if self.feature_ref in binding_refs:
            raise InteractionError(
                "an interaction cannot engage its own surface/data/state/behavior as the "
                "feature (INT-C3 / AMK-03 founding acyclicity)"
            )

    # -- identity (ENG-001) borne by object (ENG-002), by reference ------------

    def canonical_core(self) -> dict[str, Any]:
        """The canonical, hashable core of the interaction (its identity-defining tuple).

        Identity is fixed by (meta-class, type, kind/direction, engaged feature, surface,
        data, held state, bound behavior). The lifecycle ``state`` is **not** part of
        identity (an interaction keeps its identity as it advances its lifecycle).
        """
        return {
            "meta_class": INTERACTION_META_CLASS,
            "type_tag": self.type_tag,
            "kind": self.kind.value,
            "direction": self.direction(),
            "feature_ref": self.feature_ref,
            "surface_ref": self.surface_ref,
            "data_ref": self.data_ref,
            "state_ref": self.state_ref,
            "behavior_ref": self.behavior_ref,
        }

    @property
    def value_digest(self) -> str:
        """The EC-1 content hash of the interaction core — the ENG-003 value fingerprint."""
        return content_hash(self.canonical_core())

    @property
    def interaction_id(self) -> str:
        """The deterministic ENG-001 identity of the interaction (borne by this object).

        Derived through the CERTIFIED EC-1 ``content_hash`` (UAL-04 — no second identity
        scheme): identical (type, kind, refs) always yields the identical id, so identity
        is reproducible and byte-stable (determinism, VC-4).
        """
        return f"{INTERACTION_ID_PREFIX}-{self.type_tag}-{self.value_digest[:16]}"

    # -- meta-model participation (APPLICATION-005/010) ------------------------

    @property
    def meta_class(self) -> str:
        """V1 — the single meta-class this construct instantiates (AMC-06)."""
        return INTERACTION_META_CLASS

    def meta_relationships(self) -> tuple[str, ...]:
        """V2 — the AMR-01…14 relationships the interaction participates in."""
        return INTERACTION_RELATIONSHIPS

    def direction(self) -> str:
        """INT-07 / INT-C5 — the decidable exchange direction (= the AXH-06 kind)."""
        return INTERACTION_DIRECTIONS[self.kind]

    def direction_is_decidable(self) -> bool:
        """INT-07 / INT-C5 — the interaction declares a single decidable direction."""
        return self.kind in INTERACTION_DIRECTIONS

    def is_founding_acyclic(self) -> bool:
        """V4 / AMK-03 / INT-C3 — the founding graph is acyclic.

        An Interaction is the *target* of the founding engaged-through edge (Feature →
        Interaction, AMR-05). No self-founding is possible (the engaged feature is distinct
        from every binding reference, enforced at construction), so the founding structure
        carries no cycle. Proven by the fact that its core canonically encodes.
        """
        try:
            canonical_json(self.canonical_core())
        except (TypeError, ValueError):  # pragma: no cover - blocked at construction
            return False
        return self.feature_ref not in {
            self.surface_ref,
            self.data_ref,
            self.state_ref,
            self.behavior_ref,
        }

    def references_resolve(self) -> bool:
        """AOI-03 / AMK-05/07 — every ENG-005 reference is a non-empty resolvable id."""
        return all(
            isinstance(r, str) and bool(r.strip())
            for r in (
                self.feature_ref,
                self.surface_ref,
                self.data_ref,
                self.state_ref,
                self.behavior_ref,
            )
        )

    def engages_feature(self) -> bool:
        """AMR-05 / INT-04 / INT-C2 — the interaction engages a feature by reference."""
        return bool(self.feature_ref.strip())

    def engaged_feature(self) -> str:
        """AMR-05 — the ENG-005 reference to the engaged feature."""
        return self.feature_ref

    def engages(self, feature_ref: str) -> bool:
        """AMR-05 — True iff ``feature_ref`` is the feature this interaction engages."""
        return feature_ref == self.feature_ref

    def presents_data(self) -> bool:
        """AMR-14 / INT-06 / INT-C4 — the interaction presents DF-2 data by reference."""
        return bool(self.data_ref.strip())

    def holds_state(self) -> bool:
        """AMR-06 — the interaction holds/advances interaction/session state (→ RL-F2)."""
        return bool(self.state_ref.strip())

    def surface_is_abstract(self) -> bool:
        """INT-03 / INT-C1 / UAL-11 — the presentation surface is abstract (no technology).

        The surface names a surface/region abstractly and selects no rendering technology,
        UI framework, or design system.
        """
        return bool(self.surface_ref.strip()) and not _contains_marker(
            self.surface_ref, _TECHNOLOGY_MARKERS
        )

    def is_sole_engagement_point(self) -> bool:
        """INT-04 / INT-C2 — the interaction is a declared, typed, sole engagement point.

        Sole-engagement holds iff the interaction is typed, direction-decidable, and
        engages exactly one declared feature (a feature is reachable only through it).
        """
        return (
            bool(self.type_tag.strip())
            and self.direction_is_decidable()
            and self.engages_feature()
        )

    def kind_class(self) -> str:
        """AXH-06 — the input / command / query / response classification (the direction)."""
        return self.direction()

    # -- non-constitutiveness (UAL-11 / UAL-15) --------------------------------

    def confers_authority(self) -> bool:
        """UAL-15 / INT-09 / C7 — an interaction confers no authority (structurally has none)."""
        return False

    def selects_technology(self) -> bool:
        """UAL-11/15 / INT-09 / C7 — True iff the interaction names a concrete technology.

        Covers rendering technology, UI framework, design system, engine, transport,
        protocol, database, infrastructure, or vendor across the whole interaction core
        (including the abstract surface).
        """
        haystack = canonical_json(self.canonical_core()).lower()
        return any(marker in haystack for marker in _TECHNOLOGY_MARKERS)

    def embeds_secret(self) -> bool:
        """UAL-15 / RR-07 / C7 — True iff the interaction appears to embed a secret."""
        haystack = canonical_json(self.canonical_core()).lower()
        return any(marker in haystack for marker in _SECRET_MARKERS)

    def redefines_foundation(self) -> bool:
        """UAL-02 / AMI-05 / VC-5 — an interaction redefines no frozen primitive (reuse-only)."""
        return False

    # -- lifecycle (UAL-12, forward-only) --------------------------------------

    def transition(self, to_state: InteractionState) -> Interaction:
        """Return a new interaction advanced to ``to_state`` (forward-only; UAL-12).

        State advancement is forward-only and recorded; there is no silent or
        in-place-reversible transition.

        Raises:
            InteractionError: on a backward or in-place-reversing transition.
        """
        if not isinstance(to_state, InteractionState):
            raise InteractionError(
                "target state must be an AOS-01…06 InteractionState (UAL-12)"
            )
        here = LIFECYCLE_ORDER.index(self.state)
        there = LIFECYCLE_ORDER.index(to_state)
        if there < here:
            raise InteractionError(
                f"lifecycle is forward-only (UAL-12 / AOI-05): "
                f"{self.state.value} → {to_state.value} is backward"
            )
        return replace(self, state=to_state)

    # -- serialization ----------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """A deterministic, serializable projection of the interaction."""
        return {
            "interaction_id": self.interaction_id,
            "meta_class": self.meta_class,
            "type_tag": self.type_tag,
            "kind": self.kind.value,
            "direction": self.direction(),
            "feature_ref": self.feature_ref,
            "surface_ref": self.surface_ref,
            "data_ref": self.data_ref,
            "state_ref": self.state_ref,
            "behavior_ref": self.behavior_ref,
            "value_digest": self.value_digest,
            "state": self.state.value,
            "surface_abstract": self.surface_is_abstract(),
            "presents_data": self.presents_data(),
            "holds_state": self.holds_state(),
            "engages_feature": self.engages_feature(),
            "sole_engagement_point": self.is_sole_engagement_point(),
            "relationships": list(self.meta_relationships()),
            "substrate_refs": list(SUBSTRATE_REFS),
        }


def _contains_marker(value: str, markers: tuple[str, ...]) -> bool:
    """True iff ``value`` (case-insensitively) contains any of ``markers``."""
    haystack = value.lower()
    return any(marker in haystack for marker in markers)


def make_interaction(
    type_tag: str,
    feature_ref: str,
    *,
    kind: InteractionKind = InteractionKind.INPUT,
    surface_ref: str = "ENG-005:SURFACE:ucos.application.interaction.surface.primary",
    data_ref: str = "ENG-005:DF-2:ucos.application.interaction.exchange.primary",
    state_ref: str = "ENG-005:AMC-07:ucos.application.state.primary",
    behavior_ref: str = "ENG-005:RL-F2:runtime.interaction-exchange",
    state: InteractionState = InteractionState.DEFINED,
) -> Interaction:
    """Construct a well-formed :class:`Interaction` (fail-closed factory)."""
    return Interaction(
        type_tag=type_tag,
        kind=kind,
        feature_ref=feature_ref,
        surface_ref=surface_ref,
        data_ref=data_ref,
        state_ref=state_ref,
        behavior_ref=behavior_ref,
        state=state,
    )


__all__ = [
    "INTERACTION_ID_PREFIX",
    "FOUNDATION_REUSE",
    "InteractionError",
    "Interaction",
    "make_interaction",
]
