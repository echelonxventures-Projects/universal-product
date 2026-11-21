"""UCKP Layer Zero — the Universal Constitutional State Model (Article 12).

A constitutional state is a sealed, content-addressed record of what the universe
became and how. Article 12 requires that every transition create a *new* state, that
each state reference its parent and its five deltas, that it carry replay, validation
and verification proofs and an audit trail, and that no previous state ever change.

The design makes the last clause structurally true rather than procedurally enforced:

    * ``state_id`` is the digest of the state's own core, so a state cannot be edited
      and keep its name. Editing produces a different state, which is the honest
      outcome — history gained an entry, it did not lose one.
    * ``parent_state_id`` is inside that digest, so rewriting an ancestor invalidates
      every descendant. Tampering is detectable from any point in the chain, by anyone
      holding any later state.
    * :class:`ConstitutionalTimeline` is append-only. There is no update, no delete and
      no reorder method, because an API that offers one is an API someone will call.

No clock is read. States are ordered by ``sequence`` and identified by content, so a
timeline replays identically on any machine at any time — which is what Invariant 15
requires and what a wall-clock timestamp would immediately destroy.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field

from engine.uckp.canonical import content_hash
from engine.uckp.errors import StateImmutabilityError
from engine.uckp.values import AuditEntry, ReplayProof

#: The five delta registers Article 12 requires of every transition.
KNOWLEDGE = "knowledge"
EVIDENCE = "evidence"
AUTHORITY = "authority"
CAPABILITY = "capability"
CERTIFICATION = "certification"

DELTA_REGISTERS: tuple[str, ...] = (
    AUTHORITY,
    CAPABILITY,
    CERTIFICATION,
    EVIDENCE,
    KNOWLEDGE,
)

#: The identity of the state before any transition has occurred.
GENESIS_PARENT = ""


@dataclass(frozen=True, slots=True)
class ConstitutionalDelta:
    """What one register gained, lost or changed in a transition."""

    register: str
    added: tuple[str, ...] = field(default_factory=tuple)
    removed: tuple[str, ...] = field(default_factory=tuple)
    changed: tuple[str, ...] = field(default_factory=tuple)

    @property
    def empty(self) -> bool:
        return not (self.added or self.removed or self.changed)

    def to_dict(self) -> dict[str, object]:
        return {
            "register": self.register,
            "added": list(self.added),
            "removed": list(self.removed),
            "changed": list(self.changed),
        }

    @classmethod
    def from_dict(cls, data: object) -> ConstitutionalDelta:
        record = data if isinstance(data, dict) else {}
        return cls(
            register=str(record.get("register", "")),
            added=tuple(str(item) for item in record.get("added") or ()),
            removed=tuple(str(item) for item in record.get("removed") or ()),
            changed=tuple(str(item) for item in record.get("changed") or ()),
        )

    @classmethod
    def between(
        cls, register: str, before: Iterable[str], after: Iterable[str]
    ) -> ConstitutionalDelta:
        """Derive a delta from two identity sets. Deterministic and order-free."""
        old = set(before)
        new = set(after)
        return cls(
            register=str(register),
            added=tuple(sorted(new - old)),
            removed=tuple(sorted(old - new)),
        )


@dataclass(frozen=True, slots=True)
class Proof:
    """A machine-checkable claim about a transition."""

    kind: str
    procedure: str
    input_digest: str
    output_digest: str
    verdict: str = "holds"

    @property
    def holds(self) -> bool:
        return self.verdict == "holds"

    def to_dict(self) -> dict[str, str]:
        return {
            "kind": self.kind,
            "procedure": self.procedure,
            "input_digest": self.input_digest,
            "output_digest": self.output_digest,
            "verdict": self.verdict,
        }

    @classmethod
    def from_dict(cls, data: object) -> Proof:
        record = data if isinstance(data, dict) else {}
        return cls(
            kind=str(record.get("kind", "")),
            procedure=str(record.get("procedure", "")),
            input_digest=str(record.get("input_digest", "")),
            output_digest=str(record.get("output_digest", "")),
            verdict=str(record.get("verdict", "holds")),
        )

    def as_replay_proof(self) -> ReplayProof:
        return ReplayProof(
            procedure=self.procedure,
            input_digest=self.input_digest,
            output_digest=self.output_digest,
        )


@dataclass(frozen=True, slots=True)
class ConstitutionalState:
    """An immutable, content-addressed constitutional state."""

    sequence: int
    parent_state_id: str
    knowledge_digest: str
    knowledge_delta: ConstitutionalDelta
    evidence_delta: ConstitutionalDelta
    authority_delta: ConstitutionalDelta
    capability_delta: ConstitutionalDelta
    certification_delta: ConstitutionalDelta
    replay_proof: Proof
    validation_proof: Proof
    verification_proof: Proof
    audit_trail: tuple[AuditEntry, ...] = field(default_factory=tuple)
    state_id: str = ""

    # --- identity ---------------------------------------------------------------

    def _core(self) -> dict[str, object]:
        return {
            "sequence": self.sequence,
            "parent_state_id": self.parent_state_id,
            "knowledge_digest": self.knowledge_digest,
            "deltas": {
                AUTHORITY: self.authority_delta.to_dict(),
                CAPABILITY: self.capability_delta.to_dict(),
                CERTIFICATION: self.certification_delta.to_dict(),
                EVIDENCE: self.evidence_delta.to_dict(),
                KNOWLEDGE: self.knowledge_delta.to_dict(),
            },
            "proofs": {
                "replay": self.replay_proof.to_dict(),
                "validation": self.validation_proof.to_dict(),
                "verification": self.verification_proof.to_dict(),
            },
            "audit_trail": [entry.to_dict() for entry in self.audit_trail],
        }

    def derived_state_id(self) -> str:
        return content_hash(self._core())

    def sealed(self) -> ConstitutionalState:
        from dataclasses import replace

        return replace(self, state_id=self.derived_state_id())

    def verify_integrity(self) -> bool:
        return bool(self.state_id) and self.state_id == self.derived_state_id()

    def require_immutable(self) -> None:
        if not self.verify_integrity():
            raise StateImmutabilityError(
                "a constitutional state was altered after sealing",
                state_id=self.state_id,
                sequence=self.sequence,
            )

    @property
    def is_genesis(self) -> bool:
        return self.parent_state_id == GENESIS_PARENT

    def deltas(self) -> tuple[ConstitutionalDelta, ...]:
        return (
            self.authority_delta,
            self.capability_delta,
            self.certification_delta,
            self.evidence_delta,
            self.knowledge_delta,
        )

    def proofs(self) -> tuple[Proof, ...]:
        return (self.replay_proof, self.validation_proof, self.verification_proof)

    def proofs_hold(self) -> bool:
        return all(proof.holds for proof in self.proofs())

    # --- construction -----------------------------------------------------------

    @classmethod
    def genesis(
        cls,
        *,
        knowledge_digest: str,
        knowledge_ids: Sequence[str] = (),
        actor: str = "engine.uckp",
    ) -> ConstitutionalState:
        """The first state: everything is an addition and there is no parent."""
        empty = {register: ConstitutionalDelta(register) for register in DELTA_REGISTERS}
        return cls(
            sequence=0,
            parent_state_id=GENESIS_PARENT,
            knowledge_digest=knowledge_digest,
            knowledge_delta=ConstitutionalDelta(KNOWLEDGE, added=tuple(sorted(knowledge_ids))),
            evidence_delta=empty[EVIDENCE],
            authority_delta=empty[AUTHORITY],
            capability_delta=empty[CAPABILITY],
            certification_delta=empty[CERTIFICATION],
            replay_proof=Proof("replay", "uckp.genesis/1.0.0", knowledge_digest, knowledge_digest),
            validation_proof=Proof(
                "validation", "uckp.genesis/1.0.0", knowledge_digest, knowledge_digest
            ),
            verification_proof=Proof(
                "verification", "uckp.genesis/1.0.0", knowledge_digest, knowledge_digest
            ),
            audit_trail=(
                AuditEntry(
                    actor=actor, action="genesis", subject="uckp.universe", digest=knowledge_digest
                ),
            ),
        ).sealed()

    def transition(
        self,
        *,
        knowledge_digest: str,
        knowledge_delta: ConstitutionalDelta | None = None,
        evidence_delta: ConstitutionalDelta | None = None,
        authority_delta: ConstitutionalDelta | None = None,
        capability_delta: ConstitutionalDelta | None = None,
        certification_delta: ConstitutionalDelta | None = None,
        replay_proof: Proof | None = None,
        validation_proof: Proof | None = None,
        verification_proof: Proof | None = None,
        audit: Sequence[AuditEntry] = (),
        actor: str = "engine.uckp",
    ) -> ConstitutionalState:
        """Return the successor state. ``self`` is untouched — that is the point."""
        self.require_immutable()
        procedure = "uckp.transition/1.0.0"
        entries = tuple(audit) or (
            AuditEntry(
                actor=actor,
                action="transition",
                subject="uckp.universe",
                digest=knowledge_digest,
            ),
        )
        return ConstitutionalState(
            sequence=self.sequence + 1,
            parent_state_id=self.state_id,
            knowledge_digest=knowledge_digest,
            knowledge_delta=knowledge_delta or ConstitutionalDelta(KNOWLEDGE),
            evidence_delta=evidence_delta or ConstitutionalDelta(EVIDENCE),
            authority_delta=authority_delta or ConstitutionalDelta(AUTHORITY),
            capability_delta=capability_delta or ConstitutionalDelta(CAPABILITY),
            certification_delta=certification_delta or ConstitutionalDelta(CERTIFICATION),
            replay_proof=replay_proof
            or Proof("replay", procedure, self.knowledge_digest, knowledge_digest),
            validation_proof=validation_proof
            or Proof("validation", procedure, self.knowledge_digest, knowledge_digest),
            verification_proof=verification_proof
            or Proof("verification", procedure, self.knowledge_digest, knowledge_digest),
            audit_trail=entries,
        ).sealed()

    # --- serialization ----------------------------------------------------------

    def to_dict(self) -> dict[str, object]:
        record = self._core()
        record["state_id"] = self.state_id
        return record

    @classmethod
    def from_dict(cls, data: object) -> ConstitutionalState:
        if not isinstance(data, dict):
            raise StateImmutabilityError("state record must be a mapping")
        deltas = data.get("deltas") or {}
        proofs = data.get("proofs") or {}
        state = cls(
            sequence=int(data.get("sequence", 0)),
            parent_state_id=str(data.get("parent_state_id", "")),
            knowledge_digest=str(data.get("knowledge_digest", "")),
            knowledge_delta=ConstitutionalDelta.from_dict(deltas.get(KNOWLEDGE)),
            evidence_delta=ConstitutionalDelta.from_dict(deltas.get(EVIDENCE)),
            authority_delta=ConstitutionalDelta.from_dict(deltas.get(AUTHORITY)),
            capability_delta=ConstitutionalDelta.from_dict(deltas.get(CAPABILITY)),
            certification_delta=ConstitutionalDelta.from_dict(deltas.get(CERTIFICATION)),
            replay_proof=Proof.from_dict(proofs.get("replay")),
            validation_proof=Proof.from_dict(proofs.get("validation")),
            verification_proof=Proof.from_dict(proofs.get("verification")),
            audit_trail=tuple(
                AuditEntry.from_dict(entry) for entry in data.get("audit_trail") or ()
            ),
            state_id=str(data.get("state_id", "")),
        )
        if state.state_id:
            state.require_immutable()
            return state
        return state.sealed()


class ConstitutionalTimeline:
    """The append-only history of the Constitutional Knowledge Universe.

    There is no method to modify or remove a state. The only mutation is
    :meth:`append`, and it refuses anything that is not a well-founded successor of the
    current head.
    """

    __slots__ = ("_states",)

    def __init__(self, states: Iterable[ConstitutionalState] = ()) -> None:
        self._states: list[ConstitutionalState] = []
        for state in states:
            self.append(state)

    def append(self, state: ConstitutionalState) -> ConstitutionalState:
        state.require_immutable()
        if not self._states:
            if not state.is_genesis:
                raise StateImmutabilityError(
                    "the first state must be genesis", state_id=state.state_id
                )
        else:
            head = self._states[-1]
            if state.parent_state_id != head.state_id:
                raise StateImmutabilityError(
                    "a state must reference the current head as its parent",
                    expected_parent=head.state_id,
                    declared_parent=state.parent_state_id,
                )
            if state.sequence != head.sequence + 1:
                raise StateImmutabilityError(
                    "state sequence must increase by exactly one",
                    expected=head.sequence + 1,
                    declared=state.sequence,
                )
        if any(existing.state_id == state.state_id for existing in self._states):
            raise StateImmutabilityError(
                "this state is already in the timeline", state_id=state.state_id
            )
        self._states.append(state)
        return state

    def states(self) -> tuple[ConstitutionalState, ...]:
        return tuple(self._states)

    def head(self) -> ConstitutionalState | None:
        return self._states[-1] if self._states else None

    def require_head(self) -> ConstitutionalState:
        head = self.head()
        if head is None:
            raise StateImmutabilityError("the timeline is empty")
        return head

    def get(self, state_id: str) -> ConstitutionalState | None:
        for state in self._states:
            if state.state_id == str(state_id):
                return state
        return None

    def lineage(self, state_id: str) -> tuple[str, ...]:
        """The chain of state identities from genesis to ``state_id``."""
        chain: list[str] = []
        current = self.get(state_id)
        while current is not None:
            chain.append(current.state_id)
            if current.is_genesis:
                break
            current = self.get(current.parent_state_id)
        return tuple(reversed(chain))

    def __len__(self) -> int:
        return len(self._states)

    def state_ids(self) -> tuple[str, ...]:
        return tuple(state.state_id for state in self._states)

    def verify(self) -> bool:
        """True iff every state is intact and every parent link is well-founded."""
        previous: ConstitutionalState | None = None
        for state in self._states:
            if not state.verify_integrity():
                return False
            if previous is None:
                if not state.is_genesis:
                    return False
            elif (
                state.parent_state_id != previous.state_id
                or state.sequence != previous.sequence + 1
            ):
                return False
            previous = state
        return True

    def replay(self) -> tuple[str, ...]:
        """Recompute every state identity from its recorded core (Invariant 15).

        A timeline replays iff every identity re-derives to the value it was stored
        under. Because identities are content digests, this simultaneously proves the
        chain is intact and that nothing was rewritten between then and now.
        """
        return tuple(state.derived_state_id() for state in self._states)

    def replays_identically(self) -> bool:
        return self.replay() == self.state_ids()

    def proofs_complete(self) -> bool:
        """True iff every state carries three holding proofs."""
        return all(state.proofs_hold() for state in self._states)

    def audit_complete(self) -> bool:
        """True iff every state carries at least one audit entry (Invariant 17)."""
        return all(state.audit_trail for state in self._states)

    def to_document(self) -> dict[str, object]:
        return {
            "schema": "ucos-uckp-constitutional-timeline",
            "version": "1.0.0",
            "counts": {"states": len(self._states)},
            "head": self.head().state_id if self._states else "",
            "verified": self.verify(),
            "replays_identically": self.replays_identically(),
            "states": [state.to_dict() for state in self._states],
        }

    def fingerprint(self) -> str:
        return content_hash(list(self.state_ids()))


__all__ = [
    "AUTHORITY",
    "CAPABILITY",
    "CERTIFICATION",
    "DELTA_REGISTERS",
    "EVIDENCE",
    "GENESIS_PARENT",
    "KNOWLEDGE",
    "ConstitutionalDelta",
    "ConstitutionalState",
    "ConstitutionalTimeline",
    "Proof",
]
