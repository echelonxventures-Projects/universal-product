"""UCOS-CTRL-000001 — the declared Control Plane manifest.

The control plane names no repository. Every repository-specific fact it needs —
which registry documents hold Truth, which artifact categories constitute a
governance record, which governance rules apply, which linkage dimensions must
close — arrives as a *declared document*, exactly as
:mod:`platform.universal_truth` receives its zones. This module is the reader for
that document and the only place the packaged catalogue is resolved.

The manifest is data. Replacing ``catalog/ucos-control-plane.json`` specialises
the same control plane for a different repository without touching a line of code.
"""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from platform.universal_control_plane.errors import ManifestError
from typing import Any

#: The packaged catalogue directory holding declared control-plane specialisations.
CATALOG_DIRNAME = "catalog"

#: The declared specialisation shipped for the containing repository (data, not code).
DEFAULT_MANIFEST_FILENAME = "ucos-control-plane.json"


def _require_mapping(value: Any, *, at: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ManifestError(f"{at} must be an object")
    return value


def _str_tuple(value: Any, *, at: str) -> tuple[str, ...]:
    if value is None:
        return ()
    if not isinstance(value, Sequence) or isinstance(value, str | bytes):
        raise ManifestError(f"{at} must be an array of strings")
    out: list[str] = []
    for item in value:
        if not isinstance(item, str):
            raise ManifestError(f"{at} must contain only strings")
        cleaned = item.strip()
        if cleaned:
            out.append(cleaned)
    return tuple(out)


@dataclass(frozen=True, slots=True)
class DocumentRef:
    """A declared registry document: a filename plus the key its records live under."""

    name: str
    filename: str
    root_key: str | None = None

    @classmethod
    def from_dict(cls, name: str, raw: Any) -> DocumentRef:
        body = _require_mapping(raw, at=f"truth_sources.registry.documents.{name}")
        filename = str(body.get("filename", "")).strip()
        if not filename:
            raise ManifestError(f"registry document {name!r} declares no filename")
        root = body.get("root_key")
        return cls(name=name, filename=filename, root_key=str(root) if root else None)

    def to_dict(self) -> dict[str, Any]:
        return {"name": self.name, "filename": self.filename, "root_key": self.root_key}


@dataclass(frozen=True, slots=True)
class ArtifactClass:
    """A declared class of registered artifact, selected by category or programme."""

    class_id: str
    categories: tuple[str, ...] = ()
    programs: tuple[str, ...] = ()
    description: str = ""

    @classmethod
    def from_dict(cls, raw: Any) -> ArtifactClass:
        body = _require_mapping(raw, at="artifact_classes[]")
        class_id = str(body.get("class_id", "")).strip()
        if not class_id:
            raise ManifestError("artifact class declares no class_id")
        return cls(
            class_id=class_id,
            categories=_str_tuple(body.get("categories"), at=f"{class_id}.categories"),
            programs=_str_tuple(body.get("programs"), at=f"{class_id}.programs"),
            description=str(body.get("description", "")),
        )

    def admits(self, *, category: str, program: str) -> bool:
        """Whether an artifact of ``category``/``program`` belongs to this class."""
        return category in self.categories or (bool(program) and program in self.programs)

    def to_dict(self) -> dict[str, Any]:
        return {
            "class_id": self.class_id,
            "categories": list(self.categories),
            "programs": list(self.programs),
            "description": self.description,
        }


@dataclass(frozen=True, slots=True)
class Rule:
    """A declared governance rule or certification criterion.

    Both vocabularies share one shape — an identifier, a severity, and the name of
    the fact the subject must carry — because both ask the same question of a
    subject and differ only in what a failure means.
    """

    rule_id: str
    severity: str
    requires: str
    message: str = ""

    @classmethod
    def from_dict(cls, raw: Any, *, at: str) -> Rule:
        body = _require_mapping(raw, at=at)
        rule_id = str(body.get("rule_id") or body.get("criterion_id") or "").strip()
        if not rule_id:
            raise ManifestError(f"{at} declares no rule_id/criterion_id")
        requires = str(body.get("requires", "")).strip()
        if not requires:
            raise ManifestError(f"{at} declares no 'requires' fact")
        return cls(
            rule_id=rule_id,
            severity=str(body.get("severity", "MEDIUM")).strip() or "MEDIUM",
            requires=requires,
            message=str(body.get("message", "")),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "severity": self.severity,
            "requires": self.requires,
            "message": self.message,
        }


@dataclass(frozen=True, slots=True)
class EngineTaxonomy:
    """How a discovered control-plane class is classified — by suffix, then module."""

    class_suffixes: tuple[str, ...]
    module_layers: Mapping[str, str] = field(default_factory=dict)
    layer_dependencies: Mapping[str, tuple[str, ...]] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, raw: Any) -> EngineTaxonomy:
        body = _require_mapping(raw, at="engine_taxonomy")
        suffixes = _str_tuple(body.get("class_suffixes"), at="engine_taxonomy.class_suffixes")
        if not suffixes:
            raise ManifestError("engine_taxonomy declares no class_suffixes")
        layers = _require_mapping(body.get("module_layers", {}), at="engine_taxonomy.module_layers")
        deps_raw = _require_mapping(
            body.get("layer_dependencies", {}), at="engine_taxonomy.layer_dependencies"
        )
        return cls(
            class_suffixes=suffixes,
            module_layers={str(k): str(v) for k, v in layers.items()},
            layer_dependencies={
                str(k): _str_tuple(v, at=f"layer_dependencies.{k}") for k, v in deps_raw.items()
            },
        )

    def is_engine_class(self, name: str) -> bool:
        """Whether a class *name* names a control-plane engine."""
        return any(name.endswith(suffix) for suffix in self.class_suffixes)

    def layer_for(self, module: str) -> str:
        """The declared layer for the terminal segment of *module*; UNCLASSIFIED when absent."""
        return self.module_layers.get(module.rsplit(".", 1)[-1], "UNCLASSIFIED")

    def dependencies_of(self, layer: str) -> tuple[str, ...]:
        return self.layer_dependencies.get(layer, ())

    def to_dict(self) -> dict[str, Any]:
        return {
            "class_suffixes": list(self.class_suffixes),
            "module_layers": dict(sorted(self.module_layers.items())),
            "layer_dependencies": {k: list(v) for k, v in sorted(self.layer_dependencies.items())},
        }


