"""UCKP Layer Zero — the thirty-three universal facets (Article 6).

A facet is a question every constitutional object must be able to answer about
itself. Article 6 makes all thirty-three mandatory: a facet may be *unattested*
(no certifier has spoken yet) but it may never be *absent*, because an absent facet
is a question with no answer and therefore an ambiguity the law forbids.

The enumeration is closed on purpose while the *vocabularies inside* facets are
open (:mod:`engine.uckp.vocabulary`). Adding a thirty-fourth facet is a
constitutional amendment — a new question every object in the universe must
suddenly answer — and amendments belong in the law, not in a data file. Adding a
new knowledge kind, authority tier, persistence technology or relationship class
is registration, and registration must never require an amendment.
"""

from __future__ import annotations

from enum import Enum

from engine.uckp.errors import FacetError


class Facet(str, Enum):
    """The universal facets every UCKO carries."""

    IDENTITY = "identity"
    SEMANTIC_IDENTITY = "semantic-identity"
    ONTOLOGY = "ontology"
    TAXONOMY = "taxonomy"
    AUTHORITY = "authority"
    PROVENANCE = "provenance"
    OWNERSHIP = "ownership"
    DEPENDENCIES = "dependencies"
    RELATIONSHIPS = "relationships"
    LIFECYCLE = "lifecycle"
    TEMPORAL_HISTORY = "temporal-history"
    CERTIFICATION = "certification"
    VALIDATION = "validation"
    VERIFICATION = "verification"
    TRACEABILITY = "traceability"
    EVIDENCE = "evidence"
    CONTEXT = "context"
    EVOLUTION_HISTORY = "evolution-history"
    REPLAY = "replay"
    AUDIT = "audit"
    DISCOVERY = "discovery"
    METADATA = "metadata"
    CONSTRAINTS = "constraints"
    POLICIES = "policies"
    RUNTIME_BINDINGS = "runtime-bindings"
    PROJECTION_BINDINGS = "projection-bindings"
    PERSISTENCE_BINDINGS = "persistence-bindings"
    SECURITY_CONTEXT = "security-context"
    GOVERNANCE_CONTEXT = "governance-context"
    COMPLIANCE_CONTEXT = "compliance-context"
    KNOWLEDGE_CONTEXT = "knowledge-context"
    OBSERVER_CONTEXT = "observer-context"
    EXISTENCE_CONTEXT = "existence-context"

    @classmethod
    def coerce(cls, value: object) -> Facet:
        """Return the facet for ``value``, failing loudly on an unknown name."""
        if isinstance(value, cls):
            return value
        text = str(value).strip().lower()
        for member in cls:
            if member.value == text:
                return member
        raise FacetError("unknown universal facet", facet=str(value))

    @property
    def attribute(self) -> str:
        """The UCKO attribute that carries this facet."""
        return self.value.replace("-", "_")

    @property
    def question(self) -> str:
        """The question this facet answers, for human-readable projections."""
        return _FACET_QUESTIONS[self]


#: Every facet is required. The tuple is derived from the enum rather than
#: restated, so a new facet cannot be added and forgotten (Article 3).
REQUIRED_FACETS: tuple[Facet, ...] = tuple(Facet)

#: The UCKO attribute name for each facet, derived — never enumerated.
FACET_ATTRIBUTES: tuple[str, ...] = tuple(facet.attribute for facet in Facet)


_FACET_QUESTIONS: dict[Facet, str] = {
    Facet.IDENTITY: "Which unique, immutable thing is this?",
    Facet.SEMANTIC_IDENTITY: "What does it mean, independent of what it is called?",
    Facet.ONTOLOGY: "What kind of being is it?",
    Facet.TAXONOMY: "Where does it sit in the classification of knowledge?",
    Facet.AUTHORITY: "By what authority does it exist, and from whom is that derived?",
    Facet.PROVENANCE: "Where did it come from, through which hands?",
    Facet.OWNERSHIP: "Who is accountable for it?",
    Facet.DEPENDENCIES: "What must exist for it to exist?",
    Facet.RELATIONSHIPS: "How is it bound to everything else?",
    Facet.LIFECYCLE: "What stage of existence is it in?",
    Facet.TEMPORAL_HISTORY: "What happened to it, in order?",
    Facet.CERTIFICATION: "Who certified it, and to what standard?",
    Facet.VALIDATION: "Was it checked against its declared shape?",
    Facet.VERIFICATION: "Was it checked against reality?",
    Facet.TRACEABILITY: "What upstream intent and downstream effect does it connect?",
    Facet.EVIDENCE: "What proof supports every claim made about it?",
    Facet.CONTEXT: "Under what conditions is it true?",
    Facet.EVOLUTION_HISTORY: "Through which constitutional states has it passed?",
    Facet.REPLAY: "How can it be reproduced exactly?",
    Facet.AUDIT: "Who did what to it, when, and provably?",
    Facet.DISCOVERY: "How is it found without anyone listing it?",
    Facet.METADATA: "What machine-readable description does it publish?",
    Facet.CONSTRAINTS: "What must always hold of it?",
    Facet.POLICIES: "What rules govern its use?",
    Facet.RUNTIME_BINDINGS: "Which execution environments can act on it?",
    Facet.PROJECTION_BINDINGS: "Which views are generated from it?",
    Facet.PERSISTENCE_BINDINGS: "Which storage mechanisms hold copies of it?",
    Facet.SECURITY_CONTEXT: "Who may see and change it?",
    Facet.GOVERNANCE_CONTEXT: "Which governance body decides about it?",
    Facet.COMPLIANCE_CONTEXT: "Which obligations must it satisfy?",
    Facet.KNOWLEDGE_CONTEXT: "Which knowledge universe does it belong to?",
    Facet.OBSERVER_CONTEXT: "From whose vantage point is it described?",
    Facet.EXISTENCE_CONTEXT: "Under what conditions does it exist at all?",
}

if set(_FACET_QUESTIONS) != set(Facet):  # pragma: no cover - construction-time guard
    raise FacetError("every facet must declare the question it answers")


__all__ = ["FACET_ATTRIBUTES", "REQUIRED_FACETS", "Facet"]
