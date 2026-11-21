"""UCOS-CLE-000001 — the Constitutional Legality Engine (Requirement 003).

Every execution request must *prove* nine things. This module is where the nine proofs
live, and the only place any of them is decided.

The engineering point of it is the shape of :data:`PROOFS`: nine entries, each a name, a
statement and a function of ``(record, graph, population)``. Legality is therefore a fold
over data, not a nine-branch conditional — a tenth obligation is one appended entry, and
:meth:`LegalityVerdict.legal` needs no edit to start requiring it. Anything that reads the
proof set (the planner, the gateway, the acceptance gate, the CLI) picks it up in the same
commit that declares it.

Fail-closed, precisely
----------------------
There is no partial legality: :attr:`LegalityVerdict.legal` is ``all(...)`` over the
blocking proofs, so a proof that raises, returns nothing, or was never written is a
failure and not an omission. There is no assumed legality: a proof reads only the derived
graph and the declared population, never a cached verdict. And there is no trust-based
legality: no proof takes an argument by which a caller could assert a result.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import Any

from engine.constitution.authority import ATTESTATION_ACTS
from engine.constitution.dependency import DependencyGraph
from engine.constitution.errors import IllegalExecution
from engine.constitution.metadata import ConstitutionalMetadata, Population
from engine.uckp.canonical import content_hash

#: The identity of the legality engine this module realises.
LEGALITY_ENGINE_ID = "UCOS-CLE-000001"

#: Versioned so proofs can be *appended* without any prior verdict changing meaning.
LEGALITY_VERSION = "1.0.0"


@dataclass(frozen=True, slots=True)
class Proof:
    """The outcome of one legality obligation over one subject."""

    name: str
    satisfied: bool
    statement: str
    detail: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "satisfied": self.satisfied,
            "statement": self.statement,
            "detail": self.detail,
        }


#: A proof function: given the record, the derived graph and the population, decide.
#: Pure and total — it reads no clock, no filesystem and no network, so a verdict
#: replays byte-identically.
ProofFunction = Callable[
    [ConstitutionalMetadata, DependencyGraph, Population],
    "tuple[bool, str]",
]


@dataclass(frozen=True, slots=True)
class Obligation:
    """One of the nine things an execution request must prove."""

    name: str
    statement: str
    check: ProofFunction
    blocking: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {"name": self.name, "statement": self.statement, "blocking": self.blocking}


# --------------------------------------------------------------------------- #
# The nine proofs                                                              #
# --------------------------------------------------------------------------- #


def _facet_closed(
    record: ConstitutionalMetadata,
    population: Population,
    facet_id: str,
) -> tuple[bool, str]:
    """Shared shape: the facet is declared, and every referent it names exists.

    Five of the nine obligations are this same question asked of a different facet, so
    asking it once removes five chances for the five to drift apart.
    """
    declared = record.entries(facet_id)
    if not declared:
        return False, f"{facet_id} is undeclared"
    dangling = sorted(target for target in record.referents(facet_id) if target not in population)
    if dangling:
        return False, f"{facet_id} names unregistered subjects: {', '.join(dangling)}"
    return True, ""


def _dependency_complete(
    record: ConstitutionalMetadata,
    graph: DependencyGraph,
    population: Population,
) -> tuple[bool, str]:
    ok, detail = _facet_closed(record, population, "dependencies")
    if not ok:
        return ok, detail
    # A dependency that is itself incomplete does not satisfy this subject's dependency:
    # closure means the *whole chain* is declared, not only the first hop. This is what
    # makes "a dependency cannot be skipped" true transitively rather than locally.
    incomplete = sorted(
        target
        for target in graph.closure(record.subject, relations=["dependencies"])
        if target in population and not population.get(target).complete
    )
    if incomplete:
        return False, f"dependency closure contains incomplete subjects: {', '.join(incomplete)}"
    return True, ""


def _governance_complete(
    record: ConstitutionalMetadata,
    graph: DependencyGraph,
    population: Population,
) -> tuple[bool, str]:
    return _facet_closed(record, population, "governance_rules")


def _authority_complete(
    record: ConstitutionalMetadata,
    graph: DependencyGraph,
    population: Population,
) -> tuple[bool, str]:
    ok, detail = _facet_closed(record, population, "authorities")
    if not ok:
        return ok, detail
    # CEL-05, applied to this one subject. The population-wide sweep lives in
    # engine.constitution.authority; this is the per-request restatement, because a
    # legality verdict must be self-contained evidence about its own subject.
    for act in ATTESTATION_ACTS:
        if record.subject in record.entries(act.facet_id):
            return False, f"attests to itself under {act.facet_id} (act={act.act})"
    if record.subject in graph.closure(record.subject, relations=["authorities"]):
        return False, "authority chain returns to the subject itself"
    return True, ""


def _identity_complete(
    record: ConstitutionalMetadata,
    graph: DependencyGraph,
    population: Population,
) -> tuple[bool, str]:
    if not record.universal_id:
        return False, "no universal identifier"
    if not record.identity_well_formed:
        return False, f"universal identifier {record.universal_id!r} is not well formed"
    return True, ""


def _registry_complete(
    record: ConstitutionalMetadata,
    graph: DependencyGraph,
    population: Population,
) -> tuple[bool, str]:
    return _facet_closed(record, population, "registrations")


def _certification_complete(
    record: ConstitutionalMetadata,
    graph: DependencyGraph,
    population: Population,
) -> tuple[bool, str]:
    ok, detail = _facet_closed(record, population, "certifications")
    if not ok:
        return ok, detail
    if record.subject in graph.closure(record.subject, relations=["certifications"]):
        return False, "certification chain returns to the subject itself"
    return True, ""


def _verification_complete(
    record: ConstitutionalMetadata,
    graph: DependencyGraph,
    population: Population,
) -> tuple[bool, str]:
    ok, detail = _facet_closed(record, population, "verification_rules")
    if not ok:
        return ok, detail
    return _facet_closed(record, population, "validation_rules")


def _traceability_complete(
    record: ConstitutionalMetadata,
    graph: DependencyGraph,
    population: Population,
) -> tuple[bool, str]:
    for facet_id in ("traceability_rules", "lineage_rules"):
        ok, detail = _facet_closed(record, population, facet_id)
        if not ok:
            return ok, detail
    return True, ""


def _evidence_complete(
    record: ConstitutionalMetadata,
    graph: DependencyGraph,
    population: Population,
) -> tuple[bool, str]:
    # Evidence is not a facet of its own: a subject produces evidence when it declares
    # what it consumes, what it produces, the constraints it holds within and the rules
    # under which its run reproduces. A subject missing any of those emits output nobody
    # can check, which is a result rather than evidence.
    for facet_id in ("inputs", "outputs", "constraints", "replay_rules"):
        ok, detail = _facet_closed(record, population, facet_id)
        if not ok:
            return ok, detail
    return True, ""


#: The nine obligations (DATA — extend by appending, never edit).
PROOFS: tuple[Obligation, ...] = (
    Obligation(
        "dependency_complete",
        "Every dependency, transitively, is declared, registered and itself complete.",
        _dependency_complete,
    ),
    Obligation(
        "governance_complete",
        "The rules under which the subject is governed are declared and resolve.",
        _governance_complete,
    ),
    Obligation(
        "authority_complete",
        "The subject acts under a declared authority that is not, in the end, itself.",
        _authority_complete,
    ),
    Obligation(
        "identity_complete",
        "The subject carries an identifier the identity authority could have minted.",
        _identity_complete,
    ),
    Obligation(
        "registry_complete",
        "The subject is registered, and the registries it names exist.",
        _registry_complete,
    ),
    Obligation(
        "certification_complete",
        "The subject is certified by declared subjects, and not in the end by itself.",
        _certification_complete,
    ),
    Obligation(
        "verification_complete",
        "The subject declares how it is validated and how it is verified.",
        _verification_complete,
    ),
    Obligation(
        "traceability_complete",
        "The subject declares its lineage and traces to the determination requiring it.",
        _traceability_complete,
    ),
    Obligation(
        "evidence_complete",
        "The subject declares inputs, outputs, constraints and replay rules, so its run "
        "produces evidence rather than only results.",
        _evidence_complete,
    ),
)


@dataclass(frozen=True, slots=True)
class LegalityVerdict:
    """Whether one subject may execute, and the proof of it either way."""

    engine_id: str
    subject: str
    proofs: tuple[Proof, ...]

    @property
    def unproven(self) -> tuple[str, ...]:
        """The names of the blocking obligations that did not prove, ordered."""
        blocking = {o.name for o in PROOFS if o.blocking}
        return tuple(sorted(p.name for p in self.proofs if p.name in blocking and not p.satisfied))

    @property
    def legal(self) -> bool:
        """True iff every blocking obligation proved. There is no partial legality."""
        return not self.unproven

    @property
    def status(self) -> str:
        return "LEGAL" if self.legal else "ILLEGAL"

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": "ucos-constitutional-legality-verdict",
            "version": LEGALITY_VERSION,
            "engine_id": self.engine_id,
            "subject": self.subject,
            "status": self.status,
            "unproven": list(self.unproven),
            "proofs": [p.to_dict() for p in self.proofs],
        }

    def digest(self) -> str:
        return content_hash(self.to_dict())


@dataclass(frozen=True, slots=True)
class LegalityReport:
    """The legality of a whole population — one verdict per subject."""

    engine_id: str
    verdicts: tuple[LegalityVerdict, ...]

    @property
    def illegal(self) -> tuple[LegalityVerdict, ...]:
        return tuple(v for v in self.verdicts if not v.legal)

    @property
    def legal_subjects(self) -> tuple[str, ...]:
        return tuple(v.subject for v in self.verdicts if v.legal)

    @property
    def passed(self) -> bool:
        return not self.illegal

    @property
    def status(self) -> str:
        return "PASS" if self.passed else "FAIL"

    def verdict_for(self, subject: str) -> LegalityVerdict:
        for verdict in self.verdicts:
            if verdict.subject == subject:
                return verdict
        raise IllegalExecution(
            "no legality verdict was computed for this subject",
            engine_id=self.engine_id,
            subject=subject,
        )

    def measurements(self) -> dict[str, int]:
        """How many subjects failed each obligation — where the population is weakest."""
        counts = {obligation.name: 0 for obligation in PROOFS}
        for verdict in self.verdicts:
            for name in verdict.unproven:
                counts[name] += 1
        return counts

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": "ucos-constitutional-legality-report",
            "version": LEGALITY_VERSION,
            "engine_id": self.engine_id,
            "status": self.status,
            "subject_count": len(self.verdicts),
            "illegal_count": len(self.illegal),
            "measurements": self.measurements(),
            "obligations": [o.to_dict() for o in PROOFS],
            "verdicts": [v.to_dict() for v in self.verdicts],
        }

    def digest(self) -> str:
        return content_hash(self.to_dict())


def prove(
    record: ConstitutionalMetadata,
    graph: DependencyGraph,
    population: Population,
    *,
    obligations: Sequence[Obligation] = PROOFS,
) -> LegalityVerdict:
    """Run every obligation over one subject and return the verdict, satisfied or not.

    A proof that raises is recorded as *unsatisfied with the exception as its detail*
    rather than propagating. That is deliberate and it is the fail-closed reading: an
    obligation that could not be evaluated has not been proven, and a report that names
    the failure is more useful than a traceback that hides the other eight results.
    """
    proofs: list[Proof] = []
    for obligation in obligations:
        try:
            satisfied, detail = obligation.check(record, graph, population)
        except Exception as exc:  # noqa: BLE001 - an unevaluable proof is an unproven proof
            satisfied, detail = False, f"proof could not be evaluated: {exc}"
        proofs.append(
            Proof(
                name=obligation.name,
                satisfied=bool(satisfied),
                statement=obligation.statement,
                detail=str(detail),
            )
        )
    return LegalityVerdict(
        engine_id=LEGALITY_ENGINE_ID,
        subject=record.subject,
        proofs=tuple(proofs),
    )


def assess(
    population: Population,
    graph: DependencyGraph,
    *,
    obligations: Sequence[Obligation] = PROOFS,
) -> LegalityReport:
    """Prove legality for every subject in ``population``."""
    return LegalityReport(
        engine_id=LEGALITY_ENGINE_ID,
        verdicts=tuple(
            prove(record, graph, population, obligations=obligations) for record in population
        ),
    )


def require_legal(
    record: ConstitutionalMetadata,
    graph: DependencyGraph,
    population: Population,
) -> LegalityVerdict:
    """Return the verdict if the subject is legal, else refuse — the fail-closed gate.

    Raises:
        IllegalExecution: one or more obligations did not prove.
    """
    verdict = prove(record, graph, population)
    if not verdict.legal:
        raise IllegalExecution(
            "execution refused: the subject has not proven constitutional legality",
            engine_id=LEGALITY_ENGINE_ID,
            subject=record.subject,
            unproven=list(verdict.unproven),
            proofs=[p.to_dict() for p in verdict.proofs if not p.satisfied],
        )
    return verdict


def obligation_names() -> tuple[str, ...]:
    """The names of the declared obligations, in declaration order."""
    return tuple(o.name for o in PROOFS)


def to_document() -> dict[str, Any]:
    """The obligation set as a deterministic, machine-readable document."""
    return {
        "schema": "ucos-constitutional-legality-obligations",
        "version": LEGALITY_VERSION,
        "engine_id": LEGALITY_ENGINE_ID,
        "obligation_count": len(PROOFS),
        "obligations": [o.to_dict() for o in PROOFS],
        "closed_set": False,
    }


def digest() -> str:
    return content_hash(to_document())


__all__ = [
    "LEGALITY_ENGINE_ID",
    "LEGALITY_VERSION",
    "PROOFS",
    "LegalityReport",
    "LegalityVerdict",
    "Obligation",
    "Proof",
    "ProofFunction",
    "assess",
    "digest",
    "obligation_names",
    "prove",
    "require_legal",
    "to_document",
]
