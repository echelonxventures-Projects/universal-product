"""UAUE — canonical declaration reader and repository resolver (UAUE-000001).

This module answers exactly two questions and refuses to answer a third:

1. *What does the canonical declaration say?* — :class:`DeclarationReader` loads
   ``00-MASTER/UAUE-000001/uaue-evolution.json`` and fails closed on anything it cannot read
   as declared. It never repairs, defaults or infers a missing block.
2. *Does what the declaration says resolve against this repository?* — :class:`Substrate`
   measures whether a declared home exists, whether a declared symbol is bound in it, and
   whether a declared gate is wired.

It does not decide what a phase *is*. Composing these measurements into an
:class:`~engine.uaue.model.EvolutionAuthority` is :mod:`engine.uaue.authority`'s job, so the
reader can be exercised against an in-memory document with no branch in the read path.

**Why the symbol reader lives here.** Two existing readers were considered and neither fits.
``platform.coverage.repository.top_level_symbols`` collects only ``def``/``class`` and drops
module-level constants, but the declaration binds constants as symbols (``EVOLUTION_CYCLE``,
``CYCLE_LENGTH``, ``LEDGER_SCHEMA``, ``PIPELINE``, ``DEFAULT_ORDERINGS``, ``EVOLVED``,
``CATEGORY_POLICY``), so it would report bound names as missing; it also lives under
``platform``, which ``engine`` does not import. The ``module_symbols`` copies inside the
``00-MASTER/*/​*_engine.py`` programme engines have the right semantics but are stdlib-only
scripts, not importable modules: importing one would execute another programme's measurement
as a side effect of reading this declaration. :func:`module_symbols` below is therefore the
first importable ``engine``-side implementation of those semantics, and is the one a future
programme engine under ``engine/`` should import rather than copy.
"""

from __future__ import annotations

import ast
import json
import re
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path

from engine.uaue.model import ABSENT, PRESENT, UNREADABLE, EvolutionAuthorityError

#: The repository root, resolved from this file rather than from the working directory, so a
#: reader constructed anywhere reads the same declaration.
REPO_ROOT = Path(__file__).resolve().parents[2]

#: The programme's operational home and its canonical declaration, relative to the repository
#: root. Declared once here; every consumer reaches the declaration through this module.
PROGRAMME_HOME = "00-MASTER/UAUE-000001"
DECLARATION_PATH = f"{PROGRAMME_HOME}/uaue-evolution.json"

#: Every top-level block the declaration must carry. Absence of any one of them is a refusal
#: and never a default: a declaration missing its ``phases`` block describes no loop, and a
#: reader that substituted an empty tuple would report a loop with no phases as a lawful loop.
REQUIRED_KEYS: tuple[str, ...] = (
    "authority_symbols",
    "boundaries",
    "certifications",
    "classifications",
    "discovery_duties",
    "discovery_sources",
    "exit_criteria",
    "history",
    "identity",
    "mandatory",
    "object_kinds",
    "phases",
    "plan_contract",
    "programme",
    "registers",
    "required_fields",
    "self_evolution",
    "stage_authority",
    "unknown_probe",
    "validations",
    "verifications",
)

#: Blocks that must be non-empty lists. A declaration that declares no register, phase,
#: classification or object kind has nothing to reason over and must not resolve.
REQUIRED_NON_EMPTY: tuple[str, ...] = (
    "classifications",
    "object_kinds",
    "phases",
    "registers",
    "required_fields",
)

#: A canonical register filename: a zero-padded ordinal, a name, and the Markdown suffix. The
#: ordinal is what lets a missing or duplicated register be refused instead of renumbered.
REGISTER_FILE = re.compile(r"^(\d{2})-[A-Z0-9-]+\.md$")

#: The prefix of any path inside this programme's own home. A phase that declares a home here
#: would be this register measuring itself, which is the reuse-before-create violation.
OWN_PREFIX = f"{PROGRAMME_HOME}/"

_MAKE_GATE = re.compile(r"^make\s+([A-Za-z0-9_.-]+)$")


