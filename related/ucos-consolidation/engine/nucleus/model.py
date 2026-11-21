"""UCOS-NUC-001 Part 02 — the structural value objects (D-05, D-06, D-04).

One record type carries every structural subject — Nucleus, Layer and Composition —
distinguished by :class:`~engine.nucleus.law.StructuralRole` rather than by three
parallel classes. That is deliberate: three classes would mean three registries, three
identifier paths and three places for a rule to be forgotten. With one record, the
ownership law is a predicate over a field, and a future structural role costs a
vocabulary registration instead of a class.

Three properties are structural rather than conventional:

    * **Identity is derived, never supplied.** Every record's ``universal_id`` is minted
      by the single authority (:mod:`engine.registry.universal.identity`) as a pure
      function of ``(kind, namespace, natural_key)``, so two independent declarations of
      the same subject collapse onto one identity (AC-003).
    * **Role is declared and checked.** :func:`derive_role` recomputes the role from the
      declaration's own content; a declared role that contradicts it is refused (NL-06).
      Classification is therefore not a matter of who typed what.
    * **Content is sealed.** Every record carries the digest of its own canonical
      rendering with the digest field excluded, computed with the one canonical hash
      primitive, so drift and tampering are detectable and replay is exact.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable

from engine.nucleus.errors import MisclassificationError, StructuralValidationError
from engine.nucleus.law import StructuralRole
from engine.registry.universal.identity import (
    RegistryKind,
    content_digest,
    deterministic_id,
    normalize_namespace,
    normalize_natural_key,
)

#: The field excluded from a payload when computing that payload's own digest.
HASH_FIELD = "content_hash"

#: The namespace ownership assignments are registered under. Declared here because the
#: *namespace* is this layer's to choose; the *identifier* is not, and is minted by the
#: single registration authority (see :attr:`OwnershipAssignment.assignment_id`).
ASSIGNMENT_NAMESPACE = "ucos.ownership"

#: The registry kind each structural role mints under, so a Nucleus id is visibly a
#: Nucleus id. DATA, keyed by role — no function branches on a role name.
ROLE_KINDS: Mapping[StructuralRole, RegistryKind] = {
    StructuralRole.NUCLEUS: RegistryKind.NUCLEUS,
    StructuralRole.LAYER: RegistryKind.LAYER,
    StructuralRole.COMPOSITION: RegistryKind.COMPOSITION,
}


def _require_text(value: Any, *, at: str, subject: str = "") -> str:
    if not isinstance(value, str) or not value.strip():
        raise StructuralValidationError(
            "field must be a non-empty string", at=at, subject=subject, value=value
        )
    return value.strip()


def _tuple_of_keys(values: Any, *, at: str, subject: str) -> tuple[str, ...]:
    if values is None:
        return ()
    if isinstance(values, str) or not isinstance(values, Sequence):
        raise StructuralValidationError(
            "field must be a sequence of keys", at=at, subject=subject, value=values
        )
    seen: set[str] = set()
    out: list[str] = []
    for item in values:
        key = _require_text(item, at=f"{at}[]", subject=subject)
        if key in seen:
            raise StructuralValidationError(
                "duplicate key in declaration", at=at, subject=subject, key=key
            )
        seen.add(key)
        out.append(key)
    return tuple(sorted(out))


def seal(payload: Mapping[str, Any]) -> str:
    """The content digest of ``payload`` with its own digest field excluded."""
    return content_digest({k: v for k, v in payload.items() if k != HASH_FIELD})


# --------------------------------------------------------------------------- #
# Structural subjects                                                          #
# --------------------------------------------------------------------------- #


@dataclass(frozen=True, slots=True)
class SubjectDeclaration:
    """A request to register one structural subject (pre-identity form).

    ``concept`` is the single canonical concept a Nucleus owns — a Nucleus that owns
    two concepts is two nuclei. ``composes`` is the set of nucleus keys a Composition
    selects. ``organizes`` is the set of subject keys a Layer files. A declaration
    that fills more than one of ``concept``/``composes`` is refused: it would be two
    subjects wearing one name.
    """

    key: str
    title: str
    role: StructuralRole | str | None = None
    namespace: str = "ucos.structure"
    concept: str = ""
    composes: tuple[str, ...] = ()
    organizes: tuple[str, ...] = ()
    parent: str | None = None
    description: str = ""
    profile: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "key", normalize_natural_key(self.key))
        object.__setattr__(self, "title", _require_text(self.title, at="title", subject=self.key))
        object.__setattr__(self, "namespace", normalize_namespace(self.namespace))
        object.__setattr__(
            self, "concept", self.concept.strip() if isinstance(self.concept, str) else ""
        )
        object.__setattr__(
            self, "composes", _tuple_of_keys(self.composes, at="composes", subject=self.key)
        )
        object.__setattr__(
            self, "organizes", _tuple_of_keys(self.organizes, at="organizes", subject=self.key)
        )
        if self.parent is not None:
            object.__setattr__(
                self, "parent", _require_text(self.parent, at="parent", subject=self.key)
            )
        if self.concept and self.composes:
            raise MisclassificationError(
                "a subject may own a concept or compose nuclei, never both (NL-05/NL-06)",
                subject=self.key,
                concept=self.concept,
                composes=list(self.composes),
            )
        derived = derive_role(self)
        if self.role is None:
            object.__setattr__(self, "role", derived)
        else:
            declared = StructuralRole.coerce(self.role, at=self.key)
            if declared is not derived:
                raise MisclassificationError(
                    "declared structural role contradicts the role derived from the "
                    "declaration itself (NL-06)",
                    subject=self.key,
                    declared=declared.value,
                    derived=derived.value,
                )
            object.__setattr__(self, "role", declared)
        object.__setattr__(self, "profile", dict(self.profile or {}))

    @property
    def identity(self) -> str:
        """The deterministic ``universal_id`` this declaration will be registered as."""
        return deterministic_id(ROLE_KINDS[self.structural_role], self.namespace, self.key)

    @property
    def structural_role(self) -> StructuralRole:
        """The subject's role, always a :class:`StructuralRole` after construction."""
        return StructuralRole.coerce(self.role, at=self.key)

    def to_dict(self) -> dict[str, Any]:
        return {
            "key": self.key,
            "title": self.title,
            "role": self.structural_role.value,
            "namespace": self.namespace,
            "concept": self.concept,
            "composes": list(self.composes),
            "organizes": list(self.organizes),
            "parent": self.parent,
            "description": self.description,
            "profile": dict(self.profile),
        }