@dataclass(frozen=True, slots=True)
class ControlPlaneManifest:
    """The declared control-plane specialisation for one repository."""

    manifest_id: str
    version: str
    universe_id: str
    universe_name: str
    universe_description: str
    vision_statement: str
    registry_documents: Mapping[str, DocumentRef]
    capability_catalog_locator: str
    capability_catalog_root_key: str
    artifact_classes: tuple[ArtifactClass, ...]
    engine_taxonomy: EngineTaxonomy
    governance_rules: tuple[Rule, ...]
    certification_criteria: tuple[Rule, ...]
    linkage_dimensions: tuple[str, ...]
    journal_dirname: str
    journal_filename: str

    # -- construction ----------------------------------------------------

    @classmethod
    def from_document(cls, document: Mapping[str, Any]) -> ControlPlaneManifest:
        """Build a manifest from a declared document (fail-closed on every absence)."""
        body = _require_mapping(document, at="manifest")
        universe = _require_mapping(body.get("universe", {}), at="universe")
        universe_id = str(universe.get("universe_id", "")).strip()
        if not universe_id:
            raise ManifestError("manifest declares no universe_id")

        sources = _require_mapping(body.get("truth_sources", {}), at="truth_sources")
        registry = _require_mapping(sources.get("registry", {}), at="truth_sources.registry")
        documents_raw = _require_mapping(
            registry.get("documents", {}), at="truth_sources.registry.documents"
        )
        documents = {
            str(name): DocumentRef.from_dict(str(name), raw) for name, raw in documents_raw.items()
        }
        if not documents:
            raise ManifestError("manifest declares no registry documents")

        catalog = _require_mapping(
            sources.get("capability_catalog", {}), at="truth_sources.capability_catalog"
        )
        catalog_locator = str(catalog.get("locator", "")).strip()
        if not catalog_locator:
            raise ManifestError("manifest declares no capability catalogue locator")

        classes = tuple(
            ArtifactClass.from_dict(raw) for raw in body.get("artifact_classes", []) or ()
        )
        if not classes:
            raise ManifestError("manifest declares no artifact classes")

        linkage = _str_tuple(body.get("linkage_dimensions"), at="linkage_dimensions")
        if not linkage:
            raise ManifestError("manifest declares no linkage dimensions")

        replay = _require_mapping(body.get("replay", {}), at="replay")
        journal_dirname = str(replay.get("journal_dirname", "")).strip()
        journal_filename = str(replay.get("journal_filename", "")).strip()
        if not journal_dirname or not journal_filename:
            raise ManifestError("manifest declares an incomplete replay journal location")

        governance = tuple(
            Rule.from_dict(raw, at="governance_rules[]")
            for raw in body.get("governance_rules", []) or ()
        )
        if not governance:
            raise ManifestError("manifest declares no governance rules")
        criteria = tuple(
            Rule.from_dict(raw, at="certification_criteria[]")
            for raw in body.get("certification_criteria", []) or ()
        )
        if not criteria:
            raise ManifestError("manifest declares no certification criteria")

        return cls(
            manifest_id=str(body.get("manifest_id", "")).strip() or "control-plane.manifest",
            version=str(body.get("version", "0.0.0")),
            universe_id=universe_id,
            universe_name=str(universe.get("name", universe_id)),
            universe_description=str(universe.get("description", "")),
            vision_statement=str(universe.get("vision", "")),
            registry_documents=documents,
            capability_catalog_locator=catalog_locator,
            capability_catalog_root_key=str(catalog.get("root_key", "capabilities")),
            artifact_classes=classes,
            engine_taxonomy=EngineTaxonomy.from_dict(body.get("engine_taxonomy", {})),
            governance_rules=governance,
            certification_criteria=criteria,
            linkage_dimensions=linkage,
            journal_dirname=journal_dirname,
            journal_filename=journal_filename,
        )

    # -- queries ---------------------------------------------------------

    def document(self, name: str) -> DocumentRef:
        """The declared registry document *name*; raises when undeclared."""
        try:
            return self.registry_documents[name]
        except KeyError as exc:
            raise ManifestError(f"undeclared registry document: {name!r}") from exc

    def artifact_class(self, class_id: str) -> ArtifactClass:
        for cls_ in self.artifact_classes:
            if cls_.class_id == class_id:
                return cls_
        raise ManifestError(f"undeclared artifact class: {class_id!r}")

    def classify_artifact(self, *, category: str, program: str = "") -> tuple[str, ...]:
        """Every declared class that admits an artifact of ``category``/``program``."""
        return tuple(
            cls_.class_id
            for cls_ in self.artifact_classes
            if cls_.admits(category=category, program=program)
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "manifest_id": self.manifest_id,
            "version": self.version,
            "universe_id": self.universe_id,
            "universe_name": self.universe_name,
            "registry_documents": {
                name: ref.to_dict() for name, ref in sorted(self.registry_documents.items())
            },
            "capability_catalog": {
                "locator": self.capability_catalog_locator,
                "root_key": self.capability_catalog_root_key,
            },
            "artifact_classes": [c.to_dict() for c in self.artifact_classes],
            "engine_taxonomy": self.engine_taxonomy.to_dict(),
            "governance_rules": [r.to_dict() for r in self.governance_rules],
            "certification_criteria": [r.to_dict() for r in self.certification_criteria],
            "linkage_dimensions": list(self.linkage_dimensions),
            "replay": {
                "journal_dirname": self.journal_dirname,
                "journal_filename": self.journal_filename,
            },
        }


def catalog_path(filename: str = DEFAULT_MANIFEST_FILENAME) -> Path:
    """The packaged catalogue path for *filename* (no repository path is assumed)."""
    return Path(__file__).resolve().parent / CATALOG_DIRNAME / filename


def load_manifest(path: Path | str) -> ControlPlaneManifest:
    """Load a declared control-plane manifest from *path* (fail-closed)."""
    target = Path(path)
    try:
        raw = target.read_text("utf-8")
    except OSError as exc:
        raise ManifestError(f"control-plane manifest could not be read: {target} ({exc})") from exc
    try:
        document = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ManifestError(f"control-plane manifest is not valid JSON: {target} ({exc})") from exc
    return ControlPlaneManifest.from_document(document)


def default_manifest(filename: str = DEFAULT_MANIFEST_FILENAME) -> ControlPlaneManifest:
    """The declared manifest shipped in the packaged catalogue."""
    return load_manifest(catalog_path(filename))


__all__ = [
    "CATALOG_DIRNAME",
    "DEFAULT_MANIFEST_FILENAME",
    "ArtifactClass",
    "ControlPlaneManifest",
    "DocumentRef",
    "EngineTaxonomy",
    "Rule",
    "catalog_path",
    "default_manifest",
    "load_manifest",
]
