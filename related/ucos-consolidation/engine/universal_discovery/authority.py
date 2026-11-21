"""UCOS-OMEGA-001 Part 4 (Ω-2) — authority, derived. A total function, so NONE is unreachable.

THE PATTERN THIS REPLACES.

    UEC governs engines
    REG governs tools
    UCI governs inventory

Three true sentences that do not compose. Each names a scope, so a subsystem outside all three
scopes has no owner, and the repository measured 570 such files. Adding a fourth sentence fixes
the fourth subsystem and nothing else — the cost of governance grows with the number of
subsystems, which is the definition of a model that does not scale.

Ω-2 inverts it. Authority is not assigned TO a file by a list that names it; authority is
DERIVED FROM the file by a chain of rules whose last link is unconditional. The consequence is
the property that matters: a subsystem nobody has written yet already has an owner, because the
rule that will name its owner does not mention it.

THE CHAIN, IN ORDER. First match wins, and the order is load-bearing — a self-declaration must
beat an inherited one, or a module could be quietly re-owned by whoever imports it.

  Ω-A-01  DECLARATION      the artifact declares its own authority in an ``*_AUTHORITY`` constant
  Ω-A-02  CONTRACT         a governance declaration names this path as its subject
  Ω-A-03  ANCESTRY-HOME    it lives inside a programme home, and the home IS the authority
  Ω-A-04  EXECUTION GRAPH  an orchestration plane invokes it, so the invoker's plane owns it
  Ω-A-05  GOVERNANCE GRAPH every module that imports it agrees on an owner, so it inherits that
  Ω-A-06  ANCESTRY-MODULE  the capability package is the unit of custody in the code tree
  Ω-A-07  REPOSITORY       unconditional. The repository owns what nothing else claims.

``AUTHORITY = NONE (DERIVED TRUTH)`` IS NOT AN ABSENT OWNER. Roughly every engine in this
repository opens with that line, and it is a disclaimer of *legislative* authority — the module
declares that it makes no law — not a statement that nobody owns it. Reading it as an absent
owner would have inverted the measurement: the most carefully governed files in the repository
would have counted as the ungoverned ones. Ω-A-01 therefore ignores derived-truth tokens and
lets the chain continue, which is why ``_DISCLAIMED`` exists.

THE ONLY ROUTE TO ``authority = ""`` IS A DECLARED TRANSIENT. Ω-2 permits exactly one, and it is
declared in ``[tool.ucos.omega] transient`` with a reason, because an artifact that does not
persist cannot acquire a durable owner and pretending otherwise would be a fabricated fact.
"""

from __future__ import annotations

import json
import os
import re
from collections.abc import Mapping

from engine.universal_discovery.discovery import is_importable_name
from engine.universal_discovery.model import OmegaError

RULE_DECLARATION = "Ω-A-01"
RULE_CONTRACT = "Ω-A-02"
RULE_ANCESTRY_HOME = "Ω-A-03"
RULE_EXECUTION = "Ω-A-04"
RULE_GOVERNANCE = "Ω-A-05"
RULE_ANCESTRY_MODULE = "Ω-A-06"
RULE_REPOSITORY = "Ω-A-07"
RULE_TRANSIENT = "Ω-A-00"

#: The authority of last resort. Unconditional, which is what makes the function total.
REPOSITORY_AUTHORITY = "UCOS-REPOSITORY-ROOT"

#: A module-level constant whose name ends ``AUTHORITY``. Discovered by pattern, exactly as
#: ``00-MASTER/UCOS-UCAF-001/ucaf-authority.json`` already declares authority tokens are to be
#: found — this reads the same population rather than opening a second one.
AUTHORITY_CONSTANT = re.compile(
    r"""(?m)^(?P<symbol>[A-Z][A-Z0-9_]*AUTHORITY)\s*(?::[^=\n]+)?=\s*["'](?P<token>[^"']*)["']"""
)

#: Tokens that DISCLAIM legislative authority rather than assert ownership. A file carrying one
#: of these is making the derived-truth declaration this repository uses throughout, so the chain
#: must continue past it instead of recording an owner the file explicitly refused to be.
_DISCLAIMED = re.compile(r"(?i)^\s*(none\b|derived[\s-]*truth|engineering[\s-]*execution)")

#: A programme home: the directory IS the authority, which is the rule UGA-000001 already
#: declares as TOTAL. The pattern is over SHAPE — a two-segment governance tree — so a programme
#: created tomorrow is matched by the rule that was written today.
PROGRAMME_HOME = re.compile(r"^(?P<home>00-[A-Z]+)/(?P<programme>[^/]+)/")


def declared_authority(source: str) -> tuple[str, str]:
    """``(token, symbol)`` for the first asserted authority constant, or ``("", "")``.

    Reads only module-level assignments, so an authority mentioned inside a function body or a
    docstring is not mistaken for the file's own claim.
    """
    for match in AUTHORITY_CONSTANT.finditer(source):
        token = match.group("token").strip()
        if not token or _DISCLAIMED.match(token):
            continue
        return token, match.group("symbol")
    return "", ""


def _programme_of(path: str) -> str:
    match = PROGRAMME_HOME.match(path)
    return match.group("programme") if match else ""


