"""UCKP — assimilation of every existing UCOS artifact into canonical objects (Article 19).

Article 19 permits assimilation only on terms: no loss of information, authority,
replay, certification, identity or provenance, and the mapping must be *invertible*.
Invertibility is the demanding half. A mapping that merely copies the fields someone
thought were important is a summary, and a summary silently decides what the future is
allowed to remember.

So each object carries the complete original record, verbatim, in its metadata under
:data:`NATIVE_RECORD_KEY`, encoded through the one canonical form.
:func:`reconstruct_artifact` returns it. :func:`verify_invertible` re-derives every
source record from its object and compares canonical digests, so "lossless" is a
measurement over all 1201 artifacts rather than a design intention.

The salient fields are *also* mapped onto real facets — authority from ``parent``,
dependencies from ``dependencies``, traceability from ``traceability``, evidence from
``content_hash`` and ``path`` — because an object that stored only a blob would be
lossless and useless. The blob guarantees nothing is forgotten; the facets make the
artifact a participating citizen of the graph.

Three things this module refuses to do quietly, because each would be a way of faking
success:

**It does not invent meaning.** All 1201 source artifacts carry an empty
``description``, and 21 names are shared by 490 artifacts (47 files are each called
"Acceptance Decision"). Semantic identity must still be unique or the registry will
refuse the second claimant — correctly, under Article 3. Rather than mangle names or
suppress the collision, :func:`semantic_definition` states what actually distinguishes
them: the native id, the category, the volume and the path. That is a true sentence, and
the collision is reported in the assimilation report rather than absorbed.

**It does not manufacture relationships.** 58 of the 5543 traceability links in the
source registry point at ids the registry does not contain. Those links are preserved
in the native record — nothing is lost — but they are not turned into graph edges,
because an edge to a non-existent object is precisely the dangling relationship
UCKP-INV-04 forbids. They are counted and reported.

**It does not amend the law to fit the data.** The repository's six artifact statuses
(``ACTIVE``, ``COMPLETE``, ``FROZEN``, ``UNDER_REVIEW``, ``FINAL``, ``CERTIFIED``) are
not lifecycle stages the root law declares, and its 70 native categories are not UCKP
governed categories. Both are admitted by *registration* into open vocabularies
(Article 17), which is the mechanism the law provides for exactly this situation. No
line of :mod:`engine.uckp.law` changes because the repository turned out to contain
something it had not enumerated.
"""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path

from engine.uckp.canonical import canonical_json, content_hash
from engine.uckp.constitution import (
    UNIVERSAL_RUNTIMES,
    root_law_urn,
)
from engine.uckp.errors import AssimilationError
from engine.uckp.identity import urn_for
from engine.uckp.ucko import UCKO
from engine.uckp.universe import ConstitutionalUniverse, build_universe
from engine.uckp.values import (
    AuditEntry,
    EvidenceRef,
    PersistenceBinding,
    ProjectionBinding,
    ProvenanceStep,
    Relationship,
    TraceLink,
)
from engine.uckp.vocabulary import (
    ARCHITECTURE_LAYER,
    AUTHORITY_TIER,
    CIVILIZATION_STRATUM,
    DISCOVERY_DIMENSION,
    GOVERNED_CATEGORY,
    KNOWLEDGE_KIND,
    LIFECYCLE_STAGE,
    PROJECTION_KIND,
    RELATION_TYPE,
    UKIP_FACET,
    Term,
    Vocabulary,
    VocabularyRegistry,
    build_vocabulary_registry,
)

#: The canonical inventory of existing UCOS artifacts, relative to the repository root.
#: The repository is where this record currently *lives*; it is not what makes it true
#: (Article 4). Assimilation reads it as a persistence binding and mints authority.
ARTIFACT_REGISTRY_PATH = "00-BOOK/DATA/artifacts.json"

