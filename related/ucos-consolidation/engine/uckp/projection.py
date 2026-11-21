"""UCKP Layer Zero — Universal Projections (Articles 4 and 11).

A projection is a *generated view* of the canonical universe: a Markdown register, a
JSON document, an API description, a graph export, a dataset, a user interface, a
repository tree. Article 4 gives all of them the same standing — none. Article 11 adds
that a generated output never owns truth.

The enforcement is structural rather than editorial. Every artifact is a
:class:`ProjectedArtifact`, and a projected artifact that claims authority cannot be
constructed: the constructor raises. So "the document is not the authority" is not a
convention a future author can quietly break; it is a value error.

Every artifact also records ``generated_from`` — the identities it was projected from —
and a ``payload_digest``. Together these make a projection *falsifiable*: regenerate it
and compare. A view that drifts from its objects is detectable by anyone with the
objects, which is what makes a repository disposable (Invariant 10).

The set of projection kinds is open (Article 17): :meth:`ProjectionEngine.register`
admits a kind nobody has thought of yet, and the named constants below are simply the
ones that exist today.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable

from engine.uckp.canonical import canonical_json, content_hash
from engine.uckp.errors import ProjectionAuthorityError
from engine.uckp.graph import UniversalKnowledgeGraph
from engine.uckp.ucko import UCKO

#: The projection kinds that exist today. Open by registration, never by amendment.
MARKDOWN = "markdown"
JSON = "json"
API = "api"
GRAPH = "graph"
DATASET = "dataset"
REPOSITORY = "repository"
USER_INTERFACE = "user-interface"
SOURCE = "source"
RUNTIME = "runtime"
DATABASE = "database"


@dataclass(frozen=True, slots=True)
class ProjectedArtifact:
    """A generated view. Never authoritative — the constructor refuses."""

    projection_id: str
    kind: str
    locator: str
    payload: str
    generated_from: tuple[str, ...] = field(default_factory=tuple)
    authoritative: bool = False

    def __post_init__(self) -> None:
        if self.authoritative:
            raise ProjectionAuthorityError(
                "a projected artifact may not hold authority",
                projection_id=self.projection_id,
                kind=self.kind,
            )
        if not self.generated_from:
            raise ProjectionAuthorityError(
                "a projection that names no source object is an independent authority",
                projection_id=self.projection_id,
                kind=self.kind,
            )

    @property
    def payload_digest(self) -> str:
        return content_hash(self.payload)

    def to_dict(self) -> dict[str, object]:
        return {
            "projection_id": self.projection_id,
            "kind": self.kind,
            "locator": self.locator,
            "payload_digest": self.payload_digest,
            "generated_from": list(self.generated_from),
            "authoritative": self.authoritative,
        }


@runtime_checkable
class Projection(Protocol):
    """The one contract every view of the universe satisfies."""

    kind: str

    def project(self, objects: Sequence[UCKO]) -> ProjectedArtifact:  # pragma: no cover
        ...


def _sources(objects: Sequence[UCKO]) -> tuple[str, ...]:
    return tuple(sorted(obj.ucko_id for obj in objects))


class JsonProjection:
    """The canonical universe as JSON. JSON is a view; JSON is not authority."""

    kind = JSON

    def __init__(self, locator: str = "projection/universe.json") -> None:
        self.locator = locator

    def project(self, objects: Sequence[UCKO]) -> ProjectedArtifact:
        payload = canonical_json(
            {
                "schema": "ucos-uckp-projection-json",
                "count": len(objects),
                "objects": [obj.to_dict() for obj in objects],
            }
        )
        return ProjectedArtifact(
            projection_id="UCKP-PROJ-JSON",
            kind=self.kind,
            locator=self.locator,
            payload=payload,
            generated_from=_sources(objects),
        )


class MarkdownProjection:
    """The canonical universe as a human-readable register."""

    kind = MARKDOWN

    def __init__(self, locator: str = "projection/UNIVERSE.md", title: str = "") -> None:
        self.locator = locator
        self.title = title or "Universal Constitutional Knowledge Universe"

    def project(self, objects: Sequence[UCKO]) -> ProjectedArtifact:
        lines = [
            f"# {self.title}",
            "",
            "GENERATED VIEW — this document holds no authority (UCKP Article 11).",
            "Every row is projected from a canonical object; edit the object, not this file.",
            "",
            "| Identity | Concept | Kind | Authority | Owner | Lifecycle | Seal |",
            "| --- | --- | --- | --- | --- | --- | --- |",
        ]
        for obj in objects:
            lines.append(
                f"| `{obj.ucko_id}` "
                f"| {obj.semantic_identity.concept} "
                f"| {obj.taxonomy.kind} "
                f"| {obj.authority.tier} "
                f"| {obj.ownership.owner} "
                f"| {obj.lifecycle} "
                f"| `{obj.content_sha256[:16]}` |"
            )
        lines.extend(("", f"Objects projected: {len(objects)}", ""))
        return ProjectedArtifact(
            projection_id="UCKP-PROJ-MARKDOWN",
            kind=self.kind,
            locator=self.locator,
            payload="\n".join(lines),
            generated_from=_sources(objects),
        )


class ApiProjection:
    """The canonical universe as a machine-consumable resource description."""

    kind = API

    def __init__(self, locator: str = "projection/universe-api.json") -> None:
        self.locator = locator

    def project(self, objects: Sequence[UCKO]) -> ProjectedArtifact:
        resources = [
            {
                "path": f"/ucko/{obj.identity.namespace}/{obj.local_name}",
                "identity": obj.ucko_id,
                "methods": ["GET"],
                "describes": obj.describe(),
            }
            for obj in objects
        ]
        payload = canonical_json(
            {
                "schema": "ucos-uckp-projection-api",
                "authority": "none — generated view of the canonical universe",
                "resources": resources,
            }
        )
        return ProjectedArtifact(
            projection_id="UCKP-PROJ-API",
            kind=self.kind,
            locator=self.locator,
            payload=payload,
            generated_from=_sources(objects),
        )


class GraphProjection:
    """The canonical universe as a node/edge export for any graph technology."""

    kind = GRAPH

    def __init__(self, locator: str = "projection/universe-graph.json") -> None:
        self.locator = locator

    def project(self, objects: Sequence[UCKO]) -> ProjectedArtifact:
        graph = UniversalKnowledgeGraph.from_objects(objects)
        payload = canonical_json(graph.to_document())
        return ProjectedArtifact(
            projection_id="UCKP-PROJ-GRAPH",
            kind=self.kind,
            locator=self.locator,
            payload=payload,
            generated_from=_sources(objects),
        )


class DatasetProjection:
    """The canonical universe as delimited rows, for analytical technologies."""

    kind = DATASET

    _COLUMNS = (
        "ucko_id",
        "uuid",
        "kind",
        "category",
        "authority_tier",
        "derives_from",
        "owner",
        "lifecycle",
        "semantic_digest",
        "content_sha256",
    )

    def __init__(self, locator: str = "projection/universe.tsv") -> None:
        self.locator = locator

    def project(self, objects: Sequence[UCKO]) -> ProjectedArtifact:
        rows = ["\t".join(self._COLUMNS)]
        for obj in objects:
            described = obj.describe()
            rows.append(
                "\t".join(
                    str(described.get(column, "")) if column in described else ""
                    for column in self._COLUMNS
                )
            )
        return ProjectedArtifact(
            projection_id="UCKP-PROJ-DATASET",
            kind=self.kind,
            locator=self.locator,
            payload="\n".join(rows),
            generated_from=_sources(objects),
        )


class RepositoryProjection:
    """The canonical universe as a repository tree.

    This is the projection that Article 4 exists to make explicit. A repository is
    where a copy of the universe happens to be laid out on some machine; it is not
    where the universe *is*. Rendering the tree as a generated manifest — paths
    derived from identity, never identity derived from paths — is what keeps the
    direction of that dependency visible and checkable.
    """

    kind = REPOSITORY

    def __init__(self, locator: str = "projection/repository-manifest.json") -> None:
        self.locator = locator

    @staticmethod
    def path_for(obj: UCKO) -> str:
        """The repository path derived from identity (never the reverse)."""
        return f"{obj.taxonomy.category}/{obj.identity.namespace}/{obj.local_name}.json"

    def project(self, objects: Sequence[UCKO]) -> ProjectedArtifact:
        entries = [
            {
                "path": self.path_for(obj),
                "identity": obj.ucko_id,
                "content_sha256": obj.content_sha256,
                "authoritative": False,
            }
            for obj in objects
        ]
        payload = canonical_json(
            {
                "schema": "ucos-uckp-projection-repository",
                "authority": "none — the repository is a persistence and projection binding",
                "derivation": "path is derived from identity; identity is never derived from path",
                "count": len(entries),
                "entries": sorted(entries, key=lambda entry: str(entry["path"])),
            }
        )
        return ProjectedArtifact(
            projection_id="UCKP-PROJ-REPOSITORY",
            kind=self.kind,
            locator=self.locator,
            payload=payload,
            generated_from=_sources(objects),
        )


class SourceProjection:
    """The canonical universe as generated source code.

    Source code is a view like any other (Article 4). Emitting the universe *as*
    source, with a header that refuses authority, closes the loophole where a
    hand-edited module quietly becomes the place a fact really lives.
    """

    kind = SOURCE

    def __init__(self, locator: str = "projection/universe_generated.py") -> None:
        self.locator = locator

    def project(self, objects: Sequence[UCKO]) -> ProjectedArtifact:
        lines = [
            '"""GENERATED SOURCE — holds no authority (UCKP Article 4, Article 11).',
            "",
            "Regenerated from the canonical universe. Edit the object, never this file.",
            '"""',
            "",
            "UNIVERSE: tuple[dict[str, str], ...] = (",
        ]
        for obj in objects:
            lines.append("    {")
            lines.append(f'        "identity": {obj.ucko_id!r},')
            lines.append(f'        "concept": {obj.semantic_identity.concept!r},')
            lines.append(f'        "kind": {obj.taxonomy.kind!r},')
            lines.append(f'        "authority_tier": {obj.authority.tier!r},')
            lines.append(f'        "derives_from": {obj.authority.derives_from!r},')
            lines.append(f'        "content_sha256": {obj.content_sha256!r},')
            lines.append("    },")
        lines.extend((")", ""))
        return ProjectedArtifact(
            projection_id="UCKP-PROJ-SOURCE",
            kind=self.kind,
            locator=self.locator,
            payload="\n".join(lines),
            generated_from=_sources(objects),
        )


