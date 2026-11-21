"""EC3-B10-U07 — The Universal Governance construct (DMC-08).

Realizes the meta-model construct **DMC-08 Governance-Object** (DATA-005 §2; DATA-012 §3):

    the **declarative, decidable, descriptive/evaluative and non-enforcing** design
    governance of data — a record that evaluates a data construct's conformance to the
    Data Laws and represents non-enforcing data policy (the ontology root DOE-08),
    classified by DXH-08 (Conformance-Record / Policy-Object / Evaluation-Record). A
    governance object is an ENG-002 Object classified by an ENG-004 Type, recorded
    against a data construct via ``governs`` (DMR-07) and binding evaluation *by
    reference* to the frozen RUNTIME policy concern (DMR-11). Data governance is neither
    the data it governs nor an authority — it is an **evaluative record that enacts
    nothing**.

The construct is **additive over the CERTIFIED EC-1 foundation *and* the CERTIFIED
DMC-02 Entity**, reusing both *by reference* (UDL-02 / DMI-05):

* Identity is derived through the EC-1 certified deterministic encoding
  (:func:`engine.certification.contracts.canonical_json` /
  :func:`~engine.certification.contracts.content_hash`) — no second identity scheme.
* The governed subject (DMR-07 ``governs``) is a **reference to a CERTIFIED data
  construct** (id + structural digest + name/type + meta-class), **never owned,
  embedded, or copied** (DGA-C4 by record; DMX-02 non-absorbing).
* Evaluation behavior is a **RUNTIME policy reference** only (``behaves-as``, DMR-11 /
  DGA-07) — no policy engine, rules engine, access-control/IAM, or enforcement point is
  defined.

**No policy/rules engine, access-control/IAM system, enforcement point, or vendor is
selected** (UDL-13 / DGA-09 / DGA-K5) — enforced fail-closed by a technology-marker scan
over the whole construct. A governance object **confers no authority and grants no
access** (DGA-03 / DGA-K5): this is the material exercise of UDL-13 Governance as
Declarative Constraint — governance *is* an evaluative record that enacts nothing.

A :class:`GovernanceObject` is *immutable* (frozen — ENG-002 objecthood), *typed*
(ENG-004, DGA-K1/UDL-03), *identified* (ENG-001, DGA-K1/UDL-04), *subject-bound*
(``governs`` a CERTIFIED construct by reference — DMR-07), *declarative and
non-enforcing* (DGA-01/02/K2), *recorded* (DGA-06/K4), *versioned*, and holds a
*forward-only lifecycle state* (DOS-01…05, UDL-12). Constructing a
:class:`GovernanceObject` enforces DGA-K1/K2/K3/K4/K5, the evaluation rules
DGA-C1/C2/C3/C4, and UDL-13/03/04/05 **fail-closed**: an ill-formed, enforcing, or
authority-conferring governance object cannot exist.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any

# --- DMC-02 reuse by reference (UDL-02) — never redefined -------------------------
from data.entity import Entity
from data.governance_meta import (
    GOVERNANCE_META_CLASS,
    GOVERNANCE_RELATIONSHIPS,
    GOVERNANCE_SUBSTRATE_REFS,
    LIFECYCLE_ORDER,
    GovernanceKind,
    GovernanceState,
    GovernanceVerdict,
)

# --- EC-1 reuse by reference (UDL-02 / DMI-05) — imported, never redefined --------
from engine.certification.contracts import canonical_json, content_hash

#: The deterministic id prefix for a realized Governance object (mirrors EC-1 UCOS-<K>-<hex>).
GOVERNANCE_ID_PREFIX = "UCOS-GOVERNANCE"

#: The reference prefix a governance object presents to bind RUNTIME policy evaluation
#: (DMR-11 / DGA-07 / DOB-06 evaluate) — declarative, non-enforcing.
POLICY_REF_PREFIX = "UCOS-POLICY-REF"

#: The prefix of a CERTIFIED data-construct identity (the DMR-07 ``governs`` target).
CERTIFIED_ID_PREFIX = "UCOS-"

#: The map of EC-1 / DMC-02 primitives this construct reuses *by reference* (never
#: redefined). Recorded for the reuse-integrity check (UDL-02 / DMI-05 / VC-5).
REUSE_REFS: dict[str, str] = {
    "ENG-001": "engine.certification.contracts.content_hash (deterministic identity derivation)",
    "ENG-002": "python frozen object (immutable objecthood bearing the judgment record)",
    "ENG-004": "data.governance_meta.GovernanceKind + type_tag (ENG-004 typing discipline)",
    "ENG-005": "governed-construct + RUNTIME policy identity references (DMR-07/11)",
    "DMC-02": "data.entity.Entity — a CERTIFIED governs target (DMR-07); referenced only",
    "RL-F2": "RUNTIME policy — evaluation bound by reference (DMR-11 / DGA-07)",
}

#: Conservative secret markers used to enforce UDL-15 / DGA-09 / RR-07 (embed no secret).
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

#: Conservative governance-technology markers used to enforce **UDL-13 / DGA-09 / DGA-K5**
#: (select no policy/rules engine, access-control/IAM system, or enforcement point). A
#: governance object naming any of these is rejected fail-closed — governance is a
#: declarative, non-enforcing record only. This is the material exercise of UDL-13.
_TECH_MARKERS: tuple[str, ...] = (
    "open policy agent",
    "opa policy",
    "rego",
    "casbin",
    "xacml",
    "rbac",
    "abac",
    "keycloak",
    "okta",
    "auth0",
    "active directory",
    "ldap",
    "oauth2",
    "openid",
    "apache ranger",
    "immuta",
    "collibra",
    "alation",
    "policy engine",
    "rules engine",
    "access control",
    "access-control",
    "enforcement point",
    "data loss prevention",
    "approval workflow",
    "iam system",
)


def policy_ref_for(predicate: str) -> str:
    """The reference a governance object presents to bind RUNTIME policy (DMR-11 / DGA-07).

    A governance object's conformance/policy evaluation is a *reference* to the frozen
    RL-F2 policy concern (DOB-06 evaluate), which is declarative and non-enforcing by
    construction — never a redefined policy engine.
    """
    return f"{POLICY_REF_PREFIX}:{predicate}"


class GovernanceError(ValueError):
    """Raised when a value cannot be realized as a well-formed :class:`GovernanceObject`.

    A :class:`GovernanceObject` is fail-closed (TRACK-001): an ill-formed, enforcing,
    access-granting, authority-conferring, or technology-bound governance record is
    rejected at construction rather than admitted as an invalid or constitutive object.
    """


@dataclass(frozen=True, slots=True)
class GovernedConstructRef:
    """A reference to a CERTIFIED data construct a governance object ``governs`` (DMR-07).

    Records **only** the governed construct's identity, structural fingerprint, name,
    type, and meta-class — never its implementation — so the governance object
    references, and never owns or absorbs, the construct it governs (DMX-02 non-absorbing;
    DGA-C4 by record; UDL-02 reuse-by-reference).
    """

    construct_id: str
    structure_digest: str
    name: str
    type_tag: str
    meta_class: str

    @classmethod
    def from_entity(cls, entity: Entity) -> GovernedConstructRef:
        """Project a CERTIFIED :class:`~data.entity.Entity` into a governed-construct ref."""
        if not isinstance(entity, Entity):
            raise GovernanceError("a governance object governs a data construct (DMR-07)")
        return cls(
            construct_id=entity.entity_id,
            structure_digest=entity.structure_digest,
            name=entity.name,
            type_tag=entity.type_tag,
            meta_class=entity.meta_class,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "construct_id": self.construct_id,
            "structure_digest": self.structure_digest,
            "name": self.name,
            "type_tag": self.type_tag,
            "meta_class": self.meta_class,
            "binding": "DMR-07:governs",
            "owned": False,  # DGA-C4 — governed by record, never owned
            "absorbing": False,  # DMX-02 — referenced, not absorbed
        }


@dataclass(frozen=True, slots=True)
class ConformanceEntry:
    """A single recorded conformance judgment against one applicable Data Law (DGA-C1).

    Purely declarative: it *records* whether the governed construct satisfies the law;
    it enforces nothing and remediates nothing (DGA-02 / DGA-C5).
    """

    law_id: str
    satisfied: bool
    note: str = ""

    def __post_init__(self) -> None:
        if not isinstance(self.law_id, str) or not self.law_id.strip():
            raise GovernanceError("a conformance entry names an applicable Data Law (DGA-C1)")
        if not isinstance(self.satisfied, bool):
            raise GovernanceError("a conformance entry records a decidable verdict (DGA-C1)")

    def to_dict(self) -> dict[str, Any]:
        return {"law_id": self.law_id, "satisfied": self.satisfied, "note": self.note}


@dataclass(frozen=True, slots=True)
class GovernanceObject:
    """DMC-08 — an immutable, declarative, non-enforcing, non-authoritative governance record.

    Fields:
        name:         the explicit governance-object name (part of identity).
        type_tag:     the ENG-004 Type of the object (DGA-K1; UDL-03).
        kind:         the DXH-08 classification (Conformance-Record / Policy-Object /
                      Evaluation-Record; DMR-09 classified-by).
        governed_ref: the CERTIFIED construct the object ``governs`` (DMR-07; DGA-C4
                      by record, non-owning).
        policy_ref:   the RUNTIME policy reference evaluation binds to (DMR-11 / DGA-07 /
                      DGA-K3). A reference obligation only — no policy engine is defined.
        conformance:  the recorded per-law conformance verdicts (DGA-C1). Required
                      non-empty for a Conformance-Record; empty for other kinds.
        verdict:      the recorded governance judgment (DGA-06 / DOV-08). Required a
                      decidable verdict for an Evaluation-Record.
        steward:      a recorded, non-authoritative stewardship descriptor (DGA-05 /
                      DGA-C4). Confers no power; may be empty.
        state:        the DOS-01…05 forward-only lifecycle state (UDL-12).
        version:      the object version (supersession on breaking change; UDL-12/15).
        supersedes:   the id of a superseded governance object (DGA-C3 append-only).
    """

    name: str
    type_tag: str
    kind: GovernanceKind
    governed_ref: GovernedConstructRef
    policy_ref: str
    conformance: tuple[ConformanceEntry, ...] = ()
    verdict: GovernanceVerdict = GovernanceVerdict.CONFORMANT
    steward: str = ""
    state: GovernanceState = GovernanceState.DEFINED
    version: str = "1.0.0"
    supersedes: str = ""

    def __post_init__(self) -> None:
        # explicit, decidable name.
        if not isinstance(self.name, str) or not self.name.strip():
            raise GovernanceError("governance object must have an explicit name")
        # DGA-K1 / DMK-01 / UDL-03 — typed (ENG-004): a decidable, non-empty type.
        if not isinstance(self.type_tag, str) or not self.type_tag.strip():
            raise GovernanceError(
                "governance object must be typed with an ENG-004 type_tag (DGA-K1)"
            )
        # DXH-08 / DMR-09 — classified by exactly one governance kind.
        if not isinstance(self.kind, GovernanceKind):
            raise GovernanceError("governance kind must be a DXH-08 GovernanceKind (DMR-09)")
        # DMR-07 — the governed subject is a reference to a CERTIFIED construct.
        if not isinstance(self.governed_ref, GovernedConstructRef):
            raise GovernanceError("governance governs a CERTIFIED construct by reference (DMR-07)")
        if not self.governed_ref.construct_id.startswith(CERTIFIED_ID_PREFIX):
            raise GovernanceError("the governed subject is not a CERTIFIED construct id (DMR-07)")
        if len(self.governed_ref.structure_digest) != 64 or any(
            c not in "0123456789abcdef" for c in self.governed_ref.structure_digest
        ):
            raise GovernanceError("the governed subject carries no structural digest (UDL-06)")
        # DMR-11 / DGA-07 / DGA-K3 — evaluation binds a RUNTIME policy reference.
        if not isinstance(self.policy_ref, str) or not self.policy_ref.startswith(
            f"{POLICY_REF_PREFIX}:"
        ):
            raise GovernanceError(
                "evaluation must bind a RUNTIME policy reference (DMR-11 / DGA-K3)"
            )
        # DGA-C1 — a Conformance-Record records ≥1 decidable per-law verdict.
        if not isinstance(self.conformance, tuple):
            raise GovernanceError("conformance must be a tuple of ConformanceEntry (DGA-C1)")
        seen_laws: set[str] = set()
        for entry in self.conformance:
            if not isinstance(entry, ConformanceEntry):
                raise GovernanceError("conformance entries are ConformanceEntry records (DGA-C1)")
            if entry.law_id in seen_laws:
                raise GovernanceError("conformance records a duplicate law verdict (DGA-C1)")
            seen_laws.add(entry.law_id)
        if self.kind is GovernanceKind.CONFORMANCE_RECORD and not self.conformance:
            raise GovernanceError("a Conformance-Record records ≥1 law verdict (DGA-C1)")
        # DGA-06 / DOV-08 — an Evaluation-Record records a decidable verdict.
        if not isinstance(self.verdict, GovernanceVerdict):
            raise GovernanceError("verdict must be a decidable GovernanceVerdict (DGA-06)")
        # DGA-05 / DGA-C4 — stewardship is a recorded descriptor (a string), not a power.
        if not isinstance(self.steward, str):
            raise GovernanceError("steward must be a recorded descriptor string (DGA-05)")
        # V5 / UDL-12 — a valid forward-only lifecycle state.
        if not isinstance(self.state, GovernanceState):
            raise GovernanceError("governance state must be a DOS-01…05 state (UDL-12)")
        # DGA-08 — a governance object records an explicit, non-empty version.
        if not isinstance(self.version, str) or not self.version.strip():
            raise GovernanceError("governance object must record an explicit version (DGA-08)")
        if not isinstance(self.supersedes, str):
            raise GovernanceError("governance supersedes reference must be a string (DGA-C3)")
        # UDL-13 / DGA-09 / DGA-K5 — names no policy/enforcement technology (material).
        if self._scan_technology():
            raise GovernanceError(
                "governance names a policy engine/IAM/enforcement technology or vendor "
                "(UDL-13 / DGA-09 / DGA-K5)"
            )

    # -- technology-neutrality (UDL-13, material) ------------------------------

    def _scan_technology(self) -> bool:
        """True iff any technology marker appears in the object's declared surface."""
        haystack = canonical_json(self.canonical_core()).lower()
        return any(marker in haystack for marker in _TECH_MARKERS)

    def names_technology(self) -> bool:
        """UDL-13 / DGA-09 / DGA-K5 / C6 — True iff the object names a governance tech."""
        return self._scan_technology()

    # -- identity (ENG-001) borne by object (ENG-002), by reference ------------

    def canonical_core(self) -> dict[str, Any]:
        """The canonical, hashable core of the object (structure + governed reference)."""
        return {
            "meta_class": GOVERNANCE_META_CLASS,
            "name": self.name,
            "type_tag": self.type_tag,
            "kind": self.kind.value,
            "governed_ref": {
                "construct_id": self.governed_ref.construct_id,
                "structure_digest": self.governed_ref.structure_digest,
                "name": self.governed_ref.name,
                "type_tag": self.governed_ref.type_tag,
                "meta_class": self.governed_ref.meta_class,
            },
            "policy_ref": self.policy_ref,
            "conformance": [
                {"law_id": c.law_id, "satisfied": c.satisfied, "note": c.note}
                for c in self.conformance
            ],
            "verdict": self.verdict.value,
            "steward": self.steward,
            "version": self.version,
            "supersedes": self.supersedes,
        }

    @property
    def structure_digest(self) -> str:
        """The EC-1 content hash of the object core — its structural fingerprint."""
        return content_hash(self.canonical_core())

    @property
    def governance_id(self) -> str:
        """The deterministic ENG-001 identity of the object (borne by this object).

        Derived through the CERTIFIED EC-1 ``content_hash`` (UDL-04 — no second identity
        scheme): an identical object always yields the identical id, so identity is
        reproducible and byte-stable (determinism, VC-4).
        """
        return f"{GOVERNANCE_ID_PREFIX}-{self.name}-{self.structure_digest[:16]}"

    # -- meta-model participation (DATA-005 / DATA-012) ------------------------

    @property
    def meta_class(self) -> str:
        """V1 — the single meta-class this construct instantiates (DMC-08)."""
        return GOVERNANCE_META_CLASS

    def meta_relationships(self) -> tuple[str, ...]:
        """V2 — the DMR-01…12 relationships the object participates in."""
        return GOVERNANCE_RELATIONSHIPS

    def governed_construct_id(self) -> str:
        """The identity of the construct this object governs (DMR-07; by reference)."""
        return self.governed_ref.construct_id

    def conformance_laws(self) -> tuple[str, ...]:
        """The applicable Data Laws this object records a verdict for (DGA-C1)."""
        return tuple(c.law_id for c in self.conformance)

    # -- governance property predicates ----------------------------------------

    def is_declarative(self) -> bool:
        """DGA-01 / DGA-K2 — governance is a declarative, decidable predicate."""
        return True

    def enforces(self) -> bool:
        """DGA-02 / DGA-K2 — governance evaluates and records; it enforces nothing."""
        return False

    def grants_access(self) -> bool:
        """DGA-03 / DGA-K5 — governance grants no access (structurally none)."""
        return False

    def is_recorded(self) -> bool:
        """DGA-06 / DGA-K4 — the judgment is recorded against an ENG-002 object (DOV-08)."""
        return True

    def binds_policy_by_reference(self) -> bool:
        """DMR-11 / DGA-07 / DGA-K3 — evaluation binds a RUNTIME policy reference only."""
        return self.policy_ref.startswith(f"{POLICY_REF_PREFIX}:")

    def records_conformance(self) -> bool:
        """DGA-C1 — a Conformance-Record decidably records each applicable-law verdict."""
        if self.kind is GovernanceKind.CONFORMANCE_RECORD:
            return bool(self.conformance)
        return True

    def stewardship_is_descriptor(self) -> bool:
        """DGA-05 / DGA-C4 — stewardship/ownership are recorded descriptors, not powers."""
        return not self.confers_authority()

    def gap_report(self) -> tuple[str, ...]:
        """DGA-C5 — the laws recorded as violated, routed to a Gap Report (record-only).

        Governance *records* violations and routes them to a Gap Report; it does not
        itself remediate or enforce (DGA-02 / DGA-C5).
        """
        return tuple(c.law_id for c in self.conformance if not c.satisfied)

    def is_conformant(self) -> bool:
        """Whether the recorded conformance verdicts show no violation (evaluative only)."""
        return not self.gap_report()

    def is_classified(self) -> bool:
        """DXH-08 — the object is classified by exactly one governance kind."""
        return isinstance(self.kind, GovernanceKind)

    def is_founding_acyclic(self) -> bool:
        """V4 / DMK-03 — the founding/governance graph is acyclic.

        The object's founding references (``governs`` → construct, ``behaves-as`` →
        RUNTIME policy) are recorded by *identity reference*; none may reference the
        object itself, so the founding graph is a DAG.
        """
        own = self.governance_id
        refs = {self.governed_construct_id(), self.policy_ref}
        return own not in refs

    def governs_construct(self, construct_id: str) -> bool:
        """DMR-07 — whether this object governs the construct ``construct_id``."""
        return construct_id == self.governed_construct_id()

    def absorbs_governed(self) -> bool:
        """DGA-C4 / DMX-02 — the object references the construct it governs, never owns it."""
        return False

    # -- non-constitutiveness (UDL-13/15 / DGA-03/09) --------------------------

    def confers_authority(self) -> bool:
        """UDL-13/15 / DGA-03 / C7 — a governance object confers no authority (material)."""
        return False

    def embeds_secret(self) -> bool:
        """UDL-15 / DGA-09 / RR-07 / C7 — True iff the object appears to embed a secret."""
        haystack = canonical_json(self.canonical_core()).lower()
        return any(marker in haystack for marker in _SECRET_MARKERS)

    def redefines_el1(self) -> bool:
        """UDL-02 / DMI-05 / VC-5 — a governance object redefines no EL-1/DMC-02/RL-F2 model."""
        return False

    def selects_technology(self) -> bool:
        """UDL-13 / DGA-09 / DGA-K5 — a governance object selects no policy tech (material)."""
        return self._scan_technology()

    # -- lifecycle (UDL-12, forward-only) --------------------------------------

    def transition(self, to_state: GovernanceState) -> GovernanceObject:
        """Return a new object advanced to ``to_state`` (forward-only; UDL-12).

        Breaking change to a policy is supersession, never in-place mutation
        (DATA-012 §8; UDL-12/15; DGA-C3 append-only).

        Raises:
            GovernanceError: on a backward transition.
        """
        if not isinstance(to_state, GovernanceState):
            raise GovernanceError("target state must be a DOS-01…05 state (UDL-12)")
        here = LIFECYCLE_ORDER.index(self.state)
        there = LIFECYCLE_ORDER.index(to_state)
        if there < here:
            raise GovernanceError(
                f"lifecycle is forward-only (UDL-12): "
                f"{self.state.value} → {to_state.value} is backward"
            )
        return replace(self, state=to_state)

    # -- serialization ----------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """A deterministic, serializable projection of the governance object."""
        return {
            "governance_id": self.governance_id,
            "meta_class": self.meta_class,
            "name": self.name,
            "type_tag": self.type_tag,
            "kind": self.kind.value,
            "governed_ref": self.governed_ref.to_dict(),
            "governed_construct_id": self.governed_construct_id(),
            "policy_ref": self.policy_ref,
            "binds_policy_by_reference": self.binds_policy_by_reference(),
            "conformance": [c.to_dict() for c in self.conformance],
            "conformance_laws": list(self.conformance_laws()),
            "records_conformance": self.records_conformance(),
            "verdict": self.verdict.value,
            "gap_report": list(self.gap_report()),
            "is_conformant": self.is_conformant(),
            "steward": self.steward,
            "stewardship_is_descriptor": self.stewardship_is_descriptor(),
            "declarative": self.is_declarative(),
            "enforces": self.enforces(),
            "grants_access": self.grants_access(),
            "recorded": self.is_recorded(),
            "confers_authority": self.confers_authority(),
            "names_technology": self.names_technology(),
            "classified": self.is_classified(),
            "version": self.version,
            "supersedes": self.supersedes,
            "state": self.state.value,
            "relationships": list(self.meta_relationships()),
            "substrate_refs": list(GOVERNANCE_SUBSTRATE_REFS),
            "absorbs_governed": self.absorbs_governed(),
        }


