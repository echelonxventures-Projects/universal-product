"""EC3-B10-U06 — Lifecycle validation (meta-validity V1…V5 + UDL + DLA conformance).

This module proves a realized :class:`~data.lifecycle.Lifecycle` is **META-VALID**
(DATA-005 §8, V1…V5), **Data-law conformant** (DATA-001 §7, esp. **UDL-12 Lifecycle
Governance**, UDL-03, UDL-04/05, UDL-02, UDL-09, UDL-13, UDL-15), and satisfies the
Lifecycle contracts (DATA-011 §10, DLA-K1/K3/K4/K5 + the transition rules
DLA-C1/C2/C4/C5) by running a suite of deterministic, data-layer checks through the
**CERTIFIED EC-1 Validation Engine** (:class:`engine.validation.executor.ValidationEngine`)
and enforcing the EC-1 acceptance gate. Validation evidence is produced with the EC-1
:func:`~engine.validation.evidence.build_validation_evidence`.

The checks are pure predicates over an immutable :class:`LifecycleValidationSubject`, so
an identical lifecycle yields a byte-identical report, evidence, and acceptance decision
(VC-4). Every check is **blocking**. A subset of check ids (``meta-class-single``,
``meta-relationships-closed``, ``foundation-reuse-integrity``, ``data-value-fidelity``,
``founding-acyclic``, ``provisional-state-disclosure``, ``traceability-rooted``) is
**shared with the CERTIFIED DMC-01 surface**, so the DMC-01 CCE ten-gate suite
(:func:`data.certification.cce_gates`) is reused verbatim by the Lifecycle certification
(UDL-02 reuse-by-reference).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from data.lifecycle import Lifecycle
from data.lifecycle_meta import (
    LIFECYCLE_META_CLASS,
    LIFECYCLE_RELATIONSHIPS,
    LifecycleState,
    StateFacet,
)
from data.traceability import TraceabilityRecord

# --- EC-1 reuse by reference (UDL-02) — the certified validation substrate -------
from engine.runtime.disclosure import build_disclosure, disclosure_present
from engine.validation.checks import ValidationCheck
from engine.validation.contracts import Severity, ValidationFinding, ValidationReport
from engine.validation.evidence import ValidationEvidence, build_validation_evidence
from engine.validation.executor import ValidationEngine
from engine.validation.gates import AcceptanceDecision, enforce_acceptance

#: The blueprint id a Lifecycle realizes (its meta-class) — used by the EC-1 report.
LIFECYCLE_BLUEPRINT_ID = LIFECYCLE_META_CLASS

_STATE_VALUES = frozenset(s.value for s in LifecycleState)
_FACET_VALUES = frozenset(f.value for f in StateFacet)
_META_RELATIONSHIPS = frozenset(LIFECYCLE_RELATIONSHIPS)


@dataclass(frozen=True, slots=True)
class LifecycleValidationSubject:
    """A normalized, immutable projection of a Lifecycle that checks evaluate.

    Exposes ``target_id`` and ``blueprint_id`` (the interface the EC-1
    ``ValidationEngine`` consumes) plus the lifecycle's meta-facts. Holds no runtime
    state and no wall-clock, so it is deterministic.
    """

    target_id: str
    blueprint_id: str
    meta_class: str
    name: str
    type_tag: str
    value_digest: str
    transitioned_entity_id: str
    transition_pairs: tuple[tuple[str, str], ...]
    guard_refs: tuple[str, ...]
    event_refs: tuple[str, ...]
    states: tuple[str, ...]
    states_closed: bool
    current_state: str
    facet: str
    single_state: bool
    forward_only: bool
    transitions_guarded: bool
    transitions_recorded: bool
    guards_non_enforcing: bool
    represents_retention: bool
    state_ref: str
    binds_runtime_by_reference: bool
    names_technology: bool
    classified: bool
    absorbs_subject: bool
    version: str
    relationships: tuple[str, ...]
    lifecycle_state: str
    founding_acyclic: bool
    confers_authority: bool
    embeds_secret: bool
    redefines_el1: bool
    substrate_refs: tuple[str, ...]
    provenance_chain: tuple[str, ...]
    image_reference: str
    disclosure: dict[str, Any]

    @classmethod
    def from_lifecycle(
        cls, lifecycle: Lifecycle, trace: TraceabilityRecord
    ) -> LifecycleValidationSubject:
        """Project ``lifecycle`` (+ its lineage) into a validation subject."""
        return cls(
            target_id=lifecycle.lifecycle_id,
            blueprint_id=LIFECYCLE_BLUEPRINT_ID,
            meta_class=lifecycle.meta_class,
            name=lifecycle.name,
            type_tag=lifecycle.type_tag,
            value_digest=lifecycle.structure_digest,
            transitioned_entity_id=lifecycle.transitioned_entity_id(),
            transition_pairs=lifecycle.transition_pairs(),
            guard_refs=lifecycle.guard_refs(),
            event_refs=lifecycle.event_refs(),
            states=tuple(s.value for s in lifecycle.states()),
            states_closed=lifecycle.states_are_closed(),
            current_state=lifecycle.current_state.value,
            facet=lifecycle.facet.value,
            single_state=lifecycle.is_single_state(),
            forward_only=lifecycle.is_forward_only(),
            transitions_guarded=lifecycle.transitions_are_guarded(),
            transitions_recorded=lifecycle.transitions_are_recorded(),
            guards_non_enforcing=lifecycle.guards_are_non_enforcing(),
            represents_retention=lifecycle.represents_retention(),
            state_ref=lifecycle.state_ref,
            binds_runtime_by_reference=lifecycle.binds_runtime_by_reference(),
            names_technology=lifecycle.names_technology(),
            classified=lifecycle.is_classified(),
            absorbs_subject=lifecycle.absorbs_subject(),
            version=lifecycle.version,
            relationships=lifecycle.meta_relationships(),
            lifecycle_state=lifecycle.current_state.value,
            founding_acyclic=lifecycle.is_founding_acyclic(),
            confers_authority=lifecycle.confers_authority(),
            embeds_secret=lifecycle.embeds_secret(),
            redefines_el1=lifecycle.redefines_el1(),
            substrate_refs=tuple(lifecycle.to_dict()["substrate_refs"]),
            provenance_chain=trace.backward,
            image_reference="",  # a lifecycle is a description, not a deployable image
            disclosure=build_disclosure(),  # EC-1 provisional-state (DE-05)
        )


# ---------------------------------------------------------------------------
# Data-layer validation checks (each maps to explicit V*/UDL*/DLA* obligations)
# ---------------------------------------------------------------------------


class LifecycleTypedCheck(ValidationCheck):
    """UDL-03 / DLA-K1 — lifecycle is classified by a non-empty ENG-004 type."""

    check_id = "lifecycle-typed"
    severity = Severity.BLOCKING
    description = "Lifecycle bears a non-empty ENG-004 type_tag (DLA-K1 / UDL-03)."

    def evaluate(self, subject: LifecycleValidationSubject) -> ValidationFinding:
        if not subject.type_tag.strip():
            return self._failed("lifecycle is untyped (DLA-K1 / UDL-03)")
        return self._passed(type_tag=subject.type_tag)


class LifecycleNamedCheck(ValidationCheck):
    """DLA-K1 — lifecycle has an explicit, decidable name."""

    check_id = "lifecycle-named"
    severity = Severity.BLOCKING
    description = "Lifecycle has an explicit, non-empty name."

    def evaluate(self, subject: LifecycleValidationSubject) -> ValidationFinding:
        if not subject.name.strip():
            return self._failed("lifecycle is unnamed")
        return self._passed(name=subject.name)


class LifecycleIdentifiedCheck(ValidationCheck):
    """UDL-04/05 / DLA-K1 / DMK-01 / C1 — lifecycle is identified (ENG-001), object-borne."""

    check_id = "lifecycle-identified"
    severity = Severity.BLOCKING
    description = "Lifecycle bears a deterministic ENG-001 identity via an ENG-002 object."

    def evaluate(self, subject: LifecycleValidationSubject) -> ValidationFinding:
        if not subject.target_id.startswith("UCOS-LIFECYCLE-"):
            return self._failed("lifecycle has no ENG-001 identity (UDL-04)", id=subject.target_id)
        return self._passed(lifecycle_id=subject.target_id)


class LifecycleValueFidelityCheck(ValidationCheck):
    """UDL-06 (transitive) / C3 — the lifecycle's representation is ENG-003 value-faithful."""

    check_id = "data-value-fidelity"  # shared id — reused by the DMC-01 CCE gate suite
    severity = Severity.BLOCKING
    description = "Lifecycle representation is content-addressed via ENG-003 encoding (UDL-06)."

    def evaluate(self, subject: LifecycleValidationSubject) -> ValidationFinding:
        digest = subject.value_digest
        if len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
            return self._failed("lifecycle representation is not value-faithful (UDL-06)", d=digest)
        return self._passed(value_digest=digest)