class RuntimeProjection:
    """The canonical universe as a runtime binding manifest.

    Which execution environments may act on which objects — stated as a view, so
    that adding or retiring a runtime changes a projection and never the law
    (Article 10).
    """

    kind = RUNTIME

    def __init__(self, locator: str = "projection/universe-runtime.json") -> None:
        self.locator = locator

    def project(self, objects: Sequence[UCKO]) -> ProjectedArtifact:
        bindings = [
            {
                "identity": obj.ucko_id,
                "runtimes": sorted({binding.execution_kind for binding in obj.runtime_bindings}),
                "capabilities": sorted({binding.capability for binding in obj.runtime_bindings}),
                "owns_knowledge": False,
            }
            for obj in objects
        ]
        payload = canonical_json(
            {
                "schema": "ucos-uckp-projection-runtime",
                "authority": "none — execution never owns knowledge",
                "count": len(bindings),
                "bindings": sorted(bindings, key=lambda entry: str(entry["identity"])),
            }
        )
        return ProjectedArtifact(
            projection_id="UCKP-PROJ-RUNTIME",
            kind=self.kind,
            locator=self.locator,
            payload=payload,
            generated_from=_sources(objects),
        )


class DatabaseProjection:
    """The canonical universe as relational DDL and rows.

    A schema is a view (Article 11). Generating the schema from the objects, rather
    than modelling the objects to fit a schema, is the whole difference between a
    database that stores the universe and one that defines it.
    """

    kind = DATABASE

    _COLUMNS = (
        ("ucko_id", "TEXT PRIMARY KEY"),
        ("uuid", "TEXT NOT NULL"),
        ("concept", "TEXT NOT NULL"),
        ("kind", "TEXT NOT NULL"),
        ("category", "TEXT NOT NULL"),
        ("authority_tier", "TEXT NOT NULL"),
        ("derives_from", "TEXT NOT NULL"),
        ("owner", "TEXT NOT NULL"),
        ("lifecycle", "TEXT NOT NULL"),
        ("content_sha256", "TEXT NOT NULL"),
    )

    def __init__(self, locator: str = "projection/universe.sql") -> None:
        self.locator = locator

    @staticmethod
    def _quote(value: object) -> str:
        return "'" + str(value).replace("'", "''") + "'"

    def project(self, objects: Sequence[UCKO]) -> ProjectedArtifact:
        columns = ",\n".join(f"  {name} {ddl}" for name, ddl in self._COLUMNS)
        names = ", ".join(name for name, _ in self._COLUMNS)
        lines = [
            "-- GENERATED SCHEMA — holds no authority (UCKP Article 11).",
            "-- Regenerated from the canonical universe; the database stores, it does not define.",
            "DROP TABLE IF EXISTS ucko;",
            f"CREATE TABLE ucko (\n{columns}\n);",
        ]
        for obj in objects:
            described = obj.describe()
            values = ", ".join(self._quote(described.get(name, "")) for name, _ in self._COLUMNS)
            # S608: this is a generated *artifact*, never an executed query. The column
            # names come from the closed _COLUMNS tuple and every value goes through
            # _quote, so the payload is inert text that some other technology may later
            # choose to run. A projection that executed its own output would be acting
            # on knowledge, which Article 4 forbids.
            lines.append(f"INSERT INTO ucko ({names}) VALUES ({values});")  # noqa: S608
        lines.append("")
        return ProjectedArtifact(
            projection_id="UCKP-PROJ-DATABASE",
            kind=self.kind,
            locator=self.locator,
            payload="\n".join(lines),
            generated_from=_sources(objects),
        )


