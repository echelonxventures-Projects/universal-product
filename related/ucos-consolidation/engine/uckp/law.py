"""UCKP Layer Zero — the root constitutional law, as executable data.

This module is the single canonical home of the Universal Constitutional Knowledge
Principle. The law is *not* stored in Markdown, JSON, YAML or a schema: Article 11
forbids a generated representation from holding truth, and a law whose only home is
a document is a law that a document edit can silently repeal. It lives here, as
immutable Python values, and every document, JSON declaration, register and
certificate that states the law is generated from these values
(:mod:`engine.uckp.projection`).

Three catalogues are declared, and nothing else in Layer Zero restates them:

    * :data:`UCKP_ARTICLES`   — the twenty articles of the root law.
    * :data:`UCKP_INVARIANTS` — the seventeen constitutional invariants every
      implementation must prove. :mod:`engine.uckp.validation` binds an executable
      probe to each id; it never redeclares the statement.
    * :data:`UCKP_STOP_CONDITIONS` — the thirteen conditions under which the
      constitutional refactoring is complete.

Also declared: the categories of entity that must exist as a UCKO
(:data:`GOVERNED_CATEGORIES`) and the categories that may only ever be a view of
one (:data:`NON_AUTHORITATIVE_CATEGORIES`). Both are open sets — Article 17
requires that an unknown future category be admitted by registration, never by
editing this module.
"""

from __future__ import annotations

from dataclasses import dataclass

from engine.uckp.canonical import content_hash
from engine.uckp.errors import LawViolation

#: The immutable identity of the root constitutional law.
LAW_ID = "UCKP-LAW-0001"

#: The law is versioned so it can be *extended* without any prior state changing.
LAW_VERSION = "1.0.0"

#: The supreme clause. Every article elaborates it; none may contradict it.
SUPREMACY_CLAUSE = (
    "Every constitutional entity shall exist exactly once as a canonical Universal "
    "Constitutional Knowledge Object. Every representation, execution environment and "
    "persistence mechanism of that entity is a view of it and holds no independent "
    "architectural authority. No architectural authority exists outside this principle."
)


@dataclass(frozen=True, slots=True)
class Article:
    """One article of the root constitutional law."""

    article_id: str
    title: str
    clause: str
    enforces: tuple[str, ...] = ()
    binds: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, object]:
        return {
            "article_id": self.article_id,
            "title": self.title,
            "clause": self.clause,
            "enforces": list(self.enforces),
            "binds": list(self.binds),
        }


@dataclass(frozen=True, slots=True)
class Invariant:
    """A constitutional invariant an implementation must *prove*, not assert."""

    invariant_id: str
    name: str
    statement: str
    blocking: bool = True

    def to_dict(self) -> dict[str, object]:
        return {
            "invariant_id": self.invariant_id,
            "name": self.name,
            "statement": self.statement,
            "blocking": self.blocking,
        }


@dataclass(frozen=True, slots=True)
class StopCondition:
    """A condition under which the constitutional refactoring is complete."""

    condition_id: str
    statement: str
    invariants: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, object]:
        return {
            "condition_id": self.condition_id,
            "statement": self.statement,
            "invariants": list(self.invariants),
        }


# --- The seventeen constitutional invariants -----------------------------------
# Declared once here; probed once in engine.uckp.validation. An invariant with a
# declaration and no probe is unmeasured, and an unmeasured blocking invariant
# fails closed rather than reporting satisfied.

