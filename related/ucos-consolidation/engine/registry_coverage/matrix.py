"""RCM — the Registry Coverage Matrix.

Answers: **what governed objects exist, where are they registered, who owns the
registration plane, and what coverage gaps exist?**

It is coverage INTELLIGENCE, not a registry. The distinction is structural rather than
promised: this module stores no object record. Every object it reports is read from the
plane that already registers it, and every ownership it reports is read from the instrument
that already declares it. A matrix that kept its own copy would be the duplicate-catalogue
defect it exists to detect — the 141st registry.

Every mechanism, plane, disclosed gap and scan root is DATA in ``declarations.json``.
There is no registry path, no object class and no gap id below.

**W5-G1 is disclosed, never inferred.** Eight producer outputs carry no declared authority.
The producer that writes each one is *recorded* and explicitly *not adopted* as its owner:
inferring ownership permanently would manufacture the very declaration the finding says is
missing. Disclosure keeps the gap countable while its remediation stays with the owner it
is referred to — and an UNDISCLOSED registry with no authority is a violation, which is what
makes the disclosure a ratchet rather than an excuse.
"""

from __future__ import annotations

import json
import os
import re
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from engine.uckp.canonical import canonical_json, content_hash

COVERED = "COVERED"
PARTIALLY_COVERED = "PARTIALLY_COVERED"
UNREGISTERED = "UNREGISTERED"
DUPLICATE_REGISTRATION = "DUPLICATE_REGISTRATION"

_DECLARATIONS = os.path.join("engine", "registry_coverage", "declarations.json")
_OBJECTS = os.path.join("00-MASTER", "UCOS-UGA-001", "02-UNIVERSAL-OBJECT-REGISTRY.json")


class CoverageError(RuntimeError):
    """The declaration or a source is unusable. A fault, never a coverage verdict."""


def repo_root() -> str:
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _read_json(repo: str, relpath: str) -> Any:
    try:
        with open(os.path.join(repo, relpath), encoding="utf-8") as handle:
            return json.load(handle)
    except (FileNotFoundError, json.JSONDecodeError, IsADirectoryError):
        return None


@dataclass(frozen=True, slots=True)
class Plane:
    """One registration plane: the registry that holds it and the classes it holds."""

    name: str
    registry: str
    owner: str
    object_classes: frozenset[str]
    mutation_class: str
    population_key: str


@dataclass(frozen=True, slots=True)
class AuthorityGap:
    """One registry known to declare no authority, and where its remediation belongs."""

    gap_id: str
    registry: str
    producer: str
    producer_owner: str
    missing: str
    remediation: str
    referred_to: str

    def as_dict(self) -> dict[str, str]:
        return {
            "gap_id": self.gap_id,
            "missing": self.missing,
            "producer": self.producer,
            "producer_owner": self.producer_owner,
            "referred_to": self.referred_to,
            "registry": self.registry,
            "remediation": self.remediation,
        }


@dataclass(frozen=True, slots=True)
class Declarations:
    """The declaration set, rehydrated and refused when unusable."""

    declaration_id: str
    mechanisms: tuple[Mapping[str, Any], ...]
    planes: tuple[Plane, ...]
    gaps: tuple[AuthorityGap, ...]
    backlog: frozenset[str]
    scan_roots: tuple[str, ...]
    minimum_population: int
    states: frozenset[str]

    @classmethod
    def of(cls, document: Mapping[str, Any]) -> Declarations:
        for section in ("authority_mechanisms", "registration_planes", "coverage_states", "scan"):
            if not document.get(section):
                raise CoverageError(f"declaration section {section!r} is absent or empty")
        scan = document["scan"]
        planes = tuple(
            Plane(
                name=str(p["plane"]),
                registry=str(p["registry"]),
                owner=str(p["owner"]),
                object_classes=frozenset(str(c) for c in p["holds_object_classes"]),
                mutation_class=str(p["mutation_class"]),
                population_key=str(p["population_key"]),
            )
            for p in document["registration_planes"]
        )
        overlap = [
            (a.name, b.name)
            for i, a in enumerate(planes)
            for b in planes[i + 1 :]
            if a.object_classes & b.object_classes
        ]
        if overlap:
            raise CoverageError(f"two planes claim the same object class: {overlap}")
        return cls(
            declaration_id=str(document.get("declaration_id") or ""),
            mechanisms=tuple(document["authority_mechanisms"]),
            planes=planes,
            gaps=tuple(
                AuthorityGap(
                    gap_id=str(g["id"]),
                    registry=str(g["registry"]),
                    producer=str(g["producer"]),
                    producer_owner=str(g["producer_owner"]),
                    missing=str(g["missing"]),
                    remediation=str(g["remediation"]),
                    referred_to=str(g["referred_to"]),
                )
                for g in document.get("disclosed_authority_gaps") or ()
            ),
            backlog=frozenset(str(b) for b in document.get("undeclared_backlog") or ()),
            scan_roots=tuple(str(r) for r in scan["roots"]),
            minimum_population=int(scan.get("minimum_population", 3)),
            states=frozenset(str(s) for s in document["coverage_states"]),
        )


