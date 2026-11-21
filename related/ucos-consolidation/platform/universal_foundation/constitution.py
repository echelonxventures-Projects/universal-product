"""UCOS-UFC-001 — The Universal Foundation Constitution.

The **single law** every Foundation capability obeys. Not one Foundation capability governs
itself, and no capability is governed by a second constitution: there is exactly one law, it
names exactly thirteen governed domains, and every article of it is bound to an **executable
gate** so the law cannot drift away from what is actually enforced.

Why this module is law rather than prose
----------------------------------------
Three properties, deliberately mirrored from the certified Provider Constitution
(:mod:`platform.universal_provider.constitution`) so the Foundation inherits a *proven*
constitutional shape instead of inventing a rival one:

    * **One law.** :data:`FOUNDATION_ARTICLES` is the complete article set. A Foundation
      capability conforms to all of it or is not a Foundation capability. There is no
      per-capability constitution anywhere in the platform (UFC-09).
    * **Zero enumeration.** This module names **no capability**, **no module path** and **no
      project literal**. The population it governs is supplied as *data* by the capability
      register (``catalog/foundation-capabilities.json``), which is why adding a Foundation
      capability never edits this file (UFC-09, UFC-13).
    * **Executable law.** Every article declares the gate that proves it
      (:attr:`FoundationArticle.gate`). :mod:`platform.universal_foundation.conformance`
      executes one probe per gate per capability, and
      :mod:`platform.universal_foundation.freeze` consumes the result (UFC-11).

Relationship to the Provider Constitution
-----------------------------------------
The Provider Constitution is **not** superseded and **not** duplicated. It is the law of one
governed domain — :attr:`ConstitutionalDomain.PROVIDERS` — and it is itself a Foundation
capability that UFC-03 governs. The Foundation Constitution governs *capabilities*; the
Provider Constitution governs *providers*. Neither restates the other, so there is no
competing constitutional definition (UFC-15).

Determinism
-----------
Pure data plus validation helpers. No runtime state, no wall-clock, no filesystem, no
capability references. Content-addressed, so a certificate can pin exactly which law a
capability was certified against even after the law is versioned.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from enum import Enum
from platform.foundation.contracts import ContractRef, content_hash
from platform.universal_foundation.errors import FoundationConstitutionError
from typing import Any

#: The canonical identity of the Universal Foundation Constitution.
FOUNDATION_CONSTITUTION_ID = "UCOS-UFC-001"

#: The semantic version of the Constitution itself. 1.1.0 amended two articles: UFC-11, so that
#: a capability whose outputs become Repository Truth must be re-measurable at the commit that
#: carries them; and UFC-14, so that duplication is measured by content and not only by
#: declaration. 1.2.0 legislates UFC-17, which holds every registered capability to the
#: completeness of an Ω Nucleus — the production implementation programme's first amendment,
#: and the article that makes "which facets must a capability contain" a measurement rather
#: than a checklist. Every amendment is additive — no article removed, no mandate narrowed, no
#: domain added — so these are minor versions under the same discipline UFC-08 requires of
#: every contract surface.
FOUNDATION_CONSTITUTION_VERSION = "1.2.0"

#: The constitutional authority that owns this law.
FOUNDATION_CONSTITUTION_AUTHORITY = "Universal Foundation Constitutional Authority"


class ConstitutionalDomain(str, Enum):
    """The thirteen domains the Universal Foundation Constitution governs.

    The set is **closed** — a fourteenth domain is a constitutional amendment, not a
    configuration change — while the *population* inside each domain is open and supplied
    as data. That is the exact inversion the platform needs: bounded law, unbounded content.
    """

    CONTRACTS = "contracts"
    SERVICES = "services"
    PROVIDERS = "providers"
    POLICIES = "policies"
    REGISTRIES = "registries"
    RUNTIMES = "runtimes"
    LIFECYCLE = "lifecycle"
    COMPATIBILITY = "compatibility"
    EVOLUTION = "evolution"
    GOVERNANCE = "governance"
    CERTIFICATION = "certification"
    COMPOSITION = "composition"
    SPECIALIZATION = "specialization"

    @classmethod
    def coerce(cls, value: Any, *, context: str = "constitutional domain") -> ConstitutionalDomain:
        """Coerce ``value`` to a domain, failing closed (never silently)."""
        if isinstance(value, cls):
            return value
        if isinstance(value, str):
            try:
                return cls(value)
            except ValueError as exc:
                raise FoundationConstitutionError(
                    "unknown constitutional domain", subject=context, value=value
                ) from exc
        raise FoundationConstitutionError("constitutional domain must be a string", subject=context)


class ArticleScope(str, Enum):
    """Whether an article is proven per capability or once over the whole platform."""

    #: Measured against every registered Foundation capability, individually.
    CAPABILITY = "capability"
    #: Measured once over the composed platform (convergence and integrity laws).
    PLATFORM = "platform"

    @classmethod
    def coerce(cls, value: Any) -> ArticleScope:
        """Coerce ``value`` to a scope, failing closed."""
        if isinstance(value, cls):
            return value
        if isinstance(value, str):
            try:
                return cls(value)
            except ValueError as exc:
                raise FoundationConstitutionError("unknown article scope", value=value) from exc
        raise FoundationConstitutionError("article scope must be a string")


class MaturityAxis(str, Enum):
    """The fourteen axes on which a Foundation capability's maturity is measured.

    Each axis is proven by declared gates (:data:`MATURITY_GATES`) rather than asserted, so
    "mature" is a measurement over executed probes and never a status somebody typed.
    """

    IMPLEMENTED = "implemented"
    INTEGRATED = "integrated"
    REGISTERED = "registered"
    DISCOVERABLE = "discoverable"
    CONFIGURABLE = "configurable"
    COMPOSABLE = "composable"
    EXTENSIBLE = "extensible"
    VALIDATED = "validated"
    VERIFIED = "verified"
    CERTIFIED = "certified"
    DETERMINISTIC = "deterministic"
    REPLAY_SAFE = "replay-safe"
    TRACEABLE = "traceable"
    GOVERNED = "governed"


@dataclass(frozen=True, slots=True)
class FoundationArticle:
    """One article of the Universal Foundation Constitution.

    Immutable, serialisable, and bound to the executable gate that proves it, so the law
    and its enforcement can never drift apart.
    """

    article_id: str
    domain: ConstitutionalDomain
    title: str
    mandate: str
    gate: str
    scope: ArticleScope = ArticleScope.CAPABILITY
    waivable: bool = False

    def __post_init__(self) -> None:
        for field_name in ("article_id", "title", "mandate", "gate"):
            value = getattr(self, field_name)
            if not isinstance(value, str) or not value.strip():
                raise FoundationConstitutionError(
                    f"constitutional article field {field_name!r} is required",
                    article_id=str(self.article_id),
                )
        if not isinstance(self.domain, ConstitutionalDomain):
            raise FoundationConstitutionError(
                "article domain must be a ConstitutionalDomain", article_id=self.article_id
            )
        if not isinstance(self.scope, ArticleScope):
            raise FoundationConstitutionError(
                "article scope must be an ArticleScope", article_id=self.article_id
            )

    @property
    def platform_scoped(self) -> bool:
        """Whether this article is proven once over the platform rather than per capability."""
        return self.scope is ArticleScope.PLATFORM

    def to_dict(self) -> dict[str, Any]:
        """A JSON-serialisable projection of this article."""
        return {
            "article_id": self.article_id,
            "domain": self.domain.value,
            "title": self.title,
            "mandate": self.mandate,
            "gate": self.gate,
            "scope": self.scope.value,
            "waivable": self.waivable,
        }

    def fingerprint(self) -> str:
        """The deterministic content fingerprint of this article."""
        return content_hash(self.to_dict())


#: The Universal Foundation Constitution — seventeen articles over thirteen governed domains,
#: each bound to exactly one executable gate.
FOUNDATION_ARTICLES: tuple[FoundationArticle, ...] = (
    FoundationArticle(
        article_id="UFC-01",
        domain=ConstitutionalDomain.CONTRACTS,
        title="Published Contract Surface",
        mandate=(
            "Every Foundation capability publishes a named, semantically versioned contract "
            "surface. A consumer binds to the contract, never to a module, a function or an "
            "implementation detail. A capability with no published contract is not a "
            "Foundation capability."
        ),
        gate="FG-01-CONTRACT-PUBLISHED",
    ),
    FoundationArticle(
        article_id="UFC-02",
        domain=ConstitutionalDomain.SERVICES,
        title="Resolvable Service",
        mandate=(
            "Every Foundation capability is published as a service descriptor that resolves "
            "from the certified service registry, and every declared dependency resolves with "
            "it. A capability reachable only by importing its module is not integrated."
        ),
        gate="FG-02-SERVICE-REGISTERED",
    ),
    FoundationArticle(
        article_id="UFC-03",
        domain=ConstitutionalDomain.PROVIDERS,
        title="Pluggable Authority",
        mandate=(
            "Wherever a Foundation capability admits a new source of evidence, determination, "
            "validation or recommendation, it admits it through a declared provider extension "
            "point. Adding an authority SHALL NEVER require editing the capability that "
            "consumes it."
        ),
        gate="FG-03-PROVIDER-PLUGGABLE",
    ),
    FoundationArticle(
        article_id="UFC-04",
        domain=ConstitutionalDomain.POLICIES,
        title="Determination by Declared Policy",
        mandate=(
            "Every determination is made by a declared policy read as data. No Foundation "
            "module may carry a project literal, a repository path, a subject identity or a "
            "population count. Behaviour is configured by declaration, never by code."
        ),
        gate="FG-04-POLICY-DECLARED",
    ),
    FoundationArticle(
        article_id="UFC-05",
        domain=ConstitutionalDomain.REGISTRIES,
        title="Deterministic Fail-Closed Registry",
        mandate=(
            "Every Foundation population is held in a registry that orders by declared "
            "precedence and identity — never by insertion — refuses a conflicting "
            "redefinition, and reports an unknown member rather than substituting a default."
        ),
        gate="FG-05-REGISTRY-DETERMINISTIC",
    ),
    FoundationArticle(
        article_id="UFC-06",
        domain=ConstitutionalDomain.RUNTIMES,
        title="One-Command Runtime Surface",
        mandate=(
            "Every Foundation capability is invocable as a runtime in one command, through a "
            "declared entry point. A capability that can only be exercised from a test or an "
            "interactive session is not a runtime and cannot be operated."
        ),
        gate="FG-06-RUNTIME-INVOCABLE",
    ),
    FoundationArticle(
        article_id="UFC-07",
        domain=ConstitutionalDomain.LIFECYCLE,
        title="Explicit Bootstrap",
        mandate=(
            "A Foundation capability comes into existence through a declared bootstrap and "
            "nothing else. Importing a Foundation module SHALL perform no filesystem read, no "
            "network call and no registration side effect."
        ),
        gate="FG-07-LIFECYCLE-BOOTSTRAPPED",
    ),
    FoundationArticle(
        article_id="UFC-08",
        domain=ConstitutionalDomain.COMPATIBILITY,
        title="Additive Compatibility",
        mandate=(
            "Within a major version a Foundation contract surface evolves additively: names "
            "may be added, never removed or narrowed. The version a capability declares and "
            "the version its published contract carries SHALL be the same version."
        ),
        gate="FG-08-COMPATIBILITY-DECLARED",
    ),
    FoundationArticle(
        article_id="UFC-09",
        domain=ConstitutionalDomain.EVOLUTION,
        title="Evolution by Declaration",
        mandate=(
            "A Foundation capability is added by declaration and registration. Neither this "
            "Constitution nor any governing module may enumerate a capability identity, so "
            "the platform grows without a governing module ever being edited."
        ),
        gate="FG-09-EVOLUTION-ADDITIVE",
    ),
    FoundationArticle(
        article_id="UFC-10",
        domain=ConstitutionalDomain.GOVERNANCE,
        title="Fail Closed, Never Infer",
        mandate=(
            "Absent, ambiguous, contested or malformed input is refused with a typed error "
            "carrying a stable code and structured context. Absence of evidence is never "
            "evidence, and no Foundation capability may substitute an inference for a "
            "determination it cannot make."
        ),
        gate="FG-10-FAIL-CLOSED",
    ),
    FoundationArticle(
        article_id="UFC-11",
        domain=ConstitutionalDomain.CERTIFICATION,
        title="Content-Addressed and Replay-Safe",
        mandate=(
            "Every Foundation determination carries a content-addressed identity derived from "
            "its inputs alone, holds no wall-clock, and is byte-identical on replay. "
            "Certification pins the fingerprint, so what was certified is always recoverable. "
            "A capability whose outputs become Repository Truth SHALL declare a replay target "
            "and re-measure at the commit that carries those outputs until the render is a "
            "fixed point. A capability that writes no such output SHALL declare that too: the "
            "declaration is measured against the capability's own source, never trusted."
        ),
        gate="FG-11-CERTIFIABLE",
    ),
    FoundationArticle(
        article_id="UFC-12",
        domain=ConstitutionalDomain.COMPOSITION,
        title="Closed Composition",
        mandate=(
            "Every Foundation capability composes with every other by reference, the "
            "composition graph is acyclic, and a composition is itself a Foundation capability "
            "under this same Constitution. Composition is therefore closed and unbounded."
        ),
        gate="FG-12-COMPOSABLE",
    ),
    FoundationArticle(
        article_id="UFC-13",
        domain=ConstitutionalDomain.SPECIALIZATION,
        title="Specialisation by Declaration",
        mandate=(
            "A project participates in the Foundation by declaring a specialisation document. "
            "Every project-specific fact — zone, path, population, assignment — lives in a "
            "declared document, so a repository-specific fix has nowhere to be written."
        ),
        gate="FG-13-SPECIALIZED-BY-DECLARATION",
    ),
    FoundationArticle(
        article_id="UFC-14",
        domain=ConstitutionalDomain.CONTRACTS,
        title="Exactly Once",
        mandate=(
            "Each constitutional model — Repository Truth, ownership, assimilation, "
            "measurement, dependency and implementation — SHALL have exactly one canonical "
            "implementation holding exactly one contract surface. Two implementations of one "
            "model is a duplicate architecture, not a choice. Within a governed package no two "
            "artifacts SHALL be byte-identical: a copy declares nothing, and therefore competes "
            "for no model and is caught by no declaration, so duplication SHALL be measured by "
            "content and never by declaration alone."
        ),
        gate="FG-14-EXACTLY-ONCE",
        scope=ArticleScope.PLATFORM,
    ),
    FoundationArticle(
        article_id="UFC-15",
        domain=ConstitutionalDomain.GOVERNANCE,
        title="No Parallel Authority",
        mandate=(
            "No subordinate surface may hold a competing constitutional definition. A surface "
            "that once held one either delegates to the canonical owner or is recorded as "
            "superseded. A surface that does neither is a parallel authority and blocks freeze."
        ),
        gate="FG-15-NO-PARALLEL-AUTHORITY",
        scope=ArticleScope.PLATFORM,
    ),
    FoundationArticle(
        article_id="UFC-16",
        domain=ConstitutionalDomain.POLICIES,
        title="One Subject, One Measurement",
        mandate=(
            "One subject population SHALL yield one measurement. Two Foundation surfaces "
            "reporting different numbers for the same population under the same policy is a "
            "constitutional contradiction and SHALL be converged, never reconciled by note."
        ),
        gate="FG-16-ONE-MEASUREMENT",
        scope=ArticleScope.PLATFORM,
    ),
    FoundationArticle(
        article_id="UFC-17",
        domain=ConstitutionalDomain.COMPOSITION,
        title="Nucleus Completeness",
        mandate=(
            "Every registered capability is an Ω Nucleus: the complete constitutional universe "
            "of exactly one canonical concept. Every facet the declared nucleus contract "
            "requires SHALL resolve — to a field of the nucleus's own declaration, to a "
            "constitutional gate it has passed, or to its declared profile. A facet that does "
            "not apply SHALL be declared inapplicable with a reason; an undeclared facet is "
            "incompleteness, because 'nobody wrote it down' and 'it does not apply' are "
            "different facts and only one of them is a determination."
        ),
        gate="FG-17-NUCLEUS-COMPLETE",
        scope=ArticleScope.PLATFORM,
    ),
)

#: Article index for O(1) lookup by identity.
_ARTICLE_INDEX: dict[str, FoundationArticle] = {a.article_id: a for a in FOUNDATION_ARTICLES}

#: The gate identity declared by each article, in canonical article order.
CONSTITUTIONAL_GATES: tuple[str, ...] = tuple(a.gate for a in FOUNDATION_ARTICLES)

#: Gate index → article, so a gate result always resolves back to the law it proves.
_GATE_INDEX: dict[str, FoundationArticle] = {a.gate: a for a in FOUNDATION_ARTICLES}

#: Which gates prove each maturity axis. An axis is reached only when every gate proving it
#: passed, so maturity is a measurement over executed probes rather than a declared status.
MATURITY_GATES: dict[MaturityAxis, tuple[str, ...]] = {
    MaturityAxis.IMPLEMENTED: ("FG-01-CONTRACT-PUBLISHED",),
    MaturityAxis.INTEGRATED: ("FG-02-SERVICE-REGISTERED", "FG-12-COMPOSABLE"),
    MaturityAxis.REGISTERED: ("FG-02-SERVICE-REGISTERED",),
    MaturityAxis.DISCOVERABLE: ("FG-06-RUNTIME-INVOCABLE",),
    MaturityAxis.CONFIGURABLE: ("FG-04-POLICY-DECLARED",),
    MaturityAxis.COMPOSABLE: ("FG-12-COMPOSABLE",),
    MaturityAxis.EXTENSIBLE: ("FG-03-PROVIDER-PLUGGABLE", "FG-09-EVOLUTION-ADDITIVE"),
    MaturityAxis.VALIDATED: ("FG-05-REGISTRY-DETERMINISTIC", "FG-10-FAIL-CLOSED"),
    MaturityAxis.VERIFIED: ("FG-07-LIFECYCLE-BOOTSTRAPPED", "FG-08-COMPATIBILITY-DECLARED"),
    MaturityAxis.CERTIFIED: ("FG-11-CERTIFIABLE",),
    MaturityAxis.DETERMINISTIC: ("FG-11-CERTIFIABLE", "FG-05-REGISTRY-DETERMINISTIC"),
    MaturityAxis.REPLAY_SAFE: ("FG-11-CERTIFIABLE", "FG-07-LIFECYCLE-BOOTSTRAPPED"),
    MaturityAxis.TRACEABLE: ("FG-01-CONTRACT-PUBLISHED", "FG-11-CERTIFIABLE"),
    MaturityAxis.GOVERNED: ("FG-10-FAIL-CLOSED", "FG-13-SPECIALIZED-BY-DECLARATION"),
}


def article(article_id: str) -> FoundationArticle:
    """The article ``article_id``; raises when unknown (fail-closed)."""
    try:
        return _ARTICLE_INDEX[article_id]
    except KeyError as exc:
        raise FoundationConstitutionError(
            "unknown constitutional article", article_id=str(article_id)
        ) from exc


def article_for_gate(gate: str) -> FoundationArticle:
    """The article whose gate is ``gate``; raises when unknown (fail-closed)."""
    try:
        return _GATE_INDEX[gate]
    except KeyError as exc:
        raise FoundationConstitutionError("unknown constitutional gate", gate=str(gate)) from exc


def articles_of_domain(domain: ConstitutionalDomain | str) -> tuple[FoundationArticle, ...]:
    """Every article governing ``domain``, in canonical article order."""
    resolved = ConstitutionalDomain.coerce(domain)
    return tuple(a for a in FOUNDATION_ARTICLES if a.domain is resolved)


def articles_of_scope(scope: ArticleScope | str) -> tuple[FoundationArticle, ...]:
    """Every article of ``scope``, in canonical article order."""
    resolved = ArticleScope.coerce(scope)
    return tuple(a for a in FOUNDATION_ARTICLES if a.scope is resolved)


def maturity_axes() -> tuple[MaturityAxis, ...]:
    """The declared maturity axes, in constitutional order."""
    return tuple(MaturityAxis)


def require_gates(gates: Iterable[str]) -> tuple[str, ...]:
    """Validate that every gate in ``gates`` is declared by an article (fail-closed)."""
    resolved: list[str] = []
    for gate in gates:
        article_for_gate(str(gate))
        resolved.append(str(gate))
    return tuple(resolved)


_CONTRACT_NAMES: tuple[tuple[str, str], ...] = (
    ("foundation.constitution.articles", "The complete article set of the Foundation law."),
    ("foundation.constitution.conform", "Measure a capability against every article."),
    ("foundation.constitution.maturity", "Measure a capability across the maturity axes."),
    ("foundation.constitution.nucleus", "Measure a capability's Ω Nucleus completeness."),
)

#: The versioned published contract surface of the Foundation Constitution.
CONSTITUTION_CONTRACTS: tuple[ContractRef, ...] = tuple(
    ContractRef(name, FOUNDATION_CONSTITUTION_VERSION) for name, _ in _CONTRACT_NAMES
)


def constitution_contract_names() -> tuple[str, ...]:
    """The published Constitution contract names, in declaration order."""
    return tuple(name for name, _ in _CONTRACT_NAMES)


@dataclass(frozen=True, slots=True)
class FoundationConstitution:
    """The immutable, content-addressed Universal Foundation Constitution.

    A conformance determination references the law by ``constitution_id`` **and** content
    hash, so a capability certified today can be proven to have been certified against
    exactly this law even after the law is amended.
    """

    constitution_id: str = FOUNDATION_CONSTITUTION_ID
    version: str = FOUNDATION_CONSTITUTION_VERSION
    authority: str = FOUNDATION_CONSTITUTION_AUTHORITY
    articles: tuple[FoundationArticle, ...] = FOUNDATION_ARTICLES
    domains: tuple[ConstitutionalDomain, ...] = tuple(ConstitutionalDomain)

    def __post_init__(self) -> None:
        governed = {a.domain for a in self.articles}
        missing = [d.value for d in self.domains if d not in governed]
        if missing:
            raise FoundationConstitutionError(
                "constitution declares a domain no article governs", missing=",".join(missing)
            )
        gates = [a.gate for a in self.articles]
        if len(set(gates)) != len(gates):
            raise FoundationConstitutionError("two articles declare the same gate")

    def article_ids(self) -> tuple[str, ...]:
        """Every article identity, in canonical order."""
        return tuple(a.article_id for a in self.articles)

    def gates(self) -> tuple[str, ...]:
        """Every declared gate identity, in canonical article order."""
        return tuple(a.gate for a in self.articles)

    def capability_articles(self) -> tuple[FoundationArticle, ...]:
        """The articles measured against every capability individually."""
        return tuple(a for a in self.articles if a.scope is ArticleScope.CAPABILITY)

    def platform_articles(self) -> tuple[FoundationArticle, ...]:
        """The articles measured once over the composed platform."""
        return tuple(a for a in self.articles if a.scope is ArticleScope.PLATFORM)

    def by_domain(self) -> dict[str, tuple[str, ...]]:
        """Article identities grouped by governed domain, in constitutional order."""
        return {
            domain.value: tuple(a.article_id for a in self.articles if a.domain is domain)
            for domain in self.domains
        }

    def to_dict(self) -> dict[str, Any]:
        """A JSON-serialisable projection of this Constitution."""
        return {
            "constitution_id": self.constitution_id,
            "version": self.version,
            "authority": self.authority,
            "domains": [d.value for d in self.domains],
            "maturity_axes": [axis.value for axis in MaturityAxis],
            "articles": [a.to_dict() for a in self.articles],
            "articles_by_domain": {k: list(v) for k, v in self.by_domain().items()},
            "maturity_gates": {
                axis.value: list(gates) for axis, gates in sorted(MATURITY_GATES.items())
            },
        }

    def fingerprint(self) -> str:
        """The deterministic content fingerprint of this Constitution."""
        return content_hash(self.to_dict())


def foundation_constitution() -> FoundationConstitution:
    """The canonical Universal Foundation Constitution."""
    return FoundationConstitution()


__all__ = [
    "FOUNDATION_CONSTITUTION_ID",
    "FOUNDATION_CONSTITUTION_VERSION",
    "FOUNDATION_CONSTITUTION_AUTHORITY",
    "FOUNDATION_ARTICLES",
    "CONSTITUTIONAL_GATES",
    "CONSTITUTION_CONTRACTS",
    "MATURITY_GATES",
    "ArticleScope",
    "ConstitutionalDomain",
    "FoundationArticle",
    "FoundationConstitution",
    "MaturityAxis",
    "article",
    "article_for_gate",
    "articles_of_domain",
    "articles_of_scope",
    "constitution_contract_names",
    "foundation_constitution",
    "maturity_axes",
    "require_gates",
]