UCKP_INVARIANTS: tuple[Invariant, ...] = (
    Invariant(
        "UCKP-INV-01",
        "knowledge-once",
        "No two canonical knowledge objects carry the same semantic identity.",
    ),
    Invariant(
        "UCKP-INV-02",
        "single-authority",
        "Every object's authority derives from exactly one parent and grounds in the root law.",
    ),
    Invariant(
        "UCKP-INV-03",
        "zero-duplication",
        "No identity, content digest or canonical primitive is defined more than once.",
    ),
    Invariant(
        "UCKP-INV-04",
        "zero-ambiguity",
        "Every facet is populated and every relationship target resolves to a real object.",
    ),
    Invariant(
        "UCKP-INV-05",
        "zero-orphans",
        "Every object is reachable from the root law through the knowledge graph.",
    ),
    Invariant(
        "UCKP-INV-06",
        "zero-circular-authority",
        "The authority relation is acyclic, so every chain terminates at the root law.",
    ),
    Invariant(
        "UCKP-INV-07",
        "zero-hardcoded-knowledge",
        "Every object carries provenance naming the declaration it was derived from.",
    ),
    Invariant(
        "UCKP-INV-08",
        "zero-projection-authority",
        "No projection, binding or generated artifact claims authority.",
    ),
    Invariant(
        "UCKP-INV-09",
        "zero-technology-lock-in",
        "Two or more execution technologies satisfy the identical execution contract.",
    ),
    Invariant(
        "UCKP-INV-10",
        "zero-repository-lock-in",
        "The repository appears only as a persistence and projection binding, never as authority.",
    ),
    Invariant(
        "UCKP-INV-11",
        "zero-storage-lock-in",
        "Two or more persistence technologies round-trip the universe byte-identically.",
    ),
    Invariant(
        "UCKP-INV-12",
        "zero-runtime-lock-in",
        "Two or more runtime bindings exist and no object binds to exactly one runtime.",
    ),
    Invariant(
        "UCKP-INV-13",
        "infinite-evolvability",
        "The evolution cycle is append-only and has no terminal stage.",
    ),
    Invariant(
        "UCKP-INV-14",
        "infinite-extensibility",
        "Every vocabulary, adapter set and relationship class admits an unknown future member.",
    ),
    Invariant(
        "UCKP-INV-15",
        "infinite-replayability",
        "Every constitutional state carries a replay proof and the timeline replays identically.",
    ),
    Invariant(
        "UCKP-INV-16",
        "infinite-discoverability",
        "Every object self-describes and is found without manual enumeration.",
    ),
    Invariant(
        "UCKP-INV-17",
        "infinite-auditability",
        "Every object and every state transition carries a complete audit trail.",
    ),
)


# --- The twenty articles of the root law ---------------------------------------

