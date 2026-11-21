"""EC3-B12-U04 — The Universal Feature construct (AMC-04).

Realizes the meta-model concept **AMC-04 Feature** (APPLICATION-005 §2;
APPLICATION-008; APPLICATION-003 AOE-04; APPLICATION-001 §4):

    the **discrete, named unit of actor-facing capability delivered by composing one or
    more SF-2 operations under contract** — the load-bearing unit of
    experience-over-operation — a typed (ENG-004) object (ENG-002), identified (ENG-001),
    classified by one AXH-04 kind (Query / Command / Composite), that **delivers a
    capability** for the application (AMR-01, by reference), **consumes one or more SF-2
    operations under contract** (AMR-13, by reference; the defining relationship — FEA-04),
    **presents typed I/O as DF-2 data** (AMR-14, by reference; FEA-05), is **engaged
    through a typed interaction** (AMR-05, by reference; FEA-06 — the relationship no prior
    Band-12 unit used), **belongs to exactly one owning module** (AMR-03, by reference;
    FEA-07), and whose invoke/sequence/interact/emit behavior is a RUNTIME construct
    (AMR-11 / §7, by reference).

The construct is **additive over the CERTIFIED EC-1 foundation** (and the referenced,
CERTIFIED-COMPLETE Band-10 data surface + CERTIFIED-COMPLETE + FROZEN Band-11 service
surface + the CERTIFIED Band-12 U01 Universal Application root + U02 Universal Capability +
U03 Universal Module) and reuses them *by reference* (UAL-02 / AMI-05): identity and
value-fidelity are derived through the EC-1 certified deterministic encoding
(:func:`engine.certification.contracts.canonical_json` /
:func:`~engine.certification.contracts.content_hash`) — the same discipline that produces
every EC-1 runtime, artifact, and certification identity — so this module introduces
**no second identity scheme and no parallel value model**. It selects no technology/UI and
confers no authority (UAL-15).

A :class:`Feature` is *immutable* (a frozen object — ENG-002 objecthood), *typed*
(ENG-004), *identified* (ENG-001 via a deterministic id), *classified* (AXH-04 kind),
*capability-delivering* (AMR-01, by reference), *service-consuming* (AMR-13, one or more,
by reference — the defining relationship), *data-referencing* (AMR-14, by reference),
*interaction-engaged* (AMR-05, by reference), *module-owned* (AMR-03, by reference),
*behavior-bound* (AMR-11, by reference), and holds a *forward-only lifecycle state*
(AOS-01…06, UAL-12). Constructing a :class:`Feature` enforces the meta-constraints
AMK-01/02/03/04/05/07 and the laws UAL-03/04/05/06/07/08/09/10/11/12/13 fail-closed: an
ill-formed feature cannot be instantiated. It realizes **no** Application, Capability,
Module, Workflow, Interaction, State, Composition, Security, or Governance object — those
are separate Band-12 units; this construct binds them only *by reference*.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Any

from application.feature_meta import (
    ENGAGED_REQUIRED_STATES,
    FEATURE_META_CLASS,
    FEATURE_RELATIONSHIPS,
    LIFECYCLE_ORDER,
    MULTI_OPERATION_KINDS,
    READ_SIDE_KINDS,
    SUBSTRATE_REFS,
    WRITE_SIDE_KINDS,
    FeatureKind,
    FeatureState,
)

# --- EC-1 reuse by reference (UAL-02 / AMI-05) — imported, never redefined --------
from engine.certification.contracts import canonical_json, content_hash

#: The deterministic id prefix for a realized Feature (mirrors EC-1 UCOS-<KIND>-<hex16>).
FEATURE_ID_PREFIX = "UCOS-FEATURE"

#: The map of frozen-foundation primitives this construct reuses *by reference*
#: (never redefined). Recorded for the reuse-integrity check (UAL-02 / AMI-05 / VC-5).
FOUNDATION_REUSE: dict[str, str] = {
    "ENG-001": "engine.certification.contracts.content_hash (deterministic identity derivation)",
    "ENG-002": "python frozen object (immutable objecthood bearing the feature)",
    "ENG-003": "engine.certification.contracts.canonical_json (value fidelity; no parallel model)",
    "ENG-004": "application.feature_meta.FeatureKind + type_tag (ENG-004 typing, by ref)",
    "ENG-005": "reference identifiers (capability/module/interaction/operation/data refs)",
    "RL-F2": "feature-invoke/sequence/interact/emit behavior by reference (§7); none redefined",
    "SF-2": "consumed contracted operation(s) by reference (AMR-13, FEA-04); none redefined",
    "DF-2": "presented/typed-I-O data by reference (AMR-14, FEA-05); none redefined",
}

#: Concrete-technology markers forbidden by UAL-15 (no UI/framework/screen/API/protocol/vendor).
#: An abstract EL-1/RL-F2/PL-F2/DF-2/SF-2 reference names none of these.
_TECHNOLOGY_MARKERS: tuple[str, ...] = (
    "react",
    "vue",
    "angular",
    "svelte",
    "tailwind",
    "bootstrap",
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


class FeatureError(ValueError):
    """Raised when inputs cannot be realized as a well-formed :class:`Feature`.

    A :class:`Feature` is fail-closed (TRACK-001): an ill-formed feature construct is
    rejected at construction rather than admitted as an invalid feature.
    """


def _require_reference(name: str, value: Any) -> str:
    """Require ``value`` to be a non-empty ENG-005 reference string (by reference)."""
    if not isinstance(value, str) or not value.strip():
        raise FeatureError(
            f"{name} must be a non-empty ENG-005 reference (UAL-02/06/13)"
        )
    return value


@dataclass(frozen=True, slots=True)
class Feature:
    """AMC-04 — an immutable, typed, identified, capability-delivering application feature.

    Fields:
        type_tag:        the ENG-004 Type of the feature (decidable, non-empty) — UAL-03.
        kind:            the AXH-04 classification of the feature (AXC-04).
        capability_ref:  the ENG-005 reference to the Capability the feature delivers for
                         the application (AMR-01 delivers, reference-only) — FEA-04.
        operation_refs:  the ENG-005 references to the SF-2 operation(s) the feature
                         consumes under contract (AMR-13 consumes-operation, reference-only)
                         — the FEA-04 / FEA-C2 **defining relationship**: a feature delivers
                         capability only by composing one or more contracted operations.
                         Must be non-empty and a partition (distinct; FEA-C1); a
                         Composite-Feature composes ≥2 (AXH-04 / FEA-C5). Order-independent
                         for identity (canonically sorted).
        interaction_ref: the ENG-005 reference to the Interaction the feature is engaged
                         through (AMR-05 engaged-through; FEA-06 / AMK-04, by reference —
                         founding, acyclic). The relationship no prior Band-12 unit used.
        module_ref:      the ENG-005 reference to the single owning Module (AMR-03 groups;
                         FEA-07 / UAL-07, by reference — a feature belongs to exactly one).
        data_ref:        the ENG-005 reference to the DF-2 represented data the feature
                         presents as typed I/O (AMR-14 presents-data; FEA-05 / UAL-13).
        behavior_ref:    the ENG-005 reference to the RUNTIME behavior the feature binds
                         (AMR-11 behaves-as; RL-F2, by reference; invoke/sequence/interact/
                         emit) — UAL-10.
        state:           the AOS-01…06 lifecycle state (forward-only) — UAL-12 (default DEFINED).
    """

    type_tag: str
    kind: FeatureKind
    capability_ref: str
    operation_refs: tuple[str, ...]
    interaction_ref: str = "ENG-005:AMC-06:ucos.application.interaction.primary"
    module_ref: str = "ENG-005:AMC-03:ucos.application.module.foundation"
    data_ref: str = "ENG-005:DF-2:data.represented"
    behavior_ref: str = "ENG-005:RL-F2:runtime.feature-invoke"
    state: FeatureState = FeatureState.DEFINED

    #: Canonically ordered, de-duplicated view of the composed operations (identity-defining).
    _ordered_operations: tuple[str, ...] = field(init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        # AMK-01 / UAL-03 / FEA-01 — typed (ENG-004): a decidable, non-empty type tag.
        if not isinstance(self.type_tag, str) or not self.type_tag.strip():
            raise FeatureError(
                "feature must be typed with a non-empty ENG-004 type_tag (UAL-03)"
            )
        # AXH-04 / AXC-04 — classified by exactly one Feature kind.
        if not isinstance(self.kind, FeatureKind):
            raise FeatureError("feature kind must be an AXH-04 FeatureKind (AXC-04)")
        # AMR-01 / FEA-04 — delivers a capability by reference.
        _require_reference("capability_ref", self.capability_ref)
        # AMR-13 / FEA-04 / FEA-C2 / AMK-02 — composes ≥1 SF-2 operation under contract.
        if not isinstance(self.operation_refs, tuple):
            raise FeatureError(
                "operation_refs must be a tuple of ENG-005 references (AMR-13)"
            )
        if not self.operation_refs:
            raise FeatureError(
                "feature must consume at least one SF-2 operation (AMR-13 / FEA-04 / UAL-06)"
            )
        for ref in self.operation_refs:
            if not isinstance(ref, str) or not ref.strip():
                raise FeatureError(
                    "each composed operation must be a non-empty ENG-005 reference (AMR-13)"
                )
        # FEA-C1 — composed operations are a partition (distinct; declaration is decidable).
        if len(set(self.operation_refs)) != len(self.operation_refs):
            raise FeatureError(
                "composed operations must be distinct (FEA-C1 declaration completeness)"
            )
        # AXH-04 / FEA-C5 — a Composite-Feature composes more than one operation.
        if self.kind in MULTI_OPERATION_KINDS and len(self.operation_refs) < 2:
            raise FeatureError(
                "a Composite-Feature must compose ≥2 SF-2 operations (AXH-04 / FEA-C5)"
            )
        # AMR-05 / FEA-06 / AMK-04 — engaged through a typed interaction by reference.
        _require_reference("interaction_ref", self.interaction_ref)
        # AMR-03 / FEA-07 / UAL-07 — belongs to exactly one owning module by reference.
        _require_reference("module_ref", self.module_ref)
        # AMR-14 / FEA-05 / UAL-13 — presents DF-2 data (typed I/O) by reference.
        _require_reference("data_ref", self.data_ref)
        # AMR-11 / UAL-10 — behavior bound to RL-F2 by reference.
        _require_reference("behavior_ref", self.behavior_ref)
        # V5 / UAL-12 — a valid lifecycle state.
        if not isinstance(self.state, FeatureState):
            raise FeatureError("feature state must be an AOS-01…06 FeatureState (UAL-12)")
        # FEA-C3 / AMK-03 — founding relations (groups, engaged-through) form a DAG: a
        # feature cannot compose, be engaged-through, or be owned-by its own delivered
        # capability, its owning module, or its engaging interaction (no self-founding /
        # non-absorption guard).
        founding_refs = {self.module_ref, self.interaction_ref}
        if founding_refs & set(self.operation_refs):
            raise FeatureError(
                "a feature cannot compose its owning module or engaging interaction as an "
                "operation (FEA-C3 / AMK-03 founding acyclicity)"
            )
        if self.capability_ref in self.operation_refs:
            raise FeatureError(
                "a feature cannot compose its delivered capability as an operation "
                "(FEA-C3 / non-absorption)"
            )
        # AMK-04 / FEA-06 / FEA-K3 (engaged before EXECUTABLE) is guaranteed by construction:
        # ``interaction_ref`` is a mandatory declaration element (AMK-02), enforced above by
        # ``_require_reference``, so every feature is engaged in every lifecycle state. The
        # constraint is materially evaluated at the validation layer (the
        # ``feature-engaged-through-interaction`` and ``feature-engaged-before-executable``
        # checks) and re-asserted fail-closed at the EXECUTABLE lifecycle boundary in
        # :meth:`transition`.
        object.__setattr__(
            self, "_ordered_operations", tuple(sorted(self.operation_refs))
        )

    # -- identity (ENG-001) borne by object (ENG-002), by reference ------------

    def canonical_core(self) -> dict[str, Any]:
        """The canonical, hashable core of the feature (its identity-defining tuple).

        The composed operations are a set (a partition), so they are canonically sorted —
        two features composing the same operations in different declaration order bear the
        same ENG-001 identity.
        """
        return {
            "meta_class": FEATURE_META_CLASS,
            "type_tag": self.type_tag,
            "kind": self.kind.value,
            "capability_ref": self.capability_ref,
            "operation_refs": list(self._ordered_operations),
            "interaction_ref": self.interaction_ref,
            "module_ref": self.module_ref,
            "data_ref": self.data_ref,
            "behavior_ref": self.behavior_ref,
        }

    @property
    def value_digest(self) -> str:
        """The EC-1 content hash of the feature core — the ENG-003 value fingerprint."""
        return content_hash(self.canonical_core())

    @property
    def feature_id(self) -> str:
        """The deterministic ENG-001 identity of the feature (borne by this object).

        Derived through the CERTIFIED EC-1 ``content_hash`` (UAL-04 — no second identity
        scheme): identical (type, kind, refs) always yields the identical id, so identity
        is reproducible and byte-stable (determinism, VC-4).
        """
        return f"{FEATURE_ID_PREFIX}-{self.type_tag}-{self.value_digest[:16]}"

    # -- meta-model participation (APPLICATION-005/008) ------------------------

    @property
    def meta_class(self) -> str:
        """V1 — the single meta-class this construct instantiates (AMC-04)."""
        return FEATURE_META_CLASS

    def meta_relationships(self) -> tuple[str, ...]:
        """V2 — the AMR-01…14 relationships the feature participates in."""
        return FEATURE_RELATIONSHIPS

    def is_founding_acyclic(self) -> bool:
        """V4 / AMK-03 / FEA-C3 — the founding graph (groups, engaged-through) is acyclic.

        A Feature binds its constituents *by reference* (string ids), so its founding
        structure carries no cycle; this is proven by the fact that its core canonically
        encodes (a cycle would raise at construction).
        """
        try:
            canonical_json(self.canonical_core())
        except (TypeError, ValueError):  # pragma: no cover - blocked at construction
            return False
        return True

    def references_resolve(self) -> bool:
        """AOI-03 / AMK-05/07 — every ENG-005 reference is a non-empty resolvable id."""
        base = all(
            isinstance(r, str) and bool(r.strip())
            for r in (
                self.capability_ref,
                self.interaction_ref,
                self.module_ref,
                self.data_ref,
                self.behavior_ref,
            )
        )
        ops = all(isinstance(r, str) and bool(r.strip()) for r in self.operation_refs)
        return base and ops

    def delivers_capability(self) -> bool:
        """AMR-01 / FEA-04 — the feature delivers a capability by reference."""
        return bool(self.capability_ref.strip())

    def consumes_operations(self) -> bool:
        """AMR-13 / FEA-04 / FEA-C2 — the feature composes ≥1 SF-2 operation by reference."""
        return len(self.operation_refs) >= 1

    def composed_operation_count(self) -> int:
        """The number of SF-2 operations the feature composes (its delivery breadth)."""
        return len(self.operation_refs)

    def presents_data(self) -> bool:
        """AMR-14 / FEA-05 / UAL-13 — the feature presents DF-2 data by reference."""
        return bool(self.data_ref.strip())

    def is_engaged(self) -> bool:
        """AMR-05 / FEA-06 / AMK-04 — the feature is engaged through an interaction by ref."""
        return bool(self.interaction_ref.strip())

    def is_owned(self) -> bool:
        """AMR-03 / FEA-07 / UAL-07 — the feature belongs to exactly one owning module."""
        return bool(self.module_ref.strip())

    def operations_are_partition(self) -> bool:
        """FEA-C1 — the composed operations are distinct (a partition)."""
        return len(set(self.operation_refs)) == len(self.operation_refs) and all(
            r.strip() for r in self.operation_refs
        )

    def declaration_complete(self) -> bool:
        """FEA-C1 / AMK-02 / UAL-08 — the feature's declaration is complete.

        Complete iff delivered capability, composed operations, typed I/O (presented data),
        and interaction are all explicit — the governing declaration obligation of AMC-04.
        """
        return (
            bool(self.type_tag.strip())
            and self.delivers_capability()
            and self.consumes_operations()
            and self.operations_are_partition()
            and self.presents_data()
            and self.is_engaged()
            and self.is_owned()
        )

    def delivery_side(self) -> str:
        """FEA-C5 / AXH-04 — the read-side / write-side classification of delivery.

        Query features compose read-side operations (no represented state change), Command
        features compose write-side operations (intended state change), and Composite
        features compose multiple operations toward one delivered capability.
        """
        if self.kind in READ_SIDE_KINDS:
            return "read-side"
        if self.kind in WRITE_SIDE_KINDS:
            return "write-side"
        return "composite"

    def delivery_side_is_consistent(self) -> bool:
        """FEA-C5 / AXH-04 — the kind and composed-operation breadth are consistent.

        A Composite-Feature must compose ≥2 operations; Query/Command features compose ≥1.
        (Read/write-side semantics are declared per kind and carried into delivery_side.)
        """
        if self.kind in MULTI_OPERATION_KINDS:
            return self.composed_operation_count() >= 2
        return self.composed_operation_count() >= 1

    def engaged_before_executable(self) -> bool:
        """AMK-04 / FEA-06 / FEA-K3 — engaged-through holds for the current lifecycle state.

        For states at or past EXECUTABLE the feature must be engaged through an interaction;
        for earlier states engagement is declared but not yet gate-required.
        """
        if self.state in ENGAGED_REQUIRED_STATES:
            return self.is_engaged()
        return True

    def owns_operation(self, operation_ref: str) -> bool:
        """AMR-13 — True iff ``operation_ref`` is composed by this feature."""
        return operation_ref in self.operation_refs

    # -- non-constitutiveness (UAL-15) -----------------------------------------

    def confers_authority(self) -> bool:
        """UAL-15 / FEA-09 / C7 — a feature confers no authority (structurally has none)."""
        return False

    def selects_technology(self) -> bool:
        """UAL-15 / FEA-09 / C7 — True iff the feature names a concrete technology/UI/vendor."""
        haystack = canonical_json(self.canonical_core()).lower()
        return any(marker in haystack for marker in _TECHNOLOGY_MARKERS)

    def embeds_secret(self) -> bool:
        """UAL-15 / RR-07 / C7 — True iff the feature appears to embed a secret."""
        haystack = canonical_json(self.canonical_core()).lower()
        return any(marker in haystack for marker in _SECRET_MARKERS)

    def redefines_foundation(self) -> bool:
        """UAL-02 / AMI-05 / VC-5 — a feature redefines no frozen primitive (reuse-only)."""
        return False

    # -- lifecycle (UAL-12, forward-only) --------------------------------------

    def transition(self, to_state: FeatureState) -> Feature:
        """Return a new feature advanced to ``to_state`` (forward-only; UAL-12).

        The transition additionally enforces AMK-04 / FEA-06: a feature may reach EXECUTABLE
        (or beyond) only when it is engaged through an interaction.

        Raises:
            FeatureError: on a backward transition or an un-engaged EXECUTABLE transition.
        """
        if not isinstance(to_state, FeatureState):
            raise FeatureError("target state must be an AOS-01…06 FeatureState (UAL-12)")
        here = LIFECYCLE_ORDER.index(self.state)
        there = LIFECYCLE_ORDER.index(to_state)
        if there < here:
            raise FeatureError(
                f"lifecycle is forward-only (UAL-12): "
                f"{self.state.value} → {to_state.value} is backward"
            )
        if to_state in ENGAGED_REQUIRED_STATES and not self.is_engaged():  # pragma: no cover
            # Defense-in-depth (AMK-04 / FEA-06): unreachable because interaction_ref is a
            # mandatory declaration element (AMK-02), so a feature is always engaged; the
            # gate is retained fail-closed at the EXECUTABLE lifecycle boundary.
            raise FeatureError(
                f"feature must be engaged through an interaction before {to_state.value} "
                f"(AMK-04 / FEA-06)"
            )
        return replace(self, state=to_state)

    # -- serialization ----------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """A deterministic, serializable projection of the feature."""
        return {
            "feature_id": self.feature_id,
            "meta_class": self.meta_class,
            "type_tag": self.type_tag,
            "kind": self.kind.value,
            "capability_ref": self.capability_ref,
            "operation_refs": list(self._ordered_operations),
            "composed_operation_count": self.composed_operation_count(),
            "interaction_ref": self.interaction_ref,
            "module_ref": self.module_ref,
            "data_ref": self.data_ref,
            "behavior_ref": self.behavior_ref,
            "value_digest": self.value_digest,
            "state": self.state.value,
            "delivery_side": self.delivery_side(),
            "declaration_complete": self.declaration_complete(),
            "engaged": self.is_engaged(),
            "relationships": list(self.meta_relationships()),
            "substrate_refs": list(SUBSTRATE_REFS),
        }


def make_feature(
    type_tag: str,
    capability_ref: str,
    operation_refs: tuple[str, ...],
    *,
    kind: FeatureKind = FeatureKind.QUERY,
    interaction_ref: str = "ENG-005:AMC-06:ucos.application.interaction.primary",
    module_ref: str = "ENG-005:AMC-03:ucos.application.module.foundation",
    data_ref: str = "ENG-005:DF-2:data.represented",
    behavior_ref: str = "ENG-005:RL-F2:runtime.feature-invoke",
    state: FeatureState = FeatureState.DEFINED,
) -> Feature:
    """Construct a well-formed :class:`Feature` (fail-closed factory)."""
    return Feature(
        type_tag=type_tag,
        kind=kind,
        capability_ref=capability_ref,
        operation_refs=tuple(operation_refs),
        interaction_ref=interaction_ref,
        module_ref=module_ref,
        data_ref=data_ref,
        behavior_ref=behavior_ref,
        state=state,
    )


__all__ = [
    "FEATURE_ID_PREFIX",
    "FOUNDATION_REUSE",
    "FeatureError",
    "Feature",
    "make_feature",
]
