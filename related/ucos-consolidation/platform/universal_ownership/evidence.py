"""UCOS-UOF-001 — Pluggable ownership evidence providers.

Ownership determination consumes *only* constitutional evidence, and every source of that
evidence is a plug-in. A provider observes what a project has declared — an assignment
catalogue, a definitional locator inside a declared home zone, a registration ledger, a
future authority nobody has written yet — and reports findings. It never decides.

The registry is deterministic by construction: providers are ordered by declared
``(precedence, provider_id)``, never by insertion, and a provider that raises is contained
into :class:`~platform.universal_ownership.errors.OwnershipEvidenceError` rather than
allowed to corrupt a determination.
"""

from __future__ import annotations

import json
import re
from abc import ABC, abstractmethod
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass
from pathlib import Path
from platform.foundation.contracts import content_hash
from platform.universal_ownership.contracts import (
    EvidenceKind,
    OwnershipEvidence,
    OwnershipGranularity,
)
from platform.universal_ownership.errors import (
    OwnershipEvidenceError,
    OwnershipProviderConflictError,
)
from platform.universal_truth.contracts import Subject, locator_segments
from platform.universal_truth.eligibility import CanonicalHomePolicy
from platform.universal_truth.policy import TruthPolicy
from typing import Any

#: The default provider precedence. Higher wins a contest (OWN-REQ-005).
DEFAULT_PRECEDENCE = 100

#: Separators after which a definitional basename may carry a qualifier.
DEFAULT_QUALIFIER_SEPARATORS: tuple[str, ...] = ("-", ".", "_")


def _canonical_home(
    policy: TruthPolicy | CanonicalHomePolicy, *, provider_id: str
) -> CanonicalHomePolicy:
    """Accept either a Truth policy or a composed canonical-home policy (fail-closed).

    A bare :class:`TruthPolicy` is composed with an open eligibility ledger, so a project that
    declares no artifact requirement is unaffected while a project that declares one gets it
    enforced in every provider without any provider knowing what the requirement is.
    """
    if isinstance(policy, CanonicalHomePolicy):
        return policy
    if isinstance(policy, TruthPolicy):
        return CanonicalHomePolicy(policy)
    raise OwnershipEvidenceError(
        "provider requires a TruthPolicy or CanonicalHomePolicy", provider_id=provider_id
    )


def _zone_owner(
    home: CanonicalHomePolicy, locator: str, granularity: OwnershipGranularity
) -> tuple[str, str]:
    """The declared ``(owner, authority)`` for ``locator`` at the declared grain.

    The authority is always the zone's declared authority, so a record always names the
    governing authority whichever grain the project holds ownership at.
    """
    classification = home.policy.classify(locator)
    authority = classification.authority or classification.zone_id
    owner = locator if granularity is OwnershipGranularity.LOCATOR else authority
    return owner, authority


@dataclass(frozen=True, slots=True)
class EvidenceProviderDescriptor:
    """How an evidence provider identifies itself and how strongly it speaks."""

    provider_id: str
    kind: EvidenceKind
    precedence: int = DEFAULT_PRECEDENCE
    authority: str = ""
    description: str = ""

    def __post_init__(self) -> None:
        if not isinstance(self.provider_id, str) or not self.provider_id.strip():
            raise OwnershipEvidenceError("provider_id must be a non-empty string")
        if not isinstance(self.kind, EvidenceKind):
            raise OwnershipEvidenceError(
                "provider kind must be an EvidenceKind", provider_id=self.provider_id
            )
        if not isinstance(self.precedence, int) or isinstance(self.precedence, bool):
            raise OwnershipEvidenceError(
                "provider precedence must be an int", provider_id=self.provider_id
            )

    @property
    def order_key(self) -> tuple[int, str]:
        """Deterministic provider order: highest precedence first, then identity."""
        return (-self.precedence, self.provider_id)

    def to_dict(self) -> dict[str, Any]:
        """A JSON-serialisable projection of this descriptor."""
        return {
            "provider_id": self.provider_id,
            "kind": self.kind.value,
            "precedence": self.precedence,
            "authority": self.authority,
            "constitutive": self.kind.constitutive,
            "description": self.description,
        }

    def fingerprint(self) -> str:
        """The deterministic content fingerprint of this descriptor."""
        return content_hash(self.to_dict())


