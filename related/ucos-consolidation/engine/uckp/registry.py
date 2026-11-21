"""UCKP Layer Zero — the Universal Knowledge Registry (Articles 2, 3, 8, 18).

The registry is where "exists exactly once" stops being a principle and becomes a
refusal. Three admissions are possible and no fourth:

    * **registered** — nothing in the universe carried this identity or this meaning.
    * **reused** — the identical object is already homed; the registry returns the home
      instead of making a second one (Article 18).
    * **refused** — a *different* object claims an existing identity, or an existing
      meaning under a new identity. Both raise. A registry that resolves a clash by
      picking a winner has created two authorities and hidden one of them.

Discovery is automatic (Article 8). :meth:`UniversalKnowledgeRegistry.discover` walks
packages and admits every provider it finds, so a new capability becomes part of the
universe by *existing* — by exposing ``ucko_objects()`` or ``UCKO_OBJECTS`` — and never
by being added to a list somewhere. There is no enumeration to forget to update, which
is the only reliable way to keep a growing universe complete.
"""

from __future__ import annotations

import importlib
import pkgutil
from collections.abc import Iterable, Iterator, Sequence
from dataclasses import dataclass
from typing import Any, Protocol, runtime_checkable

from engine.uckp.canonical import content_hash
from engine.uckp.errors import (
    DuplicateAuthorityError,
    LawViolation,
    UnknownObjectError,
)
from engine.uckp.graph import UniversalKnowledgeGraph
from engine.uckp.ucko import UCKO
from engine.uckp.vocabulary import DEFAULT_VOCABULARIES, VocabularyRegistry

#: The module attribute and callable a provider exposes to self-register.
PROVIDER_CALLABLE = "ucko_objects"
PROVIDER_ATTRIBUTE = "UCKO_OBJECTS"

#: Admission outcomes. Closed by design.
REGISTERED = "registered"
REUSED = "reused"


@runtime_checkable
class KnowledgeProvider(Protocol):
    """Anything that can contribute canonical objects to the universe."""

    provider_id: str

    def ucko_objects(self) -> Iterable[UCKO]:  # pragma: no cover - protocol
        ...


@dataclass(frozen=True, slots=True)
class Admission:
    """The record of one admission decision."""

    outcome: str
    ucko_id: str
    provider_id: str
    semantic_digest: str

    @property
    def created_home(self) -> bool:
        return self.outcome == REGISTERED

    def to_dict(self) -> dict[str, str]:
        return {
            "outcome": self.outcome,
            "ucko_id": self.ucko_id,
            "provider_id": self.provider_id,
            "semantic_digest": self.semantic_digest,
        }


@dataclass(frozen=True, slots=True)
class DiscoveryReport:
    """What automatic discovery found, so discovery itself is auditable."""

    roots: tuple[str, ...]
    modules_scanned: int
    providers_found: tuple[str, ...]
    objects_admitted: int
    failures: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, object]:
        return {
            "roots": list(self.roots),
            "modules_scanned": self.modules_scanned,
            "providers_found": list(self.providers_found),
            "objects_admitted": self.objects_admitted,
            "failures": list(self.failures),
        }


