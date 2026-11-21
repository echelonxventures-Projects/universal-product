"""UCCFA-000001 — the declaration, rehydrated, and the six laws measured over it.

WHY THE LAWS READ FILES RATHER THAN TRUSTING THE DECLARATION. A declaration that asserted its
own correctness would certify nothing: the whole claim of this programme is that every
coordinate it names is one ``01-WORKING/ONTOLOGY-REGISTER.md`` already carries and that its
standing is the standing the ratification record grants. So the register and the supersession
record are read, and a coordinate the register does not carry is refused as invented.

THE TWO SOURCES ARE MEASURED SEPARATELY AND ON PURPOSE. ``UCCFA-L-04`` measures the eight-term
Universal Equation and ``UCCFA-L-06`` the nine dimensions of ``LAW Ω∞-000``; the two differ by
BEING, which is the axiom above reality rather than a term of it. Deriving one from the other
would make a single transcription error unfalsifiable in both.
"""

from __future__ import annotations

import json
import os
import re
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from typing import Any


class CoordinateAlignmentError(RuntimeError):
    """The declaration is unusable, which is a FAULT rather than a verdict."""


def repo_root() -> str:
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def declaration_path(root: str | None = None) -> str:
    """The one declaration this programme reads.

    Named here rather than passed in, because the path IS the binding: a programme that would
    measure whichever document it was handed is not the owner of any particular one.
    """
    return os.path.join(root or repo_root(), "00-MASTER", "UCCFA-000001", "uccfa-declaration.json")


def load_declaration(path: str | None = None) -> dict[str, Any]:
    target = path or declaration_path()
    try:
        with open(target, encoding="utf-8") as handle:
            document = json.load(handle)
    except FileNotFoundError as exc:
        raise CoordinateAlignmentError(f"declaration absent: {target}") from exc
    except json.JSONDecodeError as exc:
        raise CoordinateAlignmentError(f"declaration is not valid JSON: {exc}") from exc
    if not isinstance(document, dict):
        raise CoordinateAlignmentError("declaration is not an object")
    return document


@dataclass(frozen=True, slots=True)
class CoordinateContract:
    """The whole declaration, rehydrated and structurally usable."""

    artifact_id: str
    name: str
    version: str
    authority: str
    principle: str
    source: Mapping[str, Any]
    coordinates: tuple[Mapping[str, Any], ...]
    ratified_standing: tuple[Mapping[str, Any], ...]
    superseded: Mapping[str, Any]
    omega_law: Mapping[str, Any]
    laws: tuple[Mapping[str, Any], ...]

    @classmethod
    def of(cls, document: Mapping[str, Any]) -> CoordinateContract:
        def text(key: str) -> str:
            value = document.get(key)
            if not isinstance(value, str) or not value.strip():
                raise CoordinateAlignmentError(f"declaration states no {key}")
            return value

        def rows(key: str) -> tuple[Mapping[str, Any], ...]:
            value = document.get(key)
            if not isinstance(value, list) or not value:
                raise CoordinateAlignmentError(f"declaration carries no {key}")
            return tuple(value)

        def obj(key: str) -> Mapping[str, Any]:
            value = document.get(key)
            if not isinstance(value, dict) or not value:
                raise CoordinateAlignmentError(f"declaration carries no {key}")
            return value

        return cls(
            artifact_id=text("artifact_id"),
            name=text("name"),
            version=text("version"),
            authority=text("authority"),
            principle=text("principle"),
            source=obj("ontology_source"),
            coordinates=rows("coordinate_binding"),
            ratified_standing=rows("ratified_standing"),
            superseded=obj("superseded_root_element"),
            omega_law=obj("omega_law_binding"),
            laws=rows("laws"),
        )


def load_contract(path: str | None = None) -> CoordinateContract:
    return CoordinateContract.of(load_declaration(path))


def _read(root: str, relpath: str) -> str:
    target = os.path.join(root, relpath)
    try:
        with open(target, encoding="utf-8") as handle:
            return handle.read()
    except OSError as exc:
        raise CoordinateAlignmentError(f"declared surface is unreadable: {relpath}") from exc


def _part(text: str, header: str) -> str:
    """The body of one ``## PART x`` section, up to the next second-level header."""
    out: list[str] = []
    inside = False
    for line in text.splitlines():
        if line.startswith("## "):
            if inside:
                break
            inside = header in line
            continue
        if inside:
            out.append(line)
    return "\n".join(out)


def _row(body: str, ident: str) -> str:
    """The table row a register carries for one id, or the empty string."""
    for line in body.splitlines():
        if line.strip().startswith(f"| {ident} "):
            return line
    return ""


def _elements(rows: Sequence[Mapping[str, Any]]) -> set[str]:
    return {str(row.get("element")) for row in rows if row.get("element")}


def _primitive_elements(root: str) -> set[str]:
    """What UCPA-000001 binds. Read from ITS declaration, never restated here.

    Restating the four primitives in this source would be the second authoring UCKP-ART-03
    makes void, and the copy would drift the moment UCPA changed.
    """
    target = os.path.join(root, "00-MASTER", "UCPA-000001", "ucpa-declaration.json")
    try:
        with open(target, encoding="utf-8") as handle:
            document = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        raise CoordinateAlignmentError(f"UCPA-000001 declaration is unreadable: {exc}") from exc
    return _elements(document.get("primitive_binding") or ())


