"""EC3-B13-U10 — The Universal Infrastructure Integration construct (InfrastructureDependency).

Realizes the **one** remaining leaf meta-class of the frozen UIMM (INFRASTRUCTURE-005 §2):
**InfrastructureDependency** ``«⊑ ENG-005 reference, by ref»`` — *the typed, identified,
downward-only, non-mutating reference by which one already-CERTIFIED infrastructure concern
depends on another*.

An InfrastructureDependency is the integration primitive. It carries the mandatory bespoke
meta-attribute ``downwardOnly = true`` (invariant; INFRASTRUCTURE-005 §3) and is realized
through the ``dependsOn`` meta-relationship (``InfrastructureConstruct → InfrastructureConstruct``,
downward-only, acyclic — INFRASTRUCTURE-005 §4 / WF-3). It **composes** the nine certified
concerns (EC3-B13-U01…U09) *by reference* (UIL-02): it names a ``source`` and a ``target``
concern by ENG-005 reference and records the frozen meta-relationship (``basis``) that
grounds the edge. It **re-implements no concern, mutates nothing it references, mints no new
primitive/authority/registry/identifier/lifecycle (WF-11), confers no authority, embeds no
secret, and selects no technology (UIL-15)**.

Constructing a dependency enforces its well-formedness rules and laws fail-closed: an edge
that is not downward-only, not typed, or not reference-resolvable is rejected at construction
rather than admitted as invalid (TRACK-001).
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any

# --- EC-1 reuse by reference (UIL-02) ---
from engine.certification.contracts import canonical_json, content_hash

# --- Band-13 shared primitives reused by reference (UIL-02) ---
from infrastructure.capability import (
    _SECRET_MARKERS,
    _TECHNOLOGY_MARKERS,
    InfrastructureError,
    _require_reference,
)
from infrastructure.integration_meta import (
    CONSTRUCT_RELATIONSHIPS,
    DEPENDENCY_BASES,
    DEPENDENCY_META_CLASS,
    INFRA_DEPENDENCY_ID_FAMILY,
    INFRA_DEPENDENCY_ID_PREFIX,
    SUBSTRATE_REFS,
    InfrastructureState,
)

#: The sole admitted meta-relationship an InfrastructureDependency realizes (§4).
DEPENDS_ON = "dependsOn"

#: The admitted grounding-basis vocabulary (frozen §4 meta-relationships that ground an edge).
_ADMITTED_BASES = frozenset(DEPENDENCY_BASES)


def _selects_technology(core: dict[str, Any]) -> bool:
    """UIL-15 — True iff the construct core names a concrete technology/vendor."""
    haystack = canonical_json(core).lower()
    return any(marker in haystack for marker in _TECHNOLOGY_MARKERS)


def _embeds_secret(core: dict[str, Any]) -> bool:
    """UIL-15 — True iff the construct core appears to embed a secret."""
    haystack = canonical_json(core).lower()
    return any(marker in haystack for marker in _SECRET_MARKERS)


# ===========================================================================
# InfrastructureDependency meta-class construct
# ===========================================================================


@dataclass(frozen=True, slots=True)
class InfrastructureDependency:
    """InfrastructureDependency — a typed, identified, downward-only, non-mutating reference.

    A single leaf meta-class (INFRASTRUCTURE-005 §2) that composes two already-certified
    infrastructure concerns by reference. It records a ``source`` that ``dependsOn`` a
    ``target`` (both ENG-005 references), grounded by a frozen §4 meta-relationship
    (``basis``). It mints no new primitive, mutates neither endpoint, confers no authority,
    embeds no secret, and selects no technology (WF-11 / UIL-15).

    Fields:
        type_tag:       the ENG-004 Type of the dependency (decidable, non-empty) — UIL-03.
        source_ref:     ENG-005 reference to the depending (higher-founded) concern.
        target_ref:     ENG-005 reference to the depended-upon (lower-founded) concern.
        source_index:   the source concern's founding index (INFRASTRUCTURE-018 order).
        target_index:   the target concern's founding index (must be < source_index).
        basis:          the frozen §4 meta-relationship grounding the edge (reuses/contains/
                        provisions/arranges/sustains/scales/evaluates).
        downward_only:  INFRASTRUCTURE-005 §3 — must be True (invariant).
        relationship:   the realized meta-relationship — always ``dependsOn`` (§4).
        state:          the forward-only lifecycle state (INFRASTRUCTURE-003 §3).
    """

    META_CLASS = DEPENDENCY_META_CLASS
    ID_PREFIX = INFRA_DEPENDENCY_ID_PREFIX

    type_tag: str
    source_ref: str
    target_ref: str
    source_index: int
    target_index: int
    basis: str
    downward_only: bool = True
    relationship: str = DEPENDS_ON
    state: InfrastructureState = InfrastructureState.DEFINED

    def __post_init__(self) -> None:
        # UIL-03 — typed (ENG-004): a decidable, non-empty type tag.
        if not isinstance(self.type_tag, str) or not self.type_tag.strip():
            raise InfrastructureError(
                "dependency must be typed with a non-empty ENG-004 type_tag (UIL-03)"
            )
        # UIL-04/05/09 — source and target are non-empty ENG-005 references.
        _require_reference("dependency source", self.source_ref)
        _require_reference("dependency target", self.target_ref)
        # UIL-09 / §4 — a dependency IS a dependsOn reference; no other relationship admitted.
        if self.relationship != DEPENDS_ON:
            raise InfrastructureError(
                f"dependency relationship must be '{DEPENDS_ON}' (INFRASTRUCTURE-005 §4)"
            )
        # §4 — the edge is grounded by exactly one admitted frozen meta-relationship.
        if self.basis not in _ADMITTED_BASES:
            admitted = tuple(sorted(_ADMITTED_BASES))
            raise InfrastructureError(
                f"dependency basis '{self.basis}' not in the admitted set {admitted} (§4)"
            )
        # INFRASTRUCTURE-005 §3 — downwardOnly is a fixed-true invariant (fail-closed).
        if self.downward_only is not True:
            raise InfrastructureError(
                "dependency must be downwardOnly=true (INFRASTRUCTURE-005 §3, invariant)"
            )
        # WF-3 — a dependsOn edge must point strictly downward (no self-edge, no upward edge).
        if not (isinstance(self.source_index, int) and isinstance(self.target_index, int)):
            raise InfrastructureError("dependency endpoints must carry integer founding indices")
        if self.source_index <= self.target_index:
            raise InfrastructureError(
                f"dependsOn must be downward-only: {self.source_ref} (#{self.source_index}) → "
                f"{self.target_ref} (#{self.target_index}) is not strictly downward (WF-3)"
            )
        if self.source_ref == self.target_ref:
            raise InfrastructureError("dependsOn must not be a self-edge (WF-3 acyclic)")
        # INFRASTRUCTURE-003 §3 — a valid forward-only lifecycle state.
        if not isinstance(self.state, InfrastructureState):
            raise InfrastructureError(
                "dependency state must be an InfrastructureState (INFRASTRUCTURE-003 §3)"
            )

    # -- identity (ENG-001) borne by object (ENG-002) ---

    def canonical_core(self) -> dict[str, Any]:
        return {
            "meta_class": self.META_CLASS,
            "type_tag": self.type_tag,
            "source_ref": self.source_ref,
            "target_ref": self.target_ref,
            "relationship": self.relationship,
            "basis": self.basis,
            "downward_only": self.downward_only,
        }

    @property
    def value_digest(self) -> str:
        return content_hash(self.canonical_core())

    @property
    def construct_id(self) -> str:
        return f"{self.ID_PREFIX}-{self.type_tag}-{self.value_digest[:16]}"

    # -- meta-model participation ---

    @property
    def meta_class(self) -> str:
        return self.META_CLASS

    def meta_relationships(self) -> tuple[str, ...]:
        return CONSTRUCT_RELATIONSHIPS.get(self.META_CLASS, ())

    def is_hosting_structure(self) -> bool:
        return False

    def is_resource(self) -> bool:
        return False

    def is_evaluative_facet(self) -> bool:
        return False

    def is_dependency(self) -> bool:
        return self.relationship == DEPENDS_ON

    def is_downward_only(self) -> bool:
        """INFRASTRUCTURE-005 §3 / WF-3 — the invariant holds and the edge points downward."""
        return self.downward_only is True and self.source_index > self.target_index

    def is_founding_acyclic(self) -> bool:
        """WF-3 — a strictly-downward dependsOn edge introduces no founding cycle."""
        try:
            canonical_json(self.canonical_core())
        except (TypeError, ValueError):  # pragma: no cover - blocked at construction
            return False
        return self.source_index > self.target_index and self.source_ref != self.target_ref

    def references_resolve(self) -> bool:
        return all(
            isinstance(ref, str) and bool(ref.strip())
            for ref in (self.source_ref, self.target_ref)
        )

    def is_reference_only(self) -> bool:
        """UIL-02 — a dependency only references its endpoints; it mutates neither (§4)."""
        return True

    def declares_mandatory_attributes(self) -> bool:
        return (
            bool(self.type_tag.strip())
            and bool(self.value_digest)
            and bool(self.construct_id)
            and bool(self.source_ref.strip())
            and bool(self.target_ref.strip())
            and self.downward_only is True
            and self.relationship == DEPENDS_ON
        )

    # -- non-constitutiveness (UIL-15 / WF-11/12) ---

    def confers_authority(self) -> bool:
        return False

    def mutates_endpoints(self) -> bool:
        """UIL-02 / §4 — a dependency reference never mutates the constructs it references."""
        return False

    def selects_technology(self) -> bool:
        return _selects_technology(self.canonical_core())

    def embeds_secret(self) -> bool:
        return _embeds_secret(self.canonical_core())

    def redefines_foundation(self) -> bool:
        return False

    def projects_completion(self) -> bool:
        return False

    def is_new_primitive(self) -> bool:
        # A dependency ⊑ ENG-005 reference — a specialization, not a new primitive (WF-11).
        return False

    # -- lifecycle (forward-only) ---

    def transition(self, to_state: InfrastructureState) -> InfrastructureDependency:
        from infrastructure.integration_meta import LIFECYCLE_ORDER

        if not isinstance(to_state, InfrastructureState):
            raise InfrastructureError(
                "target state must be an InfrastructureState (INFRASTRUCTURE-003 §3)"
            )
        here = LIFECYCLE_ORDER.index(self.state)
        there = LIFECYCLE_ORDER.index(to_state)
        if there < here:
            raise InfrastructureError(
                f"lifecycle is forward-only: {self.state.value} → {to_state.value} is backward"
            )
        return replace(self, state=to_state)

    # -- serialization ---

    def to_dict(self) -> dict[str, Any]:
        return {
            "construct_id": self.construct_id,
            "meta_class": self.meta_class,
            "type_tag": self.type_tag,
            "value_digest": self.value_digest,
            "state": self.state.value,
            "source_ref": self.source_ref,
            "target_ref": self.target_ref,
            "source_index": self.source_index,
            "target_index": self.target_index,
            "relationship": self.relationship,
            "basis": self.basis,
            "downward_only": self.downward_only,
            "relationships": list(self.meta_relationships()),
            "substrate_refs": list(SUBSTRATE_REFS),
        }


# ---------------------------------------------------------------------------
# Fail-closed factory
# ---------------------------------------------------------------------------


def make_dependency(
    type_tag: str,
    *,
    source_ref: str,
    target_ref: str,
    source_index: int,
    target_index: int,
    basis: str,
    state: InfrastructureState = InfrastructureState.DEFINED,
) -> InfrastructureDependency:
    """Construct a well-formed :class:`InfrastructureDependency` (fail-closed factory)."""
    return InfrastructureDependency(
        type_tag=type_tag,
        source_ref=source_ref,
        target_ref=target_ref,
        source_index=source_index,
        target_index=target_index,
        basis=basis,
        downward_only=True,
        relationship=DEPENDS_ON,
        state=state,
    )


__all__ = [
    "DEPENDS_ON",
    "INFRA_DEPENDENCY_ID_FAMILY",
    "INFRA_DEPENDENCY_ID_PREFIX",
    "InfrastructureDependency",
    "make_dependency",
]