class UniversalKnowledgeRegistry:
    """The single home of every Universal Constitutional Knowledge Object."""

    __slots__ = ("_objects", "_by_semantics", "_admissions", "_providers", "_vocabularies")

    def __init__(
        self,
        objects: Iterable[UCKO] = (),
        *,
        vocabularies: VocabularyRegistry | None = None,
    ) -> None:
        self._objects: dict[str, UCKO] = {}
        self._by_semantics: dict[str, str] = {}
        self._admissions: list[Admission] = []
        self._providers: dict[str, int] = {}
        self._vocabularies = vocabularies or DEFAULT_VOCABULARIES
        for obj in objects:
            self.register(obj)

    # --- admission --------------------------------------------------------------

    def register(self, obj: UCKO, *, provider_id: str = "direct") -> Admission:
        """Admit an object, or refuse. The whole of Articles 2, 3 and 18 lives here."""
        obj.require_integrity()
        obj.require_lawful(self._vocabularies)
        ucko_id = obj.ucko_id
        semantic = obj.semantic_digest()
        existing = self._objects.get(ucko_id)
        if existing is not None:
            if existing.content_sha256 == obj.content_sha256:
                admission = Admission(REUSED, ucko_id, provider_id, semantic)
                self._admissions.append(admission)
                self._providers[provider_id] = self._providers.get(provider_id, 0) + 1
                return admission
            raise DuplicateAuthorityError(
                "a different object claims an existing identity",
                ucko_id=ucko_id,
                existing_sha256=existing.content_sha256,
                offered_sha256=obj.content_sha256,
            )
        claimed_by = self._by_semantics.get(semantic)
        if claimed_by is not None:
            raise DuplicateAuthorityError(
                "this knowledge already exists under another identity",
                semantic_digest=semantic,
                canonical_home=claimed_by,
                offered=ucko_id,
            )
        self._objects[ucko_id] = obj
        self._by_semantics[semantic] = ucko_id
        self._providers[provider_id] = self._providers.get(provider_id, 0) + 1
        admission = Admission(REGISTERED, ucko_id, provider_id, semantic)
        self._admissions.append(admission)
        return admission

    def register_all(
        self, objects: Iterable[UCKO], *, provider_id: str = "direct"
    ) -> tuple[Admission, ...]:
        return tuple(self.register(obj, provider_id=provider_id) for obj in objects)

    def replace(self, obj: UCKO) -> UCKO:
        """Replace an object with a lawful successor carrying the identical identity.

        Replacement is how an object *evolves*; it is not how a second object is
        smuggled in. The identity must already exist and must be unchanged, so the
        canonical home stays the same home (Article 5).
        """
        obj.require_integrity()
        obj.require_lawful(self._vocabularies)
        existing = self.require(obj.ucko_id)
        existing.identity.require_unchanged(obj.identity)
        previous_semantic = existing.semantic_digest()
        semantic = obj.semantic_digest()
        if semantic != previous_semantic:
            claimed_by = self._by_semantics.get(semantic)
            if claimed_by is not None and claimed_by != obj.ucko_id:
                raise DuplicateAuthorityError(
                    "the replacement would duplicate knowledge already homed elsewhere",
                    semantic_digest=semantic,
                    canonical_home=claimed_by,
                )
            self._by_semantics.pop(previous_semantic, None)
            self._by_semantics[semantic] = obj.ucko_id
        self._objects[obj.ucko_id] = obj
        return obj

    # --- reuse before create ----------------------------------------------------

    def locate(self, concept: str, definition: str) -> UCKO | None:
        """Find the canonical home of a meaning before anything is created (Article 18)."""
        from engine.uckp.values import SemanticIdentity

        digest = SemanticIdentity(concept=concept, definition=definition).digest()
        return self.by_semantic_digest(digest)

    def by_semantic_digest(self, digest: str) -> UCKO | None:
        ucko_id = self._by_semantics.get(str(digest))
        return self._objects.get(ucko_id) if ucko_id else None

    # --- lookup -----------------------------------------------------------------

    def get(self, ucko_id: str) -> UCKO | None:
        return self._objects.get(str(ucko_id))

    def require(self, ucko_id: str) -> UCKO:
        obj = self.get(ucko_id)
        if obj is None:
            raise UnknownObjectError("no such knowledge object", ucko_id=str(ucko_id))
        return obj

    def __contains__(self, ucko_id: object) -> bool:
        return str(ucko_id) in self._objects

    def __len__(self) -> int:
        return len(self._objects)

    def __iter__(self) -> Iterator[UCKO]:
        return iter(self.objects())

    def ids(self) -> tuple[str, ...]:
        return tuple(sorted(self._objects))

    def objects(self) -> tuple[UCKO, ...]:
        return tuple(self._objects[key] for key in self.ids())

    def by_category(self, category: str) -> tuple[UCKO, ...]:
        return tuple(o for o in self.objects() if o.taxonomy.category == str(category))

    def by_kind(self, kind: str) -> tuple[UCKO, ...]:
        return tuple(o for o in self.objects() if o.taxonomy.kind == str(kind))

    def by_authority(self, tier: str) -> tuple[UCKO, ...]:
        return tuple(o for o in self.objects() if o.authority.tier == str(tier))

    def by_owner(self, owner: str) -> tuple[UCKO, ...]:
        return tuple(o for o in self.objects() if o.ownership.owner == str(owner))

    def by_lifecycle(self, stage: str) -> tuple[UCKO, ...]:
        return tuple(o for o in self.objects() if o.lifecycle == str(stage))

    def search(self, text: str) -> tuple[UCKO, ...]:
        """Keyword search over self-published metadata only (Article 8)."""
        needle = str(text).strip().casefold()
        if not needle:
            return ()
        hits = []
        for obj in self.objects():
            haystack = " ".join(
                (
                    obj.ucko_id,
                    obj.semantic_identity.concept,
                    obj.semantic_identity.definition,
                    obj.taxonomy.kind,
                    obj.taxonomy.category,
                    *obj.discovery.keywords,
                    *obj.taxonomy.tags,
                )
            ).casefold()
            if needle in haystack:
                hits.append(obj)
        return tuple(hits)

    # --- authority --------------------------------------------------------------

    def root_ids(self) -> tuple[str, ...]:
        """Identities whose authority derives from themselves."""
        return tuple(
            key for key in self.ids() if self._objects[key].authority.derives_from in ("", key)
        )

    def require_single_root(self) -> str:
        """Fail closed unless exactly one constitutional root exists (Article 1)."""
        roots = self.root_ids()
        if len(roots) != 1:
            raise LawViolation(
                "the universe must have exactly one constitutional root",
                roots=list(roots),
            )
        return roots[0]

    def authority_of(self, ucko_id: str) -> tuple[str, ...]:
        return self.graph().authority_chain(ucko_id)

    def duplicate_semantics(self) -> tuple[tuple[str, ...], ...]:
        """Meanings homed more than once.

        Always empty by construction: :meth:`register` refuses the second home. The
        method exists so the invariant is *measured* on real data rather than trusted,
        which is the difference between a proof and a comment.
        """
        by_digest: dict[str, list[str]] = {}
        for obj in self.objects():
            by_digest.setdefault(obj.semantic_digest(), []).append(obj.ucko_id)
        return tuple(tuple(sorted(ids)) for _, ids in sorted(by_digest.items()) if len(ids) > 1)

    # --- graph ------------------------------------------------------------------

    def graph(self) -> UniversalKnowledgeGraph:
        return UniversalKnowledgeGraph.from_objects(self.objects())

    # --- automatic discovery ----------------------------------------------------

    def providers(self) -> tuple[str, ...]:
        return tuple(sorted(self._providers))

    def admissions(self) -> tuple[Admission, ...]:
        return tuple(self._admissions)

    def discover(self, *roots: str) -> DiscoveryReport:
        """Admit every provider reachable from ``roots`` (Article 8).

        A module participates by exposing ``ucko_objects()`` or ``UCKO_OBJECTS``.
        Import failures are *recorded*, not raised: a universe that cannot be
        enumerated because one optional dependency is missing would make discovery
        hostage to unrelated code, and the failures list keeps the omission visible
        rather than silent.
        """
        scanned = 0
        found: list[str] = []
        failures: list[str] = []
        admitted = 0
        for root in roots or ("engine.uckp",):
            for module_name in self._walk(root, failures):
                scanned += 1
                try:
                    module = importlib.import_module(module_name)
                except Exception as exc:  # noqa: BLE001 - recorded, never silent
                    failures.append(f"{module_name}: {exc}")
                    continue
                objects = self._provider_objects(module)
                if objects is None:
                    continue
                found.append(module_name)
                for obj in objects:
                    self.register(obj, provider_id=module_name)
                    admitted += 1
        return DiscoveryReport(
            roots=tuple(roots or ("engine.uckp",)),
            modules_scanned=scanned,
            providers_found=tuple(sorted(found)),
            objects_admitted=admitted,
            failures=tuple(sorted(failures)),
        )

    @staticmethod
    def _walk(root: str, failures: list[str]) -> tuple[str, ...]:
        try:
            package = importlib.import_module(root)
        except Exception as exc:  # noqa: BLE001 - recorded, never silent
            failures.append(f"{root}: {exc}")
            return ()
        names = [root]
        paths = getattr(package, "__path__", None)
        if paths:
            for info in pkgutil.walk_packages(paths, prefix=f"{root}."):
                names.append(info.name)
        return tuple(sorted(names))

    @staticmethod
    def _provider_objects(module: Any) -> Sequence[UCKO] | None:
        factory = getattr(module, PROVIDER_CALLABLE, None)
        if callable(factory):
            return tuple(factory())
        declared = getattr(module, PROVIDER_ATTRIBUTE, None)
        if declared is not None:
            return tuple(declared)
        return None

    # --- self-description -------------------------------------------------------

    def describe(self) -> dict[str, Any]:
        """The machine-readable description of the whole universe (Article 8)."""
        return {
            "schema": "ucos-uckp-registry-description",
            "version": "1.0.0",
            "counts": self.counts(),
            "providers": list(self.providers()),
            "roots": list(self.root_ids()),
            "categories": sorted({o.taxonomy.category for o in self.objects()}),
            "kinds": sorted({o.taxonomy.kind for o in self.objects()}),
            "owners": sorted({o.ownership.owner for o in self.objects()}),
            "vocabularies": list(self._vocabularies.vocabulary_ids()),
        }

    def vocabularies(self) -> VocabularyRegistry:
        return self._vocabularies

    def counts(self) -> dict[str, int]:
        graph = self.graph()
        return {
            "objects": len(self._objects),
            "providers": len(self._providers),
            "admissions": len(self._admissions),
            "edges": len(graph.edges()),
            "dangling_edges": len(graph.dangling()),
            "duplicate_semantics": len(self.duplicate_semantics()),
        }

    def to_document(self) -> dict[str, Any]:
        return {
            "schema": "ucos-uckp-knowledge-universe",
            "version": "1.0.0",
            "counts": self.counts(),
            "seal": self.seal(),
            "objects": [self._objects[key].to_dict() for key in self.ids()],
        }

    def seal(self) -> str:
        """The content digest of the whole universe."""
        return content_hash(
            [{"id": key, "sha256": self._objects[key].content_sha256} for key in self.ids()]
        )


__all__ = [
    "PROVIDER_ATTRIBUTE",
    "PROVIDER_CALLABLE",
    "REGISTERED",
    "REUSED",
    "Admission",
    "DiscoveryReport",
    "KnowledgeProvider",
    "UniversalKnowledgeRegistry",
]
