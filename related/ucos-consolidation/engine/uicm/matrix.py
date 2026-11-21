"""UCOS-UICM-000001 — population assembly and the capability x dimension closure matrix.

This module is the home of the first capability UICM was admitted to create: **the
capability x dimension closure matrix**. Discovery established that no artifact in the
repository crosses those two axes. ``UAKOS-CLOSURE-002`` measures 549 *concepts*;
``UAKOS-CLOSURE-009`` projects them into requirements carrying one scalar maturity level
each and measures its fifteen lifecycle dimensions *repository-wide* rather than per
capability. The question "is capability X closed on dimension Y?" had no answer anywhere,
and this module is that answer.

The population is **read, never invented**. Three canonical owners supply every field:

    capability identity      knowledge/canonical-knowledge.json   (UCKO-CAP-*)
    artifact identity        00-MASTER/UCOS-UGA-001               (UCOS-* universal_id)
    implementation mapping   intelligence/UCOS-RIE-CAPABILITY-CATALOG.json

A capability is admitted only when the tracked boundary, the capability register and the
implementation catalogue *all three* name it. That conjunction is what makes "no invented
capability" a measurement rather than a promise: this module cannot produce a capability
that the canonical owners do not already carry, because it has no code path that
constructs one from anything else.

Note the import discipline. The implementation catalogue is consumed as **JSON**, never by
importing ``intelligence``: that package depends on ``engine``, so an import in this
direction would invert the layering and create a cycle. The dependency is on a file
format, which is exactly what a reference into another owner's register should be.
"""

from __future__ import annotations

import json
import tomllib
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from engine.omega_infinite.git_provider import GitDiscoveryProvider
from engine.omega_infinite.provider import ProviderError
from engine.uicm.model import (
    Capability,
    ClosureCell,
    ClosureDeclaration,
    ClosureError,
    ClosureState,
    digest,
    state_counts,
)
from engine.uicm.observation import ObservationRegistry

#: The matrix document format, so a digest is always attributable to the shape that
#: produced it.
MATRIX_FORMAT = "ucos-uicm-closure-matrix/1.0.0"


class PopulationError(ClosureError):
    """Raised when the population cannot be derived from the canonical owners."""


def _read_json(path: Path, *, what: str) -> Any:
    """Read a canonical owner's register, failing closed rather than substituting a default."""
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise PopulationError(f"{what} is unreadable: {path}") from exc
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise PopulationError(f"{what} is not valid JSON: {path}") from exc


def tracked_paths(repo: Path) -> tuple[str, ...]:
    """The artifact universe, as version control declares it.

    ``-z`` is not stylistic. Without it git *quotes* any path containing a non-ASCII
    byte, and this repository carries paths with ``Ω`` and ``∞`` in their names; a quoted
    path is a different string, so it would silently fail every lookup and be reported as
    an absence. Failure to resolve the boundary is refused rather than guessed: a
    population measured against an unknown boundary is not a measurement.
    """
    # THE PROVIDER, NOT THE TOOL. Same question (TRACKED_CONTENT), same flags, and the same
    # refusal: the provider raises rather than guessing a boundary, which is what the docstring
    # above demands. The `-z` handling that keeps `Ω` and `∞` paths unquoted is the provider's
    # too, so the non-ASCII property this module depends on is preserved rather than reimplemented.
    try:
        artifacts = GitDiscoveryProvider(root=str(repo)).enumerate()
    except ProviderError as exc:
        raise PopulationError("the artifact boundary is undefined and will not be guessed") from exc
    return tuple(sorted(artifact.location.locator for artifact in artifacts))