#: Assimilated artifacts are minted in their own namespace, so a native identifier can
#: never collide with a constitutional one and the two populations stay distinguishable
#: for the whole life of the universe.
ASSIMILATION_NAMESPACE = "ucos.ukb"

#: The metadata key holding the complete original record. This is the invertibility seam.
NATIVE_RECORD_KEY = "native_record"

#: The UCKP governed category every assimilated artifact takes. The *native* category is
#: preserved in the taxonomy path, the tags, the metadata and the native record.
ASSIMILATED_CATEGORY = "artifact"

#: The UCKP knowledge kind. An assimilated artifact is a reference to something that
#: exists; it is not itself a law, principle or rule.
ASSIMILATED_KIND = "reference"

#: Assimilated artifacts hold engineering authority, never constitutional authority.
#: Assimilation moves an artifact under the law; it does not promote it.
ASSIMILATED_TIER = "engineering"

#: The new vocabulary admitting the repository's own artifact categories (Article 17).
NATIVE_CATEGORY_VOCABULARY = "ucos.artifact-category"

#: The new vocabulary admitting the repository's own programmes.
NATIVE_PROGRAM_VOCABULARY = "ucos.artifact-program"

#: The traceability stages the source registry records per artifact.
TRACEABILITY_STAGES: tuple[str, ...] = (
    "requirement",
    "architecture",
    "design",
    "implementation",
    "source_code",
    "unit_test",
    "integration_test",
    "functional_test",
    "security_test",
    "certification",
    "deployment",
    "production",
    "operations",
)


@dataclass(frozen=True, slots=True)
class AssimilationReport:
    """What assimilation did, and what it declined to do silently."""

    source: str
    source_digest: str
    artifacts_read: int
    objects_minted: int
    registered_lifecycle_terms: tuple[str, ...] = field(default_factory=tuple)
    registered_categories: tuple[str, ...] = field(default_factory=tuple)
    registered_programs: tuple[str, ...] = field(default_factory=tuple)
    shared_semantic_names: tuple[str, ...] = field(default_factory=tuple)
    unresolvable_traceability: tuple[str, ...] = field(default_factory=tuple)
    unresolvable_dependencies: tuple[str, ...] = field(default_factory=tuple)
    invertible: bool = False
    losses: tuple[str, ...] = field(default_factory=tuple)

    @property
    def lossless(self) -> bool:
        return self.invertible and not self.losses

    def to_dict(self) -> dict[str, object]:
        return {
            "schema": "ucos-uckp-assimilation",
            "version": "1.0.0",
            "source": self.source,
            "source_digest": self.source_digest,
            "counts": {
                "artifacts_read": self.artifacts_read,
                "objects_minted": self.objects_minted,
                "registered_lifecycle_terms": len(self.registered_lifecycle_terms),
                "registered_categories": len(self.registered_categories),
                "registered_programs": len(self.registered_programs),
                "shared_semantic_names": len(self.shared_semantic_names),
                "unresolvable_traceability": len(self.unresolvable_traceability),
                "unresolvable_dependencies": len(self.unresolvable_dependencies),
            },
            "registered_lifecycle_terms": list(self.registered_lifecycle_terms),
            "registered_categories": list(self.registered_categories),
            "registered_programs": list(self.registered_programs),
            "shared_semantic_names": list(self.shared_semantic_names),
            "unresolvable_traceability": list(self.unresolvable_traceability),
            "unresolvable_dependencies": list(self.unresolvable_dependencies),
            "invertible": self.invertible,
            "lossless": self.lossless,
            "losses": list(self.losses),
        }

    def summary(self) -> str:
        return (
            f"assimilated {self.objects_minted}/{self.artifacts_read} artifacts from "
            f"{self.source} ({self.source_digest[:16]}); "
            f"invertible={self.invertible} lossless={self.lossless}; "
            f"registered {len(self.registered_lifecycle_terms)} lifecycle terms, "
            f"{len(self.registered_categories)} native categories, "
            f"{len(self.registered_programs)} native programmes; "
            f"{len(self.unresolvable_traceability)} traceability links left un-edged"
        )


