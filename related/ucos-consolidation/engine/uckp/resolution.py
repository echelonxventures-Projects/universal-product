"""UCKP Layer Zero — Universal Resolution Reader (Articles 1, 15).

`00-BOOK/DATA/constitutional-authority-alignment.json` answers, six times over, one
recurring bounded question: *two instruments appear to rival each other — do they?* Each
answer lives in a top-level `*_resolution` section, and each has the same shape: a model,
the standings it recognises, and the test that would falsify the recognition. Not one of
them grants a right or creates an authority; every one **recognises** a standing that
measurement already shows to hold (`PHASE-UCF-012 § 6.3`).

Until this module, four of those six sections had no machine reader at all, and the two
that did were read by `uga_engine.py` — a stdlib-only process that cannot import Layer
Zero and therefore cannot see the object population. Nothing under `engine/` opened the
file: :data:`~engine.uckp.alignment.ALIGNMENT_BINDING_PATH` was declared as a string and
embedded as object metadata, never resolved.

This module is that reader, and it is deliberately **general**. It knows what a
resolution section *is* — a named, mapping-shaped answer in a constitutional binding —
and nothing about what any particular one *says*. A reader built for one section would
have to be built again for the next, which is how a file with six answers acquires six
loaders; :meth:`ResolutionReader.names` therefore discovers sections by their declared
suffix rather than from a list kept here, so a seventh section is readable the moment it
is written and this module never learns its name.

**Fail-closed, and the distinction that makes it useful.** Three states, never two: a
section that is `PRESENT`, one the document does not declare (`ABSENT`), and a document
or section that could not be read as declared (`UNREADABLE`). Collapsing the last two
would let a deleted file report exactly what an undeclared section reports, so a consumer
could not tell "nothing is claimed here" from "the claim could not be read" — and the
second must never be allowed to pass as the first (`PHASE-UCF-012 § 12.1`).

The reader reports; it never validates. Whether a section's *content* is lawful is
:func:`~engine.uckp.alignment.verify_binding`'s question, and answering it here would put
the binding's contract in two places.
"""

from __future__ import annotations

import json
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path

from engine.uckp.alignment import ALIGNMENT_BINDING_PATH
from engine.uckp.errors import UCKPValidationError

#: The suffix every constitutional resolution section is declared under. Discovery is by
#: this suffix rather than by an enumeration, so the reader does not have to be edited
#: when a section is added — which is the one edit a hardcoded list would guarantee.
RESOLUTION_SUFFIX = "_resolution"

#: The three states a read can reach. ``UNREADABLE`` exists so that an unreadable source
#: can never be mistaken for a source that declares nothing.
PRESENT = "present"
ABSENT = "absent"
UNREADABLE = "unreadable"

#: The repository root, resolved from this file rather than from the working directory,
#: so a reader constructed anywhere reads the same document.
_REPO_ROOT = Path(__file__).resolve().parents[2]


def _list_entries(value: object) -> tuple[object, ...]:
    """``value`` as a tuple of JSON list entries; empty for anything else.

    A ``str`` is a ``Sequence`` and would iterate one character at a time, so the
    exclusion is what stops a mistyped field from being read as a list of entries. The
    same guard :mod:`engine.uckp.alignment` applies to the binding's top-level lists,
    applied here to the lists inside a section.
    """
    if isinstance(value, Sequence) and not isinstance(value, str | bytes):
        return tuple(value)
    return ()


@dataclass(frozen=True, slots=True)
class Resolution:
    """One constitutional resolution section, as read.

    ``body`` is the section verbatim — empty unless ``state`` is :data:`PRESENT`, so a
    consumer that forgets to check the state reads nothing rather than something stale.
    ``detail`` says why, for the two states that are not :data:`PRESENT`, so a finding
    can quote the reason instead of asserting one.
    """

    name: str
    state: str
    source: str
    body: Mapping[str, object] = field(default_factory=dict)
    detail: str = ""

    @property
    def present(self) -> bool:
        return self.state == PRESENT

    @property
    def readable(self) -> bool:
        """False only when the source could not be read as declared."""
        return self.state != UNREADABLE

    def entries(self, key: str) -> tuple[Mapping[str, object], ...]:
        """The mapping entries of one list inside the section, in declared order.

        Every existing section carries its recognised standings as a list of mappings
        (`surfaces`, `authorities`, `namespaces`, `axes`, `projections`), so this is the
        access every consumer of this reader needs. Non-mapping entries are dropped here
        and are visible to a consumer as a count shortfall against ``key``'s raw length,
        which is what lets a caller report a malformed entry rather than crash on it.
        """
        return tuple(
            entry for entry in _list_entries(self.body.get(key)) if isinstance(entry, Mapping)
        )

    def declared(self, key: str) -> int:
        """How many entries ``key`` declares, mappings or not — the count to compare."""
        return len(_list_entries(self.body.get(key)))

    def cite(self) -> str:
        """The section and where it was read from, as a finding may quote it."""
        return f"{self.name} ({self.state}) in {self.source}"

    def to_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "state": self.state,
            "source": self.source,
            "detail": self.detail,
        }


