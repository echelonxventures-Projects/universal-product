"""EC3-B11-U09 — The Universal Policy construct (SMC-09).

Realizes the meta-model concept **SMC-09 Policy** (SERVICE-005 §2; SERVICE-003 SOE-09;
SERVICE-013 §3):

    a **declarative, decidable, non-enforcing governing rule applied at a contract/operation
    boundary** — a predicate over service constructs that is *evaluated* to produce a judgment,
    never a mechanism that *enacts* a decision — an ENG-002 Object bearing an ENG-001 Identity,
    classified by an ENG-004 Type (SXH-09 = Authorization / Validation / Quota-SLA), that is
    **bound-by** a Contract declaring it applicable (SMR-02, reference-only; SOR-02), **governs**
    the Services/Operations/Executions that reference it (SMR-08 governed-by, reference-only;
    SOR-08), **behaves-as** the RUNTIME policy concern for its evaluation (SMR-11; RUNTIME-010,
    by reference; §7 / SPL-05), and carries the DF-2-represented data its predicate operates
    over via **operates-on** (SMR-13, by reference; SPL-C4).

The construct is the **declarative governance layer**: it *declares* which contract boundary it
binds, which constructs it governs, and which RUNTIME policy concern evaluates it — all as
**references**, so the rule is decidable with **no enforcement, no access grant, no state
mutation, and no conferred authority** (USL-13 / SPL-04 / SPL-C2). Evaluating a policy yields a
recorded *judgment* (:class:`PolicyDecision`, satisfied / violated) against a governed
construct's ENG-002 object (SPL-C1 / SOV-09); the *act* of evaluation is a reference to the
frozen RUNTIME policy concern (RUNTIME-010), never re-implemented here (SPL-05 / §7). The policy
defines no policy engine, PEP/PDP, rule engine, IAM product, gateway, or enforcement point; it
references the declarative RUNTIME policy concept only (STH-13 / §2.2).

The construct is **additive over the CERTIFIED EC-1 foundation** and reuses it — and the
CERTIFIED SMC-01…08 Service / Capability / Contract / Interface / Operation / Composition /
Orchestration / Execution — *by reference* (USL-02 / SMI-05): identity and value-fidelity are
derived through the EC-1 certified deterministic encoding, so this module introduces **no second
identity scheme and no parallel value model**. It selects no technology / policy-engine / IAM /
gateway (USL-15 / SPL-09) and confers no authority (USL-13 / SPL-07).

A :class:`Policy` is *immutable* (ENG-002 objecthood), *typed* (ENG-004), *identified*
(ENG-001), *classified* (SXH-09 kind), *boundary-bound by reference* (SMR-02), *scope-declaring
by reference* (SMR-08 governed-by), *runtime-reusing* (SMR-11 / §7), *data-by-reference*
(SMR-13), and holds a *forward-only lifecycle state* (SOS-01…06, USL-12). Constructing a
:class:`Policy` enforces these obligations fail-closed: an ill-formed policy cannot be
instantiated. It realizes/binds no Service, Capability, Contract, Interface, Operation,
Composition, Orchestration, Execution, or Security object — those are separate units; this
construct binds them only *by reference*.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from enum import Enum
from typing import Any

from engine.certification.contracts import canonical_json, content_hash
from service.policy_meta import (
    KIND_BEHAVIOR_SUFFIX,
    KIND_PRECEDENCE,
    KIND_RUNTIME_CONCERN,
    LIFECYCLE_ORDER,
    POLICY_META_CLASS,
    POLICY_RELATIONSHIPS,
    POLICY_SUBSTRATE_REFS,
    PolicyKind,
    ServiceState,
)
from service.service import (
    _SECRET_MARKERS,
    _TECHNOLOGY_MARKERS,
    ServiceError,
)

#: The deterministic id prefix for a realized Policy (mirrors EC-1 UCOS-<KIND>-<hex16>).
POLICY_ID_PREFIX = "UCOS-POLICY"

#: The map of frozen-foundation primitives this construct reuses *by reference*.
POLICY_FOUNDATION_REUSE: dict[str, str] = {
    "ENG-001": "engine.certification.contracts.content_hash (deterministic identity derivation)",
    "ENG-002": "python frozen object (immutable objecthood bearing the policy)",
    "ENG-003": "engine.certification.contracts.canonical_json (structural value fidelity)",
    "ENG-004": "service.policy_meta.PolicyKind + type_tag (ENG-004 typing, by reference)",
    "ENG-005": "reference identifiers (contract/subject/behavior/data refs; no new construct)",
    "RL-F2": "policy evaluation bound by reference (SMR-11; RUNTIME-010 evaluate / RUNTIME-008)",
    "DF-2": "predicate data bound by reference (SMR-13); represented data not redefined",
}


class PolicyVerdict(str, Enum):
    """The recorded outcome of *evaluating* a declarative policy (SPL-C1 / SOV-09).

    A verdict is a recorded *judgment*, never an enacted decision (SPL-04 / SPL-C2): it grants
    no access, blocks no invocation, and mutates no state. ``INAPPLICABLE`` records that the
    policy does not govern the subject (out of declared scope).
    """

    SATISFIED = "SATISFIED"  # the governed subject satisfies the declarative predicate
    VIOLATED = "VIOLATED"  # the governed subject violates the declarative predicate
    INAPPLICABLE = "INAPPLICABLE"  # the policy does not govern the subject (out of scope)


def _default_behavior_ref(kind: PolicyKind) -> str:
    """The abstract RL-F2 policy-evaluation reference for ``kind`` (SERVICE-013 §7; SPL-05)."""
    concern = KIND_RUNTIME_CONCERN[kind]
    suffix = KIND_BEHAVIOR_SUFFIX[kind]
    return f"ENG-005:RL-F2:{concern}.{suffix}"


def _require_reference(name: str, value: Any) -> str:
    """Require ``value`` to be a non-empty ENG-005 reference string (by reference)."""
    if not isinstance(value, str) or not value.strip():
        raise ServiceError(f"{name} must be a non-empty ENG-005 reference (SMR-02/08/11/13)")
    return value


def _require_ref_tuple(name: str, values: Any) -> tuple[str, ...]:
    """Require ``values`` to be a (possibly empty) tuple of non-empty ENG-005 reference strings."""
    if not isinstance(values, tuple):
        raise ServiceError(f"{name} must be a tuple of ENG-005 references (SMR-08/13)")
    for v in values:
        if not isinstance(v, str) or not v.strip():
            raise ServiceError(f"{name} entries must be non-empty ENG-005 references (SMR-08/13)")
    return values


@dataclass(frozen=True, slots=True)
class PolicyDecision:
    """A recorded, immutable judgment produced by *evaluating* a policy (SPL-C1 / SOV-09).

    A decision **records** a verdict against a governed construct's ENG-002 object; it enacts
    nothing, grants nothing, and mutates no state (SPL-04 / SPL-C2 / USL-13). The judgment value
    itself is supplied by the frozen RUNTIME policy concern (RUNTIME-010, by reference) — this
    construct only records it deterministically.
    """

    policy_id: str
    subject_ref: str
    verdict: PolicyVerdict
    kind: str

    def enacts_nothing(self) -> bool:
        """SPL-04 / SPL-C2 — a decision is a record; it enacts nothing (structurally true)."""
        return True

    def to_dict(self) -> dict[str, Any]:
        """A deterministic, serializable projection of the recorded judgment."""
        return {
            "decision_format": "ucos-policy-decision/1.0.0",
            "policy_id": self.policy_id,
            "subject_ref": self.subject_ref,
            "verdict": self.verdict.value,
            "kind": self.kind,
            "enacts": "none",
        }


@dataclass(frozen=True, slots=True)
class Policy:
    """SMC-09 — an immutable, typed, identified, declarative, non-enforcing governing rule.

    Fields:
        type_tag:     the ENG-004 Type of the policy (decidable, non-empty) — SPL-01.
        kind:         the SXH-09 classification (Authorization / Validation / Quota-SLA).
        contract_ref: the ENG-005 reference to the Contract that declares this policy applicable
                      (SMR-02 bound-by; SOR-02; reference-only; SPL-06). The declared boundary.
        subject_refs: tuple of ENG-005 references to the Service/Operation/Execution constructs
                      this policy governs (SMR-08 governed-by; SOR-08; the declared applicability
                      scope/subjects/targets; by reference). May be empty (declared, unscoped).
        behavior_ref: the ENG-005 reference to the RUNTIME policy concern the policy evaluation
                      behaves-as (SMR-11; RL-F2; RUNTIME-010; §7 / SPL-05). If omitted it
                      defaults to the kind-appropriate RUNTIME policy reference.
        data_refs:    tuple of DF-2-represented data references the predicate operates over
                      (SMR-13 operates-on; SOR-13; SPL-C4; by reference). May be empty.
        state:        the SOS-01…06 lifecycle state (forward-only) — USL-12.
    """

    type_tag: str
    kind: PolicyKind
    contract_ref: str
    subject_refs: tuple[str, ...] = field(default=())
    behavior_ref: str = ""
    data_refs: tuple[str, ...] = field(default=())
    state: ServiceState = ServiceState.DEFINED

    def __post_init__(self) -> None:
        # SPL-K1 / USL-03 / SPL-01 — typed (ENG-004): a decidable, non-empty type tag.
        if not isinstance(self.type_tag, str) or not self.type_tag.strip():
            raise ServiceError("policy must be typed: a non-empty ENG-004 type_tag (SPL-01)")
        # SXH-09 / SXC-02 — classified by exactly one policy kind.
        if not isinstance(self.kind, PolicyKind):
            raise ServiceError("policy kind must be an SXH-09 PolicyKind (SXC-02)")
        # SMR-02 / SOR-02 / SPL-06 — bound-by exactly the contract that declares it applicable.
        _require_reference("contract_ref", self.contract_ref)
        # SMR-08 / SOR-08 — the governed constructs (applicability scope), by reference.
        _require_ref_tuple("subject_refs", self.subject_refs)
        # §7 / SPL-05 — derive the kind-appropriate RUNTIME policy behavior reference if omitted.
        if not (isinstance(self.behavior_ref, str) and self.behavior_ref.strip()):
            object.__setattr__(self, "behavior_ref", _default_behavior_ref(self.kind))
        # SMR-11 / SOR-11 / SPL-05 — behaves-as the RUNTIME policy concern, by reference.
        _require_reference("behavior_ref", self.behavior_ref)
        # SMR-13 / SOR-13 / SPL-C4 — predicate data by reference (may be empty).
        _require_ref_tuple("data_refs", self.data_refs)
        # V5 / USL-12 — a valid lifecycle state.
        if not isinstance(self.state, ServiceState):
            raise ServiceError("policy state must be a SOS-01…06 ServiceState (USL-12)")

    # -- identity (ENG-001) borne by object (ENG-002), by reference ------------

    def canonical_core(self) -> dict[str, Any]:
        """The canonical, hashable core of the policy (its identity-defining tuple)."""
        return {
            "meta_class": POLICY_META_CLASS,
            "type_tag": self.type_tag,
            "kind": self.kind.value,
            "contract_ref": self.contract_ref,
            "subject_refs": list(self.subject_refs),
            "behavior_ref": self.behavior_ref,
            "data_refs": list(self.data_refs),
        }

    @property
    def value_digest(self) -> str:
        """The EC-1 content hash of the policy core — the ENG-003 value fingerprint."""
        return content_hash(self.canonical_core())

    @property
    def policy_id(self) -> str:
        """The deterministic ENG-001 identity of the policy (borne by this object)."""
        return f"{POLICY_ID_PREFIX}-{self.type_tag}-{self.value_digest[:16]}"

    @property
    def self_ref(self) -> str:
        """The ENG-005 self-reference form of this policy (for self-founding detection)."""
        return f"ENG-005:SOE-09:{self.type_tag}"

    # -- meta-model participation (SERVICE-005) --------------------------------

    @property
    def meta_class(self) -> str:
        """V1 — the single meta-class this construct instantiates (SMC-09)."""
        return POLICY_META_CLASS

    def meta_relationships(self) -> tuple[str, ...]:
        """V2 — the SMR-01…13 relationships the policy participates in."""
        return POLICY_RELATIONSHIPS

    # -- founding acyclicity (V4 / SMK-03) -------------------------------------

    def is_founding_acyclic(self) -> bool:
        """V4 / SMK-03 / SMI-04 — the founding graph (bound-by / behaves-as) is acyclic.

        A Policy binds its contract, subjects, behavior, and data *by reference* (string ids),
        so its founding structure carries no cycle. Canonical encodability proves the core is
        well-formed; the no-self-founding guard proves no reference names the policy itself.
        """
        try:
            canonical_json(self.canonical_core())
        except (TypeError, ValueError):  # pragma: no cover - blocked at construction
            return False
        return self.no_self_founding()

    def no_self_founding(self) -> bool:
        """SMK-03 — no reference founds the policy on itself (no self-founding cycle)."""
        me = self.self_ref
        return all(
            ref != me
            for ref in (self.contract_ref, self.behavior_ref, *self.subject_refs, *self.data_refs)
        )

    # -- policy-specific obligations -------------------------------------------

    def boundary_bound(self) -> bool:
        """SMR-02 / SOR-02 / SPL-06 / SPL-K2 — bound-by exactly the declaring contract boundary."""
        return bool(self.contract_ref.strip())

    def declarative_nonenforcing(self) -> bool:
        """SPL-03 / SPL-04 / USL-13 — the policy is declarative and enacts nothing.

        This is the governing law of the Policy concern: a policy is a predicate whose evaluation
        *records a judgment* and *confers no authority*. It is structurally non-enforcing — the
        construct holds only references and a type; it can grant nothing, block nothing, and
        mutate no state.
        """
        return not self.confers_authority()

    def runtime_reuse_valid(self) -> bool:
        """SPL-05 / §7 — evaluation behaves-as the RUNTIME policy concern by reference."""
        expected = KIND_RUNTIME_CONCERN[self.kind]
        return bool(self.behavior_ref.strip()) and expected in self.behavior_ref

    def behavior_by_reference(self) -> bool:
        """SMR-11 / USL-10 — evaluation binds RL-F2 by ENG-005 reference (RUNTIME-010)."""
        return bool(self.behavior_ref.strip())

    def data_by_reference(self) -> bool:
        """SMR-13 / SOR-13 / SPL-C4 / USL-11 — every predicate data ref is a DF-2 reference."""
        return all(isinstance(r, str) and bool(r.strip()) for r in self.data_refs)

    def scope_by_reference(self) -> bool:
        """SMR-08 / SOR-08 — every governed-subject ref is a non-empty ENG-005 reference."""
        return all(isinstance(r, str) and bool(r.strip()) for r in self.subject_refs)

    @property
    def precedence(self) -> int:
        """The deterministic evaluation-precedence rank of the policy (SXH-09 order).

        A *lower* rank is evaluated first. This is a decidable, evaluative ordering only
        (SPL-03/04): it enacts nothing and confers nothing — it records the deterministic order
        in which declarative predicates are considered when several apply to one subject.
        """
        return KIND_PRECEDENCE[self.kind]

    def precedence_decidable(self) -> bool:
        """SPL-08 — the policy's evaluation precedence is decidable from its SXH-09 kind."""
        return self.kind in KIND_PRECEDENCE

    def applies_to(self, subject_ref: str) -> bool:
        """SPL-06 — True iff ``subject_ref`` is within this policy's declared governed scope."""
        return isinstance(subject_ref, str) and subject_ref in self.subject_refs

    def records_lifecycle(self) -> bool:
        """SPL-08 / SOV-08 — the policy records a decidable lifecycle state (never silent)."""
        return isinstance(self.state, ServiceState)

    def references_resolve(self) -> bool:
        """SPL-K4 / SMK-05/07 — every ENG-005 reference is a non-empty resolvable id."""
        singles = (self.contract_ref, self.behavior_ref)
        return all(
            isinstance(ref, str) and bool(ref.strip())
            for ref in (*singles, *self.subject_refs, *self.data_refs)
        ) and self.no_self_founding()

    # -- declarative evaluation → recorded judgment (SPL-C1 / SOV-09) ----------

    def record_decision(self, subject_ref: str, satisfied: bool) -> PolicyDecision:
        """Record a judgment for ``subject_ref`` — declarative and non-enforcing (SPL-C1).

        The *act* of deciding whether the predicate holds is the RUNTIME policy concern
        (RUNTIME-010, by reference; SPL-05) — supplied here as ``satisfied``. This method only
        **records** the resulting verdict against the subject's ENG-002 object; it enacts
        nothing, grants nothing, and mutates no state (SPL-04 / SPL-C2 / USL-13). A subject
        outside the declared governed scope records ``INAPPLICABLE``.
        """
        _require_reference("subject_ref", subject_ref)
        if self.subject_refs and not self.applies_to(subject_ref):
            verdict = PolicyVerdict.INAPPLICABLE
        else:
            verdict = PolicyVerdict.SATISFIED if satisfied else PolicyVerdict.VIOLATED
        return PolicyDecision(
            policy_id=self.policy_id,
            subject_ref=subject_ref,
            verdict=verdict,
            kind=self.kind.value,
        )

    # -- non-constitutiveness (USL-15 / SPL-09) --------------------------------

    def confers_authority(self) -> bool:
        """USL-13 / USL-15 / SPL-07 / C7 — a policy confers no authority (structurally none)."""
        return False

    def selects_technology(self) -> bool:
        """USL-15 / SPL-09 / C7 — True iff the policy names a policy-engine/IAM/technology."""
        haystack = canonical_json(self.canonical_core()).lower()
        return any(marker in haystack for marker in _TECHNOLOGY_MARKERS)

    def embeds_secret(self) -> bool:
        """USL-15 / RR-07 / C7 — True iff the policy appears to embed a secret."""
        haystack = canonical_json(self.canonical_core()).lower()
        return any(marker in haystack for marker in _SECRET_MARKERS)

    def redefines_foundation(self) -> bool:
        """USL-02 / SMI-05 / VC-5 — a policy redefines no frozen primitive (reuse-only)."""
        return False

    # -- lifecycle (USL-12, forward-only) --------------------------------------

    def transition(self, to_state: ServiceState) -> Policy:
        """Return a new policy advanced to ``to_state`` (forward-only; USL-12)."""
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
        """A deterministic, serializable projection of the policy."""
        return {
            "policy_id": self.policy_id,
            "meta_class": self.meta_class,
            "type_tag": self.type_tag,
            "kind": self.kind.value,
            "contract_ref": self.contract_ref,
            "subject_refs": list(self.subject_refs),
            "behavior_ref": self.behavior_ref,
            "data_refs": list(self.data_refs),
            "value_digest": self.value_digest,
            "state": self.state.value,
            "precedence": self.precedence,
            "runtime_concern": KIND_RUNTIME_CONCERN[self.kind],
            "relationships": list(self.meta_relationships()),
            "substrate_refs": list(POLICY_SUBSTRATE_REFS),
        }