@dataclass(frozen=True, slots=True)
class EvidenceRefusal:
    """A candidate locator a provider identified but the canonical-home policy refused.

    A refusal is the *diagnosis* of an absence. Without it, a subject whose only definitional
    artifact sits outside a declared home zone is indistinguishable from a subject nobody ever
    wrote anything about: both simply have no evidence, and neither can be acted on. With it,
    the determination can state which locator was refused and under which declared eligibility
    dimension — so the residue is triaged into "remedy this named deficit" and "an authority
    must decide", instead of one undifferentiated backlog.

    A refusal is NEVER evidence and NEVER an owner. It records only that a candidate existed
    and why the declarations refused it (OWN-REQ-001, OWN-REQ-003).
    """

    provider_id: str
    subject_id: str
    locator: str
    reason: str

    def __post_init__(self) -> None:
        for field, value in (
            ("provider_id", self.provider_id),
            ("subject_id", self.subject_id),
            ("locator", self.locator),
            ("reason", self.reason),
        ):
            if not isinstance(value, str) or not value.strip():
                raise OwnershipEvidenceError(
                    f"a refusal requires a non-empty {field}", provider_id=self.provider_id
                )

    @property
    def order_key(self) -> tuple[str, str, str]:
        """Deterministic refusal order: locator, then provider identity, then reason."""
        return (self.locator, self.provider_id, self.reason)

    @property
    def refusal_id(self) -> str:
        """The content-addressed identity of this refusal."""
        return f"UCOS-UOFX-{content_hash(self.to_dict())[:16]}"

    def to_dict(self) -> dict[str, Any]:
        """A JSON-serialisable projection of this refusal."""
        return {
            "provider_id": self.provider_id,
            "subject_id": self.subject_id,
            "locator": self.locator,
            "reason": self.reason,
        }


class OwnershipEvidenceProvider(ABC):
    """The extension point for every source of ownership evidence, present or future."""

    @abstractmethod
    def descriptor(self) -> EvidenceProviderDescriptor:
        """Describe this provider's identity, evidence kind and declared precedence."""
        raise NotImplementedError  # pragma: no cover - abstract

    @abstractmethod
    def provide(self, subject: Subject) -> Iterable[OwnershipEvidence]:
        """Report the ownership evidence this provider observes for ``subject``."""
        raise NotImplementedError  # pragma: no cover - abstract

    def refusals(self, subject: Subject) -> Iterable[EvidenceRefusal]:
        """Candidates this provider recognised for ``subject`` but was not permitted to use.

        The default is *no refusal*, which is the honest answer for a provider that applies no
        eligibility gate: it never had a candidate to lose. Only a provider that discards a
        candidate has a refusal to report.
        """
        return ()

    def evidence(
        self,
        subject_id: str,
        owner: str,
        *,
        locator: str = "",
        detail: str = "",
    ) -> OwnershipEvidence:
        """Helper that stamps this provider's identity, kind, authority and precedence."""
        descriptor = self.descriptor()
        return OwnershipEvidence.create(
            subject_id,
            owner,
            descriptor.kind,
            locator=locator,
            provider_id=descriptor.provider_id,
            authority=descriptor.authority,
            precedence=descriptor.precedence,
            detail=detail,
        )

    def collect(self, subject: Subject) -> tuple[OwnershipEvidence, ...]:
        """Protocol enforcement: contain faults, verify provenance, order deterministically."""
        if not isinstance(subject, Subject):
            raise OwnershipEvidenceError("evidence collection requires a Subject")
        descriptor = self.descriptor()
        try:
            produced = tuple(self.provide(subject))
        except OwnershipEvidenceError:
            raise
        except Exception as exc:  # noqa: BLE001 - contained by design (fail-closed)
            raise OwnershipEvidenceError(
                "evidence provider failed",
                provider_id=descriptor.provider_id,
                subject=subject.subject_id,
                detail=str(exc),
            ) from exc
        for item in produced:
            if not isinstance(item, OwnershipEvidence):
                raise OwnershipEvidenceError(
                    "provider produced a non-evidence value",
                    provider_id=descriptor.provider_id,
                )
            if item.provider_id != descriptor.provider_id:
                raise OwnershipEvidenceError(
                    "evidence provenance does not match its provider",
                    provider_id=descriptor.provider_id,
                    evidence_provider=item.provider_id,
                )
            if item.subject_id != subject.subject_id:
                raise OwnershipEvidenceError(
                    "evidence subject does not match the requested subject",
                    provider_id=descriptor.provider_id,
                    subject=subject.subject_id,
                )
        unique = {item.evidence_id: item for item in produced}
        return tuple(sorted(unique.values(), key=lambda item: item.order_key))

    def collect_refusals(self, subject: Subject) -> tuple[EvidenceRefusal, ...]:
        """Protocol enforcement for refusals: same containment, provenance and ordering.

        A provider that faults while diagnosing must not be able to turn a refusal into
        silence, because a silent refusal is exactly the blind spot this channel exists to
        remove (fail-closed).
        """
        if not isinstance(subject, Subject):
            raise OwnershipEvidenceError("refusal collection requires a Subject")
        descriptor = self.descriptor()
        try:
            produced = tuple(self.refusals(subject))
        except OwnershipEvidenceError:
            raise
        except Exception as exc:  # noqa: BLE001 - contained by design (fail-closed)
            raise OwnershipEvidenceError(
                "evidence provider failed while diagnosing a refusal",
                provider_id=descriptor.provider_id,
                subject=subject.subject_id,
                detail=str(exc),
            ) from exc
        for item in produced:
            if not isinstance(item, EvidenceRefusal):
                raise OwnershipEvidenceError(
                    "provider produced a non-refusal value",
                    provider_id=descriptor.provider_id,
                )
            if item.provider_id != descriptor.provider_id:
                raise OwnershipEvidenceError(
                    "refusal provenance does not match its provider",
                    provider_id=descriptor.provider_id,
                    evidence_provider=item.provider_id,
                )
            if item.subject_id != subject.subject_id:
                raise OwnershipEvidenceError(
                    "refusal subject does not match the requested subject",
                    provider_id=descriptor.provider_id,
                    subject=subject.subject_id,
                )
        unique = {item.refusal_id: item for item in produced}
        return tuple(sorted(unique.values(), key=lambda item: item.order_key))


