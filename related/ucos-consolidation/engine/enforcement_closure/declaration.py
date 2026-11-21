"""UEC-000001 Part 3 — the declaration. Loaded, validated, enforced, reported, certified.

FIVE-STAGE LIFECYCLE, WITH NO SILENT FIELD. Every field this module reads is validated here,
reaches a law in ``contract.py``, appears in the rendered report, and participates in
``digest_payload``. That is not a style preference — it is the direct remedy for a measured
defect. Three declaration documents in this repository (``ceu-declaration.json``,
``urr-declaration.json``, ``ucxi-declaration.json``) have ZERO code consumers, and
``ucon-declaration.json:5`` names ``ucxi-declaration.json`` as its constitutional superior, so
one authority chain in this repository terminates in a document no code reads.
``UEC-L-07``/``UEC-L-13`` measure that class; this module refuses to join it.

DIGEST COMPLETENESS BY INVERSION. ``digest_payload`` returns the WHOLE validated document, with
exclusions enumerated in ``DIGEST_EXCLUSIONS`` and each carrying a stated reason. The opposite
convention — include a chosen projection, document nothing — is what produced the measured
defect in ``engine/construct/declaration.py:550-571``, where ten of eleven keys collapse to bare
identifier lists. Executed against that surface: flipping ``blocking`` on ``UCON-L-01``,
rewriting rule ``UCON-DR-01``'s assigned disposition, and zeroing an evidence floor all leave
``declaration_digest`` at ``192c63af…`` byte-identical, while
``engine/construct/contract.py:1018`` makes the OPEN/CLOSED verdict depend on ``blocking``.

Here the burden is reversed: a field is in the identity unless someone wrote down why not, and
``test_enforcement_closure.py`` proves by mutation that every semantically meaningful edit MOVES
the digest. A test that only asserts a digest is *stable* cannot detect this defect class, which
is exactly what ``engine/tests/unit/test_construct_foundation.py:263-265,922-930`` asserts.
"""

from __future__ import annotations

import json
import os
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from engine.enforcement_closure.discovery import repo_root
from engine.enforcement_closure.model import (
    DeclarationError,
    Law,
    Rule,
    Withdrawal,
)

DECLARATION_RELATIVE = "00-MASTER/UEC-000001/uec-declaration.json"

#: Fields excluded from certification identity, each with the reason it cannot change a verdict.
#: The list is short by design and is itself validated: ``_check_digest_exclusions`` refuses an
#: exclusion that is not present in the document, so a stale exclusion cannot quietly widen.
DIGEST_EXCLUSIONS: Mapping[str, str] = {
    "source": (
        "the path the declaration was read from. A digest that changed with the reader would "
        "not be a digest of the declaration."
    ),
    "$comment": "prose. Cannot reach a law; changing it cannot change a verdict.",
}


def _require(document: Mapping[str, Any], key: str) -> Any:
    if key not in document or document[key] in (None, "", [], {}):
        raise DeclarationError(f"declaration section {key!r} is absent or empty")
    return document[key]


def _rows(value: Any, *, section: str) -> tuple[Mapping[str, Any], ...]:
    if not isinstance(value, Sequence) or isinstance(value, str) or not value:
        raise DeclarationError(f"declaration section {section!r} must be a non-empty list")
    for row in value:
        if not isinstance(row, Mapping):
            raise DeclarationError(f"every row of {section!r} must be an object")
    return tuple(value)


def _text(row: Mapping[str, Any], key: str, *, where: str) -> str:
    value = row.get(key)
    if not isinstance(value, str) or not value.strip():
        raise DeclarationError(f"{where} declares no {key!r}")
    return value