def module_symbols(path: Path) -> frozenset[str]:
    """Names bound by a Python module, read without importing it.

    Importing would execute the module and make this measurement depend on the very code it
    measures. Parsing keeps it inert. A module that cannot be parsed binds nothing, which
    surfaces as its declared symbols going missing rather than as an exception escaping a
    measurement.

    Four top-level forms bind a name — ``class``, ``def``, ``async def``, and assignment,
    annotated or plain — because the declaration binds module constants as symbols
    (``EVOLUTION_CYCLE``, ``CYCLE_LENGTH``, ``LEDGER_SCHEMA``, ``PIPELINE``) just as often as
    it binds callables.

    **Class members are included, both bare and qualified.** The declaration binds
    ``from_document`` and ``to_document`` on ``EvolutionLedger``, and ``propose`` and ``apply``
    on the mutation gateway — all of them class members. A top-level-only reader would report
    those bound names as missing and would classify a fully realised phase as
    PARTIALLY_IMPLEMENTED, so member names are collected as ``name`` and as ``Class.name``. The
    bare form is what the declaration's flat symbol lists match against; the qualified form is
    carried so a stricter consumer can demand the owning class without this function being
    written twice. The precision cost is deliberate and bounded: a bare member name is
    satisfied by any class in the module that declares it, which is why the qualified form
    exists for callers that cannot accept that.
    """
    try:
        tree = ast.parse(path.read_text("utf-8", errors="replace"), filename=str(path))
    except (SyntaxError, OSError, ValueError):
        return frozenset()
    names: set[str] = set()

    def bind(node: ast.stmt) -> str | None:
        if isinstance(node, ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef):
            return node.name
        return None

    for node in tree.body:
        bound = bind(node)
        if bound is not None:
            names.add(bound)
            if isinstance(node, ast.ClassDef):
                for member in node.body:
                    member_name = bind(member)
                    if member_name is not None:
                        names.add(member_name)
                        names.add(f"{node.name}.{member_name}")
                    elif isinstance(member, ast.AnnAssign) and isinstance(member.target, ast.Name):
                        names.add(member.target.id)
                        names.add(f"{node.name}.{member.target.id}")
                    elif isinstance(member, ast.Assign):
                        for target in member.targets:
                            if isinstance(target, ast.Name):
                                names.add(target.id)
                                names.add(f"{node.name}.{target.id}")
        elif isinstance(node, ast.Assign):
            names.update(target.id for target in node.targets if isinstance(target, ast.Name))
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            names.add(node.target.id)
    return frozenset(names)


