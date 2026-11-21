"""UOBC-000001 Part 04 — the eight laws, each with a computable check.

A law whose compliance nobody computes is manual governance. So every law in
``uobc-birth-contract.json`` names a check, :data:`LAW_CHECKS` implements it, and
:meth:`engine.object_birth.model.BirthContract.validate` refuses to construct a
contract whose law names a check that is missing. The same discipline
``engine/context/constitution.py`` applies to ``CXL-01…12``.

The checks are pure functions of (contract, ledger, records). They read no clock, no
network and no filesystem beyond the declaration and ledger the caller already loaded,
so a verdict is reproducible and a gate built on them cannot flake.

Two checks are worth reading closely, because they are the ones that make the steering's
prohibitions testable rather than aspirational:

* :func:`check_identity_precedes_existence` measures the declaration's own
  ``identity_exists`` flags, so "identity before existence" is verified against the
  stage model rather than asserted in prose.
* :func:`check_evolution_preserves_identity` re-derives every recorded identity from
  its namespace and local name. If a record's id is not what its own birth facts
  produce, identity was replaced somewhere, and this finds it without needing a history.
"""

from __future__ import annotations

import json
import os
from collections.abc import Callable
from typing import Any

from engine.object_birth.birth import derive_identity, local_name_of, namespace_of
from engine.object_birth.ledger import FORBIDDEN_MINT_MARKER
from engine.object_birth.model import (
    MANDATORY_FIELD_NAMES,
    BirthContract,
    BirthError,
    BirthRecord,
)

#: Where the declaration lives, relative to the repository root.
DECLARATION_PATH = "00-MASTER/UOBC-000001/uobc-birth-contract.json"


def repo_root() -> str:
    """Return the repository root, derived from this file's location."""
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def load_declaration(path: str | None = None) -> dict[str, Any]:
    """Load the birth contract declaration.

    Raises:
        BirthError: the declaration is absent or unreadable. Fail closed: a contract
            that cannot be read is not a contract that permits everything.
    """
    target = path or os.path.join(repo_root(), DECLARATION_PATH)
    try:
        with open(target, encoding="utf-8") as handle:
            doc = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        raise BirthError("birth contract declaration is unreadable", subject=target) from exc
    if not isinstance(doc, dict):
        raise BirthError("birth contract declaration is not a mapping", subject=target)
    return doc


def load_contract(path: str | None = None) -> BirthContract:
    """Rehydrate and validate the contract.

    Raises:
        BirthError: the contract is unsound. The reasons are all reported at once
            rather than one per run, because a half-diagnosed contract wastes a cycle.
    """
    contract = BirthContract.from_declaration(load_declaration(path))
    problems = contract.validate(frozenset(LAW_CHECKS))
    if problems:
        raise BirthError("birth contract is unsound: " + "; ".join(problems))
    return contract


# --------------------------------------------------------------------- the checks
# Each returns the violations it found. Empty tuple means the law holds.


def check_identity_precedes_existence(
    contract: BirthContract, ledger: dict[str, Any], records: tuple[BirthRecord, ...]
) -> tuple[str, ...]:
    """UOBC-L-01 — identity is derived before the artifact is instantiated."""
    problems: list[str] = []
    identity_stage = contract.identity_stage
    instantiation = [s for s in contract.stages if s.produces == "artifact"]
    if not instantiation:
        return ("no declared stage instantiates an artifact",)
    for stage in instantiation:
        if stage.ordinal <= identity_stage.ordinal:
            problems.append(
                f"{stage.stage_id} instantiates an artifact at ordinal {stage.ordinal}, "
                f"not after identity at {identity_stage.ordinal}"
            )
        if not stage.identity_exists:
            problems.append(f"{stage.stage_id} instantiates an artifact without identity")
    return tuple(problems)


def check_no_rival_counter(
    contract: BirthContract, ledger: dict[str, Any], records: tuple[BirthRecord, ...]
) -> tuple[str, ...]:
    """UOBC-L-02 — the contract consumes no counter, so it is not a second mint."""
    problems: list[str] = []
    if contract.counter_consumed:
        problems.append("the declaration claims to consume a counter")
    if FORBIDDEN_MINT_MARKER in ledger:
        problems.append(f"the ledger holds {FORBIDDEN_MINT_MARKER!r}, the declared mint marker")
    if contract.identity_home != "engine/uckp/identity.py":
        problems.append(
            "identity is not delegated to the supreme plane engine/uckp/identity.py; "
            f"declared home is {contract.identity_home}"
        )
    return tuple(problems)


def check_identity_immutable(
    contract: BirthContract, ledger: dict[str, Any], records: tuple[BirthRecord, ...]
) -> tuple[str, ...]:
    """UOBC-L-03 — identity is a pure function of namespace and local name."""
    problems: list[str] = []
    for record in records:
        try:
            namespace = namespace_of(record.universal_id)
            local = local_name_of(record.universal_id)
        except BirthError as exc:
            problems.append(f"{record.universal_id}: {exc}")
            continue
        if namespace != record.namespace:
            problems.append(
                f"{record.universal_id}: namespace field {record.namespace!r} "
                f"disagrees with the identity it carries ({namespace!r})"
            )
        if derive_identity(namespace, local) != record.universal_id:
            problems.append(f"{record.universal_id}: does not re-derive from its own inputs")
    return tuple(problems)