@dataclass(frozen=True)
class Declaration:
    """The governed expectation, against which discovery is compared."""

    artifact_id: str
    version: str
    authority: str
    principle: str
    rules: tuple[Rule, ...]
    governed: tuple[Mapping[str, Any], ...]
    withdrawals: tuple[Withdrawal, ...]
    withdrawal_cap: int
    laws: tuple[Law, ...]
    ratchet: Mapping[str, int]
    corpus_plane: Mapping[str, Any]
    self_coverage: Mapping[str, Any]
    #: The command CLAUDE.md names as the one repository-standard entry point. Declared so
    #: UEC-L-15 measures reach against a NAMED lane rather than a constant in the engine —
    #: a repository that renames it says so here.
    canonical_entry_point: str
    testpaths: tuple[str, ...]
    refusal_witness: Mapping[str, Any]
    gate: Mapping[str, Any]
    document: Mapping[str, Any]
    source: str

    # --- derived views the laws consume --------------------------------------------------

    @property
    def governed_keys(self) -> frozenset[str]:
        return frozenset(f"{row['kind']}::{row['identity']}" for row in self.governed)

    @property
    def withdrawn_keys(self) -> frozenset[str]:
        return frozenset(f"{item.kind}::{item.identity}" for item in self.withdrawals)

    def rule(self, rule_id: str) -> Rule:
        for rule in self.rules:
            if rule.rule_id == rule_id:
                return rule
        raise DeclarationError(f"no discovery rule {rule_id!r} is declared")

    def digest_payload(self) -> dict[str, Any]:
        """The whole validated declaration, minus the enumerated exclusions.

        Inclusion is the default. Every key of the loaded document reaches this payload unless
        ``DIGEST_EXCLUSIONS`` names it and states why it cannot change a verdict.
        """
        return {
            key: value
            for key, value in sorted(self.document.items())
            if key not in DIGEST_EXCLUSIONS
        }


def _parse_rule(row: Mapping[str, Any]) -> Rule:
    where = f"discovery rule {row.get('rule_id', '<unnamed>')!r}"
    floor = row.get("floor")
    if not isinstance(floor, int) or isinstance(floor, bool):
        raise DeclarationError(f"{where} declares no integer floor")
    if floor <= 0:
        raise DeclarationError(
            f"{where} declares floor {floor}, but a floor of zero is not a floor: it would "
            "permit the rule to match nothing and still be satisfied, which is the vacuity "
            "this programme exists to refuse"
        )
    return Rule(
        rule_id=_text(row, "rule_id", where=where),
        kind=_text(row, "kind", where=where),
        strategy=_text(row, "strategy", where=where),
        floor=floor,
        pattern=str(row.get("pattern") or ""),
        root=str(row.get("root") or ""),
        owner=_text(row, "owner", where=where),
    )


def _parse_law(row: Mapping[str, Any]) -> Law:
    where = f"law {row.get('law_id', '<unnamed>')!r}"
    blocking = row.get("blocking")
    if not isinstance(blocking, bool):
        raise DeclarationError(
            f"{where} does not declare `blocking` as a boolean. Whether a law refuses is the "
            "field that decides the verdict; leaving it implicit is how a law becomes advisory "
            "without anyone deciding that it should be"
        )
    return Law(
        law_id=_text(row, "law_id", where=where),
        check=_text(row, "check", where=where),
        statement=_text(row, "statement", where=where),
        blocking=blocking,
        concern=_text(row, "concern", where=where),
    )


def _parse_withdrawal(row: Mapping[str, Any]) -> Withdrawal:
    where = f"withdrawal {row.get('identity', '<unnamed>')!r}"
    return Withdrawal(
        identity=_text(row, "identity", where=where),
        kind=_text(row, "kind", where=where),
        owner=_text(row, "owner", where=where),
        reason=_text(row, "reason", where=where),
        date=_text(row, "date", where=where),
    )