class HomeGatedEvidenceProvider(OwnershipEvidenceProvider, ABC):
    """A provider whose candidate locators are gated by a declared canonical-home policy.

    Three providers had grown the same eight-line loop — recognise candidates, ask the
    canonical-home policy, classify the zone, resolve the zone's owner at the declared grain,
    stamp evidence — and each one discarded its rejected candidates silently and differently.
    That loop is written **once** here.

    A subclass declares only what is genuinely its own: which locators it recognises for a
    subject (:meth:`candidates`) and how it describes its own finding (:meth:`detail`).
    Eligibility, authority resolution, precedence composition, ordering and refusal diagnosis
    are the base class's, so no future provider can reintroduce a different answer to "may this
    locator hold ownership?" (UFC-14, UFC-16).
    """

    @property
    @abstractmethod
    def home(self) -> CanonicalHomePolicy:
        """The composed canonical-home policy deciding which candidates may own."""
        raise NotImplementedError  # pragma: no cover - abstract

    @property
    @abstractmethod
    def granularity(self) -> OwnershipGranularity:
        """The declared grain at which this provider names an owner."""
        raise NotImplementedError  # pragma: no cover - abstract

    @abstractmethod
    def candidates(self, subject: Subject) -> tuple[str, ...]:
        """The locators this provider recognises for ``subject``, before eligibility."""
        raise NotImplementedError  # pragma: no cover - abstract

    @abstractmethod
    def detail(self, locator: str, classification: Any) -> str:
        """How this provider describes the finding it makes at ``locator``."""
        raise NotImplementedError  # pragma: no cover - abstract

    def provide(self, subject: Subject) -> Iterable[OwnershipEvidence]:
        """Evidence for every candidate locator the declarations admit."""
        descriptor = self.descriptor()
        home = self.home
        findings: list[OwnershipEvidence] = []
        for locator in self.candidates(subject):
            if not home.admits(locator):
                continue
            classification = home.policy.classify(locator)
            owner, authority = _zone_owner(home, locator, self.granularity)
            findings.append(
                OwnershipEvidence.create(
                    subject.subject_id,
                    owner,
                    descriptor.kind,
                    locator=locator,
                    provider_id=descriptor.provider_id,
                    authority=authority,
                    precedence=descriptor.precedence + classification.precedence,
                    detail=self.detail(locator, classification),
                )
            )
        return tuple(findings)

    def refusals(self, subject: Subject) -> Iterable[EvidenceRefusal]:
        """The declared eligibility verdict for every candidate the policy refused."""
        descriptor = self.descriptor()
        home = self.home
        found: list[EvidenceRefusal] = []
        for locator in self.candidates(subject):
            verdict = home.verdict(locator)
            if verdict.eligible:
                continue
            found.append(
                EvidenceRefusal(
                    provider_id=descriptor.provider_id,
                    subject_id=subject.subject_id,
                    locator=verdict.locator,
                    reason=verdict.reason,
                )
            )
        return tuple(found)