# --- source ---------------------------------------------------------------------


def load_artifact_registry(
    source_root: str | Path | None = None,
) -> tuple[str, tuple[Mapping[str, object], ...]]:
    """Read the artifact registry, returning its digest and its records.

    The digest is over the file's parsed content, so the assimilation report can name
    exactly which state of the registry it assimilated. An assimilation that cannot
    identify its input cannot be replayed.
    """
    root = Path(source_root) if source_root is not None else Path(__file__).resolve().parents[2]
    path = root / ARTIFACT_REGISTRY_PATH
    if not path.is_file():
        raise AssimilationError(
            "the artifact registry does not exist, so nothing may be assimilated",
            path=str(path),
        )
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise AssimilationError(
            "the artifact registry could not be read", path=str(path), reason=str(exc)
        ) from exc
    records = payload.get("artifacts") if isinstance(payload, Mapping) else None
    if not isinstance(records, list):
        raise AssimilationError("the artifact registry declares no artifact list")
    return content_hash(payload), tuple(record for record in records if isinstance(record, Mapping))


# --- open-world registration (Article 17) ---------------------------------------


def native_lifecycle(status: object) -> str:
    """Map a native status onto a lifecycle term id (lowercase, hyphenated).

    A missing status becomes ``draft`` — the stage that claims least. Note that
    ``str(None)`` is ``"none"``, so the absent case has to be tested before
    stringifying, or the universe acquires a lifecycle stage literally called "none".
    """
    if status is None:
        return "draft"
    return str(status).strip().lower().replace("_", "-") or "draft"


def native_term(value: object) -> str:
    """Map a native category or programme onto a vocabulary term id."""
    if value is None:
        return "unclassified"
    return str(value).strip().lower().replace("_", "-") or "unclassified"


def _register_or_reuse(vocabularies: VocabularyRegistry, vocabulary: Vocabulary) -> tuple[str, ...]:
    """Register a native vocabulary, or reuse an identical one already registered.

    Assimilating twice against one registry is an ordinary thing to do — a caller may
    assimilate, inspect, and assimilate again — and it should not raise. But silently
    accepting a *different* vocabulary under an existing id would let two sets of terms
    compete for one name, so a genuine conflict still fails closed.
    """
    existing = vocabularies.get(vocabulary.vocabulary_id)
    if existing is None:
        vocabularies.register(vocabulary)
        return vocabulary.term_ids()
    if existing.digest() != vocabulary.digest():
        raise AssimilationError(
            "a different vocabulary is already registered under this id",
            vocabulary_id=vocabulary.vocabulary_id,
        )
    return existing.term_ids()


def register_native_vocabularies(
    vocabularies: VocabularyRegistry, records: Sequence[Mapping[str, object]]
) -> tuple[tuple[str, ...], tuple[str, ...], tuple[str, ...]]:
    """Admit every native status, category and programme by registration.

    This is Article 17 doing the work it exists for. The repository contains statuses
    and categories the root law never enumerated, and the lawful response is to
    register them — not to edit the law, and not to coerce the data into the nearest
    term the law happens to have. Coercion would be a silent loss of meaning, which
    Article 19 forbids just as firmly as a dropped field.
    """
    lifecycle = vocabularies.require(LIFECYCLE_STAGE)
    added_stages: list[str] = []
    for status in sorted({native_lifecycle(record.get("status")) for record in records}):
        if not lifecycle.has(status):
            vocabularies.extend(
                LIFECYCLE_STAGE,
                Term(
                    term_id=status,
                    definition=(
                        f"the native UCOS artifact status {status!r}, admitted by "
                        "registration under Article 17"
                    ),
                ),
            )
            lifecycle = vocabularies.require(LIFECYCLE_STAGE)
            added_stages.append(status)

    categories = sorted({native_term(record.get("category")) for record in records})
    registered_categories = _register_or_reuse(
        vocabularies,
        Vocabulary(
            vocabulary_id=NATIVE_CATEGORY_VOCABULARY,
            purpose="the repository's own artifact categories, preserved without coercion",
            terms=tuple(
                Term(term_id=name, definition=f"native UCOS artifact category {name!r}")
                for name in categories
            ),
        ),
    )
    programs = sorted({native_term(record.get("program")) for record in records})
    registered_programs = _register_or_reuse(
        vocabularies,
        Vocabulary(
            vocabulary_id=NATIVE_PROGRAM_VOCABULARY,
            purpose="the repository's own programmes, preserved without coercion",
            terms=tuple(
                Term(term_id=name, definition=f"native UCOS programme {name!r}")
                for name in programs
            ),
        ),
    )
    return tuple(added_stages), registered_categories, registered_programs