@runtime_checkable
class Classifiable(Protocol):
    """The minimum surface the one classification rule reads (NL-06).

    Declared as a protocol rather than a concrete type so *every* holder of the
    classification facts is classified by the same rule — a pre-identity
    :class:`SubjectDeclaration` and a registered :class:`SubjectRecord` alike. Before
    this existed, :func:`derive_role` was typed to the declaration only, so the ownership
    gate could not call it over a record and carried its own copy of the rule. That is
    two authorities over one question, which the Single Authority Principle forbids.
    """

    composes: tuple[str, ...]
    concept: str


def derive_role(declaration: Classifiable) -> StructuralRole:
    """Derive the structural role from a declaration's own content (NL-06).

    The single classification authority. The rule is total and has no default: a subject
    that selects nuclei composes; a subject that owns exactly one canonical concept
    operates; a subject that does neither only organises. This is the clause that makes
    "Commerce is a Composition" a *derivation* rather than an opinion — Commerce selects
    nuclei, therefore Commerce composes, therefore Commerce owns nothing.

    Every classification in the repository resolves here. No caller may re-express the
    rule; ``engine/tests/nucleus/test_classification_convergence.py`` measures that
    structurally over the source and fails if a second implementation appears.
    """
    if declaration.composes:
        return StructuralRole.COMPOSITION
    if declaration.concept:
        return StructuralRole.NUCLEUS
    return StructuralRole.LAYER


