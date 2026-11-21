"""EC3-B12-U10 — The Universal Governance construct (AMC-10).

Realizes the meta-model concept **AMC-10 Governance** (APPLICATION-005 §2; APPLICATION-014;
APPLICATION-003 AOE-10; APPLICATION-001 §2):

    the **declarative, record-only classification of an application/feature's conformance,
    lifecycle, and policy concerns** — a record of *what a construct's governance judgment
    is*, never a mechanism that *enacts* approval, enforcement, or ratification — a typed
    (ENG-004) object (ENG-002), identified (ENG-001), classified by one AXH-10 kind
    (Conformance / Lifecycle / Policy record), that is the construct an application/feature is
    **governed-by** (AMR-09, the defining relationship — the Governance record is the *target*
    of governed-by; reference-only), that **secures-by** a Security record whose conformance it
    references (AMR-08, reference-only), that **holds-state** a State construct for its
    lifecycle records (AMR-06, reference-only), binds its evaluation to the frozen RUNTIME
    policy concern (§7 governance-evaluate; RL-F2, by reference), records its judgments through
    the frozen RUNTIME event concern (§7 governance-record), and discharges supersession under
    ENG-000 change control (§7 governance-supersede).

The construct is the **declarative governance judgment**: it *records* which construct it
governs, which Security record's conformance it references, which State it holds, and which
RUNTIME policy concern evaluates it — all as **references**, so the judgment is decidable with
**no approval, no enforcement, no ratification, and no conferred authority** (UAL-14 / GOV-03 /
GOV-C1…C5). Evaluating a governance record yields a recorded *governance judgment*
(:class:`GovernanceAssessment`, satisfied / violated / inapplicable) against a governed
construct's ENG-002 object (GOV-C1 / AOV-09); the *act* of evaluation is a reference to the
frozen RUNTIME policy concern (RUNTIME-010), never re-implemented here (§7). The governance
record defines no workflow-approval engine, policy-enforcement engine, ratification authority,
or EC-series step; it references the declarative RUNTIME policy concept and the ENG-000 change
control only (ATH-13 / §2.2).

The construct is **additive over the CERTIFIED EC-1 foundation** (and the referenced,
CERTIFIED-COMPLETE Band-10 data surface + CERTIFIED-COMPLETE + FROZEN Band-11 service surface +
the CERTIFIED Band-12 U01 Application root + U02 Capability + U03 Module + U04 Feature + U05
Workflow + U06 Interaction + U07 State + U08 Composition + U09 Security) and reuses them *by
reference* (UAL-02 / AMI-05): identity and value-fidelity are derived through the EC-1 certified
deterministic encoding (:func:`engine.certification.contracts.canonical_json` /
:func:`~engine.certification.contracts.content_hash`), so this module introduces **no second
identity scheme and no parallel value model**. It selects no technology (UAL-15 / GOV-K5) and
confers no authority (UAL-14/15 / GOV-04/09).

A :class:`Governance` is *immutable* (a frozen object — ENG-002 objecthood), *typed* (ENG-004),
*identified* (ENG-001 via a deterministic id), *classified* (AXH-10 kind), *boundary-recording
by reference* (AMR-09 governed-by), *security-referencing by reference* (AMR-08 secured-by),
*state-holding by reference* (AMR-06 holds-state), *runtime-reusing* (§7 governance-evaluate →
RL-F2), and holds a *forward-only lifecycle state* (AOS-01…06, UAL-12). Constructing a
:class:`Governance` enforces these obligations fail-closed: an ill-formed governance record
cannot be instantiated. It realizes no Application, Capability, Module, Feature, Workflow,
Interaction, State, Composition, or Security object — those are separate Band-12 units; this
construct classifies and references them only *by reference*.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from enum import Enum
from typing import Any

from application.governance_meta import (
    GOVERNANCE_FACETS,
    GOVERNANCE_META_CLASS,
    GOVERNANCE_RELATIONSHIPS,
    KIND_PRECEDENCE,
    KIND_RUNTIME_CONCERN,
    LIFECYCLE_ORDER,
    STATE_BEARING_KINDS,
    SUBSTRATE_REFS,
    GovernanceKind,
    GovernanceState,
)

# --- EC-1 reuse by reference (UAL-02 / AMI-05) — imported, never redefined --------
from engine.certification.contracts import canonical_json, content_hash

#: The deterministic id prefix for a realized Governance record (mirrors EC-1 UCOS-<KIND>-<hex16>).
GOVERNANCE_ID_PREFIX = "UCOS-GOVERNANCE"

#: The map of frozen-foundation primitives this construct reuses *by reference*
#: (never redefined). Recorded for the reuse-integrity check (UAL-02 / AMI-05 / VC-5).
FOUNDATION_REUSE: dict[str, str] = {
    "ENG-001": "engine.certification.contracts.content_hash (deterministic identity derivation)",
    "ENG-002": "python frozen object (immutable objecthood bearing the governance record)",
    "ENG-003": "engine.certification.contracts.canonical_json (value fidelity; no parallel model)",
    "ENG-004": "application.governance_meta.GovernanceKind + type_tag (ENG-004 typing, by ref)",
    "ENG-005": "reference identifiers (governed/security/state/behavior refs; no new construct)",
    "RL-F2": "governance-evaluate policy + governance-record event bound by reference (§7); "
    "none redef",
}

#: Concrete-technology markers forbidden by UAL-15 / GOV-K5 (no workflow-approval engine /
#: policy-enforcement engine / ratification authority / framework / vendor). An abstract
#: EL-1/RL-F2 reference names none of these — workflow-approval and policy-enforcement engines
#: are out of scope (APPLICATION-014 §2.2), referenced through RL-F2 / ENG-000, never selected.
_TECHNOLOGY_MARKERS: tuple[str, ...] = (
    # workflow-approval / policy-enforcement / governance engines (APPLICATION-014 §2.2)
    "camunda",
    "activiti",
    "flowable",
    "zeebe",
    "jbpm",
    "drools",
    "open-policy-agent",
    "opa-engine",
    "servicenow",
    "jira",
    "sailpoint",
    "collibra",
    # identity providers / IAM / key stores / secret stores / vendors
    "keycloak",
    "okta",
    "auth0",
    "cognito",
    "vault",
    "hashicorp",
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

#: Conservative secret markers used to enforce UAL-15 / RR-07 / GOV-09 (embed no secret).
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


class GovernanceError(ValueError):
    """Raised when inputs cannot be realized as a well-formed :class:`Governance` record.

    A :class:`Governance` record is fail-closed (TRACK-001): an ill-formed record is rejected at
    construction rather than admitted as an invalid judgment.
    """


class GovernanceVerdict(str, Enum):
    """The recorded outcome of *evaluating* a governance record (GOV-C1 / AOV-09).

    A verdict is a recorded *governance judgment*, never an enacted decision (UAL-14 / GOV-03 /
    GOV-C2): it approves nothing, enforces nothing, ratifies nothing, and mutates no state.
    ``INAPPLICABLE`` records that the governance record does not govern the subject (out of the
    declared governed boundary).
    """

    SATISFIED = "SATISFIED"  # the governed subject satisfies the governance judgment
    VIOLATED = "VIOLATED"  # the governed subject violates the governance judgment
    INAPPLICABLE = "INAPPLICABLE"  # the governance record does not govern the subject (unscoped)


def _default_behavior_ref(kind: GovernanceKind) -> str:
    """The abstract RL-F2 governance-evaluate reference for ``kind`` (APPLICATION-014 §7)."""
    concern = KIND_RUNTIME_CONCERN[kind]
    return f"ENG-005:RL-F2:runtime.governance-evaluate.{concern}"


def _require_reference(name: str, value: Any) -> str:
    """Require ``value`` to be a non-empty ENG-005 reference string (by reference)."""
    if not isinstance(value, str) or not value.strip():
        raise GovernanceError(f"{name} must be a non-empty ENG-005 reference (AMR-06/08/09/§7)")
    return value


def _require_ref_tuple(name: str, values: Any, *, minimum: int = 0) -> tuple[str, ...]:
    """Require ``values`` to be a tuple of non-empty ENG-005 reference strings (≥ ``minimum``)."""
    if not isinstance(values, tuple):
        raise GovernanceError(f"{name} must be a tuple of ENG-005 references (AMR-06/08/09)")
    for v in values:
        if not isinstance(v, str) or not v.strip():
            raise GovernanceError(
                f"{name} entries must be non-empty ENG-005 references (AMR-06/08/09)"
            )
    if len(values) < minimum:
        raise GovernanceError(f"{name} must declare at least {minimum} ENG-005 reference (GOV-K2)")
    return values


def _contains_marker(value: str, markers: tuple[str, ...]) -> bool:
    """True iff ``value`` (case-insensitively) contains any of ``markers``."""
    haystack = value.lower()
    return any(marker in haystack for marker in markers)


@dataclass(frozen=True, slots=True)
class GovernanceAssessment:
    """A recorded, immutable governance judgment produced by *evaluating* a governance record.

    An assessment **records** a verdict against a governed construct's ENG-002 object; it enacts
    nothing, approves nothing, enforces nothing, ratifies nothing, and mutates no state (UAL-14 /
    GOV-C1 / GOV-C2). The judgment value itself is supplied by the frozen RUNTIME policy concern
    (RUNTIME-010, by reference; §7) — this construct only records it deterministically.
    """

    governance_id: str
    subject_ref: str
    verdict: GovernanceVerdict
    kind: str

    def enacts_nothing(self) -> bool:
        """UAL-14 / GOV-C1 — an assessment is a record; it enacts nothing (structurally true)."""
        return True

    def to_dict(self) -> dict[str, Any]:
        """A deterministic, serializable projection of the recorded governance judgment."""
        return {
            "assessment_format": "ucos-application-governance-assessment/1.0.0",
            "governance_id": self.governance_id,
            "subject_ref": self.subject_ref,
            "verdict": self.verdict.value,
            "kind": self.kind,
            "enacts": "none",
        }


@dataclass(frozen=True, slots=True)
class Governance:
    """AMC-10 — an immutable, typed, identified, decidable, non-enforcing governance record.

    Fields:
        type_tag:       the ENG-004 Type of the governance record (decidable, non-empty) — GOV-01.
        kind:           the AXH-10 classification (AXC-04): Conformance / Lifecycle / Policy
                        record.
        subject_refs:   tuple of ENG-005 references to the Application/Feature/Module/Workflow/
                        Interaction/State/Composition constructs this record governs — the
                        constructs **governed-by** this record (AMR-09; AOR-09; the declared
                        governed boundary; reference-only; GOV-07 / GOV-K2). Must be non-empty.
        security_refs:  tuple of ENG-005 references to the Security records whose conformance
                        this record references (AMR-08 secured-by; AOR-08; reference-only). May
                        be empty.
        state_refs:     tuple of ENG-005 references to the State constructs a lifecycle-record
                        holds (AMR-06 holds-state; AOR-06; reference-only). May be empty
                        (conformance/policy records hold no state).
        behavior_ref:   the ENG-005 reference to the RUNTIME policy concern the evaluation
                        behaves-as (§7 governance-evaluate; RL-F2; RUNTIME-010). If omitted it
                        defaults to the kind-appropriate RUNTIME policy reference.
        state:          the AOS-01…06 lifecycle state (forward-only) — UAL-12 (default DEFINED).
    """

    type_tag: str
    kind: GovernanceKind
    subject_refs: tuple[str, ...]
    security_refs: tuple[str, ...] = field(default=())
    state_refs: tuple[str, ...] = field(default=())
    behavior_ref: str = ""
    state: GovernanceState = GovernanceState.DEFINED

    def __post_init__(self) -> None:
        # GOV-K1 / UAL-03 / GOV-01 — typed (ENG-004): a decidable, non-empty type tag.
        if not isinstance(self.type_tag, str) or not self.type_tag.strip():
            raise GovernanceError(
                "governance record must be typed with a non-empty ENG-004 type_tag "
                "(UAL-03 / GOV-01)"
            )
        # AXH-10 / AXC-04 — classified by exactly one Governance kind.
        if not isinstance(self.kind, GovernanceKind):
            raise GovernanceError("governance kind must be an AXH-10 GovernanceKind (AXC-04)")
        # AMR-09 / AOR-09 / GOV-07 / GOV-K2 — governs at least one declared boundary.
        _require_ref_tuple("subject_refs", self.subject_refs, minimum=1)
        # AMR-08 / AOR-08 — the referenced Security records (secured-by), by reference (opt).
        _require_ref_tuple("security_refs", self.security_refs)
        # AMR-06 / AOR-06 — the held State (holds-state, lifecycle-record), by reference (opt).
        _require_ref_tuple("state_refs", self.state_refs)
        # §7 — derive the kind-appropriate RUNTIME policy behavior reference if omitted.
        if not (isinstance(self.behavior_ref, str) and self.behavior_ref.strip()):
            object.__setattr__(self, "behavior_ref", _default_behavior_ref(self.kind))
        # §7 / AMK-05 — the governance-evaluate behavior binds the RUNTIME policy concern by ref.
        _require_reference("behavior_ref", self.behavior_ref)
        # V5 / UAL-12 — a valid lifecycle state.
        if not isinstance(self.state, GovernanceState):
            raise GovernanceError(
                "governance state must be an AOS-01…06 GovernanceState (UAL-12)"
            )

    # -- identity (ENG-001) borne by object (ENG-002), by reference ------------

    def canonical_core(self) -> dict[str, Any]:
        """The canonical, hashable core of the governance record (its identity-defining tuple).

        Governed/security/state references are canonically sorted (they are reference sets), so
        two records governing the same boundaries in different declaration order bear the same
        ENG-001 identity. The lifecycle ``state`` is **not** part of identity.
        """
        return {
            "meta_class": GOVERNANCE_META_CLASS,
            "type_tag": self.type_tag,
            "kind": self.kind.value,
            "facet": self.facet(),
            "subject_refs": sorted(self.subject_refs),
            "security_refs": sorted(self.security_refs),
            "state_refs": sorted(self.state_refs),
            "behavior_ref": self.behavior_ref,
        }

    @property
    def value_digest(self) -> str:
        """The EC-1 content hash of the governance core — the ENG-003 value fingerprint."""
        return content_hash(self.canonical_core())

    @property
    def governance_id(self) -> str:
        """The deterministic ENG-001 identity of the governance record (borne by this object).

        Derived through the CERTIFIED EC-1 ``content_hash`` (UAL-04 — no second identity
        scheme): identical (type, kind, refs) always yields the identical id, so identity is
        reproducible and byte-stable (determinism, VC-4).
        """
        return f"{GOVERNANCE_ID_PREFIX}-{self.type_tag}-{self.value_digest[:16]}"

    @property
    def self_ref(self) -> str:
        """The ENG-005 self-reference form of this record (for self-founding detection)."""
        return f"ENG-005:AOE-10:{self.type_tag}"

    # -- meta-model participation (APPLICATION-005/014) ------------------------

    @property
    def meta_class(self) -> str:
        """V1 — the single meta-class this construct instantiates (AMC-10)."""
        return GOVERNANCE_META_CLASS

    def meta_relationships(self) -> tuple[str, ...]:
        """V2 — the AMR-01…14 relationships the governance record participates in."""
        return GOVERNANCE_RELATIONSHIPS

    def facet(self) -> str:
        """AXH-10 — the governance concern the kind records (conformance/lifecycle/policy)."""
        return GOVERNANCE_FACETS[self.kind]

    # -- founding acyclicity (V4 / AMK-03) -------------------------------------

    def is_founding_acyclic(self) -> bool:
        """V4 / AMK-03 / AMI-04 — the founding graph is acyclic (materially proven).

        A Governance record participates in **no** founding relationship — its relationships
        (AMR-06 holds-state, AMR-08 secured-by, AMR-09 governed-by, AMR-10 identified-by) are all
        reference-only — so its founding graph is empty and therefore trivially acyclic, exactly
        as the State/Security used no founding edge (V4 PASS vacuously). Canonical encodability
        proves the core is well-formed; the no-self-founding guard proves no reference names the
        record itself.
        """
        try:
            canonical_json(self.canonical_core())
        except (TypeError, ValueError):  # pragma: no cover - blocked at construction
            return False
        return self.no_self_founding()

    def no_self_founding(self) -> bool:
        """AMK-03 — no reference founds the governance record on itself (no self-founding cycle)."""
        me = self.self_ref
        return all(
            ref != me
            for ref in (
                self.behavior_ref,
                *self.subject_refs,
                *self.security_refs,
                *self.state_refs,
            )
        )

    def participates_in_founding_edge(self) -> bool:
        """AMK-03 — a Governance record participates in no founding edge (reference-only)."""
        return False

    # -- governance-specific obligations ---------------------------------------

    def governs_boundary(self) -> bool:
        """AMR-09 / AOR-09 / GOV-07 / GOV-K2 — the record governs ≥1 declared boundary."""
        return bool(self.subject_refs) and all(
            isinstance(r, str) and bool(r.strip()) for r in self.subject_refs
        )

    def governed_constructs(self) -> tuple[str, ...]:
        """AMR-09 — the constructs governed-by this record (the governed subjects)."""
        return self.subject_refs

    def evaluative_nonenforcing(self) -> bool:
        """UAL-14 / GOV-03/04 / GOV-C1/C2 — the record is record-only, enacts nothing.

        THE governing law of the Governance concern: a governance record *records* a
        conformance/lifecycle/policy judgment while *conferring no authority* and *approving,
        enforcing, and ratifying nothing*. It is structurally non-enforcing — the construct holds
        only references and a type; it can approve nothing, enforce nothing, ratify nothing, and
        mutate no state.
        """
        return (
            not self.confers_authority()
            and not self.enforces()
            and not self.ratifies()
        )

    def binds_runtime_policy(self) -> bool:
        """AMK-05 / §7 / UAL-10 — the governance-evaluate behavior binds RL-F2 by reference.

        The evaluation behaves-as the frozen RUNTIME policy concern (RUNTIME-010) by ENG-005
        reference; the reference must be non-empty and name no concrete governance technology.
        """
        return bool(self.behavior_ref.strip()) and not _contains_marker(
            self.behavior_ref, _TECHNOLOGY_MARKERS
        )

    def behavior_by_reference(self) -> bool:
        """§7 / UAL-10 — the evaluation binds RL-F2 by a non-empty ENG-005 reference."""
        return bool(self.behavior_ref.strip())

    def secures_by_reference(self) -> bool:
        """AMR-08 / AOR-08 — every referenced Security-conformance ref is a non-empty ENG-005."""
        return all(isinstance(r, str) and bool(r.strip()) for r in self.security_refs)

    def state_by_reference(self) -> bool:
        """AMR-06 / AOR-06 — every held-State ref is a non-empty ENG-005 reference."""
        return all(isinstance(r, str) and bool(r.strip()) for r in self.state_refs)

    @property
    def holds_state(self) -> bool:
        """True iff this governance kind holds a State construct (lifecycle-record, AMR-06)."""
        return self.kind in STATE_BEARING_KINDS

    @property
    def precedence(self) -> int:
        """The deterministic evaluation-precedence rank of the record (AXH-10 order).

        A *lower* rank is evaluated first. This is a decidable, evaluative ordering only
        (UAL-14 / GOV-03): it enacts nothing and confers nothing — it records the deterministic
        order in which governance facets are considered when several apply to one boundary.
        """
        return KIND_PRECEDENCE[self.kind]

    def precedence_decidable(self) -> bool:
        """GOV-08 — the record's evaluation precedence is decidable from its kind."""
        return self.kind in KIND_PRECEDENCE

    def governs(self, subject_ref: str) -> bool:
        """GOV-07 — True iff ``subject_ref`` is within this record's governed boundary."""
        return isinstance(subject_ref, str) and subject_ref in self.subject_refs

    def references_resolve(self) -> bool:
        """AOI-03 / AMK-05/07 — every ENG-005 reference is a non-empty resolvable id."""
        return all(
            isinstance(ref, str) and bool(ref.strip())
            for ref in (
                self.behavior_ref,
                *self.subject_refs,
                *self.security_refs,
                *self.state_refs,
            )
        ) and self.no_self_founding()

    def uses_new_connection_construct(self) -> bool:
        """GOV-C4 analog — True iff any link is not a plain ENG-005 reference string.

        A governance record introduces no new connection construct: every governed/security/
        state/behavior link is an ENG-005 reference (a non-empty string). This is False for a
        well-formed record.
        """
        links = (
            *self.subject_refs,
            *self.security_refs,
            *self.state_refs,
            self.behavior_ref,
        )
        return not all(isinstance(link, str) and bool(link.strip()) for link in links)

    # -- evaluative judgment → recorded judgment (GOV-C1 / AOV-09) -------------

    def record_assessment(self, subject_ref: str, satisfied: bool) -> GovernanceAssessment:
        """Record a governance judgment for ``subject_ref`` — declarative, non-enforcing.

        The *act* of deciding whether the boundary satisfies the governance judgment is the
        RUNTIME policy concern (RUNTIME-010, by reference; §7) — supplied here as ``satisfied``.
        This method only **records** the resulting verdict against the subject's ENG-002 object;
        it enacts nothing, approves nothing, enforces nothing, ratifies nothing, and mutates no
        state (UAL-14 / GOV-C1 / GOV-C2). A subject outside the declared governed boundary
        records ``INAPPLICABLE``.
        """
        _require_reference("subject_ref", subject_ref)
        if not self.governs(subject_ref):
            verdict = GovernanceVerdict.INAPPLICABLE
        else:
            verdict = GovernanceVerdict.SATISFIED if satisfied else GovernanceVerdict.VIOLATED
        return GovernanceAssessment(
            governance_id=self.governance_id,
            subject_ref=subject_ref,
            verdict=verdict,
            kind=self.kind.value,
        )

    # -- non-constitutiveness (UAL-15 / GOV-04/05/09) --------------------------

    def confers_authority(self) -> bool:
        """UAL-14/15 / GOV-09 / C7 — a governance record confers no authority (structurally)."""
        return False

    def enforces(self) -> bool:
        """UAL-14 / GOV-04 / GOV-C2 — a governance record enforces nothing (structurally none)."""
        return False

    def ratifies(self) -> bool:
        """UAL-14 / GOV-04 / GOV-C2/C5 — a governance record ratifies nothing (structurally)."""
        return False

    def selects_technology(self) -> bool:
        """UAL-15 / GOV-K5 / GOV-C3 / C7 — True iff the record names an engine/technology.

        Covers workflow-approval engines, policy-enforcement engines, ratification tooling,
        identity providers, frameworks, transports, or vendors across the whole governance core.
        """
        haystack = canonical_json(self.canonical_core()).lower()
        return any(marker in haystack for marker in _TECHNOLOGY_MARKERS)

    def embeds_secret(self) -> bool:
        """UAL-15 / GOV-09 / RR-07 / C7 — True iff the record appears to embed a secret."""
        haystack = canonical_json(self.canonical_core()).lower()
        return any(marker in haystack for marker in _SECRET_MARKERS)

    def redefines_foundation(self) -> bool:
        """UAL-02 / AMI-05 / VC-5 — a governance record redefines no frozen primitive (reuse)."""
        return False

    # -- lifecycle (UAL-12, forward-only) --------------------------------------

    def transition(self, to_state: GovernanceState) -> Governance:
        """Return a new governance record advanced to ``to_state`` (forward-only; UAL-12).

        Raises:
            GovernanceError: on a backward or in-place-reversing transition.
        """
        if not isinstance(to_state, GovernanceState):
            raise GovernanceError("target state must be an AOS-01…06 GovernanceState (UAL-12)")
        here = LIFECYCLE_ORDER.index(self.state)
        there = LIFECYCLE_ORDER.index(to_state)
        if there < here:
            raise GovernanceError(
                f"lifecycle is forward-only (UAL-12): "
                f"{self.state.value} → {to_state.value} is backward"
            )
        return replace(self, state=to_state)

    # -- serialization ----------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """A deterministic, serializable projection of the governance record."""
        return {
            "governance_id": self.governance_id,
            "meta_class": self.meta_class,
            "type_tag": self.type_tag,
            "kind": self.kind.value,
            "facet": self.facet(),
            "subject_refs": sorted(self.subject_refs),
            "security_refs": sorted(self.security_refs),
            "state_refs": sorted(self.state_refs),
            "behavior_ref": self.behavior_ref,
            "value_digest": self.value_digest,
            "state": self.state.value,
            "precedence": self.precedence,
            "holds_state": self.holds_state,
            "runtime_concern": KIND_RUNTIME_CONCERN[self.kind],
            "is_founding": self.participates_in_founding_edge(),
            "founding_acyclic": self.is_founding_acyclic(),
            "evaluative_nonenforcing": self.evaluative_nonenforcing(),
            "binds_runtime_policy": self.binds_runtime_policy(),
            "relationships": list(self.meta_relationships()),
            "substrate_refs": list(SUBSTRATE_REFS),
        }