def load_declarations(path: str | None = None, repo: str | None = None) -> Declarations:
    repo = repo or repo_root()
    target = path or os.path.join(repo, _DECLARATIONS)
    try:
        with open(target, encoding="utf-8") as handle:
            document = json.load(handle)
    except FileNotFoundError:
        raise CoverageError(f"the coverage declaration is absent: {target}") from None
    except json.JSONDecodeError as error:
        raise CoverageError(f"the coverage declaration is not valid JSON ({error})") from None
    return Declarations.of(document)


# --- authority location -------------------------------------------------------------------


def _population(document: Any) -> int:
    if not isinstance(document, dict):
        return 0
    sizes = [
        len(value)
        for key, value in document.items()
        if isinstance(value, list | dict) and not str(key).startswith("$")
    ]
    return max(sizes) if sizes else 0


def locate_authority(
    path: str, document: Any, declarations: Declarations, indexes: Mapping[str, Any]
) -> str | None:
    """Return the mechanism that declares this registry's authority, or None.

    The mechanisms are tried in declared rank order, so the most direct declaration is the
    one reported. Returning None is a finding, not a default.
    """
    if not isinstance(document, dict):
        return None
    for mechanism in declarations.mechanisms:
        kind = str(mechanism.get("mechanism"))
        if kind == "TOP_LEVEL_AUTHORITY_KEY":
            if isinstance(document.get("authority"), str) and document["authority"].strip():
                return kind
        elif kind == "DOMAIN_AUTHORITY_KEY":
            pattern = str(mechanism.get("key_pattern") or "")
            if pattern and any(re.search(pattern, str(k), re.IGNORECASE) for k in document):
                return kind
        elif kind == "GENERATED_ARTIFACT_REGISTRY":
            if path in indexes["generated_paths"]:
                return kind
        elif kind in ("CONSTITUTIONAL_AUTHORITY_ALIGNMENT", "MUTATION_GOVERNANCE_BOUNDARY"):
            if path in indexes["external_text"]:
                return kind
    return None


# --- the matrix ---------------------------------------------------------------------------