class DeclaredAssignmentProvider(OwnershipEvidenceProvider):
    """Reads a machine-readable ownership *declaration catalogue* — the governed assignment.

    This is the provider that turns human governance ("this authority owns this subject")
    into constitutive evidence, for any project, without a heuristic anywhere.
    """

    __slots__ = ("_descriptor", "_declarations")

    def __init__(
        self,
        declarations: Mapping[str, Mapping[str, Any]],
        *,
        provider_id: str = "ownership.declared-assignment",
        precedence: int = 900,
        authority: str = "",
        description: str = "Declared ownership assignments (governed catalogue).",
    ) -> None:
        if not isinstance(declarations, Mapping):
            raise OwnershipEvidenceError("declarations must be a mapping", provider_id=provider_id)
        self._descriptor = EvidenceProviderDescriptor(
            provider_id=provider_id,
            kind=EvidenceKind.DECLARED_ASSIGNMENT,
            precedence=precedence,
            authority=authority,
            description=description,
        )
        self._declarations = {
            str(key): dict(value)
            for key, value in declarations.items()
            if isinstance(value, Mapping)
        }

    @classmethod
    def from_document(
        cls, document: Mapping[str, Any], **kwargs: Any
    ) -> DeclaredAssignmentProvider:
        """Build from a declared document ``{"authority": ..., "assignments": {...}}``."""
        if not isinstance(document, Mapping):
            raise OwnershipEvidenceError("ownership declaration document must be a mapping")
        assignments = document.get("assignments", {})
        if not isinstance(assignments, Mapping):
            raise OwnershipEvidenceError("'assignments' must be a mapping of subject → claim")
        options: dict[str, Any] = {}
        if "authority" in document:
            options["authority"] = str(document["authority"])
        if "provider_id" in document:
            options["provider_id"] = str(document["provider_id"])
        if "precedence" in document:
            options["precedence"] = int(document["precedence"])
        options.update(kwargs)
        return cls(assignments, **options)

    @classmethod
    def from_file(cls, path: Path | str, **kwargs: Any) -> DeclaredAssignmentProvider:
        """Build from a declared JSON document at ``path`` (fail-closed)."""
        target = Path(path)
        try:
            document = json.loads(target.read_text("utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise OwnershipEvidenceError(
                "ownership declaration document could not be read",
                path=str(target),
                detail=str(exc),
            ) from exc
        return cls.from_document(document, **kwargs)

    @property
    def count(self) -> int:
        """How many subjects the catalogue declares."""
        return len(self._declarations)

    def descriptor(self) -> EvidenceProviderDescriptor:
        """Describe this provider."""
        return self._descriptor

    def provide(self, subject: Subject) -> Iterable[OwnershipEvidence]:
        """The declared assignment for ``subject``, if the catalogue declares one."""
        claim = self._declarations.get(subject.subject_id)
        if not claim:
            return ()
        owner = str(claim.get("owner", "")).strip()
        if not owner:
            raise OwnershipEvidenceError(
                "declared assignment names no owner",
                provider_id=self._descriptor.provider_id,
                subject=subject.subject_id,
            )
        locator = str(claim.get("locator", "")).strip()
        authority = str(claim.get("authority", self._descriptor.authority)).strip()
        return (
            OwnershipEvidence.create(
                subject.subject_id,
                owner,
                EvidenceKind.DECLARED_ASSIGNMENT,
                locator=locator,
                provider_id=self._descriptor.provider_id,
                authority=authority,
                precedence=int(claim.get("precedence", self._descriptor.precedence)),
                detail=str(claim.get("detail", "declared ownership assignment")),
            ),
        )


class DefinitionalLocatorProvider(HomeGatedEvidenceProvider):
    """A subject's own definitional artifact, inside a zone declared able to own it.

    The rule is not a heuristic about ownership: the *evidence* is the artifact, and the
    *owner* is the authority the Repository Truth policy already declared for that zone. A
    locator in a non-eligible zone yields nothing — evidence never becomes a home — but it now
    yields a **refusal**, so "nothing" can be told apart from "nothing was ever written".

    Eligibility is decided by the one composition that decides it
    (:class:`~platform.universal_truth.eligibility.CanonicalHomePolicy`): the zone decides the
    class, and a declared eligibility ledger decides the artifact. Passing a bare
    :class:`~platform.universal_truth.policy.TruthPolicy` composes an open ledger, so a
    project that imposes no artifact requirement behaves exactly as before.
    """

    __slots__ = ("_descriptor", "_home", "_separators", "_granularity")

    def __init__(
        self,
        policy: TruthPolicy | CanonicalHomePolicy,
        *,
        provider_id: str = "ownership.definitional-locator",
        precedence: int = 500,
        separators: Iterable[str] = DEFAULT_QUALIFIER_SEPARATORS,
        granularity: OwnershipGranularity | str = OwnershipGranularity.AUTHORITY,
        description: str = "Definitional artifact inside a declared canonical-home zone.",
    ) -> None:
        self._home = _canonical_home(policy, provider_id=provider_id)
        self._separators = tuple(str(item) for item in separators if str(item))
        self._granularity = OwnershipGranularity.coerce(granularity, subject=provider_id)
        self._descriptor = EvidenceProviderDescriptor(
            provider_id=provider_id,
            kind=EvidenceKind.DEFINITIONAL_LOCATOR,
            precedence=precedence,
            authority="",
            description=description,
        )

    @property
    def policy(self) -> TruthPolicy:
        """The Repository Truth policy that decides zone eligibility and authority."""
        return self._home.policy

    @property
    def home(self) -> CanonicalHomePolicy:
        """The composed canonical-home policy (zone class plus declared eligibility)."""
        return self._home

    @property
    def granularity(self) -> OwnershipGranularity:
        """The declared grain at which this provider names an owner."""
        return self._granularity

    def descriptor(self) -> EvidenceProviderDescriptor:
        """Describe this provider."""
        return self._descriptor

    def _is_definitional(self, basename: str, subject_id: str) -> bool:
        name = basename.upper()
        target = subject_id.upper()
        stem = name.rsplit(".", 1)[0] if "." in name else name
        if stem == target or name == target:
            return True
        return any(name.startswith(f"{target}{separator}") for separator in self._separators)

    def candidates(self, subject: Subject) -> tuple[str, ...]:
        """Every locator of ``subject`` whose basename is definitional of its identity."""
        found: list[str] = []
        for locator in subject.locators:
            segments = locator_segments(locator)
            if not segments:
                continue
            if self._is_definitional(segments[-1], subject.subject_id):
                found.append(locator)
        return tuple(found)

    def detail(self, locator: str, classification: Any) -> str:
        """How this provider describes a definitional-locator finding."""
        return (
            f"definitional artifact in declared zone {classification.zone_id} "
            f"({classification.truth_class.value})"
        )


class RoleLocatorProvider(HomeGatedEvidenceProvider):
    """Evidence from locators a project already tagged with a declared **role**.

    This is the provider that lets the Foundation *reuse* a measurement some other instrument
    already owns instead of re-deriving it. Where a project's population document records
    which locators are the definitional ones — because whichever engine owns that question
    measured it — this provider adopts that measurement verbatim and turns it into ownership
    evidence. Knowledge Once: the role is read, never recomputed, and this provider contains
    no rule about what makes a locator definitional.

    Zone eligibility still governs. A role tag is a statement about *which* locators matter,
    never a licence for an ineligible locator to become a home.
    """

    __slots__ = ("_descriptor", "_home", "_role", "_granularity")

    def __init__(
        self,
        role: str,
        policy: TruthPolicy | CanonicalHomePolicy,
        *,
        provider_id: str = "",
        precedence: int = 500,
        kind: EvidenceKind = EvidenceKind.DEFINITIONAL_LOCATOR,
        granularity: OwnershipGranularity | str = OwnershipGranularity.AUTHORITY,
        description: str = "",
    ) -> None:
        if not isinstance(role, str) or not role.strip():
            raise OwnershipEvidenceError("role provider requires a declared role name")
        resolved_id = provider_id.strip() or f"ownership.role.{role.strip()}"
        self._role = role.strip()
        self._home = _canonical_home(policy, provider_id=resolved_id)
        self._granularity = OwnershipGranularity.coerce(granularity, subject=resolved_id)
        self._descriptor = EvidenceProviderDescriptor(
            provider_id=resolved_id,
            kind=EvidenceKind.coerce(kind, subject=resolved_id),
            precedence=precedence,
            authority="",
            description=description or f"Locators tagged with the declared role '{self._role}'.",
        )

    @property
    def role(self) -> str:
        """The declared role this provider reads."""
        return self._role

    @property
    def home(self) -> CanonicalHomePolicy:
        """The composed canonical-home policy (zone class plus declared eligibility)."""
        return self._home

    @property
    def granularity(self) -> OwnershipGranularity:
        """The declared grain at which this provider names an owner."""
        return self._granularity

    def descriptor(self) -> EvidenceProviderDescriptor:
        """Describe this provider."""
        return self._descriptor

    def candidates(self, subject: Subject) -> tuple[str, ...]:
        """Every locator ``subject`` tags with this provider's declared role."""
        return tuple(subject.role(self._role))

    def detail(self, locator: str, classification: Any) -> str:
        """How this provider describes a declared-role finding."""
        return f"locator declared '{self._role}' for this subject, in zone {classification.zone_id}"


class DeclaredIdentityProvider(HomeGatedEvidenceProvider):
    """An artifact that *declares* which subject it owns, read from assimilated content.

    A declaration inside content is stronger evidence than a filename, so this provider
    outranks :class:`DefinitionalLocatorProvider`. It never reads the filesystem: the
    locator → declared-identity mapping is supplied by the caller, normally derived from
    assimilation units via :func:`declared_identities`. Zone eligibility still governs — a
    declaration inside an evidence, derived or operational-memory zone establishes nothing.
    """

    __slots__ = ("_descriptor", "_home", "_declarations", "_granularity")

    def __init__(
        self,
        declarations: Mapping[str, str],
        policy: TruthPolicy | CanonicalHomePolicy,
        *,
        provider_id: str = "ownership.declared-identity",
        precedence: int = 700,
        granularity: OwnershipGranularity | str = OwnershipGranularity.AUTHORITY,
        description: str = "Artifact-declared subject identity inside a declared home zone.",
    ) -> None:
        if not isinstance(declarations, Mapping):
            raise OwnershipEvidenceError("declarations must be a mapping", provider_id=provider_id)
        self._home = _canonical_home(policy, provider_id=provider_id)
        self._granularity = OwnershipGranularity.coerce(granularity, subject=provider_id)
        self._declarations: dict[str, list[str]] = {}
        for locator, subject_id in declarations.items():
            self._declarations.setdefault(str(subject_id), []).append(str(locator))
        self._descriptor = EvidenceProviderDescriptor(
            provider_id=provider_id,
            kind=EvidenceKind.DECLARED_IDENTITY,
            precedence=precedence,
            authority="",
            description=description,
        )

    @property
    def count(self) -> int:
        """How many subjects some locator declares."""
        return len(self._declarations)

    @property
    def home(self) -> CanonicalHomePolicy:
        """The composed canonical-home policy (zone class plus declared eligibility)."""
        return self._home

    @property
    def granularity(self) -> OwnershipGranularity:
        """The declared grain at which this provider names an owner."""
        return self._granularity

    def descriptor(self) -> EvidenceProviderDescriptor:
        """Describe this provider."""
        return self._descriptor

    def candidates(self, subject: Subject) -> tuple[str, ...]:
        """Every locator that declares ownership of ``subject``."""
        return tuple(sorted(self._declarations.get(subject.subject_id, ())))

    def detail(self, locator: str, classification: Any) -> str:
        """How this provider describes a declared-identity finding."""
        return f"artifact declares ownership of this subject in zone {classification.zone_id}"


#: The labels after which an artifact may declare the subject it owns.
DEFAULT_IDENTITY_LABELS: tuple[str, ...] = (
    "ARTIFACT ID",
    "ARTIFACT IDENTIFIER",
    "ARTIFACT-ID",
    "CANONICAL SUBJECT",
    "OWNS",
)

_DECLARED_IDENTITY = re.compile(
    r"(?:%s)\s*[:|]\s*[`*\s]*([A-Za-z0-9][A-Za-z0-9._Ω∞-]{2,})",
    re.IGNORECASE,
)


def declared_identities(
    content: Mapping[str, str], *, labels: Iterable[str] = DEFAULT_IDENTITY_LABELS
) -> dict[str, str]:
    """Extract locator → declared subject identity from already-read content.

    ``content`` maps a locator to text the caller already holds — assimilated units, an API
    response, a database row. Nothing is read from disk here, so ownership evidence can be
    derived without ever rediscovering a repository.
    """
    pattern = re.compile(
        _DECLARED_IDENTITY.pattern % "|".join(re.escape(label) for label in labels),
        re.IGNORECASE,
    )
    found: dict[str, str] = {}
    for locator, text in content.items():
        if not isinstance(text, str):
            continue
        match = pattern.search(text)
        if match:
            found[str(locator)] = match.group(1).strip(" `*")
    return found


#: How many leading bytes of an artifact are searched for its identity declaration. A
#: declaration is front matter by convention, so an identifier mentioned deep in a body table
#: cannot be mistaken for a self-declaration.
DEFAULT_IDENTITY_HEAD_BYTES = 40000


def read_declared_identities(
    locators: Iterable[str],
    *,
    root: Path | str = ".",
    labels: Iterable[str] = DEFAULT_IDENTITY_LABELS,
    head_bytes: int = DEFAULT_IDENTITY_HEAD_BYTES,
) -> dict[str, str]:
    """Read the head of each **declared** locator and extract its self-declared identity.

    This reads only locators it was given, never a directory: there is no scan, no glob and no
    discovery here, so the population remains whatever Truth declared. An unreadable locator
    contributes nothing rather than raising — a missing artifact is an absent declaration, and
    absence must never resolve to an assertion (fail-closed).
    """
    base = Path(root)
    content: dict[str, str] = {}
    for locator in locators:
        normalized = str(locator).strip()
        if not normalized:
            continue
        try:
            text = (base / normalized).read_text("utf-8", errors="replace")[: max(0, head_bytes)]
        except OSError:
            continue
        content[normalized] = text
    return declared_identities(content, labels=labels)


class RegistrationEvidenceProvider(OwnershipEvidenceProvider):
    """Registration evidence: corroborative only — registration is eligibility, not ownership."""

    __slots__ = ("_descriptor", "_registered")

    def __init__(
        self,
        registered: Mapping[str, str] | Iterable[str],
        *,
        provider_id: str = "ownership.registration",
        precedence: int = 200,
        authority: str = "",
        description: str = "Registration ledger (eligibility corroboration).",
    ) -> None:
        if isinstance(registered, Mapping):
            self._registered = {str(key): str(value) for key, value in registered.items()}
        else:
            self._registered = {str(item): "" for item in registered}
        self._descriptor = EvidenceProviderDescriptor(
            provider_id=provider_id,
            kind=EvidenceKind.REGISTRATION,
            precedence=precedence,
            authority=authority,
            description=description,
        )

    @property
    def subject_ids(self) -> frozenset[str]:
        """Every registered subject identity."""
        return frozenset(self._registered)

    def descriptor(self) -> EvidenceProviderDescriptor:
        """Describe this provider."""
        return self._descriptor

    def provide(self, subject: Subject) -> Iterable[OwnershipEvidence]:
        """Corroborating registration evidence, when the subject is registered."""
        if subject.subject_id not in self._registered:
            return ()
        owner = self._registered[subject.subject_id] or self._descriptor.authority
        if not owner:
            return ()
        return (
            OwnershipEvidence.create(
                subject.subject_id,
                owner,
                EvidenceKind.REGISTRATION,
                provider_id=self._descriptor.provider_id,
                authority=self._descriptor.authority,
                precedence=self._descriptor.precedence,
                detail="registered subject (corroboration only)",
            ),
        )


class CallableEvidenceProvider(OwnershipEvidenceProvider):
    """Wraps any callable as an evidence provider — the seam for future authorities."""

    __slots__ = ("_descriptor", "_supplier")

    def __init__(
        self,
        descriptor: EvidenceProviderDescriptor,
        supplier: Callable[[Subject], Iterable[OwnershipEvidence]],
    ) -> None:
        if not isinstance(descriptor, EvidenceProviderDescriptor):
            raise OwnershipEvidenceError("callable provider requires a descriptor")
        if not callable(supplier):
            raise OwnershipEvidenceError(
                "callable provider requires a callable", provider_id=descriptor.provider_id
            )
        self._descriptor = descriptor
        self._supplier = supplier

    def descriptor(self) -> EvidenceProviderDescriptor:
        """Describe this provider."""
        return self._descriptor

    def provide(self, subject: Subject) -> Iterable[OwnershipEvidence]:
        """Delegate to the wrapped supplier."""
        return self._supplier(subject)


class EvidenceProviderRegistry:
    """A deterministic, fail-closed registry of pluggable ownership evidence providers."""

    __slots__ = ("_providers",)

    def __init__(self, providers: Iterable[OwnershipEvidenceProvider] = ()) -> None:
        self._providers: dict[str, OwnershipEvidenceProvider] = {}
        self.extend(providers)

    def add(self, provider: OwnershipEvidenceProvider) -> OwnershipEvidenceProvider:
        """Register ``provider``; idempotent by object, fail-closed on identity collision."""
        if not isinstance(provider, OwnershipEvidenceProvider):
            raise OwnershipEvidenceError("registry accepts only OwnershipEvidenceProvider values")
        descriptor = provider.descriptor()
        existing = self._providers.get(descriptor.provider_id)
        if existing is not None:
            if existing is provider:
                return existing
            raise OwnershipProviderConflictError(
                "provider identity already registered", provider_id=descriptor.provider_id
            )
        self._providers[descriptor.provider_id] = provider
        return provider

    def extend(
        self, providers: Iterable[OwnershipEvidenceProvider]
    ) -> tuple[OwnershipEvidenceProvider, ...]:
        """Register every provider in ``providers``, returning them in resolution order."""
        for provider in providers:
            self.add(provider)
        return self.ordered()

    def remove(self, provider_id: str) -> None:
        """Deregister ``provider_id`` (fail-closed when unknown)."""
        if provider_id not in self._providers:
            raise OwnershipEvidenceError("unknown evidence provider", provider_id=provider_id)
        del self._providers[provider_id]

    def get(self, provider_id: str) -> OwnershipEvidenceProvider | None:
        """The registered provider ``provider_id``, or ``None``."""
        return self._providers.get(provider_id)

    def require(self, provider_id: str) -> OwnershipEvidenceProvider:
        """The registered provider ``provider_id`` (fail-closed)."""
        provider = self.get(provider_id)
        if provider is None:
            raise OwnershipEvidenceError("unknown evidence provider", provider_id=provider_id)
        return provider

    @property
    def count(self) -> int:
        """How many providers are registered."""
        return len(self._providers)

    def ordered(self) -> tuple[OwnershipEvidenceProvider, ...]:
        """Every provider in declared precedence order — never insertion order."""
        return tuple(sorted(self._providers.values(), key=lambda item: item.descriptor().order_key))

    def descriptors(self) -> tuple[EvidenceProviderDescriptor, ...]:
        """Every provider descriptor in resolution order."""
        return tuple(provider.descriptor() for provider in self.ordered())

    def constitutive(self) -> tuple[OwnershipEvidenceProvider, ...]:
        """Every provider whose evidence may establish ownership."""
        return tuple(
            provider for provider in self.ordered() if provider.descriptor().kind.constitutive
        )

    def collect(self, subject: Subject) -> tuple[OwnershipEvidence, ...]:
        """All evidence every provider reports for ``subject``, deterministically ordered."""
        found: dict[str, OwnershipEvidence] = {}
        for provider in self.ordered():
            for item in provider.collect(subject):
                found[item.evidence_id] = item
        return tuple(sorted(found.values(), key=lambda item: item.order_key))

    def refusals(self, subject: Subject) -> tuple[EvidenceRefusal, ...]:
        """Every refusal every provider diagnoses for ``subject``, deterministically ordered.

        This is the population-wide diagnostic channel: the reason a subject has no admissible
        evidence, per candidate locator, in the closed vocabulary the eligibility declarations
        already publish. Nothing here can become an owner.
        """
        found: dict[str, EvidenceRefusal] = {}
        for provider in self.ordered():
            for item in provider.collect_refusals(subject):
                found[item.refusal_id] = item
        return tuple(sorted(found.values(), key=lambda item: item.order_key))

    def collect_all(self, subjects: Iterable[Subject]) -> dict[str, tuple[OwnershipEvidence, ...]]:
        """Evidence for a whole population, keyed by subject identity."""
        return {subject.subject_id: self.collect(subject) for subject in subjects}

    def to_dict(self) -> dict[str, Any]:
        """A JSON-serialisable projection of this registry."""
        return {
            "provider_count": self.count,
            "providers": [descriptor.to_dict() for descriptor in self.descriptors()],
        }

    def fingerprint(self) -> str:
        """The deterministic content fingerprint of this registry."""
        return content_hash(self.to_dict())


__all__ = [
    "DEFAULT_PRECEDENCE",
    "DEFAULT_QUALIFIER_SEPARATORS",
    "EvidenceProviderDescriptor",
    "EvidenceRefusal",
    "OwnershipEvidenceProvider",
    "HomeGatedEvidenceProvider",
    "DeclaredAssignmentProvider",
    "DefinitionalLocatorProvider",
    "DeclaredIdentityProvider",
    "DEFAULT_IDENTITY_LABELS",
    "DEFAULT_IDENTITY_HEAD_BYTES",
    "RoleLocatorProvider",
    "declared_identities",
    "read_declared_identities",
    "RegistrationEvidenceProvider",
    "CallableEvidenceProvider",
    "EvidenceProviderRegistry",
]