@dataclass(frozen=True, slots=True)
class PolicyConflict:
    """A recorded, evaluative detection that two policies ambiguously bind one subject.

    A conflict is an **evaluative record** (SERVICE-013 §12 conflict-detection index): two
    same-kind policies that both govern one subject via *different* contract boundaries create
    an ambiguous applicable-policy binding. Detecting or resolving a conflict enacts nothing and
    confers no authority (USL-13 / SPL-04); the ``governing_policy_id`` is chosen by a purely
    deterministic tiebreak (lexicographically smallest ``policy_id``) and is a *recorded
    recommendation*, never an enforced override.
    """

    subject_ref: str
    kind: str
    policy_ids: tuple[str, ...]
    governing_policy_id: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "conflict_format": "ucos-policy-conflict/1.0.0",
            "subject_ref": self.subject_ref,
            "kind": self.kind,
            "policy_ids": list(self.policy_ids),
            "governing_policy_id": self.governing_policy_id,
            "resolution": "deterministic-tiebreak(min policy_id); records only, enacts nothing",
        }


def detect_policy_conflicts(policies: tuple[Policy, ...]) -> tuple[PolicyConflict, ...]:
    """Detect ambiguous same-kind bindings over a shared subject — evaluative, non-enforcing.

    Two or more policies **conflict** on a subject iff they share the same SXH-09 kind, both
    govern that subject (SMR-08 scope), and bind *different* contract boundaries (SMR-02) — an
    ambiguous "which applicable policy governs?" binding. The detection is deterministic and
    records only; it grants nothing and blocks nothing (SERVICE-013 §12 / SPL-04 / USL-13). The
    ``governing_policy_id`` is the lexicographically smallest ``policy_id`` in the conflict set
    (a stable, decidable recommendation).
    """
    # Group policies by (subject_ref, kind).
    groups: dict[tuple[str, str], list[Policy]] = {}
    for policy in policies:
        for subject_ref in policy.subject_refs:
            groups.setdefault((subject_ref, policy.kind.value), []).append(policy)

    conflicts: list[PolicyConflict] = []
    for (subject_ref, kind), members in sorted(groups.items()):
        if len(members) < 2:
            continue
        # A conflict requires divergent contract boundaries (ambiguous applicable policy).
        contracts = {p.contract_ref for p in members}
        if len(contracts) < 2:
            continue
        ids = tuple(sorted(p.policy_id for p in members))
        conflicts.append(
            PolicyConflict(
                subject_ref=subject_ref,
                kind=kind,
                policy_ids=ids,
                governing_policy_id=ids[0],
            )
        )
    return tuple(conflicts)


def make_policy(
    type_tag: str,
    contract_ref: str,
    *,
    kind: PolicyKind = PolicyKind.AUTHORIZATION,
    subject_refs: tuple[str, ...] = (),
    behavior_ref: str = "",
    data_refs: tuple[str, ...] = (),
    state: ServiceState = ServiceState.DEFINED,
) -> Policy:
    """Construct a well-formed :class:`Policy` (fail-closed factory)."""
    return Policy(
        type_tag=type_tag,
        kind=kind,
        contract_ref=contract_ref,
        subject_refs=subject_refs,
        behavior_ref=behavior_ref,
        data_refs=data_refs,
        state=state,
    )


__all__ = [
    "POLICY_ID_PREFIX",
    "POLICY_FOUNDATION_REUSE",
    "PolicyVerdict",
    "PolicyDecision",
    "Policy",
    "PolicyConflict",
    "detect_policy_conflicts",
    "make_policy",
]