class ContractIndex:
    """``path -> programme`` for every path a governance declaration names as its subject.

    DISCOVERED, NOT LISTED, in both directions: the declarations are found by walking the
    governance homes, and the paths inside them are read from the declaration's own bytes. A
    programme that starts claiming a new path is honoured on the commit that claims it.

    Bounded on purpose. Only ``*-declaration.json`` and ``*-authority.json`` are read, and only
    string values that look like repository paths are indexed, so this cannot become a scan of
    every byte in ``00-MASTER`` — which would make the authority of one file depend on the size
    of another.
    """

    #: Declaration file shapes. A shape, not a list of names.
    FILENAMES = re.compile(r"(?i)-(declaration|authority|bindings)\.json$")

    def __init__(self, root: str) -> None:
        self.by_path: dict[str, str] = {}
        self.declarations: tuple[str, ...] = ()
        found: list[str] = []
        for home in sorted(os.listdir(root)) if os.path.isdir(root) else []:
            if not re.fullmatch(r"00-[A-Z]+", home):
                continue
            home_absolute = os.path.join(root, home)
            if not os.path.isdir(home_absolute):
                continue
            for programme in sorted(os.listdir(home_absolute)):
                programme_absolute = os.path.join(home_absolute, programme)
                if not os.path.isdir(programme_absolute):
                    continue
                for name in sorted(os.listdir(programme_absolute)):
                    if not self.FILENAMES.search(name):
                        continue
                    relative = f"{home}/{programme}/{name}"
                    found.append(relative)
                    self._index(os.path.join(programme_absolute, name), programme)
        self.declarations = tuple(found)

    def _index(self, absolute: str, programme: str) -> None:
        try:
            with open(absolute, encoding="utf-8") as handle:
                document = json.load(handle)
        except (OSError, ValueError):
            # A declaration this package cannot parse is somebody else's refusal — every
            # programme gate already validates its own. Skipping it here loses precision and
            # never loses totality, because the ancestry rules below are unconditional.
            return
        for value in _strings(document):
            if value.endswith(".py") and "/" in value and not value.startswith(("http", "$")):
                self.by_path.setdefault(value.lstrip("./"), programme)

    def programme_for(self, path: str) -> str:
        return self.by_path.get(path, "")


def _strings(node: object, depth: int = 0) -> list[str]:
    """Every string in a JSON document. Depth-bounded so a cyclic or absurd shape terminates."""
    if depth > 12:
        return []
    if isinstance(node, str):
        return [node]
    if isinstance(node, dict):
        out: list[str] = []
        for key, value in node.items():
            if isinstance(key, str) and key.endswith(".py"):
                out.append(key)
            out.extend(_strings(value, depth + 1))
        return out
    if isinstance(node, list):
        out = []
        for item in node:
            out.extend(_strings(item, depth + 1))
        return out
    return []


def derive_authority(
    path: str,
    *,
    source: str,
    contracts: ContractIndex,
    invoking_planes: Mapping[str, frozenset[str]],
    importer_authorities: Mapping[str, frozenset[str]],
    transient: Mapping[str, str],
) -> tuple[str, str]:
    """``(authority, rule)`` for one artifact. TOTAL — the last rule is unconditional.

    The signature is the argument for the design: every input is a measurement over the
    discovered population, and none of them is a table keyed on this file. Change the file's
    location and rules Ω-A-03 and Ω-A-06 answer differently about the NAME of the owner while
    still answering; change nothing and there is no input that could make this return no owner.
    """
    if path in transient:
        return "", RULE_TRANSIENT

    token, _symbol = declared_authority(source)
    if token:
        return token, RULE_DECLARATION

    claimed = contracts.programme_for(path)
    if claimed:
        return claimed, RULE_CONTRACT

    programme = _programme_of(path)
    if programme:
        return programme, RULE_ANCESTRY_HOME

    planes = invoking_planes.get(path, frozenset())
    if planes:
        return f"{REPOSITORY_AUTHORITY}::{'+'.join(sorted(planes))}", RULE_EXECUTION

    inherited = importer_authorities.get(path, frozenset())
    if len(inherited) == 1:
        return next(iter(inherited)), RULE_GOVERNANCE

    parts = path.split("/")
    if len(parts) > 2 and is_importable_name(parts[0]) and is_importable_name(parts[1]):
        return f"{parts[0]}.{parts[1]}", RULE_ANCESTRY_MODULE
    if len(parts) == 2 and is_importable_name(parts[0]):
        return parts[0], RULE_ANCESTRY_MODULE

    return REPOSITORY_AUTHORITY, RULE_REPOSITORY


def assert_total(records: Mapping[str, tuple[str, str]], transient: Mapping[str, str]) -> None:
    """Ω-2's success criterion, asserted rather than reported: authority coverage is 100%.

    A file with no authority and no transient declaration is refused BY NAME. Reporting a
    percentage here instead would be the defect this package exists to end — a number that can
    drift while nothing fails.
    """
    orphans = sorted(
        path
        for path, (authority, _rule) in records.items()
        if not authority and path not in transient
    )
    if orphans:
        raise OmegaError(
            "these artifacts resolved to authority = NONE and are not declared transient, so "
            "the derivation chain is not total: " + ", ".join(orphans[:20])
        )
