"""UCOS-CAG-000001 — the Constitutional Authority Graph (Requirement 005).

Ownership already has an authority in this repository: :mod:`engine.nucleus.ownership`
measures *who owns what* and refuses a capability owned by a layer or a composition. What
it does not answer — because it is not its question — is whether the authority chain
itself closes: whether a subject is, directly or through a chain of intermediaries, the
source of its own permission to exist.

This module answers exactly that, and it does so by reading the same graph
:mod:`engine.constitution.dependency` already derived rather than building a second one.
There is no separate authority traversal here; there is a *reading* of three relations
and four attestation acts, all of which are facets of the metadata mandate.

The two failures it names
-------------------------
**Circularity** — a cycle in the authority, certification or ownership relation. A
certifies B, B certifies A: each is certified, and nothing was proven. Refused rather than
broken, because any tie-break would be this module inventing the authority.

**Self-attestation** — a subject naming itself as its own certifier, validator, verifier
or ratifier. This is the degenerate one-node cycle, and it is separated out because it is
the common one and deserves its own finding rather than being reported as "a cycle of
length 1", which reads like a graph defect instead of the constitutional defect it is.

Both are trust-based operation in its purest form, and CEL-05 refuses both.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from engine.constitution.dependency import DependencyGraph
from engine.constitution.errors import CircularAuthority, SelfAttestation
from engine.constitution.metadata import Population
from engine.uckp.canonical import content_hash

#: The identity of the authority graph this module realises.
AUTHORITY_GRAPH_ID = "UCOS-CAG-000001"

#: Versioned so acts and relations can be *added* without prior findings changing.
AUTHORITY_VERSION = "1.0.0"


@dataclass(frozen=True, slots=True)
class Act:
    """One constitutional act, and the facet naming who performs it on a subject.

    Held as data so a fifth act — attest, endorse, accredit — is one appended entry with
    no change to the detection below.
    """

    act: str
    facet_id: str
    statement: str

    def to_dict(self) -> dict[str, Any]:
        return {"act": self.act, "facet_id": self.facet_id, "statement": self.statement}


#: The acts a subject may not perform upon itself (DATA — extend by appending).
ATTESTATION_ACTS: tuple[Act, ...] = (
    Act("certify", "certifications", "no subject certifies itself"),
    Act("validate", "validation_rules", "no subject validates itself"),
    Act("verify", "verification_rules", "no subject verifies itself"),
    Act("ratify", "governance_rules", "no subject ratifies itself"),
)

#: The relations that must close acyclically, and the invariant each is measured under.
CIRCULAR_RELATIONS: Mapping[str, str] = {
    "authorities": "CEL-INV-04",
    "certifications": "CEL-INV-05",
    "canonical_owner": "CEL-INV-06",
}


@dataclass(frozen=True, slots=True)
class AuthorityFinding:
    """One measured breach of CEL-05, attributed to the invariant it violates."""

    invariant_id: str
    kind: str
    subject: str
    detail: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "invariant_id": self.invariant_id,
            "kind": self.kind,
            "subject": self.subject,
            "detail": self.detail,
        }


@dataclass(frozen=True, slots=True)
class AuthorityReport:
    """The authority graph's verdict: findings, per-invariant counts, fail-closed status."""

    authority_graph_id: str
    findings: tuple[AuthorityFinding, ...]
    measurements: Mapping[str, int]
    scope: Mapping[str, Any]

    @property
    def self_attestations(self) -> tuple[AuthorityFinding, ...]:
        return tuple(f for f in self.findings if f.kind == "self-attestation")

    @property
    def circularities(self) -> tuple[AuthorityFinding, ...]:
        return tuple(f for f in self.findings if f.kind == "circularity")

    @property
    def passed(self) -> bool:
        """True iff no authority, certification or ownership breach was measured."""
        return not self.findings

    @property
    def status(self) -> str:
        return "PASS" if self.passed else "FAIL"

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": "ucos-constitutional-authority-graph",
            "version": AUTHORITY_VERSION,
            "authority_graph_id": self.authority_graph_id,
            "status": self.status,
            "measurements": {k: self.measurements[k] for k in sorted(self.measurements)},
            "findings": [f.to_dict() for f in self.findings],
            "acts": [a.to_dict() for a in ATTESTATION_ACTS],
            "relations": dict(sorted(CIRCULAR_RELATIONS.items())),
            "scope": {k: self.scope[k] for k in sorted(self.scope)},
        }

    def digest(self) -> str:
        return content_hash(self.to_dict())