@dataclass(frozen=True, slots=True)
class CanonicalOwners:
    """The three canonical owners plus the located registration and binding sources.

    Every attribute is a projection of somebody else's register. This class owns none of
    the data it exposes; it is the adapter layer the discovery report promised.
    """

    capability_identity: Mapping[str, Mapping[str, Any]]
    capability_identity_duplicates: Mapping[str, int]
    artifact_identity: Mapping[str, Mapping[str, Any]]
    implementation: Mapping[str, tuple[Mapping[str, Any], ...]]
    coverage_source: frozenset[str]
    coverage_addopts: frozenset[str]
    entrypoints: Mapping[str, str]
    workflows: Mapping[str, str]
    verification_text: str
    tracked: tuple[str, ...]

    @classmethod
    def load(cls, repo: Path, declaration: ClosureDeclaration) -> CanonicalOwners:
        """Load every declared source. Absence of a required source fails closed."""
        repo = Path(repo)

        cap_src = declaration.source("capability_identity")
        cap_doc = _read_json(repo / str(cap_src["path"]), what="capability identity register")
        prefix = str(cap_src["title_prefix"])
        universe = str(cap_src["universe"])
        identities: dict[str, Mapping[str, Any]] = {}
        duplicates: dict[str, int] = {}
        for record in cap_doc[str(cap_src["root_key"])]:
            if record.get("universe") != universe:
                continue
            title = str(record.get("title", ""))
            if not title.startswith(prefix):
                continue
            name = title[len(prefix) :]
            duplicates[name] = duplicates.get(name, 0) + 1
            identities.setdefault(name, record)

        art_src = declaration.source("artifact_identity")
        art_doc = _read_json(repo / str(art_src["path"]), what="artifact identity register")
        artifacts = {
            str(entry[str(art_src["path_field"])]): entry
            for entry in art_doc[str(art_src["root_key"])]
        }

        impl_src = declaration.source("implementation_intelligence")
        impl_doc = _read_json(repo / str(impl_src["path"]), what="implementation catalogue")
        implementation: dict[str, list[Mapping[str, Any]]] = {}
        for record in impl_doc[str(impl_src["root_key"])]:
            implementation.setdefault(str(record[str(impl_src["location_field"])]), []).append(
                record
            )

        reg_src = declaration.source("registration")
        reg_path = repo / str(reg_src["path"])
        try:
            with reg_path.open("rb") as handle:
                pyproject = tomllib.load(handle)
        except (OSError, tomllib.TOMLDecodeError) as exc:
            raise PopulationError(f"registration source is unreadable: {reg_path}") from exc
        cov_source = frozenset(str(v) for v in _dig(pyproject, reg_src["coverage_source_key"]))
        cov_prefix = str(reg_src["coverage_addopts_prefix"])
        cov_addopts = frozenset(
            str(v)[len(cov_prefix) :]
            for v in _dig(pyproject, reg_src["coverage_addopts_key"])
            if str(v).startswith(cov_prefix)
        )
        scripts = {str(k): str(v) for k, v in dict(_dig(pyproject, reg_src["scripts_key"])).items()}

        gate_src = declaration.source("gate_binding")
        gate_dir = repo / str(gate_src["path"])
        suffix = str(gate_src["suffix"])
        if not gate_dir.is_dir():
            raise PopulationError(f"gate binding source is absent: {gate_dir}")
        workflows = {
            child.name: child.read_text(encoding="utf-8", errors="replace")
            for child in sorted(gate_dir.iterdir())
            if child.suffix == suffix
        }

        ver_src = declaration.source("verification_binding")
        ver_path = repo / str(ver_src["path"])
        try:
            verification_text = ver_path.read_text(encoding="utf-8")
        except OSError as exc:
            raise PopulationError(f"verification binding source is absent: {ver_path}") from exc

        return cls(
            capability_identity=identities,
            capability_identity_duplicates=duplicates,
            artifact_identity=artifacts,
            implementation={k: tuple(v) for k, v in implementation.items()},
            coverage_source=cov_source,
            coverage_addopts=cov_addopts,
            entrypoints=scripts,
            workflows=workflows,
            verification_text=verification_text,
            tracked=tracked_paths(repo),
        )

    def source_digests(self) -> dict[str, str]:
        """Digests of the consumed owner projections — the evidence anchor for reuse."""
        return {
            "capability_identity": digest(
                {k: v.get("cko_id") for k, v in sorted(self.capability_identity.items())}
            ),
            "artifact_identity": digest(
                {k: v.get("universal_id") for k, v in sorted(self.artifact_identity.items())}
            ),
            "implementation": digest(
                {
                    k: [r.get("implementation_status") for r in v]
                    for k, v in sorted(self.implementation.items())
                }
            ),
            "registration": digest(
                {
                    "coverage_source": sorted(self.coverage_source),
                    "coverage_addopts": sorted(self.coverage_addopts),
                    "entrypoints": dict(sorted(self.entrypoints.items())),
                }
            ),
            "boundary": digest(list(self.tracked)),
        }


def _dig(document: Mapping[str, Any], keys: Sequence[Any]) -> Any:
    """Walk a declared key path into a document, failing closed on a missing key."""
    node: Any = document
    for key in keys:
        if not isinstance(node, Mapping) or key not in node:
            raise PopulationError(f"declared key path is absent: {'.'.join(map(str, keys))}")
        node = node[key]
    return node


