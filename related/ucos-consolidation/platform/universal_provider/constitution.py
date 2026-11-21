"""UPA-000002 — The Provider Constitution (Terminal-04).

The Provider Constitution is the **single, provider-agnostic law** that every
provider — Repository, Documentation, Architecture, Research, Journal, Patent,
Standards, Government, Security, AI, Runtime, Marketplace, Customer, Financial, and
every provider not yet imagined — obeys without exception.

Three properties make the constitution universal:

    * **One interface.** :data:`CONSTITUTIONAL_OPERATIONS` enumerates the complete
      operation surface. A provider implements exactly these six operations; it may
      not add a seventh and may not omit one. There is therefore no
      provider-specific interface anywhere in the architecture (PC-01).
    * **Open vocabulary.** The constitution never enumerates provider *kinds*. A
      kind is a validated string supplied as **data** by the provider's descriptor
      (PC-02), so onboarding a new provider class requires no change to this module
      and no change to any framework module (PC-14).
    * **Executable law.** Every article declares the validation gate that proves
      it (:attr:`ProviderArticle.gate`). The constitution is not prose the code
      hopes to honour; :mod:`platform.universal_provider.validation` executes one
      gate per article and certification consumes the result (PC-11).

This module is pure data plus validation helpers. It holds no runtime state, no
wall-clock, and no provider references, and it is content-addressed so a corpus can
prove *which* constitution a provider was certified against.
"""

from __future__ import annotations

import re
from collections.abc import Iterable
from dataclasses import dataclass
from enum import Enum
from platform.universal_provider.errors import ProviderConstitutionError
from typing import Any

#: Semantic version of the Provider Constitution itself.
PROVIDER_CONSTITUTION_VERSION = "1.0.0"

#: Stable identity of the constitution (referenced by every certificate).
PROVIDER_CONSTITUTION_ID = "UCOS-PROVIDER-CONSTITUTION"

#: The one constitutional interface every provider implements (PC-01).
PROVIDER_INTERFACE = "ucos.provider.universal"

#: Semantic version of the constitutional interface surface (AR-03 / PL-05).
PROVIDER_INTERFACE_VERSION = "1.0.0"

#: The mission that owns the Provider Framework.
PROVIDER_FRAMEWORK_OWNER = "TERMINAL-04"


class ProviderOperation(str, Enum):
    """The complete constitutional operation surface (PC-01).

    Six operations span every provider concern that has ever been asked of a
    provider, at a level of abstraction that is deliberately free of any domain:

        * ``DESCRIBE`` — return the provider's own descriptor (self-description).
          Identity, kind, version, capabilities, dependencies, declared effects.
        * ``CAPABILITIES`` — return the declared capability set. Nothing undeclared
          may be invoked (PC-04), so this is the provider's own authority surface.
        * ``HEALTH`` — return a structural health report. Serviceability is
          observable without invoking a domain operation.
        * ``QUERY`` — the single universal *read many* operation. A selector in,
          zero-or-more resources out. Whether the substrate is a git repository, a
          patent office, a journal index, a market feed, or a ledger is a detail of
          the provider, never of the interface.
        * ``FETCH`` — the single universal *read one* operation. A resource
          identity in, exactly one resource out, or a fail-closed error.
        * ``VERIFY`` — return an attestation over a resource: content hash plus
          provenance chain. This is what makes provider output admissible as
          evidence rather than as hearsay (PC-06).

    ``QUERY``/``FETCH``/``VERIFY`` are read-only by construction. A provider that
    needs to *effect* something declares it as a capability with non-empty
    ``effects``; the framework surfaces the declaration and refuses undeclared
    effects (PC-08). Mutation therefore never widens the interface.
    """

    DESCRIBE = "describe"
    CAPABILITIES = "capabilities"
    HEALTH = "health"
    QUERY = "query"
    FETCH = "fetch"
    VERIFY = "verify"


#: The frozen constitutional operation surface, in canonical order.
CONSTITUTIONAL_OPERATIONS: tuple[ProviderOperation, ...] = (
    ProviderOperation.DESCRIBE,
    ProviderOperation.CAPABILITIES,
    ProviderOperation.HEALTH,
    ProviderOperation.QUERY,
    ProviderOperation.FETCH,
    ProviderOperation.VERIFY,
)