def make_conformance(entries: tuple[tuple[str, bool], ...]) -> tuple[ConformanceEntry, ...]:
    """Build a tuple of :class:`ConformanceEntry` from ``(law_id, satisfied)`` pairs."""
    return tuple(ConformanceEntry(law_id=law, satisfied=ok) for law, ok in entries)


def make_governance(
    name: str,
    type_tag: str,
    governed: Entity | GovernedConstructRef,
    policy_ref: str,
    *,
    kind: GovernanceKind = GovernanceKind.CONFORMANCE_RECORD,
    conformance: tuple[ConformanceEntry, ...] = (),
    verdict: GovernanceVerdict = GovernanceVerdict.CONFORMANT,
    steward: str = "",
    state: GovernanceState = GovernanceState.DEFINED,
    version: str = "1.0.0",
    supersedes: str = "",
) -> GovernanceObject:
    """Construct a well-formed :class:`GovernanceObject` (fail-closed factory).

    ``governed`` is the construct the object governs — either a CERTIFIED
    :class:`~data.entity.Entity` (reused by reference — the DMR-07 ``governs`` target) or
    an already-projected :class:`GovernedConstructRef`.
    """
    governed_ref = (
        governed
        if isinstance(governed, GovernedConstructRef)
        else GovernedConstructRef.from_entity(governed)
    )
    return GovernanceObject(
        name=name,
        type_tag=type_tag,
        kind=kind,
        governed_ref=governed_ref,
        policy_ref=policy_ref,
        conformance=tuple(conformance),
        verdict=verdict,
        steward=steward,
        state=state,
        version=version,
        supersedes=supersedes,
    )


__all__ = [
    "GOVERNANCE_ID_PREFIX",
    "POLICY_REF_PREFIX",
    "CERTIFIED_ID_PREFIX",
    "REUSE_REFS",
    "policy_ref_for",
    "GovernanceError",
    "GovernedConstructRef",
    "ConformanceEntry",
    "GovernanceObject",
    "make_conformance",
    "make_governance",
]
