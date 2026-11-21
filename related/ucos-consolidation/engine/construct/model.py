"""UCON-000001 Part 01 — the Universal Construct entity, and the records that dispose it.

Everything here is a VALUE. A construct is observed once, frozen, and every derived quantity
on it is a function of attributes it already carries: there is no method in this module that
reads the filesystem, the clock or the network. Assessment lives in
:mod:`engine.construct.reality`, classification in :mod:`engine.construct.disposition`, and
storage in :mod:`engine.construct.registry`. Keeping the value inert is what makes a
construct read back out of evidence comparable to one presented live — they are the same
type, and neither can change under the other.

Four types carry the whole model, and the split between them is the load-bearing design
decision of this capability:

    :class:`Presentation`      what was presented. Contains no verdict of any kind.
    :class:`DispositionRecord` what the governance decided, and under which rule.
    :class:`RealityAssessment` what the evidence supports, and nothing about admission.
    :class:`Construct`         the three joined, with full history.

A single type carrying "kind, payload, admitted, verified" would make *admission implies
truth* structurally expressible, and then no law could refuse it. Because a presentation
carries no disposition and an assessment carries no admission, the sentence "this construct
is admitted, therefore it is true" cannot be written in this model at all — which is a
stronger guarantee than a rule forbidding it.

Identity is derived, never assigned, and it is not a new grammar: it is minted by
:func:`engine.kernel.identity.mint`, the kernel's own pure function over an identity tuple,
so a construct's identifier is a ``UMK-<SLUG>-<12 hex>`` under the authority that already
owns deterministic identity. The natural key is folded through the canonical digest before
minting, which makes identity TOTAL — a natural key containing whitespace, punctuation or a
non-Latin script yields an identifier rather than a refusal. A construct that could not be
named would be a construct that could not be recorded, and an unrecordable construct is
indistinguishable from one that was silently ignored.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field, replace
from types import MappingProxyType
from typing import Any

from engine.kernel.identity import mint
from engine.uckp.canonical import canonical_json, content_hash

#: The namespace every construct identity is minted under. Disclosed in the declaration as
#: gap UCON-G-02: UOBC-000001 has not declared it, so constructs carry no birth record and
#: this capability claims none.
NAMESPACE = "ucos.construct"

#: The label the identity digest is domain-separated with, so a natural key can never be
#: confused with any other digest input in the repository.
_KEY_DOMAIN = "ucon.natural-key"


class ConstructError(RuntimeError):
    """The construct, record or declaration is unusable. A fault, never a disposition.

    Raised for a malformed *record* — a disposition naming no rule, an assessment naming no
    state, a declaration that cannot be read. It is never raised because a construct is
    unknown, contradictory, undecidable or unwelcome: those are dispositions, and a
    disposition is an answer rather than an error.
    """


def construct_id(kind: str, natural_key: str, *, namespace: str = NAMESPACE) -> str:
    """Return the deterministic identifier for ``(kind, namespace, natural_key)``.

    Pure and total: no clock, no counter, no path, no I/O, and no natural key it refuses.
    Two presentations of the same logical construct collapse onto one identifier however
    they were phrased, which is what makes re-presentation idempotent and discovery
    convergent.
    """
    if not isinstance(kind, str) or not kind.strip():
        raise ConstructError("a construct kind is required")
    if not isinstance(natural_key, str) or not natural_key.strip():
        raise ConstructError(
            "a construct natural key is required",
        )
    folded = content_hash([_KEY_DOMAIN, natural_key.strip()])
    return mint(kind.strip(), namespace, folded)


def _frozen(value: Mapping[str, Any] | None) -> Mapping[str, Any]:
    return MappingProxyType(dict(value or {}))


def _tuple(value: Any) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, str):
        return (value,)
    return tuple(str(item) for item in value)


# --- what was presented -------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class Evidence:
    """One piece of evidence offered for a construct.

    ``independent`` is what separates "observed twice by one instrument" from "reproduced":
    a reality state declaring an independent-sources floor counts distinct sources, not
    distinct records, because two records from one source are one observation written down
    twice.
    """

    source: str
    statement: str
    independent: bool = True
    evidence_id: str = field(default="", compare=False)

    def __post_init__(self) -> None:
        if not self.source.strip():
            raise ConstructError("evidence must name its source")
        object.__setattr__(self, "source", self.source.strip())
        object.__setattr__(
            self, "evidence_id", content_hash([self.source, self.statement, self.independent])[:16]
        )

    def as_dict(self) -> dict[str, Any]:
        return {
            "evidence_id": self.evidence_id,
            "independent": self.independent,
            "source": self.source,
            "statement": self.statement,
        }


@dataclass(frozen=True, slots=True)
class Lineage:
    """Where a construct came from and what it replaces.

    Never a chain of custody the foundation invents: every entry is an identifier the
    presenter supplied or a derivation this capability performed and recorded.
    """

    derived_from: tuple[str, ...] = ()
    supersedes: tuple[str, ...] = ()
    presented_by: str = ""

    def as_dict(self) -> dict[str, Any]:
        return {
            "derived_from": list(self.derived_from),
            "presented_by": self.presented_by,
            "supersedes": list(self.supersedes),
        }


@dataclass(frozen=True, slots=True)
class Presentation:
    """A construct exactly as presented. Contains no verdict, no status and no permission.

    Note what is absent: there is no ``admitted`` flag, no ``valid`` flag and no ``truth``
    field. A presentation is the thing itself plus what the presenter said about it, and the
    two claims the presenter is allowed to make about the *process* — that an authority
    should decide (``escalation_requested``) and that no decision procedure applies
    (``declared_undecidable``). Both are honoured by declared rules rather than trusted:
    they select a disposition, they do not assert one.
    """

    kind: str
    natural_key: str
    title: str = ""
    payload: Mapping[str, Any] = field(default_factory=dict)
    evidence: tuple[Evidence, ...] = ()
    dependencies: tuple[str, ...] = ()
    lineage: Lineage = field(default_factory=Lineage)
    reality_status: str = ""
    escalation_requested: bool = False
    declared_undecidable: bool = False
    identity: str = field(default="", compare=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "kind", str(self.kind).strip())
        object.__setattr__(self, "natural_key", str(self.natural_key).strip())
        object.__setattr__(self, "title", str(self.title or self.natural_key))
        object.__setattr__(self, "payload", _frozen(self.payload))
        object.__setattr__(self, "evidence", tuple(self.evidence))
        object.__setattr__(self, "dependencies", _tuple(self.dependencies))
        object.__setattr__(self, "identity", construct_id(self.kind, self.natural_key))

    @property
    def evidence_count(self) -> int:
        return len(self.evidence)

    @property
    def independent_sources(self) -> int:
        """Distinct sources that offered independent evidence."""
        return len({item.source for item in self.evidence if item.independent})

    def content_digest(self) -> str:
        """A digest over what was presented, excluding identity (which is derived from it)."""
        return content_hash(
            {
                "dependencies": list(self.dependencies),
                "declared_undecidable": self.declared_undecidable,
                "escalation_requested": self.escalation_requested,
                "evidence": [item.as_dict() for item in self.evidence],
                "kind": self.kind,
                "lineage": self.lineage.as_dict(),
                "natural_key": self.natural_key,
                "payload": dict(self.payload),
                "reality_status": self.reality_status,
                "title": self.title,
            }
        )

    def as_dict(self) -> dict[str, Any]:
        return {
            "declared_undecidable": self.declared_undecidable,
            "dependencies": list(self.dependencies),
            "escalation_requested": self.escalation_requested,
            "evidence": [item.as_dict() for item in self.evidence],
            "identity": self.identity,
            "kind": self.kind,
            "lineage": self.lineage.as_dict(),
            "natural_key": self.natural_key,
            "payload": dict(self.payload),
            "reality_status": self.reality_status,
            "title": self.title,
        }


# --- what governance decided ---------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class DispositionRecord:
    """One disposition assignment: traceable to the rule that made it, and supersedable.

    ``rule_id`` and ``rationale`` are required and are not free text the engine invents —
    both are read from the declared rule that matched, so "why does this construct have this
    disposition" is answerable from the record alone without re-running anything.
    ``inputs_digest`` pins the presentation the decision was made against, so a disposition
    that outlived a change to its subject is detectable rather than merely stale.
    """

    identity: str
    disposition: str
    rule_id: str
    rationale: str
    sequence: int
    inputs_digest: str
    active: bool = True
    superseded_by: str = ""
    record_id: str = field(default="", compare=False)

    def __post_init__(self) -> None:
        for name in ("identity", "disposition", "rule_id", "inputs_digest"):
            if not str(getattr(self, name)).strip():
                raise ConstructError(f"a disposition record requires {name}")
        if self.sequence < 0:
            raise ConstructError("a disposition sequence is a non-negative ordinal")
        object.__setattr__(
            self,
            "record_id",
            content_hash(
                [self.identity, self.disposition, self.rule_id, self.sequence, self.inputs_digest]
            )[:16],
        )

    def superseded(self, by: str) -> DispositionRecord:
        """Return this record marked superseded. History is appended to, never rewritten."""
        return replace(self, active=False, superseded_by=by)

    def as_dict(self) -> dict[str, Any]:
        return {
            "active": self.active,
            "disposition": self.disposition,
            "identity": self.identity,
            "inputs_digest": self.inputs_digest,
            "rationale": self.rationale,
            "record_id": self.record_id,
            "rule_id": self.rule_id,
            "sequence": self.sequence,
            "superseded_by": self.superseded_by,
        }


# --- what the evidence supports ------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class RealityAssessment:
    """One reality assessment. Carries no admission, no disposition and no permission to act.

    ``assessed_from`` names the evidence the state rests on and ``floor_met`` records whether
    the declared evidence floor for that state was actually reached. A state claimed above
    its floor is reported as unmet rather than silently downgraded, because downgrading would
    hide the claim, and the claim is the interesting fact.
    """

    identity: str
    status: str
    evidence_count: int
    independent_sources: int
    assessed_from: tuple[str, ...]
    sequence: int
    floor_met: bool
    active: bool = True
    superseded_by: str = ""
    record_id: str = field(default="", compare=False)

    def __post_init__(self) -> None:
        for name in ("identity", "status"):
            if not str(getattr(self, name)).strip():
                raise ConstructError(f"a reality assessment requires {name}")
        object.__setattr__(self, "assessed_from", _tuple(self.assessed_from))
        object.__setattr__(
            self,
            "record_id",
            content_hash([self.identity, self.status, self.sequence, list(self.assessed_from)])[
                :16
            ],
        )

    def superseded(self, by: str) -> RealityAssessment:
        return replace(self, active=False, superseded_by=by)

    def as_dict(self) -> dict[str, Any]:
        return {
            "active": self.active,
            "assessed_from": list(self.assessed_from),
            "evidence_count": self.evidence_count,
            "floor_met": self.floor_met,
            "identity": self.identity,
            "independent_sources": self.independent_sources,
            "record_id": self.record_id,
            "sequence": self.sequence,
            "status": self.status,
            "superseded_by": self.superseded_by,
        }


# --- the three, joined ---------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class Construct:
    """A presented construct with its full disposition and reality history.

    ``facet_violations`` records required facet fields the payload did not supply. It is a
    RECORD, not a refusal: an unknown presented without its formulation is still an unknown
    that was presented, and refusing it would lose the only evidence that somebody tried.
    The violation travels with the construct so the disposition it receives is actionable.
    """

    presentation: Presentation
    dispositions: tuple[DispositionRecord, ...]
    assessments: tuple[RealityAssessment, ...]
    kind_registered: bool
    facet_violations: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.dispositions:
            raise ConstructError(
                "a construct without a disposition cannot exist "
                f"({self.presentation.identity}): UCON-L-01"
            )
        if not self.assessments:
            raise ConstructError(
                f"a construct without a reality assessment cannot exist "
                f"({self.presentation.identity})"
            )
        active = [record for record in self.dispositions if record.active]
        if len(active) != 1:
            raise ConstructError(
                "a construct carries exactly one active disposition, found "
                f"{len(active)} ({self.presentation.identity}): UCON-L-01"
            )
        live = [record for record in self.assessments if record.active]
        if len(live) != 1:
            raise ConstructError(
                "a construct carries exactly one active reality assessment, found "
                f"{len(live)} ({self.presentation.identity})"
            )
        object.__setattr__(self, "facet_violations", _tuple(self.facet_violations))

    @property
    def identity(self) -> str:
        return self.presentation.identity

    @property
    def kind(self) -> str:
        return self.presentation.kind

    @property
    def disposition(self) -> DispositionRecord:
        """The one active disposition. Existence is an invariant, not a possibility."""
        return next(record for record in self.dispositions if record.active)

    @property
    def reality(self) -> RealityAssessment:
        """The one active reality assessment."""
        return next(record for record in self.assessments if record.active)

    def as_dict(self) -> dict[str, Any]:
        return {
            "assessments": [record.as_dict() for record in self.assessments],
            "disposition": self.disposition.disposition,
            "dispositions": [record.as_dict() for record in self.dispositions],
            "facet_violations": list(self.facet_violations),
            "identity": self.identity,
            "kind": self.kind,
            "kind_registered": self.kind_registered,
            "presentation": self.presentation.as_dict(),
            "reality_status": self.reality.status,
        }


__all__ = [
    "NAMESPACE",
    "Construct",
    "ConstructError",
    "DispositionRecord",
    "Evidence",
    "Lineage",
    "Presentation",
    "RealityAssessment",
    "canonical_json",
    "construct_id",
    "content_hash",
]
