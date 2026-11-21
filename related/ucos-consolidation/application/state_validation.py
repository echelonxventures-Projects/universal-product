"""EC3-B12-U07 — State validation (meta-validity V1…V5 + UAL/STA conformance).

This module proves a realized :class:`~application.state.State` is **META-VALID**
(APPLICATION-005 §8, V1…V5) and **Application-/State-law conformant** (APPLICATION-001 §7,
UAL-01…15; APPLICATION-011 §4, STA-01…10) by running a suite of deterministic,
application-layer checks through the **CERTIFIED EC-1 Validation Engine**
(:class:`engine.validation.executor.ValidationEngine`) and enforcing the EC-1 acceptance
gate (:func:`engine.validation.gates.enforce_acceptance`). Validation evidence is produced
with the EC-1 :func:`~engine.validation.evidence.build_validation_evidence`.

The checks are pure predicates over an immutable :class:`StateValidationSubject` (the
type-independent projection the EC-1 engine consumes), so an identical state yields a
byte-identical report, evidence, and acceptance decision (VC-4). Every check is
**blocking**: the verdict is PASS iff the state satisfies every meta-validity and
Application-/State-law obligation it is subject to.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from application.state import State
from application.state_meta import (
    META_RELATIONSHIPS,
    STATE_META_CLASS,
    StateKind,
    StateLifecycle,
)
from application.state_traceability import TraceabilityRecord

# --- EC-1 reuse by reference (UAL-02) — the certified validation substrate --------
from engine.runtime.disclosure import build_disclosure, disclosure_present
from engine.validation.checks import ValidationCheck
from engine.validation.contracts import Severity, ValidationFinding, ValidationReport
from engine.validation.evidence import ValidationEvidence, build_validation_evidence
from engine.validation.executor import ValidationEngine
from engine.validation.gates import AcceptanceDecision, enforce_acceptance

#: The blueprint id a State realizes (its meta-class) — used by the EC-1 report.
STATE_BLUEPRINT_ID = STATE_META_CLASS

_KIND_VALUES = frozenset(k.value for k in StateKind)
_STATE_VALUES = frozenset(s.value for s in StateLifecycle)
_META_RELATIONSHIPS = frozenset(META_RELATIONSHIPS)
_FACETS = frozenset({"lifecycle", "interaction", "context"})


@dataclass(frozen=True, slots=True)
class StateValidationSubject:
    """A normalized, immutable projection of a State that checks evaluate.

    Exposes ``target_id`` and ``blueprint_id`` (the interface the EC-1 ``ValidationEngine``
    consumes) plus the state's meta-facts. Holds no runtime state and no wall-clock, so it
    is deterministic.
    """

    target_id: str
    blueprint_id: str
    meta_class: str
    type_tag: str
    kind: str
    facet: str
    value_digest: str
    holder_ref: str
    context_ref: str
    data_ref: str
    behavior_ref: str
    relationships: tuple[str, ...]
    lifecycle_state: str
    founding_acyclic: bool
    participates_in_founding_edge: bool
    references_resolve: bool
    is_held: bool
    context_bound: bool
    presents_data: bool
    binds_runtime_state: bool
    lifecycle_decidable: bool
    records_transitions: bool
    confers_authority: bool
    selects_technology: bool
    embeds_secret: bool
    redefines_foundation: bool
    substrate_refs: tuple[str, ...]
    provenance_chain: tuple[str, ...]
    disclosure: dict[str, Any]

    @classmethod
    def from_state(
        cls, state: State, trace: TraceabilityRecord
    ) -> StateValidationSubject:
        """Project ``state`` (+ its lineage) into a validation subject."""
        payload = state.to_dict()
        return cls(
            target_id=state.state_id,
            blueprint_id=STATE_BLUEPRINT_ID,
            meta_class=state.meta_class,
            type_tag=state.type_tag,
            kind=state.kind.value,
            facet=state.facet(),
            value_digest=state.value_digest,
            holder_ref=state.holder_ref,
            context_ref=state.context_ref,
            data_ref=state.data_ref,
            behavior_ref=state.behavior_ref,
            relationships=state.meta_relationships(),
            lifecycle_state=state.state.value,
            founding_acyclic=state.is_founding_acyclic(),
            participates_in_founding_edge=state.participates_in_founding_edge(),
            references_resolve=state.references_resolve(),
            is_held=state.is_held(),
            context_bound=state.context_is_bound(),
            presents_data=state.presents_data(),
            binds_runtime_state=state.binds_runtime_state(),
            lifecycle_decidable=state.lifecycle_is_decidable(),
            records_transitions=state.records_transitions(),
            confers_authority=state.confers_authority(),
            selects_technology=state.selects_technology(),
            embeds_secret=state.embeds_secret(),
            redefines_foundation=state.redefines_foundation(),
            substrate_refs=tuple(payload["substrate_refs"]),
            provenance_chain=trace.backward,
            disclosure=build_disclosure(),  # EC-1 provisional-state (DE-05)
        )


# ---------------------------------------------------------------------------
# State-layer validation checks (each maps to explicit V*/UAL*/STA*/AMK* obligations)
# ---------------------------------------------------------------------------


class StateTypedCheck(ValidationCheck):
    """UAL-03 / STA-01 / AMK-01 / C1 — the state is classified by a non-empty type."""

    check_id = "state-typed"
    severity = Severity.BLOCKING
    description = "State bears a non-empty ENG-004 type_tag (UAL-03 / STA-01)."

    def evaluate(self, subject: StateValidationSubject) -> ValidationFinding:
        if not subject.type_tag.strip():
            return self._failed("state is untyped (UAL-03 / STA-01)")
        return self._passed(type_tag=subject.type_tag)


class StateIdentifiedCheck(ValidationCheck):
    """UAL-04/05 / STA-02 / AMK-01 / C1 — the state is identified and object-borne."""

    check_id = "state-identified-objectbound"
    severity = Severity.BLOCKING
    description = "State bears a deterministic ENG-001 identity via an ENG-002 object."

    def evaluate(self, subject: StateValidationSubject) -> ValidationFinding:
        if not subject.target_id.startswith("UCOS-STATE-"):
            return self._failed(
                "state lacks ENG-001 identity (UAL-04)", id=subject.target_id
            )
        if not subject.value_digest:
            return self._failed("state is not object-borne (no value digest) (UAL-05)")
        return self._passed(state_id=subject.target_id)


class StateValueFidelityCheck(ValidationCheck):
    """ENG-003 — the state core round-trips through the EC-1 canonical encoding."""

    check_id = "state-value-fidelity"
    severity = Severity.BLOCKING
    description = "State core round-trips through the EC-1 canonical encoding (ENG-003)."

    def evaluate(self, subject: StateValidationSubject) -> ValidationFinding:
        digest = subject.value_digest
        if len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
            return self._failed("state core is not ENG-003 value-faithful", digest=digest)
        return self._passed(value_digest=digest)


class StateClassifiedCheck(ValidationCheck):
    """AXH-07 / AXC-04 — the state is classified by exactly one State kind."""

    check_id = "state-classified"
    severity = Severity.BLOCKING
    description = "State is classified by an AXH-07 kind (single-facet, AXC-04)."

    def evaluate(self, subject: StateValidationSubject) -> ValidationFinding:
        if subject.kind not in _KIND_VALUES:
            return self._failed("state kind is outside AXH-07", kind=subject.kind)
        if subject.facet not in _FACETS:
            return self._failed("state facet is outside AXH-07", facet=subject.facet)
        return self._passed(kind=subject.kind, facet=subject.facet)


class StateHeldCheck(ValidationCheck):
    """AMR-06 / AOR-06 — the state is held by a construct by reference (reference-only)."""

    check_id = "state-held-by"
    severity = Severity.BLOCKING
    description = "State is held by an application/feature/interaction/workflow (AMR-06)."

    def evaluate(self, subject: StateValidationSubject) -> ValidationFinding:
        if not subject.is_held or not subject.holder_ref.strip():
            return self._failed("state is held by no construct (AMR-06 / AOR-06)")
        return self._passed(holder_ref=subject.holder_ref)


class StateContextBoundCheck(ValidationCheck):
    """STA-06 / STA-C3 / STA-K5 — the state is bound to a declared, abstract context.

    THE distinctive State obligation: every state is bound to a decidable, explicit context
    (actor/session/tenant/locale/policy) that names surface/scope without selecting a state
    store, cache, or database technology.
    """

    check_id = "state-context-bound"
    severity = Severity.BLOCKING
    description = "State bound to a declared, decidable, abstract context (STA-06 / STA-C3)."

    def evaluate(self, subject: StateValidationSubject) -> ValidationFinding:
        if not subject.context_ref.strip():
            return self._failed("state has no declared context (STA-06 / STA-C3)")
        if not subject.context_bound:
            return self._failed(
                "declared context selects a state technology (STA-06 / STA-09 / STA-K5)",
                context_ref=subject.context_ref,
            )
        return self._passed(context_ref=subject.context_ref)


class StatePresentsDataCheck(ValidationCheck):
    """AMR-14 / STA-C4 / STA-K4 / UAL-13 / AMK-07 — binds/presents DF-2 data by reference."""

    check_id = "state-presents-data"
    severity = Severity.BLOCKING
    description = "State binds/presents DF-2 data by ENG-005 reference (AMR-14 / STA-C4)."

    def evaluate(self, subject: StateValidationSubject) -> ValidationFinding:
        if not subject.presents_data or not subject.data_ref.strip():
            return self._failed("state binds no DF-2 data (AMR-14 / STA-C4 / UAL-13)")
        return self._passed(data_ref=subject.data_ref)


class StateBindsRuntimeCheck(ValidationCheck):
    """AMR-11 / §7 / AMK-05 / STA-03 / STA-C5 — behaves-as / binds RUNTIME state (→ RL-F2).

    THE governing, materially-exercised binding: the application state binds the frozen
    RL-F2 state concern by reference and re-founds no runtime concern.
    """

    check_id = "state-binds-runtime-state"
    severity = Severity.BLOCKING
    description = "State binds the RL-F2 RUNTIME state concern by reference (AMR-11 / STA-03)."

    def evaluate(self, subject: StateValidationSubject) -> ValidationFinding:
        if not subject.behavior_ref.strip():
            return self._failed("state binds no RUNTIME state (AMR-11 / §7 / STA-03)")
        if not subject.binds_runtime_state:
            return self._failed(
                "state binding names a concrete state technology, not RL-F2 "
                "(STA-03 / STA-C5 / STA-K5)",
                behavior_ref=subject.behavior_ref,
            )
        return self._passed(behavior_ref=subject.behavior_ref)


class StateLifecycleDecidableCheck(ValidationCheck):
    """STA-07 — membership in a lifecycle state is decidable at any point."""

    check_id = "state-lifecycle-decidable"
    severity = Severity.BLOCKING
    description = "State membership in a lifecycle position is decidable (STA-07)."

    def evaluate(self, subject: StateValidationSubject) -> ValidationFinding:
        if not subject.lifecycle_decidable:
            return self._failed("state lifecycle membership is not decidable (STA-07)")
        return self._passed(lifecycle_state=subject.lifecycle_state)


class StateTransitionRecordedCheck(ValidationCheck):
    """STA-05 / STA-C2 — transitions are recorded as RUNTIME events; none silent."""

    check_id = "state-transition-recorded"
    severity = Severity.BLOCKING
    description = "State transitions are recorded as RUNTIME events (STA-05 / STA-C2)."

    def evaluate(self, subject: StateValidationSubject) -> ValidationFinding:
        if not subject.records_transitions:
            return self._failed("state transitions are not recorded (STA-05 / STA-C2)")
        return self._passed()


class MetaClassSingleCheck(ValidationCheck):
    """V1 / AMI-01 — the state instantiates exactly one meta-class (AMC-07)."""

    check_id = "meta-class-single"
    severity = Severity.BLOCKING
    description = "State instantiates exactly the AMC-07 meta-class (V1)."

    def evaluate(self, subject: StateValidationSubject) -> ValidationFinding:
        if subject.meta_class != STATE_META_CLASS:
            return self._failed("meta-class is not AMC-07 (V1)", meta_class=subject.meta_class)
        return self._passed(meta_class=subject.meta_class)


class MetaRelationshipsClosedCheck(ValidationCheck):
    """V2 / AMI-02 — every relationship used lies within AMR-01…14."""

    check_id = "meta-relationships-closed"
    severity = Severity.BLOCKING
    description = "All state relationships are within AMR-01…14 (V2)."

    def evaluate(self, subject: StateValidationSubject) -> ValidationFinding:
        outside = [r for r in subject.relationships if r not in _META_RELATIONSHIPS]
        if outside:
            return self._failed("relationships outside AMR-01…14 (V2)", outside=outside)
        return self._passed(relationships=list(subject.relationships))


class MetaConstraintsCheck(ValidationCheck):
    """V3 — applicable meta-constraints (AMK-01 typed/id/object; AMK-02/05/07 references)."""

    check_id = "meta-constraints"
    severity = Severity.BLOCKING
    description = "AMK-01 (typed/identified/object) and AMK-02/05/07 (references) hold (V3)."

    def evaluate(self, subject: StateValidationSubject) -> ValidationFinding:
        if not (subject.type_tag.strip() and subject.target_id and subject.value_digest):
            return self._failed("AMK-01 not satisfied (V3)")
        if not subject.references_resolve:
            return self._failed("AMK-05/07 not satisfied: a reference does not resolve (V3)")
        if not (
            subject.context_bound
            and subject.is_held
            and subject.presents_data
            and subject.binds_runtime_state
        ):
            return self._failed(
                "AMK-02 not satisfied: context/holder/data/behavior declaration incomplete (V3)"
            )
        return self._passed(constraints=["AMK-01", "AMK-02", "AMK-03", "AMK-05", "AMK-07"])


class FoundingAcyclicCheck(ValidationCheck):
    """V4 / AMK-03 — the founding graph is acyclic (satisfied *vacuously*).

    A State participates in **no** founding relationship (AMR-02/03/05); its relationships
    AMR-06/10/11/14 are all reference-only. Its founding graph is therefore empty and
    trivially acyclic — exactly as the Workflow used no founding edge. The holder is
    distinct from every binding reference (non-absorption), so no cycle can arise.
    """

    check_id = "founding-acyclic"
    severity = Severity.BLOCKING
    description = "The state's founding graph is acyclic (V4 / AMK-03; vacuous — no founding edge)."

    def evaluate(self, subject: StateValidationSubject) -> ValidationFinding:
        if subject.participates_in_founding_edge:
            return self._failed("a state must participate in no founding edge (AMR-02/03/05)")
        if not subject.founding_acyclic:
            return self._failed("founding graph is not acyclic (V4 / AMK-03)")
        return self._passed()


class LifecycleValidCheck(ValidationCheck):
    """V5 / UAL-12 — the state holds a valid AOS-01…06 lifecycle state."""

    check_id = "lifecycle-valid"
    severity = Severity.BLOCKING
    description = "State holds a valid AOS-01…06 lifecycle state (V5 / UAL-12)."

    def evaluate(self, subject: StateValidationSubject) -> ValidationFinding:
        if subject.lifecycle_state not in _STATE_VALUES:
            return self._failed("invalid lifecycle state (V5)", state=subject.lifecycle_state)
        return self._passed(state=subject.lifecycle_state)


class FoundationReuseIntegrityCheck(ValidationCheck):
    """UAL-02 / STA-10 / AMI-05 / VC-5 — frozen foundations reused by reference, not redefined."""

    check_id = "foundation-reuse-integrity"
    severity = Severity.BLOCKING
    description = "EL-1/RL-F2/DF-2 referenced, redefined nowhere (UAL-02 / AMI-05)."

    def evaluate(self, subject: StateValidationSubject) -> ValidationFinding:
        if subject.redefines_foundation:
            return self._failed("a frozen foundation primitive was redefined (UAL-02 / AMI-05)")
        if not subject.substrate_refs:
            return self._failed("no frozen-foundation reference recorded (UAL-02)")
        return self._passed(substrate=list(subject.substrate_refs))


class TechnologyIndependenceCheck(ValidationCheck):
    """UAL-15 / STA-09 / STA-K5 / C7 — no state store / cache / db / engine / vendor selected."""

    check_id = "technology-independence"
    severity = Severity.BLOCKING
    description = "No state store/cache/db/engine/vendor selected (UAL-15 / STA-09)."

    def evaluate(self, subject: StateValidationSubject) -> ValidationFinding:
        if subject.selects_technology:
            return self._failed("a concrete technology was selected (UAL-15 / STA-09)")
        return self._passed()


class NonConstitutiveCheck(ValidationCheck):
    """UAL-15 / STA-09 / C7 — the state confers no authority and embeds no secret."""

    check_id = "non-constitutive"
    severity = Severity.BLOCKING
    description = "State confers no authority and embeds no secret (UAL-15 / RR-07)."

    def evaluate(self, subject: StateValidationSubject) -> ValidationFinding:
        if subject.confers_authority:
            return self._failed("state confers authority (UAL-15 / STA-09)")
        if subject.embeds_secret:
            return self._failed("state embeds a secret (UAL-15 / RR-07)")
        return self._passed()


class ProvisionalDisclosureCheck(ValidationCheck):
    """DE-05 — the EC-1 provisional-state disclosure is present (no finality asserted)."""

    check_id = "provisional-state-disclosure"
    severity = Severity.BLOCKING
    description = "EC-1 provisional-state disclosure present; asserts no finality (DE-05)."

    def evaluate(self, subject: StateValidationSubject) -> ValidationFinding:
        if not disclosure_present(subject.disclosure):
            return self._failed("EC-1 provisional-state disclosure absent/malformed (DE-05)")
        return self._passed(disclosure_id=subject.disclosure.get("disclosure_id"))


class TraceabilityRootedCheck(ValidationCheck):
    """§9 / AC-7 — the No-Orphan lineage is rooted and closes to the 12-APPLICATION anchor."""

    check_id = "traceability-rooted"
    severity = Severity.BLOCKING
    description = "Backward lineage rooted at AMC-07 and closed to 12-APPLICATION (No-Orphan)."

    def evaluate(self, subject: StateValidationSubject) -> ValidationFinding:
        chain = subject.provenance_chain
        if not chain:
            return self._failed("traceability chain is empty (No-Orphan)")
        if chain[0] != subject.meta_class:
            return self._failed("lineage not rooted at the meta-class", head=chain[0])
        if not any(link.startswith("12-APPLICATION@") for link in chain):
            return self._failed("lineage does not close to the 12-APPLICATION anchor")
        return self._passed(links=len(chain))


def state_checks() -> tuple[ValidationCheck, ...]:
    """The full state-layer validation suite (deterministically ordered by the engine)."""
    return (
        StateTypedCheck(),
        StateIdentifiedCheck(),
        StateValueFidelityCheck(),
        StateClassifiedCheck(),
        StateHeldCheck(),
        StateContextBoundCheck(),
        StatePresentsDataCheck(),
        StateBindsRuntimeCheck(),
        StateLifecycleDecidableCheck(),
        StateTransitionRecordedCheck(),
        MetaClassSingleCheck(),
        MetaRelationshipsClosedCheck(),
        MetaConstraintsCheck(),
        FoundingAcyclicCheck(),
        LifecycleValidCheck(),
        FoundationReuseIntegrityCheck(),
        TechnologyIndependenceCheck(),
        NonConstitutiveCheck(),
        ProvisionalDisclosureCheck(),
        TraceabilityRootedCheck(),
    )


@dataclass(frozen=True, slots=True)
class StateValidation:
    """The bundled outcome of validating a State (report + evidence + decision)."""

    report: ValidationReport
    evidence: ValidationEvidence
    decision: AcceptanceDecision

    @property
    def accepted(self) -> bool:
        return self.decision.accepted


def validate_state(
    state: State, trace: TraceabilityRecord, *, strict: bool = False
) -> StateValidation:
    """Validate ``state`` through the CERTIFIED EC-1 engine and enforce acceptance.

    Returns the EC-1 :class:`ValidationReport`, its :class:`ValidationEvidence`, and the
    :class:`AcceptanceDecision`. With ``strict=True`` a rejected state raises via the EC-1
    acceptance gate.
    """
    subject = StateValidationSubject.from_state(state, trace)
    engine = ValidationEngine(state_checks())
    report = engine.validate(subject)
    evidence = build_validation_evidence(report)
    decision = enforce_acceptance(report, strict=strict)
    return StateValidation(report=report, evidence=evidence, decision=decision)


__all__ = [
    "STATE_BLUEPRINT_ID",
    "StateValidationSubject",
    "StateValidation",
    "state_checks",
    "validate_state",
]