def check_every_coordinate_is_declared_by_the_register(
    contract: CoordinateContract, repo: str
) -> tuple[str, ...]:
    """UCCFA-L-01 — a coordinate the register does not carry is invented."""
    body = _part(_read(repo, str(contract.source["canonical_owner"])), "PART B")
    findings: list[str] = []
    for row in contract.coordinates:
        for field in ("id", "element", "answers"):
            value = str(row.get(field, ""))
            needle = value.removeprefix("Answers ") if field == "answers" else value
            if not needle or needle not in body:
                findings.append(f"{row.get('id')}: {field} {value!r} is not carried by PART B")
    return tuple(findings)


def check_standing_matches_the_ratification_record(
    contract: CoordinateContract, repo: str
) -> tuple[str, ...]:
    """UCCFA-L-02 — standing is the standing the record grants, not the one claimed."""
    record = _read(repo, str(contract.source["ratification_record"]))
    ident = str(contract.source["ratified_by"])
    row = _row(record, ident)
    if not row:
        return (f"{ident} carries no row in the ratification record",)
    return tuple(
        f"{entry.get('element')}: {ident} does not carry {entry.get('evidence_phrase')!r}"
        for entry in contract.ratified_standing
        if str(entry.get("evidence_phrase", "")).lower() not in row.lower()
    )


def check_no_element_is_both_primitive_and_coordinate(
    contract: CoordinateContract, repo: str
) -> tuple[str, ...]:
    """UCCFA-L-03 — one determination, authored once."""
    both = _elements(contract.coordinates) & _primitive_elements(repo)
    return tuple(
        f"{element} is bound as both a root primitive and a coordinate" for element in sorted(both)
    )


def check_the_coordinate_set_is_total_over_the_equation(
    contract: CoordinateContract, repo: str
) -> tuple[str, ...]:
    """UCCFA-L-04 — every term of the Universal Equation is bound exactly once."""
    equation = str(contract.source["universal_equation"])
    terms = {
        part.strip(" .")
        for part in re.split(r"[=+]", equation.split("REALITY", 1)[-1])
        if part.strip(" .")
    }
    coordinates = _elements(contract.coordinates)
    primitives = _primitive_elements(repo)
    findings = [
        f"{term}: an equation term bound as neither primitive nor coordinate"
        for term in sorted(terms - coordinates - primitives)
    ]
    findings += [
        f"{term}: bound here but it is not a term of the equation"
        for term in sorted(coordinates - terms)
    ]
    return tuple(findings)


def check_the_superseded_element_is_dispositioned(
    contract: CoordinateContract, repo: str
) -> tuple[str, ...]:
    """UCCFA-L-05 — an element a ratification retired is governed by something, or by nothing."""
    entry = contract.superseded
    body = _part(_read(repo, str(contract.source["canonical_owner"])), "PART A")
    ident = str(entry.get("id"))
    element = str(entry.get("element"))
    row = _row(body, ident)
    findings: list[str] = []
    if not row:
        findings.append(f"{ident} is not carried by PART A")
    else:
        if str(entry.get("superseded_by")) not in row:
            findings.append(
                f"PART A does not record {ident} superseded by {entry.get('superseded_by')}"
            )
        if str(entry.get("evidence_phrase", "")).lower() not in row.lower():
            findings.append(f"PART A does not carry {entry.get('evidence_phrase')!r} for {ident}")
    if element in _primitive_elements(repo):
        findings.append(f"{element} is bound as a primitive by UCPA-000001")
    if element in _elements(contract.coordinates):
        findings.append(f"{element} is bound as a coordinate by this declaration")
    bound = {str(row.get("id")) for row in contract.coordinates}
    findings += [
        f"{into}: {ident} resolves into it but it is not bound here"
        for into in entry.get("resolves_into") or ()
        if str(into) not in bound
    ]
    return tuple(findings)


def check_the_two_bindings_are_the_omega_law_dimensions(
    contract: CoordinateContract, repo: str
) -> tuple[str, ...]:
    """UCCFA-L-06 — UCPA and UCCFA partition the nine dimensions exactly."""
    binding = contract.omega_law
    text = _read(repo, str(binding["carried_by"]))
    law_id = str(binding["law_id"])
    row = next(
        (line for line in text.splitlines() if law_id in line and "representable through" in line),
        "",
    )
    if not row:
        return (f"{law_id} carries no row naming the dimensions it requires",)
    dimensions = [str(name) for name in binding.get("dimensions") or ()]
    coordinates = _elements(contract.coordinates)
    primitives = _primitive_elements(repo)
    findings: list[str] = []
    for dimension in dimensions:
        if dimension not in row:
            findings.append(f"{dimension}: not named by {law_id}")
        bound_by = (dimension in primitives) + (dimension in coordinates)
        if bound_by == 0:
            findings.append(f"{dimension}: bound by neither declaration")
        elif bound_by == 2:
            findings.append(f"{dimension}: bound by both declarations")
    findings += [
        f"{element}: bound but not named by {law_id}"
        for element in sorted((primitives | coordinates) - set(dimensions))
    ]
    return tuple(findings)


