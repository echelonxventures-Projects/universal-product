"""EC3-B10-U09 — The Universal Security construct (DMC-10).

Realizes the meta-model construct **DMC-10 Security-Object** (DATA-005 §2; DATA-014 §3):

    the **representation-level, decidable, evaluative classification of a data construct's
    sensitivity, confidentiality, and integrity requirements** — recorded as a
    classification against the construct (the ontology root DOE-10), classified by DXH-10
    (Classification-Label / Confidentiality-Record / Integrity-Record). A security object
    is an ENG-002 Object classified by an ENG-004 Type, recorded against a data construct
    via ``classifies`` (DMR-09) and binding integrity-check evaluation *by reference* to
    the frozen RUNTIME policy concern (DMR-11). Data security is neither the data it
    classifies nor an access-control/encryption mechanism — it is a **representation-level
    classification record that enacts nothing**; enforcement is a downstream concern
    consumed by reference.

The construct is **additive over the CERTIFIED EC-1 foundation *and* the CERTIFIED
DMC-02 Entity**, reusing both *by reference* (UDL-02 / DMI-05):

* Identity is derived through the EC-1 certified deterministic encoding
  (:func:`engine.certification.contracts.canonical_json` /
  :func:`~engine.certification.contracts.content_hash`) — no second identity scheme.
* The classified subject (DMR-09 ``classifies``) is a **reference to a CERTIFIED data
  construct** (id + structural digest + name/type + meta-class), **never owned,
  embedded, or copied** (DZA-C3 by record; DMX-02 non-absorbing).
* Integrity-check evaluation is a **RUNTIME policy reference** only (``behaves-as``,
  DMR-11 / DZA-06) — no cipher, key store, access-control point, or DLP engine is defined.

**No cryptography, key management, access-control/IAM, DLP, masking, or security product
or vendor is selected** (UDL-14 / DZA-07 / DZA-C5 / DZA-K5) — enforced fail-closed by a
technology-marker scan over the whole construct. A security object **grants no access and
confers no authority** (DZA-01 / DZA-09 / DZA-K5): this is the material exercise of
UDL-14 Security as an Evaluative Facet — security *is* a classification record that enacts
nothing.

A :class:`SecurityObject` is *immutable* (frozen — ENG-002 objecthood), *typed*
(ENG-004, DZA-K1/UDL-03), *identified* (ENG-001, DZA-K1/UDL-04), *subject-bound*
(``classifies`` a CERTIFIED construct by reference — DMR-09), *dimensioned and evaluative*
(DZA-01/02/K2), *recorded* (DZA-04/K4), *versioned*, and holds a *forward-only lifecycle
state* (DOS-01…05, UDL-12). Constructing a :class:`SecurityObject` enforces
DZA-K1/K2/K3/K4/K5, the classification rules DZA-C1/C2/C3/C4/C5, and UDL-14/03/04/05
**fail-closed**: an ill-formed, enforcing, access-granting, or authority-conferring
security object cannot exist.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any

# --- DMC-02 reuse by reference (UDL-02) — never redefined -------------------------
from data.entity import Entity
from data.security_meta import (
    DIMENSION_FOR_KIND,
    LEVEL_MAX,
    LEVEL_MIN,
    LIFECYCLE_ORDER,
    SECURITY_DIMENSIONS,
    SECURITY_META_CLASS,
    SECURITY_RELATIONSHIPS,
    SECURITY_SUBSTRATE_REFS,
    SecurityKind,
    SecurityState,
    SecurityVerdict,
)

# --- EC-1 reuse by reference (UDL-02 / DMI-05) — imported, never redefined --------
from engine.certification.contracts import canonical_json, content_hash

#: The deterministic id prefix for a realized Security object (mirrors EC-1 UCOS-<K>-<hex>).
SECURITY_ID_PREFIX = "UCOS-SECURITY"

#: The reference prefix a security object presents to bind RUNTIME policy evaluation
#: (DMR-11 / DZA-06 / DOB-06 evaluate) — declarative, non-enforcing.
POLICY_REF_PREFIX = "UCOS-POLICY-REF"

#: The prefix of a CERTIFIED data-construct identity (the DMR-09 ``classifies`` target).
CERTIFIED_ID_PREFIX = "UCOS-"

#: The map of EC-1 / DMC-02 primitives this construct reuses *by reference* (never
#: redefined). Recorded for the reuse-integrity check (UDL-02 / DMI-05 / VC-5).
REUSE_REFS: dict[str, str] = {
    "ENG-001": "engine.certification.contracts.content_hash (deterministic identity derivation)",
    "ENG-002": "python frozen object (immutable objecthood bearing the classification record)",
    "ENG-004": "data.security_meta.SecurityKind + type_tag (ENG-004 typing discipline)",
    "ENG-005": "classified-construct + RUNTIME policy identity references (DMR-09/11)",
    "DMC-02": "data.entity.Entity — a CERTIFIED classifies target (DMR-09); referenced only",
    "RL-F2": "RUNTIME policy — integrity-check evaluation bound by reference (DMR-11 / DZA-06)",
}

#: Conservative secret markers used to enforce UDL-15 / DZA-09 / RR-07 (embed no secret).
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

#: Conservative security-technology markers used to enforce **UDL-14 / DZA-07 / DZA-C5 /
#: DZA-K5** (select no cryptography, key-management, access-control/IAM, DLP, masking, or
#: security product/vendor). A security object naming any of these is rejected fail-closed
#: — security is a decidable, evaluative, non-enforcing classification record only. This
#: is the material exercise of UDL-14 (Security as an Evaluative Facet), DZA-07 (No
#: Cryptography Selection), and DZA-C5. Markers are chosen to avoid collision with the
#: hexadecimal alphabet used by content digests (they contain characters outside 0-9a-f).
_TECH_MARKERS: tuple[str, ...] = (
    "cryptography",
    "encryption",
    "aes-256",
    "rsa-2048",
    "openssl",
    "cipher",
    "hashicorp vault",
    "key management",
    "keystore",
    "kms",
    "tls",
    "mtls",
    "oauth",
    "saml",
    "ldap",
    "kerberos",
    "iam",
    "rbac",
    "acl",
    "dlp",
    "data loss prevention",
    "access control list",
    "tokenization",
    "masking engine",
    "certificate authority",
    "bcrypt",
    "argon2",
    "pbkdf2",
    "okta",
    "auth0",
    "keycloak",
    "cyberark",
)


def policy_ref_for(predicate: str) -> str:
    """The reference a security object presents to bind RUNTIME policy (DMR-11 / DZA-06).

    A security object's integrity-check evaluation is a *reference* to the frozen RL-F2
    policy concern (DOB-06 evaluate), which is declarative and non-enforcing by
    construction — never a redefined access-control point or cipher.
    """
    return f"{POLICY_REF_PREFIX}:{predicate}"


class SecurityError(ValueError):
    """Raised when a value cannot be realized as a well-formed :class:`SecurityObject`.

    A :class:`SecurityObject` is fail-closed (TRACK-001): an ill-formed, enforcing,
    access-granting, authority-conferring, or technology-bound security record is rejected
    at construction rather than admitted as an invalid or constitutive object.
    """


@dataclass(frozen=True, slots=True)
class ClassifiedConstructRef:
    """A reference to a CERTIFIED data construct a security object ``classifies`` (DMR-09).

    Records **only** the classified construct's identity, structural fingerprint, name,
    type, and meta-class — never its implementation — so the security object references,
    and never owns or absorbs, the construct it classifies (DMX-02 non-absorbing; DZA-C3
    by record; UDL-02 reuse-by-reference).
    """

    construct_id: str
    structure_digest: str
    name: str
    type_tag: str
    meta_class: str

    @classmethod
    def from_entity(cls, entity: Entity) -> ClassifiedConstructRef:
        """Project a CERTIFIED :class:`~data.entity.Entity` into a classified-construct ref."""
        if not isinstance(entity, Entity):
            raise SecurityError("a security object classifies a data construct (DMR-09)")
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
            "binding": "DMR-09:classifies",
            "owned": False,  # DZA-C3 — classified by record, never owned
            "absorbing": False,  # DMX-02 — referenced, not absorbed
        }


@dataclass(frozen=True, slots=True)
class ClassificationEntry:
    """A single recorded, decidable security classification along one dimension (DZA-C1).

    Purely evaluative: it *records* a decidable verdict and a bounded classification level
    for the classified dimension; it grants nothing and mutates nothing (DZA-01 / DZA-C2).
    """

    dimension: str
    satisfied: bool
    level: int = LEVEL_MIN
    note: str = ""

    def __post_init__(self) -> None:
        if not isinstance(self.dimension, str) or self.dimension not in SECURITY_DIMENSIONS:
            raise SecurityError(
                "a classification names a decidable security dimension "
                "(sensitivity/confidentiality/integrity) — DZA-02"
            )
        if not isinstance(self.satisfied, bool):
            raise SecurityError("a classification records a decidable verdict (DZA-C1)")
        if isinstance(self.level, bool) or not isinstance(self.level, int):
            raise SecurityError("a classification records an integer level ordinal (DZA-C1)")
        if not (LEVEL_MIN <= self.level <= LEVEL_MAX):
            raise SecurityError(
                f"a classification level is a bounded ordinal in [{LEVEL_MIN}, {LEVEL_MAX}] "
                f"(DZA-C1 / DZA-05)"
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "dimension": self.dimension,
            "satisfied": self.satisfied,
            "level": self.level,
            "note": self.note,
        }


@dataclass(frozen=True, slots=True)
class SecurityObject:
    """DMC-10 — an immutable, evaluative, non-enforcing, non-authoritative security record.

    Fields:
        name:            the explicit security-object name (part of identity).
        type_tag:        the ENG-004 Type of the object (DZA-K1; UDL-03).
        kind:            the DXH-10 classification (Classification-Label / Confidentiality-
                         Record / Integrity-Record; DMR-09 classified-by).
        classified_ref:  the CERTIFIED construct the object ``classifies`` (DMR-09; DZA-C3
                         by record, non-owning).
        policy_ref:      the RUNTIME policy reference integrity-check evaluation binds to
                         (DMR-11 / DZA-06 / DZA-K3). A reference obligation only — no
                         cipher/access-control point is defined.
        classifications: the recorded per-dimension classifications (DZA-C1). Required
                         non-empty; every classification is along the kind's single facet
                         (DXC-02 / DZA-02).
        verdict:         the recorded classification judgment (DZA-C1 / DOV-08).
        state:           the DOS-01…05 forward-only lifecycle state (UDL-12).
        version:         the object version (append-only re-classification; DZA-C4 /
                         UDL-12/15).
        supersedes:      the id of a superseded security object (DZA-C4 append-only).
    """

    name: str
    type_tag: str
    kind: SecurityKind
    classified_ref: ClassifiedConstructRef
    policy_ref: str
    classifications: tuple[ClassificationEntry, ...] = ()
    verdict: SecurityVerdict = SecurityVerdict.PASS
    state: SecurityState = SecurityState.DEFINED
    version: str = "1.0.0"
    supersedes: str = ""

    def __post_init__(self) -> None:
        # explicit, decidable name.
        if not isinstance(self.name, str) or not self.name.strip():
            raise SecurityError("security object must have an explicit name")
        # DZA-K1 / DMK-01 / UDL-03 — typed (ENG-004): a decidable, non-empty type.
        if not isinstance(self.type_tag, str) or not self.type_tag.strip():
            raise SecurityError("security object must be typed with an ENG-004 type_tag (DZA-K1)")
        # DXH-10 / DMR-09 — classified by exactly one security kind.
        if not isinstance(self.kind, SecurityKind):
            raise SecurityError("security kind must be a DXH-10 SecurityKind (DMR-09)")
        # DMR-09 — the classified subject is a reference to a CERTIFIED construct.
        if not isinstance(self.classified_ref, ClassifiedConstructRef):
            raise SecurityError("security classifies a CERTIFIED construct by reference (DMR-09)")
        if not self.classified_ref.construct_id.startswith(CERTIFIED_ID_PREFIX):
            raise SecurityError("the classified subject is not a CERTIFIED construct id (DMR-09)")
        if len(self.classified_ref.structure_digest) != 64 or any(
            c not in "0123456789abcdef" for c in self.classified_ref.structure_digest
        ):
            raise SecurityError("the classified subject carries no structural digest (UDL-06)")
        # DMR-11 / DZA-06 / DZA-K3 — evaluation binds a RUNTIME policy reference.
        if not isinstance(self.policy_ref, str) or not self.policy_ref.startswith(
            f"{POLICY_REF_PREFIX}:"
        ):
            raise SecurityError(
                "integrity-check must bind a RUNTIME policy reference (DMR-11 / DZA-K3)"
            )
        # DZA-C1 / DZA-02 — records ≥1 decidable classification along the kind's facet.
        if not isinstance(self.classifications, tuple):
            raise SecurityError("classifications must be a tuple of ClassificationEntry (DZA-C1)")
        if not self.classifications:
            raise SecurityError("a security object records ≥1 classification (DZA-C1)")
        facet = DIMENSION_FOR_KIND[self.kind]
        for entry in self.classifications:
            if not isinstance(entry, ClassificationEntry):
                raise SecurityError("classifications are ClassificationEntry records (DZA-C1)")
            if entry.dimension != facet:
                raise SecurityError(
                    f"a {self.kind.value} classifies only the '{facet}' dimension "
                    f"(single-facet, DXC-02 / DZA-02)"
                )
        # DZA-C1 / DOV-08 — records a decidable verdict.
        if not isinstance(self.verdict, SecurityVerdict):
            raise SecurityError("verdict must be a decidable SecurityVerdict (DZA-C1)")
        # V5 / UDL-12 — a valid forward-only lifecycle state.
        if not isinstance(self.state, SecurityState):
            raise SecurityError("security state must be a DOS-01…05 state (UDL-12)")
        # DZA-08 — a security object records an explicit, non-empty version.
        if not isinstance(self.version, str) or not self.version.strip():
            raise SecurityError("security object must record an explicit version (DZA-08)")
        if not isinstance(self.supersedes, str):
            raise SecurityError("security supersedes reference must be a string (DZA-C4)")
        # UDL-14 / DZA-07 / DZA-C5 / DZA-K5 — names no cryptography/controls tech (material).
        if self._scan_technology():
            raise SecurityError(
                "security names a cryptography/access-control/DLP technology or vendor "
                "(UDL-14 / DZA-07 / DZA-C5 / DZA-K5)"
            )

    # -- technology-neutrality (UDL-14, material) ------------------------------

    def _scan_technology(self) -> bool:
        """True iff any technology marker appears in the object's declared surface."""
        haystack = canonical_json(self.canonical_core()).lower()
        return any(marker in haystack for marker in _TECH_MARKERS)

    def names_technology(self) -> bool:
        """UDL-14 / DZA-07 / DZA-K5 / C6 — True iff the object names a security tech."""
        return self._scan_technology()

    # -- identity (ENG-001) borne by object (ENG-002), by reference ------------

    def canonical_core(self) -> dict[str, Any]:
        """The canonical, hashable core of the object (structure + classified reference)."""
        return {
            "meta_class": SECURITY_META_CLASS,
            "name": self.name,
            "type_tag": self.type_tag,
            "kind": self.kind.value,
            "classified_ref": {
                "construct_id": self.classified_ref.construct_id,
                "structure_digest": self.classified_ref.structure_digest,
                "name": self.classified_ref.name,
                "type_tag": self.classified_ref.type_tag,
                "meta_class": self.classified_ref.meta_class,
            },
            "policy_ref": self.policy_ref,
            "classifications": [
                {
                    "dimension": c.dimension,
                    "satisfied": c.satisfied,
                    "level": c.level,
                    "note": c.note,
                }
                for c in self.classifications
            ],
            "verdict": self.verdict.value,
            "version": self.version,
            "supersedes": self.supersedes,
        }

    @property
    def structure_digest(self) -> str:
        """The EC-1 content hash of the object core — its structural fingerprint."""
        return content_hash(self.canonical_core())

    @property
    def security_id(self) -> str:
        """The deterministic ENG-001 identity of the object (borne by this object).

        Derived through the CERTIFIED EC-1 ``content_hash`` (UDL-04 — no second identity
        scheme): an identical object always yields the identical id, so identity is
        reproducible and byte-stable (determinism, VC-4).
        """
        return f"{SECURITY_ID_PREFIX}-{self.name}-{self.structure_digest[:16]}"

    # -- meta-model participation (DATA-005 / DATA-014) ------------------------

    @property
    def meta_class(self) -> str:
        """V1 — the single meta-class this construct instantiates (DMC-10)."""
        return SECURITY_META_CLASS

    def meta_relationships(self) -> tuple[str, ...]:
        """V2 — the DMR-01…12 relationships the object participates in."""
        return SECURITY_RELATIONSHIPS

    def classified_construct_id(self) -> str:
        """The identity of the construct this object classifies (DMR-09; by reference)."""
        return self.classified_ref.construct_id

    def classified_dimension(self) -> str:
        """The single security dimension this object classifies (DXC-02 / DZA-02)."""
        return DIMENSION_FOR_KIND[self.kind]

    def classified_dimensions(self) -> tuple[str, ...]:
        """The distinct dimensions recorded across the classifications (DZA-02)."""
        return tuple(dict.fromkeys(c.dimension for c in self.classifications))

    # -- security property predicates ------------------------------------------

    def is_evaluative(self) -> bool:
        """DZA-01 / DZA-K2 — security is a decidable, evaluative classification."""
        return True

    def is_dimensioned(self) -> bool:
        """DZA-02 — the object classifies a decidable security dimension."""
        return all(c.dimension in SECURITY_DIMENSIONS for c in self.classifications)

    def enforces(self) -> bool:
        """DZA-01 / DZA-C2 / UDL-14 — security classifies and records; it enforces nothing."""
        return False

    def grants_access(self) -> bool:
        """DZA-01 / DZA-C2 / DZA-K5 — security grants no access (structurally none)."""
        return False

    def is_recorded(self) -> bool:
        """DZA-04 / DZA-K4 — the classification is recorded against an ENG-002 object (DOV-08)."""
        return True

    def binds_policy_by_reference(self) -> bool:
        """DMR-11 / DZA-06 / DZA-K3 — integrity-check binds a RUNTIME policy reference only."""
        return self.policy_ref.startswith(f"{POLICY_REF_PREFIX}:")

    def enforcement_by_reference(self) -> bool:
        """DZA-03 / DZA-C3 — any enforcement obligation is expressed as a downstream reference.

        The object references RUNTIME policy for integrity-check evaluation and enforces
        nothing itself; enforcement of access/encryption is a downstream concern consumed
        by reference, never defined here.
        """
        return self.binds_policy_by_reference() and not self.enforces()

    def records_classification(self) -> bool:
        """DZA-C1 — the object decidably records ≥1 per-dimension classification."""
        return bool(self.classifications)

    def gap_report(self) -> tuple[str, ...]:
        """DZA-C1 — the dimensions recorded as deficient/unclassified (record-only).

        Security *records* classification deficiencies; it does not itself remediate,
        enforce, or grant access (DZA-01 / DZA-C2).
        """
        return tuple(c.dimension for c in self.classifications if not c.satisfied)

    def passes(self) -> bool:
        """Whether the recorded classifications show no deficiency (evaluative only)."""
        return not self.gap_report()

    def is_classified(self) -> bool:
        """DXH-10 — the object is classified by exactly one security kind."""
        return isinstance(self.kind, SecurityKind)

    def is_founding_acyclic(self) -> bool:
        """V4 / DMK-03 — the founding/classification graph is acyclic.

        The object's founding references (``classifies`` → construct, ``behaves-as`` →
        RUNTIME policy) are recorded by *identity reference*; none may reference the object
        itself, so the founding graph is a DAG.
        """
        own = self.security_id
        refs = {self.classified_construct_id(), self.policy_ref}
        return own not in refs

    def classifies_construct(self, construct_id: str) -> bool:
        """DMR-09 — whether this object classifies the construct ``construct_id``."""
        return construct_id == self.classified_construct_id()

    def absorbs_classified(self) -> bool:
        """DZA-C3 / DMX-02 — the object references the construct it classifies, never owns it."""
        return False

    # -- non-constitutiveness (UDL-14/15 / DZA-07/09) --------------------------

    def confers_authority(self) -> bool:
        """UDL-14/15 / DZA-09 / C7 — a security object confers no authority (material)."""
        return False

    def embeds_secret(self) -> bool:
        """UDL-15 / DZA-09 / RR-07 / C7 — True iff the object appears to embed a secret."""
        haystack = canonical_json(self.canonical_core()).lower()
        return any(marker in haystack for marker in _SECRET_MARKERS)

    def redefines_el1(self) -> bool:
        """UDL-02 / DMI-05 / VC-5 — a security object redefines no EL-1/DMC-02/RL-F2 model."""
        return False

    def selects_technology(self) -> bool:
        """UDL-14 / DZA-07 / DZA-K5 — a security object selects no cryptography tech (material)."""
        return self._scan_technology()

    # -- lifecycle (UDL-12, forward-only) --------------------------------------

    def transition(self, to_state: SecurityState) -> SecurityObject:
        """Return a new object advanced to ``to_state`` (forward-only; UDL-12).

        A re-classification is a new record, never in-place mutation (DATA-014 §8; UDL-12/15;
        DZA-C4 append-only).

        Raises:
            SecurityError: on a backward transition.
        """
        if not isinstance(to_state, SecurityState):
            raise SecurityError("target state must be a DOS-01…05 state (UDL-12)")
        here = LIFECYCLE_ORDER.index(self.state)
        there = LIFECYCLE_ORDER.index(to_state)
        if there < here:
            raise SecurityError(
                f"lifecycle is forward-only (UDL-12): "
                f"{self.state.value} → {to_state.value} is backward"
            )
        return replace(self, state=to_state)

    # -- serialization ----------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """A deterministic, serializable projection of the security object."""
        return {
            "security_id": self.security_id,
            "meta_class": self.meta_class,
            "name": self.name,
            "type_tag": self.type_tag,
            "kind": self.kind.value,
            "classified_ref": self.classified_ref.to_dict(),
            "classified_construct_id": self.classified_construct_id(),
            "classified_dimension": self.classified_dimension(),
            "classified_dimensions": list(self.classified_dimensions()),
            "policy_ref": self.policy_ref,
            "binds_policy_by_reference": self.binds_policy_by_reference(),
            "enforcement_by_reference": self.enforcement_by_reference(),
            "classifications": [c.to_dict() for c in self.classifications],
            "records_classification": self.records_classification(),
            "verdict": self.verdict.value,
            "gap_report": list(self.gap_report()),
            "passes": self.passes(),
            "evaluative": self.is_evaluative(),
            "dimensioned": self.is_dimensioned(),
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
            "substrate_refs": list(SECURITY_SUBSTRATE_REFS),
            "absorbs_classified": self.absorbs_classified(),
        }


