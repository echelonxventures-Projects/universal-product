"""UCXI-000001 Part 01 — the Context Constitution, as executable law.

Twelve laws govern all context in the platform. They are not prose in a document that
code is trusted to honour: each law carries a **check** that computes its own
compliance from the registry, the graph and (where relevant) a composition. A law with
no reachable check would be manual governance, which this repository forbids, so the
constitution refuses to construct itself if any law is unchecked.

The laws (Part 01 §2):

    CXL-01  Universal Representability — every universal kind is classifiable and has a
            declared shape; nothing about a situation is inexpressible.
    CXL-02  Bounded Extension — the taxonomy is open, but only through declaration: a
            future context type is admitted as data, never invented at a call site.
    CXL-03  Explicit Boundedness — every context is bound to exactly one frame.
    CXL-04  Context Isolation — no reference crosses a frame boundary without an
            explicit federation.
    CXL-05  Deterministic Identity — a context's identity is a pure function of its
            identity tuple, minted by the single registration authority.
    CXL-06  Context Once — one canonical home per unit of context.
    CXL-07  Explicit Precedence — conflicts resolve by declared authority and
            specificity, or they are refused; never by arbitrary order.
    CXL-08  Mandatory Provenance — every asserted value names its authority and source.
    CXL-09  Sealed Content — every context and every derived artefact carries a
            reproducible content seal.
    CXL-10  Zero Authority — context describes; it never grants. Observation is not
            permission.
    CXL-11  Fail-Closed — ambiguity, cycles and broken history are refused, not
            defaulted.
    CXL-12  Append-Only History — context is superseded, never overwritten, and the
            history is hash-chained.

This module is DERIVED TRUTH about the platform's own rules: it legislates nothing
that the repository's governing instruments do not already require, and it grants no
authority to anything (CXL-10 applies to the constitution module itself).
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from engine.context.errors import ConstitutionViolation, TaxonomyError
from engine.context.graph import ContextGraph, build_context_graph
from engine.context.model import ContextRelationEdge, seal
from engine.context.registry import ContextRegistry
from engine.context.resolution import ContextRequest, try_resolve
from engine.context.taxonomy import ContextAuthority, ContextKind, ContextRelation


@dataclass(frozen=True, slots=True)
class ContextLaw:
    """One law of the Context Constitution."""

    law_id: str
    title: str
    statement: str
    rationale: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "law_id": self.law_id,
            "title": self.title,
            "statement": self.statement,
            "rationale": self.rationale,
        }


@dataclass(frozen=True, slots=True)
class ConstitutionSubject:
    """What a law is assessed against.

    ``graph`` and ``composed`` are optional: a law that needs a structure it was not
    given reports that it could not be assessed rather than passing vacuously.
    """

    registry: ContextRegistry
    graph: ContextGraph | None = None
    composed: Any = None  # ComposedContext | None (typed loosely to avoid an import cycle)


@dataclass(frozen=True, slots=True)
class LawAssessment:
    """The computed outcome of one law."""

    law_id: str
    title: str
    compliant: bool
    findings: tuple[str, ...] = ()
    assessed: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "law_id": self.law_id,
            "title": self.title,
            "compliant": self.compliant,
            "assessed": self.assessed,
            "findings": list(self.findings),
        }


@dataclass(frozen=True, slots=True)
class ConstitutionAssessment:
    """The outcome of assessing every law against one subject."""

    laws: tuple[LawAssessment, ...]
    content_hash: str = field(default="", compare=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "laws", tuple(sorted(self.laws, key=lambda law: law.law_id)))
        if not self.content_hash:
            object.__setattr__(self, "content_hash", seal(self._payload()))

    def _payload(self) -> dict[str, Any]:
        return {"laws": [law.to_dict() for law in self.laws]}

    @property
    def compliant(self) -> bool:
        """True iff no assessed law is violated."""
        return all(law.compliant for law in self.laws)

    @property
    def violations(self) -> tuple[LawAssessment, ...]:
        return tuple(law for law in self.laws if not law.compliant)

    def findings(self) -> tuple[str, ...]:
        """Every finding across every law, in law order."""
        out: list[str] = []
        for law in self.laws:
            out.extend(f"{law.law_id}: {finding}" for finding in law.findings)
        return tuple(out)

    def law(self, law_id: str) -> LawAssessment | None:
        for law in self.laws:
            if law.law_id == law_id:
                return law
        return None

    def summary(self) -> dict[str, Any]:
        return {
            "laws": len(self.laws),
            "compliant": sum(1 for law in self.laws if law.compliant),
            "violated": [law.law_id for law in self.violations],
            "unassessed": [law.law_id for law in self.laws if not law.assessed],
            "is_compliant": self.compliant,
            "content_hash": self.content_hash,
        }

    def to_dict(self) -> dict[str, Any]:
        payload = self._payload()
        payload["is_compliant"] = self.compliant
        payload["content_hash"] = self.content_hash
        return payload


# --------------------------------------------------------------------------- #
# The laws (DATA)                                                              #
# --------------------------------------------------------------------------- #

CONTEXT_LAWS: tuple[ContextLaw, ...] = (
    ContextLaw(
        law_id="CXL-01",
        title="Universal Representability",
        statement="Every universal context kind is classified and has a declared shape; "
        "every registered context conforms to the shape of its kind.",
        rationale="If a situation cannot be expressed, it will be asserted informally instead.",
    ),
    ContextLaw(
        law_id="CXL-02",
        title="Bounded Extension",
        statement="A context kind exists only if the taxonomy classifies it and the "
        "ontology specifies it. Future kinds are admitted by declaration.",
        rationale="Openness without declaration is indistinguishable from drift.",
    ),
    ContextLaw(
        law_id="CXL-03",
        title="Explicit Boundedness",
        statement="Every context is bound to exactly one frame; no context is unbounded.",
        rationale="An unbounded context silently applies everywhere, which is never intended.",
    ),
    ContextLaw(
        law_id="CXL-04",
        title="Context Isolation",
        statement="No context may reference a context in another frame without an "
        "explicit federation authorising it.",
        rationale="Implicit cross-boundary reference is the mechanism by which scope leaks.",
    ),
    ContextLaw(
        law_id="CXL-05",
        title="Deterministic Identity",
        statement="A context's identity is a pure function of (kind, namespace, natural "
        "key), minted by the single registration authority.",
        rationale="Reproducible identity is what makes duplicate detection possible.",
    ),
    ContextLaw(
        law_id="CXL-06",
        title="Context Once",
        statement="One canonical home per unit of context: identical substance may not be "
        "registered under two identities, and every context has exactly one taxon.",
        rationale="Two homes for one fact guarantee eventual disagreement.",
    ),
    ContextLaw(
        law_id="CXL-07",
        title="Explicit Precedence",
        statement="Conflicting assertions resolve by declared authority and specificity; "
        "an unresolvable conflict is refused.",
        rationale="Silent last-writer-wins makes the resolved value an accident.",
    ),
    ContextLaw(
        law_id="CXL-08",
        title="Mandatory Provenance",
        statement="Every asserted value names its authority and its source.",
        rationale="An unattributed value cannot be audited, challenged, or superseded.",
    ),
    ContextLaw(
        law_id="CXL-09",
        title="Sealed Content",
        statement="Every context and every derived artefact carries a content seal that "
        "reproduces from its own payload.",
        rationale="Without a seal, drift and tampering are indistinguishable from change.",
    ),
    ContextLaw(
        law_id="CXL-10",
        title="Zero Authority",
        statement="Context describes and never grants. Observer context carries no "
        "constitutional authority, and observation is not constraint.",
        rationale="Ambient context is the easiest place to smuggle in privilege.",
    ),
    ContextLaw(
        law_id="CXL-11",
        title="Fail-Closed",
        statement="Ambiguity, hierarchy cycles, unclassified contexts and broken history "
        "are refused rather than defaulted.",
        rationale="A permissive default is a decision no one made and no one recorded.",
    ),
    ContextLaw(
        law_id="CXL-12",
        title="Append-Only History",
        statement="Context is superseded, never overwritten; every write appends a "
        "hash-chained journal entry.",
        rationale="Overwritten context destroys the record of why a decision was right.",
    ),
)


# --------------------------------------------------------------------------- #
# The checks                                                                   #
# --------------------------------------------------------------------------- #


def _check_representability(subject: ConstitutionSubject) -> list[str]:
    registry = subject.registry
    findings: list[str] = []
    for kind in registry.taxonomy.universal_kinds():
        if not registry.ontology.specifies(kind):
            findings.append(f"universal kind {kind!r} has no declared ontological shape")
    for record in registry.records():
        findings.extend(
            registry.ontology.check_values(
                record.kind, record.value_mapping(), at=record.context_id
            )
        )
    return findings


def _check_bounded_extension(subject: ConstitutionSubject) -> list[str]:
    registry = subject.registry
    findings: list[str] = []
    classified = set(registry.taxonomy.kinds())
    for kind in registry.kinds():
        if kind not in classified:
            findings.append(f"registered kind {kind!r} is not classified by the taxonomy")
        elif not registry.ontology.specifies(kind):
            findings.append(f"registered kind {kind!r} has no declared ontological shape")
    for kind in registry.taxonomy.future_kinds():
        if not registry.ontology.specifies(kind):
            findings.append(f"future kind {kind!r} was admitted without a declared shape")
    return findings


def _check_boundedness(subject: ConstitutionSubject) -> list[str]:
    return [
        f"context {record.context_id} declares no bounding frame"
        for record in subject.registry.records()
        if not record.boundary
    ]


def _check_isolation(subject: ConstitutionSubject) -> list[str]:
    registry = subject.registry
    findings: list[str] = []
    federated = {
        (edge.source, edge.target)
        for edge in registry.relations(relation=ContextRelation.FEDERATES)
    }
    dependency_relations = (
        ContextRelation.DEPENDS_ON,
        ContextRelation.DERIVES_FROM,
        ContextRelation.REFINES,
    )
    for relation in dependency_relations:
        for edge in registry.relations(relation=relation):
            source = registry.find(edge.source)
            target = registry.find(edge.target)
            if source is None or target is None:
                continue
            if source.boundary != target.boundary and (edge.source, edge.target) not in federated:
                findings.append(
                    f"{edge.source} -> {edge.target} crosses frames "
                    f"({source.boundary} -> {target.boundary}) without a federation"
                )
    composed = subject.composed
    if composed is not None:
        for reference_frame in composed.reference_frames:
            for target in reference_frame.federated:
                if composed.frame_of(target) == reference_frame.context_id:
                    findings.append(
                        f"{reference_frame.universe_id} federates into its own frame "
                        f"{reference_frame.context_id}"
                    )
    return findings


def _check_identity(subject: ConstitutionSubject) -> list[str]:
    return [
        f"context {record.context_id} does not reproduce its own identity "
        f"(expected {record.expected_identity()})"
        for record in subject.registry.records()
        if record.context_id != record.expected_identity()
    ]


def _check_context_once(subject: ConstitutionSubject) -> list[str]:
    registry = subject.registry
    findings: list[str] = []
    substance: dict[str, str] = {}
    for record in registry.records():
        digest = registry.substance_hash(record)
        owner = substance.setdefault(digest, record.context_id)
        if owner != record.context_id:
            findings.append(f"context {record.context_id} duplicates the substance of {owner}")
        try:
            taxon = registry.taxonomy.taxon_for_kind(record.kind)
        except TaxonomyError:
            findings.append(f"context {record.context_id} has no canonical taxon")
            continue
        if record.taxon_id != taxon.taxon_id:
            findings.append(
                f"context {record.context_id} claims taxon {record.taxon_id} but its kind "
                f"is classified as {taxon.taxon_id}"
            )
    return findings


def _check_precedence(subject: ConstitutionSubject) -> list[str]:
    registry = subject.registry
    findings: list[str] = []
    active_kinds = {record.kind for record in registry.records() if record.lifecycle.is_active}
    for kind in sorted(active_kinds):
        resolved, reason = try_resolve(registry, ContextRequest(kind=kind))
        if resolved is None:
            findings.append(f"kind {kind!r} has an active context but is not resolvable: {reason}")
    return findings


def _check_provenance(subject: ConstitutionSubject) -> list[str]:
    findings: list[str] = []
    for record in subject.registry.records():
        for value in record.values:
            if not value.source:
                findings.append(
                    f"{record.context_id}: dimension {value.dimension!r} names no source"
                )
    return findings


def _check_seals(subject: ConstitutionSubject) -> list[str]:
    findings: list[str] = []
    for record in subject.registry.records():
        if record.content_hash != record.recomputed_hash():
            findings.append(f"context {record.context_id} content seal does not reproduce")
    for edge in subject.registry.relations():
        recomputed = ContextRelationEdge(
            relation=edge.relation, source=edge.source, target=edge.target
        ).edge_id
        if edge.edge_id != recomputed:
            findings.append(f"relation {edge.edge_id} identity does not reproduce")
    return findings


def _check_zero_authority(subject: ConstitutionSubject) -> list[str]:
    registry = subject.registry
    findings: list[str] = []
    for record in registry.by_kind(ContextKind.OBSERVER):
        if record.authority is ContextAuthority.CONSTITUTIONAL:
            findings.append(
                f"observer context {record.context_id} claims constitutional authority "
                "(observation confers no authority)"
            )
    observes = {
        (edge.source, edge.target) for edge in registry.relations(relation=ContextRelation.OBSERVES)
    }
    for edge in registry.relations(relation=ContextRelation.CONSTRAINS):
        if (edge.source, edge.target) in observes:
            findings.append(
                f"{edge.source} both observes and constrains {edge.target} "
                "(observation is not constraint)"
            )
    return findings


def _check_fail_closed(subject: ConstitutionSubject) -> list[str]:
    registry = subject.registry
    findings = list(registry.verify_audit())
    graph = subject.graph if subject.graph is not None else build_context_graph(registry)
    findings.extend(graph.validate())
    return findings


def _check_append_only(subject: ConstitutionSubject) -> list[str]:
    registry = subject.registry
    findings = list(registry.verify_audit())
    journaled = {entry.subject for entry in registry.audit()}
    for record in registry.records():
        if record.context_id not in journaled:
            findings.append(f"context {record.context_id} was never journaled")
    for edge in registry.relations(relation=ContextRelation.SUPERSEDES):
        predecessor = registry.find(edge.target)
        if predecessor is None:
            findings.append(f"supersession target {edge.target} is absent (history was destroyed)")
    return findings


#: law id -> the check that computes its compliance.
LAW_CHECKS: dict[str, Callable[[ConstitutionSubject], list[str]]] = {
    "CXL-01": _check_representability,
    "CXL-02": _check_bounded_extension,
    "CXL-03": _check_boundedness,
    "CXL-04": _check_isolation,
    "CXL-05": _check_identity,
    "CXL-06": _check_context_once,
    "CXL-07": _check_precedence,
    "CXL-08": _check_provenance,
    "CXL-09": _check_seals,
    "CXL-10": _check_zero_authority,
    "CXL-11": _check_fail_closed,
    "CXL-12": _check_append_only,
}


class ContextConstitution:
    """The executable Context Constitution.

    Construction refuses a constitution in which any law lacks a check, so the
    instrument cannot drift into prose that nothing enforces.
    """

    __slots__ = ("_laws", "_checks")

    def __init__(
        self,
        laws: tuple[ContextLaw, ...] = CONTEXT_LAWS,
        checks: dict[str, Callable[[ConstitutionSubject], list[str]]] | None = None,
    ) -> None:
        resolved_checks = LAW_CHECKS if checks is None else checks
        unchecked = [law.law_id for law in laws if law.law_id not in resolved_checks]
        if unchecked:
            raise ConstitutionViolation(
                "every law must carry an executable check (no manual governance)",
                laws=unchecked,
            )
        orphan_checks = sorted(set(resolved_checks) - {law.law_id for law in laws})
        if orphan_checks:
            raise ConstitutionViolation(
                "a check exists for a law that is not declared", checks=orphan_checks
            )
        self._laws = tuple(sorted(laws, key=lambda law: law.law_id))
        self._checks = dict(resolved_checks)

    def laws(self) -> tuple[ContextLaw, ...]:
        """Every law, ordered by identifier."""
        return self._laws

    def law(self, law_id: str) -> ContextLaw:
        for law in self._laws:
            if law.law_id == law_id:
                return law
        raise ConstitutionViolation("no such context law", law_id=law_id)

    def assess(
        self,
        registry: ContextRegistry,
        *,
        graph: ContextGraph | None = None,
        composed: Any = None,
    ) -> ConstitutionAssessment:
        """Compute compliance of every law against the given subject."""
        subject = ConstitutionSubject(registry=registry, graph=graph, composed=composed)
        outcomes: list[LawAssessment] = []
        for law in self._laws:
            findings = tuple(self._checks[law.law_id](subject))
            outcomes.append(
                LawAssessment(
                    law_id=law.law_id,
                    title=law.title,
                    compliant=not findings,
                    findings=findings,
                )
            )
        return ConstitutionAssessment(laws=tuple(outcomes))

    def require_compliance(
        self,
        registry: ContextRegistry,
        *,
        graph: ContextGraph | None = None,
        composed: Any = None,
    ) -> ConstitutionAssessment:
        """Fail-closed form of :meth:`assess`."""
        assessment = self.assess(registry, graph=graph, composed=composed)
        if not assessment.compliant:
            raise ConstitutionViolation(
                "the context set breaches the Context Constitution",
                laws=[law.law_id for law in assessment.violations],
                findings=list(assessment.findings()),
            )
        return assessment

    def to_dict(self) -> dict[str, Any]:
        return {
            "laws": [law.to_dict() for law in self._laws],
            "count": len(self._laws),
        }


#: The default constitution instance.
CONTEXT_CONSTITUTION = ContextConstitution()


__all__ = [
    "ContextLaw",
    "ConstitutionSubject",
    "LawAssessment",
    "ConstitutionAssessment",
    "CONTEXT_LAWS",
    "LAW_CHECKS",
    "ContextConstitution",
    "CONTEXT_CONSTITUTION",
]
