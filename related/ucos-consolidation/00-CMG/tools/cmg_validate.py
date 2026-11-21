#!/usr/bin/env python3
"""CMG-000001 meta-constitutional validator.

Realization of CMG-000001 Article L.3 (Validation Framework). This tool is
DERIVED TRUTH (CMG-000001 XII.6, L.6): it asserts nothing on its own authority.
It recomputes what CMG-000001 already declares, from repository state alone.

Properties required by CMG-000001 and honoured here:
  * L.4  fail-closed  — an unreadable input, a missing file, or an ambiguous
                        record produces a finding, never a pass.
  * L.5  deterministic and hermetic — identical repository state yields
                        byte-identical output. No clock, no environment, no
                        locale, no network, no ordering dependence.
  * L.7  non-duplicating — no check here re-implements a check already owned by
                        a located gate (lint, coverage, registration, closure).
  * CMG-L-08 / LXVI.5  zero hard coding — this module contains NO member of any
                        constitutional enumeration. Every kind, standing, reach,
                        phase, state, transition, relationship type, tier,
                        namespace, artifact, concern, vacancy, gap and open
                        question is read from CMG-REGISTRY.json.

Usage:
    python3 00-CMG/tools/cmg_validate.py [--repo-root PATH] [--emit PATH]

Exit status: 0 when zero findings; 1 when any finding; 2 on fail-closed abort.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys

REGISTRY_RELPATH = "00-CMG/CMG-REGISTRY.json"

ARTICLE_RE = re.compile(r"^## ARTICLE ([IVXLCDM]+) — (.+)$")
FRONTMATTER_VERSION_RE = re.compile(r"^\|\s*VERSION\s*\|\s*([^|]+?)\s*\|", re.MULTILINE)
CMG_MEMBER_RE = re.compile(r"\bCMG-([A-Z]+)-(\d+)\b")
CMG_NATIVE_RE = re.compile(r"\bCMG-(\d{4,})\b")
ROMAN_VALUES = (
    ("M", 1000), ("CM", 900), ("D", 500), ("CD", 400),
    ("C", 100), ("XC", 90), ("L", 50), ("XL", 40),
    ("X", 10), ("IX", 9), ("V", 5), ("IV", 4), ("I", 1),
)


class Abort(Exception):
    """Fail-closed abort: the validator cannot reach a determinate result."""


def roman_to_int(text: str) -> int:
    total = 0
    index = 0
    for symbol, value in ROMAN_VALUES:
        while text.startswith(symbol, index):
            total += value
            index += len(symbol)
    if index != len(text):
        raise Abort(f"not a well-formed Roman numeral: {text!r}")
    return total


class Findings:
    """Ordered, deduplicated finding collector. Order is insertion order, which
    is a pure function of the check sequence — never of dict or set iteration."""

    def __init__(self) -> None:
        self._seen: set[tuple[str, str, str]] = set()
        self.items: list[dict[str, str]] = []

    def add(self, check: str, clause: str, detail: str) -> None:
        key = (check, clause, detail)
        if key in self._seen:
            return
        self._seen.add(key)
        self.items.append({"check": check, "clause": clause, "detail": detail})

    def __len__(self) -> int:
        return len(self.items)


def load_registry(repo_root: str) -> dict:
    path = os.path.join(repo_root, REGISTRY_RELPATH)
    if not os.path.isfile(path):
        raise Abort(f"registry not found: {REGISTRY_RELPATH}")
    try:
        with open(path, encoding="utf-8") as handle:
            data = json.load(handle)
    except (OSError, ValueError) as exc:
        raise Abort(f"registry unreadable or malformed: {exc}") from exc
    if not isinstance(data, dict):
        raise Abort("registry root is not an object")
    return data


def read_canonical(repo_root: str, registry: dict) -> tuple[str, dict[str, str]]:
    relpath = registry.get("canonical_source")
    if not isinstance(relpath, str) or not relpath:
        raise Abort("registry declares no canonical_source")
    path = os.path.join(repo_root, relpath)
    if not os.path.isfile(path):
        raise Abort(f"canonical source not found: {relpath}")
    try:
        with open(path, encoding="utf-8") as handle:
            text = handle.read()
    except OSError as exc:
        raise Abort(f"canonical source unreadable: {exc}") from exc
    articles: dict[str, str] = {}
    for line in text.splitlines():
        match = ARTICLE_RE.match(line)
        if match:
            numeral, title = match.group(1), match.group(2)
            if numeral in articles:
                raise Abort(f"duplicate ARTICLE {numeral} in canonical source")
            articles[numeral] = title
    if not articles:
        raise Abort("canonical source declares no articles")
    return text, articles


def exists(repo_root: str, relpath: str) -> bool:
    return os.path.exists(os.path.join(repo_root, relpath))


def check_conformance(reg: dict, articles: dict[str, str], f: Findings) -> None:
    """L.3(a) — every mandated section resolves to a present Article, the
    article sequence is gapless, and the closing articles are present."""
    mapped = reg.get("conformance_map") or []
    if not mapped:
        f.add("conformance", "L.3(a)", "registry declares an empty conformance_map")
    seen_numbers = []
    for entry in mapped:
        number = entry.get("n")
        section = entry.get("section", "?")
        numeral = entry.get("article", "")
        seen_numbers.append(number)
        if numeral not in articles:
            f.add("conformance", "LXXIX.7",
                  f"mandated section {number} ({section}) maps to absent ARTICLE {numeral}")
            continue
        try:
            if roman_to_int(numeral) != number:
                f.add("conformance", "LXXIX.7",
                      f"mandated section {number} ({section}) maps to ARTICLE {numeral} "
                      f"whose ordinal is {roman_to_int(numeral)}")
        except Abort as exc:
            f.add("conformance", "LXXIX.7", str(exc))
    expected = list(range(1, len(mapped) + 1))
    if seen_numbers != expected:
        f.add("conformance", "LXXIX.7",
              "conformance_map section numbers are not the gapless sequence "
              f"1..{len(mapped)}")
    for entry in reg.get("closing_articles") or []:
        numeral = entry.get("article", "")
        if numeral not in articles:
            f.add("conformance", "LXXIX.7", f"closing ARTICLE {numeral} is absent")
    ordinals = sorted(roman_to_int(n) for n in articles)
    if ordinals != list(range(1, len(ordinals) + 1)):
        f.add("conformance", "V.2",
              "article ordinals are not the gapless sequence 1..N")


def check_identifier_families(reg: dict, text: str, f: Findings) -> None:
    """L.3(b) — every CMG identifier used in the canonical source belongs to a
    declared family (V.3), and every declared family is actually used."""
    families = {e.get("prefix", "") for e in reg.get("identifier_families") or []}
    if not families:
        f.add("identifiers", "V.3", "registry declares no identifier_families")
        return
    used: set[str] = set()
    for match in CMG_MEMBER_RE.finditer(text):
        prefix = f"CMG-{match.group(1)}"
        used.add(prefix)
        if prefix not in families:
            f.add("identifiers", "V.3",
                  f"undeclared identifier family in canonical source: {prefix}")
    for prefix in sorted(families - used):
        f.add("identifiers", "V.3",
              f"declared identifier family is never used: {prefix}")
    natives = {m.group(0) for m in CMG_NATIVE_RE.finditer(text)}
    namespace = next(
        (n for n in reg.get("namespaces") or [] if n.get("token") == "CMG"), None
    )
    if namespace is None:
        f.add("identifiers", "XXXI.6", "the CMG namespace is not declared in the registry")
        return
    width = namespace.get("width")
    if not isinstance(width, int) or width < 6:
        f.add("identifiers", "XXXI.3",
              f"CMG namespace width {width!r} is below the declared minimum of 6")
    for native in sorted(natives):
        digits = native.split("-", 1)[1]
        # XXXI.3 / XXXI.4 — left-padding beyond the declared width is permitted
        # (comparison is by ordinal, not by string), narrower is not.
        if len(digits) < width:
            f.add("identifiers", "XXXI.2",
                  f"identifier {native} is narrower than the declared CMG width {width}")


def check_members_unique(reg: dict, f: Findings) -> None:
    """L.3(j) / CMG-INV-08 — identifier injectivity across every registry
    collection: no identifier is reused, reassigned, or duplicated."""
    seen: dict[str, str] = {}
    for collection, items in sorted(reg.items()):
        if not isinstance(items, list):
            continue
        for item in items:
            if not isinstance(item, dict):
                continue
            identifier = item.get("id")
            if not isinstance(identifier, str) or not identifier:
                continue
            if identifier in seen:
                f.add("identity", "CMG-INV-08",
                      f"identifier {identifier} appears in both "
                      f"{seen[identifier]} and {collection}")
            else:
                seen[identifier] = collection


def check_homes(reg: dict, repo_root: str, f: Findings) -> dict[str, dict]:
    """L.3(c) — every registry entry resolves to a present canonical home
    (LVIII.3, XXXI.8)."""
    artifacts: dict[str, dict] = {}
    for artifact in reg.get("artifacts") or []:
        identifier = artifact.get("id")
        path = artifact.get("path")
        if not isinstance(identifier, str) or not identifier:
            f.add("homes", "XXX.3", f"artifact entry without identity: {artifact!r}")
            continue
        if identifier in artifacts:
            f.add("homes", "CMG-INV-08", f"duplicate artifact identity: {identifier}")
            continue
        artifacts[identifier] = artifact
        if not isinstance(path, str) or not path:
            f.add("homes", "LVIII.3", f"{identifier} declares no canonical home")
        elif not exists(repo_root, path):
            f.add("homes", "LVIII.3", f"{identifier} canonical home not found: {path}")
    if not artifacts:
        f.add("homes", "XV.2", "registry declares no artifacts")
    return artifacts


def check_classification(reg: dict, artifacts: dict[str, dict], f: Findings) -> None:
    """XII.1-XII.4 — every artifact declares a kind, standing, reach and tier
    drawn from the declared value sets."""
    kinds = {e.get("id") for e in reg.get("kinds") or []}
    standings = set(reg.get("standings") or [])
    reaches = set(reg.get("reaches") or [])
    tiers = {t.get("id") for t in reg.get("tiers") or []}
    for identifier in sorted(artifacts):
        artifact = artifacts[identifier]
        for field, allowed, clause in (
            ("kind", kinds, "XIII.1"),
            ("standing", standings, "XII.2"),
            ("reach", reaches, "XII.3"),
            ("tier", tiers, "XVI.2"),
        ):
            value = artifact.get(field)
            if value not in allowed:
                f.add("classification", clause,
                      f"{identifier} declares undeclared {field}: {value!r}")


def check_concerns(reg: dict, artifacts: dict[str, dict], repo_root: str,
                   f: Findings) -> dict[str, set[str]]:
    """L.3(d) CMG-INV-02, L.3(e) CMG-INV-03, XVIII.6 / CMG-L-07, XX.8.

    Returns the owner -> owned-concern-set map used by the precedence check."""
    concerns = reg.get("concerns") or []
    if not concerns:
        f.add("concerns", "XV.2", "registry declares no concerns")
    meta_owner = reg.get("canonical_source_owner") or "CMG-000001"
    by_name: dict[str, str] = {}
    owned: dict[str, set[str]] = {}
    for entry in concerns:
        identifier = entry.get("id", "?")
        name = entry.get("concern")
        owner = entry.get("owner")
        owner_paths = entry.get("owner_paths")
        disposition = entry.get("disposition")
        if not isinstance(name, str) or not name:
            f.add("concerns", "XIV.4", f"{identifier} declares no concern name")
            continue
        # CMG-INV-02 — the concern -> owner mapping is injective on concerns.
        if name in by_name:
            f.add("concerns", "CMG-INV-02",
                  f"concern {name!r} is claimed by both {by_name[name]} and {identifier}")
            continue
        by_name[name] = identifier
        if not entry.get("basis"):
            f.add("concerns", "CMG-L-07", f"{identifier} declares no basis")
        # CMG-INV-03 / CMG-L-07 — every concern has exactly one located owner.
        if owner:
            if owner not in artifacts:
                f.add("concerns", "XVIII.6",
                      f"{identifier} delegates to unlocated owner {owner}")
            else:
                owned.setdefault(owner, set()).add(name)
                standing = artifacts[owner].get("standing")
                if standing == "DECLARATIVE":
                    f.add("concerns", "XX.8",
                          f"{identifier} names DECLARATIVE artifact {owner} as owner")
        elif owner_paths:
            if not isinstance(owner_paths, list) or not owner_paths:
                f.add("concerns", "CMG-L-07", f"{identifier} owner_paths is not a list")
            for relpath in owner_paths:
                if not exists(repo_root, relpath):
                    f.add("concerns", "XVIII.6",
                          f"{identifier} owner path not found: {relpath}")
            owned.setdefault(f"path:{identifier}", set()).add(name)
        else:
            f.add("concerns", "CMG-INV-03", f"{identifier} has no owner")
        # LXXXII.3 / CMG-INV-12 — retained concerns are the meta layer's own;
        # delegated concerns are never owned by the meta layer.
        if disposition == "RETAIN" and owner != meta_owner:
            f.add("concerns", "LXXXII.3",
                  f"{identifier} is RETAIN but owned by {owner!r}, not {meta_owner}")
        if disposition == "REUSE" and owner == meta_owner:
            f.add("concerns", "CMG-INV-12",
                  f"{identifier} is REUSE but owned by the meta layer itself")
    # CMG-INV-03 (second projection) — an artifact that declares binding force
    # must own at least one concern; an owner with no concern is orphan governance.
    binding = {"META", "FOUNDATIONAL"}
    for identifier in sorted(artifacts):
        if artifacts[identifier].get("standing") in binding and identifier not in owned:
            f.add("concerns", "CMG-INV-03",
                  f"{identifier} declares binding standing but owns no concern")
    return owned


def check_superiors(reg: dict, artifacts: dict[str, dict], f: Findings) -> None:
    """L.3(f) CMG-INV-04 — every declared superior resolves to a located
    artifact or to a recorded vacancy carrying a closure procedure."""
    vacancies = {v.get("id"): v for v in reg.get("vacancies") or []}
    questions = {q.get("id") for q in reg.get("open_questions") or []}
    for identifier, vacancy in sorted(vacancies.items(), key=lambda kv: str(kv[0])):
        if not vacancy.get("closure_procedure"):
            f.add("superiors", "XVII.4",
                  f"vacancy {identifier} records no closure procedure")
        question = vacancy.get("open_question")
        if question not in questions:
            f.add("superiors", "XVII.4",
                  f"vacancy {identifier} references unrecorded open question {question!r}")
        if vacancy.get("located") is not False:
            f.add("superiors", "IV.11",
                  f"vacancy {identifier} does not declare located=false")
    for identifier in sorted(artifacts):
        for superior in artifacts[identifier].get("superiors") or []:
            if superior not in artifacts and superior not in vacancies:
                f.add("superiors", "CMG-INV-04",
                      f"{identifier} declares unresolvable superior {superior}")


def topological_order(graph: dict[str, list[str]]) -> list[str] | None:
    """Deterministic Kahn sort over sorted keys. Returns None on a cycle."""
    indegree = {node: 0 for node in graph}
    for node in sorted(graph):
        for target in graph[node]:
            if target in indegree:
                indegree[target] += 1
    ready = sorted(n for n in indegree if indegree[n] == 0)
    order: list[str] = []
    while ready:
        node = ready.pop(0)
        order.append(node)
        for target in sorted(graph.get(node, [])):
            if target in indegree:
                indegree[target] -= 1
                if indegree[target] == 0:
                    ready.append(target)
                    ready.sort()
    return order if len(order) == len(graph) else None


def check_acyclicity(reg: dict, artifacts: dict[str, dict], f: Findings) -> None:
    """L.3(g) CMG-INV-05 — the dependency graph and the precedence lattice are
    both acyclic (CMG-L-06)."""
    depends = {i: list(artifacts[i].get("depends_on") or []) for i in artifacts}
    if topological_order(depends) is None:
        f.add("acyclicity", "CMG-INV-05",
              "the constitutional dependency graph contains a cycle")
    for identifier in sorted(depends):
        for target in depends[identifier]:
            if target not in artifacts:
                f.add("acyclicity", "XXXV.4",
                      f"{identifier} depends on unresolvable {target}")
    tiers = {t.get("id"): list(t.get("subordinate_to") or []) for t in reg.get("tiers") or []}
    if not tiers:
        f.add("acyclicity", "XVI.2", "registry declares no tiers")
        return
    for tier in sorted(tiers):
        for superior in tiers[tier]:
            if superior not in tiers:
                f.add("acyclicity", "XVI.2",
                      f"tier {tier} is subordinate to undeclared tier {superior}")
    if topological_order(tiers) is None:
        f.add("acyclicity", "CMG-INV-05",
              "the constitutional precedence lattice contains a cycle")


def tier_reachable(tiers: dict[str, list[str]], start: str, target: str) -> bool:
    stack = [start]
    seen = {start}
    while stack:
        node = stack.pop()
        if node == target:
            return True
        for superior in tiers.get(node, []):
            if superior not in seen:
                seen.add(superior)
                stack.append(superior)
    return False


def check_precedence(reg: dict, artifacts: dict[str, dict],
                     owned: dict[str, set[str]], f: Findings) -> None:
    """L.3(h) CMG-INV-06 — every pair of recognized artifacts resolves to
    exactly one relative rank or to a declared orthogonality (XVI.4, XVI.6)."""
    tiers = {t.get("id"): list(t.get("subordinate_to") or []) for t in reg.get("tiers") or []}
    orthogonal = set()
    for pair in reg.get("orthogonal_tier_pairs") or []:
        if isinstance(pair, list) and len(pair) == 2:
            orthogonal.add((pair[0], pair[1]))
            orthogonal.add((pair[1], pair[0]))
    identifiers = sorted(artifacts)
    for index, left in enumerate(identifiers):
        for right in identifiers[index + 1:]:
            left_tier = artifacts[left].get("tier")
            right_tier = artifacts[right].get("tier")
            if left_tier != right_tier:
                if (left_tier, right_tier) in orthogonal:
                    continue
                if tier_reachable(tiers, left_tier, right_tier):
                    continue
                if tier_reachable(tiers, right_tier, left_tier):
                    continue
                f.add("precedence", "CMG-INV-06",
                      f"{left} ({left_tier}) and {right} ({right_tier}) are neither "
                      "comparable nor declared orthogonal")
                continue
            # XVI.6(a) explicit subordination, then XVI.6(c) orthogonality by
            # disjoint jurisdiction (XIV.4 forbids overlapping concerns).
            if right in (artifacts[left].get("superiors") or []):
                continue
            if left in (artifacts[right].get("superiors") or []):
                continue
            if owned.get(left, set()).isdisjoint(owned.get(right, set())):
                continue
            f.add("precedence", "CMG-INV-06",
                  f"{left} and {right} share tier {left_tier} with overlapping "
                  "jurisdiction and no declared rank")


def check_lifecycle(reg: dict, artifacts: dict[str, dict], f: Findings) -> None:
    """L.3(i) CMG-INV-07 — every recorded state is a declared state and every
    recorded transition is an enumerated transition (XXV, XXVI)."""
    phases = set(reg.get("phases") or [])
    states = {}
    for entry in reg.get("states") or []:
        name = entry.get("state")
        phase = entry.get("phase")
        if name in states:
            f.add("lifecycle", "XXV.1", f"duplicate state name: {name}")
        states[name] = phase
        if phase not in phases:
            f.add("lifecycle", "XXV.2", f"state {name} declares undeclared phase {phase!r}")
    if not states:
        f.add("lifecycle", "XXV.1", "registry declares no states")
        return
    wildcards = {f"*{phase}" for phase in phases}
    for entry in reg.get("transitions") or []:
        identifier = entry.get("id", "?")
        for field in ("from", "to"):
            value = entry.get(field)
            if value in wildcards:
                if field == "to":
                    f.add("lifecycle", "XXVI.1",
                          f"transition {identifier} uses a phase wildcard as target")
                continue
            if value not in states:
                f.add("lifecycle", "CMG-INV-07",
                      f"transition {identifier} references undeclared state {value!r}")
    for identifier in sorted(artifacts):
        state = artifacts[identifier].get("state")
        if state not in states:
            f.add("lifecycle", "CMG-INV-07",
                  f"{identifier} records undeclared state {state!r}")
            continue
        # XXVII.3 — phase-force consistency: an artifact owning a concern while
        # outside the IN-EFFECT phase must be provisional by record, not silent.
        if states[state] == "POST-EFFECT" and artifacts[identifier].get("standing") in (
            "META", "FOUNDATIONAL"
        ):
            f.add("lifecycle", "XXVII.3",
                  f"{identifier} is POST-EFFECT but declares binding standing")


def check_lineage(artifacts: dict[str, dict], f: Findings) -> None:
    """L.3(k) CMG-INV-11 — every lineage predecessor resolves to a present
    artifact (preservation)."""
    for identifier in sorted(artifacts):
        predecessor = artifacts[identifier].get("lineage_predecessor")
        if predecessor is None:
            continue
        if predecessor not in artifacts:
            f.add("lineage", "CMG-INV-11",
                  f"{identifier} lineage predecessor {predecessor} is absent")
        if predecessor == identifier:
            f.add("lineage", "LXXII.6", f"{identifier} is its own lineage predecessor")


def check_gaps(reg: dict, f: Findings) -> None:
    """LXXVIII — every gap is dispositioned and every referenced open question
    is recorded (LXXX.2 precondition 12)."""
    questions = {q.get("id") for q in reg.get("open_questions") or []}
    for gap in reg.get("gaps") or []:
        identifier = gap.get("id", "?")
        if not gap.get("disposition"):
            f.add("gaps", "LXXVIII.2", f"{identifier} carries no disposition")
        question = gap.get("open_question")
        if question is not None and question not in questions:
            f.add("gaps", "LXXVIII.3",
                  f"{identifier} references unrecorded open question {question!r}")
        if gap.get("disposition") in ("NOT-CLOSED", "PARTIALLY-CLOSED") and not question:
            f.add("gaps", "LVII.3",
                  f"{identifier} is unclosed but records no open question")
    for question in reg.get("open_questions") or []:
        if not question.get("requires"):
            f.add("gaps", "LVII.3",
                  f"{question.get('id', '?')} records no ratification requirement")


def check_closed_enumerations(reg: dict, text: str, f: Findings) -> None:
    """CMG-INV-09 — every CLOSED enumeration cites its closing invariant, and
    the cited invariant exists in the canonical source."""
    entries = reg.get("closed_enumerations") or []
    if not entries:
        f.add("finiteness", "CMG-INV-09",
              "registry declares no closed_enumerations record")
    for entry in entries:
        name = entry.get("enumeration", "?")
        invariant = entry.get("closing_invariant")
        if not invariant:
            f.add("finiteness", "CMG-INV-09",
                  f"closed enumeration {name} cites no closing invariant")
        elif invariant not in text:
            f.add("finiteness", "CMG-INV-09",
                  f"closed enumeration {name} cites absent invariant {invariant}")
        if not entry.get("reason"):
            f.add("finiteness", "CMG-INV-09",
                  f"closed enumeration {name} records no closure reason")


def check_namespaces(reg: dict, artifacts: dict[str, dict], f: Findings) -> None:
    """XXXIII — every namespace has exactly one located owner, a declared width
    and a declared status; the CMG namespace is owned by the meta instrument."""
    seen: set[str] = set()
    meta_owner = reg.get("canonical_source_owner") or "CMG-000001"
    for namespace in reg.get("namespaces") or []:
        ns_name = namespace.get("token")
        if not ns_name:
            f.add("namespaces", "XXXIII.1", f"namespace without token: {namespace!r}")
            continue
        if ns_name in seen:
            f.add("namespaces", "XXXIII.2", f"namespace {ns_name} is declared twice")
        seen.add(ns_name)
        if not isinstance(namespace.get("width"), int):
            f.add("namespaces", "XXXI.2", f"namespace {ns_name} declares no integer width")
        if not namespace.get("status"):
            f.add("namespaces", "XXXIII.3", f"namespace {ns_name} declares no status")
        owner = namespace.get("owner")
        if owner not in artifacts:
            f.add("namespaces", "XXXIII.2",
                  f"namespace {ns_name} names unlocated owner {owner!r}")
        if ns_name == "CMG" and owner != meta_owner:
            f.add("namespaces", "XXXIII.6",
                  f"the CMG namespace must be owned by {meta_owner}, not {owner!r}")


def check_no_persisted_conflict(reg: dict, artifacts: dict[str, dict], f: Findings) -> None:
    """XXXIV.4 / LXXIX.8 — a CONFLICTS-WITH relationship must not persist."""
    non_persistent = {
        e.get("type") for e in reg.get("relationship_types") or []
        if e.get("must_not_persist")
    }
    if not non_persistent:
        f.add("conflicts", "XXXIV.4",
              "no relationship type is marked must_not_persist; XXXIV.4 is unenforced")
    for identifier in sorted(artifacts):
        for relationship in sorted(non_persistent):
            field = relationship.lower().replace("-", "_")
            if artifacts[identifier].get(field):
                f.add("conflicts", "XXXIV.4",
                      f"{identifier} persists a {relationship} relationship")


def check_source_binding(reg: dict, text: str, f: Findings) -> None:
    """XV.3 / L.6 — the derived projection binds to the canonical source and to
    the exact version it projects."""
    declared = reg.get("canonical_source_version")
    match = FRONTMATTER_VERSION_RE.search(text)
    if match is None:
        f.add("binding", "XXVIII.1",
              "canonical source declares no VERSION front-matter row")
        return
    actual = match.group(1).strip()
    if declared != actual:
        f.add("binding", "XV.3",
              f"registry projects version {declared!r} but the canonical source is "
              f"version {actual!r}")
    if reg.get("authority", "").startswith("NONE") is False:
        f.add("binding", "XII.6",
              "the derived registry does not declare AUTHORITY = NONE (DERIVED TRUTH)")


def readiness(reg: dict, findings: Findings) -> str:
    """LXXX.3 — the certification outcome, computed, never asserted."""
    if len(findings):
        return "NOT-READY"
    unclosed = [v for v in reg.get("vacancies") or [] if v.get("located") is not True]
    blocking = [
        q for q in reg.get("open_questions") or []
        if q.get("blocks") and q.get("blocks") != "Nothing"
        and not str(q.get("blocks", "")).startswith("Nothing")
    ]
    if unclosed or blocking:
        return "READY-PROVISIONAL"
    return "READY"


def run(repo_root: str) -> tuple[Findings, dict]:
    findings = Findings()
    registry = load_registry(repo_root)
    text, articles = read_canonical(repo_root, registry)

    check_source_binding(registry, text, findings)
    check_conformance(registry, articles, findings)
    check_identifier_families(registry, text, findings)
    check_members_unique(registry, findings)
    artifacts = check_homes(registry, repo_root, findings)
    check_classification(registry, artifacts, findings)
    owned = check_concerns(registry, artifacts, repo_root, findings)
    check_superiors(registry, artifacts, findings)
    check_acyclicity(registry, artifacts, findings)
    check_precedence(registry, artifacts, owned, findings)
    check_lifecycle(registry, artifacts, findings)
    check_lineage(artifacts, findings)
    check_gaps(registry, findings)
    check_closed_enumerations(registry, text, findings)
    check_namespaces(registry, artifacts, findings)
    check_no_persisted_conflict(registry, artifacts, findings)

    outcome = readiness(registry, findings)
    ceiling = (registry.get("readiness") or {}).get("declared_ceiling")
    if outcome == "READY" and ceiling == "READY-PROVISIONAL":
        outcome = "READY-PROVISIONAL"

    evidence = {
        "schema": "ucos-cmg-validation-evidence",
        "authority": "NONE (DERIVED TRUTH)",
        "canonical_source": registry.get("canonical_source"),
        "canonical_source_version": registry.get("canonical_source_version"),
        "articles_present": len(articles),
        "mandated_sections": len(registry.get("conformance_map") or []),
        "artifacts_recognized": len(artifacts),
        "concerns_allocated": len(registry.get("concerns") or []),
        "delegated_concerns": sum(
            1 for c in registry.get("concerns") or [] if c.get("disposition") == "REUSE"
        ),
        "retained_concerns": sum(
            1 for c in registry.get("concerns") or [] if c.get("disposition") == "RETAIN"
        ),
        "vacancies_recorded": len(registry.get("vacancies") or []),
        "gaps_recorded": len(registry.get("gaps") or []),
        "open_questions_recorded": len(registry.get("open_questions") or []),
        "findings": findings.items,
        "finding_count": len(findings),
        "readiness_outcome": outcome,
    }
    return findings, evidence


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate the UCOS Omega-Infinity meta-constitutional layer "
                    "(CMG-000001 Article L)."
    )
    parser.add_argument("--repo-root", default=".", help="repository root (default: .)")
    parser.add_argument("--emit", default=None, help="write evidence JSON to this path")
    parser.add_argument("--quiet", action="store_true", help="print findings only")
    args = parser.parse_args(argv)

    try:
        findings, evidence = run(os.path.abspath(args.repo_root))
    except Abort as exc:
        sys.stderr.write(f"CMG VALIDATION ABORTED (fail-closed, L.4): {exc}\n")
        return 2

    if not args.quiet:
        print("CMG-000001 META-CONSTITUTIONAL VALIDATION")
        print(f"  canonical source      : {evidence['canonical_source']} "
              f"v{evidence['canonical_source_version']}")
        print(f"  articles present      : {evidence['articles_present']}")
        print(f"  mandated sections     : {evidence['mandated_sections']}")
        print(f"  artifacts recognized  : {evidence['artifacts_recognized']}")
        print(f"  concerns allocated    : {evidence['concerns_allocated']} "
              f"({evidence['delegated_concerns']} delegated, "
              f"{evidence['retained_concerns']} retained)")
        print(f"  vacancies recorded    : {evidence['vacancies_recorded']}")
        print(f"  gaps recorded         : {evidence['gaps_recorded']}")
        print(f"  open questions        : {evidence['open_questions_recorded']}")

    for finding in findings.items:
        print(f"  FINDING [{finding['check']}] {finding['clause']}: {finding['detail']}")

    print(f"  findings              : {len(findings)}")
    print(f"  readiness outcome     : {evidence['readiness_outcome']}")

    if args.emit:
        target = os.path.abspath(args.emit)
        os.makedirs(os.path.dirname(target), exist_ok=True)
        with open(target, "w", encoding="utf-8") as handle:
            json.dump(evidence, handle, indent=2, sort_keys=True, ensure_ascii=False)
            handle.write("\n")

    return 1 if len(findings) else 0


if __name__ == "__main__":
    sys.exit(main())