UCKP_ARTICLES: tuple[Article, ...] = (
    Article(
        "UCKP-ART-01",
        "Supremacy",
        SUPREMACY_CLAUSE,
        enforces=("UCKP-INV-02",),
        binds=("constitution", "authority"),
    ),
    Article(
        "UCKP-ART-02",
        "Canonical Existence",
        "Every governed category of entity shall exist exactly once as a canonical "
        "Universal Constitutional Knowledge Object. Nothing exists constitutionally "
        "until it has become one.",
        enforces=("UCKP-INV-01", "UCKP-INV-03"),
        binds=("knowledge", "identity"),
    ),
    Article(
        "UCKP-ART-03",
        "Zero Duplication",
        "The same knowledge shall not be authored twice, under one identity or two. "
        "A second definition of an existing primitive is a competing authority and is void.",
        enforces=("UCKP-INV-01", "UCKP-INV-03"),
        binds=("knowledge",),
    ),
    Article(
        "UCKP-ART-04",
        "Non-Authority of Representations",
        "Repositories, documents, files, schemas, source code, APIs, databases, graphs, "
        "interfaces and every future technology are views, projections, execution "
        "environments or persistence mechanisms. None holds independent authority.",
        enforces=("UCKP-INV-08", "UCKP-INV-10"),
        binds=("projection", "persistence", "execution"),
    ),
    Article(
        "UCKP-ART-05",
        "Universal Identity",
        "Every object receives a globally unique, immutable, canonical, persistent "
        "identity that is independent of technology, storage, repository and time. "
        "An identity, once minted, never changes.",
        enforces=("UCKP-INV-03",),
        binds=("identity",),
    ),
    Article(
        "UCKP-ART-06",
        "Facet Completeness",
        "Every object shall carry every universal facet. A facet may be unattested, "
        "but it may never be absent, because an absent facet is an unanswerable question.",
        enforces=("UCKP-INV-04",),
        binds=("knowledge", "metadata"),
    ),
    Article(
        "UCKP-ART-07",
        "Universal Knowledge Graph",
        "Every object is a node, every dependency an edge, and every relationship is "
        "executable: a relationship that cannot be resolved is not a relationship.",
        enforces=("UCKP-INV-04", "UCKP-INV-05", "UCKP-INV-06"),
        binds=("relationship", "dependency"),
    ),
    Article(
        "UCKP-ART-08",
        "Automatic Discovery",
        "Nothing shall require manual enumeration. Everything self-registers, "
        "self-describes, self-discovers and exposes machine-readable metadata.",
        enforces=("UCKP-INV-16", "UCKP-INV-07"),
        binds=("registry", "discovery"),
    ),
    Article(
        "UCKP-ART-09",
        "Persistence Abstraction",
        "Every persistence mechanism satisfies one identical constitutional contract. "
        "Replacing persistence requires zero constitutional change.",
        enforces=("UCKP-INV-11", "UCKP-INV-10"),
        binds=("persistence",),
    ),
    Article(
        "UCKP-ART-10",
        "Execution Abstraction",
        "Every execution technology satisfies one identical constitutional contract. "
        "Execution never owns knowledge.",
        enforces=("UCKP-INV-09", "UCKP-INV-12"),
        binds=("execution", "runtime"),
    ),
    Article(
        "UCKP-ART-11",
        "Document Abstraction",
        "Documents are generated views. Markdown, JSON, YAML and schemas are not "
        "authority. Generated output never owns truth; truth originates in an object.",
        enforces=("UCKP-INV-08",),
        binds=("projection", "artifact"),
    ),
    Article(
        "UCKP-ART-12",
        "Immutable Constitutional State",
        "Every transition creates a new state that references its parent and its "
        "knowledge, evidence, authority, capability and certification deltas. "
        "No previous state ever changes.",
        enforces=("UCKP-INV-15", "UCKP-INV-17"),
        binds=("state", "transition", "timeline"),
    ),
    Article(
        "UCKP-ART-13",
        "Determinism and Canonical Form",
        "Every digest, identity, proof and decision is computed through one canonical "
        "form, so identical inputs always produce identical bytes.",
        enforces=("UCKP-INV-03", "UCKP-INV-15"),
        binds=("proof", "measurement"),
    ),
    Article(
        "UCKP-ART-14",
        "Append-Only Evolution",
        "Evolution observes, learns, reasons, simulates, analyses, resolves, implements, "
        "validates, verifies, replays, certifies, transitions and assimilates, forever. "
        "It appends; it never rewrites; it never terminates.",
        enforces=("UCKP-INV-13",),
        binds=("evolution", "event"),
    ),
    Article(
        "UCKP-ART-15",
        "Universal Intelligence",
        "Knowledge reasons about itself. No conclusion rests on a hardcoded assumption; "
        "every finding is derived from the declared universe.",
        enforces=("UCKP-INV-07",),
        binds=("knowledge", "observation"),
    ),
    Article(
        "UCKP-ART-16",
        "Executable Governance",
        "Every governance decision is discoverable, replayable, deterministic, auditable, "
        "traceable, machine-verifiable and human-understandable.",
        enforces=("UCKP-INV-17", "UCKP-INV-15"),
        binds=("governance", "decision", "policy"),
    ),
    Article(
        "UCKP-ART-17",
        "Universal Compatibility",
        "Every future capability, engine, registry, intelligence, runtime, repository and "
        "technology integrates by implementing the object contracts. There are no exceptions, "
        "and an unknown future category is admitted by registration, never by amendment.",
        enforces=("UCKP-INV-14",),
        binds=("capability", "contract"),
    ),
    Article(
        "UCKP-ART-18",
        "Reuse Before Create",
        "Before anything is created its canonical object shall be located. If it exists it "
        "is reused, extended or referenced. It is never duplicated and never given a rival.",
        enforces=("UCKP-INV-01", "UCKP-INV-03"),
        binds=("knowledge", "capability"),
    ),
    Article(
        "UCKP-ART-19",
        "Lossless Assimilation",
        "Existing artifacts are mapped into objects with no loss of information, authority, "
        "replay, certification, identity or provenance. Assimilation is invertible.",
        enforces=("UCKP-INV-07", "UCKP-INV-17"),
        binds=("artifact", "provenance"),
    ),
    Article(
        "UCKP-ART-20",
        "Perpetual Validity",
        "This law is technology-, repository-, storage-, runtime- and implementation-agnostic, "
        "and remains valid across future languages, storage media, execution models, "
        "intelligences, planetary locations and civilizations.",
        enforces=("UCKP-INV-09", "UCKP-INV-11", "UCKP-INV-14"),
        binds=("constitution",),
    ),
)


