"""EC3-B12-U05 — The Universal Workflow construct (AMC-05).

Realizes the meta-model concept **AMC-05 Workflow** (APPLICATION-005 §2;
APPLICATION-009; APPLICATION-003 AOE-05; APPLICATION-001 §4):

    the **ordered, conditional arrangement of features/operations toward an outcome**
    (a long-running arrangement is a **Process**) — the arrangement of delivery over
    time — a typed (ENG-004) object (ENG-002), identified (ENG-001), classified by one
    AXH-05 kind (Sequential / Conditional / Process), that **sequences the features/
    operations it arranges** (AMR-04, by reference; the defining relationship — WKF-04),
    **consumes one or more SF-2 operations under contract through its steps** (AMR-13, by
    reference), **holds/advances state** within a declared context (AMR-06, by reference →
    RL-F2; forward-only, WKF-06), and whose sequence/transition/emit behavior is a RUNTIME
    workflow + SF-2 orchestration construct (AMR-11 / §7, by reference).

The construct is **additive over the CERTIFIED EC-1 foundation** (and the referenced,
CERTIFIED-COMPLETE Band-10 data surface + CERTIFIED-COMPLETE + FROZEN Band-11 service
surface + the CERTIFIED Band-12 U01 Universal Application root + U02 Universal Capability +
U03 Universal Module + U04 Universal Feature) and reuses them *by reference* (UAL-02 /
AMI-05): identity and value-fidelity are derived through the EC-1 certified deterministic
encoding (:func:`engine.certification.contracts.canonical_json` /
:func:`~engine.certification.contracts.content_hash`) — the same discipline that produces
every EC-1 runtime, artifact, and certification identity — so this module introduces
**no second identity scheme and no parallel value model**. It selects no technology/UI and
confers no authority (UAL-15).

A :class:`Workflow` is *immutable* (a frozen object — ENG-002 objecthood), *typed*
(ENG-004), *identified* (ENG-001 via a deterministic id), *classified* (AXH-05 kind),
*feature/operation-sequencing* (AMR-04, by reference — the defining relationship),
*service-consuming* (AMR-13, one or more, by reference), *state-holding* (AMR-06, by
reference), *behavior-bound* (AMR-11, by reference), and holds a *forward-only lifecycle
state* (AOS-01…06, UAL-12). Constructing a :class:`Workflow` enforces the meta-constraints
AMK-01/02/03/05/07 and the laws UAL-03/04/05/10/12 fail-closed: an ill-formed workflow
cannot be instantiated. It realizes **no** Application, Capability, Module, Feature,
Interaction, State, Composition, Security, or Governance object — those are separate
Band-12 units; this construct binds them only *by reference*. In particular it **delivers
no capability** (AMR-01), **groups no feature** (AMR-03), **is engaged through no
interaction** (AMR-05), and **presents no DF-2 data** (AMR-14) — a workflow *sequences*
what features *deliver* (ATH-09/14), it does not deliver.

**Ordering distinction (architectural).** Unlike a Feature (whose composed operations are
an unordered *set* — a partition), a Workflow's ``sequence_refs`` are an **ordered
sequence**: order is identity-defining, because the arrangement over time *is* the
workflow (WKF-04). The SF-2 operations its steps consume (``operation_refs``) are an
unordered set (canonically sorted for identity).
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Any

from application.workflow_meta import (
    LIFECYCLE_ORDER,
    MULTI_STEP_KINDS,
    PROCESS_KINDS,
    SUBSTRATE_REFS,
    WORKFLOW_META_CLASS,
    WORKFLOW_RELATIONSHIPS,
    WorkflowKind,
    WorkflowState,
)

# --- EC-1 reuse by reference (UAL-02 / AMI-05) — imported, never redefined --------
from engine.certification.contracts import canonical_json, content_hash

#: The deterministic id prefix for a realized Workflow (mirrors EC-1 UCOS-<KIND>-<hex16>).
WORKFLOW_ID_PREFIX = "UCOS-WORKFLOW"

#: The map of frozen-foundation primitives this construct reuses *by reference*
#: (never redefined). Recorded for the reuse-integrity check (UAL-02 / AMI-05 / VC-5).
FOUNDATION_REUSE: dict[str, str] = {
    "ENG-001": "engine.certification.contracts.content_hash (deterministic identity derivation)",
    "ENG-002": "python frozen object (immutable objecthood bearing the workflow)",
    "ENG-003": "engine.certification.contracts.canonical_json (value fidelity; no parallel model)",
    "ENG-004": "application.workflow_meta.WorkflowKind + type_tag (ENG-004 typing, by ref)",
    "ENG-005": "reference identifiers (sequenced feature/op, operation, state, behavior refs)",
    "RL-F2": "workflow concern + state advancement by reference (§7, AMR-06/11); none redefined",
    "SF-2": "consumed contracted operation(s) + orchestration by reference (AMR-13/11); none redef",
}

#: Concrete-technology markers forbidden by UAL-15 (no UI/framework/screen/API/protocol/vendor).
#: An abstract EL-1/RL-F2/PL-F2/DF-2/SF-2 reference names none of these.
_TECHNOLOGY_MARKERS: tuple[str, ...] = (
    "react",
    "vue",
    "angular",
    "svelte",
    "tailwind",
    "bootstrap",
    "airflow",
    "temporal",
    "camunda",
    "zeebe",
    "celery",
    "grpc",
    "graphql",
    "kafka",
    "rabbitmq",
    "postgres",
    "mysql",
    "mongodb",
    "kubernetes",
    "docker",
    "nginx",
    "openapi",
    "swagger",
    "lambda",
    "dynamodb",
    "http://",
    "https://",
    "tcp://",
)

#: Conservative secret markers used to enforce UAL-15 / RR-07 (embed no secret).
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


class WorkflowError(ValueError):
    """Raised when inputs cannot be realized as a well-formed :class:`Workflow`.

    A :class:`Workflow` is fail-closed (TRACK-001): an ill-formed workflow construct is
    rejected at construction rather than admitted as an invalid workflow.
    """


def _require_reference(name: str, value: Any) -> str:
    """Require ``value`` to be a non-empty ENG-005 reference string (by reference)."""
    if not isinstance(value, str) or not value.strip():
        raise WorkflowError(
            f"{name} must be a non-empty ENG-005 reference (UAL-02/10)"
        )
    return value


@dataclass(frozen=True, slots=True)
class Workflow:
    """AMC-05 — an immutable, typed, identified, feature/operation-sequencing workflow.

    Fields:
        type_tag:       the ENG-004 Type of the workflow (decidable, non-empty) — UAL-03.
        kind:           the AXH-05 classification of the workflow (AXC-04).
        sequence_refs:  the ENG-005 references to the features/operations the workflow
                        sequences toward an outcome (AMR-04 sequenced-by, reference-only)
                        — the WKF-04 / WKF-C1 **defining relationship**: the explicit,
                        typed, decidable arrangement of delivery over time. Must be
                        non-empty and a partition (distinct steps; WKF-C1). A
                        Conditional-Workflow sequences ≥2 (branch determinacy; WKF-05 /
                        AXH-05). **Order is identity-defining** (a sequence, not a set).
        operation_refs: the ENG-005 references to the SF-2 operation(s) the workflow's
                        steps consume under contract (AMR-13 consumes-operation,
                        reference-only). Must be non-empty and a partition (distinct).
                        Order-independent for identity (canonically sorted).
        state_ref:      the ENG-005 reference to the State the workflow holds/advances
                        (AMR-06 holds-state; RL-F2, by reference — forward-only, WKF-06).
        behavior_ref:   the ENG-005 reference to the RUNTIME behavior the workflow binds
                        (AMR-11 behaves-as; RL-F2 workflow + SF-2 orchestration, by
                        reference; sequence/transition/emit) — UAL-10 (the governing law).
        state:          the AOS-01…06 lifecycle state (forward-only) — UAL-12 (default DEFINED).
    """

    type_tag: str
    kind: WorkflowKind
    sequence_refs: tuple[str, ...]
    operation_refs: tuple[str, ...]
    state_ref: str = "ENG-005:AMC-07:ucos.application.state.primary"
    behavior_ref: str = "ENG-005:RL-F2:runtime.workflow-sequence"
    state: WorkflowState = WorkflowState.DEFINED

    #: Canonically ordered, de-duplicated view of the consumed operations (identity-defining).
    _ordered_operations: tuple[str, ...] = field(init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        # AMK-01 / UAL-03 / WKF-01 — typed (ENG-004): a decidable, non-empty type tag.
        if not isinstance(self.type_tag, str) or not self.type_tag.strip():
            raise WorkflowError(
                "workflow must be typed with a non-empty ENG-004 type_tag (UAL-03)"
            )
        # AXH-05 / AXC-04 — classified by exactly one Workflow kind.
        if not isinstance(self.kind, WorkflowKind):
            raise WorkflowError("workflow kind must be an AXH-05 WorkflowKind (AXC-04)")
        # AMR-04 / WKF-04 / WKF-C1 — sequences an explicit, non-empty arrangement of steps.
        if not isinstance(self.sequence_refs, tuple):
            raise WorkflowError(
                "sequence_refs must be a tuple of ENG-005 references (AMR-04)"
            )
        if not self.sequence_refs:
            raise WorkflowError(
                "workflow must sequence at least one feature/operation (AMR-04 / WKF-04)"
            )
        for ref in self.sequence_refs:
            if not isinstance(ref, str) or not ref.strip():
                raise WorkflowError(
                    "each sequenced step must be a non-empty ENG-005 reference (AMR-04)"
                )
        # WKF-C1 — the sequenced steps are a partition (distinct; the arrangement is decidable).
        if len(set(self.sequence_refs)) != len(self.sequence_refs):
            raise WorkflowError(
                "sequenced steps must be distinct (WKF-C1 sequence determinacy)"
            )
        # AXH-05 / WKF-05 — a Conditional-Workflow sequences ≥2 steps (decidable branches).
        if self.kind in MULTI_STEP_KINDS and len(self.sequence_refs) < 2:
            raise WorkflowError(
                "a Conditional-Workflow must sequence ≥2 steps (AXH-05 / WKF-05)"
            )
        # AMR-13 / AMK-07 — the steps consume ≥1 SF-2 operation under contract.
        if not isinstance(self.operation_refs, tuple):
            raise WorkflowError(
                "operation_refs must be a tuple of ENG-005 references (AMR-13)"
            )
        if not self.operation_refs:
            raise WorkflowError(
                "workflow's steps must consume at least one SF-2 operation (AMR-13 / WKF-K4)"
            )
        for ref in self.operation_refs:
            if not isinstance(ref, str) or not ref.strip():
                raise WorkflowError(
                    "each consumed operation must be a non-empty ENG-005 reference (AMR-13)"
                )
        # WKF-K4 — consumed operations are a partition (distinct).
        if len(set(self.operation_refs)) != len(self.operation_refs):
            raise WorkflowError(
                "consumed operations must be distinct (WKF-K4 partition)"
            )
        # AMR-06 / WKF-06 / AMK-05 — holds/advances state by reference (→ RL-F2).
        _require_reference("state_ref", self.state_ref)
        # AMR-11 / UAL-10 / AMK-05 — behavior bound to RL-F2 workflow / SF-2 orchestration.
        _require_reference("behavior_ref", self.behavior_ref)
        # V5 / UAL-12 — a valid lifecycle state.
        if not isinstance(self.state, WorkflowState):
            raise WorkflowError("workflow state must be an AOS-01…06 WorkflowState (UAL-12)")
        # WKF-C2 / AMK-03 — non-absorption / acyclicity guard: a workflow cannot sequence
        # its own held state or bound behavior as a step, and a consumed operation cannot
        # be the workflow's state/behavior reference (no self-founding; the sequence is a
        # finite, terminating arrangement — no implicit/infinite branch).
        binding_refs = {self.state_ref, self.behavior_ref}
        if binding_refs & set(self.sequence_refs):
            raise WorkflowError(
                "a workflow cannot sequence its own held state or bound behavior "
                "(WKF-C2 / AMK-03 founding acyclicity)"
            )
        if binding_refs & set(self.operation_refs):
            raise WorkflowError(
                "a workflow cannot consume its own held state or bound behavior as an "
                "operation (WKF-C2 / AMK-03 founding acyclicity)"
            )
        object.__setattr__(
            self, "_ordered_operations", tuple(sorted(self.operation_refs))
        )

    # -- identity (ENG-001) borne by object (ENG-002), by reference ------------

    def canonical_core(self) -> dict[str, Any]:
        """The canonical, hashable core of the workflow (its identity-defining tuple).

        The sequenced steps are an **ordered sequence** (order is identity-defining — the
        arrangement over time *is* the workflow), so they are preserved in declaration
        order. The consumed operations are a set (a partition), so they are canonically
        sorted — two workflows consuming the same operations in different declaration order
        bear the same ENG-001 identity.
        """
        return {
            "meta_class": WORKFLOW_META_CLASS,
            "type_tag": self.type_tag,
            "kind": self.kind.value,
            "sequence_refs": list(self.sequence_refs),
            "operation_refs": list(self._ordered_operations),
            "state_ref": self.state_ref,
            "behavior_ref": self.behavior_ref,
        }

    @property
    def value_digest(self) -> str:
        """The EC-1 content hash of the workflow core — the ENG-003 value fingerprint."""
        return content_hash(self.canonical_core())

    @property
    def workflow_id(self) -> str:
        """The deterministic ENG-001 identity of the workflow (borne by this object).

        Derived through the CERTIFIED EC-1 ``content_hash`` (UAL-04 — no second identity
        scheme): identical (type, kind, refs) always yields the identical id, so identity
        is reproducible and byte-stable (determinism, VC-4).
        """
        return f"{WORKFLOW_ID_PREFIX}-{self.type_tag}-{self.value_digest[:16]}"

    # -- meta-model participation (APPLICATION-005/009) ------------------------

    @property
    def meta_class(self) -> str:
        """V1 — the single meta-class this construct instantiates (AMC-05)."""
        return WORKFLOW_META_CLASS

    def meta_relationships(self) -> tuple[str, ...]:
        """V2 — the AMR-01…14 relationships the workflow participates in."""
        return WORKFLOW_RELATIONSHIPS

    def is_founding_acyclic(self) -> bool:
        """V4 / AMK-03 / WKF-C2 — the founding graph is acyclic.

        A Workflow uses **no** founding meta-relationship (AMR-02/03/05); its sequencing
        (AMR-04) is a reference-only, finite, terminating arrangement, so its founding
        structure carries no cycle. This is proven by the fact that its core canonically
        encodes (a cycle would raise at construction).
        """
        try:
            canonical_json(self.canonical_core())
        except (TypeError, ValueError):  # pragma: no cover - blocked at construction
            return False
        return True

    def references_resolve(self) -> bool:
        """AOI-03 / AMK-05/07 — every ENG-005 reference is a non-empty resolvable id."""
        base = all(
            isinstance(r, str) and bool(r.strip())
            for r in (self.state_ref, self.behavior_ref)
        )
        seq = all(isinstance(r, str) and bool(r.strip()) for r in self.sequence_refs)
        ops = all(isinstance(r, str) and bool(r.strip()) for r in self.operation_refs)
        return base and seq and ops

    def sequences_steps(self) -> bool:
        """AMR-04 / WKF-04 — the workflow sequences ≥1 feature/operation by reference."""
        return len(self.sequence_refs) >= 1

    def sequenced_step_count(self) -> int:
        """The number of features/operations the workflow sequences (its arrangement size)."""
        return len(self.sequence_refs)

    def steps_are_partition(self) -> bool:
        """WKF-C1 — the sequenced steps are distinct (a partition)."""
        return len(set(self.sequence_refs)) == len(self.sequence_refs) and all(
            r.strip() for r in self.sequence_refs
        )

    def consumes_operations(self) -> bool:
        """AMR-13 / WKF-K4 — the workflow's steps consume ≥1 SF-2 operation by reference."""
        return len(self.operation_refs) >= 1

    def consumed_operation_count(self) -> int:
        """The number of SF-2 operations the workflow's steps consume."""
        return len(self.operation_refs)

    def operations_are_partition(self) -> bool:
        """WKF-K4 — the consumed operations are distinct (a partition)."""
        return len(set(self.operation_refs)) == len(self.operation_refs) and all(
            r.strip() for r in self.operation_refs
        )

    def holds_state(self) -> bool:
        """AMR-06 / WKF-06 — the workflow holds/advances state by reference (→ RL-F2)."""
        return bool(self.state_ref.strip())

    def sequence_is_explicit(self) -> bool:
        """WKF-C1 / UAL-10 — the workflow's arrangement is explicit, typed, and decidable.

        Explicit iff the type and kind are declared and the sequence is an explicit,
        non-empty, partitioned arrangement of steps (the arrangement is closed at
        declaration — no implicit step).
        """
        return (
            bool(self.type_tag.strip())
            and self.sequences_steps()
            and self.steps_are_partition()
        )

    def branch_determinacy_holds(self) -> bool:
        """WKF-05 / WKF-C2 / AXH-05 — branch conditions are decidable and terminating.

        A Conditional-Workflow declares ≥2 sequenced branches (decidable, finite); a
        Sequential/Process workflow sequences ≥1 step. There is no implicit or
        non-terminating branch: the arrangement is a finite partition.
        """
        if self.kind in MULTI_STEP_KINDS:
            return self.sequenced_step_count() >= 2
        return self.sequenced_step_count() >= 1

    def records_intermediate_state(self) -> bool:
        """WKF-07 / WKF-C5 — a Process records its intermediate states (auditable progress).

        A Process-Workflow is long-running and must hold recorded state (AMR-06); a
        Sequential/Conditional workflow also holds state but is not required to be
        long-running. State is held by reference in every kind, so intermediate progress
        is always recordable.
        """
        if self.kind in PROCESS_KINDS:
            return self.holds_state()
        return True

    def arrangement_class(self) -> str:
        """AXH-05 — the ordered / conditional / process classification of the arrangement."""
        if self.kind in MULTI_STEP_KINDS:
            return "conditional"
        if self.kind in PROCESS_KINDS:
            return "process"
        return "sequential"

    def sequences_step(self, step_ref: str) -> bool:
        """AMR-04 — True iff ``step_ref`` is sequenced by this workflow."""
        return step_ref in self.sequence_refs

    def consumes_operation(self, operation_ref: str) -> bool:
        """AMR-13 — True iff ``operation_ref`` is consumed by this workflow's steps."""
        return operation_ref in self.operation_refs

    # -- non-constitutiveness (UAL-15) -----------------------------------------

    def confers_authority(self) -> bool:
        """UAL-15 / WKF-09 / C7 — a workflow confers no authority (structurally has none)."""
        return False

    def selects_technology(self) -> bool:
        """UAL-15 / WKF-09 / C7 — True iff the workflow names a concrete technology/vendor."""
        haystack = canonical_json(self.canonical_core()).lower()
        return any(marker in haystack for marker in _TECHNOLOGY_MARKERS)

    def embeds_secret(self) -> bool:
        """UAL-15 / RR-07 / C7 — True iff the workflow appears to embed a secret."""
        haystack = canonical_json(self.canonical_core()).lower()
        return any(marker in haystack for marker in _SECRET_MARKERS)

    def redefines_foundation(self) -> bool:
        """UAL-02 / AMI-05 / VC-5 — a workflow redefines no frozen primitive (reuse-only)."""
        return False

    # -- lifecycle (UAL-12, forward-only) --------------------------------------

    def transition(self, to_state: WorkflowState) -> Workflow:
        """Return a new workflow advanced to ``to_state`` (forward-only; UAL-12 / WKF-C3).

        State advancement is forward-only and recorded; there is no silent or
        in-place-reversible transition.

        Raises:
            WorkflowError: on a backward or in-place-reversing transition.
        """
        if not isinstance(to_state, WorkflowState):
            raise WorkflowError("target state must be an AOS-01…06 WorkflowState (UAL-12)")
        here = LIFECYCLE_ORDER.index(self.state)
        there = LIFECYCLE_ORDER.index(to_state)
        if there < here:
            raise WorkflowError(
                f"lifecycle is forward-only (UAL-12 / WKF-C3): "
                f"{self.state.value} → {to_state.value} is backward"
            )
        return replace(self, state=to_state)

    # -- serialization ----------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """A deterministic, serializable projection of the workflow."""
        return {
            "workflow_id": self.workflow_id,
            "meta_class": self.meta_class,
            "type_tag": self.type_tag,
            "kind": self.kind.value,
            "sequence_refs": list(self.sequence_refs),
            "sequenced_step_count": self.sequenced_step_count(),
            "operation_refs": list(self._ordered_operations),
            "consumed_operation_count": self.consumed_operation_count(),
            "state_ref": self.state_ref,
            "behavior_ref": self.behavior_ref,
            "value_digest": self.value_digest,
            "state": self.state.value,
            "arrangement_class": self.arrangement_class(),
            "sequence_explicit": self.sequence_is_explicit(),
            "holds_state": self.holds_state(),
            "relationships": list(self.meta_relationships()),
            "substrate_refs": list(SUBSTRATE_REFS),
        }


def make_workflow(
    type_tag: str,
    sequence_refs: tuple[str, ...],
    operation_refs: tuple[str, ...],
    *,
    kind: WorkflowKind = WorkflowKind.SEQUENTIAL,
    state_ref: str = "ENG-005:AMC-07:ucos.application.state.primary",
    behavior_ref: str = "ENG-005:RL-F2:runtime.workflow-sequence",
    state: WorkflowState = WorkflowState.DEFINED,
) -> Workflow:
    """Construct a well-formed :class:`Workflow` (fail-closed factory)."""
    return Workflow(
        type_tag=type_tag,
        kind=kind,
        sequence_refs=tuple(sequence_refs),
        operation_refs=tuple(operation_refs),
        state_ref=state_ref,
        behavior_ref=behavior_ref,
        state=state,
    )


__all__ = [
    "WORKFLOW_ID_PREFIX",
    "FOUNDATION_REUSE",
    "WorkflowError",
    "Workflow",
    "make_workflow",
]