class UserInterfaceProjection:
    """The canonical universe as a navigable view model.

    An interface presents the universe; it never holds any part of it. The view
    model is grouped by category and ordered deterministically, so two renders of
    one universe are the same interface (Article 13).
    """

    kind = USER_INTERFACE

    def __init__(self, locator: str = "projection/universe-ui.json") -> None:
        self.locator = locator

    def project(self, objects: Sequence[UCKO]) -> ProjectedArtifact:
        grouped: dict[str, list[dict[str, object]]] = {}
        for obj in objects:
            grouped.setdefault(obj.taxonomy.category, []).append(
                {
                    "identity": obj.ucko_id,
                    "label": obj.semantic_identity.concept,
                    "detail": obj.semantic_identity.definition,
                    "badges": [obj.authority.tier, obj.lifecycle, obj.taxonomy.kind],
                    "unattested": [facet.value for facet in obj.unattested_facets()],
                }
            )
        panels = [
            {
                "panel_id": f"panel:{category}",
                "title": category,
                "count": len(items),
                "items": sorted(items, key=lambda item: str(item["identity"])),
            }
            for category, items in sorted(grouped.items())
        ]
        payload = canonical_json(
            {
                "schema": "ucos-uckp-projection-ui",
                "authority": "none — an interface presents the universe, it never holds it",
                "counts": {"panels": len(panels), "objects": len(objects)},
                "panels": panels,
            }
        )
        return ProjectedArtifact(
            projection_id="UCKP-PROJ-UI",
            kind=self.kind,
            locator=self.locator,
            payload=payload,
            generated_from=_sources(objects),
        )