@dataclass(frozen=True, slots=True)
class SubjectRecord:
    """A registered structural subject: a declaration plus identity and seal."""

    universal_id: str
    key: str
    title: str
    role: StructuralRole
    namespace: str
    concept: str = ""
    composes: tuple[str, ...] = ()
    organizes: tuple[str, ...] = ()
    parent: str | None = None
    description: str = ""
    profile: Mapping[str, Any] = field(default_factory=dict)
    content_hash: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "role", StructuralRole.coerce(self.role, at=self.key))
        object.__setattr__(self, "profile", dict(self.profile or {}))
        if not self.content_hash:
            object.__setattr__(self, "content_hash", seal(self._payload()))

    @classmethod
    def of(cls, declaration: SubjectDeclaration) -> SubjectRecord:
        """Mint the record for ``declaration`` (identity derived, never supplied)."""
        return cls(
            universal_id=declaration.identity,
            key=declaration.key,
            title=declaration.title,
            role=declaration.structural_role,
            namespace=declaration.namespace,
            concept=declaration.concept,
            composes=declaration.composes,
            organizes=declaration.organizes,
            parent=declaration.parent,
            description=declaration.description,
            profile=dict(declaration.profile),
        )

    def _payload(self) -> dict[str, Any]:
        return {
            "universal_id": self.universal_id,
            "key": self.key,
            "title": self.title,
            "role": self.role.value,
            "namespace": self.namespace,
            "concept": self.concept,
            "composes": list(self.composes),
            "organizes": list(self.organizes),
            "parent": self.parent,
            "description": self.description,
            "profile": dict(self.profile),
        }

    @property
    def may_own_capability(self) -> bool:
        """True iff this subject's role permits owning a capability (NL-01)."""
        return self.role.may_own_capability

    def expected_identity(self) -> str:
        """The identity this record *should* carry, recomputed from its identity tuple."""
        return deterministic_id(ROLE_KINDS[self.role], self.namespace, self.key)

    def is_intact(self) -> bool:
        """True iff identity and digest both reproduce from the record itself."""
        return self.universal_id == self.expected_identity() and self.content_hash == seal(
            self._payload()
        )

    def to_dict(self) -> dict[str, Any]:
        payload = self._payload()
        payload[HASH_FIELD] = self.content_hash
        return payload


# --------------------------------------------------------------------------- #
# Capabilities                                                                 #
# --------------------------------------------------------------------------- #


@dataclass(frozen=True, slots=True)
class CapabilityDeclaration:
    """A request to register one capability, naming the nucleus that owns it.

    ``owner`` is mandatory. There is no constructor path that yields an unowned
    capability, so AC-012's "no orphan capabilities" is enforced by the type rather
    than measured after the fact.
    """

    key: str
    title: str
    owner: str
    namespace: str = "ucos.capability"
    description: str = ""
    depends_on: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "key", normalize_natural_key(self.key))
        object.__setattr__(self, "title", _require_text(self.title, at="title", subject=self.key))
        object.__setattr__(
            self,
            "owner",
            _require_text(self.owner, at="owner", subject=self.key),
        )
        object.__setattr__(self, "namespace", normalize_namespace(self.namespace))
        object.__setattr__(
            self, "depends_on", _tuple_of_keys(self.depends_on, at="depends_on", subject=self.key)
        )

    @property
    def identity(self) -> str:
        return deterministic_id(RegistryKind.CAPABILITY, self.namespace, self.key)

    def to_dict(self) -> dict[str, Any]:
        return {
            "key": self.key,
            "title": self.title,
            "owner": self.owner,
            "namespace": self.namespace,
            "description": self.description,
            "depends_on": list(self.depends_on),
        }


