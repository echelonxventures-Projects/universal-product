"""The impact substrate: the repository's own dependency edges, inverted.

No new graph is built here. Everything is read from surfaces that already exist and
are already gate-measured:

* ``00-MASTER/UCOS-UGA-001/01-EXECUTABLE-OBJECT-REGISTRY.json`` — 4 797 objects, each
  with ``dependencies`` resolved by ``uga_engine.py::python_imports`` to
  repository-relative paths. 816 are ``TEST_OBJECT`` and 774 carry edges.
* ``00-MASTER/UCOS-UGA-001/04-RELATIONSHIP-GRAPH.json`` — the same edge set flattened,
  used for the ``owned_by`` / ``produces`` relations.

Building a second dependency graph would be a second answer to a question the
repository already answers, which ``OBS-INV-13``'s own rationale calls out: "a second
copy of the dependency graph would be a second answer to the same question."

The one thing this module adds is **direction**. The registry stores forward edges
(object → what it imports). Impact analysis needs the reverse (object → who imports
it), and the reverse of a 1-hop edge set is only useful transitively, so
:meth:`ImpactGraph.dependents_of` closes it.
"""

from __future__ import annotations

import json
import os
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any

#: The registries this engine reads. Neither is written.
EXECUTABLE_REGISTRY = "00-MASTER/UCOS-UGA-001/01-EXECUTABLE-OBJECT-REGISTRY.json"
RELATIONSHIP_GRAPH = "00-MASTER/UCOS-UGA-001/04-RELATIONSHIP-GRAPH.json"

#: Object classes that carry executable dependency edges.
CODE_CLASSES = frozenset({"EXECUTABLE_OBJECT", "TEST_OBJECT", "TOOLING_OBJECT"})


class ImpactError(Exception):
    """The impact substrate could not be read, so no scope can be computed.

    Raised rather than degraded: an impact engine that silently returns an empty
    affected set would report "nothing to verify", which is the most dangerous
    possible failure mode for a verification selector.
    """


def repo_root() -> str:
    """Return the repository root, derived from this file's location."""
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


@dataclass(frozen=True, slots=True)
class ObjectRecord:
    """One object as the registry records it."""

    path: str
    universal_id: str
    object_class: str
    owner: str
    dependencies: tuple[str, ...]
    produces: tuple[str, ...]
    evidence_class: str
    certification_status: str
    content_hash: str | None

    @property
    def is_test(self) -> bool:
        return self.object_class == "TEST_OBJECT"


@dataclass(slots=True)
class ImpactGraph:
    """The dependency substrate, indexed for reverse traversal.

    ``dependents`` is the inversion that makes impact analysis possible:
    ``dependents[x]`` is every object that imports ``x`` directly.
    """

    objects: dict[str, ObjectRecord] = field(default_factory=dict)
    dependents: dict[str, set[str]] = field(default_factory=lambda: defaultdict(set))
    owners: dict[str, set[str]] = field(default_factory=lambda: defaultdict(set))

    @property
    def tests(self) -> tuple[str, ...]:
        """Every test object path, sorted."""
        return tuple(sorted(p for p, o in self.objects.items() if o.is_test))

    def record(self, path: str) -> ObjectRecord | None:
        """The registry record for ``path``, or None if unregistered."""
        return self.objects.get(path)

    def dependents_of(self, paths: set[str], *, transitive: bool = True) -> set[str]:
        """Every object affected by a change to ``paths``.

        Breadth-first over the inverted edge set. The seeds are excluded from the
        result unless they are reachable from each other, so the caller can
        distinguish "what changed" from "what that change reaches".
        """
        seen: set[str] = set()
        frontier = {p for p in paths if p in self.dependents or p in self.objects}
        while frontier:
            nxt: set[str] = set()
            for path in frontier:
                for dependent in self.dependents.get(path, ()):
                    if dependent not in seen:
                        seen.add(dependent)
                        nxt.add(dependent)
            if not transitive:
                break
            frontier = nxt
        return seen

    def owned_by(self, owner: str) -> tuple[str, ...]:
        """Every path attributed to ``owner``, sorted."""
        return tuple(sorted(self.owners.get(owner, ())))


def _as_tuple(value: Any) -> tuple[str, ...]:
    if not isinstance(value, list):
        return ()
    return tuple(str(v) for v in value)


def load_graph(root: str | None = None) -> ImpactGraph:
    """Load the impact substrate from the committed UGA registries.

    Raises:
        ImpactError: a registry is absent or unusable. Fail closed — see
            :class:`ImpactError`.
    """
    base = root or repo_root()
    target = os.path.join(base, EXECUTABLE_REGISTRY)
    try:
        with open(target, encoding="utf-8") as handle:
            doc = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        raise ImpactError(f"executable object registry is unreadable: {target}") from exc
    entries = doc.get("entries")
    if not isinstance(entries, list) or not entries:
        raise ImpactError(f"executable object registry holds no entries: {target}")

    graph = ImpactGraph()
    for entry in entries:
        if not isinstance(entry, dict) or "path" not in entry:
            continue
        record = ObjectRecord(
            path=str(entry["path"]),
            universal_id=str(entry.get("universal_id", "")),
            object_class=str(entry.get("object_class", "")),
            owner=str(entry.get("owner", "")),
            dependencies=_as_tuple(entry.get("dependencies")),
            produces=_as_tuple(entry.get("produces")),
            evidence_class=str(entry.get("evidence_class", "")),
            certification_status=str(entry.get("certification_status", "")),
            content_hash=entry.get("content_hash"),
        )
        graph.objects[record.path] = record
        graph.owners[record.owner].add(record.path)
        for dependency in record.dependencies:
            graph.dependents[dependency].add(record.path)

    if not graph.dependents:
        raise ImpactError(
            "the registry carries no dependency edges, so impact cannot be computed; "
            "the registry is regenerated by UCOS-UGA-001 under AUTHORIZED identity "
            "allocation (REG-AUTO-001), which is irreversible — obtain that "
            "authorization rather than invoking allocation to clear this error"
        )
    return graph