class LifecycleTransitionsSubjectCheck(ValidationCheck):
    """DMR-06 / DOR-06 / DLA-07 — lifecycle transitions a CERTIFIED entity by reference."""

    check_id = "lifecycle-transitions-subject"
    severity = Severity.BLOCKING
    description = "Lifecycle transitions a CERTIFIED entity by reference; owns none (DMR-06)."

    def evaluate(self, subject: LifecycleValidationSubject) -> ValidationFinding:
        eid = subject.transitioned_entity_id
        if not eid.startswith("UCOS-ENTITY-"):
            return self._failed("transitioned subject is not a CERTIFIED Entity (DMR-06)", eid=eid)
        if subject.absorbs_subject:
            return self._failed("lifecycle owns/absorbs its subject (DLA-07 / DMX-02)")
        return self._passed(transitions=eid)


class LifecycleStatesClosedCheck(ValidationCheck):
    """DLA-02 / DOS-01…05 — the lifecycle's state set is the closed forward-only set."""

    check_id = "lifecycle-states-closed"
    severity = Severity.BLOCKING
    description = "Lifecycle state set is the closed DOS-01…05 set (DLA-02)."

    def evaluate(self, subject: LifecycleValidationSubject) -> ValidationFinding:
        if not subject.states_closed:
            return self._failed("lifecycle state set is not the closed DOS-01…05 set (DLA-02)")
        bad = [s for s in subject.states if s not in _STATE_VALUES]
        if bad:
            return self._failed("a lifecycle state is outside DOS-01…05 (DLA-02)", bad=bad)
        return self._passed(states=list(subject.states))