#: **Intrinsic** operations — guaranteed by the framework for every provider and
#: therefore requiring no capability declaration. They are pure self-description and
#: touch no source of record.
INTRINSIC_OPERATIONS: tuple[ProviderOperation, ...] = (
    ProviderOperation.DESCRIBE,
    ProviderOperation.CAPABILITIES,
    ProviderOperation.HEALTH,
)

#: **Substrate** operations — they reach the provider's source of record and so must
#: each be backed by at least one declared capability (PC-04). This is the boundary
#: at which "nothing undeclared may be invoked" becomes enforceable.
SUBSTRATE_OPERATIONS: tuple[ProviderOperation, ...] = (
    ProviderOperation.QUERY,
    ProviderOperation.FETCH,
    ProviderOperation.VERIFY,
)


@dataclass(frozen=True, slots=True)
class ProviderArticle:
    """One article of the Provider Constitution.

    Immutable, serializable, and bound to the executable gate that proves it, so
    the constitution and the validator can never drift apart.
    """

    article_id: str
    title: str
    mandate: str
    gate: str
    waivable: bool = False

    def __post_init__(self) -> None:
        for field_name in ("article_id", "title", "mandate", "gate"):
            value = getattr(self, field_name)
            if not isinstance(value, str) or not value.strip():
                raise ProviderConstitutionError(
                    f"constitutional article field {field_name!r} is required",
                    {"article_id": self.article_id},
                )

    def to_dict(self) -> dict[str, Any]:
        return {
            "article_id": self.article_id,
            "title": self.title,
            "mandate": self.mandate,
            "gate": self.gate,
            "waivable": self.waivable,
        }


#: The Provider Constitution — fourteen articles, each with an executable gate.
PROVIDER_ARTICLES: tuple[ProviderArticle, ...] = (
    ProviderArticle(
        article_id="PC-01",
        title="One Constitutional Interface",
        mandate=(
            "Every provider implements exactly the operation surface named by "
            "CONSTITUTIONAL_OPERATIONS — no provider-specific interface, no extra "
            "operation, no omitted operation. Consumers bind to the interface, never "
            "to a provider."
        ),
        gate="PV-01-INTERFACE-COMPLETE",
    ),
    ProviderArticle(
        article_id="PC-02",
        title="Open Kind Vocabulary",
        mandate=(
            "Provider kinds are data, never code. No framework module may enumerate, "
            "branch on, or special-case a provider kind or provider identity."
        ),
        gate="PV-02-KIND-OPEN",
    ),
    ProviderArticle(
        article_id="PC-03",
        title="Declared Identity",
        mandate=(
            "A provider declares a stable identity: slug id, open kind, semantic "
            "version, and authority. Its descriptor is content-addressed, so identity "
            "plus content hash pins exactly what was certified."
        ),
        gate="PV-03-IDENTITY-DECLARED",
    ),
    ProviderArticle(
        article_id="PC-04",
        title="Capability Declaration",
        mandate=(
            "Nothing undeclared may be invoked. Every capability declares its "
            "operation, selector keys, resource kind, determinism, and effects; an "
            "undeclared capability invocation is refused."
        ),
        gate="PV-04-CAPABILITIES-DECLARED",
    ),
    ProviderArticle(
        article_id="PC-05",
        title="Determinism",
        mandate=(
            "A capability declared deterministic returns byte-identical results for "
            "identical inputs over an identical substrate. Non-deterministic "
            "capabilities must declare themselves so, and are excluded from "
            "reproducibility gates rather than silently corrupting them."
        ),
        gate="PV-05-DETERMINISM-DECLARED",
    ),
    ProviderArticle(
        article_id="PC-06",
        title="Provenance",
        mandate=(
            "Every resource a provider returns carries a source-of-record provenance "
            "and a content hash over its payload. Provider output is admissible as "
            "evidence or it is not returned."
        ),
        gate="PV-06-PROVENANCE-COMPLETE",
    ),
    ProviderArticle(
        article_id="PC-07",
        title="Fail Closed",
        mandate=(
            "Absent, unknown, malformed, or unauthorized input is refused with a typed "
            "error. Absence of evidence is never evidence of correctness, and no "
            "operation may substitute a silent default for a refusal."
        ),
        gate="PV-07-FAIL-CLOSED",
    ),
    ProviderArticle(
        article_id="PC-08",
        title="No Ambient Authority",
        mandate=(
            "A provider reaches nothing it has not declared. Every external surface — "
            "filesystem, network, process, credential — is declared as a capability "
            "effect and is refused if undeclared."
        ),
        gate="PV-08-EFFECTS-DECLARED",
    ),
    ProviderArticle(
        article_id="PC-09",
        title="Isolation",
        mandate=(
            "A provider failure degrades that provider's scope only. The framework, "
            "the registry, and sibling providers survive any provider fault; faults "
            "surface as typed errors and as health degradation, never as a crash."
        ),
        gate="PV-09-FAULT-ISOLATED",
    ),
    ProviderArticle(
        article_id="PC-10",
        title="Lifecycle Governance",
        mandate=(
            "Provider state changes only through the lifecycle engine, only along a "
            "declared transition, and only with an appended, hash-chained ledger "
            "entry. There is no back door to provider state."
        ),
        gate="PV-10-LIFECYCLE-GOVERNED",
    ),
    ProviderArticle(
        article_id="PC-11",
        title="Certification Before Activation",
        mandate=(
            "No provider serves a consumer before certification, and certification "
            "attests only what validation substantiates. An uncertified provider may "
            "be registered and discoverable, never active."
        ),
        gate="PV-11-CERTIFIABLE",
    ),
    ProviderArticle(
        article_id="PC-12",
        title="Composability",
        mandate=(
            "Every provider composes with every other by reference. A composition is "
            "itself a provider satisfying the same constitutional interface, so "
            "composition is closed and unbounded in depth."
        ),
        gate="PV-12-COMPOSABLE",
    ),
    ProviderArticle(
        article_id="PC-13",
        title="Additive Evolution",
        mandate=(
            "Within a major version a provider evolves additively: capabilities may be "
            "added, never removed or narrowed. Breaking change requires a new major "
            "version and a new registration, never a mutation of a certified record."
        ),
        gate="PV-13-ADDITIVE",
    ),
    ProviderArticle(
        article_id="PC-14",
        title="Infinite Extensibility",
        mandate=(
            "Onboarding a provider is registration plus a descriptor plus an entry "
            "point — never a framework change. If a new provider class requires "
            "editing any framework module, the architecture has failed this article."
        ),
        gate="PV-14-EXTENSIBLE",
    ),
)

