"""EC3-B12-U09 — The Universal Security construct (AMC-09).

Realizes the meta-model concept **AMC-09 Security** (APPLICATION-005 §2; APPLICATION-013;
APPLICATION-003 AOE-09; APPLICATION-001 §2):

    the **evaluative, non-enforcing classification of an application/feature's
    authentication, authorization, confidentiality, and integrity concerns** — a record of
    *what a construct requires and asserts*, never a mechanism that *enacts* protection — a
    typed (ENG-004) object (ENG-002), identified (ENG-001), classified by one AXH-09 kind
    (Authentication / Authorization / Confidentiality / Integrity record), that is the
    construct an application/feature boundary is **secured-by** (AMR-08, the defining
    relationship — the Security record is the *target* of secured-by; reference-only), is
    **governed-by** a declarative Governance security-policy record (AMR-09, reference-only),
    **presents** classified DF-2/DATA-014 data (AMR-14, by reference), binds its evaluation to
    the frozen RUNTIME policy concern (§7 security-evaluate; RL-F2, by reference), records its
    judgments through the frozen RUNTIME event concern (§7 security-record), and reuses the
    DATA-014 / SERVICE-014 security classifications by reference (§7 security-reference).

The construct is the **evaluative protection facet**: it *classifies* which boundary it is
recorded against, which governance informs it, which RUNTIME policy concern evaluates it, and
which DF-2 data it presents — all as **references**, so the classification is decidable with
**no enforcement, no access grant, no credential issuance, no encryption, and no conferred
authority** (UAL-14 / SEC-03 / SEC-C1…C5). Evaluating a security record yields a recorded
*classification judgment* (:class:`SecurityAssessment`, satisfied / violated / inapplicable)
against a classified construct's ENG-002 object (SEC-C1 / AOV-09); the *act* of evaluation is a
reference to the frozen RUNTIME policy concern (RUNTIME-010), never re-implemented here (§7).
The security record defines no cryptography, key store, identity provider, credential store,
access-control engine, protocol, or enforcement point; it references the declarative RUNTIME
policy concept and the DATA-014 data-security classifications only (ATH-13 / §2.2).

The construct is **additive over the CERTIFIED EC-1 foundation** (and the referenced,
CERTIFIED-COMPLETE Band-10 data surface + CERTIFIED-COMPLETE + FROZEN Band-11 service surface +
the CERTIFIED Band-12 U01 Application root + U02 Capability + U03 Module + U04 Feature + U05
Workflow + U06 Interaction + U07 State + U08 Composition) and reuses them *by reference*
(UAL-02 / AMI-05): identity and value-fidelity are derived through the EC-1 certified
deterministic encoding (:func:`engine.certification.contracts.canonical_json` /
:func:`~engine.certification.contracts.content_hash`), so this module introduces **no second
identity scheme and no parallel value model**. It selects no technology / cryptography / IAM /
key-management (UAL-15 / SEC-05) and confers no authority (UAL-14/15 / SEC-09).

A :class:`Security` is *immutable* (a frozen object — ENG-002 objecthood), *typed* (ENG-004),
*identified* (ENG-001 via a deterministic id), *classified* (AXH-09 kind), *boundary-recording
by reference* (AMR-08 secured-by), *governance-informed by reference* (AMR-09 governed-by),
*data-presenting by reference* (AMR-14 presents-data; DATA-014), *runtime-reusing* (§7
security-evaluate → RL-F2), and holds a *forward-only lifecycle state* (AOS-01…06, UAL-12).
Constructing a :class:`Security` enforces these obligations fail-closed: an ill-formed security
record cannot be instantiated. It realizes no Application, Capability, Module, Feature,
Workflow, Interaction, State, Composition, or Governance object — those are separate Band-12
units; this construct classifies and references them only *by reference*.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from enum import Enum
from typing import Any

from application.security_meta import (
    DATA_BEARING_KINDS,
    KIND_PRECEDENCE,
    KIND_RUNTIME_CONCERN,
    LIFECYCLE_ORDER,
    SECURITY_FACETS,
    SECURITY_META_CLASS,
    SECURITY_RELATIONSHIPS,
    SUBSTRATE_REFS,
    SecurityKind,
    SecurityState,
)

# --- EC-1 reuse by reference (UAL-02 / AMI-05) — imported, never redefined --------
from engine.certification.contracts import canonical_json, content_hash

#: The deterministic id prefix for a realized Security record (mirrors EC-1 UCOS-<KIND>-<hex16>).
SECURITY_ID_PREFIX = "UCOS-SECURITY"

#: The map of frozen-foundation primitives this construct reuses *by reference*
#: (never redefined). Recorded for the reuse-integrity check (UAL-02 / AMI-05 / VC-5).
FOUNDATION_REUSE: dict[str, str] = {
    "ENG-001": "engine.certification.contracts.content_hash (deterministic identity derivation)",
    "ENG-002": "python frozen object (immutable objecthood bearing the security record)",
    "ENG-003": "engine.certification.contracts.canonical_json (value fidelity; no parallel model)",
    "ENG-004": "application.security_meta.SecurityKind + type_tag (ENG-004 typing, by reference)",
    "ENG-005": "reference identifiers (subject/governance/data/behavior refs; no new construct)",
    "RL-F2": "security-evaluate policy + security-record event bound by reference (§7); none redef",
    "DF-2": "confidentiality/integrity data bound by reference (AMR-14; DATA-014); none redefined",
}

#: Concrete-technology markers forbidden by UAL-15 / SEC-05 (no cryptography / IAM / key store /
#: credential store / access-control engine / protocol / vendor). An abstract EL-1/RL-F2/DF-2
#: reference names none of these — security/cryptographic technology is out of scope
#: (APPLICATION-013 §2.2), referenced through RL-F2 / DATA-014, never selected.
_TECHNOLOGY_MARKERS: tuple[str, ...] = (
    # security / cryptographic technology (APPLICATION-013 §2.2 — none selected)
    "oauth",
    "openid",
    "saml",
    "jwt",
    "kerberos",
    "ldap",
    "tls",
    "mtls",
    "ssl",
    "aes",
    "rsa",
    "sha256",
    "bcrypt",
    "argon2",
    "pbkdf2",
    "hmac",
    # identity providers / IAM / key stores / secret stores / vendors
    "keycloak",
    "okta",
    "auth0",
    "cognito",
    "vault",
    "hashicorp",
    "iam",
    "kms",
    # frameworks / containers / meshes / infra / transports / vendors
    "react",
    "spring",
    "kubernetes",
    "docker",
    "istio",
    "nginx",
    "lambda",
    "grpc",
    "graphql",
    "kafka",
    "postgres",
    "mysql",
    "mongodb",
    "http://",
    "https://",
    "tcp://",
)

#: Conservative secret markers used to enforce UAL-15 / RR-07 / SEC-09 (embed no secret).
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


class SecurityError(ValueError):
    """Raised when inputs cannot be realized as a well-formed :class:`Security` record.

    A :class:`Security` record is fail-closed (TRACK-001): an ill-formed record is rejected at
    construction rather than admitted as an invalid classification.
    """


class SecurityVerdict(str, Enum):
    """The recorded outcome of *evaluating* a security classification (SEC-C1 / AOV-09).

    A verdict is a recorded *classification judgment*, never an enacted decision (UAL-14 /
    SEC-03 / SEC-C2): it grants no access, issues no credential, encrypts nothing, and mutates no
    state. ``INAPPLICABLE`` records that the security record does not classify the subject (out
    of the declared classified boundary).
    """

    SATISFIED = "SATISFIED"  # the classified subject satisfies the security classification
    VIOLATED = "VIOLATED"  # the classified subject violates the security classification
    INAPPLICABLE = "INAPPLICABLE"  # the security record does not classify the subject (unscoped)


def _default_behavior_ref(kind: SecurityKind) -> str:
    """The abstract RL-F2 security-evaluate reference for ``kind`` (APPLICATION-013 §7)."""
    concern = KIND_RUNTIME_CONCERN[kind]
    return f"ENG-005:RL-F2:runtime.security-evaluate.{concern}"


def _require_reference(name: str, value: Any) -> str:
    """Require ``value`` to be a non-empty ENG-005 reference string (by reference)."""
    if not isinstance(value, str) or not value.strip():
        raise SecurityError(f"{name} must be a non-empty ENG-005 reference (AMR-08/09/14/§7)")
    return value


def _require_ref_tuple(name: str, values: Any, *, minimum: int = 0) -> tuple[str, ...]:
    """Require ``values`` to be a tuple of non-empty ENG-005 reference strings (≥ ``minimum``)."""
    if not isinstance(values, tuple):
        raise SecurityError(f"{name} must be a tuple of ENG-005 references (AMR-08/09/14)")
    for v in values:
        if not isinstance(v, str) or not v.strip():
            raise SecurityError(
                f"{name} entries must be non-empty ENG-005 references (AMR-08/09/14)"
            )
    if len(values) < minimum:
        raise SecurityError(f"{name} must declare at least {minimum} ENG-005 reference (SEC-K2)")
    return values


def _contains_marker(value: str, markers: tuple[str, ...]) -> bool:
    """True iff ``value`` (case-insensitively) contains any of ``markers``."""
    haystack = value.lower()
    return any(marker in haystack for marker in markers)


@dataclass(frozen=True, slots=True)
class SecurityAssessment:
    """A recorded, immutable classification judgment produced by *evaluating* a security record.

    An assessment **records** a verdict against a classified construct's ENG-002 object; it
    enacts nothing, grants nothing, issues no credential, encrypts nothing, and mutates no state
    (UAL-14 / SEC-C1 / SEC-C2). The judgment value itself is supplied by the frozen RUNTIME
    policy concern (RUNTIME-010, by reference; §7) — this construct only records it
    deterministically.
    """

    security_id: str
    subject_ref: str
    verdict: SecurityVerdict
    kind: str

    def enacts_nothing(self) -> bool:
        """UAL-14 / SEC-C1 — an assessment is a record; it enacts nothing (structurally true)."""
        return True

    def to_dict(self) -> dict[str, Any]:
        """A deterministic, serializable projection of the recorded classification judgment."""
        return {
            "assessment_format": "ucos-application-security-assessment/1.0.0",
            "security_id": self.security_id,
            "subject_ref": self.subject_ref,
            "verdict": self.verdict.value,
            "kind": self.kind,
            "enacts": "none",
        }


@dataclass(frozen=True, slots=True)
class Security:
    """AMC-09 — an immutable, typed, identified, decidable, non-enforcing security record.

    Fields:
        type_tag:        the ENG-004 Type of the security record (decidable, non-empty) — SEC-01.
        kind:            the AXH-09 classification (AXC-04): Authentication / Authorization /
                         Confidentiality / Integrity record.
        subject_refs:    tuple of ENG-005 references to the Application/Feature/Module/Interaction
                         boundaries this record classifies — the boundaries **secured-by** this
                         record (AMR-08; AOR-08; the declared classified boundary; reference-only;
                         SEC-07 / SEC-K2). Must be non-empty.
        governance_refs: tuple of ENG-005 references to the declarative Governance
                         security-policy records that *inform* this classification (AMR-09
                         governed-by; AOR-09; reference-only). May be empty.
        data_refs:       tuple of DF-2/DATA-014-represented data references the record
                         **presents** (AMR-14 presents-data; AOR-14; SEC-06/SEC-C4). May be empty
                         (identity/access records need not present data).
        behavior_ref:    the ENG-005 reference to the RUNTIME policy concern the evaluation
                         behaves-as (§7 security-evaluate; RL-F2; RUNTIME-010). If omitted it
                         defaults to the kind-appropriate RUNTIME policy reference.
        state:           the AOS-01…06 lifecycle state (forward-only) — UAL-12 (default DEFINED).
    """

    type_tag: str
    kind: SecurityKind
    subject_refs: tuple[str, ...]
    governance_refs: tuple[str, ...] = field(default=())
    data_refs: tuple[str, ...] = field(default=())
    behavior_ref: str = ""
    state: SecurityState = SecurityState.DEFINED

    def __post_init__(self) -> None:
        # SEC-K1 / UAL-03 / SEC-01 — typed (ENG-004): a decidable, non-empty type tag.
        if not isinstance(self.type_tag, str) or not self.type_tag.strip():
            raise SecurityError(
                "security record must be typed with a non-empty ENG-004 type_tag (UAL-03 / SEC-01)"
            )
        # AXH-09 / AXC-04 — classified by exactly one Security kind.
        if not isinstance(self.kind, SecurityKind):
            raise SecurityError("security kind must be an AXH-09 SecurityKind (AXC-04)")
        # AMR-08 / AOR-08 / SEC-07 / SEC-K2 — classifies at least one declared boundary.
        _require_ref_tuple("subject_refs", self.subject_refs, minimum=1)
        # AMR-09 / AOR-09 — the informing Governance records (governed-by), by reference (opt).
        _require_ref_tuple("governance_refs", self.governance_refs)
        # AMR-14 / AOR-14 / SEC-06 — confidentiality/integrity data by reference (may be empty).
        _require_ref_tuple("data_refs", self.data_refs)
        # §7 — derive the kind-appropriate RUNTIME policy behavior reference if omitted.
        if not (isinstance(self.behavior_ref, str) and self.behavior_ref.strip()):
            object.__setattr__(self, "behavior_ref", _default_behavior_ref(self.kind))
        # §7 / AMK-05 — the security-evaluate behavior binds the RUNTIME policy concern by ref.
        _require_reference("behavior_ref", self.behavior_ref)
        # V5 / UAL-12 — a valid lifecycle state.
        if not isinstance(self.state, SecurityState):
            raise SecurityError(
                "security state must be an AOS-01…06 SecurityState (UAL-12)"
            )

    # -- identity (ENG-001) borne by object (ENG-002), by reference ------------

    def canonical_core(self) -> dict[str, Any]:
        """The canonical, hashable core of the security record (its identity-defining tuple).

        Subject/governance/data references are canonically sorted (they are reference sets), so
        two records classifying the same boundaries in different declaration order bear the same
        ENG-001 identity. The lifecycle ``state`` is **not** part of identity.
        """
        return {
            "meta_class": SECURITY_META_CLASS,
            "type_tag": self.type_tag,
            "kind": self.kind.value,
            "facet": self.facet(),
            "subject_refs": sorted(self.subject_refs),
            "governance_refs": sorted(self.governance_refs),
            "data_refs": sorted(self.data_refs),
            "behavior_ref": self.behavior_ref,
        }

    @property
    def value_digest(self) -> str:
        """The EC-1 content hash of the security core — the ENG-003 value fingerprint."""
        return content_hash(self.canonical_core())

    @property
    def security_id(self) -> str:
        """The deterministic ENG-001 identity of the security record (borne by this object).

        Derived through the CERTIFIED EC-1 ``content_hash`` (UAL-04 — no second identity
        scheme): identical (type, kind, refs) always yields the identical id, so identity is
        reproducible and byte-stable (determinism, VC-4).
        """
        return f"{SECURITY_ID_PREFIX}-{self.type_tag}-{self.value_digest[:16]}"

    @property
    def self_ref(self) -> str:
        """The ENG-005 self-reference form of this record (for self-founding detection)."""
        return f"ENG-005:AOE-09:{self.type_tag}"

    # -- meta-model participation (APPLICATION-005/013) ------------------------

    @property
    def meta_class(self) -> str:
        """V1 — the single meta-class this construct instantiates (AMC-09)."""
        return SECURITY_META_CLASS

    def meta_relationships(self) -> tuple[str, ...]:
        """V2 — the AMR-01…14 relationships the security record participates in."""
        return SECURITY_RELATIONSHIPS

    def facet(self) -> str:
        """AXH-09 — the security facet the kind classifies (authn/authz/conf/integrity)."""
        return SECURITY_FACETS[self.kind]

    # -- founding acyclicity (V4 / AMK-03) -------------------------------------

    def is_founding_acyclic(self) -> bool:
        """V4 / AMK-03 / AMI-04 — the founding graph is acyclic (materially proven).

        A Security record participates in **no** founding relationship — its relationships
        (AMR-08 secured-by, AMR-09 governed-by, AMR-10 identified-by, AMR-14 presents-data) are
        all reference-only — so its founding graph is empty and therefore trivially acyclic,
        exactly as the State used no founding edge (V4 PASS vacuously). Canonical encodability
        proves the core is well-formed; the no-self-founding guard proves no reference names the
        record itself.
        """
        try:
            canonical_json(self.canonical_core())
        except (TypeError, ValueError):  # pragma: no cover - blocked at construction
            return False
        return self.no_self_founding()

    def no_self_founding(self) -> bool:
        """AMK-03 — no reference founds the security record on itself (no self-founding cycle)."""
        me = self.self_ref
        return all(
            ref != me
            for ref in (
                self.behavior_ref,
                *self.subject_refs,
                *self.governance_refs,
                *self.data_refs,
            )
        )

    def participates_in_founding_edge(self) -> bool:
        """AMK-03 — a Security record participates in no founding edge (reference-only)."""
        return False

    # -- security-specific obligations -----------------------------------------

    def classifies_boundary(self) -> bool:
        """AMR-08 / AOR-08 / SEC-07 / SEC-K2 — the record classifies ≥1 declared boundary."""
        return bool(self.subject_refs) and all(
            isinstance(r, str) and bool(r.strip()) for r in self.subject_refs
        )

    def secured_boundaries(self) -> tuple[str, ...]:
        """AMR-08 — the boundaries secured-by this record (the classified subjects)."""
        return self.subject_refs

    def evaluative_nonenforcing(self) -> bool:
        """UAL-14 / SEC-03 / SEC-04 / SEC-C1 / SEC-C2 — the record is evaluative, enacts nothing.

        THE governing law of the Security concern: a security record *classifies*
        authentication/authorization/confidentiality/integrity concerns and its evaluation
        *records a judgment* while *conferring no authority* and *granting no access*. It is
        structurally non-enforcing — the construct holds only references and a type; it can grant
        nothing, issue no credential, encrypt nothing, and mutate no state.
        """
        return not self.confers_authority() and not self.grants_access()

    def binds_runtime_policy(self) -> bool:
        """AMK-05 / §7 / UAL-10 — the security-evaluate behavior binds RL-F2 by reference.

        The evaluation behaves-as the frozen RUNTIME policy concern (RUNTIME-010) by ENG-005
        reference; the reference must be non-empty and name no concrete security technology.
        """
        return bool(self.behavior_ref.strip()) and not _contains_marker(
            self.behavior_ref, _TECHNOLOGY_MARKERS
        )

    def behavior_by_reference(self) -> bool:
        """§7 / UAL-10 — the evaluation binds RL-F2 by a non-empty ENG-005 reference."""
        return bool(self.behavior_ref.strip())

    def data_by_reference(self) -> bool:
        """AMR-14 / AOR-14 / UAL-13 — every data ref is a non-empty DF-2/DATA-014 reference."""
        return all(isinstance(r, str) and bool(r.strip()) for r in self.data_refs)

    def data_security_reuse(self) -> bool:
        """SEC-06 / SEC-C4 — confidentiality/integrity data reuses DATA-014 by reference.

        Structurally true: confidentiality/integrity data references are DF-2 ids resolved
        against the DATA-014 data-security architecture; this construct never redefines a
        data-security concept. Kinds that present no data (authentication/authorization)
        trivially conform.
        """
        return self.data_by_reference()

    def governed_by_reference(self) -> bool:
        """AMR-09 / AOR-09 — every informing-governance reference is a non-empty ENG-005 ref."""
        return all(isinstance(r, str) and bool(r.strip()) for r in self.governance_refs)

    @property
    def bears_data(self) -> bool:
        """True iff this security kind presents confidentiality/integrity DF-2 data."""
        return self.kind in DATA_BEARING_KINDS

    @property
    def precedence(self) -> int:
        """The deterministic evaluation-precedence rank of the record (AXH-09 order).

        A *lower* rank is evaluated first. This is a decidable, evaluative ordering only
        (UAL-14 / SEC-03): it enacts nothing and confers nothing — it records the deterministic
        order in which classification facets are considered when several apply to one boundary.
        """
        return KIND_PRECEDENCE[self.kind]

    def precedence_decidable(self) -> bool:
        """SEC-08 — the record's evaluation precedence is decidable from its kind."""
        return self.kind in KIND_PRECEDENCE

    def classifies(self, subject_ref: str) -> bool:
        """SEC-07 — True iff ``subject_ref`` is within this record's classified boundary."""
        return isinstance(subject_ref, str) and subject_ref in self.subject_refs

    def references_resolve(self) -> bool:
        """AOI-03 / AMK-05/07 — every ENG-005 reference is a non-empty resolvable id."""
        return all(
            isinstance(ref, str) and bool(ref.strip())
            for ref in (
                self.behavior_ref,
                *self.subject_refs,
                *self.governance_refs,
                *self.data_refs,
            )
        ) and self.no_self_founding()

    def uses_new_connection_construct(self) -> bool:
        """SEC-C4 analog — True iff any link is not a plain ENG-005 reference string.

        A security record introduces no new connection construct: every subject/governance/
        data/behavior link is an ENG-005 reference (a non-empty string). This is False for a
        well-formed record.
        """
        links = (
            *self.subject_refs,
            *self.governance_refs,
            *self.data_refs,
            self.behavior_ref,
        )
        return not all(isinstance(link, str) and bool(link.strip()) for link in links)

    # -- evaluative classification → recorded judgment (SEC-C1 / AOV-09) -------

    def record_assessment(self, subject_ref: str, satisfied: bool) -> SecurityAssessment:
        """Record a classification judgment for ``subject_ref`` — evaluative, non-enforcing.

        The *act* of deciding whether the boundary satisfies the security classification is the
        RUNTIME policy concern (RUNTIME-010, by reference; §7) — supplied here as ``satisfied``.
        This method only **records** the resulting verdict against the subject's ENG-002 object;
        it enacts nothing, grants nothing, issues no credential, and mutates no state (UAL-14 /
        SEC-C1 / SEC-C2). A subject outside the declared classified boundary records
        ``INAPPLICABLE``.
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

    # -- non-constitutiveness (UAL-15 / SEC-04/05/09) --------------------------

    def confers_authority(self) -> bool:
        """UAL-14/15 / SEC-09 / C7 — a security record confers no authority (structurally none)."""
        return False

    def grants_access(self) -> bool:
        """UAL-14 / SEC-04 / SEC-C2 — a security record grants no access (structurally none)."""
        return False

    def selects_technology(self) -> bool:
        """UAL-15 / SEC-05 / SEC-C3 / C7 — True iff the record names crypto/IAM/technology.

        Covers cryptography, identity providers, IAM/key stores, credential stores,
        access-control engines, protocols, frameworks, transports, or vendors across the whole
        security core.
        """
        haystack = canonical_json(self.canonical_core()).lower()
        return any(marker in haystack for marker in _TECHNOLOGY_MARKERS)

    def embeds_secret(self) -> bool:
        """UAL-15 / SEC-09 / RR-07 / C7 — True iff the record appears to embed a secret."""
        haystack = canonical_json(self.canonical_core()).lower()
        return any(marker in haystack for marker in _SECRET_MARKERS)

    def redefines_foundation(self) -> bool:
        """UAL-02 / AMI-05 / VC-5 — a security record redefines no frozen primitive (reuse-only)."""
        return False

    # -- lifecycle (UAL-12, forward-only) --------------------------------------

    def transition(self, to_state: SecurityState) -> Security:
        """Return a new security record advanced to ``to_state`` (forward-only; UAL-12).

        Raises:
            SecurityError: on a backward or in-place-reversing transition.
        """
        if not isinstance(to_state, SecurityState):
            raise SecurityError("target state must be an AOS-01…06 SecurityState (UAL-12)")
        here = LIFECYCLE_ORDER.index(self.state)
        there = LIFECYCLE_ORDER.index(to_state)
        if there < here:
            raise SecurityError(
                f"lifecycle is forward-only (UAL-12): "
                f"{self.state.value} → {to_state.value} is backward"
            )
        return replace(self, state=to_state)

    # -- serialization ----------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """A deterministic, serializable projection of the security record."""
        return {
            "security_id": self.security_id,
            "meta_class": self.meta_class,
            "type_tag": self.type_tag,
            "kind": self.kind.value,
            "facet": self.facet(),
            "subject_refs": sorted(self.subject_refs),
            "governance_refs": sorted(self.governance_refs),
            "data_refs": sorted(self.data_refs),
            "behavior_ref": self.behavior_ref,
            "value_digest": self.value_digest,
            "state": self.state.value,
            "precedence": self.precedence,
            "bears_data": self.bears_data,
            "runtime_concern": KIND_RUNTIME_CONCERN[self.kind],
            "is_founding": self.participates_in_founding_edge(),
            "founding_acyclic": self.is_founding_acyclic(),
            "evaluative_nonenforcing": self.evaluative_nonenforcing(),
            "binds_runtime_policy": self.binds_runtime_policy(),
            "relationships": list(self.meta_relationships()),
            "substrate_refs": list(SUBSTRATE_REFS),
        }


@dataclass(frozen=True, slots=True)
class SecurityCoverage:
    """A recorded, evaluative report of which AXH-09 facets classify a given boundary.

    Coverage is an **evaluative record** (APPLICATION-013 §12 posture/coverage map): for one
    classified boundary it records which of the four AXH-09 security facets are present and which
    are absent. Recording coverage enacts nothing and confers no authority (UAL-14 / SEC-03); an
    absent facet is a *recorded observation*, never an enforced requirement.
    """

    subject_ref: str
    facets_present: tuple[str, ...]
    facets_absent: tuple[str, ...]

    @property
    def fully_covered(self) -> bool:
        """True iff every AXH-09 facet classifies this boundary (no absent facet)."""
        return not self.facets_absent

    def to_dict(self) -> dict[str, Any]:
        return {
            "coverage_format": "ucos-application-security-coverage/1.0.0",
            "subject_ref": self.subject_ref,
            "facets_present": list(self.facets_present),
            "facets_absent": list(self.facets_absent),
            "fully_covered": self.fully_covered,
            "assessment": "evaluative record; records only, enacts nothing",
        }


def assess_security_coverage(
    security_records: tuple[Security, ...],
) -> tuple[SecurityCoverage, ...]:
    """Report AXH-09 classification coverage per boundary — evaluative, non-enforcing.

    For each classified boundary (AMR-08 subject) across ``security_records``, records which of
    the four AXH-09 facets (Authentication / Authorization / Confidentiality / Integrity) classify
    it and which are absent. The report is deterministic and records only; it grants nothing,
    blocks nothing, and requires nothing (APPLICATION-013 §12 / UAL-14 / SEC-03). Facets are
    ordered by their AXH-09 declaration order (via :data:`KIND_PRECEDENCE`).
    """
    all_facets = tuple(k.value for k in sorted(SecurityKind, key=lambda k: KIND_PRECEDENCE[k]))
    present: dict[str, set[str]] = {}
    for record in security_records:
        for subject_ref in record.subject_refs:
            present.setdefault(subject_ref, set()).add(record.kind.value)

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
    governance_refs: tuple[str, ...] = (),
    data_refs: tuple[str, ...] = (),
    behavior_ref: str = "",
    state: SecurityState = SecurityState.DEFINED,
) -> Security:
    """Construct a well-formed :class:`Security` record (fail-closed factory)."""
    return Security(
        type_tag=type_tag,
        kind=kind,
        subject_refs=subject_refs,
        governance_refs=governance_refs,
        data_refs=data_refs,
        behavior_ref=behavior_ref,
        state=state,
    )


__all__ = [
    "SECURITY_ID_PREFIX",
    "FOUNDATION_REUSE",
    "SecurityError",
    "SecurityVerdict",
    "SecurityAssessment",
    "Security",
    "SecurityCoverage",
    "assess_security_coverage",
    "make_security",
]