@dataclass(frozen=True, slots=True)
class CapabilityRecord:
    """A registered capability with its derived identity, owner id and seal."""

    universal_id: str
    key: str
    title: str
    owner_key: str
    owner_id: str
    namespace: str
    description: str = ""
    depends_on: tuple[str, ...] = ()
    content_hash: str = ""

    def __post_init__(self) -> None:
        if not self.content_hash:
            object.__setattr__(self, "content_hash", seal(self._payload()))

    def _payload(self) -> dict[str, Any]:
        return {
            "universal_id": self.universal_id,
            "key": self.key,
            "title": self.title,
            "owner_key": self.owner_key,
            "owner_id": self.owner_id,
            "namespace": self.namespace,
            "description": self.description,
            "depends_on": list(self.depends_on),
        }

    def expected_identity(self) -> str:
        return deterministic_id(RegistryKind.CAPABILITY, self.namespace, self.key)

    def is_intact(self) -> bool:
        return self.universal_id == self.expected_identity() and self.content_hash == seal(
            self._payload()
        )

    def to_dict(self) -> dict[str, Any]:
        payload = self._payload()
        payload[HASH_FIELD] = self.content_hash
        return payload


# --------------------------------------------------------------------------- #
# Ownership                                                                    #
# --------------------------------------------------------------------------- #


@dataclass(frozen=True, slots=True)
class OwnershipAssignment:
    """The record that a capability is owned by a subject, and under what authority.

    Append-only by construction (NL-10): a re-assignment names the assignment it
    supersedes, so the chain of custody survives every move.
    """

    capability_id: str
    capability_key: str
    owner_id: str
    owner_key: str
    owner_role: StructuralRole
    authority: str
    supersedes: str | None = None
    note: str = ""
    content_hash: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "owner_role", StructuralRole.coerce(self.owner_role))
        object.__setattr__(
            self, "authority", _require_text(self.authority, at="authority", subject=self.owner_key)
        )
        if not self.content_hash:
            object.__setattr__(self, "content_hash", seal(self._payload()))

    @property
    def assignment_id(self) -> str:
        """A deterministic identity for the assignment triple it expresses.

        Minted **by** the single registration authority
        (:func:`engine.registry.universal.identity.deterministic_id`) rather than
        assembled here. Previously this property built ``"UCOS-REL-" + digest[:12]``
        inline, which put a second decision-maker inside the ``UCOS-`` identifier space
        that authority owns: the resulting id was shape-valid — ``is_well_formed`` accepted
        it and ``parse_kind_name`` reported ``RELATIONSHIP`` — yet no authority had minted
        it. Overlapping population plus an independent decision is authority duplication,
        so the decision is delegated and only the *natural key* is derived here.

        The natural key is the canonical digest of the triple, which is what a
        relationship's stable business key is: two assignments expressing the same
        (capability, owner, authority, supersedes) collapse onto one identity, and the
        digest is whitespace-free so the authority's key rule accepts it.
        """
        return deterministic_id(
            RegistryKind.RELATIONSHIP,
            ASSIGNMENT_NAMESPACE,
            content_digest(
                [self.capability_id, self.owner_id, self.authority, self.supersedes or ""]
            ),
        )

    def _payload(self) -> dict[str, Any]:
        return {
            "capability_id": self.capability_id,
            "capability_key": self.capability_key,
            "owner_id": self.owner_id,
            "owner_key": self.owner_key,
            "owner_role": self.owner_role.value,
            "authority": self.authority,
            "supersedes": self.supersedes,
            "note": self.note,
        }

    @property
    def is_lawful(self) -> bool:
        """True iff the owner's role permits ownership (NL-01/NL-02/NL-03)."""
        return self.owner_role.may_own_capability

    def to_dict(self) -> dict[str, Any]:
        payload = self._payload()
        payload["assignment_id"] = self.assignment_id
        payload[HASH_FIELD] = self.content_hash
        return payload


__all__ = [
    "HASH_FIELD",
    "ROLE_KINDS",
    "seal",
    "Classifiable",
    "SubjectDeclaration",
    "SubjectRecord",
    "CapabilityDeclaration",
    "CapabilityRecord",
    "OwnershipAssignment",
    "derive_role",
]