# --- mapping --------------------------------------------------------------------


def artifact_urn(universal_id: object) -> str:
    """The canonical URN an assimilated artifact takes (pure)."""
    return urn_for(ASSIMILATION_NAMESPACE, str(universal_id).strip())


def semantic_definition(record: Mapping[str, object]) -> str:
    """A true, unique statement of what this artifact means.

    Every source description is empty and 21 names are shared, so a name alone cannot
    be a semantic identity. What actually distinguishes these artifacts is their native
    identifier and the place they occupy, and the path is unique across all 1201 — so
    this sentence is both honest and injective. Fabricating a description, or appending
    a counter to a name, would make the collision disappear without making the meanings
    distinct.
    """
    declared = str(record.get("description", "")).strip()
    identity = str(record.get("universal_id", "")).strip()
    native = str(record.get("native_id", "")).strip()
    category = str(record.get("category", "")).strip()
    volume = str(record.get("volume", "")).strip()
    path = str(record.get("path", "")).strip()
    stated = f"{declared} " if declared else ""
    return (
        f"{stated}UCOS artifact {identity} (native {native}) of category {category} "
        f"in volume {volume}, homed at {path}"
    )


def assimilate_artifact(
    record: Mapping[str, object],
    *,
    known_ids: frozenset[str],
    law_urn: str,
    source: str,
    source_digest: str,
) -> UCKO:
    """Map one native artifact record onto exactly one canonical object.

    ``parent`` becomes the single authority. The one artifact with no parent derives
    from the root law, which is what gives the whole assimilated population a chain
    that terminates at the constitution instead of floating beside it.
    """
    identity = str(record.get("universal_id", "")).strip()
    if not identity:
        raise AssimilationError("an artifact record carries no universal_id")
    self_urn = artifact_urn(identity)
    native_record = canonical_json(record)

    parent = record.get("parent")
    parent_id = str(parent).strip() if parent else ""
    if parent_id and parent_id in known_ids:
        parent_urn = artifact_urn(parent_id)
    else:
        parent_urn = law_urn

    relationships = [Relationship("derived-from", parent_urn, "authority")]
    dependencies: list[str] = []
    for dependency in record.get("dependencies") or ():
        dependency_id = str(dependency).strip()
        if dependency_id and dependency_id in known_ids:
            dependencies.append(artifact_urn(dependency_id))

    traceability: list[TraceLink] = []
    declared_traceability = record.get("traceability")
    if isinstance(declared_traceability, Mapping):
        for stage in TRACEABILITY_STAGES:
            for target in declared_traceability.get(stage) or ():
                target_id = str(target).strip()
                if target_id and target_id in known_ids:
                    traceability.append(
                        TraceLink(
                            upstream=artifact_urn(target_id),
                            downstream=self_urn,
                            kind=stage,
                        )
                    )

    path = str(record.get("path", "")).strip()
    owner = str(record.get("owner", "")).strip() or "UCOS-PROGRAM-CUSTODIAN"
    declared_hash = str(record.get("content_hash", "")).strip()
    native_category = native_term(record.get("category"))
    native_program = native_term(record.get("program"))

    return UCKO.mint(
        namespace=ASSIMILATION_NAMESPACE,
        local_name=identity,
        concept=str(record.get("name", "")).strip() or identity,
        definition=semantic_definition(record),
        kind=ASSIMILATED_KIND,
        category=ASSIMILATED_CATEGORY,
        authority_tier=ASSIMILATED_TIER,
        derives_from=parent_urn,
        owner=owner,
        lifecycle=native_lifecycle(record.get("status")),
        instrument=source,
        provider="engine.uckp.assimilation",
        ontology_class=ASSIMILATED_CATEGORY,
        taxonomy_path=(ASSIMILATED_CATEGORY, native_category, native_program),
        tags=(native_category, native_program, str(record.get("volume", "")).strip()),
        keywords=(native_category, native_program, "assimilated"),
        dependencies=tuple(dependencies),
        relationships=tuple(relationships),
        traceability=tuple(traceability),
        provenance=(
            ProvenanceStep(
                actor=owner,
                action="declared",
                source=path or source,
                digest=declared_hash,
            ),
            ProvenanceStep(
                actor="engine.uckp.assimilation",
                action="assimilated",
                source=source,
                digest=source_digest,
            ),
        ),
        evidence=(
            EvidenceRef(
                evidence_id=identity,
                digest=declared_hash,
                kind="repository-artifact",
                locator=path,
            ),
        ),
        # The repository appears here and only here: as the place a copy is kept,
        # explicitly non-authoritative (Article 4, UCKP-INV-10).
        persistence_bindings=(
            PersistenceBinding("git", path, False),
            PersistenceBinding("filesystem", path, False),
        ),
        projection_bindings=(
            ProjectionBinding("repository", path, True, False),
            ProjectionBinding("json", "projection/universe.json", True, False),
        ),
        runtime_bindings=UNIVERSAL_RUNTIMES,
        metadata={
            NATIVE_RECORD_KEY: native_record,
            "native_id": str(record.get("native_id", "")),
            "native_category": native_category,
            "native_program": native_program,
            "native_status": str(record.get("status", "")),
            "native_version": str(record.get("version", "")),
            "native_volume": str(record.get("volume", "")),
            "native_path": path,
            "native_content_hash": declared_hash,
            "source_registry": source,
            "source_digest": source_digest,
        },
        audit=(
            AuditEntry(
                actor="engine.uckp.assimilation",
                action="assimilate",
                subject=self_urn,
                digest=content_hash(native_record),
            ),
        ),
    )


