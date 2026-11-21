"""UCOS-CTRL-000001 — Universal Repository Truth Engine (Wave 1).

The control plane's answer to *what is actually in this repository*. Before this
engine the control plane could describe a universe only if someone typed it into
Python; now it derives one from what the repository already records.

Nothing here re-implements discovery. Three existing capabilities are composed:

    :mod:`engine.registry`          the read-only ``00-BOOK`` registry substrate —
                                    1220 registered artifacts, their owners,
                                    versions, content hashes and traceability, and
                                    the 12,873-edge relationship graph.
    :mod:`platform.universal_truth` the declared Repository Truth policy — which
                                    locators are canonical, which are evidence,
                                    derived, historical or transient, and which
                                    may hold ownership at all.
    the sealed RIE capability catalogue, read as an artifact so control-plane
                                    discovery costs no repository-wide AST pass.

Everything repository-specific — which documents hold Truth, which artifact
categories constitute a governance record — arrives from the declared manifest
(:mod:`platform.universal_control_plane.manifest`). This module contains no path
literal and no artifact identifier: point it at a different manifest and it
discovers a different repository.

Discovery is deterministic and replayable. Registry envelopes carry a
``generated_at`` wall-clock; it is deliberately excluded from every digest, so the
truth identity is a function of repository *content* and a re-run over unchanged
data reproduces the identical ``truth_id``.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from platform.universal_control_plane.errors import ObjectNotFoundError, TruthDiscoveryError
from platform.universal_control_plane.manifest import ControlPlaneManifest, default_manifest
from platform.universal_control_plane.ontology import (
    LIFECYCLE_ACTIVE,
    TRUTH_UNCLASSIFIED,
    ArtifactRecord,
    Capability,
    DependencyRecord,
    OwnershipRecord,
    payload_digest,
)
from typing import Any

#: Registry document names the engine resolves through the declared manifest.
DOC_ARTIFACTS = "artifacts"
DOC_RELATIONSHIPS = "relationships"
DOC_CERTIFICATION = "certification"
DOC_CHANGE_LEDGER = "change_ledger"

#: Relationship types that express a dependency edge in the control-plane sense.
#: Declared here rather than in the manifest because they are the *registry's*
#: vocabulary, not the repository's — they travel with the reader that reads them.
DEPENDENCY_EDGE_TYPES: tuple[str, ...] = ("Depends-On", "Consumes", "Implements")

#: Envelope keys excluded from every source digest: a regeneration timestamp is
#: not content, and admitting one would make truth identity unreproducible.
_VOLATILE_ENVELOPE_KEYS = frozenset({"generated_at", "generator_version", "evidence_timestamp"})


def _stable(document: Mapping[str, Any]) -> dict[str, Any]:
    """A document with its volatile envelope keys removed."""
    return {k: v for k, v in document.items() if k not in _VOLATILE_ENVELOPE_KEYS}


@dataclass(frozen=True, slots=True)
class TruthSource:
    """One declared source that contributed facts, and the digest of what it held."""

    source_id: str
    kind: str
    locator: str
    digest: str
    record_count: int = 0
    available: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_id": self.source_id,
            "kind": self.kind,
            "locator": self.locator,
            "digest": self.digest,
            "record_count": self.record_count,
            "available": self.available,
        }


@dataclass(frozen=True, slots=True)
class RepositoryTruth:
    """An immutable, content-addressed snapshot of discovered Repository Truth."""

    universe_id: str
    manifest_id: str
    policy_id: str
    sources: tuple[TruthSource, ...]
    artifacts: tuple[ArtifactRecord, ...]
    capabilities: tuple[Capability, ...]
    ownership: tuple[OwnershipRecord, ...]
    dependencies: tuple[DependencyRecord, ...]
    registrations: tuple[ArtifactRecord, ...]
    certifications: tuple[ArtifactRecord, ...]
    determinations: tuple[ArtifactRecord, ...]
    evidence: tuple[ArtifactRecord, ...]
    governance: tuple[ArtifactRecord, ...]
    certification_document: Mapping[str, Any] = field(default_factory=dict)
    change_ledger: Mapping[str, Any] = field(default_factory=dict)
    tick: int = 0

    @property
    def truth_id(self) -> str:
        """The content-addressed identity of this snapshot."""
        return payload_digest(self.core())

    def core(self) -> dict[str, Any]:
        """The hashable core: discovered content only, no wall-clock."""
        return {
            "universe_id": self.universe_id,
            "manifest_id": self.manifest_id,
            "policy_id": self.policy_id,
            "sources": [s.to_dict() for s in self.sources],
            "artifacts": [a.artifact_id for a in self.artifacts],
            "capabilities": [c.capability_id for c in self.capabilities],
            "ownership": [o.ownership_id for o in self.ownership],
            "dependencies": [d.dependency_id for d in self.dependencies],
        }

    def counts(self) -> dict[str, int]:
        return {
            "artifacts": len(self.artifacts),
            "capabilities": len(self.capabilities),
            "ownership": len(self.ownership),
            "dependencies": len(self.dependencies),
            "registrations": len(self.registrations),
            "certifications": len(self.certifications),
            "determinations": len(self.determinations),
            "evidence": len(self.evidence),
            "governance": len(self.governance),
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "engine": "RepositoryTruthEngine",
            "truth_id": self.truth_id,
            "universe_id": self.universe_id,
            "manifest_id": self.manifest_id,
            "policy_id": self.policy_id,
            "tick": self.tick,
            "counts": self.counts(),
            "sources": [s.to_dict() for s in self.sources],
        }


# ---------------------------------------------------------------------------
# Readers — each returns records plus the digest of what it read
# ---------------------------------------------------------------------------


def _read_registry_document(
    source: Any, manifest: ControlPlaneManifest, name: str
) -> tuple[Mapping[str, Any], list[Any], TruthSource]:
    """Read a declared registry document through the reused registry source."""
    ref = manifest.document(name)
    try:
        document = source.read_json(ref.filename)
    except Exception as exc:  # noqa: BLE001 — every reader fault is one failure mode here
        raise TruthDiscoveryError(
            f"declared registry document {name!r} ({ref.filename}) could not be read: {exc}"
        ) from exc
    if not isinstance(document, Mapping):
        raise TruthDiscoveryError(f"registry document {name!r} is not a JSON object")
    records: list[Any] = []
    if ref.root_key:
        raw = document.get(ref.root_key)
        if not isinstance(raw, list):
            raise TruthDiscoveryError(
                f"registry document {name!r} has no {ref.root_key!r} records array"
            )
        records = raw
    stable = _stable(document)
    return (
        document,
        records,
        TruthSource(
            source_id=name,
            kind="REGISTRY",
            locator=ref.filename,
            digest=payload_digest(stable),
            record_count=len(records) if ref.root_key else len(stable),
        ),
    )


def _read_capability_catalog(
    manifest: ControlPlaneManifest, repository_root: Path
) -> tuple[list[Mapping[str, Any]], TruthSource]:
    """Read the declared capability catalogue artifact (absent is not fatal)."""
    import json

    locator = manifest.capability_catalog_locator
    path = repository_root / locator
    if not path.is_file():
        return [], TruthSource(
            source_id="capability_catalog",
            kind="DERIVED",
            locator=locator,
            digest="",
            available=False,
        )
    try:
        document = json.loads(path.read_text("utf-8"))
    except (OSError, ValueError) as exc:
        raise TruthDiscoveryError(
            f"declared capability catalogue {locator} could not be read: {exc}"
        ) from exc
    entries = document.get(manifest.capability_catalog_root_key)
    if not isinstance(entries, list):
        raise TruthDiscoveryError(
            f"capability catalogue {locator} has no "
            f"{manifest.capability_catalog_root_key!r} records array"
        )
    records = [e for e in entries if isinstance(e, Mapping)]
    return records, TruthSource(
        source_id="capability_catalog",
        kind="DERIVED",
        locator=locator,
        digest=payload_digest([_stable(e) for e in records]),
        record_count=len(records),
    )


# ---------------------------------------------------------------------------
# The engine
# ---------------------------------------------------------------------------


@dataclass
class RepositoryTruthEngine:
    """Discovers Repository Truth and projects it into control-plane objects.

    Construct it with :meth:`discover` for a live repository, or directly with
    already-read documents when replaying a recorded snapshot — the projection is
    a pure function of its inputs either way.
    """

    manifest: ControlPlaneManifest
    _artifact_records: tuple[Mapping[str, Any], ...] = ()
    _relationship_records: tuple[Mapping[str, Any], ...] = ()
    _catalog_records: tuple[Mapping[str, Any], ...] = ()
    _certification_document: Mapping[str, Any] = field(default_factory=dict)
    _change_ledger: Mapping[str, Any] = field(default_factory=dict)
    _sources: tuple[TruthSource, ...] = ()
    _policy: Any = None
    _cache: dict[str, Any] = field(default_factory=dict, repr=False)

    # -- construction ----------------------------------------------------

    @classmethod
    def discover(
        cls,
        *,
        manifest: ControlPlaneManifest | None = None,
        data_dir: Path | str | None = None,
        repository_root: Path | str | None = None,
        policy: Any = None,
    ) -> RepositoryTruthEngine:
        """Discover Repository Truth from the declared sources.

        Every source is reached through an existing reader: the registry documents
        through :class:`engine.registry.RegistrySource`, the truth policy through
        :func:`platform.universal_truth.default_truth_policy`. Nothing is scanned
        that another capability already indexes.
        """
        from platform.repository_intelligence.config import resolve_repository_root
        from platform.universal_truth.policy import default_truth_policy

        from engine.registry.source import RegistrySource

        resolved_manifest = manifest or default_manifest()
        try:
            source = RegistrySource(data_dir)
        except Exception as exc:  # noqa: BLE001
            raise TruthDiscoveryError(f"registry substrate is unreachable: {exc}") from exc

        root = Path(repository_root) if repository_root else resolve_repository_root()

        _, artifacts, artifact_src = _read_registry_document(
            source, resolved_manifest, DOC_ARTIFACTS
        )
        _, relationships, rel_src = _read_registry_document(
            source, resolved_manifest, DOC_RELATIONSHIPS
        )
        cert_doc, _, cert_src = _read_registry_document(
            source, resolved_manifest, DOC_CERTIFICATION
        )
        ledger_doc, _, ledger_src = _read_registry_document(
            source, resolved_manifest, DOC_CHANGE_LEDGER
        )
        catalog, catalog_src = _read_capability_catalog(resolved_manifest, root)

        return cls(
            manifest=resolved_manifest,
            _artifact_records=tuple(r for r in artifacts if isinstance(r, Mapping)),
            _relationship_records=tuple(r for r in relationships if isinstance(r, Mapping)),
            _catalog_records=tuple(catalog),
            _certification_document=_stable(cert_doc),
            _change_ledger=_stable(ledger_doc),
            _sources=(artifact_src, rel_src, cert_src, ledger_src, catalog_src),
            _policy=policy if policy is not None else default_truth_policy(),
        )

    # -- classification --------------------------------------------------

    def classify(self, locator: str) -> tuple[str, bool]:
        """Classify *locator* by declared Repository Truth policy.

        Returns ``(truth_class, canonical_home_eligible)``. An empty or
        unclassifiable locator is reported as an honest absence rather than being
        defaulted into Truth.
        """
        if self._policy is None or not locator.strip():
            return TRUTH_UNCLASSIFIED, False
        try:
            classification = self._policy.classify(locator)
        except Exception:  # noqa: BLE001 — an unclassifiable locator is an absence
            return TRUTH_UNCLASSIFIED, False
        truth_class = getattr(classification.truth_class, "value", classification.truth_class)
        return str(truth_class), bool(classification.canonical_home_eligible)

    # -- discovery: artifacts --------------------------------------------

    def artifacts(self, *, tick: int = 0) -> tuple[ArtifactRecord, ...]:
        """Every registered artifact, classified by truth class and artifact class."""
        cached = self._cache.get(f"artifacts:{tick}")
        if cached is not None:
            return cached
        records: list[ArtifactRecord] = []
        for raw in self._artifact_records:
            artifact_id = str(raw.get("universal_id", "")).strip()
            if not artifact_id:
                continue
            locator = str(raw.get("path", "") or "")
            truth_class, eligible = self.classify(locator)
            category = str(raw.get("category", "") or "")
            program = str(raw.get("program", "") or "")
            trace = raw.get("traceability") or {}
            references: list[str] = []
            if isinstance(trace, Mapping):
                for stage in sorted(trace):
                    values = trace.get(stage)
                    if isinstance(values, Sequence) and not isinstance(values, str | bytes):
                        references.extend(str(v) for v in values)
            records.append(
                ArtifactRecord(
                    artifact_id=artifact_id,
                    name=str(raw.get("name", "") or ""),
                    category=category,
                    status=str(raw.get("status", "") or ""),
                    version=str(raw.get("version", "") or ""),
                    owner=str(raw.get("owner", "") or ""),
                    locator=locator,
                    truth_class=truth_class,
                    canonical_home_eligible=eligible,
                    content_digest=str(raw.get("content_hash", "") or ""),
                    program=program,
                    volume=str(raw.get("volume", "") or ""),
                    dependencies=tuple(
                        str(d) for d in (raw.get("dependencies") or ()) if isinstance(d, str)
                    ),
                    classes=self.manifest.classify_artifact(category=category, program=program),
                    traceability=tuple(dict.fromkeys(references)),
                    tick=tick,
                )
            )
        result = tuple(sorted(records, key=lambda a: a.artifact_id))
        self._cache[f"artifacts:{tick}"] = result
        return result

    def artifact(self, artifact_id: str, *, tick: int = 0) -> ArtifactRecord:
        for record in self.artifacts(tick=tick):
            if record.artifact_id == artifact_id:
                return record
        raise ObjectNotFoundError(f"artifact not found in Repository Truth: {artifact_id}")

    def artifacts_in_class(self, class_id: str, *, tick: int = 0) -> tuple[ArtifactRecord, ...]:
        """Every artifact admitted by the declared artifact class *class_id*."""
        self.manifest.artifact_class(class_id)  # fail closed on an undeclared class
        return tuple(a for a in self.artifacts(tick=tick) if a.in_class(class_id))

    # The five declared artifact classes, each a first-class discovery surface.

    def registrations(self, *, tick: int = 0) -> tuple[ArtifactRecord, ...]:
        return self.artifacts_in_class("registration", tick=tick)

    def certifications(self, *, tick: int = 0) -> tuple[ArtifactRecord, ...]:
        return self.artifacts_in_class("certification", tick=tick)

    def determinations(self, *, tick: int = 0) -> tuple[ArtifactRecord, ...]:
        return self.artifacts_in_class("determination", tick=tick)

    def evidence(self, *, tick: int = 0) -> tuple[ArtifactRecord, ...]:
        return self.artifacts_in_class("evidence", tick=tick)

    def governance_records(self, *, tick: int = 0) -> tuple[ArtifactRecord, ...]:
        return self.artifacts_in_class("governance", tick=tick)

    # -- discovery: capabilities -----------------------------------------

    def capabilities(self, *, tick: int = 0) -> tuple[Capability, ...]:
        """Every capability the sealed catalogue declares, as control-plane objects."""
        cached = self._cache.get(f"capabilities:{tick}")
        if cached is not None:
            return cached
        capabilities: list[Capability] = []
        for raw in self._catalog_records:
            name = str(raw.get("canonical_name", "") or "").strip()
            if not name:
                continue
            location = str(raw.get("canonical_location", "") or "")
            truth_class, eligible = self.classify(location)
            capabilities.append(
                Capability(
                    capability_id=name,
                    universe_id=self.manifest.universe_id,
                    name=name,
                    description=str(raw.get("description", "") or ""),
                    state=LIFECYCLE_ACTIVE,
                    version=str(raw.get("version", "") or "1.0.0"),
                    attributes={
                        "category": str(raw.get("category", "") or ""),
                        "authority": str(raw.get("authority", "") or ""),
                        "reuse": str(raw.get("reuse", "") or ""),
                        "implementation_status": str(raw.get("implementation_status", "") or ""),
                        "replacement_prohibited": bool(raw.get("replacement_prohibited", False)),
                        "location": location,
                        "truth_class": truth_class,
                        "canonical_home_eligible": eligible,
                    },
                    tick=tick,
                )
            )
        result = tuple(sorted(capabilities, key=lambda c: c.capability_id))
        self._cache[f"capabilities:{tick}"] = result
        return result

    # -- discovery: ownership --------------------------------------------

    def ownership(self, *, tick: int = 0) -> tuple[OwnershipRecord, ...]:
        """Discovered ownership: one binding per artifact that declares an owner.

        An artifact whose declared home cannot hold ownership (evidence, derived
        output, historical state) still yields a record — the control plane records
        the claim and lets the Governance Engine adjudicate it, rather than
        silently dropping a binding the repository does declare.
        """
        cached = self._cache.get(f"ownership:{tick}")
        if cached is not None:
            return cached
        records = tuple(
            OwnershipRecord(
                ownership_id=f"OWN-{artifact.artifact_id}",
                capability_id=artifact.artifact_id,
                owner_id=artifact.owner,
                owner_kind="Artifact",
                rationale=f"declared owner of {artifact.artifact_id} in the registry substrate",
                attributes={
                    "truth_class": artifact.truth_class,
                    "canonical_home_eligible": artifact.canonical_home_eligible,
                },
                tick=tick,
            )
            for artifact in self.artifacts(tick=tick)
            if artifact.owner
        )
        self._cache[f"ownership:{tick}"] = records
        return records

    def owner_of(self, subject_id: str, *, tick: int = 0) -> str:
        """The declared owner of *subject_id*, or the empty string when none is declared."""
        for record in self.ownership(tick=tick):
            if record.capability_id == subject_id:
                return record.owner_id
        return ""

    # -- discovery: dependencies -----------------------------------------

    def dependencies(self, *, tick: int = 0) -> tuple[DependencyRecord, ...]:
        """Discovered dependency edges, projected from the registry relationship graph.

        Only forward edge types are admitted: the registry stores each dependency
        twice (``Depends-On`` and its ``Required-By`` inverse), and admitting both
        would put a cycle between every pair of related artifacts.
        """
        cached = self._cache.get(f"dependencies:{tick}")
        if cached is not None:
            return cached
        records: list[DependencyRecord] = []
        for raw in self._relationship_records:
            edge_type = str(raw.get("type", "") or "")
            if edge_type not in DEPENDENCY_EDGE_TYPES:
                continue
            from_id = str(raw.get("from", "") or "")
            to_id = str(raw.get("to", "") or "")
            if not from_id or not to_id or from_id == to_id:
                continue
            records.append(
                DependencyRecord(
                    dependency_id=str(raw.get("edge_id", f"{from_id}->{to_id}")),
                    from_id=from_id,
                    to_id=to_id,
                    kind=edge_type.upper().replace("-", "_"),
                    attributes={"note": str(raw.get("note", "") or "")},
                    tick=tick,
                )
            )
        result = tuple(sorted(records, key=lambda d: d.dependency_id))
        self._cache[f"dependencies:{tick}"] = result
        return result

    def dependencies_of(self, subject_id: str, *, tick: int = 0) -> tuple[str, ...]:
        return tuple(
            sorted({d.to_id for d in self.dependencies(tick=tick) if d.from_id == subject_id})
        )

    def dependents_of(self, subject_id: str, *, tick: int = 0) -> tuple[str, ...]:
        return tuple(
            sorted({d.from_id for d in self.dependencies(tick=tick) if d.to_id == subject_id})
        )

    # -- discovery: raw declared documents -------------------------------

    @property
    def certification_document(self) -> Mapping[str, Any]:
        """The declared repository certification document (verdict + domain checks)."""
        return self._certification_document

    @property
    def change_ledger(self) -> Mapping[str, Any]:
        """The declared change ledger (version records, lineage, change events)."""
        return self._change_ledger

    @property
    def sources(self) -> tuple[TruthSource, ...]:
        return self._sources

    def source(self, source_id: str) -> TruthSource:
        for src in self._sources:
            if src.source_id == source_id:
                return src
        raise ObjectNotFoundError(f"truth source not declared: {source_id}")

    # -- snapshot --------------------------------------------------------

    def truth(self, *, tick: int = 0) -> RepositoryTruth:
        """The full, content-addressed Repository Truth snapshot."""
        policy_id = getattr(self._policy, "policy_id", "") if self._policy is not None else ""
        return RepositoryTruth(
            universe_id=self.manifest.universe_id,
            manifest_id=self.manifest.manifest_id,
            policy_id=str(policy_id),
            sources=self._sources,
            artifacts=self.artifacts(tick=tick),
            capabilities=self.capabilities(tick=tick),
            ownership=self.ownership(tick=tick),
            dependencies=self.dependencies(tick=tick),
            registrations=self.registrations(tick=tick),
            certifications=self.certifications(tick=tick),
            determinations=self.determinations(tick=tick),
            evidence=self.evidence(tick=tick),
            governance=self.governance_records(tick=tick),
            certification_document=self._certification_document,
            change_ledger=self._change_ledger,
            tick=tick,
        )

    def to_dict(self, *, tick: int = 0) -> dict[str, Any]:
        return self.truth(tick=tick).to_dict()


def build_truth_engine(
    *,
    artifacts: Iterable[Mapping[str, Any]] = (),
    relationships: Iterable[Mapping[str, Any]] = (),
    capabilities: Iterable[Mapping[str, Any]] = (),
    certification: Mapping[str, Any] | None = None,
    change_ledger: Mapping[str, Any] | None = None,
    manifest: ControlPlaneManifest | None = None,
    policy: Any = None,
) -> RepositoryTruthEngine:
    """Build a truth engine over supplied records rather than a live repository.

    The projection is identical; only the reader differs. This is the seam durable
    replay uses to reconstruct a past snapshot, and the seam a test uses to pin
    behaviour without a 1,220-artifact read.
    """
    return RepositoryTruthEngine(
        manifest=manifest or default_manifest(),
        _artifact_records=tuple(artifacts),
        _relationship_records=tuple(relationships),
        _catalog_records=tuple(capabilities),
        _certification_document=dict(certification or {}),
        _change_ledger=dict(change_ledger or {}),
        _sources=(
            TruthSource("artifacts", "SUPPLIED", "-", payload_digest(list(artifacts))),
            TruthSource("capability_catalog", "SUPPLIED", "-", payload_digest(list(capabilities))),
        ),
        _policy=policy,
    )


__all__ = [
    "DEPENDENCY_EDGE_TYPES",
    "DOC_ARTIFACTS",
    "DOC_CERTIFICATION",
    "DOC_CHANGE_LEDGER",
    "DOC_RELATIONSHIPS",
    "RepositoryTruth",
    "RepositoryTruthEngine",
    "TruthSource",
    "build_truth_engine",
]