#: The prefix that makes a function in this module a law check. Resolution is by NAME, from
#: the declaration, because the binding held as a module-level table was a FIXED_DISPATCH_TABLE
#: and UCON-L-15 refused it — 447 against a ceiling of 446, a ratchet that may hold or fall and
#: never rise. Renaming it below the detector's notice would have been a bypass; removing it is
#: the fix, and a seventh law now needs a declaration entry and a function rather than an edit
#: to a table somebody must remember.
CHECK_PREFIX = "check_"


# UCCFA-L-07 measures the twenty-one absolute constitutional laws — Ω∞-000, Ω∞-001
# (Everything Is Derived From Being.), Ω∞-002 (Everything Is Registry Driven.), Ω∞-003
# (Everything Is Compiler Governed.), Ω∞-004 (Identity Before Participation.), Ω∞-005
# (Authority Before Change.), Ω∞-006 (Evidence Before Truth Claims.), Ω∞-007 (Governance
# Before Execution.), Ω∞-008 (Memory Before Intelligence.), Ω∞-009 (Intelligence Before
# Wisdom.), Ω∞-010 (Wisdom Before Evolution.), Ω∞-011 (Nothing May Violate Invariants.),
# Ω∞-012 (Nothing May Bypass Sovereignty.), Ω∞-013 (Everything Must Be Traceable.), Ω∞-014
# (Everything Must Be Auditable.), Ω∞-015 (Everything Must Be Explainable.), Ω∞-016
# (Everything Must Be Evolvable.), Ω∞-017 (Discovery Does Not Equal Execution.), Ω∞-018
# (Evolution Requires Governance.), Ω∞-019 (Reality Is Constitutionally Governed.), and
# Ω∞-020 (All Future Constructs Must Be Derivable.) — WHERE THEY ARE CARRIED: the register
# named by omega_law_binding. The law texts are deliberately NOT copied into this module.
# A second store of a verbatim law is the duplication UCKP-ART-03 voids, and UCON-L-15's
# FIXED_VOCABULARY_TUPLE ratchet refused exactly that copy when it was tried. The register
# is the single home; this check reads it. The names above are the set this check counts,
# so a law that vanished from the register is refused against the named expectation, not
# against a silent length.


def check_every_absolute_law_is_counted_where_it_is_carried(
    contract: CoordinateContract, repo: str
) -> tuple[str, ...]:
    """UCCFA-L-07 — the absolute laws are counted, contiguous and verbatim, in their register."""
    text = _read(repo, str(contract.omega_law["carried_by"]))
    rows: dict[str, list[str]] = {}
    for line in text.splitlines():
        for cid, statement in re.findall(r"\|\s*\*\*(Ω∞-\d{3})\*\*\s*\|\s*(.+?)\s*\|", line):
            rows.setdefault(cid, []).append(statement)
    expected = {f"Ω∞-{n:03d}" for n in range(21)}
    findings: list[str] = []
    for law_id in sorted(expected - set(rows)):
        findings.append(f"{law_id}: carried by no row of the absolute laws register")
    for law_id in sorted(set(rows) - expected):
        findings.append(f"{law_id}: a row this programme's law set does not carry")
    for law_id, statements in sorted(rows.items()):
        if len(statements) > 1:
            findings.append(f"{law_id}: carried by {len(statements)} rows of one register")
        elif not statements[0].strip():
            findings.append(f"{law_id}: its register row states nothing")
    return tuple(findings)


def _implemented_checks() -> dict[str, Callable[[CoordinateContract, str], tuple[str, ...]]]:
    """Every law check this module defines, keyed by the name a declaration would use."""
    return {
        name[len(CHECK_PREFIX) :]: value
        for name, value in globals().items()
        if name.startswith(CHECK_PREFIX) and callable(value)
    }


def assess(contract: CoordinateContract, repo: str) -> list[tuple[str, str, tuple[str, ...]]]:
    """Measure every declared law, in declared order.

    The binding is two-way and both directions refuse: a declared law naming a check this
    module does not implement is a fault, and a check no declared law names is a fault too. A
    law that silently measured nothing would be worse than one that was never declared.
    """
    implemented = _implemented_checks()
    named: list[tuple[str, str, str]] = []
    for law in contract.laws:
        ident = str(law.get("id"))
        check = str(law.get("check") or "")
        if not check:
            raise CoordinateAlignmentError(f"{ident} names no check")
        named.append((ident, str(law.get("title", "")), check))
    missing = [f"{i} -> {c}" for i, _, c in named if c not in implemented]
    if missing:
        raise CoordinateAlignmentError(f"declared law(s) no check implements: {missing}")
    orphan = sorted(set(implemented) - {c for _, _, c in named})
    if orphan:
        raise CoordinateAlignmentError(f"check(s) no declared law names: {orphan}")
    return [(ident, title, implemented[check](contract, repo)) for ident, title, check in named]