class LifecycleForwardOnlyCheck(ValidationCheck):
    """DLA-01 / DLA-C1 / DLA-K3 — every declared transition is forward-only."""

    check_id = "lifecycle-forward-only"
    severity = Severity.BLOCKING
    description = "Every lifecycle transition is forward-only (DLA-01 / DLA-C1 / DLA-K3)."

    def evaluate(self, subject: LifecycleValidationSubject) -> ValidationFinding:
        if not subject.transition_pairs:
            return self._failed("lifecycle declares no transition (DLA-C1)")
        order = list(subject.states)
        for src, dst in subject.transition_pairs:
            if src not in order or dst not in order or order.index(dst) <= order.index(src):
                return self._failed("a transition is not forward-only (DLA-01)", pair=(src, dst))
        if not subject.forward_only:
            return self._failed("lifecycle is not forward-only (DLA-01)")
        return self._passed(transitions=len(subject.transition_pairs))


class LifecycleGuardedCheck(ValidationCheck):
    """DLA-04 / DLA-C2 / DLA-K4 — every transition declares a non-enforcing guard."""

    check_id = "lifecycle-transitions-guarded"
    severity = Severity.BLOCKING
    description = "Every transition declares a declarative, non-enforcing guard (DLA-04 / DLA-K4)."

    def evaluate(self, subject: LifecycleValidationSubject) -> ValidationFinding:
        if not subject.transitions_guarded:
            return self._failed("a transition declares no guard (DLA-04 / DLA-C2)")
        bad = [g for g in subject.guard_refs if not g.startswith("UCOS-GUARD-REF:")]
        if bad:
            return self._failed("a guard is not a declarative reference (DLA-04)", bad=bad)
        if not subject.guards_non_enforcing:
            return self._failed("a guard is enforcing (DLA-K4 — guards evaluate, do not enact)")
        return self._passed(guards=len(subject.guard_refs))


class LifecycleRecordedCheck(ValidationCheck):
    """DLA-03 / DLA-C2 / DMR-11 — every transition records a RUNTIME event by reference."""

    check_id = "lifecycle-transitions-recorded"
    severity = Severity.BLOCKING
    description = "Every transition records a RUNTIME event reference; no silent transition."

    def evaluate(self, subject: LifecycleValidationSubject) -> ValidationFinding:
        if not subject.transitions_recorded:
            return self._failed("a transition records no RUNTIME event (DLA-03 / DLA-C2)")
        bad = [e for e in subject.event_refs if not e.startswith("UCOS-RUNTIME-REF:")]
        if bad:
            return self._failed("a recorded event is not a RUNTIME reference (DLA-03)", bad=bad)
        return self._passed(events=len(subject.event_refs))


