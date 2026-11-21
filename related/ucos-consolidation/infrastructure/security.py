"""EC3-B13-U08 — The Universal Infrastructure Security constructs (SecurityFacet).

Realizes the **one** leaf meta-class concern 013 (INFRASTRUCTURE-013) instantiates
(INFRASTRUCTURE-005 §2), across the **five** evaluative facets it defines
(INFRASTRUCTURE-013 §2):

**SecurityFacet meta-class — five evaluative facets:**
* **Isolation** — evaluative measure of environment/boundary isolation (reuses
  IsolationBoundary/011 by reference).
* **Authentication** — evaluative classification of hosting-actor authentication posture
  (reuses RL-F2 policy by reference; never enforced).
* **Authorization** — evaluative classification of hosting-access authorization posture
  (reuses RL-F2 policy + APPLICATION-013 by reference).
* **Confidentiality** — evaluative measure of confidentiality posture of hosted-data
  location (reuses DATA-014 by reference).
* **Integrity** — evaluative measure of integrity posture of the hosting substrate
  (reuses DATA-014 + SERVICE-014 by reference).

Every facet is **evaluative & NON-ENFORCING** (WF-10 / ISEC-01/04 / UIL-14): it declares an
``evaluativeVerdict``, sets ``nonEnforcing = true``, and ``evaluates`` an ENG-002 object by
typed ENG-005 reference. It **enacts no enforcement, grants no access, issues no credential,
embeds no secret/credential/key (ISEC-03/RR-07), and selects no IAM/PKI/crypto technology
(ISEC-05)**. It confers no authority and projects no operational security readiness
(ISEC-06). Every facet is **additive over the CERTIFIED EC-1 foundation** and reuses the
frozen lower-layer security concerns *by reference* (UIL-02 / ISEC-02); it re-founds none.

Constructing a facet enforces its well-formedness rules and laws fail-closed.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from enum import Enum
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
from infrastructure.security_meta import (
    ADMITTED_VERDICTS,
    CONSTRUCT_RELATIONSHIPS,
    INFRA_SECURITY_ID_PREFIX,
    LIFECYCLE_ORDER,
    SECURITY_META_CLASS,
    SUBSTRATE_REFS,
    InfrastructureState,
)

#: The shared id-family prefix every Security facet construct id begins with.
INFRA_SECURITY_ID_FAMILY = "UCOS-INFRA-"

#: Default abstract ENG-005 references each facet evaluates / reuses (by reference).
#: Technology-neutral — names no IAM/PKI/crypto product or vendor.
DEFAULT_ISOLATION_REF = "ENG-005:IsolationBoundary:infrastructure.isolation.boundary"
DEFAULT_RL_F2_POLICY_REF = "ENG-005:RL-F2:runtime.policy.foundation"
DEFAULT_APPLICATION_013_REF = "ENG-005:APPLICATION-013:application.security.classification"
DEFAULT_DATA_014_REF = "ENG-005:DATA-014:data.security.classification"
DEFAULT_SERVICE_014_REF = "ENG-005:SERVICE-014:service.security.classification"

#: The abstract ENG-002 object a facet evaluates by reference (the hosting substrate).
DEFAULT_EVALUATED_OBJECT_REF = "ENG-005:ENG-002:infrastructure.hosting.substrate"

#: The map of frozen-foundation primitives these constructs reuse by reference.
FOUNDATION_REUSE: dict[str, str] = {
    "ENG-001": "engine.certification.contracts.content_hash (deterministic identity)",
    "ENG-002": "python frozen object (immutable objecthood; the evaluated object by ref)",
    "ENG-003": "engine.certification.contracts.canonical_json (value fidelity)",
    "ENG-004": "infrastructure.security type_tag (typed construct)",
    "ENG-005": "reference identifiers (evaluates/reuse refs; no new relationship construct)",
    "RL-F2": "runtime policy referenced by reference (UIL-14); never enforced, never redefined",
    "IsolationBoundary": "INFRASTRUCTURE-011 (U05) reused by reference (Isolation facet)",
    "DATA-014": "data security classification reused by reference (Confidentiality/Integrity)",
    "SERVICE-014": "service security classification reused by reference (Integrity)",
    "APPLICATION-013": "application security classification reused by reference (Authorization)",
}


class SecurityFacetKind(str, Enum):
    """INFRASTRUCTURE-013 §2 — the five evaluative facets of infrastructure security."""

    ISOLATION = "isolation"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    CONFIDENTIALITY = "confidentiality"
    INTEGRITY = "integrity"


def _selects_technology(core: dict[str, Any]) -> bool:
    """UIL-15 / ISEC-05 — True iff the construct core names a concrete technology/vendor."""
    haystack = canonical_json(core).lower()
    return any(marker in haystack for marker in _TECHNOLOGY_MARKERS)


def _embeds_secret(core: dict[str, Any]) -> bool:
    """UIL-15 / ISEC-03 / RR-07 — True iff the construct core appears to embed a secret."""
    haystack = canonical_json(core).lower()
    return any(marker in haystack for marker in _SECRET_MARKERS)


# ===========================================================================
# SecurityFacet meta-class construct (five facets via the `facet` kind field)
# ===========================================================================


@dataclass(frozen=True, slots=True)
class SecurityFacet:
    """SecurityFacet — an evaluative, non-enforcing security classification.

    A single meta-class (INFRASTRUCTURE-005 §2) realized across five facet kinds
    (INFRASTRUCTURE-013 §2). It classifies a security posture, declares an
    ``evaluativeVerdict``, and ``evaluates`` an ENG-002 object by typed ENG-005 reference,
    reusing a frozen lower-layer security concern by reference (ISEC-02). It never enacts
    enforcement, grants access, issues a credential, embeds a secret, or selects technology
    (ISEC-03/04/05); confers no authority (ISEC-06 / AUTH-06).

    Fields:
        type_tag:          the ENG-004 Type of the facet (decidable, non-empty) — UIL-03.
        facet:             the INFRASTRUCTURE-013 §2 facet kind (Isolation/Authentication/
                           Authorization/Confidentiality/Integrity).
        evaluates:         ≥1 ENG-005 references to the ENG-002 object(s) evaluated (ISEC-01).
        references:        the frozen lower-security concern(s) reused by reference (ISEC-02).
        evaluative_verdict: a non-projecting evaluative verdict (ISEC-06).
        non_enforcing:     WF-10 / ISEC-04 — must be True (enacts nothing).
        depends_on:        founding references (empty — facets are non-founding, WF-3).
        state:             the forward-only lifecycle state (INFRASTRUCTURE-003 §3).
    """

    META_CLASS = SECURITY_META_CLASS
    ID_PREFIX = INFRA_SECURITY_ID_PREFIX

    type_tag: str
    facet: SecurityFacetKind
    evaluates: tuple[str, ...] = field(default_factory=lambda: (DEFAULT_EVALUATED_OBJECT_REF,))
    references: tuple[str, ...] = field(default_factory=tuple)
    evaluative_verdict: str = "indeterminate"
    non_enforcing: bool = True
    depends_on: tuple[str, ...] = field(default_factory=tuple)
    state: InfrastructureState = InfrastructureState.DEFINED

    def __post_init__(self) -> None:
        # ISEC-01 / UIL-03 — typed (ENG-004): a decidable, non-empty type tag.
        if not isinstance(self.type_tag, str) or not self.type_tag.strip():
            raise InfrastructureError(
                "security facet must be typed with a non-empty ENG-004 type_tag (UIL-03)"
            )
        # INFRASTRUCTURE-013 §2 — classified by exactly one facet kind.
        if not isinstance(self.facet, SecurityFacetKind):
            raise InfrastructureError(
                "facet must be a SecurityFacetKind (INFRASTRUCTURE-013 §2)"
            )
        # ISEC-01 — evaluates ≥1 ENG-002 object by reference.
        if not isinstance(self.evaluates, tuple) or len(self.evaluates) < 1:
            raise InfrastructureError(
                "security facet must evaluate ≥1 ENG-002 object by reference (ISEC-01)"
            )
        for ev in self.evaluates:
            _require_reference("security facet evaluates target", ev)
        # ISEC-02 — reuse targets, if any, are references.
        for ref in self.references:
            _require_reference("security facet reference", ref)
        for dep in self.depends_on:
            _require_reference("security facet dependsOn", dep)
        # ISEC-06 — a decidable, non-projecting evaluative verdict.
        if self.evaluative_verdict not in ADMITTED_VERDICTS:
            raise InfrastructureError(
                f"security facet verdict '{self.evaluative_verdict}' not in admitted set "
                f"{ADMITTED_VERDICTS} (ISEC-06)"
            )
        # WF-10 / ISEC-04 — every evaluative facet is non-enforcing (fail-closed).
        if self.non_enforcing is not True:
            raise InfrastructureError(
                "security facet must be non-enforcing (nonEnforcing=true) (WF-10 / ISEC-04)"
            )
        # INFRASTRUCTURE-003 §3 — a valid forward-only lifecycle state.
        if not isinstance(self.state, InfrastructureState):
            raise InfrastructureError(
                "security facet state must be an InfrastructureState (INFRASTRUCTURE-003 §3)"
            )

    # -- identity (ENG-001) borne by object (ENG-002) ---

    def canonical_core(self) -> dict[str, Any]:
        return {
            "meta_class": self.META_CLASS,
            "type_tag": self.type_tag,
            "facet": self.facet.value,
            "evaluates": list(self.evaluates),
            "references": list(self.references),
            "evaluative_verdict": self.evaluative_verdict,
            "non_enforcing": self.non_enforcing,
            "depends_on": list(self.depends_on),
        }

    @property
    def value_digest(self) -> str:
        return content_hash(self.canonical_core())

    @property
    def construct_id(self) -> str:
        return f"{self.ID_PREFIX}-{self.type_tag}-{self.value_digest[:16]}"

    @property
    def facet_value(self) -> str:
        return self.facet.value

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
        # A SecurityFacet is always an evaluative, non-enforcing construct (WF-10 / ISEC-01).
        return True

    def is_founding_acyclic(self) -> bool:
        # EvaluativeFacets participate in no founding edge — vacuously acyclic (WF-3).
        try:
            canonical_json(self.canonical_core())
        except (TypeError, ValueError):  # pragma: no cover - blocked at construction
            return False
        return True

    def references_resolve(self) -> bool:
        return all(
            isinstance(ref, str) and bool(ref.strip())
            for ref in (*self.evaluates, *self.references, *self.depends_on)
        )

    def evaluates_object_bound(self) -> bool:
        """ISEC-01 — the facet evaluates ≥1 ENG-002 object by resolvable reference."""
        return bool(self.evaluates) and all(
            isinstance(ev, str) and bool(ev.strip()) for ev in self.evaluates
        )

    def declares_mandatory_attributes(self) -> bool:
        return (
            bool(self.type_tag.strip())
            and bool(self.value_digest)
            and bool(self.construct_id)
            and bool(self.facet_value)
            and bool(self.evaluative_verdict.strip())
            and bool(self.evaluates)
        )

    def has_valid_verdict(self) -> bool:
        """ISEC-06 — the evaluative verdict is one of the admitted, non-projecting values."""
        return self.evaluative_verdict in ADMITTED_VERDICTS

    # -- non-constitutiveness (UIL-14/15 / ISEC-03/04/05/06) ---

    def confers_authority(self) -> bool:
        """ISEC-06 / AUTH-06 — a security facet confers no authority (structurally has none)."""
        return False

    def enacts_enforcement(self) -> bool:
        """WF-10 / ISEC-04 — an evaluative facet enacts no enforcement."""
        return not self.non_enforcing

    def grants_access(self) -> bool:
        """ISEC-04 / AUTH-06 — a security facet grants no access and issues no credential."""
        return False

    def selects_technology(self) -> bool:
        """UIL-15 / ISEC-05 — True iff the facet names a concrete IAM/PKI/crypto technology."""
        return _selects_technology(self.canonical_core())

    def embeds_secret(self) -> bool:
        """UIL-15 / ISEC-03 / RR-07 — True iff the facet appears to embed a secret/key."""
        return _embeds_secret(self.canonical_core())

    def redefines_foundation(self) -> bool:
        return False

    def projects_completion(self) -> bool:
        return False

    def is_new_primitive(self) -> bool:
        return False

    # -- lifecycle (forward-only) ---

    def transition(self, to_state: InfrastructureState) -> SecurityFacet:
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
            "facet": self.facet.value,
            "value_digest": self.value_digest,
            "state": self.state.value,
            "evaluates": list(self.evaluates),
            "references": list(self.references),
            "evaluative_verdict": self.evaluative_verdict,
            "non_enforcing": self.non_enforcing,
            "depends_on": list(self.depends_on),
            "relationships": list(self.meta_relationships()),
            "substrate_refs": list(SUBSTRATE_REFS),
        }


# ---------------------------------------------------------------------------
# Per-facet default reuse references (ISEC-02)
# ---------------------------------------------------------------------------

_FACET_REFERENCES: dict[SecurityFacetKind, tuple[str, ...]] = {
    SecurityFacetKind.ISOLATION: (DEFAULT_ISOLATION_REF,),
    SecurityFacetKind.AUTHENTICATION: (DEFAULT_RL_F2_POLICY_REF,),
    SecurityFacetKind.AUTHORIZATION: (DEFAULT_RL_F2_POLICY_REF, DEFAULT_APPLICATION_013_REF),
    SecurityFacetKind.CONFIDENTIALITY: (DEFAULT_DATA_014_REF,),
    SecurityFacetKind.INTEGRITY: (DEFAULT_DATA_014_REF, DEFAULT_SERVICE_014_REF),
}


# ---------------------------------------------------------------------------
# Fail-closed factory
# ---------------------------------------------------------------------------


def make_security_facet(
    type_tag: str,
    facet: SecurityFacetKind,
    *,
    evaluates: tuple[str, ...] = (DEFAULT_EVALUATED_OBJECT_REF,),
    references: tuple[str, ...] | None = None,
    evaluative_verdict: str = "indeterminate",
    depends_on: tuple[str, ...] = (),
    state: InfrastructureState = InfrastructureState.DEFINED,
) -> SecurityFacet:
    """Construct a well-formed :class:`SecurityFacet` (fail-closed factory).

    When ``references`` is omitted, the facet's canonical reuse-by-reference targets
    (ISEC-02) are supplied from :data:`_FACET_REFERENCES`.
    """
    if references is None:
        references = _FACET_REFERENCES.get(facet, ())
    return SecurityFacet(
        type_tag=type_tag,
        facet=facet,
        evaluates=evaluates,
        references=references,
        evaluative_verdict=evaluative_verdict,
        non_enforcing=True,
        depends_on=depends_on,
        state=state,
    )


__all__ = [
    "INFRA_SECURITY_ID_FAMILY",
    "INFRA_SECURITY_ID_PREFIX",
    "DEFAULT_ISOLATION_REF",
    "DEFAULT_RL_F2_POLICY_REF",
    "DEFAULT_APPLICATION_013_REF",
    "DEFAULT_DATA_014_REF",
    "DEFAULT_SERVICE_014_REF",
    "DEFAULT_EVALUATED_OBJECT_REF",
    "FOUNDATION_REUSE",
    "SecurityFacetKind",
    "SecurityFacet",
    "make_security_facet",
]