class ProjectionEngine:
    """The registry of every view of the canonical universe."""

    __slots__ = ("_projections",)

    def __init__(self, projections: Iterable[Projection] = ()) -> None:
        self._projections: dict[str, Projection] = {}
        for projection in projections:
            self.register(projection)

    def register(self, projection: Projection) -> Projection:
        """Admit a projection, including of a kind that did not exist before."""
        kind = str(projection.kind)
        if kind in self._projections:
            raise ProjectionAuthorityError("projection kind already registered", kind=kind)
        self._projections[kind] = projection
        return projection

    def kinds(self) -> tuple[str, ...]:
        return tuple(sorted(self._projections))

    def project(self, kind: str, objects: Sequence[UCKO]) -> ProjectedArtifact:
        projection = self._projections.get(str(kind))
        if projection is None:
            raise ProjectionAuthorityError("no such projection kind", kind=str(kind))
        return projection.project(objects)

    def project_all(self, objects: Sequence[UCKO]) -> tuple[ProjectedArtifact, ...]:
        return tuple(self.project(kind, objects) for kind in self.kinds())

    def regenerates_identically(self, kind: str, objects: Sequence[UCKO]) -> bool:
        """True iff projecting twice yields the same bytes (Article 13)."""
        first = self.project(kind, objects)
        second = self.project(kind, objects)
        return first.payload_digest == second.payload_digest

    def replays_identically(self, objects: Sequence[UCKO]) -> bool:
        """True iff *every* registered projection regenerates byte-identically."""
        return all(self.regenerates_identically(kind, objects) for kind in self.kinds())

    def describe(self) -> dict[str, object]:
        """The machine-readable self-description of the projection layer (Article 8)."""
        return {
            "kinds": list(self.kinds()),
            "projections": [
                {
                    "kind": kind,
                    "locator": getattr(self._projections[kind], "locator", ""),
                    "implementation": type(self._projections[kind]).__name__,
                }
                for kind in self.kinds()
            ],
        }

    def unimplemented(self, declared: Iterable[str]) -> tuple[str, ...]:
        """Declared kinds this engine cannot actually produce.

        A projection kind that is named but not built is the failure mode where a
        declaration is mistaken for a capability: callers see the constant, assume a
        view exists, and the absence never surfaces. Naming the gap is what lets it
        fail closed.
        """
        available = set(self.kinds())
        return tuple(sorted({str(kind) for kind in declared} - available))

    def require_covers(self, declared: Iterable[str]) -> None:
        """Fail closed if any declared projection kind has no implementation."""
        missing = self.unimplemented(declared)
        if missing:
            raise ProjectionAuthorityError(
                "declared projection kinds have no implementation",
                missing=list(missing),
            )

    def to_document(self, objects: Sequence[UCKO]) -> dict[str, object]:
        artifacts = self.project_all(objects)
        return {
            "schema": "ucos-uckp-projections",
            "version": "1.0.0",
            "counts": {"kinds": len(artifacts), "objects": len(objects)},
            "artifacts": [artifact.to_dict() for artifact in artifacts],
        }


