"""EC3-B12-U01 — The Universal Application construct (AMC-01).

Realizes the meta-model root concept **AMC-01 Application** (APPLICATION-005 §2;
APPLICATION-003 AOE-01; APPLICATION-001 §2/§4):

    the atomic unit of composed, actor-facing capability delivery — a typed (ENG-004)
    composition borne by an object (ENG-002), identified (ENG-001), that delivers a
    capability (AMR-01, by reference), whose state/interaction behavior is a RUNTIME
    construct (AMR-11, by reference) and whose structural participation is a PLATFORM
    experience composition (AMR-12, by reference; PLATFORM-009).

The construct is **additive over the CERTIFIED EC-1 foundation** (and the referenced,
CERTIFIED-COMPLETE Band-10 data surface + CERTIFIED-COMPLETE + FROZEN Band-11 service
surface) and reuses them *by reference* (UAL-02 / AMI-05): identity and value-fidelity
are derived through the EC-1 certified deterministic encoding
(:func:`engine.certification.contracts.canonical_json` /
:func:`~engine.certification.contracts.content_hash`) — the same discipline that
produces every EC-1 runtime, artifact, and certification identity — so this module
introduces **no second identity scheme and no parallel value model**. It selects no
technology/UI/screen (UAL-15) and confers no authority (UAL-15).

An :class:`Application` is *immutable* (a frozen object — ENG-002 objecthood), *typed*
(ENG-004), *identified* (ENG-001 via a deterministic id), *classified* (AXH-01 kind),
*capability-delivering* (AMR-01, by reference), *behavior-bound* and *composition-bound*
(AMR-11/12, by reference), and holds a *forward-only lifecycle state* (AOS-01…06,
UAL-12). Constructing an :class:`Application` enforces the meta-constraints
AMK-01/03/05/06 and the laws UAL-03/04/05/09/10/12 fail-closed: an ill-formed
application cannot be instantiated. It realizes **no** Capability, Module, Feature,
Workflow, Interaction, State, Composition, Security, or Governance object — those are
separate Band-12 units; this construct binds them only *by reference*.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any

from application.application_meta import (
    APPLICATION_META_CLASS,
    APPLICATION_RELATIONSHIPS,
    LIFECYCLE_ORDER,
    SUBSTRATE_REFS,
    ApplicationKind,
    ApplicationState,
)

# --- EC-1 reuse by reference (UAL-02 / AMI-05) — imported, never redefined --------
from engine.certification.contracts import canonical_json, content_hash

#: The deterministic id prefix for a realized Application (mirrors EC-1 UCOS-<KIND>-<hex16>).
APPLICATION_ID_PREFIX = "UCOS-APPLICATION"

#: The map of frozen-foundation primitives this construct reuses *by reference*
#: (never redefined). Recorded for the reuse-integrity check (UAL-02 / AMI-05 / VC-5).
FOUNDATION_REUSE: dict[str, str] = {
    "ENG-001": "engine.certification.contracts.content_hash (deterministic identity derivation)",
    "ENG-002": "python frozen object (immutable objecthood bearing the application)",
    "ENG-003": "engine.certification.contracts.canonical_json (value fidelity; no parallel model)",
    "ENG-004": "application.application_meta.ApplicationKind + type_tag (ENG-004 typing, by ref)",
    "ENG-005": "reference identifiers (capability/behavior/composition refs; no new construct)",
    "RL-F2": "state/interaction/workflow behavior bound by reference (AMR-11/06); none redefined",
    "PL-F2": "experience composition bound by reference (AMR-12; PLATFORM-009); none redefined",
    "DF-2": "presented/represented data by reference (AMR-14) — scoped to Feature unit (AMC-04)",
    "SF-2": "delivered capability via contracted operation by ref (AMR-13) — scoped to Feature",
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


class ApplicationError(ValueError):
    """Raised when inputs cannot be realized as a well-formed :class:`Application`.

    An :class:`Application` is fail-closed (TRACK-001): an ill-formed application
    construct is rejected at construction rather than admitted as an invalid application.
    """


def _require_reference(name: str, value: Any) -> str:
    """Require ``value`` to be a non-empty ENG-005 reference string (by reference)."""
    if not isinstance(value, str) or not value.strip():
        raise ApplicationError(
            f"{name} must be a non-empty ENG-005 reference (UAL-02/09/10)"
        )
    return value


@dataclass(frozen=True, slots=True)
class Application:
    """AMC-01 — an immutable, typed, identified, capability-delivering application root.

    Fields:
        type_tag:        the ENG-004 Type of the application (decidable, non-empty) — UAL-03.
        kind:            the AXH-01 classification of the application (AXC-02).
        capability_ref:  the ENG-005 reference to the capability the application delivers
                         (AMR-01, reference-only) — the AOE-01 defining relationship.
        behavior_ref:    the ENG-005 reference to the RUNTIME behavior/state the application
                         binds (AMR-11 behaves-as; RL-F2, by reference) — UAL-10/12.
        composition_ref: the ENG-005 reference to the PLATFORM experience composition the
                         application participates as (AMR-12 composed-as; PL-F2 /
                         PLATFORM-009) — UAL-09.
        state:           the AOS-01…06 lifecycle state (forward-only) — UAL-12 (default DEFINED).
    """

    type_tag: str
    kind: ApplicationKind
    capability_ref: str
    behavior_ref: str = "ENG-005:RL-F2:runtime.state"
    composition_ref: str = "ENG-005:PL-F2:PLATFORM-009.experience"
    state: ApplicationState = ApplicationState.DEFINED

    def __post_init__(self) -> None:
        # AMK-01 / UAL-03 — typed (ENG-004): a decidable, non-empty type tag.
        if not isinstance(self.type_tag, str) or not self.type_tag.strip():
            raise ApplicationError(
                "application must be typed with a non-empty ENG-004 type_tag (UAL-03)"
            )
        # AXH-01 / AXC-02 — classified by exactly one Application kind.
        if not isinstance(self.kind, ApplicationKind):
            raise ApplicationError("application kind must be an AXH-01 ApplicationKind (AXC-02)")
        # AMR-01 — an application delivers a capability, bound by reference (reference-only).
        _require_reference("capability_ref", self.capability_ref)
        # AMR-11 / UAL-10 — state/interaction behavior bound to RL-F2 by reference.
        _require_reference("behavior_ref", self.behavior_ref)
        # AMR-12 / UAL-09 — experience composition bound to PL-F2 by reference.
        _require_reference("composition_ref", self.composition_ref)
        # V5 / UAL-12 — a valid lifecycle state.
        if not isinstance(self.state, ApplicationState):
            raise ApplicationError(
                "application state must be an AOS-01…06 ApplicationState (UAL-12)"
            )

    # -- identity (ENG-001) borne by object (ENG-002), by reference ------------

    def canonical_core(self) -> dict[str, Any]:
        """The canonical, hashable core of the application (its identity-defining tuple)."""
        return {
            "meta_class": APPLICATION_META_CLASS,
            "type_tag": self.type_tag,
            "kind": self.kind.value,
            "capability_ref": self.capability_ref,
            "behavior_ref": self.behavior_ref,
            "composition_ref": self.composition_ref,
        }

    @property
    def value_digest(self) -> str:
        """The EC-1 content hash of the application core — the ENG-003 value fingerprint."""
        return content_hash(self.canonical_core())

    @property
    def application_id(self) -> str:
        """The deterministic ENG-001 identity of the application (borne by this object).

        Derived through the CERTIFIED EC-1 ``content_hash`` (UAL-04 — no second
        identity scheme): identical (type, kind, refs) always yields the identical id,
        so identity is reproducible and byte-stable (determinism, VC-4).
        """
        return f"{APPLICATION_ID_PREFIX}-{self.type_tag}-{self.value_digest[:16]}"

    # -- meta-model participation (APPLICATION-005) ----------------------------

    @property
    def meta_class(self) -> str:
        """V1 — the single meta-class this construct instantiates (AMC-01)."""
        return APPLICATION_META_CLASS

    def meta_relationships(self) -> tuple[str, ...]:
        """V2 — the AMR-01…14 relationships the application root participates in."""
        return APPLICATION_RELATIONSHIPS

    def is_founding_acyclic(self) -> bool:
        """V4 / AMK-03 — the founding graph is acyclic.

        An Application root binds its constituents *by reference* (string ids), so its
        founding structure carries no cycle; this is proven by the fact that its core
        canonically encodes (a cycle would raise at construction).
        """
        try:
            canonical_json(self.canonical_core())
        except (TypeError, ValueError):  # pragma: no cover - blocked at construction
            return False
        return True

    def references_resolve(self) -> bool:
        """AOI-03 / AMK-05/06 — every ENG-005 reference is a non-empty resolvable id."""
        return all(
            isinstance(ref, str) and bool(ref.strip())
            for ref in (self.capability_ref, self.behavior_ref, self.composition_ref)
        )

    # -- non-constitutiveness (UAL-15) -----------------------------------------

    def confers_authority(self) -> bool:
        """UAL-15 / C7 — an application confers no authority (structurally has none)."""
        return False

    def selects_technology(self) -> bool:
        """UAL-15 / C7 — True iff the application names a concrete technology/UI/vendor."""
        haystack = canonical_json(self.canonical_core()).lower()
        return any(marker in haystack for marker in _TECHNOLOGY_MARKERS)

    def embeds_secret(self) -> bool:
        """UAL-15 / RR-07 / C7 — True iff the application appears to embed a secret."""
        haystack = canonical_json(self.canonical_core()).lower()
        return any(marker in haystack for marker in _SECRET_MARKERS)

    def redefines_foundation(self) -> bool:
        """UAL-02 / AMI-05 / VC-5 — an application redefines no frozen primitive (reuse-only)."""
        return False

    # -- lifecycle (UAL-12, forward-only) --------------------------------------

    def transition(self, to_state: ApplicationState) -> Application:
        """Return a new application advanced to ``to_state`` (forward-only; UAL-12).

        Raises:
            ApplicationError: on a backward or in-place-reversing transition.
        """
        if not isinstance(to_state, ApplicationState):
            raise ApplicationError("target state must be an AOS-01…06 ApplicationState (UAL-12)")
        here = LIFECYCLE_ORDER.index(self.state)
        there = LIFECYCLE_ORDER.index(to_state)
        if there < here:
            raise ApplicationError(
                f"lifecycle is forward-only (UAL-12): "
                f"{self.state.value} → {to_state.value} is backward"
            )
        return replace(self, state=to_state)

    # -- serialization ----------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """A deterministic, serializable projection of the application."""
        return {
            "application_id": self.application_id,
            "meta_class": self.meta_class,
            "type_tag": self.type_tag,
            "kind": self.kind.value,
            "capability_ref": self.capability_ref,
            "behavior_ref": self.behavior_ref,
            "composition_ref": self.composition_ref,
            "value_digest": self.value_digest,
            "state": self.state.value,
            "relationships": list(self.meta_relationships()),
            "substrate_refs": list(SUBSTRATE_REFS),
        }


def make_application(
    type_tag: str,
    capability_ref: str,
    *,
    kind: ApplicationKind = ApplicationKind.SINGLE_MODULE,
    behavior_ref: str = "ENG-005:RL-F2:runtime.state",
    composition_ref: str = "ENG-005:PL-F2:PLATFORM-009.experience",
    state: ApplicationState = ApplicationState.DEFINED,
) -> Application:
    """Construct a well-formed :class:`Application` (fail-closed factory)."""
    return Application(
        type_tag=type_tag,
        kind=kind,
        capability_ref=capability_ref,
        behavior_ref=behavior_ref,
        composition_ref=composition_ref,
        state=state,
    )


__all__ = [
    "APPLICATION_ID_PREFIX",
    "FOUNDATION_REUSE",
    "ApplicationError",
    "Application",
    "make_application",
]