class LifecycleSingleStateCheck(ValidationCheck):
    """DLA-C5 — the lifecycle is in exactly one current state; that state is valid (V5)."""

    check_id = "lifecycle-single-state"
    severity = Severity.BLOCKING
    description = "Lifecycle is in exactly one valid current DOS-01…05 state (DLA-C5)."

    def evaluate(self, subject: LifecycleValidationSubject) -> ValidationFinding:
        if not subject.single_state:
            return self._failed("lifecycle is not in a single state (DLA-C5)")
        if subject.current_state not in _STATE_VALUES:
            return self._failed("current state outside DOS-01…05 (DLA-C5)", v=subject.current_state)
        return self._passed(current_state=subject.current_state)


class LifecycleBehavesByReferenceCheck(ValidationCheck):
    """DMR-11 / DLA-07 / DOB-02 — state/event behavior binds a RUNTIME reference (not redefined)."""

    check_id = "lifecycle-behaves-by-reference"
    severity = Severity.BLOCKING
    description = "State/event behavior binds a RUNTIME reference; no engine redefined (DMR-11)."

    def evaluate(self, subject: LifecycleValidationSubject) -> ValidationFinding:
        if not subject.state_ref.startswith("UCOS-RUNTIME-REF:"):
            return self._failed("state does not bind a RUNTIME reference (DMR-11 / DLA-07)")
        if not subject.binds_runtime_by_reference:
            return self._failed("lifecycle behavior is not bound by reference (DMR-11 / DLA-07)")
        return self._passed(state_ref=subject.state_ref)


class LifecycleIndependenceCheck(ValidationCheck):
    """UDL-12 / DLA-09 / DLA-K5 / C6 — the lifecycle names no workflow technology (material)."""

    check_id = "lifecycle-independence"
    severity = Severity.BLOCKING
    description = "No workflow/scheduler/ETL engine or vendor named (UDL-12 / DLA-K5)."

    def evaluate(self, subject: LifecycleValidationSubject) -> ValidationFinding:
        if subject.names_technology or subject.image_reference:
            return self._failed("a workflow/scheduler technology was named (UDL-12 / DLA-K5)")
        return self._passed()


class LifecycleVersionedCheck(ValidationCheck):
    """DLA-08 / UDL-12 — the lifecycle records an explicit version (additive/supersession)."""

    check_id = "lifecycle-versioned"
    severity = Severity.BLOCKING
    description = "Lifecycle records an explicit version (DLA-08 / UDL-12)."

    def evaluate(self, subject: LifecycleValidationSubject) -> ValidationFinding:
        if not subject.version.strip():
            return self._failed("lifecycle records no version (DLA-08)")
        return self._passed(version=subject.version)


class LifecycleClassifiedCheck(ValidationCheck):
    """DXH-07 — the current state maps to exactly one DXH-07 facet."""

    check_id = "lifecycle-classified"
    severity = Severity.BLOCKING
    description = "Current state maps to a single DXH-07 facet (Definitional/Operative/Terminal)."

    def evaluate(self, subject: LifecycleValidationSubject) -> ValidationFinding:
        if not subject.classified or subject.facet not in _FACET_VALUES:
            return self._failed("current state has no DXH-07 facet", facet=subject.facet)
        return self._passed(facet=subject.facet)


class MetaClassSingleCheck(ValidationCheck):
    """V1 / DMI-01 — the lifecycle instantiates exactly one meta-class (DMC-07)."""

    check_id = "meta-class-single"  # shared id — reused by the DMC-01 CCE gate suite
    severity = Severity.BLOCKING
    description = "Lifecycle instantiates exactly the DMC-07 meta-class (V1)."

    def evaluate(self, subject: LifecycleValidationSubject) -> ValidationFinding:
        if subject.meta_class != LIFECYCLE_META_CLASS:
            return self._failed("meta-class is not DMC-07 (V1)", meta_class=subject.meta_class)
        return self._passed(meta_class=subject.meta_class)


