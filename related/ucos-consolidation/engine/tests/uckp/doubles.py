"""Test doubles shared by the UCKP suite.

Two of them, and both exist for the same reason: several UCKP components are defences
in depth. The registry refuses an object whose seal is broken, so a *reasoner* that
reports broken seals can never see one through registration — and a branch that never
executes is a claim rather than a check. These doubles put the component in front of the
condition it says it detects, without weakening the admission rules that make the
condition unreachable in production.

They live here rather than in each test module because there is one of each. A second
copy of :class:`Proxy` would be exactly the duplication the law under test forbids.
"""

from __future__ import annotations

from collections.abc import Iterable, Iterator

from engine.uckp.graph import UniversalKnowledgeGraph
from engine.uckp.registry import UniversalKnowledgeRegistry
from engine.uckp.ucko import UCKO
from engine.uckp.vocabulary import VocabularyRegistry


class Proxy:
    """Answers exactly like ``base`` except where an override is supplied.

    Overrides are matched by attribute name, so a method is replaced by a callable and
    a plain attribute by a value — the same shape the real component exposes. Everything
    not overridden is the real behaviour, which is what makes a reported finding
    attributable to the one thing the test changed.

    Special methods (``len``, ``in``) are resolved on the type by the interpreter and so
    are *not* proxied; use :class:`RegistryView` where those are needed.
    """

    def __init__(self, base: object, **overrides: object) -> None:
        self.__dict__["_base"] = base
        self.__dict__["_overrides"] = overrides

    def __getattr__(self, name: str) -> object:
        overrides = self.__dict__["_overrides"]
        if name in overrides:
            return overrides[name]
        return getattr(self.__dict__["_base"], name)


class RegistryView:
    """A registry that holds objects the real registry would have refused.

    The full read surface of :class:`~engine.uckp.registry.UniversalKnowledgeRegistry`
    that the intelligence and governance layers consult, over a caller-supplied tuple of
    objects. Read-only by construction: there is no ``register``, so no test can mistake
    this for a second admission path.
    """

    def __init__(
        self,
        objects: Iterable[UCKO],
        *,
        vocabularies: VocabularyRegistry,
    ) -> None:
        self._objects = tuple(objects)
        self._vocabularies = vocabularies

    # --- lookup -----------------------------------------------------------------

    def objects(self) -> tuple[UCKO, ...]:
        return self._objects

    def ids(self) -> tuple[str, ...]:
        return tuple(sorted(obj.ucko_id for obj in self._objects))

    def get(self, ucko_id: str) -> UCKO | None:
        for obj in self._objects:
            if obj.ucko_id == str(ucko_id):
                return obj
        return None

    def __contains__(self, ucko_id: object) -> bool:
        return self.get(str(ucko_id)) is not None

    def __len__(self) -> int:
        return len(self._objects)

    def __iter__(self) -> Iterator[UCKO]:
        return iter(self._objects)

    # --- authority and meaning --------------------------------------------------

    def root_ids(self) -> tuple[str, ...]:
        return tuple(
            obj.ucko_id for obj in self._objects if obj.authority.derives_from in ("", obj.ucko_id)
        )

    def duplicate_semantics(self) -> tuple[tuple[str, ...], ...]:
        by_digest: dict[str, list[str]] = {}
        for obj in self._objects:
            by_digest.setdefault(obj.semantic_digest(), []).append(obj.ucko_id)
        return tuple(tuple(sorted(ids)) for _, ids in sorted(by_digest.items()) if len(ids) > 1)

    def vocabularies(self) -> VocabularyRegistry:
        return self._vocabularies

    def graph(self) -> UniversalKnowledgeGraph:
        return UniversalKnowledgeGraph.from_objects(self._objects)


def registry_of(*objects: UCKO, vocabularies: VocabularyRegistry) -> UniversalKnowledgeRegistry:
    """A real registry holding ``objects`` — the lawful path, for contrast."""
    registry = UniversalKnowledgeRegistry(vocabularies=vocabularies)
    registry.register_all(objects)
    return registry


__all__ = ["Proxy", "RegistryView", "registry_of"]