def discover_population(
    repo: Path,
    declaration: ClosureDeclaration,
    owners: CanonicalOwners,
) -> tuple[Capability, ...]:
    """Derive the capability population by rule from the tracked boundary.

    The rule is declared, not coded: roots, depth, excluded namespaces, the package
    marker and the artifact extension all come from the declaration, so admitting a
    capability is an append-only edit to the canonical sources.

    A candidate is admitted only if the capability register *and* the implementation
    catalogue both name it. A candidate the boundary carries but a register does not is
    not silently admitted under a minted identity — it is left out and surfaced as an
    orphan by :mod:`engine.uicm.validation`, because inventing an identity here is
    precisely the duplicate-identity failure UICM is forbidden.
    """
    population = declaration.population
    roots = declaration.capability_roots
    excluded = declaration.excluded_namespaces
    marker = str(population["package_marker"])
    extension = str(population["artifact_extension"])
    depth_max = int(population["capability_depth_max"])

    tracked = set(owners.tracked)
    candidates: list[str] = []
    for root in roots:
        if f"{root}/{marker}" in tracked:
            candidates.append(root)
        if depth_max < 1:
            continue
        children = {
            path.split("/")[1]
            for path in tracked
            if path.startswith(f"{root}/") and path.count("/") >= 2
        }
        for child in sorted(children):
            if child in excluded:
                continue
            if f"{root}/{child}/{marker}" in tracked:
                candidates.append(f"{root}/{child}")

    impl_src = declaration.source("implementation_intelligence")
    status_field = str(impl_src["status_field"])
    reuse_field = str(impl_src["reuse_field"])
    prohibited_field = str(impl_src["prohibited_field"])
    cap_src = declaration.source("capability_identity")
    art_src = declaration.source("artifact_identity")

    discovered: list[Capability] = []
    for location in candidates:
        name = location.replace("/", ".")
        identity = owners.capability_identity.get(name)
        implementation = owners.implementation.get(location)
        if identity is None or not implementation:
            continue
        if location == name:
            artifacts = (f"{location}/{marker}",)
        else:
            artifacts = tuple(
                sorted(
                    path
                    for path in tracked
                    if path.startswith(f"{location}/") and path.endswith(extension)
                )
            )
        identified = tuple(p for p in artifacts if p in owners.artifact_identity)
        unidentified = tuple(p for p in artifacts if p not in owners.artifact_identity)
        record = implementation[0]
        discovered.append(
            Capability(
                capability_id=str(identity[str(cap_src["id_field"])]),
                name=name,
                location=location,
                canonical_owner=str(identity[str(cap_src["owner_field"])]),
                knowledge_reference=(f"{cap_src['path']}#{identity[str(cap_src['id_field'])]}"),
                lifecycle=str(identity.get(str(cap_src["lifecycle_field"]), "")),
                authority=str(identity.get(str(cap_src["authority_field"]), "")),
                implementation_location=location,
                implementation_status=str(record[status_field]),
                reuse_disposition=str(record.get(reuse_field, "")),
                replacement_prohibited=bool(record.get(prohibited_field, False)),
                artifacts=artifacts,
                identified_artifacts=identified,
                unidentified_artifacts=unidentified,
                artifact_identities=tuple(
                    str(owners.artifact_identity[p][str(art_src["id_field"])]) for p in identified
                ),
                artifact_digests=tuple(
                    str(owners.artifact_identity[p].get(str(art_src["digest_field"]), ""))
                    for p in identified
                ),
            )
        )
    if not discovered:
        raise PopulationError("the declared population rule admitted no capability")
    return tuple(sorted(discovered, key=lambda c: c.name))