class MetaRelationshipsClosedCheck(ValidationCheck):
    """V2 / DMI-02 — every relationship used lies within DMR-01…12 (uses 06/10/11)."""

    check_id = "meta-relationships-closed"  # shared id — reused by DMC-01 CCE gate suite
    severity = Severity.BLOCKING
    description = "All lifecycle relationships are within DMR-01…12 (V2)."

    def evaluate(self, subject: LifecycleValidationSubject) -> ValidationFinding:
        outside = [r for r in subject.relationships if r not in _META_RELATIONSHIPS]
        if outside:
            return self._failed("relationships outside DMR-01…12 (V2)", outside=outside)
        return self._passed(relationships=list(subject.relationships))


class MetaConstraintsCheck(ValidationCheck):
    """V3 — applicable meta-constraints (DLA-K1 typed/identified, DLA-K3/K4 transitions)."""

    check_id = "meta-constraints"
    severity = Severity.BLOCKING
    description = "DLA-K1 (typed+identified) and DLA-K3/K4 (forward-only, guarded) hold (V3)."

    def evaluate(self, subject: LifecycleValidationSubject) -> ValidationFinding:
        ok = (
            subject.type_tag.strip()  # DLA-K1 typed
            and subject.name.strip()  # named
            and subject.target_id  # DMK-01 identified
            and subject.forward_only  # DLA-K3 forward-only
            and subject.transitions_guarded  # DLA-K4 guarded
            and subject.transitions_recorded  # DLA-03 recorded
            and subject.founding_acyclic  # DMK-03 acyclic
        )
        if not ok:
            return self._failed("DLA-K1/K3/K4 (DMK-01/03/07) not satisfied (V3)")
        return self._passed(constraints=["DLA-K1", "DLA-K3", "DLA-K4", "DMK-01", "DMK-03"])


class FoundingAcyclicCheck(ValidationCheck):
    """V4 / DMK-03 — the founding/transition graph is acyclic."""

    check_id = "founding-acyclic"  # shared id — reused by the DMC-01 CCE gate suite
    severity = Severity.BLOCKING
    description = "The lifecycle's founding/transition graph is acyclic (V4 / DMK-03)."

    def evaluate(self, subject: LifecycleValidationSubject) -> ValidationFinding:
        if not subject.founding_acyclic:
            return self._failed("founding/transition graph is not acyclic (V4)")
        return self._passed()


class LifecycleValidStateCheck(ValidationCheck):
    """V5 / UDL-12 — the lifecycle holds a valid DOS-01…05 lifecycle state."""

    check_id = "lifecycle-valid"
    severity = Severity.BLOCKING
    description = "Lifecycle holds a valid DOS-01…05 lifecycle state (V5 / UDL-12)."

    def evaluate(self, subject: LifecycleValidationSubject) -> ValidationFinding:
        if subject.lifecycle_state not in _STATE_VALUES:
            return self._failed("invalid lifecycle state (V5)", state=subject.lifecycle_state)
        return self._passed(state=subject.lifecycle_state)


class FoundationReuseIntegrityCheck(ValidationCheck):
    """UDL-02 / DMI-05 / VC-5 — EL-1 + DMC-02 + RL-F2 reused by reference only."""

    check_id = "foundation-reuse-integrity"  # shared id — reused by DMC-01 CCE gate suite
    severity = Severity.BLOCKING
    description = "EL-1 + DMC-02 + RL-F2 substrate referenced, redefined nowhere (UDL-02)."

    def evaluate(self, subject: LifecycleValidationSubject) -> ValidationFinding:
        if subject.redefines_el1:
            return self._failed("an EL-1/DMC-02/RL-F2 primitive was redefined (UDL-02)")
        if not subject.substrate_refs:
            return self._failed("no EL-1 substrate reference recorded (UDL-02)")
        if subject.absorbs_subject:
            return self._failed("the certified data model was owned, not referenced (DMX-02)")
        if not subject.binds_runtime_by_reference:
            return self._failed("RUNTIME behavior was not bound by reference (UDL-02 / DLA-07)")
        return self._passed(substrate=list(subject.substrate_refs))


class NonConstitutiveCheck(ValidationCheck):
    """UDL-15 / DLA-09 / C7 — the lifecycle confers no authority and embeds no secret."""

    check_id = "non-constitutive"
    severity = Severity.BLOCKING
    description = "Lifecycle confers no authority and embeds no secret (UDL-15 / DLA-09)."

    def evaluate(self, subject: LifecycleValidationSubject) -> ValidationFinding:
        if subject.confers_authority:
            return self._failed("lifecycle confers authority (UDL-15 / DLA-09)")
        if subject.embeds_secret:
            return self._failed("lifecycle embeds a secret (UDL-15 / RR-07)")
        return self._passed()