@dataclass(frozen=True, slots=True)
class GovernanceCoverage:
    """A recorded, evaluative report of which AXH-10 facets govern a given boundary.

    Coverage is an **evaluative record** (APPLICATION-014 §11 conformance/coverage map): for one
    governed boundary it records which of the three AXH-10 governance facets are present and which
    are absent. Recording coverage enacts nothing and confers no authority (UAL-14 / GOV-03); an
    absent facet is a *recorded observation*, never an enforced requirement.
    """

    subject_ref: str
    facets_present: tuple[str, ...]
    facets_absent: tuple[str, ...]

    @property
    def fully_covered(self) -> bool:
        """True iff every AXH-10 facet governs this boundary (no absent facet)."""
        return not self.facets_absent

    def to_dict(self) -> dict[str, Any]:
        return {
            "coverage_format": "ucos-application-governance-coverage/1.0.0",
            "subject_ref": self.subject_ref,
            "facets_present": list(self.facets_present),
            "facets_absent": list(self.facets_absent),
            "fully_covered": self.fully_covered,
            "assessment": "evaluative record; records only, enacts nothing",
        }


def assess_governance_coverage(
    governance_records: tuple[Governance, ...],
) -> tuple[GovernanceCoverage, ...]:
    """Report AXH-10 governance coverage per boundary — evaluative, non-enforcing.

    For each governed boundary (AMR-09 subject) across ``governance_records``, records which of
    the three AXH-10 facets (Conformance / Lifecycle / Policy) govern it and which are absent.
    The report is deterministic and records only; it approves nothing, blocks nothing, and
    requires nothing (APPLICATION-014 §11 / UAL-14 / GOV-03). Facets are ordered by their AXH-10
    declaration order (via :data:`KIND_PRECEDENCE`).
    """
    all_facets = tuple(k.value for k in sorted(GovernanceKind, key=lambda k: KIND_PRECEDENCE[k]))
    present: dict[str, set[str]] = {}
    for record in governance_records:
        for subject_ref in record.subject_refs:
            present.setdefault(subject_ref, set()).add(record.kind.value)

    coverage: list[GovernanceCoverage] = []
    for subject_ref in sorted(present):
        facets = present[subject_ref]
        coverage.append(
            GovernanceCoverage(
                subject_ref=subject_ref,
                facets_present=tuple(f for f in all_facets if f in facets),
                facets_absent=tuple(f for f in all_facets if f not in facets),
            )
        )
    return tuple(coverage)


def make_governance(
    type_tag: str,
    subject_refs: tuple[str, ...],
    *,
    kind: GovernanceKind = GovernanceKind.CONFORMANCE,
    security_refs: tuple[str, ...] = (),
    state_refs: tuple[str, ...] = (),
    behavior_ref: str = "",
    state: GovernanceState = GovernanceState.DEFINED,
) -> Governance:
    """Construct a well-formed :class:`Governance` record (fail-closed factory)."""
    return Governance(
        type_tag=type_tag,
        kind=kind,
        subject_refs=subject_refs,
        security_refs=security_refs,
        state_refs=state_refs,
        behavior_ref=behavior_ref,
        state=state,
    )


__all__ = [
    "GOVERNANCE_ID_PREFIX",
    "FOUNDATION_REUSE",
    "GovernanceError",
    "GovernanceVerdict",
    "GovernanceAssessment",
    "Governance",
    "GovernanceCoverage",
    "assess_governance_coverage",
    "make_governance",
]
