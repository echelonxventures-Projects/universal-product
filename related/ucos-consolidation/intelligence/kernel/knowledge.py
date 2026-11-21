"""The Canonical Knowledge Resolver — the ONLY route canonical content may travel.

Zero duplication is an architectural property here, not a review convention:

  * A derived artifact (a research claim, a publication section) stores a
    **reference** — ``cko:UCKO-PRIN-0001#statement`` — and never the text.
  * Text materialises only at render time, produced by :meth:`resolve`, and always
    arrives attached to its source id, source locator and source content hash.
  * :meth:`prose_index` publishes the shingle fingerprint of all canonical prose so
    a validator can *prove* that no derived artifact carries copied text.

Reference grammar (total, closed, self-describing)::

    <space>:<target>[#<field>]

    cko:UCKO-PRIN-0001#statement          canonical knowledge object prose
    decision:UKDA-DEC-0001#rationale      decision record prose
    concept:AF-3#disposition              concept-closure structured field
    metric:corpus.artifacts               declared derived measurement

The canonical knowledge objects and decisions are read through their registered
owner, :class:`engine.knowledge.store.KnowledgeStore`; no second reader exists.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from engine.knowledge.cko import CanonicalKnowledgeObject, DecisionRecord
from engine.knowledge.store import KNOWLEDGE_DIR, KnowledgeBase, KnowledgeStore
from intelligence.kernel.canonical import canonical_json, sha256_file, sha256_text, shingles
from intelligence.kernel.errors import UnresolvedReferenceError
from intelligence.kernel.substrate import SubstrateReader

#: Reference spaces and, for each, the fields that carry *prose* (renderable text).
PROSE_FIELDS: dict[str, frozenset[str]] = {
    "cko": frozenset({"title", "statement", "rationale"}),
    "decision": frozenset(
        {
            "title",
            "problem_statement",
            "context",
            "objective",
            "chosen_architecture",
            "rationale",
            "impact_analysis",
            "implementation_guidance",
            "validation_strategy",
            "supersession_rules",
        }
    ),
}

#: Fields that carry a *list* of prose items (rendered as an enumeration).
LIST_FIELDS: dict[str, frozenset[str]] = {
    "cko": frozenset({"tags", "knowledge_links", "evidence", "dependencies", "consumers"}),
    "decision": frozenset(
        {
            "alternatives",
            "evaluation_criteria",
            "tradeoffs",
            "consequences",
            "risks",
            "mitigations",
            "dependencies",
            "certification_requirements",
        }
    ),
}

#: Structured (non-prose) fields resolvable on a concept-closure record.
CONCEPT_FIELDS: frozenset[str] = frozenset(
    {"id", "family", "disposition", "certified", "deferred", "homed", "orphan"}
)

#: THE declared derived-measurement table. Every ``metric:`` reference resolves
#: here; adding a measurement is a data edit and requires NO engine change.
METRIC_DECLARATION: tuple[dict[str, Any], ...] = (
    {
        "key": "knowledge.objects",
        "surface": "canonical-knowledge",
        "path": ("count",),
        "unit": "canonical knowledge objects",
    },
    {
        "key": "knowledge.decisions",
        "surface": "canonical-decisions",
        "path": ("count",),
        "unit": "decision records",
    },
    {
        "key": "concepts.total",
        "surface": "concept-closure",
        "path": ("concept_total",),
        "unit": "concepts",
    },
    {
        "key": "concepts.gaps",
        "surface": "concept-closure",
        "path": ("gap_total",),
        "unit": "open concept gaps",
    },
    {
        "key": "concepts.determination",
        "surface": "concept-closure",
        "path": ("determination",),
        "unit": "closure determination",
    },
    {
        "key": "corpus.artifacts",
        "surface": "corpus-control-tower",
        "path": ("portfolio", "total_artifacts"),
        "unit": "artifacts",
    },
    {
        "key": "corpus.pages",
        "surface": "corpus-control-tower",
        "path": ("portfolio", "total_pages"),
        "unit": "pages",
    },
    {
        "key": "corpus.volumes",
        "surface": "corpus-control-tower",
        "path": ("portfolio", "total_volumes"),
        "unit": "volumes",
    },
    {
        "key": "corpus.edges",
        "surface": "corpus-control-tower",
        "path": ("portfolio", "total_edges"),
        "unit": "graph edges",
    },
    {
        "key": "graph.relationships",
        "surface": "concept-graph",
        "path": ("count",),
        "unit": "typed relationships",
    },
    {
        "key": "certification.verdict",
        "surface": "corpus-certification",
        "path": ("verdict",),
        "unit": "certification verdict",
    },
    {
        "key": "certification.domains_passed",
        "surface": "corpus-certification",
        "path": ("domains_passed",),
        "unit": "certified domains",
    },
    {
        "key": "certification.domains_total",
        "surface": "corpus-certification",
        "path": ("domains_total",),
        "unit": "certification domains",
    },
    {
        "key": "certification.standard",
        "surface": "corpus-certification",
        "path": ("standard",),
        "unit": "certification standard",
    },
)

#: Coverage attributes resolvable through the ``coverage:`` space. Coverage is read
#: through its registered owner (``intelligence.rie.evidence.EvidenceReader``) — this
#: table only declares which of its attributes a publication may cite.
COVERAGE_ATTRIBUTES: dict[str, str] = {
    "line_pct": "percent of lines covered",
    "branch_pct": "percent of branches covered",
    "lines_covered": "covered lines",
    "lines_valid": "measured lines",
}

_METRICS: dict[str, dict[str, Any]] = {m["key"]: m for m in METRIC_DECLARATION}


@dataclass(frozen=True, slots=True)
class ResolvedContent:
    """Canonical content, materialised at render time, bound to its provenance."""

    ref: str
    space: str
    target: str
    field: str
    text: str
    value_kind: str
    source_locator: str
    source_authority: str
    source_content_sha256: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "ref": self.ref,
            "space": self.space,
            "target": self.target,
            "field": self.field,
            "text": self.text,
            "value_kind": self.value_kind,
            "source_locator": self.source_locator,
            "source_authority": self.source_authority,
            "source_content_sha256": self.source_content_sha256,
        }

    def provenance(self) -> dict[str, str]:
        return {
            "ref": self.ref,
            "source_locator": self.source_locator,
            "source_authority": self.source_authority,
            "source_content_sha256": self.source_content_sha256,
        }


def parse_ref(ref: str) -> tuple[str, str, str]:
    """Split ``<space>:<target>[#<field>]`` into its three parts."""
    if not isinstance(ref, str) or ":" not in ref:
        raise UnresolvedReferenceError("malformed content reference", ref=ref)
    space, _, remainder = ref.partition(":")
    target, _, field = remainder.partition("#")
    space, target, field = space.strip(), target.strip(), field.strip()
    if not space or not target:
        raise UnresolvedReferenceError("content reference is missing a space or target", ref=ref)
    return space, target, field


def make_ref(space: str, target: str, field: str = "") -> str:
    return f"{space}:{target}#{field}" if field else f"{space}:{target}"


class CanonicalKnowledgeResolver:
    """Resolves content references against canonical knowledge and Repository Truth."""

    #: The closed set of reference spaces this resolver understands.
    SPACES = ("cko", "decision", "concept", "metric", "coverage")

    def __init__(self, substrate: SubstrateReader) -> None:
        self.substrate = substrate
        self._base: KnowledgeBase | None = None
        self._concepts: dict[str, dict[str, Any]] | None = None
        self._prose_index: dict[str, str] | None = None
        self._coverage: Any = None

    # -- canonical stores ------------------------------------------------------

    @property
    def base(self) -> KnowledgeBase:
        """The canonical knowledge base, read through its registered owner."""
        if self._base is None:
            store = KnowledgeStore(self.substrate.config.repo_root / KNOWLEDGE_DIR)
            self._base = store.load()
        return self._base

    def objects(self) -> tuple[CanonicalKnowledgeObject, ...]:
        return self.base.objects()

    def decisions(self) -> tuple[DecisionRecord, ...]:
        return self.base.decisions()

    def concepts(self) -> dict[str, dict[str, Any]]:
        if self._concepts is None:
            rows = self.substrate.records("concept-closure")
            self._concepts = {
                str(row.get("id")): row for row in rows if isinstance(row.get("id"), str)
            }
        return self._concepts

    # -- resolution ------------------------------------------------------------

    def exists(self, ref: str) -> bool:
        try:
            self.resolve(ref)
        except UnresolvedReferenceError:
            return False
        return True

    def resolve(self, ref: str) -> ResolvedContent:
        space, target, field = parse_ref(ref)
        if space == "cko":
            return self._resolve_cko(ref, target, field or "statement")
        if space == "decision":
            return self._resolve_decision(ref, target, field or "rationale")
        if space == "concept":
            return self._resolve_concept(ref, target, field or "disposition")
        if space == "metric":
            return self._resolve_metric(ref, target)
        if space == "coverage":
            return self._resolve_coverage(ref, target)
        raise UnresolvedReferenceError(
            "unknown reference space", ref=ref, space=space, allowed=list(self.SPACES)
        )

    def resolve_all(self, refs: Sequence[str]) -> tuple[ResolvedContent, ...]:
        return tuple(self.resolve(r) for r in refs)

    def _resolve_cko(self, ref: str, target: str, field: str) -> ResolvedContent:
        obj = self.base.get_object(target)
        if obj is None:
            raise UnresolvedReferenceError(
                "canonical knowledge object not found", ref=ref, cko_id=target
            )
        return self._field_content(
            ref=ref,
            space="cko",
            target=target,
            field=field,
            record=obj.to_dict(),
            content_sha256=obj.content_sha256,
            locator=f"{KNOWLEDGE_DIR}/canonical-knowledge.json#{target}",
            authority=obj.authority.value,
        )

    def _resolve_decision(self, ref: str, target: str, field: str) -> ResolvedContent:
        dec = self.base.get_decision(target)
        if dec is None:
            raise UnresolvedReferenceError("decision record not found", ref=ref, decision_id=target)
        return self._field_content(
            ref=ref,
            space="decision",
            target=target,
            field=field,
            record=dec.to_dict(),
            content_sha256=dec.content_sha256,
            locator=f"{KNOWLEDGE_DIR}/decisions.json#{target}",
            authority=dec.authority.value,
        )

    def _field_content(
        self,
        *,
        ref: str,
        space: str,
        target: str,
        field: str,
        record: Mapping[str, Any],
        content_sha256: str,
        locator: str,
        authority: str,
    ) -> ResolvedContent:
        prose = PROSE_FIELDS.get(space, frozenset())
        lists = LIST_FIELDS.get(space, frozenset())
        if field not in prose and field not in lists:
            raise UnresolvedReferenceError(
                "field is not resolvable on this space",
                ref=ref,
                field=field,
                allowed=sorted(prose | lists),
            )
        value = record.get(field)
        if field in lists:
            items = [str(v) for v in (value or []) if str(v)]
            if not items:
                raise UnresolvedReferenceError(
                    "referenced list field is empty", ref=ref, field=field, target=target
                )
            return ResolvedContent(
                ref,
                space,
                target,
                field,
                "\n".join(items),
                "list",
                locator,
                authority,
                content_sha256,
            )
        text = str(value or "").strip()
        if not text:
            raise UnresolvedReferenceError(
                "referenced prose field is empty", ref=ref, field=field, target=target
            )
        return ResolvedContent(
            ref, space, target, field, text, "prose", locator, authority, content_sha256
        )

    def _resolve_concept(self, ref: str, target: str, field: str) -> ResolvedContent:
        row = self.concepts().get(target)
        if row is None:
            raise UnresolvedReferenceError(
                "concept not found in the concept closure", ref=ref, concept=target
            )
        if field not in CONCEPT_FIELDS:
            raise UnresolvedReferenceError(
                "field is not resolvable on a concept",
                ref=ref,
                field=field,
                allowed=sorted(CONCEPT_FIELDS),
            )
        if field not in row:
            raise UnresolvedReferenceError(
                "concept record has no such field", ref=ref, field=field, concept=target
            )
        surface = self.substrate.surface("concept-closure")
        return ResolvedContent(
            ref,
            "concept",
            target,
            field,
            str(row[field]),
            "label",
            f"{surface.locator}#{target}",
            surface.authority,
            surface.content_sha256,
        )

    def _resolve_metric(self, ref: str, target: str) -> ResolvedContent:
        declaration = _METRICS.get(target)
        if declaration is None:
            raise UnresolvedReferenceError(
                "metric is not declared", ref=ref, metric=target, allowed=sorted(_METRICS)
            )
        surface = self.substrate.surface(declaration["surface"])
        if not surface.available:
            raise UnresolvedReferenceError(
                "metric substrate surface is unavailable — value may not be invented",
                ref=ref,
                metric=target,
                locator=surface.locator,
            )
        node: Any = self.substrate.payload(declaration["surface"])
        for step in declaration["path"]:
            if not isinstance(node, Mapping) or step not in node:
                raise UnresolvedReferenceError(
                    "metric path does not resolve", ref=ref, metric=target, step=step
                )
            node = node[step]
        if isinstance(node, dict | list):
            raise UnresolvedReferenceError(
                "metric path resolves to a container, not a value", ref=ref, metric=target
            )
        return ResolvedContent(
            ref,
            "metric",
            target,
            declaration["path"][-1],
            str(node),
            "scalar",
            f"{surface.locator}#{'.'.join(declaration['path'])}",
            surface.authority,
            surface.content_sha256,
        )

    # -- coverage --------------------------------------------------------------

    def coverage(self) -> Any:
        """Coverage evidence, read through its registered owner (never re-parsed here)."""
        if self._coverage is None:
            from intelligence.rie.evidence import EvidenceReader

            self._coverage = EvidenceReader(self.substrate.config).coverage()
        return self._coverage

    def _resolve_coverage(self, ref: str, target: str) -> ResolvedContent:
        if target not in COVERAGE_ATTRIBUTES:
            raise UnresolvedReferenceError(
                "coverage attribute is not declared",
                ref=ref,
                attribute=target,
                allowed=sorted(COVERAGE_ATTRIBUTES),
            )
        coverage = self.coverage()
        if coverage is None or not coverage.available:
            raise UnresolvedReferenceError(
                "coverage evidence is unavailable — value may not be invented",
                ref=ref,
                attribute=target,
            )
        path = self.substrate.config.coverage_xml
        return ResolvedContent(
            ref,
            "coverage",
            target,
            target,
            str(getattr(coverage, target)),
            "scalar",
            self.substrate.config.rel(path),
            "GENERATED",
            sha256_file(path),
        )

    # -- metrics ---------------------------------------------------------------
    def metric_keys(self) -> tuple[str, ...]:
        return tuple(sorted(_METRICS))

    def metric_unit(self, key: str) -> str:
        declaration = _METRICS.get(key)
        return str(declaration["unit"]) if declaration else ""

    def available_metrics(self) -> tuple[str, ...]:
        return tuple(k for k in self.metric_keys() if self.exists(f"metric:{k}"))

    # -- zero-duplication fingerprint -----------------------------------------

    def prose_index(self) -> dict[str, str]:
        """Shingle → owning canonical id, over ALL canonical prose.

        A derived artifact whose authored fields intersect this index has copied
        canonical content instead of referencing it.
        """
        if self._prose_index is None:
            index: dict[str, str] = {}
            for obj in self.objects():
                for field in sorted(PROSE_FIELDS["cko"]):
                    text = str(obj.to_dict().get(field) or "")
                    for shingle in shingles(text):
                        index.setdefault(shingle, f"cko:{obj.cko_id}#{field}")
            for dec in self.decisions():
                record = dec.to_dict()
                for field in sorted(PROSE_FIELDS["decision"]):
                    text = str(record.get(field) or "")
                    for shingle in shingles(text):
                        index.setdefault(shingle, f"decision:{dec.decision_id}#{field}")
            self._prose_index = index
        return self._prose_index

    def copied_prose(self, text: str) -> list[str]:
        """Canonical owners of any verbatim run found in ``text`` (empty ⇒ clean)."""
        index = self.prose_index()
        owners = {index[s] for s in shingles(text) if s in index}
        return sorted(owners)

    # -- determinism -----------------------------------------------------------

    def fingerprint(self) -> dict[str, Any]:
        return {
            "canonical_objects": len(self.objects()),
            "canonical_decisions": len(self.decisions()),
            "concepts": len(self.concepts()),
            "declared_metrics": len(_METRICS),
            "available_metrics": len(self.available_metrics()),
            "knowledge_state_sha256": sha256_text(
                canonical_json(
                    [o.content_sha256 for o in self.objects()]
                    + [d.content_sha256 for d in self.decisions()]
                )
            ),
        }


__all__ = [
    "CONCEPT_FIELDS",
    "COVERAGE_ATTRIBUTES",
    "LIST_FIELDS",
    "METRIC_DECLARATION",
    "PROSE_FIELDS",
    "CanonicalKnowledgeResolver",
    "ResolvedContent",
    "make_ref",
    "parse_ref",
]
