"""UAPF-000001 — the open vocabulary primitive.

Every classification UAPF recognises — pipeline type, plugin role, event category, policy
kind, evidence kind, escalation reason — is an **open, append-only vocabulary** rather
than a closed enumeration in code. This is the mechanism behind Unlimited Pipeline Types,
Unlimited Execution Units and Unlimited Future Expansion: admitting one more term is a
registration made from a declaration, and no module in this package needs to change.

Openness is not laxity. A vocabulary is still **fail-closed**: a term that was never
registered is rejected, so a typo can never silently become a new classification. It is
also append-only — re-registering a term is refused rather than silently redefining it,
because a term is a governed classification and a second meaning for one term would make
every record that carries it ambiguous.

The primitive is pure: no wall-clock, no I/O, deterministic iteration order (sorted), and
a content-addressed fingerprint, so a vocabulary's state is itself reproducible evidence.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass, field
from platform.foundation.contracts import content_hash
from platform.universal_pipeline.errors import UniversalPipelineError
from typing import Any

#: The recorded vocabulary format.
VOCABULARY_FORMAT = "ucos-uapf-vocabulary/1.0.0"

#: A vocabulary term is a dotted / hyphenated lower-case token (e.g. ``pipeline.registered``).
_TERM_RE = re.compile(r"^[a-z0-9]+(?:[-.][a-z0-9]+)*$")


@dataclass(frozen=True, slots=True)
class VocabularyTerm:
    """An immutable declaration of one registered vocabulary term."""

    vocabulary: str
    term: str
    description: str = ""
    attributes: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "attributes", dict(self.attributes))

    def attribute(self, name: str, default: Any = None) -> Any:
        """Return a declared attribute of this term (``default`` when absent)."""
        return self.attributes.get(name, default)

    def to_dict(self) -> dict[str, Any]:
        return {
            "vocabulary": self.vocabulary,
            "term": self.term,
            "description": self.description,
            "attributes": dict(self.attributes),
        }


class Vocabulary:
    """An open, append-only, fail-closed vocabulary of governed classification terms."""

    __slots__ = ("_error", "_name", "_terms")

    def __init__(self, name: str, *, error: type[UniversalPipelineError]) -> None:
        if not isinstance(name, str) or not _TERM_RE.match(name):
            raise UniversalPipelineError("vocabulary name must be a lower-case token", name=name)
        if not (isinstance(error, type) and issubclass(error, UniversalPipelineError)):
            raise UniversalPipelineError("a vocabulary must raise a UAPF error subclass", name=name)
        self._name = name
        self._error = error
        self._terms: dict[str, VocabularyTerm] = {}

    @property
    def name(self) -> str:
        """The vocabulary's own name (the classification it governs)."""
        return self._name

    def register(
        self,
        term: str,
        *,
        description: str = "",
        attributes: Mapping[str, Any] | None = None,
    ) -> VocabularyTerm:
        """Register one term (unbounded extension; refuses a duplicate)."""
        if not isinstance(term, str) or not _TERM_RE.match(term):
            raise self._error(
                "term must be a lower-case dotted or hyphenated token",
                vocabulary=self._name,
                term=term,
            )
        if term in self._terms:
            raise self._error(
                "term already registered in this vocabulary",
                vocabulary=self._name,
                term=term,
            )
        declared = VocabularyTerm(
            vocabulary=self._name,
            term=term,
            description=description,
            attributes=attributes or {},
        )
        self._terms[term] = declared
        return declared

    def register_many(self, declarations: Any) -> tuple[VocabularyTerm, ...]:
        """Register a sequence of term declarations, skipping terms already registered.

        Declarations may be plain strings or mappings carrying ``term`` plus optional
        ``description`` / ``attributes``. Terms already registered are *skipped* rather
        than refused, so loading the same declaration catalogue twice is idempotent — the
        property a discovery pass needs in order to be safely repeatable.
        """
        admitted: list[VocabularyTerm] = []
        for declaration in declarations:
            if isinstance(declaration, str):
                term, description, attributes = declaration, "", {}
            elif isinstance(declaration, Mapping):
                term = declaration.get("term", "")
                description = str(declaration.get("description", ""))
                raw = declaration.get("attributes", {})
                if not isinstance(raw, Mapping):
                    raise self._error(
                        "term attributes must be a mapping",
                        vocabulary=self._name,
                        term=str(term),
                    )
                attributes = dict(raw)
            else:
                raise self._error(
                    "a term declaration must be a string or a mapping", vocabulary=self._name
                )
            if term in self._terms:
                continue
            admitted.append(self.register(term, description=description, attributes=attributes))
        return tuple(admitted)

    def require(self, term: str) -> VocabularyTerm:
        """Return a registered term, else raise (fail-closed)."""
        try:
            return self._terms[term]
        except KeyError:
            raise self._error(
                "unregistered term",
                vocabulary=self._name,
                term=term,
                registered=len(self._terms),
            ) from None

    def require_all(self, terms: Any) -> tuple[str, ...]:
        """Return ``terms`` (deduplicated, sorted) once every one is registered."""
        resolved = sorted({self.require(term).term for term in terms})
        return tuple(resolved)

    def get(self, term: str) -> VocabularyTerm | None:
        """Return a registered term, or ``None`` when it is not registered."""
        return self._terms.get(term)

    def terms(self) -> tuple[str, ...]:
        """Every registered term, sorted."""
        return tuple(sorted(self._terms))

    def declarations(self) -> tuple[VocabularyTerm, ...]:
        """Every registered term declaration, sorted by term."""
        return tuple(self._terms[term] for term in sorted(self._terms))

    def terms_where(self, attribute: str, value: Any = True) -> tuple[str, ...]:
        """Every registered term whose ``attribute`` equals ``value``, sorted.

        Lets behaviour be *declared* on a term instead of branched on in code — for
        example, which event categories automatically generate execution units.
        """
        return tuple(
            term.term for term in self.declarations() if term.attribute(attribute) == value
        )

    def __contains__(self, term: object) -> bool:
        return term in self._terms

    def __len__(self) -> int:
        return len(self._terms)

    def to_dict(self) -> dict[str, Any]:
        return {
            "vocabulary_format": VOCABULARY_FORMAT,
            "vocabulary": self._name,
            "term_count": len(self._terms),
            "terms": [term.to_dict() for term in self.declarations()],
        }

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())


__all__ = ["VOCABULARY_FORMAT", "Vocabulary", "VocabularyTerm"]