def reconstruct_artifact(obj: UCKO) -> dict[str, object]:
    """Return the original native record — the exact inverse of assimilation."""
    encoded = obj.metadata.get(NATIVE_RECORD_KEY)
    if not encoded:
        raise AssimilationError(
            "this object carries no native record, so assimilation was not invertible",
            ucko_id=obj.ucko_id,
        )
    try:
        record = json.loads(encoded)
    except ValueError as exc:
        raise AssimilationError(
            "the native record is not decodable", ucko_id=obj.ucko_id, reason=str(exc)
        ) from exc
    if not isinstance(record, dict):
        raise AssimilationError("the native record is not a mapping", ucko_id=obj.ucko_id)
    return record


def verify_invertible(
    objects: Sequence[UCKO], records: Sequence[Mapping[str, object]]
) -> tuple[str, ...]:
    """Re-derive every source record from its object and report any difference.

    Compared by canonical digest rather than by ``==``, so the answer does not depend
    on key order in either direction. Returns the findings; empty means the mapping is
    invertible over this whole population.
    """
    losses: list[str] = []
    if len(objects) != len(records):
        losses.append(f"{len(records)} artifacts were read but {len(objects)} objects were minted")
    by_id = {str(record.get("universal_id", "")).strip(): record for record in records}
    for obj in objects:
        identity = obj.identity.local_name
        original = by_id.get(identity)
        if original is None:
            losses.append(f"{obj.ucko_id} corresponds to no source artifact")
            continue
        try:
            reconstructed = reconstruct_artifact(obj)
        except AssimilationError as exc:
            losses.append(f"{obj.ucko_id}: {exc}")
            continue
        if content_hash(reconstructed) != content_hash(original):
            missing = sorted(set(original) - set(reconstructed))
            changed = sorted(
                key
                for key in set(original) & set(reconstructed)
                if content_hash(original[key]) != content_hash(reconstructed[key])
            )
            losses.append(
                f"{obj.ucko_id} does not reconstruct: missing={missing} changed={changed}"
            )
    return tuple(losses)