def _self_attestation_findings(population: Population) -> list[AuthorityFinding]:
    """Every subject that names itself under an act it may not perform on itself."""
    findings: list[AuthorityFinding] = []
    for record in population:
        for act in ATTESTATION_ACTS:
            if record.subject in record.entries(act.facet_id):
                findings.append(
                    AuthorityFinding(
                        invariant_id="CEL-INV-07",
                        kind="self-attestation",
                        subject=record.subject,
                        detail=(
                            f"declares itself under {act.facet_id!r}: "
                            f"{act.statement} (act={act.act})"
                        ),
                    )
                )
    return findings


def _circularity_findings(graph: DependencyGraph) -> list[AuthorityFinding]:
    """Every subject lying on a cycle in a relation that must close acyclically."""
    findings: list[AuthorityFinding] = []
    for relation, invariant_id in sorted(CIRCULAR_RELATIONS.items()):
        if relation not in graph.relations:
            continue
        for subject in graph.cycles(relation):
            findings.append(
                AuthorityFinding(
                    invariant_id=invariant_id,
                    kind="circularity",
                    subject=subject,
                    detail=(
                        f"lies on a cycle in the {relation!r} relation; the subject "
                        "derives its own authority, so nothing is proven"
                    ),
                )
            )
    return findings


def analyse(population: Population, graph: DependencyGraph) -> AuthorityReport:
    """Measure every CEL-05 breach over ``population`` and return the verdict.

    Takes the already-derived graph rather than deriving its own: two traversals of the
    same declarations could disagree, and a disagreement between the dependency graph and
    the authority graph would be a second truth about the same relation.
    """
    findings = _self_attestation_findings(population) + _circularity_findings(graph)
    findings.sort(key=lambda f: (f.invariant_id, f.subject, f.detail))
    measurements = {invariant_id: 0 for invariant_id in sorted(set(CIRCULAR_RELATIONS.values()))}
    measurements["CEL-INV-07"] = 0
    for finding in findings:
        measurements[finding.invariant_id] += 1
    return AuthorityReport(
        authority_graph_id=AUTHORITY_GRAPH_ID,
        findings=tuple(findings),
        measurements=measurements,
        scope={
            "subjects": len(population),
            "acts": [a.act for a in ATTESTATION_ACTS],
            "relations": sorted(CIRCULAR_RELATIONS),
        },
    )


def gate(population: Population, graph: DependencyGraph) -> AuthorityReport:
    """Run the authority gate and raise if it fails — the fail-closed entry point.

    Self-attestation is raised as its own error type even though it is a circularity,
    because a caller catching :class:`SelfAttestation` is handling a different remediation
    (remove the self-reference) from one catching :class:`CircularAuthority` (introduce an
    independent authority). Both remain catchable as the latter.

    Raises:
        SelfAttestation: a subject certifies, validates, verifies or ratifies itself.
        CircularAuthority: the authority, certification or ownership relation has a cycle.
    """
    report = analyse(population, graph)
    if report.self_attestations:
        raise SelfAttestation(
            "a subject attested to itself; no independent authority proved anything",
            authority_graph_id=AUTHORITY_GRAPH_ID,
            findings=[f.to_dict() for f in report.self_attestations],
        )
    if report.circularities:
        raise CircularAuthority(
            "the authority graph contains a cycle; no order of authority exists",
            authority_graph_id=AUTHORITY_GRAPH_ID,
            findings=[f.to_dict() for f in report.circularities],
        )
    return report


def authority_closure(
    graph: DependencyGraph,
    subject: str,
    *,
    relations: Sequence[str] | None = None,
) -> tuple[str, ...]:
    """Everything ``subject`` ultimately derives its authority from.

    Requirement 002's "authority closure", computed by the one closure walk in
    :mod:`engine.constitution.dependency` rather than a second implementation here.
    """
    chosen = tuple(relations) if relations is not None else tuple(sorted(CIRCULAR_RELATIONS))
    return graph.closure(subject, relations=[r for r in chosen if r in graph.relations])


def to_document() -> dict[str, Any]:
    """The authority model itself as a deterministic, machine-readable document."""
    return {
        "schema": "ucos-constitutional-authority-model",
        "version": AUTHORITY_VERSION,
        "authority_graph_id": AUTHORITY_GRAPH_ID,
        "acts": [a.to_dict() for a in ATTESTATION_ACTS],
        "relations": dict(sorted(CIRCULAR_RELATIONS.items())),
        "closed_set": False,
    }


def digest() -> str:
    return content_hash(to_document())


__all__ = [
    "ATTESTATION_ACTS",
    "AUTHORITY_GRAPH_ID",
    "AUTHORITY_VERSION",
    "CIRCULAR_RELATIONS",
    "Act",
    "AuthorityFinding",
    "AuthorityReport",
    "analyse",
    "authority_closure",
    "digest",
    "gate",
    "to_document",
]