@dataclass(frozen=True, slots=True)
class ClosureMatrix:
    """The capability x dimension closure matrix — a view over current observations.

    The matrix holds no state of its own. Its cells are projected from the live readings in
    the observation registry, so the grid and the history cannot disagree about what was
    measured: there is only one place a state is recorded, and this is not it.

    Totality is not an aspiration: :meth:`project` fills every coordinate from the
    registry, and :meth:`require_total` re-measures the cardinality so a partially built
    matrix cannot be mistaken for a complete one.
    """

    declaration_digest: str
    capabilities: tuple[Capability, ...]
    dimension_ids: tuple[str, ...]
    cells: tuple[ClosureCell, ...]
    source_digests: Mapping[str, str]
    observation_head: str
    observation_total: int

    @classmethod
    def project(
        cls,
        *,
        declaration: ClosureDeclaration,
        capabilities: Sequence[Capability],
        observations: ObservationRegistry,
        source_digests: Mapping[str, str],
    ) -> ClosureMatrix:
        """Project the registry's current observations into the matrix."""
        observations.require_intact()
        matrix = cls(
            declaration_digest=declaration.digest(),
            capabilities=tuple(capabilities),
            dimension_ids=declaration.dimension_ids,
            cells=tuple(
                sorted(
                    observations.cells(),
                    key=lambda c: (c.capability_name, _ordinal(declaration, c)),
                )
            ),
            source_digests=dict(source_digests),
            observation_head=observations.head_hash,
            observation_total=len(observations),
        )
        matrix.require_total()
        return matrix

    def require_total(self) -> None:
        """Fail closed unless the matrix holds exactly one cell per coordinate."""
        expected = len(self.capabilities) * len(self.dimension_ids)
        if len(self.cells) != expected:
            raise ClosureError(
                "closure matrix is not total",
                cells=len(self.cells),
                expected=expected,
            )
        seen = {cell.key for cell in self.cells}
        if len(seen) != expected:
            raise ClosureError("closure matrix carries a duplicate coordinate")

    @property
    def cell_count(self) -> int:
        return len(self.cells)

    def cell(self, capability_name: str, dimension_id: str) -> ClosureCell:
        """Return one coordinate, or fail closed."""
        for candidate in self.cells:
            if candidate.capability_name == capability_name and (
                candidate.dimension_id == dimension_id
            ):
                return candidate
        raise ClosureError(f"no closure cell at coordinate {capability_name}:{dimension_id}")

    def by_capability(self) -> dict[str, tuple[ClosureCell, ...]]:
        grouped: dict[str, list[ClosureCell]] = {c.name: [] for c in self.capabilities}
        for cell in self.cells:
            grouped[cell.capability_name].append(cell)
        return {name: tuple(cells) for name, cells in grouped.items()}

    def by_dimension(self) -> dict[str, tuple[ClosureCell, ...]]:
        grouped: dict[str, list[ClosureCell]] = {d: [] for d in self.dimension_ids}
        for cell in self.cells:
            grouped[cell.dimension_id].append(cell)
        return {name: tuple(cells) for name, cells in grouped.items()}

    def capability_state(self, capability_name: str) -> ClosureState:
        """The weakest state across a capability's row — closure is a conjunction.

        A capability is only as closed as its least closed dimension, so the row state is
        the minimum by lifecycle ordinal rather than any average. An average would let a
        capability with one unmeasurable dimension present as nearly closed.
        """
        row = [c for c in self.cells if c.capability_name == capability_name]
        if not row:
            raise ClosureError(f"no closure row for capability {capability_name}")
        return min((c.state for c in row), key=lambda s: s.ordinal)

    def dimension_counts(self) -> dict[str, dict[str, int]]:
        return {name: state_counts(cells) for name, cells in self.by_dimension().items()}

    def state_counts(self) -> dict[str, int]:
        return state_counts(self.cells)

    def non_pass_cells(self) -> tuple[ClosureCell, ...]:
        return tuple(cell for cell in self.cells if not cell.is_pass)

    def to_document(self) -> dict[str, Any]:
        return {
            "format": MATRIX_FORMAT,
            "declaration_digest": self.declaration_digest,
            "observation_head": self.observation_head,
            "observation_total": self.observation_total,
            "capability_count": len(self.capabilities),
            "dimension_count": len(self.dimension_ids),
            "cell_count": self.cell_count,
            "state_counts": self.state_counts(),
            "dimension_counts": self.dimension_counts(),
            "source_digests": dict(sorted(self.source_digests.items())),
            "capabilities": [c.to_dict() for c in self.capabilities],
            "cells": [c.to_dict() for c in self.cells],
        }

    def digest(self) -> str:
        return digest(self.to_document())


def _ordinal(declaration: ClosureDeclaration, cell: ClosureCell) -> int:
    return declaration.dimension(cell.dimension_id).ordinal


__all__ = [
    "MATRIX_FORMAT",
    "CanonicalOwners",
    "ClosureMatrix",
    "PopulationError",
    "discover_population",
    "tracked_paths",
]