#: Article index for O(1) lookup by id.
_ARTICLE_INDEX: dict[str, ProviderArticle] = {a.article_id: a for a in PROVIDER_ARTICLES}

#: The gate id declared by each article, in canonical article order.
CONSTITUTIONAL_GATES: tuple[str, ...] = tuple(a.gate for a in PROVIDER_ARTICLES)

#: A provider kind is an open, lowercase, dot/dash-separated slug. The pattern
#: constrains *form* only — never membership — which is what keeps the vocabulary
#: open (PC-02).
_KIND_PATTERN = re.compile(r"^[a-z][a-z0-9]*([.-][a-z0-9]+)*$")

#: A provider id follows the same slug discipline as a kind (PC-03).
_PROVIDER_ID_PATTERN = _KIND_PATTERN

#: Semantic version pattern (major.minor.patch, no pre-release games).
_VERSION_PATTERN = re.compile(r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$")


def article(article_id: str) -> ProviderArticle:
    """Return the article with ``article_id`` or fail closed (PC-07)."""
    found = _ARTICLE_INDEX.get(article_id)
    if found is None:
        raise ProviderConstitutionError(
            f"unknown constitutional article {article_id!r}",
            {"known": sorted(_ARTICLE_INDEX)},
        )
    return found


def normalize_kind(kind: str) -> str:
    """Validate and normalize an **open** provider kind (PC-02).

    The framework asserts *form*, never *membership*: ``repository``,
    ``documentation``, ``patent``, ``marketplace`` and a kind invented years from
    now are all equally valid here, and none of them appears anywhere in the
    framework's control flow.
    """
    if not isinstance(kind, str):
        raise ProviderConstitutionError("provider kind must be a string", {"kind": repr(kind)})
    normalized = kind.strip().lower()
    if not _KIND_PATTERN.match(normalized):
        raise ProviderConstitutionError(
            "provider kind must be a lowercase dot/dash-separated slug",
            {"kind": kind},
        )
    return normalized


def normalize_provider_id(provider_id: str) -> str:
    """Validate and normalize a provider id (PC-03)."""
    if not isinstance(provider_id, str):
        raise ProviderConstitutionError(
            "provider id must be a string", {"provider_id": repr(provider_id)}
        )
    normalized = provider_id.strip().lower()
    if not _PROVIDER_ID_PATTERN.match(normalized):
        raise ProviderConstitutionError(
            "provider id must be a lowercase dot/dash-separated slug",
            {"provider_id": provider_id},
        )
    return normalized


def require_semver(version: str, *, field_name: str = "version") -> str:
    """Return ``version`` if it is a strict ``major.minor.patch`` semver (PC-13)."""
    if not isinstance(version, str) or not _VERSION_PATTERN.match(version):
        raise ProviderConstitutionError(
            f"{field_name} must be a semantic version 'major.minor.patch'",
            {field_name: repr(version)},
        )
    return version


def version_tuple(version: str) -> tuple[int, int, int]:
    """Return the comparable integer triple for a validated semver string."""
    major, minor, patch = require_semver(version).split(".")
    return (int(major), int(minor), int(patch))


def require_operations(operations: Iterable[str]) -> tuple[ProviderOperation, ...]:
    """Return the constitutional operation surface, refusing drift (PC-01).

    ``operations`` must be exactly the six constitutional operations: a missing
    operation means the provider is not a provider, and an extra operation means a
    provider-specific interface has leaked into the architecture. Both are refused.
    """
    declared = {str(op) for op in operations}
    expected = {op.value for op in CONSTITUTIONAL_OPERATIONS}
    missing = sorted(expected - declared)
    extra = sorted(declared - expected)
    if missing or extra:
        raise ProviderConstitutionError(
            "provider operation surface deviates from the constitutional interface",
            {"missing": missing, "extra": extra, "expected": sorted(expected)},
        )
    return CONSTITUTIONAL_OPERATIONS


@dataclass(frozen=True, slots=True)
class ProviderConstitution:
    """The immutable, content-addressed Provider Constitution.

    A certificate references the constitution by ``constitution_id`` **and**
    content hash, so a provider certified today can be proven to have been
    certified against exactly this law even after the law is versioned.
    """

    constitution_id: str = PROVIDER_CONSTITUTION_ID
    version: str = PROVIDER_CONSTITUTION_VERSION
    interface: str = PROVIDER_INTERFACE
    interface_version: str = PROVIDER_INTERFACE_VERSION
    owner: str = PROVIDER_FRAMEWORK_OWNER
    articles: tuple[ProviderArticle, ...] = PROVIDER_ARTICLES
    operations: tuple[ProviderOperation, ...] = CONSTITUTIONAL_OPERATIONS

    def article_ids(self) -> tuple[str, ...]:
        return tuple(a.article_id for a in self.articles)

    def gates(self) -> tuple[str, ...]:
        return tuple(a.gate for a in self.articles)

    def to_dict(self) -> dict[str, Any]:
        return {
            "constitution_id": self.constitution_id,
            "version": self.version,
            "interface": self.interface,
            "interface_version": self.interface_version,
            "owner": self.owner,
            "operations": [op.value for op in self.operations],
            "articles": [a.to_dict() for a in self.articles],
        }


def provider_constitution() -> ProviderConstitution:
    """Return the canonical Provider Constitution."""
    return ProviderConstitution()


__all__ = [
    "PROVIDER_CONSTITUTION_ID",
    "PROVIDER_CONSTITUTION_VERSION",
    "PROVIDER_INTERFACE",
    "PROVIDER_INTERFACE_VERSION",
    "PROVIDER_FRAMEWORK_OWNER",
    "PROVIDER_ARTICLES",
    "CONSTITUTIONAL_OPERATIONS",
    "CONSTITUTIONAL_GATES",
    "INTRINSIC_OPERATIONS",
    "SUBSTRATE_OPERATIONS",
    "ProviderArticle",
    "ProviderConstitution",
    "ProviderOperation",
    "article",
    "normalize_kind",
    "normalize_provider_id",
    "provider_constitution",
    "require_operations",
    "require_semver",
    "version_tuple",
]