def make_classifications(
    entries: tuple[tuple[str, bool, int], ...],
) -> tuple[ClassificationEntry, ...]:
    """Build :class:`ClassificationEntry` records from ``(dimension, satisfied, level)`` triples."""
    return tuple(
        ClassificationEntry(dimension=dim, satisfied=ok, level=level)
        for dim, ok, level in entries
    )


def make_security(
    name: str,
    type_tag: str,
    classified: Entity | ClassifiedConstructRef,
    policy_ref: str,
    *,
    kind: SecurityKind = SecurityKind.CLASSIFICATION_LABEL,
    classifications: tuple[ClassificationEntry, ...] = (),
    verdict: SecurityVerdict = SecurityVerdict.PASS,
    state: SecurityState = SecurityState.DEFINED,
    version: str = "1.0.0",
    supersedes: str = "",
) -> SecurityObject:
    """Construct a well-formed :class:`SecurityObject` (fail-closed factory).

    ``classified`` is the construct the object classifies — either a CERTIFIED
    :class:`~data.entity.Entity` (reused by reference — the DMR-09 ``classifies`` target)
    or an already-projected :class:`ClassifiedConstructRef`.
    """
    classified_ref = (
        classified
        if isinstance(classified, ClassifiedConstructRef)
        else ClassifiedConstructRef.from_entity(classified)
    )
    return SecurityObject(
        name=name,
        type_tag=type_tag,
        kind=kind,
        classified_ref=classified_ref,
        policy_ref=policy_ref,
        classifications=tuple(classifications),
        verdict=verdict,
        state=state,
        version=version,
        supersedes=supersedes,
    )


__all__ = [
    "SECURITY_ID_PREFIX",
    "POLICY_REF_PREFIX",
    "CERTIFIED_ID_PREFIX",
    "REUSE_REFS",
    "policy_ref_for",
    "SecurityError",
    "ClassifiedConstructRef",
    "ClassificationEntry",
    "SecurityObject",
    "make_classifications",
    "make_security",
]
