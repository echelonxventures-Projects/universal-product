"""UAUE — AUE-P-10/P-11, the evolution history engine (UAUE-000001, Epoch 3).

**No history store is created here.** The history is the canonical document of the Article 14
append-only ledger — :class:`engine.uckp.evolution.EvolutionLedger` — and it is read back through
that ledger's own loader. That is the whole design, and it is what makes the append-only claim
falsifiable rather than asserted: :meth:`EvolutionLedger.from_document` replays every record
through ``append``, so a skipped, reordered or renumbered history is refused *on read* by the
same code and the same error that would have refused it on write. Reading the history re-runs the
append rules instead of trusting the bytes.

**The stage cycle governs the record order, not the phase order.** The ledger's cycle is fifteen
canonical stages and it will not accept them out of order. UAUE's eleven phases claim those
fifteen stages between them, so one complete traversal of one candidate is exactly fifteen
records — one per stage, in *stage* order, each attributed to the phase that claims it. This is
why the loop interleaves: the phase that claims ``impact-analysis`` is the understanding phase,
which also claims ``learn``, and its records appear at both positions. A projection written in
phase order would be refused by the ledger, which is the correct outcome — the constitutional
cycle is not this register's to reorder.

**Logical time, never wall-clock time.** The ``when`` dimension is the cycle and the stage
ordinal. A timestamp would make two projections of one state differ, which would destroy the
determinism every other measurement in this programme depends on.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from engine.uaue.model import EvolutionAuthority, EvolutionAuthorityError
from engine.uaue.objects import EvolutionChain, EvolutionObject
from engine.uckp.canonical import content_hash
from engine.uckp.evolution import EVOLUTION_CYCLE, EvolutionLedger, EvolutionRecord

#: The phases whose objects this module derives. Positions, not identifiers, so the module names
#: no phase; the authority resolves each position to its declared phase.
_LEARNING_ORDINAL = 10
_TRANSITION_ORDINAL = 11


def _dimension_value(
    dimension: str,
    *,
    obj: EvolutionObject,
    chain: EvolutionChain,
    authority: EvolutionAuthority,
    cycle: int,
    stage: str,
    stage_ordinal: int,
) -> str:
    """One declared history dimension, for one object.

    Every dimension the declaration names must produce a value. A dimension this engine cannot
    derive returns an explicit marker rather than an empty string, so an underivable dimension is
    visible in the history instead of looking like an absent one.
    """
    if dimension == "who":
        owners = [entry.home for entry in authority.ownership if obj.phase in entry.phases]
        return f"{obj.authority} via {', '.join(owners) or '<no located owner>'}"
    if dimension == "what":
        return f"{obj.object_kind} ({obj.phase}) for {obj.subject_identity}"
    if dimension == "why":
        return obj.reason
    if dimension == "when":
        # Logical time: which cycle, which stage, at which position in the cycle.
        return f"cycle={cycle} stage={stage} ordinal={stage_ordinal}"
    if dimension == "where":
        return f"{obj.phase} at lifecycle state {obj.lifecycle_state}"
    if dimension == "context":
        return "; ".join(f"{key}={value}" for key, value in obj.context)
    if dimension == "evidence":
        return ", ".join(obj.evidence)
    if dimension == "decision":
        return obj.execution_record or f"{obj.phase} produced {obj.object_kind}"
    if dimension == "impact":
        return f"{obj.previous_state} -> {obj.target_state}"
    if dimension == "validation":
        return obj.validation_result or (
            chain.validation.summary if chain.validation else "<not measured>"
        )
    if dimension == "verification":
        return obj.verification_result or (
            chain.verification.summary if chain.verification else "<not measured>"
        )
    if dimension == "certification":
        return obj.certification_result or (
            chain.certification.summary if chain.certification else "<not measured>"
        )
    return "<no derivation declared for this dimension>"


def history_records(
    chain: EvolutionChain, authority: EvolutionAuthority, *, cycle: int = 0
) -> tuple[EvolutionRecord, ...]:
    """The fifteen records one chain contributes, in canonical stage order.

    Args:
        chain: a complete chain. Every phase must have produced its object.
        authority: the rehydrated authority, which maps each canonical stage to its phase.
        cycle: the ledger cycle this traversal occupies. One chain is one cycle.

    Returns:
        Exactly one record per canonical stage, in cycle order.

    Raises:
        EvolutionAuthorityError: a phase claiming a canonical stage produced no object, so a
            stage would have to be skipped. Skipping is refused rather than silently shortened,
            because the ledger would refuse the result anyway and a clear refusal here names the
            phase responsible.
    """
    records: list[EvolutionRecord] = []
    for ordinal, stage in enumerate(EVOLUTION_CYCLE):
        phase = authority.phase_claiming(stage.value)
        obj = chain.object_for(phase)
        if obj is None:
            raise EvolutionAuthorityError(
                "a canonical stage has no object, so the history would skip a stage",
                stage=stage.value,
                phase=phase,
                subject=chain.subject_identity,
            )
        findings = tuple(
            f"{dimension}="
            + _dimension_value(
                dimension,
                obj=obj,
                chain=chain,
                authority=authority,
                cycle=cycle,
                stage=stage.value,
                stage_ordinal=ordinal,
            )
            for dimension in authority.history.dimensions
        )
        records.append(
            EvolutionRecord(
                cycle=cycle,
                stage=stage,
                subject=obj.evolution_id,
                outcome=f"{phase} produced {obj.object_kind} at {stage.value}",
                digest=obj.digest(),
                findings=findings,
            )
        )
    return tuple(records)


def build_ledger(
    chains: EvolutionChain | Sequence[EvolutionChain], authority: EvolutionAuthority
) -> EvolutionLedger:
    """An Article 14 ledger over one or more complete chains, one cycle per chain.

    Appends through :meth:`EvolutionLedger.append`, so the ordering, cycle-advance and
    no-skipping rules are enforced by their owner rather than re-checked here.
    """
    sequence = [chains] if isinstance(chains, EvolutionChain) else list(chains)
    ledger = EvolutionLedger()
    for cycle, chain in enumerate(sequence):
        ledger.extend(history_records(chain, authority, cycle=cycle))
    return ledger


def project_history(
    chains: EvolutionChain | Sequence[EvolutionChain], authority: EvolutionAuthority
) -> dict[str, Any]:
    """The canonical history document for one or more chains.

    The Article 14 ledger document is nested verbatim under ``ledger`` rather than merged into
    the envelope. Merging would produce one document claiming two schemas, and a reader could not
    then tell which loader owns its append rules.
    """
    ledger = build_ledger(chains, authority)
    spec = authority.history
    return {
        "schema": spec.schema,
        "version": spec.version,
        "programme": authority.programme_id,
        "append_only": spec.append_only,
        "projection_of": {
            "home": spec.ledger_home,
            "ledger_symbol": spec.ledger_symbol,
            "document_symbol": spec.document_symbol,
            "rehydration_symbol": spec.rehydration_symbol,
        },
        "dimensions": list(spec.dimensions),
        "queryable_by": list(spec.queryable_by),
        "ledger": ledger.to_document(),
    }


def rehydrate_history(document: object) -> EvolutionLedger:
    """Read a history document back through the ledger that owns its append rules.

    Args:
        document: a document produced by :func:`project_history`.

    Returns:
        The rehydrated :class:`EvolutionLedger`.

    Raises:
        EvolutionAuthorityError: the envelope is not a UAUE history document.
        engine.uckp.errors.EvolutionError: the nested ledger violates the append-only rules —
            raised by the ledger itself, not re-implemented here, so a mutated history is refused
            by the same authority that would have refused writing it.
    """
    if not isinstance(document, dict):
        raise EvolutionAuthorityError(
            "a history document must be a mapping", received=type(document).__name__
        )
    if "ledger" not in document:
        raise EvolutionAuthorityError(
            "a history document must nest the Article 14 ledger document under 'ledger'"
        )
    if not document.get("append_only", False):
        raise EvolutionAuthorityError(
            "a history document that does not declare itself append-only is not this history"
        )
    return EvolutionLedger.from_document(document["ledger"])


def history_digest(document: dict[str, Any]) -> str:
    """The content-addressed digest of a history document, for the replay measurement."""
    return content_hash(document)


def query_history(document: dict[str, Any], key: str, value: str) -> tuple[dict[str, Any], ...]:
    """Records matching one declared queryable dimension.

    Only the dimensions the declaration lists in ``queryable_by`` may be queried. A query on an
    undeclared key is refused rather than returning nothing, because an empty result would be
    indistinguishable from "no record matches".
    """
    queryable = document.get("queryable_by", [])
    if key not in queryable and key != "subject":
        raise EvolutionAuthorityError(
            "the history is not declared queryable by that key",
            key=key,
            queryable_by=list(queryable),
        )
    ledger = document.get("ledger", {})
    records = ledger.get("records", []) if isinstance(ledger, dict) else []
    matched: list[dict[str, Any]] = []
    for record in records:
        if not isinstance(record, dict):
            continue
        if key in {"subject", "evolution_id"} and record.get("subject") == value:
            matched.append(record)
        elif key == "cycle" and str(record.get("cycle")) == value:
            matched.append(record)
        elif key in {"canonical_stage", "lifecycle_state"} and record.get("stage") == value:
            matched.append(record)
        elif any(
            finding.startswith(f"{key}=") and value in finding
            for finding in record.get("findings", [])
        ):
            matched.append(record)
    return tuple(matched)


def learning_object(chain: EvolutionChain, authority: EvolutionAuthority) -> EvolutionObject:
    """The learning phase's object: what the outcome established, and which assimilator holds it.

    A learned outcome cannot exist without a located assimilator, so the assimilating owner is
    named on the object. Assimilation itself already has an owner and a gate; this records who
    assimilated what, not a second assimilation.
    """
    from engine.uaue.objects import phase_object

    previous = chain.objects[-1] if chain.objects else None
    if previous is None:
        raise EvolutionAuthorityError(
            "a chain with no prior object has nothing to learn from",
            subject=chain.subject_identity,
        )
    phase = authority.phase_by_ordinal(_LEARNING_ORDINAL)
    assimilator = phase.owners[0].home if phase.owners else "<no located assimilator>"
    return phase_object(
        authority,
        previous,
        ordinal=_LEARNING_ORDINAL,
        note={"assimilated_by": assimilator, "learned": chain.candidate.target_state},
    )


def state_transition_object(
    chain: EvolutionChain, authority: EvolutionAuthority
) -> EvolutionObject:
    """The final phase's object: the state transition, and the continuation that never ends.

    The Article 14 cycle has no terminal stage, so this object records a transition and a
    continuation rather than a completion. Its lifecycle state is the stage its phase claims,
    which the loader has already proved to be a canonical stage of the owning authority.
    """
    from engine.uaue.objects import phase_object

    previous = chain.objects[-1] if chain.objects else None
    if previous is None:
        raise EvolutionAuthorityError(
            "a chain with no prior object cannot transition state",
            subject=chain.subject_identity,
        )
    return phase_object(
        authority,
        previous,
        ordinal=_TRANSITION_ORDINAL,
        note={
            "history_file": authority.history.file,
            "append_only": str(authority.history.append_only),
            "terminates": "false",
        },
    )


__all__ = [
    "build_ledger",
    "history_digest",
    "history_records",
    "learning_object",
    "project_history",
    "query_history",
    "rehydrate_history",
    "state_transition_object",
]