class ProvisionalDisclosureCheck(ValidationCheck):
    """DE-05 — the EC-1 provisional-state disclosure is present (no finality asserted)."""

    check_id = "provisional-state-disclosure"  # shared id — reused by DMC-01 CCE gate suite
    severity = Severity.BLOCKING
    description = "EC-1 provisional-state disclosure present; asserts no finality (DE-05)."

    def evaluate(self, subject: LifecycleValidationSubject) -> ValidationFinding:
        if not disclosure_present(subject.disclosure):
            return self._failed("EC-1 provisional-state disclosure absent/malformed (DE-05)")
        return self._passed(disclosure_id=subject.disclosure.get("disclosure_id"))


class TraceabilityRootedCheck(ValidationCheck):
    """§16 / AC — the No-Orphan lineage is rooted and closes to the 10-DATA anchor."""

    check_id = "traceability-rooted"  # shared id — reused by the DMC-01 CCE gate suite
    severity = Severity.BLOCKING
    description = "Backward lineage rooted at DMC-07 and closed to 10-DATA (No-Orphan)."

    def evaluate(self, subject: LifecycleValidationSubject) -> ValidationFinding:
        chain = subject.provenance_chain
        if not chain:
            return self._failed("traceability chain is empty (No-Orphan)")
        if chain[0] != subject.meta_class:
            return self._failed("lineage not rooted at the meta-class", head=chain[0])
        if not any(link.startswith("10-DATA@") for link in chain):
            return self._failed("lineage does not close to the 10-DATA anchor")
        return self._passed(links=len(chain))


def lifecycle_checks() -> tuple[ValidationCheck, ...]:
    """The full data-layer validation suite (deterministically ordered by the engine)."""
    return (
        LifecycleTypedCheck(),
        LifecycleNamedCheck(),
        LifecycleIdentifiedCheck(),
        LifecycleValueFidelityCheck(),
        LifecycleTransitionsSubjectCheck(),
        LifecycleStatesClosedCheck(),
        LifecycleForwardOnlyCheck(),
        LifecycleGuardedCheck(),
        LifecycleRecordedCheck(),
        LifecycleSingleStateCheck(),
        LifecycleBehavesByReferenceCheck(),
        LifecycleIndependenceCheck(),
        LifecycleVersionedCheck(),
        LifecycleClassifiedCheck(),
        MetaClassSingleCheck(),
        MetaRelationshipsClosedCheck(),
        MetaConstraintsCheck(),
        FoundingAcyclicCheck(),
        LifecycleValidStateCheck(),
        FoundationReuseIntegrityCheck(),
        NonConstitutiveCheck(),
        ProvisionalDisclosureCheck(),
        TraceabilityRootedCheck(),
    )


@dataclass(frozen=True, slots=True)
class LifecycleValidation:
    """The bundled outcome of validating a Lifecycle (report + evidence + decision)."""

    report: ValidationReport
    evidence: ValidationEvidence
    decision: AcceptanceDecision

    @property
    def accepted(self) -> bool:
        return self.decision.accepted


def validate_lifecycle(
    lifecycle: Lifecycle, trace: TraceabilityRecord, *, strict: bool = False
) -> LifecycleValidation:
    """Validate ``lifecycle`` through the CERTIFIED EC-1 engine and enforce acceptance.

    Returns the EC-1 :class:`ValidationReport`, its :class:`ValidationEvidence`, and the
    :class:`AcceptanceDecision`. With ``strict=True`` a rejected lifecycle raises via the
    EC-1 acceptance gate.
    """
    subject = LifecycleValidationSubject.from_lifecycle(lifecycle, trace)
    engine = ValidationEngine(lifecycle_checks())
    report = engine.validate(subject)
    evidence = build_validation_evidence(report)
    decision = enforce_acceptance(report, strict=strict)
    return LifecycleValidation(report=report, evidence=evidence, decision=decision)


__all__ = [
    "LIFECYCLE_BLUEPRINT_ID",
    "LifecycleValidationSubject",
    "LifecycleValidation",
    "lifecycle_checks",
    "validate_lifecycle",
]