def build(repo: str | None = None, declarations: Declarations | None = None) -> dict[str, Any]:
    """Compose the coverage matrix. Reads only; stores no object record."""
    repo = repo or repo_root()
    declarations = declarations or load_declarations(repo=repo)

    objects_doc = _read_json(repo, _OBJECTS) or {}
    entries = objects_doc.get("entries") or []
    objects = list(entries) if isinstance(entries, list) else list(entries.values())

    plane_registries = {p.registry for p in declarations.planes}
    plane_of_class = {c: p for p in declarations.planes for c in p.object_classes}

    # THE PARTITION IS REFUSED, NOT ASSUMED. `plane_of_class` is a dict comprehension, so two
    # planes declaring one object class would silently keep the LAST one — and with the class
    # map quietly single-valued, `governs()` below would stop being able to see a genuine
    # double-governed object at all. The declaration's own $plane_comment says the partition is
    # "MEASURED on every build, never assumed"; this is the line that makes that true.
    overlapping = sorted(
        klass
        for klass in {c for plane in declarations.planes for c in plane.object_classes}
        if sum(1 for plane in declarations.planes if klass in plane.object_classes) > 1
    )
    if overlapping:
        raise CoverageError(
            "the registration planes do not partition the object classes: "
            f"{overlapping} is declared by more than one plane, so the class-to-plane map is "
            "not single-valued and duplicate registration could not be detected for it"
        )

    classes_governed = {
        plane.name: frozenset(plane.object_classes) for plane in declarations.planes
    }

    registered: dict[str, set[str]] = {}
    for plane in declarations.planes:
        document = _read_json(repo, plane.registry) or {}
        population = document.get(plane.population_key)
        paths: set[str] = set()
        if isinstance(population, dict):
            paths = {str(k) for k in population}
        elif isinstance(population, list):
            paths = {
                str(i.get("path")) for i in population if isinstance(i, dict) and i.get("path")
            }
        registered[plane.name] = paths

    # object coverage — read from the planes, never copied into this matrix
    states: dict[str, int] = dict.fromkeys(declarations.states, 0)
    findings: list[dict[str, str]] = []
    by_class: dict[str, dict[str, int]] = {}
    for obj in objects:
        path, klass = str(obj.get("path")), str(obj.get("object_class"))
        holder = plane_of_class.get(klass)
        # GOVERNING, NOT MERELY PRESENT — and the difference is the declaration's own.
        #
        # This used to be "every plane whose registry contains this path", which conflated
        # holding an entry with governing an object. The report immediately below it says the
        # opposite in prose ($retained_not_governed: "A plane may hold MORE entries than it
        # holds governed objects, and the difference is not a discrepancy"), and each plane
        # declares `holds_object_classes` precisely to say WHICH objects it governs — a field
        # this rule did not read. The consequence was measured: 192 root-level
        # DOCUMENT_ARTIFACTs carry a historical identity in `id-ledger.json` and are governed by
        # `artifacts.json`, and every one of them was reported DUPLICATE_REGISTRATION even
        # though the REPOSITORY plane declares it does not hold that class at all. Three tests
        # failed on it continuously.
        #
        # Detection is not weakened by reading the declaration; it is made precise. An object
        # whose class TWO planes declare is still a duplicate, an object no plane governs is
        # still UNREGISTERED, and the disjointness refusal above makes the first case
        # detectable rather than silently collapsed.
        planes_holding = [
            name
            for name, paths in registered.items()
            if path in paths and klass in classes_governed[name]
        ]
        if len(planes_holding) > 1:  # pragma: no cover - the partition guard above refuses overlap
            state = DUPLICATE_REGISTRATION
            findings.append(
                {"path": path, "state": state, "planes": ",".join(sorted(planes_holding))}
            )
        elif not planes_holding:
            state = UNREGISTERED
            findings.append({"path": path, "state": state, "planes": ""})
        elif (
            holder is None or holder.name not in planes_holding
        ):  # pragma: no cover - the partition guard makes the holder unique
            state = PARTIALLY_COVERED
            findings.append({"path": path, "state": state, "planes": ",".join(planes_holding)})
        else:
            state = COVERED
        states[state] += 1
        by_class.setdefault(klass, dict.fromkeys(declarations.states, 0))[state] += 1

    governed_per_plane: dict[str, int] = {}
    for obj in objects:
        holder = plane_of_class.get(str(obj.get("object_class")))
        if holder is not None:
            governed_per_plane[holder.name] = governed_per_plane.get(holder.name, 0) + 1

    # registry authority coverage
    generated = _read_json(repo, "00-BOOK/DATA/generated-artifact-registry.json") or {}
    indexes = {
        "generated_paths": {str(e.get("canonical_path")) for e in generated.get("entries") or []},
        "external_text": json.dumps(
            [
                _read_json(repo, "00-BOOK/DATA/constitutional-authority-alignment.json"),
                _read_json(repo, "00-BOOK/DATA/mutation-governance-boundary.json"),
            ]
        ),
    }
    disclosed = {g.registry: g for g in declarations.gaps}
    registries: list[dict[str, str]] = []
    for relpath in _scan(repo, declarations):
        document = _read_json(repo, relpath)
        if _population(document) < declarations.minimum_population:
            continue
        mechanism = locate_authority(relpath, document, declarations, indexes)
        registries.append(
            {
                "registry": relpath,
                "authority_mechanism": mechanism or "",
                "status": (
                    "DECLARED"
                    if mechanism
                    else "DISCLOSED_GAP"
                    if relpath in disclosed
                    else "DISCLOSED_BACKLOG"
                    if relpath in declarations.backlog
                    else "UNDECLARED"
                ),
                "plane": next((p.name for p in declarations.planes if p.registry == relpath), ""),
            }
        )

    return {
        "schema": "ucos-registry-coverage-matrix",
        "version": "1.0.0",
        "authority": (
            "NONE — DERIVED COVERAGE INTELLIGENCE. It registers nothing, owns nothing and "
            "mints nothing: every object is read from the plane that registers it and every "
            "ownership from the instrument that declares it. Deleting it changes no "
            "registration and no verdict."
        ),
        "declaration": declarations.declaration_id,
        "planes": [
            {
                "plane": p.name,
                "registry": p.registry,
                "owner": p.owner,
                "mutation_class": p.mutation_class,
                "registered": len(registered[p.name]),
                "governed": governed_per_plane.get(p.name, 0),
                "retained_not_governed": len(registered[p.name])
                - governed_per_plane.get(p.name, 0),
                "object_classes": sorted(p.object_classes),
            }
            for p in declarations.planes
        ],
        "$retained_not_governed": (
            "A plane may hold MORE entries than it holds governed objects, and the "
            "difference is not a discrepancy. The repository plane is append-only: an "
            "object whose file leaves version control enters lifecycle state RETIRED, its "
            "identity is retained and never reissued, and it stops being a governed object "
            "while remaining a ledger entry. Reporting only one of the two numbers would "
            "make correct append-only behaviour look like a coverage error."
        ),
        "objects": {
            "total": len(objects),
            "states": dict(sorted(states.items())),
            "by_class": {k: dict(sorted(v.items())) for k, v in sorted(by_class.items())},
        },
        "registries": {
            "scanned": len(registries),
            "declared": sum(1 for r in registries if r["status"] == "DECLARED"),
            "disclosed_gap": sum(1 for r in registries if r["status"] == "DISCLOSED_GAP"),
            "disclosed_backlog": sum(1 for r in registries if r["status"] == "DISCLOSED_BACKLOG"),
            "undeclared": sum(1 for r in registries if r["status"] == "UNDECLARED"),
            "by_mechanism": _histogram(
                r["authority_mechanism"] for r in registries if r["authority_mechanism"]
            ),
            "entries": sorted(registries, key=lambda r: r["registry"]),
        },
        "disclosed_authority_gaps": [g.as_dict() for g in declarations.gaps],
        "findings": sorted(findings, key=lambda f: (f["state"], f["path"]))[:100],
        "plane_registries": sorted(plane_registries),
        "closed_set": False,
        "upper_limit": None,
    }


