"""EC3-B11-U10 — The Universal Security construct (SMC-10).

Realizes the meta-model concept **SMC-10 Security** (SERVICE-005 §2; SERVICE-003 SOE-10;
SERVICE-014 §3):

    a **decidable record classifying a service/operation's authentication, authorization,
    confidentiality, and integrity concerns** — a record of *what a construct requires and
    asserts*, never a mechanism that *enacts* protection — an ENG-002 Object bearing an ENG-001
    Identity, classified by an ENG-004 Type (SXH-10 = Authentication / Authorization /
    Confidentiality / Integrity records), that **classifies** the Service/Operation/Execution
    boundary that references it (SMR-09 classified-by, reference-only; SOR-09; SSE-07), is
    **governed-by** — i.e. its classification is *informed by* — a declarative Policy (SMR-08
    governed-by, reference-only; SOR-08), **behaves-as** the RUNTIME policy concern for its
    evaluation (SMR-11; RUNTIME-010, by reference; §7), and reuses DATA-014 data-security
    classifications for confidentiality/integrity over the operation's DF-2 data via
    **operates-on** (SMR-13, by reference; SSE-06).

The construct is the **evaluative protection facet**: it *classifies* which boundary it protects,
which policy informs it, and which RUNTIME policy concern evaluates it — all as **references**, so
the classification is decidable with **no enforcement, no access grant, no credential issuance, no
encryption, and no conferred authority** (USL-14 / SSE-03 / SSE-C1…C5). Evaluating a security
object yields a recorded *classification judgment* (:class:`SecurityAssessment`, satisfied /
violated) against a classified construct's ENG-002 object (SSE-C1 / SOV-09); the *act* of
evaluation is a reference to the frozen RUNTIME policy concern (RUNTIME-010), never re-implemented
here (§7). The security object defines no cryptography, key store, IAM product, TLS/mTLS,
credential, secret, or enforcement point; it references the declarative RUNTIME policy concept and
the DATA-014 data-security classifications only (STH-13 / §2.2).

The construct is **additive over the CERTIFIED EC-1 foundation** and reuses it — and the
CERTIFIED SMC-01…09 Service / Capability / Contract / Interface / Operation / Composition /
Orchestration / Execution / Policy — *by reference* (USL-02 / SMI-05): identity and value-fidelity
are derived through the EC-1 certified deterministic encoding, so this module introduces **no
second identity scheme and no parallel value model**. It selects no technology / cryptography /
IAM / key-management (USL-15 / SSE-04) and confers no authority (USL-13/14 / SSE-09).

A :class:`Security` is *immutable* (ENG-002 objecthood), *typed* (ENG-004), *identified*
(ENG-001), *classified* (SXH-10 kind), *boundary-classifying by reference* (SMR-09), *policy-
informed by reference* (SMR-08 governed-by), *runtime-reusing* (SMR-11 / §7), *data-by-reference*
(SMR-13; DATA-014), and holds a *forward-only lifecycle state* (SOS-01…06, USL-12). Constructing a
:class:`Security` enforces these obligations fail-closed: an ill-formed security object cannot be
instantiated. It realizes/binds no Service, Capability, Contract, Interface, Operation,
Composition, Orchestration, Execution, or Policy object — those are separate units; this construct
classifies and references them only *by reference*.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from enum import Enum
from typing import Any

from engine.certification.contracts import canonical_json, content_hash
from service.security_meta import (
    DATA_BEARING_KINDS,
    KIND_BEHAVIOR_SUFFIX,
    KIND_PRECEDENCE,
    KIND_RUNTIME_CONCERN,
    LIFECYCLE_ORDER,
    SECURITY_META_CLASS,
    SECURITY_RELATIONSHIPS,
    SECURITY_SUBSTRATE_REFS,
    SecurityKind,
    ServiceState,
)
from service.service import (
    _SECRET_MARKERS,
    _TECHNOLOGY_MARKERS,
    ServiceError,
)

#: The deterministic id prefix for a realized Security object (mirrors EC-1 UCOS-<KIND>-<hex16>).
SECURITY_ID_PREFIX = "UCOS-SECURITY"

#: The map of frozen-foundation primitives this construct reuses *by reference*.
SECURITY_FOUNDATION_REUSE: dict[str, str] = {
    "ENG-001": "engine.certification.contracts.content_hash (deterministic identity derivation)",
    "ENG-002": "python frozen object (immutable objecthood bearing the security record)",
    "ENG-003": "engine.certification.contracts.canonical_json (structural value fidelity)",
    "ENG-004": "service.security_meta.SecurityKind + type_tag (ENG-004 typing, by reference)",
    "ENG-005": "reference identifiers (subject/policy/behavior/data refs; no new construct)",
    "RL-F2": "security evaluation bound by reference (SMR-11; RUNTIME-010 evaluate / RUNTIME-008)",
    "DF-2": "confidentiality/integrity data bound by reference (SMR-13; DATA-014); not redefined",
}


class SecurityVerdict(str, Enum):
    """The recorded outcome of *evaluating* a security classification (SSE-C1 / SOV-09).

    A verdict is a recorded *classification judgment*, never an enacted decision (USL-14 /
    SSE-03 / SSE-C1): it grants no access, issues no credential, encrypts nothing, and mutates no
    state. ``INAPPLICABLE`` records that the security object does not classify the subject (out of
    the declared classified boundary).
    """

    SATISFIED = "SATISFIED"  # the classified subject satisfies the security classification
    VIOLATED = "VIOLATED"  # the classified subject violates the security classification
    INAPPLICABLE = "INAPPLICABLE"  # the security object does not classify the subject (unscoped)


def _default_behavior_ref(kind: SecurityKind) -> str:
    """The abstract RL-F2 security-evaluation reference for ``kind`` (SERVICE-014 §7)."""
    concern = KIND_RUNTIME_CONCERN[kind]
    suffix = KIND_BEHAVIOR_SUFFIX[kind]
    return f"ENG-005:RL-F2:{concern}.{suffix}"


def _require_reference(name: str, value: Any) -> str:
    """Require ``value`` to be a non-empty ENG-005 reference string (by reference)."""
    if not isinstance(value, str) or not value.strip():
        raise ServiceError(f"{name} must be a non-empty ENG-005 reference (SMR-08/09/11/13)")
    return value


def _require_ref_tuple(name: str, values: Any, *, minimum: int = 0) -> tuple[str, ...]:
    """Require ``values`` to be a tuple of non-empty ENG-005 reference strings (≥ ``minimum``)."""
    if not isinstance(values, tuple):
        raise ServiceError(f"{name} must be a tuple of ENG-005 references (SMR-08/09/13)")
    for v in values:
        if not isinstance(v, str) or not v.strip():
            raise ServiceError(
                f"{name} entries must be non-empty ENG-005 references (SMR-08/09/13)"
            )
    if len(values) < minimum:
        raise ServiceError(f"{name} must declare at least {minimum} ENG-005 reference (SSE-K2)")
    return values


@dataclass(frozen=True, slots=True)
class SecurityAssessment:
    """A recorded, immutable classification judgment produced by *evaluating* a security object.

    An assessment **records** a verdict against a classified construct's ENG-002 object; it
    enacts nothing, grants nothing, issues no credential, encrypts nothing, and mutates no state
    (USL-14 / SSE-C1 / SSE-C2). The judgment value itself is supplied by the frozen RUNTIME policy
    concern (RUNTIME-010, by reference; §7) — this construct only records it deterministically.
    """

    security_id: str
    subject_ref: str
    verdict: SecurityVerdict
    kind: str

    def enacts_nothing(self) -> bool:
        """USL-14 / SSE-C1 — an assessment is a record; it enacts nothing (structurally true)."""
        return True

    def to_dict(self) -> dict[str, Any]:
        """A deterministic, serializable projection of the recorded classification judgment."""
        return {
            "assessment_format": "ucos-security-assessment/1.0.0",
            "security_id": self.security_id,
            "subject_ref": self.subject_ref,
            "verdict": self.verdict.value,
            "kind": self.kind,
            "enacts": "none",
        }


@dataclass(frozen=True, slots=True)
class Security:
    """SMC-10 — an immutable, typed, identified, decidable, non-enforcing security classification.

    Fields:
        type_tag:     the ENG-004 Type of the security object (decidable, non-empty) — SSE-01.
        kind:         the SXH-10 classification (Authentication / Authorization / Confidentiality
                      / Integrity record).
        subject_refs: tuple of ENG-005 references to the Service/Operation/Execution boundaries
                      this security object classifies (SMR-09 classified-by; SOR-09; the declared
                      classified boundary; by reference; SSE-07 / SSE-K2). Must be non-empty.
        policy_refs:  tuple of ENG-005 references to the declarative Policies that *inform* this
                      classification (SMR-08 governed-by; SOR-08; reference-only). May be empty.
        behavior_ref: the ENG-005 reference to the RUNTIME policy concern the security evaluation
                      behaves-as (SMR-11; RL-F2; RUNTIME-010; §7). If omitted it defaults to the
                      kind-appropriate RUNTIME policy reference.
        data_refs:    tuple of DF-2-represented data references whose confidentiality/integrity is
                      classified by reference to DATA-014 (SMR-13 operates-on; SOR-13; SSE-06).
                      May be empty (identity/access records need not reference data).
        state:        the SOS-01…06 lifecycle state (forward-only) — USL-12.
    """

    type_tag: str
    kind: SecurityKind
    subject_refs: tuple[str, ...]
    policy_refs: tuple[str, ...] = field(default=())
    behavior_ref: str = ""
    data_refs: tuple[str, ...] = field(default=())
    state: ServiceState = ServiceState.DEFINED

    def __post_init__(self) -> None:
        # SSE-K1 / USL-03 / SSE-01 — typed (ENG-004): a decidable, non-empty type tag.
        if not isinstance(self.type_tag, str) or not self.type_tag.strip():
            raise ServiceError("security must be typed: a non-empty ENG-004 type_tag (SSE-01)")
        # SXH-10 / SXC-02 — classified by exactly one security kind.
        if not isinstance(self.kind, SecurityKind):
            raise ServiceError("security kind must be an SXH-10 SecurityKind (SXC-02)")
        # SMR-09 / SOR-09 / SSE-07 / SSE-K2 — classifies at least one declared boundary.
        _require_ref_tuple("subject_refs", self.subject_refs, minimum=1)
        # SMR-08 / SOR-08 — the informing Policies (governed-by), by reference (may be empty).
        _require_ref_tuple("policy_refs", self.policy_refs)
        # §7 — derive the kind-appropriate RUNTIME policy behavior reference if omitted.
        if not (isinstance(self.behavior_ref, str) and self.behavior_ref.strip()):
            object.__setattr__(self, "behavior_ref", _default_behavior_ref(self.kind))
        # SMR-11 / SOR-11 / §7 — behaves-as the RUNTIME policy concern, by reference.
        _require_reference("behavior_ref", self.behavior_ref)
        # SMR-13 / SOR-13 / SSE-06 — confidentiality/integrity data by reference (may be empty).
        _require_ref_tuple("data_refs", self.data_refs)
        # V5 / USL-12 — a valid lifecycle state.
        if not isinstance(self.state, ServiceState):
            raise ServiceError("security state must be a SOS-01…06 ServiceState (USL-12)")

    # -- identity (ENG-001) borne by object (ENG-002), by reference ------------

    def canonical_core(self) -> dict[str, Any]:
        """The canonical, hashable core of the security object (its identity-defining tuple)."""
        return {
            "meta_class": SECURITY_META_CLASS,
            "type_tag": self.type_tag,
            "kind": self.kind.value,
            "subject_refs": list(self.subject_refs),
            "policy_refs": list(self.policy_refs),
            "behavior_ref": self.behavior_ref,
            "data_refs": list(self.data_refs),
        }

    @property
    def value_digest(self) -> str:
        """The EC-1 content hash of the security core — the ENG-003 value fingerprint."""
        return content_hash(self.canonical_core())

    @property
    def security_id(self) -> str:
        """The deterministic ENG-001 identity of the security object (borne by this object)."""
        return f"{SECURITY_ID_PREFIX}-{self.type_tag}-{self.value_digest[:16]}"

    @property
    def self_ref(self) -> str:
        """The ENG-005 self-reference form of this security object (for self-founding detection)."""
        return f"ENG-005:SOE-10:{self.type_tag}"

    # -- meta-model participation (SERVICE-005) --------------------------------

    @property
    def meta_class(self) -> str:
        """V1 — the single meta-class this construct instantiates (SMC-10)."""
        return SECURITY_META_CLASS

    def meta_relationships(self) -> tuple[str, ...]:
        """V2 — the SMR-01…13 relationships the security object participates in."""
        return SECURITY_RELATIONSHIPS

    # -- founding acyclicity (V4 / SMK-03) -------------------------------------

    def is_founding_acyclic(self) -> bool:
        """V4 / SMK-03 / SMI-04 — the founding graph (classified-by / behaves-as) is acyclic.

        A Security object classifies its boundary, is informed by policies, behaves-as a runtime
        concern, and operates-on data *by reference* (string ids), so its founding structure
        carries no cycle. Canonical encodability proves the core is well-formed; the
        no-self-founding guard proves no reference names the security object itself.
        """
        try:
            canonical_json(self.canonical_core())
        except (TypeError, ValueError):  # pragma: no cover - blocked at construction
            return False
        return self.no_self_founding()

    def no_self_founding(self) -> bool:
        """SMK-03 — no reference founds the security object on itself (no self-founding cycle)."""
        me = self.self_ref
        return all(
            ref != me
            for ref in (
                self.behavior_ref,
                *self.subject_refs,
                *self.policy_refs,
                *self.data_refs,
            )
        )

    # -- security-specific obligations -----------------------------------------

    def boundary_classified(self) -> bool:
        """SMR-09 / SOR-09 / SSE-07 / SSE-K2 — classifies at least one declared boundary."""
        return bool(self.subject_refs) and all(
            isinstance(r, str) and bool(r.strip()) for r in self.subject_refs
        )

    def evaluative_nonenforcing(self) -> bool:
        """USL-14 / SSE-03 / SSE-C1 — the security object is evaluative and enacts nothing.

        This is the governing law of the Security concern: a security object *classifies*
        authentication/authorization/confidentiality/integrity concerns and its evaluation
        *records a judgment* while *conferring no authority*. It is structurally non-enforcing —
        the construct holds only references and a type; it can grant nothing, issue no credential,
        encrypt nothing, and mutate no state.
        """
        return not self.confers_authority()

    def runtime_reuse_valid(self) -> bool:
        """§7 — evaluation behaves-as the RUNTIME policy concern (RUNTIME-010) by reference."""
        expected = KIND_RUNTIME_CONCERN[self.kind]
        return bool(self.behavior_ref.strip()) and expected in self.behavior_ref

    def behavior_by_reference(self) -> bool:
        """SMR-11 / USL-10 — evaluation binds RL-F2 by ENG-005 reference (RUNTIME-010)."""
        return bool(self.behavior_ref.strip())

    def data_by_reference(self) -> bool:
        """SMR-13 / SOR-13 / SSE-06 / USL-11 — every data ref is a DF-2/DATA-014 reference."""
        return all(isinstance(r, str) and bool(r.strip()) for r in self.data_refs)

    def data_security_reuse(self) -> bool:
        """SSE-06 / SSE-C3 — confidentiality/integrity data reuses DATA-014 by reference.

        Structurally true: confidentiality/integrity data references are DF-2 ids resolved against
        the DATA-014 data-security architecture; this construct never redefines a data-security
        concept. Kinds that bear no data (authentication/access) trivially conform.
        """
        return self.data_by_reference()

    def policy_informed(self) -> bool:
        """SMR-08 / SOR-08 — every informing-policy reference is a non-empty ENG-005 reference."""
        return all(isinstance(r, str) and bool(r.strip()) for r in self.policy_refs)

    @property
    def bears_data(self) -> bool:
        """True iff this security kind classifies operation data confidentiality/integrity."""
        return self.kind in DATA_BEARING_KINDS

    @property
    def precedence(self) -> int:
        """The deterministic evaluation-precedence rank of the security object (SXH-10 order).

        A *lower* rank is evaluated first. This is a decidable, evaluative ordering only
        (USL-14 / SSE-03): it enacts nothing and confers nothing — it records the deterministic
        order in which classification facets are considered when several apply to one boundary.
        """
        return KIND_PRECEDENCE[self.kind]

    def precedence_decidable(self) -> bool:
        """SSE-08 — the security object's evaluation precedence is decidable from its kind."""
        return self.kind in KIND_PRECEDENCE

    def classifies(self, subject_ref: str) -> bool:
        """SSE-07 — True iff ``subject_ref`` is within this object's classified boundary."""
        return isinstance(subject_ref, str) and subject_ref in self.subject_refs

    def records_lifecycle(self) -> bool:
        """SSE-08 / SOV-08 — records a decidable lifecycle state (not silent)."""
        return isinstance(self.state, ServiceState)

    def references_resolve(self) -> bool:
        """SSE-K4 / SMK-05/07 — every ENG-005 reference is a non-empty resolvable id."""
        return all(
            isinstance(ref, str) and bool(ref.strip())
            for ref in (
                self.behavior_ref,
                *self.subject_refs,
                *self.policy_refs,
                *self.data_refs,
            )
        ) and self.no_self_founding()

    # -- evaluative classification → recorded judgment (SSE-C1 / SOV-09) -------

    def record_assessment(self, subject_ref: str, satisfied: bool) -> SecurityAssessment:
        """Record a classification judgment for ``subject_ref`` — evaluative, non-enforcing.

        The *act* of deciding whether the boundary satisfies the security classification is the
        RUNTIME policy concern (RUNTIME-010, by reference; §7) — supplied here as ``satisfied``.
        This method only **records** the resulting verdict against the subject's ENG-002 object; it
        enacts nothing, grants nothing, issues no credential, and mutates no state (USL-14 / SSE-C1
        / SSE-C2). A subject outside the declared classified boundary records ``INAPPLICABLE``.
        """
        _require_reference("subject_ref", subject_ref)
        if not self.classifies(subject_ref):
            verdict = SecurityVerdict.INAPPLICABLE
        else:
            verdict = SecurityVerdict.SATISFIED if satisfied else SecurityVerdict.VIOLATED
        return SecurityAssessment(
            security_id=self.security_id,
            subject_ref=subject_ref,
            verdict=verdict,
            kind=self.kind.value,
        )

    # -- non-constitutiveness (USL-15 / SSE-04/05/09) --------------------------

    def confers_authority(self) -> bool:
        """USL-13/14 / USL-15 / SSE-09 / C7 — a security object confers no authority (none)."""
        return False

    def selects_technology(self) -> bool:
        """USL-15 / SSE-04 / C7 — True iff the security object names crypto/IAM/technology."""
        haystack = canonical_json(self.canonical_core()).lower()
        return any(marker in haystack for marker in _TECHNOLOGY_MARKERS)

    def embeds_secret(self) -> bool:
        """USL-15 / SSE-05 / RR-07 / C7 — True iff the security object appears to embed a secret."""
        haystack = canonical_json(self.canonical_core()).lower()
        return any(marker in haystack for marker in _SECRET_MARKERS)

    def redefines_foundation(self) -> bool:
        """USL-02 / SMI-05 / VC-5 — a security object redefines no frozen primitive (reuse-only)."""
        return False

    # -- lifecycle (USL-12, forward-only) --------------------------------------

    def transition(self, to_state: ServiceState) -> Security:
        """Return a new security object advanced to ``to_state`` (forward-only; USL-12)."""
        if not isinstance(to_state, ServiceState):
            raise ServiceError("target state must be a SOS-01…06 ServiceState (USL-12)")
        here = LIFECYCLE_ORDER.index(self.state)
        there = LIFECYCLE_ORDER.index(to_state)
        if there < here:
            raise ServiceError(
                f"lifecycle is forward-only (USL-12): "
                f"{self.state.value} → {to_state.value} is backward"
            )
        return replace(self, state=to_state)

    # -- serialization ----------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """A deterministic, serializable projection of the security object."""
        return {
            "security_id": self.security_id,
            "meta_class": self.meta_class,
            "type_tag": self.type_tag,
            "kind": self.kind.value,
            "subject_refs": list(self.subject_refs),
            "policy_refs": list(self.policy_refs),
            "behavior_ref": self.behavior_ref,
            "data_refs": list(self.data_refs),
            "value_digest": self.value_digest,
            "state": self.state.value,
            "precedence": self.precedence,
            "bears_data": self.bears_data,
            "runtime_concern": KIND_RUNTIME_CONCERN[self.kind],
            "relationships": list(self.meta_relationships()),
            "substrate_refs": list(SECURITY_SUBSTRATE_REFS),
        }