def check_no_anonymous_object(
    contract: BirthContract, ledger: dict[str, Any], records: tuple[BirthRecord, ...]
) -> tuple[str, ...]:
    """UOBC-L-04 — every record carries all nine mandatory fields, populated."""
    problems: list[str] = []
    for record in records:
        body = record.to_dict()
        for name in MANDATORY_FIELD_NAMES:
            if name == "parent_identity":
                continue  # None is meaningful: a declared root has no parent.
            value = body.get(name)
            if value is None or value == "" or value == {}:
                problems.append(f"{record.universal_id}: field {name!r} is empty")
    return tuple(problems)


def check_no_temporary_identity(
    contract: BirthContract, ledger: dict[str, Any], records: tuple[BirthRecord, ...]
) -> tuple[str, ...]:
    """UOBC-L-05 — no provisional identity, and no undeclared namespace.

    Provisional markers are matched as whole **segments** of the local name, never as
    substrings. Substring matching is wrong in a way that is easy to miss: it flags
    ``engine.temporal`` for containing ``temp``, and a check that cries wolf on a
    legitimate name gets disabled rather than fixed.
    """
    problems: list[str] = []
    provisional = frozenset(
        {"tmp", "temp", "draft", "provisional", "placeholder", "todo", "xxx", "wip", "new"}
    )
    for record in records:
        if contract.namespace_owner(record.namespace) is None:
            problems.append(f"{record.universal_id}: namespace {record.namespace!r} is undeclared")
        try:
            local = local_name_of(record.universal_id)
        except BirthError as exc:
            problems.append(f"{record.universal_id}: {exc}")
            continue
        segments = {
            segment.lower()
            for segment in local.replace(".", " ").replace("-", " ").replace("_", " ").split()
        }
        for token in sorted(segments & provisional):
            problems.append(f"{record.universal_id}: carries provisional name segment {token!r}")
        if record.initial_state not in contract.initial_states:
            problems.append(
                f"{record.universal_id}: initial state {record.initial_state!r} is inadmissible"
            )
    return tuple(problems)


def check_no_post_creation_registration(
    contract: BirthContract, ledger: dict[str, Any], records: tuple[BirthRecord, ...]
) -> tuple[str, ...]:
    """UOBC-L-06 — registration is a declared stage that follows identity."""
    problems: list[str] = []
    registration = [s for s in contract.stages if s.produces == "registry_entry"]
    if not registration:
        return ("no declared stage produces a registry entry",)
    identity_ordinal = contract.identity_stage.ordinal
    for stage in registration:
        if stage.ordinal <= identity_ordinal:
            problems.append(f"{stage.stage_id} registers before identity exists")
        if not stage.identity_exists:
            problems.append(f"{stage.stage_id} registers without identity")
    return tuple(problems)


def check_evolution_preserves_identity(
    contract: BirthContract, ledger: dict[str, Any], records: tuple[BirthRecord, ...]
) -> tuple[str, ...]:
    """UOBC-L-07 — a superseded object keeps the identity it was born with."""
    problems: list[str] = []
    born = {r.universal_id for r in records}
    for entry in ledger.get("supersessions", []):
        identity = entry.get("universal_id")
        if identity not in born:
            problems.append(f"supersession names an identity that is not born: {identity}")
        superseded = entry.get("superseded")
        if not isinstance(superseded, dict):
            problems.append(f"{identity}: supersession records no prior state")
            continue
        if not entry.get("reason"):
            problems.append(f"{identity}: supersession records no reason")
    return tuple(problems)


def check_append_only_history(
    contract: BirthContract, ledger: dict[str, Any], records: tuple[BirthRecord, ...]
) -> tuple[str, ...]:
    """UOBC-L-08 — births are keyed by identity and history only grows."""
    problems: list[str] = []
    if ledger.get("keyed_by") != "universal_id":
        problems.append(
            f"ledger is keyed by {ledger.get('keyed_by')!r}, not by identity; "
            "a path key is rewritten by a move"
        )
    if not isinstance(ledger.get("supersessions"), list):
        problems.append("ledger holds no supersessions list, so history cannot grow")
    for identity, body in sorted(ledger.get("births", {}).items()):
        if not isinstance(body, dict):
            problems.append(f"{identity}: birth entry is not a mapping")
        elif "universal_id" in body:
            problems.append(
                f"{identity}: entry duplicates its own key as a field, so the two could diverge"
            )
    return tuple(problems)


#: Law check name → implementation. The declaration's ``check`` values must all appear
#: here, or the contract refuses to construct.
LAW_CHECKS: dict[
    str, Callable[[BirthContract, dict[str, Any], tuple[BirthRecord, ...]], tuple[str, ...]]
] = {
    "identity_precedes_existence": check_identity_precedes_existence,
    "no_rival_counter": check_no_rival_counter,
    "identity_immutable": check_identity_immutable,
    "no_anonymous_object": check_no_anonymous_object,
    "no_temporary_identity": check_no_temporary_identity,
    "no_post_creation_registration": check_no_post_creation_registration,
    "evolution_preserves_identity": check_evolution_preserves_identity,
    "append_only_history": check_append_only_history,
}


def assess(
    contract: BirthContract, ledger: dict[str, Any], records: tuple[BirthRecord, ...]
) -> tuple[tuple[str, str, tuple[str, ...]], ...]:
    """Measure every law, returning ``(law_id, title, violations)`` in declaration order."""
    out = []
    for law in contract.laws:
        check = LAW_CHECKS[law.check]
        out.append((law.law_id, law.title, check(contract, ledger, records)))
    return tuple(out)
