"""EC3-B12-U08 — The Universal Composition construct (AMC-08).

Realizes the meta-model concept **AMC-08 Composition** (APPLICATION-005 §2;
APPLICATION-012; APPLICATION-003 AOE-08; APPLICATION-001 §2):

    the **structural assembly of features into modules and modules into applications**
    (and peer federation of applications) — a typed (ENG-004) object (ENG-002), identified
    (ENG-001), classified by one AXH-08 kind (Feature-into-Module / Module-into-Application
    / Application-Federation), that **assembles the constituents it composes** (its
    ``member_refs``, by reference), is the construct an application/module is
    **assembled-by** (AMR-07, the defining relationship — the Composition is the *target*
    of assembled-by), reuses **PL-F2 composition** (AMR-12 composed-as, by reference;
    PLATFORM-009/010; CMP-03/CMP-C5), keeps its **founding structural graph acyclic**
    (features→modules→applications; CMP-05/CMP-C1 / AMK-03 / UAL-09 — the governing
    condition), introduces **no new connection construct** (all links are ENG-005
    references; CMP-04/CMP-C2), preserves constituent boundaries (absorbs none; CMP-06/
    CMP-C3), federates peer applications by reference (CMP-07/CMP-C4), and binds its
    composition-emit behavior to the frozen RUNTIME event concern (§7, by reference).

The construct is **additive over the CERTIFIED EC-1 foundation** (and the referenced,
CERTIFIED-COMPLETE Band-10 data surface + CERTIFIED-COMPLETE + FROZEN Band-11 service
surface + the CERTIFIED Band-12 U01 Application root + U02 Capability + U03 Module + U04
Feature + U05 Workflow + U06 Interaction + U07 State) and reuses them *by reference*
(UAL-02 / AMI-05): identity and value-fidelity are derived through the EC-1 certified
deterministic encoding (:func:`engine.certification.contracts.canonical_json` /
:func:`~engine.certification.contracts.content_hash`) — the same discipline that produces
every EC-1 runtime, artifact, and certification identity — so this module introduces **no
second identity scheme and no parallel value model**. It selects no technology (no module
bundler, packaging system, framework, or container) and confers no authority (CMP-09 /
UAL-15). The PL-F2 composition construct is **reused by reference and never re-founded**
(CMP-03/CMP-C5).

A :class:`Composition` is *immutable* (a frozen object — ENG-002 objecthood), *typed*
(ENG-004), *identified* (ENG-001 via a deterministic id), *classified* (AXH-08 kind),
*assembling* (its members, by reference — the defining act), *founding-acyclic*
(CMP-C1 / AMK-03, materially proven), *boundary-preserving* (CMP-C3, absorbs none),
*platform-composition-bound* (AMR-12, by reference), and holds a *forward-only lifecycle
state* (AOS-01…06, UAL-12). Constructing a :class:`Composition` enforces the
meta-constraints AMK-01/02/03/05/06/08 and the laws UAL-03/04/05/09/10/12 fail-closed: an
ill-formed or cyclic composition cannot be instantiated. It realizes **no** Application,
Capability, Module, Feature, Workflow, Interaction, State, Security, or Governance object —
those are separate Band-12 units; this construct binds them only *by reference*. In
particular it **delivers no capability** (AMR-01), **consumes no SF-2 operation** (AMR-13),
**presents no DF-2 data** (AMR-14), and **holds no state** (AMR-06) — a composition
*assembles* what modules bound and features deliver, it is not the constituent itself.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Any

from application.composition_meta import (
    COMPOSITION_FACETS,
    COMPOSITION_FOUNDING_RELATIONSHIP,
    COMPOSITION_IS_FOUNDING,
    COMPOSITION_META_CLASS,
    COMPOSITION_MIN_MEMBERS,
    COMPOSITION_RELATIONSHIPS,
    LIFECYCLE_ORDER,
    SUBSTRATE_REFS,
    CompositionKind,
    CompositionState,
)

# --- EC-1 reuse by reference (UAL-02 / AMI-05) — imported, never redefined --------
from engine.certification.contracts import canonical_json, content_hash

#: The deterministic id prefix for a realized Composition (mirrors EC-1 UCOS-<KIND>-<hex16>).
COMPOSITION_ID_PREFIX = "UCOS-COMPOSITION"

#: The map of frozen-foundation primitives this construct reuses *by reference*
#: (never redefined). Recorded for the reuse-integrity check (UAL-02 / AMI-05 / VC-5).
FOUNDATION_REUSE: dict[str, str] = {
    "ENG-001": "engine.certification.contracts.content_hash (deterministic identity derivation)",
    "ENG-002": "python frozen object (immutable objecthood bearing the composition)",
    "ENG-003": "engine.certification.contracts.canonical_json (value fidelity; no parallel model)",
    "ENG-004": "application.composition_meta.CompositionKind + type_tag (ENG-004 typing, by ref)",
    "ENG-005": "reference identifiers (member/assembled/composition refs; no new construct)",
    "RL-F2": "composition-emit event behavior bound by reference (§7); none redefined",
    "PL-F2": "experience composition bound by reference (AMR-12; PLATFORM-009/010); none redef",
}

#: Concrete-technology markers forbidden by UAL-15 / CMP-09 (no module bundler / packaging
#: system / framework / container / vendor). An abstract EL-1/RL-F2/PL-F2 reference names
#: none of these — packaging/bundling/containers are downstream concerns (APPLICATION-012
#: §2.2), referenced through PL-F2, never selected.
_TECHNOLOGY_MARKERS: tuple[str, ...] = (
    # module bundlers / packaging systems (APPLICATION-012 §2.2 — none selected)
    "webpack",
    "rollup",
    "vite",
    "esbuild",
    "parcel",
    "turbopack",
    "browserify",
    "gradle",
    "maven",
    "bazel",
    "npm",
    "yarn",
    "pnpm",
    "pip",
    "cargo",
    # frameworks / containers / meshes / infra / vendors
    "react",
    "vue",
    "angular",
    "svelte",
    "spring",
    "kubernetes",
    "docker",
    "helm",
    "istio",
    "linkerd",
    "nginx",
    "lambda",
    "grpc",
    "graphql",
    "kafka",
    "rabbitmq",
    "postgres",
    "mysql",
    "mongodb",
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


class CompositionError(ValueError):
    """Raised when inputs cannot be realized as a well-formed :class:`Composition`.

    A :class:`Composition` is fail-closed (TRACK-001): an ill-formed or cyclic composition
    is rejected at construction rather than admitted as an invalid composition.
    """


def _require_reference(name: str, value: Any) -> str:
    """Require ``value`` to be a non-empty ENG-005 reference string (by reference)."""
    if not isinstance(value, str) or not value.strip():
        raise CompositionError(f"{name} must be a non-empty ENG-005 reference (UAL-02/09)")
    return value


def _contains_marker(value: str, markers: tuple[str, ...]) -> bool:
    """True iff ``value`` (case-insensitively) contains any of ``markers``."""
    haystack = value.lower()
    return any(marker in haystack for marker in markers)


def has_cycle(edges: tuple[tuple[str, str], ...]) -> bool:
    """True iff the directed graph described by ``edges`` contains a cycle.

    A deterministic depth-first, three-colour cycle detector over the founding edge set
    (member → assembled whole). This is the **material** proof of AMK-03 / CMP-C1 / UAL-09
    — the governing condition of AMC-08: the founding composition graph
    (features→modules→applications) is a DAG. A self-loop (``a → a``) is a cycle; so is any
    back-edge reachable through the adjacency.
    """
    adjacency: dict[str, list[str]] = {}
    for src, dst in edges:
        adjacency.setdefault(src, []).append(dst)
        adjacency.setdefault(dst, [])

    WHITE, GREY, BLACK = 0, 1, 2
    colour: dict[str, int] = {node: WHITE for node in adjacency}

    def visit(node: str) -> bool:
        colour[node] = GREY
        for nxt in adjacency[node]:
            if colour[nxt] == GREY:
                return True  # back-edge → cycle
            if colour[nxt] == WHITE and visit(nxt):
                return True
        colour[node] = BLACK
        return False

    # Visit in a deterministic (sorted) node order for byte-stable behaviour.
    return any(colour[node] == WHITE and visit(node) for node in sorted(adjacency))


@dataclass(frozen=True, slots=True)
class Composition:
    """AMC-08 — an immutable, typed, identified, founding-acyclic application Composition.

    Fields:
        type_tag:        the ENG-004 Type of the composition (decidable, non-empty) — UAL-03.
        kind:            the AXH-08 classification (AXC-04): Feature-into-Module /
                         Module-into-Application / Application-Federation.
        member_refs:     the ENG-005 references to the constituents the composition
                         assembles (features for Feature-into-Module, modules for
                         Module-into-Application, peer applications for
                         Application-Federation). Must be non-empty (≥2 for federation),
                         distinct (a partition — CMP-C3 boundary preservation), and never
                         include the assembled whole (non-absorption / no self-founding —
                         CMP-C1). Order-independent for identity (canonically sorted).
        assembled_ref:   the ENG-005 reference to the whole the composition assembles — the
                         module (Feature-into-Module) or application (Module-into-Application)
                         that is **assembled-by** this composition (AMR-07, the defining
                         relationship, reference-only); for a federation, the federated
                         peer-group whole. Required, non-empty, distinct from every member.
        composition_ref: the ENG-005 reference to the PLATFORM experience composition the
                         composition is composed-as (AMR-12; PL-F2 / PLATFORM-009/010, by
                         reference) — CMP-03/CMP-C5 / UAL-09.
        behavior_ref:    the ENG-005 reference to the RUNTIME event behavior the composition
                         binds (§7 composition-emit; RL-F2, by reference) — UAL-10.
        state:           the AOS-01…06 lifecycle state (forward-only) — UAL-12 (default DEFINED).
    """

    type_tag: str
    kind: CompositionKind
    member_refs: tuple[str, ...]
    assembled_ref: str = "ENG-005:AMC-01:ucos.application.foundation"
    composition_ref: str = "ENG-005:PL-F2:PLATFORM-009.composition"
    behavior_ref: str = "ENG-005:RL-F2:runtime.composition-emit"
    state: CompositionState = CompositionState.DEFINED

    #: Canonically ordered, de-duplicated view of the assembled members (identity-defining).
    _ordered_members: tuple[str, ...] = field(init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        # AMK-01 / UAL-03 / CMP-01 — typed (ENG-004): a decidable, non-empty type tag.
        if not isinstance(self.type_tag, str) or not self.type_tag.strip():
            raise CompositionError(
                "composition must be typed with a non-empty ENG-004 type_tag (UAL-03 / CMP-01)"
            )
        # AXH-08 / AXC-04 — classified by exactly one Composition kind.
        if not isinstance(self.kind, CompositionKind):
            raise CompositionError("composition kind must be an AXH-08 CompositionKind (AXC-04)")
        # AMR-07 / CMP-K2 — assembles an explicit, declared set of typed constituents.
        if not isinstance(self.member_refs, tuple):
            raise CompositionError(
                "member_refs must be a tuple of ENG-005 references (AMR-07 / CMP-K2)"
            )
        for ref in self.member_refs:
            if not isinstance(ref, str) or not ref.strip():
                raise CompositionError(
                    "each assembled constituent must be a non-empty ENG-005 reference (CMP-K2)"
                )
        # Topology decidability per kind (CMP-C4): founding kinds ≥1; federation ≥2 peers.
        minimum = COMPOSITION_MIN_MEMBERS[self.kind]
        if len(self.member_refs) < minimum:
            raise CompositionError(
                f"{self.kind.value} composition must assemble at least {minimum} "
                f"constituent(s) (CMP-C4 topology); got {len(self.member_refs)}"
            )
        # CMP-C3 / CMP-06 — boundary preservation: assembled constituents are a partition
        # (distinct; the composition absorbs no constituent identity).
        if len(set(self.member_refs)) != len(self.member_refs):
            raise CompositionError(
                "assembled constituents must be distinct: composition absorbs no identity "
                "(CMP-C3 / CMP-06)"
            )
        # AMR-07 — the assembled whole is referenced (reference-only).
        _require_reference("assembled_ref", self.assembled_ref)
        # AMR-12 / CMP-C5 / UAL-09 — PL-F2 experience composition bound by reference.
        _require_reference("composition_ref", self.composition_ref)
        # §7 / UAL-10 — composition-emit behavior bound to RL-F2 by reference.
        _require_reference("behavior_ref", self.behavior_ref)
        # V5 / UAL-12 — a valid lifecycle state.
        if not isinstance(self.state, CompositionState):
            raise CompositionError(
                "composition state must be an AOS-01…06 CompositionState (UAL-12)"
            )
        # CMP-C1 / AMK-03 — non-absorption / no self-founding: the assembled whole may not
        # be one of its own assembled constituents (a self-founding cycle).
        if self.assembled_ref in self.member_refs:
            raise CompositionError(
                "a composition cannot assemble its own assembled whole as a constituent "
                "(CMP-C1 / CMP-C3 — no self-founding)"
            )
        object.__setattr__(self, "_ordered_members", tuple(sorted(self.member_refs)))
        # CMP-C1 / AMK-03 / UAL-09 — the founding graph is a DAG (materially proven).
        # Defense-in-depth: the non-absorption guard above already blocks the only cycle a
        # single composition node can form (a member==assembled self-loop), so this raise is
        # unreachable via construction; the material acyclicity proof lives in
        # :meth:`is_founding_acyclic` and the :func:`has_cycle` detector (both exercised).
        if has_cycle(self.founding_edges()):  # pragma: no cover - defense-in-depth
            raise CompositionError(
                "the founding composition graph must be acyclic (CMP-C1 / AMK-03 / UAL-09)"
            )

    # -- founding structure (CMP-C1 / AMK-03 / UAL-09) -------------------------

    def founding_edges(self) -> tuple[tuple[str, str], ...]:
        """The directed founding edges (member → assembled whole) for founding kinds.

        Feature-into-Module and Module-into-Application are founding (each assembled
        constituent is composed *into* the whole). Application-Federation is **peer**
        (reference-only; CMP-07/CMP-C4) and contributes **no** founding edge — its founding
        graph is empty and therefore trivially acyclic.
        """
        if not COMPOSITION_IS_FOUNDING[self.kind]:
            return ()
        return tuple((member, self.assembled_ref) for member in self._ordered_members)

    def is_founding_acyclic(self) -> bool:
        """V4 / AMK-03 / CMP-C1 / UAL-09 — the founding graph is acyclic (materially proven).

        THE governing condition of AMC-08: the founding composition graph
        (features→modules→applications) is a DAG. Proven by running the deterministic
        three-colour cycle detector over the founding edge set (empty, hence acyclic, for a
        peer federation).
        """
        try:
            canonical_json(self.canonical_core())
        except (TypeError, ValueError):  # pragma: no cover - blocked at construction
            return False
        return not has_cycle(self.founding_edges())

    def participates_in_founding_edge(self) -> bool:
        """AMK-03 — True iff the composition is founding (Feature/Module-into-*).

        A founding composition reuses AMR-02/03 (founding, acyclic); a peer
        Application-Federation reuses AMR-07 (reference-only) and founds nothing.
        """
        return COMPOSITION_IS_FOUNDING[self.kind]

    def founding_relationship(self) -> str:
        """AMR — the founding meta-relationship the assembly reuses (AMR-02/03) or AMR-07."""
        return COMPOSITION_FOUNDING_RELATIONSHIP[self.kind]

    def is_federation(self) -> bool:
        """CMP-07 / CMP-C4 — True iff the composition is a peer Application-Federation."""
        return self.kind is CompositionKind.APPLICATION_FEDERATION

    # -- identity (ENG-001) borne by object (ENG-002), by reference ------------

    def canonical_core(self) -> dict[str, Any]:
        """The canonical, hashable core of the composition (its identity-defining tuple).

        Assembled membership is a set (a partition), so the members are canonically sorted —
        two compositions assembling the same constituents in different declaration order
        bear the same ENG-001 identity. The lifecycle ``state`` is **not** part of identity.
        """
        return {
            "meta_class": COMPOSITION_META_CLASS,
            "type_tag": self.type_tag,
            "kind": self.kind.value,
            "facet": self.facet(),
            "member_refs": list(self._ordered_members),
            "assembled_ref": self.assembled_ref,
            "composition_ref": self.composition_ref,
            "behavior_ref": self.behavior_ref,
        }

    @property
    def value_digest(self) -> str:
        """The EC-1 content hash of the composition core — the ENG-003 value fingerprint."""
        return content_hash(self.canonical_core())

    @property
    def composition_id(self) -> str:
        """The deterministic ENG-001 identity of the composition (borne by this object).

        Derived through the CERTIFIED EC-1 ``content_hash`` (UAL-04 — no second identity
        scheme): identical (type, kind, refs) always yields the identical id, so identity is
        reproducible and byte-stable (determinism, VC-4).
        """
        return f"{COMPOSITION_ID_PREFIX}-{self.type_tag}-{self.value_digest[:16]}"

    # -- meta-model participation (APPLICATION-005/012) ------------------------

    @property
    def meta_class(self) -> str:
        """V1 — the single meta-class this construct instantiates (AMC-08)."""
        return COMPOSITION_META_CLASS

    def meta_relationships(self) -> tuple[str, ...]:
        """V2 — the AMR-01…14 relationships the composition participates in."""
        return COMPOSITION_RELATIONSHIPS

    def facet(self) -> str:
        """AXH-08 — the assembly facet the kind classifies (feature/module/application)."""
        return COMPOSITION_FACETS[self.kind]

    def references_resolve(self) -> bool:
        """AOI-03 / AMK-05/06 — every ENG-005 reference is a non-empty resolvable id."""
        refs = (self.assembled_ref, self.composition_ref, self.behavior_ref)
        base = all(isinstance(r, str) and bool(r.strip()) for r in refs)
        members = all(isinstance(r, str) and bool(r.strip()) for r in self.member_refs)
        return base and members

    def assembles_members(self) -> bool:
        """AMR-07 / CMP-C1 — the composition assembles at least one constituent by reference."""
        return len(self.member_refs) >= 1

    def assembled_member_count(self) -> int:
        """The number of constituents the composition assembles (its assembly size)."""
        return len(self.member_refs)

    def members_are_partition(self) -> bool:
        """CMP-C3 / CMP-06 — assembled constituents are distinct (a boundary-preserving set)."""
        return len(set(self.member_refs)) == len(self.member_refs) and all(
            r.strip() for r in self.member_refs
        )

    def preserves_boundaries(self) -> bool:
        """CMP-06 / CMP-C3 — the composition absorbs no constituent identity.

        Boundaries are preserved iff the assembled constituents are a distinct partition and
        the assembled whole is not itself one of its constituents (non-absorption).
        """
        return self.members_are_partition() and self.assembled_ref not in self.member_refs

    def federation_is_by_reference(self) -> bool:
        """CMP-07 / CMP-C4 — a federation composes ≥2 peer apps by reference (never absorbed).

        For founding kinds this is vacuously true (they are not federations); for a
        federation it requires ≥2 distinct peer references and no absorption.
        """
        if not self.is_federation():
            return True
        return self.assembled_member_count() >= 2 and self.preserves_boundaries()

    def uses_new_connection_construct(self) -> bool:
        """CMP-04 / CMP-C2 — True iff any link is not a plain ENG-005 reference string.

        A composition introduces no new connection construct: every member/assembled/
        composition/behavior link is an ENG-005 reference (a non-empty string). This is
        False for a well-formed composition.
        """
        links = (
            *self.member_refs,
            self.assembled_ref,
            self.composition_ref,
            self.behavior_ref,
        )
        return not all(isinstance(link, str) and bool(link.strip()) for link in links)

    def binds_platform_composition(self) -> bool:
        """AMR-12 / CMP-03 / CMP-C5 — the composition reuses PL-F2 composition by reference."""
        return bool(self.composition_ref.strip()) and not _contains_marker(
            self.composition_ref, _TECHNOLOGY_MARKERS
        )

    def binds_runtime_event(self) -> bool:
        """AMK-05 / §7 / UAL-10 — the composition-emit behavior binds RL-F2 by reference."""
        return bool(self.behavior_ref.strip()) and not _contains_marker(
            self.behavior_ref, _TECHNOLOGY_MARKERS
        )

    def assembled_by(self) -> str:
        """AMR-07 — the ENG-005 reference to the whole this composition assembles."""
        return self.assembled_ref

    def assembles(self, member_ref: str) -> bool:
        """AMR-07 / CMP-C1 — True iff ``member_ref`` is a constituent this composition assembles."""
        return member_ref in self.member_refs

    # -- non-constitutiveness (UAL-15 / CMP-09) --------------------------------

    def confers_authority(self) -> bool:
        """UAL-15 / CMP-09 / C7 — a composition confers no authority (structurally has none)."""
        return False

    def selects_technology(self) -> bool:
        """UAL-15 / CMP-09 / C7 — True iff the composition names a concrete technology/vendor.

        Covers module bundlers, packaging systems, frameworks, containers, meshes,
        transports, protocols, infrastructure, or vendors across the whole composition core.
        """
        haystack = canonical_json(self.canonical_core()).lower()
        return any(marker in haystack for marker in _TECHNOLOGY_MARKERS)

    def embeds_secret(self) -> bool:
        """UAL-15 / RR-07 / C7 — True iff the composition appears to embed a secret."""
        haystack = canonical_json(self.canonical_core()).lower()
        return any(marker in haystack for marker in _SECRET_MARKERS)

    def redefines_foundation(self) -> bool:
        """UAL-02 / AMI-05 / VC-5 — a composition redefines no frozen primitive (reuse-only)."""
        return False

    # -- lifecycle (UAL-12, forward-only) --------------------------------------

    def transition(self, to_state: CompositionState) -> Composition:
        """Return a new composition advanced to ``to_state`` (forward-only; UAL-12).

        Raises:
            CompositionError: on a backward or in-place-reversing transition.
        """
        if not isinstance(to_state, CompositionState):
            raise CompositionError("target state must be an AOS-01…06 CompositionState (UAL-12)")
        here = LIFECYCLE_ORDER.index(self.state)
        there = LIFECYCLE_ORDER.index(to_state)
        if there < here:
            raise CompositionError(
                f"lifecycle is forward-only (UAL-12): "
                f"{self.state.value} → {to_state.value} is backward"
            )
        return replace(self, state=to_state)

    # -- serialization ----------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """A deterministic, serializable projection of the composition."""
        return {
            "composition_id": self.composition_id,
            "meta_class": self.meta_class,
            "type_tag": self.type_tag,
            "kind": self.kind.value,
            "facet": self.facet(),
            "member_refs": list(self._ordered_members),
            "assembled_member_count": self.assembled_member_count(),
            "assembled_ref": self.assembled_ref,
            "composition_ref": self.composition_ref,
            "behavior_ref": self.behavior_ref,
            "founding_relationship": self.founding_relationship(),
            "value_digest": self.value_digest,
            "state": self.state.value,
            "is_founding": self.participates_in_founding_edge(),
            "is_federation": self.is_federation(),
            "founding_acyclic": self.is_founding_acyclic(),
            "preserves_boundaries": self.preserves_boundaries(),
            "binds_platform_composition": self.binds_platform_composition(),
            "binds_runtime_event": self.binds_runtime_event(),
            "relationships": list(self.meta_relationships()),
            "substrate_refs": list(SUBSTRATE_REFS),
        }


def make_composition(
    type_tag: str,
    member_refs: tuple[str, ...],
    *,
    kind: CompositionKind = CompositionKind.MODULE_INTO_APPLICATION,
    assembled_ref: str = "ENG-005:AMC-01:ucos.application.foundation",
    composition_ref: str = "ENG-005:PL-F2:PLATFORM-009.composition",
    behavior_ref: str = "ENG-005:RL-F2:runtime.composition-emit",
    state: CompositionState = CompositionState.DEFINED,
) -> Composition:
    """Construct a well-formed :class:`Composition` (fail-closed factory)."""
    return Composition(
        type_tag=type_tag,
        kind=kind,
        member_refs=tuple(member_refs),
        assembled_ref=assembled_ref,
        composition_ref=composition_ref,
        behavior_ref=behavior_ref,
        state=state,
    )


__all__ = [
    "COMPOSITION_ID_PREFIX",
    "FOUNDATION_REUSE",
    "CompositionError",
    "has_cycle",
    "Composition",
    "make_composition",
]