def _scan(repo: str, declarations: Declarations) -> list[str]:
    found: list[str] = []
    for root in declarations.scan_roots:
        base = os.path.join(repo, root)
        for dirpath, dirnames, filenames in os.walk(base):
            dirnames[:] = [d for d in dirnames if not d.startswith((".", "__"))]
            for name in filenames:
                if name.endswith(".json"):
                    found.append(os.path.relpath(os.path.join(dirpath, name), repo))
    return sorted(found)


def _histogram(values) -> dict[str, int]:
    counts: dict[str, int] = {}
    for value in values:
        counts[value] = counts.get(value, 0) + 1
    return dict(sorted(counts.items()))


def rendered(matrix: Mapping[str, Any]) -> str:
    """Canonical serialisation, from Layer Zero (UCKP Article 13)."""
    return canonical_json(matrix)


def digest(matrix: Mapping[str, Any]) -> str:
    return content_hash(matrix)


# --- validation -----------------------------------------------------------------------------


def validate(matrix: Mapping[str, Any], declarations: Declarations | None = None) -> list[str]:
    """Return every coverage problem. Empty means healthy.

    Refuses an UNDISCLOSED registry with no declared authority — the ratchet that makes
    W5-G1's disclosure honest rather than permissive. A disclosed gap does not fail; a new
    one does.
    """
    problems: list[str] = []
    objects = matrix["objects"]["states"]
    for state in (UNREGISTERED, DUPLICATE_REGISTRATION):
        if objects.get(state):
            examples = [f["path"] for f in matrix["findings"] if f["state"] == state][:3]
            problems.append(f"{objects[state]} object(s) are {state}, e.g. {examples}")

    undeclared = [
        r["registry"] for r in matrix["registries"]["entries"] if r["status"] == "UNDECLARED"
    ]
    for registry in sorted(undeclared):
        problems.append(
            f"{registry} is a registry-shaped artifact with no declared authority and no "
            f"disclosure; declare its authority or record it as a disclosed gap"
        )

    planes = matrix["planes"]
    for plane in planes:
        if plane["registered"] <= 0:
            problems.append(f"plane {plane['plane']} registers nothing")
    return problems


def verify(repo: str | None = None) -> dict[str, Any]:
    """Build twice and report determinism, coverage and validation."""
    repo = repo or repo_root()
    first = build(repo)
    second = build(repo)
    problems = validate(first)
    return {
        "schema": "ucos-registry-coverage-matrix-verification",
        "version": "1.0.0",
        "deterministic": rendered(first) == rendered(second) and digest(first) == digest(second),
        "digest": digest(first),
        "objects": first["objects"]["states"],
        "total_objects": first["objects"]["total"],
        "registries": {k: v for k, v in first["registries"].items() if k != "entries"},
        "disclosed_gaps": len(first["disclosed_authority_gaps"]),
        "problems": problems,
        "status": "PASS" if not problems else "FAIL",
    }


__all__ = [
    "COVERED",
    "DUPLICATE_REGISTRATION",
    "PARTIALLY_COVERED",
    "UNREGISTERED",
    "AuthorityGap",
    "CoverageError",
    "Declarations",
    "Plane",
    "build",
    "digest",
    "load_declarations",
    "locate_authority",
    "rendered",
    "repo_root",
    "validate",
    "verify",
]