@dataclass(frozen=True, slots=True)
class SecurityCoverage:
    """A recorded, evaluative report of which SXH-10 facets classify a given boundary.

    Coverage is an **evaluative record** (SERVICE-014 §12 classification coverage / exposure map):
    for one classified boundary it records which of the four SXH-10 security facets are present
    and which are absent. Recording coverage enacts nothing and confers no authority (USL-14 /
    SSE-03); an absent facet is a *recorded observation*, never an enforced requirement.
    """

    subject_ref: str
    facets_present: tuple[str, ...]
    facets_absent: tuple[str, ...]

    @property
    def fully_covered(self) -> bool:
        """True iff every SXH-10 facet classifies this boundary (no absent facet)."""
        return not self.facets_absent

    def to_dict(self) -> dict[str, Any]:
        return {
            "coverage_format": "ucos-security-coverage/1.0.0",
            "subject_ref": self.subject_ref,
            "facets_present": list(self.facets_present),
            "facets_absent": list(self.facets_absent),
            "fully_covered": self.fully_covered,
            "assessment": "evaluative record; records only, enacts nothing",
        }


def assess_security_coverage(
    security_objects: tuple[Security, ...],
) -> tuple[SecurityCoverage, ...]:
    """Report SXH-10 classification coverage per boundary — evaluative, non-enforcing.

    For each classified boundary (SMR-09 subject) across ``security_objects``, records which of
    the four SXH-10 facets (Authentication / Authorization / Confidentiality / Integrity) classify
    it and which are absent. The report is deterministic and records only; it grants nothing,
    blocks nothing, and requires nothing (SERVICE-014 §12 / USL-14 / SSE-03). Facets are ordered by
    their SXH-10 declaration order (via :data:`KIND_PRECEDENCE`).
    """
    all_facets = tuple(k.value for k in sorted(SecurityKind, key=lambda k: KIND_PRECEDENCE[k]))
    present: dict[str, set[str]] = {}
    for sec in security_objects:
        for subject_ref in sec.subject_refs:
            present.setdefault(subject_ref, set()).add(sec.kind.value)

    coverage: list[SecurityCoverage] = []
    for subject_ref in sorted(present):
        facets = present[subject_ref]
        coverage.append(
            SecurityCoverage(
                subject_ref=subject_ref,
                facets_present=tuple(f for f in all_facets if f in facets),
                facets_absent=tuple(f for f in all_facets if f not in facets),
            )
        )
    return tuple(coverage)


def make_security(
    type_tag: str,
    subject_refs: tuple[str, ...],
    *,
    kind: SecurityKind = SecurityKind.AUTHORIZATION,
    policy_refs: tuple[str, ...] = (),
    behavior_ref: str = "",
    data_refs: tuple[str, ...] = (),
    state: ServiceState = ServiceState.DEFINED,
) -> Security:
    """Construct a well-formed :class:`Security` (fail-closed factory)."""
    return Security(
        type_tag=type_tag,
        kind=kind,
        subject_refs=subject_refs,
        policy_refs=policy_refs,
        behavior_ref=behavior_ref,
        data_refs=data_refs,
        state=state,
    )


__all__ = [
    "SECURITY_ID_PREFIX",
    "SECURITY_FOUNDATION_REUSE",
    "SecurityVerdict",
    "SecurityAssessment",
    "Security",
    "SecurityCoverage",
    "assess_security_coverage",
    "make_security",
]