# --- the whole operation --------------------------------------------------------


def assimilate(
    *,
    source_root: str | Path | None = None,
    vocabularies: VocabularyRegistry | None = None,
    law_urn: str | None = None,
) -> tuple[tuple[UCKO, ...], AssimilationReport]:
    """Assimilate every existing UCOS artifact, and prove the mapping invertible."""
    source_digest, records = load_artifact_registry(source_root)
    registry = vocabularies or build_vocabulary_registry()
    registry.require_term(GOVERNED_CATEGORY, ASSIMILATED_CATEGORY)
    stages, categories, programs = register_native_vocabularies(registry, records)

    known_ids = frozenset(
        str(record.get("universal_id", "")).strip()
        for record in records
        if str(record.get("universal_id", "")).strip()
    )
    root_urn = law_urn or root_law_urn()
    objects = tuple(
        assimilate_artifact(
            record,
            known_ids=known_ids,
            law_urn=root_urn,
            source=ARTIFACT_REGISTRY_PATH,
            source_digest=source_digest,
        )
        for record in records
    )

    # Everything the source declared but the graph cannot honour, named rather than dropped.
    unresolvable_trace: list[str] = []
    unresolvable_deps: list[str] = []
    for record in records:
        identity = str(record.get("universal_id", "")).strip()
        declared = record.get("traceability")
        if isinstance(declared, Mapping):
            for stage in TRACEABILITY_STAGES:
                for target in declared.get(stage) or ():
                    target_id = str(target).strip()
                    if target_id and target_id not in known_ids:
                        unresolvable_trace.append(f"{identity} -{stage}-> {target_id}")
        for dependency in record.get("dependencies") or ():
            dependency_id = str(dependency).strip()
            if dependency_id and dependency_id not in known_ids:
                unresolvable_deps.append(f"{identity} -depends-on-> {dependency_id}")

    shared = _shared_semantic_names(records)
    losses = verify_invertible(objects, records)
    report = AssimilationReport(
        source=ARTIFACT_REGISTRY_PATH,
        source_digest=source_digest,
        artifacts_read=len(records),
        objects_minted=len(objects),
        registered_lifecycle_terms=stages,
        registered_categories=categories,
        registered_programs=programs,
        shared_semantic_names=shared,
        unresolvable_traceability=tuple(sorted(unresolvable_trace)),
        unresolvable_dependencies=tuple(sorted(unresolvable_deps)),
        invertible=not losses,
        losses=losses,
    )
    return objects, report


def _shared_semantic_names(records: Sequence[Mapping[str, object]]) -> tuple[str, ...]:
    """Names carried by more than one artifact, which is why definitions are derived."""
    counts: dict[str, int] = {}
    for record in records:
        name = str(record.get("name", "")).strip()
        counts[name] = counts.get(name, 0) + 1
    return tuple(f"{name} x{count}" for name, count in sorted(counts.items()) if count > 1)


def require_lossless(report: AssimilationReport) -> None:
    """Fail closed unless assimilation lost nothing (Article 19)."""
    if not report.lossless:
        raise AssimilationError(
            "assimilation was not lossless",
            invertible=report.invertible,
            losses=list(report.losses[:5]),
        )