# --- The thirteen stop conditions ----------------------------------------------

UCKP_STOP_CONDITIONS: tuple[StopCondition, ...] = (
    StopCondition(
        "UCKP-STOP-01",
        "Every constitutional entity exists exactly once.",
        ("UCKP-INV-01", "UCKP-INV-03"),
    ),
    StopCondition(
        "UCKP-STOP-02",
        "Every authoritative concept exists exactly once.",
        ("UCKP-INV-01", "UCKP-INV-02"),
    ),
    StopCondition(
        "UCKP-STOP-03",
        "Every artifact is derived from canonical knowledge.",
        ("UCKP-INV-07", "UCKP-INV-08"),
    ),
    StopCondition("UCKP-STOP-04", "Every projection is generated.", ("UCKP-INV-08",)),
    StopCondition(
        "UCKP-STOP-05",
        "Every persistence implementation is interchangeable.",
        ("UCKP-INV-11",),
    ),
    StopCondition(
        "UCKP-STOP-06",
        "Every execution implementation is interchangeable.",
        ("UCKP-INV-09",),
    ),
    StopCondition("UCKP-STOP-07", "Every repository is replaceable.", ("UCKP-INV-10",)),
    StopCondition("UCKP-STOP-08", "Every document is replaceable.", ("UCKP-INV-08",)),
    StopCondition(
        "UCKP-STOP-09",
        "Every technology is replaceable.",
        ("UCKP-INV-09", "UCKP-INV-11", "UCKP-INV-12"),
    ),
    StopCondition("UCKP-STOP-10", "Every constitutional state is immutable.", ("UCKP-INV-15",)),
    StopCondition("UCKP-STOP-11", "Every transition is deterministic.", ("UCKP-INV-15",)),
    StopCondition(
        "UCKP-STOP-12",
        "Every capability derives from a canonical knowledge object.",
        ("UCKP-INV-02", "UCKP-INV-05"),
    ),
    StopCondition(
        "UCKP-STOP-13",
        "Every future evolution preserves backward replay, provenance, certification "
        "and constitutional authority.",
        ("UCKP-INV-13", "UCKP-INV-15", "UCKP-INV-17"),
    ),
)


#: Categories of entity that shall exist as a UCKO (Article 2). Open by Article 17:
#: an unknown future category is admitted through
#: :meth:`engine.uckp.vocabulary.VocabularyRegistry.extend`, not by editing this tuple.
GOVERNED_CATEGORIES: tuple[str, ...] = (
    "artifact",
    "authority",
    "axiom",
    "capability",
    "certification",
    "concept",
    "constraint",
    "decision",
    "dependency",
    "engine",
    "event",
    "evidence",
    "governance",
    "identity",
    "knowledge",
    "law",
    "measurement",
    "metadata",
    "observation",
    "ontology",
    "policy",
    "principle",
    "proof",
    "registry",
    "relationship",
    "responsibility",
    "runtime",
    "simulation",
    "state",
    "taxonomy",
    "timeline",
    "transition",
    "validation",
    "verification",
    "workflow",
)


#: Categories that may only ever be a view of a UCKO (Article 4). Also open:
#: "every future technology" is the operative clause, so this tuple names the
#: present members and the law binds the unnamed ones by category, not by list.
NON_AUTHORITATIVE_CATEGORIES: tuple[str, ...] = (
    "ai-system",
    "api",
    "cloud-platform",
    "database",
    "distributed-system",
    "document",
    "execution-engine",
    "file",
    "folder",
    "graph-database",
    "interplanetary-infrastructure",
    "json",
    "knowledge-graph",
    "markdown",
    "network-protocol",
    "object-storage",
    "operating-system",
    "planetary-infrastructure",
    "programming-language",
    "repository",
    "schema",
    "source-code",
    "storage-system",
    "user-interface",
    "yaml",
)


