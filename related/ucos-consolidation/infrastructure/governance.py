"""EC3-B13-U09 — The Universal Infrastructure Governance constructs (GovernanceFacet).

Realizes the **one** leaf meta-class concern 014 (INFRASTRUCTURE-014) instantiates
(INFRASTRUCTURE-005 §2), across the **five** record-only constructs it defines
(INFRASTRUCTURE-014 §2):

**GovernanceFacet meta-class — five record-only constructs:**
* **Conformance Facet** — evaluative verdict of a construct against UIL/UIMM-CONF (reuses
  UIMM-CONF/005 by reference).
* **Lifecycle Facet** — evaluative record of a construct's architectural lifecycle state
  (reuses UITX §3.3 by reference).
* **Policy Facet** — evaluative classification of governing rules, non-enforcing (reuses
  RL-F2 policy by reference; never enforced).
* **Gap Report** — a recorded violation of a law/rule routed to the ENG-000 custodian
  (reuses ENG-000 custodian by reference).
* **Change Record** — an additive/supersession change record, no renumber/mutation (reuses
  UCI-001 + REG-AUTO-001 by reference).

Every construct is **record-only & NON-ENFORCING** (WF-10 / IGOV-01 / UIL-14): it declares
an ``evaluativeVerdict``, sets ``nonEnforcing = true``, and ``evaluates`` an ENG-002 object
by typed ENG-005 reference. It **enacts no enforcement, approves nothing, grants no access,
creates no operational/approval/enforcement/ratification authority (IGOV-04 / AUTH-06 /
ID-01), embeds no secret, and selects no policy engine/technology/vendor (IGOV-06 /
UIL-15)**. It projects no operational governance readiness (IGOV-06). Every construct is
**additive over the CERTIFIED EC-1 foundation** and reuses the frozen lower concerns *by
reference* (UIL-02 / IGOV-05); it re-founds none and mints no new authority/primitive/
registry/identifier/lifecycle (IGOV-04/05).

Constructing a construct enforces its well-formedness rules and laws fail-closed.
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
from infrastructure.governance_meta import (
    ADMITTED_VERDICTS,
    CONSTRUCT_RELATIONSHIPS,
    GOVERNANCE_META_CLASS,
    INFRA_GOVERNANCE_ID_PREFIX,
    LIFECYCLE_ORDER,
    SUBSTRATE_REFS,
    InfrastructureState,
)

#: The shared id-family prefix every Governance construct id begins with.
INFRA_GOVERNANCE_ID_FAMILY = "UCOS-INFRA-"

#: Default abstract ENG-005 references each construct evaluates / reuses (by reference).
#: Technology-neutral — names no policy engine, workflow product, or vendor.
DEFAULT_UIMM_CONF_REF = "ENG-005:UIMM-CONF:infrastructure.meta.conformance"
DEFAULT_UITX_LIFECYCLE_REF = "ENG-005:UITX:infrastructure.transition.lifecycle"
DEFAULT_RL_F2_POLICY_REF = "ENG-005:RL-F2:runtime.policy.foundation"
DEFAULT_ENG000_CUSTODIAN_REF = "ENG-005:ENG-000:foundation.custodian.registrar"
DEFAULT_UCI_CHANGE_REF = "ENG-005:UCI-001:change.additive.supersession"
DEFAULT_REG_AUTO_REF = "ENG-005:REG-AUTO-001:registration.append.only"

#: The abstract ENG-002 object a construct evaluates by reference (the hosting substrate).
DEFAULT_EVALUATED_OBJECT_REF = "ENG-005:ENG-002:infrastructure.hosting.substrate"

#: The map of frozen-foundation primitives these constructs reuse by reference.
FOUNDATION_REUSE: dict[str, str] = {
    "ENG-001": "engine.certification.contracts.content_hash (deterministic identity)",
    "ENG-002": "python frozen object (immutable objecthood; the evaluated object by ref)",
    "ENG-003": "engine.certification.contracts.canonical_json (value fidelity)",
    "ENG-004": "infrastructure.governance type_tag (typed construct)",
    "ENG-005": "reference identifiers (evaluates/reuse refs; no new relationship construct)",
    "ENG-000": "custodian/Registrar referenced by reference (Gap Report routing)",
    "RL-F2": "runtime policy referenced by reference (UIL-14); never enforced, never redefined",
    "UIMM-CONF": "INFRASTRUCTURE-005 conformance basis reused by reference (Conformance)",
    "UITX": "infrastructure lifecycle basis reused by reference (Lifecycle)",
    "UCI-001": "additive/supersession change instrument reused by reference (Change Record)",
    "REG-AUTO-001": "append-only registration law reused by reference (Change Record)",
}


class GovernanceFacetKind(str, Enum):
    """INFRASTRUCTURE-014 §2 — the five record-only constructs of infrastructure governance."""

    CONFORMANCE = "conformance"
    LIFECYCLE = "lifecycle"
    POLICY = "policy"
    GAP_REPORT = "gap_report"
    CHANGE_RECORD = "change_record"


def _selects_technology(core: dict[str, Any]) -> bool:
    """UIL-15 / IGOV-06 — True iff the construct core names a concrete technology/vendor."""
    haystack = canonical_json(core).lower()
    return any(marker in haystack for marker in _TECHNOLOGY_MARKERS)


def _embeds_secret(core: dict[str, Any]) -> bool:
    """UIL-15 / IGOV-06 — True iff the construct core appears to embed a secret."""
    haystack = canonical_json(core).lower()
    return any(marker in haystack for marker in _SECRET_MARKERS)


# ===========================================================================
# GovernanceFacet meta-class construct (five constructs via the `facet` kind field)
# ===========================================================================


@dataclass(frozen=True, slots=True)
class GovernanceFacet:
    """GovernanceFacet — a record-only, non-enforcing governance classification/record.

    A single meta-class (INFRASTRUCTURE-005 §2) realized across five construct kinds
    (INFRASTRUCTURE-014 §2). It records a governance judgment, declares an
    ``evaluativeVerdict``, and ``evaluates`` an ENG-002 object by typed ENG-005 reference,
    reusing a frozen lower concern by reference (IGOV-05). It never enacts enforcement,
    approves anything, grants access, mints authority, embeds a secret, or selects
    technology (IGOV-01/04/06); confers no authority (IGOV-04 / AUTH-06 / ID-01).

    Fields:
        type_tag:          the ENG-004 Type of the construct (decidable, non-empty) — UIL-03.
        facet:             the INFRASTRUCTURE-014 §2 construct kind (Conformance/Lifecycle/
                           Policy/Gap Report/Change Record).
        evaluates:         ≥1 ENG-005 references to the ENG-002 object(s) evaluated (IGOV-02).
        references:        the frozen lower concern(s) reused by reference (IGOV-05).
        evaluative_verdict: a non-projecting evaluative verdict (IGOV-01).
        non_enforcing:     WF-10 / IGOV-01 — must be True (enacts nothing).
        depends_on:        founding references (empty — facets are non-founding, WF-3).
        state:             the forward-only lifecycle state (INFRASTRUCTURE-003 §3).
    """

    META_CLASS = GOVERNANCE_META_CLASS
    ID_PREFIX = INFRA_GOVERNANCE_ID_PREFIX

    type_tag: str
    facet: GovernanceFacetKind
    evaluates: tuple[str, ...] = field(default_factory=lambda: (DEFAULT_EVALUATED_OBJECT_REF,))
    references: tuple[str, ...] = field(default_factory=tuple)
    evaluative_verdict: str = "indeterminate"
    non_enforcing: bool = True
    depends_on: tuple[str, ...] = field(default_factory=tuple)
    state: InfrastructureState = InfrastructureState.DEFINED

    def __post_init__(self) -> None:
        # IGOV-02 / UIL-03 — typed (ENG-004): a decidable, non-empty type tag.
        if not isinstance(self.type_tag, str) or not self.type_tag.strip():
            raise InfrastructureError(
                "governance construct must be typed with a non-empty ENG-004 type_tag (UIL-03)"
            )
        # INFRASTRUCTURE-014 §2 — classified by exactly one construct kind.
        if not isinstance(self.facet, GovernanceFacetKind):
            raise InfrastructureError(
                "facet must be a GovernanceFacetKind (INFRASTRUCTURE-014 §2)"
            )
        # IGOV-02 — evaluates ≥1 ENG-002 object by reference.
        if not isinstance(self.evaluates, tuple) or len(self.evaluates) < 1:
            raise InfrastructureError(
                "governance construct must evaluate ≥1 ENG-002 object by reference (IGOV-02)"
            )
        for ev in self.evaluates:
            _require_reference("governance construct evaluates target", ev)
        # IGOV-05 — reuse targets, if any, are references.
        for ref in self.references:
            _require_reference("governance construct reference", ref)
        for dep in self.depends_on:
            _require_reference("governance construct dependsOn", dep)
        # IGOV-01 — a decidable, non-projecting evaluative verdict.
        if self.evaluative_verdict not in ADMITTED_VERDICTS:
            raise InfrastructureError(
                f"governance construct verdict '{self.evaluative_verdict}' not in admitted set "
                f"{ADMITTED_VERDICTS} (IGOV-01)"
            )
        # WF-10 / IGOV-01 — every evaluative facet is record-only / non-enforcing (fail-closed).
        if self.non_enforcing is not True:
            raise InfrastructureError(
                "governance construct must be non-enforcing (nonEnforcing=true) (WF-10 / IGOV-01)"
            )
        # INFRASTRUCTURE-003 §3 — a valid forward-only lifecycle state.
        if not isinstance(self.state, InfrastructureState):
            raise InfrastructureError(
                "governance construct state must be an InfrastructureState (INFRASTRUCTURE-003 §3)"
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
        # A GovernanceFacet is always a record-only, non-enforcing construct (WF-10 / IGOV-01).
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
        """IGOV-02 — the construct evaluates ≥1 ENG-002 object by resolvable reference."""
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
        """IGOV-01 — the evaluative verdict is one of the admitted, non-projecting values."""
        return self.evaluative_verdict in ADMITTED_VERDICTS

    # -- non-constitutiveness (UIL-14/15 / IGOV-01/04/06) ---

    def confers_authority(self) -> bool:
        """IGOV-04 / AUTH-06 — a governance construct confers no authority (structurally none)."""
        return False

    def enacts_enforcement(self) -> bool:
        """WF-10 / IGOV-01 — a record-only facet enacts no enforcement."""
        return not self.non_enforcing

    def grants_access(self) -> bool:
        """IGOV-01/04 — a governance construct grants no access and approves nothing."""
        return False

    def selects_technology(self) -> bool:
        """UIL-15 / IGOV-06 — True iff the construct names a concrete policy engine/technology."""
        return _selects_technology(self.canonical_core())

    def embeds_secret(self) -> bool:
        """UIL-15 / IGOV-06 — True iff the construct appears to embed a secret/key."""
        return _embeds_secret(self.canonical_core())

    def redefines_foundation(self) -> bool:
        return False

    def projects_completion(self) -> bool:
        return False

    def is_new_primitive(self) -> bool:
        return False

    # -- lifecycle (forward-only) ---

    def transition(self, to_state: InfrastructureState) -> GovernanceFacet:
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
# Per-construct default reuse references (IGOV-05)
# ---------------------------------------------------------------------------

_FACET_REFERENCES: dict[GovernanceFacetKind, tuple[str, ...]] = {
    GovernanceFacetKind.CONFORMANCE: (DEFAULT_UIMM_CONF_REF,),
    GovernanceFacetKind.LIFECYCLE: (DEFAULT_UITX_LIFECYCLE_REF,),
    GovernanceFacetKind.POLICY: (DEFAULT_RL_F2_POLICY_REF,),
    GovernanceFacetKind.GAP_REPORT: (DEFAULT_ENG000_CUSTODIAN_REF,),
    GovernanceFacetKind.CHANGE_RECORD: (DEFAULT_UCI_CHANGE_REF, DEFAULT_REG_AUTO_REF),
}


# ---------------------------------------------------------------------------
# Fail-closed factory
# ---------------------------------------------------------------------------


def make_governance_facet(
    type_tag: str,
    facet: GovernanceFacetKind,
    *,
    evaluates: tuple[str, ...] = (DEFAULT_EVALUATED_OBJECT_REF,),
    references: tuple[str, ...] | None = None,
    evaluative_verdict: str = "indeterminate",
    depends_on: tuple[str, ...] = (),
    state: InfrastructureState = InfrastructureState.DEFINED,
) -> GovernanceFacet:
    """Construct a well-formed :class:`GovernanceFacet` (fail-closed factory).

    When ``references`` is omitted, the construct's canonical reuse-by-reference targets
    (IGOV-05) are supplied from :data:`_FACET_REFERENCES`.
    """
    if references is None:
        references = _FACET_REFERENCES.get(facet, ())
    return GovernanceFacet(
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
    "INFRA_GOVERNANCE_ID_FAMILY",
    "INFRA_GOVERNANCE_ID_PREFIX",
    "DEFAULT_UIMM_CONF_REF",
    "DEFAULT_UITX_LIFECYCLE_REF",
    "DEFAULT_RL_F2_POLICY_REF",
    "DEFAULT_ENG000_CUSTODIAN_REF",
    "DEFAULT_UCI_CHANGE_REF",
    "DEFAULT_REG_AUTO_REF",
    "DEFAULT_EVALUATED_OBJECT_REF",
    "FOUNDATION_REUSE",
    "GovernanceFacetKind",
    "GovernanceFacet",
    "make_governance_facet",
]