def parse(document: Mapping[str, Any], *, source: str) -> Declaration:
    """Load and validate. Every section is required; a missing section is a FAULT."""
    if not isinstance(document, Mapping):
        raise DeclarationError("the declaration must be a JSON object")

    rules = tuple(
        _parse_rule(row)
        for row in _rows(_require(document, "discovery_rules"), section="discovery_rules")
    )
    seen_rules = [rule.rule_id for rule in rules]
    if len(set(seen_rules)) != len(seen_rules):
        raise DeclarationError("two discovery rules share a rule_id")

    governed = _rows(_require(document, "governed_enforcement"), section="governed_enforcement")
    known_rules = {rule.rule_id for rule in rules}
    known_kinds = {rule.kind for rule in rules}
    for row in governed:
        where = f"governed entry {row.get('identity', '<unnamed>')!r}"
        _text(row, "identity", where=where)
        kind = _text(row, "kind", where=where)
        rule_id = _text(row, "rule_id", where=where)
        _text(row, "owner", where=where)
        if rule_id not in known_rules:
            raise DeclarationError(
                f"{where} names discovery rule {rule_id!r}, which is not declared"
            )
        if kind not in known_kinds:
            raise DeclarationError(
                f"{where} declares kind {kind!r}, which no discovery rule locates"
            )
    keys = [f"{row['kind']}::{row['identity']}" for row in governed]
    if len(set(keys)) != len(keys):
        raise DeclarationError("the governed inventory names the same artifact twice")

    withdrawal_block = document.get("withdrawals") or {}
    if not isinstance(withdrawal_block, Mapping):
        raise DeclarationError("declaration section 'withdrawals' must be an object")
    cap = withdrawal_block.get("cap")
    if not isinstance(cap, int) or isinstance(cap, bool) or cap < 0:
        raise DeclarationError(
            "declaration section 'withdrawals.cap' must be a non-negative integer"
        )
    entries = withdrawal_block.get("entries") or []
    if not isinstance(entries, Sequence) or isinstance(entries, str):
        raise DeclarationError("declaration section 'withdrawals.entries' must be a list")
    withdrawals = tuple(_parse_withdrawal(row) for row in entries)

    laws = tuple(_parse_law(row) for row in _rows(_require(document, "laws"), section="laws"))
    law_ids = [law.law_id for law in laws]
    if len(set(law_ids)) != len(law_ids):
        raise DeclarationError("two laws share a law_id")

    ratchet_raw = _require(document, "ratchet")
    if not isinstance(ratchet_raw, Mapping):
        raise DeclarationError("declaration section 'ratchet' must be an object")
    ratchet: dict[str, int] = {}
    for key, value in ratchet_raw.items():
        if key.startswith("$"):
            continue
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            raise DeclarationError(f"ratchet entry {key!r} must be a non-negative integer")
        ratchet[key] = value

    testpaths = tuple(str(item) for item in _rows_of_str(document, "testpaths"))

    declaration = Declaration(
        artifact_id=str(_require(document, "artifact_id")),
        version=str(_require(document, "version")),
        authority=str(_require(document, "authority")),
        principle=str(_require(document, "principle")),
        rules=rules,
        governed=governed,
        withdrawals=withdrawals,
        withdrawal_cap=cap,
        laws=laws,
        ratchet=ratchet,
        corpus_plane=dict(_require(document, "corpus_plane")),
        self_coverage=dict(_require(document, "self_coverage")),
        canonical_entry_point=str(
            (document.get("programme") or {}).get("canonical_entry_point") or "verify.sh"
        ),
        testpaths=testpaths,
        refusal_witness=dict(_require(document, "refusal_witness")),
        gate=dict(_require(document, "gate")),
        document=dict(document),
        source=source,
    )
    _check_digest_exclusions(declaration)
    return declaration


def _rows_of_str(document: Mapping[str, Any], key: str) -> tuple[str, ...]:
    value = _require(document, key)
    if not isinstance(value, Sequence) or isinstance(value, str):
        raise DeclarationError(f"declaration section {key!r} must be a list of strings")
    for item in value:
        if not isinstance(item, str) or not item.strip():
            raise DeclarationError(f"every entry of {key!r} must be a non-empty string")
    return tuple(value)


def _check_digest_exclusions(declaration: Declaration) -> None:
    """A digest exclusion must name a field the document actually carries.

    A stale exclusion is how an exclusion list silently widens: the field is renamed, the
    exclusion keeps matching nothing, and the next field to take that name is excluded by
    accident rather than by decision.
    """
    for key in DIGEST_EXCLUSIONS:
        if key == "source":
            continue
        if key not in declaration.document:
            raise DeclarationError(
                f"digest exclusion {key!r} names no field the declaration carries; an exclusion "
                "that matches nothing cannot be justified and may silently widen"
            )


def load(path: str | None = None, *, repository: str | None = None) -> Declaration:
    root = repository or repo_root()
    relative = path or DECLARATION_RELATIVE
    absolute = relative if os.path.isabs(relative) else os.path.join(root, relative)
    try:
        with open(absolute, encoding="utf-8") as handle:
            document = json.load(handle)
    except FileNotFoundError as exc:
        raise DeclarationError(f"the UEC declaration does not resolve: {relative}") from exc
    except json.JSONDecodeError as exc:
        raise DeclarationError(f"the UEC declaration is not valid JSON: {relative}: {exc}") from exc
    return parse(document, source=relative)
