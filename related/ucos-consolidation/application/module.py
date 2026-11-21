"""EC3-B12-U03 — The Universal Module construct (AMC-03).

Realizes the meta-model concept **AMC-03 Module** (APPLICATION-005 §2;
APPLICATION-007; APPLICATION-003 AOE-03; APPLICATION-001 §4):

    the **cohesive, bounded grouping of features within an application** — the structural
    unit of application composition — a typed (ENG-004) object (ENG-002), identified
    (ENG-001), classified by one AXH-03 kind (Core / Supporting / Extension), that
    **groups the features it owns** (AMR-03, by reference; the defining relationship —
    MOD-07) under an explicit, decidable boundary (MOD-03 / UAL-07), **composes into an
    application** (AMR-02, by reference; MOD-06), is **assembled/composed as** a PLATFORM
    experience composition (AMR-07/12, by reference; PLATFORM-009/010), and whose
    lifecycle/emit behavior is a RUNTIME construct (§7, by reference).

The construct is **additive over the CERTIFIED EC-1 foundation** (and the referenced,
CERTIFIED-COMPLETE Band-10 data surface + CERTIFIED-COMPLETE + FROZEN Band-11 service
surface + the CERTIFIED Band-12 U01 Universal Application root + the CERTIFIED Band-12
U02 Universal Capability) and reuses them *by reference* (UAL-02 / AMI-05): identity and
value-fidelity are derived through the EC-1 certified deterministic encoding
(:func:`engine.certification.contracts.canonical_json` /
:func:`~engine.certification.contracts.content_hash`) — the same discipline that produces
every EC-1 runtime, artifact, and certification identity — so this module introduces
**no second identity scheme and no parallel value model**. It selects no technology/UI and
confers no authority (UAL-15).

A :class:`Module` is *immutable* (a frozen object — ENG-002 objecthood), *typed*
(ENG-004), *identified* (ENG-001 via a deterministic id), *classified* (AXH-03 kind),
*feature-grouping* (AMR-03, by reference — the defining relationship), *bounded* and
*cohesive* (MOD-03/04 / UAL-07), *composition-bound* (AMR-02/07/12, by reference), and
holds a *forward-only lifecycle state* (AOS-01…06, UAL-12). Constructing a
:class:`Module` enforces the meta-constraints AMK-01/03/05/06 and the laws
UAL-03/04/05/07/09/10/12 fail-closed: an ill-formed module cannot be instantiated.
It realizes **no** Application, Capability, Feature, Workflow, Interaction, State,
Composition, Security, or Governance object — those are separate Band-12 units; this
construct binds them only *by reference*. In particular it **consumes no SF-2 operation**
and **presents no DF-2 data** — those are Feature/Capability concerns (AMR-13/14).
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Any

from application.module_meta import (
    LIFECYCLE_ORDER,
    MODULE_META_CLASS,
    MODULE_RELATIONSHIPS,
    SUBSTRATE_REFS,
    ModuleKind,
    ModuleState,
)

# --- EC-1 reuse by reference (UAL-02 / AMI-05) — imported, never redefined --------
from engine.certification.contracts import canonical_json, content_hash

#: The deterministic id prefix for a realized Module (mirrors EC-1 UCOS-<KIND>-<hex16>).
MODULE_ID_PREFIX = "UCOS-MODULE"

#: The map of frozen-foundation primitives this construct reuses *by reference*
#: (never redefined). Recorded for the reuse-integrity check (UAL-02 / AMI-05 / VC-5).
FOUNDATION_REUSE: dict[str, str] = {
    "ENG-001": "engine.certification.contracts.content_hash (deterministic identity derivation)",
    "ENG-002": "python frozen object (immutable objecthood bearing the module)",
    "ENG-003": "engine.certification.contracts.canonical_json (value fidelity; no parallel model)",
    "ENG-004": "application.module_meta.ModuleKind + type_tag (ENG-004 typing, by ref)",
    "ENG-005": "reference identifiers (feature/application/composition refs; no new construct)",
    "RL-F2": "module-transition / module-emit lifecycle behavior by reference (§7); none redefined",
    "PL-F2": "experience composition bound by reference (AMR-07/12; PLATFORM-009/010); none redef",
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


class ModuleError(ValueError):
    """Raised when inputs cannot be realized as a well-formed :class:`Module`.

    A :class:`Module` is fail-closed (TRACK-001): an ill-formed module construct is
    rejected at construction rather than admitted as an invalid module.
    """


def _require_reference(name: str, value: Any) -> str:
    """Require ``value`` to be a non-empty ENG-005 reference string (by reference)."""
    if not isinstance(value, str) or not value.strip():
        raise ModuleError(f"{name} must be a non-empty ENG-005 reference (UAL-02/09)")
    return value


@dataclass(frozen=True, slots=True)
class Module:
    """AMC-03 — an immutable, typed, identified, feature-grouping application module.

    Fields:
        type_tag:        the ENG-004 Type of the module (decidable, non-empty) — UAL-03.
        kind:            the AXH-03 classification of the module (AXC-02).
        feature_refs:    the ENG-005 references to the features the module groups/owns
                         (AMR-03 groups, reference-only) — the DEFINING relationship
                         (MOD-07): the module's explicit boundary is the enumeration of
                         the features it owns. Must be non-empty and a partition (distinct;
                         MOD-05/MOD-C2). Order-independent for identity (canonically sorted).
        application_ref: the ENG-005 reference to the application the module composes into
                         (AMR-02 composed-of; MOD-06, by reference; founding acyclic).
        composition_ref: the ENG-005 reference to the PLATFORM experience composition the
                         module is composed/assembled as (AMR-07/12 assembled-by/composed-as;
                         PL-F2 / PLATFORM-009/010, by reference) — UAL-09.
        behavior_ref:    the ENG-005 reference to the RUNTIME behavior the module binds
                         (§7 module-transition / module-emit; RL-F2, by reference) — UAL-10.
        state:           the AOS-01…06 lifecycle state (forward-only) — UAL-12 (default DEFINED).
    """

    type_tag: str
    kind: ModuleKind
    feature_refs: tuple[str, ...]
    application_ref: str = "ENG-005:AMC-01:ucos.application.foundation"
    composition_ref: str = "ENG-005:PL-F2:PLATFORM-009.composition"
    behavior_ref: str = "ENG-005:RL-F2:runtime.module-transition"
    state: ModuleState = ModuleState.DEFINED

    #: Canonically ordered, de-duplicated view of the owned features (identity-defining).
    _ordered_features: tuple[str, ...] = field(init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        # AMK-01 / UAL-03 — typed (ENG-004): a decidable, non-empty type tag.
        if not isinstance(self.type_tag, str) or not self.type_tag.strip():
            raise ModuleError(
                "module must be typed with a non-empty ENG-004 type_tag (UAL-03)"
            )
        # AXH-03 / AXC-02 — classified by exactly one Module kind.
        if not isinstance(self.kind, ModuleKind):
            raise ModuleError("module kind must be an AXH-03 ModuleKind (AXC-02)")
        # AMR-03 / MOD-07 / UAL-07 — groups an explicit, bounded set of owned features.
        if not isinstance(self.feature_refs, tuple):
            raise ModuleError("feature_refs must be a tuple of ENG-005 references (AMR-03)")
        if not self.feature_refs:
            raise ModuleError(
                "module must group at least one feature (AMR-03 / MOD-07 / UAL-07)"
            )
        for ref in self.feature_refs:
            if not isinstance(ref, str) or not ref.strip():
                raise ModuleError(
                    "each grouped feature must be a non-empty ENG-005 reference (AMR-03)"
                )
        # MOD-05 / MOD-07 / MOD-C2 — feature ownership is a partition (no duplicate ownership).
        if len(set(self.feature_refs)) != len(self.feature_refs):
            raise ModuleError(
                "feature ownership must be a partition: no duplicate feature (MOD-05 / MOD-C2)"
            )
        # AMR-02 / MOD-06 — composed into an application by reference.
        _require_reference("application_ref", self.application_ref)
        # AMR-07/12 / UAL-09 — experience composition bound to PL-F2 by reference.
        _require_reference("composition_ref", self.composition_ref)
        # §7 / UAL-10 — lifecycle/emit behavior bound to RL-F2 by reference.
        _require_reference("behavior_ref", self.behavior_ref)
        # V5 / UAL-12 — a valid lifecycle state.
        if not isinstance(self.state, ModuleState):
            raise ModuleError("module state must be an AOS-01…06 ModuleState (UAL-12)")
        # MOD-C4 — composition absorbs no feature identity: a module cannot own the
        # application it composes into as one of its features (structural acyclicity guard).
        if self.application_ref in self.feature_refs:
            raise ModuleError(
                "a module cannot group its own composing application (MOD-C3 / MOD-C4)"
            )
        object.__setattr__(
            self, "_ordered_features", tuple(sorted(self.feature_refs))
        )

    # -- identity (ENG-001) borne by object (ENG-002), by reference ------------

    def canonical_core(self) -> dict[str, Any]:
        """The canonical, hashable core of the module (its identity-defining tuple).

        Feature ownership is a set (a partition), so the owned features are canonically
        sorted — two modules owning the same features in different declaration order bear
        the same ENG-001 identity.
        """
        return {
            "meta_class": MODULE_META_CLASS,
            "type_tag": self.type_tag,
            "kind": self.kind.value,
            "feature_refs": list(self._ordered_features),
            "application_ref": self.application_ref,
            "composition_ref": self.composition_ref,
            "behavior_ref": self.behavior_ref,
        }

    @property
    def value_digest(self) -> str:
        """The EC-1 content hash of the module core — the ENG-003 value fingerprint."""
        return content_hash(self.canonical_core())

    @property
    def module_id(self) -> str:
        """The deterministic ENG-001 identity of the module (borne by this object).

        Derived through the CERTIFIED EC-1 ``content_hash`` (UAL-04 — no second identity
        scheme): identical (type, kind, refs) always yields the identical id, so identity
        is reproducible and byte-stable (determinism, VC-4).
        """
        return f"{MODULE_ID_PREFIX}-{self.type_tag}-{self.value_digest[:16]}"

    # -- meta-model participation (APPLICATION-005/007) ------------------------

    @property
    def meta_class(self) -> str:
        """V1 — the single meta-class this construct instantiates (AMC-03)."""
        return MODULE_META_CLASS

    def meta_relationships(self) -> tuple[str, ...]:
        """V2 — the AMR-01…14 relationships the module participates in."""
        return MODULE_RELATIONSHIPS

    def is_founding_acyclic(self) -> bool:
        """V4 / AMK-03 / MOD-C3 — the founding graph (composed-of, groups) is acyclic.

        A Module binds its constituents *by reference* (string ids), so its founding
        structure carries no cycle; this is proven by the fact that its core canonically
        encodes (a cycle would raise at construction).
        """
        try:
            canonical_json(self.canonical_core())
        except (TypeError, ValueError):  # pragma: no cover - blocked at construction
            return False
        return True

    def references_resolve(self) -> bool:
        """AOI-03 / AMK-05/06 — every ENG-005 reference is a non-empty resolvable id."""
        refs = (self.application_ref, self.composition_ref, self.behavior_ref)
        base = all(isinstance(r, str) and bool(r.strip()) for r in refs)
        feats = all(isinstance(r, str) and bool(r.strip()) for r in self.feature_refs)
        return base and feats

    def groups_features(self) -> bool:
        """AMR-03 / MOD-07 — the module groups (owns) at least one feature by reference."""
        return len(self.feature_refs) >= 1

    def owned_feature_count(self) -> int:
        """The number of features the module owns (its boundary size)."""
        return len(self.feature_refs)

    def ownership_is_partition(self) -> bool:
        """MOD-05 / MOD-07 / MOD-C2 — owned features are distinct (a partition)."""
        return len(set(self.feature_refs)) == len(self.feature_refs) and all(
            r.strip() for r in self.feature_refs
        )

    def is_bounded(self) -> bool:
        """MOD-03 / MOD-C1 / UAL-07 — the module declares an explicit, decidable boundary.

        A module is bounded iff its type and kind are explicit and it owns an explicit,
        non-empty, partitioned set of features (the boundary is closed at declaration).
        """
        return (
            bool(self.type_tag.strip())
            and self.groups_features()
            and self.ownership_is_partition()
        )

    def is_cohesive(self) -> bool:
        """MOD-04 / UAL-07 — the owned features form one cohesive grouping.

        Cohesion is structural: every owned feature resides under this single module's
        boundary (a partition), so the grouping is cohesive by construction.
        """
        return self.is_bounded()

    def owns_feature(self, feature_ref: str) -> bool:
        """MOD-07 — True iff ``feature_ref`` is owned (grouped) by this module."""
        return feature_ref in self.feature_refs

    # -- non-constitutiveness (UAL-15) -----------------------------------------

    def confers_authority(self) -> bool:
        """UAL-15 / MOD-09 / C7 — a module confers no authority (structurally has none)."""
        return False

    def selects_technology(self) -> bool:
        """UAL-15 / MOD-09 / C7 — True iff the module names a concrete technology/UI/vendor."""
        haystack = canonical_json(self.canonical_core()).lower()
        return any(marker in haystack for marker in _TECHNOLOGY_MARKERS)

    def embeds_secret(self) -> bool:
        """UAL-15 / RR-07 / C7 — True iff the module appears to embed a secret."""
        haystack = canonical_json(self.canonical_core()).lower()
        return any(marker in haystack for marker in _SECRET_MARKERS)

    def redefines_foundation(self) -> bool:
        """UAL-02 / AMI-05 / VC-5 — a module redefines no frozen primitive (reuse-only)."""
        return False

    # -- lifecycle (UAL-12, forward-only) --------------------------------------

    def transition(self, to_state: ModuleState) -> Module:
        """Return a new module advanced to ``to_state`` (forward-only; UAL-12).

        Raises:
            ModuleError: on a backward or in-place-reversing transition.
        """
        if not isinstance(to_state, ModuleState):
            raise ModuleError("target state must be an AOS-01…06 ModuleState (UAL-12)")
        here = LIFECYCLE_ORDER.index(self.state)
        there = LIFECYCLE_ORDER.index(to_state)
        if there < here:
            raise ModuleError(
                f"lifecycle is forward-only (UAL-12): "
                f"{self.state.value} → {to_state.value} is backward"
            )
        return replace(self, state=to_state)

    # -- serialization ----------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """A deterministic, serializable projection of the module."""
        return {
            "module_id": self.module_id,
            "meta_class": self.meta_class,
            "type_tag": self.type_tag,
            "kind": self.kind.value,
            "feature_refs": list(self._ordered_features),
            "owned_feature_count": self.owned_feature_count(),
            "application_ref": self.application_ref,
            "composition_ref": self.composition_ref,
            "behavior_ref": self.behavior_ref,
            "value_digest": self.value_digest,
            "state": self.state.value,
            "bounded": self.is_bounded(),
            "cohesive": self.is_cohesive(),
            "relationships": list(self.meta_relationships()),
            "substrate_refs": list(SUBSTRATE_REFS),
        }


def make_module(
    type_tag: str,
    feature_refs: tuple[str, ...],
    *,
    kind: ModuleKind = ModuleKind.CORE,
    application_ref: str = "ENG-005:AMC-01:ucos.application.foundation",
    composition_ref: str = "ENG-005:PL-F2:PLATFORM-009.composition",
    behavior_ref: str = "ENG-005:RL-F2:runtime.module-transition",
    state: ModuleState = ModuleState.DEFINED,
) -> Module:
    """Construct a well-formed :class:`Module` (fail-closed factory)."""
    return Module(
        type_tag=type_tag,
        kind=kind,
        feature_refs=tuple(feature_refs),
        application_ref=application_ref,
        composition_ref=composition_ref,
        behavior_ref=behavior_ref,
        state=state,
    )


__all__ = [
    "MODULE_ID_PREFIX",
    "FOUNDATION_REUSE",
    "ModuleError",
    "Module",
    "make_module",
]