@dataclass(frozen=True, slots=True)
class RootLaw:
    """The root constitutional law: articles, invariants and stop conditions."""

    law_id: str
    version: str
    supremacy: str
    articles: tuple[Article, ...]
    invariants: tuple[Invariant, ...]
    stop_conditions: tuple[StopCondition, ...]
    governed_categories: tuple[str, ...]
    non_authoritative_categories: tuple[str, ...]

    def article(self, article_id: str) -> Article:
        for item in self.articles:
            if item.article_id == article_id:
                return item
        raise LawViolation("no such article", article_id=article_id)

    def invariant(self, invariant_id: str) -> Invariant:
        for item in self.invariants:
            if item.invariant_id == invariant_id:
                return item
        raise LawViolation("no such invariant", invariant_id=invariant_id)

    def invariant_ids(self) -> tuple[str, ...]:
        return tuple(item.invariant_id for item in self.invariants)

    def article_ids(self) -> tuple[str, ...]:
        return tuple(item.article_id for item in self.articles)

    def articles_enforcing(self, invariant_id: str) -> tuple[Article, ...]:
        return tuple(a for a in self.articles if invariant_id in a.enforces)

    def governs(self, category: str) -> bool:
        """True iff ``category`` must exist as a UCKO."""
        return str(category).strip().lower() in self.governed_categories

    def is_non_authoritative(self, category: str) -> bool:
        """True iff ``category`` may only ever be a view of a UCKO."""
        return str(category).strip().lower() in self.non_authoritative_categories

    def require_coherent(self) -> None:
        """Fail closed unless the law is internally coherent.

        Every enforcement reference resolves, no article or invariant identity is
        declared twice, and no invariant is orphaned from every article — a law
        clause nothing enforces is decoration, and an invariant no clause demands
        has no constitutional basis.
        """
        seen_articles: set[str] = set()
        for article in self.articles:
            if article.article_id in seen_articles:
                raise LawViolation("article declared twice", article_id=article.article_id)
            seen_articles.add(article.article_id)
        declared = set(self.invariant_ids())
        if len(declared) != len(self.invariants):
            raise LawViolation("invariant declared twice", law_id=self.law_id)
        for article in self.articles:
            for invariant_id in article.enforces:
                if invariant_id not in declared:
                    raise LawViolation(
                        "article enforces an undeclared invariant",
                        article_id=article.article_id,
                        invariant_id=invariant_id,
                    )
        enforced = {i for a in self.articles for i in a.enforces}
        orphaned = sorted(declared - enforced)
        if orphaned:
            raise LawViolation("invariant enforced by no article", invariants=orphaned)
        for condition in self.stop_conditions:
            for invariant_id in condition.invariants:
                if invariant_id not in declared:
                    raise LawViolation(
                        "stop condition names an undeclared invariant",
                        condition_id=condition.condition_id,
                        invariant_id=invariant_id,
                    )

    def to_dict(self) -> dict[str, object]:
        return {
            "law_id": self.law_id,
            "version": self.version,
            "supremacy": self.supremacy,
            "articles": [a.to_dict() for a in self.articles],
            "invariants": [i.to_dict() for i in self.invariants],
            "stop_conditions": [s.to_dict() for s in self.stop_conditions],
            "governed_categories": list(self.governed_categories),
            "non_authoritative_categories": list(self.non_authoritative_categories),
        }

    def digest(self) -> str:
        """The content digest of the law — the seal every derived artifact cites."""
        return content_hash(self.to_dict())


#: The root constitutional law of the UCOS Ω∞ Constitutional Knowledge Universe.
ROOT_LAW = RootLaw(
    law_id=LAW_ID,
    version=LAW_VERSION,
    supremacy=SUPREMACY_CLAUSE,
    articles=UCKP_ARTICLES,
    invariants=UCKP_INVARIANTS,
    stop_conditions=UCKP_STOP_CONDITIONS,
    governed_categories=GOVERNED_CATEGORIES,
    non_authoritative_categories=NON_AUTHORITATIVE_CATEGORIES,
)

ROOT_LAW.require_coherent()


__all__ = [
    "GOVERNED_CATEGORIES",
    "LAW_ID",
    "LAW_VERSION",
    "NON_AUTHORITATIVE_CATEGORIES",
    "ROOT_LAW",
    "SUPREMACY_CLAUSE",
    "UCKP_ARTICLES",
    "UCKP_INVARIANTS",
    "UCKP_STOP_CONDITIONS",
    "Article",
    "Invariant",
    "RootLaw",
    "StopCondition",
]