def _projections() -> tuple[tuple[str, frozenset[str], str], ...]:
    """Return every projection of a registered vocabulary as (name, members, vocabulary).

    Every import here is function-local, and deliberately so.  ``engine.knowledge``,
    ``engine.discovery``, ``engine.graph`` and ``engine.civilization`` are downstream
    of ``engine.uckp`` and import it; importing them back at module level closes a
    capability-level import cycle and fails the acyclicity rule W3-1 cleared.  W3-6
    did exactly that with :mod:`engine.knowledge.model` — measured here as
    ``engine.uckp <-> engine.knowledge``, 177 dependency edges against W3-1's 176 —
    so the four Layer Zero enums are deferred alongside the five engine term sets.
    A function-body import resolves on first call, once every module in the loop is
    already initialised, which is precisely why ``discover_dependencies`` measures
    ``import_time_imports`` rather than every ``Import`` node it can reach.

    A guard over nine downstream term sets can only live upstream of all nine on
    these terms.  Deferring is the cure for a circular import, not a workaround.
    """
    from engine.civilization.generation import GENERATION_STRATA
    from engine.discovery.contracts import DiscoveryKind
    from engine.graph.architecture.engine import DIAGRAM_NAMES
    from engine.graph.architecture.layers import LAYER_ORDER
    from engine.knowledge.model import (
        KnowledgeAuthority,
        KnowledgeKind,
        Lifecycle,
        RelationType,
    )
    from engine.knowledge.ukip.classification import Facet as UkipFacet
    from engine.uckp.projection import KNOWN_PROJECTION_KINDS

    layer_zero = tuple(
        (enum_cls.__name__, frozenset(member.value for member in enum_cls), vocabulary_id)
        for enum_cls, vocabulary_id in (
            (KnowledgeKind, KNOWLEDGE_KIND),
            (KnowledgeAuthority, AUTHORITY_TIER),
            (Lifecycle, LIFECYCLE_STAGE),
            (RelationType, RELATION_TYPE),
        )
    )
    return layer_zero + (
        # M-1 · H-04 — the stratum key is field 0 of the GENERATION_STRATA row.
        (
            "GENERATION_STRATA",
            frozenset(row[0] for row in GENERATION_STRATA),
            CIVILIZATION_STRATUM,
        ),
        # M-2 · H-05 — the term-set half only.  UNCLASSIFIED is a fallback for a
        # category with no position in the stack, not a layer, so it is not a term;
        # the _CATEGORY_LAYER mapping is deferred to its own CEP (§12.2).
        ("LAYER_ORDER", frozenset(LAYER_ORDER), ARCHITECTURE_LAYER),
        # M-3 · H-06 — one vocabulary, two projections: a UCKO output kind and a
        # visualisation diagram kind are both projection kinds.
        (
            "KNOWN_PROJECTION_KINDS|DIAGRAM_NAMES",
            frozenset(KNOWN_PROJECTION_KINDS) | frozenset(DIAGRAM_NAMES),
            PROJECTION_KIND,
        ),
        # M-4 · H-02 — distinct from uckp.facet; the two name different decisions.
        (
            "ukip.classification.Facet",
            frozenset(member.value for member in UkipFacet),
            UKIP_FACET,
        ),
        # M-5 · H-01 — DiscoveryKind.coerce() hard-refuses an unregistered value,
        # so this is the projection whose divergence bites soonest.
        (
            "DiscoveryKind",
            frozenset(member.value for member in DiscoveryKind),
            DISCOVERY_DIMENSION,
        ),
    )


