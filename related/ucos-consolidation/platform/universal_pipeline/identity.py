"""UAPF-000001 — the Universal Identity Engine and the Universal Meta Object Engine.

Every object UAPF governs — a pipeline, a stage, an execution unit, a queue entry, a
verdict, a record, a transaction, a tick — carries **one** canonical identity, and that
identity is *derived* from what the object is rather than assigned by a counter, a clock
or a caller. Two declarations with the same content therefore mint the same identity in
every environment and at every commit, and two declarations that differ anywhere cannot
collide.

Why an identity engine and a meta-object engine are the same module
------------------------------------------------------------------
An identity is only meaningful with respect to a *kind* of object, and the set of kinds
is exactly the meta-model: the open enumeration of the object categories UAPF is allowed
to reason about. Splitting them would create two registries that must agree — a kind
registry and an identity namespace — and the two would drift. Here a kind is registered
once (:func:`register_object_kind`) and minting against an unregistered kind fails
closed, so the meta-model and the identity namespace cannot disagree by construction.

Open world (no enumeration in behaviour)
----------------------------------------
:data:`SEED_OBJECT_KINDS` is a *declaration*, not a switch: it is registered through the
same public :func:`register_object_kind` that any caller uses, so a seeded kind holds no
privileged position and admitting a new object category is one data entry. Nothing in
this module branches on a specific kind.

Reuse posture
-------------
The hash is :func:`platform.foundation.contracts.content_hash` — the single canonical
serialization + digest the repository already owns (IMP-007 §5). The kind registry is a
:class:`~platform.universal_pipeline.vocabulary.Vocabulary`, the one open-registration
primitive this package owns, so object kinds are governed by the same append-only,
fail-closed discipline as pipeline types, event categories, stage handlers and readiness
predicates rather than by a fifth hand-rolled dictionary. UAPF introduces no second
hashing rule, no second identity namespace and no wall-clock, RNG or ambient state, so
minting is pure and total over its inputs.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from platform.foundation.contracts import content_hash
from platform.universal_pipeline.errors import PipelineIdentityError
from platform.universal_pipeline.vocabulary import Vocabulary
from typing import Any

#: The identity namespace prefix. Every UAPF identity renders as
#: ``UAPF-<KIND>-<digest>``, so an identity names its own meta-object kind and its own
#: authority without a lookup.
IDENTITY_PREFIX = "UAPF"

#: The number of hex characters of the content digest carried in a rendered identity.
#: 20 hex characters is 80 bits — collision-free at any repository scale, while keeping
#: an identity readable in a log line or a table cell.
DIGEST_WIDTH = 20

#: The object kinds seeded at import. A *declaration*: each is registered through the
#: public :func:`register_object_kind`, so this tuple confers no special status and the
#: registry stays open. Adding a kind here — or calling the function from anywhere — is
#: the whole cost of admitting a new category of governed object.
SEED_OBJECT_KINDS: tuple[tuple[str, str], ...] = (
    ("capability", "a capability a pipeline declares it provides or requires"),
    ("catalog", "a discovered declaration catalogue of pipelines"),
    ("certification-record", "the certification verdict recorded for a subject"),
    ("dependency-closure", "the transitive dependency closure of one node"),
    ("discovery-report", "the admission/refusal outcome of one discovery pass"),
    ("event", "a recorded pipeline event"),
    ("execution-unit", "one unit of work executing one pipeline"),
    ("gate", "a declared blocking or advisory gate"),
    ("governance-verdict", "the policy-evaluation verdict for a subject"),
    ("handler", "a registered stage handler"),
    ("orchestration-tick", "one autonomous orchestration tick"),
    ("pipeline", "a declared pipeline"),
    ("plan", "the derived execution plan of a pipeline"),
    ("platform", "a composed UAPF platform instance"),
    ("plugin", "a registered pipeline extension point binding"),
    ("policy", "a declared governance policy"),
    ("queue-entry", "one membership record in a derived queue"),
    ("recovery-point", "a recorded forward-only recovery checkpoint"),
    ("schedule", "a derived dependency-safe execution schedule"),
    ("stage", "one declared stage of a pipeline"),
    ("telemetry", "a recorded metric or span"),
    ("transaction", "one gateway admission transaction"),
    ("validation-record", "the validation verdict recorded for a subject"),
    ("verification-record", "the verification verdict recorded for a subject"),
)

#: The meta-object kind vocabulary. Module-level because the meta-model is a property of
#: the framework, not of one platform instance: a kind registered by any consumer is
#: available to every consumer, which is precisely what prevents a second namespace.
_OBJECT_KINDS = Vocabulary("object-kind", error=PipelineIdentityError)


def register_object_kind(kind: str, description: str = "") -> None:
    """Register one meta-object kind (unbounded extension by declaration).

    Raises:
        PipelineIdentityError: if ``kind`` is not a lower-case dotted/hyphenated token, or
            is already registered. Re-registration is refused rather than ignored: a kind
            is the root of an identity namespace, and silently rebinding one would let two
            different meanings share a namespace — the ambiguity this module exists to
            remove.
    """
    _OBJECT_KINDS.register(kind, description=description)


def object_kinds() -> tuple[str, ...]:
    """Every registered meta-object kind, sorted (deterministic)."""
    return _OBJECT_KINDS.terms()


def object_kind_description(kind: str) -> str:
    """The declared description of ``kind``.

    Raises:
        PipelineIdentityError: if ``kind`` is not registered (fail-closed).
    """
    return _OBJECT_KINDS.require(kind).description


def require_object_kind(kind: str) -> None:
    """Fail closed unless ``kind`` is a registered meta-object kind.

    Raises:
        PipelineIdentityError: naming ``kind`` and how many kinds are registered, so an
            unknown kind is diagnosable without reading this module.
    """
    _OBJECT_KINDS.require(kind)


def meta_model() -> dict[str, Any]:
    """The declared meta-model as a deterministic, serializable mapping (evidence).

    The one place the meta-model is rendered for registration, evidence and
    traceability. Derived from the vocabulary, so it can never disagree with it.
    """
    return {
        "identity_prefix": IDENTITY_PREFIX,
        "digest_width": DIGEST_WIDTH,
        "kind_count": len(_OBJECT_KINDS),
        "kinds": [
            {"kind": declared.term, "description": declared.description}
            for declared in _OBJECT_KINDS.declarations()
        ],
        "fingerprint": _OBJECT_KINDS.fingerprint(),
    }


def _render_namespace(kind: str) -> str:
    """Render ``kind`` as an identity namespace segment (upper-case, hyphen-separated).

    Pure and total: any character that is not alphanumeric becomes a hyphen, so a kind
    is always renderable and the rendering is injective over the registered kinds
    (uniqueness of the whole identity is carried by the digest regardless).
    """
    return "".join(char if char.isalnum() else "-" for char in kind).upper()


@dataclass(frozen=True, slots=True)
class Identity:
    """An immutable, content-addressed identity for one governed meta-object.

    ``value`` is the canonical render (``UAPF-<KIND>-<digest>``) and is the identity
    used everywhere in UAPF. ``parts`` is retained because an identity that cannot say
    what it was derived from is not traceable: :meth:`verify` recomputes the digest from
    ``kind`` + ``parts``, so a tampered identity is detectable without a registry lookup.
    """

    kind: str
    parts: tuple[str, ...]
    value: str

    def __post_init__(self) -> None:
        if not isinstance(self.kind, str) or not self.kind:
            raise PipelineIdentityError("identity kind is required")
        if not isinstance(self.value, str) or not self.value:
            raise PipelineIdentityError("identity value is required", kind=self.kind)
        if not isinstance(self.parts, tuple):
            raise PipelineIdentityError("identity parts must be a tuple", kind=self.kind)
        for part in self.parts:
            if not isinstance(part, str) or not part:
                raise PipelineIdentityError(
                    "identity parts must be non-empty strings",
                    kind=self.kind,
                )

    @property
    def digest(self) -> str:
        """The content digest segment of the rendered identity."""
        return self.value.rsplit("-", 1)[-1]

    def verify(self) -> bool:
        """True iff ``value`` is the identity ``kind`` + ``parts`` actually derive."""
        return self.value == _render_identity(self.kind, self.parts)

    def require_intact(self) -> None:
        """Fail closed unless :meth:`verify` holds.

        Raises:
            PipelineIdentityError: if the identity does not match its own derivation —
                i.e. it was constructed by hand rather than minted.
        """
        if not self.verify():
            raise PipelineIdentityError(
                "identity does not match its own derivation (not minted)",
                kind=self.kind,
                value=self.value,
            )

    def to_dict(self) -> dict[str, Any]:
        return {"kind": self.kind, "parts": list(self.parts), "value": self.value}

    def __str__(self) -> str:
        return self.value


def _render_identity(kind: str, parts: tuple[str, ...]) -> str:
    """The single derivation rule: ``UAPF-<KIND>-<digest of kind + parts>``."""
    digest = content_hash({"kind": kind, "parts": list(parts)})[:DIGEST_WIDTH]
    return f"{IDENTITY_PREFIX}-{_render_namespace(kind)}-{digest}"


def mint(kind: str, *parts: str) -> Identity:
    """Mint the canonical identity of the ``kind`` object described by ``parts``.

    Deterministic and idempotent: the same ``kind`` and the same ``parts`` in the same
    order always yield an equal :class:`Identity`, so re-minting is a no-op rather than
    a second identity for one object (AIF-L13). Order *is* significant — ``("a", "b")``
    and ``("b", "a")`` describe different objects — so parts are not sorted.

    Raises:
        PipelineIdentityError: if ``kind`` is unregistered, no parts were supplied, or
            any part is not a non-empty string (fail-closed).
    """
    require_object_kind(kind)
    if not parts:
        raise PipelineIdentityError("at least one identity part is required", kind=kind)
    for part in parts:
        if not isinstance(part, str) or not part:
            raise PipelineIdentityError("identity parts must be non-empty strings", kind=kind)
    resolved = tuple(parts)
    return Identity(kind=kind, parts=resolved, value=_render_identity(kind, resolved))


def mint_from(kind: str, parts: Iterable[str]) -> Identity:
    """:func:`mint` for a caller that already holds an iterable of parts."""
    return mint(kind, *tuple(parts))


for _kind, _description in SEED_OBJECT_KINDS:
    register_object_kind(_kind, _description)
del _kind, _description


__all__ = [
    "DIGEST_WIDTH",
    "IDENTITY_PREFIX",
    "SEED_OBJECT_KINDS",
    "Identity",
    "meta_model",
    "mint",
    "mint_from",
    "object_kind_description",
    "object_kinds",
    "register_object_kind",
    "require_object_kind",
]