class ResolutionReader:
    """Reads `*_resolution` sections from a constitutional binding document.

    Constructed over a *loader* rather than a path so that the same class serves the
    on-disk binding and an in-memory document with no branch anywhere inside it: a test
    that needs a particular section exercises the identical read path production uses.

    The document is loaded once per reader, lazily, and the outcome is memoised —
    including a failure, so an unreadable source is reported identically on every read
    rather than re-attempted at each call.
    """

    __slots__ = ("_source", "_load", "_memo")

    def __init__(self, source: str, load: Callable[[], object]) -> None:
        self._source = source
        self._load = load
        self._memo: list[tuple[Mapping[str, object] | None, str]] = []

    @classmethod
    def from_document(cls, document: object, *, source: str = "<in-memory>") -> ResolutionReader:
        """A reader over an already-loaded document."""
        return cls(source, lambda: document)

    @classmethod
    def from_path(cls, path: Path | str) -> ResolutionReader:
        """A reader over a JSON document on disk. Read-only; never writes or creates."""
        resolved = Path(path)
        return cls(str(path), lambda: json.loads(resolved.read_text(encoding="utf-8")))

    @property
    def source(self) -> str:
        """Where this reader reads from, as a finding may cite it."""
        return self._source

    def _document(self) -> tuple[Mapping[str, object] | None, str]:
        if not self._memo:
            try:
                loaded = self._load()
            except (OSError, ValueError) as error:
                # ValueError covers json.JSONDecodeError; OSError covers absent,
                # unreadable and undecodable files. Both are the same answer to a
                # consumer — the claim could not be read — and neither is a pass.
                self._memo.append((None, f"{type(error).__name__}: {error}"))
            else:
                if isinstance(loaded, Mapping):
                    self._memo.append((loaded, ""))
                else:
                    self._memo.append((None, "the document is not a mapping"))
        return self._memo[0]

    def names(self) -> tuple[str, ...]:
        """Every resolution section the document declares, sorted.

        Empty when the document is unreadable — a caller that needs to distinguish that
        from a document declaring none reads a section and inspects its state.
        """
        document, _ = self._document()
        if document is None:
            return ()
        return tuple(
            sorted(
                key for key in document if isinstance(key, str) and key.endswith(RESOLUTION_SUFFIX)
            )
        )

    def read(self, name: str) -> Resolution:
        """One section by name. Never raises for a missing or malformed document.

        The name must be a resolution section name. That is a guard against this
        becoming a general accessor for the binding: the binding's other 35 top-level
        keys are :func:`~engine.uckp.alignment.verify_binding`'s contract, and a second
        way to reach them would be a second reader of the same contract.
        """
        if not name.endswith(RESOLUTION_SUFFIX):
            raise UCKPValidationError("not a resolution section name", section=name)
        document, detail = self._document()
        if document is None:
            return Resolution(name, UNREADABLE, self._source, detail=detail)
        body = document.get(name)
        if body is None:
            return Resolution(
                name,
                ABSENT,
                self._source,
                detail=f"{self._source} declares no {name}",
            )
        if not isinstance(body, Mapping):
            return Resolution(
                name,
                UNREADABLE,
                self._source,
                detail=f"{name} is declared as {type(body).__name__}, not as a mapping",
            )
        return Resolution(name, PRESENT, self._source, body)


def binding_reader() -> ResolutionReader:
    """A reader over the repository's constitutional authority alignment binding.

    The path is :data:`~engine.uckp.alignment.ALIGNMENT_BINDING_PATH` — the one the
    module that owns the binding's contract already declares — resolved against the
    repository root. Not cached: a reader memoises its own load, and a process-wide cache
    would make a reader's answer depend on when it was first constructed.
    """
    return ResolutionReader.from_path(_REPO_ROOT / ALIGNMENT_BINDING_PATH)


__all__ = [
    "ABSENT",
    "PRESENT",
    "RESOLUTION_SUFFIX",
    "UNREADABLE",
    "Resolution",
    "ResolutionReader",
    "binding_reader",
]