def declared_mapping(value: object, *, what: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise EvolutionAuthorityError(
            f"{what} must be a JSON object", received=type(value).__name__
        )
    return value


def declared_entries(value: object, *, what: str) -> tuple[Mapping[str, object], ...]:
    """``value`` as a tuple of mapping entries, refusing anything else.

    ``str`` is excluded explicitly because it is a ``Sequence`` and would otherwise iterate
    one character at a time, turning a mistyped block into a long list of unusable entries.
    """
    if not isinstance(value, Sequence) or isinstance(value, str | bytes):
        raise EvolutionAuthorityError(f"{what} must be a JSON list", received=type(value).__name__)
    for index, entry in enumerate(value):
        if not isinstance(entry, Mapping):
            raise EvolutionAuthorityError(
                f"every entry of {what} must be a JSON object",
                index=index,
                received=type(entry).__name__,
            )
    return tuple(value)


def declared_text(
    entry: Mapping[str, object], key: str, *, what: str, required: bool = True
) -> str:
    value = entry.get(key)
    if value is None:
        if required:
            raise EvolutionAuthorityError(f"{what} declares no '{key}'", entry=repr(entry)[:120])
        return ""
    if not isinstance(value, str):
        raise EvolutionAuthorityError(
            f"{what} declares a non-string '{key}'", received=type(value).__name__
        )
    if required and not value.strip():
        raise EvolutionAuthorityError(f"{what} declares an empty '{key}'")
    return value


def declared_strings(entry: Mapping[str, object], key: str, *, what: str) -> tuple[str, ...]:
    value = entry.get(key, [])
    if not isinstance(value, Sequence) or isinstance(value, str | bytes):
        raise EvolutionAuthorityError(
            f"{what} declares '{key}' as {type(value).__name__}, not as a list"
        )
    for item in value:
        if not isinstance(item, str):
            raise EvolutionAuthorityError(
                f"every entry of {what} '{key}' must be a string",
                received=type(item).__name__,
            )
    return tuple(value)


def declared_integer(entry: Mapping[str, object], key: str, *, what: str) -> int:
    value = entry.get(key)
    # bool is an int in Python; a boolean ordinal or rank is a declaration error, not a 0/1.
    if not isinstance(value, int) or isinstance(value, bool):
        raise EvolutionAuthorityError(
            f"{what} declares '{key}' as {type(value).__name__}, not as an integer"
        )
    return value


def declared_flag(entry: Mapping[str, object], key: str, *, what: str) -> bool:
    value = entry.get(key)
    if not isinstance(value, bool):
        raise EvolutionAuthorityError(
            f"{what} declares '{key}' as {type(value).__name__}, not as a boolean"
        )
    return value


class DeclarationReader:
    """Reads and structurally validates the canonical evolution declaration.

    Constructed over a *loader* rather than a path, for the reason
    :class:`engine.uckp.resolution.ResolutionReader` is: the on-disk declaration and an
    in-memory document travel the identical read path, so a test that mutates one block is
    exercising production's validation and not a test-only branch. The load is memoised,
    including its failure, so an unusable declaration is refused identically on every read.
    """

    __slots__ = ("_source", "_load", "_memo")

    def __init__(self, source: str, load: Callable[[], object]) -> None:
        self._source = source
        self._load = load
        self._memo: list[Mapping[str, object]] = []

    @classmethod
    def from_document(cls, document: object, *, source: str = "<in-memory>") -> DeclarationReader:
        return cls(source, lambda: document)

    @classmethod
    def from_path(cls, path: Path | str) -> DeclarationReader:
        resolved = Path(path)
        return cls(str(path), lambda: json.loads(resolved.read_text(encoding="utf-8")))

    @classmethod
    def canonical(cls) -> DeclarationReader:
        """A reader over the repository's canonical declaration."""
        return cls.from_path(REPO_ROOT / DECLARATION_PATH)

    @property
    def source(self) -> str:
        return self._source

    def document(self) -> Mapping[str, object]:
        """The validated declaration. Raises rather than returning a partial document."""
        if not self._memo:
            try:
                loaded = self._load()
            except OSError as error:
                raise EvolutionAuthorityError(
                    "the canonical declaration could not be read",
                    source=self._source,
                    detail=f"{type(error).__name__}: {error}",
                ) from error
            except ValueError as error:
                # Covers json.JSONDecodeError. A declaration that is not valid JSON is
                # unusable; guessing at its intent is how a broken authority stays broken.
                raise EvolutionAuthorityError(
                    "the canonical declaration is not valid JSON",
                    source=self._source,
                    detail=str(error),
                ) from error
            document = declared_mapping(loaded, what="the declaration")
            self._validate(document)
            self._memo.append(document)
        return self._memo[0]

    def _validate(self, document: Mapping[str, object]) -> None:
        for key in REQUIRED_KEYS:
            if key not in document:
                raise EvolutionAuthorityError(
                    "the declaration is missing a required block",
                    block=key,
                    source=self._source,
                )
        for key in REQUIRED_NON_EMPTY:
            if not declared_entries(document[key], what=f"the '{key}' block"):
                raise EvolutionAuthorityError(
                    "the declaration carries an empty block, so there is nothing to reason over",
                    block=key,
                    source=self._source,
                )

    def block(self, key: str) -> Mapping[str, object]:
        """One mapping-shaped block of the declaration."""
        return declared_mapping(self.document()[key], what=f"the '{key}' block")

    def entries(self, key: str) -> tuple[Mapping[str, object], ...]:
        """One list-shaped block of the declaration, in declared order."""
        return declared_entries(self.document()[key], what=f"the '{key}' block")


class Substrate:
    """Measures declared paths, symbols and gates against a repository tree.

    Separate from :class:`DeclarationReader` because they answer different questions and fail
    differently: an unreadable declaration is a refusal, whereas an absent home is a
    *finding* — it is exactly what the MISSING classification is for, so measuring it must
    never raise. Symbol reads are memoised per path so a home shared by several phases is
    parsed once and every phase sees the same answer.
    """

    __slots__ = ("_root", "_symbols", "_make_targets")

    def __init__(self, root: Path | None = None) -> None:
        self._root = Path(root) if root is not None else REPO_ROOT
        self._symbols: dict[str, frozenset[str]] = {}
        self._make_targets: frozenset[str] | None = None

    @property
    def root(self) -> Path:
        return self._root

    def state(self, path: str) -> str:
        """:data:`PRESENT`, :data:`ABSENT` or :data:`UNREADABLE` for one declared path."""
        if not path:
            return ABSENT
        try:
            resolved = self._root / path
            if not resolved.exists():
                return ABSENT
        except OSError:
            return UNREADABLE
        return PRESENT

    def resolves(self, path: str) -> bool:
        return self.state(path) == PRESENT

    def symbols(self, path: str) -> frozenset[str]:
        """The names bound by a declared Python home; empty for a non-module."""
        if path not in self._symbols:
            resolved = self._root / path
            if path.endswith(".py") and self.state(path) == PRESENT:
                self._symbols[path] = module_symbols(resolved)
            else:
                self._symbols[path] = frozenset()
        return self._symbols[path]

    def bound_across(self, paths: Sequence[str]) -> frozenset[str]:
        """The union of names bound across several homes.

        Union rather than per-home intersection because a phase's owners are collaborators:
        the declaration binds a symbol to a phase, and a phase is satisfied when one of its
        homes binds it. This is the rule the existing programme engines already apply.
        """
        bound: set[str] = set()
        for path in paths:
            bound |= self.symbols(path)
        return frozenset(bound)

    def make_targets(self) -> frozenset[str]:
        """Every target name declared in the repository Makefile.

        Read by parsing target lines rather than by invoking ``make``: a measurement must not
        execute the thing it measures, and a gate that has to run to be counted as wired
        would make this reader's answer depend on the build succeeding.
        """
        if self._make_targets is None:
            makefile = self._root / "Makefile"
            if not makefile.is_file():
                self._make_targets = frozenset()
            else:
                try:
                    text = makefile.read_text("utf-8", errors="replace")
                except OSError:
                    self._make_targets = frozenset()
                else:
                    self._make_targets = frozenset(
                        match.group(1)
                        for match in re.finditer(r"^([A-Za-z0-9_.-]+)\s*:(?!=)", text, re.MULTILINE)
                    )
        return self._make_targets

    def gate_state(self, command: str) -> tuple[bool, str]:
        """Whether a declared gate is wired, and the reason when it is not.

        Two forms are recognised because two forms are declared: ``make <target>``, wired when
        the Makefile declares that target, and a path such as ``./verify.sh``, wired when the
        file exists and is executable. An unrecognised form is reported as unwired rather than
        assumed to be a shell incantation that works, because an unrecognised gate is one
        nothing in the repository can be shown to discharge.
        """
        stripped = command.strip()
        if not stripped:
            return False, "no gate is declared"
        match = _MAKE_GATE.match(stripped)
        if match is not None:
            target = match.group(1)
            if target in self.make_targets():
                return True, f"Makefile declares target '{target}'"
            return False, f"Makefile declares no target '{target}'"
        candidate = stripped[2:] if stripped.startswith("./") else stripped
        resolved = self._root / candidate
        if resolved.is_file():
            import os

            if os.access(resolved, os.X_OK):
                return True, f"{candidate} exists and is executable"
            return False, f"{candidate} exists but is not executable"
        return False, f"unrecognised gate form and no such executable: {stripped}"

    def entry_point(self, command: str) -> str | None:
        """The repository-relative script a declared gate names, or ``None`` for other forms.

        A gate declared as a path is a *verification entry point*: a pipeline the declaration
        is claiming discharges one of its positions. A gate declared as ``make <target>`` is a
        target, which may belong to any owner. The two are treated differently by the
        integration obligation, so the distinction is drawn once, here, next to the parser that
        already knows both forms.
        """
        stripped = command.strip()
        if not stripped or _MAKE_GATE.match(stripped) is not None:
            return None
        candidate = stripped[2:] if stripped.startswith("./") else stripped
        return candidate if (self._root / candidate).is_file() else None

    def invokes(self, path: str, token: str) -> bool:
        """Whether the executable at ``path`` invokes ``token``.

        Read as text rather than executed, for the reason :meth:`make_targets` gives: a
        measurement must not run the thing it measures. Unreadable is reported as *not*
        invoking, because a gate whose wiring cannot be read is a gate whose wiring is unknown,
        and an unknown wiring must never be presumed present.
        """
        if not path or not token:
            return False
        resolved = self._root / path
        if not resolved.is_file():
            return False
        try:
            return token in resolved.read_text("utf-8", errors="replace")
        except OSError:
            return False


__all__ = [
    "DECLARATION_PATH",
    "OWN_PREFIX",
    "PROGRAMME_HOME",
    "REGISTER_FILE",
    "REPO_ROOT",
    "REQUIRED_KEYS",
    "REQUIRED_NON_EMPTY",
    "DeclarationReader",
    "Substrate",
    "declared_entries",
    "declared_flag",
    "declared_integer",
    "declared_mapping",
    "declared_strings",
    "declared_text",
    "module_symbols",
]