def verify_vocabulary_alignment(
    vocabularies: VocabularyRegistry | None = None,
) -> None:
    """Verify every projection of a registered vocabulary still matches its owner.

    Nine closed term sets are a typed projection of a registered vocabulary.  Four
    are the Layer Zero ``str``-enums in :mod:`engine.knowledge.model` —
    :class:`~engine.knowledge.model.KnowledgeKind`,
    :class:`~engine.knowledge.model.KnowledgeAuthority`,
    :class:`~engine.knowledge.model.Lifecycle` and
    :class:`~engine.knowledge.model.RelationType`.  Five are the engine structural
    term sets contributed by CEP-MOD-002 M-1…M-5: ``GENERATION_STRATA``,
    ``LAYER_ORDER``, ``KNOWN_PROJECTION_KINDS`` with ``DIAGRAM_NAMES``, the UKIP
    ``Facet`` enum and ``DiscoveryKind``.

    In every case the vocabulary is the canonical owner and the local type is a
    convenience view.  This function fails closed if they ever diverge, so there is
    one authority and one verified view rather than two competing declarations
    (vocabulary.py, Articles 15 and 17).  Contribution without this guard would move
    the closure rather than close it: the registry would hold a term set nothing
    checks the engine against.
    """
    registry = vocabularies or build_vocabulary_registry()
    divergences: list[str] = []
    for projection, declared, vocabulary_id in _projections():
        vocabulary = registry.require(vocabulary_id)
        vocab_terms = frozenset(vocabulary.term_ids())
        only_in_projection = sorted(declared - vocab_terms)
        only_in_vocab = sorted(vocab_terms - declared)
        if only_in_projection:
            divergences.append(
                f"{projection} declares {only_in_projection!r} not registered in {vocabulary_id!r}"
            )
        if only_in_vocab:
            divergences.append(
                f"{vocabulary_id!r} declares {only_in_vocab!r} absent from {projection}"
            )
    if divergences:
        raise AssimilationError(
            "vocabulary alignment failed: projections diverge from their registered vocabularies",
            divergences=divergences,
        )


def build_assimilated_universe(
    *,
    source_root: str | Path | None = None,
    persistence_base: str | Path | None = None,
    require_coherent: bool = True,
) -> tuple[ConstitutionalUniverse, AssimilationReport]:
    """Build the universe with every existing UCOS artifact assimilated into it.

    The constitutional objects arrive by discovery and the artifacts by assimilation,
    but both go through the same registry and the same admission rules, so the result
    is one universe rather than a constitution with an appendix.
    """
    vocabularies = build_vocabulary_registry()
    objects, report = assimilate(source_root=source_root, vocabularies=vocabularies)
    require_lossless(report)
    universe = build_universe(
        vocabularies=vocabularies,
        additional_objects=objects,
        persistence_base=persistence_base,
        require_coherent=require_coherent,
    )
    return universe, report


def ucko_objects() -> tuple[UCKO, ...]:  # pragma: no cover - intentionally absent
    """Deliberately **not** defined as a provider hook.

    This function exists only as a signpost and is removed from the module namespace
    immediately below. Defining it would make assimilation a discovery provider, which
    would put a filesystem read inside every registry walk and make discovery fail —
    or report a third provider contributing nothing — whenever the working tree was
    absent. Assimilated objects enter through :func:`build_assimilated_universe`, which
    states that dependency in its signature instead of hiding it in an import.
    """
    return ()


# Retract the name so :meth:`UniversalKnowledgeRegistry.discover` does not see a
# provider here. A docstring saying "not a provider" does not stop the walk from
# finding one; deleting the attribute does.
del ucko_objects


__all__ = [
    "ARTIFACT_REGISTRY_PATH",
    "ASSIMILATED_CATEGORY",
    "ASSIMILATED_KIND",
    "ASSIMILATED_TIER",
    "ASSIMILATION_NAMESPACE",
    "NATIVE_CATEGORY_VOCABULARY",
    "NATIVE_PROGRAM_VOCABULARY",
    "NATIVE_RECORD_KEY",
    "TRACEABILITY_STAGES",
    "AssimilationReport",
    "artifact_urn",
    "assimilate",
    "assimilate_artifact",
    "build_assimilated_universe",
    "load_artifact_registry",
    "native_lifecycle",
    "native_term",
    "reconstruct_artifact",
    "register_native_vocabularies",
    "require_lossless",
    "semantic_definition",
    "verify_invertible",
    "verify_vocabulary_alignment",
]