def build_projection_engine() -> ProjectionEngine:
    """Return an engine carrying every projection Layer Zero ships."""
    return ProjectionEngine(
        (
            JsonProjection(),
            MarkdownProjection(),
            ApiProjection(),
            GraphProjection(),
            DatasetProjection(),
            RepositoryProjection(),
            SourceProjection(),
            RuntimeProjection(),
            DatabaseProjection(),
            UserInterfaceProjection(),
        )
    )


#: The projection kinds that exist today — *derived* from the shipped engine rather
#: than restated beside it. A hand-maintained second list is a second authority over
#: the same fact (Article 3), and it is exactly how ``repository`` and
#: ``user-interface`` came to be declared while nothing could produce them.
KNOWN_PROJECTION_KINDS: tuple[str, ...] = build_projection_engine().kinds()


def assert_no_projection_authority(
    artifacts: Iterable[ProjectedArtifact],
) -> tuple[str, ...]:
    """Return the identifiers of any artifact claiming authority. Always empty."""
    return tuple(artifact.projection_id for artifact in artifacts if artifact.authoritative)


__all__ = [
    "API",
    "DATABASE",
    "DATASET",
    "GRAPH",
    "JSON",
    "KNOWN_PROJECTION_KINDS",
    "MARKDOWN",
    "REPOSITORY",
    "RUNTIME",
    "SOURCE",
    "USER_INTERFACE",
    "ApiProjection",
    "DatabaseProjection",
    "DatasetProjection",
    "GraphProjection",
    "JsonProjection",
    "MarkdownProjection",
    "ProjectedArtifact",
    "Projection",
    "ProjectionEngine",
    "RepositoryProjection",
    "RuntimeProjection",
    "SourceProjection",
    "UserInterfaceProjection",
    "assert_no_projection_authority",
    "build_projection_engine",
]
